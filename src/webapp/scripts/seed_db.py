#!/usr/bin/env python3
"""Data seeding script for the basketball-reference webapp.

This script populates the database with initial data by scraping
basketball-reference.com and persisting to PostgreSQL.

Usage:
    cd webapp/backend
    uv run python -m scripts.seed_db --season 2024

Options:
    --season YEAR   Season end year to seed (e.g., 2024 for 2023-24)
    --all           Seed all available seasons (2020-current)
    --daily DATE    Seed box scores for a specific date (YYYY-MM-DD)
"""

import argparse
import asyncio
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# Add the backend and scraper root directories to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
scraper_root = backend_dir.parent.parent
sys.path[:0] = [str(backend_dir), str(scraper_root)]


async def seed_season(season_end_year: int) -> None:
    """Seed a full season of data."""
    from app.db.session import async_session_factory
    from app.ingestion.scraper_service import ScraperService
    from app.ingestion.tasks import (
        _persist_season_data,
    )

    print(f"\n{'=' * 60}")
    print(f"Seeding season {season_end_year - 1}-{str(season_end_year)[2:]}")
    print(f"{'=' * 60}")

    scraper = ScraperService()

    # Fetch all season data
    print("\nFetching schedule...")
    schedule = await scraper.get_season_schedule(season_end_year)
    print(f"  Found {len(schedule)} games")

    print("\nFetching player season totals...")
    player_totals = await scraper.get_players_season_totals(season_end_year)
    print(f"  Found {len(player_totals)} player records")

    print("\nFetching player advanced stats...")
    advanced_totals = await scraper.get_players_advanced_season_totals(
        season_end_year, include_combined_values=True
    )
    print(f"  Found {len(advanced_totals)} advanced stat records")

    print("\nFetching standings...")
    standings = await scraper.get_standings(season_end_year)
    if isinstance(standings, dict):
        standings_count = sum(
            len(v) for v in standings.values() if isinstance(v, list)
        )
        standings_payload = standings
    elif isinstance(standings, list):
        standings_count = len(standings)
        standings_payload = {"ALL": standings}
    else:
        standings_count = 0
        standings_payload = {}
    print(f"  Found {standings_count} team standings")

    # Persist to database
    print("\nPersisting to database...")
    async with async_session_factory() as session:
        await _persist_season_data(
            session,
            season_end_year,
            schedule,
            player_totals,
            advanced_totals,
            standings_payload,
        )
        await session.commit()

    print(f"\n✓ Season {season_end_year} seeded successfully!")


async def seed_daily(target_date: date) -> None:
    """Seed box scores for a specific date."""
    from app.db.session import async_session_factory
    from app.ingestion.scraper_service import ScraperService
    from app.ingestion.tasks import _persist_box_scores

    print(f"\n{'=' * 60}")
    print(f"Seeding box scores for {target_date.isoformat()}")
    print(f"{'=' * 60}")

    scraper = ScraperService()

    print("\nFetching player box scores...")
    player_box_scores = await scraper.get_player_box_scores(
        day=target_date.day,
        month=target_date.month,
        year=target_date.year,
    )
    print(f"  Found {len(player_box_scores)} player box scores")

    print("\nFetching team box scores...")
    team_box_scores = await scraper.get_team_box_scores(
        day=target_date.day,
        month=target_date.month,
        year=target_date.year,
    )
    print(f"  Found {len(team_box_scores)} team box scores")

    if not player_box_scores and not team_box_scores:
        print("\n⚠ No games found for this date (off-day or future date)")
        return

    # Persist to database
    print("\nPersisting to database...")
    async with async_session_factory() as session:
        await _persist_box_scores(
            session,
            target_date,
            player_box_scores,
            team_box_scores,
        )
        await session.commit()

    print(f"\n✓ Box scores for {target_date.isoformat()} seeded successfully!")


async def seed_teams() -> None:
    """Seed the 30 current NBA teams."""
    from app.db.session import async_session_factory
    from app.ingestion.repositories import clear_caches, get_or_create_team

    # All 30 current NBA teams
    teams = [
        ("ATL", "Atlanta Hawks"),
        ("BOS", "Boston Celtics"),
        ("BRK", "Brooklyn Nets"),
        ("CHO", "Charlotte Hornets"),
        ("CHI", "Chicago Bulls"),
        ("CLE", "Cleveland Cavaliers"),
        ("DAL", "Dallas Mavericks"),
        ("DEN", "Denver Nuggets"),
        ("DET", "Detroit Pistons"),
        ("GSW", "Golden State Warriors"),
        ("HOU", "Houston Rockets"),
        ("IND", "Indiana Pacers"),
        ("LAC", "Los Angeles Clippers"),
        ("LAL", "Los Angeles Lakers"),
        ("MEM", "Memphis Grizzlies"),
        ("MIA", "Miami Heat"),
        ("MIL", "Milwaukee Bucks"),
        ("MIN", "Minnesota Timberwolves"),
        ("NOP", "New Orleans Pelicans"),
        ("NYK", "New York Knicks"),
        ("OKC", "Oklahoma City Thunder"),
        ("ORL", "Orlando Magic"),
        ("PHI", "Philadelphia 76ers"),
        ("PHO", "Phoenix Suns"),
        ("POR", "Portland Trail Blazers"),
        ("SAC", "Sacramento Kings"),
        ("SAS", "San Antonio Spurs"),
        ("TOR", "Toronto Raptors"),
        ("UTA", "Utah Jazz"),
        ("WAS", "Washington Wizards"),
    ]

    print(f"\n{'=' * 60}")
    print("Seeding NBA teams")
    print(f"{'=' * 60}")

    async with async_session_factory() as session:
        await clear_caches()
        for abbrev, name in teams:
            await get_or_create_team(session, abbrev, name)
            print(f"  ✓ {abbrev} - {name}")
        await session.commit()

    print(f"\n✓ Seeded {len(teams)} teams!")


async def main():
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

    args = parser.parse_args()

    if not any([args.season, args.all, args.daily, args.teams, args.yesterday]):
        parser.print_help()
        print("\n\nExamples:")
        print("  python -m scripts.seed_db --teams")
        print("  python -m scripts.seed_db --season 2024")
        print("  python -m scripts.seed_db --yesterday")
        print("  python -m scripts.seed_db --daily 2024-01-15")
        return

    if args.teams:
        await seed_teams()

    if args.season:
        await seed_season(args.season)

    if args.all:
        current_year = date.today().year
        # If we're before June, current season ends this year
        # If after June, current season ends next year
        end_year = current_year + 1 if date.today().month >= 7 else current_year

        for year in range(2020, end_year + 1):
            await seed_season(year)

    if args.daily:
        target_date = datetime.strptime(args.daily, "%Y-%m-%d").date()
        await seed_daily(target_date)

    if args.yesterday:
        yesterday = date.today() - timedelta(days=1)
        await seed_daily(yesterday)

    print("\n" + "=" * 60)
    print("Seeding complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
