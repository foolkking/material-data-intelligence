from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from mdi_api.agent2_errors import CapabilityPlanInvalid
from mdi_api.application.research.transactions import transaction_active
from mdi_api.research_agent.capabilities.schemas import CapabilityPlan, CapabilityPlannerInput, CapabilityResolution
from mdi_api.research_agent.llm.structured_client import StructuredLLMClient
from mdi_api.research_agent.orchestration.schemas import ResearchTurnDecision
from mdi_api.research_agent.planning.deterministic import (
    build_deterministic_capability_plan,
    deterministic_candidate_key,
)
from mdi_api.research_agent.planning.validator import CapabilityPlanValidator


PROMPT_VERSION = "scientific-capability-planner/1.3"


def _binding_contracts() -> dict[str, dict[str, Any]]:
    return {
        "SOURCE_OBJECT": {
            "required_fields": ["kind", "source_ref_key"],
            "forbidden_fields": ["result_ref_key", "producer_step_id", "producer_output_slot"],
        },
        "PREVIOUS_RESULT": {
            "required_fields": ["kind", "result_ref_key"],
            "forbidden_fields": ["source_ref_key", "producer_step_id", "producer_output_slot"],
        },
        "PLANNED_OUTPUT": {
            "required_fields": ["kind", "producer_step_id", "producer_output_slot"],
            "forbidden_fields": ["source_ref_key", "result_ref_key"],
        },
    }


def load_capability_planner_prompt() -> str:
    return (Path(__file__).parent / "prompts" / "scientific_capability_planner_v1.txt").read_text(encoding="utf-8")


def requires_llm_planning(
    resolution: CapabilityResolution,
    decision: ResearchTurnDecision,
    *,
    registry: Any | None = None,
) -> bool:
    decision_requirement_ids = {
        item.requirement_id for item in decision.scientific_requirements
    }
    for requirement in decision.scientific_requirements:
        options = [candidate for candidate in resolution.candidates if requirement.requirement_id in candidate.satisfies_requirement_ids and candidate.eligibility.value in {"ELIGIBLE", "CONDITIONAL"}]
        if not options:
            continue
        if registry is None:
            best_priority = min(item.planning_priority for item in options)
            equally_ranked = [
                item for item in options if item.planning_priority == best_priority
            ]
        else:
            ranked = sorted(
                options,
                key=lambda item: deterministic_candidate_key(
                    item,
                    decision_requirement_ids=decision_requirement_ids,
                    registry=registry,
                ),
            )
            best_key = deterministic_candidate_key(
                ranked[0],
                decision_requirement_ids=decision_requirement_ids,
                registry=registry,
            )[:3]
            equally_ranked = [
                item
                for item in ranked
                if deterministic_candidate_key(
                    item,
                    decision_requirement_ids=decision_requirement_ids,
                    registry=registry,
                )[:3]
                == best_key
            ]
        if len(equally_ranked) > 1:
            return True
    for candidate in resolution.candidates:
        if registry is not None:
            manifest = registry.require(candidate.capability_id, candidate.capability_version)
            if len(manifest.input_slots) > 1 and any(
                len(values) > 1 for values in candidate.bound_source_ref_keys.values()
            ):
                return True
            # Multi-input consumers need an explicit correspondence when a
            # producer has several material-specific outputs.
            if len(manifest.input_slots) > 1 and any(
                len(values) > 1
                for producer in resolution.candidates
                if f"{producer.capability_id}@{producer.capability_version}" in {
                    value for values in candidate.possible_producers.values() for value in values
                }
                for values in producer.bound_source_ref_keys.values()
            ):
                return True
        if any(len(values) > 1 for values in candidate.possible_producers.values()):
            return True
        if any(len(values) > 1 for values in candidate.reusable_result_bindings.values()):
            return True
    return False


class ScientificCapabilityPlanner:
    def __init__(self, *, registry: Any, llm_client: StructuredLLMClient | None = None, timeout_seconds: float = 60.0) -> None:
        self.registry = registry
        self.llm_client = llm_client
        self.timeout_seconds = timeout_seconds

    async def plan(self, *, decision: ResearchTurnDecision, resolution: CapabilityResolution, planner_input: CapabilityPlannerInput, context: dict[str, Any]) -> tuple[CapabilityPlan, str, Any | None]:
        if not requires_llm_planning(
            resolution,
            decision,
            registry=self.registry,
        ):
            plan = build_deterministic_capability_plan(decision=decision, resolution=resolution, registry=self.registry)
            return CapabilityPlanValidator().validate(plan=plan, resolution=resolution, decision=decision, context=context, registry=self.registry), "DETERMINISTIC", None
        if self.llm_client is None:
            raise CapabilityPlanInvalid("ambiguous capability strategy requires the bounded planner")
        first_error: Exception | None = None
        for attempt in range(2):
            if transaction_active():
                raise RuntimeError("Capability Planner provider boundary retained an open transaction")
            result = await asyncio.wait_for(self.llm_client.generate_structured(
                role="scientific_capability_planner", system_prompt=load_capability_planner_prompt(),
                input_payload=planner_input.model_dump(mode="json"), output_schema=CapabilityPlan.model_json_schema(),
                timeout_seconds=self.timeout_seconds,
                request_context={
                    "prompt_version": PROMPT_VERSION,
                    "repair_attempted": attempt == 1,
                    "binding_contracts": _binding_contracts(),
                    "repair": None if attempt == 0 else {
                        "validation_error": str(first_error)[:1000],
                        "binding_contracts": _binding_contracts(),
                        "legal_capability_contracts": [
                            item.model_dump(mode="json")
                            for item in planner_input.candidates
                        ],
                        "legal_source_keys": [
                            item.ref_key for item in planner_input.source_bindings
                        ],
                        "legal_result_keys": [
                            item.ref_key for item in planner_input.reusable_results
                        ],
                    },
                },
            ), timeout=self.timeout_seconds)
            try:
                plan = CapabilityPlan.model_validate(result.parsed)
                plan = CapabilityPlanValidator().validate(plan=plan, resolution=resolution, decision=decision, context=context, registry=self.registry)
                if attempt == 1 and not result.repair_attempted:
                    result = result.model_copy(update={"repair_attempted": True})
                return plan, "LLM", result
            except (CapabilityPlanInvalid, ValidationError, ValueError) as exc:
                first_error = exc
        raise CapabilityPlanInvalid(str(first_error or "invalid capability plan"))
