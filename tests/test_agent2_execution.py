from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import replace
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
from mdi_api.agent2_errors import CapabilityNotRegistered, InvalidResearchTurnTransition
from mdi_api.research_agent.capabilities.registry import InMemoryCapabilityRegistry
from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES
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


def _factory(tool_id="structure.xrd"):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    plan_payload = {"schemaVersion": "0.2", "goal": "Run test", "datasetId": "dataset", "profileId": "profile", "toolRegistryVersion": "test", "graphHash": compute_dependency_graph_hash([]), "assumptions": [], "warnings": [], "steps": [{"stepId": "step_1", "purpose": "执行科学分析", "reason": "test", "toolId": tool_id, "inputRefs": [], "params": {}, "output": {}}], "dependencyBindings": [], "expectedArtifacts": [{"name": "step_1.theoretical_xrd", "type": "table_json", "fromStepId": "step_1"}]}
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
    supervisor = ResearchExecutionSupervisor(factory, projector_version="agent2_execution_1.0")
    first = supervisor.sync_for_job(result.job_id)
    assert first.status == ResearchTurnStatus.RESULT_PENDING
    with factory.session() as session:
        preserved = session.agent2.research_execution_summaries.get_for_turn(turn_id)
    supervisor = ResearchExecutionSupervisor(factory)
    assert supervisor.sync_for_job(result.job_id).status == ResearchTurnStatus.RESULT_PENDING
    with engine.begin() as connection:
        connection.execute(
            update(research_turns)
            .where(research_turns.c.id == turn_id)
            .values(status=ResearchTurnStatus.COMPLETED.value, assistant_final_message_id="message")
        )
    second = supervisor.sync_for_job(result.job_id)
    assert second.status == ResearchTurnStatus.COMPLETED
    assert second.execution_outcome == ExecutionOutcome.SUCCESS
    with factory.session() as session:
        assert session.agent2.research_execution_summaries.get_for_turn(turn_id) == preserved
    with engine.connect() as connection:
        assert connection.execute(select(research_execution_summaries)).fetchall().__len__() == 1


def _retired_capability_execution(status="FAILED"):
    engine, factory, turn_id = _factory()
    dispatch = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id)
    with factory.unit_of_work() as unit:
        unit.repositories.jobs.set_status(dispatch.job_id, "running")
        unit.repositories.jobs.set_status(dispatch.job_id, "completed")
        unit.repositories.tool_calls.save({"id": "saved-call", "jobId": dispatch.job_id, "stepId": "step_1", "toolId": "structure.xrd", "status": "completed", "idempotencyKey": f"{dispatch.job_id}:step_1", "params": {}})
    with engine.begin() as connection:
        connection.execute(insert(artifacts), {"id": "saved-output", "project_id": "project", "dataset_id": "dataset", "job_id": dispatch.job_id, "tool_call_id": "saved-call", "type": "table_json", "name": "Saved XRD", "version": "1", "storage_key": "saved/output.json", "storage_provider": "local", "size_bytes": 42, "content_type": "application/json", "content_hash": "saved-hash", "sha256": "saved-hash", "metadata_json": {}})
    ResearchExecutionSupervisor(factory).sync_for_job(dispatch.job_id)
    with engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status=status))
    capabilities = InMemoryCapabilityRegistry()
    capabilities.register(DEFAULT_AGENT2_REGISTRIES.capabilities.require("diffraction.theoretical_xrd", "1.0").model_copy(update={"version": "2.0", "display_name": "New method, not the saved execution"}))
    return factory, turn_id, dispatch.job_id, replace(DEFAULT_AGENT2_REGISTRIES, capabilities=capabilities)


