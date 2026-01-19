"""Draft models."""

from datetime import date

from sqlmodel import Field, Relationship, SQLModel

from app.models.player import Position


class Draft(SQLModel, table=True):
    __tablename__ = "draft"

    draft_id: int | None = Field(default=None, primary_key=True)
    season_id: int = Field(foreign_key="season.season_id", unique=True)
    year: int = Field(index=True)
    draft_date: date | None = None
    round_count: int
    pick_count: int

    picks: list["DraftPick"] = Relationship(back_populates="draft")


class DraftPick(SQLModel, table=True):
    __tablename__ = "draft_pick"

    pick_id: int | None = Field(default=None, primary_key=True)
    draft_id: int = Field(foreign_key="draft.draft_id", index=True)
    overall_pick: int
    round_number: int
    round_pick: int

    team_id: int = Field(foreign_key="team.team_id", index=True)
    player_id: int | None = Field(default=None, foreign_key="player.player_id")

    original_team_id: int | None = Field(default=None, foreign_key="team.team_id")
    trade_notes: str | None = None

    college: str | None = Field(default=None, max_length=100)
    height_in: int | None = None
    weight_lbs: int | None = None
    position: Position | None = None

    draft: Draft = Relationship(back_populates="picks")
