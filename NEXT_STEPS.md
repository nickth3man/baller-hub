# Baller Hub: Optimal Next Steps

> **Status**: Phase 1 Complete, Phase 2 Started (2026-01-23)
> **Strategy**: "Clean & Catch-Up" - Fix hygiene first, then achieve feature parity.

## 🔴 Phase 1: Hygiene & Stability (COMPLETED ✅)
**Goal**: Get to a "Green CI" state. The codebase currently fails linting/formatting checks.

- [x] **Infra**: Fix `ruff` errors in Python root.
    - Focus: `PLR0913` (Too many arguments), `DTZ` (Timezones), `PTH` (Pathlib).
    - Action: `uv run ruff check --fix .` + manual fixes.
- [x] **Infra**: Fix `prettier`/`eslint` errors in Frontend.
    - Action: `npm run lint --fix`.
- [x] **Infra**: Verify `pre-commit` hooks pass locally.

## 🟡 Phase 2: Frontend Refactoring (IN PROGRESS)
**Goal**: Stop "Inline Componentitis". Create a reusable UI system before building new pages.

- [x] **Refactor**: Extract `Table` component to `(components)/ui/Table.tsx`.
- [x] **Refactor**: Update `StandingsPage` to use the new `Table`.
- [ ] **Refactor**: Extract `Header`/`PageLayout` components.
- [ ] **Refactor**: Move shared types from `api.ts` to `types/` if they grow too large.

## 🟢 Phase 3: Backend Feature Parity
**Goal**: Expose the rich data the Scraper already collects (Draft, Awards).

- [ ] **Backend**: Create `Draft` models (SQLModel) and Schema (Pydantic).
- [ ] **Backend**: Implement `GET /api/v1/draft` endpoints (Classes, Picks).
- [ ] **Backend**: Create `Award` models/endpoints.
- [ ] **Frontend**: Build `/draft` and `/awards` pages using new components.

## 🔵 Phase 4: Automation
**Goal**: Remove manual steps from data updates.

- [ ] **Pipeline**: Harden `scripts/seed_db.py` (or equivalent) to run reliably.
- [ ] **Testing**: Add Integration Tests for the new Draft/Awards endpoints.