@pytest.mark.parametrize("status", ["FAILED", "CANCELED", "COMPLETED", "PARTIAL"])
def test_retired_capability_keeps_exact_terminal_progress_without_rewriting_history(status):
    factory, turn_id, job_id, registries = _retired_capability_execution(status)
    def saved():
        with factory.session() as session:
            return (
                session.agent2.research_turns.get(turn_id),
                session.agent2.research_execution_summaries.get_for_turn(turn_id),
                session.agent2.research_turn_events.list_for_turn(turn_id),
                session.repositories.jobs.get(job_id),
                session.repositories.artifacts.list_for_job(job_id),
            )
    original = saved()
    supervisor = ResearchExecutionSupervisor(factory, registries=registries)
    for _ in range(2):
        progress = supervisor.sync_for_job(job_id)
        assert progress.status.value == status
        # A failed interpretation/canceled Turn does not change saved scientific success.
        assert progress.execution_outcome == ExecutionOutcome.SUCCESS
        assert progress.steps[0].display_name == "生成理论 XRD 图谱"
        assert progress.steps[0].status == ExecutionStepStatus.SUCCEEDED
        assert [item.artifact_id for item in progress.incremental_outputs] == ["saved-output"]
        assert progress.warnings[-1].code == "HISTORICAL_CAPABILITY_VERSION_UNAVAILABLE"
        assert saved() == original


@pytest.mark.parametrize("status", ["QUEUED", "RUNNING", "CANCELING", "RESULT_PENDING", "INTERPRETING"])
def test_retired_capability_cannot_authorize_incomplete_work(status):
    factory, _turn_id, job_id, registries = _retired_capability_execution(status)
    with pytest.raises(CapabilityNotRegistered):
        ResearchExecutionSupervisor(factory, registries=registries).sync_for_job(job_id)


@pytest.mark.parametrize("fault", ["missing-summary", "wrong-summary-plan", "wrong-summary-job", "running-job"])
def test_retired_capability_fallback_requires_an_exact_completed_execution(fault):
    factory, turn_id, job_id, registries = _retired_capability_execution()
    with factory.engine.begin() as connection:
        if fault == "missing-summary":
            connection.execute(research_execution_summaries.delete())
        elif fault == "running-job":
            connection.execute(update(jobs).where(jobs.c.id == job_id).values(status="running"))
        else:
            summary = connection.execute(select(research_execution_summaries.c.summary_json)).scalar_one()
            summary["analysis_plan_id" if fault == "wrong-summary-plan" else "job_id"] = "different-record"
            connection.execute(update(research_execution_summaries).values(summary_json=summary))
    with pytest.raises(CapabilityNotRegistered):
        ResearchExecutionSupervisor(factory, registries=registries).sync_for_job(job_id)


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


def _preflight_failure(code="ROOT_RESOURCE_HASH_MISMATCH"):
    engine, factory, turn_id = _factory()
    job_id = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id).job_id
    with engine.begin() as connection:
        connection.execute(update(jobs).where(jobs.c.id == job_id).values(execution_attempt=1))
    with factory.unit_of_work() as unit:
        unit.repositories.job_events.append_event(job_id, event_type="job.claimed", status="running", message="claimed", payload={"executionAttempt": 1})
        unit.repositories.job_events.append_event(job_id, event_type="dependency.validation_aborted", status="error", message="private-credential /local/path hidden reasoning", payload={"errorCode": code, "secret": "private-credential"})
        unit.repositories.jobs.set_status(job_id, "failed")
    return engine, factory, turn_id, job_id


@pytest.mark.parametrize("code,expected", [
    ("ROOT_RESOURCE_HASH_MISMATCH", "ROOT_RESOURCE_HASH_MISMATCH"),
    ("private-unknown-error", "EXECUTION_FAILED"),
])
def test_preflight_failure_has_safe_reason_without_inventing_tool_execution(code, expected):
    engine, factory, turn_id, job_id = _preflight_failure(code)
    view = ResearchExecutionSupervisor(factory).sync_for_job(job_id)
    assert view.status == ResearchTurnStatus.FAILED
    assert view.steps[0].status == ExecutionStepStatus.SKIPPED
    assert view.active_step_ids == [] and view.completed_step_count == 0
    assert view.incremental_outputs == []
    assert [warning.code for warning in view.warnings] == [expected]
    assert "private" not in view.model_dump_json() and "hidden reasoning" not in view.model_dump_json()
    with factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        assert turn["error_code"] == expected
        assert turn["error_summary"] == view.warnings[0].message
        summary = session.agent2.research_execution_summaries.get_for_turn(turn_id)["summary_json"]
        assert summary["skipped_step_ids"] == ["step_1"]
        assert summary["failed_step_ids"] == []
        assert summary["steps"][0]["tool_call_ids"] == []
        assert session.repositories.tool_calls.list_for_job(job_id) == []


