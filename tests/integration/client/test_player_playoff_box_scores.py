import filecmp
import json
import os
from datetime import datetime
from unittest import TestCase

import requests_mock

from src.core.domain import Outcome, OutputType, Team
from src.scraper.api.client import playoff_player_box_scores
from src.scraper.common.errors import InvalidPlayerAndSeasonError


class TestRussellWestbrook2019(TestCase):
    def setUp(self):
        with open(  # noqa: PTH123
            os.path.join(  # noqa: PTH118
                os.path.dirname(__file__),  # noqa: PTH120
                "../files/player_box_scores/2019/westbru01.html",
            ),
            encoding="utf-8",
        ) as file_input:
            self._html = file_input.read()

    @requests_mock.Mocker()
    def test_length(self, m):
        m.get(
            "https://www.basketball-reference.com/players/w/westbru01/gamelog/2019",
            text=self._html,
            status_code=200,
        )
        result = playoff_player_box_scores(
            player_identifier="westbru01", season_end_year=2019
        )
        assert len(result) == 5  # noqa: PLR2004

    @requests_mock.Mocker()
    def test_first_game(self, m):
        m.get(
            "https://www.basketball-reference.com/players/w/westbru01/gamelog/2019",
            text=self._html,
            status_code=200,
        )
        result = playoff_player_box_scores(
            player_identifier="westbru01", season_end_year=2019
        )
        first_game = result[0]
        assert first_game["active"]
        assert datetime.strptime("2019-04-14", "%Y-%m-%d").date() == first_game["date"]  # noqa: DTZ007
        assert first_game["team"] == Team.OKLAHOMA_CITY_THUNDER
        assert first_game["outcome"] == Outcome.LOSS
        assert first_game["seconds_played"] == 2263  # noqa: PLR2004
        assert first_game["opponent"] == Team.PORTLAND_TRAIL_BLAZERS
        assert first_game["made_field_goals"] == 8  # noqa: PLR2004
        assert first_game["attempted_field_goals"] == 17  # noqa: PLR2004
        assert first_game["made_three_point_field_goals"] == 0
        assert first_game["attempted_three_point_field_goals"] == 4  # noqa: PLR2004
        assert first_game["made_free_throws"] == 8  # noqa: PLR2004
        assert first_game["attempted_free_throws"] == 8  # noqa: PLR2004
        assert first_game["offensive_rebounds"] == 0
        assert first_game["defensive_rebounds"] == 10  # noqa: PLR2004
        assert first_game["assists"] == 10  # noqa: PLR2004
        assert first_game["steals"] == 0
        assert first_game["blocks"] == 0
        assert first_game["turnovers"] == 4  # noqa: PLR2004
        assert first_game["personal_fouls"] == 4  # noqa: PLR2004
        assert first_game["points_scored"] == 24  # noqa: PLR2004
        assert first_game["game_score"] == 19.7  # noqa: PLR2004
        assert first_game["plus_minus"] == -10  # noqa: PLR2004


class RussellWestbrook2020IncludingInactiveGames(TestCase):
    def setUp(self):
        with open(  # noqa: PTH123
            os.path.join(  # noqa: PTH118
                os.path.dirname(__file__),  # noqa: PTH120
                "../files/player_box_scores/2020/westbru01.html",
            ),
            encoding="utf-8",
        ) as file_input:
            self._html = file_input.read()
        self.expected_output_json_file_path = os.path.join(  # noqa: PTH118
            os.path.dirname(__file__),  # noqa: PTH120
            "./output/expected/playoff_player_box_scores/2020/westbru01/include_inactive.json",
        )
        self.expected_output_csv_file_path = os.path.join(  # noqa: PTH118
            os.path.dirname(__file__),  # noqa: PTH120
            "./output/expected/playoff_player_box_scores/2020/westbru01/include_inactive.csv",
        )

    @requests_mock.Mocker()
    def test_in_memory_json_output(self, m):
        m.get(
            "https://www.basketball-reference.com/players/w/westbru01/gamelog/2020",
            text=self._html,
            status_code=200,
        )

        results = playoff_player_box_scores(
            player_identifier="westbru01",
            season_end_year=2020,
            output_type=OutputType.JSON,
            include_inactive_games=True,
        )
        with open(  # noqa: PTH123
            self.expected_output_json_file_path, encoding="utf-8"
        ) as expected_output:
            assert json.loads(results) == json.load(expected_output)

    @requests_mock.Mocker()
    def test_json_file_output(self, m):
        m.get(
            "https://www.basketball-reference.com/players/w/westbru01/gamelog/2020",
            text=self._html,
            status_code=200,
        )

        output_file_path = os.path.join(  # noqa: PTH118
            os.path.dirname(__file__),  # noqa: PTH120
            "./output/generated/playoff_player_box_scores/2020/westbru01/include_inactive.json",
        )

        try:
            playoff_player_box_scores(
                player_identifier="westbru01",
                season_end_year=2020,
                output_type=OutputType.JSON,
                output_file_path=output_file_path,
                include_inactive_games=True,
            )
            assert filecmp.cmp(output_file_path, self.expected_output_json_file_path)
        finally:
            os.remove(output_file_path)  # noqa: PTH107

    @requests_mock.Mocker()
    def test_csv_file_output(self, m):
        m.get(
            "https://www.basketball-reference.com/players/w/westbru01/gamelog/2020",
            text=self._html,
            status_code=200,
        )

        output_file_path = os.path.join(  # noqa: PTH118
            os.path.dirname(__file__),  # noqa: PTH120
            "./output/generated/playoff_player_box_scores/2020/westbru01/include_inactive.csv",
        )

        try:
            playoff_player_box_scores(
                player_identifier="westbru01",
                season_end_year=2020,
                output_type=OutputType.CSV,
                output_file_path=output_file_path,
                include_inactive_games=True,
            )
            assert filecmp.cmp(output_file_path, self.expected_output_csv_file_path)
        finally:
            os.remove(output_file_path)  # noqa: PTH107


