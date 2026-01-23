"""Draft models."""

from datetime import date

from sqlmodel import Field, Relationship, SQLModel

from app.models.player import POSITION_ENUM, Position


class Draft(SQLModel, table=True):
    """Represents an NBA Draft event.

    Attributes:
        draft_id: Unique identifier for the draft.
        season_id: Foreign key to the season.
        year: Year of the draft.
        draft_date: Date the draft took place.
        round_count: Number of rounds in the draft.
        pick_count: Total number of picks in the draft.
        picks: List of picks in this draft.
    """

    __tablename__ = "draft"

    draft_id: int | None = Field(default=None, primary_key=True)
    season_id: int = Field(foreign_key="season.season_id", unique=True)
    year: int = Field(index=True)
    draft_date: date | None = None
    round_count: int
    pick_count: int

    picks: list["DraftPick"] = Relationship(back_populates="draft")


class DraftPick(SQLModel, table=True):
    """Represents a single pick in an NBA Draft.

    Attributes:
        pick_id: Unique identifier for the pick.
        draft_id: Foreign key to the draft.
        overall_pick: Overall pick number in the draft.
        round_number: Round number.
        round_pick: Pick number within the round.
        team_id: Foreign key to the team making the pick.
        player_id: Foreign key to the player selected.
        original_team_id: Foreign key to the team that originally held the pick (if traded).
        trade_notes: Notes about any trades involving this pick.
        college: College attended by the player (if applicable).
        height_in: Height of the player in inches at draft time.
        weight_lbs: Weight of the player in pounds at draft time.
        position: Position of the player.
        draft: The draft event this pick belongs to.
    """

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
    position: Position | None = Field(default=None, sa_type=POSITION_ENUM)

    draft: Draft = Relationship(back_populates="picks")
