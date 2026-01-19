"""Scraper service that wraps the existing scraper client.

This service provides an async-friendly interface to the basketball-reference-scraper
library, handling rate limiting and caching at the ingestion layer.
"""

import asyncio
from datetime import date
from typing import Any

import structlog

# Import from the existing scraper
import sys

sys.path.insert(0, str(__file__).split("webapp")[0])

from src.api import client as scraper_client
from src.common.data import Team as ScraperTeam
from src.common.errors import InvalidDate, InvalidPlayerAndSeason, InvalidSeason

logger = structlog.get_logger(__name__)


class ScraperService:
    """Service wrapper for the basketball-reference scraper.

    Provides async methods that delegate to the synchronous scraper,
    running blocking operations in a thread pool.
    """

    def __init__(self, rate_limit_seconds: float = 3.0):
        self.rate_limit_seconds = rate_limit_seconds
        self._last_request_time: float = 0

    async def _run_sync(self, func, *args, **kwargs) -> Any:
        """Run a synchronous function in a thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    async def get_player_box_scores(
        self, day: int, month: int, year: int
    ) -> list[dict[str, Any]]:
        """Get all player box scores for a specific date.

        Returns stats for every player who played in any game on the specified day.

        Args:
            day: Day of the month (1-31).
            month: Month number (1-12).
            year: 4-digit year.

        Returns:
            List of box score dictionaries.

        Raises:
            InvalidDate: If the date has no games or is invalid.
        """
        logger.info(
            "Fetching player box scores",
            day=day,
            month=month,
            year=year,
        )
        try:
            result = await self._run_sync(
                scraper_client.player_box_scores,
                day=day,
                month=month,
                year=year,
            )
            logger.info("Fetched player box scores", count=len(result))
            return result
        except InvalidDate:
            logger.warning("No games found for date", day=day, month=month, year=year)
            return []

    async def get_team_box_scores(
        self, day: int, month: int, year: int
    ) -> list[dict[str, Any]]:
        """Get team-level stats for all games on a specific date.

        Args:
            day: Day of the month.
            month: Month number.
            year: 4-digit year.

        Returns:
            List of team box score dictionaries.
        """
        logger.info("Fetching team box scores", day=day, month=month, year=year)
        try:
            result = await self._run_sync(
                scraper_client.team_box_scores,
                day=day,
                month=month,
                year=year,
            )
            logger.info("Fetched team box scores", count=len(result))
            return result
        except InvalidDate:
            logger.warning("No games found for date", day=day, month=month, year=year)
            return []

    async def get_season_schedule(self, season_end_year: int) -> list[dict[str, Any]]:
        """Get the full schedule for a season.

        Args:
            season_end_year: The year the season ends (e.g., 2024 for 2023-24).

        Returns:
            List of game dictionaries containing date, teams, and scores.

        Raises:
            InvalidSeason: If the season is invalid.
        """
        logger.info("Fetching season schedule", season_end_year=season_end_year)
        try:
            result = await self._run_sync(
                scraper_client.season_schedule,
                season_end_year=season_end_year,
            )
            logger.info("Fetched season schedule", count=len(result))
            return result
        except InvalidSeason:
            logger.warning("Invalid season", season_end_year=season_end_year)
            return []

    async def get_standings(self, season_end_year: int) -> dict[str, Any]:
        """Get team standings for a specific season.

        Args:
            season_end_year: The year the season ends.

        Returns:
            Dictionary containing standings data.

        Raises:
            InvalidSeason: If the season is invalid.
        """
        logger.info("Fetching standings", season_end_year=season_end_year)
        try:
            result = await self._run_sync(
                scraper_client.standings,
                season_end_year=season_end_year,
            )
            logger.info("Fetched standings")
            return result
        except InvalidSeason:
            logger.warning("Invalid season", season_end_year=season_end_year)
            return {}

    async def get_players_season_totals(
        self, season_end_year: int
    ) -> list[dict[str, Any]]:
        """Get aggregated season totals for all players.

        Args:
            season_end_year: The year the season ends.

        Returns:
            List of player totals.
        """
        logger.info("Fetching player season totals", season_end_year=season_end_year)
        try:
            result = await self._run_sync(
                scraper_client.players_season_totals,
                season_end_year=season_end_year,
            )
            logger.info("Fetched player season totals", count=len(result))
            return result
        except InvalidSeason:
            logger.warning("Invalid season", season_end_year=season_end_year)
            return []

    async def get_players_advanced_season_totals(
        self, season_end_year: int, include_combined_values: bool = False
    ) -> list[dict[str, Any]]:
        """Get advanced stats for all players.

        Args:
            season_end_year: The year the season ends.
            include_combined_values: Include combined row for multi-team players.

        Returns:
            List of advanced player stats.
        """
        logger.info(
            "Fetching player advanced season totals", season_end_year=season_end_year
        )
        try:
            result = await self._run_sync(
                scraper_client.players_advanced_season_totals,
                season_end_year=season_end_year,
                include_combined_values=include_combined_values,
            )
            logger.info("Fetched player advanced season totals", count=len(result))
            return result
        except InvalidSeason:
            logger.warning("Invalid season", season_end_year=season_end_year)
            return []

    async def get_regular_season_player_box_scores(
        self,
        player_identifier: str,
        season_end_year: int,
        include_inactive_games: bool = False,
    ) -> list[dict[str, Any]]:
        """Get all regular season box scores for a specific player.

        Args:
            player_identifier: Player ID (e.g., 'jamesle01').
            season_end_year: The year the season ends.
            include_inactive_games: Include DNP games.

        Returns:
            List of game logs.
        """
        logger.info(
            "Fetching player regular season box scores",
            player_identifier=player_identifier,
            season_end_year=season_end_year,
        )
        try:
            result = await self._run_sync(
                scraper_client.regular_season_player_box_scores,
                player_identifier=player_identifier,
                season_end_year=season_end_year,
                include_inactive_games=include_inactive_games,
            )
            logger.info(
                "Fetched player regular season box scores",
                player_identifier=player_identifier,
                count=len(result),
            )
            return result
        except InvalidPlayerAndSeason:
            logger.warning(
                "Invalid player/season combo",
                player_identifier=player_identifier,
                season_end_year=season_end_year,
            )
            return []

    async def get_play_by_play(
        self, home_team: str, day: int, month: int, year: int
    ) -> list[dict[str, Any]]:
        """Get the full play-by-play log for a single game.

        Args:
            home_team: Team abbreviation for the home team (e.g., 'BOS').
            day: Day of the month.
            month: Month number.
            year: 4-digit year.

        Returns:
            List of plays.
        """
        logger.info(
            "Fetching play-by-play",
            home_team=home_team,
            day=day,
            month=month,
            year=year,
        )
        try:
            # Convert abbreviation to ScraperTeam enum
            team_enum = self._get_team_enum(home_team)
            if team_enum is None:
                logger.warning("Unknown team abbreviation", home_team=home_team)
                return []

            result = await self._run_sync(
                scraper_client.play_by_play,
                home_team=team_enum,
                day=day,
                month=month,
                year=year,
            )
            logger.info("Fetched play-by-play", count=len(result))
            return result
        except InvalidDate:
            logger.warning(
                "No game found", home_team=home_team, day=day, month=month, year=year
            )
            return []

    async def search(self, term: str) -> dict[str, Any]:
        """Search for a player or team.

        Args:
            term: Search query.

        Returns:
            Search results dictionary.
        """
        logger.info("Searching", term=term)
        result = await self._run_sync(scraper_client.search, term=term)
        return result

    def _get_team_enum(self, abbreviation: str) -> ScraperTeam | None:
        """Convert team abbreviation to ScraperTeam enum."""
        try:
            from src.common.data import TEAM_ABBREVIATIONS_TO_TEAM

            return TEAM_ABBREVIATIONS_TO_TEAM.get(abbreviation)
        except (ImportError, KeyError):
            return None
