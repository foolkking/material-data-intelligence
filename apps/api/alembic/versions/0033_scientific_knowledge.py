"""Add bounded scholarly identity, snapshot and evidence authorities.

Revision ID: 0033_scientific_knowledge
Revises: 0032_provider_connections
"""

from alembic import op
import sqlalchemy as sa


revision = "0033_scientific_knowledge"
down_revision = "0032_provider_connections"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "literature_works",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("candidate_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column("canonical_key", sa.String(length=512), nullable=False, unique=True),
        sa.Column("doi", sa.String(length=512), nullable=True),
        sa.Column("arxiv_id", sa.String(length=128), nullable=True),
        sa.Column("arxiv_version", sa.String(length=16), nullable=True),
        sa.Column("relations_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "literature_snapshots",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("work_id", sa.Uuid(), sa.ForeignKey("literature_works.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_record_id", sa.String(length=512), nullable=False),
        sa.Column("provider_roles_json", sa.JSON(), nullable=False),
        sa.Column("title", sa.String(length=2000), nullable=False),
        sa.Column("authors_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("venue", sa.String(length=1000), nullable=True),
        sa.Column("publication_date", sa.Date(), nullable=True),
        sa.Column("publication_status", sa.String(length=64), nullable=False),
        sa.Column("publication_type", sa.String(length=128), nullable=True),
        sa.Column("doi", sa.String(length=512), nullable=True),
        sa.Column("arxiv_id", sa.String(length=128), nullable=True),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("retrieved_passages_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("cited_by_count", sa.Integer(), nullable=True),
        sa.Column("access_status", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.String(length=2000), nullable=True),
        sa.Column("open_access_url", sa.String(length=2000), nullable=True),
        sa.Column("license", sa.String(length=512), nullable=True),
        sa.Column("provider_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("provider_field_sources_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("raw_metadata_hash", sa.String(length=64), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.UniqueConstraint("provider", "provider_record_id", "raw_metadata_hash"),
    )
    op.create_table(
        "literature_searches",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("research_turn_id", sa.Uuid(), sa.ForeignKey("research_turns.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("requested_by", sa.String(length=64), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("query_json", sa.JSON(), nullable=False),
        sa.Column("query_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("candidate_ids_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("provider_errors_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "literature_evidence",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("research_turn_id", sa.Uuid(), sa.ForeignKey("research_turns.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("work_id", sa.Uuid(), sa.ForeignKey("literature_works.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), sa.ForeignKey("literature_snapshots.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("scope", sa.String(length=64), nullable=False),
        sa.Column("support_type", sa.String(length=64), nullable=False),
        sa.Column("purpose", sa.String(length=64), nullable=False),
        sa.Column("passage", sa.Text(), nullable=True),
        sa.Column("anchor_json", sa.JSON(), nullable=True),
        sa.Column("numeric_claims_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("claim_refs_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("source_content_hash", sa.String(length=64), nullable=False),
        sa.Column("selected_by", sa.String(length=64), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("selected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_literature_snapshots_work_retrieved", "literature_snapshots", ["work_id", "retrieved_at"])
    op.create_index("idx_literature_searches_project_created", "literature_searches", ["project_id", "created_at"])
    op.create_index("idx_literature_evidence_project_selected", "literature_evidence", ["project_id", "selected_at"])
    op.create_index("idx_literature_evidence_turn", "literature_evidence", ["research_turn_id"])


def downgrade() -> None:
    op.drop_index("idx_literature_evidence_turn", table_name="literature_evidence")
    op.drop_index("idx_literature_evidence_project_selected", table_name="literature_evidence")
    op.drop_index("idx_literature_searches_project_created", table_name="literature_searches")
    op.drop_index("idx_literature_snapshots_work_retrieved", table_name="literature_snapshots")
    op.drop_table("literature_evidence")
    op.drop_table("literature_searches")
    op.drop_table("literature_snapshots")
    op.drop_table("literature_works")
