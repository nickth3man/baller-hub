"""HTML wrappers for team season pages on basketball-reference.com."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.html import HtmlElement


@dataclass
class TeamSeasonPage:
    """Wrapper for team season summary page.

    Attributes:
        html (HtmlElement): The raw HTML element for the page.
    """

    html: HtmlElement

    @property
    def roster_table_query(self) -> str:
        """str: XPath query for roster table."""
        return '//table[@id="roster"]'

    @property
    def per_game_table_query(self) -> str:
        """str: XPath query for per-game stats table."""
        return '//table[@id="per_game"]'

    @property
    def totals_table_query(self) -> str:
        """str: XPath query for totals table."""
        return '//table[@id="totals"]'

    @property
    def team_opponent_table_query(self) -> str:
        """str: XPath query for team and opponent stats table."""
        return '//table[@id="team_and_opponent"]'

    @property
    def team_info_query(self) -> str:
        """str: XPath query for team info section."""
        return '//div[@id="meta"]'

    @property
    def record_query(self) -> str:
        """str: XPath query for team record."""
        return '//div[@id="meta"]//p[contains(text(), "Record:")]'

    @property
    def coach_query(self) -> str:
        """str: XPath query for coach."""
        return '//div[@id="meta"]//p[contains(text(), "Coach:")]/a'

    @property
    def roster_rows(self) -> list[RosterRow]:
        """list[RosterRow]: Extract roster rows."""
        tables = self.html.xpath(self.roster_table_query)
        if not tables:
            return []
        row_elements = tables[0].xpath(".//tbody/tr")
        return [RosterRow(html=row) for row in row_elements]

    @property
    def record(self) -> str | None:
        """str | None: Extract team record."""
        elements = self.html.xpath(self.record_query)
        if not elements:
            return None
        text = elements[0].text_content()
        if "Record:" in text:
            # e.g., "Record: 64-18, 1st in NBA Eastern Conference"
            return text.split("Record:")[1].split(",")[0].strip()
        return None


@dataclass
class RosterRow:
    """Wrapper for a single team roster row.

    Attributes:
        html (HtmlElement): The raw HTML element for the row.
    """

    html: HtmlElement

    @property
    def player_name_query(self) -> str:
        """str: XPath query for player name."""
        return './/td[@data-stat="player"]/a'

    @property
    def number_query(self) -> str:
        """str: XPath query for jersey number."""
        return './/th[@data-stat="number"]'

    @property
    def position_query(self) -> str:
        """str: XPath query for position."""
        return './/td[@data-stat="pos"]'

    @property
    def height_query(self) -> str:
        """str: XPath query for height."""
        return './/td[@data-stat="height"]'

    @property
    def weight_query(self) -> str:
        """str: XPath query for weight."""
        return './/td[@data-stat="weight"]'

    @property
    def birth_date_query(self) -> str:
        """str: XPath query for birth date."""
        return './/td[@data-stat="birth_date"]'

    @property
    def college_query(self) -> str:
        """str: XPath query for college."""
        return './/td[@data-stat="college"]'

    @property
    def player_name(self) -> str | None:
        """str | None: Extract player name."""
        elements = self.html.xpath(self.player_name_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def player_id(self) -> str | None:
        """str | None: Extract player ID from href."""
        elements = self.html.xpath(self.player_name_query)
        if not elements:
            return None
        href = elements[0].get("href", "")

        match = re.search(r"/players/\w/(\w+)\.html", href)
        return match.group(1) if match else None


@dataclass
class TeamStatRow:
    """Wrapper for team stat rows (per game, totals, etc.).

    Attributes:
        html (HtmlElement): The raw HTML element for the row.
    """

    html: HtmlElement

    @property
    def player_query(self) -> str:
        """str: XPath query for player name."""
        return './/td[@data-stat="player"]/a'

    @property
    def games_query(self) -> str:
        """str: XPath query for games played."""
        return './/td[@data-stat="g"]'

    @property
    def minutes_query(self) -> str:
        """str: XPath query for minutes played."""
        return './/td[@data-stat="mp"]'

    @property
    def points_query(self) -> str:
        """str: XPath query for points."""
        return './/td[@data-stat="pts"]'
