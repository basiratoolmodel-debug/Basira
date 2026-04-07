# # # # # """
# # # # # ╔══════════════════════════════════════════════════════════════════╗
# # # # # ║  BASIRA — Core Intelligence Backend  v5.0                        ║
# # # # # ║  Run:  python Basira_app_structure.py  →  http://127.0.0.1:5001  ║
# # # # # ╚══════════════════════════════════════════════════════════════════╝
# # # # # """

# # # # # # ─── Standard library ─────────────────────────────────────────────────────────
# # # # # import math
# # # # # import re
# # # # # import warnings
# # # # # from datetime import timedelta
# # # # # warnings.filterwarnings("ignore")

# # # # # # ─── Scientific stack ─────────────────────────────────────────────────────────
# # # # # import numpy as np
# # # # # import pandas as pd
# # # # # from scipy import stats
# # # # # from sklearn.decomposition import PCA
# # # # # from sklearn.ensemble import IsolationForest, RandomForestRegressor
# # # # # from sklearn.model_selection import cross_val_score
# # # # # from sklearn.preprocessing import StandardScaler

# # # # # # ─── SHAP ─────────────────────────────────────────────────────────────────────
# # # # # import shap

# # # # # # ─── Flask ────────────────────────────────────────────────────────────────────
# # # # # from flask import Flask, jsonify, request, render_template , session
# # # # # from flask_cors import CORS

# # # # # # ─── NLP: loaded lazily so the server starts even without GPU / models ───────
# # # # # NLP_AVAILABLE = False
# # # # # LANG_DETECT_AVAILABLE = False

# # # # # try:
# # # # #     import torch
# # # # #     from transformers import AutoModel, AutoTokenizer
# # # # #     NLP_AVAILABLE = True
# # # # # except ImportError:
# # # # #     pass

# # # # # try:
# # # # #     from langdetect import DetectorFactory, detect as _ld_detect
# # # # #     DetectorFactory.seed = 42
# # # # #     LANG_DETECT_AVAILABLE = True
# # # # # except ImportError:
# # # # #     pass

# # # # # # ─── Web scraping libs ────────────────────────────────────────────────────────
# # # # # WEB_SCRAPE_AVAILABLE = False
# # # # # BS4_AVAILABLE = False

# # # # # try:
# # # # #     import requests as http_requests
# # # # #     WEB_SCRAPE_AVAILABLE = True
# # # # # except ImportError:
# # # # #     pass

# # # # # try:
# # # # #     from bs4 import BeautifulSoup
# # # # #     BS4_AVAILABLE = True
# # # # # except ImportError:
# # # # #     pass

# # # # # # ─── Flask app setup ──────────────────────────────────────────────────────────
# # # # # app = Flask(__name__, template_folder="templates", static_folder="static")
# # # # # app.secret_key = "basira_local_session_secret_v1"
# # # # # app.config["SESSION_COOKIE_NAME"] = "basira_local_session"
# # # # # app.config["SESSION_COOKIE_HTTPONLY"] = True
# # # # # app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# # # # # app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

# # # # # CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# # # # # @app.after_request
# # # # # def add_cors_headers(response):
# # # # #     response.headers["Access-Control-Allow-Origin"] = "*"
# # # # #     response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
# # # # #     response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
# # # # #     return response


# # # # # def _build_session_payload():
# # # # #     return {
# # # # #         "authenticated": bool(session.get("authenticated", False)),
# # # # #         "user_name": session.get("user_name", "Basira User"),
# # # # #         "session_started": session.get("session_started"),
# # # # #         "last_seen": session.get("last_seen")
# # # # #     }


# # # # # @app.route("/", methods=["GET"])
# # # # # def home():
# # # # #     return render_template("basira_app.html")


# # # # # @app.route("/api/session/bootstrap", methods=["GET"])
# # # # # def session_bootstrap():
# # # # #     """
# # # # #     Local session bootstrap.
# # # # #     Since cloud login has already happened before reaching the local app,
# # # # #     we create a local session automatically on first access.
# # # # #     """
# # # # #     if not session.get("authenticated"):
# # # # #         session.permanent = True
# # # # #         session["authenticated"] = True
# # # # #         session["user_name"] = "Basira User"
# # # # #         session["session_started"] = pd.Timestamp.utcnow().isoformat()
# # # # #         session["last_seen"] = pd.Timestamp.utcnow().isoformat()
# # # # #     else:
# # # # #         session["last_seen"] = pd.Timestamp.utcnow().isoformat()

# # # # #     return jsonify({
# # # # #         "status": "success",
# # # # #         "session": _build_session_payload()
# # # # #     })


# # # # # @app.route("/api/session/status", methods=["GET"])
# # # # # def session_status():
# # # # #     authenticated = bool(session.get("authenticated", False))

# # # # #     if authenticated:
# # # # #         session["last_seen"] = pd.Timestamp.utcnow().isoformat()

# # # # #     return jsonify({
# # # # #         "status": "success",
# # # # #         "session": _build_session_payload()
# # # # #     })


# # # # # @app.route("/api/session/ping", methods=["POST"])
# # # # # def session_ping():
# # # # #     if not session.get("authenticated"):
# # # # #         return jsonify({
# # # # #             "status": "expired",
# # # # #             "message": "Session expired."
# # # # #         }), 401

# # # # #     session.permanent = True
# # # # #     session["last_seen"] = pd.Timestamp.utcnow().isoformat()

# # # # #     return jsonify({
# # # # #         "status": "success",
# # # # #         "session": _build_session_payload()
# # # # #     })


# # # # # @app.route("/api/session/logout", methods=["POST"])
# # # # # def session_logout():
# # # # #     session.clear()
# # # # #     return jsonify({
# # # # #         "status": "success",
# # # # #         "message": "Logged out successfully."
# # # # #     })
# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  MODEL REGISTRY
# # # # # #  Load each HuggingFace model exactly once; cache by its HF model ID.
# # # # # #  This avoids re-downloading / re-loading on every request.
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # _MODEL_CACHE: dict = {}

# # # # # # Mapping: language key  →  HuggingFace model ID
# # # # # _LANG_TO_MODEL = {
# # # # #     "arabic":  "aubmindlab/bert-base-arabertv02",  # AraBERT – best for Arabic
# # # # #     "english": "roberta-base",                       # RoBERTa – best for English
# # # # #     "mixed":   "xlm-roberta-base",                  # XLM-RoBERTa – bilingual / mixed
# # # # # }


# # # # # def _load_model(lang: str):
# # # # #     """
# # # # #     Lazily load and cache a tokenizer + model pair for the given language.

# # # # #     Args:
# # # # #         lang: 'arabic' | 'english' | 'mixed'

# # # # #     Returns:
# # # # #         (tokenizer, model) tuple, or (None, None) if NLP is unavailable
# # # # #         or the download fails (e.g. no internet, disk space).
# # # # #     """
# # # # #     if not NLP_AVAILABLE:
# # # # #         return None, None

# # # # #     hf_id = _LANG_TO_MODEL.get(lang, _LANG_TO_MODEL["mixed"])

# # # # #     if hf_id not in _MODEL_CACHE:
# # # # #         try:
# # # # #             print(f"[NLP] Loading model: {hf_id} …")
# # # # #             tok   = AutoTokenizer.from_pretrained(hf_id)
# # # # #             model = AutoModel.from_pretrained(hf_id)
# # # # #             model.eval()                   # disable dropout – inference only
# # # # #             _MODEL_CACHE[hf_id] = (tok, model)
# # # # #             print(f"[NLP] Loaded: {hf_id}")
# # # # #         except Exception as exc:
# # # # #             # Graceful degradation – log the error, store None so we don't retry
# # # # #             print(f"[NLP] Could not load {hf_id}: {exc}")
# # # # #             _MODEL_CACHE[hf_id] = (None, None)

# # # # #     return _MODEL_CACHE[hf_id]


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  ARABIC TEXT NORMALISATION
# # # # # #  Applied before AraBERT / XLM-RoBERTa tokenisation to reduce vocabulary
# # # # # #  fragmentation caused by spelling variants common in Arabic text.
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # # Regex patterns compiled once for speed
# # # # # _RE_DIACRITICS = re.compile(
# # # # #     r"[\u064B-\u065F"          # Fatha, Kasra, Damma, Tanwin forms, Shadda, Sukun
# # # # #     r"\u0610-\u061A"           # Arabic extended A
# # # # #     r"\u06D6-\u06DC"           # Quranic annotation signs
# # # # #     r"\u06DF-\u06E4"           # More Quranic marks
# # # # #     r"\u06E7-\u06ED]"          # Behdini vowels
# # # # # )
# # # # # _RE_ALEF      = re.compile(r"[إأآا]")    # Four alef variants → canonical ا
# # # # # _RE_TA_MARBUTA = re.compile(r"ة")         # Ta marbuta → Ha (common spelling variant)
# # # # # _RE_TATWEEL   = re.compile(r"\u0640")    # Kashida (elongation stroke) → removed
# # # # # _RE_WS        = re.compile(r"\s+")       # Collapse multiple whitespace


# # # # # def normalise_arabic(text: str) -> str:
# # # # #     """
# # # # #     Standardise Arabic text for consistent BERT tokenisation.

# # # # #     Steps (in order):
# # # # #       1. Remove tashkeel (short vowel diacritics)
# # # # #       2. Normalise all alef variants to bare alef ا
# # # # #       3. Replace ta marbuta with ha
# # # # #       4. Remove tatweel (elongation)
# # # # #       5. Collapse whitespace
# # # # #     """
# # # # #     text = _RE_DIACRITICS.sub("", text)
# # # # #     text = _RE_ALEF.sub("ا", text)
# # # # #     text = _RE_TA_MARBUTA.sub("ه", text)
# # # # #     text = _RE_TATWEEL.sub("", text)
# # # # #     text = _RE_WS.sub(" ", text).strip()
# # # # #     return text


# # # # # # Arabic → English column-header translation table.
# # # # # # Used by auto_detect_target() so that Arabic-named columns are recognised
# # # # # # as potential prediction targets even though the keyword list is English.
# # # # # _AR_HEADER_TRANSLATE = {
# # # # #     "الهدف":    "target",  "النتيجة":  "result",   "الإيرادات": "revenue",
# # # # #     "السعر":    "price",   "التكلفة":  "cost",     "المبيعات":  "sales",
# # # # #     "الطلب":    "demand",  "الكمية":   "quantity", "المبلغ":    "amount",
# # # # #     "العائد":   "return",  "الربح":    "profit",   "الخسارة":   "loss",
# # # # #     "الإنتاج": "production","الدرجة":  "grade",    "النقاط":    "score",
# # # # #     "الراتب":   "salary",  "الدخل":    "income",   "القيمة":    "value",
# # # # #     "الإجمالي":"total",    "المعدل":   "rate",     "العدد":     "quantity",
# # # # # }


# # # # # def translate_ar_header(col: str) -> str:
# # # # #     """
# # # # #     Map a known Arabic column name to an English equivalent.
# # # # #     Returns the original string unchanged if no mapping exists.
# # # # #     """
# # # # #     return _AR_HEADER_TRANSLATE.get(normalise_arabic(col.strip()), col)


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  LANGUAGE DETECTION
# # # # # #  Combines a fast character-ratio heuristic with langdetect for accuracy.
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # _RE_ARABIC_CHARS = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+")


# # # # # def detect_text_language(text: str) -> str:
# # # # #     """
# # # # #     Detect the primary language of a single text string.

# # # # #     Strategy:
# # # # #       - Count Arabic-script chars vs Latin-script chars.
# # # # #       - If Arabic share ≥ 60%  → 'arabic'
# # # # #       - If Arabic share ≤ 15%  → 'english'  (confirmed via langdetect if available)
# # # # #       - Otherwise             → 'mixed'

# # # # #     Returns: 'arabic' | 'english' | 'mixed' | 'unknown'
# # # # #     """
# # # # #     if not isinstance(text, str) or not text.strip():
# # # # #         return "unknown"

# # # # #     ar_len  = len(_RE_ARABIC_CHARS.findall(text))
# # # # #     lat_len = len(re.findall(r"[a-zA-Z]", text))
# # # # #     total   = ar_len + lat_len

# # # # #     if total == 0:
# # # # #         return "unknown"

# # # # #     ar_ratio = ar_len / total

# # # # #     if ar_ratio >= 0.60:
# # # # #         return "arabic"
# # # # #     elif ar_ratio <= 0.15:
# # # # #         # Confirm it's actually English (not another Latin script)
# # # # #         if LANG_DETECT_AVAILABLE:
# # # # #             try:
# # # # #                 detected = _ld_detect(text)
# # # # #                 return "english" if detected == "en" else "mixed"
# # # # #             except Exception:
# # # # #                 pass
# # # # #         return "english"
# # # # #     else:
# # # # #         return "mixed"


# # # # # def detect_column_language(series: pd.Series) -> str:
# # # # #     """
# # # # #     Determine the dominant language across all non-null values in a column.
# # # # #     Samples up to 200 rows for speed.

# # # # #     Returns: 'arabic' | 'english' | 'mixed' | 'unknown'
# # # # #     """
# # # # #     texts = series.dropna().astype(str).head(200).tolist()
# # # # #     if not texts:
# # # # #         return "unknown"

# # # # #     counts = {"arabic": 0, "english": 0, "mixed": 0, "unknown": 0}
# # # # #     for t in texts:
# # # # #         counts[detect_text_language(t)] += 1

# # # # #     total = sum(counts.values())

# # # # #     # If both Arabic and English appear non-trivially → mixed
# # # # #     ar_share  = counts["arabic"]  / total
# # # # #     en_share  = counts["english"] / total
# # # # #     if ar_share >= 0.15 and en_share >= 0.15:
# # # # #         return "mixed"

# # # # #     return max(counts, key=counts.get)


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  NLP EMBEDDING ENGINE
# # # # # #  Produces mean-pooled BERT embeddings for text columns, then compresses
# # # # # #  them with PCA before appending to the numeric feature matrix.
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # def _mean_pool(last_hidden: "torch.Tensor",
# # # # #                attn_mask: "torch.Tensor") -> np.ndarray:
# # # # #     """
# # # # #     Mean-pool over the sequence dimension, ignoring [PAD] tokens.

# # # # #     Formula:
# # # # #       embedding = sum(hidden_states * mask_expanded) / sum(mask_expanded)

# # # # #     Returns: np.ndarray of shape (batch_size, hidden_dim)
# # # # #     """
# # # # #     mask_exp = attn_mask.unsqueeze(-1).float()
# # # # #     summed   = (last_hidden * mask_exp).sum(dim=1)
# # # # #     counts   = mask_exp.sum(dim=1).clamp(min=1e-9)
# # # # #     return (summed / counts).detach().numpy()


# # # # # def embed_text_column(series: pd.Series, lang: str,
# # # # #                       batch_size: int = 32,
# # # # #                       max_len:    int = 128) -> np.ndarray | None:
# # # # #     """
# # # # #     Convert a text column to a dense embedding matrix.

# # # # #     Routing logic:
# # # # #       arabic  → AraBERT   (fine-tuned on large Arabic corpus)
# # # # #       english → RoBERTa   (best single-language English BERT)
# # # # #       mixed   → XLM-RoBERTa  (trained on 100 languages, handles code-switching)

# # # # #     Processing steps:
# # # # #       1. Fill NaN with empty string
# # # # #       2. Apply Arabic normalisation for arabic/mixed columns
# # # # #       3. Tokenise in batches (avoids OOM on large datasets)
# # # # #       4. Mean-pool over token dimension → one vector per row
# # # # #       5. Replace zero-vectors (empty strings) with column mean

# # # # #     Returns: np.ndarray (n_rows, hidden_dim) or None on failure
# # # # #     """
# # # # #     if not NLP_AVAILABLE:
# # # # #         return None

# # # # #     tok, model = _load_model(lang)
# # # # #     if tok is None:
# # # # #         return None

# # # # #     import torch

# # # # #     texts = series.fillna("").astype(str).tolist()

# # # # #     # Arabic normalisation – apply to any row that contains Arabic text
# # # # #     if lang in ("arabic", "mixed"):
# # # # #         texts = [
# # # # #             normalise_arabic(t) if detect_text_language(t) in ("arabic", "mixed") else t
# # # # #             for t in texts
# # # # #         ]

# # # # #     all_embs = []

# # # # #     with torch.no_grad():
# # # # #         for start in range(0, len(texts), batch_size):
# # # # #             batch   = texts[start: start + batch_size]
# # # # #             encoded = tok(
# # # # #                 batch,
# # # # #                 padding=True,
# # # # #                 truncation=True,
# # # # #                 max_length=max_len,
# # # # #                 return_tensors="pt",
# # # # #             )
# # # # #             out  = model(**encoded)
# # # # #             embs = _mean_pool(out.last_hidden_state, encoded["attention_mask"])
# # # # #             all_embs.append(embs)

# # # # #     matrix = np.vstack(all_embs)

# # # # #     # Replace zero-rows (e.g. empty strings that produced all-zero embeddings)
# # # # #     norms     = np.linalg.norm(matrix, axis=1, keepdims=True)
# # # # #     zero_mask = (norms.flatten() == 0)
# # # # #     if zero_mask.any() and not zero_mask.all():
# # # # #         col_mean            = matrix[~zero_mask].mean(axis=0)
# # # # #         matrix[zero_mask]   = col_mean

# # # # #     return matrix


# # # # # def process_text_columns(df: pd.DataFrame) -> tuple:
# # # # #     """
# # # # #     Main NLP pipeline orchestrator.

# # # # #     Scans every non-numeric column in the DataFrame, detects its language,
# # # # #     embeds it with the appropriate BERT model, then compresses each embedding
# # # # #     block to max 8 PCA components.

# # # # #     The compressed features are column-named with the prefix [NLP] so the
# # # # #     frontend can distinguish them from raw numeric features in XAI charts.

# # # # #     Returns:
# # # # #         (text_feature_matrix, nlp_metadata)
# # # # #         text_feature_matrix: np.ndarray (n_rows, total_nlp_dims) or None
# # # # #         nlp_metadata:        dict with per-column info for the API payload
# # # # #     """
# # # # #     # Prepare metadata structure that will be returned in the API payload
# # # # #     nlp_meta = {
# # # # #         "nlp_available":         NLP_AVAILABLE,
# # # # #         "lang_detect_available": LANG_DETECT_AVAILABLE,
# # # # #         "columns_processed":     [],
# # # # #         "warning": (
# # # # #             None if NLP_AVAILABLE else
# # # # #             "NLP libraries not installed. "
# # # # #             "Install with: pip install torch transformers langdetect sentencepiece"
# # # # #         ),
# # # # #     }

# # # # #     # Identify candidate text columns:
# # # # #     #   - dtype == object (string)
# # # # #     #   - not nearly-unique (< 95% unique values) — avoids ID columns
# # # # #     #   - average value length > 3 chars — avoids single-char codes
# # # # #     text_cols = [
# # # # #         c for c in df.columns
# # # # #         if df[c].dtype == object
# # # # #         and df[c].nunique() / max(len(df), 1) < 0.95
# # # # #         and df[c].dropna().astype(str).str.len().mean() > 3
# # # # #     ]

# # # # #     if not text_cols or not NLP_AVAILABLE:
# # # # #         return None, nlp_meta

# # # # #     all_matrices     = []
# # # # #     all_feat_names   = []

# # # # #     for col in text_cols:
# # # # #         lang       = detect_column_language(df[col])
# # # # #         model_label = {
# # # # #             "arabic":  "AraBERT (bert-base-arabertv02)",
# # # # #             "english": "RoBERTa (roberta-base)",
# # # # #             "mixed":   "XLM-RoBERTa (xlm-roberta-base)",
# # # # #         }.get(lang, "XLM-RoBERTa (xlm-roberta-base)")

# # # # #         col_meta = {
# # # # #             "column":      col,
# # # # #             "language":    lang,
# # # # #             "model_used":  model_label,
# # # # #             "n_non_null":  int(df[col].notna().sum()),
# # # # #             "sample_texts":df[col].dropna().astype(str).head(3).tolist(),
# # # # #         }

# # # # #         embed = embed_text_column(df[col], lang)

# # # # #         if embed is not None and embed.shape[0] == len(df):
# # # # #             # PCA compression: at most 8 components per column.
# # # # #             # 8 dims per column means even 10 text columns only add 80 features —
# # # # #             # manageable for the RandomForest without overwhelming numeric features.
# # # # #             n_components = min(8, embed.shape[1], len(df) - 1)

# # # # #             if n_components >= 2:
# # # # #                 pca   = PCA(n_components=n_components, random_state=42)
# # # # #                 embed = pca.fit_transform(embed)
# # # # #                 col_meta["embedding_dims"]          = n_components
# # # # #                 col_meta["variance_explained_pct"]  = round(
# # # # #                     float(pca.explained_variance_ratio_.sum() * 100), 1
# # # # #                 )
# # # # #             else:
# # # # #                 col_meta["embedding_dims"]         = embed.shape[1]
# # # # #                 col_meta["variance_explained_pct"] = 100.0

# # # # #             # Feature names: [NLP]ColumnName_dim1, [NLP]ColumnName_dim2, …
# # # # #             feat_names = [f"[NLP]{col}_d{i+1}" for i in range(embed.shape[1])]
# # # # #             col_meta["feature_names"] = feat_names

# # # # #             all_matrices.append(embed)
# # # # #             all_feat_names.extend(feat_names)

# # # # #         nlp_meta["columns_processed"].append(col_meta)

# # # # #     if not all_matrices:
# # # # #         return None, nlp_meta

# # # # #     combined = np.hstack(all_matrices)
# # # # #     nlp_meta["total_nlp_features"] = combined.shape[1]
# # # # #     return combined, nlp_meta


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  NaN / Inf SANITIZER
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # def sanitize(obj):
# # # # #     """
# # # # #     Recursively replace NaN / Inf / None with safe JSON-serialisable values.
# # # # #     Must be called on the entire payload before jsonify().
# # # # #     """
# # # # #     if isinstance(obj, dict):
# # # # #         return {k: sanitize(v) for k, v in obj.items()}
# # # # #     if isinstance(obj, list):
# # # # #         return [sanitize(v) for v in obj]
# # # # #     if isinstance(obj, float):
# # # # #         return 0 if (math.isnan(obj) or math.isinf(obj)) else round(obj, 6)
# # # # #     if isinstance(obj, (np.floating, np.float32, np.float64)):
# # # # #         v = float(obj)
# # # # #         return 0 if (math.isnan(v) or math.isinf(v)) else round(v, 6)
# # # # #     if isinstance(obj, (np.integer, np.int32, np.int64)):
# # # # #         return int(obj)
# # # # #     if isinstance(obj, np.bool_):
# # # # #         return bool(obj)
# # # # #     if obj is None:
# # # # #         return 0
# # # # #     return obj


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  AUTO TARGET DETECTION
# # # # # #  Extends v4 with Arabic header translation so columns like "الهدف" or
# # # # # #  "السعر" are recognised as potential targets even though the keyword list
# # # # # #  is English.
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # def auto_detect_target(numeric_df):
# # # # #     """
# # # # #     Intelligently select the prediction target column.

# # # # #     Priority:
# # # # #       1. English keyword match in original column name
# # # # #       2. Arabic header translation then keyword match
# # # # #       3. Highest coefficient of variation (most variable → most informative)
# # # # #       4. Last column as final fallback

# # # # #     Returns (target_col: str, reason: str)
# # # # #     """
# # # # #     cols = list(numeric_df.columns)
# # # # #     if not cols:
# # # # #         return None, "No numeric columns found"

# # # # #     target_keywords = [
# # # # #         "target", "label", "output", "result", "score", "price", "cost",
# # # # #         "revenue", "sales", "demand", "value", "amount", "total", "rate",
# # # # #         "return", "profit", "loss", "yield", "production", "quantity",
# # # # #         "salary", "income", "churn", "default", "fraud", "grade",
# # # # #     ]

# # # # #     # ── Pass 1: match on original name ────────────────────────────────────────
# # # # #     for kw in target_keywords:
# # # # #         for col in cols:
# # # # #             if kw.lower() in col.lower():
# # # # #                 return col, (
# # # # #                     f"Column '{col}' matched target keyword '{kw}'. "
# # # # #                     "Confirmed as prediction target."
# # # # #                 )

# # # # #     # ── Pass 2: match after Arabic translation ─────────────────────────────────
# # # # #     for col in cols:
# # # # #         translated = translate_ar_header(col)
# # # # #         if translated != col:                # only if a translation was found
# # # # #             for kw in target_keywords:
# # # # #                 if kw.lower() in translated.lower():
# # # # #                     return col, (
# # # # #                         f"Arabic column '{col}' translated to '{translated}' "
# # # # #                         f"and matched target keyword '{kw}'."
# # # # #                     )

# # # # #     # ── Pass 3: highest coefficient of variation ───────────────────────────────
# # # # #     best_col, best_cv = None, -1.0
# # # # #     for col in cols:
# # # # #         col_data = numeric_df[col].dropna()
# # # # #         if col_data.std() == 0 or col_data.mean() == 0 or col_data.nunique() < 3:
# # # # #             continue
# # # # #         cv = abs(col_data.std() / col_data.mean())
# # # # #         if cv > best_cv:
# # # # #             best_cv, best_col = cv, col

# # # # #     if best_col:
# # # # #         return best_col, (
# # # # #             f"No target keyword found. '{best_col}' selected automatically "
# # # # #             f"(CV = {round(best_cv*100,1)}% — highest variability, most informative to predict)."
# # # # #         )

# # # # #     # ── Pass 4: fallback ───────────────────────────────────────────────────────
# # # # #     return cols[-1], f"Defaulted to last column '{cols[-1]}' as target variable."


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  SMART CHART TYPE SELECTION  (unchanged from v4 – fully preserved)
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # def detect_chart_types(df, numeric_df, feature_impact, dist_data, target_col):
# # # # #     """
# # # # #     Select optimal chart types from the extended palette based on data properties.
# # # # #     Chart types: bar, horizontalBar, doughnut, radar, polarArea, line,
# # # # #                  scatter, histogram, bubble, area
# # # # #     """
# # # # #     charts     = []
# # # # #     n_features = len(feature_impact)
# # # # #     impacts    = [f["impact"] for f in feature_impact]
# # # # #     n_rows     = len(df)
# # # # #     top_feat   = feature_impact[0]["feature"] if feature_impact else None

# # # # #     # Average absolute skewness across feature columns (excluding target)
# # # # #     skews = (
# # # # #         numeric_df.drop(columns=[target_col], errors="ignore")
# # # # #         .apply(lambda c: abs(float(stats.skew(c.dropna()))) if c.dropna().std() > 0 else 0)
# # # # #         .mean()
# # # # #     )

# # # # #     top2_sum      = sum(sorted(impacts, reverse=True)[:2]) if len(impacts) >= 2 else 0
# # # # #     is_pareto     = top2_sum > 60          # top 2 features dominate
# # # # #     high_variance = skews > 1.2            # average skewness is high
# # # # #     large_dataset = n_rows > 1000          # switch scatter → bubble above 1k rows

# # # # #     # ── Chart 1: Feature ranking bar ──────────────────────────────────────────
# # # # #     if n_features <= 7:
# # # # #         charts.append({
# # # # #             "type": "horizontalBar",
# # # # #             "title": "Feature Impact Ranking",
# # # # #             "reason": (
# # # # #                 f"Horizontal bars are optimal for {n_features} labeled features — "
# # # # #                 "labels stay fully readable without rotation."
# # # # #             ),
# # # # #             "chartData": "impact",
# # # # #         })
# # # # #     else:
# # # # #         charts.append({
# # # # #             "type": "bar",
# # # # #             "title": "Impact Magnitude Matrix",
# # # # #             "reason": (
# # # # #                 f"{n_features} features detected — vertical bar chart efficiently "
# # # # #                 "handles a wide feature space."
# # # # #             ),
# # # # #             "chartData": "impact",
# # # # #         })

# # # # #     # ── Chart 2: Composition chart ─────────────────────────────────────────────
# # # # #     if is_pareto:
# # # # #         charts.append({
# # # # #             "type": "doughnut",
# # # # #             "title": "Decision Weight Allocation",
# # # # #             "reason": (
# # # # #                 "Top 2 features dominate (>60% combined weight). "
# # # # #                 "Doughnut chart highlights this Pareto concentration clearly."
# # # # #             ),
# # # # #             "chartData": "impact",
# # # # #         })
# # # # #     elif high_variance:
# # # # #         charts.append({
# # # # #             "type": "polarArea",
# # # # #             "title": "Asymmetric Impact Distribution",
# # # # #             "reason": (
# # # # #                 "High skewness detected in feature distributions. "
# # # # #                 "Polar area chart reveals unequal radial impact spread."
# # # # #             ),
# # # # #             "chartData": "impact",
# # # # #         })
# # # # #     else:
# # # # #         charts.append({
# # # # #             "type": "doughnut",
# # # # #             "title": "Proportional Weight Map",
# # # # #             "reason": (
# # # # #                 "Balanced impact distribution — doughnut provides intuitive "
# # # # #                 "part-to-whole proportional view."
# # # # #             ),
# # # # #             "chartData": "impact",
# # # # #         })

# # # # #     # ── Chart 3: Profile chart ──────────────────────────────────────────────────
# # # # #     if 3 <= n_features <= 10:
# # # # #         charts.append({
# # # # #             "type": "radar",
# # # # #             "title": "Multi-Axis Feature Signature",
# # # # #             "reason": (
# # # # #                 f"Radar chart maps {n_features} features on a single multi-axis canvas — "
# # # # #                 "best for comparing influence patterns."
# # # # #             ),
# # # # #             "chartData": "impact",
# # # # #         })
# # # # #     else:
# # # # #         charts.append({
# # # # #             "type": "line",
# # # # #             "title": "Impact Decay Curve",
# # # # #             "reason": (
# # # # #                 "Large feature count — line chart traces the diminishing returns "
# # # # #                 "across ranked features effectively."
# # # # #             ),
# # # # #             "chartData": "impact",
# # # # #         })

# # # # #     # ── Chart 4: Distribution of primary driver ────────────────────────────────
# # # # #     if top_feat and top_feat in dist_data:
# # # # #         charts.append({
# # # # #             "type": "histogram",
# # # # #             "title": f"Distribution: {top_feat.upper()}",
# # # # #             "reason": (
# # # # #                 f"Histogram reveals how '{top_feat}' (primary driver) is distributed — "
# # # # #                 "essential for spotting skew and outlier zones."
# # # # #             ),
# # # # #             "chartData": "histogram",
# # # # #             "histFeature": top_feat,
# # # # #         })

# # # # #     # ── Chart 5: Scatter or Bubble (top 2 features) ────────────────────────────
# # # # #     if n_features >= 2:
# # # # #         f1 = feature_impact[0]["feature"]
# # # # #         f2 = feature_impact[1]["feature"]
# # # # #         if large_dataset:
# # # # #             charts.append({
# # # # #                 "type": "bubble",
# # # # #                 "title": f"Feature Interaction: {f1.upper()} × {f2.upper()}",
# # # # #                 "reason": (
# # # # #                     "Bubble chart shows the joint relationship between top 2 drivers "
# # # # #                     "and their combined SHAP magnitude — reveals interaction clusters."
# # # # #                 ),
# # # # #                 "chartData": "bubble",
# # # # #                 "feat1": f1,
# # # # #                 "feat2": f2,
# # # # #             })
# # # # #         else:
# # # # #             charts.append({
# # # # #                 "type": "scatter",
# # # # #                 "title": f"Correlation Scatter: {f1.upper()} vs {f2.upper()}",
# # # # #                 "reason": (
# # # # #                     f"Scatter exposes the raw relationship between '{f1}' and '{f2}' — "
# # # # #                     "useful for detecting clusters, non-linearity, or outliers."
# # # # #                 ),
# # # # #                 "chartData": "scatter",
# # # # #                 "feat1": f1,
# # # # #                 "feat2": f2,
# # # # #             })

# # # # #     # ── Chart 6: Cumulative impact area chart ──────────────────────────────────
# # # # #     charts.append({
# # # # #         "type": "area",
# # # # #         "title": "Cumulative Feature Contribution",
# # # # #         "reason": (
# # # # #             "Area chart shows how decision weight accumulates as you add features — "
# # # # #             "identifies the minimum set needed for 80% coverage."
# # # # #         ),
# # # # #         "chartData": "cumulative",
# # # # #     })

# # # # #     return charts


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  ROOT CAUSE ANALYSIS (fully preserved from v4)
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # def compute_rca(df, numeric_df, feature_impact, shap_values, X, y, target_col):
# # # # #     """
# # # # #     For each top feature: compute statistical profile, identify root causes,
# # # # #     and produce a prioritised plain-language recommendation paragraph.

# # # # #     Root-cause signals examined:
# # # # #       • Outlier density (IQR method)
# # # # #       • Distribution skewness
# # # # #       • Coefficient of variation (extreme variability)
# # # # #       • SHAP context-dependence (std vs mean)
# # # # #       • Linear correlation type (strong / weak / non-linear)
# # # # #       • Directional SHAP tendency (predominantly positive / negative)
# # # # #     """
# # # # #     rca_nodes    = []
# # # # #     correlations = numeric_df.corr()[target_col]
# # # # #     n_rows       = len(X)

# # # # #     # ── Pre-compute per-feature statistics ────────────────────────────────────
# # # # #     feature_stats = {}
# # # # #     for col in X.columns:
# # # # #         col_data = X[col].dropna()
# # # # #         if len(col_data) < 2:
# # # # #             continue
# # # # #         q1, q3 = float(col_data.quantile(0.25)), float(col_data.quantile(0.75))
# # # # #         iqr     = q3 - q1
# # # # #         n_out   = int(((col_data < q1 - 1.5*iqr) | (col_data > q3 + 1.5*iqr)).sum())

# # # # #         mean_v  = float(col_data.mean())
# # # # #         std_v   = float(col_data.std())

# # # # #         def _s(v, d=4):
# # # # #             """Safe round — returns 0 for NaN / Inf."""
# # # # #             return 0 if (math.isnan(v) or math.isinf(v)) else round(v, d)

# # # # #         feature_stats[col] = {
# # # # #             "mean":     _s(mean_v),
# # # # #             "std":      _s(std_v),
# # # # #             "min":      _s(float(col_data.min())),
# # # # #             "max":      _s(float(col_data.max())),
# # # # #             "skew":     _s(float(stats.skew(col_data)), 3),
# # # # #             "kurtosis": _s(float(stats.kurtosis(col_data)), 3),
# # # # #             "outliers": n_out,
# # # # #             "cv":       _s(std_v / mean_v * 100, 1) if mean_v != 0 else 0,
# # # # #         }

# # # # #     # ── Build RCA nodes ───────────────────────────────────────────────────────
# # # # #     for rank, item in enumerate(feature_impact[:6], 1):
# # # # #         feat = item["feature"]
# # # # #         if feat not in feature_stats:
# # # # #             continue

