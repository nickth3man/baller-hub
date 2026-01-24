import filecmp
import json
from pathlib import Path
from unittest import TestCase

import requests_mock

from src.core.domain import OutputType, OutputWriteOption
from src.scraper.api import client

ARCHIVE_SEARCH_DIR = Path(__file__).parent / ".." / ".." / ".." / ".archive" / "oldfiles" / "search"


@requests_mock.Mocker()
class TestJa(TestCase):
    def setUp(self):
        base_dir = Path(__file__).parent / "../files/search/ja"
        self._html = (base_dir / "0.html").read_text(encoding="utf-8")
        self._1_html = (base_dir / "1.html").read_text(encoding="utf-8")
        self._2_html = (base_dir / "2.html").read_text(encoding="utf-8")
        self._3_html = (base_dir / "3.html").read_text(encoding="utf-8")
        self._4_html = (base_dir / "4.html").read_text(encoding="utf-8")
        self._5_html = (base_dir / "5.html").read_text(encoding="utf-8")
        self._6_html = (base_dir / "6.html").read_text(encoding="utf-8")
        self._7_html = (base_dir / "7.html").read_text(encoding="utf-8")
        self._8_html = (base_dir / "8.html").read_text(encoding="utf-8")

    def test_length(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja",
            text=self._html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=100",
            text=self._1_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=200",
            text=self._2_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=300",
            text=self._3_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=400",
            text=self._4_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=500",
            text=self._5_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=600",
            text=self._6_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=700",
            text=self._7_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&i=players&offset=800",
            text=self._8_html,
            status_code=200,
        )
        results = client.search(term="ja")
        assert len(results["players"]) == 863  # noqa: PLR2004
        assert {
            "name": "LeBron James",
            "identifier": "jamesle01",
            "leagues": set(),
        } == results["players"][0]


@requests_mock.Mocker()
class TestAlonzoMourning(TestCase):
    def setUp(self):
        html_path = Path(__file__).parent / "../files/search/Alonzo Mourning.html"
        self._html = html_path.read_text(encoding="utf-8")

    def test_result(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=Alonzo+Mourning",
            text=self._html,
            status_code=200,
        )
        results = client.search(term="Alonzo Mourning")
        self.assertEqual(  # noqa: PT009
            [
                {
                    "name": "Alonzo Mourning",
                    "identifier": "mournal01",
                    # Basketball-Reference moved leagues from the search results
                    "leagues": set(),
                }
            ],
            results["players"],
        )


@requests_mock.Mocker()
class TestDominiqueWilkins(TestCase):
    def setUp(self):
        html_path = Path(__file__).parent / "../files/search/Dominique Wilkins.html"
        self._html = html_path.read_text(encoding="utf-8")

    def test_result(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=Dominique+Wilkins",
            text=self._html,
            status_code=200,
        )
        results = client.search(term="Dominique Wilkins")
        assert [
            {"name": "Dominique Wilkins", "identifier": "wilkido01", "leagues": set()}
        ] == results["players"]


@requests_mock.Mocker()
class TestRickBarry(TestCase):
    def setUp(self):
        html_path = Path(__file__).parent / "../files/search/Rick Barry.html"
        self._html = html_path.read_text(encoding="utf-8")

    def test_result(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=Rick+Barry",
            text=self._html,
            status_code=200,
        )
        results = client.search(term="Rick Barry")
        assert [
            {"name": "Rick Barry", "identifier": "barryri01", "leagues": set()}
        ] == results["players"]


@requests_mock.Mocker()
class TestJaebaebae(TestCase):
    def setUp(self):
        html_path = Path(__file__).parent / "../files/search/jaebaebae.html"
        self._html = html_path.read_text(encoding="utf-8")

    def test_result(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=jaebaebae",
            text=self._html,
            status_code=200,
        )
        results = client.search(term="jaebaebae")
        assert results["players"] == []


