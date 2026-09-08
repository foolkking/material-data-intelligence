"""Compatibility facade for database lifecycle and repository composition.

Canonical implementations live in infrastructure/bootstrap modules. This
module remains stable because it is a public import and patch target.
"""

from mdi_api.bootstrap import repository_factory as _repository_factory
from mdi_api.infrastructure.persistence import engine as _engine
from mdi_api.unit_of_work import RepositoryFactory

_ENGINE_CACHE = _engine._ENGINE_CACHE
_ENGINE_CACHE_LOCK = _engine._ENGINE_CACHE_LOCK
_cache_key = _engine._cache_key
_configure_sqlite_pragma = _engine._configure_sqlite_pragma
_engine_kwargs = _engine._engine_kwargs
create_engine_from_settings = _engine.create_engine_from_settings
dispose_cached_engines = _engine.dispose_cached_engines
create_repository_factory = _repository_factory.create_repository_factory

__all__ = [
    "RepositoryFactory",
    "create_engine_from_settings",
    "dispose_cached_engines",
    "create_repository_factory",
]
