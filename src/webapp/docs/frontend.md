# Frontend Guide

The frontend is a Next.js 15 App Router application. Pages are server components
by default and fetch data from the FastAPI API.

## Core Routes

- `/` - Home dashboard (today's games, standings preview, leaders)
- `/players` - Player directory and filters
- `/players/[slug]` - Player profile and career stats
- `/players/[slug]/game-log/[year]` - Game log for a season
- `/teams` - Team directory
- `/teams/[abbrev]` - Team profile, roster, schedule, history
- `/seasons` - Season timeline
- `/seasons/[year]` - Season detail, leaders, schedule
- `/standings` - Conference or league standings
- `/games` - Recent games
- `/games/[id]` - Box score
- `/search` - Search results

## Data Fetching

All API calls live in `src/webapp/frontend/lib/api.ts` and are executed in
server components. Requests use a short revalidation window to keep pages fresh.

## Styling

- Tailwind CSS with a custom font pairing and a warm, textured background
- Display headers use the `font-display` family
- Layout uses rounded cards, bold typography, and dense grids

## Components

Shared components live under:

- `src/webapp/frontend/(components)/layout`
- `src/webapp/frontend/(components)/stats`

Keep components stateless when possible and pass data from server components.
