import os
import pathlib

from termcolor import cprint


def init_web():
    # TODO
    pass


def init_public():
    # TODO
    pass


def init_dirs():
    data_dir_vars = {
        "root": "BENTOV2_ROOT_DATA_DIR",

        "auth": "BENTOV2_AUTH_VOL_DIR",
        "drop-box": "BENTOV2_DROP_BOX_VOL_DIR",
        "katsu-db": "BENTOV2_KATSU_DB_PROD_VOL_DIR",
        "notification": "BENTOV2_NOTIFICATION_VOL_DIR",
        "redis": "BENTOV2_REDIS_VOL_DIR",
        "wes": "BENTOV2_WES_VOL_DIR",
    }

    print("Creating temporary secrets directory if needed... ", end="")
    (pathlib.Path.cwd() / "tmp" / "secrets").mkdir(parents=True, exist_ok=True)
    cprint("done.", "green")

    print("Creating data directories...")
    for dir_for, dir_var in data_dir_vars.items():
        print(f"  {dir_for} ", end="")

        data_dir = os.getenv(dir_var)
        if data_dir is None:
            cprint(f"error: {dir_for} data directory ({dir_var}) is not set", "red")
            exit(1)

        pathlib.Path(os.getenv(dir_var)).mkdir(parents=True, exist_ok=True)
        cprint("done.", "green")


def init_docker():
    pass


def init_secrets():
    # TODO
    pass


def clean_secrets():
    # TODO
    pass


def clean_logs():
    # TODO
    pass
