"""HTML wrappers for play-by-play data."""


class PlayByPlayPage:
    """
    Wraps the Play-by-Play page content.
    """

    def __init__(self, html):
        self.html = html

    @property
    def table_query(self):
        """str: XPath query for the main PBP table."""
        return '//table[@id="pbp"]'

    @property
    def team_names_query(self):
        """str: XPath query for team names in the scorebox."""
        return '//*[@id="content"]//div[@class="scorebox"]//strong//a'

    @property
    def play_by_play_table(self):
        """
        PlayByPlayTable: The main play-by-play table object.
        """
        return PlayByPlayTable(html=self.html.xpath(self.table_query)[0])

    @property
    def team_names(self):
        """
        list[str]: Names of the teams playing (e.g. ['Boston Celtics', 'Los Angeles Lakers']).
        """
        names = self.html.xpath(self.team_names_query)

        return [name.text_content() for name in names]

    @property
    def away_team_name(self):
        """str: Name of the visiting team."""
        return self.team_names[0]

    @property
    def home_team_name(self):
        """Name of the home team."""
        return self.team_names[1]


class PlayByPlayTable:
    """
    Wraps the main table containing all play events.
    """

    def __init__(self, html):
        self.html = html

    @property
    def rows(self):
        """
        list[PlayByPlayRow]: Chronological list of play events.
        """
        return [
            PlayByPlayRow(html=row_html)
            # Ignore first row in table
            for row_html in self.html[1:]
        ]


class PlayByPlayRow:
    """
    Wraps a single row (event) in the play-by-play table.
    """

    def __init__(self, html):
        self.html = html

    @property
    def timestamp_cell(self):
        """lxml.html.HtmlElement: The cell containing the time remaining."""
        return self.html[0]

    @property
    def timestamp(self):
        """str: Time remaining in the period (e.g., '11:45.0')."""
        return self.timestamp_cell.text_content().strip()

    @property
    def away_team_play_description(self):
        """str: Description of the away team's action (if any)."""
        if len(self.html) == 6:
            return self.html[1].text_content().strip()

        return ""

    @property
    def home_team_play_description(self):
        """str: Description of the home team's action (if any)."""
        if len(self.html) == 6:
            return self.html[5].text_content().strip()

        return ""

    @property
    def is_away_team_play(self):
        """bool: True if the event is attributed to the away team."""
        return self.away_team_play_description != ""

    @property
    def is_home_team_play(self):
        """bool: True if the event is attributed to the home team."""
        return self.home_team_play_description != ""

    @property
    def formatted_scores(self):
        """str: Current score (e.g., '10-8')."""
        if len(self.html) == 6:
            return self.html[3].text_content().strip()
        return ""

    @property
    def is_start_of_period(self):
        """bool: True if this row indicates the start of a new quarter/period."""
        return self.timestamp_cell.get("colspan") == "6"

    @property
    def has_play_by_play_data(self):
        """
        bool: True if this row contains valid game event data.

        Filters out period headers, spacers, and invalid rows.
        """
        # TODO: @nickth3man refactor this to be slightly clearer
        # Need to avoid rows that indicate start of period
        # Or denote tipoff / end of period (colspan = 5)
        # Or are one of the table headers for each period group (aria-label = Time)
        # There are certain cases, like at 10 minute mark in https://www.basketball-reference.com/boxscores/pbp/199911160ATL.html
        # where there are no event details. Probably a visual bug on Basketball Reference's side of things.
        return (
            not self.is_start_of_period
            and len(self.html) >= 2
            and self.html[1].get("colspan") != "5"
            and self.timestamp_cell.get("aria-label") != "Time"
        )
