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
import os
import socket
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

from flask import Flask, jsonify, request, send_file, session, send_from_directory, Response, redirect
from flask_cors import CORS
from werkzeug.utils import secure_filename

import basira_paths as paths

# ─── Paths ────────────────────────────────────────────────────────────────────
TEMPLATES_DIR = paths.get_templates_dir()   # packaging/templates/
APP_HTML      = TEMPLATES_DIR / "basira_app.html"

DEFAULT_HOST            = "127.0.0.1"
DEFAULT_PORT            = 5000
SESSION_TIMEOUT_MINUTES = 20


# ─── App ──────────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=None)

# FIX: secret key فريد لكل تثبيت — يُحفظ في config.json ويُقرأ منه
def _get_or_create_secret_key() -> str:
    import secrets as _secrets
    cfg_path = paths.get_config_path()
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            if cfg.get("flask_secret_key"):
                return cfg["flask_secret_key"]
        except Exception:
            pass
    key = _secrets.token_hex(32)
    try:
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        existing = {}
        if cfg_path.exists():
            try:
                existing = json.loads(cfg_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        existing["flask_secret_key"] = key
        cfg_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return key

app.secret_key = _get_or_create_secret_key()

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def now_iso():
    return datetime.utcnow().isoformat() + "Z"


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
    if not exp:
        return True
    try:
        return datetime.utcnow() > datetime.fromisoformat(exp)
    except Exception:
        return True


def refresh_timeout():
    session["expires_at"] = (
        datetime.utcnow() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    ).isoformat()


def is_logged_in() -> bool:
    # ✅ FIX: التطبيق يعمل محلياً بدون الحاجة لتسجيل دخول سحابي.
    # الجلسة تُعتبر نشطة دائماً على 127.0.0.1.
    return True


# ─── Port helper ──────────────────────────────────────────────────────────────
def _is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0




def _read_scraper_port() -> int | None:
    candidates = [
        Path(__file__).resolve().parent / "scraper.port",
        Path(__file__).resolve().parent.parent / "scraper.port",
        TEMPLATES_DIR / "scraper.port",
    ]
    for candidate in candidates:
        try:
            port = int(candidate.read_text(encoding="utf-8").strip())
            if 1 <= port <= 65535:
                return port
        except Exception:
            continue
    return None


def _is_http_service_ok(port: int, path: str = "/health") -> bool:
    try:
        import urllib.request
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=0.8) as resp:
            return 200 <= getattr(resp, "status", 200) < 500
    except Exception:
        return _is_port_open(port)


def _is_scraper_running() -> bool:
    port = _read_scraper_port()
    return bool(port and _is_port_open(port))


def _get_python_exe() -> str:
    """يرجع pythonw.exe لو موجود، وإلا python.exe — نفس البيئة الحالية."""
    exe = Path(sys.executable)
    pythonw = exe.parent / "pythonw.exe"
    return str(pythonw) if pythonw.exists() else str(exe)


def _silent_popen(cmd: list, cwd: str) -> subprocess.Popen:
    """يشغّل عملية بدون نافذة كونسول على Windows."""
    kwargs: dict = {"cwd": cwd}
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = si
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return subprocess.Popen(cmd, **kwargs)


