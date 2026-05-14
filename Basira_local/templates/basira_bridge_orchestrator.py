"""
BASIRA BRIDGE ORCHESTRATOR - FINAL PIPELINE COORDINATOR
=========================================================
Connects Basira's final analytical engines with the visualization layer.

Pipeline:
Preprocessing / uploaded clean data
→ Bridge / Orchestrator
→ Supervised OR Unsupervised engine
→ RCA engine
→ Insight engine
→ Unified JSON payload for visualization/report

This file does NOT merge or rewrite the final engines.
It only coordinates them and exposes a Flask /analyze endpoint.

Config priority order
----------------------
1. If strategy / force_strategy == "unsupervised"  → force unsupervised.
2. If explicit target_column + task_type passed in the request → use them.
3. If config.json uploaded → use task_type, target_column, modality, etc. from config.
4. Else → fall back to internal inference.

If config specifies a target column that does NOT exist in the uploaded
dataframe, the bridge returns a clear 422 error instead of silently
picking a different column.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import traceback
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except Exception:  # pragma: no cover — allows smoke tests without Flask
    Flask   = None
    request = None
    FLASK_AVAILABLE = False
    def jsonify(obj=None, *args, **kwargs):  # type: ignore
        return obj
    def CORS(app):  # type: ignore
        return app

# Keep numerical libraries from spinning up extra threads on student devices.
os.environ.setdefault("OMP_NUM_THREADS",        "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS",   "1")
os.environ.setdefault("MKL_NUM_THREADS",        "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS",    "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

APP_DIR    = Path(__file__).resolve().parent
UPLOAD_DIR = APP_DIR / "bridge_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Final Basira engines  (never rewrite or merge these)
# ---------------------------------------------------------------------------
from supervised_engine_F   import SupervisedEngine,   BasiraEngineError
from unsupervised_engine_F import UnsupervisedEngine, BasiraUnsupervisedError
from rca_engine_F          import RCAEngine,           BasiraRCAError
from insight_engine_F      import InsightEngine,       BasiraInsightError

# Optional chart helpers — bridge still works if charts_engine is absent.
try:
    import charts_engine  # type: ignore
except Exception:       # pragma: no cover
    charts_engine = None

# ---------------------------------------------------------------------------
# Flask application
# ---------------------------------------------------------------------------
if FLASK_AVAILABLE:
    app = Flask(__name__)
    CORS(app)
else:
    class _DummyApp:  # type: ignore
        def route(self, *a, **kw):
            def _d(f): return f
            return _d
        def run(self, *a, **kw):
            raise RuntimeError("Flask not installed. Run: pip install -r requirements.txt")
    app = _DummyApp()

BRIDGE_VERSION = "basira-bridge-v1.1"


# =============================================================================
# JSON safety  (mirrors the engines' own _json_safe for consistency)
# =============================================================================

def json_safe(obj: Any) -> Any:
    """Recursively convert NumPy / Pandas / dataclass values into JSON-safe types."""
    if is_dataclass(obj):
        return json_safe(asdict(obj))
    if isinstance(obj, dict):
        return {str(k): json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [json_safe(v) for v in obj]
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        v = float(obj)
        return None if (math.isnan(v) or math.isinf(v)) else v
    if isinstance(obj, np.ndarray):
        return json_safe(obj.tolist())
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    if obj is pd.NA:
        return None
    if obj is None or isinstance(obj, (str, int, bool)):
        return obj
    return str(obj)


def result_to_dict(result: Any) -> Dict[str, Any]:
    """Convert an engine result dataclass/object to a plain dict safely."""
    if hasattr(result, "to_dict"):
        return json_safe(result.to_dict())
    if is_dataclass(result):
        return json_safe(asdict(result))
    if isinstance(result, dict):
        return json_safe(result)
    if hasattr(result, "__dict__"):
        return json_safe(vars(result))
    return {}


# =============================================================================
# File loading
# =============================================================================

def load_uploaded_dataframe(file_storage) -> Tuple[pd.DataFrame, Path]:
    """Save and read the uploaded CSV / XLSX dataset."""
    filename = Path(file_storage.filename or "uploaded.csv").name
    suffix   = Path(filename).suffix.lower()
    if suffix not in {".csv", ".xlsx", ".xls"}:
        raise ValueError("Unsupported file type. Please upload CSV, XLSX, or XLS.")

    stamp     = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", filename)
    saved     = UPLOAD_DIR / f"{stamp}_{safe_name}"
    file_storage.save(saved)

    df = pd.read_csv(saved) if suffix == ".csv" else pd.read_excel(saved)
    if df.empty:
        raise ValueError("The uploaded dataset is empty.")
    df.columns = [str(c).strip() for c in df.columns]
    return df, saved


# =============================================================================
# Config.json loading and resolution
# =============================================================================

def load_optional_config(config_file_storage) -> Optional[Dict[str, Any]]:
    """
    Read and parse the optional config.json uploaded by the user.

    The preprocessor (basira_app.py) writes this file.  Returns None when no
    config file is supplied or when parsing fails (the bridge then falls back
    to internal inference).

    Parameters
    ----------
    config_file_storage : werkzeug.datastructures.FileStorage or None
        The file received under the 'config' field in the multipart request.

    Returns
    -------
    dict or None
    """
    if config_file_storage is None:
        return None
    try:
        raw = config_file_storage.read()
        if not raw:
            return None
        cfg = json.loads(raw.decode("utf-8"))
        if not isinstance(cfg, dict):
            return None
        return cfg
    except Exception as exc:
        # Log but do not crash — fall back to inference.
        print(f"[Bridge] Warning: failed to parse config.json: {exc}")
        return None


def resolve_task_from_config(
    df: pd.DataFrame,
    cfg: Dict[str, Any],
) -> Tuple[str, Optional[str]]:
    """
    Extract task_type and target_column from a preprocessor config dict.

    Rules
    -----
    - If task_type == "unsupervised", target_column is forcibly set to None.
    - If task_type is supervised and target_column is given, verify it exists
      in df.  Raise ValueError with a clear message if it is missing.

    Parameters
    ----------
    df  : The uploaded dataframe (used only for column validation).
    cfg : Parsed config.json dict from the preprocessor.

    Returns
    -------
    (task_type, target_column)  — target_column is None for unsupervised.
    """
    task_type = str(cfg.get("task_type", "")).lower().strip()
    if task_type not in {"classification", "regression", "unsupervised"}:
        # Unrecognised or missing — treat as missing so inference takes over.
        task_type = ""

    # Resolve target column (preprocessor may use either key)
    target_col = (
        cfg.get("target_column")
        or cfg.get("target_col")
        or None
    )
    if isinstance(target_col, str):
        target_col = target_col.strip() or None

    # --- Unsupervised ---
    if task_type == "unsupervised":
        return "unsupervised", None

    # --- Supervised: validate target exists ---
    if task_type in {"classification", "regression"} and target_col is not None:
        if target_col not in df.columns:
            raise ValueError(
                f"Config specifies target_column='{target_col}' "
                f"but that column does not exist in the uploaded dataframe. "
                f"Available columns: {df.columns.tolist()}"
            )
        return task_type, target_col

    # Config has a supervised task_type but no target — fall through to inference.
    if task_type in {"classification", "regression"}:
        return task_type, None   # caller will infer the target

    # task_type was empty / unrecognised
    return "", None


def build_routing_decision_from_config(
    df: pd.DataFrame,
    target_col: Optional[str],
    task_type: str,
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build the routing dict for SupervisedEngine, honouring preprocessor config.

    Uses `excluded_id_cols`, `dataset_modality`, `language_profile`, and
    `col_types` from the config when available, instead of re-inferring.

    Parameters
    ----------
    df         : Uploaded dataframe.
    target_col : Resolved target column name.
    task_type  : 'classification' or 'regression'.
    cfg        : Parsed config.json dict.
    """
    # Columns to exclude from features
    excluded_id    = list(cfg.get("excluded_id_cols", []) or [])
    excluded_empty = list(cfg.get("excluded_empty_cols", []) or [])
    excluded       = set(excluded_id + excluded_empty)
    if target_col:
        excluded.add(target_col)

    # Honour modality from config; fall back to inferring.
    dataset_modality = str(cfg.get("dataset_modality", "tabular")).lower().strip()
    if dataset_modality not in {"tabular", "text_heavy", "bilingual"}:
        dataset_modality = "tabular"

    # Language profile
    lang_profile = cfg.get("language_profile", {}) or {}
    if not isinstance(lang_profile, dict):
        lang_profile = {}
    lang = (
        lang_profile.get("dominant_language")
        or lang_profile.get("dominant")
        or "english"
    )

    # Feature columns — everything not excluded
    feature_cols = [c for c in df.columns if c not in excluded]

    # Typed column lists
    col_types = cfg.get("col_types", {}) or {}  # optional per-column type hints
    numeric_cols:   List[str] = []
    categorical_cols: List[str] = []
    datetime_cols:  List[str] = []
    text_cols:      List[str] = []

    if col_types:
        for col in feature_cols:
            ctype = str(col_types.get(col, "")).lower()
            if ctype in {"numeric", "float", "int", "integer"}:
                numeric_cols.append(col)
            elif ctype in {"datetime", "date", "time"}:
                datetime_cols.append(col)
            elif ctype in {"text", "free_text", "nlp"}:
                text_cols.append(col)
            elif ctype in {"categorical", "cat", "object", "string"}:
                categorical_cols.append(col)
            # Unknown types are silently omitted — the supervised engine handles them.
    else:
        # No col_types in config — infer from dtypes (same as build_routing_decision)
        feat_df        = df[feature_cols]
        numeric_cols   = feat_df.select_dtypes(include=[np.number]).columns.tolist()
        object_cols    = feat_df.select_dtypes(include=["object", "category"]).columns.tolist()
        datetime_cols  = [c for c in feature_cols if "date" in c.lower() or "time" in c.lower()]
        text_cols      = _text_columns(df, object_cols)
        categorical_cols = [c for c in object_cols if c not in text_cols]

    # For text-heavy modality, pick the primary text column.
    routed_text_cols: List[str] = []
    if dataset_modality in {"text_heavy", "bilingual"} and text_cols:
        routed_text_cols = [text_cols[0]]

    return {
        "task_type":              task_type,
        "target_column":         target_col,
        "text_columns":          routed_text_cols,
        "numeric_columns":       numeric_cols,
        "categorical_columns":   [c for c in categorical_cols if c not in routed_text_cols],
        "datetime_columns":      datetime_cols,
        "identifier_like_columns": excluded_id,
        "dataset_modality":      dataset_modality,
        "language_profile":      {"dominant_language": lang},
    }


