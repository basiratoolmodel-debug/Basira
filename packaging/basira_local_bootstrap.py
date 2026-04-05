import os
import json
import platform
from pathlib import Path
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

APP_NAME = "Basira"
APP_VERSION = "1.0.0"
LOCAL_API_PORT = 5001
LOCAL_API_URL = f"http://127.0.0.1:{LOCAL_API_PORT}"

CLOUD_API_BASE_URL = "https://basira.basira-toolmodel.workers.dev"
CLOUD_RENEW_URL = "https://basira.basira-toolmodel.workers.dev/renew"

LATEST_VERSION = "1.0.0"
MANDATORY_UPDATE_VERSION = "0.9.0"


# =========================================================
# PATHS
# =========================================================

def get_os_name():
    system = platform.system().lower()
    if "windows" in system:
        return "windows"
    elif "darwin" in system:
        return "mac"
    return "other"


def get_appdata_dir():
    os_name = get_os_name()

    if os_name == "windows":
        base = os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(base) / APP_NAME

    elif os_name == "mac":
        return Path.home() / "Library" / "Application Support" / APP_NAME

    else:
        return Path.home() / f".{APP_NAME.lower()}"


APPDATA_DIR = get_appdata_dir()
LOGS_DIR = APPDATA_DIR / "logs"
CACHE_DIR = APPDATA_DIR / "cache"
SESSION_DIR = APPDATA_DIR / "session"
CONFIG_PATH = APPDATA_DIR / "config.json"
SETUP_STATE_PATH = APPDATA_DIR / "setup_state.json"
VERSION_INFO_PATH = APPDATA_DIR / "version_info.json"


# =========================================================
# HELPERS
# =========================================================

def ensure_base_dirs():
    APPDATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    SESSION_DIR.mkdir(parents=True, exist_ok=True)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def safe_read_json(path: Path):
    try:
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def safe_write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def compare_versions(v1: str, v2: str):
    def parse(v):
        return [int(x) for x in v.split(".")]
    return parse(v1) < parse(v2)


def file_exists(path_str):
    try:
        return Path(path_str).exists()
    except Exception:
        return False


# =========================================================
# CONFIG DESIGN
# =========================================================

def build_default_config(data_dir: str = "", user_id: str = ""):
    data_path = Path(data_dir) if data_dir else Path("")

    return {
        "app_version": APP_VERSION,
        "setup_completed": False,
        "setup_completed_at": None,

        "data_dir": str(data_path) if data_dir else "",
        "models_dir": str(data_path / "models") if data_dir else "",
        "outputs_dir": str(data_path / "outputs") if data_dir else "",
        "assets_dir": str(data_path / "assets") if data_dir else "",
        "temp_dir": str(data_path / "temp") if data_dir else "",

        "local_api_url": LOCAL_API_URL,
        "api_base_url": CLOUD_API_BASE_URL,

        "user_id": user_id,
        "last_login_at": None,
        "last_session_check": None,

        "subscription_status": "unknown",
        "subscription_expires_at": None,

        "last_update_check": None,
        "update_status": "unknown",

        "session": {
            "access_token": "",
            "refresh_token": "",
            "expires_at": ""
        },

        "model_registry": {
            "core_model_v1": {
                "required": True,
                "installed": False,
                "path": "",
                "version": "1.0.0"
            }
        }
    }


# =========================================================
# ENVIRONMENT CHECKS
# =========================================================

def validate_config(config: dict):
    if not isinstance(config, dict):
        return False, "Config is not a valid JSON object"

    required_keys = [
        "app_version",
        "setup_completed",
        "data_dir",
        "models_dir",
        "outputs_dir",
        "assets_dir",
        "local_api_url",
        "api_base_url",
        "user_id",
        "session",
        "model_registry"
    ]

    for key in required_keys:
        if key not in config:
            return False, f"Missing required config key: {key}"

    return True, "Config is valid"


