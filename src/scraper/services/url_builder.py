"""
Service for constructing basketball-reference.com URLs.

Centralizes URL generation logic to ensure consistency and easy maintenance.
Uses constants from `src.core.domain` to map team enums to URL abbreviations.
"""

from src.core.domain import TEAM_TO_TEAM_ABBREVIATION


class URLBuilder:
    """
    Static utility class for building URLs.
    """

    BASE_URL = "https://www.basketball-reference.com"

    @staticmethod
    def standings(season_end_year):
        """Build URL for season standings."""
        return f"{URLBuilder.BASE_URL}/leagues/NBA_{season_end_year}.html"

    @staticmethod
    def player_box_scores(day, month, year):
        """Build URL for daily player box scores (Daily Leaders)."""
        return f"{URLBuilder.BASE_URL}/friv/dailyleaders.cgi?month={month}&day={day}&year={year}"

    @staticmethod
    def player_season_box_scores(player_identifier, season_end_year):
        """Build URL for a player's season game log."""
        return f"{URLBuilder.BASE_URL}/players/{player_identifier[0]}/{player_identifier}/gamelog/{season_end_year}"

    @staticmethod
    def play_by_play(home_team, day, month, year):
        """Build URL for a game's play-by-play data."""

        def add_0_if_needed(s):
            return "0" + s if len(s) == 1 else s

        return f"{URLBuilder.BASE_URL}/boxscores/pbp/{year}{add_0_if_needed(str(month))}{add_0_if_needed(str(day))}0{TEAM_TO_TEAM_ABBREVIATION[home_team]}.html"

    @staticmethod
    def players_advanced_season_totals(season_end_year):
        """Build URL for advanced player season totals."""
        return f"{URLBuilder.BASE_URL}/leagues/NBA_{season_end_year}_advanced.html"

    @staticmethod
    def players_season_totals(season_end_year):
        """Build URL for player season totals (per game)."""
        return f"{URLBuilder.BASE_URL}/leagues/NBA_{season_end_year}_totals.html"

    @staticmethod
    def season_schedule(season_end_year):
        """Build URL for season schedule."""
        return f"{URLBuilder.BASE_URL}/leagues/NBA_{season_end_year}_games.html"

    @staticmethod
    def team_box_score(game_url_path):
        """Build URL for a specific game box score."""
        return f"{URLBuilder.BASE_URL}/{game_url_path.lstrip('/')}"

    @staticmethod
    def team_box_scores_daily(day, month, year):
        """Build URL for daily team box scores listing."""
        return f"{URLBuilder.BASE_URL}/boxscores/?month={month}&day={day}&year={year}"

    @staticmethod
    def search(_term):
        """Build URL for search endpoint."""
        return f"{URLBuilder.BASE_URL}/search/search.fcgi"
