"""Ingestion package for scraper integration."""

from app.ingestion.scraper_service import ScraperService
from app.ingestion.mappers import (
    map_player_box_score,
    map_player_season_totals,
    map_player_advanced_totals,
    map_schedule_game,
    map_standings,
)

__all__ = [
    "ScraperService",
    "map_player_box_score",
    "map_player_season_totals",
    "map_player_advanced_totals",
    "map_schedule_game",
    "map_standings",
]
