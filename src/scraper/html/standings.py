"""HTML wrappers for standings pages."""


class StandingsPage:
    """DOM wrapper for the Season Standings page.

    Parses the full standings page (e.g. /leagues/NBA_2024.html) to extract
    division tables.

    Attributes:
        html (lxml.html.HtmlElement): The raw HTML element for the page.
    """

    def __init__(self, html):
        """Initialize the page wrapper.

        Args:
            html (lxml.html.HtmlElement): The root HTML element of the page.
        """
        self.html = html

    @property
    def division_standings(self):
        """DivisionStandings: The container for both conference tables."""
        division_standings = self.html.xpath('.//div[@id="all_standings"]')

        if len(division_standings) == 1:
            return DivisionStandings(html=division_standings[0])

        return None


class DivisionStandings:
    """Wrapper for the division standings section containing East/West tables.

    Attributes:
        html (lxml.html.HtmlElement): The raw HTML element for the section.
    """

    def __init__(self, html):
        """Initialize the section wrapper.

        Args:
            html (lxml.html.HtmlElement): The raw HTML element for the section.
        """
        self.html = html

    @property
    def eastern_conference_table(self):
        """ConferenceDivisionStandingsTable: The Eastern Conference standings table."""
        tables = self.html.xpath('.//table[@id="divs_standings_E"]')

        if len(tables) == 1:
            return ConferenceDivisionStandingsTable(html=tables[0])

        return None

    @property
    def western_conference_table(self):
        """ConferenceDivisionStandingsTable: The Western Conference standings table."""
        tables = self.html.xpath('.//table[@id="divs_standings_W"]')

        if len(tables) == 1:
            return ConferenceDivisionStandingsTable(html=tables[0])

        return None


class ConferenceDivisionStandingsTable:
    """Table containing standings for all divisions in a conference.

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
        """list[ConferenceDivisionStandingsRow]: List of all rows in the table."""
        return [
            ConferenceDivisionStandingsRow(html=row_html)
            for row_html in self.html.xpath(".//tbody/tr")
        ]


class ConferenceDivisionStandingsRow:
    """Single row in a division standings table.

    Can represent either a Division header (e.g. "Atlantic Division")
    or a Team row (e.g. "Boston Celtics").

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
    def is_division_name_row(self):
        """bool: True if this row represents a Division header."""
        return self.html.attrib["class"] == "thead"

    @property
    def is_standings_row(self):
        """bool: True if this row represents a Team's standings."""
        return self.html.attrib["class"] == "full_table"

    @property
    def division_name(self):
        """str | None: The name of the division (if this is a header row)."""
        cells = self.html.xpath(".//th")

        if len(cells) == 1:
            return cells[0].text_content()

        return None

    @property
    def team_name(self):
        """str | None: Name of the team."""
        cells = self.html.xpath('.//th[@data-stat="team_name"]')

        if len(cells) == 1:
            return cells[0].text_content()

        return None

    @property
    def wins(self):
        """str | None: Number of wins."""
        cells = self.html.xpath('.//td[@data-stat="wins"]')

        if len(cells) == 1:
            return cells[0].text_content()

        return None

    @property
    def losses(self):
        """str | None: Number of losses."""
        cells = self.html.xpath('.//td[@data-stat="losses"]')

        if len(cells) == 1:
            return cells[0].text_content()

        return None
