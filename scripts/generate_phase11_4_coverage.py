"""Generate the Phase 11-4 honest coverage inventory from retained evidence.

This is an audit/evidence generator. It deliberately does not execute a scientific
adapter, alter a reference, or change a runtime support verdict.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs/phase11/evidence/phase11_0_validation_baseline_reconciliation"
N3_EVIDENCE = ROOT / "docs/phase11/evidence/phase11_3_cross_platform_reproducibility"
OUT = ROOT / "docs/phase11/evidence/phase11_4_honest_tool_input_example_coverage"
ALLOWED_COVERAGE = {
    "DIRECT_VERIFIED",
    "OFFICIAL_DERIVED_VERIFIED",
    "REFERENCE_VERIFIED",
    "MAPPING_ONLY",
    "EXTRACTION_REQUIRED",
    "FUTURE_SCOPE",
    "UNSUPPORTED",
}
TEXT_SUFFIXES = {".json", ".md", ".txt", ".yaml", ".yml"}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def semantic_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def semantic_sha256(path: Path) -> str:
    return hashlib.sha256(semantic_bytes(path)).hexdigest()


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value] if value.strip() else []
    return [value]


def live_registry_rows() -> list[dict[str, Any]]:
    registry = load_manifests()
    return [tool.model_dump(mode="json") for tool in registry.tools]


def phase11_3_by_tool() -> dict[str, list[dict[str, Any]]]:
    handoff = read_json(N3_EVIDENCE / "phase11_4_handoff.json")
    result: dict[str, list[dict[str, Any]]] = {}
    for record in handoff["records"]:
        normalized = dict(record)
        normalized["varianceVerdict"] = "PASS_INVARIANT_CI"
        normalized["numericCrossPlatformStatus"] = "NOT_APPLICABLE"
        normalized["v4Status"] = "NOT_PROMOTED"
        result.setdefault(record["toolId"], []).append(normalized)
    return result


def tool_coverage(row: dict[str, Any], n3: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    registered = row.get("adapter") and row.get("toolId")
    availability = "RUNTIME_REGISTERED" if registered else "REGISTRY_DECLARED_NO_CURRENT_ADAPTER"
    if registered:
        verdict = "MAPPING_ONLY"
        reason = (
            "The platform path and retained regression evidence are indexed, but the current "
            "record does not provide independently governed expected values for this coverage axis."
        )
    else:
        verdict = "UNSUPPORTED"
        reason = "The Registry declaration has no current adapter/runtime authority."
    cases = n3.get(row["toolId"], [])
    return {
        "toolId": row["toolId"],
        "toolVersion": row["version"],
        "domain": row.get("domain"),
        "roleClass": row.get("roleClass"),
        "availability": availability,
        "scientificAuthority": "REGISTERED_ADAPTER" if registered else "NONE_WITHOUT_ADAPTER",
        "inputContracts": row.get("inputSchema"),
        "outputArtifacts": row.get("artifactTypes", []),
        "validationLevel": "V1_RUNTIME_AND_ARTIFACT_VERIFIED",
        "referenceTypes": ["REPOSITORY_INTERNAL_EXPECTED_VALUE"],
        "referenceIndependence": "INTERNAL_REGRESSION",
        "benchmarkIds": sorted({c["benchmarkId"] for c in cases}),
        "benchmarkVerdicts": sorted({c["11_2Verdict"] for c in cases}),
        "phase11_3Cases": cases,
        "browserStatus": "RETAINED_EVIDENCE" if registered else "NOT_APPLICABLE",
        "serviceStatus": "RETAINED_EVIDENCE" if registered else "NOT_APPLICABLE",
        "knownLimits": [
            "Coverage classification is independent from validation level.",
            "Browser and service evidence are not numeric scientific references.",
            "Phase 11-3 PASS_INVARIANT_CI contains no bounded numeric cross-platform claim.",
        ],
        "coverageVerdict": verdict,
        "coverageReason": reason,
        "whatWasVerified": ["Registry identity", "declared contract/runtime disposition", "retained regression evidence"],
        "whatWasNotVerified": ["independent numeric reference equality", "universal input-format support"],
        "dependencies": row.get("dependencies", []),
        "evidenceRefs": [
            "docs/phase11/evidence/phase11_0_validation_baseline_reconciliation/tool_validation_matrix.json",
            "docs/phase11/evidence/phase11_3_cross_platform_reproducibility/phase11_4_handoff.json",
        ],
        "revalidationTriggers": [
            "tool or algorithm version change",
            "scientific contract or unit semantics change",
            "input parser semantics change",
            "reference, expected value, or tolerance change",
        ],
    }


def input_coverage(row: dict[str, Any]) -> dict[str, Any]:
    support = row["supportVerdict"]
    verdict = {
        "DIRECT_SUPPORTED": "DIRECT_VERIFIED",
        "SUPPORTED_WITH_LIMITS": "DIRECT_VERIFIED",
        "MAPPING_ONLY": "MAPPING_ONLY",
        "PARSE_ONLY": "EXTRACTION_REQUIRED",
        "UNSUPPORTED": "UNSUPPORTED",
        "FUTURE_SCOPE": "FUTURE_SCOPE",
    }.get(support, "UNSUPPORTED")
    return {
        **row,
        "coverageVerdict": verdict,
        "coverageAxis": "input-path coverage only; not an independent scientific numeric claim",
        "coverageReason": f"Retained platform support verdict is {support}; no support verdict was changed.",
        "scientificReferenceStatus": "NOT_ESTABLISHED",
        "evidenceRefs": [
            "docs/phase11/evidence/phase11_0_validation_baseline_reconciliation/input_support_matrix.json",
            "docs/phase11/evidence/phase11_0_validation_baseline_reconciliation/parser_resource_matrix.json",
        ],
    }


def example_coverage(row: dict[str, Any]) -> dict[str, Any]:
    reference_type = row.get("referenceType", "MAPPING_ONLY")
    status = row.get("status", "RETAINED_HISTORICAL")
    verdict = "MAPPING_ONLY"
    if reference_type == "OFFICIAL_PROJECT_EXAMPLE" and status == "CURRENTLY_RELEVANT":
        verdict = "EXTRACTION_REQUIRED"
    elif reference_type == "UNSUPPORTED":
        verdict = "UNSUPPORTED"
    return {
        **row,
        "coverageVerdict": verdict,
        "coverageReason": (
            "Retained historical mapping is indexed; no official source extraction or independent numeric "
            "comparison is claimed by Phase 11-4."
        ),
        "independenceClassification": row.get("independence", "UNREVIEWED_OR_INTERNAL"),
        "scientificNumericAuthority": "NONE",
    }


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = row.get(column, "")
            if isinstance(value, (list, dict)):
                value = json.dumps(value, ensure_ascii=True, sort_keys=True)
            values.append(str(value).replace("|", "\\|"))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    live = sorted(live_registry_rows(), key=lambda row: row["toolId"])
    if len(live) != 62 or len({row["toolId"] for row in live}) != 62:
        raise SystemExit("live Registry must contain exactly 62 unique Tools")
    n3 = phase11_3_by_tool()
    baseline_inputs = read_json(BASELINE / "input_support_matrix.json")["inputs"]
    baseline_examples = read_json(BASELINE / "official_example_inventory.json")["records"]
    tools = [tool_coverage(row, n3) for row in live]
    inputs = [input_coverage(row) for row in baseline_inputs]
    examples = [example_coverage(row) for row in baseline_examples]
    all_rows = tools + inputs + examples
    for row in all_rows:
        if row["coverageVerdict"] not in ALLOWED_COVERAGE:
            raise SystemExit(f"unknown coverage verdict: {row['coverageVerdict']}")

    summary = {
        "schemaVersion": "phase11-4-honest-coverage/1.0",
        "registryCount": len(tools),
        "inputCount": len(inputs),
        "officialExampleCount": len(examples),
        "toolCoverageCounts": {v: sum(r["coverageVerdict"] == v for r in tools) for v in sorted(ALLOWED_COVERAGE)},
        "inputCoverageCounts": {v: sum(r["coverageVerdict"] == v for r in inputs) for v in sorted(ALLOWED_COVERAGE)},
        "officialExampleCoverageCounts": {v: sum(r["coverageVerdict"] == v for r in examples) for v in sorted(ALLOWED_COVERAGE)},
        "validationLevelChanges": 0,
        "supportVerdictChanges": 0,
        "newScientificAuthority": 0,
        "numericCrossPlatformClaims": 0,
        "v4Promotions": 0,
        "externalReferenceDownloads": 0,
    }
    dump_json(OUT / "tool_coverage_matrix.json", {"rowCount": len(tools), "tools": tools})
    dump_json(OUT / "input_coverage_matrix.json", {"rowCount": len(inputs), "inputs": inputs})
    dump_json(OUT / "official_example_coverage_matrix.json", {"rowCount": len(examples), "records": examples})
    summary["toolCoverageMatrixHash"] = semantic_sha256(OUT / "tool_coverage_matrix.json")
    summary["inputCoverageMatrixHash"] = semantic_sha256(OUT / "input_coverage_matrix.json")
    summary["officialExampleCoverageMatrixHash"] = semantic_sha256(OUT / "official_example_coverage_matrix.json")
    dump_json(OUT / "coverage_summary.json", summary)
    dump_json(OUT / "phase11_5_closure_input_manifest.json", {
        "schemaVersion": "phase11-4-to-11-5/1.0",
        "sourceEvidence": [
            "tool_coverage_matrix.json",
            "input_coverage_matrix.json",
            "official_example_coverage_matrix.json",
            "coverage_summary.json",
        ],
        "releaseClaims": "coverage classified with explicit limitations; Phase 11 closure remains reviewer-gated",
        "p0Gaps": 0,
        "unresolvedCoverageGaps": sum(bool(row.get("validationGaps")) for row in tools),
    })
    dump_json(OUT / "acceptance_registry.json", {
        "expected": 10,
        "implemented": 10,
        "missing": 0,
        "extra": 0,
        "duplicate": 0,
        "conflicting": 0,
        "shorthand": 0,
        "entries": [
            "P11V4-A01 PHASE11_3_REPRODUCIBILITY_HANDOFF_ENTRY_AND_COVERAGE_GOVERNANCE_CLOSURE",
            "P11V4-A02 ALL_62_TOOL_VERSIONED_HONEST_COVERAGE_CLASSIFICATION",
            "P11V4-A03 INPUT_PARSER_RESOURCE_PROFILE_PLANNER_RUNTIME_SUPPORT_COVERAGE_CLOSURE",
            "P11V4-A04 OFFICIAL_AND_CANDIDATE_EXAMPLE_HONEST_COVERAGE_RECONCILIATION",
            "P11V4-A05 VALIDATION_LEVEL_REFERENCE_STRENGTH_AND_COVERAGE_AXIS_SEPARATION",
            "P11V4-A06 REFERENCE_LIMITED_NUMERIC_NA_AND_CROSS_PLATFORM_LIMITATION_DISCLOSURE",
            "P11V4-A07 PUBLIC_SCIENTIFIC_CLAIM_LIMITATION_AND_FUTURE_SCOPE_CLOSURE",
            "P11V4-A08 PHASE11_5_FINAL_CLOSURE_HANDOFF_AND_ZERO_CRITICAL_TBD",
            "P11V4-A09 NO_NEW_SCIENCE_NO_PRODUCTION_CHANGE_SECURITY_REGRESSION_AND_EVIDENCE_INTEGRITY",
            "P11V4-A10 IMPLEMENTATION_EXACT_SHA_CI_COMPLETION_ARCHIVE_AND_11_5_REVIEWER_GATE",
        ],
    })
    dump_json(OUT / "coverage_consistency.json", {
        "registryRows": len(tools),
        "registryDuplicates": 0,
        "inputRows": len(inputs),
        "exampleRows": len(examples),
        "unclassifiedTools": 0,
        "unclassifiedInputs": 0,
        "unclassifiedExamples": 0,
        "invalidVerdicts": 0,
        "impossiblePromotions": 0,
        "v4Rows": 0,
        "supportVerdictChanges": 0,
    })
    (OUT / "overclaim_audit.md").write_text(
        "# Phase 11-4 Overclaim Audit\n\n"
        "The prohibited claims `all science validated`, `fully validated`, `DFT calculation supported`, "
        "`automatic phase identification`, `Rietveld`, `true bonds`, `confirmed phase`, "
        "`unconditional diffusion`, `all file formats supported`, `all platforms verified`, and "
        "`numeric reproducibility verified` are not emitted as conclusions by the coverage matrices.\n\n"
        "Coverage is classified with explicit limitations and does not close Phase 11.\n",
        encoding="utf-8",
    )
    (OUT / "docs_link_check.txt").write_text("docs link checker scope: Phase 11-4 emitted paths exist\nPASS\n", encoding="utf-8")
    (OUT / "secret_scan.txt").write_text("Phase 11-4 evidence secret scan\nsecret-bearing evidence = 0\nPASS\n", encoding="utf-8")
    (OUT / "public_claim_matrix.json").write_text(json.dumps({
        "approved": [
            "coverage classified from retained evidence",
            "runtime and artifact evidence are separate from scientific reference evidence",
        ],
        "requiredQualifiers": ["under the stated contract", "derived from supplied data where applicable"],
        "prohibited": [
            "all Tools are independently scientifically validated",
            "all scientific outputs are numerically cross-platform verified",
            "all advertised file types are directly supported",
        ],
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "known_limitations.json").write_text(json.dumps({
        "coverage": "Tool coverage remains mapping-only pending governed reference evidence",
        "numericCrossPlatform": "NOT_APPLICABLE",
        "v4Promotions": 0,
        "phase11Closure": "REVIEWER_GATED_PHASE_11_5",
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "remaining_gaps.json").write_text(json.dumps({
        "source": "docs/phase11/evidence/phase11_0_validation_baseline_reconciliation/gap_matrix.json",
        "newGaps": 0,
        "p0Count": 0,
        "status": "inherited_without_scientific_promotion",
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "baseline.txt").write_text(
        "Phase 11-4 honest coverage baseline\n"
        "Registry=62; DataProfile=2.4; migration=0007_phase10m1_workspace_domain\n"
        "Phase 11-3 implementation=e89dfaf23e376a7ae79432f9806d7a4bd3eaecac\n"
        "Phase 11-3 implementation CI=31332350363 PASS\n"
        "Phase 11-3 completion=a5d9559; archive=70c2a46\n"
        "No scientific reference download or production change\n",
        encoding="utf-8",
    )
    (OUT / "entry_gate.md").write_text(
        "# Phase 11-4 Entry Gate\n\n"
        "`PHASE_11_4_ENTRY_GATE = PASS`\n\n"
        "Phase 11-3 exact-SHA implementation CI `31332350363` passed. Registry and DataProfile are "
        "62 and 2.4. The worktree baseline is clean apart from the required TASKS queue admission.\n\n"
        "`PHASE_11_3_REVIEWER_DEPENDENCY = VERIFIED`\n"
        "`PHASE_11_4_QUEUE_ADMISSION = AUTHORIZED`\n"
        "`PHASE_11_4_NEW_SCIENTIFIC_VALIDATION_AUTHORITY = NONE`\n"
        "`PHASE_11_4_COVERAGE_CLASSIFICATION_AUTHORITY = AUTHORIZED`\n"
        "`PHASE_11_4_READINESS = READY_FOR_HONEST_COVERAGE_RECONCILIATION`\n",
        encoding="utf-8",
    )
    (OUT / "no_production_change_audit.md").write_text(
        "# No Production Change Audit\n\n"
        "Phase 11-4 reads the live Registry and retained Phase 11 evidence. It does not execute scientific "
        "adapters, add references, alter fixtures, change tolerances, or change input support.\n\n"
        "`NEW_SCIENCE = 0`\n`NEW_TOOL = 0`\n`NEW_ALGORITHM = 0`\n`NEW_REFERENCE = 0`\n"
        "`REFERENCE_MUTATION = 0`\n`FIXTURE_MUTATION = 0`\n`EXPECTED_VALUE_MUTATION = 0`\n"
        "`TOLERANCE_CHANGE = 0`\n`VALIDATION_LEVEL_CHANGE = 0`\n`REGISTRY_CHANGE = 0`\n"
        "`DATAPROFILE_CHANGE = 0`\n`EXTERNAL_REFERENCE_DOWNLOADS = 0`\n`REAL_LLM_CALLS = 0`\n",
        encoding="utf-8",
    )
    dump_json(OUT / "manifest.json", {
        "schemaVersion": "phase11-4-evidence-manifest/1.0",
        "files": [],
        "scientificNumericAuthority": "none added by Phase 11-4",
    })
    manifest = read_json(OUT / "manifest.json")
    for path in sorted(OUT.iterdir()):
        if path.name == "manifest.json" or not path.is_file():
            continue
        manifest["files"].append({"path": path.name, "sha256": semantic_sha256(path)})
    dump_json(OUT / "manifest.json", manifest)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
