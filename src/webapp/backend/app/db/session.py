"""Database session and engine configuration."""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

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
        conn.execute(
            text("""
            CREATE OR REPLACE VIEW player AS
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
            CREATE OR REPLACE VIEW team AS
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
            CREATE OR REPLACE VIEW season AS
            SELECT DISTINCT
                year(date) AS season_id,
                year(date) AS year,
                NULL AS league_id
            FROM fact_player_gamelogs
        """)
        )
        conn.execute(
            text("""
            CREATE OR REPLACE VIEW player_season AS
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
        # Create empty tables/views for other models to avoid crashes
        for table in [
            "award",
            "award_recipient",
            "draft",
            "draft_pick",
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
