from __future__ import annotations

import json
import os
import pathlib
import yaml

from typing import Tuple

__all__ = [
    "DOCKER_COMPOSE_FILE_BASE",
    "DOCKER_COMPOSE_FILE_DEV",
    "DOCKER_COMPOSE_FILE_LOCAL",
    "DOCKER_COMPOSE_FILE_PROD",
    "DOCKER_COMPOSE_BASE_DATA",
    "DOCKER_COMPOSE_SERVICES",
    "DOCKER_COMPOSE_DEV_SERVICES",

    "COMPOSE",
    "USER",

    "MODE",
    "DEV_MODE",

    "BENTO_GIT_CLONE_HTTPS",

    "BENTO_SERVICES_PATH",
    "BENTO_SERVICES_DATA",

    "BENTO_ORCHESTRATION_STATE_DB_FILE",
]

DOCKER_COMPOSE_FILE_BASE = "./docker-compose.yaml"
DOCKER_COMPOSE_FILE_DEV = "./docker-compose.dev.yaml"
DOCKER_COMPOSE_FILE_LOCAL = "./docker-compose.local.yaml"
DOCKER_COMPOSE_FILE_PROD = "./docker-compose.prod.yaml"

USER = os.getenv("USER")

MODE = os.getenv("MODE")
DEV_MODE = MODE == "dev"

BENTO_GIT_CLONE_HTTPS: bool = os.getenv("BENTO_GIT_CLONE_HTTPS", "0").lower().strip() in ("1", "true")

COMPOSE: Tuple[str, ...] = ("docker", "compose")

# Load base docker-compose services list
with open(DOCKER_COMPOSE_FILE_BASE) as dcf:
    DOCKER_COMPOSE_BASE_DATA = yaml.load(dcf, yaml.Loader)

BASE_SERVICES: Tuple[str, ...] = tuple(DOCKER_COMPOSE_BASE_DATA["services"].keys())

# Load dev docker-compose services list if in DEV_MODE
if DEV_MODE:
    with open(DOCKER_COMPOSE_FILE_DEV) as dcf_dev:
        DOCKER_COMPOSE_DEV_BASE_DATA = yaml.load(dcf_dev, yaml.Loader)

    DOCKER_COMPOSE_DEV_SERVICES = tuple(
        service for service in DOCKER_COMPOSE_DEV_BASE_DATA["services"].keys()
        if service not in BASE_SERVICES)

    DOCKER_COMPOSE_SERVICES = BASE_SERVICES + DOCKER_COMPOSE_DEV_SERVICES

else:
    DOCKER_COMPOSE_SERVICES = BASE_SERVICES


BENTO_SERVICES_PATH = os.getenv("BENTO_SERVICES", pathlib.Path(
    __file__).parent.parent / "etc" / "bento_services.json")

with open(BENTO_SERVICES_PATH, "r") as sf:
    BENTO_SERVICES_DATA = json.load(sf)


BENTO_ORCHESTRATION_STATE_DB_FILE = os.getenv("BENTO_ORCHESTRATION_STATE_DB", "./.bentoctl.state.db")
