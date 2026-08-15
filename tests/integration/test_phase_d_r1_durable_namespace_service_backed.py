from __future__ import annotations

import os
import uuid

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.schema import CreateSchema, DropSchema

from mdi_api.database import create_repository_factory
from mdi_api.main import create_app
from mdi_api.phase2_runtime import reset_phase2_runtime


def _required_postgres_url() -> str:
    database_url = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url or not make_url(database_url).get_backend_name().startswith("postgresql"):
        raise RuntimeError("A PostgreSQL MDI_TEST_DATABASE_URL or DATABASE_URL is required")
    return database_url


def _schema_database_url(database_url: str, schema_name: str) -> str:
    url = make_url(database_url)
    query = dict(url.query)
    query["options"] = f"-csearch_path={schema_name}"
    return url.set(query=query).render_as_string(hide_password=False)


@pytest.mark.integration
def test_phase_d_r1_project_namespace_survives_runtime_recreation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL running")

    database_url = _required_postgres_url()
    schema_name = f"phase_d_r1_{uuid.uuid4().hex[:12]}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    schema_created = False
    try:
        with base_engine.begin() as connection:
            connection.execute(CreateSchema(schema_name))
        schema_created = True
        monkeypatch.setenv("DATABASE_URL", schema_url)
        monkeypatch.delenv("MDI_DATABASE_URL", raising=False)
        monkeypatch.setenv("MDI_RUNTIME_BACKEND", "postgresql")
        config = AlembicConfig("apps/api/alembic.ini")
        config.set_main_option("script_location", "apps/api/alembic")
        alembic_upgrade(config, "head")

        engine = create_engine(schema_url, future=True)
        with engine.connect() as connection:
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == (
                "0008_phase_d_r1_namespace"
            )

        reset_phase2_runtime(tmp_path / "before-restart")
        with TestClient(create_app()) as client:
            created = client.post("/projects", json={"name": "Phase D-R1 durable namespace"})
            assert created.status_code == 200
            project_id = created.json()["id"]
            history = client.get(f"/projects/{project_id}/workspaces")
            assert history.status_code == 200
            assert history.json()["items"] == []

        recreated_factory = create_repository_factory()
        assert recreated_factory.create_repositories().projects.get(project_id)["name"] == (
            "Phase D-R1 durable namespace"
        )

        reset_phase2_runtime(tmp_path / "after-restart")
        with TestClient(create_app()) as restarted_client:
            assert project_id in {
                project["id"] for project in restarted_client.get("/projects").json()
            }
            history = restarted_client.get(f"/projects/{project_id}/workspaces")
            assert history.status_code == 200
            assert history.json()["items"] == []
    finally:
        if engine is not None:
            engine.dispose()
        try:
            if schema_created:
                with base_engine.begin() as connection:
                    connection.execute(DropSchema(schema_name, cascade=True))
        finally:
            base_engine.dispose()
