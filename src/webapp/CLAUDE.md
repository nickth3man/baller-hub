# WEBAPP KNOWLEDGE BASE

**Context:** Full-stack web application (FastAPI backend + Next.js frontend)

See root [`AGENTS.md`](../../AGENTS.md) for project-wide conventions.
See [`PLAN.md`](../../PLAN.md) for the current project goal and roadmap.

## Overview

Web application that serves scraped basketball data through a REST API and modern React frontend.
The backend integrates with the scraper (`src/scraper/`) for data ingestion.

## Structure

```
src/webapp/
├── backend/                     # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/endpoints/    # REST API endpoints
│   │   ├── core/                # Configuration, settings
│   │   ├── db/                  # Database session, migrations
│   │   ├── ingestion/           # Scraper integration layer
│   │   ├── models/              # SQLModel database models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── search/              # Meilisearch integration
│   │   ├── services/            # Business logic layer
│   │   └── utils/               # Utilities
│   ├── alembic/                 # Database migrations
│   ├── Dockerfile
│   └── pyproject.toml           # Backend-specific dependencies
├── frontend/                    # Next.js 15 frontend
│   ├── app/                     # App Router pages
│   ├── (components)/            # React components
│   │   ├── layout/              # Header, Footer, Navigation
│   │   └── stats/               # Statistics components
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├── scripts/
│   └── seed_db.py               # Database seeding script
├── docker-compose.yml
└── README.md
```

## Tech Stack

### Backend
- **Framework:** FastAPI 0.115+
- **ORM:** SQLModel (SQLAlchemy + Pydantic)
- **Database:** PostgreSQL 16
- **Caching:** Redis 7
- **Search:** Meilisearch
- **Task Queue:** Celery with Redis broker
- **Async HTTP:** httpx

### Frontend
- **Framework:** Next.js 15 (App Router)
- **UI:** React 18
- **Styling:** Tailwind CSS 3.4
- **State:** TanStack Query + Zustand
- **Charts:** Recharts

## Commands

### Backend

```bash
cd src/webapp/backend

# Install dependencies
uv sync

# Start dev server
uv run uvicorn app.main:app --reload

# Run database migrations
uv run alembic upgrade head

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Run backend tests
uv run pytest

# Lint
uv run ruff check .

# Type check
uv run ty check .
```

### Frontend

```bash
cd src/webapp/frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Lint
npm run lint

# Format
npm run format
```

### Docker (Full Stack)

```bash
cd src/webapp

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

**Services:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Meilisearch: http://localhost:7700

## Backend Architecture

### Layer Structure

```
Request → Endpoint → Service → Repository/Model → Database
                         ↓
                    Scraper (for ingestion)
```

- **Endpoints** (`api/v1/endpoints/`): HTTP handlers, validation, response formatting
- **Services** (`services/`): Business logic, orchestration
- **Models** (`models/`): SQLModel database models
- **Schemas** (`schemas/`): Pydantic request/response DTOs
- **Ingestion** (`ingestion/`): Scraper integration, data transformation

### API Conventions

- All endpoints under `/api/v1/`
- RESTful resource naming (plural nouns)
- Pydantic schemas for request/response validation
- Service layer for business logic (endpoints stay thin)

### Database Models

**Core Entities:**
- `Player` - Player profiles
- `Team` - Team information
- `Game` - Game results
- `Season` - Season configuration

**Statistics:**
- `PlayerBoxScore` - Individual game stats
- `PlayerSeason` - Season aggregates
- `PlayerSeasonAdvanced` - Advanced metrics

### Scraper Integration

```python
# In ingestion/scraper_service.py
from src.scraper.api import client

# Fetch data via scraper
box_scores = client.player_box_scores(day=15, month=1, year=2025)

# Transform and store
for box_score in box_scores:
    db_record = mapper.to_db_model(box_score)
    repository.save(db_record)
```

## Frontend Architecture

### App Router Structure

```
app/
├── page.tsx                 # Home page
├── layout.tsx               # Root layout
├── globals.css              # Global styles
├── providers.tsx            # React Query provider
├── games/
│   ├── page.tsx             # Games list
│   └── [id]/page.tsx        # Game details
├── players/
│   ├── page.tsx             # Players list
│   └── [slug]/
│       ├── page.tsx         # Player profile
│       └── game-log/[year]/page.tsx
├── teams/
│   ├── page.tsx             # Teams list
│   └── [abbrev]/page.tsx    # Team details
├── seasons/
├── standings/
└── search/
```

### Component Organization

- `(components)/layout/` - Layout components (Header, Footer, SearchBar)
- `(components)/stats/` - Statistics display components
- `(components)/ui/` - Reusable UI primitives (if added)

### State Management

- **Server State:** TanStack Query for API data fetching/caching
- **Client State:** Zustand for UI state (modals, filters, etc.)

## Conventions

### Backend

- **Imports:** Absolute from `app` (e.g., `from app.models import Player`)
- **Async:** Use `async def` for all database operations
- **Error Handling:** HTTPException for API errors
- **Logging:** structlog for structured logs

### Frontend

- **Components:** PascalCase files (e.g., `SearchBar.tsx`)
- **Hooks:** camelCase with `use` prefix (e.g., `usePlayer.ts`)
- **Types:** In component files or `types/` directory
- **Styling:** Tailwind utility classes, avoid custom CSS

## Environment Variables

Backend expects these in `.env`:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=your_key
SECRET_KEY=your_secret
```

See `src/webapp/backend/.env.example` for template.

## Files Never to Modify

- `uv.lock` (backend lock file)
- `package-lock.json` (frontend lock file, if present)
- `alembic/versions/` (migration files are append-only)
