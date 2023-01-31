import os
import pathlib
import shutil
import docker
from termcolor import cprint
from .openssl import _create_cert, _create_private_key


def init_web(service: str):
    if service not in ["public", "private"]:
        cprint("You must specify the service type (public or private)")
        exit(1)

    if service == "public":
        _init_web_public()
    elif service == "private":
        _init_web_private()


def _init_web_public():
    root_path = pathlib.Path.cwd()

    # Init lib dir
    public_path = (root_path / "lib" / "public")
    translation_path = (public_path / "translations")
    translation_path.mkdir(parents=True, exist_ok=True)

    # About html page
    _file_copy(
        (root_path / "etc" / "default.about.html"),
        (public_path / "about.html")
    )
    # Branding image
    _file_copy(
        (root_path / "etc" / "default.public.branding.png"),
        (public_path / "branding.png")
    )
    # English translations
    _file_copy(
        (root_path / "etc" / "templates" / "translations" / "en.example.json"),
        (translation_path / "en.json")
    )
    # French translations
    _file_copy(
        (root_path / "etc" / "templates" / "translations" / "fr.example.json"),
        (translation_path / "fr.json")
    )

def _file_copy(src_path: pathlib.Path, dst_path: pathlib.Path):
    if dst_path.is_file():
        print(f"File {dst_path} exists, skipping copy.")
    else:
        print(f"Copying {src_path} to {dst_path}...", end="")
        shutil.copyfile(src_path, dst_path)
        cprint("done.", "green")


def _init_web_private():
    print("Init public web folder with branding image ...", end="")
    root_path = pathlib.Path.cwd()
    web_path = (root_path / "lib" / "web")
    web_path.mkdir(parents=True, exist_ok=True)

    src_file = (root_path / "etc" / "default.branding.png")
    dst_file = (web_path / "branding.png")
    shutil.copyfile(src=src_file, dst=dst_file)
    cprint(" done.", "green")


def init_self_signed_certs(force: bool):
    cert_domains_vars = {
        "public": {
            "var": "BENTOV2_DOMAIN",
            "priv_key_name": "privkey1.key",
            "crt": "fullchain1.crt"
        },
        "portal": {
            "var": "BENTOV2_PORTAL_DOMAIN",
            "priv_key_name": "portal_privkey1.key",
            "crt": "portal_fullchain1.crt"
        },
        "auth": {
            "var": "BENTOV2_AUTH_DOMAIN",
            "priv_key_name": "auth_privkey1.key",
            "crt": "auth_fullchain1.crt"
        }
    }

    # Init cert directory in gateway
    certs_dir = (pathlib.Path.cwd() / "certs")
    print("Creating certs directory if needed... ", end="")
    certs_dir.mkdir(parents=True, exist_ok=True)
    cprint("done.", "green")

    # Check for existing cert files first
    cert_files = list(certs_dir.glob('*.crt')) + \
        list(certs_dir.glob('*.key')) + list(certs_dir.glob("*.pem"))
    if not force and any(cert_files):
        cprint(
            "WARNING: Cert files detected in the target directory, new cert creation skipped.",
            "yellow")
        cprint(
            "To create new certs, remove all \".crt\" and \".key\" files in target directory first.",
            "yellow")
        for f in cert_files:
            cprint(f"Cert file path: {f}", "yellow")
        return

    for domain in cert_domains_vars.keys():
        domain_var, priv_key_name, crt_name = cert_domains_vars[domain].values(
        )
        domain_val = os.getenv(domain_var)

        if domain_val is None:
            cprint(
                f"error: {domain_var} env variable ({domain}) is not set",
                "red")
            exit(1)

        #  Create private key for domain
        print(
            f"Creating .key file for domain: {domain} -> {domain_val} ... ", end="")
        pkey = _create_private_key(certs_dir, priv_key_name)
        cprint("done.", "green")

        # Create signed cert for domain
        print("Creating certificate file for domain: {} -> {} ... ".format(domain, domain_val), end="")
        _create_cert(certs_dir, pkey, crt_name, domain_val)
        cprint("done.", "green")


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
            cprint(
                f"error: {dir_for} data directory ({dir_var}) is not set",
                "red")
            exit(1)

        pathlib.Path(os.getenv(dir_var)).mkdir(parents=True, exist_ok=True)
        cprint("done.", "green")


def init_docker():
    client: docker.DockerClient = docker.from_env()

    # Init swarm
    try:
        print("Initializing docker swarm, if necessary ...", end="")
        swarm_id = client.swarm.init()
        cprint("done.", "green")
        print(f"Swarm id: {swarm_id}")
    except docker.errors.APIError:
        cprint("   Error encountered, skipping.", "red")
        cprint("   Likely due to docker already being in a swarm.", "yellow")

    # Init Docker network(s)

    base_net_name = "bridge-net"
    print(f"Creating docker network ({base_net_name}) if needed... ", end="")
    try:
        client.networks.get(base_net_name)
        cprint("exists already, done.", "green")
    except docker.errors.NotFound:
        client.networks.create("bridge-net", driver="bridge")
        cprint("network created, done.", "green")


def init_secrets(force: bool):
    client = docker.from_env()
    katsu_vars = {
        "user": {
            "env_var": "BENTOV2_KATSU_DB_USER",
            "secret_name": "metadata-db-user"
        },
        "pw": {
            "env_var": "BENTOV2_KATSU_DB_PASSWORD",
            "secret_name": "metadata-db-secret"
        },
        "secret": {
            "env_var": "BENTOV2_KATSU_DB_APP_SECRET",
            "secret_name": "metadata-app-secret"
        }
    }

    for secret_type in katsu_vars.keys():
        env_var, secret_name = katsu_vars[secret_type].values()
        val = os.getenv(env_var)
        val_bytes = bytes(val, 'UTF-8')
        path = (pathlib.Path.cwd() / "tmp" / "secrets" / secret_name)

        print(f"Creating secret for {secret_type}: {secret_name} ...", end="")
        existing_secrets = [scrt for scrt in client.secrets.list(filters={"name": secret_name}) if scrt is not None]
        if len(existing_secrets) == 0:
            with open(path, "wb") as f:
                f.write(val_bytes)
            client.secrets.create(name=secret_name, data=val_bytes)
            cprint(" done.", "green")
        elif force:
            for scrt in existing_secrets:
                client.api.remove_secret(scrt.id)
            with open(path, "wb") as f:
                f.write(val_bytes)
            client.secrets.create(name=secret_name, data=val_bytes)
            cprint(" done.", "green")
        else:
            cprint(f" {secret_name} already exists, skipping.", "yellow")

    # TODO: Use Hashicorp/Vault for more secure secret mgmt?


def clean_secrets():
    client = docker.from_env()
    for secret in client.secrets.list():
        print(f"Removing secret: {secret.id} ... ", end="")
        success = client.api.remove_secret(secret.id)
        if success:
            cprint("done.", "green")
        else:
            cprint("failed.", "red")


def clean_logs():
    # TODO
    pass
