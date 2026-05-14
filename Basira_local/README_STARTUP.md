# Basira App — Startup Guide

## ✅ Correct Way to Start

### Full App (recommended)
```
python launcher.py
```
- Opens the main UI at: **http://127.0.0.1:5000/**
- Also starts bootstrap (port 5001) automatically.

### Main UI only (no bootstrap)
```
python Basira_app_structure.py
```
- Opens at: **http://127.0.0.1:5000/**
- Home page serves `templates/basira_app.html`

### ❌ Wrong — do NOT run these as the main entry point:
```
# These run on different ports and will NOT show the home UI
python basira_local_bootstrap.py    # → port 5001 (setup API only)
python templates/basira_bridge_orchestrator.py  # → port 5055 (analysis only)
python templates/basira_app.py      # → port 5050 (preprocessor only)
```

---

## Module Ports

| Module            | Port | Entry Point                                |
|-------------------|------|--------------------------------------------|
| Main UI / Home    | 5000 | `Basira_app_structure.py`                  |
| Bootstrap (auth)  | 5001 | `basira_local_bootstrap.py`                |
| Preprocessor      | 5050 | `templates/basira_app.py`                  |
| Analysis Bridge   | 5055 | `templates/basira_bridge_orchestrator.py`  |
| Web Scraper       | auto | `templates/WebScraping/app.py`             |

---

## Flow 1: Upload → Preprocess → Analyze
1. Run `python Basira_app_structure.py`
2. Open http://127.0.0.1:5000/
3. Upload CSV/XLSX → Home page runs analysis directly via bridge.

## Flow 2: Full Pipeline
1. Click Preprocessing → upload file → preprocess
2. Click "Continue to Analysis Engine" → bridge runs automatically
3. RCA + insights appear in the Analysis Engine

## Flow 3: Web Scraping → Preprocess → Analyze
1. Click Web Scraping → scrape data → export as CSV
2. The scraped CSV is saved to `basira_runtime/session_state.json`
3. Click Preprocessing → file is auto-loaded
4. Continue to Analysis Engine

---

## Session State
All modules share: `basira_runtime/session_state.json`
This file tracks the current dataset path across modules.
