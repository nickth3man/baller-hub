# Migration Learnings

## Import Issues
- Scripts in `scripts/` fail to import `src.*` modules by default when run via `uv run scripts/x.py`.
- Fix: Add project root to `sys.path` using `sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))`.

## ETL Data Mismatches
- `birth_date` column in `Player Career Info.csv` contains "NA" strings, causing DuckDB `CAST(... AS DATE)` to fail.
- Fix: Use `TRY_CAST(... AS DATE)` and specify `nullstr='NA'` in `read_csv_auto`.
- Missing stats in `Player Play By Play.csv`: This file contains advanced metrics but lacks basic stats like points/assists.
- Fix: Join `Player Play By Play.csv` with `Player Totals.csv` on `player_id`, `season`, and `team` to get the required columns while maintaining the row count expected by validation.

## DuckDB Constraints
- `bridge_ids` table has a primary key on `(bref_id, nba_id)`. Re-running the script without `ON CONFLICT DO NOTHING` fails.
- Fix: Always use `ON CONFLICT DO NOTHING` for idempotent ETL runs.

## Team Identification
- Team abbreviations like `2TM`, `3TM` (representing multiple teams in a season) are present in fact tables but missing from team dimensions.
- Fix: Populate `dim_teams` using all distinct `team` values from the fact source CSV to ensure referential integrity.

## Commands
```bash
uv run scripts/run_migration.py
```
## DuckDB Connectivity
- DuckDB does not support 'check_same_thread=False' which is common for SQLite.
- SQLModel/SQLAlchemy may try to use Postgres-specific types like SERIAL if not properly configured for DuckDB, leading to DDL errors.
- Using Views is an effective way to bridge different schemas (e.g., Star Schema to standard Webapp models) without modifying the application code.