def _find_launcher(filename: str) -> Path | None:
    """
    يبحث عن ملف launcher في عدة مسارات محتملة:
      1. templates/ (المسار الرئيسي)
      2. نفس مجلد هذا الملف
      3. مجلد الأب
    يرجع Path أو None لو ما لقى.
    """
    candidates = [
        Path(__file__).resolve().parent.parent / filename,           # Basira_app/
        Path(__file__).resolve().parent / filename,                  # templates/
        TEMPLATES_DIR / filename,
        Path(__file__).resolve().parent / "templates" / filename,
        Path(__file__).resolve().parent.parent / "templates" / filename,
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


# ─── Request guard ────────────────────────────────────────────────────────────
PUBLIC = {
    "/", "/login", "/health", "/favicon.ico",
    "/api/session/bootstrap", "/api/session/status",
    "/api/session/ping",      "/api/auth/ping",
    "/api/auth/session",
}


@app.before_request
def guard():
    if request.path in PUBLIC:
        return
    if request.path.endswith((".css", ".js", ".png", ".jpg", ".svg",
                               ".ico", ".gif", ".webp", ".woff", ".woff2")):
        return
    if is_logged_in():
        refresh_timeout()
        return
    if request.path.startswith("/api/"):
        return jsonify({
            "status": "error",
            "code": "AUTH_REQUIRED",
            "message": "Session expired. Please log in again.",
        }), 401


# ─── Serve basira_app.html ────────────────────────────────────────────────────
@app.route("/")
def home():
    if not APP_HTML.exists():
        return (
            f"<html dir='rtl'><head><meta charset='UTF-8'></head>"
            f"<body style='font-family:Arial;padding:40px;text-align:right'>"
            f"<h2>لم يتم العثور على ملف basira_app.html</h2>"
            f"<p>المسار المتوقع: <code>{APP_HTML}</code></p>"
            f"<p>تأكد من وجود الملف في <code>packaging/templates/basira_app.html</code></p>"
            f"</body></html>"
        ), 404
    return send_file(str(APP_HTML), mimetype="text/html")


@app.route("/health")
def health():
    """
    Health check شامل — يتحقق من حالة كل الـ services الفرعية.
    الـ frontend يقدر يستخدم هذا بدل ما يتصل على كل port منفرد.
    """
    return jsonify({
        "status":      "ok",
        "server_time": now_iso(),
        "app_html":    str(APP_HTML),
        "app_ready":   APP_HTML.exists(),
        "data_dir":    str(get_data_dir()),
        "services": {
            "main_app":     _is_port_open(5000),
            "bootstrap":    _is_port_open(5001),
            "preprocessor": _is_http_service_ok(5050),
            "analysis":     _is_http_service_ok(5055),
            "scraper":      _is_scraper_running(),
            "scraper_port": _read_scraper_port(),
        },
    })


@app.route("/favicon.ico")
def favicon():
    return "", 204


# ─── Session APIs (called by basira_app.html on load) ────────────────────────
@app.route("/login")
def login_via_redirect():
    """
    THE SESSION BRIDGE — this is how cloud login reaches local Flask.

    local-setup.js redirects the browser to:
        http://127.0.0.1:5000/login?token=XXX&user_id=YYY&sub=active

    Because the browser navigates here directly (same origin), Flask sets
    a real session cookie that persists — no CORS, no no-cors issues.
    Then redirects to / so the user sees basira_app.html logged in.
    """
    token   = request.args.get("token", "")
    user_id = request.args.get("user_id", "")
    sub     = request.args.get("sub", "active")
    ref_tok = request.args.get("refresh", "")

    if token and user_id:
        session["logged_in"]           = True
        session["user_id"]             = user_id
        session["access_token"]        = token
        session["refresh_token"]       = ref_tok
        session["subscription_status"] = sub
        refresh_timeout()

    return redirect("/")


@app.route("/api/session/bootstrap")
def session_bootstrap():
    """basira_app.html calls this on DOMContentLoaded to check auth status."""
    # ✅ FIX: دائماً مصادق — التطبيق محلي لا يحتاج cloud login.
    return jsonify({
        "status": "success",
        "session": {
            "authenticated": True,
            "user_id":       session.get("user_id", "local_user"),
            "user_name":     session.get("user_name", "Basira User"),
            "email":         session.get("email", ""),
            "display_name":  session.get("display_name", "Basira User"),
        },
    })


@app.route("/api/session/status")
def session_status():
    # ✅ FIX: دائماً مصادق محلياً.
    return jsonify({"status": "success", "session": {"authenticated": True}})


@app.route("/api/session/ping", methods=["POST"])
def session_ping():
    if is_logged_in():
        refresh_timeout()
    return jsonify({"status": "ok"})


@app.route("/api/session/logout", methods=["POST"])
def session_logout():
    session.clear()
    return jsonify({"status": "ok", "redirect": "https://basira.basira-toolmodel.workers.dev/login"})


@app.route("/api/auth/ping")
def auth_ping():
    # ✅ FIX: دائماً مصادق محلياً.
    return jsonify({"status": "ok", "authenticated": True})


@app.route("/api/auth/auto-logout", methods=["POST"])
def auth_auto_logout():
    session.clear()
    return jsonify({"status": "ok"})


# ─── Session linking (called by local-setup.js after Supabase login) ──────────
@app.route("/api/auth/session", methods=["POST", "OPTIONS"])
def auth_set_session():
    """
    Fallback POST session setter (used when same-origin POST works).
    Primary session setting is done via GET /login redirect.
    """
    if request.method == "OPTIONS":
        resp = jsonify({"status": "ok"})
        resp.headers["Access-Control-Allow-Origin"]  = "*"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return resp

    p = request.get_json(force=True) or {}
    if p.get("user_id") and p.get("access_token"):
        session["logged_in"]           = True
        session["user_id"]             = p.get("user_id", "")
        session["access_token"]        = p.get("access_token", "")
        session["refresh_token"]       = p.get("refresh_token", "")
        session["subscription_status"] = p.get("subscription_status", "active")
        refresh_timeout()
    resp = jsonify({
        "status":     "ok",
        "message":    "session linked",
        "expires_at": session.get("expires_at"),
    })
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route("/api/auth/heartbeat", methods=["POST"])
def auth_heartbeat():
    # ✅ FIX: دائماً نشط محلياً.
    return jsonify({"status": "ok", "expires_at": None})


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
        return jsonify({"status": "error", "message": "No file uploaded."}), 400

    data_dir  = ensure_dirs()
    fname = secure_filename(file.filename or "uploaded.csv")
    save_path = data_dir / "input_files" / fname
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
            "source_file": fname,
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
            {"feature": "feature_1", "impact": 34, "trend": "Positive", "importance_level": "Critical"},
            {"feature": "feature_2", "impact": 22, "trend": "Negative", "importance_level": "High"},
            {"feature": "feature_3", "impact": 18, "trend": "Positive", "importance_level": "High"},
            {"feature": "feature_4", "impact": 12, "trend": "Negative", "importance_level": "Medium"},
            {"feature": "feature_5", "impact": 8,  "trend": "Positive", "importance_level": "Low"},
        ],
        "advanced_insights": [
            {
                "title": "Data Quality", "value": "97.5%", "metric": "Completeness",
                "desc": "Dataset is nearly complete with only 2.5% missing values.",
                "action": "Impute 5 missing cells before deployment.", "color": "#0ea5e9",
            },
            {
                "title": "Model Confidence", "value": "91%", "metric": "Accuracy",
                "desc": "The predictive model achieves high accuracy on cross-validation.",
                "action": "Deploy with monitoring for data drift.", "color": "#22c55e",
            },
        ],
        "chart_recommendations": [
            {"type": "bar",      "title": "Feature Impact (XAI)", "reason": "Shows relative feature importance"},
            {"type": "doughnut", "title": "Feature Share",         "reason": "Proportion of total explained variance"},
            {"type": "line",     "title": "Impact Trend",          "reason": "Trend across ranked features"},
        ],
        "rca_report": [
            {
                "id": "RCA-01", "title": "Missing Data Risk", "severity": "Medium",
                "causes": ["feature_3 has 3 nulls", "feature_7 has 2 nulls"],
                "recommendation": "Apply KNN imputation on feature_3 and median on feature_7.",
            },
        ],
        "corr_matrix":   [],
        "dist_data":     {},
        "scatter_data":  None,
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
    url = request.form.get("url", "").strip()
    if not url:
        return jsonify({"status": "error", "message": "No URL provided."}), 400

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
        "target_detection": {"column": "value", "reason": "Primary numeric column detected."},
        "decision_narrative": {
            "headline":           "Web data successfully extracted and analysed.",
            "summary":            "Scraped content shows usable tabular structure.",
            "key_finding":        "Primary column shows strong normal distribution.",
            "secondary_finding":  "Text columns require NLP preprocessing.",
            "risk_alert":         "⚠ Dynamic JavaScript content may not be fully captured.",
            "recommended_action": "Validate scraped data completeness before using in production.",
        },
        "xai_report":            [],
        "advanced_insights":     [],
        "chart_recommendations": [],
        "rca_report":            [],
        "corr_matrix":           [],
        "dist_data":             {},
        "scatter_data":          None,
        "cumulative_data":       None,
        "preview":               [],
    })


