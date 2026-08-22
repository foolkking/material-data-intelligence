from __future__ import annotations

from typing import Any

from mdi_api.research_agent.capabilities.schemas import (
    CapabilityBindingKind,
    CapabilityInputBinding,
    CapabilityPlan,
    CapabilityPlanStep,
    CapabilityResolution,
    PlannedCapabilityOutput,
)
from mdi_api.research_agent.orchestration.schemas import ResearchTurnDecision


def build_deterministic_capability_plan(*, decision: ResearchTurnDecision, resolution: CapabilityResolution, registry: Any) -> CapabilityPlan:
    if resolution.unsatisfied_required_requirement_ids:
        raise ValueError("required requirements are not capability-supported")
    selected = []
    covered: set[str] = set()
    # Prefer the smallest deterministic set, then stable registry priority/id order.
    for req in decision.scientific_requirements:
        if req.requirement_id in covered:
            continue
        options = [item for item in resolution.candidates if req.requirement_id in item.satisfies_requirement_ids and item.eligibility.value in {"ELIGIBLE", "CONDITIONAL"}]
        if not options:
            raise ValueError(f"no eligible capability for {req.requirement_id}")
        chosen = sorted(options, key=lambda item: (item.planning_priority, item.capability_id, item.capability_version))[0]
        selected.append(chosen)
        covered.update(chosen.satisfies_requirement_ids)
    # Add producer capabilities required by conditional candidates.
    changed = True
    while changed:
        changed = False
        for candidate in list(selected):
            manifest = registry.require(candidate.capability_id, candidate.capability_version)
            for producer_ref in sorted(sum(candidate.possible_producers.values(), [])):
                producer_id, producer_version = producer_ref.rsplit("@", 1)
                producer = next((item for item in resolution.candidates if item.capability_id == producer_id and item.capability_version == producer_version), None)
                if producer and producer not in selected and producer.eligibility.value == "ELIGIBLE":
                    selected.append(producer)
                    changed = True
    selected = sorted(selected, key=lambda item: (item.planning_priority, item.capability_id, item.capability_version))
    # Stable topological order: a conditional consumer always follows its
    # declared producer capability, while unrelated steps retain registry order.
    ordered: list[Any] = []
    pending = list(selected)
    while pending:
        pending_refs = {f"{item.capability_id}@{item.capability_version}" for item in pending}
        ready = next((item for item in pending if not any(
            producer_ref in pending_refs
            for producer_refs in item.possible_producers.values()
            for producer_ref in producer_refs
        )), None)
        if ready is None:
            ready = pending[0]
        ordered.append(ready)
        pending.remove(ready)
    selected = ordered
    ordered_candidates = sorted(resolution.candidates, key=lambda item: (item.planning_priority, item.capability_id, item.capability_version))
    keys = {f"{item.capability_id}@{item.capability_version}": f"cap_{index}" for index, item in enumerate(ordered_candidates, 1)}
    steps = []
    for index, candidate in enumerate(selected, 1):
        manifest = registry.require(candidate.capability_id, candidate.capability_version)
        input_bindings = {}
        for slot in manifest.input_slots:
            refs = candidate.bound_source_inputs.get(slot.name, [])
            if refs:
                input_bindings[slot.name] = [CapabilityInputBinding(kind=CapabilityBindingKind.SOURCE_OBJECT, source_ref_key=key) for key in candidate.bound_source_ref_keys.get(slot.name, [])]
            elif candidate.reusable_result_bindings.get(slot.name):
                input_bindings[slot.name] = [
                    CapabilityInputBinding(kind=CapabilityBindingKind.PREVIOUS_RESULT, result_ref_key=key)
                    for key in candidate.reusable_result_bindings[slot.name]
                ]
            elif slot.name in candidate.missing_input_slots:
                producer = next((item for item in selected if any(f"{item.capability_id}@{item.capability_version}" == p for p in candidate.possible_producers.get(slot.name, []))), None)
                if producer:
                    input_bindings[slot.name] = [CapabilityInputBinding(kind=CapabilityBindingKind.PLANNED_OUTPUT, producer_step_id=f"step_{selected.index(producer) + 1}", producer_output_slot=next(out.name for out in registry.require(producer.capability_id, producer.capability_version).output_slots if (out.scientific_object_type in slot.accepted_object_types) or (out.result_type in slot.accepted_object_types)))]
        params = {}
        for requirement in decision.scientific_requirements:
            if requirement.requirement_id not in candidate.satisfies_requirement_ids:
                continue
            mapping = manifest.tool_bindings[0].parameter_mapping if manifest.tool_bindings else {}
            for key, value in requirement.constraints.items():
                params[str(mapping.get(key) or key)] = value
        if manifest.capability_id == "trajectory.diffusion":
            params = {"fit_start_time_ps": 0.0, "fit_end_time_ps": 1.0, **params}
        steps.append(CapabilityPlanStep(
            step_id=f"step_{index}", capability_ref_key=keys[f"{candidate.capability_id}@{candidate.capability_version}"],
            satisfies_requirement_ids=list(candidate.satisfies_requirement_ids), input_bindings=input_bindings, parameters=params,
            expected_outputs=[PlannedCapabilityOutput(slot_name=out.name, result_type=out.result_type, scientific_object_type=out.scientific_object_type) for out in manifest.output_slots],
        ))
    return CapabilityPlan(contract_version="1.0", objective=decision.research_objective or resolution.objective, steps=steps, omitted_optional_requirement_ids=resolution.optional_requirement_ids_not_covered, planner_summary=None)
