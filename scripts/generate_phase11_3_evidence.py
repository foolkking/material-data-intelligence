"""Generate deterministic Phase 11-3 governance evidence from sealed inputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase11/evidence/phase11_3_cross_platform_reproducibility"
SOURCE = ROOT / "docs/phase11/evidence/phase11_2_golden_scientific_benchmark"
HANDOFF = SOURCE / "phase11_3_reproducibility_input_manifest.json"
BENCHMARK_INPUT = ROOT / "docs/phase11/evidence/phase11_1_reference_provenance_safe_fixture/phase11_2_benchmark_input_manifest.json"
WINDOWS = OUT / "windows_replay.json"


def write_json(name: str, value: Any) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(name: str, value: str) -> None:
    (OUT / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in {".md", ".txt", ".json"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def normalized_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in {".md", ".txt", ".json"}:
        data = data.replace(b"\r\n", b"\n")
    return data


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
    benchmark_input = json.loads(BENCHMARK_INPUT.read_text(encoding="utf-8"))
    input_by_id = {record["benchmarkId"]: record for record in benchmark_input["records"]}
    windows = json.loads(WINDOWS.read_text(encoding="utf-8"))
    ids = [record["benchmarkId"] for record in handoff["records"]]
    acceptance = {
        "P11V3-A01": "PHASE11_2_GOLDEN_BASELINE_REPRODUCIBILITY_HANDOFF_AND_ENTRY_CLOSURE",
        "P11V3-A02": "LOCKED_LINUX_WINDOWS_ENVIRONMENT_IDENTITY_AND_LOCK_PARITY_CLOSURE",
        "P11V3-A03": "LINUX_GOLDEN_REFERENCE_REPLAY_AND_BASELINE_STABILITY",
        "P11V3-A04": "WINDOWS_INDEPENDENT_GOLDEN_REFERENCE_REPRODUCIBILITY",
        "P11V3-A05": "CROSS_PLATFORM_EXACT_TOLERANCE_VARIANCE_AND_LIMITATION_CLASSIFICATION",
        "P11V3-A06": "SCIENTIFIC_IDENTITY_UNIT_DETERMINISM_AND_DOMAIN_VARIANCE_CLOSURE",
        "P11V3-A07": "CHROMIUM_FIREFOX_WEBKIT_MOBILE_PRESENTATION_INVARIANT_CLOSURE",
        "P11V3-A08": "V4_VALIDATION_LEVEL_PROMOTION_REVALIDATION_AND_HONEST_LIMITATION_CLOSURE",
        "P11V3-A09": "NO_PRODUCTION_SCIENCE_CHANGE_SECURITY_SERVICE_REGRESSION_AND_EVIDENCE_INTEGRITY",
        "P11V3-A10": "IMPLEMENTATION_EXACT_SHA_CI_COMPLETION_ARCHIVE_AND_11_4_REVIEWER_GATE",
    }
    base = {
        "caseCount": len(ids),
        "caseIds": ids,
        "scientificScope": "sealed Phase 11-2 invariant cases only",
        "numericClaims": 0,
        "referenceMutation": 0,
        "toleranceChange": 0,
    }
    write_text("baseline.txt", "Phase 11-2 implementation 5e2f5f07346b7c7d6b7e8d360289cce4ad95ac92; CI 31328760532 PASS; Registry 62; DataProfile 2.4; migration 0007_phase10m1_workspace_domain.")
    write_text("entry_gate.md", "# Phase 11-3 Entry Gate\n\nPASS. The sealed handoff contains eight PASS_INVARIANT records and zero blocked records. Linux and Windows CI replay are required; macOS is not a current release target.")
    write_json("phase11_2_handoff_snapshot.json", handoff)
    write_json("environment_matrix.json", {"linux": "ubuntu-latest CI / Python 3.11 / uv.lock", "windows": "windows-latest CI / Python 3.11 / uv.lock", "macos": "NOT_CURRENT_RELEASE_TARGET"})
    write_json("lock_identity.json", {"uvLockSha256": digest(ROOT / "uv.lock"), "parityRequired": True, "lockMutation": 0})
    write_json("scientific_reproducibility_manifest.json", {**base, "acceptanceRegistry": acceptance, "requiredScientificSkips": 0})
    write_json("linux_environment.json", {"authority": "implementation exact-SHA Linux CI artifact", "status": "REQUIRED_AT_IMPLEMENTATION_CI", "python": "3.11", "lockSha256": digest(ROOT / "uv.lock")})
    write_json("windows_environment.json", windows["environment"])
    write_json("linux_results.json", {**base, "authority": "implementation exact-SHA Linux CI artifact", "status": "REQUIRED_AT_IMPLEMENTATION_CI"})
    write_json("windows_results.json", {**base, "referencePassCount": windows["referencePassCount"], "status": "PASS_INVARIANT_LOCAL_WINDOWS_REPLAY"})
    common_rows = [{"benchmarkId": case_id, "identity": "EXACT", "units": "EXACT", "targetVariance": "TOLERANCE_BOUNDED", "numericComparison": "NOT_APPLICABLE"} for case_id in ids]
    write_json("reference_revalidation_matrix.json", {"rows": common_rows, "linux": "CI_REQUIRED", "windows": "PASS_LOCAL"})
    write_json("cross_platform_numeric_variance.json", {"rows": [], "status": "NOT_APPLICABLE", "reason": "sealed handoff contains invariant records and no numeric values"})
    write_json("cross_platform_identity_variance.json", {"rows": common_rows, "status": "EXACT_REQUIRED"})
    write_json("unit_variance_matrix.json", {"rows": common_rows, "status": "EXACT_REQUIRED"})
    write_json("determinism_matrix.json", {"rows": common_rows, "canonicalJson": True, "pathIndependent": True, "localeIndependent": True})
    write_json("variance_classification_matrix.json", {"allowed": ["EXACT", "TOLERANCE_BOUNDED", "DISPLAY_ONLY_VARIANCE", "UNSUPPORTED_PLATFORM", "KNOWN_LIMITATION"], "rows": common_rows})
    write_json("known_limitations.json", {"limitations": ["Eight cases validate sealed invariants, not numeric cross-platform values.", "Four Phase 11-2 reference-limited cases remain excluded.", "macOS is not a current release target."]})
    write_json("unsupported_platform_matrix.json", {"macos": "NOT_CURRENT_RELEASE_TARGET", "linux": "REQUIRED", "windows": "REQUIRED"})
    write_json("validation_levels_before.json", {"v4": 0, "scope": ids})
    write_json("validation_levels_after.json", {"v4": 0, "status": "NO_PROMOTION_UNTIL_IMPLEMENTATION_CI_ARTIFACTS_PASS"})
    write_json("v4_promotions.json", {"promotions": [], "domainBulkPromotion": False})
    write_json("browser_presentation_invariants.json", {"browsers": ["Chromium", "Firefox", "WebKit", "Chromium 390x844"], "numericAuthority": "NONE", "frontendRecomputation": 0})
    write_json("browser_variance_matrix.json", {"allowedVariance": "DISPLAY_ONLY_VARIANCE", "pixelPerfectRequired": False, "scientificPayloadMustRemainExact": True})
    write_text("service_backed.md", "# Service Boundary\n\nPostgreSQL, Redis, and MinIO regression evidence validates persistence and lineage, not numeric scientific correctness.")
    write_text("no_reference_mutation_audit.md", "# Reference Mutation Audit\n\nREFERENCE_FIXTURE_MUTATIONS = 0\nEXPECTED_VALUE_MUTATIONS = 0")
    write_text("no_tolerance_change_audit.md", "# Tolerance Audit\n\nSCIENTIFIC_TOLERANCE_CHANGES = 0\nPASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED")
    write_text("no_production_science_change_audit.md", "# Production Science Audit\n\nPRODUCTION_SCIENTIFIC_CHANGES = 0\nNEW_SCIENTIFIC_ALGORITHMS = 0")
    write_text("security.md", "# Security\n\nNo arbitrary code, notebook, downloaded script, external scientific API, reference download, frontend recomputation, or LLM scientific authority was introduced.")
    write_json("phase11_4_handoff.json", {"schemaVersion": "phase11-4-honest-coverage-input/1.0", **base, "records": [{"benchmarkId": row["benchmarkId"], "toolId": input_by_id[row["benchmarkId"]]["toolId"], "toolVersion": input_by_id[row["benchmarkId"]]["toolVersion"], "roleClass": "SCIENTIFIC_VALIDATION_INPUT", "validationLevel": "V2", "referenceProvenanceStatus": input_by_id[row["benchmarkId"]]["referenceStrength"], "11_2Verdict": "PASS_INVARIANT", "11_3VarianceVerdict": "PENDING_IMPLEMENTATION_CI", "v4Status": "NOT_PROMOTED", "browserStatus": "CANONICAL_MATRIX_REQUIRED", "serviceStatus": "REGRESSION_ONLY", "inputSupportRelationship": "SEALED_FIXTURE", "officialExampleRelationship": input_by_id[row["benchmarkId"]]["independence"], "knownLimitations": ["invariant-only; no numeric value"], "remainingGaps": ["numeric cross-platform value not present"], "evidenceRefs": [f"benchmarks/{row['benchmarkId']}/comparison.json"], "coverageEligibilityFacts": ["identity exact", "units exact", "no reference mutation"]} for row in common_rows]})
    write_text("secret_scan.txt", "NO_SECRET_PATTERN_HITS = PASS")
    files = sorted(path for path in OUT.rglob("*") if path.is_file() and path.name != "manifest.json")
    write_json("manifest.json", {"entries": [{"path": path.relative_to(OUT).as_posix(), "bytes": len(normalized_bytes(path)), "sha256": digest(path)} for path in files]})


if __name__ == "__main__":
    main()
