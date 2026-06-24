import os
import sys
import json
import asyncio
import argparse
from typing import List, Dict, Any, Optional

# Ensure apps/api is in PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "apps", "api"))

from app.extraction.service import ExtractionService
from app.extraction.context import ContextClassifier
from app.extraction.schemas import ExtractionResult
from app.services.llm import LLMProvider

class MockEvaluationLLM(LLMProvider):
    """
    Simulates Ollama by returning the expected JSON structure directly,
    optionally adding some noise (e.g., lower confidence or extra items)
    to test the validation and metric calculations.
    """
    def __init__(self, expected_json_str: str, inject_pollution: bool = False):
        self.expected_json_str = expected_json_str
        self.inject_pollution = inject_pollution

    async def generate_chat(self, messages: List[Dict[str, str]], format: Optional[str] = None) -> str:
        if not self.inject_pollution:
            data = json.loads(self.expected_json_str)
            data["metadata"] = {"confidence": 1.0, "reasoning": "Mocked correct output"}
            return json.dumps(data)
        else:
            data = json.loads(self.expected_json_str)
            data["metadata"] = {"confidence": 0.8, "reasoning": "Mocked polluted output"}
            if "facts" in data and len(data["facts"]) > 0:
                data["facts"].append({"value": "Pollution Fact", "entity": "polluted", "category": "project_detail"})
            if "tasks" in data:
                data["tasks"].append({"value": "Sub-threshold Task", "confidence": 0.4, "category": "development"})
            return json.dumps(data)

class MockContextLLM(LLMProvider):
    """
    Simulates Ollama context classifier responses.
    """
    def __init__(self, expected_context: str, inject_pollution: bool = False):
        self.expected_context = expected_context
        self.inject_pollution = inject_pollution

    async def generate_chat(self, messages: List[Dict[str, str]], format: Optional[str] = None) -> str:
        if not self.inject_pollution:
            # Matches existing context
            return json.dumps({
                "matched_context_name": self.expected_context,
                "shift_detected": False,
                "new_context": None,
                "confidence": 1.0,
                "reasoning": "Mocked correct context classification"
            })
        else:
            # Low confidence shift to incorrect context
            return json.dumps({
                "matched_context_name": None,
                "shift_detected": True,
                "new_context": {
                    "name": "Incorrect Context",
                    "description": "Simulated wrong context"
                },
                "confidence": 0.4,
                "reasoning": "Mocked polluted context classification"
            })

def normalize(val: str) -> str:
    return str(val).lower().strip()

def evaluate_run(expected: Dict[str, Any], actual: ExtractionResult) -> Dict[str, Any]:
    categories = ["facts", "decisions", "considered_options", "tasks", "deadlines", "contexts"]
    stats = {}
    
    total_tp = 0
    total_fp = 0
    total_fn = 0
    
    for cat in categories:
        exp_list = expected.get(cat, [])
        exp_vals = {normalize(item["value"]) for item in exp_list}
        
        act_list = getattr(actual, cat, [])
        act_vals = {normalize(item.value) for item in act_list}
        
        tp = len(exp_vals.intersection(act_vals))
        fp = len(act_vals - exp_vals)
        fn = len(exp_vals - act_vals)
        
        total_tp += tp
        total_fp += fp
        total_fn += fn
        
        stats[cat] = {"tp": tp, "fp": fp, "fn": fn}
        
    return {
        "categories": stats,
        "total_tp": total_tp,
        "total_fp": total_fp,
        "total_fn": total_fn
    }

async def main():
    parser = argparse.ArgumentParser(description="Evaluate Aura Knowledge Extraction Engine")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode using benchmark expectations")
    parser.add_argument("--pollute", action="store_true", help="Inject pollution/noise in mock mode to test metrics")
    parser.add_argument("--threshold", type=float, default=0.7, help="Confidence threshold for validation")
    args = parser.parse_args()

    benchmark_path = os.path.join(os.path.dirname(__file__), "..", "benchmark", "v0.1", "examples.jsonl")
    if not os.path.exists(benchmark_path):
        print(f"Error: Benchmark file not found at {benchmark_path}")
        sys.exit(1)

    print(f"Loading benchmark from {benchmark_path}...")
    examples = []
    with open(benchmark_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))

    print(f"Loaded {len(examples)} examples.")
    
    global_tp = 0
    global_fp = 0
    global_fn = 0
    
    context_matches = 0
    total_context_runs = 0
    
    service = ExtractionService(confidence_threshold=args.threshold)
    classifier = ContextClassifier()
    
    for i, ex in enumerate(examples):
        message = ex["message"]
        expected = ex["expected"]
        expected_context = ex.get("expected_context")
        
        if args.mock:
            mock_llm = MockEvaluationLLM(json.dumps(expected), inject_pollution=args.pollute)
            service.llm = mock_llm
            
            mock_ctx_llm = MockContextLLM(expected_context, inject_pollution=args.pollute)
            classifier.llm = mock_ctx_llm
            
        try:
            # 1. Evaluate context classification
            from app.models.core import Context
            mock_existing = []
            if expected_context:
                mock_existing.append(Context(name=expected_context, description="Mock context"))
            
            ctx_res = await classifier.classify(message, mock_existing)
            matched_ctx = ctx_res.get("matched_context_name")
            
            if matched_ctx and expected_context and matched_ctx.lower().strip() == expected_context.lower().strip():
                context_matches += 1
            elif ctx_res.get("shift_detected") and ctx_res.get("new_context") and ctx_res["new_context"].get("name"):
                new_name = ctx_res["new_context"]["name"]
                if expected_context and new_name.lower().strip() == expected_context.lower().strip():
                    context_matches += 1
            total_context_runs += 1

            # 2. Evaluate extraction
            actual, observations = await service.extract_from_message(message)
            run_stats = evaluate_run(expected, actual)
            global_tp += run_stats["total_tp"]
            global_fp += run_stats["total_fp"]
            global_fn += run_stats["total_fn"]
        except Exception as e:
            print(f"Error executing example {i+1}: {e}")
            global_fn += sum(len(expected.get(c, [])) for c in expected)

    precision = global_tp / (global_tp + global_fp) if (global_tp + global_fp) > 0 else 0.0
    recall = global_tp / (global_tp + global_fn) if (global_tp + global_fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    pollution_rate = global_fp / (global_tp + global_fp) if (global_tp + global_fp) > 0 else 0.0
    context_accuracy = context_matches / total_context_runs if total_context_runs > 0 else 0.0

    print("\n" + "="*40)
    print("           EVALUATION SUMMARY")
    print("="*40)
    print(f"Mode: {'MOCK' if args.mock else 'LIVE'}")
    print(f"Total True Positives (TP):  {global_tp}")
    print(f"Total False Positives (FP): {global_fp}")
    print(f"Total False Negatives (FN): {global_fn}")
    print(f"Context Matches:            {context_matches}/{total_context_runs}")
    print("-"*40)
    print(f"Precision:                 {precision:.4f}")
    print(f"Recall:                    {recall:.4f}")
    print(f"F1 Score:                  {f1:.4f}")
    print(f"Knowledge Pollution Rate:  {pollution_rate:.4f}")
    print(f"Context Detection Accuracy: {context_accuracy:.4f}")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(main())
