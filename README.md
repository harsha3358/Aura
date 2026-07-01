# AURA – Personal Operating System for Builders

AURA is a production-grade cognitive model application designed to capture builder conversations, extract structured knowledge (facts, decisions, tasks, deadlines), and generate high-quality daily executive briefs.

## What AURA Does
AURA is a Personal Operating System for Builders. It captures conversations, extracts structured knowledge, understands context, learns from user corrections, and generates daily executive briefings that help users remember not only what they decided, but why they decided it.

## North Star Metric
- **Founder Dogfood Metric:** Did AURA save the founder at least 30 minutes today? (YES/NO)

---

## Architecture Stack

- **Frontend:** Vite + React + TypeScript + Zustand (TBD in Phase 2)
- **Backend:** FastAPI + SQLAlchemy + Alembic
- **Database:** PostgreSQL + pgvector
- **LLM:** Ollama (local-first; e.g. `llama3` model)
- **Auth:** Supabase Auth Integration

---

## Directory Structure

```text
Aura/
├── apps/
│   └── api/                  # FastAPI Backend API
│       ├── app/
│       │   ├── extraction/   # Knowledge Contract and Extraction Engine
│       │   ├── models/       # SQLAlchemy models
│       │   ├── routers/      # API endpoints (users, conversations)
│       │   └── services/     # Core services (LLM, etc.)
│       └── tests/            # Test suite (pytest)
├── benchmark/
│   └── v0.1/
│       └── examples.jsonl    # 51 manually labeled evaluation examples
├── docs/                     # Design and specs
└── scripts/
    └── evaluate_extraction.py # Metric evaluation framework (F1, Pollution Rate)
```

---

## Setup & Running Locally

### 1. Run Database Containers
Ensure Docker is running, then start the Postgres database with pgvector:
```bash
docker compose up -d db
```

### 2. Prepare Virtual Environment
Navigate to the API folder, activate your virtual environment, and install dependencies:
```bash
cd apps/api
python -m venv venv
.\\venv\\Scripts\\activate
pip install -r requirements.txt
```

### 3. Run Alembic Migrations
```bash
alembic upgrade head
```

### 4. Run Development Server
```bash
uvicorn app.main:app --reload
```

---

## Validation Status

* Authentication ✅
* Onboarding ✅
* Knowledge Capture ✅
* Knowledge Review ✅
* Executive Brief Generation ✅
* Context Classification ✅
* Founder Dogfood Tested ✅

---

## Product Screenshots

### Screenshots

#### Login

![Login](./Screenshots/Login.png)

#### Onboarding

![Onboarding](./Screenshots/Onboarding.png)

#### Dashboard

![Dashboard](./Screenshots/Dashboard.png)

#### Knowledge Explorer

![Knowledge Explorer](./Screenshots/KnowledgeExplorer.png)

#### Capture Session

![Capture Session](./Screenshots/CaptureSession.png)

#### Extraction Review

![Extraction Chips](./Screenshots/ExtractionChips.png)

#### Edit Workflow

![Edit Workflow](./Screenshots/EditWorkflow.png)

#### Reject Workflow

![Reject Workflow](./Screenshots/RejectWorkflow.png)

#### Executive Brief

![Executive Brief](./Screenshots/ExecutiveBrief.png)

#### Mobile View

![Mobile View](./Screenshots/MobileView.png)

#### Desktop View

![Desktop View](./Screenshots/DesktopView.png)

---

## Developer Resources & Documentation

To set up AURA locally, run tests, or contribute, please refer to our documentation ecosystem:

* **[Developer Onboarding Guide](docs/DEVELOPER_GUIDE.md)**: Full setup details for databases, backend API, Vite web server, and local Ollama nodes.
* **[Contributing Guidelines](CONTRIBUTING.md)**: Process guidelines, branch strategies, definition of done, and code review criteria.
* **[Architecture Specifications](ARCHITECTURE.md)**: System blueprints, DB designs, and routing details.
* **[CI/CD Pipelines Guide](docs/CI_CD.md)**: Quality gates, Husky hooks, and GitHub Actions details.
* **[Engineering Standards](docs/ENGINEERING_STANDARDS.md)**: Naming conventions, component structures, and state management rules.
* **[Architecture Decisions (ADR)](docs/adr/README.md)**: Log of major design and technical selections.

---

## Testing & Quality Gates

Run the verification suites before committing or staging your code:
```bash
# Run local fast verification gates
npm run verify

# Run local release verification gates
npm run verify:release
```

---

## Benchmark Evaluation Framework

To evaluate the quality of the Extraction Engine (Precision, Recall, F1, and Knowledge Pollution Rate) against the benchmark v0.1 dataset:

### Mock / Dry Run
```bash
python scripts/evaluate_extraction.py --mock
```

### Live Run (requires Ollama running on port 11434)
```bash
python scripts/evaluate_extraction.py
```