# =============================================================================
# Internal inference helpers  (used when no config.json is supplied)
# =============================================================================

def _looks_like_id_column(name: str, series: pd.Series) -> bool:
    lname    = name.lower().strip()
    id_terms = ["id", "uuid", "guid", "ticket", "incident", "request", "serial", "key", "code"]
    if any(t == lname or lname.endswith("_" + t) or lname.startswith(t + "_") for t in id_terms):
        return True
    # Exclude counter/aggregate/derived columns that make poor targets
    count_terms = [
        "total_", "_total", "count_", "_count", "num_", "_num",
        "assignment", "index", "timestamp", "created_at", "updated_at",
        "_date", "_time", "_year", "_month", "_day", "_hour", "_dow",
    ]
    if any(t in lname for t in count_terms):
        return True
    n      = len(series)
    nuniq  = series.nunique(dropna=True)
    return n >= 20 and nuniq / max(n, 1) > 0.95 and ("id" in lname or "number" in lname or lname == "no")


def _text_columns(df: pd.DataFrame, candidate_cols: List[str]) -> List[str]:
    out: List[str] = []
    for col in candidate_cols:
        s = df[col].dropna().astype(str)
        if s.empty:
            continue
        avg_len      = float(s.str.len().mean())
        unique_ratio = float(s.nunique() / max(len(s), 1))
        if avg_len >= 35 and unique_ratio >= 0.30:
            out.append(col)
    return out


def infer_target_column(df: pd.DataFrame, explicit_target: Optional[str] = None) -> Optional[str]:
    """
    Infer a target column for supervised learning from df column names/content.
    Supports Arabic, English, and mixed column names.
    Returns None when no convincing target is found (routes to unsupervised).
    Only called when NO config.json is uploaded.
    """
    if explicit_target and explicit_target in df.columns:
        return explicit_target

    # ── Arabic + English exact-match keywords ──────────────────────────────
    exact_priority_en = [
        "target", "label", "class", "y", "output", "result", "outcome",
        "severity", "status", "decision", "root_cause", "root cause",
        "category", "prediction_target", "dependent_variable",
    ]
    exact_priority_ar = [
        "الهدف", "هدف", "التصنيف", "تصنيف", "الفئة", "فئة",
        "النتيجة", "نتيجة", "الحالة", "حالة", "القرار", "قرار",
        "المخرج", "مخرج", "الناتج", "ناتج", "التوقع", "توقع",
        "الدرجة", "درجة", "المستوى", "مستوى", "الخطورة", "خطورة",
        "التشخيص", "تشخيص", "الحكم", "حكم", "النوع", "نوع",
        "السعر", "سعر", "الربح", "ربح", "المبيعات", "مبيعات",
    ]
    lower_map = {c.lower().strip().replace(" ", "_"): c for c in df.columns}

    for key in exact_priority_en:
        norm = key.replace(" ", "_")
        if norm in lower_map:
            return lower_map[norm]

    # Arabic exact match (strip spaces)
    col_stripped = {c.strip().replace(" ", ""): c for c in df.columns}
    for key in exact_priority_ar:
        k = key.replace(" ", "")
        if k in col_stripped:
            return col_stripped[k]

    # ── English keyword partial match ──────────────────────────────────────
    keyword_priority_en = [
        "target", "label", "outcome", "result", "class", "severity", "status",
        "score", "rating", "grade", "risk", "price", "cost", "sales",
        "revenue", "profit", "amount", "total", "duration", "resolution_time",
        "sla", "delay", "failure", "root_cause",
        # domain-specific common targets
        "graduated", "churn", "default", "fraud", "survived", "survival",
        "diagnosis", "disease", "sentiment", "satisfaction", "approved",
        "promoted", "hired", "passed", "failed", "dropout", "converted",
        "purchased", "clicked", "subscribed", "cancelled", "renewed",
        "readmitted", "recurrence", "attrition", "complaint", "resolved",
    ]
    for kw in keyword_priority_en:
        for col in df.columns:
            lname = col.lower().replace(" ", "_")
            if kw in lname and not _looks_like_id_column(col, df[col]):
                if df[col].nunique(dropna=True) < len(df) * 0.98:
                    return col

    # ── Arabic keyword partial match ───────────────────────────────────────
    keyword_priority_ar = [
        "هدف", "تصنيف", "فئة", "نتيجة", "حالة", "قرار", "مخرج",
        "درجة", "مستوى", "خطورة", "تشخيص", "نوع", "سعر", "ربح",
        "مبيع", "إجمالي", "مجموع", "تقييم", "قيمة", "ناتج",
    ]
    for kw in keyword_priority_ar:
        for col in df.columns:
            cname = col.strip().replace(" ", "")
            if kw in cname and not _looks_like_id_column(col, df[col]):
                if df[col].nunique(dropna=True) < len(df) * 0.98:
                    return col

    # ── Last resort: scan all columns for best target candidate ──────────
    # Prefer columns that look like binary/categorical outcome variables
    # Avoid: _missing, _flag, _is_*, _year, _month, _day, _dow, _hour columns
    _EXCLUDE_SUFFIXES = (
        '_missing', '_flag', '_is_weekend', '_year', '_month',
        '_day', '_hour', '_dow', '_is_', '_encoded', '_label_enc',
    )
    candidates = []
    for col in df.columns:
        lname = col.lower()
        # skip ID-like, datetime-derived, and flag columns
        if _looks_like_id_column(col, df[col]):
            continue
        if any(lname.endswith(s) or s in lname for s in _EXCLUDE_SUFFIXES):
            continue
        nu = df[col].nunique(dropna=True)
        n  = len(df)
        # Good target: low cardinality, at least 2 classes, not all same
        if 2 <= nu <= max(50, int(n * 0.1)):
            # score: prefer binary (nu=2), categorical, then low-card numeric
            is_cat = df[col].dtype == object or str(df[col].dtype) in ('category', 'string')
            score = (2 if nu == 2 else 1) + (2 if is_cat else 0)
            candidates.append((score, col))

    if candidates:
        candidates.sort(key=lambda x: -x[0])
        return candidates[0][1]

    return None


def infer_task_type(df: pd.DataFrame, target_col: str) -> str:
    """Infer classification vs regression from target column distribution."""
    s           = df[target_col].dropna()
    if s.empty:
        return "classification"
    numeric     = pd.to_numeric(s, errors="coerce")
    num_ratio   = numeric.notna().mean()
    nunique     = s.nunique(dropna=True)
    n           = len(s)
    if num_ratio >= 0.95 and nunique > max(20, int(0.15 * n)):
        return "regression"
    return "classification"


def build_routing_decision(df: pd.DataFrame, target_col: str, task_type: str) -> Dict[str, Any]:
    """
    Build the routing dict for SupervisedEngine using purely internal inference.
    Only called when no config.json is available.
    """
    id_cols      = [c for c in df.columns if c != target_col and _looks_like_id_column(c, df[c])]
    feature_cols = [c for c in df.columns if c != target_col and c not in id_cols]
    feat_df      = df[feature_cols]
    numeric_cols = feat_df.select_dtypes(include=[np.number]).columns.tolist()
    object_cols  = feat_df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    datetime_cols = [c for c in feature_cols if "date" in c.lower() or "time" in c.lower()]
    text_cols     = _text_columns(df, object_cols)

    dataset_modality  = "tabular"
    routed_text_cols: List[str] = []
    if task_type == "classification" and text_cols:
        longest = max(text_cols, key=lambda c: df[c].dropna().astype(str).str.len().mean())
        avg_len = df[longest].dropna().astype(str).str.len().mean()
        if avg_len >= 50 and len(numeric_cols) <= 5:
            dataset_modality = "text_heavy"
            routed_text_cols = [longest]

    lang = "english"
    # Check Arabic in text columns first
    if routed_text_cols:
        sample = " ".join(df[routed_text_cols[0]].dropna().astype(str).head(50).tolist())
        if re.search(r"[\u0600-\u06FF]", sample):
            lang = "arabic"
    else:
        # Also check ALL object columns for Arabic — handles tabular Arabic datasets
        all_text = " ".join(
            df[object_cols].fillna("").astype(str).values.flatten()[:500].tolist()
        ) if object_cols else ""
        if re.search(r"[\u0600-\u06FF]", all_text):
            lang = "arabic"

    return {
        "task_type":               task_type,
        "target_column":          target_col,
        "text_columns":           routed_text_cols,
        "numeric_columns":        numeric_cols,
        "categorical_columns":    [c for c in object_cols if c not in routed_text_cols],
        "datetime_columns":       datetime_cols,
        "identifier_like_columns": id_cols,
        "dataset_modality":       dataset_modality,
        "language_profile":       {"dominant_language": lang},
    }


