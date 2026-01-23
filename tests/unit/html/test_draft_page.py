"""Unit tests for DraftPage HTML wrapper."""

from unittest import TestCase
from unittest.mock import MagicMock, patch


class TestDraftPage(TestCase):
    """Unit tests for DraftPage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_draft_table_query(self):
        """Test xpath query for draft table."""
        from src.scraper.html.draft import DraftPage

        assert DraftPage(html=self.html).draft_table_query == '//table[@id="stats"]'

    def test_rows_query(self):
        """Test xpath query for draft rows."""
        from src.scraper.html.draft import DraftPage

        assert DraftPage(html=self.html).rows_query == '//table[@id="stats"]//tbody/tr[not(contains(@class, "thead"))]'

    @patch.object(MagicMock, "xpath", create=True)
    def test_rows_returns_draft_rows_when_found(self, _mock_xpath):
        """Test that draft rows are returned when found."""
        from src.scraper.html.draft import DraftPage, DraftRow

        mock_row = MagicMock()
        mock_row.text_content = MagicMock(return_value="1")
        self.html.xpath = MagicMock(return_value=[mock_row])
        page = DraftPage(html=self.html)

        rows = page.rows
        assert len(rows) == 1
        assert isinstance(rows[0], DraftRow)


class TestDraftRow(TestCase):
    """Unit tests for DraftRow class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_pick_query(self):
        """Test xpath query for pick number."""
        from src.scraper.html.draft import DraftRow

        row = DraftRow(html=self.html)
        assert row.pick_query == 'td[@data-stat="pick_overall"]'

    def test_round_query(self):
        """Test xpath query for round."""
        from src.scraper.html.draft import DraftRow

        row = DraftRow(html=self.html)
        assert row.round_query == 'td[@data-stat="round_pick"]'

    def test_team_query(self):
        """Test xpath query for team."""
        from src.scraper.html.draft import DraftRow

        row = DraftRow(html=self.html)
        assert row.team_query == 'td[@data-stat="team_id"]/a'

    def test_player_query(self):
        """Test xpath query for player name."""
        from src.scraper.html.draft import DraftRow

        row = DraftRow(html=self.html)
        assert row.player_query == 'td[@data-stat="player"]/a'

    def test_college_query(self):
        """Test xpath query for college."""
        from src.scraper.html.draft import DraftRow

        row = DraftRow(html=self.html)
        assert row.college_query == 'td[@data-stat="college_name"]/a'

    def test_years_active_query(self):
        """Test xpath query for years active in NBA."""
        from src.scraper.html.draft import DraftRow

        row = DraftRow(html=self.html)
        assert row.years_active_query == 'td[@data-stat="years_played"]'
