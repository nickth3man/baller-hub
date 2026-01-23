DuckDB-Native Architecture Strategy
Executive Summary
The Oracle recommends a "Build and Swap" architecture that embraces DuckDB's embedded, OLAP-focused nature rather than fighting it. The key insight is to treat the database as a Data Artifact—a file built by ETL and consumed read-only by the webapp.
Core Recommendation: Build and Swap
| Component         | Current State                           | Target State                 |
| ----------------- | --------------------------------------- | ---------------------------- |
| ETL Pipeline      | src/etl/ (functional, standalone)       | ✅ Single source of truth     |
| Ingestion         | app/ingestion/ (broken, spec-compliant) | ❌ DELETE                     |
| Database          | DuckDB with shims/views                 | DuckDB as read-only artifact |
| Webapp Role       | Read-write capable                      | Read-only consumer           |
| Schema Definition | SQLModel ORM                            | Direct SQL in ETL            |
---
Part 1: Architecture - The "Data Artifact" Pattern
Why This Architecture?
DuckDB's characteristics that inform this decision:
| Characteristic          | Implication                                    |
| ----------------------- | ---------------------------------------------- |
| Embedded                | No server, single file                         |
| OLAP-focused            | Excellent for reads, limited concurrent writes |
| Windows File Locking    | Cannot overwrite open file                     |
| Fast Analytical Queries | SQL is often cleaner than ORM                  |
The Pattern: Build and Swap
┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   Basketball-    │────▶│    Scraper's    │────▶│   src/etl/       │
│   Reference.com  │     │   Raw Output    │     │   Build Pipeline │
└──────────────────┘     │   (Parquet/CSV) │     └────────┬─────────┘
                         └─────────────────┘              │
                                                          ▼
                         ┌─────────────────┐     ┌──────────────────┐
                         │   baller.duckdb │◀────│   Validation     │
                         │   (Production)  │     │   & Star Schema  │
                         └────────┬────────┘     └──────────────────┘
                                  │
                                  ▼ (Read-Only Mount)
                         ┌──────────────────┐
                         │  FastAPI Webapp  │
                         │  (DuckDB Client) │
                         └──────────────────┘
Key Benefits
1. Simplicity: No connection pooling, no transaction management
2. Performance: Queries run directly on optimized DuckDB engine
3. Reliability: Bad ETL = bad artifact = not deployed
4. Testability: .duckdb file can be validated before deployment
---
Part 2: ETL Integration - Single Pipeline
Consolidate to src/etl/
The dual-pipeline chaos ends. src/etl/ becomes the production pipeline.
Current src/etl/ Components (Functional)
| File        | Purpose                | Status           |
| ----------- | ---------------------- | ---------------- |
| schema.py   | DDL for Star Schema    | ✅ Keep           |
| identity.py | BREF ↔ NBA ID bridging | ✅ Keep, enhance  |
| loader.py   | Dimension/Fact loading | ✅ Keep           |
| validate.py | Data quality checks    | ✅ Port key logic |
| __init__.py | Package marker         | ✅ Keep           |
New ETL Flow
1. COPY CSV → Staging Tables (in DuckDB)
2. Validate Staging (port from validate.py)
3. Upsert to Dimensions (dim_players, dim_teams)
4. Build Facts (fact_player_gamelogs)
5. Validate Final State (row counts, formulas)
6. Export to baller.duckdb
Validation Logic to Port
From src/etl/validate.py:
- ✅ Row Count Parity: CSV rows = DB rows
- ✅ Formula Validation: Points = FG*2 + 3PT + FT
- ✅ Referential Integrity: Orphaned player/team IDs
- ⚠️ Port to: app/ingestion/tasks.py or integrate into ETL
---
Part 3: Webapp Refactoring
Current Issues
| Issue                  | Location               | Severity |
| ---------------------- | ---------------------- | -------- |
| SQLModel for DDL       | app/models/            | 🔴 High   |
| Write-capable sessions | app/db/session.py      | 🔴 High   |
| Empty validation       | app/ingestion/tasks.py | 🟡 Medium |
| Dual pipeline          | app/ingestion/         | 🔴 High   |
Target Webapp Architecture
src/webapp/backend/
├── app/
│   ├── api/v1/              # API Endpoints (unchanged)
│   │   ├── endpoints/
│   │   ├── routers/
│   │   └── schemas/         # Pydantic DTOs only
│   ├── db/
│   │   ├── connection.py    # Read-only DuckDB connection
│   │   └── queries/         # Direct SQL queries
│   └── main.py              # FastAPI app
├── baller.duckdb            # Data artifact (symlink or config path)
└── pyproject.toml
Changes Required
1. Database Connection (app/db/connection.py)
import duckdb
from contextlib import contextmanager
# Global connection - read-only mode
_conn: duckdb.DuckDBPyConnection | None = None
def get_connection() -> duckdb.DuckDBPyConnection:
    global _conn
    if _conn is None:
        _conn = duckdb.connect(
            str(settings.duckdb_path),
            read_only=True
        )
    return _conn
