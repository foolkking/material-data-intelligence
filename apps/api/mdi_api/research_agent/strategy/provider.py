from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from mdi_api.research_agent.llm.structured_client import StructuredLLMClient
from mdi_api.research_agent.strategy.schemas import (
    ProviderStrategyProposal,
    ResearchEvidenceState,
)
from mdi_api.research_agent.strategy.validation import (
    StrategyProposalValidator,
    StrategyValidationError,
)


PROMPT_VERSION = "scientific-research-strategy/1.0"


def load_strategy_prompt() -> str:
    return (
        Path(__file__).parent / "prompts" / "scientific_research_strategy_v1.txt"
    ).read_text(encoding="utf-8")


class BoundedStrategyProvider:
    """One provider proposal plus at most one validation-guided repair."""

    def __init__(
        self,
        client: StructuredLLMClient,
        *,
        timeout_seconds: float = 60.0,
    ) -> None:
        self.client = client
        self.timeout_seconds = timeout_seconds

    async def propose(
        self,
        *,
        evidence_state: ResearchEvidenceState,
        legal_requirement_ids: set[str],
        repeated_requirement_ids: set[str] | None = None,
    ) -> tuple[ProviderStrategyProposal, Any]:
        validator = StrategyProposalValidator()
        first_error: Exception | None = None
        payload = evidence_state.model_dump(mode="json", exclude={"observations"})
        payload["observations"] = [
            {
                "result_id": str(item.result_id),
                "predicate": item.predicate,
                "value": item.value,
                "unit": item.unit,
            }
            for item in evidence_state.observations[:64]
        ]
        payload["legal_requirement_ids"] = sorted(legal_requirement_ids)
        payload["proposal_constraints"] = {
            "capability_need": (
                "must be null"
                if not legal_requirement_ids
                else f"must be one of {sorted(legal_requirement_ids)}"
            ),
            "references": "must use only IDs present in this payload",
            "reason_codes": "compact observable codes, not reasoning prose",
        }
        for attempt in range(2):
            result = await asyncio.wait_for(
                self.client.generate_structured(
                    role="scientific_research_strategist",
                    system_prompt=load_strategy_prompt(),
                    input_payload=payload,
                    output_schema=ProviderStrategyProposal.model_json_schema(),
                    timeout_seconds=self.timeout_seconds,
                    request_context={
                        "prompt_version": PROMPT_VERSION,
                        "repair_attempted": attempt == 1,
                        "repair": (
                            None
                            if attempt == 0
                            else {
                                "validation_error": str(first_error)[:1000],
                                "legal_result_ids": [
                                    str(value) for value in evidence_state.result_ids
                                ],
                                "legal_question_ids": [
                                    item.question_id
                                    for item in evidence_state.questions
                                ],
                                "legal_evidence_gap_ids": [
                                    item.gap_id
                                    for item in evidence_state.evidence_gaps
                                ],
                                "legal_hypothesis_ids": [
                                    item.hypothesis_id
                                    for item in evidence_state.hypotheses
                                ],
                                "legal_requirement_ids": sorted(
                                    legal_requirement_ids
                                ),
                            }
                        ),
                    },
                ),
                timeout=self.timeout_seconds,
            )
            try:
                proposal = ProviderStrategyProposal.model_validate(result.parsed)
                validator.validate(
                    proposal=proposal,
                    evidence_state=evidence_state,
                    legal_requirement_ids=legal_requirement_ids,
                    repeated_requirement_ids=repeated_requirement_ids,
                )
                if attempt == 1 and not result.repair_attempted:
                    result = result.model_copy(update={"repair_attempted": True})
                return proposal, result
            except (ValidationError, StrategyValidationError, ValueError) as exc:
                first_error = exc
        raise StrategyValidationError(
            ("PROVIDER_STRATEGY_INVALID_AFTER_BOUNDED_REPAIR",)
        ) from first_error


__all__ = ["BoundedStrategyProvider", "PROMPT_VERSION", "load_strategy_prompt"]
