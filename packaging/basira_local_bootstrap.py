# # # # # import os
# # # # # import json
# # # # # import platform
# # # # # from pathlib import Path
# # # # # from datetime import datetime, timezone

# # # # # from flask import Flask, jsonify, request, send_from_directory
# # # # # from flask_cors import CORS

# # # # # app = Flask(__name__, static_folder=".", static_url_path="")
# # # # # CORS(app)

# # # # # APP_NAME = "Basira"
# # # # # APP_VERSION = "1.0.0"
# # # # # LOCAL_API_PORT = 5001
# # # # # LOCAL_API_URL = f"http://127.0.0.1:{LOCAL_API_PORT}"

# # # # # CLOUD_API_BASE_URL = "https://basira.basira-toolmodel.workers.dev"
# # # # # CLOUD_RENEW_URL = "https://basira.basira-toolmodel.workers.dev/renew"

# # # # # LATEST_VERSION = "1.0.0"
# # # # # MANDATORY_UPDATE_VERSION = "0.9.0"


# # # # # # =========================================================
# # # # # # PATHS
# # # # # # =========================================================

# # # # # def get_os_name():
# # # # #     system = platform.system().lower()
# # # # #     if "windows" in system:
# # # # #         return "windows"
# # # # #     elif "darwin" in system:
# # # # #         return "mac"
# # # # #     return "other"


# # # # # def get_appdata_dir():
# # # # #     os_name = get_os_name()

# # # # #     if os_name == "windows":
# # # # #         base = os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming"))
# # # # #         return Path(base) / APP_NAME

# # # # #     elif os_name == "mac":
# # # # #         return Path.home() / "Library" / "Application Support" / APP_NAME

# # # # #     else:
# # # # #         return Path.home() / f".{APP_NAME.lower()}"


# # # # # APPDATA_DIR = get_appdata_dir()
# # # # # LOGS_DIR = APPDATA_DIR / "logs"
# # # # # CACHE_DIR = APPDATA_DIR / "cache"
# # # # # SESSION_DIR = APPDATA_DIR / "session"
# # # # # CONFIG_PATH = APPDATA_DIR / "config.json"
# # # # # SETUP_STATE_PATH = APPDATA_DIR / "setup_state.json"
# # # # # VERSION_INFO_PATH = APPDATA_DIR / "version_info.json"


# # # # # # =========================================================
# # # # # # HELPERS
# # # # # # =========================================================

# # # # # def ensure_base_dirs():
# # # # #     APPDATA_DIR.mkdir(parents=True, exist_ok=True)
# # # # #     LOGS_DIR.mkdir(parents=True, exist_ok=True)
# # # # #     CACHE_DIR.mkdir(parents=True, exist_ok=True)
# # # # #     SESSION_DIR.mkdir(parents=True, exist_ok=True)


# # # # # def now_iso():
# # # # #     return datetime.now(timezone.utc).isoformat()


# # # # # def safe_read_json(path: Path):
# # # # #     try:
# # # # #         if not path.exists():
# # # # #             return None
# # # # #         with open(path, "r", encoding="utf-8") as f:
# # # # #             return json.load(f)
# # # # #     except Exception:
# # # # #         return None


# # # # # def safe_write_json(path: Path, data: dict):
# # # # #     path.parent.mkdir(parents=True, exist_ok=True)
# # # # #     with open(path, "w", encoding="utf-8") as f:
# # # # #         json.dump(data, f, indent=2, ensure_ascii=False)


# # # # # def compare_versions(v1: str, v2: str):
# # # # #     def parse(v):
# # # # #         return [int(x) for x in v.split(".")]
# # # # #     return parse(v1) < parse(v2)


# # # # # def file_exists(path_str):
# # # # #     try:
# # # # #         return Path(path_str).exists()
# # # # #     except Exception:
# # # # #         return False


# # # # # # =========================================================
# # # # # # CONFIG DESIGN
# # # # # # =========================================================

# # # # # def build_default_config(data_dir: str = "", user_id: str = ""):
# # # # #     data_path = Path(data_dir) if data_dir else Path("")

# # # # #     return {
# # # # #         "app_version": APP_VERSION,
# # # # #         "setup_completed": False,
# # # # #         "setup_completed_at": None,

# # # # #         "data_dir": str(data_path) if data_dir else "",
# # # # #         "models_dir": str(data_path / "models") if data_dir else "",
# # # # #         "outputs_dir": str(data_path / "outputs") if data_dir else "",
# # # # #         "assets_dir": str(data_path / "assets") if data_dir else "",
# # # # #         "temp_dir": str(data_path / "temp") if data_dir else "",

# # # # #         "local_api_url": LOCAL_API_URL,
# # # # #         "api_base_url": CLOUD_API_BASE_URL,

# # # # #         "user_id": user_id,
# # # # #         "last_login_at": None,
# # # # #         "last_session_check": None,

# # # # #         "subscription_status": "unknown",
# # # # #         "subscription_expires_at": None,

# # # # #         "last_update_check": None,
# # # # #         "update_status": "unknown",

# # # # #         "session": {
# # # # #             "access_token": "",
# # # # #             "refresh_token": "",
# # # # #             "expires_at": ""
# # # # #         },

# # # # #         "model_registry": {
# # # # #             "core_model_v1": {
# # # # #                 "required": True,
# # # # #                 "installed": False,
# # # # #                 "path": "",
# # # # #                 "version": "1.0.0"
# # # # #             }
# # # # #         }
# # # # #     }


# # # # # # =========================================================
# # # # # # ENVIRONMENT CHECKS
# # # # # # =========================================================

# # # # # def validate_config(config: dict):
# # # # #     if not isinstance(config, dict):
# # # # #         return False, "Config is not a valid JSON object"

# # # # #     required_keys = [
# # # # #         "app_version",
# # # # #         "setup_completed",
# # # # #         "data_dir",
# # # # #         "models_dir",
# # # # #         "outputs_dir",
# # # # #         "assets_dir",
# # # # #         "local_api_url",
# # # # #         "api_base_url",
# # # # #         "user_id",
# # # # #         "session",
# # # # #         "model_registry"
# # # # #     ]

# # # # #     for key in required_keys:
# # # # #         if key not in config:
# # # # #             return False, f"Missing required config key: {key}"

# # # # #     return True, "Config is valid"


# # # # # def check_session(config: dict):
# # # # #     session = config.get("session", {})
# # # # #     access_token = session.get("access_token", "")
# # # # #     expires_at = session.get("expires_at", "")

# # # # #     if not access_token or not expires_at:
# # # # #         return {
# # # # #             "valid": False,
# # # # #             "reason": "missing_session"
# # # # #         }

# # # # #     try:
# # # # #         expires_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
# # # # #         if datetime.now(timezone.utc) >= expires_dt:
# # # # #             return {
# # # # #                 "valid": False,
# # # # #                 "reason": "session_expired"
# # # # #             }
# # # # #     except Exception:
# # # # #         return {
# # # # #             "valid": False,
# # # # #             "reason": "invalid_session_expiry"
# # # # #         }

# # # # #     return {
# # # # #         "valid": True,
# # # # #         "reason": "session_valid"
# # # # #     }


# # # # # def check_subscription(config: dict):
# # # # #     status = config.get("subscription_status", "unknown")

# # # # #     if status in ["active", "trialing"]:
# # # # #         return {
# # # # #             "valid": True,
# # # # #             "reason": "subscription_active"
# # # # #         }

# # # # #     return {
# # # # #         "valid": False,
# # # # #         "reason": "subscription_inactive"
# # # # #     }


# # # # # def check_data_directory(config: dict):
# # # # #     data_dir = config.get("data_dir", "")
# # # # #     if not data_dir:
# # # # #         return {
# # # # #             "valid": False,
# # # # #             "reason": "missing_data_dir"
# # # # #         }

# # # # #     p = Path(data_dir)
# # # # #     if not p.exists():
# # # # #         return {
# # # # #             "valid": False,
# # # # #             "reason": "data_dir_not_found"
# # # # #         }

# # # # #     if not os.access(str(p), os.W_OK):
# # # # #         return {
# # # # #             "valid": False,
# # # # #             "reason": "data_dir_not_writable"
# # # # #         }

# # # # #     return {
# # # # #         "valid": True,
# # # # #         "reason": "data_dir_ok"
# # # # #     }


# # # # # def check_models(config: dict):
# # # # #     registry = config.get("model_registry", {})
# # # # #     missing = []

# # # # #     for model_name, meta in registry.items():
# # # # #         if meta.get("required", False):
# # # # #             model_path = meta.get("path", "")
# # # # #             installed = meta.get("installed", False)

# # # # #             if not installed or not model_path or not file_exists(model_path):
# # # # #                 missing.append(model_name)

# # # # #     if missing:
# # # # #         return {
# # # # #             "valid": False,
# # # # #             "reason": "missing_model",
# # # # #             "missing_models": missing
# # # # #         }

# # # # #     return {
# # # # #         "valid": True,
# # # # #         "reason": "models_ok",
# # # # #         "missing_models": []
# # # # #     }


# # # # # def check_update_status(config: dict):
# # # # #     current_version = config.get("app_version", APP_VERSION)

# # # # #     if compare_versions(current_version, MANDATORY_UPDATE_VERSION):
# # # # #         return {
# # # # #             "status": "mandatory_update"
# # # # #         }

# # # # #     if compare_versions(current_version, LATEST_VERSION):
# # # # #         return {
# # # # #             "status": "optional_update"
# # # # #         }

# # # # #     return {
# # # # #         "status": "up_to_date"
# # # # #     }


# # # # # # =========================================================
# # # # # # USER STATE DECISION
# # # # # # =========================================================

# # # # # def determine_user_state():
# # # # #     ensure_base_dirs()

# # # # #     if not CONFIG_PATH.exists():
# # # # #         return {
# # # # #             "state": "new_user",
# # # # #             "reason": "no_config"
# # # # #         }

# # # # #     config = safe_read_json(CONFIG_PATH)
# # # # #     if not config:
# # # # #         return {
# # # # #             "state": "recovery_required",
# # # # #             "reason": "config_corrupted"
# # # # #         }

# # # # #     valid_config, config_reason = validate_config(config)
# # # # #     if not valid_config:
# # # # #         return {
# # # # #             "state": "recovery_required",
# # # # #             "reason": "config_invalid",
# # # # #             "detail": config_reason
# # # # #         }

# # # # #     if not config.get("setup_completed", False):
# # # # #         return {
# # # # #             "state": "setup_incomplete",
# # # # #             "reason": "setup_not_completed"
# # # # #         }

# # # # #     data_check = check_data_directory(config)
# # # # #     if not data_check["valid"]:
# # # # #         return {
# # # # #             "state": "recovery_required",
# # # # #             "reason": data_check["reason"]
# # # # #         }

# # # # #     model_check = check_models(config)
# # # # #     if not model_check["valid"]:
# # # # #         return {
# # # # #             "state": "recovery_required",
# # # # #             "reason": model_check["reason"],
# # # # #             "missing_models": model_check.get("missing_models", [])
# # # # #         }

# # # # #     session_check = check_session(config)
# # # # #     if not session_check["valid"]:
# # # # #         return {
# # # # #             "state": "login_required",
# # # # #             "reason": session_check["reason"]
# # # # #         }

# # # # #     update_check = check_update_status(config)
# # # # #     if update_check["status"] == "mandatory_update":
# # # # #         return {
# # # # #             "state": "update_required",
# # # # #             "reason": "mandatory_update"
# # # # #         }

# # # # #     if update_check["status"] == "optional_update":
# # # # #         return {
# # # # #             "state": "healthy_with_optional_update",
# # # # #             "reason": "optional_update"
# # # # #         }

# # # # #     return {
# # # # #         "state": "healthy",
# # # # #         "reason": "app_healthy"
# # # # #     }


# # # # # # =========================================================
# # # # # # SETUP FLOW
# # # # # # =========================================================

# # # # # def create_data_structure(data_dir: str):
# # # # #     base = Path(data_dir)
# # # # #     models_dir = base / "models"
# # # # #     outputs_dir = base / "outputs"
# # # # #     assets_dir = base / "assets"
# # # # #     temp_dir = base / "temp"

# # # # #     for p in [base, models_dir, outputs_dir, assets_dir, temp_dir]:
# # # # #         p.mkdir(parents=True, exist_ok=True)

# # # # #     return {
# # # # #         "data_dir": str(base),
# # # # #         "models_dir": str(models_dir),
# # # # #         "outputs_dir": str(outputs_dir),
# # # # #         "assets_dir": str(assets_dir),
# # # # #         "temp_dir": str(temp_dir)
# # # # #     }


# # # # # def install_demo_models(config: dict):
# # # # #     models_dir = Path(config["models_dir"])
# # # # #     core_model_dir = models_dir / "core_model_v1"
# # # # #     core_model_dir.mkdir(parents=True, exist_ok=True)

# # # # #     demo_file = core_model_dir / "model.ready"
# # # # #     demo_file.write_text("Basira local model installed", encoding="utf-8")

# # # # #     config["model_registry"]["core_model_v1"]["installed"] = True
# # # # #     config["model_registry"]["core_model_v1"]["path"] = str(demo_file)

# # # # #     return config


# # # # # def environment_self_check(config: dict):
# # # # #     results = {
# # # # #         "config_valid": validate_config(config)[0],
# # # # #         "data_dir": check_data_directory(config),
# # # # #         "models": check_models(config),
# # # # #         "session": check_session(config),
# # # # #         "update": check_update_status(config)
# # # # #     }

# # # # #     all_good = (
# # # # #         results["config_valid"]
# # # # #         and results["data_dir"]["valid"]
# # # # #         and results["models"]["valid"]
# # # # #     )

# # # # #     return {
# # # # #         "ok": all_good,
# # # # #         "results": results
# # # # #     }


# # # # # # =========================================================
# # # # # # API ROUTES
# # # # # # =========================================================

# # # # # @app.route("/")
# # # # # def root():
# # # # #     return send_from_directory(".", "local-setup.html")


# # # # # @app.route("/health")
# # # # # def health():
# # # # #     return jsonify({
# # # # #         "status": "ok",
# # # # #         "app": APP_NAME,
# # # # #         "version": APP_VERSION
# # # # #     })


# # # # # @app.route("/api/startup-status", methods=["GET"])
# # # # # def startup_status():
# # # # #     state = determine_user_state()
# # # # #     return jsonify(state)


# # # # # @app.route("/api/setup/init", methods=["POST"])
# # # # # def setup_init():
# # # # #     ensure_base_dirs()

# # # # #     if not CONFIG_PATH.exists():
# # # # #         config = build_default_config()
# # # # #         safe_write_json(CONFIG_PATH, config)

# # # # #     return jsonify({
# # # # #         "status": "ok",
# # # # #         "message": "Setup initialized"
# # # # #     })


# # # # # @app.route("/api/setup/login-complete", methods=["POST"])
# # # # # def setup_login_complete():
# # # # #     payload = request.json or {}

# # # # #     user_id = payload.get("user_id", "")
# # # # #     access_token = payload.get("access_token", "")
# # # # #     refresh_token = payload.get("refresh_token", "")
# # # # #     expires_at = payload.get("expires_at", "")
# # # # #     subscription_status = payload.get("subscription_status", "active")

# # # # #     config = safe_read_json(CONFIG_PATH) or build_default_config()

# # # # #     config["user_id"] = user_id
# # # # #     config["last_login_at"] = now_iso()
# # # # #     config["last_session_check"] = now_iso()
# # # # #     config["subscription_status"] = subscription_status

# # # # #     config["session"] = {
# # # # #         "access_token": access_token,
# # # # #         "refresh_token": refresh_token,
# # # # #         "expires_at": expires_at
# # # # #     }

# # # # #     safe_write_json(CONFIG_PATH, config)

# # # # #     return jsonify({
# # # # #         "status": "ok",
# # # # #         "message": "Login linked to local app"
# # # # #     })


