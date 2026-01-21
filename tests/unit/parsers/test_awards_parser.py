"""Unit tests for AwardsParser."""

from unittest import TestCase
from unittest.mock import MagicMock

from src.scraper.parsers.awards import AwardsParser


class TestAwardsParser(TestCase):
    """Unit tests for AwardsParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.team_abbreviation_parser = MagicMock()
        self.parser = AwardsParser(team_abbreviation_parser=self.team_abbreviation_parser)

    def test_parse(self):
        """Test parsing awards page."""
        mock_page = MagicMock()
        mock_page.award_name = "Most Valuable Player"
        
        mock_row = MagicMock()
        mock_row.season = "2023-24"
        mock_row.player = "Nikola Jokić"
        mock_row.player_id = "jokicni01"
        mock_row.team = "DEN"
        mock_row.age = "28"
        mock_row.voting_share = "0.926"
        
        mock_page.rows = [mock_row]
        
        self.team_abbreviation_parser.from_abbreviation.return_value = "DENVER_NUGGETS"
        
        result = self.parser.parse(mock_page)
        
        self.assertEqual(result["award"], "Most Valuable Player")
        self.assertEqual(len(result["winners"]), 1)
        self.assertEqual(result["winners"][0]["player"], "Nikola Jokić")
        self.assertEqual(result["winners"][0]["age"], 28)
        self.assertEqual(result["winners"][0]["voting_share"], 0.926)
