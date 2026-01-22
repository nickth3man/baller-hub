def setup_schema(con):
    """
    Sets up the DuckDB schema for the Baller Hub ETL process.

    Args:
        con: A duckdb connection object.
    """
    con.execute("""
        CREATE TABLE IF NOT EXISTS dim_players (
            bref_id VARCHAR PRIMARY KEY,
            nba_id VARCHAR,
            name VARCHAR,
            birth_date DATE
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS dim_teams (
            bref_id VARCHAR PRIMARY KEY,
            nba_id VARCHAR,
            abbreviation VARCHAR
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS bridge_ids (
            bref_id VARCHAR,
            nba_id VARCHAR,
            name VARCHAR,
            birth_date DATE,
            PRIMARY KEY (bref_id, nba_id)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS fact_player_gamelogs (
            player_id VARCHAR,
            team_id VARCHAR,
            game_id VARCHAR,
            date DATE,
            minutes_played VARCHAR,
            made_field_goals INTEGER,
            attempted_field_goals INTEGER,
            made_three_point_field_goals INTEGER,
            attempted_three_point_field_goals INTEGER,
            made_free_throws INTEGER,
            attempted_free_throws INTEGER,
            offensive_rebounds INTEGER,
            defensive_rebounds INTEGER,
            assists INTEGER,
            steals INTEGER,
            blocks INTEGER,
            turnovers INTEGER,
            personal_fouls INTEGER,
            points INTEGER,
            PRIMARY KEY (player_id, game_id)
        )
    """)
