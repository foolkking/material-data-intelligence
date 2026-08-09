from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

from mdi_llm.grounded_interpretation import ARTIFACT_PROJECTOR_CONTRACTS
from mdi_schemas import WorkspaceSelectionKind
from mdi_tool_registry import load_manifests
from mdi_tool_registry.dependency_ports import build_artifact_port_inventory
from mdi_tool_registry.planner_metadata import build_tool_planner_metadata


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10n/evidence/phase10n6_professional_capability_integration_closure"
TOOLS = (
    "structure.coordination_crystalnn", "structure.coordination_voronoinn",
    "structure.local_environment_polyhedra", "structure.experimental_xrd_comparison",
    "trajectory.rdf", "trajectory.msd", "trajectory.diffusion",
    "electronic.band_structure", "electronic.dos",
)


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_n6_registry_profile_and_acceptance_are_exact() -> None:
    registry = load_manifests()
    assert len(registry.tools) == 62
    assert tuple(tool.toolId for tool in registry.tools if tool.toolId in TOOLS) == TOOLS
    schema = (ROOT / "packages/schemas/mdi_schemas/models.py").read_text(encoding="utf-8")
    assert 'Literal["2.0", "2.1", "2.2", "2.3", "2.4"]' in schema
    expected = [f"N6-A{i:02d}" for i in range(1, 11)]
    for name in ("phase10n_acceptance_and_test_plan.md", "phase10n_implementation_backlog.md", "phase10n_execution_lock.md", "phase10n_execution_manifest.md"):
        text = (ROOT / "docs/phase10n" / name).read_text(encoding="utf-8")
        assert text.count("## Canonical Phase 10N-6 Acceptance Registry") == 1
        section = text.split("## Canonical Phase 10N-6 Acceptance Registry", 1)[1]
        definitions = re.findall(r"N6-A\d{2}", section)
        assert definitions[:10] == expected and len(set(definitions[:10])) == 10


def test_n6_all_tools_have_planner_ports_adapter_and_projector() -> None:
    registry = load_manifests()
    ports = build_artifact_port_inventory(registry)
    for tool_id in TOOLS:
        tool = registry.get_tool_by_id(tool_id)
        assert tool.version == "0.1.0" and tool.adapter
        assert build_tool_planner_metadata(tool).availability.value == "AVAILABLE"
        assert ports[tool_id].outputPorts
        assert (tool_id, "table_json") in ARTIFACT_PROJECTOR_CONTRACTS
    assert ports["structure.local_environment_polyhedra"].inputPorts[0].portId == "coordination"
    assert ports["structure.experimental_xrd_comparison"].inputPorts[0].portId == "theoretical-xrd"
    assert ports["trajectory.diffusion"].inputPorts[0].portId == "msd"


def test_n6_renderer_and_selection_dispositions_are_complete() -> None:
    renderer = (ROOT / "apps/web/app/components/workspace/workspace-renderer-registry.ts").read_text(encoding="utf-8")
    for contract in ("phase10n1.crystalnn_coordination.v1", "phase10n1.voronoinn_coordination.v1", "phase10n2.local_environment_polyhedra.v1", "phase10n3.experimental_xrd_comparison.v1", "phase10n4.trajectory_rdf.v1", "phase10n4.trajectory_msd.v1", "phase10n4.trajectory_diffusion.v1", "phase10n5.electronic_band_structure.v1", "phase10n5.electronic_dos.v1"):
        assert contract in renderer
    required = {"PERIODIC_SITE", "LOCAL_ENVIRONMENT", "COORDINATION_POLYHEDRON", "EXPERIMENTAL_XRD_PEAK", "THEORETICAL_XRD_PEAK", "XRD_MATCH", "TRAJECTORY_RDF_PAIR", "TRAJECTORY_MSD_LAG", "TRAJECTORY_DIFFUSION_WINDOW", "ELECTRONIC_KPOINT", "ELECTRONIC_BAND_STATE", "ELECTRONIC_DOS_PROJECTION"}
    assert required.issubset({item.value for item in WorkspaceSelectionKind})


def test_n6_dependency_and_authority_boundaries_are_preserved() -> None:
    matrix = load("plan_dependency_matrix.json")
    assert matrix["plan01Readable"] and matrix["exactPortBindings"]
    assert all(item.get("recomputation", item.get("reimplementation")) is False for item in matrix["plan02"])
    assert matrix["runtimeReplanning"] is False
    report = load("report_recipe/matrix.json")
    assert report == {"recipeExecutionAuthority": False, "recipeQueueAuthority": False, "reportGeneratedScientificValues": 0, "reportScientificRecomputation": 0}


