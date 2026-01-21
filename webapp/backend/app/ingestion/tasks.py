"""Celery tasks for data ingestion from the scraper.

These tasks run periodically or on-demand to fetch data from
basketball-reference.com and persist it to our database.
"""

import asyncio
import csv
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import asyncpg
import structlog
from sqlalchemy import delete, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.data import TEAM_TO_TEAM_ABBREVIATION

from app.celery_app import celery_app
from app.core.config import settings
from app.db.session import async_session_factory
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

CSV_SOURCES: dict[str, Path] = {
    "staging_players": Path("raw-data/misc-csv/csv_1/Players.csv"),
    "staging_games": Path("raw-data/misc-csv/csv_1/Games.csv"),
    "staging_team_histories": Path("raw-data/misc-csv/csv_1/TeamHistories.csv"),
    "staging_player_statistics": Path("raw-data/misc-csv/csv_1/PlayerStatistics.csv"),
    "staging_team_statistics": Path("raw-data/misc-csv/csv_1/TeamStatistics.csv"),
    "staging_player_totals": Path("raw-data/misc-csv/csv_2/Player Totals.csv"),
    "staging_player_advanced": Path("raw-data/misc-csv/csv_2/Advanced.csv"),
    "staging_player_shooting": Path("raw-data/misc-csv/csv_2/Player Shooting.csv"),
    "staging_draft_pick_history": Path(
        "raw-data/misc-csv/csv_2/Draft Pick History.csv"
    ),
    "staging_all_star_selections": Path(
        "raw-data/misc-csv/csv_2/All-Star Selections.csv"
    ),
    "staging_end_season_teams": Path("raw-data/misc-csv/csv_2/End of Season Teams.csv"),
    "staging_team_totals": Path("raw-data/misc-csv/csv_2/Team Totals.csv"),
    "staging_team_summaries": Path("raw-data/misc-csv/csv_2/Team Summaries.csv"),
    "staging_nba_championships": Path("raw-data/misc-csv/csv_4/nba_championships.csv"),
    "staging_nba_players": Path("raw-data/misc-csv/csv_4/nba_players.csv"),
}

SCHEDULE_SOURCES = [
    Path("raw-data/misc-csv/csv_1/LeagueSchedule24_25.csv"),
    Path("raw-data/misc-csv/csv_1/LeagueSchedule25_26.csv"),
]

PLAY_BY_PLAY_SOURCE = Path("raw-data/misc-csv/csv_3/play_by_play.csv")

COPY_BATCH_SIZE = 10_000


def _asyncpg_dsn() -> str:
    url = make_url(settings.database_url)
    if "+asyncpg" in url.drivername:
        url = url.set(drivername="postgresql")
    return str(url)


async def _copy_csv_to_staging(
    conn: asyncpg.Connection,
    table_name: str,
    columns: list[str],
    csv_path: Path,
    import_batch_id: UUID,
) -> int:
    if not csv_path.exists():
        logger.warning("CSV source missing", table=table_name, path=str(csv_path))
        return 0

    if table_name not in ALLOWED_STAGING_TABLES:
        raise ValueError(f"Invalid staging table: {table_name}")

    await conn.execute(f"TRUNCATE TABLE {table_name};")

    inserted = 0
    with csv_path.open("r", encoding="utf-8") as file_handle:
        reader = csv.reader(file_handle)
        next(reader, None)  # skip header
        batch: list[tuple[Any, ...]] = []
        for row in reader:
            batch.append((*row, str(import_batch_id), None))
            if len(batch) >= COPY_BATCH_SIZE:
                await conn.copy_records_to_table(
                    table_name,
                    records=batch,
                    columns=[*columns, "import_batch_id", "validation_errors"],
                )
                inserted += len(batch)
                batch = []
        if batch:
            await conn.copy_records_to_table(
                table_name,
                records=batch,
                columns=[*columns, "import_batch_id", "validation_errors"],
            )
            inserted += len(batch)
    return inserted


async def _load_staging_tables(import_batch_id: UUID) -> None:
    dsn = _asyncpg_dsn()
    async with asyncpg.connect(dsn) as conn:
        for table_name, columns in STAGING_TABLES.items():
            csv_path = CSV_SOURCES.get(table_name)
            if not csv_path:
                continue
            logger.info("Copying CSV to staging", table=table_name, path=str(csv_path))
            count = await _copy_csv_to_staging(
                conn, table_name, columns, csv_path, import_batch_id
            )
            logger.info(
                "Copied CSV to staging",
                table=table_name,
                rows=count,
            )


def _validation_sql(table: str, checks: list[tuple[str, str]]) -> str:
    if table not in ALLOWED_STAGING_TABLES:
        raise ValueError(f"Invalid table: {table}")

    fields = []
    conditions = []
    for column, column_type in checks:
        if not column.isidentifier():
            raise ValueError(f"Invalid column name: {column}")
        if column_type not in ALLOWED_COLUMN_TYPES:
            raise ValueError(f"Invalid column type: {column_type}")

        fields.append(
            f"'{column}', "
            f"CASE WHEN {column} NOT IN ('', 'NA') "
            f"AND NOT pg_input_is_valid({column}, '{column_type}') "
            f"THEN 'invalid {column_type}' END"
        )
        conditions.append(
            f"({column} NOT IN ('', 'NA') AND NOT pg_input_is_valid({column}, '{column_type}'))"
        )
    if not conditions:
        return ""
    return f"""
        UPDATE {table}
        SET validation_errors = jsonb_strip_nulls(jsonb_build_object(
            {", ".join(fields)}
        ))
        WHERE {" OR ".join(conditions)};
    """


async def _validate_staging(session: AsyncSession) -> None:
    validations: dict[str, list[tuple[str, str]]] = {
        "staging_players": [
            ("birthdate", "date"),
            ("height", "numeric"),
            ("body_weight", "numeric"),
            ("draft_year", "int"),
            ("draft_number", "int"),
        ],
        "staging_games": [
            ("game_date_time_est", "timestamp"),
            ("home_score", "int"),
            ("away_score", "int"),
            ("attendance", "int"),
        ],
        "staging_player_statistics": [
            ("num_minutes", "numeric"),
            ("points", "int"),
            ("assists", "int"),
            ("blocks", "int"),
            ("steals", "int"),
        ],
        "staging_team_statistics": [
            ("num_minutes", "numeric"),
            ("team_score", "int"),
            ("opponent_score", "int"),
        ],
        "staging_player_totals": [
            ("season", "int"),
            ("g", "int"),
            ("mp", "int"),
            ("fg", "int"),
            ("fga", "int"),
        ],
        "staging_player_advanced": [
            ("season", "int"),
            ("g", "int"),
            ("mp", "int"),
        ],
        "staging_player_shooting": [
            ("season", "int"),
            ("g", "int"),
            ("mp", "int"),
        ],
        "staging_team_totals": [
            ("season", "int"),
            ("g", "int"),
            ("pts", "int"),
        ],
        "staging_team_summaries": [
            ("season", "int"),
            ("w", "int"),
            ("l", "int"),
        ],
    }

    for table, checks in validations.items():
        sql = _validation_sql(table, checks)
        if sql:
            await session.execute(text(sql))


