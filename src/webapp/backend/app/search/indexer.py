import duckdb
import structlog
from meilisearch import Client
from meilisearch.errors import MeilisearchApiError

from app.db.queries import search as search_queries
from app.search.client import (
    GAMES_INDEX,
    INDEX_CONFIGS,
    PLAYERS_INDEX,
    TEAMS_INDEX,
    get_meilisearch_client,
)

logger = structlog.get_logger(__name__)


class SearchIndexer:
    def __init__(self, client: Client | None = None):
        self.client = client or get_meilisearch_client()

    def setup_indices(self) -> None:
        for index_name, config in INDEX_CONFIGS.items():
            logger.info("Setting up index", index=index_name)

            try:
                self.client.create_index(
                    index_name,
                    {"primaryKey": config["primaryKey"]},
                )
            except MeilisearchApiError as e:
                if "index_already_exists" not in str(e):
                    raise
                logger.info("Index already exists", index=index_name)

            index = self.client.index(index_name)

            settings = {
                "searchableAttributes": config.get("searchableAttributes", ["*"]),
                "filterableAttributes": config.get("filterableAttributes", []),
                "sortableAttributes": config.get("sortableAttributes", []),
                "displayedAttributes": config.get("displayedAttributes", ["*"]),
            }

            if "rankingRules" in config:
                settings["rankingRules"] = config["rankingRules"]

            index.update_settings(settings)
            logger.info("Updated index settings", index=index_name)

    def index_players(
        self, conn: duckdb.DuckDBPyConnection, _batch_size: int = 1000
    ) -> int:
        logger.info("Starting player indexing")

        result = conn.execute(search_queries.INDEX_ALL_PLAYERS).fetchall()
        columns = [desc[0] for desc in conn.description]
        players = [dict(zip(columns, row)) for row in result]

        documents = [self._player_to_document(p) for p in players]

        if documents:
            index = self.client.index(PLAYERS_INDEX)
            index.add_documents(documents, primary_key="player_id")
            logger.info("Indexed players", count=len(documents))

        return len(documents)

    def index_teams(self, conn: duckdb.DuckDBPyConnection) -> int:
        logger.info("Starting team indexing")

        result = conn.execute(search_queries.INDEX_ALL_TEAMS).fetchall()
        columns = [desc[0] for desc in conn.description]
        teams = [dict(zip(columns, row)) for row in result]

        documents = [self._team_to_document(t) for t in teams]

        if documents:
            index = self.client.index(TEAMS_INDEX)
            index.add_documents(documents, primary_key="team_id")
            logger.info("Indexed teams", count=len(documents))

        return len(documents)

    def index_games(
        self,
        conn: duckdb.DuckDBPyConnection,
        season_year: int | None = None,
        _batch_size: int = 1000,
    ) -> int:
        logger.info("Starting game indexing", season_year=season_year)

        query = search_queries.INDEX_ALL_GAMES
        params = []
        if season_year:
            query += " WHERE season_year = ?"
            params.append(season_year)

        result = conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in conn.description]
        games = [dict(zip(columns, row)) for row in result]

        documents = [self._game_to_document(g) for g in games]

        if documents:
            index = self.client.index(GAMES_INDEX)
            index.add_documents(documents, primary_key="game_id")
            logger.info("Indexed games", count=len(documents))

        return len(documents)

    def delete_player(self, player_id: int) -> None:
        index = self.client.index(PLAYERS_INDEX)
        index.delete_document(player_id)

    def delete_team(self, team_id: int) -> None:
        index = self.client.index(TEAMS_INDEX)
        index.delete_document(team_id)

    def search_players(
        self,
        query: str,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        index = self.client.index(PLAYERS_INDEX)

        search_params: dict[str, Any] = {"limit": limit}

        if filters:
            filter_expr = self._build_filter_expression(filters)
            if filter_expr:
                search_params["filter"] = filter_expr

        return index.search(query, search_params)

    def search_teams(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        index = self.client.index(TEAMS_INDEX)
        return index.search(query, {"limit": limit})

    def search_all(
        self,
        query: str,
        limit_per_index: int = 5,
    ) -> dict[str, list[dict[str, Any]]]:
        results = {
            "players": [],
            "teams": [],
            "games": [],
        }

        try:
            player_results = self.search_players(query, limit=limit_per_index)
            results["players"] = player_results.get("hits", [])
        except Exception as e:
            logger.warning("Player search failed", error=str(e))

        try:
            team_results = self.search_teams(query, limit=limit_per_index)
            results["teams"] = team_results.get("hits", [])
        except Exception as e:
            logger.warning("Team search failed", error=str(e))

        try:
            game_index = self.client.index(GAMES_INDEX)
            game_results = game_index.search(query, {"limit": limit_per_index})
            results["games"] = game_results.get("hits", [])
        except Exception as e:
            logger.warning("Game search failed", error=str(e))

        return results

    def get_autocomplete_suggestions(
        self,
        query: str,
        limit: int = 8,
    ) -> list[dict[str, Any]]:
        suggestions = []

        try:
            player_results = self.search_players(query, limit=limit // 2)
            for hit in player_results.get("hits", []):
                suggestions.append(
                    {
                        "type": "player",
                        "id": hit.get("player_id"),
                        "slug": hit.get("slug"),
                        "text": hit.get("full_name"),
                        "subtitle": hit.get("position", "").replace("_", " "),
                        "url": f"/players/{hit.get('slug')}",
                    }
                )
        except Exception:
            pass

        try:
            team_results = self.search_teams(query, limit=limit // 2)
            for hit in team_results.get("hits", []):
                suggestions.append(
                    {
                        "type": "team",
                        "id": hit.get("team_id"),
                        "text": hit.get("full_name")
                        or f"{hit.get('city')} {hit.get('name')}",
                        "subtitle": hit.get("abbreviation"),
                        "url": f"/teams/{hit.get('abbreviation')}",
                    }
                )
        except Exception:
            pass

        return suggestions[:limit]

    def _player_to_document(self, player: dict) -> dict[str, Any]:
        return {
            "player_id": player.get("player_id"),
            "slug": player.get("slug"),
            "first_name": player.get("first_name"),
            "last_name": player.get("last_name"),
            "full_name": player.get("full_name"),
            "position": player.get("position"),
            "is_active": player.get("is_active"),
            "college": player.get("college"),
            "draft_year": player.get("draft_year"),
            "debut_year": player.get("debut_year"),
            "final_year": player.get("final_year"),
        }

    def _team_to_document(self, team: dict) -> dict[str, Any]:
        return {
            "team_id": team.get("team_id"),
            "name": team.get("name"),
            "city": team.get("city"),
            "abbreviation": team.get("abbreviation"),
            "full_name": team.get("full_name"),
            "is_active": team.get("is_active"),
        }

    def _game_to_document(self, game: dict) -> dict[str, Any]:
        return {
            "game_id": game.get("game_id"),
            "game_date": game.get("game_date") if game.get("game_date") else None,
            "home_team_id": game.get("home_team_id"),
            "away_team_id": game.get("away_team_id"),
            "home_score": game.get("home_score"),
            "away_score": game.get("away_score"),
            "season_type": game.get("season_type"),
            "is_final": game.get("home_score") is not None,
            "matchup": f"Game {game.get('game_id')}",
        }

    def _build_filter_expression(self, filters: dict[str, Any]) -> str:
        expressions = []

        for field, value in filters.items():
            if value is None:
                continue
            if isinstance(value, bool):
                expressions.append(f"{field} = {str(value).lower()}")
            elif isinstance(value, (int, float)):
                expressions.append(f"{field} = {value}")
            elif isinstance(value, str):
                expressions.append(f'{field} = "{value}"')
            elif isinstance(value, list):
                values = ", ".join(
                    f'"{v}"' if isinstance(v, str) else str(v) for v in value
                )
                expressions.append(f"{field} IN [{values}]")

        return " AND ".join(expressions) if expressions else ""
