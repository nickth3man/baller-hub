"""Parsers for team season data."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.scraper.html.team_season import TeamSeasonPage


class TeamSeasonParser:
    """Parse team season data into structured dictionaries."""

    def parse(self, page: TeamSeasonPage) -> dict:
        """
        Extract team season summary.

        Args:
            page: The TeamSeasonPage wrapper.

        Returns:
            dict: Structured team season data.
        """
        return {
            "record": page.record,
            "roster": self.parse_roster(page.roster_rows),
        }

    def parse_roster(self, rows) -> list[dict]:
        """
        Parse roster rows.

        Args:
            rows: List of RosterRow objects.

        Returns:
            list[dict]: Cleaned roster data.
        """
        return [
            {
                "player": row.player_name,
                "player_id": row.player_id,
            }
            for row in rows
        ]