def close_connection():
    global _conn
    if _conn:
        _conn.close()
        _conn = None
@contextmanager
def session():
    conn = get_connection()
    try:
        yield conn
    finally:
        pass  # Don't close - shared connection
2. Query Pattern (No ORM)
# Instead of: session.query(Player).filter(Player.slug == slug).first()
# Use:
def get_player_by_slug(conn, slug: str) -> dict | None:
    result = conn.execute(
        "SELECT * FROM dim_players WHERE slug = ?",
        [slug]
    ).fetchone()
    return dict(result._asdict()) if result else None
3. Pydantic Models Only (No SQLModel for Tables)
# app/schemas/player.py
from pydantic import BaseModel
class PlayerBase(BaseModel):
    slug: str
    first_name: str
    last_name: str
    position: str | None = None
    height_inches: float | None = None
    
class PlayerDetail(PlayerBase):
    career_points: int
    career_assists: int
    career_rebounds: int
    
    class Config:
        from_attributes = True
4. Hot Reload Endpoint (for Windows file locking)
# app/api/v1/admin.py
from fastapi import APIRouter, HTTPException
from app.db.connection import close_connection, get_connection
router = APIRouter(prefix="/admin", tags=["admin"])
@router.post("/reload-database")
def reload_database():
    """
    Trigger a database reload (for hot-swapping baller.duckdb)
    """
    try:
        # Close existing connection
        close_connection()
        
        # Optionally validate new file exists
        new_path = settings.duckdb_path
        if not new_path.exists():
            raise HTTPException(status_code=500, detail="Database file not found")
        
        # Reopen connection
        get_connection()
        
        return {"status": "reloaded", "path": str(new_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
---
Part 4: Schema Strategy
Keep the Star Schema
The existing Star Schema is perfect for DuckDB:
┌─────────────────────────────────────────────────────────────┐
│                      fact_player_gamelogs                    │
│  (grain: player + game)                                     │
├─────────────────────────────────────────────────────────────┤
│  player_id (FK)                                             │
│  game_id (FK)                                               │
│  team_id (FK)                                               │
│  minutes_played                                             │
│  points_scored                                              │
│  ... (all box score stats)                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├──┬──┐
                              │  │  │
                 ┌────────────┘  │  └────────────┐
                 ▼               ▼               ▼
        ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
        │ dim_players │  │  dim_teams  │  │  dim_games  │
        └─────────────┘  └─────────────┘  └─────────────┘
Schema Definition
Where: In src/etl/schema.py (SQL DDL)
How: Direct DuckDB SQL, not SQLModel
# src/etl/schema.py
SETUP_SQL = """
-- Dimensions
CREATE SEQUENCE IF NOT EXISTS seq_players;
CREATE TABLE IF NOT EXISTS dim_players (
    player_id INTEGER PRIMARY KEY,
    bref_id VARCHAR(20) UNIQUE,
    nba_id VARCHAR(20),
    slug VARCHAR(30),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    birth_date DATE,
    position VARCHAR(10),
    height_inches FLOAT,
    college VARCHAR(100)
);
CREATE SEQUENCE IF NOT EXISTS seq_teams;
CREATE TABLE IF NOT EXISTS dim_teams (
    team_id INTEGER PRIMARY KEY,
    abbreviation VARCHAR(3) UNIQUE,
    name VARCHAR(100),
    city VARCHAR(100),
    arena VARCHAR(100)
);
-- Facts
CREATE TABLE IF NOT EXISTS fact_player_gamelogs (
    player_id INTEGER,
    game_id INTEGER,
    team_id INTEGER,
    season_year INTEGER,
    season_type VARCHAR(20),
    minutes_played INTEGER,
    points_scored INTEGER,
    assists INTEGER,
    rebounds_total INTEGER,
    steals INTEGER,
    blocks INTEGER,
    turnovers INTEGER,
    personal_fouls INTEGER,
    plus_minus INTEGER,
    PRIMARY KEY (player_id, game_id)
);
-- Views for API compatibility
CREATE VIEW IF NOT EXISTS player AS SELECT * FROM dim_players;
CREATE VIEW IF NOT EXISTS team AS SELECT * FROM dim_teams;
CREATE VIEW IF NOT EXISTS game AS SELECT * FROM dim_games;
"""
Why Abandon SQLModel for DDL?
| Aspect           | SQLModel           | DuckDB Native                     |
| ---------------- | ------------------ | --------------------------------- |
| Migrations       | Alembic required   | SQL scripts are source of truth   |
| Performance      | ORM overhead       | Direct SQL execution              |
| DuckDB Features  | Limited support    | Full support (LIST, STRUCT, etc.) |
| Schema Evolution | Complex migrations | Simple script re-runs             |
---
Part 5: Implementation Roadmap
Phase 1: Cleanup (1 day)
Delete dead weight:
# Delete the spec-compliant but broken pipeline
rm -rf src/webapp/backend/app/ingestion/
rm -rf src/webapp/backend/alembic/
Keep for now:
- src/webapp/backend/app/models/ - Can be converted to Pydantic-only later
- src/webapp/backend/app/db/session.py - Rewritten for read-only
Phase 2: ETL Consolidation (2-3 days)
1. Port validation logic from src/etl/validate.py into main ETL flow
2. Add staging tables to src/etl/schema.py
3. Implement batch tracking (import_batch_id)
4. Add error logging to DuckDB
5. Create export step that validates and packages baller.duckdb
Phase 3: Webapp Refactor (2-3 days)
1. Rewrite app/db/connection.py for read-only DuckDB
2. Convert SQLModel to Pydantic for response models only
3. Replace ORM queries with direct duckdb.execute()
4. Add hot-reload endpoint for Windows file locking
5. Update settings to point to artifact path
Phase 4: Documentation (1 day)
1. Update docs/reference/schema.md - Document DuckDB Star Schema
2. Delete docs/specs/implementation.md - PostgreSQL spec no longer applies
3. Create docs/data-lifecycle.md - Document "Build and Swap" process
4. Update docs/page-types.md - Add missing 6 page types
5. Update AGENTS.md - New architecture instructions
---
Part 6: Files to Modify/Delete
Delete (Immediately)
❌ src/webapp/backend/app/ingestion/
❌ src/webapp/backend/alembic/
❌ docs/specs/implementation.md
Refactor (Phase 1-3)
🔄 src/webapp/backend/app/db/session.py → connection.py
🔄 src/webapp/backend/app/db/database.py → Delete (replaced by DuckDB)
🔄 src/webapp/backend/app/models/ → Convert to Pydantic DTOs
🔄 src/webapp/backend/app/api/v1/endpoints/ → Direct SQL queries
Keep and Enhance
✅ src/etl/schema.py - Define Star Schema
✅ src/etl/identity.py - ID bridging
✅ src/etl/loader.py - ETL pipeline
✅ src/etl/validate.py - Port to main flow
✅ src/scraper/ - Functional scraper
Create
🆕 docs/reference/duckdb-schema.md - Document Star Schema
🆕 docs/data-lifecycle.md - Build and Swap documentation
🆕 src/webapp/backend/app/db/connection.py - Read-only DuckDB
🆕 src/webapp/backend/app/db/queries/ - Direct SQL queries
---
Part 7: Windows-Specific Considerations
The File Locking Problem
On Linux: mv new.db baller.db works even if baller.db is open.
On Windows: File must be closed before replacement.
Solution: Hot Reload Pattern
# src/webapp/backend/app/core/reload.py
import os
import shutil
from pathlib import Path
class DatabaseReloader:
    def __init__(self, current_path: Path, staging_path: Path):
        self.current_path = current_path
        self.staging_path = staging_path
    
    def swap(self) -> bool:
        """
        Perform atomic swap of database files.
        Returns True if successful, False otherwise.
        """
        try:
            # 1. Close all connections (handled by endpoint)
            # 2. Rename current to backup (in case of failure)
            backup_path = self.current_path.with_suffix('.backup.db')
            if self.current_path.exists():
                os.rename(self.current_path, backup_path)
            
            # 3. Move staging to current
            os.rename(self.staging_path, self.current_path)
            
            # 4. Clean up backup
            if backup_path.exists():
                backup_path.unlink()
            
            return True
        except Exception:
            # Rollback
            if backup_path.exists():
                os.rename(backup_path, self.current_path)
            return False
Update Workflow
1. ETL runs → produces baller_staging.duckdb
2. Validation passes → signals Webapp via POST /admin/reload-db
3. Webapp closes connection → calls DatabaseReloader.swap()
4. File swapped atomically → Webapp reopens connection
5. Users see new data on next request
---
Part 8: Edge Cases and Risks
Risk 1: Windows File Locking
Mitigation: Always close connection before swap. Use the hot-reload endpoint.
Risk 2: ETL Failures Leave Stale Data
Mitigation: Keep old .duckdb as backup. Only promote staging to production after validation passes.
Risk 3: Complex ORM Features Missing
Mitigation: DuckDB SQL is often cleaner. For complex queries, write them in SQL files and load with conn.execute(open('query.sql').read()).
Risk 4: No Concurrent Writes
Mitigation: That's the point. ETL builds, Webapp reads. No concurrent writes needed.
Risk 5: Missing Features (Auth, User Data)
Mitigation: Use separate SQLite or managed service for user data. Don't mix OLTP (users) with OLAP (stats).
---
Summary: Action Items
This Week
| Priority   | Action                                     | Effort  |
| ---------- | ------------------------------------------ | ------- |
| 🔴 Critical | Delete app/ingestion/                      | 5 min   |
| 🔴 Critical | Rewrite app/db/connection.py for read-only | 2 hours |
| 🟡 High     | Port validate.py logic to ETL flow         | 4 hours |
| 🟡 High     | Convert SQLModel to Pydantic               | 4 hours |
This Month
| Priority | Action                              | Effort  |
| -------- | ----------------------------------- | ------- |
| 🟡 High   | Replace ORM queries with direct SQL | 8 hours |
| 🟡 Medium | Add hot-reload endpoint             | 2 hours |
| 🟡 Medium | Update documentation                | 4 hours |
| 🟢 Low    | Add staging tables to ETL           | 2 days  |
Long-term
| Priority | Action                           | Effort  |
| -------- | -------------------------------- | ------- |
| 🟢 Low    | Add automated ETL scheduling     | 1 day   |
| 🟢 Low    | Create query library (SQL files) | 1 week  |
| 🟢 Low    | Add data quality dashboard       | 2 weeks |
---
Conclusion
The "Build and Swap" architecture transforms the current chaos into a clean, maintainable system:
1. Single Pipeline: src/etl builds a validated .duckdb artifact
2. Read-Only Webapp: Consumes the artifact without writes
3. DuckDB-Native: Full use of DuckDB's analytical power
4. Windows-Ready: Hot-reload pattern handles file locking
5. Well-Documented: Clear separation between ETL and serving
This architecture is simpler, faster, and more reliable than the current dual-pipeline approach.