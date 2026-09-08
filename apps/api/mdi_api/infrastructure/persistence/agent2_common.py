from __future__ import annotations

from typing import Any

from sqlalchemy import Connection, Engine


class _Repository:
    def __init__(self, bind: Engine | Connection) -> None:
        self.bind = bind

    def _run(self, fn: Any) -> Any:
        if isinstance(self.bind, Engine):
            with self.bind.begin() as connection:
                return fn(connection)
        return fn(self.bind)


def _optional_dict(row: Any) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


__all__ = ["_Repository", "_optional_dict"]
