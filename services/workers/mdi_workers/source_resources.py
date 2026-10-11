from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping

from mdi_schemas import AnalysisPlan, AnalysisPlanV02, AnalysisPlanV03, parse_analysis_plan
from mdi_tool_registry import ToolRegistry, validate_dependency_plan
from mdi_tool_registry.plan_validator import validate_plan


def _same_runtime_payload(left: Any, right: Any) -> bool:
    """Compare runtime source payloads without invoking ambiguous DataFrame truthiness."""
    try:
        import pandas as pd

        if isinstance(left, pd.DataFrame) or isinstance(right, pd.DataFrame):
            return isinstance(left, pd.DataFrame) and isinstance(right, pd.DataFrame) and left.equals(right)
    except Exception:
        # Non-tabular payloads must retain the historical equality behavior below.
        pass
    try:
        result = left == right
        return bool(result) if not hasattr(result, "all") else bool(result.all())
    except Exception:
        return left is right


SOURCE_RESOURCE_INDEX_KEY = "__mdi_source_resources__"
CUKA_WAVELENGTH_ANGSTROM = 1.54184


@dataclass(frozen=True)
class ExecutionPreflightIssue:
    code: str
    message: str
    step_id: str | None = None
    ref: str | None = None


@dataclass(frozen=True)
class ExecutionPreflightResult:
    ok: bool
    resolved_root_refs: tuple[str, ...] = ()
    issues: tuple[ExecutionPreflightIssue, ...] = ()
    dependency_contracts_checked: int = 0
    scientific_compatibility_checks: tuple[str, ...] = ()


def register_runtime_source_resource(
    object_store: MutableMapping[str, Any],
    *,
    object_id: str,
    object_type: str,
    object_hash: str,
    dataset_id: str,
    value: Any,
    aliases: tuple[str, ...] = (),
) -> None:
    """Register one exact parsed source without creating a second authority."""
    if not object_id or not object_type or not object_hash or not dataset_id:
        raise ValueError("Runtime source identity requires id, type, hash, and dataset scope.")
    index = object_store.setdefault(SOURCE_RESOURCE_INDEX_KEY, {})
    if not isinstance(index, dict):
        raise ValueError("Runtime source index is invalid.")
    identity = {"objectId": object_id, "objectType": object_type, "objectHash": object_hash, "datasetId": dataset_id}
    current = index.get(object_id)
    if current is not None and current != identity:
        raise ValueError(f"Conflicting runtime source identity: {object_id}")
    if object_id in object_store and not _same_runtime_payload(object_store[object_id], value):
        raise ValueError(f"Conflicting runtime source payload: {object_id}")
    index[object_id] = identity
    object_store[object_id] = value
    for alias in aliases:
        if alias in object_store and not _same_runtime_payload(object_store[alias], value):
            raise ValueError(f"Conflicting runtime source alias: {alias}")
        object_store[alias] = value
        index[alias] = {**identity, "alias": alias, "canonicalObjectId": object_id}


