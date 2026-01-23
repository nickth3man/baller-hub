# Frontend Code Audit Report

**Date:** 2026-01-23
**Scope:** `src/webapp/frontend`

## Executive Summary
The frontend is a modern Next.js 15 application using the App Router. It is functional with real API integration for Players, Teams, Games, Seasons, and Search. However, it suffers from "inline componentitis" - many UI components are defined within page files rather than being reusable. It also includes unused dependencies (`zustand`, empty `hooks` folder) and lacks a shared UI component library.

## 1. Architecture Analysis
- **Framework:** Next.js 15 App Router.
- **Data Fetching:**
  - Primary: Server Components fetching directly via `fetch` (using `lib/api.ts`).
  - Client: `react-query` is configured in `providers.tsx` but not actively used in the inspected pages (Server Components dominate).
  - **State Management:** `zustand` is installed but **unused**. `hooks/` directory is **empty**.
- **API Client:** Strongly typed `fetch` wrapper in `lib/api.ts` handles all backend communication effectively.

## 2. Feature Completeness
| Feature | Status | Notes |
|---------|--------|-------|
| **Home Page** | ✅ Complete | Shows daily games, leaders, standings preview. |
| **Player Profile** | ✅ Complete | Bio, career stats, recent games. |
| **Team Profile** | ✅ Complete | Roster, stats, schedule, history. |
| **Game Detail** | ✅ Complete | Box score, quarter breakdown, player stats. |
| **Season Detail** | ✅ Complete | Schedule, leaders, month filter. |
| **Search** | ✅ Complete | Unified search for players, teams, games. |
| **Standings** | ✅ Complete | Conference and league views. |

## 3. UI/UX & Styling
- **Styling Engine:** Tailwind CSS.
- **Design System:** None. `src/webapp/frontend/(components)/ui` is **empty**.
- **Aesthetic:** Consistent "Dark/Light" mix. Home/Team headers use dark mode (`bg-slate-900`), while content areas use light mode (`bg-gray-100`).
- **Issues:**
  - No reusable primitives (Button, Card, Input).
  - Repetitive table styles (seen in Player, Team, Game pages).

## 4. Code Quality
- **Strengths:**
  - Strict TypeScript configuration.
  - specific, well-defined interfaces in `api.ts`.
  - Consistent error handling (`notFound()`, `try/catch`).
- **Weaknesses:**
  - **Low Reusability:** Components like `PlayerStatsTable`, `RosterTable`, `TeamHeader` are defined *inside* `page.tsx` files.
  - **Large Files:** Page files are growing large (300+ lines) due to inline components.
  - **Dead Code:** Unused `zustand`, empty `hooks/`, empty `ui/` folder.

## Recommendations
1.  **Refactor Components:** Move inline components (Tables, Headers) to `(components)/stats` or `(components)/ui`.
2.  **Clean Up:** Remove unused `zustand` or implement it if client state is needed.
3.  **Build UI Library:** Populate `(components)/ui` with shared atoms (Table, Button, Card).
4.  **Testing:** Expand test coverage beyond the single `page.test.tsx`.
