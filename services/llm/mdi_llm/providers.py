"""LLM provider abstraction and implementations for Phase 7.

All providers conform to the LLMPlannerProvider protocol.  No real API key
is read at import time; keys are resolved at call time from environment
variables or injected configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import socket
from typing import Any, Protocol
import urllib.error
import urllib.request

from mdi_schemas import AnalysisPlan, DataProfile, RegisteredTool

from .redaction import redact_credential_values


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
    timeout_seconds: float = 30.0
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


class LLMProviderError(RuntimeError):
    """Safe provider error whose text is suitable for API responses."""

    def __init__(self, message: str, *, code: str = "LLM_PROVIDER_ERROR", status_code: int | None = None) -> None:
        safe_message = redact_credential_values(message)
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
        self.status_code = status_code


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
    """OpenAI-compatible provider for gated Phase 9A planner integration.

    Configuration is resolved at call time. MDI_LLM_* environment variables
    are preferred; OPENAI_* fallbacks are accepted for compatibility. The
    default test path still uses MockLLMProvider, so this class contacts the
    network only when explicitly selected and no fake transport is injected.
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
        config = user_config or PlannerUserConfig()
        resolved = _resolve_openai_config(config)

        from .planner_prompt import build_planner_prompt
        system_prompt, user_prompt_str = build_planner_prompt(request, tools=tools, data_profile=data_profile)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt_str},
        ]

        if self._transport is not None:
            response = _call_fake_transport(
                self._transport,
                model=resolved["model"],
                messages=messages,
                temperature=resolved["temperature"],
                max_tokens=resolved["max_tokens"],
                timeout_seconds=resolved["timeout_seconds"],
                response_format={"type": "json_object"},
            )
        else:
            api_key = resolved["api_key"]
            if not api_key:
                raise LLMProviderError(
                    "OpenAI-compatible LLM provider is not configured: missing API key.",
                    code="LLM_API_KEY_MISSING",
                )
            response = _post_chat_completion(
                base_url=resolved["base_url"],
                api_key=api_key,
                model=resolved["model"],
                messages=messages,
                temperature=resolved["temperature"],
                max_tokens=resolved["max_tokens"],
                timeout_seconds=resolved["timeout_seconds"],
            )

        choice = _first_choice(response)
        content = _choice_content(choice)
        parsed = _parse_llm_json(content) if isinstance(content, str) else content
        return PlannerRawResponse(
            raw_json=parsed,
            raw_text=content if isinstance(content, str) else json.dumps(content),
            model=str(resolved["model"]),
            finish_reason=choice.get("finish_reason"),
        )

    @property
    def meta(self) -> _ProviderMeta:
        return _ProviderMeta(
            name="openai_compatible",
            model=os.environ.get("MDI_LLM_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-4o",
        )


def _resolve_openai_config(config: PlannerUserConfig) -> dict[str, Any]:
    return {
        "api_key": config.api_key or os.environ.get("MDI_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY"),
        "base_url": (config.base_url or os.environ.get("MDI_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/"),
        "model": os.environ.get("MDI_LLM_MODEL") or os.environ.get("OPENAI_MODEL") or config.model or "gpt-4o",
        "timeout_seconds": _env_float("MDI_LLM_TIMEOUT_SECONDS", config.timeout_seconds),
        "max_tokens": _env_int("MDI_LLM_MAX_TOKENS", config.max_tokens),
        "temperature": _env_float("MDI_LLM_TEMPERATURE", config.temperature),
    }


def _env_float(name: str, default: float) -> float:
    value = os.environ.get(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _call_fake_transport(
    transport: Any,
    *,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    timeout_seconds: float,
    response_format: dict[str, str],
) -> dict[str, Any]:
    import inspect

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout_seconds": timeout_seconds,
        "response_format": response_format,
    }
    try:
        signature = inspect.signature(transport)
        accepted = {name: value for name, value in kwargs.items() if name in signature.parameters}
        if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values()):
            accepted = kwargs
        return transport(**accepted)
    except LLMProviderError:
        raise
    except (TimeoutError, socket.timeout) as exc:
        raise LLMProviderError("OpenAI-compatible LLM request timed out.", code="LLM_TIMEOUT") from None
    except urllib.error.HTTPError as exc:
        raise _http_error(exc) from None
    except urllib.error.URLError as exc:
        raise LLMProviderError("OpenAI-compatible LLM request failed before a response was received.", code="LLM_NETWORK_ERROR") from None
    except Exception as exc:
        raise LLMProviderError("OpenAI-compatible LLM request failed.", code="LLM_PROVIDER_ERROR") from None


def _post_chat_completion(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    timeout_seconds: float,
) -> dict[str, Any]:
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
    ).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (TimeoutError, socket.timeout) as exc:
        raise LLMProviderError("OpenAI-compatible LLM request timed out.", code="LLM_TIMEOUT") from None
    except urllib.error.HTTPError as exc:
        raise _http_error(exc) from None
    except urllib.error.URLError as exc:
        raise LLMProviderError("OpenAI-compatible LLM request failed before a response was received.", code="LLM_NETWORK_ERROR") from None
    except ValueError as exc:
        raise LLMProviderError("OpenAI-compatible LLM response was not valid JSON.", code="LLM_RESPONSE_INVALID") from None


