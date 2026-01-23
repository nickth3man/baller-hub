import filecmp
import json
import os
from unittest import TestCase

import requests_mock

from src.core.domain import OutputType, Position, Team
from src.scraper.api import client


class BaseCSVOutputTest(TestCase):
    @property
    def year(self):
        raise NotImplementedError

    def setUp(self):
        with open(  # noqa: PTH123
            os.path.join(  # noqa: PTH118
                os.path.dirname(__file__),  # noqa: PTH120
                f"../files/players_season_totals/{self.year}.html",
            ),
            encoding="utf-8",
        ) as file_input:
            self._html = file_input.read()

        self.output_file_path = os.path.join(  # noqa: PTH118
            os.path.dirname(__file__),  # noqa: PTH120
            f"./output/generated/players_season_totals/{self.year}.csv",
        )
        self.expected_output_file_path = os.path.join(  # noqa: PTH118
            os.path.dirname(__file__),  # noqa: PTH120
            f"./output/expected/players_season_totals/{self.year}.csv",
        )

    def tearDown(self):
        os.remove(self.output_file_path)  # noqa: PTH107

    @requests_mock.Mocker()
    def assert_csv(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )

        client.players_season_totals(
            season_end_year=self.year,
            output_type=OutputType.CSV,
            output_file_path=self.output_file_path,
        )

        assert filecmp.cmp(self.output_file_path, self.expected_output_file_path)


class BaseJSONOutputTest(TestCase):
    @property
    def year(self):
        raise NotImplementedError

    def setUp(self):
        with open(  # noqa: PTH123
            os.path.join(  # noqa: PTH118
                os.path.dirname(__file__),  # noqa: PTH120
                f"../files/players_season_totals/{self.year}.html",
            ),
            encoding="utf-8",
        ) as file_input:
            self._html = file_input.read()

        self.output_file_path = os.path.join(  # noqa: PTH118
            os.path.dirname(__file__),  # noqa: PTH120
            f"./output/generated/players_season_totals/{self.year}.json",
        )
        self.expected_output_file_path = os.path.join(  # noqa: PTH118
            os.path.dirname(__file__),  # noqa: PTH120
            f"./output/expected/players_season_totals/{self.year}.json",
        )

    def tearDown(self):
        os.remove(self.output_file_path)  # noqa: PTH107

    @requests_mock.Mocker()
    def assert_json(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )

        client.players_season_totals(
            season_end_year=self.year,
            output_type=OutputType.JSON,
            output_file_path=self.output_file_path,
        )

        assert filecmp.cmp(self.output_file_path, self.expected_output_file_path)


class BaseInMemoryJSONOutputTest(TestCase):
    @property
    def year(self):
        raise NotImplementedError

    def setUp(self):
        with open(  # noqa: PTH123
            os.path.join(  # noqa: PTH118
                os.path.dirname(__file__),  # noqa: PTH120
                f"../files/players_season_totals/{self.year}.html",
            ),
            encoding="utf-8",
        ) as file_input:
            self._html = file_input.read()

        self.expected_output_file_path = os.path.join(  # noqa: PTH118
            os.path.dirname(__file__),  # noqa: PTH120
            f"./output/expected/players_season_totals/{self.year}.json",
        )

    @requests_mock.Mocker()
    def assert_json(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )

        results = client.players_season_totals(
            season_end_year=self.year,
            output_type=OutputType.JSON,
        )

        with open(  # noqa: PTH123
            self.expected_output_file_path, encoding="utf-8"
        ) as expected_output_file:
            assert json.loads(results) == json.load(expected_output_file)


class Test2001PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2001

    def test_2001_csv_output(self):
        self.assert_csv()


class Test2002PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2002

    def test_2002_csv_output(self):
        self.assert_csv()


class Test2003PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2003

    def test_2003_csv_output(self):
        self.assert_csv()


class Test2004PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2004

    def test_2004_csv_output(self):
        self.assert_csv()


class Test2005PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2005

    def test_2005_csv_output(self):
        self.assert_csv()


class Test2006PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2006

    def test_2006_csv_output(self):
        self.assert_csv()


class Test2007PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2007

    def test_2007_csv_output(self):
        self.assert_csv()


class Test2008PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2008

    def test_2008_csv_output(self):
        self.assert_csv()


class Test2009PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2009

    def test_2009_csv_output(self):
        self.assert_csv()


class Test2010PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2010

    def test_2010_csv_output(self):
        self.assert_csv()


class Test2011PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2011

    def test_2011_csv_output(self):
        self.assert_csv()


class Test2012PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2012

    def test_2012_csv_output(self):
        self.assert_csv()


class Test2013PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2013

    def test_2013_csv_output(self):
        self.assert_csv()