# # # # # @app.route("/api/setup/select-data-dir", methods=["POST"])
# # # # # def setup_select_data_dir():
# # # # #     payload = request.json or {}
# # # # #     data_dir = payload.get("data_dir", "").strip()

# # # # #     if not data_dir:
# # # # #         return jsonify({
# # # # #             "status": "error",
# # # # #             "message": "Data directory is required"
# # # # #         }), 400

# # # # #     try:
# # # # #         created = create_data_structure(data_dir)
# # # # #     except Exception as e:
# # # # #         return jsonify({
# # # # #             "status": "error",
# # # # #             "message": f"Could not create data directory: {str(e)}"
# # # # #         }), 400

# # # # #     config = safe_read_json(CONFIG_PATH) or build_default_config()

# # # # #     config["data_dir"] = created["data_dir"]
# # # # #     config["models_dir"] = created["models_dir"]
# # # # #     config["outputs_dir"] = created["outputs_dir"]
# # # # #     config["assets_dir"] = created["assets_dir"]
# # # # #     config["temp_dir"] = created["temp_dir"]

# # # # #     safe_write_json(CONFIG_PATH, config)

# # # # #     return jsonify({
# # # # #         "status": "ok",
# # # # #         "message": "Data directory configured",
# # # # #         "paths": created
# # # # #     })


# # # # # @app.route("/api/setup/install-models", methods=["POST"])
# # # # # def setup_install_models():
# # # # #     config = safe_read_json(CONFIG_PATH)
# # # # #     if not config:
# # # # #         return jsonify({
# # # # #             "status": "error",
# # # # #             "message": "Missing config"
# # # # #         }), 400

# # # # #     config = install_demo_models(config)
# # # # #     safe_write_json(CONFIG_PATH, config)

# # # # #     return jsonify({
# # # # #         "status": "ok",
# # # # #         "message": "Models installed"
# # # # #     })


# # # # # @app.route("/api/setup/verify", methods=["GET"])
# # # # # def setup_verify():
# # # # #     config = safe_read_json(CONFIG_PATH)
# # # # #     if not config:
# # # # #         return jsonify({
# # # # #             "status": "error",
# # # # #             "message": "Config not found"
# # # # #         }), 400

# # # # #     result = environment_self_check(config)

# # # # #     return jsonify({
# # # # #         "status": "ok" if result["ok"] else "error",
# # # # #         "verification": result
# # # # #     })


# # # # # @app.route("/api/setup/finalize", methods=["POST"])
# # # # # def setup_finalize():
# # # # #     config = safe_read_json(CONFIG_PATH)
# # # # #     if not config:
# # # # #         return jsonify({
# # # # #             "status": "error",
# # # # #             "message": "Config not found"
# # # # #         }), 400

# # # # #     config["setup_completed"] = True
# # # # #     config["setup_completed_at"] = now_iso()

# # # # #     safe_write_json(CONFIG_PATH, config)

# # # # #     return jsonify({
# # # # #         "status": "ok",
# # # # #         "message": "Setup completed"
# # # # #     })


# # # # # @app.route("/api/config", methods=["GET"])
# # # # # def get_config():
# # # # #     config = safe_read_json(CONFIG_PATH)
# # # # #     if not config:
# # # # #         return jsonify({
# # # # #             "status": "error",
# # # # #             "message": "Config not found"
# # # # #         }), 404

# # # # #     return jsonify(config)


# # # # # @app.route("/api/recovery/repair-models", methods=["POST"])
# # # # # def repair_models():
# # # # #     config = safe_read_json(CONFIG_PATH)
# # # # #     if not config:
# # # # #         return jsonify({
# # # # #             "status": "error",
# # # # #             "message": "Config not found"
# # # # #         }), 404

# # # # #     config = install_demo_models(config)
# # # # #     safe_write_json(CONFIG_PATH, config)

# # # # #     return jsonify({
# # # # #         "status": "ok",
# # # # #         "message": "Models repaired"
# # # # #     })


# # # # # @app.route("/api/recovery/reselect-data-dir", methods=["POST"])
# # # # # def recovery_reselect_data_dir():
# # # # #     payload = request.json or {}
# # # # #     data_dir = payload.get("data_dir", "").strip()

# # # # #     if not data_dir:
# # # # #         return jsonify({
# # # # #             "status": "error",
# # # # #             "message": "Data directory is required"
# # # # #         }), 400

# # # # #     try:
# # # # #         created = create_data_structure(data_dir)
# # # # #     except Exception as e:
# # # # #         return jsonify({
# # # # #             "status": "error",
# # # # #             "message": f"Could not reconfigure data directory: {str(e)}"
# # # # #         }), 400

# # # # #     config = safe_read_json(CONFIG_PATH)
# # # # #     if not config:
# # # # #         config = build_default_config()

# # # # #     config["data_dir"] = created["data_dir"]
# # # # #     config["models_dir"] = created["models_dir"]
# # # # #     config["outputs_dir"] = created["outputs_dir"]
# # # # #     config["assets_dir"] = created["assets_dir"]
# # # # #     config["temp_dir"] = created["temp_dir"]

# # # # #     safe_write_json(CONFIG_PATH, config)

# # # # #     return jsonify({
# # # # #         "status": "ok",
# # # # #         "message": "Data directory updated",
# # # # #         "paths": created
# # # # #     })


# # # # # @app.route("/api/session/refresh", methods=["POST"])
# # # # # def session_refresh():
# # # # #     payload = request.json or {}

# # # # #     access_token = payload.get("access_token", "")
# # # # #     refresh_token = payload.get("refresh_token", "")
# # # # #     expires_at = payload.get("expires_at", "")
# # # # #     subscription_status = payload.get("subscription_status", "active")

# # # # #     config = safe_read_json(CONFIG_PATH)
# # # # #     if not config:
# # # # #         return jsonify({
# # # # #             "status": "error",
# # # # #             "message": "Config not found"
# # # # #         }), 404

# # # # #     config["session"]["access_token"] = access_token
# # # # #     config["session"]["refresh_token"] = refresh_token
# # # # #     config["session"]["expires_at"] = expires_at
# # # # #     config["subscription_status"] = subscription_status
# # # # #     config["last_login_at"] = now_iso()
# # # # #     config["last_session_check"] = now_iso()

# # # # #     safe_write_json(CONFIG_PATH, config)

# # # # #     return jsonify({
# # # # #         "status": "ok",
# # # # #         "message": "Session refreshed"
# # # # #     })


# # # # # @app.route("/api/subscription/renew-demo", methods=["POST"])
# # # # # def renew_demo():
# # # # #     config = safe_read_json(CONFIG_PATH)
# # # # #     if not config:
# # # # #         return jsonify({
# # # # #             "status": "error",
# # # # #             "message": "Config not found"
# # # # #         }), 404

# # # # #     config["subscription_status"] = "active"
# # # # #     safe_write_json(CONFIG_PATH, config)

# # # # #     return jsonify({
# # # # #         "status": "ok",
# # # # #         "message": "Subscription renewed (demo)"
# # # # #     })


# # # # # if __name__ == "__main__":
# # # # #     ensure_base_dirs()
# # # # #     app.run(host="127.0.0.1", port=LOCAL_API_PORT, debug=True)

# # # # import os
# # # # import json
# # # # import platform
# # # # from pathlib import Path
# # # # from datetime import datetime, timezone, timedelta

# # # # from flask import Flask, jsonify, request
# # # # from flask_cors import CORS

# # # # app = Flask(__name__)
# # # # CORS(app)

# # # # APP_NAME = "Basira"
# # # # APP_VERSION = "1.0.0"
# # # # LOCAL_API_PORT = 5001
# # # # LOCAL_API_URL = f"http://127.0.0.1:{LOCAL_API_PORT}"

# # # # CLOUD_API_BASE_URL = "https://basira.basira-toolmodel.workers.dev"
# # # # CLOUD_RENEW_URL = "https://basira.basira-toolmodel.workers.dev/renew"

# # # # LATEST_VERSION = "1.0.0"
# # # # MANDATORY_UPDATE_VERSION = "0.9.0"
# # # # SESSION_TIMEOUT_MINUTES = 20


# # # # # =========================================================
# # # # # PATHS
# # # # # =========================================================

# # # # def get_os_name():
# # # #     system = platform.system().lower()
# # # #     if "windows" in system:
# # # #         return "windows"
# # # #     elif "darwin" in system:
# # # #         return "mac"
# # # #     return "other"


# # # # def get_appdata_dir():
# # # #     os_name = get_os_name()

# # # #     if os_name == "windows":
# # # #         base = os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming"))
# # # #         return Path(base) / APP_NAME
# # # #     elif os_name == "mac":
# # # #         return Path.home() / "Library" / "Application Support" / APP_NAME
# # # #     else:
# # # #         return Path.home() / f".{APP_NAME.lower()}"


# # # # APPDATA_DIR = get_appdata_dir()
# # # # LOGS_DIR = APPDATA_DIR / "logs"
# # # # CACHE_DIR = APPDATA_DIR / "cache"
# # # # SESSION_DIR = APPDATA_DIR / "session"
# # # # CONFIG_PATH = APPDATA_DIR / "config.json"
# # # # SETUP_STATE_PATH = APPDATA_DIR / "setup_state.json"
# # # # VERSION_INFO_PATH = APPDATA_DIR / "version_info.json"


# # # # # =========================================================
# # # # # HELPERS
# # # # # =========================================================

# # # # def ensure_base_dirs():
# # # #     APPDATA_DIR.mkdir(parents=True, exist_ok=True)
# # # #     LOGS_DIR.mkdir(parents=True, exist_ok=True)
# # # #     CACHE_DIR.mkdir(parents=True, exist_ok=True)
# # # #     SESSION_DIR.mkdir(parents=True, exist_ok=True)


# # # # def now_utc():
# # # #     return datetime.now(timezone.utc)


# # # # def now_iso():
# # # #     return now_utc().isoformat()


# # # # def safe_read_json(path: Path):
# # # #     try:
# # # #         if not path.exists():
# # # #             return None
# # # #         with open(path, "r", encoding="utf-8") as f:
# # # #             return json.load(f)
# # # #     except Exception:
# # # #         return None


# # # # def safe_write_json(path: Path, data: dict):
# # # #     path.parent.mkdir(parents=True, exist_ok=True)
# # # #     with open(path, "w", encoding="utf-8") as f:
# # # #         json.dump(data, f, indent=2, ensure_ascii=False)


# # # # def compare_versions(v1: str, v2: str):
# # # #     def parse(v):
# # # #         return [int(x) for x in v.split(".")]
# # # #     return parse(v1) < parse(v2)


# # # # def file_exists(path_str):
# # # #     try:
# # # #         return Path(path_str).exists()
# # # #     except Exception:
# # # #         return False


# # # # def default_data_dir():
# # # #     return Path.home() / "Documents" / "BasiraData"


# # # # # =========================================================
# # # # # CONFIG DESIGN
# # # # # =========================================================

# # # # def build_default_config(data_dir: str = "", user_id: str = ""):
# # # #     data_path = Path(data_dir) if data_dir else default_data_dir()

# # # #     return {
# # # #         "app_version": APP_VERSION,
# # # #         "setup_completed": False,
# # # #         "setup_completed_at": None,

# # # #         "data_dir": str(data_path),
# # # #         "models_dir": str(data_path / "models"),
# # # #         "outputs_dir": str(data_path / "outputs"),
# # # #         "assets_dir": str(data_path / "assets"),
# # # #         "temp_dir": str(data_path / "temp"),

# # # #         "local_api_url": LOCAL_API_URL,
# # # #         "api_base_url": CLOUD_API_BASE_URL,

# # # #         "user_id": user_id,
# # # #         "last_login_at": None,
# # # #         "last_session_check": None,
# # # #         "last_activity_at": None,

# # # #         "subscription_status": "unknown",
# # # #         "subscription_expires_at": None,

# # # #         "last_update_check": None,
# # # #         "update_status": "unknown",

# # # #         "session_timeout_minutes": SESSION_TIMEOUT_MINUTES,

# # # #         "session": {
# # # #             "access_token": "",
# # # #             "refresh_token": "",
# # # #             "expires_at": "",
# # # #             "is_authenticated": False
# # # #         },

# # # #         "model_registry": {
# # # #             "core_model_v1": {
# # # #                 "required": True,
# # # #                 "installed": False,
# # # #                 "path": "",
# # # #                 "version": "1.0.0"
# # # #             }
# # # #         }
# # # #     }


# # # # # =========================================================
# # # # # ENVIRONMENT CHECKS
# # # # # =========================================================

# # # # def validate_config(config: dict):
# # # #     if not isinstance(config, dict):
# # # #         return False, "Config is not a valid JSON object"

# # # #     required_keys = [
# # # #         "app_version",
# # # #         "setup_completed",
# # # #         "data_dir",
# # # #         "models_dir",
# # # #         "outputs_dir",
# # # #         "assets_dir",
# # # #         "local_api_url",
# # # #         "api_base_url",
# # # #         "user_id",
# # # #         "session",
# # # #         "model_registry"
# # # #     ]

# # # #     for key in required_keys:
# # # #         if key not in config:
# # # #             return False, f"Missing required config key: {key}"

# # # #     return True, "Config is valid"


# # # # def check_session(config: dict):
# # # #     session = config.get("session", {})
# # # #     access_token = session.get("access_token", "")
# # # #     expires_at = session.get("expires_at", "")
# # # #     is_authenticated = session.get("is_authenticated", False)
# # # #     last_activity_at = config.get("last_activity_at", "")

# # # #     if not is_authenticated or not access_token or not expires_at:
# # # #         return {
# # # #             "valid": False,
# # # #             "reason": "missing_session"
# # # #         }

# # # #     try:
# # # #         expires_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
# # # #         if now_utc() >= expires_dt:
# # # #             return {
# # # #                 "valid": False,
# # # #                 "reason": "session_expired"
# # # #             }
# # # #     except Exception:
# # # #         return {
# # # #             "valid": False,
# # # #             "reason": "invalid_session_expiry"
# # # #         }

# # # #     if not last_activity_at:
# # # #         return {
# # # #             "valid": False,
# # # #             "reason": "missing_last_activity"
# # # #         }

# # # #     try:
# # # #         last_activity_dt = datetime.fromisoformat(last_activity_at.replace("Z", "+00:00"))
# # # #         if now_utc() - last_activity_dt > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
# # # #             return {
# # # #                 "valid": False,
# # # #                 "reason": "idle_timeout"
# # # #             }
# # # #     except Exception:
# # # #         return {
# # # #             "valid": False,
# # # #             "reason": "invalid_last_activity"
# # # #         }

# # # #     return {
# # # #         "valid": True,
# # # #         "reason": "session_valid"
# # # #     }


# # # # def check_subscription(config: dict):
# # # #     status = config.get("subscription_status", "unknown")

# # # #     if status in ["active", "trialing"]:
# # # #         return {
# # # #             "valid": True,
# # # #             "reason": "subscription_active"
# # # #         }

# # # #     return {
# # # #         "valid": False,
# # # #         "reason": "subscription_inactive"
# # # #     }


# # # # def check_data_directory(config: dict):
# # # #     data_dir = config.get("data_dir", "")
# # # #     if not data_dir:
# # # #         return {
# # # #             "valid": False,
# # # #             "reason": "missing_data_dir"
# # # #         }

# # # #     p = Path(data_dir)
# # # #     if not p.exists():
# # # #         return {
# # # #             "valid": False,
# # # #             "reason": "data_dir_not_found"
# # # #         }

# # # #     if not os.access(str(p), os.W_OK):
# # # #         return {
# # # #             "valid": False,
# # # #             "reason": "data_dir_not_writable"
# # # #         }

# # # #     return {
# # # #         "valid": True,
# # # #         "reason": "data_dir_ok"
# # # #     }


