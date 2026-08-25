from __future__ import annotations

from pathlib import Path

from mdi_api.config import ApiSettings
from mdi_api.database import create_engine_from_settings, dispose_cached_engines


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
