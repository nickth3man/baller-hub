"""Parsers for coach page data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.scraper.utils.casting import str_to_float, str_to_int

if TYPE_CHECKING:
    from src.scraper.html.coach import CoachPage


class CoachParser:
    """Parse coach page data into structured dictionaries."""

    def __init__(self, team_abbreviation_parser):
        self.team_abbreviation_parser = team_abbreviation_parser

    def parse(self, page: CoachPage) -> dict:
        """
        Extract coach info and coaching record.

        Args:
            page (CoachPage): The CoachPage wrapper.

        Returns:
            dict: Structured coach data.
        """
        return {
            "name": page.name,
            "record": self.parse_record(page.rows),
        }

    def parse_record(self, rows) -> list[dict]:
        """
        Parse coaching record rows.

        Args:
            rows (list): List of CoachingRecordRow objects.

        Returns:
            list[dict]: Cleaned coaching record.
        """
        return [
            {
                "season": row.season,
                "team": self.team_abbreviation_parser.from_abbreviation(row.team)
                if row.team
                else None,
                "wins": str_to_int(row.wins),
                "losses": str_to_int(row.losses),
                "win_pct": str_to_float(row.win_pct),
            }
            for row in rows
            if row.season  # Skip summary/total rows if they don't have a season link
        ]
