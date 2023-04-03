import os
import pathlib
import subprocess

from termcolor import cprint
from typing import Callable, Dict, Optional, Tuple

from . import config as c
from .state import MODE_LOCAL, MODE_PREBUILT, get_state, set_state_services
from .utils import info, err

__all__ = [
    "run_service",
    "stop_service",
    "restart_service",
    "clean_service",
    "work_on_service",
    "enter_shell_for_service",
    "run_as_shell_for_service",
    "logs_service",
]

BENTO_SERVICES_DATA_BY_KIND = {
    v["service_kind"]: {**v, "compose_id": k}
    for k, v in c.BENTO_SERVICES_DATA.items()
    if v.get("service_kind")
}

BENTO_USER_EXCLUDED_SERVICES = (
    "auth",
    "gateway",
    "katsu-db",
    "redis",
)


def _get_profile_cli_args():
    for p in c.get_enabled_feature_profiles():
        yield "--profile"
        yield p


def _get_compose_with_files(dev: bool = False, local: bool = False):
    if not dev and local:
        raise NotImplementedError("Local mode not implemented with prod")

    return (
        *c.COMPOSE,
        "-f", c.DOCKER_COMPOSE_FILE_BASE,

        # Service/feature-specific compose files - profiles will take care of actual service enable/disable
        "-f", c.DOCKER_COMPOSE_FILE_AUTH,
        "-f", c.DOCKER_COMPOSE_FILE_BEACON,
        "-f", c.DOCKER_COMPOSE_FILE_CBIOPORTAL,
        "-f", c.DOCKER_COMPOSE_FILE_GOHAN,
        "-f", c.DOCKER_COMPOSE_FILE_PUBLIC,

        *(("-f", c.DOCKER_COMPOSE_FILE_DEV) if dev else ("-f", c.DOCKER_COMPOSE_FILE_PROD)),
        *(("-f", c.DOCKER_COMPOSE_FILE_LOCAL) if local else ()),

        *_get_profile_cli_args(),
    )


def _get_service_specific_compose(service: str):
    # For services that are only in docker-compose.dev.yaml (e.g. adminer)
    return _get_compose_with_files(dev=service in c.DOCKER_COMPOSE_DEV_SERVICES)


# TODO: More elegant solution for service-image associations
service_image_vars: Dict[str, Tuple[str, str, Optional[str]]] = {
    "aggregation": ("BENTOV2_AGGREGATION_IMAGE", "BENTOV2_AGGREGATION_VERSION", "BENTOV2_AGGREGATION_VERSION_DEV"),
    "auth": ("BENTOV2_AUTH_IMAGE", "BENTOV2_AUTH_VERSION", None),
    "auth-db": ("BENTO_AUTH_DB_IMAGE", "BENTO_AUTH_DB_VERSION", None),
    "beacon": ("BENTO_BEACON_IMAGE", "BENTO_BEACON_VERSION", "BENTO_BEACON_VERSION_DEV"),
    "drop-box": ("BENTOV2_DROP_BOX_IMAGE", "BENTOV2_DROP_BOX_VERSION", "BENTOV2_DROP_BOX_VERSION_DEV"),
    "drs": ("BENTOV2_DRS_IMAGE", "BENTOV2_DRS_VERSION", "BENTOV2_DRS_VERSION_DEV"),
    "event-relay": ("BENTOV2_EVENT_RELAY_IMAGE", "BENTOV2_EVENT_RELAY_VERSION", "BENTOV2_EVENT_RELAY_VERSION_DEV"),
    "gateway": ("BENTOV2_GATEWAY_IMAGE", "BENTOV2_GATEWAY_VERSION", "BENTOV2_GATEWAY_VERSION_DEV"),
    "gohan-api": ("BENTOV2_GOHAN_API_IMAGE", "BENTOV2_GOHAN_API_VERSION", "BENTOV2_GOHAN_API_VERSION_DEV"),
    "gohan-elasticsearch": ("BENTOV2_GOHAN_ES_IMAGE", "BENTOV2_GOHAN_ES_VERSION", None),
    "katsu": ("BENTOV2_KATSU_IMAGE", "BENTOV2_KATSU_VERSION", "BENTOV2_KATSU_VERSION_DEV"),
    "katsu-db": ("BENTOV2_KATSU_DB_IMAGE", "BENTOV2_KATSU_DB_VERSION", None),
    "notification": ("BENTOV2_NOTIFICATION_IMAGE", "BENTOV2_NOTIFICATION_VERSION", "BENTOV2_NOTIFICATION_VERSION_DEV"),
    "public": ("BENTO_PUBLIC_IMAGE", "BENTO_PUBLIC_VERSION", "BENTO_PUBLIC_VERSION_DEV"),
    "redis": ("BENTOV2_REDIS_BASE_IMAGE", "BENTOV2_REDIS_BASE_IMAGE_VERSION", None),
    "service-registry": ("BENTOV2_SERVICE_REGISTRY_IMAGE", "BENTOV2_SERVICE_REGISTRY_VERSION",
                         "BENTOV2_SERVICE_REGISTRY_VERSION_DEV"),
    "web": ("BENTOV2_WEB_IMAGE", "BENTOV2_WEB_VERSION", "BENTOV2_WEB_VERSION_DEV"),
    "wes": ("BENTOV2_WES_IMAGE", "BENTOV2_WES_VERSION", "BENTOV2_WES_VERSION_DEV"),
}


