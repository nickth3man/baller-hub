"""Teams API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.team import (
    TeamDetail,
    TeamList,
    TeamRoster,
    TeamSchedule,
    TeamSeasonStats,
)
from app.services.team_service import TeamService

router = APIRouter()


@router.get("/", response_model=TeamList)
async def list_teams(
    is_active: bool | None = True,
    conference: str | None = None,
    division: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    service = TeamService(session)
    return await service.list_teams(
        is_active=is_active,
        conference=conference,
        division=division,
    )


@router.get("/{team_abbrev}", response_model=TeamDetail)
async def get_team(
    team_abbrev: str,
    session: AsyncSession = Depends(get_session),
):
    service = TeamService(session)
    team = await service.get_team_by_abbreviation(team_abbrev.upper())
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/{team_abbrev}/roster/{season_year}", response_model=TeamRoster)
async def get_team_roster(
    team_abbrev: str,
    season_year: int,
    session: AsyncSession = Depends(get_session),
):
    service = TeamService(session)
    return await service.get_team_roster(team_abbrev.upper(), season_year)


@router.get("/{team_abbrev}/schedule/{season_year}", response_model=TeamSchedule)
async def get_team_schedule(
    team_abbrev: str,
    season_year: int,
    session: AsyncSession = Depends(get_session),
):
    service = TeamService(session)
    return await service.get_team_schedule(team_abbrev.upper(), season_year)


@router.get("/{team_abbrev}/stats/{season_year}", response_model=TeamSeasonStats)
async def get_team_season_stats(
    team_abbrev: str,
    season_year: int,
    session: AsyncSession = Depends(get_session),
):
    service = TeamService(session)
    return await service.get_team_season_stats(team_abbrev.upper(), season_year)


@router.get("/{team_abbrev}/history")
async def get_team_history(
    team_abbrev: str,
    session: AsyncSession = Depends(get_session),
):
    service = TeamService(session)
    return await service.get_team_history(team_abbrev.upper())
