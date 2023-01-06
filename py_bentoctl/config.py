from __future__ import annotations

import os
import shutil

from typing import Optional

__all__ = [
    "BENTO_DOCKER_SERVICES",
    "COMPOSE",

    "MODE",
    "DEV_MODE",

    "USER",
]

BENTO_DOCKER_SERVICES: list[str] = [
    x.strip() for x in (os.getenv("SERVICES") or "").strip("\"").split(" ") if x.strip()]

COMPOSE: Optional[tuple[str, ...]] = ("docker", "compose")
if shutil.which("docker-compose"):
    COMPOSE = ("docker-compose",)

MODE = os.getenv("MODE")
DEV_MODE = MODE == "dev"

USER = os.getenv("USER")
