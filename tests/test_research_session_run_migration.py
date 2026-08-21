from __future__ import annotations

from pathlib import Path

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect, text


def _config(path: Path) -> AlembicConfig:
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{path.as_posix()}")
    return config


def test_research_session_run_migration_backfills_existing_projection_messages(tmp_path: Path) -> None:
    path = tmp_path / "research-run-binding.sqlite3"
    config = _config(path)
    alembic_command.upgrade(config, "0013_drop_decision_execution_unique")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    with engine.begin() as connection:
        connection.execute(text("INSERT INTO users (id, email, display_name) VALUES ('user', 'user@example.invalid', 'User')"))
        connection.execute(text("INSERT INTO organizations (id, name) VALUES ('org', 'Org')"))
        connection.execute(text("INSERT INTO projects (id, organization_id, name, created_by) VALUES ('project', 'org', 'Project', 'user')"))
        connection.execute(text("INSERT INTO sessions (id, project_id, mode, status, created_by) VALUES ('research', 'project', 'project', 'active', 'user')"))
        connection.execute(text("INSERT INTO jobs (id, project_id, kind, status, created_by) VALUES ('job', 'project', 'analysis', 'completed', 'user')"))
        connection.execute(text("INSERT INTO messages (id, session_id, role, content_summary, payload_json) VALUES ('message', 'research', 'agent', '完成', :payload)"), {
            "payload": '{"source":"research_assistant_projection","phase":"post_run","runId":"job"}',
        })
    engine.dispose()

    alembic_command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    inspector = inspect(engine)
    assert "research_session_runs" in inspector.get_table_names()
    assert {item["name"] for item in inspector.get_unique_constraints("research_session_runs")} == {
        "uq_research_session_runs_job_id",
    }
    with engine.connect() as connection:
        assert connection.execute(text("SELECT session_id, job_id FROM research_session_runs")).one() == ("research", "job")
        assert connection.execute(text("SELECT COUNT(*) FROM messages")).scalar_one() == 1
    engine.dispose()


def test_research_session_run_migration_upgrade_downgrade_reupgrade(tmp_path: Path) -> None:
    path = tmp_path / "research-run-binding-cycle.sqlite3"
    config = _config(path)
    alembic_command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    assert "research_session_runs" in inspect(engine).get_table_names()
    engine.dispose()

    alembic_command.downgrade(config, "0013_drop_decision_execution_unique")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    assert "research_session_runs" not in inspect(engine).get_table_names()
    engine.dispose()

    alembic_command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    assert "research_session_runs" in inspect(engine).get_table_names()
    engine.dispose()
