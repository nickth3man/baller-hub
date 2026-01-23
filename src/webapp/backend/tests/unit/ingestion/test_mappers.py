from app.ingestion import mappers
from app.models.game import PlayType
from app.models.player import Position


def test_seconds_from_minutes_str():
    assert mappers._seconds_from_minutes_str("12:34") == 12 * 60 + 34
    assert mappers._seconds_from_minutes_str("0:59") == 59
    assert mappers._seconds_from_minutes_str("15") == 15
    assert mappers._seconds_from_minutes_str(None) == 0


def test_classify_play_type():
    assert mappers._classify_play_type("Start of 1st quarter") == PlayType.PERIOD_START
    assert mappers._classify_play_type("Timeout: Official") == PlayType.TIMEOUT
    assert (
        mappers._classify_play_type("makes 3-pt jump shot") == PlayType.FIELD_GOAL_MADE
    )


def test_map_player_box_score():
    raw = {
        "name": "Test Player",
        "slug": "testpl01",
        "position": "PG",
        "is_starter": True,
        "seconds_played": "10:30",
        "made_field_goals": 4,
        "attempted_field_goals": 9,
        "made_three_point_field_goals": 2,
        "attempted_three_point_field_goals": 5,
        "made_free_throws": 1,
        "attempted_free_throws": 2,
        "offensive_rebounds": 1,
        "defensive_rebounds": 4,
        "assists": 7,
        "steals": 2,
        "blocks": 1,
        "turnovers": 3,
        "personal_fouls": 2,
        "points_scored": 11,
        "plus_minus": 5,
        "game_score": 12.3,
    }

    mapped = mappers.map_player_box_score(
        raw=raw, player_id=1, box_id=2, game_id=3, team_id=4
    )

    assert mapped.player_id == 1
    assert mapped.box_id == 2
    assert mapped.game_id == 3
    assert mapped.team_id == 4
    assert mapped.player_slug == "testpl01"
    assert mapped.position == Position.POINT_GUARD
    assert mapped.seconds_played == 630
    assert mapped.points_scored == 11
