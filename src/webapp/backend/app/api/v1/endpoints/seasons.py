"""Seasons API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.season import Season, SeasonDetail, SeasonLeaders, SeasonSchedule
from app.services.season_service import SeasonService

router = APIRouter()


@router.get("/", response_model=list[Season])
def list_seasons(
    league: str = "NBA",
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    service = SeasonService(session)
    return service.list_seasons(league=league, limit=limit)


@router.get("/current", response_model=SeasonDetail)
def get_current_season(
    session: Session = Depends(get_session),
):
    service = SeasonService(session)
    season = service.get_current_season()
    if not season:
        raise HTTPException(status_code=404, detail="No active season found")
    return season


@router.get("/{season_year}", response_model=SeasonDetail)
def get_season(
    season_year: int,
    session: Session = Depends(get_session),
):
    service = SeasonService(session)
    season = service.get_season_by_year(season_year)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    return season


@router.get("/{season_year}/schedule", response_model=SeasonSchedule)
def get_season_schedule(
    season_year: int,
    month: int | None = None,
    session: Session = Depends(get_session),
):
    service = SeasonService(session)
    return service.get_season_schedule(season_year, month=month)


@router.get("/{season_year}/leaders", response_model=SeasonLeaders)
def get_season_leaders(
    season_year: int,
    category: str = Query(
        "points", pattern="^(points|rebounds|assists|steals|blocks)$"
    ),
    per_game: bool = True,
    limit: int = Query(10, ge=1, le=50),
    session: Session = Depends(get_session),
):
    service = SeasonService(session)
    return service.get_season_leaders(
        season_year,
        category=category,
        per_game=per_game,
        limit=limit,
    )


@router.get("/{season_year}/player-stats")
def get_season_player_stats(
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
    session: Session = Depends(get_session),
):
    service = SeasonService(session)
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
