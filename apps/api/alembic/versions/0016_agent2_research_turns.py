"""Agent 2.0 research turns, immutable context, and domain events."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0016_agent2_research_turns"
down_revision = "0015_agent2_scientific_objects"
branch_labels = None
depends_on = None


def _existing_tables() -> set[str]:
    return set(inspect(op.get_bind()).get_table_names())


def _foreign_key(
    existing: set[str],
    local: str,
    remote_table: str,
    remote_column: str = "id",
    *,
    name: str,
    ondelete: str,
) -> sa.ForeignKeyConstraint | None:
    if remote_table not in existing:
        return None
    return sa.ForeignKeyConstraint(
        [local], [f"{remote_table}.{remote_column}"], name=name, ondelete=ondelete
    )


def upgrade() -> None:
    # The two tables created by this revision are available to each other;
    # legacy references are included only when their real parent table exists.
    existing = _existing_tables() | {"research_turns", "research_context_snapshots"}
    turn_foreign_keys = [
        item
        for item in (
            _foreign_key(existing, "project_id", "projects", name="fk_rt_project", ondelete="RESTRICT"),
            _foreign_key(existing, "research_session_id", "sessions", name="fk_rt_session", ondelete="RESTRICT"),
            _foreign_key(existing, "parent_turn_id", "research_turns", name="fk_rt_parent", ondelete="RESTRICT"),
            _foreign_key(existing, "continuation_of_turn_id", "research_turns", name="fk_rt_continuation", ondelete="RESTRICT"),
            _foreign_key(existing, "user_message_id", "messages", name="fk_rt_user_message", ondelete="RESTRICT"),
            _foreign_key(existing, "assistant_pre_message_id", "messages", name="fk_rt_pre_message", ondelete="SET NULL"),
            _foreign_key(existing, "assistant_final_message_id", "messages", name="fk_rt_final_message", ondelete="SET NULL"),
            _foreign_key(existing, "analysis_intent_id", "analysis_intents", name="fk_rt_intent", ondelete="RESTRICT"),
            _foreign_key(existing, "analysis_plan_id", "analysis_plans", name="fk_rt_plan", ondelete="RESTRICT"),
            _foreign_key(existing, "job_id", "jobs", name="fk_rt_job", ondelete="RESTRICT"),
            _foreign_key(existing, "interpretation_id", "scientific_interpretations", name="fk_rt_interpretation", ondelete="RESTRICT"),
            _foreign_key(existing, "report_id", "reports", name="fk_rt_report", ondelete="RESTRICT"),
        )
        if item is not None
    ]
    op.create_table(
        "research_turns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("research_session_id", sa.String(length=64), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("parent_turn_id", sa.Uuid(), nullable=True),
        sa.Column("continuation_of_turn_id", sa.Uuid(), nullable=True),
        sa.Column("user_message_id", sa.String(length=64), nullable=False),
        sa.Column("assistant_pre_message_id", sa.String(length=64), nullable=True),
        sa.Column("assistant_final_message_id", sa.String(length=64), nullable=True),
        sa.Column("action_type", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("context_snapshot_id", sa.Uuid(), nullable=True),
        sa.Column("analysis_intent_id", sa.String(length=96), nullable=True),
        sa.Column("analysis_plan_id", sa.String(length=96), nullable=True),
        sa.Column("job_id", sa.String(length=64), nullable=True),
        sa.Column("interpretation_id", sa.String(length=96), nullable=True),
        sa.Column("report_id", sa.String(length=96), nullable=True),
        sa.Column("error_code", sa.String(length=96), nullable=True),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("row_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("sequence_no >= 1", name="ck_rt_sequence_no"),
        sa.CheckConstraint("row_version >= 1", name="ck_rt_row_version"),
        sa.CheckConstraint("action_type is null or action_type in ('ANSWER', 'CLARIFY', 'ANALYZE', 'CONTINUE_ANALYSIS', 'INTERPRET_RESULT', 'QUERY_DATA', 'MANAGE_DATA', 'OPEN_OBJECT', 'CREATE_REPORT', 'UPDATE_REPORT', 'EXPORT')", name="ck_rt_action"),
        sa.CheckConstraint("status in ('RECEIVED', 'RESOLVING_CONTEXT', 'ORCHESTRATING', 'NEEDS_CLARIFICATION', 'ANSWERED', 'UNSUPPORTED', 'READY_TO_PLAN', 'PLANNING', 'PLAN_REJECTED', 'QUEUED', 'RUNNING', 'INTERPRETING', 'COMPLETED', 'PARTIAL', 'FAILED', 'CANCELED')", name="ck_rt_status"),
        *turn_foreign_keys,
        sa.PrimaryKeyConstraint("id", name="pk_research_turns"),
        sa.UniqueConstraint("research_session_id", "sequence_no", name="uq_research_turns_session_sequence"),
        sa.UniqueConstraint("user_message_id", name="uq_research_turns_user_message_id"),
    )
    op.create_index("idx_research_turns_project_created", "research_turns", ["project_id", "created_at"])
    op.create_index("idx_research_turns_session_sequence", "research_turns", ["research_session_id", "sequence_no"])
    op.create_index("idx_research_turns_status_updated", "research_turns", ["status", "updated_at"])
    op.create_index("idx_research_turns_job", "research_turns", ["job_id"])
    op.create_index("idx_research_turns_plan", "research_turns", ["analysis_plan_id"])

    op.create_table(
        "research_context_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("research_session_id", sa.String(length=64), nullable=False),
        sa.Column("research_turn_id", sa.Uuid(), nullable=False),
        sa.Column("snapshot_schema_version", sa.String(length=32), nullable=False),
        sa.Column("active_scope_refs_json", sa.JSON(), nullable=False),
        sa.Column("selection_refs_json", sa.JSON(), nullable=False),
        sa.Column("resolved_references_json", sa.JSON(), nullable=False),
        sa.Column("referenced_result_refs_json", sa.JSON(), nullable=False),
        sa.Column("relevant_finding_refs_json", sa.JSON(), nullable=False),
        sa.Column("effective_constraints_json", sa.JSON(), nullable=False),
        sa.Column("research_goal", sa.Text(), nullable=True),
        sa.Column("unresolved_questions_json", sa.JSON(), nullable=False),
        sa.Column("context_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("compiler_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        *[
            item
            for item in (
                _foreign_key(existing, "project_id", "projects", name="fk_rcs_project", ondelete="RESTRICT"),
                _foreign_key(existing, "research_session_id", "sessions", name="fk_rcs_session", ondelete="RESTRICT"),
            )
            if item is not None
        ],
        sa.ForeignKeyConstraint(["research_turn_id"], ["research_turns.id"], name="fk_rcs_turn", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_research_context_snapshots"),
        sa.UniqueConstraint("research_turn_id", name="uq_research_context_snapshots_research_turn_id"),
    )
    op.create_index("idx_research_context_snapshots_session", "research_context_snapshots", ["research_session_id"])

    op.create_table(
        "research_turn_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("turn_id", sa.Uuid(), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=96), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("sequence_no >= 1", name="ck_rte_sequence_no"),
        sa.ForeignKeyConstraint(["turn_id"], ["research_turns.id"], name="fk_rte_turn", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_research_turn_events"),
        sa.UniqueConstraint("turn_id", "sequence_no", name="uq_research_turn_events_turn_sequence"),
    )
    op.create_index("idx_research_turn_events_turn", "research_turn_events", ["turn_id"])

    with op.batch_alter_table("research_turns") as batch:
        batch.create_foreign_key(
            "fk_rt_context",
            "research_context_snapshots",
            ["context_snapshot_id"],
            ["id"],
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    existing = _existing_tables()
    if "research_turns" in existing and "research_context_snapshots" in existing:
        turn_fks = inspect(op.get_bind()).get_foreign_keys("research_turns")
        if any(item.get("name") == "fk_rt_context" for item in turn_fks):
            with op.batch_alter_table("research_turns") as batch:
                batch.drop_constraint("fk_rt_context", type_="foreignkey")
    op.drop_index("idx_research_turn_events_turn", table_name="research_turn_events")
    op.drop_table("research_turn_events")
    op.drop_index("idx_research_context_snapshots_session", table_name="research_context_snapshots")
    op.drop_table("research_context_snapshots")
    op.drop_index("idx_research_turns_plan", table_name="research_turns")
    op.drop_index("idx_research_turns_job", table_name="research_turns")
    op.drop_index("idx_research_turns_status_updated", table_name="research_turns")
    op.drop_index("idx_research_turns_session_sequence", table_name="research_turns")
    op.drop_index("idx_research_turns_project_created", table_name="research_turns")
    op.drop_table("research_turns")
