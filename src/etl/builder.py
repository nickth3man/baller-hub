import logging
from pathlib import Path

import duckdb

from src.etl import schema
from src.etl.validate import validate_etl

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def find_project_root() -> Path:
    """
    Locate the project root directory by searching this file's directory and its ancestors for a `raw-data` directory or a `.git` directory.

    Returns:
        Path: Path to the discovered project root directory.

    Raises:
        FileNotFoundError: If no ancestor contains a `raw-data` directory or a `.git` directory.
    """
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "raw-data").exists() or (parent / ".git").exists():
            return parent
    msg = "Could not find project root (raw-data or .git not found)"
    raise FileNotFoundError(msg)


def load_staging(con: duckdb.DuckDBPyConnection, root: Path) -> None:
    """
    Load raw CSV files from the project's raw-data directory into DuckDB staging tables.

    For each table name in schema.STAGING_TABLES, expects a CSV file named by removing the
    "staging_" prefix and appending ".csv" (for example, "staging_players" -> "players.csv")
    located under root / "raw-data". Missing source files are skipped and a warning is logged.

    Parameters:
        con (duckdb.DuckDBPyConnection): Open DuckDB connection to execute COPY commands.
        root (Path): Project root directory containing the "raw-data" directory.
    """
    raw_data_dir = root / "raw-data"
    logger.info("Loading staging tables from %s...", raw_data_dir)

    for table_name in schema.STAGING_TABLES:
        # Map table name to filename (e.g., staging_players -> players.csv)
        file_name = table_name.replace("staging_", "") + ".csv"
        file_path = raw_data_dir / file_name

        if not file_path.exists():
            logger.warning("Missing source file: %s", file_path)
            continue

        logger.info("Loading %s from %s...", table_name, file_name)
        con.execute(
            f"""
            COPY {table_name}
            FROM '{file_path.as_posix()}'
            (FORMAT CSV, HEADER, DELIMITER ',', QUOTE '"', ESCAPE '"', AUTO_DETECT TRUE)
            """
        )


def transform_dims(con: duckdb.DuckDBPyConnection) -> None:
    """
    Transform staging tables into the application's dimensional and fact tables.

    Populates dim_teams from staging_team_histories; populates dim_players from staging_players while generating legacy-format player slugs; and populates fact_player_gamelogs from staging_player_statistics, applying safe casts for dates and numeric fields. Inserts use "INSERT OR REPLACE" semantics to update existing rows.
    """
    logger.info("Transforming dim_teams...")
    con.execute("""
        INSERT OR REPLACE INTO dim_teams (bref_id, nba_id, abbreviation)
        SELECT DISTINCT
            team_abbrev,
            team_id,
            team_abbrev
        FROM staging_team_histories
        WHERE team_abbrev IS NOT NULL
    """)

    logger.info("Transforming dim_players (generating slugs)...")
    # Generate slugs matching legacy logic: first 5 chars of last name + first 2 of first name + count
    con.execute("""
        WITH player_source AS (
            SELECT
                person_id,
                first_name,
                last_name,
                birthdate,
                lower(regexp_replace(last_name, '[^a-zA-Z0-9]', '', 'g')) as last_name_clean,
                lower(regexp_replace(first_name, '[^a-zA-Z0-9]', '', 'g')) as first_name_clean
            FROM staging_players
        ),
        player_slugs AS (
            SELECT
                person_id,
                first_name,
                last_name,
                birthdate,
                substring(last_name_clean, 1, 5)
                    || substring(first_name_clean, 1, 2)
                    || lpad(
                        row_number() OVER (
                            PARTITION BY
                                substring(last_name_clean, 1, 5),
                                substring(first_name_clean, 1, 2)
                            ORDER BY person_id
                        )::text,
                        2,
                        '0'
                    ) AS slug
            FROM player_source
        )
        INSERT OR REPLACE INTO dim_players (bref_id, nba_id, name, birth_date)
        SELECT
            slug,
            person_id,
            first_name || ' ' || last_name,
            TRY_CAST(birthdate AS DATE)
        FROM player_slugs
    """)

    logger.info("Transforming fact_player_gamelogs...")
    con.execute("""
        INSERT OR REPLACE INTO fact_player_gamelogs (
            player_id,
            team_id,
            game_id,
            date,
            minutes_played,
            made_field_goals,
            attempted_field_goals,
            made_three_point_field_goals,
            attempted_three_point_field_goals,
            made_free_throws,
            attempted_free_throws,
            offensive_rebounds,
            defensive_rebounds,
            assists,
            steals,
            blocks,
            turnovers,
            personal_fouls,
            points
        )
        SELECT
            dp.bref_id,
            sps.playerteam_name,
            sps.game_id,
            TRY_CAST(sps.game_date_time_est AS DATE),
            TRY_CAST(sps.num_minutes AS INTEGER),
            TRY_CAST(sps.field_goals_made AS INTEGER),

            TRY_CAST(sps.field_goals_attempted AS INTEGER),
            TRY_CAST(sps.three_pointers_made AS INTEGER),
            TRY_CAST(sps.three_pointers_attempted AS INTEGER),
            TRY_CAST(sps.free_throws_made AS INTEGER),
            TRY_CAST(sps.free_throws_attempted AS INTEGER),
            TRY_CAST(sps.rebounds_offensive AS INTEGER),
            TRY_CAST(sps.rebounds_defensive AS INTEGER),
            TRY_CAST(sps.assists AS INTEGER),
            TRY_CAST(sps.steals AS INTEGER),
            TRY_CAST(sps.blocks AS INTEGER),
            TRY_CAST(sps.turnovers AS INTEGER),
            TRY_CAST(sps.fouls_personal AS INTEGER),
            TRY_CAST(sps.points AS INTEGER)
        FROM staging_player_statistics sps
        LEFT JOIN dim_players dp ON sps.person_id = dp.nba_id
    """)


