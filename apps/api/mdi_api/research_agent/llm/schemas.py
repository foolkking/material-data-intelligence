from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StructuredLLMResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: str
    model: str
    parsed: dict[str, Any]
    provider_request_id: str | None = None
    latency_ms: int = Field(ge=0)
    usage: dict[str, Any] | None = None
    repair_attempted: bool = False
    prompt_version: str
