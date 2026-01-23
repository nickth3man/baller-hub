"""Service for coordinating parsing operations."""

from functools import cached_property

from src.core.domain import (
    DIVISIONS_TO_CONFERENCES,
    LEAGUE_ABBREVIATIONS_TO_LEAGUE,
    LOCATION_ABBREVIATIONS_TO_POSITION,
    OUTCOME_ABBREVIATIONS_TO_OUTCOME,
    POSITION_ABBREVIATIONS_TO_POSITION,
    TEAM_ABBREVIATIONS_TO_TEAM,
    TEAM_NAME_TO_TEAM,
    Division,
    Team,
)
from src.scraper.parsers import (
    ConferenceDivisionStandingsParser,
    DivisionNameParser,
    LeagueAbbreviationParser,
    LocationAbbreviationParser,
    OutcomeAbbreviationParser,
    PeriodDetailsParser,
    PeriodTimestampParser,
    PlayByPlaysParser,
    PlayerAdvancedSeasonTotalsParser,
    PlayerBoxScoreOutcomeParser,
    PlayerBoxScoresParser,
    PlayerDataParser,
    PlayerSeasonBoxScoresParser,
    PlayerSeasonTotalsParser,
    PositionAbbreviationParser,
    ResourceLocationParser,
    ScheduledGamesParser,
    ScheduledStartTimeParser,
    ScoresParser,
    SearchResultNameParser,
    SearchResultsParser,
    SecondsPlayedParser,
    TeamAbbreviationParser,
    TeamNameParser,
    TeamStandingsParser,
    TeamTotalsParser,
)


