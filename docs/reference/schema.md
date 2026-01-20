# Schema Reference (Reference)

This document lists all database tables, keys, and column definitions as defined
by the Alembic migrations.

## Core Tables

See League Structure, Organizations, Seasons, Players, Games, Team Stats, Awards,
Draft, and Views for core schema definitions.

## League Structure

### league
- Primary key: league_id
- Unique: name
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| league_id | integer | no | autoincrement | |
| name | varchar(100) | no | - | |
| league_type | enum(leaguetype) | no | - | NBA, ABA, BAA |
| start_year | integer | no | - | |
| end_year | integer | yes | - | |
| is_active | boolean | no | true | |

### conference
- Primary key: conference_id
- Unique: conference_type
- Foreign keys: league_id -> league.league_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| conference_id | integer | no | autoincrement | |
| name | varchar(50) | no | - | |
| conference_type | enum(conferencetype) | no | - | EASTERN, WESTERN |
| league_id | integer | no | - | |

### division
- Primary key: division_id
- Unique: division_type
- Foreign keys: conference_id -> conference.conference_id, league_id -> league.league_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| division_id | integer | no | autoincrement | |
| name | varchar(50) | no | - | |
| division_type | enum(divisiontype) | no | - | |
| conference_id | integer | no | - | |
| league_id | integer | no | - | |

## Organizations

### franchise
- Primary key: franchise_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| franchise_id | integer | no | autoincrement | |
| name | varchar(100) | no | - | |
| founded_year | integer | no | - | |
| defunct_year | integer | yes | - | |
| city | varchar(100) | yes | - | |

### team
- Primary key: team_id
- Unique: abbreviation
- Foreign keys: division_id -> division.division_id, franchise_id -> franchise.franchise_id
- Indexes: name, abbreviation
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| team_id | integer | no | autoincrement | |
| name | varchar(100) | no | - | |
| abbreviation | varchar(3) | no | - | |
| founded_year | integer | no | - | |
| defunct_year | integer | yes | - | |
| division_id | integer | yes | - | |
| franchise_id | integer | no | - | |
| is_active | boolean | no | true | |
| is_defunct | boolean | no | false | |
| city | varchar(100) | yes | - | |
| arena | varchar(100) | yes | - | |
| arena_capacity | integer | yes | - | |
| relocation_history | json | yes | - | |

## Seasons

### season
- Primary key: season_id
- Foreign keys: league_id -> league.league_id, champion_team_id -> team.team_id,
  runner_up_team_id -> team.team_id
- Indexes: year
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| season_id | integer | no | autoincrement | |
| league_id | integer | no | - | |
| year | integer | no | - | Season end year |
| season_name | varchar(20) | yes | - | |
| start_date | date | no | - | |
| end_date | date | no | - | |
| all_star_date | date | yes | - | |
| playoffs_start_date | date | yes | - | |
| playoffs_end_date | date | yes | - | |
| champion_team_id | integer | yes | - | |
| runner_up_team_id | integer | yes | - | |
| is_active | boolean | no | false | |

## Players

### player
- Primary key: player_id
- Unique: slug
- Indexes: slug
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| player_id | integer | no | autoincrement | |
| slug | varchar(20) | no | - | |
| first_name | varchar(50) | no | - | |
| last_name | varchar(50) | no | - | |
| middle_name | varchar(50) | yes | - | |
| birth_date | date | yes | - | |
| birth_place_city | varchar(100) | yes | - | |
| birth_place_country | varchar(100) | yes | - | |
| death_date | date | yes | - | |
| height_inches | numeric(5,2) | yes | - | |
| weight_lbs | integer | yes | - | |
| position | enum(player_position) | yes | - | |
| high_school | varchar(100) | yes | - | |
| college | varchar(100) | yes | - | |
| draft_year | integer | yes | - | |
| draft_pick | integer | yes | - | |
| debut_date | date | yes | - | |
| final_date | date | yes | - | |
| debut_year | integer | yes | - | |
| final_year | integer | yes | - | |
| is_active | boolean | no | true | |

