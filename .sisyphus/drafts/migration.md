# Draft: PostgreSQL Removal & DuckDB Migration

## Requirements (Confirmed)
- **Remove PostgreSQL**: Completely eliminate all PostgreSQL dependencies and infrastructure.
- **Decouple Scraper/Webapp**: Separate the scraping logic from the web application.
- **New Database Engine**: DuckDB.
- **Data Sources**:
  - `raw-data\database\sqlite\nba.sqlite`
  - `raw-data\misc-csv` (all CSV files)
- **Data Integrity**: Database must be 100% accurate, mirror basketball-reference.com structure, and have proper relational links.
- **Webapp Backend**: Must use the new DuckDB instance.

## Open Questions
- **DuckDB Strategy**: In-process file vs. Server mode (MotherDuck)?
- **Schema**: Auto-infer from SQLite/CSVs or strictly typed definition?
- **Migration**: One-time ETL script or continuous pipeline?
- **ORM/Query Builder**: What is currently used (SQLAlchemy/Kysely) and should we keep it?

## Scope Boundaries
- **INCLUDE**:
  - Migration scripts (SQLite/CSV -> DuckDB).
  - Webapp backend refactoring to use DuckDB.
  - Scraper refactoring to remove DB dependency (or output to DuckDB?).
- **EXCLUDE**:
  - (Pending analysis)

## Research Needed
- Current PostgreSQL coupling.
- Webapp DB access layer structure.
- Scraper's current output method.

## Data Source Analysis
- `raw-data/database/sqlite/nba.sqlite`: Checking existence and schema.
- `raw-data/misc-csv`: checking file list.

