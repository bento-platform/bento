import os
import pathlib
import shutil
import sys

import docker
import docker.errors

from termcolor import cprint

from . import config as c
from .openssl import create_cert, create_private_key
from .utils import task_print, task_print_done, warn, err

__all__ = [
    "init_web",
    "init_docker",
    "init_dirs",
    "init_self_signed_certs",
]


def init_web(service: str, force: bool):
    if service not in ("public", "private"):
        err("You must specify the service type (public or private)")
        exit(1)

    if service == "public":
        _init_web_public(force)
    else:  # private
        _init_web_private(force)


def _init_web_public(force: bool):
    root_path = pathlib.Path.cwd()

    # Init lib dir
    public_path = (root_path / "lib" / "public")
    translation_path = (public_path / "translations")
    translation_path.mkdir(parents=True, exist_ok=True)

    # About html page
    _file_copy(
        (root_path / "etc" / "default.about.html"),
        (public_path / "about.html"),
        force=force,
    )
    # Branding image
    _file_copy(
        (root_path / "etc" / "default.public.branding.png"),
        (public_path / "branding.png"),
        force=force,
    )
    # English translations
    _file_copy(
        (root_path / "etc" / "templates" / "translations" / "en.example.json"),
        (translation_path / "en.json"),
        force=force,
    )
    # French translations
    _file_copy(
        (root_path / "etc" / "templates" / "translations" / "fr.example.json"),
        (translation_path / "fr.json"),
        force=force,
    )


def _file_copy(src_path: pathlib.Path, dst_path: pathlib.Path, force: bool = False):
    task_print(f"Copying {src_path} to {dst_path}...")

    if dst_path.is_file():
        if not force:
            warn("destination exists, skipping copy.")
            return

        cprint("destination exists, overwriting... ", "yellow", file=sys.stderr, end="")

    shutil.copyfile(src_path, dst_path)
    cprint("done.", "green")


def _init_web_private(force: bool):
    task_print("Init public web folder with branding image...")

    root_path = pathlib.Path.cwd()
    web_path = (root_path / "lib" / "web")
    web_path.mkdir(parents=True, exist_ok=True)

    src_branding = (root_path / "etc" / "default.branding.png")
    dst_branding = (web_path / "branding.png")

    if dst_branding.is_file():
        if not force:
            warn(f"file {dst_branding} exists, skipping copy.")
            return

        cprint(f"file {dst_branding} exists, overwriting... ", "yellow", file=sys.stderr, end="")

    shutil.copyfile(src=src_branding, dst=dst_branding)
    task_print_done()


def init_self_signed_certs(force: bool):
    certs_dir = pathlib.Path(os.environ["BENTOV2_CERTS_DIR"])
    auth_certs_dir = (certs_dir / "auth")
    gateway_certs_dir = (certs_dir / "gateway")

    cert_domains_vars = {
        "public": {
            "var": "BENTOV2_DOMAIN",
            "priv_key_name": "privkey1.key",
            "crt": "fullchain1.crt",
            "dir": gateway_certs_dir,
        },
        "portal": {
            "var": "BENTOV2_PORTAL_DOMAIN",
            "priv_key_name": "portal_privkey1.key",
            "crt": "portal_fullchain1.crt",
            "dir": gateway_certs_dir,
        },
        "auth": {
            "var": "BENTOV2_AUTH_DOMAIN",
            "priv_key_name": "auth_privkey1.key",
            "crt": "auth_fullchain1.crt",
            "dir": auth_certs_dir,
        },

        # If cBioPortal is enabled, generate a cBioPortal self-signed certificate as well
        **({"cbioportal": {
            "var": "BENTOV2_CBIOPORTAL_DOMAIN",
            "priv_key_name": "cbioportal_privkey1.key",
            "crt": "cbioportal_fullchain1.crt",
            "dir": gateway_certs_dir,
        }} if c.BENTO_CBIOPORTAL_ENABLED else {}),
    }

    # Init cert directories

    task_print("Creating certs directories if needed...")
    auth_certs_dir.mkdir(parents=True, exist_ok=True)
    gateway_certs_dir.mkdir(parents=True, exist_ok=True)
    task_print_done()

    # Check for existing cert files first
    cert_files = [
        *auth_certs_dir.glob('*.crt'),
        *auth_certs_dir.glob('*.key'),
        *auth_certs_dir.glob("*.pem"),
        *gateway_certs_dir.glob('*.crt'),
        *gateway_certs_dir.glob('*.key'),
        *gateway_certs_dir.glob("*.pem"),
    ]
    if not force and any(cert_files):
        warn("WARNING: Cert files detected in the target directory, new cert creation skipped.")
        warn("To create new certs, remove all \".crt\" and \".key\" files in target directory first.")
        for f in cert_files:
            warn(f"Cert file path: {f}")
        return

    for domain in cert_domains_vars.keys():
        domain_var, priv_key_name, crt_name, crt_pk_dir = cert_domains_vars[domain].values()
        domain_val = os.getenv(domain_var)

        if domain_val is None:
            err(f"error: {domain_var} env variable ({domain}) is not set")
            exit(1)

        #  Create private key for domain
        task_print(f"Creating .key file for domain: {domain} -> {domain_val} ...")
        pkey = create_private_key(crt_pk_dir, priv_key_name)
        task_print_done()

        # Create signed cert for domain
        task_print(f"Creating certificate file for domain: {domain} -> {domain_val} ...")
        create_cert(crt_pk_dir, pkey, crt_name, domain_val)
        task_print_done()


