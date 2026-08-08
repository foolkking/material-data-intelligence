"""Bounded Phase 10L-3 composition over an exact L2 selected-tool domain."""

from __future__ import annotations

import json
from typing import Any, Iterable

from pydantic import ValidationError

from mdi_schemas import (
    AnalysisPlan,
    AnalysisPlanV02,
    CapabilityPlanningDecision,
    DependencyCompositionProposal,
    DependencyBinding,
    EligibleCandidateProjection,
    compute_dependency_graph_hash,
    dependency_semantic_hash,
    make_dependency_binding,
)
from mdi_tool_registry import build_artifact_compatibility_matrix, validate_dependency_plan

from .providers import LLMProviderError, OpenAICompatibleProvider, PlannerUserConfig


DEPENDENCY_COMPOSER_VERSION = "1.0"
_REAL_PRODUCER_CLOSURES: dict[str, tuple[str, ...]] = {
    "phonon.band_dos": ("phonon.band", "phonon.dos"),
}


class DependencyCompositionError(RuntimeError):
    def __init__(self, message: str, *, code: str, repairable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.repairable = repairable


def expand_selected_dependency_closure(
    selected_tool_ids: Iterable[str],
    *,
    projection: EligibleCandidateProjection,
    limit: int,
) -> list[str]:
    """Add only exact eligible producers required by a selected real consumer."""
    eligible_ids = {item.toolId for item in projection.candidates}
    result = set(selected_tool_ids)
    for consumer_id in sorted(tuple(result)):
        producers = _REAL_PRODUCER_CLOSURES.get(consumer_id, ())
        if producers and not set(producers).issubset(eligible_ids):
            raise DependencyCompositionError(
                "A selected dependency consumer lacks an eligible exact producer closure.",
                code="DEPENDENCY_PRODUCER_NOT_ELIGIBLE",
            )
        result.update(producers)
    if len(result) > min(limit, 4):
        raise DependencyCompositionError(
            "The exact dependency producer closure exceeds the bounded tool cap.",
            code="DEPENDENCY_TOOL_CAP_EXCEEDED",
        )
    return sorted(result)


def compose_analysis_plan_02(
    base_plan: AnalysisPlan,
    *,
    registry: Any,
    decision: CapabilityPlanningDecision,
    selected_pair_ids: Iterable[str] | None = None,
) -> AnalysisPlan | AnalysisPlanV02:
    """Return 0.2 only when selected tools have real compatible port bindings."""
    selected_ids = sorted(item.toolId for item in decision.selections)
    matrix = build_artifact_compatibility_matrix(registry, selected_tool_ids=selected_ids)
    step_by_tool = {item.toolId: item.stepId for item in base_plan.steps}
    compatible_pairs = [item for item in matrix.pairs if item.compatible]
    if not compatible_pairs:
        return base_plan
    compatible_by_id = {item.pairId: item for item in compatible_pairs}
    selected_ids_from_proposal = sorted(selected_pair_ids) if selected_pair_ids is not None else sorted(compatible_by_id)
    if selected_ids_from_proposal != sorted(set(selected_ids_from_proposal)):
        raise DependencyCompositionError(
            "Dependency composition pair identities must be unique and sorted.",
            code="DEPENDENCY_PAIR_SELECTION_INVALID",
            repairable=True,
        )
    if set(selected_ids_from_proposal) != set(compatible_by_id):
        raise DependencyCompositionError(
            "Dependency composition must use the exact compatible port-pair domain.",
            code="DEPENDENCY_PAIR_DOMAIN_MISMATCH",
            repairable=True,
        )
    compatible_pairs = [compatible_by_id[item] for item in selected_ids_from_proposal]
    bindings: list[DependencyBinding] = []
    consumer_steps: set[str] = set()
    for pair in compatible_pairs:
        producer_step = step_by_tool.get(pair.producerToolId)
        consumer_step = step_by_tool.get(pair.consumerToolId)
        if producer_step is None or consumer_step is None:
            raise DependencyCompositionError(
                "A compatible artifact port references a tool outside the exact selection.",
                code="DEPENDENCY_SELECTED_TOOL_MISMATCH",
            )
        if pair.artifactKind is None or pair.artifactContractVersion is None or pair.mediaType is None:
            raise DependencyCompositionError(
                "A compatible artifact port pair is missing an exact contract.",
                code="DEPENDENCY_CONTRACT_MISSING",
            )
        binding = make_dependency_binding(
            producerStepId=producer_step,
            producerOutputPort=pair.producerOutputPort,
            consumerStepId=consumer_step,
            consumerInputPort=pair.consumerInputPort,
            artifactKind=pair.artifactKind,
            artifactContractVersion=pair.artifactContractVersion,
            mediaType=pair.mediaType,
            cardinality="EXACTLY_ONE",
        )
        bindings.append(binding)
        consumer_steps.add(consumer_step)
    bindings = sorted(
        bindings,
        key=lambda item: (
            item.producerStepId, item.producerOutputPort, item.consumerStepId, item.consumerInputPort, item.bindingId
        ),
    )
    steps = [
        step.model_copy(update={"inputRefs": []})
        if step.stepId in consumer_steps and step.toolId != "structure.local_environment_polyhedra"
        else step
        for step in base_plan.steps
    ]
    plan = AnalysisPlanV02.model_validate(
        {
            **base_plan.model_dump(mode="json"),
            "schemaVersion": "0.2",
            "graphHash": compute_dependency_graph_hash(bindings),
            "steps": [item.model_dump(mode="json") for item in steps],
            "dependencyBindings": [item.model_dump(mode="json") for item in bindings],
        }
    )
    validation = validate_dependency_plan(plan, registry=registry, selected_tool_ids=selected_ids)
    if not validation.ok:
        raise DependencyCompositionError(
            validation.errors[0].message,
            code=validation.errors[0].code.value,
            repairable=True,
        )
    return plan


def compose_analysis_plan_with_provider(
    base_plan: AnalysisPlan,
    *,
    registry: Any,
    decision: CapabilityPlanningDecision,
    provider: OpenAICompatibleProvider,
    user_config: PlannerUserConfig | None,
    repair_budget: int,
) -> tuple[AnalysisPlan | AnalysisPlanV02, int, str | None, list[dict[str, str]]]:
    """Request only pair IDs and consume at most the remaining shared repair budget."""
    selected_tool_ids = sorted(item.toolId for item in decision.selections)
    matrix = build_artifact_compatibility_matrix(registry, selected_tool_ids=selected_tool_ids)
    compatible = [item for item in matrix.pairs if item.compatible]
    if not compatible:
        return base_plan, 0, None, []
    proposal, model = _request_composition_proposal(
        provider,
        matrix=matrix,
        user_config=user_config,
    )
    initial_hash = dependency_semantic_hash(proposal)
    try:
        plan = compose_analysis_plan_02(
            base_plan,
            registry=registry,
            decision=decision,
            selected_pair_ids=proposal.selectedPairIds,
        )
        return plan, 0, initial_hash, []
    except DependencyCompositionError as exc:
        if not exc.repairable or repair_budget < 1:
            raise DependencyCompositionError(str(exc), code=exc.code, repairable=False) from exc
        diagnostic = {"code": exc.code, "message": str(exc)}
        repaired, _ = _request_composition_proposal(
            provider,
            matrix=matrix,
            user_config=user_config,
            invalid_proposal=proposal,
            diagnostics=[diagnostic],
        )
        try:
            plan = compose_analysis_plan_02(
                base_plan,
                registry=registry,
                decision=decision,
                selected_pair_ids=repaired.selectedPairIds,
            )
        except DependencyCompositionError as final_exc:
            raise DependencyCompositionError(str(final_exc), code=final_exc.code, repairable=False) from final_exc
        return plan, 1, initial_hash, [diagnostic]


def _request_composition_proposal(
    provider: OpenAICompatibleProvider,
    *,
    matrix: Any,
    user_config: PlannerUserConfig | None,
    invalid_proposal: DependencyCompositionProposal | None = None,
    diagnostics: list[dict[str, str]] | None = None,
) -> tuple[DependencyCompositionProposal, str]:
    visible_pairs = [
        {
            "pairId": item.pairId,
            "producerToolId": item.producerToolId,
            "producerToolVersion": item.producerToolVersion,
            "producerOutputPort": item.producerOutputPort,
            "consumerToolId": item.consumerToolId,
            "consumerToolVersion": item.consumerToolVersion,
            "consumerInputPort": item.consumerInputPort,
            "artifactKind": item.artifactKind.value if item.artifactKind else None,
            "artifactContractVersion": item.artifactContractVersion,
            "mediaType": item.mediaType,
        }
        for item in matrix.pairs
        if item.compatible
    ]
    context = {
        "matrixId": matrix.matrixId,
        "selectedToolIds": matrix.selectedToolIds,
        "compatiblePairs": visible_pairs,
        "outputSchema": DependencyCompositionProposal.model_json_schema(),
        "outputTemplate": {
            "schemaVersion": "1.0",
            "matrixId": matrix.matrixId,
            "selectedPairIds": sorted(item["pairId"] for item in visible_pairs),
        },
        "invalidProposal": invalid_proposal.model_dump(mode="json") if invalid_proposal else None,
        "diagnostics": diagnostics or [],
    }
    messages = [
        {
            "role": "system",
            "content": (
                "Return exactly one bare JSON object matching DependencyCompositionProposal 1.0. "
                "Copy outputTemplate exactly: matrixId must equal the supplied matrixId and selectedPairIds must be the "
                "sorted list of every pairId in compatiblePairs. Include no fields outside outputSchema. "
                "Do not invent tools, steps, ports, contracts, "
                "artifact payloads, paths, URLs, code, dependencies, conditions, retries, or callbacks."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(context, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False),
        },
    ]
    try:
        response = provider.complete_json(
            messages=messages,
            user_config=user_config,
            purpose="MULTI_TOOL_COMPOSITION",
        )
    except LLMProviderError as exc:
        raise DependencyCompositionError(exc.safe_message, code=exc.code, repairable=False) from exc
    parsed = _strict_json_object(response.raw_text)
    try:
        proposal = DependencyCompositionProposal.model_validate(parsed)
    except ValidationError as exc:
        raise DependencyCompositionError(
            "LLM dependency composition failed the strict schema.",
            code="DEPENDENCY_LLM_SCHEMA_INVALID",
            repairable=False,
        ) from exc
    if proposal.matrixId != matrix.matrixId:
        raise DependencyCompositionError(
            "LLM dependency composition used a stale compatibility matrix.",
            code="DEPENDENCY_MATRIX_IDENTITY_MISMATCH",
            repairable=True,
        )
    compatible_ids = {item["pairId"] for item in visible_pairs}
    if not set(proposal.selectedPairIds).issubset(compatible_ids):
        raise DependencyCompositionError(
            "LLM dependency composition invented or leaked an incompatible port pair.",
            code="DEPENDENCY_PAIR_NOT_COMPATIBLE",
            repairable=True,
        )
    return proposal, response.model


def _strict_json_object(raw: str) -> dict[str, Any]:
    if not isinstance(raw, str) or raw != raw.strip() or raw.startswith("```"):
        raise DependencyCompositionError(
            "LLM dependency composition must be one bare JSON object.",
            code="DEPENDENCY_LLM_JSON_INVALID",
            repairable=False,
        )

    def reject_duplicates(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result

    try:
        parsed = json.loads(
            raw,
            object_pairs_hook=reject_duplicates,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise DependencyCompositionError(
            "LLM dependency composition is not strict JSON.",
            code="DEPENDENCY_LLM_JSON_INVALID",
            repairable=False,
        ) from exc
    if not isinstance(parsed, dict):
        raise DependencyCompositionError(
            "LLM dependency composition must be a JSON object.",
            code="DEPENDENCY_LLM_JSON_INVALID",
            repairable=False,
        )
    return parsed


# Keep the first implementation spelling as a compatibility alias for local
# callers created while the Phase 10L-3 contract was being assembled.
compose_analysis_plan_v02 = compose_analysis_plan_02


__all__ = [
    "DEPENDENCY_COMPOSER_VERSION",
    "DependencyCompositionError",
    "compose_analysis_plan_02",
    "compose_analysis_plan_with_provider",
    "compose_analysis_plan_v02",
    "expand_selected_dependency_closure",
]
