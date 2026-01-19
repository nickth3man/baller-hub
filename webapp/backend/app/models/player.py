"""Player-related database models."""

from datetime import date
from decimal import Decimal
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class Position(str, Enum):
    POINT_GUARD = "POINT_GUARD"
    SHOOTING_GUARD = "SHOOTING_GUARD"
    SMALL_FORWARD = "SMALL_FORWARD"
    POWER_FORWARD = "POWER_FORWARD"
    CENTER = "CENTER"
    GUARD = "GUARD"
    FORWARD = "FORWARD"


class SeasonType(str, Enum):
    REGULAR = "REGULAR"
    PLAYOFF = "PLAYOFF"
    ALL_STAR = "ALL_STAR"
    PRESEASON = "PRESEASON"


class Player(SQLModel, table=True):
    __tablename__ = "player"

    player_id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True, max_length=20)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    middle_name: str | None = Field(default=None, max_length=50)
    birth_date: date | None = None
    birth_place_city: str | None = Field(default=None, max_length=100)
    birth_place_country: str | None = Field(default=None, max_length=100)
    death_date: date | None = None
    height_inches: Decimal | None = Field(default=None, decimal_places=2, max_digits=5)
    weight_lbs: int | None = None
    position: Position | None = None
    high_school: str | None = Field(default=None, max_length=100)
    college: str | None = Field(default=None, max_length=100)
    draft_year: int | None = None
    draft_pick: int | None = None
    debut_date: date | None = None
    final_date: date | None = None
    debut_year: int | None = None
    final_year: int | None = None
    is_active: bool = Field(default=True)

    box_scores: list["PlayerBoxScore"] = Relationship(back_populates="player")
    seasons: list["PlayerSeason"] = Relationship(back_populates="player")
    seasons_advanced: list["PlayerSeasonAdvanced"] = Relationship(
        back_populates="player"
    )

    @property
    def full_name(self) -> str:
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


class PlayerBoxScore(SQLModel, table=True):
    __tablename__ = "player_box_score"

    player_id: int = Field(foreign_key="player.player_id", primary_key=True)
    box_id: int = Field(foreign_key="box_score.box_id", primary_key=True)
    game_id: int = Field(foreign_key="game.game_id", index=True)
    team_id: int = Field(foreign_key="team.team_id", index=True)

    player_slug: str | None = Field(default=None, max_length=20)
    player_name: str | None = None
    position: Position | None = None
    is_starter: bool = Field(default=False)
    seconds_played: int = Field(default=0)
    made_fg: int = Field(default=0)
    attempted_fg: int = Field(default=0)
    made_3pt: int = Field(default=0)
    attempted_3pt: int = Field(default=0)
    made_ft: int = Field(default=0)
    attempted_ft: int = Field(default=0)
    offensive_rebounds: int = Field(default=0)
    defensive_rebounds: int = Field(default=0)
    assists: int = Field(default=0)
    steals: int = Field(default=0)
    blocks: int = Field(default=0)
    turnovers: int = Field(default=0)
    personal_fouls: int = Field(default=0)
    points_scored: int = Field(default=0)
    plus_minus: int | None = None
    game_score: Decimal | None = Field(default=None, decimal_places=2, max_digits=6)

    player: Player = Relationship(back_populates="box_scores")

    @property
    def total_rebounds(self) -> int:
        return self.offensive_rebounds + self.defensive_rebounds

    @property
    def minutes_played(self) -> float:
        return self.seconds_played / 60.0


class PlayerSeason(SQLModel, table=True):
    __tablename__ = "player_season"

    player_id: int = Field(foreign_key="player.player_id", primary_key=True)
    season_id: int = Field(foreign_key="season.season_id", primary_key=True)
    season_type: SeasonType = Field(default=SeasonType.REGULAR, primary_key=True)
    team_id: int | None = Field(default=None, foreign_key="team.team_id")

    player_age: int | None = None
    position: Position | None = None
    games_played: int = Field(default=0)
    games_started: int = Field(default=0)
    minutes_played: int = Field(default=0)
    made_fg: int = Field(default=0)
    attempted_fg: int = Field(default=0)
    made_3pt: int = Field(default=0)
    attempted_3pt: int = Field(default=0)
    made_ft: int = Field(default=0)
    attempted_ft: int = Field(default=0)
    offensive_rebounds: int = Field(default=0)
    defensive_rebounds: int = Field(default=0)
    total_rebounds: int = Field(default=0)
    assists: int = Field(default=0)
    steals: int = Field(default=0)
    blocks: int = Field(default=0)
    turnovers: int = Field(default=0)
    personal_fouls: int = Field(default=0)
    points_scored: int = Field(default=0)
    double_doubles: int = Field(default=0)
    triple_doubles: int = Field(default=0)
    is_combined_totals: bool = Field(default=False)

    player: Player = Relationship(back_populates="seasons")

    @property
    def points_per_game(self) -> float:
        return self.points_scored / max(self.games_played, 1)


class PlayerSeasonAdvanced(SQLModel, table=True):
    __tablename__ = "player_season_advanced"

    player_id: int = Field(foreign_key="player.player_id", primary_key=True)
    season_id: int = Field(foreign_key="season.season_id", primary_key=True)
    season_type: SeasonType = Field(default=SeasonType.REGULAR, primary_key=True)
    team_id: int | None = Field(default=None, foreign_key="team.team_id")

    player_age: int | None = None
    games_played: int = Field(default=0)
    minutes_played: int = Field(default=0)

    player_efficiency_rating: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=6
    )
    true_shooting_percentage: Decimal | None = Field(
        default=None, decimal_places=3, max_digits=5
    )
    effective_fg_percentage: Decimal | None = Field(
        default=None, decimal_places=3, max_digits=5
    )
    three_point_attempt_rate: Decimal | None = Field(
        default=None, decimal_places=3, max_digits=5
    )
    free_throw_attempt_rate: Decimal | None = Field(
        default=None, decimal_places=3, max_digits=5
    )
    usage_percentage: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )
    assist_percentage: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )
    turnover_percentage: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )
    offensive_rebound_percentage: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )
    defensive_rebound_percentage: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )
    total_rebound_percentage: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )
    steal_percentage: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )
    block_percentage: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )
    offensive_box_plus_minus: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )
    defensive_box_plus_minus: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )
    box_plus_minus: Decimal | None = Field(default=None, decimal_places=2, max_digits=5)
    value_over_replacement_player: Decimal | None = Field(
        default=None, decimal_places=2, max_digits=5
    )
    offensive_win_shares: Decimal | None = Field(
        default=None, decimal_places=3, max_digits=6
    )
    defensive_win_shares: Decimal | None = Field(
        default=None, decimal_places=3, max_digits=6
    )
    win_shares: Decimal | None = Field(default=None, decimal_places=3, max_digits=6)
    win_shares_per_48: Decimal | None = Field(
        default=None, decimal_places=3, max_digits=6
    )
    is_combined_totals: bool = Field(default=False)

    player: Player = Relationship(back_populates="seasons_advanced")
