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
        self.assertIn("playoff", page.bracket_query.lower())

    def test_series_links_query(self):
        """Test xpath query for series links."""
        from src.scraper.html.playoffs import PlayoffsPage

        page = PlayoffsPage(html=self.html)
        self.assertIsNotNone(page.series_links_query)

    def test_champion_query(self):
        """Test xpath query for champion."""
        from src.scraper.html.playoffs import PlayoffsPage

        page = PlayoffsPage(html=self.html)
        self.assertIsNotNone(page.champion_query)

    def test_finals_mvp_query(self):
        """Test xpath query for Finals MVP."""
        from src.scraper.html.playoffs import PlayoffsPage

        page = PlayoffsPage(html=self.html)
        self.assertIsNotNone(page.finals_mvp_query)


class TestPlayoffSeriesPage(TestCase):
    """Unit tests for PlayoffSeriesPage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_series_result_query(self):
        """Test xpath query for series result."""
        from src.scraper.html.playoffs import PlayoffSeriesPage

        page = PlayoffSeriesPage(html=self.html)
        self.assertIsNotNone(page.series_result_query)

    def test_games_table_query(self):
        """Test xpath query for games table."""
        from src.scraper.html.playoffs import PlayoffSeriesPage

        page = PlayoffSeriesPage(html=self.html)
        self.assertIn("table", page.games_table_query)

    def test_team1_stats_query(self):
        """Test xpath query for team 1 stats."""
        from src.scraper.html.playoffs import PlayoffSeriesPage

        page = PlayoffSeriesPage(html=self.html)
        self.assertIn("stats_table", page.team1_stats_query)

    def test_team2_stats_query(self):
        """Test xpath query for team 2 stats."""
        from src.scraper.html.playoffs import PlayoffSeriesPage

        page = PlayoffSeriesPage(html=self.html)
        self.assertIn("stats_table", page.team2_stats_query)


class TestPlayoffGameRow(TestCase):
    """Unit tests for PlayoffGameRow class."""

    def setUp(self):
        """Set up test fixtures."""
        self.html = MagicMock()

    def test_game_number_query(self):
        """Test xpath query for game number."""
        from src.scraper.html.playoffs import PlayoffGameRow

        row = PlayoffGameRow(html=self.html)
        self.assertIsNotNone(row.game_number_query)

    def test_date_query(self):
        """Test xpath query for game date."""
        from src.scraper.html.playoffs import PlayoffGameRow

        row = PlayoffGameRow(html=self.html)
        self.assertIsNotNone(row.date_query)

    def test_home_team_query(self):
        """Test xpath query for home team."""
        from src.scraper.html.playoffs import PlayoffGameRow

        row = PlayoffGameRow(html=self.html)
        self.assertIsNotNone(row.home_team_query)

    def test_away_team_query(self):
        """Test xpath query for away team."""
        from src.scraper.html.playoffs import PlayoffGameRow

        row = PlayoffGameRow(html=self.html)
        self.assertIsNotNone(row.away_team_query)

    def test_score_query(self):
        """Test xpath query for score."""
        from src.scraper.html.playoffs import PlayoffGameRow

        row = PlayoffGameRow(html=self.html)
        self.assertIsNotNone(row.score_query)
