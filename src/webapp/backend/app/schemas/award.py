"""Award Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, ConfigDict
from app.models.award import AwardCategory, RecipientType


class AwardRecipientBase(BaseModel):
    award_id: int
    season_id: int
    player_id: int | None = None
    team_id: int | None = None
    vote_rank: int | None = None
    vote_count: int | None = None
    vote_percentage: float | None = None
    first_place_votes: int | None = None
    recipient_type: RecipientType | None = None
    notes: str | None = None


class AwardRecipientSummary(AwardRecipientBase):
    model_config = ConfigDict(from_attributes=True)

    player_name: str | None = None
    team_abbrev: str | None = None
    award_name: str | None = None
    season_year: int | None = None


class AwardBase(BaseModel):
    award_id: int | None = None
    name: str
    category: AwardCategory
    description: str | None = None
    first_awarded_year: int | None = None
    last_awarded_year: int | None = None
    is_active: bool = True


class AwardSummary(AwardBase):
    model_config = ConfigDict(from_attributes=True)


class AwardDetail(AwardSummary):
    model_config = ConfigDict(from_attributes=True)

    recipients: list[AwardRecipientSummary] = []
