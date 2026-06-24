import json
from typing import List, Dict, Any, Optional
from app.services.llm import LLMProvider, OllamaProvider
from app.models.core import Context

SYSTEM_PROMPT = """You are AURA's Context Engine. Your task is to analyze a raw user message and determine if it belongs to an existing context or represents a context shift to a new context.

Existing Contexts:
{existing_contexts_str}

Examples of typical contexts:
- Startup Building (developing AURA, architectural design, startup operations)
- Research (reading academic papers, studying algorithms, analyzing markets)
- Learning (studying new programming languages, learning frameworks, tutorials)
- Career Growth (interviews, job hunt, career strategy, professional network)
- Personal Productivity (daily schedules, life organization, habits)

Your response must be a JSON object with this exact structure:
{{
  "matched_context_name": "Name of Matched Context" or null,
  "shift_detected": true or false,
  "new_context": {{
    "name": "Name of suggested new context",
    "description": "Short description of the new context"
  }} or null,
  "confidence": 0.0 to 1.0,
  "reasoning": "..."
}}

Instructions:
1. If the message clearly matches one of the Existing Contexts (case-insensitive), set "matched_context_name" to that context name, "shift_detected" to false, and "new_context" to null.
2. If the message does NOT match any of the Existing Contexts, set "matched_context_name" to null, "shift_detected" to true, and suggest a new context in "new_context" (e.g. from the examples, or dynamic based on topic).
3. Do not create highly specific, one-off contexts (like "fix-bug-123"). Keep contexts broad and high-level (like "Startup Building").
4. If there are no existing contexts, set "matched_context_name" to null, "shift_detected" to true, and suggest a suitable context in "new_context".

Return ONLY raw valid JSON. Do not wrap in markdown backticks.
"""

class ContextClassifier:
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or OllamaProvider()

    async def classify(self, message: str, existing_contexts: List[Context]) -> Dict[str, Any]:
        existing_contexts_str = "\n".join([
            f"- {c.name}: {c.description or 'No description'}"
            for c in existing_contexts
        ])
        if not existing_contexts_str:
            existing_contexts_str = "(No existing contexts)"
            
        prompt = SYSTEM_PROMPT.format(existing_contexts_str=existing_contexts_str)
        
        response_text = await self.llm.generate_chat([
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ], format="json")
        
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        try:
            return json.loads(cleaned_text)
        except Exception as e:
            return {
                "matched_context_name": None,
                "shift_detected": False,
                "new_context": None,
                "confidence": 0.0,
                "reasoning": f"Failed to parse context JSON: {e}"
            }
