"""Search package for Meilisearch integration."""

from app.search.indexer import SearchIndexer
from app.search.client import get_meilisearch_client

__all__ = [
    "SearchIndexer",
    "get_meilisearch_client",
]
