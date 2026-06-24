# Testing Strategy

Layers:
- Unit: pytest
- Integration: pytest + test DB
- Benchmark: Custom evaluator (500 examples, Precision/Recall)
- E2E: Playwright
- LLM: Regression suite
