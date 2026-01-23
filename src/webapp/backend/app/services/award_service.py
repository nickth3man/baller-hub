"""Service layer for award-related business logic."""

import duckdb

from app.db.queries import awards as award_queries


class AwardService:
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def list_awards(self) -> list[dict]:
        rows = self.conn.execute(award_queries.LIST_AWARDS).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row, strict=False)) for row in rows]

    def get_award(self, award_id: int) -> dict | None:
        result = self.conn.execute(award_queries.GET_AWARD_BY_ID, [award_id]).fetchone()
        if not result:
            return None

        columns = [desc[0] for desc in self.conn.description]
        award = dict(zip(columns, result, strict=False))

        recipients_rows = self.conn.execute(
            award_queries.GET_AWARD_RECIPIENTS, [award_id]
        ).fetchall()
        recipients_columns = [desc[0] for desc in self.conn.description]
        award["recipients"] = [
            dict(zip(recipients_columns, row, strict=False)) for row in recipients_rows
        ]

        return award
