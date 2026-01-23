"""HTML wrappers for referee pages on basketball-reference.com."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.html import HtmlElement


@dataclass
class RefereePage:
    """Wrapper for referee profile page.

    Attributes:
        html (HtmlElement): The raw HTML element for the page.
    """

    html: HtmlElement

    @property
    def name_query(self) -> str:
        """str: XPath query for referee name."""
        return '//h1[@itemprop="name"]/span'

    @property
    def history_table_query(self) -> str:
        """str: XPath query for referee history table."""
        return '//table[contains(@id, "referee_history")]'

    @property
    def name(self) -> str | None:
        """str | None: Extract referee name."""
        elements = self.html.xpath(self.name_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def rows(self) -> list[RefereeHistoryRow]:
        """list[RefereeHistoryRow]: Extract history rows."""
        tables = self.html.xpath(self.history_table_query)
        if not tables:
            return []
        row_elements = tables[0].xpath('.//tbody/tr[not(contains(@class, "thead"))]')
        return [RefereeHistoryRow(html=row) for row in row_elements]


@dataclass
class RefereeHistoryRow:
    """Wrapper for a single referee history row.

    Attributes:
        html (HtmlElement): The raw HTML element for the row.
    """

    html: HtmlElement

    @property
    def season_query(self) -> str:
        """str: XPath query for season."""
        return 'th[@data-stat="season"]/a'

    @property
    def games_query(self) -> str:
        """str: XPath query for games officiated."""
        return 'td[@data-stat="g"]'

    @property
    def fouls_query(self) -> str:
        """str: XPath query for fouls called."""
        return 'td[@data-stat="fouls"]'

    @property
    def season(self) -> str | None:
        """str | None: Extract season."""
        elements = self.html.xpath(self.season_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def games(self) -> str | None:
        """str | None: Extract number of games."""
        elements = self.html.xpath(self.games_query)
        return elements[0].text_content().strip() if elements else None