# =============================================================================
# Visualization payload compatibility helpers
# =============================================================================

def normalize_feature_importance(raw: Any) -> List[Dict[str, Any]]:
    """
    Accept any of the three feature-importance formats used in Basira engines
    and return a unified list that both old and new frontend adapters understand.

    Accepted key names: impact_pct | impact | importance
    """
    items = raw if isinstance(raw, list) else []
    out: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        val = item.get("impact_pct", item.get("impact", item.get("importance", 0)))
        try:
            val = float(val)
        except Exception:
            val = 0.0
        if not math.isfinite(val):
            val = 0.0
        out.append({
            **item,
            "feature":    str(item.get("feature", item.get("name", "unknown"))),
            "impact":     val,
            "impact_pct": val,
            "importance": float(item.get("importance", val) or val),
        })
    return out


def build_preview(df: pd.DataFrame, n: int = 20) -> List[Dict[str, Any]]:
    return json_safe(df.head(n).where(pd.notna(df.head(n)), None).to_dict(orient="records"))


def insight_cards_from_result(insight_result: Any) -> List[Dict[str, Any]]:
    """
    Bridge new InsightResult.insights format → old frontend advanced_insights format.
    Also preserves all new fields so the new frontend adapters also work.
    """
    data  = result_to_dict(insight_result)
    cards = []
    for ins in data.get("insights", [])[:8]:
        metric_values = ins.get("metric_values") or {}
        first_metric  = (
            next(iter(metric_values.values()), None)
            if isinstance(metric_values, dict)
            else None
        )
        cards.append({
            # Old format keys
            "id":     ins.get("id", "insight"),
            "title":  ins.get("title", "Insight"),
            "value":  str(first_metric if first_metric is not None
                         else ins.get("severity", "info")).upper(),
            "metric": ins.get("layer", ""),
            "desc":   ins.get("narrative", ins.get("desc", "")),
            "action": ins.get("recommended_action", ins.get("action", "")),
            # New format keys (kept alongside for completeness)
            "severity":          ins.get("severity", "info"),
            "layer":             ins.get("layer", ""),
            "narrative":         ins.get("narrative", ""),
            "evidence":          ins.get("evidence", {}),
            "metric_values":     metric_values,
            "recommended_action": ins.get("recommended_action", ""),
        })
    return cards


def rca_report_legacy(rca_result: Any) -> List[Dict[str, Any]]:
    """
    Bridge new RCAResult.findings format → old rca_report list format.
    Each entry keeps both old and new fields.
    """
    data   = result_to_dict(rca_result)
    legacy = []
    for f in data.get("findings", []):
        chain = f.get("causal_chain") or []
        entry = {
            # Old keys
            "id":             f.get("id", ""),
            "title":          f.get("title", "Finding"),
            "severity":       str(f.get("severity", "info")).upper(),
            "causes":         chain if chain else [f.get("explanation", "")],
            "recommendation": f.get("recommended_action", ""),
        }
        # Merge all new-format fields on top (without losing old keys).
        for k, v in f.items():
            entry.setdefault(k, v)
        legacy.append(entry)
    return legacy


def build_decision_narrative(
    strategy: str,
    model_result: Any,
    insight_result: Any,
    rca_result: Any,
) -> Dict[str, Any]:
    """Build the old-style decision_narrative dict consumed by the frontend."""
    insight_data = result_to_dict(insight_result)
    rca_data     = result_to_dict(rca_result)
    summary      = insight_data.get("narrative_summary", "")

    if strategy == "supervised":
        headline    = f"Best model: {getattr(model_result, 'best_model_name', 'Unknown')}"
        key         = (
            f"Task: {getattr(model_result, 'task_type', 'supervised')} | "
            f"Target: {getattr(model_result, 'target_column', 'target')}"
        )
        reliability = getattr(model_result, "reliability_report", {}) or {}
        risk        = reliability.get("level", "")
        action      = (
            reliability.get("recommended_next_step")
            or (rca_data.get("priority_actions") or [""])[0]
        )
    else:
        headline    = f"Best clustering: {getattr(model_result, 'best_algorithm', 'Unknown')}"
        key         = f"Discovered {getattr(model_result, 'best_n_clusters', 0)} clusters"
        quality     = getattr(model_result, "cluster_quality_report", {}) or {}
        risk        = quality.get("level", "")
        action      = (rca_data.get("priority_actions") or ["Review cluster profiles and anomaly findings."])[0]

    return {
        "headline":           headline,
        "summary":            summary,
        "key_finding":        key,
        "recommended_action": action or "Review Basira insight and RCA cards before operational use.",
        "risk_alert":         f"Quality/Reliability level: {risk}" if risk else "Review generated warnings before deployment.",
    }


def enrich_chart_recommendations(
    strategy: str,
    model_result: Any,
    rca_result: Any,
    insight_result: Any,
) -> List[Dict[str, Any]]:
    """
    Take the chart recommendations already produced by the model engine and
    optionally prepend/append extra charts from charts_engine helpers.
    Deduplicates by chart id, caps at 10 charts.
    """
    recs: List[Dict[str, Any]] = list(getattr(model_result, "chart_recommendations", []) or [])

    if charts_engine is not None:
        try:
            if strategy == "supervised":
                if hasattr(charts_engine, "build_model_leaderboard_chart"):
                    extra = charts_engine.build_model_leaderboard_chart(
                        getattr(model_result, "cv_results", [])
                    )
                    if extra:
                        recs.insert(0, extra)

                if hasattr(charts_engine, "build_confusion_matrix_chart"):
                    cm     = getattr(model_result, "confusion_matrix", None)
                    labels = getattr(model_result, "label_classes", None)
                    if cm and labels:
                        extra = charts_engine.build_confusion_matrix_chart(cm, labels)
                        if extra:
                            recs.append(extra)

                # Actual vs predicted and residuals (regression)
                task_type_from_result = getattr(model_result, "task_type", "")
                rca_ready = getattr(model_result, "rca_ready_payload", {}) or {}
                if task_type_from_result == "regression" and hasattr(charts_engine, "build_actual_vs_predicted_chart"):
                    error_cases = rca_ready.get("error_cases", [])
                    target_lbl  = getattr(model_result, "target_column", "target")
                    if error_cases:
                        extra = charts_engine.build_actual_vs_predicted_chart(error_cases, target_lbl)
                        if extra:
                            recs.append(extra)
                if task_type_from_result == "regression" and hasattr(charts_engine, "build_residuals_chart"):
                    error_cases = rca_ready.get("error_cases", [])
                    if error_cases:
                        extra = charts_engine.build_residuals_chart(error_cases)
                        if extra:
                            recs.append(extra)

                # Class distribution (classification)
                if task_type_from_result == "classification" and hasattr(charts_engine, "build_class_distribution_chart"):
                    target_sum = rca_ready.get("target_summary", {})
                    if target_sum:
                        extra = charts_engine.build_class_distribution_chart(target_sum)
                        if extra:
                            recs.append(extra)

            else:  # unsupervised
                if hasattr(charts_engine, "build_cluster_profile_chart"):
                    extra = charts_engine.build_cluster_profile_chart(
                        getattr(model_result, "cluster_profiles", [])
                    )
                    if extra:
                        recs.insert(0, extra)

                if hasattr(charts_engine, "build_anomaly_chart"):
                    extra = charts_engine.build_anomaly_chart(
                        getattr(model_result, "anomaly_report", {})
                    )
                    if extra:
                        recs.append(extra)

            # Shared extras (both strategies)
            if hasattr(charts_engine, "build_rca_chart"):
                findings = result_to_dict(rca_result).get("findings", [])
                extra    = charts_engine.build_rca_chart(findings)
                if extra:
                    recs.append(extra)

            if hasattr(charts_engine, "build_insight_cards_chart"):
                insights_list = result_to_dict(insight_result).get("insights", [])
                extra         = charts_engine.build_insight_cards_chart(insights_list)
                if extra:
                    recs.append(extra)

        except Exception:
            # Never let optional chart enrichment break the main pipeline.
            pass

    # Deduplicate, fill defaults, make JSON-safe.
    cleaned: List[Dict[str, Any]] = []
    seen: set = set()
    for rec in recs:
        if not isinstance(rec, dict):
            continue
        rec = dict(rec)
        rid = rec.get("id") or rec.get("title") or f"chart_{len(cleaned)}"
        if rid in seen:
            continue
        seen.add(rid)
        rec.setdefault("id",          rid)
        rec.setdefault("type",        "bar")
        rec.setdefault("priority",    "medium")
        rec.setdefault("editable",    True)
        rec.setdefault("chartData",   rec.get("data_source", "impact"))
        rec.setdefault("data_source", rec.get("chartData", "impact"))
        cleaned.append(json_safe(rec))

    return cleaned[:10]


