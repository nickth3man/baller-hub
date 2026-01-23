"""Service layer for player-related business logic.

This module provides the PlayerService class which handles all player-related
data access operations including listing players, retrieving player details,
game logs, career statistics, and splits.
"""

import duckdb

from app.db.queries import players as player_queries


class PlayerService:
    """Service for managing player data retrieval and aggregation.

    This service provides methods to query and aggregate player information
    from the database, including player listings, detailed profiles,
    game logs, career statistics, and splits.

    Attributes:
        conn: DuckDB database connection for executing queries.
    """

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        """Initialize PlayerService with database connection.

        Args:
            conn: DuckDB database connection for executing queries.
        """
        self.conn = conn

    def list_players(  # noqa: PLR0913
        self,
        page: int = 1,
        per_page: int = 50,
        is_active: bool | None = None,
        position: str | None = None,
        search: str | None = None,
        season_year: int | None = None,
        team_abbrev: str | None = None,
    ) -> dict:
        """Retrieve a paginated list of players with optional filters.

        Supports filtering by active status, position, search term, season year,
        and team abbreviation. Results are ordered by last name, then first name.

        Args:
            page: Page number for pagination (1-indexed). Defaults to 1.
            per_page: Number of players per page. Defaults to 50.
            is_active: Filter for active players only. None returns all.
            position: Filter by player position (PG, SG, SF, PF, C).
            search: Case-insensitive search on first/last name (prefix match).
            season_year: Filter by current season year for the player.
            team_abbrev: Filter by team abbreviation (e.g., 'LAL', 'BOS').

        Returns:
            dict: Paginated response containing:
                - items: List of player records.
                - total: Total count of matching players.
                - page: Current page number.
                - per_page: Items per page.
                - pages: Total number of pages.
        """
        query = player_queries.LIST_PLAYERS
        params = []

        if is_active is not None:
            query += " AND (is_active = ? OR (is_active IS NULL AND ? = FALSE))"
            params.extend([is_active, is_active])

        if position:
            query += " AND position = ?"
            params.append(position)

        if search:
            query += " AND (first_name ILIKE ? OR last_name ILIKE ?)"
            pattern = f"%{search}%"
            params.extend([pattern, pattern])

        if season_year:
            query += " AND current_season_year = ?"
            params.append(season_year)

        if team_abbrev:
            query += " AND team_abbrev = ?"
            params.append(team_abbrev.upper())

        count_sql = f"SELECT COUNT(*) FROM ({query}) as q"
        total = self.conn.execute(count_sql, params).fetchone()[0]

        query += " ORDER BY last_name, first_name LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])

        result = self.conn.execute(query, params).fetchall()

        columns = [desc[0] for desc in self.conn.description]
        items = [dict(zip(columns, row, strict=False)) for row in result]

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }

    def get_player_by_slug(self, slug: str) -> dict | None:
        """Retrieve a single player by their slug identifier.

        Args:
            slug: Player's unique slug identifier.

        Returns:
            dict | None: Player record if found, None otherwise.
        """
        result = self.conn.execute(player_queries.GET_PLAYER_BY_SLUG, [slug]).fetchone()

        if not result:
            return None

        columns = [desc[0] for desc in self.conn.description]
        return dict(zip(columns, result, strict=False))

    def get_player_game_log(
        self,
        player_slug: str,
        season_year: int,
        season_type: str = "REGULAR",
    ) -> dict | None:
        """Retrieve a player's game log for a specific season.

        Args:
            player_slug: Player's unique slug identifier.
            season_year: The season year (e.g., 2024 for 2023-24 season).
            season_type: Type of season (REGULAR or PLAYOFF). Defaults to REGULAR.

        Returns:
            dict | None: Game log data including:
                - player_slug: Player identifier.
                - player_name: Player's full name.
                - season_year: Season year.
                - season_type: Season type.
                - games: List of individual game records.
                - totals: Aggregated totals (games_played, points, rebounds, assists).
            None if player not found.
        """
        player = self.get_player_by_slug(player_slug)

        if not player:
            return None

        rows = self.conn.execute(
            player_queries.GET_PLAYER_GAME_LOG, [player_slug, season_year, season_type]
        ).fetchall()

        columns = [desc[0] for desc in self.conn.description]
        games = [dict(zip(columns, row, strict=False)) for row in rows]

        totals = {
            "games_played": len(games),
            "points": sum(g.get("points_scored", 0) for g in games),
            "rebounds": sum(g.get("rebounds_total", 0) for g in games),
            "assists": sum(g.get("assists", 0) for g in games),
        }

        return {
            "player_slug": player_slug,
            "player_name": player["full_name"],
            "season_year": season_year,
            "season_type": season_type,
            "games": games,
            "totals": totals,
        }

    def get_player_career_stats(self, player_slug: str) -> list[dict]:
        """Retrieve career statistics by season for a player.

        Args:
            player_slug: Player's unique slug identifier.

        Returns:
            list[dict]: List of season-by-season career statistics.
        """
        rows = self.conn.execute(
            player_queries.GET_PLAYER_CAREER_STATS, [player_slug]
        ).fetchall()

        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row, strict=False)) for row in rows]

    def get_player_career(self, player_slug: str) -> dict | None:
        """Retrieve aggregated career totals for a player.

        Args:
            player_slug: Player's unique slug identifier.

        Returns:
            dict | None: Career summary containing:
                - player_slug: Player identifier.
                - games_played: Total games across all seasons.
                - career_points: Total points scored across all seasons.
            None if no career stats found.
        """
        stats = self.get_player_career_stats(player_slug)
        if not stats:
            return None

        total_games = sum(s["games_played"] for s in stats)
        total_points = sum(s["points_scored"] for s in stats)

        return {
            "player_slug": player_slug,
            "games_played": total_games,
            "career_points": total_points,
        }

    def get_player_splits(self, _player_slug: str, _season_year: int) -> dict:
        return {}
