"""Integration tests for Coach parser."""

import os
from unittest import TestCase

from lxml import html

from src.scraper.common.data import TEAM_ABBREVIATIONS_TO_TEAMS, Team
from src.scraper.html.coach import CoachPage
from src.scraper.parsers.base import TeamAbbreviationParser
from src.scraper.parsers.coach import CoachParser


class TestCoachIntegration(TestCase):
    """Integration tests for CoachParser with real HTML fixtures."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.fixture_dir = os.path.join(
            os.path.dirname(__file__), "../files/coaches"
        )
        cls.team_abbreviation_parser = TeamAbbreviationParser(
            abbreviations_to_teams=TEAM_ABBREVIATIONS_TO_TEAMS
        )
        cls.parser = CoachParser(team_abbreviation_parser=cls.team_abbreviation_parser)

    def _get_page(self, filename: str) -> CoachPage:
        """Helper to load a fixture and return CoachPage."""
        path = os.path.join(self.fixture_dir, filename)
        if not os.path.exists(path):
            self.skipTest(f"Fixture {filename} not found")
        with open(path, encoding="utf-8") as f:
            return CoachPage(html=html.fromstring(f.read()))

    def test_phil_jackson(self):
        """Test parsing Phil Jackson's page."""
        page = self._get_page("jacksph01c.html")
        result = self.parser.parse(page)

        self.assertEqual(result["name"], "Phil Jackson")
        # Find 1995-96 Bulls season
        bulls_72 = next(r for r in result["record"] if r["season"] == "1995-96")
        self.assertEqual(bulls_72["team"], Team.CHICAGO_BULLS)
        self.assertEqual(bulls_72["wins"], 72)
        self.assertEqual(bulls_72["losses"], 10)

    def test_gregg_popovich(self):
        """Test parsing Gregg Popovich's page."""
        page = self._get_page("popovgr01c.html")
        result = self.parser.parse(page)

        self.assertEqual(result["name"], "Gregg Popovich")
        # Popovich has coached for many seasons
        self.assertTrue(len(result["record"]) > 20)
