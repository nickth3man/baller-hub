"""Players API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
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
    session: Session = Depends(get_session),
):
    service = PlayerService(session)
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
    session: Session = Depends(get_session),
):
    service = PlayerService(session)
    player = service.get_player_by_slug(player_slug)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/{player_slug}/game-log/{season_year}", response_model=PlayerBoxScoreList)
def get_player_game_log(
    player_slug: str,
    season_year: int,
    season_type: str = Query("REGULAR", pattern="^(REGULAR|PLAYOFF)$"),
    session: Session = Depends(get_session),
):
    service = PlayerService(session)
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
    session: Session = Depends(get_session),
):
    service = PlayerService(session)
    return service.get_player_career_stats(player_slug)


@router.get("/{player_slug}/career", response_model=PlayerCareerStats)
def get_player_career(
    player_slug: str,
    session: Session = Depends(get_session),
):
    service = PlayerService(session)
    career = service.get_player_career(player_slug)
    if not career:
        raise HTTPException(status_code=404, detail="Player not found")
    return career


@router.get("/{player_slug}/splits/{season_year}")
def get_player_splits(
    player_slug: str,
    season_year: int,
    session: Session = Depends(get_session),
):
    service = PlayerService(session)
    return service.get_player_splits(player_slug, season_year)
