from unittest import TestCase

from src.scraper.parsers import SecondsPlayedParser


class TestSecondsPlayedParser(TestCase):
    def setUp(self):
        self.parser = SecondsPlayedParser()

    def test_parse_seconds_played_for_empty_string(self):
        assert self.parser.parse("") == 0

    def test_parse_seconds_played_for_0_seconds(self):
        assert self.parser.parse("0:01") == 1

    def test_parse_seconds_played_for_59_seconds(self):
        assert self.parser.parse("0:59") == 59

    def test_parse_seconds_played_for_60_seconds(self):
        assert self.parser.parse("1:00") == 60

    def test_parse_seconds_played_for_61_seconds(self):
        assert self.parser.parse("1:01") == 61

    def test_parse_seconds_played_for_59_minutes_59_seconds(self):
        assert self.parser.parse("59:59") == 3599

    def test_parse_seconds_played_for_60_minutes(self):
        assert self.parser.parse("60:00") == 3600

    def test_parse_seconds_played_for_60_minutes_and_1_second(self):
        assert self.parser.parse("60:01") == 3601