# # # # def check_models(config: dict):
# # # #     registry = config.get("model_registry", {})
# # # #     missing = []

# # # #     for model_name, meta in registry.items():
# # # #         if meta.get("required", False):
# # # #             model_path = meta.get("path", "")
# # # #             installed = meta.get("installed", False)

# # # #             if not installed or not model_path or not file_exists(model_path):
# # # #                 missing.append(model_name)

# # # #     if missing:
# # # #         return {
# # # #             "valid": False,
# # # #             "reason": "missing_model",
# # # #             "missing_models": missing
# # # #         }

# # # #     return {
# # # #         "valid": True,
# # # #         "reason": "models_ok",
# # # #         "missing_models": []
# # # #     }


# # # # def check_update_status(config: dict):
# # # #     current_version = config.get("app_version", APP_VERSION)

# # # #     if compare_versions(current_version, MANDATORY_UPDATE_VERSION):
# # # #         return {
# # # #             "status": "mandatory_update"
# # # #         }

# # # #     if compare_versions(current_version, LATEST_VERSION):
# # # #         return {
# # # #             "status": "optional_update"
# # # #         }

# # # #     return {
# # # #         "status": "up_to_date"
# # # #     }


# # # # # =========================================================
# # # # # USER STATE DECISION
# # # # # =========================================================

# # # # def determine_user_state():
# # # #     ensure_base_dirs()

# # # #     if not CONFIG_PATH.exists():
# # # #         return {
# # # #             "state": "new_user",
# # # #             "reason": "no_config"
# # # #         }

# # # #     config = safe_read_json(CONFIG_PATH)
# # # #     if not config:
# # # #         return {
# # # #             "state": "recovery_required",
# # # #             "reason": "config_corrupted"
# # # #         }

# # # #     valid_config, config_reason = validate_config(config)
# # # #     if not valid_config:
# # # #         return {
# # # #             "state": "recovery_required",
# # # #             "reason": "config_invalid",
# # # #             "detail": config_reason
# # # #         }

# # # #     if not config.get("setup_completed", False):
# # # #         return {
# # # #             "state": "setup_incomplete",
# # # #             "reason": "setup_not_completed"
# # # #         }

# # # #     data_check = check_data_directory(config)
# # # #     if not data_check["valid"]:
# # # #         return {
# # # #             "state": "recovery_required",
# # # #             "reason": data_check["reason"]
# # # #         }

# # # #     model_check = check_models(config)
# # # #     if not model_check["valid"]:
# # # #         return {
# # # #             "state": "recovery_required",
# # # #             "reason": model_check["reason"],
# # # #             "missing_models": model_check.get("missing_models", [])
# # # #         }

# # # #     subscription_check = check_subscription(config)
# # # #     if not subscription_check["valid"]:
# # # #         return {
# # # #             "state": "subscription_required",
# # # #             "reason": subscription_check["reason"]
# # # #         }

# # # #     session_check = check_session(config)
# # # #     if not session_check["valid"]:
# # # #         return {
# # # #             "state": "login_required",
# # # #             "reason": session_check["reason"]
# # # #         }

# # # #     update_check = check_update_status(config)
# # # #     if update_check["status"] == "mandatory_update":
# # # #         return {
# # # #             "state": "update_required",
# # # #             "reason": "mandatory_update"
# # # #         }

# # # #     if update_check["status"] == "optional_update":
# # # #         return {
# # # #             "state": "healthy_with_optional_update",
# # # #             "reason": "optional_update"
# # # #         }

# # # #     return {
# # # #         "state": "healthy",
# # # #         "reason": "app_healthy"
# # # #     }


# # # # # =========================================================
# # # # # SETUP FLOW
# # # # # =========================================================

# # # # def create_data_structure(data_dir: str):
# # # #     base = Path(data_dir)
# # # #     models_dir = base / "models"
# # # #     outputs_dir = base / "outputs"
# # # #     assets_dir = base / "assets"
# # # #     temp_dir = base / "temp"

# # # #     for p in [base, models_dir, outputs_dir, assets_dir, temp_dir]:
# # # #         p.mkdir(parents=True, exist_ok=True)

# # # #     return {
# # # #         "data_dir": str(base),
# # # #         "models_dir": str(models_dir),
# # # #         "outputs_dir": str(outputs_dir),
# # # #         "assets_dir": str(assets_dir),
# # # #         "temp_dir": str(temp_dir)
# # # #     }


# # # # def install_demo_models(config: dict):
# # # #     models_dir = Path(config["models_dir"])
# # # #     core_model_dir = models_dir / "core_model_v1"
# # # #     core_model_dir.mkdir(parents=True, exist_ok=True)

# # # #     demo_file = core_model_dir / "model.ready"
# # # #     demo_file.write_text("Basira local model installed", encoding="utf-8")

# # # #     config["model_registry"]["core_model_v1"]["installed"] = True
# # # #     config["model_registry"]["core_model_v1"]["path"] = str(demo_file)

# # # #     return config


# # # # def environment_self_check(config: dict):
# # # #     results = {
# # # #         "config_valid": validate_config(config)[0],
# # # #         "data_dir": check_data_directory(config),
# # # #         "models": check_models(config),
# # # #         "session": check_session(config),
# # # #         "update": check_update_status(config)
# # # #     }

# # # #     all_good = (
# # # #         results["config_valid"]
# # # #         and results["data_dir"]["valid"]
# # # #         and results["models"]["valid"]
# # # #     )

# # # #     return {
# # # #         "ok": all_good,
# # # #         "results": results
# # # #     }


# # # # def mark_activity(config: dict):
# # # #     config["last_activity_at"] = now_iso()
# # # #     config["last_session_check"] = now_iso()
# # # #     return config


# # # # # =========================================================
# # # # # API ROUTES
# # # # # =========================================================

# # # # @app.route("/")
# # # # def root():
# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "service": "basira_local_bootstrap",
# # # #         "version": APP_VERSION
# # # #     })


# # # # @app.route("/health")
# # # # def health():
# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "app": APP_NAME,
# # # #         "version": APP_VERSION
# # # #     })


# # # # @app.route("/api/startup-status", methods=["GET"])
# # # # def startup_status():
# # # #     state = determine_user_state()
# # # #     return jsonify(state)


# # # # @app.route("/api/setup/init", methods=["POST"])
# # # # def setup_init():
# # # #     ensure_base_dirs()

# # # #     if not CONFIG_PATH.exists():
# # # #         config = build_default_config()
# # # #         safe_write_json(CONFIG_PATH, config)

# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "message": "Setup initialized"
# # # #     })


# # # # @app.route("/api/setup/login-complete", methods=["POST"])
# # # # def setup_login_complete():
# # # #     payload = request.json or {}

# # # #     user_id = payload.get("user_id", "")
# # # #     access_token = payload.get("access_token", "")
# # # #     refresh_token = payload.get("refresh_token", "")
# # # #     expires_at = payload.get("expires_at", "")
# # # #     subscription_status = payload.get("subscription_status", "active")

# # # #     config = safe_read_json(CONFIG_PATH) or build_default_config()

# # # #     config["user_id"] = user_id
# # # #     config["last_login_at"] = now_iso()
# # # #     config["subscription_status"] = subscription_status
# # # #     config["session"] = {
# # # #         "access_token": access_token,
# # # #         "refresh_token": refresh_token,
# # # #         "expires_at": expires_at,
# # # #         "is_authenticated": True
# # # #     }

# # # #     config = mark_activity(config)
# # # #     safe_write_json(CONFIG_PATH, config)

# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "message": "Login linked to local app"
# # # #     })


# # # # @app.route("/api/setup/select-data-dir", methods=["POST"])
# # # # def setup_select_data_dir():
# # # #     payload = request.json or {}
# # # #     data_dir = payload.get("data_dir", "").strip()

# # # #     if not data_dir:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": "Data directory is required"
# # # #         }), 400

# # # #     try:
# # # #         created = create_data_structure(data_dir)
# # # #     except Exception as e:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": f"Could not create data directory: {str(e)}"
# # # #         }), 400

# # # #     config = safe_read_json(CONFIG_PATH) or build_default_config()

# # # #     config["data_dir"] = created["data_dir"]
# # # #     config["models_dir"] = created["models_dir"]
# # # #     config["outputs_dir"] = created["outputs_dir"]
# # # #     config["assets_dir"] = created["assets_dir"]
# # # #     config["temp_dir"] = created["temp_dir"]

# # # #     safe_write_json(CONFIG_PATH, config)

# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "message": "Data directory configured",
# # # #         "paths": created
# # # #     })


# # # # @app.route("/api/setup/install-models", methods=["POST"])
# # # # def setup_install_models():
# # # #     config = safe_read_json(CONFIG_PATH)
# # # #     if not config:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": "Missing config"
# # # #         }), 400

# # # #     config = install_demo_models(config)
# # # #     safe_write_json(CONFIG_PATH, config)

# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "message": "Models installed"
# # # #     })


# # # # @app.route("/api/setup/verify", methods=["GET"])
# # # # def setup_verify():
# # # #     config = safe_read_json(CONFIG_PATH)
# # # #     if not config:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": "Config not found"
# # # #         }), 400

# # # #     result = environment_self_check(config)

# # # #     return jsonify({
# # # #         "status": "ok" if result["ok"] else "error",
# # # #         "verification": result
# # # #     })


# # # # @app.route("/api/setup/finalize", methods=["POST"])
# # # # def setup_finalize():
# # # #     config = safe_read_json(CONFIG_PATH)
# # # #     if not config:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": "Config not found"
# # # #         }), 400

# # # #     config["setup_completed"] = True
# # # #     config["setup_completed_at"] = now_iso()
# # # #     config = mark_activity(config)

# # # #     safe_write_json(CONFIG_PATH, config)

# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "message": "Setup completed"
# # # #     })


# # # # @app.route("/api/config", methods=["GET"])
# # # # def get_config():
# # # #     config = safe_read_json(CONFIG_PATH)
# # # #     if not config:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": "Config not found"
# # # #         }), 404

# # # #     return jsonify(config)


# # # # @app.route("/api/recovery/repair-models", methods=["POST"])
# # # # def repair_models():
# # # #     config = safe_read_json(CONFIG_PATH)
# # # #     if not config:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": "Config not found"
# # # #         }), 404

# # # #     config = install_demo_models(config)
# # # #     safe_write_json(CONFIG_PATH, config)

# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "message": "Models repaired"
# # # #     })


# # # # @app.route("/api/recovery/reselect-data-dir", methods=["POST"])
# # # # def recovery_reselect_data_dir():
# # # #     payload = request.json or {}
# # # #     data_dir = payload.get("data_dir", "").strip()

# # # #     if not data_dir:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": "Data directory is required"
# # # #         }), 400

# # # #     try:
# # # #         created = create_data_structure(data_dir)
# # # #     except Exception as e:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": f"Could not reconfigure data directory: {str(e)}"
# # # #         }), 400

# # # #     config = safe_read_json(CONFIG_PATH)
# # # #     if not config:
# # # #         config = build_default_config()

# # # #     config["data_dir"] = created["data_dir"]
# # # #     config["models_dir"] = created["models_dir"]
# # # #     config["outputs_dir"] = created["outputs_dir"]
# # # #     config["assets_dir"] = created["assets_dir"]
# # # #     config["temp_dir"] = created["temp_dir"]

# # # #     safe_write_json(CONFIG_PATH, config)

# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "message": "Data directory updated",
# # # #         "paths": created
# # # #     })


# # # # @app.route("/api/session/refresh", methods=["POST"])
# # # # def session_refresh():
# # # #     payload = request.json or {}

# # # #     access_token = payload.get("access_token", "")
# # # #     refresh_token = payload.get("refresh_token", "")
# # # #     expires_at = payload.get("expires_at", "")
# # # #     subscription_status = payload.get("subscription_status", "active")

# # # #     config = safe_read_json(CONFIG_PATH)
# # # #     if not config:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": "Config not found"
# # # #         }), 404

# # # #     config["session"]["access_token"] = access_token
# # # #     config["session"]["refresh_token"] = refresh_token
# # # #     config["session"]["expires_at"] = expires_at
# # # #     config["session"]["is_authenticated"] = True
# # # #     config["subscription_status"] = subscription_status
# # # #     config["last_login_at"] = now_iso()
# # # #     config = mark_activity(config)

# # # #     safe_write_json(CONFIG_PATH, config)

# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "message": "Session refreshed"
# # # #     })


# # # # @app.route("/api/auth/heartbeat", methods=["POST"])
# # # # def auth_heartbeat():
# # # #     config = safe_read_json(CONFIG_PATH)
# # # #     if not config:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": "Config not found"
# # # #         }), 404

# # # #     session_check = check_session(config)
# # # #     if not session_check["valid"]:
# # # #         config["session"]["is_authenticated"] = False
# # # #         safe_write_json(CONFIG_PATH, config)
# # # #         return jsonify({
# # # #             "status": "expired",
# # # #             "reason": session_check["reason"]
# # # #         }), 401

# # # #     config = mark_activity(config)
# # # #     safe_write_json(CONFIG_PATH, config)

# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "message": "Heartbeat accepted"
# # # #     })


# # # # @app.route("/api/auth/auto-logout", methods=["POST"])
# # # # def auto_logout():
# # # #     config = safe_read_json(CONFIG_PATH)
# # # #     if not config:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": "Config not found"
# # # #         }), 404

# # # #     config["session"]["is_authenticated"] = False
# # # #     config["session"]["access_token"] = ""
# # # #     config["session"]["refresh_token"] = ""
# # # #     config["session"]["expires_at"] = ""
# # # #     config["last_activity_at"] = now_iso()

# # # #     safe_write_json(CONFIG_PATH, config)

# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "message": "Logged out due to inactivity"
# # # #     })


# # # # @app.route("/api/subscription/renew-demo", methods=["POST"])
# # # # def renew_demo():
# # # #     config = safe_read_json(CONFIG_PATH)
# # # #     if not config:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": "Config not found"
# # # #         }), 404

# # # #     config["subscription_status"] = "active"
# # # #     safe_write_json(CONFIG_PATH, config)

# # # #     return jsonify({
# # # #         "status": "ok",
# # # #         "message": "Subscription renewed (demo)"
# # # #     })


# # # # if __name__ == "__main__":
# # # #     ensure_base_dirs()
# # # #     app.run(host="127.0.0.1", port=LOCAL_API_PORT, debug=True)

# # # import os
# # # import json
# # # import platform
# # # import threading
# # # from pathlib import Path
# # # from datetime import datetime, timezone, timedelta
# # # from tkinter import Tk, filedialog

# # # from flask import Flask, jsonify, request
# # # from flask_cors import CORS

# # # app = Flask(__name__)
# # # CORS(app)

# # # APP_NAME = "Basira"
# # # APP_VERSION = "1.0.0"
# # # LOCAL_API_PORT = 5001
# # # LOCAL_API_URL = f"http://127.0.0.1:{LOCAL_API_PORT}"

# # # CLOUD_API_BASE_URL = "https://basira.basira-toolmodel.workers.dev"
# # # CLOUD_RENEW_URL = "https://basira.basira-toolmodel.workers.dev/renew"

# # # LATEST_VERSION = "1.0.0"
# # # MANDATORY_UPDATE_VERSION = "0.9.0"
# # # SESSION_TIMEOUT_MINUTES = 20


# # # # =========================================================
# # # # PATHS
# # # # =========================================================

# # # def get_os_name():
# # #     system = platform.system().lower()
# # #     if "windows" in system:
# # #         return "windows"
# # #     if "darwin" in system:
# # #         return "mac"
# # #     return "other"


# # # def get_appdata_dir():
# # #     os_name = get_os_name()

# # #     if os_name == "windows":
# # #         base = os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming"))
# # #         return Path(base) / APP_NAME

# # #     if os_name == "mac":
# # #         return Path.home() / "Library" / "Application Support" / APP_NAME

