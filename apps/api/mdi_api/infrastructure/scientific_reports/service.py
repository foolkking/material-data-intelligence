from __future__ import annotations

import asyncio
import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4, uuid5, NAMESPACE_URL

from pydantic import ValidationError

from mdi_api.interpretation.grounding import project_grounded_communication
from mdi_api.lifecycle_policy import retention_policy_snapshot
from mdi_api.interpretation.schemas import ScientificInterpretationOutput
from mdi_api.domain.scientific_results.relevance import ScientificResultRelevanceEvaluator
from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.unit_of_work import RepositoryFactory
from mdi_api.research_agent.context.manifest import build_operation_manifest
from mdi_api.research_agent.context.policy import ContextOperation
from mdi_api.research_agent.schemas import ResearchTurnEventType
from mdi_api.db import project_configs
from sqlalchemy import func, insert, select, update

from mdi_api.application.scientific_reports.assembler import ReportComposerInputAssembler
from mdi_api.infrastructure.scientific_reports.client import DeepSeekReportComposerClient, StructuredReportComposerClient
from mdi_api.application.scientific_reports.grounded import DeterministicScientificReportComposer
from mdi_api.application.scientific_reports.grounding import ReportGroundingValidator
from mdi_api.domain.scientific_reports.errors import ScientificReportError
from mdi_api.domain.scientific_reports.contracts import REPORT_COMPOSER_PROMPT_VERSION, REPORT_COMPOSER_VERSION, ScientificReportOutput, ScientificReportSnapshot



