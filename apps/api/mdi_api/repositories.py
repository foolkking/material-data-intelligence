from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Mapping, Protocol

from sqlalchemy import and_, func, insert, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Connection, Engine

from mdi_api.db import (  # noqa: F401
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
    messages,
    reports,
    research_turns,
    scientific_evidence_bundles,
    scientific_interpretation_runs,
    scientific_interpretation_claims,
    scientific_interpretation_evidence_links,
    scientific_interpretations,
    scientific_workspaces,
    plan_dependency_bindings,
    runtime_artifact_binding_resolutions,
    tool_calls,
    visualization_recipes,
    workspace_layout_revisions,
    workspace_panels,
)
from mdi_schemas import (  # noqa: F401
    AnalysisPlan,
    AnalysisPlanV02,
    Artifact,
    ArtifactLineageRecord,
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
    canonical_dependency_json,
    compute_analysis_plan_02_hash,
    dependency_semantic_hash,
    deterministic_dependency_id,
    make_layout_revision,
)

from mdi_api.state_machine import (  # noqa: F401
    validate_job_status,
    validate_job_transition,
    validate_tool_call_status,
    validate_tool_call_transition,
)
from mdi_api.application.data.ports import DataProfileRepository, DatasetRepository  # noqa: F401
from mdi_api.application.interpretation.ports import ScientificInterpretationRepository  # noqa: F401
from mdi_api.infrastructure.persistence.memory_interpretation import InMemoryScientificInterpretationRepository
from mdi_api.infrastructure.persistence.sqlalchemy_interpretation import (
    SqlAlchemyScientificInterpretationRepository,
)
from mdi_api.infrastructure.persistence.interpretation_common import (
    _KeyedLockRegistry,  # noqa: F401
    validate_interpretation_associations as _validate_interpretation_associations,  # noqa: F401
    validate_interpretation_run_association as _validate_interpretation_run_association,  # noqa: F401
)
from mdi_api.infrastructure.persistence.sqlalchemy_interpretation import _SQL_INTERPRETATION_LOCKS  # noqa: F401
from mdi_api.application.research.planning.ports import (
    AnalysisPlanRepository,  # noqa: F401
    DependencyExecutionRepository,  # noqa: F401
)
from mdi_api.application.research.planning.integrity import (
    canonical_analysis_plan_json,  # noqa: F401
    compute_plan_hash,  # noqa: F401
)
from mdi_api.infrastructure.persistence.memory_analysis_plans import InMemoryAnalysisPlanRepository
from mdi_api.infrastructure.persistence.memory_dependency import InMemoryDependencyExecutionRepository
from mdi_api.infrastructure.persistence.sqlalchemy_analysis_plans import SqlAlchemyAnalysisPlanRepository
from mdi_api.infrastructure.persistence.sqlalchemy_dependency import SqlAlchemyDependencyExecutionRepository
from mdi_api.infrastructure.persistence.planning_records import (
    _analysis_plan_from_record,  # noqa: F401
    _analysis_plan_from_row,  # noqa: F401
    _analysis_plan_values,  # noqa: F401
    _artifact_lineage_from_row,  # noqa: F401
    _artifact_lineage_values,  # noqa: F401
    _binding_resolution_from_row,  # noqa: F401
    _binding_resolution_values,  # noqa: F401
    _dependency_execution_from_row,  # noqa: F401
    _dependency_execution_values,  # noqa: F401
    _normalize_analysis_plan_record,  # noqa: F401
    _normalize_artifact_lineage_record,  # noqa: F401
    _normalize_binding_resolution_record,  # noqa: F401
    _normalize_dependency_execution_record,  # noqa: F401
    _normalize_plan_bindings,  # noqa: F401
    _planned_binding_from_row,  # noqa: F401
    _planned_binding_values,  # noqa: F401
    _reject_credential_keys,  # noqa: F401
)
from mdi_api.application.reports.ports import RecipeRepository, ReportRepository  # noqa: F401
from mdi_api.infrastructure.persistence.memory_reports import (
    InMemoryRecipeRepository,
    InMemoryReportRepository,
)
from mdi_api.infrastructure.persistence.sqlalchemy_reports import (
    SqlAlchemyRecipeRepository,
    SqlAlchemyReportRepository,
    _recipe_from_row,  # noqa: F401
    _report_from_row,  # noqa: F401
    _assert_immutable_delivery_compatible,  # noqa: F401
)
from mdi_api.application.artifacts.ports import ArtifactRepository  # noqa: F401
from mdi_api.infrastructure.persistence.memory_artifacts import InMemoryArtifactRepository
from mdi_api.infrastructure.persistence.sqlalchemy_artifacts import (
    SqlAlchemyArtifactRepository,
    _artifact_from_row,  # noqa: F401
    _validate_artifact_storage_record,  # noqa: F401
)
from mdi_api.application.jobs.ports import JobEventRepository, JobRepository, ToolCallRepository  # noqa: F401
from mdi_api.infrastructure.persistence.memory_jobs import (
    InMemoryJobEventRepository,
    InMemoryJobRepository,
    InMemoryToolCallRepository,
)
from mdi_api.infrastructure.persistence.sqlalchemy_jobs import (  # noqa: F401
    SqlAlchemyJobEventRepository,
    SqlAlchemyJobRepository,
    SqlAlchemyToolCallRepository,
)
from mdi_api.application.research.planning.ports import (  # noqa: F401
    AnalysisIntentRepository,
    CapabilityPlanningRepository,
)
from mdi_api.infrastructure.persistence.memory_planning import (
    InMemoryAnalysisIntentRepository,
    InMemoryCapabilityPlanningRepository,
)
from mdi_api.infrastructure.persistence.sqlalchemy_planning import (
    SqlAlchemyAnalysisIntentRepository,
    SqlAlchemyCapabilityPlanningRepository,
)
from mdi_api.application.projects.ports import ProjectRepository  # noqa: F401
from mdi_api.infrastructure.persistence.base import (
    _SqlAlchemyRepository,
    _enum_value,  # noqa: F401
    _iso,
    _json_copy,
    _model_to_record,  # noqa: F401
    _parse_iso,  # noqa: F401
    _required_id,  # noqa: F401
    _row_to_json_dict,
    _utc_now,  # noqa: F401
)
from mdi_api.infrastructure.persistence.sqlalchemy_jobs import (
    _job_event_from_row,  # noqa: F401
    _job_event_values,  # noqa: F401
    _job_from_row,  # noqa: F401
    _lock_job_event_sequence,  # noqa: F401
    _tool_call_from_row,  # noqa: F401
)
from mdi_api.infrastructure.persistence.planning import (  # noqa: F401
    analysis_intent_from_record as _analysis_intent_from_record,
    analysis_intent_from_row as _analysis_intent_from_row,
    analysis_intent_values as _analysis_intent_values,
    capability_decision_from_row as _capability_decision_from_row,
    capability_decision_values as _capability_decision_values,
    capability_execution_from_row as _capability_execution_from_row,
    capability_resolution_from_row as _capability_resolution_from_row,
    capability_resolution_values as _capability_resolution_values,
    intent_execution_from_row as _intent_execution_from_row,
    normalize_analysis_intent_record as _normalize_analysis_intent_record,
    normalize_capability_decision_record as _normalize_capability_decision_record,
    normalize_capability_resolution_record as _normalize_capability_resolution_record,
)
from mdi_api.infrastructure.persistence.memory import (
    InMemoryDataProfileRepository,
    InMemoryDatasetRepository,
    InMemoryProjectRepository,
)
from mdi_api.infrastructure.persistence.sqlalchemy import (
    SqlAlchemyDataProfileRepository,
    SqlAlchemyDatasetRepository,
    SqlAlchemyProjectRepository,
    _ensure_user,  # noqa: F401
)
























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
