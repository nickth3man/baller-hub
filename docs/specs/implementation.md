# Basketball-Reference Clone Implementation Spec (Implementation)

## 1. Data Model Changes

### 1.1 New Table: player_shooting
Purpose: store per-season shooting splits by distance range.

Columns:
- player_id (FK player.player_id)
- season_id (FK season.season_id)
- distance_range (text: "0-3 ft", "3-10 ft", "10-16 ft", "16-3P", "3P")
- fg_made, fg_attempted (int)
- fg_percentage (numeric(5,3))

Primary Key: (player_id, season_id, distance_range)

### 1.2 Staging Tables (UNLOGGED)
All staging tables use TEXT columns for import flexibility plus:
- import_batch_id UUID
- validation_errors JSONB

Staging tables required:
- staging_players (`raw-data/misc-csv/csv_1/Players.csv`)
- staging_games (`raw-data/misc-csv/csv_1/Games.csv`)
- staging_team_histories (`raw-data/misc-csv/csv_1/TeamHistories.csv`)
- staging_player_statistics (`raw-data/misc-csv/csv_1/PlayerStatistics.csv`)
- staging_team_statistics (`raw-data/misc-csv/csv_1/TeamStatistics.csv`)
- staging_player_totals (`raw-data/misc-csv/csv_2/Player Totals.csv`)
- staging_player_advanced (`raw-data/misc-csv/csv_2/Advanced.csv`)
- staging_player_shooting (`raw-data/misc-csv/csv_2/Player Shooting.csv`)
- staging_draft_pick_history (`raw-data/misc-csv/csv_2/Draft Pick History.csv`)
- staging_all_star_selections (`raw-data/misc-csv/csv_2/All-Star Selections.csv`)
- staging_end_season_teams (`raw-data/misc-csv/csv_2/End of Season Teams.csv`)
- staging_team_totals (`raw-data/misc-csv/csv_2/Team Totals.csv`)
- staging_team_summaries (`raw-data/misc-csv/csv_2/Team Summaries.csv`)
- staging_nba_championships (`raw-data/misc-csv/csv_4/nba_championships.csv`)
- staging_nba_players (`raw-data/misc-csv/csv_4/nba_players.csv`)

### 1.3 Materialized Views
- player_career_stats: aggregated career totals and per-game rates.
- team_season_standings: win/loss + win_pct summary for standings.

## 2. Data Sources and Source of Truth

### 2.1 Source-of-Truth Matrix

| Target | Primary source | Fallback | Notes |
|--------|----------------|----------|-------|
| player | `raw-data/misc-csv/csv_1/Players.csv` | `raw-data/misc-csv/csv_3/player.csv`, `raw-data/database/sqlite/nba.sqlite` table `player` | Set `player.player_id = personId`. Map csv_2 `player_id` (BR slug) to `player.slug`. |
| team + franchise | `raw-data/misc-csv/csv_1/TeamHistories.csv` | `raw-data/misc-csv/csv_3/team.csv`, `team_details.csv`, `team_history.csv` | Use `teamId` as `team.team_id`, `teamAbbrev` as `team.abbreviation`. Create `franchise` per unique `teamCity + teamName`. |
| season | derived from `game_date` | manual seed (Season table) | Season.year is end year. Times are US/Eastern. |
| game | `raw-data/misc-csv/csv_1/Games.csv` plus `LeagueSchedule24_25.csv` and `LeagueSchedule25_26.csv` | `raw-data/misc-csv/csv_3/game.csv` | Use `gameId` for `game.game_id`. |
| box_score | `raw-data/misc-csv/csv_1/TeamStatistics.csv` | `raw-data/misc-csv/csv_3/line_score.csv`, HTML `line_score` | TeamStatistics provides per-game totals; line_score fills `quarter_scores`. |
| player_box_score | `raw-data/misc-csv/csv_1/PlayerStatistics.csv` | HTML `box-<TEAM>-game-basic` rows or player game logs | Join on `personId` + `gameId`. |
| player_season | `raw-data/misc-csv/csv_2/Player Totals.csv` | aggregate `PlayerStatistics.csv`, HTML `totals_stats` | CSV uses BR slug in `player_id`; map to `player.slug`. |
| player_season_advanced | `raw-data/misc-csv/csv_2/Advanced.csv` | HTML `advanced` | Compute `effective_fg_percentage` from totals. |
| player_shooting | `raw-data/misc-csv/csv_2/Player Shooting.csv` | HTML shooting table (not in fixtures) | Derive `fg_attempted`/`fg_made` from total FGA + percent share. |
| team_season | `raw-data/misc-csv/csv_2/Team Totals.csv` + `Team Summaries.csv` | aggregate `TeamStatistics.csv`, HTML `per_game-team` | `playoffs` column sets season_type. |
| play_by_play | `raw-data/misc-csv/csv_3/play_by_play.csv` (bulk seed) | HTML `pbp` | HTML scrape uses `PlayByPlayRow` column positions. |

