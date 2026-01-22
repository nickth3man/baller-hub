"""Celery tasks for data ingestion from the scraper.

These tasks run periodically or on-demand to fetch data from
basketball-reference.com and persist it to our database.
"""

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.core.domain import TEAM_TO_TEAM_ABBREVIATION

from app.celery_app import celery_app
from app.core.config import settings
from app.db.session import session_factory
from app.ingestion.repositories import get_or_create_season
from app.ingestion.scraper_service import ScraperService

logger = structlog.get_logger(__name__)


STAGING_TABLES: dict[str, list[str]] = {
    "staging_players": [
        "person_id",
        "first_name",
        "last_name",
        "birthdate",
        "last_attended",
        "country",
        "height",
        "body_weight",
        "guard",
        "forward",
        "center",
        "draft_year",
        "draft_round",
        "draft_number",
    ],
    "staging_games": [
        "game_id",
        "game_date_time_est",
        "hometeam_city",
        "hometeam_name",
        "hometeam_id",
        "awayteam_city",
        "awayteam_name",
        "awayteam_id",
        "home_score",
        "away_score",
        "winner",
        "game_type",
        "attendance",
        "arena_id",
        "game_label",
        "game_sub_label",
        "series_game_number",
    ],
    "staging_team_histories": [
        "team_id",
        "team_city",
        "team_name",
        "team_abbrev",
        "season_founded",
        "season_active_till",
        "league",
    ],
    "staging_player_statistics": [
        "first_name",
        "last_name",
        "person_id",
        "game_id",
        "game_date_time_est",
        "playerteam_city",
        "playerteam_name",
        "opponentteam_city",
        "opponentteam_name",
        "game_type",
        "game_label",
        "game_sub_label",
        "series_game_number",
        "win",
        "home",
        "num_minutes",
        "points",
        "assists",
        "blocks",
        "steals",
        "field_goals_attempted",
        "field_goals_made",
        "field_goals_percentage",
        "three_pointers_attempted",
        "three_pointers_made",
        "three_pointers_percentage",
        "free_throws_attempted",
        "free_throws_made",
        "free_throws_percentage",
        "rebounds_defensive",
        "rebounds_offensive",
        "rebounds_total",
        "fouls_personal",
        "turnovers",
        "plus_minus_points",
    ],
    "staging_team_statistics": [
        "game_id",
        "game_date_time_est",
        "team_city",
        "team_name",
        "team_id",
        "opponent_team_city",
        "opponent_team_name",
        "opponent_team_id",
        "home",
        "win",
        "team_score",
        "opponent_score",
        "assists",
        "blocks",
        "steals",
        "field_goals_attempted",
        "field_goals_made",
        "field_goals_percentage",
        "three_pointers_attempted",
        "three_pointers_made",
        "three_pointers_percentage",
        "free_throws_attempted",
        "free_throws_made",
        "free_throws_percentage",
        "rebounds_defensive",
        "rebounds_offensive",
        "rebounds_total",
        "fouls_personal",
        "turnovers",
        "plus_minus_points",
        "num_minutes",
        "q1_points",
        "q2_points",
        "q3_points",
        "q4_points",
        "bench_points",
        "biggest_lead",
        "biggest_scoring_run",
        "lead_changes",
        "points_fast_break",
        "points_from_turnovers",
        "points_in_the_paint",
        "points_second_chance",
        "times_tied",
        "timeouts_remaining",
        "season_wins",
        "season_losses",
        "coach_id",
    ],
    "staging_player_totals": [
        "season",
        "lg",
        "player",
        "player_id",
        "age",
        "team",
        "pos",
        "g",
        "gs",
        "mp",
        "fg",
        "fga",
        "fg_percent",
        "x3p",
        "x3pa",
        "x3p_percent",
        "x2p",
        "x2pa",
        "x2p_percent",
        "e_fg_percent",
        "ft",
        "fta",
        "ft_percent",
        "orb",
        "drb",
        "trb",
        "ast",
        "stl",
        "blk",
        "tov",
        "pf",
        "pts",
        "trp_dbl",
    ],
    "staging_player_advanced": [
        "season",
        "lg",
        "player",
        "player_id",
        "age",
        "team",
        "pos",
        "g",
        "gs",
        "mp",
        "per",
        "ts_percent",
        "x3p_ar",
        "f_tr",
        "orb_percent",
        "drb_percent",
        "trb_percent",
        "ast_percent",
        "stl_percent",
        "blk_percent",
        "tov_percent",
        "usg_percent",
        "ows",
        "dws",
        "ws",
        "ws_48",
        "obpm",
        "dbpm",
        "bpm",
        "vorp",
    ],
    "staging_player_shooting": [
        "season",
        "lg",
        "player",
        "player_id",
        "age",
        "team",
        "pos",
        "g",
        "gs",
        "mp",
        "fg_percent",
        "avg_dist_fga",
        "percent_fga_from_x2p_range",
        "percent_fga_from_x0_3_range",
        "percent_fga_from_x3_10_range",
        "percent_fga_from_x10_16_range",
        "percent_fga_from_x16_3p_range",
        "percent_fga_from_x3p_range",
        "fg_percent_from_x2p_range",
        "fg_percent_from_x0_3_range",
        "fg_percent_from_x3_10_range",
        "fg_percent_from_x10_16_range",
        "fg_percent_from_x16_3p_range",
        "fg_percent_from_x3p_range",
        "percent_assisted_x2p_fg",
        "percent_assisted_x3p_fg",
        "percent_dunks_of_fga",
        "num_of_dunks",
        "percent_corner_3s_of_3pa",
        "corner_3_point_percent",
        "num_heaves_attempted",
        "num_heaves_made",
    ],
    "staging_draft_pick_history": [
        "season",
        "lg",
        "overall_pick",
        "round",
        "tm",
        "player",
        "player_id",
        "college",
    ],
    "staging_all_star_selections": [
        "player",
        "player_id",
        "team",
        "season",
        "lg",
        "replaced",
    ],
    "staging_end_season_teams": [
        "season",
        "lg",
        "type",
        "number_tm",
        "player",
        "player_id",
        "position",
    ],
    "staging_team_totals": [
        "season",
        "lg",
        "team",
        "abbreviation",
        "playoffs",
        "g",
        "mp",
        "fg",
        "fga",
        "fg_percent",
        "x3p",
        "x3pa",
        "x3p_percent",
        "x2p",
        "x2pa",
        "x2p_percent",
        "ft",
        "fta",
        "ft_percent",
        "orb",
        "drb",
        "trb",
        "ast",
        "stl",
        "blk",
        "tov",
        "pf",
        "pts",
    ],
    "staging_team_summaries": [
        "season",
        "lg",
        "team",
        "abbreviation",
        "playoffs",
        "age",
        "w",
        "l",
        "pw",
        "pl",
        "mov",
        "sos",
        "srs",
        "o_rtg",
        "d_rtg",
        "n_rtg",
        "pace",
        "f_tr",
        "x3p_ar",
        "ts_percent",
        "e_fg_percent",
        "tov_percent",
        "orb_percent",
        "ft_fga",
        "opp_e_fg_percent",
        "opp_tov_percent",
        "drb_percent",
        "opp_ft_fga",
        "arena",
        "attend",
        "attend_g",
    ],
    "staging_nba_championships": [
        "season",
        "champion",
    ],
    "staging_nba_players": [
        "player_name",
        "team_abbreviation",
        "age",
        "player_height",
        "player_weight",
        "college",
        "country",
        "draft_year",
        "draft_round",
        "draft_number",
        "gp",
        "pts",
        "reb",
        "ast",
        "net_rating",
        "oreb_pct",
        "dreb_pct",
        "usg_pct",
        "ts_pct",
        "ast_pct",
        "season",
    ],
}

ALLOWED_STAGING_TABLES = frozenset(STAGING_TABLES.keys())
ALLOWED_COLUMN_TYPES = frozenset({"date", "timestamp", "int", "numeric", "text"})

DATA_ROOT = Path(__file__).resolve().parents[5] / "raw-data"

CSV_SOURCES: dict[str, Path] = {
    "staging_players": DATA_ROOT / "misc-csv" / "csv_1" / "Players.csv",
    "staging_games": DATA_ROOT / "misc-csv" / "csv_1" / "Games.csv",
    "staging_team_histories": DATA_ROOT / "misc-csv" / "csv_1" / "TeamHistories.csv",
    "staging_player_statistics": DATA_ROOT
    / "misc-csv"
    / "csv_1"
    / "PlayerStatistics.csv",
    "staging_team_statistics": DATA_ROOT / "misc-csv" / "csv_1" / "TeamStatistics.csv",
    "staging_player_totals": DATA_ROOT / "misc-csv" / "csv_2" / "Player Totals.csv",
    "staging_player_advanced": DATA_ROOT / "misc-csv" / "csv_2" / "Advanced.csv",
    "staging_player_shooting": DATA_ROOT / "misc-csv" / "csv_2" / "Player Shooting.csv",
    "staging_draft_pick_history": DATA_ROOT
    / "misc-csv"
    / "csv_2"
    / "Draft Pick History.csv",
    "staging_all_star_selections": DATA_ROOT
    / "misc-csv"
    / "csv_2"
    / "All-Star Selections.csv",
    "staging_end_season_teams": DATA_ROOT
    / "misc-csv"
    / "csv_2"
    / "End of Season Teams.csv",
    "staging_team_totals": DATA_ROOT / "misc-csv" / "csv_2" / "Team Totals.csv",
    "staging_team_summaries": DATA_ROOT / "misc-csv" / "csv_2" / "Team Summaries.csv",
    "staging_nba_championships": DATA_ROOT
    / "misc-csv"
    / "csv_4"
    / "nba_championships.csv",
    "staging_nba_players": DATA_ROOT / "misc-csv" / "csv_4" / "nba_players.csv",
}

SCHEDULE_SOURCES = [
    DATA_ROOT / "misc-csv" / "csv_1" / "LeagueSchedule24_25.csv",
    DATA_ROOT / "misc-csv" / "csv_1" / "LeagueSchedule25_26.csv",
]

PLAY_BY_PLAY_SOURCE = DATA_ROOT / "misc-csv" / "csv_3" / "play_by_play.csv"

COPY_BATCH_SIZE = 10_000


def _load_staging_tables(session: Session, import_batch_id: UUID) -> None:
    for table_name in STAGING_TABLES:
        csv_path = CSV_SOURCES.get(table_name)
        if not csv_path or not csv_path.exists():
            continue

        logger.info(
            "Loading CSV to staging (DuckDB)", table=table_name, path=str(csv_path)
        )

        session.execute(text(f"DELETE FROM {table_name}"))
        session.execute(text(f"TRUNCATE TABLE {table_name}"))

        sql = f"""
            INSERT INTO {table_name} 
            SELECT 
                *, 
                '{str(import_batch_id)}' as import_batch_id, 
                NULL as validation_errors 
            FROM read_csv('{csv_path.as_posix()}', all_varchar=True, auto_detect=True, header=True)
        """
        session.execute(text(sql))


def _validate_staging(session: Session) -> None:
    pass


def _upsert_franchises(session: Session) -> None:
    session.execute(
        text(
            """
            INSERT INTO franchise (name, founded_year, defunct_year, city)
            SELECT DISTINCT
                concat_ws(' ', team_city, team_name) AS name,
                TRY_CAST(NULLIF(season_founded, '') AS int) AS founded_year,
                TRY_CAST(NULLIF(season_active_till, '') AS int) AS defunct_year,
                NULLIF(team_city, '') AS city
            FROM staging_team_histories
            WHERE (validation_errors IS NULL)
              AND NULLIF(team_city, '') IS NOT NULL
              AND NULLIF(team_name, '') IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM franchise f
                  WHERE f.name = concat_ws(' ', team_city, team_name)
              );
            """
        )
    )


