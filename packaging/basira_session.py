# packaging/basira_session.py
import json
from datetime import datetime, timedelta, UTC
from pathlib import Path

SESSION_TIMEOUT_MINUTES = 20


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def read_json_file(path: Path, default=None):
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json_file(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def create_local_session(path: Path, user_id: str, access_token: str, refresh_token: str, subscription_status: str):
    payload = {
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "subscription_status": subscription_status,
        "created_at": now_iso(),
        "last_activity_at": now_iso(),
        "is_authenticated": True,
    }
    write_json_file(path, payload)


def update_last_activity(path: Path):
    session = read_json_file(path, {})
    if not session:
        return
    session["last_activity_at"] = now_iso()
    write_json_file(path, session)


def clear_local_session(path: Path):
    payload = {
        "is_authenticated": False,
        "logged_out_at": now_iso()
    }
    write_json_file(path, payload)


def is_session_expired(path: Path) -> bool:
    session = read_json_file(path, {})
    if not session.get("is_authenticated"):
        return True

    last_activity = session.get("last_activity_at")
    if not last_activity:
        return True

    try:
        last_dt = datetime.fromisoformat(last_activity)
    except Exception:
        return True

    if datetime.now(UTC) - last_dt > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        return True

    return False