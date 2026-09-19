from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import ValidationError

from mdi_api.agent2_errors import ScientificResultSnapshotNotFound
from mdi_api.research_agent.schemas import ResearchAction, ResearchTurnEventType, ResearchTurnStatus
from mdi_api.research_agent.context.manifest import build_operation_manifest
from mdi_api.research_agent.context.policy import ContextOperation
from mdi_api.research_agent.turns.state_machine import ensure_transition
from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.unit_of_work import RepositoryFactory

from mdi_api.application.interpretation.assembler import InterpreterInputAssembler, effective_relevance
from mdi_api.infrastructure.interpretation.client import DeepSeekInterpreterClient, PROMPT_VERSION, StructuredInterpreterClient
from mdi_api.application.interpretation.grounding import (
    build_grounding_repair_context,
    project_grounded_answer_lead,
    project_claim_support_assessments,
    project_grounded_communication,
    validate_interpretation,
)
from mdi_api.application.interpretation.projector import AssistantResponseProjector
from mdi_api.domain.interpretation.contracts import ScientificInterpretationOutput


logger = logging.getLogger(__name__)


class ScientificInterpretationService:
    """Phase 6 orchestration with a strict transaction/provider boundary."""

    contract_version = "1.0"

    def __init__(self, repository_factory: RepositoryFactory, *, client: StructuredInterpreterClient | None = None, timeout_seconds: float = 120.0) -> None:
        self.repository_factory = repository_factory
        self.client = client or DeepSeekInterpreterClient()
        self.timeout_seconds = timeout_seconds
        self.assembler = InterpreterInputAssembler()
        self.response_projector = AssistantResponseProjector()

    def process_turn(self, turn_id: UUID) -> dict[str, Any]:
        claimed = self._claim(turn_id)
        if claimed.get("existing") is not None:
            return claimed["existing"]
        try:
            bundle, snapshot, question, relevance, envelope, fingerprint = self._load_input(turn_id)
            self._record_interpreter_manifest(
                turn_id=turn_id,
                bundle=bundle,
                snapshot=snapshot,
                question=question,
                envelope=envelope,
                context_fingerprint=fingerprint,
            )
            result, repair_attempted, provider_meta = self._generate_with_one_repair(
                envelope,
                bundle,
                turn_id=turn_id,
            )
            content = self.response_projector.project(result, bundle, effective_relevance=relevance)
            return self._persist(
                turn_id,
                snapshot_id=snapshot["id"],
                project_id=str(snapshot["project_id"]),
                fingerprint=fingerprint,
                result=result,
                content=content,
                provider_meta=provider_meta,
                repair_attempted=repair_attempted,
                bundle=bundle,
            )
        except InterpretationFailure as exc:
            self._fail(turn_id, exc.code, str(exc))
            raise
        except Exception:
            self._fail(turn_id, "INTERPRETATION_PROVIDER_FAILED", "科学结果已生成，但自动解释未完成。")
            raise

    def _generate_with_one_repair(
        self,
        envelope: Any,
        bundle: ScientificResultBundle,
        *,
        turn_id: UUID | None = None,
    ) -> tuple[ScientificInterpretationOutput, bool, dict[str, Any]]:
        repair_errors: list[str] | None = None
        for attempt in range(2):
            try:
                result, _, provider_meta = self._generate(
                    envelope,
                    bundle=bundle,
                    repair_errors=repair_errors,
                    repair_attempted=attempt == 1,
                    turn_id=turn_id,
                )
            except ValidationError as exc:
                if attempt == 0:
                    repair_errors = [str(error) for error in exc.errors()][:16]
                    continue
                raise InterpretationFailure("INTERPRETATION_SCHEMA_INVALID", "解释输出未通过结构化 schema 校验。") from exc
            except Exception as exc:
                if attempt == 0 and self._is_repairable_provider_output_error(exc):
                    repair_errors = [
                        f"{getattr(exc, 'code', type(exc).__name__)}: {exc}"
                    ]
                    continue
                raise InterpretationFailure("INTERPRETATION_PROVIDER_FAILED", "科学结果已生成，但自动解释未完成。") from exc
            result = project_grounded_answer_lead(result, bundle)
            result = project_claim_support_assessments(result, bundle)
            result = project_grounded_communication(result, bundle)
            validation = validate_interpretation(result, bundle)
            if validation.valid:
                return result, attempt == 1, provider_meta
            if attempt == 0:
                repair_errors = build_grounding_repair_context(
                    result,
                    bundle,
                    validation.errors,
                )
                continue
            raise InterpretationFailure("INTERPRETATION_GROUNDING_FAILED", "; ".join(validation.errors)[:1000])
        raise InterpretationFailure("INTERPRETATION_SCHEMA_INVALID", "解释输出未通过结构化 schema 校验。")

    @staticmethod
    def _is_repairable_provider_output_error(error: Exception) -> bool:
        """Retry only malformed structured output, not transport failures."""

        return str(getattr(error, "code", "")).upper() in {
            "DEEPSEEK_RESPONSE_INVALID",
            "OPENAI_RESPONSE_INVALID",
            "PROVIDER_RESPONSE_INVALID",
        }

    def _claim(self, turn_id: UUID) -> dict[str, Any]:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            existing = unit.agent2.interpretations.get_for_turn(turn_id)
            if existing is not None:
                return {"existing": existing}
            status = ResearchTurnStatus(str(turn["status"]))
            if status == ResearchTurnStatus.RESULT_READY:
                ensure_transition(status, ResearchTurnStatus.INTERPRETING)
                updated = unit.agent2.research_turns.compare_and_set_status(turn_id, expected_status=status.value, expected_version=int(turn["row_version"]), target_status=ResearchTurnStatus.INTERPRETING.value)
                self._event(unit, turn_id, ResearchTurnEventType.INTERPRETATION_STARTED, {"status": updated["status"]})
                return {"turn": updated, "provider_meta": {}}
            if status == ResearchTurnStatus.ORCHESTRATING and str(turn.get("action_type")) == ResearchAction.INTERPRET_RESULT.value:
                ensure_transition(status, ResearchTurnStatus.INTERPRETING)
                updated = unit.agent2.research_turns.compare_and_set_status(turn_id, expected_status=status.value, expected_version=int(turn["row_version"]), target_status=ResearchTurnStatus.INTERPRETING.value)
                self._event(unit, turn_id, ResearchTurnEventType.INTERPRETATION_STARTED, {"status": updated["status"], "existing_result": True})
                return {"turn": updated, "provider_meta": {}}
            if status == ResearchTurnStatus.INTERPRETING:
                started = turn.get("updated_at")
                if started is not None:
                    if started.tzinfo is None:
                        started = started.replace(tzinfo=timezone.utc)
                    age_seconds = (datetime.now(timezone.utc) - started).total_seconds()
                else:
                    age_seconds = 0
                if age_seconds > 900:
                    updated = unit.agent2.research_turns.compare_and_set_status(
                        turn_id,
                        expected_status=status.value,
                        expected_version=int(turn["row_version"]),
                        target_status=ResearchTurnStatus.INTERPRETING.value,
                    )
                    self._event(unit, turn_id, ResearchTurnEventType.INTERPRETATION_STARTED, {"status": updated["status"], "reclaimed": True})
                    return {"turn": updated, "provider_meta": {}}
                raise InterpretationFailure("INTERPRETATION_IN_PROGRESS", "interpretation is already in progress")
            if status == ResearchTurnStatus.FAILED:
                error_code = str(turn.get("error_code") or "")
                if not error_code.startswith("INTERPRETATION_"):
                    raise InterpretationFailure(
                        "INTERPRETATION_NOT_RETRYABLE",
                        "failed Turn did not fail at the Interpretation boundary",
                    )
                try:
                    preserved_result = (
                        unit.agent2.scientific_result_snapshots.get_latest_for_turn(
                            turn_id
                        )
                    )
                except Exception as exc:
                    raise InterpretationFailure(
                        "INTERPRETATION_NOT_RETRYABLE",
                        "failed Turn has no completed ScientificResult to preserve",
                    ) from exc
                if preserved_result is None:
                    raise InterpretationFailure(
                        "INTERPRETATION_NOT_RETRYABLE",
                        "failed Turn has no completed ScientificResult to preserve",
                    )
                ensure_transition(status, ResearchTurnStatus.INTERPRETING)
                updated = unit.agent2.research_turns.compare_and_set_status(
                    turn_id,
                    expected_status=status.value,
                    expected_version=int(turn["row_version"]),
                    target_status=ResearchTurnStatus.INTERPRETING.value,
                    clear_error=True,
                )
                self._event(
                    unit,
                    turn_id,
                    ResearchTurnEventType.INTERPRETATION_STARTED,
                    {
                        "status": updated["status"],
                        "recovered": True,
                        "preservedResult": True,
                    },
                )
                return {"turn": updated, "provider_meta": {}, "recovered": True}
            raise InterpretationFailure("INTERPRETATION_NOT_READY", f"turn status {status.value} cannot be interpreted")

    def _load_input(self, turn_id: UUID) -> tuple[ScientificResultBundle, dict[str, Any], str, str, Any, str]:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            snapshot = None
            if str(turn["status"]) == ResearchTurnStatus.INTERPRETING.value and str(turn.get("action_type") or "") == ResearchAction.INTERPRET_RESULT.value:
                decision = session.agent2.research_turn_decisions.get_for_turn(turn_id)
                referenced = ((decision or {}).get("decision_json") or {}).get("reusable_result_ref_keys") or []
                context = session.agent2.research_context_snapshots.get_for_turn(turn_id)
                refs = (context or {}).get("referenced_result_refs_json") or []
                requested_keys = set((decision or {}).get("decision_json", {}).get("reusable_result_ref_keys") or [])
                for value in refs:
                    if not isinstance(value, dict) or (requested_keys and value.get("candidate_key") not in requested_keys):
                        continue
                    try:
                        candidate = session.agent2.scientific_result_snapshots.get(UUID(str(value.get("result_id"))))
                        if str(candidate["project_id"]) == str(turn["project_id"]):
                            snapshot = candidate
                            break
                    except Exception:
                        continue
                if snapshot is None and referenced:
                    # Candidate keys are opaque; the persisted context is the authority.
                    raise ScientificResultSnapshotNotFound(str(turn_id))
            else:
                snapshot = session.agent2.scientific_result_snapshots.get_latest_for_turn(turn_id)
            bundle = ScientificResultBundle.model_validate(snapshot["bundle_json"])
            objects: dict[str, dict[str, Any]] = {}
            versions: dict[str, dict[str, Any]] = {}
            for ref in bundle.source_object_refs:
                try:
                    objects[str(ref.object_id)] = session.agent2.scientific_objects.get_object(ref.object_id)
                    versions[str(ref.version_id)] = session.agent2.scientific_objects.get_version(ref.version_id)
                except Exception:
                    pass
            message = session.agent2.research_turns.get_message(str(turn["user_message_id"]))
            question = str(message.get("content_summary") or bundle.research_question)
            relevance = effective_relevance(bundle, objects=objects, versions=versions)
            envelope, fingerprint = self.assembler.assemble(bundle=bundle, question=question, relevance_status=relevance)
            return bundle, snapshot, question, relevance, envelope, fingerprint

    def _record_interpreter_manifest(
        self,
        *,
        turn_id: UUID,
        bundle: ScientificResultBundle,
        snapshot: dict[str, Any],
        question: str,
        envelope: Any,
        context_fingerprint: str,
    ) -> None:
        """Persist the exact bounded input selection before provider execution."""
        items: list[dict[str, Any]] = []
        for index, ref in enumerate(bundle.source_object_refs, start=1):
            items.append({
                "item_id": f"source_{index}",
                "kind": "SCIENTIFIC_SELECTION",
                "authority_class": "SCIENTIFIC_DATA",
                "source_identity": f"{ref.object_id}:{ref.version_id}",
                "opaque_ref": f"source_{index}",
                "object_id": str(ref.object_id),
                "version_id": str(ref.version_id),
                "content": ref.model_dump(mode="json"),
                "inclusion_reason": "exact source bound to ScientificResult",
                "selection_mode": "EXPLICIT",
            })
        items.append({
            "item_id": "result_1",
            "kind": "SCIENTIFIC_RESULT",
            "authority_class": "SCIENTIFIC_RESULT",
            "source_identity": str(snapshot["id"]),
            "opaque_ref": "result_1",
            "result_ref": str(snapshot["id"]),
            "content": {
                "result_snapshot_id": str(snapshot["id"]),
                "result_id": str(bundle.result_id),
                "fact_ids": [str(item.fact_id) for item in bundle.facts[:64]],
                "result_item_ids": [str(item.id) for item in bundle.result_items[:24]],
                "figure_ids": [str(item.figure_id) for item in bundle.figures[:16]],
                "table_ids": [str(item.table_id) for item in bundle.tables[:16]],
            },
            "inclusion_reason": "authoritative result facts for grounded interpretation",
            "selection_mode": "EXPLICIT",
        })
        for index, evidence in enumerate(envelope.evidence[:64], start=1):
            evidence_id = str(evidence.get("evidence_id") or f"evidence_{index}")
            items.append({
                "item_id": evidence_id,
                "kind": "SCIENTIFIC_EVIDENCE",
                "authority_class": "SCIENTIFIC_EVIDENCE",
                "source_identity": evidence_id,
                "opaque_ref": f"evidence_{index}",
                "content": {
                    "evidence_id": evidence_id,
                    "evidence_type": evidence.get("evidence_type"),
                    "supports_fact_refs": list(evidence.get("supports_fact_refs") or [])[:32],
                    "supports_result_item_refs": list(evidence.get("supports_result_item_refs") or [])[:32],
                },
                "inclusion_reason": "bounded evidence references supporting Result facts",
                "selection_mode": "RETRIEVED",
            })
        items.append({
            "item_id": "research_question",
            "kind": "RESEARCH_GOAL",
            "authority_class": "CONVERSATIONAL_NARRATIVE",
            "source_identity": f"{turn_id}:question",
            "opaque_ref": "research_question",
            "content": question[:16000],
            "inclusion_reason": "current interpretation question",
            "selection_mode": "CURRENT",
        })
        manifest = build_operation_manifest(
            operation=ContextOperation.INTERPRETER,
            project_id=str(bundle.project_id),
            research_session_id=str(bundle.research_session_id),
            research_turn_id=turn_id,
            context_fingerprint=context_fingerprint,
            items=items,
            serialized_input=envelope.model_dump(mode="json"),
            serialized_input_version=str(
                getattr(envelope, "contract_version", "unknown")
            ),
            invocation_role="scientific_interpreter",
            prompt_template_version=PROMPT_VERSION,
            input_state="ACTUAL",
        )
        with self.repository_factory.unit_of_work() as unit:
            self._event(unit, turn_id, ResearchTurnEventType.CONTEXT_MANIFEST_RECORDED, {
                "operation": ContextOperation.INTERPRETER.value,
                "context_manifest": manifest.model_dump(mode="json"),
            })

    def _generate(
        self,
        envelope: Any,
        *,
        bundle: ScientificResultBundle,
        repair_errors: list[str] | None = None,
        repair_attempted: bool = False,
        turn_id: UUID | None = None,
    ) -> tuple[ScientificInterpretationOutput, bool, dict[str, Any]]:
        context = {
            "repair_attempted": repair_attempted,
            "repair": {"validation_errors": repair_errors[:16]}
            if repair_errors
            else None,
            "retry_observer": (
                (lambda payload: self._record_provider_retry(turn_id, payload))
                if turn_id is not None
                else None
            ),
        }
        result = asyncio.run(self.client.generate_structured(input_payload=envelope.model_dump(mode="json"), output_schema=ScientificInterpretationOutput.model_json_schema(), timeout_seconds=self.timeout_seconds, request_context=context))
        # Some server-side provider deployments still return retired finding
        # presentation / assessment fields.  They are not part of the current
        # provider contract and never carry authority: support, limitations,
        # defects, and method context are recomputed below by deterministic
        # grounding projections.  Strip only this explicit compatibility set;
        # every other unexpected field remains fail-closed under the strict
        # Pydantic contract.
        parsed = self._strip_legacy_finding_fields(result.parsed)
        parsed = self._resolve_provider_reference_aliases(parsed, envelope)
        return ScientificInterpretationOutput.model_validate(parsed), repair_attempted, {"provider": result.provider, "model": result.model, "provider_request_id": result.provider_request_id}

    @staticmethod
    def _resolve_provider_reference_aliases(
        parsed: Any,
        envelope: Any,
    ) -> Any:
        """Resolve only explicit ordinal provider aliases to exact Result IDs.

        The model may cite ``result_1``/``fact_1``/``evidence_1`` from the
        bounded interpreter envelope.  Grounding remains fail-closed: aliases
        are read from the exact provider-visible envelope, not re-numbered from
        the unbounded persisted bundle. Unknown references remain unchanged and
        are rejected by the normal validators.
        """

        if not isinstance(parsed, dict):
            return parsed
        serialized = (
            envelope.model_dump(mode="json")
            if hasattr(envelope, "model_dump")
            else envelope
            if isinstance(envelope, dict)
            else {}
        )
        result = serialized.get("result") if isinstance(serialized, dict) else {}
        aliases = (
            dict(result.get("reference_aliases") or {})
            if isinstance(result, dict)
            else {}
        )
        aliases = {str(key): str(value) for key, value in aliases.items() if value}

        cleaned = dict(parsed)
        for collection_name in ("primary_findings", "supporting_findings"):
            findings = cleaned.get(collection_name)
            if not isinstance(findings, list):
                continue
            normalized_findings = []
            for finding in findings:
                if not isinstance(finding, dict):
                    normalized_findings.append(finding)
                    continue
                item = dict(finding)
                for field in ("fact_refs", "evidence_refs", "result_item_refs"):
                    refs = item.get(field)
                    if isinstance(refs, list):
                        item[field] = [aliases.get(str(ref), ref) for ref in refs]
                normalized_findings.append(item)
            cleaned[collection_name] = normalized_findings
        for field in ("primary_result_refs", "supporting_result_refs"):
            refs = cleaned.get(field)
            if isinstance(refs, list):
                cleaned[field] = [aliases.get(str(ref), ref) for ref in refs]
        return cleaned

    def _record_provider_retry(
        self,
        turn_id: UUID,
        payload: dict[str, Any],
    ) -> None:
        safe_payload = {
            "provider_class": "deepseek",
            "purpose": str(payload.get("purpose") or "GROUNDED_INTERPRETATION"),
            "failed_attempt": int(payload.get("failed_attempt") or 1),
            "next_attempt": int(payload.get("next_attempt") or 2),
            "error_code": str(payload.get("error_code") or "PROVIDER_TRANSIENT_FAILURE"),
            "status_code": payload.get("status_code"),
            "retry_after_seconds": payload.get("retry_after_seconds"),
            "base_backoff_seconds": payload.get("base_backoff_seconds"),
            "jitter_seconds": payload.get("jitter_seconds"),
            "retry_delay_seconds": payload.get("retry_delay_seconds"),
            "scheduled_at": str(payload.get("scheduled_at") or datetime.now(timezone.utc).isoformat()),
            "preserved_result": True,
        }
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get(turn_id)
            if str(turn.get("status")) != ResearchTurnStatus.INTERPRETING.value:
                return
            self._event(
                unit,
                turn_id,
                ResearchTurnEventType.INTERPRETATION_RETRY_SCHEDULED,
                safe_payload,
            )

    @staticmethod
    def _strip_legacy_finding_fields(parsed: Any) -> Any:
        retired_fields = {
            "outcome",
            "accepted",
            "limitations",
            "reason_codes",
            "supporting_refs",
            "contradicting_refs",
            "defects",
            "independent_evidence_groups",
            "required_qualifiers",
            "severity",
            "method_context",
        }
        if not isinstance(parsed, dict):
            return parsed
        cleaned = dict(parsed)
        for collection_name in ("primary_findings", "supporting_findings"):
            findings = cleaned.get(collection_name)
            if not isinstance(findings, list):
                continue
            cleaned[collection_name] = [
                (
                    {key: value for key, value in finding.items()
                     if key not in retired_fields}
                    if isinstance(finding, dict)
                    else finding
                )
                for finding in findings
            ]
        return cleaned

    def _persist(self, turn_id: UUID, *, snapshot_id: Any, project_id: str, fingerprint: str, result: ScientificInterpretationOutput, content: str, provider_meta: dict[str, Any], repair_attempted: bool, bundle: ScientificResultBundle) -> dict[str, Any]:
        interpretation_id = uuid4()
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            existing = unit.agent2.interpretations.get_for_turn(turn_id)
            if existing is not None:
                return existing
            row = unit.agent2.interpretations.add({
                "id": interpretation_id,
                "research_turn_id": turn_id,
                "result_snapshot_id": snapshot_id,
                "project_id": project_id,
                "contract_version": self.contract_version,
                "prompt_version": PROMPT_VERSION,
                "provider": str(provider_meta.get("provider") or "structured_interpreter"),
                "model": str(provider_meta.get("model") or "unknown"),
                "provider_request_id": provider_meta.get("provider_request_id"),
                "repair_attempted": repair_attempted,
                "input_fingerprint": fingerprint,
                "grounding_status": "VALID",
                "output_json": {"interpretation": result.model_dump(mode="json"), "message": content, "execution_status": bundle.execution_status.value},
                "created_at": datetime.now(timezone.utc),
            })
            message_id = f"message_{uuid4().hex}"
            unit.agent2.research_turns.add_message({"id": message_id, "session_id": turn["research_session_id"], "role": "agent", "content_summary": content, "payload_json": {"source": "agent2_scientific_interpreter", "messageKind": "ASSISTANT_FINAL", "turnId": str(turn_id), "interpretationId": str(interpretation_id), "sourceResultSnapshotId": str(snapshot_id), "groundingStatus": "VALID", "factRefs": sorted({ref for item in [*result.primary_findings, *result.supporting_findings] for ref in item.fact_refs}), "evidenceRefs": sorted({ref for item in [*result.primary_findings, *result.supporting_findings] for ref in item.evidence_refs})}, "created_at": datetime.now(timezone.utc)})
            attached = unit.agent2.research_turns.attach_message_refs(turn_id, assistant_final_message_id=message_id)
            target = ResearchTurnStatus.PARTIAL if bundle.execution_status.value == "PARTIAL" else ResearchTurnStatus.COMPLETED
            unit.agent2.research_turns.compare_and_set_status(turn_id, expected_status=ResearchTurnStatus.INTERPRETING.value, expected_version=int(attached["row_version"]), target_status=target.value, completed_at=datetime.now(timezone.utc))
            self._event(unit, turn_id, ResearchTurnEventType.INTERPRETATION_READY, {"interpretation_id": str(interpretation_id), "message_id": message_id})
            self._event(unit, turn_id, ResearchTurnEventType.TURN_PARTIAL if target == ResearchTurnStatus.PARTIAL else ResearchTurnEventType.TURN_COMPLETED, {"status": target.value})
            return row

    def _fail(self, turn_id: UUID, code: str, summary: str) -> None:
        try:
            with self.repository_factory.unit_of_work() as unit:
                turn = unit.agent2.research_turns.get_for_update(turn_id)
                if str(turn["status"]) != ResearchTurnStatus.INTERPRETING.value:
                    return
                updated = unit.agent2.research_turns.compare_and_set_status(turn_id, expected_status=ResearchTurnStatus.INTERPRETING.value, expected_version=int(turn["row_version"]), target_status=ResearchTurnStatus.FAILED.value, completed_at=datetime.now(timezone.utc), error_code=code, error_summary=summary[:1000])
                self._event(unit, turn_id, ResearchTurnEventType.TURN_FAILED, {"status": updated["status"], "error_code": code})
        except Exception as exc:
            logger.error(
                "interpretation_failure_state_persist_failed",
                extra={"turn_id": str(turn_id), "error_code": code, "error_type": type(exc).__name__},
            )

    @staticmethod
    def _event(unit: Any, turn_id: UUID, event_type: ResearchTurnEventType, payload: dict[str, Any]) -> None:
        unit.agent2.research_turn_events.append_turn_event({"id": uuid4(), "turn_id": turn_id, "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id), "event_type": event_type.value, "payload_json": payload, "created_at": datetime.now(timezone.utc)})


class InterpretationFailure(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


__all__ = ["InterpretationFailure", "ScientificInterpretationService"]
