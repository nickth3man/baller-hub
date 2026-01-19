"""Games API endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.game import BoxScoreDetail, GameDetail, GameList, PlayByPlayData
from app.services.game_service import GameService

router = APIRouter()


@router.get("/", response_model=GameList)
async def list_games(
    date_from: date | None = None,
    date_to: date | None = None,
    team_abbrev: str | None = None,
    season_year: int | None = None,
    season_type: str = Query(
        "REGULAR", pattern="^(REGULAR|PLAYOFF|ALL_STAR|PRESEASON)$"
    ),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    service = GameService(session)
    return await service.list_games(
        date_from=date_from,
        date_to=date_to,
        team_abbrev=team_abbrev,
        season_year=season_year,
        season_type=season_type,
        page=page,
        per_page=per_page,
    )


@router.get("/today", response_model=GameList)
async def get_todays_games(
    session: AsyncSession = Depends(get_session),
):
    service = GameService(session)
    return await service.get_games_by_date(date.today())


@router.get("/by-date/{game_date}", response_model=GameList)
async def get_games_by_date(
    game_date: date,
    session: AsyncSession = Depends(get_session),
):
    service = GameService(session)
    return await service.get_games_by_date(game_date)


@router.get("/{game_id}", response_model=GameDetail)
async def get_game(
    game_id: int,
    session: AsyncSession = Depends(get_session),
):
    service = GameService(session)
    game = await service.get_game_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.get("/{game_id}/box-score", response_model=BoxScoreDetail)
async def get_game_box_score(
    game_id: int,
    session: AsyncSession = Depends(get_session),
):
    service = GameService(session)
    return await service.get_box_score(game_id)


@router.get("/{game_id}/play-by-play", response_model=PlayByPlayData)
async def get_game_play_by_play(
    game_id: int,
    period: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    service = GameService(session)
    return await service.get_play_by_play(game_id, period=period)


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
