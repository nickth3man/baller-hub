"""Standings API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.standings import PlayoffBracket, StandingsResponse
from app.services.standings_service import StandingsService

router = APIRouter()


@router.get("/{season_year}", response_model=StandingsResponse)
def get_standings(
    season_year: int,
    view: str = Query("conference", pattern="^(conference|division|league)$"),
    date: str | None = None,
    session: Session = Depends(get_session),
):
    """Get standings for a specific season.

    Args:
        season_year: The season year.
        view: The view mode (conference, division, or league).
        date: Optional date to get standings as of (YYYY-MM-DD).
        session: Database session.

    Returns:
        StandingsResponse: The standings data.
    """
    service = StandingsService(session)
    if date:
        return service.get_standings_as_of_date(season_year, date, view=view)
    return service.get_standings(season_year, view=view)


@router.get("/{season_year}/by-date/{as_of_date}")
def get_standings_as_of_date(
    season_year: int,
    as_of_date: str,
    session: Session = Depends(get_session),
):
    """Get standings as of a specific date.

    Args:
        season_year: The season year.
        as_of_date: The date to retrieve standings for.
        session: Database session.

    Returns:
        dict: Standings data.
    """
    service = StandingsService(session)
    return service.get_standings_as_of_date(season_year, as_of_date)


@router.get("/{season_year}/expanded")
def get_expanded_standings(
    season_year: int,
    session: Session = Depends(get_session),
):
    """Get expanded standings with detailed statistics.

    Args:
        season_year: The season year.
        session: Database session.

    Returns:
        dict: Expanded standings data.
    """
    service = StandingsService(session)
    return service.get_expanded_standings(season_year)


@router.get("/{season_year}/playoff-bracket", response_model=PlayoffBracket)
def get_playoff_bracket(
    season_year: int,
    session: Session = Depends(get_session),
):
    """Get the playoff bracket for a season.

    Args:
        season_year: The season year.
        session: Database session.

    Returns:
        PlayoffBracket: The playoff bracket structure.
    """
    service = StandingsService(session)
    return service.get_playoff_bracket(season_year)
