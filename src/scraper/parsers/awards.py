"""Parsers for awards page data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.scraper.utils.casting import str_to_float, str_to_int

if TYPE_CHECKING:
    from src.scraper.html.awards import AwardsPage


class AwardsParser:
    """Parse awards page data into structured dictionaries."""

    def __init__(self, team_abbreviation_parser):
        self.team_abbreviation_parser = team_abbreviation_parser

    def parse(self, page: AwardsPage) -> dict:
        """
        Extract award winners.

        Args:
            page: The AwardsPage wrapper.

        Returns:
            dict: Structured awards data.
        """
        return {
            "award": page.award_name,
            "winners": self.parse_winners(page.rows),
        }

    def parse_winners(self, rows) -> list[dict]:
        """
        Parse award winner rows.

        Args:
            rows: List of AwardRow objects.

        Returns:
            list[dict]: Cleaned award winners.
        """
        return [
            {
                "season": row.season,
                "player": row.player,
                "player_id": row.player_id,
                "team": self.team_abbreviation_parser.from_abbreviation(row.team) if row.team else None,
                "age": str_to_int(row.age),
                "voting_share": str_to_float(row.voting_share),
            }
            for row in rows
        ]
