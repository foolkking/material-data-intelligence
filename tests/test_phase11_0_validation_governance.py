from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from mdi_adapters.registry import ADAPTER_CLASSES
from mdi_tool_registry.loader import load_manifests


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase11/evidence/phase11_0_validation_baseline_reconciliation"
ACCEPTANCE_IDS = [f"P11V0-A{index:02d}" for index in range(1, 11)]


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_registry_inventory_matches_live_registry_and_adapter_disposition() -> None:
    live = load_manifests()
    inventory = load("registry_inventory.json")
    rows = inventory["tools"]
    assert len(live.tools) == inventory["registryCount"] == len(rows) == 62
    assert len({row["toolId"] for row in rows}) == 62
    assert {row["toolId"] for row in rows} == {tool.toolId for tool in live.tools}
    assert all(row["roleClass"] for row in rows)
    assert all(row["adapterRegistered"] == (row["adapter"] in ADAPTER_CLASSES) for row in rows)
    assert all(row["availability"] != "RUNTIME_REGISTERED" or row["adapterRegistered"] for row in rows)
    assert all(len(row["scientificReferenceStatus"]) > 0 for row in rows)


def test_all_phase10n_professional_tools_remain_exact() -> None:
    expected = {
        "structure.coordination_crystalnn", "structure.coordination_voronoinn",
        "structure.local_environment_polyhedra", "structure.experimental_xrd_comparison",
        "trajectory.rdf", "trajectory.msd", "trajectory.diffusion",
        "electronic.band_structure", "electronic.dos",
    }
    rows = load("registry_inventory.json")["tools"]
    selected = {row["toolId"]: row for row in rows if row["toolId"] in expected}
    assert set(selected) == expected
    assert all(row["version"] == "0.1.0" for row in selected.values())
    assert all(row["adapterRegistered"] for row in selected.values())


def test_input_support_verdicts_are_explicit_and_honest() -> None:
    matrix = load("input_support_matrix.json")
    rows = matrix["inputs"]
    allowed = {"DIRECT_SUPPORTED", "SUPPORTED_WITH_LIMITS", "MAPPING_ONLY", "PARSE_ONLY", "UNSUPPORTED", "FUTURE_SCOPE"}
    assert matrix["rowCount"] == len(rows) >= 14
    assert len({row["inputFamily"] for row in rows}) == len(rows)
    assert all(row["supportVerdict"] in allowed for row in rows)
    by_name = {row["inputFamily"]: row for row in rows}
    assert by_name["XLSX/Excel"]["supportVerdict"] == "UNSUPPORTED"
    assert by_name["Parquet"]["supportVerdict"] == "UNSUPPORTED"
    assert by_name["LAMMPS trajectory"]["supportVerdict"] == "UNSUPPORTED"
    assert by_name["Phonon YAML/JSON"]["supportVerdict"] == "MAPPING_ONLY"
    assert by_name["Supplied electronic Band/DOS JSON"]["supportVerdict"] == "SUPPORTED_WITH_LIMITS"


def test_validation_axes_and_honesty_markers_are_separate() -> None:
    matrix = load("tool_validation_matrix.json")
    required = {
        "softwareExecutionStatus", "scientificReferenceStatus", "numericValidationStatus",
        "artifactContractStatus", "platformIntegrationStatus", "browserStatus",
        "serviceStatus", "reproducibilityStatus", "knownLimits",
    }
    assert matrix["axesAreIndependent"] is True
    assert matrix["rowCount"] == 62
    assert all(required <= row.keys() for row in matrix["tools"])
    governance = (ROOT / "docs/phase11/phase11_validation_governance.md").read_text(encoding="utf-8")
    for marker in (
        "SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE",
        "BROWSER_PASS_EQUALS_NUMERIC_REFERENCE_PASS = NO",
        "SERVICE_PASS_EQUALS_NUMERIC_REFERENCE_PASS = NO",
        "FIXTURE_EXISTS_EQUALS_REFERENCE_VERIFIED = NO",
        "MAPPING_EQUALS_VERIFIED = NO",
        "SELF_REFERENCE_EQUALS_INDEPENDENT_REFERENCE = NO",
        "LATEST_EVIDENCE_WINS_AUTHORITY = NO",
        "GLOBAL_SCIENTIFIC_EPSILON = NONE",
        "PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED",
    ):
        assert marker in governance


def test_acceptance_registry_is_exact_in_canonical_documents() -> None:
    registry = load("phase11_acceptance_registry.json")
    assert registry["expected"] == registry["implemented"] == 10
    assert registry["missing"] == registry["extra"] == registry["duplicate"] == registry["conflicting"] == registry["shorthand"] == 0
    assert [entry.split()[0] for entry in registry["entries"]] == ACCEPTANCE_IDS
    for name in (
        "phase11_acceptance_and_test_plan.md", "phase11_execution_lock.md",
        "phase11_execution_manifest.md",
    ):
        text = (ROOT / "docs/phase11" / name).read_text(encoding="utf-8")
        assert [identifier for identifier in ACCEPTANCE_IDS if identifier in text] == ACCEPTANCE_IDS


def test_gap_backlog_has_no_catch_all_or_tbd() -> None:
    payload = load("gap_matrix.json")
    assert payload["gapCount"] == len(payload["gaps"]) > 0
    assert payload["p0Count"] == 0
    required = {"gapId", "priority", "capability", "currentEvidence", "missingEvidence", "whyNeeded", "targetPhase", "blockingRelease", "recommendedReferenceType"}
    assert all(required <= row.keys() for row in payload["gaps"])
    serialized = json.dumps(payload).lower()
    assert "tbd" not in serialized
    assert "needs more validation" not in serialized


