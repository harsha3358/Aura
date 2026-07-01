import pytest
from app.extraction.service import ExtractionService
from app.services.llm import LLMProvider


class MockLLMProvider(LLMProvider):
    def __init__(self, response_text: str):
        self.response_text = response_text
        self.last_messages = None

    async def generate_chat(self, messages, format=None):
        self.last_messages = messages
        return self.response_text


@pytest.mark.anyio
async def test_extraction_validation_layer():
    raw_json = """{
      "facts": [{"value": "AURA", "entity": "project", "confidence": 1.0, "category": "project_detail"}],
      "decisions": [],
      "considered_options": [],
      "tasks": [],
      "deadlines": [],
      "contexts": [],
      "metadata": {"confidence": 1.0, "reasoning": "Test reasoning"}
    }"""
    mock_llm = MockLLMProvider(raw_json)
    service = ExtractionService(llm_provider=mock_llm)
    res, obs = await service.extract_from_message("Test message")

    assert len(res.facts) == 1
    assert res.facts[0].value == "AURA"
    assert res.facts[0].confidence == 1.0
    assert len(obs) == 0


@pytest.mark.anyio
async def test_extraction_reject_missing_confidence():
    raw_json = """{
      "facts": [{"value": "AURA", "entity": "project", "category": "project_detail"}],
      "decisions": [],
      "considered_options": [],
      "tasks": [],
      "deadlines": [],
      "contexts": [],
      "metadata": {"confidence": 1.0, "reasoning": "Test reasoning"}
    }"""
    mock_llm = MockLLMProvider(raw_json)
    service = ExtractionService(llm_provider=mock_llm)
    res, obs = await service.extract_from_message("Test message")

    assert len(res.facts) == 0
    assert len(obs) == 0


@pytest.mark.anyio
async def test_extraction_reject_invalid_category():
    raw_json = """{
      "facts": [{"value": "AURA", "entity": "project", "confidence": 0.9, "category": "invalid_category"}],
      "decisions": [],
      "considered_options": [],
      "tasks": [],
      "deadlines": [],
      "contexts": [],
      "metadata": {"confidence": 1.0, "reasoning": "Test reasoning"}
    }"""
    mock_llm = MockLLMProvider(raw_json)
    service = ExtractionService(llm_provider=mock_llm)
    res, obs = await service.extract_from_message("Test message")

    assert len(res.facts) == 0
    assert len(obs) == 0


@pytest.mark.anyio
async def test_extraction_demote_sub_threshold():
    raw_json = """{
      "facts": [{"value": "AURA", "entity": "project", "confidence": 0.5, "category": "project_detail"}],
      "decisions": [],
      "considered_options": [],
      "tasks": [],
      "deadlines": [],
      "contexts": [],
      "metadata": {"confidence": 1.0, "reasoning": "Test reasoning"}
    }"""
    mock_llm = MockLLMProvider(raw_json)
    service = ExtractionService(llm_provider=mock_llm)
    res, obs = await service.extract_from_message("Test message")

    assert len(res.facts) == 0
    assert len(obs) == 1
    assert obs[0]["raw_type"] == "FactItem"
    assert obs[0]["confidence"] == 0.5
