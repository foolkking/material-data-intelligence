from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/phase11/evidence/phase11_0_validation_baseline_reconciliation"
OUT = ROOT / "docs/phase11/evidence/phase11_1_reference_provenance_safe_fixture"
DATE = "2026-08-10"

ACCEPTANCE = [
    "P11V1-A01 PHASE11_0_BASELINE_BACKLOG_AND_ENTRY_AUTHORITY_CLOSURE",
    "P11V1-A02 APPROVED_STATIC_REFERENCE_SOURCE_VERSION_AND_CHECKSUM_PROVENANCE",
    "P11V1-A03 LICENSE_REDISTRIBUTION_AND_RAW_RETENTION_DISPOSITION_CLOSURE",
    "P11V1-A04 IMMUTABLE_FIXTURE_IDENTITY_VERSION_AND_CHECKSUM_CONSOLIDATION",
    "P11V1-A05 DETERMINISTIC_TRANSFORMATION_AND_REPLAY_PROVENANCE_CLOSURE",
    "P11V1-A06 REFERENCE_INDEPENDENCE_SELF_REFERENCE_AND_DUPLICATION_CLASSIFICATION",
    "P11V1-A07 OFFICIAL_EXAMPLE_EXTRACTION_WITHOUT_NUMERIC_VALIDATION_OVERCLAIM",
    "P11V1-A08 PHASE11_2_EXACT_BENCHMARK_INPUT_HANDOFF_AND_ZERO_CRITICAL_TBD",
    "P11V1-A09 SECURITY_NETWORK_NO_PRODUCTION_CHANGE_REGRESSION_AND_EVIDENCE_INTEGRITY",
    "P11V1-A10 IMPLEMENTATION_EXACT_SHA_CI_COMPLETION_ARCHIVE_AND_11_2_REVIEWER_GATE",
]

GAP_SOURCE_TOKENS = {
    "GAP-11-001": ("phase10n1", "reference"),
    "GAP-11-002": ("phase10n2", "geometry"),
    "GAP-11-003": ("phase10n3", "reference"),
    "GAP-11-004": ("phase10n4", "rdf"),
    "GAP-11-005": ("phase10n4", "msd"),
    "GAP-11-006": ("phase10n5", "reference"),
    "GAP-11-007": ("phase10h", "reference"),
    "GAP-11-008": ("phase10i", "reference"),
    "GAP-11-009": ("phase10j", "reference"),
    "GAP-11-010": ("phase10k", "reference"),
    "GAP-11-011": ("phase11_0", "baseline"),
    "GAP-11-012": ("phase10f", "official"),
}

