"""Unit tests for CoachPage HTML wrapper."""

from unittest import TestCase
from unittest.mock import MagicMock, patch


class TestCoachPage(TestCase):
    """Unit tests for CoachPage class."""

    def setUp(self):
        """Set up test fixtures."""
        # Import here to avoid circular imports during test discovery
        from src.scraper.html.coach import CoachPage

        self.html = MagicMock()
        self.page = CoachPage(html=self.html)

    def test_coaching_record_table_query(self):
        """Test xpath query for coaching record table."""
        from src.scraper.html.coach import CoachPage

        assert CoachPage(html=self.html).coaching_record_table_query == '//table[contains(@id, "coach")]'

    def test_name_query(self):
        """Test xpath query for coach name."""
        from src.scraper.html.coach import CoachPage

        expected = (
            '//div[@id="meta"]//h1/span | //h1[@itemprop="name"]/span | //h1/span'
        )
        assert CoachPage(html=self.html).name_query == expected

    @patch.object(MagicMock, "xpath", create=True)
    def test_coaching_record_table_returns_table_when_found(self, _mock_xpath):
        """Test that coaching record table is returned when found."""
        from src.scraper.html.coach import CoachPage

        mock_table = MagicMock()
        self.html.xpath = MagicMock(return_value=[mock_table])
        page = CoachPage(html=self.html)

        result = page.coaching_record_table
        assert result is not None

    @patch.object(MagicMock, "xpath", create=True)
    def test_coaching_record_table_returns_none_when_not_found(self, _mock_xpath):
        """Test that None is returned when coaching record table not found."""
        from src.scraper.html.coach import CoachPage

        self.html.xpath = MagicMock(return_value=[])
        page = CoachPage(html=self.html)

        result = page.coaching_record_table
        assert result is None

    def test_biography_section_query(self):
        """Test xpath query for biography section."""
        from src.scraper.html.coach import CoachPage

        expected = '//div[@id="meta"]'
        assert CoachPage(html=self.html).biography_section_query == expected


class TestCoachingRecordRow(TestCase):
    """Unit tests for CoachingRecordRow class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_season_query(self):
        """Test xpath query for season."""
        from src.scraper.html.coach import CoachingRecordRow

        row = CoachingRecordRow(html=self.html)
        assert row.season_query == 'th[@data-stat="season"]/a | th[@data-stat="season"]'

    def test_team_query(self):
        """Test xpath query for team."""
        from src.scraper.html.coach import CoachingRecordRow

        row = CoachingRecordRow(html=self.html)
        assert row.team_query == 'td[@data-stat="team_id"]/a'

    def test_wins_query(self):
        """Test xpath query for wins."""
        from src.scraper.html.coach import CoachingRecordRow

        row = CoachingRecordRow(html=self.html)
        assert row.wins_query == 'td[@data-stat="wins"]'

    def test_losses_query(self):
        """Test xpath query for losses."""
        from src.scraper.html.coach import CoachingRecordRow

        row = CoachingRecordRow(html=self.html)
        assert row.losses_query == 'td[@data-stat="losses"]'

    def test_win_pct_query(self):
        """Test xpath query for win percentage."""
        from src.scraper.html.coach import CoachingRecordRow

        row = CoachingRecordRow(html=self.html)
        assert row.win_pct_query == 'td[@data-stat="win_loss_pct"]'
