import re

from .base_rows import BasicBoxScoreRow


class BoxScoresPage:
    def __init__(self, html):
        self.html = html

    @property
    def statistics_tables(self):
        return [
            StatisticsTable(table_html)
            for table_html in self.html.xpath(
                '//table[contains(@class, "stats_table")]'
            )
        ]

    @property
    def basic_statistics_tables(self):
        return [
            table
            for table in self.statistics_tables
            if table.has_basic_statistics is True
        ]


class StatisticsTable:
    def __init__(self, html):
        self.html = html

    @property
    def has_basic_statistics(self):
        return "game-basic" in self.html.attrib["id"]

    @property
    def team_abbreviation(self):
        # Example id value is box-BOS-game-basic or box-BOS-game-advanced
        match = re.match("^box-(.+)-game", self.html.attrib["id"])
        if match:
            return match.group(1)
        return ""

    @property
    def team_totals(self):
        # Team totals are stored as table footers
        footers = self.html.xpath("tfoot/tr")
        if len(footers) > 0:
            return BasicBoxScoreRow(html=footers[0])

        return None
