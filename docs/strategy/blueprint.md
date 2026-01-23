# Basketball-Reference Clone Blueprint (Strategic)

## 1. Problem Statement
Provide a free, queryable NBA stats site that mirrors Basketball-Reference core pages
with a modern, fast UI and a reproducible data pipeline.

**Implementation Implication:** Build an ingestion layer that can load historical data
deterministically (CSV/SQLite + scraper) into a structured schema.

## 2. Target Users
- Basketball analysts validating trends across decades.
- Fans browsing player/team/game history.
- Developers integrating a stable stats API.

**Implementation Implication:** API must expose stable filters (season/team/position)
and UI must support drill-down by player, team, game, and season.

## 3. Success Metrics
- 100% of Basketball-Reference core pages replicated for seasons 1946–2026.
- <200ms response time for player profile, game box score, and standings endpoints.
- Full data load (CSV + SQLite) completed within 2 hours on a dev machine.

**Implementation Implication:** Use bulk COPY ingestion and materialized views for
career and standings aggregates.

## 4. Core Architecture Decision
Supabase Postgres as the primary database, FastAPI for the API layer, and Next.js 15
for the frontend, with a staging-first ETL pipeline.

**Implementation Implication:** All ingestion code must be async and support COPY
into staging tables before upserting into production tables.

## 5. Tech Stack Rationale
- Supabase Postgres: managed Postgres with tooling and stable local development.
- FastAPI + SQLModel: rapid schema-driven API development.

- Next.js 15: SSR + RSC for fast page loads and SEO.

**Implementation Implication:** Keep DB access in services, and keep UI pages in the
App Router with server-side data fetching.

## 6. MVP Scope
- Player profiles + career stats.
- Team rosters + schedules.
- Game box scores.
- Standings.
- Season schedule listing.

**Implementation Implication:** Prioritize data model completeness and read-only
endpoints before advanced features.

## 7. Non-Goals (Explicit)
- User accounts, favorites, or comments.
- Live play-by-play updates.
- Prediction tools or betting integrations.

**Implementation Implication:** No auth flows or write endpoints in MVP.

## References

### Implementation Details Location
| Content Type | Location |
|--------------|----------|
| Data model + ingestion | [Implementation Spec](../specs/implementation.md#1-data-model-changes) |
| Anti-patterns | [Implementation Spec](../specs/implementation.md#anti-patterns-do-not) |
| Test cases | [Implementation Spec](../specs/implementation.md#test-case-specifications) |
| Error handling | [Implementation Spec](../specs/implementation.md#error-handling-matrix) |

### Schema References
| Topic | Location | Anchor |
|-------|----------|--------|
| Core schema tables | [Schema Reference](../reference/schema.md#core-tables) | `core-tables` |
| API endpoints | [API Reference](../reference/api.md#endpoints) | `endpoints` |
