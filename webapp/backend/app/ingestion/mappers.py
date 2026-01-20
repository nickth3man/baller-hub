"""Mappers to convert scraper output to database model instances.

These functions transform the raw dictionaries returned by the scraper
into SQLModel instances that can be persisted to the database.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from app.models.game import (
    BoxScore,
    Game,
    Location,
    Outcome,
    PlayByPlay,
    PlayType,
    PeriodType,
)
from app.models.player import (
    Player,
    PlayerBoxScore,
    PlayerSeason,
    PlayerSeasonAdvanced,
    Position,
    SeasonType,
)
from app.models.season import Season
from app.models.team import Team, TeamSeason


def _safe_decimal(value: Any, default: Decimal | None = None) -> Decimal | None:
    """Safely convert a value to Decimal."""
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _safe_date(value: Any) -> date | None:
    """Safely convert a value to date."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def _seconds_from_minutes_str(minutes_str: str | None) -> int:
    """Convert 'MM:SS' or 'M:SS' format to total seconds."""
    if not minutes_str:
        return 0
    try:
        parts = str(minutes_str).split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return int(float(parts[0]) * 60)
    except (ValueError, TypeError):
        return 0


def _map_position(position_value: str | list[str] | None) -> Position | None:
    """Map position string to Position enum."""
    if not position_value:
        return None
    if isinstance(position_value, list):
        for entry in position_value:
            mapped = _map_position(entry)
            if mapped:
                return mapped
        return None
    position_str = str(position_value)
    pos_map = {
        "PG": Position.POINT_GUARD,
        "SG": Position.SHOOTING_GUARD,
        "SF": Position.SMALL_FORWARD,
        "PF": Position.POWER_FORWARD,
        "C": Position.CENTER,
        "G": Position.GUARD,
        "F": Position.FORWARD,
        "G-F": Position.GUARD,
        "F-G": Position.FORWARD,
        "F-C": Position.FORWARD,
        "C-F": Position.CENTER,
    }
    return pos_map.get(position_str.upper().strip())


def _extract_player_slug(name: str | None, identifier: str | None = None) -> str:
    """Extract or generate a player slug.

    The scraper sometimes provides the player identifier directly,
    otherwise we generate a slug from the name.
    """
    if identifier:
        return identifier

    if not name:
        return "unknown"

    # Generate slug from name: "LeBron James" -> "jamesle01"
    parts = name.lower().split()
    if len(parts) >= 2:
        last = parts[-1][:5]  # First 5 chars of last name
        first = parts[0][:2]  # First 2 chars of first name
        return f"{last}{first}01"
    return parts[0][:7] + "01" if parts else "unknown01"


def map_player_box_score(
    raw: dict[str, Any],
    player_id: int,
    box_id: int,
    game_id: int,
    team_id: int,
) -> PlayerBoxScore:
    """Map a raw player box score dict to a PlayerBoxScore model.

    Args:
        raw: Dictionary from scraper's player_box_scores().
        player_id: Database player ID.
        box_id: Database box_score ID.
        game_id: Database game ID.
        team_id: Database team ID.

    Returns:
        PlayerBoxScore model instance (not yet committed).
    """
    return PlayerBoxScore(
        player_id=player_id,
        box_id=box_id,
        game_id=game_id,
        team_id=team_id,
        player_slug=raw.get("slug") or _extract_player_slug(raw.get("name")),
        player_name=raw.get("name"),
        position=_map_position(raw.get("position")),
        is_starter=raw.get("is_starter", False),
        seconds_played=_seconds_from_minutes_str(raw.get("seconds_played")),
        made_fg=_safe_int(raw.get("made_field_goals")),
        attempted_fg=_safe_int(raw.get("attempted_field_goals")),
        made_3pt=_safe_int(raw.get("made_three_point_field_goals")),
        attempted_3pt=_safe_int(raw.get("attempted_three_point_field_goals")),
        made_ft=_safe_int(raw.get("made_free_throws")),
        attempted_ft=_safe_int(raw.get("attempted_free_throws")),
        offensive_rebounds=_safe_int(raw.get("offensive_rebounds")),
        defensive_rebounds=_safe_int(raw.get("defensive_rebounds")),
        assists=_safe_int(raw.get("assists")),
        steals=_safe_int(raw.get("steals")),
        blocks=_safe_int(raw.get("blocks")),
        turnovers=_safe_int(raw.get("turnovers")),
        personal_fouls=_safe_int(raw.get("personal_fouls")),
        points_scored=_safe_int(raw.get("points_scored")),
        plus_minus=raw.get("plus_minus"),
        game_score=_safe_decimal(raw.get("game_score")),
    )


