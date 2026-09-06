from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal
import uuid
import secrets

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import and_, delete, func, insert, or_, select, update

from mdi_api.config import load_settings
from mdi_api.database import create_engine_from_settings
from mdi_api.db import account_invitations, audit_logs, auth_sessions, project_members, projects, users
from mdi_api.operations import build_operations_snapshot
from mdi_api.routers.auth import (
    CurrentUser,
    PLATFORM_ROLE_ADMIN,
    PlatformRole,
    _token_hash,
    get_current_user,
    require_platform_admin,
)


AdminUserStatus = Literal["ALL", "ACTIVE", "INACTIVE"]
AdminUserRole = Literal["ALL", "USER", "PLATFORM_ADMIN"]
ProjectMemberRole = Literal["owner", "admin", "researcher", "viewer"]


class PlatformUserUpdateRequest(BaseModel):
    platformRole: PlatformRole | None = None
    isActive: bool | None = None


class PlatformProjectMemberUpdateRequest(BaseModel):
    role: ProjectMemberRole


class PlatformInvitationRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    displayName: str = Field(min_length=1, max_length=160)
    expiresInDays: int = Field(default=7, ge=1, le=30)


def create_platform_invitation(
    request: PlatformInvitationRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    require_platform_admin(current_user)
    email = request.email.strip().lower()
    display_name = request.displayName.strip()
    raw_token = secrets.token_urlsafe(48)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=request.expiresInDays)
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        existing_user = connection.execute(select(users.c.id).where(users.c.email == email)).first()
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail={"code": "ADMIN_INVITATION_ACCOUNT_EXISTS", "message": "该邮箱已经存在账户。"},
            )
        connection.execute(
            update(account_invitations)
            .where(
                and_(
                    account_invitations.c.email == email,
                    account_invitations.c.accepted_at.is_(None),
                    account_invitations.c.revoked_at.is_(None),
                )
            )
            .values(revoked_at=now)
        )
        invitation_id = f"invite_{uuid.uuid4().hex}"
        connection.execute(
            insert(account_invitations).values(
                id=invitation_id,
                email=email,
                display_name=display_name,
                token_hash=_token_hash(raw_token),
                expires_at=expires,
                invited_by_user_id=current_user.id,
            )
        )
        _write_admin_audit(
            connection,
            actor=current_user,
            action="platform.account.invited",
            target_id=invitation_id,
            metadata={"email": email, "expiresAt": expires.isoformat()},
        )
    return {
        "id": invitation_id,
        "email": email,
        "displayName": display_name,
        "expiresAt": expires.isoformat(),
        "activationToken": raw_token,
    }


