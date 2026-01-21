"""Unit tests for LeadersPage HTML wrapper."""

from unittest import TestCase
from unittest.mock import MagicMock


class TestLeadersPage(TestCase):
    """Unit tests for LeadersPage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_leaders_table_query(self):
        """Test xpath query for leaders table."""
        from src.scraper.html.leaders import LeadersPage

        page = LeadersPage(html=self.html)
        self.assertIn("stats_table", page.leaders_table_query)

    def test_rows_query(self):
        """Test xpath query for leader rows."""
        from src.scraper.html.leaders import LeadersPage

        page = LeadersPage(html=self.html)
        self.assertIn("tbody/tr", page.rows_query)

    def test_stat_type_query(self):
        """Test xpath query for stat type (points, rebounds, etc.)."""
        from src.scraper.html.leaders import LeadersPage

        page = LeadersPage(html=self.html)
        self.assertIsNotNone(page.stat_type_query)

    def test_leader_type_query(self):
        """Test xpath query for leader type (career, active, season)."""
        from src.scraper.html.leaders import LeadersPage

        page = LeadersPage(html=self.html)
        self.assertIsNotNone(page.leader_type_query)


class TestLeaderRow(TestCase):
    """Unit tests for LeaderRow class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_rank_query(self):
        """Test xpath query for rank."""
        from src.scraper.html.leaders import LeaderRow

        row = LeaderRow(html=self.html)
        self.assertIn("rank", row.rank_query)

    def test_player_query(self):
        """Test xpath query for player name."""
        from src.scraper.html.leaders import LeaderRow

        row = LeaderRow(html=self.html)
        self.assertIn("player", row.player_query)

    def test_value_query(self):
        """Test xpath query for stat value."""
        from src.scraper.html.leaders import LeaderRow

        row = LeaderRow(html=self.html)
        self.assertIsNotNone(row.value_query)

    def test_years_query(self):
        """Test xpath query for years played."""
        from src.scraper.html.leaders import LeaderRow

        row = LeaderRow(html=self.html)
        self.assertIsNotNone(row.years_query)

    def test_teams_query(self):
        """Test xpath query for teams played for."""
        from src.scraper.html.leaders import LeaderRow

        row = LeaderRow(html=self.html)
        self.assertIsNotNone(row.teams_query)


class TestCareerLeadersPage(TestCase):
    """Unit tests for career leaders page."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_career_table_query(self):
        """Test xpath query for career leaders table."""
        from src.scraper.html.leaders import CareerLeadersPage

        page = CareerLeadersPage(html=self.html)
        self.assertIn("tot", page.career_table_query)


class TestActiveLeadersPage(TestCase):
    """Unit tests for active leaders page."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_active_table_query(self):
        """Test xpath query for active leaders table."""
        from src.scraper.html.leaders import ActiveLeadersPage

        page = ActiveLeadersPage(html=self.html)
        self.assertIn("active", page.active_table_query)