def preflight_execution_resources(
    plan: AnalysisPlan | AnalysisPlanV02 | Mapping[str, Any],
    *,
    object_store: Mapping[str, Any],
    registry: ToolRegistry,
    dataset_id: str,
) -> ExecutionPreflightResult:
    """Resolve all root refs and formal dependencies without creating a Job."""
    payload = plan.model_dump(mode="json") if hasattr(plan, "model_dump") else dict(plan)
    validation = validate_plan(payload, registry=registry)
    issues = [ExecutionPreflightIssue(item.code, item.message) for item in validation.errors]
    try:
        parsed = parse_analysis_plan(payload)
    except ValueError:
        return ExecutionPreflightResult(ok=False, issues=tuple(issues))
    dependency_count = 0
    if isinstance(parsed, AnalysisPlanV02):
        dependency = validate_dependency_plan(parsed, registry=registry)
        dependency_count = len(parsed.dependencyBindings)
        issues.extend(
            ExecutionPreflightIssue(item.code.value, item.message)
            for item in dependency.errors
        )

    index = object_store.get(SOURCE_RESOURCE_INDEX_KEY)
    if not isinstance(index, Mapping):
        index = {}
    profile = object_store.get("profile")
    profile_resources = {
        item.objectId: item
        for item in getattr(profile, "resourceSemantics", ())
    }
    source_datasets: dict[str, str] = {}
    resources_by_dataset: dict[str, dict[str, Any]] = {}
    if isinstance(parsed, AnalysisPlanV03):
        if parsed.datasetId != dataset_id:
            issues.append(ExecutionPreflightIssue("ROOT_RESOURCE_SCOPE_MISMATCH", "Job routing dataset differs from the exact Plan."))
        source_datasets = {str(item.versionId): item.datasetId for item in parsed.sourceVersions}
        for context in parsed.sourceContexts:
            profile_ref = f"profile:{context.profileId}"
            source_datasets[profile_ref] = context.datasetId
            source_profile = object_store.get(profile_ref)
            if (getattr(source_profile, "profileId", None) != context.profileId
                or getattr(source_profile, "datasetId", None) != context.datasetId):
                issues.append(ExecutionPreflightIssue("ROOT_PROFILE_SCOPE_MISMATCH", "Exact source Profile is unavailable or belongs to another dataset.", ref=profile_ref))
                continue
            resources_by_dataset[context.datasetId] = {item.objectId: item for item in source_profile.resourceSemantics}
    resolved: list[str] = []
    for step in parsed.steps:
        for input_ref in step.inputRefs:
            if input_ref.refType == "artifact":
                continue
            ref = input_ref.ref
            identity = index.get(ref)
            if ref not in object_store or not isinstance(identity, Mapping):
                issues.append(ExecutionPreflightIssue("ROOT_RESOURCE_UNRESOLVED", "Exact source resource is unavailable.", step.stepId, ref))
                continue
            expected_dataset = source_datasets.get(ref) if isinstance(parsed, AnalysisPlanV03) else dataset_id
            if identity.get("datasetId") != expected_dataset:
                issues.append(ExecutionPreflightIssue("ROOT_RESOURCE_SCOPE_MISMATCH", "Source resource belongs to another dataset.", step.stepId, ref))
                continue
            expected_type = input_ref.objectType.value if input_ref.objectType is not None else None
            if expected_type and identity.get("objectType") != expected_type:
                issues.append(ExecutionPreflightIssue("ROOT_RESOURCE_KIND_MISMATCH", "Source resource type does not match the Plan binding.", step.stepId, ref))
                continue
            if not identity.get("objectHash"):
                issues.append(ExecutionPreflightIssue("ROOT_RESOURCE_HASH_MISSING", "Source resource hash is unavailable.", step.stepId, ref))
                continue
            profile_resource = (resources_by_dataset.get(expected_dataset, {}).get(str(identity.get("profileObjectId") or ref))
                                if isinstance(parsed, AnalysisPlanV03) else profile_resources.get(ref))
            profile_hash = identity.get("objectHash")
            if isinstance(parsed, AnalysisPlanV03) and identity.get("profileObjectId"):
                if profile_resource is None:
                    issues.append(ExecutionPreflightIssue("ROOT_PROFILE_RESOURCE_MISSING", "Exact source Profile resource is unavailable.", step.stepId, ref))
                    continue
                profile_hash = identity.get("profileObjectHash")
            if profile_resource is not None and profile_hash != profile_resource.objectHash:
                issues.append(ExecutionPreflightIssue("ROOT_RESOURCE_HASH_MISMATCH", "Source resource hash differs from the exact Profile authority.", step.stepId, ref))
                continue
            resolved.append(ref)

    compatibility_checks: list[str] = []
    step_by_id = {step.stepId: step for step in parsed.steps}
    xrd_pairs = [(step_by_id[binding.producerStepId], step_by_id[binding.consumerStepId])
                 for binding in (parsed.dependencyBindings if isinstance(parsed, AnalysisPlanV02) else [])
                 if step_by_id[binding.producerStepId].toolId == "structure.xrd"
                 and step_by_id[binding.consumerStepId].toolId == "structure.experimental_xrd_comparison"]
    if not isinstance(parsed, AnalysisPlanV03) and not xrd_pairs:
        theoretical = [step for step in parsed.steps if step.toolId == "structure.xrd"]
        experimental = [step for step in parsed.steps if step.toolId == "structure.experimental_xrd_comparison"]
        if len(theoretical) == len(experimental) == 1:
            xrd_pairs = [(theoretical[0], experimental[0])]
    for theoretical_step, experimental_step in xrd_pairs:
        experimental_refs = [ref.ref for ref in experimental_step.inputRefs if ref.refType != "artifact"]
        experimental = object_store.get(experimental_refs[0]) if len(experimental_refs) == 1 else None
        wavelength = experimental.get("wavelength") if isinstance(experimental, Mapping) else None
        value = wavelength.get("value") if isinstance(wavelength, Mapping) else None
        unit = wavelength.get("unit") if isinstance(wavelength, Mapping) else None
        radiation = theoretical_step.params.get("radiation", "CuKa")
        if radiation != "CuKa" or unit != "angstrom" or value != CUKA_WAVELENGTH_ANGSTROM:
            issues.append(ExecutionPreflightIssue("XRD_WAVELENGTH_MISMATCH", "Experimental and planned theoretical XRD wavelengths are incompatible."))
        else:
            compatibility_checks.append("XRD_WAVELENGTH_EXACT_MATCH")

    return ExecutionPreflightResult(
        ok=not issues,
        resolved_root_refs=tuple(sorted(set(resolved))),
        issues=tuple(issues),
        dependency_contracts_checked=dependency_count,
        scientific_compatibility_checks=tuple(compatibility_checks),
    )
