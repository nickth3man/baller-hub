"""Celery tasks for data ingestion from the scraper.

These tasks run periodically or on-demand to fetch data from
basketball-reference.com and persist it to our database.
"""

import asyncio
from datetime import date, timedelta
from typing import Any

import structlog
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.db.session import async_session_factory
from app.ingestion.scraper_service import ScraperService

logger = structlog.get_logger(__name__)


def run_async(coro):
    """Helper to run async code in sync Celery tasks."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="app.ingestion.tasks.ingest_daily_box_scores",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def ingest_daily_box_scores(self, target_date: str | None = None):
    """Ingest all player and team box scores for a given date.

    Args:
        target_date: Date string in YYYY-MM-DD format. Defaults to yesterday.
    """
    if target_date:
        dt = date.fromisoformat(target_date)
    else:
        # Default to yesterday (games from last night)
        dt = date.today() - timedelta(days=1)

    logger.info("Starting daily box score ingestion", date=dt.isoformat())

    try:
        run_async(_ingest_daily_box_scores_async(dt))
        logger.info("Completed daily box score ingestion", date=dt.isoformat())
    except Exception as exc:
        logger.exception("Failed to ingest daily box scores", date=dt.isoformat())
        raise self.retry(exc=exc)


async def _ingest_daily_box_scores_async(dt: date):
    """Async implementation of daily box score ingestion."""
    scraper = ScraperService()

    # Fetch player box scores
    player_box_scores = await scraper.get_player_box_scores(
        day=dt.day, month=dt.month, year=dt.year
    )
    logger.info("Fetched player box scores", count=len(player_box_scores))

    # Fetch team box scores
    team_box_scores = await scraper.get_team_box_scores(
        day=dt.day, month=dt.month, year=dt.year
    )
    logger.info("Fetched team box scores", count=len(team_box_scores))

    # TODO: Persist to database
    # This requires looking up or creating:
    # 1. Players (by slug)
    # 2. Teams (by abbreviation)
    # 3. Games (by date + teams)
    # 4. BoxScores (team-level)
    # 5. PlayerBoxScores (player-level)

    async with async_session_factory() as session:
        await _persist_box_scores(session, dt, player_box_scores, team_box_scores)
        await session.commit()


async def _persist_box_scores(
    session: AsyncSession,
    dt: date,
    player_box_scores: list[dict[str, Any]],
    team_box_scores: list[dict[str, Any]],
):
    """Persist box scores to the database.

    Flow:
    1. Determine season from date
    2. Group team box scores by game (home vs away)
    3. Create/lookup teams, create games, create team box scores
    4. For each player box score, lookup player, create player box score
    """
    from app.ingestion.mappers import (
        _extract_player_slug,
        map_player_box_score,
    )
    from app.ingestion.repositories import (
        clear_caches,
        get_or_create_box_score,
        get_or_create_game,
        get_or_create_player,
        get_or_create_season,
        get_or_create_team,
        upsert_player_box_score,
    )
    from app.models.game import Location, Outcome

    await clear_caches()

    # Determine season (Oct-June = current year season, else previous)
    season_end_year = dt.year if dt.month >= 10 else dt.year
    if dt.month < 7:
        season_end_year = dt.year
    else:
        season_end_year = dt.year + 1

    season_id = await get_or_create_season(session, season_end_year)
    logger.info("Using season", season_id=season_id, season_end_year=season_end_year)

    # Process team box scores first to create games and team box scores
    # Team box scores come in pairs (home and away for each game)
    games_created: dict[tuple[int, int], tuple[int, dict[int, int]]] = {}

    for tbs in team_box_scores:
        team_abbrev = tbs.get("team")
        if hasattr(team_abbrev, "value"):
            team_abbrev = team_abbrev.value
        if not team_abbrev:
            continue

        opponent_abbrev = tbs.get("opponent")
        if hasattr(opponent_abbrev, "value"):
            opponent_abbrev = opponent_abbrev.value

        # Get or create teams
        team_id = await get_or_create_team(session, str(team_abbrev))
        opponent_id = await get_or_create_team(session, str(opponent_abbrev))

        # Determine location and outcome
        outcome_val = tbs.get("outcome")
        if hasattr(outcome_val, "value"):
            outcome_val = outcome_val.value
        outcome = Outcome.WIN if outcome_val == "WIN" else Outcome.LOSS

        location_val = tbs.get("location")
        if hasattr(location_val, "value"):
            location_val = location_val.value
        location = Location.HOME if location_val == "HOME" else Location.AWAY

        # Determine home/away for game creation
        if location == Location.HOME:
            home_team_id = team_id
            away_team_id = opponent_id
        else:
            home_team_id = opponent_id
            away_team_id = team_id

        # Use consistent key ordering for game lookup
        game_key = (min(home_team_id, away_team_id), max(home_team_id, away_team_id))

        # Create game if not already created for this pair
        if game_key not in games_created:
            home_score = tbs.get("points") if location == Location.HOME else None
            away_score = tbs.get("points") if location == Location.AWAY else None

            game_id = await get_or_create_game(
                session,
                game_date=dt,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                season_id=season_id,
                home_score=home_score,
                away_score=away_score,
            )
            games_created[game_key] = (game_id, {})

        game_id, box_id_map = games_created[game_key]

        # Create team box score
        box_id = await get_or_create_box_score(
            session,
            game_id=game_id,
            team_id=team_id,
            opponent_team_id=opponent_id,
            location=location,
            outcome=outcome,
            stats=tbs,
        )
        box_id_map[team_id] = box_id
        games_created[game_key] = (game_id, box_id_map)

    logger.info("Created games and team box scores", games_count=len(games_created))

    # Now process player box scores
    player_count = 0
    for pbs in player_box_scores:
        team_abbrev = pbs.get("team")
        if hasattr(team_abbrev, "value"):
            team_abbrev = team_abbrev.value
        if not team_abbrev:
            continue

        opponent_abbrev = pbs.get("opponent")
        if hasattr(opponent_abbrev, "value"):
            opponent_abbrev = opponent_abbrev.value

        team_id = await get_or_create_team(session, str(team_abbrev))
        opponent_id = await get_or_create_team(session, str(opponent_abbrev))

        # Get player
        player_slug = pbs.get("slug") or _extract_player_slug(pbs.get("name"))
        player_name = pbs.get("name")
        player_id = await get_or_create_player(session, player_slug, player_name)

        # Find the game and box score for this player
        game_key = (min(team_id, opponent_id), max(team_id, opponent_id))
        if game_key not in games_created:
            logger.warning(
                "No game found for player box score",
                player=player_name,
                team=team_abbrev,
            )
            continue

        game_id, box_id_map = games_created[game_key]
        if team_id not in box_id_map:
            logger.warning(
                "No box score found for team",
                team=team_abbrev,
                game_id=game_id,
            )
            continue

        box_id = box_id_map[team_id]

        # Create player box score
        player_box = map_player_box_score(
            raw=pbs,
            player_id=player_id,
            box_id=box_id,
            game_id=game_id,
            team_id=team_id,
        )
        await upsert_player_box_score(
            session, player_id, box_id, game_id, team_id, player_box
        )
        player_count += 1

    logger.info(
        "Persisted box scores",
        date=dt.isoformat(),
        games=len(games_created),
        players=player_count,
    )


@celery_app.task(
    name="app.ingestion.tasks.update_standings",
    bind=True,
    max_retries=3,
)
def update_standings(self, season_end_year: int | None = None):
    """Update standings for the current or specified season.

    Args:
        season_end_year: Year the season ends. Defaults to current season.
    """
    if season_end_year is None:
        today = date.today()
        # NBA season runs Oct-June, so if we're past June, use next year
        season_end_year = today.year if today.month >= 10 else today.year

    logger.info("Updating standings", season_end_year=season_end_year)

    try:
        run_async(_update_standings_async(season_end_year))
        logger.info("Completed standings update", season_end_year=season_end_year)
    except Exception as exc:
        logger.exception("Failed to update standings")
        raise self.retry(exc=exc)


async def _update_standings_async(season_end_year: int):
    """Async implementation of standings update."""
    scraper = ScraperService()
    standings = await scraper.get_standings(season_end_year)

    if not standings:
        logger.warning("No standings data returned", season_end_year=season_end_year)
        return

    logger.info("Fetched standings data", season_end_year=season_end_year)

    async with async_session_factory() as session:
        await _persist_standings(session, season_end_year, standings)
        await session.commit()


async def _persist_standings(
    session: AsyncSession,
    season_end_year: int,
    standings: dict[str, Any],
):
    """Persist standings to the database.

    Standings data comes as a dict with division/conference keys.
    Each entry contains team records.
    """
    from app.ingestion.mappers import map_standings
    from app.ingestion.repositories import (
        clear_caches,
        get_or_create_season,
        get_or_create_team,
        upsert_team_season,
    )

    await clear_caches()
    season_id = await get_or_create_season(session, season_end_year)

    teams_processed = 0

    # Standings structure: {"EASTERN": [...], "WESTERN": [...]} or by division
    for conference_or_division, team_records in standings.items():
        if not isinstance(team_records, list):
            continue

        for record in team_records:
            team_name = record.get("team")
            if hasattr(team_name, "value"):
                team_name = team_name.value
            if not team_name:
                continue

            # Get team abbreviation from the team enum or string
            team_abbrev = str(team_name)
            # If it's a full team name, try to extract abbreviation
            # For now, use the value as-is since scraper returns Team enums
            team_id = await get_or_create_team(session, team_abbrev, team_name)

            team_season = map_standings(
                raw=record,
                team_id=team_id,
                season_id=season_id,
            )
            await upsert_team_season(session, team_season)
            teams_processed += 1

    logger.info(
        "Persisted standings",
        season_end_year=season_end_year,
        teams=teams_processed,
    )


@celery_app.task(
    name="app.ingestion.tasks.sync_season_data",
    bind=True,
    max_retries=2,
)
def sync_season_data(self, season_end_year: int | None = None):
    """Full sync of season data including schedule, player totals, and advanced stats.

    This is a heavy operation meant to run weekly or on-demand.

    Args:
        season_end_year: Year the season ends. Defaults to current season.
    """
    if season_end_year is None:
        today = date.today()
        season_end_year = today.year if today.month >= 10 else today.year

    logger.info("Starting full season sync", season_end_year=season_end_year)

    try:
        run_async(_sync_season_data_async(season_end_year))
        logger.info("Completed full season sync", season_end_year=season_end_year)
    except Exception as exc:
        logger.exception("Failed full season sync")
        raise self.retry(exc=exc)


async def _sync_season_data_async(season_end_year: int):
    """Async implementation of full season sync."""
    scraper = ScraperService()

    # Fetch schedule
    schedule = await scraper.get_season_schedule(season_end_year)
    logger.info("Fetched schedule", count=len(schedule))

    # Fetch player season totals
    player_totals = await scraper.get_players_season_totals(season_end_year)
    logger.info("Fetched player totals", count=len(player_totals))

    # Fetch advanced stats
    advanced_totals = await scraper.get_players_advanced_season_totals(
        season_end_year, include_combined_values=True
    )
    logger.info("Fetched advanced totals", count=len(advanced_totals))

    # Fetch standings
    standings = await scraper.get_standings(season_end_year)
    logger.info("Fetched standings")

    async with async_session_factory() as session:
        await _persist_season_data(
            session,
            season_end_year,
            schedule,
            player_totals,
            advanced_totals,
            standings,
        )
        await session.commit()


async def _persist_season_data(
    session: AsyncSession,
    season_end_year: int,
    schedule: list[dict[str, Any]],
    player_totals: list[dict[str, Any]],
    advanced_totals: list[dict[str, Any]],
    standings: dict[str, Any],
):
    """Persist all season data to the database.

    This is the full sync that handles:
    1. Schedule (games)
    2. Player season totals
    3. Player advanced stats
    4. Standings
    """
    from app.ingestion.mappers import (
        _extract_player_slug,
        map_player_advanced_totals,
        map_player_season_totals,
        map_schedule_game,
    )
    from app.ingestion.repositories import (
        clear_caches,
        get_or_create_game,
        get_or_create_player,
        get_or_create_season,
        get_or_create_team,
        upsert_player_season,
        upsert_player_season_advanced,
    )

    await clear_caches()
    season_id = await get_or_create_season(session, season_end_year)

    # 1. Process schedule to create games
    games_created = 0
    for game_data in schedule:
        home_team = game_data.get("home_team")
        away_team = game_data.get("away_team")

        if hasattr(home_team, "value"):
            home_team = home_team.value
        if hasattr(away_team, "value"):
            away_team = away_team.value

        if not home_team or not away_team:
            continue

        home_team_id = await get_or_create_team(session, str(home_team))
        away_team_id = await get_or_create_team(session, str(away_team))

        # Parse date from start_time
        start_time = game_data.get("start_time")
        if start_time is None:
            continue

        from datetime import datetime

        if isinstance(start_time, datetime):
            game_date = start_time.date()
        elif isinstance(start_time, date):
            game_date = start_time
        else:
            continue

        await get_or_create_game(
            session,
            game_date=game_date,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            season_id=season_id,
            home_score=game_data.get("home_team_score"),
            away_score=game_data.get("away_team_score"),
        )
        games_created += 1

    logger.info("Persisted schedule", games=games_created)

    # 2. Process player season totals
    players_processed = 0
    def _select_player_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        selected: dict[str, dict[str, Any]] = {}
        for record in records:
            player_slug = record.get("slug") or _extract_player_slug(record.get("name"))
            if not player_slug:
                continue
            if record.get("is_combined_totals", False):
                selected[player_slug] = record
            else:
                selected.setdefault(player_slug, record)
        return list(selected.values())

    for pt in _select_player_records(player_totals):
        player_slug = pt.get("slug") or _extract_player_slug(pt.get("name"))
        player_name = pt.get("name")
        player_id = await get_or_create_player(session, player_slug, player_name)

        # Get team if available
        team_abbrev = pt.get("team")
        if hasattr(team_abbrev, "value"):
            team_abbrev = team_abbrev.value
        team_id = None
        if team_abbrev:
            team_id = await get_or_create_team(session, str(team_abbrev))

        player_season = map_player_season_totals(
            raw=pt,
            player_id=player_id,
            season_id=season_id,
            team_id=team_id,
        )
        await upsert_player_season(session, player_season)
        players_processed += 1

    logger.info("Persisted player totals", players=players_processed)

    # 3. Process advanced stats
    advanced_processed = 0
    for at in _select_player_records(advanced_totals):
        player_slug = at.get("slug") or _extract_player_slug(at.get("name"))
        player_name = at.get("name")
        player_id = await get_or_create_player(session, player_slug, player_name)

        team_abbrev = at.get("team")
        if hasattr(team_abbrev, "value"):
            team_abbrev = team_abbrev.value
        team_id = None
        if team_abbrev:
            team_id = await get_or_create_team(session, str(team_abbrev))

        player_advanced = map_player_advanced_totals(
            raw=at,
            player_id=player_id,
            season_id=season_id,
            team_id=team_id,
        )
        await upsert_player_season_advanced(session, player_advanced)
        advanced_processed += 1

    logger.info("Persisted advanced stats", players=advanced_processed)

    # 4. Persist standings
    await _persist_standings(session, season_end_year, standings)

    logger.info(
        "Completed full season sync",
        season_end_year=season_end_year,
        games=games_created,
        player_totals=players_processed,
        advanced_stats=advanced_processed,
    )


@celery_app.task(name="app.ingestion.tasks.ingest_player_game_log")
def ingest_player_game_log(player_identifier: str, season_end_year: int):
    """Ingest a single player's game log for a season.

    Args:
        player_identifier: Player ID (e.g., 'jamesle01').
        season_end_year: Year the season ends.
    """
    logger.info(
        "Ingesting player game log",
        player_identifier=player_identifier,
        season_end_year=season_end_year,
    )

    run_async(_ingest_player_game_log_async(player_identifier, season_end_year))


async def _ingest_player_game_log_async(player_identifier: str, season_end_year: int):
    """Async implementation of player game log ingestion."""
    scraper = ScraperService()

    game_log = await scraper.get_regular_season_player_box_scores(
        player_identifier=player_identifier,
        season_end_year=season_end_year,
        include_inactive_games=True,
    )

    logger.info(
        "Fetched player game log",
        player_identifier=player_identifier,
        count=len(game_log),
    )

    async with async_session_factory() as session:
        # TODO: Persist game log
        logger.info(
            "Would persist player game log",
            player_identifier=player_identifier,
            count=len(game_log),
        )
        await session.commit()


@celery_app.task(name="app.ingestion.tasks.ingest_play_by_play")
def ingest_play_by_play(home_team: str, day: int, month: int, year: int):
    """Ingest play-by-play data for a single game.

    Args:
        home_team: Team abbreviation for home team.
        day: Day of the month.
        month: Month number.
        year: 4-digit year.
    """
    logger.info(
        "Ingesting play-by-play",
        home_team=home_team,
        date=f"{year}-{month:02d}-{day:02d}",
    )

    run_async(_ingest_play_by_play_async(home_team, day, month, year))


async def _ingest_play_by_play_async(home_team: str, day: int, month: int, year: int):
    """Async implementation of play-by-play ingestion."""
    scraper = ScraperService()

    plays = await scraper.get_play_by_play(
        home_team=home_team, day=day, month=month, year=year
    )

    logger.info("Fetched play-by-play", count=len(plays))

    async with async_session_factory() as session:
        # TODO: Persist plays
        logger.info("Would persist play-by-play", count=len(plays))
        await session.commit()