@pytest.mark.parametrize("error_code,reason,expected", [
    ("TOOL_PARAM_INVALID", None, "CORRELATION_PARAMS_INVALID"),
    ("TOOL_INPUT_INVALID", "CORRELATION_COLUMN_LIMIT_EXCEEDED", "CORRELATION_COLUMN_LIMIT_EXCEEDED"),
    ("TOOL_INPUT_INVALID", "CORRELATION_COLUMN_IDENTITY_INVALID", "CORRELATION_COLUMN_IDENTITY_INVALID"),
    ("TOOL_INPUT_INVALID", "CORRELATION_NO_VALID_PAIRS", "CORRELATION_NO_VALID_PAIRS"),
    ("TOOL_INPUT_INVALID", ["private-reason"], "EXECUTION_FAILED"),
])
@pytest.mark.parametrize("tool_id", ["viz.correlation", "viz.histogram", "viz.scatter"])
def test_table_plot_failure_has_reviewed_terminal_feedback(error_code, reason, expected, tool_id):
    if tool_id == "viz.histogram":
        histogram_reasons = {"CORRELATION_PARAMS_INVALID": "HISTOGRAM_PARAMS_INVALID", "CORRELATION_COLUMN_LIMIT_EXCEEDED": "HISTOGRAM_GROUP_LIMIT",
                             "CORRELATION_COLUMN_IDENTITY_INVALID": "HISTOGRAM_COLUMN_INVALID", "CORRELATION_NO_VALID_PAIRS": "HISTOGRAM_VALUES_INVALID"}
        reason = histogram_reasons.get(reason, reason) if isinstance(reason, str) else reason
        expected = histogram_reasons.get(expected, expected)
    if tool_id == "viz.scatter":
        scatter_reasons = {"CORRELATION_PARAMS_INVALID": "SCATTER_PARAMS_INVALID", "CORRELATION_COLUMN_LIMIT_EXCEEDED": "SCATTER_GROUP_LIMIT",
                           "CORRELATION_COLUMN_IDENTITY_INVALID": "SCATTER_COLUMN_INVALID", "CORRELATION_NO_VALID_PAIRS": "SCATTER_VALUES_INVALID"}
        reason = scatter_reasons.get(reason, reason) if isinstance(reason, str) else reason
        expected = scatter_reasons.get(expected, expected)
    _engine, factory, turn_id = _factory(tool_id)
    job_id = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id).job_id
    error = {"code": error_code, "message": "private-credential /local/path hidden reasoning", "details": {"errorType": reason}}
    with factory.unit_of_work() as unit:
        unit.repositories.tool_calls.save({"id": "correlation-call", "jobId": job_id, "stepId": "step_1", "toolId": tool_id, "status": "failed", "params": {}, "error": error})
        unit.repositories.job_events.append_event(job_id, event_type="tool.failed", status="error", message="private-message",
            payload={"toolCallId": "correlation-call", "toolId": tool_id, "error": error})
        unit.repositories.jobs.set_status(job_id, "failed")
    view = ResearchExecutionSupervisor(factory).sync_for_job(job_id)
    assert view.status == ResearchTurnStatus.FAILED
    failure = next(warning for warning in view.warnings if warning.code == expected)
    assert view.steps[0].status == ExecutionStepStatus.FAILED
    assert not view.active_step_ids and not view.incremental_outputs
    assert "private" not in view.model_dump_json() and "hidden reasoning" not in view.model_dump_json()
    with factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        assert turn["error_code"] == expected
        assert turn["error_summary"] == failure.message


def test_historical_failure_is_enriched_without_rewriting_summary_or_turn():
    engine, factory, turn_id, job_id = _preflight_failure()
    supervisor = ResearchExecutionSupervisor(factory)
    supervisor.sync_for_job(job_id)
    with engine.begin() as connection:
        old = connection.execute(select(research_execution_summaries.c.summary_json)).scalar_one()
        old.update(warnings=[], skipped_step_ids=[], projector_version="agent2_execution_1.0")
        old["steps"][0]["status"] = "PENDING"
        connection.execute(update(research_execution_summaries).values(summary_json=old, projector_version="agent2_execution_1.0"))
        connection.execute(update(research_turns).values(error_code=None, error_summary=None))
    with factory.session() as session:
        before = session.agent2.research_execution_summaries.get_for_turn(turn_id)
        turn_before = session.agent2.research_turns.get(turn_id)
    for _ in range(2):
        view = supervisor.sync_for_job(job_id)
        assert view.warnings[0].code == "ROOT_RESOURCE_HASH_MISMATCH"
        assert view.steps[0].status == ExecutionStepStatus.SKIPPED
    with factory.session() as session:
        assert session.agent2.research_execution_summaries.get_for_turn(turn_id) == before
        assert session.agent2.research_turns.get(turn_id) == turn_before


