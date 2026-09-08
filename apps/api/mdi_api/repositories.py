# ruff: noqa: F401

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
from mdi_api.infrastructure.persistence.bundles import InMemoryRepositoryBundle, SqlAlchemyRepositoryBundle
from mdi_api.application.workspaces.ports import (
    WorkspaceCapacityError,  # noqa: F401
    WorkspaceConflictError,  # noqa: F401
    WorkspaceNotFoundError,  # noqa: F401
    WorkspaceRepository,  # noqa: F401
    WorkspaceRepositoryError,  # noqa: F401
    WorkspaceScopeError,  # noqa: F401
)
from mdi_api.infrastructure.persistence.memory_workspace import InMemoryWorkspaceRepository
from mdi_api.infrastructure.persistence.sqlalchemy_workspace import SqlAlchemyWorkspaceRepository
from mdi_api.infrastructure.persistence.workspace_common import (
    _WORKSPACE_UNSET,  # noqa: F401
    _enforce_workspace_project,  # noqa: F401
    _parse_workspace,  # noqa: F401
    _parse_workspace_layout,  # noqa: F401
    _parse_workspace_layout_revision,  # noqa: F401
    _parse_workspace_panel,  # noqa: F401
    _parse_workspace_selection,  # noqa: F401
    _prepare_workspace_update,  # noqa: F401
    _validate_layout_panel_membership,  # noqa: F401
    _validate_panel_project_scope,  # noqa: F401
    _validate_workspace_create_aggregate,  # noqa: F401
    _workspace_layout_record,  # noqa: F401
    _workspace_layout_values,  # noqa: F401
    _workspace_panel_record,  # noqa: F401
    _workspace_panel_values,  # noqa: F401
    _workspace_record,  # noqa: F401
    _workspace_source_identity,  # noqa: F401
    _workspace_values,  # noqa: F401
)
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
