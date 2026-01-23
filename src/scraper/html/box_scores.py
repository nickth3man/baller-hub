"""
DOM Wrappers for Box Score pages.

ARCHITECTURAL PATTERN:
These classes wrap `lxml.html` elements to provide a Pythonic API over the DOM.
They use XPath to locate data but DO NOT parse values (returning raw strings).

Example:
    page = BoxScoresPage(lxml_tree)
    tables = page.basic_statistics_tables  # Returns StatisticsTable objects
    row = tables[0].team_totals            # Returns BasicBoxScoreRow object
"""

import re

from .base_rows import BasicBoxScoreRow


class BoxScoresPage:
    """Wraps the full HTML page of a game box score.

    Identifies and provides access to all statistical tables on the page.

    Attributes:
        html (lxml.html.HtmlElement): The raw HTML element for the page.
    """

    def __init__(self, html):
        """Initialize the page wrapper.

        Args:
            html (lxml.html.HtmlElement): The raw HTML element for the page.
        """
        self.html = html

    @property
    def statistics_tables(self):
        """list[StatisticsTable]: All stat tables found on the page (Basic and Advanced)."""
        return [
            StatisticsTable(table_html)
            for table_html in self.html.xpath(
                '//table[contains(@class, "stats_table")]'
            )
        ]

    @property
    def basic_statistics_tables(self):
        """list[StatisticsTable]: Filter for only the 'Basic' stats tables (ignoring Advanced)."""
        return [
            table
            for table in self.statistics_tables
            if table.has_basic_statistics is True
        ]


class StatisticsTable:
    """Wraps a single statistical table (e.g., 'Boston Celtics Basic Stats').

    Attributes:
        html (lxml.html.HtmlElement): The raw HTML element for the table.
    """

    def __init__(self, html):
        """Initialize the table wrapper.

        Args:
            html (lxml.html.HtmlElement): The raw HTML element for the table.
        """
        self.html = html

    @property
    def has_basic_statistics(self):
        """bool: True if this table contains basic box score stats (PTS, REB, AST)."""
        return "game-basic" in self.html.attrib["id"]

    @property
    def team_abbreviation(self):
        """str: The 3-letter abbreviation of the team (e.g., 'BOS').

        Extracted from the table ID (e.g., 'box-BOS-game-basic').
        """
        # Example id value is box-BOS-game-basic or box-BOS-game-advanced
        match = re.match("^box-(.+)-game", self.html.attrib["id"])
        if match:
            return match.group(1)
        return ""

    @property
    def team_totals(self):
        """BasicBoxScoreRow | None: The footer row containing team aggregate totals."""
        # Team totals are stored as table footers
        footers = self.html.xpath("tfoot/tr")
        if len(footers) > 0:
            return BasicBoxScoreRow(html=footers[0])

        return None
