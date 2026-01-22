# Plan: Postgres to DuckDB Migration & Decoupling

## Context
The goal is to complete the migration of `baller-hub` to a DuckDB-backed architecture and decouple the scraper.
**CRITICAL CONTEXT**: The codebase is currently in a **BROKEN, PARTIALLY MIGRATED STATE**.
- `pyproject.toml` already has DuckDB deps.
- `session.py` is already Sync.
- `services/*.py` are defined as Sync (`def`) but contain invalid `await` calls.
- `api/v1/*.py` still use `AsyncSession` (Mismatch).

This plan focuses on **fixing the broken state** and completing the architecture shift.

### Core Objectives
1. **Fix Broken State**: Repair the mixed Sync/Async code in Services and API layer.
2. **Decouple Scraper**: Isolate `src/scraper` via new `src/core`.
3. **Finish Migration**: Complete the move to DuckDB (Schema, ETL).
4. **Accuracy**: Implement rigid validation pipeline.

### Architecture Shift
| Component | Current Broken State | Target State |
|-----------|----------------------|--------------|
| **Database** | Configured for DuckDB but broken | DuckDB (Embedded, `./baller.duckdb`) |
| **Connectivity** | Sync Engine but API expects Async | Sync Engine + Sync API |
| **Services** | `def` methods with `await` (Syntax Error) | Pure Sync `def` methods |
| **Scraper** | Coupled via `common/data.py` | Sibling module depending on `src/core` |

---

## Work Plan

### Phase 1: Decoupling & Shared Kernel
Establish the neutral ground for shared code.

- [x] 1. Create `src/core` package structure
  - Create `src/core/__init__.py`
  - Create `src/core/domain.py` for shared Enums (Team, Position)
  - Create `src/core/constants.py` for shared logic

- [x] 2. Migrate Shared Enums
  - **Move**: `src/scraper/common/data.py` content -> `src/core/domain.py`
  - **Refactor**: Update imports in `src/scraper` to use `src.core.domain`
  - **Refactor**: Update imports in `src/webapp` to use `src.core.domain`
  - **Verify**: Run `uv run pytest tests/` to check for import errors
  - **Commit**: `refactor(core): extract shared domain primitives`

### Phase 2: Fix Broken Migration (Sync Conversion)
Repair the invalid code resulting from the partial migration.

- [x] 3. Fix Service Layer (Syntax Errors)
  - **Refactor**: `src/webapp/backend/app/services/*.py` (player_service.py, etc.)
  - **Action**: Remove all orphaned `await` keywords from the `def` methods.
  - **Action**: Ensure all DB calls use the sync `session.execute()` / `session.scalars()` API.
  - **Verify**: `uv run ruff check .` (Should pass syntax checks).

- [x] 4. Fix API Layer (Type Mismatch)
  - **Refactor**: `src/webapp/backend/app/api/v1/**/*.py`
  - **Action**: Remove `AsyncSession` imports. Replace with `Session`.
  - **Action**: Update `get_session` dependency to return `Session`.
  - **Critical**: Convert endpoints from `async def` to `def` (Sync).
    - *Why*: DuckDB is synchronous. Sync `def` endpoints run in FastAPI's threadpool, preventing event loop blocking. `async def` with sync calls would block the entire app.

- [x] 5. Cleanup Infrastructure & Dependencies
  - **Delete**: `src/webapp/docker-compose.yml`
  - **Delete**: `src/webapp/backend/alembic/` (folder)
  - **Delete**: `src/webapp/backend/alembic.ini`
  - **Refactor**: `src/webapp/backend/pyproject.toml`
    - Verify `asyncpg`, `psycopg2-binary`, `alembic` are removed.
    - Verify `duckdb` is present.
  - **Run**: `uv sync` to finalize lockfile.

### Phase 3: ETL Pipeline & Schema
Build the engine that powers the data.

- [x] 6. Define DuckDB Schema
  - **Create**: `src/etl/schema.py`
  - **Define**: Star Schema DDL
    - `dim_players` (B-Ref ID, NBA ID, Name, Birthdate)
    - `dim_teams` (B-Ref ID, NBA ID, Abbr)
    - `fact_player_gamelogs` (Wide table)
    - `bridge_ids` (Mapping table)

- [x] 7. Implement ID Bridge Logic
  - **Create**: `src/etl/identity.py`
  - **Inputs**:
    - B-Ref Source: `raw-data/misc-csv/csv_2/`
    - NBA Source: `raw-data/database/sqlite/nba.sqlite`
  - **Logic**:
    - Load B-Ref Players -> Base Set
    - Load NBA Players -> Candidate Set
    - Match on `(normalized_name, birth_date)`
    - Insert matches into `bridge_ids`

- [x] 8. Implement Bulk Loaders
  - **Create**: `src/etl/loader.py`
  - **Dependencies**: `duckdb.sql("INSTALL sqlite; LOAD sqlite;")`
  - **Logic**:
    - Use `duckdb.sql("INSERT INTO target SELECT ... FROM read_csv('raw-data/misc-csv/csv_2/...')")`
    - Use `duckdb.sql("ATTACH 'raw-data/database/sqlite/nba.sqlite' AS nba (TYPE SQLITE); INSERT ... FROM nba.play_by_play ...")`
    - Prioritize `csv_2` for historical stats
    - Prioritize `nba.sqlite` for Play-by-Play details

### Phase 4: Validation Suite (100% Accuracy)
Trust but verify.

- [x] 9. Implement Validation Rules
  - **Create**: `src/etl/validate.py`
  - **Parity Checks**: `assert duckdb_count == csv_line_count`
  - **Logic Checks**: `assert points == 2*fg2 + 3*fg3 + ft`
  - **Referential Integrity**: `assert count(orphaned_game_ids) == 0`

- [ ] 10. Run Full Migration
  - **Script**: Create `scripts/run_migration.py`
  - **Execution**: Init DB -> Build Identity Bridge -> Load Data -> Run Validation
  - **Deliverable**: `baller.duckdb` (Verified)

### Phase 5: Webapp Wiring
Connect the UI to the new engine.

- [ ] 11. Connect Webapp to DuckDB
  - **Config**: Update `config.py` to point to `./baller.duckdb`
  - **Verify**: Start backend `uv run fastapi dev`
  - **Test**: Hit `/api/v1/players` -> Verify data loads

---

## Verification Strategy
- **Syntax Check**: `uv run ruff check .` MUST pass (proving `await` keywords are gone).
- **Import Check**: `uv run pytest tests/` MUST pass (proving `src/core` refactor worked).
- **Data Check**: `src/etl/validate.py` MUST pass all assertions.
- **Performance Check**: Webapp endpoints must respond without blocking (verified by converting to `def`).

## Success Criteria
- [ ] Codebase is syntactically valid (no Sync/Async mixing).
- [ ] `baller.duckdb` exists and passes validation.
- [ ] Webapp loads player data from DuckDB.
- [ ] No PostgreSQL artifacts remain.