@pytest.mark.parametrize("job_status,step_status", [("running", "PENDING"), ("failed", "SKIPPED"), ("cancelled", "CANCELED")])
def test_unstarted_steps_reflect_job_terminal_state(job_status, step_status):
    _engine, factory, turn_id = _factory()
    job_id = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id).job_id
    with factory.unit_of_work() as unit:
        if job_status == "cancelled":
            unit.repositories.jobs.request_cancel(job_id)
        unit.repositories.jobs.set_status(job_id, job_status)
    view = ResearchExecutionSupervisor(factory).sync_for_job(job_id)
    assert view.steps[0].status.value == step_status
    assert not view.active_step_ids
    if job_status == "cancelled":
        assert not view.warnings


@pytest.mark.parametrize("final_status", ["running", "completed", "failed"])
def test_current_attempt_does_not_inherit_old_preflight_failure(final_status):
    engine, factory, _turn_id, job_id = _preflight_failure()
    with engine.begin() as connection:
        connection.execute(update(jobs).where(jobs.c.id == job_id).values(execution_attempt=2, status=final_status))
    with factory.unit_of_work() as unit:
        unit.repositories.job_events.append_event(job_id, event_type="job.reclaimed", status="running", message="reclaimed", payload={"executionAttempt": 2})
        unit.repositories.job_events.append_event(job_id, event_type="dependency.validation_aborted", status="error", message="stale owner", payload={"executionAttempt": 1, "errorCode": "ROOT_RESOURCE_HASH_MISMATCH"})
        if final_status == "completed":
            unit.repositories.tool_calls.save({"id": "retry-call", "jobId": job_id, "stepId": "step_1", "toolId": "structure.xrd", "status": "completed", "attempt": 2, "params": {}})
    view = ResearchExecutionSupervisor(factory).sync_for_job(job_id)
    assert all(warning.code != "ROOT_RESOURCE_HASH_MISMATCH" for warning in view.warnings)
    if final_status == "failed":
        assert [warning.code for warning in view.warnings] == ["EXECUTION_FAILED"]
    else:
        assert not view.warnings


def test_partial_execution_keeps_successful_outputs_and_skips_unstarted_steps():
    engine, factory, turn_id = _factory()
    job_id = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id).job_id
    with engine.begin() as connection:
        plan = connection.execute(select(analysis_plans.c.analysis_plan_json)).scalar_one()
        plan["steps"].append({**plan["steps"][0], "stepId": "step_2"})
        connection.execute(update(analysis_plans).values(analysis_plan_json=plan, plan_hash=compute_plan_hash(AnalysisPlanV02.model_validate(plan))))
        connection.execute(insert(artifacts), {"id": "partial-output", "project_id": "project", "dataset_id": "dataset", "job_id": job_id, "tool_call_id": "partial-call", "type": "table_json", "name": "XRD", "version": "1", "storage_key": "test.json", "storage_provider": "local", "size_bytes": 2, "content_hash": "test-hash", "metadata_json": {}})
    with factory.unit_of_work() as unit:
        unit.repositories.tool_calls.save({"id": "partial-call", "jobId": job_id, "stepId": "step_1", "toolId": "structure.xrd", "status": "completed", "params": {}})
        unit.repositories.jobs.set_status(job_id, "running")
        unit.repositories.jobs.set_status(job_id, "partial_success")
    view = ResearchExecutionSupervisor(factory).sync_for_job(job_id)
    assert view.execution_outcome == ExecutionOutcome.PARTIAL
    assert [step.status.value for step in view.steps] == ["SUCCEEDED", "SKIPPED"]
    assert [item.artifact_id for item in view.incremental_outputs] == ["partial-output"]
    assert view.completed_step_count == 1 and not view.active_step_ids
