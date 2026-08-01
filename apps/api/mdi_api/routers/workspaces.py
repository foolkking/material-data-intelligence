from __future__ import annotations

import re
from typing import Any, Mapping

from fastapi import Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from mdi_api.routers.auth import CurrentUser, get_current_user_stub
from mdi_api.routers.planner import _planner_read_repositories
from mdi_api.workspaces import (
    WorkspaceDomainError,
    WorkspaceProjectionService,
    WorkspaceSnapshot,
)
from mdi_schemas.workspace import (
    WORKSPACE_MAX_MUTATION_BYTES,
    WORKSPACE_MAX_PANELS,
    WorkspaceLayoutState,
    WorkspaceSelectionContext,
    strict_workspace_json_loads,
    workspace_semantic_hash,
)


_IDEMPOTENCY_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_ETAG = re.compile(r'^"([0-9a-f]{64})"$')


class _StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class WorkspaceCreateRequest(_StrictRequest):
    sourceJobId: str = Field(min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=256)


class WorkspacePanelVisibilityPatch(_StrictRequest):
    panelId: str = Field(min_length=1, max_length=64)
    visible: bool


class WorkspacePatchRequest(_StrictRequest):
    title: str | None = Field(default=None, min_length=1, max_length=256)
    activePanelId: str | None = Field(default=None, max_length=64)
    panelVisibility: tuple[WorkspacePanelVisibilityPatch, ...] | None = Field(
        default=None,
        max_length=WORKSPACE_MAX_PANELS,
    )
    layout: WorkspaceLayoutState | None = None
    pinnedSelection: WorkspaceSelectionContext | None = None


def _repositories() -> Any:
    return _planner_read_repositories(None)


def _service() -> WorkspaceProjectionService:
    return WorkspaceProjectionService(_repositories())


def _require_project_access(
    service: WorkspaceProjectionService,
    project_id: str,
    current_user: CurrentUser,
) -> Mapping[str, Any]:
    project = service.get_project(project_id)
    owner_id = project.get("createdBy") or project.get("created_by")
    if owner_id != current_user.id:
        raise WorkspaceDomainError(
            "PROJECT_ACCESS_DENIED",
            "Current user cannot access this Project.",
            403,
        )
    return project


def _require_workspace_access(
    service: WorkspaceProjectionService,
    workspace_id: str,
    current_user: CurrentUser,
) -> Any:
    workspace = service.get_stored_workspace(workspace_id)
    _require_project_access(service, workspace.projectId, current_user)
    return workspace


async def _read_request_model(request: Request, model: type[_StrictRequest]) -> _StrictRequest:
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type and content_type != "application/json":
        raise WorkspaceDomainError(
            "CONTENT_TYPE_UNSUPPORTED",
            "Workspace mutations require application/json.",
            415,
        )
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            declared_length = int(content_length)
        except ValueError as exc:
            raise WorkspaceDomainError(
                "CONTENT_LENGTH_INVALID",
                "Content-Length is invalid.",
                400,
            ) from exc
        if declared_length > WORKSPACE_MAX_MUTATION_BYTES:
            raise WorkspaceDomainError(
                "WORKSPACE_PAYLOAD_CAP_EXCEEDED",
                "Workspace mutation exceeds the serialized byte cap.",
                413,
            )

    chunks: list[bytes] = []
    received = 0
    async for chunk in request.stream():
        received += len(chunk)
        if received > WORKSPACE_MAX_MUTATION_BYTES:
            raise WorkspaceDomainError(
                "WORKSPACE_PAYLOAD_CAP_EXCEEDED",
                "Workspace mutation exceeds the serialized byte cap.",
                413,
            )
        chunks.append(chunk)
    try:
        raw = b"".join(chunks).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise WorkspaceDomainError(
            "WORKSPACE_JSON_INVALID",
            "Workspace mutation must be UTF-8 JSON.",
            400,
        ) from exc
    if not raw:
        raise WorkspaceDomainError(
            "WORKSPACE_JSON_INVALID",
            "Workspace mutation body is required.",
            400,
        )
    try:
        parsed = strict_workspace_json_loads(
            raw,
            max_bytes=WORKSPACE_MAX_MUTATION_BYTES,
        )
    except (TypeError, ValueError) as exc:
        raise WorkspaceDomainError(
            "WORKSPACE_JSON_INVALID",
            "Workspace mutation JSON is invalid or unsafe.",
            400,
        ) from exc
    if not isinstance(parsed, dict):
        raise WorkspaceDomainError(
            "WORKSPACE_JSON_INVALID",
            "Workspace mutation must be one JSON object.",
            400,
        )
    try:
        return model.model_validate(parsed)
    except ValidationError as exc:
        raise WorkspaceDomainError(
            "WORKSPACE_CONTRACT_INVALID",
            "Workspace mutation failed strict contract validation.",
            422,
        ) from exc


