"""Season and league structure models."""

from datetime import date
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class LeagueType(str, Enum):
    NBA = "NBA"
    ABA = "ABA"
    BAA = "BAA"


class ConferenceType(str, Enum):
    EASTERN = "EASTERN"
    WESTERN = "WESTERN"


class DivisionType(str, Enum):
    ATLANTIC = "ATLANTIC"
    CENTRAL = "CENTRAL"
    SOUTHEAST = "SOUTHEAST"
    NORTHWEST = "NORTHWEST"
    PACIFIC = "PACIFIC"
    SOUTHWEST = "SOUTHWEST"
    MIDWEST = "MIDWEST"


class League(SQLModel, table=True):
    __tablename__ = "league"

    league_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    league_type: LeagueType
    start_year: int
    end_year: int | None = None
    is_active: bool = Field(default=True)

    seasons: list["Season"] = Relationship(back_populates="league")
    conferences: list["Conference"] = Relationship(back_populates="league")


class Conference(SQLModel, table=True):
    __tablename__ = "conference"

    conference_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    conference_type: ConferenceType = Field(unique=True)
    league_id: int = Field(foreign_key="league.league_id")

    league: League = Relationship(back_populates="conferences")
    divisions: list["Division"] = Relationship(back_populates="conference")


class Division(SQLModel, table=True):
    __tablename__ = "division"

    division_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    division_type: DivisionType = Field(unique=True)
    conference_id: int = Field(foreign_key="conference.conference_id")
    league_id: int = Field(foreign_key="league.league_id")

    conference: Conference = Relationship(back_populates="divisions")


class Season(SQLModel, table=True):
    __tablename__ = "season"

    season_id: int | None = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="league.league_id")
    year: int = Field(index=True)
    season_name: str | None = Field(default=None, max_length=20)
    start_date: date
    end_date: date
    all_star_date: date | None = None
    playoffs_start_date: date | None = None
    playoffs_end_date: date | None = None
    champion_team_id: int | None = Field(default=None, foreign_key="team.team_id")
    runner_up_team_id: int | None = Field(default=None, foreign_key="team.team_id")
    is_active: bool = Field(default=False)

    league: League = Relationship(back_populates="seasons")
