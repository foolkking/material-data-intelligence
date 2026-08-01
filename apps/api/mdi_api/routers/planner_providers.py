from __future__ import annotations

import os
import time
from typing import Any, Callable

from pydantic import BaseModel, Field

from mdi_llm import (
    DEEPSEEK_ALLOWED_MODELS,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_DEFAULT_MODEL,
    DeepSeekProvider,
    LLMProviderError,
)


MOCK_PROVIDER_ALIASES = {"mock", "mock_llm", "deterministic", "safe_mock"}


class ProviderResolveRequest(BaseModel):
    provider: str = Field(default="deepseek", max_length=80)
    baseUrl: str | None = Field(default=None, max_length=512)
    model: str | None = Field(default=None, max_length=128)
    secretId: str | None = Field(default=None, max_length=128)
    temperature: float = Field(default=0, ge=0, le=2)
    maxTokens: int = Field(default=8192, ge=1, le=8192)
    timeoutSeconds: float = Field(default=120.0, ge=1, le=120)


class ProviderTestRequest(ProviderResolveRequest):
    pass


def list_planner_providers() -> dict[str, Any]:
    providers = [
        {
            "id": "deepseek",
            "label": "DeepSeek",
            "provider": "deepseek",
            "baseUrl": DEEPSEEK_BASE_URL,
            "defaultModel": DEEPSEEK_DEFAULT_MODEL,
            "allowedModels": sorted(DEEPSEEK_ALLOWED_MODELS),
            "requiresSecret": False,
            "configurationSource": "server_environment",
        }
    ]
    if _test_providers_allowed():
        providers.append(
            {
                "id": "mock",
                "label": "Deterministic test provider",
                "provider": "mock",
                "requiresSecret": False,
                "developerOnly": True,
                "description": "Offline tests and default CI only; never a real LLM call.",
            }
        )
    return {"providers": providers}


