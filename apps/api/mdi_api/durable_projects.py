from __future__ import annotations

from typing import Any

from mdi_api.config import ApiSettings, load_settings
from mdi_api.database import create_repository_factory


def persist_runtime_project(
    runtime: Any,
    project_id: str,
    *,
    settings: ApiSettings | None = None,
    repository_factory: Any | None = None,
) -> dict[str, Any] | None:
    active_settings = settings or load_settings()
    if active_settings.runtime_backend != "postgresql":
        return None

    project = runtime.projects[project_id]
    factory = repository_factory or create_repository_factory(active_settings)
    with factory.session() as session:
        persisted = session.repositories.projects.save(
            {
                **project.summary(),
                "createdBy": "user_local",
                "organizationId": "org_local",
            }
        )
    return _runtime_project_summary(project.summary(), persisted)


def list_runtime_projects(
    runtime: Any,
    *,
    settings: ApiSettings | None = None,
    repository_factory: Any | None = None,
) -> list[dict[str, Any]]:
    active_settings = settings or load_settings()
    if active_settings.runtime_backend != "postgresql":
        return runtime.list_projects()

    factory = repository_factory or create_repository_factory(active_settings)
    return [_durable_project_summary(project) for project in factory.create_repositories().projects.list()]


def hydrate_runtime_project(
    runtime: Any,
    project_id: str,
    *,
    settings: ApiSettings | None = None,
    repository_factory: Any | None = None,
) -> dict[str, Any]:
    """Restore an existing durable project into the process-local runtime."""

    if project_id in runtime.projects:
        return runtime.projects[project_id].summary()

    active_settings = settings or load_settings()
    if active_settings.runtime_backend != "postgresql":
        raise LookupError(f"Unknown project_id: {project_id}")

    factory = repository_factory or create_repository_factory(active_settings)
    project = factory.create_repositories().projects.get(project_id)
    return runtime.ensure_project(project_id, name=str(project["name"]))


def _runtime_project_summary(runtime_project: dict[str, Any], persisted: dict[str, Any]) -> dict[str, Any]:
    return {
        **runtime_project,
        "id": persisted["id"],
        "projectId": persisted["projectId"],
        "name": persisted["name"],
        "createdAt": persisted["createdAt"],
    }


def _durable_project_summary(project: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": project["id"],
        "projectId": project["projectId"],
        "name": project["name"],
        "role": "owner",
        "status": "created",
        "createdAt": project["createdAt"],
    }
