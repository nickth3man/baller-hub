"""Parsers for All-Star game data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.scraper.utils.casting import str_to_int

if TYPE_CHECKING:
    from src.scraper.html.allstar import AllStarPage


class AllStarParser:
    """Parse All-Star game data into structured dictionaries."""

    def parse(self, page: AllStarPage) -> dict:
        """
        Extract All-Star game results and rosters.

        Args:
            page (AllStarPage): The AllStarPage wrapper.

        Returns:
            dict: Structured All-Star data containing 'mvp', 'east_roster', and 'west_roster'.
        """
        return {
            "mvp": page.mvp,
            "east_roster": self.parse_roster(page.east_rows),
            "west_roster": self.parse_roster(page.west_rows),
        }

    def parse_roster(self, rows) -> list[dict]:
        """
        Parse All-Star roster rows.

        Args:
            rows (list): List of AllStarPlayerRow objects.

        Returns:
            list[dict]: Cleaned roster data.
        """
        return [
            {
                "player": row.player_name,
                "player_id": row.player_id,
                "points": str_to_int(row.points),
            }
            for row in rows
        ]
