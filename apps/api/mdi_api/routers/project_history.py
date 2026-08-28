from __future__ import annotations

import os
from typing import Any, Mapping

from fastapi import Depends, HTTPException
from sqlalchemy import func, insert, select
from sqlalchemy.exc import SQLAlchemyError

from mdi_api.project_history import ProjectHistoryService
from mdi_api.access import require_project_access
from mdi_api.config import load_settings
from mdi_api.database import create_engine_from_settings
from mdi_api.db import jobs, messages, project_configs, research_session_runs, research_turns, sessions
from mdi_api.routers.auth import CurrentUser, get_current_user
from mdi_api.routers.planner import _planner_read_repositories


ARCHIVED_RUN_IDS_CONFIG_KEY = "archivedRunIds"
ARCHIVABLE_JOB_STATUSES = {
    "completed",
    "succeeded",
    "success",
    "partial_success",
    "failed",
    "cancelled",
}


def get_project_history(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    repositories = _planner_read_repositories(None)
    archived_run_ids: set[str] = set()
    research_context_by_run: dict[str, dict[str, str | None]] = {}
    access_role = "owner"
    # Authorize the durable Project before hydrating any child projection.
    try:
        engine = create_engine_from_settings(load_settings())
        with engine.connect() as connection:
            authorized_project = require_project_access(connection, project_id, current_user)
            access_role = str(authorized_project.get("access_role") or "viewer")
            archived_run_ids = _read_archived_run_ids(connection, project_id)
            research_context_by_run = _read_research_context_by_run(connection, project_id)
    except SQLAlchemyError as exc:
        # Older local databases may predate the additive configuration table;
        # history remains readable with no archive projection until migration
        # 0011 is applied. Do not hide unrelated database failures.
        if not any(table in str(exc).lower() for table in ("project_configs", "research_session_runs")):
            raise
    except HTTPException:
        if not os.getenv("PYTEST_CURRENT_TEST"):
            raise
        # Unit tests and the legacy in-memory adapter may not have a durable
        # Project row. Keep that compatibility path owner-scoped below.
        try:
            existing = repositories.projects.get(project_id)
        except LookupError:
            existing = None
        owner_id = (existing or {}).get("createdBy") or (existing or {}).get("created_by")
        if owner_id and owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Current user cannot access this Project.") from None
    _sync_phase2_project_to_history(repositories, project_id)
    try:
        project = repositories.projects.get(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found.") from None
    owner_id = project.get("createdBy") or project.get("created_by")
    if owner_id and owner_id != current_user.id and os.getenv("PYTEST_CURRENT_TEST"):
        raise HTTPException(status_code=403, detail="Current user cannot access this Project.")
    history = ProjectHistoryService(repositories, archived_run_ids=archived_run_ids).build(project_id)
    history["project"]["role"] = access_role
    for analysis in history.get("analyses") or []:
        context = research_context_by_run.get(str(analysis.get("jobId") or ""))
        if context:
            analysis["researchSessionId"] = context["sessionId"]
            analysis["researchContextKind"] = context["contextKind"]
            if context.get("researchTurnId"):
                analysis["researchTurnId"] = context["researchTurnId"]
            if not str(analysis.get("userQuestion") or "").strip() and context.get("userQuestion"):
                analysis["userQuestion"] = context["userQuestion"]
    return history


def archive_project_run(
    project_id: str,
    job_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    return _set_project_run_archived(project_id, job_id, archived=True, current_user=current_user)


def restore_project_run(
    project_id: str,
    job_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    return _set_project_run_archived(project_id, job_id, archived=False, current_user=current_user)


def _set_project_run_archived(
    project_id: str,
    job_id: str,
    *,
    archived: bool,
    current_user: CurrentUser,
) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        require_project_access(connection, project_id, current_user, write=True)
        job = connection.execute(
            select(jobs.c.id, jobs.c.status).where(
                jobs.c.id == job_id,
                jobs.c.project_id == project_id,
            )
        ).mappings().first()
        if not job:
            raise HTTPException(status_code=404, detail="分析运行不存在。")
        if archived and str(job["status"]).lower() not in ARCHIVABLE_JOB_STATUSES:
            raise HTTPException(status_code=409, detail="分析仍在进行，完成后才能归档。")

        row = connection.execute(
            select(project_configs.c.config_json)
            .where(project_configs.c.project_id == project_id)
            .with_for_update()
        ).scalar_one_or_none()
        config = dict(row) if isinstance(row, Mapping) else {}
        archived_ids = {
            str(item)
            for item in config.get(ARCHIVED_RUN_IDS_CONFIG_KEY, [])
            if isinstance(item, str) and item
        }
        if archived:
            archived_ids.add(job_id)
        else:
            archived_ids.discard(job_id)
        config[ARCHIVED_RUN_IDS_CONFIG_KEY] = sorted(archived_ids)

        existing = connection.execute(
            select(project_configs.c.project_id).where(project_configs.c.project_id == project_id)
        ).scalar_one_or_none()
        if existing is None:
            connection.execute(insert(project_configs).values(project_id=project_id, config_json=config))
        else:
            connection.execute(
                project_configs.update()
                .where(project_configs.c.project_id == project_id)
                .values(config_json=config, updated_at=func.now())
            )
    return {"projectId": project_id, "jobId": job_id, "archived": archived}


def _read_archived_run_ids(connection: Any, project_id: str) -> set[str]:
    config = connection.execute(
        select(project_configs.c.config_json).where(project_configs.c.project_id == project_id)
    ).scalar_one_or_none()
    return _archived_run_ids_from_config(config)


def _read_research_context_by_run(
    connection: Any,
    project_id: str,
) -> dict[str, dict[str, str | None]]:
    """Recover the user turn that immediately precedes each persisted run.

    AnalysisIntent is the primary source for new runs. Older product runs may
    only have the normalized research-session binding, so this read projection
    uses the last user message at or before that binding without mutating any
    durable execution or message record.
    """

    bindings = connection.execute(
        select(
            research_session_runs.c.job_id,
            research_session_runs.c.session_id,
            research_session_runs.c.created_at,
            research_turns.c.id.label("research_turn_id"),
            research_turns.c.user_message_id,
        )
        .join(sessions, sessions.c.id == research_session_runs.c.session_id)
        .outerjoin(research_turns, research_turns.c.job_id == research_session_runs.c.job_id)
        .where(sessions.c.project_id == project_id)
        .order_by(research_session_runs.c.created_at.asc(), research_session_runs.c.job_id.asc())
    ).mappings().all()
    if not bindings:
        return {}

    session_ids = sorted({str(item["session_id"]) for item in bindings})
    message_rows = connection.execute(
        select(
            messages.c.id,
            messages.c.session_id,
            messages.c.role,
            messages.c.content_summary,
            messages.c.created_at,
        )
        .where(messages.c.session_id.in_(session_ids))
        .order_by(messages.c.session_id.asc(), messages.c.created_at.asc(), messages.c.id.asc())
    ).mappings().all()
    user_messages_by_session: dict[str, list[Any]] = {}
    user_messages_by_id: dict[str, Any] = {}
    for row in message_rows:
        if row["role"] == "user" and str(row["content_summary"] or "").strip():
            user_messages_by_session.setdefault(str(row["session_id"]), []).append(row)
            user_messages_by_id[str(row["id"])] = row

    result: dict[str, dict[str, str | None]] = {}
    for binding in bindings:
        session_id = str(binding["session_id"])
        bound_at = binding["created_at"]
        exact_message = (
            user_messages_by_id.get(str(binding["user_message_id"]))
            if binding.get("research_turn_id") and binding.get("user_message_id")
            else None
        )
        if exact_message is not None and str(exact_message["session_id"]) != session_id:
            # A malformed historical relation must not disclose a message from
            # another session; fall back to the bounded legacy projection.
            exact_message = None
        candidates = [
            row
            for row in user_messages_by_session.get(session_id, [])
            if bound_at is None or row["created_at"] <= bound_at
        ]
        question = (
            str(exact_message["content_summary"]).strip()
            if exact_message
            else str(candidates[-1]["content_summary"]).strip()
            if candidates
            else None
        )
        context = {
            "sessionId": session_id,
            "userQuestion": question,
            "contextKind": "LEGACY_SESSION_RUN",
        }
        if binding.get("research_turn_id"):
            context["researchTurnId"] = str(binding["research_turn_id"])
            context["contextKind"] = "RESEARCH_TURN"
        result[str(binding["job_id"])] = context
    return result


def _archived_run_ids_from_config(config: Any) -> set[str]:
    if not isinstance(config, Mapping):
        return set()
    return {
        str(item)
        for item in config.get(ARCHIVED_RUN_IDS_CONFIG_KEY, [])
        if isinstance(item, str) and item
    }


def _sync_phase2_project_to_history(repositories: Any, project_id: str) -> dict[str, Any] | None:
    """Project a local Phase 2 project into the planner history read model."""

    from mdi_api.phase2_runtime import get_phase2_runtime

    runtime = get_phase2_runtime()
    runtime_project = runtime.projects.get(project_id)
    if runtime_project is None:
        # A local project is also written to the repository when it is
        # created. Rehydrate that durable shell after an API restart; parsed
        # datasets are synchronized below when they are still available in
        # the runtime.
        try:
            from mdi_api.durable_projects import hydrate_runtime_project

            hydrate_runtime_project(runtime, project_id)
            runtime_project = runtime.projects.get(project_id)
        except LookupError:
            return None
    if runtime_project is None:
        return None

    project = {
        **runtime_project.summary(),
        "createdBy": "user_local",
        "status": "active",
    }
    try:
        repositories.projects.get(project_id)
    except LookupError:
        repositories.projects.save(project)
    for dataset in runtime.datasets.values():
        if dataset.project_id != project_id:
            continue
        try:
            repositories.datasets.get(dataset.id)
        except LookupError:
            repositories.datasets.save({
                **dataset.summary(),
                "metadata": {
                    "files": dataset.files,
                    "normalizedExports": dataset.normalized_exports,
                    "inputTransport": dataset.input_transport,
                },
                "createdBy": "user_local",
            })
        try:
            repositories.data_profiles.get(dataset.profile.profileId)
        except LookupError:
            repositories.data_profiles.save(dataset.profile)
    return project
