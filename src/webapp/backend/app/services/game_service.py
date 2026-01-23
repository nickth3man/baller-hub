"""Service layer for game-related business logic.

This module provides GameService class which handles all game-related
data access operations including listing games, retrieving box scores,
play-by-play data, and weekly game summaries.
"""

from datetime import UTC, date, datetime, timedelta

import duckdb

from app.db.queries import games as game_queries


class GameService:
    """Service for managing game data retrieval and aggregation.

    This service provides methods to query and aggregate game information
    from the database, including game listings, box scores, play-by-play,
    and date-based filtering.

    Attributes:
        conn: DuckDB database connection for executing queries.
    """

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        """Initialize GameService with database connection.

        Args:
            conn: DuckDB database connection for executing queries.
        """
        self.conn = conn

    def list_games(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        team_abbrev: str | None = None,
        season_year: int | None = None,
        season_type: str = "REGULAR",
        page: int = 1,
        per_page: int = 50,
    ) -> dict:
        """Retrieve a paginated list of games with optional filters.

        Supports filtering by date range, team abbreviation, season year,
        and season type. Results are ordered by game date descending.

        Args:
            start_date: Start of date range filter.
            end_date: End of date range filter.
            team_abbrev: Filter for games involving this team (e.g., 'LAL', 'BOS').
            season_year: Filter by season year.
            season_type: Type of season (REGULAR or PLAYOFF). Defaults to REGULAR.
            page: Page number for pagination (1-indexed). Defaults to 1.
            per_page: Number of games per page. Defaults to 50.

        Returns:
            dict: Paginated response containing:
                - items: List of game records.
                - total: Total count of matching games.
                - page: Current page number.
                - per_page: Items per page.
                - pages: Total number of pages.
        """
        query = game_queries.LIST_GAMES
        params = []

        if start_date:
            query += " AND g.date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND g.date <= ?"
            params.append(end_date)

        if team_abbrev:
            query += " AND (t_home.abbreviation = ? OR t_away.abbreviation = ?)"
            params.extend([team_abbrev.upper(), team_abbrev.upper()])

        if season_year:
            query += " AND g.season_year = ?"
            params.append(season_year)

        if season_type:
            query += " AND g.season_type = ?"
            params.append(season_type)

        count_sql = f"SELECT COUNT(*) FROM ({query}) as q"
        total = self.conn.execute(count_sql, params).fetchone()[0]

        query += " ORDER BY g.date DESC LIMIT ? OFFSET ?"
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

    def get_todays_games(self, target_date: date | None = None) -> list[dict]:
        """Retrieve all games scheduled for today (or a specific date).

        Args:
            target_date: Date to fetch games for. Defaults to today's date.

        Returns:
            list[dict]: List of game records for the specified date.
        """
        if target_date is None:
            target_date = datetime.now(UTC).date()

        query = game_queries.LIST_GAMES + " AND g.date = ? ORDER BY g.date"
        result = self.conn.execute(query, [target_date]).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row, strict=False)) for row in result]

    def get_game_by_id(self, game_id: int) -> dict | None:
        """Retrieve a single game by its ID.

        Args:
            game_id: The game's unique identifier.

        Returns:
            dict | None: Game record if found, None otherwise.
        """
        result = self.conn.execute(game_queries.GET_GAME_BY_ID, [game_id]).fetchone()

        if not result:
            return None

        columns = [desc[0] for desc in self.conn.description]
        return dict(zip(columns, result, strict=False))

    def get_box_score(self, game_id: int) -> dict | None:
        """Retrieve player box scores for a specific game.

        Args:
            game_id: The game's unique identifier.

        Returns:
            dict | None: Box score data containing:
                - game: Game metadata.
                - home_team: Home team's score and player stats.
                - away_team: Away team's score and player stats.
            None if game not found.
        """
        game = self.get_game_by_id(game_id)
        if not game:
            return None

        rows = self.conn.execute(
            game_queries.GET_PLAYER_BOX_SCORES, [game_id]
        ).fetchall()

        cols = [desc[0] for desc in self.conn.description]
        players = [dict(zip(cols, row, strict=False)) for row in rows]

        home_players = [p for p in players if p["team_id"] == game["home_team_id"]]
        away_players = [p for p in players if p["team_id"] == game["away_team_id"]]

        return {
            "game": game,
            "home_team": {
                "team_id": game["home_team_id"],
                "team_abbrev": game["home_team_abbrev"],
                "score": game["home_score"],
                "players": home_players,
            },
            "away_team": {
                "team_id": game["away_team_id"],
                "team_abbrev": game["away_team_abbrev"],
                "score": game["away_score"],
                "players": away_players,
            },
        }

    def get_play_by_play(self, game_id: int, period: int | None = None) -> dict | None:
        """Retrieve play-by-play data for a specific game.

        Args:
            game_id: The game's unique identifier.
            period: Filter for specific period (quarter). None returns all periods.

        Returns:
            dict | None: Play-by-play data containing:
                - game_id: Game identifier.
                - plays: List of play events.
                - period_filter: Period that was filtered (None if all).
            None if play-by-play table doesn't exist or game not found.
        """
        query = game_queries.GET_PLAY_BY_PLAY
        params = [game_id]

        if period is not None:
            query += " AND period = ?"
            params.append(period)

        try:
            result = self.conn.execute(query, params).fetchall()
        except duckdb.CatalogException:
            return None

        cols = [desc[0] for desc in self.conn.description]
        plays = [dict(zip(cols, row, strict=False)) for row in result]

        return {"game_id": game_id, "plays": plays, "period_filter": period}

    def get_games_week(self, reference_date: date | None = None) -> dict:
        """Retrieve games for a week centered on the reference date.

        Fetches games from 3 days before to 3 days after the reference date,
        grouped by date.

        Args:
            reference_date: Center date for the week window. Defaults to today.

        Returns:
            dict: Weekly games containing:
                - start_date: Start of date range (ISO format).
                - end_date: End of date range (ISO format).
                - games_by_date: Dictionary mapping dates to game lists.
        """
        if reference_date is None:
            reference_date = datetime.now(UTC).date()

        start_date = reference_date - timedelta(days=3)
        end_date = reference_date + timedelta(days=3)

        games = self.list_games(start_date=start_date, end_date=end_date, per_page=100)[
            "items"
        ]

        games_by_date = {}
        for game in games:
            d = (
                game["game_date"].isoformat()
                if hasattr(game["game_date"], "isoformat")
                else str(game["game_date"])
            )
            if d not in games_by_date:
                games_by_date[d] = []
            games_by_date[d].append(game)

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "games_by_date": games_by_date,
        }
