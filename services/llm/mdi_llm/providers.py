"""LLM provider abstraction and implementations for Phase 7.

All providers conform to the LLMPlannerProvider protocol.  No real API key
is read at import time; keys are resolved at call time from environment
variables or injected configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import ipaddress
import json
import os
import re
import socket
from time import perf_counter
from typing import Any, Protocol
import urllib.error
import urllib.parse
import urllib.request

from mdi_schemas import DataProfile, RegisteredTool

from .redaction import redact_credential_values


DEEPSEEK_PROVIDER_NAME = "deepseek"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_DEFAULT_MODEL = "deepseek-v4-flash"
DEEPSEEK_ALLOWED_MODELS = frozenset({DEEPSEEK_DEFAULT_MODEL, "deepseek-v4-pro"})
DEEPSEEK_ALLOWED_PURPOSES = frozenset(
    {
        "INTENT_EXTRACTION",
        "CLARIFICATION_RESOLUTION",
        "CAPABILITY_PLAN_SELECTION",
        "MULTI_TOOL_COMPOSITION",
        "GROUNDED_INTERPRETATION",
        "PROVIDER_CONNECTION_TEST",
    }
)
DEEPSEEK_MAX_OUTPUT_TOKENS = 8192
DEEPSEEK_MAX_TIMEOUT_SECONDS = 120.0
DEEPSEEK_MAX_PROMPT_BYTES = 524_288


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
        materials_ml_tool = _select_materials_ml_tool(request, tools, data_profile)
        if self.fixed_plan is not None:
            plan = dict(self.fixed_plan)
        elif _should_generate_composition_space(request, tools, data_profile):
            plan = _mock_composition_space_plan(request, data_profile)
        elif materials_ml_tool is not None:
            plan = _mock_materials_ml_plan(request, data_profile, materials_ml_tool)
        elif _should_generate_ambiguous_ml_diagnostic(request, tools, data_profile):
            plan = _mock_dataset_materials_explorer_plan(request, data_profile)
            plan["steps"][0]["purpose"] = "Expose ambiguous Profile 2.0 model semantics without selecting a target or prediction column."
            plan["steps"][0]["reason"] = "Material Data Profile 2.0 marks the requested ML capability ambiguous; only the diagnostic dataset product is safe to execute."
        elif _should_generate_dataset_materials_explorer(request, tools, data_profile):
            plan = _mock_dataset_materials_explorer_plan(request, data_profile)
        elif _should_generate_band_bz_link(request, tools, data_profile):
            plan = _mock_band_bz_link_plan(request, data_profile)
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
        elif _should_generate_volumetric_data(request, tools, data_profile):
            plan = _mock_volumetric_data_plan(request)
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
        elif experimental_xrd_tools := _select_experimental_xrd_tools(request, tools, data_profile):
            plan = _mock_experimental_xrd_plan(request, data_profile, experimental_xrd_tools)
        elif local_environment_tools := _select_local_environment_tools(request, tools, data_profile):
            plan = _mock_local_environment_plan(request, data_profile, local_environment_tools)
        elif coordination_tools := _select_coordination_nn_tools(request, tools, data_profile):
            plan = _mock_coordination_nn_plan(request, data_profile, coordination_tools)
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
    """Historical OpenAI-compatible provider retained for fake-test compatibility.

    Phase 10L-5 forbids this class from making a real network request. Existing
    tests and historical replay may inject a bounded fake transport; new live
    execution must use :class:`DeepSeekProvider`.
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
        from .planner_prompt import build_planner_prompt
        system_prompt, user_prompt_str = build_planner_prompt(request, tools=tools, data_profile=data_profile)
        return self.complete_json(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_str},
            ],
            user_config=user_config,
        )

    def complete_json(
        self,
        *,
        messages: list[dict[str, str]],
        user_config: PlannerUserConfig | None = None,
        purpose: str | None = None,
    ) -> PlannerRawResponse:
        """Use an injected fake transport for historical deterministic replay."""
        if self._transport is None:
            raise LLMProviderError(
                "New real LLM calls must use the DeepSeek provider.",
                code="PROVIDER_NOT_ALLOWED",
            )
        config = user_config or PlannerUserConfig()
        resolved = _resolve_openai_config(config, prefer_config=user_config is not None)
        response = _call_fake_transport(
            self._transport,
            model=resolved["model"],
            messages=messages,
            temperature=resolved["temperature"],
            max_tokens=resolved["max_tokens"],
            timeout_seconds=resolved["timeout_seconds"],
            response_format={"type": "json_object"},
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


class DeepSeekProvider:
    """The sole provider authorized for new real LLM calls.

    Live configuration is intentionally non-extensible: the endpoint is fixed,
    the key comes only from ``DEEPSEEK_KEY``, and the model and purpose are
    bounded allowlists. An injected transport is a fake/offline test path and
    never reads a key.
    """

    def __init__(self, *, transport: Any = None, urlopen: Any = None) -> None:
        self._transport = transport
        self._urlopen = urlopen
        self._call_audit: list[dict[str, Any]] = []

    def generate_plan(
        self,
        request: PlannerRequest,
        *,
        tools: list[RegisteredTool],
        data_profile: DataProfile,
        user_config: PlannerUserConfig | None = None,
    ) -> PlannerRawResponse:
        from .planner_prompt import build_planner_prompt

        system_prompt, user_prompt_str = build_planner_prompt(request, tools=tools, data_profile=data_profile)
        return self.complete_json(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_str},
            ],
            user_config=user_config,
            purpose="CAPABILITY_PLAN_SELECTION",
        )

    def complete_json(
        self,
        *,
        messages: list[dict[str, str]],
        user_config: PlannerUserConfig | None = None,
        purpose: str,
    ) -> PlannerRawResponse:
        resolved = _resolve_deepseek_config(user_config, fake=self._transport is not None, purpose=purpose)
        started = perf_counter()
        safe_messages = [
            {
                "role": str(message.get("role", "user")),
                "content": redact_credential_values(str(message.get("content", ""))),
            }
            for message in messages
        ]
        prompt_bytes = json.dumps(
            safe_messages,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(prompt_bytes) > DEEPSEEK_MAX_PROMPT_BYTES:
            raise LLMProviderError(
                "DeepSeek prompt exceeds the bounded provider payload.",
                code="DEEPSEEK_PROMPT_TOO_LARGE",
            )
        try:
            if self._transport is not None:
                response = _call_fake_transport(
                    self._transport,
                    model=resolved["model"],
                    messages=safe_messages,
                    temperature=0.0,
                    max_tokens=resolved["max_tokens"],
                    timeout_seconds=resolved["timeout_seconds"],
                    response_format={"type": "json_object"},
                )
            else:
                response = _post_deepseek_completion(
                    api_key=resolved["api_key"],
                    model=resolved["model"],
                    messages=safe_messages,
                    max_tokens=resolved["max_tokens"],
                    timeout_seconds=resolved["timeout_seconds"],
                    urlopen=self._urlopen or urllib.request.urlopen,
                )
        except LLMProviderError as exc:
            deepseek_error = _as_deepseek_error(exc)
            self._record_call(
                purpose=purpose,
                model=resolved["model"],
                prompt_bytes=prompt_bytes,
                response=None,
                elapsed_ms=(perf_counter() - started) * 1000,
                outcome=deepseek_error.code,
            )
            raise deepseek_error from None

        try:
            choice = _first_choice(response)
            content = _choice_content(choice)
            if not isinstance(content, str):
                raise LLMProviderError(
                    "DeepSeek response content was not strict JSON text.",
                    code="DEEPSEEK_RESPONSE_INVALID",
                )
            parsed = _strict_json_object(content, error_code="DEEPSEEK_RESPONSE_INVALID")
        except LLMProviderError as exc:
            response_error = (
                exc
                if exc.code == "DEEPSEEK_RESPONSE_INVALID"
                else LLMProviderError(
                    "DeepSeek response envelope was invalid.",
                    code="DEEPSEEK_RESPONSE_INVALID",
                )
            )
            self._record_call(
                purpose=purpose,
                model=resolved["model"],
                prompt_bytes=prompt_bytes,
                response=response,
                elapsed_ms=(perf_counter() - started) * 1000,
                outcome=response_error.code,
            )
            raise response_error from None
        self._record_call(
            purpose=purpose,
            model=resolved["model"],
            prompt_bytes=prompt_bytes,
            response=response,
            elapsed_ms=(perf_counter() - started) * 1000,
            outcome="SUCCESS",
        )
        return PlannerRawResponse(
            raw_json=parsed,
            raw_text=content,
            model=resolved["model"],
            finish_reason=choice.get("finish_reason"),
        )

    @property
    def meta(self) -> _ProviderMeta:
        model = os.environ.get("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL
        return _ProviderMeta(name=DEEPSEEK_PROVIDER_NAME, model=model)

    @property
    def call_audit(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(item) for item in self._call_audit)

    def _record_call(
        self,
        *,
        purpose: str,
        model: str,
        prompt_bytes: bytes,
        response: dict[str, Any] | None,
        elapsed_ms: float,
        outcome: str,
    ) -> None:
        usage = response.get("usage") if isinstance(response, dict) else None
        prompt_tokens = usage.get("prompt_tokens") if isinstance(usage, dict) else None
        completion_tokens = usage.get("completion_tokens") if isinstance(usage, dict) else None
        estimated = not isinstance(prompt_tokens, int) or not isinstance(completion_tokens, int)
        prompt_tokens = prompt_tokens if isinstance(prompt_tokens, int) else max(1, (len(prompt_bytes) + 3) // 4)
        response_bytes = (
            json.dumps(response, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            if response is not None
            else b""
        )
        completion_tokens = (
            completion_tokens if isinstance(completion_tokens, int) else ((len(response_bytes) + 3) // 4 if response_bytes else 0)
        )
        finish_reason = None
        response_content_bytes = 0
        if isinstance(response, dict):
            choices = response.get("choices")
            if isinstance(choices, list) and choices and isinstance(choices[0], dict):
                finish_reason = choices[0].get("finish_reason")
                message = choices[0].get("message")
                if isinstance(message, dict) and isinstance(message.get("content"), str):
                    response_content_bytes = len(message["content"].encode("utf-8"))
        self._call_audit.append({
            "purpose": purpose,
            "model": model,
            "realCall": self._transport is None and self._urlopen is None,
            "promptHash": sha256(prompt_bytes).hexdigest(),
            "responseHash": sha256(response_bytes).hexdigest() if response_bytes else None,
            "promptBytes": len(prompt_bytes),
            "responseBytes": len(response_bytes),
            "responseContentBytes": response_content_bytes,
            "finishReason": finish_reason,
            "tokenUsage": {
                "promptTokens": prompt_tokens,
                "completionTokens": completion_tokens,
                "totalTokens": prompt_tokens + completion_tokens,
                "estimated": estimated,
            },
            "elapsedMs": round(elapsed_ms, 3),
            "outcome": outcome,
        })


def _resolve_deepseek_config(
    config: PlannerUserConfig | None,
    *,
    fake: bool,
    purpose: str,
) -> dict[str, Any]:
    if purpose not in DEEPSEEK_ALLOWED_PURPOSES:
        raise LLMProviderError(
            "The requested LLM call purpose is not allowed.",
            code="LLM_CALL_PURPOSE_NOT_ALLOWED",
        )
    if config is not None and (config.api_key or config.base_url):
        raise LLMProviderError(
            "DeepSeek credentials and endpoint cannot be supplied per request.",
            code="DEEPSEEK_CONFIGURATION_NOT_ALLOWED",
        )
    if config is not None and config.provider != DEEPSEEK_PROVIDER_NAME:
        raise LLMProviderError(
            "Only the DeepSeek provider is allowed for this request.",
            code="PROVIDER_NOT_ALLOWED",
        )
    requested_model = config.model if config is not None and config.model else None
    model = requested_model or os.environ.get("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL
    if model not in DEEPSEEK_ALLOWED_MODELS:
        raise LLMProviderError(
            "The requested DeepSeek model is not allowed.",
            code="DEEPSEEK_MODEL_NOT_ALLOWED",
        )
    max_tokens = min(
        DEEPSEEK_MAX_OUTPUT_TOKENS,
        max(1, int(config.max_tokens if config is not None else DEEPSEEK_MAX_OUTPUT_TOKENS)),
    )
    timeout_seconds = min(
        DEEPSEEK_MAX_TIMEOUT_SECONDS,
        max(1.0, float(config.timeout_seconds if config is not None else DEEPSEEK_MAX_TIMEOUT_SECONDS)),
    )
    api_key = None if fake else os.environ.get("DEEPSEEK_KEY")
    if not fake and not api_key:
        raise LLMProviderError(
            "DeepSeek is not configured.",
            code="DEEPSEEK_NOT_CONFIGURED",
        )
    return {
        "api_key": api_key,
        "base_url": DEEPSEEK_BASE_URL,
        "model": model,
        "max_tokens": max_tokens,
        "timeout_seconds": timeout_seconds,
        "purpose": purpose,
    }


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
    base_url = _validated_llm_base_url(base_url)
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


def _post_deepseek_completion(
    *,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    timeout_seconds: float,
    urlopen: Any = urllib.request.urlopen,
) -> dict[str, Any]:
    """Send one bounded strict-JSON request to the fixed DeepSeek endpoint."""
    url = f"{DEEPSEEK_BASE_URL}/chat/completions"
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
            "thinking": {"type": "disabled"},
        },
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read(1_048_577)
    except (TimeoutError, socket.timeout):
        raise LLMProviderError("DeepSeek request timed out.", code="DEEPSEEK_TIMEOUT") from None
    except urllib.error.HTTPError as exc:
        raise _http_error(exc) from None
    except urllib.error.URLError:
        raise LLMProviderError("DeepSeek request failed before a response was received.", code="DEEPSEEK_PROVIDER_FAILED") from None
    if len(payload) > 1_048_576:
        raise LLMProviderError("DeepSeek response exceeded the bounded byte limit.", code="DEEPSEEK_RESPONSE_INVALID")
    try:
        parsed = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_object_keys,
            parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite number")),
        )
    except (UnicodeDecodeError, ValueError, TypeError):
        raise LLMProviderError("DeepSeek response envelope was not strict JSON.", code="DEEPSEEK_RESPONSE_INVALID") from None
    if not isinstance(parsed, dict):
        raise LLMProviderError("DeepSeek response envelope was not a JSON object.", code="DEEPSEEK_RESPONSE_INVALID")
    return parsed


def _strict_json_object(raw: str, *, error_code: str) -> dict[str, Any]:
    if not isinstance(raw, str) or raw != raw.strip() or raw.startswith("```") or len(raw.encode("utf-8")) > 524_288:
        raise LLMProviderError("Provider output must be one bounded bare JSON object.", code=error_code)
    try:
        decoder = json.JSONDecoder(
            object_pairs_hook=_reject_duplicate_object_keys,
            parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite number")),
        )
        value, end = decoder.raw_decode(raw)
    except (ValueError, TypeError):
        raise LLMProviderError("Provider output was not strict JSON.", code=error_code) from None
    if end != len(raw) or not isinstance(value, dict):
        raise LLMProviderError("Provider output must contain exactly one JSON object.", code=error_code)
    return value


def _reject_duplicate_object_keys(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _as_deepseek_error(error: LLMProviderError) -> LLMProviderError:
    if error.code in {
        "DEEPSEEK_NOT_CONFIGURED",
        "DEEPSEEK_CONFIGURATION_NOT_ALLOWED",
        "DEEPSEEK_MODEL_NOT_ALLOWED",
        "DEEPSEEK_RESPONSE_INVALID",
        "DEEPSEEK_TIMEOUT",
        "LLM_CALL_PURPOSE_NOT_ALLOWED",
    }:
        return error
    if error.status_code == 401:
        return LLMProviderError("DeepSeek authentication failed.", code="DEEPSEEK_AUTH_FAILED", status_code=401)
    if error.status_code == 429:
        return LLMProviderError("DeepSeek rate limit was reached.", code="DEEPSEEK_RATE_LIMITED", status_code=429)
    if error.status_code and error.status_code >= 500:
        return LLMProviderError("DeepSeek provider failed.", code="DEEPSEEK_PROVIDER_FAILED", status_code=error.status_code)
    if error.code == "LLM_TIMEOUT":
        return LLMProviderError("DeepSeek request timed out.", code="DEEPSEEK_TIMEOUT")
    return LLMProviderError("DeepSeek provider failed.", code="DEEPSEEK_PROVIDER_FAILED", status_code=error.status_code)


_DEFAULT_ALLOWED_LLM_BASE_URLS = frozenset(
    {
        "https://api.openai.com/v1",
        "https://api.deepseek.com/v1",
        "https://generativelanguage.googleapis.com/v1beta/openai",
    }
)


def _validated_llm_base_url(base_url: str) -> str:
    """Return an exact server-approved HTTPS provider endpoint."""
    normalized = _normalize_llm_base_url(base_url)
    allowed = set(_DEFAULT_ALLOWED_LLM_BASE_URLS)
    for name in ("MDI_LLM_BASE_URL", "OPENAI_BASE_URL"):
        configured = os.environ.get(name)
        if configured:
            allowed.add(_normalize_llm_base_url(configured))
    for configured in (os.environ.get("MDI_LLM_ALLOWED_BASE_URLS") or "").split(","):
        if configured.strip():
            allowed.add(_normalize_llm_base_url(configured.strip()))
    if normalized not in allowed:
        raise LLMProviderError(
            "OpenAI-compatible LLM endpoint is not approved by server configuration.",
            code="LLM_BASE_URL_NOT_ALLOWED",
        )
    return normalized


def _normalize_llm_base_url(base_url: str) -> str:
    try:
        parsed = urllib.parse.urlsplit(base_url)
        port = parsed.port
    except (TypeError, ValueError):
        raise LLMProviderError("OpenAI-compatible LLM endpoint is invalid.", code="LLM_BASE_URL_NOT_ALLOWED") from None
    if (
        parsed.scheme.lower() != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise LLMProviderError(
            "OpenAI-compatible LLM endpoint must be an approved HTTPS base URL.",
            code="LLM_BASE_URL_NOT_ALLOWED",
        )
    try:
        address = ipaddress.ip_address(parsed.hostname)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise LLMProviderError(
            "OpenAI-compatible LLM endpoint cannot use a private or local address.",
            code="LLM_BASE_URL_NOT_ALLOWED",
        )
    host = parsed.hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    authority = f"{host}:{port}" if port is not None else host
    path = parsed.path.rstrip("/")
    return f"https://{authority}{path}"


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


def _select_coordination_nn_tools(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> list[str]:
    if not _has_structure_input(data_profile):
        return []
    prompt = request.user_prompt.lower()
    crystal = "crystalnn" in prompt
    voronoi = "voronoinn" in prompt or "voronoi nn" in prompt
    comparison = any(marker in prompt for marker in ("compare", "comparison", "versus", " vs "))
    selected: list[str] = []
    if crystal or comparison:
        selected.append("structure.coordination_crystalnn")
    if voronoi or comparison:
        selected.append("structure.coordination_voronoinn")
    return [tool_id for tool_id in selected if _has_tool(tools, tool_id)]


def _select_local_environment_tools(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> list[str]:
    if not _has_structure_input(data_profile) or not _has_tool(tools, "structure.local_environment_polyhedra"):
        return []
    prompt = request.user_prompt.casefold()
    if not any(marker in prompt for marker in ("local environment", "coordination polyhed", "local geometry")):
        return []
    if "crystalnn" in prompt:
        producer = "structure.coordination_crystalnn"
    elif "voronoinn" in prompt or "voronoi nn" in prompt:
        producer = "structure.coordination_voronoinn"
    else:
        return []
    return [producer, "structure.local_environment_polyhedra"] if _has_tool(tools, producer) else []


def _select_experimental_xrd_tools(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> list[str]:
    prompt = request.user_prompt.casefold()
    readiness = data_profile.experimentalXrdReadiness
    if (
        not _has_structure_input(data_profile)
        or readiness is None
        or readiness.status != "READY"
        or readiness.eligibleResourceCount != 1
        or not any(marker in prompt for marker in ("experimental xrd", "match experimental peaks", "xrd comparison", "xrd correspondence"))
    ):
        return []
    selected = ["structure.xrd", "structure.experimental_xrd_comparison"]
    return selected if all(_has_tool(tools, tool_id) for tool_id in selected) else []


def _mock_experimental_xrd_plan(
    request: PlannerRequest,
    data_profile: DataProfile,
    tool_ids: list[str],
) -> dict[str, Any]:
    experimental = data_profile.experimentalXrdReadiness
    if experimental is None or len(experimental.resources) != 1:
        raise LLMProviderError("Experimental XRD comparison requires one exact ready resource.")
    experimental_id = experimental.resources[0].objectId
    producer = _mock_structure_plan(
        request,
        data_profile=data_profile,
        tool_id=tool_ids[0],
        purpose="Produce the exact persisted theoretical XRD authority for bounded experimental comparison.",
        params={"radiation": "CuKa", "two_theta_min": 0.0, "two_theta_max": 180.0, "intensity_threshold": 0.0, "peak_merge_tolerance": 0.001, "max_peaks": 5000, "include_hkl": True, "plot_kind": "stem"},
        artifact_name="xrd_pattern.json",
        artifact_type="table_json",
        artifact_types=["table_json", "plotly_json", "summary_md", "recipe_json"],
    )
    producer_step = producer["steps"][0]
    producer_step["stepId"] = "step_001"
    consumer_step = {
        "stepId": "step_002",
        "toolId": tool_ids[1],
        "purpose": "Detect experimental peaks independently and compare them one-to-one with exact theoretical XRD peaks.",
        "reason": "One explicit experimental XRD resource and one exact theoretical structure are bound.",
        "inputRefs": [
            {"refType": "normalized_object", "ref": experimental_id, "objectType": "DataFrame"},
            {"refType": "normalized_object", "ref": "structures", "objectType": "Structure"},
        ],
        "params": {"normalization": "max_to_1", "minimum_prominence": 0.05, "minimum_relative_height": 0.0, "minimum_peak_separation_deg": 0.1, "max_detected_peaks": 10000, "matching_tolerance_deg": 0.15, "max_matching_candidates": 200000, "max_theoretical_peaks": 20000, "max_output_matches": 10000, "max_output_bytes": 33554432},
        "output": {"artifactTypes": ["table_json", "plotly_json", "summary_md", "recipe_json"]},
    }
    return {
        "schemaVersion": "0.1", "goal": request.user_prompt, "datasetId": request.dataset_id,
        "profileId": request.profile_id, "toolRegistryVersion": request.tool_registry_version,
        "assumptions": ["Wavelength and units are explicit and must match exactly under the N3 contract."],
        "warnings": ["This is peak correspondence under tolerance, not refinement or definitive phase identification."],
        "steps": [producer_step, consumer_step],
        "expectedArtifacts": [
            {"name": "xrd_pattern.json", "type": "table_json", "fromStepId": "step_001"},
            {"name": "experimental_xrd_comparison.json", "type": "table_json", "fromStepId": "step_002"},
            {"name": "experimental_xrd_comparison_plot.json", "type": "plotly_json", "fromStepId": "step_002"},
            {"name": "summary.md", "type": "summary_md", "fromStepId": "step_002"},
            {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_002"},
        ],
    }


def _mock_local_environment_plan(
    request: PlannerRequest,
    data_profile: DataProfile,
    tool_ids: list[str],
) -> dict[str, Any]:
    producer_id, consumer_id = tool_ids
    producer = _mock_coordination_nn_plan(request, data_profile, [producer_id])
    producer_step = producer["steps"][0]
    producer_step["stepId"] = "step_001"
    consumer_step = {
        "stepId": "step_002",
        "toolId": consumer_id,
        "purpose": "Classify geometry-derived local environments and construct coordination polyhedra from the exact persisted N1 neighbor set.",
        "reason": _structure_reason(request, data_profile, consumer_id),
        "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
        "params": {},
        "output": {"artifactTypes": ["table_json", "summary_md", "recipe_json"]},
    }
    return {
        "schemaVersion": "0.1",
        "goal": request.user_prompt,
        "datasetId": request.dataset_id,
        "profileId": request.profile_id,
        "toolRegistryVersion": request.tool_registry_version,
        "assumptions": ["Local environment is geometry-derived from one exact persisted N1 coordination Artifact."],
        "warnings": ["The result is source-algorithm-dependent and is not definitive bonding chemistry."],
        "steps": [producer_step, consumer_step],
        "expectedArtifacts": [
            {"name": producer["expectedArtifacts"][0]["name"], "type": "table_json", "fromStepId": "step_001"},
            {"name": "local_environment_polyhedra.json", "type": "table_json", "fromStepId": "step_002"},
            {"name": "summary.md", "type": "summary_md", "fromStepId": "step_002"},
            {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_002"},
        ],
    }


def _mock_coordination_nn_plan(
    request: PlannerRequest,
    data_profile: DataProfile,
    tool_ids: list[str],
) -> dict[str, Any]:
    defaults = {
        "structure.coordination_crystalnn": {
            "weighted_cn": True,
            "distance_cutoff_low": 0.5,
            "distance_cutoff_high": 1.0,
            "x_diff_weight": 3.0,
            "porous_adjustment": True,
            "search_cutoff_angstrom": 7.0,
            "max_structures": 32,
            "max_sites": 5000,
            "max_neighbors_per_site": 1000,
            "max_retained_rows": 50000,
        },
        "structure.coordination_voronoinn": {
            "tol": 0.0,
            "cutoff_angstrom": 13.0,
            "allow_pathological": False,
            "max_structures": 32,
            "max_sites": 5000,
            "max_neighbors_per_site": 1000,
            "max_retained_rows": 50000,
        },
    }
    names = {
        "structure.coordination_crystalnn": "crystalnn_coordination.json",
        "structure.coordination_voronoinn": "voronoinn_coordination.json",
    }
    steps: list[dict[str, Any]] = []
    expected: list[dict[str, Any]] = []
    for index, tool_id in enumerate(tool_ids, start=1):
        step_id = f"step_{index:03d}"
        algorithm = "CrystalNN" if tool_id.endswith("crystalnn") else "VoronoiNN"
        steps.append({
            "stepId": step_id,
            "toolId": tool_id,
            "purpose": f"Compute {algorithm}-derived coordination under bounded, persisted parameters.",
            "reason": _structure_reason(request, data_profile, tool_id),
            "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
            "params": defaults[tool_id],
            "output": {"artifactTypes": ["table_json", "summary_md", "recipe_json"]},
        })
        expected.extend([
            {"name": names[tool_id], "type": "table_json", "fromStepId": step_id},
            {"name": "summary.md", "type": "summary_md", "fromStepId": step_id},
            {"name": "recipe.json", "type": "recipe_json", "fromStepId": step_id},
        ])
    warnings = []
    if len(steps) == 2:
        warnings.append("CrystalNN and VoronoiNN results retain algorithm-specific semantics; comparison does not select a correct algorithm.")
    return {
        "schemaVersion": "0.1",
        "goal": request.user_prompt,
        "datasetId": request.dataset_id,
        "profileId": request.profile_id,
        "toolRegistryVersion": request.tool_registry_version,
        "assumptions": ["Coordination is algorithm-derived and is not definitive chemical bonding."],
        "warnings": warnings,
        "steps": steps,
        "expectedArtifacts": expected,
    }


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


def _should_generate_dataset_materials_explorer(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "dataset.materials_explorer") or data_profile.profileContractVersion not in {"2.0", "2.1"}:
        return False
    prompt = request.user_prompt.lower()
    excluded = (
        "model performance",
        "prediction error",
        "parity",
        "uncertainty calibration",
        "confusion matrix",
        "机器学习模型",
        "预测误差",
        "不确定性校准",
    )
    if any(marker in prompt for marker in excluded):
        return False
    markers = (
        "dataset materials explorer",
        "materials dataset",
        "dataset overview",
        "explore this dataset",
        "analyze this batch of materials",
        "composition and properties",
        "compare train and test coverage",
        "材料数据集",
        "这批材料",
        "数据集概览",
        "组成和属性",
        "比较训练集和测试集",
    )
    return any(marker in prompt for marker in markers)


def _should_generate_composition_space(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "dataset.composition_space") or data_profile.profileContractVersion not in {"2.0", "2.1"}:
        return False
    prompt = request.user_prompt.lower()
    markers = (
        "composition space",
        "composition pca",
        "pca compositions",
        "cluster compositions",
        "composition clustering",
        "composition embedding",
        "chemical composition space",
        "组成空间",
        "组成 pca",
        "成分空间",
        "成分聚类",
    )
    if not any(marker in prompt for marker in markers):
        return False
    return any(
        item.capability == "composition_space"
        and item.dataStatus == "READY"
        and item.platformStatus == "AVAILABLE"
        for item in data_profile.analysisReadiness
    )


def _select_materials_ml_tool(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> str | None:
    if data_profile.profileContractVersion not in {"2.0", "2.1"}:
        return None
    prompt = request.user_prompt.lower()
    candidates = (
        (
            "ml.classification_evaluation",
            "classification",
            ("classification", "confusion matrix", "precision", "recall", "roc", "pr curve", "分类", "混淆矩阵"),
        ),
        (
            "ml.uncertainty_evaluation",
            "uncertainty",
            ("uncertainty", "calibration", "reliability", "error decay", "不确定性", "校准", "可靠性"),
        ),
        (
            "ml.regression_evaluation",
            "regression",
            (
                "model performance",
                "prediction error",
                "parity",
                "residual",
                "regression evaluation",
                "compare models",
                "机器学习模型",
                "预测误差",
                "回归评估",
                "模型表现",
            ),
        ),
    )
    for tool_id, capability, markers in candidates:
        if _has_tool(tools, tool_id) and any(marker in prompt for marker in markers):
            groups = _materials_ml_groups(data_profile, capability)
            if groups:
                return tool_id
    return None


def _should_generate_ambiguous_ml_diagnostic(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if data_profile.profileContractVersion not in {"2.0", "2.1"} or not _has_tool(tools, "dataset.materials_explorer"):
        return False
    prompt = request.user_prompt.lower()
    markers = (
        "model performance",
        "prediction error",
        "parity",
        "residual",
        "regression evaluation",
        "uncertainty",
        "classification",
        "模型表现",
        "预测误差",
        "回归评估",
        "不确定性",
        "分类",
    )
    if not any(marker in prompt for marker in markers):
        return False
    return any(
        item.capability in {"regression_evaluation", "uncertainty_evaluation", "classification_evaluation"}
        and item.dataStatus == "AMBIGUOUS"
        for item in data_profile.analysisReadiness
    )


def _materials_ml_groups(data_profile: DataProfile, capability: str) -> list[Any]:
    if capability == "classification":
        return [group for group in data_profile.semanticGroups if group.kind == "classification" and group.status == "COMPLETE"]
    groups = [group for group in data_profile.semanticGroups if group.kind == "regression" and group.status == "COMPLETE"]
    if capability == "uncertainty":
        groups = [group for group in groups if group.uncertaintyColumns or any(binding.uncertaintyColumns for binding in group.seriesBindings)]
    return groups


def _mock_materials_ml_plan(
    request: PlannerRequest,
    data_profile: DataProfile,
    tool_id: str,
) -> dict[str, Any]:
    capability = {
        "ml.regression_evaluation": "regression",
        "ml.uncertainty_evaluation": "uncertainty",
        "ml.classification_evaluation": "classification",
    }[tool_id]
    groups = _materials_ml_groups(data_profile, capability)
    object_groups: dict[str, list[Any]] = {}
    for group in groups:
        object_ids = sorted(
            {
                column.objectId
                for column in data_profile.semanticColumns
                if any(role.groupId == group.groupId for role in column.roles)
            }
        )
        if len(object_ids) == 1:
            object_groups.setdefault(object_ids[0], []).append(group)
    if not object_groups:
        raise ValueError("Profile 2.0 contains no unambiguous ML table binding.")
    object_id = sorted(object_groups)[0]
    selected_groups = sorted(object_groups[object_id], key=lambda item: item.groupId)
    params: dict[str, Any] = {
        "groupIds": [group.groupId for group in selected_groups],
        "maxTableRows": 100,
        "maxPlotPoints": 2000,
    }
    if tool_id == "ml.regression_evaluation":
        params.update({"maxChemistryGroups": 128, "minGroupSize": 3, "histogramBins": 30})
    elif tool_id == "ml.uncertainty_evaluation":
        params["uncertaintyBins"] = 10
    else:
        params["maxCurvePoints"] = 1000
        explicit_positive = re.search(r"(?:positive class|正类)\s*[:=]?\s*([a-zA-Z0-9_.-]+)", request.user_prompt)
        if explicit_positive:
            requested = explicit_positive.group(1).lower().strip(".,;:!?")
            classes = sorted({label for group in selected_groups for label in group.classes})
            if requested in classes:
                params["positiveClass"] = requested
    artifact_name = {
        "ml.regression_evaluation": "materials_ml_regression.json",
        "ml.uncertainty_evaluation": "materials_ml_uncertainty.json",
        "ml.classification_evaluation": "materials_ml_classification.json",
    }[tool_id]
    purpose = {
        "ml.regression_evaluation": "Evaluate Profile-bound materials regression results and linked chemistry-conditioned errors.",
        "ml.uncertainty_evaluation": "Evaluate explicit Profile-bound uncertainty diagnostics without fitting or calibration claims.",
        "ml.classification_evaluation": "Evaluate Profile-bound classification results and valid explicit-positive-class binary curves.",
    }[tool_id]
    step = {
        "stepId": "step_001",
        "toolId": tool_id,
        "purpose": purpose,
        "reason": "The request and Material Data Profile 2.0 expose a complete compatible evaluation task.",
        "inputRefs": [
            {"refType": "profile", "ref": "profile"},
            {"refType": "normalized_object", "ref": object_id, "objectType": "DataFrame", "fieldRole": "ml_result_table"},
        ],
        "params": params,
        "output": {"artifactTypes": ["table_json", "summary_md", "recipe_json"]},
    }
    return _single_step_plan(
        request,
        step,
        [
            {"name": artifact_name, "type": "table_json", "fromStepId": "step_001"},
            {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
            {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
        ],
    )


def _mock_composition_space_plan(request: PlannerRequest, data_profile: DataProfile) -> dict[str, Any]:
    table_ids = sorted(
        item.objectId for item in data_profile.resourceSemantics if item.objectType == "DataFrame"
    )
    formula_tables = sorted(
        {
            column.objectId
            for column in data_profile.semanticColumns
            if any(role.role == "material_formula" for role in column.roles)
        }
    )
    eligible = [object_id for object_id in table_ids if object_id in formula_tables]
    if not eligible:
        raise ValueError("Profile 2.0 contains no unambiguous composition table binding.")
    object_id = eligible[0]
    params: dict[str, Any] = {
        "tableObjectId": object_id,
        "comparisonMode": "none",
        "projectionDimensions": 2,
        "clusteringEnabled": True,
        "nClusters": 3,
        "randomState": 0,
        "nInit": 10,
        "maxIterations": 300,
        "tolerance": 0.0001,
        "maxPlotPoints": 5000,
        "maxOutlierRows": 50,
    }
    prompt = request.user_prompt.lower()
    columns = {
        column.column.lower(): column.column
        for column in data_profile.semanticColumns
        if column.objectId == object_id
    }
    if any(marker in prompt for marker in ("train and test", "training and test", "train/test", "训练集和测试集")) and "split" in columns:
        params.update(
            {
                "comparisonMode": "group",
                "groupColumn": columns["split"],
                "groupA": "train",
                "groupB": "test",
            }
        )
    step = {
        "stepId": "step_001",
        "toolId": "dataset.composition_space",
        "purpose": "Build deterministic Profile-bound PCA composition space with optional bounded composition clustering.",
        "reason": "The request explicitly asks for composition-space exploration on a Profile 2.0 formula-bearing table.",
        "inputRefs": [
            {"refType": "profile", "ref": "profile"},
            {"refType": "normalized_object", "ref": object_id, "objectType": "DataFrame", "fieldRole": "composition_samples"},
        ],
        "params": params,
        "output": {"artifactTypes": ["table_json", "plotly_json", "summary_md", "recipe_json"]},
    }
    expected = [
        {"name": "composition_space.json", "type": "table_json", "fromStepId": "step_001"},
        {"name": "composition_space_plot.json", "type": "plotly_json", "fromStepId": "step_001"},
        {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
        {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
    ]
    return _single_step_plan(request, step, expected)


def _mock_dataset_materials_explorer_plan(request: PlannerRequest, data_profile: DataProfile) -> dict[str, Any]:
    table_ids = sorted(
        item.objectId for item in data_profile.resourceSemantics if item.objectType == "DataFrame"
    )
    structure_ids = [item.objectId for item in data_profile.resourceSemantics if item.objectType == "Structure"]
    input_refs: list[dict[str, Any]] = [{"refType": "profile", "ref": "profile"}]
    if table_ids:
        input_refs.append(
            {"refType": "normalized_object", "ref": table_ids[0], "objectType": "DataFrame", "fieldRole": "primary_table"}
        )
    if structure_ids:
        input_refs.append(
            {
                "refType": "normalized_object",
                "ref": "structure_resources",
                "objectType": "Structure",
                "fieldRole": "structure_collection",
            }
        )
    params: dict[str, Any] = {
        "comparisonMode": "none",
        "maxProperties": 32,
        "maxCategories": 50,
        "maxTableRows": 100,
        "histogramBins": 20,
        "maxStructures": 256,
        "symprec": 0.01,
    }
    if table_ids:
        params["tableObjectId"] = table_ids[0]
    prompt = request.user_prompt.lower()
    columns = {column.column.lower(): column.column for column in data_profile.semanticColumns if column.objectId in table_ids[:1]}
    if any(marker in prompt for marker in ("train and test", "training and test", "训练集和测试集")) and "split" in columns:
        params.update({"comparisonMode": "group", "groupColumn": columns["split"], "groupA": "train", "groupB": "test"})
    artifact_types = ["table_json", "quality_issues_json", "summary_md", "recipe_json"]
    step = {
        "stepId": "step_001",
        "toolId": "dataset.materials_explorer",
        "purpose": "Build a bounded Profile 2.0-backed materials dataset overview and explicit comparison.",
        "reason": "The request asks for one coherent dataset-level materials analysis product.",
        "inputRefs": input_refs,
        "params": params,
        "output": {"artifactTypes": artifact_types},
    }
    expected = [
        {"name": "dataset_materials_explorer.json", "type": "table_json", "fromStepId": "step_001"},
        {"name": "dataset_quality.json", "type": "quality_issues_json", "fromStepId": "step_001"},
        {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
        {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
    ]
    return _single_step_plan(request, step, expected)


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


def _should_generate_band_bz_link(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not (_has_tool(tools, "phonon.band") and _has_tool(tools, "structure.brillouin_zone")):
        return False
    if not (_has_phonon_band_input(data_profile) and _has_structure_input(data_profile)):
        return False
    prompt = request.user_prompt.lower()
    unsupported = (
        "electronic band", "electronic dos", "fermi", "dft", "dfpt", "wannier",
        "unfolding", "custom path", "edit k-path", "monkhorst", "magnetic bz",
        "surface bz", "calculate phonon", "run phonopy", "电子能带", "费米", "磁性布里渊", "表面布里渊",
    )
    if any(marker in prompt for marker in unsupported):
        return False
    markers = (
        "phonon band path in the brillouin zone", "link the phonon band chart to the 3d bz",
        "link phonon bands", "phonon bands with the brillouin zone", "highlight selected q-points in reciprocal space",
        "同时显示声子能带和布里渊区", "把声子q路径映射到三维bz", "联动查看phonon bands与高对称路径",
        "声子能带和布里渊区联动", "声子 q 路径映射到三维 bz",
    )
    return any(marker in prompt for marker in markers)


def _mock_band_bz_link_plan(request: PlannerRequest, data_profile: DataProfile) -> dict[str, Any]:
    band_types = [
        "phonon_band_json", "phonon_summary_json", "phonon_report_json", "phonon_manifest_json",
        "plotly_json", "table_json", "recipe_json",
    ]
    bz_types = [
        "reciprocal_lattice_json", "brillouin_zone_json", "kpath_json",
        "brillouin_zone_manifest_json", "summary_md", "recipe_json",
    ]
    steps = [
        {
            "stepId": "step_band",
            "toolId": "phonon.band",
            "purpose": "Validate the existing phonon band artifact for the linked reciprocal-space view.",
            "reason": "The linked product needs the canonical phonon q-path without recomputing phonons.",
            "inputRefs": [{"refType": "normalized_object", "ref": "phonon_band", "objectType": "PhononBand"}],
            "params": {"source_format": "auto", "source_frequency_unit": "terahertz", "max_table_rows": 20000, "plot_kind": "line"},
            "output": {"artifactTypes": band_types},
        },
        {
            "stepId": "step_bz",
            "toolId": "structure.brillouin_zone",
            "purpose": "Generate the canonical Brillouin-zone geometry and k-path for compatibility validation.",
            "reason": _structure_reason(request, data_profile, "structure.brillouin_zone"),
            "inputRefs": [{"refType": "normalized_object", "ref": "structures", "objectType": "Structure"}],
            "params": {"include_reciprocal_lattice": True, "include_brillouin_zone": True, "include_kpath": True, "standardization": "contract_default", "kpath_provider": "contract_default", "time_reversal": True, "symmetry_tolerance_angstrom": 0.00001, "angle_tolerance_degrees": 5.0, "include_alternative_path_variants": False},
            "output": {"artifactTypes": bz_types},
        },
    ]
    expected = [
        {"name": "phonon_band.json", "type": "phonon_band_json", "fromStepId": "step_band"},
        {"name": "reciprocal_lattice.json", "type": "reciprocal_lattice_json", "fromStepId": "step_bz"},
        {"name": "brillouin_zone.json", "type": "brillouin_zone_json", "fromStepId": "step_bz"},
        {"name": "kpath.json", "type": "kpath_json", "fromStepId": "step_bz"},
        {"name": "brillouin_zone_manifest.json", "type": "brillouin_zone_manifest_json", "fromStepId": "step_bz"},
    ]
    return {
        "schemaVersion": "0.1", "goal": request.user_prompt, "datasetId": request.dataset_id,
        "profileId": request.profile_id, "toolRegistryVersion": request.tool_registry_version,
        "assumptions": ["Linked view is an application-owned compatibility layer over inert artifacts."],
        "warnings": ["Band provider and time-reversal metadata are not declared by phase10h.phonon_band.v1; exact ordered path geometry is revalidated before linking."],
        "steps": steps, "expectedArtifacts": expected,
    }


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


def _has_volumetric_input(data_profile: DataProfile) -> bool:
    for obj in getattr(data_profile, "objects", None) or []:
        if isinstance(obj, dict) and str(obj.get("objectType") or obj.get("object_type") or "").lower() == "volumetricdata":
            return True
    return "volumetric" in str(getattr(data_profile, "datasetType", "") or "").lower()


def _should_generate_volumetric_data(
    request: PlannerRequest,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> bool:
    if not _has_tool(tools, "structure.volumetric_data") or not _has_volumetric_input(data_profile):
        return False
    prompt = request.user_prompt.lower()
    unsupported = (
        "curved slice", "arbitrary plane", "arbitrary surface", "arbitrary python", "volume filter", "remote gpu", "segmentation", "segment the", "bader", "atomic charge", "charge partition",
        "run vasp", "calculate density", "calculate charge", "calculate locpot", "calculate elf", "elf basin", "elf attractor", "lone pair",
        "calculate orbital", "generate orbital", "homo", "lumo", "wavefunction", "orbital reconstruction", "orbital combination", "linear combination",
        "work function", "vacuum level", "fermi level", "band offset", "potential alignment", "macroscopic average", "electric field", "trajectory", "phonon", "brillouin", "defect", "slab",
        "任意曲面切片", "任意平面", "自动分割", "体数据过滤", "远程 gpu", "bader", "原子电荷", "电荷分区", "计算电荷密度", "计算 locpot", "计算 elf", "elf 盆地", "孤对电子",
        "计算轨道", "生成轨道", "重构波函数", "轨道线性组合", "运行 vasp", "功函数", "真空能级", "费米能级", "能带偏移", "势对齐", "宏观平均", "电场", "轨迹", "声子", "布里渊",
    )
    if any(marker in prompt for marker in unsupported):
        return False
    markers = (
        "parse chgcar", "parse locpot", "parse elfcar", "parse parchg", "parse cube",
        "normalize volumetric", "volumetric data artifact", "canonical volumetric", "import charge density",
        "charge density", "electron density", "spin density", "spin difference", "local potential", "electrostatic potential", "equipotential", "planar-averaged potential", "planar average potential", "potential difference", "compare the potential", "cell-average-zero", "isosurface", "iso-surface", "volumetric viewer", "render density",
        "electron localization function", "elf isosurface", "visualize the elf", "show an elf", "orbital density", "orbital-density", "partial charge density", "partial density", "source-defined partial density",
        "slice through", "lattice slice", "fractional coordinate", "direct volume", "volume rendering", "render this volumetric field", "3d volume view", "ray cast this volume",
        "解析 chgcar", "解析 locpot", "解析 elfcar", "解析 parchg", "解析 cube", "规范化体数据", "导入体数据",
        "电荷密度", "电子密度", "自旋密度", "自旋差", "局域势", "静电势", "等势面", "平面平均势", "电势差", "胞平均零点", "等值面", "体数据查看器", "渲染密度",
        "电子局域函数", "elf 等值面", "部分电荷密度", "轨道密度", "源定义的部分密度",
        "切片", "晶格切片", "二维切片", "截面", "fractional 位置", "体绘制", "体渲染", "三维体数据",
    )
    return any(marker in prompt for marker in markers)


def _mock_volumetric_data_plan(request: PlannerRequest) -> dict[str, Any]:
    artifact_types = [
        "volumetric_grid_json", "volumetric_payload_json", "volumetric_field_json",
        "volumetric_dataset_json", "volumetric_manifest_json", "volumetric_binary", "summary_md", "recipe_json",
        "volumetric_structure_overlay_json",
    ]
    step = {
        "stepId": "step_001",
        "toolId": "structure.volumetric_data",
        "purpose": "Parse one bounded supported source into validated inert canonical volumetric artifacts for the application-owned isosurface, lattice-slice, or direct-volume product.",
        "reason": "The request asks to validate an available bounded volumetric source for local browser visualization without external calculation, rendering, or execution.",
        "inputRefs": [{"refType": "normalized_object", "ref": "volumetric", "objectType": "VolumetricData"}],
        "params": {
            "format": "auto", "quantity_hint": "auto", "field_selection": "all_supported",
            "stored_dtype": "source_or_float64", "compression": "contract_default",
            "include_statistics": True, "include_histogram": False,
            "verify_integrals": True, "allow_partial_dataset": False,
        },
        "output": {"artifactTypes": artifact_types},
        "constraints": {"noExternalNetwork": True},
    }
    expected = [
        {"name": "volumetric_grid.json", "type": "volumetric_grid_json", "fromStepId": "step_001"},
        {"name": "volumetric_payload_01.json", "type": "volumetric_payload_json", "fromStepId": "step_001"},
        {"name": "volumetric_field_01.json", "type": "volumetric_field_json", "fromStepId": "step_001"},
        {"name": "volumetric_dataset.json", "type": "volumetric_dataset_json", "fromStepId": "step_001"},
        {"name": "volumetric_manifest.json", "type": "volumetric_manifest_json", "fromStepId": "step_001"},
        {"name": "volumetric_structure_overlay.json", "type": "volumetric_structure_overlay_json", "fromStepId": "step_001"},
        {"name": "volumetric_field_01.f64.gz", "type": "volumetric_binary", "fromStepId": "step_001"},
        {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
        {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
    ]
    return _single_step_plan(request, step, expected)


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
