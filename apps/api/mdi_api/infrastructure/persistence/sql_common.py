"""Shared SQL persistence infrastructure helpers."""

from __future__ import annotations

from sqlalchemy import insert, select
from sqlalchemy.engine import Connection

from mdi_api.db import users


def ensure_user(connection: Connection, *, user_id: str) -> None:
    exists = connection.execute(select(users.c.id).where(users.c.id == user_id)).first()
    if exists is None:
        connection.execute(insert(users).values(id=user_id, email=f"{user_id}@local.invalid", display_name=user_id))


__all__ = ["ensure_user"]
