from __future__ import annotations

from typing import Any

from mdi_api.agent2_errors import CapabilityPlanInvalid
from mdi_api.research_agent.capabilities.schemas import CapabilityBindingKind, CapabilityEligibility, CapabilityPlan, CapabilityResolution
from mdi_api.research_agent.orchestration.schemas import ResearchTurnDecision


class CapabilityPlanValidator:
    def validate(self, *, plan: CapabilityPlan, resolution: CapabilityResolution, decision: ResearchTurnDecision, context: dict[str, Any], registry: Any) -> CapabilityPlan:
        candidate_by_key = {f"cap_{index}": item for index, item in enumerate(sorted(resolution.candidates, key=lambda item: (item.planning_priority, item.capability_id, item.capability_version)), 1)}
        used_requirements: set[str] = set()
        step_ids = {step.step_id for step in plan.steps}
        if len(step_ids) != len(plan.steps):
            raise CapabilityPlanInvalid("duplicate plan step", code="CAPABILITY_PLAN_INVALID")
        edges = 0
        raw_refs = [*(context.get("selection_refs_json") or []), *(context.get("active_scope_refs_json") or [])]
        source_refs = {f"obj_{index}": item for index, item in enumerate(raw_refs, 1)}
        for step in plan.steps:
            candidate = candidate_by_key.get(step.capability_ref_key)
            if candidate is None or candidate.eligibility not in {CapabilityEligibility.ELIGIBLE, CapabilityEligibility.CONDITIONAL}:
                raise CapabilityPlanInvalid("unknown or ineligible capability", code="CAPABILITY_PLAN_UNKNOWN_REFERENCE")
            manifest = registry.require(candidate.capability_id, candidate.capability_version)
            used_requirements.update(step.satisfies_requirement_ids)
            if not set(step.satisfies_requirement_ids).issubset(set(candidate.satisfies_requirement_ids)):
                raise CapabilityPlanInvalid("step requirement membership mismatch")
            expected_outputs = {
                (item.name, item.result_type, item.scientific_object_type)
                for item in manifest.output_slots
            }
            actual_outputs = {
                (item.slot_name, item.result_type, item.scientific_object_type)
                for item in step.expected_outputs
            }
            if actual_outputs != expected_outputs:
                raise CapabilityPlanInvalid(
                    f"capability output contract mismatch for {step.capability_ref_key}: "
                    f"expected={sorted(expected_outputs, key=str)!r}; actual={sorted(actual_outputs, key=str)!r}",
                    code="CAPABILITY_PLAN_PORT_MISMATCH",
                )
            authorized_parameters: dict[str, Any] = {}
            parameter_mapping = (
                manifest.tool_bindings[0].parameter_mapping
                if manifest.tool_bindings
                else {}
            )
            for requirement in decision.scientific_requirements:
                if requirement.requirement_id not in candidate.satisfies_requirement_ids:
                    continue
                for key, value in requirement.constraints.items():
                    authorized_parameters[str(parameter_mapping.get(key) or key)] = value
            if step.parameters != authorized_parameters:
                raise CapabilityPlanInvalid(
                    "capability parameters must exactly match authorized scientific constraints; "
                    "Tool defaults are resolved deterministically after validation",
                    code="CAPABILITY_PLAN_PARAMETER_AUTHORITY_INVALID",
                )
            for slot_name, bindings in step.input_bindings.items():
                slot = next((item for item in manifest.input_slots if item.name == slot_name), None)
                if slot is None or not bindings:
                    raise CapabilityPlanInvalid("unknown or empty input slot", code="CAPABILITY_PLAN_PORT_MISMATCH")
                for binding in bindings:
                    if binding.kind == CapabilityBindingKind.SOURCE_OBJECT:
                        raw_ref = source_refs.get(binding.source_ref_key or "")
                        if raw_ref is None or raw_ref.get("object_type") not in slot.accepted_object_types:
                            raise CapabilityPlanInvalid("unknown or incompatible source reference", code="CAPABILITY_PLAN_UNKNOWN_REFERENCE")
                    if binding.kind == CapabilityBindingKind.PLANNED_OUTPUT:
                        edges += 1
                        if binding.producer_step_id not in step_ids or binding.producer_step_id == step.step_id:
                            raise CapabilityPlanInvalid("invalid planned output dependency", code="CAPABILITY_PLAN_CYCLE")
                        producer = next(item for item in plan.steps if item.step_id == binding.producer_step_id)
                        if plan.steps.index(producer) >= plan.steps.index(step):
                            raise CapabilityPlanInvalid("producer must precede consumer", code="CAPABILITY_PLAN_CYCLE")
                        producer_candidate = candidate_by_key[producer.capability_ref_key]
                        output = next((item for item in registry.require(producer_candidate.capability_id, producer_candidate.capability_version).output_slots if item.name == binding.producer_output_slot), None)
                        if output is None or not ((output.scientific_object_type in slot.accepted_object_types) or (output.result_type in slot.accepted_object_types)):
                            raise CapabilityPlanInvalid("producer/consumer port mismatch", code="CAPABILITY_PLAN_PORT_MISMATCH")
                    elif binding.kind == CapabilityBindingKind.PREVIOUS_RESULT:
                        if binding.result_ref_key not in candidate.reusable_result_bindings.get(slot_name, []):
                            raise CapabilityPlanInvalid("unknown or incompatible result binding", code="CAPABILITY_PLAN_UNKNOWN_REFERENCE")
            for slot in manifest.input_slots:
                count = len(step.input_bindings.get(slot.name, []))
                if count < slot.min_count or (slot.max_count is not None and count > slot.max_count):
                    raise CapabilityPlanInvalid("required capability input is not bound", code="CAPABILITY_PLAN_PORT_MISMATCH")
        if edges > 16:
            raise CapabilityPlanInvalid("dependency limit exceeded")
        required = {item.requirement_id for item in decision.scientific_requirements if item.criticality.value == "REQUIRED"}
        if not required.issubset(used_requirements):
            raise CapabilityPlanInvalid("required requirement omitted", code="CAPABILITY_PLAN_UNSATISFIED_REQUIREMENT")
        return plan
