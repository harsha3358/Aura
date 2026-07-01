# AURA Developer Onboarding Guide

Welcome! This guide provides a detailed walkthrough for setting up AURA on your local developer machine, running all dependencies, executing tests, and troubleshooting common issues.

---

## 1. Prerequisites

Before starting, ensure you have the following installed globally:
- **Node.js**: `20.x` (or newer)
- **Python**: `3.11.x`
- **Docker & Docker Compose**: (For local PostgreSQL + pgvector database)
- **Git**: (To clone and track branch versions)
- **Ollama**: (Optional: for running local cognitive extraction LLMs, default model: `llama3`)

---

## 2. Installation & Setup

Cloning the repository and initializing dependencies:

```bash
# 1. Clone the repository
git clone https://github.com/harsha3358/Aura.git
cd Aura

# 2. Configure root development tools
npm install

# 3. Setup Frontend dependencies
cd apps/web
npm ci
cd ../..

# 4. Setup Backend virtual environment (Windows commands)
cd apps/api
python -m venv venv
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\pip install -r requirements.txt
cd ../..
```
*(On POSIX/macOS systems, use `venv/bin/python` and `venv/bin/pip`)*

---

## 3. Running Dependencies

AURA depends on a PostgreSQL database container with the `pgvector` extension.

### A. Run Database Container
Use Docker Compose from the repository root:
```bash
# Start Postgres in background
docker compose up -d
```
Verify the container is active by checking docker processes:
```bash
docker ps
```
The database port maps `5433` on the host to `5432` inside the container.

### B. Run Ollama (LLM Engine)
To enable local cognitive extraction, download Ollama and pull the default model:
```bash
ollama pull llama3
```
Ensure Ollama is running on its default host `http://localhost:11434`.

---

## 4. Launching Application Servers

To run AURA locally, start both the backend API and the frontend Vite web server:

### A. Run Backend API
```bash
cd apps/api
# Apply migrations to create the database schema
venv\Scripts\alembic upgrade head

# Launch Uvicorn dev server
venv\Scripts\uvicorn app.main:app --reload --port 8000
```
*(The backend API Swagger documentation will be available at `http://localhost:8000/docs`)*

### B. Run Frontend Web App
```bash
cd apps/web
# Launch Vite dev server
npm run dev
```
*(Open `http://localhost:5173` in your browser. Default mock login details: `harsha@aura.run` / `password123`)*

---

## 5. Running Validation & Verification

AURA includes strict quality gates. You should run these manually before pushing commits:

```bash
# 1. Run standard quality checks (Hygiene, README, Linting, Unit tests)
npm run verify

# 2. Run release checks (Includes package audits for vulnerabilities)
npm run verify:release

# 3. Run screenshot automation E2E tests (requires both servers running on port 8000 & 5173)
node scripts/capture_screenshots.js
```

---

## 6. Troubleshooting Common Errors

### 1. `ImportError: No module named 'app'`
- **Reason**: Python cannot find the root `app` package.
- **Solution**: Set the python path environment variable. Run `export PYTHONPATH=.` on Unix or `$env:PYTHONPATH="."` on Windows PowerShell prior to running pytest.

### 2. `SQLAlchemy / connection refused on port 5433`
- **Reason**: Docker Postgres container is not running or port 5433 is occupied.
- **Solution**: Execute `docker ps` to ensure the container is active. If port 5433 is in use, verify no other local postgres instance is bound to it.

### 3. `vector extension does not exist`
- **Reason**: The postgres container doesn't include the vector extension.
- **Solution**: Check that the docker image configured in `docker-compose.yml` is `pgvector/pgvector:pg16`, not standard `postgres`.

### 4. `Ollama call failed / Connection refused`
- **Reason**: Ollama server is offline.
- **Solution**: If Ollama is offline, the backend API automatically catches the connection error and triggers a mock JSON extraction fallback (defined in `app/services/llm.py`). Ensure the mock fallback works, or start the local Ollama app.
