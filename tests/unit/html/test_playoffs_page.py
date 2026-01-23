"""Unit tests for PlayoffsPage HTML wrapper."""

from unittest import TestCase
from unittest.mock import MagicMock


class TestPlayoffsPage(TestCase):
    """Unit tests for PlayoffsPage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_bracket_query(self):
        """Test xpath query for playoff bracket."""
        from src.scraper.html.playoffs import PlayoffsPage

        page = PlayoffsPage(html=self.html)
        assert "playoff" in page.bracket_query.lower()

    def test_series_links_query(self):
        """Test xpath query for series links."""
        from src.scraper.html.playoffs import PlayoffsPage

        page = PlayoffsPage(html=self.html)
        assert page.series_links_query is not None

    def test_champion_query(self):
        """Test xpath query for champion."""
        from src.scraper.html.playoffs import PlayoffsPage

        page = PlayoffsPage(html=self.html)
        assert page.champion_query is not None

    def test_finals_mvp_query(self):
        """Test xpath query for Finals MVP."""
        from src.scraper.html.playoffs import PlayoffsPage

        page = PlayoffsPage(html=self.html)
        assert page.finals_mvp_query is not None


class TestPlayoffSeriesPage(TestCase):
    """Unit tests for PlayoffSeriesPage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_series_result_query(self):
        """Test xpath query for series result."""
        from src.scraper.html.playoffs import PlayoffSeriesPage

        page = PlayoffSeriesPage(html=self.html)
        assert page.series_result_query is not None

    def test_games_table_query(self):
        """Test xpath query for games table."""
        from src.scraper.html.playoffs import PlayoffSeriesPage

        page = PlayoffSeriesPage(html=self.html)
        assert "table" in page.games_table_query

    def test_team1_stats_query(self):
        """Test xpath query for team 1 stats."""
        from src.scraper.html.playoffs import PlayoffSeriesPage

        page = PlayoffSeriesPage(html=self.html)
        assert "stats_table" in page.team1_stats_query

    def test_team2_stats_query(self):
        """Test xpath query for team 2 stats."""
        from src.scraper.html.playoffs import PlayoffSeriesPage

        page = PlayoffSeriesPage(html=self.html)
        assert "stats_table" in page.team2_stats_query


class TestPlayoffGameRow(TestCase):
    """Unit tests for PlayoffGameRow class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_game_number_query(self):
        """Test xpath query for game number."""
        from src.scraper.html.playoffs import PlayoffGameRow

        row = PlayoffGameRow(html=self.html)
        assert row.game_number_query is not None

    def test_date_query(self):
        """Test xpath query for game date."""
        from src.scraper.html.playoffs import PlayoffGameRow

        row = PlayoffGameRow(html=self.html)
        assert row.date_query is not None

    def test_home_team_query(self):
        """Test xpath query for home team."""
        from src.scraper.html.playoffs import PlayoffGameRow

        row = PlayoffGameRow(html=self.html)
        assert row.home_team_query is not None

    def test_away_team_query(self):
        """Test xpath query for away team."""
        from src.scraper.html.playoffs import PlayoffGameRow

        row = PlayoffGameRow(html=self.html)
        assert row.away_team_query is not None

    def test_score_query(self):
        """Test xpath query for score."""
        from src.scraper.html.playoffs import PlayoffGameRow

        row = PlayoffGameRow(html=self.html)
        assert row.score_query is not None
