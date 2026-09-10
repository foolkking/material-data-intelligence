from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from mdi_api.application.research.ports import ResearchRepositoryFactoryPort
from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.research_agent.autonomy.assessment import (
    ResearchProgressAssessor,
    semantic_step_signature,
)
from mdi_api.research_agent.autonomy.policy import (
    DEFAULT_AUTONOMY_POLICY,
    CapabilityAutonomyPolicy,
)
from mdi_api.research_agent.autonomy.schemas import (
    AutonomyAdvanceResult,
    AutonomyAssessment,
    AutonomyPolicy,
    AutonomyProgressOutcome,
)
from mdi_api.research_agent.orchestration.queue import AgentTurnQueue
from mdi_api.research_agent.memory.schemas import (
    ContextScope,
    ResearchContextItemType,
)
from mdi_api.research_agent.registry_validation import (
    Agent2Registries,
    DEFAULT_AGENT2_REGISTRIES,
)
from mdi_api.research_agent.schemas import (
    AutonomyMode,
    ResearchTurnEventType,
    ResearchTurnStatus,
    ResearchTurnUIContext,
)
from mdi_api.research_agent.service import ResearchTurnService


logger = logging.getLogger(__name__)


class BoundedAutonomyService:
    """Advance one autonomous branch from its latest durable Result.

    Scientific execution is never performed here. This service records a
    bounded progress assessment and, when justified, creates exactly one child
    ResearchTurn that re-enters the canonical queue-owned lifecycle.
    """

    def __init__(
        self,
        repository_factory: ResearchRepositoryFactoryPort,
        *,
        queue: AgentTurnQueue,
        registries: Agent2Registries = DEFAULT_AGENT2_REGISTRIES,
        assessor: ResearchProgressAssessor | None = None,
    ) -> None:
        self.repository_factory = repository_factory
        self.queue = queue
        self.registries = registries
        self.assessor = assessor or ResearchProgressAssessor()

    def advance_after_interpretation(self, turn_id: UUID) -> AutonomyAdvanceResult | None:
        state = self._load_state(turn_id)
        if state is None:
            return None
        policy = state["policy"]
        existing = state["existing_assessment"]
        if existing is not None:
            assessment = AutonomyAssessment.model_validate(existing)
        else:
            assessment = self._assess(state)
            self._record_assessment(assessment)

        if assessment.outcome != AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS:
            self._record_stop(assessment)
            return AutonomyAdvanceResult(
                turn_id=turn_id,
                outcome=assessment.outcome,
                cycle_index=assessment.cycle_index,
                assessment=assessment,
            )

        child = self._create_child(state, assessment, policy)
        if child.status == ResearchTurnStatus.CANCELED:
            cancelled = assessment.model_copy(
                update={
                    "outcome": AutonomyProgressOutcome.CANCELLED,
                    "selected_capability_id": None,
                    "selected_capability_version": None,
                    "unresolved_requirement_id": None,
                    "semantic_step_signature": None,
                    "reason_codes": ["USER_CANCELLED_AUTONOMOUS_CONTINUATION"],
                }
            )
            self._record_stop(cancelled)
            return AutonomyAdvanceResult(
                turn_id=turn_id,
                outcome=AutonomyProgressOutcome.CANCELLED,
                cycle_index=assessment.cycle_index,
                child_turn_id=child.turn_id,
                enqueued=False,
                assessment=cancelled,
            )
        try:
            queued = self.queue.enqueue_turn(child.turn_id)
        except Exception as exc:
            self._append_event(
                turn_id,
                ResearchTurnEventType.AUTONOMY_QUEUE_PUBLISH_FAILED,
                {
                    "child_turn_id": str(child.turn_id),
                    "cycle_index": assessment.cycle_index + 1,
                    "failure_category": "RETRYABLE",
                    "error_type": type(exc).__name__,
                },
            )
            raise
        self._append_event(
            turn_id,
            ResearchTurnEventType.AUTONOMY_QUEUE_PUBLISHED,
            {
                "child_turn_id": str(child.turn_id),
                "cycle_index": assessment.cycle_index + 1,
                "enqueued": queued.enqueued,
                "queue_backend": queued.backend,
            },
        )
        return AutonomyAdvanceResult(
            turn_id=turn_id,
            outcome=assessment.outcome,
            cycle_index=assessment.cycle_index,
            child_turn_id=child.turn_id,
            enqueued=queued.enqueued,
            assessment=assessment,
        )

    def _load_state(self, turn_id: UUID) -> dict[str, Any] | None:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            status = ResearchTurnStatus(str(turn["status"]))
            if status == ResearchTurnStatus.CANCELED:
                return None
            if status not in {
                ResearchTurnStatus.COMPLETED,
                ResearchTurnStatus.PARTIAL,
            }:
                raise ValueError("autonomy assessment requires a terminal interpreted Turn")
            if session.agent2.interpretations.get_for_turn(turn_id) is None:
                raise ValueError("autonomy assessment requires a durable interpretation")
            current_result_row = session.agent2.scientific_result_snapshots.get_latest_for_turn(
                turn_id
            )
            context_snapshot = (
                session.agent2.research_context_snapshots.get_for_turn(turn_id)
            )
            current_bundle = ScientificResultBundle.model_validate(
                current_result_row["bundle_json"]
            )
            lineage = self._lineage(session, turn)
            autonomy = self._autonomy_payload(session, lineage)
            if autonomy.get("mode") != AutonomyMode.BOUNDED_AUTONOMOUS.value:
                return None
            raw_policy = dict(
                autonomy.get("policy")
                or DEFAULT_AUTONOMY_POLICY.model_dump(
                    mode="json", exclude={"fingerprint"}
                )
            )
            # Compatibility for the first Workstream E snapshots, which
            # accidentally serialized Pydantic's computed fingerprint inside
            # the strict policy object as well as beside it.
            raw_policy.pop("fingerprint", None)
            policy = AutonomyPolicy.model_validate(raw_policy)
            cycle_index = int(autonomy.get("cycle_index") or len(lineage))
            objective = str(autonomy.get("research_objective") or "").strip()
            root_turn = lineage[0]
            if not objective:
                root_message = session.agent2.research_turns.get_message(
                    str(root_turn["user_message_id"])
                )
                objective = str(root_message["content_summary"]).strip()
            completed_bundles: list[ScientificResultBundle] = []
            completed_result_ids: list[UUID] = []
            completed_capability_ids: set[str] = set()
            result_parent_ids: dict[str, tuple[str, ...]] = {}
            llm_decision_calls = 0
            for item in lineage:
                decision = session.agent2.research_turn_decisions.get_for_turn(
                    item["id"]
                )
                if decision is not None and str(decision.get("provider") or "") not in {
                    "",
                    "deterministic_bounded_autonomy",
                }:
                    llm_decision_calls += 1
                capability_plan = (
                    session.agent2.research_capability_plans.get_for_turn(item["id"])
                )
                if capability_plan is not None and capability_plan.get("provider"):
                    llm_decision_calls += 1
                if not session.agent2.scientific_result_snapshots.exists_for_turn(
                    item["id"]
                ):
                    continue
                result_row = (
                    session.agent2.scientific_result_snapshots.get_latest_for_turn(
                        item["id"]
                    )
                )
                item_autonomy = self._turn_autonomy_payload(session, item)
                evidence_parent = item_autonomy.get("evidence_result_id")
                if evidence_parent:
                    result_parent_ids[str(result_row["id"])] = (
                        str(evidence_parent),
                    )
                completed_result_ids.append(result_row["id"])
                bundle = ScientificResultBundle.model_validate(result_row["bundle_json"])
                completed_bundles.append(bundle)
                completed_capability_ids.update(
                    method.capability_id for method in bundle.methods
                )
            events = session.agent2.research_turn_events.list_for_turn(turn_id)
            recorded = next(
                (
                    (event.get("payload_json") or {}).get("assessment")
                    for event in events
                    if event["event_type"]
                    == ResearchTurnEventType.AUTONOMY_ASSESSMENT_RECORDED.value
                    and (event.get("payload_json") or {}).get("assessment")
                ),
                None,
            )
            signatures = {
                str((event.get("payload_json") or {}).get("semantic_step_signature"))
                for item in lineage
                for event in session.agent2.research_turn_events.list_for_turn(item["id"])
                if event["event_type"]
                == ResearchTurnEventType.AUTONOMY_ASSESSMENT_RECORDED.value
                and (event.get("payload_json") or {}).get("semantic_step_signature")
            }
            capability_execution_count = sum(
                len(bundle.methods) for bundle in completed_bundles
            )
            return {
                "turn": turn,
                "lineage": lineage,
                "root_turn_id": root_turn["id"],
                "autonomy": autonomy,
                "policy": policy,
                "cycle_index": cycle_index,
                "objective": objective,
                "current_result_row": current_result_row,
                "current_bundle": current_bundle,
                "context_snapshot": context_snapshot,
                "completed_result_ids": completed_result_ids,
                "completed_bundles": completed_bundles,
                "result_parent_ids": result_parent_ids,
                "completed_capability_ids": completed_capability_ids,
                "capability_execution_count": capability_execution_count,
                "llm_decision_calls": llm_decision_calls,
                "semantic_signatures": signatures,
                "existing_assessment": recorded,
            }

    def _assess(self, state: dict[str, Any]) -> AutonomyAssessment:
        policy: AutonomyPolicy = state["policy"]
        current: ScientificResultBundle = state["current_bundle"]
        cycle_index = int(state["cycle_index"])
        completed = set(state["completed_capability_ids"])
        base = self.assessor.assess(
            objective=state["objective"],
            current=current,
            completed_capability_ids=completed,
            completed_bundles=state["completed_bundles"],
            completed_result_ids=state["completed_result_ids"],
            result_parent_ids=state["result_parent_ids"],
        )
        outcome = base.outcome
        reason_codes = list(base.reason_codes)
        capability_id = base.capability_id
        requirement_id = base.requirement_id
        qualification = None
        limitations = list(base.limitations)
        signature = None
        selected_parameters = dict(base.parameter_dict)

        if cycle_index >= policy.max_cycles:
            outcome = AutonomyProgressOutcome.BUDGET_EXHAUSTED
            reason_codes = ["AUTONOMY_CYCLE_LIMIT_REACHED"]
            capability_id = None
            requirement_id = None
            selected_parameters = {}
        elif state["capability_execution_count"] >= policy.max_capability_executions:
            outcome = AutonomyProgressOutcome.BUDGET_EXHAUSTED
            reason_codes = ["AUTONOMY_EXECUTION_LIMIT_REACHED"]
            capability_id = None
            requirement_id = None
            selected_parameters = {}
        elif state["llm_decision_calls"] >= policy.max_llm_decision_calls:
            outcome = AutonomyProgressOutcome.BUDGET_EXHAUSTED
            reason_codes = ["AUTONOMY_LLM_DECISION_LIMIT_REACHED"]
            capability_id = None
            requirement_id = None
            selected_parameters = {}
        elif capability_id is not None:
            manifest = self.registries.capabilities.require(capability_id, "1.0")
            qualification = CapabilityAutonomyPolicy(policy).qualification_snapshot(
                manifest
            )
            limitations.extend(qualification.known_limitations)
            if not qualification.allowed_for_autonomy:
                outcome = AutonomyProgressOutcome.NO_QUALIFIED_CAPABILITY
                reason_codes = [qualification.reason_code]
                capability_id = None
                requirement_id = None
                selected_parameters = {}
            else:
                signature = semantic_step_signature(
                    capability_id=base.capability_id,
                    source_version_ids=[
                        str(ref.version_id) for ref in current.source_object_refs
                    ],
                    parameters=selected_parameters,
                )
                if signature in state["semantic_signatures"]:
                    outcome = AutonomyProgressOutcome.NON_PROGRESS
                    reason_codes = ["DUPLICATE_SEMANTIC_STEP_PREVENTED"]
                    capability_id = None
                    requirement_id = None
                    selected_parameters = {}

        return AutonomyAssessment(
            research_turn_id=state["turn"]["id"],
            root_turn_id=state["root_turn_id"],
            cycle_index=cycle_index,
            research_objective=state["objective"],
            outcome=outcome,
            evidence_result_ids=list(state["completed_result_ids"])[-16:],
            completed_capability_ids=sorted(completed),
            unresolved_requirement_id=requirement_id,
            selected_capability_id=capability_id,
            selected_capability_version="1.0" if capability_id else None,
            selected_parameters=selected_parameters,
            qualification=qualification,
            exact_source_version_ids=sorted(
                {
                    ref.version_id
                    for bundle in state["completed_bundles"]
                    for ref in [
                        *bundle.source_object_refs,
                        *bundle.output_object_refs,
                    ]
                },
                key=str,
            ),
            context_snapshot_id=(
                state["context_snapshot"].get("id")
                if state["context_snapshot"]
                else None
            ),
            context_snapshot_fingerprint=(
                state["context_snapshot"].get("context_fingerprint")
                if state["context_snapshot"]
                else None
            ),
            semantic_step_signature=signature,
            reason_codes=reason_codes,
            limitations=sorted(set(limitations))[:16],
            strategy_decision=base.strategy_decision,
            strategy_summary=base.strategy_summary,
            policy_version=policy.version,
            policy_fingerprint=policy.fingerprint,
        )

    def _create_child(
        self,
        state: dict[str, Any],
        assessment: AutonomyAssessment,
        policy: AutonomyPolicy,
    ) -> Any:
        source_refs = []
        seen_source_versions: set[UUID] = set()
        for bundle in state["completed_bundles"]:
            for ref in [*bundle.source_object_refs, *bundle.output_object_refs]:
                if ref.version_id in seen_source_versions:
                    continue
                seen_source_versions.add(ref.version_id)
                source_refs.append(ref)
        assessment_payload = assessment.model_dump(mode="json")
        assessment_signature = hashlib.sha256(
            json.dumps(
                assessment_payload, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        autonomy = {
            "mode": AutonomyMode.BOUNDED_AUTONOMOUS.value,
            "root_turn_id": str(assessment.root_turn_id),
            "cycle_index": assessment.cycle_index + 1,
            "research_objective": assessment.research_objective,
            "subgoal": assessment.unresolved_requirement_id,
            "selected_capability_id": assessment.selected_capability_id,
            "selected_capability_version": assessment.selected_capability_version,
            "constraints": assessment.selected_parameters,
            "requirement_id": assessment.unresolved_requirement_id,
            "evidence_result_id": str(assessment.evidence_result_ids[-1]),
            "source_version_ids": [
                str(value) for value in assessment.exact_source_version_ids
            ],
            "semantic_step_signature": assessment.semantic_step_signature,
            "assessment_signature": assessment_signature,
            "strategy": (
                assessment.strategy_summary.model_dump(mode="json")
                if assessment.strategy_summary
                else None
            ),
            "qualification": (
                assessment.qualification.model_dump(mode="json")
                if assessment.qualification
                else None
            ),
            "policy": policy.model_dump(mode="json", exclude={"fingerprint"}),
            "policy_version": policy.version,
            "policy_fingerprint": policy.fingerprint,
        }
        message = (
            "自动研究子目标：在保留既有科学结果与精确来源版本的前提下，"
            f"完成需求 {assessment.unresolved_requirement_id}；"
            f"仅使用能力 {assessment.selected_capability_id}，不得扩大原始研究目标。"
        )
        return ResearchTurnService(self.repository_factory).receive_autonomous_turn(
            project_id=str(state["turn"]["project_id"]),
            session_id=str(state["turn"]["research_session_id"]),
            parent_turn_id=state["turn"]["id"],
            message=message,
            ui_context=ResearchTurnUIContext(
                active_object_refs=source_refs,
                selection_refs=source_refs,
                explicit_object_refs=source_refs,
                explicit_result_ids=[assessment.evidence_result_ids[-1]],
            ),
            autonomy=autonomy,
        )

    def _record_assessment(self, assessment: AutonomyAssessment) -> None:
        payload = {
            "assessment": assessment.model_dump(mode="json"),
            "cycle_index": assessment.cycle_index,
            "outcome": assessment.outcome.value,
            "selected_capability_id": assessment.selected_capability_id,
            "semantic_step_signature": assessment.semantic_step_signature,
            "policy_version": assessment.policy_version,
            "policy_fingerprint": assessment.policy_fingerprint,
            "strategy": (
                assessment.strategy_summary.model_dump(mode="json")
                if assessment.strategy_summary
                else None
            ),
        }
        with self.repository_factory.unit_of_work() as unit:
            self._event(
                unit,
                assessment.research_turn_id,
                ResearchTurnEventType.AUTONOMY_ASSESSMENT_RECORDED,
                payload,
            )
            turn = unit.agent2.research_turns.get(assessment.research_turn_id)
            memory_items = unit.agent2.research_session_memory.list_items(
                str(turn["research_session_id"])
            )
            memory_identity = (
                f"autonomy-assessment:{assessment.research_turn_id}:"
                f"{assessment.cycle_index}"
            )
            if not any(
                memory_identity
                in set((item.get("ref_json") or {}).get("provenance_refs") or [])
                for item in memory_items
            ):
                unit.agent2.research_session_memory.add_item(
                    {
                        "id": uuid4(),
                        "session_id": str(turn["research_session_id"]),
                        "project_id": str(turn["project_id"]),
                        "item_type": ResearchContextItemType.PRIOR_FINDING.value,
                        "scope": ContextScope.TURN.value,
                        "ref_json": {
                            "authority_class": "MEMORY",
                            "epistemic_status": "DECISION",
                            "freshness": "CURRENT",
                            "result_ids": [
                                str(value) for value in assessment.evidence_result_ids
                            ],
                            "capability_ids": assessment.completed_capability_ids,
                            "outcome": assessment.outcome.value,
                            "strategy_action": (
                                assessment.strategy_decision.action.value
                                if assessment.strategy_decision
                                else None
                            ),
                            "question_id": (
                                assessment.strategy_decision.current_question_id
                                if assessment.strategy_decision
                                else None
                            ),
                            "evidence_gap_id": (
                                assessment.strategy_decision.evidence_gap.gap_id
                                if assessment.strategy_decision
                                and assessment.strategy_decision.evidence_gap
                                else None
                            ),
                            "hypothesis_id": (
                                assessment.strategy_decision.hypothesis.hypothesis_id
                                if assessment.strategy_decision
                                and assessment.strategy_decision.hypothesis
                                else None
                            ),
                            "provenance_refs": [
                                memory_identity,
                                *(
                                    f"result:{value}"
                                    for value in assessment.evidence_result_ids
                                ),
                            ],
                        },
                        "statement": self._memory_statement(assessment),
                        "structured_constraint_json": None,
                        "source_message_id": None,
                        "explicitly_requested": False,
                        "active": True,
                        "version": 1,
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc),
                    }
                )
            hypothesis = (
                assessment.strategy_decision.hypothesis
                if assessment.strategy_decision
                else None
            )
            if hypothesis is not None:
                hypothesis_identity = (
                    f"strategy-hypothesis:{assessment.research_turn_id}:"
                    f"{hypothesis.hypothesis_id}"
                )
                if not any(
                    hypothesis_identity
                    in set(
                        (item.get("ref_json") or {}).get("provenance_refs")
                        or []
                    )
                    for item in memory_items
                ):
                    unit.agent2.research_session_memory.add_item(
                        {
                            "id": uuid4(),
                            "session_id": str(turn["research_session_id"]),
                            "project_id": str(turn["project_id"]),
                            "item_type": ResearchContextItemType.OPEN_QUESTION.value,
                            "scope": ContextScope.TURN.value,
                            "ref_json": {
                                "authority_class": "MEMORY",
                                "epistemic_status": "HYPOTHESIS",
                                "freshness": "CURRENT",
                                "hypothesis_id": hypothesis.hypothesis_id,
                                "hypothesis_status": hypothesis.status.value,
                                "question_id": hypothesis.question_id,
                                "result_ids": [
                                    str(value)
                                    for value in hypothesis.supporting_result_ids
                                ],
                                "provenance_refs": [
                                    hypothesis_identity,
                                    *(
                                        f"result:{value}"
                                        for value in hypothesis.supporting_result_ids
                                    ),
                                ],
                            },
                            "statement": hypothesis.statement,
                            "structured_constraint_json": None,
                            "source_message_id": None,
                            "explicitly_requested": False,
                            "active": True,
                            "version": 1,
                            "created_at": datetime.now(timezone.utc),
                            "updated_at": datetime.now(timezone.utc),
                        }
                    )

    def _record_stop(self, assessment: AutonomyAssessment) -> None:
        with self.repository_factory.unit_of_work() as unit:
            events = unit.agent2.research_turn_events.list_for_turn(
                assessment.research_turn_id
            )
            if any(
                event["event_type"] == ResearchTurnEventType.AUTONOMY_STOPPED.value
                for event in events
            ):
                return
            self._event(
                unit,
                assessment.research_turn_id,
                ResearchTurnEventType.AUTONOMY_STOPPED,
                {
                    "cycle_index": assessment.cycle_index,
                    "stop_reason": assessment.outcome.value,
                    "reason_codes": assessment.reason_codes,
                    "limitations": assessment.limitations[:8],
                    "evidence_result_ids": [
                        str(value) for value in assessment.evidence_result_ids
                    ],
                    "completed_capability_ids": assessment.completed_capability_ids,
                    "policy_version": assessment.policy_version,
                    "policy_fingerprint": assessment.policy_fingerprint,
                },
            )

    def _append_event(
        self,
        turn_id: UUID,
        event_type: ResearchTurnEventType,
        payload: dict[str, Any],
    ) -> None:
        with self.repository_factory.unit_of_work() as unit:
            self._event(unit, turn_id, event_type, payload)

    @staticmethod
    def _event(
        unit: Any,
        turn_id: UUID,
        event_type: ResearchTurnEventType,
        payload: dict[str, Any],
    ) -> None:
        unit.agent2.research_turn_events.append_turn_event(
            {
                "id": uuid4(),
                "turn_id": turn_id,
                "sequence_no": unit.agent2.research_turn_events.next_sequence_no(
                    turn_id
                ),
                "event_type": event_type.value,
                "payload_json": payload,
                "created_at": datetime.now(timezone.utc),
            }
        )

    @staticmethod
    def _lineage(session: Any, turn: dict[str, Any]) -> list[dict[str, Any]]:
        lineage = [turn]
        seen = {turn["id"]}
        current = turn
        for _ in range(8):
            parent_id = current.get("parent_turn_id")
            if parent_id is None or parent_id in seen:
                break
            current = session.agent2.research_turns.get(parent_id)
            lineage.append(current)
            seen.add(current["id"])
        return list(reversed(lineage))

    @staticmethod
    def _autonomy_payload(session: Any, lineage: list[dict[str, Any]]) -> dict[str, Any]:
        for turn in reversed(lineage):
            for event in session.agent2.research_turn_events.list_for_turn(turn["id"]):
                if event["event_type"] != ResearchTurnEventType.TURN_RECEIVED.value:
                    continue
                autonomy = (event.get("payload_json") or {}).get("autonomy") or {}
                if autonomy:
                    return dict(autonomy)
        return {"mode": AutonomyMode.STANDARD.value}

    @staticmethod
    def _turn_autonomy_payload(
        session: Any, turn: dict[str, Any]
    ) -> dict[str, Any]:
        for event in session.agent2.research_turn_events.list_for_turn(turn["id"]):
            if event["event_type"] != ResearchTurnEventType.TURN_RECEIVED.value:
                continue
            autonomy = (event.get("payload_json") or {}).get("autonomy") or {}
            if autonomy:
                return dict(autonomy)
        return {}

    @staticmethod
    def _memory_statement(assessment: AutonomyAssessment) -> str:
        if assessment.outcome == AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS:
            return (
                f"Cycle {assessment.cycle_index} retained durable Results and "
                f"selected {assessment.selected_capability_id} for unresolved "
                f"requirement {assessment.unresolved_requirement_id}."
            )
        return (
            f"Cycle {assessment.cycle_index} stopped with "
            f"{assessment.outcome.value}; completed scientific Results remain "
            "the evidence authority."
        )


__all__ = ["BoundedAutonomyService"]
