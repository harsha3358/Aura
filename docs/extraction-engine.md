# Extraction Engine Design

Input: Raw user message text, active context, recent conversation window
Output: facts, decisions, considered_options, contexts, tasks, deadlines, context_shift_detected

Prompt Strategy: System prompt with Knowledge Contract rules, 8-12 few-shot examples, JSON formatting.
