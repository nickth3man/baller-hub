from unittest import TestCase, mock

from requests import codes

from src.scraper.common.errors import InvalidDateError
from src.scraper.services.http import HTTPService


class TestHTTPService(TestCase):
    def test_player_box_scores_raises_invalid_date_for_300_response(self):
        service = HTTPService(parser=mock.MagicMock())
        response = mock.Mock(status_code=codes.multiple_choices)

        with mock.patch.object(service, "_fetch", return_value=response):
            self.assertRaisesRegex(
                InvalidDateError,
                "Date with year set to 2018, month set to 1, and day set to 1 is invalid",
                service.player_box_scores,
                day=1,
                month=1,
                year=2018,
            )
