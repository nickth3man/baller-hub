"""
Parsers module for basketball-reference-scraper.

This module re-exports all parser classes from submodules to maintain
backward compatibility with existing imports from src.scraper.parsers.
"""

# Base parsers and constants
from src.scraper.parsers.base import (
    PLAYER_SEASON_BOX_SCORES_GAME_DATE_FORMAT,
    PLAYER_SEASON_BOX_SCORES_OUTCOME_REGEX,
    SEARCH_RESULT_NAME_REGEX,
    LeagueAbbreviationParser,
    LocationAbbreviationParser,
    OutcomeAbbreviationParser,
    PositionAbbreviationParser,
    TeamAbbreviationParser,
)

# Box score parsers
from src.scraper.parsers.box_scores import (
    PlayerBoxScoreOutcomeParser,
    PlayerBoxScoresParser,
    PlayerSeasonBoxScoresParser,
)

# Play-by-play parsers
from src.scraper.parsers.play_by_play import (
    PeriodDetailsParser,
    PeriodTimestampParser,
    PlayByPlaysParser,
    ScoresParser,
    SecondsPlayedParser,
)

# Player parsers
from src.scraper.parsers.player import (
    PlayerAdvancedSeasonTotalsParser,
    PlayerSeasonTotalsParser,
)

# Schedule parsers
from src.scraper.parsers.schedule import (
    ScheduledGamesParser,
    ScheduledStartTimeParser,
    TeamNameParser,
)

# Search parsers
from src.scraper.parsers.search import (
    PlayerDataParser,
    ResourceLocationParser,
    SearchResultNameParser,
    SearchResultsParser,
)

# Standings parsers
from src.scraper.parsers.standings import (
    ConferenceDivisionStandingsParser,
    DivisionNameParser,
    TeamStandingsParser,
)

# Team parsers
from src.scraper.parsers.team import (
    TeamTotalsParser,
)

__all__ = [
    # Constants
    "PLAYER_SEASON_BOX_SCORES_GAME_DATE_FORMAT",
    "PLAYER_SEASON_BOX_SCORES_OUTCOME_REGEX",
    "SEARCH_RESULT_NAME_REGEX",
    # Base parsers
    "LeagueAbbreviationParser",
    "LocationAbbreviationParser",
    "OutcomeAbbreviationParser",
    "PositionAbbreviationParser",
    "TeamAbbreviationParser",
    # Box score parsers
    "PlayerBoxScoreOutcomeParser",
    "PlayerBoxScoresParser",
    "PlayerSeasonBoxScoresParser",
    # Play-by-play parsers
    "PeriodDetailsParser",
    "PeriodTimestampParser",
    "PlayByPlaysParser",
    "ScoresParser",
    "SecondsPlayedParser",
    # Player parsers
    "PlayerAdvancedSeasonTotalsParser",
    "PlayerSeasonTotalsParser",
    # Schedule parsers
    "ScheduledGamesParser",
    "ScheduledStartTimeParser",
    "TeamNameParser",
    # Search parsers
    "PlayerDataParser",
    "ResourceLocationParser",
    "SearchResultNameParser",
    "SearchResultsParser",
    # Standings parsers
    "ConferenceDivisionStandingsParser",
    "DivisionNameParser",
    "TeamStandingsParser",
    # Team parsers
    "TeamTotalsParser",
]
