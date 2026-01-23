"""Teams API endpoints."""

import duckdb
from fastapi import APIRouter, Depends, HTTPException

from app.db.connection import get_connection
from app.schemas.team import RosterPlayer, ScheduleGame, Team, TeamSeasonStats
from app.services.team_service import TeamService

router = APIRouter()


@router.get("/", response_model=list[Team])
def list_teams(
    is_active: bool | None = True,
    conference: str | None = None,
    division: str | None = None,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """List teams with optional filtering.

    Args:
        is_active: Filter by active status (default: True).
        conference: Filter by conference.
        division: Filter by division.
        conn: Database connection.

    Returns:
        list[Team]: List of teams matching the criteria.
    """
    service = TeamService(conn)
    return service.list_teams(
        is_active=is_active if is_active is not None else True,
        conference=conference,
        division=division,
    )


@router.get("/{team_abbrev}", response_model=Team)
def get_team(
    team_abbrev: str,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get details for a specific team.

    Args:
        team_abbrev: Team abbreviation (e.g., 'LAL').
        conn: Database connection.

    Returns:
        Team: Team details.

    Raises:
        HTTPException: If the team is not found.
    """
    service = TeamService(conn)
    team = service.get_team_by_abbreviation(team_abbrev.upper())
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/{team_abbrev}/roster/{season_year}", response_model=list[RosterPlayer])
def get_team_roster(
    team_abbrev: str,
    season_year: int,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Retrieve a team's roster for a specific season.

    Args:
        team_abbrev: Team abbreviation (e.g., 'LAL', 'BOS').
        season_year: The season year.
        conn: DuckDB database connection (injected by FastAPI).

    Returns:
        list[RosterPlayer]: List of roster entries for the team.
    """
    service = TeamService(conn)
    return service.get_team_roster(team_abbrev.upper(), season_year)


@router.get("/{team_abbrev}/schedule/{season_year}", response_model=list[ScheduleGame])
def get_team_schedule(
    team_abbrev: str,
    season_year: int,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Retrieve a team's schedule for a specific season.

    Args:
        team_abbrev: Team abbreviation (e.g., 'LAL', 'BOS').
        season_year: The season year.
        conn: DuckDB database connection (injected by FastAPI).

    Returns:
        list[ScheduleGame]: List of scheduled games for the team.
    """
    service = TeamService(conn)
    return service.get_team_schedule(team_abbrev.upper(), season_year)


@router.get("/{team_abbrev}/stats/{season_year}", response_model=TeamSeasonStats)
def get_team_season_stats(
    team_abbrev: str,
    season_year: int,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get aggregated season stats for a team.

    Args:
        team_abbrev: Team abbreviation.
        season_year: The season year.
        conn: Database connection.

    Returns:
        TeamSeasonStats: Season statistics for the team.

    Raises:
        HTTPException: If stats are not found.
    """
    service = TeamService(conn)
    stats = service.get_team_season_stats(team_abbrev.upper(), season_year)
    if not stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    return stats


@router.get("/{team_abbrev}/history")
def get_team_history(
    team_abbrev: str,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get historical data for a franchise.

    Args:
        team_abbrev: Team abbreviation.
        conn: Database connection.

    Returns:
        list: List of historical team data.
    """
    service = TeamService(conn)
    return service.get_team_history(team_abbrev.upper())