# # #     return Path.home() / f".{APP_NAME.lower()}"


# # # APPDATA_DIR = get_appdata_dir()
# # # LOGS_DIR = APPDATA_DIR / "logs"
# # # CACHE_DIR = APPDATA_DIR / "cache"
# # # SESSION_DIR = APPDATA_DIR / "session"
# # # CONFIG_PATH = APPDATA_DIR / "config.json"
# # # SETUP_STATE_PATH = APPDATA_DIR / "setup_state.json"
# # # VERSION_INFO_PATH = APPDATA_DIR / "version_info.json"


# # # # =========================================================
# # # # HELPERS
# # # # =========================================================

# # # def ensure_base_dirs():
# # #     APPDATA_DIR.mkdir(parents=True, exist_ok=True)
# # #     LOGS_DIR.mkdir(parents=True, exist_ok=True)
# # #     CACHE_DIR.mkdir(parents=True, exist_ok=True)
# # #     SESSION_DIR.mkdir(parents=True, exist_ok=True)


# # # def now_utc():
# # #     return datetime.now(timezone.utc)


# # # def now_iso():
# # #     return now_utc().isoformat()


# # # def safe_read_json(path: Path):
# # #     try:
# # #         if not path.exists():
# # #             return None
# # #         with open(path, "r", encoding="utf-8") as f:
# # #             return json.load(f)
# # #     except Exception:
# # #         return None


# # # def safe_write_json(path: Path, data: dict):
# # #     path.parent.mkdir(parents=True, exist_ok=True)
# # #     with open(path, "w", encoding="utf-8") as f:
# # #         json.dump(data, f, indent=2, ensure_ascii=False)


# # # def compare_versions(v1: str, v2: str):
# # #     def parse(v):
# # #         return [int(x) for x in v.split(".")]
# # #     return parse(v1) < parse(v2)


# # # def file_exists(path_str):
# # #     try:
# # #         return Path(path_str).exists()
# # #     except Exception:
# # #         return False


# # # def default_data_dir():
# # #     return Path.home() / "Documents" / "BasiraData"


# # # def open_native_folder_picker():
# # #     selected_path = {"value": ""}

# # #     def _pick():
# # #         root = Tk()
# # #         root.withdraw()
# # #         root.attributes("-topmost", True)
# # #         path = filedialog.askdirectory(title="اختيار مسار حفظ بيانات Basira")
# # #         selected_path["value"] = path or ""
# # #         root.destroy()

# # #     thread = threading.Thread(target=_pick)
# # #     thread.start()
# # #     thread.join()

# # #     return selected_path["value"]


# # # # =========================================================
# # # # CONFIG DESIGN
# # # # =========================================================

# # # def build_default_config(data_dir: str = "", user_id: str = ""):
# # #     data_path = Path(data_dir) if data_dir else default_data_dir()

# # #     return {
# # #         "app_version": APP_VERSION,
# # #         "setup_completed": False,
# # #         "setup_completed_at": None,

# # #         "data_dir": str(data_path),
# # #         "models_dir": str(data_path / "models"),
# # #         "outputs_dir": str(data_path / "outputs"),
# # #         "assets_dir": str(data_path / "assets"),
# # #         "temp_dir": str(data_path / "temp"),

# # #         "local_api_url": LOCAL_API_URL,
# # #         "api_base_url": CLOUD_API_BASE_URL,

# # #         "user_id": user_id,
# # #         "last_login_at": None,
# # #         "last_session_check": None,
# # #         "last_activity_at": None,

# # #         "subscription_status": "unknown",
# # #         "subscription_expires_at": None,

# # #         "last_update_check": None,
# # #         "update_status": "unknown",

# # #         "session_timeout_minutes": SESSION_TIMEOUT_MINUTES,

# # #         "session": {
# # #             "access_token": "",
# # #             "refresh_token": "",
# # #             "expires_at": "",
# # #             "is_authenticated": False
# # #         },

# # #         "model_registry": {
# # #             "core_model_v1": {
# # #                 "required": True,
# # #                 "installed": False,
# # #                 "path": "",
# # #                 "version": "1.0.0"
# # #             }
# # #         }
# # #     }


# # # # =========================================================
# # # # ENVIRONMENT CHECKS
# # # # =========================================================

# # # def validate_config(config: dict):
# # #     if not isinstance(config, dict):
# # #         return False, "Config is not a valid JSON object"

# # #     required_keys = [
# # #         "app_version",
# # #         "setup_completed",
# # #         "data_dir",
# # #         "models_dir",
# # #         "outputs_dir",
# # #         "assets_dir",
# # #         "local_api_url",
# # #         "api_base_url",
# # #         "user_id",
# # #         "session",
# # #         "model_registry"
# # #     ]

# # #     for key in required_keys:
# # #         if key not in config:
# # #             return False, f"Missing required config key: {key}"

# # #     return True, "Config is valid"


# # # def check_session(config: dict):
# # #     session = config.get("session", {})
# # #     access_token = session.get("access_token", "")
# # #     expires_at = session.get("expires_at", "")
# # #     is_authenticated = session.get("is_authenticated", False)
# # #     last_activity_at = config.get("last_activity_at", "")

# # #     if not is_authenticated or not access_token or not expires_at:
# # #         return {
# # #             "valid": False,
# # #             "reason": "missing_session"
# # #         }

# # #     try:
# # #         expires_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
# # #         if now_utc() >= expires_dt:
# # #             return {
# # #                 "valid": False,
# # #                 "reason": "session_expired"
# # #             }
# # #     except Exception:
# # #         return {
# # #             "valid": False,
# # #             "reason": "invalid_session_expiry"
# # #         }

# # #     if not last_activity_at:
# # #         return {
# # #             "valid": False,
# # #             "reason": "missing_last_activity"
# # #         }

# # #     try:
# # #         last_activity_dt = datetime.fromisoformat(last_activity_at.replace("Z", "+00:00"))
# # #         if now_utc() - last_activity_dt > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
# # #             return {
# # #                 "valid": False,
# # #                 "reason": "idle_timeout"
# # #             }
# # #     except Exception:
# # #         return {
# # #             "valid": False,
# # #             "reason": "invalid_last_activity"
# # #         }

# # #     return {
# # #         "valid": True,
# # #         "reason": "session_valid"
# # #     }


# # # def check_subscription(config: dict):
# # #     status = config.get("subscription_status", "unknown")

# # #     if status in ["active", "trialing"]:
# # #         return {
# # #             "valid": True,
# # #             "reason": "subscription_active"
# # #         }

# # #     return {
# # #         "valid": False,
# # #         "reason": "subscription_inactive"
# # #     }


# # # def check_data_directory(config: dict):
# # #     data_dir = config.get("data_dir", "")
# # #     if not data_dir:
# # #         return {
# # #             "valid": False,
# # #             "reason": "missing_data_dir"
# # #         }

# # #     p = Path(data_dir)
# # #     if not p.exists():
# # #         return {
# # #             "valid": False,
# # #             "reason": "data_dir_not_found"
# # #         }

# # #     if not os.access(str(p), os.W_OK):
# # #         return {
# # #             "valid": False,
# # #             "reason": "data_dir_not_writable"
# # #         }

# # #     return {
# # #         "valid": True,
# # #         "reason": "data_dir_ok"
# # #     }


# # # def check_models(config: dict):
# # #     registry = config.get("model_registry", {})
# # #     missing = []

# # #     for model_name, meta in registry.items():
# # #         if meta.get("required", False):
# # #             model_path = meta.get("path", "")
# # #             installed = meta.get("installed", False)

# # #             if not installed or not model_path or not file_exists(model_path):
# # #                 missing.append(model_name)

# # #     if missing:
# # #         return {
# # #             "valid": False,
# # #             "reason": "missing_model",
# # #             "missing_models": missing
# # #         }

# # #     return {
# # #         "valid": True,
# # #         "reason": "models_ok",
# # #         "missing_models": []
# # #     }


# # # def check_update_status(config: dict):
# # #     current_version = config.get("app_version", APP_VERSION)

# # #     if compare_versions(current_version, MANDATORY_UPDATE_VERSION):
# # #         return {
# # #             "status": "mandatory_update"
# # #         }

# # #     if compare_versions(current_version, LATEST_VERSION):
# # #         return {
# # #             "status": "optional_update"
# # #         }

# # #     return {
# # #         "status": "up_to_date"
# # #     }


# # # # =========================================================
# # # # USER STATE DECISION
# # # # =========================================================

# # # def determine_user_state():
# # #     ensure_base_dirs()

# # #     if not CONFIG_PATH.exists():
# # #         return {
# # #             "state": "new_user",
# # #             "reason": "no_config"
# # #         }

# # #     config = safe_read_json(CONFIG_PATH)
# # #     if not config:
# # #         return {
# # #             "state": "recovery_required",
# # #             "reason": "config_corrupted"
# # #         }

# # #     valid_config, config_reason = validate_config(config)
# # #     if not valid_config:
# # #         return {
# # #             "state": "recovery_required",
# # #             "reason": "config_invalid",
# # #             "detail": config_reason
# # #         }

# # #     if not config.get("setup_completed", False):
# # #         return {
# # #             "state": "setup_incomplete",
# # #             "reason": "setup_not_completed"
# # #         }

# # #     data_check = check_data_directory(config)
# # #     if not data_check["valid"]:
# # #         return {
# # #             "state": "recovery_required",
# # #             "reason": data_check["reason"]
# # #         }

# # #     model_check = check_models(config)
# # #     if not model_check["valid"]:
# # #         return {
# # #             "state": "recovery_required",
# # #             "reason": model_check["reason"],
# # #             "missing_models": model_check.get("missing_models", [])
# # #         }

# # #     subscription_check = check_subscription(config)
# # #     if not subscription_check["valid"]:
# # #         return {
# # #             "state": "subscription_required",
# # #             "reason": subscription_check["reason"]
# # #         }

# # #     session_check = check_session(config)
# # #     if not session_check["valid"]:
# # #         return {
# # #             "state": "login_required",
# # #             "reason": session_check["reason"]
# # #         }

# # #     update_check = check_update_status(config)
# # #     if update_check["status"] == "mandatory_update":
# # #         return {
# # #             "state": "update_required",
# # #             "reason": "mandatory_update"
# # #         }

# # #     if update_check["status"] == "optional_update":
# # #         return {
# # #             "state": "healthy_with_optional_update",
# # #             "reason": "optional_update"
# # #         }

# # #     return {
# # #         "state": "healthy",
# # #         "reason": "app_healthy"
# # #     }


# # # # =========================================================
# # # # SETUP FLOW
# # # # =========================================================

# # # def create_data_structure(data_dir: str):
# # #     base = Path(data_dir)
# # #     models_dir = base / "models"
# # #     outputs_dir = base / "outputs"
# # #     assets_dir = base / "assets"
# # #     temp_dir = base / "temp"

# # #     for p in [base, models_dir, outputs_dir, assets_dir, temp_dir]:
# # #         p.mkdir(parents=True, exist_ok=True)

# # #     return {
# # #         "data_dir": str(base),
# # #         "models_dir": str(models_dir),
# # #         "outputs_dir": str(outputs_dir),
# # #         "assets_dir": str(assets_dir),
# # #         "temp_dir": str(temp_dir)
# # #     }


# # # def install_demo_models(config: dict):
# # #     models_dir = Path(config["models_dir"])
# # #     core_model_dir = models_dir / "core_model_v1"
# # #     core_model_dir.mkdir(parents=True, exist_ok=True)

# # #     demo_file = core_model_dir / "model.ready"
# # #     demo_file.write_text("Basira local model installed", encoding="utf-8")

# # #     config["model_registry"]["core_model_v1"]["installed"] = True
# # #     config["model_registry"]["core_model_v1"]["path"] = str(demo_file)

# # #     return config


# # # def environment_self_check(config: dict):
# # #     results = {
# # #         "config_valid": validate_config(config)[0],
# # #         "data_dir": check_data_directory(config),
# # #         "models": check_models(config),
# # #         "session": check_session(config),
# # #         "update": check_update_status(config)
# # #     }

# # #     all_good = (
# # #         results["config_valid"]
# # #         and results["data_dir"]["valid"]
# # #         and results["models"]["valid"]
# # #     )

# # #     return {
# # #         "ok": all_good,
# # #         "results": results
# # #     }


# # # def mark_activity(config: dict):
# # #     config["last_activity_at"] = now_iso()
# # #     config["last_session_check"] = now_iso()
# # #     return config


# # # # =========================================================
# # # # API ROUTES
# # # # =========================================================

# # # @app.route("/")
# # # def root():
# # #     return jsonify({
# # #         "status": "ok",
# # #         "service": "basira_local_bootstrap",
# # #         "version": APP_VERSION
# # #     })


# # # @app.route("/health")
# # # def health():
# # #     return jsonify({
# # #         "status": "ok",
# # #         "app": APP_NAME,
# # #         "version": APP_VERSION
# # #     })


# # # @app.route("/api/startup-status", methods=["GET"])
# # # def startup_status():
# # #     state = determine_user_state()
# # #     return jsonify(state)


# # # @app.route("/api/system/pick-data-dir", methods=["GET"])
# # # def pick_data_dir():
# # #     try:
# # #         selected = open_native_folder_picker()
# # #         return jsonify({
# # #             "status": "ok",
# # #             "path": selected
# # #         })
# # #     except Exception as e:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": str(e)
# # #         }), 500


# # # @app.route("/api/setup/init", methods=["POST"])
# # # def setup_init():
# # #     ensure_base_dirs()

# # #     if not CONFIG_PATH.exists():
# # #         config = build_default_config()
# # #         safe_write_json(CONFIG_PATH, config)

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Setup initialized"
# # #     })


# # # @app.route("/api/setup/login-complete", methods=["POST"])
# # # def setup_login_complete():
# # #     payload = request.json or {}

# # #     user_id = payload.get("user_id", "")
# # #     access_token = payload.get("access_token", "")
# # #     refresh_token = payload.get("refresh_token", "")
# # #     expires_at = payload.get("expires_at", "")
# # #     subscription_status = payload.get("subscription_status", "active")

# # #     config = safe_read_json(CONFIG_PATH) or build_default_config()

# # #     config["user_id"] = user_id
# # #     config["last_login_at"] = now_iso()
# # #     config["subscription_status"] = subscription_status
# # #     config["session"] = {
# # #         "access_token": access_token,
# # #         "refresh_token": refresh_token,
# # #         "expires_at": expires_at,
# # #         "is_authenticated": True
# # #     }

# # #     config = mark_activity(config)
# # #     safe_write_json(CONFIG_PATH, config)

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Login linked to local app"
# # #     })


# # # @app.route("/api/setup/select-data-dir", methods=["POST"])
# # # def setup_select_data_dir():
# # #     payload = request.json or {}
# # #     data_dir = payload.get("data_dir", "").strip()

# # #     if not data_dir:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Data directory is required"
# # #         }), 400

# # #     try:
# # #         created = create_data_structure(data_dir)
# # #     except Exception as e:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": f"Could not create data directory: {str(e)}"
# # #         }), 400

# # #     config = safe_read_json(CONFIG_PATH) or build_default_config()

# # #     config["data_dir"] = created["data_dir"]
# # #     config["models_dir"] = created["models_dir"]
# # #     config["outputs_dir"] = created["outputs_dir"]
# # #     config["assets_dir"] = created["assets_dir"]
# # #     config["temp_dir"] = created["temp_dir"]

# # #     safe_write_json(CONFIG_PATH, config)

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Data directory configured",
# # #         "paths": created
# # #     })


# # # @app.route("/api/setup/install-models", methods=["POST"])
# # # def setup_install_models():
# # #     config = safe_read_json(CONFIG_PATH)
# # #     if not config:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Missing config"
# # #         }), 400

