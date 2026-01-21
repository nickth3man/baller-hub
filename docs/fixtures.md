# Fixture Catalog (Reference)

Complete catalog of HTML fixtures used for integration testing.

> **Source of Truth**: This document is derived from [PLAN.md](../PLAN.md).

## Overview

| Metric | Value |
|--------|-------|
| Total Fixtures | ~543 pages |
| Page Types | 50+ |
| Historical Coverage | BAA (1946-1949), ABA (1967-1976), NBA (1949-2025) |
| Location | `tests/integration/files/` |

## Fixture Directory Structure

```
tests/integration/files/
├── allstar/                    # All-Star game pages
├── awards/                     # Award history pages (MVP, DPOY, ROY, etc.)
├── boxscores/                  # Game box scores (flattened: {YYYYMMDD}{TEAM}.html)
│   └── index/                  # Daily box score index pages
├── coaches/                    # Coach profile pages
├── daily_leaders/              # Daily statistical leaders
├── draft/                      # Draft results and combine data
├── executives/                 # Executive/GM pages
├── leaders/                    # Career and active leaders
├── per_game/                   # Per-game league stats
├── per_minute/                 # Per-36-minute league stats
├── per_poss/                   # Per-100-possession league stats
├── play_by_play/               # Play-by-play data (flattened)
├── player_advanced/            # Player advanced stats sub-pages
├── player_game_logs/           # Player game log pages
├── player_playoffs/            # Player playoff game logs
├── player_shooting/            # Player shooting zone data
├── player_splits/              # Player situational splits
├── players/                    # Player profile pages
├── players_advanced_season_totals/  # League-wide advanced stats
├── players_season_totals/      # League-wide season totals
├── playoffs/                   # Playoff bracket and series pages
├── referees/                   # Referee pages
├── rookies/                    # Rookie stats pages
├── schedule/                   # Season and monthly schedules
├── search/                     # Search result pages
├── standings/                  # Division/conference standings
└── team_seasons/               # Team season pages (roster, stats)
```

## Fixture Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Box Scores | `{YYYYMMDD0}{TEAM}.html` | `201801010TOR.html` |
| Play-by-Play | `{YYYYMMDD0}{TEAM}.html` | `201810160GSW.html` |
| Season Totals | `{YYYY}.html` | `2024.html` |
| Schedules | `{YYYY}.html` or `{month}.html` | `2018.html`, `october.html` |
| Player Profiles | `{playerid}.html` | `jamesle01.html` |
| Player Game Logs | `{playerid}_{YYYY}.html` | `jamesle01_2020.html` |
| Draft | `NBA_{YYYY}.html` | `NBA_2024.html` |
| Awards | `{award}.html` | `mvp.html` |

## Fixtures by Phase

### Phase 1: Critical Fixes (8 fixtures)

> Fixes test failures and conftest issues.

| URL Pattern | Fixture Path | Status |
|-------------|--------------|--------|
| `/leagues/NBA_{year}.html` | `standings/{year}.html` | TODO |

### Phase 2: Existing Types - Historical Coverage (180 fixtures)

> Expands coverage for currently implemented page types.

- Season Totals: 30 fixtures (BAA, ABA, NBA sampled years)
- Advanced Stats: 25 fixtures
- Schedules: 35 fixtures
- Box Scores: 25 fixtures
- Play-by-Play: 15 fixtures
- Player Profiles: 20 fixtures
- Player Game Logs: 20 fixtures
- Search Results: 10 fixtures

### Phase 3: New Page Types - Core Additions (200 fixtures)

> New page types requiring parser implementation.

- Coaches: 15 fixtures
- Draft: 30 fixtures
- Awards: 25 fixtures
- Playoffs: 30 fixtures
- All-Star: 20 fixtures
- Leaders: 20 fixtures
- Team Pages: 30 fixtures
- Executives: 10 fixtures
- Team Sub-pages: 30 fixtures

### Phase 4: Historical Leagues (80 fixtures)

> BAA, ABA, and NBL coverage.

- BAA: 12 fixtures (1947-1950)
- ABA: 36 fixtures (1968-1976)
- NBL: 10 fixtures
- Historical NBA: 22 fixtures

### Phase 5: Extended League Stats (60 fixtures)

> Statistical variants by season.

- Per-Game Stats: 12 fixtures
- Per-Minute Stats: 12 fixtures
- Per-Possession Stats: 12 fixtures
- Shooting Stats: 12 fixtures
- Adjusted Shooting: 12 fixtures

### Phase 6: Player Sub-Pages (120 fixtures)

> Player statistical breakdowns.

- Splits: 20 fixtures
- Shooting: 20 fixtures
- Advanced: 20 fixtures
- Per-Minute: 20 fixtures
- Per-Possession: 20 fixtures
- Playoffs: 20 fixtures

## Validation

All fixtures are validated against structural rules defined in the scraper. See
[scraping-guide.md](./scraping-guide.md) for validation rules per page type.

## Archived Fixtures

Previous fixture versions are archived in `.archive/oldfiles/`. See
[.archive/README.md](../.archive/README.md) for archive documentation.

## References

| Topic | Location |
|-------|----------|
| Fixture rebuild plan | [PLAN.md](../PLAN.md) |
| Scraping guide | [scraping-guide.md](./scraping-guide.md) |
| Page type documentation | [page-types.md](./page-types.md) |
| Test strategy | [tests/AGENTS.md](../tests/AGENTS.md) |
