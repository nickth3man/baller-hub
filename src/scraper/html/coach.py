"""HTML wrappers for coach pages on basketball-reference.com."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.html import HtmlElement


@dataclass
class CoachPage:
    """Wrapper for coach profile page.

    Attributes:
        html (HtmlElement): The raw HTML element for the page.
    """

    html: HtmlElement

    @property
    def coaching_record_table_query(self) -> str:
        """str: XPath query for coaching record table."""
        return '//table[contains(@id, "coach")]'

    @property
    def name_query(self) -> str:
        """str: XPath query for coach name."""
        return '//div[@id="meta"]//h1/span | //h1[@itemprop="name"]/span | //h1/span'

    @property
    def biography_section_query(self) -> str:
        """str: XPath query for biography section."""
        return '//div[@id="meta"]'

    @property
    def coaching_record_table(self) -> HtmlElement | None:
        """HtmlElement | None: Extract coaching record table if present."""
        tables = self.html.xpath(self.coaching_record_table_query)
        return tables[0] if tables else None

    @property
    def name(self) -> str | None:
        """str | None: Extract coach name."""
        elements = self.html.xpath(self.name_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def rows(self) -> list[CoachingRecordRow]:
        """list[CoachingRecordRow]: Extract coaching record rows."""
        table = self.coaching_record_table
        if table is None:
            return []
        row_elements = table.xpath('.//tbody/tr[not(contains(@class, "thead"))]')
        return [CoachingRecordRow(html=row) for row in row_elements]


@dataclass
class CoachingRecordRow:
    """Wrapper for a single coaching record row.

    Attributes:
        html (HtmlElement): The raw HTML element for the row.
    """

    html: HtmlElement

    @property
    def season_query(self) -> str:
        """str: XPath query for season."""
        return 'th[@data-stat="season"]/a | th[@data-stat="season"]'

    @property
    def team_query(self) -> str:
        """str: XPath query for team."""
        return 'td[@data-stat="team_id"]/a'

    @property
    def wins_query(self) -> str:
        """str: XPath query for wins."""
        return 'td[@data-stat="wins"]'

    @property
    def losses_query(self) -> str:
        """str: XPath query for losses."""
        return 'td[@data-stat="losses"]'

    @property
    def win_pct_query(self) -> str:
        """str: XPath query for win percentage."""
        return 'td[@data-stat="win_loss_pct"]'

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
    def wins(self) -> str | None:
        """str | None: Extract wins (as string for parser to convert)."""
        elements = self.html.xpath(self.wins_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def losses(self) -> str | None:
        """str | None: Extract losses (as string for parser to convert)."""
        elements = self.html.xpath(self.losses_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def win_pct(self) -> str | None:
        """str | None: Extract win percentage (as string for parser to convert)."""
        elements = self.html.xpath(self.win_pct_query)
        return elements[0].text_content().strip() if elements else None
