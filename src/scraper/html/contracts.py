"""HTML wrappers for player contract data."""


class PlayerContractsRow:
    """Wrapper for a single row in the player contracts table.

    Represents a player's contract details including salary projections.

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
    def player_name(self):
        """str | None: Name of the player."""
        matching_cells = self.html.xpath('.//td[@data-stat="player"]')

        if len(matching_cells) == 1:
            return matching_cells[0].text_content()

        return None

    @property
    def player_identifier(self):
        """str | None: Unique identifier for the player."""
        matching_attribute_value = self.html.xpath(".//td/@data-append-csv")
        if len(matching_attribute_value) == 1:
            return matching_attribute_value[0]

        return None

    @property
    def team_abbreviation(self):
        """str | None: Team abbreviation."""
        matching_cells = self.html.xpath('.//td[@data-stat="team_id"]')

        if len(matching_cells) == 1:
            return matching_cells[0].text_content()

        return None

    @property
    def first_contract_year_data(self):
        """tuple(str, list[str]) | None: Salary and CSS classes for year 1."""
        return self.calculate_contract_year_data(
            contract_year_data_stat_attribute_value="y1"
        )

    @property
    def second_contract_year_data(self):
        """tuple(str, list[str]) | None: Salary and CSS classes for year 2."""
        return self.calculate_contract_year_data(
            contract_year_data_stat_attribute_value="y2"
        )

    @property
    def third_contract_year_data(self):
        """tuple(str, list[str]) | None: Salary and CSS classes for year 3."""
        return self.calculate_contract_year_data(
            contract_year_data_stat_attribute_value="y3"
        )

    @property
    def fourth_contract_year_data(self):
        """tuple(str, list[str]) | None: Salary and CSS classes for year 4."""
        return self.calculate_contract_year_data(
            contract_year_data_stat_attribute_value="y4"
        )

    @property
    def fifth_contract_year_data(self):
        """tuple(str, list[str]) | None: Salary and CSS classes for year 5."""
        return self.calculate_contract_year_data(
            contract_year_data_stat_attribute_value="y5"
        )

    @property
    def sixth_contract_year_data(self):
        """tuple(str, list[str]) | None: Salary and CSS classes for year 6."""
        return self.calculate_contract_year_data(
            contract_year_data_stat_attribute_value="y6"
        )

    @property
    def guaranteed(self):
        """str | None: Total guaranteed amount."""
        matching_cells = self.html.xpath('.//td[@data-stat="remain_gtd"]')

        if len(matching_cells) == 1:
            return matching_cells[0].text_content()

        return None

    def calculate_contract_year_data(self, contract_year_data_stat_attribute_value):
        """Extracts salary and style info for a specific contract year column.

        Args:
            contract_year_data_stat_attribute_value (str): The data-stat value (e.g. "y1").

        Returns:
            tuple: (salary_string, list_of_css_classes)
        """
        matching_cells = self.html.xpath(
            f'.//td[@data-stat="{contract_year_data_stat_attribute_value}"]'
        )

        if len(matching_cells) == 1:
            salary = matching_cells[0].text_content()
            class_names = matching_cells[0].get("class")

            return salary, class_names

        return None