def _http_error(exc: urllib.error.HTTPError) -> LLMProviderError:
    code = int(getattr(exc, "code", 0) or 0)
    if code == 401:
        message = "OpenAI-compatible LLM request was rejected with status 401."
    elif code == 429:
        message = "OpenAI-compatible LLM request was rate limited with status 429."
    elif code >= 500:
        message = f"OpenAI-compatible LLM provider returned status {code}."
    else:
        message = f"OpenAI-compatible LLM request failed with status {code}."
    return LLMProviderError(message, code="LLM_HTTP_ERROR", status_code=code or None)


def _first_choice(response: dict[str, Any]) -> dict[str, Any]:
    try:
        choice = response["choices"][0]
    except Exception as exc:
        raise LLMProviderError(
            "OpenAI-compatible LLM response did not include a completion choice.",
            code="LLM_RESPONSE_INVALID",
        ) from None
    if not isinstance(choice, dict):
        raise LLMProviderError(
            "OpenAI-compatible LLM response choice was not a JSON object.",
            code="LLM_RESPONSE_INVALID",
        )
    return choice


def _choice_content(choice: dict[str, Any]) -> Any:
    try:
        return choice["message"]["content"]
    except Exception as exc:
        raise LLMProviderError(
            "OpenAI-compatible LLM response did not include message content.",
            code="LLM_RESPONSE_INVALID",
        ) from None


def _parse_llm_json(content: str) -> dict[str, Any] | None:
    """Parse an LLM completion into a JSON object.

    Handles two non-ideal cases gracefully (returns None rather than raising):
      1. Plain non-JSON text (e.g. an apology or explanation).
      2. Markdown-fenced JSON (```json ... ``` or ``` ... ```).

    Returning None lets the planner layer + PlanValidator reject the output
    with a structured error instead of an unhandled exception.
    """
    import json as _json
    import re as _re

    if not isinstance(content, str):
        return None

    text = content.strip()

    # Strip markdown code fences if present.
    fence = _re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, _re.DOTALL)
    if fence:
        text = fence.group(1).strip()

    try:
        result = _json.loads(text)
    except (ValueError, TypeError):
        return None

    return result if isinstance(result, dict) else None


def _mock_basic_metrics_plan(request: PlannerRequest, tools: list[RegisteredTool]) -> dict[str, Any]:
    """Generate a minimal valid plan with a single ml.basic_metrics step.

    The step references the conventional ``ml_table`` normalized object so the
    plan is executable end-to-end through the runtime + Tool Registry + Adapter.
    """
    step = {
        "stepId": "step_001",
        "toolId": "ml.basic_metrics",
        "purpose": "Compute regression metrics",
        "reason": "User requested basic regression evaluation",
        "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
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