### 2.2 Column-Level Mappings (CSV -> Tables)

#### Players.csv -> player
| CSV column | Field | Notes |
|------------|-------|-------|
| personId | player_id | Use NBA API id for stable joins. |
| firstName | first_name | |
| lastName | last_name | |
| birthdate | birth_date | Parse YYYY-MM-DD. |
| country | birth_place_country | Null if empty. |
| height | height_inches | Assume inches; convert if source changes. |
| bodyWeight | weight_lbs | |
| guard/forward/center | position | If multiple flags, prefer GUARD > FORWARD > CENTER. |
| draftYear | draft_year | |
| draftNumber | draft_pick | |
| (computed) | slug | lower(last_name) + first 2 of first_name + "01". |

#### Games.csv -> game
| CSV column | Field | Notes |
|------------|-------|-------|
| gameId | game_id | Use CSV id as PK. |
| gameDateTimeEst | game_date + game_time | Parse US/Eastern. |
| hometeamId | home_team_id | Map via `team.team_id`. |
| awayteamId | away_team_id | Map via `team.team_id`. |
| homeScore | home_score | |
| awayScore | away_score | |
| gameType | season_type | REGULAR/PLAYOFF mapping. |
| attendance | attendance | |
| arenaId | arena | Leave null unless mapped. |

#### TeamStatistics.csv -> box_score
| CSV column | Field | Notes |
|------------|-------|-------|
| gameId | game_id | |
| teamId | team_id | |
| opponentTeamId | opponent_team_id | |
| home | location | HOME if true else AWAY. |
| win | outcome | WIN if true else LOSS. |
| numMinutes | seconds_played | minutes * 60. |
| fieldGoalsMade | made_fg | |
| fieldGoalsAttempted | attempted_fg | |
| threePointersMade | made_3pt | |
| threePointersAttempted | attempted_3pt | |
| freeThrowsMade | made_ft | |
| freeThrowsAttempted | attempted_ft | |
| reboundsOffensive | offensive_rebounds | |
| reboundsDefensive | defensive_rebounds | |
| assists | assists | |
| steals | steals | |
| blocks | blocks | |
| turnovers | turnovers | |
| foulsPersonal | personal_fouls | |
| teamScore | points_scored | |
| plusMinusPoints | plus_minus | |
| q1Points..q4Points | quarter_scores | Dict per quarter; OT missing in CSV_1. |
Derived:
- `total_rebounds` = reboundsOffensive + reboundsDefensive.
- `field_goal_percentage`, `three_point_percentage`, `free_throw_percentage` computed from makes/attempts.

#### PlayerStatistics.csv -> player_box_score
| CSV column | Field | Notes |
|------------|-------|-------|
| personId | player_id | |
| gameId | game_id | |
| playerteamCity + playerteamName | team_id | Map via `team.city` + `team.name`. |
| numMinutes | seconds_played | minutes * 60. |
| points | points_scored | |
| assists | assists | |
| blocks | blocks | |
| steals | steals | |
| fieldGoalsMade | made_fg | |
| fieldGoalsAttempted | attempted_fg | |
| threePointersMade | made_3pt | |
| threePointersAttempted | attempted_3pt | |
| freeThrowsMade | made_ft | |
| freeThrowsAttempted | attempted_ft | |
| reboundsOffensive | offensive_rebounds | |
| reboundsDefensive | defensive_rebounds | |
| foulsPersonal | personal_fouls | |
| turnovers | turnovers | |
| plusMinusPoints | plus_minus | |
Derived:
- `is_starter` defaults to false (no CSV column).
- `player_slug` populated from `player.slug` for the same `player_id`.

