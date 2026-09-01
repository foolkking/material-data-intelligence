"""Reconcile foundation tables that predated their Alembic authority.

The application metadata has always declared these tables, but the original
baseline migration omitted them.  Some long-lived databases therefore already
contain the correct objects (created by the historical bootstrap path), while
fresh Alembic databases do not.  This revision is deliberately conservative:

* compatible existing tables are retained;
* missing tables and safe missing indexes are created;
* incompatible columns, primary keys, foreign keys, checks, or same-name
  indexes fail before any missing table is created.

Revision ID: 0028_foundation_schema_reconciliation
Revises: 0027_research_session_management
"""

from __future__ import annotations

from collections.abc import Callable
import re
from typing import NamedTuple

from alembic import op
import sqlalchemy as sa


revision = "0028_foundation_schema_reconciliation"
down_revision = "0027_research_session_management"
branch_labels = None
depends_on = None


class ColumnShape(NamedTuple):
    kind: str
    nullable: bool
    length: int | None = None


class TableShape(NamedTuple):
    columns: dict[str, ColumnShape]
    primary_key: tuple[str, ...]
    foreign_keys: frozenset[tuple[tuple[str, ...], str, tuple[str, ...]]]
    check_fragments: tuple[str, ...] = ()


FOUNDATION_SHAPES: dict[str, TableShape] = {
    "project_members": TableShape(
        columns={
            "project_id": ColumnShape("string", False, 64),
            "user_id": ColumnShape("string", False, 64),
            "role": ColumnShape("string", False, 32),
            "created_at": ColumnShape("datetime", False),
        },
        primary_key=("project_id", "user_id"),
        foreign_keys=frozenset(
            {
                (("project_id",), "projects", ("id",)),
                (("user_id",), "users", ("id",)),
            }
        ),
        # PostgreSQL rewrites IN (...) to = ANY (ARRAY[...]); require the
        # constrained column and every permitted role rather than one
        # dialect-specific rendering of the expression.
        check_fragments=("role", "'owner'", "'admin'", "'researcher'", "'viewer'"),
    ),
    "files": TableShape(
        columns={
            "id": ColumnShape("string", False, 64),
            "dataset_id": ColumnShape("string", False, 64),
            "file_name": ColumnShape("string", False, 255),
            "media_type": ColumnShape("string", False, 160),
            "detected_format": ColumnShape("string", False, 64),
            "storage_key": ColumnShape("text", False),
            "sha256": ColumnShape("string", False, 64),
            "size_bytes": ColumnShape("integer", False),
            "parse_status": ColumnShape("string", False, 32),
            "created_at": ColumnShape("datetime", False),
        },
        primary_key=("id",),
        foreign_keys=frozenset({(("dataset_id",), "datasets", ("id",))}),
        check_fragments=("size_bytes>=0",),
    ),
    "field_mappings": TableShape(
        columns={
            "id": ColumnShape("string", False, 64),
            "dataset_id": ColumnShape("string", False, 64),
            "mapping_json": ColumnShape("json", False),
            "created_by": ColumnShape("string", False, 64),
            "created_at": ColumnShape("datetime", False),
        },
        primary_key=("id",),
        foreign_keys=frozenset(
            {
                (("dataset_id",), "datasets", ("id",)),
                (("created_by",), "users", ("id",)),
            }
        ),
    ),
    "user_configs": TableShape(
        columns={
            "id": ColumnShape("string", False, 64),
            "user_id": ColumnShape("string", False, 64),
            "config_json": ColumnShape("json", False),
            "updated_at": ColumnShape("datetime", False),
        },
        primary_key=("id",),
        foreign_keys=frozenset({(("user_id",), "users", ("id",))}),
    ),
    "secrets": TableShape(
        columns={
            "id": ColumnShape("string", False, 64),
            "owner_type": ColumnShape("string", False, 32),
            "owner_id": ColumnShape("string", False, 64),
            "provider": ColumnShape("string", False, 80),
            "secret_ref": ColumnShape("string", False, 160),
            "encrypted_blob_key": ColumnShape("text", False),
            "created_at": ColumnShape("datetime", False),
        },
        primary_key=("id",),
        foreign_keys=frozenset(),
    ),
    "audit_logs": TableShape(
        columns={
            "id": ColumnShape("string", False, 64),
            "actor_user_id": ColumnShape("string", True, 64),
            "project_id": ColumnShape("string", True, 64),
            "action": ColumnShape("string", False, 120),
            "target_type": ColumnShape("string", False, 80),
            "target_id": ColumnShape("string", False, 96),
            "metadata_json": ColumnShape("json", False),
            "created_at": ColumnShape("datetime", False),
        },
        primary_key=("id",),
        foreign_keys=frozenset(
            {
                (("actor_user_id",), "users", ("id",)),
                (("project_id",), "projects", ("id",)),
            }
        ),
    ),
}

