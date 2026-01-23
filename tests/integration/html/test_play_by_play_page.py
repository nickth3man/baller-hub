import os
from unittest import TestCase

from lxml import html

from src.scraper.html import PlayByPlayPage


class TestPlayByPlayPage(TestCase):
    def setUp(self):
        with open(  # noqa: PTH123
            os.path.join(  # noqa: PTH118
                os.path.dirname(__file__),
                "../files/play_by_play/199911160ATL.html",
            ),
            encoding="utf-8",
        ) as f:
            self._1999_11_16_ATL_html = f.read()

    def test_game_url_paths_query(self):
        page = PlayByPlayPage(html=html.fromstring(self._1999_11_16_ATL_html))
        rows = page.play_by_play_table.rows
        assert len(rows) == 449  # noqa: PLR2004

        last_row = rows[448]
        assert last_row.timestamp == "0:01.0"
        assert last_row.away_team_play_description == ""
        assert not last_row.is_away_team_play
        assert last_row.is_home_team_play
        assert last_row.home_team_play_description == "Defensive rebound by D. Mutombo"
        assert last_row.formatted_scores == "98-103"
