from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from mdi_api.config import load_settings
from mdi_api.db import metadata


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

runtime_database_url = load_settings().database_url
if os.getenv("DATABASE_URL") or os.getenv("MDI_DATABASE_URL") or os.getenv("POSTGRES_HOST"):
    config.set_main_option("sqlalchemy.url", runtime_database_url.replace("%", "%%"))

target_metadata = metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