def _format_etag(value: str) -> str:
    return f'"{value}"'


def _parse_etag(value: str | None, *, required: bool) -> str | None:
    if value is None:
        if required:
            raise WorkspaceDomainError(
                "IF_MATCH_REQUIRED",
                "If-Match is required for Workspace mutation.",
                412,
            )
        return None
    match = _ETAG.fullmatch(value.strip())
    if match is None:
        raise WorkspaceDomainError(
            "ETAG_INVALID",
            "Workspace ETag is malformed.",
            400,
        )
    return match.group(1)


def _not_modified(request: Request, etag: str) -> bool:
    value = request.headers.get("if-none-match")
    if value is None:
        return False
    if value.strip() == "*":
        return True
    candidates = [item.strip() for item in value.split(",")]
    parsed = {_parse_etag(item, required=False) for item in candidates}
    return etag in parsed


def _snapshot_response(
    snapshot: WorkspaceSnapshot,
    *,
    status_code: int = 200,
    idempotent_replay: bool | None = None,
) -> JSONResponse:
    headers = {
        "ETag": _format_etag(snapshot.etag),
        "Cache-Control": "private, no-cache",
    }
    if idempotent_replay is not None:
        headers["X-Idempotent-Replay"] = "true" if idempotent_replay else "false"
    return JSONResponse(status_code=status_code, content=snapshot.body, headers=headers)


def _safe_http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, WorkspaceDomainError):
        return HTTPException(status_code=exc.status_code, detail=exc.as_detail())
    return HTTPException(
        status_code=500,
        detail={
            "code": "WORKSPACE_INTERNAL_ERROR",
            "message": "Workspace request could not be completed.",
            "retryable": False,
        },
    )


