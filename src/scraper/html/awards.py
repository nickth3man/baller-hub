"""HTML wrappers for awards pages on basketball-reference.com."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.html import HtmlElement


@dataclass
class AwardsPage:
    """Wrapper for awards page (MVP, DPOY, ROY, etc.)."""

    html: HtmlElement

    @property
    def awards_table_query(self) -> str:
        """XPath query for awards table."""
        return '//table[contains(@class, "stats_table")]'

    @property
    def rows_query(self) -> str:
        """XPath query for award rows."""
        return '//table[contains(@class, "stats_table")]//tbody/tr[not(contains(@class, "thead"))]'

    @property
    def header_query(self) -> str:
        """XPath query for page header."""
        return '//h1'

    @property
    def awards_table(self) -> HtmlElement | None:
        """Extract awards table if present."""
        tables = self.html.xpath(self.awards_table_query)
        return tables[0] if tables else None

    @property
    def rows(self) -> list[AwardRow]:
        """Extract award rows."""
        row_elements = self.html.xpath(self.rows_query)
        return [
            AwardRow(html=row)
            for row in row_elements
            if row.text_content().strip()
        ]

    @property
    def award_name(self) -> str | None:
        """Extract award name from page header."""
        elements = self.html.xpath(self.header_query)
        return elements[0].text_content().strip() if elements else None


@dataclass
class AwardRow:
    """Wrapper for a single award winner row."""

    html: HtmlElement

    @property
    def season_query(self) -> str:
        """XPath query for season."""
        return 'th[@data-stat="season"]/a'

    @property
    def player_query(self) -> str:
        """XPath query for player name."""
        return 'td[@data-stat="player"]/a'

    @property
    def team_query(self) -> str:
        """XPath query for team."""
        return 'td[@data-stat="team_id"]/a'

    @property
    def age_query(self) -> str:
        """XPath query for age."""
        return 'td[@data-stat="age"]'

    @property
    def voting_share_query(self) -> str:
        """XPath query for voting share."""
        return 'td[@data-stat="award_share"]'

    @property
    def season(self) -> str | None:
        """Extract season."""
        elements = self.html.xpath(self.season_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def player(self) -> str | None:
        """Extract player name."""
        elements = self.html.xpath(self.player_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def player_id(self) -> str | None:
        """Extract player ID from href."""
        elements = self.html.xpath(self.player_query)
        if not elements:
            return None
        href = elements[0].get("href", "")
        import re

        match = re.search(r"/players/\w/(\w+)\.html", href)
        return match.group(1) if match else None

    @property
    def team(self) -> str | None:
        """Extract team abbreviation."""
        elements = self.html.xpath(self.team_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def age(self) -> str | None:
        """Extract age."""
        elements = self.html.xpath(self.age_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def voting_share(self) -> str | None:
        """Extract voting share."""
        elements = self.html.xpath(self.voting_share_query)
        return elements[0].text_content().strip() if elements else None


@dataclass
class HallOfFamePage:
    """Wrapper for Hall of Fame page."""

    html: HtmlElement

    @property
    def inductees_table_query(self) -> str:
        """XPath query for inductees table."""
        return '//table[contains(@class, "stats_table")]'

    @property
    def rows_query(self) -> str:
        """XPath query for inductee rows."""
        return '//table[contains(@class, "stats_table")]//tbody/tr[not(contains(@class, "thead"))]'

    @property
    def rows(self) -> list[HallOfFameRow]:
        """Extract inductee rows."""
        row_elements = self.html.xpath(self.rows_query)
        return [
            HallOfFameRow(html=row)
            for row in row_elements
            if row.text_content().strip()
        ]


@dataclass
class HallOfFameRow:
    """Wrapper for a single Hall of Fame inductee row."""

    html: HtmlElement

    @property
    def year_query(self) -> str:
        """XPath query for induction year."""
        return 'th[@data-stat="year_inducted"]'

    @property
    def player_query(self) -> str:
        """XPath query for player name."""
        return 'td[@data-stat="player"]/a'

    @property
    def category_query(self) -> str:
        """XPath query for induction category."""
        return 'td[@data-stat="category"]'

    @property
    def year(self) -> str | None:
        """Extract induction year."""
        elements = self.html.xpath(self.year_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def player(self) -> str | None:
        """Extract player/person name."""
        elements = self.html.xpath(self.player_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def category(self) -> str | None:
        """Extract induction category."""
        elements = self.html.xpath(self.category_query)
        return elements[0].text_content().strip() if elements else None


@dataclass
class AllNBATeamPage:
    """Wrapper for All-NBA team pages."""

    html: HtmlElement

    @property
    def team_tables_query(self) -> str:
        """XPath query for team selection tables."""
        return '//table[contains(@class, "stats_table")]'

    @property
    def first_team_query(self) -> str:
        """XPath query for first team selections."""
        return '//table[contains(@id, "first")]'

    @property
    def rows_query(self) -> str:
        """XPath query for team selection rows."""
        return '//table[contains(@class, "stats_table")]//tbody/tr[not(contains(@class, "thead"))]'

    @property
    def rows(self) -> list[AllNBATeamRow]:
        """Extract team selection rows."""
        row_elements = self.html.xpath(self.rows_query)
        return [
            AllNBATeamRow(html=row)
            for row in row_elements
            if row.text_content().strip()
        ]


@dataclass
class AllNBATeamRow:
    """Wrapper for All-NBA team selection row."""

    html: HtmlElement

    @property
    def season_query(self) -> str:
        """XPath query for season."""
        return 'th[@data-stat="season"]/a'

    @property
    def player_query(self) -> str:
        """XPath query for player name."""
        return 'td[@data-stat="player"]/a'

    @property
    def team_type_query(self) -> str:
        """XPath query for team type (1st, 2nd, 3rd)."""
        return 'td[@data-stat="team_type"]'

    @property
    def season(self) -> str | None:
        """Extract season."""
        elements = self.html.xpath(self.season_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def player(self) -> str | None:
        """Extract player name."""
        elements = self.html.xpath(self.player_query)
        return elements[0].text_content().strip() if elements else None
