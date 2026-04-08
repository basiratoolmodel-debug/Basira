# packaging/Basira_app_structure.py
"""
Basira Main App  —  http://127.0.0.1:5000
==========================================
Started automatically by launcher.py.

Serves packaging/templates/basira_app.html — the full analysis UI.
Handles all analysis API routes called by basira_app.html:
  POST /analyze          → CSV upload → XAI/RCA/chart analysis
  POST /scrape_analyze   → URL scrape → analysis

Also handles session management so basira_app.html knows
the user is authenticated after the cloud login.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

from flask import Flask, jsonify, request, send_file, session
from flask_cors import CORS

import basira_paths as paths

# ─── Paths ────────────────────────────────────────────────────────────────────
TEMPLATES_DIR = paths.get_templates_dir()   # packaging/templates/
APP_HTML      = TEMPLATES_DIR / "basira_app.html"

DEFAULT_HOST            = "127.0.0.1"
DEFAULT_PORT            = 5000
SESSION_TIMEOUT_MINUTES = 20


# ─── App ──────────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=None)
app.secret_key = "basira-local-key-2025-change-in-production"

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def now_iso(): return datetime.utcnow().isoformat() + "Z"

def get_data_dir() -> Path:
    """Read the data_dir the user chose during setup."""
    cfg_path = paths.get_config_path()
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            d = cfg.get("data_dir", "")
            if d and Path(d).exists():
                return Path(d)
        except Exception:
            pass
    return paths.get_default_user_data_dir()

def ensure_dirs() -> Path:
    d = get_data_dir()
    (d / "input_files").mkdir(parents=True, exist_ok=True)
    (d / "output_files").mkdir(parents=True, exist_ok=True)
    return d

def session_expired() -> bool:
    exp = session.get("expires_at")
    if not exp: return True
    try: return datetime.utcnow() > datetime.fromisoformat(exp)
    except: return True

def refresh_timeout():
    session["expires_at"] = (
        datetime.utcnow() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    ).isoformat()

def is_logged_in() -> bool:
    return bool(session.get("logged_in")) and not session_expired()


# ─── Request guard ────────────────────────────────────────────────────────────
PUBLIC = {"/", "/health", "/favicon.ico",
          "/api/session/bootstrap", "/api/session/status",
          "/api/session/ping",      "/api/auth/ping",
          "/api/auth/session"}

@app.before_request
def guard():
    if request.path in PUBLIC: return
    if request.path.endswith((".css",".js",".png",".jpg",".svg",
                               ".ico",".gif",".webp",".woff",".woff2")): return
    if is_logged_in(): refresh_timeout(); return
    if request.path.startswith("/api/"):
        return jsonify({"status":"error","code":"AUTH_REQUIRED",
                        "message":"Session expired. Please log in again."}), 401


# ─── Serve basira_app.html ────────────────────────────────────────────────────
@app.route("/")
def home():
    if not APP_HTML.exists():
        return (
            f"<html dir='rtl'><head><meta charset='UTF-8'></head><body style='font-family:Arial;padding:40px;text-align:right'>"
            f"<h2>لم يتم العثور على ملف basira_app.html</h2>"
            f"<p>المسار المتوقع: <code>{APP_HTML}</code></p>"
            f"<p>تأكد من وجود الملف في <code>packaging/templates/basira_app.html</code></p>"
            f"</body></html>"
        ), 404
    return send_file(str(APP_HTML), mimetype="text/html")

@app.route("/health")
def health():
    return jsonify({
        "status":     "ok",
        "server_time": now_iso(),
        "app_html":   str(APP_HTML),
        "app_ready":  APP_HTML.exists(),
        "data_dir":   str(get_data_dir()),
    })

@app.route("/favicon.ico")
def favicon(): return "", 204


# ─── Session APIs (called by basira_app.html on load) ────────────────────────
@app.route("/api/session/bootstrap")
def session_bootstrap():
    """basira_app.html calls this on DOMContentLoaded."""
    authenticated = is_logged_in()
    if authenticated: refresh_timeout()
    return jsonify({
        "status": "success",
        "session": {
            "authenticated": authenticated,
            "user_id":       session.get("user_id", ""),
            "user_name":     session.get("user_id", "Basira User"),
        }
    })

@app.route("/api/session/status")
def session_status():
    return jsonify({"status":"success","session":{"authenticated":is_logged_in()}})

@app.route("/api/session/ping", methods=["POST"])
def session_ping():
    if is_logged_in(): refresh_timeout()
    return jsonify({"status":"ok"})

@app.route("/api/session/logout", methods=["POST"])
def session_logout():
    session.clear()
    return jsonify({"status":"ok"})

@app.route("/api/auth/ping")
def auth_ping():
    return jsonify({"status":"ok","authenticated":is_logged_in()})

@app.route("/api/auth/auto-logout", methods=["POST"])
def auth_auto_logout():
    session.clear()
    return jsonify({"status":"ok"})


# ─── Session linking (called by local-setup.js after Supabase login) ──────────
@app.route("/api/auth/session", methods=["POST"])
def auth_set_session():
    """
    local-setup.js calls this after the user logs in via Supabase.
    This links the cloud login to the local Flask session so
    basira_app.html's /api/session/bootstrap returns authenticated=true.
    """
    p = request.get_json(force=True) or {}
    session["logged_in"]           = True
    session["user_id"]             = p.get("user_id", "")
    session["access_token"]        = p.get("access_token", "")
    session["refresh_token"]       = p.get("refresh_token", "")
    session["subscription_status"] = p.get("subscription_status", "active")
    refresh_timeout()
    return jsonify({"status":"ok","message":"session linked",
                    "expires_at":session.get("expires_at")})

@app.route("/api/auth/heartbeat", methods=["POST"])
def auth_heartbeat():
    if not is_logged_in():
        return jsonify({"status":"error","message":"Session expired."}), 401
    refresh_timeout()
    return jsonify({"status":"ok","expires_at":session.get("expires_at")})


# ─── Analysis — POST /analyze ─────────────────────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Receives CSV from basira_app.html.
    Saves to <data_dir>/input_files/
    Returns full XAI/RCA/chart JSON.

    TODO: Replace the placeholder return block with your real ML analysis.
    The response schema must match what basira_app.html expects (see below).
    """
    file = request.files.get("file")
    if not file:
        return jsonify({"status":"error","message":"No file uploaded."}), 400

    data_dir  = ensure_dirs()
    save_path = data_dir / "input_files" / file.filename
    file.save(str(save_path))

    # ─── TODO: Replace with your real analysis ────────────────────────────────
    # import pandas as pd
    # from your_analysis_module import run_full_analysis
    # df     = pd.read_csv(save_path)
    # result = run_full_analysis(df)
    # return jsonify(result)
    # ─────────────────────────────────────────────────────────────────────────

    return jsonify({
        "status": "ok",
        "dataset_meta": {
            "rows": 200, "cols": 10, "numeric_cols": 7,
            "missing_total": 5, "duplicate_rows": 2,
            "target_column": "target",
            "source_file": file.filename,
        },
        "model_score": 91,
        "target_detection": {
            "column": "target",
            "reason": "Auto-detected: highest correlation with outcome.",
        },
        "decision_narrative": {
            "headline":           "Strong predictive signal detected in dataset.",
            "summary":            "The uploaded dataset shows clear structure suitable for modelling with high confidence.",
            "key_finding":        "Top feature (feature_1) accounts for 34% of total variance.",
            "secondary_finding":  "Features 3 and 5 exhibit moderate multicollinearity — consider dimensionality reduction.",
            "risk_alert":         "⚠ 5 missing values detected across 2 columns — imputation recommended.",
            "recommended_action": "Apply median imputation to missing values, then retrain for production deployment.",
        },
        "xai_report": [
            {"feature":"feature_1","impact":34,"trend":"Positive","importance_level":"Critical"},
            {"feature":"feature_2","impact":22,"trend":"Negative","importance_level":"High"},
            {"feature":"feature_3","impact":18,"trend":"Positive","importance_level":"High"},
            {"feature":"feature_4","impact":12,"trend":"Negative","importance_level":"Medium"},
            {"feature":"feature_5","impact":8, "trend":"Positive","importance_level":"Low"},
        ],
        "advanced_insights": [
            {"title":"Data Quality","value":"97.5%","metric":"Completeness",
             "desc":"Dataset is nearly complete with only 2.5% missing values.",
             "action":"Impute 5 missing cells before deployment.","color":"#0ea5e9"},
            {"title":"Model Confidence","value":"91%","metric":"Accuracy",
             "desc":"The predictive model achieves high accuracy on cross-validation.",
             "action":"Deploy with monitoring for data drift.","color":"#22c55e"},
        ],
        "chart_recommendations": [
            {"type":"bar","title":"Feature Impact (XAI)","reason":"Shows relative feature importance"},
            {"type":"doughnut","title":"Feature Share","reason":"Proportion of total explained variance"},
            {"type":"line","title":"Impact Trend","reason":"Trend across ranked features"},
        ],
        "rca_report": [
            {"id":"RCA-01","title":"Missing Data Risk","severity":"Medium",
             "causes":["feature_3 has 3 nulls","feature_7 has 2 nulls"],
             "recommendation":"Apply KNN imputation on feature_3 and median on feature_7."},
        ],
        "corr_matrix": [],
        "dist_data":   {},
        "scatter_data":    None,
        "cumulative_data": None,
        "preview": [],
    })


