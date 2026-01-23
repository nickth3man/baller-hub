from unittest import TestCase

from src.core.domain import Location, Outcome, Position, Team
from src.scraper.output.fields import format_value


class TestRowFormatter(TestCase):
    def test_team_enum_value(self):
        assert format_value(Team.BOSTON_CELTICS) == "BOSTON CELTICS"

    def test_location_enum_value(self):
        assert format_value(Location.HOME) == "HOME"

    def test_outcome_enum_value(self):
        assert format_value(Outcome.LOSS) == "LOSS"

    def test_empty_array(self):
        assert format_value([]) == ""

    def test_empty_set(self):
        assert format_value(set()) == ""

    def test_position_enum_value(self):
        assert format_value(Position.POINT_GUARD) == "POINT GUARD"

    def test_positions_array_with_single_position(self):
        assert format_value([Position.POINT_GUARD]) == "POINT GUARD"

    def test_positions_array_with_multiple_positions(self):
        assert format_value([Position.POINT_GUARD, Position.SHOOTING_GUARD]) == "POINT GUARD-SHOOTING GUARD"

    def test_positions_set_with_single_position(self):
        assert format_value({Position.POINT_GUARD}) == "POINT GUARD"

    def test_string_value(self):
        assert format_value("jaebaebae") == "jaebaebae"
