from __future__ import annotations

import os
import time
from typing import Any, Callable

from pydantic import BaseModel, Field

from mdi_llm import LLMProviderError, MockLLMProvider, OpenAICompatibleProvider, PlannerRequest, PlannerUserConfig
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan

from .secrets import get_secret_value, mark_secret_used


MOCK_PROVIDER_ALIASES = {"mock", "mock_llm", "deterministic", "safe_mock", ""}


class ProviderResolveRequest(BaseModel):
    provider: str = Field(default="mock", max_length=80)
    baseUrl: str | None = None
    model: str | None = None
    secretId: str | None = None
    temperature: float = 0.1
    maxTokens: int = 1024
    timeoutSeconds: float = 60.0


class ProviderTestRequest(ProviderResolveRequest):
    pass


def list_planner_providers() -> dict[str, Any]:
    return {
        "providers": [
            {
                "id": "mock",
                "label": "Mock Planner",
                "provider": "mock",
                "requiresSecret": False,
                "description": "Local deterministic planner used by default tests and demos.",
            },
            {
                "id": "openai",
                "label": "OpenAI",
                "provider": "openai_compatible",
                "baseUrl": "https://api.openai.com/v1",
                "defaultModel": "gpt-4o",
                "requiresSecret": True,
            },
            {
                "id": "deepseek",
                "label": "DeepSeek",
                "provider": "openai_compatible",
                "baseUrl": "https://api.deepseek.com/v1",
                "defaultModel": "deepseek-chat",
                "requiresSecret": True,
            },
            {
                "id": "custom",
                "label": "Custom OpenAI-compatible",
                "provider": "openai_compatible",
                "baseUrl": "",
                "defaultModel": "",
                "requiresSecret": True,
            },
        ]
    }