# ─── Web Scraping Launcher ────────────────────────────────────────────────────
@app.route("/launch-webscraper", methods=["POST", "OPTIONS"])
def launch_webscraper():
    import socket as _sock, time as _time

    if request.method == "OPTIONS":
        return Response(status=200)

    # scraper.port في Basira_app/ (نفس مجلد هذا الملف)
    _port_file = Path(__file__).resolve().parent / "scraper.port"

    def _read_port():
        try:
            p = int(_port_file.read_text(encoding="utf-8").strip())
            with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as s:
                s.settimeout(0.4)
                if s.connect_ex(("127.0.0.1", p)) == 0:
                    return p
        except Exception:
            pass
        try: _port_file.unlink(missing_ok=True)
        except: pass
        return None

    # السكرابر شغّال مسبقاً؟
    existing = _read_port()
    if existing:
        return jsonify({"status": "already_running", "port": existing})

    # ابحث عن launch_webscraping.py في Basira_app/
    launcher = _find_launcher("launch_webscraping.py")
    if launcher is None:
        return jsonify({
            "status": "error",
            "message": "launch_webscraping.py not found in Basira_app/",
        }), 404

    # ✅ FIX: cwd دائماً = Basira_app/ حتى يُكتب scraper.port في المكان الصحيح
    # بغض النظر عن أين وُجد launch_webscraping.py (Basira_app/ أو templates/)
    basira_app_dir = Path(__file__).resolve().parent
    _silent_popen([_get_python_exe(), str(launcher), "--silent"],
                  cwd=str(basira_app_dir))

    # انتظر حتى scraper.port يُكتب (max 20s)
    for _ in range(40):
        _time.sleep(0.5)
        port = _read_port()
        if port:
            return jsonify({"status": "started", "port": port})

    return jsonify({"status": "timeout",
                    "message": "Scraper did not start in 20s — تحقق من المكتبات المطلوبة"}), 503


