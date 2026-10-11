from __future__ import annotations

import asyncio
import json
from dataclasses import replace
from pathlib import Path
from time import perf_counter
from typing import Any, Protocol

from mdi_llm.providers import DeepSeekProvider, PlannerUserConfig

from mdi_api.application.research.transactions import transaction_active
from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.context.policy import ContextOperation, context_budget_policy


PROMPT_VERSION = "research-orchestrator/1.8"


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

    def __init__(self, provider: DeepSeekProvider | None = None, *, turn_id: str | None = None) -> None:
        self.provider = provider or DeepSeekProvider()
        self.turn_id = turn_id

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
        provider = self.provider
        user_config = PlannerUserConfig(provider="deepseek", model=provider.meta.model, timeout_seconds=min(timeout_seconds, 120.0), max_tokens=4096, temperature=0.0)
        turn_id = self.turn_id or request_context.get("turn_id")
        if turn_id:
            from mdi_api.user_models import selection_for_turn, resolve_user_selection
            selection = await asyncio.to_thread(selection_for_turn, str(turn_id))
            if selection:
                provider, user_config = await asyncio.to_thread(resolve_user_selection, selection, timeout_seconds)
        purpose = {
            "scientific_report_composer": "REPORT_COMPOSITION",
            "scientific_literature_synthesizer": "LITERATURE_SYNTHESIS",
        }.get(role, "INTENT_EXTRACTION")
        if role == "scientific_report_composer":
            # A complete cited report has a different output size from a chat
            # answer. Match the report context reservation for every connection.
            user_config = replace(
                user_config,
                max_tokens=context_budget_policy(ContextOperation.REPORT).reserved_output_tokens,
            )
        stream_callback = request_context.get("on_answer_delta") if role == "research_turn_orchestrator" else None
        streaming = {}
        if callable(stream_callback):
            streaming["on_content"] = lambda delta: stream_callback(
                delta, secret_values=(user_config.api_key or "",),
            )
        response = await asyncio.to_thread(
            provider.complete_json,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))},
            ],
            user_config=user_config,
            purpose=purpose,
            **streaming,
        )
        if response.raw_json is None:
            raise ValueError("Provider returned no structured object")
        parsed = response.raw_json
        if role == "research_turn_orchestrator" and isinstance(parsed.get("assistant_message"), str):
            from mdi_api.research_agent.orchestration.answer_stream import public_answer_text
            parsed = {**parsed, "assistant_message": public_answer_text(parsed["assistant_message"], (user_config.api_key or "",))}
        calls = getattr(provider, "call_audit", [])
        audit = calls[-1] if calls else {}
        return StructuredLLMResult(
            provider=user_config.provider,
            model=response.model,
            parsed=parsed,
            provider_request_id=None,
            latency_ms=max(0, round((perf_counter() - started) * 1000)),
            usage=audit.get("tokenUsage") if isinstance(audit, dict) else None,
            repair_attempted=repair,
            prompt_version=str(
                request_context.get("prompt_version") or PROMPT_VERSION
            ),
        )