# # #     config = install_demo_models(config)
# # #     safe_write_json(CONFIG_PATH, config)

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Models installed"
# # #     })


# # # @app.route("/api/setup/verify", methods=["GET"])
# # # def setup_verify():
# # #     config = safe_read_json(CONFIG_PATH)
# # #     if not config:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Config not found"
# # #         }), 400

# # #     result = environment_self_check(config)

# # #     return jsonify({
# # #         "status": "ok" if result["ok"] else "error",
# # #         "verification": result
# # #     })


# # # @app.route("/api/setup/finalize", methods=["POST"])
# # # def setup_finalize():
# # #     config = safe_read_json(CONFIG_PATH)
# # #     if not config:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Config not found"
# # #         }), 400

# # #     config["setup_completed"] = True
# # #     config["setup_completed_at"] = now_iso()
# # #     config = mark_activity(config)

# # #     safe_write_json(CONFIG_PATH, config)

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Setup completed"
# # #     })


# # # @app.route("/api/config", methods=["GET"])
# # # def get_config():
# # #     config = safe_read_json(CONFIG_PATH)
# # #     if not config:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Config not found"
# # #         }), 404

# # #     return jsonify(config)


# # # @app.route("/api/recovery/repair-models", methods=["POST"])
# # # def repair_models():
# # #     config = safe_read_json(CONFIG_PATH)
# # #     if not config:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Config not found"
# # #         }), 404

# # #     config = install_demo_models(config)
# # #     safe_write_json(CONFIG_PATH, config)

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Models repaired"
# # #     })


# # # @app.route("/api/recovery/reselect-data-dir", methods=["POST"])
# # # def recovery_reselect_data_dir():
# # #     payload = request.json or {}
# # #     data_dir = payload.get("data_dir", "").strip()

# # #     if not data_dir:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Data directory is required"
# # #         }), 400

# # #     try:
# # #         created = create_data_structure(data_dir)
# # #     except Exception as e:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": f"Could not reconfigure data directory: {str(e)}"
# # #         }), 400

# # #     config = safe_read_json(CONFIG_PATH)
# # #     if not config:
# # #         config = build_default_config()

# # #     config["data_dir"] = created["data_dir"]
# # #     config["models_dir"] = created["models_dir"]
# # #     config["outputs_dir"] = created["outputs_dir"]
# # #     config["assets_dir"] = created["assets_dir"]
# # #     config["temp_dir"] = created["temp_dir"]

# # #     safe_write_json(CONFIG_PATH, config)

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Data directory updated",
# # #         "paths": created
# # #     })


# # # @app.route("/api/session/refresh", methods=["POST"])
# # # def session_refresh():
# # #     payload = request.json or {}

# # #     access_token = payload.get("access_token", "")
# # #     refresh_token = payload.get("refresh_token", "")
# # #     expires_at = payload.get("expires_at", "")
# # #     subscription_status = payload.get("subscription_status", "active")

# # #     config = safe_read_json(CONFIG_PATH)
# # #     if not config:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Config not found"
# # #         }), 404

# # #     config["session"]["access_token"] = access_token
# # #     config["session"]["refresh_token"] = refresh_token
# # #     config["session"]["expires_at"] = expires_at
# # #     config["session"]["is_authenticated"] = True
# # #     config["subscription_status"] = subscription_status
# # #     config["last_login_at"] = now_iso()
# # #     config = mark_activity(config)

# # #     safe_write_json(CONFIG_PATH, config)

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Session refreshed"
# # #     })


# # # @app.route("/api/auth/heartbeat", methods=["POST"])
# # # def auth_heartbeat():
# # #     config = safe_read_json(CONFIG_PATH)
# # #     if not config:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Config not found"
# # #         }), 404

# # #     session_check = check_session(config)
# # #     if not session_check["valid"]:
# # #         config["session"]["is_authenticated"] = False
# # #         safe_write_json(CONFIG_PATH, config)
# # #         return jsonify({
# # #             "status": "expired",
# # #             "reason": session_check["reason"]
# # #         }), 401

# # #     config = mark_activity(config)
# # #     safe_write_json(CONFIG_PATH, config)

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Heartbeat accepted"
# # #     })


# # # @app.route("/api/auth/auto-logout", methods=["POST"])
# # # def auto_logout():
# # #     config = safe_read_json(CONFIG_PATH)
# # #     if not config:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Config not found"
# # #         }), 404

# # #     config["session"]["is_authenticated"] = False
# # #     config["session"]["access_token"] = ""
# # #     config["session"]["refresh_token"] = ""
# # #     config["session"]["expires_at"] = ""
# # #     config["last_activity_at"] = now_iso()

# # #     safe_write_json(CONFIG_PATH, config)

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Logged out due to inactivity"
# # #     })


# # # @app.route("/api/subscription/renew-demo", methods=["POST"])
# # # def renew_demo():
# # #     config = safe_read_json(CONFIG_PATH)
# # #     if not config:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Config not found"
# # #         }), 404

# # #     config["subscription_status"] = "active"
# # #     safe_write_json(CONFIG_PATH, config)

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Subscription renewed (demo)"
# # #     })


# # # if __name__ == "__main__":
# # #     ensure_base_dirs()
# # #     app.run(host="127.0.0.1", port=LOCAL_API_PORT, debug=True)

# # """
# # basira_local_bootstrap.py — Basira Setup & Session API
# # =======================================================
# # Runs locally on http://127.0.0.1:5001
# # Called by the cloud page (local-setup.js) after the user logs in via Supabase.

# # Responsibilities:
# #   • Determine first-run vs. returning user state  (/api/startup-status)
# #   • Native folder picker for data directory       (/api/system/pick-data-dir)
# #   • Setup flow (init → select-data-dir → install-models → finalize)
# #   • Persist session tokens from cloud login       (/api/setup/login-complete)
# #   • Heartbeat / auto-logout                       (/api/auth/heartbeat)
# #   • Config and subscription helpers
# # """

# # import os
# # import json
# # import platform
# # import threading
# # from pathlib import Path
# # from datetime import datetime, timezone, timedelta
# # from tkinter import Tk, filedialog

# # from flask import Flask, jsonify, request
# # from flask_cors import CORS

# # # ─── App ──────────────────────────────────────────────────────────────────────
# # app = Flask(__name__)
# # CORS(app)

# # APP_NAME     = "Basira"
# # APP_VERSION  = "1.0.0"
# # LOCAL_API_PORT = 5001
# # LOCAL_API_URL  = f"http://127.0.0.1:{LOCAL_API_PORT}"

# # CLOUD_API_BASE_URL = "https://basira.basira-toolmodel.workers.dev"
# # CLOUD_RENEW_URL    = "https://basira.basira-toolmodel.workers.dev/renew"

# # LATEST_VERSION           = "1.0.0"
# # MANDATORY_UPDATE_VERSION = "0.9.0"
# # SESSION_TIMEOUT_MINUTES  = 20


# # # ─── Paths ────────────────────────────────────────────────────────────────────
# # def get_os_name():
# #     system = platform.system().lower()
# #     if "windows" in system:
# #         return "windows"
# #     if "darwin" in system:
# #         return "mac"
# #     return "other"


# # def get_appdata_dir():
# #     os_name = get_os_name()
# #     if os_name == "windows":
# #         base = os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming"))
# #         return Path(base) / APP_NAME
# #     if os_name == "mac":
# #         return Path.home() / "Library" / "Application Support" / APP_NAME
# #     return Path.home() / f".{APP_NAME.lower()}"


# # APPDATA_DIR      = get_appdata_dir()
# # LOGS_DIR         = APPDATA_DIR / "logs"
# # CACHE_DIR        = APPDATA_DIR / "cache"
# # SESSION_DIR      = APPDATA_DIR / "session"
# # CONFIG_PATH      = APPDATA_DIR / "config.json"
# # SETUP_STATE_PATH = APPDATA_DIR / "setup_state.json"
# # VERSION_INFO_PATH = APPDATA_DIR / "version_info.json"


# # # ─── Helpers ──────────────────────────────────────────────────────────────────
# # def ensure_base_dirs():
# #     for d in [APPDATA_DIR, LOGS_DIR, CACHE_DIR, SESSION_DIR]:
# #         d.mkdir(parents=True, exist_ok=True)


# # def now_utc():
# #     return datetime.now(timezone.utc)


# # def now_iso():
# #     return now_utc().isoformat()


# # def safe_read_json(path: Path):
# #     try:
# #         if not path.exists():
# #             return None
# #         with open(path, "r", encoding="utf-8") as f:
# #             return json.load(f)
# #     except Exception:
# #         return None


# # def safe_write_json(path: Path, data: dict):
# #     path.parent.mkdir(parents=True, exist_ok=True)
# #     with open(path, "w", encoding="utf-8") as f:
# #         json.dump(data, f, indent=2, ensure_ascii=False)


# # def compare_versions(v1: str, v2: str) -> bool:
# #     """Return True if v1 < v2."""
# #     def parse(v):
# #         return [int(x) for x in v.split(".")]
# #     return parse(v1) < parse(v2)


# # def default_data_dir() -> Path:
# #     return Path.home() / "Documents" / "BasiraData"


# # def open_native_folder_picker() -> str:
# #     selected = {"value": ""}

# #     def _pick():
# #         root = Tk()
# #         root.withdraw()
# #         root.attributes("-topmost", True)
# #         path = filedialog.askdirectory(title="اختيار مسار حفظ بيانات Basira")
# #         selected["value"] = path or ""
# #         root.destroy()

# #     t = threading.Thread(target=_pick)
# #     t.start()
# #     t.join()
# #     return selected["value"]


# # # ─── Config ───────────────────────────────────────────────────────────────────
# # def build_default_config(data_dir: str = "", user_id: str = "") -> dict:
# #     data_path = Path(data_dir) if data_dir else Path("")
# #     return {
# #         "app_version": APP_VERSION,
# #         "setup_completed": False,
# #         "setup_completed_at": None,
# #         "data_dir":    str(data_path) if data_dir else "",
# #         "models_dir":  str(data_path / "models")  if data_dir else "",
# #         "outputs_dir": str(data_path / "outputs") if data_dir else "",
# #         "assets_dir":  str(data_path / "assets")  if data_dir else "",
# #         "temp_dir":    str(data_path / "temp")    if data_dir else "",
# #         "local_api_url":  LOCAL_API_URL,
# #         "api_base_url":   CLOUD_API_BASE_URL,
# #         "user_id":     user_id,
# #         "last_login_at":      None,
# #         "last_activity_at":   None,
# #         "last_session_check": None,
# #         "subscription_status":    "unknown",
# #         "subscription_expires_at": None,
# #         "last_update_check": None,
# #         "update_status":     "unknown",
# #         "session": {
# #             "access_token":    "",
# #             "refresh_token":   "",
# #             "expires_at":      "",
# #             "is_authenticated": False
# #         },
# #         "model_registry": {
# #             "core_model_v1": {
# #                 "required":  True,
# #                 "installed": False,
# #                 "path":      "",
# #                 "version":   "1.0.0"
# #             }
# #         }
# #     }


# # # ─── Environment checks ───────────────────────────────────────────────────────
# # def validate_config(config: dict):
# #     if not isinstance(config, dict):
# #         return False, "Config is not a valid JSON object"
# #     required_keys = [
# #         "app_version", "setup_completed", "data_dir", "models_dir",
# #         "outputs_dir", "assets_dir", "local_api_url", "api_base_url",
# #         "user_id", "session", "model_registry"
# #     ]
# #     for key in required_keys:
# #         if key not in config:
# #             return False, f"Missing required config key: {key}"
# #     return True, "Config is valid"


# # def check_session(config: dict) -> dict:
# #     session = config.get("session", {})
# #     access_token     = session.get("access_token", "")
# #     expires_at       = session.get("expires_at", "")
# #     is_authenticated = session.get("is_authenticated", False)
# #     last_activity_at = config.get("last_activity_at", "")

# #     if not is_authenticated or not access_token or not expires_at:
# #         return {"valid": False, "reason": "missing_session"}

# #     try:
# #         expires_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
# #         if now_utc() >= expires_dt:
# #             return {"valid": False, "reason": "session_expired"}
# #     except Exception:
# #         return {"valid": False, "reason": "invalid_session_expiry"}

# #     if not last_activity_at:
# #         return {"valid": False, "reason": "missing_last_activity"}

# #     try:
# #         last_dt = datetime.fromisoformat(last_activity_at.replace("Z", "+00:00"))
# #         if now_utc() - last_dt > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
# #             return {"valid": False, "reason": "idle_timeout"}
# #     except Exception:
# #         return {"valid": False, "reason": "invalid_last_activity"}

# #     return {"valid": True, "reason": "session_valid"}


# # def check_subscription(config: dict) -> dict:
# #     status = config.get("subscription_status", "unknown")
# #     if status in ["active", "trialing"]:
# #         return {"valid": True, "reason": "subscription_active"}
# #     return {"valid": False, "reason": "subscription_inactive"}


# # def check_data_directory(config: dict) -> dict:
# #     data_dir = config.get("data_dir", "")
# #     if not data_dir:
# #         return {"valid": False, "reason": "data_dir_not_set"}
# #     path = Path(data_dir)
# #     if not path.exists():
# #         return {"valid": False, "reason": "data_dir_missing"}
# #     return {"valid": True, "reason": "data_dir_ok"}


# # def check_models(config: dict) -> dict:
# #     registry = config.get("model_registry", {})
# #     missing = [
# #         name for name, info in registry.items()
# #         if info.get("required") and not info.get("installed")
# #     ]
# #     if missing:
# #         return {"valid": False, "reason": "models_not_installed", "missing_models": missing}
# #     return {"valid": True, "reason": "models_ok"}


# # def check_update_status(config: dict) -> dict:
# #     current = config.get("app_version", APP_VERSION)
# #     if compare_versions(current, MANDATORY_UPDATE_VERSION):
# #         return {"status": "mandatory_update"}
# #     if compare_versions(current, LATEST_VERSION):
# #         return {"status": "optional_update"}
# #     return {"status": "up_to_date"}


# # def determine_user_state() -> dict:
# #     config = safe_read_json(CONFIG_PATH)

# #     if not config:
# #         return {"state": "new_user", "reason": "no_config"}

# #     valid, reason = validate_config(config)
# #     if not valid:
# #         return {"state": "new_user", "reason": reason}

# #     if not config.get("setup_completed", False):
# #         return {"state": "setup_incomplete", "reason": "setup_not_completed"}

# #     data_check = check_data_directory(config)
# #     if not data_check["valid"]:
# #         return {"state": "recovery_required", "reason": data_check["reason"]}

# #     model_check = check_models(config)
# #     if not model_check["valid"]:
# #         return {
# #             "state": "recovery_required",
# #             "reason": model_check["reason"],
# #             "missing_models": model_check.get("missing_models", [])
# #         }

# #     sub_check = check_subscription(config)
# #     if not sub_check["valid"]:
# #         return {"state": "subscription_required", "reason": sub_check["reason"]}

# #     session_check = check_session(config)
# #     if not session_check["valid"]:
# #         return {"state": "login_required", "reason": session_check["reason"]}

# #     update_check = check_update_status(config)
# #     if update_check["status"] == "mandatory_update":
# #         return {"state": "update_required", "reason": "mandatory_update"}
# #     if update_check["status"] == "optional_update":
# #         return {"state": "healthy_with_optional_update", "reason": "optional_update"}

# #     return {"state": "healthy", "reason": "app_healthy"}


# # # ─── Setup helpers ────────────────────────────────────────────────────────────
# # def create_data_structure(data_dir: str) -> dict:
# #     base = Path(data_dir)
# #     dirs = {
# #         "models_dir":  base / "models",
# #         "outputs_dir": base / "outputs",
# #         "assets_dir":  base / "assets",
# #         "temp_dir":    base / "temp",
# #     }
# #     base.mkdir(parents=True, exist_ok=True)
# #     for d in dirs.values():
# #         d.mkdir(parents=True, exist_ok=True)
# #     return {"data_dir": str(base), **{k: str(v) for k, v in dirs.items()}}


