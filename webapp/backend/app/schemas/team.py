"""Team Pydantic schemas."""

from pydantic import BaseModel


class Team(BaseModel):
    team_id: int
    name: str
    abbreviation: str
    city: str | None = None
    is_active: bool = True
    founded_year: int | None = None
    arena: str | None = None
    arena_capacity: int | None = None
    franchise: dict | None = None

    class Config:
        from_attributes = True


class RosterPlayer(BaseModel):
    player_id: int
    slug: str
    name: str
    position: str | None = None
    games_played: int
    games_started: int
    ppg: float


class ScheduleGame(BaseModel):
    game_id: int
    date: str
    opponent_abbrev: str
    location: str
    result: str | None = None
    team_score: int | None = None
    opponent_score: int | None = None


class TeamSeasonStats(BaseModel):
    games_played: int
    wins: int
    losses: int
    points_per_game: float | None = None
    points_allowed_per_game: float | None = None
    offensive_rating: float | None = None
    defensive_rating: float | None = None
    net_rating: float | None = None
    pace: float | None = None
    playoff_seed: int | None = None
    made_playoffs: bool | None = None
