"""
Database schema definition and setup.

Defines the structure of staging tables, dimensional tables, fact tables,
and the V2 relational schema (Franchises, Team Seasons, Player Stats).
Includes schema creation (DDL) and view setup.
"""

import duckdb

STAGING_TABLES: dict[str, list[str]] = {
    "staging_players": [
        "person_id",
        "first_name",
        "last_name",
        "birthdate",
        "last_attended",
        "country",
        "height",
        "body_weight",
        "guard",
        "forward",
        "center",
        "draft_year",
        "draft_round",
        "draft_number",
    ],
    "staging_games": [
        "game_id",
        "game_date_time_est",
        "hometeam_city",
        "hometeam_name",
        "hometeam_id",
        "awayteam_city",
        "awayteam_name",
        "awayteam_id",
        "home_score",
        "away_score",
        "winner",
        "game_type",
        "attendance",
        "arena_id",
        "game_label",
        "game_sub_label",
        "series_game_number",
    ],
    "staging_team_details": [
        "team_id",
        "abbreviation",
        "nickname",
        "yearfounded",
        "city",
        "arena",
        "arenacapacity",
        "owner",
        "generalmanager",
        "headcoach",
        "dleagueaffiliation",
        "facebook",
        "instagram",
        "twitter",
    ],
    "staging_team_abbrev": [
        "season",
        "lg",
        "team",
        "abbreviation",
        "playoffs",
    ],
    "staging_player_career_info": [
        "player",
        "player_id",
        "pos",
        "ht_in_in",
        "wt",
        "birth_date",
        "colleges",
        "from_year",
        "to_year",
        "debut",
        "hof",
    ],
    "staging_playerstatistics": [
        "first_name",
        "last_name",
        "person_id",
        "game_id",
        "game_date_time_est",
        "playerteam_city",
        "playerteam_name",
        "opponentteam_city",
        "opponentteam_name",
        "game_type",
        "game_label",
        "game_sub_label",
        "series_game_number",
        "win",
        "home",
        "num_minutes",
        "points",
        "assists",
        "blocks",
        "steals",
        "field_goals_attempted",
        "field_goals_made",
        "field_goals_percentage",
        "three_pointers_attempted",
        "three_pointers_made",
        "three_pointers_percentage",
        "free_throws_attempted",
        "free_throws_made",
        "free_throws_percentage",
        "rebounds_defensive",
        "rebounds_offensive",
        "rebounds_total",
        "fouls_personal",
        "turnovers",
        "plus_minus_points",
    ],
    "staging_team_statistics": [
        "game_id",
        "game_date_time_est",
        "team_city",
        "team_name",
        "team_id",
        "opponent_team_city",
        "opponent_team_name",
        "opponent_team_id",
        "home",
        "win",
        "team_score",
        "opponent_score",
        "assists",
        "blocks",
        "steals",
        "field_goals_attempted",
        "field_goals_made",
        "field_goals_percentage",
        "three_pointers_attempted",
        "three_pointers_made",
        "three_pointers_percentage",
        "free_throws_attempted",
        "free_throws_made",
        "free_throws_percentage",
        "rebounds_defensive",
        "rebounds_offensive",
        "rebounds_total",
        "fouls_personal",
        "turnovers",
        "plus_minus_points",
        "num_minutes",
        "q1_points",
        "q2_points",
        "q3_points",
        "q4_points",
        "bench_points",
        "biggest_lead",
        "biggest_scoring_run",
        "lead_changes",
        "points_fast_break",
        "points_from_turnovers",
        "points_in_the_paint",
        "points_second_chance",
        "times_tied",
        "timeouts_remaining",
        "season_wins",
        "season_losses",
        "coach_id",
    ],
    "staging_player_totals": [
        "season",
        "lg",
        "player",
        "player_id",
        "age",
        "team",
        "pos",
        "g",
        "gs",
        "mp",
        "fg",
        "fga",
        "fg_percent",
        "x3p",
        "x3pa",
        "x3p_percent",
        "x2p",
        "x2pa",
        "x2p_percent",
        "e_fg_percent",
        "ft",
        "fta",
        "ft_percent",
        "orb",
        "drb",
        "trb",
        "ast",
        "stl",
        "blk",
        "tov",
        "pf",
        "pts",
        "trp_dbl",
    ],
    "staging_advanced": [
        "season",
        "lg",
        "player",
        "player_id",
        "age",
        "team",
        "pos",
        "g",
        "gs",
        "mp",
        "per",
        "ts_percent",
        "x3p_ar",
        "f_tr",
        "orb_percent",
        "drb_percent",
        "trb_percent",
        "ast_percent",
        "stl_percent",
        "blk_percent",
        "tov_percent",
        "usg_percent",
        "ows",
        "dws",
        "ws",
        "ws_48",
        "obpm",
        "dbpm",
        "bpm",
        "vorp",
    ],
    "staging_player_shooting": [
        "season",
        "lg",
        "player",
        "player_id",
        "age",
        "team",
        "pos",
        "g",
        "gs",
        "mp",
        "fg_percent",
        "avg_dist_fga",
        "percent_fga_from_x2p_range",
        "percent_fga_from_x0_3_range",
        "percent_fga_from_x3_10_range",
        "percent_fga_from_x10_16_range",
        "percent_fga_from_x16_3p_range",
        "percent_fga_from_x3p_range",
        "fg_percent_from_x2p_range",
        "fg_percent_from_x0_3_range",
        "fg_percent_from_x3_10_range",
        "fg_percent_from_x10_16_range",
        "fg_percent_from_x16_3p_range",
        "fg_percent_from_x3p_range",
        "percent_assisted_x2p_fg",
        "percent_assisted_x3p_fg",
        "percent_dunks_of_fga",
        "num_of_dunks",
        "percent_corner_3s_of_3pa",
        "corner_3_point_percent",
        "num_heaves_attempted",
        "num_heaves_made",
    ],
    "staging_player_play_by_play": [
        "season",
        "lg",
        "player",
        "player_id",
        "age",
        "team",
        "pos",
        "g",
        "gs",
        "mp",
        "pg_percent",
        "sg_percent",
        "sf_percent",
        "pf_percent",
        "c_percent",
        "on_court_plus_minus_per_100_poss",
        "net_plus_minus_per_100_poss",
        "bad_pass_turnover",
        "lost_ball_turnover",
        "shooting_foul_committed",
        "offensive_foul_committed",
        "shooting_foul_drawn",
        "offensive_foul_drawn",
        "points_generated_by_assists",
        "and1",
        "fga_blocked",
    ],
    "staging_draft_pick_history": [
        "season",
        "lg",
        "overall_pick",
        "round",
        "tm",
        "player",
        "player_id",
        "college",
    ],
    "staging_all_star_selections": [
        "player",
        "player_id",
        "team",
        "season",
        "lg",
        "replaced",
    ],
    "staging_end_season_teams": [
        "season",
        "lg",
        "type",
        "number_tm",
        "player",
        "player_id",
        "position",
    ],
    "staging_team_totals": [
        "season",
        "lg",
        "team",
        "abbreviation",
        "playoffs",
        "g",
        "mp",
        "fg",
        "fga",
        "fg_percent",
        "x3p",
        "x3pa",
        "x3p_percent",
        "x2p",
        "x2pa",
        "x2p_percent",
        "ft",
        "fta",
        "ft_percent",
        "orb",
        "drb",
        "trb",
        "ast",
        "stl",
        "blk",
        "tov",
        "pf",
        "pts",
    ],
    "staging_team_summaries": [
        "season",
        "lg",
        "team",
        "abbreviation",
        "playoffs",
        "age",
        "w",
        "l",
        "pw",
        "pl",
        "mov",
        "sos",
        "srs",
        "o_rtg",
        "d_rtg",
        "n_rtg",
        "pace",
        "f_tr",
        "x3p_ar",
        "ts_percent",
        "e_fg_percent",
        "tov_percent",
        "orb_percent",
        "ft_fga",
        "opp_e_fg_percent",
        "opp_tov_percent",
        "drb_percent",
        "opp_ft_fga",
        "arena",
        "attend",
        "attend_g",
    ],
    "staging_nba_championships": [
        "season",
        "champion",
    ],
    "staging_nba_players": [
        "player_name",
        "team_abbreviation",
        "age",
        "player_height",
        "player_weight",
        "college",
        "country",
        "draft_year",
        "draft_round",
        "draft_number",
        "gp",
        "pts",
        "reb",
        "ast",
        "net_rating",
        "oreb_pct",
        "dreb_pct",
        "usg_pct",
        "ts_pct",
        "ast_pct",
        "season",
    ],
}


