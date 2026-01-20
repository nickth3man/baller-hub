# Basketball-Reference Clone Pivot Plan

## Raw Data Inventory (`raw-data/`)

### SQLite Database

- **`database/sqlite/nba.sqlite`** - Pre-existing NBA database (likely from nba_api)

### CSV Dataset 1 (`misc-csv/csv_1/`) - Core entities

| File | Records | Maps To |

|------|---------|---------|

| `Players.csv` | ~6,700 players | `player` table |

| `Games.csv` | Game records | `game` table |

| `LeagueSchedule24_25.csv` | 2024-25 schedule | `game` table |

| `LeagueSchedule25_26.csv` | 2025-26 schedule | `game` table |

| `PlayerStatistics.csv` | Player stats | `player_season` table |

| `TeamHistories.csv` | Franchise history | `franchise`, `team` tables |

| `TeamStatistics.csv` | Team stats | `team_season` table |

### CSV Dataset 2 (`misc-csv/csv_2/`) - Detailed stats (Basketball-Reference format)

| File | Maps To |

|------|---------|

| `Player Totals.csv` (~33K rows) | `player_season` table |

| `Advanced.csv` | `player_season_advanced` table |

| `Player Per Game.csv` | Derived views |

| `Player Shooting.csv` | Shot chart data (new table needed) |

| `Player Play By Play.csv` | `play_by_play` enrichment |

| `Draft Pick History.csv` | `draft`, `draft_pick` tables |

| `All-Star Selections.csv` | `award_recipient` table |

| `End of Season Teams.csv` | `award_recipient` (All-NBA) |

| `Team Totals.csv` | `team_season` table |

| `Team Summaries.csv` | `team_season` enrichment |

### CSV Dataset 3 (`misc-csv/csv_3/`) - NBA API format

| File | Maps To |

|------|---------|

| `game.csv` (~30K rows) | `game`, `box_score` tables |

| `player.csv` | `player` table (alternate source) |

| `play_by_play.csv` | `play_by_play` table |

| `team.csv`, `team_details.csv` | `team` table |

| `draft_history.csv` | `draft_pick` table |

| `line_score.csv` | `box_score` quarter_scores |

### CSV Dataset 4 (`misc-csv/csv_4/`) - Supplementary

| File | Maps To |

|------|---------|

| `nba_championships.csv` | `season.champion_team_id` |

| `nba_players.csv` | `player` deduplication source |

---

## Phase 1: Strategic Thinking (Docs Audit + Blueprint)

### 1.1 Documentation Audit

- Consolidate existing docs, remove aspirational/outdated content (target 40-50% reduction)
- Single source of truth for: schema, API endpoints, UI components

### 1.2 Strategic Blueprint (7 Questions)

1. **What problem?** - Provide free, queryable NBA statistics with modern UI
2. **For whom?** - Basketball analysts, fans, developers building apps
3. **Why now?** - Existing scraped data + raw CSVs ready for production use
4. **What's the MVP?** - Read-only browse: Players, Teams, Games, Standings, Seasons
5. **What's NOT MVP?** - User accounts, favorites, comments, predictions, live data
6. **Success metric?** - 100% of Basketball-Reference core pages replicated
7. **Tech stack?** - PostgreSQL + FastAPI + Next.js 15 (existing webapp structure)

### 1.3 Architecture Decision Records (ADRs)

- **ADR-001**: PostgreSQL as primary data store (already decided)
- **ADR-002**: Hybrid ingestion (scraper + CSV/SQLite imports)
- **ADR-003**: Staging tables for bulk CSV import with validation
- **ADR-004**: Materialized views for career/season aggregates
- **ADR-005**: Season-based partitioning for games/box_scores (future optimization)

---

## Phase 2: Implementation Specs

### 2.1 Data Model Enhancements

#### New Tables Needed

```sql
-- Shooting data (from csv_2/Player Shooting.csv)
CREATE TABLE player_shooting (
    player_id INTEGER REFERENCES player(player_id),
    season_id INTEGER REFERENCES season(season_id),
    distance_range VARCHAR(20),  -- '0-3 ft', '3-10 ft', '10-16 ft', '16-3P', '3P'
    fg_made INTEGER,
    fg_attempted INTEGER,
    fg_percentage NUMERIC(5,3),
    PRIMARY KEY (player_id, season_id, distance_range)
);

-- Staging tables for CSV import
CREATE UNLOGGED TABLE staging_players (
    row_id SERIAL PRIMARY KEY,
    person_id TEXT,
    first_name TEXT,
    last_name TEXT,
    birthdate TEXT,
    country TEXT,
    height TEXT,
    weight TEXT,
    -- All TEXT for flexible import, validate later
    import_batch_id UUID,
    validation_errors JSONB
);
```

