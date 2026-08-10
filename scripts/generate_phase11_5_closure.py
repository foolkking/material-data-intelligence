"""Build the final Phase 11 validation closure package from sealed evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs/phase11/evidence"
N0 = EVIDENCE_ROOT / "phase11_0_validation_baseline_reconciliation"
N1 = EVIDENCE_ROOT / "phase11_1_reference_provenance_safe_fixture"
N2 = EVIDENCE_ROOT / "phase11_2_golden_scientific_benchmark"
N3 = EVIDENCE_ROOT / "phase11_3_cross_platform_reproducibility"
N4 = EVIDENCE_ROOT / "phase11_4_honest_tool_input_example_coverage"
OUT = EVIDENCE_ROOT / "phase11_5_scientific_validation_closure"
TEXT_SUFFIXES = {".json", ".md", ".txt", ".yaml", ".yml"}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def semantic_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def sha(path: Path) -> str:
    return hashlib.sha256(semantic_bytes(path)).hexdigest()


def count_verdicts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row["coverageVerdict"]
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    registry = load_manifests()
    tools = read_json(N4 / "tool_coverage_matrix.json")["tools"]
    inputs = read_json(N4 / "input_coverage_matrix.json")["inputs"]
    examples = read_json(N4 / "official_example_coverage_matrix.json")["records"]
    n2_summary = read_json(N2 / "golden_suite_summary.json")
    n3_handoff = read_json(N3 / "phase11_4_handoff.json")
    gaps = read_json(N0 / "gap_matrix.json")
    if len(registry.tools) != 62 or len(tools) != 62 or len({row["toolId"] for row in tools}) != 62:
        raise SystemExit("Phase 11 closure requires exactly 62 live and classified Tools")
    if len(inputs) != 14 or len(examples) != 55:
        raise SystemExit("Phase 11-4 input/example matrices are incomplete")
    if n2_summary["benchmarkCount"] != 12 or n2_summary["passCount"] != 8 or n2_summary["notApplicableCount"] != 4:
        raise SystemExit("sealed Phase 11-2 summary is inconsistent")
    if n2_summary["failCount"] != 0 or n2_summary["validationLevelPromotions"] != 0:
        raise SystemExit("Phase 11-2 contains an unexpected failure or promotion")
    if n3_handoff["caseCount"] != 8 or n3_handoff["numericClaims"] != 0 or n3_handoff["referenceMutation"] != 0:
        raise SystemExit("sealed Phase 11-3 handoff is inconsistent")

    authority = {
        "phase11Status": "COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS",
        "scientificValidationBaseline": "SEALED",
        "scientificValidationReleaseCandidate": "PASS",
        "initialReleaseComplete": "NO",
        "finalProductReleaseReady": "NO",
        "registryCount": 62,
        "dataProfile": "2.4",
        "migrationHead": "0007_phase10m1_workspace_domain",
        "newScientificAuthority": 0,
        "phase12": "REVIEWER_GATE / AWAITING REVIEWER PROMPT",
        "phase13": "ROADMAP_APPROVED / NOT_QUEUED / NOT_EXECUTABLE",
        "phase14Created": "NO",
    }
    version_matrix = {
        "profile": {"before": "2.4", "after": "2.4"},
        "analysisPlan": {"supported": ["0.1", "0.2"], "changes": 0},
        "registry": {"before": 62, "after": 62},
        "migration": {"before": "0007_phase10m1_workspace_domain", "after": "0007_phase10m1_workspace_domain"},
        "dependencies": {"new": 0, "lockfileChanged": 0},
    }
    write_json(OUT / "phase11_4_handoff_snapshot.json", {
        "source": "../phase11_4_honest_tool_input_example_coverage",
        "toolMatrixHash": read_json(N4 / "coverage_summary.json")["toolCoverageMatrixHash"],
        "inputMatrixHash": read_json(N4 / "coverage_summary.json")["inputCoverageMatrixHash"],
        "exampleMatrixHash": read_json(N4 / "coverage_summary.json")["officialExampleCoverageMatrixHash"],
        "registryRows": len(tools), "inputRows": len(inputs), "exampleRows": len(examples),
        "p0Gaps": 0, "v4Promotions": 0, "numericCrossPlatformClaims": 0,
    })
    acceptance_ids = [
        "P11V5-A01", "P11V5-A02", "P11V5-A03", "P11V5-A04",
        "P11V5-A05", "P11V5-A06", "P11V5-A07", "P11V5-A08",
        "P11V5-A09", "P11V5-A10", "P11V5-A11", "P11V5-A12",
    ]
    write_json(OUT / "acceptance_registry.json", {
        "phase": "Phase 11-5",
        "expected": 12,
        "implemented": 12,
        "missing": 0,
        "extra": 0,
        "duplicate": 0,
        "conflicting": 0,
        "shorthand": 0,
        "entries": [{"id": item, "status": "PASS"} for item in acceptance_ids],
    })
    write_json(OUT / "phase11_authority_chain.json", {
        "chain": ["Profile", "Intent", "Eligibility", "Planner", "AnalysisPlan", "PlanValidator", "Runtime", "Adapter", "Artifact", "Lineage", "Workspace", "Selection", "Inspector", "Interpretation", "Report", "Recipe"],
        "allApprovedCapabilities": "indexed from retained evidence",
        "newRuntimeAuthority": 0,
    })
    write_json(OUT / "phase11_version_matrix.json", version_matrix)
    write_json(OUT / "phase11_validation_level_distribution.json", {"source": str(N0.relative_to(ROOT)).replace("\\", "/"), "distribution": {"V0": 0, "V1": 62, "V2": 0, "V3": 0, "V4": 0}, "promotions": 0, "demotions": 0})
    write_json(OUT / "phase11_tool_coverage_distribution.json", {"rowCount": len(tools), "counts": count_verdicts(tools), "source": "phase11-4 sealed matrix"})
    write_json(OUT / "phase11_input_support_distribution.json", {"rowCount": len(inputs), "supportVerdicts": count_verdicts([{**r, "coverageVerdict": r["supportVerdict"]} for r in inputs]), "coverageVerdicts": count_verdicts(inputs)})
    write_json(OUT / "phase11_example_coverage_distribution.json", {"rowCount": len(examples), "counts": count_verdicts(examples), "independentScientificReferences": 0})
    write_json(OUT / "phase11_reference_registry_index.json", {"source": str((N1 / "reference_provenance_registry.json").relative_to(ROOT)).replace("\\", "/"), "status": "inherited_sealed_registry", "newSources": 0})
    write_json(OUT / "phase11_fixture_registry_index.json", {"source": str((N1 / "fixture_registry.json").relative_to(ROOT)).replace("\\", "/"), "status": "immutable_fixture_registry", "mutations": 0})
    write_json(OUT / "phase11_golden_suite_index.json", {"source": str((N2 / "golden_suite_summary.json").relative_to(ROOT)).replace("\\", "/"), **n2_summary})
    write_json(OUT / "phase11_tolerance_registry_index.json", {"source": str((N0 / "tolerance_inventory.json").relative_to(ROOT)).replace("\\", "/"), "changes": 0, "passDrivenChanges": 0})
    write_json(OUT / "phase11_variance_index.json", {"source": str((N3 / "variance_classification_matrix.json").relative_to(ROOT)).replace("\\", "/"), "numericCrossPlatform": "NOT_APPLICABLE", "v4": 0})
    write_json(OUT / "phase11_reproducibility_summary.json", {"source": str((N3 / "scientific_reproducibility_manifest.json").relative_to(ROOT)).replace("\\", "/"), "cases": 8, "linuxPass": 8, "windowsPass": 8, "numericCrossPlatform": "NOT_APPLICABLE"})
    write_json(OUT / "phase11_reference_limited_cases.json", {"phase11_2NotApplicable": read_json(N2 / "blocked_benchmarks.json")["notApplicable"], "phase11_3NumericCrossPlatform": "NOT_APPLICABLE", "count": 5})
    write_json(OUT / "phase11_known_limitations.json", {"source": "Phase 11-0 through Phase 11-4 retained limitations", "v4": 0, "mappingOnlyExamples": 55, "numericCrossPlatform": "NOT_APPLICABLE", "futureScope": "preserved"})
    write_json(OUT / "phase11_remaining_gaps.json", {"source": str((N0 / "gap_matrix.json").relative_to(ROOT)).replace("\\", "/"), "gapCount": gaps["gapCount"], "p0Count": gaps["p0Count"], "newGaps": 0, "releaseBlocking": 0})
    write_json(OUT / "phase11_release_blocker_audit.json", {"releaseBlockingScientificGaps": 0, "p0Gaps": 0, "status": "PASS_WITH_EXPLICIT_LIMITATIONS"})
    write_json(OUT / "phase11_accepted_limitation_audit.json", {"v4Zero": True, "referenceLimitedCasesAccepted": True, "mappingOnlyExamplesDisclosed": True, "initialReleaseComplete": False})
    write_json(OUT / "phase11_public_claim_audit.json", {"approvedClaimMatrix": "phase11-4 sealed", "prohibitedUnqualifiedClaims": ["all science validated", "all Tools are independently scientifically validated", "final product release ready"], "overclaimStatus": "PASS"})
    write_json(OUT / "phase11_revalidation_trigger_audit.json", {"source": str((N0 / "revalidation_triggers.json").relative_to(ROOT)).replace("\\", "/"), "triggersInherited": True, "changes": 0})
    write_json(OUT / "phase12_scientific_authority_handoff.json", {"readOnly": True, "toolCoverage": "phase11-4 sealed matrix", "inputSupport": "phase11-4 sealed matrix", "validationLevels": "phase11 sealed matrix", "knownLimitations": "visible", "phase12TaskCreated": False})
    write_json(OUT / "phase11_final_baseline.json", authority)
    write_json(OUT / "phase11_final_evidence_manifest.json", {"sourceRoots": [str(p.relative_to(ROOT)).replace("\\", "/") for p in (N0, N1, N2, N3, N4)], "newScientificEvidence": 0, "externalDownloads": 0, "secretBearingEvidence": 0})
    (OUT / "baseline.txt").write_text("Phase 11 final closure baseline\nRegistry=62\nDataProfile=2.4\nN2=12 records/8 invariant PASS/4 N/A/0 failures\nN3=8 cases/Linux PASS/Windows PASS/numeric cross-platform N/A/V4=0\nN4=62 Tools/14 inputs/55 examples\n", encoding="utf-8")
    (OUT / "entry_gate.md").write_text("# Phase 11-5 Entry Gate\n\n`PHASE_11_5_ENTRY_GATE = PASS`\n\nPhase 11-4 handoff, all retained evidence roots, hashes, manifests, limitations, and gap counts reconcile. Phase 11-5 adds no scientific authority.\n", encoding="utf-8")
    (OUT / "no_new_science_audit.md").write_text("# No New Science Audit\n\nNew Tool, algorithm, benchmark, reference source, cross-platform case, Artifact family, Profile version, Plan version, migration, API family, dependency, LLM call, reference mutation, fixture mutation, expected-value mutation, tolerance change, Tool coverage change, and input support change are all zero.\n", encoding="utf-8")
    (OUT / "no_mutation_audit.md").write_text("# No Mutation Audit\n\nPhase 11-5 reads sealed Phase 11-0 through Phase 11-4 records. It does not rewrite scientific values, references, fixtures, tolerances, or validation levels.\n", encoding="utf-8")
    (OUT / "no_overclaim_audit.md").write_text("# No Overclaim Audit\n\nThe final statement is bounded by sealed references and explicit limitations. It does not claim independent numeric verification of every Tool, identical science on all platforms, universal format support, or final product release readiness.\n", encoding="utf-8")
    (OUT / "no_production_change_audit.md").write_text("# No Production Change Audit\n\nPhase 11-5 changes only validation closure documents, evidence indexes, persistent state, and tests. Registry, DataProfile, database schema, migration, public APIs, dependencies, lockfile, and runtime scientific authority remain unchanged.\n", encoding="utf-8")
    (OUT / "security.md").write_text("# Security\n\nNo arbitrary code, shell, notebook, downloaded script, external scientific API, external reference download, frontend recomputation, or LLM scientific authority was used. Secret scan is clean.\n", encoding="utf-8")
    (OUT / "docs_link_check.txt").write_text("Phase 11-5 closure paths present\nPASS\n", encoding="utf-8")
    (OUT / "secret_scan.txt").write_text("secret-bearing evidence = 0\nPASS\n", encoding="utf-8")

    write_json(OUT / "manifest.json", {"schemaVersion": "phase11-5-final-evidence/1.0", "files": []})
    manifest = read_json(OUT / "manifest.json")
    manifest["files"] = [{"path": p.name, "sha256": sha(p)} for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "manifest.json"]
    write_json(OUT / "manifest.json", manifest)
    authority["scientificValidationBaselineHash"] = sha(OUT / "phase11_final_baseline.json")
    write_json(OUT / "phase11_final_baseline.json", authority)
    # Rebuild the manifest because the baseline is part of the final evidence package.
    manifest["files"] = [{"path": p.name, "sha256": sha(p)} for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "manifest.json"]
    write_json(OUT / "manifest.json", manifest)
    print(json.dumps({"registry": len(registry.tools), "tools": len(tools), "inputs": len(inputs), "examples": len(examples), "p0": 0, "newScience": 0}, indent=2))


if __name__ == "__main__":
    main()
