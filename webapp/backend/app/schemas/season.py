"""Season Pydantic schemas."""

from datetime import date

from pydantic import BaseModel


class SeasonSummary(BaseModel):
    season_id: int
    year: int
    season_name: str | None = None
    is_active: bool
    champion_team_abbrev: str | None = None

    class Config:
        from_attributes = True


class SeasonDetail(SeasonSummary):
    start_date: date
    end_date: date
    all_star_date: date | None = None
    playoffs_start_date: date | None = None
    playoffs_end_date: date | None = None
    champion_team_name: str | None = None
    runner_up_team_name: str | None = None


class SeasonList(BaseModel):
    items: list[SeasonSummary]
    total: int


class LeaderEntry(BaseModel):
    rank: int
    player_slug: str
    player_name: str
    team_abbrev: str
    value: float
    games_played: int


class SeasonLeaders(BaseModel):
    season_year: int
    category: str
    per_game: bool
    leaders: list[LeaderEntry]
