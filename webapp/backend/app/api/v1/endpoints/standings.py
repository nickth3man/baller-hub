"""Standings API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.standings import StandingsResponse, PlayoffBracket
from app.services.standings_service import StandingsService

router = APIRouter()


@router.get("/{season_year}", response_model=StandingsResponse)
async def get_standings(
    season_year: int,
    view: str = Query("conference", pattern="^(conference|division|league)$"),
    date: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    service = StandingsService(session)
    if date:
        return await service.get_standings_as_of_date(
            season_year, date, view=view
        )
    return await service.get_standings(season_year, view=view)


@router.get("/{season_year}/by-date/{as_of_date}")
async def get_standings_as_of_date(
    season_year: int,
    as_of_date: str,
    session: AsyncSession = Depends(get_session),
):
    service = StandingsService(session)
    return await service.get_standings_as_of_date(season_year, as_of_date)


@router.get("/{season_year}/expanded")
async def get_expanded_standings(
    season_year: int,
    session: AsyncSession = Depends(get_session),
):
    service = StandingsService(session)
    return await service.get_expanded_standings(season_year)


@router.get("/{season_year}/playoff-bracket", response_model=PlayoffBracket)
async def get_playoff_bracket(
    season_year: int,
    session: AsyncSession = Depends(get_session),
):
    service = StandingsService(session)
    return await service.get_playoff_bracket(season_year)
