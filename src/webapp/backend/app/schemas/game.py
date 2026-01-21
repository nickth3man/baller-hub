"""Game Pydantic schemas."""

from pydantic import BaseModel


class Game(BaseModel):
    game_id: int
    date: str
    time: str | None = None
    home_team_id: int
    away_team_id: int
    home_score: int | None = None
    away_score: int | None = None
    season_type: str
    is_final: bool = False
    arena: str | None = None
    attendance: int | None = None
    home_team_abbrev: str | None = None
    away_team_abbrev: str | None = None


class GameList(BaseModel):
    items: list[Game]
    total: int
    page: int
    per_page: int
    pages: int


class PlayerBoxScore(BaseModel):
    player_id: int
    slug: str
    name: str
    position: str | None = None
    is_starter: bool
    minutes: int
    points: int
    rebounds: int
    offensive_rebounds: int
    defensive_rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    personal_fouls: int
    fg_made: int
    fg_attempted: int
    fg3_made: int
    fg3_attempted: int
    ft_made: int
    ft_attempted: int
    plus_minus: int | None = None
    game_score: float | None = None


class TeamBoxScore(BaseModel):
    points: int
    fg_made: int
    fg_attempted: int
    fg_pct: float | None = None
    fg3_made: int
    fg3_attempted: int
    fg3_pct: float | None = None
    ft_made: int
    ft_attempted: int
    ft_pct: float | None = None
    offensive_rebounds: int
    defensive_rebounds: int
    total_rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    personal_fouls: int
    quarter_scores: dict | None = None


class BoxScoreTeam(BaseModel):
    team_id: int
    team_abbrev: str | None = None
    team_name: str | None = None
    score: int | None = None
    box_score: TeamBoxScore | None = None
    players: list[PlayerBoxScore]


class BoxScoreResponse(BaseModel):
    game: Game
    home_team: BoxScoreTeam
    away_team: BoxScoreTeam


class Play(BaseModel):
    play_id: int
    period: int
    time: str
    seconds_remaining: int
    away_score: int | None = None
    home_score: int | None = None
    description: str | None = None
    play_type: str
    team_abbrev: str | None = None
    player_id: int | None = None
    points: int


class PlayByPlayData(BaseModel):
    game_id: int
    home_team_abbrev: str
    away_team_abbrev: str
    plays: list[Play]
    period_filter: int | None = None
