from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import asyncio
import logging
from typing import Any
from uuid import UUID, uuid4

from pydantic import ValidationError
from mdi_llm.providers import LLMProviderError

from mdi_api.agent2_errors import (
    ConcurrentTurnModification,
    ContextAssemblyFailed,
    InvalidResearchTurnDecision,
    OrchestratorProviderUnavailable,
    OrchestratorTimeout,
)
from mdi_api.research_agent.context.assembler import ResearchContextCandidateAssembler
from mdi_api.application.research.ports import ResearchRepositoryFactoryPort
from mdi_api.application.research.transactions import transaction_active
from mdi_api.research_agent.context.compiler import COMPILER_VERSION, ResearchContextCompiler
from mdi_api.research_agent.context.policy import ContextOperation, context_budget_policy
from mdi_api.research_agent.context.resolver import (
    DeterministicReferenceResolver,
    ReferenceResolution,
    candidate_source_priority,
)
from mdi_api.research_agent.context.schemas import CompactResearchContext, ResearchContextCandidateBundle, ReferenceCandidateSource
from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.llm.structured_client import (
    PROMPT_VERSION,
    StructuredLLMClient,
    load_research_orchestrator_prompt,
)
from mdi_api.research_agent.orchestration.router import ResearchActionRouter
from mdi_api.research_agent.orchestration.schemas import (
    ClarificationRequest,
    OrchestratorConfidence,
    OrchestratorRequirementOption,
    ProposedRequirement,
    ResearchOrchestratorInput,
    ResearchTurnDecision,
)
from mdi_api.research_agent.orchestration.validator import ResearchTurnDecisionValidator
from mdi_api.research_agent.registry_validation import Agent2Registries
from mdi_api.research_agent.schemas import ResearchAction, ResearchTurnEventType, ResearchTurnStatus, ScientificSelectionContext, ResolvedResearchContext, RequirementCriticality, TERMINAL_TURN_STATUSES
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.research_agent.planning.queue import DisabledCapabilityPlanningQueue


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PreparedTurn:
    turn: dict[str, Any]
    bundle: ResearchContextCandidateBundle
    compact_context: CompactResearchContext
    resolution: ReferenceResolution
    user_message: str
    autonomy: dict[str, Any]


@dataclass(frozen=True)
class ProcessTurnResult:
    outcome: str
    status: str
    provider_calls: int


