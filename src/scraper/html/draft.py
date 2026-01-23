"""HTML wrappers for draft pages on basketball-reference.com."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.html import HtmlElement


@dataclass
class DraftPage:
    """Wrapper for draft page.

    Attributes:
        html (HtmlElement): The raw HTML element for the page.
    """

    html: HtmlElement

    @property
    def draft_table_query(self) -> str:
        """str: XPath query for draft table."""
        return '//table[@id="stats"]'

    @property
    def rows_query(self) -> str:
        """str: XPath query for draft rows."""
        return '//table[@id="stats"]//tbody/tr[not(contains(@class, "thead"))]'

    @property
    def year_query(self) -> str:
        """str: XPath query for draft year."""
        return "//h1"

    @property
    def draft_table(self) -> HtmlElement | None:
        """HtmlElement | None: Extract draft table if present."""
        tables = self.html.xpath(self.draft_table_query)
        return tables[0] if tables else None

    @property
    def rows(self) -> list[DraftRow]:
        """list[DraftRow]: Extract draft rows."""
        row_elements = self.html.xpath(self.rows_query)
        return [
            DraftRow(html=row)
            for row in row_elements
            if row.text_content().strip()  # Skip empty rows
        ]

    @property
    def year(self) -> str | None:
        """str | None: Extract draft year from page header."""
        elements = self.html.xpath(self.year_query)
        if not elements:
            return None
        text = elements[0].text_content()
        # Extract year from text like "2024 NBA Draft"
        import re

        match = re.search(r"\d{4}", text)
        return match.group() if match else None


@dataclass
class DraftRow:
    """Wrapper for a single draft pick row.

    Attributes:
        html (HtmlElement): The raw HTML element for the row.
    """

    html: HtmlElement

    @property
    def pick_query(self) -> str:
        """str: XPath query for overall pick number."""
        return 'td[@data-stat="pick_overall"]'

    @property
    def round_query(self) -> str:
        """str: XPath query for round pick."""
        return 'td[@data-stat="round_pick"]'

    @property
    def team_query(self) -> str:
        """str: XPath query for team."""
        return 'td[@data-stat="team_id"]/a'

    @property
    def player_query(self) -> str:
        """str: XPath query for player name."""
        return 'td[@data-stat="player"]/a'

    @property
    def college_query(self) -> str:
        """str: XPath query for college."""
        return 'td[@data-stat="college_name"]/a'

    @property
    def years_active_query(self) -> str:
        """str: XPath query for years active in NBA."""
        return 'td[@data-stat="years_played"]'

    @property
    def pick(self) -> str | None:
        """str | None: Extract overall pick number."""
        elements = self.html.xpath(self.pick_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def round_pick(self) -> str | None:
        """str | None: Extract round pick number."""
        elements = self.html.xpath(self.round_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def team(self) -> str | None:
        """str | None: Extract team abbreviation."""
        elements = self.html.xpath(self.team_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def player(self) -> str | None:
        """str | None: Extract player name."""
        elements = self.html.xpath(self.player_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def player_id(self) -> str | None:
        """str | None: Extract player ID from href."""
        elements = self.html.xpath(self.player_query)
        if not elements:
            return None
        href = elements[0].get("href", "")
        # Extract ID from href like "/players/l/lillada01.html"
        import re

        match = re.search(r"/players/\w/(\w+)\.html", href)
        return match.group(1) if match else None

    @property
    def college(self) -> str | None:
        """str | None: Extract college name."""
        elements = self.html.xpath(self.college_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def years_active(self) -> str | None:
        """str | None: Extract years active."""
        elements = self.html.xpath(self.years_active_query)
        return elements[0].text_content().strip() if elements else None