def _upsert_teams(session: Session) -> None:
    session.execute(
        text(
            """
            WITH latest_by_team AS (
                SELECT DISTINCT ON (TRY_CAST(NULLIF(team_id, '') AS int))
                    TRY_CAST(NULLIF(team_id, '') AS int) AS team_id,
                    team_name,
                    trim(team_abbrev) AS team_abbrev,
                    TRY_CAST(NULLIF(season_founded, '') AS int) AS founded_year,
                    TRY_CAST(NULLIF(season_active_till, '') AS int) AS defunct_year,
                    f.franchise_id,
                    CASE
                        WHEN NULLIF(season_active_till, '') IS NULL THEN true
                        WHEN TRY_CAST(NULLIF(season_active_till, '') AS int)
                            >= EXTRACT(YEAR FROM CURRENT_DATE)::int THEN true
                        ELSE false
                    END AS is_active,
                    CASE
                        WHEN NULLIF(season_active_till, '') IS NULL THEN false
                        WHEN TRY_CAST(NULLIF(season_active_till, '') AS int)
                            >= EXTRACT(YEAR FROM CURRENT_DATE)::int THEN false
                        ELSE true
                    END AS is_defunct,
                    NULLIF(team_city, '') AS city
                FROM staging_team_histories sth
                JOIN franchise f
                  ON f.name = concat_ws(' ', sth.team_city, sth.team_name)
                WHERE (validation_errors IS NULL)
                  AND NULLIF(team_id, '') IS NOT NULL
                  AND NULLIF(trim(team_abbrev), '') IS NOT NULL
                  AND NULLIF(team_city, '') IS NOT NULL
                  AND NULLIF(team_name, '') IS NOT NULL
                  AND team_city <> 'All-Star'
                  AND league IN ('NBA', 'BAA', 'ABA', 'NBL')
                ORDER BY
                    TRY_CAST(NULLIF(team_id, '') AS int),
                    TRY_CAST(NULLIF(season_active_till, '') AS int) DESC,
                    TRY_CAST(NULLIF(season_founded, '') AS int) DESC
            ),
            latest_by_abbrev AS (
                SELECT DISTINCT ON (team_abbrev)
                    team_id,
                    team_name,
                    team_abbrev,
                    founded_year,
                    defunct_year,
                    franchise_id,
                    is_active,
                    is_defunct,
                    city
                FROM latest_by_team
                ORDER BY
                    team_abbrev,
                    defunct_year DESC,
                    founded_year DESC
            )
            INSERT INTO team (
                team_id,
                name,
                abbreviation,
                founded_year,
                defunct_year,
                franchise_id,
                is_active,
                is_defunct,
                city
            )
            SELECT
                team_id,
                team_name,
                team_abbrev,
                founded_year,
                defunct_year,
                franchise_id,
                is_active,
                is_defunct,
                city
            FROM latest_by_abbrev
            ON CONFLICT (abbreviation) DO UPDATE SET
                name = EXCLUDED.name,
                abbreviation = EXCLUDED.abbreviation,
                founded_year = EXCLUDED.founded_year,
                defunct_year = EXCLUDED.defunct_year,
                franchise_id = EXCLUDED.franchise_id,
                is_active = EXCLUDED.is_active,
                is_defunct = EXCLUDED.is_defunct,
                city = EXCLUDED.city;
            """
        )
    )


def _upsert_players(session: Session) -> None:
    session.execute(
        text(
            """
            WITH player_source AS (
                SELECT
                    TRY_CAST(NULLIF(person_id, '') AS int) AS player_id,
                    first_name,
                    last_name,
                    TRY_CAST(NULLIF(birthdate, '') AS date) AS birth_date,
                    NULLIF(country, '') AS birth_place_country,
                    TRY_CAST(NULLIF(height, '') AS numeric) AS height_inches,
                    TRY_CAST(NULLIF(body_weight, '') AS int) AS weight_lbs,
                    CASE
                        WHEN guard IN ('1', 'true', 'TRUE') THEN 'GUARD'
                        WHEN forward IN ('1', 'true', 'TRUE') THEN 'FORWARD'
                        WHEN center IN ('1', 'true', 'TRUE') THEN 'CENTER'
                        ELSE NULL
                    END AS position,
                    TRY_CAST(NULLIF(draft_year, '') AS int) AS draft_year,
                    TRY_CAST(NULLIF(draft_number, '') AS int) AS draft_pick,
                    lower(COALESCE(last_name, '')) AS last_name_lower,
                    lower(COALESCE(first_name, '')) AS first_name_lower
                FROM staging_players
                WHERE (validation_errors IS NULL)
                  AND NULLIF(person_id, '') IS NOT NULL
            ),
            player_slugs AS (
                SELECT
                    player_id,
                    first_name,
                    last_name,
                    birth_date,
                    birth_place_country,
                    height_inches,
                    weight_lbs,
                    position,
                    draft_year,
                    draft_pick,
                    substring(last_name_lower, 1, 5)
                        || substring(first_name_lower, 1, 2)
                        || lpad(
                            row_number() OVER (
                                PARTITION BY
                                    substring(last_name_lower, 1, 5),
                                    substring(first_name_lower, 1, 2)
                                ORDER BY player_id
                            )::text,
                            2,
                            '0'
                        ) AS slug
                FROM player_source
            )
            INSERT INTO player (
                player_id,
                slug,
                first_name,
                last_name,
                birth_date,
                birth_place_country,
                height_inches,
                weight_lbs,
                position,
                draft_year,
                draft_pick,
                is_active
            )
            SELECT
                player_id,
                slug,
                first_name,
                last_name,
                birth_date,
                birth_place_country,
                height_inches,
                weight_lbs,
                CAST(position AS player_position),
                draft_year,
                draft_pick,
                true AS is_active
            FROM player_slugs
            ON CONFLICT (player_id) DO UPDATE SET
                slug = EXCLUDED.slug,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                birth_date = EXCLUDED.birth_date,
                birth_place_country = EXCLUDED.birth_place_country,
                height_inches = EXCLUDED.height_inches,
                weight_lbs = EXCLUDED.weight_lbs,
                position = EXCLUDED.position,
                draft_year = EXCLUDED.draft_year,
                draft_pick = EXCLUDED.draft_pick,
                is_active = EXCLUDED.is_active;
            """
        )
    )