def translate_service_aliases(service: str, include_prefixes: bool = True) -> str:
    if service in BENTO_SERVICES_DATA_BY_KIND and (include_prefixes or service not in c.MULTI_SERVICE_PREFIXES):
        return BENTO_SERVICES_DATA_BY_KIND[service]["compose_id"]

    return service


def check_service_is_compose(compose_service: str) -> None:
    if compose_service not in c.DOCKER_COMPOSE_SERVICES:
        err(f"  {compose_service} not in Docker Compose services: {c.DOCKER_COMPOSE_SERVICES}")
        exit(1)


def _handle_multi_service_prefix(service: str, action: Callable[[str], None]):
    # E.g. with Gohan: 'gohan' is not actually a real Compose service;
    #   instead we <action> both API and ES (i.e., all Gohan stuff)

    for pf in c.MULTI_SERVICE_PREFIXES:
        if service == pf:
            for s in service_image_vars:
                if s.startswith(pf):
                    action(s)
            return


def _run_service_in_local_mode(compose_service: str) -> None:
    info(f"Running {compose_service} in local (development) mode...")
    subprocess.check_call((*_get_compose_with_files(dev=True, local=True), "up", "-d", compose_service))


def _run_service_in_prebuilt_mode(compose_service: str) -> None:
    info(f"Running {compose_service} in prebuilt ({'development' if c.DEV_MODE else 'production'}) mode...")
    subprocess.check_call((*_get_compose_with_files(dev=c.DEV_MODE, local=False), "up", "-d", compose_service))


def run_service(compose_service: str) -> None:
    compose_service = translate_service_aliases(compose_service)

    service_state = get_state()["services"]

    if compose_service == "all":
        # special: run everything
        subprocess.check_call((
            *_get_compose_with_files(dev=c.DEV_MODE, local=False),
            "up", "-d",
            *(
                s for s in c.DOCKER_COMPOSE_SERVICES
                if service_state.get(s, {}).get("mode") != MODE_LOCAL
            )
        ))

        for service, service_settings in service_state.items():
            if service_settings["mode"] == MODE_LOCAL:
                _run_service_in_local_mode(service)

        return

    if compose_service not in c.DOCKER_COMPOSE_SERVICES:
        err(f"  {compose_service} not in list of services: {c.DOCKER_COMPOSE_SERVICES}")
        exit(1)

    if service_state.get(compose_service, {}).get("mode") == MODE_LOCAL:
        _run_service_in_local_mode(compose_service)  # 'dev' / local mode
    else:
        _run_service_in_prebuilt_mode(compose_service)


