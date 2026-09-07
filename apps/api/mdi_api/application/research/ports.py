from __future__ import annotations

from dataclasses import dataclass
from types import TracebackType
from typing import Any, Protocol


class ProjectAccessNotFound(LookupError):
    """The requested project does not exist in an authorized persistence view."""


class ProjectAccessDenied(PermissionError):
    """The actor is not permitted to perform the requested project operation."""


class ResearchActor(Protocol):
    """Minimum actor identity consumed by Research authorization."""

    id: str


@dataclass(frozen=True, slots=True)
class ResearchActorContext:
    """Transport-neutral Research actor projected by HTTP or another transport."""

    id: str


class ResearchPersistenceContext(Protocol):
    """Repository/UoW surface consumed by Research application services."""

    connection: Any
    repositories: Any
    agent2: Any

    def __enter__(self) -> "ResearchPersistenceContext": ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool: ...


class ResearchProjectAccessPort(Protocol):
    """Authorize one actor against one project without transport dependencies."""

    def require(
        self,
        connection: Any,
        project_id: str,
        actor: ResearchActor,
        *,
        write: bool = False,
    ) -> dict[str, Any]: ...


class ResearchRepositoryFactoryPort(Protocol):
    """Stable persistence boundary consumed by Research application code."""

    project_access: ResearchProjectAccessPort

    def session(self) -> ResearchPersistenceContext: ...

    def unit_of_work(self) -> ResearchPersistenceContext: ...
