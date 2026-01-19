"""Meilisearch indexer for syncing database records to search indices."""

from typing import Any

import structlog
from meilisearch import Client
from meilisearch.errors import MeilisearchApiError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import Game
from app.models.player import Player
from app.models.team import Team
from app.search.client import (
    GAMES_INDEX,
    INDEX_CONFIGS,
    PLAYERS_INDEX,
    TEAMS_INDEX,
    get_meilisearch_client,
)

logger = structlog.get_logger(__name__)


class SearchIndexer:
    """Service for indexing database records into Meilisearch."""

    def __init__(self, client: Client | None = None):
        self.client = client or get_meilisearch_client()

    def setup_indices(self) -> None:
        """Create and configure all search indices.

        Should be called during application startup or migration.
        """
        for index_name, config in INDEX_CONFIGS.items():
            logger.info("Setting up index", index=index_name)

            try:
                # Create index if it doesn't exist
                self.client.create_index(
                    index_name,
                    {"primaryKey": config["primaryKey"]},
                )
            except MeilisearchApiError as e:
                if "index_already_exists" not in str(e):
                    raise
                logger.info("Index already exists", index=index_name)

            # Update settings
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

    async def index_players(self, session: AsyncSession, batch_size: int = 1000) -> int:
        """Index all players from the database.

        Args:
            session: Database session.
            batch_size: Number of records per batch.

        Returns:
            Total number of indexed documents.
        """
        logger.info("Starting player indexing")

        query = select(Player).order_by(Player.player_id)
        result = await session.execute(query)
        players = result.scalars().all()

        documents = [self._player_to_document(p) for p in players]

        if documents:
            index = self.client.index(PLAYERS_INDEX)
            index.add_documents(documents, primary_key="player_id")
            logger.info("Indexed players", count=len(documents))

        return len(documents)

    async def index_teams(self, session: AsyncSession) -> int:
        """Index all teams from the database.

        Args:
            session: Database session.

        Returns:
            Total number of indexed documents.
        """
        logger.info("Starting team indexing")

        query = select(Team).order_by(Team.team_id)
        result = await session.execute(query)
        teams = result.scalars().all()

        documents = [self._team_to_document(t) for t in teams]

        if documents:
            index = self.client.index(TEAMS_INDEX)
            index.add_documents(documents, primary_key="team_id")
            logger.info("Indexed teams", count=len(documents))

        return len(documents)

    async def index_games(
        self,
        session: AsyncSession,
        season_year: int | None = None,
        batch_size: int = 1000,
    ) -> int:
        """Index games from the database.

        Args:
            session: Database session.
            season_year: Optional filter by season.
            batch_size: Number of records per batch.

        Returns:
            Total number of indexed documents.
        """
        logger.info("Starting game indexing", season_year=season_year)

        query = select(Game).order_by(Game.game_id)

        # TODO: Add season filter when we have the join logic

        result = await session.execute(query)
        games = result.scalars().all()

        documents = [self._game_to_document(g) for g in games]

        if documents:
            index = self.client.index(GAMES_INDEX)
            index.add_documents(documents, primary_key="game_id")
            logger.info("Indexed games", count=len(documents))

        return len(documents)

    async def index_single_player(self, player: Player) -> None:
        """Index or update a single player.

        Args:
            player: Player model instance.
        """
        document = self._player_to_document(player)
        index = self.client.index(PLAYERS_INDEX)
        index.add_documents([document], primary_key="player_id")

    async def index_single_team(self, team: Team) -> None:
        """Index or update a single team.

        Args:
            team: Team model instance.
        """
        document = self._team_to_document(team)
        index = self.client.index(TEAMS_INDEX)
        index.add_documents([document], primary_key="team_id")

    async def index_single_game(self, game: Game) -> None:
        """Index or update a single game.

        Args:
            game: Game model instance.
        """
        document = self._game_to_document(game)
        index = self.client.index(GAMES_INDEX)
        index.add_documents([document], primary_key="game_id")

    def delete_player(self, player_id: int) -> None:
        """Remove a player from the search index.

        Args:
            player_id: Player ID to remove.
        """
        index = self.client.index(PLAYERS_INDEX)
        index.delete_document(player_id)

    def delete_team(self, team_id: int) -> None:
        """Remove a team from the search index.

        Args:
            team_id: Team ID to remove.
        """
        index = self.client.index(TEAMS_INDEX)
        index.delete_document(team_id)

    def search_players(
        self,
        query: str,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Search for players.

        Args:
            query: Search query string.
            limit: Maximum results.
            filters: Optional Meilisearch filter expressions.

        Returns:
            Meilisearch search response.
        """
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
        """Search for teams.

        Args:
            query: Search query string.
            limit: Maximum results.

        Returns:
            Meilisearch search response.
        """
        index = self.client.index(TEAMS_INDEX)
        return index.search(query, {"limit": limit})

    def search_all(
        self,
        query: str,
        limit_per_index: int = 5,
    ) -> dict[str, list[dict[str, Any]]]:
        """Search across all indices.

        Args:
            query: Search query string.
            limit_per_index: Maximum results per index.

        Returns:
            Dictionary with results from each index.
        """
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
        """Get autocomplete suggestions for a search query.

        Searches players and teams, returns combined results
        formatted for autocomplete UI.

        Args:
            query: Partial search query.
            limit: Maximum total suggestions.

        Returns:
            List of suggestion dictionaries.
        """
        suggestions = []

        # Search players
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

        # Search teams
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

    # Private helper methods
    def _player_to_document(self, player: Player) -> dict[str, Any]:
        """Convert Player model to search document."""
        return {
            "player_id": player.player_id,
            "slug": player.slug,
            "first_name": player.first_name,
            "last_name": player.last_name,
            "full_name": player.full_name,
            "position": player.position.value if player.position else None,
            "is_active": player.is_active,
            "college": player.college,
            "draft_year": player.draft_year,
            "debut_year": player.debut_year,
        }

    def _team_to_document(self, team: Team) -> dict[str, Any]:
        """Convert Team model to search document."""
        return {
            "team_id": team.team_id,
            "name": team.name,
            "city": team.city,
            "abbreviation": team.abbreviation,
            "full_name": f"{team.city} {team.name}",
            "is_active": team.is_active,
            # TODO: Add conference/division when relationship is available
        }

    def _game_to_document(self, game: Game) -> dict[str, Any]:
        """Convert Game model to search document."""
        return {
            "game_id": game.game_id,
            "game_date": game.game_date.isoformat() if game.game_date else None,
            "home_team_id": game.home_team_id,
            "away_team_id": game.away_team_id,
            "home_score": game.home_score,
            "away_score": game.away_score,
            "season_type": game.season_type,
            "is_final": game.home_score is not None,
            # TODO: Add team names when we have the join
            "matchup": f"Game {game.game_id}",
        }

    def _build_filter_expression(self, filters: dict[str, Any]) -> str:
        """Build Meilisearch filter expression from dict.

        Args:
            filters: Dictionary of field -> value filters.

        Returns:
            Meilisearch filter expression string.
        """
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
                # IN filter
                values = ", ".join(
                    f'"{v}"' if isinstance(v, str) else str(v) for v in value
                )
                expressions.append(f"{field} IN [{values}]")

        return " AND ".join(expressions) if expressions else ""
