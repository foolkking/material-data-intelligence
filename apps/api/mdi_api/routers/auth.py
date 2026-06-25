from __future__ import annotations

from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: str
    email: str
    displayName: str
    roles: list[str]


def get_current_user_stub() -> CurrentUser:
    return CurrentUser(
        id="user_local",
        email="local@example.invalid",
        displayName="Local Researcher",
        roles=["owner"],
    )
