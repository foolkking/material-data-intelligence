from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "phase10n"
REGISTRY_DOCS = [
    DOCS / "phase10n_implementation_backlog.md",
    DOCS / "phase10n_acceptance_and_test_plan.md",
    DOCS / "phase10n_execution_lock.md",
    DOCS / "phase10n_execution_manifest.md",
]
EXPECTED = [
    "N0-A01 BASELINE_AND_REPOSITORY_FACT_AUDIT",
    "N0-A02 DEPENDENCY_VERSION_LICENSE_AND_UPSTREAM_CAPABILITY_AUDIT",
    "N0-A03 CURRENT_PROFESSIONAL_SCIENTIFIC_CAPABILITY_INVENTORY",
    "N0-A04 IDENTITY_UNITS_AUTHORITY_AND_SCIENTIFIC_WORDING_SEAL",
    "N0-A05 N1_COORDINATION_SCOPE_SEAL",
    "N0-A06 N2_LOCAL_ENVIRONMENT_AND_POLYHEDRA_SCOPE_SEAL",
    "N0-A07 N3_EXPERIMENTAL_XRD_COMPARISON_SCOPE_SEAL",
    "N0-A08 N4_TRAJECTORY_ANALYTICS_SCOPE_SEAL",
    "N0-A09 N5_ELECTRONIC_BAND_AND_DOS_SCOPE_SEAL",
    "N0-A10 CROSS_CUTTING_CONTRACT_REFERENCE_TOLERANCE_PERFORMANCE_AND_SECURITY_SEAL",
    "N0-A11 N1_TO_N6_IMPLEMENTATION_SEQUENCE_ACCEPTANCE_AND_EXECUTION_LOCK",
    "N0-A12 AUDIT_EVIDENCE_DOCUMENTATION_EXACT_SHA_LIFECYCLE_AND_REVIEWER_GATE",
]


def canonical_section(text: str) -> str:
    marker = "## Canonical Phase 10N-0 Acceptance Registry"
    assert text.count(marker) == 1
    section = text.split(marker, 1)[1]
    return section.split("\n## ", 1)[0]


def registry_entries(text: str) -> list[str]:
    section = canonical_section(text)
    return re.findall(r"`(N0-A\d{2} [A-Z0-9_]+)`", section)


def test_canonical_n0_registry_is_identical_across_four_documents() -> None:
    parsed = [registry_entries(path.read_text(encoding="utf-8")) for path in REGISTRY_DOCS]
    assert parsed == [EXPECTED] * 4
    assert all(len(set(entries)) == 12 for entries in parsed)
    assert not any("through" in canonical_section(path.read_text(encoding="utf-8")) for path in REGISTRY_DOCS)


def test_n0_registry_has_no_extra_canonical_ids() -> None:
    for path in REGISTRY_DOCS:
        entries = registry_entries(path.read_text(encoding="utf-8"))
        assert all(entry in EXPECTED for entry in entries)
        assert not re.search(r"`N0-A(?:1[3-9]|[2-9][0-9])\b", canonical_section(path.read_text(encoding="utf-8")))


def test_n0_does_not_admit_an_executable_task() -> None:
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    # N0 itself never admitted a task; the corrective N1 authorization may
    # subsequently admit the sole N1 task while N2 remains a reviewer gate.
    assert tasks.count("---TASK---") == tasks.count("---END---")
    assert tasks.count("---TASK---") in {0, 1}
    if "Phase 10N-1" in tasks:
        assert "Phase 10N-2:\nREVIEWER_GATE" in tasks
    else:
        assert "Phase 10N-2:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT" in tasks


def test_n0_decision_registry_is_contiguous_and_review_gated() -> None:
    text = (DOCS / "phase10n0_decision_log.md").read_text(encoding="utf-8")
    ids = re.findall(r"\| (N-D\d{3}) \|", text)
    assert ids == [f"N-D{index:03d}" for index in range(1, 34)]
    assert text.count("SEALED_FOR_REVIEWER_APPROVAL") == 34


def test_n0_evidence_manifest_is_complete_and_hashed() -> None:
    evidence = DOCS / "evidence" / "phase10n0_professional_scientific_gap_audit"
    required = {
        "baseline.txt", "git_history.txt", "repository_status.txt", "m7_lifecycle_verification.txt",
        "dependency_inventory.json", "dependency_license_matrix.md", "runtime_import_versions.txt",
        "upstream_source_inventory.md", "registry_inventory.json", "adapter_inventory.json",
        "artifact_inventory.json", "profile_fact_inventory.json", "viewer_inventory.json",
        "interpretation_projector_inventory.json", "workspace_panel_inventory.json",
        "report_recipe_inventory.json", "current_capability_matrix.md", "long_list_classification.md",
        "identity_audit.md", "units_audit.md", "wording_audit.md", "reference_fixture_inventory.md",
        "tolerance_plan.md", "performance_cap_plan.md", "security_boundary.md", "n1_scope_evidence.md",
        "n2_scope_evidence.md", "n3_scope_evidence.md", "n4_scope_evidence.md", "n5_scope_evidence.md",
        "n6_scope_evidence.md", "migration_api_dependency_decisions.md", "acceptance_registry.md",
        "decision_registry.md", "docs_link_check.txt", "secret_scan.txt", "verification_summary.md",
        "browser_replay.md", "service_backed_summary.md", "npm_audit.md", "screenshots/README.md",
    }
    manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
    entries = manifest["entries"]
    assert {entry["path"] for entry in entries} == required
    assert len(entries) == len(required) == len({entry["path"] for entry in entries})
    for entry in entries:
        raw = (evidence / entry["path"]).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
    assert manifest["missing_entries"] == 0
    assert manifest["duplicate_entries"] == 0
    assert manifest["secret_entries"] == 0


def test_n0_required_docs_are_present_and_scope_is_non_executable() -> None:
    required = {
        "phase10n0_professional_scientific_capability_gap_audit.md",
        "phase10n0_current_capability_inventory.md",
        "phase10n0_dependency_version_license_matrix.md",
        "phase10n0_long_list_scope_classification.md",
        "phase10n0_identity_units_authority_wording_seal.md",
        "phase10n0_reference_fixture_and_tolerance_policy.md",
        "phase10n0_performance_security_and_resource_caps.md",
        "phase10n0_data_profile_registry_planner_contract_audit.md",
        "phase10n0_workspace_interpretation_report_integration.md",
        "phase10n0_decision_log.md",
        "phase10n_implementation_backlog.md",
        "phase10n_acceptance_and_test_plan.md",
        "phase10n_execution_lock.md",
        "phase10n_execution_manifest.md",
        "phase10n1_coordination_scope.md",
        "phase10n2_local_environment_polyhedra_scope.md",
        "phase10n3_experimental_xrd_scope.md",
        "phase10n4_trajectory_analytics_scope.md",
        "phase10n5_electronic_band_dos_scope.md",
        "phase10n6_integration_evidence_scope.md",
        "phase10n1_next_scope.md",
    }
    assert required <= {path.name for path in DOCS.glob("*.md")}
    next_scope = (DOCS / "phase10n1_next_scope.md").read_text(encoding="utf-8")
    if "ACTIVE_IMPLEMENTATION_SCOPE" in next_scope:
        assert "REVIEWER_APPROVAL_GRANTED" in next_scope
    else:
        assert "REVIEWER_GATE" in next_scope and "NOT QUEUED" in next_scope and "NOT EXECUTABLE" in next_scope
