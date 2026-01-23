"""Service layer for draft-related business logic."""

import duckdb
from app.db.queries import drafts as draft_queries


class DraftService:
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def list_drafts(self) -> list[dict]:
        rows = self.conn.execute(draft_queries.LIST_DRAFTS).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row, strict=False)) for row in rows]

    def get_draft_by_year(self, year: int) -> dict | None:
        result = self.conn.execute(draft_queries.GET_DRAFT_BY_YEAR, [year]).fetchone()
        if not result:
            return None

        columns = [desc[0] for desc in self.conn.description]
        draft = dict(zip(columns, result, strict=False))

        picks_rows = self.conn.execute(
            draft_queries.GET_DRAFT_PICKS, [draft["draft_id"]]
        ).fetchall()
        picks_columns = [desc[0] for desc in self.conn.description]
        draft["picks"] = [
            dict(zip(picks_columns, row, strict=False)) for row in picks_rows
        ]

        return draft
