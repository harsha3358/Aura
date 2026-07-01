# AURA CI/CD Pipeline Documentation

This document explains the architecture, jobs, configuration, and troubleshooting steps for AURA's Continuous Integration and Continuous Deployment (CI/CD) pipelines.

## Workflow Architecture

The CI pipeline runs on every push and pull request targeting the `main` branch. It uses a parallelized, modular design leveraging GitHub Actions **reusable workflows** to isolate job runtimes and simplify maintenance.

```mermaid
graph TD
    A[ci.yml - Orchestrator] --> B[release-check.yml]
    A --> C[backend.yml]
    A --> D[frontend.yml]
    A --> E[e2e.yml]
    B --> F[summary]
    C --> F
    D --> F
    E --> F
    F[generate_ci_summary.js]
```

---

## Workflow Directory Structure

All workflow configuration files are located under `.github/workflows/`:
- **[ci.yml](file:///.github/workflows/ci.yml)**: The entry-point orchestrator. It manages execution concurrency, parallelizes sub-workflows, and publishes a markdown summary of test results.
- **[release-check.yml](file:///.github/workflows/release-check.yml)**: Validates code linting, formatting, type checking, security audits, README links, and repository hygiene.
- **[backend.yml](file:///.github/workflows/backend.yml)**: Spins up the `pgvector` service container, runs database migrations, and executes the backend FastAPI test suite.
- **[frontend.yml](file:///.github/workflows/frontend.yml)**: Runs Vitest unit tests and builds the Vite production application bundle.
- **[e2e.yml](file:///.github/workflows/e2e.yml)**: Starts backend & frontend servers in the background, waits for ports to open, runs Playwright E2E smoke tests, and uploads screenshot artifacts.

---

## Detailed Job Responsibilities

### 1. Quality & Release Checks (`release-check.yml`)
- **Repository Hygiene**: Runs `node scripts/check_hygiene.js` to fail if forbidden folders/files (e.g. untracked `venv`, `node_modules`, `.env`, `.log`) are committed or unignored.
- **README Validation**: Runs `node scripts/verify_readme.js` to verify README image relative links exist and match filename casing exactly (case-sensitive check).
- **Architecture Compliance**: Runs `node scripts/check_architecture.js` to print warnings if architectural source files were updated without modifying `ARCHITECTURE.md`.
- **Linter & Formatter**: Enforces `ruff check` and `ruff format --check` (Python) and `eslint`/`prettier --check` (React).
- **TypeScript**: Runs `npx tsc --noEmit` in `apps/web` to catch compilation type errors.
- **Security Auditing**: Runs `pip-audit` for backend requirements and `npm audit --audit-level=high` for frontend packages.

### 2. Backend Suite (`backend.yml`)
- **Database Service**: Spins up a Docker container using `pgvector/pgvector:pg16` on host port `5433` with database name `aura_db`.
- **Database Schema**: Applies migrations using `alembic upgrade head`.
- **Unit & Integration Tests**: Executes `pytest` with coverage report generation (`pytest-cov`).

### 3. Frontend Suite (`frontend.yml`)
- **Unit Tests**: Runs React component tests using Vitest (`vitest run`).
- **Production Compilation**: Executes `npm run build` using Vite to verify error-free building.

### 4. E2E Smoke Tests (`e2e.yml`)
- **Environment**: Sets up Python, Node, and spins up PostgreSQL + pgvector database.
- **Application Startup**: Runs both servers in background mode (FastAPI on port `8000`, Vite on port `5173`).
- **Playwright Test**: Runs `node scripts/capture_screenshots.js` which performs an E2E user walkthrough, verifies interactive workflows, and captures product screenshots.

---

## Environment Variables & Secrets

- **`DATABASE_URL`**: Used by the backend and migrations. Hardcoded in local development to `postgresql+asyncpg://aura:password@127.0.0.1:5433/aura_db`. Overridden dynamically in test environments or CI steps where appropriate.
- **`SUPABASE_JWT_SECRET`**: (Optional) Supabase token signature key. If missing, the backend automatically runs in development bypass mode, authenticating mock user profiles.

---

## Local Commands Mirroring CI

You can run identical validation tasks on your developer machine before pushing to remote:

```bash
# 1. Verify README references and case sensitivity
node scripts/verify_readme.js

# 2. Verify repository hygiene
node scripts/check_hygiene.js

# 3. Check architecture compliance
node scripts/check_architecture.js

# 4. Run backend tests (requires active postgres on port 5433)
cd apps/api
venv/Scripts/python -m pytest

# 5. Run frontend tests and compile build
cd apps/web
npm run test
npm run build
```

---

## Troubleshooting CI Failures

1. **`❌ FORBIDDEN FILE TRACKED/UNIGNORED`**:
   - Run `git rm -r --cached <file>` to stop tracking the file.
   - Verify the file is ignored in the root `.gitignore`.

2. **`❌ CASE MISMATCH`**:
   - Check that filename capitalization in `README.md` matches the actual file on disk. Linux GitHub runners are case-sensitive.

3. **`❌ selector [data-testid="..."] not found`**:
   - Check the logs of the Playwright smoke test. It indicates that either the frontend Vite server failed to start, the backend API crashed, or the UI layout changed. Check `error.log` and uploaded screenshot artifacts under the GitHub actions run to debug visually.