async def create_workspace(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> Response:
    try:
        idempotency_key = request.headers.get("idempotency-key")
        if idempotency_key is None:
            raise WorkspaceDomainError(
                "IDEMPOTENCY_KEY_REQUIRED",
                "Idempotency-Key is required for Workspace creation.",
                400,
            )
        if _IDEMPOTENCY_KEY.fullmatch(idempotency_key.strip()) is None:
            raise WorkspaceDomainError(
                "IDEMPOTENCY_KEY_INVALID",
                "Idempotency-Key is malformed.",
                400,
            )
        body = await _read_request_model(request, WorkspaceCreateRequest)
        assert isinstance(body, WorkspaceCreateRequest)
        service = _service()
        job = service.get_job(body.sourceJobId)
        project_id = str(job.get("projectId") or job.get("project_id") or "")
        if not project_id:
            raise WorkspaceDomainError(
                "JOB_PROJECT_MISSING",
                "The source job has no exact Project identity.",
                409,
            )
        _require_project_access(service, project_id, current_user)
        snapshot, created = service.project_job(
            source_job_id=body.sourceJobId,
            created_by=current_user.id,
            title=body.title,
        )
        return _snapshot_response(
            snapshot,
            status_code=201 if created else 200,
            idempotent_replay=not created,
        )
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def get_workspace(
    workspace_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> Response:
    try:
        service = _service()
        _require_workspace_access(service, workspace_id, current_user)
        snapshot = service.get_snapshot(workspace_id)
        if _not_modified(request, snapshot.etag):
            return Response(
                status_code=304,
                headers={
                    "ETag": _format_etag(snapshot.etag),
                    "Cache-Control": "private, no-cache",
                },
            )
        return _snapshot_response(snapshot)
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def patch_workspace(
    workspace_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> Response:
    try:
        supplied_etag = _parse_etag(request.headers.get("if-match"), required=True)
        service = _service()
        stored = _require_workspace_access(service, workspace_id, current_user)
        current_snapshot = service.get_snapshot(workspace_id)
        if supplied_etag != current_snapshot.etag:
            raise WorkspaceDomainError(
                "REVISION_MISMATCH",
                "Workspace revision does not match If-Match.",
                412,
            )
        body = await _read_request_model(request, WorkspacePatchRequest)
        assert isinstance(body, WorkspacePatchRequest)
        if not body.model_fields_set:
            raise WorkspaceDomainError(
                "WORKSPACE_PATCH_EMPTY",
                "Workspace patch must contain at least one mutable field.",
                422,
            )
        changes: dict[str, Any] = {}
        for field in body.model_fields_set:
            value = getattr(body, field)
            if isinstance(value, BaseModel):
                changes[field] = value.model_dump(mode="json", by_alias=True)
            elif isinstance(value, tuple):
                changes[field] = [
                    item.model_dump(mode="json", by_alias=True)
                    if isinstance(item, BaseModel)
                    else item
                    for item in value
                ]
            else:
                changes[field] = value
        snapshot = service.patch_workspace(
            workspace_id=workspace_id,
            expected_revision=stored.revision,
            changes=changes,
            updated_by=current_user.id,
        )
        return _snapshot_response(snapshot)
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def list_project_workspaces(
    project_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None, min_length=1, max_length=96),
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> dict[str, Any]:
    try:
        service = _service()
        _require_project_access(service, project_id, current_user)
        return service.list_project_workspaces(
            project_id=project_id,
            limit=limit,
            cursor=cursor,
        )
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def list_analysis_jobs(
    project_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None, min_length=1, max_length=64),
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> dict[str, Any]:
    try:
        service = _service()
        _require_project_access(service, project_id, current_user)
        return service.list_analysis_jobs(
            project_id=project_id,
            limit=limit,
            cursor=cursor,
        )
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def list_workspace_panels(
    workspace_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> Response:
    try:
        service = _service()
        _require_workspace_access(service, workspace_id, current_user)
        panels = service.list_panels(workspace_id)
        body = {
            "workspaceId": workspace_id,
            "items": [
                panel.model_dump(mode="json", by_alias=True) for panel in panels
            ],
        }
        etag = workspace_semantic_hash(body)
        if _not_modified(request, etag):
            return Response(status_code=304, headers={"ETag": _format_etag(etag)})
        return JSONResponse(
            content=body,
            headers={"ETag": _format_etag(etag), "Cache-Control": "private, no-cache"},
        )
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def get_workspace_panel(
    workspace_id: str,
    panel_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> Response:
    try:
        service = _service()
        _require_workspace_access(service, workspace_id, current_user)
        panel = service.get_panel(workspace_id, panel_id)
        body = panel.model_dump(mode="json", by_alias=True)
        etag = panel.panelStateHash
        if _not_modified(request, etag):
            return Response(status_code=304, headers={"ETag": _format_etag(etag)})
        return JSONResponse(
            content=body,
            headers={"ETag": _format_etag(etag), "Cache-Control": "private, no-cache"},
        )
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def list_workspace_layout_revisions(
    workspace_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> Response:
    try:
        service = _service()
        _require_workspace_access(service, workspace_id, current_user)
        revisions = service.list_layout_revisions(workspace_id)
        body = {
            "workspaceId": workspace_id,
            "items": [
                revision.model_dump(mode="json", by_alias=True)
                for revision in revisions
            ],
        }
        etag = workspace_semantic_hash(body)
        if _not_modified(request, etag):
            return Response(status_code=304, headers={"ETag": _format_etag(etag)})
        return JSONResponse(
            content=body,
            headers={"ETag": _format_etag(etag), "Cache-Control": "private, no-cache"},
        )
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def get_workspace_layout_revision(
    workspace_id: str,
    revision: int,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> Response:
    try:
        service = _service()
        _require_workspace_access(service, workspace_id, current_user)
        record = service.get_layout_revision(workspace_id, revision)
        body = record.model_dump(mode="json", by_alias=True)
        etag = record.semanticHash
        if _not_modified(request, etag):
            return Response(status_code=304, headers={"ETag": _format_etag(etag)})
        return JSONResponse(
            content=body,
            headers={"ETag": _format_etag(etag), "Cache-Control": "private, no-cache"},
        )
    except Exception as exc:
        raise _safe_http_error(exc) from None
