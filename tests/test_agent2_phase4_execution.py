from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.pool import StaticPool

from mdi_api.db import (
    analysis_plans, artifacts, data_profiles, datasets, jobs, metadata, messages, organizations,
    projects, research_capability_plans, research_capability_resolutions, research_context_snapshots, research_execution_summaries, research_turn_events, research_turns, scientific_result_snapshots, sessions, users,
)
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.execution.errors import ExecutionQueuePublishFailed
from mdi_api.research_agent.execution.reconciler import ResearchExecutionReconciler
from mdi_api.research_agent.execution.schemas import ExecutionOutcome, ExecutionStepStatus
from mdi_api.research_agent.execution.supervisor import ExecutionOutcomeClassifier, ResearchExecutionSupervisor
from mdi_api.research_agent.schemas import ResearchTurnStatus
from mdi_api.research_agent.turns.state_machine import ensure_transition
from mdi_api.agent2_errors import InvalidResearchTurnTransition
from mdi_api.unit_of_work import RepositoryFactory
from mdi_api.repositories import compute_plan_hash
from mdi_schemas import AnalysisPlanV02
from mdi_schemas.dependency_planning import compute_dependency_graph_hash


class CaptureQueue:
    def __init__(self) -> None:
        self.ids: list[str] = []

    def enqueue_job(self, job_id: str) -> dict[str, object]:
        self.ids.append(job_id)
        return {"job_id": job_id, "enqueued": True, "backend": "test", "message": "queued"}


class FailOnceQueue(CaptureQueue):
    def __init__(self) -> None:
        super().__init__()
        self.failed = False

    def enqueue_job(self, job_id: str) -> dict[str, object]:
        self.ids.append(job_id)
        if not self.failed:
            self.failed = True
            raise RuntimeError("queue unavailable")
        return {"job_id": job_id, "enqueued": True, "backend": "test", "message": "recovered"}


