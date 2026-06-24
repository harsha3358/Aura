import httpx
from typing import Optional, List, Dict
from abc import ABC, abstractmethod
from app.config import get_settings

settings = get_settings()

class LLMProvider(ABC):
    @abstractmethod
    async def generate_chat(self, messages: List[Dict[str, str]], format: Optional[str] = None) -> str:
        pass

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL

    async def generate_chat(self, messages: List[Dict[str, str]], format: Optional[str] = None) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        if format:
            payload["format"] = format
            
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                res_data = response.json()
                return res_data["message"]["content"]
            except Exception as e:
                raise RuntimeError(f"Ollama call failed: {e}")
