"""Agent 2.0 validated Research Turn orchestration decisions."""

from alembic import op
import sqlalchemy as sa


revision = "0018_agent2_orchestration_decisions"
down_revision = "0017_agent2_scientific_results"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "research_turn_decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("research_turn_id", sa.Uuid(), nullable=False),
        sa.Column("contract_version", sa.String(length=32), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("decision_json", sa.JSON(), nullable=False),
        sa.Column("input_context_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("prompt_version", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("provider_request_id", sa.String(length=128), nullable=True),
        sa.Column("repair_attempted", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("validation_status", sa.String(length=32), nullable=False),
        sa.Column("action_dispatch_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("validation_status = 'VALIDATED'", name="ck_rtd_validation"),
        sa.CheckConstraint(
            "action_dispatch_status in ('COMPLETED', 'READY_FOR_DOWNSTREAM')",
            name="ck_rtd_dispatch",
        ),
        sa.ForeignKeyConstraint(
            ["research_turn_id"], ["research_turns.id"],
            name="fk_rtd_turn", ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_research_turn_decisions"),
        sa.UniqueConstraint("research_turn_id", name="uq_research_turn_decisions_turn"),
    )
    op.create_index(
        "idx_research_turn_decisions_action_created",
        "research_turn_decisions",
        ["action", "created_at"],
    )
    op.create_index(
        "idx_research_turn_decisions_fingerprint",
        "research_turn_decisions",
        ["input_context_fingerprint"],
    )


def downgrade() -> None:
    op.drop_index("idx_research_turn_decisions_fingerprint", table_name="research_turn_decisions")
    op.drop_index("idx_research_turn_decisions_action_created", table_name="research_turn_decisions")
    op.drop_table("research_turn_decisions")