# # def install_demo_models(config: dict) -> dict:
# #     models_dir    = Path(config["models_dir"])
# #     core_model_dir = models_dir / "core_model_v1"
# #     core_model_dir.mkdir(parents=True, exist_ok=True)
# #     demo_file = core_model_dir / "model.ready"
# #     demo_file.write_text("Basira local model installed", encoding="utf-8")
# #     config["model_registry"]["core_model_v1"]["installed"] = True
# #     config["model_registry"]["core_model_v1"]["path"]      = str(demo_file)
# #     return config


# # def mark_activity(config: dict) -> dict:
# #     config["last_activity_at"]   = now_iso()
# #     config["last_session_check"] = now_iso()
# #     return config


# # def environment_self_check(config: dict) -> dict:
# #     results = {
# #         "config_valid": validate_config(config)[0],
# #         "data_dir":     check_data_directory(config),
# #         "models":       check_models(config),
# #         "session":      check_session(config),
# #         "update":       check_update_status(config),
# #     }
# #     all_good = (
# #         results["config_valid"]
# #         and results["data_dir"]["valid"]
# #         and results["models"]["valid"]
# #     )
# #     return {"ok": all_good, "results": results}


# # # ─── Routes ───────────────────────────────────────────────────────────────────
# # @app.route("/")
# # def root():
# #     return jsonify({"status": "ok", "service": "basira_local_bootstrap", "version": APP_VERSION})


# # @app.route("/health")
# # def health():
# #     return jsonify({"status": "ok", "app": APP_NAME, "version": APP_VERSION})


# # @app.route("/api/startup-status", methods=["GET"])
# # def startup_status():
# #     return jsonify(determine_user_state())


# # @app.route("/api/system/pick-data-dir", methods=["GET"])
# # def pick_data_dir():
# #     try:
# #         selected = open_native_folder_picker()
# #         return jsonify({"status": "ok", "path": selected})
# #     except Exception as e:
# #         return jsonify({"status": "error", "message": str(e)}), 500


# # @app.route("/api/setup/init", methods=["POST"])
# # def setup_init():
# #     ensure_base_dirs()
# #     if not CONFIG_PATH.exists():
# #         safe_write_json(CONFIG_PATH, build_default_config())
# #     return jsonify({"status": "ok", "message": "Setup initialized"})


# # @app.route("/api/setup/login-complete", methods=["POST"])
# # def setup_login_complete():
# #     payload = request.json or {}
# #     config  = safe_read_json(CONFIG_PATH) or build_default_config()

# #     config["user_id"]      = payload.get("user_id", "")
# #     config["last_login_at"] = now_iso()
# #     config["subscription_status"] = payload.get("subscription_status", "active")
# #     config["session"] = {
# #         "access_token":    payload.get("access_token", ""),
# #         "refresh_token":   payload.get("refresh_token", ""),
# #         "expires_at":      payload.get("expires_at", ""),
# #         "is_authenticated": True
# #     }
# #     config = mark_activity(config)
# #     safe_write_json(CONFIG_PATH, config)
# #     return jsonify({"status": "ok", "message": "Login linked to local app"})


# # @app.route("/api/setup/select-data-dir", methods=["POST"])
# # def setup_select_data_dir():
# #     payload  = request.json or {}
# #     data_dir = payload.get("data_dir", "").strip()
# #     if not data_dir:
# #         return jsonify({"status": "error", "message": "data_dir is required"}), 400
# #     try:
# #         created = create_data_structure(data_dir)
# #     except Exception as e:
# #         return jsonify({"status": "error", "message": str(e)}), 400

# #     config = safe_read_json(CONFIG_PATH) or build_default_config()
# #     config.update(created)
# #     safe_write_json(CONFIG_PATH, config)
# #     return jsonify({"status": "ok", "message": "Data directory configured", "paths": created})


# # @app.route("/api/setup/install-models", methods=["POST"])
# # def setup_install_models():
# #     config = safe_read_json(CONFIG_PATH)
# #     if not config:
# #         return jsonify({"status": "error", "message": "Missing config"}), 400
# #     config = install_demo_models(config)
# #     safe_write_json(CONFIG_PATH, config)
# #     return jsonify({"status": "ok", "message": "Models installed"})


# # @app.route("/api/setup/verify", methods=["GET"])
# # def setup_verify():
# #     config = safe_read_json(CONFIG_PATH)
# #     if not config:
# #         return jsonify({"status": "error", "message": "Config not found"}), 400
# #     result = environment_self_check(config)
# #     return jsonify({"status": "ok" if result["ok"] else "error", "verification": result})


# # @app.route("/api/setup/finalize", methods=["POST"])
# # def setup_finalize():
# #     config = safe_read_json(CONFIG_PATH)
# #     if not config:
# #         return jsonify({"status": "error", "message": "Config not found"}), 400
# #     config["setup_completed"]    = True
# #     config["setup_completed_at"] = now_iso()
# #     config = mark_activity(config)
# #     safe_write_json(CONFIG_PATH, config)
# #     return jsonify({"status": "ok", "message": "Setup completed"})


# # @app.route("/api/config", methods=["GET"])
# # def get_config():
# #     config = safe_read_json(CONFIG_PATH)
# #     if not config:
# #         return jsonify({"status": "error", "message": "Config not found"}), 404
# #     return jsonify(config)


# # @app.route("/api/session/refresh", methods=["POST"])
# # def session_refresh():
# #     payload = request.json or {}
# #     config  = safe_read_json(CONFIG_PATH)
# #     if not config:
# #         return jsonify({"status": "error", "message": "Config not found"}), 404

# #     config["session"]["access_token"]    = payload.get("access_token", "")
# #     config["session"]["refresh_token"]   = payload.get("refresh_token", "")
# #     config["session"]["expires_at"]      = payload.get("expires_at", "")
# #     config["session"]["is_authenticated"] = True
# #     config["subscription_status"]        = payload.get("subscription_status", "active")
# #     config["last_login_at"]              = now_iso()
# #     config = mark_activity(config)
# #     safe_write_json(CONFIG_PATH, config)
# #     return jsonify({"status": "ok", "message": "Session refreshed"})


# # @app.route("/api/auth/heartbeat", methods=["POST"])
# # def auth_heartbeat():
# #     config = safe_read_json(CONFIG_PATH)
# #     if not config:
# #         return jsonify({"status": "error", "message": "Config not found"}), 404

# #     session_check = check_session(config)
# #     if not session_check["valid"]:
# #         config["session"]["is_authenticated"] = False
# #         safe_write_json(CONFIG_PATH, config)
# #         return jsonify({"status": "expired", "reason": session_check["reason"]}), 401

# #     config = mark_activity(config)
# #     safe_write_json(CONFIG_PATH, config)
# #     return jsonify({"status": "ok", "message": "Heartbeat accepted"})


# # @app.route("/api/auth/auto-logout", methods=["POST"])
# # def auto_logout():
# #     config = safe_read_json(CONFIG_PATH)
# #     if not config:
# #         return jsonify({"status": "error", "message": "Config not found"}), 404
# #     config["session"]["is_authenticated"] = False
# #     config["session"]["access_token"]     = ""
# #     config["session"]["refresh_token"]    = ""
# #     config["session"]["expires_at"]       = ""
# #     config["last_activity_at"]            = now_iso()
# #     safe_write_json(CONFIG_PATH, config)
# #     return jsonify({"status": "ok", "message": "Logged out due to inactivity"})


# # @app.route("/api/recovery/repair-models", methods=["POST"])
# # def repair_models():
# #     config = safe_read_json(CONFIG_PATH)
# #     if not config:
# #         return jsonify({"status": "error", "message": "Config not found"}), 404
# #     config = install_demo_models(config)
# #     safe_write_json(CONFIG_PATH, config)
# #     return jsonify({"status": "ok", "message": "Models repaired"})


# # @app.route("/api/recovery/reselect-data-dir", methods=["POST"])
# # def recovery_reselect_data_dir():
# #     payload  = request.json or {}
# #     data_dir = payload.get("data_dir", "").strip()
# #     if not data_dir:
# #         return jsonify({"status": "error", "message": "data_dir is required"}), 400
# #     try:
# #         created = create_data_structure(data_dir)
# #     except Exception as e:
# #         return jsonify({"status": "error", "message": str(e)}), 400

# #     config = safe_read_json(CONFIG_PATH) or build_default_config()
# #     config.update(created)
# #     safe_write_json(CONFIG_PATH, config)
# #     return jsonify({"status": "ok", "message": "Data directory updated", "paths": created})


# # @app.route("/api/subscription/renew-demo", methods=["POST"])
# # def renew_demo():
# #     config = safe_read_json(CONFIG_PATH)
# #     if not config:
# #         return jsonify({"status": "error", "message": "Config not found"}), 404
# #     config["subscription_status"] = "active"
# #     safe_write_json(CONFIG_PATH, config)
# #     return jsonify({"status": "ok", "message": "Subscription renewed (demo)"})


# # # ─── Main ─────────────────────────────────────────────────────────────────────
# # if __name__ == "__main__":
# #     ensure_base_dirs()
# #     print(f"[bootstrap] Basira Bootstrap API → http://127.0.0.1:{LOCAL_API_PORT}")
# #     app.run(host="127.0.0.1", port=LOCAL_API_PORT, debug=False)

# # packaging/basira_local_bootstrap.py
# """
# Basira Bootstrap API  —  http://127.0.0.1:5001
# ================================================
# Started automatically by launcher.py.
# The cloud page (local-setup.html) talks to this API.

# FIRST-TIME SETUP (what this file does for a new user):
#   1.  POST /api/setup/init
#         → creates config.json in %LOCALAPPDATA%\\Basira\\

#   2.  POST /api/setup/login-complete
#         → stores Supabase session tokens in config + session.json

#   3.  POST /api/setup/select-data-dir   { data_dir: "D:\\BasiraData" }
#         → creates the directory tree in the user's chosen folder:
#             D:\\BasiraData\\
#                 input_files\\    output_files\\   models\\
#                 assets\\         audit\\          reports\\
#                 temp\\           exports\\

#   4.  POST /api/setup/download-files
#         → downloads files FROM GITHUB (via Cloudflare Worker) into data_dir:
#             D:\\BasiraData\\models\\core_model_v1\\   (AI models)
#             (basira_app.html ships with the repo — no download needed)

#   5.  POST /api/setup/finalize
#         → marks setup_completed = True, saves data_dir to config permanently

#   6.  Browser opens http://127.0.0.1:5000
#         → Basira_app_structure.py serves basira_app.html from templates/
#         → User uploads CSV → gets XAI / RCA / chart analysis

# RETURNING USER:
#   Bootstrap checks config → all ok → state = "healthy"
#   Browser goes straight to 127.0.0.1:5000 → analysis UI

# CLOUDFLARE WORKER ROUTES NEEDED:
#   Your Worker (basira.basira-toolmodel.workers.dev) must expose:
#     GET /download/models.zip  → proxies GitHub release zip
#   You configure the GitHub repo/release URL inside the Worker.
# """

# import json
# import os
# import threading
# import urllib.request
# import zipfile
# from pathlib import Path
# from datetime import datetime, timezone, timedelta
# from tkinter import Tk, filedialog

# from flask import Flask, jsonify, request
# from flask_cors import CORS

# import basira_paths as paths
# import basira_session as session_mgr

# # ─── App ──────────────────────────────────────────────────────────────────────
# app = Flask(__name__)
# CORS(app)

# APP_NAME       = "Basira"
# APP_VERSION    = "1.0.0"
# LOCAL_API_PORT = 5001

# CLOUD_BASE_URL    = "https://basira.basira-toolmodel.workers.dev"
# CLOUD_RENEW_URL   = f"{CLOUD_BASE_URL}/renew"
# DOWNLOAD_MODELS_URL = f"{CLOUD_BASE_URL}/download/models.zip"

# LATEST_VERSION           = "1.0.0"
# MANDATORY_UPDATE_VERSION = "0.9.0"
# SESSION_TIMEOUT_MINUTES  = 20

# CONFIG_PATH  = paths.get_config_path()
# SESSION_PATH = paths.get_session_path()
# APPDATA_DIR  = paths.get_appdata_dir()
# TEMPLATES_DIR = paths.get_templates_dir()


# # ─── Helpers ──────────────────────────────────────────────────────────────────
# def now_utc(): return datetime.now(timezone.utc)
# def now_iso(): return now_utc().isoformat()

# def safe_read(path: Path):
#     if not path.exists(): return None
#     try: return json.loads(path.read_text(encoding="utf-8"))
#     except: return None

# def safe_write(path: Path, data: dict):
#     path.parent.mkdir(parents=True, exist_ok=True)
#     path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# def compare_ver(v1, v2):
#     return [int(x) for x in v1.split(".")] < [int(x) for x in v2.split(".")]

# def open_folder_picker() -> str:
#     result = {"v": ""}
#     def _run():
#         root = Tk(); root.withdraw(); root.attributes("-topmost", True)
#         result["v"] = filedialog.askdirectory(title="اختيار مجلد حفظ ملفات بصيرة") or ""
#         root.destroy()
#     t = threading.Thread(target=_run); t.start(); t.join()
#     return result["v"]


# # ─── Config builder ───────────────────────────────────────────────────────────
# def build_default_config(data_dir="", user_id="") -> dict:
#     dp = Path(data_dir) if data_dir else Path("")
#     mk = lambda *parts: str(dp.joinpath(*parts)) if data_dir else ""
#     return {
#         "app_version":         APP_VERSION,
#         "setup_completed":     False,
#         "setup_completed_at":  None,
#         "data_dir":            str(dp) if data_dir else "",
#         "models_dir":          mk("models"),
#         "outputs_dir":         mk("output_files"),
#         "assets_dir":          mk("assets"),
#         "temp_dir":            mk("temp"),
#         "local_api_url":       f"http://127.0.0.1:{LOCAL_API_PORT}",
#         "api_base_url":        CLOUD_BASE_URL,
#         "user_id":             user_id,
#         "last_login_at":       None,
#         "last_activity_at":    None,
#         "subscription_status": "unknown",
#         "session": {
#             "access_token": "", "refresh_token": "",
#             "expires_at": "", "is_authenticated": False,
#         },
#         "model_registry": {
#             "core_model_v1": {
#                 "required": True, "installed": False,
#                 "path": "", "version": "1.0.0",
#             }
#         },
#     }


# # ─── State checks ─────────────────────────────────────────────────────────────
# def validate_config(cfg) -> tuple:
#     if not isinstance(cfg, dict): return False, "not a dict"
#     for k in ["app_version","setup_completed","data_dir",
#                "local_api_url","user_id","session","model_registry"]:
#         if k not in cfg: return False, f"missing: {k}"
#     return True, "ok"

# def check_session(cfg) -> dict:
#     s = cfg.get("session", {})
#     if not s.get("is_authenticated") or not s.get("access_token"):
#         return {"valid": False, "reason": "missing_session"}
#     exp = s.get("expires_at", "")
#     if exp:
#         try:
#             if now_utc() >= datetime.fromisoformat(exp.replace("Z","+00:00")):
#                 return {"valid": False, "reason": "session_expired"}
#         except: return {"valid": False, "reason": "invalid_expiry"}
#     last = cfg.get("last_activity_at","")
#     if last:
#         try:
#             if now_utc() - datetime.fromisoformat(last.replace("Z","+00:00")) \
#                     > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
#                 return {"valid": False, "reason": "idle_timeout"}
#         except: pass
#     return {"valid": True, "reason": "ok"}

# def check_subscription(cfg) -> dict:
#     return ({"valid": True} if cfg.get("subscription_status") in ["active","trialing"]
#             else {"valid": False, "reason": "subscription_inactive"})

