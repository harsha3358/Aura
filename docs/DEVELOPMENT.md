# Mandatory Development Rules
This is a production-grade software company, not a college project. Every implementation task follows this loop:
1. Make Change
2. Run Relevant Tests
3. Verify App Works
4. Update Docs If Affected
5. Add Benchmark If Bug
6. Git Commit
7. Push To GitHub
8. Update Roadmap Status

## Git Workflow
- Granularity: One logical change = one commit
- Clean start: Before each new task: git status must show clean working tree
- No orphans: Never leave uncommitted work; never skip commits
- History: Every feature, bug fix, and refactor gets its own commit
- Push: Push to GitHub after every completed task (remote: origin/main)
- Roadmap: Update docs/roadmap.md implementation status after each task

Commit message format (Conventional Commits):
feat: ..., fix: ..., refactor: ..., docs: ..., test: ...

## Code Quality Gate
- No compilation errors
- No TypeScript errors (npm run build in apps/web)
- No Python linting errors (ruff check in apps/api)
- No failing tests (pytest, npm test)
- No dead code or unused imports
- No TODO placeholders without issue references

## Documentation Sync Rule
- New API endpoint -> docs/api-spec.yaml
- New DB table/column -> docs/database-schema.md
- New service/engine -> docs/TDD.md + engine-specific doc
- New user-facing feature -> docs/PRD.md
- Architecture change -> docs/TDD.md mermaid diagrams

## Founder Rule (Build Gate)
Never optimize for writing code. Optimize for:
- Executive Brief Quality
- Knowledge Accuracy
- Knowledge Pollution Rate (< 5%)
- Hours Saved Per User Per Week
