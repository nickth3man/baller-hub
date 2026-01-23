"""Database session and engine configuration."""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from contextlib import suppress

# check_same_thread=False is required for SQLite, but not supported/needed by DuckDB
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args=connect_args,
    future=True,
)

session_factory = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
    autoflush=False,
)


def get_session() -> Generator[Session, None, None]:
    with session_factory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def init_db() -> None:
    # Create views to bridge Star Schema to SQLModel expectations
    with engine.connect() as conn:
        for obj in [
            "player",
            "team",
            "season",
            "player_season",
            "draft",
            "draft_pick",
            "award",
            "award_recipient",
        ]:
            with suppress(Exception):
                conn.execute(text(f"DROP VIEW IF EXISTS {obj};"))
            with suppress(Exception):
                conn.execute(text(f"DROP TABLE IF EXISTS {obj};"))

        conn.execute(
            text("""
            CREATE VIEW player AS
            SELECT
                hash(bref_id) AS player_id,
                bref_id AS slug,
                split_part(name, ' ', 1) AS first_name,
                split_part(name, ' ', 2) AS last_name,
                name AS full_name,
                birth_date,
                TRUE AS is_active,
                NULL AS middle_name,
                NULL AS birth_place_city,
                NULL AS birth_place_country,
                NULL AS death_date,
                NULL AS height_inches,
                NULL AS weight_lbs,
                NULL AS position,
                NULL AS high_school,
                NULL AS college,
                NULL AS draft_year,
                NULL AS draft_pick,
                NULL AS debut_date,
                NULL AS final_date,
                NULL AS debut_year,
                NULL AS final_year
            FROM dim_players
        """)
        )
        conn.execute(
            text("""
            CREATE VIEW team AS
            SELECT
                hash(bref_id) AS team_id,
                bref_id AS abbreviation,
                bref_id AS name,
                1900 AS founded_year,
                NULL AS defunct_year,
                NULL AS division_id,
                NULL AS franchise_id,
                TRUE AS is_active,
                FALSE AS is_defunct,
                NULL AS city,
                NULL AS arena,
                NULL AS arena_capacity,
                NULL AS relocation_history
            FROM dim_teams
        """)
        )
        conn.execute(
            text("""
            CREATE VIEW season AS
            SELECT DISTINCT
                year(date) AS season_id,
                year(date) AS year,
                NULL AS league_id
            FROM fact_player_gamelogs
        """)
        )
        conn.execute(
            text("""
            CREATE VIEW player_season AS
            SELECT
                hash(player_id) AS player_id,
                year(date) AS season_id,
                'REGULAR' AS season_type,
                hash(team_id) AS team_id,
                count(*) AS games_played,
                0 AS games_started,
                0 AS minutes_played,
                sum(points) AS points_scored,
                0 AS made_fg,
                0 AS attempted_fg,
                0 AS made_3pt,
                0 AS attempted_3pt,
                0 AS made_ft,
                0 AS attempted_ft,
                0 AS offensive_rebounds,
                0 AS defensive_rebounds,
                0 AS total_rebounds,
                sum(assists) AS assists,
                sum(steals) AS steals,
                sum(blocks) AS blocks,
                sum(turnovers) AS turnovers,
                sum(personal_fouls) AS personal_fouls,
                0 AS double_doubles,
                0 AS triple_doubles,
                FALSE AS is_combined_totals,
                NULL AS player_age,
                NULL AS position
            FROM fact_player_gamelogs
            GROUP BY player_id, year(date), team_id
        """)
        )
        conn.execute(
            text("""
            CREATE VIEW draft AS
            SELECT DISTINCT
                hash(season) AS draft_id,
                year(CAST(split_part(season, '-', 1) || '-06-25' AS DATE)) AS season_id,
                CAST(split_part(season, '-', 1) AS INTEGER) AS year,
                CAST(split_part(season, '-', 1) || '-06-25' AS DATE) AS draft_date,
                2 AS round_count,
                60 AS pick_count
            FROM staging_draft_pick_history
        """)
        )
        conn.execute(
            text("""
            CREATE VIEW draft_pick AS
            SELECT
                hash(season || overall_pick) AS pick_id,
                hash(season) AS draft_id,
                CAST(overall_pick AS INTEGER) AS overall_pick,
                CAST(round AS INTEGER) AS round_number,
                ((CAST(overall_pick AS INTEGER) - 1) % 30) + 1 AS round_pick,
                hash(tm) AS team_id,
                hash(player_id) AS player_id,
                hash(tm) AS original_team_id,
                NULL AS trade_notes,
                college,
                NULL AS height_in,
                NULL AS weight_lbs,
                NULL AS position
            FROM staging_draft_pick_history
        """)
        )
        conn.execute(
            text("""
            CREATE VIEW award AS
            SELECT 1 AS award_id, 'NBA Championship' AS name, 'CHAMPIONSHIP' AS category, 'NBA Finals Winner' AS description, 1947 AS first_awarded_year, NULL AS last_awarded_year, TRUE AS is_active
            UNION ALL
            SELECT 2 AS award_id, 'All-Star Selection' AS name, 'ALL_STAR' AS category, 'NBA All-Star' AS description, 1951 AS first_awarded_year, NULL AS last_awarded_year, TRUE AS is_active
        """)
        )
        conn.execute(
            text("""
            CREATE VIEW award_recipient AS
            SELECT
                1 AS award_id,
                year(CAST(split_part(season, '-', 1) || '-06-01' AS DATE)) AS season_id,
                NULL AS player_id,
                hash(champion) AS team_id,
                1 AS vote_rank,
                NULL AS vote_count,
                1.0 AS vote_percentage,
                NULL AS first_place_votes,
                'TEAM' AS recipient_type,
                NULL AS notes
            FROM staging_nba_championships
        """)
        )
        # Create empty tables/views for other models to avoid crashes
        for table in [
            "game",
            "box_score",
            "play_by_play",
            "player_box_score",
            "player_season_advanced",
            "player_shooting",
            "franchise",
            "league",
            "conference",
            "division",
        ]:
            conn.execute(text(f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER)"))
        conn.commit()

    # We skip metadata.create_all for now to avoid SERIAL issues and conflicts
    # metadata.create_all(engine) would fail on DuckDB if it uses SERIAL types
