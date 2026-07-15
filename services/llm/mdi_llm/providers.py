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

from mdi_schemas import DataProfile, RegisteredTool

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
        elif _should_generate_phonon_animation(request, tools, data_profile):
            plan = _mock_phonon_animation_plan(request, data_profile)
        elif _should_generate_phonon_band_dos(request, tools, data_profile):
            plan = _mock_phonon_band_dos_plan(request, data_profile)
        elif _should_generate_phonon_dos(request, tools, data_profile):
            plan = _mock_phonon_dos_plan(request)
        elif _should_generate_phonon_band(request, tools, data_profile):
            plan = _mock_phonon_band_plan(request)
        elif _should_generate_trajectory_viewer(request, tools, data_profile):
            plan = _mock_trajectory_viewer_plan(request)
        elif _should_generate_brillouin_zone(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.brillouin_zone",
                purpose="Generate validated inert first-Brillouin-zone data and the canonical high-symmetry k-path for the application-owned interactive viewer; artifacts include no renderer or external resources.",
                params={
                    "include_reciprocal_lattice": True,
                    "include_brillouin_zone": True,
                    "include_kpath": True,
                    "standardization": "contract_default",
                    "kpath_provider": "contract_default",
                    "time_reversal": True,
                    "symmetry_tolerance_angstrom": 0.00001,
                    "angle_tolerance_degrees": 5.0,
                    "include_alternative_path_variants": False,
                },
                artifact_name="reciprocal_lattice.json",
                artifact_type="reciprocal_lattice_json",
                artifact_types=[
                    "reciprocal_lattice_json",
                    "brillouin_zone_json",
                    "kpath_json",
                    "brillouin_zone_manifest_json",
                    "summary_md",
                    "recipe_json",
                ],
                extra_expected_artifacts=[
                    {"name": "brillouin_zone.json", "type": "brillouin_zone_json", "fromStepId": "step_001"},
                    {"name": "kpath.json", "type": "kpath_json", "fromStepId": "step_001"},
                    {"name": "brillouin_zone_manifest.json", "type": "brillouin_zone_manifest_json", "fromStepId": "step_001"},
                ],
            )
        elif _should_generate_viewer_scene(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.viewer_scene",
                purpose="Create an inert viewer_scene.v2 JSON artifact with the current manifest; no renderer is included.",
                params={
                    "include_bonds": True,
                    "bond_cutoff_angstrom": 3.0,
                    "max_sites": 256,
                    "max_bonds": 2048,
                    "coordinate_basis": "cartesian_angstrom",
                    "include_cartesian_positions": True,
                    "include_fractional_positions": True,
                    "cell_expansion": [1, 1, 1],
                    "style_preset": "default",
                    "camera_preset": "auto",
                },
                artifact_name="viewer_scene.json",
                artifact_type="structure_json",
                artifact_types=["structure_json", "table_json", "summary_md", "recipe_json"],
                extra_expected_artifacts=[{"name": "viewer_scene_manifest.json", "type": "table_json", "fromStepId": "step_001"}],
            )
        elif _should_generate_viewer_export_package(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.viewer_scene",
                purpose="Regenerate a current inert viewer_scene.v2 artifact package; legacy export production is deprecated.",
                params=_canonical_viewer_scene_params(),
                artifact_name="viewer_scene.json",
                artifact_type="structure_json",
                artifact_types=["structure_json", "table_json", "summary_md", "recipe_json"],
                extra_expected_artifacts=[{"name": "viewer_scene_manifest.json", "type": "table_json", "fromStepId": "step_001"}],
            )
        elif _should_generate_viewer_scene_metadata(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.viewer_scene",
                purpose="Regenerate current inert viewer_scene.v2 data; legacy metadata production is deprecated.",
                params=_canonical_viewer_scene_params(),
                artifact_name="viewer_scene.json",
                artifact_type="structure_json",
                artifact_types=["structure_json", "table_json", "summary_md", "recipe_json"],
                extra_expected_artifacts=[{"name": "viewer_scene_manifest.json", "type": "table_json", "fromStepId": "step_001"}],
            )
        elif _should_generate_structure_viewer(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.viewer_3d",
                purpose="Generate a canonical inert viewer scene for the minimal interactive structure viewer.",
                params=_canonical_viewer_scene_params(),
                artifact_name="viewer_scene.json",
                artifact_type="structure_json",
                artifact_types=["structure_json", "table_json", "summary_md", "recipe_json"],
                extra_expected_artifacts=[{"name": "viewer_scene_manifest.json", "type": "table_json", "fromStepId": "step_001"}],
            )
        elif _should_generate_rdf(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.rdf",
                purpose="Compute a static radial distribution function using periodic neighbors and number-density normalization.",
                params={
                    "r_max_angstrom": 8.0,
                    "bin_width_angstrom": 0.1,
                    "normalization": "number_density",
                    "include_partial_pairs": True,
                    "max_partial_pairs": 64,
                    "max_sites": 500,
                    "max_bins": 1000,
                    "max_neighbors_total": 200000,
                    "plot_kind": "line",
                },
                artifact_name="rdf.json",
                artifact_type="table_json",
                artifact_types=["table_json", "plotly_json", "summary_md", "recipe_json"],
                extra_expected_artifacts=[
                    {"name": "rdf_plot.json", "type": "plotly_json", "fromStepId": "step_001"}
                ],
            )
        elif _should_generate_xrd(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.xrd",
                purpose="Generate a static simulated XRD peak list using deterministic CuKa defaults.",
                params={
                    "radiation": "CuKa",
                    "two_theta_min": 0.0,
                    "two_theta_max": 90.0,
                    "intensity_threshold": 0.0,
                    "peak_merge_tolerance": 0.05,
                    "max_peaks": 500,
                    "include_hkl": True,
                    "plot_kind": "stem",
                },
                artifact_name="xrd_pattern.json",
                artifact_type="table_json",
                artifact_types=["table_json", "plotly_json", "summary_md", "recipe_json"],
                extra_expected_artifacts=[
                    {"name": "xrd_plot.json", "type": "plotly_json", "fromStepId": "step_001"}
                ],
            )
        elif _should_generate_coordination_hist(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.coordination_hist",
                purpose="Compute a static coordination-number histogram using deterministic distance-cutoff neighbors.",
                params={
                    "neighbor_policy": "distance_cutoff",
                    "cutoff_angstrom": 3.0,
                    "max_sites": 500,
                    "max_neighbors_per_site": 128,
                    "include_site_details": True,
                    "group_by_element": True,
                    "include_pair_counts": True,
                    "plot_kind": "bar",
                },
                artifact_name="coordination_hist.json",
                artifact_type="table_json",
                artifact_types=["table_json", "plotly_json", "summary_md", "recipe_json"],
                extra_expected_artifacts=[
                    {"name": "coordination_hist_plot.json", "type": "plotly_json", "fromStepId": "step_001"}
                ],
            )
        elif _should_generate_structure_spacegroup(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.spacegroup_summary",
                purpose="Detect space group and crystal system information.",
                params={"symprec": 0.01, "angleTolerance": 5, "maxStructures": 50},
                artifact_name="spacegroup_summary.json",
                artifact_type="table_json",
                artifact_types=["table_json", "summary_md", "recipe_json"],
            )
        elif _should_generate_structure_lattice(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.lattice_summary",
                purpose="Summarize lattice parameters and volumes.",
                params={"maxStructures": 100, "detectOutliers": True},
                artifact_name="lattice_summary.json",
                artifact_type="table_json",
                artifact_types=["table_json", "summary_md", "recipe_json"],
            )
        elif _should_generate_structure_composition(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.composition_from_structure",
                purpose="Extract composition information from structure objects.",
                params={"maxStructures": 100, "includeRecommendedTools": True},
                artifact_name="structure_composition.json",
                artifact_type="table_json",
                artifact_types=["table_json", "summary_md", "recipe_json"],
            )
        elif _should_generate_structure_preview(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.preview_metadata",
                purpose="Generate lightweight structure preview metadata.",
                params={"maxPreviewSites": 100, "includeCartesian": True, "includeFractional": True},
                artifact_name="structure_preview_metadata.json",
                artifact_type="structure_json",
                artifact_types=["structure_json", "summary_md", "recipe_json"],
            )
        elif _should_generate_structure_summary(request, tools, data_profile):
            plan = _mock_structure_plan(
                request,
                data_profile=data_profile,
                tool_id="structure.summary",
                purpose="Summarize structure formula, elements, sites, and lattice.",
                params={"maxStructures": 50, "includeSitesPreview": True, "maxPreviewSites": 20},
                artifact_name="structure_summary.json",
                artifact_type="structure_json",
                artifact_types=["structure_json", "summary_md", "recipe_json"],
            )
        elif _should_generate_ptable_heatmap(request, tools, data_profile):
            plan = _mock_composition_visual_plan(
                request,
                data_profile=data_profile,
                tool_id="composition.ptable_heatmap",
                purpose="Create a periodic table heatmap of element occurrence.",
                params=_composition_params(data_profile, {"countMode": "occurrence", "log": False}),
                artifact_name="ptable_heatmap.json",
            )
        elif _should_generate_elements_hist(request, tools, data_profile):
            plan = _mock_composition_visual_plan(
                request,
                data_profile=data_profile,
                tool_id="composition.elements_hist",
                purpose="Create an element frequency histogram.",
                params=_composition_params(data_profile, {"countMode": "occurrence", "topN": 30}),
                artifact_name="elements_hist.json",
            )
        elif _should_generate_chem_sys_sunburst(request, tools, data_profile):
            plan = _mock_composition_visual_plan(
                request,
                data_profile=data_profile,
                tool_id="composition.chem_sys_sunburst",
                purpose="Create a chemical system sunburst hierarchy.",
                params=_composition_params(
                    data_profile,
                    {"hierarchy": ["arity", "chem_sys", "reduced_formula"], "maxLeafNodes": 100},
                ),
                artifact_name="chem_sys_sunburst.json",
            )
        elif _should_generate_chem_sys_treemap(request, tools, data_profile):
            plan = _mock_composition_visual_plan(
                request,
                data_profile=data_profile,
                tool_id="composition.chem_sys_treemap",
                purpose="Create a chemical system treemap.",
                params=_composition_params(data_profile, {"groupMode": "chem_sys", "maxGroups": 50}),
                artifact_name="chem_sys_treemap.json",
            )
        elif _should_generate_formula_statistics(request, tools, data_profile):
            plan = _mock_composition_visual_plan(
                request,
                data_profile=data_profile,
                tool_id="composition.formula_statistics",
                purpose="Summarize formula statistics.",
                params=_composition_params(data_profile, {"maxExamples": 20, "strict": False}),
                artifact_name="formula_statistics.json",
                artifact_type="table_json",
                artifact_types=["table_json", "summary_md", "recipe_json"],
            )
        elif _should_generate_scatter(request, tools, data_profile):
            plan = _mock_scatter_plan(request, tools, data_profile=data_profile)
        elif _should_generate_correlation(request, tools, data_profile):
            plan = _mock_correlation_plan(request, tools, data_profile=data_profile)
        elif _should_generate_distribution_summary(request, tools, data_profile):
            plan = _mock_distribution_summary_plan(request, tools, data_profile=data_profile)
        elif _should_generate_composition_summary(request, tools, data_profile):
            plan = _mock_composition_summary_plan(request, tools, data_profile=data_profile)
        elif _should_generate_histogram(request, tools, data_profile):
            plan = _mock_histogram_plan(request, tools, data_profile=data_profile)
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
    except (TimeoutError, socket.timeout):
        raise LLMProviderError("OpenAI-compatible LLM request timed out.", code="LLM_TIMEOUT") from None
    except urllib.error.HTTPError as exc:
        raise _http_error(exc) from None
    except urllib.error.URLError:
        raise LLMProviderError("OpenAI-compatible LLM request failed before a response was received.", code="LLM_NETWORK_ERROR") from None
    except Exception:
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
        except (TimeoutError, socket.timeout):
            raise LLMProviderError("OpenAI-compatible LLM request timed out.", code="LLM_TIMEOUT") from None
        except urllib.error.HTTPError as exc:
            if include_response_format and int(getattr(exc, "code", 0) or 0) == 400:
                continue
            raise _http_error(exc) from None
        except urllib.error.URLError:
            raise LLMProviderError("OpenAI-compatible LLM request failed before a response was received.", code="LLM_NETWORK_ERROR") from None
        except ValueError:
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
    except Exception:
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
    except Exception:
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
        "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        "params": params,
        "output": {"artifactTypes": ["table_json", "summary_md", "recipe_json"]},
    }
    return _single_step_plan(
        request,
        step,
        [{"name": "composition_summary.json", "type": "table_json", "fromStepId": "step_001"}],
    )


