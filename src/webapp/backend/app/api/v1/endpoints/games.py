"""Games API endpoints."""

from datetime import UTC, date, datetime

import duckdb
from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.connection import get_connection
from app.schemas.game import BoxScoreResponse, Game, GameList, PlayByPlayData
from app.services.game_service import GameService

router = APIRouter()


@router.get("/", response_model=GameList)
def list_games(
    start_date: date | None = Query(None, alias="startDate"),
    end_date: date | None = Query(None, alias="endDate"),
    team: str | None = None,
    season_year: int | None = None,
    season_type: str = Query(
        "REGULAR", pattern="^(REGULAR|PLAYOFF|ALL_STAR|PRESEASON)$"
    ),
    is_playoff: bool | None = Query(None, alias="isPlayoff"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """List games with filtering options.

    Args:
        start_date: Filter by start date (inclusive).
        end_date: Filter by end date (inclusive).
        team: Filter by team abbreviation.
        season_year: Filter by season year.
        season_type: Filter by season type (REGULAR, PLAYOFF, ALL_STAR, PRESEASON).
        is_playoff: Legacy filter for playoff games (overrides season_type).
        page: Page number for pagination.
        per_page: Number of items per page.
        conn: Database connection.

    Returns:
        GameList: Paginated list of games.
    """
    service = GameService(conn)
    effective_season_type = season_type
    if is_playoff is True:
        effective_season_type = "PLAYOFF"
    elif is_playoff is False:
        effective_season_type = "REGULAR"
    return service.list_games(
        start_date=start_date,
        end_date=end_date,
        team_abbrev=team,
        season_year=season_year,
        season_type=effective_season_type,
        page=page,
        per_page=per_page,
    )


@router.get("/today", response_model=list[Game])
def get_todays_games(conn: duckdb.DuckDBPyConnection = Depends(get_connection)):
    """Get games scheduled for today.

    Args:
        conn: Database connection.

    Returns:
        list[Game]: List of games for the current date.
    """
    service = GameService(conn)
    return service.get_todays_games(datetime.now(UTC).date())


@router.get("/by-date/{game_date}", response_model=list[Game])
def get_games_by_date(
    game_date: date,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get games for a specific date.

    Args:
        game_date: The date to fetch games for.
        conn: Database connection.

    Returns:
        list[Game]: List of games for the specified date.
    """
    service = GameService(conn)
    return service.list_games(start_date=game_date, end_date=game_date)["items"]


@router.get("/{game_id}", response_model=Game)
def get_game(
    game_id: int,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get a specific game by ID.

    Args:
        game_id: The unique identifier of the game.
        conn: Database connection.

    Returns:
        Game: The game details.

    Raises:
        HTTPException: If the game is not found.
    """
    service = GameService(conn)
    game = service.get_game_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.get("/{game_id}/box-score", response_model=BoxScoreResponse)
def get_game_box_score(
    game_id: int,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get the box score for a specific game.

    Args:
        game_id: The unique identifier of the game.
        conn: Database connection.

    Returns:
        BoxScoreResponse: The box score data including player and team stats.

    Raises:
        HTTPException: If the game or box score is not found.
    """
    service = GameService(conn)
    box_score = service.get_box_score(game_id)
    if not box_score:
        raise HTTPException(status_code=404, detail="Game not found")
    return box_score


@router.get("/{game_id}/play-by-play", response_model=PlayByPlayData)
def get_game_play_by_play(
    game_id: int,
    period: int | None = None,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get play-by-play data for a game.

    Args:
        game_id: The unique identifier of the game.
        period: Optional filter for a specific period/quarter.
        conn: Database connection.

    Returns:
        PlayByPlayData: The play-by-play events.

    Raises:
        HTTPException: If the game is not found.
    """
    service = GameService(conn)
    pbp = service.get_play_by_play(game_id, period=period)
    if pbp is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return pbp


@router.get("/{game_id}/shot-chart")
def get_game_shot_chart(
    _game_id: int,
    _team_abbrev: str | None = None,
    _player_slug: str | None = None,
    _conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get shot chart data for a game.

    Args:
        _game_id: The unique identifier of the game.
        _team_abbrev: Optional filter by team.
        _player_slug: Optional filter by player.
        conn: Database connection.

    Returns:
        dict: Shot chart data.

    Raises:
        HTTPException: Currently returns 501 Not Implemented.
    """
    raise HTTPException(status_code=501, detail="Shot chart not implemented")
