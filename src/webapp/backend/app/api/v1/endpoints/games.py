"""Games API endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.game import BoxScoreResponse, Game, GameList, PlayByPlayData
from app.services.game_service import GameService

router = APIRouter()


@router.get("/", response_model=GameList)
async def list_games(
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
    session: AsyncSession = Depends(get_session),
):
    service = GameService(session)
    effective_season_type = season_type
    if is_playoff is True:
        effective_season_type = "PLAYOFF"
    elif is_playoff is False:
        effective_season_type = "REGULAR"
    return await service.list_games(
        start_date=start_date,
        end_date=end_date,
        team_abbrev=team,
        season_year=season_year,
        season_type=effective_season_type,
        page=page,
        per_page=per_page,
    )


@router.get("/today", response_model=list[Game])
async def get_todays_games(session: AsyncSession = Depends(get_session)):
    service = GameService(session)
    return await service.get_todays_games(date.today())


@router.get("/by-date/{game_date}", response_model=list[Game])
async def get_games_by_date(
    game_date: date,
    session: AsyncSession = Depends(get_session),
):
    service = GameService(session)
    return await service.get_games_by_date(game_date)


@router.get("/{game_id}", response_model=Game)
async def get_game(
    game_id: int,
    session: AsyncSession = Depends(get_session),
):
    service = GameService(session)
    game = await service.get_game_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.get("/{game_id}/box-score", response_model=BoxScoreResponse)
async def get_game_box_score(
    game_id: int,
    session: AsyncSession = Depends(get_session),
):
    service = GameService(session)
    box_score = await service.get_box_score(game_id)
    if not box_score:
        raise HTTPException(status_code=404, detail="Game not found")
    return box_score


@router.get("/{game_id}/play-by-play", response_model=PlayByPlayData)
async def get_game_play_by_play(
    game_id: int,
    period: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    service = GameService(session)
    pbp = await service.get_play_by_play(game_id, period=period)
    if pbp is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return pbp


@router.get("/{game_id}/shot-chart")
async def get_game_shot_chart(
    game_id: int,
    team_abbrev: str | None = None,
    player_slug: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    service = GameService(session)
    return await service.get_shot_chart(
        game_id,
        team_abbrev=team_abbrev,
        player_slug=player_slug,
    )
