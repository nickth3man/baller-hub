"""
The public API for the basketball-reference-scraper.

This module acts as a FACADE. It provides a simple, unified interface for users
while delegating all actual work to the `HTTPService` (for fetching/parsing)
and `OutputService` (for formatting JSON/CSV).

Usage:
    >>> from src import client
    >>> client.player_box_scores(day=1, month=1, year=2020)
"""

import requests

from src.common.errors import InvalidDate, InvalidPlayerAndSeason, InvalidSeason
from src.output.columns import (
    BOX_SCORE_COLUMN_NAMES,
    PLAY_BY_PLAY_COLUMN_NAMES,
    PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES,
    PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
    PLAYER_SEASON_TOTALS_COLUMN_NAMES,
    SCHEDULE_COLUMN_NAMES,
    SEARCH_RESULTS_COLUMN_NAMES,
    STANDINGS_COLUMNS_NAMES,
    TEAM_BOX_SCORES_COLUMN_NAMES,
)
from src.output.fields import BasketballReferenceJSONEncoder, format_value
from src.output.service import OutputService
from src.output.writers import (
    CSVWriter,
    FileOptions,
    JSONWriter,
    OutputOptions,
    SearchCSVWriter,
)
from src.services.http import HTTPService
from src.services.parsing import ParserService


def _get_http_service():
    return HTTPService(parser=ParserService())


def standings(
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """
    Get team standings for a specific season.

    Retrieves division standings for both the Eastern and Western conferences.
    Useful for analyzing playoff seeding and division rankings.

    Args:
        season_end_year (int): The year the season ends (e.g., 2024 for the 2023-24 season).
        output_type (OutputType, optional): Format to export (JSON or CSV). Defaults to None (return dict).
        output_file_path (str, optional): Path to save the output file.
        output_write_option (OutputWriteOption, optional): Mode for writing ('w' or 'a').
        json_options (dict, optional): Kwargs for JSON serialization.

    Returns:
        dict: A dictionary containing standings data if no output_type is specified.
    """
    try:
        http_service = _get_http_service()
        values = http_service.standings(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:  # ty: ignore[unresolved-attribute]
            raise InvalidSeason(season_end_year=season_end_year) from None
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": STANDINGS_COLUMNS_NAMES},
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value),
    )
    return output_service.output(data=values, options=options)


def player_box_scores(
    day,
    month,
    year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """
    Get all player box scores for a specific date.

    Returns stats for every player who played in any game on the specified day.
    Equivalent to the "Daily Leaders" page.

    Args:
        day (int): Day of the month.
        month (int): Month number (1-12).
        year (int): 4-digit year.
        output_type (OutputType, optional): Format to export (JSON or CSV).
        output_file_path (str, optional): Path to save the output file.
        output_write_option (OutputWriteOption, optional): Mode for writing ('w' or 'a').
        json_options (dict, optional): Kwargs for JSON serialization.

    Returns:
        list[dict]: A list of box scores if output_type is None.
    """
    # MENTAL MODEL: Execution Flow
    # 1. User calls client.player_box_scores()
    # 2. HTTPService constructs URL: https://basketball-reference.com/friv/dailyleaders.fcgi?...
    # 3. HTTPService fetches HTML and wraps it in a Page object (html/daily.py)
    # 4. ParserService delegates to PlayerBoxScoresParser (parsers/box_scores.py)
    # 5. Parser converts raw HTML strings into Python types (int, float, Team enum)
    # 6. OutputService formats the result (JSON, CSV, or raw dict)
    try:
        http_service = _get_http_service()
        values = http_service.player_box_scores(day=day, month=month, year=year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:  # ty: ignore[unresolved-attribute]
            raise InvalidDate(day=day, month=month, year=year) from None
        else:
            raise http_error

    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": BOX_SCORE_COLUMN_NAMES},
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value),
    )
    return output_service.output(data=values, options=options)


def regular_season_player_box_scores(
    player_identifier,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
    include_inactive_games=False,
):
    """
    Get all regular season box scores for a specific player.

    Fetches the game log for a single player in a specific season.

    Args:
        player_identifier (str): The unique player ID (e.g., 'jamesle01' for LeBron James).
            This ID can be found in the URL of the player's page.
        season_end_year (int): The year the season ends (e.g., 2024 for 2023-24).
        include_inactive_games (bool): If True, includes games where the player was
            inactive/DNP. Defaults to False.

    Returns:
        list[dict]: List of game logs.
    """
    try:
        http_service = _get_http_service()
        values = http_service.regular_season_player_box_scores(
            player_identifier=player_identifier,
            season_end_year=season_end_year,
            include_inactive_games=include_inactive_games,
        )
    except requests.exceptions.HTTPError as http_error:
        if (
            http_error.response.status_code == requests.codes.internal_server_error  # ty: ignore[unresolved-attribute]
            or http_error.response.status_code == requests.codes.not_found  # ty: ignore[unresolved-attribute]
        ):
            raise InvalidPlayerAndSeason(
                player_identifier=player_identifier, season_end_year=season_end_year
            ) from None
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES},
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value),
    )
    return output_service.output(data=values, options=options)


