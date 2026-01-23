# Ruff Analysis & Magic Value Findings

**Date:** 2026-01-22
**Files Analyzed:** `analyze_bbr.py`, `src/etl/validate.py`

## Findings

### 1. analyze_bbr.py

**Ruff Violation:**
- **Location:** Line 86
- **Rule:** `TRY400`
- **Issue:** Use of `logger.error` inside `except` block obscures traceback.
- **Fix:** Replace `logger.error("Error: %s", e)` with `logger.exception("Error analyzing URLs")`.

**Magic Values:**
- **Location:** Line 24
- **Issue:** Hardcoded `timeout=30` and `impersonate="chrome120"`.
- **Fix:** Extract to module constants:
  ```python
  TIMEOUT_SECONDS = 30
  BROWSER_IMPERSONATION = "chrome120"
  ```

### 2. src/etl/validate.py

**Magic Values:**
- **Location:** Line 12
- **Issue:** Hardcoded CSV path `'raw-data/misc-csv/csv_2/Player Play By Play.csv'`.
- **Fix:** Extract to module constant:
  ```python
  PLAY_BY_PLAY_CSV_PATH = 'raw-data/misc-csv/csv_2/Player Play By Play.csv'
  ```
