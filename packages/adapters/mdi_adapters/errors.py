from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolExecutionError(Exception):
    code: str
    message: str
    tool_id: str
    retryable: bool = False
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "toolId": self.tool_id,
            "retryable": self.retryable,
            "details": self.details,
        }


def normalize_exception(exc: Exception, *, tool_id: str, code: str = "TOOL_RUNTIME_ERROR") -> ToolExecutionError:
    if isinstance(exc, ToolExecutionError):
        return exc
    return ToolExecutionError(code=code, message=str(exc), tool_id=tool_id, retryable=False)

