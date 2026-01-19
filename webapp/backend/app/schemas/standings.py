"""Standings Pydantic schemas."""

from pydantic import BaseModel


class TeamStanding(BaseModel):
    team_id: int
    team_abbrev: str
    team_name: str
    wins: int
    losses: int
    win_pct: float
    games_back: float
    home_record: str
    road_record: str
    last_10: str
    streak: str
    points_per_game: float
    points_allowed_per_game: float
    net_rating: float | None = None


class DivisionStandings(BaseModel):
    division_name: str
    teams: list[TeamStanding]


class ConferenceStandings(BaseModel):
    conference_name: str
    divisions: list[DivisionStandings] | None = None
    teams: list[TeamStanding]


class StandingsResponse(BaseModel):
    season_year: int
    view: str
    eastern: ConferenceStandings | None = None
    western: ConferenceStandings | None = None
    league: list[TeamStanding] | None = None


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
