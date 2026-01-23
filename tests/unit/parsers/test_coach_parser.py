"""Unit tests for CoachParser."""

from unittest import TestCase
from unittest.mock import MagicMock

from src.scraper.parsers.coach import CoachParser


class TestCoachParser(TestCase):
    """Unit tests for CoachParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.team_abbreviation_parser = MagicMock()
        self.parser = CoachParser(
            team_abbreviation_parser=self.team_abbreviation_parser
        )

    def test_parse(self):
        """Test parsing coach page."""
        mock_page = MagicMock()
        mock_page.name = "Phil Jackson"

        mock_row = MagicMock()
        mock_row.season = "1995-96"
        mock_row.team = "CHI"
        mock_row.wins = "72"
        mock_row.losses = "10"
        mock_row.win_pct = ".878"

        mock_page.rows = [mock_row]

        self.team_abbreviation_parser.from_abbreviation.return_value = "CHICAGO_BULLS"

        result = self.parser.parse(mock_page)

        assert result["name"] == "Phil Jackson"
        assert len(result["record"]) == 1
        assert result["record"][0]["season"] == "1995-96"
        assert result["record"][0]["wins"] == 72
        assert result["record"][0]["losses"] == 10
        assert result["record"][0]["win_pct"] == 0.878
        assert result["record"][0]["team"] == "CHICAGO_BULLS"
