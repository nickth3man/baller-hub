"""HTML wrappers for player game log pages."""

from .base_rows import PlayerSeasonGameLogRow


class PlayerSeasonBoxScoresPage:
    """Wraps the Player Gamelog page (e.g., /players/j/jamesle01/gamelog/2024).

    Contains tables for both Regular Season and Playoff games.

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
    def regular_season_box_scores_table_query(self):
        """str: XPath for the regular season table."""
        return '//table[@id="player_game_log_reg"]'

    @property
    def regular_season_box_scores_table(self):
        """PlayerSeasonBoxScoresTable | None: The regular season table if present."""
        matching_tables = self.html.xpath(self.regular_season_box_scores_table_query)

        if len(matching_tables) != 1:
            return None

        return PlayerSeasonBoxScoresTable(html=matching_tables[0])

    @property
    def playoff_box_scores_table_query(self):
        """str: XPath for the playoff table."""
        return '//table[@id="player_game_log_post"]'

    @property
    def playoff_box_scores_table(self):
        """PlayerSeasonBoxScoresTable | None: The playoff table if present."""
        matching_tables = self.html.xpath(self.playoff_box_scores_table_query)

        if len(matching_tables) != 1:
            return None

        return PlayerSeasonBoxScoresTable(html=matching_tables[0])


class PlayerSeasonBoxScoresTable:
    """Wraps a specific gamelog table (Regular Season or Playoffs).

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
    def rows_query(self):
        """str: XPath to select valid data rows, filtering out headers and spacers."""
        # Every 20 rows, there's a row that has column header values - those should be ignored
        return 'tbody/tr[not(contains(@class, "spacer")) and not(contains(@class, "thead"))]'

    @property
    def rows(self):
        """list[PlayerSeasonBoxScoresRow]: List of parsed rows."""
        return [
            PlayerSeasonBoxScoresRow(html=row_html)
            for row_html in self.html.xpath(self.rows_query)
        ]


class PlayerSeasonBoxScoresRow(PlayerSeasonGameLogRow):
    """Single row in a player's gamelog table.

    Attributes:
        html (lxml.html.HtmlElement): The raw HTML element for the row.
    """

    def __init__(self, html):
        """Initialize the row wrapper.

        Args:
            html (lxml.html.HtmlElement): The raw HTML element for the row.
        """
        super().__init__(html)

    def __eq__(self, other):
        """Check if two rows represent the same HTML element.

        Args:
            other (object): The other object to compare.

        Returns:
            bool: True if the rows wrap the same HTML element, False otherwise.
        """
        if isinstance(other, PlayerSeasonBoxScoresRow):
            return self.html == other.html
        return False

    __hash__ = None

    @property
    def is_active(self):
        """bool: True if the player played in the game (not DNP/Inactive).

        Determined by checking if the 'is_starter' column spans multiple columns
        (which happens when a 'Did Not Play' message is displayed).
        """
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
        """str: Date of the game."""
        cells = self.html.xpath('td[@data-stat="date"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def points_scored(self):
        """str: Points scored in the game."""
        cells = self.html.xpath('td[@data-stat="pts"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""
