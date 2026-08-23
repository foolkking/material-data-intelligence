from __future__ import annotations

from typing import Any, Callable
from uuid import UUID, uuid4

from mdi_api.agent2_errors import (
    InvalidScientificObjectVersion,
    ScientificResultNotReady,
    ScientificResultProjectionConflict,
    ScientificResultProjectionFailed,
    ScientificResultSourceUnavailable,
)
from mdi_api.research_agent.schemas import ResearchTurnEventType, ResearchTurnStatus
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.scientific_results.fingerprint import ScientificResultSourceFingerprint
from mdi_api.scientific_results.projectors.base import ScientificResultProjectionContext
from mdi_api.scientific_results.schemas import ScientificResultBundle
from mdi_api.unit_of_work import RepositoryFactory


ArtifactLoader = Callable[[dict[str, Any]], Any]


class ScientificResultSnapshotService:
    """Phase 1 snapshot CRUD retained as the low-level persistence API."""

    def __init__(self, repository_factory: RepositoryFactory) -> None:
        self.repository_factory = repository_factory

    def persist_snapshot(self, bundle: ScientificResultBundle, source_fingerprint: str, *, job_id: str | None = None) -> dict[str, Any]:
        if not source_fingerprint.strip():
            raise ValueError("source_fingerprint is required")
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get(bundle.research_turn_id)
            if turn["project_id"] != bundle.project_id or turn["research_session_id"] != bundle.research_session_id:
                raise InvalidScientificObjectVersion("result bundle scope does not match its ResearchTurn")
            for ref in [*bundle.source_object_refs, *bundle.output_object_refs, *[ref for item in bundle.result_items for ref in item.scientific_object_refs]]:
                logical = unit.agent2.scientific_objects.get_object(ref.object_id)
                version = unit.agent2.scientific_objects.get_version(ref.version_id)
                if logical["project_id"] != bundle.project_id or ref.project_id != bundle.project_id or version["scientific_object_id"] != logical["id"] or logical["object_type"] != ref.object_type or version["object_type"] != ref.object_type:
                    raise InvalidScientificObjectVersion("result bundle contains an unauthorized or inconsistent ScientificObjectRef")
            existing = unit.agent2.scientific_result_snapshots.get_by_identity(bundle.research_turn_id, bundle.projection_version, source_fingerprint)
            if existing:
                return existing
            return unit.agent2.scientific_result_snapshots.add({
                "id": uuid4(), "project_id": bundle.project_id, "research_turn_id": bundle.research_turn_id,
                "job_id": job_id, "schema_version": bundle.schema_version, "projection_version": bundle.projection_version,
                "execution_status": bundle.execution_status.value, "relevance_status": bundle.relevance_status.value,
                "source_fingerprint": source_fingerprint, "bundle_json": bundle.model_dump(mode="json"),
            })

    def get_latest_for_turn(self, turn_id: UUID) -> ScientificResultBundle:
        with self.repository_factory.session() as session:
            row = session.agent2.scientific_result_snapshots.get_latest_for_turn(turn_id)
            return ScientificResultBundle.model_validate(row["bundle_json"])

    def list_for_turn(self, turn_id: UUID) -> list[ScientificResultBundle]:
        with self.repository_factory.session() as session:
            return [ScientificResultBundle.model_validate(row["bundle_json"]) for row in session.agent2.scientific_result_snapshots.list_for_turn(turn_id)]