def list_platform_projects(
    q: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=100_000),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    """Return a bounded platform-admin project catalog for access governance."""
    require_platform_admin(current_user)
    normalized_query = (q or "").strip().lower()
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        statement = select(
            projects.c.id,
            projects.c.name,
            projects.c.description,
            projects.c.created_by,
            projects.c.created_at,
            projects.c.updated_at,
            users.c.email.label("owner_email"),
            users.c.display_name.label("owner_display_name"),
            func.count(project_members.c.user_id).label("member_count"),
        ).select_from(
            projects.join(users, users.c.id == projects.c.created_by).outerjoin(
                project_members, project_members.c.project_id == projects.c.id
            )
        ).group_by(
            projects.c.id,
            users.c.email,
            users.c.display_name,
        ).order_by(projects.c.updated_at.desc(), projects.c.id.asc())
        if normalized_query:
            pattern = f"%{normalized_query}%"
            statement = statement.where(
                or_(
                    func.lower(projects.c.id).like(pattern),
                    func.lower(projects.c.name).like(pattern),
                    func.lower(projects.c.description).like(pattern),
                    func.lower(users.c.email).like(pattern),
                    func.lower(users.c.display_name).like(pattern),
                )
            )
        rows = connection.execute(statement.offset(offset).limit(limit)).mappings().all()
        count_statement = select(func.count()).select_from(projects)
        if normalized_query:
            count_statement = count_statement.select_from(
                projects.join(users, users.c.id == projects.c.created_by)
            ).where(
                or_(
                    func.lower(projects.c.id).like(pattern),
                    func.lower(projects.c.name).like(pattern),
                    func.lower(projects.c.description).like(pattern),
                    func.lower(users.c.email).like(pattern),
                    func.lower(users.c.display_name).like(pattern),
                )
            )
        total = int(connection.scalar(count_statement) or 0)
    return {
        "items": [
            {
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "owner": {
                    "id": row["created_by"],
                    "email": row["owner_email"],
                    "displayName": row["owner_display_name"],
                },
                "memberCount": int(row["member_count"] or 0),
                "createdAt": _iso(row["created_at"]),
                "updatedAt": _iso(row["updated_at"]),
            }
            for row in rows
        ],
        "count": len(rows),
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def list_platform_project_members(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    require_platform_admin(current_user)
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        project = connection.execute(
            select(projects.c.id, projects.c.name, projects.c.created_by).where(projects.c.id == project_id)
        ).mappings().first()
        if project is None:
            raise HTTPException(status_code=404, detail={"code": "ADMIN_PROJECT_NOT_FOUND", "message": "未找到该项目。"})
        rows = connection.execute(
            select(
                project_members.c.project_id,
                project_members.c.user_id,
                project_members.c.role,
                project_members.c.created_at,
                users.c.email,
                users.c.display_name,
                users.c.is_active,
            ).select_from(
                project_members.join(users, users.c.id == project_members.c.user_id)
            ).where(project_members.c.project_id == project_id).order_by(
                project_members.c.role.asc(), users.c.display_name.asc(), users.c.email.asc()
            )
        ).mappings().all()
    return {
        "project": {"id": project["id"], "name": project["name"], "ownerId": project["created_by"]},
        "items": [
            {
                "userId": row["user_id"],
                "email": row["email"],
                "displayName": row["display_name"],
                "role": row["role"],
                "isActive": bool(row["is_active"]),
                "createdAt": _iso(row["created_at"]),
            }
            for row in rows
        ],
        "count": len(rows),
    }


def update_platform_project_member(
    project_id: str,
    user_id: str,
    request: PlatformProjectMemberUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    require_platform_admin(current_user)
    engine = create_engine_from_settings(load_settings())
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        project = connection.execute(
            select(projects.c.id, projects.c.created_by).where(projects.c.id == project_id)
        ).mappings().first()
        if project is None:
            raise HTTPException(status_code=404, detail={"code": "ADMIN_PROJECT_NOT_FOUND", "message": "未找到该项目。"})
        user = connection.execute(select(users.c.id).where(users.c.id == user_id)).first()
        if user is None:
            raise HTTPException(status_code=404, detail={"code": "ADMIN_USER_NOT_FOUND", "message": "未找到该用户。"})
        if request.role == "owner" and project["created_by"] != user_id:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "PROJECT_OWNER_IDENTITY_IMMUTABLE",
                    "message": "项目所有者由项目创建身份固定；请为协作者选择管理员、研究者或查看者。",
                },
            )
        if project["created_by"] == user_id and request.role != "owner":
            raise HTTPException(status_code=409, detail={"code": "PROJECT_OWNER_ROLE_REQUIRED", "message": "项目所有者必须保留 owner 角色。"})
        existing = connection.execute(
            select(project_members.c.role).where(
                and_(project_members.c.project_id == project_id, project_members.c.user_id == user_id)
            )
        ).scalar_one_or_none()
        if existing is None:
            connection.execute(
                insert(project_members).values(
                    project_id=project_id,
                    user_id=user_id,
                    role=request.role,
                    created_at=now,
                )
            )
        else:
            connection.execute(
                update(project_members).where(
                    and_(project_members.c.project_id == project_id, project_members.c.user_id == user_id)
                ).values(role=request.role)
            )
        _write_admin_audit(
            connection,
            actor=current_user,
            action="platform.project.member.updated",
            target_id=f"{project_id}:{user_id}",
            metadata={"projectId": project_id, "userId": user_id, "role": request.role, "previousRole": existing},
        )
    return {"projectId": project_id, "userId": user_id, "role": request.role}


def remove_platform_project_member(
    project_id: str,
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    require_platform_admin(current_user)
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        project = connection.execute(select(projects.c.created_by).where(projects.c.id == project_id)).first()
        if project is None:
            raise HTTPException(status_code=404, detail={"code": "ADMIN_PROJECT_NOT_FOUND", "message": "未找到该项目。"})
        if project[0] == user_id:
            raise HTTPException(status_code=409, detail={"code": "PROJECT_OWNER_REMOVE_FORBIDDEN", "message": "不能移除项目所有者。"})
        result = connection.execute(
            delete(project_members).where(
                and_(project_members.c.project_id == project_id, project_members.c.user_id == user_id)
            )
        )
        if not result.rowcount:
            raise HTTPException(status_code=404, detail={"code": "PROJECT_MEMBER_NOT_FOUND", "message": "未找到该项目成员。"})
        _write_admin_audit(
            connection,
            actor=current_user,
            action="platform.project.member.removed",
            target_id=f"{project_id}:{user_id}",
            metadata={"projectId": project_id, "userId": user_id},
        )
    return {"projectId": project_id, "userId": user_id, "removed": True}


def get_platform_admin_overview(
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    require_platform_admin(current_user)
    settings = load_settings()
    engine = create_engine_from_settings(settings)
    now = datetime.now(timezone.utc)
    with engine.connect() as connection:
        counts = {
            "users": int(connection.scalar(select(func.count()).select_from(users)) or 0),
            "activeUsers": int(
                connection.scalar(
                    select(func.count()).select_from(users).where(users.c.is_active.is_(True))
                )
                or 0
            ),
            "platformAdmins": int(
                connection.scalar(
                    select(func.count())
                    .select_from(users)
                    .where(
                        and_(
                            users.c.platform_role == PLATFORM_ROLE_ADMIN,
                            users.c.is_active.is_(True),
                        )
                    )
                )
                or 0
            ),
            "projects": int(connection.scalar(select(func.count()).select_from(projects)) or 0),
            "activeSessions": int(
                connection.scalar(
                    select(func.count())
                    .select_from(auth_sessions)
                    .where(
                        and_(
                            auth_sessions.c.revoked_at.is_(None),
                            auth_sessions.c.expires_at > now,
                        )
                    )
                )
                or 0
            ),
        }
    return {
        "schemaVersion": "platform-admin-overview/1.0",
        "counts": counts,
        "operations": _sanitize_operations(build_operations_snapshot(settings)),
    }


def list_platform_users(
    q: str | None = None,
    status: AdminUserStatus = "ALL",
    role: AdminUserRole = "ALL",
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=100_000),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    require_platform_admin(current_user)
    conditions = []
    normalized_query = (q or "").strip().lower()
    if normalized_query:
        pattern = f"%{normalized_query}%"
        conditions.append(
            or_(
                func.lower(users.c.email).like(pattern),
                func.lower(users.c.display_name).like(pattern),
                func.lower(users.c.id).like(pattern),
            )
        )
    if status == "ACTIVE":
        conditions.append(users.c.is_active.is_(True))
    elif status == "INACTIVE":
        conditions.append(users.c.is_active.is_(False))
    if role != "ALL":
        conditions.append(users.c.platform_role == role)

    engine = create_engine_from_settings(load_settings())
    now = datetime.now(timezone.utc)
    with engine.connect() as connection:
        where_clause = and_(*conditions) if conditions else None
        count_statement = select(func.count()).select_from(users)
        rows_statement = select(users).order_by(
            users.c.is_active.desc(),
            users.c.display_name.asc(),
            users.c.email.asc(),
        )
        if where_clause is not None:
            count_statement = count_statement.where(where_clause)
            rows_statement = rows_statement.where(where_clause)
        rows = connection.execute(
            rows_statement.offset(offset).limit(limit)
        ).mappings().all()
        total = int(connection.scalar(count_statement) or 0)
        user_ids = [row["id"] for row in rows]
        project_counts: dict[str, int] = {}
        session_counts: dict[str, int] = {}
        if user_ids:
            project_counts = {
                user_id: int(count)
                for user_id, count in connection.execute(
                    select(project_members.c.user_id, func.count())
                    .where(project_members.c.user_id.in_(user_ids))
                    .group_by(project_members.c.user_id)
                ).all()
            }
            session_counts = {
                user_id: int(count)
                for user_id, count in connection.execute(
                    select(auth_sessions.c.user_id, func.count())
                    .where(
                        and_(
                            auth_sessions.c.user_id.in_(user_ids),
                            auth_sessions.c.revoked_at.is_(None),
                            auth_sessions.c.expires_at > now,
                        )
                    )
                    .group_by(auth_sessions.c.user_id)
                ).all()
            }
    return {
        "items": [
            _project_user(
                row,
                project_count=project_counts.get(row["id"], 0),
                active_session_count=session_counts.get(row["id"], 0),
            )
            for row in rows
        ],
        "count": len(rows),
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def update_platform_user(
    user_id: str,
    request: PlatformUserUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    require_platform_admin(current_user)
    if request.platformRole is None and request.isActive is None:
        raise HTTPException(
            status_code=422,
            detail={"code": "ADMIN_USER_UPDATE_EMPTY", "message": "未提供账户变更。"},
        )
    now = datetime.now(timezone.utc)
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        row = connection.execute(
            select(users).where(users.c.id == user_id).with_for_update()
        ).mappings().first()
        if not row:
            raise HTTPException(
                status_code=404,
                detail={"code": "ADMIN_USER_NOT_FOUND", "message": "未找到该用户。"},
            )
        requested_role = request.platformRole or row["platform_role"]
        requested_active = row["is_active"] if request.isActive is None else request.isActive
        if user_id == current_user.id and requested_role != row["platform_role"]:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "ADMIN_SELF_ROLE_CHANGE_FORBIDDEN",
                    "message": "不能修改自己的平台角色。",
                },
            )
        if user_id == current_user.id and not requested_active:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "ADMIN_SELF_DEACTIVATION_FORBIDDEN",
                    "message": "不能通过管理中心停用当前账户。",
                },
            )
        removes_active_admin = (
            row["platform_role"] == PLATFORM_ROLE_ADMIN
            and bool(row["is_active"])
            and (requested_role != PLATFORM_ROLE_ADMIN or not requested_active)
        )
        if removes_active_admin:
            active_admin_ids = connection.execute(
                select(users.c.id)
                .where(
                    and_(
                        users.c.platform_role == PLATFORM_ROLE_ADMIN,
                        users.c.is_active.is_(True),
                    )
                )
                .with_for_update()
            ).scalars().all()
            if len(active_admin_ids) <= 1:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "LAST_ACTIVE_PLATFORM_ADMIN",
                        "message": "不能移除或停用最后一名有效平台管理员。",
                    },
                )
        connection.execute(
            update(users)
            .where(users.c.id == user_id)
            .values(
                platform_role=requested_role,
                is_active=requested_active,
                updated_at=now,
            )
        )
        revoked_sessions = 0
        if not requested_active:
            result = connection.execute(
                update(auth_sessions)
                .where(
                    and_(
                        auth_sessions.c.user_id == user_id,
                        auth_sessions.c.revoked_at.is_(None),
                    )
                )
                .values(revoked_at=now)
            )
            revoked_sessions = max(0, int(result.rowcount or 0))
        _write_admin_audit(
            connection,
            actor=current_user,
            action="platform.user.updated",
            target_id=user_id,
            metadata={
                "previousPlatformRole": row["platform_role"],
                "platformRole": requested_role,
                "previousIsActive": bool(row["is_active"]),
                "isActive": bool(requested_active),
                "revokedSessions": revoked_sessions,
            },
        )
        updated = connection.execute(select(users).where(users.c.id == user_id)).mappings().one()
        project_count = int(
            connection.scalar(
                select(func.count())
                .select_from(project_members)
                .where(project_members.c.user_id == user_id)
            )
            or 0
        )
        active_session_count = int(
            connection.scalar(
                select(func.count())
                .select_from(auth_sessions)
                .where(
                    and_(
                        auth_sessions.c.user_id == user_id,
                        auth_sessions.c.revoked_at.is_(None),
                        auth_sessions.c.expires_at > now,
                    )
                )
            )
            or 0
        )
    return _project_user(
        updated,
        project_count=project_count,
        active_session_count=active_session_count,
    )


