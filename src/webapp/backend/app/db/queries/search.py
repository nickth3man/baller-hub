SEARCH_PLAYERS_DB = """
    SELECT 
        p.*,
        (p.first_name || ' ' || p.last_name) as full_name
    FROM dim_players p
    WHERE 
        p.first_name ILIKE ? OR 
        p.last_name ILIKE ?
    LIMIT ?
"""

SEARCH_TEAMS_DB = """
    SELECT 
        t.*,
        (t.city || ' ' || t.name) as full_name
    FROM dim_teams t
    WHERE 
        t.name ILIKE ? OR 
        t.city ILIKE ? OR 
        t.abbreviation ILIKE ?
    LIMIT ?
"""

INDEX_ALL_GAMES = """
    SELECT g.* FROM games g
"""
