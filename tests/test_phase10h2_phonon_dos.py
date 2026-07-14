from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mdi_adapters import PhononDosAdapter, ToolExecutionContext, ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import (
    PHONON_DOS_SCHEMA_VERSION,
    convert_frequency,
    validate_phonon_dos,
    validate_phonon_dos_manifest,
    validate_phonon_dos_summary,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10h" / "fixtures" / "phonon_contract"
ARTIFACT_TYPES = [
    "phonon_dos_json", "phonon_summary_json", "phonon_report_json", "phonon_manifest_json",
    "plotly_json", "table_json", "recipe_json",
]


def _canonical(name: str = "projected_dos.json") -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _source() -> dict:
    return {
        "producer": "phonopy",
        "producer_version": "2.43",
        "calculation_method": "finite_displacement",
        "force_constants_source": "force_constants",
        "supercell_matrix": [[2, 0, 0], [0, 2, 0], [0, 0, 2]],
        "primitive_matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        "nac": {"enabled": False, "direction_policy": None, "gamma_direction": None},
        "adapter_version": "source-wrapper-v1",
    }


def _wrapper(*, projected: bool = False, unit: str = "terahertz", normalization: str = "total_modes") -> dict:
    frequencies_thz = [-1, 0, 1, 2, 3, 4, 5]
    frequency_scale = convert_frequency(1.0, unit, "terahertz")
    canonical_density = 1.0 if normalization == "total_modes" else 1.0 / 6.0
    source_density = canonical_density * frequency_scale
    rows = []
    for frequency in frequencies_thz:
        columns = [frequency / frequency_scale, source_density]
        if projected:
            columns.extend([source_density / 2.0, source_density / 2.0])
        rows.append(" ".join(f"{value:.17g}" for value in columns))
    return {
        "source_format": "phonopy_projected_dos" if projected else "phonopy_total_dos",
        "content": "# frequency total projected...\n" + "\n".join(rows) + "\n",
        "structure_identity": "a" * 64,
        "atom_count": 2,
        "species": ["Si", "Si"],
        "source_frequency_unit": unit,
        "source_normalization": normalization,
        "projection_completeness": "complete" if projected else "unknown",
        "projections": [
            {"projection_type": "atom", "atom_index": 0, "species": "Si"},
            {"projection_type": "atom", "atom_index": 1, "species": "Si"},
        ] if projected else [],
        "broadening": {"method": "none", "width": None, "unit": None, "source": "phonopy"},
        "source": _source(),
    }


def _context(tmp_path: Path, source: object) -> ToolExecutionContext:
    tool = load_manifests().get_tool_by_id("phonon.dos")
    return ToolExecutionContext(
        job_id="job_h2", project_id="project_h2", dataset_id="dataset_h2", tool_id=tool.toolId,
        tool_version=tool.version, adapter_version="0.1.0", registry_version=load_manifests().version,
        artifact_root=tmp_path / "artifacts", tool_call_id="call_h2", object_store={"phonon_dos": source},
        resource_limits=tool.resourceLimits,
    )


def _request(params: dict | None = None) -> ToolExecutionRequest:
    return ToolExecutionRequest(
        jobId="job_h2", stepId="step_001", toolId="phonon.dos",
        inputRefs=[{"refType": "normalized_object", "ref": "phonon_dos", "objectType": "PhononDos"}],
        params=params or {}, artifactTypes=ARTIFACT_TYPES,
    )


def _execute(tmp_path: Path, source: object, params: dict | None = None) -> tuple[list, dict[str, dict]]:
    artifacts = PhononDosAdapter().execute(_context(tmp_path, source), _request(params))
    payloads = {artifact.name: json.loads((tmp_path / "artifacts" / artifact.storageKey).read_text(encoding="utf-8")) for artifact in artifacts}
    return artifacts, payloads


def _profile() -> DataProfile:
    return DataProfile(
        profileId="profile_h2", datasetId="dataset_h2", version="1", datasetType="phonondos",
        objects=[{"id": "phonon_dos", "objectType": "PhononDos"}],
        phononSummary={"dosAvailable": True}, createdAt="2026-07-14T00:00:00Z",
    )


def _plan(prompt: str) -> dict:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(prompt, "dataset_h2", "profile_h2", registry.version),
        tools=registry.list_mvp_tools(), data_profile=_profile(),
    )
    assert response.raw_json is not None
    return response.raw_json


