from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, Field
from fastapi import Depends
from mdi_api.routers.auth import (
    CurrentUser,
    get_current_user,
    get_current_user_compat,
    require_platform_admin,
)

from mdi_llm import (
    DEEPSEEK_ALLOWED_MODELS,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_DEFAULT_MODEL,
    DEEPSEEK_PROVIDER_NAME,
    DeepSeekProvider,
    LLMProviderError,
)
from mdi_api.provider_connections import (
    ProviderConnectionConfigurationError,
    decrypt_api_key,
    delete_connection,
    get_connection,
    list_connections,
    public_connection,
    save_connection,
    update_connection_models,
    thinking_modes,
)


MOCK_PROVIDER_ALIASES = {"mock", "mock_llm", "deterministic", "safe_mock"}


@dataclass(frozen=True)
class ServerProviderProfile:
    """Server-owned metadata for one provider execution profile.

    The catalog is intentionally code-owned.  A browser may select a profile
    id and model from this catalog, but it cannot provide a secret or endpoint.
    Adding another live provider therefore requires an explicit server-side
    transport and allowlisted profile rather than arbitrary URL injection.
    """

    provider: str
    kind: str
    label: str
    base_url: str
    default_model: str
    allowed_models: tuple[str, ...]
    secret_source: str
    execution: str
    description: str


def _server_provider_catalog() -> tuple[ServerProviderProfile, ...]:
    # DeepSeek remains the only current live profile.  The generic contract is
    # deliberately ready for additional server-owned profiles without claiming
    # that an OpenAI-compatible transport is production-enabled today.
    return (
        ServerProviderProfile(
            provider=DEEPSEEK_PROVIDER_NAME,
            kind="openai_compatible",
            label="DeepSeek",
            base_url=DEEPSEEK_BASE_URL,
            default_model=DEEPSEEK_DEFAULT_MODEL,
            allowed_models=tuple(sorted(DEEPSEEK_ALLOWED_MODELS)),
            # Do not return the concrete environment variable name in the API
            # payload; the source category is sufficient for the UI contract.
            secret_source="server_environment",
            execution="live",
            description="服务端托管的结构化科学规划与依据化结果解释服务。",
        ),
    )


def _provider_profile(provider: str | None) -> ServerProviderProfile | None:
    normalized = _normalize_provider(provider)
    return next((item for item in _server_provider_catalog() if item.provider == normalized), None)


def _allowed_provider_details() -> str:
    allowed = ",".join(item.provider for item in _server_provider_catalog())
    return f"catalogProviders={allowed or 'none'}"


def _allowed_provider_suggestions() -> list[str]:
    return [f"选择 {item.label}" for item in _server_provider_catalog()]


class ProviderResolveRequest(BaseModel):
    provider: str = Field(default="deepseek", max_length=80)
    baseUrl: str | None = Field(default=None, max_length=512)
    model: str | None = Field(default=None, max_length=128)
    secretId: str | None = Field(default=None, max_length=128)
    temperature: float = Field(default=0, ge=0, le=2)
    maxTokens: int = Field(default=8192, ge=1, le=8192)
    timeoutSeconds: float = Field(default=120.0, ge=1, le=120)
    thinkingMode: str = Field(default="standard", pattern=r"^(quick|standard|deep)$")


class ProviderTestRequest(ProviderResolveRequest):
    pass


class ProviderConfigureRequest(BaseModel):
    provider: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z][A-Za-z0-9_.-]+$")
    label: str | None = Field(default=None, max_length=120)
    kind: str = Field(default="openai_compatible", pattern=r"^openai_compatible$")
    baseUrl: str = Field(min_length=8, max_length=512)
    apiKey: str | None = Field(default=None, max_length=4096)
    defaultModel: str | None = Field(default=None, max_length=256)
    modelIds: list[str] = Field(default_factory=list, max_length=256)


class ProviderModelsUpdateRequest(BaseModel):
    modelIds: list[str] = Field(default_factory=list, max_length=256)
    defaultModel: str | None = Field(default=None, max_length=256)


