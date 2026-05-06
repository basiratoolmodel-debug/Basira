# import json
# from datetime import datetime, timedelta, timezone
# from pathlib import Path

# SESSION_TIMEOUT_MINUTES = 20
# _UTC = timezone.utc


# def _now():
#     return datetime.now(_UTC)


# def now_iso():
#     return _now().isoformat()


# def _read(path: Path) -> dict:
#     if not path.exists():
#         return {}
#     try:
#         return json.loads(path.read_text(encoding="utf-8"))
#     except Exception:
#         return {}


# def _write(path: Path, data: dict):
#     path.parent.mkdir(parents=True, exist_ok=True)
#     path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# def create_local_session(path: Path, user_id: str, access_token: str, refresh_token: str, subscription_status: str):
#     _write(path, {
#         "user_id": user_id,
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "subscription_status": subscription_status,
#         "created_at": now_iso(),
#         "last_activity_at": now_iso(),
#         "is_authenticated": True,
#     })


# def update_last_activity(path: Path):
#     d = _read(path)
#     if not d:
#         return
#     d["last_activity_at"] = now_iso()
#     _write(path, d)


# def clear_local_session(path: Path):
#     _write(path, {
#         "is_authenticated": False,
#         "logged_out_at": now_iso(),
#     })


# def is_session_expired(path: Path) -> bool:
#     d = _read(path)
#     if not d.get("is_authenticated"):
#         return True

#     last = d.get("last_activity_at")
#     if not last:
#         return True

#     try:
#         return _now() - datetime.fromisoformat(last) > timedelta(minutes=SESSION_TIMEOUT_MINUTES)
#     except Exception:
#         return True


# def get_session(path: Path) -> dict:
#     return _read(path)
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

SESSION_TIMEOUT_MINUTES = 20
_UTC = timezone.utc


def _now():
    return datetime.now(_UTC)


def now_iso():
    return _now().isoformat()


def _read(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def create_local_session(path: Path, user_id: str, access_token: str, refresh_token: str, subscription_status: str):
    _write(path, {
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "subscription_status": subscription_status,
        "created_at": now_iso(),
        "last_activity_at": now_iso(),
        "is_authenticated": True,
    })


def update_last_activity(path: Path):
    d = _read(path)
    if not d:
        return
    d["last_activity_at"] = now_iso()
    _write(path, d)


def clear_local_session(path: Path):
    _write(path, {
        "is_authenticated": False,
        "logged_out_at": now_iso(),
    })


def is_session_expired(path: Path) -> bool:
    d = _read(path)
    if not d.get("is_authenticated"):
        return True

    last = d.get("last_activity_at")
    if not last:
        return True

    try:
        return _now() - datetime.fromisoformat(last) > timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    except Exception:
        return True


def get_session(path: Path) -> dict:
    return _read(path)