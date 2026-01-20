# API Reference (Reference)

## Endpoints

### Players
- `GET /api/v1/players`
  - Params: `page`, `per_page`, `search`, `position`, `is_active`, `season`, `team`
- `GET /api/v1/players/{slug}`
- `GET /api/v1/players/{slug}/career-stats`
- `GET /api/v1/players/{slug}/career`
- `GET /api/v1/players/{slug}/game-log/{season_year}`

### Teams
- `GET /api/v1/teams`
- `GET /api/v1/teams/{abbrev}`
- `GET /api/v1/teams/{abbrev}/roster/{year}`
- `GET /api/v1/teams/{abbrev}/schedule/{year}`
- `GET /api/v1/teams/{abbrev}/stats/{year}`

### Games
- `GET /api/v1/games`
  - Params: `startDate`, `endDate`, `team`, `season_year`, `season_type`, `isPlayoff`
- `GET /api/v1/games/today`
- `GET /api/v1/games/{id}`
- `GET /api/v1/games/{id}/box-score`
- `GET /api/v1/games/{id}/play-by-play`

### Seasons
- `GET /api/v1/seasons`
- `GET /api/v1/seasons/{year}`
- `GET /api/v1/seasons/{year}/leaders`
- `GET /api/v1/seasons/{year}/player-stats`

### Standings
- `GET /api/v1/standings/{season_year}`
  - Params: `date` (optional)
- `GET /api/v1/standings/{season_year}/playoff-bracket`

## References

| Topic | Location | Anchor |
|-------|----------|--------|
| Implementation spec | `docs/specs/implementation.md` | `5-api-enhancements` |
| Player endpoints | `webapp/backend/app/api/v1/endpoints/players.py` | `router` |
| Game endpoints | `webapp/backend/app/api/v1/endpoints/games.py` | `router` |
