from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from mdi_api.config import load_settings
from mdi_api.phase1_demo import submit_analysis_request_stub
from mdi_api.phase2_runtime import (
    create_phase2_dataset_profile,
    create_phase2_demo_dataset,
    create_phase2_job,
    create_phase2_project,
    get_phase2_artifact,
    get_phase2_artifact_download,
    get_phase2_dataset,
    get_phase2_dataset_profile,
    get_phase2_job,
    get_phase2_job_artifacts,
    get_phase2_job_events,
    get_phase2_job_tool_calls,
    list_phase2_datasets,
    list_phase2_projects,
    stream_phase2_job_events,
    upload_phase2_dataset,
)
from mdi_api.routers.auth import CurrentUser, get_current_user_stub, get_current_user, login, logout, LoginRequest
from mdi_api.routers.research import (
    ResearchAssistantProjectionCreate,
    ResearchMessageCreate,
    ResearchSessionCreate,
    ScopeResolveRequest,
    create_assistant_projection,
    create_message,
    create_session,
    get_session,
    list_sessions,
    resolve_scope,
)
from mdi_api.routers.datasets import (
    DatasetSummary,
    cancel_upload_session,
    complete_upload_session,
    create_upload_session,
    get_dataset_object_store,
    get_upload_capabilities,
    put_upload_session_file,
)
from mdi_api.routers.secured_runtime import (
    create_phase2_job_secured,
    create_demo_dataset_secured,
    upload_dataset_secured,
    create_dataset_profile_secured,
    put_upload_session_file_secured,
    complete_upload_session_secured,
    cancel_upload_session_secured,
    create_project_secured,
    create_upload_session_secured,
    get_phase2_artifact_download_secured,
    get_phase2_artifact_secured,
    get_phase2_job_artifacts_secured,
    get_phase2_job_events_secured,
    get_phase2_job_secured,
    get_phase2_job_tool_calls_secured,
    stream_phase2_job_events_secured,
    get_dataset_object_store_secured,
    get_dataset_profile_secured,
    get_dataset_secured,
    update_dataset_secured,
    bulk_dataset_action_secured,
    delete_empty_dataset_secured,
    list_datasets_secured,
    list_projects_secured,
    update_project_secured,
    bulk_project_action_secured,
    delete_empty_project_secured,
    stream_phase1_job_events_secured,
    submit_analysis_request_secured,
)
from mdi_api.routers.secured_planner import (
    create_planner_job_interpretation_secured,
    create_planner_job_secured,
    get_planner_interpretation_evidence_secured,
    get_planner_job_artifact_content_secured,
    get_planner_job_artifacts_secured,
    get_planner_job_dependencies_secured,
    get_planner_job_events_secured,
    get_planner_job_result_secured,
    get_planner_job_secured,
    get_planner_job_tool_calls_secured,
    stream_planner_job_events_secured,
    create_planner_intent_secured,
    get_planner_intent_secured,
    clarify_planner_intent_secured,
    get_planner_analysis_plan_secured,
    get_planner_interpretation_secured,
    list_planner_job_interpretations_secured,
    planner_preview_secured,
    planner_validate_secured,
)
from mdi_api.routers.health import health, runtime_health
from mdi_api.routers.planner import (
    PlannerIntentClarificationRequest,
    PlannerIntentCreateRequest,
    PlannerInterpretationRequest,
    PlannerJobsRequest,
    PlannerPreviewRequest,
    PlannerValidateRequest,
    clarify_planner_intent_route,
    create_planner_intent_route,
    create_planner_job_interpretation_route,
    get_planner_analysis_plan,
    get_planner_intent_route,
    get_planner_interpretation,
    get_planner_interpretation_evidence,
    get_planner_job,
    get_planner_job_artifacts,
    get_planner_job_dependencies,
    get_planner_job_artifact_content_route,
    get_planner_job_events,
    get_planner_job_result,
    list_planner_job_interpretations,
    get_planner_job_tool_calls,
    planner_jobs_route,
    planner_preview_route,
    planner_validate_route,
    stream_planner_job_events,
)
from mdi_api.routers.planner_providers import (
    configure_planner_provider,
    update_planner_provider_models,
    list_planner_providers,
    planner_provider_models,
    planner_provider_status,
    remove_planner_provider,
    resolve_planner_provider_route,
    test_planner_provider_route,
)
from mdi_api.routers.projects import ProjectSummary
from mdi_api.routers.project_history import archive_project_run, get_project_history, restore_project_run
from mdi_api.routers.report_compositions import (
    export_report_composition,
    finalize_report_composition,
    get_report_composition,
    get_report_composition_recipe,
    get_report_composition_sources,
    list_report_compositions,
    preview_report_composition,
)
from mdi_api.routers.secrets import (
    CreateSecretRequest,
    SecretSummary,
    create_secret,
    delete_secret,
    list_secrets,
)
from mdi_api.routers.tools import list_mvp_tools, list_tools
from mdi_api.routers.agent2 import (
    cancel_research_turn,
    dispatch_research_turn,
    create_research_turn,
    get_research_turn,
    get_research_turn_progress,
    get_research_turn_result,
    project_research_turn_result,
    interpret_research_turn,
    get_research_turn_interpretation,
    get_scientific_object,
    get_scientific_object_version,
    get_scientific_object_viewer,
    list_research_turns,
    get_research_session_memory,
    pin_research_result,
    unpin_research_result,
    pin_research_object,
    unpin_research_object,
    list_scientific_object_relationships,
    list_scientific_object_versions,
    list_scientific_objects,
    promote_dataset_table,
    stream_research_turn_events,
)
from mdi_api.routers.scientific_reports import (
    generate_scientific_report,
    get_scientific_report,
    get_scientific_report_by_id,
    list_scientific_reports,
)
from mdi_api.routers.workspaces import (
    create_workspace,
    get_workspace,
    get_workspace_layout_revision,
    get_workspace_panel,
    list_analysis_jobs,
    list_project_workspaces,
    list_workspace_layout_revisions,
    list_workspace_panels,
    patch_workspace,
)


