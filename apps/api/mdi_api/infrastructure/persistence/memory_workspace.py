"""In-memory scientific workspace persistence."""

from __future__ import annotations

from threading import RLock
from typing import Any, Mapping

from mdi_schemas import (
    ScientificWorkspace,
    WorkspaceLayoutRevision,
    WorkspaceLayoutState,
    WorkspacePanel,
    WorkspaceSelectionContext,
    WORKSPACE_MAX_LAYOUT_REVISIONS,
    WORKSPACE_MAX_PANELS,
)
from mdi_api.application.workspaces.ports import (
    WorkspaceCapacityError,
    WorkspaceConflictError,
    WorkspaceNotFoundError,
)
from mdi_api.infrastructure.persistence.workspace_common import (
    _WORKSPACE_UNSET,
    _enforce_workspace_project,
    _parse_workspace,
    _parse_workspace_layout_revision,
    _parse_workspace_panel,
    _prepare_workspace_update,
    _validate_layout_panel_membership,
    _validate_panel_project_scope,
    _validate_workspace_create_aggregate,
    _workspace_layout_record,
    _workspace_layout_values,
    _workspace_panel_record,
    _workspace_panel_values,
    _workspace_record,
    _workspace_source_identity,
    _workspace_values,
)

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

__all__ = ["InMemoryWorkspaceRepository"]
