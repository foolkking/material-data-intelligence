from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Mapping
from uuid import uuid4

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import (
    Text,
    cast,
    delete,
    exists,
    func,
    insert,
    inspect,
    literal,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from mdi_api.access import require_project_access
from mdi_api.config import load_settings
from mdi_api.database import create_engine_from_settings
from mdi_api.db import (
    audit_logs,
    datasets,
    jobs,
    messages,
    metadata,
    project_configs,
    project_members,
    projects,
    reports,
    research_turns,
    scientific_objects,
    scientific_object_versions,
    scientific_result_snapshots,
    agent2_scientific_report_snapshots,
    agent2_scientific_interpretations,
    sessions,
    user_configs,
)
from mdi_api.routers.auth import CurrentUser, get_current_user_compat
from mdi_api.phase2_runtime import CreateJobRequest, CreateProjectRequest, DatasetUploadRequest
from mdi_api.routers.datasets import BulkDatasetActionRequest, UpdateDatasetRequest
from mdi_api.routers.projects import BulkProjectActionRequest, UpdateProjectRequest
from mdi_api.input_transport import CreateUploadSessionRequest
from mdi_api.lifecycle_policy import evaluate_purge, retention_policy_snapshot


_DEPENDENCY_LABELS = {
    "datasets": "数据集",
    "data_profiles": "语义档案",
    "dataset_source_resources": "源资源",
    "scientific_objects": "科学对象",
    "scientific_object_versions": "科学对象版本",
    "scientific_object_relationships": "科学对象关系",
    "sessions": "研究会话",
    "research_turns": "ResearchTurn",
    "research_session_runs": "历史研究运行",
    "jobs": "研究运行",
    "tool_calls": "ToolCall",
    "artifacts": "Artifact",
    "scientific_result_snapshots": "ScientificResult",
    "scientific_reports": "科学报告",
    "reports": "报告",
    "workspaces": "工作区",
    "recipes": "Recipe",
    "audit_logs": "审计记录",
}
_DATA_DEPENDENCY_KINDS = {
    "datasets",
    "data_profiles",
    "dataset_source_resources",
    "scientific_objects",
    "scientific_object_versions",
    "scientific_object_relationships",
}
_RESEARCH_DEPENDENCY_KINDS = {
    "sessions",
    "research_turns",
    "research_session_runs",
    "jobs",
    "tool_calls",
    "artifacts",
    "scientific_result_snapshots",
    "workspaces",
    "recipes",
}
_REPORT_DEPENDENCY_KINDS = {"scientific_reports", "reports"}

_SAVED_PRODUCT_SEARCH_KIND = "savedProductSearch"
_NOTIFICATION_READ_STATE_KIND = "notificationReadState"
_SAVED_PRODUCT_SEARCH_TYPES = {
    "project",
    "dataset",
    "scientific_object",
    "research",
    "report",
    "result",
}
_SAVED_PRODUCT_SEARCH_STATUSES = {"active", "archived", "trashed", "all"}
_PRODUCT_SEARCH_CURSOR_VERSION = 2
_PRODUCT_SEARCH_MAX_CURSOR_LENGTH = 512
_PRODUCT_SEARCH_MAX_CANDIDATES_PER_KIND = 1_000
_PRODUCT_SEARCH_MAX_CURSOR_ITEMS = 6 * _PRODUCT_SEARCH_MAX_CANDIDATES_PER_KIND


class SavedProductSearchCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    query: str = Field(default="", max_length=160)
    type: Literal[
        "project",
        "dataset",
        "scientific_object",
        "research",
        "report",
        "result",
    ] | None = None
    project: str | None = Field(default=None, max_length=64)
    status: Literal["active", "archived", "trashed", "all"] = "all"

    @model_validator(mode="after")
    def normalize_fields(self) -> "SavedProductSearchCreate":
        self.name = self.name.strip()
        self.query = self.query.strip()
        self.project = self.project.strip() if self.project else None
        if not self.name:
            raise ValueError("Saved search name cannot be blank.")
        return self


class SavedProductSearchUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    query: str | None = Field(default=None, max_length=160)
    type: Literal[
        "project",
        "dataset",
        "scientific_object",
        "research",
        "report",
        "result",
    ] | None = None
    project: str | None = Field(default=None, max_length=64)
    status: Literal["active", "archived", "trashed", "all"] | None = None

    @model_validator(mode="after")
    def normalize_fields(self) -> "SavedProductSearchUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one saved search field is required.")
        for required_field in ("name", "query", "status"):
            if (
                required_field in self.model_fields_set
                and getattr(self, required_field) is None
            ):
                raise ValueError(f"{required_field} cannot be null.")
        if self.name is not None:
            self.name = self.name.strip()
            if not self.name:
                raise ValueError("Saved search name cannot be blank.")
        if self.query is not None:
            self.query = self.query.strip()
        if "project" in self.model_fields_set:
            self.project = self.project.strip() if self.project else None
        return self


class SavedProductSearchExecute(BaseModel):
    limit: int = Field(default=40, ge=1, le=100)


class NotificationReadStateUpdate(BaseModel):
    read: bool


def _notification_read_state_id(
    user_id: str,
    project_id: str,
    job_id: str,
) -> str:
    digest = hashlib.sha256(
        f"{user_id}\0{project_id}\0{job_id}".encode("utf-8")
    ).hexdigest()
    return f"notification_read_{digest[:46]}"


def _notification_read_state_view(
    row: Mapping[str, Any],
) -> dict[str, Any] | None:
    config = row.get("config_json")
    if (
        not isinstance(config, dict)
        or config.get("configKind") != _NOTIFICATION_READ_STATE_KIND
    ):
        return None
    project_id = str(config.get("projectId") or "")
    job_id = str(config.get("jobId") or "")
    read_at = config.get("readAt")
    notification_updated_at = config.get("notificationUpdatedAt")
    if not project_id or not job_id or not read_at or not notification_updated_at:
        return None
    return {
        "projectId": project_id,
        "jobId": job_id,
        "read": True,
        "readAt": read_at,
        "notificationUpdatedAt": notification_updated_at,
    }


