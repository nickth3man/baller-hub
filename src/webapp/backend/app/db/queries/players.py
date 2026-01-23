LIST_PLAYERS = """
    SELECT
        p.*,
        (p.first_name || ' ' || p.last_name) as full_name,
        ps.team_id,
        t.abbreviation as team_abbrev,
        ps.season_id as current_season_year
    FROM dim_players p
    LEFT JOIN (
        SELECT player_id, team_id, season_id,
               ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY season_id DESC) as rn
        FROM fact_player_gamelogs
    ) ps ON p.player_id = ps.player_id AND ps.rn = 1
    LEFT JOIN dim_teams t ON ps.team_id = t.team_id
    WHERE 1=1
"""

GET_PLAYER_BY_SLUG = """
    SELECT
        p.*,
        (p.first_name || ' ' || p.last_name) as full_name
    FROM dim_players p
    WHERE p.slug = ?
"""

GET_PLAYER_GAME_LOG = """
    SELECT
        pg.*,
        g.date as game_date,
        t.abbreviation as opponent_abbrev,
        CASE WHEN g.home_team_id = pg.team_id THEN 'HOME' ELSE 'AWAY' END as location,
        CASE WHEN (g.home_team_id = pg.team_id AND g.home_score > g.away_score) OR
                  (g.away_team_id = pg.team_id AND g.away_score > g.home_score)
             THEN 'WIN' ELSE 'LOSS' END as outcome
    FROM fact_player_gamelogs pg
    JOIN dim_games g ON pg.game_id = g.game_id
    JOIN dim_teams t ON (CASE WHEN g.home_team_id = pg.team_id THEN g.away_team_id ELSE g.home_team_id END) = t.team_id
    JOIN dim_players p ON pg.player_id = p.player_id
    WHERE p.slug = ? AND pg.season_year = ? AND pg.season_type = ?
    ORDER BY g.date
"""

GET_PLAYER_CAREER_STATS = """
    SELECT
        ps.season_year,
        ps.season_type,
        ps.team_id,
        t.abbreviation as team_abbrev,
        SUM(ps.games_played) as games_played,
        SUM(ps.points_scored) as points_scored,
        SUM(ps.assists) as assists,
        SUM(ps.rebounds_total) as total_rebounds
    FROM fact_player_gamelogs ps
    JOIN dim_players p ON ps.player_id = p.player_id
    LEFT JOIN dim_teams t ON ps.team_id = t.team_id
    WHERE p.slug = ?
    GROUP BY ps.season_year, ps.season_type, ps.team_id, t.abbreviation
    ORDER BY ps.season_year DESC
"""
