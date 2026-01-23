"""Search API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.search import SearchResponse
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=2, max_length=100),
    search_type: str | None = Query(None, pattern="^(player|team|game)$", alias="type"),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """Perform a global search across all entities.

    Args:
        q: The search query string.
        search_type: Optional filter by entity type (player, team, game).
        limit: Maximum number of results to return.
        session: Database session.

    Returns:
        SearchResponse: The search results.
    """
    service = SearchService(session)
    return service.search(query=q, entity_type=search_type, limit=limit)


@router.get("/autocomplete")
def autocomplete(
    q: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(10, ge=1, le=20),
    session: Session = Depends(get_session),
):
    """Get autocomplete suggestions for a query.

    Args:
        q: The partial query string.
        limit: Maximum number of suggestions to return.
        session: Database session.

    Returns:
        dict: Autocomplete suggestions.
    """
    service = SearchService(session)
    return service.autocomplete(query=q, limit=limit)


@router.get("/players")
def search_players(  # noqa: PLR0913
    q: str = Query(..., min_length=2),
    position: str | None = None,
    team_abbrev: str | None = None,
    active_only: bool = False,
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """Search specifically for players.

    Args:
        q: The search query string.
        position: Filter by player position.
        team_abbrev: Filter by team abbreviation.
        active_only: If True, return only active players.
        limit: Maximum number of results to return.
        session: Database session.

    Returns:
        list: List of matching players.
    """
    service = SearchService(session)
    return service.search_players(
        query=q,
        position=position,
        team_abbrev=team_abbrev,
        active_only=active_only,
        limit=limit,
    )


@router.get("/games")
def search_games(  # noqa: PLR0913
    team1: str | None = None,
    team2: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    min_score: int | None = None,
    overtime: bool | None = None,
    playoff: bool | None = None,
    limit: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """Search specifically for games.

    Args:
        team1: Filter by first team.
        team2: Filter by second team.
        date_from: Filter by start date.
        date_to: Filter by end date.
        min_score: Filter by minimum score.
        overtime: Filter by overtime games.
        playoff: Filter by playoff games.
        limit: Maximum number of results to return.
        session: Database session.

    Returns:
        list: List of matching games.
    """
    service = SearchService(session)
    return service.search_games(
        team1=team1,
        team2=team2,
        date_from=date_from,
        date_to=date_to,
        min_score=min_score,
        overtime=overtime,
        playoff=playoff,
        limit=limit,
    )
