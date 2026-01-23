# DuckDB Build Pipeline (Phase 1 & 2)

## Context

### Original Request
Implement the "Build and Swap" architecture defined in `PLAN.md`.
Focus on **Phase 1 (Cleanup)** and **Phase 2 (ETL Build Pipeline)**.

### Interview Summary
**Key Discussions**:
- **Staging Schema**: Use explicit column definitions ported from `tasks.py` (strict schema).
- **Output Strategy**: Build script writes directly to `src/webapp/baller.duckdb`.
- **Validation Failure**: Keep the artifact for debugging if validation fails.
- **Views**: Move View creation from `session.py` (runtime) to `schema.py` (build-time).
- **Slug Generation**: Port the complex logic (jamesle01 style) from `tasks.py` to `builder.py`.

**Research Findings**:
- `src/webapp/backend/app/ingestion/` contains 1300+ lines of redundant code.
- `src/webapp/backend/app/celery_app.py` imports `app.ingestion`, which must be removed before deletion.
- `src/webapp/backend/app/db/session.py` has the View definitions we need to port.
- Windows file locking requires the file to be closed before replacement.

### Metis Review
**Guardrails Applied**:
- **Dependency Check**: Must remove imports of `app.ingestion` from `celery_app.py` and `main.py` BEFORE deleting the directory.
- **Atomic Swap Safety**: Build to `.tmp` extension first, then rename. Handle `PermissionError` on Windows if webapp is running.
- **Data Discovery**: Robust `find_project_root` needed to locate `raw-data`.
- **Slug Logic**: Explicitly requiring the complex slug generation logic to be ported.

---

## Work Objectives

### Core Objective
Replace the broken runtime ingestion pipeline with a robust, offline DuckDB build script.

### Concrete Deliverables
- `src/etl/builder.py`: New orchestrator script (Logic + Slugs).
- `src/etl/schema.py`: Updated with Staging tables and Views.
- `src/webapp/baller.duckdb`: The resulting artifact.

### Definition of Done
- [x] `app/ingestion` directory is gone.
- [x] `uv run python src/etl/builder.py` runs successfully.
- [x] `baller.duckdb` contains all tables and views.
- [x] Player slugs match the legacy format (e.g., `jamesle01`).

### Must Have
- Explicit staging table definitions (no `CREATE TABLE AS SELECT * FROM read_csv`).
- Ported Slug Generation Logic (first 5 last + first 2 first + counter).
- Pre-baked Views for `player`, `team`, `season`.

### Must NOT Have (Guardrails)
- Do NOT modify `src/webapp/backend/app/api/` (Phase 3).
- Do NOT delete `app/db/session.py` (Phase 3).
- Do NOT implement the "Hot Reload" endpoint (Phase 3).

---

## Verification Strategy

### Test Decision
- **Strategy**: Manual Execution Verification (The build *is* the test).

### Verification Procedures

**1. Cleanup Verification**
- Check for lingering imports: `grep -r "app.ingestion" src/webapp/backend`
- Specific Check: `src/webapp/backend/app/celery_app.py` should NOT contain `app.ingestion`.

**2. Build Script Verification**
- Run: `uv run python src/etl/builder.py`
- Verify Output:
  ```bash
  duckdb src/webapp/baller.duckdb "SELECT slug FROM player WHERE first_name='LeBron' AND last_name='James'"
  # Expected: jamesle01
  ```

---

## Task Flow

