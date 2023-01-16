from __future__ import annotations

import json
import os
import pathlib
import shutil

from typing import Optional

__all__ = [
    "BENTO_DOCKER_SERVICES",

    "COMPOSE",
    "USER",

    "MODE",
    "DEV_MODE",


    "BENTO_SERVICES_PATH",
    "BENTO_SERVICES_DATA",

    "BENTO_ORCHESTRATION_STATE_DB_FILE",
]

BENTO_DOCKER_SERVICES: list[str] = [
    x.strip() for x in (os.getenv("SERVICES") or "").strip("\"").split(" ") if x.strip()]

COMPOSE: Optional[tuple[str, ...]] = ("docker", "compose")
if shutil.which("docker-compose"):
    COMPOSE = ("docker-compose",)

USER = os.getenv("USER")

MODE = os.getenv("MODE")
DEV_MODE = MODE == "dev"

BENTO_SERVICES_PATH = os.getenv("BENTO_SERVICES", pathlib.Path(__file__).parent.parent / "etc" / "bento_services.json")
with open(BENTO_SERVICES_PATH, "r") as sf:
    BENTO_SERVICES_DATA = json.load(sf)

BENTO_ORCHESTRATION_STATE_DB_FILE = os.getenv("BENTO_ORCHESTRATION_STATE_DB", "./bentoctl.state.db")