def check_session(config: dict):
    session = config.get("session", {})
    access_token = session.get("access_token", "")
    expires_at = session.get("expires_at", "")

    if not access_token or not expires_at:
        return {
            "valid": False,
            "reason": "missing_session"
        }

    try:
        expires_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        if datetime.now(timezone.utc) >= expires_dt:
            return {
                "valid": False,
                "reason": "session_expired"
            }
    except Exception:
        return {
            "valid": False,
            "reason": "invalid_session_expiry"
        }

    return {
        "valid": True,
        "reason": "session_valid"
    }


def check_subscription(config: dict):
    status = config.get("subscription_status", "unknown")

    if status in ["active", "trialing"]:
        return {
            "valid": True,
            "reason": "subscription_active"
        }

    return {
        "valid": False,
        "reason": "subscription_inactive"
    }


def check_data_directory(config: dict):
    data_dir = config.get("data_dir", "")
    if not data_dir:
        return {
            "valid": False,
            "reason": "missing_data_dir"
        }

    p = Path(data_dir)
    if not p.exists():
        return {
            "valid": False,
            "reason": "data_dir_not_found"
        }

    if not os.access(str(p), os.W_OK):
        return {
            "valid": False,
            "reason": "data_dir_not_writable"
        }

    return {
        "valid": True,
        "reason": "data_dir_ok"
    }


def check_models(config: dict):
    registry = config.get("model_registry", {})
    missing = []

    for model_name, meta in registry.items():
        if meta.get("required", False):
            model_path = meta.get("path", "")
            installed = meta.get("installed", False)

            if not installed or not model_path or not file_exists(model_path):
                missing.append(model_name)

    if missing:
        return {
            "valid": False,
            "reason": "missing_model",
            "missing_models": missing
        }

    return {
        "valid": True,
        "reason": "models_ok",
        "missing_models": []
    }


def check_update_status(config: dict):
    current_version = config.get("app_version", APP_VERSION)

    if compare_versions(current_version, MANDATORY_UPDATE_VERSION):
        return {
            "status": "mandatory_update"
        }

    if compare_versions(current_version, LATEST_VERSION):
        return {
            "status": "optional_update"
        }

    return {
        "status": "up_to_date"
    }


# =========================================================
# USER STATE DECISION
# =========================================================

def determine_user_state():
    ensure_base_dirs()

    if not CONFIG_PATH.exists():
        return {
            "state": "new_user",
            "reason": "no_config"
        }

    config = safe_read_json(CONFIG_PATH)
    if not config:
        return {
            "state": "recovery_required",
            "reason": "config_corrupted"
        }

    valid_config, config_reason = validate_config(config)
    if not valid_config:
        return {
            "state": "recovery_required",
            "reason": "config_invalid",
            "detail": config_reason
        }

    if not config.get("setup_completed", False):
        return {
            "state": "setup_incomplete",
            "reason": "setup_not_completed"
        }

    data_check = check_data_directory(config)
    if not data_check["valid"]:
        return {
            "state": "recovery_required",
            "reason": data_check["reason"]
        }

    model_check = check_models(config)
    if not model_check["valid"]:
        return {
            "state": "recovery_required",
            "reason": model_check["reason"],
            "missing_models": model_check.get("missing_models", [])
        }

    session_check = check_session(config)
    if not session_check["valid"]:
        return {
            "state": "login_required",
            "reason": session_check["reason"]
        }

    update_check = check_update_status(config)
    if update_check["status"] == "mandatory_update":
        return {
            "state": "update_required",
            "reason": "mandatory_update"
        }

    if update_check["status"] == "optional_update":
        return {
            "state": "healthy_with_optional_update",
            "reason": "optional_update"
        }

    return {
        "state": "healthy",
        "reason": "app_healthy"
    }


# =========================================================
# SETUP FLOW
# =========================================================

