"""HTML wrappers for season totals pages."""

from .base_rows import PlayerIdentificationRow


class PlayerAdvancedSeasonTotalsTable:
    """Wraps the 'Advanced' stats table (PER, Win Shares, BPM, etc.).

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
        """str: XPath query to select valid data rows.

        Excludes header rows and 'League Average' rows (marked with 'norank').
        """
        # Basketball Reference includes individual rows for players that played for multiple teams in a season.
        # It also includes a "League Average" row that has a class value of 'norank'.
        return """
            //table[@id="advanced"]
            /tbody
            /tr[
                (
                    not(contains(@class, 'thead')) and
                    not(contains(@class, 'norank'))
                )
            ]
        """

    def get_rows(self, include_combined_totals=False):
        """Parse rows from the table, optionally filtering combined 'TOT' rows.

        Args:
            include_combined_totals (bool): If True, includes rows representing
                combined stats for players who played for multiple teams.

        Returns:
            list[PlayerAdvancedSeasonTotalsRow]: Parsed rows.
        """
        player_advanced_season_totals_rows = []
        for row_html in self.html.xpath(self.rows_query):
            row = PlayerAdvancedSeasonTotalsRow(html=row_html)
            if (
                include_combined_totals is True and row.is_combined_totals is True
            ) or row.is_combined_totals is False:
                # Basketball Reference includes a "total" row for players that got traded
                # which is essentially a sum of all player team rows
                # I want to avoid including those, so I check the "team" field value for "TOT"
                player_advanced_season_totals_rows.append(row)

        return player_advanced_season_totals_rows


class PlayerSeasonTotalTable:
    """Wraps the standard 'Totals' or 'Per Game' table.

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
        """str: XPath query for valid data rows."""
        # Basketball Reference includes individual rows for players that played for multiple teams in a season.
        # It also includes a "League Average" row that has a class value of 'norank'.
        return """
                    //table[@id='totals_stats']
                    /tbody
                    /tr[
                        not(contains(@class, 'thead')) and
                        not(contains(@class, 'norank'))
                    ]
                """

    @property
    def rows(self):
        """list[PlayerSeasonTotalsRow]: List of parsed rows, excluding combined 'TOT' rows."""
        player_season_totals_rows = []
        for row_html in self.html.xpath(self.rows_query):
            row = PlayerSeasonTotalsRow(html=row_html)
            # Basketball Reference includes a "total" row for players that got traded
            # which is essentially a sum of all player team rows
            # I want to avoid including those, so I check the "team" field value for "TOT"
            if not row.is_combined_totals:
                player_season_totals_rows.append(row)

        return player_season_totals_rows