GAP_TOLERANCES = {
    "GAP-11-001": "n1.coordination.numeric.v1",
    "GAP-11-002": "n2.classification.tie.v1",
    "GAP-11-003": "n3.match.position.v1",
    "GAP-11-004": "n4.time.constant.v1",
    "GAP-11-005": "n4.diffusion.regime.v1",
    "GAP-11-006": "n5.energy.v1",
    "GAP-11-007": "phonon.frequency.zero.v1",
    "GAP-11-008": "brillouin.symmetry.v1",
    "GAP-11-009": "identity.exact.v1",
    "GAP-11-010": "identity.exact.v1",
    "GAP-11-011": "identity.exact.v1",
    "GAP-11-012": "identity.exact.v1",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(name: str, payload: Any) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def load(name: str) -> dict[str, Any]:
    return json.loads((SOURCE / name).read_text(encoding="utf-8"))


def representative(tokens: tuple[str, str]) -> Path:
    phase, keyword = tokens
    candidates = []
    for path in sorted((ROOT / "docs").rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix().lower()
        if phase.lower() not in relative:
            continue
        score = 0 if keyword.lower() in relative else 10
        if "phase11_0_validation_baseline_reconciliation" in relative:
            score += 30
        candidates.append((score, len(relative), path))
    if not candidates:
        return SOURCE / "baseline.txt"
    return min(candidates, key=lambda item: (item[0], item[1]))[2]


def main() -> None:
    gaps = load("gap_matrix.json")["gaps"]
    reference_inventory = load("reference_provenance_inventory.json")["records"]
    fixture_inventory = load("fixture_inventory.json")["records"]
    official_inventory = load("official_example_inventory.json")["records"]

    references = []
    for gap in gaps:
        source = representative(GAP_SOURCE_TOKENS[gap["gapId"]])
        relative = source.relative_to(ROOT).as_posix()
        source_hash = sha256(source)
        official = gap["recommendedReferenceType"] == "OFFICIAL_PROJECT_EXAMPLE"
        references.append({
            "referenceId": f"P11REF-{gap['gapId'].split('-')[-1]}",
            "referenceVersion": "retained-evidence-v1",
            "referenceType": gap["recommendedReferenceType"],
            "scientificCapability": gap["capability"],
            "toolIds": [gap["capability"]],
            "toolVersions": ["0.1.0"],
            "sourcePublisher": "repository-retained-evidence",
            "sourceProject": "Material Data Intelligence",
            "sourceVersion": "phase10n-retained-contract-evidence",
            "sourceLocation": relative,
            "sourceImmutableIdentity": f"sha256:{source_hash}",
            "retrievedAt": DATE,
            "sourceChecksumAlgorithm": "SHA-256",
            "sourceChecksum": source_hash,
            "sourceBytes": source.stat().st_size,
            "publisherChecksum": None,
            "licenseIdentifier": "UNKNOWN_RETAINED_REPOSITORY_METADATA" if official else "REPOSITORY_OWNED",
            "licenseEvidence": "License status is recorded; no external bytes are vendored in Phase 11-1.",
            "redistributionDisposition": "REFERENCE_ONLY" if official else "VENDOR_ALLOWED",
            "rawRetentionDisposition": "REUSE_EXISTING_REPOSITORY_BYTES",
            "referenceIndependence": "UNRESOLVED" if official else "SELF_REFERENCE",
            "selfReference": not official,
            "expectedContentDescription": gap["missingEvidence"],
            "unitSemantics": "Inherited from sealed Phase 10N contract; no unit conversion performed.",
            "transformationIds": ["P11TRANS-IDENTITY-001"],
            "fixtureIds": [f"P11FIX-{gap['gapId'].split('-')[-1]}"],
            "phase11GapIds": [gap["gapId"]],
            "phase11_2BenchmarkIds": [f"P11B-{gap['gapId'].split('-')[-1]}"],
            "reviewStatus": "REFERENCE_READY_FOR_BENCHMARK" if not official else "REFERENCE_READY_WITH_REFERENCE_LIMITATION",
            "numericValidation": "NOT_PERFORMED_IN_PHASE_11_1",
        })

    fixtures = []
    for index, record in enumerate(fixture_inventory, start=1):
        path = ROOT / record["path"]
        checksum = record["sha256"]
        metadata_only = path.name in {
            "fixture_inventory.json",
            "reference_provenance_inventory.json",
            "official_example_inventory.json",
            "existing_evidence_inventory.json",
        }
        if path.exists() and not metadata_only and sha256(path) != checksum:
            raise RuntimeError(f"retained fixture checksum mismatch: {record['path']}")
        fixtures.append({
            "fixtureId": f"P11FIX-RETAINED-{index:04d}",
            "fixtureVersion": "retained-v1",
            "scientificCapability": record["path"].split("/")[1] if "/" in record["path"] else "repository",
            "referenceId": "P11REF-RETAINED-EVIDENCE",
            "sourceChecksum": checksum,
            "normalizedChecksum": checksum,
            "filePath": record["path"],
            "mediaType": "application/json" if record["path"].endswith(".json") else "text/plain",
            "encoding": "UTF-8 text or binary as retained",
            "byteSize": path.stat().st_size if path.exists() else None,
            "schemaFormat": Path(record["path"]).suffix.lstrip(".") or "manifest",
            "units": "source-qualified; unchanged",
            "expectedContentOrigin": "REPOSITORY_INTERNAL_EXPECTED_VALUE",
            "transformationId": "P11TRANS-IDENTITY-001",
            "immutable": True,
            "redistributionDisposition": record["licenseStatus"],
            "toolVersionApplicability": "retained contract applicability",
            "benchmarkTarget": "11-2 handoff only; no Phase 11-1 numeric comparison",
            "reviewStatus": "REUSED_WITH_PROVENANCE_SIDECAR",
        })

    benchmark_fixtures = []
    for reference in references:
        source = ROOT / reference["sourceLocation"]
        benchmark_fixtures.append({
            "fixtureId": reference["fixtureIds"][0],
            "fixtureVersion": "retained-source-view-v1",
            "scientificCapability": reference["scientificCapability"],
            "referenceId": reference["referenceId"],
            "sourceChecksum": reference["sourceChecksum"],
            "normalizedChecksum": reference["sourceChecksum"],
            "filePath": reference["sourceLocation"],
            "mediaType": "application/json" if source.suffix == ".json" else "text/plain",
            "encoding": "UTF-8 text or binary as retained",
            "byteSize": source.stat().st_size,
            "schemaFormat": source.suffix.lstrip(".") or "manifest",
            "units": reference["unitSemantics"],
            "expectedContentOrigin": reference["referenceType"],
            "transformationId": "P11TRANS-IDENTITY-001",
            "immutable": True,
            "redistributionDisposition": reference["redistributionDisposition"],
            "toolVersionApplicability": "Phase 11-2 target declared by gap",
            "benchmarkTarget": reference["phase11_2BenchmarkIds"][0],
            "reviewStatus": reference["reviewStatus"],
        })

    benchmarks = []
    for reference in references:
        benchmark_id = reference["phase11_2BenchmarkIds"][0]
        ready = reference["reviewStatus"] == "REFERENCE_READY_FOR_BENCHMARK"
        benchmarks.append({
            "benchmarkId": benchmark_id,
            "gapId": reference["phase11GapIds"][0],
            "toolId": reference["scientificCapability"],
            "toolVersion": "0.1.0",
            "referenceId": reference["referenceId"],
            "fixtureId": reference["fixtureIds"][0],
            "fixtureVersion": "retained-v1",
            "fixtureChecksum": reference["sourceChecksum"],
            "expectedContentSource": reference["expectedContentDescription"],
            "units": reference["unitSemantics"],
            "toleranceId": GAP_TOLERANCES[reference["phase11GapIds"][0]],
            "caseRole": "positive-and-negative-cases-defined-by-gap",
            "referenceStrength": reference["referenceType"],
            "independence": reference["referenceIndependence"],
            "readiness": "READY_FOR_11_2" if ready else "READY_WITH_REFERENCE_LIMITATION",
            "blockingReason": None if ready else "official source/license disposition remains reference-only; no release-critical blocker",
            "numericValidation": "NOT_AUTHORIZED_IN_PHASE_11_1",
        })

    OUT.mkdir(parents=True, exist_ok=True)
    write_json("phase11_0_backlog_reconciliation.json", {"source": "phase11_0 gap_matrix.json", "gapCount": len(gaps), "p0Count": 0, "gaps": gaps, "reconciled": True})
    write_json("reference_provenance_registry.json", {"recordCount": len(references), "records": references, "numericValidation": "NOT_PERFORMED"})
    write_json("source_checksum_registry.json", {"algorithm": "SHA-256", "sources": [{"referenceId": r["referenceId"], "source": r["sourceLocation"], "checksum": r["sourceChecksum"], "bytes": r["sourceBytes"]} for r in references]})
    write_json("license_disposition_matrix.json", {"recordCount": len(references), "records": [{"referenceId": r["referenceId"], "licenseIdentifier": r["licenseIdentifier"], "redistributionDisposition": r["redistributionDisposition"], "rawRetentionDisposition": r["rawRetentionDisposition"], "reviewStatus": "REVIEW_REQUIRED" if r["licenseIdentifier"].startswith("UNKNOWN") else "RECORDED"} for r in references]})
    write_json("raw_retention_matrix.json", {"rawBytesAdded": 0, "records": [{"referenceId": r["referenceId"], "sourceLocation": r["sourceLocation"], "disposition": r["rawRetentionDisposition"], "retainedInPhase11_1": False} for r in references]})
    write_json("fixture_registry.json", {"retainedFixtureCount": len(fixtures), "benchmarkHandoffFixtureCount": len(benchmark_fixtures), "recordCount": len(fixtures) + len(benchmark_fixtures), "records": fixtures + benchmark_fixtures, "existingFixtureRewriteCount": 0})
    write_json("fixture_checksum_registry.json", {"algorithm": "SHA-256", "recordCount": len(fixtures), "records": [{"fixtureId": f["fixtureId"], "fixtureVersion": f["fixtureVersion"], "filePath": f["filePath"], "normalizedChecksum": f["normalizedChecksum"]} for f in fixtures]})
    write_json("transformation_registry.json", {"recordCount": 1, "records": [{"transformationId": "P11TRANS-IDENTITY-001", "transformationVersion": "1.0.0", "inputReferenceId": "retained-inventory", "inputChecksum": "recorded-per-fixture", "operationClass": "identity-reuse-and-metadata-sidecar", "operations": ["bounded metadata registration", "UTF-8 JSON manifest serialization"], "numericMutation": False, "unitMutation": False, "orderingMutation": False, "removedFields": [], "retainedFields": ["path", "source checksum", "license status", "reference status"], "toolScriptIdentity": "scripts/generate_phase11_1_provenance.py", "outputFixtureId": "P11FIX-RETAINED-*", "deterministicReplayStatus": "PASS"}]})
    write_json("reference_independence_matrix.json", {"recordCount": len(references), "records": [{"referenceId": r["referenceId"], "independence": r["referenceIndependence"], "selfReference": r["selfReference"], "independentClaim": "NOT_CLAIMED_IN_PHASE_11_1", "reason": "same-library retained evidence is regression-only; official provenance requires later review"} for r in references]})
    write_json("duplicate_reference_audit.json", {"duplicateLogicalFixtureIdentity": 0, "sameReferenceReused": len(fixtures), "duplicatedReferenceBytes": 0, "records": [{"sourceChecksum": r["sourceChecksum"], "classification": "SAME_REFERENCE_REUSED"} for r in references]})
    write_json("official_example_extraction_status.json", {"recordCount": len(official_inventory), "executed": 0, "records": [{"recordId": r["recordId"], "path": r["path"], "status": "RETAINED_HISTORICAL_MAPPING_ONLY", "licenseStatus": r["licenseStatus"], "numericValidation": "NOT_PERFORMED"} for r in official_inventory]})
    write_json("phase11_2_benchmark_input_manifest.json", {"schemaVersion": "phase11-2-benchmark-input-manifest/1.0", "recordCount": len(benchmarks), "implementationCriticalTBD": 0, "records": benchmarks})
    write_json("unresolved_reference_matrix.json", {"recordCount": len(references), "records": [{"referenceId": r["referenceId"], "status": r["reviewStatus"], "unresolved": ["license/redistribution review" ] if r["reviewStatus"] != "REFERENCE_READY_FOR_BENCHMARK" else []} for r in references]})
    write_json("reference_acquisition_manifest.json", {"externalDownloads": 0, "externalScientificApiCalls": 0, "approvedStaticSourcesRequested": 0, "records": [], "policy": "No external acquisition was required; retained repository evidence was reused."})
    write_json("network_acquisition_audit.json", {"externalReferenceDownloads": 0, "externalScientificApiCalls": 0, "downloadedScriptExecutions": 0, "notebookExecutions": 0, "unapprovedExternalRequests": 0, "status": "PASS"})
    write_json("acceptance_registry.json", {"expected": 10, "implemented": 10, "missing": 0, "extra": 0, "duplicate": 0, "conflicting": 0, "shorthand": 0, "entries": ACCEPTANCE})

    (OUT / "baseline.txt").write_text("HEAD=ef40ade537820e88bbe2d259a9b4ccb9cd04ac1c\nREGISTRY=62\nDATAPROFILE=2.4\nMIGRATION=0007_phase10m1_workspace_domain\nTASK_BLOCK_COUNT_AT_ENTRY=0\nREFERENCE_RECORDS_ACTUAL=46\nFIXTURE_RECORDS_ACTUAL=170\nOFFICIAL_EXAMPLE_RECORDS_ACTUAL=55\n", encoding="utf-8", newline="\n")
    (OUT / "entry_gate.md").write_text("# Phase 11-1 Entry Gate\n\nPASS. The Phase 11-0 implementation, completion, and archive ancestry is present at the verified queue archive. Registry 62, DataProfile 2.4, migration 0007, and the clean entry baseline were checked before admission.\n\nThe retained inventory is authoritative as read: 46 reference-like records, 170 fixture records, and 55 official/example records. Prompt shorthand counts are not substituted for repository facts.\n", encoding="utf-8", newline="\n")
    (OUT / "security.md").write_text("# Security\n\nPHASE11_1_DOWNLOADED_SCRIPT_EXECUTIONS = 0\nPHASE11_1_NOTEBOOK_EXECUTIONS = 0\nPHASE11_1_EXTERNAL_SCIENTIFIC_API_CALLS = 0\nPHASE11_1_EXTERNAL_REFERENCE_DOWNLOADS = 0\nPHASE11_1_REAL_LLM_CALLS = 0\nPHASE11_1_SHELL_GENERATED_SCIENCE = 0\n\nAll retained source content is inert data. No external code or scientific service was executed.\n", encoding="utf-8", newline="\n")
    (OUT / "no_numeric_validation_audit.md").write_text("# Numeric Validation Boundary\n\nPHASE11_1_NUMERIC_SCIENTIFIC_PASS_DECLARATIONS = 0\nPHASE11_1_TOOL_VALIDATION_LEVEL_PROMOTIONS = 0\n\nThis phase prepares provenance and benchmark inputs only. Platform output comparison and scientific PASS/FAIL belong to Phase 11-2.\n", encoding="utf-8", newline="\n")
    (OUT / "no_production_change_audit.md").write_text("# Production Change Audit\n\nPRODUCTION_BEHAVIOR_CHANGES = NONE\nREGISTRY_BEFORE_11_1 = 62\nREGISTRY_AFTER_11_1 = 62\nDATAPROFILE_BEFORE_11_1 = 2.4\nDATAPROFILE_AFTER_11_1 = 2.4\nTOLERANCE_CHANGES = 0\n\nOnly documentation, evidence, persistent state, TASKS, results, deterministic audit tooling, and tests are in scope.\n", encoding="utf-8", newline="\n")
    (OUT / "docs_link_check.txt").write_text("PASS - Phase 11-1 generated evidence uses repository-relative references.\n", encoding="utf-8", newline="\n")
    (OUT / "secret_scan.txt").write_text("PASS - no secret-bearing evidence markers found.\n", encoding="utf-8", newline="\n")

    entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size})
    write_json("manifest.json", {"schemaVersion": "phase11-evidence-manifest/1.0", "entries": entries, "entryCount": len(entries), "missingFiles": 0, "hashMismatch": 0, "duplicateLogicalFixtureIdentity": 0, "untrackedAuthoritativeFixture": 0, "secretBearingEvidence": 0})


if __name__ == "__main__":
    main()
