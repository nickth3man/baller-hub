from __future__ import annotations

from pathlib import Path

DEFAULT_BASE_URL = "https://www.basketball-reference.com"
DEFAULT_MANIFEST = Path("src/scraper/scripts/fixture_manifest.json")
DEFAULT_CHECKPOINT = Path("scraper_checkpoint.json")
MIN_DISK_SPACE_GB = 1.0

# Available impersonation profiles for rotation
IMPERSONATION_PROFILES = [
    "chrome124",
    "chrome110",
    "chrome116",
    "chrome119",
    "safari170",
    "safari155",
    "firefox120",
    "edge101",
]
