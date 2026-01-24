import filecmp
import json
from datetime import datetime
from pathlib import Path
from unittest import TestCase

import pytz
import requests_mock

from src.core.domain import OutputType, Team
from src.scraper.api.client import season_schedule
from tests.integration.client.utilities import SeasonScheduleMocker

BASE_DIR = Path(__file__).parent
SCHEDULE_FILES_DIR = BASE_DIR / "../files/schedule"


@SeasonScheduleMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2018,
)
class TestSeasonScheduleInMemoryOutput(TestCase):
    def test_2018_season_schedule_length(self):
        result = season_schedule(season_end_year=2018)
        assert len(result) == 1416  # noqa: PLR2004

    def test_first_game_of_2018_season(self):
        result = season_schedule(season_end_year=2018)
        assert result[0] == {
            "away_team": Team.BOSTON_CELTICS,
            "away_team_score": 99,
            "home_team": Team.CLEVELAND_CAVALIERS,
            "home_team_score": 102,
            "start_time": datetime(2017, 10, 18, 0, 1, tzinfo=pytz.utc),
        }

    def test_last_game_of_2018_season(self):
        result = season_schedule(season_end_year=2018)
        assert result[1415] == {
            "away_team": Team.GOLDEN_STATE_WARRIORS,
            "away_team_score": 108,
            "home_team": Team.CLEVELAND_CAVALIERS,
            "home_team_score": 85,
            "start_time": datetime(2018, 6, 9, 1, 0, tzinfo=pytz.utc),
        }


class TestFutureSeasonSchedule(TestCase):
    def setUp(self):
        html_path = SCHEDULE_FILES_DIR / "not-found.html"
        self._html = html_path.read_text(encoding="utf-8")

    @requests_mock.Mocker()
    def test_future_season_schedule_returns_empty_list(self, m):
        m.get(
            url="https://www.basketball-reference.com/leagues/NBA_2026_games.html",
            text=self._html,
            status_code=200,
        )
        result = season_schedule(season_end_year=2026)
        assert result == []


@SeasonScheduleMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2018,
)
class Test2018SeasonScheduleCsvOutput(TestCase):
    def setUp(self):
        self.output_file_path = BASE_DIR / "./output/generated/season_schedule/2018.csv"
        self.expected_output_file_path = BASE_DIR / "./output/expected/season_schedule/2018.csv"

    def tearDown(self):
        self.output_file_path.unlink()

    def test_output(self):
        season_schedule(
            season_end_year=2018,
            output_type=OutputType.CSV,
            output_file_path=str(self.output_file_path),
        )
        assert filecmp.cmp(self.output_file_path, self.expected_output_file_path)


@SeasonScheduleMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2018,
)
class Test2018SeasonScheduleJsonOutput(TestCase):
    def setUp(self):
        self.output_file_path = BASE_DIR / "./output/generated/season_schedule/2018.json"
        self.expected_output_file_path = BASE_DIR / "./output/expected/season_schedule/2018.json"

    def tearDown(self):
        self.output_file_path.unlink()

    def test_file_output(self):
        season_schedule(
            season_end_year=2018,
            output_type=OutputType.JSON,
            output_file_path=str(self.output_file_path),
        )
        assert filecmp.cmp(self.output_file_path, self.expected_output_file_path)


@SeasonScheduleMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2018,
)
class Test2018SeasonScheduleInMemoryJson(TestCase):
    def setUp(self):
        self.expected_output_file_path = BASE_DIR / "./output/expected/season_schedule/2018.json"

    def test_in_memory_json(self):
        schedule = season_schedule(season_end_year=2018, output_type=OutputType.JSON)
        expected = json.loads(self.expected_output_file_path.read_text(encoding="utf-8"))
        assert expected == json.loads(schedule)


@SeasonScheduleMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2001,
)
class Test2001SeasonScheduleCsvOutput(TestCase):
    def setUp(self):
        self.output_file_path = BASE_DIR / "./output/generated/season_schedule/2001.csv"
        self.expected_output_file_path = BASE_DIR / "./output/expected/season_schedule/2001.csv"

    def tearDown(self):
        self.output_file_path.unlink()

    def test_output(self):
        season_schedule(
            season_end_year=2001,
            output_type=OutputType.CSV,
            output_file_path=str(self.output_file_path),
        )
        assert filecmp.cmp(self.output_file_path, self.expected_output_file_path)


@SeasonScheduleMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2001,
)
class Test2001SeasonScheduleJsonOutput(TestCase):
    def setUp(self):
        self.output_file_path = BASE_DIR / "./output/generated/season_schedule/2001.json"
        self.expected_output_file_path = BASE_DIR / "./output/expected/season_schedule/2001.json"

    def tearDown(self):
        self.output_file_path.unlink()

    def test_file_output(self):
        season_schedule(
            season_end_year=2001,
            output_type=OutputType.JSON,
            output_file_path=str(self.output_file_path),
        )
        assert filecmp.cmp(self.output_file_path, self.expected_output_file_path)


@SeasonScheduleMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2001,
)
class Test2001SeasonScheduleInMemoryJson(TestCase):
    def setUp(self):
        self.expected_output_file_path = BASE_DIR / "./output/expected/season_schedule/2001.json"

    def test_in_memory_json(self):
        schedule = season_schedule(season_end_year=2001, output_type=OutputType.JSON)
        expected = json.loads(self.expected_output_file_path.read_text(encoding="utf-8"))
        assert expected == json.loads(schedule)
