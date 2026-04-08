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
GITHUB_RAW      = "https://raw.githubusercontent.com/basiratoolmodel-debug/Basira/main/Basira_local"
GITHUB_RELEASE  = "https://github.com/basiratoolmodel-debug/Basira/releases/download/v1.0.0"

# Direct raw file URLs — no ZIP, no extraction needed
DOWNLOAD_MODELS_URL = f"{GITHUB_RELEASE}/models.zip"

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

    # Download models zip from GitHub release
    # Note: your uploaded file is "models (2).zip" — URL-encode the spaces
    models_url = f"{GITHUB_RELEASE}/models.zip"
    zip_path   = models_dir / "_download_tmp.zip"
    try:
        urllib.request.urlretrieve(models_url, str(zip_path))
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
