"""Published platform models, distinct from server credentials and personal BYOK."""
from datetime import datetime, timezone
from sqlalchemy import select, or_
from mdi_api.db import platform_model_offerings, user_model_plan_grants
from mdi_api.provider_connections import get_connection, decrypt_api_key


def available_offerings(user_id: str) -> list[dict]:
    from mdi_api.user_models import _engine
    with _engine().connect() as db:
        plans = set(db.execute(select(user_model_plan_grants.c.plan).where(
            user_model_plan_grants.c.user_id == user_id,
            or_(user_model_plan_grants.c.expires_at.is_(None),
                user_model_plan_grants.c.expires_at > datetime.now(timezone.utc)),
        )).scalars())
        offerings = db.execute(select(platform_model_offerings).where(
            platform_model_offerings.c.enabled.is_(True),
        ).order_by(platform_model_offerings.c.id)).mappings().all()
    return [dict(item) for item in offerings
            if (item["audience"] == "all" or plans.intersection(item["plans_json"]))
            and get_connection(item["provider"]) is not None]


def catalog_for_user(user_id: str) -> list[dict]:
    return [{"provider": f"platform:{item['id']}", "model": item["model"],
             "label": item["label"]} for item in available_offerings(user_id)]


def resolve_offering(user_id: str, provider: str, model: str):
    # Re-check authoritative entitlement at execution, not just at UI selection.
    item = next((item for item in available_offerings(user_id)
                 if provider == f"platform:{item['id']}" and model == item["model"]), None)
    if item is None:
        raise ValueError("平台模型未开放或当前账户无使用权限。")
    connection = get_connection(item["provider"])
    if connection is None:
        raise ValueError("平台模型连接已不可用。")
    return connection.base_url, decrypt_api_key(connection), item["protocol"]
