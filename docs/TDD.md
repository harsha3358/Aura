# Technical Design Document (TDD)

## Extraction Feedback System
```sql
extraction_feedback (
    id UUID PRIMARY KEY,
    extraction_run_id UUID,
    user_id UUID,
    feedback_type TEXT,
    comment TEXT,
    created_at TIMESTAMPTZ
)
```
Feedback values: `correct`, `incorrect`, `partial`. Every incorrect extraction becomes a benchmark candidate.
