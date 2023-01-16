import json
import sqlite3
import sys

__all__ = [
    "get_state",
    "set_state",
]

STATE_FILE = "./bentoctl.state.db"

STATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS kvstore (k TEXT, v TEXT);
INSERT INTO kvstore (k, v) VALUES ('services', '{}') WHERE NOT EXISTS (SELECT 1 FROM kvstore WHERE k = 'services');
"""


def get_state():
    db = sqlite3.connect(STATE_FILE)
    try:
        with db:
            db.executescript(STATE_SCHEMA)
            rs = db.execute("SELECT v FROM kvstore WHERE k = 'services'")
            services_r = rs.fetchone()
            if services_r is None:
                print("Something went wrong while loading service status from state.", file=sys.stderr)
                exit(1)
            services = json.loads(services_r[0])
            return {"services": services}
    finally:
        db.close()


def set_state():
    pass