def _upsert_seasons_from_games(session: Session) -> int:
    from app.ingestion.repositories import get_or_create_league

    league_id = get_or_create_league(session)
    result = session.execute(
        text(
            """
            WITH game_dates AS (
                SELECT DISTINCT
                    TRY_CAST(NULLIF(game_date_time_est, '') AS timestamp) AS game_ts
                FROM staging_games
                WHERE NULLIF(game_date_time_est, '') IS NOT NULL
            ),
            seasons AS (
                SELECT DISTINCT
                    CASE
                        WHEN EXTRACT(MONTH FROM game_ts) >= 10
                            THEN EXTRACT(YEAR FROM game_ts)::int + 1
                        ELSE EXTRACT(YEAR FROM game_ts)::int
                    END AS season_year
                FROM game_dates
                WHERE game_ts IS NOT NULL
            )
            INSERT INTO season (
                league_id,
                year,
                season_name,
                start_date,
                end_date,
                is_active
            )
            SELECT
                :league_id,
                season_year,
                concat(season_year - 1, '-', right(season_year::text, 2)),
                make_date(season_year - 1, 10, 1),
                make_date(season_year, 6, 30),
                season_year >= EXTRACT(YEAR FROM CURRENT_DATE)
            FROM seasons s
            WHERE NOT EXISTS (
                SELECT 1 FROM season se WHERE se.year = s.season_year
            )
            RETURNING season_id;
            """
        ),
        {"league_id": league_id},
    )
    return len(result.fetchall())


def _upsert_games(session: Session) -> None:
    session.execute(
        text(
            """
            INSERT INTO game (
                game_id,
                season_id,
                game_date,
                game_time,
                home_team_id,
                away_team_id,
                home_score,
                away_score,
                season_type,
                attendance,
                arena
            )
            SELECT
                TRY_CAST(NULLIF(game_id, '') AS int) AS game_id,
                se.season_id,
                (TRY_CAST(NULLIF(game_date_time_est, '') AS timestamp))::date AS game_date,
                (TRY_CAST(NULLIF(game_date_time_est, '') AS timestamp))::time AS game_time,
                TRY_CAST(NULLIF(hometeam_id, '') AS int) AS home_team_id,
                TRY_CAST(NULLIF(awayteam_id, '') AS int) AS away_team_id,
                TRY_CAST(NULLIF(home_score, '') AS int) AS home_score,
                TRY_CAST(NULLIF(away_score, '') AS int) AS away_score,
                CASE
                    WHEN game_type ILIKE '%playoff%' THEN 'PLAYOFF'
                    ELSE 'REGULAR'
                END AS season_type,
                TRY_CAST(NULLIF(attendance, '') AS int) AS attendance,
                NULLIF(arena_id, '') AS arena
            FROM staging_games sg
            JOIN season se
              ON se.year = CASE
                  WHEN EXTRACT(MONTH FROM TRY_CAST(sg.game_date_time_est AS timestamp)) >= 10
                      THEN EXTRACT(YEAR FROM TRY_CAST(sg.game_date_time_est AS timestamp))::int + 1
                  ELSE EXTRACT(YEAR FROM TRY_CAST(sg.game_date_time_est AS timestamp))::int
              END
            WHERE (validation_errors IS NULL)
              AND NULLIF(game_id, '') IS NOT NULL
            ON CONFLICT (game_id) DO UPDATE SET
                game_date = EXCLUDED.game_date,
                game_time = EXCLUDED.game_time,
                home_team_id = EXCLUDED.home_team_id,
                away_team_id = EXCLUDED.away_team_id,
                home_score = COALESCE(game.home_score, EXCLUDED.home_score),
                away_score = COALESCE(game.away_score, EXCLUDED.away_score),
                season_type = EXCLUDED.season_type,
                attendance = COALESCE(game.attendance, EXCLUDED.attendance),
                arena = COALESCE(game.arena, EXCLUDED.arena);
            """
        )
    )


def _upsert_schedule_games(session: Session) -> None:
    from app.ingestion.repositories import get_or_create_season

    existing_team_ids = {
        row[0]
        for row in (session.execute(text("SELECT team_id FROM team"))).all()
        if row[0] is not None
    }
    missing_schedule_team_ids: set[int] = set()

    for schedule_path in SCHEDULE_SOURCES:
        if not schedule_path.exists():
            logger.warning("Schedule CSV missing", path=str(schedule_path))
            continue

        with schedule_path.open("r", encoding="utf-8") as file_handle:
            reader = csv.DictReader(file_handle)
            for row in reader:
                game_id = row.get("gameId")
                date_time = row.get("gameDateTimeEst")
                home_team_raw = row.get("hometeamId")
                away_team_raw = row.get("awayteamId")
                if not game_id or not date_time:
                    continue
                if not home_team_raw or not away_team_raw:
                    continue
                home_team_id = int(home_team_raw)
                away_team_id = int(away_team_raw)
                if (
                    home_team_id not in existing_team_ids
                    or away_team_id not in existing_team_ids
                ):
                    if home_team_id not in existing_team_ids:
                        missing_schedule_team_ids.add(home_team_id)
                    if away_team_id not in existing_team_ids:
                        missing_schedule_team_ids.add(away_team_id)
                    continue
                normalized_dt = date_time.replace("Z", "+00:00")
                try:
                    parsed_dt = datetime.fromisoformat(normalized_dt)
                except ValueError:
                    try:
                        parsed_dt = datetime.fromisoformat(
                            normalized_dt.replace(" ", "T")
                        )
                    except ValueError:
                        continue
                game_ts = parsed_dt.date()
                season_end_year = (
                    game_ts.year + 1 if game_ts.month >= 10 else game_ts.year
                )
                season_id = get_or_create_season(session, season_end_year)
                game_time_value = parsed_dt.time()
                if game_time_value.tzinfo is not None:
                    game_time_value = game_time_value.replace(tzinfo=None)

                session.execute(
                    text(
                        """
                        INSERT INTO game (
                            game_id,
                            season_id,
                            game_date,
                            game_time,
                            home_team_id,
                            away_team_id,
                            season_type
                        )
                        VALUES (
                            :game_id,
                            :season_id,
                            :game_date,
                            :game_time,
                            :home_team_id,
                            :away_team_id,
                            'REGULAR'
                        )
                        ON CONFLICT (game_id) DO UPDATE SET
                            game_date = EXCLUDED.game_date,
                            game_time = COALESCE(game.game_time, EXCLUDED.game_time),
                            home_team_id = COALESCE(
                                game.home_team_id, EXCLUDED.home_team_id
                            ),
                            away_team_id = COALESCE(
                                game.away_team_id, EXCLUDED.away_team_id
                            );
                        """
                    ),
                    {
                        "game_id": int(game_id),
                        "season_id": season_id,
                        "game_date": game_ts,
                        "game_time": game_time_value,
                        "home_team_id": home_team_id,
                        "away_team_id": away_team_id,
                    },
                )
    if missing_schedule_team_ids:
        logger.warning(
            "Skipping schedule games with unknown teams",
            team_ids=sorted(missing_schedule_team_ids),
        )


