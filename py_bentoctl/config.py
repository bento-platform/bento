from __future__ import annotations

import json
import os
import pathlib
import yaml

from typing import Iterable, Tuple

__all__ = [
    "DOCKER_COMPOSE_FILE_BASE",
    "DOCKER_COMPOSE_FILE_DEV",
    "DOCKER_COMPOSE_FILE_LOCAL",
    "DOCKER_COMPOSE_FILE_PROD",
    "DOCKER_COMPOSE_BASE_DATA",

    "DOCKER_COMPOSE_SERVICES",
    "DOCKER_COMPOSE_DEV_SERVICES",
    "DOCKER_COMPOSE_CBIOPORTAL_SERVICES",

    "COMPOSE",
    "USER",

    "MODE",
    "DEV_MODE",

    "BENTOV2_USE_EXTERNAL_IDP",
    "BENTOV2_USE_BENTO_PUBLIC",
    "BENTO_CBIOPORTAL_ENABLED",

    "BENTO_GIT_CLONE_HTTPS",

    "BENTO_SERVICES_PATH",
    "BENTO_SERVICES_DATA",

    "BENTO_ORCHESTRATION_STATE_DB_FILE",
]

DOCKER_COMPOSE_FILE_BASE = "./docker-compose.yaml"
DOCKER_COMPOSE_FILE_DEV = "./docker-compose.dev.yaml"
DOCKER_COMPOSE_FILE_LOCAL = "./docker-compose.local.yaml"
DOCKER_COMPOSE_FILE_PROD = "./docker-compose.prod.yaml"
DOCKER_COMPOSE_FILE_FEATURE_CBIOPORTAL = "./lib/cbioportal/docker-compose.cbioportal.yaml"

USER = os.getenv("USER")

MODE = os.getenv("MODE")
DEV_MODE = MODE == "dev"


def _env_get_bool(var: str, default: bool = False) -> bool:
    return os.getenv(var, str(default).lower()).lower().strip() in ("1", "true")


BENTOV2_USE_EXTERNAL_IDP: bool = _env_get_bool("BENTOV2_USE_EXTERNAL_IDP", default=False)
BENTOV2_USE_BENTO_PUBLIC: bool = _env_get_bool("BENTOV2_USE_BENTO_PUBLIC", default=True)
BENTO_CBIOPORTAL_ENABLED: bool = _env_get_bool("BENTO_CBIOPORTAL_ENABLED", default=False)

if not DEV_MODE and BENTO_CBIOPORTAL_ENABLED:
    import sys
    print("cBioPortal for production deployments is not finished.", file=sys.stderr)
    exit(1)

BENTO_GIT_CLONE_HTTPS: bool = os.getenv("BENTO_GIT_CLONE_HTTPS", "0").lower().strip() in ("1", "true")

COMPOSE: Tuple[str, ...] = ("docker", "compose")

# Load base docker-compose services list
with open(DOCKER_COMPOSE_FILE_BASE) as dcf:
    DOCKER_COMPOSE_BASE_DATA = yaml.load(dcf, yaml.Loader)

BASE_SERVICES: Tuple[str, ...] = tuple(DOCKER_COMPOSE_BASE_DATA["services"].keys())


def _filter_base_services(services: Iterable[str]) -> Tuple[str, ...]:
    return tuple(service for service in services if service not in BASE_SERVICES)


# Load dev docker-compose services list if in DEV_MODE
DOCKER_COMPOSE_DEV_SERVICES: Tuple[str, ...] = ()
if DEV_MODE:
    with open(DOCKER_COMPOSE_FILE_DEV) as dcf_dev:
        DOCKER_COMPOSE_DEV_BASE_DATA = yaml.load(dcf_dev, yaml.Loader)
    DOCKER_COMPOSE_DEV_SERVICES = _filter_base_services(DOCKER_COMPOSE_DEV_BASE_DATA["services"].keys())

DOCKER_COMPOSE_CBIOPORTAL_SERVICES: Tuple[str, ...] = ()
if BENTO_CBIOPORTAL_ENABLED:
    with open(DOCKER_COMPOSE_FILE_FEATURE_CBIOPORTAL) as dcf_cbp:
        DOCKER_COMPOSE_CBIOPORTAL_BASE_DATA = yaml.load(dcf_cbp, yaml.Loader)
    DOCKER_COMPOSE_CBIOPORTAL_SERVICES = _filter_base_services(DOCKER_COMPOSE_CBIOPORTAL_BASE_DATA["services"].keys())

# Final amalgamation of services for Bento taking into account dev/prod mode and feature flags
DOCKER_COMPOSE_SERVICES: Tuple[str, ...] = (
    BASE_SERVICES +
    DOCKER_COMPOSE_DEV_SERVICES +
    DOCKER_COMPOSE_CBIOPORTAL_SERVICES
)


BENTO_SERVICES_PATH = os.getenv("BENTO_SERVICES", pathlib.Path(
    __file__).parent.parent / "etc" / "bento_services.json")

with open(BENTO_SERVICES_PATH, "r") as sf:
    BENTO_SERVICES_DATA = json.load(sf)


BENTO_ORCHESTRATION_STATE_DB_FILE = os.getenv("BENTO_ORCHESTRATION_STATE_DB", "./.bentoctl.state.db")
