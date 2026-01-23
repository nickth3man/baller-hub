LIST_GAMES = """
    SELECT 
        g.game_id,
        g.date as game_date,
        g.home_team_id,
        g.away_team_id,
        g.home_score,
        g.away_score,
        g.season_year,
        g.season_type,
        t_home.abbreviation as home_team_abbrev,
        t_away.abbreviation as away_team_abbrev,
        g.arena,
        g.attendance
    FROM games g
    LEFT JOIN dim_teams t_home ON g.home_team_id = t_home.team_id
    LEFT JOIN dim_teams t_away ON g.away_team_id = t_away.team_id
    WHERE 1=1
"""

GET_GAME_BY_ID = """
    SELECT 
        g.game_id,
        g.date as game_date,
        g.home_team_id,
        g.away_team_id,
        g.home_score,
        g.away_score,
        g.season_year,
        g.season_type,
        t_home.abbreviation as home_team_abbrev,
        t_away.abbreviation as away_team_abbrev,
        g.arena,
        g.attendance,
        g.duration_minutes
    FROM games g
    LEFT JOIN dim_teams t_home ON g.home_team_id = t_home.team_id
    LEFT JOIN dim_teams t_away ON g.away_team_id = t_away.team_id
    WHERE g.game_id = ?
"""

GET_PLAYER_BOX_SCORES = """
    SELECT 
        pg.*,
        p.slug,
        (p.first_name || ' ' || p.last_name) as full_name,
        p.position
    FROM fact_player_gamelogs pg
    JOIN dim_players p ON pg.player_id = p.player_id
    WHERE pg.game_id = ?
    ORDER BY pg.team_id, pg.minutes_played DESC
"""

GET_PLAY_BY_PLAY = """
    SELECT * FROM play_by_play WHERE game_id = ? ORDER BY period, seconds_remaining DESC
"""
