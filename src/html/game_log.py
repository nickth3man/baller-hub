
from .base_rows import PlayerSeasonGameLogRow


class PlayerSeasonBoxScoresPage:
    def __init__(self, html):
        self.html = html

    @property
    def regular_season_box_scores_table_query(self):
        return '//table[@id="player_game_log_reg"]'

    @property
    def regular_season_box_scores_table(self):
        matching_tables = self.html.xpath(self.regular_season_box_scores_table_query)

        if len(matching_tables) != 1:
            return None

        return PlayerSeasonBoxScoresTable(html=matching_tables[0])

    @property
    def playoff_box_scores_table_query(self):
        return '//table[@id="player_game_log_post"]'

    @property
    def playoff_box_scores_table(self):
        matching_tables = self.html.xpath(self.playoff_box_scores_table_query)

        if len(matching_tables) != 1:
            return None

        return PlayerSeasonBoxScoresTable(html=matching_tables[0])


class PlayerSeasonBoxScoresTable:
    def __init__(self, html):
        self.html = html

    @property
    def rows_query(self):
        # Every 20 rows, there's a row that has column header values - those should be ignored
        return 'tbody/tr[not(contains(@class, "spacer")) and not(contains(@class, "thead"))]'

    @property
    def rows(self):
        return [
            PlayerSeasonBoxScoresRow(html=row_html)
            for row_html in self.html.xpath(self.rows_query)
        ]


class PlayerSeasonBoxScoresRow(PlayerSeasonGameLogRow):
    def __init__(self, html):
        super().__init__(html)

    def __eq__(self, other):
        if isinstance(other, PlayerSeasonBoxScoresRow):
            return self.html == other.html
        return False

    @property
    def is_active(self):
        # When a player is not active (for a reason like "Inactive", "Did Not Play", "Did Not Dress")
        # "is_starter" column has a "colspan" attribute. When a player is active, "is_starter" column does not
        # have a "colspan" attribute
        cells = self.html.xpath('td[@data-stat="is_starter"]')
        if len(cells) > 0:
            colspan_value = cells[0].get("colspan", None)
            return colspan_value is None

        return False

    @property
    def date(self):
        cells = self.html.xpath('td[@data-stat="date"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def points_scored(self):
        cells = self.html.xpath('td[@data-stat="pts"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""
