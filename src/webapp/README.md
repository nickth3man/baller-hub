# Basketball Reference Clone - Web Application

A local clone of basketball-reference.com built on top of the existing Python scraper.

## Architecture

```
src/webapp/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/endpoints/  # REST API endpoints
│   │   ├── core/              # Configuration, settings
│   │   ├── db/                # Database session, migrations
│   │   ├── models/            # SQLModel database models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # Business logic layer
│   │   └── utils/             # Utilities
│   ├── tests/                 # Backend tests
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                   # Next.js 15 frontend
│   ├── app/                   # App Router pages
│   ├── (components)/          # React components
│   │   ├── layout/            # Header, Footer, Navigation
│   │   ├── stats/             # Statistics components
│   │   ├── ui/                # Reusable UI components
│   │   └── charts/            # Data visualization
│   ├── lib/                   # Utilities, API client
│   ├── hooks/                 # Custom React hooks
│   ├── types/                 # TypeScript types
│   └── public/                # Static assets
├── docker/                     # Docker configs
├── scripts/                    # CLI scripts
└── docs/                       # Documentation
```

## Tech Stack

### Backend
- **Framework**: FastAPI 0.115+
- **Database**: PostgreSQL 16 with SQLModel ORM
- **Caching**: Redis 7
- **Search**: Meilisearch
- **Task Queue**: Celery
- **Real-time**: WebSocket (FastAPI native)

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS 3.4
- **State**: TanStack Query + Zustand
- **Charts**: Recharts

## Quick Start

### Development with Docker

```bash
cd src/webapp
docker compose up -d
```

Services:
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Meilisearch: http://localhost:7700

### Manual Setup

**Backend:**
```bash
cd src/webapp/backend
uv sync
uv run uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd src/webapp/frontend
npm install
npm run dev
```

### Populate the Database

For a full historical load, run the CSV ingestion pipeline and then rebuild
search indices:

```bash
cd src/webapp
python -m scripts.seed_db --bootstrap
```

To seed a specific season from the scraper:

```bash
python -m scripts.seed_db --season 2024
```

## API Endpoints

### Players
- `GET /api/v1/players` - List players with pagination
- `GET /api/v1/players/{slug}` - Get player details
- `GET /api/v1/players/{slug}/game-log/{year}` - Player game log
- `GET /api/v1/players/{slug}/career-stats` - Career statistics

### Teams
- `GET /api/v1/teams` - List all teams
- `GET /api/v1/teams/{abbrev}` - Team details
- `GET /api/v1/teams/{abbrev}/roster/{year}` - Team roster
- `GET /api/v1/teams/{abbrev}/schedule/{year}` - Team schedule
- `GET /api/v1/teams/{abbrev}/history` - Franchise history

### Games
- `GET /api/v1/games` - List games with filters
- `GET /api/v1/games/today` - Today's games
- `GET /api/v1/games/{id}` - Game details
- `GET /api/v1/games/{id}/box-score` - Full box score
- `GET /api/v1/games/{id}/play-by-play` - Play-by-play data

### Seasons
- `GET /api/v1/seasons` - List seasons
- `GET /api/v1/seasons/{year}` - Season details
- `GET /api/v1/seasons/{year}/leaders` - Season leaders
- `GET /api/v1/seasons/{year}/player-stats` - All player stats

### Standings
- `GET /api/v1/standings/{year}` - Current standings
- `GET /api/v1/standings/{year}/playoff-bracket` - Playoff bracket

### Search
- `GET /api/v1/search?q={query}` - Search everything
- `GET /api/v1/search/autocomplete?q={query}` - Autocomplete

## Database Models

### Core Entities
- **Player** - Player profiles with biographical data
- **Team** - Team information with franchise history
- **Game** - Game results and metadata
- **Season** - Season configurations
- **League/Conference/Division** - Organizational structure

### Statistics
- **PlayerBoxScore** - Individual game statistics
- **PlayerSeason** - Aggregated season totals
- **PlayerSeasonAdvanced** - Advanced metrics (PER, WS, VORP)
- **TeamSeason** - Team season aggregates
- **BoxScore** - Team-level game statistics
- **PlayByPlay** - Detailed play data

### Supplementary
- **Award/AwardRecipient** - Awards and recipients
- **Draft/DraftPick** - Draft history
- **Franchise** - Franchise lineage tracking

## Integration with Scraper

The webapp integrates with the existing scraper (`src/`) for data ingestion:

```python
from src.scraper.api import client

# Scrape and ingest daily box scores
box_scores = client.player_box_scores(day=15, month=1, year=2025)

# Scrape season totals
totals = client.players_season_totals(season_end_year=2025)
```

A Celery worker handles scheduled scraping tasks to keep data fresh.

## Development Roadmap

### Phase 1: Foundation (Current)
- [x] Project structure
- [x] Database models
- [x] API endpoints (stubs)
- [x] Frontend skeleton
- [ ] Database migrations
- [ ] Scraper integration pipeline

## Documentation

- `docs/overview.md` - Architecture and setup
- `docs/api.md` - REST API reference
- `docs/data-ingestion.md` - CSV and scraper ingestion
- `docs/frontend.md` - Frontend routing and styling

### Phase 2: Core Features
- [ ] Player pages with full stats
- [ ] Team pages with rosters/schedules
- [ ] Game box scores with play-by-play
- [ ] Season leaderboards
- [ ] Standings with playoff brackets

### Phase 3: Advanced Features
- [ ] Full-text search with Meilisearch
- [ ] Player comparison tools
- [ ] Historical data visualization
- [ ] Advanced stat calculators

### Phase 4: Polish
- [ ] Real-time game updates
- [ ] Mobile optimization
- [ ] Performance tuning
- [ ] SEO optimization
