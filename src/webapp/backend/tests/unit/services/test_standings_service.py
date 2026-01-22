from app.services.standings_service import StandingsService


def test_apply_rank_and_games_back():
    service = StandingsService(session=None)  # type: ignore[arg-type]
    teams = [
        {"name": "Alpha", "wins": 10, "losses": 5},
        {"name": "Beta", "wins": 8, "losses": 7},
        {"name": "Gamma", "wins": 7, "losses": 8},
    ]

    ranked = service._apply_rank_and_games_back(teams)

    assert ranked[0]["conference_rank"] == 1
    assert ranked[0]["games_back"] == 0.0
    assert ranked[1]["conference_rank"] == 2
    assert ranked[1]["games_back"] == 2.0
    assert ranked[2]["conference_rank"] == 3