# # # # #         fs       = feature_stats[feat]
# # # # #         corr_val = round(float(correlations.get(feat, 0)), 3)
# # # # #         if math.isnan(corr_val) or math.isinf(corr_val):
# # # # #             corr_val = 0.0

# # # # #         shap_idx     = list(X.columns).index(feat)
# # # # #         shap_feat    = shap_values[:, shap_idx]
# # # # #         shap_mean    = round(float(np.mean(shap_feat)), 4)
# # # # #         shap_std     = round(float(np.std(shap_feat)), 4)
# # # # #         shap_mean    = 0 if (math.isnan(shap_mean) or math.isinf(shap_mean)) else shap_mean
# # # # #         shap_std     = 0 if (math.isnan(shap_std)  or math.isinf(shap_std))  else shap_std
# # # # #         shap_pos_pct = round(float((shap_feat > 0).sum() / max(len(shap_feat), 1) * 100), 1)

# # # # #         causes         = []
# # # # #         severity_score = 0

# # # # #         # Cause 1 – outlier density
# # # # #         if fs["outliers"] > n_rows * 0.05:
# # # # #             causes.append(
# # # # #                 f"High outlier density: {fs['outliers']} records "
# # # # #                 f"({round(fs['outliers']/n_rows*100,1)}% of data) fall outside normal range. "
# # # # #                 f"These extreme values are likely inflating this feature's apparent importance."
# # # # #             )
# # # # #             severity_score += 2

# # # # #         # Cause 2 – distribution skewness
# # # # #         if abs(fs["skew"]) > 1.5:
# # # # #             direction = "right-skewed" if fs["skew"] > 0 else "left-skewed"
# # # # #             tail      = "extreme high values" if fs["skew"] > 0 else "extreme low values"
# # # # #             causes.append(
# # # # #                 f"Distribution is {direction} (skew={fs['skew']}), with a long tail of {tail}. "
# # # # #                 f"A log-transform would likely stabilise variance and improve model reliability."
# # # # #             )
# # # # #             severity_score += 1

# # # # #         # Cause 3 – extreme variability
# # # # #         if abs(fs["cv"]) > 80:
# # # # #             causes.append(
# # # # #                 f"Extreme variability detected (CV={fs['cv']}%). "
# # # # #                 f"This feature behaves inconsistently across records and can destabilise predictions. "
# # # # #                 f"Consider grouping or binning this variable."
# # # # #             )
# # # # #             severity_score += 2

# # # # #         # Cause 4 – context-dependent SHAP
# # # # #         if shap_std > abs(shap_mean) * 1.5 and shap_mean != 0:
# # # # #             causes.append(
# # # # #                 f"Highly context-dependent influence: SHAP values vary greatly "
# # # # #                 f"(std={shap_std} vs mean={shap_mean}). "
# # # # #                 f"This feature helps some records strongly but has little or opposite effect on others — "
# # # # #                 f"suggesting important interaction effects."
# # # # #             )
# # # # #             severity_score += 1

# # # # #         # Cause 5 – linear correlation type
# # # # #         if abs(corr_val) > 0.75:
# # # # #             causes.append(
# # # # #                 f"Strong direct linear link to target (r={corr_val}). "
# # # # #                 f"This feature and the outcome move "
# # # # #                 f"{'together' if corr_val > 0 else 'in opposite directions'} almost proportionally. "
# # # # #                 f"Changes in this variable translate directly and predictably into outcome changes."
# # # # #             )
# # # # #             severity_score += 1
# # # # #         elif abs(corr_val) < 0.15:
# # # # #             causes.append(
# # # # #                 f"Weak linear correlation (r={corr_val}) yet high SHAP importance — "
# # # # #                 f"this feature influences the target through non-linear, threshold, or interaction effects. "
# # # # #                 f"Standard correlation analysis would completely miss this."
# # # # #             )
# # # # #             severity_score += 1

# # # # #         # Cause 6 – SHAP direction
# # # # #         if shap_pos_pct > 70:
# # # # #             causes.append(
# # # # #                 f"Predominantly positive effect: in {shap_pos_pct}% of records "
# # # # #                 f"it pushes the predicted outcome upward — a consistent positive lever."
# # # # #             )
# # # # #         elif shap_pos_pct < 30:
# # # # #             causes.append(
# # # # #                 f"Acts mainly as a suppressor: in {100-shap_pos_pct}% of records "
# # # # #                 f"it pulls the predicted outcome downward. "
# # # # #                 f"Managing it could help prevent negative outcomes."
# # # # #             )

# # # # #         if not causes:
# # # # #             causes.append(
# # # # #                 "Stable, consistent influence with no anomalous patterns detected. "
# # # # #                 "Contributes predictably to model decisions and can be relied upon as a stable signal."
# # # # #             )

# # # # #         # Recommendation paragraph (calibrated by importance level)
# # # # #         if item["importance_level"] == "Critical":
# # # # #             recommendation = (
# # # # #                 f"URGENT: '{feat}' is the single most powerful lever — "
# # # # #                 f"it drives {item['impact']}% of all predictions. "
# # # # #                 f"Any policy or operational decision affecting this variable will have immediate, "
# # # # #                 f"large consequences. Set up real-time monitoring, define acceptable value ranges, "
# # # # #                 f"assign ownership, and never change it without prior impact assessment."
# # # # #             )
# # # # #         elif item["importance_level"] == "High":
# # # # #             recommendation = (
# # # # #                 f"MONITOR: '{feat}' contributes {item['impact']}% to decisions. "
# # # # #                 f"Changes — especially combined with the primary driver — can significantly shift outcomes. "
# # # # #                 f"Establish monthly review thresholds and document baseline values."
# # # # #             )
# # # # #         else:
# # # # #             recommendation = (
# # # # #                 f"TRACK: '{feat}' provides {item['impact']}% of predictive weight. "
# # # # #                 f"It plays a supporting, relatively stable role. "
# # # # #                 f"Include in your standard periodic review cycle. "
# # # # #                 f"Can be de-prioritised if resource constraints arise."
# # # # #             )

# # # # #         rca_nodes.append({
# # # # #             "rank":             rank,
# # # # #             "feature":          feat,
# # # # #             "impact":           item["impact"],
# # # # #             "trend":            item["trend"],
# # # # #             "importance_level": item["importance_level"],
# # # # #             "corr_with_target": corr_val,
# # # # #             "shap_mean":        shap_mean,
# # # # #             "shap_std":         shap_std,
# # # # #             "shap_pos_pct":     shap_pos_pct,
# # # # #             "stats":            fs,
# # # # #             "root_causes":      causes,
# # # # #             "recommendation":   recommendation,
# # # # #             "severity_score":   severity_score,
# # # # #         })

# # # # #     return rca_nodes


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  ADVANCED INSIGHT CARDS (7 cards, fully preserved from v4)
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # def compute_advanced_insights(df, numeric_df, feature_impact,
# # # # #                                shap_values, X, y, target_col, model_r2):
# # # # #     """
# # # # #     Generate 7 plain-language strategic insight cards:
# # # # #       1. Model Reliability Score
# # # # #       2. Primary Decision Driver
# # # # #       3. Anomaly Detection
# # # # #       4. Decision Concentration Risk
# # # # #       5. Data Integrity Score
# # # # #       6. Target Volatility Index
# # # # #       7. Top-2 Feature Synergy
# # # # #     """
# # # # #     insights = []
# # # # #     n_rows   = len(df)
# # # # #     n_cols   = len(df.columns)

# # # # #     missing_pct = round(df.isnull().sum().sum() / (n_rows * n_cols) * 100, 1)
# # # # #     dup_rows    = int(df.duplicated().sum())
# # # # #     top         = feature_impact[0]
# # # # #     second      = feature_impact[1] if len(feature_impact) > 1 else feature_impact[0]

# # # # #     def _sf(v):
# # # # #         """Safe float — returns 0 for NaN/Inf."""
# # # # #         if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
# # # # #             return 0
# # # # #         return v

# # # # #     target_skew = _sf(round(float(stats.skew(y)), 2))
# # # # #     target_std  = _sf(round(float(y.std()), 3))
# # # # #     y_mean      = float(y.mean())
# # # # #     target_cv   = _sf(round(float(y.std() / y_mean * 100), 1)) if y_mean != 0 else 0

# # # # #     # Isolation Forest anomaly detection
# # # # #     try:
# # # # #         contamination = min(0.05, max(0.01, 1.0 / max(n_rows, 2)))
# # # # #         iso           = IsolationForest(contamination=contamination, random_state=42)
# # # # #         iso.fit(X)
# # # # #         n_anomalies = int((iso.predict(X) == -1).sum())
# # # # #     except Exception:
# # # # #         n_anomalies = 0
# # # # #     anomaly_pct  = round(n_anomalies / n_rows * 100, 1)

# # # # #     # SHAP concentration
# # # # #     total_shap  = sum(np.abs(shap_values[:, i]).mean() for i in range(X.shape[1]))
# # # # #     top3_shap   = sum(np.abs(shap_values[:, i]).mean() for i in range(min(3, X.shape[1])))
# # # # #     top3_conc   = round(top3_shap / total_shap * 100, 1) if total_shap > 0 else 0

# # # # #     inter_r     = 0.0
# # # # #     f1, f2      = top["feature"], second["feature"]
# # # # #     if f1 in X.columns and f2 in X.columns:
# # # # #         inter_r = _sf(round(float(abs(X[f1].corr(X[f2]))), 3))

# # # # #     # ── Card 1: Model reliability ──────────────────────────────────────────────
# # # # #     if model_r2 >= 80:
# # # # #         desc   = (f"The model explains {model_r2}% of outcome variation — strong predictive power. "
# # # # #                   f"Rankings and insights are reliable signals ready for decision use.")
# # # # #         action = "✓ High confidence — insights are decision-ready"
# # # # #         color  = "#22c55e"
# # # # #     elif model_r2 >= 55:
# # # # #         desc   = (f"The model achieves {model_r2}% explanation power — moderate performance. "
# # # # #                   f"Insights are directionally correct but should be validated with domain expertise.")
# # # # #         action = "⚠ Use with caution — validate key findings"
# # # # #         color  = "#f59e0b"
# # # # #     else:
# # # # #         desc   = (f"The model explains only {model_r2}% of variance — low performance. "
# # # # #                   f"The dataset may lack key predictors. Treat insights as exploratory hypotheses.")
# # # # #         action = "⚠ Low confidence — explore additional data sources"
# # # # #         color  = "#ef4444"

# # # # #     insights.append({"id":"model_reliability","title":"MODEL RELIABILITY SCORE",
# # # # #                      "value":f"{model_r2}%","metric":"Cross-validated R² score",
# # # # #                      "desc":desc,"action":action,"color":color})

# # # # #     # ── Card 2: Primary driver ──────────────────────────────────────────────────
# # # # #     direction = "increases" if top["trend"] == "Positive" else "decreases"
# # # # #     insights.append({
# # # # #         "id":"primary_driver","title":"PRIMARY DECISION DRIVER",
# # # # #         "value":top["feature"].upper(),"metric":f"{top['impact']}% of all predictive weight",
# # # # #         "desc":(f"'{top['feature']}' has the strongest influence on outcomes, "
# # # # #                 f"accounting for {top['impact']}% of the model's total decision weight. "
# # # # #                 f"When this value {direction}, your target outcome moves in the same direction. "
# # # # #                 f"If you could only monitor one variable, this is it."),
# # # # #         "action":"Set up real-time alerts for this variable","color":"#0ea5e9",
# # # # #     })

# # # # #     # ── Card 3: Anomaly alert ───────────────────────────────────────────────────
# # # # #     if anomaly_pct > 8:
# # # # #         desc   = (f"A significant {anomaly_pct}% of records ({n_anomalies} rows) were flagged as anomalous. "
# # # # #                   f"These may represent data errors, rare events, fraud, or equipment failures. "
# # # # #                   f"Review them individually before high-stakes decisions.")
# # # # #         action = "🚨 Investigate flagged records immediately"
# # # # #         color  = "#ef4444"
# # # # #     else:
# # # # #         desc   = (f"{n_anomalies} anomalous records ({anomaly_pct}%) — within acceptable limits. "
# # # # #                   f"Dataset is relatively clean; anomalies are unlikely to distort overall patterns.")
# # # # #         action = "✓ Anomaly rate acceptable — proceed normally"
# # # # #         color  = "#10b981"

# # # # #     insights.append({"id":"anomaly_alert","title":"ANOMALY DETECTION",
# # # # #                      "value":f"{n_anomalies} Records","metric":f"{anomaly_pct}% of dataset flagged",
# # # # #                      "desc":desc,"action":action,"color":color})

# # # # #     # ── Card 4: Concentration risk ──────────────────────────────────────────────
# # # # #     if top3_conc > 80:
# # # # #         desc   = (f"Model decisions are heavily concentrated: 3 features drive {top3_conc}% of all predictions. "
# # # # #                   f"Creates fragility — if any of those 3 shifts, predictions break down quickly.")
# # # # #         action = "⚠ Risk: over-reliance on 3 variables"
# # # # #         color  = "#f59e0b"
# # # # #     elif top3_conc > 60:
# # # # #         desc   = (f"Top 3 features account for {top3_conc}% — moderate concentration. "
# # # # #                   f"Clear hierarchy makes the model explainable. Monitor top 3 closely.")
# # # # #         action = "Monitor top 3 features closely"
# # # # #         color  = "#6366f1"
# # # # #     else:
# # # # #         desc   = (f"Decision weight well-distributed (top 3 = only {top3_conc}%). "
# # # # #                   f"A robust multi-factor model resistant to single-variable failures.")
# # # # #         action = "✓ Healthy — balanced feature utilisation"
# # # # #         color  = "#22c55e"

# # # # #     insights.append({"id":"complexity","title":"DECISION CONCENTRATION RISK",
# # # # #                      "value":f"{top3_conc}%","metric":"Top 3 features drive this share",
# # # # #                      "desc":desc,"action":action,"color":color})

# # # # #     # ── Card 5: Data quality ────────────────────────────────────────────────────
# # # # #     quality = round(100 - missing_pct - (dup_rows / n_rows * 100), 1)
# # # # #     if quality >= 95:
# # # # #         desc   = (f"Excellent dataset: {quality}% quality score, {missing_pct}% missing, "
# # # # #                   f"{dup_rows} duplicates. Analysis results are fully trustworthy.")
# # # # #         action = "✓ Dataset passes all quality checks"
# # # # #         color  = "#22c55e"
# # # # #     elif quality >= 80:
# # # # #         desc   = (f"Acceptable quality at {quality}%. {missing_pct}% missing and {dup_rows} duplicates. "
# # # # #                   f"Investigate why data is missing — may indicate broken pipelines.")
# # # # #         action = "⚠ Investigate missing data sources"
# # # # #         color  = "#f59e0b"
# # # # #     else:
# # # # #         desc   = (f"Concerning quality at {quality}%. {missing_pct}% missing and {dup_rows} duplicates. "
# # # # #                   f"Poor data quality is the #1 cause of misleading analytics. Prioritise cleaning.")
# # # # #         action = "🚨 Clean dataset before production use"
# # # # #         color  = "#ef4444"

# # # # #     insights.append({"id":"data_quality","title":"DATA INTEGRITY SCORE",
# # # # #                      "value":f"{quality}%","metric":f"{missing_pct}% missing · {dup_rows} duplicates",
# # # # #                      "desc":desc,"action":action,"color":color})

# # # # #     # ── Card 6: Target volatility ───────────────────────────────────────────────
# # # # #     if target_cv > 60:
# # # # #         desc   = (f"Target '{target_col}' is highly volatile (CV={target_cv}%). "
# # # # #                   f"Outcomes jump widely — individual forecasts carry wide error margins.")
# # # # #         action = "⚠ High variance — widen prediction confidence intervals"
# # # # #     elif target_cv > 30:
# # # # #         desc   = (f"Target '{target_col}' shows moderate variability (CV={target_cv}%). "
# # # # #                   f"Typical for real-world outcomes — predictions reliable on average.")
# # # # #         action = "Normal variance — predictions reliable on average"
# # # # #     else:
# # # # #         desc   = (f"Target '{target_col}' is quite stable (CV={target_cv}%). "
# # # # #                   f"Low variability means the model should achieve high accuracy.")
# # # # #         action = "✓ Low variance — high prediction confidence"

# # # # #     insights.append({"id":"target_volatility","title":"TARGET VOLATILITY INDEX",
# # # # #                      "value":f"CV: {target_cv}%","metric":f"σ={target_std} · Skew={target_skew}",
# # # # #                      "desc":desc,"action":action,"color":"#8b5cf6"})

# # # # #     # ── Card 7: Feature interaction / collinearity ─────────────────────────────
# # # # #     combined = round(top["impact"] + second["impact"], 1)
# # # # #     if inter_r > 0.6:
# # # # #         desc   = (f"'{f1}' and '{f2}' are strongly correlated (r={inter_r}), moving together "
# # # # #                   f"and sharing {combined}% of decisions. SHAP scores may be inflated — "
# # # # #                   f"you may only need one of them.")
# # # # #         action = "⚠ Collinearity risk — consider removing one"
# # # # #         color  = "#f59e0b"
# # # # #     else:
# # # # #         desc   = (f"'{f1}' and '{f2}' contribute independently (r={inter_r}), "
# # # # #                   f"together accounting for {combined}% of decisions without redundancy. "
# # # # #                   f"Both bring unique, non-overlapping information.")
# # # # #         action = "✓ Features contribute independently"
# # # # #         color  = "#6366f1"

# # # # #     insights.append({"id":"feature_interaction","title":"TOP-2 FEATURE SYNERGY",
# # # # #                      "value":f"r = {inter_r}","metric":f"{combined}% combined decision weight",
# # # # #                      "desc":desc,"action":action,"color":color})

# # # # #     return insights


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  DECISION NARRATIVE  (executive summary banner, preserved from v4)
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # def generate_decision_narrative(feature_impact, rca_report, insights,
# # # # #                                  target_col, model_r2, n_rows, anomaly_pct):
# # # # #     """
# # # # #     Build the 5-paragraph narrative block shown at the top of results.
# # # # #     Fully plain language — no jargon. Suitable for executives.
# # # # #     """
# # # # #     top  = feature_impact[0]
# # # # #     top2 = feature_impact[1] if len(feature_impact) > 1 else feature_impact[0]
# # # # #     conf = "high" if model_r2 >= 75 else "moderate" if model_r2 >= 50 else "low"

# # # # #     return {
# # # # #         "headline": "Your dataset has been fully analyzed. Here is what the data is telling you.",
# # # # #         "summary": (
# # # # #             f"This analysis examined {n_rows:,} records across {len(feature_impact)+1} variables "
# # # # #             f"to understand what drives your target outcome: '{target_col}'. "
# # # # #             f"The AI model explains {model_r2}% of outcome variation, "
# # # # #             f"giving us {conf} confidence in these findings."
# # # # #         ),
# # # # #         "key_finding": (
# # # # #             f"The single most important factor affecting '{target_col}' is '{top['feature']}', "
# # # # #             f"which carries {top['impact']}% of all predictive weight. "
# # # # #             f"This means that if you want to move the needle on your outcomes, "
# # # # #             f"'{top['feature']}' is where your attention and resources should go first."
# # # # #         ),
# # # # #         "secondary_finding": (
# # # # #             f"The second most influential factor is '{top2['feature']}' at {top2['impact']}% weight. "
# # # # #             f"Together, these two variables explain the majority of what happens in your data."
# # # # #         ),
# # # # #         "risk_alert": (
# # # # #             f"⚠ ATTENTION: {round(anomaly_pct)}% of records show unusual patterns "
# # # # #             f"that may indicate errors or rare events. Review before acting on this analysis."
# # # # #             if anomaly_pct > 8 else
# # # # #             "✓ No major anomaly risks detected. The data is clean enough to support "
# # # # #             "confident decision-making."
# # # # #         ),
# # # # #         "recommended_action": (
# # # # #             f"Focus immediate effort on monitoring and controlling '{top['feature']}'. "
# # # # #             f"Establish clear operational boundaries for its acceptable range, "
# # # # #             f"assign a team or individual responsible for tracking it, "
# # # # #             f"and build dashboards that alert you when it moves outside normal limits."
# # # # #         ),
# # # # #     }


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  MAIN ROUTE  — POST /analyze
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  SHARED ANALYSIS PIPELINE
# # # # # #  Called by both POST /analyze (file upload) and POST /scrape_analyze (web).
# # # # # #  Accepts a raw pandas DataFrame; returns a sanitized JSON-ready payload dict.
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # def run_analysis_pipeline(df: pd.DataFrame) -> dict:
# # # # #     """
# # # # #     Full analysis pipeline — steps 2-18 from the original analyze() route.

# # # # #     1.  NLP text column detection + language identification
# # # # #     2.  Embedding with AraBERT / RoBERTa / XLM-RoBERTa
# # # # #     3.  PCA compression of embeddings
# # # # #     4.  Auto target detection (supports Arabic headers)
# # # # #     5.  Build augmented feature matrix X = [numeric | NLP_embeddings]
# # # # #     6.  RandomForest model training
# # # # #     7.  SHAP explainability
# # # # #     8.  Feature impact scoring
# # # # #     9.  Distribution, scatter, cumulative data
# # # # #     10. Smart chart selection
# # # # #     11. Cross-validated R² scoring
# # # # #     12. Advanced insight cards
# # # # #     13. Root Cause Analysis
# # # # #     14. Decision narrative
# # # # #     15. Correlation matrix
# # # # #     16. Safe data preview
# # # # #     17. JSON response assembly (sanitized)

# # # # #     Args:
# # # # #         df: Raw input DataFrame (may contain NaN / mixed types).

# # # # #     Returns:
# # # # #         Sanitized dict ready for jsonify().  Callers may add extra keys
# # # # #         (e.g. source, source_url) before returning to the client.

# # # # #     Raises:
# # # # #         ValueError: if the DataFrame has fewer than 2 numeric columns.
# # # # #     """
# # # # #     missing_total = int(df.isnull().sum().sum())
# # # # #     dup_rows      = int(df.duplicated().sum())

# # # # #     df_clean = df.replace([np.inf, -np.inf], np.nan)

# # # # #     # ── Auto-coerce string columns that are ≥85% parseable as numbers ─────────
# # # # #     for col in df_clean.select_dtypes(include=[object]).columns:
# # # # #         converted = pd.to_numeric(df_clean[col], errors="coerce")
# # # # #         ratio = converted.notna().sum() / max(len(df_clean), 1)
# # # # #         if ratio >= 0.85:
# # # # #             df_clean[col] = converted

# # # # #     df_clean = df_clean.fillna(0)

# # # # #     # ── Validate minimum dataset size ─────────────────────────────────────────
# # # # #     if len(df_clean) < 5:
# # # # #         raise ValueError(
# # # # #             f"Dataset has only {len(df_clean)} rows. "
# # # # #             "At least 5 rows are required for meaningful analysis."
# # # # #         )

# # # # #     # ── NLP pipeline ──────────────────────────────────────────────────────────
# # # # #     text_matrix, nlp_metadata = process_text_columns(df_clean)

# # # # #     # ── Numeric feature isolation ──────────────────────────────────────────────
# # # # #     numeric_df = df_clean.select_dtypes(include=[np.number])

# # # # #     # Drop constant columns (std == 0) — they crash correlations and SHAP
# # # # #     constant_cols = [c for c in numeric_df.columns if numeric_df[c].std() == 0]
# # # # #     if constant_cols:
# # # # #         numeric_df = numeric_df.drop(columns=constant_cols)

# # # # #     if numeric_df.empty or numeric_df.shape[1] < 2:
# # # # #         raise ValueError(
# # # # #             "Dataset needs at least 2 non-constant numeric columns for analysis. "
# # # # #             "Please check that your file contains numeric data and is not all text or all identical values."
# # # # #         )

# # # # #     target_col, target_reason = auto_detect_target(numeric_df)
# # # # #     feature_cols = [c for c in numeric_df.columns if c != target_col]

# # # # #     # Edge case: only 1 numeric column → use it as both target and only feature
# # # # #     if not feature_cols:
# # # # #         raise ValueError(
# # # # #             "Only one usable numeric column found. "
# # # # #             "At least 2 numeric columns are needed (one target + at least one feature)."
# # # # #         )

# # # # #     X_num = numeric_df[feature_cols]
# # # # #     y     = numeric_df[target_col]

# # # # #     # ── Augment X with NLP embeddings ─────────────────────────────────────────
# # # # #     nlp_feat_names = []
# # # # #     for cm in nlp_metadata.get("columns_processed", []):
# # # # #         nlp_feat_names.extend(cm.get("feature_names", []))

# # # # #     if (text_matrix is not None
# # # # #             and text_matrix.shape[0] == len(X_num)
# # # # #             and len(nlp_feat_names) == text_matrix.shape[1]):
# # # # #         nlp_df = pd.DataFrame(text_matrix, columns=nlp_feat_names, index=X_num.index)
# # # # #         X      = pd.concat([X_num, nlp_df], axis=1)
# # # # #         nlp_metadata["features_added"] = len(nlp_feat_names)
# # # # #     else:
# # # # #         X = X_num

# # # # #     # Drop any NaN/Inf that crept in through NLP embeddings
# # # # #     X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

# # # # #     # ── Model training ─────────────────────────────────────────────────────────
# # # # #     n_estimators = min(80, max(10, len(X) * 2))  # scale to dataset size
# # # # #     model = RandomForestRegressor(
# # # # #         n_estimators=n_estimators, random_state=42,
# # # # #         max_depth=min(12, len(X) // 2 + 1), n_jobs=-1
# # # # #     )
# # # # #     model.fit(X, y)

# # # # #     # ── SHAP ───────────────────────────────────────────────────────────────────
# # # # #     explainer   = shap.TreeExplainer(model)
# # # # #     shap_values = explainer.shap_values(X)

# # # # #     # ── Feature impact ─────────────────────────────────────────────────────────
# # # # #     all_frame    = pd.concat([X, y], axis=1)
# # # # #     correlations = all_frame.corr()[target_col]
# # # # #     raw_impacts  = [np.abs(shap_values[:, i]).mean() for i in range(X.shape[1])]
# # # # #     total_impact = sum(raw_impacts) or 1

# # # # #     feature_impact = []
# # # # #     for i, col in enumerate(X.columns):
# # # # #         pct      = round((raw_impacts[i] / total_impact) * 100, 1)
# # # # #         corr_val = float(correlations.get(col, 0))
# # # # #         trend    = "Positive" if corr_val >= 0 else "Negative"
# # # # #         level    = "Critical" if pct > 25 else "High" if pct > 10 else "Standard"
# # # # #         feature_impact.append({
# # # # #             "feature":          col,
# # # # #             "impact":           pct,
# # # # #             "trend":            trend,
# # # # #             "importance_level": level,
# # # # #             "is_nlp":           col.startswith("[NLP]"),
# # # # #         })
# # # # #     feature_impact.sort(key=lambda x: x["impact"], reverse=True)

# # # # #     # ── Distribution data ──────────────────────────────────────────────────────
# # # # #     dist_data = {}
# # # # #     for col in X_num.columns[:6]:
# # # # #         col_data    = X_num[col].dropna()
# # # # #         hist, edges = np.histogram(col_data, bins=12)
# # # # #         dist_data[col] = {
# # # # #             "bins":   [round(float(e), 3) for e in edges[:-1]],
# # # # #             "counts": [int(h) for h in hist],
# # # # #             "labels": [str(round(float(e), 2)) for e in edges[:-1]],
# # # # #         }

# # # # #     # ── Scatter data (top 2 non-NLP numeric features) ─────────────────────────
# # # # #     scatter_data  = {}
# # # # #     top_num_feats = [f["feature"] for f in feature_impact
# # # # #                      if not f["is_nlp"] and f["feature"] in X_num.columns]
# # # # #     if len(top_num_feats) >= 2:
# # # # #         f1, f2      = top_num_feats[0], top_num_feats[1]
# # # # #         sample_idx  = np.random.choice(len(X), min(300, len(X)), replace=False)
# # # # #         fi1         = list(X.columns).index(f1)
# # # # #         scatter_data = {
# # # # #             "feat1": f1, "feat2": f2,
# # # # #             "points": [
# # # # #                 {
# # # # #                     "x": round(float(X[f1].iloc[i]), 4),
# # # # #                     "y": round(float(X[f2].iloc[i]), 4),
# # # # #                     "r": round(float(abs(shap_values[i, fi1])) * 10 + 4, 1),
# # # # #                 }
# # # # #                 for i in sample_idx
# # # # #             ],
# # # # #         }

# # # # #     # ── Cumulative impact curve ────────────────────────────────────────────────
# # # # #     sorted_impacts = sorted([f["impact"] for f in feature_impact], reverse=True)
# # # # #     cum, running   = [], 0
# # # # #     for v in sorted_impacts:
# # # # #         running += v
# # # # #         cum.append(round(running, 1))

# # # # #     # ── Chart recommendations ──────────────────────────────────────────────────
# # # # #     chart_recommendations = detect_chart_types(
# # # # #         df_clean, numeric_df, feature_impact, dist_data, target_col
# # # # #     )

# # # # #     # ── Cross-validated R² ─────────────────────────────────────────────────────
# # # # #     n_splits  = max(2, min(5, len(X) // 2))
# # # # #     try:
# # # # #         cv_scores = cross_val_score(model, X, y, cv=n_splits, scoring="r2")
# # # # #         model_r2  = max(0.0, min(100.0, round(float(np.nanmean(cv_scores)) * 100, 1)))
# # # # #     except Exception:
# # # # #         # Fallback: use training R² if CV fails (very small dataset)
# # # # #         y_pred   = model.predict(X)
# # # # #         ss_res   = float(np.sum((y - y_pred) ** 2))
# # # # #         ss_tot   = float(np.sum((y - y.mean()) ** 2))
# # # # #         model_r2 = max(0.0, min(100.0, round((1 - ss_res / max(ss_tot, 1e-9)) * 100, 1)))

# # # # #     # ── Advanced insights ──────────────────────────────────────────────────────
# # # # #     advanced_insights = compute_advanced_insights(
# # # # #         df_clean, numeric_df, feature_impact, shap_values, X, y, target_col, model_r2
# # # # #     )

# # # # #     # ── RCA ────────────────────────────────────────────────────────────────────
# # # # #     rca_report = compute_rca(
# # # # #         df_clean, numeric_df, feature_impact, shap_values, X, y, target_col
# # # # #     )

# # # # #     # Extract anomaly percentage for narrative
# # # # #     anomaly_pct_val = 0.0
# # # # #     for ins in advanced_insights:
# # # # #         if ins["id"] == "anomaly_alert":
# # # # #             try:
# # # # #                 anomaly_pct_val = float(ins["metric"].split("%")[0])
# # # # #             except Exception:
# # # # #                 pass

# # # # #     # ── Decision narrative ─────────────────────────────────────────────────────
# # # # #     decision_narrative = generate_decision_narrative(
# # # # #         feature_impact, rca_report, advanced_insights,
# # # # #         target_col, model_r2, len(df), anomaly_pct_val,
# # # # #     )

# # # # #     # ── Correlation matrix ─────────────────────────────────────────────────────
# # # # #     top_feats = [f["feature"] for f in feature_impact[:7]
# # # # #                  if not f["is_nlp"] and f["feature"] in numeric_df.columns]
# # # # #     sub_cols  = list(dict.fromkeys(top_feats + [target_col]))
# # # # #     sub_cols  = [c for c in sub_cols if c in numeric_df.columns]
# # # # #     corr_matrix = []
# # # # #     if len(sub_cols) >= 2:
# # # # #         sub = numeric_df[sub_cols].corr()
# # # # #         for r in sub.index:
# # # # #             for c in sub.columns:
# # # # #                 corr_matrix.append({"row": r, "col": c,
# # # # #                                      "value": round(float(sub.loc[r, c]), 3)})

# # # # #     # ── Safe data preview (first 10 rows) ──────────────────────────────────────
# # # # #     preview_records = []
# # # # #     for _, row in df.head(10).iterrows():
# # # # #         rec = {}
# # # # #         for col in df.columns:
# # # # #             v = row[col]
# # # # #             if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
# # # # #                 rec[col] = "—"
# # # # #             elif pd.isna(v):
# # # # #                 rec[col] = "—"
# # # # #             elif isinstance(v, np.integer):
# # # # #                 rec[col] = int(v)
# # # # #             elif isinstance(v, np.floating):
# # # # #                 rec[col] = round(float(v), 4)
# # # # #             else:
# # # # #                 rec[col] = v
# # # # #         preview_records.append(rec)

# # # # #     # ── Assemble and sanitize ──────────────────────────────────────────────────
# # # # #     return sanitize({
# # # # #         "status":                "success",
# # # # #         "preview":               preview_records,
# # # # #         "xai_report":            feature_impact,
# # # # #         "chart_recommendations": chart_recommendations,
# # # # #         "advanced_insights":     advanced_insights,
# # # # #         "rca_report":            rca_report,
# # # # #         "corr_matrix":           corr_matrix,
# # # # #         "dist_data":             dist_data,
# # # # #         "scatter_data":          scatter_data,
# # # # #         "cumulative_data": {
# # # # #             "values": cum,
# # # # #             "labels": [f["feature"] for f in feature_impact[:len(cum)]],
# # # # #         },
# # # # #         "model_score":        model_r2,
# # # # #         "decision_narrative": decision_narrative,
# # # # #         "target_detection":   {"column": target_col, "reason": target_reason},
# # # # #         "nlp_analysis":       nlp_metadata,
# # # # #         "dataset_meta": {
# # # # #             "rows":           len(df),
# # # # #             "cols":           len(df.columns),
# # # # #             "numeric_cols":   len(numeric_df.columns),
# # # # #             "missing_total":  missing_total,
# # # # #             "duplicate_rows": dup_rows,
# # # # #             "target_column":  target_col,
# # # # #             "target_reason":  target_reason,
# # # # #             "nlp_text_cols":  len(nlp_metadata.get("columns_processed", [])),
# # # # #         },
# # # # #     })


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  ROUTE  — POST /analyze    (Track A: file upload)
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # @app.route("/analyze", methods=["POST","OPTIONS"])
# # # # # def analyze():
# # # # #     if request.method == "OPTIONS": return "", 200
# # # # #     """
# # # # #     Track A entry point.
# # # # #     Accepts: multipart/form-data with a 'file' field (CSV).
# # # # #     Runs run_analysis_pipeline() and returns the full JSON payload.
# # # # #     """
# # # # #     try:
# # # # #         if "file" not in request.files:
# # # # #             return jsonify({"status": "error", "message": "No file uploaded"}), 400

# # # # #         file     = request.files["file"]
# # # # #         filename = (file.filename or "").lower()

