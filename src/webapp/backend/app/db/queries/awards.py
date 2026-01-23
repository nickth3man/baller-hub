"""Awards database queries."""

LIST_AWARDS = """
    SELECT * FROM award ORDER BY name
"""

GET_AWARD_BY_ID = """
    SELECT * FROM award WHERE award_id = ?
"""

GET_AWARD_RECIPIENTS = """
    SELECT
        ar.*,
        p.full_name as player_name,
        t.abbreviation as team_abbrev,
        a.name as award_name,
        s.year as season_year
    FROM award_recipient ar
    JOIN award a ON ar.award_id = a.award_id
    JOIN season s ON ar.season_id = s.season_id
    LEFT JOIN player p ON ar.player_id = p.player_id
    LEFT JOIN team t ON ar.team_id = t.team_id
    WHERE ar.award_id = ?
    ORDER BY s.year DESC, ar.vote_rank ASC
"""