def planner_provider_status() -> dict[str, Any]:
    provider = _normalize_provider(os.getenv("MDI_LLM_PROVIDER") or "mock")
    if provider in MOCK_PROVIDER_ALIASES:
        return {
            "ok": True,
            "provider": "mock",
            "model": "mock",
            "status": "ready",
            "message": "Default provider is Mock Planner. No external LLM will be called by default.",
            "redacted": True,
        }
    configured = provider == "openai_compatible" and bool(os.getenv("MDI_LLM_API_KEY") or os.getenv("OPENAI_API_KEY"))
    return {
        "ok": configured,
        "provider": provider,
        "model": os.getenv("MDI_LLM_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o",
        "status": "ready" if configured else "not_configured",
        "message": "Default OpenAI-compatible provider is configured." if configured else "Default OpenAI-compatible provider needs an API key.",
        "redacted": True,
    }


def resolve_planner_provider_route(request: ProviderResolveRequest) -> dict[str, Any]:
    return resolve_planner_provider(request)


def resolve_planner_provider(
    request: ProviderResolveRequest,
    *,
    secret_resolver: Callable[[str], str | None] = get_secret_value,
) -> dict[str, Any]:
    provider = _normalize_provider(request.provider)
    if provider in MOCK_PROVIDER_ALIASES:
        return {
            "ok": True,
            "provider": "mock",
            "model": "mock",
            "status": "ready",
            "willUseLiveProvider": False,
            "secretConfigured": False,
            "source": "request",
            "message": "Current planner job configuration will use Mock Planner.",
            "redacted": True,
        }

    if provider != "openai_compatible":
        return _provider_status_error(
            provider=provider,
            model=request.model or "",
            error_type="provider_not_supported",
            message="Current planner job configuration uses an unsupported provider.",
            safe_details=f"provider={provider}",
        )

    secret_id = request.secretId or ""
    has_secret = bool(secret_id and secret_resolver(secret_id))
    has_env_key = bool(os.getenv("MDI_LLM_API_KEY") or os.getenv("OPENAI_API_KEY"))
    configured = has_secret or has_env_key
    model = request.model or os.getenv("MDI_LLM_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o"
    source = "secret" if has_secret else "env" if has_env_key else "missing_secret"
    return {
        "ok": configured,
        "provider": "openai_compatible",
        "model": model,
        "status": "ready" if configured else "not_configured",
        "willUseLiveProvider": configured,
        "secretConfigured": has_secret,
        "source": source,
        "message": (
            "Current planner job configuration will use an OpenAI-compatible LLM."
            if configured
            else "Current planner job configuration needs a saved API key before it can use a live LLM."
        ),
        "safeDetails": None if configured else "secretId is missing or was not found, and no env API key is configured.",
        "redacted": True,
    }


def test_planner_provider_route(request: ProviderTestRequest) -> dict[str, Any]:
    return test_planner_provider(request)


def test_planner_provider(
    request: ProviderTestRequest,
    *,
    transport: Any = None,
    secret_resolver: Callable[[str], str | None] = get_secret_value,
) -> dict[str, Any]:
    provider = _normalize_provider(request.provider)
    registry = load_manifests()
    tools = [tool for tool in registry.tools if tool.stage == "mvp"]
    planner_request = PlannerRequest(
        user_prompt="Create one safe ml.basic_metrics AnalysisPlan for y_true and y_pred.",
        dataset_id="dataset_demo",
        profile_id="profile_demo",
        tool_registry_version=registry.version,
    )
    data_profile = DataProfile(
        profileId="profile_demo",
        datasetId="dataset_demo",
        version="0.1",
        datasetType="ml",
        createdAt="2026-07-04T00:00:00+00:00",
    )

    try:
        if provider in MOCK_PROVIDER_ALIASES:
            llm = MockLLMProvider()
            user_config = None
        elif provider == "openai_compatible":
            secret_id = request.secretId or ""
            api_key = secret_resolver(secret_id) if secret_id else None
            if not api_key:
                return _provider_error(
                    "provider_not_configured",
                    "Live LLM is not configured. Save and select an API key first.",
                    "secretId is missing or was not found",
                    ["Save an API key", "Select a saved secret", "Switch to Mock Planner"],
                )
            mark_secret_used(secret_id)
            llm = OpenAICompatibleProvider(transport=transport)
            user_config = PlannerUserConfig(
                provider="openai_compatible",
                model=request.model or "gpt-4o",
                base_url=request.baseUrl,
                api_key=api_key,
                timeout_seconds=request.timeoutSeconds,
                temperature=request.temperature,
                max_tokens=request.maxTokens,
            )
        else:
            return _provider_error(
                "provider_not_supported",
                "This planner provider is not supported.",
                f"provider={provider}",
                ["Select Mock Planner", "Select OpenAI-compatible LLM"],
            )

        started = time.perf_counter()
        response = llm.generate_plan(planner_request, tools=tools, data_profile=data_profile, user_config=user_config)
        latency_ms = int((time.perf_counter() - started) * 1000)
    except LLMProviderError as exc:
        return _provider_exception_error(exc)

    if response.raw_json is None:
        return _provider_error(
            "provider_response_invalid",
            "Provider response was not valid AnalysisPlan JSON.",
            "Provider response could not be parsed as an AnalysisPlan JSON object.",
            ["Lower temperature", "Check whether the model supports JSON output", "Switch to Mock Planner to verify the workflow"],
        )

    validation = validate_plan(response.raw_json, registry=registry)
    if not validation.ok:
        return _provider_error(
            "plan_validation_failed",
            "Provider returned a plan that did not pass validation.",
            "; ".join(f"{error.code}: {error.message}" for error in validation.errors),
            ["Adjust the prompt", "Check that selected tools are MVP Tool Registry tools", "Switch to Mock Planner to verify the workflow"],
        )

    return {
        "ok": True,
        "provider": provider,
        "model": response.model,
        "latencyMs": latency_ms,
        "validated": True,
        "message": "Provider connection succeeded and returned a valid AnalysisPlan.",
        "redacted": True,
    }


def _provider_exception_error(exc: LLMProviderError) -> dict[str, Any]:
    if exc.status_code == 401:
        error_type = "provider_auth_failed"
        message = "Provider authentication failed. Check the API key."
    elif exc.status_code == 429:
        error_type = "provider_rate_limited"
        message = "Provider rate limit was reached. Try again later."
    elif exc.code == "LLM_TIMEOUT":
        error_type = "provider_timeout"
        message = "Provider request timed out. Check the network or base URL."
    elif exc.code == "LLM_API_KEY_MISSING":
        error_type = "provider_not_configured"
        message = "Live LLM is not configured. Save and select an API key first."
    else:
        error_type = "provider_error"
        message = "Provider connection failed. Check the configuration."
    return _provider_error(error_type, message, exc.safe_message, ["Check base URL", "Check model name", "Switch to Mock Planner"])


def _provider_error(error_type: str, message: str, safe_details: str, suggestions: list[str]) -> dict[str, Any]:
    return {
        "ok": False,
        "errorType": error_type,
        "message": message,
        "safeDetails": safe_details,
        "suggestions": suggestions,
        "redacted": True,
    }


def _provider_status_error(*, provider: str, model: str, error_type: str, message: str, safe_details: str) -> dict[str, Any]:
    return {
        "ok": False,
        "provider": provider,
        "model": model,
        "status": "not_configured",
        "willUseLiveProvider": False,
        "secretConfigured": False,
        "source": "request",
        "message": message,
        "errorType": error_type,
        "safeDetails": safe_details,
        "redacted": True,
    }


def _normalize_provider(provider: str | None) -> str:
    return (provider or "mock").strip().lower()
