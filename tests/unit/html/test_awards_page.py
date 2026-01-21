"""Unit tests for AwardsPage HTML wrapper."""

from unittest import TestCase
from unittest.mock import MagicMock


class TestAwardsPage(TestCase):
    """Unit tests for AwardsPage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_awards_table_query(self):
        """Test xpath query for awards table."""
        from src.scraper.html.awards import AwardsPage

        page = AwardsPage(html=self.html)
        # Awards tables have IDs like mvp_NBA, dpoy_NBA, etc.
        self.assertIn("stats_table", page.awards_table_query)

    def test_rows_query(self):
        """Test xpath query for award rows."""
        from src.scraper.html.awards import AwardsPage

        page = AwardsPage(html=self.html)
        self.assertIn("tbody/tr", page.rows_query)

    def test_header_query(self):
        """Test xpath query for page header."""
        from src.scraper.html.awards import AwardsPage

        page = AwardsPage(html=self.html)
        expected = '//h1'
        self.assertEqual(page.header_query, expected)


class TestAwardRow(TestCase):
    """Unit tests for AwardRow class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_season_query(self):
        """Test xpath query for season."""
        from src.scraper.html.awards import AwardRow

        row = AwardRow(html=self.html)
        self.assertEqual(row.season_query, 'th[@data-stat="season"]/a')

    def test_player_query(self):
        """Test xpath query for player name."""
        from src.scraper.html.awards import AwardRow

        row = AwardRow(html=self.html)
        self.assertEqual(row.player_query, 'td[@data-stat="player"]/a')

    def test_team_query(self):
        """Test xpath query for team."""
        from src.scraper.html.awards import AwardRow

        row = AwardRow(html=self.html)
        self.assertEqual(row.team_query, 'td[@data-stat="team_id"]/a')

    def test_age_query(self):
        """Test xpath query for age."""
        from src.scraper.html.awards import AwardRow

        row = AwardRow(html=self.html)
        self.assertEqual(row.age_query, 'td[@data-stat="age"]')

    def test_voting_share_query(self):
        """Test xpath query for voting share."""
        from src.scraper.html.awards import AwardRow

        row = AwardRow(html=self.html)
        self.assertEqual(row.voting_share_query, 'td[@data-stat="award_share"]')


class TestHallOfFamePage(TestCase):
    """Unit tests for Hall of Fame page."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_inductees_table_query(self):
        """Test xpath query for inductees table."""
        from src.scraper.html.awards import HallOfFamePage

        page = HallOfFamePage(html=self.html)
        self.assertIn("stats_table", page.inductees_table_query)

    def test_inductee_rows_query(self):
        """Test xpath query for inductee rows."""
        from src.scraper.html.awards import HallOfFamePage

        page = HallOfFamePage(html=self.html)
        self.assertIn("tbody/tr", page.rows_query)


class TestAllNBATeamPage(TestCase):
    """Unit tests for All-NBA team pages."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_team_tables_query(self):
        """Test xpath query for team selection tables."""
        from src.scraper.html.awards import AllNBATeamPage

        page = AllNBATeamPage(html=self.html)
        self.assertIn("stats_table", page.team_tables_query)

    def test_first_team_query(self):
        """Test xpath query for first team selections."""
        from src.scraper.html.awards import AllNBATeamPage

        page = AllNBATeamPage(html=self.html)
        self.assertIsNotNone(page.first_team_query)
