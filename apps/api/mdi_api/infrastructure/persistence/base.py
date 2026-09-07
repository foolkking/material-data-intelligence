"""Domain-neutral persistence primitives.

These helpers intentionally contain no capability policy.  They preserve the
legacy repository mechanics while allowing individual repository verticals to
adopt canonical ownership incrementally.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
from threading import RLock
from typing import Any, ContextManager, Iterator, Mapping

from sqlalchemy.engine import Connection, Engine


def _json_copy(value: Any) -> Any:
    if value is None:
        return None
    return json.loads(json.dumps(value, default=str))


def _required_id(record: Mapping[str, Any], alias: str = "id") -> str:
    value = record.get("id") or record.get(alias)
    if not value:
        raise ValueError(f"Record is missing id/{alias}")
    return str(value)


def _model_to_record(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return _json_copy(value)


def _row_to_json_dict(row: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items()}


def _enum_value(value: Any) -> str:
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _iso(value: Any) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class _InMemoryRecordRepository:
    """Shared record storage mechanics for in-memory repositories."""

    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}
        self._record_lock = RLock()

    def _save(self, record: Mapping[str, Any], *, record_id: str) -> dict[str, Any]:
        stored = _json_copy(record)
        stored.setdefault("id", record_id)
        self.records[record_id] = stored
        return _json_copy(stored)

    def _get(self, record_id: str) -> dict[str, Any]:
        try:
            return _json_copy(self.records[record_id])
        except KeyError as exc:
            raise LookupError(f"Unknown record id: {record_id}") from exc

    def create(self, record: Mapping[str, Any]) -> dict[str, Any]:
        return self.save(record)  # type: ignore[attr-defined]

    def get_by_id(self, record_id: str) -> dict[str, Any]:
        return self.get(record_id)  # type: ignore[attr-defined]


class _SqlAlchemyRepository:
    """Shared SQLAlchemy connection and row-fetching mechanics."""

    def __init__(self, bind: Engine | Connection) -> None:
        self.bind = bind

    def _with_connection(self, fn: Any) -> Any:
        if isinstance(self.bind, Engine):
            with self.bind.begin() as connection:
                return fn(connection)
        return fn(self.bind)

    def _fetch_one_dict(self, statement: Any) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(statement).mappings().first()
            if row is None:
                raise LookupError("Record not found")
            return _row_to_json_dict(row)

        return self._with_connection(run)

    def _fetch_all_dicts(self, statement: Any) -> list[dict[str, Any]]:
        def run(connection: Connection) -> list[dict[str, Any]]:
            return [_row_to_json_dict(row) for row in connection.execute(statement).mappings().all()]

        return self._with_connection(run)

    def create(self, record: Mapping[str, Any]) -> dict[str, Any]:
        return self.save(record)  # type: ignore[attr-defined]

    def get_by_id(self, record_id: str) -> dict[str, Any]:
        return self.get(record_id)  # type: ignore[attr-defined]


__all__ = [
    "_InMemoryRecordRepository",
    "_SqlAlchemyRepository",
    "_enum_value",
    "_iso",
    "_json_copy",
    "_model_to_record",
    "_parse_iso",
    "_required_id",
    "_row_to_json_dict",
    "_utc_now",
]

