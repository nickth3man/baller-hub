"""
Custom exceptions for the Basketball Reference Scraper.

This module defines domain-specific errors that occur during the scraping process.
These exceptions help distinguish between network errors (handled by requests),
parsing errors, and logical errors like invalid dates or player IDs.

When a 404 Not Found response is received from basketball-reference.com,
these exceptions provide a more meaningful error message to the user than
a generic HTTPError.
"""


class InvalidDate(Exception):
    """
    Raised when a requested date (day, month, year) is invalid or has no data.

    This typically happens when:
    1. The date does not exist (e.g., February 30th).
    2. No games were played on that date.
    3. The URL constructed for that date returns a 404.

    Args:
        day (int): The day of the month.
        month (int): The month number (1-12).
        year (int): The year.
    """

    def __init__(self, day, month, year):
        message = f"Date with year set to {year}, month set to {month}, and day set to {day} is invalid"
        super().__init__(message)


class InvalidSeason(Exception):
    """
    Raised when a requested season year is invalid.

    Basketball Reference URLs often use the year the season ENDS.
    For example, the 2023-24 season is accessed via '2024'.

    Common causes:
    1. Requesting a future season that hasn't started.
    2. Requesting a year before data is available (e.g., pre-1946).

    Args:
        season_end_year (int): The year the season ends.
    """

    def __init__(self, season_end_year):
        message = f"Season end year of {season_end_year} is invalid"
        super().__init__(message)


class InvalidPlayerAndSeason(Exception):
    """
    Raised when a specific player cannot be found in a specific season.

    This is thrown when querying player logs (regular season or playoffs)
    if the player did not play in that season or if the player ID is incorrect.

    Args:
        player_identifier (str): The unique player ID.
        season_end_year (int): The year the season ends.
    """

    def __init__(self, player_identifier, season_end_year):
        message = f'Player with identifier "{player_identifier}" in season ending in {season_end_year} is invalid'
        super().__init__(message)
