"""Database connection management module.

This module provides functions for managing DuckDB database connections
using a singleton pattern for read-only access.
"""

from contextlib import contextmanager

import duckdb

from app.core.config import settings

_conn: duckdb.DuckDBPyConnection | None = None


def get_connection() -> duckdb.DuckDBPyConnection:
    """Get or create a singleton DuckDB connection.

    Returns:
        duckdb.DuckDBPyConnection: Read-only database connection.
    """
    global _conn  # noqa: PLW0603
    if _conn is None:
        _conn = duckdb.connect(str(settings.duckdb_path), read_only=True)
    return _conn


def close_connection():
    """Close the active database connection.

    Resets the singleton connection to None so a new connection
    can be created on next call to get_connection().
    """
    global _conn  # noqa: PLW0603
    if _conn:
        _conn.close()
        _conn = None


@contextmanager
def session():
    """Context manager for database sessions.

    Provides a context that yields a database connection and ensures
    proper cleanup after use.

    Yields:
        duckdb.DuckDBPyConnection: Database connection.
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        pass
