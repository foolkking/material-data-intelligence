from __future__ import annotations

from typing import Any

from mdi_api.agent2_errors import CapabilityResolutionFailed
from mdi_api.research_agent.capabilities.fingerprint import capability_registry_fingerprint
from mdi_api.research_agent.capabilities.preconditions import CapabilityPreconditionRegistry
from mdi_api.research_agent.capabilities.schemas import CapabilityCandidate, CapabilityEligibility, CapabilityResolution
from mdi_api.research_agent.orchestration.schemas import ResearchTurnDecision
from mdi_api.research_agent.schemas import CapabilitySurfaceSupport
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.research_agent.capabilities.versions import version_satisfies
from mdi_tool_registry import build_tool_artifact_port_metadata


RESOLVER_VERSION = "agent2.capability-resolver/1.0"


class CapabilityResolutionService:
    def __init__(self, capability_registry: Any, requirement_registry: Any, tool_registry: Any, preconditions: CapabilityPreconditionRegistry | None = None) -> None:
        self.capability_registry = capability_registry
        self.requirement_registry = requirement_registry
        self.tool_registry = tool_registry
        self.preconditions = preconditions

    def resolve(
        self,
        *,
        turn: dict[str, Any],
        decision: ResearchTurnDecision,
        context_snapshot: dict[str, Any],
        candidate_refs: dict[str, ScientificObjectRef] | None = None,
        reusable_results: dict[str, dict[str, Any]] | None = None,
    ) -> CapabilityResolution:
        requirements = self._requirements(
            decision,
            candidate_refs or self._snapshot_refs(context_snapshot),
            turn["id"],
            turn["project_id"],
        )
        all_refs = candidate_refs or self._snapshot_refs(context_snapshot)
        key_by_version = {str(ref.version_id): key for key, ref in all_refs.items()}
        registry_fp = capability_registry_fingerprint(self.capability_registry, self.tool_registry)
        active_manifests = {
            f"{manifest.capability_id}@{manifest.version}": manifest
            for manifest in self.capability_registry.list_active()
        }

        def possible_producers(manifest: Any, slot: Any) -> list[str]:
            producer_ids = []
            for producer in self.capability_registry.list_active():
                if producer.capability_id == manifest.capability_id:
                    continue
                if any(
                    (out.scientific_object_type in slot.accepted_object_types)
                    or (out.result_type in slot.accepted_object_types)
                    for out in producer.output_slots
                ):
                    producer_ids.append(f"{producer.capability_id}@{producer.version}")
            return sorted(producer_ids)

        def artifact_required_slots(manifest: Any) -> set[str]:
            if manifest.artifact_port_support != CapabilitySurfaceSupport.REQUIRED:
                return set()
            tool = None
            for binding in manifest.tool_bindings:
                try:
                    candidate_tool = self.tool_registry.get_tool_by_id(binding.tool_id)
                except KeyError:
                    continue
                if not binding.conditions and version_satisfies(
                    candidate_tool.version, binding.version_constraint
                ):
                    tool = candidate_tool
                    break
            if tool is None:
                return set()
            ports = list(build_tool_artifact_port_metadata(tool).inputPorts)
            if not ports:
                return set()

            required: set[str] = set()
            for slot in manifest.input_slots:
                aliases = {
                    slot.name,
                    f"{slot.name}_artifact",
                    f"{slot.name}-artifact",
                }
                if any(
                    port.portId in aliases or port.inputFieldRole in aliases
                    for port in ports
                ):
                    required.add(slot.name)

            # Some established Tools use a domain-specific artifact port name
            # (for example ``theoretical-xrd``) while the capability slot is
            # simply ``theoretical``.  A single registered input port can be
            # mapped only when exactly one capability slot has a registered
            # producer.  This keeps direct source-only slots such as
            # experimental XRD bound to their source object.
            if len(ports) == 1 and not required:
                produced_slots = [
                    slot.name
                    for slot in manifest.input_slots
                    if possible_producers(manifest, slot)
                ]
                if len(produced_slots) == 1:
                    required.add(produced_slots[0])
            return required

        def build_candidate(
            manifest: Any,
            matched: list[dict[str, Any]],
        ) -> CapabilityCandidate:
            bound: dict[str, list[ScientificObjectRef]] = {}
            result_bindings: dict[str, list[str]] = {}
            missing: list[str] = []
            reasons: list[str] = []
            required_artifact_slots = artifact_required_slots(manifest)
            for slot in manifest.input_slots:
                refs = [ref for item in requirements for ref in item["refs"] if ref.object_type in slot.accepted_object_types]
                dedup = {(str(ref.object_id), str(ref.version_id)): ref for ref in refs}
                refs = list(dedup.values())[: slot.max_count or len(dedup)]
                reusable_keys = []
                if not refs or slot.name in required_artifact_slots:
                    for result_key, result in sorted((reusable_results or {}).items()):
                        if not result.get("usable"):
                            continue
                        output_refs = result.get("output_object_refs") or []
                        result_types = set(result.get("result_types") or [])
                        if (
                            any(
                                ref.object_type in slot.accepted_object_types
                                for ref in output_refs
                            )
                            or bool(result_types.intersection(slot.accepted_object_types))
                        ):
                            reusable_keys.append(result_key)
                if reusable_keys:
                    result_bindings[slot.name] = reusable_keys
                elif (
                    slot.name in required_artifact_slots
                    or len(refs) < slot.min_count
                    or (slot.required and not refs)
                ):
                    missing.append(slot.name)
                    reasons.append(f"MISSING_INPUT:{slot.name}")
                else:
                    bound[slot.name] = refs
            eligibility = CapabilityEligibility.ELIGIBLE
            producers: dict[str, list[str]] = {}
            if missing:
                for slot_name in missing:
                    slot = next(slot for slot in manifest.input_slots if slot.name == slot_name)
                    producer_ids = possible_producers(manifest, slot)
                    if producer_ids:
                        producers[slot_name] = producer_ids
                    else:
                        reasons.append(f"NO_PRODUCER:{slot_name}")
                eligibility = CapabilityEligibility.CONDITIONAL if len(producers) == len(missing) else CapabilityEligibility.INELIGIBLE
            if self.preconditions:
                for precondition in manifest.preconditions:
                    evaluator = self.preconditions.require(precondition.predicate_id)
                    evaluation = evaluator.evaluate(manifest=manifest, precondition=precondition, bindings=bound, context=context_snapshot)
                    if not evaluation.passed:
                        reasons.append(evaluation.reason_code)
                        if precondition.required:
                            eligibility = CapabilityEligibility.INELIGIBLE
            executable = False
            for binding in manifest.tool_bindings:
                try:
                    tool = self.tool_registry.get_tool_by_id(binding.tool_id)
                except KeyError:
                    continue
                if not binding.conditions and version_satisfies(tool.version, binding.version_constraint):
                    executable = True
                    break
            if not executable:
                eligibility = CapabilityEligibility.INELIGIBLE
                reasons.append("TOOL_VERSION_UNAVAILABLE")
            return CapabilityCandidate(
                capability_id=manifest.capability_id,
                capability_version=manifest.version,
                eligibility=eligibility,
                satisfies_requirement_ids=sorted({item["requirement_id"] for item in matched}),
                bound_source_inputs=bound,
                bound_source_ref_keys={slot: [key_by_version[str(ref.version_id)] for ref in refs] for slot, refs in bound.items()},
                reusable_result_bindings=result_bindings,
                missing_input_slots=missing,
                possible_producers=producers,
                reason_codes=sorted(set(reasons)),
                limitations=list(manifest.limitations),
                planning_priority=manifest.planning_priority,
            )

        candidates: list[CapabilityCandidate] = []
        candidate_refs: set[str] = set()
        for manifest_ref, manifest in active_manifests.items():
            matched = [
                item
                for item in requirements
                if item["requirement_id"] in manifest.satisfies_requirements
            ]
            if not matched:
                continue
            candidates.append(build_candidate(manifest, matched))
            candidate_refs.add(manifest_ref)

        # Resolution must expose the complete bounded producer closure, not
        # only capabilities that directly satisfy a user requirement. A
        # clarification continuation can legitimately narrow the requirement
        # set to a derived capability (for example diffusion) while retaining
        # the original trajectory source. The derived capability still needs
        # its registered producer (MSD) in the same validated plan.
        pending_producer_refs = sorted({
            producer_ref
            for candidate in candidates
            for producer_refs in candidate.possible_producers.values()
            for producer_ref in producer_refs
        })
        while pending_producer_refs:
            producer_ref = pending_producer_refs.pop(0)
            if producer_ref in candidate_refs:
                continue
            manifest = active_manifests.get(producer_ref)
            if manifest is None:
                continue
            matched = [
                item
                for item in requirements
                if item["requirement_id"] in manifest.satisfies_requirements
            ]
            producer = build_candidate(manifest, matched)
            candidates.append(producer)
            candidate_refs.add(producer_ref)
            pending_producer_refs.extend(
                sorted({
                    nested_ref
                    for producer_refs in producer.possible_producers.values()
                    for nested_ref in producer_refs
                    if nested_ref not in candidate_refs
                })
            )
        required_ids = [item.requirement_id for item in decision.scientific_requirements if item.criticality.value == "REQUIRED"]
        optional_ids = [item.requirement_id for item in decision.scientific_requirements if item.criticality.value != "REQUIRED"]
        covered = {req for candidate in candidates if candidate.eligibility in {CapabilityEligibility.ELIGIBLE, CapabilityEligibility.CONDITIONAL} for req in candidate.satisfies_requirement_ids}
        return CapabilityResolution(
            research_turn_id=turn["id"], objective=decision.research_objective or "Scientific analysis",
            requirement_ids=[item.requirement_id for item in decision.scientific_requirements], candidates=sorted(candidates, key=lambda item: (item.planning_priority, item.capability_id, item.capability_version)),
            unsatisfied_required_requirement_ids=sorted(set(required_ids) - covered), optional_requirement_ids_not_covered=sorted(set(optional_ids) - covered), registry_fingerprint=registry_fp, resolver_version=RESOLVER_VERSION,
        )

    def _requirements(
        self,
        decision: ResearchTurnDecision,
        refs: dict[str, ScientificObjectRef],
        turn_id: Any,
        project_id: str,
    ) -> list[dict[str, Any]]:
        result = []
        for proposed in decision.scientific_requirements:
            missing = [key for key in proposed.subject_ref_keys if key not in refs]
            if missing:
                raise CapabilityResolutionFailed(f"Unknown subject reference(s): {', '.join(missing)}")
            manifest = self.requirement_registry.require(proposed.requirement_id)
            selected = [refs[key] for key in proposed.subject_ref_keys]
            if any(ref.project_id != project_id for ref in selected):
                raise CapabilityResolutionFailed(
                    f"Requirement source exceeds ResearchTurn project scope: {turn_id}"
                )
            if manifest.accepted_object_types and any(ref.object_type not in manifest.accepted_object_types for ref in selected):
                continue
            result.append({"requirement_id": proposed.requirement_id, "criticality": proposed.criticality.value, "refs": selected, "constraints": proposed.constraints})
        return result

    @staticmethod
    def _snapshot_refs(snapshot: dict[str, Any]) -> dict[str, ScientificObjectRef]:
        raw = list(snapshot.get("selection_refs_json") or []) + list(snapshot.get("active_scope_refs_json") or [])
        result = {}
        for raw_ref in raw:
            ref = ScientificObjectRef.model_validate(raw_ref)
            key = f"obj_{len(result) + 1}"
            result.setdefault(key, ref)
        return result