def setup_views(con: duckdb.DuckDBPyConnection) -> None:
    """
    Create SQL views (player, team, season, player_season) that expose the star-schema tables in the shape expected by SQLModel, and create placeholder empty tables for a set of models to prevent runtime errors.

    The views surface data from dim_players, dim_teams, and fact_player_gamelogs into normalized shapes used by downstream code; placeholder tables are created with a single integer `id` column if they do not already exist.

    Args:
        con (duckdb.DuckDBPyConnection): The DuckDB connection.
    """
    con.execute("""
        CREATE OR REPLACE VIEW player AS
        SELECT
            hash(bref_id) AS player_id,
            bref_id AS slug,
            split_part(name, ' ', 1) AS first_name,
            split_part(name, ' ', 2) AS last_name,
            name AS full_name,
            birth_date,
            TRUE AS is_active,
            NULL AS middle_name,
            NULL AS birth_place_city,
            NULL AS birth_place_country,
            NULL AS death_date,
            NULL AS height_inches,
            NULL AS weight_lbs,
            NULL AS position,
            NULL AS high_school,
            NULL AS college,
            NULL AS draft_year,
            NULL AS draft_pick,
            NULL AS debut_date,
            NULL AS final_date,
            NULL AS debut_year,
            NULL AS final_year
        FROM dim_players
    """)

    con.execute("""
        CREATE OR REPLACE VIEW team AS
        SELECT
            hash(bref_id) AS team_id,
            bref_id AS abbreviation,
            bref_id AS name,
            1900 AS founded_year,
            NULL AS defunct_year,
            NULL AS division_id,
            NULL AS franchise_id,
            TRUE AS is_active,
            FALSE AS is_defunct,
            NULL AS city,
            NULL AS arena,
            NULL AS arena_capacity,
            NULL AS relocation_history
        FROM dim_teams
    """)

    con.execute("""
        CREATE OR REPLACE VIEW season AS
        SELECT DISTINCT
            year(date) AS season_id,
            year(date) AS year,
            NULL AS league_id
        FROM fact_player_gamelogs
    """)

    con.execute("""
        CREATE OR REPLACE VIEW player_season AS
        SELECT
            hash(player_id) AS player_id,
            year(date) AS season_id,
            'REGULAR' AS season_type,
            hash(team_id) AS team_id,
            count(*) AS games_played,
            0 AS games_started,
            0 AS minutes_played,
            sum(points) AS points_scored,
            0 AS made_fg,
            0 AS attempted_fg,
            0 AS made_3pt,
            0 AS attempted_3pt,
            0 AS made_ft,
            0 AS attempted_ft,
            0 AS offensive_rebounds,
            0 AS defensive_rebounds,
            0 AS total_rebounds,
            sum(assists) AS assists,
            sum(steals) AS steals,
            sum(blocks) AS blocks,
            sum(turnovers) AS turnovers,
            sum(personal_fouls) AS personal_fouls,
            0 AS double_doubles,
            0 AS triple_doubles,
            FALSE AS is_combined_totals,
            NULL AS player_age,
            NULL AS position
        FROM fact_player_gamelogs
        GROUP BY player_id, year(date), team_id
    """)

    # Create empty tables/views for other models to avoid crashes
    empty_tables = [
        "award",
        "award_recipient",
        "draft",
        "draft_pick",
        "game",
        "box_score",
        "play_by_play",
        "player_box_score",
        "player_season_advanced",
        "player_shooting",
        "franchise",
        "league",
        "conference",
        "division",
    ]
    for table in empty_tables:
        con.execute(f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER)")


