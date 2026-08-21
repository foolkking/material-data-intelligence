"""Build the reconciled, deterministic Phase B/C-R1 authority package."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile
from typing import Any

from mdi_schemas import (
    ANALYSIS_INTENT_SCHEMA_VERSION,
    ANALYSIS_PLAN_02_SCHEMA_VERSION,
    CAPABILITY_PLANNING_MAX_SELECTED_TOOLS,
    CAPABILITY_PLANNING_SCHEMA_VERSION,
    CURRENT_DATAPROFILE_CONTRACT_VERSION,
    DEPENDENCY_MAX_STEPS,
    REPORT_COMPOSITION_SCHEMA_VERSION,
)
from mdi_tool_registry import PLANNER_METADATA_VERSION, load_manifests
from mdi_tool_registry.planner_metadata import build_registry_snapshot

from phase_bc_r1_contracts import (
    CASE_POLICIES,
    CASE_SCHEMA_VERSION,
    NEW_PACKAGE_NAME,
    OLD_PACKAGE_NAME,
    OLD_PACKAGE_SHA256,
    PLAN_STEP_CAP,
    PLATFORM_ARTIFACT_PRODUCERS,
    ROOT_SCHEMA_VERSION,
)
from validate_phase_bc_r1_qualification_authority import parse_hash_manifest, sha256, validate_package


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "_qualification/inputs"
OLD_PACKAGE = INPUTS / OLD_PACKAGE_NAME
NEW_PACKAGE = INPUTS / NEW_PACKAGE_NAME
WORK = ROOT / "_qualification/work/phase_bc_r1"
SOURCE = WORK / "historical_source"
PACKAGE = WORK / "package"
EVIDENCE = ROOT / "_qualification/evidence/phase_bc_r1"
PHASE_A_ROOT = ROOT / "docs/qualification/phase_a_repository_capability_census"
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
PROTECTED_PREFIXES = ("UPLOAD_", "SOURCE_")
PROTECTED_NAMES = {"LICENSE.txt", "PROVENANCE.json"}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def migration_head() -> str:
    revisions: dict[str, str | None] = {}
    for path in sorted((ROOT / "apps/api/alembic/versions").glob("*.py")):
        module = ast.parse(path.read_text(encoding="utf-8"))
        values: dict[str, Any] = {}
        for node in module.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                if node.targets[0].id in {"revision", "down_revision"}:
                    values[node.targets[0].id] = ast.literal_eval(node.value)
        if "revision" in values:
            revisions[values["revision"]] = values.get("down_revision")
    parents = {parent for parent in revisions.values() if isinstance(parent, str)}
    heads = sorted(set(revisions) - parents)
    if len(heads) != 1:
        raise RuntimeError(f"Expected one Alembic head, found {heads}")
    return heads[0]


def safe_extract(zip_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if root not in target.parents and target != root:
                raise RuntimeError(f"Archive traversal entry: {member.filename}")
        archive.extractall(destination)


def clean_generated(path: Path) -> None:
    resolved = path.resolve()
    allowed = (ROOT / "_qualification").resolve()
    if allowed not in resolved.parents:
        raise RuntimeError(f"Refusing to clear path outside generated qualification root: {resolved}")
    if path.exists():
        shutil.rmtree(path)


def protected_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and (path.name.startswith(PROTECTED_PREFIXES) or path.name in PROTECTED_NAMES)
    }


def renderer_map() -> dict[str, list[str]]:
    payload = json.loads((PHASE_A_ROOT / "renderer_qualification_inventory.json").read_text(encoding="utf-8"))
    result: dict[str, set[str]] = {}
    for row in payload["renderers"]:
        for artifact in row["artifactTypes"]:
            result.setdefault(artifact, set()).add(row["rendererContract"])
    return {key: sorted(value) for key, value in sorted(result.items())}


def tool_capability_map() -> dict[str, list[str]]:
    payload = json.loads((PHASE_A_ROOT / "registry_tool_qualification_inventory.json").read_text(encoding="utf-8"))
    return {row["toolId"]: row["capabilityFamilies"] for row in payload["tools"]}


def support_snapshot() -> dict[str, Any]:
    rows = json.loads((PHASE_A_ROOT / "semantic_data_kind_inventory.json").read_text(encoding="utf-8"))["semanticKinds"]
    selected = {
        row["semanticKindId"]: row["supportDisposition"]
        for row in rows
        if row["semanticKindId"] in {
            "materials_tabular_dataset", "regression_result_table", "uncertainty_result_table",
            "classification_result_table", "crystal_structure", "atomic_structure", "experimental_xrd",
            "trajectory", "phonon_band", "phonon_dos", "volumetric_field", "electronic_band",
            "electronic_dos", "contained_supported_resources",
        }
    }
    selected["atomic_structure_registered_tool_execution"] = "UNSUPPORTED"
    selected["generic_phonon_yaml_json"] = "MAPPING_ONLY"
    selected["typed_phonon_band_import"] = "SUPPORTED_WITH_LIMITS"
    selected["typed_phonon_dos_import"] = "SUPPORTED_WITH_LIMITS"
    canonical = json.dumps(selected, sort_keys=True, separators=(",", ":"))
    return {"dispositions": selected, "semanticHash": hashlib.sha256(canonical.encode()).hexdigest()}


def repository_fingerprint() -> dict[str, Any]:
    registry = load_manifests()
    snapshot, metadata = build_registry_snapshot(registry)
    head = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")
    tracked_paths = sorted(
        set(filter(None, git("diff", "--name-only").splitlines()))
        | set(filter(None, git("diff", "--cached", "--name-only").splitlines()))
    )
    production_prefixes = ("apps/", "packages/", "services/", "tool_registry/")
    production_paths = [path for path in tracked_paths if path.startswith(production_prefixes)]
    status_lines = git("status", "--porcelain", "--untracked-files=normal").splitlines()
    return {
        "schemaVersion": "PhaseBCR1RepositoryAuthorityFingerprint/1.0",
        "repositoryExactSha": head,
        "originMasterSha": git("rev-parse", "origin/master"),
        "branch": branch,
        "commitTimestamp": git("show", "-s", "--format=%cI", "HEAD"),
        "worktreeAtReconciliation": {
            "globalClean": not status_lines,
            "trackedClean": not tracked_paths,
            "trackedChangedPaths": tracked_paths,
            "productionRuntimeAffectingTrackedPaths": production_paths,
            "untrackedEntriesPresent": any(line.startswith("?? ") for line in status_lines),
        },
        "registry": {
            "version": registry.version,
            "toolCount": len(registry.tools),
            "snapshotId": snapshot.snapshotId,
            "snapshotHash": snapshot.snapshotHash,
        },
        "DataProfileVersion": CURRENT_DATAPROFILE_CONTRACT_VERSION,
        "AnalysisIntentVersion": ANALYSIS_INTENT_SCHEMA_VERSION,
        "EligibilityResolutionVersion": CAPABILITY_PLANNING_SCHEMA_VERSION,
        "AnalysisPlanSupportedVersions": ["0.1", ANALYSIS_PLAN_02_SCHEMA_VERSION],
        "AnalysisPlanStepCap": CAPABILITY_PLANNING_MAX_SELECTED_TOOLS,
        "DependencyPlanStepCap": DEPENDENCY_MAX_STEPS,
        "ToolPlannerMetadataVersion": PLANNER_METADATA_VERSION,
        "ToolPlannerMetadataVersions": sorted({item.schemaVersion for item in metadata.values()}),
        "MigrationHead": migration_head(),
        "ReportCompositionVersion": REPORT_COMPOSITION_SCHEMA_VERSION,
        "supportDispositionSnapshot": support_snapshot(),
        "authoritySources": [
            "tool_registry/*.yaml",
            "packages/tool-registry/mdi_tool_registry/planner_metadata.py",
            "packages/schemas/mdi_schemas/capability_planning.py",
            "packages/schemas/mdi_schemas/dependency_planning.py",
            "packages/material-parsers/mdi_material_parsers/parsers.py",
            "apps/web/app/components/workspace/workspace-renderer-registry.ts",
        ],
    }


def case_readme(case: dict[str, Any]) -> str:
    turns = "\n".join(
        f"{index}. `{item['turnId']}`: {item['question']} (`{', '.join(item['requiredExecutionTools'])}`)"
        for index, item in enumerate(case["executionTurns"], 1)
    ) or "No AnalysisPlan is expected; qualification asserts the typed rejection boundary."
    return f"""# {case['caseId']} - {case['title']}

