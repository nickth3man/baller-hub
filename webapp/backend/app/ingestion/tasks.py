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

    This is a stub that will be implemented when we have the full
    lookup/upsert logic for players, teams, and games.
    """
    # For now, just log what we would persist
    logger.info(
        "Would persist box scores",
        date=dt.isoformat(),
        player_count=len(player_box_scores),
        team_count=len(team_box_scores),
    )
    # TODO: Implement actual persistence


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
    """Persist standings to the database."""
    logger.info(
        "Would persist standings",
        season_end_year=season_end_year,
        divisions=list(standings.keys()) if isinstance(standings, dict) else "N/A",
    )
    # TODO: Implement actual persistence


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
    """Persist all season data to the database."""
    logger.info(
        "Would persist season data",
        season_end_year=season_end_year,
        schedule_count=len(schedule),
        player_totals_count=len(player_totals),
        advanced_totals_count=len(advanced_totals),
    )
    # TODO: Implement actual persistence


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
