"""LLM provider abstraction and implementations for Phase 7.

All providers conform to the LLMPlannerProvider protocol.  No real API key
is read at import time; keys are resolved at call time from environment
variables or injected configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from mdi_schemas import AnalysisPlan, DataProfile, RegisteredTool


@dataclass(frozen=True)
class PlannerRequest:
    user_prompt: str
    dataset_id: str
    profile_id: str
    tool_registry_version: str


@dataclass(frozen=True)
class PlannerUserConfig:
    provider: str = "openai_compatible"
    model: str = "gpt-4o"
    base_url: str | None = None
    api_key: str | None = None
    temperature: float = 0.2
    max_tokens: int = 4096


@dataclass
class PlannerRawResponse:
    raw_json: dict[str, Any] | None
    raw_text: str | None
    model: str
    finish_reason: str | None


class LLMPlannerProvider(Protocol):
    """Protocol for LLM-backed AnalysisPlan generators."""

    def generate_plan(
        self,
        request: PlannerRequest,
        *,
        tools: list[RegisteredTool],
        data_profile: DataProfile,
        user_config: PlannerUserConfig | None = None,
    ) -> PlannerRawResponse:
        ...


@dataclass
class _ProviderMeta:
    name: str
    model: str


@dataclass
class MockLLMProvider:
    """Returns a pre-defined AnalysisPlan dict for deterministic testing.

    This provider never contacts a network and does not require any API key.
    """

    fixed_plan: dict[str, Any] | None = None

    def generate_plan(
        self,
        request: PlannerRequest,
        *,
        tools: list[RegisteredTool],
        data_profile: DataProfile,
        user_config: PlannerUserConfig | None = None,
    ) -> PlannerRawResponse:
        if self.fixed_plan is not None:
            plan = dict(self.fixed_plan)
        else:
            plan = _mock_basic_metrics_plan(request, tools)
        return PlannerRawResponse(
            raw_json=plan,
            raw_text=None,
            model="mock",
            finish_reason="stop",
        )

    @property
    def meta(self) -> _ProviderMeta:
        return _ProviderMeta(name="mock", model="mock")


class OpenAICompatibleProvider:
    """OpenAI / DeepSeek compatible provider.

    API key resolution order:  user_config.api_key
                            -> os.environ['OPENAI_API_KEY']
    Base URL resolution order:  user_config.base_url
                             -> os.environ['OPENAI_BASE_URL']
    Model resolution order:     user_config.model
                             -> os.environ.get('OPENAI_MODEL', 'gpt-4o')
    """

    def __init__(self, *, transport: Any = None) -> None:
        self._transport = transport

    def generate_plan(
        self,
        request: PlannerRequest,
        *,
        tools: list[RegisteredTool],
        data_profile: DataProfile,
        user_config: PlannerUserConfig | None = None,
    ) -> PlannerRawResponse:
        import json as _json
        import os

        config = user_config or PlannerUserConfig()

        api_key = config.api_key or os.environ.get("OPENAI_API_KEY")
        base_url = config.base_url or os.environ.get("OPENAI_BASE_URL") or None
        model = config.model or os.environ.get("OPENAI_MODEL", "gpt-4o")

        from .planner_prompt import build_planner_prompt
        system_prompt, user_prompt_str = build_planner_prompt(request, tools=tools, data_profile=data_profile)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt_str},
        ]

        if self._transport is not None:
            response = self._transport(
                model=model,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
        else:
            import urllib.request

            url = f"{base_url or 'https://api.openai.com/v1'}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            body = _json.dumps(
                {
                    "model": model,
                    "messages": messages,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    "response_format": {"type": "json_object"},
                }
            ).encode("utf-8")

            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req) as resp:
                response = _json.loads(resp.read().decode("utf-8"))

        choice = response["choices"][0]
        content = choice["message"]["content"]
        parsed = _json.loads(content) if isinstance(content, str) else content
        return PlannerRawResponse(
            raw_json=parsed,
            raw_text=content if isinstance(content, str) else _json.dumps(content),
            model=model,
            finish_reason=choice.get("finish_reason"),
        )

    @property
    def meta(self) -> _ProviderMeta:
        import os
        return _ProviderMeta(
            name="openai_compatible",
            model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
        )


def _mock_basic_metrics_plan(request: PlannerRequest, tools: list[RegisteredTool]) -> dict[str, Any]:
    """Generate a minimal valid plan with a single ml.basic_metrics step."""
    import os as _os
    step = {
        "stepId": "step_001",
        "toolId": "ml.basic_metrics",
        "purpose": "Compute regression metrics",
        "reason": "User requested basic regression evaluation",
        "inputRefs": [],
        "params": {"targetColumn": "y_true", "predictionColumn": "y_pred"},
        "output": {"artifactTypes": ["metrics_json"]},
    }
    return {
        "schemaVersion": "0.1",
        "goal": request.user_prompt,
        "datasetId": request.dataset_id,
        "profileId": request.profile_id,
        "toolRegistryVersion": request.tool_registry_version,
        "assumptions": ["Generated by MockLLMProvider for testing."],
        "warnings": [],
        "steps": [step],
        "expectedArtifacts": [{"name": "metrics.json", "type": "metrics_json", "fromStepId": "step_001"}],
    }
