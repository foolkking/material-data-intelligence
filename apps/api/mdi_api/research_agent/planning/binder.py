from __future__ import annotations

from typing import Any

from mdi_schemas import (
    AnalysisPlanV02,
    AnalysisPlanV03,
    AnalysisPlanV04,
    AnalysisStep,
    ArtifactType,
    ExpectedArtifact,
    InputRef,
    PlannerBindingSource,
)
from mdi_schemas.dependency_planning import DependencyBinding, compute_dependency_graph_hash, deterministic_binding_id
from mdi_schemas.multi_source_planning import SCIENTIFIC_OBJECT_EXECUTION_TYPES as _OBJECT_TYPE_TO_EXEC
from mdi_tool_registry import (
    build_tool_artifact_port_metadata,
    build_tool_planner_metadata,
    validate_dependency_plan,
)
from mdi_tool_registry.plan_validator import validate_plan
from mdi_tool_registry.project_tools import project_reference_inventory

from mdi_api.agent2_errors import CapabilityBindingFailed
from mdi_api.repositories import compute_plan_hash
from mdi_api.research_agent.capabilities.versions import version_satisfies
from mdi_api.research_agent.capabilities.schemas import CapabilityBindingKind, CapabilityPlan, CapabilityResolution
from mdi_api.research_agent.orchestration.schemas import ResearchTurnDecision
from mdi_api.research_agent.planning.parameter_authority import (
    resolved_parameter_provenance,
    tool_defaults,
)


