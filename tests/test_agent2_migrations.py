from __future__ import annotations

from pathlib import Path

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect


def config(path: Path) -> AlembicConfig:
    value = AlembicConfig("apps/api/alembic.ini")
    value.set_main_option("script_location", "apps/api/alembic")
    value.set_main_option("sqlalchemy.url", f"sqlite:///{path.as_posix()}")
    return value


def test_agent2_migrations_upgrade_from_previous_head_and_preserve_order(tmp_path: Path):
    path = tmp_path / "agent2.sqlite3"
    alembic = config(path)
    alembic_command.upgrade(alembic, "0014_research_session_run_bindings")
    alembic_command.upgrade(alembic, "head")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    inspector = inspect(engine)
    expected = {
        "scientific_objects", "scientific_object_versions", "scientific_object_relationships",
        "research_turns", "research_context_snapshots", "research_turn_events", "scientific_result_snapshots",
    }
    assert expected.issubset(set(inspector.get_table_names()))
    assert {item["name"] for item in inspector.get_unique_constraints("scientific_object_versions")} >= {"uq_scientific_object_versions_object_version"}
    assert {item["name"] for item in inspector.get_unique_constraints("research_turns")} >= {"uq_research_turns_session_sequence", "uq_research_turns_user_message_id"}
    assert {item["name"] for item in inspector.get_indexes("scientific_result_snapshots")} >= {
        "idx_scientific_result_snapshots_turn", "idx_scientific_result_snapshots_job", "idx_scientific_result_snapshots_project_created",
    }
    fk_tables = {item["referred_table"] for item in inspector.get_foreign_keys("research_turns")}
    assert {"projects", "sessions", "messages", "analysis_intents", "analysis_plans", "jobs"}.issubset(fk_tables)
    engine.dispose()

    alembic_command.downgrade(alembic, "0014_research_session_run_bindings")
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    assert not expected.intersection(inspect(engine).get_table_names())
    engine.dispose()
    alembic_command.upgrade(alembic, "head")
