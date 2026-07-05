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
        elif _should_generate_scatter(request, tools, data_profile):
            plan = _mock_scatter_plan(request, tools, data_profile=data_profile)
        elif _should_generate_correlation(request, tools, data_profile):
            plan = _mock_correlation_plan(request, tools, data_profile=data_profile)
        elif _should_generate_distribution_summary(request, tools, data_profile):
            plan = _mock_distribution_summary_plan(request, tools, data_profile=data_profile)
        elif _should_generate_histogram(request, tools, data_profile):
            plan = _mock_histogram_plan(request, tools, data_profile=data_profile)
        elif _should_generate_composition_summary(request, tools, data_profile):
            plan = _mock_composition_summary_plan(request, tools, data_profile=data_profile)
        elif _should_generate_numeric_summary(request, tools, data_profile):
            plan = _mock_numeric_summary_plan(request, tools, data_profile=data_profile)
        else:
            plan = _mock_basic_metrics_plan(request, tools, data_profile=data_profile)
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

    Configuration is resolved at call time. Explicit per-request
    PlannerUserConfig values win when provided; otherwise MDI_LLM_* and
    OPENAI_* environment variables are used for gated integration tests. The
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
        resolved = _resolve_openai_config(config, prefer_config=user_config is not None)

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


def _resolve_openai_config(config: PlannerUserConfig, *, prefer_config: bool = False) -> dict[str, Any]:
    if prefer_config:
        return {
            "api_key": config.api_key or os.environ.get("MDI_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY"),
            "base_url": (config.base_url or os.environ.get("MDI_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/"),
            "model": config.model or os.environ.get("MDI_LLM_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-4o",
            "timeout_seconds": config.timeout_seconds,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
        }
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
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    response_format_attempts = (False,) if _base_url_disables_response_format(base_url) else (True, False)
    for include_response_format in response_format_attempts:
        body_payload = dict(payload)
        if include_response_format:
            body_payload["response_format"] = {"type": "json_object"}
        body = json.dumps(body_payload).encode("utf-8")

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (TimeoutError, socket.timeout) as exc:
            raise LLMProviderError("OpenAI-compatible LLM request timed out.", code="LLM_TIMEOUT") from None
        except urllib.error.HTTPError as exc:
            if include_response_format and int(getattr(exc, "code", 0) or 0) == 400:
                continue
            raise _http_error(exc) from None
        except urllib.error.URLError as exc:
            raise LLMProviderError("OpenAI-compatible LLM request failed before a response was received.", code="LLM_NETWORK_ERROR") from None
        except ValueError as exc:
            raise LLMProviderError("OpenAI-compatible LLM response was not valid JSON.", code="LLM_RESPONSE_INVALID") from None

    raise LLMProviderError("OpenAI-compatible LLM request failed.", code="LLM_PROVIDER_ERROR")


def _base_url_disables_response_format(base_url: str) -> bool:
    return "generativelanguage.googleapis.com" in base_url.lower()


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


def _mock_basic_metrics_plan(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    *,
    data_profile: DataProfile,
) -> dict[str, Any]:
    """Generate a minimal valid plan with a single ml.basic_metrics step.

    The step references the conventional ``ml_table`` normalized object so the
    plan is executable end-to-end through the runtime + Tool Registry + Adapter.
    """
    target_column, prediction_column, column_reason = _select_regression_columns(data_profile)
    step = {
        "stepId": "step_001",
        "toolId": "ml.basic_metrics",
        "purpose": "Compute regression metrics",
        "reason": column_reason or "User requested basic regression evaluation",
        "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        "params": {"targetColumn": target_column, "predictionColumn": prediction_column},
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


def _mock_numeric_summary_plan(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    *,
    data_profile: DataProfile,
) -> dict[str, Any]:
    """Generate a descriptive table-summary plan for non-regression tables."""
    params = _numeric_summary_params(data_profile)
    step = {
        "stepId": "step_001",
        "toolId": "table.numeric_summary",
        "purpose": "Summarize numeric and categorical columns",
        "reason": "The request asks for table statistics rather than target/prediction error metrics.",
        "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        "params": params,
        "output": {"artifactTypes": ["table_json", "summary_md", "recipe_json"]},
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
        "expectedArtifacts": [
            {"name": "numeric_summary.json", "type": "table_json", "fromStepId": "step_001"},
            {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
            {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
        ],
    }


def _mock_distribution_summary_plan(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    *,
    data_profile: DataProfile,
) -> dict[str, Any]:
    params = _numeric_summary_params(data_profile)
    params["maxCategories"] = params.get("maxCategories", 12)
    step = {
        "stepId": "step_001",
        "toolId": "table.distribution_summary",
        "purpose": "Summarize table distributions",
        "reason": "The request asks for numeric/categorical distribution statistics.",
        "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        "params": params,
        "output": {"artifactTypes": ["table_json", "summary_md", "recipe_json"]},
    }
    return _single_step_plan(
        request,
        step,
        [{"name": "distribution_summary.json", "type": "table_json", "fromStepId": "step_001"}],
    )


def _mock_scatter_plan(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    *,
    data_profile: DataProfile,
) -> dict[str, Any]:
    x_column, y_column = _select_scatter_columns(data_profile)
    step = {
        "stepId": "step_001",
        "toolId": "viz.scatter",
        "purpose": "Generate a scatter plot",
        "reason": f"The request asks to compare numeric columns {x_column} and {y_column}.",
        "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        "params": {"xColumn": x_column, "yColumn": y_column, "title": f"{x_column} vs {y_column}"},
        "output": {"artifactTypes": ["plotly_json", "plotly_html", "summary_md", "recipe_json"]},
    }
    return _single_step_plan(
        request,
        step,
        [{"name": "scatter.json", "type": "plotly_json", "fromStepId": "step_001"}],
    )


def _mock_histogram_plan(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    *,
    data_profile: DataProfile,
) -> dict[str, Any]:
    column = _select_histogram_column(request, data_profile)
    step = {
        "stepId": "step_001",
        "toolId": "viz.histogram",
        "purpose": "Generate a histogram",
        "reason": f"The request asks for the distribution of numeric column {column}.",
        "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        "params": {"column": column, "bins": 20, "title": f"{column} distribution"},
        "output": {"artifactTypes": ["plotly_json", "plotly_html", "summary_md", "recipe_json"]},
    }
    return _single_step_plan(
        request,
        step,
        [{"name": "histogram.json", "type": "plotly_json", "fromStepId": "step_001"}],
    )


def _mock_correlation_plan(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    *,
    data_profile: DataProfile,
) -> dict[str, Any]:
    columns = _numeric_columns(data_profile)[:12]
    step = {
        "stepId": "step_001",
        "toolId": "viz.correlation",
        "purpose": "Generate a numeric correlation matrix",
        "reason": "The request asks for correlations between numeric fields.",
        "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        "params": {"numericColumns": columns, "method": "pearson", "minNonNullCount": 2},
        "output": {"artifactTypes": ["table_json", "plotly_json", "plotly_html", "summary_md", "recipe_json"]},
    }
    return _single_step_plan(
        request,
        step,
        [{"name": "correlation_matrix.json", "type": "table_json", "fromStepId": "step_001"}],
    )


def _mock_composition_summary_plan(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    *,
    data_profile: DataProfile,
) -> dict[str, Any]:
    formula_column = _formula_column(data_profile)
    params = {"formulaColumn": formula_column} if formula_column else {}
    step = {
        "stepId": "step_001",
        "toolId": "composition.summary",
        "purpose": "Summarize formula compositions",
        "reason": f"The request asks for element composition statistics from {formula_column or 'formula data'}.",
        "inputRefs": [{"refType": "normalized_object", "ref": "formulas", "objectType": "Composition"}],
        "params": params,
        "output": {"artifactTypes": ["table_json", "summary_md", "recipe_json"]},
    }
    return _single_step_plan(
        request,
        step,
        [{"name": "composition_summary.json", "type": "table_json", "fromStepId": "step_001"}],
    )


def _single_step_plan(
    request: PlannerRequest,
    step: dict[str, Any],
    expected_artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schemaVersion": "0.1",
        "goal": request.user_prompt,
        "datasetId": request.dataset_id,
        "profileId": request.profile_id,
        "toolRegistryVersion": request.tool_registry_version,
        "assumptions": ["Generated by MockLLMProvider for testing."],
        "warnings": [],
        "steps": [step],
        "expectedArtifacts": expected_artifacts,
    }


def _should_generate_scatter(request: PlannerRequest, tools: list[RegisteredTool], data_profile: DataProfile) -> bool:
    if not _has_tool(tools, "viz.scatter"):
        return False
    prompt = request.user_prompt.lower()
    return any(marker in prompt for marker in ("scatter", "散点", "比较", "compare")) and len(_numeric_columns(data_profile)) >= 2


def _should_generate_histogram(request: PlannerRequest, tools: list[RegisteredTool], data_profile: DataProfile) -> bool:
    if not _has_tool(tools, "viz.histogram"):
        return False
    prompt = request.user_prompt.lower()
    return any(marker in prompt for marker in ("histogram", "distribution", "分布", "直方图")) and len(_numeric_columns(data_profile)) >= 1


def _should_generate_correlation(request: PlannerRequest, tools: list[RegisteredTool], data_profile: DataProfile) -> bool:
    if not _has_tool(tools, "viz.correlation"):
        return False
    prompt = request.user_prompt.lower()
    return any(marker in prompt for marker in ("correlation", "相关", "相关性")) and len(_numeric_columns(data_profile)) >= 2


def _should_generate_distribution_summary(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "table.distribution_summary"):
        return False
    prompt = request.user_prompt.lower()
    markers = ("distribution summary", "distribution statistics", "数值分布", "类别字段", "分布统计")
    return any(marker in prompt for marker in markers)


def _should_generate_composition_summary(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "composition.summary"):
        return False
    prompt = request.user_prompt.lower()
    markers = ("composition summary", "element composition", "元素组成", "组成", "formula")
    return any(marker in prompt for marker in markers) and bool(_formula_column(data_profile))


def _should_generate_numeric_summary(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "table.numeric_summary"):
        return False
    prompt = request.user_prompt.lower()
    summary_markers = (
        "numeric summary",
        "table summary",
        "data summary",
        "metallic glasses",
        "ward",
        "数值列分布",
        "组成字段",
        "类别字段",
        "基础数据摘要",
        "数据摘要",
    )
    regression_markers = ("target", "prediction", "y_true", "y_pred", "误差指标", "预测误差")
    if any(marker in prompt for marker in summary_markers) and not any(marker in prompt for marker in regression_markers):
        return True
    names = {name.lower() for name in _table_column_names(data_profile)}
    return {"composition", "gfa_type"}.issubset(names) and any(marker in prompt for marker in summary_markers)


def _has_tool(tools: list[RegisteredTool], tool_id: str) -> bool:
    return any(tool.toolId == tool_id for tool in tools)


def _numeric_summary_params(data_profile: DataProfile) -> dict[str, Any]:
    columns = _table_columns(data_profile)
    numeric_columns = _numeric_columns(data_profile)
    categorical_columns = [
        name
        for column in columns
        if (name := _column_name(column))
        and not _is_numeric_column(column)
        and _is_candidate_metric_column(column, data_profile)
    ]
    params: dict[str, Any] = {"maxCategories": 12}
    if numeric_columns:
        params["numericColumns"] = numeric_columns
    if categorical_columns:
        params["categoricalColumns"] = categorical_columns
    return params


def _select_scatter_columns(data_profile: DataProfile) -> tuple[str, str]:
    names = _table_column_names(data_profile)
    by_lower = {name.lower(): name for name in names}
    if "pbe" in by_lower and "r2scan" in by_lower:
        return by_lower["pbe"], by_lower["r2scan"]
    numeric_columns = _numeric_columns(data_profile)
    if len(numeric_columns) >= 2:
        return numeric_columns[0], numeric_columns[1]
    return "x", "y"


def _select_histogram_column(request: PlannerRequest, data_profile: DataProfile) -> str:
    prompt = request.user_prompt.lower()
    names = _table_column_names(data_profile)
    for name in names:
        if name.lower() in prompt and name in _numeric_columns(data_profile):
            return name
    numeric_columns = _numeric_columns(data_profile)
    return numeric_columns[0] if numeric_columns else "value"


def _numeric_columns(data_profile: DataProfile) -> list[str]:
    return [
        name
        for column in _table_columns(data_profile)
        if (name := _column_name(column))
        and _is_numeric_column(column)
        and _is_candidate_metric_column(column, data_profile)
    ]


def _formula_column(data_profile: DataProfile) -> str:
    by_lower = {name.lower(): name for name in _table_column_names(data_profile)}
    for candidate in ("formula", "composition", "reduced_formula", "pretty_formula", "formula_pretty"):
        if candidate in by_lower:
            return by_lower[candidate]
    return ""


def _select_regression_columns(data_profile: DataProfile) -> tuple[str, str, str | None]:
    columns = _table_columns(data_profile)
    if not columns:
        return "y_true", "y_pred", None

    target = _find_column_by_role(columns, "target") or _find_column_by_name(
        columns, ("target", "y_true", "true", "actual", "label", "y")
    )
    prediction = _find_column_by_role(columns, "prediction") or _find_column_by_name(
        columns, ("prediction", "pred", "y_pred", "predicted", "estimate", "p")
    )
    if target and prediction and target != prediction:
        return target, prediction, f"Selected DataProfile target/prediction columns {target} and {prediction}."

    numeric_columns = [
        name
        for column in columns
        if (name := _column_name(column))
        and _is_numeric_column(column)
        and _is_candidate_metric_column(column, data_profile)
        and str(column.get("inferredRole") or "").lower() not in {"structure_id", "formula", "label"}
    ]
    if len(numeric_columns) >= 2:
        return (
            numeric_columns[0],
            numeric_columns[1],
            f"Selected the first two numeric DataProfile columns {numeric_columns[0]} and {numeric_columns[1]}.",
        )

    return "y_true", "y_pred", None


def _table_columns(data_profile: DataProfile) -> list[dict[str, Any]]:
    table_summary = getattr(data_profile, "tableSummary", None) or {}
    if not isinstance(table_summary, dict):
        return []
    columns = table_summary.get("columns") or []
    return [column for column in columns if isinstance(column, dict)]


def _find_column_by_role(columns: list[dict[str, Any]], role: str) -> str | None:
    for column in columns:
        if str(column.get("inferredRole") or "").lower() == role:
            name = _column_name(column)
            if name:
                return name
    return None


def _find_column_by_name(columns: list[dict[str, Any]], candidates: tuple[str, ...]) -> str | None:
    by_lower = {name.lower(): name for column in columns if (name := _column_name(column))}
    for candidate in candidates:
        if candidate in by_lower:
            return by_lower[candidate]
    return None


def _table_column_names(data_profile: DataProfile) -> list[str]:
    return [name for column in _table_columns(data_profile) if (name := _column_name(column))]


def _column_name(column: dict[str, Any]) -> str:
    name = column.get("name")
    return str(name) if name not in (None, "") else ""


def _is_numeric_column(column: dict[str, Any]) -> bool:
    return str(column.get("dtype") or "").lower() in {"number", "integer", "float", "double", "int"}


def _is_candidate_metric_column(column: dict[str, Any], data_profile: DataProfile) -> bool:
    name = _column_name(column).strip().lower()
    if not name or name.startswith("unnamed:"):
        return False
    table_summary = getattr(data_profile, "tableSummary", None) or {}
    n_rows = table_summary.get("nRows") if isinstance(table_summary, dict) else None
    missing = column.get("missingCount")
    if isinstance(n_rows, int) and n_rows > 0 and isinstance(missing, int):
        if missing / n_rows > 0.95:
            return False
    return True
