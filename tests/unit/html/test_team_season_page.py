"""Unit tests for TeamSeasonPage HTML wrapper."""

from unittest import TestCase
from unittest.mock import MagicMock


class TestTeamSeasonPage(TestCase):
    """Unit tests for TeamSeasonPage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_roster_table_query(self):
        """Test xpath query for roster table."""
        from src.scraper.html.team_season import TeamSeasonPage

        page = TeamSeasonPage(html=self.html)
        self.assertEqual(page.roster_table_query, '//table[@id="roster"]')

    def test_per_game_table_query(self):
        """Test xpath query for per-game stats table."""
        from src.scraper.html.team_season import TeamSeasonPage

        page = TeamSeasonPage(html=self.html)
        self.assertIn("per_game", page.per_game_table_query)

    def test_totals_table_query(self):
        """Test xpath query for totals table."""
        from src.scraper.html.team_season import TeamSeasonPage

        page = TeamSeasonPage(html=self.html)
        self.assertIn("totals", page.totals_table_query)

    def test_team_opponent_table_query(self):
        """Test xpath query for team and opponent stats table."""
        from src.scraper.html.team_season import TeamSeasonPage

        page = TeamSeasonPage(html=self.html)
        self.assertIn("team_and_opponent", page.team_opponent_table_query)

    def test_team_info_query(self):
        """Test xpath query for team info section."""
        from src.scraper.html.team_season import TeamSeasonPage

        page = TeamSeasonPage(html=self.html)
        self.assertIsNotNone(page.team_info_query)

    def test_record_query(self):
        """Test xpath query for team record."""
        from src.scraper.html.team_season import TeamSeasonPage

        page = TeamSeasonPage(html=self.html)
        self.assertIsNotNone(page.record_query)

    def test_coach_query(self):
        """Test xpath query for coach."""
        from src.scraper.html.team_season import TeamSeasonPage

        page = TeamSeasonPage(html=self.html)
        self.assertIsNotNone(page.coach_query)


class TestRosterRow(TestCase):
    """Unit tests for RosterRow class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_player_name_query(self):
        """Test xpath query for player name."""
        from src.scraper.html.team_season import RosterRow

        row = RosterRow(html=self.html)
        self.assertIn("player", row.player_name_query)

    def test_number_query(self):
        """Test xpath query for jersey number."""
        from src.scraper.html.team_season import RosterRow

        row = RosterRow(html=self.html)
        self.assertIn("number", row.number_query)

    def test_position_query(self):
        """Test xpath query for position."""
        from src.scraper.html.team_season import RosterRow

        row = RosterRow(html=self.html)
        self.assertIn("pos", row.position_query)

    def test_height_query(self):
        """Test xpath query for height."""
        from src.scraper.html.team_season import RosterRow

        row = RosterRow(html=self.html)
        self.assertIn("height", row.height_query)

    def test_weight_query(self):
        """Test xpath query for weight."""
        from src.scraper.html.team_season import RosterRow

        row = RosterRow(html=self.html)
        self.assertIn("weight", row.weight_query)

    def test_birth_date_query(self):
        """Test xpath query for birth date."""
        from src.scraper.html.team_season import RosterRow

        row = RosterRow(html=self.html)
        self.assertIn("birth", row.birth_date_query)

    def test_college_query(self):
        """Test xpath query for college."""
        from src.scraper.html.team_season import RosterRow

        row = RosterRow(html=self.html)
        self.assertIn("college", row.college_query)


class TestTeamStatRow(TestCase):
    """Unit tests for TeamStatRow class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_player_query(self):
        """Test xpath query for player."""
        from src.scraper.html.team_season import TeamStatRow

        row = TeamStatRow(html=self.html)
        self.assertIn("player", row.player_query)

    def test_games_query(self):
        """Test xpath query for games played."""
        from src.scraper.html.team_season import TeamStatRow

        row = TeamStatRow(html=self.html)
        self.assertIn("g", row.games_query)

    def test_minutes_query(self):
        """Test xpath query for minutes."""
        from src.scraper.html.team_season import TeamStatRow

        row = TeamStatRow(html=self.html)
        self.assertIn("mp", row.minutes_query)

    def test_points_query(self):
        """Test xpath query for points."""
        from src.scraper.html.team_season import TeamStatRow

        row = TeamStatRow(html=self.html)
        self.assertIn("pts", row.points_query)
