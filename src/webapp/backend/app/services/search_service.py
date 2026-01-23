"""Service layer for search and autocomplete functionality.

This module provides SearchService class which handles search operations
across players, teams, and games using both Meilisearch (when available)
and DuckDB fallback.
"""

import duckdb
import structlog
from app.db.queries import search as search_queries
from app.search.indexer import SearchIndexer

logger = structlog.get_logger(__name__)


class SearchService:
    """Service for managing search and autocomplete operations.

    This service provides methods to search across players, teams, and games,
    with support for both Meilisearch (preferred) and DuckDB fallback.

    Attributes:
        conn: DuckDB database connection for fallback queries.
        use_meilisearch: Whether to use Meilisearch when available.
        _indexer: Lazy-loaded SearchIndexer instance.
    """

    def __init__(self, conn: duckdb.DuckDBPyConnection, use_meilisearch: bool = True):
        """Initialize SearchService with database connection.

        Args:
            conn: DuckDB database connection for fallback queries.
            use_meilisearch: Whether to use Meilisearch when available.
        """
        self.conn = conn
        self.use_meilisearch = use_meilisearch
        self._indexer: SearchIndexer | None = None

    def __init__(self, conn: duckdb.DuckDBPyConnection, use_meilisearch: bool = True):
        self.conn = conn
        self.use_meilisearch = use_meilisearch
        self._indexer: SearchIndexer | None = None

    @property
    def indexer(self) -> SearchIndexer:
        """Lazy-load and return the SearchIndexer instance.

        Returns:
            SearchIndexer: Configured search indexer instance.
        """
        if self._indexer is None:
            self._indexer = SearchIndexer()
        return self._indexer

    def search(
        self,
        query: str,
        entity_type: str | None = None,
        limit: int = 20,
    ) -> dict:
        results = {
            "query": query,
            "players": [],
            "teams": [],
            "games": [],
            "total_results": 0,
        }

        if self.use_meilisearch:
            try:
                meili_results = self.indexer.search_all(query, limit_per_index=limit)

                if entity_type is None or entity_type == "player":
                    results["players"] = [
                        self._normalize_player_hit(hit)
                        for hit in meili_results.get("players", [])
                    ]
                if entity_type is None or entity_type == "team":
                    results["teams"] = [
                        self._normalize_team_hit(hit)
                        for hit in meili_results.get("teams", [])
                    ]
                if entity_type is None or entity_type == "game":
                    results["games"] = [
                        self._normalize_game_hit(hit)
                        for hit in meili_results.get("games", [])
                    ]

                results["total_results"] = (
                    len(results["players"])
                    + len(results["teams"])
                    + len(results["games"])
                )
                return results
            except Exception as e:
                logger.warning(
                    "Meilisearch search failed, falling back to DB", error=str(e)
                )

        if entity_type is None or entity_type == "player":
            players = self._db_search_players(query, limit)
            results["players"] = [self._normalize_player_model(p) for p in players]

        if entity_type is None or entity_type == "team":
            teams = self._db_search_teams(query, limit)
            results["teams"] = [self._normalize_team_model(t) for t in teams]

        results["total_results"] = len(results["players"]) + len(results["teams"])
        return results

    def autocomplete(
        self,
        query: str,
        limit: int = 10,
    ) -> dict:
        if self.use_meilisearch:
            try:
                suggestions = self.indexer.get_autocomplete_suggestions(query, limit)
                return {"query": query, "suggestions": suggestions}
            except Exception as e:
                logger.warning("Meilisearch autocomplete failed", error=str(e))

        suggestions = []

        player_result = self.conn.execute(
            search_queries.SEARCH_PLAYERS_DB, [f"%{query}%", f"%{query}%", limit // 2]
        ).fetchall()
        cols = [desc[0] for desc in self.conn.description]

        for row in player_result:
            p = dict(zip(cols, row))
            suggestions.append(
                {
                    "type": "player",
                    "id": p.get("player_id"),
                    "slug": p.get("slug"),
                    "text": p.get("full_name"),
                    "subtitle": p.get("position", "").replace("_", " ")
                    if p.get("position")
                    else "",
                    "url": f"/players/{p.get('slug')}",
                }
            )

        team_result = self.conn.execute(
            search_queries.SEARCH_TEAMS_DB,
            [f"%{query}%", f"%{query}%", f"%{query}%", limit // 2],
        ).fetchall()
        cols = [desc[0] for desc in self.conn.description]

        for row in team_result:
            t = dict(zip(cols, row))
            suggestions.append(
                {
                    "type": "team",
                    "id": t.get("team_id"),
                    "text": f"{t.get('city')} {t.get('name')}",
                    "subtitle": t.get("abbreviation"),
                    "url": f"/teams/{t.get('abbreviation')}",
                }
            )

        return {"query": query, "suggestions": suggestions}

    def _db_search_players(
        self,
        query: str,
        limit: int,
        position: str | None = None,
        active_only: bool = False,
        team_abbrev: str | None = None,
    ) -> list[dict]:
        sql = search_queries.SEARCH_PLAYERS_DB
        params = [f"%{query}%", f"%{query}%", limit]

        result = self.conn.execute(sql, params).fetchall()
        cols = [desc[0] for desc in self.conn.description]
        return [dict(zip(cols, row)) for row in result]

    def _db_search_teams(
        self,
        query: str,
        limit: int,
        active_only: bool = True,
    ) -> list[dict]:
        sql = search_queries.SEARCH_TEAMS_DB
        params = [f"%{query}%", f"%{query}%", f"%{query}%", limit]

        result = self.conn.execute(sql, params).fetchall()
        cols = [desc[0] for desc in self.conn.description]
        return [dict(zip(cols, row)) for row in result]

    def _format_years_active(
        self, debut_year: int | None, final_year: int | None, is_active: bool
    ) -> str | None:
        if debut_year and final_year:
            return (
                f"{debut_year}-Present" if is_active else f"{debut_year}-{final_year}"
            )
        if debut_year:
            return f"{debut_year}-Present" if is_active else str(debut_year)
        if final_year:
            return str(final_year)
        return None

    def _normalize_player_hit(self, hit: dict) -> dict:
        debut_year = hit.get("debut_year")
        final_year = hit.get("final_year")
        is_active = hit.get("is_active", False)
        return {
            "player_id": hit.get("player_id"),
            "slug": hit.get("slug"),
            "full_name": hit.get("full_name") or hit.get("name") or "",
            "name": hit.get("full_name") or hit.get("name"),
            "position": hit.get("position"),
            "years_active": self._format_years_active(
                debut_year, final_year, is_active
            ),
            "is_active": is_active,
        }

    def _normalize_team_hit(self, hit: dict) -> dict:
        return {
            "team_id": hit.get("team_id"),
            "abbreviation": hit.get("abbreviation"),
            "name": hit.get("name"),
            "city": hit.get("city"),
            "is_active": hit.get("is_active", True),
        }

    def _normalize_game_hit(self, hit: dict) -> dict:
        score = None
        if hit.get("away_score") is not None and hit.get("home_score") is not None:
            score = f"{hit.get('away_score')}-{hit.get('home_score')}"
        return {
            "game_id": hit.get("game_id"),
            "game_date": hit.get("game_date") or hit.get("date"),
            "matchup": hit.get("matchup") or f"Game {hit.get('game_id')}",
            "score": score,
        }

    def _normalize_player_model(self, player: dict) -> dict:
        return {
            "player_id": player.get("player_id"),
            "slug": player.get("slug"),
            "full_name": player.get("full_name"),
            "name": player.get("full_name"),
            "position": player.get("position"),
            "years_active": self._format_years_active(
                player.get("debut_year"),
                player.get("final_year"),
                player.get("is_active", False),
            ),
            "is_active": player.get("is_active"),
        }

    def _normalize_team_model(self, team: dict) -> dict:
        return {
            "team_id": team.get("team_id"),
            "abbreviation": team.get("abbreviation"),
            "name": team.get("name"),
            "city": team.get("city"),
            "is_active": team.get("is_active"),
        }
