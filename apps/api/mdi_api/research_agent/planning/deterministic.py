from __future__ import annotations

from typing import Any

from mdi_api.agent2_errors import CapabilityPlanInvalid
from mdi_api.research_agent.capabilities.schemas import (
    CapabilityBindingKind,
    CapabilityInputBinding,
    CapabilityPlan,
    CapabilityPlanStep,
    CapabilityResolution,
    PlannedCapabilityOutput,
)
from mdi_api.research_agent.orchestration.schemas import ResearchTurnDecision


def deterministic_candidate_key(
    candidate: Any,
    *,
    decision_requirement_ids: set[str],
    registry: Any,
) -> tuple[int, int, int, str, str]:
    """Rank deterministic candidates by requested coverage and contract scope.

    A broad suite should win when it covers several requirements in the same
    user request, but it must not shadow a narrower algorithm-specific
    capability when only that one requirement was requested.
    """

    manifest = registry.require(
        candidate.capability_id,
        candidate.capability_version,
    )
    covered = len(
        set(candidate.satisfies_requirement_ids) & decision_requirement_ids
    )
    unrelated_contract_requirements = len(
        set(manifest.satisfies_requirements) - decision_requirement_ids
    )
    return (
        -covered,
        unrelated_contract_requirements,
        candidate.planning_priority,
        candidate.capability_id,
        candidate.capability_version,
    )


def build_deterministic_capability_plan(*, decision: ResearchTurnDecision, resolution: CapabilityResolution, registry: Any) -> CapabilityPlan:
    if resolution.unsatisfied_required_requirement_ids:
        raise ValueError("required requirements are not capability-supported")
    selected = []
    covered: set[str] = set()
    decision_requirement_ids = {
        item.requirement_id for item in decision.scientific_requirements
    }
    # Prefer the smallest deterministic set, then stable registry priority/id order.
    for req in decision.scientific_requirements:
        if req.requirement_id in covered:
            continue
        options = [item for item in resolution.candidates if req.requirement_id in item.satisfies_requirement_ids and item.eligibility.value in {"ELIGIBLE", "CONDITIONAL"}]
        if not options:
            raise ValueError(f"no eligible capability for {req.requirement_id}")
        chosen = sorted(
            options,
            key=lambda item: deterministic_candidate_key(
                item,
                decision_requirement_ids=decision_requirement_ids,
                registry=registry,
            ),
        )[0]
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
    # Stable requirement-preserving topological order: visit the producer
    # chain for each originally selected requirement before its consumer,
    # while unrelated later requirements retain user-request order.
    ordered: list[Any] = []
    visiting: set[str] = set()
    emitted: set[str] = set()
    selected_by_ref = {
        f"{item.capability_id}@{item.capability_version}": item
        for item in selected
    }

    def visit(candidate: Any) -> None:
        reference = f"{candidate.capability_id}@{candidate.capability_version}"
        if reference in emitted:
            return
        if reference in visiting:
            return
        visiting.add(reference)
        for producer_ref in sorted(
            {
                value
                for values in candidate.possible_producers.values()
                for value in values
            }
        ):
            producer = selected_by_ref.get(producer_ref)
            if producer is not None:
                visit(producer)
        visiting.remove(reference)
        emitted.add(reference)
        ordered.append(candidate)

    for candidate in selected:
        visit(candidate)
    selected = ordered
    ordered_candidates = sorted(resolution.candidates, key=lambda item: (item.planning_priority, item.capability_id, item.capability_version))
    keys = {f"{item.capability_id}@{item.capability_version}": f"cap_{index}" for index, item in enumerate(ordered_candidates, 1)}
    steps = []
    emitted_steps: dict[str, list[CapabilityPlanStep]] = {}
    for candidate in selected:
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
                    producer_ref = f"{producer.capability_id}@{producer.capability_version}"
                    output_slot = next(out.name for out in registry.require(producer.capability_id, producer.capability_version).output_slots if (out.scientific_object_type in slot.accepted_object_types) or (out.result_type in slot.accepted_object_types))
                    input_bindings[slot.name] = [CapabilityInputBinding(kind=CapabilityBindingKind.PLANNED_OUTPUT, producer_step_id=item.step_id, producer_output_slot=output_slot)
                        for item in emitted_steps.get(producer_ref, [])]
        params = {}
        for requirement in decision.scientific_requirements:
            if requirement.requirement_id not in candidate.satisfies_requirement_ids:
                continue
            mapping = manifest.tool_bindings[0].parameter_mapping if manifest.tool_bindings else {}
            for key, value in requirement.constraints.items():
                parameter = str(mapping.get(key) or key)
                if parameter in params and params[parameter] != value:
                    raise CapabilityPlanInvalid(
                        "conflicting scientific constraints require separate analyses; "
                        "per-material parameter binding is not yet supported",
                        code="CAPABILITY_PLAN_PARAMETER_AUTHORITY_INVALID",
                    )
                params[parameter] = value
        variants = [input_bindings]
        for slot in manifest.input_slots:
            bindings = input_bindings.get(slot.name, [])
            if slot.max_count is not None and len(bindings) > slot.max_count:
                if len(manifest.input_slots) != 1 or slot.min_count != 1 or slot.max_count != 1:
                    raise CapabilityPlanInvalid("multiple source inputs require explicit pairing by the bounded planner")
                variants = [{slot.name: [binding]} for binding in bindings]
        reference = f"{candidate.capability_id}@{candidate.capability_version}"
        for bindings in variants:
            if len(steps) >= 8:
                raise CapabilityPlanInvalid("the complete source scope exceeds the capability plan step limit")
            step = CapabilityPlanStep(
                step_id=f"step_{len(steps) + 1}", capability_ref_key=keys[reference],
                satisfies_requirement_ids=list(candidate.satisfies_requirement_ids), input_bindings=bindings, parameters=params,
                expected_outputs=[PlannedCapabilityOutput(slot_name=out.name, result_type=out.result_type, scientific_object_type=out.scientific_object_type) for out in manifest.output_slots],
            )
            steps.append(step)
            emitted_steps.setdefault(reference, []).append(step)
    return CapabilityPlan(contract_version="1.0", objective=decision.research_objective or resolution.objective, steps=steps, omitted_optional_requirement_ids=resolution.optional_requirement_ids_not_covered, planner_summary=None)
