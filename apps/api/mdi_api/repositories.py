from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock, RLock
from typing import Any, ContextManager, Iterator, Mapping, Protocol

from sqlalchemy import and_, delete, func, insert, or_, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Connection, Engine

from mdi_api.db import (
    analysis_intent_executions,
    analysis_intents,
    analysis_plans,
    artifact_lineage_records,
    artifacts,
    capability_eligibility_resolutions,
    capability_planning_decisions,
    capability_planning_executions,
    data_profiles,
    dependency_execution_records,
    datasets,
    job_events,
    jobs,
    organizations,
    projects,
    reports,
    scientific_evidence_bundles,
    scientific_interpretation_runs,
    scientific_interpretation_claims,
    scientific_interpretation_evidence_links,
    scientific_interpretations,
    scientific_workspaces,
    plan_dependency_bindings,
    runtime_artifact_binding_resolutions,
    tool_calls,
    users,
    visualization_recipes,
    workspace_layout_revisions,
    workspace_panels,
)
from mdi_schemas import (
    AnalysisIntent,
    AnalysisPlan,
    AnalysisPlanV02,
    Artifact,
    ArtifactLineageRecord,
    CapabilityPlanningDecision,
    DataProfile,
    EligibilityResolution,
    GroundedScientificInterpretation,
    InterpretationExecutionRecord,
    DependencyBinding,
    DependencyExecutionRecord,
    JobEvent,
    JobEventStatus,
    JobStatus,
    ScientificEvidenceBundle,
    ScientificWorkspace,
    ResolvedArtifactInputRef,
    ToolCall,
    VisualizationRecipe,
    WorkspaceLayoutRevision,
    WorkspaceLayoutState,
    WorkspacePanel,
    WorkspaceSelectionContext,
    WorkspaceStatus,
    WORKSPACE_MAX_LAYOUT_REVISIONS,
    WORKSPACE_MAX_PANELS,
    compute_analysis_intent_hash,
    canonical_dependency_json,
    capability_semantic_hash,
    compute_analysis_plan_02_hash,
    deterministic_capability_id,
    dependency_semantic_hash,
    deterministic_dependency_id,
    deterministic_intent_id,
    make_layout_revision,
)

from mdi_api.state_machine import (
    validate_job_status,
    validate_job_transition,
    validate_tool_call_status,
    validate_tool_call_transition,
)


class ProjectRepository(Protocol):
    def save(self, project: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, project_id: str) -> dict[str, Any]:
        ...

    def list(self) -> list[dict[str, Any]]:
        ...


class DatasetRepository(Protocol):
    def save(self, dataset: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, dataset_id: str) -> dict[str, Any]:
        ...

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        ...


class DataProfileRepository(Protocol):
    def save(self, profile: DataProfile | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, profile_id: str) -> dict[str, Any]:
        ...

    def list_for_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        ...

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        ...


