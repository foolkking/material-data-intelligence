from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from mdi_api.application.interpretation import interpret_queued_turn
from mdi_api.application.jobs import execute_queued_job
from mdi_api.application.research import (
    process_queued_planning,
    process_queued_turn,
)
from mdi_api.research_agent.planning.worker import _process_and_dispatch
from mdi_api.application.scientific_reports import generate_queued_report
from mdi_api.application.scientific_results import project_queued_result
from mdi_api.scientific_reports.service import ScientificReportError
from mdi_schemas.worker_queues import WORKER_QUEUE_MANIFEST
from mdi_workers import queue_runtime


EXPECTED_QUEUES_AND_HANDLERS = (
    (
        "mdi-agent-turns",
        "mdi_api.research_agent_worker.run_queued_turn",
    ),
    (
        "mdi-agent-plans",
        "mdi_api.research_agent_planning_worker.run_queued_planning",
    ),
    (
        "mdi-jobs",
        "mdi_workers.queue_runtime.run_queued_job",
    ),
    (
        "mdi-agent-results",
        "mdi_api.scientific_results.worker.run_queued_result_projection",
    ),
    (
        "mdi-agent-interpretations",
        "mdi_workers.interpretation_worker.run_queued_interpretation",
    ),
    (
        "mdi-agent-reports",
        "mdi_workers.report_worker.run_queued_report_generation",
    ),
)


def _resolve(dotted_path: str):
    module_name, symbol_name = dotted_path.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), symbol_name)


def test_frozen_worker_queue_and_handler_contracts_resolve() -> None:
    actual = tuple(
        (definition.default_name, definition.handler)
        for definition in WORKER_QUEUE_MANIFEST
    )
    assert actual == EXPECTED_QUEUES_AND_HANDLERS
    for _, dotted_path in actual:
        handler = _resolve(dotted_path)
        assert callable(handler)
        assert tuple(inspect.signature(handler).parameters) in {
            ("turn_id",),
            ("job_id",),
            ("generation_id",),
            ("generation_id", "expected_attempt"),
        }
        if "expected_attempt" in inspect.signature(handler).parameters:
            assert inspect.signature(handler).parameters["expected_attempt"].default is None


def test_application_entrypoints_do_not_import_worker_transport_or_concrete_composition() -> None:
    application_root = (
        Path(__file__).resolve().parents[1]
        / "apps"
        / "api"
        / "mdi_api"
        / "application"
    )
    forbidden_prefixes = (
        "fastapi",
        "mdi_api.config",
        "mdi_api.database",
        "mdi_api.routers",
        "mdi_workers",
    )
    violations: list[str] = []
    for path in application_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                if name.startswith(forbidden_prefixes):
                    violations.append(f"{path.relative_to(application_root)}:{name}")
    assert violations == []


class _AsyncTurnProcessor:
    def __init__(self) -> None:
        self.turn_id: UUID | None = None

    async def process(self, turn_id: UUID) -> str:
        self.turn_id = turn_id
        return "turn-processed"


class _PlanningProcessor:
    def __init__(self) -> None:
        self.turn_id: UUID | None = None

    def process(self, turn_id: UUID) -> dict[str, str]:
        self.turn_id = turn_id
        return {"status": "planned"}


class _PlanReadyProcessor:
    def __init__(self) -> None:
        self.turn_id: UUID | None = None

    def process(self, turn_id: UUID) -> dict[str, str]:
        self.turn_id = turn_id
        return {"status": "PLAN_READY", "turn_id": str(turn_id)}


class _ExecutionDispatcher:
    def __init__(self) -> None:
        self.turn_id: UUID | None = None

    def dispatch_turn(self, turn_id: UUID):
        self.turn_id = turn_id
        return SimpleNamespace(
            job_id=f"job_agent2_{turn_id.hex}",
            queued=True,
            queue_backend="rq",
            message="job queued",
        )


def test_research_worker_entrypoints_adapt_string_identity_once() -> None:
    turn_id = uuid4()
    turn_processor = _AsyncTurnProcessor()
    planning_processor = _PlanningProcessor()

    assert (
        process_queued_turn(str(turn_id), processor=turn_processor)
        == "turn-processed"
    )
    assert process_queued_planning(
        str(turn_id),
        processor=planning_processor,
    ) == {"status": "planned"}
    assert turn_processor.turn_id == turn_id
    assert planning_processor.turn_id == turn_id


