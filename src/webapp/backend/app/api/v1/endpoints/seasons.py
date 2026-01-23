"""Seasons API endpoints."""

import duckdb
from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.connection import get_connection
from app.schemas.season import Season, SeasonDetail, SeasonLeaders, SeasonSchedule
from app.services.season_service import SeasonService

router = APIRouter()


@router.get("/", response_model=list[Season])
def list_seasons(
    league: str = "NBA",
    limit: int = Query(20, ge=1, le=100),
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """List available seasons.

    Args:
        league: League identifier (default: "NBA").
        limit: Maximum number of seasons to return.
        conn: Database connection.

    Returns:
        list[Season]: List of seasons.
    """
    service = SeasonService(conn)
    return service.list_seasons(league=league, limit=limit)


@router.get("/current", response_model=SeasonDetail)
def get_current_season(
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get the current active season.

    Args:
        conn: Database connection.

    Returns:
        SeasonDetail: Details of the current season.

    Raises:
        HTTPException: If no active season is found.
    """
    service = SeasonService(conn)
    season = service.get_current_season()
    if not season:
        raise HTTPException(status_code=404, detail="No active season found")
    return season


@router.get("/{season_year}", response_model=SeasonDetail)
def get_season(
    season_year: int,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get details for a specific season.

    Args:
        season_year: The year of the season.
        conn: Database connection.

    Returns:
        SeasonDetail: Details of the requested season.

    Raises:
        HTTPException: If the season is not found.
    """
    service = SeasonService(conn)
    season = service.get_season_by_year(season_year)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    return season


@router.get("/{season_year}/schedule", response_model=SeasonSchedule)
def get_season_schedule(
    season_year: int,
    month: int | None = None,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get the schedule for a specific season.

    Args:
        season_year: The year of the season.
        month: Optional filter for a specific month.
        conn: Database connection.

    Returns:
        SeasonSchedule: The schedule for the season.
    """
    service = SeasonService(conn)
    return service.get_season_schedule(season_year, month=month)


@router.get("/{season_year}/leaders", response_model=SeasonLeaders)
def get_season_leaders(
    season_year: int,
    category: str = Query(
        "points", pattern="^(points|rebounds|assists|steals|blocks)$"
    ),
    per_game: bool = True,
    limit: int = Query(10, ge=1, le=50),
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get statistical leaders for a specific season.

    Args:
        season_year: The year of the season.
        category: Statistical category (points, rebounds, assists, etc.).
        per_game: Whether to return per-game stats or totals.
        limit: Number of leaders to return.
        conn: Database connection.

    Returns:
        SeasonLeaders: List of leaders for the category.
    """
    service = SeasonService(conn)
    return service.get_season_leaders(
        season_year,
        category=category,
        per_game=per_game,
        limit=limit,
    )


@router.get("/{season_year}/player-stats")
def get_season_player_stats(  # noqa: PLR0913
    season_year: int,
    stat_type: str = Query(
        "totals", pattern="^(totals|per_game|advanced|per_36|per_100)$"
    ),
    position: str | None = None,
    min_games: int = Query(0, ge=0),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    sort_by: str = "points",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get comprehensive player statistics for a season.

    Args:
        season_year: The year of the season.
        stat_type: Type of stats (totals, per_game, advanced, etc.).
        position: Optional filter by player position.
        min_games: Minimum games played filter.
        page: Page number.
        per_page: Items per page.
        sort_by: Field to sort by.
        sort_order: Sort order (asc or desc).
        conn: Database connection.

    Returns:
        dict: Paginated player statistics.
    """
    service = SeasonService(conn)
    return service.get_season_player_stats(
        season_year,
        stat_type=stat_type,
        position=position,
        min_games=min_games,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )
