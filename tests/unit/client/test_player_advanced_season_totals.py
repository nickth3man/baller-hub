from unittest import TestCase
from unittest.mock import MagicMock, patch

from requests import HTTPError, codes

from src.scraper.api.client import players_advanced_season_totals
from src.scraper.common.errors import InvalidSeasonError
from src.scraper.services.http import HTTPService


class TestPlayerAdvancedSeasonTotals(TestCase):
    @patch.object(HTTPService, "players_advanced_season_totals")
    def test_not_found_raises_invalid_season(
        self, mocked_players_advanced_season_totals
    ):
        end_year = "jaebaebae"
        expected_message = f"Season end year of {end_year} is invalid"
        mocked_players_advanced_season_totals.side_effect = HTTPError(
            response=MagicMock(status_code=codes.not_found)
        )
        self.assertRaisesRegex(
            InvalidSeasonError,
            expected_message,
            players_advanced_season_totals,
            season_end_year=end_year,
        )

    @patch.object(HTTPService, "players_advanced_season_totals")
    def test_other_http_error_is_raised(self, mocked_players_advanced_season_totals):
        mocked_players_advanced_season_totals.side_effect = HTTPError(
            response=MagicMock(status_code=codes.internal_server_error)
        )
        self.assertRaises(
            HTTPError, players_advanced_season_totals, season_end_year=2018
        )