# # # # #         try:
# # # # #             if filename.endswith((".xlsx", ".xls")):
# # # # #                 df = pd.read_excel(file)
# # # # #             else:
# # # # #                 # Try CSV; if that fails try with different separators
# # # # #                 raw = file.read()
# # # # #                 for sep in [",", ";", "\t", "|"]:
# # # # #                     try:
# # # # #                         df = pd.read_csv(
# # # # #                             __import__("io").BytesIO(raw),
# # # # #                             sep=sep, engine="python"
# # # # #                         )
# # # # #                         if df.shape[1] >= 2:
# # # # #                             break
# # # # #                     except Exception:
# # # # #                         continue
# # # # #                 else:
# # # # #                     df = pd.read_csv(__import__("io").BytesIO(raw))
# # # # #         except Exception as read_err:
# # # # #             return jsonify({
# # # # #                 "status":  "error",
# # # # #                 "message": (
# # # # #                     f"Could not read file '{file.filename}'. "
# # # # #                     f"Supported formats: CSV (.csv) and Excel (.xlsx, .xls). "
# # # # #                     f"Detail: {read_err}"
# # # # #                 )
# # # # #             }), 400

# # # # #         payload = run_analysis_pipeline(df)
# # # # #         payload["dataset_meta"]["source"]    = "file_upload"
# # # # #         payload["dataset_meta"]["file_name"] = file.filename or "uploaded_file"

# # # # #         return jsonify(payload)

# # # # #     except ValueError as ve:
# # # # #         return jsonify({"status": "error", "message": str(ve)}), 400
# # # # #     except Exception as exc:
# # # # #         import traceback
# # # # #         traceback.print_exc()
# # # # #         return jsonify({"status": "error", "message": str(exc)}), 500


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  ROUTE — POST /analyze_full  (Preprocess + XAI in one call)
# # # # # #  Used by: "Analyze Dataset" workflow and "Continue to Analysis" from Preprocess
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # @app.route("/analyze_full", methods=["POST","OPTIONS"])
# # # # # def analyze_full():
# # # # #     if request.method == "OPTIONS": return "", 200
# # # # #     """
# # # # #     POST /analyze_full
# # # # #     Accepts: multipart/form-data with 'file' field (CSV or Excel).
# # # # #     Runs basira_auto_preprocessing() followed by run_analysis_pipeline().
# # # # #     Returns full XAI payload with preprocessing_summary included.
# # # # #     """
# # # # #     try:
# # # # #         if "file" not in request.files:
# # # # #             return jsonify({"status": "error", "message": "No file uploaded"}), 400

# # # # #         file     = request.files["file"]
# # # # #         filename = (file.filename or "").lower()

# # # # #         try:
# # # # #             if filename.endswith((".xlsx", ".xls")):
# # # # #                 df_raw = pd.read_excel(file)
# # # # #             else:
# # # # #                 raw = file.read()
# # # # #                 for sep in [",", ";", "\t", "|"]:
# # # # #                     try:
# # # # #                         df_raw = pd.read_csv(
# # # # #                             __import__("io").BytesIO(raw),
# # # # #                             sep=sep, engine="python"
# # # # #                         )
# # # # #                         if df_raw.shape[1] >= 2:
# # # # #                             break
# # # # #                     except Exception:
# # # # #                         continue
# # # # #                 else:
# # # # #                     df_raw = pd.read_csv(__import__("io").BytesIO(raw))
# # # # #         except Exception as read_err:
# # # # #             return jsonify({
# # # # #                 "status": "error",
# # # # #                 "message": (
# # # # #                     f"Could not read file '{file.filename}'. "
# # # # #                     f"Supported: CSV (.csv) and Excel (.xlsx, .xls). "
# # # # #                     f"Detail: {read_err}"
# # # # #                 )
# # # # #             }), 400

# # # # #         if df_raw.empty:
# # # # #             return jsonify({"status": "error", "message": "Uploaded file is empty."}), 400

# # # # #         # Step 1: Auto-preprocess
# # # # #         try:
# # # # #             cleaned_df, audit_df, preprocess_summary, _, _ = basira_auto_preprocessing(
# # # # #                 df_raw, file.filename or "upload.csv"
# # # # #             )
# # # # #         except Exception as pp_err:
# # # # #             cleaned_df = df_raw
# # # # #             preprocess_summary = {"warning": str(pp_err)}

# # # # #         # Step 2: Full XAI analysis on cleaned data
# # # # #         payload = run_analysis_pipeline(cleaned_df)
# # # # #         payload["dataset_meta"]["source"]               = "file_upload_preprocessed"
# # # # #         payload["dataset_meta"]["file_name"]            = file.filename or "uploaded_file"
# # # # #         payload["preprocessing_summary"]                = preprocess_summary

# # # # #         return jsonify(payload)

# # # # #     except ValueError as ve:
# # # # #         return jsonify({"status": "error", "message": str(ve)}), 400
# # # # #     except Exception as exc:
# # # # #         import traceback
# # # # #         traceback.print_exc()
# # # # #         return jsonify({"status": "error", "message": str(exc)}), 500


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  ROUTE  — POST /scrape_analyze    (Track B: URL → scrape → analysis)
# # # # # # ══════════════════════════════════════════════════════════════════════════════


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  SMART SCRAPING ENGINE  —  Multi-strategy universal extractor
# # # # # #  Supports: HTML tables, JSON-LD, product cards, review lists, grids,
# # # # # #            repeated-element patterns, generic content, JS-rendered pages
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # import re as _re
# # # # # import json as _json
# # # # # from urllib.parse import urlparse as _urlparse

# # # # # def _fetch_page(url: str, timeout: int = 25) -> tuple:
# # # # #     """Fetch URL with realistic browser headers. Returns (html_text, final_url, error)."""
# # # # #     headers = {
# # # # #         "User-Agent": (
# # # # #             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
# # # # #             "AppleWebKit/537.36 (KHTML, like Gecko) "
# # # # #             "Chrome/124.0.0.0 Safari/537.36"
# # # # #         ),
# # # # #         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
# # # # #         "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
# # # # #         "Accept-Encoding": "gzip, deflate, br",
# # # # #         "DNT": "1",
# # # # #         "Connection": "keep-alive",
# # # # #         "Upgrade-Insecure-Requests": "1",
# # # # #     }
# # # # #     try:
# # # # #         sess = http_requests.Session()
# # # # #         sess.headers.update(headers)
# # # # #         resp = sess.get(url, timeout=timeout, allow_redirects=True)
# # # # #         resp.raise_for_status()
# # # # #         return resp.text, resp.url, None
# # # # #     except Exception as e:
# # # # #         return None, url, str(e)


# # # # # def _score_df(df: pd.DataFrame) -> float:
# # # # #     """Score a candidate dataframe by richness."""
# # # # #     if df is None or df.empty or len(df) < 2:
# # # # #         return 0.0
# # # # #     rows = len(df)
# # # # #     cols = len(df.columns)
# # # # #     num_cols = df.select_dtypes(include=[np.number]).shape[1]
# # # # #     fill_rate = df.notna().mean().mean()
# # # # #     return (rows * 0.4 + cols * 1.5 + num_cols * 2.0 + fill_rate * 5.0)


# # # # # # ── Strategy 1: HTML <table> tags ─────────────────────────────────────────────
# # # # # def _strat_html_tables(html: str) -> list:
# # # # #     """Classic pandas.read_html()."""
# # # # #     try:
# # # # #         dfs = pd.read_html(__import__("io").StringIO(html))
# # # # #         return [d for d in dfs if len(d) >= 2]
# # # # #     except Exception:
# # # # #         return []


# # # # # # ── Strategy 2: JSON-LD / schema.org structured data ─────────────────────────
# # # # # def _strat_jsonld(html: str) -> list:
# # # # #     """Extract JSON-LD blocks and flatten to DataFrame."""
# # # # #     from bs4 import BeautifulSoup
# # # # #     soup = BeautifulSoup(html, "lxml")
# # # # #     results = []
# # # # #     for tag in soup.find_all("script", type="application/ld+json"):
# # # # #         try:
# # # # #             data = _json.loads(tag.string or "")
# # # # #         except Exception:
# # # # #             continue
# # # # #         # Unwrap @graph
# # # # #         if isinstance(data, dict) and "@graph" in data:
# # # # #             data = data["@graph"]
# # # # #         items = data if isinstance(data, list) else [data]
# # # # #         rows = []
# # # # #         for item in items:
# # # # #             if not isinstance(item, dict):
# # # # #                 continue
# # # # #             row = {}
# # # # #             for k, v in item.items():
# # # # #                 if k.startswith("@"):
# # # # #                     continue
# # # # #                 if isinstance(v, (str, int, float, bool)):
# # # # #                     row[k] = v
# # # # #                 elif isinstance(v, dict):
# # # # #                     for sk, sv in v.items():
# # # # #                         if isinstance(sv, (str, int, float)):
# # # # #                             row[f"{k}_{sk}"] = sv
# # # # #                 elif isinstance(v, list) and all(isinstance(x, (str, int, float)) for x in v):
# # # # #                     row[k] = ", ".join(str(x) for x in v)
# # # # #             if row:
# # # # #                 rows.append(row)
# # # # #         if len(rows) >= 2:
# # # # #             df = pd.DataFrame(rows)
# # # # #             results.append(df)
# # # # #     return results


# # # # # # ── Strategy 3: Repeated card/article/item patterns ───────────────────────────
# # # # # def _strat_repeated_elements(html: str) -> list:
# # # # #     """
# # # # #     Detect repeated sibling elements that share the same tag+class
# # # # #     (e.g. <article class="product_pod">, <div class="review">, <li class="item">).
# # # # #     Extract all text fields from each element into a row.
# # # # #     """
# # # # #     from bs4 import BeautifulSoup, Tag
# # # # #     soup = BeautifulSoup(html, "lxml")
# # # # #     results = []

# # # # #     # Count (tag, class) combinations across all elements
# # # # #     from collections import Counter
# # # # #     combos: Counter = Counter()
# # # # #     for el in soup.find_all(True):
# # # # #         if not isinstance(el, Tag):
# # # # #             continue
# # # # #         cls = " ".join(sorted(el.get("class", [])))
# # # # #         if cls:
# # # # #             combos[(el.name, cls)] += 1

# # # # #     # Consider combos with 5+ occurrences as potential repeating items
# # # # #     candidates = [(tag, cls, count) for (tag, cls), count in combos.items() if count >= 5]
# # # # #     candidates.sort(key=lambda x: -x[2])

# # # # #     seen_selectors = set()
# # # # #     for tag_name, cls_str, count in candidates[:10]:
# # # # #         cls_list = cls_str.split()
# # # # #         primary_cls = cls_list[0] if cls_list else ""
# # # # #         if not primary_cls or primary_cls in seen_selectors:
# # # # #             continue
# # # # #         seen_selectors.add(primary_cls)

# # # # #         elements = soup.find_all(tag_name, class_=lambda c: c and primary_cls in c)
# # # # #         if len(elements) < 5:
# # # # #             continue

# # # # #         rows = []
# # # # #         for el in elements:
# # # # #             row = _extract_element_fields(el)
# # # # #             if row:
# # # # #                 rows.append(row)

# # # # #         if len(rows) >= 5:
# # # # #             df = pd.DataFrame(rows)
# # # # #             df = df.loc[:, df.nunique() > 1]  # drop constant cols
# # # # #             if len(df.columns) >= 2:
# # # # #                 results.append(df)

# # # # #     return results


# # # # # def _extract_element_fields(el) -> dict:
# # # # #     """Extract named text fields from a single card/item element."""
# # # # #     from bs4 import Tag
# # # # #     row = {}

# # # # #     # Rating patterns (stars, numbers)
# # # # #     rating_el = el.find(attrs={"class": _re.compile(r"rating|star|score|rate", _re.I)})
# # # # #     if rating_el:
# # # # #         txt = rating_el.get("title") or rating_el.get("aria-label") or rating_el.get_text(strip=True)
# # # # #         nums = _re.findall(r"\d+\.?\d*", txt or "")
# # # # #         if nums:
# # # # #             row["rating"] = float(nums[0])

# # # # #     # Price patterns
# # # # #     price_el = el.find(attrs={"class": _re.compile(r"price|cost|amount", _re.I)})
# # # # #     if price_el:
# # # # #         txt = price_el.get_text(strip=True)
# # # # #         nums = _re.findall(r"[\d,]+\.?\d*", txt.replace(",", ""))
# # # # #         if nums:
# # # # #             try:
# # # # #                 row["price"] = float(nums[0])
# # # # #             except Exception:
# # # # #                 row["price"] = txt

# # # # #     # Title / name / heading
# # # # #     for heading in el.find_all(["h1","h2","h3","h4","h5","a","p"], limit=5):
# # # # #         txt = heading.get_text(strip=True)
# # # # #         if txt and 3 < len(txt) < 200:
# # # # #             attr_cls = " ".join(heading.get("class", []))
# # # # #             if _re.search(r"title|name|header|heading|product", attr_cls, _re.I):
# # # # #                 row.setdefault("title", txt)
# # # # #                 break
# # # # #     if "title" not in row:
# # # # #         for heading in el.find_all(["h1","h2","h3","h4","h5"], limit=3):
# # # # #             txt = heading.get_text(strip=True)
# # # # #             if txt and 3 < len(txt) < 200:
# # # # #                 row["title"] = txt
# # # # #                 break

# # # # #     # Generic labelled fields by class name
# # # # #     for child in el.find_all(True):
# # # # #         cls = " ".join(child.get("class", [])).lower()
# # # # #         txt = child.get_text(strip=True)
# # # # #         if not txt or len(txt) > 300:
# # # # #             continue
# # # # #         for field in ["category","genre","author","brand","location","date",
# # # # #                       "description","review","comment","status","availability",
# # # # #                       "count","total","stock","type","label","tag"]:
# # # # #             if field in cls and field not in row:
# # # # #                 row[field] = txt
# # # # #                 break

# # # # #     # Image alt text as description fallback
# # # # #     img = el.find("img")
# # # # #     if img and "title" not in row:
# # # # #         alt = img.get("alt", "").strip()
# # # # #         if alt and len(alt) > 2:
# # # # #             row["title"] = alt

# # # # #     return row


# # # # # # ── Strategy 4: List structures <ul>/<ol> with consistent items ───────────────
# # # # # def _strat_lists(html: str) -> list:
# # # # #     """Extract structured <ul>/<li> lists where each <li> has multiple fields."""
# # # # #     from bs4 import BeautifulSoup
# # # # #     soup = BeautifulSoup(html, "lxml")
# # # # #     results = []

# # # # #     for ul in soup.find_all(["ul", "ol"]):
# # # # #         items = ul.find_all("li", recursive=False)
# # # # #         if len(items) < 5:
# # # # #             continue
# # # # #         rows = []
# # # # #         for li in items:
# # # # #             row = _extract_element_fields(li)
# # # # #             if not row:
# # # # #                 # fallback: just get text
# # # # #                 txt = li.get_text(strip=True)
# # # # #                 if txt and len(txt) > 2:
# # # # #                     row = {"item": txt}
# # # # #             if row:
# # # # #                 rows.append(row)
# # # # #         if len(rows) >= 5:
# # # # #             df = pd.DataFrame(rows)
# # # # #             if len(df.columns) >= 1 and len(df) >= 5:
# # # # #                 results.append(df)

# # # # #     return results


# # # # # # ── Strategy 5: Meta + OpenGraph extraction ────────────────────────────────────
# # # # # def _strat_meta(html: str, url: str) -> list:
# # # # #     """Extract page metadata as a single-row summary dataset."""
# # # # #     from bs4 import BeautifulSoup
# # # # #     soup = BeautifulSoup(html, "lxml")
# # # # #     row = {"url": url}

# # # # #     # Title
# # # # #     title_tag = soup.find("title")
# # # # #     if title_tag:
# # # # #         row["page_title"] = title_tag.get_text(strip=True)

# # # # #     # Meta tags
# # # # #     for meta in soup.find_all("meta"):
# # # # #         name = meta.get("name") or meta.get("property") or ""
# # # # #         content = meta.get("content") or ""
# # # # #         if not content or not name:
# # # # #             continue
# # # # #         name = name.lower().replace("og:", "og_").replace(":", "_")
# # # # #         if name in ("description", "keywords", "author", "og_title",
# # # # #                     "og_description", "og_type", "og_site_name"):
# # # # #             row[name] = content[:300]

# # # # #     # Headings summary
# # # # #     headings = [h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"])
# # # # #                 if h.get_text(strip=True)]
# # # # #     if headings:
# # # # #         row["headings"] = " | ".join(headings[:10])

# # # # #     # Link count, image count
# # # # #     row["link_count"]  = len(soup.find_all("a", href=True))
# # # # #     row["image_count"] = len(soup.find_all("img"))
# # # # #     row["word_count"]  = len((soup.get_text() or "").split())

# # # # #     return [pd.DataFrame([row])] if len(row) > 3 else []


# # # # # # ── Strategy 6: Generic paragraph / review text blocks ────────────────────────
# # # # # def _strat_text_blocks(html: str) -> list:
# # # # #     """
# # # # #     Extract blocks of text content (reviews, articles, paragraphs).
# # # # #     Groups sibling <p> or <div> blocks that look like review/content text.
# # # # #     """
# # # # #     from bs4 import BeautifulSoup
# # # # #     soup = BeautifulSoup(html, "lxml")

# # # # #     # Remove noise
# # # # #     for tag in soup(["script","style","nav","footer","header","aside"]):
# # # # #         tag.decompose()

# # # # #     # Try to find review-like blocks
# # # # #     review_containers = soup.find_all(
# # # # #         attrs={"class": _re.compile(r"review|comment|feedback|testimonial|opinion", _re.I)}
# # # # #     )
# # # # #     rows = []
# # # # #     for container in review_containers:
# # # # #         text = container.get_text(separator=" ", strip=True)
# # # # #         if text and 20 < len(text) < 2000:
# # # # #             row = {"text": text}
# # # # #             # Look for author, date, rating nearby
# # # # #             parent = container.parent
# # # # #             if parent:
# # # # #                 for sibling in parent.find_all(True, limit=10):
# # # # #                     sc = " ".join(sibling.get("class", [])).lower()
# # # # #                     st = sibling.get_text(strip=True)
# # # # #                     if not st:
# # # # #                         continue
# # # # #                     if "author" in sc or "name" in sc:
# # # # #                         row["author"] = st
# # # # #                     elif "date" in sc or "time" in sc:
# # # # #                         row["date"] = st
# # # # #                     elif "rating" in sc or "star" in sc:
# # # # #                         nums = _re.findall(r"\d+\.?\d*", st)
# # # # #                         if nums:
# # # # #                             row["rating"] = float(nums[0])
# # # # #             rows.append(row)

# # # # #     if len(rows) >= 3:
# # # # #         return [pd.DataFrame(rows)]

# # # # #     # Fallback: all substantial paragraphs
# # # # #     paragraphs = []
# # # # #     for p in soup.find_all("p"):
# # # # #         txt = p.get_text(strip=True)
# # # # #         if txt and 30 < len(txt) < 1000:
# # # # #             paragraphs.append({"paragraph": txt,
# # # # #                                 "word_count": len(txt.split())})
# # # # #     if len(paragraphs) >= 5:
# # # # #         return [pd.DataFrame(paragraphs)]

# # # # #     return []


# # # # # # ── Strategy 7: Google Maps / JS-heavy fallback ────────────────────────────────
# # # # # def _strat_js_hints(html: str, url: str) -> list:
# # # # #     """
# # # # #     Try to find embedded JSON data blobs (Next.js __NEXT_DATA__, 
# # # # #     window.__data__, Apollo state, etc.) in <script> tags.
# # # # #     """
# # # # #     from bs4 import BeautifulSoup
# # # # #     soup = BeautifulSoup(html, "lxml")
# # # # #     results = []

# # # # #     patterns = [
# # # # #         _re.compile(r'window\.__(?:INITIAL|NEXT|REDUX|APP|STORE|DATA)_(?:DATA|STATE)__\s*=\s*(\{.*?\});', _re.S),
# # # # #         _re.compile(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.+?)</script>', _re.S),
# # # # #         _re.compile(r'data-react-props="([^"]+)"'),
# # # # #     ]

# # # # #     for script in soup.find_all("script"):
# # # # #         text = script.string or ""
# # # # #         if len(text) < 50:
# # # # #             continue
# # # # #         for pat in patterns:
# # # # #             match = pat.search(text)
# # # # #             if match:
# # # # #                 try:
# # # # #                     blob = _json.loads(match.group(1))
# # # # #                     # Flatten any arrays inside
# # # # #                     rows = _flatten_json_to_rows(blob)
# # # # #                     if len(rows) >= 3:
# # # # #                         df = pd.DataFrame(rows)
# # # # #                         results.append(df)
# # # # #                         break
# # # # #                 except Exception:
# # # # #                     pass

# # # # #     return results


# # # # # def _flatten_json_to_rows(obj, depth=0, max_depth=5) -> list:
# # # # #     """Recursively find the largest list of dicts inside a JSON blob."""
# # # # #     if depth > max_depth:
# # # # #         return []
# # # # #     if isinstance(obj, list):
# # # # #         dicts = [x for x in obj if isinstance(x, dict)]
# # # # #         if len(dicts) >= 3:
# # # # #             rows = []
# # # # #             for d in dicts:
# # # # #                 row = {}
# # # # #                 for k, v in d.items():
# # # # #                     if isinstance(v, (str, int, float, bool)):
# # # # #                         row[k] = v
# # # # #                     elif isinstance(v, dict):
# # # # #                         for sk, sv in v.items():
# # # # #                             if isinstance(sv, (str, int, float)):
# # # # #                                 row[f"{k}_{sk}"] = sv
# # # # #                 if row:
# # # # #                     rows.append(row)
# # # # #             if rows:
# # # # #                 return rows
# # # # #     if isinstance(obj, dict):
# # # # #         best = []
# # # # #         for v in obj.values():
# # # # #             candidate = _flatten_json_to_rows(v, depth + 1, max_depth)
# # # # #             if len(candidate) > len(best):
# # # # #                 best = candidate
# # # # #         return best
# # # # #     return []


# # # # # # ── Master scraper ─────────────────────────────────────────────────────────────
# # # # # def smart_scrape(url: str) -> dict:
# # # # #     """
# # # # #     Run all strategies and return the best dataset found.
# # # # #     Returns: {
# # # # #         "df": pd.DataFrame,
# # # # #         "strategy": str,
# # # # #         "rows": int,
# # # # #         "cols": int,
# # # # #         "all_candidates": int,
# # # # #         "page_title": str,
# # # # #         "is_js_limited": bool,
# # # # #         "error": str or None
# # # # #     }
# # # # #     """
# # # # #     html, final_url, fetch_err = _fetch_page(url)
# # # # #     if not html:
# # # # #         return {"df": None, "error": fetch_err or "Could not fetch URL",
# # # # #                 "strategy": "none", "rows": 0, "cols": 0,
# # # # #                 "all_candidates": 0, "page_title": "", "is_js_limited": False}

# # # # #     # Detect JS-heavy pages
# # # # #     from bs4 import BeautifulSoup
# # # # #     soup_q = BeautifulSoup(html, "lxml")
# # # # #     visible_text_len = len(soup_q.get_text(strip=True))
# # # # #     script_count = len(soup_q.find_all("script"))
# # # # #     is_js_limited = (script_count > 15 and visible_text_len < 2000)

# # # # #     # Page title
# # # # #     title_tag = soup_q.find("title")
# # # # #     page_title = title_tag.get_text(strip=True) if title_tag else ""

# # # # #     # Run all strategies
# # # # #     all_dfs = []
# # # # #     strategy_map = {}

# # # # #     strat_fns = [
# # # # #         ("HTML Tables",    lambda: _strat_html_tables(html)),
# # # # #         ("JSON-LD Schema", lambda: _strat_jsonld(html)),
# # # # #         ("Repeated Cards", lambda: _strat_repeated_elements(html)),
# # # # #         ("List Items",     lambda: _strat_lists(html)),
# # # # #         ("JS Data Blobs",  lambda: _strat_js_hints(html, url)),
# # # # #         ("Text/Reviews",   lambda: _strat_text_blocks(html)),
# # # # #         ("Page Metadata",  lambda: _strat_meta(html, url)),
# # # # #     ]

# # # # #     for strat_name, strat_fn in strat_fns:
# # # # #         try:
# # # # #             dfs = strat_fn()
# # # # #         except Exception as _e:
# # # # #             import traceback as _tb; _tb.print_exc()
# # # # #             continue
# # # # #         for df in (dfs or []):
# # # # #             try:
# # # # #                 if df is not None and not df.empty and len(df) >= 2:
# # # # #                     score = _score_df(df)
# # # # #                     all_dfs.append((score, strat_name, df))
# # # # #             except Exception:
# # # # #                 continue

# # # # #     if not all_dfs:
# # # # #         return {
# # # # #             "df": None,
# # # # #             "error": (
# # # # #                 "No extractable data found. This page is likely fully "
# # # # #                 "JavaScript-rendered (Google Maps, React SPAs). "
# # # # #                 "Basira can only scrape static HTML content."
# # # # #                 if is_js_limited else
# # # # #                 "No structured data found on this page. Try a page that "
# # # # #                 "contains tables, product listings, reviews, or repeated content."
# # # # #             ),
# # # # #             "strategy": "none",
# # # # #             "rows": 0, "cols": 0,
# # # # #             "all_candidates": 0,
# # # # #             "page_title": page_title,
# # # # #             "is_js_limited": is_js_limited
# # # # #         }

# # # # #     # Pick best
# # # # #     all_dfs.sort(key=lambda x: -x[0])
# # # # #     best_score, best_strat, best_df = all_dfs[0]

# # # # #     # Clean up
# # # # #     best_df = best_df.copy()
# # # # #     best_df.columns = [str(c).strip().lower().replace(" ","_") for c in best_df.columns]
# # # # #     best_df = best_df.dropna(how="all").reset_index(drop=True)
# # # # #     # Coerce numeric strings
# # # # #     for col in best_df.columns:
# # # # #         if best_df[col].dtype == object:
# # # # #             converted = pd.to_numeric(best_df[col].astype(str).str.replace(r"[^\d\.\-]","",regex=True), errors="coerce")
# # # # #             if converted.notna().sum() / max(len(best_df), 1) >= 0.75:
# # # # #                 best_df[col] = converted

# # # # #     return {
# # # # #         "df": best_df,
# # # # #         "error": None,
# # # # #         "strategy": best_strat,
# # # # #         "rows": len(best_df),
# # # # #         "cols": len(best_df.columns),
# # # # #         "all_candidates": len(all_dfs),
# # # # #         "page_title": page_title,
# # # # #         "is_js_limited": is_js_limited,
# # # # #         "all_strategies_found": [
# # # # #             {"strategy": s, "rows": len(d), "cols": len(d.columns), "score": round(sc, 1)}
# # # # #             for sc, s, d in all_dfs[:5]
# # # # #         ]
# # # # #     }


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  ROUTE  — POST /scrape_analyze    (Smart Universal Scraper)
# # # # # # ══════════════════════════════════════════════════════════════════════════════


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  SMART SCRAPING ENGINE  —  Multi-strategy universal extractor
# # # # # #  Supports: HTML tables, JSON-LD, product cards, review lists, grids,
# # # # # #            repeated-element patterns, generic content, JS-rendered pages
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # import re as _re
# # # # # import json as _json
# # # # # from urllib.parse import urlparse as _urlparse

# # # # # _UA_LIST = [
# # # # #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
# # # # #     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
# # # # #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
# # # # #     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
# # # # #     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
# # # # # ]

# # # # # def _fetch_page(url: str, timeout: int = 30) -> tuple:
# # # # #     """Fetch URL with realistic browser headers, rotating UAs. Returns (html_text, final_url, error)."""
# # # # #     parsed = _urlparse(url)
# # # # #     referer = f"{parsed.scheme}://{parsed.netloc}/"

# # # # #     for ua in _UA_LIST:
# # # # #         headers = {
# # # # #             "User-Agent": ua,
# # # # #             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
# # # # #             "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
# # # # #             "Accept-Encoding": "gzip, deflate, br",
# # # # #             "Referer": referer,
# # # # #             "DNT": "1",
# # # # #             "Connection": "keep-alive",
# # # # #             "Upgrade-Insecure-Requests": "1",
# # # # #             "Cache-Control": "max-age=0",
# # # # #         }
# # # # #         try:
# # # # #             sess = http_requests.Session()
# # # # #             sess.headers.update(headers)
# # # # #             # First hit the root to get cookies
# # # # #             if parsed.path and parsed.path != "/":
# # # # #                 try: sess.get(referer, timeout=8, allow_redirects=True)
# # # # #                 except Exception: pass
# # # # #             resp = sess.get(url, timeout=timeout, allow_redirects=True)
# # # # #             if resp.status_code in (200, 206):
# # # # #                 return resp.text, resp.url, None
# # # # #             if resp.status_code == 403:
# # # # #                 continue  # try next UA
# # # # #             resp.raise_for_status()
# # # # #             return resp.text, resp.url, None
# # # # #         except http_requests.exceptions.RequestException:
# # # # #             continue
# # # # #         except Exception as e:
# # # # #             return None, url, str(e)

# # # # #     return None, url, f"Site blocked automated access (403). Try a different URL."


# # # # # def _score_df(df: pd.DataFrame) -> float:
# # # # #     """Score a candidate dataframe by richness."""
# # # # #     if df is None or df.empty or len(df) < 2:
# # # # #         return 0.0
# # # # #     rows = len(df)
# # # # #     cols = len(df.columns)
# # # # #     num_cols = df.select_dtypes(include=[np.number]).shape[1]
# # # # #     fill_rate = df.notna().mean().mean()
# # # # #     return (rows * 0.4 + cols * 1.5 + num_cols * 2.0 + fill_rate * 5.0)


# # # # # # ── Strategy 1: HTML <table> tags ─────────────────────────────────────────────
# # # # # def _strat_html_tables(html: str) -> list:
# # # # #     """Classic pandas.read_html()."""
# # # # #     try:
# # # # #         dfs = pd.read_html(__import__("io").StringIO(html))
# # # # #         return [d for d in dfs if len(d) >= 2]
# # # # #     except Exception:
# # # # #         return []


# # # # # # ── Strategy 2: JSON-LD / schema.org structured data ─────────────────────────
# # # # # def _strat_jsonld(html: str) -> list:
# # # # #     """Extract JSON-LD blocks and flatten to DataFrame."""
# # # # #     from bs4 import BeautifulSoup
# # # # #     soup = BeautifulSoup(html, "lxml")
# # # # #     results = []
# # # # #     for tag in soup.find_all("script", type="application/ld+json"):
# # # # #         try:
# # # # #             data = _json.loads(tag.string or "")
# # # # #         except Exception:
# # # # #             continue
# # # # #         # Unwrap @graph
# # # # #         if isinstance(data, dict) and "@graph" in data:
# # # # #             data = data["@graph"]
# # # # #         items = data if isinstance(data, list) else [data]
# # # # #         rows = []
# # # # #         for item in items:
# # # # #             if not isinstance(item, dict):
# # # # #                 continue
# # # # #             row = {}
# # # # #             for k, v in item.items():
# # # # #                 if k.startswith("@"):
# # # # #                     continue
# # # # #                 if isinstance(v, (str, int, float, bool)):
# # # # #                     row[k] = v
# # # # #                 elif isinstance(v, dict):
# # # # #                     for sk, sv in v.items():
# # # # #                         if isinstance(sv, (str, int, float)):
# # # # #                             row[f"{k}_{sk}"] = sv
# # # # #                 elif isinstance(v, list) and all(isinstance(x, (str, int, float)) for x in v):
# # # # #                     row[k] = ", ".join(str(x) for x in v)
# # # # #             if row:
# # # # #                 rows.append(row)
# # # # #         if len(rows) >= 2:
# # # # #             df = pd.DataFrame(rows)
# # # # #             results.append(df)
# # # # #     return results


# # # # # # ── Strategy 3: Repeated card/article/item patterns ───────────────────────────
# # # # # def _strat_repeated_elements(html: str) -> list:
# # # # #     """
# # # # #     Detect repeated sibling elements that share the same tag+class
# # # # #     (e.g. <article class="product_pod">, <div class="review">, <li class="item">).
# # # # #     Extract all text fields from each element into a row.
# # # # #     """
# # # # #     from bs4 import BeautifulSoup, Tag
# # # # #     soup = BeautifulSoup(html, "lxml")
# # # # #     results = []

# # # # #     # Count (tag, class) combinations across all elements
# # # # #     from collections import Counter
# # # # #     combos: Counter = Counter()
# # # # #     for el in soup.find_all(True):
# # # # #         if not isinstance(el, Tag):
# # # # #             continue
# # # # #         cls = " ".join(sorted(el.get("class", [])))
# # # # #         if cls:
# # # # #             combos[(el.name, cls)] += 1

# # # # #     # Consider combos with 5+ occurrences as potential repeating items
# # # # #     candidates = [(tag, cls, count) for (tag, cls), count in combos.items() if count >= 5]
# # # # #     candidates.sort(key=lambda x: -x[2])

# # # # #     seen_selectors = set()
# # # # #     for tag_name, cls_str, count in candidates[:10]:
# # # # #         cls_list = cls_str.split()
# # # # #         primary_cls = cls_list[0] if cls_list else ""
# # # # #         if not primary_cls or primary_cls in seen_selectors:
# # # # #             continue
# # # # #         seen_selectors.add(primary_cls)

# # # # #         elements = soup.find_all(tag_name, class_=lambda c: c and primary_cls in c)
# # # # #         if len(elements) < 5:
# # # # #             continue

# # # # #         rows = []
# # # # #         for el in elements:
# # # # #             row = _extract_element_fields(el)
# # # # #             if row:
# # # # #                 rows.append(row)

# # # # #         if len(rows) >= 5:
# # # # #             df = pd.DataFrame(rows)
# # # # #             df = df.loc[:, df.nunique() > 1]  # drop constant cols
# # # # #             if len(df.columns) >= 2:
# # # # #                 results.append(df)

# # # # #     return results


# # # # # def _extract_element_fields(el) -> dict:
# # # # #     """Extract named text fields from a single card/item element."""
# # # # #     from bs4 import Tag
# # # # #     row = {}

# # # # #     # Rating patterns (stars, numbers, word-based)
# # # # #     WORD_RATINGS = {"one":1,"two":2,"three":3,"four":4,"five":5,
# # # # #                     "one-star":1,"two-star":2,"three-star":3,"four-star":4,"five-star":5}
# # # # #     rating_el = el.find(attrs={"class": _re.compile(r"rating|star|score|rate", _re.I)})
# # # # #     if rating_el:
# # # # #         cls_str = " ".join(rating_el.get("class", [])).lower()
# # # # #         txt = rating_el.get("title") or rating_el.get("aria-label") or rating_el.get_text(strip=True) or ""
# # # # #         # Word-based class ratings (e.g. "star-rating Three")
# # # # #         for word, val in WORD_RATINGS.items():
# # # # #             if word in cls_str.split():
# # # # #                 row["rating"] = val
# # # # #                 break
# # # # #         if "rating" not in row:
# # # # #             nums = _re.findall(r"\d+\.?\d*", txt)
# # # # #             if nums:
# # # # #                 row["rating"] = float(nums[0])

