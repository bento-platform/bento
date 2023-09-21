from __future__ import annotations

import itertools
import json
import os
import pathlib
import pwd
import yaml

from typing import Dict, Generator, List, Optional, Tuple

__all__ = [
    "DOCKER_COMPOSE_FILE_BASE",
    "DOCKER_COMPOSE_FILE_DEV",
    "DOCKER_COMPOSE_FILE_LOCAL",
    "DOCKER_COMPOSE_FILE_PROD",

    "DOCKER_COMPOSE_FILE_AUTH",
    "DOCKER_COMPOSE_FILE_BEACON",
    "DOCKER_COMPOSE_FILE_CBIOPORTAL",
    "DOCKER_COMPOSE_FILE_GOHAN",
    "DOCKER_COMPOSE_FILE_PUBLIC",

    "DOCKER_COMPOSE_SERVICES",
    "DOCKER_COMPOSE_DEV_SERVICES",

    "COMPOSE",
    "USER",

    "BENTO_UID",
    "BENTO_USERNAME",

    "MODE",
    "DEV_MODE",

    "BENTO_OPTIONAL_FEATURES",
    "BENTO_OPTIONAL_FEATURES_BY_PROFILE",
    "get_enabled_feature_profiles",
    "BentoOptionalFeature",

    "BENTOV2_USE_EXTERNAL_IDP",
    "BENTOV2_USE_BENTO_PUBLIC",

    "BENTO_FEATURE_AUTH",
    "BENTO_FEATURE_BEACON",
    "BENTO_FEATURE_CBIOPORTAL",
    "BENTO_FEATURE_GOHAN",
    "BENTO_FEATURE_PUBLIC",

    "BENTO_GIT_CLONE_HTTPS",

    "BENTO_SERVICES_PATH",
    "BENTO_SERVICES_DATA",

    "BENTO_ORCHESTRATION_STATE_DB_FILE",
]

DOCKER_COMPOSE_FILE_BASE = "./docker-compose.yaml"
DOCKER_COMPOSE_FILE_DEV = "./docker-compose.dev.yaml"
DOCKER_COMPOSE_FILE_LOCAL = "./docker-compose.local.yaml"
DOCKER_COMPOSE_FILE_PROD = "./docker-compose.prod.yaml"

DOCKER_COMPOSE_FILE_AUTH = "./lib/auth/docker-compose.auth.yaml"
DOCKER_COMPOSE_FILE_BEACON = "./lib/beacon/docker-compose.beacon.yaml"
DOCKER_COMPOSE_FILE_CBIOPORTAL = "./lib/cbioportal/docker-compose.cbioportal.yaml"
DOCKER_COMPOSE_FILE_GOHAN = "./lib/gohan/docker-compose.gohan.yaml"
DOCKER_COMPOSE_FILE_PUBLIC = "./lib/public/docker-compose.public.yaml"

USER = os.getenv("USER")

BENTO_UID: int = int(os.getenv("BENTO_UID", str(os.getuid())))
BENTO_USERNAME: str = pwd.getpwuid(BENTO_UID).pw_name

MODE = os.getenv("MODE")
DEV_MODE = MODE == "dev"


def _env_get_bool(var: str, default: bool = False) -> bool:
    return os.getenv(var, str(default).lower()).lower().strip() in ("1", "true")


BENTO_OPTIONAL_FEATURES: List["BentoOptionalFeature"] = []
BENTO_OPTIONAL_FEATURES_BY_PROFILE: Dict[str, "BentoOptionalFeature"] = {}


def get_enabled_feature_profiles() -> Generator[str, None, None]:
    for f in BENTO_OPTIONAL_FEATURES:
        if f.enabled:
            yield f.profile


class BentoOptionalFeature:
    def __init__(self, enabled: bool, profile: str):
        self.enabled: bool = enabled
        self.profile: str = profile  # Single-feature profile

        # Register self into various records of optional features
        BENTO_OPTIONAL_FEATURES.append(self)
        BENTO_OPTIONAL_FEATURES_BY_PROFILE[profile] = self