def _upsert_box_scores(session: Session) -> None:
    session.execute(
        text(
            """
            INSERT INTO box_score (
                game_id,
                team_id,
                opponent_team_id,
                location,
                outcome,
                seconds_played,
                made_fg,
                attempted_fg,
                made_3pt,
                attempted_3pt,
                made_ft,
                attempted_ft,
                offensive_rebounds,
                defensive_rebounds,
                total_rebounds,
                assists,
                steals,
                blocks,
                turnovers,
                personal_fouls,
                points_scored,
                plus_minus,
                field_goal_percentage,
                three_point_percentage,
                free_throw_percentage,
                quarter_scores
            )
            SELECT
                TRY_CAST(NULLIF(game_id, '') AS int) AS game_id,
                TRY_CAST(NULLIF(team_id, '') AS int) AS team_id,
                TRY_CAST(NULLIF(opponent_team_id, '') AS int) AS opponent_team_id,
                CAST(CASE WHEN home = '1' THEN 'HOME' ELSE 'AWAY' END AS location) AS location,
                CAST(CASE WHEN win = '1' THEN 'WIN' ELSE 'LOSS' END AS outcome) AS outcome,
                ROUND(TRY_CAST(NULLIF(num_minutes, '') AS numeric) * 60) AS seconds_played,
                COALESCE(TRY_CAST(NULLIF(field_goals_made, '') AS numeric), 0)::int AS made_fg,
                COALESCE(TRY_CAST(NULLIF(field_goals_attempted, '') AS numeric), 0)::int AS attempted_fg,
                COALESCE(TRY_CAST(NULLIF(three_pointers_made, '') AS numeric), 0)::int AS made_3pt,
                COALESCE(TRY_CAST(NULLIF(three_pointers_attempted, '') AS numeric), 0)::int AS attempted_3pt,
                COALESCE(TRY_CAST(NULLIF(free_throws_made, '') AS numeric), 0)::int AS made_ft,
                COALESCE(TRY_CAST(NULLIF(free_throws_attempted, '') AS numeric), 0)::int AS attempted_ft,
                COALESCE(TRY_CAST(NULLIF(rebounds_offensive, '') AS numeric), 0)::int AS offensive_rebounds,
                COALESCE(TRY_CAST(NULLIF(rebounds_defensive, '') AS numeric), 0)::int AS defensive_rebounds,
                TRY_CAST(NULLIF(rebounds_total, '') AS numeric)::int AS total_rebounds,
                COALESCE(TRY_CAST(NULLIF(assists, '') AS numeric), 0)::int AS assists,
                COALESCE(TRY_CAST(NULLIF(steals, '') AS numeric), 0)::int AS steals,
                COALESCE(TRY_CAST(NULLIF(blocks, '') AS numeric), 0)::int AS blocks,
                COALESCE(TRY_CAST(NULLIF(turnovers, '') AS numeric), 0)::int AS turnovers,
                COALESCE(TRY_CAST(NULLIF(fouls_personal, '') AS numeric), 0)::int AS personal_fouls,
                COALESCE(TRY_CAST(NULLIF(team_score, '') AS numeric), 0)::int AS points_scored,
                TRY_CAST(NULLIF(plus_minus_points, '') AS numeric)::int AS plus_minus,
                CASE
                    WHEN TRY_CAST(NULLIF(field_goals_attempted, '') AS numeric) > 0
                        THEN ROUND(
                            TRY_CAST(NULLIF(field_goals_made, '') AS numeric)
                            / TRY_CAST(NULLIF(field_goals_attempted, '') AS numeric),
                            3
                        )
                    ELSE NULL
                END AS field_goal_percentage,
                CASE
                    WHEN TRY_CAST(NULLIF(three_pointers_attempted, '') AS numeric) > 0
                        THEN ROUND(
                            TRY_CAST(NULLIF(three_pointers_made, '') AS numeric)
                            / TRY_CAST(NULLIF(three_pointers_attempted, '') AS numeric),
                            3
                        )
                    ELSE NULL
                END AS three_point_percentage,
                CASE
                    WHEN TRY_CAST(NULLIF(free_throws_attempted, '') AS numeric) > 0
                        THEN ROUND(
                            TRY_CAST(NULLIF(free_throws_made, '') AS numeric)
                            / TRY_CAST(NULLIF(free_throws_attempted, '') AS numeric),
                            3
                        )
                    ELSE NULL
                END AS free_throw_percentage,
                json_object(
                    '1', TRY_CAST(NULLIF(q1_points, '') AS numeric)::int,
                    '2', TRY_CAST(NULLIF(q2_points, '') AS numeric)::int,
                    '3', TRY_CAST(NULLIF(q3_points, '') AS numeric)::int,
                    '4', TRY_CAST(NULLIF(q4_points, '') AS numeric)::int
                ) AS quarter_scores
            FROM staging_team_statistics sts
            WHERE (validation_errors IS NULL)
              AND NULLIF(game_id, '') IS NOT NULL
              AND NULLIF(team_id, '') IS NOT NULL
              AND EXISTS (
                  SELECT 1 FROM game g
                  WHERE g.game_id = TRY_CAST(NULLIF(sts.game_id, '') AS int)
              )
              AND NOT EXISTS (
                  SELECT 1 FROM box_score bs
                  WHERE bs.game_id = TRY_CAST(NULLIF(sts.game_id, '') AS int)
                    AND bs.team_id = TRY_CAST(NULLIF(sts.team_id, '') AS int)
              );
            """
        )
    )


