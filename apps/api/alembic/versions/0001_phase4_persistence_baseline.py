from __future__ import annotations

from alembic import op

from mdi_api.migrations import PHASE4_MIGRATION_BASELINE_SQL


revision = "0001_phase4_persistence_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    for statement in _split_sql(PHASE4_MIGRATION_BASELINE_SQL):
        op.execute(statement)


def downgrade() -> None:
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
        op.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")


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