def build_unified_payload(
    strategy: str,
    model_result: Any,
    rca_result: Any,
    insight_result: Any,
    df: pd.DataFrame,
    uploaded_path: Path,
    predictions_or_assignments: Optional[Dict[str, Any]] = None,
    preprocessor_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Assemble the final unified JSON payload for the visualization layer.

    Includes both new pipeline fields and old frontend-compatibility fields so
    either version of basira_analysis_engine.html can render the response.
    """
    model_dict   = result_to_dict(model_result)
    rca_dict     = result_to_dict(rca_result)
    insight_dict = result_to_dict(insight_result)

    dashboard          = dict(getattr(model_result, "dashboard_payload", {}) or {})
    feature_importance = normalize_feature_importance(
        getattr(model_result, "feature_importance", [])
    )
    chart_data         = getattr(model_result, "chart_data", {}) or {}
    chart_recs         = enrich_chart_recommendations(strategy, model_result, rca_result, insight_result)

    # ── Detect UI language (from preprocessor config or column content) ───
    ui_lang = "en"
    if preprocessor_config:
        lp = preprocessor_config.get("language_profile", {}) or {}
        # preprocessor writes "dominant", bridge spec uses "dominant_language" — support both
        dl = str(lp.get("dominant_language") or lp.get("dominant") or "").lower()
        if dl in ("arabic", "ar"):
            ui_lang = "ar"
    else:
        obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
        sample = " ".join(df[obj_cols].fillna("").astype(str).values.flatten()[:300].tolist()) if obj_cols else ""
        if re.search(r"[\u0600-\u06FF]", sample):
            ui_lang = "ar"

    # ── Forecast payload ──────────────────────────────────────────────────
    forecast_payload = build_forecast_payload(df, horizon=12, lang=ui_lang)

    # ── Smart chart recommendations (data-driven, no duplicates) ──────────
    task_t = getattr(model_result, "task_type", "") if strategy == "supervised" else "unsupervised"
    smart_recs = get_smart_chart_recommendations(
        df, strategy, task_t, feature_importance, chart_recs, lang=ui_lang
    )
    # Merge: smart recs first, then engine recs, deduplicated
    all_ids = set()
    merged_recs = []
    for r in smart_recs + chart_recs:
        rid = r.get("id", r.get("title", ""))
        if rid not in all_ids:
            all_ids.add(rid)
            merged_recs.append(r)
    chart_recs = merged_recs[:10]
    dashboard["chart_recommendations"] = chart_recs

    # Ensure the dashboard_payload is rich enough for the new frontend adapters.
    dashboard.setdefault("feature_importance",     feature_importance)
    dashboard.setdefault("chart_data",             chart_data)
    dashboard.setdefault("chart_recommendations",  chart_recs)
    dashboard.setdefault("insights",               insight_dict.get("insights", []))
    dashboard.setdefault("narrative",              insight_dict.get("narrative_summary", ""))
    dashboard.setdefault("reliability",            getattr(model_result, "reliability_report", {}))
    dashboard.setdefault("best_model",             getattr(model_result, "best_model_name", None))
    dashboard.setdefault("best_algorithm",         getattr(model_result, "best_algorithm", None))

    pred_rows   = []
    assign_rows = []
    if predictions_or_assignments:
        pred_rows   = list(predictions_or_assignments.get("predictions", []) or [])
        assign_rows = list(predictions_or_assignments.get("assignments", []) or [])

    # Config provenance metadata
    cfg_used        = preprocessor_config is not None
    cfg_task_type   = str(preprocessor_config.get("task_type", ""))  if cfg_used else None
    cfg_target_col  = (
        preprocessor_config.get("target_column") or preprocessor_config.get("target_col")
    ) if cfg_used else None

    payload: Dict[str, Any] = {
        "status":        "success",
        "bridge_version": BRIDGE_VERSION,
        "strategy":      strategy,
        "task_type":     getattr(model_result, "task_type", None) if strategy == "supervised" else "unsupervised",
        "target_column": getattr(model_result, "target_column", None) if strategy == "supervised" else None,
        "uploaded_file": str(uploaded_path.name),
        "n_rows":        int(len(df)),
        "n_columns":     int(len(df.columns)),
        "ui_lang":       ui_lang,

        # ── Forecast ──────────────────────────────────────────────────────
        "forecast":      forecast_payload,

        # Config provenance (required by specification)
        "preprocessor_config_used": cfg_used,
        "config_task_type":         cfg_task_type,
        "config_target_column":     cfg_target_col,

        # ── New final pipeline fields ──────────────────────────────────────
        "dashboard_payload":   dashboard,
        "rca_result":          rca_dict,
        "insight_result":      insight_dict,
        "chart_data":          chart_data,
        "chart_recommendations": chart_recs,
        "feature_importance":  feature_importance,
        "model_result":        model_dict,

        # ── Old visualization compatibility fields ─────────────────────────
        "xai_report":          feature_importance,
        "advanced_insights":   insight_cards_from_result(insight_result),
        "decision_narrative":  build_decision_narrative(strategy, model_result, insight_result, rca_result),
        "rca_report":          _translate_rca_findings(rca_report_legacy(rca_result), ui_lang),
        "preview":             build_preview(df),
        "data_preview":        build_preview(df),
        "predictions":              pred_rows,
        "assigned_clusters":        assign_rows,
        "cluster_assignments":      assign_rows,
        "predictions_warnings":     (predictions_or_assignments.get("warnings", []) if predictions_or_assignments else []),

        # ── Helpful metadata ───────────────────────────────────────────────
        "model_performance": {
            "best_model":     getattr(model_result, "best_model_name",      None),
            "best_algorithm": getattr(model_result, "best_algorithm",       None),
            "metrics":        getattr(model_result, "test_metrics",          None),
            "reliability":    getattr(model_result, "reliability_report",    None),
            "quality":        getattr(model_result, "cluster_quality_report", None),
        },
        "warnings": (
            list(getattr(model_result,   "warnings", []) or [])
            + list(getattr(rca_result,   "warnings", []) or [])
            + list(getattr(insight_result, "warnings", []) or [])
        ),
    }
    return json_safe(payload)


# =============================================================================
# Main pipeline coordinator
# =============================================================================

def run_basira_pipeline(
    df: pd.DataFrame,
    uploaded_path: Path,
    explicit_target: Optional[str]    = None,
    explicit_task_type: Optional[str] = None,
    force_strategy: Optional[str]     = None,
    preprocessor_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run the full Basira analytical pipeline and return a unified visualization payload.

    Priority order for strategy / target resolution
    ------------------------------------------------
    1. force_strategy == 'unsupervised'   → unsupervised, no target.
    2. explicit_target + explicit_task_type in request form → use them.
    3. preprocessor_config (config.json)  → use its task_type & target_column.
    4. Internal inference                 → infer from df column names/content.

    Parameters
    ----------
    df                  : Cleaned / model-ready dataframe from the upload.
    uploaded_path       : Path where the uploaded file was saved.
    explicit_target     : target_column from the HTTP form/query string.
    explicit_task_type  : task_type from the HTTP form/query string.
    force_strategy      : 'supervised' | 'unsupervised' override.
    preprocessor_config : Parsed config.json from the Basira preprocessor.
    """
    run_id = datetime.now().strftime("basira_%Y%m%d_%H%M%S")

    # ──────────────────────────────────────────────────────────────────────
    # Step 1: Determine strategy (force_strategy wins unconditionally)
    # ──────────────────────────────────────────────────────────────────────
    if force_strategy == "unsupervised":
        return _run_unsupervised_pipeline(
            df, uploaded_path, run_id,
            preprocessor_config=preprocessor_config,
        )

    # ──────────────────────────────────────────────────────────────────────
    # Step 2: Explicit request parameters take priority over config
    # ──────────────────────────────────────────────────────────────────────
    resolved_target    = None
    resolved_task_type = None

    if explicit_target and explicit_target in df.columns:
        resolved_target    = explicit_target
        resolved_task_type = (
            explicit_task_type
            if explicit_task_type in {"classification", "regression"}
            else infer_task_type(df, resolved_target)
        )

    # ──────────────────────────────────────────────────────────────────────
    # Step 3: Config.json (preprocessor output)
    # ──────────────────────────────────────────────────────────────────────
    if resolved_target is None and preprocessor_config is not None:
        cfg_task, cfg_target = resolve_task_from_config(df, preprocessor_config)
        # resolve_task_from_config raises ValueError if target_col is missing from df.

        if cfg_task == "unsupervised":
            return _run_unsupervised_pipeline(
                df, uploaded_path, run_id,
                preprocessor_config=preprocessor_config,
            )

        resolved_task_type = cfg_task or None
        resolved_target    = cfg_target  # may still be None if config had no target

        # If config had a supervised task_type but no target, infer the target.
        if resolved_target is None and resolved_task_type in {"classification", "regression"}:
            resolved_target = infer_target_column(df)
            if resolved_target is None:
                # Cannot find a target despite supervised task_type in config.
                # Fall back to unsupervised rather than crashing.
                return _run_unsupervised_pipeline(
                    df, uploaded_path, run_id,
                    preprocessor_config=preprocessor_config,
                )

    # ──────────────────────────────────────────────────────────────────────
    # Step 4: Pure inference (no config, no explicit params)
    # ──────────────────────────────────────────────────────────────────────
    if resolved_target is None:
        resolved_target = infer_target_column(df, explicit_target)

    if resolved_target is None:
        # No target found at all → unsupervised.
        return _run_unsupervised_pipeline(
            df, uploaded_path, run_id,
            preprocessor_config=preprocessor_config,
        )

    if resolved_task_type not in {"classification", "regression"}:
        resolved_task_type = infer_task_type(df, resolved_target)

    print(f"[bridge] Strategy=supervised, target={resolved_target}, task={resolved_task_type}")
    return _run_supervised_pipeline(
        df, uploaded_path, run_id,
        target_col=resolved_target,
        task_type=resolved_task_type,
        preprocessor_config=preprocessor_config,
    )


# =============================================================================
# Private pipeline runners
# =============================================================================

def _run_supervised_pipeline(
    df: pd.DataFrame,
    uploaded_path: Path,
    run_id: str,
    target_col: str,
    task_type: str,
    preprocessor_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute supervised engine → RCA → Insight and return unified payload."""
    print(f"[bridge] _run_supervised_pipeline: target={target_col}, task={task_type}, rows={len(df)}")

    # Build routing — use config fields when available, otherwise infer.
    if preprocessor_config is not None:
        routing = build_routing_decision_from_config(df, target_col, task_type, preprocessor_config)
    else:
        routing = build_routing_decision(df, target_col, task_type)

    # ── Model ──
    supervised = SupervisedEngine(routing, output_name=f"{run_id}_supervised").run(df)

    # ── RCA ──
    # Prefer rca_ready_payload (richer) over dashboard_payload.
    rca_payload = (
        getattr(supervised, "rca_ready_payload", None)
        or getattr(supervised, "dashboard_payload", {})
        or {}
    )
    rca = RCAEngine(output_name=f"{run_id}_rca").run_from_supervised(
        rca_payload,
        raw_df=df,
    )

    # ── Insights ──
    insights = InsightEngine(output_name=f"{run_id}_insights").run_from_supervised_result(
        supervised,
        raw_df=df,
    )

    # ── Predictions on the uploaded data (best-effort; non-fatal) ──
    prediction_payload: Dict[str, Any] = {"predictions": [], "warnings": []}
    try:
        model_dir = getattr(supervised, "saved_model_dir", None)
        model_dir_path = Path(model_dir) if model_dir else None

        if not model_dir_path or not model_dir_path.exists():
            prediction_payload["warnings"].append(
                f"Model dir not found: {model_dir}. Predictions skipped."
            )
        else:
            # Build routing from saved feature_schema so pred_engine matches training exactly
            schema_path = model_dir_path / "feature_schema.json"
            if schema_path.exists():
                with open(schema_path, "r", encoding="utf-8") as _sf:
                    _saved_schema = json.load(_sf)
                # Reconstruct minimal routing from saved schema — avoids re-inference bugs
                _pred_routing = {
                    "task_type":               _saved_schema.get("task_type", routing["task_type"]),
                    "target_column":           target_col,
                    "text_columns":            _saved_schema.get("text_columns",  routing.get("text_columns", [])),
                    "numeric_columns":         _saved_schema.get("numeric_columns", routing.get("numeric_columns", [])),
                    "categorical_columns":     _saved_schema.get("categorical_columns", routing.get("categorical_columns", [])),
                    "datetime_columns":        _saved_schema.get("datetime_columns", routing.get("datetime_columns", [])),
                    "identifier_like_columns": _saved_schema.get("identifier_like_columns", []),
                    "dataset_modality":        _saved_schema.get("modality", routing.get("dataset_modality", "tabular")),
                    "language_profile":        {"dominant_language": _saved_schema.get("language", routing.get("language_profile", {}).get("dominant_language", "english"))},
                }
            else:
                _pred_routing = routing

            pred_engine = SupervisedEngine(_pred_routing, output_name="_predict_tmp")
            X_pred = df.drop(columns=[target_col], errors="ignore")
            result = pred_engine.predict(X_pred, model_dir=str(model_dir_path))

            preds = result.get("predictions", [])
            prediction_payload = {
                "predictions": preds,
                "warnings":    result.get("warnings", []),
            }
            print(f"[bridge] predict() returned {len(preds)} rows, status={result.get('status')}")
            if not preds:
                prediction_payload["warnings"].append(
                    f"predict() returned 0 rows. task_type={result.get('task_type')}, n_rows={result.get('n_rows')}"
                )
    except Exception as exc:
        import traceback as _tb
        _tstr = _tb.format_exc()
        print(f"[bridge] PREDICT EXCEPTION: {exc}")
        print(_tstr)
        prediction_payload["warnings"].append(
            f"Prediction failed: {type(exc).__name__}: {exc}"
        )
        prediction_payload["_traceback"] = _tstr

    return build_unified_payload(
        strategy               = "supervised",
        model_result           = supervised,
        rca_result             = rca,
        insight_result         = insights,
        df                     = df,
        uploaded_path          = uploaded_path,
        predictions_or_assignments = prediction_payload,
        preprocessor_config    = preprocessor_config,
    )


def _run_unsupervised_pipeline(
    df: pd.DataFrame,
    uploaded_path: Path,
    run_id: str,
    preprocessor_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute unsupervised engine → RCA → Insight and return unified payload."""

    # ── Model ──
    unsupervised = UnsupervisedEngine(output_name=f"{run_id}_unsupervised").run(df)

    # ── RCA ──
    # Prefer rca_ready_payload for richer cluster/anomaly context.
    rca_payload = (
        getattr(unsupervised, "rca_ready_payload", None)
        or getattr(unsupervised, "dashboard_payload", {})
        or {}
    )
    rca = RCAEngine(output_name=f"{run_id}_rca").run_from_unsupervised(
        rca_payload,
        raw_df=df,
    )

    # ── Insights ──
    insights = InsightEngine(output_name=f"{run_id}_insights").run_from_unsupervised_result(
        unsupervised,
        raw_df=df,
    )

    # ── Cluster assignment (best-effort; non-fatal) ──
    # Call .assign_clusters() on the SAME unsupervised instance.
    assignment_payload: Dict[str, Any] = {"assignments": [], "warnings": []}
    if getattr(unsupervised, "assignment_ready", False):
        try:
            result = unsupervised.assign_clusters(
                df,
                model_dir=unsupervised.saved_model_dir,
            )
            # assign_clusters() returns {"status", "strategy", "n_rows", "assignments", "warnings"}
            assignment_payload = {
                "assignments": result.get("assignments", []),
                "warnings":    result.get("warnings", []),
            }
        except Exception as exc:
            assignment_payload["warnings"].append(f"Cluster assignment generation failed: {exc}")
    else:
        assignment_payload["warnings"].append(
            "Selected clustering model does not support predict/assignment for new data."
        )

    return build_unified_payload(
        strategy               = "unsupervised",
        model_result           = unsupervised,
        rca_result             = rca,
        insight_result         = insights,
        df                     = df,
        uploaded_path          = uploaded_path,
        predictions_or_assignments = assignment_payload,
        preprocessor_config    = preprocessor_config,
    )


# =============================================================================
# Flask endpoints
# =============================================================================

def _serve_html(filename: str):
    """Helper: قراءة HTML مباشرة كـ Response (يتجنب مشاكل Flask 3.x send_from_directory)."""
    from flask import Response
    html_path = Path(__file__).resolve().parent / filename
    if not html_path.exists():
        return jsonify({"status": "error", "message": f"{filename} not found at: {html_path}"}), 404
    try:
        return Response(html_path.read_text(encoding="utf-8"), mimetype="text/html")
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/", methods=["GET"])
def index():
    return _serve_html("basira_analysis_engine.html")


@app.route("/analysis-engine", methods=["GET"])
def analysis_engine():
    return _serve_html("basira_analysis_engine.html")


@app.route("/chart_management.html", methods=["GET"])
def chart_management():
    return _serve_html("chart_management.html")


@app.route("/chart-management", methods=["GET"])
def chart_management_clean():
    return _serve_html("chart_management.html")




def _analysis_result_store_dir() -> Path:
    base = Path(__file__).resolve().parent
    d = base / "basira_runtime" / "analysis_results"
    d.mkdir(parents=True, exist_ok=True)
    return d


@app.route("/api/store-result", methods=["POST"])
def store_analysis_result():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        result = payload.get("result", payload)
        if isinstance(result, dict):
            result["target_column"] = result.get("target_column") or result.get("target_col")
            if result.get("target_column") and not result.get("target_col"):
                result["target_col"] = result.get("target_column")
        run_id = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        out = {"status": "success", "run_id": run_id, "source": payload.get("source", "unknown"), "result": json_safe(result)}
        (_analysis_result_store_dir() / f"{run_id}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        return jsonify({"status": "success", "run_id": run_id})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/analysis-result/<run_id>", methods=["GET"])
def get_analysis_result(run_id: str):
    safe_id = "".join(ch for ch in run_id if ch.isalnum() or ch in {"_", "-"})
    if not safe_id or safe_id != run_id:
        return jsonify({"status": "error", "message": "Invalid run_id."}), 400
    path = _analysis_result_store_dir() / f"{safe_id}.json"
    if not path.exists():
        return jsonify({"status": "error", "message": "Analysis result not found."}), 404
    return jsonify(json.loads(path.read_text(encoding="utf-8")))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":   "ok",
        "service":  "Basira Bridge Orchestrator",
        "version":  BRIDGE_VERSION,
        "pipeline": [
            "supervised_engine_F",
            "unsupervised_engine_F",
            "rca_engine_F",
            "insight_engine_F",
            "visualization_payload",
        ],
    })



