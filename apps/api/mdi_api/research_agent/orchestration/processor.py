from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import asyncio
import json
import logging
import re
from typing import Any
from uuid import UUID, uuid4

from pydantic import ValidationError
from mdi_llm.providers import LLMProviderError, PROVIDER_TIMEOUT_CODES
from mdi_llm.http_transport import ProviderStreamCancelled

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
from mdi_api.research_agent.orchestration.answer_stream import ResearchAnswerPublisher
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
    explicit_result_candidate_keys: frozenset[str]
    requested_action: str | None = None


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
        policy_decision = (
            self._requested_action_decision(prepared)
            or self._trajectory_window_decision(prepared)
            or self._autonomy_decision(prepared)
        )
        if policy_decision is not None:
            decision = self.validator.validate(
                decision=policy_decision,
                input_context=orchestrator_input,
                candidate_bundle=prepared.bundle,
                continuation_turn_available=(
                    prepared.turn.get("parent_turn_id") is not None
                ),
            )
            provider_result = StructuredLLMResult(
                provider="explicit_user_action" if prepared.requested_action else "deterministic_bounded_policy",
                model="none",
                parsed=decision.model_dump(mode="json"),
                latency_ms=0,
                repair_attempted=False,
                prompt_version="agent2.explicit-action/1.0" if prepared.requested_action else "agent2.bounded-policy/1.0",
            )
            calls = 0
        else:
            try:
                provider_result, decision, calls = await self._generate_validated(prepared, orchestrator_input)
            except ProviderStreamCancelled:
                return self._noop_result(turn_id, provider_calls=1)
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

    @staticmethod
    def _requested_action_decision(prepared: PreparedTurn) -> ResearchTurnDecision | None:
        if prepared.requested_action != "INTERPRET_RESULT":
            return None
        # _prepare has resolved the exact, authorized snapshot. The regular
        # validator/router still reauthorize it before asynchronous dispatch.
        return ResearchTurnDecision(
            contract_version="1.0",
            action=ResearchAction.INTERPRET_RESULT,
            assistant_message=None,
            research_objective=None,
            selected_scope_ref_keys=[],
            scientific_requirements=[],
            reusable_result_ref_keys=sorted(prepared.explicit_result_candidate_keys),
            clarification=None,
            confidence=OrchestratorConfidence.HIGH,
        )

    def _trajectory_window_decision(
        self,
        prepared: PreparedTurn,
    ) -> ResearchTurnDecision | None:
        """Enforce an explicit bounded analytics window for large trajectories.

        This is a finite scientific-selection policy, not an intent shortcut:
        it applies only when the user asks for registered trajectory analytics
        over an exact trajectory whose durable metadata exceeds the released
        200-frame analysis cap.
        """

        message = prepared.user_message.strip()
        lowered = message.lower()
        analytics_requested = any(
            token in lowered
            for token in ("rdf", "msd", "diffusion", "扩散", "均方位移", "径向分布")
        )
        if not analytics_requested:
            return None
        candidates: list[tuple[Any, dict[str, Any]]] = []
        for item in prepared.bundle.active_object_candidates:
            if item.object_ref is None or item.object_ref.object_type != "trajectory.atomic":
                continue
            try:
                summary = json.loads(item.semantic_summary or "{}")
            except (TypeError, ValueError):
                continue
            metadata = dict(summary.get("canonical_metadata") or {})
            if int(metadata.get("frameCount") or 0) > 0:
                candidates.append((item, metadata))
        if len(candidates) != 1:
            return None
        candidate, metadata = candidates[0]
        frame_count = int(metadata["frameCount"])
        if frame_count <= 200:
            return None

        selected_count: int | None = None
        frame_start: int | None = None
        frame_end: int | None = None
        final_match = re.search(
            r"\b(?:final|last)\s+(\d{1,4})\s+frames?\b",
            lowered,
        )
        range_match = re.search(
            r"\bframes?\s+(\d{1,5})\s*(?:-|–|—|to)\s*(\d{1,5})\b",
            lowered,
        )
        if final_match:
            selected_count = int(final_match.group(1))
            frame_end = frame_count
            frame_start = frame_count - selected_count
        elif range_match:
            first_user = int(range_match.group(1))
            last_user = int(range_match.group(2))
            frame_start = first_user - 1
            frame_end = last_user
            selected_count = frame_end - frame_start

        if (
            selected_count is None
            or frame_start is None
            or frame_end is None
            or selected_count < 1
            or selected_count > 200
            or frame_start < 0
            or frame_end > frame_count
        ):
            question = (
                f"完整轨迹包含 {frame_count} 帧；科学轨迹分析一次最多使用 200 帧。"
                "请选择一个明确的连续分析帧范围（例如“最后 200 帧”）；"
                "完整轨迹仍会保留用于查看。"
            )
            return ResearchTurnDecision(
                contract_version="1.0",
                action=ResearchAction.CLARIFY,
                assistant_message=question,
                research_objective=None,
                selected_scope_ref_keys=[],
                scientific_requirements=[],
                reusable_result_ref_keys=[],
                clarification=ClarificationRequest(
                    question=question,
                    candidate_keys=[candidate.candidate_key],
                ),
                confidence=OrchestratorConfidence.HIGH,
            )

        time_start = float(metadata.get("timeStartPs") or 0.0)
        time_end = float(metadata.get("timeEndPs") or 0.0)
        timestep = (
            (time_end - time_start) / float(frame_count - 1)
            if frame_count > 1 and time_end > time_start
            else 0.0
        )
        selected_duration = timestep * float(selected_count - 1)
        if timestep <= 0 or selected_duration <= timestep:
            return None
        window = {
            "window_mode": "frame",
            "frame_start": frame_start,
            "frame_end": frame_end,
        }
        requirements = [
            ("trajectory.inspect_view", {}),
            ("trajectory.compute_rdf", window),
            ("trajectory.compute_msd", window),
            (
                "trajectory.estimate_diffusion",
                {
                    "fit_start_time_ps": round(timestep, 12),
                    "fit_end_time_ps": round(selected_duration, 12),
                },
            ),
        ]
        return ResearchTurnDecision(
            contract_version="1.0",
            action=ResearchAction.CONTINUE_ANALYSIS,
            assistant_message=(
                f"将保留完整 {frame_count} 帧轨迹用于查看，并仅使用用户明确选择的"
                f"第 {frame_start + 1}–{frame_end} 帧执行有界 RDF、MSD 与扩散分析。"
            ),
            research_objective=message[:2048],
            selected_scope_ref_keys=[candidate.candidate_key],
            scientific_requirements=[
                ProposedRequirement(
                    requirement_id=requirement_id,
                    criticality=RequirementCriticality.REQUIRED,
                    subject_ref_keys=[candidate.candidate_key],
                    constraints=dict(constraints),
                )
                for requirement_id, constraints in requirements
            ],
            reusable_result_ref_keys=[],
            clarification=None,
            confidence=OrchestratorConfidence.HIGH,
        )

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
            received_event = next(
                (event for event in unit.agent2.research_turn_events.list_for_turn(turn_id)
                 if event["event_type"] == ResearchTurnEventType.TURN_RECEIVED.value),
                None,
            )
            received_payload = (received_event or {}).get("payload_json") or {}
            requested_action = received_payload.get("requested_action")
            explicit_result_ids = (received_payload.get("ui_context") or {}).get("explicit_result_ids") or []
            explicit_result_candidate_keys = frozenset(
                item.candidate_key for item in bundle.result_candidates
                if item.result_id is not None
                and str(item.result_id) in {str(result_id) for result_id in explicit_result_ids}
            )
            resolution = self.resolver.resolve(bundle)
            if requested_action is not None:
                if (
                    requested_action != "INTERPRET_RESULT"
                    or len(explicit_result_ids) != 1
                    or len(explicit_result_candidate_keys) != 1
                ):
                    raise ValueError("所选科学结果不可用于重新解释，请重新选择可用结果。")
                # Object ambiguity cannot change an explicit result action
                # into analysis or a request to choose unrelated source data.
                resolution = ReferenceResolution((), (), tuple(explicit_result_candidate_keys), ())
            budget_policy = context_budget_policy(ContextOperation.ORCHESTRATOR)
            user_message = str(unit.agent2.research_turns.get_message(str(turn["user_message_id"]))["content_summary"])
            compact = self.compiler.compile(
                turn=resolving,
                candidates=bundle,
                token_budget=budget_policy.effective_input_budget,
                input_payload=None if requested_action is not None else lambda context: self._build_orchestrator_input(
                    user_message=user_message, context=context, bundle=bundle, turn=resolving,
                ).model_dump(mode="json"),
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
            scientific_selections = [
                item.model_dump(mode="json") for item in bundle.scientific_selections
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
            prepared = PreparedTurn(
                turn=orchestrating,
                bundle=bundle,
                compact_context=compact,
                resolution=resolution,
                user_message=user_message,
                autonomy=dict(received_payload.get("autonomy") or {}),
                explicit_result_candidate_keys=explicit_result_candidate_keys,
                requested_action=requested_action,
            )
            resolved_payload = {
                "status": ResearchTurnStatus.ORCHESTRATING.value,
                "context_snapshot_id": str(snapshot_id),
            }
            if requested_action is None:
                orchestrator_input = self._orchestrator_input(prepared)
                context_manifest = ResearchTurnService._build_context_manifest(
                    turn_id=turn_id,
                    context=manifest_context,
                    context_fingerprint=compact.context_fingerprint,
                    serialized_input=orchestrator_input.model_dump(mode="json"),
                    serialized_input_version=orchestrator_input.contract_version,
                    invocation_role="research_turn_orchestrator",
                    prompt_template_version=PROMPT_VERSION,
                    input_state="ACTUAL",
                )
                resolved_payload["context_manifest"] = context_manifest.model_dump(mode="json")
            else:
                # No intent-model invocation took place. The interpreter
                # records its actual input manifest when its queue runs.
                resolved_payload["requested_action"] = requested_action
            self._append_event(unit, turn_id, ResearchTurnEventType.CONTEXT_RESOLVED, resolved_payload)
            if resolution.requires_clarification:
                self._append_event(unit, turn_id, ResearchTurnEventType.CONTEXT_AMBIGUOUS, {
                    "candidate_keys": list(resolution.ambiguous_object_keys),
                })
            else:
                self._append_event(unit, turn_id, ResearchTurnEventType.ORCHESTRATION_STARTED, {
                    "status": ResearchTurnStatus.ORCHESTRATING.value,
                })
            return prepared

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
        return self._build_orchestrator_input(
            user_message=prepared.user_message, context=prepared.compact_context,
            bundle=prepared.bundle, turn=prepared.turn,
        )

    def _build_orchestrator_input(
        self, *, user_message: str, context: CompactResearchContext,
        bundle: ResearchContextCandidateBundle, turn: dict[str, Any],
    ) -> ResearchOrchestratorInput:
        return ResearchOrchestratorInput(
            contract_version="1.0",
            user_message=user_message,
            research_context=context,
            available_requirement_ids=[OrchestratorRequirementOption(
                requirement_id=item.requirement_id,
                display_name=item.display_name,
                description=item.description,
                constraint_schema=item.constraint_schema,
                requires_material=item.requires_material,
            ) for item in self.registries.requirements.list_active()],
            allowed_actions=self._allowed_actions(bundle, turn),
        )

    @staticmethod
    def _allowed_actions(bundle: ResearchContextCandidateBundle, turn: dict[str, Any]) -> list[ResearchAction]:
        """Advertise only actions that the resolved context can satisfy.

        The validator remains the fail-closed authority.  This bounded
        projection prevents the provider from repeatedly selecting an
        impossible result-only action when the turn has scientific objects but
        no reusable result.
        """

        result_available = bool(bundle.result_candidates)
        continuation_available = (
            result_available or turn.get("parent_turn_id") is not None
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
            stream = ResearchAnswerPublisher(self.repository_factory, prepared.turn)
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
                            "on_answer_delta": stream.feed,
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
                decision = self._normalize_materials_exploration_decision(
                    prepared,
                    decision,
                )
                # ANALYZE is normally a new computation over the selected
                # source.  A provider may echo a historical result key from
                # bounded context, so unrelated recency-derived keys remain
                # invalid for ANALYZE.  An explicitly selected persisted
                # result is different: it is an authoritative UI binding and
                # is required for capabilities that consume a prior result
                # (for example experimental/theoretical XRD comparison).
                # Preserve only those explicit bindings; discard provider
                # echoes from non-explicit history before validation.
                if (
                    decision.action == ResearchAction.ANALYZE
                    and decision.reusable_result_ref_keys
                ):
                    if not set(decision.reusable_result_ref_keys).issubset(
                        prepared.explicit_result_candidate_keys
                    ):
                        decision = decision.model_copy(
                            update={"reusable_result_ref_keys": []}
                        )
                decision = self.validator.validate(
                    decision=decision,
                    input_context=orchestrator_input,
                    candidate_bundle=prepared.bundle,
                    continuation_turn_available=prepared.turn.get("parent_turn_id") is not None,
                )
                decision = self._coalesce_local_environment_requirements(decision)
                if attempt == 1 and not result.repair_attempted:
                    result = result.model_copy(update={"repair_attempted": True})
                stream.finish(decision.assistant_message, action=decision.action.value)
                return result, decision, attempt + 1
            except (InvalidResearchTurnDecision, ValidationError, ValueError) as exc:
                stream.discard()
                first_error = exc
                if attempt == 1:
                    code = exc.code if isinstance(exc, InvalidResearchTurnDecision) else "ORCHESTRATOR_INVALID_OUTPUT"
                    self._fail_if_active(prepared.turn["id"], code, str(exc))
                    raise
            except TimeoutError as exc:
                stream.discard()
                self._fail_if_active(prepared.turn["id"], "ORCHESTRATOR_TIMEOUT", "Orchestrator request timed out")
                raise OrchestratorTimeout("Orchestrator request timed out") from exc
            except LLMProviderError as exc:
                stream.discard()
                if exc.code == "PROVIDER_INVALID_RESPONSE":
                    first_error = ValueError("Provider returned no valid structured object")
                    if attempt == 0:
                        continue
                    self._fail_if_active(prepared.turn["id"], "ORCHESTRATOR_INVALID_OUTPUT", exc.safe_message)
                    raise InvalidResearchTurnDecision(exc.safe_message) from None
                provider_code = "PROVIDER_TIMEOUT" if exc.code in PROVIDER_TIMEOUT_CODES else exc.code
                code = {
                    "PROVIDER_TIMEOUT": "ORCHESTRATOR_TIMEOUT",
                    "PROVIDER_RATE_LIMITED": "ORCHESTRATOR_PROVIDER_RATE_LIMITED",
                    "PROVIDER_AUTH_FAILED": "ORCHESTRATOR_PROVIDER_AUTH_FAILED",
                    "PROVIDER_REQUEST_REJECTED": "ORCHESTRATOR_PROVIDER_REQUEST_REJECTED",
                    "PROVIDER_OUTPUT_TRUNCATED": "ORCHESTRATOR_OUTPUT_TRUNCATED",
                }.get(provider_code, "ORCHESTRATOR_PROVIDER_UNAVAILABLE")
                self._fail_if_active(prepared.turn["id"], code, exc.safe_message)
                if code == "ORCHESTRATOR_TIMEOUT":
                    raise OrchestratorTimeout(exc.safe_message) from exc
                raise OrchestratorProviderUnavailable(exc.safe_message) from exc
        raise AssertionError("unreachable")

    @staticmethod
    def _coalesce_local_environment_requirements(decision: ResearchTurnDecision) -> ResearchTurnDecision:
        """The registered polyhedron suite already runs its exact N1 method.

        Coalesce only validated, unconstrained requirements for the same exact
        source scope and method. Other methods, source sets and parameters stay
        independent; optional geometry cannot replace required coordination.
        """
        covered = {
            (item.requirement_id.replace("inspect_local_environment_", "inspect_coordination_"), frozenset(item.subject_ref_keys))
            for item in decision.scientific_requirements
            if item.requirement_id in {"structure.inspect_local_environment_crystalnn", "structure.inspect_local_environment_voronoi"}
            and item.criticality == RequirementCriticality.REQUIRED
        }
        requirements = [item for item in decision.scientific_requirements
                        if item.constraints or (item.requirement_id, frozenset(item.subject_ref_keys)) not in covered]
        return decision.model_copy(update={"scientific_requirements": requirements})

    @staticmethod
    def _normalize_materials_exploration_decision(
        prepared: PreparedTurn,
        decision: ResearchTurnDecision,
    ) -> ResearchTurnDecision:
        """Keep generic materials exploration requests on their full path.

        A materials dataset/table request that asks to explore, inspect, map,
        or browse the supplied data needs both registered dataset projections:
        composition space and materials explorer.  The provider may otherwise
        choose the unrelated numeric-table suite merely because the source
        happens to contain numeric columns.  This guard is semantic (object
        type plus request class), not qualification-case or exact-question
        matching, and leaves explicit numeric/formula/ML requests untouched.
        """
        if decision.action != ResearchAction.ANALYZE:
            return decision
        message = prepared.user_message.casefold()
        exploration_markers = (
            "explore",
            "inspect",
            "browse",
            "overview",
            "map",
            "supported materials table",
            "materials dataset",
            "materials table",
            "archive",
            "探索",
            "浏览",
            "查看",
            "概览",
            "材料表",
            "数据集",
        )
        specific_analysis_markers = (
            "numeric",
            "correlation",
            "histogram",
            "scatter",
            "regression",
            "classification",
            "uncertainty",
            "formula statistics",
            "chemical-system",
            "化学体系",
            "回归",
            "分类",
            "不确定性",
            "相关性",
            "直方图",
            "散点",
        )
        if not any(marker in message for marker in exploration_markers):
            return decision
        if any(marker in message for marker in specific_analysis_markers):
            return decision

        eligible = [
            item
            for item in prepared.bundle.active_object_candidates
            if item.object_ref is not None
            and item.object_ref.object_type in {"materials.dataset", "materials.table"}
        ]
        if not eligible:
            return decision
        eligible_keys = {item.candidate_key for item in eligible}
        selected = [key for key in decision.selected_scope_ref_keys if key in eligible_keys]
        if not selected and len(eligible) == 1:
            selected = [eligible[0].candidate_key]
        if not selected:
            return decision

        preserved_constraints: dict[str, Any] = {}
        for requirement in decision.scientific_requirements:
            for key in ("property", "sample"):
                if key in requirement.constraints:
                    preserved_constraints[key] = requirement.constraints[key]
        requirements = [
            ProposedRequirement(
                requirement_id="data.explore_composition_space",
                criticality=RequirementCriticality.REQUIRED,
                subject_ref_keys=selected,
                constraints=dict(preserved_constraints),
            ),
            ProposedRequirement(
                requirement_id="data.explore_materials",
                criticality=RequirementCriticality.REQUIRED,
                subject_ref_keys=selected,
                constraints=dict(preserved_constraints),
            ),
        ]
        return decision.model_copy(
            update={
                "selected_scope_ref_keys": selected,
                "scientific_requirements": requirements,
            }
        )

    def _fail_if_active(self, turn_id: UUID, code: str, summary: str) -> None:
        ResearchTurnService(self.repository_factory).fail_if_active(
            turn_id,
            code,
            summary,
            expected_statuses=frozenset({
                ResearchTurnStatus.RECEIVED,
                ResearchTurnStatus.RESOLVING_CONTEXT,
                ResearchTurnStatus.ORCHESTRATING,
            }),
        )

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
