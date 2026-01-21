"""Search Pydantic schemas."""

from pydantic import BaseModel


class SearchResultPlayer(BaseModel):
    player_id: int
    slug: str
    full_name: str
    name: str | None = None
    position: str | None = None
    years_active: str | None = None
    is_active: bool


class SearchResultTeam(BaseModel):
    team_id: int
    abbreviation: str
    name: str
    city: str | None = None
    is_active: bool


class SearchResultGame(BaseModel):
    game_id: int
    game_date: str
    matchup: str
    score: str | None = None


class SearchResponse(BaseModel):
    query: str
    players: list[SearchResultPlayer]
    teams: list[SearchResultTeam]
    games: list[SearchResultGame]
    total_results: int


class AutocompleteItem(BaseModel):
    type: str
    value: str
    label: str
    url: str


class AutocompleteResponse(BaseModel):
    query: str
    suggestions: list[AutocompleteItem]
