from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Event
from uuid import uuid4

import pytest
from sqlalchemy import update

from mdi_api.application.research.ports import ResearchActorContext
from mdi_api.agent2_errors import ConcurrentTurnModification, InvalidResearchTurnTransition
from mdi_api.db import research_turns
from mdi_api.interpretation.client import FakeStructuredInterpreterClient
from mdi_api.interpretation.service import ScientificInterpretationService
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from tests.test_agent2_execution import CaptureQueue, _factory
from tests.test_agent2_interpretation import _bundle, _output
from tests.test_research_execution_loss_recovery import isolated_postgres_execution


@pytest.mark.parametrize("provider_outcome", ["success", "failure", "invalid"])
@pytest.mark.parametrize("has_job", [False, True])
def test_cancel_interpretation_preserves_science_and_fences_late_provider(provider_outcome, has_job):
    engine, factory, turn_id = _factory()
    job_id = None
    if has_job:
        job_id = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id).job_id
        with factory.unit_of_work() as unit:
            unit.repositories.jobs.set_status(job_id, "running")
            unit.repositories.jobs.set_status(job_id, "completed")
    bundle = _bundle().model_copy(update={"research_turn_id": turn_id, "source_object_refs": []})
    with engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status="RESULT_READY"))
    with factory.unit_of_work() as unit:
        snapshot = unit.agent2.scientific_result_snapshots.add({
            "id": uuid4(), "project_id": "project", "research_turn_id": turn_id,
            "job_id": job_id, "schema_version": bundle.schema_version,
            "projection_version": bundle.projection_version,
            "execution_status": bundle.execution_status.value,
            "relevance_status": bundle.relevance_status.value,
            "source_fingerprint": "cancel-preserves-snapshot", "bundle_json": bundle.model_dump(mode="json"),
        })
    started, release = Event(), Event()

    class GatedClient(FakeStructuredInterpreterClient):
        invocations = 0

        async def generate_structured(self, **kwargs):
            self.invocations += 1
            started.set()
            assert release.wait(10), "test provider was not released"
            if provider_outcome == "failure":
                raise TimeoutError("provider finished after cancellation")
            return await super().generate_structured(**kwargs)

    client = GatedClient({} if provider_outcome == "invalid" else _output())
    service = ScientificInterpretationService(factory, client=client)
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            try:
                work = pool.submit(service.process_turn, turn_id)
                assert started.wait(10)
                canceled = ResearchTurnService(factory).cancel_turn(turn_id, ResearchActorContext("owner"))
                assert canceled["status"] == "CANCELED"
                assert canceled["completed_at"] is not None
                release.set()
                error = work.exception(timeout=10)
                assert error is not None
                assert client.invocations == 1  # No schema repair after cancellation.
                if provider_outcome != "failure":
                    assert getattr(error, "code", None) == "INTERPRETATION_CLAIM_LOST"
                with factory.session() as session:
                    turn = session.agent2.research_turns.get(turn_id)
                    assert turn["status"] == "CANCELED"
                    assert turn["row_version"] == canceled["row_version"]
                    assert turn["assistant_final_message_id"] is None
                    assert turn["error_code"] is None
                    assert session.agent2.interpretations.get_for_turn(turn_id) is None
                    assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
                    if job_id:
                        assert session.repositories.jobs.get(job_id)["status"] == "completed"
                    events = session.agent2.research_turn_events.list_for_turn(turn_id)
                    assert sum(e["event_type"] == "TURN_CANCELED" for e in events) == 1
                    assert not any(e["event_type"] in {"TURN_FAILED", "TURN_COMPLETED", "INTERPRETATION_READY", "CANCELLATION_REQUESTED"} for e in events)
                with pytest.raises(InvalidResearchTurnTransition):
                    ResearchTurnService(factory).cancel_turn(turn_id, ResearchActorContext("owner"))
            finally:
                release.set()
    finally:
        engine.dispose()


