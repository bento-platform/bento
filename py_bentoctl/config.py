from __future__ import annotations

import itertools
import json
import os
import pathlib
import pwd
import subprocess
import yaml

from typing import Dict, Generator, List, Optional, Tuple

from .utils import err

__all__ = [
    "DOCKER_COMPOSE_FILE_BASE",
    "DOCKER_COMPOSE_FILE_DEV",
    "DOCKER_COMPOSE_FILE_LOCAL",
    "DOCKER_COMPOSE_FILE_PROD",

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
    "BENTO_GATEWAY_USE_TLS",

    "BENTO_FEATURE_AUTH",
    "BENTO_FEATURE_BEACON",
    "BENTO_FEATURE_CBIOPORTAL",
    "BENTO_FEATURE_GOHAN",
    "BENTO_FEATURE_PUBLIC",

    "BENTO_GIT_CLONE_HTTPS",

    "BENTO_SERVICES_PATH",
    "BENTO_SERVICES_DATA",

    "BENTO_ORCHESTRATION_STATE_DB_FILE",

    "MULTI_SERVICE_PREFIXES",

    "PHENOTOOL_PATH",

    "DATA_DIR_ENV_VARS",
]

DOCKER_COMPOSE_FILE_BASE = "./docker-compose.yaml"
DOCKER_COMPOSE_FILE_DEV = "./docker-compose.dev.yaml"
DOCKER_COMPOSE_FILE_LOCAL = "./docker-compose.local.yaml"
DOCKER_COMPOSE_FILE_PROD = "./docker-compose.prod.yaml"

USER = os.getenv("USER")

BENTO_UID: int = int(os.getenv("BENTO_UID", str(os.getuid())))
BENTO_USERNAME: str = pwd.getpwuid(BENTO_UID).pw_name

MODE = os.getenv("MODE")
DEV_MODE = MODE == "dev"

SERVICE_LITERAL_ALL: str = "all"


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
BENTO_GATEWAY_USE_TLS: bool = _env_get_bool("BENTO_GATEWAY_USE_TLS", default=True)
BENTO_DOMAIN_REDIRECT: str = os.getenv("BENTO_DOMAIN_REDIRECT", default=None)

BENTO_FEATURE_AUTH = BentoOptionalFeature(enabled=not BENTOV2_USE_EXTERNAL_IDP, profile="auth")
BENTO_FEATURE_BEACON = BentoOptionalFeature(
    enabled=_env_get_bool("BENTO_BEACON_ENABLED", default=False), profile="beacon")
BENTO_FEATURE_CBIOPORTAL = BentoOptionalFeature(
    enabled=_env_get_bool("BENTO_CBIOPORTAL_ENABLED", default=False), profile="cbioportal")
BENTO_FEATURE_GOHAN = BentoOptionalFeature(
    enabled=_env_get_bool("BENTO_GOHAN_ENABLED", default=False), profile="gohan")
BENTO_FEATURE_GARAGE = BentoOptionalFeature(
    enabled=_env_get_bool("BENTO_GARAGE_ENABLED", default=False), profile="garage")
BENTO_FEATURE_MONITORING = BentoOptionalFeature(
    enabled=_env_get_bool("BENTO_MONITORING_ENABLED", default=False), profile="monitoring")

BENTO_FEATURE_PUBLIC = BentoOptionalFeature(enabled=BENTOV2_USE_BENTO_PUBLIC, profile="public")
BENTO_FEATURE_REDIRECT = BentoOptionalFeature(enabled=bool(BENTO_DOMAIN_REDIRECT), profile="redirect")

BENTO_GIT_CLONE_HTTPS: bool = os.getenv("BENTO_GIT_CLONE_HTTPS", "0").lower().strip() in ("1", "true")

COMPOSE: Tuple[str, ...] = ("docker", "compose")