def stop_service(compose_service: str) -> None:
    compose_service = translate_service_aliases(compose_service)

    if compose_service == "all":
        # special: stop everything
        subprocess.check_call((*_get_service_specific_compose(compose_service), "down"))
        return

    check_service_is_compose(compose_service)

    info(f"Stopping {compose_service}...")
    subprocess.check_call((*_get_service_specific_compose(compose_service), "stop", compose_service))


def restart_service(compose_service: str) -> None:
    stop_service(compose_service)
    run_service(compose_service)


def clean_service(compose_service: str) -> None:
    compose_service = translate_service_aliases(compose_service)

    if compose_service == "all":
        # special: stop everything
        for s in c.DOCKER_COMPOSE_SERVICES:
            clean_service(s)
        return

    check_service_is_compose(compose_service)

    info(f"Stopping {compose_service}...")
    subprocess.check_call((*_get_service_specific_compose(compose_service), "rm", "-svf", compose_service))


def work_on_service(compose_service: str) -> None:
    compose_service = translate_service_aliases(compose_service)
    service_state = get_state()["services"]

    if compose_service == "all":
        err("  Cannot work on all services.")
        exit(1)

    check_service_is_compose(compose_service)

    if compose_service not in c.BENTO_SERVICES_DATA:
        err(f"  {compose_service} not in bento_services.json: {list(c.BENTO_SERVICES_DATA.keys())}")
        exit(1)

    repo_path = pathlib.Path.cwd() / "repos" / compose_service
    if not repo_path.exists():
        # Clone the repository if it doesn't already exist
        cprint(f"  Cloning {compose_service} repository into repos/ ...", "blue")
        repo: str = c.BENTO_SERVICES_DATA[compose_service]["repository"]
        if c.BENTO_GIT_CLONE_HTTPS:
            repo = repo.replace("git@github.com:", "https://github.com/")
        subprocess.check_call(("git", "clone", "--recurse-submodules", repo, repo_path))
    else:
        # If the repository already exists, fetch tags to make sure we have any latest release tags
        subprocess.call(("git", "fetch", "--tags"), cwd=repo_path)

    # Save state change
    service_state = set_state_services({
        **service_state,
        compose_service: {
            **service_state[compose_service],
            "mode": MODE_LOCAL,
        },
    })["services"]

    # Clean up existing container
    clean_service(compose_service)

    # Pull new version of development container if needed
    pull_service(compose_service, service_state)

    # Start new dev container
    _run_service_in_local_mode(compose_service)


def prod_service(compose_service: str) -> None:
    compose_service = translate_service_aliases(compose_service)
    service_state = get_state()["services"]

    if compose_service == "all":
        for service in c.BENTO_SERVICES_DATA:
            prod_service(service)
        return

    check_service_is_compose(compose_service)

    if compose_service not in c.BENTO_SERVICES_DATA:
        err(f"  {compose_service} not in bento_services.json: {list(c.BENTO_SERVICES_DATA.keys())}")
        exit(1)

    # Save state change
    service_state = set_state_services({
        **service_state,
        compose_service: {
            **service_state[compose_service],
            "mode": MODE_PREBUILT,
        },
    })["services"]

    # Clean up existing container
    clean_service(compose_service)

    # Pull new version of production container if needed
    pull_service(compose_service, service_state)

    # Start new production container
    _run_service_in_prebuilt_mode(compose_service)


def mode_service(compose_service: str) -> None:
    # TODO: conn dependency injection for this and other commands

    compose_service = translate_service_aliases(compose_service)
    service_state = get_state()["services"]

    if compose_service == "all":
        for service in service_state:
            mode_service(service)
        return

    if compose_service not in service_state:
        err(f"  {compose_service} not in state[services] dict: {list(service_state.keys())}")
        exit(1)

    mode = service_state[compose_service]["mode"]
    colour = "green" if mode == MODE_PREBUILT else "blue"
    if mode == MODE_PREBUILT and not c.DEV_MODE:
        mode += "\t(prod)"
    else:
        mode += "\t(dev)"

    print(f"{compose_service[:18].rjust(18)} ", end="")
    cprint(mode, colour)