#### Player Totals.csv -> player_season
| CSV column | Field | Notes |
|------------|-------|-------|
| season | season_id | Season.year == season end year. |
| player_id | player.slug | CSV uses BR slug. |
| age | player_age | |
| team | team_id | If TOT/2TM/3TM set `is_combined_totals` true and `team_id` null. |
| pos | position | |
| g | games_played | |
| gs | games_started | |
| mp | minutes_played | |
| fg | made_fg | |
| fga | attempted_fg | |
| x3p | made_3pt | |
| x3pa | attempted_3pt | |
| ft | made_ft | |
| fta | attempted_ft | |
| orb | offensive_rebounds | |
| drb | defensive_rebounds | |
| trb | total_rebounds | |
| ast | assists | |
| stl | steals | |
| blk | blocks | |
| tov | turnovers | |
| pf | personal_fouls | |
| pts | points_scored | |
| trp_dbl | triple_doubles | |
| (not stored) | double_doubles | Set to 0. |
| fg_percent, x3p_percent, x2p, x2pa, x2p_percent, e_fg_percent, ft_percent | derived | Compute in views if needed. |

#### Advanced.csv -> player_season_advanced
| CSV column | Field | Notes |
|------------|-------|-------|
| season | season_id | |
| player_id | player.slug | |
| age | player_age | |
| team | team_id | Same combined totals rule as Player Totals. |
| g | games_played | |
| mp | minutes_played | |
| per | player_efficiency_rating | |
| ts_percent | true_shooting_percentage | |
| x3p_ar | three_point_attempt_rate | |
| f_tr | free_throw_attempt_rate | |
| orb_percent | offensive_rebound_percentage | |
| drb_percent | defensive_rebound_percentage | |
| trb_percent | total_rebound_percentage | |
| ast_percent | assist_percentage | |
| stl_percent | steal_percentage | |
| blk_percent | block_percentage | |
| tov_percent | turnover_percentage | |
| usg_percent | usage_percentage | |
| ows | offensive_win_shares | |
| dws | defensive_win_shares | |
| ws | win_shares | |
| ws_48 | win_shares_per_48 | |
| obpm | offensive_box_plus_minus | |
| dbpm | defensive_box_plus_minus | |
| bpm | box_plus_minus | |
| vorp | value_over_replacement_player | |
| (derived) | effective_fg_percentage | Prefer Player Totals `e_fg_percent`; else compute `(made_fg + 0.5 * made_3pt) / attempted_fg` from Player Totals. |

#### Player Shooting.csv -> player_shooting
| Source columns | Field | Notes |
|----------------|-------|-------|
| percent_fga_from_x0_3_range + fg_percent_from_x0_3_range | distance_range="0-3 ft" | Attempts = round(fga * percent_fga_from_x0_3_range). |
| percent_fga_from_x3_10_range + fg_percent_from_x3_10_range | distance_range="3-10 ft" | |
| percent_fga_from_x10_16_range + fg_percent_from_x10_16_range | distance_range="10-16 ft" | |
| percent_fga_from_x16_3p_range + fg_percent_from_x16_3p_range | distance_range="16-3P" | |
| percent_fga_from_x3p_range + fg_percent_from_x3p_range | distance_range="3P" | |
Notes:
- `fg_attempted` derived from total FGA in Player Totals; `fg_made` = round(fg_attempted * fg_percent).
- Adjust final bucket (3P) to fix rounding diff so sum of per-range attempts equals total FGA.
- Use combined totals row (team TOT/2TM/3TM) only.

#### Team Totals.csv + Team Summaries.csv -> team_season
| CSV column | Field | Notes |
|------------|-------|-------|
| abbreviation | team_id | Map via `team.abbreviation`. |
| Team Totals.g | games_played | |
| Team Summaries.w/l | wins/losses | |
| Team Totals.pts | points_scored | |
| Team Summaries.o_rtg/d_rtg/n_rtg | offensive_rating/defensive_rating/net_rating | |
| Team Summaries.pace | pace | |
| Team Totals.playoffs | season_type | PLAYOFF if 1 else REGULAR. |

### 2.3 HTML Fixtures and Table IDs (Basketball-Reference)

