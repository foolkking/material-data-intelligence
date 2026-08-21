"""Persist the owning Research Session for each analysis run."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0014_research_session_run_bindings"
down_revision = "0013_drop_decision_execution_unique"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "research_session_runs",
        sa.Column("session_id", sa.String(length=64), sa.ForeignKey("sessions.id"), primary_key=True),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("jobs.id"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("job_id", name="uq_research_session_runs_job_id"),
    )
    op.create_index(
        "idx_research_session_runs_session_created",
        "research_session_runs",
        ["session_id", "created_at"],
    )
    _backfill_from_assistant_messages()


def downgrade() -> None:
    op.drop_index("idx_research_session_runs_session_created", table_name="research_session_runs")
    op.drop_table("research_session_runs")


def _backfill_from_assistant_messages() -> None:
    connection = op.get_bind()
    metadata = sa.MetaData()
    messages = sa.Table("messages", metadata, autoload_with=connection)
    sessions = sa.Table("sessions", metadata, autoload_with=connection)
    jobs = sa.Table("jobs", metadata, autoload_with=connection)
    bindings = sa.Table("research_session_runs", metadata, autoload_with=connection)

    session_projects = dict(connection.execute(sa.select(sessions.c.id, sessions.c.project_id)).all())
    job_projects = dict(connection.execute(sa.select(jobs.c.id, jobs.c.project_id)).all())
    rows = connection.execute(
        sa.select(messages.c.session_id, messages.c.payload_json, messages.c.created_at)
        .where(messages.c.role == "agent")
        .order_by(messages.c.created_at.asc(), messages.c.id.asc())
    ).mappings()
    bound_jobs: set[str] = set()
    for row in rows:
        payload = row["payload_json"] or {}
        if not isinstance(payload, dict) or payload.get("source") != "research_assistant_projection":
            continue
        job_id = str(payload.get("runId") or "")
        session_id = str(row["session_id"] or "")
        if not job_id or job_id in bound_jobs:
            continue
        if session_projects.get(session_id) != job_projects.get(job_id):
            continue
        connection.execute(
            bindings.insert().values(
                session_id=session_id,
                job_id=job_id,
                created_at=row["created_at"],
            )
        )
        bound_jobs.add(job_id)
