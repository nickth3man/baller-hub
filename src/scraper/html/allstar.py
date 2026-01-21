"""HTML wrappers for All-Star game pages on basketball-reference.com."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.html import HtmlElement


@dataclass
class AllStarPage:
    """Wrapper for All-Star Game results page."""

    html: HtmlElement

    @property
    def box_score_tables_query(self) -> str:
        """XPath query for box score tables."""
        return '//table[contains(@class, "stats_table")]'

    @property
    def east_roster_query(self) -> str:
        """XPath query for East roster."""
        return '//table[contains(@id, "EAS")]'

    @property
    def west_roster_query(self) -> str:
        """XPath query for West roster."""
        return '//table[contains(@id, "WST")]'

    @property
    def game_info_query(self) -> str:
        """XPath query for game info."""
        return '//div[@id="meta"]'

    @property
    def mvp_query(self) -> str:
        """XPath query for All-Star MVP."""
        return '//div[@id="meta"]//strong[contains(text(), "MVP")]/..'

    @property
    def final_score_query(self) -> str:
        """XPath query for final score."""
        return '//div[@class="scorebox"]'

    @property
    def mvp(self) -> str | None:
        """Extract All-Star MVP name."""
        elements = self.html.xpath(self.mvp_query)
        if not elements:
            return None
        text = elements[0].text_content()
        if "MVP:" in text:
            return text.split("MVP:")[1].strip()
        return None

    @property
    def east_rows(self) -> list[AllStarPlayerRow]:
        """Extract East roster rows."""
        tables = self.html.xpath(self.east_roster_query)
        if not tables:
            return []
        row_elements = tables[0].xpath('.//tbody/tr[not(contains(@class, "thead"))]')
        return [AllStarPlayerRow(html=row) for row in row_elements if row.text_content().strip()]

    @property
    def west_rows(self) -> list[AllStarPlayerRow]:
        """Extract West roster rows."""
        tables = self.html.xpath(self.west_roster_query)
        if not tables:
            return []
        row_elements = tables[0].xpath('.//tbody/tr[not(contains(@class, "thead"))]')
        return [AllStarPlayerRow(html=row) for row in row_elements if row.text_content().strip()]


@dataclass
class AllStarPlayerRow:
    """Wrapper for a single All-Star player row."""

    html: HtmlElement

    @property
    def player_name_query(self) -> str:
        """XPath query for player name."""
        return './/th[@data-stat="player"]/a'

    @property
    def minutes_query(self) -> str:
        """XPath query for minutes played."""
        return './/td[@data-stat="mp"]'

    @property
    def points_query(self) -> str:
        """XPath query for points."""
        return './/td[@data-stat="pts"]'

    @property
    def rebounds_query(self) -> str:
        """XPath query for rebounds."""
        return './/td[@data-stat="trb"]'

    @property
    def assists_query(self) -> str:
        """XPath query for assists."""
        return './/td[@data-stat="ast"]'

    @property
    def starter_query(self) -> str:
        """XPath query for starter status."""
        # Starters are usually the first 5 rows and not marked with specific data-stat
        # But we can check if they have a 'span' or specific class if applicable
        return None

    @property
    def player_name(self) -> str | None:
        """Extract player name."""
        elements = self.html.xpath(self.player_name_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def player_id(self) -> str | None:
        """Extract player ID from href."""
        elements = self.html.xpath(self.player_name_query)
        if not elements:
            return None
        href = elements[0].get("href", "")
        import re
        match = re.search(r"/players/\w/(\w+)\.html", href)
        return match.group(1) if match else None

    @property
    def points(self) -> str | None:
        """Extract points."""
        elements = self.html.xpath(self.points_query)
        return elements[0].text_content().strip() if elements else None
