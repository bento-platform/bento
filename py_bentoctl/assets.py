import io
import json
import os
import pathlib
import tarfile

import docker.errors

from typing import Optional

from .utils import info, task_print, task_print_done, warn, err, get_docker_client

__all__ = ["init_assets"]

# Layout of bento_assets images: /assets/manifest.json, plus files under /assets/lib/ mirroring Bento's lib/ dir.
IMAGE_ASSETS_DIR = "/assets"


def _dest_path(lib_path: pathlib.Path, source: str) -> pathlib.Path:
    # Beacon's config directory is configurable; everything else is mounted from lib/ directly.
    beacon_config_prefix = "beacon/config/"
    if source.startswith(beacon_config_prefix) and (beacon_config_dir := os.getenv("BENTO_BEACON_CONFIG_DIR")):
        return pathlib.Path(beacon_config_dir) / source.removeprefix(beacon_config_prefix)
    return lib_path / source


def _read_image_assets(client, image: str) -> tarfile.TarFile:
    container = client.containers.create(image)
    try:
        stream, _ = container.get_archive(IMAGE_ASSETS_DIR)
        return tarfile.open(fileobj=io.BytesIO(b"".join(stream)))
    finally:
        container.remove()


def init_assets(instance: Optional[str], version: Optional[str], services: Optional[list[str]]):
    instance = instance or os.environ["BENTO_ASSETS_INSTANCE"]
    version = version or os.environ["BENTO_ASSETS_VERSION"]
    repository = f"{os.environ['BENTO_ASSETS_IMAGE']}-{instance}"
    image = f"{repository}:{version}"

    client = get_docker_client()

    # Always pull, since tags like edge and pr-<N> move
    task_print(f"Pulling {image}...")
    try:
        client.images.pull(repository, tag=version)
    except docker.errors.APIError as e:
        err(f"failed: {e.explanation}")
        exit(1)
    task_print_done()

    archive = _read_image_assets(client, image)
    manifest = json.load(archive.extractfile("assets/manifest.json"))

    services = services or list(manifest)
    if unknown := [s for s in services if s not in manifest]:
        err(f"Unknown service(s) for {image}: {', '.join(unknown)} (available: {', '.join(manifest)})")
        exit(1)

    lib_path = pathlib.Path.cwd() / "lib"

    # Check required files first, so we don't leave a service with half of its assets copied
    for service in services:
        for file in manifest[service]:
            if not file.get("optional", False) and f"assets/lib/{file['source']}" not in archive.getnames():
                err(f"{image} is missing required file {file['source']} for {service}")
                exit(1)

    for service in services:
        info(f"{service}:")
        for file in manifest[service]:
            member = f"assets/lib/{file['source']}"
            if member not in archive.getnames():
                warn(f"  {file['source']} not in image (optional), skipping")
                continue

            dest = _dest_path(lib_path, file["source"])
            dest_display = dest.relative_to(pathlib.Path.cwd()) if dest.is_relative_to(pathlib.Path.cwd()) else dest
            task_print(f"  {file['source']} -> {dest_display}...")
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Write into the existing file rather than replacing it, so single-file bind mounts in running
            # containers (which follow the inode) see the new contents.
            with open(dest, "wb") as fh:
                fh.write(archive.extractfile(member).read())
            task_print_done()

    info(f"Done. Restart affected services to apply changes: ./bentoctl.bash restart <{'|'.join(services)}>")
