"""Parsers for draft page data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.scraper.utils.casting import str_to_int

if TYPE_CHECKING:
    from src.scraper.html.draft import DraftPage


class DraftParser:
    """Parse draft page data into structured dictionaries."""

    def __init__(self, team_abbreviation_parser):
        self.team_abbreviation_parser = team_abbreviation_parser

    def parse(self, page: DraftPage) -> dict:
        """
        Extract draft results.

        Args:
            page (DraftPage): The DraftPage wrapper.

        Returns:
            dict: Structured draft data.
        """
        return {
            "year": str_to_int(page.year),
            "picks": self.parse_picks(page.rows),
        }

    def parse_picks(self, rows) -> list[dict]:
        """
        Parse draft pick rows.

        Args:
            rows (list): List of DraftRow objects.

        Returns:
            list[dict]: Cleaned draft picks.
        """
        return [
            {
                "pick": str_to_int(row.pick),
                "round": str_to_int(row.round_pick),
                "team": self.team_abbreviation_parser.from_abbreviation(row.team),
                "player": row.player,
                "player_id": row.player_id,
                "college": row.college,
                "years_active": str_to_int(row.years_active),
            }
            for row in rows
        ]
