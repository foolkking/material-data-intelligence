from __future__ import annotations

import asyncio
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Protocol

from mdi_llm.providers import DeepSeekProvider, PlannerUserConfig

from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.unit_of_work import transaction_active


PROMPT_VERSION = "research-orchestrator/1.0"


class StructuredLLMClient(Protocol):
    async def generate_structured(
        self,
        *,
        role: str,
        system_prompt: str,
        input_payload: dict[str, Any],
        output_schema: dict[str, Any],
        timeout_seconds: float,
        request_context: dict[str, Any] | None = None,
    ) -> StructuredLLMResult: ...


def load_research_orchestrator_prompt() -> str:
    path = Path(__file__).resolve().parents[1] / "orchestration" / "prompts" / "research_orchestrator_v1.txt"
    return path.read_text(encoding="utf-8")


class DeepSeekStructuredLLMClient:
    """Adapter over the existing server-managed DeepSeek transport."""

    def __init__(self, provider: DeepSeekProvider | None = None) -> None:
        self.provider = provider or DeepSeekProvider()

    async def generate_structured(
        self,
        *,
        role: str,
        system_prompt: str,
        input_payload: dict[str, Any],
        output_schema: dict[str, Any],
        timeout_seconds: float,
        request_context: dict[str, Any] | None = None,
    ) -> StructuredLLMResult:
        if transaction_active():
            raise RuntimeError("Structured LLM call attempted inside a database transaction")
        request_context = dict(request_context or {})
        repair = bool(request_context.get("repair_attempted"))
        user_payload = {
            "role": role,
            "input": input_payload,
            "output_schema": output_schema,
            "repair": request_context.get("repair"),
        }
        started = perf_counter()
        purpose = "REPORT_COMPOSITION" if role == "scientific_report_composer" else "INTENT_EXTRACTION"
        response = await asyncio.to_thread(
            self.provider.complete_json,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))},
            ],
            user_config=PlannerUserConfig(
                provider="deepseek",
                model=self.provider.meta.model,
                timeout_seconds=min(timeout_seconds, 120.0),
                max_tokens=4096,
                temperature=0.0,
            ),
            purpose=purpose,
        )
        if response.raw_json is None:
            raise ValueError("Provider returned no structured object")
        audit = self.provider.call_audit[-1] if self.provider.call_audit else {}
        return StructuredLLMResult(
            provider="deepseek",
            model=response.model,
            parsed=response.raw_json,
            provider_request_id=None,
            latency_ms=max(0, round((perf_counter() - started) * 1000)),
            usage=audit.get("tokenUsage") if isinstance(audit, dict) else None,
            repair_attempted=repair,
            prompt_version=PROMPT_VERSION,
        )
