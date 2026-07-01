# Contributing to AURA

Welcome to the AURA developer community! We are excited to build the next-generation personal cognitive OS with you. 

This document serves as your guide to the contribution workflow, branching strategies, Definition of Done, and review guidelines.

---

## Documentation Ecosystem

AURA maintains a structured, cross-linked documentation network. Before making changes, familiarize yourself with these key guides:

- **[README.md](README.md)**: Product overview, quickstart, and features.
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Core design patterns, schemas, and structural boundaries.
- **[docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)**: Step-by-step developer setup, dependency management, and debugging.
- **[docs/CI_CD.md](docs/CI_CD.md)**: Details on automated quality gates and GitHub Actions workflows.
- **[docs/ENGINEERING_STANDARDS.md](docs/ENGINEERING_STANDARDS.md)**: Folder structures, naming conventions, API design, and component rules.
- **[docs/adr/README.md](docs/adr/README.md)**: Architecture Decision Records (ADRs) tracking design choices.

---

## Branching Strategy

AURA follows a structured branching strategy to maintain git history cleanliness and release reliability:

* **`main`**: The stable branch. Directly deployable. Pushing directly to `main` is blocked by branch protection rules; changes must go through pull requests.
* **`feature/*`**: All new features or enhancements must be developed on feature branches (e.g. `feature/capture-session`).
* **`bugfix/*`**: Standard bug fixes and regression adjustments.
* **`hotfix/*`**: Urgent production patches applied directly to restore services.
* **`release/*`**: Pre-release verification branches used for final QA, screenshotting, and changelog consolidation before merging to `main`.

---

## Definition of Done (DoD)

Before any change is merged into `main`, it must meet the following criteria:

1. **Compilation**: Frontend compiles successfully (`npm run build`) and TypeScript check passes (`npx tsc --noEmit`).
2. **Automated Testing**: 100% pass on backend `pytest` and frontend `vitest` unit suites.
3. **Local Quality Verification**: The unified verify check runs successfully (`npm run verify:release`).
4. **Documentation**: Any schema, API, or component changes must be reflected in `ARCHITECTURE.md`, `docs/DEVELOPER_GUIDE.md`, or `docs/ENGINEERING_STANDARDS.md`.
5. **Architectural Decisions**: Significant design changes must have a corresponding **ADR** added in the `docs/adr/` directory.

---

## Review Expectations

We value constructive, thorough code reviews. When reviewing or submitting PRs:
- **Code Readability**: Ensure variable names are self-documenting and complex blocks have clear annotations.
- **Test Coverage**: PRs adding functionality must introduce accompanying unit or integration tests.
- **Accidental Commits**: Check that no transient log files, credentials, local environment settings, or python `__pycache__` directories are staged.

---

## Performance & Quality Standards

To maintain AURA as a premium, high-performance cognitive OS, your code must adhere to these budgets:
- **React Re-renders**: Prevent unnecessary re-renders in components (e.g. use memoization, separate context state, optimize Zustand selector imports).
- **API Call Overhead**: Avoid duplicate queries. Use caching, batch updates, or share Zustand state to reduce backend load.
- **Bundle Size**: Avoid importing heavy, unneeded packages. Ensure code splitting is utilized.
- **Accessibility**: Ensure keyboard outlines and clear focus rings (`focus:outline-none focus:border-[#a78bfa] focus:ring-1 focus:ring-[#a78bfa]`) exist for all interactive elements.
