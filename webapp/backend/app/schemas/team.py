"""Team Pydantic schemas."""

from pydantic import BaseModel


class TeamBase(BaseModel):
    team_id: int
    name: str
    abbreviation: str
    city: str | None = None
    is_active: bool = True


class TeamSummary(TeamBase):
    conference: str | None = None
    division: str | None = None
    wins: int | None = None
    losses: int | None = None

    class Config:
        from_attributes = True


class TeamDetail(TeamBase):
    founded_year: int
    arena: str | None = None
    arena_capacity: int | None = None
    conference: str | None = None
    division: str | None = None
    franchise_name: str | None = None

    class Config:
        from_attributes = True


class TeamList(BaseModel):
    items: list[TeamSummary]
    total: int


class RosterPlayer(BaseModel):
    player_slug: str
    player_name: str
    position: str | None = None
    jersey_number: int | None = None
    height: str | None = None
    weight: int | None = None
    age: int | None = None
    experience: int | None = None


class TeamRoster(BaseModel):
    team_abbreviation: str
    team_name: str
    season_year: int
    players: list[RosterPlayer]


class ScheduleGame(BaseModel):
    game_id: int
    game_date: str
    opponent_abbrev: str
    location: str
    result: str | None = None
    score: str | None = None


class TeamSchedule(BaseModel):
    team_abbreviation: str
    team_name: str
    season_year: int
    games: list[ScheduleGame]
    record: dict


class TeamSeasonStats(BaseModel):
    team_abbreviation: str
    team_name: str
    season_year: int
    wins: int
    losses: int
    points_per_game: float
    points_allowed_per_game: float
    offensive_rating: float | None = None
    defensive_rating: float | None = None
    net_rating: float | None = None
    pace: float | None = None