def test_registry_declares_single_strict_dos_tool() -> None:
    registry = load_manifests()
    matches = [tool for tool in registry.tools if tool.toolId == "phonon.dos"]
    assert len(matches) == 1
    tool = matches[0]
    assert tool.stage == "mvp" and tool.adapter == "PhononDosAdapter"
    assert tool.inputSchema.inputOptions[0].requiredObjectTypes == ["PhononDos"]
    assert tool.paramsSchema["additionalProperties"] is False
    assert [item.value for item in tool.artifactTypes] == ARTIFACT_TYPES
    assert "combined" in tool.description and "external resources" in tool.description


def test_canonical_input_emits_dos_specific_summary_manifest_and_static_products(tmp_path: Path) -> None:
    original = _canonical()
    source = copy.deepcopy(original)
    artifacts, payloads = _execute(tmp_path, source)
    assert source == original
    assert len(artifacts) == len({artifact.id for artifact in artifacts}) == 7
    assert payloads["phonon_dos.json"] == original
    assert validate_phonon_dos(payloads["phonon_dos.json"]).valid
    assert validate_phonon_dos_summary(payloads["phonon_dos_summary.json"]).valid
    assert validate_phonon_dos_manifest(payloads["phonon_manifest.json"]).valid
    assert payloads["phonon_dos_summary.json"]["projection_completeness"] == "complete"
    assert payloads["phonon_dos_plot.json"]["metadata"]["negative_frequency_preserved"] is True
    assert payloads["phonon_dos_table.json"]["rows"][0]["classification"] == "imaginary"


@pytest.mark.parametrize("unit", ["terahertz", "inverse_centimeter", "millielectronvolt"])
def test_phonopy_total_dos_converts_frequency_density_and_preserves_integral(tmp_path: Path, unit: str) -> None:
    wrapper = _wrapper(unit=unit)
    _, payloads = _execute(tmp_path, wrapper, {"source_format": "phonopy_total_dos", "source_frequency_unit": unit})
    dos = payloads["phonon_dos.json"]
    report = payloads["phonon_dos_parse_report.json"]
    assert validate_phonon_dos(dos).valid
    assert dos["frequencies"] == pytest.approx([-1, 0, 1, 2, 3, 4, 5])
    assert dos["total_dos"] == pytest.approx([1] * 7)
    assert dos["integration"]["observed_integral"] == pytest.approx(6)
    assert report["conversion"]["density_jacobian_applied"] is (unit != "terahertz")


def test_unit_area_and_projected_dos_are_scaled_to_total_modes_without_inference(tmp_path: Path) -> None:
    wrapper = _wrapper(projected=True, unit="inverse_centimeter", normalization="unit_area")
    _, payloads = _execute(tmp_path, wrapper, {
        "source_format": "phonopy_projected_dos", "source_frequency_unit": "inverse_centimeter", "source_normalization": "unit_area",
    })
    dos = payloads["phonon_dos.json"]
    assert dos["integration"]["observed_integral"] == pytest.approx(6)
    assert dos["total_dos"] == pytest.approx([1] * 7)
    assert dos["projected_dos"][0]["values"] == pytest.approx([0.5] * 7)
    assert dos["projected_dos"][0]["source_guarantees_sum"] is True
    assert payloads["phonon_dos_parse_report.json"]["conversion"]["normalization_scale_applied"] is True


def test_partial_projection_does_not_claim_complete_sum(tmp_path: Path) -> None:
    wrapper = _wrapper(projected=True)
    wrapper["projection_completeness"] = "partial"
    wrapper["content"] = wrapper["content"].replace(" 0.5 0.5", " 0.25 0.25")
    _, payloads = _execute(tmp_path, wrapper, {"source_format": "phonopy_projected_dos"})
    assert payloads["phonon_dos_summary.json"]["projection_completeness"] == "partial"
    assert all(item["source_guarantees_sum"] is False for item in payloads["phonon_dos.json"]["projected_dos"])