#### Materialized Views

```sql
CREATE MATERIALIZED VIEW player_career_stats AS
SELECT
    p.player_id, p.first_name, p.last_name,
    COUNT(DISTINCT pbs.game_id) AS games_played,
    SUM(pbs.points_scored) AS career_points,
    ROUND(AVG(pbs.points_scored)::NUMERIC, 1) AS ppg,
    ROUND(AVG(pbs.assists)::NUMERIC, 1) AS apg,
    ROUND(AVG(pbs.offensive_rebounds + pbs.defensive_rebounds)::NUMERIC, 1) AS rpg
FROM player p
LEFT JOIN player_box_score pbs ON p.player_id = pbs.player_id
GROUP BY p.player_id, p.first_name, p.last_name;

CREATE INDEX idx_player_career_stats_player_id ON player_career_stats(player_id);
```

### 2.2 Ingestion Pipeline Architecture

```mermaid
flowchart TB
    subgraph Sources
        scraper[Scraper Service]
        csv1[CSV Dataset 1]
        csv2[CSV Dataset 2]
        csv3[CSV Dataset 3]
        sqlite[SQLite DB]
    end
    
    subgraph Staging
        staging_players[staging_players]
        staging_games[staging_games]
        staging_stats[staging_stats]
    end
    
    subgraph Validation
        type_check[pg_input_is_valid]
        constraint_check[Business Rules]
        dedup[Deduplication]
    end
    
    subgraph Production
        players[(player)]
        games[(game)]
        box_scores[(box_score)]
        stats[(player_season)]
    end
    
    csv1 --> |COPY| staging_players
    csv2 --> |COPY| staging_stats
    csv3 --> |COPY| staging_games
    sqlite --> |pgloader| staging_games
    scraper --> |Direct| Production
    
    staging_players --> type_check
    staging_games --> type_check
    staging_stats --> type_check
    
    type_check --> constraint_check
    constraint_check --> dedup
    dedup --> Production
```

### 2.3 CSV Import Implementation

```python
# Recommended approach using psycopg2 copy_from (fastest)
async def bulk_import_csv(filepath: Path, staging_table: str) -> int:
    """Import CSV to staging table using COPY protocol."""
    async with async_session_factory() as session:
        conn = await session.connection()
        raw_conn = await conn.get_raw_connection()
        
        with open(filepath, 'r') as f:
            # Skip header
            next(f)
            await raw_conn.copy_from(
                f, staging_table, sep=',', null='',
                columns=['col1', 'col2', ...]  # Map CSV columns
            )
        
        # Run validation queries
        await session.execute(text("""
            UPDATE staging_players 
            SET validation_errors = jsonb_build_object(
                'birthdate', CASE WHEN NOT pg_input_is_valid(birthdate, 'date') 
                             THEN 'Invalid date format' END,
                'height', CASE WHEN NOT pg_input_is_valid(height, 'numeric') 
                          THEN 'Invalid number' END
            )
            WHERE NOT pg_input_is_valid(birthdate, 'date')
               OR NOT pg_input_is_valid(height, 'numeric')
        """))
        
        # Migrate valid rows
        await session.execute(text("""
            INSERT INTO player (slug, first_name, last_name, birth_date, height_inches)
            SELECT 
                lower(last_name) || substring(first_name, 1, 2) || '01',
                first_name, last_name, 
                birthdate::date, height::numeric
            FROM staging_players
            WHERE validation_errors IS NULL OR validation_errors = '{}'
            ON CONFLICT (slug) DO UPDATE SET ...
        """))
```

### 2.4 SQLite Migration Strategy

```bash
# Using pgloader for SQLite -> PostgreSQL
pgloader sqlite:///raw-data/database/sqlite/nba.sqlite \
         postgresql://user:pass@localhost/nba \
         --with "data only" \
         --cast "type text to varchar"
```