def _factory():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    plan_payload = {"schemaVersion": "0.2", "goal": "Run test", "datasetId": "dataset", "profileId": "profile", "toolRegistryVersion": "test", "graphHash": compute_dependency_graph_hash([]), "assumptions": [], "warnings": [], "steps": [{"stepId": "step_1", "purpose": "生成理论 XRD", "reason": "test", "toolId": "structure.xrd", "inputRefs": [], "params": {}, "output": {}}], "dependencyBindings": [], "expectedArtifacts": [{"name": "step_1.theoretical_xrd", "type": "table_json", "fromStepId": "step_1"}]}
    with engine.begin() as connection:
        connection.execute(insert(users), {"id": "owner", "email": "owner@local.invalid", "display_name": "Owner", "is_active": True})
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), {"id": "project", "organization_id": "org", "name": "Project", "created_by": "owner"})
        connection.execute(insert(datasets), {"id": "dataset", "project_id": "project", "name": "Dataset", "status": "profile_ready", "metadata_json": {}, "created_by": "owner"})
        connection.execute(insert(data_profiles), {"id": "profile", "dataset_id": "dataset", "version": "2.0", "profile_json": {"id": "profile", "datasetId": "dataset"}})
        connection.execute(insert(sessions), {"id": "session", "project_id": "project", "dataset_id": "dataset", "mode": "project", "status": "active", "created_by": "owner"})
        connection.execute(insert(messages), {"id": "message", "session_id": "session", "role": "user", "content_summary": "Run the analysis", "payload_json": {}, "created_at": now})
        connection.execute(insert(analysis_plans), {"id": "plan_phase4", "project_id": "project", "dataset_id": "dataset", "profile_id": "profile", "plan_source": "agent2_test", "analysis_plan_json": plan_payload, "plan_hash": compute_plan_hash(AnalysisPlanV02.model_validate(plan_payload)), "validation_status": "validated", "created_by": "owner"})
        turn_id = uuid4()
        snapshot_id, resolution_id = uuid4(), uuid4()
        connection.execute(insert(research_turns), {"id": turn_id, "project_id": "project", "research_session_id": "session", "sequence_no": 1, "user_message_id": "message", "action_type": "ANALYZE", "status": "PLAN_READY", "analysis_plan_id": "plan_phase4", "row_version": 1, "created_at": now, "updated_at": now})
        connection.execute(insert(research_context_snapshots), {"id": snapshot_id, "project_id": "project", "research_session_id": "session", "research_turn_id": turn_id, "snapshot_schema_version": "2.0", "active_scope_refs_json": [], "selection_refs_json": [], "resolved_references_json": [], "referenced_result_refs_json": [], "relevant_finding_refs_json": [], "effective_constraints_json": [], "research_goal": "Run test", "unresolved_questions_json": [], "context_fingerprint": "f" * 64, "compiler_version": "test/1.0", "created_at": now})
        resolution_json = {
            "contract_version": "1.0", "research_turn_id": str(turn_id), "objective": "Generate theoretical XRD",
            "requirement_ids": ["diffraction.generate_theoretical_pattern"],
            "candidates": [{
                "capability_id": "diffraction.theoretical_xrd", "capability_version": "1.0",
                "eligibility": "ELIGIBLE", "satisfies_requirement_ids": ["diffraction.generate_theoretical_pattern"],
                "bound_source_inputs": {}, "bound_source_ref_keys": {}, "reusable_result_bindings": {},
                "missing_input_slots": [], "possible_producers": {}, "reason_codes": [], "limitations": [],
                "planning_priority": 100,
            }],
            "unsatisfied_required_requirement_ids": [], "optional_requirement_ids_not_covered": [],
            "registry_fingerprint": "a" * 64, "resolver_version": "test/1.0",
        }
        capability_plan_json = {
            "contract_version": "1.0", "objective": "Generate theoretical XRD",
            "steps": [{
                "step_id": "step_1", "capability_ref_key": "cap_1",
                "satisfies_requirement_ids": ["diffraction.generate_theoretical_pattern"],
                "input_bindings": {}, "parameters": {},
                "expected_outputs": [{"slot_name": "theoretical_xrd", "result_type": "diffraction.xrd.theoretical", "scientific_object_type": "diffraction.xrd.theoretical"}],
            }],
            "omitted_optional_requirement_ids": [], "planner_summary": None,
        }
        connection.execute(insert(research_capability_resolutions), {"id": resolution_id, "research_turn_id": turn_id, "contract_version": "1.0", "requirement_snapshot_json": {}, "resolution_json": resolution_json, "registry_fingerprint": "a" * 64, "resolver_version": "test/1.0", "created_at": now})
        connection.execute(insert(research_capability_plans), {"id": uuid4(), "research_turn_id": turn_id, "capability_resolution_id": resolution_id, "contract_version": "1.0", "plan_json": capability_plan_json, "input_fingerprint": "p" * 64, "planner_mode": "DETERMINISTIC", "repair_attempted": False, "validation_status": "VALIDATED", "created_at": now})
    return engine, RepositoryFactory(engine), turn_id


def test_dispatch_is_idempotent_and_uses_identity_only_queue_payload():
    engine, factory, turn_id = _factory()
    queue = CaptureQueue()
    first = ResearchExecutionDispatcher(factory, queue=queue).dispatch_turn(turn_id)
    second = ResearchExecutionDispatcher(factory, queue=queue).dispatch_turn(turn_id)
    assert first.job_id == second.job_id == f"job_agent2_{str(turn_id).replace('-', '')}"
    assert len(queue.ids) == 2
    with engine.connect() as connection:
        assert connection.execute(select(research_turns.c.status).where(research_turns.c.id == turn_id)).scalar_one() == "QUEUED"
        assert connection.execute(select(research_turns.c.job_id).where(research_turns.c.id == turn_id)).scalar_one() == first.job_id
        assert connection.execute(select(jobs.c.created_by).where(jobs.c.id == first.job_id)).scalar_one() == "owner"


