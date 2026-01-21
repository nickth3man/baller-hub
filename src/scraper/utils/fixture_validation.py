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


# ============================================================================
# VALIDATION RULES FOR ALL 50+ PAGE TYPES
# ============================================================================

VALIDATION_RULES: dict[str, ValidationRule] = {
    # ==========================================================================
    # EXISTING PAGE TYPES (Phase 1-2)
    # ==========================================================================
    "standings": ValidationRule(
        required_ids=("divs_standings_E", "divs_standings_W"),
        required_xpath=(
            "//table[@id='divs_standings_E']//tbody/tr",
            "//table[@id='divs_standings_W']//tbody/tr",
        ),
        min_rows=10,
    ),
    "standings_historical": ValidationRule(
        # Historical leagues may have different table structures
        required_xpath=(
            "//table[contains(@id, 'divs_standings') or "
            "contains(@class, 'standings')]//tbody/tr",
        ),
        min_rows=5,
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
    "schedule_early": ValidationRule(
        required_ids=("schedule",),
        required_xpath=("//table[@id='schedule']//tbody/tr",),
        min_rows=1,
    ),
    "daily_box_scores": ValidationRule(
        required_xpath=(
            "//div[contains(@class, 'breadcrumbs')]"
            "//strong[contains(., 'Games Played on')]",
        ),
        min_rows=0,
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
        required_xpath=("//h1[contains(., 'Daily Stats Leaders')]",),
        min_rows=0,
    ),
    "search_results": ValidationRule(
        required_xpath=(
            "//div[@id='searches']/div[@id='players']"
            "//div[contains(@class, 'search-item')]",
        ),
        min_rows=1,
    ),
    "search_results_empty": ValidationRule(
        # Empty search results page - current content is a guidance block
        required_xpath=(
            "//strong[contains(., 'Examples of successful searches')]",
        ),
    ),
    "player_profile": ValidationRule(
        required_ids=("per_game_stats",),
        required_xpath=("//table[@id='per_game_stats']//tbody/tr",),
        min_rows=1,
    ),
    "player_game_log": ValidationRule(
        required_xpath=("//table[contains(@id, 'player_game_log')]//tbody/tr",),
        min_rows=1,
    ),
    "schedule_month": ValidationRule(
        required_ids=("schedule",),
        required_xpath=("//table[@id='schedule']//tbody/tr",),
        min_rows=1,
    ),
    # ==========================================================================
    # NEW CORE PAGE TYPES (Phase 3)
    # ==========================================================================
    "coach": ValidationRule(
        # Coach pages have coaching record tables
        required_xpath=(
            "//table[contains(@id, 'coach')]//tbody/tr",
        ),
        min_rows=1,
    ),
    "draft": ValidationRule(
        required_ids=("stats",),
        required_xpath=("//table[@id='stats']//tbody/tr",),
        min_rows=30,  # At least 30 picks in most drafts
    ),
    "awards": ValidationRule(
        # Awards pages have tables with award winners
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=10,
    ),
    "awards_teams": ValidationRule(
        # All-NBA, All-Rookie, All-Defensive team pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=5,
    ),
    "awards_hof": ValidationRule(
        # Hall of Fame page
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=50,
    ),
    "playoffs": ValidationRule(
        # Playoff bracket/summary pages
        required_xpath=(
            "//div[contains(@class, 'playoff')]",
            "//table[contains(@class, 'stats_table')]",
        ),
        min_tables=1,
    ),
    "allstar": ValidationRule(
        # All-Star game pages have box scores
        required_xpath=("//table[contains(@class, 'stats_table')]",),
        min_tables=2,
    ),
    "leaders": ValidationRule(
        # Career/active/season leaders pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=10,
    ),
    "team_season": ValidationRule(
        # Team season pages have roster and stats
        required_ids=("roster",),
        required_xpath=("//table[@id='roster']//tbody/tr",),
        min_rows=10,
    ),
    "team_schedule": ValidationRule(
        # Team schedule pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=10,
    ),
    "team_gamelog": ValidationRule(
        # Team game log pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=10,
    ),
    # ==========================================================================
    # HISTORICAL LEAGUES (Phase 4)
    # ==========================================================================
    "rookies": ValidationRule(
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=5,
    ),
    "season_leaders": ValidationRule(
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=5,
    ),
    # ==========================================================================
    # EXTENDED STATS (Phase 5)
    # ==========================================================================
    "per_game": ValidationRule(
        required_ids=("per_game_stats",),
        required_xpath=("//table[@id='per_game_stats']//tbody/tr",),
        min_rows=100,
    ),
    "per_minute": ValidationRule(
        required_ids=("per_minute_stats",),
        required_xpath=("//table[@id='per_minute_stats']//tbody/tr",),
        min_rows=100,
    ),
    "per_poss": ValidationRule(
        required_ids=("per_poss_stats",),
        required_xpath=("//table[@id='per_poss_stats']//tbody/tr",),
        min_rows=100,
    ),
    "shooting": ValidationRule(
        required_ids=("shooting_stats",),
        required_xpath=("//table[@id='shooting_stats']//tbody/tr",),
        min_rows=50,
    ),
    # ==========================================================================
    # PLAYER SUB-PAGES (Phase 6)
    # ==========================================================================
    "player_splits": ValidationRule(
        # Player splits pages have multiple tables
        required_xpath=("//table[contains(@class, 'stats_table')]",),
        min_tables=3,
    ),
    "player_shooting": ValidationRule(
        # Player shooting chart pages
        required_xpath=("//table[contains(@class, 'stats_table')]",),
        min_tables=1,
    ),
    "player_advanced_gamelog": ValidationRule(
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=10,
    ),
    # ==========================================================================
    # ADDITIONAL PAGE TYPES
    # ==========================================================================
    "team_draft": ValidationRule(
        # Team draft history pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=10,
    ),
    "standings_by_date": ValidationRule(
        # Historical standings by date
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=10,
    ),
    "ratings": ValidationRule(
        # Team ratings pages (offensive/defensive ratings)
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=30,
    ),
    "uniform_numbers": ValidationRule(
        # Uniform numbers pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=50,
    ),
    "team_franchise": ValidationRule(
        # Team franchise history pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=10,
    ),
    "player_index": ValidationRule(
        # Player index pages by letter
        required_xpath=("//table[contains(@id, 'players')]//tbody/tr",),
        min_rows=10,
    ),
    "team_salaries": ValidationRule(
        # Team salary pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=5,
    ),
    "team_depth_chart": ValidationRule(
        # Team depth chart pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=5,
    ),
    "team_starting_lineups": ValidationRule(
        # Team starting lineups pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=10,
    ),
    "team_transactions": ValidationRule(
        # Team transactions pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=5,
    ),
    "boxscore_shot_chart": ValidationRule(
        # Box score shot chart pages
        required_xpath=("//div[contains(@id, 'shot-chart')] | //table[contains(@class, 'shot_chart')]",),
        min_rows=1,
    ),
    "boxscore_plus_minus": ValidationRule(
        # Box score plus/minus pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=10,
    ),
    "player_on_off": ValidationRule(
        # Player on/off court data pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=5,
    ),
    "referee_index": ValidationRule(
        # Referee index page
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=10,
    ),
    "referee_profile": ValidationRule(
        # Referee profile pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=5,
    ),
    "league_transactions": ValidationRule(
        # League-wide transactions pages
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=10,
    ),
    "injuries": ValidationRule(
        # Injuries page (dynamic, may be empty)
        required_xpath=("//table[contains(@class, 'stats_table')]//tbody/tr",),
        min_rows=0,
    ),
}


def validate_fixture_html(html_content: bytes, validator_key: str) -> list[str]:
    """Validate HTML content against a named rule set.

    Args:
        html_content: Raw HTML bytes to validate
        validator_key: Key for the validation rule to apply

    Returns:
        List of validation error messages (empty if valid)
    """
    rule = VALIDATION_RULES.get(validator_key)
    if rule is None:
        # Unknown validator - allow it but log warning
        return []

    try:
        tree = lxml_html.fromstring(html_content)
    except Exception as e:
        return [f"Failed to parse HTML: {e}"]

    comment_trees = _extract_comment_trees(tree)
    trees = [tree, *comment_trees]
    combined_text = tree.text_content() + "".join(
        comment.text or "" for comment in tree.xpath("//comment()")
    )

    errors: list[str] = []

    # Check required element IDs
    for required_id in _as_iterable(rule.required_ids):
        if not any(t.xpath(f".//*[@id='{required_id}']") for t in trees):
            errors.append(f"Missing element id: {required_id}")

    # Check required XPath expressions and collect row counts
    row_counts: list[int] = []
    for xpath in _as_iterable(rule.required_xpath):
        match_count = sum(len(t.xpath(xpath)) for t in trees)
        if match_count == 0:
            errors.append(f"Missing required xpath: {xpath}")
        row_counts.append(match_count)

    # Check minimum row count
    if rule.min_rows is not None and row_counts:
        if max(row_counts) < rule.min_rows:
            errors.append(
                f"Expected at least {rule.min_rows} rows, found {max(row_counts)}"
            )

    # Check minimum table count
    if rule.min_tables is not None:
        table_count = sum(len(t.xpath("//table")) for t in trees)
        if table_count < rule.min_tables:
            errors.append(
                f"Expected at least {rule.min_tables} tables, found {table_count}"
            )

    # Check required text content
    for required_text in _as_iterable(rule.required_text):
        if required_text not in combined_text:
            errors.append(f"Missing required text: {required_text}")

    return errors


def _as_iterable(values: Sequence[str] | None) -> Iterable[str]:
    """Convert optional sequence to iterable (empty tuple if None)."""
    if not values:
        return ()
    return values


def _extract_comment_trees(tree: lxml_html.HtmlElement) -> list[lxml_html.HtmlElement]:
    comment_trees: list[lxml_html.HtmlElement] = []
    for comment in tree.xpath("//comment()"):
        if not comment.text or "<table" not in comment.text:
            continue
        try:
            fragment = lxml_html.fragment_fromstring(
                comment.text, create_parent=True
            )
        except Exception:
            continue
        comment_trees.append(fragment)
    return comment_trees


def build_validation_context(
    html_content: bytes, validator_key: str | None
) -> dict[str, object]:
    """Collect additional validation context for logging/debugging."""
    rule = VALIDATION_RULES.get(validator_key or "")
    try:
        tree = lxml_html.fromstring(html_content)
    except Exception as e:
        return {"parse_error": str(e), "content_bytes": len(html_content)}

    comment_trees = _extract_comment_trees(tree)
    trees = [tree, *comment_trees]
    title = tree.xpath("//title/text()")
    table_count = sum(len(t.xpath("//table")) for t in trees)
    context: dict[str, object] = {
        "title": title[0].strip() if title else None,
        "table_count": table_count,
        "content_bytes": len(html_content),
    }

    if rule is None:
        return context

    combined_text = tree.text_content() + "".join(
        comment.text or "" for comment in tree.xpath("//comment()")
    )
    required_ids = {
        required_id: any(t.xpath(f".//*[@id='{required_id}']") for t in trees)
        for required_id in _as_iterable(rule.required_ids)
    }
    xpath_counts = {
        xpath: sum(len(t.xpath(xpath)) for t in trees)
        for xpath in _as_iterable(rule.required_xpath)
    }
    required_text = {
        text: text in combined_text
        for text in _as_iterable(rule.required_text)
    }

    context.update(
        {
            "required_ids": required_ids,
            "xpath_counts": xpath_counts,
            "required_text": required_text,
        }
    )
    return context


def get_available_validators() -> list[str]:
    """Return list of available validator keys."""
    return sorted(VALIDATION_RULES.keys())