def init_dirs():
    data_dir_vars = {
        "root": "BENTOV2_ROOT_DATA_DIR",
        "drs": "BENTOV2_DRS_DEV_VOL_DIR" if c.DEV_MODE else "BENTOV2_DRS_PROD_VOL_DIR",
        "drop-box": "BENTOV2_DROP_BOX_VOL_DIR",
        "gohan": "BENTOV2_GOHAN_DATA_ROOT",
        "gohan-elasticsearch": "BENTOV2_GOHAN_ES_DATA_DIR",
        "gohan-api-drs-bridge": "BENTOV2_GOHAN_API_DRS_BRIDGE_HOST_DIR",
        "gohan-vcfs": "BENTOV2_GOHAN_API_VCF_PATH",
        "gohan-gtfs": "BENTOV2_GOHAN_API_GTF_PATH",
        "katsu-db": "BENTOV2_KATSU_DB_PROD_VOL_DIR",
        "notification": "BENTOV2_NOTIFICATION_VOL_DIR",
        "redis": "BENTOV2_REDIS_VOL_DIR",
        "wes": "BENTOV2_WES_VOL_DIR",

        # Feature-specific volume dirs - only if the relevant feature is enabled.
        #  - internal IdP
        **({"auth": "BENTOV2_AUTH_VOL_DIR"} if not c.BENTOV2_USE_EXTERNAL_IDP else {}),
        #  - cBioPortal
        **({"cbioportal": "BENTO_CBIOPORTAL_STUDY_DIR"} if c.BENTO_CBIOPORTAL_ENABLED else {}),
    }

    task_print("Creating temporary secrets directory if needed...")
    secrets_dir = pathlib.Path.cwd() / "tmp" / "secrets"
    secrets_dir_exists = secrets_dir.exists()
    secrets_dir.mkdir(parents=True, exist_ok=True)
    task_print_done(msg="already exists." if secrets_dir_exists else "done.")

    print("Creating data directories if needed... this may ask you for your password to set permissions.")
    for dir_for, dir_var in data_dir_vars.items():
        task_print(f"  {dir_for}")

        data_dir = os.getenv(dir_var)
        if data_dir is None:
            err(f"error: {dir_for} data directory ({dir_var}) is not set")
            exit(1)

        data_dir_path = pathlib.Path(data_dir)
        already_exists = data_dir_path.exists()

        if already_exists and (data_dir_owner := data_dir_path.owner()) != c.BENTO_USERNAME:
            err(f"error: data directory {data_dir_path} exists, but is owned by {data_dir_owner}. please fix this!")
            exit(1)

        data_dir_path.mkdir(parents=True, exist_ok=True)
        task_print_done(msg="already exists." if already_exists else "done.")


