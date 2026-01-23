"""Service layer for season-related business logic.

This module provides SeasonService class which handles all season-related
data access operations including listing seasons, retrieving season details,
player statistics, and scheduling information.
"""

import duckdb

from app.db.queries import seasons as season_queries


class SeasonService:
    """Service for managing season data retrieval and aggregation.

    This service provides methods to query and aggregate season information
    from the database, including season listings, player statistics,
    and schedule data.

    Attributes:
        conn: DuckDB database connection for executing queries.
    """

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def list_seasons(self, _league: str = "NBA", limit: int = 20):
        query = season_queries.LIST_SEASONS + " LIMIT ?"
        result = self.conn.execute(query, [limit]).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row, strict=False)) for row in result]

    def get_current_season(self):
        max_year = self.conn.execute("SELECT MAX(year) FROM season").fetchone()[0]
        if not max_year:
            return None
        return self.get_season_by_year(max_year)

    def get_season_by_year(self, year: int):
        result = self.conn.execute(
            season_queries.GET_SEASON_BY_YEAR, [year, year, year]
        ).fetchone()

        if not result:
            return None

        columns = [desc[0] for desc in self.conn.description]
        return dict(zip(columns, result, strict=False))

    def get_season_schedule(self, season_year: int, month: int | None = None):
        query = season_queries.GET_SEASON_SCHEDULE
        params = [season_year]

        if month is not None:
            query = "SELECT * FROM (" + query + ") WHERE month(date) = ?"
            params.append(month)

        result = self.conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        games = [dict(zip(columns, row, strict=False)) for row in result]

        return {"season_year": season_year, "month": month, "games": games}

    def get_season_leaders(
        self,
        season_year: int,
        category: str = "points",
        per_game: bool = True,
        limit: int = 10,
    ):
        stat_map = {
            "points": "points_scored",
            "rebounds": "total_rebounds",
            "assists": "assists",
            "steals": "steals",
            "blocks": "blocks",
        }
        stat_col = stat_map.get(category, "points_scored")

        query = season_queries.GET_SEASON_PLAYER_STATS
        params = [season_year, 0]

        result = self.conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        rows = [dict(zip(columns, row, strict=False)) for row in result]

        players = {}
        for row in rows:
            pid = row["player_id"]
            if pid not in players or row["is_combined_totals"]:
                players[pid] = row

        leaders = []
        for p in players.values():
            val = p.get(stat_col, 0) or 0
            gp = p.get("games_played", 1) or 1
            if per_game:
                val = val / gp

            leaders.append(
                {
                    "player_slug": p["player_slug"],
                    "player_name": p["player_name"],
                    "team_abbrev": p["team_abbrev"],
                    "value": float(val),
                    "games_played": p["games_played"],
                }
            )

        leaders.sort(key=lambda x: x["value"], reverse=True)
        leaders = leaders[:limit]

        for idx, leader in enumerate(leaders):
            leader["rank"] = idx + 1

        return {
            "season_year": season_year,
            "category": category,
            "per_game": per_game,
            "leaders": leaders,
        }

    def get_season_player_stats(  # noqa: PLR0913
        self,
        season_year: int,
        stat_type: str = "totals",
        position: str | None = None,
        min_games: int = 0,
        page: int = 1,
        per_page: int = 50,
        sort_by: str = "points",
        sort_order: str = "desc",
    ):
        is_advanced = stat_type == "advanced"
        query = (
            season_queries.GET_SEASON_ADVANCED_STATS
            if is_advanced
            else season_queries.GET_SEASON_PLAYER_STATS
        )
        params = [season_year, min_games]

        if position:
            query += " AND position = ?"
            params.append(position)

        result = self.conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        items = [dict(zip(columns, row, strict=False)) for row in result]

        unique_items = {}
        for item in items:
            pid = item["player_id"]
            if pid not in unique_items or item.get("is_combined_totals"):
                unique_items[pid] = item

        items = list(unique_items.values())

        if not is_advanced and stat_type in {"per_game", "per_36", "per_100"}:
            items = [self._apply_rate_transform(stat_type, item) for item in items]

        reverse = sort_order.lower() == "desc"
        items.sort(key=lambda x: x.get(sort_by, 0) or 0, reverse=reverse)

        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        paged_items = items[start:end]

        return {
            "items": paged_items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }

    def _apply_rate_transform(self, stat_type: str, item: dict) -> dict:
        games_played = max(item.get("games_played", 0), 1)
        minutes_played = item.get("minutes_played", 0) or 0
        if stat_type == "per_game":
            factor = games_played
        elif stat_type == "per_36":
            factor = minutes_played / 36 if minutes_played else 0
        else:
            factor = minutes_played / 100 if minutes_played else 0

        if factor == 0:
            return item

        fields_to_transform = [
            "points",
            "rebounds",
            "assists",
            "steals",
            "blocks",
            "turnovers",
            "fg_made",
            "fg_attempted",
            "fg3_made",
            "fg3_attempted",
            "ft_made",
            "ft_attempted",
        ]

        new_item = item.copy()
        for field in fields_to_transform:
            key_map = {
                "points": "points_scored",
                "rebounds": "total_rebounds",
            }
            actual_key = key_map.get(field, field)
            if actual_key in item:
                new_item[actual_key] = (item[actual_key] or 0) / factor

        return new_item
