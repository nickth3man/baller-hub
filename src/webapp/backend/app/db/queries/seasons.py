LIST_SEASONS = """
    SELECT
        season_id,
        year,
        (year - 1) || '-' || substr(CAST(year AS VARCHAR), 3, 2) as season_name,
        -- champion, runner_up logic requires joining with something not yet in simple view
        -- For now return basic info
        year = (SELECT MAX(year) FROM season) as is_active,
        NULL as champion,
        NULL as champion_team_name
    FROM season
    ORDER BY year DESC
"""

GET_SEASON_BY_YEAR = """
    SELECT
        season_id,
        year,
        (year - 1) || '-' || substr(CAST(year AS VARCHAR), 3, 2) as season_name,
        year = (SELECT MAX(year) FROM season) as is_active,
        NULL as champion,
        NULL as champion_team_name,
        NULL as runner_up_team_name,
        -- dates from games
        (SELECT MIN(date) FROM games WHERE season_year = ?) as start_date,
        (SELECT MAX(date) FROM games WHERE season_year = ?) as end_date
    FROM season
    WHERE year = ?
"""

GET_SEASON_SCHEDULE = """
    SELECT
        g.game_id,
        g.date,
        g.time,
        t_home.abbreviation as home_team_abbrev,
        t_away.abbreviation as away_team_abbrev,
        g.home_score,
        g.away_score,
        g.season_type
    FROM games g
    LEFT JOIN dim_teams t_home ON g.home_team_id = t_home.team_id
    LEFT JOIN dim_teams t_away ON g.away_team_id = t_away.team_id
    WHERE g.season_year = ?
    ORDER BY g.date, g.time
"""

GET_SEASON_PLAYER_STATS = """
    SELECT
        ps.*,
        p.slug as player_slug,
        (p.first_name || ' ' || p.last_name) as player_name,
        -- team_abbrev handling needs logic for TOT
        CASE WHEN ps.team_id IS NULL THEN 'TOT' ELSE t.abbreviation END as team_abbrev
    FROM player_season ps
    JOIN dim_players p ON ps.player_id = p.player_id
    LEFT JOIN dim_teams t ON ps.team_id = t.team_id
    WHERE ps.season_id = ?
      AND ps.season_type = 'REGULAR'
      AND ps.games_played >= ?
"""

GET_SEASON_ADVANCED_STATS = """
    SELECT
        ps.*,
        p.slug as player_slug,
        (p.first_name || ' ' || p.last_name) as player_name,
        t.abbreviation as team_abbrev -- might be NULL for TOT? need to check schema
    FROM player_season_advanced ps
    JOIN dim_players p ON ps.player_id = p.player_id
    LEFT JOIN dim_teams t ON ps.franchise_id = t.team_id -- table uses franchise_id? check schema
    WHERE ps.season_id = ?
      -- AND ps.season_type = 'REGULAR' -- table might not have season_type? check schema
      AND ps.games_played >= ?
"""
