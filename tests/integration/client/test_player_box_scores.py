import filecmp
import json
from pathlib import Path
from unittest import TestCase

import requests_mock

from src.core.domain import OutputType, OutputWriteOption
from src.scraper.api.client import player_box_scores
from src.scraper.common.errors import InvalidDateError


class Test20180101(TestCase):
    def setUp(self):
        self._html = (
            Path(__file__).parent / "../files/player_box_scores/2018/1/1.html"
        ).read_text(encoding="utf-8")

    @requests_mock.Mocker()
    def test_player_box_scores_length(self, m):
        m.get(
            "https://www.basketball-reference.com/friv/dailyleaders.cgi?month=1&day=1&year=2018",
            text=self._html,
            status_code=200,
        )
        result = player_box_scores(day=1, month=1, year=2018)
        assert len(result) == 82  # noqa: PLR2004


class Test20010101(TestCase):
    def setUp(self):
        self._html = (
            Path(__file__).parent / "../files/player_box_scores/2001/1/1.html"
        ).read_text(encoding="utf-8")

    @requests_mock.Mocker()
    def test_2001_01_01_player_box_scores_length(self, m):
        m.get(
            "https://www.basketball-reference.com/friv/dailyleaders.cgi?month=1&day=1&year=2001",
            text=self._html,
            status_code=200,
        )
        result = player_box_scores(day=1, month=1, year=2001)
        assert len(result) == 39  # noqa: PLR2004

    @requests_mock.Mocker()
    def test_json_output(self, m):
        m.get(
            "https://www.basketball-reference.com/friv/dailyleaders.cgi?month=1&day=1&year=2001",
            text=self._html,
            status_code=200,
        )

        output_file_path = (
            Path(__file__).parent / "output/generated/player_box_scores/2001/1/1.json"
        )

        try:
            player_box_scores(
                day=1,
                month=1,
                year=2001,
                output_type=OutputType.JSON,
                output_file_path=str(output_file_path),
                output_write_option=OutputWriteOption.WRITE,
            )
            assert filecmp.cmp(
                output_file_path,
                Path(__file__).parent
                / "output/expected/player_box_scores/2001/1/1.json",
            )
        finally:
            output_file_path.unlink(missing_ok=True)

    @requests_mock.Mocker()
    def test_in_memory_json_output(self, m):
        m.get(
            "https://www.basketball-reference.com/friv/dailyleaders.cgi?month=1&day=1&year=2001",
            text=self._html,
            status_code=200,
        )

        box_scores = player_box_scores(
            day=1,
            month=1,
            year=2001,
            output_type=OutputType.JSON,
        )

        expected_path = (
            Path(__file__).parent / "output/expected/player_box_scores/2001/1/1.json"
        )
        with expected_path.open(encoding="utf-8") as expected_output_file:
            assert json.loads(box_scores) == json.load(expected_output_file)

    @requests_mock.Mocker()
    def test_csv_output(self, m):
        m.get(
            "https://www.basketball-reference.com/friv/dailyleaders.cgi?month=1&day=1&year=2001",
            text=self._html,
            status_code=200,
        )

        output_file_path = (
            Path(__file__).parent / "output/generated/player_box_scores/2001/1/1.csv"
        )
        try:
            player_box_scores(
                day=1,
                month=1,
                year=2001,
                output_type=OutputType.CSV,
                output_file_path=str(output_file_path),
                output_write_option=OutputWriteOption.WRITE,
            )
            assert filecmp.cmp(
                output_file_path,
                Path(__file__).parent
                / "output/expected/player_box_scores/2001/1/1.csv",
            )
        finally:
            output_file_path.unlink(missing_ok=True)


class TestPlayerBoxScores(TestCase):
    @requests_mock.Mocker()
    def test_get_box_scores_for_day_that_does_not_exist(self, m):
        m.get(
            "https://www.basketball-reference.com/friv/dailyleaders.cgi?month=1&day=-1&year=2018",
            text="Not found",
            status_code=404,
        )
        self.assertRaisesRegex(  # noqa: PT027
            InvalidDateError,
            "Date with year set to 2018, month set to 1, and day set to -1 is invalid",
            player_box_scores,
            day=-1,
            month=1,
            year=2018,
        )
