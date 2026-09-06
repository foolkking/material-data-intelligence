from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
from types import SimpleNamespace

from sqlalchemy import create_engine, insert
from sqlalchemy.pool import StaticPool
from starlette.requests import Request

from mdi_api.db import auth_sessions, metadata, users
import mdi_api.routers.auth as auth


def test_authenticated_identity_projects_persisted_platform_role(
    monkeypatch,
) -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    raw_token = "platform-admin-token"
    with engine.begin() as connection:
        connection.execute(
            insert(users),
            {
                "id": "platform-admin",
                "email": "admin@example.invalid",
                "display_name": "Platform Admin",
                "platform_role": "PLATFORM_ADMIN",
                "is_active": True,
            },
        )
        connection.execute(
            insert(auth_sessions),
            {
                "id": "session-platform-admin",
                "user_id": "platform-admin",
                "token_hash": hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
                "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            },
        )
    monkeypatch.setattr(auth, "create_engine_from_settings", lambda _settings: engine)
    monkeypatch.setattr(
        auth,
        "load_settings",
        lambda: SimpleNamespace(
            auth_cookie_name="mdi_session",
            auth_required=True,
        ),
    )
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/auth/me",
            "headers": [(b"cookie", f"mdi_session={raw_token}".encode("ascii"))],
        }
    )

    current_user = auth.get_current_user(request)

    assert current_user.platformRole == "PLATFORM_ADMIN"
    assert current_user.id == "platform-admin"
    assert current_user.roles == ["owner"]