def _upsert_player_box_scores(session: Session) -> None:
    session.execute(
        text(
            """
            INSERT INTO player_box_score (
                player_id,
                box_id,
                game_id,
                team_id,
                player_slug,
                player_name,
                position,
                is_starter,
                seconds_played,
                made_fg,
                attempted_fg,
                made_3pt,
                attempted_3pt,
                made_ft,
                attempted_ft,
                offensive_rebounds,
                defensive_rebounds,
                assists,
                steals,
                blocks,
                turnovers,
                personal_fouls,
                points_scored,
                plus_minus
            )
            SELECT
                p.player_id,
                bs.box_id,
                TRY_CAST(NULLIF(sps.game_id, '') AS int) AS game_id,
                t.team_id,
                p.slug,
                concat(p.first_name, ' ', p.last_name) AS player_name,
                p.position,
                false AS is_starter,
                COALESCE(
                    CASE
                        WHEN sps.num_minutes LIKE '%:%' THEN
                            TRY_CAST(split_part(sps.num_minutes, ':', 1) AS int) * 60
                            + TRY_CAST(split_part(sps.num_minutes, ':', 2) AS int)
                        WHEN NULLIF(sps.num_minutes, '') IS NOT NULL THEN
                            ROUND(TRY_CAST(NULLIF(sps.num_minutes, '') AS numeric) * 60)
                        ELSE NULL
                    END,
                    0
                ) AS seconds_played,
                COALESCE(TRY_CAST(NULLIF(sps.field_goals_made, '') AS numeric), 0)::int AS made_fg,
                COALESCE(TRY_CAST(NULLIF(sps.field_goals_attempted, '') AS numeric), 0)::int AS attempted_fg,
                COALESCE(TRY_CAST(NULLIF(sps.three_pointers_made, '') AS numeric), 0)::int AS made_3pt,
                COALESCE(TRY_CAST(NULLIF(sps.three_pointers_attempted, '') AS numeric), 0)::int AS attempted_3pt,
                COALESCE(TRY_CAST(NULLIF(sps.free_throws_made, '') AS numeric), 0)::int AS made_ft,
                COALESCE(TRY_CAST(NULLIF(sps.free_throws_attempted, '') AS numeric), 0)::int AS attempted_ft,
                COALESCE(TRY_CAST(NULLIF(sps.rebounds_offensive, '') AS numeric), 0)::int AS offensive_rebounds,
                COALESCE(TRY_CAST(NULLIF(sps.rebounds_defensive, '') AS numeric), 0)::int AS defensive_rebounds,
                COALESCE(TRY_CAST(NULLIF(sps.assists, '') AS numeric), 0)::int AS assists,
                COALESCE(TRY_CAST(NULLIF(sps.steals, '') AS numeric), 0)::int AS steals,
                COALESCE(TRY_CAST(NULLIF(sps.blocks, '') AS numeric), 0)::int AS blocks,
                COALESCE(TRY_CAST(NULLIF(sps.turnovers, '') AS numeric), 0)::int AS turnovers,
                COALESCE(TRY_CAST(NULLIF(sps.fouls_personal, '') AS numeric), 0)::int AS personal_fouls,
                COALESCE(TRY_CAST(NULLIF(sps.points, '') AS numeric), 0)::int AS points_scored,
                TRY_CAST(NULLIF(sps.plus_minus_points, '') AS numeric)::int AS plus_minus
            FROM staging_player_statistics sps
            JOIN player p
              ON p.player_id = TRY_CAST(NULLIF(sps.person_id, '') AS int)
            JOIN team t
              ON regexp_replace(lower(t.city || t.name), '[^a-z0-9]', '', 'g')
                = regexp_replace(
                    lower(sps.playerteam_city || sps.playerteam_name),
                    '[^a-z0-9]',
                    '',
                    'g'
                )
            JOIN box_score bs
              ON bs.game_id = TRY_CAST(NULLIF(sps.game_id, '') AS int)
             AND bs.team_id = t.team_id
            WHERE (sps.validation_errors IS NULL)
              AND NULLIF(sps.game_id, '') IS NOT NULL
            ON CONFLICT (player_id, box_id) DO UPDATE SET
                seconds_played = EXCLUDED.seconds_played,
                made_fg = EXCLUDED.made_fg,
                attempted_fg = EXCLUDED.attempted_fg,
                made_3pt = EXCLUDED.made_3pt,
                attempted_3pt = EXCLUDED.attempted_3pt,
                made_ft = EXCLUDED.made_ft,
                attempted_ft = EXCLUDED.attempted_ft,
                offensive_rebounds = EXCLUDED.offensive_rebounds,
                defensive_rebounds = EXCLUDED.defensive_rebounds,
                assists = EXCLUDED.assists,
                steals = EXCLUDED.steals,
                blocks = EXCLUDED.blocks,
                turnovers = EXCLUDED.turnovers,
                personal_fouls = EXCLUDED.personal_fouls,
                points_scored = EXCLUDED.points_scored,
                plus_minus = EXCLUDED.plus_minus;
            """
        )
    )


