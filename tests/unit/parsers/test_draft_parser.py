"""Unit tests for DraftParser."""

from unittest import TestCase
from unittest.mock import MagicMock

from src.scraper.parsers.draft import DraftParser


class TestDraftParser(TestCase):
    """Unit tests for DraftParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.team_abbreviation_parser = MagicMock()
        self.parser = DraftParser(team_abbreviation_parser=self.team_abbreviation_parser)

    def test_parse(self):
        """Test parsing draft page."""
        mock_page = MagicMock()
        mock_page.year = "2024"
        
        mock_row = MagicMock()
        mock_row.pick = "1"
        mock_row.round_pick = "1"
        mock_row.team = "ATL"
        mock_row.player = "Zaccharie Risacher"
        mock_row.player_id = "risacza01"
        mock_row.college = "JL Bourg"
        mock_row.years_active = "1"
        
        mock_page.rows = [mock_row]
        
        self.team_abbreviation_parser.from_abbreviation.return_value = "ATLANTA_HAWKS"
        
        result = self.parser.parse(mock_page)
        
        self.assertEqual(result["year"], 2024)
        self.assertEqual(len(result["picks"]), 1)
        self.assertEqual(result["picks"][0]["pick"], 1)
        self.assertEqual(result["picks"][0]["player"], "Zaccharie Risacher")
        self.assertEqual(result["picks"][0]["team"], "ATLANTA_HAWKS")