def create_data_structure(data_dir: str):
    base = Path(data_dir)
    models_dir = base / "models"
    outputs_dir = base / "outputs"
    assets_dir = base / "assets"
    temp_dir = base / "temp"

    for p in [base, models_dir, outputs_dir, assets_dir, temp_dir]:
        p.mkdir(parents=True, exist_ok=True)

    return {
        "data_dir": str(base),
        "models_dir": str(models_dir),
        "outputs_dir": str(outputs_dir),
        "assets_dir": str(assets_dir),
        "temp_dir": str(temp_dir)
    }


def install_demo_models(config: dict):
    models_dir = Path(config["models_dir"])
    core_model_dir = models_dir / "core_model_v1"
    core_model_dir.mkdir(parents=True, exist_ok=True)

    demo_file = core_model_dir / "model.ready"
    demo_file.write_text("Basira local model installed", encoding="utf-8")

    config["model_registry"]["core_model_v1"]["installed"] = True
    config["model_registry"]["core_model_v1"]["path"] = str(demo_file)

    return config


def environment_self_check(config: dict):
    results = {
        "config_valid": validate_config(config)[0],
        "data_dir": check_data_directory(config),
        "models": check_models(config),
        "session": check_session(config),
        "update": check_update_status(config)
    }

    all_good = (
        results["config_valid"]
        and results["data_dir"]["valid"]
        and results["models"]["valid"]
    )

    return {
        "ok": all_good,
        "results": results
    }


# =========================================================
# API ROUTES
# =========================================================

@app.route("/")
def root():
    return send_from_directory(".", "local-setup.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION
    })


@app.route("/api/startup-status", methods=["GET"])
def startup_status():
    state = determine_user_state()
    return jsonify(state)


@app.route("/api/setup/init", methods=["POST"])
def setup_init():
    ensure_base_dirs()

    if not CONFIG_PATH.exists():
        config = build_default_config()
        safe_write_json(CONFIG_PATH, config)

    return jsonify({
        "status": "ok",
        "message": "Setup initialized"
    })


@app.route("/api/setup/login-complete", methods=["POST"])
def setup_login_complete():
    payload = request.json or {}

    user_id = payload.get("user_id", "")
    access_token = payload.get("access_token", "")
    refresh_token = payload.get("refresh_token", "")
    expires_at = payload.get("expires_at", "")
    subscription_status = payload.get("subscription_status", "active")

    config = safe_read_json(CONFIG_PATH) or build_default_config()

    config["user_id"] = user_id
    config["last_login_at"] = now_iso()
    config["last_session_check"] = now_iso()
    config["subscription_status"] = subscription_status

    config["session"] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at
    }

    safe_write_json(CONFIG_PATH, config)

    return jsonify({
        "status": "ok",
        "message": "Login linked to local app"
    })


@app.route("/api/setup/select-data-dir", methods=["POST"])
def setup_select_data_dir():
    payload = request.json or {}
    data_dir = payload.get("data_dir", "").strip()

    if not data_dir:
        return jsonify({
            "status": "error",
            "message": "Data directory is required"
        }), 400

    try:
        created = create_data_structure(data_dir)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Could not create data directory: {str(e)}"
        }), 400

    config = safe_read_json(CONFIG_PATH) or build_default_config()

    config["data_dir"] = created["data_dir"]
    config["models_dir"] = created["models_dir"]
    config["outputs_dir"] = created["outputs_dir"]
    config["assets_dir"] = created["assets_dir"]
    config["temp_dir"] = created["temp_dir"]

    safe_write_json(CONFIG_PATH, config)

    return jsonify({
        "status": "ok",
        "message": "Data directory configured",
        "paths": created
    })


@app.route("/api/setup/install-models", methods=["POST"])
def setup_install_models():
    config = safe_read_json(CONFIG_PATH)
    if not config:
        return jsonify({
            "status": "error",
            "message": "Missing config"
        }), 400

    config = install_demo_models(config)
    safe_write_json(CONFIG_PATH, config)

    return jsonify({
        "status": "ok",
        "message": "Models installed"
    })