@app.route("/forecast", methods=["POST"])
def forecast_endpoint():
    """Standalone forecast: accepts CSV/XLSX + horizon + lang, returns forecast JSON."""
    try:
        if "file" not in request.files:
            return jsonify({"status": "error", "message": "No file uploaded."}), 400
        df, _ = load_uploaded_dataframe(request.files["file"])
        horizon = min(max(int(request.form.get("horizon", 12)), 1), 120)
        lang    = request.form.get("lang", "en")
        result  = build_forecast_payload(df, horizon=horizon, lang=lang)
        return jsonify({"status": "success", "forecast": result})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # ── Require a data file ──────────────────────────────────────────
        if "file" not in request.files:
            return jsonify({
                "status":  "error",
                "message": "No file was uploaded under field name 'file'.",
            }), 400

        df, saved_path = load_uploaded_dataframe(request.files["file"])

        # ── Optional preprocessor config ────────────────────────────────
        # Sent by the preprocessor UI as a second multipart field "config".
        config_storage = request.files.get("config")
        preprocessor_config = load_optional_config(config_storage)

        # ── Request-level overrides (form fields / query params) ─────────
        explicit_target    = (request.form.get("target_column")
                              or request.args.get("target_column")
                              or None)
        explicit_task_type = (request.form.get("task_type")
                              or request.args.get("task_type")
                              or None)
        force_strategy     = (request.form.get("strategy")
                              or request.args.get("strategy")
                              or None)

        payload = run_basira_pipeline(
            df                  = df,
            uploaded_path       = saved_path,
            explicit_target     = explicit_target,
            explicit_task_type  = explicit_task_type,
            force_strategy      = force_strategy,
            preprocessor_config = preprocessor_config,
        )
        return jsonify(payload)

    except ValueError as exc:
        # Covers the Scenario 5 error (config target missing from df) and
        # any other user-input validation errors.
        return jsonify({
            "status":  "error",
            "message": str(exc),
        }), 422

    except (BasiraEngineError, BasiraUnsupervisedError, BasiraRCAError, BasiraInsightError) as exc:
        report = getattr(exc, "report", None)
        return jsonify({
            "status":        "error",
            "message":       str(exc),
            "engine_report": (
                json_safe(report.to_dict())
                if report is not None and hasattr(report, "to_dict")
                else None
            ),
        }), 422

    except Exception as exc:
        traceback.print_exc()
        return jsonify({
            "status":    "error",
            "message":   str(exc),
            "traceback": traceback.format_exc().splitlines()[-8:],
        }), 500


