from src.common.data import TEAM_TO_TEAM_ABBREVIATION


class URLBuilder:
    BASE_URL = "https://www.basketball-reference.com"

    @staticmethod
    def standings(season_end_year):
        return f"{URLBuilder.BASE_URL}/leagues/NBA_{season_end_year}.html"

    @staticmethod
    def player_box_scores(day, month, year):
        return f"{URLBuilder.BASE_URL}/friv/dailyleaders.cgi?month={month}&day={day}&year={year}"

    @staticmethod
    def player_season_box_scores(player_identifier, season_end_year):
        return f"{URLBuilder.BASE_URL}/players/{player_identifier[0]}/{player_identifier}/gamelog/{season_end_year}"

    @staticmethod
    def play_by_play(home_team, day, month, year):
        def add_0_if_needed(s):
            return "0" + s if len(s) == 1 else s

        return f"{URLBuilder.BASE_URL}/boxscores/pbp/{year}{add_0_if_needed(str(month))}{add_0_if_needed(str(day))}0{TEAM_TO_TEAM_ABBREVIATION[home_team]}.html"

    @staticmethod
    def players_advanced_season_totals(season_end_year):
        return f"{URLBuilder.BASE_URL}/leagues/NBA_{season_end_year}_advanced.html"

    @staticmethod
    def players_season_totals(season_end_year):
        return f"{URLBuilder.BASE_URL}/leagues/NBA_{season_end_year}_totals.html"

    @staticmethod
    def season_schedule(season_end_year):
        return f"{URLBuilder.BASE_URL}/leagues/NBA_{season_end_year}_games.html"

    @staticmethod
    def team_box_score(game_url_path):
        return f"{URLBuilder.BASE_URL}/{game_url_path.lstrip('/')}"

    @staticmethod
    def team_box_scores_daily(day, month, year):
        return f"{URLBuilder.BASE_URL}/boxscores/?month={month}&day={day}&year={year}"

    @staticmethod
    def search(term):
        return f"{URLBuilder.BASE_URL}/search/search.fcgi"
