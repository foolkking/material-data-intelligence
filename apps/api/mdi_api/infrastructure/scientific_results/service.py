from __future__ import annotations

import logging
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
from mdi_api.domain.scientific_objects.contracts import ScientificObjectRef
from mdi_api.domain.scientific_results.fingerprint import ScientificResultSourceFingerprint
from mdi_api.application.scientific_results.projectors.base import ScientificResultProjectionContext
from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.unit_of_work import RepositoryFactory


ArtifactLoader = Callable[[dict[str, Any]], Any]
logger = logging.getLogger(__name__)


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
            projections.extend(projector.project(scoped) for scoped in self._contexts_for_projector(context, projector_id))
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
            self._enqueue_interpretation(turn_id)
            return existing
        row = self._persist(turn_id, bundle, source_fingerprint, context.execution_summary.get("job_id"))
        self._enqueue_interpretation(turn_id)
        return row

    def project_context(self, context: ScientificResultProjectionContext) -> ScientificResultBundle:
        projector_ids = self._projector_ids(context)
        context = ScientificResultProjectionContext(**{**context.__dict__, "projector_ids": tuple(projector_ids)})
        projections = [self.projector_registry.require(projector_id).project(scoped)
                       for projector_id in projector_ids for scoped in self._contexts_for_projector(context, projector_id)]
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
        message = session.agent2.research_turns.get_message(str(turn["user_message_id"]))
        question = message.get("content_summary")
        if (
            message.get("role") != "user"
            or str(message.get("session_id")) != str(turn["research_session_id"])
            or not isinstance(question, str)
            or not question.strip()
        ):
            raise ScientificResultProjectionFailed("original research question is unavailable or inconsistent")
        plan = session.repositories.analysis_plans.get_plan(str(turn.get("analysis_plan_id")))
        cap = session.agent2.research_capability_plans.get_for_turn(turn["id"])
        resolution = session.agent2.research_capability_resolutions.get_for_turn(turn["id"])
        if cap is None:
            raise ScientificResultProjectionFailed("capability plan is missing")
        snapshot = session.agent2.research_context_snapshots.get_for_turn(turn["id"])
        if snapshot is None:
            raise ScientificResultProjectionFailed("context snapshot is missing")
        plan_json = plan.get("analysisPlan") or plan.get("analysis_plan") or plan
        project_scoped = plan_json.get("schemaVersion") == "0.4"
        if project_scoped:
            from mdi_schemas import AnalysisPlanV04
            validated_plan = AnalysisPlanV04.model_validate(plan_json)
            if validated_plan.projectId != str(turn["project_id"]):
                raise ScientificResultProjectionFailed("project reference plan belongs to another project")
        refs = [] if project_scoped else self._snapshot_refs(snapshot, str(turn["project_id"]))
        for index, ref in enumerate(refs):
            logical = session.agent2.scientific_objects.get_object(ref.object_id)
            version = session.agent2.scientific_objects.get_version(ref.version_id)
            if str(logical["project_id"]) != str(turn["project_id"]) or str(version["scientific_object_id"]) != str(ref.object_id) or str(version["availability_status"]) in {"SOURCE_MISSING", "INVALID"}:
                raise ScientificResultSourceUnavailable(f"exact source version is unavailable: {ref.version_id}")
            if len(refs) > 1:
                profile_ref = version.get("semantic_profile_ref_json") or {}
                if profile_ref.get("profileId"):
                    profile = session.repositories.data_profiles.get(str(profile_ref["profileId"]))
                    label = self._source_file_label(version, profile)
                    if label:
                        refs[index] = ref.model_copy(update={"display_name": label})
        job_id = str(summary["job_id"])
        job = session.repositories.jobs.get(job_id)
        self._validate_execution_identity(turn, summary, plan, cap, job)
        current_attempt = int(job.get("executionAttempt") or 0)
        tool_calls = tuple(
            self._as_dict(item)
            for item in session.repositories.tool_calls.list_for_job(job_id)
            if not current_attempt
            or int(self._as_dict(item).get("attempt") or 0) == current_attempt
        )
        current_call_ids = {str(item.get("id")) for item in tool_calls}
        artifacts = tuple(
            self._as_dict(item)
            for item in session.repositories.artifacts.list_for_job(job_id)
            if not current_attempt
            or str(self._as_dict(item).get("toolCallId") or "")
            in current_call_ids
        )
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
            research_turn_id=str(turn["id"]), research_question=question,
            execution_summary={**summary, "id": summary.get("id")},
            capability_plan=capability_plan, analysis_plan=plan_json,
            tool_calls=tool_calls, artifacts=artifacts, artifact_payloads={},
            source_object_refs=tuple(refs), projector_ids=tuple(),
            scientific_selections=() if project_scoped else tuple(snapshot.get("scientific_selections_json") or ()),
            analysis_plan_id=str(plan["planId"]), capability_plan_id=str(cap["id"]),
        )

    @staticmethod
    def _validate_execution_identity(
        turn: dict[str, Any], summary: dict[str, Any], plan: dict[str, Any],
        capability_plan: dict[str, Any], job: dict[str, Any],
    ) -> None:
        payload = summary.get("summary_json") or {}
        identities = (
            (turn.get("id"), (
                summary.get("research_turn_id"), payload.get("research_turn_id"),
                capability_plan.get("research_turn_id"),
            )),
            (turn.get("project_id"), (plan.get("projectId"), job.get("projectId"))),
            (turn.get("analysis_plan_id"), (
                plan.get("planId"), job.get("planId"), payload.get("analysis_plan_id"),
            )),
            (turn.get("job_id"), (summary.get("job_id"), payload.get("job_id"), job.get("id"))),
        )
        if not capability_plan.get("id") or any(
            not expected or any(str(actual or "") != str(expected) for actual in values)
            for expected, values in identities
        ):
            raise ScientificResultProjectionFailed("execution provenance is inconsistent")

    @staticmethod
    def _source_file_label(version: dict[str, Any], profile: dict[str, Any]) -> str | None:
        """Name a resource only through its saved exact Profile/file edges."""
        profile_ref = version.get("semantic_profile_ref_json") or {}
        if any(str(profile.get(key) or "") != str(profile_ref.get(key) or "")
               for key in ("profileId", "datasetId", "semanticHash")):
            return None
        resources = [item for item in profile.get("objects", [])
                     if item.get("objectId") == profile_ref.get("resourceId")
                     and item.get("objectHash") == profile_ref.get("resourceHash")]
        if len(resources) != 1:
            return None
        names = []
        for file_id in resources[0].get("sourceFileIds", []):
            files = [item for item in profile.get("files", []) if item.get("fileId") == file_id]
            if len(files) != 1:
                return None
            name = str(files[0].get("fileName") or "")
            if not name or len(name) > 240 or any(char in name for char in ("/", "\\", "\n", "\r")):
                return None
            names.append(name)
        label = ", ".join(dict.fromkeys(names))
        return label if label and len(label) <= 512 else None

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
        summary_payload = context.execution_summary.get("summary_json") or {}
        successful_step_ids = {
            str(step_id)
            for step_id in (
                context.execution_summary.get("successful_step_ids")
                or summary_payload.get("successful_step_ids")
                or []
            )
        }
        if not successful_step_ids:
            successful_step_ids = {
                str(step.get("step_id") or step.get("stepId"))
                for step in (summary_payload.get("steps") or [])
                if str(step.get("status") or "").upper() == "SUCCEEDED"
            }
        outcome = str(
            context.execution_summary.get("execution_outcome")
            or context.execution_summary.get("outcome")
            or summary_payload.get("outcome")
            or "SUCCESS"
        )
        ids: list[str] = []
        for step in context.capability_plan.get("steps") or []:
            step_id = str(step.get("step_id") or step.get("stepId") or "")
            if outcome == "PARTIAL" and step_id not in successful_step_ids:
                continue
            capability_id = step.get("capability_id") or step.get("capabilityId")
            if capability_id:
                ids.append(f"agent2.{capability_id}")
        return sorted(set(ids))

    @staticmethod
    def _contexts_for_projector(context: ScientificResultProjectionContext, projector_id: str) -> list[ScientificResultProjectionContext]:
        steps = [step for step in context.capability_plan.get("steps") or []
                 if str(step.get("capability_id")) == projector_id.removeprefix("agent2.")]
        if len(steps) <= 1:
            return [ScientificResultProjectionService._context_for_projector(context, projector_id)]
        contexts = []
        for step in steps:
            step_id = str(step.get("step_id") or step.get("stepId"))
            scoped = ScientificResultProjectionContext(**{
                **context.__dict__, "capability_plan": {**context.capability_plan, "steps": [step]},
                "projection_scope_key": step_id,
            })
            # Apply the execution outcome per invocation, including repeated
            # uses of the same capability in a partially successful Job.
            if projector_id in ScientificResultProjectionService._projector_ids(scoped):
                contexts.append(ScientificResultProjectionService._context_for_projector(scoped, projector_id))
        return contexts

    @staticmethod
    def _context_for_projector(context: ScientificResultProjectionContext, projector_id: str) -> ScientificResultProjectionContext:
        capability_id = projector_id.removeprefix("agent2.")
        steps = [step for step in context.capability_plan.get("steps") or [] if str(step.get("capability_id")) == capability_id]
        step_ids = {str(step.get("step_id") or step.get("stepId")) for step in steps}
        analysis_steps = [
            step
            for step in context.analysis_plan.get("steps") or []
            if (
                str(step.get("stepId") or step.get("step_id")) in step_ids
                or str(
                    (step.get("output") or {}).get("capabilityPlanStepId") or ""
                )
                in step_ids
            )
        ]
        analysis_step_ids = {
            str(step.get("stepId") or step.get("step_id"))
            for step in analysis_steps
        }
        bound_version_ids = {
            str(input_ref.get("ref"))
            for step in analysis_steps
            for input_ref in (step.get("inputRefs") or step.get("input_refs") or [])
            if str(input_ref.get("refType") or input_ref.get("ref_type") or "")
            == "normalized_object"
        }
        bound_version_ids.update(
            str(version_id) for step in analysis_steps
            for version_id in (step.get("output") or {}).get("sourceObjectVersionIds", [])
        )
        exact_source_refs = tuple(
            ref
            for ref in context.source_object_refs
            if str(ref.version_id) in bound_version_ids
        )
        # Modern AnalysisPlans bind exact ScientificObjectVersion IDs. Legacy
        # plans without that binding retain the complete source set rather
        # than guessing a single source and manufacturing false provenance.
        project_scoped = context.analysis_plan.get("schemaVersion") == "0.4"
        projector_source_refs = () if project_scoped else exact_source_refs or context.source_object_refs
        calls = tuple(
            call
            for call in context.tool_calls
            if str(call.get("stepId") or call.get("step_id"))
            in analysis_step_ids
        )
        if context.projection_scope_key and not project_scoped and (
            not exact_source_refs
            or bound_version_ids != {str(ref.version_id) for ref in exact_source_refs}
        ):
            raise ScientificResultProjectionFailed("repeated capability invocation has no exact source binding")
        call_ids = {str(call.get("id")) for call in calls}
        artifacts = tuple(artifact for artifact in context.artifacts if str(artifact.get("toolCallId") or artifact.get("tool_call_id")) in call_ids or str(artifact.get("stepId") or artifact.get("step_id")) in step_ids)
        if not artifacts and len(context.projector_ids) <= 1 and not context.projection_scope_key:
            artifacts = context.artifacts
        payloads = {str(item.get("id")): context.artifact_payloads.get(str(item.get("id"))) for item in artifacts}
        return ScientificResultProjectionContext(**{
            **context.__dict__, "capability_plan": {**context.capability_plan, "steps": steps},
            "tool_calls": calls, "artifacts": artifacts, "artifact_payloads": payloads,
            "source_object_refs": projector_source_refs,
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
            bundle.provenance.source_object_version_ids.extend(
                other.provenance.source_object_version_ids
            )
            bundle.provenance.tool_call_ids.extend(other.provenance.tool_call_ids)
            bundle.provenance.artifact_ids.extend(other.provenance.artifact_ids)
        # Composite authority retains every exact source; individual result
        # items/evidence/methods keep the narrower per-capability refs.
        bundle.source_object_refs = list(context.source_object_refs)
        bundle.provenance.projector_ids = sorted(set(bundle.provenance.projector_ids))
        bundle.provenance.source_object_version_ids = sorted(
            set(bundle.provenance.source_object_version_ids)
        )
        bundle.provenance.tool_call_ids = sorted(set(bundle.provenance.tool_call_ids))
        bundle.provenance.artifact_ids = sorted(set(bundle.provenance.artifact_ids))
        project_inputs = [projection.bundle.provenance.model_dump(mode="json") for projection in projections]
        if any(item.get("execution_scope") == "PROJECT" for item in project_inputs):
            if not all(item.get("execution_scope") == "PROJECT" for item in project_inputs):
                raise ScientificResultProjectionFailed("Project inputs cannot inherit sample provenance")
            from mdi_api.domain.scientific_results.contracts import ProvenanceRecord
            from mdi_api.domain.scientific_results.reference_sources import project_reference_context
            origins = sorted({origin for item in project_inputs for origin in item.get("input_origins", [item.get("input_origin")])})
            references: dict[str, dict[str, Any]] = {}
            for item in project_inputs:
                for reference in item.get("reference_sources", []):
                    key = reference["referenceId"]
                    if key in references and references[key] != reference:
                        raise ScientificResultProjectionFailed("Composite reference versions conflict")
                    references[key] = reference
            bundle.provenance = ProvenanceRecord.model_validate({**bundle.provenance.model_dump(mode="json"),
                "input_origin": origins[0] if len(origins) == 1 else "MIXED", "input_origins": origins,
                "reference_sources": [references[key] for key in sorted(references)],
                "parameter_inputs": [record for item in project_inputs for record in item.get("parameter_inputs", [])]})
            project_reference_context(bundle)
        bundle.limitations = list({item.limitation_id: item for item in bundle.limitations}.values())
        bundle.warnings = list({item.warning_id: item for item in bundle.warnings}.values())
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
    def _enqueue_interpretation(turn_id: UUID) -> None:
        """Publish only after RESULT_READY commit; failures remain recoverable."""
        try:
            from mdi_api.config import load_settings
            from mdi_api.infrastructure.interpretation.queue import RedisRQInterpretationQueue

            settings = load_settings()
            if not settings.agent2_interpretation_enabled or settings.queue_backend != "redis":
                return
            RedisRQInterpretationQueue(redis_url=settings.redis_url, queue_name=settings.agent2_interpretation_queue_name).enqueue_turn(turn_id)
        except Exception as exc:
            # RESULT_READY is the durable authority. A reconciler/manual retry
            # can republish the identity without changing execution facts.
            logger.warning("interpretation_wakeup_failed", extra={"turn_id": str(turn_id), "error_type": type(exc).__name__})

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

