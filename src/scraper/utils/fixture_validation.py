"""Fixture validation helpers for basketball-reference HTML snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from lxml import html as lxml_html


@dataclass(frozen=True)
class ValidationRule:
    """Declarative HTML validation rule for a fixture."""

    required_ids: Sequence[str] | None = None
    required_xpath: Sequence[str] | None = None
    required_text: Sequence[str] | None = None
    min_rows: int | None = None
    min_tables: int | None = None


VALIDATION_RULES: dict[str, ValidationRule] = {
    "standings": ValidationRule(
        required_ids=("divs_standings_E", "divs_standings_W"),
        required_xpath=(
            "//table[@id='divs_standings_E']//tbody/tr",
            "//table[@id='divs_standings_W']//tbody/tr",
        ),
        min_rows=10,
    ),
    "players_season_totals": ValidationRule(
        required_ids=("totals_stats",),
        required_xpath=("//table[@id='totals_stats']//tbody/tr",),
        min_rows=100,
    ),
    "players_advanced_season_totals": ValidationRule(
        required_ids=("advanced",),
        required_xpath=("//table[@id='advanced']//tbody/tr",),
        min_rows=100,
    ),
    "schedule": ValidationRule(
        required_ids=("schedule",),
        required_xpath=("//table[@id='schedule']//tbody/tr",),
        min_rows=10,
    ),
    "daily_box_scores": ValidationRule(
        required_xpath=("//td[contains(@class, 'gamelink')]/a",),
        min_rows=1,
    ),
    "box_score": ValidationRule(
        required_xpath=("//table[contains(@class, 'stats_table')]",),
        min_tables=2,
    ),
    "play_by_play": ValidationRule(
        required_ids=("pbp",),
        required_xpath=("//table[@id='pbp']//tr",),
        min_rows=50,
    ),
    "daily_leaders": ValidationRule(
        required_ids=("stats",),
        required_xpath=("//table[@id='stats']//tbody/tr",),
        min_rows=5,
    ),
    "search_results": ValidationRule(
        required_xpath=(
            "//div[@id='searches']/div[@id='players']"
            "//div[contains(@class, 'search-item')]",
        ),
        min_rows=1,
    ),
    "player_profile": ValidationRule(
        required_ids=("per_game",),
        required_xpath=("//table[@id='per_game']//tbody/tr",),
        min_rows=1,
    ),
}


def validate_fixture_html(html_content: bytes, validator_key: str) -> list[str]:
    """Validate HTML content against a named rule set."""
    rule = VALIDATION_RULES.get(validator_key)
    if rule is None:
        return [f"Unknown validator key: {validator_key}"]

    tree = lxml_html.fromstring(html_content)
    errors: list[str] = []

    for required_id in _as_iterable(rule.required_ids):
        if not tree.xpath(f".//*[@id='{required_id}']"):
            errors.append(f"Missing element id: {required_id}")

    row_counts: list[int] = []
    for xpath in _as_iterable(rule.required_xpath):
        matches = tree.xpath(xpath)
        if not matches:
            errors.append(f"Missing required xpath: {xpath}")
        row_counts.append(len(matches))

    if rule.min_rows is not None and row_counts:
        if max(row_counts) < rule.min_rows:
            errors.append(
                f"Expected at least {rule.min_rows} rows, found {max(row_counts)}"
            )

    if rule.min_tables is not None:
        table_count = len(tree.xpath("//table"))
        if table_count < rule.min_tables:
            errors.append(
                f"Expected at least {rule.min_tables} tables, found {table_count}"
            )

    for required_text in _as_iterable(rule.required_text):
        if required_text not in tree.text_content():
            errors.append(f"Missing required text: {required_text}")

    return errors


def _as_iterable(values: Sequence[str] | None) -> Iterable[str]:
    if not values:
        return ()
    return values
