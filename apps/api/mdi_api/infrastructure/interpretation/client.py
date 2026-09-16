from __future__ import annotations

import asyncio
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Protocol

from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.unit_of_work import transaction_active
from mdi_llm.providers import DeepSeekProvider, PlannerUserConfig


PROMPT_VERSION = "scientific-interpreter/1.1"


class StructuredInterpreterClient(Protocol):
    async def generate_structured(
        self,
        *,
        input_payload: dict[str, Any],
        output_schema: dict[str, Any],
        timeout_seconds: float,
        request_context: dict[str, Any] | None = None,
    ) -> StructuredLLMResult: ...


def load_interpreter_prompt() -> str:
    return (Path(__file__).resolve().parents[2] / "interpretation" / "prompts" / "scientific_interpreter_v1.txt").read_text(encoding="utf-8")


class DeepSeekInterpreterClient:
    """Adapter over the existing server-managed DeepSeek transport."""

    def __init__(self, provider: DeepSeekProvider | None = None) -> None:
        self.provider = provider or DeepSeekProvider()

    async def generate_structured(self, *, input_payload: dict[str, Any], output_schema: dict[str, Any], timeout_seconds: float, request_context: dict[str, Any] | None = None) -> StructuredLLMResult:
        if transaction_active():
            raise RuntimeError("Interpreter provider call attempted inside a database transaction")
        context = dict(request_context or {})
        started = perf_counter()
        response = await asyncio.to_thread(
            self.provider.complete_json,
            messages=[
                {"role": "system", "content": load_interpreter_prompt()},
                {"role": "user", "content": json.dumps({"input": input_payload, "output_schema": output_schema, "repair": context.get("repair")}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))},
            ],
            user_config=PlannerUserConfig(provider="deepseek", model=self.provider.meta.model, timeout_seconds=min(timeout_seconds, 120.0), max_tokens=4096, temperature=0.0),
            purpose="GROUNDED_INTERPRETATION",
            retry_observer=context.get("retry_observer"),
        )
        if response.raw_json is None:
            raise ValueError("provider returned no structured interpretation")
        audit = self.provider.call_audit[-1] if self.provider.call_audit else {}
        return StructuredLLMResult(
            provider="deepseek",
            model=response.model,
            parsed=response.raw_json,
            latency_ms=max(0, round((perf_counter() - started) * 1000)),
            usage=audit.get("tokenUsage") if isinstance(audit, dict) else None,
            repair_attempted=bool(context.get("repair_attempted")),
            prompt_version=PROMPT_VERSION,
        )


class FakeStructuredInterpreterClient:
    """Deterministic fixture client used by unit and service qualification."""

    def __init__(self, responses: list[dict[str, Any]] | dict[str, Any]):
        self.responses = list(responses) if isinstance(responses, list) else [responses]
        self.calls = 0

    async def generate_structured(self, *, input_payload: dict[str, Any], output_schema: dict[str, Any], timeout_seconds: float, request_context: dict[str, Any] | None = None) -> StructuredLLMResult:
        if transaction_active():
            raise AssertionError("fake interpreter called inside an open transaction")
        response = self.responses[min(self.calls, len(self.responses) - 1)]
        self.calls += 1
        return StructuredLLMResult(provider="fake", model="fixture", parsed=response, latency_ms=0, repair_attempted=bool((request_context or {}).get("repair_attempted")), prompt_version=PROMPT_VERSION)


__all__ = ["DeepSeekInterpreterClient", "FakeStructuredInterpreterClient", "PROMPT_VERSION", "StructuredInterpreterClient", "load_interpreter_prompt"]
