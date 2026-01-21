"""Unit tests for LeadersParser."""

from unittest import TestCase
from unittest.mock import MagicMock

from src.scraper.parsers.leaders import LeadersParser


class TestLeadersParser(TestCase):
    """Unit tests for LeadersParser class."""

    def test_parse(self):
        """Test parsing leaders page."""
        mock_page = MagicMock()
        mock_page.stat_name = "Points"
        
        mock_row = MagicMock()
        mock_row.rank = "1"
        mock_row.player = "LeBron James"
        mock_row.player_id = "jamesle01"
        mock_row.value = "40474"
        
        mock_page.rows = [mock_row]
        
        parser = LeadersParser()
        result = parser.parse(mock_page)
        
        self.assertEqual(result["stat"], "Points")
        self.assertEqual(len(result["leaders"]), 1)
        self.assertEqual(result["leaders"][0]["rank"], 1)
        self.assertEqual(result["leaders"][0]["player"], "LeBron James")
        self.assertEqual(result["leaders"][0]["value"], 40474.0)
        self.assertEqual(result["leaders"][0]["player_id"], "jamesle01")
