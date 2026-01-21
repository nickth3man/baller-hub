"""HTML wrappers for playoff pages on basketball-reference.com."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.html import HtmlElement


@dataclass
class PlayoffsPage:
    """Wrapper for playoff summary page."""

    html: HtmlElement

    @property
    def bracket_query(self) -> str:
        """XPath query for playoff bracket."""
        return '//div[contains(@class, "playoff")]'

    @property
    def series_links_query(self) -> str:
        """XPath query for series links."""
        return '//div[contains(@class, "playoff")]//a[contains(@href, "playoffs")]'

    @property
    def champion_query(self) -> str:
        """XPath query for champion."""
        return '//div[@id="meta"]//strong[contains(text(), "Champion")]/..'

    @property
    def finals_mvp_query(self) -> str:
        """XPath query for Finals MVP."""
        return '//div[@id="meta"]//strong[contains(text(), "Finals MVP")]/..'

    @property
    def champion(self) -> str | None:
        """Extract champion team name."""
        elements = self.html.xpath(self.champion_query)
        if not elements:
            return None
        text = elements[0].text_content()
        # Extract team name after "Champion:"
        if "Champion:" in text:
            return text.split("Champion:")[1].strip()
        return None

    @property
    def finals_mvp(self) -> str | None:
        """Extract Finals MVP name."""
        elements = self.html.xpath(self.finals_mvp_query)
        if not elements:
            return None
        text = elements[0].text_content()
        if "Finals MVP:" in text:
            return text.split("Finals MVP:")[1].strip()
        return None

    @property
    def series_links(self) -> list[str]:
        """Extract links to individual series pages."""
        elements = self.html.xpath(self.series_links_query)
        return [el.get("href", "") for el in elements if el.get("href")]


@dataclass
class PlayoffSeriesPage:
    """Wrapper for individual playoff series page."""

    html: HtmlElement

    @property
    def series_result_query(self) -> str:
        """XPath query for series result."""
        return '//div[@id="meta"]'

    @property
    def games_table_query(self) -> str:
        """XPath query for games table."""
        return '//table[contains(@class, "stats_table")]'

    @property
    def team1_stats_query(self) -> str:
        """XPath query for team 1 stats table."""
        return '//table[contains(@class, "stats_table")][1]'

    @property
    def team2_stats_query(self) -> str:
        """XPath query for team 2 stats table."""
        return '//table[contains(@class, "stats_table")][2]'

    @property
    def game_rows_query(self) -> str:
        """XPath query for game rows."""
        return '//table[contains(@id, "schedule")]//tbody/tr'

    @property
    def games(self) -> list[PlayoffGameRow]:
        """Extract game rows."""
        row_elements = self.html.xpath(self.game_rows_query)
        return [
            PlayoffGameRow(html=row)
            for row in row_elements
            if row.text_content().strip()
        ]


@dataclass
class PlayoffGameRow:
    """Wrapper for a single playoff game row."""

    html: HtmlElement

    @property
    def game_number_query(self) -> str:
        """XPath query for game number."""
        return 'th[@data-stat="game"]'

    @property
    def date_query(self) -> str:
        """XPath query for game date."""
        return 'td[@data-stat="date_game"]/a'

    @property
    def home_team_query(self) -> str:
        """XPath query for home team."""
        return 'td[@data-stat="home_team_name"]/a'

    @property
    def away_team_query(self) -> str:
        """XPath query for away team."""
        return 'td[@data-stat="visitor_team_name"]/a'

    @property
    def score_query(self) -> str:
        """XPath query for score."""
        return 'td[@data-stat="pts"]'

    @property
    def game_number(self) -> str | None:
        """Extract game number."""
        elements = self.html.xpath(self.game_number_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def date(self) -> str | None:
        """Extract game date."""
        elements = self.html.xpath(self.date_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def home_team(self) -> str | None:
        """Extract home team name."""
        elements = self.html.xpath(self.home_team_query)
        return elements[0].text_content().strip() if elements else None

    @property
    def away_team(self) -> str | None:
        """Extract away team name."""
        elements = self.html.xpath(self.away_team_query)
        return elements[0].text_content().strip() if elements else None
