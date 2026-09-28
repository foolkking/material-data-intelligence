from __future__ import annotations

import ast
import re
from pathlib import Path

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text


EXPECTED_HEAD = "0035_job_execution_leases"
VERSIONS = Path("apps/api/alembic/versions")
_DANGEROUS_SQL = re.compile(
    r"\b(?:DROP\s+(?:TABLE|COLUMN)|TRUNCATE|DELETE\s+FROM)\b",
    re.IGNORECASE,
)


def _config(path: Path | None = None) -> AlembicConfig:
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    if path is not None:
        config.set_main_option("sqlalchemy.url", f"sqlite:///{path.as_posix()}")
    return config


def _static_text(node: ast.AST) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(_static_text(value) for value in node.values)
    if isinstance(node, ast.Call):
        return " ".join(_static_text(argument) for argument in node.args)
    return ""


def _dangerous_upgrade_operations(source: str) -> list[str]:
    module = ast.parse(source)
    upgrade = next(
        (
            node
            for node in module.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "upgrade"
        ),
        None,
    )
    if upgrade is None:
        return ["missing upgrade()"]

    findings: list[str] = []
    for node in ast.walk(upgrade):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Attribute) and function.attr in {
            "drop_table",
            "drop_column",
        }:
            findings.append(f"line {node.lineno}: {function.attr}")
        if (
            isinstance(function, ast.Attribute)
            and function.attr == "execute"
            and node.args
        ):
            sql = _static_text(node.args[0])
            if _DANGEROUS_SQL.search(sql):
                findings.append(f"line {node.lineno}: destructive SQL")
    return findings


def test_alembic_revision_graph_has_one_locked_linear_head() -> None:
    scripts = ScriptDirectory.from_config(_config())
    assert scripts.get_heads() == [EXPECTED_HEAD]

    revisions = list(scripts.walk_revisions())
    assert revisions
    assert len({revision.revision for revision in revisions}) == len(revisions)
    assert all(
        revision.down_revision is None
        or isinstance(revision.down_revision, str)
        for revision in revisions
    ), "Merge revisions and multiple Alembic parents require explicit review."

    visited: set[str] = set()
    current = scripts.get_revision(EXPECTED_HEAD)
    while current is not None:
        assert current.revision not in visited
        visited.add(current.revision)
        current = (
            scripts.get_revision(current.down_revision)
            if current.down_revision
            else None
        )
    assert visited == {revision.revision for revision in revisions}


