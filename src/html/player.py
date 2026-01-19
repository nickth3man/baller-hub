

class PlayerPageTotalsRow:
    def __init__(self, html):
        self.html = html

    @property
    def league_abbreviation(self):
        league_abbreviation_cells = self.html.xpath('.//td[@data-stat="lg_id"]')

        if len(league_abbreviation_cells) > 0:
            return league_abbreviation_cells[0].text_content()

        return None

    def __eq__(self, other):
        if isinstance(other, PlayerPageTotalsRow):
            return self.html == other.html
        return False


class PlayerPageTotalsTable:
    def __init__(self, html):
        self.html = html

    @property
    def rows(self):
        return [
            PlayerPageTotalsRow(html=row_html)
            for row_html in self.html.xpath(".//tbody/tr")
        ]

    def __eq__(self, other):
        if isinstance(other, PlayerPageTotalsTable):
            return self.html == other.html
        return False


class PlayerPage:
    def __init__(self, html):
        self.html = html

    @property
    def name(self):
        name_headers = self.html.xpath('.//h1[@itemprop="name"]')

        if len(name_headers) > 0:
            return name_headers[0].text_content().strip()

        return None

    @property
    def totals_table(self):
        totals_tables = self.html.xpath('.//table[@id="per_game"]')

        if len(totals_tables) > 0:
            return PlayerPageTotalsTable(html=totals_tables[0])

        return None
