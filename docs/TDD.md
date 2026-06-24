# Technical Design Document (TDD)

## System Architecture
- Frontend: Vite + React + TypeScript + Tailwind + Zustand
- Backend: FastAPI + SQLAlchemy + Alembic
- Data: PostgreSQL + pgvector
- External: Supabase Auth, Ollama (Local)

## Core Design Principles
- Single extraction path
- Confidence-gated writes
- Context-scoped truth
- Hypotheses are never facts
- Idempotent brief generation
- Ollama-first with provider interface

## Backend Architecture
Request Pipeline: UI -> FastAPI -> ExtractionEngine -> ContextEngine -> KnowledgeContract -> PostgreSQL

## Frontend Architecture
Stack: Vite 6 + React 19 + TS 5 + Tailwind 4 + Zustand + React Router 7 + Supabase JS.
