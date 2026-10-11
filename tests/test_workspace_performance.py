from __future__ import annotations

from uuid import uuid4

from sqlalchemy import create_engine, event, insert

from mdi_api.db import messages, metadata, research_turns, sessions
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


def _task_feed_query_count(job_count: int) -> tuple[int, int]:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    repositories = SqlAlchemyRepositoryBundle.create(engine)
    repositories.projects.save(
        {"projectId": "project_feed", "name": "Task feed", "createdBy": "user_local"}
    )
    repositories.datasets.save(
        {
            "datasetId": "dataset_feed",
            "projectId": "project_feed",
            "name": "Task feed source",
            "createdBy": "user_local",
        }
    )
    for index in range(job_count):
        repositories.jobs.save(
            {
                "id": f"job_feed_{index}",
                "projectId": "project_feed",
                "datasetId": "dataset_feed",
                "kind": "analysis",
                "status": "completed",
                "createdBy": "user_local",
            }
        )

    query_count = 0

    def count_query(*_args: object, **_kwargs: object) -> None:
        nonlocal query_count
        query_count += 1

    event.listen(engine, "before_cursor_execute", count_query)
    result = WorkspaceProjectionService(repositories).list_task_feed(
        projects=(
            {
                "id": "project_feed",
                "projectId": "project_feed",
                "name": "Task feed",
                "role": "owner",
                "status": "active",
            },
        ),
        limit=100,
        cursor=None,
    )
    event.remove(engine, "before_cursor_execute", count_query)
    engine.dispose()
    return query_count, len(result["items"])


def test_task_feed_uses_one_bounded_sql_projection_for_page_items() -> None:
    one_queries, one_items = _task_feed_query_count(1)
    five_queries, five_items = _task_feed_query_count(5)

    assert one_items == 1 and five_items == 5
    assert one_queries == five_queries == 2


def test_task_feed_projects_the_exact_turn_question_as_bounded_display_metadata() -> None:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    repositories = SqlAlchemyRepositoryBundle.create(engine)
    repositories.projects.save(
        {"projectId": "project_question", "name": "Question", "createdBy": "user_local"}
    )
    repositories.datasets.save(
        {
            "datasetId": "dataset_question",
            "projectId": "project_question",
            "name": "Question source",
            "createdBy": "user_local",
        }
    )
    repositories.jobs.save(
        {
            "id": "job_question",
            "projectId": "project_question",
            "datasetId": "dataset_question",
            "kind": "analysis",
            "status": "completed",
            "createdBy": "user_local",
        }
    )
    turn_id = uuid4()
    with engine.begin() as connection:
        connection.execute(
            insert(sessions),
            {
                "id": "session_question",
                "project_id": "project_question",
                "dataset_id": "dataset_question",
                "mode": "project",
                "status": "active",
                "created_by": "user_local",
            },
        )
        connection.execute(
            insert(messages),
            {
                "id": "message_question",
                "session_id": "session_question",
                "role": "user",
                "content_summary": "  Compare CrystalNN   and VoronoiNN for the selected structure.  ",
                "payload_json": {},
            },
        )
        connection.execute(
            insert(research_turns),
            {
                "id": turn_id,
                "project_id": "project_question",
                "research_session_id": "session_question",
                "sequence_no": 1,
                "user_message_id": "message_question",
                "action_type": "ANALYZE",
                "status": "COMPLETED",
                "job_id": "job_question",
            },
        )

    result = WorkspaceProjectionService(repositories).list_task_feed(
        projects=(
            {
                "id": "project_question",
                "projectId": "project_question",
                "name": "Question",
                "role": "owner",
                "status": "active",
            },
        ),
        limit=100,
        cursor=None,
    )

    assert result["items"][0]["researchTurnId"] == str(turn_id)
    assert result["items"][0]["researchSessionId"] == "session_question"
    assert result["items"][0]["researchQuestion"] == (
        "Compare CrystalNN and VoronoiNN for the selected structure."
    )
    engine.dispose()
