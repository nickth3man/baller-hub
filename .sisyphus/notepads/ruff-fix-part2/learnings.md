# Learnings - Ruff Fix Part 2

- Prefer `pathlib.Path` over `os.path` for path manipulations.
- Magic numbers in tests can be suppressed with `# noqa: PLR2004` when they are acceptable context-specific values.
