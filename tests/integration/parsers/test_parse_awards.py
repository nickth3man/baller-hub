"""Integration tests for Awards parser."""

import os
from unittest import TestCase

from lxml import html

from src.scraper.common.data import TEAM_ABBREVIATIONS_TO_TEAMS, Team
from src.scraper.html.awards import AwardsPage
from src.scraper.parsers.awards import AwardsParser
from src.scraper.parsers.base import TeamAbbreviationParser


class TestAwardsIntegration(TestCase):
    """Integration tests for AwardsParser with real HTML fixtures."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.fixture_dir = os.path.join(
            os.path.dirname(__file__), "../files/awards"
        )
        cls.team_abbreviation_parser = TeamAbbreviationParser(
            abbreviations_to_teams=TEAM_ABBREVIATIONS_TO_TEAMS
        )
        cls.parser = AwardsParser(team_abbreviation_parser=cls.team_abbreviation_parser)

    def _get_page(self, filename: str) -> AwardsPage:
        """Helper to load a fixture and return AwardsPage."""
        path = os.path.join(self.fixture_dir, filename)
        if not os.path.exists(path):
            self.skipTest(f"Fixture {filename} not found")
        with open(path, encoding="utf-8") as f:
            return AwardsPage(html=html.fromstring(f.read()))

    def test_mvp_awards(self):
        """Test parsing MVP award history."""
        page = self._get_page("mvp.html")
        result = self.parser.parse(page)

        self.assertIn("Most Valuable Player", result["award"])
        # Find 2023-24 Jokic
        jokic = next(w for w in result["winners"] if w["season"] == "2023-24")
        self.assertEqual(jokic["player"], "Nikola Jokić")
        self.assertEqual(jokic["team"], Team.DENVER_NUGGETS)
