from __future__ import annotations

from alembic import op

from mdi_api.migrations import PHASE4_MIGRATION_BASELINE_SQL


revision = "0001_phase4_persistence_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    sqlite = op.get_bind().dialect.name == "sqlite"
    for statement in _split_sql(PHASE4_MIGRATION_BASELINE_SQL):
        op.execute(_sqlite_statement(statement) if sqlite else statement)


def downgrade() -> None:
    sqlite = op.get_bind().dialect.name == "sqlite"
    for table_name in (
        "reports",
        "visualization_recipes",
        "artifacts",
        "tool_calls",
        "job_events",
        "jobs",
        "data_profiles",
        "datasets",
        "projects",
    ):
        suffix = "" if sqlite else " CASCADE"
        op.execute(f"DROP TABLE IF EXISTS {table_name}{suffix}")


def _sqlite_statement(statement: str) -> str:
    """Preserve baseline semantics using SQLite's supported DDL vocabulary."""
    return (
        statement.replace("timestamptz", "datetime")
        .replace("::jsonb", "")
        .replace("jsonb", "json")
        .replace("DEFAULT now()", "DEFAULT CURRENT_TIMESTAMP")
    )


def _split_sql(sql: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        current.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(current).rstrip(";"))
            current = []
    if current:
        statements.append("\n".join(current))
    return statements
