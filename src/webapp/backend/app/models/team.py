"""Team-related database models."""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    pass


class Franchise(SQLModel, table=True):
    __tablename__ = "franchise"

    franchise_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    founded_year: int
    defunct_year: int | None = None
    city: str | None = Field(default=None, max_length=100)

    teams: list["Team"] = Relationship(back_populates="franchise")


class Team(SQLModel, table=True):
    __tablename__ = "team"

    team_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    abbreviation: str = Field(max_length=3, unique=True, index=True)
    founded_year: int
    defunct_year: int | None = None
    division_id: int | None = Field(default=None, foreign_key="division.division_id")
    franchise_id: int = Field(foreign_key="franchise.franchise_id")
    is_active: bool = Field(default=True)
    is_defunct: bool = Field(default=False)
    city: str | None = Field(default=None, max_length=100)
    arena: str | None = Field(default=None, max_length=100)
    arena_capacity: int | None = None
    relocation_history: dict | None = Field(default=None, sa_type=JSON)

    franchise: Franchise = Relationship(back_populates="teams")
    seasons: list["TeamSeason"] = Relationship(back_populates="team")


class TeamSeason(SQLModel, table=True):
    __tablename__ = "team_season"

    team_id: int = Field(foreign_key="team.team_id", primary_key=True)
    season_id: int = Field(foreign_key="season.season_id", primary_key=True)
    season_type: str = Field(default="REGULAR", primary_key=True)

    games_played: int = Field(default=0)
    wins: int = Field(default=0)
    losses: int = Field(default=0)
    home_wins: int = Field(default=0)
    home_losses: int = Field(default=0)
    road_wins: int = Field(default=0)
    road_losses: int = Field(default=0)
    conference_wins: int = Field(default=0)
    conference_losses: int = Field(default=0)
    division_wins: int = Field(default=0)
    division_losses: int = Field(default=0)

    win_streak: int = Field(default=0)
    loss_streak: int = Field(default=0)
    longest_win_streak: int = Field(default=0)
    longest_loss_streak: int = Field(default=0)

    points_scored: int = Field(default=0)
    points_allowed: int = Field(default=0)
    points_per_game: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )
    points_allowed_per_game: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )

    minutes_played: int = Field(default=0)
    made_fg: int = Field(default=0)
    attempted_fg: int = Field(default=0)
    made_3pt: int = Field(default=0)
    attempted_3pt: int = Field(default=0)
    made_ft: int = Field(default=0)
    attempted_ft: int = Field(default=0)
    offensive_rebounds: int = Field(default=0)
    defensive_rebounds: int = Field(default=0)
    total_rebounds: int = Field(default=0)
    assists: int = Field(default=0)
    steals: int = Field(default=0)
    blocks: int = Field(default=0)
    turnovers: int = Field(default=0)
    personal_fouls: int = Field(default=0)

    pace: Decimal | None = Field(default=None, decimal_places=2, max_digits=6)
    offensive_rating: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=6
    )
    defensive_rating: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=6
    )
    net_rating: Decimal | None = Field(default=None, decimal_places=2, max_digits=6)

    playoff_seed: int | None = None
    made_playoffs: bool = Field(default=False)
    playoff_round_reached: str | None = Field(default=None, max_length=50)

    team: Team = Relationship(back_populates="seasons")

    @property
    def win_percentage(self) -> float:
        total = self.wins + self.losses
        return self.wins / max(total, 1)
