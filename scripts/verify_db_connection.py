import os
import sys

from sqlalchemy import text

# Add backend to path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/webapp/backend"))
)

from app.db.session import get_session, init_db


def verify():
    print("Initializing DB (creating views)...")
    init_db()

    print("Getting session...")
    session_gen = get_session()
    session = next(session_gen)

    try:
        print("Testing connection...")
        result = session.execute(text("SELECT 1")).scalar()
        print(f"Connection test result: {result}")
        assert result == 1

        print("Querying 'player' view...")
        players = session.execute(text("SELECT * FROM player LIMIT 5")).fetchall()
        print(f"Found {len(players)} players.")
        for p in players:
            print(f" - {p.full_name} ({p.slug})")

        print("Querying 'team' view...")
        teams = session.execute(text("SELECT * FROM team LIMIT 5")).fetchall()
        print(f"Found {len(teams)} teams.")
        for t in teams:
            print(f" - {t.name} ({t.abbreviation})")

        print("Querying 'player_season' view...")
        stats = session.execute(text("SELECT * FROM player_season LIMIT 5")).fetchall()
        print(f"Found {len(stats)} player_season records.")

        print("VERIFICATION SUCCESSFUL")

    except Exception as e:
        print(f"VERIFICATION FAILED: {e}")
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    verify()
