"""Standings service - business logic for standings operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import TeamSeason


class StandingsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_standings(self, season_year: int, view: str = "conference"):
        query = (
            select(TeamSeason)
            .where(TeamSeason.season_type == "REGULAR")
            .order_by(TeamSeason.wins.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_standings_as_of_date(self, season_year: int, as_of_date: str):
        raise NotImplementedError("TODO: Implement historical standings")

    async def get_expanded_standings(self, season_year: int):
        raise NotImplementedError("TODO: Implement expanded standings")

    async def get_playoff_bracket(self, season_year: int):
        raise NotImplementedError("TODO: Implement playoff bracket retrieval")
