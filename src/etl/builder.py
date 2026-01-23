import logging
from pathlib import Path

import duckdb

from src.etl import schema
from src.etl.identity import build_identity_bridge
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

    Handles file naming discrepancies (underscore vs space).

    Args:
        con (duckdb.DuckDBPyConnection): The DuckDB connection.
        root (Path): The project root directory path.
    """
    raw_data_dir = root / "raw-data" / "csv"
    if not raw_data_dir.exists():
        raw_data_dir = root / "raw-data"

    logger.info("Loading staging tables from %s...", raw_data_dir)

    for table_name in schema.STAGING_TABLES:
        base_name = table_name.replace("staging_", "")
        file_path_underscore = raw_data_dir / (base_name + ".csv")
        file_path_space = raw_data_dir / (base_name.replace("_", " ") + ".csv")

        file_path = None
        if file_path_underscore.exists():
            file_path = file_path_underscore
        elif file_path_space.exists():
            file_path = file_path_space

        if not file_path:
            logger.warning(
                "Missing source file for %s (checked %s and %s)",
                table_name,
                file_path_underscore.name,
                file_path_space.name,
            )
            continue

        logger.info("Loading %s from %s...", table_name, file_path.name)
        try:
            con.execute(
                f"""
                COPY {table_name}
                FROM '{file_path.as_posix()}'
                (FORMAT CSV, HEADER, DELIMITER ',', QUOTE '"', ESCAPE '"', AUTO_DETECT TRUE, NULL_PADDING TRUE, IGNORE_ERRORS TRUE)
                """
            )
        except Exception as e:
            logger.error("Failed to load %s: %s", table_name, e)


def transform_dims(con: duckdb.DuckDBPyConnection) -> None:
    """
    Transform staging tables into the application's dimensional and fact tables (Legacy Schema).

    Args:
        con (duckdb.DuckDBPyConnection): The DuckDB connection.
    """
    logger.info("Transforming dim_teams (Legacy)...")
    try:
        con.execute("""
            INSERT OR REPLACE INTO dim_teams (bref_id, nba_id, abbreviation)
            SELECT DISTINCT
                team_abbrev,
                team_id,
                team_abbrev
            FROM staging_team_histories
            WHERE team_abbrev IS NOT NULL
        """)
    except Exception as e:
        logger.warning("Skipping dim_teams legacy transform: %s", e)

    logger.info("Transforming dim_players (Legacy)...")
    try:
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
    except Exception as e:
        logger.warning("Skipping dim_players legacy transform: %s", e)

    logger.info("Transforming fact_player_gamelogs (Legacy)...")
    try:
        con.execute("""
            INSERT OR REPLACE INTO fact_player_gamelogs (
                player_id, team_id, game_id, date, minutes_played, points, assists, rebounds_total
            )
            SELECT
                dp.bref_id,
                sps.playerteam_name,
                sps.game_id,
                TRY_CAST(sps.game_date_time_est AS DATE),
                TRY_CAST(sps.num_minutes AS INTEGER),
                TRY_CAST(sps.points AS INTEGER),
                TRY_CAST(sps.assists AS INTEGER),
                TRY_CAST(sps.rebounds_total AS INTEGER)
            FROM staging_player_statistics sps
            LEFT JOIN dim_players dp ON sps.person_id = dp.nba_id
        """)
    except Exception as e:
        logger.warning("Skipping fact_player_gamelogs legacy transform: %s", e)


def transform_v2_schema(con: duckdb.DuckDBPyConnection) -> None:
    """
    Transform staging tables into the V2 Schema (Franchises, TeamSeasons, PlayerStats).

    Args:
        con (duckdb.DuckDBPyConnection): The DuckDB connection.
    """
    logger.info("Transforming V2: franchises...")
    con.execute("""
        INSERT INTO franchises (franchise_id, full_name, city, year_founded, is_active)
        SELECT
            abbreviation, 
            MAX(city || ' ' || nickname), 
            MAX(city), 
            MAX(TRY_CAST(yearfounded AS INTEGER)), 
            TRUE
        FROM staging_team_details
        WHERE abbreviation IS NOT NULL
        GROUP BY abbreviation
    """)

    logger.info("Transforming V2: team_seasons...")
    con.execute("""
        INSERT INTO team_seasons (season_id, franchise_id, team_name, abbreviation, arena, arena_capacity)
        SELECT
            CAST(season AS VARCHAR), 
            abbreviation, 
            MAX(team), 
            abbreviation, 
            MAX(arena), 
            MAX(TRY_CAST(attend AS INTEGER))
        FROM staging_team_summaries
        WHERE abbreviation IS NOT NULL
        GROUP BY season, abbreviation
    """)

    logger.info("Transforming V2: team_season_stats...")
    con.execute("""
        INSERT INTO team_season_stats (
            season_id, franchise_id, games_played, wins, losses, win_percentage,
            mov, sos, srs, offensive_rating, defensive_rating, net_rating, pace,
            free_throw_rate, three_point_attempt_rate, true_shooting_percentage,
            effective_fg_percentage, turnover_percentage, offensive_rebound_percentage
        )
        SELECT
            CAST(season AS VARCHAR),
            abbreviation,
            NULL,
            MAX(TRY_CAST(w AS INTEGER)),
            MAX(TRY_CAST(l AS INTEGER)),
            MAX(TRY_CAST(w AS DOUBLE)) / (MAX(TRY_CAST(w AS DOUBLE)) + MAX(TRY_CAST(l AS DOUBLE))),
            MAX(TRY_CAST(mov AS DOUBLE)),
            MAX(TRY_CAST(sos AS DOUBLE)),
            MAX(TRY_CAST(srs AS DOUBLE)),
            MAX(TRY_CAST(o_rtg AS DOUBLE)),
            MAX(TRY_CAST(d_rtg AS DOUBLE)),
            MAX(TRY_CAST(n_rtg AS DOUBLE)),
            MAX(TRY_CAST(pace AS DOUBLE)),
            MAX(TRY_CAST(f_tr AS DOUBLE)),
            MAX(TRY_CAST(x3p_ar AS DOUBLE)),
            MAX(TRY_CAST(ts_percent AS DOUBLE)),
            MAX(TRY_CAST(e_fg_percent AS DOUBLE)),
            MAX(TRY_CAST(tov_percent AS DOUBLE)),
            MAX(TRY_CAST(orb_percent AS DOUBLE))
        FROM staging_team_summaries
        WHERE abbreviation IS NOT NULL
        GROUP BY season, abbreviation
    """)

    logger.info("Transforming V2: players...")
    con.execute("""
        INSERT INTO players (person_id, player_slug, first_name, last_name, birth_date, is_hof)
        SELECT DISTINCT
            b.nba_id,
            b.bref_id,
            split_part(b.name, ' ', 1),
            split_part(b.name, ' ', 2),
            b.birth_date,
            CASE WHEN pci.hof = 'TRUE' THEN TRUE ELSE FALSE END
        FROM bridge_ids b
        LEFT JOIN staging_player_career_info pci ON b.bref_id = pci.player_id
        WHERE b.nba_id IS NOT NULL AND b.bref_id IS NOT NULL
    """)

    logger.info("Transforming V2: player_season_stats...")
    con.execute("""
        INSERT INTO player_season_stats (
            player_id, season_id, franchise_id, team_abbrev, games_played, games_started, minutes_played,
            points, total_rebounds, assists, steals, blocks, turnovers, personal_fouls,
            field_goals_made, field_goals_attempted, three_pointers_made, three_pointers_attempted,
            two_pointers_made, two_pointers_attempted, free_throws_made, free_throws_attempted
        )
        SELECT
            p.person_id,
            CAST(st.season AS VARCHAR),
            NULL,
            st.team,
            TRY_CAST(st.g AS INTEGER),
            TRY_CAST(st.gs AS INTEGER),
            TRY_CAST(st.mp AS INTEGER),
            TRY_CAST(st.pts AS INTEGER),
            TRY_CAST(st.trb AS INTEGER),
            TRY_CAST(st.ast AS INTEGER),
            TRY_CAST(st.stl AS INTEGER),
            TRY_CAST(st.blk AS INTEGER),
            TRY_CAST(st.tov AS INTEGER),
            TRY_CAST(st.pf AS INTEGER),
            TRY_CAST(st.fg AS INTEGER),
            TRY_CAST(st.fga AS INTEGER),
            TRY_CAST(st.x3p AS INTEGER),
            TRY_CAST(st.x3pa AS INTEGER),
            TRY_CAST(st.x2p AS INTEGER),
            TRY_CAST(st.x2pa AS INTEGER),
            TRY_CAST(st.ft AS INTEGER),
            TRY_CAST(st.fta AS INTEGER)
        FROM staging_player_totals st
        JOIN players p ON st.player_id = p.player_slug
    """)

    logger.info("Transforming V2: player_season_advanced...")
    con.execute("""
        INSERT INTO player_season_advanced (
            player_id, season_id, franchise_id, per, true_shooting_percentage, three_point_attempt_rate,
            free_throw_rate, offensive_rebound_percentage, defensive_rebound_percentage,
            total_rebound_percentage, assist_percentage, steal_percentage, block_percentage,
            turnover_percentage, usage_percentage, offensive_win_shares, defensive_win_shares,
            win_shares, win_shares_per_48, offensive_box_plus_minus, defensive_box_plus_minus,
            box_plus_minus, vorp
        )
        SELECT
            p.person_id,
            CAST(st.season AS VARCHAR),
            NULL,
            TRY_CAST(st.per AS DOUBLE),
            TRY_CAST(st.ts_percent AS DOUBLE),
            TRY_CAST(st.x3p_ar AS DOUBLE),
            TRY_CAST(st.f_tr AS DOUBLE),
            TRY_CAST(st.orb_percent AS DOUBLE),
            TRY_CAST(st.drb_percent AS DOUBLE),
            TRY_CAST(st.trb_percent AS DOUBLE),
            TRY_CAST(st.ast_percent AS DOUBLE),
            TRY_CAST(st.stl_percent AS DOUBLE),
            TRY_CAST(st.blk_percent AS DOUBLE),
            TRY_CAST(st.tov_percent AS DOUBLE),
            TRY_CAST(st.usg_percent AS DOUBLE),
            TRY_CAST(st.ows AS DOUBLE),
            TRY_CAST(st.dws AS DOUBLE),
            TRY_CAST(st.ws AS DOUBLE),
            TRY_CAST(st.ws_48 AS DOUBLE),
            TRY_CAST(st.obpm AS DOUBLE),
            TRY_CAST(st.dbpm AS DOUBLE),
            TRY_CAST(st.bpm AS DOUBLE),
            TRY_CAST(st.vorp AS DOUBLE)
        FROM staging_advanced st
        JOIN players p ON st.player_id = p.player_slug
    """)

    logger.info("Transforming V2: player_season_shooting...")
    con.execute("""
        INSERT INTO player_season_shooting (
            player_id, season_id, franchise_id, avg_dist_fga, percent_fga_2p, percent_fga_0_3,
            percent_fga_3_10, percent_fga_10_16, percent_fga_16_3p, percent_fga_3p,
            fg_percent_2p, fg_percent_0_3, fg_percent_3_10, fg_percent_10_16,
            fg_percent_16_3p, fg_percent_3p, percent_assisted_2p, percent_assisted_3p,
            percent_dunks_of_fga, num_dunks, percent_corner_3s_of_3pa, corner_3_point_percent,
            num_heaves_attempted, num_heaves_made
        )
        SELECT
            p.person_id,
            CAST(st.season AS VARCHAR),
            NULL,
            TRY_CAST(st.avg_dist_fga AS DOUBLE),
            TRY_CAST(st.percent_fga_from_x2p_range AS DOUBLE),
            TRY_CAST(st.percent_fga_from_x0_3_range AS DOUBLE),
            TRY_CAST(st.percent_fga_from_x3_10_range AS DOUBLE),
            TRY_CAST(st.percent_fga_from_x10_16_range AS DOUBLE),
            TRY_CAST(st.percent_fga_from_x16_3p_range AS DOUBLE),
            TRY_CAST(st.percent_fga_from_x3p_range AS DOUBLE),
            TRY_CAST(st.fg_percent_from_x2p_range AS DOUBLE),
            TRY_CAST(st.fg_percent_from_x0_3_range AS DOUBLE),
            TRY_CAST(st.fg_percent_from_x3_10_range AS DOUBLE),
            TRY_CAST(st.fg_percent_from_x10_16_range AS DOUBLE),
            TRY_CAST(st.fg_percent_from_x16_3p_range AS DOUBLE),
            TRY_CAST(st.fg_percent_from_x3p_range AS DOUBLE),
            TRY_CAST(st.percent_assisted_x2p_fg AS DOUBLE),
            TRY_CAST(st.percent_assisted_x3p_fg AS DOUBLE),
            TRY_CAST(st.percent_dunks_of_fga AS DOUBLE),
            TRY_CAST(st.num_of_dunks AS INTEGER),
            TRY_CAST(st.percent_corner_3s_of_3pa AS DOUBLE),
            TRY_CAST(st.corner_3_point_percent AS DOUBLE),
            TRY_CAST(st.num_heaves_attempted AS INTEGER),
            TRY_CAST(st.num_heaves_made AS INTEGER)
        FROM staging_player_shooting st
        JOIN players p ON st.player_id = p.player_slug
    """)

    logger.info("Transforming V2: player_season_play_by_play...")
    con.execute("""
        INSERT INTO player_season_play_by_play (
            player_id, season_id, franchise_id, pg_percent, sg_percent, sf_percent, pf_percent, c_percent,
            on_court_plus_minus_per_100, net_plus_minus_per_100, bad_pass_turnovers, lost_ball_turnovers,
            shooting_fouls_committed, offensive_fouls_committed, shooting_fouls_drawn, offensive_fouls_drawn,
            points_generated_by_assists, and1s, fga_blocked
        )
        SELECT
            p.person_id,
            CAST(st.season AS VARCHAR),
            NULL,
            TRY_CAST(st.pg_percent AS INTEGER),
            TRY_CAST(st.sg_percent AS INTEGER),
            TRY_CAST(st.sf_percent AS INTEGER),
            TRY_CAST(st.pf_percent AS INTEGER),
            TRY_CAST(st.c_percent AS INTEGER),
            TRY_CAST(st.on_court_plus_minus_per_100_poss AS DOUBLE),
            TRY_CAST(st.net_plus_minus_per_100_poss AS DOUBLE),
            TRY_CAST(st.bad_pass_turnover AS INTEGER),
            TRY_CAST(st.lost_ball_turnover AS INTEGER),
            TRY_CAST(st.shooting_foul_committed AS INTEGER),
            TRY_CAST(st.offensive_foul_committed AS INTEGER),
            TRY_CAST(st.shooting_foul_drawn AS INTEGER),
            TRY_CAST(st.offensive_foul_drawn AS INTEGER),
            TRY_CAST(st.points_generated_by_assists AS INTEGER),
            TRY_CAST(st.and1 AS INTEGER),
            TRY_CAST(st.fga_blocked AS INTEGER)
        FROM staging_player_play_by_play st
        JOIN players p ON st.player_id = p.player_slug
    """)

    logger.info("Transforming V2: games...")
    con.execute("""
        INSERT OR IGNORE INTO games (game_id, season_id, game_date, home_franchise_id, away_franchise_id, home_score, away_score, attendance, arena_id)
        SELECT DISTINCT
            sg.game_id,
            CASE 
                WHEN month(TRY_CAST(sg.game_date_time_est AS DATE)) >= 10 THEN CAST(year(TRY_CAST(sg.game_date_time_est AS DATE)) AS VARCHAR) || '-' || CAST(year(TRY_CAST(sg.game_date_time_est AS DATE)) + 1 AS VARCHAR)
                ELSE CAST(year(TRY_CAST(sg.game_date_time_est AS DATE)) - 1 AS VARCHAR) || '-' || CAST(year(TRY_CAST(sg.game_date_time_est AS DATE)) AS VARCHAR)
            END,
            TRY_CAST(sg.game_date_time_est AS DATE),
            th.abbreviation,
            ta.abbreviation,
            TRY_CAST(sg.home_score AS INTEGER),
            TRY_CAST(sg.away_score AS INTEGER),
            TRY_CAST(sg.attendance AS INTEGER),
            sg.arena_id
        FROM staging_games sg
        LEFT JOIN staging_team_details th ON CAST(sg.hometeam_id AS VARCHAR) = CAST(th.team_id AS VARCHAR)
        LEFT JOIN staging_team_details ta ON CAST(sg.awayteam_id AS VARCHAR) = CAST(ta.team_id AS VARCHAR)
    """)

    logger.info("Transforming V2: player_game_stats...")
    con.execute("""
        INSERT OR IGNORE INTO player_game_stats (
            player_id, game_id, franchise_id, minutes_played,
            pts, ast, reb, blk, stl, tov,
            fgm, fga, fg3m, fg3a, ftm, fta,
            plus_minus
        )
        SELECT DISTINCT
            CAST(sps.person_id AS VARCHAR),
            sps.game_id,
            sps.playerteam_name, -- Assuming this is abbreviation (e.g. LAL)
            TRY_CAST(sps.num_minutes AS DOUBLE),
            TRY_CAST(sps.points AS INTEGER),
            TRY_CAST(sps.assists AS INTEGER),
            TRY_CAST(sps.rebounds_total AS INTEGER),
            TRY_CAST(sps.blocks AS INTEGER),
            TRY_CAST(sps.steals AS INTEGER),
            TRY_CAST(sps.turnovers AS INTEGER),
            TRY_CAST(sps.field_goals_made AS INTEGER),
            TRY_CAST(sps.field_goals_attempted AS INTEGER),
            TRY_CAST(sps.three_pointers_made AS INTEGER),
            TRY_CAST(sps.three_pointers_attempted AS INTEGER),
            TRY_CAST(sps.free_throws_made AS INTEGER),
            TRY_CAST(sps.free_throws_attempted AS INTEGER),
            TRY_CAST(sps.plus_minus_points AS INTEGER)
        FROM staging_playerstatistics sps
        WHERE sps.person_id IS NOT NULL
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

        logger.info("Building identity bridge...")
        build_identity_bridge(con)

        transform_dims(con)
        transform_v2_schema(con)

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
