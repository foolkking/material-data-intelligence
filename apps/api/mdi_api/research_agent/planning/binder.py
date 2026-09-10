from __future__ import annotations

from typing import Any

from mdi_schemas import AnalysisPlanV02, AnalysisStep, ArtifactType, ExpectedArtifact, InputRef
from mdi_schemas.dependency_planning import DependencyBinding, compute_dependency_graph_hash, deterministic_binding_id
from mdi_tool_registry import build_tool_artifact_port_metadata, validate_dependency_plan
from mdi_tool_registry.plan_validator import validate_plan

from mdi_api.agent2_errors import CapabilityBindingFailed
from mdi_api.repositories import compute_plan_hash
from mdi_api.research_agent.capabilities.versions import version_satisfies
from mdi_api.research_agent.capabilities.schemas import CapabilityBindingKind, CapabilityPlan, CapabilityResolution


_OBJECT_TYPE_TO_EXEC = {
    "structure.crystal": "Structure", "trajectory.atomic": "Trajectory", "materials.dataset": "DataFrame",
    "phonon.band_structure": "PhononBand", "phonon.dos": "PhononDos", "diffraction.xrd.experimental": "DataFrame",
    "diffraction.xrd.theoretical": "Structure",
}
_RESULT_TO_ARTIFACT = {
    "structure.rdf": ArtifactType.table_json, "diffraction.xrd.theoretical": ArtifactType.table_json,
    "diffraction.xrd.comparison": ArtifactType.table_json, "ml.regression.evaluation": ArtifactType.table_json,
    "trajectory.msd": ArtifactType.table_json, "trajectory.diffusion": ArtifactType.table_json,
    "phonon.band": ArtifactType.phonon_band_json, "phonon.dos": ArtifactType.phonon_dos_json,
    "phonon.band_dos": ArtifactType.phonon_band_dos_json,
}

# Dataset requirement constraints such as a selected sample/property are
# semantic planning context, not executable adapter arguments.  They remain
# persisted in the immutable decision/context snapshot and are consumed by
# the bounded result/interpretation path.  Only these known keys may be
# omitted before strict Tool paramsSchema validation; arbitrary unknown keys
# remain fail-closed below.
_DATASET_SEMANTIC_ONLY_CONSTRAINTS = frozenset({"sample", "property"})
_PROFILE_BACKED_DATA_TOOLS = frozenset({
    "dataset.materials_explorer",
    "dataset.composition_space",
    "ml.regression_evaluation",
    "ml.uncertainty_evaluation",
    "ml.classification_evaluation",
})


