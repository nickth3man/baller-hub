"""Celery tasks for search index management."""

import structlog

from app.celery_app import celery_app
from app.db.connection import session
from app.search.indexer import SearchIndexer

logger = structlog.get_logger(__name__)


def reindex_all():
    """Reindex all data from the database.

    This is a heavy operation that rebuilds all search indices.
    """
    logger.info("Starting full reindex")
    _reindex_all_sync()
    logger.info("Full reindex completed")


def _reindex_all_sync():
    """Sync implementation of full reindex."""
    indexer = SearchIndexer()

    # Ensure indices are configured
    indexer.setup_indices()

    with session() as conn:
        # Index players
        player_count = indexer.index_players(conn)
        logger.info("Indexed players", count=player_count)

        # Index teams
        team_count = indexer.index_teams(conn)
        logger.info("Indexed teams", count=team_count)

        # Index games
        game_count = indexer.index_games(conn)
        logger.info("Indexed games", count=game_count)


@celery_app.task(name="app.search.tasks.reindex_players")
def reindex_players():
    """Reindex all players."""
    logger.info("Reindexing players")
    indexer = SearchIndexer()
    with session() as conn:
        count = indexer.index_players(conn)
        logger.info("Indexed players", count=count)
    logger.info("Player reindex completed")


@celery_app.task(name="app.search.tasks.reindex_teams")
def reindex_teams():
    """Reindex all teams."""
    logger.info("Reindexing teams")
    indexer = SearchIndexer()
    with session() as conn:
        count = indexer.index_teams(conn)
        logger.info("Indexed teams", count=count)
    logger.info("Team reindex completed")


@celery_app.task(name="app.search.tasks.reindex_games")
def reindex_games(season_year: int | None = None):
    """Reindex games, optionally for a specific season.

    Args:
        season_year: Optional season to reindex.
    """
    logger.info("Reindexing games", season_year=season_year)
    indexer = SearchIndexer()
    with session() as conn:
        count = indexer.index_games(conn, season_year=season_year)
        logger.info("Indexed games", count=count)
    logger.info("Game reindex completed")