def perform_atomic_swap(target_db_path: Path, tmp_db_path: Path) -> None:
    """
    Perform an atomic swap of a temporary DuckDB file into the target location, preserving a backup.

    This moves the existing target file to a backup with the suffix ".duckdb.bak" (removing any prior backup), then renames the temporary database into the target path. After a successful swap the backup is removed when possible.

    Parameters:
        target_db_path (Path): Filesystem path of the live DuckDB to be replaced.
        tmp_db_path (Path): Filesystem path of the newly built temporary DuckDB to promote.

    Raises:
        OSError: If filesystem operations (rename or delete) fail and prevent completing the swap.
    """
    logger.info("Performing atomic swap...")

    if target_db_path.exists():
        backup_path = target_db_path.with_suffix(".duckdb.bak")
        if backup_path.exists():
            try:
                backup_path.unlink()
            except OSError:
                logger.warning("Could not remove old backup: %s", backup_path)

        try:
            target_db_path.rename(backup_path)
        except OSError:
            logger.warning("Could not rename target to backup (file locking?)")
            try:
                target_db_path.unlink()
            except OSError:
                logger.exception("Could not delete target DB. Aborting swap.")
                raise

    try:
        tmp_db_path.rename(target_db_path)
        logger.info("Swap successful. New DB is live at %s", target_db_path)
    except OSError:
        logger.exception("Failed to rename temp DB to target DB")
        raise

    # Cleanup backup
    backup_path = target_db_path.with_suffix(".duckdb.bak")
    if backup_path.exists():
        try:
            backup_path.unlink()
        except OSError:
            logger.warning("Could not clean up backup file: %s", backup_path)


def build() -> None:
    """
    Builds a DuckDB database from raw data and atomically installs it into the webapp.

    Performs the end-to-end ETL: locates the project root, ensures the webapp directory exists, creates a temporary DuckDB, loads raw CSVs into staging tables, transforms staging data into dimensional and fact tables, runs validation, and on success atomically swaps the temporary database into the target location (with backup handling). If the project root cannot be found the build aborts; on build failure the temporary database is preserved for inspection.
    """
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

        load_staging(con, root)
        transform_dims(con)

        logger.info("Running validation...")
        validate_etl(con)

        logger.info("Build complete. Verifying tables...")
        tables = con.execute("SHOW TABLES").fetchall()
        logger.info("Tables created: %s", [t[0] for t in tables])

    except Exception:
        logger.exception("Build failed")
        con.close()
        logger.warning("Build failed. Keeping temp DB for inspection: %s", tmp_db_path)
        raise

    con.close()
    perform_atomic_swap(target_db_path, tmp_db_path)


if __name__ == "__main__":
    build()
