from unittest.mock import patch

import pytest


@pytest.fixture(scope="session", autouse=True)
def vcr_config():
    return {
        "filter_headers": ["authorization"],
        "ignore_localhost": True,
        "record_mode": "once",  # Record once, then replay
    }


@pytest.fixture(autouse=True)
def speed_up_tests(_request):
    """
    Patch time.sleep to do nothing unless we are in recording mode.
    """
    # Check if we are recording (pytest-recording adds this marker/config)
    # This is a simplification; robust detection depends on pytest-recording internals
    # or an env var.

    # Simple heuristic: If we are just running tests (replay), we want speed.
    # If we are recording, we need the sleeps.

    # For now, let's assume we want speed by default.
    # Users should set env var CI_RECORD=1 if they need real sleeps.
    import os

    if not os.getenv("CI_RECORD"):
        with patch("time.sleep"):
            yield
    else:
        yield