REQUIRED_INDEXES: dict[str, tuple[str, tuple[str, ...]]] = {
    "idx_project_members_user": ("project_members", ("user_id",)),
    "idx_files_dataset_created": ("files", ("dataset_id", "created_at")),
    "idx_audit_logs_project_created": ("audit_logs", ("project_id", "created_at")),
}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # Validate every pre-existing object before mutating the schema.  This
    # prevents a partially reconciled database when one historical table has
    # drifted from the application authority.
    for table_name, shape in FOUNDATION_SHAPES.items():
        if table_name in existing_tables:
            _validate_table(inspector, table_name, shape)
    _validate_existing_indexes(inspector, existing_tables)
    _widen_alembic_version_if_needed(inspector)

    creators: dict[str, Callable[[], None]] = {
        "project_members": _create_project_members,
        "files": _create_files,
        "field_mappings": _create_field_mappings,
        "user_configs": _create_user_configs,
        "secrets": _create_secrets,
        "audit_logs": _create_audit_logs,
    }
    for table_name, creator in creators.items():
        if table_name not in existing_tables:
            creator()

    # Re-inspect after table creation.  A compatible historical table may be
    # missing only a safe, non-unique lookup index; add it without rewriting
    # data.  Same-name indexes with different columns were rejected above.
    inspector = sa.inspect(bind)
    for index_name, (table_name, columns) in REQUIRED_INDEXES.items():
        indexes = {item["name"]: item for item in inspector.get_indexes(table_name)}
        if index_name not in indexes:
            op.create_index(index_name, table_name, list(columns))


def downgrade() -> None:
    # This revision reconciles long-standing application metadata with Alembic;
    # it does not introduce a disposable feature domain.  Dropping a table on
    # downgrade could destroy files, access control, user configuration,
    # secrets references, or audit history that existed before revision 0028.
    # The safe downgrade is therefore intentionally schema-preserving.
    pass


def _validate_table(
    inspector: sa.Inspector,
    table_name: str,
    expected: TableShape,
) -> None:
    actual_columns = {item["name"]: item for item in inspector.get_columns(table_name)}
    if set(actual_columns) != set(expected.columns):
        _incompatible(
            table_name,
            f"columns expected={sorted(expected.columns)} actual={sorted(actual_columns)}",
        )
    for column_name, shape in expected.columns.items():
        actual = actual_columns[column_name]
        actual_shape = _column_shape(actual["type"], bool(actual["nullable"]))
        if actual_shape != shape:
            _incompatible(
                table_name,
                f"column {column_name} expected={shape} actual={actual_shape}",
            )

    primary_key = tuple(inspector.get_pk_constraint(table_name).get("constrained_columns") or ())
    if primary_key != expected.primary_key:
        _incompatible(
            table_name,
            f"primary key expected={expected.primary_key} actual={primary_key}",
        )

    foreign_keys = frozenset(
        (
            tuple(item.get("constrained_columns") or ()),
            str(item.get("referred_table") or ""),
            tuple(item.get("referred_columns") or ()),
        )
        for item in inspector.get_foreign_keys(table_name)
    )
    if foreign_keys != expected.foreign_keys:
        _incompatible(
            table_name,
            f"foreign keys expected={sorted(expected.foreign_keys)} actual={sorted(foreign_keys)}",
        )

    normalized_checks = tuple(
        _normalize_sql(str(item.get("sqltext") or ""))
        for item in inspector.get_check_constraints(table_name)
    )
    for fragment in expected.check_fragments:
        if not any(fragment in value for value in normalized_checks):
            _incompatible(
                table_name,
                f"missing required check expression {fragment!r}",
            )