| Feature | Fixture | Table ID(s) | Parsing notes |
|--------|---------|-------------|---------------|
| Box score: line score | `tests/integration/files/boxscores/2018/1/1/201801010TOR.html` | `line_score` inside `div#all_line_score` | Table is inside HTML comment; unwrap `<!-- ... -->`. |
| Box score: four factors | `tests/integration/files/boxscores/2018/1/1/201801010TOR.html` | `four_factors` inside `div#all_four_factors` | Same comment wrapper. |
| Box score: team/player stats | `tests/integration/files/boxscores/2018/1/1/201801010TOR.html` | `box-{TEAM}-game-basic`, `box-{TEAM}-game-advanced`, `box-{TEAM}-q1-basic`, `box-{TEAM}-h1-basic`, `box-{TEAM}-ot1-basic` | TEAM is abbreviation from scorebox; use `tfoot` totals for `box_score`. |
| Play-by-play | `tests/integration/files/play_by_play/201810160GSW.html` | `pbp` inside `div#all_pbp` | 6 columns: time, away_play, away_margin, score, home_margin, home_play. |
| Player game log | `tests/integration/files/player_box_scores/2020/westbru01.html` | `player_game_log_reg`, `player_game_log_post` | Skip `tr.thead`, `tr.spacer`, `tr.partial_table`. |
| Player season totals | `tests/integration/files/players_season_totals/2024.html` | `totals_stats`, `totals_stats_post` | Wrapper `div#all_totals_stats` controls reg/post. |
| Player advanced totals | `tests/integration/files/player_advanced_season_totals/2019.html` | `advanced`, `advanced_post` | Wrapper `div#all_advanced` controls reg/post. |
| Schedule (monthly) | `tests/integration/files/schedule/2018/october.html` | `schedule` | Paginated by month. |
| Standings | `tests/integration/files/schedule/2019/2019.html` | `confs_standings_E/W`, `divs_standings_E/W` | Use for standings view only. |

Row filtering rules (HTML fixtures):
- PBP: ignore rows where `td` has `colspan="6"` (period start), `colspan="5"`, or header rows with `aria-label="Time"`.
- Box scores: ignore `tr.thead`, `tr.spacer`, and `tr.partial_table` when constructing season totals.
- Commented tables: if wrapper has `setup_commented commented`, parse the HTML comment content first.
PBP mapping (HTML -> model):
- `PlayByPlaysParser` returns `period`, `period_type`, `remaining_seconds_in_period`, `relevant_team`, `away_score`, `home_score`, `description`.
- Map to `PlayByPlay.period`, `PlayByPlay.period_type`, `PlayByPlay.seconds_remaining`, `PlayByPlay.team_id`, `PlayByPlay.away_score`, `PlayByPlay.home_score`, `PlayByPlay.description`.

### 2.4 Scraping Assumptions and Risk Controls

- Table IDs are not static for box scores; use `box-{TEAM}-*` with the team abbreviation from the scorebox.
- Some core tables are commented out; always un-comment before XPath selection.
- Play-by-play rows are positional (not `data-stat`); use `PlayByPlayRow` index logic.
- Combined totals rows (TOT/2TM/3TM) are authoritative for season aggregates when a player changes teams.

### 2.5 Play-by-Play Classification Rules

Use `description` text + score deltas to populate fields not provided by
`PlayByPlaysParser`.

| Signal in description | play_type | Notes |
|-----------------------|-----------|-------|
| "makes free throw" | FREE_THROW_MADE | points_scored = 1 |
| "misses free throw" | FREE_THROW_MISSED | points_scored = 0 |
| "makes 3-pt" | FIELD_GOAL_MADE | points_scored = 3 |
| "makes 2-pt" or "makes layup" | FIELD_GOAL_MADE | points_scored = 2 |
| "misses 3-pt" | FIELD_GOAL_MISSED | points_scored = 0 |
| "misses 2-pt" or "misses layup" | FIELD_GOAL_MISSED | points_scored = 0 |
| "Offensive rebound" | REBOUND_OFFENSIVE | |
| "Defensive rebound" | REBOUND_DEFENSIVE | |
| "Turnover" | TURNOVER | |
| "foul" + "technical" | FOUL_TECHNICAL | |
| "foul" + "flagrant" | FOUL_FLAGRANT | |
| "foul" (default) | FOUL_PERSONAL | |
| "timeout" | TIMEOUT | |
| "substitution" or "enters the game for" | SUBSTITUTION | |
| "violation" | VIOLATION | |
| "jump ball" | JUMP_BALL | |
| "Start of" | PERIOD_START | |
| "End of" | PERIOD_END | |