class AgentTurnProcessor:
    """Idempotent Phase 2 processor. Queue payloads contain only ``turn_id``."""

    def __init__(
        self,
        *,
        repository_factory: ResearchRepositoryFactoryPort,
        registries: Agent2Registries,
        llm_client: StructuredLLMClient,
        planning_queue: Any | None = None,
        interpretation_queue: Any | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        self.repository_factory = repository_factory
        self.registries = registries
        self.llm_client = llm_client
        self.planning_queue = planning_queue or DisabledCapabilityPlanningQueue()
        self.interpretation_queue = interpretation_queue
        self.timeout_seconds = timeout_seconds
        self.assembler = ResearchContextCandidateAssembler()
        self.compiler = ResearchContextCompiler()
        self.resolver = DeterministicReferenceResolver()
        self.validator = ResearchTurnDecisionValidator(registries.requirements)
        self.router = ResearchActionRouter(repository_factory)

    async def process(self, turn_id: UUID) -> ProcessTurnResult:
        try:
            prepared = self._prepare(turn_id)
        except ConcurrentTurnModification:
            return self._noop_result(turn_id)
        except Exception as exc:
            self._fail_if_active(turn_id, "CONTEXT_ASSEMBLY_FAILED", str(exc))
            raise ContextAssemblyFailed("Research context assembly failed") from exc
        if prepared is None:
            return self._noop_result(turn_id)

        if prepared.resolution.requires_clarification:
            labels = {
                item.candidate_key: item.display_label
                for item in prepared.bundle.active_object_candidates
            }
            keys = list(prepared.resolution.ambiguous_object_keys)
            if not keys:
                result_labels = {item.candidate_key: item.display_label for item in prepared.bundle.result_candidates}
                keys = list(prepared.resolution.ambiguous_result_keys)
                question = "你指的是哪一个历史结果：" + "、".join(result_labels.get(key, key) for key in keys) + "？"
            else:
                question = "你指的是哪一个科研对象：" + "、".join(labels[key] for key in keys) + "？"
            decision = ResearchTurnDecision(
                contract_version="1.0",
                action=ResearchAction.CLARIFY,
                assistant_message=question,
                research_objective=None,
                selected_scope_ref_keys=[],
                scientific_requirements=[],
                reusable_result_ref_keys=[],
                clarification=ClarificationRequest(question=question, candidate_keys=keys),
                confidence=OrchestratorConfidence.HIGH,
            )
            self.validator.validate(
                decision=decision,
                input_context=self._orchestrator_input(prepared),
                candidate_bundle=prepared.bundle,
                continuation_turn_available=prepared.turn.get("parent_turn_id") is not None,
            )
            try:
                routed = self.router.apply(
                    turn_id=turn_id,
                    expected_version=int(prepared.turn["row_version"]),
                    decision=decision,
                    candidate_bundle=prepared.bundle,
                    provider_result=StructuredLLMResult(
                        provider="deterministic_context_resolver",
                        model="none",
                        parsed=decision.model_dump(mode="json"),
                        latency_ms=0,
                        repair_attempted=False,
                        prompt_version=PROMPT_VERSION,
                    ),
                )
            except ConcurrentTurnModification:
                return self._noop_result(turn_id)
            return ProcessTurnResult("CLARIFICATION", routed.turn_status, 0)

        orchestrator_input = self._orchestrator_input(prepared)
        autonomy_decision = self._autonomy_decision(prepared)
        if autonomy_decision is not None:
            decision = self.validator.validate(
                decision=autonomy_decision,
                input_context=orchestrator_input,
                candidate_bundle=prepared.bundle,
                continuation_turn_available=True,
            )
            provider_result = StructuredLLMResult(
                provider="deterministic_bounded_autonomy",
                model="none",
                parsed=decision.model_dump(mode="json"),
                latency_ms=0,
                repair_attempted=False,
                prompt_version="agent2.autonomy-decision/1.0",
            )
            calls = 0
        else:
            provider_result, decision, calls = await self._generate_validated(prepared, orchestrator_input)
        try:
            routed = self.router.apply(
                turn_id=turn_id,
                expected_version=int(prepared.turn["row_version"]),
                decision=decision,
                candidate_bundle=prepared.bundle,
                provider_result=provider_result,
            )
        except ConcurrentTurnModification:
            return self._noop_result(turn_id, provider_calls=calls)
        if routed.turn_status == ResearchTurnStatus.READY_TO_PLAN.value:
            self.planning_queue.enqueue_turn(turn_id)
        elif decision.action == ResearchAction.INTERPRET_RESULT and self.interpretation_queue is not None:
            self.interpretation_queue.enqueue_turn(turn_id)
        logger.info("research_turn_orchestrated", extra={
            "turn_id": str(turn_id),
            "action": decision.action.value,
            "prompt_version": provider_result.prompt_version,
            "provider": provider_result.provider,
            "model": provider_result.model,
            "latency_ms": provider_result.latency_ms,
            "repair_attempted": provider_result.repair_attempted,
            "validation_outcome": "VALIDATED",
        })
        return ProcessTurnResult("APPLIED", routed.turn_status, calls)

    def _noop_result(
        self,
        turn_id: UUID,
        *,
        provider_calls: int = 0,
    ) -> ProcessTurnResult:
        """Treat duplicate delivery or a durable cancel as an idempotent no-op."""
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
        return ProcessTurnResult("NOOP", str(turn["status"]), provider_calls)

    def _prepare(self, turn_id: UUID) -> PreparedTurn | None:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            if unit.agent2.research_turn_decisions.get_for_turn(turn_id) is not None:
                return None
            if turn["status"] != ResearchTurnStatus.RECEIVED.value:
                return None
            resolving = unit.agent2.research_turns.compare_and_set_status(
                turn_id,
                expected_status=ResearchTurnStatus.RECEIVED.value,
                expected_version=int(turn["row_version"]),
                target_status=ResearchTurnStatus.RESOLVING_CONTEXT.value,
            )
            self._append_event(unit, turn_id, ResearchTurnEventType.CONTEXT_RESOLUTION_STARTED, {
                "status": ResearchTurnStatus.RESOLVING_CONTEXT.value,
            })
            bundle = self.assembler.assemble(unit, resolving)
            resolution = self.resolver.resolve(bundle)
            budget_policy = context_budget_policy(ContextOperation.ORCHESTRATOR)
            compact = self.compiler.compile(
                turn=resolving,
                candidates=bundle,
                token_budget=budget_policy.effective_input_budget,
            )
            snapshot_id = uuid4()
            active_refs = [
                item.object_ref.model_dump(mode="json")
                for item in bundle.active_object_candidates
                if item.source != ReferenceCandidateSource.UI_SELECTION
            ]
            selected_refs = [
                item.object_ref.model_dump(mode="json")
                for item in bundle.active_object_candidates
                if item.source == ReferenceCandidateSource.UI_SELECTION
            ]
            received_event = next(
                (event for event in unit.agent2.research_turn_events.list_for_turn(turn_id)
                 if event["event_type"] == ResearchTurnEventType.TURN_RECEIVED.value),
                None,
            )
            received_payload = (received_event or {}).get("payload_json") or {}
            raw_selections = (received_payload.get("ui_context") or {}).get("scientific_selections") or []
            scientific_selections = [
                ScientificSelectionContext.model_validate(item).model_dump(mode="json")
                for item in raw_selections
            ]
            manifest_context = ResolvedResearchContext(
                project_id=bundle.project_id,
                research_session_id=bundle.research_session_id,
                active_objects=[
                    ScientificObjectRef.model_validate(item.object_ref.model_dump(mode="json"))
                    for item in bundle.active_object_candidates
                    if item.object_ref is not None and item.source != ReferenceCandidateSource.UI_SELECTION
                ],
                selection_refs=[
                    ScientificObjectRef.model_validate(item.object_ref.model_dump(mode="json"))
                    for item in bundle.active_object_candidates
                    if item.object_ref is not None and item.source == ReferenceCandidateSource.UI_SELECTION
                ],
                scientific_selections=[ScientificSelectionContext.model_validate(item) for item in scientific_selections],
                resolved_references=[],
                referenced_result_ids=[item.result_id for item in bundle.result_candidates if item.result_id is not None],
                research_goal=bundle.current_research_goal,
                user_constraints=[str(item) for item in bundle.explicit_constraints],
                unresolved_questions=list(resolution.ambiguous_object_keys),
                requires_clarification=resolution.requires_clarification,
            )
            context_manifest = ResearchTurnService._build_context_manifest(
                turn_id=turn_id,
                context=manifest_context,
                context_fingerprint=compact.context_fingerprint,
            )
            unit.agent2.research_context_snapshots.add({
                "id": snapshot_id,
                "project_id": bundle.project_id,
                "research_session_id": bundle.research_session_id,
                "research_turn_id": turn_id,
                "snapshot_schema_version": "2.0",
                "active_scope_refs_json": active_refs,
                "selection_refs_json": selected_refs,
                "scientific_selections_json": scientific_selections,
                "resolved_references_json": [item.model_dump(mode="json") for item in bundle.active_object_candidates],
                "referenced_result_refs_json": [item.model_dump(mode="json") for item in bundle.result_candidates],
                "relevant_finding_refs_json": [item.model_dump(mode="json") for item in bundle.finding_candidates],
                "effective_constraints_json": bundle.explicit_constraints,
                "research_goal": bundle.current_research_goal,
                "unresolved_questions_json": list(resolution.ambiguous_object_keys),
                "context_fingerprint": compact.context_fingerprint,
                "compiler_version": COMPILER_VERSION,
                "created_at": datetime.now(timezone.utc),
            })
            attached = unit.agent2.research_turns.attach_context_snapshot(turn_id, snapshot_id)
            orchestrating = unit.agent2.research_turns.compare_and_set_status(
                turn_id,
                expected_status=ResearchTurnStatus.RESOLVING_CONTEXT.value,
                expected_version=int(attached["row_version"]),
                target_status=ResearchTurnStatus.ORCHESTRATING.value,
            )
            self._append_event(unit, turn_id, ResearchTurnEventType.CONTEXT_RESOLVED, {
                "status": ResearchTurnStatus.ORCHESTRATING.value,
                "context_snapshot_id": str(snapshot_id),
                "context_manifest": context_manifest.model_dump(mode="json"),
            })
            if resolution.requires_clarification:
                self._append_event(unit, turn_id, ResearchTurnEventType.CONTEXT_AMBIGUOUS, {
                    "candidate_keys": list(resolution.ambiguous_object_keys),
                })
            else:
                self._append_event(unit, turn_id, ResearchTurnEventType.ORCHESTRATION_STARTED, {
                    "status": ResearchTurnStatus.ORCHESTRATING.value,
                })
            message = unit.agent2.research_turns.get_message(str(turn["user_message_id"]))
            return PreparedTurn(
                turn=orchestrating,
                bundle=bundle,
                compact_context=compact,
                resolution=resolution,
                user_message=str(message["content_summary"]),
                autonomy=dict(received_payload.get("autonomy") or {}),
            )

    def _autonomy_decision(self, prepared: PreparedTurn) -> ResearchTurnDecision | None:
        autonomy = prepared.autonomy
        if (
            autonomy.get("mode") != "BOUNDED_AUTONOMOUS"
            or not autonomy.get("assessment_signature")
        ):
            return None
        requirement_id = str(autonomy.get("requirement_id") or "")
        capability_id = str(autonomy.get("selected_capability_id") or "")
        if not requirement_id or not capability_id:
            raise InvalidResearchTurnDecision(
                "Autonomous cycle is missing its persisted scientific subgoal",
                code="AUTONOMY_DECISION_INVALID",
            )
        requirement = self.registries.requirements.require(requirement_id)
        selected_scope = [
            item.candidate_key
            for item in prepared.bundle.active_object_candidates
            if (
                item.object_ref is not None
                and (
                    not requirement.accepted_object_types
                    or item.object_ref.object_type in requirement.accepted_object_types
                )
            )
        ]
        if not selected_scope:
            raise InvalidResearchTurnDecision(
                "Autonomous cycle has no exact eligible source object",
                code="AUTONOMY_SOURCE_UNAVAILABLE",
            )
        highest = min(
            candidate_source_priority(item.source)
            for item in prepared.bundle.active_object_candidates
            if item.candidate_key in selected_scope
        )
        selected_scope = [
            item.candidate_key
            for item in prepared.bundle.active_object_candidates
            if item.candidate_key in selected_scope
            and candidate_source_priority(item.source) == highest
        ]
        reusable = [
            item.candidate_key
            for item in prepared.bundle.result_candidates
            if str(item.result_id) == str(autonomy.get("evidence_result_id"))
        ]
        return ResearchTurnDecision(
            contract_version="1.0",
            action=ResearchAction.CONTINUE_ANALYSIS,
            assistant_message=(
                "现有科学结果仍有一个明确未解决的研究需求；"
                "系统将在限定策略内执行最小的下一项分析。"
            ),
            research_objective=str(
                autonomy.get("research_objective") or prepared.user_message
            )[:2048],
            selected_scope_ref_keys=selected_scope,
            scientific_requirements=[
                ProposedRequirement(
                    requirement_id=requirement_id,
                    criticality=RequirementCriticality.REQUIRED,
                    subject_ref_keys=selected_scope,
                    constraints=dict(autonomy.get("constraints") or {}),
                )
            ],
            reusable_result_ref_keys=reusable,
            clarification=None,
            confidence=OrchestratorConfidence.HIGH,
        )

    def _orchestrator_input(self, prepared: PreparedTurn) -> ResearchOrchestratorInput:
        return ResearchOrchestratorInput(
            contract_version="1.0",
            user_message=prepared.user_message,
            research_context=prepared.compact_context,
            available_requirement_ids=[OrchestratorRequirementOption(
                requirement_id=item.requirement_id,
                display_name=item.display_name,
                description=item.description,
                constraint_schema=item.constraint_schema,
            ) for item in self.registries.requirements.list_active()],
            allowed_actions=self._allowed_actions(prepared),
        )

    @staticmethod
    def _allowed_actions(prepared: PreparedTurn) -> list[ResearchAction]:
        """Advertise only actions that the resolved context can satisfy.

        The validator remains the fail-closed authority.  This bounded
        projection prevents the provider from repeatedly selecting an
        impossible result-only action when the turn has scientific objects but
        no reusable result.
        """

        result_available = bool(prepared.bundle.result_candidates)
        continuation_available = (
            result_available or prepared.turn.get("parent_turn_id") is not None
        )
        unavailable: set[ResearchAction] = set()
        if not result_available:
            unavailable.update({
                ResearchAction.INTERPRET_RESULT,
                ResearchAction.CREATE_REPORT,
                ResearchAction.UPDATE_REPORT,
            })
        if not continuation_available:
            unavailable.add(ResearchAction.CONTINUE_ANALYSIS)
        return [action for action in ResearchAction if action not in unavailable]

    async def _generate_validated(
        self,
        prepared: PreparedTurn,
        orchestrator_input: ResearchOrchestratorInput,
    ) -> tuple[StructuredLLMResult, ResearchTurnDecision, int]:
        first_error: Exception | None = None
        for attempt in range(2):
            try:
                if transaction_active():
                    raise RuntimeError("Provider boundary retained an open database transaction")
                result = await asyncio.wait_for(
                    self.llm_client.generate_structured(
                        role="research_turn_orchestrator",
                        system_prompt=load_research_orchestrator_prompt(),
                        input_payload=orchestrator_input.model_dump(mode="json"),
                        output_schema=ResearchTurnDecision.model_json_schema(),
                        timeout_seconds=self.timeout_seconds,
                        request_context={
                            "turn_id": str(prepared.turn["id"]),
                            "prompt_version": PROMPT_VERSION,
                            "repair_attempted": attempt == 1,
                            "repair": None if attempt == 0 else {
                                "validation_error": str(first_error)[:1000],
                                "legal_candidate_keys": self._candidate_keys(prepared.bundle),
                                "registered_requirement_ids": [item.requirement_id for item in self.registries.requirements.list_active()],
                            },
                        },
                    ),
                    timeout=self.timeout_seconds,
                )
                decision = ResearchTurnDecision.model_validate(result.parsed)
                decision = self.validator.validate(
                    decision=decision,
                    input_context=orchestrator_input,
                    candidate_bundle=prepared.bundle,
                    continuation_turn_available=prepared.turn.get("parent_turn_id") is not None,
                )
                if attempt == 1 and not result.repair_attempted:
                    result = result.model_copy(update={"repair_attempted": True})
                return result, decision, attempt + 1
            except (InvalidResearchTurnDecision, ValidationError, ValueError) as exc:
                first_error = exc
                if attempt == 1:
                    code = exc.code if isinstance(exc, InvalidResearchTurnDecision) else "ORCHESTRATOR_INVALID_OUTPUT"
                    self._fail_if_active(prepared.turn["id"], code, str(exc))
                    raise
            except TimeoutError as exc:
                self._fail_if_active(prepared.turn["id"], "ORCHESTRATOR_TIMEOUT", "Orchestrator request timed out")
                raise OrchestratorTimeout("Orchestrator request timed out") from exc
            except LLMProviderError as exc:
                code = "ORCHESTRATOR_TIMEOUT" if "TIMEOUT" in exc.code else "ORCHESTRATOR_PROVIDER_UNAVAILABLE"
                self._fail_if_active(prepared.turn["id"], code, exc.safe_message)
                if code == "ORCHESTRATOR_TIMEOUT":
                    raise OrchestratorTimeout(exc.safe_message) from exc
                raise OrchestratorProviderUnavailable(exc.safe_message) from exc
        raise AssertionError("unreachable")

    def _fail_if_active(self, turn_id: UUID, code: str, summary: str) -> None:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            status = ResearchTurnStatus(str(turn["status"]))
            if status in TERMINAL_TURN_STATUSES or status not in {
                ResearchTurnStatus.RECEIVED,
                ResearchTurnStatus.RESOLVING_CONTEXT,
                ResearchTurnStatus.ORCHESTRATING,
            }:
                return
            updated = unit.agent2.research_turns.compare_and_set_status(
                turn_id,
                expected_status=status.value,
                expected_version=int(turn["row_version"]),
                target_status=ResearchTurnStatus.FAILED.value,
                completed_at=datetime.now(timezone.utc),
                error_code=code,
                error_summary=summary[:1000],
            )
            self._append_event(unit, turn_id, ResearchTurnEventType.TURN_FAILED, {
                "status": updated["status"],
                "error_code": code,
            })

    @staticmethod
    def _append_event(unit: Any, turn_id: UUID, event_type: ResearchTurnEventType, payload: dict[str, Any]) -> None:
        unit.agent2.research_turn_events.append_turn_event({
            "id": uuid4(),
            "turn_id": turn_id,
            "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
            "event_type": event_type.value,
            "payload_json": payload,
            "created_at": datetime.now(timezone.utc),
        })

    @staticmethod
    def _candidate_keys(bundle: ResearchContextCandidateBundle) -> list[str]:
        return [item.candidate_key for item in [
            *bundle.active_object_candidates,
            *bundle.result_candidates,
            *bundle.finding_candidates,
        ]]
