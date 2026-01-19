
from .base_rows import PlayerGameBoxScoreRow


class DailyLeadersPage:
    def __init__(self, html):
        self.html = html

    @property
    def daily_leaders(self):
        return [
            PlayerGameBoxScoreRow(row_html)
            for row_html in self.html.xpath(
                '//table[@id="stats"]//tbody/tr[not(contains(@class, "thead"))]'
            )
        ]


class DailyBoxScoresPage:
    def __init__(self, html):
        self.html = html

    @property
    def game_url_paths_query(self):
        return '//td[contains(@class, "gamelink")]/a'

    @property
    def game_url_paths(self):
        game_links = self.html.xpath(self.game_url_paths_query)
        return [game_link.attrib["href"] for game_link in game_links]
