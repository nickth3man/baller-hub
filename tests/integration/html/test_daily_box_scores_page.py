import os
from unittest import TestCase

from lxml import html

from src.scraper.html import DailyBoxScoresPage


class TestDailyBoxScoresPage(TestCase):
    def setUp(self):
        with open(
            os.path.join(os.path.dirname(__file__), "../files/boxscores/2017/1/1.html"),
            encoding="utf-8",
        ) as file_input:
            self.january_01_2017_box_scores = file_input.read()

    def test_game_url_paths_query(self):
        page = DailyBoxScoresPage(html=html.fromstring(self.january_01_2017_box_scores))
        assert page.game_url_paths_query == '//td[contains(@class, "gamelink")]/a'

    def test_parse_urls(self):
        page = DailyBoxScoresPage(html=html.fromstring(self.january_01_2017_box_scores))
        urls = page.game_url_paths
        assert len(urls) == 5
        assert urls[0] == "/boxscores/201701010ATL.html"
        assert urls[1] == "/boxscores/201701010IND.html"
        assert urls[2] == "/boxscores/201701010LAL.html"
        assert urls[3] == "/boxscores/201701010MIA.html"
        assert urls[4] == "/boxscores/201701010MIN.html"
