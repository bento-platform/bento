import os
import pathlib

import docker.errors

from typing import Optional

from .utils import info, task_print, task_print_done, err, get_docker_client

__all__ = ["init_assets"]

# Where Bento's lib/ is mounted in the bento_assets container; the image's entrypoint copies files there when
# ASSETS_LIB_DIR is set, using the same layout as lib/.
CONTAINER_LIB_DIR = "/lib-assets"


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

    lib_path = pathlib.Path.cwd() / "lib"
    volumes = {str(lib_path): {"bind": CONTAINER_LIB_DIR, "mode": "rw"}}

    # Beacon's config directory is configurable; mount it over lib/beacon/config if it lives elsewhere.
    beacon_config_dir = pathlib.Path(os.getenv("BENTO_BEACON_CONFIG_DIR", lib_path / "beacon" / "config"))
    if beacon_config_dir.resolve() != (lib_path / "beacon" / "config").resolve():
        beacon_config_dir.mkdir(parents=True, exist_ok=True)
        volumes[str(beacon_config_dir)] = {"bind": f"{CONTAINER_LIB_DIR}/beacon/config", "mode": "rw"}

    container = client.containers.run(
        image,
        command=services or [],  # no services: the entrypoint copies assets for all of them
        environment={"ASSETS_LIB_DIR": CONTAINER_LIB_DIR},
        volumes=volumes,
        # So the copied files are owned by the current user rather than root
        user=f"{os.getuid()}:{os.getgid()}",
        detach=True,
    )
    try:
        for line in container.logs(stream=True, follow=True):
            print(line.decode("utf-8"), end="", flush=True)
        exit_code = container.wait()["StatusCode"]
    finally:
        container.remove()

    if exit_code != 0:
        err(f"{image} failed to copy assets (exit code {exit_code})")
        exit(1)

    restart_target = " ".join(services) if services and len(services) == 1 else "<service>"
    info(f"Done. Restart affected services to apply changes: ./bentoctl.bash restart {restart_target}")
