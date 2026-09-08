from __future__ import annotations

from typing import Any

from mdi_api.config import ApiSettings
from mdi_api.infrastructure.persistence.engine import create_engine_from_settings
from mdi_api.unit_of_work import RepositoryFactory


def create_repository_factory(settings: ApiSettings | None = None, **kwargs: Any) -> RepositoryFactory:
    """Compose repositories from the canonical infrastructure engine lifecycle."""

    return RepositoryFactory(create_engine_from_settings(settings, **kwargs))
