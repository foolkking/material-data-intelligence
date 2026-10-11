from __future__ import annotations

import json
from copy import deepcopy
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event, insert, select, update

from mdi_api.db import analysis_plans, datasets, messages, metadata, research_turns, sessions
from mdi_api.repositories import InMemoryRepositoryBundle, SqlAlchemyRepositoryBundle
from mdi_api.workspaces import WorkspaceProjectionService

from tests.test_project_history import _multi_material_history


def _seed_sources(repos, job_count=1):
    source = _multi_material_history()
    repos.projects.save(source.projects.records[0])
    for item, name in zip(source.datasets.records, ["Si 晶体", "Cu 晶体", "NaCl 晶体"]):
        repos.datasets.save({**item, "name": name, "metadata": {"storageKey": "internal-only"}})
    repos.analysis_plans.save_plan(source.analysis_plans.records[0])
    for index in range(job_count):
        repos.jobs.save({**source.jobs.records[0], "jobId": f"job_multi_{index}", "status": "completed" if index == 0 else "failed"})


def _feed(repos, limit=100):
    return WorkspaceProjectionService(repos).list_task_feed(
        projects=({"projectId": "project_1", "name": "Three materials"},), limit=limit, cursor=None,
    )


@pytest.mark.parametrize("backend", ["memory", "sqlite"])
def test_task_views_keep_every_verified_source_for_success_and_failure_without_writing(backend):
    engine = create_engine("sqlite:///:memory:") if backend == "sqlite" else None
    if engine is not None:
        metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine) if engine is not None else InMemoryRepositoryBundle.create()
    try:
        _seed_sources(repos, job_count=2)
        before = deepcopy((repos.jobs.list_by_project("project_1"), repos.analysis_plans.get_plan("plan_multi")))
        views = [_feed(repos), WorkspaceProjectionService(repos).list_analysis_jobs(project_id="project_1", limit=10, cursor=None)]
        expected = [{"datasetId": f"dataset_{key}", "name": name} for key, name in zip("abc", ["Si 晶体", "Cu 晶体", "NaCl 晶体"])]
        for view in views:
            assert len(view["items"]) == 2
            assert {item["jobStatus"] for item in view["items"]} == {"completed", "failed"}
            assert all(item["sourceDatasets"] == expected and item["datasetId"] == "dataset_a" for item in view["items"])
            assert "internal-only" not in json.dumps(view)
        assert before == (repos.jobs.list_by_project("project_1"), repos.analysis_plans.get_plan("plan_multi"))
        assert repos.workspaces.list_by_project("project_1") == []
    finally:
        if engine is not None:
            engine.dispose()


@pytest.mark.parametrize("corruption", ["hash", "project", "profile", "foreign_source", "malformed_plan"])
def test_task_feed_does_not_fall_back_to_the_routing_dataset_when_multi_source_identity_is_unverified(corruption):
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    try:
        _seed_sources(repos)
        with engine.begin() as connection:
            if corruption == "foreign_source":
                connection.execute(update(datasets).where(datasets.c.id == "dataset_b").values(project_id="other_project"))
            else:
                change = {"hash": {"plan_hash": "0" * 64}, "project": {"project_id": "other_project"},
                          "profile": {"profile_id": "another_profile"}, "malformed_plan": {"analysis_plan_json": {"schemaVersion": "0.3"}}}[corruption]
                connection.execute(update(analysis_plans).where(analysis_plans.c.id == "plan_multi").values(**change))
        item = _feed(repos)["items"][0]
        assert item["sourceDatasets"] == []
        assert item["datasetId"] == "dataset_a"
        assert item["jobId"] == "job_multi_0"
    finally:
        engine.dispose()


@pytest.mark.parametrize("job_count", [1, 5])
def test_multi_source_task_names_are_loaded_once_for_the_page(job_count):
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    try:
        _seed_sources(repos, job_count=job_count)
        queries = []

        def record_query(_connection, _cursor, statement, *_args):
            queries.append(statement)

        event.listen(engine, "before_cursor_execute", record_query)
        view = _feed(repos)
        event.remove(engine, "before_cursor_execute", record_query)
        assert len(view["items"]) == job_count
        assert all(len(item["sourceDatasets"]) == 3 for item in view["items"])
        assert len(queries) == 3  # Jobs, page metadata, one batch of dataset labels.
    finally:
        engine.dispose()


@pytest.mark.parametrize("turn_project", ["project_1", "another_project"])
def test_task_views_use_the_saved_turn_session_only_within_the_owning_project(turn_project):
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    try:
        _seed_sources(repos)
        turn_id = uuid4()
        with engine.begin() as connection:
            connection.execute(insert(sessions), {
                "id": "session_owned", "project_id": turn_project, "dataset_id": "dataset_a",
                "mode": "project", "status": "active", "created_by": "user_local",
            })
            connection.execute(insert(messages), {
                "id": "message_owned", "session_id": "session_owned", "role": "user",
                "content_summary": "Compare three materials", "payload_json": {},
            })
            connection.execute(insert(research_turns), {
                "id": turn_id, "project_id": turn_project, "research_session_id": "session_owned",
                "sequence_no": 1, "user_message_id": "message_owned", "action_type": "ANALYZE",
                "status": "COMPLETED", "job_id": "job_multi_0",
            })
            before = dict(connection.execute(select(research_turns)).mappings().one())
        service = WorkspaceProjectionService(repos)
        for view in [_feed(repos), service.list_analysis_jobs(project_id="project_1", limit=100, cursor=None)]:
            item = view["items"][0]
            expected = turn_project == "project_1"
            assert item["researchTurnId"] == (str(turn_id) if expected else None)
            assert item["researchSessionId"] == ("session_owned" if expected else None)
            if not expected:
                assert item.get("researchQuestion") is None
        with engine.connect() as connection:
            assert dict(connection.execute(select(research_turns)).mappings().one()) == before
    finally:
        engine.dispose()


@pytest.mark.parametrize("mismatch", [None, "job_id", "project_id"])
def test_fallback_task_views_preserve_the_exact_turn_owner(mismatch):
    repos = InMemoryRepositoryBundle.create()
    _seed_sources(repos)
    turn = {
        "id": str(uuid4()), "job_id": "job_multi_0", "project_id": "project_1",
        "research_session_id": "session_owned",
    }
    if mismatch:
        turn[mismatch] = "another_record"
    repos.get_research_turn_for_job = lambda _job_id: turn
    for view in [_feed(repos), WorkspaceProjectionService(repos).list_analysis_jobs(project_id="project_1", limit=100, cursor=None)]:
        item = view["items"][0]
        assert item["researchTurnId"] == (turn["id"] if mismatch is None else None)
        assert item["researchSessionId"] == ("session_owned" if mismatch is None else None)
