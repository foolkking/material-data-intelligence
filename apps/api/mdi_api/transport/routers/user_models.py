from typing import Literal
from fastapi import Body, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from mdi_api.transport.routers.auth import CurrentUser, get_current_user
from mdi_api import user_models


class ConnectionScopeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    connectionId: str = Field(default="personal", pattern=r"^(personal|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$")


class PersonalConnectionRequest(ConnectionScopeRequest):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    label: str = Field(default="我的模型服务", max_length=120)
    protocol: Literal["openai_chat_json", "openai_chat", "openai_responses", "anthropic"] = "openai_chat_json"
    baseUrl: str = Field(min_length=8, max_length=512)
    apiKey: str | None = Field(default=None, max_length=4096, repr=False)
    revision: int = Field(ge=0)


class ModelSelection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=128)


class ModelSelectionRequest(ConnectionScopeRequest):
    model_config = ConfigDict(extra="forbid")
    selected: list[ModelSelection] = Field(max_length=256)
    revision: int = Field(ge=0)


def get_user_models(current_user: CurrentUser = Depends(get_current_user)):
    return user_models.public_settings(user_models.read_settings(current_user.id))


def save_user_connection(request: PersonalConnectionRequest, current_user: CurrentUser = Depends(get_current_user)):
    try:
        return user_models.save_personal_connection(current_user.id, label=request.label, base_url=request.baseUrl, api_key=request.apiKey, protocol=request.protocol, revision=request.revision, connection_id=request.connectionId)
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc


def discover_user_models(request: ConnectionScopeRequest = Body(default=ConnectionScopeRequest()), current_user: CurrentUser = Depends(get_current_user)):
    try:
        return user_models.discover_user_models(current_user.id, request.connectionId)
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc


def save_user_model_selection(request: ModelSelectionRequest, current_user: CurrentUser = Depends(get_current_user)):
    try:
        return user_models.select_user_models(current_user.id, [item.model_dump() for item in request.selected], request.revision, request.connectionId)
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc
