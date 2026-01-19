"""HTML wrappers for daily leader pages."""

from .base_rows import PlayerGameBoxScoreRow


class DailyLeadersPage:
    """
    Wraps the 'Daily Leaders' page (e.g., /friv/dailyleaders.fcgi).

    Contains the top performers for a specific date across all games.
    """

    def __init__(self, html):
        self.html = html

    @property
    def daily_leaders(self):
        """
        list[PlayerGameBoxScoreRow]: List of rows containing top performer stats.
        """
        return [
            PlayerGameBoxScoreRow(row_html)
            for row_html in self.html.xpath(
                '//table[@id="stats"]//tbody/tr[not(contains(@class, "thead"))]'
            )
        ]


class DailyBoxScoresPage:
    """
    Wraps the main 'Box Scores' index page for a date (e.g., /boxscores/?month=X&day=Y&year=Z).

    This page lists all games played on that day and links to their detailed box scores.
    """

    def __init__(self, html):
        self.html = html

    @property
    def game_url_paths_query(self):
        """str: XPath query to find links to detailed box scores."""
        return '//td[contains(@class, "gamelink")]/a'

    @property
    def game_url_paths(self):
        """Returns a list of relative URL paths to each game's box score page."""
        game_links = self.html.xpath(self.game_url_paths_query)
        return [game_link.attrib["href"] for game_link in game_links]
