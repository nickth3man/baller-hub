"""Ingestion package for scraper integration."""

from app.ingestion.mappers import (
    map_player_advanced_totals,
    map_player_box_score,
    map_player_season_totals,
    map_schedule_game,
    map_standings,
)
try:
    from app.ingestion.scraper_service import ScraperService
except ModuleNotFoundError:  # pragma: no cover - optional during isolated tests
    ScraperService = None

__all__ = [
    "ScraperService",
    "map_player_box_score",
    "map_player_season_totals",
    "map_player_advanced_totals",
    "map_schedule_game",
    "map_standings",
]
