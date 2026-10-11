from datetime import datetime
from typing import Literal
from fastapi import Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, insert, select
from mdi_api.db import platform_model_offerings, user_model_plan_grants, users
from mdi_api.provider_connections import get_connection
from mdi_api.transport.routers.auth import CurrentUser, get_current_user, require_platform_admin
from mdi_api.user_models import _engine


class OfferingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: str = Field(min_length=1, max_length=64)
    model: str = Field(min_length=1, max_length=128)
    label: str = Field(min_length=1, max_length=120)
    protocol: Literal["openai_chat_json", "openai_chat", "openai_responses", "anthropic"]
    audience: Literal["all", "plans"]
    plans: list[str] = Field(default_factory=list, max_length=100)
    enabled: bool = True


class PlanGrantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool
    expiresAt: datetime | None = None


def list_offerings(current_user: CurrentUser = Depends(get_current_user)):
    require_platform_admin(current_user)
    with _engine().connect() as db:
        return [dict(row) for row in db.execute(select(platform_model_offerings)).mappings()]


def save_offering(offering_id: str, request: OfferingRequest, current_user: CurrentUser = Depends(get_current_user)):
    require_platform_admin(current_user)
    if not offering_id or len(offering_id) > 64 or not request.model.strip():
        raise HTTPException(422, "Invalid model offering identity")
    if get_connection(request.provider) is None:
        raise HTTPException(422, "Configure the platform provider connection first")
    plans = list(dict.fromkeys(request.plans))
    if any(not plan.strip() or len(plan) > 64 for plan in plans) or (request.audience == "plans" and not plans):
        raise HTTPException(422, "A plan-scoped model requires valid plan identifiers")
    values = request.model_dump(exclude={"plans"})
    with _engine().begin() as db:
        db.execute(delete(platform_model_offerings).where(platform_model_offerings.c.id == offering_id))
        db.execute(insert(platform_model_offerings).values(id=offering_id, plans_json=plans, **values))
    return {"ok": True}


def save_plan_grant(user_id: str, plan: str, request: PlanGrantRequest, current_user: CurrentUser = Depends(get_current_user)):
    require_platform_admin(current_user)
    if not plan.strip() or len(plan) > 64 or (request.expiresAt and request.expiresAt.tzinfo is None):
        raise HTTPException(422, "Use a valid plan identifier and timezone-aware expiry")
    with _engine().begin() as db:
        if db.execute(select(users.c.id).where(users.c.id == user_id)).scalar_one_or_none() is None:
            raise HTTPException(404, "Account not found")
        db.execute(delete(user_model_plan_grants).where(user_model_plan_grants.c.user_id == user_id, user_model_plan_grants.c.plan == plan))
        if request.enabled:
            db.execute(insert(user_model_plan_grants).values(user_id=user_id, plan=plan, expires_at=request.expiresAt))
    return {"ok": True}
