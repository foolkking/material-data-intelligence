from __future__ import annotations

from sqlalchemy import create_engine, event

from mdi_api.db import metadata
from mdi_api.repositories import SqlAlchemyRepositoryBundle
from mdi_api.workspaces import WorkspaceProjectionService


def _list_query_count(workspace_count: int) -> tuple[int, int, int]:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    repositories = SqlAlchemyRepositoryBundle.create(engine)
    repositories.projects.save(
        {"projectId": "project_perf", "name": "Performance", "createdBy": "user_local"}
    )
    repositories.datasets.save(
        {
            "datasetId": "dataset_perf",
            "projectId": "project_perf",
            "name": "Performance source",
            "createdBy": "user_local",
        }
    )
    service = WorkspaceProjectionService(repositories)
    for index in range(workspace_count):
        job_id = f"job_perf_{index}"
        repositories.jobs.save(
            {
                "id": job_id,
                "projectId": "project_perf",
                "datasetId": "dataset_perf",
                "kind": "analysis",
                "status": "completed",
                "createdBy": "user_local",
            }
        )
        service.project_job(source_job_id=job_id, created_by="user_local")

    query_count = 0

    def count_query(*_args: object, **_kwargs: object) -> None:
        nonlocal query_count
        query_count += 1

    event.listen(engine, "before_cursor_execute", count_query)
    result = service.list_project_workspaces(
        project_id="project_perf", limit=100, cursor=None
    )
    event.remove(engine, "before_cursor_execute", count_query)
    serialized_bytes = len(str(result).encode("utf-8"))
    engine.dispose()
    return query_count, len(result["items"]), serialized_bytes


def test_workspace_project_list_is_constant_query_metadata_projection() -> None:
    one_queries, one_items, one_bytes = _list_query_count(1)
    five_queries, five_items, five_bytes = _list_query_count(5)

    assert one_items == 1 and five_items == 5
    assert one_queries == five_queries == 2
    assert one_bytes < 524_288 and five_bytes < 524_288