def test_supervisor_projects_running_then_result_pending_without_scientific_result():
    engine, factory, turn_id = _factory()
    dispatcher = ResearchExecutionDispatcher(factory, queue=CaptureQueue())
    result = dispatcher.dispatch_turn(turn_id)
    with factory.unit_of_work() as unit:
        unit.repositories.jobs.set_status(result.job_id, "queued")
        unit.repositories.jobs.set_status(result.job_id, "running")
        unit.repositories.tool_calls.save({"id": "call_phase4", "jobId": result.job_id, "stepId": "step_1", "toolId": "structure.xrd", "status": "completed", "idempotencyKey": f"{result.job_id}:step_1", "params": {}})
    running = ResearchExecutionSupervisor(factory).sync_for_job(result.job_id)
    assert running.status.value == "RUNNING"
    with factory.unit_of_work() as unit:
        unit.repositories.jobs.set_status(result.job_id, "completed")
    terminal = ResearchExecutionSupervisor(factory).sync_for_job(result.job_id)
    assert terminal.status.value == "RESULT_PENDING"
    assert terminal.execution_outcome == ExecutionOutcome.SUCCESS
    assert terminal.steps[0].status == ExecutionStepStatus.SUCCEEDED
    assert terminal.steps[0].display_name == "生成理论 XRD 图谱"
    with engine.connect() as connection:
        assert connection.execute(select(research_turns.c.status).where(research_turns.c.id == turn_id)).scalar_one() == "RESULT_PENDING"
        assert connection.execute(select(scientific_result_snapshots)).first() is None
        assert connection.execute(select(research_execution_summaries)).first() is not None
        assert connection.execute(select(research_turns.c.assistant_final_message_id).where(research_turns.c.id == turn_id)).scalar_one() is None


def test_supervisor_reprojects_existing_summary_after_terminal_final_message():
    engine, factory, turn_id = _factory()
    dispatcher = ResearchExecutionDispatcher(factory, queue=CaptureQueue())
    result = dispatcher.dispatch_turn(turn_id)
    with factory.unit_of_work() as unit:
        unit.repositories.jobs.set_status(result.job_id, "running")
        unit.repositories.jobs.set_status(result.job_id, "completed")
        unit.repositories.tool_calls.save(
            {
                "id": "call_terminal",
                "jobId": result.job_id,
                "stepId": "step_1",
                "toolId": "structure.xrd",
                "status": "completed",
                "idempotencyKey": f"{result.job_id}:step_1",
                "params": {},
            }
        )
    supervisor = ResearchExecutionSupervisor(factory)
    first = supervisor.sync_for_job(result.job_id)
    assert first.status == ResearchTurnStatus.RESULT_PENDING
    with engine.begin() as connection:
        connection.execute(
            update(research_turns)
            .where(research_turns.c.id == turn_id)
            .values(status=ResearchTurnStatus.COMPLETED.value, assistant_final_message_id="message")
        )
    second = supervisor.sync_for_job(result.job_id)
    assert second.status == ResearchTurnStatus.COMPLETED
    assert second.execution_outcome == ExecutionOutcome.SUCCESS
    with engine.connect() as connection:
        assert connection.execute(select(research_execution_summaries)).fetchall().__len__() == 1


def test_incremental_output_is_projected_before_job_terminal_and_deduplicated():
    engine, factory, turn_id = _factory()
    result = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id)
    with factory.unit_of_work() as unit:
        unit.repositories.jobs.set_status(result.job_id, "queued")
        unit.repositories.jobs.set_status(result.job_id, "running")
        unit.repositories.tool_calls.save({"id": "call_output", "jobId": result.job_id, "stepId": "step_1", "toolId": "structure.xrd", "status": "completed", "idempotencyKey": f"{result.job_id}:step_1", "params": {}})
    with engine.begin() as connection:
        connection.execute(insert(artifacts), {"id": "artifact_output", "project_id": "project", "dataset_id": "dataset", "job_id": result.job_id, "tool_call_id": "call_output", "type": "table_json", "name": "Theoretical XRD", "version": "1", "storage_key": "phase4/theoretical-xrd.json", "storage_provider": "local", "preview_key": "phase4/theoretical-xrd.preview.json", "size_bytes": 42, "content_type": "application/json", "content_hash": "sha-output", "sha256": "sha-output", "metadata_json": {}})
    supervisor = ResearchExecutionSupervisor(factory)
    first = supervisor.sync_for_job(result.job_id)
    second = supervisor.sync_for_job(result.job_id)
    assert first.status.value == "RUNNING"
    assert [item.artifact_id for item in first.incremental_outputs] == ["artifact_output"]
    assert len(second.incremental_outputs) == 1
    product_payload = first.model_dump(mode="json")
    product_text = str(product_payload)
    assert result.job_id not in product_text
    assert "call_output" not in product_text
    assert "structure.xrd" not in product_text
    assert not ({"job_id", "tool_call_id", "tool_id", "worker_id", "queue", "rq", "provider"} & set(product_payload))
    with engine.connect() as connection:
        output_events = connection.execute(select(research_turn_events).where(research_turn_events.c.event_type == "EXECUTION_OUTPUT_AVAILABLE")).all()
        assert len(output_events) == 1


