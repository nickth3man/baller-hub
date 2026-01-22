# src/webapp/frontend AGENTS.md

**Generated:** 2026-01-22
**Context:** Next.js 15 Frontend.

## OVERVIEW
The user interface for Baller Hub, built with Next.js 15 (App Router). It consumes the backend API and provides a responsive, interactive experience.

## FOLDER STRUCTURE
- `app/`: Next.js App Router pages, layouts, and route groups.
- `components/`: React components organized by domain (`stats`, `ui`) or function (`layout`).
- `lib/`: Utility functions and shared API clients.
- `hooks/`: Custom React hooks for state and logic reuse.

## CORE BEHAVIORS & PATTERNS
- **Server Components**: Used by default for data fetching and layout.
- **Client Components**: Used only when interactivity (state, effects) is required.
- **Data Fetching**: TanStack Query is used for client-side data management.

## CONVENTIONS
- **Commands**: `npm run dev` (start), `npm run lint` (lint), `npm run format` (format).
- **Styling**: Tailwind CSS with `clsx` and `tailwind-merge`.
- **Naming**: PascalCase for components, camelCase for functions/vars.

## WORKING AGREEMENTS
- **Component Colocation**: Keep related components close to where they are used if not generic.
- **Strict Typing**: No `any` types. Define interfaces for all props.
- **Clean Effects**: Avoid `useEffect` for data fetching; prefer TanStack Query.
