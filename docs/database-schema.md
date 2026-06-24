# Database Schema

## Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

## Core Tables
- users: id, email, display_name, timezone, onboarding_completed
- contexts: id, user_id, name, description, confidence, is_active
- projects: id, user_id, project_name, description, status, context_id
- conversations: id, user_id, title, context_id
- messages: id, conversation_id, role, content
- facts: id, user_id, entity, value, context_id, project_id, confidence, embedding
- decisions: id, user_id, chosen_option, rejected_options, reason, confidence
- considered_options: id, user_id, option_text, confidence
- observations: id, user_id, raw_type, payload, confidence
- tasks: id, user_id, task, status, priority, deadline
- deadlines: id, user_id, title, due_at
- hypotheses: id, user_id, context_id, statement, confidence
- evidence: id, hypothesis_id, decision_id, weight, is_contradiction
- strategies: id, user_id, hypothesis_id, recommendation, status
- executive_briefs: id, user_id, brief_date, content
- benchmark tables: benchmark_examples, extraction_runs, benchmark_eval_runs
