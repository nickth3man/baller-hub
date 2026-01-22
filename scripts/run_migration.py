import sys
import duckdb
from src.etl.schema import setup_schema
from src.etl.identity import build_identity_bridge
from src.etl.loader import load_dims, load_facts
from src.etl.validate import validate_etl


def run_migration():
    db_path = "baller.duckdb"
    con = None
    try:
        print(f"Connecting to DuckDB at {db_path}...")
        con = duckdb.connect(db_path)

        print("Step 1: Setting up schema...")
        setup_schema(con)

        print("Step 2: Building identity bridge...")
        build_identity_bridge(con)

        print("Step 3: Loading dimensions...")
        load_dims(con)

        print("Step 4: Loading facts...")
        load_facts(con)

        print("Step 5: Validating ETL pipeline...")
        validate_etl(con)

        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)
    finally:
        if con:
            print("Closing database connection.")
            con.close()


if __name__ == "__main__":
    run_migration()
