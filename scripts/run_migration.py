import logging
import os
import sys
import time
from datetime import datetime

# Fix path to allow importing src from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import duckdb

try:
    from src.etl.identity import build_identity_bridge
    from src.etl.loader import load_dims, load_facts
    from src.etl.schema import setup_schema
    from src.etl.validate import validate_etl
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import project modules: {e}")
    sys.exit(1)


def setup_logging():
    # Create logs directory in project root
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"migration_{timestamp}.log")

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
    db_path = "baller.duckdb"
    con = None
    start_time = time.time()

    logger.info("🚀 Starting migration process")
    logger.info(f"📂 Log file: {os.path.abspath(log_file)}")
    logger.debug(f"Python executable: {sys.executable}")
    logger.debug(f"Current working directory: {os.getcwd()}")

    try:
        if os.path.exists(db_path):
            logger.warning(
                f"Database file {db_path} already exists. It will be updated."
            )

        logger.info(f"🔌 Connecting to DuckDB at {db_path}...")
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
        # Capture stdout from validate_etl to log it
        from io import StringIO

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        try:
            validate_etl(con)
            validation_output = mystdout.getvalue()
            for line in validation_output.splitlines():
                logger.info(f"[VALIDATION] {line}")
        finally:
            sys.stdout = old_stdout

        duration = time.time() - start_time
        logger.info(f"🎉 Migration completed successfully in {duration:.2f} seconds!")

    except Exception as e:
        logger.exception(f"❌ Error during migration: {e}")
        sys.exit(1)
    finally:
        if con:
            logger.debug("Closing database connection.")
            con.close()
            logger.info("Connection closed.")


if __name__ == "__main__":
    run_migration()
