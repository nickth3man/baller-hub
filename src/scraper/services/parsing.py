"""Service for coordinating parsing operations."""

from src.scraper.common.data import (
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

    def __init__(self):
        # Parsers are initialized lazily
        self._team_abbreviation_parser = None
        self._league_abbreviation_parser = None
        self._location_abbreviation_parser = None
        self._outcome_abbreviation_parser = None
        self._outcome_parser = None
        self._period_details_parser = None
        self._period_timestamp_parser = None
        self._position_abbreviation_parser = None
        self._seconds_played_parser = None
        self._scores_parser = None
        self._search_result_name_parser = None
        self._search_result_location_parser = None
        self._team_name_parser = None
        self._play_by_plays_parser = None
        self._player_box_scores_parser = None
        self._player_data_parser = None
        self._player_season_box_scores_parser = None
        self._player_season_totals_parser = None
        self._player_advanced_season_totals_parser = None
        self._scheduled_start_time_parser = None
        self._scheduled_games_parser = None
        self._search_results_parser = None
        self._team_totals_parser = None
        self._division_name_parser = None
        self._team_standings_parser = None
        self._conference_division_standings_parser = None

    @property
    def team_abbreviation_parser(self):
        if self._team_abbreviation_parser is None:
            self._team_abbreviation_parser = TeamAbbreviationParser(
                abbreviations_to_teams=TEAM_ABBREVIATIONS_TO_TEAM
            )
        return self._team_abbreviation_parser

    @property
    def league_abbreviation_parser(self):
        if self._league_abbreviation_parser is None:
            self._league_abbreviation_parser = LeagueAbbreviationParser(
                abbreviations_to_league=LEAGUE_ABBREVIATIONS_TO_LEAGUE
            )
        return self._league_abbreviation_parser

    @property
    def location_abbreviation_parser(self):
        if self._location_abbreviation_parser is None:
            self._location_abbreviation_parser = LocationAbbreviationParser(
                abbreviations_to_locations=LOCATION_ABBREVIATIONS_TO_POSITION,
            )
        return self._location_abbreviation_parser

    @property
    def outcome_abbreviation_parser(self):
        if self._outcome_abbreviation_parser is None:
            self._outcome_abbreviation_parser = OutcomeAbbreviationParser(
                abbreviations_to_outcomes=OUTCOME_ABBREVIATIONS_TO_OUTCOME,
            )
        return self._outcome_abbreviation_parser

    @property
    def outcome_parser(self):
        if self._outcome_parser is None:
            self._outcome_parser = PlayerBoxScoreOutcomeParser(
                outcome_abbreviation_parser=self.outcome_abbreviation_parser
            )
        return self._outcome_parser

    @property
    def period_details_parser(self):
        if self._period_details_parser is None:
            self._period_details_parser = PeriodDetailsParser(
                regulation_periods_count=4
            )
        return self._period_details_parser

    @property
    def period_timestamp_parser(self):
        if self._period_timestamp_parser is None:
            self._period_timestamp_parser = PeriodTimestampParser(
                timestamp_format=ParserService.PLAY_BY_PLAY_TIMESTAMP_FORMAT
            )
        return self._period_timestamp_parser

    @property
    def position_abbreviation_parser(self):
        if self._position_abbreviation_parser is None:
            self._position_abbreviation_parser = PositionAbbreviationParser(
                abbreviations_to_positions=POSITION_ABBREVIATIONS_TO_POSITION,
            )
        return self._position_abbreviation_parser

    @property
    def seconds_played_parser(self):
        if self._seconds_played_parser is None:
            self._seconds_played_parser = SecondsPlayedParser()
        return self._seconds_played_parser

    @property
    def scores_parser(self):
        if self._scores_parser is None:
            self._scores_parser = ScoresParser(
                scores_regex=ParserService.PLAY_BY_PLAY_SCORES_REGEX
            )
        return self._scores_parser

    @property
    def search_result_name_parser(self):
        if self._search_result_name_parser is None:
            self._search_result_name_parser = SearchResultNameParser()
        return self._search_result_name_parser

    @property
    def search_result_location_parser(self):
        if self._search_result_location_parser is None:
            self._search_result_location_parser = ResourceLocationParser(
                resource_location_regex=ParserService.SEARCH_RESULT_RESOURCE_LOCATION_REGEX
            )
        return self._search_result_location_parser

    @property
    def team_name_parser(self):
        if self._team_name_parser is None:
            self._team_name_parser = TeamNameParser(
                team_names_to_teams=TEAM_NAME_TO_TEAM
            )
        return self._team_name_parser

    @property
    def play_by_plays_parser(self):
        if self._play_by_plays_parser is None:
            self._play_by_plays_parser = PlayByPlaysParser(
                period_details_parser=self.period_details_parser,
                period_timestamp_parser=self.period_timestamp_parser,
                scores_parser=self.scores_parser,
            )
        return self._play_by_plays_parser

    @property
    def player_box_scores_parser(self):
        if self._player_box_scores_parser is None:
            self._player_box_scores_parser = PlayerBoxScoresParser(
                team_abbreviation_parser=self.team_abbreviation_parser,
                location_abbreviation_parser=self.location_abbreviation_parser,
                outcome_abbreviation_parser=self.outcome_abbreviation_parser,
                seconds_played_parser=self.seconds_played_parser,
            )
        return self._player_box_scores_parser

    @property
    def player_data_parser(self):
        if self._player_data_parser is None:
            self._player_data_parser = PlayerDataParser(
                search_result_location_parser=self.search_result_location_parser,
                league_abbreviation_parser=self.league_abbreviation_parser,
            )
        return self._player_data_parser

    @property
    def player_season_box_scores_parser(self):
        if self._player_season_box_scores_parser is None:
            self._player_season_box_scores_parser = PlayerSeasonBoxScoresParser(
                team_abbreviation_parser=self.team_abbreviation_parser,
                location_abbreviation_parser=self.location_abbreviation_parser,
                outcome_parser=self.outcome_parser,
                seconds_played_parser=self.seconds_played_parser,
            )
        return self._player_season_box_scores_parser

    @property
    def player_season_totals_parser(self):
        if self._player_season_totals_parser is None:
            self._player_season_totals_parser = PlayerSeasonTotalsParser(
                position_abbreviation_parser=self.position_abbreviation_parser,
                team_abbreviation_parser=self.team_abbreviation_parser,
            )
        return self._player_season_totals_parser

    @property
    def player_advanced_season_totals_parser(self):
        if self._player_advanced_season_totals_parser is None:
            self._player_advanced_season_totals_parser = (
                PlayerAdvancedSeasonTotalsParser(
                    team_abbreviation_parser=self.team_abbreviation_parser,
                    position_abbreviation_parser=self.position_abbreviation_parser,
                )
            )
        return self._player_advanced_season_totals_parser

    @property
    def scheduled_start_time_parser(self):
        if self._scheduled_start_time_parser is None:
            self._scheduled_start_time_parser = ScheduledStartTimeParser()
        return self._scheduled_start_time_parser

    @property
    def scheduled_games_parser(self):
        if self._scheduled_games_parser is None:
            self._scheduled_games_parser = ScheduledGamesParser(
                start_time_parser=self.scheduled_start_time_parser,
                team_name_parser=self.team_name_parser,
            )
        return self._scheduled_games_parser

    @property
    def search_results_parser(self):
        if self._search_results_parser is None:
            self._search_results_parser = SearchResultsParser(
                search_result_name_parser=self.search_result_name_parser,
                search_result_location_parser=self.search_result_location_parser,
                league_abbreviation_parser=self.league_abbreviation_parser,
            )
        return self._search_results_parser

    @property
    def team_totals_parser(self):
        if self._team_totals_parser is None:
            self._team_totals_parser = TeamTotalsParser(
                team_abbreviation_parser=self.team_abbreviation_parser
            )
        return self._team_totals_parser

    @property
    def division_name_parser(self):
        if self._division_name_parser is None:
            self._division_name_parser = DivisionNameParser(divisions=Division)
        return self._division_name_parser

    @property
    def team_standings_parser(self):
        if self._team_standings_parser is None:
            self._team_standings_parser = TeamStandingsParser(teams=Team)
        return self._team_standings_parser

    @property
    def conference_division_standings_parser(self):
        if self._conference_division_standings_parser is None:
            self._conference_division_standings_parser = (
                ConferenceDivisionStandingsParser(
                    division_name_parser=self.division_name_parser,
                    team_standings_parser=self.team_standings_parser,
                    divisions_to_conferences=DIVISIONS_TO_CONFERENCES,
                )
            )
        return self._conference_division_standings_parser

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
