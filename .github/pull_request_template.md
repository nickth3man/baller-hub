## Summary
<!-- What does this PR do? Link to issue if applicable: Fixes #123 -->


## Type of Change
<!-- Check one -->
- [ ] Bug fix
- [ ] New feature
- [ ] Refactor (no functional change)
- [ ] Documentation
- [ ] Test-only change

## Checklist
<!-- Check all that apply -->
- [ ] `uv run ruff check src/` passes
- [ ] `uv run ty check src/` passes
- [ ] Tests added/updated for changes
- [ ] `uv run pytest` passes locally

## Layer-Specific (check if touched)

### Scraping/Parsing
- [ ] Tested against live HTML (not just fixtures)
- [ ] Handles missing/malformed data gracefully
- [ ] Test fixtures updated if HTML structure changed

### API/Database
- [ ] Migration included (if schema changed)
- [ ] Backwards compatible or migration path documented
- [ ] API endpoint tested with example requests

### Frontend
- [ ] Tested in browser (not just build passes)
- [ ] Screenshots attached for visual changes

---

## PR-Agent Summary

pr_agent:summary

## PR-Agent Walkthrough

pr_agent:walkthrough