# ─── Scrape analysis — POST /scrape_analyze ───────────────────────────────────
@app.route("/scrape_analyze", methods=["POST"])
def scrape_analyze():
    """
    Receives a URL from basira_app.html, scrapes it, runs analysis.

    TODO: Replace with real scraping logic using requests + BeautifulSoup.
    """
    url = request.form.get("url","").strip()
    if not url:
        return jsonify({"status":"error","message":"No URL provided."}), 400

    # ─── TODO: Replace with real scraping ────────────────────────────────────
    # import requests as http_req
    # from bs4 import BeautifulSoup
    # import pandas as pd
    # ...
    # ─────────────────────────────────────────────────────────────────────────

    return jsonify({
        "status": "ok",
        "dataset_meta": {
            "rows": 80, "cols": 6, "numeric_cols": 4,
            "missing_total": 2, "duplicate_rows": 0,
            "target_column": "value", "source_url": url,
        },
        "model_score": 83,
        "target_detection": {"column":"value","reason":"Primary numeric column detected."},
        "decision_narrative": {
            "headline":           "Web data successfully extracted and analysed.",
            "summary":            "Scraped content shows usable tabular structure.",
            "key_finding":        "Primary column shows strong normal distribution.",
            "secondary_finding":  "Text columns require NLP preprocessing.",
            "risk_alert":         "⚠ Dynamic JavaScript content may not be fully captured.",
            "recommended_action": "Validate scraped data completeness before using in production.",
        },
        "xai_report":[],
        "advanced_insights":[],
        "chart_recommendations":[],
        "rca_report":[],
        "corr_matrix":[],
        "dist_data":{},
        "scatter_data":None,
        "cumulative_data":None,
        "preview":[],
    })


# ─── Subscription status (used by basira_app.html settings) ──────────────────
@app.route("/api/subscription/status")
def subscription_status():
    return jsonify({"status":"ok",
                    "subscription_status":session.get("subscription_status","inactive")})


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ensure_dirs()
    print(f"\n[main-app] Running at http://{DEFAULT_HOST}:{DEFAULT_PORT}")
    print(f"[main-app] Serving: {APP_HTML}")
    print(f"[main-app] Data dir: {get_data_dir()}\n")
    app.run(host=DEFAULT_HOST, port=DEFAULT_PORT, debug=False, threaded=True)
