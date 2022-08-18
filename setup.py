import os
# import subprocess
from os import path
from os.path import join, dirname
import sys
from envsubst import envsubst
from dotenv import load_dotenv
import shutil
import docker
from git import Repo
from colors import *
from scripts.openssl import cert_gen

docker_client = docker.from_env()
ABS_PATH = dirname(path.abspath(__file__))


def exit_error(msg, e=None):
    if e:
        print_error(e)
    print_error(msg)
    print_error("Exiting")
    sys.exit(1)


def set_up():
    if not path.isdir(join(ABS_PATH, 'temp')):
        os.mkdir(join(ABS_PATH, 'temp'))


def env_setup():
    print_info("-- Setting up environment variables --")
    try:
        if path.exists(join(ABS_PATH, '.env')):
            print_success(".env file already exists")
        else:
            shutil.copy(join(ABS_PATH, 'etc', 'bento.env'), join(ABS_PATH, '.env'))
            print_success("Duplicated")
            set_env_vars()

        load_dotenv(dotenv_path=join(ABS_PATH, '.env'), verbose=True)
    except Exception as e:
        exit_error("Failed to load environment variables", e)

    try:
        print("Duplicating ./etc/katsu.config.example.json to ./lib/katsu/config.json ...")
        if path.exists(join(ABS_PATH, 'etc', 'katsu.config.example.json')):
            shutil.copy(join(ABS_PATH, 'etc', 'katsu.config.example.json'), join(ABS_PATH, 'lib', 'katsu', 'config.json'))
            print_success("Duplicated")
        else:
            exit_error("./etc/katsu.config.example.json not found")
    except Exception as e:
        exit_error("Failed to load katsu config", e)


def katsu_config_setup():
    print_info("-- Setting up Katsu config file --")
    try:
        if path.exists(join(ABS_PATH, 'lib', 'katsu', 'config.json')):
            print("Katsu config already exists")
        else:
            print("Duplicating ./etc/bento.env to ./env")
            if path.exists(join(ABS_PATH, 'etc/bento.env')):
                shutil.copy(join(ABS_PATH, 'etc/bento.env'), join(ABS_PATH, 'env'))
            else:
                print("No ./etc/bento.env file found")
                print("Exiting")
                sys.exit(1)
        load_dotenv(dotenv_path=join(ABS_PATH, '.env'), verbose=True)
    except Exception as e:
        exit_error("Failed to load environment variables", e)


def init_chord_services():
    print_info("-- Initializing CHORD service configuration files  --")

    # copy services json to the microservices that need it
    try:
        print("loading ./etc/templates/chord_services.example.json")
        if path.exists(join(ABS_PATH, 'etc', 'templates', 'chord_services.example.json')):
            with open(join(ABS_PATH, 'etc', 'templates', 'chord_services.example.json'), 'r') as f:
                print("substituting environment variables in chord_services.example.json")
                services_json = envsubst(f.read())
            with open(join(ABS_PATH, "temp", "temp.chord.json"), 'w') as f:
                f.write(services_json)

            print("saving chord_services.json to ./lib/logging")
            shutil.copy(join(ABS_PATH, "temp", "temp.chord.json"), join(ABS_PATH, "lib", "logging", "chord_services.json"))

            print("saving chord_services.json to ./lib/service-registry")
            shutil.copy(join(ABS_PATH, "temp", "temp.chord.json"), join(ABS_PATH, "lib", "service-registry", "chord_services.json"))

            print("saving chord_services.json to ./lib/wes")
            shutil.copy(join(ABS_PATH, "temp", "temp.chord.json"), join(ABS_PATH, "lib", "wes", "chord_services.json"))

        else:
            print("No ./etc/templates/chord_services.example.json file found")
            print("Exiting")
            sys.exit(1)
    except Exception as e:
        print(e)
        print("Failed to load chord_services.example.json")
        sys.exit(1)


def init_dirs():
    print_info("-- Initializing temp and data directories --")

    print("Creating tmp dir...")
    if not path.exists(join(ABS_PATH, 'tmp')):
        os.mkdir(join(ABS_PATH, 'tmp'))
        print_success("Created")
    else:
        print_warning("tmp dir already exists")

    try:
        print("Creating tmp/secretes dir...")
        if not path.exists(join(ABS_PATH, 'tmp', 'secrets')):
            os.mkdir(join(ABS_PATH, 'tmp', 'secrets'))
            print_success("Created")
        else:
            print_warning("tmp/secrets dir already exists")
    except Exception as e:
        print(e)
        print("Failed to create temporary secrets dir")
        sys.exit(1)
    print("Creating temporary deployment logs dir...")

    try:
        if not path.exists(join(ABS_PATH, 'tmp', 'logs')):
            os.mkdir(join(ABS_PATH, 'tmp', 'logs'))
            print_success("Created")

    except Exception as e:
        print(e)
        print("Failed to create temporary deployment logs dir")
        sys.exit(1)


