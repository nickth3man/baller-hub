"""HTML wrappers for executive pages on basketball-reference.com."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.html import HtmlElement


@dataclass
class ExecutivePage:
    """Wrapper for executive profile page.

    Attributes:
        html (HtmlElement): The raw HTML element for the page.
    """

    html: HtmlElement

    @property
    def name_query(self) -> str:
        """str: XPath query for executive name."""
        return '//h1[@itemprop="name"]/span'

    @property
    def history_table_query(self) -> str:
        """str: XPath query for executive history table."""
        return '//table[contains(@id, "executive_history")]'

    @property
    def name(self) -> str | None:
        """str | None: Extract executive name."""
        elements = self.html.xpath(self.name_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def rows(self) -> list[ExecutiveHistoryRow]:
        """list[ExecutiveHistoryRow]: Extract history rows."""
        tables = self.html.xpath(self.history_table_query)
        if not tables:
            return []
        row_elements = tables[0].xpath('.//tbody/tr[not(contains(@class, "thead"))]')
        return [ExecutiveHistoryRow(html=row) for row in row_elements]


@dataclass
class ExecutiveHistoryRow:
    """Wrapper for a single executive history row.

    Attributes:
        html (HtmlElement): The raw HTML element for the row.
    """

    html: HtmlElement

    @property
    def season_query(self) -> str:
        """str: XPath query for season."""
        return 'th[@data-stat="season"]/a'

    @property
    def team_query(self) -> str:
        """str: XPath query for team."""
        return 'td[@data-stat="team_id"]/a'

    @property
    def role_query(self) -> str:
        """str: XPath query for role."""
        return 'td[@data-stat="role"]'

    @property
    def season(self) -> str | None:
        """str | None: Extract season."""
        elements = self.html.xpath(self.season_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def team(self) -> str | None:
        """str | None: Extract team abbreviation."""
        elements = self.html.xpath(self.team_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def role(self) -> str | None:
        """str | None: Extract role."""
        elements = self.html.xpath(self.role_query)
        return elements[0].text_content().strip() if elements else None
