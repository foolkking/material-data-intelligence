"""Add production indexes for authorized keyset product search.

Revision ID: 0031_product_search_keyset
Revises: 0030_account_invitations
"""

from alembic import op
from sqlalchemy import inspect


revision = "0031_product_search_keyset"
down_revision = "0030_account_invitations"
branch_labels = None
depends_on = None


_INDEXES = (
    (
        "idx_projects_search_owner_updated",
        "projects",
        ["created_by", "updated_at", "id"],
    ),
    (
        "idx_project_members_search_user_project",
        "project_members",
        ["user_id", "project_id"],
    ),
    (
        "idx_datasets_search_project_updated",
        "datasets",
        ["project_id", "updated_at", "id"],
    ),
    (
        "idx_sessions_search_project_created",
        "sessions",
        ["project_id", "created_at", "id"],
    ),
    (
        "idx_reports_search_project_created",
        "reports",
        ["project_id", "created_at", "id"],
    ),
    (
        "idx_scientific_objects_search_project_created",
        "scientific_objects",
        ["project_id", "created_at", "id"],
    ),
    (
        "idx_scientific_results_search_project_created",
        "scientific_result_snapshots",
        ["project_id", "created_at", "id"],
    ),
)


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    table_names = set(inspector.get_table_names())
    for index_name, table_name, columns in _INDEXES:
        if table_name not in table_names:
            continue
        existing_columns = {
            str(item["name"])
            for item in inspector.get_columns(table_name)
        }
        if not set(columns).issubset(existing_columns):
            continue
        existing = {
            str(item["name"])
            for item in inspector.get_indexes(table_name)
        }
        if index_name not in existing:
            op.create_index(index_name, table_name, columns)


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    table_names = set(inspector.get_table_names())
    for index_name, table_name, _columns in reversed(_INDEXES):
        if table_name not in table_names:
            continue
        existing = {
            str(item["name"])
            for item in inspector.get_indexes(table_name)
        }
        if index_name in existing:
            op.drop_index(index_name, table_name=table_name)