def map_player_season_totals(
    raw: dict[str, Any],
    player_id: int,
    season_id: int,
    team_id: int | None = None,
) -> PlayerSeason:
    """Map raw player season totals to a PlayerSeason model.

    Args:
        raw: Dictionary from scraper's players_season_totals().
        player_id: Database player ID.
        season_id: Database season ID.
        team_id: Optional team ID for the season.

    Returns:
        PlayerSeason model instance.
    """
    return PlayerSeason(
        player_id=player_id,
        season_id=season_id,
        season_type=SeasonType.REGULAR,
        team_id=team_id,
        player_age=raw.get("age"),
        position=_map_position(raw.get("positions")),
        games_played=_safe_int(raw.get("games_played")),
        games_started=_safe_int(raw.get("games_started")),
        minutes_played=_safe_int(raw.get("minutes_played")),
        made_fg=_safe_int(raw.get("made_field_goals")),
        attempted_fg=_safe_int(raw.get("attempted_field_goals")),
        made_3pt=_safe_int(raw.get("made_three_point_field_goals")),
        attempted_3pt=_safe_int(raw.get("attempted_three_point_field_goals")),
        made_ft=_safe_int(raw.get("made_free_throws")),
        attempted_ft=_safe_int(raw.get("attempted_free_throws")),
        offensive_rebounds=_safe_int(raw.get("offensive_rebounds")),
        defensive_rebounds=_safe_int(raw.get("defensive_rebounds")),
        total_rebounds=_safe_int(raw.get("total_rebounds")),
        assists=_safe_int(raw.get("assists")),
        steals=_safe_int(raw.get("steals")),
        blocks=_safe_int(raw.get("blocks")),
        turnovers=_safe_int(raw.get("turnovers")),
        personal_fouls=_safe_int(raw.get("personal_fouls")),
        points_scored=_safe_int(raw.get("points")),
        is_combined_totals=raw.get("is_combined_totals", False),
    )


def map_player_advanced_totals(
    raw: dict[str, Any],
    player_id: int,
    season_id: int,
    team_id: int | None = None,
) -> PlayerSeasonAdvanced:
    """Map raw player advanced stats to a PlayerSeasonAdvanced model.

    Args:
        raw: Dictionary from scraper's players_advanced_season_totals().
        player_id: Database player ID.
        season_id: Database season ID.
        team_id: Optional team ID.

    Returns:
        PlayerSeasonAdvanced model instance.
    """
    return PlayerSeasonAdvanced(
        player_id=player_id,
        season_id=season_id,
        season_type=SeasonType.REGULAR,
        team_id=team_id,
        player_age=raw.get("age"),
        games_played=_safe_int(raw.get("games_played")),
        minutes_played=_safe_int(raw.get("minutes_played")),
        player_efficiency_rating=_safe_decimal(raw.get("player_efficiency_rating")),
        true_shooting_percentage=_safe_decimal(raw.get("true_shooting_percentage")),
        effective_fg_percentage=_safe_decimal(
            raw.get("effective_field_goal_percentage")
        ),
        three_point_attempt_rate=_safe_decimal(raw.get("three_point_attempt_rate")),
        free_throw_attempt_rate=_safe_decimal(raw.get("free_throw_attempt_rate")),
        usage_percentage=_safe_decimal(raw.get("usage_percentage")),
        assist_percentage=_safe_decimal(raw.get("assist_percentage")),
        turnover_percentage=_safe_decimal(raw.get("turnover_percentage")),
        offensive_rebound_percentage=_safe_decimal(
            raw.get("offensive_rebound_percentage")
        ),
        defensive_rebound_percentage=_safe_decimal(
            raw.get("defensive_rebound_percentage")
        ),
        total_rebound_percentage=_safe_decimal(raw.get("total_rebound_percentage")),
        steal_percentage=_safe_decimal(raw.get("steal_percentage")),
        block_percentage=_safe_decimal(raw.get("block_percentage")),
        offensive_box_plus_minus=_safe_decimal(raw.get("offensive_box_plus_minus")),
        defensive_box_plus_minus=_safe_decimal(raw.get("defensive_box_plus_minus")),
        box_plus_minus=_safe_decimal(raw.get("box_plus_minus")),
        value_over_replacement_player=_safe_decimal(
            raw.get("value_over_replacement_player")
        ),
        offensive_win_shares=_safe_decimal(raw.get("offensive_win_shares")),
        defensive_win_shares=_safe_decimal(raw.get("defensive_win_shares")),
        win_shares=_safe_decimal(raw.get("win_shares")),
        win_shares_per_48=_safe_decimal(raw.get("win_shares_per_48_minutes")),
        is_combined_totals=raw.get("is_combined_totals", False),
    )


def map_schedule_game(
    raw: dict[str, Any],
    season_id: int,
    home_team_id: int,
    away_team_id: int,
) -> Game:
    """Map a raw schedule entry to a Game model.

    Args:
        raw: Dictionary from scraper's season_schedule().
        season_id: Database season ID.
        home_team_id: Database team ID for home team.
        away_team_id: Database team ID for away team.

    Returns:
        Game model instance.
    """
    game_date = _safe_date(raw.get("start_time"))
    if game_date is None:
        # Fallback to parsing date components
        game_date = date.today()

    return Game(
        season_id=season_id,
        game_date=game_date,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        home_score=raw.get("home_team_score"),
        away_score=raw.get("away_team_score"),
        season_type="REGULAR",
        box_score_url=raw.get("box_score_url"),
    )


def map_standings(
    raw: dict[str, Any],
    team_id: int,
    season_id: int,
) -> TeamSeason:
    """Map raw standings data to a TeamSeason model.

    Args:
        raw: Dictionary from scraper's standings().
        team_id: Database team ID.
        season_id: Database season ID.

    Returns:
        TeamSeason model instance.
    """
    return TeamSeason(
        team_id=team_id,
        season_id=season_id,
        season_type="REGULAR",
        wins=_safe_int(raw.get("wins")),
        losses=_safe_int(raw.get("losses")),
        games_played=_safe_int(raw.get("wins", 0)) + _safe_int(raw.get("losses", 0)),
        points_per_game=_safe_decimal(raw.get("points_per_game")),
        points_allowed_per_game=_safe_decimal(raw.get("opponent_points_per_game")),
    )
