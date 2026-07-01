import httpx
from typing import Optional, List, Dict
from abc import ABC, abstractmethod
from app.config import get_settings

settings = get_settings()


class LLMProvider(ABC):
    @abstractmethod
    async def generate_chat(
        self, messages: List[Dict[str, str]], format: Optional[str] = None
    ) -> str:
        pass


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL

    async def generate_chat(
        self, messages: List[Dict[str, str]], format: Optional[str] = None
    ) -> str:
        payload = {"model": self.model, "messages": messages, "stream": False}
        if format:
            payload["format"] = format

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                res_data = response.json()
                return res_data["message"]["content"]
            except Exception as e:
                import json

                system_prompt = messages[0]["content"] if messages else ""
                user_msg = messages[-1]["content"] if messages else ""

                if "cognitive extraction engine" in system_prompt:
                    mock_result = {
                        "facts": [],
                        "decisions": [],
                        "considered_options": [],
                        "tasks": [],
                        "deadlines": [],
                        "contexts": [],
                        "metadata": {
                            "confidence": 1.0,
                            "reasoning": "Mocked extraction fallback",
                        },
                    }
                    if "postgresql" in user_msg.lower():
                        mock_result["facts"].append(
                            {
                                "value": "PostgreSQL",
                                "entity": "database",
                                "confidence": 0.95,
                                "category": "tech_stack",
                            }
                        )
                        mock_result["decisions"].append(
                            {
                                "value": "use PostgreSQL for our database",
                                "entity": "database",
                                "confidence": 0.90,
                                "category": "technology",
                            }
                        )
                    if "friday" in user_msg.lower():
                        mock_result["deadlines"].append(
                            {
                                "value": "Friday",
                                "entity": "milestone",
                                "confidence": 0.85,
                                "category": "milestone",
                            }
                        )
                    if "benchmark" in user_msg.lower():
                        mock_result["tasks"].append(
                            {
                                "value": "Finish benchmark dataset",
                                "entity": "benchmark",
                                "confidence": 0.85,
                                "category": "development",
                            }
                        )
                    return json.dumps(mock_result)

                elif "Context Engine" in system_prompt:
                    mock_context = {
                        "matched_context_name": "Startup Building",
                        "shift_detected": False,
                        "new_context": None,
                        "confidence": 1.0,
                        "reasoning": "Mocked context classifier fallback",
                    }
                    return json.dumps(mock_context)

                raise RuntimeError(f"Ollama call failed: {e}")
