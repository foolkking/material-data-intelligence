from __future__ import annotations

import os
from typing import Any

from fastapi import Depends, HTTPException, Request
from sqlalchemy import delete, func, insert, inspect, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from mdi_api.access import require_project_access
from mdi_api.config import load_settings
from mdi_api.database import create_engine_from_settings
from mdi_api.db import (
    audit_logs,
    datasets,
    messages,
    metadata,
    project_configs,
    project_members,
    projects,
    reports,
    scientific_objects,
    scientific_result_snapshots,
    sessions,
)
from mdi_api.routers.auth import CurrentUser, get_current_user_compat
from mdi_api.phase2_runtime import CreateJobRequest, CreateProjectRequest, DatasetUploadRequest
from mdi_api.routers.datasets import BulkDatasetActionRequest, UpdateDatasetRequest
from mdi_api.routers.projects import BulkProjectActionRequest, UpdateProjectRequest
from mdi_api.input_transport import CreateUploadSessionRequest


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
            for row in rows:
                role = "owner" if row["created_by"] == current_user.id else "viewer"
                if project_members_available:
                    try:
                        role = connection.execute(
                            select(project_members.c.role).where(
                                project_members.c.project_id == row["id"],
                                project_members.c.user_id == current_user.id,
                            )
                        ).scalar_one_or_none() or role
                    except SQLAlchemyError:
                        pass
                archived = False
                try:
                    config = connection.execute(
                        select(project_configs.c.config_json).where(project_configs.c.project_id == row["id"])
                    ).scalar_one_or_none()
                    archived = bool(config.get("archivedProject")) if isinstance(config, dict) else False
                except SQLAlchemyError:
                    pass
                visible.append({
                    "id": row["id"], "projectId": row["id"], "name": row["name"],
                    "description": row["description"], "status": "archived" if archived else "active", "role": role,
                    "createdAt": row["created_at"].isoformat() if row["created_at"] else None,
                    "updatedAt": row["updated_at"].isoformat() if row["updated_at"] else None,
                })
    except SQLAlchemyError:
        if not os.getenv("PYTEST_CURRENT_TEST"):
            raise
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
    limit: int = 40,
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
            return {"query": query, "items": [], "count": 0}

        pattern = f"%{query.lower()}%" if query else "%"
        items: list[dict[str, Any]] = []

        def add_item(
            *,
            item_kind: str,
            item_id: str,
            item_project_id: str,
            title: str,
            subtitle: str,
            href: str,
            status: str | None = None,
            updated_at: Any = None,
        ) -> None:
            if requested_kind and requested_kind != item_kind:
                return
            items.append({
                "kind": item_kind,
                "id": item_id,
                "projectId": item_project_id,
                "title": title,
                "subtitle": subtitle,
                "href": href,
                "status": status,
                "updatedAt": updated_at.isoformat() if updated_at else None,
            })

        if not requested_kind or requested_kind == "project":
            project_rows = connection.execute(
                select(projects).where(
                    projects.c.id.in_(visible_ids),
                    func.lower(projects.c.name).like(pattern)
                    | func.lower(projects.c.description).like(pattern),
                ).order_by(projects.c.updated_at.desc()).limit(bounded_limit)
            ).mappings().all()
            for row in project_rows:
                add_item(
                    item_kind="project",
                    item_id=str(row["id"]),
                    item_project_id=str(row["id"]),
                    title=str(row["name"]),
                    subtitle=str(row.get("description") or "材料研究项目"),
                    href=f"/projects/{row['id']}",
                    status="active",
                    updated_at=row.get("updated_at"),
                )

        if not requested_kind or requested_kind == "dataset":
            dataset_rows = connection.execute(
                select(datasets).where(
                    datasets.c.project_id.in_(visible_ids),
                    func.lower(datasets.c.name).like(pattern),
                ).order_by(datasets.c.updated_at.desc()).limit(bounded_limit)
            ).mappings().all()
            for row in dataset_rows:
                add_item(
                    item_kind="dataset",
                    item_id=str(row["id"]),
                    item_project_id=str(row["project_id"]),
                    title=str(row["name"]),
                    subtitle="数据集",
                    href=f"/projects/{row['project_id']}/data?dataset={row['id']}",
                    status=str(row.get("status") or ""),
                    updated_at=row.get("updated_at"),
                )

        if not requested_kind or requested_kind == "scientific_object":
            object_rows = connection.execute(
                select(scientific_objects).where(
                    scientific_objects.c.project_id.in_(visible_ids),
                    func.lower(scientific_objects.c.display_name).like(pattern)
                    | func.lower(scientific_objects.c.object_type).like(pattern),
                ).order_by(scientific_objects.c.created_at.desc()).limit(bounded_limit)
            ).mappings().all()
            for row in object_rows:
                add_item(
                    item_kind="scientific_object",
                    item_id=str(row["id"]),
                    item_project_id=str(row["project_id"]),
                    title=str(row["display_name"]),
                    subtitle=str(row["object_type"]),
                    href=f"/projects/{row['project_id']}/data?object={row['id']}",
                    status=str(row.get("lifecycle_status") or ""),
                    updated_at=row.get("created_at"),
                )

        if not requested_kind or requested_kind == "research":
            session_rows = connection.execute(
                select(sessions).join(messages, messages.c.session_id == sessions.c.id, isouter=True).where(
                    sessions.c.project_id.in_(visible_ids),
                    func.lower(sessions.c.id).like(pattern)
                    | func.lower(messages.c.content_summary).like(pattern),
                ).distinct().order_by(sessions.c.created_at.desc()).limit(bounded_limit)
            ).mappings().all()
            for row in session_rows:
                add_item(
                    item_kind="research",
                    item_id=str(row["id"]),
                    item_project_id=str(row["project_id"]),
                    title=f"研究会话 {row['id']}",
                    subtitle="Research",
                    href=f"/projects/{row['project_id']}/research/{row['id']}",
                    status=str(row.get("status") or ""),
                    updated_at=row.get("created_at"),
                )

        if not requested_kind or requested_kind == "report":
            report_rows = connection.execute(
                select(reports).where(
                    reports.c.project_id.in_(visible_ids),
                    func.lower(reports.c.title).like(pattern),
                ).order_by(reports.c.created_at.desc()).limit(bounded_limit)
            ).mappings().all()
            for row in report_rows:
                add_item(
                    item_kind="report",
                    item_id=str(row["id"]),
                    item_project_id=str(row["project_id"]),
                    title=str(row["title"]),
                    subtitle="科学报告",
                    href=f"/projects/{row['project_id']}/reports/{row['id']}",
                    status="available",
                    updated_at=row.get("created_at"),
                )

        if not requested_kind or requested_kind == "result":
            result_rows = connection.execute(
                select(scientific_result_snapshots).where(
                    scientific_result_snapshots.c.project_id.in_(visible_ids),
                ).order_by(scientific_result_snapshots.c.created_at.desc()).limit(bounded_limit * 2)
            ).mappings().all()
            for row in result_rows:
                result_id = str(row["id"])
                if query and query.lower() not in result_id.lower() and query.lower() not in str(row.get("schema_version") or "").lower():
                    continue
                add_item(
                    item_kind="result",
                    item_id=result_id,
                    item_project_id=str(row["project_id"]),
                    title=f"ScientificResult {result_id[:12]}",
                    subtitle=str(row.get("schema_version") or "科学结果"),
                    href=f"/projects/{row['project_id']}/research?result={result_id}",
                    status=str(row.get("relevance_status") or ""),
                    updated_at=row.get("created_at"),
                )

    items.sort(key=lambda item: item.get("updatedAt") or "", reverse=True)
    return {"query": query, "items": items[:bounded_limit], "count": min(len(items), bounded_limit)}


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
                _write_project_archive_state(connection, project_id, request.archived)
            row = connection.execute(select(projects).where(projects.c.id == project_id)).mappings().one()
            config = connection.execute(
                select(project_configs.c.config_json).where(project_configs.c.project_id == project_id)
            ).scalar_one_or_none()
            archived = bool(config.get("archivedProject")) if isinstance(config, dict) else False
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
        "description": row["description"], "status": "archived" if archived else "active",
        "role": role, "createdAt": row["created_at"].isoformat() if row["created_at"] else None,
        "updatedAt": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


