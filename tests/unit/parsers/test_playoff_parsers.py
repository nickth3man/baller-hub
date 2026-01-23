"""Unit tests for Playoff parsers."""

from unittest import TestCase
from unittest.mock import MagicMock

from src.scraper.parsers.playoffs import PlayoffSeriesParser, PlayoffsParser


class TestPlayoffsParser(TestCase):
    """Unit tests for PlayoffsParser class."""

    def test_parse(self):
        """Test parsing playoff summary page."""
        mock_page = MagicMock()
        mock_page.champion = "Boston Celtics"
        mock_page.finals_mvp = "Jaylen Brown"
        mock_page.series_links = ["/playoffs/2024-nba-finals.html"]

        parser = PlayoffsParser()
        result = parser.parse(mock_page)

        assert result["champion"] == "Boston Celtics"
        assert result["finals_mvp"] == "Jaylen Brown"
        assert result["series_urls"] == ["/playoffs/2024-nba-finals.html"]


class TestPlayoffSeriesParser(TestCase):
    """Unit tests for PlayoffSeriesParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.team_name_parser = MagicMock()
        self.parser = PlayoffSeriesParser(team_name_parser=self.team_name_parser)

    def test_parse(self):
        """Test parsing playoff series page."""
        mock_page = MagicMock()

        mock_row = MagicMock()
        mock_row.game_number = "1"
        mock_row.date = "Sun, Jun 6, 2024"
        mock_row.home_team = "Boston Celtics"
        mock_row.away_team = "Dallas Mavericks"
        mock_row.score = "107-89"

        mock_page.games = [mock_row]

        self.team_name_parser.from_name.side_effect = [
            "BOSTON_CELTICS",
            "DALLAS_MAVERICKS",
        ]

        result = self.parser.parse(mock_page)

        assert len(result["games"]) == 1
        assert result["games"][0]["game_number"] == 1
        assert result["games"][0]["home_team"] == "BOSTON_CELTICS"
        assert result["games"][0]["away_team"] == "DALLAS_MAVERICKS"
