"""Player Pydantic schemas for API request/response validation."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PlayerBase(BaseModel):
    player_id: int
    slug: str
    first_name: str
    last_name: str
    full_name: str
    position: str | None = None
    is_active: bool = True
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
    current_team: str | None = None


class PlayerSummary(PlayerBase):
    model_config = ConfigDict(from_attributes=True)


class PlayerDetail(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    middle_name: str | None = None


class PlayerList(BaseModel):
    items: list[PlayerSummary]
    total: int
    page: int
    per_page: int
    pages: int


class PlayerBoxScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class PlayerBoxScoreList(BaseModel):
    player_slug: str
    player_name: str
    season_year: int
    season_type: str
    games: list[PlayerBoxScoreResponse]
    totals: dict


class PlayerCareerStats(BaseModel):
    player_id: int
    slug: str
    first_name: str
    last_name: str
    games_played: int
    career_points: int
    career_assists: int
    career_rebounds: int
    ppg: float
    apg: float
    rpg: float


class PlayerSeasonStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    season_id: int
    season_year: int
    season_type: str
    team_id: int | None = None
    team_abbrev: str | None = None
    games_played: int
    games_started: int
    minutes_played: int
    points: int
    ppg: float
    rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    fg_made: int
    fg_attempted: int
    fg3_made: int
    fg3_attempted: int
    ft_made: int
    ft_attempted: int