def test_interpretation_completion_winning_cancel_race_is_not_overwritten(monkeypatch):
    engine, factory, turn_id = _factory()
    service = ResearchTurnService(factory)
    original = service.transition
    with engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status="INTERPRETING"))

    def complete_before_cancel(**kwargs):
        with engine.begin() as connection:
            connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status="COMPLETED", row_version=research_turns.c.row_version + 1))
        return original(**kwargs)

    monkeypatch.setattr(service, "transition", complete_before_cancel)
    try:
        with pytest.raises(ConcurrentTurnModification):
            service.cancel_turn(turn_id, ResearchActorContext("owner"))
        with factory.session() as session:
            assert session.agent2.research_turns.get(turn_id)["status"] == "COMPLETED"
            assert not session.agent2.research_turn_events.list_for_turn(turn_id)
    finally:
        engine.dispose()


@pytest.mark.parametrize("old_outcome", ["success", "failure"])
@pytest.mark.parametrize("repository_backend", ["sqlite", pytest.param("postgres", marks=pytest.mark.integration)])
def test_reclaimed_interpretation_rejects_the_previous_workers_late_outcome(old_outcome, repository_backend, request):
    if repository_backend == "postgres":
        factory, turn_id, _job_id, _lease = request.getfixturevalue("isolated_postgres_execution")
        engine = factory.engine
    else:
        engine, factory, turn_id = _factory()
    bundle = _bundle().model_copy(update={
        "research_turn_id": turn_id, "source_object_refs": [],
    })
    with engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status="RESULT_READY"))
    with factory.unit_of_work() as unit:
        snapshot = unit.agent2.scientific_result_snapshots.add({
            "id": uuid4(), "project_id": "project", "research_turn_id": turn_id,
            "job_id": None, "schema_version": bundle.schema_version,
            "projection_version": bundle.projection_version,
            "execution_status": bundle.execution_status.value,
            "relevance_status": bundle.relevance_status.value,
            "source_fingerprint": "owned-snapshot", "bundle_json": bundle.model_dump(mode="json"),
        })
    old_started, new_started, release_old, release_new = (Event() for _ in range(4))

    class GatedClient(FakeStructuredInterpreterClient):
        def __init__(self, title, started, release, fail=False):
            super().__init__({**_output(), "title": title})
            self.started, self.release, self.fail = started, release, fail

        async def generate_structured(self, **kwargs):
            self.started.set()
            assert self.release.wait(10), "test provider was not released"
            if self.fail:
                raise RuntimeError("old provider failed after another worker reclaimed the Turn")
            return await super().generate_structured(**kwargs)

    old = ScientificInterpretationService(factory, client=GatedClient("过期解释", old_started, release_old, old_outcome == "failure"))
    new = ScientificInterpretationService(factory, client=GatedClient("恢复后的解释", new_started, release_new))
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            try:
                old_work = pool.submit(old.process_turn, turn_id)
                assert old_started.wait(10)
                # Advance only this fixture's inactivity clock to exercise the
                # real stale-claim path without slowing the suite by 15 minutes.
                with engine.begin() as connection:
                    connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
                        updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
                    ))
                new_work = pool.submit(new.process_turn, turn_id)
                assert new_started.wait(10)
                with factory.session() as session:
                    new_version = session.agent2.research_turns.get(turn_id)["row_version"]
                release_old.set()
                old_error = old_work.exception(timeout=10)
                with factory.session() as session:
                    turn = session.agent2.research_turns.get(turn_id)
                    assert turn["status"] == "INTERPRETING"
                    assert turn["row_version"] == new_version
                    assert turn["assistant_final_message_id"] is None
                    assert session.agent2.interpretations.get_for_turn(turn_id) is None
                    assert not any(e["event_type"] == "TURN_FAILED" for e in session.agent2.research_turn_events.list_for_turn(turn_id))
                assert old_error is not None
                if old_outcome == "success":
                    assert getattr(old_error, "code", None) == "INTERPRETATION_CLAIM_LOST"
                release_new.set()
                current = new_work.result(timeout=10)
                assert current["output_json"]["interpretation"]["title"] == "恢复后的解释"
                with factory.session() as session:
                    assert session.agent2.research_turns.get(turn_id)["status"] == "COMPLETED"
                    assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
                    events = session.agent2.research_turn_events.list_for_turn(turn_id)
                    assert sum(e["event_type"] == "TURN_COMPLETED" for e in events) == 1
            finally:
                release_old.set()
                release_new.set()
    finally:
        if repository_backend == "sqlite":
            engine.dispose()
