#!/usr/bin/env python3
"""Data seeding script for the basketball-reference webapp.

This script populates the database with initial data by scraping
basketball-reference.com and persisting to PostgreSQL or by loading
CSV datasets through the staging ingestion pipeline.

Usage:
  cd src/webapp
  python -m scripts.seed_db --season 2024

Options:
  --season YEAR         Seed a specific season end year (e.g., 2024 for 2023-24)
  --all                 Seed all available seasons (2020-current)
  --daily DATE          Seed box scores for a specific date (YYYY-MM-DD)
  --teams               Seed the 30 current NBA teams
  --yesterday           Seed yesterday's box scores
  --csv                 Ingest CSV datasets into the database
  --csv-play-by-play    Include play-by-play CSV ingestion (large)
  --index               Rebuild Meilisearch indices from the database
  --bootstrap           Run CSV ingestion and rebuild search indices
"""

import argparse
import asyncio
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# Add the backend and repo root directories to sys.path for imports.
repo_root = Path(__file__).resolve().parents[3]
backend_dir = repo_root / "src" / "webapp" / "backend"
sys.path[:0] = [str(backend_dir), str(repo_root)]


async def seed_season(season_end_year: int) -> None:
    """
    Prints season headers and a deprecation notice for seeding the specified season.
    
    Parameters:
        season_end_year (int): The calendar year in which the season ends (e.g., 2024 for the 2023–24 season).
    """
    print(f"\n{'=' * 60}")
    print(f"Seeding season {season_end_year - 1}-{str(season_end_year)[2:]}")
    print(f"{'=' * 60}")
    print(
        "\n[DEPRECATED] seed_season relies on the ingestion module which has been removed."
    )



async def seed_daily(target_date: date) -> None:
    """
    Prints a header and a deprecation notice for seeding box scores for the given date.
    
    Parameters:
        target_date (date): The date for which box score seeding would have been performed.
    """
    print(f"\n{'=' * 60}")
    print(f"Seeding box scores for {target_date.isoformat()}")
    print(f"{'=' * 60}")
    print(
        "\n[DEPRECATED] seed_daily relies on the ingestion module which has been removed."
    )



async def seed_teams() -> None:
    """
    Print a header and a deprecation notice for the team seeding routine.
    
    This function no longer performs any data ingestion; it only emits a banner and a message explaining that the legacy ingestion module for seeding the 30 NBA teams has been removed.
    """
    print(f"\n{'=' * 60}")
    print("Seeding NBA teams")
    print(f"{'=' * 60}")
    print(
        "\n[DEPRECATED] seed_teams relies on the ingestion module which has been removed."
    )



async def seed_csv_datasets(include_play_by_play: bool = False) -> None:
    """
    Seed the database from CSV datasets (deprecated).
    
    This function is deprecated and no longer performs CSV ingestion; it remains as a CLI placeholder and emits a deprecation notice.
    
    Parameters:
    	include_play_by_play (bool): If true, would include play-by-play CSV ingestion in the operation; otherwise only summary datasets would be considered.
    """
    print(f"\n{'=' * 60}")
    print("Seeding database from CSV datasets")
    print(f"{'=' * 60}")
    print(
        "\n[DEPRECATED] seed_csv_datasets relies on the ingestion module which has been removed."
    )


async def reindex_search() -> None:
    """Rebuild Meilisearch indices from database."""
    from app.search.tasks import _reindex_all_async

    print(f"\n{'=' * 60}")
    print("Reindexing search data")
    print(f"{'=' * 60}")
    await _reindex_all_async()
    print("\nOK: Search indices rebuilt successfully.")


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed the basketball-reference webapp database"
    )
    parser.add_argument(
        "--season",
        type=int,
        help="Season end year to seed (e.g., 2024 for 2023-24)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Seed all available seasons (2020-current)",
    )
    parser.add_argument(
        "--daily",
        type=str,
        help="Seed box scores for a specific date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--teams",
        action="store_true",
        help="Seed all 30 NBA teams",
    )
    parser.add_argument(
        "--yesterday",
        action="store_true",
        help="Seed yesterday's box scores",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Ingest CSV datasets into the database",
    )
    parser.add_argument(
        "--csv-play-by-play",
        action="store_true",
        help="Include play-by-play CSV ingestion (large)",
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="Rebuild Meilisearch indices from the database",
    )
    parser.add_argument(
        "--bootstrap",
        action="store_true",
        help="Run CSV ingestion and rebuild search indices",
    )

    args = parser.parse_args()

    if not any(
        [
            args.season,
            args.all,
            args.daily,
            args.teams,
            args.yesterday,
            args.csv,
            args.index,
            args.bootstrap,
        ]
    ):
        parser.print_help()
        print("\n\nExamples:")
        print("  python -m scripts.seed_db --teams")
        print("  python -m scripts.seed_db --season 2024")
        print("  python -m scripts.seed_db --yesterday")
        print("  python -m scripts.seed_db --daily 2024-01-15")
        print("  python -m scripts.seed_db --csv")
        print("  python -m scripts.seed_db --csv --csv-play-by-play")
        print("  python -m scripts.seed_db --index")
        print("  python -m scripts.seed_db --bootstrap")
        return

    if args.teams:
        await seed_teams()

    if args.season:
        await seed_season(args.season)

    if args.all:
        current_year = date.today().year
        end_year = current_year + 1 if date.today().month >= 7 else current_year

        for year in range(2020, end_year + 1):
            await seed_season(year)

    if args.daily:
        target_date = datetime.strptime(args.daily, "%Y-%m-%d").date()
        await seed_daily(target_date)

    if args.yesterday:
        yesterday = date.today() - timedelta(days=1)
        await seed_daily(yesterday)

    if args.csv or args.bootstrap:
        await seed_csv_datasets(include_play_by_play=args.csv_play_by_play)

    if args.index or args.bootstrap:
        await reindex_search()

    print("\n" + "=" * 60)
    print("Seeding complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())