BENTOV2_USE_EXTERNAL_IDP: bool = _env_get_bool("BENTOV2_USE_EXTERNAL_IDP", default=False)
BENTOV2_USE_BENTO_PUBLIC: bool = _env_get_bool("BENTOV2_USE_BENTO_PUBLIC", default=True)

BENTO_FEATURE_AUTH = BentoOptionalFeature(enabled=not BENTOV2_USE_EXTERNAL_IDP, profile="auth")
BENTO_FEATURE_BEACON = BentoOptionalFeature(
    enabled=_env_get_bool("BENTO_BEACON_ENABLED", default=False), profile="beacon")
BENTO_FEATURE_CBIOPORTAL = BentoOptionalFeature(
    enabled=_env_get_bool("BENTO_CBIOPORTAL_ENABLED", default=False), profile="cbioportal")
BENTO_FEATURE_GOHAN = BentoOptionalFeature(
    enabled=_env_get_bool("BENTO_GOHAN_ENABLED", default=False), profile="gohan")
BENTO_FEATURE_PUBLIC = BentoOptionalFeature(enabled=BENTOV2_USE_BENTO_PUBLIC, profile="public")

if not DEV_MODE and BENTO_FEATURE_CBIOPORTAL.enabled:
    import sys
    print("cBioPortal for production deployments is not finished.", file=sys.stderr)
    exit(1)


BENTO_GIT_CLONE_HTTPS: bool = os.getenv("BENTO_GIT_CLONE_HTTPS", "0").lower().strip() in ("1", "true")

COMPOSE: Tuple[str, ...] = ("docker", "compose")


def _get_enabled_services(compose_file: str, filter_out: Tuple[str, ...] = ()) -> Generator[str, None, None]:
    # Loop through compose file and find enabled services - either no profiles specified,
    # or the profile of an enabled feature.

    # Load base docker-compose services list
    with open(compose_file) as dcf:
        compose_data = yaml.load(dcf, yaml.Loader)

    for k, v in compose_data["services"].items():
        if k in filter_out:
            continue

        profiles: Optional[List[str]] = v.get("profiles")
        if profiles is None:
            # If no profiles, always enabled
            yield k
            continue
        for p in profiles:
            if (f := BENTO_OPTIONAL_FEATURES_BY_PROFILE.get(p)) is not None and f.enabled:
                yield k
                break


BASE_SERVICES: Tuple[str, ...] = tuple(itertools.chain.from_iterable(_get_enabled_services(cf, ()) for cf in (
    DOCKER_COMPOSE_FILE_BASE,
    DOCKER_COMPOSE_FILE_AUTH,
    DOCKER_COMPOSE_FILE_BEACON,
    DOCKER_COMPOSE_FILE_CBIOPORTAL,
    DOCKER_COMPOSE_FILE_GOHAN,
    DOCKER_COMPOSE_FILE_PUBLIC,
)))

# Load dev docker-compose services list if in DEV_MODE
DOCKER_COMPOSE_DEV_SERVICES: Tuple[str, ...] = tuple(
    _get_enabled_services(DOCKER_COMPOSE_FILE_DEV, BASE_SERVICES)) if DEV_MODE else ()

# Final amalgamation of services for Bento taking into account dev/prod mode + profiles
DOCKER_COMPOSE_SERVICES: Tuple[str, ...] = BASE_SERVICES + DOCKER_COMPOSE_DEV_SERVICES


BENTO_SERVICES_PATH = os.getenv("BENTO_SERVICES", pathlib.Path(__file__).parent.parent / "etc" / "bento_services.json")

with open(BENTO_SERVICES_PATH, "r") as sf:
    BENTO_SERVICES_DATA = json.load(sf)


BENTO_ORCHESTRATION_STATE_DB_FILE = os.getenv("BENTO_ORCHESTRATION_STATE_DB", "./.bentoctl.state.db")

MULTI_SERVICE_PREFIXES = ("gohan",)

PHENOTOOL_PATH = os.getenv("PHENOTOOL_JAR_PATH", "")
