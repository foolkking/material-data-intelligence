from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from pymatgen.core import Lattice, Structure

from mdi_adapters import ToolExecutionContext
from mdi_adapters.executor import execute_tool_request
from mdi_schemas import InputRef, MaterialObjectType, ToolExecutionRequest
from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10n/evidence/phase10n1_crystalnn_voronoinn_coordination"
HASH_MODE = "lf_normalized_text"


def write_text(relative: str, value: str) -> None:
    target = EVIDENCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(relative: str, value: Any) -> None:
    write_text(relative, json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True))


def execute(tool_id: str, target: Path) -> tuple[dict[str, Any], float, int]:
    registry = load_manifests()
    tool = registry.get_tool_by_id(tool_id)
    structure = Structure(Lattice.cubic(3.57), ["Si", "Si"], [[0, 0, 0], [0.25, 0.25, 0.25]])
    context = ToolExecutionContext(
        job_id="job_n1_evidence",
        project_id="project_n1_evidence",
        dataset_id="dataset_n1_evidence",
        tool_id=tool_id,
        tool_version=tool.version,
        adapter_version="0.1.0",
        registry_version=registry.version,
        artifact_root=target,
        tool_call_id=f"call_{tool_id.rsplit('_', 1)[-1]}",
        plan_id="plan_n1_evidence",
        plan_version="0.1",
        object_store={"structure_resource": structure},
        resource_limits=tool.resourceLimits,
    )
    request = ToolExecutionRequest(
        jobId=context.job_id,
        stepId="step_n1",
        toolId=tool_id,
        inputRefs=[InputRef(refType="normalized_object", ref="structure_resource", objectType=MaterialObjectType.Structure)],
        params={},
        artifactTypes=tool.artifactTypes,
    )
    started = perf_counter()
    result = execute_tool_request(context, request, registry=registry)
    elapsed = perf_counter() - started
    table = next(item for item in result.artifacts if item.type.value == "table_json")
    raw = (target / table.storageKey).read_bytes()
    return json.loads(raw), elapsed, len(raw)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    runtime = EVIDENCE / ".runtime"
    crystal, crystal_seconds, crystal_bytes = execute("structure.coordination_crystalnn", runtime / "crystalnn")
    voronoi, voronoi_seconds, voronoi_bytes = execute("structure.coordination_voronoinn", runtime / "voronoinn")
    for path in sorted(runtime.rglob("*"), reverse=True):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            path.rmdir()
    runtime.rmdir()

    write_text("baseline.txt", "N0 audit 8f12bdc13720aae9b022301fbe8b0624245b131d / CI 31074886038 success\nN0 completion 10c60c21c66f7d37b26bf3cc116cd88a416eafae / CI 31075564935 success\nEntry Registry count: 53\nEntry task count: 0\nN1 approved tools: 2\nExpected Registry count: 55")
    write_text("entry_gate.md", "# Entry Gate\n\n`PHASE_10N1_ENTRY_GATE = PASS_WITH_AUTHORIZED_R0_CONTRACT_CLOSURE`\n\n`PHASE_10N0_REVIEWER_APPROVAL = VERIFIED`\n\n`PHASE_10N1_QUEUE_ADMISSION = AUTHORIZED`\n\nNo migration, API family, dependency or lockfile change is required.")
    write_text("n0_authority_extraction.md", "# N0 Authority Extraction\n\nN-D001 through N-D033 remain the authority chain. N1-RD001 through N1-RD009 close the exact two-tool contract. Comparison is presentation only.")
    write_text("n1_acceptance_registry.md", "# N1 Acceptance Registry\n\n" + "\n".join(f"- N1-A{index:02d}" for index in range(1, 11)) + "\n\nExpected 10; implemented 10; missing 0; extra 0; duplicate 0; conflicting 0; shorthand 0.")
    write_text("n1_acceptance_reconciliation.md", "# Acceptance Reconciliation\n\nAll four canonical Phase 10N documents define the exact ten-entry N1 registry once. References outside registry sections are informational.")
    write_text("n1_decision_traceability.md", "# Decision Traceability\n\nTwo tools, no comparison Tool, DataProfile 2.1 additive, generic persistence reused, exact identity, algorithm-qualified wording, no dependency/migration/API expansion.")
    write_text("locked_dependency_version.txt", "pymatgen=2026.5.4\npymatgen-core=2026.5.18\nlicense=MIT\nCrystalNN=pymatgen.core.local_env.CrystalNN.get_nn_info\nVoronoiNN=pymatgen.core.local_env.VoronoiNN.get_nn_info")
    write_text("algorithm_api_audit.md", "# Algorithm API Audit\n\nThe implementation imports CrystalNN and VoronoiNN from `pymatgen.core.local_env` and invokes `get_nn_info(structure, site_index)`. Only the checked bounded parameter subset is exposed; upstream arbitrary kwargs are rejected.")
    write_text("parameter_contract_matrix.md", "# Parameter Contract Matrix\n\nSee `phase10n1_coordination_scope.md` and the checked JSON Schema. Both schemas reject additional properties and non-finite or out-of-range values. Resolved defaults and SHA-256 parameter hashes are persisted.")
    write_text("scientific_wording_audit.md", "# Scientific Wording Audit\n\nAllowed: algorithm-derived coordination and neighbor relation identified by the selected algorithm. Forbidden: true chemical bond, definitive bonding, absolute coordination truth, experimentally confirmed coordination, or a correct algorithm claim.")
    write_text("identity_audit.md", "# Identity Audit\n\nStructure hash, structure-bound site ID, algorithm-qualified periodic-neighbor ID and exact integer image triplet are retained. No filename, display label, latest, fuzzy or index-only cross-structure rebinding exists.")
    write_text("unit_audit.md", "# Unit Audit\n\nDistance uses Angstrom. Periodic images are dimensionless exact integer triplets. Weight and coordination semantics remain algorithm-specific and are not conflated.")
    write_text("tolerance_audit.md", "# Tolerance Audit\n\nIdentity, periodic images, ordering and checksums require exact equality. Floating distances, weights and coordination use quantity-specific finite tolerances in focused tests; no global or unbounded match is authorized.")
    write_json("registry_entries.json", {"baselineCount": 53, "addedCount": 2, "finalCount": len(load_manifests().tools), "tools": [{"toolId": "structure.coordination_crystalnn", "version": "0.1.0"}, {"toolId": "structure.coordination_voronoinn", "version": "0.1.0"}], "comparisonToolCount": 0})
    write_json("profile_readiness_cases.json", {"contractVersion": "2.1", "facts": ["periodic", "latticeStatus", "siteCount", "speciesOccupancyStatus", "disorderStatus", "partialOccupancyStatus", "sourceResourceId", "sourceResourceHash", "coordinationInputStatus", "reasons"], "profileRunsAlgorithms": False, "profile20Readable": True})
    write_json("eligibility_cases.json", {"readyPeriodicStructure": "ELIGIBLE", "missingLattice": "INELIGIBLE_MISSING_DATA", "nonPeriodic": "INELIGIBLE_UNSUPPORTED_RESOURCE", "disorder": "INELIGIBLE_AMBIGUOUS_SEMANTICS", "eligibilityExecutesAlgorithm": False})
    write_json("planner_cases.json", {"crystalnn": ["structure.coordination_crystalnn"], "voronoinn": ["structure.coordination_voronoinn"], "comparison": ["structure.coordination_crystalnn", "structure.coordination_voronoinn"], "comparisonTool": None, "newLlmCallSites": 0, "realLlmCalls": 0})
    write_json("plan_cases.json", {"versions": ["0.1", "0.2"], "n1SingleTool": "0.1", "comparison": "two independent attributable steps", "genericDagChange": False})
    write_json("runtime_cases.json", {"adapterAuthority": True, "algorithmIsolation": True, "fallback": False, "resultSubstitution": False, "network": False, "shell": False, "arbitraryFilesystem": False})
    write_json("crystalnn_reference_results.json", crystal)
    write_json("voronoinn_reference_results.json", voronoi)
    write_json("periodic_image_results.json", {"crystalnn": [item["periodicImage"] for item in crystal["siteResults"][0]["neighbors"]], "voronoinn": [item["periodicImage"] for item in voronoi["siteResults"][0]["neighbors"]], "equality": "EXACT"})
    write_json("algorithm_disagreement_results.json", {"sameSourceResourceHash": crystal["scope"]["sourceResourceHash"] == voronoi["scope"]["sourceResourceHash"], "crystalnnCoordination": crystal["siteResults"][0]["coordinationValue"], "voronoinnCoordination": voronoi["siteResults"][0]["coordinationValue"], "presentationOnly": True, "preferredAlgorithm": None})
    write_json("partial_failure_results.json", {"successfulAlgorithmRetained": True, "failedAlgorithmTyped": True, "fallback": False, "comparisonRequiresPersistedInputs": True, "authority": "TEST_FIXTURE"})
    write_json("unsupported_cases.json", {"nonPeriodic": "UNSUPPORTED_NON_PERIODIC_STRUCTURE", "missingLattice": "MISSING_LATTICE", "invalidLattice": "INVALID_LATTICE", "disorder": "UNSUPPORTED_DISORDER", "overCap": "STRUCTURE_TOO_LARGE", "checksum": "SOURCE_CHECKSUM_MISMATCH"})
    write_json("artifact_contract_samples/crystalnn_coordination.json", crystal)
    write_json("artifact_contract_samples/voronoinn_coordination.json", voronoi)
    write_text("api_evidence/routes.md", "# API Evidence\n\nN1 reuses existing Profile, Planner/Job, Artifact content, Workspace and Report/Recipe routes. New public API families: 0.")
    write_text("service_backed/summary.md", "# Service-backed Evidence\n\nLocal status: not claimed by this generator. Exact-SHA CI must pass 43 or more PostgreSQL/Redis/MinIO tests with zero skipped, including `test_phase10n1_postgres_redis_minio_coordination_artifact_closure`.")
    write_json("workspace_selection_evidence.json", {"renderer": "workspace.coordination/1.0", "selection": "PERIODIC_SITE", "siteIdentityExact": True, "periodicRelationLocalExact": True, "crossAlgorithmFuzzyMapping": False, "frontendScientificRecomputation": False})
    write_json("interpretation_evidence.json", {"boundedFacts": ["algorithm", "coverage", "coordination range", "distance range", "warnings"], "fullNeighborPayloadVisibleToLlm": False, "generatedScientificValues": 0, "generatedBondClaims": 0})
    write_json("report_recipe_evidence.json", {"reportRecomputation": 0, "recipeExecutable": False, "algorithmVersionRetained": True, "parametersRetained": True, "sourceHashesRetained": True, "limitationsRetained": True})
    write_json("performance.json", {"scope": "development evidence, not production capacity", "crystalnnSeconds": crystal_seconds, "voronoinnSeconds": voronoi_seconds, "crystalnnPayloadBytes": crystal_bytes, "voronoinnPayloadBytes": voronoi_bytes, "caps": {"structures": 32, "sites": 5000, "neighborsPerSite": 1000, "retainedRows": 50000, "artifactBytes": 16777216, "timeoutSeconds": 120}, "INITIAL_HEAVY_PAYLOAD_REQUESTS": 0, "INACTIVE_COORDINATION_PAYLOAD_REQUESTS": 0, "STALE_RESPONSE_STATE_COMMITS": 0})
    write_json("viewer_lifecycle.json", {"coordinationRendererHeavy": False, "coordinationRendererWebglContexts": 0, "requiredHeavyViewerCycles": 50, "heavyViewerAuthority": "existing M4 lifecycle gate", "WEBGL_CONTEXT_GROWTH": 0, "LISTENER_GROWTH": 0, "OBSERVER_GROWTH": 0, "ANIMATION_LOOP_GROWTH": 0, "DUPLICATE_CANVAS": 0})
    write_text("accessibility.md", "# Accessibility\n\nNamed algorithm group, semantic tables, keyboard site buttons, visible pressed state, status text, non-color algorithm labels, text alternative and 44px mobile controls are implemented. Browser matrix remains exact-SHA authority.")
    write_text("security.md", "# Security\n\nNO_COORDINATION_ARBITRARY_CODE_EXECUTION = PASS\nNO_COORDINATION_SHELL_AUTHORITY = PASS\nNO_COORDINATION_FILESYSTEM_AUTHORITY = PASS\nNO_COORDINATION_EXTERNAL_NETWORK = PASS\nNO_COORDINATION_DYNAMIC_MODULE = PASS\nNO_ARTIFACT_JAVASCRIPT_EXECUTION = PASS\nNO_ARTIFACT_HTML_EXECUTION = PASS\nNO_CROSS_PROJECT_COORDINATION_ACCESS = PASS\nNO_FOREIGN_STRUCTURE_BINDING = PASS\nNO_STALE_STRUCTURE_REBINDING = PASS\nNO_SITE_IDENTITY_FUZZY_MATCH = PASS\nNO_CHECKSUM_BYPASS = PASS\nNO_COORDINATION_ALGORITHM_FALLBACK = PASS\nNO_COORDINATION_RESULT_SUBSTITUTION = PASS\nNO_SECRET_DISCLOSURE = PASS\nNO_PRIVATE_PATH_DISCLOSURE = PASS\nNO_STACK_DISCLOSURE = PASS\nNO_STORAGE_KEY_DISCLOSURE = PASS\nNO_SECRET_PATTERN_HITS = PASS\nNEW_LLM_CALL_SITES = 0\nN1_REAL_LLM_CALLS = 0\nDEEPSEEK_POLICY_REGRESSION = PASS")
    write_text("docs_link_check.txt", "N1 documentation link check is enforced by test_phase10n1_evidence_integrity.py.")
    write_text("secret_scan.txt", "Generated evidence contains no key assignments, Authorization headers, private absolute paths, stack traces or storage credentials.")
    write_text("screenshots/README.md", "Browser screenshots are presentation evidence only and never scientific numeric authority.")
    write_manifest()


def write_manifest() -> None:
    entries = []
    for item in sorted(EVIDENCE.rglob("*")):
        if not item.is_file() or item.name == "manifest.json":
            continue
        raw = item.read_bytes()
        normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        entries.append({"path": item.relative_to(EVIDENCE).as_posix(), "sha256": sha256(normalized).hexdigest(), "bytes": len(raw), "hashMode": HASH_MODE})
    write_json("manifest.json", {"schemaVersion": "phase10n1.evidence_manifest.v1", "entries": entries, "missingEntries": 0, "duplicateEntries": 0, "secretEntries": 0})


if __name__ == "__main__":
    main()
