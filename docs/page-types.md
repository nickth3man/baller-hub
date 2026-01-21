# Page Types Reference

Documentation for all basketball-reference.com page types supported by the scraper.

> **Source of Truth**: This document is derived from [PLAN.md](../PLAN.md).

## Overview

| Category | Page Types | Implementation Status |
|----------|------------|----------------------|
| Currently Implemented | 12 | ✅ Complete |
| Newly Discovered | 40+ | 🚧 In Progress |

## Currently Implemented (12 types)

### 1. Player Profile Pages

- **URL**: `/players/{letter}/{playerid}.html`
- **Example**: `/players/j/jamesle01.html`
- **HTML Wrapper**: `src/scraper/html/player.py` → `PlayerPage`
- **Parser**: `src/scraper/parsers/player.py`
- **Key Table IDs**: `totals_stats`, `advanced`, `per_game`

### 2. Player Game Logs (Regular Season)

- **URL**: `/players/{letter}/{playerid}/gamelog/{year}`
- **Example**: `/players/j/jamesle01/gamelog/2020`
- **HTML Wrapper**: `src/scraper/html/game_log.py` → `PlayerSeasonBoxScoresPage`
- **Key Table IDs**: `pgl_basic`, `pgl_basic_playoffs`

### 3. Player Game Logs (Playoffs)

- **URL**: `/players/{letter}/{playerid}/gamelog/{year}` (same page, different table)
- **Key Table IDs**: `pgl_basic_playoffs`

### 4. Player Season Totals

- **URL**: `/leagues/NBA_{year}_totals.html`
- **Example**: `/leagues/NBA_2024_totals.html`
- **HTML Wrapper**: `src/scraper/html/season_totals.py` → `PlayerSeasonTotalTable`
- **Parser**: `src/scraper/parsers/player.py` → `PlayerSeasonTotalsParser`
- **Key Table IDs**: `totals_stats`

### 5. Player Advanced Season Totals

- **URL**: `/leagues/NBA_{year}_advanced.html`
- **HTML Wrapper**: `src/scraper/html/season_totals.py` → `PlayerAdvancedSeasonTotalsTable`
- **Key Table IDs**: `advanced_stats`

### 6. Season Standings

- **URL**: `/leagues/NBA_{year}.html`
- **Example**: `/leagues/NBA_2024.html`
- **HTML Wrapper**: `src/scraper/html/standings.py` → `StandingsPage`
- **Parser**: `src/scraper/parsers/standings.py`
- **Key Table IDs**: `divs_standings_E`, `divs_standings_W`

### 7. Season Schedules (Full)

- **URL**: `/leagues/NBA_{year}_games.html`
- **HTML Wrapper**: `src/scraper/html/schedule.py` → `SchedulePage`
- **Parser**: `src/scraper/parsers/schedule.py`
- **Key Table IDs**: `schedule`

### 8. Season Schedules (Monthly)

- **URL**: `/leagues/NBA_{year}_games-{month}.html`
- **Example**: `/leagues/NBA_2024_games-october.html`
- **Same wrapper/parser as full schedule**

### 9. Daily Box Scores Index

- **URL**: `/boxscores/?month={m}&day={d}&year={y}`
- **HTML Wrapper**: `src/scraper/html/daily.py` → `DailyBoxScoresPage`
- **Returns**: List of game URLs for that day

### 10. Game Box Scores

- **URL**: `/boxscores/{gameid}.html`
- **Example**: `/boxscores/202406170BOS.html`
- **HTML Wrapper**: `src/scraper/html/box_scores.py` → `BoxScoresPage`
- **Parser**: `src/scraper/parsers/box_scores.py`
- **Key Table IDs**: `box-{TEAM}-game-basic`, `box-{TEAM}-game-advanced`

### 11. Play-by-Play

- **URL**: `/boxscores/pbp/{gameid}.html`
- **Example**: `/boxscores/pbp/202406170BOS.html`
- **HTML Wrapper**: `src/scraper/html/play_by_play.py` → `PlayByPlayPage`
- **Parser**: `src/scraper/parsers/play_by_play.py`
- **Key Table IDs**: `pbp`

