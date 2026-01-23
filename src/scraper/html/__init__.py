"""Exposes HTML wrapper classes for scraping basketball-reference.com pages.

This module re-exports all page and row wrapper classes to provide a flat
namespace for the scraper.
"""

from .base_rows import (
    BasicBoxScoreRow,
    PlayerBoxScoreRow,
    PlayerGameBoxScoreRow,
    PlayerIdentificationRow,
)
from .box_scores import (
    BoxScoresPage,
    StatisticsTable,
)
from .contracts import (
    PlayerContractsRow,
)
from .daily import (
    DailyBoxScoresPage,
    DailyLeadersPage,
)
from .game_log import (
    PlayerSeasonBoxScoresPage,
    PlayerSeasonBoxScoresRow,
    PlayerSeasonBoxScoresTable,
    PlayerSeasonGameLogRow,
)
from .play_by_play import (
    PlayByPlayPage,
    PlayByPlayRow,
    PlayByPlayTable,
)
from .player import (
    PlayerPage,
    PlayerPageTotalsRow,
    PlayerPageTotalsTable,
)
from .schedule import (
    SchedulePage,
    ScheduleRow,
)
from .search import (
    PlayerSearchResult,
    SearchPage,
    SearchResult,
)
from .season_totals import (
    PlayerAdvancedSeasonTotalsRow,
    PlayerAdvancedSeasonTotalsTable,
    PlayerSeasonTotalsRow,
    PlayerSeasonTotalTable,
)
from .standings import (
    ConferenceDivisionStandingsRow,
    ConferenceDivisionStandingsTable,
    DivisionStandings,
    StandingsPage,
)

__all__ = [
    # Base rows
    "BasicBoxScoreRow",
    # Box scores
    "BoxScoresPage",
    "ConferenceDivisionStandingsRow",
    "ConferenceDivisionStandingsTable",
    "DailyBoxScoresPage",
    # Daily
    "DailyLeadersPage",
    "DivisionStandings",
    # Play by play
    "PlayByPlayPage",
    "PlayByPlayRow",
    "PlayByPlayTable",
    "PlayerAdvancedSeasonTotalsRow",
    "PlayerAdvancedSeasonTotalsTable",
    "PlayerBoxScoreRow",
    # Contracts
    "PlayerContractsRow",
    "PlayerGameBoxScoreRow",
    "PlayerIdentificationRow",
    # Player
    "PlayerPage",
    "PlayerPageTotalsRow",
    "PlayerPageTotalsTable",
    "PlayerSearchResult",
    # Game log
    "PlayerSeasonBoxScoresPage",
    "PlayerSeasonBoxScoresRow",
    "PlayerSeasonBoxScoresTable",
    "PlayerSeasonGameLogRow",
    # Season totals
    "PlayerSeasonTotalTable",
    "PlayerSeasonTotalsRow",
    # Schedule
    "SchedulePage",
    "ScheduleRow",
    # Search
    "SearchPage",
    "SearchResult",
    # Standings
    "StandingsPage",
    "StatisticsTable",
]
