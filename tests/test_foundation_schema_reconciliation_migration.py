from __future__ import annotations

from pathlib import Path

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
import pytest
from sqlalchemy import create_engine, inspect, text

from mdi_api.db import metadata


FOUNDATION_TABLES = {
    "project_members",
    "files",
    "field_mappings",
    "user_configs",
    "secrets",
    "audit_logs",
}

EXPECTED_INDEXES = {
    "project_members": {
        "idx_project_members_user",
        "idx_project_members_search_user_project",
    },
    "files": {"idx_files_dataset_created"},
    "audit_logs": {"idx_audit_logs_project_created"},
    "projects": {"idx_projects_search_owner_updated"},
    "datasets": {"idx_datasets_search_project_updated"},
    "sessions": {"idx_sessions_search_project_created"},
    "reports": {"idx_reports_search_project_created"},
    "scientific_objects": {"idx_scientific_objects_search_project_created"},
    "scientific_result_snapshots": {
        "idx_scientific_results_search_project_created"
    },
}


def _config(path: Path) -> AlembicConfig:
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{path.as_posix()}")
    return config


def _upgrade_to_0027(path: Path) -> AlembicConfig:
    config = _config(path)
    alembic_command.upgrade(config, "0027_research_session_management")
    return config


def _create_legacy_foundation_tables(path: Path) -> None:
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    for table_name in (
        "project_members",
        "files",
        "field_mappings",
        "user_configs",
        "secrets",
        "audit_logs",
    ):
        metadata.tables[table_name].create(engine)
    engine.dispose()


def _seed_foundation_rows(path: Path) -> None:
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users "
                "(id, email, display_name) "
                "VALUES ('user_0028', 'user_0028@local.invalid', '0028 User')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO organizations (id, name) "
                "VALUES ('org_0028', '0028 Organization')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO projects "
                "(id, organization_id, name, created_by) "
                "VALUES ('project_0028', 'org_0028', '0028 Project', 'user_0028')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO datasets "
                "(id, project_id, name, created_by) "
                "VALUES ('dataset_0028', 'project_0028', '0028 Dataset', 'user_0028')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO project_members (project_id, user_id, role) "
                "VALUES ('project_0028', 'user_0028', 'owner')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO files "
                "(id, dataset_id, file_name, media_type, storage_key, sha256, size_bytes) "
                "VALUES "
                "('file_0028', 'dataset_0028', 'source.cif', 'chemical/x-cif', "
                "'source/file_0028', :sha256, 128)"
            ),
            {"sha256": "a" * 64},
        )
        connection.execute(
            text(
                "INSERT INTO field_mappings "
                "(id, dataset_id, mapping_json, created_by) "
                "VALUES ('mapping_0028', 'dataset_0028', '{}', 'user_0028')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO user_configs (id, user_id, config_json) "
                "VALUES ('config_0028', 'user_0028', '{}')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO secrets "
                "(id, owner_type, owner_id, provider, secret_ref, encrypted_blob_key) "
                "VALUES "
                "('secret_0028', 'user', 'user_0028', 'test', 'opaque', 'encrypted/key')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO audit_logs "
                "(id, actor_user_id, project_id, action, target_type, target_id) "
                "VALUES "
                "('audit_0028', 'user_0028', 'project_0028', "
                "'foundation.reconcile', 'schema', '0028')"
            )
        )
    engine.dispose()


def test_fresh_upgrade_creates_complete_foundation_schema(tmp_path: Path) -> None:
    path = tmp_path / "fresh-foundation.sqlite3"
    config = _config(path)

    alembic_command.upgrade(config, "head")

    engine = create_engine(f"sqlite:///{path.as_posix()}")
    inspector = inspect(engine)
    assert FOUNDATION_TABLES.issubset(set(inspector.get_table_names()))
    for table_name, expected in EXPECTED_INDEXES.items():
        assert expected.issubset(
            {item["name"] for item in inspector.get_indexes(table_name)}
        )
    assert {
        (tuple(item["constrained_columns"]), item["referred_table"])
        for item in inspector.get_foreign_keys("project_members")
    } == {
        (("project_id",), "projects"),
        (("user_id",), "users"),
    }
    assert {
        (tuple(item["constrained_columns"]), item["referred_table"])
        for item in inspector.get_foreign_keys("audit_logs")
    } == {
        (("actor_user_id",), "users"),
        (("project_id",), "projects"),
    }
    with engine.connect() as connection:
        assert connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one() == "0032_provider_connections"
    engine.dispose()


def test_compatible_legacy_tables_are_preserved_and_missing_index_is_repaired(
    tmp_path: Path,
) -> None:
    path = tmp_path / "legacy-foundation.sqlite3"
    config = _upgrade_to_0027(path)
    _create_legacy_foundation_tables(path)
    _seed_foundation_rows(path)

    engine = create_engine(f"sqlite:///{path.as_posix()}")
    with engine.begin() as connection:
        connection.execute(text("DROP INDEX idx_files_dataset_created"))
    engine.dispose()

    alembic_command.upgrade(config, "head")

    engine = create_engine(f"sqlite:///{path.as_posix()}")
    inspector = inspect(engine)
    assert "idx_files_dataset_created" in {
        item["name"] for item in inspector.get_indexes("files")
    }
    with engine.connect() as connection:
        for table_name in FOUNDATION_TABLES:
            assert connection.execute(
                text(f"SELECT count(*) FROM {table_name}")
            ).scalar_one() == 1
    engine.dispose()

    # Reconciliation is deliberately downgrade-safe: it does not destroy
    # foundation data that may have existed before Alembic revision 0028.
    alembic_command.downgrade(config, "0027_research_session_management")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    assert FOUNDATION_TABLES.issubset(set(inspect(engine).get_table_names()))
    engine.dispose()


def test_incompatible_existing_table_fails_before_partial_reconciliation(
    tmp_path: Path,
) -> None:
    path = tmp_path / "incompatible-foundation.sqlite3"
    config = _upgrade_to_0027(path)
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE secrets ("
                "id varchar(64) NOT NULL PRIMARY KEY, "
                "owner_type varchar(32) NOT NULL, "
                "owner_id integer NOT NULL, "
                "provider varchar(80) NOT NULL, "
                "secret_ref varchar(160) NOT NULL, "
                "encrypted_blob_key text NOT NULL, "
                "created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP"
                ")"
            )
        )
    engine.dispose()

    with pytest.raises(
        RuntimeError,
        match="refused incompatible existing table 'secrets'.*owner_id",
    ):
        alembic_command.upgrade(config, "head")

    engine = create_engine(f"sqlite:///{path.as_posix()}")
    inspector = inspect(engine)
    assert FOUNDATION_TABLES.intersection(inspector.get_table_names()) == {"secrets"}
    with engine.connect() as connection:
        assert connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one() == "0027_research_session_management"
    engine.dispose()