def _validate_existing_indexes(
    inspector: sa.Inspector,
    existing_tables: set[str],
) -> None:
    for index_name, (table_name, columns) in REQUIRED_INDEXES.items():
        if table_name not in existing_tables:
            continue
        indexes = {item["name"]: item for item in inspector.get_indexes(table_name)}
        actual = indexes.get(index_name)
        if actual is None:
            continue
        actual_columns = tuple(actual.get("column_names") or ())
        if actual_columns != columns or bool(actual.get("unique")):
            _incompatible(
                table_name,
                f"index {index_name} expected columns={columns}, unique=False; "
                f"actual columns={actual_columns}, unique={bool(actual.get('unique'))}",
            )


def _widen_alembic_version_if_needed(inspector: sa.Inspector) -> None:
    """Allow a directly reconciled 0027 marker to record descriptive 0028.

    Databases that actually ran revision 0011 already use VARCHAR(64).
    Historical bootstrap databases may have all later schema objects while
    retaining the original VARCHAR(32) Alembic version column.  This mirrors
    the safe widening in revision 0011 without changing marker identity.
    """

    if op.get_bind().dialect.name != "postgresql":
        return
    version_columns = {
        item["name"]: item for item in inspector.get_columns("alembic_version")
    }
    version_type = version_columns["version_num"]["type"]
    if isinstance(version_type, sa.String) and (version_type.length or 0) < 64:
        op.alter_column(
            "alembic_version",
            "version_num",
            type_=sa.String(64),
            existing_type=version_type,
            existing_nullable=False,
        )


def _column_shape(column_type: sa.types.TypeEngine, nullable: bool) -> ColumnShape:
    if isinstance(column_type, sa.JSON):
        return ColumnShape("json", nullable)
    if isinstance(column_type, sa.Text):
        return ColumnShape("text", nullable)
    if isinstance(column_type, sa.String):
        return ColumnShape("string", nullable, column_type.length)
    if isinstance(column_type, sa.DateTime):
        return ColumnShape("datetime", nullable)
    if isinstance(column_type, sa.Integer):
        return ColumnShape("integer", nullable)
    return ColumnShape(type(column_type).__name__.lower(), nullable)


def _normalize_sql(value: str) -> str:
    return re.sub(r"[\s\"]+", "", value).lower()


def _incompatible(table_name: str, detail: str) -> None:
    raise RuntimeError(
        "0028 foundation schema reconciliation refused incompatible existing "
        f"table {table_name!r}: {detail}"
    )


def _create_project_members() -> None:
    op.create_table(
        "project_members",
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "role in ('owner', 'admin', 'researcher', 'viewer')",
            name="ck_project_members_project_member_role",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="fk_project_members_project_id_projects",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_project_members_user_id_users",
        ),
        sa.PrimaryKeyConstraint(
            "project_id",
            "user_id",
            name="pk_project_members",
        ),
    )


def _create_files() -> None:
    op.create_table(
        "files",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("dataset_id", sa.String(64), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("media_type", sa.String(160), nullable=False),
        sa.Column("detected_format", sa.String(64), nullable=False, server_default="unknown"),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("parse_status", sa.String(32), nullable=False, server_default="uploaded"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("size_bytes >= 0", name="ck_files_file_size_non_negative"),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["datasets.id"],
            name="fk_files_dataset_id_datasets",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_files"),
    )


def _create_field_mappings() -> None:
    op.create_table(
        "field_mappings",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("dataset_id", sa.String(64), nullable=False),
        sa.Column("mapping_json", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["datasets.id"],
            name="fk_field_mappings_dataset_id_datasets",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name="fk_field_mappings_created_by_users",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_field_mappings"),
    )


def _create_user_configs() -> None:
    op.create_table(
        "user_configs",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_configs_user_id_users",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_configs"),
    )


def _create_secrets() -> None:
    op.create_table(
        "secrets",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("owner_type", sa.String(32), nullable=False),
        sa.Column("owner_id", sa.String(64), nullable=False),
        sa.Column("provider", sa.String(80), nullable=False),
        sa.Column("secret_ref", sa.String(160), nullable=False),
        sa.Column("encrypted_blob_key", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_secrets"),
    )


def _create_audit_logs() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("actor_user_id", sa.String(64), nullable=True),
        sa.Column("project_id", sa.String(64), nullable=True),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("target_type", sa.String(80), nullable=False),
        sa.Column("target_id", sa.String(96), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name="fk_audit_logs_actor_user_id_users",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="fk_audit_logs_project_id_projects",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
    )
