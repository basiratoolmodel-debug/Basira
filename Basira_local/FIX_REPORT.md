# Basira App Fix Report

## Summary
This build applies structural fixes for the Basira local multi-service app. The changes focus on Python syntax, dynamic WebScraping ports, localhost versus 127.0.0.1 consistency, backend result transfer between Preprocessor and Analysis Engine, localStorage key normalization, launcher path robustness, visible logging, upload filename safety, and dependency coverage.

## Main fixes
- Fixed the broken `fix_basira_index.py` files that previously caused a Python `SyntaxError`.
- Replaced the hardcoded Web Scraper port `3001` with dynamic `scraper.port` detection.
- Unified local service URLs to `127.0.0.1`.
- Added backend result storage to the Analysis Engine using `/api/store-result` and `/api/analysis-result/<run_id>`.
- Updated Preprocessor navigation to pass `run_id` to Analysis Engine instead of relying on `sessionStorage` across different ports.
- Kept localStorage fallback for compatibility.
- Migrated chart config storage from `basiraChartConfigs` to `basira_chart_configs`.
- Added `target_column` compatibility while keeping `target_col` as a temporary fallback.
- Made launcher paths more robust when files are run from either root or `templates`.
- Added log files under `logs/` instead of suppressing subprocess output.
- Added `secure_filename` for file uploads.
- Added missing WebScraping dependencies to `requirements.txt`.

## Validation performed
- Ran Python compilation over all `.py` files using `py_compile`.
- Result: `0` Python compile errors.

## How to run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the app:
   ```bash
   python launcher.py
   ```
3. Check health endpoints:
   - `http://127.0.0.1:5000/health`
   - `http://127.0.0.1:5050/health`
   - `http://127.0.0.1:5055/health`
   - Web Scraper uses the port stored in `scraper.port`.

## Files intentionally left duplicated
Some duplicate files still exist because the project structure currently references both root-level launchers and backend files inside `templates`. The dangerous path assumptions were made more robust, but the physical duplicates were not deleted to avoid breaking existing references.
