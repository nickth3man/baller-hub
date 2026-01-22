"""Unit tests for TeamSeasonParser."""

from unittest import TestCase
from unittest.mock import MagicMock

from src.scraper.parsers.team_season import TeamSeasonParser


class TestTeamSeasonParser(TestCase):
    """Unit tests for TeamSeasonParser class."""

    def test_parse(self):
        """Test parsing team season page."""
        mock_page = MagicMock()
        mock_page.record = "64-18"

        mock_row = MagicMock()
        mock_row.player_name = "Jayson Tatum"
        mock_row.player_id = "tatumja01"

        mock_page.roster_rows = [mock_row]

        parser = TeamSeasonParser()
        result = parser.parse(mock_page)

        self.assertEqual(result["record"], "64-18")
        self.assertEqual(len(result["roster"]), 1)
        self.assertEqual(result["roster"][0]["player"], "Jayson Tatum")
        self.assertEqual(result["roster"][0]["player_id"], "tatumja01")