def test_planning_worker_dispatches_plan_ready_without_browser_participation() -> None:
    turn_id = uuid4()
    processor = _PlanReadyProcessor()
    dispatcher = _ExecutionDispatcher()

    result = _process_and_dispatch(
        str(turn_id),
        processor=processor,
        dispatcher=dispatcher,
    )

    assert processor.turn_id == turn_id
    assert dispatcher.turn_id == turn_id
    assert result["status"] == "PLAN_READY"
    assert result["execution_dispatch"] == {
        "job_id": f"job_agent2_{turn_id.hex}",
        "queued": True,
        "queue_backend": "rq",
        "message": "job queued",
    }


class _JobRuntime:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def handle_job(self, job_id: str) -> dict[str, str]:
        self.calls.append(("handle", job_id))
        return {"job_id": job_id, "status": "completed"}

    def notify_job_progress(self, job_id: str) -> None:
        self.calls.append(("notify", job_id))


def test_job_application_entrypoint_preserves_handle_then_notify_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = _JobRuntime()
    monkeypatch.setattr(
        queue_runtime,
        "create_queue_worker_runtime_from_settings",
        lambda: runtime,
    )

    result = queue_runtime.run_queued_job("job-1")

    assert result == {"job_id": "job-1", "status": "completed"}
    assert runtime.calls == [("handle", "job-1"), ("notify", "job-1")]


class _Projector:
    def __init__(self, snapshot_id: UUID) -> None:
        self.snapshot_id = snapshot_id
        self.turn_id: UUID | None = None

    def project_turn(self, turn_id: UUID) -> dict[str, UUID]:
        self.turn_id = turn_id
        return {"id": self.snapshot_id}


def test_result_projection_entrypoint_preserves_result_identity() -> None:
    turn_id = uuid4()
    snapshot_id = uuid4()
    projector = _Projector(snapshot_id)

    result = project_queued_result(str(turn_id), projector=projector)

    assert result == {
        "turn_id": str(turn_id),
        "snapshot_id": str(snapshot_id),
        "status": "RESULT_READY",
    }
    assert projector.turn_id == turn_id


class _InterpretationSession:
    def __init__(self, status: str) -> None:
        self.agent2 = SimpleNamespace(
            research_turns=SimpleNamespace(
                get=lambda _turn_id: {"status": status}
            )
        )

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class _InterpretationFactory:
    def __init__(self, status: str) -> None:
        self.status = status

    def session(self) -> _InterpretationSession:
        return _InterpretationSession(self.status)


class _Interpreter:
    def __init__(self, interpretation_id: UUID) -> None:
        self.interpretation_id = interpretation_id
        self.turn_id: UUID | None = None

    def process_turn(self, turn_id: UUID) -> dict[str, UUID]:
        self.turn_id = turn_id
        return {"id": self.interpretation_id}


class _AutonomyAdvance:
    def model_dump(self, *, mode: str) -> dict:
        assert mode == "json"
        return {
            "outcome": "CONTINUE_WITH_ANALYSIS",
            "cycle_index": 1,
            "child_turn_id": str(uuid4()),
        }


class _Autonomy:
    def __init__(self) -> None:
        self.turn_id: UUID | None = None

    def advance_after_interpretation(self, turn_id: UUID) -> _AutonomyAdvance:
        self.turn_id = turn_id
        return _AutonomyAdvance()


def test_interpretation_entrypoint_returns_persisted_status() -> None:
    turn_id = uuid4()
    interpretation_id = uuid4()
    interpreter = _Interpreter(interpretation_id)

    result = interpret_queued_turn(
        str(turn_id),
        interpreter=interpreter,
        repository_factory=_InterpretationFactory("COMPLETED"),
    )

    assert result == {
        "turn_id": str(turn_id),
        "interpretation_id": str(interpretation_id),
        "status": "COMPLETED",
    }
    assert interpreter.turn_id == turn_id


def test_interpretation_entrypoint_advances_bounded_autonomy_only_after_terminal_state() -> None:
    turn_id = uuid4()
    autonomy = _Autonomy()

    completed = interpret_queued_turn(
        str(turn_id),
        interpreter=_Interpreter(uuid4()),
        repository_factory=_InterpretationFactory("COMPLETED"),
        autonomy=autonomy,
    )

    assert autonomy.turn_id == turn_id
    assert completed["autonomy"]["outcome"] == "CONTINUE_WITH_ANALYSIS"

    nonterminal_autonomy = _Autonomy()
    running = interpret_queued_turn(
        str(turn_id),
        interpreter=_Interpreter(uuid4()),
        repository_factory=_InterpretationFactory("INTERPRETING"),
        autonomy=nonterminal_autonomy,
    )
    assert "autonomy" not in running
    assert nonterminal_autonomy.turn_id is None