class ParserService:
    """
    Central registry and factory for all parsers.

    This service initializes all specialized parsers with their dependencies
    (like regex patterns and enum mappings) and provides a unified interface
    for parsing different types of data.

    Why this exists:
    - Decouples parsing logic from the HTTP service.
    - Centralizes configuration (regexes, formats).
    - Manages dependencies between parsers (e.g., BoxScoreParser needs TeamAbbreviationParser).
    """

    PLAY_BY_PLAY_TIMESTAMP_FORMAT = "%M:%S.%f"
    PLAY_BY_PLAY_SCORES_REGEX = (
        "(?P<away_team_score>[0-9]+)-(?P<home_team_score>[0-9]+)"
    )
    SEARCH_RESULT_RESOURCE_LOCATION_REGEX = r"(https?:\/\/www\.basketball-reference\.com\/)?(?P<resource_type>.+?(?=\/)).*\/(?P<resource_identifier>.+).html"

    @cached_property
    def team_abbreviation_parser(self):
        return TeamAbbreviationParser(abbreviations_to_teams=TEAM_ABBREVIATIONS_TO_TEAM)

    @cached_property
    def league_abbreviation_parser(self):
        return LeagueAbbreviationParser(
            abbreviations_to_league=LEAGUE_ABBREVIATIONS_TO_LEAGUE
        )

    @cached_property
    def location_abbreviation_parser(self):
        return LocationAbbreviationParser(
            abbreviations_to_locations=LOCATION_ABBREVIATIONS_TO_POSITION,
        )

    @cached_property
    def outcome_abbreviation_parser(self):
        return OutcomeAbbreviationParser(
            abbreviations_to_outcomes=OUTCOME_ABBREVIATIONS_TO_OUTCOME,
        )

    @cached_property
    def outcome_parser(self):
        return PlayerBoxScoreOutcomeParser(
            outcome_abbreviation_parser=self.outcome_abbreviation_parser
        )

    @cached_property
    def period_details_parser(self):
        return PeriodDetailsParser(regulation_periods_count=4)

    @cached_property
    def period_timestamp_parser(self):
        return PeriodTimestampParser(
            timestamp_format=ParserService.PLAY_BY_PLAY_TIMESTAMP_FORMAT
        )

    @cached_property
    def position_abbreviation_parser(self):
        return PositionAbbreviationParser(
            abbreviations_to_positions=POSITION_ABBREVIATIONS_TO_POSITION,
        )

    @cached_property
    def seconds_played_parser(self):
        return SecondsPlayedParser()

    @cached_property
    def scores_parser(self):
        return ScoresParser(scores_regex=ParserService.PLAY_BY_PLAY_SCORES_REGEX)

    @cached_property
    def search_result_name_parser(self):
        return SearchResultNameParser()

    @cached_property
    def search_result_location_parser(self):
        return ResourceLocationParser(
            resource_location_regex=ParserService.SEARCH_RESULT_RESOURCE_LOCATION_REGEX
        )

    @cached_property
    def team_name_parser(self):
        return TeamNameParser(team_names_to_teams=TEAM_NAME_TO_TEAM)

    @cached_property
    def play_by_plays_parser(self):
        return PlayByPlaysParser(
            period_details_parser=self.period_details_parser,
            period_timestamp_parser=self.period_timestamp_parser,
            scores_parser=self.scores_parser,
        )

    @cached_property
    def player_box_scores_parser(self):
        return PlayerBoxScoresParser(
            team_abbreviation_parser=self.team_abbreviation_parser,
            location_abbreviation_parser=self.location_abbreviation_parser,
            outcome_abbreviation_parser=self.outcome_abbreviation_parser,
            seconds_played_parser=self.seconds_played_parser,
        )

    @cached_property
    def player_data_parser(self):
        return PlayerDataParser(
            search_result_location_parser=self.search_result_location_parser,
            league_abbreviation_parser=self.league_abbreviation_parser,
        )

    @cached_property
    def player_season_box_scores_parser(self):
        return PlayerSeasonBoxScoresParser(
            team_abbreviation_parser=self.team_abbreviation_parser,
            location_abbreviation_parser=self.location_abbreviation_parser,
            outcome_parser=self.outcome_parser,
            seconds_played_parser=self.seconds_played_parser,
        )

    @cached_property
    def player_season_totals_parser(self):
        return PlayerSeasonTotalsParser(
            position_abbreviation_parser=self.position_abbreviation_parser,
            team_abbreviation_parser=self.team_abbreviation_parser,
        )

    @cached_property
    def player_advanced_season_totals_parser(self):
        return PlayerAdvancedSeasonTotalsParser(
            team_abbreviation_parser=self.team_abbreviation_parser,
            position_abbreviation_parser=self.position_abbreviation_parser,
        )

    @cached_property
    def scheduled_start_time_parser(self):
        return ScheduledStartTimeParser()

    @cached_property
    def scheduled_games_parser(self):
        return ScheduledGamesParser(
            start_time_parser=self.scheduled_start_time_parser,
            team_name_parser=self.team_name_parser,
        )

    @cached_property
    def search_results_parser(self):
        return SearchResultsParser(
            search_result_name_parser=self.search_result_name_parser,
            search_result_location_parser=self.search_result_location_parser,
            league_abbreviation_parser=self.league_abbreviation_parser,
        )

    @cached_property
    def team_totals_parser(self):
        return TeamTotalsParser(team_abbreviation_parser=self.team_abbreviation_parser)

    @cached_property
    def division_name_parser(self):
        return DivisionNameParser(divisions=Division)

    @cached_property
    def team_standings_parser(self):
        return TeamStandingsParser(teams=Team)

    @cached_property
    def conference_division_standings_parser(self):
        return ConferenceDivisionStandingsParser(
            division_name_parser=self.division_name_parser,
            team_standings_parser=self.team_standings_parser,
            divisions_to_conferences=DIVISIONS_TO_CONFERENCES,
        )

    def parse_division_standings(self, standings):
        """Parse raw division standing rows into structured data."""
        return self.conference_division_standings_parser.parse(
            division_standings=standings
        )

    def parse_play_by_plays(self, play_by_plays, away_team_name, home_team_name):
        """Parse play-by-play rows, contextualized with team names."""
        return self.play_by_plays_parser.parse(
            play_by_plays=play_by_plays,
            away_team=self.team_name_parser.parse_team_name(team_name=away_team_name),
            home_team=self.team_name_parser.parse_team_name(team_name=home_team_name),
        )

    def parse_player_box_scores(self, box_scores):
        """Parse daily leader box scores."""
        return self.player_box_scores_parser.parse(box_scores=box_scores)

    def parse_player_season_box_scores(self, box_scores, include_inactive_games=False):
        """Parse a player's full season game log."""
        return self.player_season_box_scores_parser.parse(
            box_scores=box_scores, include_inactive_games=include_inactive_games
        )

    def parse_player_advanced_season_totals_parser(self, totals):
        """Parse advanced season stats (PER, WS, etc.)."""
        return self.player_advanced_season_totals_parser.parse(totals=totals)

    def parse_player_season_totals(self, totals):
        """Parse standard per-game season totals."""
        return self.player_season_totals_parser.parse(totals=totals)

    def parse_scheduled_games(self, games):
        """Parse schedule rows into Game objects."""
        return self.scheduled_games_parser.parse_games(games)

    def parse_team_totals(self, first_team_totals, second_team_totals):
        """
        Parse team-level box score totals.

        Requires both teams to determine the winner/loser outcome.
        """
        return self.team_totals_parser.parse(
            first_team_totals=first_team_totals, second_team_totals=second_team_totals
        )

    def parse_player_search_results(self, nba_aba_baa_players):
        """Parse search result rows."""
        return self.search_results_parser.parse(nba_aba_baa_players=nba_aba_baa_players)

    def parse_player_data(self, player):
        """Parse individual player metadata."""
        return self.player_data_parser.parse(player=player)
