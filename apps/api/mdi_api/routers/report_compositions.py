from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from mdi_api.report_composition import ReportCompositionDomainError, ReportCompositionService
from mdi_api.routers.auth import CurrentUser, get_current_user_stub
from mdi_api.routers.planner import _planner_read_repositories
from mdi_api.routers.workspaces import _require_workspace_access
from mdi_api.workspaces import WorkspaceDomainError
from mdi_schemas import (
    REPORT_COMPOSITION_MAX_REQUEST_BYTES,
    ReportCompositionRequest,
    strict_report_composition_json_loads,
)


def _composition_service() -> ReportCompositionService:
    return ReportCompositionService(_planner_read_repositories(None))


def _authorize(service: ReportCompositionService, workspace_id: str, current_user: CurrentUser) -> None:
    _require_workspace_access(service.projector.workspace_service, workspace_id, current_user)


async def _read_composition_request(request: Request) -> ReportCompositionRequest:
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type and content_type != "application/json":
        raise ReportCompositionDomainError("REPORT_VALIDATION_FAILED", "Report composition requires application/json.", 415)
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > REPORT_COMPOSITION_MAX_REQUEST_BYTES:
                raise ReportCompositionDomainError("REPORT_CAP_EXCEEDED", "Report composition request exceeds the byte cap.", 413)
        except ValueError as exc:
            raise ReportCompositionDomainError("REPORT_VALIDATION_FAILED", "Content-Length is invalid.", 400) from exc
    chunks: list[bytes] = []
    received = 0
    async for chunk in request.stream():
        received += len(chunk)
        if received > REPORT_COMPOSITION_MAX_REQUEST_BYTES:
            raise ReportCompositionDomainError("REPORT_CAP_EXCEEDED", "Report composition request exceeds the byte cap.", 413)
        chunks.append(chunk)
    try:
        raw = b"".join(chunks).decode("utf-8")
        parsed = strict_report_composition_json_loads(raw)
    except (UnicodeDecodeError, TypeError, ValueError) as exc:
        raise ReportCompositionDomainError("REPORT_VALIDATION_FAILED", "Report composition JSON is invalid or unsafe.", 400) from exc
    if not isinstance(parsed, dict):
        raise ReportCompositionDomainError("REPORT_VALIDATION_FAILED", "Report composition must be one JSON object.", 400)
    try:
        return ReportCompositionRequest.model_validate(parsed)
    except ValidationError as exc:
        raise ReportCompositionDomainError("REPORT_VALIDATION_FAILED", "Report composition failed strict contract validation.", 422) from exc


def _safe_http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ReportCompositionDomainError):
        return HTTPException(status_code=exc.status_code, detail=exc.as_detail())
    if isinstance(exc, WorkspaceDomainError):
        return HTTPException(status_code=exc.status_code, detail=exc.as_detail())
    return HTTPException(
        status_code=500,
        detail={"code": "REPORT_INTERNAL_ERROR", "message": "Report composition could not be completed.", "retryable": False},
    )


async def get_report_composition_sources(
    workspace_id: str,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> Response:
    try:
        service = _composition_service()
        _authorize(service, workspace_id, current_user)
        body = service.source_inventory(workspace_id)
        return JSONResponse(content=body, headers={"ETag": f'"{body["workspaceProjectionHash"]}"', "Cache-Control": "private, no-cache"})
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def preview_report_composition(
    workspace_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> Response:
    try:
        service = _composition_service()
        _authorize(service, workspace_id, current_user)
        body = await _read_composition_request(request)
        if body.workspaceId != workspace_id:
            raise ReportCompositionDomainError("SOURCE_SCOPE_MISMATCH", "Request Workspace identity does not match the route.", 403)
        preview = service.preview(body)
        return JSONResponse(content=preview.as_dict(), headers={"ETag": f'"{preview.report.reportHash}"', "Cache-Control": "no-store"})
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def finalize_report_composition(
    workspace_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> Response:
    try:
        idempotency_key = request.headers.get("idempotency-key")
        if idempotency_key is None:
            raise ReportCompositionDomainError("REPORT_VALIDATION_FAILED", "Idempotency-Key is required.", 400)
        service = _composition_service()
        _authorize(service, workspace_id, current_user)
        body = await _read_composition_request(request)
        if body.workspaceId != workspace_id:
            raise ReportCompositionDomainError("SOURCE_SCOPE_MISMATCH", "Request Workspace identity does not match the route.", 403)
        result = service.finalize(body, idempotency_key=idempotency_key.strip(), created_by=current_user.id)
        return JSONResponse(
            status_code=200 if result["idempotentReplay"] else 201,
            content=result,
            headers={
                "ETag": f'"{result["reportHash"]}"',
                "X-Idempotent-Replay": "true" if result["idempotentReplay"] else "false",
                "Cache-Control": "no-store",
            },
        )
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def list_report_compositions(
    workspace_id: str,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> dict[str, Any]:
    try:
        service = _composition_service()
        _authorize(service, workspace_id, current_user)
        return service.list_history(workspace_id)
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def get_report_composition(
    workspace_id: str,
    report_id: str,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> dict[str, Any]:
    try:
        service = _composition_service()
        _authorize(service, workspace_id, current_user)
        return service.get_report(workspace_id, report_id)
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def get_report_composition_recipe(
    workspace_id: str,
    report_id: str,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> dict[str, Any]:
    try:
        service = _composition_service()
        _authorize(service, workspace_id, current_user)
        return service.get_recipe(workspace_id, report_id)
    except Exception as exc:
        raise _safe_http_error(exc) from None


async def export_report_composition(
    workspace_id: str,
    report_id: str,
    format: str,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> Response:
    try:
        service = _composition_service()
        _authorize(service, workspace_id, current_user)
        exported = service.export(workspace_id, report_id, format)
        return Response(
            content=exported["content"].encode("utf-8"),
            media_type=exported["contentType"].split(";", 1)[0],
            headers={
                "Content-Disposition": f'attachment; filename="{exported["filename"]}"',
                "X-Report-Export-Hash": exported["manifest"]["exportHash"],
                "Cache-Control": "private, no-store",
            },
        )
    except Exception as exc:
        raise _safe_http_error(exc) from None


__all__ = [
    "export_report_composition",
    "finalize_report_composition",
    "get_report_composition",
    "get_report_composition_recipe",
    "get_report_composition_sources",
    "list_report_compositions",
    "preview_report_composition",
]