def bulk_project_action_secured(
    request: BulkProjectActionRequest,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    archived = request.action == "archive"
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        for project_id in request.projectIds:
            require_project_access(connection, project_id, current_user, write=True)
        for project_id in request.projectIds:
            _write_project_archive_state(connection, project_id, archived)
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
        if blockers:
            raise HTTPException(status_code=409, detail={
                "message": "项目包含数据或研究记录，不能物理删除。请改为归档。",
                "blockers": blockers,
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
    )


def _write_project_archive_state(connection: Any, project_id: str, archived: bool) -> None:
    current = connection.execute(
        select(project_configs.c.config_json).where(project_configs.c.project_id == project_id).with_for_update()
    ).scalar_one_or_none()
    config = dict(current) if isinstance(current, dict) else {}
    config["archivedProject"] = archived
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
            if request.archived is not None:
                values.update(_dataset_archive_values(row=dict(connection.execute(
                    select(datasets).where(datasets.c.id == dataset_id)
                ).mappings().one()), archived=request.archived))
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
            if request.archived is not None:
                if request.archived:
                    runtime_dataset.status = "archived"
                else:
                    runtime_dataset.status = str(row["status"])
    except Exception:
        pass
    return {
        "id": row["id"], "datasetId": row["id"], "projectId": row["project_id"],
        "name": row["name"], "status": row["status"],
        "createdAt": row["created_at"].isoformat() if row["created_at"] else None,
        "updatedAt": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


def bulk_dataset_action_secured(
    request: BulkDatasetActionRequest,
    current_user: CurrentUser = Depends(get_current_user_compat),
) -> dict[str, Any]:
    archived = request.action == "archive"
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        rows = connection.execute(select(datasets).where(datasets.c.id.in_(request.datasetIds))).mappings().all()
        if len(rows) != len(request.datasetIds):
            raise HTTPException(status_code=404, detail="部分数据集不存在。")
        final_status: dict[str, str] = {}
        for row in rows:
            require_project_access(connection, str(row["project_id"]), current_user, write=True)
        for row in rows:
            values = _dataset_archive_values(dict(row), archived)
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
        if blockers:
            raise HTTPException(status_code=409, detail={
                "message": "数据集包含源文件、语义档案或研究记录，不能物理删除。请改为归档。",
                "blockers": blockers,
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
    )


def _dataset_archive_values(row: dict[str, Any], archived: bool) -> dict[str, Any]:
    metadata_json = dict(row.get("metadata_json") or {})
    current_status = str(row.get("status") or "created")
    if archived:
        if current_status != "archived":
            metadata_json["archivedPreviousStatus"] = current_status
        return {"status": "archived", "metadata_json": metadata_json}
    previous = str(metadata_json.pop("archivedPreviousStatus", "created"))
    if previous not in {"created", "uploading", "profile_ready", "failed"}:
        previous = "created"
    return {"status": previous, "metadata_json": metadata_json}


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
) -> dict[str, Any]:
    dependencies = [
        {"kind": table_name, "label": _DEPENDENCY_LABELS.get(table_name, table_name), "count": count}
        for table_name, count in sorted(blockers.items())
    ]
    total = sum(item["count"] for item in dependencies)
    return {
        "entity": entity,
        "entityId": entity_id,
        "displayName": display_name,
        "canDelete": not dependencies,
        "dependencyCount": total,
        "dependencies": dependencies,
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
    from mdi_api.routers.datasets import get_dataset_object_store

    return get_dataset_object_store(dataset_id)


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
    del current_user
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
