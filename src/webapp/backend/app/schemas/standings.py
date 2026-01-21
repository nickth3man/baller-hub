"""Standings Pydantic schemas."""

from pydantic import BaseModel


class StandingsTeam(BaseModel):
    team_id: int
    name: str
    abbreviation: str
    wins: int
    losses: int
    win_pct: float
    games_back: float
    conference_rank: int | None = None
    points_per_game: float | None = None
    points_allowed_per_game: float | None = None
    net_rating: float | None = None


class StandingsResponse(BaseModel):
    season_year: int
    view: str
    eastern: list[StandingsTeam] | None = None
    western: list[StandingsTeam] | None = None
    league: list[StandingsTeam] | None = None


class PlayoffSeries(BaseModel):
    round_name: str
    series_number: int
    team1_abbrev: str
    team1_seed: int
    team1_wins: int
    team2_abbrev: str
    team2_seed: int
    team2_wins: int
    winner_abbrev: str | None = None
    is_complete: bool


class PlayoffBracket(BaseModel):
    season_year: int
    eastern_conference: list[list[PlayoffSeries]]
    western_conference: list[list[PlayoffSeries]]
    finals: PlayoffSeries | None = None
    champion_abbrev: str | None = None