def _mock_composition_visual_plan(
    request: PlannerRequest,
    *,
    data_profile: DataProfile,
    tool_id: str,
    purpose: str,
    params: dict[str, Any],
    artifact_name: str,
    artifact_type: str = "plotly_json",
    artifact_types: list[str] | None = None,
) -> dict[str, Any]:
    output_types = artifact_types or ["plotly_json", "plotly_html", "summary_md", "recipe_json"]
    formula_column = params.get("formulaColumn") or _formula_column(data_profile)
    step = {
        "stepId": "step_001",
        "toolId": tool_id,
        "purpose": purpose,
        "reason": f"The request asks for composition analysis using {formula_column or 'the detected formula column'}.",
        "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
        "params": params,
        "output": {"artifactTypes": output_types},
    }
    expected = [{"name": artifact_name, "type": artifact_type, "fromStepId": "step_001"}]
    expected.extend(
        {"name": name, "type": artifact_type_name, "fromStepId": "step_001"}
        for name, artifact_type_name in (("summary.md", "summary_md"), ("recipe.json", "recipe_json"))
    )
    if "plotly_html" in output_types:
        expected.append({"name": artifact_name.replace(".json", ".html"), "type": "plotly_html", "fromStepId": "step_001"})
    return _single_step_plan(request, step, expected)


