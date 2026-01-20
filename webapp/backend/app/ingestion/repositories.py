"""Repository layer for entity lookup and upsert operations.

Provides methods to find-or-create entities by their natural keys,
handling the foreign key dependencies during data ingestion.
"""

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models.game import BoxScore, Game, Location, Outcome
from app.models.player import Player, PlayerBoxScore, PlayerSeason, PlayerSeasonAdvanced
from app.models.season import League, LeagueType, Season
from app.models.team import Franchise, Team, TeamSeason
from src.common.data import (
    TEAM_ABBREVIATIONS_TO_TEAM,
    TEAM_NAME_TO_TEAM,
    TEAM_TO_TEAM_ABBREVIATION,
)

# Cache for frequently accessed entities to avoid repeated queries
_team_cache: dict[str, int] = {}
_player_cache: dict[str, int] = {}
_season_cache: dict[int, int] = {}


async def clear_caches():
    """Clear all entity caches. Call at start of new ingestion session."""
    global _team_cache, _player_cache, _season_cache
    _team_cache = {}
    _player_cache = {}
    _season_cache = {}


async def get_or_create_league(session: AsyncSession) -> int:
    """Get or create the NBA league record."""
    query = select(League).where(League.league_type == LeagueType.NBA)
    result = await session.execute(query)
    league = result.scalar_one_or_none()

    if league is None:
        league = League(
            name="National Basketball Association",
            league_type=LeagueType.NBA,
            start_year=1946,
            is_active=True,
        )
        session.add(league)
        await session.flush()

    return league.league_id


async def get_or_create_season(session: AsyncSession, season_end_year: int) -> int:
    """Get or create a season by its end year.

    Args:
        session: Database session.
        season_end_year: Year the season ends (e.g., 2024 for 2023-24).

    Returns:
        The season_id.
    """
    if season_end_year in _season_cache:
        return _season_cache[season_end_year]

    query = select(Season).where(Season.year == season_end_year)
    result = await session.execute(query)
    season = result.scalar_one_or_none()

    if season is None:
        league_id = await get_or_create_league(session)
        season = Season(
            league_id=league_id,
            year=season_end_year,
            season_name=f"{season_end_year - 1}-{str(season_end_year)[2:]}",
            start_date=date(season_end_year - 1, 10, 1),
            end_date=date(season_end_year, 6, 30),
            is_active=(season_end_year >= date.today().year),
        )
        session.add(season)
        await session.flush()

    _season_cache[season_end_year] = season.season_id
    return season.season_id


async def get_or_create_team(
    session: AsyncSession, abbreviation: str, name: str | None = None
) -> int:
    """Get or create a team by abbreviation.

    Args:
        session: Database session.
        abbreviation: Team abbreviation (e.g., 'BOS').
        name: Optional team name.

    Returns:
        The team_id.
    """
    normalized = abbreviation.strip().upper()
    team_name = name
    team_abbrev = normalized
    if normalized in TEAM_ABBREVIATIONS_TO_TEAM:
        team_enum = TEAM_ABBREVIATIONS_TO_TEAM[normalized]
        team_name = team_name or team_enum.value
    elif normalized in TEAM_NAME_TO_TEAM:
        team_enum = TEAM_NAME_TO_TEAM[normalized]
        team_abbrev = TEAM_TO_TEAM_ABBREVIATION.get(team_enum, normalized[:3])
        team_name = team_name or team_enum.value
    else:
        team_abbrev = normalized[:3]
        team_name = team_name or abbreviation

    if team_abbrev in _team_cache:
        return _team_cache[team_abbrev]

    query = select(Team).where(Team.abbreviation == team_abbrev)
    result = await session.execute(query)
    team = result.scalar_one_or_none()

    if team is None:
        # Need to create franchise first
        franchise_name = team_name or team_abbrev
        franchise = Franchise(
            name=franchise_name,
            founded_year=1946,  # Default
        )
        session.add(franchise)
        await session.flush()

        team = Team(
            name=team_name or team_abbrev,
            abbreviation=team_abbrev,
            founded_year=1946,
            franchise_id=franchise.franchise_id,
            is_active=True,
        )
        session.add(team)
        await session.flush()

    _team_cache[team_abbrev] = team.team_id
    return team.team_id


