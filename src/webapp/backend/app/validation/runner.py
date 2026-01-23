"""Validation runner for database data quality checks.

This module provides comprehensive validation for Baller Hub database
including referential integrity, data consistency, business logic, and data quality.
"""

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.validation.models import (
    Category,
    Severity,
    ValidationIssue,
    ValidationResult,
    ValidationSummary,
)

logger = structlog.get_logger(__name__)


class DatabaseValidator:
    """Main validator class for running database validation checks."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.results: list[ValidationIssue] = []

    async def run_all_checks(self) -> ValidationResult:
        """Run all validation checks.

        Returns:
            ValidationResult with all findings.
        """
        start_time = datetime.now(UTC)
        self.results.clear()

        logger.info("Starting comprehensive database validation")

        try:
            await self._check_critical_foreign_keys()
            await self._check_game_teams_different()
            await self._check_game_scores_match_box_scores()
            await self._check_season_dates_valid()
            await self._check_no_negative_statistics()
            await self._check_orphaned_players()
            await self._check_orphaned_games()
            await self._check_box_score_player_totals()
            await self._check_valid_position_enums()
            await self._check_valid_season_type_enums()
            await self._check_height_weight_ranges()
            await self._check_player_age_ranges()
            await self._check_team_abbreviation_unique()

        except Exception as e:
            logger.exception("Validation run failed", error=str(e))
            raise

        duration = (datetime.now(UTC) - start_time).total_seconds()

        summary = self._build_summary()
        return ValidationResult(
            run_id=str(uuid.uuid4()),
            timestamp=datetime.now(UTC),
            target_tables=[
                "game",
                "player",
                "box_score",
                "player_box_score",
                "player_season",
                "team_season",
                "team",
                "season",
            ],
            summary=summary,
            issues=self.results,
            duration_seconds=duration,
        )

    def _build_summary(self) -> ValidationSummary:
        """Build summary from collected results."""
        total_rules = 12
        rules_passed = total_rules - len({r.rule_id for r in self.results})
        rules_failed = len({r.rule_id for r in self.results})

        critical_issues = len(
            [r for r in self.results if r.severity == Severity.CRITICAL]
        )
        major_issues = len([r for r in self.results if r.severity == Severity.MAJOR])
        minor_issues = len([r for r in self.results if r.severity == Severity.MINOR])

        total_rows_checked = 0
        total_affected_rows = sum(r.affected_count for r in self.results)

        success_rate = (rules_passed / total_rules * 100) if total_rules > 0 else 100.0

        return ValidationSummary(
            total_rules=total_rules,
            rules_passed=rules_passed,
            rules_failed=rules_failed,
            critical_issues=critical_issues,
            major_issues=major_issues,
            minor_issues=minor_issues,
            total_rows_checked=total_rows_checked,
            total_affected_rows=total_affected_rows,
            success_rate=success_rate,
            duration_seconds=0.0,
        )

    async def _add_issue(  # noqa: PLR0913
        self,
        rule_id: str,
        rule_name: str,
        severity: Severity,
        category: Category,
        table_name: str,
        row_identifier: Any | None = None,
        error_type: str = "",
        error_message: str = "",
        expected_value: str | None = None,
        actual_value: str | None = None,
    ) -> None:
        """Add a validation issue to results."""
        issue = ValidationIssue(
            rule_id=rule_id,
            rule_name=rule_name,
            severity=severity,
            category=category,
            table_name=table_name,
            row_identifier=row_identifier,
            error_type=error_type,
            error_message=error_message,
            expected_value=expected_value,
            actual_value=actual_value,
            affected_count=1,
        )
        self.results.append(issue)

    async def _check_critical_foreign_keys(self) -> None:
        """Check for foreign key violations across all tables."""
        logger.info("Checking foreign key violations")

        query = text("""
            SELECT
                'game' AS table_name,
                game_id::text AS record_id,
                home_team_id,
                away_team_id,
                season_id,
                'Invalid home_team_id or away_team_id or season_id' AS violation_type
            FROM game
            WHERE home_team_id NOT IN (SELECT team_id FROM team)
               OR away_team_id NOT IN (SELECT team_id FROM team)
               OR season_id NOT IN (SELECT season_id FROM season)
        """)

        result = await self.session.execute(query)
        for row in result:
            await self._add_issue(
                rule_id="C1_FK_VIOLATIONS",
                rule_name="Foreign Key Violations",
                severity=Severity.CRITICAL,
                category=Category.REFERENTIAL_INTEGRITY,
                table_name=row.table_name,
                row_identifier=row.record_id,
                error_type="foreign_key_violation",
                error_message=row.violation_type,
                actual_value=f"home_team_id={row.home_team_id}, away_team_id={row.away_team_id}, season_id={row.season_id}",
            )

        affected = result.rowcount
        if affected > 0:
            logger.warning("Found foreign key violations", count=affected)

    async def _check_game_teams_different(self) -> None:
        """Check that home and away teams are different."""
        logger.info("Checking game teams are different")

        query = text("""
            SELECT
                game_id::text AS record_id,
                home_team_id,
                away_team_id,
                'Same team as home and away' AS violation_type
            FROM game
            WHERE home_team_id = away_team_id
        """)

        result = await self.session.execute(query)
        for row in result:
            await self._add_issue(
                rule_id="C4_GAME_TEAMS_DIFFERENT",
                rule_name="Game Teams Different",
                severity=Severity.CRITICAL,
                category=Category.BUSINESS_LOGIC,
                table_name="game",
                row_identifier=row.record_id,
                error_type="business_rule_violation",
                error_message="Home team cannot be same as away team",
                actual_value=f"home_team_id={row.home_team_id}, away_team_id={row.away_team_id}",
            )

        if result.rowcount > 0:
            logger.warning(
                "Found games with same home/away team", count=result.rowcount
            )

    async def _check_game_scores_match_box_scores(self) -> None:
        """Check that game scores match box score totals."""
        logger.info("Checking game scores match box scores")

        query = text("""
            SELECT
                'game_box_score' AS table_name,
                g.game_id::text AS record_id,
                g.game_date,
                g.home_score AS game_home_score,
                bs_home.points_scored AS box_home_points,
                g.away_score AS game_away_score,
                bs_away.points_scored AS box_away_points,
                g.home_score - bs_home.points_scored AS home_diff,
                g.away_score - bs_away.points_scored AS away_diff,
                'Game score does not match box score' AS violation_type
            FROM game g
            JOIN box_score bs_home ON g.game_id = bs_home.game_id
                AND g.home_team_id = bs_home.team_id
                AND bs_home.location = 'HOME'
            JOIN box_score bs_away ON g.game_id = bs_away.game_id
                AND g.away_team_id = bs_away.team_id
                AND bs_away.location = 'AWAY'
            WHERE (g.home_score != bs_home.points_scored
               OR g.away_score != bs_away.points_scored)
            LIMIT 50
        """)

        result = await self.session.execute(query)
        for row in result:
            await self._add_issue(
                rule_id="C5_GAME_SCORES_MATCH_BOX",
                rule_name="Game Scores Match Box Scores",
                severity=Severity.CRITICAL,
                category=Category.DATA_CONSISTENCY,
                table_name=row.table_name,
                row_identifier=row.record_id,
                error_type="score_mismatch",
                error_message="Game score does not match box score",
                actual_value=f"Home: game={row.game_home_score}, box={row.box_home_points} | Away: game={row.game_away_score}, box={row.box_away_points}",
            )

        if result.rowcount > 0:
            logger.warning("Found score mismatches", count=result.rowcount)

    async def _check_season_dates_valid(self) -> None:
        """Check that season start date is before end date."""
        logger.info("Checking season date validity")

        query = text("""
            SELECT
                season_id::text AS record_id,
                year,
                season_name,
                start_date,
                end_date,
                'Season start date after end date' AS violation_type
            FROM season
            WHERE start_date > end_date
        """)

        result = await self.session.execute(query)
        for row in result:
            await self._add_issue(
                rule_id="C6_SEASON_DATES_VALID",
                rule_name="Season Dates Valid",
                severity=Severity.CRITICAL,
                category=Category.BUSINESS_LOGIC,
                table_name="season",
                row_identifier=row.record_id,
                error_type="date_order_violation",
                error_message="Season start date after end date",
                actual_value=f"start_date={row.start_date}, end_date={row.end_date}",
            )

        if result.rowcount > 0:
            logger.warning("Found invalid season dates", count=result.rowcount)

    async def _check_no_negative_statistics(self) -> None:
        """Check for negative statistics values."""
        logger.info("Checking for negative statistics")

        query = text("""
            SELECT
                'player_box_score' AS table_name,
                player_id::text || '_' || game_id::text AS record_id,
                'points_scored' AS stat_column,
                points_scored::text AS negative_value,
                'Negative statistic value' AS violation_type
            FROM player_box_score
            WHERE points_scored < 0
            UNION ALL
            SELECT
                'player_box_score' AS table_name,
                player_id::text || '_' || game_id::text AS record_id,
                'made_fg' AS stat_column,
                made_fg::text AS negative_value,
                'Negative statistic value' AS violation_type
            FROM player_box_score
            WHERE made_fg < 0
            UNION ALL
            SELECT
                'player_box_score' AS table_name,
                player_id::text || '_' || game_id::text AS record_id,
                'attempted_fg' AS stat_column,
                attempted_fg::text AS negative_value,
                'Negative statistic value' AS violation_type
            FROM player_box_score
            WHERE attempted_fg < 0
            LIMIT 50
        """)

        result = await self.session.execute(query)
        for row in result:
            await self._add_issue(
                rule_id="C7_NO_NEGATIVE_STATS",
                rule_name="No Negative Statistics",
                severity=Severity.CRITICAL,
                category=Category.DATA_QUALITY,
                table_name=row.table_name,
                row_identifier=row.record_id,
                error_type="negative_value",
                error_message=f"Negative value in {row.stat_column}",
                actual_value=f"{row.stat_column}={row.negative_value}",
            )

        if result.rowcount > 0:
            logger.warning("Found negative statistics", count=result.rowcount)

    async def _check_orphaned_players(self) -> None:
        """Check for players without box scores or seasons."""
        logger.info("Checking for orphaned players")

        query = text("""
            SELECT
                p.player_id::text AS record_id,
                p.first_name,
                p.last_name,
                p.is_active,
                'Player has no box scores' AS violation_type
            FROM player p
            LEFT JOIN player_box_score pbs ON p.player_id = pbs.player_id
            GROUP BY p.player_id, p.first_name, p.last_name, p.is_active
            HAVING COUNT(pbs.player_id) = 0
            LIMIT 20
        """)

        result = await self.session.execute(query)
        for row in result:
            severity = Severity.CRITICAL if row.is_active else Severity.MAJOR
            await self._add_issue(
                rule_id="M1_ORPHANED_PLAYERS",
                rule_name="Orphaned Players",
                severity=severity,
                category=Category.REFERENTIAL_INTEGRITY,
                table_name="player",
                row_identifier=row.record_id,
                error_type="orphaned_record",
                error_message="Player has no associated box scores",
                actual_value=f"{row.first_name} {row.last_name} (active={row.is_active})",
            )

        if result.rowcount > 0:
            logger.warning("Found orphaned players", count=result.rowcount)

    async def _check_orphaned_games(self) -> None:
        """Check for games without box scores."""
        logger.info("Checking for orphaned games")

        query = text("""
            SELECT
                g.game_id::text AS record_id,
                g.game_date,
                g.home_team_id,
                g.away_team_id,
                COUNT(bs.box_id) AS box_score_count,
                'Game has no box scores' AS violation_type
            FROM game g
            LEFT JOIN box_score bs ON g.game_id = bs.game_id
            GROUP BY g.game_id, g.game_date, g.home_team_id, g.away_team_id
            HAVING COUNT(bs.box_id) = 0
            LIMIT 20
        """)

        result = await self.session.execute(query)
        for row in result:
            await self._add_issue(
                rule_id="M2_ORPHANED_GAMES",
                rule_name="Orphaned Games",
                severity=Severity.MAJOR,
                category=Category.REFERENTIAL_INTEGRITY,
                table_name="game",
                row_identifier=row.record_id,
                error_type="orphaned_record",
                error_message="Game has no associated box scores",
                actual_value=f"game_date={row.game_date}, home={row.home_team_id}, away={row.away_team_id}",
            )

        if result.rowcount > 0:
            logger.warning("Found orphaned games", count=result.rowcount)

    async def _check_box_score_player_totals(self) -> None:
        """Check that box score totals match player aggregations."""
        logger.info("Checking box score totals match player totals")

        query = text("""
            SELECT
                'box_score' AS table_name,
                bs.box_id::text AS record_id,
                bs.game_id,
                bs.team_id,
                bs.points_scored AS team_points,
                agg.sum_player_points,
                bs.assists AS team_assists,
                agg.sum_player_assists,
                bs.made_fg AS team_fg_made,
                agg.sum_player_fg_made,
                ABS(bs.points_scored - agg.sum_player_points) AS point_diff,
                'Box score totals do not match player totals' AS violation_type
            FROM box_score bs
            LEFT JOIN (
                SELECT
                    box_id,
                    SUM(points_scored) AS sum_player_points,
                    SUM(assists) AS sum_player_assists,
                    SUM(made_fg) AS sum_player_fg_made
                FROM player_box_score
                GROUP BY box_id
            ) agg ON bs.box_id = agg.box_id
            WHERE bs.points_scored != agg.sum_player_points
               OR bs.assists != agg.sum_player_assists
               OR bs.made_fg != agg.sum_player_fg_made
            LIMIT 20
        """)

        result = await self.session.execute(query)
        for row in result:
            await self._add_issue(
                rule_id="M5_BOX_SCORE_PLAYER_TOTALS",
                rule_name="Box Score Player Totals",
                severity=Severity.MAJOR,
                category=Category.DATA_CONSISTENCY,
                table_name=row.table_name,
                row_identifier=row.record_id,
                error_type="aggregation_mismatch",
                error_message="Box score totals do not match player aggregations",
                actual_value=f"Points: team={row.team_points}, sum={row.sum_player_points} | Assists: team={row.team_assists}, sum={row.sum_player_assists}",
            )

        if result.rowcount > 0:
            logger.warning("Found box score mismatches", count=result.rowcount)

    async def _check_valid_position_enums(self) -> None:
        """Check for invalid position enum values."""
        logger.info("Checking position enum validity")

        valid_positions = [
            "POINT_GUARD",
            "SHOOTING_GUARD",
            "SMALL_FORWARD",
            "POWER_FORWARD",
            "CENTER",
            "GUARD",
            "FORWARD",
        ]

        query = text(f"""
            SELECT
                'player' AS table_name,
                player_id::text AS record_id,
                first_name,
                last_name,
                position,
                'Invalid position enum value' AS violation_type
            FROM player
            WHERE position IS NOT NULL
              AND position NOT IN ({",".join(f"'{p}'" for p in valid_positions)})
            LIMIT 20
        """)

        result = await self.session.execute(query)
        for row in result:
            await self._add_issue(
                rule_id="M6_VALID_POSITION_ENUMS",
                rule_name="Valid Position Enums",
                severity=Severity.MAJOR,
                category=Category.DATA_QUALITY,
                table_name=row.table_name,
                row_identifier=row.record_id,
                error_type="invalid_enum_value",
                error_message="Invalid position enum value",
                actual_value=f"position={row.position}",
                expected_value=f"One of: {', '.join(valid_positions)}",
            )

        if result.rowcount > 0:
            logger.warning("Found invalid position values", count=result.rowcount)

    async def _check_valid_season_type_enums(self) -> None:
        """Check for invalid season type enum values."""
        logger.info("Checking season type enum validity")

        valid_season_types = ["REGULAR", "PLAYOFF", "ALL_STAR", "PRESEASON"]

        query = text(f"""
            SELECT
                'game' AS table_name,
                game_id::text AS record_id,
                game_date,
                season_type,
                'Invalid season_type enum value' AS violation_type
            FROM game
            WHERE season_type NOT IN ({",".join(f"'{t}'" for t in valid_season_types)})
            LIMIT 20
        """)

        result = await self.session.execute(query)
        for row in result:
            await self._add_issue(
                rule_id="M7_VALID_SEASON_TYPE_ENUMS",
                rule_name="Valid Season Type Enums",
                severity=Severity.MAJOR,
                category=Category.DATA_QUALITY,
                table_name=row.table_name,
                row_identifier=row.record_id,
                error_type="invalid_enum_value",
                error_message="Invalid season_type enum value",
                actual_value=f"season_type={row.season_type}",
                expected_value=f"One of: {', '.join(valid_season_types)}",
            )

        if result.rowcount > 0:
            logger.warning("Found invalid season type values", count=result.rowcount)

    async def _check_height_weight_ranges(self) -> None:
        """Check that height and weight are within NBA ranges."""
        logger.info("Checking height and weight ranges")

        query = text("""
            SELECT
                'player' AS table_name,
                player_id::text AS record_id,
                first_name,
                last_name,
                height_inches,
                'Height outside realistic NBA range (66-90 inches)' AS violation_type
            FROM player
            WHERE height_inches IS NOT NULL
              AND (height_inches < 66 OR height_inches > 90)
            UNION ALL
            SELECT
                'player' AS table_name,
                player_id::text AS record_id,
                first_name,
                last_name,
                weight_lbs,
                'Weight outside realistic NBA range (150-400 lbs)' AS violation_type
            FROM player
            WHERE weight_lbs IS NOT NULL
              AND (weight_lbs < 150 OR weight_lbs > 400)
            LIMIT 20
        """)

        result = await self.session.execute(query)
        for row in result:
            await self._add_issue(
                rule_id="M9_HEIGHT_WEIGHT_RANGES",
                rule_name="Height Weight Ranges",
                severity=Severity.MAJOR,
                category=Category.BUSINESS_LOGIC,
                table_name=row.table_name,
                row_identifier=row.record_id,
                error_type="value_out_of_range",
                error_message=row.violation_type,
                actual_value=f"{row.first_name} {row.last_name} - height={row.height_inches}, weight={row.weight_lbs}",
            )

        if result.rowcount > 0:
            logger.warning("Found height/weight out of range", count=result.rowcount)

    async def _check_player_age_ranges(self) -> None:
        """Check that active player ages are reasonable."""
        logger.info("Checking player age ranges")

        query = text("""
            SELECT
                'player' AS table_name,
                player_id::text AS record_id,
                first_name,
                last_name,
                birth_date,
                is_active,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date)) AS current_age,
                'Active player age outside realistic range (18-45)' AS violation_type
            FROM player
            WHERE is_active = true
              AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date)) < 18
            LIMIT 20
        """)

        result = await self.session.execute(query)
        for row in result:
            await self._add_issue(
                rule_id="M10_PLAYER_AGE_RANGES",
                rule_name="Player Age Ranges",
                severity=Severity.CRITICAL,
                category=Category.BUSINESS_LOGIC,
                table_name=row.table_name,
                row_identifier=row.record_id,
                error_type="age_out_of_range",
                error_message="Active player age outside realistic range",
                actual_value=f"{row.first_name} {row.last_name} - age={row.current_age}, active={row.is_active}",
            )

        if result.rowcount > 0:
            logger.warning("Found player age issues", count=result.rowcount)

    async def _check_team_abbreviation_unique(self) -> None:
        """Check for duplicate team abbreviations."""
        logger.info("Checking team abbreviation uniqueness")

        query = text("""
            SELECT
                'team' AS table_name,
                abbreviation AS record_id,
                name,
                COUNT(*) AS count,
                'Duplicate team abbreviation' AS violation_type
            FROM team
            GROUP BY abbreviation, name
            HAVING COUNT(*) > 1
        """)

        result = await self.session.execute(query)
        for row in result:
            await self._add_issue(
                rule_id="m1_TEAM_ABBREV_UNIQUE",
                rule_name="Team Abbreviation Unique",
                severity=Severity.MINOR,
                category=Category.DATA_QUALITY,
                table_name=row.table_name,
                row_identifier=row.record_id,
                error_type="duplicate_value",
                error_message="Duplicate team abbreviation",
                actual_value=f"abbreviation={row.record_id}, count={row.count}",
            )

        if result.rowcount > 0:
            logger.warning("Found duplicate team abbreviations", count=result.rowcount)


class ValidationReporter:
    """Generate reports from validation results."""

    @staticmethod
    def generate_console_report(result: ValidationResult) -> str:
        """Generate a console-friendly report."""
        if not result.issues:
            return "\n" + "=" * 60 + "\n✅ No validation issues found!\n" + "=" * 60

        lines = [
            "=" * 60,
            "DATABASE VALIDATION REPORT",
            "=" * 60,
            f"Run ID: {result.run_id}",
            f"Timestamp: {result.timestamp}",
            f"Duration: {result.summary.duration_seconds:.2f}s",
            "",
            "-" * 60,
            f"TOTAL RULES: {result.summary.total_rules}",
            f"RULES PASSED: {result.summary.rules_passed}",
            f"RULES FAILED: {result.summary.rules_failed}",
            f"SUCCESS RATE: {result.summary.success_rate:.1f}%",
            "",
            "-" * 60,
            f"CRITICAL: {result.summary.critical_issues} {'🔴' if result.summary.critical_issues > 0 else ''}",
            f"MAJOR: {result.summary.major_issues} {'🟠' if result.summary.major_issues > 0 else ''}",
            f"MINOR: {result.summary.minor_issues} {'🟡' if result.summary.minor_issues > 0 else ''}",
            "",
        ]

        if result.summary.critical_issues > 0:
            lines.append("CRITICAL ISSUES:")
            critical = [i for i in result.issues if i.severity == Severity.CRITICAL][
                :10
            ]
            for issue in critical:
                lines.append(
                    f"  [{issue.rule_id}] {issue.table_name}: {issue.error_message}"
                )
                if issue.row_identifier:
                    lines.append(f"    ID: {issue.row_identifier}")
            if result.summary.critical_issues > 10:  # noqa: PLR2004
                lines.append(
                    f"  ... and {result.summary.critical_issues - 10} more critical issues"
                )
            lines.append("")

        if result.summary.major_issues > 0:
            lines.append("MAJOR ISSUES:")
            major = [i for i in result.issues if i.severity == Severity.MAJOR][:10]
            lines.extend(
                f"  [{issue.rule_id}] {issue.table_name}: {issue.error_message}"
                for issue in major
            )
            if result.summary.major_issues > 10:  # noqa: PLR2004
                lines.append(
                    f"  ... and {result.summary.major_issues - 10} more major issues"
                )
            lines.append("")

        if result.summary.minor_issues > 0:
            lines.append("MINOR ISSUES:")
            minor = [i for i in result.issues if i.severity == Severity.MINOR][:10]
            lines.extend(
                f"  [{issue.rule_id}] {issue.table_name}: {issue.error_message}"
                for issue in minor
            )
            if result.summary.minor_issues > 10:  # noqa: PLR2004
                lines.append(
                    f"  ... and {result.summary.minor_issues - 10} more minor issues"
                )
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    @staticmethod
    def generate_json_report(result: ValidationResult) -> str:
        """Generate a JSON report."""
        return json.dumps(result.model_dump(mode="json"), indent=2, default=str)
