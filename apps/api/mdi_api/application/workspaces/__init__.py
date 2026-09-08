"""Application workspace persistence contracts."""

from mdi_api.domain.workspaces import WorkspaceDomainError, WorkspaceSnapshot

from .ports import (
    WorkspaceCapacityError,
    WorkspaceConflictError,
    WorkspaceNotFoundError,
    WorkspaceRepository,
    WorkspaceRepositoryError,
    WorkspaceScopeError,
)
from .projection import WorkspaceProjectionService

__all__ = [
    "WorkspaceCapacityError",
    "WorkspaceConflictError",
    "WorkspaceNotFoundError",
    "WorkspaceRepository",
    "WorkspaceRepositoryError",
    "WorkspaceScopeError",
    "WorkspaceDomainError",
    "WorkspaceProjectionService",
    "WorkspaceSnapshot",
]
