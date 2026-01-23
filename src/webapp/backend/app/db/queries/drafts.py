"""Draft database queries."""

LIST_DRAFTS = """
    SELECT
        d.*,
        s.year as season_year
    FROM draft d
    JOIN season s ON d.season_id = s.season_id
    ORDER BY d.year DESC
"""

GET_DRAFT_BY_YEAR = """
    SELECT
        d.*,
        s.year as season_year
    FROM draft d
    JOIN season s ON d.season_id = s.season_id
    WHERE d.year = ?
"""

GET_DRAFT_PICKS = """
    SELECT
        dp.*,
        p.full_name as player_name,
        t.abbreviation as team_abbrev
    FROM draft_pick dp
    LEFT JOIN player p ON dp.player_id = p.player_id
    LEFT JOIN team t ON dp.team_id = t.team_id
    WHERE dp.draft_id = ?
    ORDER BY dp.overall_pick
"""