def list_platform_audit(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    require_platform_admin(current_user)
    actor = users.alias("audit_actor")
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        rows = connection.execute(
            select(
                audit_logs.c.id,
                audit_logs.c.actor_user_id,
                actor.c.email.label("actor_email"),
                audit_logs.c.action,
                audit_logs.c.target_type,
                audit_logs.c.target_id,
                audit_logs.c.metadata_json,
                audit_logs.c.created_at,
            )
            .select_from(audit_logs.outerjoin(actor, actor.c.id == audit_logs.c.actor_user_id))
            .where(audit_logs.c.project_id.is_(None))
            .order_by(audit_logs.c.created_at.desc(), audit_logs.c.id.desc())
            .limit(limit)
        ).mappings().all()
    return {
        "items": [
            {
                "id": row["id"],
                "actor": {
                    "id": row["actor_user_id"],
                    "email": row["actor_email"],
                },
                "action": row["action"],
                "targetType": row["target_type"],
                "targetId": row["target_id"],
                "metadata": _sanitize_audit_metadata(row["metadata_json"] or {}),
                "createdAt": _iso(row["created_at"]),
            }
            for row in rows
        ],
        "count": len(rows),
    }


def _project_user(
    row,
    *,
    project_count: int,
    active_session_count: int,
) -> dict[str, object]:
    return {
        "id": row["id"],
        "email": row["email"],
        "displayName": row["display_name"],
        "platformRole": row["platform_role"],
        "isActive": bool(row["is_active"]),
        "projectCount": project_count,
        "activeSessionCount": active_session_count,
        "createdAt": _iso(row["created_at"]),
        "updatedAt": _iso(row["updated_at"]),
    }


def _write_admin_audit(
    connection,
    *,
    actor: CurrentUser,
    action: str,
    target_id: str,
    metadata: dict[str, object],
) -> None:
    connection.execute(
        insert(audit_logs).values(
            id=f"audit_{uuid.uuid4().hex}",
            actor_user_id=actor.id,
            project_id=None,
            action=action,
            target_type="user",
            target_id=target_id,
            metadata_json=metadata,
        )
    )


def _sanitize_operations(snapshot: dict[str, object]) -> dict[str, object]:
    def component(name: str) -> dict[str, object]:
        raw = snapshot.get(name)
        source = raw if isinstance(raw, dict) else {}
        allowed = {
            "status",
            "backend",
            "reason",
            "connections",
            "idleInTransaction",
            "staleResearchTurns",
            "staleJobs",
            "pool",
            "totalQueued",
            "totalStarted",
            "recentFailed",
            "workerCount",
            "workerStates",
            "workerHealth",
        }
        return {key: source[key] for key in allowed if key in source}

    alerts = []
    for raw_alert in snapshot.get("alerts") or []:
        if not isinstance(raw_alert, dict):
            continue
        sanitized = {
            key: raw_alert[key]
            for key in (
                "code",
                "severity",
                "component",
                "observed",
                "threshold",
                "message",
            )
            if key in raw_alert
        }
        raw_runbook = raw_alert.get("runbook")
        if isinstance(raw_runbook, dict):
            sanitized["runbook"] = {
                key: raw_runbook[key]
                for key in (
                    "id",
                    "reference",
                    "operatorAction",
                    "recheckCommand",
                )
                if key in raw_runbook
            }
        alerts.append(sanitized)

    return {
        "status": snapshot.get("status"),
        "capturedAt": snapshot.get("capturedAt"),
        "alertsSchemaVersion": snapshot.get("alertsSchemaVersion"),
        "alertSummary": snapshot.get("alertSummary") or {},
        "alerts": alerts,
        "database": component("database"),
        "queues": component("queues"),
        "artifactStorage": component("artifactStorage"),
        "resourceGovernance": {
            "status": (snapshot.get("resourceGovernance") or {}).get("status")
            if isinstance(snapshot.get("resourceGovernance"), dict)
            else "unknown"
        },
        "storageBudgets": _sanitize_storage_budgets(
            snapshot.get("storageBudgets")
        ),
    }


def _sanitize_storage_budgets(raw: object) -> dict[str, object]:
    source = raw if isinstance(raw, dict) else {}
    categories = []
    for raw_category in source.get("categories") or []:
        if not isinstance(raw_category, dict):
            continue
        categories.append(
            {
                key: raw_category[key]
                for key in (
                    "category",
                    "scope",
                    "observedBytes",
                    "budgetBytes",
                    "utilizationPercent",
                    "state",
                    "itemCount",
                    "scanComplete",
                    "inaccessibleCount",
                )
                if key in raw_category
            }
        )
    return {
        "schemaVersion": source.get("schemaVersion"),
        "status": source.get("status"),
        "readOnly": bool(source.get("readOnly")),
        "redacted": bool(source.get("redacted")),
        "scanEntryLimit": source.get("scanEntryLimit"),
        "categories": categories,
    }


_SAFE_AUDIT_KEYS = {
    "displayNameChanged",
    "sessionId",
    "revokedCount",
    "otherSessionsRevoked",
    "provenanceRetained",
    "previousPlatformRole",
    "platformRole",
    "previousIsActive",
    "isActive",
    "revokedSessions",
}


def _sanitize_audit_metadata(value: dict[str, object]) -> dict[str, object]:
    return {key: value[key] for key in sorted(value) if key in _SAFE_AUDIT_KEYS}


def _iso(value: datetime) -> str:
    normalized = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
    return normalized.isoformat()
