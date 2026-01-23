from unittest import TestCase

from src.core.domain import PlayerData


class TestPlayerData(TestCase):
    def test_instantiation(self):
        data = PlayerData(
            name="some name",
            resource_location="some location",
            league_abbreviations=["NBA", "ABA", "NBA", "ABA"],
        )
        assert data.name == "some name"
        assert data.resource_location == "some location"
        assert data.league_abbreviations == {"NBA", "ABA"}