class Test2014PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2014

    def test_2014_csv_output(self):
        self.assert_csv()


class Test2015PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2015

    def test_2015_csv_output(self):
        self.assert_csv()


class Test2016PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2016

    def test_2016_csv_output(self):
        self.assert_csv()


class Test2017PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2017

    def test_2017_csv_output(self):
        self.assert_csv()


class Test2018PlayerSeasonCSVTotals(BaseCSVOutputTest):
    @property
    def year(self):
        return 2018

    def test_2018_csv_output(self):
        self.assert_csv()


class Test2001PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2001

    def test_2001_json_output(self):
        self.assert_json()


class Test2002PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2002

    def test_2002_json_output(self):
        self.assert_json()


class Test2003PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2003

    def test_2003_json_output(self):
        self.assert_json()


class Test2004PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2004

    def test_2004_json_output(self):
        self.assert_json()


class Test2005PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2005

    def test_2005_json_output(self):
        self.assert_json()


class Test2006PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2006

    def test_2006_json_output(self):
        self.assert_json()


class Test2007PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2007

    def test_2007_json_output(self):
        self.assert_json()


class Test2008PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2008

    def test_2008_json_output(self):
        self.assert_json()


class Test2009PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2009

    def test_2009_json_output(self):
        self.assert_json()


class Test2010PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2010

    def test_2010_json_output(self):
        self.assert_json()


class Test2011PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2011

    def test_2011_json_output(self):
        self.assert_json()


class Test2012PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2012

    def test_2012_json_output(self):
        self.assert_json()


class Test2013PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2013

    def test_2013_json_output(self):
        self.assert_json()


class Test2014PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2014

    def test_2014_json_output(self):
        self.assert_json()


class Test2015PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2015

    def test_2015_json_output(self):
        self.assert_json()


class Test2016PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2016

    def test_2016_json_output(self):
        self.assert_json()


class Test2017PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2017

    def test_2017_json_output(self):
        self.assert_json()


class Test2018PlayerSeasonJSONTotals(BaseJSONOutputTest):
    @property
    def year(self):
        return 2018

    def test_2018_json_output(self):
        self.assert_json()


class Test2001PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2001

    def test_2001_json_output(self):
        self.assert_json()


class Test2002PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2002

    def test_2002_json_output(self):
        self.assert_json()


class Test2003PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2003

    def test_2003_json_output(self):
        self.assert_json()


class Test2004PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2004

    def test_2004_json_output(self):
        self.assert_json()


class Test2005PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2005

    def test_2005_json_output(self):
        self.assert_json()


class Test2006PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2006

    def test_2006_json_output(self):
        self.assert_json()


class Test2007PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2007

    def test_2007_json_output(self):
        self.assert_json()


class Test2008PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2008

    def test_2008_json_output(self):
        self.assert_json()


class Test2009PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2009

    def test_2009_json_output(self):
        self.assert_json()


class Test2010PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2010

    def test_2010_json_output(self):
        self.assert_json()


class Test2011PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2011

    def test_2011_json_output(self):
        self.assert_json()


class Test2012PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2012

    def test_2012_json_output(self):
        self.assert_json()


class Test2013PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2013

    def test_2013_json_output(self):
        self.assert_json()


class Test2014PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2014

    def test_2014_json_output(self):
        self.assert_json()


class Test2015PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2015

    def test_2015_json_output(self):
        self.assert_json()


class Test2016PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2016

    def test_2016_json_output(self):
        self.assert_json()


class Test2017PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2017

    def test_2017_json_output(self):
        self.assert_json()


class Test2018PlayerSeasonInMemoryJSONTotals(BaseInMemoryJSONOutputTest):
    @property
    def year(self):
        return 2018

    def test_2018_json_output(self):
        self.assert_json()


class BaseInMemoryTest(TestCase):
    @property
    def year(self):
        msg = "Implement year to fetch players season totals for"
        raise NotImplementedError(msg)

    def setUp(self):
        with open(  # noqa: PTH123
            os.path.join(  # noqa: PTH118
                os.path.dirname(__file__),  # noqa: PTH120
                f"../files/players_season_totals/{self.year}.html",
            ),
            encoding="utf-8",
        ) as file_input:
            self._html = file_input.read()