### player_season
- Primary key: (player_id, season_id, season_type)
- Foreign keys: player_id -> player.player_id, season_id -> season.season_id,
  team_id -> team.team_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| player_id | integer | no | - | |
| season_id | integer | no | - | |
| season_type | enum(seasontype) | no | REGULAR | |
| team_id | integer | yes | - | |
| player_age | integer | yes | - | |
| position | enum(player_position) | yes | - | |
| games_played | integer | no | 0 | |
| games_started | integer | no | 0 | |
| minutes_played | integer | no | 0 | |
| made_fg | integer | no | 0 | |
| attempted_fg | integer | no | 0 | |
| made_3pt | integer | no | 0 | |
| attempted_3pt | integer | no | 0 | |
| made_ft | integer | no | 0 | |
| attempted_ft | integer | no | 0 | |
| offensive_rebounds | integer | no | 0 | |
| defensive_rebounds | integer | no | 0 | |
| total_rebounds | integer | no | 0 | |
| assists | integer | no | 0 | |
| steals | integer | no | 0 | |
| blocks | integer | no | 0 | |
| turnovers | integer | no | 0 | |
| personal_fouls | integer | no | 0 | |
| points_scored | integer | no | 0 | |
| double_doubles | integer | no | 0 | |
| triple_doubles | integer | no | 0 | |
| is_combined_totals | boolean | no | false | |

### player_season_advanced
- Primary key: (player_id, season_id, season_type)
- Foreign keys: player_id -> player.player_id, season_id -> season.season_id,
  team_id -> team.team_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| player_id | integer | no | - | |
| season_id | integer | no | - | |
| season_type | enum(seasontype) | no | REGULAR | |
| team_id | integer | yes | - | |
| player_age | integer | yes | - | |
| games_played | integer | no | 0 | |
| minutes_played | integer | no | 0 | |
| player_efficiency_rating | numeric(6,2) | yes | - | |
| true_shooting_percentage | numeric(5,3) | yes | - | |
| effective_fg_percentage | numeric(5,3) | yes | - | |
| three_point_attempt_rate | numeric(5,3) | yes | - | |
| free_throw_attempt_rate | numeric(5,3) | yes | - | |
| usage_percentage | numeric(5,2) | yes | - | |
| assist_percentage | numeric(5,2) | yes | - | |
| turnover_percentage | numeric(5,2) | yes | - | |
| offensive_rebound_percentage | numeric(5,2) | yes | - | |
| defensive_rebound_percentage | numeric(5,2) | yes | - | |
| total_rebound_percentage | numeric(5,2) | yes | - | |
| steal_percentage | numeric(5,2) | yes | - | |
| block_percentage | numeric(5,2) | yes | - | |
| offensive_box_plus_minus | numeric(5,2) | yes | - | |
| defensive_box_plus_minus | numeric(5,2) | yes | - | |
| box_plus_minus | numeric(5,2) | yes | - | |
| value_over_replacement_player | numeric(5,2) | yes | - | |
| offensive_win_shares | numeric(6,3) | yes | - | |
| defensive_win_shares | numeric(6,3) | yes | - | |
| win_shares | numeric(6,3) | yes | - | |
| win_shares_per_48 | numeric(6,3) | yes | - | |
| is_combined_totals | boolean | no | false | |

### player_shooting
- Primary key: (player_id, season_id, distance_range)
- Foreign keys: player_id -> player.player_id, season_id -> season.season_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| player_id | integer | no | - | |
| season_id | integer | no | - | |
| distance_range | varchar(20) | no | - | |
| fg_made | integer | no | 0 | |
| fg_attempted | integer | no | 0 | |
| fg_percentage | numeric(5,3) | yes | - | |

## Games

### game
- Primary key: game_id
- Foreign keys: season_id -> season.season_id, home_team_id -> team.team_id,
  away_team_id -> team.team_id
