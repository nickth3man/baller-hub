"""Game Pydantic schemas."""

from datetime import date, time

from pydantic import BaseModel


class GameSummary(BaseModel):
    game_id: int
    game_date: date
    home_team_abbrev: str
    away_team_abbrev: str
    home_score: int | None = None
    away_score: int | None = None
    season_type: str
    is_final: bool = False

    class Config:
        from_attributes = True


class GameDetail(GameSummary):
    game_time: time | None = None
    arena: str | None = None
    attendance: int | None = None
    season_year: int
    playoff_round: str | None = None
    playoff_game_number: int | None = None


class GameList(BaseModel):
    items: list[GameSummary]
    total: int
    page: int
    per_page: int


class PlayerBoxScoreLine(BaseModel):
    player_slug: str
    player_name: str
    position: str | None = None
    is_starter: bool
    minutes: str
    points: int
    rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    fouls: int
    fg: str
    three_pt: str
    ft: str
    plus_minus: int | None = None


class TeamBoxScore(BaseModel):
    team_abbrev: str
    team_name: str
    players: list[PlayerBoxScoreLine]
    totals: dict


class BoxScoreDetail(BaseModel):
    game_id: int
    game_date: date
    home_team: TeamBoxScore
    away_team: TeamBoxScore
    quarter_scores: dict | None = None


class Play(BaseModel):
    play_id: int
    period: int
    time_remaining: str
    away_score: int
    home_score: int
    description: str
    play_type: str
    team_abbrev: str | None = None


class PlayByPlayData(BaseModel):
    game_id: int
    home_team_abbrev: str
    away_team_abbrev: str
    plays: list[Play]
    period_filter: int | None = None