class _ReportGenerationRepository:
    def __init__(self, generation: dict, *, claimed: dict | None) -> None:
        self.generation = generation
        self.claimed = claimed
        self.status_calls: list[tuple[UUID, str, dict]] = []

    def get(self, _identifier: UUID) -> dict:
        return self.generation

    def claim(self, _identifier: UUID, **_kwargs) -> dict | None:
        return self.claimed

    def compare_status(self, identifier: UUID, status: str, **kwargs) -> dict:
        self.status_calls.append((identifier, status, kwargs))
        return {**self.generation, "status": status}


class _ReportUnit:
    def __init__(self, generations: _ReportGenerationRepository) -> None:
        self.agent2 = SimpleNamespace(
            scientific_report_generations=generations,
            scientific_reports=SimpleNamespace(
                get_for_turn=lambda _turn_id: None
            ),
        )

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class _ReportFactory:
    def __init__(self, generations: _ReportGenerationRepository) -> None:
        self.generations = generations

    def unit_of_work(self) -> _ReportUnit:
        return _ReportUnit(self.generations)


class _ReportGenerator:
    def __init__(self, report_id: str = "report-1", error: Exception | None = None):
        self.report_id = report_id
        self.error = error
        self.calls: list[tuple[UUID, str]] = []

    def generate_for_turn(
        self,
        turn_id: UUID,
        *,
        created_by: str = "user_local",
        generation_id: UUID | None = None,
        expected_attempt: int | None = None,
    ) -> dict[str, str]:
        self.calls.append((turn_id, created_by))
        if self.error is not None:
            raise self.error
        return {"report_id": self.report_id}


def _report_generation() -> dict:
    return {
        "status": "COMPOSING",
        "attempt_count": 1,
        "research_turn_id": uuid4(),
        "requested_by": "user-1",
    }


def test_report_entrypoint_preserves_claim_generate_ready_lifecycle() -> None:
    generation_id = uuid4()
    generation = _report_generation()
    generations = _ReportGenerationRepository(
        generation,
        claimed=generation,
    )
    generator = _ReportGenerator()

    result = generate_queued_report(
        str(generation_id),
        repository_factory=_ReportFactory(generations),
        report_generator=generator,
    )

    assert result == {
        "generation_id": str(generation_id),
        "report_id": "report-1",
        "status": "READY",
    }
    assert generator.calls == [
        (generation["research_turn_id"], generation["requested_by"])
    ]
    assert generations.status_calls == [(generation_id, "READY", {"expected_status": "COMPOSING", "expected_attempt": 1})]


@pytest.mark.parametrize(
    ("error", "expected_code"),
    [
        (
            ScientificReportError("REPORT_INPUT_INVALID", "invalid report"),
            "REPORT_INPUT_INVALID",
        ),
        (RuntimeError("provider failed"), "REPORT_GENERATION_FAILED"),
    ],
)
def test_report_entrypoint_preserves_typed_failure_persistence(
    error: Exception,
    expected_code: str,
) -> None:
    generation_id = uuid4()
    generation = _report_generation()
    generations = _ReportGenerationRepository(
        generation,
        claimed=generation,
    )

    with pytest.raises(type(error)):
        generate_queued_report(
            str(generation_id),
            repository_factory=_ReportFactory(generations),
            report_generator=_ReportGenerator(error=error),
        )

    assert len(generations.status_calls) == 1
    identifier, status, details = generations.status_calls[0]
    assert identifier == generation_id
    assert status == "FAILED"
    assert details["error_code"] == expected_code


def test_execute_queued_job_propagates_handle_failure_without_notification() -> None:
    class FailingRuntime(_JobRuntime):
        def handle_job(self, job_id: str):
            self.calls.append(("handle", job_id))
            raise RuntimeError("job failed")

    runtime = FailingRuntime()
    with pytest.raises(RuntimeError, match="job failed"):
        execute_queued_job("job-2", runtime=runtime)
    assert runtime.calls == [("handle", "job-2")]


def test_research_worker_boundary_persists_failure_before_rq_rethrows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A fresh RQ process failure must not leave a received Turn orphaned."""

    from mdi_api import research_agent_worker
    from mdi_api.research_agent.orchestration import worker as orchestration_worker

    turn_id = str(uuid4())
    persisted: list[tuple[str, str, str]] = []

    monkeypatch.setattr(
        research_agent_worker,
        "_persist_worker_boundary_failure",
        lambda failed_turn_id, error: persisted.append(
            (str(failed_turn_id), type(error).__name__, str(error))
        ),
    )

    def fail_before_handler(_turn_id: str):
        raise ImportError("simulated missing worker dependency")

    monkeypatch.setattr(
        orchestration_worker,
        "run_queued_turn",
        fail_before_handler,
    )

    with pytest.raises(ImportError, match="simulated missing worker dependency"):
        research_agent_worker.run_queued_turn(turn_id)

    assert persisted == [
        (turn_id, "ImportError", "simulated missing worker dependency")
    ]