class AnalysisPlanRepository(Protocol):
    def save_plan(self, record: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get_plan(self, plan_id: str) -> dict[str, Any]:
        ...

    def get_plan_for_job(self, job_id: str) -> dict[str, Any]:
        ...

    def attach_plan_to_job(self, plan_id: str, job_id: str) -> dict[str, Any]:
        ...


class AnalysisIntentRepository(Protocol):
    def save_intent(self, record: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get_intent(self, intent_id: str) -> dict[str, Any]:
        ...

    def attach_execution(self, intent_id: str, plan_id: str, job_id: str) -> dict[str, Any]:
        ...

    def get_execution(self, intent_id: str) -> dict[str, Any] | None:
        ...

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        ...


class CapabilityPlanningRepository(Protocol):
    def save_resolution(self, record: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get_resolution(self, resolution_id: str) -> dict[str, Any]:
        ...

    def save_decision(self, record: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get_decision(self, decision_id: str) -> dict[str, Any]:
        ...

    def attach_execution(self, decision_id: str, intent_id: str, plan_id: str, job_id: str) -> dict[str, Any]:
        ...

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        ...


class DependencyExecutionRepository(Protocol):
    def save_plan_bindings(
        self,
        plan_id: str,
        plan_hash: str,
        graph_hash: str,
        bindings: list[DependencyBinding | Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        ...

    def list_plan_bindings(self, plan_id: str) -> list[dict[str, Any]]:
        ...

    def save_binding_resolution(self, record: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def list_binding_resolutions(self, job_id: str) -> list[dict[str, Any]]:
        ...

    def save_execution(self, record: DependencyExecutionRecord | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        ...

    def save_lineage(self, record: ArtifactLineageRecord | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def list_lineage_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...

    def get_lineage_for_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        ...


class JobRepository(Protocol):
    def save(self, job: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, job_id: str) -> dict[str, Any]:
        ...

    def set_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        ...


class JobEventRepository(Protocol):
    def append_event(
        self,
        job_id: str,
        *,
        event_type: str,
        status: JobEventStatus | str,
        message: str,
        payload: Mapping[str, Any] | None = None,
        progress: float | None = None,
    ) -> JobEvent:
        ...

    def list_for_job(self, job_id: str) -> list[JobEvent]:
        ...

    def list_events_after_seq(self, job_id: str, after_seq: int) -> list[JobEvent]:
        ...


class ToolCallRepository(Protocol):
    def save(self, tool_call: ToolCall | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...


class ArtifactRepository(Protocol):
    def save(self, artifact: Artifact | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, artifact_id: str) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...


class RecipeRepository(Protocol):
    def save(self, recipe: VisualizationRecipe | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, recipe_id: str) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...


class ReportRepository(Protocol):
    def save(self, report: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, report_id: str) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        ...


class ScientificInterpretationRepository(Protocol):
    def idempotency_guard(self, job_id: str, mode: str, idempotency_key_hash: str) -> ContextManager[None]:
        ...

    def save_bundle(self, bundle: ScientificEvidenceBundle | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get_bundle(self, bundle_id: str) -> dict[str, Any]:
        ...

    def save_interpretation(
        self,
        bundle: ScientificEvidenceBundle | Mapping[str, Any],
        interpretation: GroundedScientificInterpretation | Mapping[str, Any],
        execution: InterpretationExecutionRecord | Mapping[str, Any],
    ) -> dict[str, Any]:
        ...

    def get_interpretation(self, interpretation_id: str) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...


class WorkspaceRepository(Protocol):
    def create_workspace(
        self,
        workspace: ScientificWorkspace | Mapping[str, Any],
        *,
        panels: list[WorkspacePanel | Mapping[str, Any]] | tuple[WorkspacePanel | Mapping[str, Any], ...] = (),
        initial_layout: WorkspaceLayoutRevision | Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...

    def get(self, workspace_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        ...

    def get_by_project_job(self, project_id: str, source_job_id: str) -> dict[str, Any]:
        ...

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        ...

    def save_panel(
        self,
        panel: WorkspacePanel | Mapping[str, Any],
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        ...

    def get_panel(
        self,
        workspace_id: str,
        panel_id: str,
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        ...

    def list_panels(self, workspace_id: str, *, project_id: str | None = None) -> list[dict[str, Any]]:
        ...

    def append_layout_revision(
        self,
        revision: WorkspaceLayoutRevision | Mapping[str, Any],
        *,
        expected_revision: int,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        ...

    def get_layout_revision(
        self,
        workspace_id: str,
        revision: int,
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        ...

    def get_current_layout(self, workspace_id: str, *, project_id: str | None = None) -> dict[str, Any] | None:
        ...

    def list_layout_revisions(
        self,
        workspace_id: str,
        *,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        ...

    def update_workspace(
        self,
        workspace_id: str,
        *,
        expected_revision: int,
        project_id: str | None = None,
        title: str | object = ...,
        active_panel_id: str | None | object = ...,
        pinned_selection: WorkspaceSelectionContext | Mapping[str, Any] | None | object = ...,
        layout: WorkspaceLayoutState | Mapping[str, Any] | None = None,
        layout_revision: WorkspaceLayoutRevision | Mapping[str, Any] | None = None,
        created_by: str | None = None,
    ) -> dict[str, Any]:
        ...


@dataclass
class InMemoryRepositoryBundle:
    projects: "InMemoryProjectRepository"
    datasets: "InMemoryDatasetRepository"
    data_profiles: "InMemoryDataProfileRepository"
    analysis_intents: "InMemoryAnalysisIntentRepository"
    capability_planning: "InMemoryCapabilityPlanningRepository"
    dependency_execution: "InMemoryDependencyExecutionRepository"
    analysis_plans: "InMemoryAnalysisPlanRepository"
    jobs: "InMemoryJobRepository"
    job_events: "InMemoryJobEventRepository"
    tool_calls: "InMemoryToolCallRepository"
    artifacts: "InMemoryArtifactRepository"
    recipes: "InMemoryRecipeRepository"
    reports: "InMemoryReportRepository"
    interpretations: "InMemoryScientificInterpretationRepository"
    workspaces: "InMemoryWorkspaceRepository"

    @classmethod
    def create(cls) -> "InMemoryRepositoryBundle":
        datasets = InMemoryDatasetRepository()
        jobs = InMemoryJobRepository()
        analysis_plans_repository = InMemoryAnalysisPlanRepository(jobs)
        return cls(
            projects=InMemoryProjectRepository(),
            datasets=datasets,
            data_profiles=InMemoryDataProfileRepository(datasets),
            analysis_intents=InMemoryAnalysisIntentRepository(),
            capability_planning=InMemoryCapabilityPlanningRepository(),
            dependency_execution=InMemoryDependencyExecutionRepository(analysis_plans_repository),
            analysis_plans=analysis_plans_repository,
            jobs=jobs,
            job_events=InMemoryJobEventRepository(),
            tool_calls=InMemoryToolCallRepository(),
            artifacts=InMemoryArtifactRepository(),
            recipes=InMemoryRecipeRepository(),
            reports=InMemoryReportRepository(),
            interpretations=InMemoryScientificInterpretationRepository(),
            workspaces=InMemoryWorkspaceRepository(),
        )


class _InMemoryRecordRepository:
    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}

    def _save(self, record: Mapping[str, Any], *, record_id: str) -> dict[str, Any]:
        stored = _json_copy(record)
        stored.setdefault("id", record_id)
        self.records[record_id] = stored
        return _json_copy(stored)

    def _get(self, record_id: str) -> dict[str, Any]:
        try:
            return _json_copy(self.records[record_id])
        except KeyError as exc:
            raise LookupError(f"Unknown record id: {record_id}") from exc

    def create(self, record: Mapping[str, Any]) -> dict[str, Any]:
        return self.save(record)  # type: ignore[attr-defined]

    def get_by_id(self, record_id: str) -> dict[str, Any]:
        return self.get(record_id)  # type: ignore[attr-defined]


class InMemoryProjectRepository(_InMemoryRecordRepository):
    def save(self, project: Mapping[str, Any]) -> dict[str, Any]:
        return self._save(project, record_id=_required_id(project, "projectId"))

    def get(self, project_id: str) -> dict[str, Any]:
        return self._get(project_id)

    def list(self) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values()]


class InMemoryDatasetRepository(_InMemoryRecordRepository):
    def save(self, dataset: Mapping[str, Any]) -> dict[str, Any]:
        return self._save(dataset, record_id=_required_id(dataset, "datasetId"))

    def get(self, dataset_id: str) -> dict[str, Any]:
        return self._get(dataset_id)

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        return self.list_for_project(project_id)


class InMemoryDataProfileRepository(_InMemoryRecordRepository):
    def __init__(self, datasets: InMemoryDatasetRepository | None = None) -> None:
        super().__init__()
        self.datasets = datasets

    def save(self, profile: DataProfile | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(profile)
        return self._save(record, record_id=_required_id(record, "profileId"))

    def get(self, profile_id: str) -> dict[str, Any]:
        return self._get(profile_id)

    def list_for_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("datasetId") == dataset_id]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        if self.datasets is None:
            return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]
        dataset_ids = {
            record.get("datasetId") or record.get("id")
            for record in self.datasets.list_for_project(project_id)
            if record.get("datasetId") or record.get("id")
        }
        return [_json_copy(record) for record in self.records.values() if record.get("datasetId") in dataset_ids]


class InMemoryAnalysisIntentRepository(_InMemoryRecordRepository):
    def __init__(self) -> None:
        super().__init__()
        self.executions: dict[str, dict[str, Any]] = {}

    def save_intent(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_analysis_intent_record(record)
        intent_id = _required_id(normalized, "intentId")
        existing = self.records.get(intent_id)
        if existing is not None:
            if existing.get("intentHash") != normalized.get("intentHash"):
                raise ValueError("AnalysisIntent records are immutable")
            return _analysis_intent_from_record(existing)
        return _analysis_intent_from_record(self._save(normalized, record_id=intent_id))

    def get_intent(self, intent_id: str) -> dict[str, Any]:
        return _analysis_intent_from_record(self._get(intent_id))

    def attach_execution(self, intent_id: str, plan_id: str, job_id: str) -> dict[str, Any]:
        self.get_intent(intent_id)
        current = self.executions.get(intent_id)
        binding = {
            "id": f"intent_exec_{intent_id.removeprefix('intent_')[:16]}",
            "intentId": intent_id,
            "planId": plan_id,
            "jobId": job_id,
            "createdAt": _utc_now(),
        }
        if current is not None and (current["planId"] != plan_id or current["jobId"] != job_id):
            raise ValueError("AnalysisIntent execution association is immutable")
        self.executions[intent_id] = current or binding
        return _json_copy(self.executions[intent_id])

    def get_execution(self, intent_id: str) -> dict[str, Any] | None:
        value = self.executions.get(intent_id)
        return _json_copy(value) if value is not None else None

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        value = next((item for item in self.executions.values() if item["jobId"] == job_id), None)
        return _json_copy(value) if value is not None else None


class InMemoryCapabilityPlanningRepository:
    def __init__(self) -> None:
        self.resolutions: dict[str, dict[str, Any]] = {}
        self.decisions: dict[str, dict[str, Any]] = {}
        self.executions: dict[str, dict[str, Any]] = {}

    def save_resolution(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_capability_resolution_record(record)
        resolution_id = normalized["resolutionId"]
        existing = self.resolutions.get(resolution_id)
        if existing is not None and existing["resolutionHash"] != normalized["resolutionHash"]:
            raise ValueError("Eligibility Resolution records are immutable")
        self.resolutions.setdefault(resolution_id, normalized)
        return _json_copy(self.resolutions[resolution_id])

    def get_resolution(self, resolution_id: str) -> dict[str, Any]:
        try:
            return _json_copy(self.resolutions[resolution_id])
        except KeyError as exc:
            raise LookupError(f"Unknown Eligibility Resolution: {resolution_id}") from exc

    def save_decision(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_capability_decision_record(record)
        self.get_resolution(normalized["resolutionId"])
        decision_id = normalized["decisionId"]
        existing = self.decisions.get(decision_id)
        if existing is not None and existing["decisionHash"] != normalized["decisionHash"]:
            raise ValueError("Capability Planning Decision records are immutable")
        self.decisions.setdefault(decision_id, normalized)
        return _json_copy(self.decisions[decision_id])

    def get_decision(self, decision_id: str) -> dict[str, Any]:
        try:
            return _json_copy(self.decisions[decision_id])
        except KeyError as exc:
            raise LookupError(f"Unknown Capability Planning Decision: {decision_id}") from exc

    def attach_execution(self, decision_id: str, intent_id: str, plan_id: str, job_id: str) -> dict[str, Any]:
        decision = self.get_decision(decision_id)
        if decision["intentId"] != intent_id or decision["outcome"] != "PLAN_READY":
            raise ValueError("Only a matching PLAN_READY decision can be attached to execution")
        binding = {
            "id": f"cap_exec_{decision_id.removeprefix('decision_')[:16]}",
            "decisionId": decision_id,
            "intentId": intent_id,
            "planId": plan_id,
            "jobId": job_id,
            "createdAt": _utc_now(),
        }
        current = self.executions.get(decision_id)
        if current is not None and current != binding:
            comparable = {key: value for key, value in current.items() if key != "createdAt"}
            requested = {key: value for key, value in binding.items() if key != "createdAt"}
            if comparable != requested:
                raise ValueError("Capability Planning execution association is immutable")
        self.executions.setdefault(decision_id, binding)
        return _json_copy(self.executions[decision_id])

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        value = next((item for item in self.executions.values() if item["jobId"] == job_id), None)
        return _json_copy(value) if value is not None else None


class InMemoryDependencyExecutionRepository:
    def __init__(self, plans: "InMemoryAnalysisPlanRepository") -> None:
        self.plans = plans
        self.plan_bindings: dict[str, dict[str, dict[str, Any]]] = {}
        self.binding_resolutions: dict[tuple[str, str], dict[str, Any]] = {}
        self.executions: dict[str, dict[str, Any]] = {}
        self.lineage: dict[str, dict[str, Any]] = {}

    def save_plan_bindings(
        self, plan_id: str, plan_hash: str, graph_hash: str, bindings: list[DependencyBinding | Mapping[str, Any]]
    ) -> list[dict[str, Any]]:
        normalized = _normalize_plan_bindings(self.plans.get_plan(plan_id), plan_id, plan_hash, graph_hash, bindings)
        requested = {item["bindingId"]: item for item in normalized}
        existing = self.plan_bindings.get(plan_id)
        if existing is not None and existing != requested:
            raise ValueError("Planned dependency binding records are immutable")
        self.plan_bindings.setdefault(plan_id, requested)
        return self.list_plan_bindings(plan_id)

    def list_plan_bindings(self, plan_id: str) -> list[dict[str, Any]]:
        return [_json_copy(item) for _, item in sorted(self.plan_bindings.get(plan_id, {}).items())]

    def save_binding_resolution(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_binding_resolution_record(record)
        key = (normalized["jobId"], normalized["bindingId"])
        existing = self.binding_resolutions.get(key)
        if existing is not None and existing["recordHash"] != normalized["recordHash"]:
            raise ValueError("Runtime artifact binding resolution records are immutable")
        self.binding_resolutions.setdefault(key, normalized)
        return _json_copy(self.binding_resolutions[key])

    def list_binding_resolutions(self, job_id: str) -> list[dict[str, Any]]:
        return [
            _json_copy(item)
            for key, item in sorted(self.binding_resolutions.items())
            if key[0] == job_id
        ]

    def save_execution(self, record: DependencyExecutionRecord | Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_dependency_execution_record(record)
        existing = self.executions.get(normalized["jobId"])
        if existing is not None and existing["executionHash"] != normalized["executionHash"]:
            raise ValueError("Dependency execution records are immutable")
        self.executions.setdefault(normalized["jobId"], normalized)
        return _json_copy(self.executions[normalized["jobId"]])

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        value = self.executions.get(job_id)
        return _json_copy(value) if value is not None else None

    def save_lineage(self, record: ArtifactLineageRecord | Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_artifact_lineage_record(record)
        existing = self.lineage.get(normalized["artifactId"])
        if existing is not None and existing["lineageHash"] != normalized["lineageHash"]:
            raise ValueError("Artifact lineage records are immutable")
        self.lineage.setdefault(normalized["artifactId"], normalized)
        return _json_copy(self.lineage[normalized["artifactId"]])

    def list_lineage_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(item) for _, item in sorted(self.lineage.items()) if item["jobId"] == job_id]

    def get_lineage_for_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        value = self.lineage.get(artifact_id)
        return _json_copy(value) if value is not None else None


class InMemoryAnalysisPlanRepository(_InMemoryRecordRepository):
    def __init__(self, jobs: "InMemoryJobRepository | None" = None) -> None:
        super().__init__()
        self.jobs = jobs

    def save_plan(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_analysis_plan_record(record)
        plan_id = _required_id(normalized, "planId")
        existing = self.records.get(plan_id)
        if existing is not None:
            existing_schema = (existing.get("analysisPlan") or {}).get("schemaVersion")
            new_schema = normalized["analysisPlan"].get("schemaVersion")
            if "0.2" in {existing_schema, new_schema} and existing.get("planHash") != normalized["planHash"]:
                raise ValueError("AnalysisPlan 0.2 records are immutable")
        return _analysis_plan_from_record(self._save(normalized, record_id=plan_id))

    def get_plan(self, plan_id: str) -> dict[str, Any]:
        return _analysis_plan_from_record(self._get(plan_id))

    def get_plan_for_job(self, job_id: str) -> dict[str, Any]:
        if self.jobs is not None:
            try:
                job = self.jobs.get(job_id)
            except LookupError:
                job = {}
            plan_id = job.get("planId") or job.get("plan_id")
            if plan_id:
                return self.get_plan(str(plan_id))
        for record in self.records.values():
            if record.get("jobId") == job_id or record.get("job_id") == job_id:
                return _analysis_plan_from_record(record)
        raise LookupError(f"Unknown analysis plan for job id: {job_id}")

    def attach_plan_to_job(self, plan_id: str, job_id: str) -> dict[str, Any]:
        record = self._get(plan_id)
        record["jobId"] = job_id
        record["job_id"] = job_id
        record["updatedAt"] = _utc_now()
        self.records[plan_id] = record
        if self.jobs is not None:
            job = self.jobs.get(job_id)
            job["planId"] = plan_id
            job["plan_id"] = plan_id
            job["updatedAt"] = _utc_now()
            self.jobs.records[job_id] = job
        return _analysis_plan_from_record(record)


class InMemoryJobRepository(_InMemoryRecordRepository):
    def save(self, job: Mapping[str, Any]) -> dict[str, Any]:
        record = _json_copy(job)
        record["status"] = validate_job_status(record.get("status") or JobStatus.created.value)
        return self._save(record, record_id=_required_id(record, "jobId"))

    def get(self, job_id: str) -> dict[str, Any]:
        return self._get(job_id)

    def set_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        record = self._get(job_id)
        record["status"] = validate_job_transition(record.get("status") or JobStatus.created.value, status)
        record["updatedAt"] = _utc_now()
        self.records[job_id] = record
        return _json_copy(record)

    def update_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        return self.set_status(job_id, status)

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]


class InMemoryJobEventRepository:
    def __init__(self) -> None:
        self.events_by_job: dict[str, list[JobEvent]] = {}
        self._lock = Lock()

    def append_event(
        self,
        job_id: str,
        *,
        event_type: str,
        status: JobEventStatus | str,
        message: str,
        payload: Mapping[str, Any] | None = None,
        progress: float | None = None,
    ) -> JobEvent:
        with self._lock:
            events = self.events_by_job.setdefault(job_id, [])
            seq = len(events) + 1
            event = JobEvent(
                id=f"evt_{job_id}_{seq:04d}",
                jobId=job_id,
                seq=seq,
                eventType=event_type,
                status=JobEventStatus(_enum_value(status)),
                message=message,
                progress=progress,
                payload=dict(payload or {}),
                createdAt=_utc_now(),
            )
            events.append(event)
            return event

    def save_event(self, event: JobEvent) -> JobEvent:
        with self._lock:
            events = self.events_by_job.setdefault(event.jobId, [])
            if any(existing.seq == event.seq for existing in events):
                raise ValueError(f"Duplicate job event seq {event.seq} for job {event.jobId}")
            if events and event.seq <= events[-1].seq:
                raise ValueError(f"Job event seq must increase for job {event.jobId}")
            events.append(event)
            return event

    def list_for_job(self, job_id: str) -> list[JobEvent]:
        return list(self.events_by_job.get(job_id, []))

    def list_events(self, job_id: str) -> list[JobEvent]:
        return self.list_for_job(job_id)

    def list_events_after_seq(self, job_id: str, after_seq: int) -> list[JobEvent]:
        return [event for event in self.events_by_job.get(job_id, []) if event.seq > after_seq]


class InMemoryToolCallRepository(_InMemoryRecordRepository):
    def save(self, tool_call: ToolCall | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(tool_call)
        record_id = _required_id(record)
        record["status"] = validate_tool_call_status(record.get("status") or "planned")
        record["attempt"] = int(record.get("attempt") or 1)
        record["idempotencyKey"] = str(record.get("idempotencyKey") or record.get("idempotency_key") or f"{record['jobId']}:{record['stepId']}")
        existing_id = self._find_existing_id(record_id, record)
        if existing_id:
            current = self.records[existing_id]
            record["id"] = existing_id
            record["status"] = validate_tool_call_transition(current.get("status") or "planned", record["status"])
            record["attempt"] = max(int(current.get("attempt") or 1), record["attempt"])
            self.records[existing_id] = {**_json_copy(current), **_json_copy(record)}
            return _json_copy(self.records[existing_id])
        return self._save(record, record_id=record_id)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("jobId") == job_id]

    def list_by_job(self, job_id: str) -> list[dict[str, Any]]:
        return self.list_for_job(job_id)

    def _find_existing_id(self, record_id: str, record: Mapping[str, Any]) -> str | None:
        if record_id in self.records:
            return record_id
        for existing_id, existing in self.records.items():
            if existing.get("jobId") == record.get("jobId") and existing.get("stepId") == record.get("stepId"):
                return existing_id
            if (
                existing.get("jobId") == record.get("jobId")
                and existing.get("idempotencyKey")
                and existing.get("idempotencyKey") == record.get("idempotencyKey")
            ):
                return existing_id
        return None


class InMemoryArtifactRepository(_InMemoryRecordRepository):
    def save(self, artifact: Artifact | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(artifact)
        artifact_id = _required_id(record, "artifactId")
        _validate_artifact_storage_record(record)
        existing_id = self._find_existing_id(artifact_id, record)
        if existing_id:
            current = self.records[existing_id]
            record["id"] = existing_id
            self.records[existing_id] = {**_json_copy(current), **_json_copy(record)}
            return _json_copy(self.records[existing_id])
        return self._save(record, record_id=artifact_id)

    def get(self, artifact_id: str) -> dict[str, Any]:
        return self._get(artifact_id)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("jobId") == job_id]

    def list_artifacts_by_job(self, job_id: str) -> list[dict[str, Any]]:
        return self.list_for_job(job_id)

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]

    def _find_existing_id(self, artifact_id: str, record: Mapping[str, Any]) -> str | None:
        if artifact_id in self.records:
            return artifact_id
        storage_key = record.get("storageKey")
        sha256 = record.get("sha256") or record.get("contentHash")
        for existing_id, existing in self.records.items():
            existing_sha = existing.get("sha256") or existing.get("contentHash")
            if existing.get("jobId") == record.get("jobId") and existing.get("storageKey") == storage_key and existing_sha == sha256:
                return existing_id
        return None


class InMemoryRecipeRepository(_InMemoryRecordRepository):
    def save(self, recipe: VisualizationRecipe | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(recipe)
        return self._save(record, record_id=_required_id(record, "recipeId"))

    def get(self, recipe_id: str) -> dict[str, Any]:
        return self._get(recipe_id)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("sourceJobId") == job_id]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]


class InMemoryReportRepository(_InMemoryRecordRepository):
    def save(self, report: Mapping[str, Any]) -> dict[str, Any]:
        return self._save(report, record_id=_required_id(report, "reportId"))

    def get(self, report_id: str) -> dict[str, Any]:
        return self._get(report_id)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [
            _json_copy(record)
            for record in self.records.values()
            if record.get("jobId") == job_id or record.get("sourceJobId") == job_id
        ]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]


class InMemoryScientificInterpretationRepository(_InMemoryRecordRepository):
    def __init__(self) -> None:
        super().__init__()
        self.bundles: dict[str, dict[str, Any]] = {}
        self.runs: dict[str, dict[str, Any]] = {}
        self._idempotency_locks = _KeyedLockRegistry()

    def idempotency_guard(self, job_id: str, mode: str, idempotency_key_hash: str) -> ContextManager[None]:
        return self._idempotency_locks.guard((job_id, mode, idempotency_key_hash))

    def save_bundle(self, bundle: ScientificEvidenceBundle | Mapping[str, Any]) -> dict[str, Any]:
        parsed = ScientificEvidenceBundle.model_validate(
            bundle.model_dump(mode="json") if isinstance(bundle, ScientificEvidenceBundle) else bundle
        )
        record = parsed.model_dump(mode="json")
        existing = self.bundles.get(parsed.bundleId)
        if existing is not None and existing["bundleHash"] != parsed.bundleHash:
            raise ValueError("Scientific evidence bundles are immutable")
        self.bundles.setdefault(parsed.bundleId, record)
        return _json_copy(self.bundles[parsed.bundleId])

    def get_bundle(self, bundle_id: str) -> dict[str, Any]:
        try:
            return _json_copy(self.bundles[bundle_id])
        except KeyError as exc:
            raise LookupError(f"Unknown evidence bundle: {bundle_id}") from exc

    def save_run(
        self,
        bundle: ScientificEvidenceBundle | Mapping[str, Any],
        execution: InterpretationExecutionRecord | Mapping[str, Any],
        *,
        interpretation_id: str | None = None,
    ) -> dict[str, Any]:
        parsed_bundle = ScientificEvidenceBundle.model_validate(
            bundle.model_dump(mode="json") if isinstance(bundle, ScientificEvidenceBundle) else bundle
        )
        parsed = InterpretationExecutionRecord.model_validate(
            execution.model_dump(mode="json") if isinstance(execution, InterpretationExecutionRecord) else execution
        )
        self.save_bundle(parsed_bundle)
        _validate_interpretation_run_association(parsed_bundle, parsed)
        record = {
            "execution": parsed.model_dump(mode="json"),
            "bundleId": parsed_bundle.bundleId,
            "jobId": parsed_bundle.jobId,
            "mode": parsed.mode.value,
            "idempotencyKeyHash": parsed.idempotencyKeyHash,
            "interpretationId": interpretation_id,
        }
        existing = self.runs.get(parsed.executionRecordId)
        if existing is not None:
            if existing["execution"]["executionRecordHash"] != parsed.executionRecordHash:
                raise ValueError("Scientific interpretation runs are immutable")
            if existing.get("interpretationId") != interpretation_id:
                raise ValueError("Scientific interpretation run association is immutable")
        for other in self.runs.values():
            if parsed.idempotencyKeyHash and (
                other["jobId"], other["mode"], other["idempotencyKeyHash"]
            ) == (parsed_bundle.jobId, parsed.mode.value, parsed.idempotencyKeyHash) and other["execution"]["executionRecordHash"] != parsed.executionRecordHash:
                raise ValueError("Scientific interpretation idempotency key is already bound to another run")
        self.runs.setdefault(parsed.executionRecordId, record)
        return _json_copy(self.runs[parsed.executionRecordId])

    def get_run_by_idempotency(self, job_id: str, mode: str, idempotency_key_hash: str) -> dict[str, Any] | None:
        for record in self.runs.values():
            if (record["jobId"], record["mode"], record["idempotencyKeyHash"]) == (job_id, mode, idempotency_key_hash):
                return _json_copy(record)
        return None

    def get_run(self, execution_record_id: str) -> dict[str, Any]:
        try:
            return _json_copy(self.runs[execution_record_id])
        except KeyError as exc:
            raise LookupError(f"Unknown interpretation run: {execution_record_id}") from exc

    def list_runs_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for _id, record in sorted(self.runs.items()) if record["jobId"] == job_id]

    def save_interpretation(
        self,
        bundle: ScientificEvidenceBundle | Mapping[str, Any],
        interpretation: GroundedScientificInterpretation | Mapping[str, Any],
        execution: InterpretationExecutionRecord | Mapping[str, Any],
    ) -> dict[str, Any]:
        parsed_bundle = ScientificEvidenceBundle.model_validate(
            bundle.model_dump(mode="json") if isinstance(bundle, ScientificEvidenceBundle) else bundle
        )
        parsed = GroundedScientificInterpretation.model_validate(
            interpretation.model_dump(mode="json")
            if isinstance(interpretation, GroundedScientificInterpretation)
            else interpretation
        )
        execution_record = InterpretationExecutionRecord.model_validate(
            execution.model_dump(mode="json") if isinstance(execution, InterpretationExecutionRecord) else execution
        )
        _validate_interpretation_associations(parsed_bundle, parsed, execution_record)
        record = {
            "interpretation": parsed.model_dump(mode="json"),
            "execution": execution_record.model_dump(mode="json"),
            "bundleId": parsed.sourceBundleId,
            "jobId": parsed.sourceJobId,
        }
        existing = self.records.get(parsed.interpretationId)
        if existing is not None and existing["interpretation"]["interpretationHash"] != parsed.interpretationHash:
            raise ValueError("Scientific interpretations are immutable")
        existing_bundle = self.bundles.get(parsed_bundle.bundleId)
        if existing_bundle is not None and existing_bundle["bundleHash"] != parsed_bundle.bundleHash:
            raise ValueError("Scientific evidence bundles are immutable")
        existing_run = self.runs.get(execution_record.executionRecordId)
        if existing_run is not None and (
            existing_run["execution"]["executionRecordHash"] != execution_record.executionRecordHash
            or existing_run.get("interpretationId") != parsed.interpretationId
        ):
            raise ValueError("Scientific interpretation run association is immutable")
        self.save_bundle(parsed_bundle)
        self.save_run(parsed_bundle, execution_record, interpretation_id=parsed.interpretationId)
        self.records.setdefault(parsed.interpretationId, record)
        return _json_copy(self.records[parsed.interpretationId])

    def get_interpretation(self, interpretation_id: str) -> dict[str, Any]:
        return self._get(interpretation_id)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [
            _json_copy(record)
            for _record_id, record in sorted(self.records.items())
            if record.get("jobId") == job_id
        ]


class WorkspaceRepositoryError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class WorkspaceConflictError(WorkspaceRepositoryError):
    pass


class WorkspaceScopeError(WorkspaceRepositoryError):
    pass


class WorkspaceCapacityError(WorkspaceRepositoryError):
    pass


class WorkspaceNotFoundError(LookupError):
    def __init__(self, code: str = "WORKSPACE_NOT_FOUND") -> None:
        self.code = code
        super().__init__(code)


_WORKSPACE_UNSET = object()


class InMemoryWorkspaceRepository:
    def __init__(self) -> None:
        self.workspaces: dict[str, dict[str, Any]] = {}
        self.project_jobs: dict[tuple[str, str], str] = {}
        self.panels: dict[tuple[str, str], dict[str, Any]] = {}
        self.layout_revisions: dict[tuple[str, int], dict[str, Any]] = {}
        self._lock = RLock()

    def create_workspace(
        self,
        workspace: ScientificWorkspace | Mapping[str, Any],
        *,
        panels: list[WorkspacePanel | Mapping[str, Any]] | tuple[WorkspacePanel | Mapping[str, Any], ...] = (),
        initial_layout: WorkspaceLayoutRevision | Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        parsed = _parse_workspace(workspace)
        parsed_panels = tuple(_parse_workspace_panel(panel) for panel in panels)
        parsed_layout = None if initial_layout is None else _parse_workspace_layout_revision(initial_layout)
        _validate_workspace_create_aggregate(parsed, parsed_panels, parsed_layout)
        key = (parsed.projectId, parsed.sourceJobId)
        with self._lock:
            existing_id = self.project_jobs.get(key)
            if existing_id is not None:
                self._assert_create_compatible(existing_id, parsed, parsed_panels, parsed_layout)
                return self._get_unlocked(existing_id)
            if parsed.workspaceId in self.workspaces:
                raise WorkspaceConflictError("WORKSPACE_ID_CONFLICT")
            row = _workspace_values(parsed)
            self.workspaces[parsed.workspaceId] = row
            self.project_jobs[key] = parsed.workspaceId
            for panel in parsed_panels:
                self.panels[(parsed.workspaceId, panel.panelId)] = _workspace_panel_values(panel)
            if parsed_layout is not None:
                self.layout_revisions[(parsed.workspaceId, parsed_layout.revision)] = _workspace_layout_values(parsed_layout)
            return self._get_unlocked(parsed.workspaceId)

    create = create_workspace

    def get(self, workspace_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        with self._lock:
            record = self._get_unlocked(workspace_id)
            _enforce_workspace_project(record["projectId"], project_id)
            return record

    def get_by_project_job(self, project_id: str, source_job_id: str) -> dict[str, Any]:
        with self._lock:
            workspace_id = self.project_jobs.get((project_id, source_job_id))
            if workspace_id is None:
                raise WorkspaceNotFoundError()
            return self._get_unlocked(workspace_id)

    get_by_project_and_job = get_by_project_job

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        with self._lock:
            records = [
                self._get_unlocked(workspace_id)
                for workspace_id, row in self.workspaces.items()
                if row["project_id"] == project_id
            ]
            records.sort(key=lambda item: item["workspaceId"])
            records.sort(key=lambda item: item["updatedAt"], reverse=True)
            return records

    def save_panel(
        self,
        panel: WorkspacePanel | Mapping[str, Any],
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        parsed = _parse_workspace_panel(panel)
        with self._lock:
            workspace = self._workspace_row(parsed.workspaceId)
            _enforce_workspace_project(workspace["project_id"], project_id)
            _validate_panel_project_scope(parsed, workspace["project_id"])
            key = (parsed.workspaceId, parsed.panelId)
            existing = self.panels.get(key)
            if existing is not None:
                if existing["panel_state_hash"] != parsed.panelStateHash:
                    raise WorkspaceConflictError("WORKSPACE_PANEL_IMMUTABLE_CONFLICT")
                return _workspace_panel_record(existing)
            if self._panel_count(parsed.workspaceId) >= WORKSPACE_MAX_PANELS:
                raise WorkspaceCapacityError("PANEL_CAP_EXCEEDED")
            self.panels[key] = _workspace_panel_values(parsed)
            return _workspace_panel_record(self.panels[key])

    def save_panels(
        self,
        panels: list[WorkspacePanel | Mapping[str, Any]] | tuple[WorkspacePanel | Mapping[str, Any], ...],
        *,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        parsed = tuple(_parse_workspace_panel(panel) for panel in panels)
        if len({(panel.workspaceId, panel.panelId) for panel in parsed}) != len(parsed):
            raise WorkspaceConflictError("WORKSPACE_PANEL_DUPLICATE")
        with self._lock:
            return [self.save_panel(panel, project_id=project_id) for panel in parsed]

    def get_panel(
        self,
        workspace_id: str,
        panel_id: str,
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            workspace = self._workspace_row(workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            try:
                return _workspace_panel_record(self.panels[(workspace_id, panel_id)])
            except KeyError as exc:
                raise WorkspaceNotFoundError("WORKSPACE_PANEL_NOT_FOUND") from exc

    def list_panels(self, workspace_id: str, *, project_id: str | None = None) -> list[dict[str, Any]]:
        with self._lock:
            workspace = self._workspace_row(workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            rows = [row for (owner, _panel_id), row in self.panels.items() if owner == workspace_id]
            return [_workspace_panel_record(row) for row in sorted(rows, key=lambda row: (row["ordinal"], row["panel_id"]))]

    def append_layout_revision(
        self,
        revision: WorkspaceLayoutRevision | Mapping[str, Any],
        *,
        expected_revision: int,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        parsed = _parse_workspace_layout_revision(revision)
        with self._lock:
            workspace = self._workspace_row(parsed.workspaceId)
            _enforce_workspace_project(workspace["project_id"], project_id)
            existing = self.layout_revisions.get((parsed.workspaceId, parsed.revision))
            if existing is not None:
                if existing["semantic_hash"] != parsed.semanticHash:
                    raise WorkspaceConflictError("WORKSPACE_LAYOUT_IMMUTABLE_CONFLICT")
                if workspace["revision"] != parsed.revision:
                    raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
                return _workspace_layout_record(existing)
            current = int(workspace["revision"])
            if current != expected_revision:
                raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
            count = self._layout_count(parsed.workspaceId)
            if count >= WORKSPACE_MAX_LAYOUT_REVISIONS:
                raise WorkspaceCapacityError("REVISION_CAP_EXCEEDED")
            initial = count == 0 and parsed.revision == current == expected_revision
            if not initial and parsed.revision != expected_revision + 1:
                raise WorkspaceConflictError("WORKSPACE_LAYOUT_REVISION_SEQUENCE_INVALID")
            self._validate_layout_membership(parsed.workspaceId, parsed.layout)
            self.layout_revisions[(parsed.workspaceId, parsed.revision)] = _workspace_layout_values(parsed)
            workspace["revision"] = parsed.revision
            workspace["active_panel_id"] = parsed.layout.activePanelId
            workspace["pinned_selection_json"] = (
                None if parsed.selection is None else parsed.selection.model_dump(mode="json")
            )
            workspace["updated_at"] = parsed.createdAt
            return _workspace_layout_record(self.layout_revisions[(parsed.workspaceId, parsed.revision)])

    def get_layout_revision(
        self,
        workspace_id: str,
        revision: int,
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            workspace = self._workspace_row(workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            try:
                return _workspace_layout_record(self.layout_revisions[(workspace_id, revision)])
            except KeyError as exc:
                raise WorkspaceNotFoundError("WORKSPACE_LAYOUT_REVISION_NOT_FOUND") from exc

    def get_current_layout(self, workspace_id: str, *, project_id: str | None = None) -> dict[str, Any] | None:
        with self._lock:
            workspace = self._workspace_row(workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            row = self.layout_revisions.get((workspace_id, int(workspace["revision"])))
            return None if row is None else _workspace_layout_record(row)

    def list_layout_revisions(
        self,
        workspace_id: str,
        *,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        with self._lock:
            workspace = self._workspace_row(workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            rows = [row for (owner, _revision), row in self.layout_revisions.items() if owner == workspace_id]
            return [_workspace_layout_record(row) for row in sorted(rows, key=lambda row: row["revision"])]

    def update_workspace(
        self,
        workspace_id: str,
        *,
        expected_revision: int,
        project_id: str | None = None,
        title: str | object = _WORKSPACE_UNSET,
        active_panel_id: str | None | object = _WORKSPACE_UNSET,
        pinned_selection: WorkspaceSelectionContext | Mapping[str, Any] | None | object = _WORKSPACE_UNSET,
        layout: WorkspaceLayoutState | Mapping[str, Any] | None = None,
        layout_revision: WorkspaceLayoutRevision | Mapping[str, Any] | None = None,
        created_by: str | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            workspace = self._workspace_row(workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            if int(workspace["revision"]) != expected_revision:
                raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
            next_revision, next_title = _prepare_workspace_update(
                workspace_record=self._get_unlocked(workspace_id),
                current_layout=self.get_current_layout(workspace_id),
                panel_records=self.list_panels(workspace_id),
                expected_revision=expected_revision,
                title=title,
                active_panel_id=active_panel_id,
                pinned_selection=pinned_selection,
                layout=layout,
                layout_revision=layout_revision,
                created_by=created_by,
            )
            if next_revision is None:
                return self._get_unlocked(workspace_id)
            self.append_layout_revision(next_revision, expected_revision=expected_revision)
            workspace["title"] = next_title
            return self._get_unlocked(workspace_id)

    update = update_workspace

    def _workspace_row(self, workspace_id: str) -> dict[str, Any]:
        try:
            return self.workspaces[workspace_id]
        except KeyError as exc:
            raise WorkspaceNotFoundError() from exc

    def _get_unlocked(self, workspace_id: str) -> dict[str, Any]:
        workspace = self._workspace_row(workspace_id)
        panels = [row for (owner, _panel_id), row in self.panels.items() if owner == workspace_id]
        layout = self.layout_revisions.get((workspace_id, int(workspace["revision"])))
        return _workspace_record(workspace, panels, layout)

    def _panel_count(self, workspace_id: str) -> int:
        return sum(1 for owner, _panel_id in self.panels if owner == workspace_id)

    def _layout_count(self, workspace_id: str) -> int:
        return sum(1 for owner, _revision in self.layout_revisions if owner == workspace_id)

    def _validate_layout_membership(self, workspace_id: str, layout: WorkspaceLayoutState) -> None:
        panel_ids = {panel_id for owner, panel_id in self.panels if owner == workspace_id}
        _validate_layout_panel_membership(layout, panel_ids)

    def _assert_create_compatible(
        self,
        workspace_id: str,
        requested: ScientificWorkspace,
        panels: tuple[WorkspacePanel, ...],
        layout: WorkspaceLayoutRevision | None,
    ) -> None:
        existing = self._workspace_row(workspace_id)
        if _workspace_source_identity(existing) != _workspace_source_identity(_workspace_values(requested)):
            raise WorkspaceConflictError("WORKSPACE_SEMANTIC_CONFLICT")
        for panel in panels:
            row = self.panels.get((workspace_id, panel.panelId))
            if row is None or row["panel_state_hash"] != panel.panelStateHash:
                raise WorkspaceConflictError("WORKSPACE_SEMANTIC_CONFLICT")
        if layout is not None:
            row = self.layout_revisions.get((workspace_id, layout.revision))
            if row is None or row["semantic_hash"] != layout.semanticHash:
                raise WorkspaceConflictError("WORKSPACE_SEMANTIC_CONFLICT")


@dataclass
class SqlAlchemyRepositoryBundle:
    projects: "SqlAlchemyProjectRepository"
    datasets: "SqlAlchemyDatasetRepository"
    data_profiles: "SqlAlchemyDataProfileRepository"
    analysis_intents: "SqlAlchemyAnalysisIntentRepository"
    capability_planning: "SqlAlchemyCapabilityPlanningRepository"
    dependency_execution: "SqlAlchemyDependencyExecutionRepository"
    analysis_plans: "SqlAlchemyAnalysisPlanRepository"
    jobs: "SqlAlchemyJobRepository"
    job_events: "SqlAlchemyJobEventRepository"
    tool_calls: "SqlAlchemyToolCallRepository"
    artifacts: "SqlAlchemyArtifactRepository"
    recipes: "SqlAlchemyRecipeRepository"
    reports: "SqlAlchemyReportRepository"
    interpretations: "SqlAlchemyScientificInterpretationRepository"
    workspaces: "SqlAlchemyWorkspaceRepository"

    @classmethod
    def create(cls, bind: Engine | Connection) -> "SqlAlchemyRepositoryBundle":
        return cls(
            projects=SqlAlchemyProjectRepository(bind),
            datasets=SqlAlchemyDatasetRepository(bind),
            data_profiles=SqlAlchemyDataProfileRepository(bind),
            analysis_intents=SqlAlchemyAnalysisIntentRepository(bind),
            capability_planning=SqlAlchemyCapabilityPlanningRepository(bind),
            dependency_execution=SqlAlchemyDependencyExecutionRepository(bind),
            analysis_plans=SqlAlchemyAnalysisPlanRepository(bind),
            jobs=SqlAlchemyJobRepository(bind),
            job_events=SqlAlchemyJobEventRepository(bind),
            tool_calls=SqlAlchemyToolCallRepository(bind),
            artifacts=SqlAlchemyArtifactRepository(bind),
            recipes=SqlAlchemyRecipeRepository(bind),
            reports=SqlAlchemyReportRepository(bind),
            interpretations=SqlAlchemyScientificInterpretationRepository(bind),
            workspaces=SqlAlchemyWorkspaceRepository(bind),
        )


class _SqlAlchemyRepository:
    def __init__(self, bind: Engine | Connection) -> None:
        self.bind = bind

    def _with_connection(self, fn: Any) -> Any:
        if isinstance(self.bind, Engine):
            with self.bind.begin() as connection:
                return fn(connection)
        return fn(self.bind)

    def _fetch_one_dict(self, statement: Any) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(statement).mappings().first()
            if row is None:
                raise LookupError("Record not found")
            return _row_to_json_dict(row)

        return self._with_connection(run)

    def _fetch_all_dicts(self, statement: Any) -> list[dict[str, Any]]:
        def run(connection: Connection) -> list[dict[str, Any]]:
            return [_row_to_json_dict(row) for row in connection.execute(statement).mappings().all()]

        return self._with_connection(run)

    def create(self, record: Mapping[str, Any]) -> dict[str, Any]:
        return self.save(record)  # type: ignore[attr-defined]

    def get_by_id(self, record_id: str) -> dict[str, Any]:
        return self.get(record_id)  # type: ignore[attr-defined]


class SqlAlchemyProjectRepository(_SqlAlchemyRepository):
    def save(self, project: Mapping[str, Any]) -> dict[str, Any]:
        project_id = _required_id(project, "projectId")
        organization_id = str(project.get("organizationId") or project.get("organization_id") or "org_local")
        created_by = str(project.get("createdBy") or project.get("created_by") or "user_local")
        values = {
            "id": project_id,
            "organization_id": organization_id,
            "name": str(project.get("name") or project_id),
            "description": str(project.get("description") or ""),
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            _ensure_actor_and_org(connection, user_id=created_by, organization_id=organization_id)
            connection.execute(delete(projects).where(projects.c.id == project_id))
            connection.execute(insert(projects).values(**values))

        self._with_connection(run)
        return self.get(project_id)

    def get(self, project_id: str) -> dict[str, Any]:
        return _project_from_row(self._fetch_one_dict(select(projects).where(projects.c.id == project_id)))

    def list(self) -> list[dict[str, Any]]:
        return [_project_from_row(row) for row in self._fetch_all_dicts(select(projects).order_by(projects.c.created_at, projects.c.id))]


class SqlAlchemyDatasetRepository(_SqlAlchemyRepository):
    def save(self, dataset: Mapping[str, Any]) -> dict[str, Any]:
        dataset_id = _required_id(dataset, "datasetId")
        created_by = str(dataset.get("createdBy") or dataset.get("created_by") or "user_local")
        values = {
            "id": dataset_id,
            "project_id": str(dataset["projectId"]),
            "name": str(dataset.get("name") or dataset.get("datasetName") or dataset_id),
            "status": str(dataset.get("status") or "created"),
            "metadata_json": _json_copy(dataset.get("metadata") or dataset),
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            _ensure_user(connection, user_id=created_by)
            connection.execute(delete(datasets).where(datasets.c.id == dataset_id))
            connection.execute(insert(datasets).values(**values))

        self._with_connection(run)
        return self.get(dataset_id)

    def get(self, dataset_id: str) -> dict[str, Any]:
        return _dataset_from_row(self._fetch_one_dict(select(datasets).where(datasets.c.id == dataset_id)))

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = select(datasets).where(datasets.c.project_id == project_id).order_by(datasets.c.created_at, datasets.c.id)
        return [_dataset_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        return self.list_for_project(project_id)


class SqlAlchemyDataProfileRepository(_SqlAlchemyRepository):
    def save(self, profile: DataProfile | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(profile)
        profile_id = _required_id(record, "profileId")
        values = {
            "id": profile_id,
            "dataset_id": str(record["datasetId"]),
            "version": str(record.get("version") or "1"),
            "profile_json": _json_copy(record),
        }

        def run(connection: Connection) -> None:
            connection.execute(delete(data_profiles).where(data_profiles.c.id == profile_id))
            connection.execute(insert(data_profiles).values(**values))

        self._with_connection(run)
        return self.get(profile_id)

    def get(self, profile_id: str) -> dict[str, Any]:
        return _data_profile_from_row(self._fetch_one_dict(select(data_profiles).where(data_profiles.c.id == profile_id)))

    def list_for_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        statement = (
            select(data_profiles)
            .where(data_profiles.c.dataset_id == dataset_id)
            .order_by(data_profiles.c.created_at, data_profiles.c.id)
        )
        return [_data_profile_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = (
            select(data_profiles)
            .select_from(data_profiles.join(datasets, data_profiles.c.dataset_id == datasets.c.id))
            .where(datasets.c.project_id == project_id)
            .order_by(data_profiles.c.created_at, data_profiles.c.id)
        )
        return [_data_profile_from_row(row) for row in self._fetch_all_dicts(statement)]


class SqlAlchemyAnalysisIntentRepository(_SqlAlchemyRepository):
    def save_intent(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_analysis_intent_record(record)
        intent_id = _required_id(normalized, "intentId")
        values = _analysis_intent_values(normalized)

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(analysis_intents).where(analysis_intents.c.id == intent_id)
            ).mappings().first()
            if existing is None:
                connection.execute(insert(analysis_intents).values(**values))
                return
            current = _analysis_intent_from_row(_row_to_json_dict(existing))
            if current["intentHash"] != normalized["intentHash"]:
                raise ValueError("AnalysisIntent records are immutable")

        self._with_connection(run)
        return self.get_intent(intent_id)

    def get_intent(self, intent_id: str) -> dict[str, Any]:
        return _analysis_intent_from_row(
            self._fetch_one_dict(select(analysis_intents).where(analysis_intents.c.id == intent_id))
        )

    def attach_execution(self, intent_id: str, plan_id: str, job_id: str) -> dict[str, Any]:
        binding_id = f"intent_exec_{intent_id.removeprefix('intent_')[:16]}"

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(analysis_intent_executions).where(
                    or_(
                        analysis_intent_executions.c.intent_id == intent_id,
                        analysis_intent_executions.c.plan_id == plan_id,
                        analysis_intent_executions.c.job_id == job_id,
                    )
                )
            ).mappings().first()
            if existing is None:
                connection.execute(
                    insert(analysis_intent_executions).values(
                        id=binding_id,
                        intent_id=intent_id,
                        plan_id=plan_id,
                        job_id=job_id,
                    )
                )
                return
            current = _row_to_json_dict(existing)
            if current["intent_id"] != intent_id or current["plan_id"] != plan_id or current["job_id"] != job_id:
                raise ValueError("AnalysisIntent execution association is immutable")

        self._with_connection(run)
        result = self.get_execution(intent_id)
        if result is None:
            raise LookupError(f"Unknown AnalysisIntent execution association: {intent_id}")
        return result

    def get_execution(self, intent_id: str) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            row = connection.execute(
                select(analysis_intent_executions).where(analysis_intent_executions.c.intent_id == intent_id)
            ).mappings().first()
            return _intent_execution_from_row(_row_to_json_dict(row)) if row is not None else None

        return self._with_connection(run)

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            row = connection.execute(
                select(analysis_intent_executions).where(analysis_intent_executions.c.job_id == job_id)
            ).mappings().first()
            return _intent_execution_from_row(_row_to_json_dict(row)) if row is not None else None

        return self._with_connection(run)


class SqlAlchemyCapabilityPlanningRepository(_SqlAlchemyRepository):
    def save_resolution(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_capability_resolution_record(record)
        resolution_id = normalized["resolutionId"]
        values = _capability_resolution_values(normalized)

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(capability_eligibility_resolutions).where(capability_eligibility_resolutions.c.id == resolution_id)
            ).mappings().first()
            if existing is None:
                connection.execute(insert(capability_eligibility_resolutions).values(**values))
                return
            if str(existing["resolution_hash"]) != normalized["resolutionHash"]:
                raise ValueError("Eligibility Resolution records are immutable")

        self._with_connection(run)
        return self.get_resolution(resolution_id)

    def get_resolution(self, resolution_id: str) -> dict[str, Any]:
        return _capability_resolution_from_row(
            self._fetch_one_dict(
                select(capability_eligibility_resolutions).where(capability_eligibility_resolutions.c.id == resolution_id)
            )
        )

    def save_decision(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_capability_decision_record(record)
        decision_id = normalized["decisionId"]
        values = _capability_decision_values(normalized)

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(capability_planning_decisions).where(capability_planning_decisions.c.id == decision_id)
            ).mappings().first()
            if existing is None:
                connection.execute(insert(capability_planning_decisions).values(**values))
                return
            if str(existing["decision_hash"]) != normalized["decisionHash"]:
                raise ValueError("Capability Planning Decision records are immutable")

        self._with_connection(run)
        return self.get_decision(decision_id)

    def get_decision(self, decision_id: str) -> dict[str, Any]:
        return _capability_decision_from_row(
            self._fetch_one_dict(
                select(capability_planning_decisions).where(capability_planning_decisions.c.id == decision_id)
            )
        )

    def attach_execution(self, decision_id: str, intent_id: str, plan_id: str, job_id: str) -> dict[str, Any]:
        decision = self.get_decision(decision_id)
        if decision["intentId"] != intent_id or decision["outcome"] != "PLAN_READY":
            raise ValueError("Only a matching PLAN_READY decision can be attached to execution")
        binding_id = f"cap_exec_{decision_id.removeprefix('decision_')[:16]}"

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(capability_planning_executions).where(
                    or_(
                        capability_planning_executions.c.decision_id == decision_id,
                        capability_planning_executions.c.plan_id == plan_id,
                        capability_planning_executions.c.job_id == job_id,
                    )
                )
            ).mappings().first()
            if existing is None:
                connection.execute(
                    insert(capability_planning_executions).values(
                        id=binding_id,
                        decision_id=decision_id,
                        intent_id=intent_id,
                        plan_id=plan_id,
                        job_id=job_id,
                    )
                )
                return
            current = _row_to_json_dict(existing)
            if (
                current["decision_id"] != decision_id
                or current["intent_id"] != intent_id
                or current["plan_id"] != plan_id
                or current["job_id"] != job_id
            ):
                raise ValueError("Capability Planning execution association is immutable")

        self._with_connection(run)
        result = self.get_execution_for_job(job_id)
        if result is None:
            raise LookupError(f"Unknown Capability Planning execution association: {job_id}")
        return result

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            row = connection.execute(
                select(capability_planning_executions).where(capability_planning_executions.c.job_id == job_id)
            ).mappings().first()
            return _capability_execution_from_row(_row_to_json_dict(row)) if row is not None else None

        return self._with_connection(run)


class SqlAlchemyDependencyExecutionRepository(_SqlAlchemyRepository):
    def save_plan_bindings(
        self, plan_id: str, plan_hash: str, graph_hash: str, bindings: list[DependencyBinding | Mapping[str, Any]]
    ) -> list[dict[str, Any]]:
        plan_row = self._fetch_one_dict(select(analysis_plans).where(analysis_plans.c.id == plan_id))
        normalized = _normalize_plan_bindings(
            _analysis_plan_from_row(plan_row), plan_id, plan_hash, graph_hash, bindings
        )

        def run(connection: Connection) -> None:
            rows = [
                _planned_binding_from_row(_row_to_json_dict(row))
                for row in connection.execute(
                    select(plan_dependency_bindings)
                    .where(plan_dependency_bindings.c.plan_id == plan_id)
                    .order_by(plan_dependency_bindings.c.binding_id)
                ).mappings().all()
            ]
            if rows:
                if rows != sorted(normalized, key=lambda item: item["bindingId"]):
                    raise ValueError("Planned dependency binding records are immutable")
                return
            for item in normalized:
                connection.execute(insert(plan_dependency_bindings).values(**_planned_binding_values(item)))

        self._with_connection(run)
        return self.list_plan_bindings(plan_id)

    def list_plan_bindings(self, plan_id: str) -> list[dict[str, Any]]:
        statement = (
            select(plan_dependency_bindings)
            .where(plan_dependency_bindings.c.plan_id == plan_id)
            .order_by(plan_dependency_bindings.c.binding_id)
        )
        return [_planned_binding_from_row(item) for item in self._fetch_all_dicts(statement)]

    def save_binding_resolution(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_binding_resolution_record(record)
        values = _binding_resolution_values(normalized)

        def run(connection: Connection) -> None:
            row = connection.execute(
                select(runtime_artifact_binding_resolutions).where(
                    and_(
                        runtime_artifact_binding_resolutions.c.job_id == normalized["jobId"],
                        runtime_artifact_binding_resolutions.c.binding_id == normalized["bindingId"],
                    )
                )
            ).mappings().first()
            if row is not None:
                existing = _binding_resolution_from_row(_row_to_json_dict(row))
                if existing["recordHash"] != normalized["recordHash"]:
                    raise ValueError("Runtime artifact binding resolution records are immutable")
                return
            connection.execute(insert(runtime_artifact_binding_resolutions).values(**values))

        self._with_connection(run)
        return next(
            item for item in self.list_binding_resolutions(normalized["jobId"])
            if item["bindingId"] == normalized["bindingId"]
        )

    def list_binding_resolutions(self, job_id: str) -> list[dict[str, Any]]:
        statement = (
            select(runtime_artifact_binding_resolutions)
            .where(runtime_artifact_binding_resolutions.c.job_id == job_id)
            .order_by(runtime_artifact_binding_resolutions.c.binding_id)
        )
        return [_binding_resolution_from_row(item) for item in self._fetch_all_dicts(statement)]

    def save_execution(self, record: DependencyExecutionRecord | Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_dependency_execution_record(record)
        values = _dependency_execution_values(normalized)

        def run(connection: Connection) -> None:
            row = connection.execute(
                select(dependency_execution_records).where(dependency_execution_records.c.job_id == normalized["jobId"])
            ).mappings().first()
            if row is not None:
                existing = _dependency_execution_from_row(_row_to_json_dict(row))
                if existing["executionHash"] != normalized["executionHash"]:
                    raise ValueError("Dependency execution records are immutable")
                return
            connection.execute(insert(dependency_execution_records).values(**values))

        self._with_connection(run)
        return self.get_execution_for_job(normalized["jobId"]) or normalized

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            row = connection.execute(
                select(dependency_execution_records).where(dependency_execution_records.c.job_id == job_id)
            ).mappings().first()
            return _dependency_execution_from_row(_row_to_json_dict(row)) if row is not None else None

        return self._with_connection(run)

    def save_lineage(self, record: ArtifactLineageRecord | Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_artifact_lineage_record(record)
        values = _artifact_lineage_values(normalized)

        def run(connection: Connection) -> None:
            row = connection.execute(
                select(artifact_lineage_records).where(artifact_lineage_records.c.artifact_id == normalized["artifactId"])
            ).mappings().first()
            if row is not None:
                existing = _artifact_lineage_from_row(_row_to_json_dict(row))
                if existing["lineageHash"] != normalized["lineageHash"]:
                    raise ValueError("Artifact lineage records are immutable")
                return
            connection.execute(insert(artifact_lineage_records).values(**values))

        self._with_connection(run)
        return self.get_lineage_for_artifact(normalized["artifactId"]) or normalized

    def list_lineage_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = (
            select(artifact_lineage_records)
            .where(artifact_lineage_records.c.job_id == job_id)
            .order_by(artifact_lineage_records.c.artifact_id)
        )
        return [_artifact_lineage_from_row(item) for item in self._fetch_all_dicts(statement)]

    def get_lineage_for_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            row = connection.execute(
                select(artifact_lineage_records).where(artifact_lineage_records.c.artifact_id == artifact_id)
            ).mappings().first()
            return _artifact_lineage_from_row(_row_to_json_dict(row)) if row is not None else None

        return self._with_connection(run)


class SqlAlchemyAnalysisPlanRepository(_SqlAlchemyRepository):
    def save_plan(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_analysis_plan_record(record)
        plan_id = _required_id(normalized, "planId")
        values = _analysis_plan_values(normalized)

        def run(connection: Connection) -> None:
            _ensure_user(connection, user_id=values["created_by"])
            existing = connection.execute(
                select(analysis_plans.c.plan_hash, analysis_plans.c.analysis_plan_json).where(analysis_plans.c.id == plan_id)
            ).mappings().first()
            if existing is None:
                connection.execute(insert(analysis_plans).values(**values))
            else:
                existing_schema = (_json_copy(existing["analysis_plan_json"]) or {}).get("schemaVersion")
                new_schema = normalized["analysisPlan"].get("schemaVersion")
                if "0.2" in {existing_schema, new_schema} and existing["plan_hash"] != normalized["planHash"]:
                    raise ValueError("AnalysisPlan 0.2 records are immutable")
                connection.execute(
                    analysis_plans.update()
                    .where(analysis_plans.c.id == plan_id)
                    .values(**{**values, "updated_at": func.now()})
                )

        self._with_connection(run)
        return self.get_plan(plan_id)

    def get_plan(self, plan_id: str) -> dict[str, Any]:
        return _analysis_plan_from_row(self._fetch_one_dict(select(analysis_plans).where(analysis_plans.c.id == plan_id)))

    def get_plan_for_job(self, job_id: str) -> dict[str, Any]:
        def run(connection: Connection) -> str:
            plan_id = connection.execute(select(jobs.c.plan_id).where(jobs.c.id == job_id)).scalar_one_or_none()
            if plan_id:
                return str(plan_id)
            fallback = connection.execute(select(analysis_plans.c.id).where(analysis_plans.c.job_id == job_id)).scalar_one_or_none()
            if fallback is None:
                raise LookupError(f"Unknown analysis plan for job id: {job_id}")
            return str(fallback)

        return self.get_plan(self._with_connection(run))

    def attach_plan_to_job(self, plan_id: str, job_id: str) -> dict[str, Any]:
        def run(connection: Connection) -> None:
            exists = connection.execute(select(analysis_plans.c.id).where(analysis_plans.c.id == plan_id)).scalar_one_or_none()
            if exists is None:
                raise LookupError(f"Unknown analysis plan id: {plan_id}")
            job_exists = connection.execute(select(jobs.c.id).where(jobs.c.id == job_id)).scalar_one_or_none()
            if job_exists is None:
                raise LookupError(f"Unknown job id: {job_id}")
            connection.execute(
                analysis_plans.update()
                .where(analysis_plans.c.id == plan_id)
                .values(job_id=job_id, updated_at=func.now())
            )
            connection.execute(jobs.update().where(jobs.c.id == job_id).values(plan_id=plan_id, updated_at=func.now()))

        self._with_connection(run)
        return self.get_plan(plan_id)


class SqlAlchemyJobRepository(_SqlAlchemyRepository):
    def save(self, job: Mapping[str, Any]) -> dict[str, Any]:
        job_id = _required_id(job, "jobId")
        created_by = str(job.get("createdBy") or job.get("created_by") or "user_local")
        status = validate_job_status(job.get("status") or JobStatus.created.value)
        values = {
            "id": job_id,
            "project_id": str(job["projectId"]),
            "dataset_id": job.get("datasetId"),
            "plan_id": job.get("planId") or job.get("plan_id"),
            "kind": str(job.get("kind") or "analysis"),
            "status": status,
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            _ensure_user(connection, user_id=created_by)
            connection.execute(delete(jobs).where(jobs.c.id == job_id))
            connection.execute(insert(jobs).values(**values))

        self._with_connection(run)
        return self.get(job_id)

    def get(self, job_id: str) -> dict[str, Any]:
        return _job_from_row(self._fetch_one_dict(select(jobs).where(jobs.c.id == job_id)))

    def set_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        def run(connection: Connection) -> None:
            current = connection.execute(select(jobs.c.status).where(jobs.c.id == job_id)).scalar_one_or_none()
            if current is None:
                raise LookupError(f"Unknown job id: {job_id}")
            next_status = validate_job_transition(current, status)
            connection.execute(jobs.update().where(jobs.c.id == job_id).values(status=next_status, updated_at=func.now()))

        self._with_connection(run)
        return self.get(job_id)

    def update_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        return self.set_status(job_id, status)

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = select(jobs).where(jobs.c.project_id == project_id).order_by(jobs.c.created_at.desc(), jobs.c.id)
        return [_job_from_row(row) for row in self._fetch_all_dicts(statement)]


class SqlAlchemyJobEventRepository(_SqlAlchemyRepository):
    POSTGRES_ADVISORY_LOCK_SQL = "SELECT pg_advisory_xact_lock(hashtext('mdi_job_events'), hashtext(:job_id))"

    def __init__(self, bind: Engine | Connection) -> None:
        super().__init__(bind)
        self._event_lock = Lock()

    def append_event(
        self,
        job_id: str,
        *,
        event_type: str,
        status: JobEventStatus | str,
        message: str,
        payload: Mapping[str, Any] | None = None,
        progress: float | None = None,
    ) -> JobEvent:
        def run(connection: Connection) -> JobEvent:
            _lock_job_event_sequence(connection, job_id)
            max_seq = connection.execute(select(func.max(job_events.c.seq)).where(job_events.c.job_id == job_id)).scalar()
            seq = int(max_seq or 0) + 1
            event = JobEvent(
                id=f"evt_{job_id}_{seq:04d}",
                jobId=job_id,
                seq=seq,
                eventType=event_type,
                status=JobEventStatus(_enum_value(status)),
                message=message,
                progress=progress,
                payload=dict(payload or {}),
                createdAt=_utc_now(),
            )
            connection.execute(insert(job_events).values(**_job_event_values(event)))
            return event

        with self._event_lock:
            return self._with_connection(run)

    def list_for_job(self, job_id: str) -> list[JobEvent]:
        return self.list_events_after_seq(job_id, 0)

    def list_events(self, job_id: str) -> list[JobEvent]:
        return self.list_for_job(job_id)

    def list_events_after_seq(self, job_id: str, after_seq: int) -> list[JobEvent]:
        statement = (
            select(job_events)
            .where(job_events.c.job_id == job_id, job_events.c.seq > after_seq)
            .order_by(job_events.c.seq)
        )
        return [_job_event_from_row(row) for row in self._fetch_all_dicts(statement)]


def _lock_job_event_sequence(connection: Connection, job_id: str) -> None:
    if connection.dialect.name.startswith("postgresql"):
        connection.execute(text(SqlAlchemyJobEventRepository.POSTGRES_ADVISORY_LOCK_SQL), {"job_id": job_id})


class SqlAlchemyToolCallRepository(_SqlAlchemyRepository):
    def save(self, tool_call: ToolCall | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(tool_call)
        tool_call_id = _required_id(record)
        job_id = str(record["jobId"])
        step_id = str(record["stepId"])
        idempotency_key = str(record.get("idempotencyKey") or record.get("idempotency_key") or f"{job_id}:{step_id}")
        status = validate_tool_call_status(record.get("status") or "planned")
        values = {
            "id": tool_call_id,
            "job_id": job_id,
            "step_id": step_id,
            "tool_id": str(record["toolId"]),
            "idempotency_key": idempotency_key,
            "attempt": int(record.get("attempt") or 1),
            "status": status,
            "params_json": _json_copy(record.get("params") or {}),
            "error_json": _json_copy(record.get("error")) if record.get("error") else None,
        }

        def run(connection: Connection) -> str:
            existing = connection.execute(
                select(tool_calls).where(
                    or_(
                        tool_calls.c.id == tool_call_id,
                        and_(tool_calls.c.job_id == job_id, tool_calls.c.step_id == step_id),
                        and_(tool_calls.c.job_id == job_id, tool_calls.c.idempotency_key == idempotency_key),
                    )
                )
            ).mappings().first()
            if existing is None:
                connection.execute(insert(tool_calls).values(**values))
                return tool_call_id
            existing_row = _row_to_json_dict(existing)
            existing_id = str(existing_row["id"])
            next_status = validate_tool_call_transition(existing_row.get("status") or "planned", status)
            update_values = {**values, "id": existing_id, "status": next_status, "attempt": max(int(existing_row.get("attempt") or 1), values["attempt"])}
            connection.execute(tool_calls.update().where(tool_calls.c.id == existing_id).values(**update_values, updated_at=func.now()))
            return existing_id

        stored_id = self._with_connection(run)
        return self.get(stored_id)

    def get(self, tool_call_id: str) -> dict[str, Any]:
        return _tool_call_from_row(self._fetch_one_dict(select(tool_calls).where(tool_calls.c.id == tool_call_id)))

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = select(tool_calls).where(tool_calls.c.job_id == job_id).order_by(tool_calls.c.created_at, tool_calls.c.id)
        return [_tool_call_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_by_job(self, job_id: str) -> list[dict[str, Any]]:
        return self.list_for_job(job_id)


class SqlAlchemyArtifactRepository(_SqlAlchemyRepository):
    def save(self, artifact: Artifact | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(artifact)
        artifact_id = _required_id(record, "artifactId")
        _validate_artifact_storage_record(record)
        metadata = _json_copy(record.get("metadata") or {})
        content_type = str(record.get("contentType") or metadata.get("provenance", {}).get("mediaType") or "application/octet-stream")
        sha256 = str(record.get("sha256") or record.get("contentHash") or "")
        storage_provider = str(record.get("storageProvider") or record.get("storage_provider") or metadata.get("storageProvider") or metadata.get("storage_provider") or "local")
        bucket = record.get("bucket") or metadata.get("bucket")
        values = {
            "id": artifact_id,
            "project_id": str(record["projectId"]),
            "dataset_id": record.get("datasetId"),
            "job_id": str(record["jobId"]),
            "tool_call_id": record.get("toolCallId"),
            "type": _enum_value(record.get("type")),
            "name": str(record.get("name") or artifact_id),
            "version": str(record.get("version") or "1"),
            "storage_key": str(record["storageKey"]),
            "storage_provider": storage_provider,
            "bucket": str(bucket) if bucket else None,
            "preview_key": record.get("previewKey"),
            "size_bytes": int(record.get("sizeBytes") or 0),
            "content_type": content_type,
            "content_hash": str(record.get("contentHash") or sha256),
            "sha256": sha256,
            "metadata_json": metadata,
        }

        def run(connection: Connection) -> str:
            existing = connection.execute(
                select(artifacts).where(
                    or_(
                        artifacts.c.id == artifact_id,
                        and_(
                            artifacts.c.job_id == values["job_id"],
                            artifacts.c.storage_key == values["storage_key"],
                            artifacts.c.sha256 == values["sha256"],
                        ),
                    )
                )
            ).mappings().first()
            if existing is None:
                connection.execute(insert(artifacts).values(**values))
                return artifact_id
            existing_row = _row_to_json_dict(existing)
            existing_id = str(existing_row["id"])
            connection.execute(artifacts.update().where(artifacts.c.id == existing_id).values(**{**values, "id": existing_id}))
            return existing_id

        stored_id = self._with_connection(run)
        return self.get(stored_id)

    def get(self, artifact_id: str) -> dict[str, Any]:
        return _artifact_from_row(self._fetch_one_dict(select(artifacts).where(artifacts.c.id == artifact_id)))

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = select(artifacts).where(artifacts.c.job_id == job_id).order_by(artifacts.c.created_at, artifacts.c.id)
        return [_artifact_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_artifacts_by_job(self, job_id: str) -> list[dict[str, Any]]:
        return self.list_for_job(job_id)

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = select(artifacts).where(artifacts.c.project_id == project_id).order_by(artifacts.c.created_at.desc(), artifacts.c.id)
        return [_artifact_from_row(row) for row in self._fetch_all_dicts(statement)]


class SqlAlchemyRecipeRepository(_SqlAlchemyRepository):
    def save(self, recipe: VisualizationRecipe | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(recipe)
        recipe_id = _required_id(record, "recipeId")
        created_by = str(record.get("createdBy") or record.get("created_by") or "user_local")
        values = {
            "id": recipe_id,
            "project_id": str(record["projectId"]),
            "source_job_id": record.get("sourceJobId"),
            "name": str(record.get("name") or recipe_id),
            "recipe_json": _json_copy(record),
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            _ensure_user(connection, user_id=created_by)
            connection.execute(delete(visualization_recipes).where(visualization_recipes.c.id == recipe_id))
            connection.execute(insert(visualization_recipes).values(**values))

        self._with_connection(run)
        return self.get(recipe_id)

    def get(self, recipe_id: str) -> dict[str, Any]:
        row = self._fetch_one_dict(select(visualization_recipes).where(visualization_recipes.c.id == recipe_id))
        return _recipe_from_row(row)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = (
            select(visualization_recipes)
            .where(visualization_recipes.c.source_job_id == job_id)
            .order_by(visualization_recipes.c.created_at, visualization_recipes.c.id)
        )
        return [_recipe_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = (
            select(visualization_recipes)
            .where(visualization_recipes.c.project_id == project_id)
            .order_by(visualization_recipes.c.created_at.desc(), visualization_recipes.c.id)
        )
        return [_recipe_from_row(row) for row in self._fetch_all_dicts(statement)]


class SqlAlchemyReportRepository(_SqlAlchemyRepository):
    def save(self, report: Mapping[str, Any]) -> dict[str, Any]:
        record = _json_copy(report)
        report_id = _required_id(record, "reportId")
        created_by = str(record.get("createdBy") or record.get("created_by") or "user_local")
        job_id_value = record.get("jobId") or record.get("sourceJobId")
        if not job_id_value:
            raise ValueError("Report record is missing jobId/sourceJobId")
        job_id = str(job_id_value)
        values = {
            "id": report_id,
            "project_id": str(record["projectId"]),
            "dataset_id": record.get("datasetId"),
            "job_id": job_id,
            "version": str(record.get("version") or "1"),
            "title": str(record.get("title") or record.get("name") or report_id),
            "markdown_key": record.get("markdownKey") or record.get("markdownArtifactKey"),
            "html_key": record.get("htmlKey") or record.get("htmlArtifactKey"),
            "report_json": record,
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            _ensure_user(connection, user_id=created_by)
            connection.execute(delete(reports).where(reports.c.id == report_id))
            connection.execute(insert(reports).values(**values))

        self._with_connection(run)
        return self.get(report_id)

    def get(self, report_id: str) -> dict[str, Any]:
        return _report_from_row(self._fetch_one_dict(select(reports).where(reports.c.id == report_id)))

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = select(reports).where(reports.c.job_id == job_id).order_by(reports.c.created_at, reports.c.id)
        return [_report_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = select(reports).where(reports.c.project_id == project_id).order_by(reports.c.created_at.desc(), reports.c.id)
        return [_report_from_row(row) for row in self._fetch_all_dicts(statement)]


class SqlAlchemyScientificInterpretationRepository(_SqlAlchemyRepository):
    @contextmanager
    def idempotency_guard(self, job_id: str, mode: str, idempotency_key_hash: str) -> Iterator[None]:
        identity = f"{job_id}\x1f{mode}\x1f{idempotency_key_hash}"
        dialect = self.bind.dialect.name
        if dialect != "postgresql":
            with _SQL_INTERPRETATION_LOCKS.guard((dialect, identity)):
                yield
            return

        advisory_key = int.from_bytes(hashlib.sha256(identity.encode("utf-8")).digest()[:8], "big", signed=True)
        if isinstance(self.bind, Engine):
            with self.bind.connect() as connection:
                connection.execute(text("SELECT pg_advisory_lock(:key)"), {"key": advisory_key})
                try:
                    yield
                finally:
                    connection.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": advisory_key})
            return

        self.bind.execute(text("SELECT pg_advisory_lock(:key)"), {"key": advisory_key})
        try:
            yield
        finally:
            self.bind.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": advisory_key})

    def save_bundle(self, bundle: ScientificEvidenceBundle | Mapping[str, Any]) -> dict[str, Any]:
        parsed = ScientificEvidenceBundle.model_validate(
            bundle.model_dump(mode="json") if isinstance(bundle, ScientificEvidenceBundle) else bundle
        )
        record = parsed.model_dump(mode="json")
        values = {
            "id": parsed.bundleId,
            "bundle_hash": parsed.bundleHash,
            "project_id": parsed.projectId,
            "dataset_id": parsed.datasetId,
            "job_id": parsed.jobId,
            "plan_id": parsed.planId,
            "plan_hash": parsed.planHash,
            "schema_version": parsed.schemaVersion,
            "execution_outcome": parsed.executionOutcome,
            "evidence_item_count": len(parsed.evidenceItems),
            "warning_count": len(parsed.bundleWarnings),
            "limitation_count": len(parsed.bundleLimitations),
            "bundle_json": record,
        }

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(scientific_evidence_bundles.c.bundle_hash).where(scientific_evidence_bundles.c.id == parsed.bundleId)
            ).scalar_one_or_none()
            if existing is not None:
                if existing != parsed.bundleHash:
                    raise ValueError("Scientific evidence bundles are immutable")
                return
            connection.execute(insert(scientific_evidence_bundles).values(**values))

        self._with_connection(run)
        return self.get_bundle(parsed.bundleId)

    def get_bundle(self, bundle_id: str) -> dict[str, Any]:
        row = self._fetch_one_dict(select(scientific_evidence_bundles).where(scientific_evidence_bundles.c.id == bundle_id))
        return ScientificEvidenceBundle.model_validate(row["bundle_json"]).model_dump(mode="json")

    def save_run(
        self,
        bundle: ScientificEvidenceBundle | Mapping[str, Any],
        execution: InterpretationExecutionRecord | Mapping[str, Any],
        *,
        interpretation_id: str | None = None,
    ) -> dict[str, Any]:
        parsed_bundle = ScientificEvidenceBundle.model_validate(
            bundle.model_dump(mode="json") if isinstance(bundle, ScientificEvidenceBundle) else bundle
        )
        parsed = InterpretationExecutionRecord.model_validate(
            execution.model_dump(mode="json") if isinstance(execution, InterpretationExecutionRecord) else execution
        )
        self.save_bundle(parsed_bundle)
        _validate_interpretation_run_association(parsed_bundle, parsed)
        values = {
            "id": parsed.executionRecordId,
            "execution_record_hash": parsed.executionRecordHash,
            "bundle_id": parsed_bundle.bundleId,
            "project_id": parsed_bundle.projectId,
            "dataset_id": parsed_bundle.datasetId,
            "job_id": parsed_bundle.jobId,
            "plan_id": parsed_bundle.planId,
            "mode": parsed.mode.value,
            "provider": parsed.provider,
            "provider_model": parsed.providerModel,
            "provider_config_hash": parsed.providerConfigHash,
            "idempotency_key_hash": parsed.idempotencyKeyHash,
            "repair_count": parsed.repairCount,
            "outcome": parsed.outcome.value,
            "interpretation_id": interpretation_id,
            "execution_json": parsed.model_dump(mode="json"),
        }

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(scientific_interpretation_runs).where(scientific_interpretation_runs.c.id == parsed.executionRecordId)
            ).mappings().first()
            if existing is not None:
                if existing["execution_record_hash"] != parsed.executionRecordHash:
                    raise ValueError("Scientific interpretation runs are immutable")
                if existing["interpretation_id"] != interpretation_id:
                    raise ValueError("Scientific interpretation run association is immutable")
                return
            if parsed.idempotencyKeyHash:
                bound = connection.execute(
                    select(scientific_interpretation_runs.c.execution_record_hash).where(
                        and_(
                            scientific_interpretation_runs.c.job_id == parsed_bundle.jobId,
                            scientific_interpretation_runs.c.mode == parsed.mode.value,
                            scientific_interpretation_runs.c.idempotency_key_hash == parsed.idempotencyKeyHash,
                        )
                    )
                ).scalar_one_or_none()
                if bound is not None and bound != parsed.executionRecordHash:
                    raise ValueError("Scientific interpretation idempotency key is already bound to another run")
            connection.execute(insert(scientific_interpretation_runs).values(**values))

        try:
            self._with_connection(run)
        except IntegrityError as exc:
            if parsed.idempotencyKeyHash:
                existing = self.get_run_by_idempotency(
                    parsed_bundle.jobId,
                    parsed.mode.value,
                    parsed.idempotencyKeyHash,
                )
                if existing is not None:
                    if (
                        existing["execution"]["executionRecordHash"] != parsed.executionRecordHash
                        or existing.get("interpretationId") != interpretation_id
                    ):
                        raise ValueError(
                            "Scientific interpretation idempotency key is already bound to another run"
                        ) from exc
                    return existing
            raise
        return self.get_run(parsed.executionRecordId)

    def get_run(self, execution_record_id: str) -> dict[str, Any]:
        row = self._fetch_one_dict(
            select(scientific_interpretation_runs).where(scientific_interpretation_runs.c.id == execution_record_id)
        )
        return {
            "execution": InterpretationExecutionRecord.model_validate(row["execution_json"]).model_dump(mode="json"),
            "bundleId": row["bundle_id"],
            "jobId": row["job_id"],
            "mode": row["mode"],
            "idempotencyKeyHash": row["idempotency_key_hash"],
            "interpretationId": row["interpretation_id"],
        }

    def get_run_by_idempotency(self, job_id: str, mode: str, idempotency_key_hash: str) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            row = connection.execute(
                select(scientific_interpretation_runs).where(
                    and_(
                        scientific_interpretation_runs.c.job_id == job_id,
                        scientific_interpretation_runs.c.mode == mode,
                        scientific_interpretation_runs.c.idempotency_key_hash == idempotency_key_hash,
                    )
                )
            ).mappings().first()
            if row is None:
                return None
            normalized = _row_to_json_dict(row)
            return {
                "execution": InterpretationExecutionRecord.model_validate(normalized["execution_json"]).model_dump(mode="json"),
                "bundleId": normalized["bundle_id"],
                "jobId": normalized["job_id"],
                "mode": normalized["mode"],
                "idempotencyKeyHash": normalized["idempotency_key_hash"],
                "interpretationId": normalized["interpretation_id"],
            }
        return self._with_connection(run)

    def list_runs_for_job(self, job_id: str) -> list[dict[str, Any]]:
        rows = self._fetch_all_dicts(
            select(scientific_interpretation_runs)
            .where(scientific_interpretation_runs.c.job_id == job_id)
            .order_by(scientific_interpretation_runs.c.created_at, scientific_interpretation_runs.c.id)
        )
        return [
            {
                "execution": InterpretationExecutionRecord.model_validate(row["execution_json"]).model_dump(mode="json"),
                "bundleId": row["bundle_id"],
                "jobId": row["job_id"],
                "mode": row["mode"],
                "idempotencyKeyHash": row["idempotency_key_hash"],
                "interpretationId": row["interpretation_id"],
            }
            for row in rows
        ]
    def save_interpretation(
        self,
        bundle: ScientificEvidenceBundle | Mapping[str, Any],
        interpretation: GroundedScientificInterpretation | Mapping[str, Any],
        execution: InterpretationExecutionRecord | Mapping[str, Any],
    ) -> dict[str, Any]:
        parsed_bundle = ScientificEvidenceBundle.model_validate(
            bundle.model_dump(mode="json") if isinstance(bundle, ScientificEvidenceBundle) else bundle
        )
        parsed = GroundedScientificInterpretation.model_validate(
            interpretation.model_dump(mode="json")
            if isinstance(interpretation, GroundedScientificInterpretation)
            else interpretation
        )
        execution_record = InterpretationExecutionRecord.model_validate(
            execution.model_dump(mode="json") if isinstance(execution, InterpretationExecutionRecord) else execution
        )
        _validate_interpretation_associations(parsed_bundle, parsed, execution_record)
        evidence = {item.evidenceItemId: item for item in parsed_bundle.evidenceItems}
        interpretation_values = {
            "id": parsed.interpretationId,
            "interpretation_hash": parsed.interpretationHash,
            "bundle_id": parsed.sourceBundleId,
            "project_id": parsed_bundle.projectId,
            "dataset_id": parsed_bundle.datasetId,
            "job_id": parsed.sourceJobId,
            "plan_id": parsed.sourcePlanId,
            "mode": parsed.mode.value,
            "provider": parsed.provider,
            "repair_count": parsed.repairCount,
            "outcome": parsed.outcome.value,
            "execution_record_id": execution_record.executionRecordId,
            "interpretation_json": parsed.model_dump(mode="json"),
            "execution_json": execution_record.model_dump(mode="json"),
        }

        def run(connection: Connection) -> None:
            scoped = SqlAlchemyScientificInterpretationRepository(connection)
            scoped.save_bundle(parsed_bundle)
            scoped.save_run(parsed_bundle, execution_record, interpretation_id=parsed.interpretationId)
            existing = connection.execute(
                select(scientific_interpretations).where(scientific_interpretations.c.id == parsed.interpretationId)
            ).mappings().first()
            if existing is not None:
                if (
                    existing["interpretation_hash"] != parsed.interpretationHash
                    or existing["execution_record_id"] != execution_record.executionRecordId
                    or existing["bundle_id"] != parsed_bundle.bundleId
                ):
                    raise ValueError("Scientific interpretations are immutable")
                return
            connection.execute(insert(scientific_interpretations).values(**interpretation_values))
            for claim in parsed.claims:
                connection.execute(insert(scientific_interpretation_claims).values(
                    interpretation_id=parsed.interpretationId,
                    claim_id=claim.claimId,
                    claim_type=claim.claimType.value,
                    predicate=claim.semanticPredicate.value,
                    confidence_class=claim.confidenceClass.value,
                    grounding_status=claim.groundingStatus.value,
                    display_order=claim.displayOrder,
                    claim_json=claim.model_dump(mode="json"),
                ))
                roles = {
                    "SUPPORTING": set(claim.subjectEvidenceIds + claim.supportingEvidenceIds),
                    "LIMITING": set(claim.limitingEvidenceIds),
                    "CONTRADICTING": set(claim.contradictingEvidenceIds),
                }
                for role, evidence_ids in roles.items():
                    for evidence_id in sorted(evidence_ids):
                        item = evidence[evidence_id]
                        connection.execute(insert(scientific_interpretation_evidence_links).values(
                            interpretation_id=parsed.interpretationId,
                            claim_id=claim.claimId,
                            evidence_item_id=evidence_id,
                            role=role,
                            source_artifact_id=item.sourceArtifactId,
                            source_artifact_hash=item.sourceArtifactChecksum,
                            field_locator_json=item.fieldLocator.model_dump(mode="json"),
                        ))

        self._with_connection(run)
        return self.get_interpretation(parsed.interpretationId)

    def get_interpretation(self, interpretation_id: str) -> dict[str, Any]:
        row = self._fetch_one_dict(
            select(scientific_interpretations).where(scientific_interpretations.c.id == interpretation_id)
        )
        return {
            "interpretation": GroundedScientificInterpretation.model_validate(row["interpretation_json"]).model_dump(mode="json"),
            "execution": InterpretationExecutionRecord.model_validate(row["execution_json"]).model_dump(mode="json"),
            "bundleId": row["bundle_id"],
            "jobId": row["job_id"],
        }

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        rows = self._fetch_all_dicts(
            select(scientific_interpretations)
            .where(scientific_interpretations.c.job_id == job_id)
            .order_by(scientific_interpretations.c.created_at, scientific_interpretations.c.id)
        )
        return [
            {
                "interpretation": GroundedScientificInterpretation.model_validate(row["interpretation_json"]).model_dump(mode="json"),
                "execution": InterpretationExecutionRecord.model_validate(row["execution_json"]).model_dump(mode="json"),
                "bundleId": row["bundle_id"],
                "jobId": row["job_id"],
            }
            for row in rows
        ]


class SqlAlchemyWorkspaceRepository(_SqlAlchemyRepository):
    def create_workspace(
        self,
        workspace: ScientificWorkspace | Mapping[str, Any],
        *,
        panels: list[WorkspacePanel | Mapping[str, Any]] | tuple[WorkspacePanel | Mapping[str, Any], ...] = (),
        initial_layout: WorkspaceLayoutRevision | Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        parsed = _parse_workspace(workspace)
        parsed_panels = tuple(_parse_workspace_panel(panel) for panel in panels)
        parsed_layout = None if initial_layout is None else _parse_workspace_layout_revision(initial_layout)
        _validate_workspace_create_aggregate(parsed, parsed_panels, parsed_layout)
        values = _workspace_values(parsed)

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(scientific_workspaces).where(
                    or_(
                        scientific_workspaces.c.workspace_id == parsed.workspaceId,
                        and_(
                            scientific_workspaces.c.project_id == parsed.projectId,
                            scientific_workspaces.c.source_job_id == parsed.sourceJobId,
                        ),
                    )
                )
            ).mappings().first()
            if existing is not None:
                self._assert_create_compatible(connection, existing, parsed, parsed_panels, parsed_layout)
                return
            try:
                with connection.begin_nested():
                    connection.execute(insert(scientific_workspaces).values(**values))
                    for panel in parsed_panels:
                        connection.execute(insert(workspace_panels).values(**_workspace_panel_values(panel)))
                    if parsed_layout is not None:
                        connection.execute(
                            insert(workspace_layout_revisions).values(**_workspace_layout_values(parsed_layout))
                        )
            except IntegrityError as exc:
                existing = connection.execute(
                    select(scientific_workspaces).where(
                        and_(
                            scientific_workspaces.c.project_id == parsed.projectId,
                            scientific_workspaces.c.source_job_id == parsed.sourceJobId,
                        )
                    )
                ).mappings().first()
                if existing is None:
                    raise WorkspaceConflictError("WORKSPACE_CREATE_CONFLICT") from exc
                self._assert_create_compatible(connection, existing, parsed, parsed_panels, parsed_layout)

        self._with_connection(run)
        return self.get(parsed.workspaceId, project_id=parsed.projectId)

    create = create_workspace

    def get(self, workspace_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(
                select(scientific_workspaces).where(scientific_workspaces.c.workspace_id == workspace_id)
            ).mappings().first()
            if row is None:
                raise WorkspaceNotFoundError()
            normalized = _row_to_json_dict(row)
            _enforce_workspace_project(normalized["project_id"], project_id)
            return self._aggregate_record(connection, normalized)

        return self._with_connection(run)

    def get_by_project_job(self, project_id: str, source_job_id: str) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(
                select(scientific_workspaces).where(
                    and_(
                        scientific_workspaces.c.project_id == project_id,
                        scientific_workspaces.c.source_job_id == source_job_id,
                    )
                )
            ).mappings().first()
            if row is None:
                raise WorkspaceNotFoundError()
            return self._aggregate_record(connection, _row_to_json_dict(row))

        return self._with_connection(run)

    get_by_project_and_job = get_by_project_job

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        def run(connection: Connection) -> list[dict[str, Any]]:
            rows = connection.execute(
                select(scientific_workspaces)
                .where(scientific_workspaces.c.project_id == project_id)
                .order_by(scientific_workspaces.c.updated_at.desc(), scientific_workspaces.c.workspace_id)
            ).mappings().all()
            return [self._aggregate_record(connection, _row_to_json_dict(row)) for row in rows]

        return self._with_connection(run)

    def list_projection_metadata_by_project(self, project_id: str) -> list[dict[str, Any]]:
        """Load bounded Workspace list metadata in one SQL statement."""
        artifact_count = (
            select(func.count())
            .select_from(artifacts)
            .where(artifacts.c.job_id == scientific_workspaces.c.source_job_id)
            .scalar_subquery()
        )
        tool_call_count = (
            select(func.count())
            .select_from(tool_calls)
            .where(tool_calls.c.job_id == scientific_workspaces.c.source_job_id)
            .scalar_subquery()
        )
        interpretation_count = (
            select(func.count())
            .select_from(scientific_interpretations)
            .where(scientific_interpretations.c.job_id == scientific_workspaces.c.source_job_id)
            .scalar_subquery()
        )
        panel_count = (
            select(func.count())
            .select_from(workspace_panels)
            .where(workspace_panels.c.workspace_id == scientific_workspaces.c.workspace_id)
            .scalar_subquery()
        )
        source = (
            scientific_workspaces
            .outerjoin(jobs, jobs.c.id == scientific_workspaces.c.source_job_id)
            .outerjoin(datasets, datasets.c.id == scientific_workspaces.c.dataset_id)
            .outerjoin(data_profiles, data_profiles.c.id == scientific_workspaces.c.profile_id)
            .outerjoin(analysis_intents, analysis_intents.c.id == scientific_workspaces.c.intent_id)
            .outerjoin(analysis_plans, analysis_plans.c.id == scientific_workspaces.c.plan_id)
            .outerjoin(
                capability_planning_executions,
                capability_planning_executions.c.job_id == scientific_workspaces.c.source_job_id,
            )
            .outerjoin(
                capability_planning_decisions,
                capability_planning_decisions.c.id
                == capability_planning_executions.c.decision_id,
            )
            .outerjoin(
                capability_eligibility_resolutions,
                capability_eligibility_resolutions.c.id
                == capability_planning_decisions.c.resolution_id,
            )
            .outerjoin(
                dependency_execution_records,
                dependency_execution_records.c.job_id
                == scientific_workspaces.c.source_job_id,
            )
        )
        statement = (
            select(
                scientific_workspaces,
                jobs.c.id.label("current_job_id"),
                jobs.c.status.label("current_job_status"),
                datasets.c.id.label("current_dataset_id"),
                data_profiles.c.id.label("current_profile_id"),
                data_profiles.c.profile_json.label("current_profile_json"),
                analysis_intents.c.id.label("current_intent_id"),
                analysis_intents.c.intent_hash.label("current_intent_hash"),
                analysis_plans.c.id.label("current_plan_id"),
                analysis_plans.c.plan_hash.label("current_plan_hash"),
                capability_planning_executions.c.id.label("current_capability_execution_id"),
                capability_planning_decisions.c.id.label("current_decision_id"),
                capability_eligibility_resolutions.c.id.label("current_resolution_id"),
                dependency_execution_records.c.outcome.label("dependency_outcome"),
                artifact_count.label("artifact_count"),
                tool_call_count.label("tool_call_count"),
                interpretation_count.label("interpretation_count"),
                panel_count.label("panel_count"),
            )
            .select_from(source)
            .where(scientific_workspaces.c.project_id == project_id)
            .order_by(
                scientific_workspaces.c.updated_at.desc(),
                scientific_workspaces.c.workspace_id,
            )
        )
        return self._fetch_all_dicts(statement)

    def save_panel(
        self,
        panel: WorkspacePanel | Mapping[str, Any],
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        parsed = _parse_workspace_panel(panel)

        def run(connection: Connection) -> dict[str, Any]:
            workspace = self._workspace_row(connection, parsed.workspaceId, for_update=True)
            _enforce_workspace_project(workspace["project_id"], project_id)
            _validate_panel_project_scope(parsed, workspace["project_id"])
            existing = connection.execute(
                select(workspace_panels).where(
                    and_(
                        workspace_panels.c.workspace_id == parsed.workspaceId,
                        workspace_panels.c.panel_id == parsed.panelId,
                    )
                )
            ).mappings().first()
            if existing is not None:
                normalized = _row_to_json_dict(existing)
                if normalized["panel_state_hash"] != parsed.panelStateHash:
                    raise WorkspaceConflictError("WORKSPACE_PANEL_IMMUTABLE_CONFLICT")
                return _workspace_panel_record(normalized)
            count = connection.execute(
                select(func.count()).select_from(workspace_panels).where(
                    workspace_panels.c.workspace_id == parsed.workspaceId
                )
            ).scalar_one()
            if int(count) >= WORKSPACE_MAX_PANELS:
                raise WorkspaceCapacityError("PANEL_CAP_EXCEEDED")
            try:
                with connection.begin_nested():
                    connection.execute(insert(workspace_panels).values(**_workspace_panel_values(parsed)))
            except IntegrityError as exc:
                existing = connection.execute(
                    select(workspace_panels).where(
                        and_(
                            workspace_panels.c.workspace_id == parsed.workspaceId,
                            workspace_panels.c.panel_id == parsed.panelId,
                        )
                    )
                ).mappings().first()
                if existing is None or existing["panel_state_hash"] != parsed.panelStateHash:
                    raise WorkspaceConflictError("WORKSPACE_PANEL_IMMUTABLE_CONFLICT") from exc
            row = connection.execute(
                select(workspace_panels).where(
                    and_(
                        workspace_panels.c.workspace_id == parsed.workspaceId,
                        workspace_panels.c.panel_id == parsed.panelId,
                    )
                )
            ).mappings().one()
            return _workspace_panel_record(_row_to_json_dict(row))

        return self._with_connection(run)

    def save_panels(
        self,
        panels: list[WorkspacePanel | Mapping[str, Any]] | tuple[WorkspacePanel | Mapping[str, Any], ...],
        *,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        parsed = tuple(_parse_workspace_panel(panel) for panel in panels)
        if len({(panel.workspaceId, panel.panelId) for panel in parsed}) != len(parsed):
            raise WorkspaceConflictError("WORKSPACE_PANEL_DUPLICATE")
        return [self.save_panel(panel, project_id=project_id) for panel in parsed]

    def get_panel(
        self,
        workspace_id: str,
        panel_id: str,
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            workspace = self._workspace_row(connection, workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            row = connection.execute(
                select(workspace_panels).where(
                    and_(
                        workspace_panels.c.workspace_id == workspace_id,
                        workspace_panels.c.panel_id == panel_id,
                    )
                )
            ).mappings().first()
            if row is None:
                raise WorkspaceNotFoundError("WORKSPACE_PANEL_NOT_FOUND")
            return _workspace_panel_record(_row_to_json_dict(row))

        return self._with_connection(run)

    def list_panels(self, workspace_id: str, *, project_id: str | None = None) -> list[dict[str, Any]]:
        def run(connection: Connection) -> list[dict[str, Any]]:
            workspace = self._workspace_row(connection, workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            rows = connection.execute(
                select(workspace_panels)
                .where(workspace_panels.c.workspace_id == workspace_id)
                .order_by(workspace_panels.c.ordinal, workspace_panels.c.panel_id)
            ).mappings().all()
            return [_workspace_panel_record(_row_to_json_dict(row)) for row in rows]

        return self._with_connection(run)

    def append_layout_revision(
        self,
        revision: WorkspaceLayoutRevision | Mapping[str, Any],
        *,
        expected_revision: int,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        parsed = _parse_workspace_layout_revision(revision)

        def run(connection: Connection) -> dict[str, Any]:
            workspace = self._workspace_row(connection, parsed.workspaceId, for_update=True)
            _enforce_workspace_project(workspace["project_id"], project_id)
            existing = connection.execute(
                select(workspace_layout_revisions).where(
                    and_(
                        workspace_layout_revisions.c.workspace_id == parsed.workspaceId,
                        workspace_layout_revisions.c.revision == parsed.revision,
                    )
                )
            ).mappings().first()
            if existing is not None:
                if existing["semantic_hash"] != parsed.semanticHash:
                    raise WorkspaceConflictError("WORKSPACE_LAYOUT_IMMUTABLE_CONFLICT")
                if int(workspace["revision"]) != parsed.revision:
                    raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
                return _workspace_layout_record(_row_to_json_dict(existing))
            self._validate_new_layout(connection, workspace, parsed, expected_revision)
            result = connection.execute(
                update(scientific_workspaces)
                .where(
                    and_(
                        scientific_workspaces.c.workspace_id == parsed.workspaceId,
                        scientific_workspaces.c.revision == expected_revision,
                    )
                )
                .values(
                    revision=parsed.revision,
                    active_panel_id=parsed.layout.activePanelId,
                    pinned_selection_json=None if parsed.selection is None else parsed.selection.model_dump(mode="json"),
                    updated_at=parsed.createdAt,
                )
            )
            if result.rowcount != 1:
                raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
            try:
                with connection.begin_nested():
                    connection.execute(
                        insert(workspace_layout_revisions).values(**_workspace_layout_values(parsed))
                    )
            except IntegrityError as exc:
                raise WorkspaceConflictError("WORKSPACE_LAYOUT_IMMUTABLE_CONFLICT") from exc
            return _workspace_layout_record(_workspace_layout_values(parsed))

        return self._with_connection(run)

    def get_layout_revision(
        self,
        workspace_id: str,
        revision: int,
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            workspace = self._workspace_row(connection, workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            row = connection.execute(
                select(workspace_layout_revisions).where(
                    and_(
                        workspace_layout_revisions.c.workspace_id == workspace_id,
                        workspace_layout_revisions.c.revision == revision,
                    )
                )
            ).mappings().first()
            if row is None:
                raise WorkspaceNotFoundError("WORKSPACE_LAYOUT_REVISION_NOT_FOUND")
            return _workspace_layout_record(_row_to_json_dict(row))

        return self._with_connection(run)

    def get_current_layout(self, workspace_id: str, *, project_id: str | None = None) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            workspace = self._workspace_row(connection, workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            row = connection.execute(
                select(workspace_layout_revisions).where(
                    and_(
                        workspace_layout_revisions.c.workspace_id == workspace_id,
                        workspace_layout_revisions.c.revision == workspace["revision"],
                    )
                )
            ).mappings().first()
            return None if row is None else _workspace_layout_record(_row_to_json_dict(row))

        return self._with_connection(run)

    def list_layout_revisions(
        self,
        workspace_id: str,
        *,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        def run(connection: Connection) -> list[dict[str, Any]]:
            workspace = self._workspace_row(connection, workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            rows = connection.execute(
                select(workspace_layout_revisions)
                .where(workspace_layout_revisions.c.workspace_id == workspace_id)
                .order_by(workspace_layout_revisions.c.revision)
            ).mappings().all()
            return [_workspace_layout_record(_row_to_json_dict(row)) for row in rows]

        return self._with_connection(run)

    def update_workspace(
        self,
        workspace_id: str,
        *,
        expected_revision: int,
        project_id: str | None = None,
        title: str | object = _WORKSPACE_UNSET,
        active_panel_id: str | None | object = _WORKSPACE_UNSET,
        pinned_selection: WorkspaceSelectionContext | Mapping[str, Any] | None | object = _WORKSPACE_UNSET,
        layout: WorkspaceLayoutState | Mapping[str, Any] | None = None,
        layout_revision: WorkspaceLayoutRevision | Mapping[str, Any] | None = None,
        created_by: str | None = None,
    ) -> dict[str, Any]:
        def run(connection: Connection) -> bool:
            workspace = self._workspace_row(connection, workspace_id, for_update=True)
            _enforce_workspace_project(workspace["project_id"], project_id)
            if int(workspace["revision"]) != expected_revision:
                raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
            current_layout_row = connection.execute(
                select(workspace_layout_revisions).where(
                    and_(
                        workspace_layout_revisions.c.workspace_id == workspace_id,
                        workspace_layout_revisions.c.revision == expected_revision,
                    )
                )
            ).mappings().first()
            panel_rows = connection.execute(
                select(workspace_panels)
                .where(workspace_panels.c.workspace_id == workspace_id)
                .order_by(workspace_panels.c.ordinal, workspace_panels.c.panel_id)
            ).mappings().all()
            current_record = _workspace_record(
                workspace,
                [_row_to_json_dict(row) for row in panel_rows],
                None if current_layout_row is None else _row_to_json_dict(current_layout_row),
            )
            next_revision, next_title = _prepare_workspace_update(
                workspace_record=current_record,
                current_layout=None if current_layout_row is None else _workspace_layout_record(current_layout_row),
                panel_records=[_workspace_panel_record(row) for row in panel_rows],
                expected_revision=expected_revision,
                title=title,
                active_panel_id=active_panel_id,
                pinned_selection=pinned_selection,
                layout=layout,
                layout_revision=layout_revision,
                created_by=created_by,
            )
            if next_revision is None:
                return False
            self._validate_new_layout(connection, workspace, next_revision, expected_revision)
            result = connection.execute(
                update(scientific_workspaces)
                .where(
                    and_(
                        scientific_workspaces.c.workspace_id == workspace_id,
                        scientific_workspaces.c.revision == expected_revision,
                    )
                )
                .values(
                    title=next_title,
                    active_panel_id=next_revision.layout.activePanelId,
                    pinned_selection_json=(
                        None
                        if next_revision.selection is None
                        else next_revision.selection.model_dump(mode="json")
                    ),
                    revision=next_revision.revision,
                    updated_at=next_revision.createdAt,
                )
            )
            if result.rowcount != 1:
                raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
            try:
                with connection.begin_nested():
                    connection.execute(
                        insert(workspace_layout_revisions).values(**_workspace_layout_values(next_revision))
                    )
            except IntegrityError as exc:
                raise WorkspaceConflictError("WORKSPACE_LAYOUT_IMMUTABLE_CONFLICT") from exc
            return True

        self._with_connection(run)
        return self.get(workspace_id, project_id=project_id)

    update = update_workspace

    def _workspace_row(
        self,
        connection: Connection,
        workspace_id: str,
        *,
        for_update: bool = False,
    ) -> dict[str, Any]:
        statement = select(scientific_workspaces).where(
            scientific_workspaces.c.workspace_id == workspace_id
        )
        if for_update:
            statement = statement.with_for_update()
        row = connection.execute(statement).mappings().first()
        if row is None:
            raise WorkspaceNotFoundError()
        return _row_to_json_dict(row)

    def _aggregate_record(self, connection: Connection, workspace: Mapping[str, Any]) -> dict[str, Any]:
        panel_rows = connection.execute(
            select(workspace_panels)
            .where(workspace_panels.c.workspace_id == workspace["workspace_id"])
            .order_by(workspace_panels.c.ordinal, workspace_panels.c.panel_id)
        ).mappings().all()
        layout_row = connection.execute(
            select(workspace_layout_revisions).where(
                and_(
                    workspace_layout_revisions.c.workspace_id == workspace["workspace_id"],
                    workspace_layout_revisions.c.revision == workspace["revision"],
                )
            )
        ).mappings().first()
        return _workspace_record(
            workspace,
            [_row_to_json_dict(row) for row in panel_rows],
            None if layout_row is None else _row_to_json_dict(layout_row),
        )

    def _validate_new_layout(
        self,
        connection: Connection,
        workspace: Mapping[str, Any],
        revision: WorkspaceLayoutRevision,
        expected_revision: int,
    ) -> None:
        if int(workspace["revision"]) != expected_revision:
            raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
        count = int(connection.execute(
            select(func.count()).select_from(workspace_layout_revisions).where(
                workspace_layout_revisions.c.workspace_id == revision.workspaceId
            )
        ).scalar_one())
        if count >= WORKSPACE_MAX_LAYOUT_REVISIONS:
            raise WorkspaceCapacityError("REVISION_CAP_EXCEEDED")
        initial = count == 0 and revision.revision == int(workspace["revision"]) == expected_revision
        if not initial and revision.revision != expected_revision + 1:
            raise WorkspaceConflictError("WORKSPACE_LAYOUT_REVISION_SEQUENCE_INVALID")
        panel_ids = set(connection.execute(
            select(workspace_panels.c.panel_id).where(workspace_panels.c.workspace_id == revision.workspaceId)
        ).scalars().all())
        _validate_layout_panel_membership(revision.layout, panel_ids)

    def _assert_create_compatible(
        self,
        connection: Connection,
        existing: Mapping[str, Any],
        requested: ScientificWorkspace,
        panels: tuple[WorkspacePanel, ...],
        layout: WorkspaceLayoutRevision | None,
    ) -> None:
        normalized = _row_to_json_dict(existing)
        if _workspace_source_identity(normalized) != _workspace_source_identity(_workspace_values(requested)):
            raise WorkspaceConflictError("WORKSPACE_SEMANTIC_CONFLICT")
        for panel in panels:
            row = connection.execute(
                select(workspace_panels.c.panel_state_hash).where(
                    and_(
                        workspace_panels.c.workspace_id == requested.workspaceId,
                        workspace_panels.c.panel_id == panel.panelId,
                    )
                )
            ).scalar_one_or_none()
            if row != panel.panelStateHash:
                raise WorkspaceConflictError("WORKSPACE_SEMANTIC_CONFLICT")
        if layout is not None:
            semantic_hash = connection.execute(
                select(workspace_layout_revisions.c.semantic_hash).where(
                    and_(
                        workspace_layout_revisions.c.workspace_id == requested.workspaceId,
                        workspace_layout_revisions.c.revision == layout.revision,
                    )
                )
            ).scalar_one_or_none()
            if semantic_hash != layout.semanticHash:
                raise WorkspaceConflictError("WORKSPACE_SEMANTIC_CONFLICT")


def _parse_workspace(value: ScientificWorkspace | Mapping[str, Any]) -> ScientificWorkspace:
    return ScientificWorkspace.model_validate(
        value.model_dump(mode="json") if isinstance(value, ScientificWorkspace) else value
    )


def _parse_workspace_panel(value: WorkspacePanel | Mapping[str, Any]) -> WorkspacePanel:
    return WorkspacePanel.model_validate(
        value.model_dump(mode="json") if isinstance(value, WorkspacePanel) else value
    )


def _parse_workspace_layout_revision(
    value: WorkspaceLayoutRevision | Mapping[str, Any],
) -> WorkspaceLayoutRevision:
    return WorkspaceLayoutRevision.model_validate(
        value.model_dump(mode="json") if isinstance(value, WorkspaceLayoutRevision) else value
    )


def _parse_workspace_layout(value: WorkspaceLayoutState | Mapping[str, Any]) -> WorkspaceLayoutState:
    return WorkspaceLayoutState.model_validate(
        value.model_dump(mode="json") if isinstance(value, WorkspaceLayoutState) else value
    )


def _parse_workspace_selection(
    value: WorkspaceSelectionContext | Mapping[str, Any] | None,
) -> WorkspaceSelectionContext | None:
    if value is None:
        return None
    return WorkspaceSelectionContext.model_validate(
        value.model_dump(mode="json") if isinstance(value, WorkspaceSelectionContext) else value
    )


def _workspace_values(workspace: ScientificWorkspace) -> dict[str, Any]:
    return {
        "workspace_id": workspace.workspaceId,
        "schema_version": workspace.schemaVersion,
        "project_id": workspace.projectId,
        "source_job_id": workspace.sourceJobId,
        "source_reference_hash": workspace.sourceReferenceHash,
        "dataset_id": workspace.datasetId,
        "dataset_version": workspace.datasetVersion,
        "profile_id": workspace.profileId,
        "profile_semantic_hash": workspace.profileSemanticHash,
        "intent_id": workspace.intentId,
        "intent_semantic_hash": workspace.intentSemanticHash,
        "plan_id": workspace.planId,
        "plan_hash": workspace.planHash,
        "plan_schema_version": workspace.planSchemaVersion,
        "title": workspace.title,
        "active_panel_id": workspace.activePanelId,
        "pinned_selection_json": (
            None if workspace.pinnedSelection is None else workspace.pinnedSelection.model_dump(mode="json")
        ),
        "revision": workspace.revision,
        "created_by": workspace.createdBy,
        "created_at": workspace.createdAt,
        "updated_at": workspace.updatedAt,
    }


def _workspace_panel_values(panel: WorkspacePanel) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    descriptor = {
        "schemaVersion": panel.schemaVersion,
        "sourceRefs": [ref.model_dump(mode="json") for ref in panel.sourceRefs],
        "sourceReferenceHash": panel.sourceReferenceHash,
        "state": panel.state.value,
        "emittedSelectionKinds": [kind.value for kind in panel.emittedSelectionKinds],
        "evidenceRefs": list(panel.evidenceRefs),
        "provenanceRefs": list(panel.provenanceRefs),
        "capabilityRequirement": panel.capabilityRequirement,
        "mobilePresentationMode": panel.mobilePresentationMode,
        "accessibleName": panel.accessibleName,
        "unsupportedReason": panel.unsupportedReason,
        "contractProvenance": panel.contractProvenance,
    }
    return {
        "workspace_id": panel.workspaceId,
        "panel_id": panel.panelId,
        "panel_kind": panel.panelKind.value,
        "title": panel.title,
        "ordinal": panel.ordinal,
        "visible": panel.visible,
        "source_refs_json": descriptor,
        "renderer_contract": panel.rendererContract,
        "accepted_selection_kinds_json": [kind.value for kind in panel.acceptedSelectionKinds],
        "layout_json": panel.layout.model_dump(mode="json"),
        "panel_state_hash": panel.panelStateHash,
        "created_at": now,
        "updated_at": now,
    }


def _workspace_layout_values(revision: WorkspaceLayoutRevision) -> dict[str, Any]:
    return {
        "workspace_id": revision.workspaceId,
        "revision": revision.revision,
        "layout_json": revision.layout.model_dump(mode="json"),
        "selection_json": None if revision.selection is None else revision.selection.model_dump(mode="json"),
        "semantic_hash": revision.semanticHash,
        "created_by": revision.createdBy,
        "created_at": revision.createdAt,
    }


def _workspace_source_identity(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return tuple(
        row.get(field)
        for field in (
            "workspace_id",
            "schema_version",
            "project_id",
            "source_job_id",
            "source_reference_hash",
            "dataset_id",
            "dataset_version",
            "profile_id",
            "profile_semantic_hash",
            "intent_id",
            "intent_semantic_hash",
            "plan_id",
            "plan_hash",
            "plan_schema_version",
        )
    )


def _workspace_record(
    workspace: Mapping[str, Any],
    panel_rows: list[Mapping[str, Any]],
    layout_row: Mapping[str, Any] | None,
) -> dict[str, Any]:
    ordered_panels = sorted(panel_rows, key=lambda row: (int(row["ordinal"]), str(row["panel_id"])))
    layout = None if layout_row is None else _workspace_layout_record(layout_row)
    record = {
        "schemaVersion": workspace["schema_version"],
        "workspaceId": workspace["workspace_id"],
        "projectId": workspace["project_id"],
        "sourceJobId": workspace["source_job_id"],
        "sourceReferenceHash": workspace["source_reference_hash"],
        "datasetId": workspace.get("dataset_id"),
        "datasetVersion": workspace.get("dataset_version"),
        "profileId": workspace.get("profile_id"),
        "profileSemanticHash": workspace.get("profile_semantic_hash"),
        "intentId": workspace.get("intent_id"),
        "intentSemanticHash": workspace.get("intent_semantic_hash"),
        "planId": workspace.get("plan_id"),
        "planHash": workspace.get("plan_hash"),
        "planSchemaVersion": workspace.get("plan_schema_version"),
        "title": workspace["title"],
        "activePanelId": workspace.get("active_panel_id"),
        "pinnedSelection": _json_copy(workspace.get("pinned_selection_json")),
        "durableMetadata": {} if layout is None else _json_copy(layout["layout"]["durableMetadata"]),
        "panelIds": [row["panel_id"] for row in ordered_panels],
        "currentLayoutRevision": int(workspace["revision"]),
        "revision": int(workspace["revision"]),
        "projectedStatus": WorkspaceStatus.INITIALIZING.value,
        "historicalProjection": False,
        "readOnly": False,
        "warnings": [],
        "diagnostics": [],
        "artifactCount": 0,
        "toolCallCount": 0,
        "interpretationCount": 0,
        "reportCount": 0,
        "recipeCount": 0,
        "createdByKind": "USER",
        "createdBy": workspace["created_by"],
        "createdAt": _iso(workspace["created_at"]),
        "updatedAt": _iso(workspace["updated_at"]),
        "executionAuthorized": False,
        "scientificAuthority": False,
    }
    return ScientificWorkspace.model_validate(record).model_dump(mode="json")


def _workspace_panel_record(row: Mapping[str, Any]) -> dict[str, Any]:
    descriptor = _json_copy(row["source_refs_json"])
    if not isinstance(descriptor, Mapping) or "sourceRefs" not in descriptor:
        raise WorkspaceRepositoryError("WORKSPACE_PANEL_DESCRIPTOR_INCOMPLETE")
    record = {
        "schemaVersion": descriptor.get("schemaVersion", "1.0"),
        "workspaceId": row["workspace_id"],
        "panelId": row["panel_id"],
        "panelKind": row["panel_kind"],
        "title": row["title"],
        "ordinal": int(row["ordinal"]),
        "visible": bool(row["visible"]),
        "sourceRefs": descriptor["sourceRefs"],
        "sourceReferenceHash": descriptor.get("sourceReferenceHash"),
        "rendererContract": row["renderer_contract"],
        "state": descriptor.get("state"),
        "acceptedSelectionKinds": _json_copy(row["accepted_selection_kinds_json"]),
        "emittedSelectionKinds": descriptor.get("emittedSelectionKinds", []),
        "evidenceRefs": descriptor.get("evidenceRefs", []),
        "provenanceRefs": descriptor.get("provenanceRefs", []),
        "capabilityRequirement": descriptor.get("capabilityRequirement"),
        "layout": _json_copy(row["layout_json"]),
        "mobilePresentationMode": descriptor.get("mobilePresentationMode", "STACKED"),
        "accessibleName": descriptor.get("accessibleName"),
        "unsupportedReason": descriptor.get("unsupportedReason"),
        "panelStateHash": row["panel_state_hash"],
        "contractProvenance": descriptor.get("contractProvenance", "workspace-projection/1.0"),
    }
    return WorkspacePanel.model_validate(record).model_dump(mode="json")


def _workspace_layout_record(row: Mapping[str, Any]) -> dict[str, Any]:
    record = {
        "schemaVersion": "1.0",
        "workspaceId": row["workspace_id"],
        "revision": int(row["revision"]),
        "layout": _json_copy(row["layout_json"]),
        "selection": _json_copy(row.get("selection_json")),
        "semanticHash": row["semantic_hash"],
        "createdBy": row["created_by"],
        "createdAt": _iso(row["created_at"]),
    }
    return WorkspaceLayoutRevision.model_validate(record).model_dump(mode="json")


def _validate_workspace_create_aggregate(
    workspace: ScientificWorkspace,
    panels: tuple[WorkspacePanel, ...],
    initial_layout: WorkspaceLayoutRevision | None,
) -> None:
    if len(panels) > WORKSPACE_MAX_PANELS:
        raise WorkspaceCapacityError("PANEL_CAP_EXCEEDED")
    if len({panel.panelId for panel in panels}) != len(panels):
        raise WorkspaceConflictError("WORKSPACE_PANEL_DUPLICATE")
    ordered_ids = tuple(panel.panelId for panel in sorted(panels, key=lambda panel: (panel.ordinal, panel.panelId)))
    if tuple(workspace.panelIds) != ordered_ids:
        raise WorkspaceConflictError("WORKSPACE_PANEL_MEMBERSHIP_MISMATCH")
    for panel in panels:
        if panel.workspaceId != workspace.workspaceId:
            raise WorkspaceScopeError("WORKSPACE_PANEL_SCOPE_MISMATCH")
        _validate_panel_project_scope(panel, workspace.projectId)
    if initial_layout is not None:
        if initial_layout.workspaceId != workspace.workspaceId:
            raise WorkspaceScopeError("WORKSPACE_LAYOUT_SCOPE_MISMATCH")
        if initial_layout.revision != workspace.revision:
            raise WorkspaceConflictError("WORKSPACE_LAYOUT_REVISION_MISMATCH")
        _validate_layout_panel_membership(initial_layout.layout, set(ordered_ids))
        if initial_layout.layout.activePanelId != workspace.activePanelId:
            raise WorkspaceConflictError("WORKSPACE_ACTIVE_PANEL_MISMATCH")
        expected_selection = (
            None if workspace.pinnedSelection is None else workspace.pinnedSelection.model_dump(mode="json")
        )
        actual_selection = (
            None if initial_layout.selection is None else initial_layout.selection.model_dump(mode="json")
        )
        if expected_selection != actual_selection:
            raise WorkspaceConflictError("WORKSPACE_PINNED_SELECTION_MISMATCH")


def _validate_panel_project_scope(panel: WorkspacePanel, project_id: str) -> None:
    if any(ref.projectId != project_id for ref in panel.sourceRefs):
        raise WorkspaceScopeError("WORKSPACE_PANEL_PROJECT_SCOPE_MISMATCH")


def _validate_layout_panel_membership(layout: WorkspaceLayoutState, panel_ids: set[str]) -> None:
    referenced = set(layout.panelOrder) | set(layout.visiblePanelIds)
    if layout.activePanelId is not None:
        referenced.add(layout.activePanelId)
    if not referenced.issubset(panel_ids):
        raise WorkspaceScopeError("WORKSPACE_LAYOUT_UNKNOWN_PANEL")


def _enforce_workspace_project(actual_project_id: str, requested_project_id: str | None) -> None:
    if requested_project_id is not None and actual_project_id != requested_project_id:
        raise WorkspaceScopeError("WORKSPACE_PROJECT_SCOPE_MISMATCH")


def _prepare_workspace_update(
    *,
    workspace_record: Mapping[str, Any],
    current_layout: Mapping[str, Any] | None,
    panel_records: list[Mapping[str, Any]],
    expected_revision: int,
    title: str | object,
    active_panel_id: str | None | object,
    pinned_selection: WorkspaceSelectionContext | Mapping[str, Any] | None | object,
    layout: WorkspaceLayoutState | Mapping[str, Any] | None,
    layout_revision: WorkspaceLayoutRevision | Mapping[str, Any] | None,
    created_by: str | None,
) -> tuple[WorkspaceLayoutRevision | None, str]:
    current = ScientificWorkspace.model_validate(workspace_record)
    next_title = current.title if title is _WORKSPACE_UNSET else str(title)
    ScientificWorkspace.model_validate({**current.model_dump(mode="json"), "title": next_title})
    next_selection = (
        current.pinnedSelection
        if pinned_selection is _WORKSPACE_UNSET
        else _parse_workspace_selection(pinned_selection)  # type: ignore[arg-type]
    )
    if next_selection is not None:
        refs = (() if next_selection.primary is None else (next_selection.primary,)) + next_selection.secondary
        if any(ref.projectId != current.projectId for ref in refs):
            raise WorkspaceScopeError("WORKSPACE_SELECTION_PROJECT_SCOPE_MISMATCH")

    parsed_current_revision = (
        None if current_layout is None else _parse_workspace_layout_revision(current_layout)
    )
    if layout_revision is not None:
        supplied = _parse_workspace_layout_revision(layout_revision)
        if supplied.workspaceId != current.workspaceId:
            raise WorkspaceScopeError("WORKSPACE_LAYOUT_SCOPE_MISMATCH")
        if supplied.revision != expected_revision + 1:
            raise WorkspaceConflictError("WORKSPACE_LAYOUT_REVISION_SEQUENCE_INVALID")
        if created_by is not None and supplied.createdBy != created_by:
            raise WorkspaceConflictError("WORKSPACE_LAYOUT_PROVENANCE_MISMATCH")
        next_layout = supplied.layout
        if layout is not None and _parse_workspace_layout(layout) != next_layout:
            raise WorkspaceConflictError("WORKSPACE_LAYOUT_CONFLICT")
        supplied_selection = supplied.selection
        if pinned_selection is not _WORKSPACE_UNSET and supplied_selection != next_selection:
            raise WorkspaceConflictError("WORKSPACE_PINNED_SELECTION_MISMATCH")
        next_selection = supplied_selection
    elif layout is not None:
        supplied = None
        next_layout = _parse_workspace_layout(layout)
    elif parsed_current_revision is not None:
        supplied = None
        next_layout = parsed_current_revision.layout
    else:
        supplied = None
        ordered = sorted(panel_records, key=lambda panel: (int(panel["ordinal"]), str(panel["panelId"])))
        next_layout = WorkspaceLayoutState.model_validate({
            "activePanelId": current.activePanelId,
            "panelOrder": [panel["panelId"] for panel in ordered],
            "visiblePanelIds": [panel["panelId"] for panel in ordered if panel["visible"]],
            "panelLayouts": [
                {"panelId": panel["panelId"], **panel["layout"]}
                for panel in ordered
            ],
            "durableMetadata": current.durableMetadata.model_dump(mode="json"),
        })

    resolved_active = next_layout.activePanelId if active_panel_id is _WORKSPACE_UNSET else active_panel_id
    if resolved_active is not None and not isinstance(resolved_active, str):
        raise WorkspaceRepositoryError("WORKSPACE_ACTIVE_PANEL_INVALID")
    if next_layout.activePanelId != resolved_active:
        next_layout = WorkspaceLayoutState.model_validate({
            **next_layout.model_dump(mode="json"),
            "activePanelId": resolved_active,
        })
    panel_ids = {str(panel["panelId"]) for panel in panel_records}
    _validate_layout_panel_membership(next_layout, panel_ids)

    current_selection = None if current.pinnedSelection is None else current.pinnedSelection.model_dump(mode="json")
    next_selection_json = None if next_selection is None else next_selection.model_dump(mode="json")
    current_layout_value = None if parsed_current_revision is None else parsed_current_revision.layout
    no_change = (
        supplied is None
        and next_title == current.title
        and resolved_active == current.activePanelId
        and next_selection_json == current_selection
        and next_layout == current_layout_value
    )
    if no_change:
        return None, next_title
    if supplied is not None:
        if supplied.layout.activePanelId != resolved_active:
            raise WorkspaceConflictError("WORKSPACE_ACTIVE_PANEL_MISMATCH")
        return supplied, next_title
    revision = make_layout_revision(
        workspace_id=current.workspaceId,
        revision=expected_revision + 1,
        layout=next_layout,
        selection=next_selection,
        created_by=created_by or current.createdBy,
        created_at=datetime.now(timezone.utc),
    )
    return revision, next_title


def _validate_interpretation_run_association(
    bundle: ScientificEvidenceBundle,
    execution: InterpretationExecutionRecord,
) -> None:
    expected = (
        execution.sourceBundleId == bundle.bundleId,
        execution.sourceBundleHash == bundle.bundleHash,
        execution.sourceJobId == bundle.jobId,
        execution.sourcePlanId == bundle.planId,
        execution.sourcePlanHash == bundle.planHash,
        execution.sourceGraphHash == bundle.graphHash,
        execution.evidenceItemCount == len(bundle.evidenceItems),
        execution.warningCount == len(bundle.bundleWarnings),
        execution.limitationCount == len(bundle.bundleLimitations),
    )
    if not all(expected):
        raise ValueError("Interpretation execution record does not match its evidence bundle")


class _KeyedLockRegistry:
    def __init__(self) -> None:
        self._guard = Lock()
        self._entries: dict[tuple[str, ...], tuple[Lock, int]] = {}

    @contextmanager
    def guard(self, key: tuple[str, ...]) -> Iterator[None]:
        with self._guard:
            lock, users = self._entries.get(key, (Lock(), 0))
            self._entries[key] = (lock, users + 1)
        lock.acquire()
        try:
            yield
        finally:
            lock.release()
            with self._guard:
                current_lock, current_users = self._entries[key]
                if current_users == 1:
                    del self._entries[key]
                else:
                    self._entries[key] = (current_lock, current_users - 1)


_SQL_INTERPRETATION_LOCKS = _KeyedLockRegistry()


def _validate_interpretation_associations(
    bundle: ScientificEvidenceBundle,
    interpretation: GroundedScientificInterpretation,
    execution: InterpretationExecutionRecord,
) -> None:
    _validate_interpretation_run_association(bundle, execution)
    expected = (
        interpretation.sourceBundleId == bundle.bundleId,
        interpretation.sourceBundleHash == bundle.bundleHash,
        interpretation.sourceJobId == bundle.jobId,
        interpretation.sourcePlanId == bundle.planId,
        interpretation.sourcePlanHash == bundle.planHash,
        interpretation.sourceGraphHash == bundle.graphHash,
        interpretation.executionRecordId == execution.executionRecordId,
        interpretation.mode == execution.mode,
        interpretation.provider == execution.provider,
        interpretation.providerVersion == execution.providerVersion,
        interpretation.repairCount == execution.repairCount,
        interpretation.outcome == execution.outcome,
        execution.claimCount == len(interpretation.claims),
    )
    if not all(expected):
        raise ValueError("Interpretation, execution, and evidence identities are inconsistent")
    evidence_ids = {item.evidenceItemId for item in bundle.evidenceItems}
    for claim in interpretation.claims:
        refs = set(
            claim.subjectEvidenceIds
            + claim.supportingEvidenceIds
            + claim.limitingEvidenceIds
            + claim.contradictingEvidenceIds
        )
        if not refs.issubset(evidence_ids):
            raise ValueError("Interpretation claim references evidence outside its bundle")


def _ensure_actor_and_org(connection: Connection, *, user_id: str, organization_id: str) -> None:
    _ensure_user(connection, user_id=user_id)
    exists = connection.execute(select(organizations.c.id).where(organizations.c.id == organization_id)).first()
    if exists is None:
        connection.execute(insert(organizations).values(id=organization_id, name=organization_id))


def _ensure_user(connection: Connection, *, user_id: str) -> None:
    exists = connection.execute(select(users.c.id).where(users.c.id == user_id)).first()
    if exists is None:
        connection.execute(insert(users).values(id=user_id, email=f"{user_id}@local.invalid", display_name=user_id))


def _job_event_values(event: JobEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "job_id": event.jobId,
        "seq": event.seq,
        "event_type": event.eventType,
        "status": event.status.value,
        "message": event.message,
        "progress": event.progress,
        "payload_json": event.payload or {},
        "created_at": _parse_iso(event.createdAt),
    }


def _job_event_from_row(row: Mapping[str, Any]) -> JobEvent:
    return JobEvent(
        id=str(row["id"]),
        jobId=str(row["job_id"]),
        seq=int(row["seq"]),
        eventType=str(row["event_type"]),
        status=JobEventStatus(str(row["status"])),
        message=str(row["message"]),
        progress=row.get("progress"),
        payload=_json_copy(row.get("payload_json") or {}),
        createdAt=_iso(row["created_at"]),
    )


def _project_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "projectId": row["id"],
        "organizationId": row["organization_id"],
        "name": row["name"],
        "description": row["description"],
        "createdBy": row["created_by"],
        "createdAt": _iso(row["created_at"]),
        "updatedAt": _iso(row["updated_at"]),
    }


def _dataset_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "datasetId": row["id"],
        "projectId": row["project_id"],
        "name": row["name"],
        "status": row["status"],
        "metadata": _json_copy(row.get("metadata_json") or {}),
        "createdBy": row["created_by"],
        "createdAt": _iso(row["created_at"]),
        "updatedAt": _iso(row["updated_at"]),
    }


def _data_profile_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    profile = _json_copy(row.get("profile_json") or {})
    profile.setdefault("id", row["id"])
    profile.setdefault("profileId", row["id"])
    profile.setdefault("datasetId", row["dataset_id"])
    profile.setdefault("version", row["version"])
    profile["createdAt"] = profile.get("createdAt") or _iso(row["created_at"])
    return profile


def canonical_analysis_plan_json(plan: AnalysisPlan | AnalysisPlanV02 | Mapping[str, Any]) -> str:
    if isinstance(plan, AnalysisPlanV02):
        return canonical_dependency_json(plan)
    if isinstance(plan, AnalysisPlan):
        return json.dumps(plan.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if str(plan.get("schemaVersion") or "") == "0.2":
        return canonical_dependency_json(AnalysisPlanV02.model_validate(plan))
    parsed = AnalysisPlan.model_validate(plan)
    return json.dumps(parsed.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compute_plan_hash(plan: AnalysisPlan | AnalysisPlanV02 | Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_analysis_plan_json(plan).encode("utf-8")).hexdigest()


def _normalize_analysis_intent_record(record: Mapping[str, Any]) -> dict[str, Any]:
    source = _json_copy(record)
    intent_json = source.get("analysisIntent") or source.get("intentJson") or source.get("intent_json")
    if intent_json is None:
        raise ValueError("AnalysisIntent record is missing intent_json")
    parsed = AnalysisIntent.model_validate(intent_json)
    computed_hash = compute_analysis_intent_hash(parsed)
    if parsed.intentHash != computed_hash or parsed.intentId != deterministic_intent_id(computed_hash):
        raise ValueError("AnalysisIntent identity does not match canonical JSON")
    intent_id = str(source.get("id") or source.get("intentId") or parsed.intentId)
    if intent_id != parsed.intentId:
        raise ValueError("AnalysisIntent record id does not match contract identity")
    provided_hash = source.get("intentHash") or source.get("intent_hash")
    if provided_hash and str(provided_hash) != parsed.intentHash:
        raise ValueError("AnalysisIntent record hash does not match contract identity")
    payload = parsed.model_dump(mode="json")
    return {
        "id": intent_id,
        "intentId": intent_id,
        "projectId": str(source.get("projectId") or source.get("project_id") or ""),
        "datasetId": parsed.datasetId,
        "profileId": parsed.profileId,
        "schemaVersion": parsed.schemaVersion,
        "intentHash": parsed.intentHash,
        "outcome": parsed.outcome.value,
        "parentIntentId": parsed.provenance.parentIntentId,
        "clarificationRound": parsed.clarification.round,
        "provider": parsed.provenance.provider,
        "model": parsed.provenance.model,
        "promptVersion": parsed.provenance.promptVersion,
        "analysisIntent": payload,
        "intentJson": payload,
        "createdBy": str(source.get("createdBy") or source.get("created_by") or "user_local"),
        "createdAt": source.get("createdAt") or source.get("created_at") or parsed.provenance.createdAt,
    }


def _analysis_intent_values(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized = _normalize_analysis_intent_record(record)
    if not normalized["projectId"]:
        raise ValueError("AnalysisIntent record is missing projectId")
    return {
        "id": normalized["intentId"],
        "project_id": normalized["projectId"],
        "dataset_id": normalized["datasetId"],
        "profile_id": normalized["profileId"],
        "schema_version": normalized["schemaVersion"],
        "intent_hash": normalized["intentHash"],
        "outcome": normalized["outcome"],
        "parent_intent_id": normalized["parentIntentId"],
        "clarification_round": normalized["clarificationRound"],
        "provider": normalized["provider"],
        "model": normalized["model"],
        "prompt_version": normalized["promptVersion"],
        "intent_json": _json_copy(normalized["analysisIntent"]),
        "created_by": normalized["createdBy"],
    }


def _analysis_intent_from_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return _json_copy(_normalize_analysis_intent_record(record))


def _analysis_intent_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return _analysis_intent_from_record(
        {
            "id": row["id"],
            "projectId": row["project_id"],
            "analysisIntent": _json_copy(row.get("intent_json") or {}),
            "createdBy": row["created_by"],
            "createdAt": _iso(row["created_at"]),
        }
    )


def _intent_execution_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "intentId": row["intent_id"],
        "planId": row["plan_id"],
        "jobId": row["job_id"],
        "createdAt": _iso(row["created_at"]),
    }


def _normalize_capability_resolution_record(record: Mapping[str, Any]) -> dict[str, Any]:
    source = _json_copy(record)
    payload = source.get("eligibilityResolution") or source.get("resolutionJson") or source.get("resolution_json")
    if payload is None:
        raise ValueError("Eligibility Resolution record is missing resolution_json")
    parsed = EligibilityResolution.model_validate(payload)
    computed_hash = capability_semantic_hash(parsed, identity_fields=("resolutionId", "resolutionHash"))
    if parsed.resolutionHash != computed_hash or parsed.resolutionId != deterministic_capability_id("resolution", computed_hash):
        raise ValueError("Eligibility Resolution identity does not match canonical JSON")
    return {
        "id": parsed.resolutionId,
        "resolutionId": parsed.resolutionId,
        "resolutionHash": parsed.resolutionHash,
        "intentId": parsed.intentId,
        "profileId": parsed.profileId,
        "profileSemanticHash": parsed.profileSemanticHash,
        "registrySnapshotId": parsed.registrySnapshotId,
        "registrySnapshotHash": parsed.registrySnapshotHash,
        "resolverVersion": parsed.provenance.resolverVersion,
        "eligibilityResolution": parsed.model_dump(mode="json"),
        "createdBy": str(source.get("createdBy") or source.get("created_by") or "user_local"),
        "createdAt": source.get("createdAt") or source.get("created_at"),
    }


def _capability_resolution_values(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized = _normalize_capability_resolution_record(record)
    return {
        "id": normalized["resolutionId"],
        "resolution_hash": normalized["resolutionHash"],
        "intent_id": normalized["intentId"],
        "profile_id": normalized["profileId"],
        "profile_semantic_hash": normalized["profileSemanticHash"],
        "registry_snapshot_id": normalized["registrySnapshotId"],
        "registry_snapshot_hash": normalized["registrySnapshotHash"],
        "resolver_version": normalized["resolverVersion"],
        "resolution_json": _json_copy(normalized["eligibilityResolution"]),
        "created_by": normalized["createdBy"],
    }


def _capability_resolution_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    record = _normalize_capability_resolution_record(
        {
            "eligibilityResolution": _json_copy(row.get("resolution_json") or {}),
            "createdBy": row["created_by"],
            "createdAt": _iso(row["created_at"]),
        }
    )
    record["createdAt"] = _iso(row["created_at"])
    return record


def _normalize_capability_decision_record(record: Mapping[str, Any]) -> dict[str, Any]:
    source = _json_copy(record)
    payload = source.get("capabilityDecision") or source.get("decisionJson") or source.get("decision_json")
    if payload is None:
        raise ValueError("Capability Planning Decision record is missing decision_json")
    parsed = CapabilityPlanningDecision.model_validate(payload)
    computed_hash = capability_semantic_hash(parsed, identity_fields=("decisionId", "decisionHash"))
    if parsed.decisionHash != computed_hash or parsed.decisionId != deterministic_capability_id("decision", computed_hash):
        raise ValueError("Capability Planning Decision identity does not match canonical JSON")
    return {
        "id": parsed.decisionId,
        "decisionId": parsed.decisionId,
        "decisionHash": parsed.decisionHash,
        "intentId": parsed.intentId,
        "resolutionId": parsed.resolutionId,
        "outcome": parsed.outcome.value,
        "provider": parsed.provenance.provider,
        "providerContractVersion": parsed.provenance.providerContractVersion,
        "model": parsed.provenance.model,
        "repairCount": parsed.provenance.repairCount,
        "capabilityDecision": parsed.model_dump(mode="json"),
        "createdBy": str(source.get("createdBy") or source.get("created_by") or "user_local"),
        "createdAt": source.get("createdAt") or source.get("created_at"),
    }


def _capability_decision_values(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized = _normalize_capability_decision_record(record)
    return {
        "id": normalized["decisionId"],
        "decision_hash": normalized["decisionHash"],
        "intent_id": normalized["intentId"],
        "resolution_id": normalized["resolutionId"],
        "outcome": normalized["outcome"],
        "provider": normalized["provider"],
        "provider_contract_version": normalized["providerContractVersion"],
        "model": normalized["model"],
        "repair_count": normalized["repairCount"],
        "decision_json": _json_copy(normalized["capabilityDecision"]),
        "created_by": normalized["createdBy"],
    }


def _capability_decision_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    record = _normalize_capability_decision_record(
        {
            "capabilityDecision": _json_copy(row.get("decision_json") or {}),
            "createdBy": row["created_by"],
            "createdAt": _iso(row["created_at"]),
        }
    )
    record["createdAt"] = _iso(row["created_at"])
    return record


def _capability_execution_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "decisionId": row["decision_id"],
        "intentId": row["intent_id"],
        "planId": row["plan_id"],
        "jobId": row["job_id"],
        "createdAt": _iso(row["created_at"]),
    }


def _normalize_plan_bindings(
    plan_record: Mapping[str, Any],
    plan_id: str,
    plan_hash: str,
    graph_hash: str,
    bindings: list[DependencyBinding | Mapping[str, Any]],
) -> list[dict[str, Any]]:
    payload = plan_record.get("analysisPlan") or plan_record.get("analysisPlanJson") or {}
    plan = AnalysisPlanV02.model_validate(payload)
    if str(plan_record.get("planId") or plan_record.get("id")) != plan_id:
        raise ValueError("Planned dependency binding plan identity is invalid")
    if compute_analysis_plan_02_hash(plan) != plan_hash or str(plan_record.get("planHash")) != plan_hash:
        raise ValueError("Planned dependency binding plan hash is invalid")
    if plan.graphHash != graph_hash:
        raise ValueError("Planned dependency binding graph hash is invalid")
    parsed = [item if isinstance(item, DependencyBinding) else DependencyBinding.model_validate(item) for item in bindings]
    expected = sorted((item.model_dump(mode="json") for item in plan.dependencyBindings), key=lambda item: item["bindingId"])
    actual = sorted((item.model_dump(mode="json") for item in parsed), key=lambda item: item["bindingId"])
    if actual != expected:
        raise ValueError("Planned dependency bindings must exactly match AnalysisPlan 0.2")
    records: list[dict[str, Any]] = []
    for binding in actual:
        semantic = {
            "planId": plan_id,
            "planHash": plan_hash,
            "graphHash": graph_hash,
            "dependencyBinding": binding,
        }
        records.append(
            {
                **semantic,
                **binding,
                "semanticRecordHash": dependency_semantic_hash(semantic),
            }
        )
    return records


def _planned_binding_values(record: Mapping[str, Any]) -> dict[str, Any]:
    binding = DependencyBinding.model_validate(record["dependencyBinding"])
    return {
        "plan_id": record["planId"],
        "binding_id": binding.bindingId,
        "plan_hash": record["planHash"],
        "graph_hash": record["graphHash"],
        "producer_step_id": binding.producerStepId,
        "producer_output_port": binding.producerOutputPort,
        "consumer_step_id": binding.consumerStepId,
        "consumer_input_port": binding.consumerInputPort,
        "artifact_kind": binding.artifactKind.value,
        "artifact_contract_version": binding.artifactContractVersion,
        "media_type": binding.mediaType,
        "cardinality": binding.cardinality.value,
        "binding_json": binding.model_dump(mode="json"),
        "semantic_record_hash": record["semanticRecordHash"],
    }


def _planned_binding_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    binding = DependencyBinding.model_validate(_json_copy(row["binding_json"]))
    semantic = {
        "planId": row["plan_id"],
        "planHash": row["plan_hash"],
        "graphHash": row["graph_hash"],
        "dependencyBinding": binding.model_dump(mode="json"),
    }
    record = {
        **semantic,
        **binding.model_dump(mode="json"),
        "semanticRecordHash": row["semantic_record_hash"],
    }
    if record["semanticRecordHash"] != dependency_semantic_hash(semantic):
        raise ValueError("Persisted dependency binding record hash is invalid")
    return record


def _normalize_binding_resolution_record(record: Mapping[str, Any]) -> dict[str, Any]:
    source = _json_copy(record)
    resolved_payload = source.get("resolvedArtifactInputRef") or source.get("resolved_ref_json")
    resolved = ResolvedArtifactInputRef.model_validate(resolved_payload) if resolved_payload is not None else None

    def field(camel: str, snake: str, default: Any = None) -> Any:
        if source.get(camel) is not None:
            return source[camel]
        if source.get(snake) is not None:
            return source[snake]
        if resolved is not None and hasattr(resolved, camel):
            return getattr(resolved, camel)
        return default

    semantic = {
        "planId": str(field("planId", "plan_id") or ""),
        "planHash": str(field("planHash", "plan_hash") or ""),
        "jobId": str(field("jobId", "job_id") or ""),
        "bindingId": str(field("bindingId", "binding_id") or ""),
        "producerToolCallId": field("producerToolCallId", "producer_tool_call_id"),
        "producerStepId": str(field("producerStepId", "producer_step_id") or ""),
        "artifactId": field("artifactId", "artifact_id"),
        "artifactChecksum": field("artifactChecksum", "artifact_checksum", field("checksum", "checksum")),
        "artifactKind": _enum_value(field("artifactKind", "artifact_kind")) if field("artifactKind", "artifact_kind") else None,
        "artifactContractVersion": field("artifactContractVersion", "artifact_contract_version"),
        "mediaType": field("mediaType", "media_type"),
        "consumerToolCallId": field("consumerToolCallId", "consumer_tool_call_id"),
        "consumerStepId": str(field("consumerStepId", "consumer_step_id") or ""),
        "consumerInputPort": str(field("consumerInputPort", "consumer_input_port") or ""),
        "validationOutcome": str(field("validationOutcome", "validation_outcome") or ""),
        "errorCode": field("errorCode", "error_code"),
        "resolvedArtifactInputRef": resolved.model_dump(mode="json") if resolved is not None else None,
    }
    for required in ("planId", "planHash", "jobId", "bindingId", "producerStepId", "consumerStepId", "consumerInputPort", "validationOutcome"):
        if not semantic[required]:
            raise ValueError(f"Runtime artifact binding resolution is missing {required}")
    if len(semantic["planHash"]) != 64:
        raise ValueError("Runtime artifact binding resolution planHash is invalid")
    if resolved is not None:
        for key in ("planId", "planHash", "jobId", "bindingId", "producerStepId", "consumerStepId", "consumerInputPort"):
            if semantic[key] != getattr(resolved, key):
                raise ValueError("Resolved artifact input identity conflicts with binding resolution")
    computed_hash = dependency_semantic_hash(semantic)
    provided_hash = source.get("recordHash") or source.get("record_hash")
    if provided_hash and str(provided_hash) != computed_hash:
        raise ValueError("Runtime artifact binding resolution hash is invalid")
    record_id = str(source.get("id") or deterministic_dependency_id("binding_resolution", computed_hash))
    return {
        "id": record_id,
        "recordHash": computed_hash,
        **semantic,
        "resolvedAt": source.get("resolvedAt") or source.get("resolved_at") or _utc_now(),
    }


def _binding_resolution_values(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": record["id"],
        "record_hash": record["recordHash"],
        "plan_id": record["planId"],
        "plan_hash": record["planHash"],
        "job_id": record["jobId"],
        "binding_id": record["bindingId"],
        "producer_tool_call_id": record["producerToolCallId"],
        "producer_step_id": record["producerStepId"],
        "artifact_id": record["artifactId"],
        "artifact_checksum": record["artifactChecksum"],
        "artifact_kind": record["artifactKind"],
        "artifact_contract_version": record["artifactContractVersion"],
        "media_type": record["mediaType"],
        "consumer_tool_call_id": record["consumerToolCallId"],
        "consumer_step_id": record["consumerStepId"],
        "consumer_input_port": record["consumerInputPort"],
        "validation_outcome": record["validationOutcome"],
        "error_code": record["errorCode"],
        "resolved_ref_json": _json_copy(record["resolvedArtifactInputRef"]),
        "resolved_at": _parse_iso(str(record["resolvedAt"])),
    }


def _binding_resolution_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return _normalize_binding_resolution_record(
        {
            "id": row["id"],
            "recordHash": row["record_hash"],
            "planId": row["plan_id"],
            "planHash": row["plan_hash"],
            "jobId": row["job_id"],
            "bindingId": row["binding_id"],
            "producerToolCallId": row.get("producer_tool_call_id"),
            "producerStepId": row["producer_step_id"],
            "artifactId": row.get("artifact_id"),
            "artifactChecksum": row.get("artifact_checksum"),
            "artifactKind": row.get("artifact_kind"),
            "artifactContractVersion": row.get("artifact_contract_version"),
            "mediaType": row.get("media_type"),
            "consumerToolCallId": row.get("consumer_tool_call_id"),
            "consumerStepId": row["consumer_step_id"],
            "consumerInputPort": row["consumer_input_port"],
            "validationOutcome": row["validation_outcome"],
            "errorCode": row.get("error_code"),
            "resolvedArtifactInputRef": _json_copy(row.get("resolved_ref_json")),
            "resolvedAt": _iso(row["resolved_at"]),
        }
    )


def _normalize_dependency_execution_record(record: DependencyExecutionRecord | Mapping[str, Any]) -> dict[str, Any]:
    source = record.model_dump(mode="json") if isinstance(record, DependencyExecutionRecord) else _json_copy(record)
    payload = source.get("dependencyExecutionRecord") or source.get("recordJson") or source.get("record_json") or source
    parsed = DependencyExecutionRecord.model_validate(payload)
    semantic_hash = dependency_semantic_hash(
        parsed.model_dump(mode="json"), identity_fields=("executionId", "executionHash", "createdAt", "updatedAt")
    )
    expected_id = deterministic_dependency_id("execution", semantic_hash)
    if parsed.executionHash != semantic_hash or parsed.executionId != expected_id:
        raise ValueError("Dependency execution record identity is invalid")
    parsed_json = parsed.model_dump(mode="json")
    return {
        **parsed_json,
        "id": parsed.executionId,
        "executionId": parsed.executionId,
        "executionHash": parsed.executionHash,
        "planId": parsed.planId,
        "planHash": parsed.planHash,
        "jobId": parsed.jobId,
        "graphHash": parsed.graphHash,
        "outcome": parsed.outcome.value,
        "dependencyExecutionRecord": parsed_json,
        "createdAt": parsed.createdAt,
        "updatedAt": parsed.updatedAt,
    }


def _dependency_execution_values(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "execution_id": record["executionId"],
        "execution_hash": record["executionHash"],
        "plan_id": record["planId"],
        "plan_hash": record["planHash"],
        "job_id": record["jobId"],
        "graph_hash": record["graphHash"],
        "outcome": record["outcome"],
        "record_json": _json_copy(record["dependencyExecutionRecord"]),
        "created_at": _parse_iso(record["createdAt"]),
        "updated_at": _parse_iso(record["updatedAt"]),
    }


def _dependency_execution_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return _normalize_dependency_execution_record(_json_copy(row["record_json"]))


def _normalize_artifact_lineage_record(record: ArtifactLineageRecord | Mapping[str, Any]) -> dict[str, Any]:
    source = record.model_dump(mode="json") if isinstance(record, ArtifactLineageRecord) else _json_copy(record)
    payload = source.get("artifactLineageRecord") or source.get("recordJson") or source.get("record_json") or source
    parsed = ArtifactLineageRecord.model_validate(payload)
    semantic_hash = dependency_semantic_hash(
        parsed.model_dump(mode="json"), identity_fields=("lineageId", "lineageHash", "createdAt")
    )
    expected_id = deterministic_dependency_id("lineage", semantic_hash)
    if parsed.lineageHash != semantic_hash or parsed.lineageId != expected_id:
        raise ValueError("Artifact lineage record identity is invalid")
    parsed_json = parsed.model_dump(mode="json")
    return {
        **parsed_json,
        "id": parsed.lineageId,
        "lineageId": parsed.lineageId,
        "lineageHash": parsed.lineageHash,
        "artifactId": parsed.artifactId,
        "jobId": parsed.jobId,
        "planId": parsed.planId,
        "planHash": parsed.planHash,
        "graphHash": parsed.graphHash,
        "producerToolCallId": parsed.producerToolCallId,
        "producerStepId": parsed.producerStepId,
        "outputPort": parsed.outputPort,
        "artifactLineageRecord": parsed_json,
        "createdAt": parsed.createdAt,
    }


def _artifact_lineage_values(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "lineage_id": record["lineageId"],
        "lineage_hash": record["lineageHash"],
        "artifact_id": record["artifactId"],
        "job_id": record["jobId"],
        "plan_id": record["planId"],
        "plan_hash": record["planHash"],
        "graph_hash": record["graphHash"],
        "producer_tool_call_id": record["producerToolCallId"],
        "producer_step_id": record["producerStepId"],
        "output_port": record["outputPort"],
        "record_json": _json_copy(record["artifactLineageRecord"]),
        "created_at": _parse_iso(record["createdAt"]),
    }


def _artifact_lineage_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return _normalize_artifact_lineage_record(_json_copy(row["record_json"]))


def _normalize_analysis_plan_record(record: Mapping[str, Any]) -> dict[str, Any]:
    source = _json_copy(record)
    plan_json = (
        source.get("analysisPlan")
        or source.get("analysisPlanJson")
        or source.get("analysis_plan_json")
        or source.get("plan")
    )
    if plan_json is None:
        raise ValueError("AnalysisPlan record is missing analysis_plan_json")
    parsed_plan: AnalysisPlan | AnalysisPlanV02
    if str(plan_json.get("schemaVersion") or "") == "0.2":
        parsed_plan = AnalysisPlanV02.model_validate(plan_json)
    else:
        parsed_plan = AnalysisPlan.model_validate(plan_json)
    plan_payload = parsed_plan.model_dump(mode="json")
    _reject_credential_keys(plan_payload)
    computed_hash = compute_plan_hash(parsed_plan)
    provided_hash = source.get("planHash") or source.get("plan_hash")
    if provided_hash and str(provided_hash) != computed_hash:
        raise ValueError("AnalysisPlan planHash does not match canonical AnalysisPlan JSON")
    plan_hash = computed_hash
    plan_id = str(source.get("id") or source.get("planId") or source.get("plan_id") or f"plan_{plan_hash[:24]}")
    validation_status = str(source.get("validationStatus") or source.get("validation_status") or "validated")
    if validation_status != "validated":
        raise ValueError("Only validated AnalysisPlan records may be persisted")
    return {
        "id": plan_id,
        "planId": plan_id,
        "projectId": str(source.get("projectId") or source.get("project_id") or ""),
        "datasetId": source.get("datasetId") or source.get("dataset_id") or parsed_plan.datasetId,
        "profileId": source.get("profileId") or source.get("profile_id") or parsed_plan.profileId,
        "jobId": source.get("jobId") or source.get("job_id"),
        "planSource": str(source.get("planSource") or source.get("plan_source") or "llm"),
        "plannerProvider": source.get("plannerProvider") or source.get("planner_provider"),
        "analysisPlan": plan_payload,
        "analysisPlanJson": plan_payload,
        "analysis_plan_json": plan_payload,
        "planHash": plan_hash,
        "plan_hash": plan_hash,
        "validationStatus": validation_status,
        "createdBy": str(source.get("createdBy") or source.get("created_by") or "user_local"),
        "createdAt": source.get("createdAt") or source.get("created_at") or _utc_now(),
        "updatedAt": source.get("updatedAt") or source.get("updated_at") or _utc_now(),
    }


def _analysis_plan_values(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized = _normalize_analysis_plan_record(record)
    if not normalized["projectId"]:
        raise ValueError("AnalysisPlan record is missing projectId")
    return {
        "id": normalized["id"],
        "project_id": normalized["projectId"],
        "dataset_id": normalized.get("datasetId"),
        "profile_id": normalized.get("profileId"),
        "job_id": normalized.get("jobId"),
        "plan_source": normalized["planSource"],
        "planner_provider": normalized.get("plannerProvider"),
        "analysis_plan_json": _json_copy(normalized["analysisPlan"]),
        "plan_hash": normalized["planHash"],
        "validation_status": normalized["validationStatus"],
        "created_by": normalized["createdBy"],
    }


def _analysis_plan_from_record(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized = _normalize_analysis_plan_record(record)
    return _json_copy(normalized)


def _analysis_plan_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    plan_payload = _json_copy(row.get("analysis_plan_json") or {})
    return _analysis_plan_from_record(
        {
            "id": row["id"],
            "projectId": row["project_id"],
            "datasetId": row.get("dataset_id"),
            "profileId": row.get("profile_id"),
            "jobId": row.get("job_id"),
            "planSource": row["plan_source"],
            "plannerProvider": row.get("planner_provider"),
            "analysisPlan": plan_payload,
            "planHash": row["plan_hash"],
            "validationStatus": row["validation_status"],
            "createdBy": row["created_by"],
            "createdAt": _iso(row["created_at"]),
            "updatedAt": _iso(row["updated_at"]),
        }
    )


def _job_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "jobId": row["id"],
        "projectId": row["project_id"],
        "datasetId": row["dataset_id"],
        "planId": row.get("plan_id"),
        "kind": row["kind"],
        "status": row["status"],
        "createdBy": row["created_by"],
        "createdAt": _iso(row["created_at"]),
        "updatedAt": _iso(row["updated_at"]),
    }


def _tool_call_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "jobId": row["job_id"],
        "stepId": row["step_id"],
        "toolId": row["tool_id"],
        "status": row["status"],
        "idempotencyKey": row.get("idempotency_key"),
        "attempt": row.get("attempt") or 1,
        "params": _json_copy(row.get("params_json") or {}),
        "error": _json_copy(row.get("error_json")) if row.get("error_json") else None,
    }


def _artifact_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "artifactId": row["id"],
        "projectId": row["project_id"],
        "datasetId": row["dataset_id"],
        "jobId": row["job_id"],
        "toolCallId": row["tool_call_id"],
        "type": row["type"],
        "name": row["name"],
        "version": row["version"],
        "storageKey": row["storage_key"],
        "storageProvider": row.get("storage_provider") or "local",
        "bucket": row.get("bucket"),
        "previewKey": row["preview_key"],
        "sizeBytes": row["size_bytes"],
        "contentType": row["content_type"],
        "contentHash": row["content_hash"],
        "sha256": row["sha256"],
        "metadata": _json_copy(row.get("metadata_json") or {}),
        "createdAt": _iso(row["created_at"]),
    }


def _recipe_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    recipe = _json_copy(row.get("recipe_json") or {})
    recipe.setdefault("recipeId", row["id"])
    recipe.setdefault("id", row["id"])
    recipe.setdefault("projectId", row["project_id"])
    recipe.setdefault("sourceJobId", row["source_job_id"])
    recipe.setdefault("name", row["name"])
    recipe["createdAt"] = _iso(row["created_at"])
    return recipe


def _report_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    report = _json_copy(row.get("report_json") or {})
    report.setdefault("id", row["id"])
    report.setdefault("reportId", row["id"])
    report.setdefault("projectId", row["project_id"])
    report.setdefault("datasetId", row["dataset_id"])
    report.setdefault("jobId", row["job_id"])
    report.setdefault("sourceJobId", row["job_id"])
    report.setdefault("version", row["version"])
    report.setdefault("title", row["title"])
    report.setdefault("markdownKey", row["markdown_key"])
    report.setdefault("htmlKey", row["html_key"])
    report["createdBy"] = report.get("createdBy") or row["created_by"]
    report["createdAt"] = report.get("createdAt") or _iso(row["created_at"])
    return report


def _validate_artifact_storage_record(record: Mapping[str, Any]) -> None:
    metadata = record.get("metadata") or {}
    if hasattr(metadata, "model_dump"):
        metadata = metadata.model_dump(mode="json")
    provider = str(
        record.get("storageProvider")
        or record.get("storage_provider")
        or metadata.get("storageProvider")
        or metadata.get("storage_provider")
        or "local"
    )
    if provider not in {"local", "s3", "minio"}:
        raise ValueError(f"Unknown artifact storage provider: {provider}")
    bucket = record.get("bucket") or metadata.get("bucket")
    if provider in {"s3", "minio"} and not bucket:
        raise ValueError(f"Artifact storage provider {provider} requires bucket")
    size_bytes = int(record.get("sizeBytes") or record.get("size_bytes") or 0)
    if size_bytes < 0:
        raise ValueError("Artifact sizeBytes must be non-negative")
    if not (record.get("storageKey") or record.get("storage_key")):
        raise ValueError("Artifact record is missing storageKey")


def _reject_credential_keys(value: Any) -> None:
    credential_keys = {"api_key", "apikey", "api-key", "token", "password", "secret", "credential", "authorization"}
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).lower().replace("_", "").replace("-", "")
            if normalized in credential_keys:
                raise ValueError(f"AnalysisPlan JSON contains credential-like key: {key}")
            _reject_credential_keys(nested)
    elif isinstance(value, list):
        for item in value:
            _reject_credential_keys(item)


def _required_id(record: Mapping[str, Any], alias: str = "id") -> str:
    value = record.get("id") or record.get(alias)
    if not value:
        raise ValueError(f"Record is missing id/{alias}")
    return str(value)


def _model_to_record(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return _json_copy(value)


def _row_to_json_dict(row: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items()}


def _json_copy(value: Any) -> Any:
    if value is None:
        return None
    return json.loads(json.dumps(value, default=str))


def _enum_value(value: Any) -> str:
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _iso(value: Any) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