def _get_enabled_services(
    compose_files: Tuple[str, ...],
    filter_out: Tuple[str, ...] = (),
) -> Generator[str, None, None]:
    # Loop through compose file and find enabled services - either no profiles specified,
    # or the profile of an enabled feature.

    enabled_profiles = tuple(get_enabled_feature_profiles())

    # Generate merged Docker Compose YAML using docker compose config command
    r = subprocess.run(
        (
            *COMPOSE,
            *itertools.chain.from_iterable(("-f", cf) for cf in compose_files),
            *itertools.chain.from_iterable(("--profile", p) for p in enabled_profiles),
            "config"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    if r.returncode != 0:
        err(f"Parsing compose file(s) {compose_files} failed with error:\n\t{r.stderr.decode('utf-8').strip()}")
        exit(1)

    # Load the compose data
    compose_data = yaml.load(r.stdout, yaml.Loader)

    for k, v in compose_data["services"].items():
        if k in filter_out:
            continue

        profiles: Optional[List[str]] = v.get("profiles")
        if profiles is None:
            # If no profiles, always enabled
            yield k
            continue
        for p in profiles:
            if p in enabled_profiles:
                yield k
                break  # escape profile loop, we found one which enables this service


BASE_SERVICES: Tuple[str, ...] = tuple(_get_enabled_services((DOCKER_COMPOSE_FILE_BASE,), ()))

# Load dev docker-compose services list if in DEV_MODE
DOCKER_COMPOSE_DEV_SERVICES: Tuple[str, ...] = tuple(
    _get_enabled_services((DOCKER_COMPOSE_FILE_BASE, DOCKER_COMPOSE_FILE_DEV), BASE_SERVICES)) if DEV_MODE else ()

# Final amalgamation of services for Bento taking into account dev/prod mode + profiles
DOCKER_COMPOSE_SERVICES: Tuple[str, ...] = BASE_SERVICES + DOCKER_COMPOSE_DEV_SERVICES
# For use by CLI service arguments: adds in an `all` option, meaning all services:
DOCKER_COMPOSE_SERVICES_PLUS_ALL: Tuple[str, ...] = (*DOCKER_COMPOSE_SERVICES, SERVICE_LITERAL_ALL)


BENTO_SERVICES_PATH = os.getenv("BENTO_SERVICES", pathlib.Path(__file__).parent.parent / "etc" / "bento_services.json")

with open(BENTO_SERVICES_PATH, "r") as sf:
    BENTO_SERVICES_DATA = json.load(sf)


BENTO_SERVICES_COMPOSE_IDS: Tuple[str, ...] = tuple(BENTO_SERVICES_DATA.keys())
# For use by CLI service arguments: adds in an `all` option, meaning all services:
BENTO_SERVICES_COMPOSE_IDS_PLUS_ALL: Tuple[str, ...] = (*BENTO_SERVICES_COMPOSE_IDS, SERVICE_LITERAL_ALL)


BENTO_ORCHESTRATION_STATE_DB_FILE = os.getenv("BENTO_ORCHESTRATION_STATE_DB", "./.bentoctl.state.db")

MULTI_SERVICE_PREFIXES = ("gohan",)

PHENOTOOL_PATH = os.getenv("PHENOTOOL_JAR_PATH", "")

# Look up table
#   from: a well-known arbitrary key representing a particular service volume
#   to:   the name of an environment variable containing the path to the corresponding data volume on disk
DATA_DIR_ENV_VARS = {
    "root_fast": "BENTO_FAST_DATA_DIR",
    "root_slow": "BENTO_SLOW_DATA_DIR",
    "authz-db": "BENTO_AUTHZ_DB_VOL_DIR",
    "drs-data": "BENTO_DRS_DATA_VOL_DIR",
    "drs-tmp": "BENTO_DRS_TMP_VOL_DIR",
    "drop-box": "BENTOV2_DROP_BOX_VOL_DIR",
    "gohan": "BENTOV2_GOHAN_DATA_ROOT",
    "gohan-elasticsearch": "BENTOV2_GOHAN_ES_DATA_DIR",
    "gohan-vcfs": "BENTOV2_GOHAN_API_VCF_PATH",
    "gohan-gtfs": "BENTOV2_GOHAN_API_GTF_PATH",
    "katsu-db": "BENTOV2_KATSU_DB_DEV_VOL_DIR" if DEV_MODE else "BENTOV2_KATSU_DB_PROD_VOL_DIR",
    "notification": "BENTOV2_NOTIFICATION_VOL_DIR",
    "redis": "BENTOV2_REDIS_VOL_DIR",
    "reference": "BENTO_REFERENCE_TMP_VOL_DIR",
    "reference-db": "BENTO_REFERENCE_DB_VOL_DIR",
    "wes": "BENTOV2_WES_VOL_DIR",
    "wes-tmp": "BENTOV2_WES_VOL_TMP_DIR",

    # Feature-specific volume dirs - only if the relevant feature is enabled.
    #  - internal IdP
    **({"auth": "BENTOV2_AUTH_VOL_DIR"} if not BENTOV2_USE_EXTERNAL_IDP else {}),
    #  - cBioPortal
    **({"cbioportal": "BENTO_CBIOPORTAL_STUDY_DIR"} if BENTO_FEATURE_CBIOPORTAL.enabled else {}),
    #  - Garage
    **({"garage-meta": "BENTO_GARAGE_META_DIR",
        "garage-data": "BENTO_GARAGE_DATA_DIR"} if BENTO_FEATURE_GARAGE.enabled else {}),
    #  - Monitoring: Grafana/Loki
    **({"grafana": "BENTO_GRAFANA_LIB_DIR"} if BENTO_FEATURE_MONITORING else {}),
    **({"loki": "BENTO_LOKI_TEMP_DIR"} if BENTO_FEATURE_MONITORING else {}),
}
