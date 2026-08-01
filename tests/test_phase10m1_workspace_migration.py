from __future__ import annotations

from pathlib import Path

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect, text


WORKSPACE_TABLES = {
    "scientific_workspaces",
    "workspace_panels",
    "workspace_layout_revisions",
}


def _config(path: Path) -> AlembicConfig:
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{path.as_posix()}")
    return config


def test_percent_encoded_database_url_round_trips_through_alembic_config() -> None:
    database_url = (
        "postgresql+psycopg://user:pass@localhost/db"
        "?options=-csearch_path%3Dphase10m1_test%2Cpublic"
    )
    config = AlembicConfig()
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    assert config.get_main_option("sqlalchemy.url") == database_url


def _create_exact_parent_fixture(path: Path) -> None:
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON"))
        connection.execute(text("CREATE TABLE projects (id VARCHAR(64) PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE datasets (id VARCHAR(64) PRIMARY KEY, project_id VARCHAR(64))"))
        connection.execute(text("CREATE TABLE data_profiles (id VARCHAR(64) PRIMARY KEY, dataset_id VARCHAR(64))"))
        connection.execute(text("CREATE TABLE analysis_plans (id VARCHAR(96) PRIMARY KEY, project_id VARCHAR(64))"))
        connection.execute(text("CREATE TABLE analysis_intents (id VARCHAR(96) PRIMARY KEY, project_id VARCHAR(64))"))
        connection.execute(
            text(
                "CREATE TABLE jobs ("
                "id VARCHAR(64) PRIMARY KEY, project_id VARCHAR(64), dataset_id VARCHAR(64), plan_id VARCHAR(96))"
            )
        )
    engine.dispose()


def test_phase10m1_migration_upgrade_downgrade_reupgrade(tmp_path: Path) -> None:
    path = tmp_path / "workspace-migration.sqlite3"
    _create_exact_parent_fixture(path)
    config = _config(path)
    alembic_command.stamp(config, "0006_phase10l4_interpretation")

    alembic_command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    inspector = inspect(engine)
    assert WORKSPACE_TABLES.issubset(set(inspector.get_table_names()))
    assert {column["name"] for column in inspector.get_columns("scientific_workspaces")} == {
        "workspace_id",
        "schema_version",
        "project_id",
        "source_job_id",
        "source_reference_hash",
        "dataset_id",
        "dataset_version",
        "profile_id",
        "profile_semantic_hash",
        "intent_id",
        "intent_semantic_hash",
        "plan_id",
        "plan_hash",
        "plan_schema_version",
        "title",
        "active_panel_id",
        "pinned_selection_json",
        "revision",
        "created_by",
        "created_at",
        "updated_at",
    }
    assert {index["name"] for index in inspector.get_indexes("scientific_workspaces")} == {
        "idx_workspaces_project_updated",
        "idx_workspaces_source_job",
    }
    workspace_fks = {
        (foreign_key["constrained_columns"][0], foreign_key["referred_table"], foreign_key["options"].get("ondelete"))
        for foreign_key in inspector.get_foreign_keys("scientific_workspaces")
    }
    assert workspace_fks == {
        ("project_id", "projects", "RESTRICT"),
        ("source_job_id", "jobs", "RESTRICT"),
        ("dataset_id", "datasets", "RESTRICT"),
        ("profile_id", "data_profiles", "RESTRICT"),
        ("intent_id", "analysis_intents", "RESTRICT"),
        ("plan_id", "analysis_plans", "RESTRICT"),
    }
    for table in ("workspace_panels", "workspace_layout_revisions"):
        foreign_keys = inspector.get_foreign_keys(table)
        assert len(foreign_keys) == 1
        assert foreign_keys[0]["referred_table"] == "scientific_workspaces"
        assert foreign_keys[0]["options"].get("ondelete") == "CASCADE"
    unique_names = {
        constraint["name"]
        for constraint in inspector.get_unique_constraints("scientific_workspaces")
    }
    assert "uq_scientific_workspaces_project_job" in unique_names
    engine.dispose()

    alembic_command.downgrade(config, "0006_phase10l4_interpretation")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    assert WORKSPACE_TABLES.isdisjoint(set(inspect(engine).get_table_names()))
    engine.dispose()

    alembic_command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    assert WORKSPACE_TABLES.issubset(set(inspect(engine).get_table_names()))
    engine.dispose()


def test_phase10m1_fresh_sqlite_database_upgrades_to_head(tmp_path: Path) -> None:
    path = tmp_path / "workspace-fresh-head.sqlite3"
    config = _config(path)
    alembic_command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    tables = set(inspect(engine).get_table_names())
    assert WORKSPACE_TABLES.issubset(tables)
    assert {
        "projects",
        "datasets",
        "data_profiles",
        "analysis_intents",
        "analysis_plans",
        "jobs",
        "artifacts",
    }.issubset(tables)
    engine.dispose()
