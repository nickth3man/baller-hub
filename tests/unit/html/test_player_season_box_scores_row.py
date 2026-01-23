from unittest import TestCase
from unittest.mock import MagicMock

from src.scraper.html import PlayerSeasonBoxScoresRow


class TestPlayerSeasonBoxScoresRow(TestCase):
    def setUp(self):
        self.html = MagicMock()

    def test_not_equal_when_row_is_compared_against_non_row(self):
        assert PlayerSeasonBoxScoresRow(html=MagicMock()) != 1

    def test_not_equal_when_both_rows_but_different_html(self):
        assert PlayerSeasonBoxScoresRow(
            html=MagicMock(name="first html")
        ) != PlayerSeasonBoxScoresRow(html=MagicMock(name="second html"))

    def test_equal_when_both_rows_and_same_html(self):
        html = MagicMock(name="shared html")
        assert PlayerSeasonBoxScoresRow(html=html) == PlayerSeasonBoxScoresRow(
            html=html
        )

    def test_date_when_cells_exist(self):
        self.html.xpath = MagicMock(
            return_value=[MagicMock(text_content=MagicMock(return_value="some date"))]
        )
        assert PlayerSeasonBoxScoresRow(html=self.html).date == "some date"
        self.html.xpath.assert_called_once_with('td[@data-stat="date"]')

    def test_date_is_empty_string_when_cells_do_not_exist(self):
        self.html.xpath = MagicMock(return_value=[])
        assert PlayerSeasonBoxScoresRow(html=self.html).date == ""
        self.html.xpath.assert_called_once_with('td[@data-stat="date"]')

    def test_points_scored_when_cells_exist(self):
        self.html.xpath = MagicMock(
            return_value=[MagicMock(text_content=MagicMock(return_value="some points"))]
        )
        assert PlayerSeasonBoxScoresRow(html=self.html).points_scored == "some points"
        self.html.xpath.assert_called_once_with('td[@data-stat="pts"]')

    def test_points_scored_is_empty_string_when_cells_do_not_exist(self):
        self.html.xpath = MagicMock(return_value=[])
        assert PlayerSeasonBoxScoresRow(html=self.html).points_scored == ""
        self.html.xpath.assert_called_once_with('td[@data-stat="pts"]')
