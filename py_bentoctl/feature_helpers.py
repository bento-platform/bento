import os
import pathlib
import subprocess

from . import config as c
from .utils import info, err


__all__ = [
    "init_cbioportal",
]


CBIOPORTAL_VERSION = os.getenv("BENTO_CBIOPORTAL_IMAGE_VERSION")
CBIOPORTAL_SCHEMA_SQL_URL = (
    f"https://raw.githubusercontent.com/cBioPortal/cbioportal/v{CBIOPORTAL_VERSION}"
    f"/db-scripts/src/main/resources/cgds.sql"
)
CBIOPORTAL_SEED_DB_HG19_URL = (
    "https://github.com/cBioPortal/datahub/raw/ef7e21214a84f31393e3dd197ca6b78a1fc42698/seedDB/seedDB_hg19_archive/"
    "seed-cbioportal_hg19_v2.12.14.sql.gz")
CBIOPORTAL_SEED_DB_HG38_URL = (
    "https://github.com/cBioPortal/datahub/raw/ef7e21214a84f31393e3dd197ca6b78a1fc42698/seedDB/"
    "seed-cbioportal_hg19_hg38_v2.13.1.sql.gz")

CBIOPORTAL_SEED_DATA_PATH = pathlib.Path(__file__).parent.parent / "lib" / "cbioportal" / "seed_data"
CBIOPORTAL_SCHEMA_PATH = CBIOPORTAL_SEED_DATA_PATH / "cgds.sql"
CBIOPORTAL_SEED_DB_HG19_PATH = CBIOPORTAL_SEED_DATA_PATH / "seed-hg19.sql.gz"
CBIOPORTAL_SEED_DB_HG38_PATH = CBIOPORTAL_SEED_DATA_PATH / "seed-hg38.sql.gz"


def init_cbioportal():
    if not c.BENTO_FEATURE_CBIOPORTAL.enabled:
        err("cBioPortal must be enabled in local.env before initialization")
        exit(1)

    if not CBIOPORTAL_SCHEMA_PATH.exists():
        info("cBioPortal schema does not exist; downloading now...")
        subprocess.check_call(("curl", "-L", CBIOPORTAL_SCHEMA_SQL_URL, "-o", str(CBIOPORTAL_SCHEMA_PATH)))
    if not CBIOPORTAL_SEED_DB_HG19_PATH.exists():
        info("cBioPortal seed data (hg19) does not exist; downloading now")
        subprocess.check_call(("curl", "-L", CBIOPORTAL_SEED_DB_HG19_URL, "-o", str(CBIOPORTAL_SEED_DB_HG19_PATH)))
    if not CBIOPORTAL_SEED_DB_HG38_PATH.exists():
        info("cBioPortal seed data (hg38) does not exist; downloading now")
        subprocess.check_call(("curl", "-L", CBIOPORTAL_SEED_DB_HG38_URL, "-o", str(CBIOPORTAL_SEED_DB_HG38_PATH)))
