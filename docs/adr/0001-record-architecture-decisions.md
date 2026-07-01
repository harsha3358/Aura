# ADR 0001: Record Architecture Decisions

* **Status**: **APPROVED**
* **Date**: 2026-07-01
* **Author**: Harsha
* **Deciders**: Harsha, Antigravity

---

## Context

As AURA grows and onboarding new developers becomes essential, capturing the "why" behind key system-level designs is critical. Standard code comments are often too localized, and git histories become hard to parse for design evolution over months. We need a lightweight, structured way to document technical decisions.

---

## Decision

We will use **Architecture Decision Records (ADRs)** to document significant architectural decisions.
- ADRs are markdown files stored directly in the repository under `docs/adr/`.
- Every ADR follows the standardized layout defined in **[ADR Template](ADR_TEMPLATE.md)**.
- Every record is assigned a sequential 4-digit ID and listed in the index **[ADR Index](README.md)**.
- ADRs are reviewed, approved, and merged via the normal pull request lifecycle.

---

## Consequences

* **Benefits**:
  * Captures design rationale in a central, searchable, and version-controlled format.
  * Accelerates developer onboarding by explaining past constraints.
  * Standardizes the communication of design tradeoffs among deciders.
* **Costs/Drawbacks**:
  * Requires discipline from developers to write and maintain ADRs when design changes occur.
  * Adds minor documentation overhead to pull requests.

---

## Alternatives Considered

1. **Inline Code Comments & Module Docstrings**: Rejected because they lack context on alternative approaches considered or architectural-wide dependencies.
2. **Wiki Pages (GitHub Wiki)**: Rejected because wikis are separated from the git review cycle. We cannot run pull requests or require approvals on wiki edits.
