import os
import shutil
import socket

from dataclasses import dataclass
from pathlib import Path

from . import config as c, utils as u

__all__ = [
    "pg_dump",
    "pg_load",
]

# Each entry here is a three-tuple of the following:
#  - An environment variable prefix
POSTGRES_DB_CONTAINERS: tuple[tuple[str, c.BentoOptionalFeature | None, str], ...] = (
    ("BENTO_AUTH_DB", c.BENTO_FEATURE_AUTH, "auth"),
    ("BENTO_AUTHZ_DB", None, "authz-db"),
    ("BENTO_REFERENCE_DB", None, "reference-db"),
    ("BENTOV2_KATSU_DB", None, "katsu-db"),
)


@dataclass
class PostgresContainer:
    container: str
    image: str
    version: str
    # -----------
    vol_dir: Path
    # -----------
    db: str
    username: str


def process_ansi(res: bytes) -> bytes:
    # noinspection PyTypeChecker
    return res.replace(b"\x00", b"").replace(b"\x01", b"").replace(b"\x02", b"").lstrip(b"]k")


def _load_pg_db_containers() -> list[PostgresContainer]:
    pg_containers: list[PostgresContainer] = []

    for prefix, feature, volume_key in POSTGRES_DB_CONTAINERS:
        if feature is not None and not feature.enabled:
            # TODO: log
            continue

        pg_containers.append(
            PostgresContainer(
                container=os.getenv(f"{prefix}_CONTAINER_NAME"),
                image=os.getenv(f"{prefix}_IMAGE"),
                version=os.getenv(f"{prefix}_VERSION"),
                vol_dir=Path(os.getenv(c.DATA_DIR_ENV_VARS[volume_key])),
                db=os.getenv(f"{prefix}_NAME"),
                username=os.getenv(f"{prefix}_USER"),
            )
        )

    return pg_containers


def pg_dump(pgdump_dir: Path):
    docker_client = u.get_docker_client()
    pg_containers = _load_pg_db_containers()

    for pg in pg_containers:
        u.info(f"creating pgdumps for database {pg.container}")

        container = docker_client.containers.get(pg.container)

        # ---

        _, output = container.exec_run(("pg_dumpall", "-U", pg.username), stream=True, demux=True)

        # ---

        if not pgdump_dir.exists():
            pgdump_dir.mkdir(parents=True, exist_ok=True)

        # TODO: validate not empty

        with open(pgdump_dir / f"{pg.container}.pgdump", "wb") as fh:
            for chunk_stdout, chunk_stderr in output:
                if chunk_stderr:
                    u.warn(chunk_stderr.decode("ascii"))
                if chunk_stdout:
                    fh.write(chunk_stdout)

    # TODO: write success


def pg_load(pgdump_dir: Path):
    if not pgdump_dir.exists():
        u.err(f"directory {pgdump_dir} does not exist")
        exit(1)

    docker_client = u.get_docker_client()
    pg_containers = _load_pg_db_containers()

    for pg in pg_containers:
        container = docker_client.containers.get(pg.container)

        u.info(f"working on postgres database {pg.container}")

        container_pgdump_to_load = pgdump_dir / f"{pg.container}.pgdump"

        if not container_pgdump_to_load.exists():
            u.err(f"    file {container_pgdump_to_load} does not exist")
            # TODO
            exit(1)

        # --------------------------------------------------------------------------------------------------------------

        u.task_print(f"    importing {container_pgdump_to_load} into container...")

        skt: socket.SocketIO
        _, skt = container.exec_run(rf"psql -U {pg.username} {pg.db}", stdin=True, socket=True)
        # noinspection PyUnresolvedReferences,PyProtectedMember
        s: socket.socket = skt._sock

        # Receive any initial messages

        s.settimeout(1.0)
        try:
            initial_messages: bytes = s.recv(1024 * 100)
            u.warn("    receieved initial messages:")
            u.warn(u.indent_str(process_ansi(initial_messages).decode("ascii"), 6))
        except TimeoutError:
            pass
        s.settimeout(None)

        with open(container_pgdump_to_load, "rb") as fh:
            while send_chunk := fh.read(4096):
                # TODO:
                # s.sendall(send_chunk)
                pass

        # noinspection PyTypeChecker
        s.sendall(b"SELECT * FROM dasdf;\n")
        response: bytes = process_ansi(s.recv(1024 * 100))

        # noinspection PyTypeChecker
        has_error = response.find(b"ERROR:") >= 0
        if has_error:
            u.task_print_done("failed.", color="red")
            u.err(u.indent_str(response.decode("ascii").strip(), 6))
            # exit(1)
        else:
            u.task_print_done("imported.")


def pg_wipe():
    """
    Scary utility!! Wipes all Postgres database volumes.
    """

    confirm = input("Are you sure you want to wipe all Postgres database volumes? [y/N]")

    if confirm.lower() != "y":
        u.info("terminating without destroying data.")
        exit(0)

    # Now we do the scary thing

    containers = _load_pg_db_containers()

    u.info(f"deleting contents of {len(containers)} Postgres volumes")

    for pg in containers:
        u.task_print(f"    deleting {pg.container} database volume...")
        if not pg.vol_dir.exists():
            u.task_print_done("already does not exist.", color="yellow")
            continue
        shutil.rmtree(pg.vol_dir)
        pg.vol_dir.mkdir(exist_ok=True)
        u.task_print_done()

    u.info("done.")
