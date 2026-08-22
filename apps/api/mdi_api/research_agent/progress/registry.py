from __future__ import annotations

from typing import Any, Callable, Protocol


class ScientificProgressProjectorRegistry(Protocol):
    def register(self, projector_id: str, projector: Callable[..., Any]) -> None: ...
    def require(self, projector_id: str) -> Callable[..., Any]: ...
    def contains(self, projector_id: str) -> bool: ...


class InMemoryScientificProgressProjectorRegistry:
    def __init__(self) -> None:
        self._projectors: dict[str, Callable[..., Any]] = {}

    def register(self, projector_id: str, projector: Callable[..., Any]) -> None:
        if projector_id in self._projectors:
            raise ValueError(f"Duplicate progress projector: {projector_id}")
        self._projectors[projector_id] = projector

    def require(self, projector_id: str) -> Callable[..., Any]:
        try:
            return self._projectors[projector_id]
        except KeyError as exc:
            raise KeyError(f"Unknown progress projector: {projector_id}") from exc

    def contains(self, projector_id: str) -> bool:
        return projector_id in self._projectors