def test_tolerances_have_owners_and_no_global_epsilon() -> None:
    payload = load("tolerance_inventory.json")
    assert payload["globalScientificEpsilon"] is None
    assert payload["passDrivenChanges"] == "PROHIBITED"
    required = {"toleranceId", "toolContract", "fieldMetric", "absTolerance", "relativeTolerance", "unit", "referenceProvenance", "reason", "ownerPhase", "scientificJustification", "platformVarianceRelevance", "reviewStatus"}
    assert all(required <= row.keys() for row in payload["tolerances"])
    assert any(row["unit"] == "EXACT" for row in payload["tolerances"])


def test_evidence_manifest_is_normalized_and_complete() -> None:
    manifest = load("manifest.json")
    assert manifest["entryCount"] == len(manifest["entries"]) > 0
    assert manifest["missingFiles"] == manifest["hashMismatch"] == manifest["secretBearingEvidence"] == 0
    expected = {path.relative_to(EVIDENCE).as_posix() for path in EVIDENCE.rglob("*") if path.is_file() and path.name != "manifest.json"}
    actual = {entry["path"] for entry in manifest["entries"]}
    assert actual == expected
    for entry in manifest["entries"]:
        path = EVIDENCE / entry["path"]
        assert path.stat().st_size == entry["bytes"]
        assert digest(path) == entry["sha256"]


def test_roadmap_and_queue_boundaries_are_exact() -> None:
    roadmap = (ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    assert "Phase 11 - Scientific Validation" in roadmap
    assert "Phase 12 - Comprehensive UI/UX Product Experience Redesign" in roadmap
    assert "Phase 13 - Final Product Closure" in roadmap
    assert "SUPERSEDED_BY_APPROVED_ROADMAP_REVISION" in roadmap
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    blocks = re.findall(r"---TASK---.*?---END---", tasks, flags=re.DOTALL)
    if not blocks:
        return
    if "Phase 12-0 Current UX Reality Audit" in blocks[0]:
        assert len(blocks) == 1
        assert "状态：处理中" in blocks[0] or "状态：已完成" in blocks[0]
        return
    assert len(blocks) in {0, 1, 2, 3}
    if blocks and "Phase 11-4 Reviewer Prompt" in blocks[0]:
        assert len(blocks) == 2
        assert "状态：处理中" in blocks[0]
        assert "Phase 11-5 Reviewer Prompt" in blocks[1]
        return
    if blocks and "Phase 11-5 Reviewer Prompt" in blocks[0]:
        assert len(blocks) == 1
        assert "状态：处理中" in blocks[0]
        return
    if len(blocks) == 1:
        assert (
            "Phase 11-0 Validation Baseline Reconciliation + Governance Seal" in blocks[0]
            or "Phase 11-3 Reviewer Prompt" in blocks[0]
        )
        if "Phase 11-3 Reviewer Prompt" in blocks[0]:
            assert "状态：处理中" in blocks[0]
        assert "Task: Phase 11-1" not in blocks[0]
        assert "Task: Phase 12" not in blocks[0]
        assert "Task: Phase 13" not in blocks[0]
    if len(blocks) == 3:
        assert "Phase 11-1 Reviewer Prompt" in blocks[0]
        assert "状态：处理中" in blocks[0]
        assert "Phase 11-2 Reviewer Prompt" in blocks[1]
        assert "Phase 11-3 Reviewer Prompt" in blocks[2]
    if len(blocks) == 2:
        assert "Phase 11-2 Reviewer Prompt" in blocks[0]
        assert "状态：处理中" in blocks[0]
        assert "Phase 11-3 Reviewer Prompt" in blocks[1]


def test_no_production_contract_change_markers() -> None:
    text = (ROOT / "docs/phase11/phase11_0_validation_baseline_reconciliation.md").read_text(encoding="utf-8")
    for marker in (
        "PHASE11_0_NEW_SCIENTIFIC_TOOLS = 0",
        "PHASE11_0_NEW_SCIENTIFIC_ALGORITHMS = 0",
        "PHASE11_0_NEW_ARTIFACT_FAMILIES = 0",
        "PHASE11_0_NEW_DATAPROFILE_VERSION = 0",
        "PHASE11_0_NEW_ANALYSISPLAN_VERSION = 0",
        "PHASE11_0_NEW_PUBLIC_API_FAMILIES = 0",
        "PHASE11_0_NEW_DATABASE_MIGRATIONS = 0",
        "PHASE11_0_NEW_DEPENDENCIES = 0",
        "PHASE11_0_NEW_LLM_CALL_SITES = 0",
        "PHASE11_0_REAL_LLM_CALLS = 0",
        "REGISTRY_AFTER_11_0 = 62",
        "DATAPROFILE_AFTER_11_0 = 2.4",
    ):
        assert marker in text


def test_phase11_document_links_resolve_and_secret_patterns_are_absent() -> None:
    phase_root = ROOT / "docs/phase11"
    markdown = list(phase_root.glob("*.md"))
    assert markdown
    link_pattern = re.compile(r"\[[^]]+\]\(([^)]+)\)")
    for document in markdown:
        text = document.read_text(encoding="utf-8")
        for target in link_pattern.findall(text):
            if target.startswith(("http://", "https://", "#")):
                continue
            path = (document.parent / target.split("#", 1)[0]).resolve()
            assert path.exists(), f"broken link in {document.name}: {target}"
    audited = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in [*markdown, *EVIDENCE.rglob("*.md"), *EVIDENCE.rglob("*.txt"), *EVIDENCE.rglob("*.json")])
    assert "DEEPSEEK_KEY=" not in audited
    assert "Authorization: Bearer" not in audited
    assert not re.search(r"[A-Za-z]:\\Users\\", audited)