### 12. Search Results

- **URL**: `/search/search.fcgi?search={term}`
- **HTML Wrapper**: `src/scraper/html/search.py` → `SearchPage`
- **Parser**: `src/scraper/parsers/search.py`
- **Key Sections**: `#players`, `#teams`

---

## Newly Discovered Page Types (40+)

### Coaches & Personnel

#### Coach Profile

- **URL**: `/coaches/{coachid}.html`
- **Example**: `/coaches/jacksph01c.html` (Phil Jackson)
- **HTML Wrapper**: `src/scraper/html/coach.py` → `CoachPage` 🚧
- **Key Table IDs**: `coaching_record`
- **Data**: Name, seasons coached, wins/losses, championships

#### Executive Profile

- **URL**: `/executives/{executiveid}/`
- **HTML Wrapper**: `src/scraper/html/executives.py` → `ExecutivePage` 🚧
- **Data**: GM/President history, team affiliations

#### Referee Directory

- **URL**: `/referees/`
- **HTML Wrapper**: `src/scraper/html/referees.py` → `RefereesPage` 🚧

---

### Draft

#### Annual Draft Results

- **URL**: `/draft/NBA_{year}.html`
- **Example**: `/draft/NBA_2024.html`
- **HTML Wrapper**: `src/scraper/html/draft.py` → `DraftPage` 🚧
- **Key Table IDs**: `stats`
- **Data**: Pick number, team, player, college, position

#### Draft Combine

- **URL**: `/draft/combine/{year}.html`
- **Data**: Measurements, athletic testing results

#### Draft Lottery

- **URL**: `/draft/lottery_{year}.html`
- **Data**: Lottery order, odds, results

---

### Awards

#### MVP History

- **URL**: `/awards/mvp.html`
- **HTML Wrapper**: `src/scraper/html/awards.py` → `AwardsPage` 🚧
- **Key Table IDs**: `mvp_NBA`

#### Other Award Pages

| Award | URL | Table ID |
|-------|-----|----------|
| Defensive POY | `/awards/dpoy.html` | `dpoy_NBA` |
| Rookie of Year | `/awards/roy.html` | `roy_NBA` |
| Sixth Man | `/awards/smoy.html` | `smoy_NBA` |
| Most Improved | `/awards/mip.html` | `mip_NBA` |
| Coach of Year | `/awards/coy.html` | `coy_NBA` |
| All-NBA Teams | `/awards/all_nba.html` | `all_nba` |
| All-Rookie Teams | `/awards/all_rookie.html` | `all_rookie` |
| All-Defensive Teams | `/awards/all_defensive.html` | `all_defense` |
| Hall of Fame | `/awards/hof.html` | `hof` |

---

### Playoffs

#### Playoff Bracket/Results

- **URL**: `/playoffs/NBA_{year}.html`
- **Example**: `/playoffs/NBA_2024.html`
- **HTML Wrapper**: `src/scraper/html/playoffs.py` → `PlayoffsPage` 🚧
- **Data**: Bracket, series results, round-by-round

#### Series Pages

- **URL**: `/playoffs/{year}-nba-{round}-{teams}.html`
- **Example**: `/playoffs/2024-nba-finals-celtics-vs-mavericks.html`
- **Data**: Game-by-game results, series stats

#### Playoff Stats

- **URL**: `/playoffs/NBA_{year}_per_game.html`
- **Data**: Playoff statistical leaders

---

### All-Star

#### All-Star Game Results

- **URL**: `/allstar/NBA_{year}.html`
- **Example**: `/allstar/NBA_2024.html`
- **HTML Wrapper**: `src/scraper/html/allstar.py` → `AllStarPage` 🚧
- **Data**: Game score, rosters, box score

#### All-Star History Index

- **URL**: `/allstar/`
- **Data**: Historical All-Star game list

---

### Leaders

#### Career Leaders

- **URL**: `/leaders/career_{stat}.html`
- **Examples**: `/leaders/career_pts.html`, `/leaders/career_ast.html`
- **HTML Wrapper**: `src/scraper/html/leaders.py` → `LeadersPage` 🚧
- **Data**: Top players all-time for each stat

