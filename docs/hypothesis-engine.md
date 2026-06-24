# Hypothesis Engine Design

Trigger: Nightly batch + after 5 new decisions.
Pattern Detection: Cluster decisions/facts by context. Generate hypotheses.
Lifecycle: Tentative -> Validated (evidence>=5) -> Rejected (contradictions>=3).
