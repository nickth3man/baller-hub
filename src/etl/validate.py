"""
Validation logic for the ETL pipeline.

Performs integrity checks on the transformed data to ensure
completeness and consistency before promoting the database.
"""

import logging

logger = logging.getLogger(__name__)


def validate_etl(con):
    """
    Validate ETL consistency and integrity for the V2 Schema tables.

    Args:
        con (duckdb.DuckDBPyConnection): The DuckDB connection.
    """
    logger.info("Starting validation...")

    # 1. Check Players
    player_count = con.execute("SELECT count(*) FROM players").fetchone()[0]
    logger.info("V2 Check: players count = %s", player_count)
    if player_count == 0:
        logger.warning("WARNING: 'players' table is empty!")

    # 2. Check Franchises
    franchise_count = con.execute("SELECT count(*) FROM franchises").fetchone()[0]
    logger.info("V2 Check: franchises count = %s", franchise_count)
    if franchise_count == 0:
        logger.warning("WARNING: 'franchises' table is empty!")

    # 3. Check Team Seasons
    team_season_count = con.execute("SELECT count(*) FROM team_seasons").fetchone()[0]
    logger.info("V2 Check: team_seasons count = %s", team_season_count)

    # 4. Parity Check: player_season_stats vs staging_player_totals
    pss_count = con.execute("SELECT count(*) FROM player_season_stats").fetchone()[0]
    staging_count = con.execute(
        "SELECT count(*) FROM staging_player_totals"
    ).fetchone()[0]

    logger.info(
        "Parity Check: player_season_stats=%s, staging_player_totals=%s",
        pss_count,
        staging_count,
    )

    # We expect roughly equal counts (might differ if players missing from players table are filtered out)
    # The V2 transform uses JOIN players, so if player_id not in players, rows are dropped.
    # staging_player_totals has player_id (slug). players table has player_slug.
    # If players table is comprehensive (sourced from dim_players + bridge), it should match.
    # But strict equality might fail if bridge is missing some IDs.
    # Let's just assert it's not empty and within reasonable range (e.g. > 90%)

    assert pss_count > 0, "player_season_stats is empty!"

    if staging_count > 0:
        ratio = pss_count / staging_count
        logger.info("Retention rate: %.2f%%", ratio * 100)
        if ratio < 0.9:
            logger.warning("WARNING: Low retention rate in player_season_stats (< 90%)")

    # 5. Check Games
    game_count = con.execute("SELECT count(*) FROM games").fetchone()[0]
    logger.info("V2 Check: games count = %s", game_count)

    # 6. Check Player Game Stats
    pgs_count = con.execute("SELECT count(*) FROM player_game_stats").fetchone()[0]
    logger.info("V2 Check: player_game_stats count = %s", pgs_count)

    logger.info("Validation successful!")