async def get_or_create_player(
    session: AsyncSession,
    slug: str,
    name: str | None = None,
) -> int:
    """Get or create a player by slug.

    Args:
        session: Database session.
        slug: Player slug (e.g., 'jamesle01').
        name: Optional player name for new records.

    Returns:
        The player_id.
    """
    if slug in _player_cache:
        return _player_cache[slug]

    query = select(Player).where(Player.slug == slug)
    result = await session.execute(query)
    player = result.scalar_one_or_none()

    if player is None:
        # Parse name if provided
        first_name = "Unknown"
        last_name = "Player"
        if name:
            parts = name.split()
            if len(parts) >= 2:
                first_name = parts[0]
                last_name = " ".join(parts[1:])
            elif parts:
                last_name = parts[0]

        player = Player(
            slug=slug,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )
        session.add(player)
        await session.flush()

    _player_cache[slug] = player.player_id
    return player.player_id


async def get_or_create_game(
    session: AsyncSession,
    game_date: date,
    home_team_id: int,
    away_team_id: int,
    season_id: int,
    home_score: int | None = None,
    away_score: int | None = None,
) -> int:
    """Get or create a game by date and teams.

    Args:
        session: Database session.
        game_date: Date of the game.
        home_team_id: Home team's ID.
        away_team_id: Away team's ID.
        season_id: Season ID.
        home_score: Optional home team score.
        away_score: Optional away team score.

    Returns:
        The game_id.
    """
    query = (
        select(Game)
        .where(Game.game_date == game_date)
        .where(Game.home_team_id == home_team_id)
        .where(Game.away_team_id == away_team_id)
    )
    result = await session.execute(query)
    game = result.scalar_one_or_none()

    if game is None:
        game = Game(
            season_id=season_id,
            game_date=game_date,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            home_score=home_score,
            away_score=away_score,
            season_type="REGULAR",
        )
        session.add(game)
        await session.flush()
    elif home_score is not None and game.home_score is None:
        # Update scores if we have them now
        game.home_score = home_score
        game.away_score = away_score
        await session.flush()

    return game.game_id


async def get_or_create_box_score(
    session: AsyncSession,
    game_id: int,
    team_id: int,
    opponent_team_id: int,
    location: Location,
    outcome: Outcome,
    stats: dict[str, Any] | None = None,
) -> int:
    """Get or create a team box score for a game.

    Args:
        session: Database session.
        game_id: Game ID.
        team_id: Team ID.
        opponent_team_id: Opponent team ID.
        location: HOME or AWAY.
        outcome: WIN or LOSS.
        stats: Optional team stats dictionary.

    Returns:
        The box_id.
    """
    query = (
        select(BoxScore)
        .where(BoxScore.game_id == game_id)
        .where(BoxScore.team_id == team_id)
    )
    result = await session.execute(query)
    box = result.scalar_one_or_none()

    if box is None:
        box = BoxScore(
            game_id=game_id,
            team_id=team_id,
            opponent_team_id=opponent_team_id,
            location=location,
            outcome=outcome,
        )
        if stats:
            box.made_fg = stats.get("made_field_goals", 0)
            box.attempted_fg = stats.get("attempted_field_goals", 0)
            box.made_3pt = stats.get("made_three_point_field_goals", 0)
            box.attempted_3pt = stats.get("attempted_three_point_field_goals", 0)
            box.made_ft = stats.get("made_free_throws", 0)
            box.attempted_ft = stats.get("attempted_free_throws", 0)
            box.offensive_rebounds = stats.get("offensive_rebounds", 0)
            box.defensive_rebounds = stats.get("defensive_rebounds", 0)
            box.assists = stats.get("assists", 0)
            box.steals = stats.get("steals", 0)
            box.blocks = stats.get("blocks", 0)
            box.turnovers = stats.get("turnovers", 0)
            box.personal_fouls = stats.get("personal_fouls", 0)
            box.points_scored = stats.get("points", 0)

        session.add(box)
        await session.flush()

    return box.box_id


async def upsert_player_box_score(
    session: AsyncSession,
    player_id: int,
    box_id: int,
    game_id: int,
    team_id: int,
    player_box: "PlayerBoxScore",
) -> None:
    """Insert or update a player box score.

    Args:
        session: Database session.
        player_id: Player ID.
        box_id: Team box score ID.
        game_id: Game ID.
        team_id: Team ID.
        player_box: PlayerBoxScore instance to persist.
    """
    # Check if exists
    query = (
        select(PlayerBoxScore)
        .where(PlayerBoxScore.player_id == player_id)
        .where(PlayerBoxScore.box_id == box_id)
    )
    result = await session.execute(query)
    existing = result.scalar_one_or_none()

    if existing is None:
        player_box.player_id = player_id
        player_box.box_id = box_id
        player_box.game_id = game_id
        player_box.team_id = team_id
        session.add(player_box)
    # If exists, we skip (no update needed for historical data)


async def upsert_player_season(
    session: AsyncSession,
    player_season: "PlayerSeason",
) -> None:
    """Insert or update player season totals.

    Args:
        session: Database session.
        player_season: PlayerSeason instance.
    """
    query = (
        select(PlayerSeason)
        .where(PlayerSeason.player_id == player_season.player_id)
        .where(PlayerSeason.season_id == player_season.season_id)
        .where(PlayerSeason.season_type == player_season.season_type)
    )
    result = await session.execute(query)
    existing = result.scalar_one_or_none()

    if existing is None:
        session.add(player_season)
    else:
        # Update with new values
        existing.games_played = player_season.games_played
        existing.games_started = player_season.games_started
        existing.minutes_played = player_season.minutes_played
        existing.made_fg = player_season.made_fg
        existing.attempted_fg = player_season.attempted_fg
        existing.made_3pt = player_season.made_3pt
        existing.attempted_3pt = player_season.attempted_3pt
        existing.made_ft = player_season.made_ft
        existing.attempted_ft = player_season.attempted_ft
        existing.offensive_rebounds = player_season.offensive_rebounds
        existing.defensive_rebounds = player_season.defensive_rebounds
        existing.total_rebounds = player_season.total_rebounds
        existing.assists = player_season.assists
        existing.steals = player_season.steals
        existing.blocks = player_season.blocks
        existing.turnovers = player_season.turnovers
        existing.personal_fouls = player_season.personal_fouls
        existing.points_scored = player_season.points_scored


async def upsert_player_season_advanced(
    session: AsyncSession,
    player_advanced: "PlayerSeasonAdvanced",
) -> None:
    """Insert or update player advanced season stats.

    Args:
        session: Database session.
        player_advanced: PlayerSeasonAdvanced instance.
    """
    query = (
        select(PlayerSeasonAdvanced)
        .where(PlayerSeasonAdvanced.player_id == player_advanced.player_id)
        .where(PlayerSeasonAdvanced.season_id == player_advanced.season_id)
        .where(PlayerSeasonAdvanced.season_type == player_advanced.season_type)
    )
    result = await session.execute(query)
    existing = result.scalar_one_or_none()

    if existing is None:
        session.add(player_advanced)
    else:
        # Update with new values
        existing.games_played = player_advanced.games_played
        existing.minutes_played = player_advanced.minutes_played
        existing.player_efficiency_rating = player_advanced.player_efficiency_rating
        existing.true_shooting_percentage = player_advanced.true_shooting_percentage
        existing.effective_fg_percentage = player_advanced.effective_fg_percentage
        existing.usage_percentage = player_advanced.usage_percentage
        existing.box_plus_minus = player_advanced.box_plus_minus
        existing.value_over_replacement_player = (
            player_advanced.value_over_replacement_player
        )
        existing.win_shares = player_advanced.win_shares
        existing.win_shares_per_48 = player_advanced.win_shares_per_48


async def upsert_team_season(
    session: AsyncSession,
    team_season: "TeamSeason",
) -> None:
    """Insert or update team season standings.

    Args:
        session: Database session.
        team_season: TeamSeason instance.
    """
    query = (
        select(TeamSeason)
        .where(TeamSeason.team_id == team_season.team_id)
        .where(TeamSeason.season_id == team_season.season_id)
        .where(TeamSeason.season_type == team_season.season_type)
    )
    result = await session.execute(query)
    existing = result.scalar_one_or_none()

    if existing is None:
        session.add(team_season)
    else:
        # Update standings
        existing.wins = team_season.wins
        existing.losses = team_season.losses
        existing.games_played = team_season.games_played
        existing.points_per_game = team_season.points_per_game
        existing.points_allowed_per_game = team_season.points_allowed_per_game