class ScientificReportService:
    """Phase 8 report lifecycle; no scientific execution is reachable here."""

    def __init__(self, repository_factory: RepositoryFactory, *, client: StructuredReportComposerClient | None = None, timeout_seconds: float = 120.0) -> None:
        self.repository_factory = repository_factory
        self.assembler = ReportComposerInputAssembler()
        self.client = client or DeepSeekReportComposerClient()
        self.timeout_seconds = timeout_seconds
        self.validator = ReportGroundingValidator()

    def generate_for_turn(self, turn_id: UUID, *, created_by: str = "user_local") -> dict[str, Any]:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            existing = session.agent2.scientific_reports.get_for_turn(turn_id)
            if existing is not None:
                return self._public(existing)
            interpretation = session.agent2.interpretations.get_for_turn(turn_id)
            if interpretation is None:
                raise ScientificReportError("REPORT_INTERPRETATION_NOT_READY", "报告需要已验证的 ScientificInterpretation。", 409)
            snapshot = self._snapshot_for_interpretation(
                session,
                turn=turn,
                interpretation=interpretation,
            )
            bundle = ScientificResultBundle.model_validate(snapshot["bundle_json"])
            objects: dict[str, dict[str, Any]] = {}
            versions: dict[str, dict[str, Any]] = {}
            for ref in bundle.source_object_refs:
                try:
                    objects[str(ref.object_id)] = session.agent2.scientific_objects.get_object(ref.object_id)
                    versions[str(ref.version_id)] = session.agent2.scientific_objects.get_version(ref.version_id)
                except Exception:
                    pass
            source_labels = [
                str(
                    (objects.get(str(ref.object_id)) or {}).get("display_name")
                    or ref.display_name
                    or ref.object_type
                )
                for ref in bundle.source_object_refs
            ]
            relevance = ScientificResultRelevanceEvaluator().evaluate(bundle.source_object_refs, objects=objects, versions=versions).value
            input_payload, input_fingerprint = self.assembler.assemble(bundle=bundle, interpretation=interpretation["output_json"], relevance_status=relevance)
        self._record_report_manifest(
            turn=turn,
            turn_id=turn_id,
            snapshot=snapshot,
            bundle=bundle,
            interpretation=interpretation["output_json"],
            input_payload=input_payload,
            context_fingerprint=input_fingerprint,
        )
        output, provider_meta, repair_attempted = self._compose_with_one_repair(
            input_payload=input_payload,
            bundle=bundle,
            interpretation=interpretation["output_json"],
        )
        output = self._project_authoritative_report(
            output,
            bundle=bundle,
            interpretation=interpretation["output_json"],
            relevance_status=relevance,
            source_labels=source_labels,
        )
        projection_errors = self.validator.validate(
            output,
            bundle=bundle,
            interpretation=interpretation["output_json"],
        )
        if projection_errors:
            raise ScientificReportError(
                "REPORT_PROJECTION_GROUNDING_FAILED",
                "; ".join(projection_errors)[:2000],
                422,
            )
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            interpretation = session.agent2.interpretations.get_for_turn(turn_id)
            if interpretation is None:
                raise ScientificReportError("REPORT_INTERPRETATION_NOT_READY", "报告需要已验证的 ScientificInterpretation。", 409)
            snapshot = self._snapshot_for_interpretation(
                session,
                turn=turn,
                interpretation=interpretation,
            )
            source_fingerprint = hashlib.sha256(json.dumps({
                "result_snapshot_id": str(snapshot["id"]),
                "result_source_fingerprint": snapshot["source_fingerprint"],
                "interpretation_id": str(interpretation["id"]),
                "interpretation_input_fingerprint": interpretation["input_fingerprint"],
                "relevance": relevance,
                "report": output.model_dump(mode="json"),
                "composer_version": REPORT_COMPOSER_VERSION,
                "input_fingerprint": input_fingerprint,
                "provider": provider_meta.get("provider"),
                "model": provider_meta.get("model"),
            }, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
            existing = session.agent2.scientific_reports.get_for_turn(turn_id)
            if existing is not None:
                if str(existing["source_fingerprint"]) != source_fingerprint:
                    raise ScientificReportError("REPORT_SNAPSHOT_CONFLICT", "同一 ResearchTurn 的报告来源已改变。", 409)
                return self._public(existing)
            report_id = f"agent2_report_{source_fingerprint[:32]}"
            job_id = str(bundle.provenance.job_id or snapshot.get("job_id") or "")
            if not job_id:
                raise ScientificReportError("REPORT_SOURCE_JOB_MISSING", "报告需要绑定 exact execution Job。", 409)
            report_payload = {
                "reportId": report_id, "projectId": str(turn["project_id"]), "jobId": job_id,
                "title": output.title, "version": "agent2-1", "createdBy": created_by,
                "scientificReport": output.model_dump(mode="json"), "sourceFingerprint": source_fingerprint,
                "scientificResultSnapshotId": str(snapshot["id"]), "scientificInterpretationId": str(interpretation["id"]),
                "researchTurnId": str(turn_id), "relevanceAtGeneration": relevance,
                "groundingStatus": "VALID", "reportType": "AGENT2_SCIENTIFIC_REPORT",
            }
        with self.repository_factory.unit_of_work() as unit:
            existing = unit.agent2.scientific_reports.get_for_turn(turn_id)
            if existing is not None:
                if str(existing["source_fingerprint"]) != source_fingerprint:
                    raise ScientificReportError("REPORT_SNAPSHOT_CONFLICT", "同一 ResearchTurn 的报告来源已改变。", 409)
                return self._public(existing)
            unit.repositories.reports.create_immutable(report_payload)
            row = unit.agent2.scientific_reports.add({
                "id": uuid5(NAMESPACE_URL, f"mdi:agent2-report-row:{source_fingerprint}"), "report_id": report_id, "project_id": str(turn["project_id"]),
                "research_session_id": turn.get("research_session_id"), "research_turn_id": turn_id,
                "scientific_result_snapshot_id": snapshot["id"], "scientific_interpretation_id": interpretation["id"],
                "contract_version": output.contract_version, "composer_version": REPORT_COMPOSER_VERSION,
                "prompt_version": REPORT_COMPOSER_PROMPT_VERSION, "source_fingerprint": source_fingerprint,
                "relevance_at_generation": relevance, "grounding_status": "VALID",
                "report_json": {"snapshot": ScientificReportSnapshot(
                    report_id=report_id, snapshot_id=uuid5(NAMESPACE_URL, f"mdi:agent2-report:{source_fingerprint}"), project_id=str(turn["project_id"]), research_session_id=turn.get("research_session_id"),
                    research_turn_id=turn_id, scientific_result_snapshot_id=snapshot["id"], scientific_interpretation_id=interpretation["id"],
                    execution_status=bundle.execution_status.value, relevance_at_generation=relevance, title=output.title, report=output,
                    source_fingerprint=source_fingerprint,
                    composer_metadata={
                        "provider": provider_meta.get("provider"),
                        "model": provider_meta.get("model"),
                        "repair_attempted": repair_attempted,
                        "input_fingerprint": input_fingerprint,
                    },
                    created_at=datetime.now(timezone.utc),
                ).model_dump(mode="json")}, "created_by": created_by,
                "created_at": datetime.now(timezone.utc),
            })
            return self._public(row)

    @staticmethod
    def _snapshot_for_interpretation(
        session: Any,
        *,
        turn: dict[str, Any],
        interpretation: dict[str, Any],
    ) -> dict[str, Any]:
        """Resolve the exact Result authority already bound to Interpretation."""
        snapshot_id = interpretation.get("result_snapshot_id")
        if snapshot_id is None:
            raise ScientificReportError(
                "REPORT_RESULT_NOT_READY",
                "报告需要已验证解释绑定的精确 ScientificResult。",
                409,
            )
        snapshot = session.agent2.scientific_result_snapshots.get(
            UUID(str(snapshot_id)),
        )
        if str(snapshot["project_id"]) != str(turn["project_id"]):
            raise ScientificReportError(
                "REPORT_RESULT_PROJECT_MISMATCH",
                "报告来源 ScientificResult 不属于当前项目。",
                403,
            )
        return snapshot

    @staticmethod
    def _project_authoritative_report(
        provider_output: ScientificReportOutput,
        *,
        bundle: ScientificResultBundle,
        interpretation: dict[str, Any],
        relevance_status: str,
        source_labels: list[str],
    ) -> ScientificReportOutput:
        """Keep provider organization inside the validated scientific boundary.

        The provider may organize prose and suggest bounded next steps, but
        scientific summary/finding/method/source statements are projected
        deterministically from the already validated Interpretation and
        ScientificResult. This prevents qualitative claims such as method
        effectiveness from being promoted merely because they contain no new
        numeric token.
        """
        interpretation_payload = dict(interpretation)
        raw_interpretation = interpretation_payload.get("interpretation")
        if isinstance(raw_interpretation, dict):
            readable_interpretation = project_grounded_communication(
                ScientificInterpretationOutput.model_validate(raw_interpretation),
                bundle,
            )
            interpretation_payload["interpretation"] = readable_interpretation.model_dump(
                mode="json"
            )
        authoritative = DeterministicScientificReportComposer().compose(
            bundle=bundle,
            interpretation=interpretation_payload,
            relevance_status=relevance_status,
        )
        return provider_output.model_copy(
            update={
                "title": authoritative.title,
                "research_question": ScientificReportService._friendly_research_question(
                    authoritative.research_question,
                    source_labels,
                ),
                "summary": authoritative.summary,
                "discussion": authoritative.discussion,
                "conclusion": authoritative.conclusion,
                "main_findings": authoritative.main_findings,
                "primary_figures": authoritative.primary_figures,
                "supporting_results": authoritative.supporting_results,
                "method_summary": authoritative.method_summary,
                "limitations": authoritative.limitations,
                "data_sources": authoritative.data_sources,
                "evidence_refs": authoritative.evidence_refs,
                "reproducibility_summary": authoritative.reproducibility_summary,
            },
        )

    @staticmethod
    def _friendly_research_question(question: str, source_labels: list[str]) -> str:
        rendered = question
        for index, label in enumerate(source_labels, start=1):
            if not label:
                continue
            for alias in (f"obj_{index}", f"source_{index}"):
                rendered = re.sub(
                    rf"(?<![A-Za-z0-9_]){re.escape(alias)}(?![A-Za-z0-9_])",
                    label,
                    rendered,
                )
        return rendered

    def _record_report_manifest(
        self,
        *,
        turn: dict[str, Any],
        turn_id: UUID,
        snapshot: dict[str, Any],
        bundle: ScientificResultBundle,
        interpretation: dict[str, Any],
        input_payload: dict[str, Any],
        context_fingerprint: str,
    ) -> None:
        """Persist a bounded report context selection before composition."""
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
                "inclusion_reason": "exact source bound to Report result",
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
            "inclusion_reason": "authoritative Result projection for report composition",
            "selection_mode": "EXPLICIT",
        })
        interpretation_payload = input_payload.get("interpretation") or interpretation.get("interpretation") or {}
        items.append({
            "item_id": "validated_interpretation",
            "kind": "SCIENTIFIC_RESULT",
            "authority_class": "SCIENTIFIC_RESULT",
            "source_identity": str(interpretation.get("interpretationId") or interpretation.get("id") or "validated-interpretation"),
            "opaque_ref": "validated_interpretation",
            "content": {
                "title": interpretation_payload.get("title"),
                "findings": interpretation_payload.get("findings") or interpretation_payload.get("primary_findings") or [],
                "supporting_findings": interpretation_payload.get("supporting_findings") or [],
                "limitations": interpretation_payload.get("limitations") or [],
            },
            "inclusion_reason": "validated grounded interpretation used for communication",
            "selection_mode": "EXPLICIT",
        })
        for index, evidence in enumerate(bundle.evidence[:64], start=1):
            evidence_id = str(evidence.evidence_id)
            items.append({
                "item_id": evidence_id,
                "kind": "SCIENTIFIC_EVIDENCE",
                "authority_class": "SCIENTIFIC_EVIDENCE",
                "source_identity": evidence_id,
                "opaque_ref": f"evidence_{index}",
                "content": {
                    "evidence_id": evidence_id,
                    "evidence_type": evidence.evidence_type,
                    "supports_fact_refs": list(evidence.supports_fact_refs or [])[:32],
                    "supports_result_item_refs": list(evidence.supports_result_item_refs or [])[:32],
                },
                "inclusion_reason": "bounded evidence references for report provenance",
                "selection_mode": "RETRIEVED",
            })
        manifest = build_operation_manifest(
            operation=ContextOperation.REPORT,
            project_id=str(turn["project_id"]),
            research_session_id=str(turn.get("research_session_id") or bundle.research_session_id),
            research_turn_id=turn_id,
            context_fingerprint=context_fingerprint,
            items=items,
        )
        with self.repository_factory.unit_of_work() as unit:
            unit.agent2.research_turn_events.append_turn_event({
                "id": uuid4(),
                "turn_id": turn_id,
                "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id),
                "event_type": ResearchTurnEventType.CONTEXT_MANIFEST_RECORDED.value,
                "payload_json": {
                    "operation": ContextOperation.REPORT.value,
                    "context_manifest": manifest.model_dump(mode="json"),
                },
                "created_at": datetime.now(timezone.utc),
            })

    def _compose_with_one_repair(
        self,
        *,
        input_payload: dict[str, Any],
        bundle: ScientificResultBundle,
        interpretation: dict[str, Any],
    ) -> tuple[ScientificReportOutput, dict[str, Any], bool]:
        repair_errors: list[str] | None = None
        for attempt in range(2):
            try:
                result = asyncio.run(self.client.generate_structured(
                    input_payload=input_payload,
                    output_schema=ScientificReportOutput.model_json_schema(),
                    timeout_seconds=self.timeout_seconds,
                    request_context={
                        "repair_attempted": attempt == 1,
                        "repair": {"validation_errors": repair_errors[:16]} if repair_errors else None,
                    },
                ))
                output = ScientificReportOutput.model_validate(result.parsed)
            except ValidationError as exc:
                if attempt == 0:
                    repair_errors = [str(error) for error in exc.errors()][:16]
                    continue
                raise ScientificReportError("REPORT_SCHEMA_INVALID", "报告输出未通过结构化 schema 校验。", 422) from exc
            except Exception as exc:
                raise ScientificReportError("REPORT_COMPOSITION_FAILED", "科学结果已完成，但报告整理暂时未完成。", 503) from exc
            errors = self.validator.validate(output, bundle=bundle, interpretation=interpretation)
            if not errors:
                return output, {"provider": result.provider, "model": result.model}, attempt == 1
            if attempt == 0:
                repair_errors = errors[:16]
                continue
            raise ScientificReportError("REPORT_GROUNDING_FAILED", "; ".join(errors)[:2000], 422)
        raise ScientificReportError("REPORT_SCHEMA_INVALID", "报告输出未通过结构化 schema 校验。", 422)

    def get_for_turn(self, turn_id: UUID) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            row = session.agent2.scientific_reports.get_for_turn(turn_id)
            if row is None:
                raise ScientificReportError("REPORT_NOT_READY", "报告尚未生成。", 404)
            report_id = str(row["report_id"])
            project_id = str(row["project_id"])
            lifecycle = self._lifecycle_map(session.connection, project_id).get(report_id, "ACTIVE")
            organization = self._organization_map(session.connection, project_id).get(report_id, {})
            return self._with_viewer_sources(self._public(row, current_relevance=self._current_relevance(session, row), lifecycle_status=lifecycle, organization=organization), session, row)

    def status_for_turn(self, turn_id: UUID) -> dict[str, Any]:
        """Return a non-exceptional, bounded composition status for product polling."""
        with self.repository_factory.session() as session:
            report = session.agent2.scientific_reports.get_for_turn(turn_id)
            if report is not None:
                return {
                    "research_turn_id": str(turn_id),
                    "status": "READY",
                    "report_id": str(report["report_id"]),
                    "generation_id": None,
                    "attempt_count": 0,
                    "error_code": None,
                    "updated_at": report.get("created_at"),
                }
            generation = session.agent2.scientific_report_generations.get_for_turn(turn_id)
            if generation is None:
                return {
                    "research_turn_id": str(turn_id),
                    "status": "NOT_REQUESTED",
                    "report_id": None,
                    "generation_id": None,
                    "attempt_count": 0,
                    "error_code": None,
                    "updated_at": None,
                }
            return {
                "research_turn_id": str(turn_id),
                "status": str(generation["status"]).upper(),
                "report_id": None,
                "generation_id": str(generation["id"]),
                "attempt_count": int(generation.get("attempt_count") or 0),
                "error_code": generation.get("error_code"),
                "updated_at": generation.get("updated_at"),
            }

    def get_by_report_id(self, report_id: str) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            row = session.agent2.scientific_reports.get_by_report_id(report_id)
            if row is None:
                raise ScientificReportError("REPORT_NOT_FOUND", "报告不存在。", 404)
            project_id = str(row["project_id"])
            lifecycle = self._lifecycle_map(session.connection, project_id).get(str(row["report_id"]), "ACTIVE")
            organization = self._organization_map(session.connection, project_id).get(str(row["report_id"]), {})
            return self._with_viewer_sources(self._public(row, current_relevance=self._current_relevance(session, row), lifecycle_status=lifecycle, organization=organization), session, row)

    def create_revision(
        self,
        report_id: str,
        *,
        created_by: str,
        reason: str = "USER_REVISION",
        title: str | None = None,
    ) -> dict[str, Any]:
        """Create a new immutable communication snapshot from an existing Report.

        A revision copies only the already-grounded Report communication layer.
        It deliberately does not invoke a provider, Planner, Tool, Artifact, or
        ScientificResult path. Exact scientific Result, Interpretation and
        object/version authority remain bound to the new snapshot.
        """

        normalized_reason = str(reason or "USER_REVISION").strip().upper()
        if normalized_reason not in {"USER_REVISION", "DUPLICATE"}:
            raise ScientificReportError(
                "REPORT_REVISION_REASON_INVALID",
                "报告修订原因不受支持。",
                422,
            )
        normalized_title = str(title or "").strip()
        if len(normalized_title) > 256:
            raise ScientificReportError(
                "REPORT_TITLE_INVALID",
                "报告名称不能超过 256 个字符。",
                422,
            )
        with self.repository_factory.session() as session:
            parent = session.agent2.scientific_reports.get_by_report_id(report_id)
            if parent is None:
                raise ScientificReportError("REPORT_NOT_FOUND", "报告不存在。", 404)
            siblings = session.agent2.scientific_reports.list_for_turn(
                parent["research_turn_id"]
            )
            parent_payload = self._snapshot_payload(parent)
            parent_revision = self._revision_metadata(parent)
            revision_group_id = str(
                parent_revision.get("revision_group_id") or parent["report_id"]
            )
            revision_number = max(
                (
                    int(self._revision_metadata(candidate).get("revision_number") or 1)
                    for candidate in siblings
                    if str(
                        self._revision_metadata(candidate).get("revision_group_id")
                        or candidate["report_id"]
                    )
                    == revision_group_id
                ),
                default=1,
            ) + 1
            report_output = ScientificReportOutput.model_validate(
                parent_payload["report"]
            )
            if normalized_title:
                report_output = report_output.model_copy(
                    update={"title": normalized_title}
                )
            revision_seed = {
                "revision_group_id": revision_group_id,
                "parent_report_id": str(parent["report_id"]),
                "parent_snapshot_id": str(parent["id"]),
                "revision_number": revision_number,
                "revision_reason": normalized_reason,
                "scientific_result_snapshot_id": str(
                    parent["scientific_result_snapshot_id"]
                ),
                "scientific_interpretation_id": str(
                    parent["scientific_interpretation_id"]
                ),
                "report": report_output.model_dump(mode="json"),
            }
            source_fingerprint = hashlib.sha256(
                json.dumps(
                    revision_seed,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode()
            ).hexdigest()
            existing = next(
                (
                    candidate
                    for candidate in siblings
                    if str(candidate["source_fingerprint"]) == source_fingerprint
                ),
                None,
            )
            if existing is not None:
                project_id = str(existing["project_id"])
                lifecycle = self._lifecycle_map(
                    session.connection, project_id
                ).get(str(existing["report_id"]), "ACTIVE")
                organization = self._organization_map(
                    session.connection, project_id
                ).get(str(existing["report_id"]), {})
                return self._with_viewer_sources(
                    self._public(
                        existing,
                        current_relevance=self._current_relevance(
                            session, existing
                        ),
                        lifecycle_status=lifecycle,
                        organization=organization,
                    ),
                    session,
                    existing,
                )
            new_report_id = f"agent2_report_revision_{source_fingerprint[:32]}"
            new_snapshot_id = uuid5(
                NAMESPACE_URL, f"mdi:agent2-report:{source_fingerprint}"
            )
            composer_metadata = dict(
                parent_payload.get("composer_metadata") or {}
            )
            composer_metadata["revision"] = {
                "revision_group_id": revision_group_id,
                "parent_report_id": str(parent["report_id"]),
                "parent_snapshot_id": str(parent["id"]),
                "revision_number": revision_number,
                "revision_reason": normalized_reason,
            }
            snapshot_payload = ScientificReportSnapshot(
                report_id=new_report_id,
                snapshot_id=new_snapshot_id,
                project_id=str(parent["project_id"]),
                research_session_id=parent.get("research_session_id"),
                research_turn_id=parent["research_turn_id"],
                scientific_result_snapshot_id=parent[
                    "scientific_result_snapshot_id"
                ],
                scientific_interpretation_id=parent[
                    "scientific_interpretation_id"
                ],
                execution_status=str(parent_payload["execution_status"]),
                relevance_at_generation=str(
                    parent["relevance_at_generation"]
                ),
                title=report_output.title,
                report=report_output,
                source_fingerprint=source_fingerprint,
                composer_version=str(parent["composer_version"]),
                prompt_version=str(parent["prompt_version"]),
                composer_metadata=composer_metadata,
                created_at=datetime.now(timezone.utc),
            )
            bundle = ScientificResultBundle.model_validate(
                session.agent2.scientific_result_snapshots.get(
                    parent["scientific_result_snapshot_id"]
                )["bundle_json"]
            )
            job_id = str(bundle.provenance.job_id or "")
            if not job_id:
                raise ScientificReportError(
                    "REPORT_SOURCE_JOB_MISSING",
                    "报告修订需要保留 exact execution Job。",
                    409,
                )
            report_payload = {
                "reportId": new_report_id,
                "projectId": str(parent["project_id"]),
                "jobId": job_id,
                "title": report_output.title,
                "version": f"agent2-r{revision_number}",
                "createdBy": created_by,
                "scientificReport": report_output.model_dump(mode="json"),
                "sourceFingerprint": source_fingerprint,
                "scientificResultSnapshotId": str(
                    parent["scientific_result_snapshot_id"]
                ),
                "scientificInterpretationId": str(
                    parent["scientific_interpretation_id"]
                ),
                "researchTurnId": str(parent["research_turn_id"]),
                "relevanceAtGeneration": str(
                    parent["relevance_at_generation"]
                ),
                "groundingStatus": "VALID",
                "reportType": "AGENT2_SCIENTIFIC_REPORT_REVISION",
            }
        with self.repository_factory.unit_of_work() as unit:
            existing = unit.agent2.scientific_reports.get_by_report_id(
                new_report_id
            )
            if existing is not None:
                row = existing
            else:
                unit.repositories.reports.create_immutable(report_payload)
                row = unit.agent2.scientific_reports.add(
                    {
                        "id": new_snapshot_id,
                        "report_id": new_report_id,
                        "project_id": str(parent["project_id"]),
                        "research_session_id": parent.get(
                            "research_session_id"
                        ),
                        "research_turn_id": parent["research_turn_id"],
                        "scientific_result_snapshot_id": parent[
                            "scientific_result_snapshot_id"
                        ],
                        "scientific_interpretation_id": parent[
                            "scientific_interpretation_id"
                        ],
                        "contract_version": report_output.contract_version,
                        "composer_version": str(parent["composer_version"]),
                        "prompt_version": str(parent["prompt_version"]),
                        "source_fingerprint": source_fingerprint,
                        "relevance_at_generation": str(
                            parent["relevance_at_generation"]
                        ),
                        "grounding_status": "VALID",
                        "report_json": {
                            "snapshot": snapshot_payload.model_dump(
                                mode="json"
                            )
                        },
                        "created_by": created_by,
                        "created_at": datetime.now(timezone.utc),
                    }
                )
        return self.get_by_report_id(str(row["report_id"]))

    def list_revisions(self, report_id: str) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            row = session.agent2.scientific_reports.get_by_report_id(report_id)
            if row is None:
                raise ScientificReportError("REPORT_NOT_FOUND", "报告不存在。", 404)
            metadata = self._revision_metadata(row)
            group_id = str(
                metadata.get("revision_group_id") or row["report_id"]
            )
            lifecycle = self._lifecycle_map(
                session.connection, str(row["project_id"])
            )
            organization = self._organization_map(
                session.connection, str(row["project_id"])
            )
            siblings = [
                candidate
                for candidate in session.agent2.scientific_reports.list_for_turn(
                    row["research_turn_id"]
                )
                if str(
                    self._revision_metadata(candidate).get("revision_group_id")
                    or candidate["report_id"]
                )
                == group_id
            ]
            items = [
                self._public(
                    candidate,
                    summary=True,
                    current_relevance=self._current_relevance(
                        session, candidate
                    ),
                    lifecycle_status=lifecycle.get(
                        str(candidate["report_id"]), "ACTIVE"
                    ),
                    organization=organization.get(
                        str(candidate["report_id"]), {}
                    ),
                )
                for candidate in siblings
            ]
            items.sort(
                key=lambda item: int(item.get("revision_number") or 1)
            )
            return {
                "revision_group_id": group_id,
                "current_report_id": report_id,
                "items": items,
                "count": len(items),
            }

    def compare_revisions(
        self, report_id: str, *, base_report_id: str | None = None
    ) -> dict[str, Any]:
        revisions = self.list_revisions(report_id)
        items = revisions["items"]
        current = next(
            (item for item in items if item["report_id"] == report_id), None
        )
        if current is None:
            raise ScientificReportError(
                "REPORT_REVISION_NOT_FOUND", "报告修订不存在。", 404
            )
        if base_report_id:
            base = next(
                (
                    item
                    for item in items
                    if item["report_id"] == base_report_id
                ),
                None,
            )
        else:
            current_number = int(current.get("revision_number") or 1)
            base = next(
                (
                    item
                    for item in reversed(items)
                    if int(item.get("revision_number") or 1)
                    < current_number
                ),
                None,
            )
        if base is None:
            raise ScientificReportError(
                "REPORT_REVISION_BASE_NOT_FOUND",
                "没有可用于比较的上一版报告。",
                404,
            )
        base_full = self.get_by_report_id(str(base["report_id"]))
        current_full = self.get_by_report_id(str(current["report_id"]))
        before = base_full.get("report") or {}
        after = current_full.get("report") or {}
        sections = [
            "title",
            "research_question",
            "summary",
            "method_summary",
            "discussion",
            "conclusion",
            "next_steps",
            "limitations",
        ]
        changed_sections = [
            section
            for section in sections
            if before.get(section) != after.get(section)
        ]
        before_findings = {
            str(item.get("statement"))
            for item in before.get("main_findings") or []
            if isinstance(item, dict)
        }
        after_findings = {
            str(item.get("statement"))
            for item in after.get("main_findings") or []
            if isinstance(item, dict)
        }
        authority_keys = (
            "project_id",
            "research_turn_id",
            "scientific_result_snapshot_id",
            "scientific_interpretation_id",
        )
        return {
            "revision_group_id": revisions["revision_group_id"],
            "base_report_id": str(base["report_id"]),
            "report_id": report_id,
            "base_revision_number": int(base.get("revision_number") or 1),
            "revision_number": int(current.get("revision_number") or 1),
            "scientific_authority_unchanged": all(
                base_full.get(key) == current_full.get(key)
                for key in authority_keys
            ),
            "changed_sections": changed_sections,
            "added_findings": sorted(after_findings - before_findings),
            "removed_findings": sorted(before_findings - after_findings),
            "source_versions_unchanged": {
                (item["object_id"], item["version_id"])
                for item in base_full.get("viewer_sources") or []
            }
            == {
                (item["object_id"], item["version_id"])
                for item in current_full.get("viewer_sources") or []
            },
        }

    @staticmethod
    def _snapshot_payload(row: dict[str, Any]) -> dict[str, Any]:
        payload = dict(row.get("report_json") or {}).get("snapshot")
        if not isinstance(payload, dict):
            raise ScientificReportError(
                "REPORT_SNAPSHOT_INVALID",
                "报告快照内容无效。",
                500,
            )
        return payload

    @classmethod
    def _revision_metadata(cls, row: dict[str, Any]) -> dict[str, Any]:
        payload = cls._snapshot_payload(row)
        composer = payload.get("composer_metadata")
        if not isinstance(composer, dict):
            return {}
        revision = composer.get("revision")
        return dict(revision) if isinstance(revision, dict) else {}

    @staticmethod
    def _with_viewer_sources(payload: dict[str, Any], session: Any, row: dict[str, Any]) -> dict[str, Any]:
        snapshot = session.agent2.scientific_result_snapshots.get(row["scientific_result_snapshot_id"])
        bundle = ScientificResultBundle.model_validate(snapshot["bundle_json"])
        sources = []
        for index, ref in enumerate(bundle.source_object_refs[:8], start=1):
            try:
                obj = session.agent2.scientific_objects.get_object(ref.object_id)
                version = session.agent2.scientific_objects.get_version(ref.version_id)
            except Exception:
                continue
            sources.append({
                "source_ref": f"source_{index}", "object_id": str(ref.object_id), "version_id": str(ref.version_id),
                "object_type": str(version["object_type"]), "display_name": str(obj["display_name"]),
                "is_current_version": str(obj.get("current_version_id")) == str(ref.version_id),
                # Lifecycle remains communication metadata derived from the
                # authoritative object. It is intentionally separate from
                # exact-version provenance: an archived object can still
                # retain this immutable version as its current state.
                "lifecycle_status": str(obj.get("lifecycle_status") or "ACTIVE").upper(),
            })
        # Figure descriptors are communication-layer projections, but opening
        # the persisted figure must still resolve through the exact Result
        # artifact authority. Keep this bounded and derived from the immutable
        # ScientificResult bundle; never accept arbitrary report-provided URLs.
        job_id = str(bundle.provenance.job_id or row.get("job_id") or "")
        figure_sources = [
            {
                "figure_ref": str(figure.figure_id),
                "artifact_ids": [str(artifact_id) for artifact_id in figure.artifact_ids[:8]],
                "job_id": job_id or None,
                **(
                    {
                        "object_id": str(source["object_id"]),
                        "version_id": str(source["version_id"]),
                        "object_type": str(source["object_type"]),
                    }
                    if (
                        source := next(
                            (
                                candidate
                                for candidate in sources
                                if str(candidate["object_type"]) == str(figure.figure_type)
                            ),
                            None,
                        )
                    )
                    else {}
                ),
            }
            for figure in bundle.figures[:16]
        ]
        table_sources = [
            {
                "table_ref": str(table.table_id),
                "title": str(table.title or table.table_type or table.table_id),
                "artifact_ids": [str(artifact_id) for artifact_id in table.artifact_ids[:8]],
                "job_id": job_id or None,
                "source_refs": [
                    {
                        "object_id": str(source["object_id"]),
                        "version_id": str(source["version_id"]),
                        "object_type": str(source["object_type"]),
                    }
                    for source in sources
                ],
            }
            for table in bundle.tables[:16]
        ]
        report = payload.get("report")
        if isinstance(report, dict):
            authored_title = str(report.get("title") or "").strip()
            # Historical provider-composed snapshots remain immutable. Their
            # authorized read model is nevertheless projected through the
            # same deterministic communication boundary as newly generated
            # reports, so older qualitative overclaims are not repeated.
            interpretation_repository = getattr(session.agent2, "interpretations", None)
            interpretation_id = row.get("scientific_interpretation_id")
            if interpretation_repository is not None and interpretation_id is not None:
                interpretation_row = interpretation_repository.get(UUID(str(interpretation_id)))
                report = ScientificReportService._project_authoritative_report(
                    ScientificReportOutput.model_validate(report),
                    bundle=bundle,
                    interpretation=interpretation_row["output_json"],
                    relevance_status=str(
                        payload.get("current_effective_relevance")
                        or row.get("relevance_at_generation")
                        or bundle.relevance_status.value
                    ),
                    source_labels=[
                        str(source.get("display_name") or "")
                        for source in sources
                    ],
                ).model_dump(mode="json")
            if authored_title:
                # The title is bounded communication metadata. Preserve the
                # immutable snapshot's authored revision title while the
                # scientific narrative/facts are re-projected from authority.
                report["title"] = authored_title
            report = {
                **report,
                "research_question": ScientificReportService._friendly_research_question(
                    str(report.get("research_question") or ""),
                    [str(source.get("display_name") or "") for source in sources],
                ),
                # Result provenance is authoritative even when a historical
                # provider response omitted this optional presentation field.
                "data_sources": [str(source["source_ref"]) for source in sources],
            }
        return {
            **payload,
            **({"report": report} if report is not None else {}),
            "viewer_sources": sources,
            "figure_sources": figure_sources,
            "table_sources": table_sources,
        }

    def list_project(self, project_id: str, *, limit: int = 50) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            lifecycle = self._lifecycle_map(session.connection, project_id)
            organization = self._organization_map(session.connection, project_id)
            rows = session.agent2.scientific_reports.list_by_project(project_id, limit=limit)
            items = [
                self._public(
                    row,
                    summary=True,
                    current_relevance=self._current_relevance(session, row),
                    lifecycle_status=lifecycle.get(str(row["report_id"]), "ACTIVE"),
                    organization=organization.get(str(row["report_id"]), {}),
                )
                for row in rows
            ]
            items.sort(
                key=lambda item: (
                    bool(item.get("pinned")),
                    str(item.get("created_at") or ""),
                ),
                reverse=True,
            )
            return {
                "items": items,
                "count": len(rows),
            }

    def set_lifecycle(self, report_id: str, lifecycle: str) -> dict[str, Any]:
        normalized = str(lifecycle).upper()
        if normalized not in {"ACTIVE", "ARCHIVED", "TRASHED"}:
            raise ScientificReportError("REPORT_LIFECYCLE_INVALID", "报告状态不受支持。", 422)
        with self.repository_factory.session() as session:
            row = session.agent2.scientific_reports.get_by_report_id(report_id)
            if row is None:
                raise ScientificReportError("REPORT_NOT_FOUND", "报告不存在。", 404)
            project_id = str(row["project_id"])
            config_row = session.connection.execute(
                select(project_configs.c.config_json)
                .where(project_configs.c.project_id == project_id)
                .with_for_update()
            ).scalar_one_or_none()
            config = dict(config_row) if isinstance(config_row, dict) else {}
            lifecycle_map = dict(config.get("scientificReportLifecycle") or {})
            if normalized == "ACTIVE":
                lifecycle_map.pop(report_id, None)
            else:
                lifecycle_map[report_id] = normalized
            config["scientificReportLifecycle"] = lifecycle_map
            existing = session.connection.execute(
                select(project_configs.c.project_id)
                .where(project_configs.c.project_id == project_id)
            ).scalar_one_or_none()
            if existing is None:
                session.connection.execute(insert(project_configs).values(project_id=project_id, config_json=config))
            else:
                session.connection.execute(
                    update(project_configs)
                    .where(project_configs.c.project_id == project_id)
                    .values(config_json=config, updated_at=func.now())
                )
            organization = self._organization_map(session.connection, project_id).get(report_id, {})
            return self._public(row, lifecycle_status=normalized, organization=organization)

    def bulk_set_lifecycle(
        self,
        project_id: str,
        report_ids: list[str],
        lifecycle: str,
    ) -> dict[str, Any]:
        """Atomically archive or restore a bounded set of project Reports."""
        normalized = str(lifecycle).upper()
        if normalized not in {"ACTIVE", "ARCHIVED"}:
            raise ScientificReportError(
                "REPORT_BULK_LIFECYCLE_INVALID",
                "批量报告状态仅支持归档或恢复。",
                422,
            )
        unique_ids = list(dict.fromkeys(str(value).strip() for value in report_ids))
        if not unique_ids or any(not value for value in unique_ids):
            raise ScientificReportError(
                "REPORT_BULK_SELECTION_INVALID",
                "请选择至少一份有效报告。",
                422,
            )
        if len(unique_ids) > 100:
            raise ScientificReportError(
                "REPORT_BULK_SELECTION_TOO_LARGE",
                "单次最多管理 100 份报告。",
                422,
            )
        with self.repository_factory.session() as session:
            rows: list[dict[str, Any]] = []
            for report_id in unique_ids:
                row = session.agent2.scientific_reports.get_by_report_id(report_id)
                if row is None or str(row["project_id"]) != project_id:
                    raise ScientificReportError(
                        "REPORT_BULK_SCOPE_INVALID",
                        "所选报告不存在或不属于当前项目。",
                        404,
                    )
                rows.append(row)

            config_row = session.connection.execute(
                select(project_configs.c.config_json)
                .where(project_configs.c.project_id == project_id)
                .with_for_update()
            ).scalar_one_or_none()
            config = dict(config_row) if isinstance(config_row, dict) else {}
            lifecycle_map = dict(config.get("scientificReportLifecycle") or {})
            for report_id in unique_ids:
                if normalized == "ACTIVE":
                    lifecycle_map.pop(report_id, None)
                else:
                    lifecycle_map[report_id] = normalized
            if lifecycle_map:
                config["scientificReportLifecycle"] = lifecycle_map
            else:
                config.pop("scientificReportLifecycle", None)

            existing = session.connection.execute(
                select(project_configs.c.project_id)
                .where(project_configs.c.project_id == project_id)
            ).scalar_one_or_none()
            if existing is None:
                session.connection.execute(
                    insert(project_configs).values(
                        project_id=project_id,
                        config_json=config,
                    )
                )
            else:
                session.connection.execute(
                    update(project_configs)
                    .where(project_configs.c.project_id == project_id)
                    .values(config_json=config, updated_at=func.now())
                )

            organization = self._organization_map(session.connection, project_id)
            return {
                "lifecycle": normalized,
                "reportIds": unique_ids,
                "count": len(unique_ids),
                "items": [
                    self._public(
                        row,
                        lifecycle_status=normalized,
                        organization=organization.get(str(row["report_id"]), {}),
                    )
                    for row in rows
                ],
            }

    def set_organization(self, report_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        """Persist bounded non-scientific report navigation metadata."""
        allowed = {"title", "pinned"}
        if not changes or set(changes) - allowed:
            raise ScientificReportError("REPORT_ORGANIZATION_INVALID", "报告组织信息不受支持。", 422)
        with self.repository_factory.session() as session:
            row = session.agent2.scientific_reports.get_by_report_id(report_id)
            if row is None:
                raise ScientificReportError("REPORT_NOT_FOUND", "报告不存在。", 404)
            project_id = str(row["project_id"])
            config_row = session.connection.execute(
                select(project_configs.c.config_json)
                .where(project_configs.c.project_id == project_id)
                .with_for_update()
            ).scalar_one_or_none()
            config = dict(config_row) if isinstance(config_row, dict) else {}
            organization_map = dict(config.get("scientificReportOrganization") or {})
            entry = dict(organization_map.get(report_id) or {})
            if "title" in changes:
                title = str(changes.get("title") or "").strip()
                if len(title) > 256:
                    raise ScientificReportError("REPORT_TITLE_INVALID", "报告名称不能超过 256 个字符。", 422)
                if title:
                    entry["titleOverride"] = title
                else:
                    entry.pop("titleOverride", None)
            if "pinned" in changes:
                if bool(changes.get("pinned")):
                    entry["pinned"] = True
                else:
                    entry.pop("pinned", None)
            if entry:
                organization_map[report_id] = entry
            else:
                organization_map.pop(report_id, None)
            if organization_map:
                config["scientificReportOrganization"] = organization_map
            else:
                config.pop("scientificReportOrganization", None)
            existing = session.connection.execute(
                select(project_configs.c.project_id)
                .where(project_configs.c.project_id == project_id)
            ).scalar_one_or_none()
            if existing is None:
                session.connection.execute(insert(project_configs).values(project_id=project_id, config_json=config))
            else:
                session.connection.execute(
                    update(project_configs)
                    .where(project_configs.c.project_id == project_id)
                    .values(config_json=config, updated_at=func.now())
                )
            lifecycle = self._lifecycle_map(session.connection, project_id).get(report_id, "ACTIVE")
            return self._public(
                row,
                current_relevance=self._current_relevance(session, row),
                lifecycle_status=lifecycle,
                organization=entry,
            )

    def dependency_impact(self, report_id: str) -> dict[str, Any]:
        """Return a bounded, server-derived impact preview for report lifecycle actions.

        The preview is derived from the immutable report snapshot and its
        ScientificResult bundle. It is intentionally read-only: it does not
        mutate lifecycle state or scientific authorities, and it never exposes
        raw infrastructure details.
        """
        with self.repository_factory.session() as session:
            row = session.agent2.scientific_reports.get_by_report_id(report_id)
            if row is None:
                raise ScientificReportError("REPORT_NOT_FOUND", "报告不存在。", 404)
            project_id = str(row["project_id"])
            lifecycle = self._lifecycle_map(session.connection, project_id).get(str(row["report_id"]), "ACTIVE")
            organization = self._organization_map(session.connection, project_id).get(str(row["report_id"]), {})
            view = self._with_viewer_sources(
                self._public(
                    row,
                    current_relevance=self._current_relevance(session, row),
                    lifecycle_status=lifecycle,
                    organization=organization,
                ),
                session,
                row,
            )
            report = view.get("report") if isinstance(view.get("report"), dict) else {}
            dependencies: list[dict[str, str]] = []

            source_research_href = (
                f"/projects/{project_id}/research/{row['research_session_id']}"
                f"?turn={row['research_turn_id']}"
                if row.get("research_session_id") and row.get("research_turn_id")
                else f"/projects/{project_id}/research"
            )

            def add(
                kind: str,
                identity: Any,
                label: str,
                href: str | None = None,
            ) -> None:
                value = str(identity or "").strip()
                if not value or any(item["kind"] == kind and item["id"] == value for item in dependencies):
                    return
                dependencies.append(
                    {
                        "kind": kind,
                        "id": value,
                        "label": label,
                        **({"href": href} if href else {}),
                    }
                )

            add("RESEARCH_TURN", row.get("research_turn_id"), "研究回合", source_research_href)
            add("SCIENTIFIC_RESULT", row.get("scientific_result_snapshot_id"), "ScientificResult", source_research_href)
            add("INTERPRETATION", row.get("scientific_interpretation_id"), "科学解释", source_research_href)
            for source in view.get("viewer_sources") or []:
                if isinstance(source, dict):
                    object_id = source.get("object_id")
                    version_id = source.get("version_id")
                    href = (
                        f"/projects/{project_id}/data?object={object_id}&version={version_id}"
                        if object_id and version_id
                        else f"/projects/{project_id}/data"
                    )
                    add("SCIENTIFIC_OBJECT_VERSION", version_id, f"来源版本 · {source.get('display_name') or '科学对象'}", href)
            for source in view.get("figure_sources") or []:
                if not isinstance(source, dict):
                    continue
                for artifact_id in source.get("artifact_ids") or []:
                    add("ARTIFACT", artifact_id, "图表 Artifact", source_research_href)
            if isinstance(report, dict):
                for evidence_id in report.get("evidence_refs") or []:
                    add("EVIDENCE", evidence_id, "科学证据", source_research_href)
                for source_id in report.get("data_sources") or []:
                    add("DATA_SOURCE", source_id, "报告数据来源")
            dependencies = dependencies[:64]
            return {
                "entity": "scientific_report",
                "entityId": str(row["report_id"]),
                "displayName": view.get("title") or "科学报告",
                "lifecycleStatus": lifecycle,
                "dependencyCount": len(dependencies),
                "dependencies": dependencies,
                "canDelete": False,
                "retentionPolicy": retention_policy_snapshot(
                    manual_purge_supported=False
                ),
                "impact": {
                    "removedFromActiveDiscovery": True,
                    "historicalProvenanceProtected": True,
                    "historicalResearchRemainsAccessible": True,
                    "scientificSnapshotMutated": False,
                },
            }

    @staticmethod
    def _current_relevance(session: Any, row: dict[str, Any]) -> str:
        snapshot = session.agent2.scientific_result_snapshots.get(row["scientific_result_snapshot_id"])
        bundle = ScientificResultBundle.model_validate(snapshot["bundle_json"])
        objects: dict[str, dict[str, Any]] = {}
        versions: dict[str, dict[str, Any]] = {}
        for ref in bundle.source_object_refs:
            try:
                objects[str(ref.object_id)] = session.agent2.scientific_objects.get_object(ref.object_id)
                versions[str(ref.version_id)] = session.agent2.scientific_objects.get_version(ref.version_id)
            except Exception:
                continue
        return ScientificResultRelevanceEvaluator().evaluate(
            bundle.source_object_refs,
            objects=objects,
            versions=versions,
        ).value

    @staticmethod
    def _public(
        row: dict[str, Any],
        *,
        summary: bool = False,
        current_relevance: str | None = None,
        lifecycle_status: str = "ACTIVE",
        organization: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = dict(row.get("report_json") or {}).get("snapshot") or {}
        report = payload.get("report") or {}
        organization = organization or {}
        revision = ScientificReportService._revision_metadata(row)
        source_title = row.get("report_json", {}).get("snapshot", {}).get("title") or report.get("title")
        return {
            "report_id": str(row["report_id"]), "snapshot_id": str(row["id"]), "project_id": str(row["project_id"]),
            "research_session_id": payload.get("research_session_id"),
            "research_turn_id": str(row["research_turn_id"]), "scientific_result_snapshot_id": str(row["scientific_result_snapshot_id"]),
            "scientific_interpretation_id": str(row["scientific_interpretation_id"]),
            "title": organization.get("titleOverride") or source_title,
            "source_title": source_title,
            "pinned": bool(organization.get("pinned")),
            "revision_group_id": str(
                revision.get("revision_group_id") or row["report_id"]
            ),
            "parent_report_id": revision.get("parent_report_id"),
            "parent_snapshot_id": revision.get("parent_snapshot_id"),
            "revision_number": int(revision.get("revision_number") or 1),
            "revision_reason": revision.get("revision_reason") or "ORIGINAL",
            "relevance_at_generation": row["relevance_at_generation"],
            "current_effective_relevance": current_relevance or row["relevance_at_generation"],
            "grounding_status": row["grounding_status"],
            "lifecycle_status": lifecycle_status,
            "scientific_context": report.get("research_question") or "",
            "finding_count": len(report.get("main_findings") or []),
            "figure_count": len(report.get("primary_figures") or []),
            "source_fingerprint": row["source_fingerprint"], "created_at": row.get("created_at").isoformat() if hasattr(row.get("created_at"), "isoformat") else row.get("created_at"),
            **({"report": report} if not summary else {}),
        }

    @staticmethod
    def _lifecycle_map(connection: Any, project_id: str) -> dict[str, str]:
        row = connection.execute(
            select(project_configs.c.config_json).where(project_configs.c.project_id == project_id)
        ).scalar_one_or_none()
        config = row if isinstance(row, dict) else {}
        values = config.get("scientificReportLifecycle") if isinstance(config, dict) else {}
        return {
            str(key): str(value).upper()
            for key, value in (values.items() if isinstance(values, dict) else [])
            if str(value).upper() in {"ARCHIVED", "TRASHED"}
        }

    @staticmethod
    def _organization_map(connection: Any, project_id: str) -> dict[str, dict[str, Any]]:
        row = connection.execute(
            select(project_configs.c.config_json).where(project_configs.c.project_id == project_id)
        ).scalar_one_or_none()
        config = row if isinstance(row, dict) else {}
        values = config.get("scientificReportOrganization") if isinstance(config, dict) else {}
        result: dict[str, dict[str, Any]] = {}
        for key, value in (values.items() if isinstance(values, dict) else []):
            if not isinstance(value, dict):
                continue
            title = str(value.get("titleOverride") or "").strip()
            entry: dict[str, Any] = {}
            if title:
                entry["titleOverride"] = title[:256]
            if bool(value.get("pinned")):
                entry["pinned"] = True
            if entry:
                result[str(key)] = entry
        return result


__all__ = ["ScientificReportError", "ScientificReportService"]
