"""Agent 2.0 scientific object identity and immutable versions."""

from alembic import op
import sqlalchemy as sa


revision = "0015_agent2_scientific_objects"
down_revision = "0014_research_session_run_bindings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scientific_objects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("object_type", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=512), nullable=False),
        sa.Column("lifecycle_status", sa.String(length=32), server_default="ACTIVE", nullable=False),
        sa.Column("current_version_id", sa.Uuid(), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("row_version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint("row_version >= 1", name="ck_so_row_version"),
        sa.CheckConstraint(
            "lifecycle_status in ('ACTIVE', 'ARCHIVED', 'INVALIDATED')",
            name="ck_so_lifecycle",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], name="fk_so_project", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], name="fk_so_creator", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_scientific_objects"),
    )
    op.create_index("idx_scientific_objects_project_lifecycle", "scientific_objects", ["project_id", "lifecycle_status"])
    op.create_index("idx_scientific_objects_project_kind", "scientific_objects", ["project_id", "kind"])
    op.create_index("idx_scientific_objects_project_type", "scientific_objects", ["project_id", "object_type"])
    op.create_index("idx_scientific_objects_current_version", "scientific_objects", ["current_version_id"])

    op.create_table(
        "scientific_object_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scientific_object_id", sa.Uuid(), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("object_type", sa.String(length=128), nullable=False),
        sa.Column("object_schema_version", sa.String(length=32), nullable=False),
        sa.Column("source_resource_refs_json", sa.JSON(), nullable=False),
        sa.Column("parent_object_version_refs_json", sa.JSON(), nullable=False),
        sa.Column("semantic_profile_ref_json", sa.JSON(), nullable=True),
        sa.Column("normalized_payload_ref_json", sa.JSON(), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("semantic_hash", sa.String(length=128), nullable=False),
        sa.Column("canonical_metadata_json", sa.JSON(), nullable=False),
        sa.Column("availability_status", sa.String(length=32), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("version_no >= 1", name="ck_sov_version_no"),
        sa.CheckConstraint(
            "availability_status in ('AVAILABLE', 'PARTIALLY_AVAILABLE', 'SOURCE_MISSING', 'INVALID')",
            name="ck_sov_availability",
        ),
        sa.ForeignKeyConstraint(["scientific_object_id"], ["scientific_objects.id"], name="fk_sov_object", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], name="fk_sov_creator", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_scientific_object_versions"),
        sa.UniqueConstraint("scientific_object_id", "version_no", name="uq_scientific_object_versions_object_version"),
    )
    op.create_index("idx_scientific_object_versions_object", "scientific_object_versions", ["scientific_object_id"])
    op.create_index("idx_scientific_object_versions_type", "scientific_object_versions", ["object_type"])
    op.create_index("idx_scientific_object_versions_content_hash", "scientific_object_versions", ["content_hash"])
    op.create_index("idx_scientific_object_versions_semantic_hash", "scientific_object_versions", ["semantic_hash"])

    op.create_table(
        "scientific_object_relationships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("source_version_id", sa.Uuid(), nullable=False),
        sa.Column("target_version_id", sa.Uuid(), nullable=False),
        sa.Column("relation_type", sa.String(length=128), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("source_version_id <> target_version_id", name="ck_sor_not_self"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], name="fk_sor_project", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["source_version_id"], ["scientific_object_versions.id"], name="fk_sor_source", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["target_version_id"], ["scientific_object_versions.id"], name="fk_sor_target", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], name="fk_sor_creator", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_scientific_object_relationships"),
        sa.UniqueConstraint("source_version_id", "target_version_id", "relation_type", name="uq_scientific_object_relationship_edge"),
    )
    op.create_index("idx_scientific_object_relationships_project", "scientific_object_relationships", ["project_id"])
    op.create_index("idx_scientific_object_relationships_source", "scientific_object_relationships", ["source_version_id"])
    op.create_index("idx_scientific_object_relationships_target", "scientific_object_relationships", ["target_version_id"])

    with op.batch_alter_table("scientific_objects") as batch:
        batch.create_foreign_key(
            "fk_so_current_version",
            "scientific_object_versions",
            ["current_version_id"],
            ["id"],
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    with op.batch_alter_table("scientific_objects") as batch:
        batch.drop_constraint("fk_so_current_version", type_="foreignkey")
    op.drop_index("idx_scientific_object_relationships_target", table_name="scientific_object_relationships")
    op.drop_index("idx_scientific_object_relationships_source", table_name="scientific_object_relationships")
    op.drop_index("idx_scientific_object_relationships_project", table_name="scientific_object_relationships")
    op.drop_table("scientific_object_relationships")
    op.drop_index("idx_scientific_object_versions_semantic_hash", table_name="scientific_object_versions")
    op.drop_index("idx_scientific_object_versions_content_hash", table_name="scientific_object_versions")
    op.drop_index("idx_scientific_object_versions_type", table_name="scientific_object_versions")
    op.drop_index("idx_scientific_object_versions_object", table_name="scientific_object_versions")
    op.drop_table("scientific_object_versions")
    op.drop_index("idx_scientific_objects_current_version", table_name="scientific_objects")
    op.drop_index("idx_scientific_objects_project_type", table_name="scientific_objects")
    op.drop_index("idx_scientific_objects_project_kind", table_name="scientific_objects")
    op.drop_index("idx_scientific_objects_project_lifecycle", table_name="scientific_objects")
    op.drop_table("scientific_objects")