#### Active Leaders

- **URL**: `/leaders/active_{stat}.html`
- **Data**: Top active players for each stat

#### Progressive/Trailing Leaders

- **URL**: `/trailers/{stat}_yearly_p.html`
- **Data**: Year-by-year progression of records

---

### Team Pages

#### Franchise History

- **URL**: `/teams/{team}/`
- **Example**: `/teams/BOS/`
- **HTML Wrapper**: `src/scraper/html/team_season.py` → `TeamPage` 🚧
- **Data**: All-time record, championships, retired numbers

#### Team Season Page

- **URL**: `/teams/{team}/{year}.html`
- **Example**: `/teams/BOS/2024.html`
- **Key Table IDs**: `roster`, `team_and_opponent`
- **Data**: Roster, season stats, schedule

#### Team Schedule

- **URL**: `/teams/{team}/{year}_schedule.html`

#### Team Game Log

- **URL**: `/teams/{team}/{year}_gamelog.html`

#### Team Draft History

- **URL**: `/teams/{team}/draft.html`

---

### League Statistics Variants

| Variant | URL Pattern | Description |
|---------|-------------|-------------|
| Per-Game | `/leagues/NBA_{year}_per_game.html` | Per-game averages |
| Per-Minute | `/leagues/NBA_{year}_per_minute.html` | Per-36-minute stats |
| Per-Possession | `/leagues/NBA_{year}_per_poss.html` | Per-100-possession stats |
| Shooting | `/leagues/NBA_{year}_shooting.html` | Shooting by distance |
| Adjusted Shooting | `/leagues/NBA_{year}_adj_shooting.html` | League-adjusted |
| Opponent Stats | `/leagues/NBA_{year}_opponent.html` | Opponent stats |
| Team Stats | `/leagues/NBA_{year}_team.html` | Team aggregates |
| Season Leaders | `/leagues/NBA_{year}_leaders.html` | Season stat leaders |
| Rookies | `/leagues/NBA_{year}_rookies.html` | Rookie stats only |
| Standings by Date | `/leagues/NBA_{year}_standings_by_date.html` | Historical standings |

---

### Player Sub-Pages

| Sub-Page | URL Pattern | Description |
|----------|-------------|-------------|
| Splits | `/players/{l}/{id}/splits/{year}` | Situational stats |
| Shooting | `/players/{l}/{id}/shooting/{year}` | Shot chart data |
| Advanced | `/players/{l}/{id}/advanced/{year}` | Advanced metrics |
| Per-Minute | `/players/{l}/{id}/per_minute/{year}` | Per-36 stats |
| Per-Possession | `/players/{l}/{id}/per_poss/{year}` | Per-100 stats |

---

### Historical Leagues

#### BAA (1946-1949)

- **URL**: `/leagues/BAA_{year}.html`
- **Years**: 1947, 1948, 1949, 1950

#### ABA (1967-1976)

- **URL**: `/leagues/ABA_{year}.html`
- **Years**: 1968-1976

#### NBL (Pre-BAA)

- **URL**: `/nbl/players/{id}n.html`

---

### Box Score Variants

| Variant | URL Pattern | Description |
|---------|-------------|-------------|
| Shooting | `/boxscores/{gameid}_shooting.html` | Shot chart |
| Advanced | `/boxscores/{gameid}_advanced.html` | Advanced box score |
| Four Factors | `/boxscores/{gameid}_four_factors.html` | Four factors analysis |

---

## Implementation Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Fully implemented with tests |
| 🚧 | In progress or planned |
| ❌ | Not planned for MVP |

## References

| Topic | Location |
|-------|----------|
| Fixture rebuild plan | [PLAN.md](../PLAN.md) |
| Fixture catalog | [fixtures.md](./fixtures.md) |
| Scraping guide | [scraping-guide.md](./scraping-guide.md) |
| HTML wrappers | `src/scraper/html/` |
| Parsers | `src/scraper/parsers/` |