def _upsert_player_season_totals(session: Session) -> None:
    session.execute(
        text(
            """
            WITH ranked AS (
                SELECT
                    pt.*,
                    CASE WHEN team IN ('TOT', '2TM', '3TM') THEN 1 ELSE 0 END AS is_combined,
                    ROW_NUMBER() OVER (
                        PARTITION BY player_id, season
                        ORDER BY CASE WHEN team IN ('TOT', '2TM', '3TM') THEN 0 ELSE 1 END
                    ) AS rn
                FROM staging_player_totals pt
                WHERE (validation_errors IS NULL)
            )
            INSERT INTO player_season (
                player_id,
                season_id,
                season_type,
                team_id,
                player_age,
                position,
                games_played,
                games_started,
                minutes_played,
                made_fg,
                attempted_fg,
                made_3pt,
                attempted_3pt,
                made_ft,
                attempted_ft,
                offensive_rebounds,
                defensive_rebounds,
                total_rebounds,
                assists,
                steals,
                blocks,
                turnovers,
                personal_fouls,
                points_scored,
                double_doubles,
                triple_doubles,
                is_combined_totals
            )
            SELECT
                p.player_id,
                se.season_id,
                CAST('REGULAR' AS seasontype),
                CASE WHEN r.is_combined = 1 THEN NULL ELSE t.team_id END,
                TRY_CAST(NULLIF(NULLIF(trim(r.age), ''), 'NA') AS numeric)::int,
                CAST(CASE
                    WHEN r.pos ILIKE 'PG' THEN 'POINT_GUARD'
                    WHEN r.pos ILIKE 'SG' THEN 'SHOOTING_GUARD'
                    WHEN r.pos ILIKE 'SF' THEN 'SMALL_FORWARD'
                    WHEN r.pos ILIKE 'PF' THEN 'POWER_FORWARD'
                    WHEN r.pos ILIKE 'C' THEN 'CENTER'
                    WHEN r.pos ILIKE 'G' THEN 'GUARD'
                    WHEN r.pos ILIKE 'F' THEN 'FORWARD'
                    WHEN r.pos ILIKE 'G-F' THEN 'GUARD'
                    WHEN r.pos ILIKE 'F-G' THEN 'FORWARD'
                    WHEN r.pos ILIKE 'F-C' THEN 'FORWARD'
                    WHEN r.pos ILIKE 'C-F' THEN 'CENTER'
                    ELSE NULL
                END AS player_position),
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.g), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.gs), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.mp), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.fg), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.fga), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.x3p), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.x3pa), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.ft), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.fta), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.orb), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.drb), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.trb), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.ast), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.stl), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.blk), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.tov), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.pf), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.pts), ''), 'NA') AS numeric), 0)::int,
                COALESCE(TRY_CAST(NULLIF(NULLIF(trim(r.trp_dbl), ''), 'NA') AS numeric), 0)::int,
                0,
                CASE WHEN r.is_combined = 1 THEN true ELSE false END
            FROM ranked r
            JOIN player p ON p.player_id = TRY_CAST(r.player_id AS int)
            JOIN season se ON se.year = TRY_CAST(r.season AS int)
            LEFT JOIN team t ON t.abbreviation = CASE
                WHEN r.team = 'CHO' THEN 'CHA'
                WHEN r.team = 'BRK' THEN 'BKN'
                WHEN r.team = 'PHO' THEN 'PHX'
                ELSE r.team
            END
            WHERE r.rn = 1
            ON CONFLICT (player_id, season_id, season_type) DO UPDATE SET
                games_played = EXCLUDED.games_played,
                games_started = EXCLUDED.games_started,
                minutes_played = EXCLUDED.minutes_played,
                made_fg = EXCLUDED.made_fg,
                attempted_fg = EXCLUDED.attempted_fg,
                made_3pt = EXCLUDED.made_3pt,
                attempted_3pt = EXCLUDED.attempted_3pt,
                made_ft = EXCLUDED.made_ft,
                attempted_ft = EXCLUDED.attempted_ft,
                offensive_rebounds = EXCLUDED.offensive_rebounds,
                defensive_rebounds = EXCLUDED.defensive_rebounds,
                total_rebounds = EXCLUDED.total_rebounds,
                assists = EXCLUDED.assists,
                steals = EXCLUDED.steals,
                blocks = EXCLUDED.blocks,
                turnovers = EXCLUDED.turnovers,
                personal_fouls = EXCLUDED.personal_fouls,
                points_scored = EXCLUDED.points_scored,
                is_combined_totals = EXCLUDED.is_combined_totals;
            """
        )
    )


