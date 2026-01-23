from unittest import TestCase

from src.scraper.utils.casting import str_to_float, str_to_int
from src.scraper.utils.dictionaries import merge_two_dicts


class TestStrToInt(TestCase):
    def test_empty_string_is_zero(self):
        assert str_to_int("") == 0

    def test_whitespace_is_zero(self):
        assert str_to_int("    ") == 0

    def test_stringified_number_is_converted(self):
        assert str_to_int("10") == 10

    def test_stringified_number_with_leading_whitespace_is_converted(self):
        assert str_to_int("  10") == 10

    def test_stringified_number_with_trailing_whitespace_is_converted(self):
        assert str_to_int("10    ") == 10

    def test_with_default(self):
        assert str_to_int("", default=None) is None


class TestStrToFloat(TestCase):
    def test_empty_string_is_zero(self):
        assert str_to_float("") == 0.0

    def test_whitespace_is_zero(self):
        assert str_to_float("    ") == 0.0

    def test_stringified_number_is_converted(self):
        assert str_to_float("1.234") == 1.234

    def test_stringified_number_with_leading_whitespace_is_converted(self):
        assert str_to_float("  1.234") == 1.234

    def test_stringified_number_with_trailing_whitespace_is_converted(self):
        assert str_to_float("1.234    ") == 1.234

    def test_with_default(self):
        assert str_to_float("", default=None) is None


class TestMergeTwoDicts(TestCase):
    def test_merges_two_empty_dicts(self):
        assert merge_two_dicts({}, {}) == {}

    def test_merges_empty_dict_with_non_empty_dict(self):
        assert merge_two_dicts({}, {"jae": "baebae"}) == {"jae": "baebae"}

    def test_merges_non_empty_dict_with_empty_dict(self):
        assert merge_two_dicts({"jae": "baebae"}, {}) == {"jae": "baebae"}

    def test_merge_non_empty_dicts_with_unique_keys(self):
        assert merge_two_dicts({"jae": "baebae"}, {"bae": "jadley"}) == {"jae": "baebae", "bae": "jadley"}

    def test_merge_non_empty_dicts_with_shared_keys(self):
        assert merge_two_dicts({"jae": "baebae"}, {"jae": "baebae2"}) == {"jae": "baebae2"}
