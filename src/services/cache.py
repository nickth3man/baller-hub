"""Disk-based caching service."""

import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class FileCache:
    """
    Simple URL -> Disk cache with TTL support.

    Caches HTTP responses to disk to avoid redundant network requests.
    Uses SHA256 of the URL as the filename.
    """

    def __init__(self, cache_dir=".cache/bref", default_ttl=timedelta(days=7)):
        """
        Initialize the file cache.

        Args:
            cache_dir (str): Path to the cache directory.
            default_ttl (timedelta): Default time-to-live for cached items.
        """
        self._cache_dir = Path(cache_dir)
        self._default_ttl = default_ttl

        # Ensure cache directory exists
        if not self._cache_dir.exists():
            try:
                self._cache_dir.mkdir(parents=True, exist_ok=True)
            except OSError:
                # If we can't create the cache dir, we just won't cache
                pass

    def _key(self, url):
        """Generate a stable key for a URL."""
        return hashlib.sha256(url.encode()).hexdigest()

    def get(self, url):
        """
        Retrieve content from cache if valid.

        Args:
            url (str): The URL to retrieve.

        Returns:
            bytes or None: Cached content if hit and valid, else None.
        """
        if not self._cache_dir.exists():
            return None

        key = self._key(url)
        path = self._cache_dir / f"{key}.cache"
        meta_path = self._cache_dir / f"{key}.meta"

        if not path.exists() or not meta_path.exists():
            return None

        try:
            meta = json.loads(meta_path.read_text())
            cached_at = datetime.fromisoformat(meta["cached_at"])
            ttl = timedelta(seconds=meta.get("ttl", self._default_ttl.total_seconds()))

            if datetime.now() - cached_at > ttl:
                return None

            return path.read_bytes()
        except (ValueError, OSError, json.JSONDecodeError):
            return None

    def set(self, url, content, ttl=None):
        """
        Save content to cache.

        Args:
            url (str): The URL.
            content (bytes): The content to cache.
            ttl (timedelta, optional): Custom TTL for this item.
        """
        if not self._cache_dir.exists():
            try:
                self._cache_dir.mkdir(parents=True, exist_ok=True)
            except OSError:
                return

        try:
            key = self._key(url)
            path = self._cache_dir / f"{key}.cache"
            meta_path = self._cache_dir / f"{key}.meta"

            path.write_bytes(content)

            meta = {
                "url": url,
                "cached_at": datetime.now().isoformat(),
                "ttl": (ttl or self._default_ttl).total_seconds(),
            }
            meta_path.write_text(json.dumps(meta))
        except OSError:
            # Silently fail on write errors (e.g. disk full)
            pass
