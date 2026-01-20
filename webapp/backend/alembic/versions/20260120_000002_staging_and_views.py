"""Add staging tables, shooting splits, and materialized views.

Revision ID: 20260120_000002
Revises: 20260119_000001
Create Date: 2026-01-20

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260120_000002"
down_revision: Union[str, None] = "20260119_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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


def _create_staging_table(table_name: str, columns: list[str]) -> None:
    columns_sql = ",\n        ".join(f"{col} text" for col in columns)
    op.execute(
        f"""
        CREATE UNLOGGED TABLE {table_name} (
            row_id bigserial PRIMARY KEY,
            {columns_sql},
            import_batch_id uuid,
            validation_errors jsonb
        );
        """
    )


def upgrade() -> None:
    op.create_table(
        "player_shooting",
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column(
            "distance_range", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False
        ),
        sa.Column("fg_made", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fg_attempted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fg_percentage", sa.Numeric(precision=5, scale=3), nullable=True),
        sa.PrimaryKeyConstraint("player_id", "season_id", "distance_range"),
        sa.ForeignKeyConstraint(["player_id"], ["player.player_id"]),
        sa.ForeignKeyConstraint(["season_id"], ["season.season_id"]),
    )

    for table_name, columns in STAGING_TABLES.items():
        _create_staging_table(table_name, columns)

    op.execute(
        """
        CREATE MATERIALIZED VIEW player_career_stats AS
        SELECT
            p.player_id,
            p.slug,
            p.first_name,
            p.last_name,
            COUNT(DISTINCT pbs.game_id) AS games_played,
            SUM(pbs.points_scored) AS career_points,
            SUM(pbs.assists) AS career_assists,
            SUM(pbs.offensive_rebounds + pbs.defensive_rebounds) AS career_rebounds,
            ROUND(AVG(pbs.points_scored)::numeric, 1) AS ppg,
            ROUND(AVG(pbs.assists)::numeric, 1) AS apg,
            ROUND(AVG(pbs.offensive_rebounds + pbs.defensive_rebounds)::numeric, 1) AS rpg
        FROM player p
        LEFT JOIN player_box_score pbs ON p.player_id = pbs.player_id
        GROUP BY p.player_id, p.slug, p.first_name, p.last_name;
        """
    )
    op.execute(
        "CREATE INDEX idx_player_career_stats_player_id "
        "ON player_career_stats(player_id);"
    )
    op.execute(
        "CREATE INDEX idx_player_career_stats_slug "
        "ON player_career_stats(slug);"
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW team_season_standings AS
        SELECT
            ts.team_id,
            t.abbreviation AS team_abbrev,
            t.name AS team_name,
            ts.season_id,
            ts.wins,
            ts.losses,
            ts.games_played,
            ts.points_per_game,
            ts.points_allowed_per_game,
            ROUND(ts.wins::numeric / NULLIF(ts.wins + ts.losses, 0), 3) AS win_pct
        FROM team_season ts
        JOIN team t ON ts.team_id = t.team_id
        WHERE ts.season_type = 'REGULAR';
        """
    )
    op.execute(
        "CREATE INDEX idx_team_season_standings_season "
        "ON team_season_standings(season_id);"
    )
    op.execute(
        "CREATE INDEX idx_team_season_standings_team "
        "ON team_season_standings(team_id);"
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS team_season_standings;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS player_career_stats;")

    for table_name in STAGING_TABLES.keys():
        op.execute(f"DROP TABLE IF EXISTS {table_name};")

    op.drop_table("player_shooting")
