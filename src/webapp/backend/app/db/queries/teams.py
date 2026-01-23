LIST_TEAMS = """
    SELECT 
        team_id,
        abbreviation,
        name,
        city,
        arena,
        1900 as founded_year, -- Placeholder
        TRUE as is_active     -- Placeholder
    FROM dim_teams
    WHERE 1=1
"""

GET_TEAM_BY_ABBREVIATION = """
    SELECT 
        team_id,
        abbreviation,
        name,
        city,
        arena,
        1900 as founded_year, -- Placeholder
        TRUE as is_active     -- Placeholder
    FROM dim_teams
    WHERE abbreviation = ?
"""

GET_TEAM_ID = """
    SELECT team_id FROM dim_teams WHERE abbreviation = ?
"""

GET_TEAM_ROSTER = """
    SELECT 
        p.player_id,
        p.slug,
        (p.first_name || ' ' || p.last_name) as name,
        p.position,
        COUNT(DISTINCT pg.game_id) as games_played,
        SUM(CASE WHEN pg.minutes_played > 0 THEN 1 ELSE 0 END) as games_started, -- Approximation
        CAST(SUM(pg.points_scored) AS FLOAT) / NULLIF(COUNT(DISTINCT pg.game_id), 0) as ppg
    FROM fact_player_gamelogs pg
    JOIN dim_players p ON pg.player_id = p.player_id
    WHERE pg.team_id = ? AND pg.season_year = ?
    GROUP BY p.player_id, p.slug, p.first_name, p.last_name, p.position
    ORDER BY p.last_name
"""

GET_TEAM_SCHEDULE = """
    SELECT 
        g.game_id,
        g.date,
        CASE WHEN g.home_team_id = ? THEN g.home_score ELSE g.away_score END as team_score,
        CASE WHEN g.home_team_id = ? THEN g.away_score ELSE g.home_score END as opponent_score,
        CASE WHEN g.home_team_id = ? THEN 'HOME' ELSE 'AWAY' END as location,
        CASE WHEN (g.home_team_id = ? AND g.home_score > g.away_score) OR
                  (g.away_team_id = ? AND g.away_score > g.home_score) 
             THEN 'W' ELSE 'L' END as result,
        t_opp.abbreviation as opponent_abbrev
    FROM games g
    JOIN dim_teams t_opp ON (CASE WHEN g.home_team_id = ? THEN g.away_team_id ELSE g.home_team_id END) = t_opp.team_id
    WHERE (g.home_team_id = ? OR g.away_team_id = ?) 
      AND g.season_year = ?
    ORDER BY g.date
"""

GET_TEAM_SEASON_STATS = """
    SELECT * FROM team_season_stats 
    WHERE team_id = ? AND season_id = ? 
    -- Note: This table might need adjustment based on schema
"""

GET_TEAM_HISTORY = """
    SELECT 
        ts.season_id as year,
        ts.wins,
        ts.losses,
        ts.win_percentage as win_pct,
        ts.made_playoffs,
        -- ts.playoff_round_reached
        '' as playoff_round
    FROM team_seasons ts
    -- Join dim_teams/franchises if needed to link by abbreviation/id
    WHERE ts.abbreviation = ?
    ORDER BY ts.season_id DESC
"""

GET_FRANCHISE_HISTORY = """
    SELECT * FROM franchises WHERE franchise_id = (
        SELECT franchise_id FROM dim_teams WHERE abbreviation = ?
    )
"""
