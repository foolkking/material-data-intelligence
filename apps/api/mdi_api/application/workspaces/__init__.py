"""Application workspace persistence contracts."""

from .ports import (
    WorkspaceCapacityError,
    WorkspaceConflictError,
    WorkspaceNotFoundError,
    WorkspaceRepository,
    WorkspaceRepositoryError,
    WorkspaceScopeError,
)

__all__ = [
    "WorkspaceCapacityError",
    "WorkspaceConflictError",
    "WorkspaceNotFoundError",
    "WorkspaceRepository",
    "WorkspaceRepositoryError",
    "WorkspaceScopeError",
]
