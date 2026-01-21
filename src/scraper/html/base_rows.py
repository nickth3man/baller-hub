"""Base classes for HTML table rows."""


class BasicBoxScoreRow:
    """
    Base DOM wrapper for a single row in a box score table.

    This class extracts raw string data from an `lxml.html` table row (<tr>).
    It is designed to be inherited by more specific row types.

    Attributes:
        html (lxml.html.HtmlElement): The raw HTML element for the <tr>.
    """

    def __init__(self, html):
        self.html = html

    @property
    def playing_time(self):
        """String value of minutes played (e.g., '34:12')."""
        cells = self.html.xpath('td[@data-stat="mp"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def minutes_played(self):
        """str: Minutes played."""
        return self.playing_time

    @property
    def made_field_goals(self):
        """str: Made field goals."""
        cells = self.html.xpath('td[@data-stat="fg"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def attempted_field_goals(self):
        """str: Attempted field goals."""
        cells = self.html.xpath('td[@data-stat="fga"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def made_three_point_field_goals(self):
        """str: Made 3-point field goals."""
        cells = self.html.xpath('td[@data-stat="fg3"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def attempted_three_point_field_goals(self):
        """str: Attempted 3-point field goals."""
        cells = self.html.xpath('td[@data-stat="fg3a"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def made_free_throws(self):
        """str: Made free throws."""
        cells = self.html.xpath('td[@data-stat="ft"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def attempted_free_throws(self):
        """str: Attempted free throws."""
        cells = self.html.xpath('td[@data-stat="fta"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def offensive_rebounds(self):
        """str: Offensive rebounds."""
        cells = self.html.xpath('td[@data-stat="orb"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def defensive_rebounds(self):
        """str: Defensive rebounds."""
        cells = self.html.xpath('td[@data-stat="drb"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def assists(self):
        """str: Assists."""
        cells = self.html.xpath('td[@data-stat="ast"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def steals(self):
        """str: Steals."""
        cells = self.html.xpath('td[@data-stat="stl"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def blocks(self):
        """str: Blocks."""
        cells = self.html.xpath('td[@data-stat="blk"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def turnovers(self):
        """str: Turnovers."""
        cells = self.html.xpath('td[@data-stat="tov"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def personal_fouls(self):
        """str: Personal fouls."""
        cells = self.html.xpath('td[@data-stat="pf"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def points(self):
        """str: Points scored."""
        cells = self.html.xpath('td[@data-stat="pts"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def location_abbreviation(self):
        """str: Game location abbreviation (e.g., '@' for away)."""
        cells = self.html.xpath('td[@data-stat="game_location"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def outcome(self):
        """str: Game outcome ('W' or 'L')."""
        cells = self.html.xpath('td[@data-stat="game_result"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def plus_minus(self):
        """str: Plus-minus score."""
        cells = self.html.xpath('td[@data-stat="plus_minus"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def game_score(self):
        """str: Game score metric."""
        cells = self.html.xpath('td[@data-stat="game_score"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""


class PlayerSeasonGameLogRow(BasicBoxScoreRow):
    """
    Row representing a game in a player's season log.
    """

    def __init__(self, html):
        super().__init__(html=html)

    def __eq__(self, other):
        if isinstance(other, PlayerBoxScoreRow):
            return self.html == other.html
        return False

    @property
    def team_abbreviation(self):
        """str: Player's team abbreviation."""
        cells = self.html.xpath('td[@data-stat="team_name_abbr"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def opponent_abbreviation(self):
        """str: Opponent's team abbreviation."""
        cells = self.html.xpath('td[@data-stat="opp_name_abbr"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""


class PlayerBoxScoreRow(BasicBoxScoreRow):
    """
    Row representing a player's stats in a single game box score.
    """

    def __init__(self, html):
        super().__init__(html=html)

    def __eq__(self, other):
        if isinstance(other, PlayerBoxScoreRow):
            return self.html == other.html
        return False

    @property
    def team_abbreviation(self):
        """str: Player's team abbreviation."""
        cells = self.html.xpath('td[@data-stat="team_id"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def opponent_abbreviation(self):
        """str: Opponent's team abbreviation."""
        cells = self.html.xpath('td[@data-stat="opp_id"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""


class PlayerIdentificationRow:
    """
    Mixin for rows that include player identity information.
    """

    def __init__(self, html):
        self.html = html

    @property
    def player_cell(self):
        """lxml.html.HtmlElement | None: The cell containing player info."""
        cells = self.html.xpath('td[@data-stat="player"]')

        if len(cells) > 0:
            return cells[0]

        return None

    @property
    def slug(self):
        """str: Unique player identifier (e.g. 'jamesle01')."""
        cell = self.player_cell
        if cell is None:
            return ""

        return cell.get("data-append-csv")

    @property
    def name(self):
        """str: Player's name."""
        cell = self.player_cell
        if cell is None:
            return ""

        return cell.text_content()


class PlayerGameBoxScoreRow(PlayerBoxScoreRow, PlayerIdentificationRow):
    """
    Row combining player stats and identification.
    """

    def __init__(self, html):
        super().__init__(html)
