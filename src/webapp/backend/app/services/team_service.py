"""Service layer for team-related business logic.

This module provides TeamService class which handles all team-related
data access operations including listing teams, retrieving team details,
roster information, schedules, and season statistics.
"""

import duckdb

from app.db.queries import teams as team_queries


class TeamService:
    """Service for managing team data retrieval and aggregation.

    This service provides methods to query and aggregate team information
    from the database, including team listings, rosters, schedules,
    and historical statistics.

    Attributes:
        conn: DuckDB database connection for executing queries.
    """

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def list_teams(
        self,
        is_active: bool = True,
        conference: str | None = None,
        division: str | None = None,
    ) -> list[dict]:
        query = team_queries.LIST_TEAMS
        params = []

        result = self.conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row, strict=False)) for row in result]

    def get_team_by_abbreviation(self, abbreviation: str) -> dict | None:
        result = self.conn.execute(
            team_queries.GET_TEAM_BY_ABBREVIATION, [abbreviation.upper()]
        ).fetchone()

        if not result:
            return None

        columns = [desc[0] for desc in self.conn.description]
        return dict(zip(columns, result, strict=False))

    def get_team_roster(self, abbreviation: str, season_year: int) -> list[dict]:
        team = self.get_team_by_abbreviation(abbreviation)
        if not team:
            return []
        team_id = team["team_id"]

        result = self.conn.execute(
            team_queries.GET_TEAM_ROSTER, [team_id, season_year]
        ).fetchall()

        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row, strict=False)) for row in result]

    def get_team_schedule(self, abbreviation: str, season_year: int) -> list[dict]:
        team = self.get_team_by_abbreviation(abbreviation)
        if not team:
            return []
        team_id = team["team_id"]

        params = [team_id] * 8 + [season_year]

        result = self.conn.execute(team_queries.GET_TEAM_SCHEDULE, params).fetchall()

        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row, strict=False)) for row in result]

    def get_team_season_stats(self, abbreviation: str, season_year: int) -> dict | None:
        team = self.get_team_by_abbreviation(abbreviation)
        if not team:
            return None
        team_id = team["team_id"]

        try:
            result = self.conn.execute(
                team_queries.GET_TEAM_SEASON_STATS, [team_id, season_year]
            ).fetchone()
        except duckdb.CatalogException:
            return None

        if not result:
            return None

        columns = [desc[0] for desc in self.conn.description]
        return dict(zip(columns, result, strict=False))

    def get_team_history(self, abbreviation: str) -> list[dict]:
        try:
            result = self.conn.execute(
                team_queries.GET_TEAM_HISTORY, [abbreviation.upper()]
            ).fetchall()
        except duckdb.CatalogException:
            return []

        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row, strict=False)) for row in result]

    def get_franchise_history(self, abbreviation: str) -> dict | None:
        try:
            result = self.conn.execute(
                team_queries.GET_FRANCHISE_HISTORY, [abbreviation.upper()]
            ).fetchone()
        except duckdb.CatalogException:
            return None

        if not result:
            return None

        columns = [desc[0] for desc in self.conn.description]
        return dict(zip(columns, result, strict=False))

