from __future__ import annotations

from copy import deepcopy

import pytest
from sqlalchemy import insert

from mdi_api.db import artifacts
from mdi_api.infrastructure.scientific_results.execution_records import read_snapshot_execution_records
from tests.test_agent2_results import _persisted_projection


@pytest.fixture
def saved_execution(monkeypatch):
    factory, turn_id, job_id, service = _persisted_projection()
    monkeypatch.setattr(service, "_enqueue_interpretation", lambda _: None)
    snapshot = service.project_turn(turn_id)
    with factory.engine.begin() as connection:
        connection.execute(insert(artifacts), {
            "id": "unrecorded-output", "project_id": "project", "dataset_id": "dataset", "job_id": job_id,
            "tool_call_id": "call-output", "type": "table_json", "name": "unrecorded.json", "version": "1",
            "storage_key": "test/unrecorded.json", "size_bytes": 42, "content_type": "application/json",
            "content_hash": "unrecorded",
        })
    yield factory, snapshot
    factory.engine.dispose()


def test_old_snapshot_resolves_only_exact_artifact_producers(saved_execution):
    factory, snapshot = saved_execution
    historical = deepcopy(snapshot)
    historical["bundle_json"]["provenance"] = {}
    with factory.engine.connect() as connection:
        outputs, calls = read_snapshot_execution_records(connection, historical)
    assert [row["id"] for row in outputs] == ["saved-output"]
    assert [row["id"] for row in calls] == ["call-output"]


def test_missing_inventory_does_not_expand_to_the_job(saved_execution):
    factory, snapshot = saved_execution
    empty = {**snapshot, "bundle_json": {"provenance": {}}}
    with factory.engine.connect() as connection:
        assert read_snapshot_execution_records(connection, empty) == ([], [])


@pytest.mark.parametrize("field", ["job_id", "project_id", "research_turn_id"])
def test_conflicting_snapshot_scope_fails_closed(saved_execution, field):
    factory, snapshot = saved_execution
    altered = {**snapshot, field: "foreign"}
    with factory.engine.connect() as connection, pytest.raises(ValueError, match="scope is inconsistent"):
        read_snapshot_execution_records(connection, altered)


@pytest.mark.parametrize("foreign_field", ["project_id", "job_id"])
def test_referenced_foreign_artifact_is_not_exposed(saved_execution, foreign_field):
    factory, snapshot = saved_execution
    record = {
        "id": "foreign-output", "project_id": snapshot["project_id"], "dataset_id": "dataset",
        "job_id": snapshot["job_id"], "type": "table_json", "name": "foreign.json", "version": "1",
        "storage_key": "test/foreign.json", "size_bytes": 42, "content_type": "application/json", "content_hash": "foreign",
        foreign_field: "foreign",
    }
    with factory.engine.begin() as connection:
        connection.execute(insert(artifacts), record)
    altered = deepcopy(snapshot)
    altered["bundle_json"]["provenance"]["artifact_ids"].append("foreign-output")
    with factory.engine.connect() as connection:
        outputs, calls = read_snapshot_execution_records(connection, altered)
    assert [row["id"] for row in outputs] == ["saved-output"]
    assert [row["id"] for row in calls] == ["call-output"]


def test_execution_record_reads_leave_the_result_and_summary_unchanged(saved_execution):
    factory, snapshot = saved_execution
    with factory.session() as session:
        original = session.agent2.research_execution_summaries.get_for_turn(snapshot["research_turn_id"])
        read_snapshot_execution_records(session.connection, snapshot)
        assert session.agent2.research_execution_summaries.get_for_turn(snapshot["research_turn_id"]) == original
        assert session.agent2.scientific_result_snapshots.get(snapshot["id"]) == snapshot
