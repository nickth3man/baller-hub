"""Search API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.search import SearchResponse
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2, max_length=100),
    type: str | None = Query(None, pattern="^(player|team|game)$"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    service = SearchService(session)
    return await service.search(query=q, entity_type=type, limit=limit)


@router.get("/autocomplete")
async def autocomplete(
    q: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(10, ge=1, le=20),
    session: AsyncSession = Depends(get_session),
):
    service = SearchService(session)
    return await service.autocomplete(query=q, limit=limit)


@router.get("/players")
async def search_players(
    q: str = Query(..., min_length=2),
    position: str | None = None,
    team_abbrev: str | None = None,
    active_only: bool = False,
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    service = SearchService(session)
    return await service.search_players(
        query=q,
        position=position,
        team_abbrev=team_abbrev,
        active_only=active_only,
        limit=limit,
    )


@router.get("/games")
async def search_games(
    team1: str | None = None,
    team2: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    min_score: int | None = None,
    overtime: bool | None = None,
    playoff: bool | None = None,
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    service = SearchService(session)
    return await service.search_games(
        team1=team1,
        team2=team2,
        date_from=date_from,
        date_to=date_to,
        min_score=min_score,
        overtime=overtime,
        playoff=playoff,
        limit=limit,
    )
