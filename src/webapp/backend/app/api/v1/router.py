"""API v1 router configuration.

Aggregates all endpoint routers for version 1 of the API.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import games, players, search, seasons, standings, teams

api_router = APIRouter()

api_router.include_router(players.router, prefix="/players", tags=["Players"])
api_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_router.include_router(games.router, prefix="/games", tags=["Games"])
api_router.include_router(seasons.router, prefix="/seasons", tags=["Seasons"])
api_router.include_router(standings.router, prefix="/standings", tags=["Standings"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