Player extraction:
- `player_involved_id`: first player link in the row description.
- `assist_player_id`: player after "assist by".
- `block_player_id`: player after "block by".
- If no player link present, leave IDs null.

Points scored:
- Prefer score delta vs previous non-empty score for the relevant team.
- Fallback to description pattern (3-pt, 2-pt, free throw).

Shot metadata:
- `shot_distance_ft`: regex `from (\\d+) ft`.
- `shot_type`: phrase after "makes"/"misses" before "from".
- `is_fast_break`: description contains "fast break".
- `is_second_chance`: description contains "second chance".

## 3. Ingestion Pipeline

### 3.1 Sources
- csv_1: core entities (players, games, team histories, basic stats).
- csv_2: Basketball-Reference format (totals, advanced, shooting, awards).
- csv_3: NBA API format (game, play-by-play, team metadata).
- csv_4: supplementary (champions, dedupe helpers).
- sqlite: nba.sqlite for fallback raw data (optional).

### 3.2 Flow
1. COPY CSV -> staging tables.
2. Validate with pg_input_is_valid + rule checks.
3. Upsert into production tables.
4. Refresh materialized views.

### 3.3 Mapping Rules (Core)
- player.slug: lowercase(last_name) + first 2 chars of first_name + "01".
- csv_1 `personId` maps to `player.player_id`; csv_2 `player_id` maps to `player.slug`.
- season_id: Season.year == season (end year) for BR datasets.
- season_end_year for game rows: `game_date.month >= 10 ? game_date.year + 1 : game_date.year`.
- team abbreviation: normalize and map via TEAM_ABBREVIATIONS_TO_TEAM.
- positions: map to enums (PG/SG/SF/PF/C -> Position enum).
- if team is deprecated, keep historical team data but never use deprecated
  teams for current-season queries.
- unwrap `setup_commented commented` wrappers before XPath selection.

## 4. Supabase Integration

### 4.1 Connection
- Use Supabase Postgres (`supabase-db`) as database host.
- Connection string: `postgresql+asyncpg://supabase_admin:password@supabase-db:5432/basketball_reference`.

### 4.2 Migration + Load Steps
1. Create `basketball_reference` database.
2. Apply Alembic migrations.
3. COPY CSVs into staging tables.
4. Run upsert SQL for production tables.
5. Refresh materialized views.

## 5. API Enhancements
Canonical parameter lists live in `docs/reference/api.md#endpoints`.

### 5.1 Players
- Implement player list filters and career endpoints defined in the API reference.

### 5.2 Games
- Implement list filters and play-by-play endpoints defined in the API reference.

### 5.3 Standings
- Implement point-in-time standings filter defined in the API reference.

## 6. UI Pages (MVP)
- Player Profile: `player` + `player_career_stats` view.
- Player Season Log: `player_box_score`.
- Team Roster: `player` + `player_season`.
- Game Box Score: `game` + `box_score` + `player_box_score`.
- Season Schedule: `game` filtered by season.
- Standings: `team_season_standings` view.

## ANTI-PATTERNS (DO NOT)

| DON'T | DO INSTEAD | WHY |
|-------|------------|-----|
| Insert CSV rows directly into production tables | Load into staging, validate, then upsert | Prevents corrupt data |
| Use deprecated team enums for current seasons | Normalize to current team abbreviations | Avoids incorrect current rosters |
| Skip pg_input_is_valid checks | Validate every numeric/date field | Prevents COPY failures |
| Mix multiple CSV sources without dedupe | Pick a single source of truth per table | Avoids duplicate players/games |
| Compute career stats per request | Use materialized views | Keeps endpoints fast |
| Assume tables are in the DOM | Unwrap `setup_commented commented` HTML before parsing | Avoids empty table extraction |
| Treat box score table IDs as fixed | Compute `box-{TEAM}-*` IDs from scorebox | Prevents missed team tables |
| Parse PBP without row filtering | Apply `PlayByPlayRow` rules for headers/spacers | Avoids bogus events |