def _mock_structure_plan(
    request: PlannerRequest,
    *,
    data_profile: DataProfile,
    tool_id: str,
    purpose: str,
    params: dict[str, Any],
    artifact_name: str,
    artifact_type: str,
    artifact_types: list[str],
    extra_expected_artifacts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    step = {
        "stepId": "step_001",
        "toolId": tool_id,
        "purpose": purpose,
        "reason": _structure_reason(request, data_profile, tool_id),
        "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
        "params": params,
        "output": {"artifactTypes": artifact_types},
    }
    expected = [{"name": artifact_name, "type": artifact_type, "fromStepId": "step_001"}]
    expected.extend(extra_expected_artifacts or [])
    expected.extend(
        {"name": name, "type": artifact_type_name, "fromStepId": "step_001"}
        for name, artifact_type_name in (("summary.md", "summary_md"), ("recipe.json", "recipe_json"))
    )
    return _single_step_plan(request, step, expected)


def _should_generate_viewer_export_package(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.viewer_export_package") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    markers = (
        "viewer export package",
        "export package",
        "viewer package",
        "viewer_assets_manifest",
        "package this structure for future 3d viewer",
        "static viewer export",
    )
    return any(marker in prompt for marker in markers)


def _should_generate_brillouin_zone(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.brillouin_zone") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    unsupported = (
        "电子能带", "electronic band", "band structure",
        "phonon", "声子", "trajectory", "轨迹", "fermi", "monkhorst", "charge density",
        "电荷密度", "xrd", "crystalnn", "edit structure", "编辑结构", "dft",
        "magnetic brillouin", "surface brillouin", "surface bz", "磁性布里渊", "表面布里渊",
    )
    if any(marker in prompt for marker in unsupported):
        return False
    markers = (
        "first brillouin zone", "brillouin zone data", "brillouin zone json",
        "reciprocal lattice and high-symmetry path", "reciprocal lattice and high symmetry path",
        "standardized k-path", "standardized kpath", "crystal k-path", "crystal kpath",
        "第一布里渊区", "布里渊区数据", "倒易晶格和高对称路径", "高对称路径",
        "这个晶体的k路径", "这个晶体的 k 路径", "导出这个结构的brillouin zone数据",
        "interactive brillouin zone viewer", "brillouin zone interactively", "brillouin zone in 3d",
        "3d reciprocal lattice", "reciprocal axes and the high-symmetry path",
        "交互式布里渊区", "可旋转的第一布里渊区", "三维布里渊区", "3d查看倒易晶格", "3d 查看倒易晶格",
    )
    return any(marker in prompt for marker in markers)


def _should_generate_viewer_scene_metadata(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.viewer_scene_metadata") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    markers = (
        "viewer scene metadata",
        "viewer_scene",
        "viewer scene contract",
        "scene contract",
        "static structure viewer scene",
        "structure viewer metadata",
        "create viewer scene metadata",
        "build a static structure viewer scene contract",
    )
    return any(marker in prompt for marker in markers)


def _should_generate_viewer_scene(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.viewer_scene") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    deferred_markers = (
        "interactive",
        "live viewer",
        "webgl",
        "three.js",
        "threejs",
        "render with three",
        "rotatable",
        "可旋转",
        "真实 3d",
        "brillouin",
        "phonon",
        "trajectory",
        "animation",
        "animate",
    )
    if any(marker in prompt for marker in deferred_markers):
        return False
    markers = (
        "viewer_scene.v1",
        "viewer scene json",
        "viewer_scene json",
        "viewer_scene artifact",
        "viewer scene artifact",
        "inert viewer scene",
        "json scene data",
        "scene data for a future structure renderer",
        "导出这个晶体的 viewer scene 数据",
        "生成这个结构的 viewer scene json",
        "创建 viewer_scene.v1 artifact",
    )
    return any(marker in prompt for marker in markers)


def _should_generate_structure_viewer(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.viewer_3d") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    unsupported = (
        "trajectory", "animation", "animate", "phonon", "brillouin", "charge density",
        "spin density", "volumetric", "isosurface", "edit structure", "structure editing",
        "rietveld", "轨迹", "动画", "声子", "布里渊", "电荷密度", "编辑结构",
    )
    if any(marker in prompt for marker in unsupported):
        return False
    markers = (
        "3d viewer", "3d view", "in 3d", "structure viewer", "interactive 3d", "interactive view", "webgl",
        "render this crystal", "open an interactive 3d view", "三维查看器", "3d 查看器",
        "交互查看", "三维模型", "三维结构", "显示这个结构",
    )
    return any(marker in prompt for marker in markers)


def _canonical_viewer_scene_params() -> dict[str, Any]:
    return {
        "include_bonds": True,
        "bond_cutoff_angstrom": 3.0,
        "max_sites": 256,
        "max_bonds": 2048,
        "coordinate_basis": "cartesian_angstrom",
        "include_cartesian_positions": True,
        "include_fractional_positions": True,
        "cell_expansion": [1, 1, 1],
        "style_preset": "default",
        "camera_preset": "auto",
    }


def _should_generate_xrd(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.xrd") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    deferred_markers = (
        "rdf",
        "radial distribution",
        "coordination",
        "neighbor count",
        "3d viewer",
        "webgl",
        "brillouin",
        "phonon",
        "rietveld",
        "refinement",
        "experimental",
        "fitting",
        "peak broadening",
        "profile fitting",
    )
    if any(marker in prompt for marker in deferred_markers):
        return False
    markers = (
        "xrd",
        "x-ray diffraction",
        "x ray diffraction",
        "powder xrd",
        "powder diffraction",
        "diffraction peaks",
    )
    return any(marker in prompt for marker in markers)


def _should_generate_rdf(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.rdf") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    deferred_markers = (
        "xrd",
        "diffraction",
        "coordination",
        "neighbor count",
        "3d viewer",
        "webgl",
        "brillouin",
        "phonon",
        "pdf fitting",
        "experimental pdf",
        "neutron scattering",
        "rietveld",
        "refinement",
        "experimental",
        "fitting",
    )
    if any(marker in prompt for marker in deferred_markers):
        return False
    markers = (
        "rdf",
        "radial distribution",
        "pair distribution g(r)",
        "pair distribution",
        "g(r)",
        "径向分布函数",
    )
    return any(marker in prompt for marker in markers)


def _should_generate_coordination_hist(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.coordination_hist") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    deferred_markers = (
        "xrd",
        "diffraction",
        "rdf",
        "radial distribution",
        "pair distribution",
        "3d viewer",
        "webgl",
        "brillouin",
        "phonon",
        "voronoi",
        "crystalnn",
        "local environment classification",
        "chemical environment classification",
    )
    if any(marker in prompt for marker in deferred_markers):
        return False
    markers = (
        "coordination histogram",
        "coordination number histogram",
        "coordination number",
        "coordination distribution",
        "neighbor count",
        "count neighbors",
        "fixed cutoff",
        "配位数",
        "配位数直方图",
        "邻居数",
    )
    return any(marker in prompt for marker in markers)


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


def _should_generate_structure_spacegroup(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.spacegroup_summary") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    markers = ("space group", "spacegroup", "crystal system", "symmetry", "空间群", "晶系", "对称")
    return any(marker in prompt for marker in markers)


def _should_generate_structure_lattice(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.lattice_summary") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    if any(marker in prompt for marker in ("summarize", "summary", "basic", "基本信息", "总结")):
        return False
    markers = ("lattice", "cell", "volume", "angle", "晶格", "晶胞", "体积", "角度")
    return any(marker in prompt for marker in markers)


def _should_generate_structure_composition(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.composition_from_structure") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    structure_markers = ("structure", "cif", "poscar", "crystal", "结构", "晶体")
    composition_markers = ("composition", "formula", "element", "元素组成", "组成", "化学式")
    return any(marker in prompt for marker in structure_markers) and any(
        marker in prompt for marker in composition_markers
    )


def _should_generate_structure_preview(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.preview_metadata") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    markers = (
        "preview metadata",
        "preview",
        "metadata",
        "sites preview",
        "bounding box",
        "coordinates",
        "坐标范围",
        "预览",
        "元数据",
    )
    return any(marker in prompt for marker in markers) or _is_3d_viewer_request(prompt)


def _should_generate_structure_summary(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.summary") or not _has_structure_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    if _is_3d_viewer_request(prompt):
        return False
    markers = ("structure", "cif", "poscar", "crystal", "结构", "晶体结构", "基本信息", "原子数")
    return any(marker in prompt for marker in markers)


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


def _should_generate_ptable_heatmap(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "composition.ptable_heatmap") or not _formula_column(data_profile):
        return False
    prompt = request.user_prompt.lower()
    markers = ("periodic table", "ptable", "periodic heatmap", "周期表", "周期表热力图")
    return any(marker in prompt for marker in markers)


def _should_generate_elements_hist(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "composition.elements_hist") or not _formula_column(data_profile):
        return False
    prompt = request.user_prompt.lower()
    markers = (
        "elements histogram",
        "element histogram",
        "element frequency",
        "element distribution",
        "composition distribution",
        "元素分布",
        "元素出现频率",
        "元素直方图",
    )
    return any(marker in prompt for marker in markers)


def _should_generate_chem_sys_sunburst(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "composition.chem_sys_sunburst") or not _formula_column(data_profile):
        return False
    prompt = request.user_prompt.lower()
    markers = ("sunburst", "chemical system sunburst", "chem sys sunburst", "化学体系 sunburst", "sunburst 图")
    return any(marker in prompt for marker in markers)


def _should_generate_chem_sys_treemap(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "composition.chem_sys_treemap") or not _formula_column(data_profile):
        return False
    prompt = request.user_prompt.lower()
    markers = (
        "chemical system treemap",
        "chem sys treemap",
        "chemical system distribution",
        "chem_sys",
        "treemap",
        "化学体系分布",
        "化学体系 treemap",
    )
    return any(marker in prompt for marker in markers)


def _should_generate_formula_statistics(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "composition.formula_statistics") or not _formula_column(data_profile):
        return False
    prompt = request.user_prompt.lower()
    markers = (
        "formula statistics",
        "formula stats",
        "formula summary",
        "chemical formula statistics",
        "化学式统计",
        "formula 基础信息",
    )
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


def _has_structure_input(data_profile: DataProfile) -> bool:
    summary = getattr(data_profile, "structureSummary", None)
    if isinstance(summary, dict):
        try:
            if int(summary.get("nStructures") or summary.get("structureCount") or 0) > 0:
                return True
        except (TypeError, ValueError):
            pass
    for obj in getattr(data_profile, "objects", None) or []:
        if isinstance(obj, dict):
            object_type = str(obj.get("objectType") or obj.get("object_type") or "").lower()
            if "structure" in object_type:
                return True
    dataset_type = str(getattr(data_profile, "datasetType", "") or "").lower()
    return "structure" in dataset_type or "cif" in dataset_type or "poscar" in dataset_type


def _has_phonon_band_input(data_profile: DataProfile) -> bool:
    for obj in getattr(data_profile, "objects", None) or []:
        if isinstance(obj, dict):
            object_type = str(obj.get("objectType") or obj.get("object_type") or "").lower()
            if object_type == "phononband":
                return True
    return "phononband" in str(getattr(data_profile, "datasetType", "") or "").lower()


def _has_phonon_dos_input(data_profile: DataProfile) -> bool:
    for obj in getattr(data_profile, "objects", None) or []:
        if isinstance(obj, dict):
            object_type = str(obj.get("objectType") or obj.get("object_type") or "").lower()
            if object_type == "phonondos":
                return True
    return "phonondos" in str(getattr(data_profile, "datasetType", "") or "").lower()


def _phonon_profile_object(data_profile: DataProfile, object_type: str) -> dict[str, Any] | None:
    for item in getattr(data_profile, "objects", None) or []:
        if isinstance(item, dict) and str(item.get("objectType") or item.get("object_type") or "") == object_type:
            return item
    return None


def _should_generate_phonon_animation(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "phonon.animation"):
        return False
    structure = _phonon_profile_object(data_profile, "Structure")
    band = _phonon_profile_object(data_profile, "PhononBand")
    eigenvectors = _phonon_profile_object(data_profile, "PhononEigenvector")
    mode_id = eigenvectors.get("modeId") if eigenvectors else None
    if structure is None or band is None or eigenvectors is None or not isinstance(mode_id, str) or len(mode_id) != 64:
        return False
    prompt = request.user_prompt.lower()
    unsupported = (
        "calculate phonon", "run phonopy", "force constants", "thermal conductivity", "heat capacity",
        "raman", "infrared", "neutron", "molecular dynamics", "md trajectory", "brillouin",
        "charge density", "xrd", "crystalnn", "edit structure", "mp4", "gif",
        "计算声子", "力常数", "热导率", "热容", "分子动力学轨迹", "布里渊区", "编辑结构",
    )
    if any(marker in prompt for marker in unsupported):
        return False
    markers = (
        "animate the selected phonon mode", "visualize this phonon eigenmode", "phonon mode animation",
        "open a phonon mode animation", "show atomic displacements for this q-point",
        "播放这个声子模式", "显示这个q点的原子振动", "声子模式动画", "动画展示这个虚频模式",
    )
    return any(marker in prompt for marker in markers)


def _mock_phonon_animation_plan(request: PlannerRequest, data_profile: DataProfile) -> dict[str, Any]:
    structure = _phonon_profile_object(data_profile, "Structure") or {}
    band = _phonon_profile_object(data_profile, "PhononBand") or {}
    eigenvectors = _phonon_profile_object(data_profile, "PhononEigenvector") or {}
    mode_id = str(eigenvectors["modeId"])
    artifact_types = ["phonon_animation_json", "phonon_animation_summary_json", "phonon_animation_manifest_json", "recipe_json"]
    step = {
        "stepId": "step_001", "toolId": "phonon.animation",
        "purpose": "Build a bounded declarative visualization package for one validated phonon eigenmode.",
        "reason": "The request explicitly asks to visualize an available canonical phonon eigenvector.",
        "inputRefs": [
            {"refType": "normalized_object", "ref": structure.get("id") or structure.get("ref") or "structure", "fieldRole": "structure", "objectType": "Structure"},
            {"refType": "artifact", "ref": band.get("id") or band.get("ref") or "phonon_band", "fieldRole": "band", "objectType": "PhononBand"},
            {"refType": "artifact", "ref": eigenvectors.get("id") or eigenvectors.get("ref") or "phonon_eigenvectors", "fieldRole": "eigenvectors", "objectType": "PhononEigenvector"},
        ],
        "params": {"mode_id": mode_id, "display_scale": 0.15, "initial_phase_radians": 0.0, "playback_cycles_per_second": 0.5, "autoplay": False, "loop": True, "supercell_mode": "auto", "supercell": [1, 1, 1], "show_vectors": True, "show_trails": False, "trail_length": 12, "show_bonds": True, "show_unit_cell": True, "show_axes": True, "representation": "ball_and_stick"},
        "output": {"artifactTypes": artifact_types},
    }
    expected = [
        {"name": "phonon_animation.json", "type": "phonon_animation_json", "fromStepId": "step_001"},
        {"name": "phonon_animation_summary.json", "type": "phonon_animation_summary_json", "fromStepId": "step_001"},
        {"name": "phonon_animation_manifest.json", "type": "phonon_animation_manifest_json", "fromStepId": "step_001"},
        {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
    ]
    return _single_step_plan(request, step, expected)


def _should_generate_phonon_band_dos(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "phonon.band_dos") or not _has_phonon_band_input(data_profile) or not _has_phonon_dos_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    unsupported = (
        "eigenvector", "animate", "animation", "displacement", "thermal", "free energy", "entropy",
        "heat capacity", "gruneisen", "calculate phonon", "run phonopy", "force constants", "brillouin",
        "volumetric", "isosurface", "trajectory", "phonon movie", "phonon video",
        "\u672c\u5f81\u5411\u91cf", "\u52a8\u753b", "\u4f4d\u79fb\u77e2\u91cf", "\u8ba1\u7b97\u58f0\u5b50", "\u70ed\u5bb9", "\u81ea\u7531\u80fd",
    )
    if any(marker in prompt for marker in unsupported):
        return False
    markers = (
        "band dos", "band + dos", "band and dos", "combined band", "combined phonon",
        "phonon band with dos", "phonon bands with dos", "shared frequency axis",
        "\u8054\u5408\u663e\u793a\u58f0\u5b50\u80fd\u5e26\u548cdos",
        "\u58f0\u5b50\u80fd\u5e26\u548c\u58f0\u5b50\u6001\u5bc6\u5ea6",
        "\u628a phonon band \u548c phonon dos \u653e\u5728\u4e00\u5f20\u56fe",
        "\u5171\u4eab\u9891\u7387\u8f74",
    )
    return any(marker in prompt for marker in markers)


def _mock_phonon_band_dos_plan(request: PlannerRequest, data_profile: DataProfile) -> dict[str, Any]:
    artifact_types = [
        "phonon_band_dos_json", "phonon_summary_json", "phonon_compatibility_json", "plotly_json",
        "table_json", "phonon_manifest_json", "recipe_json",
    ]
    step = {
        "stepId": "step_001",
        "toolId": "phonon.band_dos",
        "purpose": "Validate and compose approved static phonon band and DOS artifacts on one shared frequency axis.",
        "reason": "The request asks for a combined band-left/DOS-right phonon view from compatible canonical artifacts.",
        "inputRefs": [
            {"refType": "artifact", "ref": _phonon_object_ref(data_profile, "PhononBand", "phonon_band"), "fieldRole": "band", "objectType": "PhononBand"},
            {"refType": "artifact", "ref": _phonon_object_ref(data_profile, "PhononDos", "phonon_dos"), "fieldRole": "dos", "objectType": "PhononDos"},
        ],
        "params": {"selected_projection_ids": [], "domain_policy": "union", "max_table_rows": 200, "layout": "band_left_dos_right"},
        "output": {"artifactTypes": artifact_types},
    }
    expected = [
        {"name": "phonon_band_dos.json", "type": "phonon_band_dos_json", "fromStepId": "step_001"},
        {"name": "phonon_band_dos_summary.json", "type": "phonon_summary_json", "fromStepId": "step_001"},
        {"name": "phonon_band_dos_compatibility_report.json", "type": "phonon_compatibility_json", "fromStepId": "step_001"},
        {"name": "phonon_band_dos_plot.json", "type": "plotly_json", "fromStepId": "step_001"},
        {"name": "phonon_band_dos_table.json", "type": "table_json", "fromStepId": "step_001"},
        {"name": "phonon_band_dos_manifest.json", "type": "phonon_manifest_json", "fromStepId": "step_001"},
        {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
    ]
    return _single_step_plan(request, step, expected)


def _phonon_object_ref(data_profile: DataProfile, object_type: str, fallback: str) -> str:
    for item in getattr(data_profile, "objects", None) or []:
        if isinstance(item, dict) and str(item.get("objectType") or item.get("object_type") or "") == object_type:
            value = item.get("id") or item.get("ref")
            if isinstance(value, str) and value:
                return value
    return fallback


def _should_generate_phonon_dos(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "phonon.dos") or not _has_phonon_dos_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    unsupported = (
        "band dos", "band + dos", "band and dos", "combined", "eigenvector", "animate", "animation",
        "displacement", "thermal", "free energy", "entropy", "heat capacity", "gruneisen",
        "calculate phonon", "run phonopy", "force constants", "brillouin", "volumetric",
        "声子能带和态密度", "联合", "声子动画", "计算声子", "热容", "自由能",
    )
    if any(marker in prompt for marker in unsupported):
        return False
    markers = (
        "phonon dos", "phonon density of states", "total phonon dos", "projected phonon dos",
        "imaginary-frequency dos", "声子态密度", "总声子态密度", "分波声子态密度",
    )
    return any(marker in prompt for marker in markers)


def _mock_phonon_dos_plan(request: PlannerRequest) -> dict[str, Any]:
    artifact_types = [
        "phonon_dos_json", "phonon_summary_json", "phonon_report_json", "phonon_manifest_json",
        "plotly_json", "table_json", "recipe_json",
    ]
    step = {
        "stepId": "step_001",
        "toolId": "phonon.dos",
        "purpose": "Normalize and visualize an approved static phonon density-of-states source.",
        "reason": "The request asks for a static phonon DOS plot from an available PhononDos object.",
        "inputRefs": [{"refType": "normalized_object", "ref": "phonon_dos", "objectType": "PhononDos"}],
        "params": {
            "source_format": "auto", "source_frequency_unit": "terahertz", "source_normalization": "total_modes",
            "max_table_rows": 20000, "max_plot_values": 100000, "plot_kind": "line",
        },
        "output": {"artifactTypes": artifact_types},
    }
    expected = [
        {"name": "phonon_dos.json", "type": "phonon_dos_json", "fromStepId": "step_001"},
        {"name": "phonon_dos_summary.json", "type": "phonon_summary_json", "fromStepId": "step_001"},
        {"name": "phonon_dos_parse_report.json", "type": "phonon_report_json", "fromStepId": "step_001"},
        {"name": "phonon_manifest.json", "type": "phonon_manifest_json", "fromStepId": "step_001"},
        {"name": "phonon_dos_plot.json", "type": "plotly_json", "fromStepId": "step_001"},
        {"name": "phonon_dos_table.json", "type": "table_json", "fromStepId": "step_001"},
        {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
    ]
    return _single_step_plan(request, step, expected)


def _should_generate_phonon_band(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "phonon.band") or not _has_phonon_band_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    unsupported = (
        "dos", "density of states", "band dos", "eigenvector", "animate", "animation",
        "displacement", "thermal", "free energy", "entropy", "heat capacity", "gruneisen",
        "calculate phonon", "run phonopy", "force constants", "brillouin", "volumetric",
        "声子态密度", "声子动画", "计算声子", "热容", "自由能",
    )
    if any(marker in prompt for marker in unsupported):
        return False
    markers = (
        "phonon band", "phonon dispersion", "plot the phonon bands", "show phonon bands",
        "声子能带", "声子色散", "绘制声子能带", "显示声子能带",
    )
    return any(marker in prompt for marker in markers)


def _mock_phonon_band_plan(request: PlannerRequest) -> dict[str, Any]:
    artifact_types = [
        "phonon_band_json", "phonon_summary_json", "phonon_report_json", "phonon_manifest_json",
        "plotly_json", "table_json", "recipe_json",
    ]
    step = {
        "stepId": "step_001",
        "toolId": "phonon.band",
        "purpose": "Normalize and visualize an approved static phonon band source.",
        "reason": "The request asks for a static phonon band plot from an available PhononBand object.",
        "inputRefs": [{"refType": "normalized_object", "ref": "phonon_band", "objectType": "PhononBand"}],
        "params": {"source_format": "auto", "source_frequency_unit": "terahertz", "max_table_rows": 20000, "plot_kind": "line"},
        "output": {"artifactTypes": artifact_types},
    }
    expected = [
        {"name": "phonon_band.json", "type": "phonon_band_json", "fromStepId": "step_001"},
        {"name": "phonon_summary.json", "type": "phonon_summary_json", "fromStepId": "step_001"},
        {"name": "phonon_band_parse_report.json", "type": "phonon_report_json", "fromStepId": "step_001"},
        {"name": "phonon_manifest.json", "type": "phonon_manifest_json", "fromStepId": "step_001"},
        {"name": "phonon_band_plot.json", "type": "plotly_json", "fromStepId": "step_001"},
        {"name": "phonon_band_table.json", "type": "table_json", "fromStepId": "step_001"},
        {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
    ]
    return _single_step_plan(request, step, expected)


def _has_trajectory_input(data_profile: DataProfile) -> bool:
    summary = getattr(data_profile, "trajectorySummary", None)
    if isinstance(summary, dict):
        try:
            if int(summary.get("frames") or summary.get("frameCount") or 0) > 0:
                return True
        except (TypeError, ValueError):
            pass
    for obj in getattr(data_profile, "objects", None) or []:
        if isinstance(obj, dict) and str(obj.get("objectType") or obj.get("object_type") or "").lower() == "trajectory":
            return True
    return "trajectory" in str(getattr(data_profile, "datasetType", "") or "").lower()


def _should_generate_trajectory_viewer(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.trajectory_viewer") or not _has_trajectory_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    unsupported = (
        "rdf", "radial distribution", "diffusion", "msd", "mean squared", "vacf",
        "velocity distribution", "infer bond", "changing bond", "dynamic bond",
        "edit frame", "trajectory editing", "trim", "merge", "cluster", "compare",
        "video", "gif", "mp4", "扩散", "径向分布", "动态键", "编辑", "裁剪轨迹",
    )
    if any(marker in prompt for marker in unsupported):
        return False
    markers = (
        "play this molecular dynamics trajectory", "play this trajectory", "trajectory viewer",
        "inspect this relaxation trajectory frame by frame", "frame by frame",
        "show the atomic motion", "atomic motion", "view this trajectory", "animate this trajectory",
        "播放这个轨迹", "逐帧查看", "查看这个轨迹", "原子运动", "轨迹查看器",
    )
    return any(marker in prompt for marker in markers)


def _mock_trajectory_viewer_plan(request: PlannerRequest) -> dict[str, Any]:
    artifact_types = ["trajectory_json", "trajectory_summary_json", "trajectory_report_json", "trajectory_manifest_json"]
    step = {
        "stepId": "step_001",
        "toolId": "structure.trajectory_viewer",
        "purpose": "Prepare validated trajectory artifacts for bounded interactive playback.",
        "reason": "The request asks to inspect a validated trajectory with the formal trajectory viewer.",
        "inputRefs": [{"refType": "normalized_object", "ref": "trajectory", "objectType": "Trajectory"}],
        "params": {"playbackSpeed": 1, "loop": False, "supercell": [1, 1, 1], "showCell": True, "clipping": False, "performanceMode": "auto", "bondMode": "none"},
        "output": {"artifactTypes": artifact_types},
    }
    expected = [
        {"name": "trajectory.json", "type": "trajectory_json", "fromStepId": "step_001"},
        {"name": "trajectory_summary.json", "type": "trajectory_summary_json", "fromStepId": "step_001"},
        {"name": "trajectory_parse_report.json", "type": "trajectory_report_json", "fromStepId": "step_001"},
        {"name": "trajectory_manifest.json", "type": "trajectory_manifest_json", "fromStepId": "step_001"},
    ]
    return _single_step_plan(request, step, expected)


def _is_3d_viewer_request(prompt: str) -> bool:
    markers = ("3d", "3-d", "viewer", "render", "渲染", "三维", "3维", "structure viewer")
    return any(marker in prompt for marker in markers)


def _structure_reason(request: PlannerRequest, data_profile: DataProfile, tool_id: str) -> str:
    count = 0
    summary = getattr(data_profile, "structureSummary", None)
    if isinstance(summary, dict):
        try:
            count = int(summary.get("nStructures") or summary.get("structureCount") or 0)
        except (TypeError, ValueError):
            count = 0
    base = f"The request asks for lightweight structure analysis using {count or 'the available'} structure input(s)."
    if tool_id == "structure.preview_metadata" and _is_3d_viewer_request(request.user_prompt.lower()):
        return base + " Full 3D rendering is future scope; this plan only creates preview metadata."
    return base


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


def _composition_params(data_profile: DataProfile, defaults: dict[str, Any] | None = None) -> dict[str, Any]:
    params = dict(defaults or {})
    if formula_column := _formula_column(data_profile):
        params.setdefault("formulaColumn", formula_column)
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
