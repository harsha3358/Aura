# Database Schema

## Extensions
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## Core Tables

### extraction_feedback
```sql
CREATE TABLE extraction_feedback (
    id UUID PRIMARY KEY,
    extraction_run_id UUID,
    user_id UUID,
    feedback_type TEXT,
    comment TEXT,
    created_at TIMESTAMPTZ
);
```

### model_usage
```sql
CREATE TABLE model_usage (
    id UUID PRIMARY KEY,
    user_id UUID,
    model_name TEXT,
    tokens_in INT,
    tokens_out INT,
    estimated_cost FLOAT,
    latency_ms INT,
    created_at TIMESTAMPTZ
);
```

### decision_outcomes
```sql
CREATE TABLE decision_outcomes (
    id UUID PRIMARY KEY,
    decision_id UUID,
    outcome TEXT,
    success_score FLOAT,
    lessons_learned TEXT,
    created_at TIMESTAMPTZ
);
```
