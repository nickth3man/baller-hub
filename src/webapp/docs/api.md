# API Reference (Webapp)

Base path: `/api/v1`

## Players

- `GET /players`
  - Query: `page`, `per_page`, `is_active`, `position`, `search`, `season`, `team`
- `GET /players/{slug}`
- `GET /players/{slug}/career-stats`
- `GET /players/{slug}/career`
- `GET /players/{slug}/game-log/{season_year}?season_type=REGULAR|PLAYOFF`
- `GET /players/{slug}/splits/{season_year}`

## Teams

- `GET /teams`
  - Query: `is_active`, `conference`, `division`
- `GET /teams/{abbrev}`
- `GET /teams/{abbrev}/roster/{season_year}`
- `GET /teams/{abbrev}/schedule/{season_year}`
- `GET /teams/{abbrev}/stats/{season_year}`
- `GET /teams/{abbrev}/history`

## Games

- `GET /games`
  - Query: `startDate`, `endDate`, `team`, `season_year`, `season_type`, `page`, `per_page`
- `GET /games/today`
- `GET /games/{id}`
- `GET /games/{id}/box-score`
- `GET /games/{id}/play-by-play`

## Seasons

- `GET /seasons`
- `GET /seasons/{year}`
- `GET /seasons/{year}/schedule?month={1-12}`
- `GET /seasons/{year}/leaders?category=points|rebounds|assists|steals|blocks&per_game=true|false&limit=10`

## Standings

- `GET /standings/{year}?view=conference|league`
- `GET /standings/{year}/by-date/{YYYY-MM-DD}`
- `GET /standings/{year}/expanded`
- `GET /standings/{year}/playoff-bracket`

## Search

- `GET /search?q={query}`
- `GET /search/autocomplete?q={query}`
- `GET /search/players?q={query}&position=...&team_abbrev=...`
- `GET /search/games?team1=...&team2=...&date_from=YYYY-MM-DD&date_to=YYYY-MM-DD`
