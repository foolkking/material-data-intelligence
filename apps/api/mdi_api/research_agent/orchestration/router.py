from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from mdi_api.agent2_errors import ConcurrentTurnModification, UnauthorizedScientificObjectReference
from mdi_api.application.research.ports import ResearchRepositoryFactoryPort
from mdi_api.research_agent.context.schemas import ResearchContextCandidateBundle
from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.orchestration.schemas import (
    ActionRoutingResult,
    DownstreamDispatchStatus,
    ResearchTurnDecision,
)
from mdi_api.research_agent.schemas import ResearchAction, ResearchTurnEventType, ResearchTurnStatus


class ResearchActionRouter:
    def __init__(self, repository_factory: ResearchRepositoryFactoryPort) -> None:
        self.repository_factory = repository_factory

    def apply(
        self,
        *,
        turn_id: UUID,
        expected_version: int,
        decision: ResearchTurnDecision,
        candidate_bundle: ResearchContextCandidateBundle,
        provider_result: StructuredLLMResult,
    ) -> ActionRoutingResult:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            existing = unit.agent2.research_turn_decisions.get_for_turn(turn_id)
            if existing is not None:
                raise ConcurrentTurnModification(f"ResearchTurn already has decision: {turn_id}")
            if turn["status"] != ResearchTurnStatus.ORCHESTRATING.value or int(turn["row_version"]) != expected_version:
                raise ConcurrentTurnModification(str(turn_id))
            self._reauthorize(unit, str(turn["project_id"]), decision, candidate_bundle)

            target_status, dispatch_status, message_slot, message_kind = self._routing_shape(decision.action)
            assistant_content = self._assistant_content(decision, candidate_bundle)
            message_id = None
            if assistant_content:
                message_id = f"message_{uuid4().hex}"
                unit.agent2.research_turns.add_message({
                    "id": message_id,
                    "session_id": turn["research_session_id"],
                    "role": "agent",
                    "content_summary": assistant_content,
                    "payload_json": {
                        "source": "agent2_research_orchestration",
                        "messageKind": message_kind,
                        "turnId": str(turn_id),
                        "decisionContractVersion": decision.contract_version,
                    },
                    "created_at": datetime.now(timezone.utc),
                })

            continuation_of_turn_id = self._continuation_turn(unit, decision, candidate_bundle)
            completed_at = datetime.now(timezone.utc) if target_status in {
                ResearchTurnStatus.ANSWERED,
                ResearchTurnStatus.NEEDS_CLARIFICATION,
            } else None
            decision_id = uuid4()
            unit.agent2.research_turn_decisions.add({
                "id": decision_id,
                "research_turn_id": turn_id,
                "contract_version": decision.contract_version,
                "action": decision.action.value,
                "decision_json": decision.model_dump(mode="json"),
                "input_context_fingerprint": self._context_fingerprint(unit, turn_id),
                "prompt_version": provider_result.prompt_version,
                "provider": provider_result.provider,
                "model": provider_result.model,
                "provider_request_id": provider_result.provider_request_id,
                "repair_attempted": provider_result.repair_attempted,
                "validation_status": "VALIDATED",
                "action_dispatch_status": dispatch_status.value,
                "created_at": datetime.now(timezone.utc),
            })
            updated = unit.agent2.research_turns.apply_decision_projection(
                turn_id,
                expected_version=expected_version,
                action_type=decision.action.value,
                target_status=target_status.value,
                assistant_pre_message_id=message_id if message_slot == "pre" else None,
                assistant_final_message_id=message_id if message_slot == "final" else None,
                continuation_of_turn_id=continuation_of_turn_id,
                completed_at=completed_at,
            )
            self._append_event(unit, turn_id, ResearchTurnEventType.ORCHESTRATION_COMPLETED, {
                "action": decision.action.value,
                "dispatch_status": dispatch_status.value,
            })
            if decision.action == ResearchAction.ANSWER:
                self._append_event(unit, turn_id, ResearchTurnEventType.DIRECT_ANSWER_READY, {
                    "message_id": message_id,
                    "content": assistant_content,
                    "status": target_status.value,
                })
                self._append_event(unit, turn_id, ResearchTurnEventType.TURN_COMPLETED, {"status": target_status.value})
            elif decision.action == ResearchAction.CLARIFY:
                self._append_event(unit, turn_id, ResearchTurnEventType.CLARIFICATION_REQUESTED, {
                    "message_id": message_id,
                    "content": assistant_content,
                    "candidate_keys": decision.clarification.candidate_keys,
                    "status": target_status.value,
                })
            elif decision.action in {ResearchAction.ANALYZE, ResearchAction.CONTINUE_ANALYSIS}:
                self._append_event(unit, turn_id, ResearchTurnEventType.PLAN_REQUESTED, {
                    "message_id": message_id,
                    "content": assistant_content,
                    "status": target_status.value,
                })
        return ActionRoutingResult(
            action=decision.action,
            turn_status=str(updated["status"]),
            dispatch_status=dispatch_status,
            assistant_message_id=message_id,
        )

    @staticmethod
    def _routing_shape(action: ResearchAction) -> tuple[ResearchTurnStatus, DownstreamDispatchStatus, str | None, str]:
        if action == ResearchAction.ANSWER:
            return ResearchTurnStatus.ANSWERED, DownstreamDispatchStatus.COMPLETED, "final", "ASSISTANT_FINAL"
        if action == ResearchAction.CLARIFY:
            return ResearchTurnStatus.NEEDS_CLARIFICATION, DownstreamDispatchStatus.COMPLETED, "final", "CLARIFICATION"
        # A query-only request is a completed conversational handoff to the
        # Data Platform, not scientific execution.  Leaving it in
        # ORCHESTRATING with no downstream consumer strands the ResearchTurn
        # forever and gives the browser a false "preparing analysis" state.
        if action == ResearchAction.QUERY_DATA:
            return ResearchTurnStatus.ANSWERED, DownstreamDispatchStatus.COMPLETED, "final", "QUERY_DATA_ACK"
        if action in {ResearchAction.ANALYZE, ResearchAction.CONTINUE_ANALYSIS}:
            return ResearchTurnStatus.READY_TO_PLAN, DownstreamDispatchStatus.READY_FOR_DOWNSTREAM, "pre", "ASSISTANT_PRE_RUN"
        return ResearchTurnStatus.ORCHESTRATING, DownstreamDispatchStatus.READY_FOR_DOWNSTREAM, "pre", "DOWNSTREAM_ACKNOWLEDGEMENT"

    @staticmethod
    def _assistant_content(
        decision: ResearchTurnDecision,
        candidate_bundle: ResearchContextCandidateBundle,
    ) -> str | None:
        if decision.action == ResearchAction.CLARIFY:
            return decision.clarification.question
        if decision.action == ResearchAction.QUERY_DATA:
            projection = ResearchActionRouter._query_data_projection(
                decision,
                candidate_bundle,
            )
            if projection:
                return projection
            if decision.assistant_message:
                return decision.assistant_message
            return "已识别为数据查询请求。请在数据平台查看或调整筛选条件；本次未创建科学分析运行。"
        if decision.action == ResearchAction.INTERPRET_RESULT:
            # The orchestrator only selects the exact reusable Result. It is
            # not scientific authority and must not place an ungrounded
            # interpretation candidate into the conversation before the
            # grounded interpreter runs.
            return "已找到可复用的精确科学结果，正在基于其权威事实重新组织解释；不会重新计算科学结果。"
        return decision.assistant_message

    @staticmethod
    def _query_data_projection(
        decision: ResearchTurnDecision,
        candidate_bundle: ResearchContextCandidateBundle,
    ) -> str | None:
        """Answer a read-only data query from the bounded object projection.

        QUERY_DATA remains non-executing: it must not create a plan, job, or
        result.  When the selected object already carries a bounded semantic
        projection, however, returning only a generic hand-off is misleading
        and leaves the user without the facts they explicitly requested.
        This formatter is deliberately deterministic and only exposes the
        metadata projection assembled for the exact selected object/version.
        """
        selected = set(decision.selected_scope_ref_keys)
        candidates = [
            item for item in candidate_bundle.active_object_candidates
            if item.candidate_key in selected and item.semantic_summary
        ]
        if not candidates:
            return None

        rendered: list[str] = []
        for candidate in candidates[:4]:
            try:
                summary = json.loads(candidate.semantic_summary or "")
            except (TypeError, ValueError):
                continue
            metadata = summary.get("canonical_metadata")
            if not isinstance(metadata, dict) or not metadata:
                continue
            known_keys = (
                "row_count", "nRows", "nColumns", "columns", "frameCount",
                "atomCount", "timeStartPs", "timeEndPs", "timeUnit", "pbc",
                "positionWrapping", "qPointCount", "branchCount", "bandCount",
                "kpointCount", "spinMode", "energyUnit", "energyReference",
                "fermiAvailable", "gridShape", "fieldKind", "unit",
                "experimentalXrd",
            )
            if not any(key in metadata for key in known_keys):
                continue
            lines = [f"只基于已选择对象 {candidate.display_label} 的有界元数据："]
            if "row_count" in metadata or "nRows" in metadata:
                lines.append(f"- 行数：{metadata.get('row_count', metadata.get('nRows'))}")
            if "nColumns" in metadata:
                lines.append(f"- 列数：{metadata['nColumns']}")
            columns = metadata.get("columns")
            if isinstance(columns, list) and columns:
                descriptions = []
                for column in columns[:16]:
                    if not isinstance(column, dict):
                        continue
                    name = column.get("name")
                    if not name:
                        continue
                    details = [str(name)]
                    if column.get("dtype") is not None:
                        details.append(f"type={column['dtype']}")
                    if column.get("unit") is not None:
                        details.append(f"unit={column['unit']}")
                    if column.get("missingCount") is not None:
                        details.append(f"missing={column['missingCount']}")
                    if column.get("uniqueCount") is not None:
                        details.append(f"unique={column['uniqueCount']}")
                    descriptions.append(" ".join(details))
                if descriptions:
                    lines.append("- 暴露列：" + "；".join(descriptions))
            for key in known_keys:
                if key in metadata and not isinstance(metadata[key], (dict, list)):
                    lines.append(f"- {key}：{metadata[key]}")
            experimental_xrd = metadata.get("experimentalXrd")
            if isinstance(experimental_xrd, dict):
                xrd_fields = (
                    ("resourceId", "资源 ID"),
                    ("resourceVersion", "资源版本"),
                    ("resourceHash", "资源哈希"),
                    ("pointCount", "测量点数"),
                    ("axisMonotonicity", "横轴单调性"),
                    ("intensitySemantic", "强度语义"),
                )
                for key, label in xrd_fields:
                    if experimental_xrd.get(key) is not None:
                        lines.append(f"- XRD {label}：{experimental_xrd[key]}")
                axis = experimental_xrd.get("xAxis")
                if isinstance(axis, dict):
                    lines.append(
                        f"- XRD 横轴：{axis.get('kind', 'unknown')} "
                        f"（{axis.get('unit', 'unknown')}）"
                    )
                wavelength = experimental_xrd.get("wavelength")
                if isinstance(wavelength, dict):
                    lines.append(
                        f"- XRD 波长：{wavelength.get('value', 'unknown')} "
                        f"{wavelength.get('unit', '')}".rstrip()
                    )
            if len(lines) == 1:
                compact = json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                lines.append(f"- 有界元数据：{compact[:1200]}")
            lines.append("- 当前投影未暴露逐行身份或更多字段；不据此推断物理因果。")
            rendered.append("\n".join(lines))
        return "\n\n".join(rendered) if rendered else None

    @staticmethod
    def _context_fingerprint(unit: Any, turn_id: UUID) -> str:
        snapshot = unit.agent2.research_context_snapshots.get_for_turn(turn_id)
        if snapshot is None:
            raise ConcurrentTurnModification("ResearchTurn context snapshot is missing")
        return str(snapshot["context_fingerprint"])

    @staticmethod
    def _continuation_turn(unit: Any, decision: ResearchTurnDecision, bundle: ResearchContextCandidateBundle) -> UUID | None:
        if decision.action != ResearchAction.CONTINUE_ANALYSIS or not decision.reusable_result_ref_keys:
            return None
        results = {item.candidate_key: item for item in bundle.result_candidates}
        candidate = results[decision.reusable_result_ref_keys[0]]
        snapshot = unit.agent2.scientific_result_snapshots.get(candidate.result_id)
        return snapshot["research_turn_id"]

    @staticmethod
    def _reauthorize(unit: Any, project_id: str, decision: ResearchTurnDecision, bundle: ResearchContextCandidateBundle) -> None:
        objects = {item.candidate_key: item for item in bundle.active_object_candidates}
        results = {item.candidate_key: item for item in bundle.result_candidates}
        object_keys = set(decision.selected_scope_ref_keys)
        object_keys.update(key for requirement in decision.scientific_requirements for key in requirement.subject_ref_keys)
        for key in object_keys:
            candidate = objects[key]
            logical = unit.agent2.scientific_objects.get_object(candidate.object_ref.object_id)
            version = unit.agent2.scientific_objects.get_version(candidate.object_ref.version_id)
            if (
                str(logical["project_id"]) != project_id
                or version["scientific_object_id"] != candidate.object_ref.object_id
                or str(version["object_type"]) != candidate.object_ref.object_type
            ):
                raise UnauthorizedScientificObjectReference(key)
        for key in decision.reusable_result_ref_keys:
            snapshot = unit.agent2.scientific_result_snapshots.get(results[key].result_id)
            if str(snapshot["project_id"]) != project_id:
                raise UnauthorizedScientificObjectReference(key)

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
