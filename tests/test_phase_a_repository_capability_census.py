from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


pytestmark = pytest.mark.qualification


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "qualification" / "phase_a_repository_capability_census"


def load(name: str):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_phase_a_inventory_is_complete_and_grounded() -> None:
    tools = load("registry_tool_qualification_inventory.json")["tools"]
    renderers = load("renderer_qualification_inventory.json")["renderers"]
    cases = load("proposed_qualification_cases.json")["cases"]
    assert len(tools) == 62
    assert sum(row["plannerVisible"] for row in tools) == 47
    assert len(renderers) == 42
    assert all(row["repositoryEvidenceRefs"] for row in tools)
    assert all(row["repositoryEvidenceRefs"] for row in renderers)
    assert all(row["repositoryEvidenceRefs"] and row["externalDataRequirementIds"] for row in cases)


def test_phase_a_required_deliverables_and_classifications() -> None:
    required = {
        "README.md", "SystemQualificationCapabilityManifest.md", "entry_gate.json", "current_authorities.json",
        "user_entry_inventory.json", "file_format_inventory.json", "semantic_data_kind_inventory.json",
        "input_support_matrix.json", "input_support_matrix.csv", "capability_family_inventory.json",
        "registry_tool_qualification_inventory.json", "capability_matrix.json", "capability_matrix.csv",
        "artifact_qualification_inventory.json", "renderer_qualification_inventory.json", "output_matrix.json",
        "output_matrix.csv", "interpretation_inventory.json", "report_recipe_inventory.json",
        "negative_case_catalog.json", "existing_evidence_matrix.json", "existing_evidence_matrix.csv",
        "external_data_requirements.json", "external_data_requirement_matrix.csv",
        "proposed_qualification_cases.json", "minimum_case_set.json", "extended_case_set.json",
        "qualification_coverage_matrix.json", "qualification_coverage_matrix.csv", "authority_conflicts.json",
        "qualification_design_gaps.json", "qualification_readiness.json",
        "phase_b_external_qualification_dataset_research_handoff.json", "manifest.json",
    }
    assert required <= {path.name for path in OUT.iterdir() if path.is_file()}
    assert all(row["entryPathId"] for row in load("user_entry_inventory.json")["entries"])
    assert all(row["qualificationParticipationClass"] for row in load("registry_tool_qualification_inventory.json")["tools"])
    assert all(isinstance(row["releaseRelevant"], bool) for row in load("artifact_qualification_inventory.json")["artifacts"])
    assert all(row["classification"] for row in load("renderer_qualification_inventory.json")["renderers"])


def test_phase_a_support_boundaries_are_preserved() -> None:
    rows = load("input_support_matrix.json")["rows"]
    keyed = {(row["format"], row["semanticDataKind"]): row["supportDisposition"] for row in rows}
    assert keyed[("TYPED_PHONON_BAND_JSON", "phonon_band")] == "SUPPORTED_WITH_LIMITS"
    assert keyed[("TYPED_PHONON_DOS_JSON", "phonon_dos")] == "SUPPORTED_WITH_LIMITS"
    assert keyed[("GENERIC_PHONON_YAML_JSON", "phonon_band")] == "MAPPING_ONLY"
    assert keyed[("EXCEL", "materials_tabular_dataset")] == "UNSUPPORTED"


def test_phase_a_case_coverage_and_readiness() -> None:
    coverage = load("qualification_coverage_matrix.json")["counts"]
    assert coverage["CAPABILITY_FAMILIES_WITH_CASE_COVERAGE"] == coverage["TOTAL_CAPABILITY_FAMILIES"]
    assert coverage["REGISTRY_TOOLS_WITH_CASE_PARTICIPATION"] == coverage["TOTAL_RELEASE_RELEVANT_TOOLS"]
    assert coverage["INPUT_COMBINATIONS_WITH_CASE_COVERAGE"] == (
        coverage["TOTAL_SUPPORTED_INPUT_COMBINATIONS"]
        + coverage["TOTAL_SUPPORTED_WITH_LIMITS_INPUT_COMBINATIONS"]
    )
    assert load("qualification_readiness.json")["QUALIFICATION_DATA_RESEARCH_READY"] == "YES"
    assert load("authority_conflicts.json")["rowCount"] == 0
    gaps = {row["gapId"] for row in load("qualification_design_gaps.json")["gaps"]}
    assert "GAP-PHONON-ANIMATION-NORMAL-USER-ENTRY" in gaps


def test_phase_a_repository_evidence_references_exist() -> None:
    refs: set[str] = set()

    def collect(value) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "repositoryEvidenceRefs":
                    refs.update(item)
                collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)

    for path in OUT.glob("*.json"):
        if path.name != "manifest.json":
            collect(json.loads(path.read_text(encoding="utf-8")))
    assert refs
    assert not [ref for ref in sorted(refs) if not (ROOT / ref).exists()]


def test_phase_a_manifest_self_check() -> None:
    manifest = load("manifest.json")
    assert manifest["manifestMissingFiles"] == 0
    assert manifest["manifestHashMismatches"] == 0
    for item in manifest["files"]:
        path = OUT / item["path"]
        assert path.is_file()
        raw = path.read_bytes()
        assert len(raw) == item["bytes"]
        assert hashlib.sha256(raw).hexdigest() == item["sha256"]


def test_phase_a_has_no_execution_or_support_mutation() -> None:
    manifest = load("manifest.json")
    for key in (
        "productionCodeChanges", "scientificBehaviorChanges", "inputSupportChanges", "registryChanges",
        "parserChanges", "adapterChanges", "rendererChanges", "apiBehaviorChanges", "downloadedExternalFixtures",
        "liveChromeQualificationCases", "liveDeepSeekQualificationCases", "realLlmCalls",
    ):
        assert manifest[key] == 0
    assert manifest["webAccessForCapabilityDiscovery"] is False
