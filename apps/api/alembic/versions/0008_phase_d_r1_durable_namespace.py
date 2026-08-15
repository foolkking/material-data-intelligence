from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0008_phase_d_r1_namespace"
down_revision = "0007_phase10m1_workspace_domain"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    projects = sa.table(
        "projects",
        sa.column("organization_id", sa.String(length=64)),
        sa.column("created_by", sa.String(length=64)),
    )
    users = sa.table(
        "users",
        sa.column("id", sa.String(length=64)),
        sa.column("email", sa.String(length=320)),
        sa.column("display_name", sa.String(length=160)),
    )
    organizations = sa.table(
        "organizations",
        sa.column("id", sa.String(length=64)),
        sa.column("name", sa.String(length=160)),
    )
    bind = op.get_bind()
    actor_ids = bind.execute(sa.select(projects.c.created_by).distinct()).scalars().all()
    organization_ids = bind.execute(sa.select(projects.c.organization_id).distinct()).scalars().all()
    if actor_ids:
        bind.execute(
            sa.insert(users),
            [
                {
                    "id": actor_id,
                    "email": f"{actor_id}@local.invalid",
                    "display_name": actor_id,
                }
                for actor_id in actor_ids
            ],
        )
    if organization_ids:
        bind.execute(
            sa.insert(organizations),
            [{"id": organization_id, "name": organization_id} for organization_id in organization_ids],
        )

    with op.batch_alter_table("projects") as batch:
        batch.create_foreign_key(
            "fk_projects_organization_id_organizations",
            "organizations",
            ["organization_id"],
            ["id"],
        )
        batch.create_foreign_key(
            "fk_projects_created_by_users",
            "users",
            ["created_by"],
            ["id"],
        )
    op.create_index(
        "idx_projects_org_created",
        "projects",
        ["organization_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_projects_org_created", table_name="projects")
    with op.batch_alter_table("projects") as batch:
        batch.drop_constraint("fk_projects_created_by_users", type_="foreignkey")
        batch.drop_constraint("fk_projects_organization_id_organizations", type_="foreignkey")
    op.drop_table("organizations")
    op.drop_table("users")