# ─── Analysis Engine Launcher ─────────────────────────────────────────────────
@app.route("/analysis-engine")
def serve_analysis_engine():
    """يخدم basira_analysis_engine.html مباشرة."""
    # ابحث في templates/ أو نفس مجلد هذا الملف
    for folder in [TEMPLATES_DIR, Path(__file__).resolve().parent]:
        if (folder / "basira_analysis_engine.html").exists():
            return send_from_directory(str(folder), "basira_analysis_engine.html")
    return jsonify({"status": "error", "message": "basira_analysis_engine.html not found"}), 404


@app.route("/chart-management")
def serve_chart_management():
    """يخدم chart_management.html مباشرة."""
    for folder in [TEMPLATES_DIR, Path(__file__).resolve().parent]:
        if (folder / "chart_management.html").exists():
            return send_from_directory(str(folder), "chart_management.html")
    return jsonify({"status": "error", "message": "chart_management.html not found"}), 404


@app.route("/launch-analysis", methods=["POST", "OPTIONS"])
def launch_analysis():
    """
    ✅ FIX: كان يعطي 404 لأن TEMPLATES_DIR لم يكن يُحسب صح في بعض بيئات التشغيل.
    الحل: _find_launcher يبحث في عدة مسارات تلقائياً.
    """
    if request.method == "OPTIONS":
        return Response(status=200)

    ANALYSIS_PORT = 5055

    if _is_port_open(ANALYSIS_PORT):
        return jsonify({"status": "already_running"})

    launcher = _find_launcher("launch_analysis.py")
    if launcher is None:
        return jsonify({
            "status": "error",
            "message": "launch_analysis.py not found. تأكد من وجود الملف في templates/",
            "searched_in": [
                str(TEMPLATES_DIR / "launch_analysis.py"),
                str(Path(__file__).resolve().parent / "launch_analysis.py"),
            ],
        }), 404

    _silent_popen(
        [_get_python_exe(), str(launcher), "--silent"],
        cwd=str(launcher.parent),
    )
    return jsonify({"status": "launching", "launcher": str(launcher)})


# ─── Subscription status ──────────────────────────────────────────────────────
@app.route("/api/subscription/status")
def subscription_status():
    # ✅ FIX: الاشتراك نشط دائماً محلياً.
    return jsonify({
        "status": "ok",
        "subscription_status": "active",
    })


# ─── Preprocessor ─────────────────────────────────────────────────────────────
@app.route("/basira_preprocessor.html")
def serve_preprocessor_html():
    for folder in [TEMPLATES_DIR, Path(__file__).resolve().parent]:
        if (folder / "basira_preprocessor.html").exists():
            return send_from_directory(str(folder), "basira_preprocessor.html")
    return jsonify({"status": "error", "message": "basira_preprocessor.html not found"}), 404


@app.route("/launch-preprocessor", methods=["POST", "OPTIONS"])
def launch_preprocessor():
    """
    ✅ FIX: كان يعطي 404 لأن TEMPLATES_DIR لم يكن يُحسب صح في بعض بيئات التشغيل.
    الحل: _find_launcher يبحث في عدة مسارات تلقائياً.
    """
    if request.method == "OPTIONS":
        return Response(status=200)

    PREPROCESS_PORT = 5050

    if _is_port_open(PREPROCESS_PORT):
        return jsonify({"status": "already_running"})

    # حاول launch_preprocessor.py أولاً، وإلا basira_app.py مباشرة
    launcher = _find_launcher("launch_preprocessor.py") or _find_launcher("basira_app.py")
    if launcher is None:
        return jsonify({
            "status": "error",
            "message": "launch_preprocessor.py / basira_app.py not found. تأكد من وجود الملفات في templates/",
            "searched_in": [
                str(TEMPLATES_DIR / "launch_preprocessor.py"),
                str(TEMPLATES_DIR / "basira_app.py"),
                str(Path(__file__).resolve().parent / "launch_preprocessor.py"),
            ],
        }), 404

    _silent_popen(
        [_get_python_exe(), str(launcher), "--silent"],
        cwd=str(launcher.parent),
    )
    return jsonify({"status": "launching", "launcher": str(launcher)})


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ensure_dirs()
    print(f"\n[main-app] Running at http://{DEFAULT_HOST}:{DEFAULT_PORT}")
    print(f"[main-app] Serving:  {APP_HTML}")
    print(f"[main-app] Data dir: {get_data_dir()}\n")
    app.run(host=DEFAULT_HOST, port=DEFAULT_PORT, debug=False, threaded=True)
