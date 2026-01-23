"""Draft Pydantic schemas for API request/response validation."""

from datetime import date
from pydantic import BaseModel, ConfigDict
from app.models.player import Position


class DraftPickBase(BaseModel):
    pick_id: int | None = None
    draft_id: int
    overall_pick: int
    round_number: int
    round_pick: int
    team_id: int
    player_id: int | None = None
    original_team_id: int | None = None
    trade_notes: str | None = None
    college: str | None = None
    height_in: int | None = None
    weight_lbs: int | None = None
    position: Position | None = None


class DraftPickSummary(DraftPickBase):
    model_config = ConfigDict(from_attributes=True)

    player_name: str | None = None
    team_abbrev: str | None = None


class DraftBase(BaseModel):
    draft_id: int | None = None
    season_id: int
    year: int
    draft_date: date | None = None
    round_count: int
    pick_count: int


class DraftSummary(DraftBase):
    model_config = ConfigDict(from_attributes=True)


class DraftDetail(DraftSummary):
    model_config = ConfigDict(from_attributes=True)

    picks: list[DraftPickSummary] = []
