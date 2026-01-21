"""Celery tasks for search index management."""

import asyncio

import structlog

from app.celery_app import celery_app
from app.db.session import async_session_factory
from app.search.indexer import SearchIndexer

logger = structlog.get_logger(__name__)


def run_async(coro):
    """Helper to run async code in sync Celery tasks."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.search.tasks.setup_search_indices")
def setup_search_indices():
    """Create and configure all Meilisearch indices.

    Should be called during initial setup or after Meilisearch reset.
    """
    logger.info("Setting up search indices")

    try:
        indexer = SearchIndexer()
        indexer.setup_indices()
        logger.info("Search indices configured successfully")
    except Exception as e:
        logger.exception("Failed to set up search indices", error=str(e))
        raise


@celery_app.task(name="app.search.tasks.reindex_all")
def reindex_all():
    """Reindex all data from the database.

    This is a heavy operation that rebuilds all search indices.
    """
    logger.info("Starting full reindex")
    run_async(_reindex_all_async())
    logger.info("Full reindex completed")


async def _reindex_all_async():
    """Async implementation of full reindex."""
    indexer = SearchIndexer()

    # Ensure indices are configured
    indexer.setup_indices()

    async with async_session_factory() as session:
        # Index players
        player_count = await indexer.index_players(session)
        logger.info("Indexed players", count=player_count)

        # Index teams
        team_count = await indexer.index_teams(session)
        logger.info("Indexed teams", count=team_count)

        # Index games
        game_count = await indexer.index_games(session)
        logger.info("Indexed games", count=game_count)


@celery_app.task(name="app.search.tasks.reindex_players")
def reindex_players():
    """Reindex all players."""
    logger.info("Reindexing players")
    run_async(_reindex_players_async())
    logger.info("Player reindex completed")


async def _reindex_players_async():
    """Async implementation of player reindex."""
    indexer = SearchIndexer()
    async with async_session_factory() as session:
        count = await indexer.index_players(session)
        logger.info("Indexed players", count=count)


@celery_app.task(name="app.search.tasks.reindex_teams")
def reindex_teams():
    """Reindex all teams."""
    logger.info("Reindexing teams")
    run_async(_reindex_teams_async())
    logger.info("Team reindex completed")


async def _reindex_teams_async():
    """Async implementation of team reindex."""
    indexer = SearchIndexer()
    async with async_session_factory() as session:
        count = await indexer.index_teams(session)
        logger.info("Indexed teams", count=count)


@celery_app.task(name="app.search.tasks.reindex_games")
def reindex_games(season_year: int | None = None):
    """Reindex games, optionally for a specific season.

    Args:
        season_year: Optional season to reindex.
    """
    logger.info("Reindexing games", season_year=season_year)
    run_async(_reindex_games_async(season_year))
    logger.info("Game reindex completed")


async def _reindex_games_async(season_year: int | None = None):
    """Async implementation of game reindex."""
    indexer = SearchIndexer()
    async with async_session_factory() as session:
        count = await indexer.index_games(session, season_year=season_year)
        logger.info("Indexed games", count=count)