# # # # #     # Price patterns
# # # # #     price_el = el.find(attrs={"class": _re.compile(r"price|cost|amount", _re.I)})
# # # # #     if price_el:
# # # # #         txt = price_el.get_text(strip=True)
# # # # #         nums = _re.findall(r"[\d,]+\.?\d*", txt.replace(",", ""))
# # # # #         if nums:
# # # # #             try:
# # # # #                 row["price"] = float(nums[0])
# # # # #             except Exception:
# # # # #                 row["price"] = txt

# # # # #     # Title / name / heading
# # # # #     for heading in el.find_all(["h1","h2","h3","h4","h5","a","p"], limit=5):
# # # # #         txt = heading.get_text(strip=True)
# # # # #         if txt and 3 < len(txt) < 200:
# # # # #             attr_cls = " ".join(heading.get("class", []))
# # # # #             if _re.search(r"title|name|header|heading|product", attr_cls, _re.I):
# # # # #                 row.setdefault("title", txt)
# # # # #                 break
# # # # #     if "title" not in row:
# # # # #         for heading in el.find_all(["h1","h2","h3","h4","h5"], limit=3):
# # # # #             txt = heading.get_text(strip=True)
# # # # #             if txt and 3 < len(txt) < 200:
# # # # #                 row["title"] = txt
# # # # #                 break

# # # # #     # Generic labelled fields by class name
# # # # #     for child in el.find_all(True):
# # # # #         cls = " ".join(child.get("class", [])).lower()
# # # # #         txt = child.get_text(strip=True)
# # # # #         if not txt or len(txt) > 300:
# # # # #             continue
# # # # #         for field in ["category","genre","author","brand","location","date",
# # # # #                       "description","review","comment","status","availability",
# # # # #                       "count","total","stock","type","label","tag"]:
# # # # #             if field in cls and field not in row:
# # # # #                 row[field] = txt
# # # # #                 break

# # # # #     # Image alt text as description fallback
# # # # #     img = el.find("img")
# # # # #     if img and "title" not in row:
# # # # #         alt = img.get("alt", "").strip()
# # # # #         if alt and len(alt) > 2:
# # # # #             row["title"] = alt

# # # # #     return row


# # # # # # ── Strategy 4: List structures <ul>/<ol> with consistent items ───────────────
# # # # # def _strat_lists(html: str) -> list:
# # # # #     """Extract structured <ul>/<li> lists where each <li> has multiple fields."""
# # # # #     from bs4 import BeautifulSoup
# # # # #     soup = BeautifulSoup(html, "lxml")
# # # # #     results = []

# # # # #     for ul in soup.find_all(["ul", "ol"]):
# # # # #         items = ul.find_all("li", recursive=False)
# # # # #         if len(items) < 5:
# # # # #             continue
# # # # #         rows = []
# # # # #         for li in items:
# # # # #             row = _extract_element_fields(li)
# # # # #             if not row:
# # # # #                 # fallback: just get text
# # # # #                 txt = li.get_text(strip=True)
# # # # #                 if txt and len(txt) > 2:
# # # # #                     row = {"item": txt}
# # # # #             if row:
# # # # #                 rows.append(row)
# # # # #         if len(rows) >= 5:
# # # # #             df = pd.DataFrame(rows)
# # # # #             if len(df.columns) >= 1 and len(df) >= 5:
# # # # #                 results.append(df)

# # # # #     return results


# # # # # # ── Strategy 5: Meta + OpenGraph extraction ────────────────────────────────────
# # # # # def _strat_meta(html: str, url: str) -> list:
# # # # #     """Extract page metadata as a single-row summary dataset."""
# # # # #     from bs4 import BeautifulSoup
# # # # #     soup = BeautifulSoup(html, "lxml")
# # # # #     row = {"url": url}

# # # # #     # Title
# # # # #     title_tag = soup.find("title")
# # # # #     if title_tag:
# # # # #         row["page_title"] = title_tag.get_text(strip=True)

# # # # #     # Meta tags
# # # # #     for meta in soup.find_all("meta"):
# # # # #         name = meta.get("name") or meta.get("property") or ""
# # # # #         content = meta.get("content") or ""
# # # # #         if not content or not name:
# # # # #             continue
# # # # #         name = name.lower().replace("og:", "og_").replace(":", "_")
# # # # #         if name in ("description", "keywords", "author", "og_title",
# # # # #                     "og_description", "og_type", "og_site_name"):
# # # # #             row[name] = content[:300]

# # # # #     # Headings summary
# # # # #     headings = [h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"])
# # # # #                 if h.get_text(strip=True)]
# # # # #     if headings:
# # # # #         row["headings"] = " | ".join(headings[:10])

# # # # #     # Link count, image count
# # # # #     row["link_count"]  = len(soup.find_all("a", href=True))
# # # # #     row["image_count"] = len(soup.find_all("img"))
# # # # #     row["word_count"]  = len((soup.get_text() or "").split())

# # # # #     return [pd.DataFrame([row])] if len(row) > 3 else []


# # # # # # ── Strategy 6: Generic paragraph / review text blocks ────────────────────────
# # # # # def _strat_text_blocks(html: str) -> list:
# # # # #     """
# # # # #     Extract blocks of text content (reviews, articles, paragraphs).
# # # # #     Groups sibling <p> or <div> blocks that look like review/content text.
# # # # #     """
# # # # #     from bs4 import BeautifulSoup
# # # # #     soup = BeautifulSoup(html, "lxml")

# # # # #     # Remove noise
# # # # #     for tag in soup(["script","style","nav","footer","header","aside"]):
# # # # #         tag.decompose()

# # # # #     # Try to find review-like blocks
# # # # #     review_containers = soup.find_all(
# # # # #         attrs={"class": _re.compile(r"review|comment|feedback|testimonial|opinion", _re.I)}
# # # # #     )
# # # # #     rows = []
# # # # #     for container in review_containers:
# # # # #         text = container.get_text(separator=" ", strip=True)
# # # # #         if text and 20 < len(text) < 2000:
# # # # #             row = {"text": text}
# # # # #             # Look for author, date, rating nearby
# # # # #             parent = container.parent
# # # # #             if parent:
# # # # #                 for sibling in parent.find_all(True, limit=10):
# # # # #                     sc = " ".join(sibling.get("class", [])).lower()
# # # # #                     st = sibling.get_text(strip=True)
# # # # #                     if not st:
# # # # #                         continue
# # # # #                     if "author" in sc or "name" in sc:
# # # # #                         row["author"] = st
# # # # #                     elif "date" in sc or "time" in sc:
# # # # #                         row["date"] = st
# # # # #                     elif "rating" in sc or "star" in sc:
# # # # #                         nums = _re.findall(r"\d+\.?\d*", st)
# # # # #                         if nums:
# # # # #                             row["rating"] = float(nums[0])
# # # # #             rows.append(row)

# # # # #     if len(rows) >= 3:
# # # # #         return [pd.DataFrame(rows)]

# # # # #     # Fallback: all substantial paragraphs
# # # # #     paragraphs = []
# # # # #     for p in soup.find_all("p"):
# # # # #         txt = p.get_text(strip=True)
# # # # #         if txt and 30 < len(txt) < 1000:
# # # # #             paragraphs.append({"paragraph": txt,
# # # # #                                 "word_count": len(txt.split())})
# # # # #     if len(paragraphs) >= 5:
# # # # #         return [pd.DataFrame(paragraphs)]

# # # # #     return []


# # # # # # ── Strategy 7: Google Maps / JS-heavy fallback ────────────────────────────────
# # # # # def _strat_js_hints(html: str, url: str) -> list:
# # # # #     """
# # # # #     Try to find embedded JSON data blobs (Next.js __NEXT_DATA__, 
# # # # #     window.__data__, Apollo state, etc.) in <script> tags.
# # # # #     """
# # # # #     from bs4 import BeautifulSoup
# # # # #     soup = BeautifulSoup(html, "lxml")
# # # # #     results = []

# # # # #     patterns = [
# # # # #         _re.compile(r'window\.__(?:INITIAL|NEXT|REDUX|APP|STORE|DATA)_(?:DATA|STATE)__\s*=\s*(\{.*?\});', _re.S),
# # # # #         _re.compile(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.+?)</script>', _re.S),
# # # # #         _re.compile(r'data-react-props="([^"]+)"'),
# # # # #     ]

# # # # #     for script in soup.find_all("script"):
# # # # #         text = script.string or ""
# # # # #         if len(text) < 50:
# # # # #             continue
# # # # #         for pat in patterns:
# # # # #             match = pat.search(text)
# # # # #             if match:
# # # # #                 try:
# # # # #                     blob = _json.loads(match.group(1))
# # # # #                     # Flatten any arrays inside
# # # # #                     rows = _flatten_json_to_rows(blob)
# # # # #                     if len(rows) >= 3:
# # # # #                         df = pd.DataFrame(rows)
# # # # #                         results.append(df)
# # # # #                         break
# # # # #                 except Exception:
# # # # #                     pass

# # # # #     return results


# # # # # def _flatten_json_to_rows(obj, depth=0, max_depth=5) -> list:
# # # # #     """Recursively find the largest list of dicts inside a JSON blob."""
# # # # #     if depth > max_depth:
# # # # #         return []
# # # # #     if isinstance(obj, list):
# # # # #         dicts = [x for x in obj if isinstance(x, dict)]
# # # # #         if len(dicts) >= 3:
# # # # #             rows = []
# # # # #             for d in dicts:
# # # # #                 row = {}
# # # # #                 for k, v in d.items():
# # # # #                     if isinstance(v, (str, int, float, bool)):
# # # # #                         row[k] = v
# # # # #                     elif isinstance(v, dict):
# # # # #                         for sk, sv in v.items():
# # # # #                             if isinstance(sv, (str, int, float)):
# # # # #                                 row[f"{k}_{sk}"] = sv
# # # # #                 if row:
# # # # #                     rows.append(row)
# # # # #             if rows:
# # # # #                 return rows
# # # # #     if isinstance(obj, dict):
# # # # #         best = []
# # # # #         for v in obj.values():
# # # # #             candidate = _flatten_json_to_rows(v, depth + 1, max_depth)
# # # # #             if len(candidate) > len(best):
# # # # #                 best = candidate
# # # # #         return best
# # # # #     return []


# # # # # # ── Master scraper ─────────────────────────────────────────────────────────────
# # # # # def smart_scrape(url: str) -> dict:
# # # # #     """
# # # # #     Run all strategies and return the best dataset found.
# # # # #     Returns: {
# # # # #         "df": pd.DataFrame,
# # # # #         "strategy": str,
# # # # #         "rows": int,
# # # # #         "cols": int,
# # # # #         "all_candidates": int,
# # # # #         "page_title": str,
# # # # #         "is_js_limited": bool,
# # # # #         "error": str or None
# # # # #     }
# # # # #     """
# # # # #     html, final_url, fetch_err = _fetch_page(url)
# # # # #     if not html:
# # # # #         return {"df": None, "error": fetch_err or "Could not fetch URL",
# # # # #                 "strategy": "none", "rows": 0, "cols": 0,
# # # # #                 "all_candidates": 0, "page_title": "", "is_js_limited": False}

# # # # #     # Detect JS-heavy pages
# # # # #     from bs4 import BeautifulSoup
# # # # #     soup_q = BeautifulSoup(html, "lxml")
# # # # #     visible_text_len = len(soup_q.get_text(strip=True))
# # # # #     script_count = len(soup_q.find_all("script"))
# # # # #     is_js_limited = (script_count > 15 and visible_text_len < 2000)

# # # # #     # Page title
# # # # #     title_tag = soup_q.find("title")
# # # # #     page_title = title_tag.get_text(strip=True) if title_tag else ""

# # # # #     # Run all strategies
# # # # #     all_dfs = []
# # # # #     strategy_map = {}

# # # # #     strat_fns = [
# # # # #         ("HTML Tables",    lambda: _strat_html_tables(html)),
# # # # #         ("JSON-LD Schema", lambda: _strat_jsonld(html)),
# # # # #         ("Repeated Cards", lambda: _strat_repeated_elements(html)),
# # # # #         ("List Items",     lambda: _strat_lists(html)),
# # # # #         ("JS Data Blobs",  lambda: _strat_js_hints(html, url)),
# # # # #         ("Text/Reviews",   lambda: _strat_text_blocks(html)),
# # # # #         ("Page Metadata",  lambda: _strat_meta(html, url)),
# # # # #     ]

# # # # #     for strat_name, strat_fn in strat_fns:
# # # # #         try:
# # # # #             dfs = strat_fn()
# # # # #         except Exception as _e:
# # # # #             import traceback as _tb; _tb.print_exc()
# # # # #             continue
# # # # #         for df in (dfs or []):
# # # # #             try:
# # # # #                 if df is not None and not df.empty and len(df) >= 2:
# # # # #                     score = _score_df(df)
# # # # #                     all_dfs.append((score, strat_name, df))
# # # # #             except Exception:
# # # # #                 continue

# # # # #     if not all_dfs:
# # # # #         return {
# # # # #             "df": None,
# # # # #             "error": (
# # # # #                 "No extractable data found. This page is likely fully "
# # # # #                 "JavaScript-rendered (Google Maps, React SPAs). "
# # # # #                 "Basira can only scrape static HTML content."
# # # # #                 if is_js_limited else
# # # # #                 "No structured data found on this page. Try a page that "
# # # # #                 "contains tables, product listings, reviews, or repeated content."
# # # # #             ),
# # # # #             "strategy": "none",
# # # # #             "rows": 0, "cols": 0,
# # # # #             "all_candidates": 0,
# # # # #             "page_title": page_title,
# # # # #             "is_js_limited": is_js_limited
# # # # #         }

# # # # #     # Pick best
# # # # #     all_dfs.sort(key=lambda x: -x[0])
# # # # #     best_score, best_strat, best_df = all_dfs[0]

# # # # #     # Clean up
# # # # #     best_df = best_df.copy()
# # # # #     best_df.columns = [str(c).strip().lower().replace(" ","_") for c in best_df.columns]
# # # # #     best_df = best_df.dropna(how="all").reset_index(drop=True)
# # # # #     # Coerce numeric strings
# # # # #     for col in best_df.columns:
# # # # #         if best_df[col].dtype == object:
# # # # #             converted = pd.to_numeric(best_df[col].astype(str).str.replace(r"[^\d\.\-]","",regex=True), errors="coerce")
# # # # #             if converted.notna().sum() / max(len(best_df), 1) >= 0.75:
# # # # #                 best_df[col] = converted

# # # # #     return {
# # # # #         "df": best_df,
# # # # #         "error": None,
# # # # #         "strategy": best_strat,
# # # # #         "rows": len(best_df),
# # # # #         "cols": len(best_df.columns),
# # # # #         "all_candidates": len(all_dfs),
# # # # #         "page_title": page_title,
# # # # #         "is_js_limited": is_js_limited,
# # # # #         "all_strategies_found": [
# # # # #             {"strategy": s, "rows": len(d), "cols": len(d.columns), "score": round(sc, 1)}
# # # # #             for sc, s, d in all_dfs[:5]
# # # # #         ]
# # # # #     }


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  ROUTE  — POST /scrape_analyze    (Smart Universal Scraper)
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # @app.route("/scrape_analyze", methods=["POST", "OPTIONS"])
# # # # # def scrape_analyze():
# # # # #     if request.method == "OPTIONS":
# # # # #         return "", 200

# # # # #     if not WEB_SCRAPE_AVAILABLE:
# # # # #         return jsonify({
# # # # #             "status": "error",
# # # # #             "message": "Install required libs: pip install requests lxml beautifulsoup4"
# # # # #         }), 500

# # # # #     try:
# # # # #         url = (request.form.get("url") or "").strip()
# # # # #         if not url:
# # # # #             return jsonify({"status": "error", "message": "No URL provided."}), 400
# # # # #         if not url.startswith(("http://", "https://")):
# # # # #             url = "https://" + url

# # # # #         # Run smart scraper
# # # # #         result = smart_scrape(url)

# # # # #         if result["df"] is None:
# # # # #             return jsonify({
# # # # #                 "status":        "error",
# # # # #                 "message":       result.get("error", "No data found."),
# # # # #                 "is_js_limited": result.get("is_js_limited", False),
# # # # #                 "page_title":    result.get("page_title", ""),
# # # # #             }), 400

# # # # #         best_df = result["df"]

# # # # #         # Raw preview (first 10 rows before preprocessing)
# # # # #         raw_preview  = _df_to_safe_records(best_df.head(10))
# # # # #         raw_csv_b64  = _df_to_b64_csv(best_df)

# # # # #         # Auto-preprocess (non-fatal)
# # # # #         try:
# # # # #             cleaned_df, _, preprocess_summary, _, _ = basira_auto_preprocessing(
# # # # #                 best_df, "scraped_data.csv"
# # # # #             )
# # # # #         except Exception as _pp_e:
# # # # #             print(f"[Basira] Preprocessing skipped: {_pp_e}")
# # # # #             cleaned_df = best_df
# # # # #             preprocess_summary = {}

# # # # #         if len(cleaned_df) < 5:
# # # # #             return jsonify({
# # # # #                 "status":  "error",
# # # # #                 "message": (
# # # # #                     f"Extracted only {len(cleaned_df)} rows — "
# # # # #                     "not enough for analysis. Try a page with more data."
# # # # #                 ),
# # # # #             }), 400

# # # # #         # Full XAI pipeline
# # # # #         try:
# # # # #             payload = run_analysis_pipeline(cleaned_df)
# # # # #         except ValueError as ve:
# # # # #             return jsonify({"status": "error", "message": str(ve)}), 400
# # # # #         payload["dataset_meta"]["source"]              = "web_scrape"
# # # # #         payload["dataset_meta"]["source_url"]          = url
# # # # #         payload["dataset_meta"]["page_title"]          = result["page_title"]
# # # # #         payload["dataset_meta"]["scrape_strategy"]     = result["strategy"]
# # # # #         payload["dataset_meta"]["all_candidates"]      = result["all_candidates"]
# # # # #         payload["dataset_meta"]["is_js_limited"]       = result["is_js_limited"]
# # # # #         payload["dataset_meta"]["strategies_summary"]  = result.get("all_strategies_found", [])
# # # # #         payload["raw_preview"]                         = raw_preview
# # # # #         payload["raw_csv_b64"]                         = raw_csv_b64

# # # # #         return jsonify(payload)

# # # # #     except Exception as exc:
# # # # #         import traceback
# # # # #         traceback.print_exc()
# # # # #         return jsonify({"status": "error", "message": str(exc)}), 500




# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  ROUTE  — POST /preprocess    (Track C: standalone preprocessing)
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # @app.route("/preprocess", methods=["POST","OPTIONS"])
# # # # # def preprocess():
# # # # #     if request.method == "OPTIONS": return "", 200
# # # # #     """
# # # # #     Track C: standalone bilingual preprocessing pipeline.

# # # # #     Steps:
# # # # #       1.  Read CSV/Excel upload
# # # # #       2.  Clean column names (strip, lowercase underscores)
# # # # #       3.  Auto-coerce string columns that are ≥85% numeric
# # # # #       4.  Compute baseline stats (rows, cols, missing, duplicates)
# # # # #       5.  Remove fully empty columns
# # # # #       6.  Remove high-missing columns (≥60%)
# # # # #       7.  Remove duplicate rows
# # # # #       8.  Impute numeric missing values (median — robust to skew)
# # # # #       9.  Impute categorical missing values (most frequent)
# # # # #       10. IQR outlier detection + Winsorization capping
# # # # #       11. Bilingual text normalization (Arabic + English)
# # # # #       12. Return cleaned CSV as base64 + audit trail + summary
# # # # #     """
# # # # #     import base64
# # # # #     import io as _io

# # # # #     try:
# # # # #         if "file" not in request.files:
# # # # #             return jsonify({"status": "error", "message": "No file uploaded"}), 400

# # # # #         file     = request.files["file"]
# # # # #         filename = (file.filename or "dataset").lower()
# # # # #         audit    = []  # list of audit log rows

# # # # #         def log(stage, column, action, before, after, method, notes=""):
# # # # #             audit.append({
# # # # #                 "stage":   stage,
# # # # #                 "column":  column,
# # # # #                 "action":  action,
# # # # #                 "before":  str(before),
# # # # #                 "after":   str(after),
# # # # #                 "method":  method,
# # # # #                 "notes":   notes,
# # # # #             })

# # # # #         # ── Read file ──────────────────────────────────────────────────────
# # # # #         try:
# # # # #             if filename.endswith((".xlsx", ".xls")):
# # # # #                 df = pd.read_excel(file)
# # # # #             else:
# # # # #                 raw = file.read()
# # # # #                 for sep in [",", ";", "\t", "|"]:
# # # # #                     try:
# # # # #                         df = pd.read_csv(_io.BytesIO(raw), sep=sep, engine="python")
# # # # #                         if df.shape[1] >= 1:
# # # # #                             break
# # # # #                     except Exception:
# # # # #                         continue
# # # # #                 else:
# # # # #                     df = pd.read_csv(_io.BytesIO(raw))
# # # # #         except Exception as e:
# # # # #             return jsonify({"status": "error",
# # # # #                             "message": f"Could not read file: {e}"}), 400

# # # # #         if df.empty:
# # # # #             return jsonify({"status": "error", "message": "File is empty."}), 400

# # # # #         rows_before = len(df)
# # # # #         cols_before = len(df.columns)
# # # # #         log("Ingestion", "*", "File loaded", f"{rows_before} rows", f"{cols_before} cols",
# # # # #             "pandas read_csv/read_excel")

# # # # #         # ── Clean column names ─────────────────────────────────────────────
# # # # #         original_cols = list(df.columns)
# # # # #         df.columns = [
# # # # #             re.sub(r"\s+", "_", str(c).strip().lower())
# # # # #             for c in df.columns
# # # # #         ]
# # # # #         renamed = [(o, n) for o, n in zip(original_cols, df.columns) if o != n]
# # # # #         if renamed:
# # # # #             log("Column Cleaning", "*", "Renamed columns",
# # # # #                 str(len(renamed)), str(len(renamed)),
# # # # #                 "strip + lowercase + underscore",
# # # # #                 "; ".join(f"'{o}'→'{n}'" for o, n in renamed[:5]))

# # # # #         # ── Replace Inf ────────────────────────────────────────────────────
# # # # #         inf_count = int(np.isinf(df.select_dtypes(include=[np.number])).sum().sum())
# # # # #         df = df.replace([np.inf, -np.inf], np.nan)
# # # # #         if inf_count:
# # # # #             log("Cleaning", "*", "Replaced Inf values", inf_count, "NaN",
# # # # #                 "replace([inf,-inf], NaN)")

# # # # #         # ── Auto-coerce string-but-numeric columns ─────────────────────────
# # # # #         coerced = []
# # # # #         for col in df.select_dtypes(include=[object]).columns:
# # # # #             converted = pd.to_numeric(df[col], errors="coerce")
# # # # #             ratio = converted.notna().sum() / max(len(df), 1)
# # # # #             if ratio >= 0.85:
# # # # #                 df[col] = converted
# # # # #                 coerced.append(col)
# # # # #         if coerced:
# # # # #             log("Type Coercion", str(coerced), "String → Numeric",
# # # # #                 "object", "float64", "pd.to_numeric ≥85% parseable",
# # # # #                 f"{len(coerced)} column(s) converted")

# # # # #         # ── Baseline stats ─────────────────────────────────────────────────
# # # # #         missing_before = int(df.isnull().sum().sum())
# # # # #         dup_before     = int(df.duplicated().sum())

# # # # #         # ── Remove fully empty columns ─────────────────────────────────────
# # # # #         empty_cols = [c for c in df.columns if df[c].isna().all()]
# # # # #         if empty_cols:
# # # # #             df = df.drop(columns=empty_cols)
# # # # #             log("Column Removal", str(empty_cols), "Dropped empty columns",
# # # # #                 len(empty_cols), 0, "isna().all()",
# # # # #                 "Columns with 100% missing values removed")

# # # # #         # ── Remove high-missing columns (≥60%) ────────────────────────────
# # # # #         missing_ratios   = df.isnull().mean()
# # # # #         high_miss_cols   = missing_ratios[missing_ratios >= 0.60].index.tolist()
# # # # #         if high_miss_cols:
# # # # #             df = df.drop(columns=high_miss_cols)
# # # # #             log("Column Removal", str(high_miss_cols), "Dropped high-missing columns",
# # # # #                 "≥60% missing", "removed", "threshold=0.60",
# # # # #                 f"{len(high_miss_cols)} column(s) exceeded 60% missing rate")

# # # # #         # ── Remove duplicate rows ──────────────────────────────────────────
# # # # #         if dup_before > 0:
# # # # #             df = df.drop_duplicates().reset_index(drop=True)
# # # # #             log("Duplicate Removal", "*", "Removed duplicate rows",
# # # # #                 dup_before, 0, "drop_duplicates()")

# # # # #         # ── Numeric imputation (median) ────────────────────────────────────
# # # # #         num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
# # # # #         for col in num_cols:
# # # # #             n_miss = int(df[col].isna().sum())
# # # # #             if n_miss > 0:
# # # # #                 median_val = df[col].median()
# # # # #                 df[col]    = df[col].fillna(median_val)
# # # # #                 log("Imputation", col, "Filled missing numeric",
# # # # #                     n_miss, round(float(median_val), 4),
# # # # #                     "median", f"{n_miss} missing values → median={round(float(median_val),4)}")

# # # # #         # ── Categorical imputation (most frequent) ─────────────────────────
# # # # #         cat_cols = df.select_dtypes(include=[object]).columns.tolist()
# # # # #         for col in cat_cols:
# # # # #             n_miss = int(df[col].isna().sum())
# # # # #             if n_miss > 0:
# # # # #                 mode_val = df[col].mode()
# # # # #                 fill_val = mode_val.iloc[0] if len(mode_val) > 0 else "unknown"
# # # # #                 df[col]  = df[col].fillna(fill_val)
# # # # #                 log("Imputation", col, "Filled missing categorical",
# # # # #                     n_miss, fill_val, "most_frequent",
# # # # #                     f"{n_miss} missing → mode='{fill_val}'")

# # # # #         # ── IQR outlier detection + Winsorization ─────────────────────────
# # # # #         outlier_summary = {}
# # # # #         for col in num_cols:
# # # # #             if col not in df.columns:
# # # # #                 continue
# # # # #             q1  = df[col].quantile(0.25)
# # # # #             q3  = df[col].quantile(0.75)
# # # # #             iqr = q3 - q1
# # # # #             if iqr == 0:
# # # # #                 continue
# # # # #             lo  = q1 - 1.5 * iqr
# # # # #             hi  = q3 + 1.5 * iqr
# # # # #             n_out = int(((df[col] < lo) | (df[col] > hi)).sum())
# # # # #             if n_out > 0:
# # # # #                 pct = n_out / len(df)
# # # # #                 if pct <= 0.05:
# # # # #                     # Winsorize
# # # # #                     df[col] = df[col].clip(lo, hi)
# # # # #                     action  = "Winsorized (capped)"
# # # # #                 else:
# # # # #                     # Flag only — don't destroy data
# # # # #                     action = "Flagged only (>5% outliers)"
# # # # #                 outlier_summary[col] = {"count": n_out, "pct": round(pct*100,1), "action": action}
# # # # #                 log("Outlier", col, action, n_out,
# # # # #                     f"[{round(float(lo),3)}, {round(float(hi),3)}]",
# # # # #                     "IQR 1.5×", f"{n_out} outliers ({round(pct*100,1)}%)")

# # # # #         # ── Bilingual text normalization ───────────────────────────────────
# # # # #         _RE_D  = re.compile(r"[\u064B-\u065F\u0610-\u061A\u06D6-\u06DC\u06DF-\u06E4\u06E7-\u06ED]")
# # # # #         _RE_AL = re.compile(r"[إأآا]")
# # # # #         _RE_TA = re.compile(r"ة")
# # # # #         _RE_TW = re.compile(r"\u0640")
# # # # #         _RE_WS = re.compile(r"\s+")
# # # # #         _RE_AR = re.compile(r"[\u0600-\u06FF]")

# # # # #         def _norm_cell(v):
# # # # #             if not isinstance(v, str) or not v.strip():
# # # # #                 return v
# # # # #             ar_ratio = len(_RE_AR.findall(v)) / max(len(v), 1)
# # # # #             if ar_ratio > 0.3:
# # # # #                 v = _RE_D.sub("", v)
# # # # #                 v = _RE_AL.sub("ا", v)
# # # # #                 v = _RE_TA.sub("ه", v)
# # # # #                 v = _RE_TW.sub("", v)
# # # # #             else:
# # # # #                 v = v.lower()
# # # # #             return _RE_WS.sub(" ", v).strip()

# # # # #         for col in cat_cols:
# # # # #             if col not in df.columns:
# # # # #                 continue
# # # # #             before_sample = str(df[col].iloc[0]) if len(df) > 0 else ""
# # # # #             df[col]       = df[col].apply(_norm_cell)
# # # # #             after_sample  = str(df[col].iloc[0]) if len(df) > 0 else ""
# # # # #             if before_sample != after_sample:
# # # # #                 log("Normalization", col, "Bilingual text normalized",
# # # # #                     before_sample[:40], after_sample[:40],
# # # # #                     "Arabic diacritics + alef / English lowercase")

# # # # #         # ── Final stats ────────────────────────────────────────────────────
# # # # #         rows_after    = len(df)
# # # # #         missing_after = int(df.isnull().sum().sum())

# # # # #         # Column type map
# # # # #         col_type_map = {
# # # # #             "numeric":     [c for c in df.columns if df[c].dtype != object],
# # # # #             "categorical": [c for c in df.columns if df[c].dtype == object],
# # # # #         }

# # # # #         # ── Encode cleaned CSV as base64 ───────────────────────────────────
# # # # #         csv_buf = _io.BytesIO()
# # # # #         df.to_csv(csv_buf, index=False, encoding="utf-8-sig")
# # # # #         cleaned_b64 = base64.b64encode(csv_buf.getvalue()).decode("ascii")

# # # # #         # ── Encode audit CSV as base64 ─────────────────────────────────────
# # # # #         audit_df  = pd.DataFrame(audit)
# # # # #         audit_buf = _io.BytesIO()
# # # # #         audit_df.to_csv(audit_buf, index=False, encoding="utf-8-sig")
# # # # #         audit_b64 = base64.b64encode(audit_buf.getvalue()).decode("ascii")

# # # # #         # ── Safe preview records ───────────────────────────────────────────
# # # # #         def _safe_val(v):
# # # # #             if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
# # # # #                 return None
# # # # #             if isinstance(v, (np.integer, np.int32, np.int64)):
# # # # #                 return int(v)
# # # # #             if isinstance(v, (np.floating, np.float32, np.float64)):
# # # # #                 v2 = float(v)
# # # # #                 return None if (math.isnan(v2) or math.isinf(v2)) else round(v2, 4)
# # # # #             return v

# # # # #         preview = [
# # # # #             {col: _safe_val(row[col]) for col in df.columns}
# # # # #             for _, row in df.head(15).iterrows()
# # # # #         ]

# # # # #         summary = {
# # # # #             "rows_before":     rows_before,
# # # # #             "cols_before":     cols_before,
# # # # #             "rows_after":      rows_after,
# # # # #             "cols_after":      len(df.columns),
# # # # #             "missing_before":  missing_before,
# # # # #             "missing_after":   missing_after,
# # # # #             "duplicates_removed": dup_before,
# # # # #             "empty_cols_removed": len(empty_cols),
# # # # #             "high_miss_cols_removed": len(high_miss_cols),
# # # # #             "numeric_cols":    len(col_type_map["numeric"]),
# # # # #             "categorical_cols": len(col_type_map["categorical"]),
# # # # #             "outlier_cols":    len(outlier_summary),
# # # # #             "text_normalized_cols": len([
# # # # #                 c for c in cat_cols if c in df.columns
# # # # #             ]),
# # # # #             "coerced_cols":    len(coerced),
# # # # #             "audit_steps":     len(audit),
# # # # #         }

# # # # #         import time as _time
# # # # #         run_id = f"basira_{int(_time.time())}"

# # # # #         # Extend summary with fields the frontend needs
# # # # #         summary["run_id"]                 = run_id
# # # # #         summary["rows_before"]            = rows_before
# # # # #         summary["rows_after"]             = rows_after
# # # # #         summary["missing_total_before"]   = missing_before
# # # # #         summary["missing_total_after"]    = missing_after
# # # # #         summary["exact_dup_before"]       = dup_before
# # # # #         summary["exact_dup_after"]        = max(0, dup_before - summary.get("duplicates_removed", 0))
# # # # #         summary["validation_pass_final"]  = missing_after == 0
# # # # #         summary["validation_pass_initial"]= missing_before == 0
# # # # #         summary["numeric_strategy"]       = "SIMPLE"
# # # # #         summary["features_generated"]     = False
# # # # #         summary["id_column"]              = None
# # # # #         summary["model_input_cols"]       = len(col_type_map.get("numeric", []))

# # # # #         # Align col_type_map to have all 4 keys
# # # # #         col_type_map.setdefault("text",     [])
# # # # #         col_type_map.setdefault("datetime", [])

# # # # #         return jsonify({
# # # # #             "status":          "success",
# # # # #             "run_id":          run_id,
# # # # #             "summary":         summary,
# # # # #             "col_type_map":    col_type_map,
# # # # #             "cleaned_preview": preview,
# # # # #             "model_preview":   preview,
# # # # #             "audit_preview":   audit,
# # # # #             "cleaned_csv_b64": cleaned_b64,
# # # # #             "audit_csv_b64":   audit_b64,
# # # # #             "feat_csv_b64":    None,
# # # # #             "model_csv_b64":   cleaned_b64,
# # # # #             "columns":         list(df.columns),
# # # # #         })

# # # # #     except Exception as exc:
# # # # #         import traceback
# # # # #         traceback.print_exc()
# # # # #         return jsonify({"status": "error", "message": str(exc)}), 500


# # # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # # #  ENTRY POINT
# # # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # # if __name__ == "__main__":
# # # # #     import subprocess as _sub, sys as _sys
# # # # #     _REQUIRED = [
# # # # #         "flask", "flask_cors", "pandas", "numpy", "shap",
# # # # #         "scikit-learn", "scipy", "requests", "lxml",
# # # # #         "beautifulsoup4", "openpyxl",
# # # # #     ]
# # # # #     _IMPORT_MAP = {"scikit-learn": "sklearn", "beautifulsoup4": "bs4"}
# # # # #     _missing = []
# # # # #     for pkg in _REQUIRED:
# # # # #         try:
# # # # #             __import__(_IMPORT_MAP.get(pkg, pkg.replace("-","_")))
# # # # #         except ImportError:
# # # # #             _missing.append(pkg)
# # # # #     if _missing:
# # # # #         print(f"[Basira] Auto-installing: {', '.join(_missing)}")
# # # # #         _sub.check_call([_sys.executable, "-m", "pip", "install",
# # # # #                          "--break-system-packages", "-q"] + _missing)
# # # # #         print("[Basira] Done. Starting server...")
# # # # #     app.run(debug=False, port=5001, host="127.0.0.1")