def test_n6_identity_units_and_historical_closure() -> None:
    identity, units, history = load("identity_matrix.json"), load("unit_matrix.json"), load("historical_compatibility/matrix.json")
    assert not any(identity[key] for key in ("arrayPositionAuthority", "displayLabelAuthority", "filenameAuthority", "nearestFuzzyAuthority", "latestAuthority"))
    assert units["distance"] == "angstrom" and units["time"] == "ps" and units["energy"] == "eV" and units["silentConversion"] is False
    assert history["profiles"] == ["2.0", "2.1", "2.2", "2.3", "2.4"] and history["plans"] == ["0.1", "0.2"]
    assert history["backfill"] == history["readTimeScience"] == history["historicalRebinding"] == 0


def test_n6_retained_n1_n5_evidence_manifests_remain_complete() -> None:
    dirs = sorted(path for path in (ROOT / "docs/phase10n/evidence").iterdir() if path.is_dir() and re.match(r"phase10n[1-5]_", path.name))
    assert len(dirs) == 5
    for directory in dirs:
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        entries = manifest["entries"]
        assert entries
        for entry in entries:
            raw = (directory / entry["path"]).read_bytes()
            normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            assert sha256(normalized).hexdigest() == entry["sha256"]


def test_n6_evidence_inventory_and_manifest_are_exact() -> None:
    required = {"baseline.txt", "entry_gate.md", "n1_n5_authority_inventory.md", "n6_r0_integration_closure.md", "n6_acceptance_registry.md", "professional_capability_matrix.json", "professional_tool_inventory.json", "profile_readiness_matrix.json", "planner_eligibility_matrix.json", "plan_dependency_matrix.json", "artifact_contract_matrix.json", "identity_matrix.json", "unit_matrix.json", "scientific_wording_audit.md", "performance.json", "viewer_lifecycle.json", "accessibility.md", "security.md", "phase10n_final_acceptance.json", "docs_link_check.txt", "secret_scan.txt", "manifest.json", "n1_n2_end_to_end/cases.json", "n3_xrd_end_to_end/cases.json", "n4_trajectory_end_to_end/cases.json", "n5_electronic_end_to_end/cases.json", "negative_cases/matrix.json", "historical_compatibility/matrix.json", "workspace_selection/matrix.json", "interpretation/matrix.json", "report_recipe/matrix.json", "service_backed/status.md", "browser/matrix.json", "screenshots/README.md"}
    assert all((EVIDENCE / path).is_file() for path in required)
    manifest = load("manifest.json")
    actual = {path.relative_to(EVIDENCE).as_posix() for path in EVIDENCE.rglob("*") if path.is_file() and path.name != "manifest.json"}
    assert {item["path"] for item in manifest["entries"]} == actual
    assert manifest["missingFiles"] == manifest["extraRequiredFiles"] == manifest["hashMismatch"] == manifest["secretBearingEvidence"] == 0
    for item in manifest["entries"]:
        content = (EVIDENCE / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        assert sha256(content).hexdigest() == item["sha256"] and len(content) == item["bytes"]


def test_n6_security_and_scientific_negative_markers_are_closed() -> None:
    security = (EVIDENCE / "security.md").read_text(encoding="utf-8")
    wording = (EVIDENCE / "scientific_wording_audit.md").read_text(encoding="utf-8")
    assert "N6_NEW_LLM_CALL_SITES = 0" in security and "N6_REAL_LLM_CALLS_DEFAULT_CI = 0" in security
    assert "No arbitrary code" in security and "PASS" in wording
    assert load("n4_trajectory_end_to_end/cases.json")["ballisticAccepted"] is False
    assert load("n5_electronic_end_to_end/cases.json")["dft"] == 0


def test_n6_queue_lifecycle_and_no_phase11_task() -> None:
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    task_count = tasks.count("---TASK---")
    assert task_count == tasks.count("---END---")
    assert task_count in {0, 1, 2, 3}
    if task_count == 2 and "Phase 11-2 Reviewer Prompt" in tasks:
        assert "状态：处理中" in tasks
        return
    if task_count == 3 and "Phase 11-1 Reviewer Prompt" in tasks:
        assert "状态：处理中" in tasks
        return
    if task_count and "Task: Phase 11-0" in tasks:
        assert "Phase 10N-6:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
        assert "Task: Phase 11-1" not in tasks
    elif task_count:
        assert "Task: Phase 10N-6 Professional Capability Integration + Evidence Closure" in tasks
        assert any(
            state in tasks
            for state in (
                "Status: IN_PROGRESS",
                "Status: PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI",
            )
        )
    assert "Task: Phase 11-1" not in tasks


def test_n6_final_boundary_docs_do_not_queue_phase11() -> None:
    next_scope = (ROOT / "docs/phase10n/phase11_next_scope.md").read_text(encoding="utf-8")
    assert "REVIEWER_GATE" in next_scope and "NOT QUEUED" in next_scope and "NOT EXECUTABLE" in next_scope
    assert "Fermi surface" not in next_scope and "DFT" not in next_scope