class CapabilityBinder:
    def __init__(self, tool_registry: Any) -> None:
        self.tool_registry = tool_registry

    def bind(self, *, capability_plan: CapabilityPlan, resolution: CapabilityResolution, context: dict[str, Any], registry: Any) -> tuple[AnalysisPlanV02, str]:
        candidates = {f"cap_{index}": item for index, item in enumerate(sorted(resolution.candidates, key=lambda item: (item.planning_priority, item.capability_id, item.capability_version)), 1)}
        steps: list[AnalysisStep] = []
        expected: list[ExpectedArtifact] = []
        dep_bindings: list[DependencyBinding] = []
        step_to_tool: dict[str, tuple[Any, Any]] = {}
        for step in capability_plan.steps:
            candidate = candidates.get(step.capability_ref_key)
            if candidate is None:
                raise CapabilityBindingFailed(f"unknown capability ref: {step.capability_ref_key}", code="CAPABILITY_PLAN_UNKNOWN_REFERENCE")
            manifest = registry.require(candidate.capability_id, candidate.capability_version)
            binding = self._select_binding(manifest)
            tool = self.tool_registry.get_tool_by_id(binding.tool_id)
            step_to_tool[step.step_id] = (tool, build_tool_artifact_port_metadata(tool))
            input_refs: list[InputRef] = []
            # Profile-backed dataset adapters consume the exact persisted
            # DataProfile in addition to their source table/structure refs.
            # Keep this binding explicit so the worker cannot silently run
            # against an unprofiled or latest-inferred dataset.
            if tool.toolId in _PROFILE_BACKED_DATA_TOOLS:
                input_refs.append(InputRef(refType="profile", ref="profile", fieldRole="profile"))
            for slot_name, bindings in step.input_bindings.items():
                for item in bindings:
                    if item.kind == CapabilityBindingKind.SOURCE_OBJECT:
                        source_key = item.source_ref_key or ""
                        source_ref = (context.get("object_refs") or {}).get(source_key)
                        exact_ref = str(source_ref.version_id) if source_ref is not None else source_key
                        input_refs.append(InputRef(refType="normalized_object", ref=exact_ref, fieldRole=slot_name, objectType=_OBJECT_TYPE_TO_EXEC.get(next(slot for slot in manifest.input_slots if slot.name == slot_name).accepted_object_types[0], "RawUnsupported")))
                    elif item.kind == CapabilityBindingKind.PREVIOUS_RESULT:
                        result_ref = (context.get("result_object_refs") or {}).get(item.result_ref_key or "")
                        slot = next(slot for slot in manifest.input_slots if slot.name == slot_name)
                        if result_ref is not None:
                            if result_ref.object_type not in slot.accepted_object_types:
                                raise CapabilityBindingFailed("previous Result output is incompatible with capability input", code="CAPABILITY_PLAN_PORT_MISMATCH")
                            input_refs.append(InputRef(
                                refType="normalized_object",
                                ref=str(result_ref.version_id),
                                fieldRole=slot_name,
                                objectType=_OBJECT_TYPE_TO_EXEC.get(result_ref.object_type, "RawUnsupported"),
                            ))
                            continue
                        result_artifacts = (
                            context.get("result_artifact_refs") or {}
                        ).get(item.result_ref_key or "", {})
                        artifact_ids = sorted({
                            artifact_id
                            for result_type, values in result_artifacts.items()
                            if result_type in slot.accepted_object_types
                            for artifact_id in values
                        })
                        ports = build_tool_artifact_port_metadata(tool)
                        port = next(
                            (
                                value
                                for value in ports.inputPorts
                                if value.portId == slot_name
                                or value.inputFieldRole == f"{slot_name}_artifact"
                            ),
                            None,
                        )
                        if len(artifact_ids) != 1 or port is None:
                            raise CapabilityBindingFailed(
                                "previous Result has no exact reusable output",
                                code="CAPABILITY_PLAN_UNKNOWN_REFERENCE",
                            )
                        input_refs.append(InputRef(
                            refType="artifact",
                            ref=artifact_ids[0],
                            fieldRole=port.inputFieldRole,
                            objectType=port.inputObjectType,
                        ))
            artifact_outputs = [out.result_type for out in manifest.output_slots]
            for out in manifest.output_slots:
                expected.append(ExpectedArtifact(name=f"{step.step_id}.{out.name}", type=_RESULT_TO_ARTIFACT.get(out.result_type, ArtifactType.table_json), fromStepId=step.step_id))
            # Requirement constraints are normally mapped to adapter params,
            # but Dataset semantic selectors are not part of the
            # materials_explorer/composition_space executable schema.  Keep
            # them in the authoritative requirement/context records and
            # remove only this explicit, bounded set before plan validation.
            executable_params = dict(step.parameters)
            if tool.toolId in {"dataset.materials_explorer", "dataset.composition_space"}:
                allowed_params = set((tool.paramsSchema or {}).get("properties") or {})
                executable_params = {
                    key: value
                    for key, value in executable_params.items()
                    if key in allowed_params
                    or key not in _DATASET_SEMANTIC_ONLY_CONSTRAINTS
                }
            steps.append(AnalysisStep(
                stepId=step.step_id,
                toolId=tool.toolId,
                purpose=manifest.display_name,
                reason=manifest.scientific_purpose,
                inputRefs=input_refs,
                params=executable_params,
                output={"resultTypes": artifact_outputs},
                constraints={},
            ))
        for consumer in capability_plan.steps:
            _consumer_tool, consumer_ports = step_to_tool[consumer.step_id]
            consumer_candidate = candidates[consumer.capability_ref_key]
            consumer_manifest = registry.require(consumer_candidate.capability_id, consumer_candidate.capability_version)
            for slot_name, bindings in consumer.input_bindings.items():
                for item in bindings:
                    if item.kind != CapabilityBindingKind.PLANNED_OUTPUT:
                        continue
                    producer = next(step for step in capability_plan.steps if step.step_id == item.producer_step_id)
                    producer_tool, producer_ports = step_to_tool[producer.step_id]
                    producer_manifest = registry.require(candidates[producer.capability_ref_key].capability_id, candidates[producer.capability_ref_key].capability_version)
                    producer_slot_index = next((index for index, output in enumerate(producer_manifest.output_slots) if output.name == item.producer_output_slot), 0)
                    producer_port = producer_ports.outputPorts[producer_slot_index] if producer_slot_index < len(producer_ports.outputPorts) else None
                    consumer_slot_index = 0 if len(consumer_ports.inputPorts) == 1 else next((index for index, input_slot in enumerate(consumer_manifest.input_slots) if input_slot.name == slot_name), 0)
                    consumer_port = consumer_ports.inputPorts[consumer_slot_index] if consumer_slot_index < len(consumer_ports.inputPorts) else None
                    if producer_port is None or consumer_port is None:
                        raise CapabilityBindingFailed("missing dependency port metadata", code="CAPABILITY_PLAN_PORT_MISMATCH")
                    common_kind = next((kind for kind in consumer_port.acceptedArtifactKinds if kind == producer_port.artifactKind), None)
                    common_version = next((version for version in consumer_port.acceptedContractVersions if version in producer_port.contractVersions), None)
                    common_media = next((media for media in consumer_port.mediaTypes if media in producer_port.mediaTypes), None)
                    if common_kind is None or common_version is None or common_media is None:
                        raise CapabilityBindingFailed("incompatible producer/consumer artifact ports", code="CAPABILITY_PLAN_PORT_MISMATCH")
                    semantic = {"producerStepId": producer.step_id, "producerOutputPort": producer_port.portId, "consumerStepId": consumer.step_id, "consumerInputPort": consumer_port.portId, "artifactKind": common_kind.value, "artifactContractVersion": common_version, "mediaType": common_media, "cardinality": producer_port.cardinality.value}
                    dep_bindings.append(DependencyBinding(bindingId=deterministic_binding_id(semantic), **semantic))
        graph_hash = compute_dependency_graph_hash(dep_bindings)
        plan = AnalysisPlanV02(goal=capability_plan.objective, datasetId=str(context.get("dataset_id") or "agent2_dataset"), profileId=str(context.get("profile_id") or "agent2_profile"), toolRegistryVersion=self.tool_registry.version, graphHash=graph_hash, assumptions=[], warnings=[], steps=steps, dependencyBindings=dep_bindings, expectedArtifacts=expected)
        dependency_result = validate_dependency_plan(plan.model_dump(mode="json"), registry=self.tool_registry, selected_tool_ids=sorted({step.toolId for step in steps}))
        if not dependency_result.ok:
            raise CapabilityBindingFailed("AnalysisPlan dependency validation failed", code="ANALYSIS_PLAN_VALIDATION_FAILED")
        plan_result = validate_plan(plan.model_dump(mode="json"), registry=self.tool_registry)
        if not plan_result.ok:
            raise CapabilityBindingFailed("AnalysisPlan validation failed: " + "; ".join(item.message for item in plan_result.errors), code="ANALYSIS_PLAN_VALIDATION_FAILED")
        return plan, compute_plan_hash(plan)

    def _select_binding(self, manifest: Any) -> Any:
        if not manifest.tool_bindings:
            raise CapabilityBindingFailed(f"capability has no executable binding: {manifest.capability_id}", code="CAPABILITY_TOOL_NOT_FOUND")
        candidates = []
        for binding in manifest.tool_bindings:
            try:
                tool = self.tool_registry.get_tool_by_id(binding.tool_id)
            except KeyError:
                continue
            if not binding.conditions and version_satisfies(tool.version, binding.version_constraint):
                candidates.append(binding)
        if not candidates:
            raise CapabilityBindingFailed(f"no Tool version satisfies capability binding: {manifest.capability_id}", code="CAPABILITY_TOOL_VERSION_MISMATCH")
        return sorted(candidates, key=lambda item: (item.priority, item.tool_id, item.version_constraint))[0]