# # # # """
# # # # ╔══════════════════════════════════════════════════════════════════╗
# # # # ║  BASIRA — Core Intelligence Backend  v5.0                      ║
# # # # ║  Run:  python Basira_app_structure.py  →  http://127.0.0.1:5001 ║
# # # # ╚══════════════════════════════════════════════════════════════════╝
# # # # """

# # # # # ─── Standard library ─────────────────────────────────────────────────────────
# # # # import base64
# # # # import io
# # # # import json as _json
# # # # import math
# # # # import re
# # # # import subprocess as _sub
# # # # import sys as _sys
# # # # import time as _time
# # # # import warnings
# # # # from datetime import timedelta
# # # # from urllib.parse import urlparse as _urlparse

# # # # warnings.filterwarnings("ignore")

# # # # # ─── Scientific stack ─────────────────────────────────────────────────────────
# # # # import numpy as np
# # # # import pandas as pd
# # # # from scipy import stats
# # # # from sklearn.decomposition import PCA
# # # # from sklearn.ensemble import IsolationForest, RandomForestRegressor
# # # # from sklearn.model_selection import cross_val_score
# # # # import shap

# # # # # ─── Flask ────────────────────────────────────────────────────────────────────
# # # # from flask import Flask, jsonify, request, render_template, session
# # # # from flask_cors import CORS

# # # # # ─── Optional NLP libs ────────────────────────────────────────────────────────
# # # # NLP_AVAILABLE = False
# # # # LANG_DETECT_AVAILABLE = False

# # # # try:
# # # #     import torch
# # # #     from transformers import AutoModel, AutoTokenizer
# # # #     NLP_AVAILABLE = True
# # # # except ImportError:
# # # #     pass

# # # # try:
# # # #     from langdetect import DetectorFactory, detect as _ld_detect
# # # #     DetectorFactory.seed = 42
# # # #     LANG_DETECT_AVAILABLE = True
# # # # except ImportError:
# # # #     pass

# # # # # ─── Optional web scraping libs ───────────────────────────────────────────────
# # # # WEB_SCRAPE_AVAILABLE = False
# # # # BS4_AVAILABLE = False

# # # # try:
# # # #     import requests as http_requests
# # # #     WEB_SCRAPE_AVAILABLE = True
# # # # except ImportError:
# # # #     pass

# # # # try:
# # # #     from bs4 import BeautifulSoup, Tag
# # # #     BS4_AVAILABLE = True
# # # # except ImportError:
# # # #     pass

# # # # # ─── Flask app setup ──────────────────────────────────────────────────────────
# # # # app = Flask(__name__, template_folder="templates", static_folder="static")
# # # # app.secret_key = "basira_local_session_secret_v1"
# # # # app.config["SESSION_COOKIE_NAME"] = "basira_local_session"
# # # # app.config["SESSION_COOKIE_HTTPONLY"] = True
# # # # app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# # # # app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

# # # # CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


# # # # @app.after_request
# # # # def add_cors_headers(response):
# # # #     response.headers["Access-Control-Allow-Origin"] = "*"
# # # #     response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
# # # #     response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
# # # #     return response


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  SESSION HELPERS
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # def _build_session_payload():
# # # #     return {
# # # #         "authenticated": bool(session.get("authenticated", False)),
# # # #         "user_name": session.get("user_name", "Basira User"),
# # # #         "session_started": session.get("session_started"),
# # # #         "last_seen": session.get("last_seen"),
# # # #     }


# # # # @app.route("/", methods=["GET"])
# # # # def home():
# # # #     return render_template("basira_app.html")


# # # # @app.route("/api/session/bootstrap", methods=["GET"])
# # # # def session_bootstrap():
# # # #     if not session.get("authenticated"):
# # # #         session.permanent = True
# # # #         session["authenticated"] = True
# # # #         session["user_name"] = "Basira User"
# # # #         session["session_started"] = pd.Timestamp.utcnow().isoformat()
# # # #         session["last_seen"] = pd.Timestamp.utcnow().isoformat()
# # # #     else:
# # # #         session["last_seen"] = pd.Timestamp.utcnow().isoformat()

# # # #     return jsonify({
# # # #         "status": "success",
# # # #         "session": _build_session_payload()
# # # #     })


# # # # @app.route("/api/session/status", methods=["GET"])
# # # # def session_status():
# # # #     authenticated = bool(session.get("authenticated", False))
# # # #     if authenticated:
# # # #         session["last_seen"] = pd.Timestamp.utcnow().isoformat()

# # # #     return jsonify({
# # # #         "status": "success",
# # # #         "session": _build_session_payload()
# # # #     })


# # # # @app.route("/api/session/ping", methods=["POST"])
# # # # def session_ping():
# # # #     if not session.get("authenticated"):
# # # #         return jsonify({
# # # #             "status": "expired",
# # # #             "message": "Session expired."
# # # #         }), 401

# # # #     session.permanent = True
# # # #     session["last_seen"] = pd.Timestamp.utcnow().isoformat()

# # # #     return jsonify({
# # # #         "status": "success",
# # # #         "session": _build_session_payload()
# # # #     })


# # # # @app.route("/api/session/logout", methods=["POST"])
# # # # def session_logout():
# # # #     session.clear()
# # # #     return jsonify({
# # # #         "status": "success",
# # # #         "message": "Logged out successfully."
# # # #     })


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  GENERIC HELPERS
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # def _safe_json_value(value):
# # # #     if pd.isna(value):
# # # #         return None

# # # #     if isinstance(value, (np.integer, np.int32, np.int64)):
# # # #         return int(value)

# # # #     if isinstance(value, (np.floating, np.float32, np.float64)):
# # # #         v = float(value)
# # # #         if math.isnan(v) or math.isinf(v):
# # # #             return None
# # # #         return round(v, 6)

# # # #     if isinstance(value, np.bool_):
# # # #         return bool(value)

# # # #     return value


# # # # def _df_to_safe_records(df: pd.DataFrame) -> list:
# # # #     records = []
# # # #     for _, row in df.iterrows():
# # # #         item = {}
# # # #         for col in df.columns:
# # # #             item[col] = _safe_json_value(row[col])
# # # #         records.append(item)
# # # #     return records


# # # # def _df_to_b64_csv(df: pd.DataFrame) -> str:
# # # #     csv_buf = io.BytesIO()
# # # #     df.to_csv(csv_buf, index=False, encoding="utf-8-sig")
# # # #     return base64.b64encode(csv_buf.getvalue()).decode("ascii")


# # # # def sanitize(obj):
# # # #     if isinstance(obj, dict):
# # # #         return {k: sanitize(v) for k, v in obj.items()}
# # # #     if isinstance(obj, list):
# # # #         return [sanitize(v) for v in obj]
# # # #     if isinstance(obj, float):
# # # #         return 0 if (math.isnan(obj) or math.isinf(obj)) else round(obj, 6)
# # # #     if isinstance(obj, (np.floating, np.float32, np.float64)):
# # # #         v = float(obj)
# # # #         return 0 if (math.isnan(v) or math.isinf(v)) else round(v, 6)
# # # #     if isinstance(obj, (np.integer, np.int32, np.int64)):
# # # #         return int(obj)
# # # #     if isinstance(obj, np.bool_):
# # # #         return bool(obj)
# # # #     if obj is None:
# # # #         return 0
# # # #     return obj


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  TEMP PREPROCESSOR
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # def basira_auto_preprocessing(df: pd.DataFrame, file_name: str = "dataset.csv"):
# # # #     """
# # # #     Stable preprocessing layer used by /analyze_full and /scrape_analyze.
# # # #     """
# # # #     if df is None or df.empty:
# # # #         cleaned_df = pd.DataFrame()
# # # #         audit_df = pd.DataFrame([
# # # #             {
# # # #                 "stage": "preprocessing",
# # # #                 "column": "*",
# # # #                 "action": "empty_input",
# # # #                 "before": 0,
# # # #                 "after": 0,
# # # #                 "method": "temporary_stub",
# # # #                 "notes": f"No rows found in {file_name}"
# # # #             }
# # # #         ])
# # # #         preprocess_summary = {
# # # #             "status": "warning",
# # # #             "file_name": file_name,
# # # #             "rows_before": 0,
# # # #             "rows_after": 0,
# # # #             "message": "Input dataset is empty."
# # # #         }
# # # #         feat_df = None
# # # #         model_df = cleaned_df.copy()
# # # #         return cleaned_df, audit_df, preprocess_summary, feat_df, model_df

# # # #     cleaned_df = df.copy()
# # # #     cleaned_df = cleaned_df.replace([np.inf, -np.inf], np.nan)

# # # #     original_columns = list(cleaned_df.columns)
# # # #     cleaned_df.columns = [
# # # #         re.sub(r"\s+", "_", str(c).strip().lower())
# # # #         for c in cleaned_df.columns
# # # #     ]

# # # #     renamed_columns = [
# # # #         {"before": old, "after": new}
# # # #         for old, new in zip(original_columns, cleaned_df.columns)
# # # #         if old != new
# # # #     ]

# # # #     coerced_cols = []
# # # #     for col in cleaned_df.select_dtypes(include=[object]).columns:
# # # #         converted = pd.to_numeric(cleaned_df[col], errors="coerce")
# # # #         ratio = converted.notna().sum() / max(len(cleaned_df), 1)
# # # #         if ratio >= 0.85:
# # # #             cleaned_df[col] = converted
# # # #             coerced_cols.append(col)

# # # #     numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns.tolist()
# # # #     for col in numeric_cols:
# # # #         if cleaned_df[col].isna().any():
# # # #             median_val = cleaned_df[col].median()
# # # #             if pd.isna(median_val):
# # # #                 median_val = 0
# # # #             cleaned_df[col] = cleaned_df[col].fillna(median_val)

# # # #     categorical_cols = cleaned_df.select_dtypes(include=[object]).columns.tolist()
# # # #     for col in categorical_cols:
# # # #         if cleaned_df[col].isna().any():
# # # #             mode_val = cleaned_df[col].mode()
# # # #             fill_val = mode_val.iloc[0] if len(mode_val) > 0 else "unknown"
# # # #             cleaned_df[col] = cleaned_df[col].fillna(fill_val)

# # # #     audit_rows = [
# # # #         {
# # # #             "stage": "preprocessing",
# # # #             "column": "*",
# # # #             "action": "pass_through_cleaning",
# # # #             "before": len(df),
# # # #             "after": len(cleaned_df),
# # # #             "method": "temporary_stub",
# # # #             "notes": f"Temporary preprocessing applied for {file_name}"
# # # #         },
# # # #         {
# # # #             "stage": "preprocessing",
# # # #             "column": ",".join(coerced_cols) if coerced_cols else "*",
# # # #             "action": "numeric_coercion",
# # # #             "before": "object",
# # # #             "after": "numeric",
# # # #             "method": "pd.to_numeric >= 85%",
# # # #             "notes": f"Converted {len(coerced_cols)} column(s)"
# # # #         },
# # # #         {
# # # #             "stage": "preprocessing",
# # # #             "column": "*",
# # # #             "action": "column_normalization",
# # # #             "before": len(original_columns),
# # # #             "after": len(cleaned_df.columns),
# # # #             "method": "strip + lowercase + underscore",
# # # #             "notes": f"Renamed {len(renamed_columns)} column(s)"
# # # #         }
# # # #     ]

# # # #     audit_df = pd.DataFrame(audit_rows)

# # # #     preprocess_summary = {
# # # #         "status": "success",
# # # #         "file_name": file_name,
# # # #         "rows_before": int(len(df)),
# # # #         "rows_after": int(len(cleaned_df)),
# # # #         "cols_before": int(len(original_columns)),
# # # #         "cols_after": int(len(cleaned_df.columns)),
# # # #         "numeric_cols": int(len(cleaned_df.select_dtypes(include=[np.number]).columns)),
# # # #         "categorical_cols": int(len(cleaned_df.select_dtypes(include=[object]).columns)),
# # # #         "coerced_cols": int(len(coerced_cols)),
# # # #         "renamed_cols": int(len(renamed_columns)),
# # # #         "message": "Temporary preprocessing layer is active and working."
# # # #     }

# # # #     feat_df = None
# # # #     model_df = cleaned_df.copy()
# # # #     return cleaned_df, audit_df, preprocess_summary, feat_df, model_df


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  MODEL REGISTRY
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # _MODEL_CACHE: dict = {}

# # # # _LANG_TO_MODEL = {
# # # #     "arabic": "aubmindlab/bert-base-arabertv02",
# # # #     "english": "roberta-base",
# # # #     "mixed": "xlm-roberta-base",
# # # # }


# # # # def _load_model(lang: str):
# # # #     if not NLP_AVAILABLE:
# # # #         return None, None

# # # #     hf_id = _LANG_TO_MODEL.get(lang, _LANG_TO_MODEL["mixed"])

# # # #     if hf_id not in _MODEL_CACHE:
# # # #         try:
# # # #             print(f"[NLP] Loading model: {hf_id} …")
# # # #             tok = AutoTokenizer.from_pretrained(hf_id)
# # # #             model = AutoModel.from_pretrained(hf_id)
# # # #             model.eval()
# # # #             _MODEL_CACHE[hf_id] = (tok, model)
# # # #             print(f"[NLP] Loaded: {hf_id}")
# # # #         except Exception as exc:
# # # #             print(f"[NLP] Could not load {hf_id}: {exc}")
# # # #             _MODEL_CACHE[hf_id] = (None, None)

# # # #     return _MODEL_CACHE[hf_id]


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  ARABIC NORMALIZATION + LANGUAGE DETECTION
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # _RE_DIACRITICS = re.compile(
# # # #     r"[\u064B-\u065F"
# # # #     r"\u0610-\u061A"
# # # #     r"\u06D6-\u06DC"
# # # #     r"\u06DF-\u06E4"
# # # #     r"\u06E7-\u06ED]"
# # # # )
# # # # _RE_ALEF = re.compile(r"[إأآا]")
# # # # _RE_TA_MARBUTA = re.compile(r"ة")
# # # # _RE_TATWEEL = re.compile(r"\u0640")
# # # # _RE_WS = re.compile(r"\s+")
# # # # _RE_ARABIC_CHARS = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+")


# # # # def normalise_arabic(text: str) -> str:
# # # #     text = _RE_DIACRITICS.sub("", text)
# # # #     text = _RE_ALEF.sub("ا", text)
# # # #     text = _RE_TA_MARBUTA.sub("ه", text)
# # # #     text = _RE_TATWEEL.sub("", text)
# # # #     text = _RE_WS.sub(" ", text).strip()
# # # #     return text


# # # # _AR_HEADER_TRANSLATE = {
# # # #     "الهدف": "target", "النتيجة": "result", "الإيرادات": "revenue",
# # # #     "السعر": "price", "التكلفة": "cost", "المبيعات": "sales",
# # # #     "الطلب": "demand", "الكمية": "quantity", "المبلغ": "amount",
# # # #     "العائد": "return", "الربح": "profit", "الخسارة": "loss",
# # # #     "الإنتاج": "production", "الدرجة": "grade", "النقاط": "score",
# # # #     "الراتب": "salary", "الدخل": "income", "القيمة": "value",
# # # #     "الإجمالي": "total", "المعدل": "rate", "العدد": "quantity",
# # # # }


# # # # def translate_ar_header(col: str) -> str:
# # # #     return _AR_HEADER_TRANSLATE.get(normalise_arabic(col.strip()), col)


# # # # def detect_text_language(text: str) -> str:
# # # #     if not isinstance(text, str) or not text.strip():
# # # #         return "unknown"

# # # #     ar_len = len(_RE_ARABIC_CHARS.findall(text))
# # # #     lat_len = len(re.findall(r"[a-zA-Z]", text))
# # # #     total = ar_len + lat_len

# # # #     if total == 0:
# # # #         return "unknown"

# # # #     ar_ratio = ar_len / total

# # # #     if ar_ratio >= 0.60:
# # # #         return "arabic"
# # # #     elif ar_ratio <= 0.15:
# # # #         if LANG_DETECT_AVAILABLE:
# # # #             try:
# # # #                 detected = _ld_detect(text)
# # # #                 return "english" if detected == "en" else "mixed"
# # # #             except Exception:
# # # #                 pass
# # # #         return "english"
# # # #     else:
# # # #         return "mixed"


# # # # def detect_column_language(series: pd.Series) -> str:
# # # #     texts = series.dropna().astype(str).head(200).tolist()
# # # #     if not texts:
# # # #         return "unknown"

# # # #     counts = {"arabic": 0, "english": 0, "mixed": 0, "unknown": 0}
# # # #     for t in texts:
# # # #         counts[detect_text_language(t)] += 1

# # # #     total = sum(counts.values())
# # # #     ar_share = counts["arabic"] / total
# # # #     en_share = counts["english"] / total
# # # #     if ar_share >= 0.15 and en_share >= 0.15:
# # # #         return "mixed"

# # # #     return max(counts, key=counts.get)


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  NLP EMBEDDING ENGINE
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # def _mean_pool(last_hidden, attn_mask) -> np.ndarray:
# # # #     mask_exp = attn_mask.unsqueeze(-1).float()
# # # #     summed = (last_hidden * mask_exp).sum(dim=1)
# # # #     counts = mask_exp.sum(dim=1).clamp(min=1e-9)
# # # #     return (summed / counts).detach().numpy()


# # # # def embed_text_column(series: pd.Series, lang: str, batch_size: int = 32, max_len: int = 128):
# # # #     if not NLP_AVAILABLE:
# # # #         return None

# # # #     tok, model = _load_model(lang)
# # # #     if tok is None:
# # # #         return None

# # # #     import torch

# # # #     texts = series.fillna("").astype(str).tolist()

# # # #     if lang in ("arabic", "mixed"):
# # # #         texts = [
# # # #             normalise_arabic(t) if detect_text_language(t) in ("arabic", "mixed") else t
# # # #             for t in texts
# # # #         ]

# # # #     all_embs = []

# # # #     with torch.no_grad():
# # # #         for start in range(0, len(texts), batch_size):
# # # #             batch = texts[start:start + batch_size]
# # # #             encoded = tok(
# # # #                 batch,
# # # #                 padding=True,
# # # #                 truncation=True,
# # # #                 max_length=max_len,
# # # #                 return_tensors="pt",
# # # #             )
# # # #             out = model(**encoded)
# # # #             embs = _mean_pool(out.last_hidden_state, encoded["attention_mask"])
# # # #             all_embs.append(embs)

# # # #     matrix = np.vstack(all_embs)

# # # #     norms = np.linalg.norm(matrix, axis=1, keepdims=True)
# # # #     zero_mask = (norms.flatten() == 0)
# # # #     if zero_mask.any() and not zero_mask.all():
# # # #         col_mean = matrix[~zero_mask].mean(axis=0)
# # # #         matrix[zero_mask] = col_mean

# # # #     return matrix


# # # # def process_text_columns(df: pd.DataFrame) -> tuple:
# # # #     nlp_meta = {
# # # #         "nlp_available": NLP_AVAILABLE,
# # # #         "lang_detect_available": LANG_DETECT_AVAILABLE,
# # # #         "columns_processed": [],
# # # #         "warning": None if NLP_AVAILABLE else
# # # #         "NLP libraries not installed. Install with: pip install torch transformers langdetect sentencepiece",
# # # #     }

# # # #     text_cols = [
# # # #         c for c in df.columns
# # # #         if df[c].dtype == object
# # # #         and df[c].nunique() / max(len(df), 1) < 0.95
# # # #         and df[c].dropna().astype(str).str.len().mean() > 3
# # # #     ]

# # # #     if not text_cols or not NLP_AVAILABLE:
# # # #         return None, nlp_meta

# # # #     all_matrices = []
# # # #     all_feat_names = []

# # # #     for col in text_cols:
# # # #         lang = detect_column_language(df[col])
# # # #         model_label = {
# # # #             "arabic": "AraBERT (bert-base-arabertv02)",
# # # #             "english": "RoBERTa (roberta-base)",
# # # #             "mixed": "XLM-RoBERTa (xlm-roberta-base)",
# # # #         }.get(lang, "XLM-RoBERTa (xlm-roberta-base)")

# # # #         col_meta = {
# # # #             "column": col,
# # # #             "language": lang,
# # # #             "model_used": model_label,
# # # #             "n_non_null": int(df[col].notna().sum()),
# # # #             "sample_texts": df[col].dropna().astype(str).head(3).tolist(),
# # # #         }

# # # #         embed = embed_text_column(df[col], lang)

# # # #         if embed is not None and embed.shape[0] == len(df):
# # # #             n_components = min(8, embed.shape[1], len(df) - 1)

# # # #             if n_components >= 2:
# # # #                 pca = PCA(n_components=n_components, random_state=42)
# # # #                 embed = pca.fit_transform(embed)
# # # #                 col_meta["embedding_dims"] = n_components
# # # #                 col_meta["variance_explained_pct"] = round(
# # # #                     float(pca.explained_variance_ratio_.sum() * 100), 1
# # # #                 )
# # # #             else:
# # # #                 col_meta["embedding_dims"] = embed.shape[1]
# # # #                 col_meta["variance_explained_pct"] = 100.0

# # # #             feat_names = [f"[NLP]{col}_d{i+1}" for i in range(embed.shape[1])]
# # # #             col_meta["feature_names"] = feat_names

# # # #             all_matrices.append(embed)
# # # #             all_feat_names.extend(feat_names)

# # # #         nlp_meta["columns_processed"].append(col_meta)

# # # #     if not all_matrices:
# # # #         return None, nlp_meta

# # # #     combined = np.hstack(all_matrices)
# # # #     nlp_meta["total_nlp_features"] = combined.shape[1]
# # # #     return combined, nlp_meta


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  TARGET DETECTION
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # def auto_detect_target(numeric_df):
# # # #     cols = list(numeric_df.columns)
# # # #     if not cols:
# # # #         return None, "No numeric columns found"

# # # #     target_keywords = [
# # # #         "target", "label", "output", "result", "score", "price", "cost",
# # # #         "revenue", "sales", "demand", "value", "amount", "total", "rate",
# # # #         "return", "profit", "loss", "yield", "production", "quantity",
# # # #         "salary", "income", "churn", "default", "fraud", "grade",
# # # #     ]

# # # #     for kw in target_keywords:
# # # #         for col in cols:
# # # #             if kw.lower() in col.lower():
# # # #                 return col, (
# # # #                     f"Column '{col}' matched target keyword '{kw}'. "
# # # #                     "Confirmed as prediction target."
# # # #                 )

# # # #     for col in cols:
# # # #         translated = translate_ar_header(col)
# # # #         if translated != col:
# # # #             for kw in target_keywords:
# # # #                 if kw.lower() in translated.lower():
# # # #                     return col, (
# # # #                         f"Arabic column '{col}' translated to '{translated}' "
# # # #                         f"and matched target keyword '{kw}'."
# # # #                     )

# # # #     best_col, best_cv = None, -1.0
# # # #     for col in cols:
# # # #         col_data = numeric_df[col].dropna()
# # # #         if col_data.std() == 0 or col_data.mean() == 0 or col_data.nunique() < 3:
# # # #             continue
# # # #         cv = abs(col_data.std() / col_data.mean())
# # # #         if cv > best_cv:
# # # #             best_cv, best_col = cv, col

# # # #     if best_col:
# # # #         return best_col, (
# # # #             f"No target keyword found. '{best_col}' selected automatically "
# # # #             f"(CV = {round(best_cv*100,1)}% — highest variability, most informative to predict)."
# # # #         )

# # # #     return cols[-1], f"Defaulted to last column '{cols[-1]}' as target variable."


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  CHART RECOMMENDATIONS
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # def detect_chart_types(df, numeric_df, feature_impact, dist_data, target_col):
# # # #     charts = []
# # # #     n_features = len(feature_impact)
# # # #     impacts = [f["impact"] for f in feature_impact]
# # # #     n_rows = len(df)

# # # #     skews = (
# # # #         numeric_df.drop(columns=[target_col], errors="ignore")
# # # #         .apply(lambda c: abs(float(stats.skew(c.dropna()))) if c.dropna().std() > 0 else 0)
# # # #         .mean()
# # # #     )

# # # #     top2_sum = sum(sorted(impacts, reverse=True)[:2]) if len(impacts) >= 2 else 0
# # # #     is_pareto = top2_sum > 60
# # # #     high_variance = skews > 1.2
# # # #     large_dataset = n_rows > 1000

# # # #     if n_features <= 7:
# # # #         charts.append({
# # # #             "type": "horizontalBar",
# # # #             "title": "Feature Impact Ranking",
# # # #             "reason": "Horizontal bars are optimal for labeled features.",
# # # #             "chartData": "impact",
# # # #         })
# # # #     else:
# # # #         charts.append({
# # # #             "type": "bar",
# # # #             "title": "Impact Magnitude Matrix",
# # # #             "reason": "Vertical bar chart efficiently handles wider feature spaces.",
# # # #             "chartData": "impact",
# # # #         })

# # # #     if is_pareto:
# # # #         charts.append({
# # # #             "type": "doughnut",
# # # #             "title": "Decision Weight Allocation",
# # # #             "reason": "Top 2 features dominate, so doughnut highlights concentration clearly.",
# # # #             "chartData": "impact",
# # # #         })
# # # #     elif high_variance:
# # # #         charts.append({
# # # #             "type": "polarArea",
# # # #             "title": "Asymmetric Impact Distribution",
# # # #             "reason": "High skewness detected, polar area reveals unequal radial spread.",
# # # #             "chartData": "impact",
# # # #         })
# # # #     else:
# # # #         charts.append({
# # # #             "type": "doughnut",
# # # #             "title": "Proportional Weight Map",
# # # #             "reason": "Balanced impact distribution, doughnut provides intuitive proportional view.",
# # # #             "chartData": "impact",
# # # #         })

# # # #     if 3 <= n_features <= 10:
# # # #         charts.append({
# # # #             "type": "radar",
# # # #             "title": "Multi-Axis Feature Signature",
# # # #             "reason": "Radar chart is best for comparing influence patterns across mid-sized feature sets.",
# # # #             "chartData": "impact",
# # # #         })
# # # #     else:
# # # #         charts.append({
# # # #             "type": "line",
# # # #             "title": "Impact Decay Curve",
# # # #             "reason": "Line chart traces diminishing returns across ranked features.",
# # # #             "chartData": "impact",
# # # #         })

# # # #     top_feat = feature_impact[0]["feature"] if feature_impact else None
# # # #     if top_feat and top_feat in dist_data:
# # # #         charts.append({
# # # #             "type": "histogram",
# # # #             "title": f"Distribution: {top_feat.upper()}",
# # # #             "reason": f"Histogram shows how the primary driver '{top_feat}' is distributed.",
# # # #             "chartData": "histogram",
# # # #             "histFeature": top_feat,
# # # #         })

# # # #     if n_features >= 2:
# # # #         f1 = feature_impact[0]["feature"]
# # # #         f2 = feature_impact[1]["feature"]
# # # #         if large_dataset:
# # # #             charts.append({
# # # #                 "type": "bubble",
# # # #                 "title": f"Feature Interaction: {f1.upper()} × {f2.upper()}",
# # # #                 "reason": "Bubble chart shows joint relationship and combined magnitude.",
# # # #                 "chartData": "bubble",
# # # #                 "feat1": f1,
# # # #                 "feat2": f2,
# # # #             })
# # # #         else:
# # # #             charts.append({
# # # #                 "type": "scatter",
# # # #                 "title": f"Correlation Scatter: {f1.upper()} vs {f2.upper()}",
# # # #                 "reason": "Scatter plot exposes raw relationship between the top 2 drivers.",
# # # #                 "chartData": "scatter",
# # # #                 "feat1": f1,
# # # #                 "feat2": f2,
# # # #             })

# # # #     charts.append({
# # # #         "type": "area",
# # # #         "title": "Cumulative Feature Contribution",
# # # #         "reason": "Area chart shows how decision weight accumulates across ranked features.",
# # # #         "chartData": "cumulative",
# # # #     })

# # # #     return charts


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  ROOT CAUSE ANALYSIS + INSIGHTS + NARRATIVE
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # def compute_rca(df, numeric_df, feature_impact, shap_values, X, y, target_col):
# # # #     rca_nodes = []
# # # #     correlations = numeric_df.corr()[target_col]
# # # #     n_rows = len(X)

# # # #     feature_stats = {}
# # # #     for col in X.columns:
# # # #         col_data = X[col].dropna()
# # # #         if len(col_data) < 2:
# # # #             continue
# # # #         q1, q3 = float(col_data.quantile(0.25)), float(col_data.quantile(0.75))
# # # #         iqr = q3 - q1
# # # #         n_out = int(((col_data < q1 - 1.5*iqr) | (col_data > q3 + 1.5*iqr)).sum())

# # # #         mean_v = float(col_data.mean())
# # # #         std_v = float(col_data.std())

# # # #         def _s(v, d=4):
# # # #             return 0 if (math.isnan(v) or math.isinf(v)) else round(v, d)

# # # #         feature_stats[col] = {
# # # #             "mean": _s(mean_v),
# # # #             "std": _s(std_v),
# # # #             "min": _s(float(col_data.min())),
# # # #             "max": _s(float(col_data.max())),
# # # #             "skew": _s(float(stats.skew(col_data)), 3),
# # # #             "kurtosis": _s(float(stats.kurtosis(col_data)), 3),
# # # #             "outliers": n_out,
# # # #             "cv": _s(std_v / mean_v * 100, 1) if mean_v != 0 else 0,
# # # #         }

# # # #     for rank, item in enumerate(feature_impact[:6], 1):
# # # #         feat = item["feature"]
# # # #         if feat not in feature_stats:
# # # #             continue

# # # #         fs = feature_stats[feat]
# # # #         corr_val = round(float(correlations.get(feat, 0)), 3)
# # # #         if math.isnan(corr_val) or math.isinf(corr_val):
# # # #             corr_val = 0.0

# # # #         shap_idx = list(X.columns).index(feat)
# # # #         shap_feat = shap_values[:, shap_idx]
# # # #         shap_mean = round(float(np.mean(shap_feat)), 4)
# # # #         shap_std = round(float(np.std(shap_feat)), 4)
# # # #         shap_mean = 0 if (math.isnan(shap_mean) or math.isinf(shap_mean)) else shap_mean
# # # #         shap_std = 0 if (math.isnan(shap_std) or math.isinf(shap_std)) else shap_std
# # # #         shap_pos_pct = round(float((shap_feat > 0).sum() / max(len(shap_feat), 1) * 100), 1)

# # # #         causes = []
# # # #         severity_score = 0

# # # #         if fs["outliers"] > n_rows * 0.05:
# # # #             causes.append(
# # # #                 f"High outlier density: {fs['outliers']} records fall outside normal range and may inflate importance."
# # # #             )
# # # #             severity_score += 2

# # # #         if abs(fs["skew"]) > 1.5:
# # # #             direction = "right-skewed" if fs["skew"] > 0 else "left-skewed"
# # # #             causes.append(
# # # #                 f"Distribution is {direction} (skew={fs['skew']}). A transform may improve stability."
# # # #             )
# # # #             severity_score += 1

# # # #         if abs(fs["cv"]) > 80:
# # # #             causes.append(
# # # #                 f"Extreme variability detected (CV={fs['cv']}%). This feature behaves inconsistently across records."
# # # #             )
# # # #             severity_score += 2

# # # #         if shap_std > abs(shap_mean) * 1.5 and shap_mean != 0:
# # # #             causes.append(
# # # #                 f"Highly context-dependent influence: SHAP std={shap_std} vs mean={shap_mean}."
# # # #             )
# # # #             severity_score += 1

# # # #         if abs(corr_val) > 0.75:
# # # #             causes.append(
# # # #                 f"Strong direct linear link to target (r={corr_val})."
# # # #             )
# # # #             severity_score += 1
# # # #         elif abs(corr_val) < 0.15:
# # # #             causes.append(
# # # #                 f"Weak linear correlation (r={corr_val}) yet high SHAP importance, suggesting non-linear effects."
# # # #             )
# # # #             severity_score += 1

# # # #         if shap_pos_pct > 70:
# # # #             causes.append(
# # # #                 f"Predominantly positive effect in {shap_pos_pct}% of records."
# # # #             )
# # # #         elif shap_pos_pct < 30:
# # # #             causes.append(
# # # #                 f"Acts mainly as a suppressor in {100 - shap_pos_pct}% of records."
# # # #             )

# # # #         if not causes:
# # # #             causes.append("Stable, consistent influence with no anomalous patterns detected.")

# # # #         if item["importance_level"] == "Critical":
# # # #             recommendation = (
# # # #                 f"URGENT: '{feat}' is the strongest lever. Set up real-time monitoring and clear ownership."
# # # #             )
# # # #         elif item["importance_level"] == "High":
# # # #             recommendation = (
# # # #                 f"MONITOR: '{feat}' contributes materially to decisions. Establish review thresholds."
# # # #             )
# # # #         else:
# # # #             recommendation = (
# # # #                 f"TRACK: '{feat}' is a supporting variable. Include it in normal review cycles."
# # # #             )

# # # #         rca_nodes.append({
# # # #             "rank": rank,
# # # #             "feature": feat,
# # # #             "impact": item["impact"],
# # # #             "trend": item["trend"],
# # # #             "importance_level": item["importance_level"],
# # # #             "corr_with_target": corr_val,
# # # #             "shap_mean": shap_mean,
# # # #             "shap_std": shap_std,
# # # #             "shap_pos_pct": shap_pos_pct,
# # # #             "stats": fs,
# # # #             "root_causes": causes,
# # # #             "recommendation": recommendation,
# # # #             "severity_score": severity_score,
# # # #         })

# # # #     return rca_nodes


# # # # def compute_advanced_insights(df, numeric_df, feature_impact, shap_values, X, y, target_col, model_r2):
# # # #     insights = []
# # # #     n_rows = len(df)
# # # #     n_cols = len(df.columns)

# # # #     missing_pct = round(df.isnull().sum().sum() / (n_rows * n_cols) * 100, 1)
# # # #     dup_rows = int(df.duplicated().sum())
# # # #     top = feature_impact[0]
# # # #     second = feature_impact[1] if len(feature_impact) > 1 else feature_impact[0]

# # # #     def _sf(v):
# # # #         if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
# # # #             return 0
# # # #         return v

# # # #     target_skew = _sf(round(float(stats.skew(y)), 2))
# # # #     target_std = _sf(round(float(y.std()), 3))
# # # #     y_mean = float(y.mean())
# # # #     target_cv = _sf(round(float(y.std() / y_mean * 100), 1)) if y_mean != 0 else 0

# # # #     try:
# # # #         contamination = min(0.05, max(0.01, 1.0 / max(n_rows, 2)))
# # # #         iso = IsolationForest(contamination=contamination, random_state=42)
# # # #         iso.fit(X)
# # # #         n_anomalies = int((iso.predict(X) == -1).sum())
# # # #     except Exception:
# # # #         n_anomalies = 0
# # # #     anomaly_pct = round(n_anomalies / n_rows * 100, 1)