@app.route("/api/setup/verify", methods=["GET"])
def setup_verify():
    config = safe_read_json(CONFIG_PATH)
    if not config:
        return jsonify({
            "status": "error",
            "message": "Config not found"
        }), 400

    result = environment_self_check(config)

    return jsonify({
        "status": "ok" if result["ok"] else "error",
        "verification": result
    })


@app.route("/api/setup/finalize", methods=["POST"])
def setup_finalize():
    config = safe_read_json(CONFIG_PATH)
    if not config:
        return jsonify({
            "status": "error",
            "message": "Config not found"
        }), 400

    config["setup_completed"] = True
    config["setup_completed_at"] = now_iso()

    safe_write_json(CONFIG_PATH, config)

    return jsonify({
        "status": "ok",
        "message": "Setup completed"
    })


@app.route("/api/config", methods=["GET"])
def get_config():
    config = safe_read_json(CONFIG_PATH)
    if not config:
        return jsonify({
            "status": "error",
            "message": "Config not found"
        }), 404

    return jsonify(config)


@app.route("/api/recovery/repair-models", methods=["POST"])
def repair_models():
    config = safe_read_json(CONFIG_PATH)
    if not config:
        return jsonify({
            "status": "error",
            "message": "Config not found"
        }), 404

    config = install_demo_models(config)
    safe_write_json(CONFIG_PATH, config)

    return jsonify({
        "status": "ok",
        "message": "Models repaired"
    })


@app.route("/api/recovery/reselect-data-dir", methods=["POST"])
def recovery_reselect_data_dir():
    payload = request.json or {}
    data_dir = payload.get("data_dir", "").strip()

    if not data_dir:
        return jsonify({
            "status": "error",
            "message": "Data directory is required"
        }), 400

    try:
        created = create_data_structure(data_dir)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Could not reconfigure data directory: {str(e)}"
        }), 400

    config = safe_read_json(CONFIG_PATH)
    if not config:
        config = build_default_config()

    config["data_dir"] = created["data_dir"]
    config["models_dir"] = created["models_dir"]
    config["outputs_dir"] = created["outputs_dir"]
    config["assets_dir"] = created["assets_dir"]
    config["temp_dir"] = created["temp_dir"]

    safe_write_json(CONFIG_PATH, config)

    return jsonify({
        "status": "ok",
        "message": "Data directory updated",
        "paths": created
    })


@app.route("/api/session/refresh", methods=["POST"])
def session_refresh():
    payload = request.json or {}

    access_token = payload.get("access_token", "")
    refresh_token = payload.get("refresh_token", "")
    expires_at = payload.get("expires_at", "")
    subscription_status = payload.get("subscription_status", "active")

    config = safe_read_json(CONFIG_PATH)
    if not config:
        return jsonify({
            "status": "error",
            "message": "Config not found"
        }), 404

    config["session"]["access_token"] = access_token
    config["session"]["refresh_token"] = refresh_token
    config["session"]["expires_at"] = expires_at
    config["subscription_status"] = subscription_status
    config["last_login_at"] = now_iso()
    config["last_session_check"] = now_iso()

    safe_write_json(CONFIG_PATH, config)

    return jsonify({
        "status": "ok",
        "message": "Session refreshed"
    })


@app.route("/api/subscription/renew-demo", methods=["POST"])
def renew_demo():
    config = safe_read_json(CONFIG_PATH)
    if not config:
        return jsonify({
            "status": "error",
            "message": "Config not found"
        }), 404

    config["subscription_status"] = "active"
    safe_write_json(CONFIG_PATH, config)

    return jsonify({
        "status": "ok",
        "message": "Subscription renewed (demo)"
    })


if __name__ == "__main__":
    ensure_base_dirs()
    app.run(host="127.0.0.1", port=LOCAL_API_PORT, debug=True)