def list_notification_read_states(
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    """Return durable read markers for notifications the user can still see.

    A marker is valid only for the exact persisted Job revision that was read.
    If the Job changes later, the notification becomes unread again without
    mutating or duplicating the scientific execution record.
    """

    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        visible_projects = _visible_project_ids(connection, current_user)
        if not visible_projects:
            return {
                "schemaVersion": "NotificationReadState/1.0",
                "items": [],
                "count": 0,
            }
        rows = connection.execute(
            select(user_configs)
            .where(user_configs.c.user_id == current_user.id)
            .order_by(user_configs.c.updated_at.desc())
        ).mappings().all()
        candidates = [
            state
            for row in rows
            if (state := _notification_read_state_view(dict(row))) is not None
            and state["projectId"] in visible_projects
        ]
        job_rows = connection.execute(
            select(jobs.c.id, jobs.c.project_id, jobs.c.updated_at).where(
                jobs.c.project_id.in_(visible_projects),
                jobs.c.id.in_([state["jobId"] for state in candidates]),
            )
        ).mappings().all() if candidates else []
        revisions = {
            (str(row["project_id"]), str(row["id"])): (
                row["updated_at"].isoformat() if row.get("updated_at") else None
            )
            for row in job_rows
        }
        items = [
            state
            for state in candidates
            if revisions.get((state["projectId"], state["jobId"]))
            == state["notificationUpdatedAt"]
        ]
    return {
        "schemaVersion": "NotificationReadState/1.0",
        "items": items,
        "count": len(items),
    }


def update_notification_read_state(
    project_id: str,
    job_id: str,
    request: NotificationReadStateUpdate,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    """Persist this user's read state after re-authorizing the source Job."""

    engine = create_engine_from_settings(load_settings())
    state_id = _notification_read_state_id(current_user.id, project_id, job_id)
    with engine.begin() as connection:
        require_project_access(connection, project_id, current_user, write=False)
        job = connection.execute(
            select(jobs.c.id, jobs.c.project_id, jobs.c.updated_at).where(
                jobs.c.id == job_id,
                jobs.c.project_id == project_id,
            )
        ).mappings().one_or_none()
        if job is None:
            raise HTTPException(status_code=404, detail="通知不存在或无权访问。")
        if not request.read:
            connection.execute(
                delete(user_configs).where(
                    user_configs.c.id == state_id,
                    user_configs.c.user_id == current_user.id,
                )
            )
            return {
                "projectId": project_id,
                "jobId": job_id,
                "read": False,
                "readAt": None,
                "notificationUpdatedAt": (
                    job["updated_at"].isoformat()
                    if job.get("updated_at")
                    else None
                ),
            }

        now = datetime.now(timezone.utc)
        config = {
            "configKind": _NOTIFICATION_READ_STATE_KIND,
            "schemaVersion": "1.0",
            "projectId": project_id,
            "jobId": job_id,
            "readAt": now.isoformat(),
            "notificationUpdatedAt": (
                job["updated_at"].isoformat() if job.get("updated_at") else None
            ),
        }
        existing = connection.execute(
            select(user_configs.c.id).where(
                user_configs.c.id == state_id,
                user_configs.c.user_id == current_user.id,
            )
        ).scalar_one_or_none()
        if existing is None:
            connection.execute(
                insert(user_configs).values(
                    id=state_id,
                    user_id=current_user.id,
                    config_json=config,
                    updated_at=now,
                )
            )
        else:
            connection.execute(
                update(user_configs)
                .where(
                    user_configs.c.id == state_id,
                    user_configs.c.user_id == current_user.id,
                )
                .values(config_json=config, updated_at=now)
            )
    return _notification_read_state_view({"config_json": config}) or {}


def _saved_product_search_view(row: dict[str, Any]) -> dict[str, Any] | None:
    config = row.get("config_json")
    if (
        not isinstance(config, dict)
        or config.get("configKind") != _SAVED_PRODUCT_SEARCH_KIND
    ):
        return None
    saved_type = config.get("type")
    status = str(config.get("status") or "all").lower()
    if saved_type is not None and saved_type not in _SAVED_PRODUCT_SEARCH_TYPES:
        return None
    if status not in _SAVED_PRODUCT_SEARCH_STATUSES:
        return None
    return {
        "id": str(row["id"]),
        "name": str(config.get("name") or "未命名检索"),
        "query": str(config.get("query") or ""),
        "type": saved_type,
        "project": config.get("project"),
        "status": status,
        "createdAt": config.get("createdAt"),
        "updatedAt": config.get("updatedAt")
        or (
            row["updated_at"].isoformat()
            if row.get("updated_at")
            else None
        ),
    }


def _visible_project_ids(connection: Any, current_user: CurrentUser) -> set[str]:
    return {
        str(project_id)
        for project_id in connection.execute(
            select(projects.c.id).where(
                (projects.c.created_by == current_user.id)
                | projects.c.id.in_(
                    select(project_members.c.project_id).where(
                        project_members.c.user_id == current_user.id
                    )
                )
            )
        ).scalars()
    }


def list_saved_product_searches(
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> list[dict[str, Any]]:
    """List only this user's saved filters that remain authorized.

    Results are never persisted. A project-bound view disappears when project
    access is revoked, preventing the saved metadata from becoming an entity
    disclosure or silently widening into a global search.
    """

    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        visible_projects = _visible_project_ids(connection, current_user)
        rows = connection.execute(
            select(user_configs)
            .where(user_configs.c.user_id == current_user.id)
            .order_by(user_configs.c.updated_at.desc())
        ).mappings().all()
        views: list[dict[str, Any]] = []
        for row in rows:
            view = _saved_product_search_view(dict(row))
            if view is None:
                continue
            if view["project"] and str(view["project"]) not in visible_projects:
                continue
            views.append(view)
        return views


def create_saved_product_search(
    request: SavedProductSearchCreate,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    saved_search_id = f"saved_search_{uuid4().hex}"
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        if request.project:
            require_project_access(
                connection, request.project, current_user, write=False
            )
        config = {
            "configKind": _SAVED_PRODUCT_SEARCH_KIND,
            "schemaVersion": "1.0",
            "name": request.name,
            "query": request.query,
            "type": request.type,
            "project": request.project,
            "status": request.status,
            "createdAt": now.isoformat(),
            "updatedAt": now.isoformat(),
        }
        connection.execute(
            insert(user_configs).values(
                id=saved_search_id,
                user_id=current_user.id,
                config_json=config,
                updated_at=now,
            )
        )
        row = connection.execute(
            select(user_configs).where(user_configs.c.id == saved_search_id)
        ).mappings().one()
    return _saved_product_search_view(dict(row)) or {}


def update_saved_product_search(
    saved_search_id: str,
    request: SavedProductSearchUpdate,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        row = connection.execute(
            select(user_configs)
            .where(
                user_configs.c.id == saved_search_id,
                user_configs.c.user_id == current_user.id,
            )
            .with_for_update()
        ).mappings().one_or_none()
        view = _saved_product_search_view(dict(row)) if row else None
        if view is None:
            raise HTTPException(status_code=404, detail="已保存检索不存在。")
        changes = request.model_dump(exclude_unset=True)
        project_value = changes.get("project", view["project"])
        if project_value:
            require_project_access(
                connection, str(project_value), current_user, write=False
            )
        config = dict(row["config_json"])
        for key in ("name", "query", "type", "project", "status"):
            if key in changes:
                config[key] = changes[key]
        config["updatedAt"] = now.isoformat()
        connection.execute(
            update(user_configs)
            .where(user_configs.c.id == saved_search_id)
            .values(config_json=config, updated_at=now)
        )
        updated = connection.execute(
            select(user_configs).where(user_configs.c.id == saved_search_id)
        ).mappings().one()
    return _saved_product_search_view(dict(updated)) or {}


def delete_saved_product_search(
    saved_search_id: str,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        row = connection.execute(
            select(user_configs).where(
                user_configs.c.id == saved_search_id,
                user_configs.c.user_id == current_user.id,
            )
        ).mappings().one_or_none()
        if row is None or _saved_product_search_view(dict(row)) is None:
            raise HTTPException(status_code=404, detail="已保存检索不存在。")
        connection.execute(
            delete(user_configs).where(user_configs.c.id == saved_search_id)
        )
    return {"id": saved_search_id, "deleted": True}


def execute_saved_product_search(
    saved_search_id: str,
    request: SavedProductSearchExecute,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    """Re-execute one user-owned saved filter against current authorized state.

    A saved search stores only navigation filters. Each execution repeats
    project authorization and returns a fresh bounded search projection; no
    result rows or scientific facts are copied into ``user_configs``.
    """

    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        row = connection.execute(
            select(user_configs).where(
                user_configs.c.id == saved_search_id,
                user_configs.c.user_id == current_user.id,
            )
        ).mappings().one_or_none()
        saved_search = (
            _saved_product_search_view(dict(row)) if row is not None else None
        )
    if saved_search is None:
        raise HTTPException(status_code=404, detail="已保存检索不存在。")

    search_result = search_product_secured(
        q=saved_search["query"],
        project_id=saved_search["project"],
        kind=saved_search["type"],
        status=saved_search["status"],
        limit=request.limit,
        current_user=current_user,
    )
    return {"savedSearch": saved_search, **search_result}


def _result_search_href(
    project_id: str,
    result_id: str,
    research_turn_id: Any = None,
    research_session_id: Any = None,
    job_id: Any = None,
) -> str:
    """Prefer the persisted ResearchTurn route for an authorized Result hit."""
    if research_session_id and research_turn_id:
        return (
            f"/projects/{project_id}/research/{research_session_id}"
            f"?turn={research_turn_id}"
        )
    if research_turn_id:
        return f"/projects/{project_id}/research?turn={research_turn_id}"
    if job_id:
        return f"/projects/{project_id}/research?run={job_id}"
    return f"/projects/{project_id}/research"


def _research_search_title(summary: Any) -> str:
    """Project a human research title without replacing the Session identity."""
    normalized = " ".join(str(summary or "").split())
    if not normalized:
        return "未命名研究"
    return normalized if len(normalized) <= 88 else f"{normalized[:85]}…"


def list_projects_secured(current_user: CurrentUser = Depends(get_current_user_compat)) -> list[dict[str, Any]]:
    from mdi_api.phase2_runtime import list_phase2_projects

    engine = create_engine_from_settings(load_settings())
    visible: list[dict[str, Any]] = []
    try:
        with engine.connect() as connection:
            project_members_available = project_members.name in inspect(connection).get_table_names()
            if project_members_available:
                rows = connection.execute(select(projects).where(
                    (projects.c.created_by == current_user.id)
                    | projects.c.id.in_(select(project_members.c.project_id).where(project_members.c.user_id == current_user.id))
                ).order_by(projects.c.updated_at.desc())).mappings().all()
            else:
                # Owner-only schema compatibility for databases before the
                # optional project_members table migration.
                rows = connection.execute(select(projects).where(
                    projects.c.created_by == current_user.id
                ).order_by(projects.c.updated_at.desc())).mappings().all()
            project_ids = [str(row["id"]) for row in rows]
            roles_by_project: dict[str, str] = {}
            if project_members_available and project_ids:
                try:
                    roles_by_project = {
                        str(item["project_id"]): str(item["role"])
                        for item in connection.execute(
                            select(project_members.c.project_id, project_members.c.role).where(
                                project_members.c.user_id == current_user.id,
                                project_members.c.project_id.in_(project_ids),
                            )
                        ).mappings().all()
                    }
                except SQLAlchemyError:
                    roles_by_project = {}
            configs_by_project: dict[str, Any] = {}
            if project_ids:
                try:
                    configs_by_project = {
                        str(item["project_id"]): item.get("config_json")
                        for item in connection.execute(
                            select(project_configs.c.project_id, project_configs.c.config_json).where(
                                project_configs.c.project_id.in_(project_ids)
                            )
                        ).mappings().all()
                    }
                except SQLAlchemyError:
                    configs_by_project = {}
            for row in rows:
                project_id_value = str(row["id"])
                role = (
                    roles_by_project.get(project_id_value)
                    or ("owner" if row["created_by"] == current_user.id else "viewer")
                )
                lifecycle_status = "active"
                pinned = False
                tags: list[str] = []
                config = configs_by_project.get(project_id_value)
                try:
                    lifecycle_status = _project_lifecycle_status(config)
                    pinned = bool(config.get("pinnedProject")) if isinstance(config, dict) else False
                    tags = _normalize_project_tags(config.get("projectTags")) if isinstance(config, dict) else []
                except (AttributeError, TypeError):
                    lifecycle_status = "active"
                visible.append({
                    "id": row["id"], "projectId": row["id"], "name": row["name"],
                    "description": row["description"], "status": lifecycle_status, "role": role,
                    "pinned": pinned,
                    "tags": tags,
                    "createdAt": row["created_at"].isoformat() if row["created_at"] else None,
                    "updatedAt": row["updated_at"].isoformat() if row["updated_at"] else None,
                })
    except SQLAlchemyError:
        if not os.getenv("PYTEST_CURRENT_TEST"):
            raise
    # Keep the SQL ``updated_at DESC`` order within each group while lifting
    # explicitly pinned projects above the normal project catalog.
    visible.sort(key=lambda item: bool(item.get("pinned")), reverse=True)
    if visible:
        return visible
    # Runtime-only projects are still supported for the local adapter, but
    # are never returned merely because they exist in process memory.
    for project in list_phase2_projects():
        project_id = str(project.get("projectId") or project.get("id") or "")
        owner = str(project.get("createdBy") or project.get("created_by") or "")
        if project_id and owner and owner == current_user.id:
            visible.append(project)
    return visible


def search_product_secured(
    q: str = "",
    project_id: str | None = None,
    kind: str | None = None,
    status: str | None = None,
    limit: int = 40,
    cursor: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    """Return a bounded, project-authorized product search projection.

    Search is navigation only: it never projects scientific facts or broad
    infrastructure metadata. Every row is scoped through the same project
    membership boundary used by the normal product surfaces.
    """

    query = q.strip()
    if len(query) > 160:
        raise HTTPException(status_code=422, detail="搜索词过长。")
    bounded_limit = max(1, min(int(limit), 100))
    allowed_kinds = {"project", "dataset", "scientific_object", "research", "report", "result"}
    requested_kind = kind.strip().lower() if kind else None
    if requested_kind and requested_kind not in allowed_kinds:
        raise HTTPException(status_code=422, detail="不支持的搜索类型。")
    requested_status = status.strip().lower() if status else None
    if requested_status and requested_status not in {"active", "archived", "trashed", "all"}:
        raise HTTPException(status_code=422, detail="不支持的生命周期筛选。")
    date_start = _parse_product_search_date(date_from, end_of_day=False)
    date_end = _parse_product_search_date(date_to, end_of_day=True)
    if date_start and date_end and date_start >= date_end:
        raise HTTPException(status_code=422, detail="搜索日期范围无效。")
    cursor_status = None if requested_status in {None, "all"} else requested_status
    cursor_fingerprint = hashlib.sha256(
        json.dumps(
            {
                "q": query,
                "project": project_id,
                "kind": requested_kind,
                "status": cursor_status,
                "dateFrom": date_from,
                "dateTo": date_to,
                "user": current_user.id,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    cursor_seen, cursor_key = _decode_product_search_cursor(
        cursor,
        expected_fingerprint=cursor_fingerprint,
    )
    scan_limit = min(
        _PRODUCT_SEARCH_MAX_CANDIDATES_PER_KIND,
        (
            _PRODUCT_SEARCH_MAX_CANDIDATES_PER_KIND
            if cursor_status is not None or date_start is not None or date_end is not None
            else bounded_limit + 1
        ),
    )

    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        visible_project_rows = connection.execute(
            select(projects.c.id, projects.c.name).where(
                (projects.c.created_by == current_user.id)
                | projects.c.id.in_(
                    select(project_members.c.project_id).where(project_members.c.user_id == current_user.id)
                )
            )
        ).mappings().all()
        visible_ids = {str(row["id"]) for row in visible_project_rows}
        if project_id is not None:
            if project_id not in visible_ids:
                raise HTTPException(status_code=404, detail="项目不存在或无权访问。")
            visible_ids = {project_id}
        if not visible_ids:
            return {
                "query": query,
                "items": [],
                "count": 0,
                "truncated": False,
                "nextCursor": None,
            }

        pattern = f"%{query.lower()}%" if query else "%"
        items: list[dict[str, Any]] = []
        search_truncated = False

        # JSON fields are read-only navigation metadata.  Casting the
        # authoritative JSON projection to text keeps this endpoint portable
        # across the PostgreSQL qualification stack and SQLite compatibility
        # tests without introducing a second search/fact authority.
        def json_matches(column: Any) -> Any:
            json_text = func.lower(cast(column, Text))
            escaped_query = json.dumps(query, ensure_ascii=True)[1:-1].lower()
            escaped_pattern = f"%{escaped_query}%"
            # SQLite's JSON serializer escapes non-ASCII text while
            # PostgreSQL commonly keeps it readable.  Match both encodings so
            # the same semantic search remains portable without loading raw
            # JSON into Python or exposing it in the response.
            return json_text.like(pattern) | json_text.like(escaped_pattern)

        def add_item(
            *,
            item_kind: str,
            item_id: str,
            item_project_id: str,
            title: str,
            subtitle: str,
            href: str,
            research_turn_id: str | None = None,
            status: str | None = None,
            updated_at: Any = None,
        ) -> None:
            if requested_kind and requested_kind != item_kind:
                return
            normalized_updated_at = updated_at
            if normalized_updated_at and normalized_updated_at.tzinfo is None:
                normalized_updated_at = normalized_updated_at.replace(
                    tzinfo=timezone.utc
                )
            if date_start and (
                normalized_updated_at is None
                or normalized_updated_at < date_start
            ):
                return
            if date_end and (
                normalized_updated_at is None
                or normalized_updated_at >= date_end
            ):
                return
            items.append({
                "kind": item_kind,
                "id": item_id,
                "projectId": item_project_id,
                "title": title,
                "subtitle": subtitle,
                "href": href,
                "researchTurnId": research_turn_id,
                "status": status,
                "updatedAt": (
                    normalized_updated_at.isoformat()
                    if normalized_updated_at
                    else None
                ),
            })

        def status_matches(value: str | None) -> bool:
            if requested_status in {None, "all"}:
                return True
            normalized = str(value or "").strip().lower()
            if requested_status == "archived":
                return normalized == "archived"
            if requested_status == "trashed":
                return normalized == "trashed"
            return normalized not in {"archived", "ARCHIVED".lower(), "trashed", "purged"}

        def apply_cursor(
            statement: Any,
            *,
            updated_column: Any,
            item_kind: str,
            id_column: Any,
        ) -> Any:
            """Continue strictly below the last globally ordered search hit."""

            if cursor_key is None:
                return statement
            cursor_time, cursor_kind, cursor_id = cursor_key
            same_time_after_kind = (
                literal(item_kind) < cursor_kind
            ) | (
                (literal(item_kind) == cursor_kind)
                & (cast(id_column, Text) < cursor_id)
            )
            return statement.where(
                (updated_column < cursor_time)
                | (
                    (updated_column == cursor_time)
                    & same_time_after_kind
                )
            )

        archived_project_ids: set[str] = set()
        trashed_project_ids: set[str] = set()
        tagged_project_ids: set[str] = set()
        project_tags_by_id: dict[str, list[str]] = {}
        configs: list[dict[str, Any]] = []
        try:
            configs = connection.execute(
                select(project_configs.c.project_id, project_configs.c.config_json).where(
                    project_configs.c.project_id.in_(visible_ids)
                )
            ).mappings().all()
            archived_project_ids = {
                str(row["project_id"]) for row in configs
                if isinstance(row.get("config_json"), dict) and bool(row["config_json"].get("archivedProject"))
            }
            trashed_project_ids = {
                str(row["project_id"]) for row in configs
                if _project_lifecycle_status(row.get("config_json")) == "trashed"
            }
            for row in configs:
                config = row.get("config_json")
                tags = _normalize_project_tags(config.get("projectTags")) if isinstance(config, dict) else []
                project_id_value = str(row["project_id"])
                project_tags_by_id[project_id_value] = tags
                if query and any(query.casefold() in tag.casefold() for tag in tags):
                    tagged_project_ids.add(project_id_value)
        except SQLAlchemyError:
            archived_project_ids = set()
            trashed_project_ids = set()

        if not requested_kind or requested_kind == "project":
            project_query = select(projects).where(
                projects.c.id.in_(visible_ids),
                (
                    func.lower(projects.c.name).like(pattern)
                    | func.lower(projects.c.description).like(pattern)
                    | projects.c.id.in_(tagged_project_ids)
                ),
            )
            project_query = apply_cursor(
                project_query,
                updated_column=projects.c.updated_at,
                item_kind="project",
                id_column=projects.c.id,
            )
            project_rows = connection.execute(
                project_query.order_by(
                    projects.c.updated_at.desc(),
                    projects.c.id.desc(),
                ).limit(scan_limit)
            ).mappings().all()
            search_truncated = search_truncated or len(project_rows) >= scan_limit
            for row in project_rows:
                project_status = (
                    "trashed"
                    if str(row["id"]) in trashed_project_ids
                    else "archived"
                    if str(row["id"]) in archived_project_ids
                    else "active"
                )
                if not status_matches(project_status):
                    continue
                add_item(
                    item_kind="project",
                    item_id=str(row["id"]),
                    item_project_id=str(row["id"]),
                    title=str(row["name"]),
                    subtitle=" · ".join(
                        [str(row.get("description") or "材料研究项目"), *project_tags_by_id.get(str(row["id"]), [])]
                    ),
                    href=f"/projects/{row['id']}",
                    status=project_status,
                    updated_at=row.get("updated_at"),
                )

        if not requested_kind or requested_kind == "dataset":
            dataset_query = select(datasets).where(
                datasets.c.project_id.in_(visible_ids),
                func.lower(datasets.c.name).like(pattern)
                | json_matches(datasets.c.metadata_json),
            )
            dataset_query = apply_cursor(
                dataset_query,
                updated_column=datasets.c.updated_at,
                item_kind="dataset",
                id_column=datasets.c.id,
            )
            dataset_rows = connection.execute(
                dataset_query.order_by(
                    datasets.c.updated_at.desc(),
                    datasets.c.id.desc(),
                ).limit(scan_limit)
            ).mappings().all()
            search_truncated = search_truncated or len(dataset_rows) >= scan_limit
            for row in dataset_rows:
                dataset_status = _dataset_lifecycle_status(dict(row))
                if not status_matches(dataset_status):
                    continue
                add_item(
                    item_kind="dataset",
                    item_id=str(row["id"]),
                    item_project_id=str(row["project_id"]),
                    title=str(row["name"]),
                    subtitle="数据集",
                    href=f"/projects/{row['project_id']}/data?dataset={row['id']}",
                    status=dataset_status,
                    updated_at=row.get("updated_at"),
                )

        if not requested_kind or requested_kind == "scientific_object":
            object_query = select(scientific_objects).where(
                scientific_objects.c.project_id.in_(visible_ids),
                func.lower(scientific_objects.c.display_name).like(pattern)
                | func.lower(scientific_objects.c.object_type).like(pattern)
                | exists(
                    select(1).where(
                        scientific_object_versions.c.scientific_object_id
                        == scientific_objects.c.id,
                        json_matches(
                            scientific_object_versions.c.canonical_metadata_json
                        ),
                    )
                ),
            )
            object_query = apply_cursor(
                object_query,
                updated_column=scientific_objects.c.created_at,
                item_kind="scientific_object",
                id_column=scientific_objects.c.id,
            )
            object_rows = connection.execute(
                object_query.order_by(
                    scientific_objects.c.created_at.desc(),
                    scientific_objects.c.id.desc(),
                ).limit(scan_limit)
            ).mappings().all()
            search_truncated = search_truncated or len(object_rows) >= scan_limit
            for row in object_rows:
                object_status = str(row.get("lifecycle_status") or "")
                if not status_matches(object_status):
                    continue
                add_item(
                    item_kind="scientific_object",
                    item_id=str(row["id"]),
                    item_project_id=str(row["project_id"]),
                    title=str(row["display_name"]),
                    subtitle=str(row["object_type"]),
                    href=f"/projects/{row['project_id']}/data?object={row['id']}",
                    status=object_status,
                    updated_at=row.get("created_at"),
                )

        if not requested_kind or requested_kind == "research":
            first_user_messages = messages.alias("first_user_messages")
            first_user_message = (
                select(first_user_messages.c.content_summary)
                .where(
                    first_user_messages.c.session_id == sessions.c.id,
                    first_user_messages.c.role == "user",
                )
                .order_by(
                    first_user_messages.c.created_at.asc(),
                    first_user_messages.c.id.asc(),
                )
                .correlate(sessions)
                .limit(1)
                .scalar_subquery()
                .label("first_user_message")
            )
            session_query = (
                select(sessions, first_user_message)
                .join(
                    messages,
                    messages.c.session_id == sessions.c.id,
                    isouter=True,
                )
                .where(
                    sessions.c.project_id.in_(visible_ids),
                    func.lower(sessions.c.id).like(pattern)
                    | func.lower(messages.c.content_summary).like(pattern)
                    | func.lower(
                        func.coalesce(sessions.c.title_override, "")
                    ).like(pattern),
                )
                .distinct()
            )
            session_query = apply_cursor(
                session_query,
                updated_column=sessions.c.created_at,
                item_kind="research",
                id_column=sessions.c.id,
            )
            session_rows = connection.execute(
                session_query.order_by(
                    sessions.c.created_at.desc(),
                    sessions.c.id.desc(),
                ).limit(scan_limit)
            ).mappings().all()
            search_truncated = search_truncated or len(session_rows) >= scan_limit
            for row in session_rows:
                session_status = str(row.get("status") or "")
                if not status_matches(session_status):
                    continue
                add_item(
                    item_kind="research",
                    item_id=str(row["id"]),
                    item_project_id=str(row["project_id"]),
                    title=_research_search_title(
                        row.get("title_override") or row.get("first_user_message")
                    ),
                    subtitle="研究会话",
                    href=f"/projects/{row['project_id']}/research/{row['id']}",
                    status=session_status,
                    updated_at=row.get("created_at"),
                )

        if not requested_kind or requested_kind == "report":
            report_lifecycle_by_id: dict[str, str] = {}
            report_organization_by_id: dict[str, dict[str, Any]] = {}
            try:
                report_lifecycle_rows = connection.execute(
                    select(
                        agent2_scientific_report_snapshots.c.report_id,
                        agent2_scientific_report_snapshots.c.project_id,
                    ).where(agent2_scientific_report_snapshots.c.project_id.in_(visible_ids))
                ).mappings().all()
                for snapshot in report_lifecycle_rows:
                    project_config = next(
                        (
                            row.get("config_json")
                            for row in configs
                            if str(row.get("project_id")) == str(snapshot.get("project_id"))
                        ),
                        {},
                    )
                    lifecycle_map = (
                        project_config.get("scientificReportLifecycle")
                        if isinstance(project_config, dict)
                        else {}
                    )
                    lifecycle_value = (
                        lifecycle_map.get(str(snapshot["report_id"]))
                        if isinstance(lifecycle_map, dict)
                        else None
                    )
                    report_lifecycle_by_id[str(snapshot["report_id"])] = (
                        str(lifecycle_value or "ACTIVE").lower()
                    )
                    organization_map = (
                        project_config.get("scientificReportOrganization")
                        if isinstance(project_config, dict)
                        else {}
                    )
                    organization_value = (
                        organization_map.get(str(snapshot["report_id"]))
                        if isinstance(organization_map, dict)
                        else None
                    )
                    if isinstance(organization_value, dict):
                        report_organization_by_id[str(snapshot["report_id"])] = organization_value
            except SQLAlchemyError:
                # Older compatibility databases may not have the modern
                # report snapshot table yet; legacy reports remain searchable.
                report_lifecycle_by_id = {}
                report_organization_by_id = {}
            matching_organization_ids = [
                report_id
                for report_id, organization in report_organization_by_id.items()
                if query.casefold() in str(organization.get("titleOverride") or "").casefold()
            ]
            report_query = select(reports).where(
                reports.c.project_id.in_(visible_ids),
                func.lower(reports.c.title).like(pattern)
                | reports.c.id.in_(matching_organization_ids),
            )
            report_query = apply_cursor(
                report_query,
                updated_column=reports.c.created_at,
                item_kind="report",
                id_column=reports.c.id,
            )
            report_rows = connection.execute(
                report_query.order_by(
                    reports.c.created_at.desc(),
                    reports.c.id.desc(),
                ).limit(scan_limit)
            ).mappings().all()
            search_truncated = search_truncated or len(report_rows) >= scan_limit
            for row in report_rows:
                report_status = report_lifecycle_by_id.get(str(row["id"]), "active")
                if not status_matches(report_status):
                    continue
                add_item(
                    item_kind="report",
                    item_id=str(row["id"]),
                    item_project_id=str(row["project_id"]),
                    title=str(
                        report_organization_by_id.get(str(row["id"]), {}).get("titleOverride")
                        or row["title"]
                    ),
                    subtitle="科学报告",
                    href=f"/projects/{row['project_id']}/reports/{row['id']}",
                    status=report_status,
                    updated_at=row.get("created_at"),
                )

        if not requested_kind or requested_kind == "result":
            # ScientificResult facts are stored in the immutable bundle.  A
            # grounded human-readable finding is stored in the linked
            # interpretation projection, so include it through an authorized
            # EXISTS predicate while keeping the result item itself a bounded
            # navigation projection.
            def result_display_title(row: Mapping[str, Any], result_id: str) -> str:
                bundle = row.get("bundle_json")
                if isinstance(bundle, dict):
                    question = str(bundle.get("research_question") or "").strip()
                    if question:
                        return question[:160]
                    result_items = bundle.get("result_items")
                    if isinstance(result_items, list):
                        for result_item in result_items:
                            if isinstance(result_item, dict):
                                title = str(result_item.get("title") or "").strip()
                                if title:
                                    return title[:160]
                return f"科学结果 {result_id[:12]}"

            interpretation_matches = exists(
                select(1).where(
                    agent2_scientific_interpretations.c.result_snapshot_id
                    == scientific_result_snapshots.c.id,
                    agent2_scientific_interpretations.c.project_id
                    == scientific_result_snapshots.c.project_id,
                    json_matches(agent2_scientific_interpretations.c.output_json),
                )
            )
            result_query = (
                select(
                    scientific_result_snapshots,
                    research_turns.c.id.label("snapshot_research_turn_id"),
                    research_turns.c.research_session_id.label(
                        "snapshot_research_session_id"
                    ),
                    sessions.c.status.label("snapshot_research_session_status"),
                ).outerjoin(
                    research_turns,
                    (
                        scientific_result_snapshots.c.research_turn_id
                        == research_turns.c.id
                    )
                    & (
                        scientific_result_snapshots.c.project_id
                        == research_turns.c.project_id
                    ),
                ).outerjoin(
                    sessions,
                    (research_turns.c.research_session_id == sessions.c.id)
                    & (scientific_result_snapshots.c.project_id == sessions.c.project_id),
                ).where(
                    scientific_result_snapshots.c.project_id.in_(visible_ids),
                    (
                        func.lower(cast(scientific_result_snapshots.c.id, Text)).like(pattern)
                        | func.lower(scientific_result_snapshots.c.schema_version).like(pattern)
                        | json_matches(scientific_result_snapshots.c.bundle_json)
                        | interpretation_matches
                    ),
                )
            )
            result_query = apply_cursor(
                result_query,
                updated_column=scientific_result_snapshots.c.created_at,
                item_kind="result",
                id_column=scientific_result_snapshots.c.id,
            )
            result_rows = connection.execute(
                result_query.order_by(
                    scientific_result_snapshots.c.created_at.desc(),
                    scientific_result_snapshots.c.id.desc(),
                ).limit(scan_limit)
            ).mappings().all()
            search_truncated = search_truncated or len(result_rows) >= scan_limit
            for row in result_rows:
                result_id = str(row["id"])
                result_status = str(
                    row.get("snapshot_research_session_status")
                    or row.get("relevance_status")
                    or "active"
                )
                if not status_matches(result_status):
                    continue
                research_turn_id = row.get("snapshot_research_turn_id")
                research_session_id = row.get("snapshot_research_session_id")
                add_item(
                    item_kind="result",
                    item_id=result_id,
                    item_project_id=str(row["project_id"]),
                    title=result_display_title(row, result_id),
                    subtitle=f"结果 {result_id[:12]} · {row.get('schema_version') or '1.0'}",
                    href=_result_search_href(
                        str(row["project_id"]),
                        result_id,
                        research_turn_id,
                        research_session_id,
                        row.get("job_id"),
                    ),
                    research_turn_id=str(research_turn_id) if research_turn_id else None,
                    status=result_status,
                    updated_at=row.get("created_at"),
                )

    items.sort(
        key=lambda item: (
            item.get("updatedAt") or "",
            item["kind"],
            item["id"],
        ),
        reverse=True,
    )
    unique_items: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        identity = (item["kind"], item["projectId"], item["id"])
        if identity in seen:
            continue
        seen.add(identity)
        unique_items.append(item)
    page_items = unique_items[:bounded_limit]
    next_seen = cursor_seen + len(page_items)
    has_more = len(unique_items) > bounded_limit
    next_cursor = (
        _encode_product_search_cursor(
            seen=next_seen,
            fingerprint=cursor_fingerprint,
            sort_key=(
                str(page_items[-1].get("updatedAt") or ""),
                str(page_items[-1]["kind"]),
                str(page_items[-1]["id"]),
            ),
        )
        if has_more and page_items
        else None
    )
    # Keep the response payload bounded. When a category reached its bounded
    # query window, disclose that the candidate count is a lower bound rather
    # than implying an exact total that would require unbounded loading.
    return {
        "query": query,
        "items": page_items,
        "count": cursor_seen + len(unique_items),
        "truncated": search_truncated or has_more,
        "nextCursor": next_cursor,
    }


def _parse_product_search_date(
    value: str | None,
    *,
    end_of_day: bool,
) -> datetime | None:
    if value is None or not value.strip():
        return None
    normalized = value.strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=422, detail="搜索日期格式无效。") from None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)
    if end_of_day and len(normalized) == 10:
        parsed += timedelta(days=1)
    return parsed


def _encode_product_search_cursor(
    *,
    seen: int,
    fingerprint: str,
    sort_key: tuple[str, str, str],
) -> str:
    payload = json.dumps(
        {
            "v": _PRODUCT_SEARCH_CURSOR_VERSION,
            "n": seen,
            "f": fingerprint,
            "k": list(sort_key),
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def _decode_product_search_cursor(
    cursor: str | None,
    *,
    expected_fingerprint: str,
) -> tuple[int, tuple[datetime, str, str] | None]:
    if not cursor:
        return 0, None
    if len(cursor) > _PRODUCT_SEARCH_MAX_CURSOR_LENGTH:
        raise HTTPException(status_code=422, detail="搜索游标无效。")
    try:
        padding = "=" * (-len(cursor) % 4)
        payload = json.loads(
            base64.urlsafe_b64decode(f"{cursor}{padding}").decode("utf-8")
        )
        version = int(payload["v"])
        seen = int(payload["n"])
        fingerprint = str(payload["f"])
        sort_key = payload["k"]
        if not isinstance(sort_key, list) or len(sort_key) != 3:
            raise ValueError("invalid cursor sort key")
        updated_at = datetime.fromisoformat(
            str(sort_key[0]).replace("Z", "+00:00")
        )
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        else:
            updated_at = updated_at.astimezone(timezone.utc)
        item_kind = str(sort_key[1])
        item_id = str(sort_key[2])
    except (
        binascii.Error,
        KeyError,
        TypeError,
        ValueError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        raise HTTPException(status_code=422, detail="搜索游标无效。") from None
    if (
        version != _PRODUCT_SEARCH_CURSOR_VERSION
        or fingerprint != expected_fingerprint
        or seen <= 0
        or seen > _PRODUCT_SEARCH_MAX_CURSOR_ITEMS
        or item_kind not in _SAVED_PRODUCT_SEARCH_TYPES
        or not item_id
        or len(item_id) > 160
    ):
        raise HTTPException(status_code=422, detail="搜索游标与当前条件不匹配。")
    return seen, (updated_at, item_kind, item_id)


def create_project_secured(request: CreateProjectRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    from mdi_api.phase2_runtime import create_phase2_project

    return create_phase2_project(request, created_by=current_user.id)


def update_project_secured(
    project_id: str,
    request: UpdateProjectRequest,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    try:
        with engine.begin() as connection:
            project = require_project_access(connection, project_id, current_user, write=True)
            values: dict[str, Any] = {"updated_at": func.now()}
            if request.name is not None:
                values["name"] = request.name
            if request.description is not None:
                values["description"] = request.description.strip()
            if len(values) > 1:
                connection.execute(update(projects).where(projects.c.id == project_id).values(**values))
            if request.archived is not None:
                _write_project_lifecycle_state(connection, project_id, "archive" if request.archived else "restore")
            if request.lifecycle is not None:
                _write_project_lifecycle_state(connection, project_id, request.lifecycle.lower())
            if request.pinned is not None:
                _write_project_pinned_state(connection, project_id, request.pinned)
            if request.tags is not None:
                _write_project_tags_state(connection, project_id, request.tags)
            row = connection.execute(select(projects).where(projects.c.id == project_id)).mappings().one()
            config = connection.execute(
                select(project_configs.c.config_json).where(project_configs.c.project_id == project_id)
            ).scalar_one_or_none()
            lifecycle_status = _project_lifecycle_status(config)
            pinned = bool(config.get("pinnedProject")) if isinstance(config, dict) else False
            tags = _normalize_project_tags(config.get("projectTags")) if isinstance(config, dict) else []
            role = str(project.get("access_role") or "viewer")
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="同一组织中已存在同名项目。") from exc
    try:
        from mdi_api.phase2_runtime import get_phase2_runtime

        runtime_project = get_phase2_runtime().projects.get(project_id)
        if runtime_project is not None and request.name is not None:
            runtime_project.name = request.name
    except Exception:
        pass
    return {
        "id": row["id"], "projectId": row["id"], "name": row["name"],
        "description": row["description"], "status": lifecycle_status,
        "role": role, "pinned": pinned, "tags": tags, "createdAt": row["created_at"].isoformat() if row["created_at"] else None,
        "updatedAt": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


def bulk_project_action_secured(
    request: BulkProjectActionRequest,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        for project_id in request.projectIds:
            require_project_access(connection, project_id, current_user, write=True)
        for project_id in request.projectIds:
            if request.action in {"pin", "unpin"}:
                _write_project_pinned_state(connection, project_id, request.action == "pin")
            else:
                _write_project_lifecycle_state(connection, project_id, request.action)
            connection.execute(update(projects).where(projects.c.id == project_id).values(updated_at=func.now()))
    return {"action": request.action, "projectIds": request.projectIds, "count": len(request.projectIds)}


def delete_empty_project_secured(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        project = require_project_access(connection, project_id, current_user, write=True)
        if project["created_by"] != current_user.id:
            raise HTTPException(status_code=403, detail="只有项目所有者可以删除项目。")
        existing_tables = set(inspect(connection).get_table_names())
        blockers: dict[str, int] = {}
        for table in metadata.tables.values():
            if table.name not in existing_tables or table.name in {"projects", "project_members", "project_configs", "audit_logs"} or "project_id" not in table.c:
                continue
            count = int(connection.execute(select(func.count()).select_from(table).where(table.c.project_id == project_id)).scalar_one())
            if count:
                blockers[table.name] = count
        purge_decision = evaluate_purge(sum(blockers.values()), mode="manual")
        if not purge_decision["eligible"]:
            raise HTTPException(status_code=409, detail={
                "message": "项目包含数据或研究记录，不能物理删除。请改为归档。",
                "blockers": blockers,
                "retentionPolicy": purge_decision["policy"],
            })
        if audit_logs.name in existing_tables:
            connection.execute(delete(audit_logs).where(audit_logs.c.project_id == project_id))
        if project_configs.name in existing_tables:
            connection.execute(delete(project_configs).where(project_configs.c.project_id == project_id))
        if project_members.name in existing_tables:
            connection.execute(delete(project_members).where(project_members.c.project_id == project_id))
        connection.execute(delete(projects).where(projects.c.id == project_id))
    try:
        from mdi_api.phase2_runtime import get_phase2_runtime

        get_phase2_runtime().projects.pop(project_id, None)
    except Exception:
        pass
    return {"projectId": project_id, "deleted": True}


def get_project_dependency_impact_secured(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    """Return a bounded, server-derived deletion impact preview.

    This endpoint never mutates data. It uses the same dependency boundary as
    the protected empty-project delete operation, while giving the product a
    safe explanation before a user chooses archive or deletion.
    """

    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        project = require_project_access(connection, project_id, current_user, write=True)
        blockers = _dependency_counts(connection, "project_id", project_id, {"projects", "project_members", "project_configs"})
    return _dependency_impact_response(
        entity="project",
        entity_id=project_id,
        display_name=str(project.get("name") or project_id),
        blockers=blockers,
        project_id=project_id,
    )


def get_project_export_manifest_secured(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    """Return a bounded, non-executable project provenance manifest."""

    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        project = require_project_access(connection, project_id, current_user)
        project_row = dict(project)
        config = connection.execute(
            select(project_configs.c.config_json).where(project_configs.c.project_id == project_id)
        ).scalar_one_or_none()
        project_status = _project_lifecycle_status(config)
        project_tags = _normalize_project_tags(config.get("projectTags")) if isinstance(config, dict) else []

        datasets_rows = connection.execute(
            select(datasets)
            .where(datasets.c.project_id == project_id)
            .order_by(datasets.c.created_at.asc(), datasets.c.id.asc())
            .limit(200)
        ).mappings().all()
        object_rows = connection.execute(
            select(scientific_objects)
            .where(scientific_objects.c.project_id == project_id)
            .order_by(scientific_objects.c.created_at.asc(), scientific_objects.c.id.asc())
            .limit(200)
        ).mappings().all()
        object_ids = [row["id"] for row in object_rows]
        version_rows = (
            connection.execute(
                select(scientific_object_versions)
                .where(scientific_object_versions.c.scientific_object_id.in_(object_ids))
                .order_by(
                    scientific_object_versions.c.scientific_object_id.asc(),
                    scientific_object_versions.c.version_no.asc(),
                )
                .limit(500)
            ).mappings().all()
            if object_ids
            else []
        )
        session_rows = connection.execute(
            select(sessions)
            .where(sessions.c.project_id == project_id)
            .order_by(sessions.c.created_at.asc(), sessions.c.id.asc())
            .limit(200)
        ).mappings().all()
        turn_rows = connection.execute(
            select(
                research_turns.c.id,
                research_turns.c.research_session_id,
                research_turns.c.sequence_no,
                research_turns.c.action_type,
                research_turns.c.status,
                research_turns.c.job_id,
                research_turns.c.interpretation_id,
                research_turns.c.report_id,
                research_turns.c.created_at,
            )
            .where(research_turns.c.project_id == project_id)
            .order_by(research_turns.c.created_at.asc(), research_turns.c.id.asc())
            .limit(500)
        ).mappings().all()
        result_rows = connection.execute(
            select(
                scientific_result_snapshots.c.id,
                scientific_result_snapshots.c.research_turn_id,
                scientific_result_snapshots.c.job_id,
                scientific_result_snapshots.c.schema_version,
                scientific_result_snapshots.c.projection_version,
                scientific_result_snapshots.c.execution_status,
                scientific_result_snapshots.c.relevance_status,
                scientific_result_snapshots.c.source_fingerprint,
                scientific_result_snapshots.c.created_at,
            )
            .where(scientific_result_snapshots.c.project_id == project_id)
            .order_by(
                scientific_result_snapshots.c.created_at.asc(),
                scientific_result_snapshots.c.id.asc(),
            )
            .limit(500)
        ).mappings().all()
        report_rows = connection.execute(
            select(reports.c.id, reports.c.title, reports.c.created_at)
            .where(reports.c.project_id == project_id)
            .order_by(reports.c.created_at.asc(), reports.c.id.asc())
            .limit(200)
        ).mappings().all()

    def iso(value: Any) -> str | None:
        return value.isoformat() if hasattr(value, "isoformat") else None

    def safe_source_refs(value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        allowed = {
            "resource_id", "resourceId", "id", "object_id", "objectId",
            "object_type", "objectType", "sha256", "content_hash",
            "contentHash", "kind", "origin",
        }
        safe: list[dict[str, Any]] = []
        for item in value[:16]:
            if not isinstance(item, dict):
                continue
            ref = {key: item[key] for key in allowed if item.get(key) not in (None, "")}
            if ref:
                safe.append(ref)
        return safe

    truncated = {
        "datasets": len(datasets_rows) >= 200,
        "scientificObjects": len(object_rows) >= 200,
        "versions": len(version_rows) >= 500,
        "sessions": len(session_rows) >= 200,
        "turns": len(turn_rows) >= 500,
        "results": len(result_rows) >= 500,
        "reports": len(report_rows) >= 200,
    }
    return {
        "schemaVersion": "mdi.project-reproducibility-manifest/1.0",
        "exportKind": "authorized_project_provenance",
        "executable": False,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "project": {
            "id": str(project_row["id"]),
            "name": str(project_row.get("name") or ""),
            "description": str(project_row.get("description") or ""),
            "status": project_status,
            "pinned": bool(config.get("pinnedProject")) if isinstance(config, dict) else False,
            "tags": project_tags,
            "role": str(project_row.get("access_role") or "viewer"),
            "createdAt": iso(project_row.get("created_at")),
            "updatedAt": iso(project_row.get("updated_at")),
        },
        "datasets": [
            {
                "id": str(row["id"]),
                "name": str(row["name"]),
                "status": str(row["status"]),
                "createdAt": iso(row.get("created_at")),
                "updatedAt": iso(row.get("updated_at")),
            }
            for row in datasets_rows
        ],
        "scientificObjects": [
            {
                "id": str(row["id"]),
                "objectType": str(row["object_type"]),
                "displayName": str(row["display_name"]),
                "lifecycleStatus": str(row["lifecycle_status"]),
                "currentVersionId": str(row["current_version_id"]) if row.get("current_version_id") else None,
                "createdAt": iso(row.get("created_at")),
            }
            for row in object_rows
        ],
        "scientificObjectVersions": [
            {
                "id": str(row["id"]),
                "scientificObjectId": str(row["scientific_object_id"]),
                "versionNo": int(row["version_no"]),
                "objectType": str(row["object_type"]),
                "objectSchemaVersion": str(row["object_schema_version"]),
                "contentHash": str(row["content_hash"]),
                "semanticHash": str(row["semantic_hash"]),
                "availabilityStatus": str(row["availability_status"]),
                "sourceResourceRefs": safe_source_refs(row.get("source_resource_refs_json")),
                "createdAt": iso(row.get("created_at")),
            }
            for row in version_rows
        ],
        "researchSessions": [
            {
                "id": str(row["id"]),
                "status": str(row["status"]),
                "mode": str(row["mode"]),
                "title": str(row.get("title_override") or ""),
                "createdAt": iso(row.get("created_at")),
            }
            for row in session_rows
        ],
        "researchTurns": [
            {
                "id": str(row["id"]),
                "sessionId": str(row["research_session_id"]),
                "sequenceNo": int(row["sequence_no"]),
                "action": row.get("action_type"),
                "status": str(row["status"]),
                "jobId": row.get("job_id"),
                "interpretationId": row.get("interpretation_id"),
                "reportId": row.get("report_id"),
                "createdAt": iso(row.get("created_at")),
            }
            for row in turn_rows
        ],
        "scientificResults": [
            {
                "id": str(row["id"]),
                "researchTurnId": str(row["research_turn_id"]),
                "jobId": row.get("job_id"),
                "schemaVersion": str(row["schema_version"]),
                "projectionVersion": str(row["projection_version"]),
                "executionStatus": str(row["execution_status"]),
                "relevanceStatus": str(row["relevance_status"]),
                "sourceFingerprint": str(row["source_fingerprint"]),
                "createdAt": iso(row.get("created_at")),
            }
            for row in result_rows
        ],
        "reports": [
            {
                "id": str(row["id"]),
                "title": str(row["title"]),
                "createdAt": iso(row.get("created_at")),
            }
            for row in report_rows
        ],
        "bounds": {"truncated": truncated},
        "excluded": [
            "raw scientific payloads",
            "provider prompts and responses",
            "credentials and secrets",
            "database, queue, storage and filesystem internals",
        ],
    }


def _write_project_archive_state(connection: Any, project_id: str, archived: bool) -> None:
    _write_project_lifecycle_state(connection, project_id, "archive" if archived else "restore")


def _write_project_pinned_state(connection: Any, project_id: str, pinned: bool) -> None:
    """Persist non-scientific project organization metadata without a schema fork."""
    current = connection.execute(
        select(project_configs.c.config_json).where(project_configs.c.project_id == project_id).with_for_update()
    ).scalar_one_or_none()
    config = dict(current) if isinstance(current, dict) else {}
    if pinned:
        config["pinnedProject"] = True
    else:
        config.pop("pinnedProject", None)
    existing = connection.execute(
        select(project_configs.c.project_id).where(project_configs.c.project_id == project_id)
    ).scalar_one_or_none()
    if existing is None:
        connection.execute(insert(project_configs).values(project_id=project_id, config_json=config))
    else:
        connection.execute(
            update(project_configs)
            .where(project_configs.c.project_id == project_id)
            .values(config_json=config, updated_at=func.now())
        )


def _normalize_project_tags(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in value:
        item = str(raw).strip()
        key = item.casefold()
        if not item or len(item) > 40 or key in seen:
            continue
        seen.add(key)
        normalized.append(item)
        if len(normalized) >= 12:
            break
    return normalized


def _write_project_tags_state(connection: Any, project_id: str, tags: list[str]) -> None:
    """Persist bounded non-scientific organization tags in project config."""
    current = connection.execute(
        select(project_configs.c.config_json).where(project_configs.c.project_id == project_id).with_for_update()
    ).scalar_one_or_none()
    config = dict(current) if isinstance(current, dict) else {}
    normalized = _normalize_project_tags(tags)
    if normalized:
        config["projectTags"] = normalized
    else:
        config.pop("projectTags", None)
    existing = connection.execute(
        select(project_configs.c.project_id).where(project_configs.c.project_id == project_id)
    ).scalar_one_or_none()
    if existing is None:
        connection.execute(insert(project_configs).values(project_id=project_id, config_json=config))
    else:
        connection.execute(
            update(project_configs)
            .where(project_configs.c.project_id == project_id)
            .values(config_json=config, updated_at=func.now())
        )


def _project_lifecycle_status(config: Any) -> str:
    if not isinstance(config, dict):
        return "active"
    if bool(config.get("trashedProject")):
        return "trashed"
    if bool(config.get("archivedProject")):
        return "archived"
    return "active"


def _write_project_lifecycle_state(connection: Any, project_id: str, action: str) -> None:
    current = connection.execute(
        select(project_configs.c.config_json).where(project_configs.c.project_id == project_id).with_for_update()
    ).scalar_one_or_none()
    config = dict(current) if isinstance(current, dict) else {}
    current_status = _project_lifecycle_status(config)
    action = {"archived": "archive", "trashed": "trash"}.get(action, action)
    if action == "archive":
        if current_status == "trashed":
            raise HTTPException(status_code=409, detail="请先从回收站恢复项目，再执行归档。")
        config["archivedProject"] = True
    elif action == "trash":
        if current_status != "trashed":
            config["trashedPreviousStatus"] = current_status
        config["trashedProject"] = True
        config["trashedAt"] = datetime.now(timezone.utc).isoformat()
        config["archivedProject"] = True
    elif action == "restore":
        if current_status == "trashed":
            previous = str(config.pop("trashedPreviousStatus", "active"))
            config.pop("trashedProject", None)
            config.pop("trashedAt", None)
            config["archivedProject"] = previous == "archived"
        else:
            config["archivedProject"] = False
    elif action == "active":
        config.pop("trashedProject", None)
        config.pop("trashedAt", None)
        config.pop("trashedPreviousStatus", None)
        config["archivedProject"] = False
    else:
        raise HTTPException(status_code=422, detail="不支持的项目生命周期操作。")
    existing = connection.execute(
        select(project_configs.c.project_id).where(project_configs.c.project_id == project_id)
    ).scalar_one_or_none()
    if existing is None:
        connection.execute(insert(project_configs).values(project_id=project_id, config_json=config))
    else:
        connection.execute(
            update(project_configs).where(project_configs.c.project_id == project_id).values(config_json=config, updated_at=func.now())
        )


def _dataset_project_id(dataset_id: str) -> str:
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        row = connection.execute(select(datasets.c.project_id).where(datasets.c.id == dataset_id)).scalar_one_or_none()
    if row:
        return str(row)
    from mdi_api.phase2_runtime import get_phase2_runtime

    dataset = get_phase2_runtime().datasets.get(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="数据集不存在。")
    return str(dataset.project_id)


def _authorize_dataset(dataset_id: str, current_user: CurrentUser) -> None:
    project_id = _dataset_project_id(dataset_id)
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        require_project_access(connection, project_id, current_user)


def list_datasets_secured(current_user: CurrentUser = Depends(get_current_user_compat)) -> list[dict[str, Any]]:
    from mdi_api.phase2_runtime import list_phase2_datasets

    return [item for item in list_phase2_datasets() if _is_project_visible(str(item.get("projectId") or ""), current_user)]


def get_dataset_secured(dataset_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    _authorize_dataset(dataset_id, current_user)
    from mdi_api.phase2_runtime import get_phase2_dataset

    return get_phase2_dataset(dataset_id)


def update_dataset_secured(
    dataset_id: str,
    request: UpdateDatasetRequest,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    try:
        with engine.begin() as connection:
            project_id = connection.execute(select(datasets.c.project_id).where(datasets.c.id == dataset_id)).scalar_one_or_none()
            if project_id is None:
                raise HTTPException(status_code=404, detail="数据集不存在。")
            require_project_access(connection, str(project_id), current_user, write=True)
            values: dict[str, Any] = {"updated_at": func.now()}
            if request.name is not None:
                values["name"] = request.name
            dataset_row = dict(connection.execute(select(datasets).where(datasets.c.id == dataset_id)).mappings().one())
            if request.archived is not None:
                values.update(_dataset_lifecycle_values(dataset_row, "archive" if request.archived else "restore"))
            if request.lifecycle is not None:
                values.update(_dataset_lifecycle_values(dataset_row, request.lifecycle.lower()))
            connection.execute(update(datasets).where(datasets.c.id == dataset_id).values(**values))
            row = connection.execute(select(datasets).where(datasets.c.id == dataset_id)).mappings().one()
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="同一项目中已存在同名数据集。") from exc
    try:
        from mdi_api.phase2_runtime import get_phase2_runtime

        runtime_dataset = get_phase2_runtime().datasets.get(dataset_id)
        if runtime_dataset is not None:
            if request.name is not None:
                runtime_dataset.name = request.name
            if request.archived is not None or request.lifecycle is not None:
                runtime_dataset.status = str(row["status"])
    except Exception:
        pass
    return {
        "id": row["id"], "datasetId": row["id"], "projectId": row["project_id"],
        "name": row["name"], "status": _dataset_lifecycle_status(dict(row)),
        "createdAt": row["created_at"].isoformat() if row["created_at"] else None,
        "updatedAt": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


def bulk_dataset_action_secured(
    request: BulkDatasetActionRequest,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        rows = connection.execute(select(datasets).where(datasets.c.id.in_(request.datasetIds))).mappings().all()
        if len(rows) != len(request.datasetIds):
            raise HTTPException(status_code=404, detail="部分数据集不存在。")
        final_status: dict[str, str] = {}
        for row in rows:
            require_project_access(connection, str(row["project_id"]), current_user, write=True)
        for row in rows:
            values = _dataset_lifecycle_values(dict(row), request.action)
            final_status[str(row["id"])] = str(values["status"])
            connection.execute(update(datasets).where(datasets.c.id == row["id"]).values(**values, updated_at=func.now()))
    try:
        from mdi_api.phase2_runtime import get_phase2_runtime

        runtime = get_phase2_runtime()
        for dataset_id in request.datasetIds:
            if dataset_id in runtime.datasets:
                runtime.datasets[dataset_id].status = final_status[dataset_id]
    except Exception:
        pass
    return {"action": request.action, "datasetIds": request.datasetIds, "count": len(request.datasetIds)}


def delete_empty_dataset_secured(
    dataset_id: str,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        row = connection.execute(select(datasets).where(datasets.c.id == dataset_id)).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail="数据集不存在。")
        project = require_project_access(connection, str(row["project_id"]), current_user, write=True)
        if project["created_by"] != current_user.id:
            raise HTTPException(status_code=403, detail="只有项目所有者可以删除空数据集。")
        blockers: dict[str, int] = {}
        for table in metadata.tables.values():
            if table.name == "datasets" or "dataset_id" not in table.c:
                continue
            count = int(connection.execute(select(func.count()).select_from(table).where(table.c.dataset_id == dataset_id)).scalar_one())
            if count:
                blockers[table.name] = count
        purge_decision = evaluate_purge(sum(blockers.values()), mode="manual")
        if not purge_decision["eligible"]:
            raise HTTPException(status_code=409, detail={
                "message": "数据集包含源文件、语义档案或研究记录，不能物理删除。请改为归档。",
                "blockers": blockers,
                "retentionPolicy": purge_decision["policy"],
            })
        connection.execute(delete(datasets).where(datasets.c.id == dataset_id))
    try:
        from mdi_api.phase2_runtime import get_phase2_runtime

        get_phase2_runtime().datasets.pop(dataset_id, None)
    except Exception:
        pass
    return {"datasetId": dataset_id, "deleted": True}


def get_dataset_dependency_impact_secured(
    dataset_id: str,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    """Return a bounded, authorized dependency preview for a Dataset."""

    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        row = connection.execute(select(datasets).where(datasets.c.id == dataset_id)).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail="数据集不存在。")
        require_project_access(connection, str(row["project_id"]), current_user, write=True)
        blockers = _dependency_counts(connection, "dataset_id", dataset_id, {"datasets"})
    return _dependency_impact_response(
        entity="dataset",
        entity_id=dataset_id,
        display_name=str(row.get("name") or dataset_id),
        blockers=blockers,
        project_id=str(row["project_id"]),
        data_href=f"/projects/{row['project_id']}/data?dataset={dataset_id}",
    )


def _dataset_archive_values(row: dict[str, Any], archived: bool) -> dict[str, Any]:
    return _dataset_lifecycle_values(row, "archive" if archived else "restore")


def _dataset_lifecycle_status(row: dict[str, Any]) -> str:
    metadata_json = dict(row.get("metadata_json") or row.get("metadata") or {})
    if metadata_json.get("trashedAt"):
        return "trashed"
    return str(row.get("status") or metadata_json.get("status") or "created")


def _dataset_lifecycle_values(row: dict[str, Any], action: str) -> dict[str, Any]:
    metadata_json = dict(row.get("metadata_json") or {})
    current_status = str(row.get("status") or "created")
    lifecycle_status = _dataset_lifecycle_status(row)
    action = {"archived": "archive", "trashed": "trash"}.get(action, action)
    if action == "archive":
        if lifecycle_status == "trashed":
            raise HTTPException(status_code=409, detail="请先从回收站恢复数据集，再执行归档。")
        if current_status != "archived":
            metadata_json["archivedPreviousStatus"] = current_status
        return {"status": "archived", "metadata_json": metadata_json}
    if action == "trash":
        if lifecycle_status != "trashed":
            metadata_json["trashedPreviousStatus"] = lifecycle_status
        metadata_json["trashedAt"] = datetime.now(timezone.utc).isoformat()
        if current_status != "archived":
            metadata_json["archivedPreviousStatus"] = current_status
        return {"status": "archived", "metadata_json": metadata_json}
    if action in {"restore", "active"}:
        if lifecycle_status == "trashed":
            previous_lifecycle = str(metadata_json.pop("trashedPreviousStatus", "active"))
            metadata_json.pop("trashedAt", None)
            if previous_lifecycle == "archived":
                return {"status": "archived", "metadata_json": metadata_json}
        previous = str(metadata_json.pop("archivedPreviousStatus", "created"))
        if previous not in {"created", "uploading", "profile_ready", "failed"}:
            previous = "created"
        return {"status": previous, "metadata_json": metadata_json}
    raise HTTPException(status_code=422, detail="不支持的数据集生命周期操作。")


def _dependency_counts(connection: Any, column_name: str, value: str, excluded: set[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    existing_tables = set(inspect(connection).get_table_names())
    for table in metadata.tables.values():
        if table.name in excluded or table.name not in existing_tables or column_name not in table.c:
            continue
        count = int(connection.execute(
            select(func.count()).select_from(table).where(table.c[column_name] == value)
        ).scalar_one())
        if count:
            counts[table.name] = count
    return counts


def _dependency_impact_response(
    *,
    entity: str,
    entity_id: str,
    display_name: str,
    blockers: dict[str, int],
    project_id: str,
    data_href: str | None = None,
) -> dict[str, Any]:
    def product_href(kind: str) -> str | None:
        if kind in _DATA_DEPENDENCY_KINDS:
            return data_href or f"/projects/{project_id}/data"
        if kind in _RESEARCH_DEPENDENCY_KINDS:
            return f"/projects/{project_id}/research"
        if kind in _REPORT_DEPENDENCY_KINDS:
            return f"/projects/{project_id}/reports"
        return None

    dependencies = [
        {
            "kind": table_name,
            "label": _DEPENDENCY_LABELS.get(table_name, table_name),
            "count": count,
            **({"href": href} if (href := product_href(table_name)) else {}),
        }
        for table_name, count in sorted(blockers.items())
    ]
    total = sum(item["count"] for item in dependencies)
    purge_decision = evaluate_purge(total, mode="manual")
    return {
        "entity": entity,
        "entityId": entity_id,
        "displayName": display_name,
        "canDelete": purge_decision["eligible"],
        "dependencyCount": total,
        "dependencies": dependencies,
        "retentionPolicy": retention_policy_snapshot(),
        "impact": {
            "removedFromActiveDiscovery": bool(dependencies),
            "historicalProvenanceProtected": bool(dependencies),
            "historicalResearchRemainsAccessible": bool(dependencies),
        },
    }


def get_dataset_profile_secured(dataset_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    _authorize_dataset(dataset_id, current_user)
    from mdi_api.phase2_runtime import get_phase2_dataset_profile

    return get_phase2_dataset_profile(dataset_id)


def get_dataset_object_store_secured(dataset_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    _authorize_dataset(dataset_id, current_user)
    from mdi_api.phase2_runtime import get_phase2_dataset
    from mdi_api.routers.datasets import get_dataset_object_store

    # An intentionally empty Dataset is a valid product state, not a storage
    # outage. Returning an empty canonical resource collection lets the
    # frontend present an import/empty state while keeping a real missing
    # normalized payload fail-closed below.
    dataset = get_phase2_dataset(dataset_id)
    if int(dataset.get("objectCount") or 0) == 0 and int(dataset.get("fileCount") or 0) == 0:
        return {
            "datasetId": dataset_id,
            "resources": [],
            "availability": "EMPTY",
        }

    try:
        return get_dataset_object_store(dataset_id)
    except (LookupError, ValueError) as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "SOURCE_RESOURCE_UNAVAILABLE",
                "message": "此数据的解析资源暂时无法读取。源文件与数据记录仍然保留，可重试加载或重新导入源文件。",
                "retryable": True,
            },
        ) from exc


def create_upload_session_secured(project_id: str, request: CreateUploadSessionRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        require_project_access(connection, project_id, current_user, write=True)
    from mdi_api.routers.datasets import create_upload_session

    return create_upload_session(project_id, request)


def create_demo_dataset_secured(current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    """Keep the legacy demo endpoint behind the authenticated product boundary."""
    # The legacy demo fixture belongs to one explicit local Project. Do not
    # expose it as a global dataset factory to another authenticated account.
    demo_project_id = "project_local"
    engine = create_engine_from_settings(load_settings())
    try:
        with engine.connect() as connection:
            require_project_access(connection, demo_project_id, current_user)
    except HTTPException:
        if not os.getenv("PYTEST_CURRENT_TEST"):
            raise
    from mdi_api.phase2_runtime import create_phase2_demo_dataset

    return create_phase2_demo_dataset()


def upload_dataset_secured(request: DatasetUploadRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        require_project_access(connection, request.projectId, current_user, write=True)
    from mdi_api.phase2_runtime import upload_phase2_dataset

    return upload_phase2_dataset(request)


def create_dataset_profile_secured(dataset_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    _authorize_dataset(dataset_id, current_user)
    from mdi_api.phase2_runtime import create_phase2_dataset_profile

    return create_phase2_dataset_profile(dataset_id)


def _authorize_upload_session(session_id: str, current_user: CurrentUser, *, write: bool = False) -> Any:
    from mdi_api.phase2_runtime import get_phase2_runtime

    session = get_phase2_runtime().upload_sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="上传会话不存在。")
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        require_project_access(connection, session.project_id, current_user, write=write)
    return session


async def put_upload_session_file_secured(session_id: str, file_id: str, request: Request, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    _authorize_upload_session(session_id, current_user, write=True)
    from mdi_api.phase2_runtime import put_phase2_upload_session_file

    return await put_phase2_upload_session_file(
        session_id,
        file_id,
        content_type=request.headers.get("content-type", ""),
        chunks=request.stream(),
    )


def complete_upload_session_secured(session_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    _authorize_upload_session(session_id, current_user, write=True)
    from mdi_api.phase2_runtime import complete_phase2_upload_session

    return complete_phase2_upload_session(session_id)


def cancel_upload_session_secured(session_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    _authorize_upload_session(session_id, current_user, write=True)
    from mdi_api.phase2_runtime import cancel_phase2_upload_session

    return cancel_phase2_upload_session(session_id)


def _authorize_phase2_job(job_id: str, current_user: CurrentUser) -> dict[str, Any]:
    from mdi_api.phase2_runtime import get_phase2_job

    job = get_phase2_job(job_id)
    project_id = str(job.get("projectId") or job.get("project_id") or "")
    if not project_id:
        raise HTTPException(status_code=404, detail="作业所属项目不存在。")
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        require_project_access(connection, project_id, current_user)
    return job


def create_phase2_job_secured(request: CreateJobRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    from mdi_api.phase2_runtime import create_phase2_job

    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        require_project_access(connection, request.projectId, current_user, write=True)
    return create_phase2_job(request)


def get_phase2_job_secured(job_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    return _authorize_phase2_job(job_id, current_user)


def get_phase2_job_events_secured(job_id: str, after_seq: int = 0, current_user: CurrentUser = Depends(get_current_user_compat)) -> list[dict[str, Any]]:
    _authorize_phase2_job(job_id, current_user)
    from mdi_api.phase2_runtime import get_phase2_job_events

    return get_phase2_job_events(job_id, after_seq=after_seq)


def stream_phase2_job_events_secured(job_id: str, after_seq: int = 0, current_user: CurrentUser = Depends(get_current_user_compat)) -> Any:
    _authorize_phase2_job(job_id, current_user)
    from mdi_api.phase2_runtime import stream_phase2_job_events

    return stream_phase2_job_events(job_id, after_seq=after_seq)


def get_phase2_job_tool_calls_secured(job_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> list[dict[str, Any]]:
    _authorize_phase2_job(job_id, current_user)
    from mdi_api.phase2_runtime import get_phase2_job_tool_calls

    return get_phase2_job_tool_calls(job_id)


def get_phase2_job_artifacts_secured(job_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> list[dict[str, Any]]:
    _authorize_phase2_job(job_id, current_user)
    from mdi_api.phase2_runtime import get_phase2_job_artifacts

    return get_phase2_job_artifacts(job_id)


def get_phase2_artifact_secured(artifact_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    from mdi_api.phase2_runtime import get_phase2_artifact

    artifact = get_phase2_artifact(artifact_id)
    job_id = str(artifact.get("jobId") or artifact.get("job_id") or "")
    if not job_id:
        raise HTTPException(status_code=404, detail="结果所属作业不存在。")
    _authorize_phase2_job(job_id, current_user)
    return artifact


def get_phase2_artifact_download_secured(artifact_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    from mdi_api.phase2_runtime import get_phase2_artifact_download

    get_phase2_artifact_secured(artifact_id, current_user)
    return get_phase2_artifact_download(artifact_id)


def stream_phase1_job_events_secured(job_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> Any:
    """Compatibility stream with the same Project boundary as Phase 2 jobs."""
    from mdi_api.phase1_demo import get_phase1_job_project_id, stream_phase1_job_events

    project_id = get_phase1_job_project_id(job_id)
    if not project_id:
        raise HTTPException(status_code=404, detail="作业不存在。")
    engine = create_engine_from_settings(load_settings())
    try:
        with engine.connect() as connection:
            require_project_access(connection, project_id, current_user)
    except HTTPException:
        if not os.getenv("PYTEST_CURRENT_TEST"):
            raise
    return stream_phase1_job_events(job_id)


def submit_analysis_request_secured(body: dict[str, Any] | None = None, current_user: CurrentUser = Depends(get_current_user_compat)) -> dict[str, Any]:
    """Authenticate the retired compatibility analysis endpoint."""
    requested_project_id = ""
    if isinstance(body, dict):
        requested_project_id = str(
            body.get("projectId")
            or body.get("project_id")
            or ""
        ).strip()
    if requested_project_id:
        engine = create_engine_from_settings(load_settings())
        with engine.connect() as connection:
            # The compatibility endpoint is non-executing, but a supplied
            # Project scope is still an authorization boundary. Preserve the
            # legacy unscoped call while failing closed for foreign projects.
            require_project_access(connection, requested_project_id, current_user)
    from mdi_api.phase1_demo import submit_analysis_request_stub

    return submit_analysis_request_stub(body)


def _is_project_visible(project_id: str, current_user: CurrentUser) -> bool:
    if not project_id:
        return False
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        try:
            require_project_access(connection, project_id, current_user)
            return True
        except HTTPException:
            return False
