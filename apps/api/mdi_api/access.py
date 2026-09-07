from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from mdi_api.application.research.ports import (
    ProjectAccessDenied,
    ProjectAccessNotFound,
    ResearchActor,
)
from mdi_api.infrastructure.project_access import (
    READ_ROLES,
    SQLALCHEMY_PROJECT_ACCESS,
    WRITE_ROLES,
)


def require_project_access(
    connection: Any,
    project_id: str,
    current_user: ResearchActor,
    *,
    write: bool = False,
) -> dict[str, Any]:
    """Authorize a Project once so every child resource can inherit it.

    The owner column remains the backwards-compatible authority for historical
    projects.  Membership is the extensible boundary for future collaborators.
    """

    try:
        return SQLALCHEMY_PROJECT_ACCESS.require(
            connection,
            project_id,
            current_user,
            write=write,
        )
    except ProjectAccessNotFound as exc:
        raise HTTPException(status_code=404, detail="项目不存在。") from exc
    except ProjectAccessDenied as exc:
        raise HTTPException(status_code=403, detail="当前用户无权访问此项目。") from exc