def planner_provider_status() -> dict[str, Any]:
    model = os.getenv("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL
    model_allowed = model in DEEPSEEK_ALLOWED_MODELS
    configured = bool(os.getenv("DEEPSEEK_KEY")) and model_allowed
    return {
        "ok": configured,
        "provider": "deepseek",
        "model": model if model_allowed else DEEPSEEK_DEFAULT_MODEL,
        "status": "ready" if configured else "not_configured",
        "configured": configured,
        "configurationSource": "server_environment",
        "allowedModels": sorted(DEEPSEEK_ALLOWED_MODELS),
        "message": "DeepSeek is configured." if configured else (
            "DeepSeek model configuration is not allowed." if not model_allowed else "DeepSeek is not configured."
        ),
        "errorType": None if configured else ("deepseek_model_not_allowed" if not model_allowed else "deepseek_not_configured"),
        "redacted": True,
    }


def resolve_planner_provider_route(request: ProviderResolveRequest) -> dict[str, Any]:
    return resolve_planner_provider(request)


def resolve_planner_provider(
    request: ProviderResolveRequest,
    *,
    secret_resolver: Callable[[str], str | None] | None = None,
) -> dict[str, Any]:
    del secret_resolver
    provider = _normalize_provider(request.provider)
    if provider in MOCK_PROVIDER_ALIASES:
        if not _test_providers_allowed():
            return _provider_status_error(
                provider=provider,
                model="mock",
                error_type="provider_not_allowed",
                error_code="PROVIDER_NOT_ALLOWED",
                message="Test providers require the explicit offline test gate.",
                safe_details="allowedProvider=DEEPSEEK",
            )
        return {
            "ok": True,
            "provider": "mock",
            "model": "mock",
            "status": "ready",
            "willUseLiveProvider": False,
            "secretConfigured": False,
            "source": "developer_test_only",
            "developerOnly": True,
            "message": "Deterministic test provider selected; no external LLM call is possible.",
            "redacted": True,
        }
    if provider != "deepseek":
        return _provider_status_error(
            provider=provider,
            model=request.model or "",
            error_type="provider_not_allowed",
            error_code="PROVIDER_NOT_ALLOWED",
            message="New real LLM calls are restricted to DeepSeek.",
            safe_details="allowedProvider=DEEPSEEK",
        )
    policy_error = _request_policy_error(request)
    if policy_error:
        return policy_error
    status = planner_provider_status()
    return {
        "ok": status["ok"],
        "provider": "deepseek",
        "model": request.model or status["model"],
        "status": status["status"],
        "configured": status["configured"],
        "willUseLiveProvider": status["configured"],
        "secretConfigured": False,
        "source": "server_environment",
        "message": status["message"],
        "errorType": status["errorType"],
        "redacted": True,
    }


def test_planner_provider_route(request: ProviderTestRequest) -> dict[str, Any]:
    return test_planner_provider(request)


def test_planner_provider(
    request: ProviderTestRequest,
    *,
    transport: Any = None,
    secret_resolver: Callable[[str], str | None] | None = None,
) -> dict[str, Any]:
    del secret_resolver
    provider = _normalize_provider(request.provider)
    if provider in MOCK_PROVIDER_ALIASES:
        if not _test_providers_allowed():
            return _provider_error(
                "provider_not_allowed",
                "Test providers require the explicit offline test gate.",
                "allowedProvider=DEEPSEEK",
                ["Select DeepSeek"],
                error_code="PROVIDER_NOT_ALLOWED",
            )
        return {
            "ok": True,
            "provider": "mock",
            "model": "mock",
            "latencyMs": 0,
            "validated": True,
            "message": "Deterministic test provider is ready; no external LLM call was made.",
            "redacted": True,
            "realLlmCalls": 0,
        }
    if provider != "deepseek":
        return _provider_error(
            "provider_not_allowed",
            "New real LLM calls are restricted to DeepSeek.",
            "allowedProvider=DEEPSEEK",
            ["Select DeepSeek"],
            error_code="PROVIDER_NOT_ALLOWED",
        )
    policy_error = _request_policy_error(request)
    if policy_error:
        return policy_error

    llm = DeepSeekProvider(transport=transport)
    started = time.perf_counter()
    try:
        response = llm.complete_json(
            messages=[
                {"role": "system", "content": "Return exactly one JSON object with status equal to ok."},
                {"role": "user", "content": '{"purpose":"provider_connection_test"}'},
            ],
            user_config=_deepseek_user_config(request),
            purpose="PROVIDER_CONNECTION_TEST",
        )
    except LLMProviderError as exc:
        return _provider_exception_error(exc)
    latency_ms = int((time.perf_counter() - started) * 1000)
    if response.raw_json != {"status": "ok"}:
        return _provider_error(
            "provider_response_invalid",
            "DeepSeek response failed the connection-test contract.",
            "response must equal the bounded status object",
            ["Check the allowlisted DeepSeek model"],
        )
    return {
        "ok": True,
        "provider": "deepseek",
        "model": response.model,
        "latencyMs": latency_ms,
        "validated": True,
        "message": "DeepSeek connection succeeded with a strict JSON response.",
        "redacted": True,
        "realLlmCalls": 0 if transport is not None else 1,
    }


def _deepseek_user_config(request: ProviderResolveRequest) -> Any:
    from mdi_llm import PlannerUserConfig

    return PlannerUserConfig(
        provider="deepseek",
        model=request.model or os.getenv("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL,
        timeout_seconds=request.timeoutSeconds,
        temperature=0,
        max_tokens=request.maxTokens,
    )


def _request_policy_error(request: ProviderResolveRequest) -> dict[str, Any] | None:
    if request.baseUrl or request.secretId or request.temperature != 0:
        return _provider_error(
            "deepseek_configuration_not_allowed",
            "DeepSeek endpoint, key source, and temperature are fixed by server policy.",
            "baseUrl/secretId/custom temperature are not accepted",
            ["Remove per-request provider configuration"],
        )
    model = request.model or os.getenv("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL
    if model not in DEEPSEEK_ALLOWED_MODELS:
        return _provider_error(
            "deepseek_model_not_allowed",
            "The requested DeepSeek model is not allowed.",
            "allowedModels=" + ",".join(sorted(DEEPSEEK_ALLOWED_MODELS)),
            ["Select an allowlisted DeepSeek model"],
        )
    return None


def _provider_exception_error(exc: LLMProviderError) -> dict[str, Any]:
    mapping = {
        "DEEPSEEK_NOT_CONFIGURED": ("deepseek_not_configured", "DeepSeek is not configured."),
        "DEEPSEEK_AUTH_FAILED": ("deepseek_auth_failed", "DeepSeek authentication failed."),
        "DEEPSEEK_RATE_LIMITED": ("deepseek_rate_limited", "DeepSeek rate limit was reached."),
        "DEEPSEEK_TIMEOUT": ("deepseek_timeout", "DeepSeek request timed out."),
        "DEEPSEEK_RESPONSE_INVALID": ("deepseek_response_invalid", "DeepSeek returned an invalid strict JSON response."),
    }
    error_type, message = mapping.get(exc.code, ("deepseek_provider_failed", "DeepSeek provider failed."))
    return _provider_error(error_type, message, exc.safe_message, ["Retry DeepSeek after reviewing the typed status"])


def _provider_error(
    error_type: str,
    message: str,
    safe_details: str,
    suggestions: list[str],
    *,
    error_code: str | None = None,
) -> dict[str, Any]:
    payload = {
        "ok": False,
        "errorType": error_type,
        "message": message,
        "safeDetails": safe_details,
        "suggestions": suggestions,
        "redacted": True,
    }
    if error_code is not None:
        payload["code"] = error_code
    return payload


def _provider_status_error(
    *,
    provider: str,
    model: str,
    error_type: str,
    message: str,
    safe_details: str,
    error_code: str | None = None,
) -> dict[str, Any]:
    payload = {
        "ok": False,
        "provider": provider,
        "model": model,
        "status": "not_configured",
        "configured": False,
        "willUseLiveProvider": False,
        "secretConfigured": False,
        "source": "server_environment",
        "message": message,
        "errorType": error_type,
        "safeDetails": safe_details,
        "redacted": True,
    }
    if error_code is not None:
        payload["code"] = error_code
    return payload


def _normalize_provider(provider: str | None) -> str:
    return (provider or "deepseek").strip().lower()


def _test_providers_allowed() -> bool:
    return os.getenv("MDI_ALLOW_TEST_PROVIDERS", "").strip().lower() in {"1", "true", "yes", "on"}
