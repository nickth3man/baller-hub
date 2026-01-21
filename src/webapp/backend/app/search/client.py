"""Meilisearch client configuration."""

from functools import lru_cache

import meilisearch
from meilisearch import Client

from app.core.config import settings


@lru_cache
def get_meilisearch_client() -> Client:
    """Get a configured Meilisearch client.

    Returns:
        Configured Meilisearch Client instance.
    """
    return meilisearch.Client(
        settings.meilisearch_url,
        settings.meilisearch_api_key or None,
    )


# Index names
PLAYERS_INDEX = "players"
TEAMS_INDEX = "teams"
GAMES_INDEX = "games"

# Index configurations
INDEX_CONFIGS = {
    PLAYERS_INDEX: {
        "primaryKey": "player_id",
        "searchableAttributes": [
            "full_name",
            "first_name",
            "last_name",
            "college",
            "slug",
        ],
        "filterableAttributes": [
            "position",
            "is_active",
            "draft_year",
            "debut_year",
        ],
        "sortableAttributes": [
            "last_name",
            "first_name",
            "debut_year",
        ],
        "displayedAttributes": [
            "player_id",
            "slug",
            "full_name",
            "first_name",
            "last_name",
            "position",
            "is_active",
            "college",
            "draft_year",
        ],
        "rankingRules": [
            "words",
            "typo",
            "proximity",
            "attribute",
            "sort",
            "exactness",
            "is_active:desc",  # Prioritize active players
        ],
    },
    TEAMS_INDEX: {
        "primaryKey": "team_id",
        "searchableAttributes": [
            "name",
            "city",
            "abbreviation",
            "full_name",
        ],
        "filterableAttributes": [
            "is_active",
            "conference",
            "division",
        ],
        "sortableAttributes": [
            "name",
            "city",
        ],
        "displayedAttributes": [
            "team_id",
            "name",
            "city",
            "abbreviation",
            "full_name",
            "is_active",
            "conference",
            "division",
        ],
    },
    GAMES_INDEX: {
        "primaryKey": "game_id",
        "searchableAttributes": [
            "home_team_name",
            "away_team_name",
            "matchup",
        ],
        "filterableAttributes": [
            "season_year",
            "season_type",
            "home_team_id",
            "away_team_id",
            "game_date",
        ],
        "sortableAttributes": [
            "game_date",
        ],
        "displayedAttributes": [
            "game_id",
            "game_date",
            "matchup",
            "home_team_id",
            "home_team_name",
            "away_team_id",
            "away_team_name",
            "home_score",
            "away_score",
            "is_final",
        ],
    },
}
