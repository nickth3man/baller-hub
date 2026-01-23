"""Unit tests for AllStarParser."""

from unittest import TestCase
from unittest.mock import MagicMock

from src.scraper.parsers.allstar import AllStarParser


class TestAllStarParser(TestCase):
    """Unit tests for AllStarParser class."""

    def test_parse(self):
        """Test parsing All-Star page."""
        mock_page = MagicMock()
        mock_page.mvp = "Giannis Antetokounmpo"

        mock_row_east = MagicMock()
        mock_row_east.player_name = "Joel Embiid"
        mock_row_east.player_id = "embiijo01"
        mock_row_east.points = "30"

        mock_row_west = MagicMock()
        mock_row_west.player_name = "LeBron James"
        mock_row_west.player_id = "jamesle01"
        mock_row_west.points = "25"

        mock_page.east_rows = [mock_row_east]
        mock_page.west_rows = [mock_row_west]

        parser = AllStarParser()
        result = parser.parse(mock_page)

        assert result["mvp"] == "Giannis Antetokounmpo"
        assert len(result["east_roster"]) == 1
        assert result["east_roster"][0]["player"] == "Joel Embiid"
        assert result["east_roster"][0]["points"] == 30
        assert len(result["west_roster"]) == 1
        assert result["west_roster"][0]["player"] == "LeBron James"
        assert result["west_roster"][0]["points"] == 25
