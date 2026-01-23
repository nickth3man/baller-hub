"""HTML wrappers for player profile pages."""


class PlayerPageTotalsRow:
    """Single row in the player's 'Totals' table (stats per season).

    Attributes:
        html (lxml.html.HtmlElement): The raw HTML element for the row.
    """

    def __init__(self, html):
        """Initialize the row wrapper.

        Args:
            html (lxml.html.HtmlElement): The raw HTML element for the row.
        """
        self.html = html

    @property
    def league_abbreviation(self):
        """str | None: League abbreviation (e.g. 'NBA', 'ABA') if present."""
        league_abbreviation_cells = self.html.xpath('.//td[@data-stat="lg_id"]')

        if len(league_abbreviation_cells) > 0:
            return league_abbreviation_cells[0].text_content()

        return None

    def __eq__(self, other):
        """Check if two rows represent the same HTML element.

        Args:
            other (object): The other object to compare.

        Returns:
            bool: True if the rows wrap the same HTML element, False otherwise.
        """
        if isinstance(other, PlayerPageTotalsRow):
            return self.html == other.html
        return False

    __hash__ = None


class PlayerPageTotalsTable:
    """Wrapper for the 'Totals' table on a player page.

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
    def rows(self):
        """list[PlayerPageTotalsRow]: List of season data rows."""
        return [
            PlayerPageTotalsRow(html=row_html)
            for row_html in self.html.xpath(".//tbody/tr")
        ]

    def __eq__(self, other):
        """Check if two tables represent the same HTML element.

        Args:
            other (object): The other object to compare.

        Returns:
            bool: True if the tables wrap the same HTML element, False otherwise.
        """
        if isinstance(other, PlayerPageTotalsTable):
            return self.html == other.html
        return False

    __hash__ = None


class PlayerPage:
    """Wraps a player's profile page (e.g., /players/j/jamesle01.html).

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
    def name(self):
        """str | None: The player's full name from the page header."""
        name_headers = self.html.xpath('.//h1[@itemprop="name"]')

        if len(name_headers) > 0:
            return name_headers[0].text_content().strip()

        return None

    @property
    def totals_table(self):
        """PlayerPageTotalsTable | None: The 'Totals' table if it exists."""
        totals_tables = self.html.xpath('.//table[@id="per_game"]')

        if len(totals_tables) > 0:
            return PlayerPageTotalsTable(html=totals_tables[0])

        return None
