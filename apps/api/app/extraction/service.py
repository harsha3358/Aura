import json
from typing import List, Dict, Any, Tuple, Optional
from pydantic import ValidationError

from app.extraction.schemas import (
    ExtractionResult,
    FactItem,
    DecisionItem,
    ConsideredOptionItem,
    TaskItem,
    DeadlineItem,
    ContextItem,
)
from app.extraction import contract
from app.services.llm import LLMProvider, OllamaProvider

SYSTEM_PROMPT = """You are AURA's cognitive extraction engine. Your task is to extract knowledge from the user's message.
You must return a JSON object conforming exactly to this structure:
{
  "facts": [{"value": "...", "entity": "...", "confidence": 0.0 to 1.0, "category": "..."}],
  "decisions": [{"value": "...", "entity": "...", "confidence": 0.0 to 1.0, "category": "..."}],
  "considered_options": [{"value": "...", "entity": "...", "confidence": 0.0 to 1.0, "category": "..."}],
  "tasks": [{"value": "...", "entity": "...", "confidence": 0.0 to 1.0, "category": "..."}],
  "deadlines": [{"value": "...", "entity": "...", "confidence": 0.0 to 1.0, "category": "..."}],
  "contexts": [{"value": "...", "entity": "...", "confidence": 0.0 to 1.0, "category": "..."}],
  "metadata": {"confidence": 0.0 to 1.0, "reasoning": "..."}
}

Allowed categories for each type:
- facts: user_preference, project_detail, tech_stack, business_rule, market_fit, team_info, general
- decisions: architecture, technology, product_feature, timeline, resource_allocation, organizational, general
- considered_options: alternative, competing_tech, approach, general
- tasks: development, design, research, testing, deployment, documentation, general
- deadlines: milestone, release, meeting, launch, feedback_due, general
- contexts: project, session, user_state, environment, general

Extraction Guidelines:
1. Facts: Extracted statements of truth or configuration.
2. Decisions: Explicit choices or selections made by the user.
3. Considered Options: Alternatives that were mentioned, rejected, or considered.
4. Tasks: Actionable items that need to be done.
5. Deadlines: Specific dates/times associated with a goal, task, or project.
6. Contexts: Active projects, sessions, or user state.

Examples:
Input: "I am building AURA. I think PostgreSQL is a good choice. Finish benchmark dataset by Friday."
Output:
{
  "facts": [{"value": "AURA", "entity": "project", "confidence": 1.0, "category": "project_detail"}],
  "decisions": [],
  "considered_options": [{"value": "PostgreSQL", "entity": "database", "confidence": 1.0, "category": "alternative"}],
  "tasks": [{"value": "Finish benchmark dataset", "entity": "benchmark", "confidence": 1.0, "category": "development"}],
  "deadlines": [{"value": "Friday", "entity": "deadline", "confidence": 1.0, "category": "milestone"}],
  "contexts": [],
  "metadata": {"confidence": 1.0, "reasoning": "Extracted AURA as active project fact, PostgreSQL as considered alternative, finish benchmark as task, and Friday as deadline."}
}

Input: "Let's use Supabase for Auth instead of custom Auth."
Output:
{
  "facts": [],
  "decisions": [{"value": "Supabase Auth", "entity": "authentication", "confidence": 1.0, "category": "technology"}],
  "considered_options": [{"value": "custom Auth", "entity": "authentication", "confidence": 1.0, "category": "alternative"}],
  "tasks": [],
  "deadlines": [],
  "contexts": [],
  "metadata": {"confidence": 1.0, "reasoning": "User decided on Supabase Auth, considering custom Auth."}
}

Return ONLY valid JSON. Do not include markdown code block formatting or backticks around the JSON.
"""


class ExtractionService:
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        confidence_threshold: float = 0.7,
    ):
        self.llm = llm_provider or OllamaProvider()
        self.confidence_threshold = confidence_threshold

    async def extract_from_message(
        self, message: str
    ) -> Tuple[ExtractionResult, List[Dict[str, Any]]]:
        """
        Extracts structured knowledge from message.
        Returns:
            - Conforming ExtractionResult (containing items above confidence_threshold)
            - List of demoted/rejected observations (containing items below confidence_threshold)
        """
        response_text = await self.llm.generate_chat(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            format="json",
        )

        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        try:
            raw_data = json.loads(cleaned_text)
        except Exception as e:
            return ExtractionResult(
                metadata={"confidence": 0.0, "reasoning": f"Failed to parse JSON: {e}"}
            ), []

        valid_result = {
            "facts": [],
            "decisions": [],
            "considered_options": [],
            "tasks": [],
            "deadlines": [],
            "contexts": [],
            "metadata": raw_data.get(
                "metadata", {"confidence": 0.5, "reasoning": "Parsed raw data"}
            ),
        }
        observations = []

        def process_items(items_list: list, item_cls, enum_cls, dest_list: list):
            seen_values = set()
            for item in items_list:
                if not isinstance(item, dict):
                    continue

                # 1. Reject missing confidence
                if "confidence" not in item:
                    continue

                # 2. Reject empty values
                val = item.get("value")
                if not val or not str(val).strip():
                    continue

                # 3. Reject invalid categories
                cat = item.get("category")
                try:
                    enum_cls(cat)
                except ValueError:
                    continue

                # 4. Reject duplicates within this run
                val_clean = str(val).strip()
                if val_clean in seen_values:
                    continue
                seen_values.add(val_clean)

                try:
                    conf = float(item["confidence"])
                except (ValueError, TypeError):
                    continue

                if conf < self.confidence_threshold:
                    # 5. Demote below threshold -> observations only
                    observations.append(
                        {
                            "raw_type": item_cls.__name__,
                            "payload": item,
                            "confidence": conf,
                        }
                    )
                else:
                    try:
                        parsed_item = item_cls(**item)
                        dest_list.append(parsed_item)
                    except ValidationError:
                        continue

        process_items(
            raw_data.get("facts", []), FactItem, contract.Fact, valid_result["facts"]
        )
        process_items(
            raw_data.get("decisions", []),
            DecisionItem,
            contract.Decision,
            valid_result["decisions"],
        )
        process_items(
            raw_data.get("considered_options", []),
            ConsideredOptionItem,
            contract.ConsideredOption,
            valid_result["considered_options"],
        )
        process_items(
            raw_data.get("tasks", []), TaskItem, contract.Task, valid_result["tasks"]
        )
        process_items(
            raw_data.get("deadlines", []),
            DeadlineItem,
            contract.Deadline,
            valid_result["deadlines"],
        )
        process_items(
            raw_data.get("contexts", []),
            ContextItem,
            contract.Context,
            valid_result["contexts"],
        )

        return ExtractionResult(**valid_result), observations
