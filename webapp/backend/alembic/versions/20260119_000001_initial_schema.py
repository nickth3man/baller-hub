"""Initial database schema with all models

Revision ID: 20260119_000001_initial_schema
Revises:
Create Date: 2026-01-19

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260119_000001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # League structure tables
    op.create_table(
        "league",
        sa.Column("league_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column(
            "league_type",
            sa.Enum("NBA", "ABA", "BAA", name="leaguetype"),
            nullable=False,
        ),
        sa.Column("start_year", sa.Integer(), nullable=False),
        sa.Column("end_year", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("league_id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "conference",
        sa.Column("conference_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column(
            "conference_type",
            sa.Enum("EASTERN", "WESTERN", name="conferencetype"),
            nullable=False,
        ),
        sa.Column("league_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("conference_id"),
        sa.ForeignKeyConstraint(["league_id"], ["league.league_id"]),
        sa.UniqueConstraint("conference_type"),
    )

    op.create_table(
        "division",
        sa.Column("division_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column(
            "division_type",
            sa.Enum(
                "ATLANTIC",
                "CENTRAL",
                "SOUTHEAST",
                "NORTHWEST",
                "PACIFIC",
                "SOUTHWEST",
                "MIDWEST",
                name="divisiontype",
            ),
            nullable=False,
        ),
        sa.Column("conference_id", sa.Integer(), nullable=False),
        sa.Column("league_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("division_id"),
        sa.ForeignKeyConstraint(["conference_id"], ["conference.conference_id"]),
        sa.ForeignKeyConstraint(["league_id"], ["league.league_id"]),
        sa.UniqueConstraint("division_type"),
    )

    # Franchise and Team tables
    op.create_table(
        "franchise",
        sa.Column("franchise_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("founded_year", sa.Integer(), nullable=False),
        sa.Column("defunct_year", sa.Integer(), nullable=True),
        sa.Column("city", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.PrimaryKeyConstraint("franchise_id"),
    )

    op.create_table(
        "team",
        sa.Column("team_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column(
            "abbreviation", sqlmodel.sql.sqltypes.AutoString(length=3), nullable=False
        ),
        sa.Column("founded_year", sa.Integer(), nullable=False),
        sa.Column("defunct_year", sa.Integer(), nullable=True),
        sa.Column("division_id", sa.Integer(), nullable=True),
        sa.Column("franchise_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_defunct", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("city", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column("arena", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column("arena_capacity", sa.Integer(), nullable=True),
        sa.Column("relocation_history", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("team_id"),
        sa.ForeignKeyConstraint(["division_id"], ["division.division_id"]),
        sa.ForeignKeyConstraint(["franchise_id"], ["franchise.franchise_id"]),
        sa.UniqueConstraint("abbreviation"),
    )
    op.create_index(op.f("ix_team_name"), "team", ["name"])
    op.create_index(op.f("ix_team_abbreviation"), "team", ["abbreviation"])

    # Season table
    op.create_table(
        "season",
        sa.Column("season_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("league_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column(
            "season_name", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("all_star_date", sa.Date(), nullable=True),
        sa.Column("playoffs_start_date", sa.Date(), nullable=True),
        sa.Column("playoffs_end_date", sa.Date(), nullable=True),
        sa.Column("champion_team_id", sa.Integer(), nullable=True),
        sa.Column("runner_up_team_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="false"),
        sa.PrimaryKeyConstraint("season_id"),
        sa.ForeignKeyConstraint(["league_id"], ["league.league_id"]),
        sa.ForeignKeyConstraint(["champion_team_id"], ["team.team_id"]),
        sa.ForeignKeyConstraint(["runner_up_team_id"], ["team.team_id"]),
    )
    op.create_index(op.f("ix_season_year"), "season", ["year"])

    # Player table
    op.create_table(
        "player",
        sa.Column("player_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column(
            "first_name", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False
        ),
        sa.Column(
            "last_name", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False
        ),
        sa.Column(
            "middle_name", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True
        ),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column(
            "birth_place_city",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=True,
        ),
        sa.Column(
            "birth_place_country",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=True,
        ),
        sa.Column("death_date", sa.Date(), nullable=True),
        sa.Column("height_inches", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("weight_lbs", sa.Integer(), nullable=True),
        sa.Column(
            "position",
            sa.Enum(
                "POINT_GUARD",
                "SHOOTING_GUARD",
                "SMALL_FORWARD",
                "POWER_FORWARD",
                "CENTER",
                "GUARD",
                "FORWARD",
                name="player_position",
            ),
            nullable=True,
        ),
        sa.Column(
            "high_school", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True
        ),
        sa.Column(
            "college", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True
        ),
        sa.Column("draft_year", sa.Integer(), nullable=True),
        sa.Column("draft_pick", sa.Integer(), nullable=True),
        sa.Column("debut_date", sa.Date(), nullable=True),
        sa.Column("final_date", sa.Date(), nullable=True),
        sa.Column("debut_year", sa.Integer(), nullable=True),
        sa.Column("final_year", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("player_id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_player_slug"), "player", ["slug"])

    # Game table
    op.create_table(
        "game",
        sa.Column("game_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("game_date", sa.Date(), nullable=False),
        sa.Column("game_time", sa.Time(), nullable=True),
        sa.Column("home_team_id", sa.Integer(), nullable=False),
        sa.Column("away_team_id", sa.Integer(), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column(
            "season_type",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            server_default="REGULAR",
        ),
        sa.Column("arena", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column("attendance", sa.Integer(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("officials", sa.JSON(), nullable=True),
        sa.Column(
            "playoff_round", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True
        ),
        sa.Column("playoff_game_number", sa.Integer(), nullable=True),
        sa.Column("series_home_wins", sa.Integer(), nullable=True),
        sa.Column("series_away_wins", sa.Integer(), nullable=True),
        sa.Column(
            "box_score_url", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.Column(
            "play_by_play_url",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("game_id"),
        sa.ForeignKeyConstraint(["season_id"], ["season.season_id"]),
        sa.ForeignKeyConstraint(["home_team_id"], ["team.team_id"]),
        sa.ForeignKeyConstraint(["away_team_id"], ["team.team_id"]),
    )
    op.create_index(op.f("ix_game_season_id"), "game", ["season_id"])
    op.create_index(op.f("ix_game_game_date"), "game", ["game_date"])
    op.create_index(op.f("ix_game_home_team_id"), "game", ["home_team_id"])
    op.create_index(op.f("ix_game_away_team_id"), "game", ["away_team_id"])

    # BoxScore table
    op.create_table(
        "box_score",
        sa.Column("box_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("location", sa.Enum("HOME", "AWAY", name="location"), nullable=False),
        sa.Column("outcome", sa.Enum("WIN", "LOSS", name="outcome"), nullable=False),
        sa.Column("opponent_team_id", sa.Integer(), nullable=True),
        sa.Column("seconds_played", sa.Integer(), nullable=True),
        sa.Column("made_fg", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_fg", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("made_3pt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_3pt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("made_ft", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_ft", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "offensive_rebounds", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "defensive_rebounds", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("total_rebounds", sa.Integer(), nullable=True),
        sa.Column("assists", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("steals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blocks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("turnovers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("personal_fouls", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("points_scored", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("plus_minus", sa.Integer(), nullable=True),
        sa.Column(
            "field_goal_percentage", sa.Numeric(precision=5, scale=3), nullable=True
        ),
        sa.Column(
            "three_point_percentage", sa.Numeric(precision=5, scale=3), nullable=True
        ),
        sa.Column(
            "free_throw_percentage", sa.Numeric(precision=5, scale=3), nullable=True
        ),
        sa.Column("quarter_scores", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("box_id"),
        sa.ForeignKeyConstraint(["game_id"], ["game.game_id"]),
        sa.ForeignKeyConstraint(["team_id"], ["team.team_id"]),
        sa.ForeignKeyConstraint(["opponent_team_id"], ["team.team_id"]),
    )
    op.create_index(op.f("ix_box_score_game_id"), "box_score", ["game_id"])
    op.create_index(op.f("ix_box_score_team_id"), "box_score", ["team_id"])

    # PlayerBoxScore table
    op.create_table(
        "player_box_score",
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("box_id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column(
            "player_slug", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True
        ),
        sa.Column("player_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "position",
            sa.Enum(
                "POINT_GUARD",
                "SHOOTING_GUARD",
                "SMALL_FORWARD",
                "POWER_FORWARD",
                "CENTER",
                "GUARD",
                "FORWARD",
                name="player_position",
            ),
            nullable=True,
        ),
        sa.Column("is_starter", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("seconds_played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("made_fg", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_fg", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("made_3pt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_3pt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("made_ft", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_ft", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "offensive_rebounds", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "defensive_rebounds", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("assists", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("steals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blocks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("turnovers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("personal_fouls", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("points_scored", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("plus_minus", sa.Integer(), nullable=True),
        sa.Column("game_score", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.PrimaryKeyConstraint("player_id", "box_id"),
        sa.ForeignKeyConstraint(["player_id"], ["player.player_id"]),
        sa.ForeignKeyConstraint(["box_id"], ["box_score.box_id"]),
        sa.ForeignKeyConstraint(["game_id"], ["game.game_id"]),
        sa.ForeignKeyConstraint(["team_id"], ["team.team_id"]),
    )
    op.create_index(
        op.f("ix_player_box_score_game_id"), "player_box_score", ["game_id"]
    )
    op.create_index(
        op.f("ix_player_box_score_team_id"), "player_box_score", ["team_id"]
    )

    # PlayerSeason table
    op.create_table(
        "player_season",
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column(
            "season_type",
            sa.Enum("REGULAR", "PLAYOFF", "ALL_STAR", "PRESEASON", name="seasontype"),
            nullable=False,
            server_default="REGULAR",
        ),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("player_age", sa.Integer(), nullable=True),
        sa.Column(
            "position",
            sa.Enum(
                "POINT_GUARD",
                "SHOOTING_GUARD",
                "SMALL_FORWARD",
                "POWER_FORWARD",
                "CENTER",
                "GUARD",
                "FORWARD",
                name="player_position",
            ),
            nullable=True,
        ),
        sa.Column("games_played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("games_started", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("minutes_played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("made_fg", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_fg", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("made_3pt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_3pt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("made_ft", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_ft", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "offensive_rebounds", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "defensive_rebounds", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("total_rebounds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assists", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("steals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blocks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("turnovers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("personal_fouls", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("points_scored", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("double_doubles", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("triple_doubles", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "is_combined_totals", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.PrimaryKeyConstraint("player_id", "season_id", "season_type"),
        sa.ForeignKeyConstraint(["player_id"], ["player.player_id"]),
        sa.ForeignKeyConstraint(["season_id"], ["season.season_id"]),
        sa.ForeignKeyConstraint(["team_id"], ["team.team_id"]),
    )

    # PlayerSeasonAdvanced table
    op.create_table(
        "player_season_advanced",
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column(
            "season_type",
            sa.Enum("REGULAR", "PLAYOFF", "ALL_STAR", "PRESEASON", name="seasontype"),
            nullable=False,
            server_default="REGULAR",
        ),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("player_age", sa.Integer(), nullable=True),
        sa.Column("games_played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("minutes_played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "player_efficiency_rating", sa.Numeric(precision=6, scale=2), nullable=True
        ),
        sa.Column(
            "true_shooting_percentage", sa.Numeric(precision=5, scale=3), nullable=True
        ),
        sa.Column(
            "effective_fg_percentage", sa.Numeric(precision=5, scale=3), nullable=True
        ),
        sa.Column(
            "three_point_attempt_rate", sa.Numeric(precision=5, scale=3), nullable=True
        ),
        sa.Column(
            "free_throw_attempt_rate", sa.Numeric(precision=5, scale=3), nullable=True
        ),
        sa.Column("usage_percentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("assist_percentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column(
            "turnover_percentage", sa.Numeric(precision=5, scale=2), nullable=True
        ),
        sa.Column(
            "offensive_rebound_percentage",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
        ),
        sa.Column(
            "defensive_rebound_percentage",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
        ),
        sa.Column(
            "total_rebound_percentage", sa.Numeric(precision=5, scale=2), nullable=True
        ),
        sa.Column("steal_percentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("block_percentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column(
            "offensive_box_plus_minus", sa.Numeric(precision=5, scale=2), nullable=True
        ),
        sa.Column(
            "defensive_box_plus_minus", sa.Numeric(precision=5, scale=2), nullable=True
        ),
        sa.Column("box_plus_minus", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column(
            "value_over_replacement_player",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
        ),
        sa.Column(
            "offensive_win_shares", sa.Numeric(precision=6, scale=3), nullable=True
        ),
        sa.Column(
            "defensive_win_shares", sa.Numeric(precision=6, scale=3), nullable=True
        ),
        sa.Column("win_shares", sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column("win_shares_per_48", sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column(
            "is_combined_totals", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.PrimaryKeyConstraint("player_id", "season_id", "season_type"),
        sa.ForeignKeyConstraint(["player_id"], ["player.player_id"]),
        sa.ForeignKeyConstraint(["season_id"], ["season.season_id"]),
        sa.ForeignKeyConstraint(["team_id"], ["team.team_id"]),
    )

    # TeamSeason table
    op.create_table(
        "team_season",
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column(
            "season_type",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            server_default="REGULAR",
        ),
        sa.Column("games_played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("losses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("home_wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("home_losses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("road_wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("road_losses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("conference_wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "conference_losses", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("division_wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("division_losses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("win_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("loss_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "longest_win_streak", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "longest_loss_streak", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("points_scored", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("points_allowed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("points_per_game", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column(
            "points_allowed_per_game", sa.Numeric(precision=5, scale=2), nullable=True
        ),
        sa.Column("minutes_played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("made_fg", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_fg", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("made_3pt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_3pt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("made_ft", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_ft", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "offensive_rebounds", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "defensive_rebounds", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("total_rebounds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assists", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("steals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blocks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("turnovers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("personal_fouls", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pace", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("offensive_rating", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("defensive_rating", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("net_rating", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("playoff_seed", sa.Integer(), nullable=True),
        sa.Column(
            "made_playoffs", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "playoff_round_reached",
            sqlmodel.sql.sqltypes.AutoString(length=50),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("team_id", "season_id", "season_type"),
        sa.ForeignKeyConstraint(["team_id"], ["team.team_id"]),
        sa.ForeignKeyConstraint(["season_id"], ["season.season_id"]),
    )

    # PlayByPlay table
    op.create_table(
        "play_by_play",
        sa.Column("play_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("period", sa.Integer(), nullable=False),
        sa.Column(
            "period_type",
            sa.Enum("QUARTER", "OVERTIME", name="periodtype"),
            nullable=False,
        ),
        sa.Column("seconds_remaining", sa.Integer(), nullable=False),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column(
            "play_type",
            sa.Enum(
                "FIELD_GOAL_MADE",
                "FIELD_GOAL_MISSED",
                "FREE_THROW_MADE",
                "FREE_THROW_MISSED",
                "REBOUND_OFFENSIVE",
                "REBOUND_DEFENSIVE",
                "ASSIST",
                "STEAL",
                "BLOCK",
                "TURNOVER",
                "FOUL_PERSONAL",
                "FOUL_TECHNICAL",
                "FOUL_FLAGRANT",
                "TIMEOUT",
                "SUBSTITUTION",
                "VIOLATION",
                "JUMP_BALL",
                "PERIOD_START",
                "PERIOD_END",
                name="playtype",
            ),
            nullable=False,
        ),
        sa.Column("player_involved_id", sa.Integer(), nullable=True),
        sa.Column("assist_player_id", sa.Integer(), nullable=True),
        sa.Column("block_player_id", sa.Integer(), nullable=True),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("shot_distance_ft", sa.Integer(), nullable=True),
        sa.Column(
            "shot_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True
        ),
        sa.Column(
            "foul_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True
        ),
        sa.Column("points_scored", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "is_fast_break", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "is_second_chance", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.PrimaryKeyConstraint("play_id"),
        sa.ForeignKeyConstraint(["game_id"], ["game.game_id"]),
        sa.ForeignKeyConstraint(["team_id"], ["team.team_id"]),
        sa.ForeignKeyConstraint(["player_involved_id"], ["player.player_id"]),
        sa.ForeignKeyConstraint(["assist_player_id"], ["player.player_id"]),
        sa.ForeignKeyConstraint(["block_player_id"], ["player.player_id"]),
    )
    op.create_index(op.f("ix_play_by_play_game_id"), "play_by_play", ["game_id"])

    # Award tables
    op.create_table(
        "award",
        sa.Column("award_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "MOST_VALUABLE_PLAYER",
                "CHAMPIONSHIP",
                "FINALS_MVP",
                "DEFENSIVE_PLAYER_OF_THE_YEAR",
                "ROOKIE_OF_THE_YEAR",
                "COACH_OF_THE_YEAR",
                "SIXTH_MAN",
                "MOST_IMPROVED",
                "ALL_NBA_FIRST_TEAM",
                "ALL_NBA_SECOND_TEAM",
                "ALL_NBA_THIRD_TEAM",
                "ALL_DEFENSIVE_FIRST_TEAM",
                "ALL_DEFENSIVE_SECOND_TEAM",
                "ALL_ROOKIE_FIRST_TEAM",
                "ALL_ROOKIE_SECOND_TEAM",
                "ALL_STAR",
                name="awardcategory",
            ),
            nullable=False,
        ),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("first_awarded_year", sa.Integer(), nullable=True),
        sa.Column("last_awarded_year", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("award_id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "award_recipient",
        sa.Column("award_id", sa.Integer(), nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("vote_rank", sa.Integer(), nullable=True),
        sa.Column("vote_count", sa.Integer(), nullable=True),
        sa.Column("vote_percentage", sa.Float(), nullable=True),
        sa.Column("first_place_votes", sa.Integer(), nullable=True),
        sa.Column(
            "recipient_type",
            sa.Enum("PLAYER", "TEAM", "COACH", name="recipienttype"),
            nullable=True,
        ),
        sa.Column("notes", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("award_id", "season_id"),
        sa.ForeignKeyConstraint(["award_id"], ["award.award_id"]),
        sa.ForeignKeyConstraint(["season_id"], ["season.season_id"]),
        sa.ForeignKeyConstraint(["player_id"], ["player.player_id"]),
        sa.ForeignKeyConstraint(["team_id"], ["team.team_id"]),
    )

    # Draft tables
    op.create_table(
        "draft",
        sa.Column("draft_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("draft_date", sa.Date(), nullable=True),
        sa.Column("round_count", sa.Integer(), nullable=False),
        sa.Column("pick_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("draft_id"),
        sa.ForeignKeyConstraint(["season_id"], ["season.season_id"]),
        sa.UniqueConstraint("season_id"),
    )
    op.create_index(op.f("ix_draft_year"), "draft", ["year"])

    op.create_table(
        "draft_pick",
        sa.Column("pick_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("draft_id", sa.Integer(), nullable=False),
        sa.Column("overall_pick", sa.Integer(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("round_pick", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=True),
        sa.Column("original_team_id", sa.Integer(), nullable=True),
        sa.Column("trade_notes", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "college", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True
        ),
        sa.Column("height_in", sa.Integer(), nullable=True),
        sa.Column("weight_lbs", sa.Integer(), nullable=True),
        sa.Column(
            "position",
            sa.Enum(
                "POINT_GUARD",
                "SHOOTING_GUARD",
                "SMALL_FORWARD",
                "POWER_FORWARD",
                "CENTER",
                "GUARD",
                "FORWARD",
                name="player_position",
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("pick_id"),
        sa.ForeignKeyConstraint(["draft_id"], ["draft.draft_id"]),
        sa.ForeignKeyConstraint(["team_id"], ["team.team_id"]),
        sa.ForeignKeyConstraint(["player_id"], ["player.player_id"]),
        sa.ForeignKeyConstraint(["original_team_id"], ["team.team_id"]),
    )
    op.create_index(op.f("ix_draft_pick_draft_id"), "draft_pick", ["draft_id"])
    op.create_index(op.f("ix_draft_pick_team_id"), "draft_pick", ["team_id"])


def downgrade() -> None:
    # Drop in reverse order of creation (respecting foreign keys)
    op.drop_table("draft_pick")
    op.drop_table("draft")
    op.drop_table("award_recipient")
    op.drop_table("award")
    op.drop_table("play_by_play")
    op.drop_table("team_season")
    op.drop_table("player_season_advanced")
    op.drop_table("player_season")
    op.drop_table("player_box_score")
    op.drop_table("box_score")
    op.drop_table("game")
    op.drop_table("player")
    op.drop_table("season")
    op.drop_table("team")
    op.drop_table("franchise")
    op.drop_table("division")
    op.drop_table("conference")
    op.drop_table("league")

    # Drop enums
    sa.Enum(name="player_position").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="seasontype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="location").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="outcome").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="periodtype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="playtype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="leaguetype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="conferencetype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="divisiontype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="awardcategory").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="recipienttype").drop(op.get_bind(), checkfirst=True)