- Indexes: season_id, game_date, home_team_id, away_team_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| game_id | integer | no | autoincrement | |
| season_id | integer | no | - | |
| game_date | date | no | - | |
| game_time | time | yes | - | |
| home_team_id | integer | no | - | |
| away_team_id | integer | no | - | |
| home_score | integer | yes | - | |
| away_score | integer | yes | - | |
| season_type | text | no | REGULAR | |
| arena | varchar(100) | yes | - | |
| attendance | integer | yes | - | |
| duration_minutes | integer | yes | - | |
| officials | json | yes | - | |
| playoff_round | varchar(50) | yes | - | |
| playoff_game_number | integer | yes | - | |
| series_home_wins | integer | yes | - | |
| series_away_wins | integer | yes | - | |
| box_score_url | varchar(255) | yes | - | |
| play_by_play_url | varchar(255) | yes | - | |

### box_score
- Primary key: box_id
- Foreign keys: game_id -> game.game_id, team_id -> team.team_id,
  opponent_team_id -> team.team_id
- Indexes: game_id, team_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| box_id | integer | no | autoincrement | |
| game_id | integer | no | - | |
| team_id | integer | no | - | |
| location | enum(location) | no | - | HOME, AWAY |
| outcome | enum(outcome) | no | - | WIN, LOSS |
| opponent_team_id | integer | yes | - | |
| seconds_played | integer | yes | - | |
| made_fg | integer | no | 0 | |
| attempted_fg | integer | no | 0 | |
| made_3pt | integer | no | 0 | |
| attempted_3pt | integer | no | 0 | |
| made_ft | integer | no | 0 | |
| attempted_ft | integer | no | 0 | |
| offensive_rebounds | integer | no | 0 | |
| defensive_rebounds | integer | no | 0 | |
| total_rebounds | integer | yes | - | |
| assists | integer | no | 0 | |
| steals | integer | no | 0 | |
| blocks | integer | no | 0 | |
| turnovers | integer | no | 0 | |
| personal_fouls | integer | no | 0 | |
| points_scored | integer | no | 0 | |
| plus_minus | integer | yes | - | |
| field_goal_percentage | numeric(5,3) | yes | - | |
| three_point_percentage | numeric(5,3) | yes | - | |
| free_throw_percentage | numeric(5,3) | yes | - | |
| quarter_scores | json | yes | - | |

### player_box_score
- Primary key: (player_id, box_id)
- Foreign keys: player_id -> player.player_id, box_id -> box_score.box_id,
  game_id -> game.game_id, team_id -> team.team_id
- Indexes: game_id, team_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| player_id | integer | no | - | |
| box_id | integer | no | - | |
| game_id | integer | no | - | |
| team_id | integer | no | - | |
| player_slug | varchar(20) | yes | - | |
| player_name | text | yes | - | |
| position | enum(player_position) | yes | - | |
| is_starter | boolean | no | false | |
| seconds_played | integer | no | 0 | |
| made_fg | integer | no | 0 | |
| attempted_fg | integer | no | 0 | |
| made_3pt | integer | no | 0 | |
| attempted_3pt | integer | no | 0 | |
| made_ft | integer | no | 0 | |
| attempted_ft | integer | no | 0 | |
| offensive_rebounds | integer | no | 0 | |
| defensive_rebounds | integer | no | 0 | |
| assists | integer | no | 0 | |
| steals | integer | no | 0 | |
| blocks | integer | no | 0 | |
| turnovers | integer | no | 0 | |
| personal_fouls | integer | no | 0 | |
| points_scored | integer | no | 0 | |
| plus_minus | integer | yes | - | |
| game_score | numeric(6,2) | yes | - | |

### play_by_play
- Primary key: play_id
- Foreign keys: game_id -> game.game_id, team_id -> team.team_id,
  player_involved_id -> player.player_id, assist_player_id -> player.player_id,
  block_player_id -> player.player_id
- Indexes: game_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| play_id | integer | no | autoincrement | |
| game_id | integer | no | - | |
| period | integer | no | - | |
| period_type | enum(periodtype) | no | - | QUARTER, OVERTIME |
| seconds_remaining | integer | no | - | |
| away_score | integer | yes | - | |
| home_score | integer | yes | - | |
| team_id | integer | yes | - | |
| play_type | enum(playtype) | no | - | |
| player_involved_id | integer | yes | - | |
| assist_player_id | integer | yes | - | |
| block_player_id | integer | yes | - | |
| description | text | yes | - | |
| shot_distance_ft | integer | yes | - | |
| shot_type | varchar(50) | yes | - | |
| foul_type | varchar(50) | yes | - | |
| points_scored | integer | no | 0 | |
| is_fast_break | boolean | no | false | |
| is_second_chance | boolean | no | false | |

