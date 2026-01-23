"""Awards API endpoints."""

import duckdb
from fastapi import APIRouter, Depends, HTTPException

from app.db.connection import get_connection
from app.schemas.award import AwardDetail, AwardSummary
from app.services.award_service import AwardService

router = APIRouter()


@router.get("/", response_model=list[AwardSummary])
def list_awards(
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """List all awards.

    Args:
        conn: Database connection.

    Returns:
        list[AwardSummary]: List of all awards.
    """
    service = AwardService(conn)
    return service.list_awards()


@router.get("/{award_id}", response_model=AwardDetail)
def get_award(
    award_id: int,
    conn: duckdb.DuckDBPyConnection = Depends(get_connection),
):
    """Get a specific award by ID.

    Args:
        award_id: The ID of the award.
        conn: Database connection.

    Returns:
        AwardDetail: The award details including recipients.

    Raises:
        HTTPException: If the award is not found.
    """
    service = AwardService(conn)
    award = service.get_award(award_id)
    if not award:
        raise HTTPException(status_code=404, detail="Award not found")
    return award
