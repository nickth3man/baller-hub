"""Unit tests for AllStarPage HTML wrapper."""

from unittest import TestCase
from unittest.mock import MagicMock


class TestAllStarPage(TestCase):
    """Unit tests for AllStarPage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_box_score_tables_query(self):
        """Test xpath query for box score tables."""
        from src.scraper.html.allstar import AllStarPage

        page = AllStarPage(html=self.html)
        self.assertIn("stats_table", page.box_score_tables_query)

    def test_east_roster_query(self):
        """Test xpath query for East roster."""
        from src.scraper.html.allstar import AllStarPage

        page = AllStarPage(html=self.html)
        self.assertIsNotNone(page.east_roster_query)

    def test_west_roster_query(self):
        """Test xpath query for West roster."""
        from src.scraper.html.allstar import AllStarPage

        page = AllStarPage(html=self.html)
        self.assertIsNotNone(page.west_roster_query)

    def test_game_info_query(self):
        """Test xpath query for game info."""
        from src.scraper.html.allstar import AllStarPage

        page = AllStarPage(html=self.html)
        self.assertIsNotNone(page.game_info_query)

    def test_mvp_query(self):
        """Test xpath query for All-Star MVP."""
        from src.scraper.html.allstar import AllStarPage

        page = AllStarPage(html=self.html)
        self.assertIsNotNone(page.mvp_query)

    def test_final_score_query(self):
        """Test xpath query for final score."""
        from src.scraper.html.allstar import AllStarPage

        page = AllStarPage(html=self.html)
        self.assertIsNotNone(page.final_score_query)


class TestAllStarPlayerRow(TestCase):
    """Unit tests for AllStarPlayerRow class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_player_name_query(self):
        """Test xpath query for player name."""
        from src.scraper.html.allstar import AllStarPlayerRow

        row = AllStarPlayerRow(html=self.html)
        self.assertIn("player", row.player_name_query)

    def test_minutes_query(self):
        """Test xpath query for minutes played."""
        from src.scraper.html.allstar import AllStarPlayerRow

        row = AllStarPlayerRow(html=self.html)
        self.assertIn("mp", row.minutes_query)

    def test_points_query(self):
        """Test xpath query for points."""
        from src.scraper.html.allstar import AllStarPlayerRow

        row = AllStarPlayerRow(html=self.html)
        self.assertIn("pts", row.points_query)

    def test_rebounds_query(self):
        """Test xpath query for rebounds."""
        from src.scraper.html.allstar import AllStarPlayerRow

        row = AllStarPlayerRow(html=self.html)
        self.assertIn("trb", row.rebounds_query)

    def test_assists_query(self):
        """Test xpath query for assists."""
        from src.scraper.html.allstar import AllStarPlayerRow

        row = AllStarPlayerRow(html=self.html)
        self.assertIn("ast", row.assists_query)

    def test_starter_query(self):
        """Test xpath query for starter status."""
        from src.scraper.html.allstar import AllStarPlayerRow

        row = AllStarPlayerRow(html=self.html)
        self.assertIsNotNone(row.starter_query)
