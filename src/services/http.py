"""Service for making HTTP requests."""

import re
from datetime import timedelta

import requests
from lxml import html
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.common.data import PlayerData, TeamTotal
from src.common.errors import InvalidDate, InvalidPlayerAndSeason
from src.html import (
    BoxScoresPage,
    DailyBoxScoresPage,
    DailyLeadersPage,
    PlayByPlayPage,
    PlayerAdvancedSeasonTotalsTable,
    PlayerPage,
    PlayerSeasonBoxScoresPage,
    PlayerSeasonTotalTable,
    SchedulePage,
    SearchPage,
    StandingsPage,
)
from src.services.cache import FileCache
from src.services.rate_limiter import RateLimiter
from src.services.url_builder import URLBuilder


class HTTPService:
    """
    Orchestrates the scraping pipeline.

    Responsibilities:
    1. Construct URLs for basketball-reference.com via URLBuilder.
    2. Fetch raw HTML using `requests`.
    3. Parse HTML bytes into `lxml` ElementTrees.
    4. Initialize specific `html.*` Page objects.
    5. Delegate data extraction to the `parser_service`.
    """

    def __init__(self, parser, rate_limiter=None, cache=None):
        """
        Initialize the HTTP service.

        Args:
            parser (ParserService): Service for parsing HTML responses.
            rate_limiter (RateLimiter, optional): Rate limiting strategy.
            cache (FileCache, optional): Caching strategy.
        """
        self.parser = parser
        self.rate_limiter = rate_limiter or RateLimiter()
        self.cache = cache or FileCache()
        self._session = self._create_session()

    def _create_session(self):
        """
        Creates a requests Session with retry logic.
        """
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,  # 1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],
            respect_retry_after_header=True,
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _get_ttl(self, url):
        """
        Determine appropriate TTL for a URL.

        - Historical box scores: Immutable -> Long TTL (30 days)
        - Historical season data: Rarely changes -> Long TTL (7 days)
        - Current season/daily data: Changes often -> Short TTL (1 day or less)
        """
        # Historical Box Scores (e.g. /boxscores/pbp/2023...)
        if re.search(r"/boxscores/(?:pbp/)?\d{8}", url):
            return timedelta(days=30)

        # Historical Season Data (past years)
        # Assuming current year is dynamic, past years are static
        # This is a heuristic; technically past seasons can be corrected
        if re.search(r"NBA_\d{4}", url):
            # If year is less than current year (simplified check)
            # In a real app we'd check against current date
            return timedelta(days=7)

        return timedelta(days=1)

    def _fetch(self, url, params=None, allow_redirects=True):
        """
        Centralized method for handling all HTTP requests.

        Acts as the single injection point for:
        - Rate limiting
        - Caching
        - Retry logic
        - Session management

        Args:
            url (str): The URL to fetch.
            params (dict, optional): Query parameters.
            allow_redirects (bool, optional): Whether to follow redirects. Defaults to True.

        Returns:
            requests.Response: The HTTP response object.
        """
        # Check cache first
        # Note: We only cache GET requests without params for simplicity in this V1
        # For params support, we'd need to canonicalize them in the key
        if not params:
            cached_content = self.cache.get(url)
            if cached_content:
                # Create a mock response object from cached content
                # This is a bit of a hack to keep the signature consistent
                # Ideally we'd return content directly, but downstream expects response properties sometimes
                resp = requests.Response()
                resp._content = cached_content
                resp.status_code = 200
                resp.url = url
                return resp

        # Apply rate limiting
        self.rate_limiter.wait()

        response = self._session.get(
            url=url, params=params, allow_redirects=allow_redirects
        )

        # Update rate limiter if Retry-After header is present
        self.rate_limiter.update_from_response(response)

        response.raise_for_status()

        # Cache successful responses
        if not params and response.status_code == 200:
            ttl = self._get_ttl(url)
            self.cache.set(url, response.content, ttl=ttl)

        return response

    def standings(self, season_end_year):
        """
        Fetches division standings for a given season.
        """
        url = URLBuilder.standings(season_end_year)

        response = self._fetch(url=url, allow_redirects=False)

        # We parse response.content (bytes) rather than response.text to let lxml handle encoding
        page = StandingsPage(html=html.fromstring(response.content))
        division_standings = page.division_standings

        if division_standings is None:
            raise ValueError("Parsing error: Unable to locate division standings")

        eastern_conference_table = division_standings.eastern_conference_table
        western_conference_table = division_standings.western_conference_table

        if eastern_conference_table is None or western_conference_table is None:
            raise ValueError("Parsing error: Unable to locate conference tables")

        return self.parser.parse_division_standings(
            standings=eastern_conference_table.rows
        ) + self.parser.parse_division_standings(
            standings=western_conference_table.rows
        )

    def player_box_scores(self, day, month, year):
        """
        Fetches daily leader stats for all players on a specific date.
        """
        url = URLBuilder.player_box_scores(day=day, month=month, year=year)

        response = self._fetch(url=url, allow_redirects=False)

        if response.status_code == requests.codes.ok:  # ty: ignore[unresolved-attribute]
            page = DailyLeadersPage(html=html.fromstring(response.content))
            return self.parser.parse_player_box_scores(box_scores=page.daily_leaders)

        raise InvalidDate(day=day, month=month, year=year)

    def regular_season_player_box_scores(
        self, player_identifier, season_end_year, include_inactive_games=False
    ):
        """
        Fetches the regular season game log for a specific player.
        """
        url = URLBuilder.player_season_box_scores(
            player_identifier=player_identifier, season_end_year=season_end_year
        )

        response = self._fetch(url=url, allow_redirects=False)

        page = PlayerSeasonBoxScoresPage(html=html.fromstring(response.content))
        if page.regular_season_box_scores_table is None:
            raise InvalidPlayerAndSeason(
                player_identifier=player_identifier, season_end_year=season_end_year
            )

        return self.parser.parse_player_season_box_scores(
            box_scores=page.regular_season_box_scores_table.rows,
            include_inactive_games=include_inactive_games,
        )

    def playoff_player_box_scores(
        self, player_identifier, season_end_year, include_inactive_games=False
    ):
        """
        Fetches the playoff game log for a specific player.
        """
        url = URLBuilder.player_season_box_scores(
            player_identifier=player_identifier, season_end_year=season_end_year
        )

        response = self._fetch(url=url, allow_redirects=False)

        page = PlayerSeasonBoxScoresPage(html=html.fromstring(response.content))
        if page.playoff_box_scores_table is None:
            raise InvalidPlayerAndSeason(
                player_identifier=player_identifier, season_end_year=season_end_year
            )

        return self.parser.parse_player_season_box_scores(
            box_scores=page.playoff_box_scores_table.rows,
            include_inactive_games=include_inactive_games,
        )

    def play_by_play(self, home_team, day, month, year):
        """
        Fetches the play-by-play data for a specific game.
        """
        url = URLBuilder.play_by_play(
            home_team=home_team, day=day, month=month, year=year
        )
        response = self._fetch(url=url)

        page = PlayByPlayPage(html=html.fromstring(response.content))

        return self.parser.parse_play_by_plays(
            play_by_plays=page.play_by_play_table.rows,
            away_team_name=page.away_team_name,
            home_team_name=page.home_team_name,
        )

    def players_advanced_season_totals(
        self, season_end_year, include_combined_values=False
    ):
        """
        Fetches advanced player statistics (e.g., PER, WS, BPM) for a season.
        """
        url = URLBuilder.players_advanced_season_totals(season_end_year=season_end_year)

        response = self._fetch(url=url)

        table = PlayerAdvancedSeasonTotalsTable(html=html.fromstring(response.content))
        return self.parser.parse_player_advanced_season_totals_parser(
            totals=table.get_rows(include_combined_values)
        )

    def players_season_totals(self, season_end_year):
        """
        Fetches per-game player statistics for a season.
        """
        url = URLBuilder.players_season_totals(season_end_year=season_end_year)

        response = self._fetch(url=url)

        table = PlayerSeasonTotalTable(html=html.fromstring(response.content))
        return self.parser.parse_player_season_totals(totals=table.rows)

    def schedule_for_month(self, url):
        """
        Fetches the schedule for a specific month.
        Helper method used by season_schedule.
        """
        response = self._fetch(url=url)

        page = SchedulePage(html=html.fromstring(html=response.content))
        return self.parser.parse_scheduled_games(games=page.rows)

    def season_schedule(self, season_end_year):
        """
        Fetches the full season schedule.
        """
        url = URLBuilder.season_schedule(season_end_year=season_end_year)

        response = self._fetch(url=url)

        page = SchedulePage(html=html.fromstring(html=response.content))
        season_schedule_values = self.parser.parse_scheduled_games(games=page.rows)

        for month_url_path in page.other_months_schedule_urls:
            url = f"{URLBuilder.BASE_URL}{month_url_path}"
            monthly_schedule = self.schedule_for_month(url=url)
            season_schedule_values.extend(monthly_schedule)

        return season_schedule_values

    def team_box_score(self, game_url_path):
        """
        Fetches detailed stats for a single game.
        """
        url = URLBuilder.team_box_score(game_url_path=game_url_path)

        response = self._fetch(url=url)

        page = BoxScoresPage(html.fromstring(response.content))
        combined_team_totals = [
            TeamTotal(
                team_abbreviation=table.team_abbreviation, totals=table.team_totals
            )
            for table in page.basic_statistics_tables
        ]

        return self.parser.parse_team_totals(
            first_team_totals=combined_team_totals[0],
            second_team_totals=combined_team_totals[1],
        )

    def team_box_scores(self, day, month, year):
        """
        Fetches stats for ALL games on a specific day.
        """
        url = URLBuilder.team_box_scores_daily(day=day, month=month, year=year)

        response = self._fetch(url=url)

        page = DailyBoxScoresPage(html=html.fromstring(response.content))

        return [
            box_score
            for game_url_path in page.game_url_paths
            for box_score in self.team_box_score(game_url_path=game_url_path)
        ]

    def search(self, term):
        """
        Performs a search for players or teams.
        """
        url = URLBuilder.search(term=term)
        response = self._fetch(url=url, params={"search": term})

        player_results = []

        if response.url.startswith(f"{URLBuilder.BASE_URL}/search/search.fcgi"):
            page = SearchPage(html=html.fromstring(response.content))
            parsed_results = self.parser.parse_player_search_results(
                nba_aba_baa_players=page.nba_aba_baa_players
            )
            player_results += parsed_results["players"]

            while page.nba_aba_baa_players_pagination_url is not None:
                response = self._fetch(
                    url=f"{URLBuilder.BASE_URL}/search/{page.nba_aba_baa_players_pagination_url}"
                )

                page = SearchPage(html=html.fromstring(response.content))

                parsed_results = self.parser.parse_player_search_results(
                    nba_aba_baa_players=page.nba_aba_baa_players
                )
                player_results += parsed_results["players"]

        elif response.url.startswith(f"{URLBuilder.BASE_URL}/players"):
            page = PlayerPage(html=html.fromstring(response.content))

            name = page.name
            totals_table = page.totals_table

            if name is None:
                raise ValueError("Parsing error: Unable to locate player name")

            if totals_table is None:
                raise ValueError("Parsing error: Unable to locate totals table")

            data = PlayerData(
                name=name,
                resource_location=response.url,
                league_abbreviations={
                    row.league_abbreviation
                    for row in totals_table.rows
                    if row.league_abbreviation is not None
                },
            )
            player_results += [self.parser.parse_player_data(player=data)]

        return {"players": player_results}
