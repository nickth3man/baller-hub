import logging
from pathlib import Path

import duckdb

from src.etl import schema

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def find_project_root() -> Path:
    """Finds the project root directory by looking for raw-data or .git."""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "raw-data").exists() or (parent / ".git").exists():
            return parent
    msg = "Could not find project root (raw-data or .git not found)"
    raise FileNotFoundError(msg)


def build():
    """Orchestrates the DuckDB creation process."""
    try:
        root = find_project_root()
    except FileNotFoundError:
        logger.exception("Failed to locate project root")
        return

    webapp_dir = root / "src" / "webapp"
    webapp_dir.mkdir(parents=True, exist_ok=True)

    target_db_path = webapp_dir / "baller.duckdb"
    tmp_db_path = webapp_dir / "baller.duckdb.tmp"

    logger.info("Project root: %s", root)
    logger.info("Target DB: %s", target_db_path)
    logger.info("Temp DB: %s", tmp_db_path)

    if tmp_db_path.exists():
        logger.info("Cleaning up existing temp DB: %s", tmp_db_path)
        tmp_db_path.unlink()

    logger.info("Connecting to temp DB...")
    con = duckdb.connect(str(tmp_db_path))

    try:
        logger.info("Setting up schema...")
        schema.setup_schema(con)
        logger.info("Schema initialized.")

    except Exception:
        logger.exception("Build failed")
        con.close()
        if tmp_db_path.exists():
            tmp_db_path.unlink()
        raise

    con.close()

    logger.info("Would swap files now (baller.duckdb.tmp -> baller.duckdb)")
    logger.info("Build successful.")


if __name__ == "__main__":
    build()