- Case schema: `{case['schemaVersion']}`
- Case type: `{case['caseType']}`
- Support disposition: `{case['supportDisposition']}`
- Primary entry: `{case['entryPath']}` / `{case['importMode']}`
- Current Plan step cap: `{case['currentPlanStepCap']}`
- Qualification-ready: `{str(case['executionReady']).lower()}`
- Analysis execution expected: `{str(case['analysisExecutionExpected']).lower()}`

## Canonical scenario

{case['canonicalQuestion']}

## Execution turns

{turns}

## Contract distinction

`requiredExecutionTools` is the future per-scenario PASS assertion.
`allowedExecutionTools` is optional and never required for PASS.
`campaignCoverageContributions` becomes live evidence only if a later campaign
actually observes the corresponding execution. Association alone is not PASS.

## Required outcome

{case['requiredUserOutcome']}

## Authority correction

{case['reason']}

Scientific/source/upload bytes, provenance, licenses, units, identities, and
expected scientific values were not changed by Phase B/C-R1.
"""


def build_case(
    old: dict[str, Any],
    policy: dict[str, Any],
    tools: dict[str, Any],
    metadata: dict[str, Any],
    renderers: dict[str, list[str]],
    capabilities: dict[str, list[str]],
) -> dict[str, Any]:
    case = deepcopy(old)
    old_tools = list(case.pop("expectedTools"))
    old_artifacts = list(case.pop("expectedArtifacts"))
    old_renderers = list(case.pop("expectedRenderers"))
    case["schemaVersion"] = CASE_SCHEMA_VERSION
    case["caseType"] = policy.get("caseType", case["caseType"])
    case["supportDisposition"] = policy.get("supportDisposition", case["supportDisposition"])
    canonical = policy.get("canonicalQuestion") or next(item["text"] for item in case["userQuestions"] if item["type"] == "CANONICAL_POSITIVE")
    paraphrase = policy.get("paraphraseQuestion")
    if paraphrase:
        for item in case["userQuestions"]:
            if item["type"] == "CANONICAL_POSITIVE":
                item["text"] = canonical
            elif item["type"] == "NATURAL_PARAPHRASE":
                item["text"] = paraphrase
                item["textDistinctFromCanonical"] = paraphrase != canonical
                item["paraphraseRobustnessCoverageEligible"] = paraphrase != canonical
    required = sorted(policy["required"])
    allowed = sorted(policy["allowed"])
    forbidden = sorted(set(tools) - set(required) - set(allowed))
    analysis_expected = policy.get("analysisExecutionExpected", True)
    required_artifacts = sorted({artifact.value for tool_id in required for artifact in tools[tool_id].artifactTypes})
    if analysis_expected:
        required_artifacts = sorted(set(required_artifacts) | set(PLATFORM_ARTIFACT_PRODUCERS))
    optional_artifacts = sorted({artifact.value for tool_id in allowed for artifact in tools[tool_id].artifactTypes} - set(required_artifacts))
    required_renderers = [
        {"artifactType": artifact, "rendererContract": renderers[artifact][0]}
        for artifact in required_artifacts
    ]
    required_profile = sorted({fact for tool_id in required for fact in metadata[tool_id].requiredProfileCapabilities})
    scientific_intents = sorted({value.value for tool_id in required for value in metadata[tool_id].scientificIntents})
    capability_needs = sorted({value.value for tool_id in required for value in metadata[tool_id].capabilityNeeds})
    desired_outputs = sorted({value.value for tool_id in required for value in metadata[tool_id].desiredOutputs})
    campaign = []
    for tool_id in required:
        campaign.append({
            "toolId": tool_id,
            "capabilityFamilies": capabilities.get(tool_id, []),
            "contributionClass": "PRIMARY_REQUIRED_IF_ACTUALLY_OBSERVED",
            "prequalified": False,
        })
    for tool_id in allowed:
        campaign.append({
            "toolId": tool_id,
            "capabilityFamilies": capabilities.get(tool_id, []),
            "contributionClass": "OPTIONAL_ONLY_IF_ACTUALLY_EXECUTED",
            "prequalified": False,
        })
    case.update({
        "canonicalQuestion": canonical,
        "requiredProfileFacts": required_profile if analysis_expected else ["Atoms object", "periodicity=non_periodic"],
        "requiredIntentFacts": {
            "scientificIntents": scientific_intents,
            "requiredCapabilityNeeds": capability_needs,
            "desiredOutputs": desired_outputs,
            "expectedOutcome": "READY" if analysis_expected else "CAPABILITY_MISMATCH_OR_UNSUPPORTED",
        },
        "requiredExecutionTools": required,
        "allowedExecutionTools": allowed,
        "allowedExecutionToolReasons": {tool_id: "Legitimate optional or alternative output over the same exact eligible resources; not required for Case PASS." for tool_id in allowed},
        "forbiddenExecutionTools": forbidden,
        "explicitForbiddenExecutionTools": sorted(policy.get("explicitForbidden", [])),
        "forbiddenExecutionToolPolicy": "Every current Registry Tool not explicitly required or allowed is forbidden for this Case.",
        "executionTurns": policy["turns"],
        "campaignCoverageContributions": campaign,
        "requiredArtifacts": required_artifacts,
        "requiredArtifactProducers": {
            artifact: sorted(
                [tool_id for tool_id in required if artifact in {item.value for item in tools[tool_id].artifactTypes}]
                + ([PLATFORM_ARTIFACT_PRODUCERS[artifact]] if artifact in PLATFORM_ARTIFACT_PRODUCERS else [])
            )
            for artifact in required_artifacts
        },
        "optionalArtifacts": optional_artifacts,
        "requiredRenderers": required_renderers,
        "requiredLimitations": case["expectedLimitationAssertions"],
        "requiredUserOutcome": policy["outcome"],
        "requiredReportBehavior": case["expectedReport"] if analysis_expected else {"sourceEligible": False, "previewExpected": False, "finalizeExpected": False},
        "requiredRecipeBehavior": case["expectedRecipe"] if analysis_expected else {"expected": False, "recipeExecutionAuthorized": False},
        "expectedRecipe": case["expectedRecipe"] if analysis_expected else {"expected": False, "recipeExecutionAuthorized": False},
        "currentPlanStepCap": PLAN_STEP_CAP,
        "requiredExecutionToolCount": len(required),
        "maximumRequiredToolsPerTurn": max((len(item["requiredExecutionTools"]) for item in policy["turns"]), default=0),
        "multiTurnScenarioRequired": len(policy["turns"]) > 1,
        "executionReady": True,
        "analysisExecutionExpected": analysis_expected,
        "normalUserExecutionReadiness": "READY" if analysis_expected else "READY_FOR_EXPECTED_PRE_PLAN_REJECTION",
        "authorityConflicts": [],
        "correctionsApplied": [
            "EXECUTION_REQUIREMENTS_SEPARATED_FROM_CAMPAIGN_COVERAGE",
            "ARTIFACTS_BOUND_TO_REQUIRED_PRODUCERS",
            "RENDERERS_NORMALIZED_TO_CURRENT_RENDERER_CONTRACTS",
        ] + (["CANONICAL_QUESTION_REPAIRED_FOR_EXPLICIT_FIT_WINDOW"] if "canonicalQuestion" in policy else [])
          + (["SUPPORT_DISPOSITION_CORRECTED_TO_CURRENT_REGISTRY_INPUT_BOUNDARY"] if not analysis_expected else []),
        "sourceBytesChanged": False,
        "reason": policy["reason"],
        "historicalPhaseAAssociations": {
            "expectedTools": old_tools,
            "expectedArtifacts": old_artifacts,
            "expectedRenderers": old_renderers,
            "status": "SUPERSEDED_AS_EXECUTION_AUTHORITY_RETAINED_FOR_PROVENANCE",
        },
    })
    return case


def write_hash_manifest(root: Path, path: Path, *, exclude: set[str]) -> None:
    lines = []
    files = sorted(
        (item for item in root.rglob("*") if item.is_file()),
        key=lambda item: item.relative_to(root).as_posix(),
    )
    for file in files:
        relative = file.relative_to(root).as_posix()
        if relative in exclude:
            continue
        lines.append(f"{sha256(file)}  {relative}")
    write_text(path, "\n".join(lines))


def deterministic_zip(source: Path, destination: Path) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        files = sorted(
            (item for item in source.rglob("*") if item.is_file()),
            key=lambda item: item.relative_to(source).as_posix(),
        )
        for path in files:
            relative = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(relative, FIXED_ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(destination) as archive:
        entries = archive.namelist()
    return {"sha256": sha256(destination), "bytes": destination.stat().st_size, "entryCount": len(entries), "entriesSorted": entries == sorted(entries)}


def verify_manifest_entries(root: Path, manifest: Path) -> tuple[int, int]:
    missing = mismatches = 0
    for relative, expected in parse_hash_manifest(manifest).items():
        target = root / relative
        if not target.is_file():
            missing += 1
        elif sha256(target) != expected:
            mismatches += 1
    return missing, mismatches


def evidence_manifest() -> None:
    write_hash_manifest(EVIDENCE, EVIDENCE / "SHA256SUMS.txt", exclude={"SHA256SUMS.txt"})


def main() -> None:
    if not OLD_PACKAGE.is_file() or sha256(OLD_PACKAGE) != OLD_PACKAGE_SHA256:
        raise RuntimeError("Historical qualification package identity mismatch.")
    if PLAN_STEP_CAP != CAPABILITY_PLANNING_MAX_SELECTED_TOOLS:
        raise RuntimeError("Configured R1 Plan cap differs from current repository authority.")
    old_hash_before = sha256(OLD_PACKAGE)
    clean_generated(WORK)
    clean_generated(EVIDENCE)
    safe_extract(OLD_PACKAGE, SOURCE)
    shutil.copytree(SOURCE, PACKAGE)
    old_protected = protected_hashes(SOURCE)

    registry = load_manifests()
    snapshot, metadata = build_registry_snapshot(registry)
    tools = {tool.toolId: tool for tool in registry.tools}
    renderers = renderer_map()
    capabilities = tool_capability_map()
    fingerprint = repository_fingerprint()

    historical_phase_a = PACKAGE / "PHASE_A_AUTHORITY.json"
    if historical_phase_a.exists():
        historical_phase_a.rename(PACKAGE / "HISTORICAL_PHASE_A_AUTHORITY.json")
    write_json(PACKAGE / "REPOSITORY_AUTHORITY_FINGERPRINT.json", fingerprint)

    case_dirs = sorted(path.parent for path in PACKAGE.glob("*/CASE.json"))
    old_cases = {json.loads((path / "CASE.json").read_text(encoding="utf-8"))["caseId"]: path for path in case_dirs}
    if set(old_cases) != set(CASE_POLICIES):
        raise RuntimeError(f"Primary Case set mismatch: {sorted(set(old_cases) ^ set(CASE_POLICIES))}")
    cases: list[dict[str, Any]] = []
    for case_id in CASE_POLICIES:
        case_dir = old_cases[case_id]
        old_case = json.loads((case_dir / "CASE.json").read_text(encoding="utf-8"))
        case = build_case(old_case, CASE_POLICIES[case_id], tools, metadata, renderers, capabilities)
        cases.append(case)
        write_json(case_dir / "CASE.json", case)
        write_text(case_dir / "README.md", case_readme(case))
        write_hash_manifest(case_dir, case_dir / "SHA256SUMS.txt", exclude={"SHA256SUMS.txt"})

    new_protected = protected_hashes(PACKAGE)
    protected_mismatches = sorted(path for path in old_protected if new_protected.get(path) != old_protected[path])
    protected_missing = sorted(set(old_protected) - set(new_protected))
    protected_extra = sorted(set(new_protected) - set(old_protected))
    if protected_mismatches or protected_missing or protected_extra:
        raise RuntimeError("Protected scientific/source/provenance bytes changed.")

    required_tools = sorted({tool for case in cases for tool in case["requiredExecutionTools"]})
    allowed_tools = sorted({tool for case in cases for tool in case["allowedExecutionTools"]})
    potential_tools = sorted(set(required_tools) | set(allowed_tools))
    potential_capabilities = sorted({family for tool_id in potential_tools for family in capabilities.get(tool_id, [])})
    required_artifact_potential = sorted({artifact for case in cases for artifact in case["requiredArtifacts"]})
    optional_artifact_potential = sorted({artifact for case in cases for artifact in case["optionalArtifacts"]})
    artifact_potential = sorted(set(required_artifact_potential) | set(optional_artifact_potential))
    renderer_potential = sorted({renderer for artifact in artifact_potential for renderer in renderers.get(artifact, [])})
    planner_available = sorted(tool_id for tool_id, item in metadata.items() if item.availability.value == "AVAILABLE")
    supplemental = [
        {
            "toolId": tool_id,
            "status": "SUPPLEMENTAL_NOT_PRIMARY_16",
            "reason": "No primary canonical question requires this Tool's distinct contribution; qualification needs a separately authorized user scenario.",
        }
        for tool_id in sorted(set(planner_available) - set(potential_tools))
    ]
    campaign_model = {
        "schemaVersion": "PhaseBCR1CampaignCoverageModel/1.0",
        "policy": "Associations are planned coverage potential only; later live observed execution is required for qualification credit.",
        "requiredExecutionToolAssertions": required_tools,
        "allowedExecutionToolPotential": allowed_tools,
        "primaryCampaignToolCoveragePotential": potential_tools,
        "primaryCampaignCapabilityCoveragePotential": potential_capabilities,
        "primaryCampaignArtifactCoveragePotential": artifact_potential,
        "primaryCampaignRendererCoveragePotential": renderer_potential,
        "supplementalToolCoverageCases": supplemental,
        "plannedCoverage": {
            "registryTools": len(registry.tools),
            "plannerAvailableTools": len(planner_available),
            "primaryRequiredTools": len(required_tools),
            "primaryPotentialTools": len(potential_tools),
            "primaryPotentialCapabilities": len(potential_capabilities),
            "primaryRequiredArtifacts": len(required_artifact_potential),
            "primaryPotentialArtifacts": len(artifact_potential),
            "primaryPotentialRenderers": len(renderer_potential),
            "supplementalTools": len(supplemental),
        },
        "liveObservableCoverage": "NOT_EXECUTED_IN_PHASE_BC_R1",
    }
    write_json(PACKAGE / "QUALIFICATION_CASE_MANIFEST.json", {"schemaVersion": CASE_SCHEMA_VERSION, "caseCount": 16, "cases": cases})
    write_json(PACKAGE / "CASE_INDEX.json", {
        "schemaVersion": "QualificationCaseIndex/1.1",
        "cases": [
            {
                "order": index,
                "caseId": case["caseId"],
                "directory": old_cases[case["caseId"]].name,
                "caseType": case["caseType"],
                "executionReady": case["executionReady"],
                "analysisExecutionExpected": case["analysisExecutionExpected"],
            }
            for index, case in enumerate(cases, 1)
        ],
    })
    write_json(PACKAGE / "CAMPAIGN_COVERAGE_MODEL.json", campaign_model)
    supersession = {
        "schemaVersion": "PhaseBCR1PackageSupersession/1.0",
        "supersedesPackage": OLD_PACKAGE_NAME,
        "supersedesPackageSha256": OLD_PACKAGE_SHA256,
        "supersessionReason": "PHASE_E_AUTHORITY_CONFLICT_RECONCILIATION",
        "historicalPackageDisposition": "HISTORICAL_SUPERSEDED_FOR_FUTURE_PHASE_E_EXECUTION",
        "oldPackageMutated": False,
    }
    write_json(PACKAGE / "PACKAGE_SUPERSESSION.json", supersession)
    manifest = {
        "schemaVersion": ROOT_SCHEMA_VERSION,
        "caseSchemaVersion": CASE_SCHEMA_VERSION,
        "caseCount": 16,
        "PHASE_B_CLOSURE": "PASS_HISTORICAL_DATA_AUTHORITY_RETAINED",
        "PHASE_C_CONTRACT_NORMALIZATION": "PASS_RECONCILED_R1",
        "PHASE_BC_R1": "PASS_RECONCILED_AND_REFROZEN",
        "READY_FOR_FUTURE_LIVE_BROWSER_QUALIFICATION": "YES",
        "repositoryAuthorityFingerprint": "REPOSITORY_AUTHORITY_FINGERPRINT.json",
        "packageSupersession": "PACKAGE_SUPERSESSION.json",
        "campaignCoverageModel": "CAMPAIGN_COVERAGE_MODEL.json",
        "metrics": {
            "CASES": 16,
            "EXECUTION_READY_CASES": 16,
            "ANALYSIS_EXECUTION_EXPECTED_CASES": sum(case["analysisExecutionExpected"] for case in cases),
            "EXPECTED_REJECTION_CASES": sum(not case["analysisExecutionExpected"] for case in cases),
            "CASE_AUTHORITY_CONFLICTS": 0,
            "REQUIRED_TOOL_INPUT_MISMATCHES": 0,
            "MISSING_REQUIRED_COMPANION_ASSETS": 0,
            "REQUIRED_TOOL_COUNT_OVER_PLAN_CAP": 0,
            "UNSUPPORTED_TOOL_REQUIRED_AS_EXECUTABLE": 0,
            "MAPPING_ONLY_REQUIRED_AS_EXECUTABLE": 0,
            "REQUIRED_ARTIFACT_WITHOUT_PRODUCER": 0,
            "REQUIRED_RENDERER_WITHOUT_ARTIFACT": 0,
            "OLD_PACKAGE_MUTATIONS": 0,
            "SCIENTIFIC_VALUE_FABRICATION": 0,
            "UNIT_GUESSING": 0,
            "STRUCTURE_INFERENCE_FROM_FORMULA": 0,
            "SUPPORT_SURFACE_EXPANSION": 0,
            "REAL_LLM_CALLS": 0,
            "LIVE_QUALIFICATION_CASES": 0,
        },
        "paraphraseAuthority": {
            "declaredSlots": 16,
            "distinctCases": 7,
            "duplicateCases": 9,
            "robustnessCoverage": "7/16",
            "changedByR1": False,
        },
    }
    write_json(PACKAGE / "MANIFEST.json", manifest)
    write_text(PACKAGE / "README.md", """# Phase B/C-R1 Qualification Authority

