from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from alembic.config import Config as AlembicConfig
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine

from mdi_api.config import ApiSettings
from mdi_api.database import create_engine_from_settings


class DatabaseMigrationHeadError(RuntimeError):
    """Raised before admission when code and database revisions disagree."""


@dataclass(frozen=True)
class DatabaseMigrationHeadStatus:
    expected_heads: tuple[str, ...]
    current_heads: tuple[str, ...]


def migration_head_guard_required(settings: ApiSettings) -> bool:
    """Protect declared qualification/staging-style same-stack runtimes."""

    return settings.runtime_profile == "same-stack"


def repository_migration_heads() -> tuple[str, ...]:
    repo_root = Path(__file__).resolve().parents[3]
    config = AlembicConfig(str(repo_root / "apps" / "api" / "alembic.ini"))
    config.set_main_option(
        "script_location",
        str(repo_root / "apps" / "api" / "alembic"),
    )
    return tuple(sorted(ScriptDirectory.from_config(config).get_heads()))


def validate_database_migration_head(
    settings: ApiSettings,
    *,
    engine: Engine | None = None,
) -> DatabaseMigrationHeadStatus | None:
    """Fail before API/worker admission when the database is not at code head."""

    if not migration_head_guard_required(settings):
        return None

    expected_heads = repository_migration_heads()
    active_engine = engine or create_engine_from_settings(settings)
    with active_engine.connect() as connection:
        current_heads = tuple(
            sorted(MigrationContext.configure(connection).get_current_heads())
        )
    status = DatabaseMigrationHeadStatus(
        expected_heads=expected_heads,
        current_heads=current_heads,
    )
    if status.current_heads != status.expected_heads:
        current = ",".join(status.current_heads) or "<unversioned>"
        expected = ",".join(status.expected_heads) or "<missing-code-head>"
        raise DatabaseMigrationHeadError(
            "DATABASE_MIGRATION_HEAD_MISMATCH"
            f"(current={current}, expected={expected})"
        )
    return status
