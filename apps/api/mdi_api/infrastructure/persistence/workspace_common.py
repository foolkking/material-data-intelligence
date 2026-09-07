"""Workspace persistence normalization and projection helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from mdi_schemas import (
    ScientificWorkspace,
    WorkspaceLayoutRevision,
    WorkspaceLayoutState,
    WorkspacePanel,
    WorkspaceSelectionContext,
    WorkspaceStatus,
    WORKSPACE_MAX_PANELS,
    make_layout_revision,
)
from mdi_api.infrastructure.persistence.base import _iso, _json_copy
from mdi_api.application.workspaces.ports import (
    WorkspaceCapacityError,
    WorkspaceConflictError,
    WorkspaceRepositoryError,
    WorkspaceScopeError,
)











_WORKSPACE_UNSET = object()

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


__all__ = []
