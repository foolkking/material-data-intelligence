from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
import logging
from typing import Any, Callable

from mdi_api.config import load_settings
from mdi_api.transport.routers.auth import (
    CurrentUser,
    activate_account,
    change_password,
    deactivate_account,
    get_current_user,
    list_auth_sessions,
    login,
    logout,
    revoke_auth_session,
    revoke_other_auth_sessions,
    update_profile,
)
from mdi_api.transport.routers.platform_admin import (
    get_platform_admin_overview,
    list_platform_audit,
    list_platform_project_members,
    list_platform_projects,
    list_platform_users,
    remove_platform_project_member,
    update_platform_project_member,
    update_platform_user,
    create_platform_invitation,
)
from mdi_api.transport.routers.research import (
    bulk_update_sessions,
    create_assistant_projection,
    create_message,
    create_session,
    get_session,
    get_session_dependency_impact,
    list_sessions,
    update_session,
    resolve_scope,
)
from mdi_api.transport.routers.datasets import (
    DatasetSummary,
    get_upload_capabilities,
)
from mdi_api.transport.routers.secured_runtime import (
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
    get_dataset_research_sources_secured,
    get_dataset_profile_secured,
    get_dataset_secured,
    update_dataset_secured,
    bulk_dataset_action_secured,
    delete_empty_dataset_secured,
    get_dataset_dependency_impact_secured,
    list_datasets_secured,
    list_projects_secured,
    list_saved_product_searches,
    list_notification_read_states,
    search_product_secured,
    create_saved_product_search,
    update_saved_product_search,
    delete_saved_product_search,
    execute_saved_product_search,
    update_notification_read_state,
    update_project_secured,
    bulk_project_action_secured,
    delete_empty_project_secured,
    get_project_dependency_impact_secured,
    get_project_export_manifest_secured,
    stream_phase1_job_events_secured,
    submit_analysis_request_secured,
)
from mdi_api.transport.routers.secured_planner import (
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
from mdi_api.transport.routers.health import health, runtime_health, task_health_projection
from mdi_api.transport.routers.user_models import get_user_models, save_user_connection, discover_user_models, save_user_model_selection
from mdi_api.transport.routers.platform_models import list_offerings, save_offering, save_plan_grant
from mdi_api.transport.routers.observability import capture_client_exception
from mdi_api.transport.routers.planner_providers import (
    configure_planner_provider,
    update_planner_provider_models,
    list_planner_providers,
    planner_provider_models,
    planner_provider_status,
    remove_planner_provider,
    resolve_planner_provider_route,
    test_planner_provider_route,
)
from mdi_api.transport.routers.projects import ProjectSummary
from mdi_api.transport.routers.project_history import archive_project_run, get_project_history, restore_project_run
from mdi_api.transport.routers.report_compositions import (
    export_report_composition,
    finalize_report_composition,
    get_report_composition,
    get_report_composition_recipe,
    get_report_composition_sources,
    list_report_compositions,
    preview_report_composition,
)
from mdi_api.transport.routers.secrets import (
    SecretSummary,
    create_secret,
    delete_secret,
    list_secrets,
)
from mdi_api.transport.routers.tools import list_mvp_tools, list_tools
from mdi_api.transport.routers.agent2 import (
    cancel_research_turn,
    dispatch_research_turn,
    create_research_turn,
    get_research_turn,
    get_research_turn_context_manifest,
    get_research_turn_correlation,
    get_research_turn_progress,
    get_research_turn_result,
    project_research_turn_result,
    interpret_research_turn,
    get_research_turn_interpretation,
    get_scientific_object,
    get_scientific_object_dependency_impact,
    admit_scientific_object,
    update_scientific_object,
    get_scientific_object_version,
    create_scientific_object_version,
    query_scientific_dataset,
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
    bulk_update_scientific_objects,
    promote_dataset_table,
    stream_research_turn_events,
    stream_research_answer,
)
from mdi_api.transport.routers.scientific_reports import (
    bulk_update_scientific_report_lifecycle,
    compare_scientific_report_revisions,
    create_scientific_report_revision,
    generate_scientific_report,
    get_scientific_report_dependency_impact,
    get_scientific_report,
    get_scientific_report_status,
    get_scientific_report_by_id,
    list_scientific_report_revisions,
    list_scientific_reports,
    update_scientific_report_lifecycle,
    update_scientific_report_organization,
)
from mdi_api.transport.routers.scientific_knowledge import (
    get_scientific_literature_evidence,
    list_turn_scientific_literature,
    search_scientific_literature,
    select_scientific_literature_evidence,
)
from mdi_api.transport.routers.workspaces import (
    create_workspace,
    get_workspace,
    get_workspace_layout_revision,
    get_workspace_panel,
    list_analysis_jobs,
    list_project_workspaces,
    list_task_feed,
    list_workspace_layout_revisions,
    list_workspace_panels,
    patch_workspace,
)


logger = logging.getLogger("uvicorn.error")


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
    RouteSpec("/health/tasks", task_health_projection, ("GET",), ("health",)),
    RouteSpec(
        "/api/observability/client-exceptions",
        capture_client_exception,
        ("POST",),
        ("observability",),
    ),
    RouteSpec("/auth/me", get_current_user, ("GET",), ("auth",), CurrentUser),
    RouteSpec("/auth/login", login, ("POST",), ("auth",), CurrentUser),
    RouteSpec("/auth/activate", activate_account, ("POST",), ("auth",), CurrentUser),
    RouteSpec("/auth/logout", logout, ("POST",), ("auth",)),
    RouteSpec("/auth/profile", update_profile, ("PATCH",), ("auth",), CurrentUser),
    RouteSpec("/auth/sessions", list_auth_sessions, ("GET",), ("auth",)),
    RouteSpec("/auth/sessions/revoke-others", revoke_other_auth_sessions, ("POST",), ("auth",)),
    RouteSpec("/auth/sessions/{session_id}", revoke_auth_session, ("DELETE",), ("auth",)),
    RouteSpec("/auth/change-password", change_password, ("POST",), ("auth",)),
    RouteSpec("/auth/deactivate", deactivate_account, ("POST",), ("auth",)),
    RouteSpec("/api/admin/overview", get_platform_admin_overview, ("GET",), ("admin",)),
    RouteSpec("/api/admin/users", list_platform_users, ("GET",), ("admin",)),
    RouteSpec("/api/admin/users/{user_id}", update_platform_user, ("PATCH",), ("admin",)),
    RouteSpec("/api/admin/invitations", create_platform_invitation, ("POST",), ("admin",)),
    RouteSpec("/api/admin/projects", list_platform_projects, ("GET",), ("admin",)),
    RouteSpec("/api/admin/projects/{project_id}/members", list_platform_project_members, ("GET",), ("admin",)),
    RouteSpec("/api/admin/projects/{project_id}/members/{user_id}", update_platform_project_member, ("PUT",), ("admin",)),
    RouteSpec("/api/admin/projects/{project_id}/members/{user_id}", remove_platform_project_member, ("DELETE",), ("admin",)),
    RouteSpec("/api/admin/audit", list_platform_audit, ("GET",), ("admin",)),
    RouteSpec("/projects/{project_id}/research-sessions", list_sessions, ("GET",), ("research",)),
    RouteSpec("/projects/{project_id}/research-sessions", create_session, ("POST",), ("research",)),
    RouteSpec("/projects/{project_id}/research-sessions/bulk", bulk_update_sessions, ("POST",), ("research",)),
    RouteSpec("/research-sessions/{session_id}", get_session, ("GET",), ("research",)),
    RouteSpec("/research-sessions/{session_id}/dependency-impact", get_session_dependency_impact, ("GET",), ("research",)),
    RouteSpec("/research-sessions/{session_id}", update_session, ("PATCH",), ("research",)),
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
    RouteSpec("/api/research/turns/{turn_id}/context-manifest", get_research_turn_context_manifest, ("GET",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/correlation", get_research_turn_correlation, ("GET",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/cancel", cancel_research_turn, ("POST",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/dispatch", dispatch_research_turn, ("POST",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/progress", get_research_turn_progress, ("GET",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/result", get_research_turn_result, ("GET",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/project-result", project_research_turn_result, ("POST",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/interpret", interpret_research_turn, ("POST",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/interpretation", get_research_turn_interpretation, ("GET",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/report", generate_scientific_report, ("POST",), ("agent2", "reports")),
    RouteSpec("/api/research/turns/{turn_id}/report", get_scientific_report, ("GET",), ("agent2", "reports")),
    RouteSpec("/api/research/turns/{turn_id}/report-status", get_scientific_report_status, ("GET",), ("agent2", "reports")),
    RouteSpec("/api/projects/{project_id}/scientific-literature/search", search_scientific_literature, ("POST",), ("agent2", "literature")),
    RouteSpec("/api/projects/{project_id}/scientific-literature/evidence", select_scientific_literature_evidence, ("POST",), ("agent2", "literature")),
    RouteSpec("/api/scientific-literature/evidence/{evidence_id}", get_scientific_literature_evidence, ("GET",), ("agent2", "literature")),
    RouteSpec("/api/research/turns/{turn_id}/scientific-literature", list_turn_scientific_literature, ("GET",), ("agent2", "literature")),
    RouteSpec("/api/scientific-reports/{report_id}", get_scientific_report_by_id, ("GET",), ("agent2", "reports")),
    RouteSpec("/api/scientific-reports/{report_id}/lifecycle", update_scientific_report_lifecycle, ("PATCH",), ("agent2", "reports")),
    RouteSpec("/api/scientific-reports/{report_id}/organization", update_scientific_report_organization, ("PATCH",), ("agent2", "reports")),
    RouteSpec("/api/scientific-reports/{report_id}/dependency-impact", get_scientific_report_dependency_impact, ("GET",), ("agent2", "reports")),
    RouteSpec("/api/scientific-reports/{report_id}/revisions", create_scientific_report_revision, ("POST",), ("agent2", "reports")),
    RouteSpec("/api/scientific-reports/{report_id}/revisions", list_scientific_report_revisions, ("GET",), ("agent2", "reports")),
    RouteSpec("/api/scientific-reports/{report_id}/compare", compare_scientific_report_revisions, ("GET",), ("agent2", "reports")),
    RouteSpec("/api/projects/{project_id}/scientific-reports", list_scientific_reports, ("GET",), ("agent2", "reports")),
    RouteSpec("/api/projects/{project_id}/scientific-reports/bulk", bulk_update_scientific_report_lifecycle, ("POST",), ("agent2", "reports")),
    RouteSpec("/api/research/turns/{turn_id}/events", stream_research_turn_events, ("GET",), ("agent2", "research")),
    RouteSpec("/api/research/turns/{turn_id}/answer-stream", stream_research_answer, ("GET",), ("agent2", "research")),
    RouteSpec("/api/projects/{project_id}/scientific-objects", list_scientific_objects, ("GET",), ("agent2", "scientific-objects")),
    RouteSpec("/api/projects/{project_id}/scientific-objects", admit_scientific_object, ("POST",), ("agent2", "scientific-objects")),
    RouteSpec("/api/projects/{project_id}/scientific-objects/bulk", bulk_update_scientific_objects, ("POST",), ("agent2", "scientific-objects")),
    RouteSpec("/api/projects/{project_id}/datasets/{dataset_id}/scientific-table", promote_dataset_table, ("POST",), ("agent2", "scientific-objects")),
    RouteSpec("/api/scientific-objects/{object_id}", get_scientific_object, ("GET",), ("agent2", "scientific-objects")),
    RouteSpec("/api/scientific-objects/{object_id}/dependency-impact", get_scientific_object_dependency_impact, ("GET",), ("agent2", "scientific-objects")),
    RouteSpec("/api/scientific-objects/{object_id}", update_scientific_object, ("PATCH",), ("agent2", "scientific-objects")),
    RouteSpec("/api/scientific-objects/{object_id}/versions", list_scientific_object_versions, ("GET",), ("agent2", "scientific-objects")),
    RouteSpec("/api/scientific-objects/{object_id}/versions", create_scientific_object_version, ("POST",), ("agent2", "scientific-objects")),
    RouteSpec("/api/scientific-objects/{object_id}/versions/{version_id}", get_scientific_object_version, ("GET",), ("agent2", "scientific-objects")),
    RouteSpec("/api/scientific-objects/{object_id}/versions/{version_id}/query", query_scientific_dataset, ("POST",), ("agent2", "scientific-objects")),
    RouteSpec("/api/scientific-objects/{object_id}/versions/{version_id}/viewer", get_scientific_object_viewer, ("GET",), ("agent2", "scientific-viewers")),
    RouteSpec("/api/scientific-objects/{object_id}/relationships", list_scientific_object_relationships, ("GET",), ("agent2", "scientific-objects")),
    RouteSpec("/projects/{project_id}/research-scope", resolve_scope, ("POST",), ("research",)),
    RouteSpec("/projects", list_projects_secured, ("GET",), ("projects",), list[ProjectSummary]),
    RouteSpec("/search", search_product_secured, ("GET",), ("search",)),
    RouteSpec("/api/search", search_product_secured, ("GET",), ("search",)),
    RouteSpec("/saved-searches", list_saved_product_searches, ("GET",), ("search",)),
    RouteSpec("/saved-searches", create_saved_product_search, ("POST",), ("search",)),
    RouteSpec("/saved-searches/{saved_search_id}", update_saved_product_search, ("PATCH",), ("search",)),
    RouteSpec("/saved-searches/{saved_search_id}", delete_saved_product_search, ("DELETE",), ("search",)),
    RouteSpec("/saved-searches/{saved_search_id}/execute", execute_saved_product_search, ("POST",), ("search",)),
    RouteSpec("/api/notifications/read-state", list_notification_read_states, ("GET",), ("notifications",)),
    RouteSpec("/api/notifications/{project_id}/{job_id}/read-state", update_notification_read_state, ("PATCH",), ("notifications",)),
    RouteSpec("/projects", create_project_secured, ("POST",), ("projects",)),
    RouteSpec("/projects/bulk", bulk_project_action_secured, ("POST",), ("projects",)),
    RouteSpec("/projects/{project_id}", update_project_secured, ("PATCH",), ("projects",)),
    RouteSpec("/projects/{project_id}", delete_empty_project_secured, ("DELETE",), ("projects",)),
    RouteSpec("/projects/{project_id}/dependency-impact", get_project_dependency_impact_secured, ("GET",), ("projects",)),
    RouteSpec("/projects/{project_id}/export-manifest", get_project_export_manifest_secured, ("GET",), ("projects",)),
    RouteSpec("/projects/{project_id}/history", get_project_history, ("GET",), ("projects",)),
    RouteSpec("/projects/{project_id}/runs/{job_id}/archive", archive_project_run, ("POST",), ("projects",)),
    RouteSpec("/projects/{project_id}/runs/{job_id}/archive", restore_project_run, ("DELETE",), ("projects",)),
    RouteSpec("/datasets", list_datasets_secured, ("GET",), ("datasets",), list[DatasetSummary]),
    RouteSpec("/datasets/bulk", bulk_dataset_action_secured, ("POST",), ("datasets",)),
    RouteSpec("/datasets/demo", create_demo_dataset_secured, ("POST",), ("datasets",)),
    RouteSpec("/datasets/upload-capabilities", get_upload_capabilities, ("GET",), ("datasets",)),
    RouteSpec("/datasets/upload", upload_dataset_secured, ("POST",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}/object-store", get_dataset_object_store_secured, ("GET",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}/research-sources", get_dataset_research_sources_secured, ("GET",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}", get_dataset_secured, ("GET",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}", update_dataset_secured, ("PATCH",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}", delete_empty_dataset_secured, ("DELETE",), ("datasets",)),
    RouteSpec("/datasets/{dataset_id}/dependency-impact", get_dataset_dependency_impact_secured, ("GET",), ("datasets",)),
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
    RouteSpec("/account/models", get_user_models, ("GET",), ("account",)),
    RouteSpec("/admin/model-offerings", list_offerings, ("GET",), ("admin",)),
    RouteSpec("/admin/model-offerings/{offering_id}", save_offering, ("PUT",), ("admin",)),
    RouteSpec("/admin/accounts/{user_id}/model-plans/{plan}", save_plan_grant, ("PUT",), ("admin",)),
    RouteSpec("/account/models/connection", save_user_connection, ("PUT",), ("account",)),
    RouteSpec("/account/models/discover", discover_user_models, ("POST",), ("account",)),
    RouteSpec("/account/models/selection", save_user_model_selection, ("PUT",), ("account",)),
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
    RouteSpec("/api/tasks/feed", list_task_feed, ("GET",), ("workspaces",)),
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
        from fastapi import FastAPI, Request
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import JSONResponse
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
    from mdi_api.migration_head import (
        migration_head_guard_required,
        validate_database_migration_head,
    )

    @asynccontextmanager
    async def lifespan(_app: Any) -> Any:
        """Validate admission first, then best-effort recover durable work."""

        if migration_head_guard_required(settings):
            status = validate_database_migration_head(settings)
            if status is not None:
                logger.info(
                    "database_migration_head_verified current=%s expected=%s",
                    ",".join(status.current_heads),
                    ",".join(status.expected_heads),
                )

        if settings.agent2_startup_recovery_enabled:
            try:
                from mdi_api.research_agent.recovery import run_startup_recovery

                summary = run_startup_recovery(
                    settings,
                    stale_minutes=settings.agent2_startup_recovery_stale_minutes,
                    limit=settings.agent2_startup_recovery_limit,
                )
                logger.info(
                    "research_startup_recovery "
                    "product_candidates=%s qualification_retained=%s "
                    "accepted=%s attention=%s",
                    summary.get("productCandidates", 0),
                    summary.get("qualificationRetained", 0),
                    summary.get("accepted", 0),
                    summary.get("attention", 0),
                )
            except Exception:
                # Recovery is operational hardening, not an alternate API
                # authority. A failed wakeup remains visible in the
                # operations snapshot and must not make the API lie about
                # scientific completion.
                logger.exception("research_startup_recovery_failed")

        from mdi_api.research_agent.recovery import research_stage_watchdog

        async with research_stage_watchdog(settings):
            yield

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Controlled API boundary for material data intelligence workflows.",
        lifespan=lifespan,
    )
    from fastapi.exceptions import RequestValidationError
    from fastapi.exception_handlers import request_validation_exception_handler

    @app.exception_handler(RequestValidationError)
    async def redact_model_connection_validation(request: Request, exc: RequestValidationError):
        if request.url.path.endswith("/account/models/connection"):
            return JSONResponse(status_code=422, content={"detail": "模型连接字段无效，请检查服务地址、协议和密钥长度。"})
        return await request_validation_exception_handler(request, exc)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["ETag", "X-Idempotent-Replay", "X-Request-ID"],
    )
    from mdi_api.observability import (
        log_exception_event,
        request_correlation,
        request_id,
    )

    @app.middleware("http")
    async def operational_exception_boundary(
        request: Request,
        call_next: Callable[..., Any],
    ) -> Any:
        request.state.request_id = request_id(request.headers.get("x-request-id"))
        request.state.context_manifest_id = request.headers.get(
            "x-mdi-context-manifest-id"
        )
        try:
            response = await call_next(request)
        except Exception as exc:
            log_exception_event(
                logger,
                component="api",
                error=exc,
                correlation=request_correlation(request),
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "请求处理失败。",
                    "requestId": request.state.request_id,
                },
                headers={"X-Request-ID": request.state.request_id},
            )
        response.headers["X-Request-ID"] = request.state.request_id
        return response
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
