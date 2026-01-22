"""Integration tests for Draft parser."""

import os
from unittest import TestCase

from lxml import html

from src.core.domain import TEAM_ABBREVIATIONS_TO_TEAM, Team
from src.scraper.html.draft import DraftPage
from src.scraper.parsers.base import TeamAbbreviationParser
from src.scraper.parsers.draft import DraftParser


class TestDraftIntegration(TestCase):
    """Integration tests for DraftParser with real HTML fixtures."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.fixture_dir = os.path.join(
            os.path.dirname(__file__), "../files/draft"
        )
        cls.team_abbreviation_parser = TeamAbbreviationParser(
            abbreviations_to_teams=TEAM_ABBREVIATIONS_TO_TEAM
        )
        cls.parser = DraftParser(team_abbreviation_parser=cls.team_abbreviation_parser)

    def _get_page(self, filename: str) -> DraftPage:
        """Helper to load a fixture and return DraftPage."""
        path = os.path.join(self.fixture_dir, filename)
        if not os.path.exists(path):
            self.skipTest(f"Fixture {filename} not found")
        with open(path, encoding="utf-8") as f:
            return DraftPage(html=html.fromstring(f.read()))

    def test_2003_draft(self):
        """Test parsing 2003 draft (LeBron)."""
        page = self._get_page("2003.html")
        result = self.parser.parse(page)

        self.assertEqual(result["year"], 2003)
        # LeBron was pick 1
        lebron = next(p for p in result["picks"] if p["pick"] == 1)
        self.assertEqual(lebron["player"], "LeBron James")
        self.assertEqual(lebron["team"], Team.CLEVELAND_CAVALIERS)

    def test_1984_draft(self):
        """Test parsing 1984 draft (Jordan)."""
        page = self._get_page("1984.html")
        result = self.parser.parse(page)

        self.assertEqual(result["year"], 1984)
        # Jordan was pick 3
        jordan = next(p for p in result["picks"] if p["pick"] == 3)
        self.assertEqual(jordan["player"], "Michael Jordan")
        self.assertEqual(jordan["team"], Team.CHICAGO_BULLS)
