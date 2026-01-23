"""HTML wrappers for schedule pages."""


class SchedulePage:
    """Wraps a monthly schedule page (e.g., /leagues/NBA_2024_games-october.html).

    This page contains:
    1. A table of games for the current month.
    2. Links to schedule pages for other months in the season.

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
    def other_months_schedule_links_query(self):
        """str: XPath query for links to other months' schedules."""
        return (
            '//div[@id="content"]'
            '/div[@class="filter"]'
            '/div[not(contains(@class, "current"))]'
            "/a"
        )

    @property
    def rows_query(self):
        """str: XPath query for the game rows in the current month's table."""
        return '//table[@id="schedule"]//tbody/tr'

    @property
    def other_months_schedule_urls(self):
        """list[str]: URLs for other months in the same season."""
        links = self.html.xpath(self.other_months_schedule_links_query)
        return [link.attrib["href"] for link in links]

    @property
    def rows(self):
        """list[ScheduleRow]: List of game rows for the current month."""
        return [
            ScheduleRow(html=row)
            for row in self.html.xpath(self.rows_query)
            # Every row in each month's schedule table represents a game
            # except for the row where only content is "Playoffs"
            # or blank/header rows.
            if row.text_content() != "Playoffs"
        ]


class ScheduleRow:
    """Wraps a single game row in the schedule table.

    Attributes:
        html (lxml.html.HtmlElement): The raw HTML element for the row.
    """

    def __init__(self, html):
        """Initialize the row wrapper.

        Args:
            html (lxml.html.HtmlElement): The raw HTML element for the row.
        """
        self.html = html

    def __eq__(self, other):
        """Check if two rows represent the same HTML element.

        Args:
            other (object): The other object to compare.

        Returns:
            bool: True if the rows wrap the same HTML element, False otherwise.
        """
        if isinstance(other, ScheduleRow):
            return self.html == other.html
        return False

    __hash__ = None

    @property
    def start_date(self):
        """str: Date of the game."""
        cells = self.html.xpath('th[@data-stat="date_game"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def start_time_of_day(self):
        """str: Start time (ET) of the game."""
        cells = self.html.xpath('td[@data-stat="game_start_time"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def away_team_name(self):
        """str: Visitor team name."""
        cells = self.html.xpath('td[@data-stat="visitor_team_name"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def home_team_name(self):
        """str: Home team name."""
        cells = self.html.xpath('td[@data-stat="home_team_name"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def away_team_score(self):
        """str: Visitor team score (if game played)."""
        cells = self.html.xpath('td[@data-stat="visitor_pts"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def home_team_score(self):
        """str: Home team score (if game played)."""
        cells = self.html.xpath('td[@data-stat="home_pts"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""