def _upsert_player_season_advanced(session: Session) -> None:
    session.execute(
        text(
            """
            WITH ranked AS (
                SELECT
                    psa.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY player_id, season
                        ORDER BY CASE WHEN team IN ('TOT', '2TM', '3TM') THEN 0 ELSE 1 END
                    ) AS rn
                FROM staging_player_advanced psa
                WHERE (validation_errors IS NULL)
            )
            INSERT INTO player_season_advanced (
                player_id, season_id, season_type, team_id,
                player_age, games_played, minutes_played,
                player_efficiency_rating, true_shooting_percentage,
                three_point_attempt_rate, free_throw_attempt_rate, usage_percentage,
                offensive_win_shares, defensive_win_shares, win_shares, win_shares_per_48,
                offensive_box_plus_minus, defensive_box_plus_minus, box_plus_minus,
                value_over_replacement_player
            )
            SELECT
                p.player_id,
                se.season_id,
                CAST('REGULAR' AS seasontype),
                t.team_id,
                TRY_CAST(NULLIF(trim(r.age), '') AS int),
                COALESCE(TRY_CAST(NULLIF(trim(r.g), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(r.mp), '') AS int), 0),
                TRY_CAST(NULLIF(trim(r.per), '') AS numeric),
                TRY_CAST(NULLIF(trim(r.ts_percent), '') AS numeric),
                TRY_CAST(NULLIF(trim(r.x3p_ar), '') AS numeric),
                TRY_CAST(NULLIF(trim(r.f_tr), '') AS numeric),
                TRY_CAST(NULLIF(trim(r.usg_percent), '') AS numeric),
                TRY_CAST(NULLIF(trim(r.ows), '') AS numeric),
                TRY_CAST(NULLIF(trim(r.dws), '') AS numeric),
                TRY_CAST(NULLIF(trim(r.ws), '') AS numeric),
                TRY_CAST(NULLIF(trim(r.ws_48), '') AS numeric),
                TRY_CAST(NULLIF(trim(r.obpm), '') AS numeric),
                TRY_CAST(NULLIF(trim(r.dbpm), '') AS numeric),
                TRY_CAST(NULLIF(trim(r.bpm), '') AS numeric),
                TRY_CAST(NULLIF(trim(r.vorp), '') AS numeric)
            FROM ranked r
            JOIN player p ON p.player_id = TRY_CAST(r.player_id AS int)
            JOIN season se ON se.year = TRY_CAST(r.season AS int)
            LEFT JOIN team t ON t.abbreviation = CASE
                    WHEN r.team = 'CHO' THEN 'CHA'
                    WHEN r.team = 'BRK' THEN 'BKN'
                    WHEN r.team = 'PHO' THEN 'PHX'
                    ELSE r.team
                END
            WHERE r.rn = 1
            ON CONFLICT (player_id, season_id, season_type) DO UPDATE SET
                player_efficiency_rating = EXCLUDED.player_efficiency_rating,
                true_shooting_percentage = EXCLUDED.true_shooting_percentage,
                win_shares = EXCLUDED.win_shares,
                box_plus_minus = EXCLUDED.box_plus_minus,
                value_over_replacement_player = EXCLUDED.value_over_replacement_player;
            """
        )
    )


def _upsert_team_totals(session: Session) -> None:
    session.execute(
        text(
            """
            INSERT INTO team_season (
                team_id, season_id, season_type,
                games_played, minutes_played,
                made_fg, attempted_fg, made_3pt, attempted_3pt,
                made_ft, attempted_ft,
                offensive_rebounds, defensive_rebounds, total_rebounds,
                assists, steals, blocks, turnovers, personal_fouls,
                points_scored
            )
            SELECT
                t.team_id,
                se.season_id,
                'REGULAR',
                COALESCE(TRY_CAST(NULLIF(trim(tt.g), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.mp), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.fg), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.fga), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.x3p), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.x3pa), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.ft), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.fta), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.orb), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.drb), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.trb), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.ast), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.stl), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.blk), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.tov), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.pf), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(tt.pts), '') AS int), 0)
            FROM staging_team_totals tt
            JOIN season se ON se.year = TRY_CAST(tt.season AS int)
            JOIN team t ON t.abbreviation = tt.abbreviation
            WHERE (validation_errors IS NULL)
            ON CONFLICT (team_id, season_id, season_type) DO UPDATE SET
                games_played = EXCLUDED.games_played,
                points_scored = EXCLUDED.points_scored,
                wins = team_season.wins, -- preserve existing
                losses = team_season.losses; -- preserve existing
            """
        )
    )


def _upsert_team_summaries(session: Session) -> None:
    session.execute(
        text(
            """
            INSERT INTO team_season (
                team_id, season_id, season_type,
                wins, losses,
                points_per_game, points_allowed_per_game,
                offensive_rating, defensive_rating, net_rating,
                pace
            )
            SELECT
                t.team_id,
                se.season_id,
                'REGULAR',
                COALESCE(TRY_CAST(NULLIF(trim(ts.w), '') AS int), 0),
                COALESCE(TRY_CAST(NULLIF(trim(ts.l), '') AS int), 0),
                TRY_CAST(NULLIF(trim(ts.pw), '') AS numeric),
                TRY_CAST(NULLIF(trim(ts.pl), '') AS numeric),
                TRY_CAST(NULLIF(trim(ts.o_rtg), '') AS numeric),
                TRY_CAST(NULLIF(trim(ts.d_rtg), '') AS numeric),
                TRY_CAST(NULLIF(trim(ts.n_rtg), '') AS numeric),
                TRY_CAST(NULLIF(trim(ts.pace), '') AS numeric)
            FROM staging_team_summaries ts
            JOIN season se ON se.year = TRY_CAST(ts.season AS int)
            JOIN team t ON t.abbreviation = ts.abbreviation
            WHERE (validation_errors IS NULL)
            ON CONFLICT (team_id, season_id, season_type) DO UPDATE SET
                wins = EXCLUDED.wins,
                losses = EXCLUDED.losses,
                offensive_rating = EXCLUDED.offensive_rating,
                defensive_rating = EXCLUDED.defensive_rating,
                net_rating = EXCLUDED.net_rating,
                pace = EXCLUDED.pace;
            """
        )
    )


def run_ingestion_sync(import_batch_id: UUID) -> None:
    """Synchronous ingestion entry point for Celery."""
    logger.info("Starting ingestion task", batch_id=str(import_batch_id))

    with session_factory() as session:
        try:
            # 1. Load CSVs to staging
            _load_staging_tables(session, import_batch_id)

            # 2. Validate (Simplified/Skipped for DuckDB transition)
            _validate_staging(session)

            # 3. Upsert core entities
            _upsert_franchises(session)
            _upsert_teams(session)
            _upsert_players(session)
            _upsert_seasons_from_games(session)
            _upsert_games(session)
            _upsert_schedule_games(session)

            # 4. Upsert stats
            _upsert_box_scores(session)
            _upsert_player_box_scores(session)
            _upsert_player_season_totals(session)

            _upsert_player_season_advanced(session)
            _upsert_team_totals(session)
            _upsert_team_summaries(session)

            session.commit()
            logger.info("Ingestion complete")
        except Exception as e:
            session.rollback()
            logger.exception("Ingestion failed", error=str(e))
            raise e


@celery_app.task
def ingest_data_task() -> str:
    batch_id = uuid4()
    run_ingestion_sync(batch_id)
    return str(batch_id)
