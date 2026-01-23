from app.services.search_service import SearchService


def test_format_years_active():
    service = SearchService(conn=None)  # type: ignore[arg-type]

    assert service._format_years_active(2003, None, True) == "2003-Present"
    assert service._format_years_active(2003, 2020, False) == "2003-2020"
    assert service._format_years_active(None, None, False) is None


def test_normalize_game_hit():
    service = SearchService(conn=None)  # type: ignore[arg-type]
    hit = {
        "game_id": 42,
        "game_date": "2024-01-01",
        "away_score": 100,
        "home_score": 110,
        "matchup": "BOS @ LAL",
    }

    normalized = service._normalize_game_hit(hit)

    assert normalized["game_id"] == 42  # noqa: PLR2004
    assert normalized["game_date"] == "2024-01-01"
    assert normalized["matchup"] == "BOS @ LAL"
    assert normalized["score"] == "100-110"
