from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException

from mdi_api.project_history import ProjectHistoryService
from mdi_api.routers.auth import CurrentUser, get_current_user_stub
from mdi_api.routers.planner import _planner_read_repositories


def get_project_history(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user_stub),
) -> dict[str, Any]:
    repositories = _planner_read_repositories(None)
    try:
        project = repositories.projects.get(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found.") from None
    owner_id = project.get("createdBy") or project.get("created_by")
    if owner_id and owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Current user cannot access this Project.")
    return ProjectHistoryService(repositories).build(project_id)

