

class BasicBoxScoreRow:
    def __init__(self, html):
        self.html = html

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

    @property
    def location_abbreviation(self):
        cells = self.html.xpath('td[@data-stat="game_location"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def outcome(self):
        cells = self.html.xpath('td[@data-stat="game_result"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def plus_minus(self):
        cells = self.html.xpath('td[@data-stat="plus_minus"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def game_score(self):
        cells = self.html.xpath('td[@data-stat="game_score"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""


class PlayerSeasonGameLogRow(BasicBoxScoreRow):
    def __init__(self, html):
        super().__init__(html=html)

    def __eq__(self, other):
        if isinstance(other, PlayerBoxScoreRow):
            return self.html == other.html
        return False

    @property
    def team_abbreviation(self):
        cells = self.html.xpath('td[@data-stat="team_name_abbr"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def opponent_abbreviation(self):
        cells = self.html.xpath('td[@data-stat="opp_name_abbr"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""


class PlayerBoxScoreRow(BasicBoxScoreRow):
    def __init__(self, html):
        super().__init__(html=html)

    def __eq__(self, other):
        if isinstance(other, PlayerBoxScoreRow):
            return self.html == other.html
        return False

    @property
    def team_abbreviation(self):
        cells = self.html.xpath('td[@data-stat="team_id"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def opponent_abbreviation(self):
        cells = self.html.xpath('td[@data-stat="opp_id"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""


class PlayerIdentificationRow:
    def __init__(self, html):
        self.html = html

    @property
    def player_cell(self):
        cells = self.html.xpath('td[@data-stat="player"]')

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


class PlayerGameBoxScoreRow(PlayerBoxScoreRow, PlayerIdentificationRow):
    def __init__(self, html):
        super().__init__(html)
