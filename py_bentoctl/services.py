import docker
import os
import pathlib
import subprocess

from termcolor import cprint

from .config import BENTO_DOCKER_SERVICES, COMPOSE, BENTO_SERVICES_DATA
from .state import MODE_DEV, MODE_PROD, get_state, set_state_services

__all__ = [
    "run_service",
    "stop_service",
    "restart_service",
    "clean_service",
    "work_on_service",
    "enter_shell_for_service",
    "run_as_shell_for_service",
]

BENTO_SERVICES_DATA_BY_KIND = {
    v["service_kind"]: {**v, "compose_id": k}
    for k, v in BENTO_SERVICES_DATA.items()
}


compose_with_files_prod = (*COMPOSE, "-f", "docker-compose.yaml", "-f", "docker-compose.prod.yaml")
compose_with_files_dev = (*COMPOSE, "-f", "docker-compose.yaml", "-f", "docker-compose.dev.yaml")


# TODO: More elegant solution for service-image associations
service_image_vars = {
    "aggregation": ("BENTOV2_AGGREGATION_IMAGE", "BENTOV2_AGGREGATION_VERSION"),
    "auth": ("BENTOV2_AUTH_IMAGE", "BENTOV2_AUTH_VERSION"),
    "beacon": ("BENTO_BEACON_IMAGE", "BENTO_BEACON_VERSION"),
    "drop-box": ("BENTOV2_DROP_BOX_IMAGE", "BENTOV2_DROP_BOX_VERSION"),
    "drs": ("BENTOV2_DRS_IMAGE", "BENTOV2_DRS_VERSION"),
    "event-relay": ("BENTOV2_EVENT_RELAY_IMAGE", "BENTOV2_EVENT_RELAY_VERSION"),
    "gateway": ("BENTOV2_GATEWAY_IMAGE", "BENTOV2_GATEWAY_VERSION"),
    "gohan-api": ("BENTOV2_GOHAN_API_IMAGE", "BENTOV2_GOHAN_API_VERSION"),
    "gohan-elasticsearch": ("BENTOV2_GOHAN_ES_IMAGE", "BENTOV2_GOHAN_ES_VERSION"),
    "katsu": ("BENTOV2_KATSU_IMAGE", "BENTOV2_KATSU_VERSION"),
    "notification": ("BENTOV2_NOTIFICATION_IMAGE", "BENTOV2_NOTIFICATION_VERSION"),
    "public": ("BENTO_PUBLIC_IMAGE", "BENTO_PUBLIC_VERSION"),
    "service-registry": ("BENTOV2_SERVICE_REGISTRY_IMAGE", "BENTOV2_SERVICE_REGISTRY_VERSION"),
    "wes": ("BENTOV2_WES_IMAGE", "BENTOV2_WES_VERSION"),
}


docker_client = docker.from_env()


def translate_service_aliases(service: str):
    if service in BENTO_SERVICES_DATA_BY_KIND:
        return BENTO_SERVICES_DATA_BY_KIND[service]["compose_id"]

    return service


def _run_service_in_dev_mode(compose_service: str):
    print(f"Running {compose_service} in development mode...")
    subprocess.check_call((*compose_with_files_dev, "up", "-d", compose_service))


def _run_service_in_prod_mode(compose_service: str):
    print(f"Running {compose_service} in production mode...")
    subprocess.check_call((*compose_with_files_prod, "up", "-d", compose_service))


def run_service(compose_service: str):
    compose_service = translate_service_aliases(compose_service)

    service_state = get_state()["services"]

    # TODO: Look up dev/prod mode based on compose_service

    if compose_service == "all":
        # special: run everything
        subprocess.check_call((*compose_with_files_prod, "up", "-d"))

        for service, service_settings in service_state.items():
            if service_settings["mode"] == MODE_DEV:
                _run_service_in_dev_mode(service)

        return

    if compose_service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {compose_service} not in list of services: {BENTO_DOCKER_SERVICES}", "red")
        exit(1)

    if service_state[compose_service]["mode"] == MODE_DEV:
        _run_service_in_dev_mode(compose_service)
    else:
        _run_service_in_prod_mode(compose_service)


def stop_service(compose_service: str):
    compose_service = translate_service_aliases(compose_service)

    if compose_service == "all":
        # special: stop everything
        subprocess.check_call((*COMPOSE, "down"))
        return

    if compose_service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {compose_service} not in list of services: {BENTO_DOCKER_SERVICES}", "red")
        exit(1)

    print(f"Stopping {compose_service}...")
    subprocess.check_call((*COMPOSE, "stop", compose_service))


