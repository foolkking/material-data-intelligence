from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from sqlalchemy import text

from mdi_api.config import ApiSettings
from mdi_api.database import (
    create_engine_from_settings,
    create_repository_factory,
    dispose_cached_engines,
)
from mdi_api.bootstrap.repository_factory import (
    create_repository_factory as canonical_create_repository_factory,
)
from mdi_api.infrastructure.persistence.engine import (
    create_engine_from_settings as canonical_create_engine_from_settings,
)
from mdi_api.infrastructure.persistence.engine import (
    dispose_cached_engines as canonical_dispose_cached_engines,
)


def test_legacy_database_exports_are_canonical_symbols() -> None:
    assert create_engine_from_settings is canonical_create_engine_from_settings
    assert dispose_cached_engines is canonical_dispose_cached_engines
    assert create_repository_factory is canonical_create_repository_factory


def test_repeated_request_engine_creation_reuses_one_pool_and_returns_connections(tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'pool-lifecycle.db').as_posix()}"
    settings = ApiSettings(database_url=database_url)
    try:
        engines = []
        for _ in range(8):
            engine = create_engine_from_settings(settings)
            engines.append(engine)
            with engine.connect() as connection:
                connection.exec_driver_sql("SELECT 1")

        assert len({id(engine) for engine in engines}) == 1
        pool = engines[0].pool
        checked_out = getattr(pool, "checkedout", None)
        if callable(checked_out):
            assert checked_out() == 0
    finally:
        dispose_cached_engines()


@pytest.mark.integration
def test_live_postgres_pool_pressure_reuses_engine_and_returns_all_connections():
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 for the PostgreSQL pool campaign")
    database_url = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url or "postgres" not in database_url:
        pytest.skip("No PostgreSQL test URL configured")

    settings = ApiSettings(database_url=database_url)
    dispose_cached_engines()
    try:
        engine = create_engine_from_settings(settings)
        factory = create_repository_factory(settings)

        def probe(_: int) -> None:
            for _ in range(40):
                with factory.session() as session:
                    session.connection.execute(text("SELECT 1")).scalar_one()

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(probe, range(8)))

        assert create_engine_from_settings(settings) is engine
        checked_out = getattr(engine.pool, "checkedout", None)
        if callable(checked_out):
            assert checked_out() == 0
        with engine.connect() as connection:
            idle_in_transaction = connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                      AND state = 'idle in transaction'
                    """
                )
            ).scalar_one()
        assert int(idle_in_transaction) == 0
    finally:
        dispose_cached_engines()
