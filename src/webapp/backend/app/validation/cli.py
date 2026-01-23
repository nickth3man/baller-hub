"""CLI command for running database validation."""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).parents[3])]

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.validation.models import ValidationRun
from app.validation.runner import DatabaseValidator, ValidationReporter

logger = structlog.get_logger(__name__)


async def run_validation(
    output_format: str = "console",
    save_to_db: bool = False,
    tables: list[str] | None = None,
) -> None:
    """Run database validation and output results.

    Args:
        output_format: Output format (console, json)
        save_to_db: Whether to save results to database
        tables: Specific tables to validate (None = all tables)
    """

    async with async_session_factory() as session:
        validator = DatabaseValidator(session)

        result = await validator.run_all_checks()

        if output_format == "console":
            ValidationReporter.generate_console_report(result)
        elif output_format == "json":
            ValidationReporter.generate_json_report(result)

            if save_to_db:
                validation_run = ValidationRun(
                    run_id=result.run_id,
                    timestamp=result.timestamp,
                    target_tables=result.target_tables,
                    summary=result.summary.model_dump(),
                    issues=[issue.model_dump() for issue in result.issues],
                    duration_seconds=result.summary.duration_seconds,
                    triggered_by="manual_cli",
                )
                session.add(validation_run)
                await session.commit()

        if result.summary.critical_issues > 0:
            sys.exit(1)
        elif result.summary.major_issues > 0:
            sys.exit(2)
        else:
            sys.exit(0)


async def create_validation_tables(session: AsyncSession) -> None:
    """Create validation tables in database."""

    await session.execute(
        text("""
        CREATE TABLE IF NOT EXISTS validation_run (
            run_id VARCHAR(50) PRIMARY KEY,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            target_tables JSONB,
            summary JSONB,
            issues JSONB,
            duration_seconds FLOAT NOT NULL DEFAULT 0.0,
            triggered_by VARCHAR(50) DEFAULT 'manual',
            git_commit VARCHAR(50)
        )
    """)
    )

    await session.execute(
        text("""
        CREATE INDEX IF NOT EXISTS idx_validation_run_timestamp
        ON validation_run(timestamp DESC)
    """)
    )

    await session.execute(
        text("""
        CREATE INDEX IF NOT EXISTS idx_validation_run_triggered_by
        ON validation_run(triggered_by)
    """)
    )

    await session.commit()


async def check_database_connection(session: AsyncSession) -> bool:
    """Check if database connection is working."""
    try:
        result = await session.execute(text("SELECT 1"))
        result.fetchone()
    except Exception as e:
        logger.exception("Database connection failed", error=str(e))
        return False
    else:
        return True


async def main() -> None:
    """Main entry point for validation CLI."""
    parser = argparse.ArgumentParser(
        description="Run database validation for Baller Hub"
    )

    parser.add_argument(
        "--format",
        choices=["console", "json"],
        default="console",
        help="Output format (default: console)",
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save validation results to database",
    )

    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize validation tables in database",
    )

    parser.add_argument(
        "--check-connection",
        action="store_true",
        help="Check database connection",
    )

    args = parser.parse_args()

    async with async_session_factory() as session:
        if args.check_connection:
            if await check_database_connection(session):
                sys.exit(0)
            else:
                sys.exit(1)

        if args.init:
            await create_validation_tables(session)
            sys.exit(0)

        await run_validation(
            output_format=args.format,
            save_to_db=args.save,
        )


if __name__ == "__main__":
    asyncio.run(main())