# # # #     total_shap = sum(np.abs(shap_values[:, i]).mean() for i in range(X.shape[1]))
# # # #     top3_shap = sum(np.abs(shap_values[:, i]).mean() for i in range(min(3, X.shape[1])))
# # # #     top3_conc = round(top3_shap / total_shap * 100, 1) if total_shap > 0 else 0

# # # #     inter_r = 0.0
# # # #     f1, f2 = top["feature"], second["feature"]
# # # #     if f1 in X.columns and f2 in X.columns:
# # # #         inter_r = _sf(round(float(abs(X[f1].corr(X[f2]))), 3))

# # # #     if model_r2 >= 80:
# # # #         desc = f"The model explains {model_r2}% of outcome variation."
# # # #         action = "✓ High confidence — insights are decision-ready"
# # # #         color = "#22c55e"
# # # #     elif model_r2 >= 55:
# # # #         desc = f"The model achieves {model_r2}% explanation power."
# # # #         action = "⚠ Use with caution — validate key findings"
# # # #         color = "#f59e0b"
# # # #     else:
# # # #         desc = f"The model explains only {model_r2}% of variance."
# # # #         action = "⚠ Low confidence — explore additional data sources"
# # # #         color = "#ef4444"

# # # #     insights.append({
# # # #         "id": "model_reliability", "title": "MODEL RELIABILITY SCORE",
# # # #         "value": f"{model_r2}%", "metric": "Cross-validated R² score",
# # # #         "desc": desc, "action": action, "color": color
# # # #     })

# # # #     direction = "increases" if top["trend"] == "Positive" else "decreases"
# # # #     insights.append({
# # # #         "id": "primary_driver", "title": "PRIMARY DECISION DRIVER",
# # # #         "value": top["feature"].upper(), "metric": f"{top['impact']}% of all predictive weight",
# # # #         "desc": (
# # # #             f"'{top['feature']}' has the strongest influence on outcomes. "
# # # #             f"When this value {direction}, your target outcome tends to move accordingly."
# # # #         ),
# # # #         "action": "Set up real-time alerts for this variable", "color": "#0ea5e9",
# # # #     })

# # # #     if anomaly_pct > 8:
# # # #         desc = f"A significant {anomaly_pct}% of records ({n_anomalies} rows) were flagged as anomalous."
# # # #         action = "🚨 Investigate flagged records immediately"
# # # #         color = "#ef4444"
# # # #     else:
# # # #         desc = f"{n_anomalies} anomalous records ({anomaly_pct}%) — within acceptable limits."
# # # #         action = "✓ Anomaly rate acceptable — proceed normally"
# # # #         color = "#10b981"

# # # #     insights.append({
# # # #         "id": "anomaly_alert", "title": "ANOMALY DETECTION",
# # # #         "value": f"{n_anomalies} Records", "metric": f"{anomaly_pct}% of dataset flagged",
# # # #         "desc": desc, "action": action, "color": color
# # # #     })

# # # #     if top3_conc > 80:
# # # #         desc = f"Model decisions are heavily concentrated: top 3 features drive {top3_conc}%."
# # # #         action = "⚠ Risk: over-reliance on 3 variables"
# # # #         color = "#f59e0b"
# # # #     elif top3_conc > 60:
# # # #         desc = f"Top 3 features account for {top3_conc}% — moderate concentration."
# # # #         action = "Monitor top 3 features closely"
# # # #         color = "#6366f1"
# # # #     else:
# # # #         desc = f"Decision weight is well-distributed (top 3 = {top3_conc}%)."
# # # #         action = "✓ Healthy — balanced feature utilisation"
# # # #         color = "#22c55e"

# # # #     insights.append({
# # # #         "id": "complexity", "title": "DECISION CONCENTRATION RISK",
# # # #         "value": f"{top3_conc}%", "metric": "Top 3 features drive this share",
# # # #         "desc": desc, "action": action, "color": color
# # # #     })

# # # #     quality = round(100 - missing_pct - (dup_rows / n_rows * 100), 1)
# # # #     if quality >= 95:
# # # #         desc = f"Excellent dataset: {quality}% quality score."
# # # #         action = "✓ Dataset passes all quality checks"
# # # #         color = "#22c55e"
# # # #     elif quality >= 80:
# # # #         desc = f"Acceptable quality at {quality}%."
# # # #         action = "⚠ Investigate missing data sources"
# # # #         color = "#f59e0b"
# # # #     else:
# # # #         desc = f"Concerning quality at {quality}%."
# # # #         action = "🚨 Clean dataset before production use"
# # # #         color = "#ef4444"

# # # #     insights.append({
# # # #         "id": "data_quality", "title": "DATA INTEGRITY SCORE",
# # # #         "value": f"{quality}%", "metric": f"{missing_pct}% missing · {dup_rows} duplicates",
# # # #         "desc": desc, "action": action, "color": color
# # # #     })

# # # #     if target_cv > 60:
# # # #         desc = f"Target '{target_col}' is highly volatile (CV={target_cv}%)."
# # # #         action = "⚠ High variance — widen prediction confidence intervals"
# # # #     elif target_cv > 30:
# # # #         desc = f"Target '{target_col}' shows moderate variability (CV={target_cv}%)."
# # # #         action = "Normal variance — predictions reliable on average"
# # # #     else:
# # # #         desc = f"Target '{target_col}' is quite stable (CV={target_cv}%)."
# # # #         action = "✓ Low variance — high prediction confidence"

# # # #     insights.append({
# # # #         "id": "target_volatility", "title": "TARGET VOLATILITY INDEX",
# # # #         "value": f"CV: {target_cv}%", "metric": f"σ={target_std} · Skew={target_skew}",
# # # #         "desc": desc, "action": action, "color": "#8b5cf6"
# # # #     })

# # # #     combined = round(top["impact"] + second["impact"], 1)
# # # #     if inter_r > 0.6:
# # # #         desc = f"'{f1}' and '{f2}' are strongly correlated (r={inter_r})."
# # # #         action = "⚠ Collinearity risk — consider removing one"
# # # #         color = "#f59e0b"
# # # #     else:
# # # #         desc = f"'{f1}' and '{f2}' contribute independently (r={inter_r})."
# # # #         action = "✓ Features contribute independently"
# # # #         color = "#6366f1"

# # # #     insights.append({
# # # #         "id": "feature_interaction", "title": "TOP-2 FEATURE SYNERGY",
# # # #         "value": f"r = {inter_r}", "metric": f"{combined}% combined decision weight",
# # # #         "desc": desc, "action": action, "color": color
# # # #     })

# # # #     return insights


# # # # def generate_decision_narrative(feature_impact, rca_report, insights, target_col, model_r2, n_rows, anomaly_pct):
# # # #     top = feature_impact[0]
# # # #     top2 = feature_impact[1] if len(feature_impact) > 1 else feature_impact[0]
# # # #     conf = "high" if model_r2 >= 75 else "moderate" if model_r2 >= 50 else "low"

# # # #     return {
# # # #         "headline": "Your dataset has been fully analyzed. Here is what the data is telling you.",
# # # #         "summary": (
# # # #             f"This analysis examined {n_rows:,} records to understand what drives '{target_col}'. "
# # # #             f"The AI model explains {model_r2}% of outcome variation, giving {conf} confidence."
# # # #         ),
# # # #         "key_finding": (
# # # #             f"The single most important factor is '{top['feature']}', "
# # # #             f"which carries {top['impact']}% of all predictive weight."
# # # #         ),
# # # #         "secondary_finding": (
# # # #             f"The second most influential factor is '{top2['feature']}' at {top2['impact']}% weight."
# # # #         ),
# # # #         "risk_alert": (
# # # #             f"⚠ ATTENTION: {round(anomaly_pct)}% of records show unusual patterns."
# # # #             if anomaly_pct > 8 else
# # # #             "✓ No major anomaly risks detected. The data is clean enough for confident decision-making."
# # # #         ),
# # # #         "recommended_action": (
# # # #             f"Focus immediate effort on monitoring and controlling '{top['feature']}'."
# # # #         ),
# # # #     }


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  SHARED ANALYSIS PIPELINE
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # def run_analysis_pipeline(df: pd.DataFrame) -> dict:
# # # #     missing_total = int(df.isnull().sum().sum())
# # # #     dup_rows = int(df.duplicated().sum())

# # # #     df_clean = df.replace([np.inf, -np.inf], np.nan)

# # # #     for col in df_clean.select_dtypes(include=[object]).columns:
# # # #         converted = pd.to_numeric(df_clean[col], errors="coerce")
# # # #         ratio = converted.notna().sum() / max(len(df_clean), 1)
# # # #         if ratio >= 0.85:
# # # #             df_clean[col] = converted

# # # #     df_clean = df_clean.fillna(0)

# # # #     if len(df_clean) < 5:
# # # #         raise ValueError(
# # # #             f"Dataset has only {len(df_clean)} rows. At least 5 rows are required for meaningful analysis."
# # # #         )

# # # #     text_matrix, nlp_metadata = process_text_columns(df_clean)

# # # #     numeric_df = df_clean.select_dtypes(include=[np.number])

# # # #     constant_cols = [c for c in numeric_df.columns if numeric_df[c].std() == 0]
# # # #     if constant_cols:
# # # #         numeric_df = numeric_df.drop(columns=constant_cols)

# # # #     if numeric_df.empty or numeric_df.shape[1] < 2:
# # # #         raise ValueError(
# # # #             "Dataset needs at least 2 non-constant numeric columns for analysis."
# # # #         )

# # # #     target_col, target_reason = auto_detect_target(numeric_df)
# # # #     feature_cols = [c for c in numeric_df.columns if c != target_col]

# # # #     if not feature_cols:
# # # #         raise ValueError(
# # # #             "Only one usable numeric column found. At least 2 numeric columns are needed."
# # # #         )

# # # #     X_num = numeric_df[feature_cols]
# # # #     y = numeric_df[target_col]

# # # #     nlp_feat_names = []
# # # #     for cm in nlp_metadata.get("columns_processed", []):
# # # #         nlp_feat_names.extend(cm.get("feature_names", []))

# # # #     if (
# # # #         text_matrix is not None
# # # #         and text_matrix.shape[0] == len(X_num)
# # # #         and len(nlp_feat_names) == text_matrix.shape[1]
# # # #     ):
# # # #         nlp_df = pd.DataFrame(text_matrix, columns=nlp_feat_names, index=X_num.index)
# # # #         X = pd.concat([X_num, nlp_df], axis=1)
# # # #         nlp_metadata["features_added"] = len(nlp_feat_names)
# # # #     else:
# # # #         X = X_num

# # # #     X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

# # # #     n_estimators = min(80, max(10, len(X) * 2))
# # # #     model = RandomForestRegressor(
# # # #         n_estimators=n_estimators,
# # # #         random_state=42,
# # # #         max_depth=min(12, len(X) // 2 + 1),
# # # #         n_jobs=-1
# # # #     )
# # # #     model.fit(X, y)

# # # #     explainer = shap.TreeExplainer(model)
# # # #     shap_values = explainer.shap_values(X)

# # # #     all_frame = pd.concat([X, y], axis=1)
# # # #     correlations = all_frame.corr()[target_col]
# # # #     raw_impacts = [np.abs(shap_values[:, i]).mean() for i in range(X.shape[1])]
# # # #     total_impact = sum(raw_impacts) or 1

# # # #     feature_impact = []
# # # #     for i, col in enumerate(X.columns):
# # # #         pct = round((raw_impacts[i] / total_impact) * 100, 1)
# # # #         corr_val = float(correlations.get(col, 0))
# # # #         trend = "Positive" if corr_val >= 0 else "Negative"
# # # #         level = "Critical" if pct > 25 else "High" if pct > 10 else "Standard"
# # # #         feature_impact.append({
# # # #             "feature": col,
# # # #             "impact": pct,
# # # #             "trend": trend,
# # # #             "importance_level": level,
# # # #             "is_nlp": col.startswith("[NLP]"),
# # # #         })
# # # #     feature_impact.sort(key=lambda x: x["impact"], reverse=True)

# # # #     dist_data = {}
# # # #     for col in X_num.columns[:6]:
# # # #         col_data = X_num[col].dropna()
# # # #         hist, edges = np.histogram(col_data, bins=12)
# # # #         dist_data[col] = {
# # # #             "bins": [round(float(e), 3) for e in edges[:-1]],
# # # #             "counts": [int(h) for h in hist],
# # # #             "labels": [str(round(float(e), 2)) for e in edges[:-1]],
# # # #         }

# # # #     scatter_data = {}
# # # #     top_num_feats = [f["feature"] for f in feature_impact if not f["is_nlp"] and f["feature"] in X_num.columns]
# # # #     if len(top_num_feats) >= 2:
# # # #         f1, f2 = top_num_feats[0], top_num_feats[1]
# # # #         sample_idx = np.random.choice(len(X), min(300, len(X)), replace=False)
# # # #         fi1 = list(X.columns).index(f1)
# # # #         scatter_data = {
# # # #             "feat1": f1,
# # # #             "feat2": f2,
# # # #             "points": [
# # # #                 {
# # # #                     "x": round(float(X[f1].iloc[i]), 4),
# # # #                     "y": round(float(X[f2].iloc[i]), 4),
# # # #                     "r": round(float(abs(shap_values[i, fi1])) * 10 + 4, 1),
# # # #                 }
# # # #                 for i in sample_idx
# # # #             ],
# # # #         }

# # # #     sorted_impacts = sorted([f["impact"] for f in feature_impact], reverse=True)
# # # #     cum, running = [], 0
# # # #     for v in sorted_impacts:
# # # #         running += v
# # # #         cum.append(round(running, 1))

# # # #     chart_recommendations = detect_chart_types(
# # # #         df_clean, numeric_df, feature_impact, dist_data, target_col
# # # #     )

# # # #     n_splits = max(2, min(5, len(X) // 2))
# # # #     try:
# # # #         cv_scores = cross_val_score(model, X, y, cv=n_splits, scoring="r2")
# # # #         model_r2 = max(0.0, min(100.0, round(float(np.nanmean(cv_scores)) * 100, 1)))
# # # #     except Exception:
# # # #         y_pred = model.predict(X)
# # # #         ss_res = float(np.sum((y - y_pred) ** 2))
# # # #         ss_tot = float(np.sum((y - y.mean()) ** 2))
# # # #         model_r2 = max(0.0, min(100.0, round((1 - ss_res / max(ss_tot, 1e-9)) * 100, 1)))

# # # #     advanced_insights = compute_advanced_insights(
# # # #         df_clean, numeric_df, feature_impact, shap_values, X, y, target_col, model_r2
# # # #     )

# # # #     rca_report = compute_rca(
# # # #         df_clean, numeric_df, feature_impact, shap_values, X, y, target_col
# # # #     )

# # # #     anomaly_pct_val = 0.0
# # # #     for ins in advanced_insights:
# # # #         if ins["id"] == "anomaly_alert":
# # # #             try:
# # # #                 anomaly_pct_val = float(ins["metric"].split("%")[0])
# # # #             except Exception:
# # # #                 pass

# # # #     decision_narrative = generate_decision_narrative(
# # # #         feature_impact, rca_report, advanced_insights,
# # # #         target_col, model_r2, len(df), anomaly_pct_val,
# # # #     )

# # # #     top_feats = [f["feature"] for f in feature_impact[:7] if not f["is_nlp"] and f["feature"] in numeric_df.columns]
# # # #     sub_cols = list(dict.fromkeys(top_feats + [target_col]))
# # # #     sub_cols = [c for c in sub_cols if c in numeric_df.columns]
# # # #     corr_matrix = []
# # # #     if len(sub_cols) >= 2:
# # # #         sub = numeric_df[sub_cols].corr()
# # # #         for r in sub.index:
# # # #             for c in sub.columns:
# # # #                 corr_matrix.append({"row": r, "col": c, "value": round(float(sub.loc[r, c]), 3)})

# # # #     preview_records = []
# # # #     for _, row in df.head(10).iterrows():
# # # #         rec = {}
# # # #         for col in df.columns:
# # # #             v = row[col]
# # # #             if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
# # # #                 rec[col] = "—"
# # # #             elif pd.isna(v):
# # # #                 rec[col] = "—"
# # # #             elif isinstance(v, np.integer):
# # # #                 rec[col] = int(v)
# # # #             elif isinstance(v, np.floating):
# # # #                 rec[col] = round(float(v), 4)
# # # #             else:
# # # #                 rec[col] = v
# # # #         preview_records.append(rec)

# # # #     return sanitize({
# # # #         "status": "success",
# # # #         "preview": preview_records,
# # # #         "xai_report": feature_impact,
# # # #         "chart_recommendations": chart_recommendations,
# # # #         "advanced_insights": advanced_insights,
# # # #         "rca_report": rca_report,
# # # #         "corr_matrix": corr_matrix,
# # # #         "dist_data": dist_data,
# # # #         "scatter_data": scatter_data,
# # # #         "cumulative_data": {
# # # #             "values": cum,
# # # #             "labels": [f["feature"] for f in feature_impact[:len(cum)]],
# # # #         },
# # # #         "model_score": model_r2,
# # # #         "decision_narrative": decision_narrative,
# # # #         "target_detection": {"column": target_col, "reason": target_reason},
# # # #         "nlp_analysis": nlp_metadata,
# # # #         "dataset_meta": {
# # # #             "rows": len(df),
# # # #             "cols": len(df.columns),
# # # #             "numeric_cols": len(numeric_df.columns),
# # # #             "missing_total": missing_total,
# # # #             "duplicate_rows": dup_rows,
# # # #             "target_column": target_col,
# # # #             "target_reason": target_reason,
# # # #             "nlp_text_cols": len(nlp_metadata.get("columns_processed", [])),
# # # #         },
# # # #     })


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  FILE READING HELPER
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # def read_uploaded_dataframe(file):
# # # #     filename = (file.filename or "").lower()

# # # #     if filename.endswith((".xlsx", ".xls")):
# # # #         return pd.read_excel(file)

# # # #     raw = file.read()
# # # #     for sep in [",", ";", "\t", "|"]:
# # # #         try:
# # # #             df = pd.read_csv(io.BytesIO(raw), sep=sep, engine="python")
# # # #             if df.shape[1] >= 2:
# # # #                 return df
# # # #         except Exception:
# # # #             continue

# # # #     return pd.read_csv(io.BytesIO(raw))


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  ROUTE — /analyze
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # @app.route("/analyze", methods=["POST", "OPTIONS"])
# # # # def analyze():
# # # #     if request.method == "OPTIONS":
# # # #         return "", 200

# # # #     try:
# # # #         if "file" not in request.files:
# # # #             return jsonify({"status": "error", "message": "No file uploaded"}), 400

# # # #         file = request.files["file"]

# # # #         try:
# # # #             df = read_uploaded_dataframe(file)
# # # #         except Exception as read_err:
# # # #             return jsonify({
# # # #                 "status": "error",
# # # #                 "message": (
# # # #                     f"Could not read file '{file.filename}'. "
# # # #                     f"Supported formats: CSV (.csv) and Excel (.xlsx, .xls). "
# # # #                     f"Detail: {read_err}"
# # # #                 )
# # # #             }), 400

# # # #         payload = run_analysis_pipeline(df)
# # # #         payload["dataset_meta"]["source"] = "file_upload"
# # # #         payload["dataset_meta"]["file_name"] = file.filename or "uploaded_file"

# # # #         return jsonify(payload)

# # # #     except ValueError as ve:
# # # #         return jsonify({"status": "error", "message": str(ve)}), 400
# # # #     except Exception as exc:
# # # #         import traceback
# # # #         traceback.print_exc()
# # # #         return jsonify({"status": "error", "message": str(exc)}), 500


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  ROUTE — /analyze_full
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # @app.route("/analyze_full", methods=["POST", "OPTIONS"])
# # # # def analyze_full():
# # # #     if request.method == "OPTIONS":
# # # #         return "", 200

# # # #     try:
# # # #         if "file" not in request.files:
# # # #             return jsonify({"status": "error", "message": "No file uploaded"}), 400

# # # #         file = request.files["file"]

# # # #         try:
# # # #             df_raw = read_uploaded_dataframe(file)
# # # #         except Exception as read_err:
# # # #             return jsonify({
# # # #                 "status": "error",
# # # #                 "message": (
# # # #                     f"Could not read file '{file.filename}'. "
# # # #                     f"Supported: CSV (.csv) and Excel (.xlsx, .xls). "
# # # #                     f"Detail: {read_err}"
# # # #                 )
# # # #             }), 400

# # # #         if df_raw.empty:
# # # #             return jsonify({"status": "error", "message": "Uploaded file is empty."}), 400

# # # #         try:
# # # #             cleaned_df, audit_df, preprocess_summary, _, _ = basira_auto_preprocessing(
# # # #                 df_raw, file.filename or "upload.csv"
# # # #             )
# # # #         except Exception as pp_err:
# # # #             cleaned_df = df_raw
# # # #             audit_df = pd.DataFrame()
# # # #             preprocess_summary = {"warning": str(pp_err)}

# # # #         payload = run_analysis_pipeline(cleaned_df)
# # # #         payload["dataset_meta"]["source"] = "file_upload_preprocessed"
# # # #         payload["dataset_meta"]["file_name"] = file.filename or "uploaded_file"
# # # #         payload["preprocessing_summary"] = preprocess_summary
# # # #         payload["preprocessing_audit_preview"] = _df_to_safe_records(audit_df.head(20)) if not audit_df.empty else []

# # # #         return jsonify(payload)

# # # #     except ValueError as ve:
# # # #         return jsonify({"status": "error", "message": str(ve)}), 400
# # # #     except Exception as exc:
# # # #         import traceback
# # # #         traceback.print_exc()
# # # #         return jsonify({"status": "error", "message": str(exc)}), 500


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  SMART SCRAPER
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # _UA_LIST = [
# # # #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
# # # #     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
# # # #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
# # # #     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
# # # # ]


# # # # def _fetch_page(url: str, timeout: int = 30) -> tuple:
# # # #     parsed = _urlparse(url)
# # # #     referer = f"{parsed.scheme}://{parsed.netloc}/"

# # # #     for ua in _UA_LIST:
# # # #         headers = {
# # # #             "User-Agent": ua,
# # # #             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
# # # #             "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
# # # #             "Accept-Encoding": "gzip, deflate, br",
# # # #             "Referer": referer,
# # # #             "DNT": "1",
# # # #             "Connection": "keep-alive",
# # # #             "Upgrade-Insecure-Requests": "1",
# # # #             "Cache-Control": "max-age=0",
# # # #         }
# # # #         try:
# # # #             sess = http_requests.Session()
# # # #             sess.headers.update(headers)
# # # #             if parsed.path and parsed.path != "/":
# # # #                 try:
# # # #                     sess.get(referer, timeout=8, allow_redirects=True)
# # # #                 except Exception:
# # # #                     pass
# # # #             resp = sess.get(url, timeout=timeout, allow_redirects=True)
# # # #             if resp.status_code in (200, 206):
# # # #                 return resp.text, resp.url, None
# # # #             if resp.status_code == 403:
# # # #                 continue
# # # #             resp.raise_for_status()
# # # #             return resp.text, resp.url, None
# # # #         except http_requests.exceptions.RequestException:
# # # #             continue
# # # #         except Exception as e:
# # # #             return None, url, str(e)

# # # #     return None, url, "Site blocked automated access (403). Try a different URL."


# # # # def _score_df(df: pd.DataFrame) -> float:
# # # #     if df is None or df.empty or len(df) < 2:
# # # #         return 0.0
# # # #     rows = len(df)
# # # #     cols = len(df.columns)
# # # #     num_cols = df.select_dtypes(include=[np.number]).shape[1]
# # # #     fill_rate = df.notna().mean().mean()
# # # #     return (rows * 0.4 + cols * 1.5 + num_cols * 2.0 + fill_rate * 5.0)


# # # # def _strat_html_tables(html: str) -> list:
# # # #     try:
# # # #         dfs = pd.read_html(io.StringIO(html))
# # # #         return [d for d in dfs if len(d) >= 2]
# # # #     except Exception:
# # # #         return []


# # # # def _strat_jsonld(html: str) -> list:
# # # #     if not BS4_AVAILABLE:
# # # #         return []

# # # #     soup = BeautifulSoup(html, "lxml")
# # # #     results = []
# # # #     for tag in soup.find_all("script", type="application/ld+json"):
# # # #         try:
# # # #             data = _json.loads(tag.string or "")
# # # #         except Exception:
# # # #             continue

# # # #         if isinstance(data, dict) and "@graph" in data:
# # # #             data = data["@graph"]

# # # #         items = data if isinstance(data, list) else [data]
# # # #         rows = []
# # # #         for item in items:
# # # #             if not isinstance(item, dict):
# # # #                 continue
# # # #             row = {}
# # # #             for k, v in item.items():
# # # #                 if k.startswith("@"):
# # # #                     continue
# # # #                 if isinstance(v, (str, int, float, bool)):
# # # #                     row[k] = v
# # # #                 elif isinstance(v, dict):
# # # #                     for sk, sv in v.items():
# # # #                         if isinstance(sv, (str, int, float)):
# # # #                             row[f"{k}_{sk}"] = sv
# # # #                 elif isinstance(v, list) and all(isinstance(x, (str, int, float)) for x in v):
# # # #                     row[k] = ", ".join(str(x) for x in v)
# # # #             if row:
# # # #                 rows.append(row)
# # # #         if len(rows) >= 2:
# # # #             results.append(pd.DataFrame(rows))
# # # #     return results


# # # # def _extract_element_fields(el) -> dict:
# # # #     row = {}

# # # #     word_ratings = {
# # # #         "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
# # # #         "one-star": 1, "two-star": 2, "three-star": 3, "four-star": 4, "five-star": 5
# # # #     }

# # # #     rating_el = el.find(attrs={"class": re.compile(r"rating|star|score|rate", re.I)})
# # # #     if rating_el:
# # # #         cls_str = " ".join(rating_el.get("class", [])).lower()
# # # #         txt = rating_el.get("title") or rating_el.get("aria-label") or rating_el.get_text(strip=True) or ""
# # # #         for word, val in word_ratings.items():
# # # #             if word in cls_str.split():
# # # #                 row["rating"] = val
# # # #                 break
# # # #         if "rating" not in row:
# # # #             nums = re.findall(r"\d+\.?\d*", txt)
# # # #             if nums:
# # # #                 row["rating"] = float(nums[0])

# # # #     price_el = el.find(attrs={"class": re.compile(r"price|cost|amount", re.I)})
# # # #     if price_el:
# # # #         txt = price_el.get_text(strip=True)
# # # #         nums = re.findall(r"[\d,]+\.?\d*", txt.replace(",", ""))
# # # #         if nums:
# # # #             try:
# # # #                 row["price"] = float(nums[0])
# # # #             except Exception:
# # # #                 row["price"] = txt

# # # #     for heading in el.find_all(["h1", "h2", "h3", "h4", "h5", "a", "p"], limit=5):
# # # #         txt = heading.get_text(strip=True)
# # # #         if txt and 3 < len(txt) < 200:
# # # #             attr_cls = " ".join(heading.get("class", []))
# # # #             if re.search(r"title|name|header|heading|product", attr_cls, re.I):
# # # #                 row.setdefault("title", txt)
# # # #                 break

# # # #     if "title" not in row:
# # # #         for heading in el.find_all(["h1", "h2", "h3", "h4", "h5"], limit=3):
# # # #             txt = heading.get_text(strip=True)
# # # #             if txt and 3 < len(txt) < 200:
# # # #                 row["title"] = txt
# # # #                 break

# # # #     for child in el.find_all(True):
# # # #         cls = " ".join(child.get("class", [])).lower()
# # # #         txt = child.get_text(strip=True)
# # # #         if not txt or len(txt) > 300:
# # # #             continue
# # # #         for field in [
# # # #             "category", "genre", "author", "brand", "location", "date",
# # # #             "description", "review", "comment", "status", "availability",
# # # #             "count", "total", "stock", "type", "label", "tag"
# # # #         ]:
# # # #             if field in cls and field not in row:
# # # #                 row[field] = txt
# # # #                 break

# # # #     img = el.find("img")
# # # #     if img and "title" not in row:
# # # #         alt = img.get("alt", "").strip()
# # # #         if alt and len(alt) > 2:
# # # #             row["title"] = alt

# # # #     return row


# # # # def _strat_repeated_elements(html: str) -> list:
# # # #     if not BS4_AVAILABLE:
# # # #         return []

# # # #     soup = BeautifulSoup(html, "lxml")
# # # #     results = []

# # # #     from collections import Counter
# # # #     combos = Counter()
# # # #     for el in soup.find_all(True):
# # # #         if not isinstance(el, Tag):
# # # #             continue
# # # #         cls = " ".join(sorted(el.get("class", [])))
# # # #         if cls:
# # # #             combos[(el.name, cls)] += 1

# # # #     candidates = [(tag, cls, count) for (tag, cls), count in combos.items() if count >= 5]
# # # #     candidates.sort(key=lambda x: -x[2])

# # # #     seen_selectors = set()
# # # #     for tag_name, cls_str, count in candidates[:10]:
# # # #         cls_list = cls_str.split()
# # # #         primary_cls = cls_list[0] if cls_list else ""
# # # #         if not primary_cls or primary_cls in seen_selectors:
# # # #             continue
# # # #         seen_selectors.add(primary_cls)

# # # #         elements = soup.find_all(tag_name, class_=lambda c: c and primary_cls in c)
# # # #         if len(elements) < 5:
# # # #             continue

# # # #         rows = []
# # # #         for el in elements:
# # # #             row = _extract_element_fields(el)
# # # #             if row:
# # # #                 rows.append(row)

# # # #         if len(rows) >= 5:
# # # #             df = pd.DataFrame(rows)
# # # #             df = df.loc[:, df.nunique() > 1]
# # # #             if len(df.columns) >= 2:
# # # #                 results.append(df)

# # # #     return results


# # # # def _strat_lists(html: str) -> list:
# # # #     if not BS4_AVAILABLE:
# # # #         return []

# # # #     soup = BeautifulSoup(html, "lxml")
# # # #     results = []

# # # #     for ul in soup.find_all(["ul", "ol"]):
# # # #         items = ul.find_all("li", recursive=False)
# # # #         if len(items) < 5:
# # # #             continue
# # # #         rows = []
# # # #         for li in items:
# # # #             row = _extract_element_fields(li)
# # # #             if not row:
# # # #                 txt = li.get_text(strip=True)
# # # #                 if txt and len(txt) > 2:
# # # #                     row = {"item": txt}
# # # #             if row:
# # # #                 rows.append(row)
# # # #         if len(rows) >= 5:
# # # #             df = pd.DataFrame(rows)
# # # #             if len(df.columns) >= 1 and len(df) >= 5:
# # # #                 results.append(df)

# # # #     return results


# # # # def _strat_meta(html: str, url: str) -> list:
# # # #     if not BS4_AVAILABLE:
# # # #         return []

# # # #     soup = BeautifulSoup(html, "lxml")
# # # #     row = {"url": url}

# # # #     title_tag = soup.find("title")
# # # #     if title_tag:
# # # #         row["page_title"] = title_tag.get_text(strip=True)

# # # #     for meta in soup.find_all("meta"):
# # # #         name = meta.get("name") or meta.get("property") or ""
# # # #         content = meta.get("content") or ""
# # # #         if not content or not name:
# # # #             continue
# # # #         name = name.lower().replace("og:", "og_").replace(":", "_")
# # # #         if name in ("description", "keywords", "author", "og_title", "og_description", "og_type", "og_site_name"):
# # # #             row[name] = content[:300]

# # # #     headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"]) if h.get_text(strip=True)]
# # # #     if headings:
# # # #         row["headings"] = " | ".join(headings[:10])

# # # #     row["link_count"] = len(soup.find_all("a", href=True))
# # # #     row["image_count"] = len(soup.find_all("img"))
# # # #     row["word_count"] = len((soup.get_text() or "").split())

# # # #     return [pd.DataFrame([row])] if len(row) > 3 else []


# # # # def _flatten_json_to_rows(obj, depth=0, max_depth=5) -> list:
# # # #     if depth > max_depth:
# # # #         return []
# # # #     if isinstance(obj, list):
# # # #         dicts = [x for x in obj if isinstance(x, dict)]
# # # #         if len(dicts) >= 3:
# # # #             rows = []
# # # #             for d in dicts:
# # # #                 row = {}
# # # #                 for k, v in d.items():
# # # #                     if isinstance(v, (str, int, float, bool)):
# # # #                         row[k] = v
# # # #                     elif isinstance(v, dict):
# # # #                         for sk, sv in v.items():
# # # #                             if isinstance(sv, (str, int, float)):
# # # #                                 row[f"{k}_{sk}"] = sv
# # # #                 if row:
# # # #                     rows.append(row)
# # # #             if rows:
# # # #                 return rows
# # # #     if isinstance(obj, dict):
# # # #         best = []
# # # #         for v in obj.values():
# # # #             candidate = _flatten_json_to_rows(v, depth + 1, max_depth)
# # # #             if len(candidate) > len(best):
# # # #                 best = candidate
# # # #         return best
# # # #     return []


# # # # def _strat_js_hints(html: str, url: str) -> list:
# # # #     if not BS4_AVAILABLE:
# # # #         return []

# # # #     soup = BeautifulSoup(html, "lxml")
# # # #     results = []

# # # #     patterns = [
# # # #         re.compile(r'window\.__(?:INITIAL|NEXT|REDUX|APP|STORE|DATA)_(?:DATA|STATE)__\s*=\s*(\{.*?\});', re.S),
# # # #         re.compile(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.+?)</script>', re.S),
# # # #         re.compile(r'data-react-props="([^"]+)"'),
# # # #     ]

# # # #     for script in soup.find_all("script"):
# # # #         text = script.string or ""
# # # #         if len(text) < 50:
# # # #             continue
# # # #         for pat in patterns:
# # # #             match = pat.search(text)
# # # #             if match:
# # # #                 try:
# # # #                     blob = _json.loads(match.group(1))
# # # #                     rows = _flatten_json_to_rows(blob)
# # # #                     if len(rows) >= 3:
# # # #                         df = pd.DataFrame(rows)
# # # #                         results.append(df)
# # # #                         break
# # # #                 except Exception:
# # # #                     pass

# # # #     return results


# # # # def _strat_text_blocks(html: str) -> list:
# # # #     if not BS4_AVAILABLE:
# # # #         return []

# # # #     soup = BeautifulSoup(html, "lxml")

# # # #     for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
# # # #         tag.decompose()

