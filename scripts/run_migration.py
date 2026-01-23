import logging
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

# Fix path to allow importing src from project root
sys.path.append(str(Path(__file__).resolve().parent.parent))

import duckdb

try:
    from src.etl.identity import build_identity_bridge
    from src.etl.loader import load_dims, load_facts
    from src.etl.schema import setup_schema
    from src.etl.validate import validate_etl
except ImportError as e:
    # We use basic print here because logger isn't setup yet and this is critical
    sys.stderr.write(f"CRITICAL ERROR: Could not import project modules: {e}\n")
    sys.exit(1)


def setup_logging():
    # Create logs directory in project root
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"migration_{timestamp}.log"

    # Configure logging
    logger = logging.getLogger("migration")
    logger.setLevel(logging.DEBUG)

    # File handler - Very verbose
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # Console handler - Info level for visibility
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger, log_file


def run_migration():
    logger, log_file = setup_logging()
    logger.warning("=" * 60)
    logger.warning("DEPRECATED: This script is deprecated.")
    logger.warning("Please use 'src/etl/builder.py' for the unified ETL pipeline.")
    logger.warning("This script targets the legacy root 'baller.duckdb' path.")
    logger.warning("=" * 60)

    db_path = "baller.duckdb"
    con = None
    start_time = time.time()

    logger.info("🚀 Starting migration process")
    logger.info("📂 Log file: %s", log_file.resolve())
    logger.debug("Python executable: %s", sys.executable)
    logger.debug("Current working directory: %s", Path.cwd())

    try:
        if Path(db_path).exists():
            logger.warning(
                "Database file %s already exists. It will be updated.", db_path
            )

        logger.info("🔌 Connecting to DuckDB at %s...", db_path)
        con = duckdb.connect(db_path)
        logger.debug("Connection established.")

        logger.info("🛠️  Step 1: Setting up schema...")
        setup_schema(con)
        logger.debug("Schema setup completed.")

        logger.info("🌉 Step 2: Building identity bridge...")
        build_identity_bridge(con)
        logger.debug("Identity bridge build completed.")

        logger.info("📦 Step 3: Loading dimensions...")
        load_dims(con)
        logger.debug("Dimensions load completed.")

        logger.info("📊 Step 4: Loading facts...")
        load_facts(con)
        logger.debug("Facts load completed.")

        logger.info("✅ Step 5: Validating ETL pipeline...")
        validate_etl(con)

        duration = time.time() - start_time
        logger.info("🎉 Migration completed successfully in %.2f seconds!", duration)

    except Exception:
        logger.exception("❌ Error during migration")
        sys.exit(1)
    finally:
        if con:
            logger.debug("Closing database connection.")
            con.close()
            logger.info("Connection closed.")


if __name__ == "__main__":
    run_migration()
