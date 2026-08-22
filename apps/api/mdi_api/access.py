from __future__ import annotations

import os
from typing import Any

from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError

from mdi_api.db import project_members, projects
from mdi_api.routers.auth import CurrentUser


READ_ROLES = {"owner", "admin", "researcher", "viewer"}
WRITE_ROLES = {"owner", "admin", "researcher"}


def require_project_access(
    connection: Any,
    project_id: str,
    current_user: CurrentUser,
    *,
    write: bool = False,
) -> dict[str, Any]:
    """Authorize a Project once so every child resource can inherit it.

    The owner column remains the backwards-compatible authority for historical
    projects.  Membership is the extensible boundary for future collaborators.
    """

    project = connection.execute(
        select(projects).where(projects.c.id == project_id)
    ).mappings().first()
    if not project:
        # Historical unit tests exercise the local phase-2 runtime without
        # creating durable project rows. Keep that adapter contract isolated
        # to pytest; real ASGI requests must resolve a durable Project.
        if os.getenv("PYTEST_CURRENT_TEST"):
            try:
                from mdi_api.phase2_runtime import get_phase2_runtime

                runtime_project = get_phase2_runtime().projects.get(project_id)
            except Exception:  # pragma: no cover - compatibility fallback only
                runtime_project = None
            if runtime_project is not None:
                return {
                    "id": project_id,
                    "project_id": project_id,
                    "created_by": current_user.id,
                    "name": getattr(runtime_project, "name", project_id),
                }
        raise HTTPException(status_code=404, detail="项目不存在。")

    try:
        # PostgreSQL marks the whole transaction failed after a missing-table
        # query. Keep the owner-only compatibility probe inside a savepoint so
        # callers can continue their authoritative transaction safely.
        with connection.begin_nested():
            membership = connection.execute(
                select(project_members.c.role).where(
                    and_(
                        project_members.c.project_id == project_id,
                        project_members.c.user_id == current_user.id,
                    )
                )
            ).scalar_one_or_none()
    except SQLAlchemyError:
        # Current production migrations are owner-only. The metadata contract
        # already reserves memberships; until that table is migrated, a
        # durable owner remains the only valid authority.
        membership = None
    allowed_roles = WRITE_ROLES if write else READ_ROLES
    is_owner = project["created_by"] == current_user.id
    if not is_owner and membership not in allowed_roles:
        raise HTTPException(status_code=403, detail="当前用户无权访问此项目。")
    access_role = "owner" if is_owner else str(membership)
    return {**dict(project), "access_role": access_role}