## TEST CASE SPECIFICATIONS

### Unit Tests
| Test ID | Component | Input | Expected Output | Edge Cases |
|---------|-----------|-------|-----------------|------------|
| TC-001 | Slug generator | "LeBron James" | "jamesle01" | Multi-word last names |
| TC-002 | Position mapper | "G-F" | GUARD | Unknown position |
| TC-003 | Season resolver | season=1999 | season_id for 1999 | Missing season |
| TC-004 | CSV validator | birthdate="bad" | validation_errors set | empty fields |
| TC-005 | Shooting mapper | pct values | normalized decimals | null percentages |
| TC-006 | Comment unwrap | `all_line_score` HTML | table nodes parsed | nested comments |
| TC-007 | PBP row filter | rows with colspan/thead | skipped | empty rows |
| TC-008 | PBP classifier | "makes 3-pt..." | play_type=FIELD_GOAL_MADE, points_scored=3 | missing score |

### Integration Tests
| Test ID | Flow | Setup | Verification | Teardown |
|---------|------|-------|--------------|----------|
| IT-001 | CSV -> staging | sample Players.csv | staging_players row count | truncate staging |
| IT-002 | Staging -> player | staged players | player rows upserted | delete test rows |
| IT-003 | View refresh | player + box scores | player_career_stats matches totals | drop temp rows |
| IT-004 | Boxscore parsing | `201801010TOR.html` | line_score + four_factors extracted | none |
| IT-005 | PBP parsing | `201810160GSW.html` | play rows count > 0 | none |
| IT-006 | PBP player extraction | `201810160GSW.html` | assist/block player ids set | none |

## ERROR HANDLING MATRIX

### External Service Errors
| Error Type | Detection | Response | Fallback | Logging |
|------------|-----------|----------|----------|---------|
| Supabase connection failure | DB connect exception | Retry 3x | Abort import | ERROR |
| CSV file missing | FileNotFoundError | Skip dataset | Continue other datasets | WARN |
| COPY failure | asyncpg error | Mark batch failed | Halt batch | ERROR |
| Invalid numeric/date | pg_input_is_valid false | Set validation_errors | Skip row | WARN |
| Commented table missing | XPath table not found | Log + skip fixture | Use CSV fallback | WARN |
| PBP classification failure | Unmapped description | Store raw description | Set play_type=VIOLATION | WARN |

### User-Facing Errors
| Error Type | User Message | Code | Recovery Action |
|------------|--------------|------|-----------------|
| Player not found | "Player not found" | 404 | Show search link |
| Invalid query param | "Invalid filter value" | 400 | Show allowed values |
| Data not loaded | "Data unavailable" | 503 | Retry later |

## REFERENCES

| Topic | Location | Anchor |
|-------|----------|--------|
| Alembic schema | `webapp/backend/alembic/versions/20260119_000001_initial_schema.py` | `upgrade` |
| Ingestion tasks | `webapp/backend/app/ingestion/tasks.py` | `sync_season_data` |
| Ingestion repositories | `webapp/backend/app/ingestion/repositories.py` | `get_or_create_team` |
| Player service | `webapp/backend/app/services/player_service.py` | `list_players` |
| Games service | `webapp/backend/app/services/game_service.py` | `list_games` |
| Frontend players | `webapp/frontend/app/players/page.tsx` | `PlayersPage` |
| Play-by-play model | `webapp/backend/app/models/game.py` | `PlayByPlay` |
| Play type enum | `webapp/backend/app/models/game.py` | `PlayType` |
| Play-by-play HTML wrapper | `src/html/play_by_play.py` | `PlayByPlayRow` |
| Play-by-play parser | `src/parsers/play_by_play.py` | `PlayByPlaysParser` |
| Boxscore fixture | `tests/integration/files/boxscores/2018/1/1/201801010TOR.html` | `line_score` |
| PBP fixture | `tests/integration/files/play_by_play/201810160GSW.html` | `pbp` |
| Player totals fixture | `tests/integration/files/players_season_totals/2024.html` | `totals_stats` |
| Player game log fixture | `tests/integration/files/player_box_scores/2020/westbru01.html` | `player_game_log_reg` |