## Team Stats

### team_season
- Primary key: (team_id, season_id, season_type)
- Foreign keys: team_id -> team.team_id, season_id -> season.season_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| team_id | integer | no | - | |
| season_id | integer | no | - | |
| season_type | text | no | REGULAR | |
| games_played | integer | no | 0 | |
| wins | integer | no | 0 | |
| losses | integer | no | 0 | |
| home_wins | integer | no | 0 | |
| home_losses | integer | no | 0 | |
| road_wins | integer | no | 0 | |
| road_losses | integer | no | 0 | |
| conference_wins | integer | no | 0 | |
| conference_losses | integer | no | 0 | |
| division_wins | integer | no | 0 | |
| division_losses | integer | no | 0 | |
| win_streak | integer | no | 0 | |
| loss_streak | integer | no | 0 | |
| longest_win_streak | integer | no | 0 | |
| longest_loss_streak | integer | no | 0 | |
| points_scored | integer | no | 0 | |
| points_allowed | integer | no | 0 | |
| points_per_game | numeric(5,2) | yes | - | |
| points_allowed_per_game | numeric(5,2) | yes | - | |
| minutes_played | integer | no | 0 | |
| made_fg | integer | no | 0 | |
| attempted_fg | integer | no | 0 | |
| made_3pt | integer | no | 0 | |
| attempted_3pt | integer | no | 0 | |
| made_ft | integer | no | 0 | |
| attempted_ft | integer | no | 0 | |
| offensive_rebounds | integer | no | 0 | |
| defensive_rebounds | integer | no | 0 | |
| total_rebounds | integer | no | 0 | |
| assists | integer | no | 0 | |
| steals | integer | no | 0 | |
| blocks | integer | no | 0 | |
| turnovers | integer | no | 0 | |
| personal_fouls | integer | no | 0 | |
| pace | numeric(6,2) | yes | - | |
| offensive_rating | numeric(6,2) | yes | - | |
| defensive_rating | numeric(6,2) | yes | - | |
| net_rating | numeric(6,2) | yes | - | |
| playoff_seed | integer | yes | - | |
| made_playoffs | boolean | no | false | |
| playoff_round_reached | varchar(50) | yes | - | |

## Awards

### award
- Primary key: award_id
- Unique: name
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| award_id | integer | no | autoincrement | |
| name | varchar(100) | no | - | |
| category | enum(awardcategory) | no | - | |
| description | text | yes | - | |
| first_awarded_year | integer | yes | - | |
| last_awarded_year | integer | yes | - | |
| is_active | boolean | no | true | |

### award_recipient
- Primary key: (award_id, season_id)
- Foreign keys: award_id -> award.award_id, season_id -> season.season_id,
  player_id -> player.player_id, team_id -> team.team_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| award_id | integer | no | - | |
| season_id | integer | no | - | |
| player_id | integer | yes | - | |
| team_id | integer | yes | - | |
| vote_rank | integer | yes | - | |
| vote_count | integer | yes | - | |
| vote_percentage | float | yes | - | |
| first_place_votes | integer | yes | - | |
| recipient_type | enum(recipienttype) | yes | - | PLAYER, TEAM, COACH |
| notes | text | yes | - | |

## Draft

### draft
- Primary key: draft_id
- Unique: season_id
- Foreign keys: season_id -> season.season_id
- Indexes: year
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| draft_id | integer | no | autoincrement | |
| season_id | integer | no | - | |
| year | integer | no | - | |
| draft_date | date | yes | - | |
| round_count | integer | no | - | |
| pick_count | integer | no | - | |

### draft_pick
- Primary key: pick_id
- Foreign keys: draft_id -> draft.draft_id, team_id -> team.team_id,
  player_id -> player.player_id, original_team_id -> team.team_id
