import filecmp
import functools
import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

import requests_mock

from src.core.domain import (
    Conference,
    Division,
    OutputType,
    OutputWriteOption,
    Team,
)
from src.scraper.api.client import standings

BASE_DIR = Path(__file__).parent
SCHEDULE_FILES_DIR = BASE_DIR / "../files/schedule"
STANDINGS_FILES_DIR = BASE_DIR / "../files/standings"


class StandingsMocker:
    def __init__(self, schedules_directory: str | Path, season_end_year: int):
        self._schedules_directory = Path(schedules_directory)
        self._season_end_year = season_end_year

    def decorate_class(self, klass):
        for attr_name in dir(klass):
            if not attr_name.startswith("test_"):
                continue

            attr = getattr(klass, attr_name)
            if not callable(attr):
                continue

            setattr(klass, attr_name, self.mock(attr))

        return klass

    def mock(self, callable):  # noqa: A002
        @functools.wraps(callable)
        def inner(*args, **kwargs):
            html_files_directory = self._schedules_directory / str(self._season_end_year)
            standings_fixture_path = STANDINGS_FILES_DIR / f"{self._season_end_year}.html"

            # Create a single mock context for all files
            with (
                patch("src.scraper.services.cache.FileCache.get", return_value=None),
                patch("src.scraper.services.cache.FileCache.set", return_value=None),
                requests_mock.Mocker() as m,
            ):
                if standings_fixture_path.exists():
                    key = f"https://www.basketball-reference.com/leagues/NBA_{self._season_end_year}.html"
                    m.get(key, text=standings_fixture_path.read_text(encoding="utf-8"), status_code=200)
                for file_path in html_files_directory.iterdir():
                    if file_path.suffix != ".html":
                        continue
                    filename = file_path.name

                    file_content = file_path.read_text(encoding="utf-8")
                    # Mock the standings URL (NBA_YEAR.html, not NBA_YEAR_games.html)
                    if filename.startswith(str(self._season_end_year)):
                        if standings_fixture_path.exists():
                            continue
                        key = f"https://www.basketball-reference.com/leagues/NBA_{self._season_end_year}.html"
                        m.get(key, text=file_content, status_code=200)
                    else:
                        # Mock schedule URLs for monthly files
                        key = f"https://www.basketball-reference.com/leagues/NBA_{self._season_end_year}_games-{filename}"
                        m.get(key, text=file_content, status_code=200)

                # Execute the test within the mock context
                return callable(*args, **kwargs)

        return inner

    def __call__(self, obj):
        if isinstance(obj, type):
            return self.decorate_class(obj)

        msg = "Should only be used as a class decorator"
        raise ValueError(msg)


@StandingsMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2000,
)
class Test2000StandingsInMemory(TestCase):
    def test_2000_standings(self):
        result = standings(season_end_year=2000)
        assert len(result) == 29  # noqa: PLR2004

        miami_heat = result[0]
        assert miami_heat["team"] == Team.MIAMI_HEAT
        assert miami_heat["wins"] == 52  # noqa: PLR2004
        assert miami_heat["losses"] == 30  # noqa: PLR2004
        assert miami_heat["division"] == Division.ATLANTIC
        assert miami_heat["conference"] == Conference.EASTERN

        los_angeles_clippers = result[28]
        assert los_angeles_clippers["team"] == Team.LOS_ANGELES_CLIPPERS
        assert los_angeles_clippers["wins"] == 15  # noqa: PLR2004
        assert los_angeles_clippers["losses"] == 67  # noqa: PLR2004
        assert los_angeles_clippers["division"] == Division.PACIFIC
        assert los_angeles_clippers["conference"] == Conference.WESTERN


@StandingsMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2001,
)
class Test2001StandingsInMemory(TestCase):
    def test_2001_standings(self):
        result = standings(season_end_year=2001)
        assert len(result) == 29  # noqa: PLR2004

        philadelphia_76ers = result[0]
        assert philadelphia_76ers["team"] == Team.PHILADELPHIA_76ERS
        assert philadelphia_76ers["wins"] == 56  # noqa: PLR2004
        assert philadelphia_76ers["losses"] == 26  # noqa: PLR2004
        assert philadelphia_76ers["division"] == Division.ATLANTIC
        assert philadelphia_76ers["conference"] == Conference.EASTERN

        golden_state_warriors = result[28]
        assert golden_state_warriors["team"] == Team.GOLDEN_STATE_WARRIORS
        assert golden_state_warriors["wins"] == 17  # noqa: PLR2004
        assert golden_state_warriors["losses"] == 65  # noqa: PLR2004
        assert golden_state_warriors["division"] == Division.PACIFIC
        assert golden_state_warriors["conference"] == Conference.WESTERN


@StandingsMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2002,
)
class Test2002StandingsInMemory(TestCase):
    def test_2002_standings(self):
        result = standings(season_end_year=2002)
        assert len(result) == 29  # noqa: PLR2004

        nets = result[0]
        assert nets["team"] == Team.NEW_JERSEY_NETS
        assert nets["wins"] == 52  # noqa: PLR2004
        assert nets["losses"] == 30  # noqa: PLR2004
        assert nets["division"] == Division.ATLANTIC
        assert nets["conference"] == Conference.EASTERN

        golden_state_warriors = result[28]
        assert golden_state_warriors["team"] == Team.GOLDEN_STATE_WARRIORS
        assert golden_state_warriors["wins"] == 21  # noqa: PLR2004
        assert golden_state_warriors["losses"] == 61  # noqa: PLR2004
        assert golden_state_warriors["division"] == Division.PACIFIC
        assert golden_state_warriors["conference"] == Conference.WESTERN


@StandingsMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2005,
)
class Test2005StandingsInMemory(TestCase):
    def test_2005_standings(self):
        result = standings(season_end_year=2005)
        assert len(result) == 30  # noqa: PLR2004

        phoenix_suns = result[0]
        assert phoenix_suns["team"] == Team.BOSTON_CELTICS
        assert phoenix_suns["wins"] == 45  # noqa: PLR2004
        assert phoenix_suns["losses"] == 37  # noqa: PLR2004
        assert phoenix_suns["division"] == Division.ATLANTIC
        assert phoenix_suns["conference"] == Conference.EASTERN

        detroit_pistons = result[5]
        assert detroit_pistons["team"] == Team.DETROIT_PISTONS
        assert detroit_pistons["wins"] == 54  # noqa: PLR2004
        assert detroit_pistons["losses"] == 28  # noqa: PLR2004
        assert detroit_pistons["division"] == Division.CENTRAL
        assert detroit_pistons["conference"] == Conference.EASTERN

        miami_heat = result[10]
        assert miami_heat["team"] == Team.MIAMI_HEAT
        assert miami_heat["wins"] == 59  # noqa: PLR2004
        assert miami_heat["losses"] == 23  # noqa: PLR2004
        assert miami_heat["division"] == Division.SOUTHEAST
        assert miami_heat["conference"] == Conference.EASTERN

        seattle_supersonics = result[15]
        assert seattle_supersonics["team"] == Team.SEATTLE_SUPERSONICS
        assert seattle_supersonics["wins"] == 52  # noqa: PLR2004
        assert seattle_supersonics["losses"] == 30  # noqa: PLR2004
        assert seattle_supersonics["division"] == Division.NORTHWEST
        assert seattle_supersonics["conference"] == Conference.WESTERN

        phoenix_suns = result[20]
        assert phoenix_suns["team"] == Team.PHOENIX_SUNS
        assert phoenix_suns["wins"] == 62  # noqa: PLR2004
        assert phoenix_suns["losses"] == 20  # noqa: PLR2004
        assert phoenix_suns["division"] == Division.PACIFIC
        assert phoenix_suns["conference"] == Conference.WESTERN

        new_orleans_hornets = result[29]
        assert new_orleans_hornets["team"] == Team.NEW_ORLEANS_HORNETS
        assert new_orleans_hornets["wins"] == 18  # noqa: PLR2004
        assert new_orleans_hornets["losses"] == 64  # noqa: PLR2004
        assert new_orleans_hornets["division"] == Division.SOUTHWEST
        assert new_orleans_hornets["conference"] == Conference.WESTERN


@StandingsMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2020,
)
class Test2020StandingsInMemory(TestCase):
    def test_2020_standings(self):
        result = standings(season_end_year=2020)
        assert len(result) == 30  # noqa: PLR2004

        toronto_raptors = result[0]
        assert toronto_raptors["team"] == Team.TORONTO_RAPTORS
        assert toronto_raptors["wins"] == 53  # noqa: PLR2004
        assert toronto_raptors["losses"] == 19  # noqa: PLR2004
        assert toronto_raptors["division"] == Division.ATLANTIC
        assert toronto_raptors["conference"] == Conference.EASTERN

        milwaukee_bucks = result[5]
        assert milwaukee_bucks["team"] == Team.MILWAUKEE_BUCKS
        assert milwaukee_bucks["wins"] == 56  # noqa: PLR2004
        assert milwaukee_bucks["losses"] == 17  # noqa: PLR2004
        assert milwaukee_bucks["division"] == Division.CENTRAL
        assert milwaukee_bucks["conference"] == Conference.EASTERN

        orlando_magic = result[11]
        assert orlando_magic["team"] == Team.ORLANDO_MAGIC
        assert orlando_magic["wins"] == 33  # noqa: PLR2004
        assert orlando_magic["losses"] == 40  # noqa: PLR2004
        assert orlando_magic["division"] == Division.SOUTHEAST
        assert orlando_magic["conference"] == Conference.EASTERN

        denver_nuggets = result[15]
        assert denver_nuggets["team"] == Team.DENVER_NUGGETS
        assert denver_nuggets["wins"] == 46  # noqa: PLR2004
        assert denver_nuggets["losses"] == 27  # noqa: PLR2004
        assert denver_nuggets["division"] == Division.NORTHWEST
        assert denver_nuggets["conference"] == Conference.WESTERN

        golden_state_warriors = result[24]
        assert golden_state_warriors["team"] == Team.GOLDEN_STATE_WARRIORS
        assert golden_state_warriors["wins"] == 15  # noqa: PLR2004
        assert golden_state_warriors["losses"] == 50  # noqa: PLR2004
        assert golden_state_warriors["division"] == Division.PACIFIC
        assert golden_state_warriors["conference"] == Conference.WESTERN

        dallas_mavericks = result[26]
        assert dallas_mavericks["team"] == Team.DALLAS_MAVERICKS
        assert dallas_mavericks["wins"] == 43  # noqa: PLR2004
        assert dallas_mavericks["losses"] == 32  # noqa: PLR2004
        assert dallas_mavericks["division"] == Division.SOUTHWEST
        assert dallas_mavericks["conference"] == Conference.WESTERN


@StandingsMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2001,
)
class TestCSVStandingsFor2001(TestCase):
    def setUp(self):
        self.output_file_path = BASE_DIR / "./output/generated/standings/2001.csv"
        self.expected_output_file_path = BASE_DIR / "./output/expected/standings/2001.csv"

    def tearDown(self):
        self.output_file_path.unlink()

    def test_2001_standings(self):
        standings(
            season_end_year=2001,
            output_type=OutputType.CSV,
            output_file_path=str(self.output_file_path),
            output_write_option=OutputWriteOption.WRITE,
        )
        assert filecmp.cmp(self.output_file_path, self.expected_output_file_path)


@StandingsMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2001,
)
class TestJSONPlayerBoxScores2001(TestCase):
    def setUp(self):
        self.output_file_path = BASE_DIR / "./output/generated/standings/2001.json"
        self.expected_output_file_path = BASE_DIR / "./output/expected/standings/2001.json"

    def tearDown(self):
        self.output_file_path.unlink()

    def test_2001_standings(self):
        standings(
            season_end_year=2001,
            output_type=OutputType.JSON,
            output_file_path=str(self.output_file_path),
            output_write_option=OutputWriteOption.WRITE,
        )

        assert filecmp.cmp(self.output_file_path, self.expected_output_file_path)


@StandingsMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2001,
)
class TestInMemoryJSONStandings2001(TestCase):
    def setUp(self):
        self.expected_output_file_path = BASE_DIR / "./output/expected/standings/2001.json"

    def test_2001_standings(self):
        box_scores = standings(
            season_end_year=2001,
            output_type=OutputType.JSON,
        )

        expected = json.loads(self.expected_output_file_path.read_text(encoding="utf-8"))
        assert json.loads(box_scores) == expected


@StandingsMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2019,
)
class TestCSVStandingsFor2019(TestCase):
    def setUp(self):
        self.output_file_path = BASE_DIR / "./output/generated/standings/2019.csv"
        self.expected_output_file_path = BASE_DIR / "./output/expected/standings/2019.csv"

    def tearDown(self):
        self.output_file_path.unlink()

    def test_2019_standings(self):
        standings(
            season_end_year=2019,
            output_type=OutputType.CSV,
            output_file_path=str(self.output_file_path),
            output_write_option=OutputWriteOption.WRITE,
        )
        assert filecmp.cmp(self.output_file_path, self.expected_output_file_path)


@StandingsMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2019,
)
class TestJSONPlayerBoxScores2019(TestCase):
    def setUp(self):
        self.output_file_path = BASE_DIR / "./output/generated/standings/2019.json"
        self.expected_output_file_path = BASE_DIR / "./output/expected/standings/2019.json"

    def tearDown(self):
        self.output_file_path.unlink()

    def test_2019_standings(self):
        standings(
            season_end_year=2019,
            output_type=OutputType.JSON,
            output_file_path=str(self.output_file_path),
            output_write_option=OutputWriteOption.WRITE,
        )

        assert filecmp.cmp(self.output_file_path, self.expected_output_file_path)


@StandingsMocker(
    schedules_directory=SCHEDULE_FILES_DIR,
    season_end_year=2019,
)
class TestInMemoryJSONStandings2019(TestCase):
    def setUp(self):
        self.expected_output_file_path = BASE_DIR / "./output/expected/standings/2019.json"

    def test_2019_standings(self):
        box_scores = standings(
            season_end_year=2019,
            output_type=OutputType.JSON,
        )

        expected = json.loads(self.expected_output_file_path.read_text(encoding="utf-8"))
        assert json.loads(box_scores) == expected
