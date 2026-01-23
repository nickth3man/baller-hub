"""HTML wrappers for leaders pages on basketball-reference.com."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.html import HtmlElement


@dataclass
class LeadersPage:
    """Wrapper for leaders index or specific stat leader page.

    Attributes:
        html (HtmlElement): The raw HTML element for the page.
    """

    html: HtmlElement

    @property
    def leaders_table_query(self) -> str:
        """str: XPath query for leaders table."""
        return '//table[contains(@class, "stats_table")]'

    @property
    def rows_query(self) -> str:
        """str: XPath query for leader rows."""
        return '//table[contains(@class, "stats_table")]//tbody/tr[not(contains(@class, "thead"))]'

    @property
    def stat_type_query(self) -> str:
        """str: XPath query for stat type."""
        return "//h1"

    @property
    def leader_type_query(self) -> str:
        """str: XPath query for leader type."""
        return "//h1"

    @property
    def rows(self) -> list[LeaderRow]:
        """list[LeaderRow]: Extract leader rows."""
        row_elements = self.html.xpath(self.rows_query)
        return [
            LeaderRow(html=row) for row in row_elements if row.text_content().strip()
        ]

    @property
    def stat_name(self) -> str | None:
        """str | None: Extract stat name from header."""
        elements = self.html.xpath(self.stat_type_query)
        return elements[0].text_content().strip() if elements else None


@dataclass
class CareerLeadersPage(LeadersPage):
    """Wrapper for career leaders page.

    Attributes:
        html (HtmlElement): The raw HTML element for the page.
    """

    @property
    def career_table_query(self) -> str:
        """str: XPath query for career leaders table."""
        return '//table[contains(@class, "stats_table") and contains(@id, "tot")]'


@dataclass
class ActiveLeadersPage(LeadersPage):
    """Wrapper for active leaders page.

    Attributes:
        html (HtmlElement): The raw HTML element for the page.
    """

    @property
    def active_table_query(self) -> str:
        """str: XPath query for active leaders table."""
        return '//table[contains(@class, "stats_table") and contains(@id, "active")]'


@dataclass
class LeaderRow:
    """Wrapper for a single leader row.

    Attributes:
        html (HtmlElement): The raw HTML element for the row.
    """

    html: HtmlElement

    @property
    def rank_query(self) -> str:
        """str: XPath query for rank."""
        return './/td[@data-stat="rank"]'

    @property
    def player_query(self) -> str:
        """str: XPath query for player name."""
        return './/td[@data-stat="player"]/a'

    @property
    def value_query(self) -> str:
        """str: XPath query for stat value."""
        # The data-stat attribute depends on the specific leader page
        return './/td[contains(@data-stat, "pts") or contains(@data-stat, "trb") or contains(@data-stat, "ast")]'

    @property
    def years_query(self) -> str:
        """str: XPath query for years played."""
        return './/td[@data-stat="years"]'

    @property
    def teams_query(self) -> str:
        """str: XPath query for teams played for."""
        return './/td[@data-stat="team_id"]'

    @property
    def rank(self) -> str | None:
        """str | None: Extract rank."""
        elements = self.html.xpath(self.rank_query)
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

        match = re.search(r"/players/\w/(\w+)\.html", href)
        return match.group(1) if match else None

    @property
    def value(self) -> str | None:
        """str | None: Extract stat value."""
        elements = self.html.xpath(self.value_query)
        return elements[0].text_content().strip() if elements else None
