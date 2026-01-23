# Code Audit Report

## Executive Summary
The `baller-hub` repository is a well-structured monorepo leveraging modern tooling (`uv` for Python, `npm`/`Next.js 15` for Frontend). The core `scraper` library is mature with excellent test coverage, while the `webapp` (Backend + Frontend) is in early-to-mid development stages with solid scaffolding but lighter test coverage.

**Overall Health Score**: 🟡 **Good (with gaps)**
- **Infrastructure**: Strong (uv workspaces, Docker, GitHub Actions).
- **Code Quality**: Mixed (Strict linters enabled but failing in backend/scripts).
- **Testing**: Excellent for Scraper, Basic for App.

---

## 1. Infra Health

### Monorepo Structure
- **Root**: Python-centric with `uv` workspace. Contains global `tests/` and shared configuration.
- **Src**: cleanly separated into `scraper` (library) and `webapp` (application).
- **Backend**: FastAPI service nested in `src/webapp/backend`. correctly identified as a workspace member.
- **Frontend**: Next.js 15 app in `src/webapp/frontend`.

### Tooling Configuration
| Tool | Status | Config Location | Notes |
|------|--------|-----------------|-------|
| **uv** | ✅ Healthy | `pyproject.toml` | Workspace set up correctly. |
| **Ruff** | ⚠️ Issues | `pyproject.toml` | Configured but **failing** checks (Complexity, Pathlib, etc.). |
| **Ty** | ✅ Healthy | `pyproject.toml` | Type checker passing (clean run). |
| **Pre-commit**| ✅ Healthy | `.pre-commit-config.yaml` | Hooks for ruff, formatting, and ty present. |
| **CI/CD** | ✅ Healthy | `.github/workflows/ci.yml` | Split jobs for Backend (Python) and Frontend (Node). |
| **Frontend** | ⚠️ Issues | `package.json` | `npm run lint` failing due to Prettier formatting rules. |

---

## 2. Test Coverage

### 🟢 Scraper (`tests/`)
- **Unit**: Extensive coverage of parsers, HTML wrappers, and output logic.
- **Integration**: robust system using frozen HTML fixtures (`tests/integration/files`) and `requests_mock`.
- **End-to-End**: Uses cassettes to simulate full client interactions.
- **Assessment**: **Production Grade**.

### 🟡 Backend (`src/webapp/backend/tests`)
- **Unit**: Basic health checks and service tests exist (`test_health.py`, `test_mappers.py`).
- **Integration**: Directory exists but appears empty/underutilized.
- **Assessment**: **Early Stage**. Critical business logic needs more coverage.

### 🔴 Frontend (`src/webapp/frontend`)
- **Unit**: Vitest configured. Only one smoke test (`page.test.tsx`) exists.
- **Integration**: No integration/E2E tests (Playwright/Cypress) found.
- **Assessment**: **Minimal**.

---

## 3. Tooling Gaps & Technical Debt

### Linting Violations (Blocking Clean CI)
- **Python**: `uv run ruff check .` failed with:
    - `PLR0913`: Too many arguments (Client API design issue).
    - `PTH*`: Use of `os.path` instead of `pathlib` in tests.
    - `DTZ*`: Unsafe timezone usage (`datetime.utcnow()`).
    - `PLR2004`: Magic numbers in tests.
    - `INP001`: Missing `__init__.py` in test subdirectories.
- **Frontend**: `npm run lint` failed due to `prettier/prettier` rule violations in test files.

### Architectural Debt
- **Global Tests vs App Tests**: The root `tests/` folder is heavily scraper-focused. As the webapp grows, the distinction between "global library tests" and "webapp tests" may become blurred.
- **Complexity**: `scripts/analyze_csv_relationships.py` flagged for high complexity (`PLR0912`, `PLR0915`).

### Documentation
- **README**: Mentions a "Restructuring Plan" (Rename `src/` to `scraper/`, etc.) which conflicts with the current `src/scraper` layout. The docs might be slightly ahead or behind the actual structure.
- **AGENTS.md**: Comprehensive and up-to-date.

---

## 4. Recommendations

### Immediate Actions (Quick Wins)
1.  **Fix Linting Errors**:
    - Run `uv run ruff format .` and `npm run format` to fix formatting issues.
    - Mass-apply safe fixes: `uv run ruff check --fix .`
    - Manually address `DTZ` (timezone) and `PTH` (pathlib) errors, or add to `ignore` list if tech debt is acceptable for now.
2.  **Add `__init__.py`**: Create empty `__init__.py` files in all test subdirectories to resolve `INP001`.

### Short Term (High Value)
3.  **Flesh out Backend Integration Tests**: Populate `src/webapp/backend/tests/integration` with tests that use the Dockerized DB (or mocked DB session) to verify API-to-DB flows.
4.  **Enhance Frontend Testing**: Add tests for critical components (e.g., `LeagueLeaders`, `TodaysGames`) beyond just "it renders".

### Long Term
5.  **Refactor Client API**: Address `PLR0913` (Too many arguments) by introducing parameter objects or Pydantic models for complex query filters.
6.  **Update Documentation**: Align `README.md` "Restructuring Plan" with the actual state of the repo to avoid confusion.
