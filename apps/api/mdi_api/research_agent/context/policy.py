"""Checked-in, operation-specific context budget policy.

The provider's advertised context window is not treated as the product
budget.  Each operation gets a bounded effective input budget after reserving
space for the provider response and one structured-repair attempt.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ContextOperation(StrEnum):
    ORCHESTRATOR = "ORCHESTRATOR"
    PLANNER = "PLANNER"
    INTERPRETER = "INTERPRETER"
    DATA = "DATA"
    REPORT = "REPORT"


@dataclass(frozen=True)
class ContextBudgetPolicy:
    """A bounded product policy for one provider-facing operation."""

    provider_context_limit: int
    product_global_limit: int
    operation_specific_limit: int
    reserved_output_tokens: int
    repair_margin: int

    @property
    def effective_input_budget(self) -> int:
        budget = min(
            self.provider_context_limit,
            self.product_global_limit,
            self.operation_specific_limit,
        ) - self.reserved_output_tokens - self.repair_margin
        if budget < 256:
            raise ValueError("context policy leaves less than the minimum input budget")
        return budget


# The provider integration currently exposes a conservative 16k product-facing
# context envelope.  The product deliberately caps payloads below that envelope
# and reserves output/repair space instead of filling the provider window.
CONTEXT_BUDGET_POLICIES: dict[ContextOperation, ContextBudgetPolicy] = {
    ContextOperation.ORCHESTRATOR: ContextBudgetPolicy(
        provider_context_limit=16_384,
        product_global_limit=14_560,
        operation_specific_limit=14_560,
        reserved_output_tokens=2_048,
        repair_margin=512,
    ),
    ContextOperation.PLANNER: ContextBudgetPolicy(
        provider_context_limit=16_384,
        product_global_limit=12_560,
        operation_specific_limit=12_560,
        reserved_output_tokens=2_048,
        repair_margin=512,
    ),
    ContextOperation.INTERPRETER: ContextBudgetPolicy(
        provider_context_limit=16_384,
        product_global_limit=14_560,
        operation_specific_limit=14_560,
        reserved_output_tokens=2_048,
        repair_margin=512,
    ),
    ContextOperation.DATA: ContextBudgetPolicy(
        provider_context_limit=16_384,
        product_global_limit=10_560,
        operation_specific_limit=10_560,
        reserved_output_tokens=2_048,
        repair_margin=512,
    ),
    ContextOperation.REPORT: ContextBudgetPolicy(
        provider_context_limit=16_384,
        product_global_limit=16_384,
        operation_specific_limit=16_384,
        reserved_output_tokens=6_144,
        repair_margin=512,
    ),
}


def context_budget_policy(operation: ContextOperation) -> ContextBudgetPolicy:
    return CONTEXT_BUDGET_POLICIES[operation]