# # # #     review_containers = soup.find_all(
# # # #         attrs={"class": re.compile(r"review|comment|feedback|testimonial|opinion", re.I)}
# # # #     )
# # # #     rows = []
# # # #     for container in review_containers:
# # # #         text = container.get_text(separator=" ", strip=True)
# # # #         if text and 20 < len(text) < 2000:
# # # #             row = {"text": text}
# # # #             parent = container.parent
# # # #             if parent:
# # # #                 for sibling in parent.find_all(True, limit=10):
# # # #                     sc = " ".join(sibling.get("class", [])).lower()
# # # #                     st = sibling.get_text(strip=True)
# # # #                     if not st:
# # # #                         continue
# # # #                     if "author" in sc or "name" in sc:
# # # #                         row["author"] = st
# # # #                     elif "date" in sc or "time" in sc:
# # # #                         row["date"] = st
# # # #                     elif "rating" in sc or "star" in sc:
# # # #                         nums = re.findall(r"\d+\.?\d*", st)
# # # #                         if nums:
# # # #                             row["rating"] = float(nums[0])
# # # #             rows.append(row)

# # # #     if len(rows) >= 3:
# # # #         return [pd.DataFrame(rows)]

# # # #     paragraphs = []
# # # #     for p in soup.find_all("p"):
# # # #         txt = p.get_text(strip=True)
# # # #         if txt and 30 < len(txt) < 1000:
# # # #             paragraphs.append({"paragraph": txt, "word_count": len(txt.split())})
# # # #     if len(paragraphs) >= 5:
# # # #         return [pd.DataFrame(paragraphs)]

# # # #     return []


# # # # def smart_scrape(url: str) -> dict:
# # # #     html, final_url, fetch_err = _fetch_page(url)
# # # #     if not html:
# # # #         return {
# # # #             "df": None, "error": fetch_err or "Could not fetch URL",
# # # #             "strategy": "none", "rows": 0, "cols": 0,
# # # #             "all_candidates": 0, "page_title": "", "is_js_limited": False
# # # #         }

# # # #     if not BS4_AVAILABLE:
# # # #         return {
# # # #             "df": None, "error": "BeautifulSoup/lxml not installed.",
# # # #             "strategy": "none", "rows": 0, "cols": 0,
# # # #             "all_candidates": 0, "page_title": "", "is_js_limited": False
# # # #         }

# # # #     soup_q = BeautifulSoup(html, "lxml")
# # # #     visible_text_len = len(soup_q.get_text(strip=True))
# # # #     script_count = len(soup_q.find_all("script"))
# # # #     is_js_limited = (script_count > 15 and visible_text_len < 2000)

# # # #     title_tag = soup_q.find("title")
# # # #     page_title = title_tag.get_text(strip=True) if title_tag else ""

# # # #     all_dfs = []

# # # #     strat_fns = [
# # # #         ("HTML Tables", lambda: _strat_html_tables(html)),
# # # #         ("JSON-LD Schema", lambda: _strat_jsonld(html)),
# # # #         ("Repeated Cards", lambda: _strat_repeated_elements(html)),
# # # #         ("List Items", lambda: _strat_lists(html)),
# # # #         ("JS Data Blobs", lambda: _strat_js_hints(html, url)),
# # # #         ("Text/Reviews", lambda: _strat_text_blocks(html)),
# # # #         ("Page Metadata", lambda: _strat_meta(html, url)),
# # # #     ]

# # # #     for strat_name, strat_fn in strat_fns:
# # # #         try:
# # # #             dfs = strat_fn()
# # # #         except Exception:
# # # #             import traceback as _tb
# # # #             _tb.print_exc()
# # # #             continue
# # # #         for df in (dfs or []):
# # # #             try:
# # # #                 if df is not None and not df.empty and len(df) >= 2:
# # # #                     score = _score_df(df)
# # # #                     all_dfs.append((score, strat_name, df))
# # # #             except Exception:
# # # #                 continue

# # # #     if not all_dfs:
# # # #         return {
# # # #             "df": None,
# # # #             "error": (
# # # #                 "No extractable data found. This page is likely fully JavaScript-rendered."
# # # #                 if is_js_limited else
# # # #                 "No structured data found on this page."
# # # #             ),
# # # #             "strategy": "none",
# # # #             "rows": 0,
# # # #             "cols": 0,
# # # #             "all_candidates": 0,
# # # #             "page_title": page_title,
# # # #             "is_js_limited": is_js_limited
# # # #         }

# # # #     all_dfs.sort(key=lambda x: -x[0])
# # # #     best_score, best_strat, best_df = all_dfs[0]

# # # #     best_df = best_df.copy()
# # # #     best_df.columns = [str(c).strip().lower().replace(" ", "_") for c in best_df.columns]
# # # #     best_df = best_df.dropna(how="all").reset_index(drop=True)

# # # #     for col in best_df.columns:
# # # #         if best_df[col].dtype == object:
# # # #             converted = pd.to_numeric(
# # # #                 best_df[col].astype(str).str.replace(r"[^\d\.\-]", "", regex=True),
# # # #                 errors="coerce"
# # # #             )
# # # #             if converted.notna().sum() / max(len(best_df), 1) >= 0.75:
# # # #                 best_df[col] = converted

# # # #     return {
# # # #         "df": best_df,
# # # #         "error": None,
# # # #         "strategy": best_strat,
# # # #         "rows": len(best_df),
# # # #         "cols": len(best_df.columns),
# # # #         "all_candidates": len(all_dfs),
# # # #         "page_title": page_title,
# # # #         "is_js_limited": is_js_limited,
# # # #         "all_strategies_found": [
# # # #             {"strategy": s, "rows": len(d), "cols": len(d.columns), "score": round(sc, 1)}
# # # #             for sc, s, d in all_dfs[:5]
# # # #         ]
# # # #     }


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  ROUTE — /scrape_analyze
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # @app.route("/scrape_analyze", methods=["POST", "OPTIONS"])
# # # # def scrape_analyze():
# # # #     if request.method == "OPTIONS":
# # # #         return "", 200

# # # #     if not WEB_SCRAPE_AVAILABLE:
# # # #         return jsonify({
# # # #             "status": "error",
# # # #             "message": "Install required libs: pip install requests lxml beautifulsoup4"
# # # #         }), 500

# # # #     try:
# # # #         url = (request.form.get("url") or "").strip()
# # # #         if not url:
# # # #             return jsonify({"status": "error", "message": "No URL provided."}), 400
# # # #         if not url.startswith(("http://", "https://")):
# # # #             url = "https://" + url

# # # #         result = smart_scrape(url)

# # # #         if result["df"] is None:
# # # #             return jsonify({
# # # #                 "status": "error",
# # # #                 "message": result.get("error", "No data found."),
# # # #                 "is_js_limited": result.get("is_js_limited", False),
# # # #                 "page_title": result.get("page_title", ""),
# # # #             }), 400

# # # #         best_df = result["df"]

# # # #         raw_preview = _df_to_safe_records(best_df.head(10))
# # # #         raw_csv_b64 = _df_to_b64_csv(best_df)

# # # #         try:
# # # #             cleaned_df, _, preprocess_summary, _, _ = basira_auto_preprocessing(
# # # #                 best_df, "scraped_data.csv"
# # # #             )
# # # #         except Exception as _pp_e:
# # # #             print(f"[Basira] Preprocessing skipped: {_pp_e}")
# # # #             cleaned_df = best_df
# # # #             preprocess_summary = {}

# # # #         if len(cleaned_df) < 5:
# # # #             return jsonify({
# # # #                 "status": "error",
# # # #                 "message": f"Extracted only {len(cleaned_df)} rows — not enough for analysis."
# # # #             }), 400

# # # #         payload = run_analysis_pipeline(cleaned_df)
# # # #         payload["dataset_meta"]["source"] = "web_scrape"
# # # #         payload["dataset_meta"]["source_url"] = url
# # # #         payload["dataset_meta"]["page_title"] = result["page_title"]
# # # #         payload["dataset_meta"]["scrape_strategy"] = result["strategy"]
# # # #         payload["dataset_meta"]["all_candidates"] = result["all_candidates"]
# # # #         payload["dataset_meta"]["is_js_limited"] = result["is_js_limited"]
# # # #         payload["dataset_meta"]["strategies_summary"] = result.get("all_strategies_found", [])
# # # #         payload["raw_preview"] = raw_preview
# # # #         payload["raw_csv_b64"] = raw_csv_b64
# # # #         payload["preprocessing_summary"] = preprocess_summary

# # # #         return jsonify(payload)

# # # #     except Exception as exc:
# # # #         import traceback
# # # #         traceback.print_exc()
# # # #         return jsonify({"status": "error", "message": str(exc)}), 500


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  ROUTE — /preprocess
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # @app.route("/preprocess", methods=["POST", "OPTIONS"])
# # # # def preprocess():
# # # #     if request.method == "OPTIONS":
# # # #         return "", 200

# # # #     try:
# # # #         if "file" not in request.files:
# # # #             return jsonify({"status": "error", "message": "No file uploaded"}), 400

# # # #         file = request.files["file"]
# # # #         filename = (file.filename or "dataset").lower()
# # # #         audit = []

# # # #         def log(stage, column, action, before, after, method, notes=""):
# # # #             audit.append({
# # # #                 "stage": stage,
# # # #                 "column": column,
# # # #                 "action": action,
# # # #                 "before": str(before),
# # # #                 "after": str(after),
# # # #                 "method": method,
# # # #                 "notes": notes,
# # # #             })

# # # #         try:
# # # #             df = read_uploaded_dataframe(file)
# # # #         except Exception as e:
# # # #             return jsonify({"status": "error", "message": f"Could not read file: {e}"}), 400

# # # #         if df.empty:
# # # #             return jsonify({"status": "error", "message": "File is empty."}), 400

# # # #         rows_before = len(df)
# # # #         cols_before = len(df.columns)
# # # #         log("Ingestion", "*", "File loaded", f"{rows_before} rows", f"{cols_before} cols", "pandas read_csv/read_excel")

# # # #         original_cols = list(df.columns)
# # # #         df.columns = [re.sub(r"\s+", "_", str(c).strip().lower()) for c in df.columns]
# # # #         renamed = [(o, n) for o, n in zip(original_cols, df.columns) if o != n]
# # # #         if renamed:
# # # #             log(
# # # #                 "Column Cleaning", "*", "Renamed columns",
# # # #                 str(len(renamed)), str(len(renamed)),
# # # #                 "strip + lowercase + underscore",
# # # #                 "; ".join(f"'{o}'→'{n}'" for o, n in renamed[:5])
# # # #             )

# # # #         inf_count = int(np.isinf(df.select_dtypes(include=[np.number])).sum().sum())
# # # #         df = df.replace([np.inf, -np.inf], np.nan)
# # # #         if inf_count:
# # # #             log("Cleaning", "*", "Replaced Inf values", inf_count, "NaN", "replace([inf,-inf], NaN)")

# # # #         coerced = []
# # # #         for col in df.select_dtypes(include=[object]).columns:
# # # #             converted = pd.to_numeric(df[col], errors="coerce")
# # # #             ratio = converted.notna().sum() / max(len(df), 1)
# # # #             if ratio >= 0.85:
# # # #                 df[col] = converted
# # # #                 coerced.append(col)
# # # #         if coerced:
# # # #             log("Type Coercion", str(coerced), "String → Numeric", "object", "float64", "pd.to_numeric ≥85% parseable", f"{len(coerced)} column(s) converted")

# # # #         missing_before = int(df.isnull().sum().sum())
# # # #         dup_before = int(df.duplicated().sum())

# # # #         empty_cols = [c for c in df.columns if df[c].isna().all()]
# # # #         if empty_cols:
# # # #             df = df.drop(columns=empty_cols)
# # # #             log("Column Removal", str(empty_cols), "Dropped empty columns", len(empty_cols), 0, "isna().all()", "Columns with 100% missing values removed")

# # # #         missing_ratios = df.isnull().mean()
# # # #         high_miss_cols = missing_ratios[missing_ratios >= 0.60].index.tolist()
# # # #         if high_miss_cols:
# # # #             df = df.drop(columns=high_miss_cols)
# # # #             log("Column Removal", str(high_miss_cols), "Dropped high-missing columns", "≥60% missing", "removed", "threshold=0.60", f"{len(high_miss_cols)} column(s) exceeded 60% missing rate")

# # # #         if dup_before > 0:
# # # #             df = df.drop_duplicates().reset_index(drop=True)
# # # #             log("Duplicate Removal", "*", "Removed duplicate rows", dup_before, 0, "drop_duplicates()")

# # # #         num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
# # # #         for col in num_cols:
# # # #             n_miss = int(df[col].isna().sum())
# # # #             if n_miss > 0:
# # # #                 median_val = df[col].median()
# # # #                 df[col] = df[col].fillna(median_val)
# # # #                 log("Imputation", col, "Filled missing numeric", n_miss, round(float(median_val), 4), "median", f"{n_miss} missing values → median={round(float(median_val),4)}")

# # # #         cat_cols = df.select_dtypes(include=[object]).columns.tolist()
# # # #         for col in cat_cols:
# # # #             n_miss = int(df[col].isna().sum())
# # # #             if n_miss > 0:
# # # #                 mode_val = df[col].mode()
# # # #                 fill_val = mode_val.iloc[0] if len(mode_val) > 0 else "unknown"
# # # #                 df[col] = df[col].fillna(fill_val)
# # # #                 log("Imputation", col, "Filled missing categorical", n_miss, fill_val, "most_frequent", f"{n_miss} missing → mode='{fill_val}'")

# # # #         outlier_summary = {}
# # # #         for col in num_cols:
# # # #             if col not in df.columns:
# # # #                 continue
# # # #             q1 = df[col].quantile(0.25)
# # # #             q3 = df[col].quantile(0.75)
# # # #             iqr = q3 - q1
# # # #             if iqr == 0:
# # # #                 continue
# # # #             lo = q1 - 1.5 * iqr
# # # #             hi = q3 + 1.5 * iqr
# # # #             n_out = int(((df[col] < lo) | (df[col] > hi)).sum())
# # # #             if n_out > 0:
# # # #                 pct = n_out / len(df)
# # # #                 if pct <= 0.05:
# # # #                     df[col] = df[col].clip(lo, hi)
# # # #                     action = "Winsorized (capped)"
# # # #                 else:
# # # #                     action = "Flagged only (>5% outliers)"
# # # #                 outlier_summary[col] = {"count": n_out, "pct": round(pct * 100, 1), "action": action}
# # # #                 log("Outlier", col, action, n_out, f"[{round(float(lo),3)}, {round(float(hi),3)}]", "IQR 1.5×", f"{n_out} outliers ({round(pct*100,1)}%)")

# # # #         _RE_D = re.compile(r"[\u064B-\u065F\u0610-\u061A\u06D6-\u06DC\u06DF-\u06E4\u06E7-\u06ED]")
# # # #         _RE_AL = re.compile(r"[إأآا]")
# # # #         _RE_TA = re.compile(r"ة")
# # # #         _RE_TW = re.compile(r"\u0640")
# # # #         _RE_WS2 = re.compile(r"\s+")
# # # #         _RE_AR = re.compile(r"[\u0600-\u06FF]")

# # # #         def _norm_cell(v):
# # # #             if not isinstance(v, str) or not v.strip():
# # # #                 return v
# # # #             ar_ratio = len(_RE_AR.findall(v)) / max(len(v), 1)
# # # #             if ar_ratio > 0.3:
# # # #                 v = _RE_D.sub("", v)
# # # #                 v = _RE_AL.sub("ا", v)
# # # #                 v = _RE_TA.sub("ه", v)
# # # #                 v = _RE_TW.sub("", v)
# # # #             else:
# # # #                 v = v.lower()
# # # #             return _RE_WS2.sub(" ", v).strip()

# # # #         for col in cat_cols:
# # # #             if col not in df.columns:
# # # #                 continue
# # # #             before_sample = str(df[col].iloc[0]) if len(df) > 0 else ""
# # # #             df[col] = df[col].apply(_norm_cell)
# # # #             after_sample = str(df[col].iloc[0]) if len(df) > 0 else ""
# # # #             if before_sample != after_sample:
# # # #                 log("Normalization", col, "Bilingual text normalized", before_sample[:40], after_sample[:40], "Arabic diacritics + alef / English lowercase")

# # # #         rows_after = len(df)
# # # #         missing_after = int(df.isnull().sum().sum())

# # # #         col_type_map = {
# # # #             "numeric": [c for c in df.columns if df[c].dtype != object],
# # # #             "categorical": [c for c in df.columns if df[c].dtype == object],
# # # #             "text": [],
# # # #             "datetime": []
# # # #         }

# # # #         cleaned_b64 = _df_to_b64_csv(df)
# # # #         audit_df = pd.DataFrame(audit)
# # # #         audit_b64 = _df_to_b64_csv(audit_df) if not audit_df.empty else ""

# # # #         preview = [
# # # #             {col: _safe_json_value(row[col]) for col in df.columns}
# # # #             for _, row in df.head(15).iterrows()
# # # #         ]

# # # #         run_id = f"basira_{int(_time.time())}"

# # # #         summary = {
# # # #             "run_id": run_id,
# # # #             "rows_before": rows_before,
# # # #             "cols_before": cols_before,
# # # #             "rows_after": rows_after,
# # # #             "cols_after": len(df.columns),
# # # #             "missing_before": missing_before,
# # # #             "missing_after": missing_after,
# # # #             "missing_total_before": missing_before,
# # # #             "missing_total_after": missing_after,
# # # #             "duplicates_removed": dup_before,
# # # #             "exact_dup_before": dup_before,
# # # #             "exact_dup_after": 0,
# # # #             "empty_cols_removed": len(empty_cols),
# # # #             "high_miss_cols_removed": len(high_miss_cols),
# # # #             "numeric_cols": len(col_type_map["numeric"]),
# # # #             "categorical_cols": len(col_type_map["categorical"]),
# # # #             "outlier_cols": len(outlier_summary),
# # # #             "text_normalized_cols": len([c for c in cat_cols if c in df.columns]),
# # # #             "coerced_cols": len(coerced),
# # # #             "audit_steps": len(audit),
# # # #             "validation_pass_initial": missing_before == 0,
# # # #             "validation_pass_final": missing_after == 0,
# # # #             "numeric_strategy": "SIMPLE",
# # # #             "features_generated": False,
# # # #             "id_column": None,
# # # #             "model_input_cols": len(col_type_map["numeric"]),
# # # #         }

# # # #         return jsonify({
# # # #             "status": "success",
# # # #             "run_id": run_id,
# # # #             "summary": summary,
# # # #             "col_type_map": col_type_map,
# # # #             "cleaned_preview": preview,
# # # #             "model_preview": preview,
# # # #             "audit_preview": audit,
# # # #             "cleaned_csv_b64": cleaned_b64,
# # # #             "audit_csv_b64": audit_b64,
# # # #             "feat_csv_b64": None,
# # # #             "model_csv_b64": cleaned_b64,
# # # #             "columns": list(df.columns),
# # # #         })

# # # #     except Exception as exc:
# # # #         import traceback
# # # #         traceback.print_exc()
# # # #         return jsonify({"status": "error", "message": str(exc)}), 500


# # # # # ══════════════════════════════════════════════════════════════════════════════
# # # # #  ENTRY POINT
# # # # # ══════════════════════════════════════════════════════════════════════════════

# # # # if __name__ == "__main__":
# # # #     _REQUIRED = [
# # # #         "flask", "flask_cors", "pandas", "numpy", "shap",
# # # #         "scikit-learn", "scipy", "requests", "lxml",
# # # #         "beautifulsoup4", "openpyxl",
# # # #     ]
# # # #     _IMPORT_MAP = {"scikit-learn": "sklearn", "beautifulsoup4": "bs4"}

# # # #     _missing = []
# # # #     for pkg in _REQUIRED:
# # # #         try:
# # # #             __import__(_IMPORT_MAP.get(pkg, pkg.replace("-", "_")))
# # # #         except ImportError:
# # # #             _missing.append(pkg)

# # # #     if _missing:
# # # #         print(f"[Basira] Auto-installing: {', '.join(_missing)}")
# # # #         _sub.check_call([_sys.executable, "-m", "pip", "install", "--break-system-packages", "-q"] + _missing)
# # # #         print("[Basira] Done. Starting server...")

# # # #     app.run(debug=False, port=5001, host="127.0.0.1")

# # # import json
# # # from pathlib import Path
# # # from datetime import datetime, timedelta

# # # from flask import Flask, jsonify, request, render_template, session

# # # # =========================================================
# # # # Paths
# # # # =========================================================

# # # BASE_DIR = Path(__file__).resolve().parent
# # # TEMPLATES_DIR = BASE_DIR / "templates"
# # # STATIC_DIR = BASE_DIR / "static"

# # # DEFAULT_HOST = "127.0.0.1"
# # # DEFAULT_PORT = 5000
# # # SESSION_TIMEOUT_MINUTES = 20

# # # app = Flask(
# # #     __name__,
# # #     template_folder=str(TEMPLATES_DIR),
# # #     static_folder=str(STATIC_DIR) if STATIC_DIR.exists() else None
# # # )
# # # app.secret_key = "basira-local-secret-key-change-this"


# # # # =========================================================
# # # # Helpers
# # # # =========================================================

# # # def now_iso():
# # #     return datetime.utcnow().isoformat() + "Z"


# # # def get_data_dir():
# # #     return Path.home() / "Documents" / "BasiraData"


# # # def ensure_data_dir():
# # #     path = get_data_dir()
# # #     path.mkdir(parents=True, exist_ok=True)
# # #     return path


# # # def session_expired():
# # #     expires_at = session.get("expires_at")
# # #     if not expires_at:
# # #         return True

# # #     try:
# # #         expires_dt = datetime.fromisoformat(expires_at)
# # #     except Exception:
# # #         return True

# # #     return datetime.utcnow() > expires_dt


# # # def refresh_session_timeout():
# # #     session["expires_at"] = (
# # #         datetime.utcnow() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
# # #     ).isoformat()


# # # def is_logged_in():
# # #     if not session.get("logged_in"):
# # #         return False
# # #     if session_expired():
# # #         return False
# # #     return True


# # # def build_status_payload():
# # #     return {
# # #         "status": "ok",
# # #         "app": "Basira Local",
# # #         "version": "1.0.0",
# # #         "mode": "local",
# # #         "server_time": now_iso(),
# # #         "data_dir": str(get_data_dir()),
# # #         "logged_in": is_logged_in(),
# # #         "subscription_status": session.get("subscription_status", "inactive"),
# # #         "user_id": session.get("user_id", ""),
# # #         "template_found": (TEMPLATES_DIR / "basira_app.html").exists(),
# # #         "template_dir": str(TEMPLATES_DIR),
# # #         "static_dir": str(STATIC_DIR),
# # #     }


# # # def load_local_config():
# # #     config_path = ensure_data_dir() / "local_config.json"

# # #     if not config_path.exists():
# # #         default_config = {
# # #             "app_name": "Basira Local",
# # #             "theme": "light",
# # #             "language": "ar",
# # #             "created_at": now_iso(),
# # #         }
# # #         config_path.write_text(
# # #             json.dumps(default_config, ensure_ascii=False, indent=2),
# # #             encoding="utf-8"
# # #         )

# # #     try:
# # #         return json.loads(config_path.read_text(encoding="utf-8"))
# # #     except Exception:
# # #         return {
# # #             "app_name": "Basira Local",
# # #             "theme": "light",
# # #             "language": "ar"
# # #         }


# # # def save_local_config(config_data):
# # #     config_path = ensure_data_dir() / "local_config.json"
# # #     config_path.write_text(
# # #         json.dumps(config_data, ensure_ascii=False, indent=2),
# # #         encoding="utf-8"
# # #     )


# # # # =========================================================
# # # # Session Middleware
# # # # =========================================================

# # # @app.before_request
# # # def before_request():
# # #     public_paths = {
# # #         "/",
# # #         "/health",
# # #         "/api/app/status",
# # #         "/api/auth/ping",
# # #         "/favicon.ico"
# # #     }

# # #     if request.path in public_paths:
# # #         return

# # #     if request.path.endswith((".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".webp")):
# # #         return

# # #     if is_logged_in():
# # #         refresh_session_timeout()
# # #         return

# # #     if request.path.startswith("/api/"):
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Session expired or not authenticated.",
# # #             "code": "AUTH_REQUIRED"
# # #         }), 401


# # # # =========================================================
# # # # Frontend Routes
# # # # =========================================================

# # # @app.route("/")
# # # def home():
# # #     template_path = TEMPLATES_DIR / "basira_app.html"

# # #     if not template_path.exists():
# # #         return f"""
# # #         <html lang="ar" dir="rtl">
# # #         <head><meta charset="UTF-8"><title>Basira Local</title></head>
# # #         <body style="font-family: Arial; padding: 40px;">
# # #             <h1>Basira Local</h1>
# # #             <p>تعذر العثور على ملف basira_app.html</p>
# # #             <p>Expected path: {template_path}</p>
# # #         </body>
# # #         </html>
# # #         """

# # #     return render_template("basira_app.html")


# # # @app.route("/health")
# # # def health():
# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Basira local app is running.",
# # #         "server_time": now_iso()
# # #     })


# # # @app.route("/favicon.ico")
# # # def favicon():
# # #     return "", 204


# # # # =========================================================
# # # # App Status APIs
# # # # =========================================================

# # # @app.route("/api/app/status", methods=["GET"])
# # # def api_app_status():
# # #     return jsonify(build_status_payload())


# # # @app.route("/api/app/config", methods=["GET"])
# # # def api_get_app_config():
# # #     return jsonify({
# # #         "status": "ok",
# # #         "config": load_local_config()
# # #     })


# # # @app.route("/api/app/config", methods=["POST"])
# # # def api_save_app_config():
# # #     try:
# # #         payload = request.get_json(force=True) or {}
# # #         config = load_local_config()

# # #         config["app_name"] = payload.get("app_name", config.get("app_name", "Basira Local"))
# # #         config["theme"] = payload.get("theme", config.get("theme", "light"))
# # #         config["language"] = payload.get("language", config.get("language", "ar"))
# # #         config["updated_at"] = now_iso()

# # #         save_local_config(config)

# # #         return jsonify({
# # #             "status": "ok",
# # #             "message": "Config updated successfully.",
# # #             "config": config
# # #         })
# # #     except Exception as e:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": f"Failed to save config: {str(e)}"
# # #         }), 500


# # # # =========================================================
# # # # Auth APIs
# # # # =========================================================

# # # @app.route("/api/auth/ping", methods=["GET"])
# # # def auth_ping():
# # #     return jsonify({
# # #         "status": "ok",
# # #         "authenticated": is_logged_in(),
# # #         "server_time": now_iso()
# # #     })


# # # @app.route("/api/auth/session", methods=["GET"])
# # # def auth_session():
# # #     if not is_logged_in():
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "No active session."
# # #         }), 401

# # #     return jsonify({
# # #         "status": "ok",
# # #         "session": {
# # #             "user_id": session.get("user_id", ""),
# # #             "subscription_status": session.get("subscription_status", "inactive"),
# # #             "expires_at": session.get("expires_at", ""),
# # #             "logged_in": True
# # #         }
# # #     })


# # # @app.route("/api/auth/session", methods=["POST"])
# # # def auth_set_session():
# # #     try:
# # #         payload = request.get_json(force=True) or {}

# # #         session["logged_in"] = True
# # #         session["user_id"] = payload.get("user_id", "")
# # #         session["access_token"] = payload.get("access_token", "")
# # #         session["refresh_token"] = payload.get("refresh_token", "")
# # #         session["subscription_status"] = payload.get("subscription_status", "active")
# # #         refresh_session_timeout()

# # #         return jsonify({
# # #             "status": "ok",
# # #             "message": "Session linked successfully.",
# # #             "expires_at": session.get("expires_at")
# # #         })
# # #     except Exception as e:
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": f"Failed to set session: {str(e)}"
# # #         }), 500


# # # @app.route("/api/auth/heartbeat", methods=["POST"])
# # # def auth_heartbeat():
# # #     if not is_logged_in():
# # #         return jsonify({
# # #             "status": "error",
# # #             "message": "Session expired."
# # #         }), 401

# # #     refresh_session_timeout()
# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Heartbeat accepted.",
# # #         "expires_at": session.get("expires_at")
# # #     })


# # # @app.route("/api/auth/auto-logout", methods=["POST"])
# # # def auth_auto_logout():
# # #     session.clear()
# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Logged out automatically."
# # #     })


# # # @app.route("/api/auth/logout", methods=["POST"])
# # # def auth_logout():
# # #     session.clear()
# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Logged out successfully."
# # #     })


# # # # =========================================================
# # # # Subscription APIs
# # # # =========================================================

# # # @app.route("/api/subscription/status", methods=["GET"])
# # # def subscription_status():
# # #     return jsonify({
# # #         "status": "ok",
# # #         "subscription_status": session.get("subscription_status", "inactive")
# # #     })


# # # @app.route("/api/subscription/renew-demo", methods=["POST"])
# # # def subscription_renew_demo():
# # #     session["subscription_status"] = "active"
# # #     if session.get("logged_in"):
# # #         refresh_session_timeout()

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Demo subscription renewed successfully.",
# # #         "subscription_status": "active"
# # #     })


# # # # =========================================================
# # # # Placeholder APIs
# # # # =========================================================

# # # @app.route("/api/files/list", methods=["GET"])
# # # def files_list():
# # #     data_dir = ensure_data_dir()
# # #     files = []

# # #     for item in data_dir.iterdir():
# # #         if item.is_file():
# # #             files.append({
# # #                 "name": item.name,
# # #                 "size": item.stat().st_size,
# # #                 "modified_at": datetime.utcfromtimestamp(item.stat().st_mtime).isoformat() + "Z"
# # #             })

# # #     return jsonify({
# # #         "status": "ok",
# # #         "files": files
# # #     })


# # # @app.route("/api/process/test", methods=["POST"])
# # # def process_test():
# # #     payload = request.get_json(force=True) or {}

# # #     return jsonify({
# # #         "status": "ok",
# # #         "message": "Local processing placeholder completed.",
# # #         "received": payload,
# # #         "processed_at": now_iso()
# # #     })


# # # @app.route("/api/ai/analyze", methods=["POST"])
# # # def ai_analyze():
# # #     payload = request.get_json(force=True) or {}
# # #     text = payload.get("text", "")

# # #     result = {
# # #         "summary": f"تم استلام النص محليًا بطول {len(text)} حرفًا.",
# # #         "keywords": [],
# # #         "confidence": 0.95,
# # #         "mode": "placeholder"
# # #     }

# # #     return jsonify({
# # #         "status": "ok",
# # #         "result": result
# # #     })


# # # # =========================================================
# # # # Main
# # # # =========================================================

# # # if __name__ == "__main__":
# # #     ensure_data_dir()
# # #     print("=" * 60)
# # #     print("Basira Local is running")
# # #     print(f"URL: http://{DEFAULT_HOST}:{DEFAULT_PORT}")
# # #     print(f"TEMPLATES_DIR: {TEMPLATES_DIR}")
# # #     print(f"STATIC_DIR: {STATIC_DIR}")
# # #     print("=" * 60)

# # #     app.run(host=DEFAULT_HOST, port=DEFAULT_PORT, debug=False, threaded=True)
# # import json
# # from pathlib import Path
# # from datetime import datetime, timedelta

# # from flask import Flask, jsonify, request, render_template, session

# # # =========================================================
# # # Paths
# # # =========================================================

# # BASE_DIR = Path(__file__).resolve().parent
# # TEMPLATES_DIR = BASE_DIR / "templates"
# # STATIC_DIR = BASE_DIR / "static"

# # DEFAULT_HOST = "127.0.0.1"
# # DEFAULT_PORT = 5000
# # SESSION_TIMEOUT_MINUTES = 20

# # app = Flask(
# #     __name__,
# #     template_folder=str(TEMPLATES_DIR),
# #     static_folder=str(STATIC_DIR) if STATIC_DIR.exists() else None
# # )
# # app.secret_key = "basira-local-secret-key-change-this"


# # # =========================================================
# # # Helpers
# # # =========================================================

# # def now_iso():
# #     return datetime.utcnow().isoformat() + "Z"


# # def get_data_dir():
# #     return Path.home() / "Documents" / "BasiraData"


# # def ensure_data_dir():
# #     path = get_data_dir()
# #     path.mkdir(parents=True, exist_ok=True)
# #     return path


# # def session_expired():
# #     expires_at = session.get("expires_at")
# #     if not expires_at:
# #         return True

# #     try:
# #         expires_dt = datetime.fromisoformat(expires_at)
# #     except Exception:
# #         return True

# #     return datetime.utcnow() > expires_dt


# # def refresh_session_timeout():
# #     session["expires_at"] = (
# #         datetime.utcnow() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
# #     ).isoformat()


# # def is_logged_in():
# #     if not session.get("logged_in"):
# #         return False
# #     if session_expired():
# #         return False
# #     return True


# # def build_status_payload():
# #     return {
# #         "status": "ok",
# #         "app": "Basira Local",
# #         "version": "1.0.0",
# #         "mode": "local",
# #         "server_time": now_iso(),
# #         "data_dir": str(get_data_dir()),
# #         "logged_in": is_logged_in(),
# #         "subscription_status": session.get("subscription_status", "inactive"),
# #         "user_id": session.get("user_id", ""),
# #         "template_found": (TEMPLATES_DIR / "basira_app.html").exists(),
# #         "template_dir": str(TEMPLATES_DIR),
# #         "static_dir": str(STATIC_DIR),
# #     }


# # def load_local_config():
# #     config_path = ensure_data_dir() / "local_config.json"

# #     if not config_path.exists():
# #         default_config = {
# #             "app_name": "Basira Local",
# #             "theme": "light",
# #             "language": "ar",
# #             "created_at": now_iso(),
# #         }
# #         config_path.write_text(
# #             json.dumps(default_config, ensure_ascii=False, indent=2),
# #             encoding="utf-8"
# #         )

# #     try:
# #         return json.loads(config_path.read_text(encoding="utf-8"))
# #     except Exception:
# #         return {
# #             "app_name": "Basira Local",
# #             "theme": "light",
# #             "language": "ar"
# #         }


# # def save_local_config(config_data):
# #     config_path = ensure_data_dir() / "local_config.json"
# #     config_path.write_text(
# #         json.dumps(config_data, ensure_ascii=False, indent=2),
# #         encoding="utf-8"
# #     )


# # # =========================================================
# # # Session Middleware
# # # =========================================================

# # @app.before_request
# # def before_request():
# #     public_paths = {
# #         "/",
# #         "/health",
# #         "/api/app/status",
# #         "/api/auth/ping",
# #         "/favicon.ico"
# #     }

# #     if request.path in public_paths:
# #         return

# #     if request.path.endswith((".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".webp")):
# #         return

# #     if is_logged_in():
# #         refresh_session_timeout()
# #         return

# #     if request.path.startswith("/api/"):
# #         return jsonify({
# #             "status": "error",
# #             "message": "Session expired or not authenticated.",
# #             "code": "AUTH_REQUIRED"
# #         }), 401


# # # =========================================================
# # # Frontend Routes
# # # =========================================================

# # @app.route("/")
# # def home():
# #     template_path = TEMPLATES_DIR / "basira_app.html"

