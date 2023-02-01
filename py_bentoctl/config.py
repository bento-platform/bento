from __future__ import annotations

import json
import os
import pathlib
import shutil
import yaml

__all__ = [
    "DOCKER_COMPOSE_FILE_BASE",
    "DOCKER_COMPOSE_FILE_DEV",
    "DOCKER_COMPOSE_FILE_PROD",
    "DOCKER_COMPOSE_BASE_DATA",
    "DOCKER_COMPOSE_SERVICES",
    "DOCKER_COMPOSE_DEV_SERVICES",

    "COMPOSE",
    "USER",

    "MODE",
    "DEV_MODE",

    "BENTO_SERVICES_PATH",
    "BENTO_SERVICES_DATA",

    "BENTO_ORCHESTRATION_STATE_DB_FILE",
]

DOCKER_COMPOSE_FILE_BASE = "./docker-compose.yaml"
DOCKER_COMPOSE_FILE_DEV = "./docker-compose.dev.yaml"
DOCKER_COMPOSE_FILE_PROD = "./docker-compose.prod.yaml"

USER = os.getenv("USER")

MODE = os.getenv("MODE")
DEV_MODE = MODE == "dev"

COMPOSE: tuple[str, ...] = ("docker", "compose")
if shutil.which("docker-compose"):
    COMPOSE = ("docker-compose",)

# Load base docker-compose services list
with open(DOCKER_COMPOSE_FILE_BASE) as dcf:
    DOCKER_COMPOSE_BASE_DATA = yaml.load(dcf, yaml.Loader)
    base_services = list(DOCKER_COMPOSE_BASE_DATA["services"].keys())

# Load dev docker-compose services list if in DEV_MODE
if DEV_MODE:
    with open(DOCKER_COMPOSE_FILE_DEV) as dcf_dev:
        DOCKER_COMPOSE_DEV_BASE_DATA = yaml.load(dcf_dev, yaml.Loader)
    dev_services = list(DOCKER_COMPOSE_DEV_BASE_DATA["services"].keys())
    dev_services = [service for service in dev_services if service not in base_services]
    combined_services = base_services + dev_services
    DOCKER_COMPOSE_DEV_SERVICES = tuple(dev_services)

DOCKER_COMPOSE_SERVICES = tuple(combined_services)

BENTO_SERVICES_PATH = os.getenv("BENTO_SERVICES", pathlib.Path(
    __file__).parent.parent / "etc" / "bento_services.json")
with open(BENTO_SERVICES_PATH, "r") as sf:
    BENTO_SERVICES_DATA = json.load(sf)

BENTO_ORCHESTRATION_STATE_DB_FILE = os.getenv(
    "BENTO_ORCHESTRATION_STATE_DB", "./.bentoctl.state.db")