def data_dirs():
    print_info("-- Initializing data directories --")
    print("Creating data directories...")

    root_data_dir_path = os.environ['BENTOV2_ROOT_DATA_DIR']
    try:
        os.mkdir(root_data_dir_path)
    except Exception as e:
        print_error(e)
        print_error("Failed to create data dir")
        print_error(f"Fetched path {root_data_dir_path}")
        sys.exit(1)

    auth_vol_dir_path = os.environ['BENTOV2_AUTH_VOL_DIR']
    try:
        os.mkdir(auth_vol_dir_path)
    except Exception as e:
        print_error(e)
        print_error("Failed to create auth_vol_dir_path")
        print_error(f"Fetched path {auth_vol_dir_path}")
        sys.exit(1)

    katsu_db_prod_vol_dir_path = os.environ['BENTOV2_KATSU_DB_PROD_VOL_DIR']
    try:
        os.mkdir(katsu_db_prod_vol_dir_path)
    except Exception as e:
        print_error(e)
        print_error("Failed to create katsu_db_prod_vol_dir_path")
        print_error(f"Fetched path {katsu_db_prod_vol_dir_path}")
        sys.exit(1)

    notification_vol_dir_path = os.environ['BENTOV2_NOTIFICATION_VOL_DIR']
    try:
        os.mkdir(notification_vol_dir_path)
    except Exception as e:
        print_error(e)
        print_error("Failed to create notification_vol_dir_path")
        print_error(f"Fetched path {notification_vol_dir_path}")
        sys.exit(1)

    federation_prod_vol_dir_path = os.environ['BENTOV2_FEDERATION_PROD_VOL_DIR']
    try:
        os.mkdir(federation_prod_vol_dir_path)
    except Exception as e:
        print_error(e)
        print_error("Failed to create federation_prod_vol_dir_path")
        print_error(f"Fetched path {federation_prod_vol_dir_path}")
        sys.exit(1)

    wes_vol_dir_path = os.environ['BENTOV2_WES_VOL_DIR']
    try:
        os.mkdir(wes_vol_dir_path)
    except Exception as e:
        print_error(e)
        print_error("Failed to create wes_vol_dir_path")
        print_error(f"Fetched path {wes_vol_dir_path}")
        sys.exit(1)

    redis_vol_dir_path = os.environ['BENTOV2_REDIS_VOL_DIR']
    try:
        os.mkdir(redis_vol_dir_path)
    except Exception as e:
        print_error(e)
        print_error("Failed to create redis_vol_dir_path")
        print_error(f"Fetched path {redis_vol_dir_path}")
        sys.exit(1)

    print('Data directories created')


def clean_up():
    print("-- Cleaning up --")
    try:
        if path.exists(join(ABS_PATH, 'temp')):
            shutil.rmtree(join(ABS_PATH, 'temp'))
    except Exception as e:
        print_error(e)
        print_error("Failed to clean up")
        sys.exit(1)


def init_docker():
    print_info("-- Initializing Docker --")

    # Swarm for docker Secrets
    print("-- Initializing Docker Swarm for docker secrets (this may crash if already set) --")
    try:
        # subprocess.run(['docker', 'swarm', 'init'])
        docker_client.swarm.init()
    except docker.errors.APIError as e:
        print("Swarm already initialized")
    except Exception as e:
        print_error(e)
        print_error("Failed to initialize Docker Swarm")
        sys.exit(1)

    # Internal cluster network
    if len(docker_client.networks.list("bridge-net")) == 0:
        print_info("-- Initializing Docker Internal Cluster Network --")
        try:
            # subprocess.run(['docker', 'network', 'create', 'bridge-net'])
            docker_client.networks.create('bridge-net')
            print_success("Docker Internal Cluster Network created")
        except Exception as e:
            print_error(e)
            print_error("Failed to initialize Docker Internal Cluster Network")
            sys.exit(1)
    else:
        print_success("Docker Internal Cluster Network already initialized")


def init_gohan():
    print_info("-- Initializing Gohan --")
    gohan_path = join(ABS_PATH, 'lib', 'gohan')

    if path.isdir(gohan_path) and len(os.listdir(gohan_path)) > 0:
        print_success("Gohan already cloned")
    else:
        print("Cloning Gohan...")
        try:
            repo = Repo.clone_from(os.environ['GOHAN_REPO'], gohan_path)
            print_success("Gohan cloned")
            if os.environ['GOHAN_BRANCH']:
                repo.git.checkout(os.environ['GOHAN_BRANCH'])
                print_success("Checked out gohan to branch " + os.environ['GOHAN_BRANCH'])
            else:
                print_warning("No gohan branch specified, using master")

        except Exception as e:
            print_error(e)
            print_error("Failed to clone gohan")
            print_error("Exiting")
            sys.exit(1)

    print("Creating .env file...")
    try:
        shutil.copy(join(gohan_path, 'etc', 'example.env'), join(gohan_path, '.env'))
        print_success("Gohan .env file created")
        print_warning("Set Gohan environment variables as described in README.md")
        input("Press enter to continue...")
    except Exception as e:
        exit_error("Failed to create gohan .env file", e)

    load_dotenv(join(gohan_path, '.env'))
    print_success("Gohan environment variables set")


