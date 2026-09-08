from __future__ import annotations

class ScientificReportError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code

__all__ = ["ScientificReportError"]
