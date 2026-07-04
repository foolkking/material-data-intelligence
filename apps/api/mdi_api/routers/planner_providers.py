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


class ProviderTestRequest(BaseModel):
    provider: str = Field(default="mock", max_length=80)
    baseUrl: str | None = None
    model: str | None = None
    secretId: str | None = None
    temperature: float = 0.1
    maxTokens: int = 1024
    timeoutSeconds: float = 60.0


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
    provider = (os.getenv("MDI_LLM_PROVIDER") or "mock").strip().lower() or "mock"
    if provider in {"mock", "mock_llm", "deterministic", "safe_mock"}:
        return {
            "ok": True,
            "provider": "mock",
            "model": "mock",
            "status": "ready",
            "message": "Mock Planner is active. No external LLM will be called by default.",
        }
    configured = provider == "openai_compatible" and bool(os.getenv("MDI_LLM_API_KEY") or os.getenv("OPENAI_API_KEY"))
    return {
        "ok": configured,
        "provider": provider,
        "model": os.getenv("MDI_LLM_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o",
        "status": "ready" if configured else "not_configured",
        "message": "OpenAI-compatible provider is configured." if configured else "OpenAI-compatible provider needs a configured API key.",
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
    provider = request.provider.strip().lower() or "mock"
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
        if provider in {"mock", "mock_llm", "deterministic", "safe_mock"}:
            llm = MockLLMProvider()
            user_config = None
        elif provider == "openai_compatible":
            secret_id = request.secretId or ""
            api_key = secret_resolver(secret_id) if secret_id else None
            if not api_key:
                return _provider_error(
                    "provider_not_configured",
                    "真实大模型尚未配置，请先保存并选择 API Key。",
                    "secretId is missing or was not found",
                    ["保存 API Key", "选择已保存密钥", "切换到 Mock Planner"],
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
                "暂不支持该模型供应商。",
                f"provider={provider}",
                ["选择 Mock Planner", "选择 OpenAI-compatible LLM"],
            )

        started = time.perf_counter()
        response = llm.generate_plan(planner_request, tools=tools, data_profile=data_profile, user_config=user_config)
        latency_ms = int((time.perf_counter() - started) * 1000)
    except LLMProviderError as exc:
        return _provider_exception_error(exc)

    if response.raw_json is None:
        return _provider_error(
            "provider_response_invalid",
            "模型返回内容不是合法 JSON。",
            "Provider response could not be parsed as an AnalysisPlan JSON object.",
            ["降低 temperature", "检查模型是否支持 JSON 输出", "切换到 Mock Planner 验证流程"],
        )

    validation = validate_plan(response.raw_json, registry=registry)
    if not validation.ok:
        return _provider_error(
            "plan_validation_failed",
            "模型返回的计划没有通过校验。",
            "; ".join(f"{error.code}: {error.message}" for error in validation.errors),
            ["调整提示词", "检查工具是否属于 MVP Tool Registry", "切换到 Mock Planner 验证流程"],
        )

    return {
        "ok": True,
        "provider": provider,
        "model": response.model,
        "latencyMs": latency_ms,
        "validated": True,
        "message": "模型连接成功，并成功返回可解析的 AnalysisPlan。",
        "redacted": True,
    }


def _provider_exception_error(exc: LLMProviderError) -> dict[str, Any]:
    if exc.status_code == 401:
        error_type = "provider_auth_failed"
        message = "模型认证失败，请检查 API Key。"
    elif exc.status_code == 429:
        error_type = "provider_rate_limited"
        message = "模型请求被限流，请稍后重试。"
    elif exc.code == "LLM_TIMEOUT":
        error_type = "provider_timeout"
        message = "模型请求超时，请检查网络或 base URL。"
    elif exc.code == "LLM_API_KEY_MISSING":
        error_type = "provider_not_configured"
        message = "真实大模型尚未配置，请先保存并选择 API Key。"
    else:
        error_type = "provider_error"
        message = "模型连接失败，请检查配置。"
    return _provider_error(error_type, message, exc.safe_message, ["检查 base URL", "检查模型名称", "切换到 Mock Planner"])


def _provider_error(error_type: str, message: str, safe_details: str, suggestions: list[str]) -> dict[str, Any]:
    return {
        "ok": False,
        "errorType": error_type,
        "message": message,
        "safeDetails": safe_details,
        "suggestions": suggestions,
        "redacted": True,
    }
