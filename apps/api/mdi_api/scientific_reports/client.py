from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.llm.structured_client import DeepSeekStructuredLLMClient, StructuredLLMClient


class StructuredReportComposerClient(Protocol):
    async def generate_structured(
        self,
        *,
        input_payload: dict[str, Any],
        output_schema: dict[str, Any],
        timeout_seconds: float,
        request_context: dict[str, Any] | None = None,
    ) -> StructuredLLMResult: ...


def load_report_composer_prompt() -> str:
    return (Path(__file__).resolve().parent / "prompts" / "scientific_report_composer_v2.txt").read_text(encoding="utf-8")


class DeepSeekReportComposerClient:
    """Report-specific adapter over the existing structured LLM transport."""

    def __init__(self, client: StructuredLLMClient | None = None) -> None:
        self.client = client or DeepSeekStructuredLLMClient()

    async def generate_structured(
        self,
        *,
        input_payload: dict[str, Any],
        output_schema: dict[str, Any],
        timeout_seconds: float,
        request_context: dict[str, Any] | None = None,
    ) -> StructuredLLMResult:
        return await self.client.generate_structured(
            role="scientific_report_composer",
            system_prompt=load_report_composer_prompt(),
            input_payload=input_payload,
            output_schema=output_schema,
            timeout_seconds=timeout_seconds,
            request_context=request_context,
        )


class FakeStructuredReportComposerClient:
    def __init__(self, responses: list[dict[str, Any]] | dict[str, Any]) -> None:
        self.responses = list(responses) if isinstance(responses, list) else [responses]
        self.calls = 0

    async def generate_structured(
        self,
        *,
        input_payload: dict[str, Any],
        output_schema: dict[str, Any],
        timeout_seconds: float,
        request_context: dict[str, Any] | None = None,
    ) -> StructuredLLMResult:
        response = self.responses[min(self.calls, len(self.responses) - 1)]
        self.calls += 1
        return StructuredLLMResult(
            provider="fake",
            model="report-fixture",
            parsed=response,
            latency_ms=0,
            repair_attempted=bool((request_context or {}).get("repair_attempted")),
            prompt_version="scientific-report-composer/2.0",
        )


__all__ = [
    "DeepSeekReportComposerClient",
    "FakeStructuredReportComposerClient",
    "StructuredReportComposerClient",
    "load_report_composer_prompt",
]
