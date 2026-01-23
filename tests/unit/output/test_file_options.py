from unittest import TestCase

from src.scraper.output.writers import FileOptions


class TestFileOptions(TestCase):
    def test_should_write_to_file_is_false_when_type_is_none(self):
        assert not FileOptions.of().should_write_to_file

    def test_should_write_to_file_is_false_when_nothing_is_defined(self):
        assert not FileOptions.of().should_write_to_file

    def test_should_write_to_file_is_true_when_file_path_is_not_none_but_mode_is_none(
        self,
    ):
        assert FileOptions.of(path="some file path", mode=None).should_write_to_file

    def test_should_write_to_file_is_true_when_output_type_is_not_none_and_file_path_is_not_none_and_mode_is_not_none(
        self,
    ):
        assert FileOptions.of(
            path="some file path", mode="some mode"
        ).should_write_to_file

    def test_two_options_with_same_properties_are_equivalent(self):
        assert FileOptions.of() == FileOptions.of()

    def test_two_options_with_same_properties_except_file_path_are_not_equivalent(self):
        assert FileOptions.of(path="some file path") != FileOptions.of()

    def test_two_options_with_same_properties_except_mode_are_not_equivalent(self):
        assert FileOptions.of(mode="some mode") != FileOptions.of()
