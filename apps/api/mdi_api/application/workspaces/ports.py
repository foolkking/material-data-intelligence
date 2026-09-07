"""Application contract for scientific workspace persistence."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from mdi_schemas import (
    ScientificWorkspace,
    WorkspaceLayoutRevision,
    WorkspaceLayoutState,
    WorkspacePanel,
    WorkspaceSelectionContext,
)


class WorkspaceRepositoryError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class WorkspaceConflictError(WorkspaceRepositoryError):
    pass


class WorkspaceScopeError(WorkspaceRepositoryError):
    pass


class WorkspaceCapacityError(WorkspaceRepositoryError):
    pass


class WorkspaceNotFoundError(LookupError):
    def __init__(self, code: str = "WORKSPACE_NOT_FOUND") -> None:
        self.code = code
        super().__init__(code)


class WorkspaceRepository(Protocol):
    def create_workspace(
        self,
        workspace: ScientificWorkspace | Mapping[str, Any],
        *,
        panels: list[WorkspacePanel | Mapping[str, Any]] | tuple[WorkspacePanel | Mapping[str, Any], ...] = (),
        initial_layout: WorkspaceLayoutRevision | Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...

    def get(self, workspace_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        ...

    def get_by_project_job(self, project_id: str, source_job_id: str) -> dict[str, Any]:
        ...

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        ...

    def save_panel(
        self,
        panel: WorkspacePanel | Mapping[str, Any],
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        ...

    def get_panel(
        self,
        workspace_id: str,
        panel_id: str,
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        ...

    def list_panels(self, workspace_id: str, *, project_id: str | None = None) -> list[dict[str, Any]]:
        ...

    def append_layout_revision(
        self,
        revision: WorkspaceLayoutRevision | Mapping[str, Any],
        *,
        expected_revision: int,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        ...

    def get_layout_revision(
        self,
        workspace_id: str,
        revision: int,
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        ...

    def get_current_layout(self, workspace_id: str, *, project_id: str | None = None) -> dict[str, Any] | None:
        ...

    def list_layout_revisions(
        self,
        workspace_id: str,
        *,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        ...

    def update_workspace(
        self,
        workspace_id: str,
        *,
        expected_revision: int,
        project_id: str | None = None,
        title: str | object = ...,
        active_panel_id: str | None | object = ...,
        pinned_selection: WorkspaceSelectionContext | Mapping[str, Any] | None | object = ...,
        layout: WorkspaceLayoutState | Mapping[str, Any] | None = None,
        layout_revision: WorkspaceLayoutRevision | Mapping[str, Any] | None = None,
        created_by: str | None = None,
    ) -> dict[str, Any]:
        ...



__all__ = [
    "WorkspaceCapacityError",
    "WorkspaceConflictError",
    "WorkspaceNotFoundError",
    "WorkspaceRepository",
    "WorkspaceRepositoryError",
    "WorkspaceScopeError",
]