# #     if not template_path.exists():
# #         return f"""
# #         <html lang="ar" dir="rtl">
# #         <head><meta charset="UTF-8"><title>Basira Local</title></head>
# #         <body style="font-family: Arial; padding: 40px;">
# #             <h1>Basira Local</h1>
# #             <p>تعذر العثور على ملف basira_app.html</p>
# #             <p>Expected path: {template_path}</p>
# #         </body>
# #         </html>
# #         """

# #     return render_template("basira_app.html")


# # @app.route("/health")
# # def health():
# #     return jsonify({
# #         "status": "ok",
# #         "message": "Basira local app is running.",
# #         "server_time": now_iso()
# #     })


# # @app.route("/favicon.ico")
# # def favicon():
# #     return "", 204


# # # =========================================================
# # # App Status APIs
# # # =========================================================

# # @app.route("/api/app/status", methods=["GET"])
# # def api_app_status():
# #     return jsonify(build_status_payload())


# # @app.route("/api/app/config", methods=["GET"])
# # def api_get_app_config():
# #     return jsonify({
# #         "status": "ok",
# #         "config": load_local_config()
# #     })


# # @app.route("/api/app/config", methods=["POST"])
# # def api_save_app_config():
# #     try:
# #         payload = request.get_json(force=True) or {}
# #         config = load_local_config()

# #         config["app_name"] = payload.get("app_name", config.get("app_name", "Basira Local"))
# #         config["theme"] = payload.get("theme", config.get("theme", "light"))
# #         config["language"] = payload.get("language", config.get("language", "ar"))
# #         config["updated_at"] = now_iso()

# #         save_local_config(config)

# #         return jsonify({
# #             "status": "ok",
# #             "message": "Config updated successfully.",
# #             "config": config
# #         })
# #     except Exception as e:
# #         return jsonify({
# #             "status": "error",
# #             "message": f"Failed to save config: {str(e)}"
# #         }), 500


# # # =========================================================
# # # Auth APIs
# # # =========================================================

# # @app.route("/api/auth/ping", methods=["GET"])
# # def auth_ping():
# #     return jsonify({
# #         "status": "ok",
# #         "authenticated": is_logged_in(),
# #         "server_time": now_iso()
# #     })


# # @app.route("/api/auth/session", methods=["GET"])
# # def auth_session():
# #     if not is_logged_in():
# #         return jsonify({
# #             "status": "error",
# #             "message": "No active session."
# #         }), 401

# #     return jsonify({
# #         "status": "ok",
# #         "session": {
# #             "user_id": session.get("user_id", ""),
# #             "subscription_status": session.get("subscription_status", "inactive"),
# #             "expires_at": session.get("expires_at", ""),
# #             "logged_in": True
# #         }
# #     })


# # @app.route("/api/auth/session", methods=["POST"])
# # def auth_set_session():
# #     try:
# #         payload = request.get_json(force=True) or {}

# #         session["logged_in"] = True
# #         session["user_id"] = payload.get("user_id", "")
# #         session["access_token"] = payload.get("access_token", "")
# #         session["refresh_token"] = payload.get("refresh_token", "")
# #         session["subscription_status"] = payload.get("subscription_status", "active")
# #         refresh_session_timeout()

# #         return jsonify({
# #             "status": "ok",
# #             "message": "Session linked successfully.",
# #             "expires_at": session.get("expires_at")
# #         })
# #     except Exception as e:
# #         return jsonify({
# #             "status": "error",
# #             "message": f"Failed to set session: {str(e)}"
# #         }), 500


# # @app.route("/api/auth/heartbeat", methods=["POST"])
# # def auth_heartbeat():
# #     if not is_logged_in():
# #         return jsonify({
# #             "status": "error",
# #             "message": "Session expired."
# #         }), 401

# #     refresh_session_timeout()
# #     return jsonify({
# #         "status": "ok",
# #         "message": "Heartbeat accepted.",
# #         "expires_at": session.get("expires_at")
# #     })


# # @app.route("/api/auth/auto-logout", methods=["POST"])
# # def auth_auto_logout():
# #     session.clear()
# #     return jsonify({
# #         "status": "ok",
# #         "message": "Logged out automatically."
# #     })


# # @app.route("/api/auth/logout", methods=["POST"])
# # def auth_logout():
# #     session.clear()
# #     return jsonify({
# #         "status": "ok",
# #         "message": "Logged out successfully."
# #     })


# # # =========================================================
# # # Subscription APIs
# # # =========================================================

# # @app.route("/api/subscription/status", methods=["GET"])
# # def subscription_status():
# #     return jsonify({
# #         "status": "ok",
# #         "subscription_status": session.get("subscription_status", "inactive")
# #     })


# # @app.route("/api/subscription/renew-demo", methods=["POST"])
# # def subscription_renew_demo():
# #     session["subscription_status"] = "active"
# #     if session.get("logged_in"):
# #         refresh_session_timeout()

# #     return jsonify({
# #         "status": "ok",
# #         "message": "Demo subscription renewed successfully.",
# #         "subscription_status": "active"
# #     })


# # # =========================================================
# # # Placeholder APIs
# # # =========================================================

# # @app.route("/api/files/list", methods=["GET"])
# # def files_list():
# #     data_dir = ensure_data_dir()
# #     files = []

# #     for item in data_dir.iterdir():
# #         if item.is_file():
# #             files.append({
# #                 "name": item.name,
# #                 "size": item.stat().st_size,
# #                 "modified_at": datetime.utcfromtimestamp(item.stat().st_mtime).isoformat() + "Z"
# #             })

# #     return jsonify({
# #         "status": "ok",
# #         "files": files
# #     })


# # @app.route("/api/process/test", methods=["POST"])
# # def process_test():
# #     payload = request.get_json(force=True) or {}

# #     return jsonify({
# #         "status": "ok",
# #         "message": "Local processing placeholder completed.",
# #         "received": payload,
# #         "processed_at": now_iso()
# #     })


# # @app.route("/api/ai/analyze", methods=["POST"])
# # def ai_analyze():
# #     payload = request.get_json(force=True) or {}
# #     text = payload.get("text", "")

# #     result = {
# #         "summary": f"تم استلام النص محليًا بطول {len(text)} حرفًا.",
# #         "keywords": [],
# #         "confidence": 0.95,
# #         "mode": "placeholder"
# #     }

# #     return jsonify({
# #         "status": "ok",
# #         "result": result
# #     })


# # # =========================================================
# # # Main
# # # =========================================================

# # if __name__ == "__main__":
# #     ensure_data_dir()
# #     print("=" * 60)
# #     print("Basira Local is running")
# #     print(f"URL: http://{DEFAULT_HOST}:{DEFAULT_PORT}")
# #     print(f"TEMPLATES_DIR: {TEMPLATES_DIR}")
# #     print(f"STATIC_DIR: {STATIC_DIR}")
# #     print("=" * 60)

# #     app.run(host=DEFAULT_HOST, port=DEFAULT_PORT, debug=False, threaded=True)

# from pathlib import Path
# from datetime import timedelta
# from io import BytesIO
# import math

# import numpy as np
# import pandas as pd
# from flask import Flask, jsonify, request, render_template, session
# from flask_cors import CORS

# # =========================================================
# # PATHS / APP CONFIG
# # =========================================================

# BASE_DIR = Path(__file__).resolve().parent
# TEMPLATES_DIR = BASE_DIR
# STATIC_DIR = BASE_DIR / "static"

# DEFAULT_HOST = "127.0.0.1"
# DEFAULT_PORT = 5000
# SESSION_TIMEOUT_MINUTES = 20

# app = Flask(
#     __name__,
#     template_folder=str(TEMPLATES_DIR),
#     static_folder=str(STATIC_DIR) if STATIC_DIR.exists() else None
# )

# app.secret_key = "basira-local-secret-key-change-this"
# app.config["SESSION_COOKIE_NAME"] = "basira_local_session"
# app.config["SESSION_COOKIE_HTTPONLY"] = True
# app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=SESSION_TIMEOUT_MINUTES)

# CORS(app, supports_credentials=True)


# # =========================================================
# # SESSION HELPERS
# # =========================================================

# def now_iso() -> str:
#     return pd.Timestamp.utcnow().isoformat()


# def is_logged_in() -> bool:
#     return bool(session.get("logged_in", False))


# def refresh_session_timeout() -> None:
#     session.permanent = True
#     session["last_seen"] = now_iso()


# def build_front_session_payload() -> dict:
#     return {
#         "authenticated": is_logged_in(),
#         "user_id": session.get("user_id", ""),
#         "subscription_status": session.get("subscription_status", "active"),
#         "expires_at": session.get("expires_at", ""),
#         "logged_in": is_logged_in(),
#     }


# @app.before_request
# def before_request():
#     public_paths = {
#         "/",
#         "/health",
#         "/favicon.ico",
#         "/api/app/status",
#         "/api/auth/ping",
#         "/api/session/bootstrap",
#         "/api/session/status",
#     }

#     if request.path in public_paths:
#         return

#     if request.path.endswith((".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".webp")):
#         return

#     if is_logged_in():
#         refresh_session_timeout()
#         return

#     if request.path.startswith("/api/"):
#         return jsonify({
#             "status": "error",
#             "message": "Session expired or not authenticated.",
#             "code": "AUTH_REQUIRED"
#         }), 401


# # =========================================================
# # GENERAL HELPERS
# # =========================================================

# def sanitize_value(value):
#     if value is None:
#         return "—"

#     if isinstance(value, (np.integer,)):
#         return int(value)

#     if isinstance(value, (np.floating, float)):
#         if math.isnan(float(value)) or math.isinf(float(value)):
#             return "—"
#         return round(float(value), 4)

#     if pd.isna(value):
#         return "—"

#     return value


# def sanitize_records(df: pd.DataFrame, limit: int = 10):
#     records = []
#     for _, row in df.head(limit).iterrows():
#         rec = {}
#         for col in df.columns:
#             rec[col] = sanitize_value(row[col])
#         records.append(rec)
#     return records


# def try_read_uploaded_dataframe(file_storage) -> pd.DataFrame:
#     filename = (file_storage.filename or "").lower()
#     raw = file_storage.read()

#     if not raw:
#         raise ValueError("Uploaded file is empty.")

#     if filename.endswith((".xlsx", ".xls")):
#         return pd.read_excel(BytesIO(raw))

#     csv_errors = []
#     for sep in [",", ";", "\t", "|"]:
#         try:
#             df = pd.read_csv(BytesIO(raw), sep=sep, engine="python")
#             if df.shape[1] >= 1:
#                 return df
#         except Exception as exc:
#             csv_errors.append(str(exc))

#     try:
#         return pd.read_csv(BytesIO(raw))
#     except Exception as exc:
#         csv_errors.append(str(exc))

#     raise ValueError("Could not read file as CSV or Excel.")


# def numeric_analysis(df: pd.DataFrame) -> dict:
#     df_clean = df.copy()
#     df_clean = df_clean.replace([np.inf, -np.inf], np.nan)

#     for col in df_clean.select_dtypes(include=["object"]).columns:
#         converted = pd.to_numeric(df_clean[col], errors="coerce")
#         ratio = converted.notna().sum() / max(len(df_clean), 1)
#         if ratio >= 0.85:
#             df_clean[col] = converted

#     missing_total = int(df_clean.isna().sum().sum())
#     duplicate_rows = int(df_clean.duplicated().sum())

#     numeric_df = df_clean.select_dtypes(include=[np.number]).copy()

#     constant_cols = [c for c in numeric_df.columns if numeric_df[c].nunique(dropna=True) <= 1]
#     if constant_cols:
#         numeric_df = numeric_df.drop(columns=constant_cols)

#     if len(df_clean) < 2:
#         raise ValueError("Dataset must contain at least 2 rows.")

#     if numeric_df.shape[1] < 2:
#         raise ValueError("Dataset must contain at least 2 numeric columns for analysis.")

#     target_column = numeric_df.columns[-1]
#     feature_columns = [c for c in numeric_df.columns if c != target_column]

#     if not feature_columns:
#         raise ValueError("No usable feature columns found.")

#     correlations = numeric_df.corr(numeric_only=True)[target_column].drop(labels=[target_column], errors="ignore")
#     correlations = correlations.fillna(0)

#     xai_report = []
#     abs_sum = float(correlations.abs().sum())

#     if abs_sum == 0:
#         uniform_weight = round(100 / max(len(feature_columns), 1), 1)
#         for col in feature_columns:
#             xai_report.append({
#                 "feature": col,
#                 "impact": uniform_weight,
#                 "trend": "Positive",
#                 "importance_level": "Standard",
#                 "is_nlp": False
#             })
#     else:
#         for col in feature_columns:
#             corr_val = float(correlations.get(col, 0))
#             impact = round(abs(corr_val) / abs_sum * 100, 1)
#             level = "Critical" if impact > 25 else "High" if impact > 10 else "Standard"
#             trend = "Positive" if corr_val >= 0 else "Negative"

#             xai_report.append({
#                 "feature": col,
#                 "impact": impact,
#                 "trend": trend,
#                 "importance_level": level,
#                 "is_nlp": False
#             })

#     xai_report.sort(key=lambda x: x["impact"], reverse=True)

#     top_feature = xai_report[0]["feature"]
#     top_feature_data = numeric_df[top_feature].dropna()

#     hist_counts, hist_edges = np.histogram(top_feature_data, bins=min(12, max(4, len(top_feature_data.unique()))))
#     dist_data = {
#         top_feature: {
#             "bins": [round(float(v), 3) for v in hist_edges[:-1]],
#             "counts": [int(v) for v in hist_counts],
#             "labels": [str(round(float(v), 2)) for v in hist_edges[:-1]],
#         }
#     }

#     scatter_data = {}
#     if len(xai_report) >= 2:
#         f1 = xai_report[0]["feature"]
#         f2 = xai_report[1]["feature"]
#         sample_df = numeric_df[[f1, f2]].dropna().head(300)

#         scatter_data = {
#             "feat1": f1,
#             "feat2": f2,
#             "points": [
#                 {
#                     "x": round(float(row[f1]), 4),
#                     "y": round(float(row[f2]), 4),
#                     "r": 6
#                 }
#                 for _, row in sample_df.iterrows()
#             ]
#         }

#     cumulative_values = []
#     running = 0
#     for item in xai_report:
#         running += item["impact"]
#         cumulative_values.append(round(min(running, 100), 1))

#     cumulative_data = {
#         "values": cumulative_values,
#         "labels": [item["feature"] for item in xai_report]
#     }

#     chart_recommendations = [
#         {
#             "type": "horizontalBar",
#             "title": "Feature Impact Ranking",
#             "reason": "Shows the relative weight of each feature clearly.",
#             "chartData": "impact"
#         },
#         {
#             "type": "doughnut",
#             "title": "Proportional Weight Map",
#             "reason": "Displays contribution share across the main features.",
#             "chartData": "impact"
#         },
#         {
#             "type": "line",
#             "title": "Impact Decay Curve",
#             "reason": "Shows how influence declines across ranked features.",
#             "chartData": "impact"
#         },
#         {
#             "type": "histogram",
#             "title": f"Distribution: {top_feature}",
#             "reason": "Shows how the primary driver is distributed.",
#             "chartData": "histogram",
#             "histFeature": top_feature
#         }
#     ]

#     target_series = numeric_df[target_column].dropna()
#     target_std = float(target_series.std()) if len(target_series) > 1 else 0.0
#     target_mean = float(target_series.mean()) if len(target_series) > 0 else 0.0
#     target_cv = round((target_std / target_mean) * 100, 1) if target_mean not in [0, 0.0] else 0.0

#     model_score = round(min(99.9, max(55.0, float(correlations.abs().max() * 100))), 1)

#     top_item = xai_report[0]
#     second_item = xai_report[1] if len(xai_report) > 1 else xai_report[0]

#     advanced_insights = [
#         {
#             "id": "model_reliability",
#             "title": "MODEL RELIABILITY SCORE",
#             "value": f"{model_score}%",
#             "metric": "Correlation-based local scoring",
#             "desc": "This local build is using a lightweight fallback analytics mode to keep the HTML app responsive and stable.",
#             "action": "Results are suitable for interface validation and feature flow testing.",
#             "color": "#22c55e"
#         },
#         {
#             "id": "primary_driver",
#             "title": "PRIMARY DECISION DRIVER",
#             "value": str(top_item["feature"]).upper(),
#             "metric": f"{top_item['impact']}% of total influence",
#             "desc": f"'{top_item['feature']}' is currently the strongest detected numeric driver of the target column.",
#             "action": "Prioritize monitoring this variable first.",
#             "color": "#0ea5e9"
#         },
#         {
#             "id": "data_quality",
#             "title": "DATA INTEGRITY SCORE",
#             "value": f"{round(max(0, 100 - missing_total - duplicate_rows), 1)}%",
#             "metric": f"{missing_total} missing · {duplicate_rows} duplicates",
#             "desc": "Basic integrity checks were completed on the uploaded dataset.",
#             "action": "Review missing data before relying on conclusions.",
#             "color": "#f59e0b"
#         },
#         {
#             "id": "target_volatility",
#             "title": "TARGET VOLATILITY INDEX",
#             "value": f"CV: {target_cv}%",
#             "metric": f"Std = {round(target_std, 3)}",
#             "desc": f"The selected target column is '{target_column}', and its spread was measured to estimate stability.",
#             "action": "High volatility means wider uncertainty in outcomes.",
#             "color": "#8b5cf6"
#         },
#         {
#             "id": "feature_synergy",
#             "title": "TOP-2 FEATURE SYNERGY",
#             "value": f"{round(top_item['impact'] + second_item['impact'], 1)}%",
#             "metric": "Combined influence share",
#             "desc": f"The two strongest variables are '{top_item['feature']}' and '{second_item['feature']}'.",
#             "action": "Inspect these together when investigating performance changes.",
#             "color": "#6366f1"
#         }
#     ]

#     rca_report = []
#     for idx, item in enumerate(xai_report[:6], start=1):
#         col = item["feature"]
#         series = numeric_df[col].dropna()

#         stats_payload = {
#             "mean": round(float(series.mean()), 4) if len(series) else 0,
#             "std": round(float(series.std()), 4) if len(series) > 1 else 0,
#             "min": round(float(series.min()), 4) if len(series) else 0,
#             "max": round(float(series.max()), 4) if len(series) else 0,
#             "skew": round(float(series.skew()), 4) if len(series) > 2 else 0,
#             "kurtosis": round(float(series.kurtosis()), 4) if len(series) > 3 else 0,
#             "cv": round((float(series.std()) / float(series.mean()) * 100), 1) if len(series) > 1 and float(series.mean()) != 0 else 0,
#             "outliers": 0
#         }

#         corr_val = round(float(correlations.get(col, 0)), 4)

#         rca_report.append({
#             "rank": idx,
#             "feature": col,
#             "impact": item["impact"],
#             "trend": item["trend"],
#             "importance_level": item["importance_level"],
#             "corr_with_target": corr_val,
#             "shap_mean": round(abs(corr_val), 4),
#             "shap_std": round(abs(corr_val) / 2, 4),
#             "shap_pos_pct": 100 if corr_val >= 0 else 0,
#             "stats": stats_payload,
#             "root_causes": [
#                 f"This variable shows a measurable direct relationship with '{target_column}'.",
#                 f"The detected direction is {item['trend'].lower()}, which means changes in '{col}' tend to move the outcome accordingly.",
#                 "This lightweight local mode uses numeric relationships for explanation stability."
#             ],
#             "recommendation": f"Track '{col}' closely and compare it with changes in '{target_column}' during operational review.",
#             "severity_score": 1
#         })

#     decision_narrative = {
#         "headline": "Your dataset has been analyzed successfully.",
#         "summary": f"This upload contains {len(df_clean):,} rows and {len(df_clean.columns)} columns. The current target column is '{target_column}'.",
#         "key_finding": f"The strongest detected driver is '{top_item['feature']}', with {top_item['impact']}% relative influence.",
#         "secondary_finding": f"The next important factor is '{second_item['feature']}', contributing {second_item['impact']}%.",
#         "risk_alert": "✓ No fatal analysis issue was detected in the uploaded file.",
#         "recommended_action": f"Start by reviewing '{top_item['feature']}' and its relationship to '{target_column}'."
#     }

#     corr_matrix = []
#     corr_df = numeric_df[[*feature_columns[:6], target_column]].corr(numeric_only=True)
#     for row_name in corr_df.index:
#         for col_name in corr_df.columns:
#             corr_matrix.append({
#                 "row": row_name,
#                 "col": col_name,
#                 "value": round(float(corr_df.loc[row_name, col_name]), 3)
#             })

#     dataset_meta = {
#         "rows": int(len(df_clean)),
#         "cols": int(len(df_clean.columns)),
#         "numeric_cols": int(len(numeric_df.columns)),
#         "missing_total": missing_total,
#         "duplicate_rows": duplicate_rows,
#         "target_column": target_column,
#         "target_reason": f"Fallback mode selected '{target_column}' as the last numeric column.",
#         "source_url": None
#     }

#     return {
#         "status": "success",
#         "preview": sanitize_records(df_clean),
#         "xai_report": xai_report,
#         "chart_recommendations": chart_recommendations,
#         "advanced_insights": advanced_insights,
#         "rca_report": rca_report,
#         "corr_matrix": corr_matrix,
#         "dist_data": dist_data,
#         "scatter_data": scatter_data,
#         "cumulative_data": cumulative_data,
#         "model_score": model_score,
#         "decision_narrative": decision_narrative,
#         "target_detection": {
#             "column": target_column,
#             "reason": f"Fallback mode selected '{target_column}' as the analysis target."
#         },
#         "dataset_meta": dataset_meta
#     }


# # =========================================================
# # PAGE ROUTES
# # =========================================================

# @app.route("/")
# def home():
#     template_path = TEMPLATES_DIR / "basira_app.html"

#     if not template_path.exists():
#         return f"""
#         <html lang="ar" dir="rtl">
#         <head>
#             <meta charset="UTF-8">
#             <title>Basira Local</title>
#         </head>
#         <body style="font-family:Arial;padding:40px;">
#             <h1>Basira Local</h1>
#             <p>تعذر العثور على ملف basira_app.html</p>
#             <p>Expected path: {template_path}</p>
#         </body>
#         </html>
#         """

#     return render_template("basira_app.html")


# @app.route("/health", methods=["GET"])
# def health():
#     return jsonify({
#         "status": "ok",
#         "app": "Basira Local Web App",
#         "port": DEFAULT_PORT
#     })


# @app.route("/api/app/status", methods=["GET"])
# def app_status():
#     return jsonify({
#         "status": "ok",
#         "message": "Application is running."
#     })


# # =========================================================
# # SESSION ROUTES FOR HTML COMPATIBILITY
# # =========================================================

# @app.route("/api/session/bootstrap", methods=["GET"])
# def session_bootstrap():
#     if not session.get("logged_in"):
#         session["logged_in"] = True
#         session["user_id"] = session.get("user_id", "local_user")
#         session["subscription_status"] = session.get("subscription_status", "active")
#         session["expires_at"] = ""

#     refresh_session_timeout()

#     return jsonify({
#         "status": "success",
#         "session": build_front_session_payload()
#     })


# @app.route("/api/session/status", methods=["GET"])
# def session_status():
#     if is_logged_in():
#         refresh_session_timeout()

#     return jsonify({
#         "status": "success",
#         "session": build_front_session_payload()
#     })


# @app.route("/api/session/ping", methods=["POST"])
# def session_ping():
#     if not is_logged_in():
#         return jsonify({
#             "status": "expired",
#             "message": "Session expired."
#         }), 401

#     refresh_session_timeout()

#     return jsonify({
#         "status": "success",
#         "session": build_front_session_payload()
#     })


# @app.route("/api/session/logout", methods=["POST"])
# def session_logout():
#     session.clear()
#     return jsonify({
#         "status": "success",
#         "message": "Logged out successfully."
#     })


# # =========================================================
# # OPTIONAL AUTH ALIASES
# # =========================================================

# @app.route("/api/auth/ping", methods=["GET"])
# def auth_ping():
#     return jsonify({
#         "status": "ok",
#         "message": "Auth service reachable."
#     })


# # =========================================================
# # ANALYSIS ROUTES
# # =========================================================

# @app.route("/analyze", methods=["POST", "OPTIONS"])
# def analyze():
#     if request.method == "OPTIONS":
#         return "", 200

#     try:
#         if "file" not in request.files:
#             return jsonify({
#                 "status": "error",
#                 "message": "No file uploaded."
#             }), 400

#         uploaded_file = request.files["file"]
#         if not uploaded_file or not uploaded_file.filename:
#             return jsonify({
#                 "status": "error",
#                 "message": "Uploaded file is missing."
#             }), 400

#         df = try_read_uploaded_dataframe(uploaded_file)
#         payload = numeric_analysis(df)
#         return jsonify(payload)

#     except ValueError as exc:
#         return jsonify({
#             "status": "error",
#             "message": str(exc)
#         }), 400

#     except Exception as exc:
#         return jsonify({
#             "status": "error",
#             "message": f"Analysis failed: {str(exc)}"
#         }), 500


# @app.route("/scrape_analyze", methods=["POST", "OPTIONS"])
# def scrape_analyze():
#     if request.method == "OPTIONS":
#         return "", 200

#     try:
#         url = request.form.get("url", "").strip()
#         if not url:
#             return jsonify({
#                 "status": "error",
#                 "message": "URL is required."
#             }), 400

#         demo_df = pd.DataFrame({
#             "page_metric_1": [10, 20, 15, 30, 18, 24],
#             "page_metric_2": [100, 120, 110, 160, 130, 145],
#             "engagement": [0.20, 0.35, 0.30, 0.50, 0.33, 0.41],
#             "score": [55, 66, 61, 79, 64, 71]
#         })

#         payload = numeric_analysis(demo_df)
#         payload["dataset_meta"]["source_url"] = url
#         payload["dataset_meta"]["target_reason"] = "Demo scraping mode generated a numeric sample dataset from the provided URL."
#         payload["target_detection"]["reason"] = "Demo scraping mode selected the last numeric column as target."
#         return jsonify(payload)

#     except Exception as exc:
#         return jsonify({
#             "status": "error",
#             "message": f"Scraping failed: {str(exc)}"
#         }), 500


# # =========================================================
# # MAIN
# # =========================================================

# if __name__ == "__main__":
#     app.run(host=DEFAULT_HOST, port=DEFAULT_PORT, debug=True)
"""
Basira_app_structure.py — Basira Main Web Application
======================================================
Runs locally on http://127.0.0.1:5000
Serves the main HTML interface (templates/basira_app.html) and all app APIs.
Started automatically by launcher.py after the bootstrap API is ready.

Responsibilities:
  • Serve basira_app.html via Flask templates
  • Session management (linked from cloud login via bootstrap)
  • App config, auth ping, heartbeat, auto-logout
  • Subscription status
  • File listing and AI processing placeholders
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

from flask import Flask, jsonify, request, render_template, session
from flask_cors import CORS

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR    = BASE_DIR / "static"

DEFAULT_HOST            = "127.0.0.1"
DEFAULT_PORT            = 5000
SESSION_TIMEOUT_MINUTES = 20

# ─── App ──────────────────────────────────────────────────────────────────────
app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR) if STATIC_DIR.exists() else None
)
app.secret_key = "basira-local-secret-key-change-this"

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def get_data_dir() -> Path:
    return Path.home() / "Documents" / "BasiraData"


def ensure_data_dir() -> Path:
    path = get_data_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def session_expired() -> bool:
    expires_at = session.get("expires_at")
    if not expires_at:
        return True
    try:
        expires_dt = datetime.fromisoformat(expires_at)
    except Exception:
        return True
    return datetime.utcnow() > expires_dt


def refresh_session_timeout():
    session["expires_at"] = (
        datetime.utcnow() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    ).isoformat()


def is_logged_in() -> bool:
    if not session.get("logged_in"):
        return False
    if session_expired():
        return False
    return True


def build_status_payload() -> dict:
    return {
        "status":              "ok",
        "app":                 "Basira Local",
        "version":             "1.0.0",
        "mode":                "local",
        "server_time":         now_iso(),
        "data_dir":            str(get_data_dir()),
        "logged_in":           is_logged_in(),
        "subscription_status": session.get("subscription_status", "inactive"),
        "user_id":             session.get("user_id", ""),
        "template_found":      (TEMPLATES_DIR / "basira_app.html").exists(),
        "template_dir":        str(TEMPLATES_DIR),
        "static_dir":          str(STATIC_DIR),
    }


def load_local_config() -> dict:
    config_path = ensure_data_dir() / "local_config.json"
    if not config_path.exists():
        default = {
            "app_name":   "Basira Local",
            "theme":      "light",
            "language":   "ar",
            "created_at": now_iso(),
        }
        config_path.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return {"app_name": "Basira Local", "theme": "light", "language": "ar"}


def save_local_config(config_data: dict):
    config_path = ensure_data_dir() / "local_config.json"
    config_path.write_text(json.dumps(config_data, ensure_ascii=False, indent=2), encoding="utf-8")


# ─── Session middleware ───────────────────────────────────────────────────────
@app.before_request
def before_request():
    public_paths = {"/", "/health", "/api/app/status", "/api/auth/ping", "/favicon.ico"}

    if request.path in public_paths:
        return
    if request.path.endswith((".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".webp")):
        return
    if is_logged_in():
        refresh_session_timeout()
        return
    if request.path.startswith("/api/"):
        return jsonify({
            "status":  "error",
            "message": "Session expired or not authenticated.",
            "code":    "AUTH_REQUIRED"
        }), 401


# ─── Frontend routes ──────────────────────────────────────────────────────────
@app.route("/")
def home():
    template_path = TEMPLATES_DIR / "basira_app.html"
    if not template_path.exists():
        return f"""
        <html lang="ar" dir="rtl">
        <head><meta charset="UTF-8"><title>Basira Local</title></head>
        <body style="font-family:Arial;padding:40px">
          <h1>Basira Local</h1>
          <p>تعذر العثور على ملف basira_app.html</p>
          <p>المسار المتوقع: {template_path}</p>
        </body>
        </html>
        """
    return render_template("basira_app.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Basira local app is running.", "server_time": now_iso()})


@app.route("/favicon.ico")
def favicon():
    return "", 204


# ─── App status APIs ──────────────────────────────────────────────────────────
@app.route("/api/app/status", methods=["GET"])
def api_app_status():
    return jsonify(build_status_payload())


@app.route("/api/app/config", methods=["GET"])
def api_get_app_config():
    return jsonify({"status": "ok", "config": load_local_config()})


@app.route("/api/app/config", methods=["POST"])
def api_save_app_config():
    try:
        payload = request.get_json(force=True) or {}
        config  = load_local_config()
        config["app_name"]   = payload.get("app_name",  config.get("app_name", "Basira Local"))
        config["theme"]      = payload.get("theme",     config.get("theme",    "light"))
        config["language"]   = payload.get("language",  config.get("language", "ar"))
        config["updated_at"] = now_iso()
        save_local_config(config)
        return jsonify({"status": "ok", "message": "Config updated.", "config": config})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ─── Auth APIs ────────────────────────────────────────────────────────────────
@app.route("/api/auth/ping", methods=["GET"])
def auth_ping():
    return jsonify({"status": "ok", "authenticated": is_logged_in(), "server_time": now_iso()})


@app.route("/api/auth/session", methods=["GET"])
def auth_session_get():
    if not is_logged_in():
        return jsonify({"status": "error", "message": "No active session."}), 401
    return jsonify({
        "status":  "ok",
        "session": {
            "user_id":             session.get("user_id", ""),
            "subscription_status": session.get("subscription_status", "inactive"),
            "expires_at":          session.get("expires_at", ""),
            "logged_in":           True
        }
    })


@app.route("/api/auth/session", methods=["POST"])
def auth_set_session():
    """Called by local-setup.js (or bootstrap) after cloud login to link the session."""
    try:
        payload = request.get_json(force=True) or {}
        session["logged_in"]           = True
        session["user_id"]             = payload.get("user_id", "")
        session["access_token"]        = payload.get("access_token", "")
        session["refresh_token"]       = payload.get("refresh_token", "")
        session["subscription_status"] = payload.get("subscription_status", "active")
        refresh_session_timeout()
        return jsonify({"status": "ok", "message": "Session linked.", "expires_at": session.get("expires_at")})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/auth/heartbeat", methods=["POST"])
def auth_heartbeat():
    if not is_logged_in():
        return jsonify({"status": "error", "message": "Session expired."}), 401
    refresh_session_timeout()
    return jsonify({"status": "ok", "message": "Heartbeat accepted.", "expires_at": session.get("expires_at")})


@app.route("/api/auth/auto-logout", methods=["POST"])
def auth_auto_logout():
    session.clear()
    return jsonify({"status": "ok", "message": "Logged out automatically."})


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({"status": "ok", "message": "Logged out successfully."})


# ─── Subscription APIs ────────────────────────────────────────────────────────
@app.route("/api/subscription/status", methods=["GET"])
def subscription_status():
    return jsonify({
        "status":              "ok",
        "subscription_status": session.get("subscription_status", "inactive")
    })


@app.route("/api/subscription/renew-demo", methods=["POST"])
def subscription_renew_demo():
    session["subscription_status"] = "active"
    if session.get("logged_in"):
        refresh_session_timeout()
    return jsonify({
        "status":              "ok",
        "message":             "Demo subscription renewed.",
        "subscription_status": "active"
    })


# ─── File & processing APIs (placeholders) ────────────────────────────────────
@app.route("/api/files/list", methods=["GET"])
def files_list():
    data_dir = ensure_data_dir()
    files = []
    for item in data_dir.iterdir():
        if item.is_file():
            files.append({
                "name":        item.name,
                "size":        item.stat().st_size,
                "modified_at": datetime.utcfromtimestamp(item.stat().st_mtime).isoformat() + "Z"
            })
    return jsonify({"status": "ok", "files": files})


@app.route("/api/process/test", methods=["POST"])
def process_test():
    payload = request.get_json(force=True) or {}
    return jsonify({
        "status":       "ok",
        "message":      "Local processing placeholder completed.",
        "received":     payload,
        "processed_at": now_iso()
    })


@app.route("/api/ai/analyze", methods=["POST"])
def ai_analyze():
    payload = request.get_json(force=True) or {}
    text    = payload.get("text", "")
    return jsonify({
        "status": "ok",
        "result": {
            "summary":    f"تم استلام النص محليًا بطول {len(text)} حرفًا.",
            "keywords":   [],
            "confidence": 0.95,
            "mode":       "placeholder"
        }
    })


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ensure_data_dir()
    print("=" * 55)
    print("  Basira Local — Main Web App")
    print(f"  URL:           http://{DEFAULT_HOST}:{DEFAULT_PORT}")
    print(f"  Templates dir: {TEMPLATES_DIR}")
    print(f"  Static dir:    {STATIC_DIR}")
    print("=" * 55)
    app.run(host=DEFAULT_HOST, port=DEFAULT_PORT, debug=False, threaded=True)
