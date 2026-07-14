from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mdi_adapters import PhononBandAdapter, ToolExecutionContext, ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import validate_phonon_band, validate_phonon_manifest, validate_phonon_summary
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_FIXTURE = ROOT / "docs" / "phase10h" / "fixtures" / "phonon_contract" / "stable_band.json"
ARTIFACT_TYPES = [
    "phonon_band_json",
    "phonon_summary_json",
    "phonon_report_json",
    "phonon_manifest_json",
    "plotly_json",
    "table_json",
    "recipe_json",
]


def _canonical() -> dict:
    return json.loads(CANONICAL_FIXTURE.read_text(encoding="utf-8"))


def _phonopy_yaml() -> str:
    bands = "\n".join(f"      - # {index + 1}\n        frequency: {value}" for index, value in enumerate([-0.2, 0.0, 0.1, 4.0, 4.1, 4.2]))
    records = []
    for qpoint, shift in (([0, 0, 0], 0.0), ([0.5, 0, 0], 0.5), ([0.5, 0.5, 0.5], 1.0), ([0, 0, 0], 1.5)):
        shifted = bands.replace("frequency: -0.2", f"frequency: {-0.2 + shift}").replace("frequency: 4.2", f"frequency: {4.2 + shift}")
        records.append(f"  - q-position: [{qpoint[0]}, {qpoint[1]}, {qpoint[2]}]\n    band:\n{shifted}")
    return "\n".join(
        [
            "natom: 2",
            "lattice:",
            "  - [5.0, 0.0, 0.0]",
            "  - [0.0, 5.0, 0.0]",
            "  - [0.0, 0.0, 5.0]",
            "points:",
            "  - symbol: Si",
            "    coordinates: [0.0, 0.0, 0.0]",
            "  - symbol: Si",
            "    coordinates: [0.25, 0.25, 0.25]",
            "nqpoint: 4",
            "npath: 2",
            "segment_nqpoint: [2, 2]",
            "labels: [[GAMMA, X], [L, GAMMA]]",
            "phonon:",
            *records,
        ]
    ) + "\n"


def _context(tmp_path: Path, source: object) -> ToolExecutionContext:
    tool = load_manifests().get_tool_by_id("phonon.band")
    return ToolExecutionContext(
        job_id="job_h1",
        project_id="project_h1",
        dataset_id="dataset_h1",
        tool_id=tool.toolId,
        tool_version=tool.version,
        adapter_version="0.1.0",
        registry_version=load_manifests().version,
        artifact_root=tmp_path / "artifacts",
        tool_call_id="call_h1",
        object_store={"phonon_band": source},
        resource_limits=tool.resourceLimits,
    )


def _request(params: dict | None = None) -> ToolExecutionRequest:
    return ToolExecutionRequest(
        jobId="job_h1",
        stepId="step_001",
        toolId="phonon.band",
        inputRefs=[{"refType": "normalized_object", "ref": "phonon_band", "objectType": "PhononBand"}],
        params=params or {},
        artifactTypes=ARTIFACT_TYPES,
    )


def _execute(tmp_path: Path, source: object, params: dict | None = None) -> tuple[list, dict[str, dict]]:
    artifacts = PhononBandAdapter().execute(_context(tmp_path, source), _request(params))
    payloads = {
        artifact.name: json.loads((tmp_path / "artifacts" / artifact.storageKey).read_text(encoding="utf-8"))
        for artifact in artifacts
    }
    return artifacts, payloads


def _profile() -> DataProfile:
    return DataProfile(
        profileId="profile_h1",
        datasetId="dataset_h1",
        version="1",
        datasetType="phononband",
        objects=[{"id": "phonon_band", "objectType": "PhononBand"}],
        phononSummary={"bandAvailable": True},
        createdAt="2026-07-14T00:00:00Z",
    )


def _plan(prompt: str) -> dict:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(prompt, "dataset_h1", "profile_h1", registry.version),
        tools=registry.list_mvp_tools(),
        data_profile=_profile(),
    )
    assert response.raw_json is not None
    return response.raw_json


def test_registry_declares_single_strict_band_tool():
    registry = load_manifests()
    matches = [tool for tool in registry.tools if tool.toolId == "phonon.band"]
    assert len(matches) == 1
    tool = matches[0]
    assert tool.adapter == "PhononBandAdapter"
    assert tool.inputSchema.inputOptions[0].requiredObjectTypes == ["PhononBand"]
    assert tool.paramsSchema["additionalProperties"] is False
    assert [item.value for item in tool.artifactTypes] == ARTIFACT_TYPES
    assert "DOS" in tool.description and "animation" in tool.description


def test_canonical_input_is_validated_and_emits_unique_artifacts(tmp_path: Path):
    original = _canonical()
    source = copy.deepcopy(original)
    artifacts, payloads = _execute(tmp_path, source)
    assert source == original
    assert len(artifacts) == len({artifact.id for artifact in artifacts}) == 7
    assert payloads["phonon_band.json"] == original
    assert validate_phonon_band(payloads["phonon_band.json"]).valid
    assert validate_phonon_summary(payloads["phonon_summary.json"]).valid
    assert validate_phonon_manifest(payloads["phonon_manifest.json"]).valid
    assert payloads["phonon_band_parse_report.json"]["branch_order"] == "source_order_preserved"
    assert payloads["phonon_band_plot.json"]["metadata"]["negative_frequency_preserved"] is True
    assert payloads["phonon_band_table.json"]["truncated"] is False
    table = payloads["phonon_band_table.json"]
    assert table["units"] == {
        "qpoint_coordinates": "reciprocal_fractional",
        "path_distance": "radian_per_angstrom",
        "frequency": "terahertz",
    }
    assert table["columns"][-4:] == ["label", "branch_index", "frequency_terahertz", "classification"]
    assert {row["classification"] for row in table["rows"]} == {"near_zero", "real"}
    assert table["rows"][0]["q_x"] == table["rows"][0]["q_y"] == table["rows"][0]["q_z"] == 0.0