def pull_service(compose_service: str, existing_service_state: Optional[dict] = None) -> None:
    compose_service = translate_service_aliases(compose_service, include_prefixes=False)
    service_state = existing_service_state or get_state()["services"]

    if compose_service == "all":
        # special: run everything
        subprocess.check_call((*_get_compose_with_files(dev=c.DEV_MODE), "pull"))

        # This won't pull local images; loop through those explicitly and pull them
        for s in c.DOCKER_COMPOSE_SERVICES:
            if service_state.get(s, {}).get("mode") == MODE_LOCAL:
                pull_service(s)

        return

    if compose_service in c.MULTI_SERVICE_PREFIXES:
        _handle_multi_service_prefix(compose_service, pull_service)
        return

    check_service_is_compose(compose_service)

    image_t = service_image_vars.get(compose_service)
    if image_t is None:
        err(f"  {compose_service} not in service_image_vars keys: {list(service_image_vars.keys())}")
        exit(1)

    image_var, image_version_var, image_local_version_var = image_t
    service_mode = service_state.get(compose_service, {}).get("mode")

    image_version_var_final: str = image_local_version_var if service_mode == MODE_LOCAL else image_version_var

    # occurs if in dev mode (somehow) but with no dev image
    if image_version_var_final is None:
        # TODO: Fix the state
        err(f"  {compose_service} does not have a dev image")
        exit(1)

    image = os.getenv(image_var)
    image_version = os.getenv(image_version_var_final)

    if image is None:
        err(f"  {image_var} is not set")
        exit(1)
    if image_version is None:
        err(f"  {image_version_var_final} is not set")
        exit(1)

    info(f"Pulling {compose_service} ({image}:{image_version})...")

    # TODO: Pull dev if in dev mode
    # Use subprocess to get nice output
    subprocess.check_call(("docker", "pull", f"{image}:{image_version}"))
    subprocess.check_call((*_get_compose_with_files(dev=service_mode == "dev", local=False), "pull", compose_service))


def _get_shell_user(compose_service: str) -> Tuple[str, ...]:
    if compose_service in BENTO_USER_EXCLUDED_SERVICES:
        return ()

    if compose_service.startswith("cbioportal"):
        return ()

    return "--user", str(c.BENTO_UID)


def enter_shell_for_service(compose_service: str, shell: str) -> None:
    compose_service = translate_service_aliases(compose_service)

    check_service_is_compose(compose_service)

    # TODO: Detect shell
    os.execvp(
        c.COMPOSE[0],
        (*c.COMPOSE, "exec", "-it", *_get_shell_user(compose_service), compose_service, shell))


def run_as_shell_for_service(compose_service: str, shell: str) -> None:
    compose_service = translate_service_aliases(compose_service)

    check_service_is_compose(compose_service)

    # TODO: Detect shell
    os.execvp(
        c.COMPOSE[0],
        (*c.COMPOSE, "run", *_get_profile_cli_args(), *_get_shell_user(compose_service), compose_service, shell))


def logs_service(compose_service: str, follow: bool) -> None:
    compose_service = translate_service_aliases(compose_service)
    profile_args = tuple(_get_profile_cli_args())
    extra_args = ("-f",) if follow else ()

    if compose_service == "all":
        # special: show all logs
        os.execvp(c.COMPOSE[0], (*c.COMPOSE, "logs", *profile_args, *extra_args))
        return

    check_service_is_compose(compose_service)
    os.execvp(c.COMPOSE[0], (*c.COMPOSE, "logs", *profile_args, *extra_args, compose_service))
