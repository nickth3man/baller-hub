import logging
import os
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


def load_staging(con: duckdb.DuckDBPyConnection, root: Path) -> None:
    """Loads raw CSV data into staging tables."""
    raw_data_dir = root / "raw-data"
    logger.info("Loading staging tables from %s...", raw_data_dir)

    for table_name in schema.STAGING_TABLES:
        # Map staging_players -> players.csv
        file_name = table_name.replace("staging_", "") + ".csv"
        file_path = raw_data_dir / file_name

        if not file_path.exists():
            logger.warning("Missing source file: %s", file_path)
            continue

        logger.info("Loading %s from %s...", table_name, file_name)
        # Use strict COPY command
        # Quote path to handle spaces if necessary, though pathlib handles it well
        con.execute(f"COPY {table_name} FROM '{file_path.as_posix()}'")


def transform_dims(con: duckdb.DuckDBPyConnection) -> None:
    """Transforms staging data into dimensional tables."""
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
    # Clean/normalize text and generate slugs matches legacy logic
    # We strip special chars to ensure clean slugs (e.g. O'Neal -> oneal)
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
    # Join with dim_players to get the generated slug (bref_id)
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
            sps.num_minutes,
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

        logger.info("Loading staging data...")
        load_staging(con, root)

        logger.info("Transforming dimensions and facts...")
        transform_dims(con)

        logger.info("Build complete. Verifying tables...")
        tables = con.execute("SHOW TABLES").fetchall()
        logger.info("Tables created: %s", [t[0] for t in tables])

    except Exception:
        logger.exception("Build failed")
        con.close()
        if tmp_db_path.exists():
            tmp_db_path.unlink()
        raise

    con.close()

    logger.info("Performing atomic swap...")

    # Atomic swap logic with Windows safety
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
            # If we can't rename, we might fail the next step, or we can try to delete
            try:
                target_db_path.unlink()
            except OSError:
                logger.error("Could not delete target DB. Aborting swap.")
                raise

    try:
        tmp_db_path.rename(target_db_path)
        logger.info("Swap successful. New DB is live at %s", target_db_path)
    except OSError:
        logger.error("Failed to rename temp DB to target DB")
        raise

    # Cleanup backup
    backup_path = target_db_path.with_suffix(".duckdb.bak")
    if backup_path.exists():
        try:
            backup_path.unlink()
        except OSError:
            logger.warning("Could not clean up backup file: %s", backup_path)


if __name__ == "__main__":
    build()