def test_phonopy_yaml_maps_qpoints_segments_branches_and_negative_frequency(tmp_path: Path):
    wrapper = {"source_format": "phonopy_band_yaml", "content": _phonopy_yaml(), "structure_identity": "a" * 64}
    _, payloads = _execute(tmp_path, wrapper, {"source_format": "phonopy_band_yaml", "plot_kind": "line"})
    band = payloads["phonon_band.json"]
    assert validate_phonon_band(band).valid
    assert band["species"] == ["Si", "Si"]
    assert len(band["branches"]) == 6
    assert band["branches"][0]["frequencies"][0] == pytest.approx(-0.2)
    assert band["branches"][5]["frequencies"][-1] == pytest.approx(5.7)
    assert band["segments"][1]["discontinuous_from_previous"] is True
    assert band["qpoints"][2]["distance"] == pytest.approx(band["qpoints"][1]["distance"])
    assert payloads["phonon_band_plot.json"]["metadata"]["trace_count"] == 12
    assert payloads["phonon_band_parse_report.json"]["source_format"] == "phonopy_band_yaml"
    assert payloads["phonon_band_table.json"]["rows"][0]["classification"] == "imaginary"


@pytest.mark.parametrize(
    "content,error_type",
    [
        ("value: &anchor [1, 2, 3]\ncopy: *anchor\n", "PHONON_BAND_YAML_UNSAFE"),
        ("value: !!python/object:os.system {}\n", "PHONON_BAND_YAML_UNSAFE"),
    ],
)
def test_phonopy_yaml_rejects_aliases_and_tags(tmp_path: Path, content: str, error_type: str):
    wrapper = {"source_format": "phonopy_band_yaml", "content": content, "structure_identity": "a" * 64}
    with pytest.raises(ToolExecutionError) as exc:
        PhononBandAdapter().execute(_context(tmp_path, wrapper), _request())
    assert exc.value.details["errorType"] == error_type


def test_invalid_canonical_input_is_rejected_before_artifact_export(tmp_path: Path):
    band = _canonical()
    band["branches"][0]["frequencies"][0] = float("nan")
    with pytest.raises(ToolExecutionError) as exc:
        PhononBandAdapter().execute(_context(tmp_path, band), _request())
    assert exc.value.details["errorType"] == "PHONON_BAND_VALIDATION_FAILED"
    assert not (tmp_path / "artifacts").exists()


def test_planner_routes_only_approved_static_band_requests():
    plan = _plan("Plot the phonon bands for this approved result")
    assert plan["steps"][0]["toolId"] == "phonon.band"
    assert validate_plan(plan, registry=load_manifests()).ok
    assert {item["type"] for item in plan["expectedArtifacts"]} == set(ARTIFACT_TYPES)
    for prompt in (
        "Plot the phonon DOS",
        "Animate phonon eigenvectors",
        "Calculate phonons by running phonopy",
        "Show the Brillouin zone",
    ):
        assert _plan(prompt)["steps"][0]["toolId"] != "phonon.band"


def test_table_is_bounded_without_mutating_canonical_band(tmp_path: Path):
    source = _canonical()
    _, payloads = _execute(tmp_path, source, {"max_table_rows": 2})
    table = payloads["phonon_band_table.json"]
    assert table["row_count"] == 2
    assert table["total_row_count"] == 18
    assert table["truncated"] is True
    assert validate_phonon_band(payloads["phonon_band.json"]).valid


def test_planner_job_runtime_persists_live_adapter_artifacts_deterministically(tmp_path: Path):
    registry = load_manifests()
    plan = _plan("Plot the phonon bands for this approved result")
    outputs: list[dict[str, object]] = []
    for suffix in ("first", "second"):
        repos = InMemoryRepositoryBundle.create()
        root = tmp_path / suffix
        runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=root)
        created = planner_jobs(
            PlannerJobsRequest(
                userPrompt="Plot the phonon bands for this approved result",
                projectId="project_h1",
                datasetId="dataset_h1",
                profileId="profile_h1",
                enqueue=True,
            ),
            provider=MockLLMProvider(fixed_plan=plan),
            repositories=repos,
            queue_runtime=runtime,
            registry=registry,
        )
        assert created.ok and created.job_id and created.enqueued
        result = runtime.handle_job(created.job_id, object_store={"phonon_band": _canonical()})
        assert result.status == "completed"
        calls = repos.tool_calls.list_for_job(created.job_id)
        records = repos.artifacts.list_for_job(created.job_id)
        assert len(calls) == 1 and calls[0]["toolId"] == "phonon.band"
        assert [record["name"] for record in records] == [
            "phonon_band.json", "phonon_summary.json", "phonon_band_parse_report.json",
            "phonon_manifest.json", "phonon_band_plot.json", "phonon_band_table.json", "recipe.json",
        ]
        assert all(record["metadata"]["provenance"]["toolId"] == "phonon.band" for record in records)
        outputs.append({record["name"]: json.loads((root / record["storageKey"]).read_text(encoding="utf-8")) for record in records})
    assert outputs[0] == outputs[1]