# NOTE: Entry point is at the BOTTOM of this file (after all function definitions).
# app.run() blocks — any code after it never executes.


# =============================================================================
# BASIRA ARABIC TRANSLATION LAYER — RCA + Insights
# Translates English field values to Arabic when ui_lang == "ar"
# =============================================================================

_AR_SEVERITY = {
    "critical": "حرجة", "high": "عالية", "medium": "متوسطة",
    "low": "منخفضة", "info": "معلومات",
}
_AR_CONFIDENCE = {
    "high": "عالية", "moderate": "متوسطة", "low": "منخفضة",
}
_AR_CATEGORY = {
    "model_error":       "خطأ في النموذج",
    "data_quality":      "جودة البيانات",
    "feature_signal":    "إشارة المتغير",
    "anomaly":           "شذوذ",
    "class_confusion":   "تداخل الفئات",
    "cluster_structure": "بنية التجمعات",
    "interaction":       "تفاعل المتغيرات",
    "drift":             "انجراف البيانات",
    "leakage_risk":      "خطر تسرب البيانات",
}

# Common EN→AR phrase patterns (partial match, longest first)
_AR_PHRASES: List[tuple] = [
    # Severity/confidence words inside titles
    ("Dominates the Model",              "يهيمن على النموذج"),
    ("Explain",                          "يفسّر"),
    ("Correlation",                      "ارتباط"),
    ("Potential Leakage",                "خطر تسرب محتمل"),
    ("Primary Confusion",                "تداخل رئيسي"),
    ("Structural Weakness",              "ضعف هيكلي"),
    ("Systematic",                       "منهجي"),
    ("Heteroscedastic",                  "تباين متغير"),
    ("Errors Concentrated",              "أخطاء متركزة"),
    ("Near-Zero Variance",               "تباين شبه معدوم"),
    ("Missingness",                      "قيم مفقودة"),
    ("Outlier",                          "قيمة شاذة"),
    ("Imbalanced",                       "غير متوازن"),
    ("Cluster",                          "تجمع"),
    ("Anomaly",                          "شذوذ"),
    ("Feature",                          "متغير"),
    ("Model",                            "نموذج"),
    ("Target",                           "الهدف"),
    ("Distribution",                     "توزيع"),
    ("Performance",                      "الأداء"),
]

def _translate_rca_findings(findings: List[Dict], lang: str) -> List[Dict]:
    """Translate RCA finding titles and severity labels to Arabic when lang=ar."""
    if not lang.startswith("ar"):
        return findings
    out = []
    for f in findings:
        f = dict(f)
        # severity, confidence, category labels
        f["severity_label"] = _AR_SEVERITY.get(str(f.get("severity","")).lower(), f.get("severity",""))
        f["confidence_label"] = _AR_CONFIDENCE.get(str(f.get("confidence","")).lower(), f.get("confidence",""))
        f["category_label"] = _AR_CATEGORY.get(str(f.get("category","")).lower(), f.get("category",""))
        # Translate title using phrase table
        title = f.get("title", "")
        for en, ar in _AR_PHRASES:
            title = title.replace(en, ar)
        f["title_ar"] = title
        # Add translated recommendation prefix if in English
        rec = f.get("recommended_action", "") or f.get("recommendation", "")
        f["recommendation_ar"] = _translate_recommendation(rec)
        out.append(f)
    return out


def _translate_recommendation(text: str) -> str:
    """Best-effort translation of common recommendation phrases."""
    if not text:
        return ""
    replacements = [
        ("Investigate", "تحقق من"),
        ("Consider", "ضع في اعتبارك"),
        ("Review", "راجع"),
        ("Remove", "أزل"),
        ("Drop", "احذف"),
        ("Collect more data", "اجمع بيانات أكثر"),
        ("Retrain", "أعد التدريب"),
        ("Monitor", "راقب"),
        ("Validate", "تحقق من صحة"),
        ("Use", "استخدم"),
        ("Apply", "طبّق"),
        ("Check", "تحقق من"),
        ("Ensure", "تأكد من"),
        ("before modelling", "قبل النمذجة"),
        ("before deployment", "قبل النشر"),
        ("this column", "هذا العمود"),
        ("the model", "النموذج"),
    ]
    out = text
    for en, ar in replacements:
        out = out.replace(en, ar)
    return out


def _translate_insight_cards(cards: List[Dict], lang: str) -> List[Dict]:
    """Add Arabic label fields to insight cards."""
    if not lang.startswith("ar"):
        return cards
    out = []
    for c in cards:
        c = dict(c)
        sev = str(c.get("value", "")).upper()
        sev_map = {"CRITICAL":"حرجة","HIGH":"عالية","MEDIUM":"متوسطة",
                   "LOW":"منخفضة","INFO":"معلومات"}
        c["value_ar"] = sev_map.get(sev, sev)
        title = c.get("title","")
        for en, ar in _AR_PHRASES:
            title = title.replace(en, ar)
        c["title_ar"] = title
        out.append(c)
    return out

# =============================================================================
# BASIRA FORECAST ENGINE  — Smart time-series & trend forecasting
# Detects data type automatically and picks the right forecasting method.
# =============================================================================

