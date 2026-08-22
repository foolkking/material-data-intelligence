from __future__ import annotations

from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory


def current_alembic_head() -> str:
    """Resolve the repository head instead of freezing tests to a revision."""
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    return ScriptDirectory.from_config(config).get_current_head()
