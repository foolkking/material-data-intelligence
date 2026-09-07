"""Canonical transport-neutral LLM provider selection.

This module owns provider-selection policy for every caller: the planner HTTP
transport, the research transport and deterministic report composition. It
deliberately depends only on configuration, the provider-connection catalogue
and `mdi_llm` provider contracts, so it can be called without a FastAPI
request, router instance or router-private helper.

Behavior is transplanted unchanged from the former private router helper
`mdi_api.routers.planner._select_planner_provider`; that name is retained
there as a thin delegating facade for existing callers and patch targets.
"""

from __future__ import annotations

import os
from typing import Any

from mdi_llm import DeepSeekProvider, LLMProviderError, MockLLMProvider, OpenAICompatibleProvider

from mdi_api.provider_connections import get_connection

__all__ = [
    "TEST_PROVIDER_NAMES",
    "requested_provider_name",
    "select_llm_provider",
    "test_providers_allowed",
]


# Deterministic/offline provider names that require the explicit offline gate.
TEST_PROVIDER_NAMES = frozenset({"", "mock", "mock_llm", "deterministic", "safe_mock"})

# Single offline provider instance shared by every caller. The planner module
# aliases this object so the previously module-level `_LLM_PROVIDER` identity
# is preserved rather than duplicated.
_MOCK_PROVIDER = MockLLMProvider()


def requested_provider_name(requested_provider: str | None) -> str:
    """Resolve the effective provider name from request then environment."""

    return (requested_provider or os.getenv("MDI_LLM_PROVIDER") or "deepseek").strip().lower()


def test_providers_allowed() -> bool:
    """Report whether deterministic/offline providers are explicitly gated on."""

    return os.getenv("MDI_ALLOW_TEST_PROVIDERS", "").strip().lower() in {"1", "true", "yes", "on"}


def select_llm_provider(requested_provider: str | None, *, provider: Any = None) -> Any:
    """Select the LLM provider for a request.

    An explicitly injected `provider` is always honored and bypasses the
    offline gate. Otherwise the resolved name selects a deterministic offline
    provider (gated), DeepSeek, or a configured OpenAI-compatible connection.
    An unconfigured name is refused fail-closed.
    """

    if provider is not None:
        return provider
    provider_name = requested_provider_name(requested_provider)
    if provider_name in TEST_PROVIDER_NAMES:
        if not test_providers_allowed():
            raise LLMProviderError(
                "Test and deterministic providers require the explicit offline test gate.",
                code="PROVIDER_NOT_ALLOWED",
            )
        return _MOCK_PROVIDER
    if provider_name == "deepseek":
        return DeepSeekProvider()
    if get_connection(provider_name) is not None:
        return OpenAICompatibleProvider()
    raise LLMProviderError(
        "所选 Provider 尚未配置或不在服务目录中。",
        code="PROVIDER_NOT_ALLOWED",
    )
