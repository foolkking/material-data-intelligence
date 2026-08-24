"""FastAPI application boundary for Material Data Intelligence."""

from typing import Any

__all__ = ["create_app"]


def __getattr__(name: str) -> Any:
    if name == "create_app":
        from .main import create_app

        return create_app
    if name == "research_agent_worker":
        from importlib import import_module

        return import_module(f"{__name__}.research_agent_worker")
    raise AttributeError(name)
