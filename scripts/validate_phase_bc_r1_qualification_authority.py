"""Static executable-contract validator for the Phase B/C-R1 package.

The validator performs no live provider, browser, queue, worker, Tool, or
Artifact execution.  It compares a package to the exact current Registry,
Planner metadata, renderer declarations, and package assets.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from mdi_schemas import CAPABILITY_PLANNING_MAX_SELECTED_TOOLS
from mdi_tool_registry import load_manifests
from mdi_tool_registry.planner_metadata import build_registry_snapshot

from phase_bc_r1_contracts import (
    CASE_SCHEMA_VERSION,
    PLAN_STEP_CAP,
    PLATFORM_ARTIFACT_PRODUCERS,
    ROOT_SCHEMA_VERSION,
    SEMANTIC_OBJECT_TYPES,
)


ROOT = Path(__file__).resolve().parents[1]
RENDERER_INVENTORY = ROOT / "docs/qualification/phase_a_repository_capability_census/renderer_qualification_inventory.json"
CUKA_WAVELENGTH_ANGSTROM = 1.54184
TRANSPORT_CONTRACT_FILE = "REPOSITORY_INPUT_TRANSPORT_CONTRACT.json"
BINARY_EXTENSIONS = {".zip", ".npy", ".npz", ".brml"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _issue(issues: list[dict[str, str]], case_id: str, code: str, detail: str) -> None:
    issues.append({"caseId": case_id, "code": code, "detail": detail})


def _renderer_map() -> dict[str, set[str]]:
    payload = load_json(RENDERER_INVENTORY)
    mapping: dict[str, set[str]] = {}
    for renderer in payload["renderers"]:
        for artifact in renderer["artifactTypes"]:
            mapping.setdefault(artifact, set()).add(renderer["rendererContract"])
    return mapping


def _semantic_object_types(case: dict[str, Any]) -> set[str]:
    return {
        object_type
        for kind in case["semanticDataKinds"]
        for object_type in SEMANTIC_OBJECT_TYPES.get(kind, set())
    }


def _input_satisfied(metadata: Any, object_types: set[str]) -> bool:
    return any(set(option).issubset(object_types) for option in metadata.inputObjectTypeOptions)


def _verify_assets(case_dir: Path, case: dict[str, Any], issues: list[dict[str, str]]) -> None:
    case_id = case["caseId"]
    filenames = {asset["filename"] for asset in case["assets"]}
    roles = [asset["role"] for asset in case["assets"]]
    if len(roles) != len(set(roles)):
        _issue(issues, case_id, "DUPLICATE_SEMANTIC_ROLE", "Asset roles are not unique.")
    for asset in case["assets"]:
        path = case_dir / asset["filename"]
        if not path.is_file():
            _issue(issues, case_id, "REQUIRED_ASSET_MISSING", asset["filename"])
            continue
        actual = sha256(path)
        if actual != asset["sha256"]:
            _issue(issues, case_id, "ASSET_HASH_MISMATCH", f"{asset['filename']}: {actual}")
        for companion in asset.get("requiredCompanionAssets", []):
            if companion not in filenames or not (case_dir / companion).is_file():
                _issue(issues, case_id, "MISSING_REQUIRED_COMPANION_ASSET", f"{asset['filename']} -> {companion}")


def _verify_csv_roles(case_dir: Path, case: dict[str, Any], issues: list[dict[str, str]]) -> None:
    required_by_kind = {
        "regression_result_table": {"sample_id", "y_true_eV", "y_pred_eV"},
        "uncertainty_result_table": {"sample_id", "y_true_eV", "y_pred_eV", "y_std_eV"},
        "classification_result_table": {"sample_id", "class_true", "class_pred", "prob_perovskite"},
    }
    expected = set().union(*(required_by_kind.get(kind, set()) for kind in case["semanticDataKinds"]))
    if not expected:
        return
    csv_asset = next((item for item in case["assets"] if item["filename"].lower().endswith(".csv")), None)
    if csv_asset is None:
        _issue(issues, case["caseId"], "REQUIRED_SEMANTIC_COLUMNS_MISSING", "No CSV asset declares required source columns.")
        return
    with (case_dir / csv_asset["filename"]).open("r", encoding="utf-8-sig", newline="") as stream:
        columns = set(next(csv.reader(stream)))
    missing = sorted(expected - columns)
    if missing:
        _issue(issues, case["caseId"], "REQUIRED_SEMANTIC_COLUMNS_MISSING", ",".join(missing))


def _verify_pair_identity(case_dir: Path, case: dict[str, Any], issues: list[dict[str, str]]) -> None:
    case_id = case["caseId"]
    if case_id == "Q-XRD-001":
        asset = next(item for item in case["assets"] if item["semanticKind"] == "experimental_xrd")
        payload = load_json(case_dir / asset["filename"])
        wavelength = payload.get("wavelength") or {}
        x_axis = payload.get("xAxis") or {}
        if not isinstance(wavelength.get("value"), (int, float)) or wavelength.get("value", 0) <= 0:
            _issue(issues, case_id, "INCOMPATIBLE_MULTI_RESOURCE_IDENTITY", "XRD wavelength is not explicit and positive.")
        if wavelength.get("unit") != "angstrom" or x_axis.get("kind") != "two_theta" or x_axis.get("unit") != "degree":
            _issue(issues, case_id, "INCOMPATIBLE_MULTI_RESOURCE_IDENTITY", "XRD axis/wavelength contract is incompatible.")
        value = wavelength.get("value")
        if not isinstance(value, (int, float)) or abs(float(value) - CUKA_WAVELENGTH_ANGSTROM) > 1e-9:
            _issue(
                issues,
                case_id,
                "XRD_WAVELENGTH_INCOMPATIBILITY",
                f"Experimental wavelength {value!r} does not match released CuKa authority {CUKA_WAVELENGTH_ANGSTROM} angstrom.",
            )
    elif case_id == "Q-PHONON-001":
        band = load_json(case_dir / next(item["filename"] for item in case["assets"] if item["semanticKind"] == "phonon_band"))
        dos = load_json(case_dir / next(item["filename"] for item in case["assets"] if item["semanticKind"] == "phonon_dos"))
        for key in ("structure_identity", "atom_count", "species", "atom_ordering", "frequency_unit"):
            if band.get(key) != dos.get(key):
                _issue(issues, case_id, "INCOMPATIBLE_MULTI_RESOURCE_IDENTITY", f"Phonon Band/DOS mismatch: {key}")
    elif case_id == "Q-ELECTRONIC-001":
        band = load_json(case_dir / next(item["filename"] for item in case["assets"] if item["semanticKind"] == "electronic_band"))
        dos = load_json(case_dir / next(item["filename"] for item in case["assets"] if item["semanticKind"] == "electronic_dos"))
        for key in ("calculationIdentity", "structureIdentity", "energyUnit", "energyReference", "fermiEnergyEv"):
            if band.get(key) != dos.get(key):
                _issue(issues, case_id, "INCOMPATIBLE_MULTI_RESOURCE_IDENTITY", f"Electronic Band/DOS mismatch: {key}")


def _verify_case(
    case_dir: Path,
    case: dict[str, Any],
    tools: dict[str, Any],
    metadata: dict[str, Any],
    renderers: dict[str, set[str]],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    case_id = case.get("caseId", case_dir.name)
    if case.get("schemaVersion") != CASE_SCHEMA_VERSION:
        _issue(issues, case_id, "CASE_SCHEMA_VERSION_INVALID", str(case.get("schemaVersion")))
    required = case.get("requiredExecutionTools") or []
    allowed = case.get("allowedExecutionTools") or []
    forbidden = case.get("forbiddenExecutionTools") or []
    if required != sorted(set(required)) or allowed != sorted(set(allowed)) or forbidden != sorted(set(forbidden)):
        _issue(issues, case_id, "TOOL_LIST_NOT_CANONICAL", "Tool lists must be unique and sorted.")
    if set(required) & set(allowed) or set(required) & set(forbidden) or set(allowed) & set(forbidden):
        _issue(issues, case_id, "TOOL_DISPOSITION_OVERLAP", "Required, allowed, and forbidden Tool sets overlap.")
    if set(required) | set(allowed) | set(forbidden) != set(tools):
        _issue(issues, case_id, "TOOL_DISPOSITION_INCOMPLETE", "Every current Registry Tool must have one Case disposition.")

    turns = case.get("executionTurns", [])
    turn_tools = sorted({tool for item in turns for tool in item["requiredExecutionTools"]})
    if turn_tools != required:
        _issue(
            issues,
            case_id,
            "EXECUTION_TURN_TOOL_UNION_MISMATCH",
            "Turn Tool union differs from requiredExecutionTools.",
        )
    if case.get("requiredExecutionToolCount") != len(set(required)):
        _issue(issues, case_id, "REQUIRED_TOOL_COUNT_MISMATCH", str(case.get("requiredExecutionToolCount")))
    if not set(case.get("explicitForbiddenExecutionTools") or []).issubset(forbidden):
        _issue(issues, case_id, "EXPLICIT_FORBIDDEN_TOOL_NOT_FORBIDDEN", "Explicit negative boundary is not preserved.")
    for item in turns:
        turn_required = item["requiredExecutionTools"]
        turn_max = item.get("maxRequiredStepCount")
        if len(turn_required) != len(set(turn_required)):
            _issue(issues, case_id, "EXECUTION_TURN_TOOL_UNION_MISMATCH", f"{item['turnId']}: duplicate Tool")
        if not isinstance(turn_max, int) or len(turn_required) > turn_max or turn_max > PLAN_STEP_CAP:
            _issue(issues, case_id, "REQUIRED_TOOL_COUNT_OVER_PLAN_CAP", item["turnId"])
        if item.get("planVersionExpected") not in {"0.1", "0.2"}:
            _issue(issues, case_id, "PLAN_VERSION_UNSUPPORTED", item["turnId"])
    if case.get("currentPlanStepCap") != PLAN_STEP_CAP:
        _issue(issues, case_id, "PLAN_CAP_AUTHORITY_MISMATCH", str(case.get("currentPlanStepCap")))
    if CAPABILITY_PLANNING_MAX_SELECTED_TOOLS != PLAN_STEP_CAP:
        _issue(issues, case_id, "REPOSITORY_PLAN_CAP_DRIFT", str(CAPABILITY_PLANNING_MAX_SELECTED_TOOLS))

    object_types = _semantic_object_types(case)
    for tool_id in required + allowed:
        tool = tools.get(tool_id)
        planner = metadata.get(tool_id)
        if tool is None or planner is None:
            _issue(issues, case_id, "REQUIRED_TOOL_NOT_REGISTRY_CURRENT", tool_id)
            continue
        if planner.availability.value != "AVAILABLE" or tool.stage != "mvp" or not tool.adapter:
            _issue(issues, case_id, "REQUIRED_TOOL_NOT_EXECUTION_READY", tool_id)
        if not _input_satisfied(planner, object_types):
            _issue(issues, case_id, "REQUIRED_TOOL_INPUT_KIND_ABSENT", f"{tool_id}: {sorted(object_types)}")

    if case.get("analysisExecutionExpected", True):
        if not required or case.get("supportDisposition") in {"MAPPING_ONLY", "UNSUPPORTED"}:
            _issue(issues, case_id, "SUPPORT_DISPOSITION_CONTRADICTION", "Executable analysis lacks supported required Tools.")
    elif required or case.get("supportDisposition") != "UNSUPPORTED":
        _issue(issues, case_id, "SUPPORT_DISPOSITION_CONTRADICTION", "Expected rejection must not require executable Tools.")

    alias_pairs = (
        ("expectedReport", "requiredReportBehavior", "CONFLICTING_REPORT_REQUIREMENTS"),
        ("expectedRecipe", "requiredRecipeBehavior", "CONFLICTING_RECIPE_REQUIREMENTS"),
        ("expectedLimitationAssertions", "requiredLimitations", "CONFLICTING_LIMITATION_REQUIREMENTS"),
    )
    for alias, canonical, code in alias_pairs:
        if alias not in case or canonical not in case or case.get(alias) != case.get(canonical):
            _issue(issues, case_id, code, f"{alias} must exactly mirror {canonical}.")

    if case.get("caseType") == "EXPECTED_REJECTION":
        report = case.get("requiredReportBehavior") or {}
        recipe = case.get("requiredRecipeBehavior") or {}
        rejection_conflicts = {
            "analysisExecutionExpected": case.get("analysisExecutionExpected") is not False,
            "requiredExecutionTools": bool(required),
            "executionTurns": bool(turns),
            "requiredArtifacts": bool(case.get("requiredArtifacts")),
            "requiredRenderers": bool(case.get("requiredRenderers")),
            "reportPreviewExpected": report.get("previewExpected") is not False,
            "reportFinalizeExpected": report.get("finalizeExpected") is not False,
            "reportSourceEligible": report.get("sourceEligible") is not False,
            "recipeExpected": recipe.get("expected") is not False,
            "recipeExecutionAuthorized": recipe.get("recipeExecutionAuthorized") is not False,
        }
        active = sorted(field for field, conflicting in rejection_conflicts.items() if conflicting)
        if active:
            _issue(
                issues,
                case_id,
                "EXPECTED_REJECTION_HAS_EXECUTION_REQUIREMENTS",
                ",".join(active),
            )

    produced: dict[str, set[str]] = {artifact: {producer} for artifact, producer in PLATFORM_ARTIFACT_PRODUCERS.items()}
    for tool_id in required:
        for artifact in tools[tool_id].artifactTypes:
            produced.setdefault(artifact.value, set()).add(tool_id)
    required_artifacts = case.get("requiredArtifacts") or []
    for artifact in required_artifacts:
        if artifact not in produced:
            _issue(issues, case_id, "REQUIRED_ARTIFACT_WITHOUT_PRODUCER", artifact)
    declared_renderers = case.get("requiredRenderers") or []
    rendered_artifacts: set[str] = set()
    for declaration in declared_renderers:
        artifact = declaration.get("artifactType")
        renderer = declaration.get("rendererContract")
        rendered_artifacts.add(artifact)
        if artifact not in required_artifacts or renderer not in renderers.get(artifact, set()):
            _issue(issues, case_id, "REQUIRED_RENDERER_WITHOUT_ARTIFACT", f"{artifact} -> {renderer}")
    if rendered_artifacts != set(required_artifacts):
        _issue(issues, case_id, "REQUIRED_RENDERER_COVERAGE_INCOMPLETE", ",".join(sorted(set(required_artifacts) - rendered_artifacts)))

    _verify_assets(case_dir, case, issues)
    _verify_csv_roles(case_dir, case, issues)
    _verify_pair_identity(case_dir, case, issues)
    if len(case.get("semanticDataKinds") or []) != len(set(case.get("semanticDataKinds") or [])):
        _issue(issues, case_id, "CONFLICTING_SEMANTIC_KIND", "semanticDataKinds contains duplicates.")
    asset_semantic_kinds = {asset["semanticKind"] for asset in case.get("assets", [])}
    contained_semantic_kinds = {
        kind for asset in case.get("assets", []) for kind in asset.get("containedSemanticKinds", [])
    }
    declared_semantic_kinds = set(case.get("semanticDataKinds") or [])
    expected_semantic_kinds = asset_semantic_kinds | contained_semantic_kinds
    if expected_semantic_kinds != declared_semantic_kinds:
        _issue(issues, case_id, "ASSET_SEMANTIC_KIND_CONTRADICTION", str(sorted(asset_semantic_kinds)))
    for asset in case.get("assets", []):
        if asset.get("semanticKind") in {"phonon_band", "phonon_dos"} and asset.get("phaseAInputFormat") not in {
            "TYPED_PHONON_BAND_JSON",
            "TYPED_PHONON_DOS_JSON",
        }:
            _issue(issues, case_id, "MAPPING_ONLY_REQUIRED_AS_EXECUTABLE", asset["filename"])
    if not case.get("entryPath") or not case.get("importMode"):
        _issue(issues, case_id, "NO_VALID_PRIMARY_USER_PATH", "Entry path/import mode missing.")
    if not case.get("requiredUserOutcome"):
        _issue(issues, case_id, "REQUIRED_USER_OUTCOME_MISSING", "No user-visible outcome is defined.")
    if case.get("expectedRecipe", {}).get("recipeExecutionAuthorized") is not False:
        _issue(issues, case_id, "RECIPE_EXECUTION_AUTHORITY_INVALID", "Recipe execution must remain unauthorized.")
    return issues


def _verify_primary_submission_authority(package_dir: Path, cases: list[dict[str, Any]], issues: list[dict[str, str]]) -> None:
    path = package_dir / "PRIMARY_QUALIFICATION_EXECUTION_AUTHORITY.json"
    if not path.is_file():
        _issue(issues, "PACKAGE", "PRIMARY_SUBMISSION_AUTHORITY_MISSING", path.name)
        return
    payload = load_json(path)
    rows = {row.get("caseId"): row for row in payload.get("cases", [])}
    if set(rows) != {case["caseId"] for case in cases}:
        _issue(issues, "PACKAGE", "PRIMARY_SUBMISSION_AUTHORITY_INCOMPLETE", "Expected exactly all 16 Cases.")
        return
    for case in cases:
        case_id = case["caseId"]
        row = rows[case_id]
        turns = case.get("executionTurns", [])
        if case.get("caseType") == "EXPECTED_REJECTION":
            expected_mode = "CANONICAL_QUESTION_EXPECTED_PRE_PLAN_REJECTION"
            expected_questions = [case["canonicalQuestion"]]
        elif case.get("multiTurnScenarioRequired"):
            expected_mode = "ORDERED_EXECUTION_TURNS"
            expected_questions = [turn["question"] for turn in turns]
        else:
            expected_mode = "SINGLE_EXECUTION_TURN"
            expected_questions = [turns[0]["question"]] if len(turns) == 1 else []
        if row.get("submissionMode") != expected_mode or row.get("plannerSubmissionQuestions") != expected_questions:
            _issue(
                issues,
                case_id,
                "PRIMARY_SUBMISSION_AUTHORITY_CONTRADICTION",
                f"Expected {expected_mode} with declared ordered question(s).",
            )


def _verify_input_transport(
    package_dir: Path,
    case_dir: Path,
    case: dict[str, Any],
    issues: list[dict[str, str]],
) -> None:
    contract_path = package_dir / TRANSPORT_CONTRACT_FILE
    case_id = case["caseId"]
    if not contract_path.is_file():
        _issue(issues, case_id, "REPOSITORY_INPUT_TRANSPORT_CONTRACT_MISSING", TRANSPORT_CONTRACT_FILE)
        return
    contract = load_json(contract_path)
    required = {
        "schemaVersion",
        "entryPathId",
        "supportsTextBytes",
        "supportsBinaryBytes",
        "supportsMultipleResources",
        "maxFilesPerSubmission",
        "perFileByteCap",
        "totalByteCap",
        "sameDatasetCompanionPolicy",
        "roleBindingPolicy",
        "fileOrderIsSemanticAuthority",
        "partialFailurePolicy",
        "supportedImportModes",
        "semanticHash",
    }
    if not required.issubset(contract):
        _issue(issues, case_id, "REPOSITORY_INPUT_TRANSPORT_CONTRACT_INVALID", "Required transport fields are absent.")
        return
    aliases = set(contract.get("qualificationEntryPathAliases") or [])
    if case.get("entryPath") not in aliases | {contract.get("entryPathId")}:
        _issue(issues, case_id, "NO_VALID_PRIMARY_USER_PATH", str(case.get("entryPath")))

    assets = case.get("assets") or []
    max_files = contract.get("maxFilesPerSubmission")
    if not isinstance(max_files, int) or len(assets) > max_files:
        _issue(issues, case_id, "ASSET_COUNT_EXCEEDS_ENTRY_PATH_CAP", f"{len(assets)} > {max_files!r}")
    if len(assets) > 1 and contract.get("supportsMultipleResources") is not True:
        _issue(issues, case_id, "COMPANION_IMPORT_UNAVAILABLE", "Entry path cannot import multiple resources.")
    has_companions = any(asset.get("requiredCompanionAssets") for asset in assets)
    if has_companions and contract.get("sameDatasetCompanionPolicy") != "ATOMIC_SINGLE_UPLOAD_SESSION":
        _issue(issues, case_id, "SAME_DATASET_BINDING_UNAVAILABLE", str(contract.get("sameDatasetCompanionPolicy")))
    if case.get("uploadFileOrderSemantic") or contract.get("fileOrderIsSemanticAuthority") is not False:
        _issue(issues, case_id, "FILE_ORDER_ROLE_AUTHORITY_REQUIRED", "Role binding must not depend on file order.")

    supported_modes = set(contract.get("qualificationImportModeAliases") or [])
    sizes: list[int] = []
    binary_assets = 0
    text_assets = 0
    for asset in assets:
        mode = asset.get("importMode")
        if mode not in supported_modes:
            _issue(issues, case_id, "UNSUPPORTED_IMPORT_MODE", f"{asset.get('filename')}: {mode}")
        path = case_dir / asset["filename"]
        if path.is_file():
            sizes.append(path.stat().st_size)
            if path.suffix.lower() in BINARY_EXTENSIONS:
                binary_assets += 1
            else:
                text_assets += 1
    if binary_assets and contract.get("supportsBinaryBytes") is not True:
        _issue(issues, case_id, "BINARY_ASSET_ON_TEXT_ONLY_ENTRY_PATH", f"{binary_assets} binary asset(s)")
    if text_assets and contract.get("supportsTextBytes") is not True:
        _issue(issues, case_id, "TEXT_ASSET_ON_BINARY_ONLY_ENTRY_PATH", f"{text_assets} text asset(s)")
    per_file_cap = contract.get("perFileByteCap")
    total_cap = contract.get("totalByteCap")
    if not isinstance(per_file_cap, int) or any(size > per_file_cap for size in sizes):
        _issue(issues, case_id, "UPLOAD_SIZE_CAP_CONFLICT", f"per-file sizes={sizes}, cap={per_file_cap!r}")
    if not isinstance(total_cap, int) or sum(sizes) > total_cap:
        _issue(issues, case_id, "UPLOAD_SIZE_CAP_CONFLICT", f"total={sum(sizes)}, cap={total_cap!r}")
    if binary_assets and text_assets and not (
        contract.get("supportsBinaryBytes") is True and contract.get("supportsTextBytes") is True
    ):
        _issue(issues, case_id, "MIXED_BINARY_TEXT_TRANSPORT_UNSUPPORTED", "Mixed assets require byte-safe generic transport.")


def _verify_repository_fingerprint(
    package_dir: Path,
    registry: Any,
    snapshot: Any,
    metadata: dict[str, Any],
    issues: list[dict[str, str]],
) -> None:
    path = package_dir / "REPOSITORY_AUTHORITY_FINGERPRINT.json"
    if not path.is_file():
        _issue(issues, "PACKAGE", "REPOSITORY_AUTHORITY_FINGERPRINT_MISSING", path.name)
        return
    fingerprint = load_json(path)
    current_head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, encoding="utf-8"
    ).strip()
    checks = {
        "repositoryExactSha": current_head,
        "AnalysisPlanStepCap": CAPABILITY_PLANNING_MAX_SELECTED_TOOLS,
        "ToolPlannerMetadataVersion": next(iter(metadata.values())).schemaVersion,
    }
    for field, expected in checks.items():
        if fingerprint.get(field) != expected:
            _issue(
                issues,
                "PACKAGE",
                "REPOSITORY_AUTHORITY_FINGERPRINT_DRIFT",
                f"{field}: package={fingerprint.get(field)!r}, current={expected!r}",
            )
    registry_fingerprint = fingerprint.get("registry") or {}
    registry_checks = {
        "version": registry.version,
        "toolCount": len(registry.tools),
        "snapshotId": snapshot.snapshotId,
        "snapshotHash": snapshot.snapshotHash,
    }
    for field, expected in registry_checks.items():
        if registry_fingerprint.get(field) != expected:
            _issue(
                issues,
                "PACKAGE",
                "REPOSITORY_AUTHORITY_FINGERPRINT_DRIFT",
                f"registry.{field}: package={registry_fingerprint.get(field)!r}, current={expected!r}",
            )
    transport_path = package_dir / TRANSPORT_CONTRACT_FILE
    if transport_path.is_file():
        transport = load_json(transport_path)
        expected_hash = transport.get("semanticHash")
        actual_hash = (fingerprint.get("inputTransport") or {}).get("semanticHash")
        if not expected_hash or actual_hash != expected_hash:
            _issue(
                issues,
                "PACKAGE",
                "REPOSITORY_INPUT_TRANSPORT_FINGERPRINT_DRIFT",
                f"fingerprint={actual_hash!r}, contract={expected_hash!r}",
            )


def parse_hash_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        digest, relative = raw.split("  ", 1)
        entries[relative.replace("\\", "/")] = digest
    return entries


def verify_hash_manifest(root: Path, manifest: Path, *, require_complete: bool = False) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not manifest.is_file():
        return [{"caseId": "PACKAGE", "code": "HASH_MANIFEST_FILE_MISSING", "detail": manifest.name}]
    entries: dict[str, str] = {}
    for line_number, raw in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            digest, relative = raw.split("  ", 1)
        except ValueError:
            issues.append({"caseId": "PACKAGE", "code": "HASH_MANIFEST_MALFORMED", "detail": f"line {line_number}"})
            continue
        relative = relative.replace("\\", "/")
        if relative in entries:
            issues.append({"caseId": "PACKAGE", "code": "HASH_MANIFEST_DUPLICATE_ENTRY", "detail": relative})
        entries[relative] = digest
    for relative, expected in entries.items():
        target = root / relative
        if not target.is_file():
            issues.append({"caseId": "PACKAGE", "code": "HASH_MANIFEST_FILE_MISSING", "detail": relative})
        elif sha256(target) != expected:
            issues.append({"caseId": "PACKAGE", "code": "HASH_MANIFEST_MISMATCH", "detail": relative})
    if require_complete:
        expected_paths = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and path.resolve() != manifest.resolve()
        }
        if set(entries) != expected_paths:
            missing = sorted(expected_paths - set(entries))
            extra = sorted(set(entries) - expected_paths)
            issues.append(
                {
                    "caseId": "PACKAGE",
                    "code": "HASH_MANIFEST_COVERAGE_MISMATCH",
                    "detail": f"missing={missing}; extra={extra}",
                }
            )
    return issues


def validate_package(package_dir: Path) -> dict[str, Any]:
    registry = load_manifests()
    snapshot, metadata = build_registry_snapshot(registry)
    tools = {tool.toolId: tool for tool in registry.tools}
    renderers = _renderer_map()
    root_manifest = load_json(package_dir / "MANIFEST.json")
    issues: list[dict[str, str]] = []
    if root_manifest.get("schemaVersion") != ROOT_SCHEMA_VERSION:
        _issue(issues, "PACKAGE", "ROOT_SCHEMA_VERSION_INVALID", str(root_manifest.get("schemaVersion")))
    _verify_repository_fingerprint(package_dir, registry, snapshot, metadata, issues)
    case_dirs = sorted(path.parent for path in package_dir.glob("*/CASE.json"))
    cases: list[dict[str, Any]] = []
    for case_dir in case_dirs:
        case = load_json(case_dir / "CASE.json")
        cases.append(case)
        issues.extend(_verify_case(case_dir, case, tools, metadata, renderers))
        if root_manifest.get("qualificationAuthorityRevision") == "R1.2":
            _verify_input_transport(package_dir, case_dir, case, issues)
        issues.extend(
            verify_hash_manifest(
                case_dir,
                case_dir / "SHA256SUMS.txt",
                require_complete=root_manifest.get("qualificationAuthorityRevision") == "R1.2",
            )
        )
    if root_manifest.get("qualificationAuthorityRevision") in {"R1.1", "R1.2"}:
        _verify_primary_submission_authority(package_dir, cases, issues)
    issues.extend(
        verify_hash_manifest(
            package_dir,
            package_dir / "SHA256SUMS.txt",
            require_complete=root_manifest.get("qualificationAuthorityRevision") == "R1.2",
        )
    )
    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue["code"]] = counts.get(issue["code"], 0) + 1
    return {
        "schemaVersion": "PhaseBCR1StaticExecutableContractValidation/1.0",
        "status": "PASS" if not issues and len(case_dirs) == 16 else "FAIL",
        "caseCount": len(case_dirs),
        "registryVersion": registry.version,
        "registryToolCount": len(registry.tools),
        "registrySnapshotId": snapshot.snapshotId,
        "registrySnapshotHash": snapshot.snapshotHash,
        "analysisPlanStepCap": PLAN_STEP_CAP,
        "issueCounts": dict(sorted(counts.items())),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate_package(args.package_dir.resolve())
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    sys.stdout.write(encoded)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