async def _upsert_franchises(session: AsyncSession) -> None:
    await session.execute(
        text(
            """
            INSERT INTO franchise (name, founded_year, defunct_year, city)
            SELECT DISTINCT
                concat_ws(' ', team_city, team_name) AS name,
                NULLIF(season_founded, '')::int AS founded_year,
                NULLIF(season_active_till, '')::int AS defunct_year,
                NULLIF(team_city, '') AS city
            FROM staging_team_histories
            WHERE (validation_errors IS NULL OR validation_errors = '{}'::jsonb)
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


async def _upsert_teams(session: AsyncSession) -> None:
    await session.execute(
        text(
            """
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
                NULLIF(team_id, '')::int AS team_id,
                team_name,
                team_abbrev,
                NULLIF(season_founded, '')::int AS founded_year,
                NULLIF(season_active_till, '')::int AS defunct_year,
                f.franchise_id,
                CASE WHEN NULLIF(season_active_till, '') IS NULL THEN true ELSE false END,
                CASE WHEN NULLIF(season_active_till, '') IS NULL THEN false ELSE true END,
                NULLIF(team_city, '') AS city
            FROM staging_team_histories sth
            JOIN franchise f
              ON f.name = concat_ws(' ', sth.team_city, sth.team_name)
            WHERE (validation_errors IS NULL OR validation_errors = '{}'::jsonb)
              AND NULLIF(team_id, '') IS NOT NULL
            ON CONFLICT (team_id) DO UPDATE SET
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


async def _upsert_players(session: AsyncSession) -> None:
    await session.execute(
        text(
            """
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
                NULLIF(person_id, '')::int AS player_id,
                lower(last_name) || substring(lower(first_name), 1, 2) || '01' AS slug,
                first_name,
                last_name,
                NULLIF(birthdate, '')::date AS birth_date,
                NULLIF(country, '') AS birth_place_country,
                NULLIF(height, '')::numeric AS height_inches,
                NULLIF(body_weight, '')::int AS weight_lbs,
                CASE
                    WHEN guard IN ('1', 'true', 'TRUE') THEN 'GUARD'
                    WHEN forward IN ('1', 'true', 'TRUE') THEN 'FORWARD'
                    WHEN center IN ('1', 'true', 'TRUE') THEN 'CENTER'
                    ELSE NULL
                END::player_position AS position,
                NULLIF(draft_year, '')::int AS draft_year,
                NULLIF(draft_number, '')::int AS draft_pick,
                true AS is_active
            FROM staging_players
            WHERE (validation_errors IS NULL OR validation_errors = '{}'::jsonb)
              AND NULLIF(person_id, '') IS NOT NULL
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


async def _upsert_seasons_from_games(session: AsyncSession) -> int:
    from app.ingestion.repositories import get_or_create_league

    league_id = await get_or_create_league(session)
    result = await session.execute(
        text(
            """
            WITH game_dates AS (
                SELECT DISTINCT
                    NULLIF(game_date_time_est, '')::timestamp AS game_ts
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


async def _upsert_games(session: AsyncSession) -> None:
    await session.execute(
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
                NULLIF(game_id, '')::int AS game_id,
                se.season_id,
                (NULLIF(game_date_time_est, '')::timestamp)::date AS game_date,
                (NULLIF(game_date_time_est, '')::timestamp)::time AS game_time,
                NULLIF(hometeam_id, '')::int AS home_team_id,
                NULLIF(awayteam_id, '')::int AS away_team_id,
                NULLIF(home_score, '')::int AS home_score,
                NULLIF(away_score, '')::int AS away_score,
                CASE
                    WHEN game_type ILIKE '%playoff%' THEN 'PLAYOFF'
                    ELSE 'REGULAR'
                END AS season_type,
                NULLIF(attendance, '')::int AS attendance,
                NULLIF(arena_id, '') AS arena
            FROM staging_games sg
            JOIN season se
              ON se.year = CASE
                  WHEN EXTRACT(MONTH FROM sg.game_date_time_est::timestamp) >= 10
                      THEN EXTRACT(YEAR FROM sg.game_date_time_est::timestamp)::int + 1
                  ELSE EXTRACT(YEAR FROM sg.game_date_time_est::timestamp)::int
              END
            WHERE (validation_errors IS NULL OR validation_errors = '{}'::jsonb)
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


async def _upsert_schedule_games(session: AsyncSession) -> None:
    from app.ingestion.repositories import get_or_create_season

    for schedule_path in SCHEDULE_SOURCES:
        if not schedule_path.exists():
            logger.warning("Schedule CSV missing", path=str(schedule_path))
            continue

        with schedule_path.open("r", encoding="utf-8") as file_handle:
            reader = csv.DictReader(file_handle)
            for row in reader:
                game_id = row.get("gameId")
                date_time = row.get("gameDateTimeEst")
                if not game_id or not date_time:
                    continue
                game_ts = date.fromisoformat(date_time.split(" ")[0])
                season_end_year = (
                    game_ts.year + 1 if game_ts.month >= 10 else game_ts.year
                )
                season_id = await get_or_create_season(session, season_end_year)

                await session.execute(
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
                        "game_time": date_time.split(" ")[1]
                        if " " in date_time
                        else None,
                        "home_team_id": int(row.get("hometeamId") or 0),
                        "away_team_id": int(row.get("awayteamId") or 0),
                    },
                )


async def _upsert_box_scores(session: AsyncSession) -> None:
    await session.execute(
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
                NULLIF(game_id, '')::int AS game_id,
                NULLIF(team_id, '')::int AS team_id,
                NULLIF(opponent_team_id, '')::int AS opponent_team_id,
                CASE WHEN home = '1' THEN 'HOME' ELSE 'AWAY' END::location AS location,
                CASE WHEN win = '1' THEN 'WIN' ELSE 'LOSS' END::outcome AS outcome,
                ROUND(NULLIF(num_minutes, '')::numeric * 60) AS seconds_played,
                NULLIF(field_goals_made, '')::int AS made_fg,
                NULLIF(field_goals_attempted, '')::int AS attempted_fg,
                NULLIF(three_pointers_made, '')::int AS made_3pt,
                NULLIF(three_pointers_attempted, '')::int AS attempted_3pt,
                NULLIF(free_throws_made, '')::int AS made_ft,
                NULLIF(free_throws_attempted, '')::int AS attempted_ft,
                NULLIF(rebounds_offensive, '')::int AS offensive_rebounds,
                NULLIF(rebounds_defensive, '')::int AS defensive_rebounds,
                NULLIF(rebounds_total, '')::int AS total_rebounds,
                NULLIF(assists, '')::int AS assists,
                NULLIF(steals, '')::int AS steals,
                NULLIF(blocks, '')::int AS blocks,
                NULLIF(turnovers, '')::int AS turnovers,
                NULLIF(fouls_personal, '')::int AS personal_fouls,
                NULLIF(team_score, '')::int AS points_scored,
                NULLIF(plus_minus_points, '')::int AS plus_minus,
                CASE
                    WHEN NULLIF(field_goals_attempted, '')::numeric > 0
                        THEN ROUND(
                            NULLIF(field_goals_made, '')::numeric
                            / NULLIF(field_goals_attempted, '')::numeric,
                            3
                        )
                    ELSE NULL
                END AS field_goal_percentage,
                CASE
                    WHEN NULLIF(three_pointers_attempted, '')::numeric > 0
                        THEN ROUND(
                            NULLIF(three_pointers_made, '')::numeric
                            / NULLIF(three_pointers_attempted, '')::numeric,
                            3
                        )
                    ELSE NULL
                END AS three_point_percentage,
                CASE
                    WHEN NULLIF(free_throws_attempted, '')::numeric > 0
                        THEN ROUND(
                            NULLIF(free_throws_made, '')::numeric
                            / NULLIF(free_throws_attempted, '')::numeric,
                            3
                        )
                    ELSE NULL
                END AS free_throw_percentage,
                jsonb_build_object(
                    '1', NULLIF(q1_points, '')::int,
                    '2', NULLIF(q2_points, '')::int,
                    '3', NULLIF(q3_points, '')::int,
                    '4', NULLIF(q4_points, '')::int
                ) AS quarter_scores
            FROM staging_team_statistics sts
            WHERE (validation_errors IS NULL OR validation_errors = '{}'::jsonb)
              AND NULLIF(game_id, '') IS NOT NULL
              AND NULLIF(team_id, '') IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM box_score bs
                  WHERE bs.game_id = NULLIF(sts.game_id, '')::int
                    AND bs.team_id = NULLIF(sts.team_id, '')::int
              );
            """
        )
    )


async def _upsert_player_box_scores(session: AsyncSession) -> None:
    await session.execute(
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
                NULLIF(sps.game_id, '')::int AS game_id,
                t.team_id,
                p.slug,
                concat(p.first_name, ' ', p.last_name) AS player_name,
                p.position,
                false AS is_starter,
                CASE
                    WHEN sps.num_minutes LIKE '%:%' THEN
                        split_part(sps.num_minutes, ':', 1)::int * 60
                        + split_part(sps.num_minutes, ':', 2)::int
                    ELSE ROUND(NULLIF(sps.num_minutes, '')::numeric * 60)
                END AS seconds_played,
                NULLIF(sps.field_goals_made, '')::int AS made_fg,
                NULLIF(sps.field_goals_attempted, '')::int AS attempted_fg,
                NULLIF(sps.three_pointers_made, '')::int AS made_3pt,
                NULLIF(sps.three_pointers_attempted, '')::int AS attempted_3pt,
                NULLIF(sps.free_throws_made, '')::int AS made_ft,
                NULLIF(sps.free_throws_attempted, '')::int AS attempted_ft,
                NULLIF(sps.rebounds_offensive, '')::int AS offensive_rebounds,
                NULLIF(sps.rebounds_defensive, '')::int AS defensive_rebounds,
                NULLIF(sps.assists, '')::int AS assists,
                NULLIF(sps.steals, '')::int AS steals,
                NULLIF(sps.blocks, '')::int AS blocks,
                NULLIF(sps.turnovers, '')::int AS turnovers,
                NULLIF(sps.fouls_personal, '')::int AS personal_fouls,
                NULLIF(sps.points, '')::int AS points_scored,
                NULLIF(sps.plus_minus_points, '')::int AS plus_minus
            FROM staging_player_statistics sps
            JOIN player p
              ON p.player_id = NULLIF(sps.person_id, '')::int
            JOIN team t
              ON regexp_replace(lower(t.city || t.name), '[^a-z0-9]', '', 'g')
                = regexp_replace(
                    lower(sps.playerteam_city || sps.playerteam_name),
                    '[^a-z0-9]',
                    '',
                    'g'
                )
            JOIN box_score bs
              ON bs.game_id = NULLIF(sps.game_id, '')::int
             AND bs.team_id = t.team_id
            WHERE (sps.validation_errors IS NULL OR sps.validation_errors = '{}'::jsonb)
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


async def _upsert_player_season_totals(session: AsyncSession) -> None:
    await session.execute(
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
                WHERE (validation_errors IS NULL OR validation_errors = '{}'::jsonb)
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
                'REGULAR'::seasontype,
                CASE WHEN r.is_combined = 1 THEN NULL ELSE t.team_id END,
                NULLIF(r.age, '')::int,
                NULLIF(r.pos, '')::player_position,
                NULLIF(r.g, '')::int,
                NULLIF(r.gs, '')::int,
                NULLIF(r.mp, '')::int,
                NULLIF(r.fg, '')::int,
                NULLIF(r.fga, '')::int,
                NULLIF(r.x3p, '')::int,
                NULLIF(r.x3pa, '')::int,
                NULLIF(r.ft, '')::int,
                NULLIF(r.fta, '')::int,
                NULLIF(r.orb, '')::int,
                NULLIF(r.drb, '')::int,
                NULLIF(r.trb, '')::int,
                NULLIF(r.ast, '')::int,
                NULLIF(r.stl, '')::int,
                NULLIF(r.blk, '')::int,
                NULLIF(r.tov, '')::int,
                NULLIF(r.pf, '')::int,
                NULLIF(r.pts, '')::int,
                0,
                NULLIF(r.trp_dbl, '')::int,
                CASE WHEN r.is_combined = 1 THEN true ELSE false END
            FROM ranked r
            JOIN player p ON p.slug = r.player_id
            JOIN season se ON se.year = NULLIF(r.season, '')::int
            LEFT JOIN team t ON t.abbreviation = r.team
            WHERE r.rn = 1
            ON CONFLICT (player_id, season_id, season_type) DO UPDATE SET
                team_id = EXCLUDED.team_id,
                player_age = EXCLUDED.player_age,
                position = EXCLUDED.position,
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
                triple_doubles = EXCLUDED.triple_doubles,
                is_combined_totals = EXCLUDED.is_combined_totals;
            """
        )
    )


async def _upsert_player_season_advanced(session: AsyncSession) -> None:
    await session.execute(
        text(
            """
            WITH ranked AS (
                SELECT
                    pa.*,
                    CASE WHEN team IN ('TOT', '2TM', '3TM') THEN 1 ELSE 0 END AS is_combined,
                    ROW_NUMBER() OVER (
                        PARTITION BY player_id, season
                        ORDER BY CASE WHEN team IN ('TOT', '2TM', '3TM') THEN 0 ELSE 1 END
                    ) AS rn
                FROM staging_player_advanced pa
                WHERE (validation_errors IS NULL OR validation_errors = '{}'::jsonb)
            ),
            totals AS (
                SELECT
                    pt.player_id,
                    pt.season,
                    NULLIF(NULLIF(pt.fg, ''), 'NA')::numeric AS fg,
                    NULLIF(NULLIF(pt.fga, ''), 'NA')::numeric AS fga,
                    NULLIF(NULLIF(pt.x3p, ''), 'NA')::numeric AS fg3,
                    NULLIF(NULLIF(pt.e_fg_percent, ''), 'NA')::numeric AS efg
                FROM staging_player_totals pt
                WHERE pt.team IN ('TOT', '2TM', '3TM')
            )
            INSERT INTO player_season_advanced (
                player_id,
                season_id,
                season_type,
                team_id,
                player_age,
                games_played,
                minutes_played,
                player_efficiency_rating,
                true_shooting_percentage,
                effective_fg_percentage,
                three_point_attempt_rate,
                free_throw_attempt_rate,
                usage_percentage,
                assist_percentage,
                turnover_percentage,
                offensive_rebound_percentage,
                defensive_rebound_percentage,
                total_rebound_percentage,
                steal_percentage,
                block_percentage,
                offensive_box_plus_minus,
                defensive_box_plus_minus,
                box_plus_minus,
                value_over_replacement_player,
                offensive_win_shares,
                defensive_win_shares,
                win_shares,
                win_shares_per_48,
                is_combined_totals
            )
            SELECT
                p.player_id,
                se.season_id,
                'REGULAR'::seasontype,
                CASE WHEN r.is_combined = 1 THEN NULL ELSE t.team_id END,
                NULLIF(r.age, '')::int,
                NULLIF(r.g, '')::int,
                NULLIF(r.mp, '')::int,
                NULLIF(NULLIF(r.per, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.ts_percent, ''), 'NA')::numeric,
                COALESCE(
                    totals.efg,
                    CASE
                        WHEN totals.fga > 0 THEN
                            ROUND((totals.fg + 0.5 * totals.fg3) / totals.fga, 3)
                        ELSE NULL
                    END
                ),
                NULLIF(NULLIF(r.x3p_ar, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.f_tr, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.usg_percent, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.ast_percent, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.tov_percent, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.orb_percent, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.drb_percent, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.trb_percent, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.stl_percent, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.blk_percent, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.obpm, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.dbpm, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.bpm, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.vorp, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.ows, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.dws, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.ws, ''), 'NA')::numeric,
                NULLIF(NULLIF(r.ws_48, ''), 'NA')::numeric,
                CASE WHEN r.is_combined = 1 THEN true ELSE false END
            FROM ranked r
            JOIN player p ON p.slug = r.player_id
            JOIN season se ON se.year = NULLIF(r.season, '')::int
            LEFT JOIN team t ON t.abbreviation = r.team
            LEFT JOIN totals ON totals.player_id = r.player_id
                AND totals.season = r.season
            WHERE r.rn = 1
            ON CONFLICT (player_id, season_id, season_type) DO UPDATE SET
                team_id = EXCLUDED.team_id,
                player_efficiency_rating = EXCLUDED.player_efficiency_rating,
                true_shooting_percentage = EXCLUDED.true_shooting_percentage,
                effective_fg_percentage = EXCLUDED.effective_fg_percentage,
                three_point_attempt_rate = EXCLUDED.three_point_attempt_rate,
                free_throw_attempt_rate = EXCLUDED.free_throw_attempt_rate,
                usage_percentage = EXCLUDED.usage_percentage,
                assist_percentage = EXCLUDED.assist_percentage,
                turnover_percentage = EXCLUDED.turnover_percentage,
                offensive_rebound_percentage = EXCLUDED.offensive_rebound_percentage,
                defensive_rebound_percentage = EXCLUDED.defensive_rebound_percentage,
                total_rebound_percentage = EXCLUDED.total_rebound_percentage,
                steal_percentage = EXCLUDED.steal_percentage,
                block_percentage = EXCLUDED.block_percentage,
                offensive_box_plus_minus = EXCLUDED.offensive_box_plus_minus,
                defensive_box_plus_minus = EXCLUDED.defensive_box_plus_minus,
                box_plus_minus = EXCLUDED.box_plus_minus,
                value_over_replacement_player = EXCLUDED.value_over_replacement_player,
                offensive_win_shares = EXCLUDED.offensive_win_shares,
                defensive_win_shares = EXCLUDED.defensive_win_shares,
                win_shares = EXCLUDED.win_shares,
                win_shares_per_48 = EXCLUDED.win_shares_per_48,
                is_combined_totals = EXCLUDED.is_combined_totals;
            """
        )
    )


async def _upsert_player_shooting(session: AsyncSession) -> None:
    await session.execute(
        text(
            """
            WITH shooting AS (
                SELECT
                    ps.player_id AS player_slug,
                    NULLIF(ps.season, '')::int AS season_year,
                    NULLIF(ps.team, '') AS team,
                    NULLIF(NULLIF(ps.percent_fga_from_x0_3_range, ''), 'NA')::numeric AS pct_0_3,
                    NULLIF(NULLIF(ps.percent_fga_from_x3_10_range, ''), 'NA')::numeric AS pct_3_10,
                    NULLIF(NULLIF(ps.percent_fga_from_x10_16_range, ''), 'NA')::numeric AS pct_10_16,
                    NULLIF(NULLIF(ps.percent_fga_from_x16_3p_range, ''), 'NA')::numeric AS pct_16_3p,
                    NULLIF(NULLIF(ps.percent_fga_from_x3p_range, ''), 'NA')::numeric AS pct_3p,
                    NULLIF(NULLIF(ps.fg_percent_from_x0_3_range, ''), 'NA')::numeric AS fg_pct_0_3,
                    NULLIF(NULLIF(ps.fg_percent_from_x3_10_range, ''), 'NA')::numeric AS fg_pct_3_10,
                    NULLIF(NULLIF(ps.fg_percent_from_x10_16_range, ''), 'NA')::numeric AS fg_pct_10_16,
                    NULLIF(NULLIF(ps.fg_percent_from_x16_3p_range, ''), 'NA')::numeric AS fg_pct_16_3p,
                    NULLIF(NULLIF(ps.fg_percent_from_x3p_range, ''), 'NA')::numeric AS fg_pct_3p
                FROM staging_player_shooting ps
                WHERE ps.team IN ('TOT', '2TM', '3TM')
            ),
            totals AS (
                SELECT
                    pt.player_id AS player_slug,
                    NULLIF(pt.season, '')::int AS season_year,
                    NULLIF(NULLIF(pt.fga, ''), 'NA')::numeric AS fga
                FROM staging_player_totals pt
                WHERE pt.team IN ('TOT', '2TM', '3TM')
            ),
            base AS (
                SELECT
                    p.player_id,
                    se.season_id,
                    totals.fga,
                    shooting.*
                FROM shooting
                JOIN totals
                  ON totals.player_slug = shooting.player_slug
                 AND totals.season_year = shooting.season_year
                JOIN player p ON p.slug = shooting.player_slug
                JOIN season se ON se.year = shooting.season_year
                WHERE totals.fga IS NOT NULL
            ),
            attempts AS (
                SELECT
                    player_id,
                    season_id,
                    fga,
                    ROUND(fga * COALESCE(pct_0_3, 0))::int AS att_0_3,
                    ROUND(fga * COALESCE(pct_3_10, 0))::int AS att_3_10,
                    ROUND(fga * COALESCE(pct_10_16, 0))::int AS att_10_16,
                    ROUND(fga * COALESCE(pct_16_3p, 0))::int AS att_16_3p,
                    ROUND(fga * COALESCE(pct_3p, 0))::int AS att_3p_raw,
                    fg_pct_0_3,
                    fg_pct_3_10,
                    fg_pct_10_16,
                    fg_pct_16_3p,
                    fg_pct_3p
                FROM base
            ),
            normalized AS (
                SELECT
                    player_id,
                    season_id,
                    att_0_3,
                    att_3_10,
                    att_10_16,
                    att_16_3p,
                    GREATEST(
                        COALESCE(fga, 0)::int
                        - (att_0_3 + att_3_10 + att_10_16 + att_16_3p),
                        0
                    ) AS att_3p,
                    fg_pct_0_3,
                    fg_pct_3_10,
                    fg_pct_10_16,
                    fg_pct_16_3p,
                    fg_pct_3p
                FROM attempts
            )
            INSERT INTO player_shooting (
                player_id,
                season_id,
                distance_range,
                fg_made,
                fg_attempted,
                fg_percentage
            )
            SELECT
                player_id,
                season_id,
                '0-3 ft',
                COALESCE(ROUND(att_0_3 * fg_pct_0_3), 0)::int,
                att_0_3,
                fg_pct_0_3
            FROM normalized
            UNION ALL
            SELECT
                player_id,
                season_id,
                '3-10 ft',
                COALESCE(ROUND(att_3_10 * fg_pct_3_10), 0)::int,
                att_3_10,
                fg_pct_3_10
            FROM normalized
            UNION ALL
            SELECT
                player_id,
                season_id,
                '10-16 ft',
                COALESCE(ROUND(att_10_16 * fg_pct_10_16), 0)::int,
                att_10_16,
                fg_pct_10_16
            FROM normalized
            UNION ALL
            SELECT
                player_id,
                season_id,
                '16-3P',
                COALESCE(ROUND(att_16_3p * fg_pct_16_3p), 0)::int,
                att_16_3p,
                fg_pct_16_3p
            FROM normalized
            UNION ALL
            SELECT
                player_id,
                season_id,
                '3P',
                COALESCE(ROUND(att_3p * fg_pct_3p), 0)::int,
                att_3p,
                fg_pct_3p
            FROM normalized
            ON CONFLICT (player_id, season_id, distance_range) DO UPDATE SET
                fg_made = EXCLUDED.fg_made,
                fg_attempted = EXCLUDED.fg_attempted,
                fg_percentage = EXCLUDED.fg_percentage;
            """
        )
    )


async def _upsert_team_season(session: AsyncSession) -> None:
    await session.execute(
        text(
            """
            WITH totals AS (
                SELECT
                    tt.*,
                    NULLIF(tt.season, '')::int AS season_year
                FROM staging_team_totals tt
                WHERE (validation_errors IS NULL OR validation_errors = '{}'::jsonb)
            ),
            summaries AS (
                SELECT
                    ts.*,
                    NULLIF(ts.season, '')::int AS season_year
                FROM staging_team_summaries ts
                WHERE (validation_errors IS NULL OR validation_errors = '{}'::jsonb)
            )
            INSERT INTO team_season (
                team_id,
                season_id,
                season_type,
                games_played,
                wins,
                losses,
                points_scored,
                points_per_game,
                points_allowed_per_game,
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
                pace,
                offensive_rating,
                defensive_rating,
                net_rating
            )
            SELECT
                t.team_id,
                se.season_id,
                CASE WHEN totals.playoffs = '1' THEN 'PLAYOFF' ELSE 'REGULAR' END,
                NULLIF(totals.g, '')::int AS games_played,
                NULLIF(summaries.w, '')::int AS wins,
                NULLIF(summaries.l, '')::int AS losses,
                NULLIF(totals.pts, '')::int AS points_scored,
                CASE
                    WHEN NULLIF(totals.g, '')::numeric > 0
                        THEN ROUND(
                            NULLIF(totals.pts, '')::numeric
                            / NULLIF(totals.g, '')::numeric,
                            2
                        )
                    ELSE NULL
                END AS points_per_game,
                NULL AS points_allowed_per_game,
                NULLIF(totals.mp, '')::int AS minutes_played,
                NULLIF(totals.fg, '')::int AS made_fg,
                NULLIF(totals.fga, '')::int AS attempted_fg,
                NULLIF(totals.x3p, '')::int AS made_3pt,
                NULLIF(totals.x3pa, '')::int AS attempted_3pt,
                NULLIF(totals.ft, '')::int AS made_ft,
                NULLIF(totals.fta, '')::int AS attempted_ft,
                NULLIF(totals.orb, '')::int AS offensive_rebounds,
                NULLIF(totals.drb, '')::int AS defensive_rebounds,
                NULLIF(totals.trb, '')::int AS total_rebounds,
                NULLIF(totals.ast, '')::int AS assists,
                NULLIF(totals.stl, '')::int AS steals,
                NULLIF(totals.blk, '')::int AS blocks,
                NULLIF(totals.tov, '')::int AS turnovers,
                NULLIF(totals.pf, '')::int AS personal_fouls,
                NULLIF(NULLIF(summaries.pace, ''), 'NA')::numeric AS pace,
                NULLIF(NULLIF(summaries.o_rtg, ''), 'NA')::numeric AS offensive_rating,
                NULLIF(NULLIF(summaries.d_rtg, ''), 'NA')::numeric AS defensive_rating,
                NULLIF(NULLIF(summaries.n_rtg, ''), 'NA')::numeric AS net_rating
            FROM totals
            JOIN summaries
              ON summaries.abbreviation = totals.abbreviation
             AND summaries.season_year = totals.season_year
            JOIN team t ON t.abbreviation = totals.abbreviation
            JOIN season se ON se.year = totals.season_year
            ON CONFLICT (team_id, season_id, season_type) DO UPDATE SET
                games_played = EXCLUDED.games_played,
                wins = EXCLUDED.wins,
                losses = EXCLUDED.losses,
                points_scored = EXCLUDED.points_scored,
                points_per_game = EXCLUDED.points_per_game,
                points_allowed_per_game = EXCLUDED.points_allowed_per_game,
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
                pace = EXCLUDED.pace,
                offensive_rating = EXCLUDED.offensive_rating,
                defensive_rating = EXCLUDED.defensive_rating,
                net_rating = EXCLUDED.net_rating;
            """
        )
    )


async def _refresh_materialized_views(session: AsyncSession) -> None:
    await session.execute(text("REFRESH MATERIALIZED VIEW player_career_stats;"))
    await session.execute(text("REFRESH MATERIALIZED VIEW team_season_standings;"))


async def _ingest_play_by_play_csv() -> None:
    if not PLAY_BY_PLAY_SOURCE.exists():
        logger.warning("Play-by-play CSV missing", path=str(PLAY_BY_PLAY_SOURCE))
        return

    from app.ingestion.mappers import map_play_by_play
    from app.models.game import PlayByPlay

    dsn = _asyncpg_dsn()
    async with asyncpg.connect(dsn) as conn:
        with PLAY_BY_PLAY_SOURCE.open("r", encoding="utf-8") as file_handle:
            reader = csv.DictReader(file_handle)
            batch: list[tuple[Any, ...]] = []
            previous_scores: dict[int, tuple[int | None, int | None]] = {}

            for row in reader:
                game_id = row.get("game_id")
                if not game_id:
                    continue
                game_id_int = int(game_id)

                score = row.get("score") or ""
                away_score = None
                home_score = None
                if "-" in score:
                    parts = score.split("-")
                    if len(parts) == 2:
                        away_score = int(parts[0]) if parts[0].isdigit() else None
                        home_score = int(parts[1]) if parts[1].isdigit() else None

                description = (
                    row.get("homedescription")
                    or row.get("visitordescription")
                    or row.get("neutraldescription")
                    or ""
                )
                period = int(row.get("period") or 0)
                period_type = "OVERTIME" if period > 4 else "QUARTER"

                seconds_remaining = 0
                pct_time = row.get("pctimestring") or ""
                if ":" in pct_time:
                    minutes, seconds = pct_time.split(":")
                    seconds_remaining = int(minutes) * 60 + int(seconds)

                team_id = row.get("player1_team_id")
                team_id_int = int(team_id) if team_id and team_id.isdigit() else None

                prev_scores = previous_scores.get(game_id_int, (None, None))
                play = map_play_by_play(
                    {
                        "period": period,
                        "period_type": period_type,
                        "remaining_seconds_in_period": seconds_remaining,
                        "away_score": away_score,
                        "home_score": home_score,
                        "description": description,
                    },
                    game_id=game_id_int,
                    team_id=team_id_int,
                    previous_scores=prev_scores,
                )
                play.player_involved_id = (
                    int(row["player1_id"])
                    if row.get("player1_id") and row["player1_id"].isdigit()
                    else None
                )
                play.assist_player_id = (
                    int(row["player2_id"])
                    if row.get("player2_id") and row["player2_id"].isdigit()
                    else None
                )
                play.block_player_id = (
                    int(row["player3_id"])
                    if row.get("player3_id") and row["player3_id"].isdigit()
                    else None
                )

                previous_scores[game_id_int] = (away_score, home_score)

                batch.append(
                    (
                        play.game_id,
                        play.period,
                        play.period_type.value,
                        play.seconds_remaining,
                        play.away_score,
                        play.home_score,
                        play.team_id,
                        play.play_type.value,
                        play.player_involved_id,
                        play.assist_player_id,
                        play.block_player_id,
                        play.description,
                        play.shot_distance_ft,
                        play.shot_type,
                        play.foul_type,
                        play.points_scored,
                        play.is_fast_break,
                        play.is_second_chance,
                    )
                )

                if len(batch) >= COPY_BATCH_SIZE:
                    await conn.copy_records_to_table(
                        PlayByPlay.__tablename__,
                        records=batch,
                        columns=[
                            "game_id",
                            "period",
                            "period_type",
                            "seconds_remaining",
                            "away_score",
                            "home_score",
                            "team_id",
                            "play_type",
                            "player_involved_id",
                            "assist_player_id",
                            "block_player_id",
                            "description",
                            "shot_distance_ft",
                            "shot_type",
                            "foul_type",
                            "points_scored",
                            "is_fast_break",
                            "is_second_chance",
                        ],
                    )
                    batch = []

            if batch:
                await conn.copy_records_to_table(
                    PlayByPlay.__tablename__,
                    records=batch,
                    columns=[
                        "game_id",
                        "period",
                        "period_type",
                        "seconds_remaining",
                        "away_score",
                        "home_score",
                        "team_id",
                        "play_type",
                        "player_involved_id",
                        "assist_player_id",
                        "block_player_id",
                        "description",
                        "shot_distance_ft",
                        "shot_type",
                        "foul_type",
                        "points_scored",
                        "is_fast_break",
                        "is_second_chance",
                    ],
                )


def run_async(coro):
    """Helper to run async code in sync Celery tasks."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="app.ingestion.tasks.ingest_csv_datasets",
    bind=True,
    max_retries=1,
)
def ingest_csv_datasets(self, include_play_by_play: bool = False):
    """Ingest CSV datasets into staging and upsert into production tables."""
    try:
        run_async(_ingest_csv_datasets_async(include_play_by_play))
    except Exception as exc:
        logger.exception("Failed CSV ingestion")
        raise self.retry(exc=exc) from exc


async def _ingest_csv_datasets_async(include_play_by_play: bool) -> None:
    import_batch_id = uuid4()
    logger.info("Starting CSV ingestion", batch_id=str(import_batch_id))

    await _load_staging_tables(import_batch_id)

    async with async_session_factory() as session:
        await _validate_staging(session)
        await _upsert_franchises(session)
        await _upsert_teams(session)
        await _upsert_players(session)
        await _upsert_seasons_from_games(session)
        await _upsert_games(session)
        await _upsert_schedule_games(session)
        await _upsert_box_scores(session)
        await _upsert_player_box_scores(session)
        await _upsert_player_season_totals(session)
        await _upsert_player_season_advanced(session)
        await _upsert_player_shooting(session)
        await _upsert_team_season(session)
        await _refresh_materialized_views(session)
        await session.commit()

    if include_play_by_play:
        await _ingest_play_by_play_csv()
    logger.info("CSV ingestion completed", batch_id=str(import_batch_id))


@celery_app.task(
    name="app.ingestion.tasks.ingest_daily_box_scores",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def ingest_daily_box_scores(self, target_date: str | None = None):
    """Ingest all player and team box scores for a given date.

    Args:
        target_date: Date string in YYYY-MM-DD format. Defaults to yesterday.
    """
    if target_date:
        dt = date.fromisoformat(target_date)
    else:
        # Default to yesterday (games from last night)
        dt = date.today() - timedelta(days=1)

    logger.info("Starting daily box score ingestion", date=dt.isoformat())

    try:
        run_async(_ingest_daily_box_scores_async(dt))
        logger.info("Completed daily box score ingestion", date=dt.isoformat())
    except Exception as exc:
        logger.exception("Failed to ingest daily box scores", date=dt.isoformat())
        raise self.retry(exc=exc) from exc


async def _ingest_daily_box_scores_async(dt: date):
    """Async implementation of daily box score ingestion."""
    scraper = ScraperService()

    # Fetch player box scores
    player_box_scores = await scraper.get_player_box_scores(
        day=dt.day, month=dt.month, year=dt.year
    )
    logger.info("Fetched player box scores", count=len(player_box_scores))

    # Fetch team box scores
    team_box_scores = await scraper.get_team_box_scores(
        day=dt.day, month=dt.month, year=dt.year
    )
    logger.info("Fetched team box scores", count=len(team_box_scores))

    async with async_session_factory() as session:
        await _persist_box_scores(session, dt, player_box_scores, team_box_scores)
        await session.commit()


async def _persist_box_scores(
    session: AsyncSession,
    dt: date,
    player_box_scores: list[dict[str, Any]],
    team_box_scores: list[dict[str, Any]],
):
    """Persist box scores to the database.

    Flow:
    1. Determine season from date
    2. Group team box scores by game (home vs away)
    3. Create/lookup teams, create games, create team box scores
    4. For each player box score, lookup player, create player box score
    """
    from app.ingestion.mappers import (
        _extract_player_slug,
        map_player_box_score,
    )
    from app.ingestion.repositories import (
        clear_caches,
        get_or_create_box_score,
        get_or_create_game,
        get_or_create_player,
        get_or_create_season,
        get_or_create_team,
        upsert_player_box_score,
    )
    from app.models.game import Location, Outcome

    await clear_caches()

    # Determine season end year (Oct-Dec belongs to next season end year)
    season_end_year = dt.year + 1 if dt.month >= 10 else dt.year

    season_id = await get_or_create_season(session, season_end_year)
    logger.info("Using season", season_id=season_id, season_end_year=season_end_year)

    # Process team box scores first to create games and team box scores
    # Team box scores come in pairs (home and away for each game)
    games_created: dict[tuple[int, int], tuple[int, dict[int, int]]] = {}

    for tbs in team_box_scores:
        team_abbrev = tbs.get("team")
        if hasattr(team_abbrev, "value"):
            team_abbrev = team_abbrev.value
        if not team_abbrev:
            continue

        opponent_abbrev = tbs.get("opponent")
        if hasattr(opponent_abbrev, "value"):
            opponent_abbrev = opponent_abbrev.value

        # Get or create teams
        team_id = await get_or_create_team(session, str(team_abbrev))
        opponent_id = await get_or_create_team(session, str(opponent_abbrev))

        # Determine location and outcome
        outcome_val = tbs.get("outcome")
        if hasattr(outcome_val, "value"):
            outcome_val = outcome_val.value
        outcome = Outcome.WIN if outcome_val == "WIN" else Outcome.LOSS

        location_val = tbs.get("location")
        if hasattr(location_val, "value"):
            location_val = location_val.value
        location = Location.HOME if location_val == "HOME" else Location.AWAY

        # Determine home/away for game creation
        if location == Location.HOME:
            home_team_id = team_id
            away_team_id = opponent_id
        else:
            home_team_id = opponent_id
            away_team_id = team_id

        # Use consistent key ordering for game lookup
        game_key = (min(home_team_id, away_team_id), max(home_team_id, away_team_id))

        # Create game if not already created for this pair
        if game_key not in games_created:
            home_score = tbs.get("points") if location == Location.HOME else None
            away_score = tbs.get("points") if location == Location.AWAY else None

            game_id = await get_or_create_game(
                session,
                game_date=dt,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                season_id=season_id,
                home_score=home_score,
                away_score=away_score,
            )
            games_created[game_key] = (game_id, {})

        game_id, box_id_map = games_created[game_key]

        # Create team box score
        box_id = await get_or_create_box_score(
            session,
            game_id=game_id,
            team_id=team_id,
            opponent_team_id=opponent_id,
            location=location,
            outcome=outcome,
            stats=tbs,
        )
        box_id_map[team_id] = box_id
        games_created[game_key] = (game_id, box_id_map)

    logger.info("Created games and team box scores", games_count=len(games_created))

    # Now process player box scores
    player_count = 0
    for pbs in player_box_scores:
        team_abbrev = pbs.get("team")
        if hasattr(team_abbrev, "value"):
            team_abbrev = team_abbrev.value
        if not team_abbrev:
            continue

        opponent_abbrev = pbs.get("opponent")
        if hasattr(opponent_abbrev, "value"):
            opponent_abbrev = opponent_abbrev.value

        team_id = await get_or_create_team(session, str(team_abbrev))
        opponent_id = await get_or_create_team(session, str(opponent_abbrev))

        # Get player
        player_slug = pbs.get("slug") or _extract_player_slug(pbs.get("name"))
        player_name = pbs.get("name")
        player_id = await get_or_create_player(session, player_slug, player_name)

        # Find the game and box score for this player
        game_key = (min(team_id, opponent_id), max(team_id, opponent_id))
        if game_key not in games_created:
            logger.warning(
                "No game found for player box score",
                player=player_name,
                team=team_abbrev,
            )
            continue

        game_id, box_id_map = games_created[game_key]
        if team_id not in box_id_map:
            logger.warning(
                "No box score found for team",
                team=team_abbrev,
                game_id=game_id,
            )
            continue

        box_id = box_id_map[team_id]

        # Create player box score
        player_box = map_player_box_score(
            raw=pbs,
            player_id=player_id,
            box_id=box_id,
            game_id=game_id,
            team_id=team_id,
        )
        await upsert_player_box_score(
            session, player_id, box_id, game_id, team_id, player_box
        )
        player_count += 1

    logger.info(
        "Persisted box scores",
        date=dt.isoformat(),
        games=len(games_created),
        players=player_count,
    )


@celery_app.task(
    name="app.ingestion.tasks.update_standings",
    bind=True,
    max_retries=3,
)
def update_standings(self, season_end_year: int | None = None):
    """Update standings for the current or specified season.

    Args:
        season_end_year: Year the season ends. Defaults to current season.
    """
    if season_end_year is None:
        today = date.today()
        # NBA season runs Oct-June, so if we're past June, use next year
        season_end_year = today.year + 1 if today.month >= 10 else today.year

    logger.info("Updating standings", season_end_year=season_end_year)

    try:
        run_async(_update_standings_async(season_end_year))
        logger.info("Completed standings update", season_end_year=season_end_year)
    except Exception as exc:
        logger.exception("Failed to update standings")
        raise self.retry(exc=exc) from exc


async def _update_standings_async(season_end_year: int):
    """Async implementation of standings update."""
    scraper = ScraperService()
    standings = await scraper.get_standings(season_end_year)

    if not standings:
        logger.warning("No standings data returned", season_end_year=season_end_year)
        return

    logger.info("Fetched standings data", season_end_year=season_end_year)

    async with async_session_factory() as session:
        await _persist_standings(session, season_end_year, standings)
        await session.commit()


async def _persist_standings(
    session: AsyncSession,
    season_end_year: int,
    standings: dict[str, Any],
):
    """Persist standings to the database.

    Standings data comes as a dict with division/conference keys.
    Each entry contains team records.
    """
    from app.ingestion.mappers import map_standings
    from app.ingestion.repositories import (
        clear_caches,
        get_or_create_season,
        get_or_create_team,
        upsert_team_season,
    )

    await clear_caches()
    season_id = await get_or_create_season(session, season_end_year)

    teams_processed = 0

    # Standings structure: {"EASTERN": [...], "WESTERN": [...]} or by division
    for _conference_or_division, team_records in standings.items():
        if not isinstance(team_records, list):
            continue

        for record in team_records:
            team_name = record.get("team")
            if hasattr(team_name, "value"):
                team_name = team_name.value
            if not team_name:
                continue

            # Get team abbreviation from the team enum or string
            team_abbrev = str(team_name)
            # If it's a full team name, try to extract abbreviation
            # For now, use the value as-is since scraper returns Team enums
            team_id = await get_or_create_team(session, team_abbrev, team_name)

            team_season = map_standings(
                raw=record,
                team_id=team_id,
                season_id=season_id,
            )
            await upsert_team_season(session, team_season)
            teams_processed += 1

    logger.info(
        "Persisted standings",
        season_end_year=season_end_year,
        teams=teams_processed,
    )


@celery_app.task(
    name="app.ingestion.tasks.sync_season_data",
    bind=True,
    max_retries=2,
)
def sync_season_data(self, season_end_year: int | None = None):
    """Full sync of season data including schedule, player totals, and advanced stats.

    This is a heavy operation meant to run weekly or on-demand.

    Args:
        season_end_year: Year the season ends. Defaults to current season.
    """
    if season_end_year is None:
        today = date.today()
        season_end_year = today.year + 1 if today.month >= 10 else today.year

    logger.info("Starting full season sync", season_end_year=season_end_year)

    try:
        run_async(_sync_season_data_async(season_end_year))
        logger.info("Completed full season sync", season_end_year=season_end_year)
    except Exception as exc:
        logger.exception("Failed full season sync")
        raise self.retry(exc=exc) from exc


async def _sync_season_data_async(season_end_year: int):
    """Async implementation of full season sync."""
    scraper = ScraperService()

    # Fetch schedule
    schedule = await scraper.get_season_schedule(season_end_year)
    logger.info("Fetched schedule", count=len(schedule))

    # Fetch player season totals
    player_totals = await scraper.get_players_season_totals(season_end_year)
    logger.info("Fetched player totals", count=len(player_totals))

    # Fetch advanced stats
    advanced_totals = await scraper.get_players_advanced_season_totals(
        season_end_year, include_combined_values=True
    )
    logger.info("Fetched advanced totals", count=len(advanced_totals))

    # Fetch standings
    standings = await scraper.get_standings(season_end_year)
    logger.info("Fetched standings")

    async with async_session_factory() as session:
        await _persist_season_data(
            session,
            season_end_year,
            schedule,
            player_totals,
            advanced_totals,
            standings,
        )
        await session.commit()


async def _persist_season_data(
    session: AsyncSession,
    season_end_year: int,
    schedule: list[dict[str, Any]],
    player_totals: list[dict[str, Any]],
    advanced_totals: list[dict[str, Any]],
    standings: dict[str, Any],
):
    """Persist all season data to the database.

    This is the full sync that handles:
    1. Schedule (games)
    2. Player season totals
    3. Player advanced stats
    4. Standings
    """
    from app.ingestion.mappers import (
        _extract_player_slug,
        map_player_advanced_totals,
        map_player_season_totals,
    )
    from app.ingestion.repositories import (
        clear_caches,
        get_or_create_game,
        get_or_create_player,
        get_or_create_season,
        get_or_create_team,
        upsert_player_season,
        upsert_player_season_advanced,
    )

    await clear_caches()
    season_id = await get_or_create_season(session, season_end_year)

    # 1. Process schedule to create games
    games_created = 0
    for game_data in schedule:
        home_team = game_data.get("home_team")
        away_team = game_data.get("away_team")

        if hasattr(home_team, "value"):
            home_team = home_team.value
        if hasattr(away_team, "value"):
            away_team = away_team.value

        if not home_team or not away_team:
            continue

        home_team_id = await get_or_create_team(session, str(home_team))
        away_team_id = await get_or_create_team(session, str(away_team))

        # Parse date from start_time
        start_time = game_data.get("start_time")
        if start_time is None:
            continue

        from datetime import datetime

        if isinstance(start_time, datetime):
            game_date = start_time.date()
        elif isinstance(start_time, date):
            game_date = start_time
        else:
            continue

        await get_or_create_game(
            session,
            game_date=game_date,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            season_id=season_id,
            home_score=game_data.get("home_team_score"),
            away_score=game_data.get("away_team_score"),
        )
        games_created += 1

    logger.info("Persisted schedule", games=games_created)

    # 2. Process player season totals
    players_processed = 0

    def _select_player_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        selected: dict[str, dict[str, Any]] = {}
        for record in records:
            player_slug = record.get("slug") or _extract_player_slug(record.get("name"))
            if not player_slug:
                continue
            if record.get("is_combined_totals", False):
                selected[player_slug] = record
            else:
                selected.setdefault(player_slug, record)
        return list(selected.values())

    for pt in _select_player_records(player_totals):
        player_slug = pt.get("slug") or _extract_player_slug(pt.get("name"))
        player_name = pt.get("name")
        player_id = await get_or_create_player(session, player_slug, player_name)

        # Get team if available
        team_abbrev = pt.get("team")
        if hasattr(team_abbrev, "value"):
            team_abbrev = team_abbrev.value
        team_id = None
        if team_abbrev:
            team_id = await get_or_create_team(session, str(team_abbrev))

        player_season = map_player_season_totals(
            raw=pt,
            player_id=player_id,
            season_id=season_id,
            team_id=team_id,
        )
        await upsert_player_season(session, player_season)
        players_processed += 1

    logger.info("Persisted player totals", players=players_processed)

    # 3. Process advanced stats
    advanced_processed = 0
    for at in _select_player_records(advanced_totals):
        player_slug = at.get("slug") or _extract_player_slug(at.get("name"))
        player_name = at.get("name")
        player_id = await get_or_create_player(session, player_slug, player_name)

        team_abbrev = at.get("team")
        if hasattr(team_abbrev, "value"):
            team_abbrev = team_abbrev.value
        team_id = None
        if team_abbrev:
            team_id = await get_or_create_team(session, str(team_abbrev))

        player_advanced = map_player_advanced_totals(
            raw=at,
            player_id=player_id,
            season_id=season_id,
            team_id=team_id,
        )
        await upsert_player_season_advanced(session, player_advanced)
        advanced_processed += 1

    logger.info("Persisted advanced stats", players=advanced_processed)

    # 4. Persist standings
    await _persist_standings(session, season_end_year, standings)

    logger.info(
        "Completed full season sync",
        season_end_year=season_end_year,
        games=games_created,
        player_totals=players_processed,
        advanced_stats=advanced_processed,
    )


@celery_app.task(name="app.ingestion.tasks.ingest_player_game_log")
def ingest_player_game_log(player_identifier: str, season_end_year: int):
    """Ingest a single player's game log for a season.

    Args:
        player_identifier: Player ID (e.g., 'jamesle01').
        season_end_year: Year the season ends.
    """
    logger.info(
        "Ingesting player game log",
        player_identifier=player_identifier,
        season_end_year=season_end_year,
    )

    run_async(_ingest_player_game_log_async(player_identifier, season_end_year))


async def _ingest_player_game_log_async(player_identifier: str, season_end_year: int):
    """Async implementation of player game log ingestion."""
    scraper = ScraperService()

    game_log = await scraper.get_regular_season_player_box_scores(
        player_identifier=player_identifier,
        season_end_year=season_end_year,
        include_inactive_games=True,
    )

    logger.info(
        "Fetched player game log",
        player_identifier=player_identifier,
        count=len(game_log),
    )

    async with async_session_factory() as session:
        from app.ingestion.mappers import map_player_box_score
        from app.ingestion.repositories import (
            clear_caches,
            get_or_create_box_score,
            get_or_create_game,
            get_or_create_player,
            get_or_create_season,
            get_or_create_team,
            upsert_player_box_score,
        )
        from app.models.game import Location, Outcome

        await clear_caches()
        season_id = await get_or_create_season(session, season_end_year)
        player_id = await get_or_create_player(session, player_identifier)

        persisted = 0
        for entry in game_log:
            if entry.get("active") is False:
                continue

            team_enum = entry.get("team")
            opponent_enum = entry.get("opponent")
            team_abbrev = TEAM_TO_TEAM_ABBREVIATION.get(team_enum, str(team_enum))
            opponent_abbrev = TEAM_TO_TEAM_ABBREVIATION.get(
                opponent_enum, str(opponent_enum)
            )
            team_id = await get_or_create_team(session, team_abbrev)
            opponent_id = await get_or_create_team(session, opponent_abbrev)

            location_val = entry.get("location")
            if hasattr(location_val, "value"):
                location_val = location_val.value
            location = Location.HOME if location_val == "HOME" else Location.AWAY

            outcome_val = entry.get("outcome")
            if hasattr(outcome_val, "value"):
                outcome_val = outcome_val.value
            outcome = Outcome.WIN if outcome_val == "WIN" else Outcome.LOSS

            if location == Location.HOME:
                home_team_id = team_id
                away_team_id = opponent_id
            else:
                home_team_id = opponent_id
                away_team_id = team_id

            game_date = entry.get("date")
            if game_date is None:
                continue

            game_id = await get_or_create_game(
                session,
                game_date=game_date,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                season_id=season_id,
            )

            box_id = await get_or_create_box_score(
                session,
                game_id=game_id,
                team_id=team_id,
                opponent_team_id=opponent_id,
                location=location,
                outcome=outcome,
            )

            player_box = map_player_box_score(
                raw=entry,
                player_id=player_id,
                box_id=box_id,
                game_id=game_id,
                team_id=team_id,
            )
            await upsert_player_box_score(
                session, player_id, box_id, game_id, team_id, player_box
            )
            persisted += 1

        await session.commit()
        logger.info(
            "Persisted player game log",
            player_identifier=player_identifier,
            count=persisted,
        )


@celery_app.task(name="app.ingestion.tasks.ingest_play_by_play")
def ingest_play_by_play(home_team: str, day: int, month: int, year: int):
    """Ingest play-by-play data for a single game.

    Args:
        home_team: Team abbreviation for home team.
        day: Day of the month.
        month: Month number.
        year: 4-digit year.
    """
    logger.info(
        "Ingesting play-by-play",
        home_team=home_team,
        date=f"{year}-{month:02d}-{day:02d}",
    )

    run_async(_ingest_play_by_play_async(home_team, day, month, year))


async def _ingest_play_by_play_async(home_team: str, day: int, month: int, year: int):
    """Async implementation of play-by-play ingestion."""
    scraper = ScraperService()

    plays = await scraper.get_play_by_play(
        home_team=home_team, day=day, month=month, year=year
    )

    logger.info("Fetched play-by-play", count=len(plays))

    async with async_session_factory() as session:
        from app.ingestion.mappers import map_play_by_play
        from app.ingestion.repositories import (
            clear_caches,
            get_or_create_game,
            get_or_create_season,
            get_or_create_team,
        )
        from app.models.game import PlayByPlay

        if not plays:
            return

        await clear_caches()
        game_date = date(year, month, day)
        season_end_year = year + 1 if month >= 10 else year
        season_id = await get_or_create_season(session, season_end_year)

        first = plays[0]
        away_enum = first.get("away_team")
        home_enum = first.get("home_team")
        away_abbrev = TEAM_TO_TEAM_ABBREVIATION.get(away_enum, str(away_enum))
        home_abbrev = TEAM_TO_TEAM_ABBREVIATION.get(home_enum, str(home_enum))
        away_id = await get_or_create_team(session, away_abbrev)
        home_id = await get_or_create_team(session, home_abbrev)

        game_id = await get_or_create_game(
            session,
            game_date=game_date,
            home_team_id=home_id,
            away_team_id=away_id,
            season_id=season_id,
        )

        await session.execute(delete(PlayByPlay).where(PlayByPlay.game_id == game_id))

        prev_scores: tuple[int | None, int | None] = (None, None)
        for play in plays:
            relevant_team = play.get("relevant_team")
            if relevant_team is None:
                team_id = None
            else:
                relevant_abbrev = TEAM_TO_TEAM_ABBREVIATION.get(
                    relevant_team, str(relevant_team)
                )
                team_id = await get_or_create_team(session, relevant_abbrev)

            play_model = map_play_by_play(play, game_id, team_id, prev_scores)
            session.add(play_model)
            prev_scores = (play.get("away_score"), play.get("home_score"))

        await session.commit()
        logger.info("Persisted play-by-play", game_id=game_id, plays=len(plays))