@dataclass(frozen=True)
class RouteSpec:
    path: str
    endpoint: Callable[..., Any]
    methods: tuple[str, ...]
    tags: tuple[str, ...]
    response_model: Any | None = None


@dataclass(frozen=True)
class AppSpec:
    title: str
    version: str
    routes: tuple[RouteSpec, ...]


ROUTES: tuple[RouteSpec, ...] = (
    RouteSpec("/health", health, ("GET",), ("health",)),
    RouteSpec("/health/runtime", runtime_health, ("GET",), ("health",)),
    RouteSpec("/auth/me", get_current_user, ("GET",), ("auth",), CurrentUser),
    RouteSpec("/auth/login", login, ("POST",), ("auth",), CurrentUser),
    RouteSpec("/auth/logout", logout, ("POST",), ("auth",)),
    RouteSpec("/projects/{project_id}/research-sessions", list_sessions, ("GET",), ("research",)),
    RouteSpec("/projects/{project_id}/research-sessions", create_session, ("POST",), ("research",)),
    RouteSpec("/research-sessions/{session_id}", get_session, ("GET",), ("research",)),
    RouteSpec("/research-sessions/{session_id}/messages", create_message, ("POST",), ("research",)),
    RouteSpec("/research-sessions/{session_id}/assistant-projections", create_assistant_projection, ("POST",), ("research",)),
    RouteSpec("/api/projects/{project_id}/research/sessions/{session_id}/turns", create_research_turn, ("POST",), ("agent2", "research")),
    RouteSpec("/api/projects/{project_id}/research/sessions/{session_id}/turns", list_research_turns, ("GET",), ("agent2", "research")),
    RouteSpec("/api/projects/{project_id}/research/sessions/{session_id}/memory", get_research_session_memory, ("GET",), ("agent2", "research")),
    RouteSpec("/api/projects/{project_id}/research/sessions/{session_id}/memory/pinned-results/{result_id}", pin_research_result, ("POST",), ("agent2", "research")),
    RouteSpec("/api/projects/{project_id}/research/sessions/{session_id}/memory/pinned-results/{result_id}", unpin_research_result, ("DELETE",), ("agent2", "research")),
    RouteSpec("/api/projects/{project_id}/research/sessions/{session_id}/memory/pinned-objects", pin_research_object, ("POST",), ("agent2", "research")),
    RouteSpec("/api/projects/{project_id}/research/sessions/{session_id}/memory/pinned-objects", unpin_research_object, ("DELETE",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}", get_research_turn, ("GET",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/cancel", cancel_research_turn, ("POST",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/dispatch", dispatch_research_turn, ("POST",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/progress", get_research_turn_progress, ("GET",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/result", get_research_turn_result, ("GET",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/project-result", project_research_turn_result, ("POST",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/interpret", interpret_research_turn, ("POST",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/interpretation", get_research_turn_interpretation, ("GET",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/report", generate_scientific_report, ("POST",), ("agent2", "reports")),
    RouteSpec("/api/research/turns/{turn_id}/report", get_scientific_report, ("GET",), ("agent2", "reports")),
    RouteSpec("/api/scientific-reports/{report_id}", get_scientific_report_by_id, ("GET",), ("agent2", "reports")),
    RouteSpec("/api/projects/{project_id}/scientific-reports", list_scientific_reports, ("GET",), ("agent2", "reports")),
    RouteSpec("/api/research/turns/{turn_id}/events", stream_research_turn_events, ("GET",), ("agent2", "research")),
    RouteSpec("/api/projects/{project_id}/scientific-objects", list_scientific_objects, ("GET",), ("agent2", "scientific-objects")),
    RouteSpec("/api/projects/{project_id}/datasets/{dataset_id}/scientific-table", promote_dataset_table, ("POST",), ("agent2", "scientific-objects")),
    RouteSpec("/api/scientific-objects/{object_id}", get_scientific_object, ("GET",), ("agent2", "scientific-objects")),
    RouteSpec("/api/scientific-objects/{object_id}/versions", list_scientific_object_versions, ("GET",), ("agent2", "scientific-objects")),
    RouteSpec("/api/scientific-objects/{object_id}/versions/{version_id}", get_scientific_object_version, ("GET",), ("agent2", "scientific-objects")),
    RouteSpec("/api/scientific-objects/{object_id}/versions/{version_id}/viewer", get_scientific_object_viewer, ("GET",), ("agent2", "scientific-viewers")),
    RouteSpec("/api/scientific-objects/{object_id}/relationships", list_scientific_object_relationships, ("GET",), ("agent2", "scientific-objects")),
    RouteSpec("/projects/{project_id}/research-scope", resolve_scope, ("POST",), ("research",)),
    RouteSpec("/projects", list_projects_secured, ("GET",), ("projects",), list[ProjectSummary]),
    RouteSpec("/projects", create_project_secured, ("POST",), ("projects",)),
    RouteSpec("/projects/bulk", bulk_project_action_secured, ("POST",), ("projects",)),
    RouteSpec("/projects/{project_id}", update_project_secured, ("PATCH",), ("projects",)),
    RouteSpec("/projects/{project_id}", delete_empty_project_secured, ("DELETE",), ("projects",)),
    RouteSpec("/projects/{project_id}/history", get_project_history, ("GET",), ("projects",)),
    RouteSpec("/projects/{project_id}/runs/{job_id}/archive", archive_project_run, ("POST",), ("projects",)),
    RouteSpec("/projects/{project_id}/runs/{job_id}/archive", restore_project_run, ("DELETE",), ("projects",)),
    RouteSpec("/datasets", list_datasets_secured, ("GET",), ("datasets",), list[DatasetSummary]),
    RouteSpec("/datasets/bulk", bulk_dataset_action_secured, ("POST",), ("datasets",)),
    RouteSpec("/datasets/demo", create_demo_dataset_secured, ("POST",), ("datasets",)),
    RouteSpec("/datasets/upload-capabilities", get_upload_capabilities, ("GET",), ("datasets",)),
    RouteSpec("/datasets/upload", upload_dataset_secured, ("POST",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}/object-store", get_dataset_object_store_secured, ("GET",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}", get_dataset_secured, ("GET",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}", update_dataset_secured, ("PATCH",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}", delete_empty_dataset_secured, ("DELETE",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}/profile", get_dataset_profile_secured, ("GET",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}/profile", create_dataset_profile_secured, ("POST",), ("datasets",)),
    RouteSpec("/projects/{project_id}/upload-sessions", create_upload_session_secured, ("POST",), ("datasets",)),
    RouteSpec("/upload-sessions/{session_id}/files/{file_id}", put_upload_session_file_secured, ("PUT",), ("datasets",)),
    RouteSpec("/upload-sessions/{session_id}/complete", complete_upload_session_secured, ("POST",), ("datasets",)),
    RouteSpec("/upload-sessions/{session_id}", cancel_upload_session_secured, ("DELETE",), ("datasets",)),
    RouteSpec("/analysis-requests", submit_analysis_request_secured, ("POST",), ("analysis",)),
    RouteSpec("/jobs", create_phase2_job_secured, ("POST",), ("jobs",)),
    RouteSpec("/jobs/{job_id}", get_phase2_job_secured, ("GET",), ("jobs",)),
    RouteSpec("/jobs/{job_id}/events", get_phase2_job_events_secured, ("GET",), ("jobs",)),
    RouteSpec("/jobs/{job_id}/events/stream", stream_phase1_job_events_secured, ("GET",), ("jobs",)),
    RouteSpec("/jobs/{job_id}/stream", stream_phase2_job_events_secured, ("GET",), ("jobs",)),
    RouteSpec("/jobs/{job_id}/tool-calls", get_phase2_job_tool_calls_secured, ("GET",), ("jobs",)),
    RouteSpec("/jobs/{job_id}/artifacts", get_phase2_job_artifacts_secured, ("GET",), ("jobs",)),
    RouteSpec("/artifacts/{artifact_id}", get_phase2_artifact_secured, ("GET",), ("artifacts",)),
    RouteSpec("/artifacts/{artifact_id}/download", get_phase2_artifact_download_secured, ("GET",), ("artifacts",)),
    RouteSpec("/tools", list_tools, ("GET",), ("tools",)),
    RouteSpec("/tools/mvp", list_mvp_tools, ("GET",), ("tools",)),
    # Phase 7: Planner API
    RouteSpec("/planner/preview", planner_preview_secured, ("POST",), ("planner",)),
    RouteSpec("/planner/validate", planner_validate_secured, ("POST",), ("planner",)),
    RouteSpec("/planner/intents", create_planner_intent_secured, ("POST",), ("planner",)),
    RouteSpec("/planner/intents/{intent_id}", get_planner_intent_secured, ("GET",), ("planner",)),
    RouteSpec("/planner/intents/{intent_id}/clarification", clarify_planner_intent_secured, ("POST",), ("planner",)),
    RouteSpec("/planner/jobs", create_planner_job_secured, ("POST",), ("planner",)),
    RouteSpec("/planner/providers", list_planner_providers, ("GET",), ("planner",)),
    RouteSpec("/planner/providers/configure", configure_planner_provider, ("POST",), ("planner",)),
    RouteSpec("/planner/providers/{provider}/models", update_planner_provider_models, ("PATCH",), ("planner",)),
    RouteSpec("/planner/providers/status", planner_provider_status, ("GET",), ("planner",)),
    RouteSpec("/planner/providers/{provider}/models", planner_provider_models, ("GET",), ("planner",)),
    RouteSpec("/planner/providers/{provider}", remove_planner_provider, ("DELETE",), ("planner",)),
    RouteSpec("/planner/providers/resolve", resolve_planner_provider_route, ("POST",), ("planner",)),
    RouteSpec("/planner/providers/test", test_planner_provider_route, ("POST",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}", get_planner_job_secured, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/events", get_planner_job_events_secured, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/events/stream", stream_planner_job_events_secured, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/tool-calls", get_planner_job_tool_calls_secured, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/artifacts", get_planner_job_artifacts_secured, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/dependencies", get_planner_job_dependencies_secured, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/artifacts/{artifact_id}/content", get_planner_job_artifact_content_secured, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/result", get_planner_job_result_secured, ("GET",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/interpretations", create_planner_job_interpretation_secured, ("POST",), ("planner",)),
    RouteSpec("/planner/jobs/{job_id}/interpretations", list_planner_job_interpretations_secured, ("GET",), ("planner",)),
    RouteSpec("/planner/interpretations/{interpretation_id}", get_planner_interpretation_secured, ("GET",), ("planner",)),
    RouteSpec("/planner/interpretations/{interpretation_id}/evidence", get_planner_interpretation_evidence_secured, ("GET",), ("planner",)),
    RouteSpec("/planner/analysis-plans/{plan_id}", get_planner_analysis_plan_secured, ("GET",), ("planner",)),
    # Phase 10M-1: metadata-only Scientific Workspace API
    RouteSpec("/workspaces", create_workspace, ("POST",), ("workspaces",)),
    RouteSpec("/workspaces/{workspace_id}", get_workspace, ("GET",), ("workspaces",)),
    RouteSpec("/workspaces/{workspace_id}", patch_workspace, ("PATCH",), ("workspaces",)),
    RouteSpec("/projects/{project_id}/workspaces", list_project_workspaces, ("GET",), ("workspaces",)),
    RouteSpec("/projects/{project_id}/analysis-jobs", list_analysis_jobs, ("GET",), ("workspaces",)),
    RouteSpec("/workspaces/{workspace_id}/panels", list_workspace_panels, ("GET",), ("workspaces",)),
    RouteSpec("/workspaces/{workspace_id}/panels/{panel_id}", get_workspace_panel, ("GET",), ("workspaces",)),
    RouteSpec(
        "/workspaces/{workspace_id}/layout-revisions",
        list_workspace_layout_revisions,
        ("GET",),
        ("workspaces",),
    ),
    RouteSpec(
        "/workspaces/{workspace_id}/layout-revisions/{revision}",
        get_workspace_layout_revision,
        ("GET",),
        ("workspaces",),
    ),
    # Phase 10M-5: deterministic Report/Recipe composition over exact Workspace sources
    RouteSpec("/workspaces/{workspace_id}/report-composition/sources", get_report_composition_sources, ("GET",), ("workspaces", "reports")),
    RouteSpec("/workspaces/{workspace_id}/report-compositions/preview", preview_report_composition, ("POST",), ("workspaces", "reports")),
    RouteSpec("/workspaces/{workspace_id}/report-compositions", finalize_report_composition, ("POST",), ("workspaces", "reports")),
    RouteSpec("/workspaces/{workspace_id}/report-compositions", list_report_compositions, ("GET",), ("workspaces", "reports")),
    RouteSpec("/workspaces/{workspace_id}/report-compositions/{report_id}", get_report_composition, ("GET",), ("workspaces", "reports")),
    RouteSpec("/workspaces/{workspace_id}/report-compositions/{report_id}/recipe", get_report_composition_recipe, ("GET",), ("workspaces", "reports")),
    RouteSpec("/workspaces/{workspace_id}/report-compositions/{report_id}/exports/{format}", export_report_composition, ("GET",), ("workspaces", "reports")),
    # Phase 7: Secrets API
    RouteSpec("/me/secrets", create_secret, ("POST",), ("secrets",)),
    RouteSpec("/me/secrets", list_secrets, ("GET",), ("secrets",), list[SecretSummary]),
    RouteSpec("/me/secrets/{secret_id}", delete_secret, ("DELETE",), ("secrets",)),
)


def create_app() -> Any:
    settings = load_settings()
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError:
        return AppSpec(title=settings.app_name, version="0.1.0", routes=ROUTES)

    # Registry validation is intentionally outside the compatibility fallback:
    # a malformed registered manifest must fail startup, not silently degrade
    # into an AppSpec shell.
    from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES, validate_agent2_registries
    from mdi_tool_registry import ToolRegistry, list_tools as list_registered_tools

    validate_agent2_registries(
        DEFAULT_AGENT2_REGISTRIES,
        ToolRegistry(version="agent2-startup", tools=tuple(list_registered_tools())),
    )
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Controlled API boundary for material data intelligence workflows.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["ETag", "X-Idempotent-Replay"],
    )
    for route in ROUTES:
        app.add_api_route(
            route.path,
            route.endpoint,
            methods=list(route.methods),
            tags=list(route.tags),
            response_model=route.response_model,
        )
    return app


app = create_app()
