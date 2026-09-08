"""Compatibility facade for workspace projection behavior."""

from mdi_api.application.workspaces.projection import WorkspaceProjectionService
from mdi_api.domain.workspaces.contracts import WorkspaceDomainError, WorkspaceSnapshot

__all__ = ["WorkspaceDomainError", "WorkspaceProjectionService", "WorkspaceSnapshot"]
