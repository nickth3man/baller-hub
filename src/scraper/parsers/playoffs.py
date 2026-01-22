"""Parsers for playoff page data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.scraper.utils.casting import str_to_int

if TYPE_CHECKING:
    from src.scraper.html.playoffs import PlayoffSeriesPage, PlayoffsPage


class PlayoffsParser:
    """Parse playoff summary page data."""

    def parse(self, page: PlayoffsPage) -> dict:
        """
        Extract playoff summary info.

        Args:
            page: The PlayoffsPage wrapper.

        Returns:
            dict: Structured playoff summary.
        """
        return {
            "champion": page.champion,
            "finals_mvp": page.finals_mvp,
            "series_urls": page.series_links,
        }


class PlayoffSeriesParser:
    """Parse individual playoff series data."""

    def __init__(self, team_name_parser):
        self.team_name_parser = team_name_parser

    def parse(self, page: PlayoffSeriesPage) -> dict:
        """
        Extract series details and games.

        Args:
            page: The PlayoffSeriesPage wrapper.

        Returns:
            dict: Structured series data.
        """
        return {
            "games": self.parse_games(page.games),
        }

    def parse_games(self, rows) -> list[dict]:
        """
        Parse playoff game rows.

        Args:
            rows: List of PlayoffGameRow objects.

        Returns:
            list[dict]: Cleaned game data.
        """
        return [
            {
                "game_number": str_to_int(row.game_number),
                "date": row.date,
                "home_team": self.team_name_parser.from_name(row.home_team),
                "away_team": self.team_name_parser.from_name(row.away_team),
                "score": row.score,
            }
            for row in rows
        ]
