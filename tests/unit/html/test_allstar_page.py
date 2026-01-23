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
        from src.scraper.html.allstar import AllStarPage  # noqa: PLC0415

        page = AllStarPage(html=self.html)
        assert "stats_table" in page.box_score_tables_query

    def test_east_roster_query(self):
        """Test xpath query for East roster."""
        from src.scraper.html.allstar import AllStarPage  # noqa: PLC0415

        page = AllStarPage(html=self.html)
        assert page.east_roster_query is not None

    def test_west_roster_query(self):
        """Test xpath query for West roster."""
        from src.scraper.html.allstar import AllStarPage  # noqa: PLC0415

        page = AllStarPage(html=self.html)
        assert page.west_roster_query is not None

    def test_game_info_query(self):
        """Test xpath query for game info."""
        from src.scraper.html.allstar import AllStarPage  # noqa: PLC0415

        page = AllStarPage(html=self.html)
        assert page.game_info_query is not None

    def test_mvp_query(self):
        """Test xpath query for All-Star MVP."""
        from src.scraper.html.allstar import AllStarPage  # noqa: PLC0415

        page = AllStarPage(html=self.html)
        assert page.mvp_query is not None

    def test_final_score_query(self):
        """Test xpath query for final score."""
        from src.scraper.html.allstar import AllStarPage  # noqa: PLC0415

        page = AllStarPage(html=self.html)
        assert page.final_score_query is not None


class TestAllStarPlayerRow(TestCase):
    """Unit tests for AllStarPlayerRow class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_player_name_query(self):
        """Test xpath query for player name."""
        from src.scraper.html.allstar import AllStarPlayerRow  # noqa: PLC0415

        row = AllStarPlayerRow(html=self.html)
        assert "player" in row.player_name_query

    def test_minutes_query(self):
        """Test xpath query for minutes played."""
        from src.scraper.html.allstar import AllStarPlayerRow  # noqa: PLC0415

        row = AllStarPlayerRow(html=self.html)
        assert "mp" in row.minutes_query

    def test_points_query(self):
        """Test xpath query for points."""
        from src.scraper.html.allstar import AllStarPlayerRow  # noqa: PLC0415

        row = AllStarPlayerRow(html=self.html)
        assert "pts" in row.points_query

    def test_rebounds_query(self):
        """Test xpath query for rebounds."""
        from src.scraper.html.allstar import AllStarPlayerRow  # noqa: PLC0415

        row = AllStarPlayerRow(html=self.html)
        assert "trb" in row.rebounds_query

    def test_assists_query(self):
        """Test xpath query for assists."""
        from src.scraper.html.allstar import AllStarPlayerRow  # noqa: PLC0415

        row = AllStarPlayerRow(html=self.html)
        assert "ast" in row.assists_query

    def test_starter_query(self):
        """Test xpath query for starter status."""
        from src.scraper.html.allstar import AllStarPlayerRow  # noqa: PLC0415

        row = AllStarPlayerRow(html=self.html)
        assert row.starter_query is not None
