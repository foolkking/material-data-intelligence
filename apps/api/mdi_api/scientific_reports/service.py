from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid5, NAMESPACE_URL

from pydantic import ValidationError

from mdi_api.scientific_results.relevance import ScientificResultRelevanceEvaluator
from mdi_api.scientific_results.schemas import ScientificResultBundle
from mdi_api.unit_of_work import RepositoryFactory

from .assembler import ReportComposerInputAssembler
from .client import DeepSeekReportComposerClient, StructuredReportComposerClient
from .grounding import ReportGroundingValidator
from .schemas import REPORT_COMPOSER_PROMPT_VERSION, REPORT_COMPOSER_VERSION, ScientificReportOutput, ScientificReportSnapshot


class ScientificReportError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


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
            snapshot = session.agent2.scientific_result_snapshots.get_latest_for_turn(turn_id)
            interpretation = session.agent2.interpretations.get_for_turn(turn_id)
            if interpretation is None:
                raise ScientificReportError("REPORT_INTERPRETATION_NOT_READY", "报告需要已验证的 ScientificInterpretation。", 409)
            bundle = ScientificResultBundle.model_validate(snapshot["bundle_json"])
            objects: dict[str, dict[str, Any]] = {}
            versions: dict[str, dict[str, Any]] = {}
            for ref in bundle.source_object_refs:
                try:
                    objects[str(ref.object_id)] = session.agent2.scientific_objects.get_object(ref.object_id)
                    versions[str(ref.version_id)] = session.agent2.scientific_objects.get_version(ref.version_id)
                except Exception:
                    pass
            relevance = ScientificResultRelevanceEvaluator().evaluate(bundle.source_object_refs, objects=objects, versions=versions).value
            input_payload, input_fingerprint = self.assembler.assemble(bundle=bundle, interpretation=interpretation["output_json"], relevance_status=relevance)
        output, provider_meta, repair_attempted = self._compose_with_one_repair(
            input_payload=input_payload,
            bundle=bundle,
            interpretation=interpretation["output_json"],
        )
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            snapshot = session.agent2.scientific_result_snapshots.get_latest_for_turn(turn_id)
            interpretation = session.agent2.interpretations.get_for_turn(turn_id)
            if interpretation is None:
                raise ScientificReportError("REPORT_INTERPRETATION_NOT_READY", "报告需要已验证的 ScientificInterpretation。", 409)
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
                "contract_version": "1.0", "composer_version": REPORT_COMPOSER_VERSION,
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
            return self._with_viewer_sources(self._public(row, current_relevance=self._current_relevance(session, row)), session, row)

    def get_by_report_id(self, report_id: str) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            row = session.agent2.scientific_reports.get_by_report_id(report_id)
            if row is None:
                raise ScientificReportError("REPORT_NOT_FOUND", "报告不存在。", 404)
            return self._with_viewer_sources(self._public(row, current_relevance=self._current_relevance(session, row)), session, row)

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
            }
            for figure in bundle.figures[:16]
        ]
        return {**payload, "viewer_sources": sources, "figure_sources": figure_sources}

    def list_project(self, project_id: str, *, limit: int = 50) -> dict[str, Any]:
        with self.repository_factory.session() as session:
            rows = session.agent2.scientific_reports.list_by_project(project_id, limit=limit)
            return {
                "items": [
                    self._public(
                        row,
                        summary=True,
                        current_relevance=self._current_relevance(session, row),
                    )
                    for row in rows
                ],
                "count": len(rows),
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
    ) -> dict[str, Any]:
        payload = dict(row.get("report_json") or {}).get("snapshot") or {}
        report = payload.get("report") or {}
        return {
            "report_id": str(row["report_id"]), "snapshot_id": str(row["id"]), "project_id": str(row["project_id"]),
            "research_turn_id": str(row["research_turn_id"]), "scientific_result_snapshot_id": str(row["scientific_result_snapshot_id"]),
            "scientific_interpretation_id": str(row["scientific_interpretation_id"]), "title": row.get("report_json", {}).get("snapshot", {}).get("title") or report.get("title"),
            "relevance_at_generation": row["relevance_at_generation"],
            "current_effective_relevance": current_relevance or row["relevance_at_generation"],
            "grounding_status": row["grounding_status"],
            "scientific_context": report.get("research_question") or "",
            "finding_count": len(report.get("main_findings") or []),
            "figure_count": len(report.get("primary_figures") or []),
            "source_fingerprint": row["source_fingerprint"], "created_at": row.get("created_at").isoformat() if hasattr(row.get("created_at"), "isoformat") else row.get("created_at"),
            **({"report": report} if not summary else {}),
        }


__all__ = ["ScientificReportError", "ScientificReportService"]