def _detect_forecast_capability(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Detect whether and how forecasting is possible for this dataset.
    Returns a capability dict consumed by build_forecast_payload().

    Scenarios handled:
      A) Real datetime column found          → time-series forecast
      B) Sequential integer index (row-based)→ trend projection
      C) Regression target with enough rows  → value trend
      D) None of the above                   → forecast not available
    """
    info: Dict[str, Any] = {
        "available": False,
        "mode": None,           # "timeseries" | "trend" | "value_trend"
        "date_col": None,
        "value_col": None,
        "freq": None,           # inferred pandas frequency string
        "n_points": 0,
        "numeric_cols": [],
    }

    # ── A: Real datetime columns ──────────────────────────────────────────
    date_candidates = []
    for col in df.columns:
        s = df[col]
        # Already datetime dtype
        if pd.api.types.is_datetime64_any_dtype(s):
            date_candidates.append((col, s))
            continue
        # Try parsing object columns with date-like names
        lname = col.lower().replace(" ", "_")
        date_keywords = ["date","time","month","year","week","day","period","quarter","dt","timestamp"]
        if s.dtype == object and any(k in lname for k in date_keywords):
            try:
                parsed = pd.to_datetime(s, infer_datetime_format=True, errors="coerce")
                if parsed.notna().mean() >= 0.7:
                    date_candidates.append((col, parsed))
            except Exception:
                pass

    if date_candidates:
        date_col, date_series = date_candidates[0]
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        # Choose value column: highest variance numeric col that isn't a date proxy
        value_col = None
        best_var = -1.0
        for c in numeric_cols:
            if c == date_col:
                continue
            v = float(df[c].dropna().var() or 0)
            if v > best_var:
                best_var = v
                value_col = c

        if value_col and len(df) >= 6:
            # Infer frequency
            try:
                sorted_dates = pd.to_datetime(date_series).dropna().sort_values()
                diffs = sorted_dates.diff().dropna()
                med_days = float(diffs.dt.days.median())
                if   med_days <= 1.5:  freq = "D"
                elif med_days <= 8:    freq = "W"
                elif med_days <= 32:   freq = "MS"
                elif med_days <= 95:   freq = "QS"
                else:                  freq = "YS"
            except Exception:
                freq = "MS"

            info.update({
                "available": True,
                "mode": "timeseries",
                "date_col": date_col,
                "value_col": value_col,
                "freq": freq,
                "n_points": int(df[value_col].dropna().shape[0]),
                "numeric_cols": numeric_cols,
            })
            return info

    # ── B/C: No real datetime — use sequential trend ──────────────────────
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) >= 1 and len(df) >= 8:
        # Pick highest-variance numeric column as trend target
        best_col = max(numeric_cols, key=lambda c: float(df[c].dropna().var() or 0))
        info.update({
            "available": True,
            "mode": "trend",
            "date_col": None,
            "value_col": best_col,
            "freq": None,
            "n_points": int(df[best_col].dropna().shape[0]),
            "numeric_cols": numeric_cols,
        })
    return info


def _simple_exponential_smoothing(values: List[float], alpha: float = 0.3) -> List[float]:
    """Simple exponential smoothing — no external dependencies."""
    smoothed = [values[0]]
    for v in values[1:]:
        smoothed.append(alpha * v + (1 - alpha) * smoothed[-1])
    return smoothed


def _linear_trend(values: List[float]) -> tuple:
    """OLS slope and intercept."""
    n = len(values)
    x = list(range(n))
    mx = sum(x) / n
    my = sum(values) / n
    denom = sum((xi - mx) ** 2 for xi in x)
    slope = sum((x[i] - mx) * (values[i] - my) for i in range(n)) / denom if denom else 0.0
    intercept = my - slope * mx
    return slope, intercept


def _holt_linear(values: List[float], alpha: float = 0.4, beta: float = 0.3) -> tuple:
    """Holt double exponential smoothing — returns (level, trend) for the last point."""
    l = values[0]
    b = values[1] - values[0] if len(values) > 1 else 0.0
    for v in values[1:]:
        l_prev, b_prev = l, b
        l = alpha * v + (1 - alpha) * (l_prev + b_prev)
        b = beta  * (l - l_prev) + (1 - beta) * b_prev
    return l, b


def build_forecast_payload(
    df: pd.DataFrame,
    horizon: int = 12,
    lang: str = "en",
) -> Dict[str, Any]:
    """
    Build a self-contained forecast payload for the frontend.

    Parameters
    ----------
    df      : Cleaned dataframe (from Bridge).
    horizon : Number of future steps to forecast (5 months → 60 months).
    lang    : "ar" | "en" — controls label language.

    Returns
    -------
    dict with keys:
      available, mode, labels (historical), forecast_labels (future),
      historical, forecast, lower_bound, upper_bound,
      value_col, date_col, horizon, method, lang_used,
      summary_ar, summary_en
    """
    cap = _detect_forecast_capability(df)
    is_ar = lang.startswith("ar")

    if not cap["available"]:
        return {
            "available": False,
            "reason_ar": "لا توجد بيانات كافية أو عمود زمني للتوقع",
            "reason_en": "Insufficient data or no time column for forecasting",
        }

    value_col = cap["value_col"]
    series_raw = df[value_col].dropna().tolist()
    series = [float(v) for v in series_raw if isinstance(v, (int, float)) and not (v != v)]

    if len(series) < 4:
        return {"available": False, "reason_en": "Not enough data points for forecasting."}

    # ── Smoothed historical ───────────────────────────────────────────────
    smoothed_hist = _simple_exponential_smoothing(series, alpha=0.25)

    # ── Choose forecasting method ─────────────────────────────────────────
    # Holt if there's a visible trend, otherwise simple level
    slope, intercept = _linear_trend(series)
    rel_slope = abs(slope) / (abs(np.mean(series)) + 1e-9)
    use_holt = rel_slope > 0.01   # more than 1% per-step trend

    if use_holt:
        level, trend = _holt_linear(series, alpha=0.4, beta=0.3)
        forecast_vals = [level + trend * (i + 1) for i in range(horizon)]
        method = "Holt Double Exponential Smoothing"
        method_ar = "تنعيم أسي مزدوج (هولت)"
    else:
        level = _simple_exponential_smoothing(series, alpha=0.3)[-1]
        trend = slope  # gentle drift
        forecast_vals = [level + trend * (i + 1) for i in range(horizon)]
        method = "Exponential Smoothing with Trend"
        method_ar = "تنعيم أسي مع الاتجاه"

    # ── Confidence intervals ──────────────────────────────────────────────
    residuals = [series[i] - smoothed_hist[i] for i in range(len(series))]
    std_resid = float(np.std(residuals)) if residuals else 0.0
    lower = [v - 1.645 * std_resid * (1 + 0.05 * (i + 1)) for i, v in enumerate(forecast_vals)]
    upper = [v + 1.645 * std_resid * (1 + 0.05 * (i + 1)) for i, v in enumerate(forecast_vals)]

    # ── Labels ───────────────────────────────────────────────────────────
    mode = cap["mode"]
    date_col = cap["date_col"]
    freq = cap["freq"]

    if mode == "timeseries" and date_col:
        try:
            raw_dates = pd.to_datetime(df[date_col], errors="coerce").dropna().sort_values()
            hist_labels = [str(d.date()) for d in raw_dates][-len(series):]
            last_date   = raw_dates.iloc[-1]
            future_dates = pd.date_range(start=last_date, periods=horizon + 1, freq=freq)[1:]
            fc_labels   = [str(d.date()) for d in future_dates]
        except Exception:
            hist_labels = [str(i + 1) for i in range(len(series))]
            fc_labels   = [f"+{i+1}" for i in range(horizon)]
    else:
        hist_labels = [str(i + 1) for i in range(len(series))]
        unit_ar = "خطوة"
        unit_en = "step"
        fc_labels = [f"+{i+1} {unit_en}" for i in range(horizon)]
        if is_ar:
            fc_labels = [f"+{i+1} {unit_ar}" for i in range(horizon)]

    # ── Summary narrative ─────────────────────────────────────────────────
    direction = "صاعد" if slope > 0 else ("هابط" if slope < 0 else "مستقر")
    direction_en = "upward" if slope > 0 else ("downward" if slope < 0 else "stable")
    last_val = series[-1]
    fc_end   = forecast_vals[-1]
    pct_chg  = ((fc_end - last_val) / (abs(last_val) + 1e-9)) * 100

    summary_ar = (
        f"الاتجاه العام {direction}. "
        f"القيمة الحالية {last_val:,.2f}، "
        f"والتوقع بعد {horizon} خطوة {fc_end:,.2f} "
        f"({'+' if pct_chg >= 0 else ''}{pct_chg:.1f}٪)."
    )
    summary_en = (
        f"Overall trend is {direction_en}. "
        f"Current value {last_val:,.2f}, "
        f"forecast after {horizon} steps: {fc_end:,.2f} "
        f"({'+' if pct_chg >= 0 else ''}{pct_chg:.1f}%)."
    )

    return {
        "available":       True,
        "mode":            mode,
        "value_col":       value_col,
        "date_col":        date_col,
        "freq":            freq,
        "horizon":         horizon,
        "method":          method,
        "method_ar":       method_ar,
        "labels":          hist_labels,
        "forecast_labels": fc_labels,
        "historical":      [round(v, 4) for v in series],
        "historical_smooth": [round(v, 4) for v in smoothed_hist],
        "forecast":        [round(v, 4) for v in forecast_vals],
        "lower_bound":     [round(v, 4) for v in lower],
        "upper_bound":     [round(v, 4) for v in upper],
        "summary_ar":      summary_ar,
        "summary_en":      summary_en,
        "numeric_cols":    cap["numeric_cols"],
        "n_historical":    len(series),
    }


def get_smart_chart_recommendations(
    df: pd.DataFrame,
    strategy: str,
    task_type: str,
    feature_importance: List[Dict],
    existing_recs: List[Dict],
    lang: str = "en",
) -> List[Dict[str, Any]]:
    """
    Generate smart, data-driven chart recommendations.
    Avoids repeating chart types, picks charts that suit the actual data.
    Returns up to 8 diverse, meaningful charts.
    """
    is_ar = lang.startswith("ar")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols     = df.select_dtypes(include=["object", "category"]).columns.tolist()
    n_rows       = len(df)
    recs: List[Dict] = []
    used_types: set  = set()

    def _lbl(en, ar):
        return ar if is_ar else en

    # ── 1. Feature Impact (always if we have importance) ──────────────────
    if feature_importance and "horizontalBar" not in used_types:
        fi = sorted(feature_importance, key=lambda x: -abs(x.get("impact", 0)))[:12]
        recs.append({
            "id": "smart_feature_impact",
            "type": "horizontalBar",
            "title": _lbl("Feature Impact Ranking", "ترتيب تأثير المتغيرات"),
            "reason": _lbl("Shows which features drive predictions most.", "يوضح المتغيرات الأكثر تأثيراً على التوقعات."),
            "chartData": "impact",
            "data_source": "impact",
            "labels": [f["feature"] for f in fi],
            "datasets": [{
                "label": _lbl("Impact %", "التأثير %"),
                "data":  [round(f["impact"], 2) for f in fi],
                "backgroundColor": [
                    f"rgba(14,165,233,{max(0.3, 0.95 - i * 0.06)})" for i in range(len(fi))
                ],
            }],
            "editable": True,
            "priority": "high",
        })
        used_types.add("horizontalBar")

    # ── 2. Stacked Bar: top categorical column breakdown ──────────────────
    if cat_cols and n_rows >= 10 and "stackedBar" not in used_types:
        best_cat = min(cat_cols, key=lambda c: abs(df[c].nunique() - 5))
        vc = df[best_cat].value_counts().head(10)
        if len(vc) >= 2:
            recs.append({
                "id": "smart_category_dist",
                "type": "bar",
                "title": _lbl(f"Distribution: {best_cat}", f"توزيع: {best_cat}"),
                "reason": _lbl("Shows count per category.", "يوضح العدد لكل تصنيف."),
                "labels": [str(k) for k in vc.index],
                "datasets": [{
                    "label": _lbl("Count", "العدد"),
                    "data": [int(v) for v in vc.values],
                    "backgroundColor": [
                        "rgba(99,102,241,.8)", "rgba(14,165,233,.8)", "rgba(16,185,129,.8)",
                        "rgba(245,158,11,.8)", "rgba(239,68,68,.8)", "rgba(139,92,246,.8)",
                        "rgba(20,184,166,.8)", "rgba(234,179,8,.8)", "rgba(59,130,246,.8)",
                        "rgba(251,146,60,.8)",
                    ][:len(vc)],
                }],
                "config": {"plugins": {"legend": {"display": False}}},
                "editable": True,
                "priority": "high",
                "show_values": True,
            })
            used_types.add("stackedBar")

    # ── 3. Stacked grouped bar: cat × second cat ──────────────────────────
    if len(cat_cols) >= 2 and n_rows >= 20 and "groupedBar" not in used_types:
        col_a = cat_cols[0]
        col_b = cat_cols[1] if cat_cols[1] != col_a else (cat_cols[2] if len(cat_cols) > 2 else None)
        if col_b and df[col_a].nunique() <= 8 and df[col_b].nunique() <= 6:
            crosstab = pd.crosstab(df[col_a], df[col_b])
            STACK_COLORS = ["rgba(14,165,233,.8)","rgba(139,92,246,.8)","rgba(16,185,129,.8)",
                            "rgba(245,158,11,.8)","rgba(239,68,68,.8)","rgba(99,102,241,.8)"]
            datasets = []
            for j, col_name in enumerate(crosstab.columns):
                datasets.append({
                    "label": str(col_name),
                    "data":  [int(v) for v in crosstab[col_name].values],
                    "backgroundColor": STACK_COLORS[j % len(STACK_COLORS)],
                })
            recs.append({
                "id": "smart_grouped_cat",
                "type": "bar",
                "title": _lbl(f"{col_a} × {col_b}", f"{col_a} × {col_b}"),
                "reason": _lbl("Stacked comparison across two categories.",
                               "مقارنة مجمّعة بين تصنيفين."),
                "labels": [str(i) for i in crosstab.index],
                "datasets": datasets,
                "config": {"scales": {"x": {"stacked": True}, "y": {"stacked": True}},
                           "plugins": {"legend": {"display": True}}},
                "editable": True,
                "priority": "medium",
                "show_values": True,
            })
            used_types.add("groupedBar")

    # ── 4. Numeric distribution (histogram-style bar) ─────────────────────
    if numeric_cols and "histogram" not in used_types:
        col = numeric_cols[0]
        series = df[col].dropna()
        if len(series) >= 10:
            bins = min(12, max(5, int(len(series) ** 0.5)))
            hist, edges = np.histogram(series, bins=bins)
            labels = [f"{edges[i]:.1f}–{edges[i+1]:.1f}" for i in range(len(hist))]
            recs.append({
                "id": "smart_histogram",
                "type": "bar",
                "title": _lbl(f"Distribution: {col}", f"توزيع: {col}"),
                "reason": _lbl("Histogram of numeric values.", "توزيع تكراري للقيم الرقمية."),
                "labels": labels,
                "datasets": [{"label": col, "data": [int(v) for v in hist],
                              "backgroundColor": "rgba(14,165,233,.7)",
                              "borderColor": "rgba(14,165,233,1)", "borderWidth": 1}],
                "config": {"plugins": {"legend": {"display": False}}},
                "editable": True,
                "priority": "medium",
            })
            used_types.add("histogram")

    # ── 5. Correlation line (two best numeric cols) ───────────────────────
    if len(numeric_cols) >= 2 and n_rows >= 15 and "scatter_corr" not in used_types:
        # Find most correlated pair
        best_pair = (numeric_cols[0], numeric_cols[1])
        best_corr = 0.0
        for i in range(min(len(numeric_cols), 6)):
            for j in range(i + 1, min(len(numeric_cols), 6)):
                try:
                    r = abs(float(df[numeric_cols[i]].corr(df[numeric_cols[j]])))
                    if r > best_corr:
                        best_corr = r
                        best_pair = (numeric_cols[i], numeric_cols[j])
                except Exception:
                    pass
        col_x, col_y = best_pair
        pairs = df[[col_x, col_y]].dropna().head(80)
        recs.append({
            "id": "smart_scatter",
            "type": "scatter",
            "title": _lbl(f"Correlation: {col_x} vs {col_y}",
                          f"الارتباط: {col_x} و{col_y}"),
            "reason": _lbl(f"Pearson r ≈ {best_corr:.2f}",
                           f"معامل ارتباط ≈ {best_corr:.2f}"),
            "labels": [],
            "datasets": [{
                "label": _lbl("Data points", "النقاط"),
                "data": [{"x": float(r[col_x]), "y": float(r[col_y])} for _, r in pairs.iterrows()],
                "backgroundColor": "rgba(99,102,241,.6)",
                "pointRadius": 4,
            }],
            "config": {
                "scales": {
                    "x": {"title": {"display": True, "text": col_x}},
                    "y": {"title": {"display": True, "text": col_y}},
                }
            },
            "editable": True,
            "priority": "medium",
        })
        used_types.add("scatter_corr")

    # ── 6. Doughnut: top categorical proportions ──────────────────────────
    if cat_cols and "doughnut" not in used_types:
        col = cat_cols[-1] if len(cat_cols) > 1 else cat_cols[0]
        vc  = df[col].value_counts().head(7)
        if 2 <= len(vc) <= 7:
            PIE_C = ["rgba(14,165,233,.85)","rgba(139,92,246,.85)","rgba(16,185,129,.85)",
                     "rgba(245,158,11,.85)","rgba(239,68,68,.85)","rgba(99,102,241,.85)","rgba(20,184,166,.85)"]
            recs.append({
                "id": "smart_doughnut",
                "type": "doughnut",
                "title": _lbl(f"Breakdown: {col}", f"تفصيل: {col}"),
                "reason": _lbl("Proportional view of categories.", "النسب النسبية لكل تصنيف."),
                "labels": [str(k) for k in vc.index],
                "datasets": [{"label": col, "data": [int(v) for v in vc.values],
                              "backgroundColor": PIE_C[:len(vc)]}],
                "config": {"plugins": {"legend": {"display": True, "position": "right"}}},
                "editable": True,
                "priority": "medium",
            })
            used_types.add("doughnut")

    # ── 7. Radar: top features comparison (classification only) ───────────
    if strategy == "supervised" and task_type == "classification" and feature_importance:
        top5 = sorted(feature_importance, key=lambda x: -abs(x.get("impact", 0)))[:6]
        if len(top5) >= 3 and "radar" not in used_types:
            recs.append({
                "id": "smart_radar",
                "type": "radar",
                "title": _lbl("Feature Profile Radar", "رادار ملف المتغيرات"),
                "reason": _lbl("Multi-axis comparison of top features.",
                               "مقارنة متعددة الأبعاد لأبرز المتغيرات."),
                "labels": [f["feature"] for f in top5],
                "datasets": [{"label": _lbl("Impact", "التأثير"),
                              "data": [round(abs(f["impact"]), 2) for f in top5],
                              "backgroundColor": "rgba(14,165,233,.2)",
                              "borderColor": "rgba(14,165,233,1)", "borderWidth": 2}],
                "config": {"plugins": {"legend": {"display": False}}},
                "editable": True,
                "priority": "medium",
            })
            used_types.add("radar")

    # ── 8. Line trend (multi-numeric over row index) ──────────────────────
    if len(numeric_cols) >= 2 and n_rows >= 10 and "line_trend" not in used_types:
        top2 = numeric_cols[:2]
        step = max(1, n_rows // 60)
        idx  = list(range(0, n_rows, step))
        recs.append({
            "id": "smart_line_trend",
            "type": "line",
            "title": _lbl("Value Trends", "اتجاهات القيم"),
            "reason": _lbl("Numeric column trends across the dataset.",
                           "اتجاهات الأعمدة الرقمية عبر البيانات."),
            "labels": [str(i + 1) for i in idx],
            "datasets": [
                {
                    "label": col,
                    "data": [round(float(v), 4) if pd.notna(v) else None
                             for v in df[col].iloc[idx].values],
                    "borderColor": "rgba(14,165,233,1)" if k == 0 else "rgba(139,92,246,1)",
                    "backgroundColor": "transparent",
                    "tension": 0.35,
                    "pointRadius": 2,
                }
                for k, col in enumerate(top2)
            ],
            "config": {"plugins": {"legend": {"display": True}}},
            "editable": True,
            "priority": "low",
        })
        used_types.add("line_trend")

    return recs[:8]



# =============================================================================
# Entry point — MUST be at the bottom so all functions above are defined first.
# app.run() blocks execution, so anything after it never gets defined.
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 72)
    print("🚀 BASIRA BRIDGE ORCHESTRATOR")
    print("   Final pipeline coordinator: Model → RCA → Insight → Visualization")
    print("=" * 72)
    print(f"\n  Health  : http://127.0.0.1:5055/health")
    print(f"  Analyze : http://127.0.0.1:5055/analyze")
    print("\n  Press Ctrl+C to stop.\n")
    app.run(host="127.0.0.1", port=5055, debug=False, threaded=True, use_reloader=False)
