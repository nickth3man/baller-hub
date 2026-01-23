# Baller Hub: Optimal Next Steps

> **Status**: Phase 2 Complete, Phase 3 Complete, Phase 4 Complete (2026-01-23)
> **Strategy**: "Clean & Catch-Up" - Fix hygiene first, then achieve feature parity.

## 🔴 Phase 1: Hygiene & Stability (COMPLETED ✅)
**Goal**: Get to a "Green CI" state. The codebase currently fails linting/formatting checks.

- [x] **Infra**: Fix `ruff` errors in Python root.
    - Focus: `PLR0913` (Too many arguments), `DTZ` (Timezones), `PTH` (Pathlib).
    - Action: `uv run ruff check --fix .` + manual fixes.
- [x] **Infra**: Fix `prettier`/`eslint` errors in Frontend.
    - Action: `npm run lint --fix`.
- [x] **Infra**: Verify `pre-commit` hooks pass locally.

## 🟡 Phase 2: Frontend Refactoring (COMPLETED ✅)
**Goal**: Stop "Inline Componentitis". Create a reusable UI system before building new pages.

- [x] **Refactor**: Extract `Table` component to `(components)/ui/Table.tsx`.
- [x] **Refactor**: Update `StandingsPage` to use the new `Table`.
- [x] **Refactor**: Extract `Header`/`PageLayout` components.
- [x] **Refactor**: Move shared types from `api.ts` to `types/`.
- [x] **Refactor**: Extracted numerous inline components (PlayerBio, CareerStatsTable, RosterTable, etc.).

## 🟢 Phase 3: Backend Feature Parity (COMPLETED ✅)
**Goal**: Expose the rich data the Scraper already collects (Draft, Awards).

- [x] **Backend**: Create `Draft` models (SQLModel) and Schema (Pydantic).
- [x] **Backend**: Implement `GET /api/v1/draft` endpoints (Classes, Picks).
- [x] **Backend**: Create `Award` models/endpoints.
- [x] **Frontend**: Build `/draft` and `/awards` pages using new components.

## 🔵 Phase 4: Automation (COMPLETED ✅)
**Goal**: Remove manual steps from data updates.

- [x] **Pipeline**: Harden `scripts/seed_db.py` (or equivalent) to run reliably.
- [x] **Testing**: Add Integration Tests for the new Draft/Awards endpoints.
- [x] **Hygiene**: Removed broken ingestion tests and fixed Pydantic V2 warnings.
