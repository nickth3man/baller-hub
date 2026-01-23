"""Draft API endpoints."""

import duckdb
from fastapi import APIRouter, Depends, HTTPException

from app.db.connection import get_connection
from app.schemas.draft import DraftDetail, DraftSummary
from app.services.draft_service import DraftService

router = APIRouter()


@router.get("/", response_model=list[DraftSummary])
def list_drafts(
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """List all drafts.

    Args:
        conn: Database connection.

    Returns:
        list[DraftSummary]: List of all drafts.
    """
    service = DraftService(conn)
    return service.list_drafts()


@router.get("/{year}", response_model=DraftDetail)
def get_draft(
    year: int,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get a specific draft by year.

    Args:
        year: The year of the draft.
        conn: Database connection.

    Returns:
        DraftDetail: The draft details including picks.

    Raises:
        HTTPException: If the draft is not found.
    """
    service = DraftService(conn)
    draft = service.get_draft_by_year(year)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft
