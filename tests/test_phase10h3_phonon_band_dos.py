from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mdi_adapters import PhononBandDosAdapter, ToolExecutionContext, ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import (
    COMBINED_CHECK_ORDER,
    PHONON_BAND_DOS_COMPATIBILITY_SCHEMA_VERSION,
    PHONON_BAND_DOS_MANIFEST_SCHEMA_VERSION,
    PHONON_BAND_DOS_PLOT_SCHEMA_VERSION,
    PHONON_BAND_DOS_SCHEMA_VERSION,
    PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION,
    PhononBandDosContractError,
    combined_content_hash,
    compose_phonon_band_dos,
    convert_dos_frequency_density,
    convert_frequency,
    stable_phonon_json,
    validate_phonon_band_dos,
    validate_phonon_band_dos_compatibility_report,
    validate_phonon_band_dos_manifest,
    validate_phonon_band_dos_plot,
    validate_phonon_band_dos_summary,
    validate_phonon_band_dos_table,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10h" / "fixtures" / "phonon_contract"
ARTIFACT_TYPES = [
    "phonon_band_dos_json",
    "phonon_summary_json",
    "phonon_compatibility_json",
    "plotly_json",
    "table_json",
    "phonon_manifest_json",
    "recipe_json",
]


def _band() -> dict:
    return json.loads((FIXTURES / "stable_band.json").read_text(encoding="utf-8"))


def _dos() -> dict:
    return json.loads((FIXTURES / "projected_dos.json").read_text(encoding="utf-8"))


def _envelope(payload: dict, artifact_id: str, *, source_unit: str = "terahertz", role: str) -> dict:
    content = stable_phonon_json(payload).encode("utf-8")
    converted = source_unit != "terahertz"
    integral = payload["integration"]["observed_integral"] if role == "dos" else None
    return {
        "artifact_id": artifact_id,
        "schema_version": payload["schema_version"],
        "media_type": "application/json",
        "size_bytes": len(content),
        "sha256": combined_content_hash(payload),
        "payload": payload,
        "canonicalization": {
            "source_frequency_unit": source_unit,
            "frequency_factor_to_terahertz": convert_frequency(1.0, source_unit, "terahertz"),
            "density_jacobian_applied": converted if role == "dos" else False,
            "broadening_width_converted": False,
            "integral_before": integral,
            "integral_after": integral,
        },
    }


def _context(tmp_path: Path, band: object, dos: object) -> ToolExecutionContext:
    registry = load_manifests()
    tool = registry.get_tool_by_id("phonon.band_dos")
    return ToolExecutionContext(
        job_id="job_h3",
        project_id="project_h3",
        dataset_id="dataset_h3",
        tool_id=tool.toolId,
        tool_version=tool.version,
        adapter_version="0.1.0",
        registry_version=registry.version,
        artifact_root=tmp_path / "artifacts",
        tool_call_id="call_h3",
        object_store={"band_artifact": band, "dos_artifact": dos},
        resource_limits=tool.resourceLimits,
    )


def _request(params: dict | None = None, *, reverse: bool = False) -> ToolExecutionRequest:
    refs = [
        {"refType": "artifact", "ref": "band_artifact", "fieldRole": "band", "objectType": "PhononBand"},
        {"refType": "artifact", "ref": "dos_artifact", "fieldRole": "dos", "objectType": "PhononDos"},
    ]
    return ToolExecutionRequest(
        jobId="job_h3",
        stepId="step_001",
        toolId="phonon.band_dos",
        inputRefs=list(reversed(refs)) if reverse else refs,
        params=params or {},
        artifactTypes=ARTIFACT_TYPES,
    )


def _execute(tmp_path: Path, band: object | None = None, dos: object | None = None, params: dict | None = None, *, reverse: bool = False) -> tuple[list, dict[str, dict]]:
    artifacts = PhononBandDosAdapter().execute(_context(tmp_path, band or _band(), dos or _dos()), _request(params, reverse=reverse))
    payloads = {
        artifact.name: json.loads((tmp_path / "artifacts" / artifact.storageKey).read_text(encoding="utf-8"))
        for artifact in artifacts
    }
    return artifacts, payloads


def _profile() -> DataProfile:
    return DataProfile(
        profileId="profile_h3",
        datasetId="dataset_h3",
        version="1",
        datasetType="phonon",
        objects=[
            {"id": "band_artifact", "objectType": "PhononBand"},
            {"id": "dos_artifact", "objectType": "PhononDos"},
        ],
        phononSummary={"bandAvailable": True, "dosAvailable": True},
        createdAt="2026-07-14T00:00:00Z",
    )


def _plan(prompt: str) -> dict:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(prompt, "dataset_h3", "profile_h3", registry.version),
        tools=registry.list_mvp_tools(),
        data_profile=_profile(),
    )
    assert response.raw_json is not None
    return response.raw_json


def test_registry_declares_one_formal_combined_tool() -> None:
    registry = load_manifests()
    matches = [tool for tool in registry.tools if tool.toolId == "phonon.band_dos"]
    assert len(matches) == 1
    tool = matches[0]
    assert tool.stage == "mvp" and tool.adapter == "PhononBandDosAdapter"
    assert tool.implementationSource == "pymatviz_composed"
    assert tool.inputSchema.inputOptions[0].requiredObjectTypes == ["PhononBand", "PhononDos"]
    assert tool.paramsSchema["additionalProperties"] is False
    assert [item.value for item in tool.artifactTypes] == ARTIFACT_TYPES
    assert "shared-frequency-axis" in tool.description and "eigenvectors" in tool.description


def test_composer_emits_reference_only_combined_contract_and_valid_products() -> None:
    products = compose_phonon_band_dos(_band(), _dos(), selected_projection_ids=["atom:0"])
    assert products.combined["schema_version"] == PHONON_BAND_DOS_SCHEMA_VERSION
    assert "branches" not in products.combined and "frequencies" not in products.combined
    assert products.combined["band"]["schema_version"] == "phase10h.phonon_band.v1"
    assert products.combined["dos"]["schema_version"] == "phase10h.phonon_dos.v1"
    assert products.compatibility_report["schema_version"] == PHONON_BAND_DOS_COMPATIBILITY_SCHEMA_VERSION
    assert [item["name"] for item in products.compatibility_report["checks"]] == list(COMBINED_CHECK_ORDER)
    assert products.plot["schema_version"] == PHONON_BAND_DOS_PLOT_SCHEMA_VERSION
    assert products.plot["layout"] == "band_left_dos_right"
    assert products.plot["dos_panel"]["y_axis"] == "shared_frequency"
    assert products.summary["schema_version"] == PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION
    assert products.manifest["schema_version"] == PHONON_BAND_DOS_MANIFEST_SCHEMA_VERSION
    assert validate_phonon_band_dos(products.combined).valid
    assert validate_phonon_band_dos_summary(products.summary).valid
    assert validate_phonon_band_dos_compatibility_report(products.compatibility_report).valid
    assert validate_phonon_band_dos_plot(products.plot).valid
    assert validate_phonon_band_dos_table(products.table).valid
    assert validate_phonon_band_dos_manifest(products.manifest).valid


def test_manual_domain_is_explicit_view_only_and_does_not_mutate_inputs() -> None:
    band, dos = _band(), _dos()
    original_band, original_dos = copy.deepcopy(band), copy.deepcopy(dos)
    products = compose_phonon_band_dos(
        band,
        dos,
        domain_policy="manual_view",
        manual_frequency_domain=(-0.5, 4.0),
    )
    assert products.combined["frequency_axis"]["domain_policy"] == "manual_view"
    assert products.plot["shared_frequency_axis"]["domain_policy"] == "manual_view"
    assert products.compatibility_report["frequency_domain"]["union"] == [-1.0, 5.0]
    assert band == original_band and dos == original_dos


@pytest.mark.parametrize("unit", ["inverse_centimeter", "millielectronvolt"])
def test_proven_unit_conversion_is_reported_as_convertible_with_dos_jacobian(unit: str) -> None:
    products = compose_phonon_band_dos(
        _envelope(_band(), "band-source", source_unit=unit, role="band"),
        _envelope(_dos(), "dos-source", source_unit=unit, role="dos"),
    )
    report = products.compatibility_report
    frequency_check = next(item for item in report["checks"] if item["name"] == "frequency_unit")
    assert report["status"] == "convertible"
    assert frequency_check["status"] == "convertible"
    assert frequency_check["result_code"] == "PHONON_BAND_DOS_UNIT_CONVERSION_APPLIED"
    assert report["conversion"]["density_jacobian_applied"] is True
    assert report["conversion"]["integral_before"] == pytest.approx(report["conversion"]["integral_after"])


def test_density_conversion_preserves_integral_and_scales_broadening() -> None:
    result = convert_dos_frequency_density(
        [-10.0, 0.0, 10.0],
        [0.1, 0.2, 0.1],
        [[0.05, 0.1, 0.05]],
        source_unit="inverse_centimeter",
        broadening_width=2.0,
    )
    assert result["integral_before"] == pytest.approx(result["integral_after"])
    assert result["density_jacobian"] == pytest.approx(1 / result["factor"])
    assert result["broadening_width"] == pytest.approx(2 * result["factor"])


