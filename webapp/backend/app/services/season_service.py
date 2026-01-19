"""Season service - business logic for season operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.season import Season


class SeasonService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_seasons(self, league: str = "NBA", limit: int = 20):
        query = select(Season).order_by(Season.year.desc()).limit(limit)
        result = await self.session.execute(query)
        seasons = result.scalars().all()
        return {"items": seasons, "total": len(seasons)}

    async def get_current_season(self):
        query = select(Season).where(Season.is_active == True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_season_by_year(self, year: int):
        query = select(Season).where(Season.year == year)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_season_schedule(self, season_year: int, month: int | None = None):
        raise NotImplementedError("TODO: Implement season schedule retrieval")

    async def get_season_leaders(
        self,
        season_year: int,
        category: str = "points",
        per_game: bool = True,
        limit: int = 10,
    ):
        raise NotImplementedError("TODO: Implement season leaders retrieval")

    async def get_season_player_stats(
        self,
        season_year: int,
        stat_type: str = "totals",
        position: str | None = None,
        min_games: int = 0,
        page: int = 1,
        per_page: int = 50,
        sort_by: str = "points",
        sort_order: str = "desc",
    ):
        raise NotImplementedError("TODO: Implement player stats retrieval")
