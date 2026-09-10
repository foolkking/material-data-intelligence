"""Independent validator for AnalysisPlan 0.2 dependency semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mdi_schemas import (
    AnalysisPlanV02,
    DependencyDiagnostic,
    DependencyDiagnosticCode,
    compute_dependency_graph_hash,
    deterministic_binding_id,
    topological_order,
)

from .dependency_ports import build_artifact_compatibility_matrix
from .dependency_ports import build_artifact_port_inventory


@dataclass(frozen=True)
class DependencyValidationResult:
    ok: bool
    errors: list[DependencyDiagnostic] = field(default_factory=list)
    topological_order: list[str] = field(default_factory=list)


def validate_dependency_plan(
    plan: dict[str, Any] | AnalysisPlanV02,
    *,
    registry: Any,
    selected_tool_ids: list[str] | None = None,
) -> DependencyValidationResult:
    try:
        parsed = plan if isinstance(plan, AnalysisPlanV02) else AnalysisPlanV02.model_validate(plan)
    except Exception as exc:
        message = str(exc)
        code = _schema_diagnostic_code(message)
        return _failed(code, "plan", f"AnalysisPlan 0.2 schema/graph validation failed: {message}")
    actual_selected = sorted(step.toolId for step in parsed.steps)
    if selected_tool_ids is not None and actual_selected != sorted(selected_tool_ids):
        return _failed(DependencyDiagnosticCode.selected_tool_mismatch, "steps", "Plan tools do not match the exact L2 selected tool set.")
    try:
        matrix = build_artifact_compatibility_matrix(registry, selected_tool_ids=actual_selected)
    except Exception as exc:
        return _failed(DependencyDiagnosticCode.dependency_composition_not_allowed, "registry", f"Artifact-port compatibility could not be recomputed: {exc}")
    compatible = {
        (item.producerToolId, item.producerOutputPort, item.consumerToolId, item.consumerInputPort): item
        for item in matrix.pairs
        if item.compatible
    }
    steps = {item.stepId: item for item in parsed.steps}
    errors: list[DependencyDiagnostic] = []
    port_inventory = build_artifact_port_inventory(registry)
    bound_consumer_ports = {
        (binding.consumerStepId, binding.consumerInputPort)
        for binding in parsed.dependencyBindings
    }
    for step in parsed.steps:
        direct_artifacts = [ref for ref in step.inputRefs if ref.refType == "artifact"]
        seen_roles: set[str] = set()
        for ref in direct_artifacts:
            ports = port_inventory.get(step.toolId)
            port = next(
                (
                    item
                    for item in (ports.inputPorts if ports is not None else [])
                    if item.inputFieldRole == ref.fieldRole
                ),
                None,
            )
            if port is None:
                errors.append(
                    _diagnostic(
                        DependencyDiagnosticCode.input_port_not_declared,
                        "steps.inputRefs",
                        "Persisted Artifact input does not match a declared Tool input port.",
                    )
                )
                continue
            if port.identityPolicy.value != "EXACT_PROJECT_DATASET_ARTIFACT":
                errors.append(
                    _diagnostic(
                        DependencyDiagnosticCode.external_authority_rejected,
                        "steps.inputRefs",
                        "Tool input port does not permit a persisted cross-run Artifact.",
                    )
                )
            if ref.objectType is None or ref.objectType.value != port.inputObjectType:
                errors.append(
                    _diagnostic(
                        DependencyDiagnosticCode.resource_version_mismatch,
                        "steps.inputRefs.objectType",
                        "Persisted Artifact input object type does not match its Tool port.",
                    )
                )
            if port.portId in seen_roles or (step.stepId, port.portId) in bound_consumer_ports:
                errors.append(
                    _diagnostic(
                        DependencyDiagnosticCode.duplicate_consumer_port,
                        "steps.inputRefs",
                        "A Tool input port may be supplied only once.",
                    )
                )
            seen_roles.add(port.portId)
    for binding in parsed.dependencyBindings:
        expected_id = deterministic_binding_id(binding.model_dump(mode="json", exclude={"bindingId"}))
        if binding.bindingId != expected_id:
            errors.append(_diagnostic(DependencyDiagnosticCode.binding_identity_invalid, "bindingId", "Binding semantic identity is invalid.", binding.bindingId))
            continue
        producer = steps.get(binding.producerStepId)
        consumer = steps.get(binding.consumerStepId)
        if producer is None or consumer is None:
            errors.append(_diagnostic(DependencyDiagnosticCode.unknown_step, "dependencyBindings", "Binding references an unknown step.", binding.bindingId))
            continue
        pair = compatible.get((producer.toolId, binding.producerOutputPort, consumer.toolId, binding.consumerInputPort))
        if pair is None:
            errors.append(_diagnostic(DependencyDiagnosticCode.dependency_composition_not_allowed, "dependencyBindings", "Binding is absent from the exact compatible artifact-port matrix.", binding.bindingId))
            continue
        if (
            pair.artifactKind != binding.artifactKind
            or pair.artifactContractVersion != binding.artifactContractVersion
            or pair.mediaType != binding.mediaType
        ):
            errors.append(_diagnostic(DependencyDiagnosticCode.contract_version_mismatch, "dependencyBindings", "Binding contract does not equal the compatible port contract.", binding.bindingId))
    if parsed.graphHash != compute_dependency_graph_hash(parsed.dependencyBindings):
        errors.append(_diagnostic(DependencyDiagnosticCode.graph_identity_invalid, "graphHash", "Graph semantic identity is invalid."))
    try:
        order = topological_order(parsed.steps, parsed.dependencyBindings)
    except Exception as exc:
        errors.append(_diagnostic(DependencyDiagnosticCode.cycle_would_be_created, "dependencyBindings", str(exc)))
        order = []
    return DependencyValidationResult(ok=not errors, errors=errors, topological_order=order)


def _failed(code: DependencyDiagnosticCode, field_name: str, message: str) -> DependencyValidationResult:
    return DependencyValidationResult(ok=False, errors=[_diagnostic(code, field_name, message)])


def _schema_diagnostic_code(message: str) -> DependencyDiagnosticCode:
    normalized = message.casefold()
    if "graph hash" in normalized or "graphhash" in normalized:
        return DependencyDiagnosticCode.graph_identity_invalid
    if "cycle" in normalized:
        return DependencyDiagnosticCode.cycle_would_be_created
    if "unknown" in normalized and "step" in normalized:
        return DependencyDiagnosticCode.unknown_step
    if "input port may be bound only once" in normalized or "duplicate" in normalized:
        return DependencyDiagnosticCode.duplicate_binding
    if "binding cap" in normalized or "depth cap" in normalized or "at most 4" in normalized:
        return DependencyDiagnosticCode.graph_cap_exceeded
    return DependencyDiagnosticCode.dependency_composition_not_allowed


def _diagnostic(
    code: DependencyDiagnosticCode,
    field_name: str,
    message: str,
    binding_id: str | None = None,
) -> DependencyDiagnostic:
    return DependencyDiagnostic(code=code, field=field_name, message=message[:1024], bindingId=binding_id)


__all__ = ["DependencyValidationResult", "validate_dependency_plan"]
