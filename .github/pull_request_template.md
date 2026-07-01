## Description

Please include a detailed summary of the changes, the problem solved, and any architectural implications.

Fixes # (issue)

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation Update / Governance change
- [ ] CI/CD or Repository Tooling modification

## Quality Gate Checklist

Please verify that your pull request satisfies all local quality requirements:

- [ ] **Automated Verification**: `npm run verify` passes locally.
- [ ] **Release Verification**: `npm run verify:release` passes locally (including security audits).
- [ ] **Unit Tests**: All backend `pytest` and frontend `vitest` tests pass.
- [ ] **Type Safety**: TypeScript compile checks pass without warnings (`tsc --noEmit`).
- [ ] **Linting & Formatting**: Ruff checks (backend) and ESLint/Prettier checks (frontend) are clean.
- [ ] **Architecture**: `ARCHITECTURE.md` is updated if database schemas, core abstractions, or routing structures changed.
- [ ] **Governance**: Significant architectural decisions are captured in a new **ADR** file under `docs/adr/`.
- [ ] **Clean History**: Commit messages comply with Conventional Commits specifications, are under 72 characters, and use imperative mood.
- [ ] **Hygiene**: Staged files contain no transient log files, credentials, local environment setups, or python `__pycache__` directories.
- [ ] **Accessibility**: Component focus outlines, keyboard focus rings, and tab indexes have been validated.
- [ ] **Performance**: Re-renders in React and API database query calls have been optimized for minimum load.
