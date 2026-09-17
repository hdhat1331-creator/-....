import json
from pathlib import Path

DB_PATH = Path("database.json")

DEFAULT = {
    "replies": {},
    "interval_messages": [],
    "targets": [],
    "seen_groups": [],
}

def load_db():
    if not DB_PATH.exists():
        return {k: (v.copy() if isinstance(v, (dict, list)) else v) for k, v in DEFAULT.items()}
    try:
        data = json.loads(DB_PATH.read_text(encoding="utf-8"))
        for k, v in DEFAULT.items():
            data.setdefault(k, v.copy() if isinstance(v, (dict, list)) else v)
        return data
    except Exception:
        return {k: (v.copy() if isinstance(v, (dict, list)) else v) for k, v in DEFAULT.items()}

def save_db(db):
    DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