# def check_data_dir(cfg) -> dict:
#     d = cfg.get("data_dir","")
#     if not d: return {"valid": False, "reason": "data_dir_not_set"}
#     if not Path(d).exists(): return {"valid": False, "reason": "data_dir_missing"}
#     return {"valid": True}

# def check_models(cfg) -> dict:
#     reg = cfg.get("model_registry", {})
#     missing = [n for n,info in reg.items() if info.get("required") and not info.get("installed")]
#     if missing: return {"valid": False, "reason": "models_not_installed", "missing": missing}
#     # Verify the actual marker file exists
#     models_dir = cfg.get("models_dir","")
#     if models_dir:
#         marker = Path(models_dir) / "core_model_v1" / "model.ready"
#         if not marker.exists():
#             return {"valid": False, "reason": "models_not_installed", "missing": ["core_model_v1"]}
#     return {"valid": True}

# def check_update(cfg) -> dict:
#     v = cfg.get("app_version", APP_VERSION)
#     if compare_ver(v, MANDATORY_UPDATE_VERSION): return {"status": "mandatory_update"}
#     if compare_ver(v, LATEST_VERSION): return {"status": "optional_update"}
#     return {"status": "up_to_date"}

# def determine_state() -> dict:
#     cfg = safe_read(CONFIG_PATH)
#     if not cfg: return {"state": "new_user", "reason": "no_config"}
#     ok, reason = validate_config(cfg)
#     if not ok: return {"state": "new_user", "reason": reason}
#     if not cfg.get("setup_completed"):
#         return {"state": "setup_incomplete", "reason": "setup_not_completed"}
#     for fn, fail in [(check_data_dir,"recovery_required"),
#                      (check_models,"recovery_required"),
#                      (check_subscription,"subscription_required")]:
#         r = fn(cfg)
#         if not r["valid"]:
#             out = {"state": fail, "reason": r.get("reason","")}
#             if "missing" in r: out["missing"] = r["missing"]
#             return out
#     sc = check_session(cfg)
#     if not sc["valid"]: return {"state": "login_required", "reason": sc["reason"]}
#     upd = check_update(cfg)
#     if upd["status"] == "mandatory_update": return {"state": "update_required"}
#     if upd["status"] == "optional_update": return {"state": "healthy_with_optional_update"}
#     return {"state": "healthy"}


# # ─── Setup helpers ────────────────────────────────────────────────────────────
# def create_dirs(data_dir: str) -> dict:
#     base = Path(data_dir)
#     paths.ensure_user_data_tree(base)
#     return {
#         "data_dir":    str(base),
#         "models_dir":  str(base / "models"),
#         "outputs_dir": str(base / "output_files"),
#         "assets_dir":  str(base / "assets"),
#         "temp_dir":    str(base / "temp"),
#     }

# def do_download_files(cfg: dict) -> dict:
#     """
#     Download model files from GitHub via the Cloudflare Worker.

#     Your Cloudflare Worker at basira.basira-toolmodel.workers.dev
#     must have a route:
#       GET /download/models.zip
#     that fetches the models zip from your GitHub repo/release and
#     streams it back to the caller.

#     The zip should contain a folder: core_model_v1/
#     with the model files inside it.

#     On success: extracts to <data_dir>/models/core_model_v1/
#     On failure: writes a placeholder model.ready marker so the
#                 system still reaches "healthy" state during dev.
#     """
#     data_dir   = Path(cfg["data_dir"])
#     models_dir = Path(cfg["models_dir"])
#     models_dir.mkdir(parents=True, exist_ok=True)

#     downloaded = []
#     warnings   = []

#     # Download and extract models zip
#     zip_path = models_dir / "_download_tmp.zip"
#     try:
#         urllib.request.urlretrieve(DOWNLOAD_MODELS_URL, str(zip_path))
#         with zipfile.ZipFile(str(zip_path), "r") as z:
#             z.extractall(str(models_dir))
#         zip_path.unlink(missing_ok=True)

#         cfg["model_registry"]["core_model_v1"]["installed"] = True
#         cfg["model_registry"]["core_model_v1"]["path"] = str(models_dir / "core_model_v1")
#         downloaded.append("models/core_model_v1")

#     except Exception as e:
#         # DEV FALLBACK: write placeholder so setup can complete
#         # Remove this block when real models are hosted
#         core_dir = models_dir / "core_model_v1"
#         core_dir.mkdir(parents=True, exist_ok=True)
#         (core_dir / "model.ready").write_text(
#             "placeholder — connect real model URL at DOWNLOAD_MODELS_URL", encoding="utf-8")
#         cfg["model_registry"]["core_model_v1"]["installed"] = True
#         cfg["model_registry"]["core_model_v1"]["path"] = str(core_dir)
#         downloaded.append("models/core_model_v1 (placeholder)")
#         warnings.append(f"models.zip download failed: {e}. Placeholder used.")

#     return {"ok": True, "downloaded": downloaded, "warnings": warnings, "config": cfg}

# def mark_activity(cfg: dict) -> dict:
#     cfg["last_activity_at"] = now_iso()
#     return cfg


# # ─── Routes ───────────────────────────────────────────────────────────────────
# @app.route("/")
# def root():
#     return jsonify({"status":"ok","service":"basira_bootstrap","version":APP_VERSION})

# @app.route("/health")
# def health():
#     return jsonify({"status":"ok","version":APP_VERSION})

# @app.route("/api/startup-status")
# def startup_status():
#     return jsonify(determine_state())

# @app.route("/api/system/pick-data-dir")
# def pick_data_dir():
#     try:
#         p = open_folder_picker()
#         return jsonify({"status":"ok","path":p})
#     except Exception as e:
#         return jsonify({"status":"error","message":str(e)}), 500

# # ── Setup flow routes ─────────────────────────────────────────────────────────

# @app.route("/api/setup/init", methods=["POST"])
# def setup_init():
#     """Step 0: create config.json in AppData if missing."""
#     APPDATA_DIR.mkdir(parents=True, exist_ok=True)
#     if not CONFIG_PATH.exists():
#         safe_write(CONFIG_PATH, build_default_config())
#     return jsonify({"status":"ok","message":"initialized"})

# @app.route("/api/setup/login-complete", methods=["POST"])
# def setup_login_complete():
#     """Step 1: save Supabase session tokens after user logs in on cloud."""
#     p   = request.json or {}
#     cfg = safe_read(CONFIG_PATH) or build_default_config()
#     cfg["user_id"]             = p.get("user_id","")
#     cfg["last_login_at"]       = now_iso()
#     cfg["subscription_status"] = p.get("subscription_status","active")
#     cfg["session"] = {
#         "access_token":     p.get("access_token",""),
#         "refresh_token":    p.get("refresh_token",""),
#         "expires_at":       p.get("expires_at",""),
#         "is_authenticated": True,
#     }
#     cfg = mark_activity(cfg)
#     safe_write(CONFIG_PATH, cfg)
#     session_mgr.create_local_session(
#         SESSION_PATH,
#         user_id=cfg["user_id"],
#         access_token=cfg["session"]["access_token"],
#         refresh_token=cfg["session"]["refresh_token"],
#         subscription_status=cfg["subscription_status"],
#     )
#     return jsonify({"status":"ok","message":"login linked"})

# @app.route("/api/setup/select-data-dir", methods=["POST"])
# def setup_select_data_dir():
#     """Step 2: user picks folder → create directory tree there."""
#     data_dir = (request.json or {}).get("data_dir","").strip()
#     if not data_dir:
#         return jsonify({"status":"error","message":"data_dir required"}), 400
#     try:
#         created = create_dirs(data_dir)
#     except Exception as e:
#         return jsonify({"status":"error","message":str(e)}), 400
#     cfg = safe_read(CONFIG_PATH) or build_default_config()
#     cfg.update(created)
#     safe_write(CONFIG_PATH, cfg)
#     return jsonify({"status":"ok","message":"folders created","paths":created})

# @app.route("/api/setup/download-files", methods=["POST"])
# def setup_download_files():
#     """
#     Step 3: download model files from GitHub via Cloudflare Worker.
#     This is the only network download in the setup flow.
#     basira_app.html is already in packaging/templates/ (ships with repo).
#     """
#     cfg = safe_read(CONFIG_PATH)
#     if not cfg:
#         return jsonify({"status":"error","message":"run /api/setup/init first"}), 400
#     if not cfg.get("data_dir"):
#         return jsonify({"status":"error","message":"run /api/setup/select-data-dir first"}), 400

#     result = do_download_files(cfg)
#     safe_write(CONFIG_PATH, result["config"])

#     return jsonify({
#         "status":     "ok",
#         "downloaded": result["downloaded"],
#         "warnings":   result["warnings"],
#     })

# @app.route("/api/setup/verify")
# def setup_verify():
#     """Step 4: verify all required files and config are in place."""
#     cfg = safe_read(CONFIG_PATH)
#     if not cfg:
#         return jsonify({"status":"error","verification":{"ok":False}}), 400
#     checks = {
#         "config":   validate_config(cfg)[0],
#         "data_dir": check_data_dir(cfg),
#         "models":   check_models(cfg),
#         "session":  check_session(cfg),
#     }
#     ok = checks["config"] and checks["data_dir"]["valid"] and checks["models"]["valid"]
#     return jsonify({"status":"ok" if ok else "error","verification":checks})

# @app.route("/api/setup/finalize", methods=["POST"])
# def setup_finalize():
#     """Step 5: mark setup complete. Saves chosen data_dir permanently."""
#     cfg = safe_read(CONFIG_PATH)
#     if not cfg:
#         return jsonify({"status":"error","message":"no config"}), 400
#     cfg["setup_completed"]    = True
#     cfg["setup_completed_at"] = now_iso()
#     cfg = mark_activity(cfg)
#     safe_write(CONFIG_PATH, cfg)
#     return jsonify({"status":"ok","message":"setup complete","data_dir":cfg.get("data_dir","")})

# # ── Runtime routes ────────────────────────────────────────────────────────────

# @app.route("/api/config")
# def get_config():
#     cfg = safe_read(CONFIG_PATH)
#     if not cfg: return jsonify({"status":"error"}), 404
#     return jsonify(cfg)

# @app.route("/api/session/refresh", methods=["POST"])
# def session_refresh():
#     p   = request.json or {}
#     cfg = safe_read(CONFIG_PATH)
#     if not cfg: return jsonify({"status":"error"}), 404
#     cfg["session"].update({
#         "access_token":     p.get("access_token",""),
#         "refresh_token":    p.get("refresh_token",""),
#         "expires_at":       p.get("expires_at",""),
#         "is_authenticated": True,
#     })
#     cfg["subscription_status"] = p.get("subscription_status","active")
#     cfg["last_login_at"]       = now_iso()
#     cfg = mark_activity(cfg)
#     safe_write(CONFIG_PATH, cfg)
#     session_mgr.update_last_activity(SESSION_PATH)
#     return jsonify({"status":"ok"})

# @app.route("/api/auth/heartbeat", methods=["POST"])
# def auth_heartbeat():
#     cfg = safe_read(CONFIG_PATH)
#     if not cfg: return jsonify({"status":"error"}), 404
#     chk = check_session(cfg)
#     if not chk["valid"]:
#         cfg["session"]["is_authenticated"] = False
#         safe_write(CONFIG_PATH, cfg)
#         return jsonify({"status":"expired","reason":chk["reason"]}), 401
#     cfg = mark_activity(cfg)
#     safe_write(CONFIG_PATH, cfg)
#     session_mgr.update_last_activity(SESSION_PATH)
#     return jsonify({"status":"ok"})

# @app.route("/api/auth/auto-logout", methods=["POST"])
# def auto_logout():
#     cfg = safe_read(CONFIG_PATH)
#     if cfg:
#         cfg["session"]["is_authenticated"] = False
#         cfg["session"]["access_token"]     = ""
#         cfg = mark_activity(cfg)
#         safe_write(CONFIG_PATH, cfg)
#     session_mgr.clear_local_session(SESSION_PATH)
#     return jsonify({"status":"ok"})

# @app.route("/api/recovery/repair-files", methods=["POST"])
# def repair_files():
#     """Re-download model files when something is missing."""
#     cfg = safe_read(CONFIG_PATH)
#     if not cfg: return jsonify({"status":"error"}), 404
#     result = do_download_files(cfg)
#     safe_write(CONFIG_PATH, result["config"])
#     if result["ok"]:
#         return jsonify({"status":"ok","downloaded":result["downloaded"],"warnings":result["warnings"]})
#     return jsonify({"status":"error","errors":result.get("errors",[])}), 500

# @app.route("/api/recovery/reselect-data-dir", methods=["POST"])
# def recovery_reselect():
#     data_dir = (request.json or {}).get("data_dir","").strip()
#     if not data_dir: return jsonify({"status":"error","message":"data_dir required"}), 400
#     try: created = create_dirs(data_dir)
#     except Exception as e: return jsonify({"status":"error","message":str(e)}), 400
#     cfg = safe_read(CONFIG_PATH) or build_default_config()
#     cfg.update(created)
#     safe_write(CONFIG_PATH, cfg)
#     return jsonify({"status":"ok","paths":created})

# @app.route("/api/subscription/renew-demo", methods=["POST"])
# def renew_demo():
#     cfg = safe_read(CONFIG_PATH)
#     if not cfg: return jsonify({"status":"error"}), 404
#     cfg["subscription_status"] = "active"
#     safe_write(CONFIG_PATH, cfg)
#     return jsonify({"status":"ok","message":"subscription renewed (demo)"})


# # ─── Main ─────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     APPDATA_DIR.mkdir(parents=True, exist_ok=True)
#     print(f"\n[bootstrap] Running at http://127.0.0.1:{LOCAL_API_PORT}\n")
#     app.run(host="127.0.0.1", port=LOCAL_API_PORT, debug=False)
# packaging/basira_local_bootstrap.py
"""
Basira Bootstrap API  —  http://127.0.0.1:5001
================================================
Started automatically by launcher.py.
The cloud page (local-setup.html) talks to this API.

FIRST-TIME SETUP (what this file does for a new user):
  1.  POST /api/setup/init
        → creates config.json in %LOCALAPPDATA%\\Basira\\

  2.  POST /api/setup/login-complete
        → stores Supabase session tokens in config + session.json

  3.  POST /api/setup/select-data-dir   { data_dir: "D:\\BasiraData" }
        → creates the directory tree in the user's chosen folder:
            D:\\BasiraData\\
                input_files\\    output_files\\   models\\
                assets\\         audit\\          reports\\
                temp\\           exports\\

  4.  POST /api/setup/download-files
        → downloads files FROM GITHUB (via Cloudflare Worker) into data_dir:
            D:\\BasiraData\\models\\core_model_v1\\   (AI models)
            (basira_app.html ships with the repo — no download needed)

  5.  POST /api/setup/finalize
        → marks setup_completed = True, saves data_dir to config permanently

  6.  Browser opens http://127.0.0.1:5000
        → Basira_app_structure.py serves basira_app.html from templates/
        → User uploads CSV → gets XAI / RCA / chart analysis

RETURNING USER:
  Bootstrap checks config → all ok → state = "healthy"
  Browser goes straight to 127.0.0.1:5000 → analysis UI

CLOUDFLARE WORKER ROUTES NEEDED:
  Your Worker (basira.basira-toolmodel.workers.dev) must expose:
    GET /download/models.zip  → proxies GitHub release zip
  You configure the GitHub repo/release URL inside the Worker.
"""

import json
import os
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

# ─── App ──────────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

APP_NAME       = "Basira"
APP_VERSION    = "1.0.0"
LOCAL_API_PORT = 5001

CLOUD_BASE_URL    = "https://basira.basira-toolmodel.workers.dev"
CLOUD_RENEW_URL   = f"{CLOUD_BASE_URL}/renew"
DOWNLOAD_MODELS_URL = f"{CLOUD_BASE_URL}/download/models.zip"