def playoff_player_box_scores(
    player_identifier,
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
    include_inactive_games=False,
):
    """
    Get all playoff box scores for a specific player.

    Similar to regular season logs, but for the post-season.

    Args:
        player_identifier (str): The unique player ID (e.g., 'jamesle01').
        season_end_year (int): The year the season ends.
        include_inactive_games (bool): If True, includes games where the player was DNP.

    Returns:
        list[dict]: List of playoff game logs.
    """
    try:
        http_service = _get_http_service()
        values = http_service.playoff_player_box_scores(
            player_identifier=player_identifier,
            season_end_year=season_end_year,
            include_inactive_games=include_inactive_games,
        )
    except requests.exceptions.HTTPError as http_error:
        if (
            http_error.response.status_code == requests.codes.internal_server_error  # ty: ignore[unresolved-attribute]
            or http_error.response.status_code == requests.codes.not_found  # ty: ignore[unresolved-attribute]
        ):
            raise InvalidPlayerAndSeason(
                player_identifier=player_identifier, season_end_year=season_end_year
            ) from None
        else:
            raise http_error

    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES},
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value),
    )
    return output_service.output(data=values, options=options)


def season_schedule(
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """
    Get the full schedule for a season.

    Iterates through every month of the season to build a complete list of games.

    Note:
        This fetches the schedule for ALL months in the season.
        For the 2023-24 season, pass `season_end_year=2024`.

    Returns:
        list[dict]: List of games containing date, home/away teams, and scores (if played).
    """
    try:
        http_service = _get_http_service()
        values = http_service.season_schedule(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        # https://github.com/requests/requests/blob/master/requests/status_codes.py#L58
        if http_error.response.status_code == requests.codes.not_found:  # ty: ignore[unresolved-attribute]
            raise InvalidSeason(season_end_year=season_end_year) from None
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": SCHEDULE_COLUMN_NAMES},
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value),
    )
    return output_service.output(data=values, options=options)


def players_season_totals(
    season_end_year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """
    Get aggregated season totals for all players.

    This scrapes the "Per Game" table (not "Totals") from the season summary page.
    It returns averages (points per game, rebounds per game) rather than cumulative totals.

    Args:
        season_end_year (int): The year the season ends.

    Returns:
        list[dict]: List of player totals (points, rebounds, assists, etc. per game).
    """
    try:
        http_service = _get_http_service()
        values = http_service.players_season_totals(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:  # ty: ignore[unresolved-attribute]
            raise InvalidSeason(season_end_year=season_end_year) from None
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_SEASON_TOTALS_COLUMN_NAMES},
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value),
    )
    return output_service.output(data=values, options=options)


def players_advanced_season_totals(
    season_end_year,
    include_combined_values=False,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """
    Get advanced stats (PER, TS%, Win Shares) for all players.

    Includes efficiency metrics and advanced analytics not found in standard box scores.

    Args:
        season_end_year (int): The year the season ends.
        include_combined_values (bool): If True, for players who played for multiple teams,
            includes a "Total" row combining their stats. Defaults to False.

    Returns:
        list[dict]: List of advanced player stats.
    """
    try:
        http_service = _get_http_service()
        values = http_service.players_advanced_season_totals(
            season_end_year, include_combined_values=include_combined_values
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:  # ty: ignore[unresolved-attribute]
            raise InvalidSeason(season_end_year=season_end_year) from None
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES},
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value),
    )
    return output_service.output(data=values, options=options)


def team_box_scores(
    day,
    month,
    year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """
    Get team-level stats for all games on a specific date.

    Aggregates individual player stats to give team totals (FG%, Rebounds, etc.) for each game.

    Args:
        day (int): Day of the month.
        month (int): Month number (1-12).
        year (int): 4-digit year.

    Returns:
        list[dict]: List of team stats for that day's games.
    """
    try:
        http_service = _get_http_service()
        values = http_service.team_box_scores(day=day, month=month, year=year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:  # ty: ignore[unresolved-attribute]
            raise InvalidDate(day=day, month=month, year=year) from None
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_BOX_SCORES_COLUMN_NAMES},
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value),
    )
    return output_service.output(data=values, options=options)


def play_by_play(
    home_team,
    day,
    month,
    year,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """
    Get the full play-by-play log for a single game.

    Returns every event (shot, foul, sub) with timestamps and scores.

    Args:
        home_team (Team): The Team enum for the HOME team (used to identify the game).
            Import `Team` from `src.data`.
        day (int): Day of the month.
        month (int): Month number.
        year (int): Year.

    Returns:
        list[dict]: Chronological list of plays.
    """
    try:
        http_service = _get_http_service()
        values = http_service.play_by_play(
            home_team=home_team, day=day, month=month, year=year
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:  # ty: ignore[unresolved-attribute]
            raise InvalidDate(day=day, month=month, year=year) from None
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAY_BY_PLAY_COLUMN_NAMES},
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value),
    )
    return output_service.output(data=values, options=options)


def search(
    term,
    output_type=None,
    output_file_path=None,
    output_write_option=None,
    json_options=None,
):
    """
    Search for a player or team on basketball-reference.com.

    Args:
        term (str): The search query (e.g., "LeBron", "Lakers").

    Returns:
        dict: Search results containing players and teams matching the term.
    """
    http_service = _get_http_service()
    values = http_service.search(term=term)
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": SEARCH_RESULTS_COLUMN_NAMES},
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=SearchCSVWriter(value_formatter=format_value),
    )
    return output_service.output(data=values, options=options)
