"""Phase 7 LLM JSON Planner — public exports."""

from __future__ import annotations

from .planner_prompt import build_planner_prompt
from .analysis_intent import (
    AnalysisIntentError,
    AnalysisIntentRequest,
    AnalysisIntentValidator,
    ClarificationSubmission,
    DeterministicAnalysisIntentBuilder,
    OpenAICompatibleAnalysisIntentBuilder,
    build_analysis_intent_messages,
    detect_goal_language,
    normalize_analysis_goal,
)
from .providers import (
    LLMProviderError,
    LLMPlannerProvider,
    MockLLMProvider,
    OpenAICompatibleProvider,
    PlannerRawResponse,
    PlannerRequest,
    PlannerUserConfig,
)
from .capability_planner import (
    CAPABILITY_PLANNER_VERSION,
    CapabilityContextValidator,
    CapabilityPlanningError,
    CapabilityPlanningResult,
    plan_capabilities,
    project_eligible_candidates,
    resolve_eligibility,
)
from .redaction import is_credential_key, redact_credential_values, redact_params_for_log

__all__ = [
    "AnalysisIntentError",
    "AnalysisIntentRequest",
    "AnalysisIntentValidator",
    "CAPABILITY_PLANNER_VERSION",
    "CapabilityContextValidator",
    "CapabilityPlanningError",
    "CapabilityPlanningResult",
    "ClarificationSubmission",
    "DeterministicAnalysisIntentBuilder",
    "OpenAICompatibleAnalysisIntentBuilder",
    "build_analysis_intent_messages",
    "build_planner_prompt",
    "detect_goal_language",
    "is_credential_key",
    "LLMProviderError",
    "LLMPlannerProvider",
    "MockLLMProvider",
    "OpenAICompatibleProvider",
    "PlannerRawResponse",
    "PlannerRequest",
    "PlannerUserConfig",
    "plan_capabilities",
    "project_eligible_candidates",
    "redact_credential_values",
    "redact_params_for_log",
    "resolve_eligibility",
    "normalize_analysis_goal",
]
