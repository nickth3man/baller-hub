- Deleted legacy ingestion code and migrations as we move to a 'replace the whole DB file' strategy with DuckDB.
- Created `src/etl/builder.py` to orchestrate DuckDB creation.
- Implemented `find_project_root` to robustly locate the project root based on `raw-data` or `.git`.
- Implemented `build` function to handle the build lifecycle: verify root, clean temp, connect, setup schema.
- Used `logging` instead of `print` for better observability and to pass linter checks.
- Verified script execution and schema initialization.

## AGENTS.md Generation
- **Pattern**: Generated root AGENTS.md to serve as a central hub pointing to sub-component guides.
- **Structure**: Monorepo requires clear separation in documentation but unified command reference.
- **Constraints**: Concise (30-50 lines) format forces prioritization of high-level pointers over detailed instructions.