class TestNonExistentPlayerPlayoffBoxScores(TestCase):
    def setUp(self):
        with open(  # noqa: PTH123
            os.path.join(  # noqa: PTH118
                os.path.dirname(__file__),
                "../files/player_box_scores/2020/foobar.html",
            ),
            encoding="utf-8",
        ) as file_input:
            self._html = file_input.read()

    @requests_mock.Mocker()
    def test_get_season_box_scores_for_player_that_does_not_exist_raises_exception(
        self, m
    ):
        # bbref won't actually 404 or 500 if the player/season is invalid, it'll
        # just take you to the player page with blank data

        m.get(
            "https://www.basketball-reference.com/players/f/foobar/gamelog/2020",
            text=self._html,
            status_code=200,
        )

        self.assertRaisesRegex(  # noqa: PT027
            InvalidPlayerAndSeasonError,
            'Player with identifier "foobar" in season ending in 2020 is invalid',
            playoff_player_box_scores,
            player_identifier="foobar",
            season_end_year=2020,
        )


class Giannis2020(TestCase):
    def setUp(self):
        with open(  # noqa: PTH123
            os.path.join(  # noqa: PTH118
                os.path.dirname(__file__),  # noqa: PTH120
                "../files/player_box_scores/2020/antetgi01.html",
            ),
            encoding="utf-8",
        ) as file_input:
            self._html = file_input.read()

    @requests_mock.Mocker()
    def test_inactive_games_are_removed_by_default(self, m):
        m.get(
            "https://www.basketball-reference.com/players/a/antetgi01/gamelog/2020",
            text=self._html,
            status_code=200,
        )
        # Giannis missed one playoff game in 2020. Verify that the game from
        # 9/8/2020 is not included in his boxscores.
        results = playoff_player_box_scores(
            player_identifier="antetgi01", season_end_year=2020
        )
        assert results is not None
        assert len(results) == 9  # noqa: PLR2004

        d = datetime.strptime("2020-09-08", "%Y-%m-%d").date()  # noqa: DTZ007
        assert all(bs["date"] != d and bs["active"] for bs in results)

    @requests_mock.Mocker()
    def test_inactive_games_are_included_when_option_is_explicitly_selected(self, m):
        m.get(
            "https://www.basketball-reference.com/players/a/antetgi01/gamelog/2020",
            text=self._html,
            status_code=200,
        )
        results = playoff_player_box_scores(
            player_identifier="antetgi01",
            season_end_year=2020,
            include_inactive_games=True,
        )
        assert results is not None
        assert len(results) == 10  # noqa: PLR2004

        inactive_game = results[-1]
        assert (
            datetime.strptime("2020-09-08", "%Y-%m-%d").date() == inactive_game["date"]  # noqa: DTZ007
        )
        assert not inactive_game["active"]

        expected_null_stats = {
            "seconds_played",
            "made_field_goals",
            "attempted_field_goals",
            "made_three_point_field_goals",
            "attempted_three_point_field_goals",
            "made_free_throws",
            "attempted_free_throws",
            "offensive_rebounds",
            "defensive_rebounds",
            "assists",
            "steals",
            "blocks",
            "turnovers",
            "personal_fouls",
            "points_scored",
            "game_score",
            "plus_minus",
        }

        for stat in expected_null_stats:
            assert inactive_game[stat] is None