def setup_schema(con: duckdb.DuckDBPyConnection) -> None:
    """
    Create the DuckDB schema, staging tables, and supporting views required by the Baller Hub ETL.

    Creates core dimensional and fact tables (dim_players, dim_teams, bridge_ids, fact_player_gamelogs), creates staging tables defined in STAGING_TABLES with all columns as VARCHAR, and invokes setup_views to create additional views and placeholder tables.

    Args:
        con (duckdb.DuckDBPyConnection): Connection used to execute DDL statements.
    """
    con.execute("""
        CREATE TABLE IF NOT EXISTS franchises (
            franchise_id VARCHAR PRIMARY KEY,
            full_name VARCHAR,
            city VARCHAR,
            year_founded INTEGER,
            is_active BOOLEAN
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS team_seasons (
            season_id VARCHAR,
            franchise_id VARCHAR,
            team_name VARCHAR,
            abbreviation VARCHAR,
            head_coach VARCHAR,
            general_manager VARCHAR,
            owner VARCHAR,
            arena VARCHAR,
            arena_capacity INTEGER,
            PRIMARY KEY (season_id, franchise_id)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS team_season_stats (
            season_id VARCHAR,
            franchise_id VARCHAR,
            games_played INTEGER,
            wins INTEGER,
            losses INTEGER,
            win_percentage DOUBLE,
            mov DOUBLE,
            sos DOUBLE,
            srs DOUBLE,
            offensive_rating DOUBLE,
            defensive_rating DOUBLE,
            net_rating DOUBLE,
            pace DOUBLE,
            free_throw_rate DOUBLE,
            three_point_attempt_rate DOUBLE,
            true_shooting_percentage DOUBLE,
            effective_fg_percentage DOUBLE,
            turnover_percentage DOUBLE,
            offensive_rebound_percentage DOUBLE,
            PRIMARY KEY (season_id, franchise_id)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS player_season_stats (
            player_id VARCHAR,
            season_id VARCHAR,
            franchise_id VARCHAR,
            team_abbrev VARCHAR,
            games_played INTEGER,
            games_started INTEGER,
            minutes_played INTEGER,
            field_goals_made INTEGER,
            field_goals_attempted INTEGER,
            three_pointers_made INTEGER,
            three_pointers_attempted INTEGER,
            two_pointers_made INTEGER,
            two_pointers_attempted INTEGER,
            free_throws_made INTEGER,
            free_throws_attempted INTEGER,
            offensive_rebounds INTEGER,
            defensive_rebounds INTEGER,
            total_rebounds INTEGER,
            assists INTEGER,
            steals INTEGER,
            blocks INTEGER,
            turnovers INTEGER,
            personal_fouls INTEGER,
            points INTEGER
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS player_season_advanced (
            player_id VARCHAR,
            season_id VARCHAR,
            franchise_id VARCHAR,
            per DOUBLE,
            true_shooting_percentage DOUBLE,
            three_point_attempt_rate DOUBLE,
            free_throw_rate DOUBLE,
            offensive_rebound_percentage DOUBLE,
            defensive_rebound_percentage DOUBLE,
            total_rebound_percentage DOUBLE,
            assist_percentage DOUBLE,
            steal_percentage DOUBLE,
            block_percentage DOUBLE,
            turnover_percentage DOUBLE,
            usage_percentage DOUBLE,
            offensive_win_shares DOUBLE,
            defensive_win_shares DOUBLE,
            win_shares DOUBLE,
            win_shares_per_48 DOUBLE,
            offensive_box_plus_minus DOUBLE,
            defensive_box_plus_minus DOUBLE,
            box_plus_minus DOUBLE,
            vorp DOUBLE
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS player_season_shooting (
            player_id VARCHAR,
            season_id VARCHAR,
            franchise_id VARCHAR,
            avg_dist_fga DOUBLE,
            percent_fga_2p DOUBLE,
            percent_fga_0_3 DOUBLE,
            percent_fga_3_10 DOUBLE,
            percent_fga_10_16 DOUBLE,
            percent_fga_16_3p DOUBLE,
            percent_fga_3p DOUBLE,
            fg_percent_2p DOUBLE,
            fg_percent_0_3 DOUBLE,
            fg_percent_3_10 DOUBLE,
            fg_percent_10_16 DOUBLE,
            fg_percent_16_3p DOUBLE,
            fg_percent_3p DOUBLE,
            percent_assisted_2p DOUBLE,
            percent_assisted_3p DOUBLE,
            percent_dunks_of_fga DOUBLE,
            num_dunks INTEGER,
            percent_corner_3s_of_3pa DOUBLE,
            corner_3_point_percent DOUBLE,
            num_heaves_attempted INTEGER,
            num_heaves_made INTEGER
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS player_season_play_by_play (
            player_id VARCHAR,
            season_id VARCHAR,
            franchise_id VARCHAR,
            pg_percent INTEGER,
            sg_percent INTEGER,
            sf_percent INTEGER,
            pf_percent INTEGER,
            c_percent INTEGER,
            on_court_plus_minus_per_100 DOUBLE,
            net_plus_minus_per_100 DOUBLE,
            bad_pass_turnovers INTEGER,
            lost_ball_turnovers INTEGER,
            shooting_fouls_committed INTEGER,
            offensive_fouls_committed INTEGER,
            shooting_fouls_drawn INTEGER,
            offensive_fouls_drawn INTEGER,
            points_generated_by_assists INTEGER,
            and1s INTEGER,
            fga_blocked INTEGER
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS games (
            game_id VARCHAR PRIMARY KEY,
            season_id VARCHAR,
            game_date DATE,
            home_franchise_id VARCHAR,
            away_franchise_id VARCHAR,
            home_score INTEGER,
            away_score INTEGER,
            winner_franchise_id VARCHAR,
            game_type VARCHAR,
            attendance INTEGER,
            arena_id VARCHAR,
            duration_minutes INTEGER
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS player_game_stats (
            player_id VARCHAR,
            game_id VARCHAR,
            franchise_id VARCHAR,
            minutes_played DOUBLE,
            pts INTEGER,
            ast INTEGER,
            reb INTEGER,
            blk INTEGER,
            stl INTEGER,
            tov INTEGER,
            fgm INTEGER,
            fga INTEGER,
            fg3m INTEGER,
            fg3a INTEGER,
            ftm INTEGER,
            fta INTEGER,
            plus_minus INTEGER,
            game_score DOUBLE,
            PRIMARY KEY (player_id, game_id)
        )
    """)

    # Create Core Dimensional Tables (Preserved from existing schema)
    con.execute("""
        CREATE TABLE IF NOT EXISTS players (
            person_id VARCHAR PRIMARY KEY,
            player_slug VARCHAR UNIQUE NOT NULL,
            first_name VARCHAR,
            last_name VARCHAR,
            birth_date DATE,
            height_string VARCHAR,
            height_inches INTEGER,
            weight INTEGER,
            draft_year INTEGER,
            draft_round INTEGER,
            draft_number INTEGER,
            from_year INTEGER,
            to_year INTEGER,
            is_hof BOOLEAN
        )
    """)
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
            minutes_played INTEGER,
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

    # Create Staging Tables
    for table_name, columns in STAGING_TABLES.items():
        # Using VARCHAR for all staging columns to allow raw data loading without type errors.
        # Strict typing happens during transformation to dim/fact tables.
        columns_def = ", ".join([f"{col} VARCHAR" for col in columns])
        con.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})")

    # Setup Views
    setup_views(con)