- Indexes: draft_id, team_id
- Columns:
| Column | Type | Nullable | Default | Notes |
| --- | --- | --- | --- | --- |
| pick_id | integer | no | autoincrement | |
| draft_id | integer | no | - | |
| overall_pick | integer | no | - | |
| round_number | integer | no | - | |
| round_pick | integer | no | - | |
| team_id | integer | no | - | |
| player_id | integer | yes | - | |
| original_team_id | integer | yes | - | |
| trade_notes | text | yes | - | |
| college | varchar(100) | yes | - | |
| height_in | integer | yes | - | |
| weight_lbs | integer | yes | - | |
| position | enum(player_position) | yes | - | |

## Views

### player_career_stats
- Columns: player_id, slug, first_name, last_name, games_played, career_points,
  career_assists, career_rebounds, ppg, apg, rpg
- Indexes: player_id, slug

### team_season_standings
- Columns: team_id, team_abbrev, team_name, season_id, wins, losses, games_played,
  points_per_game, points_allowed_per_game, win_pct
- Indexes: season_id, team_id
- Filter: season_type = 'REGULAR'

## Staging Tables (UNLOGGED)

All staging tables are UNLOGGED with:
- row_id bigserial primary key
- import_batch_id uuid
- validation_errors jsonb
- All CSV columns as text

Staging tables:
- staging_players
- staging_games
- staging_team_histories
- staging_player_statistics
- staging_team_statistics
- staging_player_totals
- staging_player_advanced
- staging_player_shooting
- staging_draft_pick_history
- staging_all_star_selections
- staging_end_season_teams
- staging_team_totals
- staging_team_summaries
- staging_nba_championships
- staging_nba_players

## Enums

| Enum | Values |
| --- | --- |
| leaguetype | NBA, ABA, BAA |
| conferencetype | EASTERN, WESTERN |
| divisiontype | ATLANTIC, CENTRAL, SOUTHEAST, NORTHWEST, PACIFIC, SOUTHWEST, MIDWEST |
| player_position | POINT_GUARD, SHOOTING_GUARD, SMALL_FORWARD, POWER_FORWARD, CENTER, GUARD, FORWARD |
| seasontype | REGULAR, PLAYOFF, ALL_STAR, PRESEASON |
| location | HOME, AWAY |
| outcome | WIN, LOSS |
| periodtype | QUARTER, OVERTIME |
| playtype | FIELD_GOAL_MADE, FIELD_GOAL_MISSED, FREE_THROW_MADE, FREE_THROW_MISSED, REBOUND_OFFENSIVE, REBOUND_DEFENSIVE, ASSIST, STEAL, BLOCK, TURNOVER, FOUL_PERSONAL, FOUL_TECHNICAL, FOUL_FLAGRANT, TIMEOUT, SUBSTITUTION, VIOLATION, JUMP_BALL, PERIOD_START, PERIOD_END |
| awardcategory | MOST_VALUABLE_PLAYER, CHAMPIONSHIP, FINALS_MVP, DEFENSIVE_PLAYER_OF_THE_YEAR, ROOKIE_OF_THE_YEAR, COACH_OF_THE_YEAR, SIXTH_MAN, MOST_IMPROVED, ALL_NBA_FIRST_TEAM, ALL_NBA_SECOND_TEAM, ALL_NBA_THIRD_TEAM, ALL_DEFENSIVE_FIRST_TEAM, ALL_DEFENSIVE_SECOND_TEAM, ALL_ROOKIE_FIRST_TEAM, ALL_ROOKIE_SECOND_TEAM, ALL_STAR |
| recipienttype | PLAYER, TEAM, COACH |

## References

| Topic | Location | Anchor |
| --- | --- | --- |
| Initial schema migration | `webapp/backend/alembic/versions/20260119_000001_initial_schema.py` | `upgrade` |
| Staging tables + views | `webapp/backend/alembic/versions/20260120_000002_staging_and_views.py` | `upgrade` |
| Implementation spec | `docs/specs/implementation.md` | `1-data-model-changes` |