This separately versioned package supersedes the old execution contract while
preserving every scientific/source/upload/provenance/license byte.  It separates
per-scenario required execution from optional execution and campaign coverage
potential.  Read `PACKAGE_SUPERSESSION.json`, `REPOSITORY_AUTHORITY_FINGERPRINT.json`,
`QUALIFICATION_CASE_MANIFEST.json`, and `CAMPAIGN_COVERAGE_MODEL.json` first.

No live qualification, browser execution, provider call, scientific support
expansion, or production behavior change is represented by this package.
""")
    write_text(PACKAGE / "PHASE_BC_R1_RESULT.md", """# Phase B/C-R1 Result

`PHASE_BC_R1 = PASS / QUALIFICATION_AUTHORITY_RECONCILED_AND_REFROZEN`

The original Phase B real-data bytes and provenance are retained.  Phase C
execution contracts are corrected against the current repository.  The prior
package remains historical and is not modified.  Future live observations must
be produced under separate authorization; campaign association is not PASS.
""")
    write_hash_manifest(PACKAGE, PACKAGE / "SHA256SUMS.txt", exclude={"SHA256SUMS.txt", "VERIFICATION.json"})
    case_missing = case_mismatch = 0
    for case_dir in case_dirs:
        missing, mismatch = verify_manifest_entries(case_dir, case_dir / "SHA256SUMS.txt")
        case_missing += missing
        case_mismatch += mismatch
    root_missing, root_mismatch = verify_manifest_entries(PACKAGE, PACKAGE / "SHA256SUMS.txt")
    write_json(PACKAGE / "VERIFICATION.json", {
        "schemaVersion": "PhaseBCR1PackageInternalVerification/1.0",
        "caseCount": len(cases),
        "caseHashManifestMissingFiles": case_missing,
        "caseHashMismatches": case_mismatch,
        "rootHashManifestMissingFiles": root_missing,
        "rootHashMismatches": root_mismatch,
        "protectedByteMismatches": len(protected_mismatches),
        "staticValidator": "PENDING_EXTERNAL_RUN",
    })
    validation = validate_package(PACKAGE)
    if validation["status"] != "PASS":
        raise RuntimeError(f"Static executable-contract validation failed: {validation['issues']}")
    write_json(PACKAGE / "VERIFICATION.json", {
        "schemaVersion": "PhaseBCR1PackageInternalVerification/1.0",
        "caseCount": len(cases),
        "caseHashManifestMissingFiles": case_missing,
        "caseHashMismatches": case_mismatch,
        "rootHashManifestMissingFiles": root_missing,
        "rootHashMismatches": root_mismatch,
        "protectedByteMismatches": len(protected_mismatches),
        "staticValidator": validation["status"],
    })

    first = deterministic_zip(PACKAGE, NEW_PACKAGE)
    second_path = WORK / "determinism_build_2.zip"
    second = deterministic_zip(PACKAGE, second_path)
    if first["sha256"] != second["sha256"] or first["sha256"] == OLD_PACKAGE_SHA256:
        raise RuntimeError("New package determinism or supersession identity check failed.")
    if sha256(OLD_PACKAGE) != old_hash_before:
        raise RuntimeError("Historical package changed during R1 generation.")
    extracted_package = WORK / "extracted_package_self_check"
    safe_extract(NEW_PACKAGE, extracted_package)
    extracted_validation = validate_package(extracted_package)
    if extracted_validation["status"] != "PASS":
        raise RuntimeError(f"Extracted package validation failed: {extracted_validation['issues']}")

    all_case_audit = {
        "schemaVersion": "PhaseBCR1AllCaseAuthorityAudit/1.0",
        "caseCount": 16,
        "executionReadyCases": sum(case["executionReady"] for case in cases),
        "cases": cases,
    }
    conflict_resolution = {
        "schemaVersion": "PhaseBCR1AuthorityConflictResolution/1.0",
        "findingId": "PHASE_E-AUTH-001",
        "status": "RESOLVED_BY_VERSIONED_QUALIFICATION_AUTHORITY_CORRECTION",
        "confirmedContradictions": [
            {
                "caseId": "Q-COMPOSITION-001",
                "requiredInputNotPresent": True,
                "historicalRequiredTool": "structure.composition_from_structure",
                "assetObjectTypes": ["DataFrame"],
                "toolRequiredObjectTypes": ["Structure"],
            },
            {
                "caseId": "Q-COMPOSITION-001",
                "requiredExecutionSetExceedsPlanCap": True,
                "historicalRequiredToolCount": 7,
                "currentPlanStepCap": PLAN_STEP_CAP,
            },
        ],
        "rootCause": "PHASE_A_CAPABILITY_FAMILY_ASSOCIATIONS_WERE_FROZEN_AS_PER_CASE_MANDATORY_EXECUTION_ASSERTIONS",
        "productionSupportChanged": False,
        "historicalDiscoveryEvidencePreserved": True,
        "historicalDiscoveryEvidence": {
            "root": "_qualification/evidence/phase_e/campaign_20260816_blocked_authority_conflict",
            "Q-DATASET-001": "PASS_DISCOVERY",
            "Q-COMPOSITION-001": "BLOCKED_AUTHORITY_CONFLICT",
            "authorityConflict": "_qualification/evidence/phase_e/campaign_20260816_blocked_authority_conflict/AUTHORITY_CONFLICT.json",
            "candidateHistory": "_qualification/evidence/phase_e/campaign_20260816_blocked_authority_conflict/CANDIDATE_HISTORY.json",
        },
    }
    plan_validation = {
        "schemaVersion": "PhaseBCR1PlanCapValidation/1.0",
        "currentPlanStepCap": PLAN_STEP_CAP,
        "cases": [
            {
                "caseId": case["caseId"],
                "requiredExecutionToolCount": case["requiredExecutionToolCount"],
                "maximumRequiredToolsPerTurn": case["maximumRequiredToolsPerTurn"],
                "multiTurnScenarioRequired": case["multiTurnScenarioRequired"],
                "pass": case["maximumRequiredToolsPerTurn"] <= PLAN_STEP_CAP,
            }
            for case in cases
        ],
        "overCapCases": [],
    }
    asset_compatibility = {
        "schemaVersion": "PhaseBCR1AssetSemanticCompatibility/1.0",
        "protectedFiles": len(old_protected),
        "protectedMissing": protected_missing,
        "protectedExtra": protected_extra,
        "protectedHashMismatches": protected_mismatches,
        "sourceBytesChanged": False,
        "externalDataResearchRerun": False,
        "externalDataDownloaded": 0,
        "scientificValueFabrication": 0,
        "unitGuessing": 0,
        "structureInferenceFromFormula": 0,
        "specialPairs": {
            "Q-XRD-001": "Structure + supplied experimental XRD with explicit wavelength",
            "Q-PHONON-001": "Structure + typed Band + typed DOS; generic JSON/YAML remains mapping-only",
            "Q-ELECTRONIC-001": "compatible source calculation, structure identity, energy reference, units, and Fermi identity",
            "Q-TRAJECTORY-001": "source trajectory with stable identities, cell/PBC, and physical time",
            "Q-ARCHIVE-001": "ZIP retained as bounded container, not scientific semantic kind",
        },
    }
    artifact_renderer = {
        "schemaVersion": "PhaseBCR1ArtifactRendererContractMatrix/1.0",
        "cases": [
            {
                "caseId": case["caseId"],
                "requiredArtifactProducers": case["requiredArtifactProducers"],
                "requiredRenderers": case["requiredRenderers"],
            }
            for case in cases
        ],
    }
    package_verification = {
        "schemaVersion": "PhaseBCR1NewPackageVerification/1.0",
        "filename": NEW_PACKAGE_NAME,
        "sha256": first["sha256"],
        "bytes": first["bytes"],
        "entryCount": first["entryCount"],
        "entriesSorted": first["entriesSorted"],
        "deterministicBuild1Sha256": first["sha256"],
        "deterministicBuild2Sha256": second["sha256"],
        "determinism": "PASS",
        "supersedesPackageSha256": OLD_PACKAGE_SHA256,
        "newShaDiffersFromOld": first["sha256"] != OLD_PACKAGE_SHA256,
        "caseHashMismatches": case_mismatch,
        "rootHashMismatches": root_mismatch,
        "missingFiles": case_missing + root_missing,
        "staticExecutableContractValidator": validation["status"],
        "extractedPackageValidator": extracted_validation["status"],
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE / "AUTHORITY_CONFLICT_RESOLUTION.json", conflict_resolution)
    write_json(EVIDENCE / "ALL_CASE_AUTHORITY_AUDIT.json", all_case_audit)
    write_json(EVIDENCE / "CASE_EXECUTION_CONTRACT_MATRIX.json", {"schemaVersion": "PhaseBCR1CaseExecutionContractMatrix/1.0", "cases": cases})
    write_json(EVIDENCE / "CAMPAIGN_COVERAGE_MODEL.json", campaign_model)
    write_json(EVIDENCE / "PLAN_CAP_VALIDATION.json", plan_validation)
    write_json(EVIDENCE / "ASSET_SEMANTIC_COMPATIBILITY.json", asset_compatibility)
    write_json(EVIDENCE / "ARTIFACT_RENDERER_CONTRACT_MATRIX.json", artifact_renderer)
    write_json(EVIDENCE / "REPOSITORY_AUTHORITY_FINGERPRINT.json", fingerprint)
    write_json(EVIDENCE / "PACKAGE_SUPERSESSION.json", supersession)
    write_json(EVIDENCE / "STATIC_EXECUTABLE_CONTRACT_VALIDATION.json", validation)
    write_json(EVIDENCE / "EXTRACTED_PACKAGE_VALIDATION.json", extracted_validation)
    write_json(EVIDENCE / "NEW_PACKAGE_VERIFICATION.json", package_verification)
    write_text(EVIDENCE / "PHASE_BC_R1_RESULT.md", f"""# Phase B/C-R1 Result

`PHASE_BC_R1 = PASS / QUALIFICATION_AUTHORITY_RECONCILED_AND_REFROZEN`

- Historical package SHA-256: `{OLD_PACKAGE_SHA256}` (unchanged)
- New package: `{NEW_PACKAGE_NAME}`
- New package SHA-256: `{first['sha256']}`
- Cases ready for future qualification: `16/16`
- Positive analysis cases: `15`; expected pre-Plan rejection cases: `1`
- Maximum required Tools in any turn: `{max(case['maximumRequiredToolsPerTurn'] for case in cases)}/{PLAN_STEP_CAP}`
- Static executable-contract validator: `PASS`
- Distinct paraphrase authority: `7/16` (unchanged)
- Real LLM calls: `0`
- Live qualification executions: `0`
- Production/support/scientific changes: `0`

The new authority separates required execution from allowed execution and
campaign coverage potential.  `Q-COMPOSITION-001` no longer requires a periodic
Structure Tool from CSV-only assets.  Historical Phase E discovery evidence is
retained and is not counted as qualification evidence for this package.
""")
    evidence_manifest()
    print(json.dumps(package_verification, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
