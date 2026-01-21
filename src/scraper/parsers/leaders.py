"""Parsers for leaders page data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.scraper.utils.casting import str_to_float, str_to_int

if TYPE_CHECKING:
    from src.scraper.html.leaders import LeadersPage


class LeadersParser:
    """Parse leaders page data into structured dictionaries."""

    def parse(self, page: LeadersPage) -> dict:
        """
        Extract leaders list.

        Args:
            page: The LeadersPage wrapper.

        Returns:
            dict: Structured leaders data.
        """
        return {
            "stat": page.stat_name,
            "leaders": self.parse_leaders(page.rows),
        }

    def parse_leaders(self, rows) -> list[dict]:
        """
        Parse leader rows.

        Args:
            rows: List of LeaderRow objects.

        Returns:
            list[dict]: Cleaned leader data.
        """
        return [
            {
                "rank": str_to_int(row.rank),
                "player": row.player,
                "player_id": row.player_id,
                "value": str_to_float(row.value),
            }
            for row in rows
        ]
