from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Mapping, Protocol

from sqlalchemy import and_, delete, func, insert, or_, select, text
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
    plan_dependency_bindings,
    runtime_artifact_binding_resolutions,
    tool_calls,
    users,
    visualization_recipes,
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
    DependencyBinding,
    DependencyExecutionRecord,
    JobEvent,
    JobEventStatus,
    JobStatus,
    ResolvedArtifactInputRef,
    ToolCall,
    VisualizationRecipe,
    compute_analysis_intent_hash,
    canonical_dependency_json,
    capability_semantic_hash,
    compute_analysis_plan_02_hash,
    deterministic_capability_id,
    dependency_semantic_hash,
    deterministic_dependency_id,
    deterministic_intent_id,
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
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