class PlayerAdvancedSeasonTotalsRow(PlayerIdentificationRow):
    """Row containing advanced analytics (PER, WS, etc.).

    Attributes:
        html (lxml.html.HtmlElement): The raw HTML element for the row.
    """

    def __init__(self, html):
        """Initialize the row wrapper.

        Args:
            html (lxml.html.HtmlElement): The raw HTML element for the row.
        """
        super().__init__(html=html)

    @property
    def player_cell(self):
        """lxml.html.HtmlElement | None: The cell containing player info."""
        cells = self.html.xpath('td[@data-stat="name_display"]')

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

    @property
    def position_abbreviations(self):
        """str: Position abbreviations."""
        cells = self.html.xpath('td[@data-stat="pos"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def age(self):
        """str: Age."""
        cells = self.html.xpath('td[@data-stat="age"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def team_abbreviation(self):
        """str: Team abbreviation."""
        cells = self.html.xpath('td[@data-stat="team_name_abbr"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def games_played(self):
        """str: Games played."""
        cells = self.html.xpath('td[@data-stat="games"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def minutes_played(self):
        """str: Minutes played."""
        cells = self.html.xpath('td[@data-stat="mp"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def player_efficiency_rating(self):
        """str: Player Efficiency Rating (PER)."""
        cells = self.html.xpath('td[@data-stat="per"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def true_shooting_percentage(self):
        """str: True Shooting Percentage (TS%)."""
        cells = self.html.xpath('td[@data-stat="ts_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def three_point_attempt_rate(self):
        """str: 3-Point Attempt Rate."""
        cells = self.html.xpath('td[@data-stat="fg3a_per_fga_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def free_throw_attempt_rate(self):
        """str: Free Throw Attempt Rate."""
        cells = self.html.xpath('td[@data-stat="fta_per_fga_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def offensive_rebound_percentage(self):
        """str: Offensive Rebound Percentage."""
        cells = self.html.xpath('td[@data-stat="orb_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def defensive_rebound_percentage(self):
        """str: Defensive Rebound Percentage."""
        cells = self.html.xpath('td[@data-stat="drb_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def total_rebound_percentage(self):
        """str: Total Rebound Percentage."""
        cells = self.html.xpath('td[@data-stat="trb_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def assist_percentage(self):
        """str: Assist Percentage."""
        cells = self.html.xpath('td[@data-stat="ast_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def steal_percentage(self):
        """str: Steal Percentage."""
        cells = self.html.xpath('td[@data-stat="stl_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def block_percentage(self):
        """str: Block Percentage."""
        cells = self.html.xpath('td[@data-stat="blk_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def turnover_percentage(self):
        """str: Turnover Percentage."""
        cells = self.html.xpath('td[@data-stat="tov_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def usage_percentage(self):
        """str: Usage Percentage."""
        cells = self.html.xpath('td[@data-stat="usg_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def offensive_win_shares(self):
        """str: Offensive Win Shares."""
        cells = self.html.xpath('td[@data-stat="ows"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def defensive_win_shares(self):
        """str: Defensive Win Shares."""
        cells = self.html.xpath('td[@data-stat="dws"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def win_shares(self):
        """str: Win Shares."""
        cells = self.html.xpath('td[@data-stat="ws"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def win_shares_per_48_minutes(self):
        """str: Win Shares Per 48 Minutes."""
        cells = self.html.xpath('td[@data-stat="ws_per_48"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def offensive_plus_minus(self):
        """str: Offensive Box Plus/Minus."""
        cells = self.html.xpath('td[@data-stat="obpm"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def defensive_plus_minus(self):
        """str: Defensive Box Plus/Minus."""
        cells = self.html.xpath('td[@data-stat="dbpm"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def plus_minus(self):
        """str: Box Plus/Minus."""
        cells = self.html.xpath('td[@data-stat="bpm"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def value_over_replacement_player(self):
        """str: Value Over Replacement Player (VORP)."""
        cells = self.html.xpath('td[@data-stat="vorp"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def is_combined_totals(self):
        """bool: True if this row represents combined stats for multiple teams."""
        #  No longer says 'TOT' - now says 2TM, 3TM, etc.
        # Can safely use of 'TM' suffix as an identifier as no team abbreviations
        # end in 'TM'
        return self.team_abbreviation.endswith("TM")


class PlayerSeasonTotalsRow:
    """Wraps a row from the standard 'Totals' or 'Per Game' table.

    Maps table cells (td) to properties.

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
    def position_abbreviations(self):
        """str: Position abbreviations."""
        cells = self.html.xpath('td[@data-stat="pos"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def age(self):
        """str: Age."""
        cells = self.html.xpath('td[@data-stat="age"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def games_played(self):
        """str: Games played."""
        cells = self.html.xpath('td[@data-stat="games"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def games_started(self):
        """str: Games started."""
        cells = self.html.xpath('td[@data-stat="games_started"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def is_combined_totals(self):
        """bool: True if this row represents combined stats for multiple teams."""
        #  No longer says 'TOT' - now says 2TM, 3TM, etc.
        # Can safely use of 'TM' suffix as an identifier as no team abbreviations
        # end in 'TM'
        return self.team_abbreviation.endswith("TM")

    @property
    def team_abbreviation(self):
        """str: Team abbreviation."""
        cells = self.html.xpath('td[@data-stat="team_name_abbr"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def player_cell(self):
        """lxml.html.HtmlElement | None: The cell containing player info."""
        cells = self.html.xpath('td[@data-stat="name_display"]')

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

    @property
    def playing_time(self):
        """str: Playing time."""
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
        """str: Points."""
        cells = self.html.xpath('td[@data-stat="pts"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""