def test_upgrade_functions_reject_unreviewed_destructive_operations() -> None:
    violations: dict[str, list[str]] = {}
    for migration in sorted(VERSIONS.glob("*.py")):
        source = migration.read_text(encoding="utf-8")
        findings = _dangerous_upgrade_operations(source)
        if findings:
            violations[migration.name] = findings
        module = ast.parse(source)
        functions = {
            node.name
            for node in module.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert {"upgrade", "downgrade"}.issubset(functions), migration.name

    assert violations == {}
    assert _dangerous_upgrade_operations(
        "def upgrade():\n    op.drop_table('scientific_results')\n"
    ) == ["line 2: drop_table"]
    assert _dangerous_upgrade_operations(
        "def upgrade():\n    op.execute('TRUNCATE scientific_results')\n"
    ) == ["line 2: destructive SQL"]


def test_0031_round_trip_preserves_existing_data_and_indexes(tmp_path: Path) -> None:
    database = tmp_path / "migration-safety.sqlite3"
    config = _config(database)
    alembic_command.upgrade(config, "0030_account_invitations")

    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users (id, email, display_name) "
                "VALUES ('migration-user', 'migration@local.invalid', 'Migration')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO organizations (id, name) "
                "VALUES ('migration-org', 'Migration')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO projects "
                "(id, organization_id, name, created_by) "
                "VALUES "
                "('migration-project', 'migration-org', 'Migration', "
                "'migration-user')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO sessions "
                "(id, project_id, mode, status, created_by) "
                "VALUES "
                "('migration-session', 'migration-project', 'auto', "
                "'active', 'migration-user')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO messages "
                "(id, session_id, role, content_summary, payload_json) "
                "VALUES "
                "('migration-message', 'migration-session', 'user', "
                "'Migration smoke', '{}')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO jobs "
                "(id, project_id, kind, status, created_by) "
                "VALUES "
                "('migration-job', 'migration-project', 'agent2', "
                "'completed', 'migration-user')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO scientific_objects "
                "(id, project_id, kind, object_type, display_name, "
                "lifecycle_status, created_by_user_id) "
                "VALUES "
                "('11111111111111111111111111111111', "
                "'migration-project', 'STRUCTURE', 'atomic.structure', "
                "'Migration structure', 'ACTIVE', 'migration-user')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO scientific_object_versions "
                "(id, scientific_object_id, version_no, object_type, "
                "object_schema_version, source_resource_refs_json, "
                "parent_object_version_refs_json, semantic_profile_ref_json, "
                "normalized_payload_ref_json, content_hash, semantic_hash, "
                "canonical_metadata_json, availability_status, "
                "created_by_user_id) "
                "VALUES "
                "('22222222222222222222222222222222', "
                "'11111111111111111111111111111111', 1, "
                "'atomic.structure', '1.0', '[]', '[]', '{}', "
                "'{\"artifactId\":\"migration-artifact\"}', "
                "'content-hash', 'semantic-hash', '{}', 'AVAILABLE', "
                "'migration-user')"
            )
        )
        connection.execute(
            text(
                "UPDATE scientific_objects "
                "SET current_version_id = "
                "'22222222222222222222222222222222' "
                "WHERE id = '11111111111111111111111111111111'"
            )
        )
        connection.execute(
            text(
                "INSERT INTO research_turns "
                "(id, project_id, research_session_id, sequence_no, "
                "user_message_id, action_type, status, job_id) "
                "VALUES "
                "('33333333333333333333333333333333', "
                "'migration-project', 'migration-session', 1, "
                "'migration-message', 'ANALYZE', 'COMPLETED', "
                "'migration-job')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO scientific_result_snapshots "
                "(id, project_id, research_turn_id, job_id, schema_version, "
                "projection_version, execution_status, relevance_status, "
                "source_fingerprint, bundle_json) "
                "VALUES "
                "('44444444444444444444444444444444', "
                "'migration-project', "
                "'33333333333333333333333333333333', 'migration-job', "
                "'1.0', 'migration-smoke', 'SUCCESS', 'CURRENT', "
                "'migration-source', "
                "'{\"sourceObjectVersionId\":"
                "\"22222222-2222-2222-2222-222222222222\"}')"
            )
        )
    engine.dispose()

    alembic_command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    assert "provider_connections" in inspect(engine).get_table_names()
    assert "idx_projects_search_owner_updated" in {
        item["name"] for item in inspect(engine).get_indexes("projects")
    }
    with engine.connect() as connection:
        assert connection.execute(
            text(
                "SELECT name FROM projects "
                "WHERE id = 'migration-project'"
            )
        ).scalar_one() == "Migration"
        exact_identity = connection.execute(
            text(
                "SELECT r.id, o.id, v.id, o.current_version_id "
                "FROM scientific_result_snapshots AS r "
                "JOIN research_turns AS t ON t.id = r.research_turn_id "
                "JOIN scientific_objects AS o "
                "ON o.project_id = r.project_id "
                "JOIN scientific_object_versions AS v "
                "ON v.scientific_object_id = o.id "
                "WHERE r.id = '44444444444444444444444444444444'"
            )
        ).one()
        assert tuple(str(item) for item in exact_identity) == (
            "44444444444444444444444444444444",
            "11111111111111111111111111111111",
            "22222222222222222222222222222222",
            "22222222222222222222222222222222",
        )
    engine.dispose()

    alembic_command.downgrade(config, "0030_account_invitations")
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    assert "idx_projects_search_owner_updated" not in {
        item["name"] for item in inspect(engine).get_indexes("projects")
    }
    with engine.connect() as connection:
        assert connection.execute(
            text("SELECT count(*) FROM projects WHERE id = 'migration-project'")
        ).scalar_one() == 1
        assert connection.execute(
            text(
                "SELECT count(*) FROM scientific_result_snapshots "
                "WHERE id = '44444444444444444444444444444444'"
            )
        ).scalar_one() == 1
    engine.dispose()

    alembic_command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    assert "idx_projects_search_owner_updated" in {
        item["name"] for item in inspect(engine).get_indexes("projects")
    }
    with engine.connect() as connection:
        assert connection.execute(
            text("SELECT count(*) FROM projects WHERE id = 'migration-project'")
        ).scalar_one() == 1
        assert connection.execute(
            text(
                "SELECT count(*) FROM scientific_object_versions "
                "WHERE id = '22222222222222222222222222222222'"
            )
        ).scalar_one() == 1
        assert connection.execute(
            text(
                "SELECT count(*) FROM scientific_result_snapshots "
                "WHERE id = '44444444444444444444444444444444'"
            )
        ).scalar_one() == 1
    engine.dispose()