@requests_mock.Mocker()
class Test2001InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2001

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 490  # noqa: PLR2004

    def test_first_record(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert next(
            filter(lambda totals: totals["slug"] == "abdulma02", players_season_totals)
        ) == {
            "slug": "abdulma02",
            "name": "Mahmoud Abdul-Rauf",
            "positions": [Position.POINT_GUARD],
            "age": 31,
            "team": Team.VANCOUVER_GRIZZLIES,
            "games_played": 41,
            "games_started": 0,
            "minutes_played": 486,
            "made_field_goals": 120,
            "attempted_field_goals": 246,
            "made_three_point_field_goals": 4,
            "attempted_three_point_field_goals": 14,
            "made_free_throws": 22,
            "attempted_free_throws": 29,
            "offensive_rebounds": 5,
            "defensive_rebounds": 20,
            "assists": 76,
            "steals": 9,
            "blocks": 1,
            "turnovers": 26,
            "personal_fouls": 50,
            "points": 266,
        }


@requests_mock.Mocker()
class Test2002InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2002

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 470  # noqa: PLR2004


@requests_mock.Mocker()
class Test2003InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2003

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 456  # noqa: PLR2004


@requests_mock.Mocker()
class Test2004InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2004

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 517  # noqa: PLR2004


@requests_mock.Mocker()
class Test2005InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2005

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 526  # noqa: PLR2004


@requests_mock.Mocker()
class Test2006InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2006

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 512  # noqa: PLR2004


@requests_mock.Mocker()
class Test2007InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2007

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 487  # noqa: PLR2004


@requests_mock.Mocker()
class Test2008InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2008

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 527  # noqa: PLR2004


@requests_mock.Mocker()
class Test2009InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2009

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 515  # noqa: PLR2004


@requests_mock.Mocker()
class Test2010InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2010

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 512  # noqa: PLR2004


@requests_mock.Mocker()
class Test2011InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2011

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 542  # noqa: PLR2004


@requests_mock.Mocker()
class Test2012InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2012

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 515  # noqa: PLR2004


@requests_mock.Mocker()
class Test2013InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2013

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 523  # noqa: PLR2004


@requests_mock.Mocker()
class Test2014InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2014

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 548  # noqa: PLR2004


@requests_mock.Mocker()
class Test2015InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2015

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 575  # noqa: PLR2004


@requests_mock.Mocker()
class Test2016InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2016

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 528  # noqa: PLR2004


@requests_mock.Mocker()
class Test2017InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2017

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 542  # noqa: PLR2004


@requests_mock.Mocker()
class Test2018InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2018

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 605  # noqa: PLR2004


@requests_mock.Mocker()
class Test2019InMemoryTotals(BaseInMemoryTest):
    @property
    def year(self):
        return 2019

    def test_length(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert len(players_season_totals) == 622  # noqa: PLR2004

    def test_last_is_not_league_average_row(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        assert players_season_totals[-1]["name"] != "League Average"

    def test_avery_bradley(self, m):
        m.get(
            f"https://www.basketball-reference.com/leagues/NBA_{self.year}_totals.html",
            text=self._html,
            status_code=200,
        )
        players_season_totals = client.players_season_totals(season_end_year=self.year)
        clippers_avery_bradley = players_season_totals[198]

        assert clippers_avery_bradley["slug"] == "bradlav01"
        assert clippers_avery_bradley["name"] == "Avery Bradley"
        self.assertListEqual(  # noqa: PT009
            [Position.SHOOTING_GUARD], clippers_avery_bradley["positions"]
        )
        assert clippers_avery_bradley["age"] == 28  # noqa: PLR2004
        assert clippers_avery_bradley["team"] == Team.LOS_ANGELES_CLIPPERS
        assert clippers_avery_bradley["games_played"] == 49  # noqa: PLR2004
        assert clippers_avery_bradley["games_started"] == 49  # noqa: PLR2004
        assert clippers_avery_bradley["minutes_played"] == 1463  # noqa: PLR2004
        assert clippers_avery_bradley["made_field_goals"] == 161  # noqa: PLR2004
        assert clippers_avery_bradley["attempted_field_goals"] == 420  # noqa: PLR2004
        assert clippers_avery_bradley["made_three_point_field_goals"] == 58  # noqa: PLR2004
        assert clippers_avery_bradley["attempted_three_point_field_goals"] == 172  # noqa: PLR2004
        assert clippers_avery_bradley["made_free_throws"] == 20  # noqa: PLR2004
        assert clippers_avery_bradley["attempted_free_throws"] == 25  # noqa: PLR2004
        assert clippers_avery_bradley["offensive_rebounds"] == 35  # noqa: PLR2004
        assert clippers_avery_bradley["defensive_rebounds"] == 96  # noqa: PLR2004
        assert clippers_avery_bradley["assists"] == 96  # noqa: PLR2004
        assert clippers_avery_bradley["steals"] == 27  # noqa: PLR2004
        assert clippers_avery_bradley["blocks"] == 16  # noqa: PLR2004
        assert clippers_avery_bradley["turnovers"] == 61  # noqa: PLR2004
        assert clippers_avery_bradley["personal_fouls"] == 133  # noqa: PLR2004
        assert clippers_avery_bradley["points"] == 400  # noqa: PLR2004
