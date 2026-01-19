"""Player Pydantic schemas for API request/response validation."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class PlayerBase(BaseModel):
    slug: str
    first_name: str
    last_name: str
    position: str | None = None
    is_active: bool = True


class PlayerSummary(PlayerBase):
    player_id: int
    team_abbreviation: str | None = None
    points_per_game: float | None = None
    rebounds_per_game: float | None = None
    assists_per_game: float | None = None

    class Config:
        from_attributes = True


class PlayerDetail(PlayerBase):
    player_id: int
    middle_name: str | None = None
    birth_date: date | None = None
    birth_place_city: str | None = None
    birth_place_country: str | None = None
    height_inches: Decimal | None = None
    weight_lbs: int | None = None
    high_school: str | None = None
    college: str | None = None
    draft_year: int | None = None
    draft_pick: int | None = None
    debut_year: int | None = None
    final_year: int | None = None

    class Config:
        from_attributes = True


class PlayerList(BaseModel):
    items: list[PlayerSummary]
    total: int
    page: int
    per_page: int
    pages: int


class PlayerBoxScoreResponse(BaseModel):
    game_id: int
    game_date: date
    opponent_abbrev: str
    location: str
    outcome: str
    seconds_played: int
    points: int
    rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    made_fg: int
    attempted_fg: int
    made_3pt: int
    attempted_3pt: int
    made_ft: int
    attempted_ft: int
    plus_minus: int | None = None

    class Config:
        from_attributes = True


class PlayerBoxScoreList(BaseModel):
    player_slug: str
    player_name: str
    season_year: int
    season_type: str
    games: list[PlayerBoxScoreResponse]
    totals: dict


class PlayerSeasonStats(BaseModel):
    season_year: int
    team_abbreviation: str | None = None
    games_played: int
    games_started: int
    minutes_per_game: float
    points_per_game: float
    rebounds_per_game: float
    assists_per_game: float
    steals_per_game: float
    blocks_per_game: float
    turnovers_per_game: float
    field_goal_percentage: float | None = None
    three_point_percentage: float | None = None
    free_throw_percentage: float | None = None
    player_efficiency_rating: float | None = None
    win_shares: float | None = None

    class Config:
        from_attributes = True
