"""Search service - full-text and filtered search operations.

This service provides search functionality using Meilisearch for fast
full-text search with typo tolerance and filtering. Falls back to
database search when Meilisearch is unavailable.
"""

from typing import Any

import structlog
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player import Player
from app.models.team import Team
from app.search.indexer import SearchIndexer

logger = structlog.get_logger(__name__)


class SearchService:
    """Service for searching players, teams, and games."""

    def __init__(self, session: AsyncSession, use_meilisearch: bool = True):
        self.session = session
        self.use_meilisearch = use_meilisearch
        self._indexer: SearchIndexer | None = None

    @property
    def indexer(self) -> SearchIndexer:
        """Lazy-load the search indexer."""
        if self._indexer is None:
            self._indexer = SearchIndexer()
        return self._indexer

    async def search(
        self,
        query: str,
        entity_type: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Search across all entities.

        Args:
            query: Search query string.
            entity_type: Optional filter (player, team, game).
            limit: Maximum results per entity type.

        Returns:
            Dictionary with results by entity type.
        """
        results: dict[str, Any] = {
            "query": query,
            "players": [],
            "teams": [],
            "games": [],
            "total_results": 0,
        }

        # Try Meilisearch first
        if self.use_meilisearch:
            try:
                meili_results = self.indexer.search_all(query, limit_per_index=limit)

                if entity_type is None or entity_type == "player":
                    results["players"] = meili_results.get("players", [])
                if entity_type is None or entity_type == "team":
                    results["teams"] = meili_results.get("teams", [])
                if entity_type is None or entity_type == "game":
                    results["games"] = meili_results.get("games", [])

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

        # Fallback to database search
        if entity_type is None or entity_type == "player":
            players = await self._db_search_players(query, limit)
            results["players"] = [self._player_to_dict(p) for p in players]

        if entity_type is None or entity_type == "team":
            teams = await self._db_search_teams(query, limit)
            results["teams"] = [self._team_to_dict(t) for t in teams]

        results["total_results"] = len(results["players"]) + len(results["teams"])
        return results

    async def autocomplete(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Get autocomplete suggestions for a search query.

        Args:
            query: Partial search query.
            limit: Maximum suggestions.

        Returns:
            Dictionary with suggestions list.
        """
        if self.use_meilisearch:
            try:
                suggestions = self.indexer.get_autocomplete_suggestions(query, limit)
                return {"query": query, "suggestions": suggestions}
            except Exception as e:
                logger.warning("Meilisearch autocomplete failed", error=str(e))

        # Fallback to database
        suggestions = []

        # Search players
        player_query = (
            select(Player).where(Player.last_name.ilike(f"{query}%")).limit(limit // 2)
        )
        player_result = await self.session.execute(player_query)

        for player in player_result.scalars():
            suggestions.append(
                {
                    "type": "player",
                    "id": player.player_id,
                    "slug": player.slug,
                    "text": player.full_name,
                    "subtitle": player.position.value.replace("_", " ")
                    if player.position
                    else "",
                    "url": f"/players/{player.slug}",
                }
            )

        # Search teams
        team_query = select(Team).where(Team.name.ilike(f"%{query}%")).limit(limit // 2)
        team_result = await self.session.execute(team_query)

        for team in team_result.scalars():
            suggestions.append(
                {
                    "type": "team",
                    "id": team.team_id,
                    "text": f"{team.city} {team.name}",
                    "subtitle": team.abbreviation,
                    "url": f"/teams/{team.abbreviation}",
                }
            )

        return {"query": query, "suggestions": suggestions}

    async def search_players(
        self,
        query: str,
        position: str | None = None,
        active_only: bool = False,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search for players with filters.

        Args:
            query: Search query.
            position: Filter by position.
            active_only: Only return active players.
            limit: Maximum results.

        Returns:
            List of player dictionaries.
        """
        if self.use_meilisearch:
            try:
                filters = {}
                if position:
                    filters["position"] = position
                if active_only:
                    filters["is_active"] = True

                results = self.indexer.search_players(query, limit, filters)
                return results.get("hits", [])
            except Exception as e:
                logger.warning("Meilisearch player search failed", error=str(e))

        # Fallback to database
        players = await self._db_search_players(query, limit, position, active_only)
        return [self._player_to_dict(p) for p in players]

    async def search_teams(
        self,
        query: str,
        active_only: bool = True,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search for teams.

        Args:
            query: Search query.
            active_only: Only return active teams.
            limit: Maximum results.

        Returns:
            List of team dictionaries.
        """
        if self.use_meilisearch:
            try:
                results = self.indexer.search_teams(query, limit)
                hits = results.get("hits", [])
                if active_only:
                    hits = [h for h in hits if h.get("is_active", True)]
                return hits
            except Exception as e:
                logger.warning("Meilisearch team search failed", error=str(e))

        teams = await self._db_search_teams(query, limit, active_only)
        return [self._team_to_dict(t) for t in teams]

    async def search_games(
        self,
        team1: str | None = None,
        team2: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        min_score: int | None = None,
        playoff: bool | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Search for games with filters.

        Args:
            team1: First team abbreviation.
            team2: Second team abbreviation.
            date_from: Start date (YYYY-MM-DD).
            date_to: End date (YYYY-MM-DD).
            min_score: Minimum combined score.
            playoff: Filter for playoff games only.
            limit: Maximum results.

        Returns:
            List of game dictionaries.
        """
        from datetime import date
        from app.models.game import Game

        query = select(Game)

        if team1:
            # Get team ID from abbreviation
            team_query = select(Team.team_id).where(Team.abbreviation == team1.upper())
            team_result = await self.session.execute(team_query)
            team_id = team_result.scalar_one_or_none()

            if team_id:
                query = query.where(
                    (Game.home_team_id == team_id) | (Game.away_team_id == team_id)
                )

        if team2:
            team_query = select(Team.team_id).where(Team.abbreviation == team2.upper())
            team_result = await self.session.execute(team_query)
            team_id = team_result.scalar_one_or_none()

            if team_id:
                query = query.where(
                    (Game.home_team_id == team_id) | (Game.away_team_id == team_id)
                )

        if date_from:
            query = query.where(Game.game_date >= date.fromisoformat(date_from))

        if date_to:
            query = query.where(Game.game_date <= date.fromisoformat(date_to))

        if min_score:
            query = query.where((Game.home_score + Game.away_score) >= min_score)

        if playoff is not None:
            if playoff:
                query = query.where(Game.season_type == "PLAYOFF")
            else:
                query = query.where(Game.season_type == "REGULAR")

        query = query.order_by(Game.game_date.desc()).limit(limit)
        result = await self.session.execute(query)
        games = result.scalars().all()

        return [self._game_to_dict(g) for g in games]

    # Private database fallback methods
    async def _db_search_players(
        self,
        query: str,
        limit: int,
        position: str | None = None,
        active_only: bool = False,
    ) -> list[Player]:
        """Database fallback for player search."""
        player_query = select(Player).where(
            or_(
                Player.first_name.ilike(f"%{query}%"),
                Player.last_name.ilike(f"%{query}%"),
            )
        )

        if active_only:
            player_query = player_query.where(Player.is_active == True)
        if position:
            player_query = player_query.where(Player.position == position)

        player_query = player_query.limit(limit)
        result = await self.session.execute(player_query)
        return list(result.scalars().all())

    async def _db_search_teams(
        self,
        query: str,
        limit: int,
        active_only: bool = True,
    ) -> list[Team]:
        """Database fallback for team search."""
        team_query = select(Team).where(
            or_(
                Team.name.ilike(f"%{query}%"),
                Team.city.ilike(f"%{query}%"),
                Team.abbreviation.ilike(f"%{query}%"),
            )
        )

        if active_only:
            team_query = team_query.where(Team.is_active == True)

        team_query = team_query.limit(limit)
        result = await self.session.execute(team_query)
        return list(result.scalars().all())

    # Serialization helpers
    def _player_to_dict(self, player: Player) -> dict[str, Any]:
        """Convert Player to dict for search results."""
        return {
            "player_id": player.player_id,
            "slug": player.slug,
            "full_name": player.full_name,
            "first_name": player.first_name,
            "last_name": player.last_name,
            "position": player.position.value if player.position else None,
            "is_active": player.is_active,
        }

    def _team_to_dict(self, team: Team) -> dict[str, Any]:
        """Convert Team to dict for search results."""
        return {
            "team_id": team.team_id,
            "name": team.name,
            "city": team.city,
            "abbreviation": team.abbreviation,
            "full_name": f"{team.city} {team.name}",
            "is_active": team.is_active,
        }

    def _game_to_dict(self, game) -> dict[str, Any]:
        """Convert Game to dict for search results."""
        return {
            "game_id": game.game_id,
            "date": game.game_date.isoformat() if game.game_date else None,
            "home_team_id": game.home_team_id,
            "away_team_id": game.away_team_id,
            "home_score": game.home_score,
            "away_score": game.away_score,
            "season_type": game.season_type,
        }