@requests_mock.Mocker()
class TestKobeBryant(TestCase):
    def setUp(self):
        html_path = Path(__file__).parent / "../files/search/kobe bryant.html"
        self._html = html_path.read_text(encoding="utf-8")

    def test_result(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=kobe+bryant",
            text=self._html,
            status_code=200,
        )
        results = client.search(term="kobe bryant")
        assert [
            {"name": "Kobe Bryant", "identifier": "bryanko01", "leagues": set()}
        ] == results["players"]


@requests_mock.Mocker()
class TestKobe(TestCase):
    def setUp(self):
        self._html = (ARCHIVE_SEARCH_DIR / "kobe.html").read_text(encoding="utf-8")

    def test_result(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=kobe",
            text=self._html,
            status_code=200,
        )
        results = client.search(term="kobe")
        assert [
            {"name": "Kobe Bryant", "identifier": "bryanko01", "leagues": set()},
            {"name": "Ruben Patterson", "identifier": "patteru01", "leagues": set()},
            {"name": "Dion Waiters", "identifier": "waitedi01", "leagues": set()},
            {"name": "Austin Reaves", "identifier": "reaveau01", "leagues": set()},
            {"name": "Kobe Bufkin", "identifier": "bufkiko01", "leagues": set()},
            {"name": "Kobe Brown", "identifier": "brownko01", "leagues": set()},
            {"name": "Oleksandr Kobets", "identifier": "kobetol01", "leagues": set()},
        ] == results["players"]


@requests_mock.Mocker()
class TestSearchJSONFileOutput(TestCase):
    def setUp(self):
        self._html = (ARCHIVE_SEARCH_DIR / "kobe.html").read_text(encoding="utf-8")
        base_dir = Path(__file__).parent
        self.output_file_path = base_dir / "./output/generated/search/kobe.json"
        self.expected_output_file_path = base_dir / "./output/expected/search/kobe.json"

    def tearDown(self):
        self.output_file_path.unlink()

    def test_file_output(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=kobe",
            text=self._html,
            status_code=200,
        )

        client.search(
            term="kobe",
            output_type=OutputType.JSON,
            output_file_path=str(self.output_file_path),
            output_write_option=OutputWriteOption.WRITE,
        )
        assert filecmp.cmp(self.output_file_path, self.expected_output_file_path)


@requests_mock.Mocker()
class TestSearchJSONInMemoryOutput(TestCase):
    def setUp(self):
        self._html = (ARCHIVE_SEARCH_DIR / "kobe.html").read_text(encoding="utf-8")
        base_dir = Path(__file__).parent
        self.output_file_path = base_dir / "./output/generated/search/kobe.json"
        self.expected_output_file_path = base_dir / "./output/expected/search/kobe.json"

    def test_in_memory_output(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=kobe",
            text=self._html,
            status_code=200,
        )

        results = client.search(
            term="kobe",
            output_type=OutputType.JSON,
        )
        expected_output = json.loads(self.expected_output_file_path.read_text(encoding="utf-8"))
        assert json.loads(results) == expected_output


@requests_mock.Mocker()
class TestSearchCSVOutput(TestCase):
    def setUp(self):
        self._html = (ARCHIVE_SEARCH_DIR / "kobe.html").read_text(encoding="utf-8")
        base_dir = Path(__file__).parent
        self.output_file_path = base_dir / "./output/generated/search/kobe.csv"
        self.expected_output_file_path = base_dir / "./output/expected/search/kobe.csv"

    def tearDown(self):
        self.output_file_path.unlink()

    def test_file_output(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=kobe",
            text=self._html,
            status_code=200,
        )

        client.search(
            term="kobe",
            output_type=OutputType.CSV,
            output_file_path=str(self.output_file_path),
            output_write_option=OutputWriteOption.WRITE,
        )

        assert filecmp.cmp(self.output_file_path, self.expected_output_file_path)
