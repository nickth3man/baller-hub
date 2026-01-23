from unittest import TestCase, mock

from requests import HTTPError, codes

from src.core.domain import Team
from src.scraper.api.client import play_by_play
from src.scraper.common.errors import InvalidDateError
from src.scraper.services.http import HTTPService


class TestPlayByPlay(TestCase):
    @mock.patch.object(HTTPService, "play_by_play")
    def test_raises_invalid_date_for_404_response(self, mocked_play_by_play):
        mocked_play_by_play.side_effect = HTTPError(
            response=mock.Mock(status_code=codes.not_found)
        )
        self.assertRaises(  # noqa: PT027
            InvalidDateError,
            play_by_play,
            home_team=Team.MILWAUKEE_BUCKS,
            day=1,
            month=1,
            year=2018,
        )

    @mock.patch.object(HTTPService, "play_by_play")
    def test_raises_non_404_http_error(self, mocked_play_by_play):
        mocked_play_by_play.side_effect = HTTPError(
            response=mock.Mock(status_code=codes.server_error)
        )
        self.assertRaises(  # noqa: PT027
            HTTPError,
            play_by_play,
            home_team=Team.MILWAUKEE_BUCKS,
            day=1,
            month=1,
            year=2018,
        )
