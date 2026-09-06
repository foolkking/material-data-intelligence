from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine

from mdi_api.config import ApiSettings
from mdi_api.migration_head import (
    DatabaseMigrationHeadError,
    repository_migration_heads,
    validate_database_migration_head,
)
from mdi_workers import worker_entrypoint


def _config(database: Path) -> AlembicConfig:
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")
    return config


def test_local_runtime_does_not_require_a_migration_database() -> None:
    settings = ApiSettings(runtime_profile="local", database_url="invalid://unused")

    assert validate_database_migration_head(settings) is None


def test_same_stack_runtime_accepts_exact_repository_head(tmp_path: Path) -> None:
    database = tmp_path / "current.sqlite3"
    alembic_command.upgrade(_config(database), "head")
    engine = create_engine(f"sqlite:///{database.as_posix()}")

    status = validate_database_migration_head(
        ApiSettings(runtime_profile="same-stack"),
        engine=engine,
    )

    assert status is not None
    assert status.current_heads == repository_migration_heads()
    engine.dispose()


def test_same_stack_runtime_rejects_stale_database_before_admission(
    tmp_path: Path,
) -> None:
    database = tmp_path / "stale.sqlite3"
    alembic_command.upgrade(_config(database), "0030_account_invitations")
    engine = create_engine(f"sqlite:///{database.as_posix()}")

    with pytest.raises(
        DatabaseMigrationHeadError,
        match=(
            "DATABASE_MIGRATION_HEAD_MISMATCH"
            r"\(current=0030_account_invitations, "
            r"expected=0032_provider_connections\)"
        ),
    ):
        validate_database_migration_head(
            ApiSettings(runtime_profile="same-stack"),
            engine=engine,
        )
    engine.dispose()


def test_same_stack_worker_checks_migration_before_redis_worker_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MDI_RUNTIME_PROFILE", "same-stack")
    checked = False

    def mark_checked(_settings: ApiSettings) -> None:
        nonlocal checked
        checked = True
        raise DatabaseMigrationHeadError("DATABASE_MIGRATION_HEAD_MISMATCH")

    monkeypatch.setattr(
        "mdi_api.config.load_settings",
        lambda: ApiSettings(runtime_profile="same-stack"),
    )
    monkeypatch.setattr(
        "mdi_api.config.validate_runtime_settings",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "mdi_api.migration_head.validate_database_migration_head",
        mark_checked,
    )
    monkeypatch.setattr(
        worker_entrypoint,
        "create_worker",
        lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("worker creation must not be reached")
        ),
    )

    with pytest.raises(
        DatabaseMigrationHeadError,
        match="DATABASE_MIGRATION_HEAD_MISMATCH",
    ):
        worker_entrypoint.main(["mdi-jobs", "--burst"])

    assert checked is True