def init_docker(client: docker.DockerClient):
    # Init swarm
    #
    # try:
    #     task_print("Initializing Docker Swarm, if necessary...")
    #     swarm_id = client.swarm.init()
    #     task_print_done()
    #     info(f"Swarm ID: {swarm_id}")
    # except docker.errors.APIError as e:
    #     warn(" error encountered, skipping.")  # continues on the task_print line
    #     warn(f"    Likely due to Docker already being in Swarm mode ({e})")

    # Init Docker network(s)

    # network environment variable, kwargs
    networks = (
        ("BENTO_AGGREGATION_NETWORK", dict(driver="bridge")),
        ("BENTO_AUTH_NETWORK", dict(driver="bridge")),
        ("BENTO_AUTH_DB_NETWORK", dict(driver="bridge", internal=True)),  # Does not need to access the web
        ("BENTO_BEACON_NETWORK", dict(driver="bridge")),
        ("BENTO_CBIOPORTAL_NETWORK", dict(driver="bridge")),
        ("BENTO_CBIOPORTAL_DATABASE_NETWORK", dict(driver="bridge", internal=True)),  # Does not need to access the web
        ("BENTO_CBIOPORTAL_SESSION_NETWORK", dict(driver="bridge")),
        ("BENTO_DROP_BOX_NETWORK", dict(driver="bridge")),
        ("BENTO_DRS_NETWORK", dict(driver="bridge")),
        ("BENTO_EVENT_RELAY_NETWORK", dict(driver="bridge")),
        ("BENTO_GOHAN_API_NETWORK", dict(driver="bridge")),
        ("BENTO_GOHAN_ES_NETWORK", dict(driver="bridge", internal=True)),  # Does not need to access the web
        ("BENTO_KATSU_NETWORK", dict(driver="bridge")),
        ("BENTO_KATSU_DB_NETWORK", dict(driver="bridge", internal=True)),  # Does not need to access the web
        ("BENTO_NOTIFICATION_NETWORK", dict(driver="bridge")),
        ("BENTO_PUBLIC_NETWORK", dict(driver="bridge")),
        ("BENTO_REDIS_NETWORK", dict(driver="bridge", internal=True)),  # Does not need to access the web
        ("BENTO_SERVICE_REGISTRY_NETWORK", dict(driver="bridge")),
        ("BENTO_WEB_NETWORK", dict(driver="bridge")),
        ("BENTO_WES_NETWORK", dict(driver="bridge")),
    )

    for net_var, net_kwargs in networks:
        task_print(f"Creating Docker network (var: {net_var}) if needed...")

        net_name = os.getenv(net_var)
        if not net_name:
            cprint(f"failed ({net_var} not set).", "red")

        try:
            client.networks.get(net_name)
            task_print_done(f"exists already (name: {net_name}).")
        except docker.errors.NotFound:
            client.networks.create(net_name, **net_kwargs)
            task_print_done(f"network created (name: {net_name}).")


# def init_secrets(force: bool):
#     client = docker.from_env()
#     katsu_vars = {
#         "user": {
#             "env_var": "BENTOV2_KATSU_DB_USER",
#             "secret_name": "metadata-db-user"
#         },
#         "pw": {
#             "env_var": "BENTOV2_KATSU_DB_PASSWORD",
#             "secret_name": "metadata-db-secret"
#         },
#         "secret": {
#             "env_var": "BENTOV2_KATSU_DB_APP_SECRET",
#             "secret_name": "metadata-app-secret"
#         }
#     }
#
#     for secret_type in katsu_vars.keys():
#         env_var, secret_name = katsu_vars[secret_type].values()
#         val = os.getenv(env_var)
#         val_bytes = bytes(val, "UTF-8")
#         path = (pathlib.Path.cwd() / "tmp" / "secrets" / secret_name)
#
#         task_print(f"Creating secret for {secret_type}: {secret_name} ...")
#
#         existing_secrets = [scrt for scrt in client.secrets.list(filters={"name": secret_name}) if scrt is not None]
#
#         if not existing_secrets:
#             with open(path, "wb") as f:
#                 f.write(val_bytes)
#             client.secrets.create(name=secret_name, data=val_bytes)
#             task_print_done()
#
#         elif force:
#             for scrt in existing_secrets:
#                 client.api.remove_secret(scrt.id)
#             with open(path, "wb") as f:
#                 f.write(val_bytes)
#             client.secrets.create(name=secret_name, data=val_bytes)
#             task_print_done()
#
#         else:
#             warn(f"  {secret_name} already exists, skipping.")
#
#     # TODO: Use Hashicorp/Vault for more secure secret mgmt?
#
#
# def clean_secrets():
#     client = docker.from_env()
#     for secret in client.secrets.list():
#         task_print(f"Removing secret: {secret.id} ...")
#         success = client.api.remove_secret(secret.id)
#         if success:
#             task_print_done()
#         else:
#             err("failed.")


def clean_logs():
    # TODO
    pass