class ScientificResultProjectionService:
    """Read-only execution-fact projection with immutable snapshot persistence."""

    projection_version = "agent2.result/1.0"

    def __init__(self, repository_factory: RepositoryFactory, *, projector_registry: Any | None = None, artifact_loader: ArtifactLoader | None = None) -> None:
        self.repository_factory = repository_factory
        if projector_registry is None:
            from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES
            projector_registry = DEFAULT_AGENT2_REGISTRIES.result_projectors
        self.projector_registry = projector_registry
        self.artifact_loader = artifact_loader or self._missing_artifact_loader

    @staticmethod
    def _missing_artifact_loader(_artifact: dict[str, Any]) -> Any:
        raise FileNotFoundError("an explicit committed Artifact loader is required")

    def project_turn(self, turn_id: UUID) -> dict[str, Any]:
        try:
            context, existing = self._load_projection_context(turn_id)
        except Exception:
            self._append_event_if_possible(turn_id, "RESULT_PROJECTION_FAILED", {"code": "RESULT_PROJECTION_FAILED"})
            raise
        if existing is None:
            self._append_event_if_possible(turn_id, "RESULT_PROJECTION_STARTED", {})
        projector_ids = self._projector_ids(context)
        if not projector_ids:
            raise ScientificResultProjectionFailed("no registered result projector for capability plan")
        context = ScientificResultProjectionContext(**{**context.__dict__, "projector_ids": tuple(projector_ids)})
        projections = []
        for projector_id in projector_ids:
            try:
                projector = self.projector_registry.require(projector_id)
            except KeyError as exc:
                raise ScientificResultProjectionFailed(f"result projector is not registered: {projector_id}", code="RESULT_PROJECTOR_NOT_REGISTERED") from exc
            projections.append(projector.project(self._context_for_projector(context, projector_id)))
        bundle = self._merge_projections(context, projections).bundle
        source_fingerprint = ScientificResultSourceFingerprint.compute(
            research_turn_id=context.research_turn_id,
            execution_summary=context.execution_summary,
            analysis_plan=context.analysis_plan,
            capability_plan=context.capability_plan,
            source_object_refs=[ref.model_dump(mode="json") for ref in context.source_object_refs],
            tool_calls=list(context.tool_calls),
            artifacts=list(context.artifacts),
            projector_ids=projector_ids,
            projection_version=self.projection_version,
        )
        if existing is not None:
            if str(existing["source_fingerprint"]) != source_fingerprint:
                raise ScientificResultProjectionConflict("immutable result projection fingerprint changed")
            self._reconcile_ready(turn_id)
            return existing
        return self._persist(turn_id, bundle, source_fingerprint, context.execution_summary.get("job_id"))

    def project_context(self, context: ScientificResultProjectionContext) -> ScientificResultBundle:
        projector_ids = self._projector_ids(context)
        context = ScientificResultProjectionContext(**{**context.__dict__, "projector_ids": tuple(projector_ids)})
        projections = [self.projector_registry.require(projector_id).project(self._context_for_projector(context, projector_id)) for projector_id in projector_ids]
        return self._merge_projections(context, projections).bundle

    def _load_projection_context(self, turn_id: UUID) -> tuple[ScientificResultProjectionContext, dict[str, Any] | None]:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            if str(turn["status"]) not in {ResearchTurnStatus.RESULT_PENDING.value, ResearchTurnStatus.RESULT_READY.value}:
                raise ScientificResultNotReady(str(turn_id))
            summary = session.agent2.research_execution_summaries.get_for_turn(turn_id)
            if summary is None:
                raise ScientificResultProjectionFailed("execution summary is missing", code="RESULT_PROJECTION_FAILED")
            existing_rows = session.agent2.scientific_result_snapshots.list_for_turn(turn_id)
            existing = next((row for row in existing_rows if str(row["projection_version"]) == self.projection_version), None)
            if existing is None and str(summary.get("execution_outcome")) not in {"SUCCESS", "PARTIAL"}:
                raise ScientificResultProjectionFailed("only successful or partial executions can be projected", code="RESULT_PROJECTION_FAILED")
            context = self._context_from_rows(session, turn, summary)
        return self._load_artifact_payloads(context), existing

    def _context_from_rows(self, session: Any, turn: dict[str, Any], summary: dict[str, Any]) -> ScientificResultProjectionContext:
        plan = session.repositories.analysis_plans.get_plan(str(turn.get("analysis_plan_id")))
        cap = session.agent2.research_capability_plans.get_for_turn(turn["id"])
        resolution = session.agent2.research_capability_resolutions.get_for_turn(turn["id"])
        if cap is None:
            raise ScientificResultProjectionFailed("capability plan is missing")
        snapshot = session.agent2.research_context_snapshots.get_for_turn(turn["id"])
        if snapshot is None:
            raise ScientificResultProjectionFailed("context snapshot is missing")
        refs = self._snapshot_refs(snapshot, str(turn["project_id"]))
        for ref in refs:
            logical = session.agent2.scientific_objects.get_object(ref.object_id)
            version = session.agent2.scientific_objects.get_version(ref.version_id)
            if str(logical["project_id"]) != str(turn["project_id"]) or str(version["scientific_object_id"]) != str(ref.object_id) or str(version["availability_status"]) in {"SOURCE_MISSING", "INVALID"}:
                raise ScientificResultSourceUnavailable(f"exact source version is unavailable: {ref.version_id}")
        job_id = str(summary["job_id"])
        tool_calls = tuple(self._as_dict(item) for item in session.repositories.tool_calls.list_for_job(job_id))
        artifacts = tuple(self._as_dict(item) for item in session.repositories.artifacts.list_for_job(job_id))
        plan_json = plan.get("analysisPlan") or plan.get("analysis_plan") or plan
        capability_plan = dict(cap.get("plan_json") or {})
        if resolution:
            candidates = (resolution.get("resolution_json") or {}).get("candidates") or []
            by_key = {f"cap_{index}": item for index, item in enumerate(sorted(candidates, key=lambda item: (item.get("planning_priority", 100), item.get("capability_id", ""), item.get("capability_version", ""))), 1)}
            for step in capability_plan.get("steps") or []:
                candidate = by_key.get(step.get("capability_ref_key"))
                if candidate:
                    step["capability_id"] = candidate.get("capability_id")
                    step["capability_version"] = candidate.get("capability_version")
        return ScientificResultProjectionContext(
            project_id=str(turn["project_id"]), research_session_id=str(turn["research_session_id"]),
            research_turn_id=str(turn["id"]), research_question=str((snapshot.get("research_goal") or plan_json.get("goal") or "Scientific analysis")),
            execution_summary={**summary, "id": summary.get("id")},
            capability_plan=capability_plan, analysis_plan=plan_json,
            tool_calls=tool_calls, artifacts=artifacts, artifact_payloads={},
            source_object_refs=tuple(refs), projector_ids=tuple(),
        )

    def _load_artifact_payloads(self, context: ScientificResultProjectionContext) -> ScientificResultProjectionContext:
        payloads: dict[str, Any] = {}
        for artifact in context.artifacts:
            try:
                payloads[str(artifact.get("id"))] = self.artifact_loader(artifact)
            except (FileNotFoundError, KeyError, OSError) as exc:
                raise ScientificResultSourceUnavailable(f"committed artifact payload unavailable: {artifact.get('id')}") from exc
        return ScientificResultProjectionContext(**{**context.__dict__, "artifact_payloads": payloads})

    @staticmethod
    def _snapshot_refs(snapshot: dict[str, Any], project_id: str) -> list[ScientificObjectRef]:
        refs: dict[tuple[str, str], ScientificObjectRef] = {}
        for key in ("active_scope_refs_json", "selection_refs_json", "resolved_references_json"):
            raw = snapshot.get(key) or []
            if isinstance(raw, dict):
                raw = list(raw.values())
            for item in raw:
                if isinstance(item, dict) and item.get("object_id") and item.get("version_id"):
                    ref = ScientificObjectRef.model_validate(item)
                    if ref.project_id != project_id:
                        raise InvalidScientificObjectVersion("result source reference belongs to another project")
                    refs[(str(ref.object_id), str(ref.version_id))] = ref
                elif isinstance(item, dict) and item.get("selected_ref"):
                    ref = ScientificObjectRef.model_validate(item["selected_ref"])
                    if ref.project_id != project_id:
                        raise InvalidScientificObjectVersion("result source reference belongs to another project")
                    refs[(str(ref.object_id), str(ref.version_id))] = ref
        return [refs[key] for key in sorted(refs)]

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")
        return dict(value)

    @staticmethod
    def _projector_ids(context: ScientificResultProjectionContext) -> list[str]:
        ids: list[str] = []
        for step in context.capability_plan.get("steps") or []:
            capability_id = step.get("capability_id") or step.get("capabilityId")
            if capability_id:
                ids.append(f"agent2.{capability_id}")
        return sorted(set(ids))

    @staticmethod
    def _context_for_projector(context: ScientificResultProjectionContext, projector_id: str) -> ScientificResultProjectionContext:
        capability_id = projector_id.removeprefix("agent2.")
        steps = [step for step in context.capability_plan.get("steps") or [] if str(step.get("capability_id")) == capability_id]
        step_ids = {str(step.get("step_id") or step.get("stepId")) for step in steps}
        calls = tuple(call for call in context.tool_calls if str(call.get("stepId") or call.get("step_id")) in step_ids)
        call_ids = {str(call.get("id")) for call in calls}
        artifacts = tuple(artifact for artifact in context.artifacts if str(artifact.get("toolCallId") or artifact.get("tool_call_id")) in call_ids or str(artifact.get("stepId") or artifact.get("step_id")) in step_ids)
        if not artifacts and len(context.projector_ids) <= 1:
            artifacts = context.artifacts
        payloads = {str(item.get("id")): context.artifact_payloads.get(str(item.get("id"))) for item in artifacts}
        return ScientificResultProjectionContext(**{
            **context.__dict__, "capability_plan": {**context.capability_plan, "steps": steps},
            "tool_calls": calls, "artifacts": artifacts, "artifact_payloads": payloads,
        })

    @staticmethod
    def _merge_projections(context: ScientificResultProjectionContext, projections: list[Any]) -> Any:
        if len(projections) == 1:
            return projections[0]
        first = projections[0]
        bundle = first.bundle.model_copy(deep=True)
        for projection in projections[1:]:
            other = projection.bundle
            bundle.result_items.extend(other.result_items)
            bundle.facts.extend(other.facts)
            bundle.figures.extend(other.figures)
            bundle.tables.extend(other.tables)
            bundle.evidence.extend(other.evidence)
            bundle.methods.extend(other.methods)
            bundle.limitations.extend(other.limitations)
            bundle.warnings.extend(other.warnings)
            bundle.provenance.projector_ids.extend(other.provenance.projector_ids)
            bundle.provenance.tool_call_ids.extend(other.provenance.tool_call_ids)
            bundle.provenance.artifact_ids.extend(other.provenance.artifact_ids)
        bundle.provenance.projector_ids = sorted(set(bundle.provenance.projector_ids))
        bundle.provenance.tool_call_ids = sorted(set(bundle.provenance.tool_call_ids))
        bundle.provenance.artifact_ids = sorted(set(bundle.provenance.artifact_ids))
        return type(first)(bundle=ScientificResultBundle.model_validate(bundle.model_dump()), projector_id="agent2.composite", projector_version="1.0")

    def _persist(self, turn_id: UUID, bundle: ScientificResultBundle, source_fingerprint: str, job_id: str | None) -> dict[str, Any]:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            same_version = [row for row in unit.agent2.scientific_result_snapshots.list_for_turn(turn_id) if str(row["projection_version"]) == self.projection_version]
            if same_version:
                existing = same_version[0]
                if str(existing["source_fingerprint"]) != source_fingerprint:
                    raise ScientificResultProjectionConflict("immutable result projection fingerprint changed")
                self._ready_if_needed(unit, turn)
                return existing
            if str(turn["status"]) == ResearchTurnStatus.RESULT_READY.value:
                raise ScientificResultProjectionConflict("RESULT_READY turn has no matching immutable snapshot")
            row = unit.agent2.scientific_result_snapshots.add({
                "id": uuid4(), "project_id": bundle.project_id, "research_turn_id": turn_id, "job_id": job_id,
                "schema_version": bundle.schema_version, "projection_version": bundle.projection_version,
                "execution_status": bundle.execution_status.value, "relevance_status": bundle.relevance_status.value,
                "source_fingerprint": source_fingerprint, "bundle_json": bundle.model_dump(mode="json"),
            })
            self._event(unit, turn_id, ResearchTurnEventType.RESULT_PROJECTED, {"snapshot_id": str(row["id"]), "source_fingerprint": source_fingerprint})
            current = unit.agent2.research_turns.get_for_update(turn_id)
            unit.agent2.research_turns.compare_and_set_status(turn_id, expected_status=ResearchTurnStatus.RESULT_PENDING.value, expected_version=int(current["row_version"]), target_status=ResearchTurnStatus.RESULT_READY.value)
            self._event(unit, turn_id, ResearchTurnEventType.RESULT_READY, {"snapshot_id": str(row["id"])})
            return row

    @staticmethod
    def _ready_if_needed(unit: Any, turn: dict[str, Any]) -> None:
        if str(turn["status"]) == ResearchTurnStatus.RESULT_PENDING.value:
            unit.agent2.research_turns.compare_and_set_status(turn["id"], expected_status=ResearchTurnStatus.RESULT_PENDING.value, expected_version=int(turn["row_version"]), target_status=ResearchTurnStatus.RESULT_READY.value)

    def _reconcile_ready(self, turn_id: UUID) -> None:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            if str(turn["status"]) != ResearchTurnStatus.RESULT_PENDING.value:
                return
            updated = unit.agent2.research_turns.compare_and_set_status(
                turn_id, expected_status=ResearchTurnStatus.RESULT_PENDING.value,
                expected_version=int(turn["row_version"]), target_status=ResearchTurnStatus.RESULT_READY.value,
            )
            self._event(unit, turn_id, ResearchTurnEventType.RESULT_READY, {"status": updated["status"]})

    @staticmethod
    def _event(unit: Any, turn_id: UUID, event_type: ResearchTurnEventType, payload: dict[str, Any]) -> None:
        sequence = unit.agent2.research_turn_events.next_sequence_no(turn_id)
        unit.agent2.research_turn_events.append_turn_event({"id": uuid4(), "turn_id": turn_id, "sequence_no": sequence, "event_type": event_type.value, "payload_json": payload})

    def _append_event_if_possible(self, turn_id: UUID, event_type: str, payload: dict[str, Any]) -> None:
        try:
            with self.repository_factory.unit_of_work() as unit:
                unit.agent2.research_turns.get(turn_id)
                self._event(unit, turn_id, ResearchTurnEventType(event_type), payload)
        except (KeyError, ValueError, LookupError):
            return
