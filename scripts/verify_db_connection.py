import logging
import sys
from pathlib import Path

from sqlalchemy import text

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "src" / "webapp" / "backend"))

from app.db.session import get_session, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def verify():
    logger.info("Initializing DB (creating views)...")
    init_db()

    logger.info("Getting session...")
    session_gen = get_session()
    session = next(session_gen)

    try:
        logger.info("Testing connection...")
        result = session.execute(text("SELECT 1")).scalar()
        logger.info("Connection test result: %s", result)
        assert result == 1

        logger.info("Querying 'player' view...")
        players = session.execute(text("SELECT * FROM player LIMIT 5")).fetchall()
        logger.info("Found %d players.", len(players))
        for p in players:
            logger.info(" - %s (%s)", p.full_name, p.slug)

        logger.info("Querying 'team' view...")
        teams = session.execute(text("SELECT * FROM team LIMIT 5")).fetchall()
        logger.info("Found %d teams.", len(teams))
        for t in teams:
            logger.info(" - %s (%s)", t.name, t.abbreviation)

        logger.info("Querying 'player_season' view...")
        stats = session.execute(text("SELECT * FROM player_season LIMIT 5")).fetchall()
        logger.info("Found %d player_season records.", len(stats))

        logger.info("VERIFICATION SUCCESSFUL")

    except Exception:
        logger.exception("VERIFICATION FAILED")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    verify()
