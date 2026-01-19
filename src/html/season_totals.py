"""HTML wrappers for season totals pages."""

from .base_rows import PlayerIdentificationRow


class PlayerAdvancedSeasonTotalsTable:
    """
    Wraps the 'Advanced' stats table (PER, Win Shares, BPM, etc.).
    """

    def __init__(self, html):
        self.html = html

    @property
    def rows_query(self):
        """
        str: XPath query to select valid data rows.

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
        """
        Parse rows from the table, optionally filtering combined 'TOT' rows.

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
    """
    Wraps the standard 'Totals' or 'Per Game' table.
    """

    def __init__(self, html):
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
        """
        list[PlayerSeasonTotalsRow]: List of parsed rows, excluding combined 'TOT' rows.
        """
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
    """
    Row containing advanced analytics (PER, WS, etc.).
    """

    def __init__(self, html):
        super().__init__(html=html)

    @property
    def player_cell(self):
        cells = self.html.xpath('td[@data-stat="name_display"]')

        if len(cells) > 0:
            return cells[0]

        return None

    @property
    def slug(self):
        cell = self.player_cell
        if cell is None:
            return ""

        return cell.get("data-append-csv")

    @property
    def name(self):
        cell = self.player_cell
        if cell is None:
            return ""

        return cell.text_content()

    @property
    def position_abbreviations(self):
        cells = self.html.xpath('td[@data-stat="pos"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def age(self):
        cells = self.html.xpath('td[@data-stat="age"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def team_abbreviation(self):
        cells = self.html.xpath('td[@data-stat="team_name_abbr"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def games_played(self):
        cells = self.html.xpath('td[@data-stat="games"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def minutes_played(self):
        cells = self.html.xpath('td[@data-stat="mp"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def player_efficiency_rating(self):
        cells = self.html.xpath('td[@data-stat="per"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def true_shooting_percentage(self):
        cells = self.html.xpath('td[@data-stat="ts_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def three_point_attempt_rate(self):
        cells = self.html.xpath('td[@data-stat="fg3a_per_fga_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def free_throw_attempt_rate(self):
        cells = self.html.xpath('td[@data-stat="fta_per_fga_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def offensive_rebound_percentage(self):
        cells = self.html.xpath('td[@data-stat="orb_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def defensive_rebound_percentage(self):
        cells = self.html.xpath('td[@data-stat="drb_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def total_rebound_percentage(self):
        cells = self.html.xpath('td[@data-stat="trb_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def assist_percentage(self):
        cells = self.html.xpath('td[@data-stat="ast_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def steal_percentage(self):
        cells = self.html.xpath('td[@data-stat="stl_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def block_percentage(self):
        cells = self.html.xpath('td[@data-stat="blk_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def turnover_percentage(self):
        cells = self.html.xpath('td[@data-stat="tov_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def usage_percentage(self):
        cells = self.html.xpath('td[@data-stat="usg_pct"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def offensive_win_shares(self):
        cells = self.html.xpath('td[@data-stat="ows"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def defensive_win_shares(self):
        cells = self.html.xpath('td[@data-stat="dws"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def win_shares(self):
        cells = self.html.xpath('td[@data-stat="ws"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def win_shares_per_48_minutes(self):
        cells = self.html.xpath('td[@data-stat="ws_per_48"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def offensive_plus_minus(self):
        cells = self.html.xpath('td[@data-stat="obpm"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def defensive_plus_minus(self):
        cells = self.html.xpath('td[@data-stat="dbpm"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def plus_minus(self):
        cells = self.html.xpath('td[@data-stat="bpm"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def value_over_replacement_player(self):
        cells = self.html.xpath('td[@data-stat="vorp"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def is_combined_totals(self):
        #  No longer says 'TOT' - now says 2TM, 3TM, etc.
        # Can safely use of 'TM' suffix as an identifier as no team abbreviations
        # end in 'TM'
        return self.team_abbreviation.endswith("TM")


class PlayerSeasonTotalsRow:
    """
    Wraps a row from the standard 'Totals' or 'Per Game' table.

    Maps table cells (td) to properties.
    """

    def __init__(self, html):
        self.html = html

    @property
    def position_abbreviations(self):
        cells = self.html.xpath('td[@data-stat="pos"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def age(self):
        cells = self.html.xpath('td[@data-stat="age"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def games_played(self):
        cells = self.html.xpath('td[@data-stat="games"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def games_started(self):
        cells = self.html.xpath('td[@data-stat="games_started"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def is_combined_totals(self):
        #  No longer says 'TOT' - now says 2TM, 3TM, etc.
        # Can safely use of 'TM' suffix as an identifier as no team abbreviations
        # end in 'TM'
        return self.team_abbreviation.endswith("TM")

    @property
    def team_abbreviation(self):
        cells = self.html.xpath('td[@data-stat="team_name_abbr"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def player_cell(self):
        cells = self.html.xpath('td[@data-stat="name_display"]')

        if len(cells) > 0:
            return cells[0]

        return None

    @property
    def slug(self):
        cell = self.player_cell
        if cell is None:
            return ""

        return cell.get("data-append-csv")

    @property
    def name(self):
        cell = self.player_cell
        if cell is None:
            return ""

        return cell.text_content()

    @property
    def playing_time(self):
        cells = self.html.xpath('td[@data-stat="mp"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def minutes_played(self):
        return self.playing_time

    @property
    def made_field_goals(self):
        cells = self.html.xpath('td[@data-stat="fg"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def attempted_field_goals(self):
        cells = self.html.xpath('td[@data-stat="fga"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def made_three_point_field_goals(self):
        cells = self.html.xpath('td[@data-stat="fg3"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def attempted_three_point_field_goals(self):
        cells = self.html.xpath('td[@data-stat="fg3a"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def made_free_throws(self):
        cells = self.html.xpath('td[@data-stat="ft"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def attempted_free_throws(self):
        cells = self.html.xpath('td[@data-stat="fta"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def offensive_rebounds(self):
        cells = self.html.xpath('td[@data-stat="orb"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def defensive_rebounds(self):
        cells = self.html.xpath('td[@data-stat="drb"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def assists(self):
        cells = self.html.xpath('td[@data-stat="ast"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def steals(self):
        cells = self.html.xpath('td[@data-stat="stl"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def blocks(self):
        cells = self.html.xpath('td[@data-stat="blk"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def turnovers(self):
        cells = self.html.xpath('td[@data-stat="tov"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def personal_fouls(self):
        cells = self.html.xpath('td[@data-stat="pf"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def points(self):
        cells = self.html.xpath('td[@data-stat="pts"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""
