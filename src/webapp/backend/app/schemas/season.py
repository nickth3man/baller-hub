"""Season Pydantic schemas."""

from datetime import date

from pydantic import BaseModel


class Season(BaseModel):
    season_id: int
    year: int
    season_name: str | None = None
    is_active: bool
    champion: str | None = None

    class Config:
        from_attributes = True


class SeasonDetail(Season):
    start_date: date
    end_date: date
    all_star_date: date | None = None
    playoffs_start_date: date | None = None
    playoffs_end_date: date | None = None
    champion_team_name: str | None = None
    runner_up_team_name: str | None = None


class SeasonLeadersEntry(BaseModel):
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
    leaders: list[SeasonLeadersEntry]


class SeasonScheduleGame(BaseModel):
    game_id: int
    date: str
    time: str | None = None
    home_team_abbrev: str
    away_team_abbrev: str
    home_score: int | None = None
    away_score: int | None = None
    season_type: str


class SeasonSchedule(BaseModel):
    season_year: int
    month: int | None = None
    games: list[SeasonScheduleGame]