def restart_service(compose_service: str):
    stop_service(compose_service)
    run_service(compose_service)


def clean_service(compose_service: str):
    compose_service = translate_service_aliases(compose_service)

    if compose_service == "all":
        # special: stop everything
        for s in BENTO_DOCKER_SERVICES:
            clean_service(s)
        return

    if compose_service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {compose_service} not in list of services: {BENTO_DOCKER_SERVICES}")
        exit(1)

    print(f"Stopping {compose_service}...")
    subprocess.check_call((*COMPOSE, "rm", "-svf", compose_service))


def work_on_service(compose_service: str):
    compose_service = translate_service_aliases(compose_service)

    service_state = get_state()["services"]

    if compose_service == "all":
        cprint(f"  Cannot work on all services.", "red")
        exit(1)

    if compose_service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {compose_service} not in list of services: {BENTO_DOCKER_SERVICES}")
        exit(1)

    if compose_service not in BENTO_SERVICES_DATA:
        cprint(f"  {compose_service} not in bento_services.json: {list(BENTO_SERVICES_DATA.keys())}")
        exit(1)

    if not (repo_path := pathlib.Path.cwd() / "repos" / compose_service).exists():
        # Clone the repository if it doesn't already exist
        cprint(f"  Cloning {compose_service} repository into repos/ ...", "blue")
        # TODO: clone ssh...
        subprocess.check_call(("git", "clone", BENTO_SERVICES_DATA[compose_service]["repository"], repo_path))
        # TODO

    # Save state change
    set_state_services({
        **service_state,
        compose_service: {
            **service_state[compose_service],
            "mode": MODE_DEV,
        },
    })

    # Clean up existing container
    clean_service(compose_service)

    # Start new dev container
    _run_service_in_dev_mode(compose_service)


def prod_service(compose_service: str):
    compose_service = translate_service_aliases(compose_service)

    service_state = get_state()["services"]

    if compose_service == "all":
        # TODO
        pass

    if compose_service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {compose_service} not in list of services: {BENTO_DOCKER_SERVICES}")
        exit(1)

    if compose_service not in BENTO_SERVICES_DATA:
        cprint(f"  {compose_service} not in bento_services.json: {list(BENTO_SERVICES_DATA.keys())}")
        exit(1)

    # Save state change
    set_state_services({
        **service_state,
        compose_service: {
            **service_state[compose_service],
            "mode": MODE_PROD,
        },
    })

    # Clean up existing container
    clean_service(compose_service)

    # Start new dev container
    _run_service_in_prod_mode(compose_service)


def pull_service(compose_service: str):
    compose_service = translate_service_aliases(compose_service)

    if compose_service == "all":
        # special: run everything
        subprocess.check_call((*COMPOSE, "pull"))
        return

    if compose_service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {compose_service} not in list of services: {BENTO_DOCKER_SERVICES}", "red")
        exit(1)

    print(f"Pulling {compose_service}...")

    image_t = service_image_vars.get(compose_service)
    if image_t is None:
        cprint(f"  {compose_service} not in service_image_vars keys: {list(service_image_vars.keys())}", "red")
        exit(1)

    image_var, image_version_var = image_t
    image = os.getenv(image_var)
    image_version = os.getenv(image_version_var)

    if image is None:
        cprint(f"  {image_var} is not set", "red")
        exit(1)
    if image_version is None:
        cprint(f"  {image_version_var} is not set", "red")
        exit(1)

    # TODO: Pull dev if in dev mode
    subprocess.check_call(("docker", "pull", f"{image}:{image_version}"))  # Use subprocess to get nice output
    subprocess.check_call((*COMPOSE, "pull", compose_service))


def enter_shell_for_service(compose_service: str, shell: str):
    compose_service = translate_service_aliases(compose_service)

    if compose_service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {compose_service} not in list of services: {BENTO_DOCKER_SERVICES}")
        exit(1)

    cmd = COMPOSE[0]
    compose_args = COMPOSE[1:]
    os.execvp(cmd, (cmd, *compose_args, "exec", "-it", compose_service, shell))  # TODO: Detect shell


def run_as_shell_for_service(compose_service: str, shell: str):
    compose_service = translate_service_aliases(compose_service)

    if compose_service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {compose_service} not in list of services: {BENTO_DOCKER_SERVICES}")
        exit(1)

    cmd = COMPOSE[0]
    compose_args = COMPOSE[1:]
    os.execvp(cmd, (cmd, *compose_args, "run", compose_service, shell))  # TODO: Detect shell