@pytest.mark.parametrize(
    ("mutator", "error_type"),
    [
        (lambda wrapper: wrapper.update(content="0 1\n0 1\n"), "PHONON_DOS_GRID_INVALID"),
        (lambda wrapper: wrapper.update(content="0 -1\n1 -1\n"), "PHONON_DOS_NONFINITE"),
        (lambda wrapper: wrapper.update(content="0 1 2\n1 1 2\n"), "PHONON_DOS_PARSE_FAILED"),
        (lambda wrapper: wrapper.update(projection_completeness="complete"), None),
    ],
)
def test_malformed_sources_fail_before_artifact_export(tmp_path: Path, mutator, error_type: str | None) -> None:
    wrapper = _wrapper()
    mutator(wrapper)
    if error_type is None:
        wrapper["projections"] = [{"projection_type": "atom", "atom_index": 9, "species": "Si"}]
        wrapper["source_format"] = "phonopy_projected_dos"
        error_type = "PHONON_DOS_PROJECTION_UNSUPPORTED"
    with pytest.raises(ToolExecutionError) as exc:
        PhononDosAdapter().execute(_context(tmp_path, wrapper), _request({"source_format": wrapper["source_format"]}))
    assert exc.value.details["errorType"] == error_type
    assert not (tmp_path / "artifacts").exists()


def test_canonical_invalid_and_plot_table_caps_are_safe(tmp_path: Path) -> None:
    invalid = _canonical()
    invalid["frequencies"][0] = float("nan")
    with pytest.raises(ToolExecutionError) as exc:
        PhononDosAdapter().execute(_context(tmp_path, invalid), _request())
    assert exc.value.details["errorType"] == "PHONON_DOS_VALIDATION_FAILED"
    _, payloads = _execute(tmp_path / "bounded", _canonical(), {"max_table_rows": 2, "max_plot_values": 7})
    assert payloads["phonon_dos_table.json"]["truncated"] is True
    assert payloads["phonon_dos_plot.json"]["metadata"]["degraded"] is True
    assert len(payloads["phonon_dos_plot.json"]["data"]) == 1


def test_planner_routes_only_static_dos_requests() -> None:
    for prompt in ("Plot the phonon density of states", "Show atom-projected phonon DOS", "显示声子态密度"):
        plan = _plan(prompt)
        assert plan["steps"][0]["toolId"] == "phonon.dos"
        assert validate_plan(plan, registry=load_manifests()).ok
    for prompt in (
        "Plot phonon bands", "Combine phonon bands and DOS", "Animate a phonon mode",
        "Calculate phonons from this structure", "Compute heat capacity", "Show the Brillouin zone",
    ):
        assert _plan(prompt)["steps"][0]["toolId"] != "phonon.dos"


def test_runtime_persists_deterministic_live_adapter_artifacts(tmp_path: Path) -> None:
    registry = load_manifests()
    plan = _plan("Plot the phonon density of states")
    outputs: list[dict[str, object]] = []
    for suffix in ("first", "second"):
        repos = InMemoryRepositoryBundle.create()
        root = tmp_path / suffix
        runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=root)
        created = planner_jobs(
            PlannerJobsRequest(userPrompt="Plot the phonon density of states", projectId="project_h2", datasetId="dataset_h2", profileId="profile_h2", enqueue=True),
            provider=MockLLMProvider(fixed_plan=plan), repositories=repos, queue_runtime=runtime, registry=registry,
        )
        assert created.ok and created.job_id and created.enqueued
        result = runtime.handle_job(created.job_id, object_store={"phonon_dos": _canonical()})
        assert result.status == "completed"
        records = repos.artifacts.list_for_job(created.job_id)
        assert [record["name"] for record in records] == [
            "phonon_dos.json", "phonon_dos_summary.json", "phonon_dos_parse_report.json",
            "phonon_manifest.json", "phonon_dos_plot.json", "phonon_dos_table.json", "recipe.json",
        ]
        assert all(record["metadata"]["provenance"]["toolId"] == "phonon.dos" for record in records)
        outputs.append({record["name"]: json.loads((root / record["storageKey"]).read_text(encoding="utf-8")) for record in records})
    assert outputs[0] == outputs[1]