_RESULT_TO_ARTIFACT = {
    "generation.ideal_crystal": ArtifactType.structure_json,
    "structure.summary": ArtifactType.structure_json,
    "structure.rdf": ArtifactType.table_json, "diffraction.xrd.theoretical": ArtifactType.table_json,
    "diffraction.xrd.comparison": ArtifactType.table_json, "ml.regression.evaluation": ArtifactType.table_json,
    "ml.uncertainty.evaluation": ArtifactType.table_json, "ml.classification.evaluation": ArtifactType.table_json,
    "structure.viewer_scene": ArtifactType.structure_json,
    "trajectory.viewer": ArtifactType.trajectory_json,
    "trajectory.viewer.summary": ArtifactType.trajectory_summary_json,
    "trajectory.viewer.report": ArtifactType.trajectory_report_json,
    "trajectory.viewer.manifest": ArtifactType.trajectory_manifest_json,
    "trajectory.msd": ArtifactType.table_json, "trajectory.diffusion": ArtifactType.table_json,
    "phonon.band": ArtifactType.phonon_band_json, "phonon.dos": ArtifactType.phonon_dos_json,
    "phonon.band_dos": ArtifactType.phonon_band_dos_json,
    "volumetric.field": ArtifactType.volumetric_field_json,
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
_MANDATORY_SUITE_KEY = "mandatory_capability_tool"
_SUITE_INPUT_FROM_TOOL_KEY = "input_from_tool"


class CapabilityBinder:
    def __init__(self, tool_registry: Any) -> None:
        self.tool_registry = tool_registry

    def bind(
        self,
        *,
        capability_plan: CapabilityPlan,
        resolution: CapabilityResolution,
        context: dict[str, Any],
        registry: Any,
        decision: ResearchTurnDecision | None = None,
    ) -> tuple[AnalysisPlanV02, str]:
        candidates = {f"cap_{index}": item for index, item in enumerate(sorted(resolution.candidates, key=lambda item: (item.planning_priority, item.capability_id, item.capability_version)), 1)}
        steps: list[AnalysisStep] = []
        expected: list[ExpectedArtifact] = []
        dep_bindings: list[DependencyBinding] = []
        step_to_tool: dict[str, tuple[Any, Any]] = {}
        suite_tool_steps: dict[tuple[str, str], str] = {}
        suite_dependencies: list[tuple[str, str]] = []
        source_keys_by_step: dict[str, list[str]] = {}
        source_contexts = context.get("source_contexts") or {}
        source_versions = context.get("source_versions") or {}
        multi_source_context = len(source_contexts) > 1
        for step in capability_plan.steps:
            candidate = candidates.get(step.capability_ref_key)
            if candidate is None:
                raise CapabilityBindingFailed(f"unknown capability ref: {step.capability_ref_key}", code="CAPABILITY_PLAN_UNKNOWN_REFERENCE")
            source_keys: list[str] = []
            for slot_name, values in step.input_bindings.items():
                for item in values:
                    if item.kind == CapabilityBindingKind.SOURCE_OBJECT and item.source_ref_key:
                        source_keys.append(item.source_ref_key)
                    elif item.kind == CapabilityBindingKind.PLANNED_OUTPUT:
                        source_keys.extend(source_keys_by_step.get(item.producer_step_id or "", []))
                    elif item.kind == CapabilityBindingKind.PREVIOUS_RESULT:
                        source_keys.extend(candidate.reusable_result_source_ref_keys.get(slot_name, {}).get(item.result_ref_key or "", []))
            source_keys_by_step[step.step_id] = list(dict.fromkeys(source_keys))
            step_datasets = {source_versions[key]["datasetId"] for key in source_keys if key in source_versions}
            step_context = {**context,
                "resource_facts": {key: value for key, value in (context.get("resource_facts") or {}).items() if key in source_keys},
                "object_refs": {key: value for key, value in (context.get("object_refs") or {}).items() if key in source_keys},
            }
            if len(step_datasets) == 1:
                step_context.update(source_contexts[next(iter(step_datasets))])
            elif multi_source_context:
                # A tool that combines multiple materials has no single
                # authoritative profile from which to infer columns or groups.
                step_context.update(profile=None, profile_id=None, dataset_id=None)
            manifest = registry.require(candidate.capability_id, candidate.capability_version)
            selected_bindings = self._select_bindings(manifest)
            if len(selected_bindings) > 1 and any(
                item.kind == CapabilityBindingKind.PLANNED_OUTPUT
                for values in step.input_bindings.values()
                for item in values
            ):
                raise CapabilityBindingFailed(
                    "mandatory Tool suites cannot consume an ambiguous planned output",
                    code="CAPABILITY_PLAN_PORT_MISMATCH",
                )
            for binding_index, binding in enumerate(selected_bindings, start=1):
                tool = self.tool_registry.get_tool_by_id(binding.tool_id)
                execution_step_id = (
                    step.step_id
                    if len(selected_bindings) == 1
                    else f"{step.step_id}_{binding_index}"
                )
                if len(selected_bindings) == 1:
                    step_to_tool[step.step_id] = (
                        tool,
                        build_tool_artifact_port_metadata(tool),
                    )
                else:
                    step_to_tool[execution_step_id] = (
                        tool,
                        build_tool_artifact_port_metadata(tool),
                    )
                    suite_tool_steps[(step.step_id, tool.toolId)] = execution_step_id
                    input_from_tool = binding.output_mapping.get(
                        _SUITE_INPUT_FROM_TOOL_KEY
                    )
                    if input_from_tool:
                        suite_dependencies.append(
                            (
                                f"{step.step_id}:{str(input_from_tool)}",
                                execution_step_id,
                            )
                        )
                input_refs: list[InputRef] = []
                # Profile-backed dataset adapters consume the exact persisted
                # DataProfile in addition to their source table/structure refs.
                if tool.toolId in _PROFILE_BACKED_DATA_TOOLS:
                    if multi_source_context and len(step_datasets) != 1:
                        raise CapabilityBindingFailed("this profile-backed Tool requires one exact source dataset per invocation", code="CAPABILITY_PROFILE_BINDING_MISSING")
                    input_refs.append(
                        InputRef(refType="profile", ref=f"profile:{step_context['profile_id']}" if multi_source_context else "profile", fieldRole="profile")
                    )
                for slot_name, slot_bindings in step.input_bindings.items():
                    for item in slot_bindings:
                        if item.kind == CapabilityBindingKind.SOURCE_OBJECT:
                            source_key = item.source_ref_key or ""
                            source_ref = (context.get("object_refs") or {}).get(
                                source_key
                            )
                            exact_ref = (
                                str(source_ref.version_id)
                                if source_ref is not None
                                else source_key
                            )
                            input_refs.append(
                                InputRef(
                                    refType="normalized_object",
                                    ref=exact_ref,
                                    fieldRole=slot_name,
                                    objectType=_OBJECT_TYPE_TO_EXEC.get(
                                        source_ref.object_type if source_ref is not None else next(
                                            slot
                                            for slot in manifest.input_slots
                                            if slot.name == slot_name
                                        ).accepted_object_types[0],
                                        "RawUnsupported",
                                    ),
                                )
                            )
                        elif item.kind == CapabilityBindingKind.PREVIOUS_RESULT:
                            result_ref = (
                                context.get("result_object_refs") or {}
                            ).get(item.result_ref_key or "")
                            slot = next(
                                slot
                                for slot in manifest.input_slots
                                if slot.name == slot_name
                            )
                            if result_ref is not None:
                                if result_ref.object_type not in slot.accepted_object_types:
                                    raise CapabilityBindingFailed(
                                        "previous Result output is incompatible with capability input",
                                        code="CAPABILITY_PLAN_PORT_MISMATCH",
                                    )
                                input_refs.append(
                                    InputRef(
                                        refType="normalized_object",
                                        ref=str(result_ref.version_id),
                                        fieldRole=slot_name,
                                        objectType=_OBJECT_TYPE_TO_EXEC.get(
                                            result_ref.object_type, "RawUnsupported"
                                        ),
                                    )
                                )
                                continue
                            result_artifacts = (
                                context.get("result_artifact_refs") or {}
                            ).get(item.result_ref_key or "", {})
                            result_artifact_metadata = (
                                context.get("result_artifact_metadata_refs") or {}
                            ).get(item.result_ref_key or "", {})
                            artifact_ids = sorted(
                                {
                                    artifact_id
                                    for result_type, values in result_artifacts.items()
                                    if result_type in slot.accepted_object_types
                                    for artifact_id in values
                                }
                            )
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
                            if port is None and len(ports.inputPorts) == 1:
                                port = ports.inputPorts[0]
                            if port is not None and result_artifact_metadata:
                                accepted_kinds = {
                                    kind.value for kind in port.acceptedArtifactKinds
                                }
                                filtered_artifact_ids = [
                                    artifact_id
                                    for artifact_id in artifact_ids
                                    if result_artifact_metadata.get(
                                        str(artifact_id), {}
                                    ).get("type")
                                    in accepted_kinds
                                ]
                                if filtered_artifact_ids:
                                    artifact_ids = sorted(filtered_artifact_ids)
                            if len(artifact_ids) != 1 or port is None:
                                raise CapabilityBindingFailed(
                                    "previous Result has no exact reusable output",
                                    code="CAPABILITY_PLAN_UNKNOWN_REFERENCE",
                                )
                            input_refs.append(
                                InputRef(
                                    refType="artifact",
                                    ref=artifact_ids[0],
                                    fieldRole=port.inputFieldRole,
                                    objectType=port.inputObjectType,
                                )
                            )
                artifact_outputs = [out.result_type for out in manifest.output_slots]
                execution_artifact_types = [
                    artifact_type.value for artifact_type in tool.artifactTypes
                ]
                if len(selected_bindings) == 1:
                    for out in manifest.output_slots:
                        expected.append(
                            ExpectedArtifact(
                                name=f"{execution_step_id}.{out.name}",
                                type=_RESULT_TO_ARTIFACT.get(
                                    out.result_type, ArtifactType.table_json
                                ),
                                fromStepId=execution_step_id,
                            )
                        )
                else:
                    for artifact_type in tool.artifactTypes:
                        expected.append(
                            ExpectedArtifact(
                                name=(
                                    f"{execution_step_id}."
                                    f"{artifact_type.value}"
                                ),
                                type=artifact_type,
                                fromStepId=execution_step_id,
                            )
                        )
                default_params = tool_defaults(tool)
                resource_params, resource_sources = self._resource_fact_parameters(
                    tool=tool,
                    step=step,
                    context=context,
                    source_ref_keys=source_keys_by_step[step.step_id],
                )
                profile_params, profile_sources = self._profile_parameters(
                    tool=tool,
                    context=step_context,
                )
                executable_params = {
                    **default_params,
                    **resource_params,
                    **profile_params,
                    **dict(step.parameters),
                }
                if (candidate.capability_id in {"structure.local_environment_crystalnn", "structure.local_environment_voronoi"}
                        and tool.toolId in {"structure.coordination_crystalnn", "structure.coordination_voronoinn"}):
                    # N1 records the bounded structure's neighbors; only its N2
                    # consumer accepts an explicit subset of sites to describe.
                    executable_params.pop("site_indices", None)
                parameter_sources: dict[str, tuple[str, str]] = {
                    key: (
                        "TOOL_DEFAULT",
                        f"tool:{tool.toolId}@{tool.version}:default:{key}",
                    )
                    for key in default_params
                }
                parameter_sources.update(resource_sources)
                parameter_sources.update(profile_sources)
                for key in step.parameters:
                    parameter_sources[key] = (
                        "AGENT_DERIVED" if decision is not None else "USER_EXPLICIT",
                        f"capability-plan:{step.step_id}:parameter:{key}",
                    )
                if decision is not None:
                    for requirement in decision.scientific_requirements:
                        if (
                            requirement.requirement_id
                            not in candidate.satisfies_requirement_ids
                        ):
                            continue
                        for key in requirement.constraints:
                            parameter = str(binding.parameter_mapping.get(key) or key)
                            parameter_sources[parameter] = (
                                "USER_EXPLICIT",
                                f"requirement:{requirement.requirement_id}:USER_EXPLICIT",
                            )
                if tool.toolId in {
                    "dataset.materials_explorer",
                    "dataset.composition_space",
                }:
                    allowed_params = set(
                        (tool.paramsSchema or {}).get("properties") or {}
                    )
                    executable_params = {
                        key: value
                        for key, value in executable_params.items()
                        if key in allowed_params
                        or key not in _DATASET_SEMANTIC_ONLY_CONSTRAINTS
                    }
                if tool.toolId == "viz.inline_xy":
                    raw_table = executable_params.get("data_text")
                    user_message = context.get("user_message")
                    if (not isinstance(raw_table, str) or not raw_table.strip() or not isinstance(user_message, str)
                            or raw_table.replace("\r\n", "\n") not in user_message.replace("\r\n", "\n")):
                        raise CapabilityBindingFailed("表格内容与本条消息不一致，请直接粘贴原始小表格。", code="INLINE_DATA_SOURCE_MISMATCH")
                parameter_provenance = [
                    resolved_parameter_provenance(
                        tool_id=tool.toolId,
                        tool_version=tool.version,
                        parameter=key,
                        value=value,
                        source_origin=parameter_sources.get(
                            key,
                            (
                                "SYSTEM_POLICY",
                                f"tool:{tool.toolId}@{tool.version}:policy:{key}",
                            ),
                        )[0],
                        source_identity=parameter_sources.get(
                            key,
                            (
                                "SYSTEM_POLICY",
                                f"tool:{tool.toolId}@{tool.version}:policy:{key}",
                            ),
                        )[1],
                    )
                    for key, value in sorted(executable_params.items())
                ]
                steps.append(
                    AnalysisStep(
                        stepId=execution_step_id,
                        toolId=tool.toolId,
                        purpose=manifest.display_name,
                        reason=manifest.scientific_purpose,
                        inputRefs=input_refs,
                        params=executable_params,
                        parameterProvenance=parameter_provenance,
                        output={
                            "resultTypes": artifact_outputs,
                            "artifactTypes": execution_artifact_types,
                            "capabilityId": candidate.capability_id,
                            "capabilityVersion": candidate.capability_version,
                            "capabilityPlanStepId": step.step_id,
                            "sourceObjectVersionIds": [
                                str(context["object_refs"][key].version_id)
                                for key in source_keys_by_step[step.step_id]
                                if key in (context.get("object_refs") or {})
                            ],
                            "mandatoryCoverage": len(selected_bindings) > 1,
                        },
                        constraints={},
                    )
                )
        for producer_ref, consumer_step_id in suite_dependencies:
            capability_step_id, producer_tool_id = producer_ref.split(":", 1)
            producer_step_id = suite_tool_steps.get(
                (capability_step_id, producer_tool_id)
            )
            if producer_step_id is None:
                raise CapabilityBindingFailed(
                    "mandatory Tool suite dependency producer is absent",
                    code="CAPABILITY_PLAN_PORT_MISMATCH",
                )
            producer_tool, producer_ports = step_to_tool[producer_step_id]
            consumer_tool, consumer_ports = step_to_tool[consumer_step_id]
            if len(producer_ports.outputPorts) != 1 or len(
                consumer_ports.inputPorts
            ) != 1:
                raise CapabilityBindingFailed(
                    "mandatory Tool suite dependency is not unambiguous",
                    code="CAPABILITY_PLAN_PORT_MISMATCH",
                )
            producer_port = producer_ports.outputPorts[0]
            consumer_port = consumer_ports.inputPorts[0]
            common_kind = next(
                (
                    kind
                    for kind in consumer_port.acceptedArtifactKinds
                    if kind == producer_port.artifactKind
                ),
                None,
            )
            common_version = next(
                (
                    version
                    for version in consumer_port.acceptedContractVersions
                    if version in producer_port.contractVersions
                ),
                None,
            )
            common_media = next(
                (
                    media
                    for media in consumer_port.mediaTypes
                    if media in producer_port.mediaTypes
                ),
                None,
            )
            if common_kind is None or common_version is None or common_media is None:
                raise CapabilityBindingFailed(
                    "mandatory Tool suite dependency ports are incompatible",
                    code="CAPABILITY_PLAN_PORT_MISMATCH",
                )
            semantic = {
                "producerStepId": producer_step_id,
                "producerOutputPort": producer_port.portId,
                "consumerStepId": consumer_step_id,
                "consumerInputPort": consumer_port.portId,
                "artifactKind": common_kind.value,
                "artifactContractVersion": common_version,
                "mediaType": common_media,
                "cardinality": producer_port.cardinality.value,
            }
            dep_bindings.append(
                DependencyBinding(
                    bindingId=deterministic_binding_id(semantic), **semantic
                )
            )
        for consumer in capability_plan.steps:
            planned_inputs = [
                (slot_name, item)
                for slot_name, bindings in consumer.input_bindings.items()
                for item in bindings
                if item.kind == CapabilityBindingKind.PLANNED_OUTPUT
            ]
            if not planned_inputs:
                continue
            if consumer.step_id not in step_to_tool:
                raise CapabilityBindingFailed(
                    "mandatory Tool suites cannot consume planned outputs",
                    code="CAPABILITY_PLAN_PORT_MISMATCH",
                )
            _consumer_tool, consumer_ports = step_to_tool[consumer.step_id]
            consumer_candidate = candidates[consumer.capability_ref_key]
            consumer_manifest = registry.require(consumer_candidate.capability_id, consumer_candidate.capability_version)
            for slot_name, item in planned_inputs:
                    producer = next(step for step in capability_plan.steps if step.step_id == item.producer_step_id)
                    if producer.step_id not in step_to_tool:
                        raise CapabilityBindingFailed(
                            "mandatory Tool suites cannot be dependency producers",
                            code="CAPABILITY_PLAN_PORT_MISMATCH",
                        )
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
        plan_fields = dict(goal=capability_plan.objective, datasetId=str(context.get("dataset_id") or "agent2_dataset"), profileId=str(context.get("profile_id") or "agent2_profile"), toolRegistryVersion=self.tool_registry.version, graphHash=graph_hash, assumptions=[], warnings=[], steps=steps, dependencyBindings=dep_bindings, expectedArtifacts=expected)
        if multi_source_context:
            used_versions = {value for item in steps for value in item.output.get("sourceObjectVersionIds", [])}
            inventory = {source["versionId"]: {**source, "objectType": _OBJECT_TYPE_TO_EXEC.get(source["objectType"], "RawUnsupported")}
                         for source in source_versions.values() if source["versionId"] in used_versions}
            used_datasets = sorted({item["datasetId"] for item in inventory.values()})
            if not used_datasets or set(inventory) != used_versions:
                raise CapabilityBindingFailed("exact source inventory is missing from the plan context")
            route = source_contexts[used_datasets[0]]
            plan_fields.update(datasetId=route["dataset_id"], profileId=route["profile_id"])
            if len(used_datasets) > 1:
                plan = AnalysisPlanV03.model_validate({
                    **plan_fields, "schemaVersion": "0.3",
                    "steps": [item.model_dump(mode="json") for item in steps],
                    "sourceContexts": [{"datasetId": key, "profileId": source_contexts[key]["profile_id"]} for key in used_datasets],
                    "sourceVersions": [inventory[key] for key in sorted(inventory)],
                })
            else:
                # Unused context does not make a single-dataset plan multi-source.
                for item in steps:
                    item.inputRefs = [ref.model_copy(update={"ref": "profile"}) if ref.refType == "profile" else ref for ref in item.inputRefs]
                plan = AnalysisPlanV02(**plan_fields)
        elif context.get("execution_scope") == "project":
            plan_fields.update(datasetId=None, profileId=None)
            plan = AnalysisPlanV04(**plan_fields, projectId=context["project_id"],
                                  referenceSources=project_reference_inventory(self.tool_registry.get_tool_by_id(step.toolId) for step in steps))
        else:
            plan = AnalysisPlanV02(**plan_fields)
        dependency_result = validate_dependency_plan(plan.model_dump(mode="json"), registry=self.tool_registry, selected_tool_ids=sorted(step.toolId for step in steps))
        if not dependency_result.ok:
            raise CapabilityBindingFailed("AnalysisPlan dependency validation failed: " + "; ".join(item.message for item in dependency_result.errors), code="ANALYSIS_PLAN_VALIDATION_FAILED")
        plan_result = validate_plan(plan.model_dump(mode="json"), registry=self.tool_registry)
        if not plan_result.ok:
            raise CapabilityBindingFailed("AnalysisPlan validation failed: " + "; ".join(item.message for item in plan_result.errors), code="ANALYSIS_PLAN_VALIDATION_FAILED")
        return plan, compute_plan_hash(plan)

    def _select_bindings(self, manifest: Any) -> list[Any]:
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
        mandatory = [
            item
            for item in candidates
            if item.output_mapping.get(_MANDATORY_SUITE_KEY) is True
        ]
        if mandatory:
            if len(mandatory) != len(candidates):
                raise CapabilityBindingFailed(
                    f"capability mixes mandatory and alternative Tool bindings: {manifest.capability_id}",
                    code="CAPABILITY_TOOL_BINDING_INVALID",
                )
            return sorted(
                mandatory,
                key=lambda item: (item.priority, item.tool_id, item.version_constraint),
            )
        return [
            sorted(
                candidates,
                key=lambda item: (item.priority, item.tool_id, item.version_constraint),
            )[0]
        ]

    @staticmethod
    def _resource_fact_parameters(
        *,
        tool: Any,
        step: Any,
        context: dict[str, Any],
        source_ref_keys: list[str],
    ) -> tuple[dict[str, Any], dict[str, tuple[str, str]]]:
        metadata = build_tool_planner_metadata(tool)
        bindings = [
            binding
            for binding in metadata.parameterBindings
            if binding.source is PlannerBindingSource.resource_fact
        ]
        if not bindings:
            return {}, {}

        ordered_ref_keys = list(dict.fromkeys(source_ref_keys))
        facts_by_ref = context.get("resource_facts") or {}
        resolved: dict[str, Any] = {}
        sources: dict[str, tuple[str, str]] = {}

        for binding in bindings:
            matches: list[tuple[str, dict[str, Any], str, Any]] = []
            for ref_key in ordered_ref_keys:
                record = facts_by_ref.get(ref_key)
                if not isinstance(record, dict):
                    continue
                object_type = str(record.get("object_type") or "")
                planner_object_type = _OBJECT_TYPE_TO_EXEC.get(object_type, object_type)
                if (
                    binding.objectTypes
                    and object_type not in binding.objectTypes
                    and planner_object_type not in binding.objectTypes
                ):
                    continue
                facts = record.get("facts") or {}
                for fact_key in binding.factKeys:
                    if fact_key in facts:
                        matches.append((ref_key, record, fact_key, facts[fact_key]))
                        break
            if not matches:
                if binding.required and binding.parameter not in step.parameters:
                    raise CapabilityBindingFailed(
                        f"required registered resource fact is unavailable for {binding.parameter}",
                        code="CAPABILITY_RESOURCE_FACT_MISSING",
                    )
                continue
            if binding.multiple:
                value: Any = [match[3] for match in matches]
                source_identity = ",".join(
                    CapabilityBinder._resource_fact_source_identity(record, fact_key)
                    for _ref_key, record, fact_key, _value in matches
                )
            else:
                if len(matches) != 1:
                    raise CapabilityBindingFailed(
                        f"registered resource fact is ambiguous for {binding.parameter}",
                        code="CAPABILITY_RESOURCE_FACT_AMBIGUOUS",
                    )
                _ref_key, record, fact_key, value = matches[0]
                source_identity = CapabilityBinder._resource_fact_source_identity(
                    record,
                    fact_key,
                )
            resolved[binding.parameter] = value
            sources[binding.parameter] = ("CONTEXT_RESOLVED", source_identity)
        return resolved, sources

    @staticmethod
    def _resource_fact_source_identity(record: dict[str, Any], fact_key: str) -> str:
        return (
            f"scientific-object:{record.get('object_id')}@"
            f"{record.get('version_id')}:fact:{fact_key}"
        )

    @staticmethod
    def _profile_parameters(
        *,
        tool: Any,
        context: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, tuple[str, str]]]:
        metadata = build_tool_planner_metadata(tool)
        bindings = [
            binding
            for binding in metadata.parameterBindings
            if binding.source is not PlannerBindingSource.resource_fact
        ]
        if not bindings:
            return {}, {}

        profile = context.get("profile")
        if hasattr(profile, "model_dump"):
            profile = profile.model_dump(mode="json")
        profile = profile if isinstance(profile, dict) else {}
        semantic_columns = [
            item
            for item in profile.get("semanticColumns") or []
            if isinstance(item, dict)
        ]
        semantic_groups = [
            item
            for item in profile.get("semanticGroups") or []
            if isinstance(item, dict)
        ]
        if len({str(item.get("objectId")) for item in semantic_columns}) > 1:
            # A profile can contain several tables. Resolve column/group
            # parameters only from the resource bound to this invocation.
            resource_ids = {str(item.get("resource_id") or item.get("object_id"))
                            for item in (context.get("resource_facts") or {}).values() if isinstance(item, dict)}
            semantic_columns = [item for item in semantic_columns if str(item.get("objectId")) in resource_ids]
            if not semantic_columns:
                raise CapabilityBindingFailed("profile columns cannot be bound to the exact step source", code="CAPABILITY_PROFILE_BINDING_MISSING")
            group_ids = {str(role.get("groupId")) for item in semantic_columns for role in item.get("roles") or []
                         if isinstance(role, dict) and role.get("groupId")}
            semantic_groups = [item for item in semantic_groups if item.get("groupId") in group_ids]
        resolved: dict[str, Any] = {}
        sources: dict[str, tuple[str, str]] = {}
        already_selected_columns: set[str] = set()

        def columns_for_roles(roles: list[str]) -> list[str]:
            ranked: list[tuple[int, str, str]] = []
            for column in semantic_columns:
                column_name = str(column.get("column") or "")
                object_id = str(column.get("objectId") or "")
                if not column_name:
                    continue
                role_names = {
                    str(role.get("role"))
                    for role in column.get("roles") or []
                    if isinstance(role, dict) and role.get("role")
                }
                matched = next(
                    (index for index, role in enumerate(roles) if role in role_names),
                    None,
                )
                if matched is not None:
                    ranked.append((matched, object_id, column_name))
            resolved_columns = list(
                dict.fromkeys(
                    column_name
                    for _rank, _object_id, column_name in sorted(ranked)
                )
            )
            if resolved_columns or "material_property" not in roles:
                return resolved_columns
            # Material Profile 2.0 intentionally does not assert that every
            # numeric column is a scientific material property.  Generic
            # table visualization may still select bounded numeric columns,
            # while excluding identifiers and explicitly semantic targets.
            numeric_tokens = (
                "int",
                "float",
                "double",
                "decimal",
                "number",
            )
            fallback = []
            for column in semantic_columns:
                dtype = str(column.get("dtype") or "").casefold()
                role_names = {
                    str(role.get("role"))
                    for role in column.get("roles") or []
                    if isinstance(role, dict) and role.get("role")
                }
                if (
                    any(token in dtype for token in numeric_tokens)
                    and "sample_identity" not in role_names
                ):
                    fallback.append(str(column.get("column") or ""))
            return sorted({item for item in fallback if item})

        for binding in bindings:
            value: Any | None = None
            identity: str | None = None
            if binding.source in {
                PlannerBindingSource.target_column,
                PlannerBindingSource.semantic_columns,
            }:
                columns = columns_for_roles(list(binding.targetRoles))
                if binding.source is PlannerBindingSource.target_column:
                    value = next(
                        (
                            column
                            for column in columns
                            if column not in already_selected_columns
                        ),
                        columns[0] if columns else None,
                    )
                    if value is not None:
                        already_selected_columns.add(str(value))
                elif columns:
                    value = columns if binding.multiple else columns[0]
                if value is not None:
                    identity = (
                        f"profile:{context.get('profile_id')}:semantic-columns:"
                        f"{','.join(value if isinstance(value, list) else [str(value)])}"
                    )
            elif binding.source is PlannerBindingSource.target_group_ids:
                expected_kind = {
                    "ml.regression_evaluation": "regression",
                    "ml.uncertainty_evaluation": "regression",
                    "ml.classification_evaluation": "classification",
                }.get(tool.toolId)
                groups = [
                    str(item.get("groupId"))
                    for item in semantic_groups
                    if item.get("groupId")
                    and item.get("status") == "COMPLETE"
                    and (
                        expected_kind is None
                        or item.get("kind") == expected_kind
                    )
                ]
                if groups:
                    value = groups if binding.multiple or binding.parameter == "groupIds" else groups[0]
                    identity = (
                        f"profile:{context.get('profile_id')}:semantic-groups:"
                        f"{','.join(groups)}"
                    )
            elif binding.source is PlannerBindingSource.profile_id:
                value = str(context.get("profile_id") or "") or None
                identity = f"profile:{value}" if value else None
            elif binding.source is PlannerBindingSource.resource_id:
                object_ids = sorted(
                    {
                        str(item.get("resource_id") or item.get("object_id"))
                        for item in (context.get("resource_facts") or {}).values()
                        if isinstance(item, dict)
                        and (item.get("resource_id") or item.get("object_id"))
                    }
                )
                if not object_ids:
                    object_ids = sorted(
                        {
                            str(
                                getattr(item, "object_id", None)
                                or (
                                    item.get("object_id")
                                    if isinstance(item, dict)
                                    else ""
                                )
                            )
                            for item in (context.get("object_refs") or {}).values()
                            if (
                                getattr(item, "object_id", None)
                                or (
                                    item.get("object_id")
                                    if isinstance(item, dict)
                                    else None
                                )
                            )
                        }
                    )
                if object_ids:
                    value = object_ids if binding.multiple else object_ids[0]
                    identity = f"scientific-object:{','.join(object_ids)}"
            elif binding.source is PlannerBindingSource.literal:
                value = binding.literalValue
                identity = f"planner-metadata:{tool.toolId}:literal:{binding.parameter}"

            if value is None:
                if binding.required:
                    raise CapabilityBindingFailed(
                        (
                            "required registered profile binding is unavailable "
                            f"for {tool.toolId}:{binding.parameter}"
                        ),
                        code="CAPABILITY_PROFILE_BINDING_MISSING",
                    )
                continue
            resolved[binding.parameter] = value
            sources[binding.parameter] = (
                "CONTEXT_RESOLVED",
                identity or f"profile:{context.get('profile_id')}",
            )
        return resolved, sources