def init_bento_public():
    print_info("-- Initializing Bento Public --")
    bento_public_path = join(ABS_PATH, 'lib', 'bento_public')

    if path.isdir(bento_public_path) and len(os.listdir(bento_public_path)) > 0:
        print_success("Bento Public already cloned")
    else:
        print("Cloning Bento Public...")
        try:
            repo = Repo.clone_from(os.environ['BENTO_PUBLIC_REPO'], bento_public_path)
            print_success("Bento Public cloned")
            if os.environ['BENTO_PUBLIC_BRANCH']:
                repo.git.checkout(os.environ['BENTO_PUBLIC_BRANCH'])
                print_success("Checked out Bento Public to branch " + os.environ['BENTO_PUBLIC_BRANCH'])
            else:
                print_warning("No Bento Public branch specified, using master")

        except Exception as e:
            print(e)
            print_error("Failed to clone Bento Public")
            print_error("Exiting")
            sys.exit(1)

    print("Creating client.env and server.env files...")

    try:
        if path.isfile(join(bento_public_path, 'server.env')):
            print_warning(f"{join(bento_public_path, 'server.env')} already exists, Moving on")
        else:
            shutil.copy(join(bento_public_path, 'etc', 'example.server.env'), join(bento_public_path, 'server.env'))
            print_success("Bento Public server.env file created")

        if path.isfile(join(bento_public_path, 'client.env')):
            print_warning(f"{join(bento_public_path, 'client.env')} already exists, Moving on")
        else:
            shutil.copy(join(bento_public_path, 'etc', 'example.client.env'), join(bento_public_path, 'client.env'))
            print_success("Bento Public client.env file created")

        print_success("Bento Public env files created")
    except Exception as e:
        print_error(e)
        print_error("Failed to create Bento Public .env file")
        print_error("Exiting")
        sys.exit(1)

    print_warning("Set Bento Public environment variables as described in README.md")
    input("Press enter to continue...")


def docker_secrets():
    print_info("-- Creating Docker Secrets --")
    #
    # print("Creating Admin User...")
    # try:
    #
    #     docker_client.secrets.create(os.environ['BENTO_V2_SECRET_PATH'], './bento_v2_secret.json')
    # except Exception as e:
    #     exit_error("Failed to create Admin User", e)


def set_env_vars():
    print_warning("Set Environment Variables (Refer to README.md for more info)")
    input("Press ENTER to continue...")


def auth_setup():
    pass


def boot_gateway_controller():
    init_chord_services()
    init_dirs()
    init_docker()
    docker_secrets()
    
    auth_setup()


def create_certificates():
    print_info("-- Creating Certificates --")

    certs_path = join(ABS_PATH, 'lib', 'gateway', 'certs')
    print(f"Creating {certs_path}...")
    if not path.isdir(certs_path):
        os.mkdir(certs_path)
    else:
        print_warning(f"{certs_path} already exists, Moving on")

    print("Creating Certificates for gateway private...")
    print(f"Creating > Private key: certs/privkey1.key & certificate: certs/fullchain1.crt")
    try:
        cert_gen(KEY_FILE=join(certs_path, 'privkey1.key'),
                 CERT_FILE=join(certs_path, 'fullchain1.crt'))
        print_success("Certificates created")

    except Exception as e:
        exit_error("Failed to create private certificates", e)

    print("Creating Certificates for gateway portal...")
    print("Creating > Private key: certs/portal_privkey1.key & certificate: certs/portal_fullchain1.crt")
    try:
        cert_gen(KEY_FILE=join(ABS_PATH, 'lib', 'gateway', 'certs', 'portal_privkey1.key'),
                 CERT_FILE=join(ABS_PATH, 'lib', 'gateway', 'certs', 'portal_fullchain1.crt'))
        print_success("Certificates created")

    except Exception as e:
        exit_error("Failed to create portal certificates", e)

    print("Creating Certificates for auth...")
    print("Creating > Private key: certs/auth_privkey1.key & certificate: certs/auth_fullchain1.crt")
    try:
        cert_gen(KEY_FILE=join(ABS_PATH, 'lib', 'gateway', 'certs', 'auth_privkey1.key'),
                 CERT_FILE=join(ABS_PATH, 'lib', 'gateway', 'certs', 'auth_fullchain1.crt'))
        print_success("Certificates created")

    except Exception as e:
        exit_error("Failed to create auth certificates", e)


def set_gohan_env_vars():
    pass


def set_bento_public_env_vars():
    pass


def main():
    print_finish("-- Starting BentoV2 Setup --")
    set_up()
    env_setup()
    
    init_gohan()
    init_bento_public()
    
    create_certificates()
    
    boot_gateway_controller()
    
    clean_up()
    print_finish("-- Setup complete --")

    
if __name__ == '__main__':
    main()
    sys.exit(0)