def test_queued_cancel_waits_for_authoritative_job_confirmation():
    _engine, factory, turn_id = _factory()
    result = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id)
    canceling = ResearchExecutionSupervisor(factory).request_cancel(turn_id)
    assert canceling["status"] == "CANCELING"
    with factory.unit_of_work() as unit:
        assert unit.repositories.jobs.get(result.job_id)["status"] == "cancel_requested"
        unit.repositories.jobs.set_status(result.job_id, "cancelled")
    canceled = ResearchExecutionSupervisor(factory).sync_for_job(result.job_id)
    assert canceled.status.value == "CANCELED"
    assert canceled.execution_outcome == ExecutionOutcome.CANCELED


def test_result_pending_execution_cannot_be_canceled():
    with pytest.raises(InvalidResearchTurnTransition):
        ensure_transition(ResearchTurnStatus.RESULT_PENDING, ResearchTurnStatus.CANCELED)


def test_queue_publish_failure_reconciles_the_same_job_identity():
    engine, factory, turn_id = _factory()
    queue = FailOnceQueue()
    try:
        ResearchExecutionDispatcher(factory, queue=queue).dispatch_turn(turn_id)
    except ExecutionQueuePublishFailed:
        pass
    else:
        raise AssertionError("the first queue publish must fail")
    recovered = ResearchExecutionReconciler(factory, queue=queue).reconcile_turn(turn_id)
    assert recovered.queued is True
    assert queue.ids == [recovered.job_id, recovered.job_id]
    with engine.connect() as connection:
        assert connection.execute(select(research_turns.c.job_id).where(research_turns.c.id == turn_id)).scalar_one() == recovered.job_id


def test_cancellation_race_preserves_completed_execution_with_warning():
    engine, factory, turn_id = _factory()
    result = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id)
    ResearchExecutionSupervisor(factory).request_cancel(turn_id)
    with factory.unit_of_work() as unit:
        unit.repositories.tool_calls.save({"id": "call_race", "jobId": result.job_id, "stepId": "step_1", "toolId": "structure.xrd", "status": "completed", "idempotencyKey": f"{result.job_id}:step_1", "params": {}})
        unit.repositories.jobs.set_status(result.job_id, "completed")
    view = ResearchExecutionSupervisor(factory).sync_for_job(result.job_id)
    assert view.status.value == "RESULT_PENDING"
    assert [item.code for item in view.warnings] == ["CANCELLATION_REQUESTED_AFTER_EXECUTION_COMPLETED"]
    with engine.connect() as connection:
        summary = connection.execute(select(research_execution_summaries.c.summary_json)).scalar_one()
        assert summary["warnings"][0]["code"] == "CANCELLATION_REQUESTED_AFTER_EXECUTION_COMPLETED"


def test_execution_outcome_classifier_uses_runtime_steps_and_outputs():
    classifier = ExecutionOutcomeClassifier()
    cases = [
        ({"status": "completed"}, [{"status": "completed"}], [], ExecutionOutcome.SUCCESS),
        ({"status": "partial_success"}, [{"status": "completed"}, {"status": "failed"}], [{}], ExecutionOutcome.PARTIAL),
        ({"status": "failed"}, [{"status": "failed"}], [], ExecutionOutcome.FAILED),
        ({"status": "cancelled"}, [], [], ExecutionOutcome.CANCELED),
    ]
    for job, calls, output_rows, expected in cases:
        assert classifier.classify(
            analysis_plan={"steps": [{"stepId": f"step_{index}"} for index in range(1, max(1, len(calls)) + 1)]},
            job=job,
            tool_calls=[{**call, "stepId": f"step_{index}"} for index, call in enumerate(calls, 1)],
            artifacts=output_rows,
        ) == expected
