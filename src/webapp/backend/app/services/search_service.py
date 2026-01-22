"""Search service - full-text and filtered search operations.

This service provides search functionality using Meilisearch for fast
full-text search with typo tolerance and filtering. Falls back to
database search when Meilisearch is unavailable.
"""

from typing import Any

import structlog
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, aliased

from app.models.player import Player, PlayerSeason, SeasonType
from app.models.team import Team
from app.search.indexer import SearchIndexer

logger = structlog.get_logger(__name__)


class SearchService:
    """Service for searching players, teams, and games."""

    def __init__(self, session: Session, use_meilisearch: bool = True):
        self.session = session
        self.use_meilisearch = use_meilisearch
        self._indexer: SearchIndexer | None = None

    @property
    def indexer(self) -> SearchIndexer:
        """Lazy-load the search indexer."""
        if self._indexer is None:
            self._indexer = SearchIndexer()
        return self._indexer

    def search(
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

        # Fallback to database search
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
        player_result = self.session.execute(player_query)

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
        team_result = self.session.execute(team_query)

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

    def search_players(
        self,
        query: str,
        position: str | None = None,
        team_abbrev: str | None = None,
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
        if self.use_meilisearch and team_abbrev is None:
            try:
                filters = {}
                if position:
                    filters["position"] = position
                if active_only:
                    filters["is_active"] = True

                results = self.indexer.search_players(query, limit, filters)
                return [
                    self._normalize_player_hit(hit) for hit in results.get("hits", [])
                ]
            except Exception as e:
                logger.warning("Meilisearch player search failed", error=str(e))

        # Fallback to database
        players = self._db_search_players(
            query, limit, position, active_only, team_abbrev
        )
        return [self._normalize_player_model(p) for p in players]

    def search_teams(
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
                return [self._normalize_team_hit(hit) for hit in hits]
            except Exception as e:
                logger.warning("Meilisearch team search failed", error=str(e))

        teams = self._db_search_teams(query, limit, active_only)
        return [self._normalize_team_model(t) for t in teams]

    def search_games(
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

        home_team = aliased(Team)
        away_team = aliased(Team)
        query = (
            select(Game, home_team.abbreviation, away_team.abbreviation)
            .join(home_team, Game.home_team_id == home_team.team_id)
            .join(away_team, Game.away_team_id == away_team.team_id)
        )

        if team1:
            # Get team ID from abbreviation
            team_query = select(Team.team_id).where(Team.abbreviation == team1.upper())
            team_result = self.session.execute(team_query)
            team_id = team_result.scalar_one_or_none()

            if team_id:
                query = query.where(
                    (Game.home_team_id == team_id) | (Game.away_team_id == team_id)
                )

        if team2:
            team_query = select(Team.team_id).where(Team.abbreviation == team2.upper())
            team_result = self.session.execute(team_query)
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
        result = self.session.execute(query)
        rows = result.all()

        return [
            self._game_to_dict(game, home_abbrev, away_abbrev)
            for game, home_abbrev, away_abbrev in rows
        ]

    # Private database fallback methods
    def _db_search_players(
        self,
        query: str,
        limit: int,
        position: str | None = None,
        active_only: bool = False,
        team_abbrev: str | None = None,
    ) -> list[Player]:
        """Database fallback for player search."""
        player_query = select(Player).where(
            or_(
                Player.first_name.ilike(f"%{query}%"),
                Player.last_name.ilike(f"%{query}%"),
            )
        )

        if active_only:
            player_query = player_query.where(Player.is_active)
        if position:
            player_query = player_query.where(Player.position == position)
        if team_abbrev:
            player_ids = (
                select(PlayerSeason.player_id)
                .join(Team, PlayerSeason.team_id == Team.team_id)
                .where(Team.abbreviation == team_abbrev.upper())
                .where(PlayerSeason.season_type == SeasonType.REGULAR)
                .distinct()
            )
            player_query = player_query.where(Player.player_id.in_(player_ids))

        player_query = player_query.limit(limit)
        result = self.session.execute(player_query)
        return list(result.scalars().all())

    def _db_search_teams(
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
            team_query = team_query.where(Team.is_active)

        team_query = team_query.limit(limit)
        result = self.session.execute(team_query)
        return list(result.scalars().all())

    # Serialization helpers
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

    def _normalize_player_hit(self, hit: dict[str, Any]) -> dict[str, Any]:
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

    def _normalize_team_hit(self, hit: dict[str, Any]) -> dict[str, Any]:
        return {
            "team_id": hit.get("team_id"),
            "abbreviation": hit.get("abbreviation"),
            "name": hit.get("name"),
            "city": hit.get("city"),
            "is_active": hit.get("is_active", True),
        }

    def _normalize_game_hit(self, hit: dict[str, Any]) -> dict[str, Any]:
        score = None
        if hit.get("away_score") is not None and hit.get("home_score") is not None:
            score = f"{hit.get('away_score')}-{hit.get('home_score')}"
        return {
            "game_id": hit.get("game_id"),
            "game_date": hit.get("game_date") or hit.get("date"),
            "matchup": hit.get("matchup") or f"Game {hit.get('game_id')}",
            "score": score,
        }

    def _normalize_player_model(self, player: Player) -> dict[str, Any]:
        return {
            "player_id": player.player_id,
            "slug": player.slug,
            "full_name": player.full_name,
            "name": player.full_name,
            "position": player.position.value if player.position else None,
            "years_active": self._format_years_active(
                player.debut_year, player.final_year, player.is_active
            ),
            "is_active": player.is_active,
        }

    def _normalize_team_model(self, team: Team) -> dict[str, Any]:
        return {
            "team_id": team.team_id,
            "abbreviation": team.abbreviation,
            "name": team.name,
            "city": team.city,
            "is_active": team.is_active,
        }

    def _game_to_dict(
        self, game, home_abbrev: str | None = None, away_abbrev: str | None = None
    ) -> dict[str, Any]:
        score = None
        if game.home_score is not None and game.away_score is not None:
            score = f"{game.away_score}-{game.home_score}"
        matchup = f"Game {game.game_id}"
        if home_abbrev and away_abbrev:
            matchup = f"{away_abbrev} @ {home_abbrev}"
        return {
            "game_id": game.game_id,
            "game_date": game.game_date.isoformat() if game.game_date else None,
            "matchup": matchup,
            "score": score,
        }