def configure_planner_provider(request: ProviderConfigureRequest, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    require_platform_admin(current_user)
    try:
        if request.apiKey:
            connection = save_connection(
                provider=request.provider,
                label=request.label,
                kind=request.kind,
                base_url=request.baseUrl,
                api_key=request.apiKey,
                model_ids=request.modelIds,
                default_model=request.defaultModel,
            )
        else:
            connection = update_connection_models(
                provider=request.provider,
                model_ids=request.modelIds,
                default_model=request.defaultModel,
            )
    except ValueError as exc:
        error_code = (
            exc.code
            if isinstance(exc, ProviderConnectionConfigurationError)
            else "PROVIDER_CONFIGURATION_INVALID"
        )
        return _provider_error(
            "provider_configuration_invalid",
            str(exc),
            "字段校验失败",
            ["检查 Provider、Base URL 和 API Key"],
            error_code=error_code,
        )
    return {"ok": True, "provider": public_connection(connection), "message": "Provider 已安全保存；API Key 不会再次显示。", "redacted": True}


def update_planner_provider_models(provider: str, request: ProviderModelsUpdateRequest, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    require_platform_admin(current_user)
    try:
        connection = update_connection_models(provider=provider, model_ids=request.modelIds, default_model=request.defaultModel)
    except ValueError as exc:
        return _provider_error("provider_models_invalid", str(exc), "模型组保存失败", ["先保存 Provider，再选择模型"], error_code="PROVIDER_MODELS_INVALID")
    return {"ok": True, "provider": public_connection(connection), "message": "模型组已保存。", "redacted": True}


def remove_planner_provider(provider: str, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    require_platform_admin(current_user)
    return {"ok": delete_connection(provider), "provider": provider, "redacted": True}


def planner_provider_models(provider: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    del current_user
    connection = get_connection(provider)
    if connection is None:
        return {"ok": False, "provider": provider, "models": [], "message": "请先在模型设置中保存 Provider。", "redacted": True}
    try:
        import json
        import urllib.request
        request = urllib.request.Request(
            f"{connection.base_url}/models",
            headers={"Authorization": f"Bearer {decrypt_api_key(connection)}", "Accept": "application/json"},
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=12) as response:
            payload = json.loads(response.read(2_000_001).decode("utf-8"))
        raw_models = payload.get("data", payload.get("models", [])) if isinstance(payload, dict) else payload
        models = [str(item.get("id")) for item in raw_models if isinstance(item, dict) and item.get("id")][:256] if isinstance(raw_models, list) else []
        return {"ok": True, "provider": provider, "models": sorted(set(models)), "source": "remote_models_endpoint", "redacted": True}
    except Exception:
        return {"ok": False, "provider": provider, "models": list(connection.model_ids), "source": "saved_catalog", "message": "模型目录暂时无法读取；可以继续使用已保存的模型。", "redacted": True}


def list_planner_providers(current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    del current_user
    providers = [
        {
            "id": profile.provider,
            "provider": profile.provider,
            "kind": profile.kind,
            "label": profile.label,
            "baseUrl": profile.base_url,
            "defaultModel": profile.default_model,
            "allowedModels": list(profile.allowed_models),
            "requiresSecret": True,
            "secretSource": profile.secret_source,
            "configurationSource": "server_environment",
            "execution": profile.execution,
            "description": profile.description,
        }
        for profile in _server_provider_catalog()
    ]
    providers.extend(public_connection(connection) for connection in list_connections() if connection.provider not in {item["provider"] for item in providers})
    if _test_providers_allowed():
        providers.append(
            {
                "id": "mock",
                "label": "Deterministic test provider",
                "provider": "mock",
                "requiresSecret": False,
                "developerOnly": True,
                "kind": "deterministic",
                "execution": "offline",
                "description": "Offline tests and default CI only; never a real LLM call.",
            }
        )
    return {"providers": providers}


def planner_provider_status(current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    del current_user
    requested_provider = _normalize_provider(os.getenv("MDI_LLM_PROVIDER") or (list_connections()[0].provider if list_connections() else DEEPSEEK_PROVIDER_NAME))
    saved_connection = get_connection(requested_provider)
    if saved_connection is not None:
        return {
            "ok": True,
            "provider": saved_connection.provider,
            "kind": saved_connection.kind,
            "baseUrl": saved_connection.base_url,
            "model": saved_connection.default_model,
            "status": "ready",
            "configured": True,
            "configurationSource": saved_connection.persistence,
            "secretSource": "encrypted_server_store",
            "execution": "live",
            "allowedModels": list(saved_connection.model_ids),
            "thinkingModes": thinking_modes(),
            "message": "已配置 Provider。",
            "errorType": None,
            "redacted": True,
        }
    profile = _provider_profile(requested_provider)
    # Unknown server selections are reported honestly rather than silently
    # falling back to a different provider.  The default remains DeepSeek.
    if profile is None:
        requested = _normalize_provider(os.getenv("MDI_LLM_PROVIDER"))
        return {
            "ok": False,
            "provider": requested,
            "kind": "unknown",
            "baseUrl": None,
            "model": os.getenv("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL,
            "status": "unsupported",
            "configured": False,
            "configurationSource": "server_environment",
            "secretSource": None,
            "execution": "unavailable",
            "allowedModels": [],
            "thinkingModes": thinking_modes(),
            "message": "The configured server provider is not supported.",
            "errorType": "provider_not_supported",
            "redacted": True,
        }

    model = os.getenv("DEEPSEEK_MODEL") or profile.default_model
    model_allowed = model in profile.allowed_models
    configured = bool(os.getenv("DEEPSEEK_KEY")) and model_allowed
    return {
        "ok": configured,
        "provider": profile.provider,
        "kind": profile.kind,
        "baseUrl": profile.base_url,
        "model": model if model_allowed else profile.default_model,
        "status": "ready" if configured else "not_configured",
        "configured": configured,
        "configurationSource": "server_environment",
        "secretSource": profile.secret_source,
        "execution": profile.execution,
        "allowedModels": list(profile.allowed_models),
        "thinkingModes": thinking_modes(),
        "message": f"{profile.label} is configured." if configured else (
            f"{profile.label} model configuration is not allowed." if not model_allowed else f"{profile.label} is not configured."
        ),
        "errorType": None if configured else ("deepseek_model_not_allowed" if not model_allowed else "deepseek_not_configured"),
        "redacted": True,
    }


def resolve_planner_provider_route(request: ProviderResolveRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    del current_user
    return resolve_planner_provider(request)


def resolve_planner_provider(
    request: ProviderResolveRequest,
    *,
    secret_resolver: Callable[[str], str | None] | None = None,
) -> dict[str, Any]:
    del secret_resolver
    provider = _normalize_provider(request.provider)
    connection = get_connection(provider)
    if connection is not None:
        model = request.model or connection.default_model
        if model and connection.model_ids and model not in connection.model_ids:
            return _provider_status_error(provider=provider, model=model, error_type="provider_model_not_allowed", message="所选模型不在该 Provider 的模型目录中。", safe_details="从模型目录中选择模型", error_code="PROVIDER_MODEL_NOT_ALLOWED")
        return {
            "ok": True, "provider": provider, "kind": connection.kind, "baseUrl": connection.base_url,
            "model": model, "status": "ready", "configured": True, "willUseLiveProvider": True,
            "secretConfigured": True, "secretSource": "encrypted_server_store", "execution": "live",
            "source": connection.persistence, "thinkingModes": thinking_modes(), "message": "Provider 已配置。", "errorType": None, "redacted": True,
        }
    if provider in MOCK_PROVIDER_ALIASES:
        if not _test_providers_allowed():
            return _provider_status_error(
                provider=provider,
                model="mock",
                error_type="provider_not_allowed",
                error_code="PROVIDER_NOT_ALLOWED",
                message="Test providers require the explicit offline test gate.",
                safe_details=_allowed_provider_details(),
            )
        return {
            "ok": True,
            "provider": "mock",
            "kind": "deterministic",
            "baseUrl": None,
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
            message="实时模型调用仅允许使用已配置的 Provider。",
            safe_details=_allowed_provider_details(),
        )
    policy_error = _request_policy_error(request)
    if policy_error:
        return policy_error
    status = planner_provider_status()
    return {
        "ok": status["ok"],
        "provider": "deepseek",
        "kind": status.get("kind", "openai_compatible"),
        "baseUrl": status.get("baseUrl", DEEPSEEK_BASE_URL),
        "model": request.model or status["model"],
        "status": status["status"],
        "configured": status["configured"],
        "willUseLiveProvider": status["configured"],
        # Keep the historical redacted contract: callers learn readiness via
        # `configured`, never whether a particular secret slot is populated.
        "secretConfigured": False,
        "secretSource": status.get("secretSource"),
        "execution": status.get("execution", "live"),
        "source": "server_environment",
        "message": status["message"],
        "errorType": status["errorType"],
        "redacted": True,
    }


def test_planner_provider_route(request: ProviderTestRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    del current_user
    return test_planner_provider(request)


def test_planner_provider(
    request: ProviderTestRequest,
    *,
    transport: Any = None,
    secret_resolver: Callable[[str], str | None] | None = None,
) -> dict[str, Any]:
    del secret_resolver
    provider = _normalize_provider(request.provider)
    connection = get_connection(provider)
    if connection is not None:
        model = request.model or connection.default_model
        if not model:
            return _provider_error("provider_model_required", "请先读取并选择一个模型。", "模型目录为空", ["刷新模型目录"], error_code="PROVIDER_MODEL_REQUIRED")
        if connection.model_ids and model not in connection.model_ids:
            return _provider_error("provider_model_not_allowed", "所选模型不在该 Provider 的模型目录中。", "从模型目录中选择模型", ["刷新模型目录"], error_code="PROVIDER_MODEL_NOT_ALLOWED")
        from mdi_llm import OpenAICompatibleProvider, PlannerUserConfig
        llm = OpenAICompatibleProvider(transport=transport)
        started = time.perf_counter()
        try:
            response = llm.complete_json(
                messages=[{"role": "system", "content": "Return exactly one JSON object with status equal to ok."}, {"role": "user", "content": '{"purpose":"provider_connection_test"}'}],
                user_config=PlannerUserConfig(provider=provider, model=model, base_url=connection.base_url, api_key=decrypt_api_key(connection), timeout_seconds=request.timeoutSeconds, temperature=0, max_tokens=256, thinking_mode=request.thinkingMode),
                purpose="PROVIDER_CONNECTION_TEST",
            )
        except LLMProviderError as exc:
            return _provider_exception_error(exc)
        if response.raw_json != {"status": "ok"}:
            return _provider_error("provider_response_invalid", "Provider 未返回预期的连接测试结果。", "响应必须为严格 JSON 状态对象", ["检查所选模型是否支持 JSON 输出"])
        return {"ok": True, "provider": provider, "kind": connection.kind, "baseUrl": connection.base_url, "model": response.model, "latencyMs": int((time.perf_counter() - started) * 1000), "validated": True, "message": "Provider 连接成功。", "redacted": True, "realLlmCalls": 0 if transport is not None else 1}
    if provider in MOCK_PROVIDER_ALIASES:
        if not _test_providers_allowed():
            return _provider_error(
                "provider_not_allowed",
                "Test providers require the explicit offline test gate.",
                _allowed_provider_details(),
                _allowed_provider_suggestions(),
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
            "实时模型调用仅允许使用已配置的 Provider。",
            _allowed_provider_details(),
            _allowed_provider_suggestions(),
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
        "kind": "openai_compatible",
        "baseUrl": DEEPSEEK_BASE_URL,
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
        "kind": "deterministic" if provider in MOCK_PROVIDER_ALIASES else "unknown",
        "baseUrl": None,
        "model": model,
        "status": "not_configured",
        "configured": False,
        "willUseLiveProvider": False,
        "secretConfigured": False,
        "secretSource": None,
        "execution": "offline" if provider in MOCK_PROVIDER_ALIASES else "unavailable",
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
