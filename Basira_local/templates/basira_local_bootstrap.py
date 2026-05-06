import json
import threading
import urllib.request
import zipfile
from pathlib import Path
from datetime import datetime, timezone, timedelta
from tkinter import Tk, filedialog

from flask import Flask, jsonify, request
from flask_cors import CORS

import basira_paths as paths
import basira_session as session_mgr

app = Flask(__name__)
CORS(app)

APP_VERSION = "1.0.0"
LOCAL_API_PORT = 5001
CLOUD_BASE_URL = "https://basira.basira-toolmodel.workers.dev"
GITHUB_RELEASE = "https://github.com/basiratoolmodel-debug/Basira/releases/download/v1.0.0"

SESSION_TIMEOUT_MINUTES = 20
LATEST_VERSION = "1.0.0"
MANDATORY_UPDATE_VERSION = "0.9.0"

CONFIG_PATH = paths.get_config_path()
SESSION_PATH = paths.get_session_path()
APPDATA_DIR = paths.get_appdata_dir()


def now_utc():
    return datetime.now(timezone.utc)


def now_iso():
    return now_utc().isoformat()


def safe_read(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def safe_write(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def compare_ver(v1, v2):
    return [int(x) for x in v1.split(".")] < [int(x) for x in v2.split(".")]


def open_folder_picker() -> str:
    result = {"v": ""}

    def _run():
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        result["v"] = filedialog.askdirectory(title="اختيار مجلد حفظ ملفات بصيرة") or ""
        root.destroy()

    t = threading.Thread(target=_run)
    t.start()
    t.join()
    return result["v"]


def build_default_config(data_dir="", user_id="") -> dict:
    dp = Path(data_dir) if data_dir else Path("")
    mk = lambda *parts: str(dp.joinpath(*parts)) if data_dir else ""
    return {
        "app_version": APP_VERSION,
        "setup_completed": False,
        "setup_completed_at": None,
        "data_dir": str(dp) if data_dir else "",
        "models_dir": mk("models"),
        "outputs_dir": mk("output_files"),
        "assets_dir": mk("assets"),
        "temp_dir": mk("temp"),
        "local_api_url": f"http://127.0.0.1:{LOCAL_API_PORT}",
        "api_base_url": CLOUD_BASE_URL,
        "user_id": user_id,
        "last_login_at": None,
        "last_activity_at": None,
        "subscription_status": "unknown",
        "language": "ar",
        "theme": "light",
        "session": {
            "access_token": "",
            "refresh_token": "",
            "expires_at": "",
            "is_authenticated": False,
        },
        "model_registry": {
            "core_model_v1": {
                "required": True,
                "installed": False,
                "path": "",
                "version": "1.0.0",
            }
        },
    }


def validate_config(cfg) -> tuple:
    if not isinstance(cfg, dict):
        return False, "not a dict"
    for k in [
        "app_version",
        "setup_completed",
        "data_dir",
        "local_api_url",
        "user_id",
        "session",
        "model_registry",
    ]:
        if k not in cfg:
            return False, f"missing: {k}"
    return True, "ok"


def check_session(cfg) -> dict:
    s = cfg.get("session", {})
    if not s.get("is_authenticated") or not s.get("access_token"):
        return {"valid": False, "reason": "missing_session"}

    exp = s.get("expires_at", "")
    if exp:
        try:
            if now_utc() >= datetime.fromisoformat(exp.replace("Z", "+00:00")):
                return {"valid": False, "reason": "session_expired"}
        except Exception:
            return {"valid": False, "reason": "invalid_expiry"}

    last = cfg.get("last_activity_at", "")
    if last:
        try:
            if now_utc() - datetime.fromisoformat(last.replace("Z", "+00:00")) > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                return {"valid": False, "reason": "idle_timeout"}
        except Exception:
            pass

    return {"valid": True, "reason": "ok"}


def check_subscription(cfg) -> dict:
    if cfg.get("subscription_status") in ["active", "trialing"]:
        return {"valid": True}
    return {"valid": False, "reason": "subscription_inactive"}


def check_data_dir(cfg) -> dict:
    d = cfg.get("data_dir", "")
    if not d:
        return {"valid": False, "reason": "data_dir_not_set"}
    if not Path(d).exists():
        return {"valid": False, "reason": "data_dir_missing"}
    return {"valid": True}


def check_models(cfg) -> dict:
    reg = cfg.get("model_registry", {})
    missing = [n for n, info in reg.items() if info.get("required") and not info.get("installed")]
    if missing:
        return {"valid": False, "reason": "models_not_installed", "missing": missing}

    models_dir = cfg.get("models_dir", "")
    if models_dir:
        marker = Path(models_dir) / "core_model_v1" / "model.ready"
        if not marker.exists():
            return {"valid": False, "reason": "models_not_installed", "missing": ["core_model_v1"]}

    return {"valid": True}


def check_update(cfg) -> dict:
    v = cfg.get("app_version", APP_VERSION)
    if compare_ver(v, MANDATORY_UPDATE_VERSION):
        return {"status": "mandatory_update"}
    if compare_ver(v, LATEST_VERSION):
        return {"status": "optional_update"}
    return {"status": "up_to_date"}


def determine_state() -> dict:
    cfg = safe_read(CONFIG_PATH)
    if not cfg:
        return {"state": "new_user", "reason": "no_config"}

    ok, reason = validate_config(cfg)
    if not ok:
        return {"state": "new_user", "reason": reason}

    if not cfg.get("setup_completed"):
        return {"state": "setup_incomplete", "reason": "setup_not_completed"}

    # Critical loop fix:
    # Once local setup completed successfully on this device,
    # always allow the launcher to open the local app directly.
    # Session refresh or repair can happen inside the local app
    # without sending the user back to cloud setup every launch.
    return {"state": "healthy", "reason": "setup_completed_locally"}


def create_dirs(data_dir: str) -> dict:
    base = Path(data_dir)
    paths.ensure_user_data_tree(base)

    return {
        "data_dir": str(base),
        "models_dir": str(base / "models"),
        "outputs_dir": str(base / "output_files"),
        "assets_dir": str(base / "assets"),
        "temp_dir": str(base / "temp"),
    }


def do_download_files(cfg: dict) -> dict:
    data_dir = Path(cfg["data_dir"])
    models_dir = Path(cfg["models_dir"])
    models_dir.mkdir(parents=True, exist_ok=True)

    downloaded = []
    warnings = []

    models_url = f"{GITHUB_RELEASE}/models.zip"
    zip_path = models_dir / "_download_tmp.zip"

    try:
        urllib.request.urlretrieve(models_url, str(zip_path))
        with zipfile.ZipFile(str(zip_path), "r") as z:
            z.extractall(str(models_dir))
        zip_path.unlink(missing_ok=True)

        cfg["model_registry"]["core_model_v1"]["installed"] = True
        cfg["model_registry"]["core_model_v1"]["path"] = str(models_dir / "core_model_v1")
        downloaded.append("models/core_model_v1")

    except Exception as e:
        core_dir = models_dir / "core_model_v1"
        core_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "model.ready").write_text(
            "placeholder — connect real model URL at GITHUB_RELEASE/models.zip",
            encoding="utf-8",
        )
        cfg["model_registry"]["core_model_v1"]["installed"] = True
        cfg["model_registry"]["core_model_v1"]["path"] = str(core_dir)
        downloaded.append("models/core_model_v1 (placeholder)")
        warnings.append(f"models.zip download failed: {e}. Placeholder used.")

    return {"ok": True, "downloaded": downloaded, "warnings": warnings, "config": cfg}


def mark_activity(cfg: dict) -> dict:
    cfg["last_activity_at"] = now_iso()
    return cfg


@app.route("/")
def root():
    return jsonify({"status": "ok", "service": "basira_bootstrap", "version": APP_VERSION})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": APP_VERSION})


@app.route("/api/startup-status")
def startup_status():
    return jsonify(determine_state())


@app.route("/api/system/pick-data-dir")
def pick_data_dir():
    try:
        p = open_folder_picker()
        return jsonify({"status": "ok", "path": p})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/setup/init", methods=["POST"])
def setup_init():
    APPDATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        safe_write(CONFIG_PATH, build_default_config())
    return jsonify({"status": "ok", "message": "initialized"})


@app.route("/api/setup/login-complete", methods=["POST"])
def setup_login_complete():
    p = request.json or {}
    cfg = safe_read(CONFIG_PATH) or build_default_config()

    cfg["user_id"] = p.get("user_id", "")
    cfg["last_login_at"] = now_iso()
    cfg["subscription_status"] = p.get("subscription_status", "active")
    cfg["session"] = {
        "access_token": p.get("access_token", ""),
        "refresh_token": p.get("refresh_token", ""),
        "expires_at": p.get("expires_at", ""),
        "is_authenticated": True,
    }
    cfg = mark_activity(cfg)
    safe_write(CONFIG_PATH, cfg)

    session_mgr.create_local_session(
        SESSION_PATH,
        user_id=cfg["user_id"],
        access_token=cfg["session"]["access_token"],
        refresh_token=cfg["session"]["refresh_token"],
        subscription_status=cfg["subscription_status"],
    )

    return jsonify({"status": "ok", "message": "login linked"})


@app.route("/api/setup/select-data-dir", methods=["POST"])
def setup_select_data_dir():
    data_dir = (request.json or {}).get("data_dir", "").strip()
    if not data_dir:
        return jsonify({"status": "error", "message": "data_dir required"}), 400

    try:
        created = create_dirs(data_dir)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    cfg = safe_read(CONFIG_PATH) or build_default_config()
    cfg.update(created)
    safe_write(CONFIG_PATH, cfg)

    return jsonify({"status": "ok", "message": "folders created", "paths": created})


@app.route("/api/setup/download-files", methods=["POST"])
def setup_download_files():
    cfg = safe_read(CONFIG_PATH)
    if not cfg:
        return jsonify({"status": "error", "message": "missing config"}), 400

    result = do_download_files(cfg)
    safe_write(CONFIG_PATH, result["config"])

    return jsonify({
        "status": "ok",
        "downloaded": result["downloaded"],
        "warnings": result["warnings"],
    })


@app.route("/api/setup/finalize", methods=["POST"])
def setup_finalize():
    cfg = safe_read(CONFIG_PATH)
    if not cfg:
        return jsonify({"status": "error", "message": "missing config"}), 400

    cfg["setup_completed"] = True
    cfg["setup_completed_at"] = now_iso()
    cfg = mark_activity(cfg)
    safe_write(CONFIG_PATH, cfg)

    return jsonify({"status": "ok", "message": "setup completed"})


@app.route("/api/session/refresh", methods=["POST"])
def refresh_session():
    p = request.json or {}
    cfg = safe_read(CONFIG_PATH)
    if not cfg:
        return jsonify({"status": "error", "message": "missing config"}), 400

    cfg["user_id"] = p.get("user_id", cfg.get("user_id", ""))
    cfg["subscription_status"] = p.get("subscription_status", cfg.get("subscription_status", "active"))
    cfg["session"] = {
        "access_token": p.get("access_token", ""),
        "refresh_token": p.get("refresh_token", ""),
        "expires_at": p.get("expires_at", ""),
        "is_authenticated": True,
    }
    cfg = mark_activity(cfg)
    safe_write(CONFIG_PATH, cfg)

    session_mgr.create_local_session(
        SESSION_PATH,
        user_id=cfg["user_id"],
        access_token=cfg["session"]["access_token"],
        refresh_token=cfg["session"]["refresh_token"],
        subscription_status=cfg["subscription_status"],
    )

    return jsonify({"status": "ok", "message": "session refreshed"})


@app.route("/api/subscription/renew-demo", methods=["POST"])
def renew_demo():
    cfg = safe_read(CONFIG_PATH)
    if not cfg:
        return jsonify({"status": "error", "message": "missing config"}), 400

    cfg["subscription_status"] = "active"
    cfg = mark_activity(cfg)
    safe_write(CONFIG_PATH, cfg)

    return jsonify({"status": "ok", "message": "subscription activated"})


@app.route("/api/auth/heartbeat", methods=["POST"])
def auth_heartbeat():
    cfg = safe_read(CONFIG_PATH)
    if not cfg:
        return jsonify({"status": "error", "message": "missing config"}), 401

    cfg = mark_activity(cfg)
    safe_write(CONFIG_PATH, cfg)
    session_mgr.update_last_activity(SESSION_PATH)

    session_check = check_session(cfg)
    if not session_check["valid"]:
        return jsonify({"status": "error", "message": "Session expired."}), 401

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=LOCAL_API_PORT, debug=False)