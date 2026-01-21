"""Search package for Meilisearch integration."""

from app.search.client import get_meilisearch_client
from app.search.indexer import SearchIndexer

__all__ = [
    "SearchIndexer",
    "get_meilisearch_client",
]
