from __future__ import annotations

from pathlib import Path

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text

from mdi_api.config import ApiSettings
from mdi_api.database import create_repository_factory
from mdi_api.main import create_app
from mdi_api.phase2_runtime import reset_phase2_runtime


CURRENT_HEAD = "0008_phase_d_r1_namespace"
REQUIRED_DURABLE_NAMESPACE_TABLES = {
    "users",
    "organizations",
    "projects",
    "scientific_workspaces",
    "workspace_panels",
    "workspace_layout_revisions",
}


def _config(path: Path) -> AlembicConfig:
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{path.as_posix()}")
    return config


def _settings(path: Path) -> ApiSettings:
    return ApiSettings(
        database_url=f"sqlite:///{path.as_posix()}",
        runtime_backend="postgresql",
    )


def _assert_durable_namespace_schema(path: Path) -> None:
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    inspector = inspect(engine)
    assert REQUIRED_DURABLE_NAMESPACE_TABLES.issubset(inspector.get_table_names())
    project_foreign_keys = {
        (
            foreign_key["name"],
            tuple(foreign_key["constrained_columns"]),
            foreign_key["referred_table"],
            tuple(foreign_key["referred_columns"]),
        )
        for foreign_key in inspector.get_foreign_keys("projects")
    }
    assert project_foreign_keys == {
        (
            "fk_projects_created_by_users",
            ("created_by",),
            "users",
            ("id",),
        ),
        (
            "fk_projects_organization_id_organizations",
            ("organization_id",),
            "organizations",
            ("id",),
        ),
    }
    assert "idx_projects_org_created" in {
        index["name"] for index in inspector.get_indexes("projects")
    }
    with engine.connect() as connection:
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == CURRENT_HEAD
    engine.dispose()


def test_fresh_alembic_database_contains_complete_durable_namespace_schema(tmp_path: Path) -> None:
    path = tmp_path / "fresh-durable-namespace.sqlite3"
    alembic_command.upgrade(_config(path), "head")
    _assert_durable_namespace_schema(path)


def test_upgrade_from_0007_backfills_project_identities_without_data_loss(tmp_path: Path) -> None:
    path = tmp_path / "upgrade-durable-namespace.sqlite3"
    config = _config(path)
    alembic_command.upgrade(config, "0007_phase10m1_workspace_domain")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO projects "
                "(id, organization_id, name, description, created_by) "
                "VALUES (:id, :organization_id, :name, '', :created_by)"
            ),
            {
                "id": "project_before_d_r1",
                "organization_id": "org_before_d_r1",
                "name": "Project before D-R1",
                "created_by": "user_before_d_r1",
            },
        )
    engine.dispose()

    alembic_command.upgrade(config, "head")
    _assert_durable_namespace_schema(path)
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    with engine.connect() as connection:
        assert connection.execute(
            text("SELECT name FROM projects WHERE id = 'project_before_d_r1'")
        ).scalar_one() == "Project before D-R1"
        assert connection.execute(
            text("SELECT email FROM users WHERE id = 'user_before_d_r1'")
        ).scalar_one() == "user_before_d_r1@local.invalid"
        assert connection.execute(
            text("SELECT name FROM organizations WHERE id = 'org_before_d_r1'")
        ).scalar_one() == "org_before_d_r1"
    engine.dispose()

    alembic_command.upgrade(config, "head")
    _assert_durable_namespace_schema(path)


def test_project_repository_persists_across_repository_session_recreation(tmp_path: Path) -> None:
    path = tmp_path / "repository-durable-namespace.sqlite3"
    alembic_command.upgrade(_config(path), "head")
    factory = create_repository_factory(_settings(path))
    with factory.session() as session:
        saved = session.repositories.projects.save(
            {
                "projectId": "project_repository_d_r1",
                "name": "Repository D-R1",
                "createdBy": "user_local",
                "organizationId": "org_local",
            }
        )
    assert saved["projectId"] == "project_repository_d_r1"

    recreated_factory = create_repository_factory(_settings(path))
    loaded = recreated_factory.create_repositories().projects.get("project_repository_d_r1")
    assert loaded["name"] == "Repository D-R1"
    assert loaded["createdBy"] == "user_local"


def test_post_projects_is_durable_and_empty_workspace_history_resolves(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "api-durable-namespace.sqlite3"
    alembic_command.upgrade(_config(path), "head")
    settings = _settings(path)
    monkeypatch.setenv("DATABASE_URL", settings.database_url)
    monkeypatch.setenv("MDI_RUNTIME_BACKEND", "postgresql")
    reset_phase2_runtime(tmp_path / "phase2-before-restart")

    with TestClient(create_app()) as client:
        created_response = client.post("/projects", json={"name": "Durable namespace"})
        assert created_response.status_code == 200
        project_id = created_response.json()["id"]

    fresh_factory = create_repository_factory(settings)
    assert fresh_factory.create_repositories().projects.get(project_id)["name"] == "Durable namespace"

    reset_phase2_runtime(tmp_path / "phase2-after-restart")
    monkeypatch.setattr(
        "mdi_api.routers.workspaces._repositories",
        lambda: create_repository_factory(settings).create_repositories(),
    )
    with TestClient(create_app()) as restarted_client:
        assert project_id in {
            project["id"] for project in restarted_client.get("/projects").json()
        }
        history_response = restarted_client.get(f"/projects/{project_id}/workspaces")
        assert history_response.status_code == 200
        assert history_response.json()["items"] == []
