import json
import sqlite3
import sys

from typing import Any, Dict, Optional

from .config import BENTO_ORCHESTRATION_STATE_DB_FILE, BENTO_SERVICES_DATA

__all__ = [
    "MODE_DEV",
    "MODE_PROD",
    "get_db",
    "get_state",
    "set_state_services",
]

STATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS kvstore (
    k TEXT PRIMARY KEY, 
    v TEXT
);
"""


MODE_DEV = "dev"
MODE_PROD = "prod"


def get_db() -> sqlite3.Connection:
    return sqlite3.connect(BENTO_ORCHESTRATION_STATE_DB_FILE)


def get_state(conn: Optional[sqlite3.Connection] = None):
    db = conn or get_db()

    first_run_services = {
        k: {"mode": "prod"}
        for k in BENTO_SERVICES_DATA.keys()
    }

    try:
        with db:
            db.executescript(STATE_SCHEMA)
            db.execute("INSERT OR IGNORE INTO kvstore (k, v) VALUES ('services', ?)",
                       (json.dumps(first_run_services),))
            db.commit()

            rs = db.execute("SELECT v FROM kvstore WHERE k = 'services'")
            if (services_r := rs.fetchone()) is not None:
                return {"services": json.loads(services_r[0])}

            print(
                "Something went wrong while loading service status from state.", file=sys.stderr)
            exit(1)

    finally:
        db.close()


def set_state_services(services: Dict[str, Dict[str, Any]], conn: Optional[sqlite3.Connection] = None):
    db = conn or get_db()
    try:
        with db:
            db.execute(
                "INSERT OR REPLACE INTO kvstore (k, v) VALUES ('services', ?)", (json.dumps(services),))
            db.commit()
        return get_state(conn=db)
    finally:
        db.close()
