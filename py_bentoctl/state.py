import json
import sqlite3
import sys

from typing import Any, Dict, Optional

from .config import BENTO_ORCHESTRATION_STATE_DB_FILE, BENTO_SERVICES_DATA

__all__ = [
    "MODE_LOCAL",
    "MODE_PREBUILT",
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


MODE_LOCAL = "local"
MODE_PREBUILT = "prebuilt"


def get_db() -> sqlite3.Connection:
    return sqlite3.connect(BENTO_ORCHESTRATION_STATE_DB_FILE)


def get_state(conn: Optional[sqlite3.Connection] = None):
    db = conn or get_db()

    first_run_services = {
        k: {"mode": MODE_PREBUILT}
        for k in BENTO_SERVICES_DATA.keys()
    }

    try:
        with db:
            db.executescript(STATE_SCHEMA)
            db.execute(
                "INSERT OR IGNORE INTO kvstore (k, v) VALUES ('services', ?)",
                (json.dumps(first_run_services),
                 ))
            db.commit()

            rs = db.execute("SELECT v FROM kvstore WHERE k = 'services'")
            if (services_r := rs.fetchone()) is not None:
                services_state = json.loads(services_r[0])
                did_migration = False
                for k, v in services_state.items():
                    # Migration from alpha build of bentoV2 2.11: port over dev/prod --> local/prebuilt
                    if v["mode"] == "prod":
                        services_state[k]["mode"] = MODE_PREBUILT
                        did_migration = True
                    elif v["mode"] == "dev":
                        services_state[k]["mode"] = MODE_LOCAL
                        did_migration = True

                if did_migration:  # apply migration changes if needed
                    return set_state_services(services_state)

                return {"services": services_state}

            print("Something went wrong while loading service status from state.", file=sys.stderr)
            exit(1)

    finally:
        db.close()


def set_state_services(
        services: Dict[str, Dict[str, Any]], conn: Optional[sqlite3.Connection] = None):
    db = conn or get_db()
    try:
        with db:
            db.execute("INSERT OR REPLACE INTO kvstore (k, v) VALUES ('services', ?)", (json.dumps(services),))
            db.commit()
        return get_state(conn=db)
    finally:
        db.close()
