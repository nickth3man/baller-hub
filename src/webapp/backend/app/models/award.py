"""Award models."""

from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class AwardCategory(str, Enum):
    MOST_VALUABLE_PLAYER = "MOST_VALUABLE_PLAYER"
    CHAMPIONSHIP = "CHAMPIONSHIP"
    FINALS_MVP = "FINALS_MVP"
    DEFENSIVE_PLAYER_OF_THE_YEAR = "DEFENSIVE_PLAYER_OF_THE_YEAR"
    ROOKIE_OF_THE_YEAR = "ROOKIE_OF_THE_YEAR"
    COACH_OF_THE_YEAR = "COACH_OF_THE_YEAR"
    SIXTH_MAN = "SIXTH_MAN"
    MOST_IMPROVED = "MOST_IMPROVED"
    ALL_NBA_FIRST_TEAM = "ALL_NBA_FIRST_TEAM"
    ALL_NBA_SECOND_TEAM = "ALL_NBA_SECOND_TEAM"
    ALL_NBA_THIRD_TEAM = "ALL_NBA_THIRD_TEAM"
    ALL_DEFENSIVE_FIRST_TEAM = "ALL_DEFENSIVE_FIRST_TEAM"
    ALL_DEFENSIVE_SECOND_TEAM = "ALL_DEFENSIVE_SECOND_TEAM"
    ALL_ROOKIE_FIRST_TEAM = "ALL_ROOKIE_FIRST_TEAM"
    ALL_ROOKIE_SECOND_TEAM = "ALL_ROOKIE_SECOND_TEAM"
    ALL_STAR = "ALL_STAR"


class RecipientType(str, Enum):
    PLAYER = "PLAYER"
    TEAM = "TEAM"
    COACH = "COACH"


class Award(SQLModel, table=True):
    __tablename__ = "award"

    award_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    category: AwardCategory
    description: str | None = None
    first_awarded_year: int | None = None
    last_awarded_year: int | None = None
    is_active: bool = Field(default=True)

    recipients: list["AwardRecipient"] = Relationship(back_populates="award")


class AwardRecipient(SQLModel, table=True):
    __tablename__ = "award_recipient"

    award_id: int = Field(foreign_key="award.award_id", primary_key=True)
    season_id: int = Field(foreign_key="season.season_id", primary_key=True)
    player_id: int | None = Field(default=None, foreign_key="player.player_id")
    team_id: int | None = Field(default=None, foreign_key="team.team_id")

    vote_rank: int | None = None
    vote_count: int | None = None
    vote_percentage: float | None = None
    first_place_votes: int | None = None
    recipient_type: RecipientType | None = None
    notes: str | None = None

    award: Award = Relationship(back_populates="recipients")