```
Cleanup (1-3) → Schema Update (4) → Build Script (5-6) → Execution (7)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 4, 5 | Schema update and Builder skeleton can be written in parallel |

---

## TODOs

- [x] 1. Remove Ingestion Dependencies (CRITICAL)
  **What to do**:
  - Edit `src/webapp/backend/app/celery_app.py`: Remove `import app.ingestion.tasks` and `celery_app.conf.imports` references.
  - Edit `src/webapp/backend/app/main.py` (if applicable): Remove any ingestion references.
  - Edit `src/webapp/scripts/seed_db.py`: Remove imports of `app.ingestion`. (It may break, but we are replacing it).
  **Verification**: `grep -r "app.ingestion" src/webapp/backend` returns no results (except the dir itself).
  **Parallelizable**: NO (Must be first)

- [x] 2. Delete Legacy Ingestion
  **What to do**:
  - Delete `src/webapp/backend/app/ingestion/` directory.
  - Delete `src/webapp/backend/alembic/` directory.
  - Delete `src/webapp/backend/app/db/migrations/` (if exists).
  **Verification**: Folders no longer exist.
  **Parallelizable**: NO (Depends on 1)

- [x] 3. Read Legacy Logic (Context Capture)
  **What to do**:
  - Read `src/webapp/backend/app/ingestion/tasks.py` one last time to extract:
    - `STAGING_TABLES` dict.
    - Slug generation SQL (Lines 595-618).
  - Read `src/webapp/backend/app/db/session.py` to extract `init_db` VIEW SQL.
  **Verification**: Context ready for Step 4.
  **Parallelizable**: YES

- [x] 4. Update ETL Schema (`src/etl/schema.py`)
  **What to do**:
  - Add `STAGING_TABLES` definitions matching `tasks.py`.
  - Add `setup_views(con)` function containing the `CREATE VIEW` statements from `session.py`.
  - Ensure `setup_schema(con)` calls `setup_views(con)`.
  **Verification**: `uv run python -c "import duckdb; from src.etl.schema import setup_schema; con=duckdb.connect(); setup_schema(con); print('Schema OK')"`
  **Parallelizable**: YES (with 5)

- [x] 5. Create Builder Skeleton (`src/etl/builder.py`)
  **What to do**:
  - Create file `src/etl/builder.py`.
  - Implement `find_project_root()` logic to locate `raw-data`.
  - Implement `build()` function structure:
    1. Connect to `.tmp.duckdb`.
    2. `schema.setup_schema()`.
    3. `loader.load_staging()` (placeholder/call existing).
    4. `validate.validate()` (placeholder).
  **Verification**: Script runs and prints steps.
  **Parallelizable**: YES (with 4)

- [x] 6. Implement ETL Logic & Slugs
  **What to do**:
  - Port `_load_staging_tables` logic from `tasks.py` to `src/etl/builder.py`.
  - **CRITICAL**: Port the Slug Generation SQL (window functions) from `tasks.py` into the `INSERT INTO player` step.
  - Implement "Atomic Swap":
    - Close connection.
    - `os.replace('baller.duckdb.tmp', 'src/webapp/baller.duckdb')`.
  **References**:
  - `src/webapp/backend/app/ingestion/tasks.py` (Lines 595-618 for Slugs)
  **Verification**: Running builder creates a populated DB file.

- [x] 7. Port Validation Logic
  **What to do**:
  - Read `src/etl/validate.py`.
  - Integrate it into `builder.py` execution flow.
  - If validation fails, `sys.exit(1)` but do NOT delete the `.tmp` file.
  **Verification**: Run builder with valid data -> Success. Corrupt data -> Fail + Keep Artifact.

---

## Success Criteria

### Verification Commands
```bash
# 1. Run the build
uv run python src/etl/builder.py

# 2. Verify artifact exists
ls -l src/webapp/baller.duckdb

# 3. Verify content and slugs
uv run python -c "import duckdb; con=duckdb.connect('src/webapp/baller.duckdb', read_only=True); print(con.sql('SELECT slug, first_name FROM player LIMIT 5').fetchall())"
```

### Final Checklist
- [x] app/ingestion is gone and dependencies removed from `celery_app.py`
- [x] baller.duckdb is created by script
- [x] Views `player`, `team`, `season` exist in `baller.duckdb`
- [x] Slugs follow `jamesle01` format