def test_structure_mismatch_and_hash_mismatch_fail_before_success_products(tmp_path: Path) -> None:
    incompatible = _dos()
    incompatible["structure_identity"] = "b" * 64
    with pytest.raises(PhononBandDosContractError) as contract_error:
        compose_phonon_band_dos(_band(), incompatible)
    assert contract_error.value.code == "PHONON_BAND_DOS_STRUCTURE_MISMATCH"
    with pytest.raises(ToolExecutionError) as adapter_error:
        PhononBandDosAdapter().execute(_context(tmp_path, _band(), incompatible), _request())
    assert adapter_error.value.details["errorType"] == "PHONON_BAND_DOS_STRUCTURE_MISMATCH"
    assert not (tmp_path / "artifacts").exists()

    bad_hash = _envelope(_dos(), "dos-source", role="dos")
    bad_hash["sha256"] = "0" * 64
    with pytest.raises(PhononBandDosContractError) as hash_error:
        compose_phonon_band_dos(_band(), bad_hash)
    assert hash_error.value.code == "PHONON_BAND_DOS_ARTIFACT_HASH_MISMATCH"


def test_adapter_role_binding_is_order_independent_and_strict(tmp_path: Path) -> None:
    artifacts, payloads = _execute(tmp_path, reverse=True)
    assert [artifact.name for artifact in artifacts] == [
        "phonon_band_dos.json",
        "phonon_band_dos_summary.json",
        "phonon_band_dos_compatibility_report.json",
        "phonon_band_dos_plot.json",
        "phonon_band_dos_table.json",
        "phonon_band_dos_manifest.json",
        "recipe.json",
    ]
    assert payloads["phonon_band_dos.json"]["compatibility"]["status"] == "compatible"
    invalid = _request().model_dump(mode="json")
    invalid["inputRefs"][1]["fieldRole"] = "band"
    with pytest.raises(ToolExecutionError) as exc:
        PhononBandDosAdapter().execute(_context(tmp_path / "invalid", _band(), _dos()), invalid)
    assert exc.value.details["errorType"] == "PHONON_BAND_DOS_INPUT_BINDING_INVALID"


def test_planner_routes_combined_only_for_static_supported_intent() -> None:
    for prompt in (
        "Show a combined phonon band + DOS with shared frequency axis",
        "Plot phonon bands with DOS",
        "\u8054\u5408\u663e\u793a\u58f0\u5b50\u80fd\u5e26\u548cDOS",
    ):
        plan = _plan(prompt)
        assert plan["steps"][0]["toolId"] == "phonon.band_dos"
        assert [ref["fieldRole"] for ref in plan["steps"][0]["inputRefs"]] == ["band", "dos"]
        assert validate_plan(plan, registry=load_manifests()).ok
    for prompt in (
        "Animate phonon eigenvectors with the DOS",
        "Calculate phonon bands and DOS from force constants",
        "Compute phonon heat capacity",
        "Show the Brillouin zone and DOS",
    ):
        assert _plan(prompt)["steps"][0]["toolId"] != "phonon.band_dos"


def test_runtime_and_planner_job_persist_deterministic_combined_artifacts(tmp_path: Path) -> None:
    registry = load_manifests()
    plan = _plan("Show a combined phonon band + DOS with shared frequency axis")
    outputs: list[dict[str, object]] = []
    for suffix in ("first", "second"):
        repositories = InMemoryRepositoryBundle.create()
        root = tmp_path / suffix
        runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=root)
        created = planner_jobs(
            PlannerJobsRequest(
                userPrompt="Show a combined phonon band + DOS with shared frequency axis",
                projectId="project_h3",
                datasetId="dataset_h3",
                profileId="profile_h3",
                enqueue=True,
            ),
            provider=MockLLMProvider(fixed_plan=plan),
            repositories=repositories,
            queue_runtime=runtime,
            registry=registry,
        )
        assert created.ok and created.job_id and created.enqueued
        result = runtime.handle_job(created.job_id, object_store={"band_artifact": _band(), "dos_artifact": _dos()})
        assert result.status == "completed"
        records = repositories.artifacts.list_for_job(created.job_id)
        assert [record["name"] for record in records] == [
            "phonon_band_dos.json",
            "phonon_band_dos_summary.json",
            "phonon_band_dos_compatibility_report.json",
            "phonon_band_dos_plot.json",
            "phonon_band_dos_table.json",
            "phonon_band_dos_manifest.json",
            "recipe.json",
        ]
        assert all(record["metadata"]["provenance"]["toolId"] == "phonon.band_dos" for record in records)
        outputs.append({record["name"]: json.loads((root / record["storageKey"]).read_text(encoding="utf-8")) for record in records})
    assert outputs[0] == outputs[1]


def test_security_and_unknown_fields_never_reach_combined_output(tmp_path: Path) -> None:
    malicious = _dos()
    malicious["module"] = "https://example.invalid/phonon.js"
    with pytest.raises(ToolExecutionError) as exc:
        PhononBandDosAdapter().execute(_context(tmp_path, _band(), malicious), _request())
    assert exc.value.details["errorType"] == "PHONON_BAND_DOS_DOS_ARTIFACT_INVALID"
    assert not (tmp_path / "artifacts").exists()
