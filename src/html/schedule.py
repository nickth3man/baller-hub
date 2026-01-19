

class SchedulePage:
    def __init__(self, html):
        self.html = html

    @property
    def other_months_schedule_links_query(self):
        return (
            '//div[@id="content"]'
            '/div[@class="filter"]'
            '/div[not(contains(@class, "current"))]'
            "/a"
        )

    @property
    def rows_query(self):
        return '//table[@id="schedule"]//tbody/tr'

    @property
    def other_months_schedule_urls(self):
        links = self.html.xpath(self.other_months_schedule_links_query)
        return [link.attrib["href"] for link in links]

    @property
    def rows(self):
        return [
            ScheduleRow(html=row)
            for row in self.html.xpath(self.rows_query)
            # Every row in each month's schedule table represents a game
            # except for the row where only content is "Playoffs"
            if row.text_content() != "Playoffs"
        ]


class ScheduleRow:
    def __init__(self, html):
        self.html = html

    def __eq__(self, other):
        if isinstance(other, ScheduleRow):
            return self.html == other.html
        return False

    @property
    def start_date(self):
        cells = self.html.xpath('th[@data-stat="date_game"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def start_time_of_day(self):
        cells = self.html.xpath('td[@data-stat="game_start_time"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def away_team_name(self):
        cells = self.html.xpath('td[@data-stat="visitor_team_name"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def home_team_name(self):
        cells = self.html.xpath('td[@data-stat="home_team_name"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def away_team_score(self):
        cells = self.html.xpath('td[@data-stat="visitor_pts"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""

    @property
    def home_team_score(self):
        cells = self.html.xpath('td[@data-stat="home_pts"]')

        if len(cells) > 0:
            return cells[0].text_content()

        return ""
