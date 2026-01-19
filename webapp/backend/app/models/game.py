"""Game-related database models."""

from datetime import date, time
from decimal import Decimal
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class Location(str, Enum):
    HOME = "HOME"
    AWAY = "AWAY"


class Outcome(str, Enum):
    WIN = "WIN"
    LOSS = "LOSS"


class PeriodType(str, Enum):
    QUARTER = "QUARTER"
    OVERTIME = "OVERTIME"


class PlayType(str, Enum):
    FIELD_GOAL_MADE = "FIELD_GOAL_MADE"
    FIELD_GOAL_MISSED = "FIELD_GOAL_MISSED"
    FREE_THROW_MADE = "FREE_THROW_MADE"
    FREE_THROW_MISSED = "FREE_THROW_MISSED"
    REBOUND_OFFENSIVE = "REBOUND_OFFENSIVE"
    REBOUND_DEFENSIVE = "REBOUND_DEFENSIVE"
    ASSIST = "ASSIST"
    STEAL = "STEAL"
    BLOCK = "BLOCK"
    TURNOVER = "TURNOVER"
    FOUL_PERSONAL = "FOUL_PERSONAL"
    FOUL_TECHNICAL = "FOUL_TECHNICAL"
    FOUL_FLAGRANT = "FOUL_FLAGRANT"
    TIMEOUT = "TIMEOUT"
    SUBSTITUTION = "SUBSTITUTION"
    VIOLATION = "VIOLATION"
    JUMP_BALL = "JUMP_BALL"
    PERIOD_START = "PERIOD_START"
    PERIOD_END = "PERIOD_END"


class Game(SQLModel, table=True):
    __tablename__ = "game"

    game_id: int | None = Field(default=None, primary_key=True)
    season_id: int = Field(foreign_key="season.season_id", index=True)
    game_date: date = Field(index=True)
    game_time: time | None = None
    home_team_id: int = Field(foreign_key="team.team_id", index=True)
    away_team_id: int = Field(foreign_key="team.team_id", index=True)
    home_score: int | None = None
    away_score: int | None = None
    season_type: str = Field(default="REGULAR")

    arena: str | None = Field(default=None, max_length=100)
    attendance: int | None = None
    duration_minutes: int | None = None
    officials: list[str] | None = Field(
        default=None, sa_type_kwargs={"native_json": True}
    )

    playoff_round: str | None = Field(default=None, max_length=50)
    playoff_game_number: int | None = None
    series_home_wins: int | None = None
    series_away_wins: int | None = None

    box_score_url: str | None = Field(default=None, max_length=255)
    play_by_play_url: str | None = Field(default=None, max_length=255)

    box_scores: list["BoxScore"] = Relationship(back_populates="game")
    plays: list["PlayByPlay"] = Relationship(back_populates="game")


class BoxScore(SQLModel, table=True):
    __tablename__ = "box_score"

    box_id: int | None = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.game_id", index=True)
    team_id: int = Field(foreign_key="team.team_id", index=True)

    location: Location
    outcome: Outcome
    opponent_team_id: int | None = Field(default=None, foreign_key="team.team_id")

    seconds_played: int | None = None
    made_fg: int = Field(default=0)
    attempted_fg: int = Field(default=0)
    made_3pt: int = Field(default=0)
    attempted_3pt: int = Field(default=0)
    made_ft: int = Field(default=0)
    attempted_ft: int = Field(default=0)
    offensive_rebounds: int = Field(default=0)
    defensive_rebounds: int = Field(default=0)
    total_rebounds: int | None = None
    assists: int = Field(default=0)
    steals: int = Field(default=0)
    blocks: int = Field(default=0)
    turnovers: int = Field(default=0)
    personal_fouls: int = Field(default=0)
    points_scored: int = Field(default=0)
    plus_minus: int | None = None

    field_goal_percentage: Decimal | None = Field(
        default=None, decimal_places=3, max_digits=5
    )
    three_point_percentage: Decimal | None = Field(
        default=None, decimal_places=3, max_digits=5
    )
    free_throw_percentage: Decimal | None = Field(
        default=None, decimal_places=3, max_digits=5
    )
    quarter_scores: dict | None = Field(
        default=None, sa_type_kwargs={"native_json": True}
    )

    game: Game = Relationship(back_populates="box_scores")


class PlayByPlay(SQLModel, table=True):
    __tablename__ = "play_by_play"

    play_id: int | None = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.game_id", index=True)
    period: int
    period_type: PeriodType
    seconds_remaining: int

    away_score: int | None = None
    home_score: int | None = None
    team_id: int | None = Field(default=None, foreign_key="team.team_id")
    play_type: PlayType
    player_involved_id: int | None = Field(default=None, foreign_key="player.player_id")
    assist_player_id: int | None = Field(default=None, foreign_key="player.player_id")
    block_player_id: int | None = Field(default=None, foreign_key="player.player_id")

    description: str | None = None
    shot_distance_ft: int | None = None
    shot_type: str | None = Field(default=None, max_length=50)
    foul_type: str | None = Field(default=None, max_length=50)
    points_scored: int = Field(default=0)
    is_fast_break: bool = Field(default=False)
    is_second_chance: bool = Field(default=False)

    game: Game = Relationship(back_populates="plays")
