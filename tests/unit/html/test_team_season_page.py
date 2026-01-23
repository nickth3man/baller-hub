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
        from src.scraper.html.team_season import TeamSeasonPage  # noqa: PLC0415

        page = TeamSeasonPage(html=self.html)
        assert page.roster_table_query == '//table[@id="roster"]'

    def test_per_game_table_query(self):
        """Test xpath query for per-game stats table."""
        from src.scraper.html.team_season import TeamSeasonPage  # noqa: PLC0415

        page = TeamSeasonPage(html=self.html)
        assert "per_game" in page.per_game_table_query

    def test_totals_table_query(self):
        """Test xpath query for totals table."""
        from src.scraper.html.team_season import TeamSeasonPage  # noqa: PLC0415

        page = TeamSeasonPage(html=self.html)
        assert "totals" in page.totals_table_query

    def test_team_opponent_table_query(self):
        """Test xpath query for team and opponent stats table."""
        from src.scraper.html.team_season import TeamSeasonPage  # noqa: PLC0415

        page = TeamSeasonPage(html=self.html)
        assert "team_and_opponent" in page.team_opponent_table_query

    def test_team_info_query(self):
        """Test xpath query for team info section."""
        from src.scraper.html.team_season import TeamSeasonPage  # noqa: PLC0415

        page = TeamSeasonPage(html=self.html)
        assert page.team_info_query is not None

    def test_record_query(self):
        """Test xpath query for team record."""
        from src.scraper.html.team_season import TeamSeasonPage  # noqa: PLC0415

        page = TeamSeasonPage(html=self.html)
        assert page.record_query is not None

    def test_coach_query(self):
        """Test xpath query for coach."""
        from src.scraper.html.team_season import TeamSeasonPage  # noqa: PLC0415

        page = TeamSeasonPage(html=self.html)
        assert page.coach_query is not None


class TestRosterRow(TestCase):
    """Unit tests for RosterRow class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_player_name_query(self):
        """Test xpath query for player name."""
        from src.scraper.html.team_season import RosterRow  # noqa: PLC0415

        row = RosterRow(html=self.html)
        assert "player" in row.player_name_query

    def test_number_query(self):
        """Test xpath query for jersey number."""
        from src.scraper.html.team_season import RosterRow  # noqa: PLC0415

        row = RosterRow(html=self.html)
        assert "number" in row.number_query

    def test_position_query(self):
        """Test xpath query for position."""
        from src.scraper.html.team_season import RosterRow  # noqa: PLC0415

        row = RosterRow(html=self.html)
        assert "pos" in row.position_query

    def test_height_query(self):
        """Test xpath query for height."""
        from src.scraper.html.team_season import RosterRow  # noqa: PLC0415

        row = RosterRow(html=self.html)
        assert "height" in row.height_query

    def test_weight_query(self):
        """Test xpath query for weight."""
        from src.scraper.html.team_season import RosterRow  # noqa: PLC0415

        row = RosterRow(html=self.html)
        assert "weight" in row.weight_query

    def test_birth_date_query(self):
        """Test xpath query for birth date."""
        from src.scraper.html.team_season import RosterRow  # noqa: PLC0415

        row = RosterRow(html=self.html)
        assert "birth" in row.birth_date_query

    def test_college_query(self):
        """Test xpath query for college."""
        from src.scraper.html.team_season import RosterRow  # noqa: PLC0415

        row = RosterRow(html=self.html)
        assert "college" in row.college_query


class TestTeamStatRow(TestCase):
    """Unit tests for TeamStatRow class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_player_query(self):
        """Test xpath query for player."""
        from src.scraper.html.team_season import TeamStatRow  # noqa: PLC0415

        row = TeamStatRow(html=self.html)
        assert "player" in row.player_query

    def test_games_query(self):
        """Test xpath query for games played."""
        from src.scraper.html.team_season import TeamStatRow  # noqa: PLC0415

        row = TeamStatRow(html=self.html)
        assert "g" in row.games_query

    def test_minutes_query(self):
        """Test xpath query for minutes."""
        from src.scraper.html.team_season import TeamStatRow  # noqa: PLC0415

        row = TeamStatRow(html=self.html)
        assert "mp" in row.minutes_query

    def test_points_query(self):
        """Test xpath query for points."""
        from src.scraper.html.team_season import TeamStatRow  # noqa: PLC0415

        row = TeamStatRow(html=self.html)
        assert "pts" in row.points_query