### 2.5 API Enhancements

Add these query parameters:

| Endpoint | New Parameters |

|----------|---------------|

| `/api/v1/players` | `season`, `team`, `position`, `isActive` |

| `/api/v1/players/{id}/stats` | `seasonType` (regular/playoff), `perMode` (totals/per_game) |

| `/api/v1/games` | `startDate`, `endDate`, `isPlayoff`, `team` |

| `/api/v1/standings` | `date` (point-in-time standings) |

### 2.6 UI Pages (MVP Scope)

| Page | Data Source | Priority |

|------|-------------|----------|

| Player Profile | `player` + `player_career_stats` view | P0 |

| Player Season Log | `player_box_score` | P0 |

| Team Roster | `player` + current roster | P0 |

| Game Box Score | `game` + `box_score` + `player_box_score` | P0 |

| Season Schedule | `game` filtered by season | P0 |

| Standings | `team_season` aggregated | P0 |

| League Leaders | `player_season` ranked | P1 |

| Player Comparison | `player_career_stats` multiple | P1 |

---

## Phase 3: Execution Order

### Step 1: Seed Data Infrastructure

1. Create staging tables migration
2. Implement CSV import service with COPY protocol
3. Map each raw-data CSV to target tables
4. Run pgloader for SQLite database
5. Validate and migrate to production tables

### Step 2: Materialized Views

1. Create `player_career_stats` materialized view
2. Create `team_season_standings` materialized view
3. Add refresh triggers/scheduled jobs

### Step 3: API Extensions

1. Add query parameter support to existing endpoints
2. Implement pagination with cursor-based approach
3. Add `/api/v1/players/{id}/career` endpoint using materialized view

### Step 4: UI Implementation

1. Enhance existing game detail page
2. Build player profile page with career stats
3. Build standings page with live data
4. Add season/team filtering UI components

---

## Phase 4: Quality & Iteration

### Data Validation Checklist

- [ ] All 6,700 players imported with valid slugs
- [ ] All seasons (1946-2026) have schedule data
- [ ] Player stats totals match across CSV sources
- [ ] No orphaned foreign keys (player_box_score -> player)
- [ ] Materialized views refresh < 30 seconds

### Performance Targets

- Player career lookup: < 50ms (using materialized view)
- Season schedule query: < 100ms
- Game box score: < 200ms
- Full text player search: < 100ms (existing Meilisearch)

---

## Key Files/Locations

| Purpose | Location |

|---------|----------|

| Strategic docs | `docs/strategy/` (new) |

| Implementation specs | `docs/specs/` (new) |

| Schema reference | `docs/reference/schema.md` (new) |

| API reference | `docs/reference/api.md` (new) |

| Raw seed data | `raw-data/` (existing) |

| DB migrations | `webapp/backend/alembic/versions/` |

| Ingestion services | `webapp/backend/app/ingestion/` |

| API endpoints | `webapp/backend/app/api/v1/endpoints/` |

| Frontend pages | `webapp/frontend/app/` |

---

## Mermaid: Complete Data Flow

```mermaid
flowchart LR
    subgraph DataSources["Data Sources"]
        scraper[Scraper Service]
        csv[CSV Files<br/>47 files]
        sqlite[SQLite DB<br/>nba.sqlite]
    end
    
    subgraph Ingestion["Ingestion Layer"]
        staging[Staging Tables<br/>UNLOGGED]
        validator[Validation<br/>pg_input_is_valid]
        mapper[Entity Mappers]
    end
    
    subgraph Storage["PostgreSQL"]
        core[Core Tables<br/>player, game, team]
        stats[Stats Tables<br/>box_score, player_season]
        views[Materialized Views<br/>career_stats]
    end
    
    subgraph API["FastAPI"]
        rest[REST Endpoints<br/>/api/v1/*]
        celery[Celery Tasks<br/>refresh views]
    end
    
    subgraph UI["Next.js 15"]
        pages[React Server Components]
        search[Meilisearch]
    end
    
    scraper --> mapper
    csv -->|COPY| staging
    sqlite -->|pgloader| staging
    staging --> validator
    validator --> mapper
    mapper --> core
    mapper --> stats
    core --> views
    stats --> views
    
    core --> rest
    stats --> rest
    views --> rest
    rest --> pages
    core --> search
    search --> pages
```