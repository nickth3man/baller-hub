"""Players API endpoints."""

import duckdb
from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.connection import get_connection
from app.schemas.player import (
    PlayerBoxScoreList,
    PlayerCareerStats,
    PlayerDetail,
    PlayerList,
    PlayerSeasonStats,
)
from app.services.player_service import PlayerService

router = APIRouter()


@router.get("/", response_model=PlayerList)
def list_players(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    is_active: bool | None = None,
    position: str | None = None,
    search: str | None = None,
    season: int | None = None,
    team: str | None = None,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """List players with filtering options.

    Args:
        page: Page number for pagination.
        per_page: Number of items per page.
        is_active: Filter by active status.
        position: Filter by player position.
        search: Search term for player name.
        season: Filter by season year.
        team: Filter by team abbreviation.
        conn: Database connection.

    Returns:
        PlayerList: Paginated list of players.
    """
    service = PlayerService(conn)
    return service.list_players(
        page=page,
        per_page=per_page,
        is_active=is_active,
        position=position,
        search=search,
        season_year=season,
        team_abbrev=team,
    )


@router.get("/{player_slug}", response_model=PlayerDetail)
def get_player(
    player_slug: str,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get a specific player by slug.

    Args:
        player_slug: The unique slug of the player.
        conn: Database connection.

    Returns:
        PlayerDetail: The player details.

    Raises:
        HTTPException: If the player is not found.
    """
    service = PlayerService(conn)
    player = service.get_player_by_slug(player_slug)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/{player_slug}/game-log/{season_year}", response_model=PlayerBoxScoreList)
def get_player_game_log(
    player_slug: str,
    season_year: int,
    season_type: str = Query("REGULAR", pattern="^(REGULAR|PLAYOFF)$"),
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get game log for a player in a specific season.

    Args:
        player_slug: The unique slug of the player.
        season_year: The season year.
        season_type: The type of season (REGULAR or PLAYOFF).
        conn: Database connection.

    Returns:
        PlayerBoxScoreList: List of game logs for the player.

    Raises:
        HTTPException: If the player or season is not found.
    """
    service = PlayerService(conn)
    game_log = service.get_player_game_log(
        player_slug=player_slug,
        season_year=season_year,
        season_type=season_type,
    )
    if game_log is None:
        raise HTTPException(status_code=404, detail="Player or season not found")
    return game_log


@router.get("/{player_slug}/career-stats", response_model=list[PlayerSeasonStats])
def get_player_career_stats(
    player_slug: str,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get career statistics for a player.

    Args:
        player_slug: The unique slug of the player.
        conn: Database connection.

    Returns:
        list[PlayerSeasonStats]: List of seasonal stats for the player's career.
    """
    service = PlayerService(conn)
    return service.get_player_career_stats(player_slug)


@router.get("/{player_slug}/career", response_model=PlayerCareerStats)
def get_player_career(
    player_slug: str,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get summarized career stats for a player.

    Args:
        player_slug: The unique slug of the player.
        conn: Database connection.

    Returns:
        PlayerCareerStats: Summarized career statistics.

    Raises:
        HTTPException: If the player is not found.
    """
    service = PlayerService(conn)
    career = service.get_player_career(player_slug)
    if not career:
        raise HTTPException(status_code=404, detail="Player not found")
    return career


@router.get("/{player_slug}/splits/{season_year}")
def get_player_splits(
    player_slug: str,
    season_year: int,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get performance splits for a player in a specific season.

    Args:
        player_slug: The unique slug of the player.
        season_year: The season year.
        conn: Database connection.

    Returns:
        dict: Player performance splits.
    """
    service = PlayerService(conn)
    return service.get_player_splits(player_slug, season_year)
