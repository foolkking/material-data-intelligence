from __future__ import annotations

from typing import Any

from sqlalchemy import Engine, create_engine, event

from mdi_api.config import ApiSettings, load_settings
from mdi_api.unit_of_work import RepositoryFactory


def _engine_kwargs(settings: ApiSettings, **overrides: Any) -> dict[str, Any]:
    """Return sensible defaults for both SQLite and PostgreSQL engines."""
    is_postgres = "postgres" in settings.database_url
    kwargs: dict[str, Any] = {"future": True, "pool_pre_ping": True}

    if is_postgres:
        kwargs.setdefault("pool_size", 5)
        kwargs.setdefault("max_overflow", 10)
        kwargs.setdefault("pool_recycle", 1800)
        kwargs.setdefault("connect_args", {})
    else:
        kwargs.setdefault("connect_args", {"check_same_thread": False})

    kwargs.update(overrides)
    return kwargs


def create_engine_from_settings(settings: ApiSettings | None = None, **kwargs: Any) -> Engine:
    active = settings or load_settings()
    engine_kwargs = _engine_kwargs(active, **kwargs)
    engine = create_engine(active.database_url, **engine_kwargs)
    _configure_sqlite_pragma(engine, active.database_url)
    return engine


def create_repository_factory(settings: ApiSettings | None = None, **kwargs: Any) -> RepositoryFactory:
    return RepositoryFactory(create_engine_from_settings(settings, **kwargs))


def _configure_sqlite_pragma(engine: Engine, database_url: str) -> None:
    """Enable WAL mode and foreign keys for SQLite connections."""
    if "postgres" in database_url:
        return

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