LATEST_VERSION           = "1.0.0"
MANDATORY_UPDATE_VERSION = "0.9.0"
SESSION_TIMEOUT_MINUTES  = 20

CONFIG_PATH  = paths.get_config_path()
SESSION_PATH = paths.get_session_path()
APPDATA_DIR  = paths.get_appdata_dir()
TEMPLATES_DIR = paths.get_templates_dir()


# ─── Helpers ──────────────────────────────────────────────────────────────────
def now_utc(): return datetime.now(timezone.utc)
def now_iso(): return now_utc().isoformat()

def safe_read(path: Path):
    if not path.exists(): return None
    try: return json.loads(path.read_text(encoding="utf-8"))
    except: return None

def safe_write(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def compare_ver(v1, v2):
    return [int(x) for x in v1.split(".")] < [int(x) for x in v2.split(".")]

def open_folder_picker() -> str:
    result = {"v": ""}
    def _run():
        root = Tk(); root.withdraw(); root.attributes("-topmost", True)
        result["v"] = filedialog.askdirectory(title="اختيار مجلد حفظ ملفات بصيرة") or ""
        root.destroy()
    t = threading.Thread(target=_run); t.start(); t.join()
    return result["v"]


# ─── Config builder ───────────────────────────────────────────────────────────
def build_default_config(data_dir="", user_id="") -> dict:
    dp = Path(data_dir) if data_dir else Path("")
    mk = lambda *parts: str(dp.joinpath(*parts)) if data_dir else ""
    return {
        "app_version":         APP_VERSION,
        "setup_completed":     False,
        "setup_completed_at":  None,
        "data_dir":            str(dp) if data_dir else "",
        "models_dir":          mk("models"),
        "outputs_dir":         mk("output_files"),
        "assets_dir":          mk("assets"),
        "temp_dir":            mk("temp"),
        "local_api_url":       f"http://127.0.0.1:{LOCAL_API_PORT}",
        "api_base_url":        CLOUD_BASE_URL,
        "user_id":             user_id,
        "last_login_at":       None,
        "last_activity_at":    None,
        "subscription_status": "unknown",
        "session": {
            "access_token": "", "refresh_token": "",
            "expires_at": "", "is_authenticated": False,
        },
        "model_registry": {
            "core_model_v1": {
                "required": True, "installed": False,
                "path": "", "version": "1.0.0",
            }
        },
    }


# ─── State checks ─────────────────────────────────────────────────────────────
def validate_config(cfg) -> tuple:
    if not isinstance(cfg, dict): return False, "not a dict"
    for k in ["app_version","setup_completed","data_dir",
               "local_api_url","user_id","session","model_registry"]:
        if k not in cfg: return False, f"missing: {k}"
    return True, "ok"

def check_session(cfg) -> dict:
    s = cfg.get("session", {})
    if not s.get("is_authenticated") or not s.get("access_token"):
        return {"valid": False, "reason": "missing_session"}
    exp = s.get("expires_at", "")
    if exp:
        try:
            if now_utc() >= datetime.fromisoformat(exp.replace("Z","+00:00")):
                return {"valid": False, "reason": "session_expired"}
        except: return {"valid": False, "reason": "invalid_expiry"}
    last = cfg.get("last_activity_at","")
    if last:
        try:
            if now_utc() - datetime.fromisoformat(last.replace("Z","+00:00")) \
                    > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                return {"valid": False, "reason": "idle_timeout"}
        except: pass
    return {"valid": True, "reason": "ok"}

def check_subscription(cfg) -> dict:
    return ({"valid": True} if cfg.get("subscription_status") in ["active","trialing"]
            else {"valid": False, "reason": "subscription_inactive"})

def check_data_dir(cfg) -> dict:
    d = cfg.get("data_dir","")
    if not d: return {"valid": False, "reason": "data_dir_not_set"}
    if not Path(d).exists(): return {"valid": False, "reason": "data_dir_missing"}
    return {"valid": True}

def check_models(cfg) -> dict:
    reg = cfg.get("model_registry", {})
    missing = [n for n,info in reg.items() if info.get("required") and not info.get("installed")]
    if missing: return {"valid": False, "reason": "models_not_installed", "missing": missing}
    # Verify the actual marker file exists
    models_dir = cfg.get("models_dir","")
    if models_dir:
        marker = Path(models_dir) / "core_model_v1" / "model.ready"
        if not marker.exists():
            return {"valid": False, "reason": "models_not_installed", "missing": ["core_model_v1"]}
    return {"valid": True}

def check_update(cfg) -> dict:
    v = cfg.get("app_version", APP_VERSION)
    if compare_ver(v, MANDATORY_UPDATE_VERSION): return {"status": "mandatory_update"}
    if compare_ver(v, LATEST_VERSION): return {"status": "optional_update"}
    return {"status": "up_to_date"}

def determine_state() -> dict:
    cfg = safe_read(CONFIG_PATH)
    if not cfg: return {"state": "new_user", "reason": "no_config"}
    ok, reason = validate_config(cfg)
    if not ok: return {"state": "new_user", "reason": reason}
    if not cfg.get("setup_completed"):
        return {"state": "setup_incomplete", "reason": "setup_not_completed"}
    for fn, fail in [(check_data_dir,"recovery_required"),
                     (check_models,"recovery_required"),
                     (check_subscription,"subscription_required")]:
        r = fn(cfg)
        if not r["valid"]:
            out = {"state": fail, "reason": r.get("reason","")}
            if "missing" in r: out["missing"] = r["missing"]
            return out
    sc = check_session(cfg)
    if not sc["valid"]: return {"state": "login_required", "reason": sc["reason"]}
    upd = check_update(cfg)
    if upd["status"] == "mandatory_update": return {"state": "update_required"}
    if upd["status"] == "optional_update": return {"state": "healthy_with_optional_update"}
    return {"state": "healthy"}


# ─── Setup helpers ────────────────────────────────────────────────────────────
def create_dirs(data_dir: str) -> dict:
    base = Path(data_dir)
    paths.ensure_user_data_tree(base)
    return {
        "data_dir":    str(base),
        "models_dir":  str(base / "models"),
        "outputs_dir": str(base / "output_files"),
        "assets_dir":  str(base / "assets"),
        "temp_dir":    str(base / "temp"),
    }

def do_download_files(cfg: dict) -> dict:
    """
    Download model files from GitHub via the Cloudflare Worker.

    Your Cloudflare Worker at basira.basira-toolmodel.workers.dev
    must have a route:
      GET /download/models.zip
    that fetches the models zip from your GitHub repo/release and
    streams it back to the caller.

    The zip should contain a folder: core_model_v1/
    with the model files inside it.

    On success: extracts to <data_dir>/models/core_model_v1/
    On failure: writes a placeholder model.ready marker so the
                system still reaches "healthy" state during dev.
    """
    data_dir   = Path(cfg["data_dir"])
    models_dir = Path(cfg["models_dir"])
    models_dir.mkdir(parents=True, exist_ok=True)

    downloaded = []
    warnings   = []

    # Download and extract models zip
    zip_path = models_dir / "_download_tmp.zip"
    try:
        urllib.request.urlretrieve(DOWNLOAD_MODELS_URL, str(zip_path))
        with zipfile.ZipFile(str(zip_path), "r") as z:
            z.extractall(str(models_dir))
        zip_path.unlink(missing_ok=True)

        cfg["model_registry"]["core_model_v1"]["installed"] = True
        cfg["model_registry"]["core_model_v1"]["path"] = str(models_dir / "core_model_v1")
        downloaded.append("models/core_model_v1")

    except Exception as e:
        # DEV FALLBACK: write placeholder so setup can complete
        # Remove this block when real models are hosted
        core_dir = models_dir / "core_model_v1"
        core_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "model.ready").write_text(
            "placeholder — connect real model URL at DOWNLOAD_MODELS_URL", encoding="utf-8")
        cfg["model_registry"]["core_model_v1"]["installed"] = True
        cfg["model_registry"]["core_model_v1"]["path"] = str(core_dir)
        downloaded.append("models/core_model_v1 (placeholder)")
        warnings.append(f"models.zip download failed: {e}. Placeholder used.")

    return {"ok": True, "downloaded": downloaded, "warnings": warnings, "config": cfg}

def mark_activity(cfg: dict) -> dict:
    cfg["last_activity_at"] = now_iso()
    return cfg


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def root():
    return jsonify({"status":"ok","service":"basira_bootstrap","version":APP_VERSION})

@app.route("/health")
def health():
    return jsonify({"status":"ok","version":APP_VERSION})

@app.route("/api/startup-status")
def startup_status():
    return jsonify(determine_state())

@app.route("/api/system/pick-data-dir")
def pick_data_dir():
    try:
        p = open_folder_picker()
        return jsonify({"status":"ok","path":p})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

# ── Setup flow routes ─────────────────────────────────────────────────────────

@app.route("/api/setup/init", methods=["POST"])
def setup_init():
    """Step 0: create config.json in AppData if missing."""
    APPDATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        safe_write(CONFIG_PATH, build_default_config())
    return jsonify({"status":"ok","message":"initialized"})

@app.route("/api/setup/login-complete", methods=["POST"])
def setup_login_complete():
    """Step 1: save Supabase session tokens after user logs in on cloud."""
    p   = request.json or {}
    cfg = safe_read(CONFIG_PATH) or build_default_config()
    cfg["user_id"]             = p.get("user_id","")
    cfg["last_login_at"]       = now_iso()
    cfg["subscription_status"] = p.get("subscription_status","active")
    cfg["session"] = {
        "access_token":     p.get("access_token",""),
        "refresh_token":    p.get("refresh_token",""),
        "expires_at":       p.get("expires_at",""),
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
    return jsonify({"status":"ok","message":"login linked"})

@app.route("/api/setup/select-data-dir", methods=["POST"])
def setup_select_data_dir():
    """Step 2: user picks folder → create directory tree there."""
    data_dir = (request.json or {}).get("data_dir","").strip()
    if not data_dir:
        return jsonify({"status":"error","message":"data_dir required"}), 400
    try:
        created = create_dirs(data_dir)
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 400
    cfg = safe_read(CONFIG_PATH) or build_default_config()
    cfg.update(created)
    safe_write(CONFIG_PATH, cfg)
    return jsonify({"status":"ok","message":"folders created","paths":created})

@app.route("/api/setup/download-files", methods=["POST"])
def setup_download_files():
    """
    Step 3: download model files from GitHub via Cloudflare Worker.
    This is the only network download in the setup flow.
    basira_app.html is already in packaging/templates/ (ships with repo).
    """
    cfg = safe_read(CONFIG_PATH)
    if not cfg:
        return jsonify({"status":"error","message":"run /api/setup/init first"}), 400
    if not cfg.get("data_dir"):
        return jsonify({"status":"error","message":"run /api/setup/select-data-dir first"}), 400

    result = do_download_files(cfg)
    safe_write(CONFIG_PATH, result["config"])

    return jsonify({
        "status":     "ok",
        "downloaded": result["downloaded"],
        "warnings":   result["warnings"],
    })

@app.route("/api/setup/verify")
def setup_verify():
    """Step 4: verify all required files and config are in place."""
    cfg = safe_read(CONFIG_PATH)
    if not cfg:
        return jsonify({"status":"error","verification":{"ok":False}}), 400
    checks = {
        "config":   validate_config(cfg)[0],
        "data_dir": check_data_dir(cfg),
        "models":   check_models(cfg),
        "session":  check_session(cfg),
    }
    ok = checks["config"] and checks["data_dir"]["valid"] and checks["models"]["valid"]
    return jsonify({"status":"ok" if ok else "error","verification":checks})

@app.route("/api/setup/finalize", methods=["POST"])
def setup_finalize():
    """Step 5: mark setup complete. Saves chosen data_dir permanently."""
    cfg = safe_read(CONFIG_PATH)
    if not cfg:
        return jsonify({"status":"error","message":"no config"}), 400
    cfg["setup_completed"]    = True
    cfg["setup_completed_at"] = now_iso()
    cfg = mark_activity(cfg)
    safe_write(CONFIG_PATH, cfg)
    return jsonify({"status":"ok","message":"setup complete","data_dir":cfg.get("data_dir","")})

# ── Runtime routes ────────────────────────────────────────────────────────────

@app.route("/api/config")
def get_config():
    cfg = safe_read(CONFIG_PATH)
    if not cfg: return jsonify({"status":"error"}), 404
    return jsonify(cfg)

@app.route("/api/session/refresh", methods=["POST"])
def session_refresh():
    p   = request.json or {}
    cfg = safe_read(CONFIG_PATH)
    if not cfg: return jsonify({"status":"error"}), 404
    cfg["session"].update({
        "access_token":     p.get("access_token",""),
        "refresh_token":    p.get("refresh_token",""),
        "expires_at":       p.get("expires_at",""),
        "is_authenticated": True,
    })
    cfg["subscription_status"] = p.get("subscription_status","active")
    cfg["last_login_at"]       = now_iso()
    cfg = mark_activity(cfg)
    safe_write(CONFIG_PATH, cfg)
    session_mgr.update_last_activity(SESSION_PATH)
    return jsonify({"status":"ok"})

@app.route("/api/auth/heartbeat", methods=["POST"])
def auth_heartbeat():
    cfg = safe_read(CONFIG_PATH)
    if not cfg: return jsonify({"status":"error"}), 404
    chk = check_session(cfg)
    if not chk["valid"]:
        cfg["session"]["is_authenticated"] = False
        safe_write(CONFIG_PATH, cfg)
        return jsonify({"status":"expired","reason":chk["reason"]}), 401
    cfg = mark_activity(cfg)
    safe_write(CONFIG_PATH, cfg)
    session_mgr.update_last_activity(SESSION_PATH)
    return jsonify({"status":"ok"})

@app.route("/api/auth/auto-logout", methods=["POST"])
def auto_logout():
    cfg = safe_read(CONFIG_PATH)
    if cfg:
        cfg["session"]["is_authenticated"] = False
        cfg["session"]["access_token"]     = ""
        cfg = mark_activity(cfg)
        safe_write(CONFIG_PATH, cfg)
    session_mgr.clear_local_session(SESSION_PATH)
    return jsonify({"status":"ok"})

@app.route("/api/recovery/repair-files", methods=["POST"])
def repair_files():
    """Re-download model files when something is missing."""
    cfg = safe_read(CONFIG_PATH)
    if not cfg: return jsonify({"status":"error"}), 404
    result = do_download_files(cfg)
    safe_write(CONFIG_PATH, result["config"])
    if result["ok"]:
        return jsonify({"status":"ok","downloaded":result["downloaded"],"warnings":result["warnings"]})
    return jsonify({"status":"error","errors":result.get("errors",[])}), 500

@app.route("/api/recovery/reselect-data-dir", methods=["POST"])
def recovery_reselect():
    data_dir = (request.json or {}).get("data_dir","").strip()
    if not data_dir: return jsonify({"status":"error","message":"data_dir required"}), 400
    try: created = create_dirs(data_dir)
    except Exception as e: return jsonify({"status":"error","message":str(e)}), 400
    cfg = safe_read(CONFIG_PATH) or build_default_config()
    cfg.update(created)
    safe_write(CONFIG_PATH, cfg)
    return jsonify({"status":"ok","paths":created})

@app.route("/api/subscription/renew-demo", methods=["POST"])
def renew_demo():
    cfg = safe_read(CONFIG_PATH)
    if not cfg: return jsonify({"status":"error"}), 404
    cfg["subscription_status"] = "active"
    safe_write(CONFIG_PATH, cfg)
    return jsonify({"status":"ok","message":"subscription renewed (demo)"})


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    APPDATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n[bootstrap] Running at http://127.0.0.1:{LOCAL_API_PORT}\n")
    app.run(host="127.0.0.1", port=LOCAL_API_PORT, debug=False)
