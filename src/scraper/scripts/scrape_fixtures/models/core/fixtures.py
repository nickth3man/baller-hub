from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict

from src.scraper.scripts.scrape_fixtures.constants import DEFAULT_BASE_URL


class FixtureDict(TypedDict, total=False):
    """Dictionary representation of a fixture specification for JSON serialization.

    Attributes:
        url: Relative URL path for the fixture
        fixture_path: Local file path where the fixture should be saved
        validator: Optional validator key for HTML validation
        phase: Optional scraping phase this fixture belongs to
    """

    url: str
    fixture_path: str
    validator: str | None
    phase: str | None


@dataclass(frozen=True)
class FixtureSpec:
    """Immutable specification for a single fixture to be scraped.

    Attributes:
        url: Relative URL path for the fixture
        fixture_path: Local file path where the fixture should be saved
        validator: Optional validator key for HTML validation
        phase: Optional scraping phase this fixture belongs to
    """

    url: str
    fixture_path: str
    validator: str | None = None
    phase: str | None = None


@dataclass(frozen=True)
class FixtureManifest:
    """Manifest containing all fixtures to be scraped with their configuration.

    Attributes:
        base_url: Base URL for all fixture requests
        output_dir: Directory where fixtures should be saved
        fixtures: List of all fixture specifications
        phases: Mapping of phase names to descriptions
    """

    base_url: str
    output_dir: Path
    fixtures: list[FixtureSpec]
    phases: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> FixtureManifest:
        """Load fixture manifest from a JSON file.

        Args:
            path: Path to the JSON manifest file

        Returns:
            FixtureManifest instance loaded from the file

        Raises:
            FileNotFoundError: If the manifest file doesn't exist
            json.JSONDecodeError: If the JSON is malformed
        """
        data = json.loads(path.read_text(encoding="utf-8"))
        base_url = data.get("base_url", DEFAULT_BASE_URL)
        output_dir = Path(data.get("output_dir", "tests/integration/files"))
        phases = data.get("phases", {})
        fixtures = [
            FixtureSpec(
                url=fixture["url"],
                fixture_path=fixture["fixture_path"],
                validator=fixture.get("validator"),
                phase=fixture.get("phase"),
            )
            for fixture in data.get("fixtures", [])
        ]
        return cls(
            base_url=base_url, output_dir=output_dir, fixtures=fixtures, phases=phases
        )

    def filter_by_phase(self, phase: str | None) -> list[FixtureSpec]:
        """Filter fixtures by scraping phase.

        Args:
            phase: Phase name to filter by, or None for all fixtures

        Returns:
            List of fixtures matching the specified phase
        """
        if phase is None:
            return self.fixtures
        return [f for f in self.fixtures if f.phase and f.phase.startswith(phase)]
