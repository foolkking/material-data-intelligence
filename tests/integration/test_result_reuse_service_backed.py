from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest
from redis import Redis
from rq import Queue
from sqlalchemy import create_engine, func, select

from mdi_api.db import (
    agent2_scientific_interpretations,
    analysis_plans,
    artifacts,
    jobs,
    messages,
    research_context_snapshots,
    research_session_states,
    research_turns,
    scientific_result_snapshots,
    tool_calls,
)
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import ScientificObjectRef, StorageRef
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.scientific_results.relevance import ScientificResultRelevanceEvaluator
from mdi_api.unit_of_work import RepositoryFactory


ROOT = Path(__file__).resolve().parents[2]


def _phase6_module():
    path = ROOT / "tests" / "integration" / "test_interpretation_service_backed.py"
    spec = importlib.util.spec_from_file_location("agent2_phase6_service_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _counts(connection) -> dict[str, int]:
    return {
        "plans": connection.execute(select(func.count()).select_from(analysis_plans)).scalar_one(),
        "jobs": connection.execute(select(func.count()).select_from(jobs)).scalar_one(),
        "tool_calls": connection.execute(select(func.count()).select_from(tool_calls)).scalar_one(),
        "artifacts": connection.execute(select(func.count()).select_from(artifacts)).scalar_one(),
        "result_snapshots": connection.execute(select(func.count()).select_from(scientific_result_snapshots)).scalar_one(),
    }


def _safe_interpreter_fixture(bundle: dict) -> str:
    facts = list(bundle.get("facts") or [])
    result_items = list(bundle.get("result_items") or [])
    assert facts, "service fixture requires at least one persisted ScientificFact"
    assert result_items, "service fixture requires at least one persisted ResultItem"
    fact = facts[0]
    item = result_items[0]
    return json.dumps({
        "contract_version": "1.0",
        "title": "已验证的历史科学结果",
        "answer_lead": "该回答仅解释已提交且可追溯的科学结果。",
        "primary_findings": [{
            "finding_id": "phase7-grounded-finding-1",
            "statement": "该结果单元由已提交的持久化科学证据支持。",
            "importance": "MEDIUM",
            "confidence": "HIGH",
            "fact_refs": [fact["fact_id"]],
            "evidence_refs": [],
            "result_item_refs": [item["id"]],
        }],
        "supporting_findings": [],
        "limitations": [],
        "primary_result_refs": [item["id"]],
        "supporting_result_refs": [],
        "follow_up_suggestions": [],
    }, ensure_ascii=False)


_FOLLOW_UP_PROCESS = r"""
import asyncio
import json
import sys

from sqlalchemy import select

from mdi_api.database import create_repository_factory
from mdi_api.db import projects, research_turns, scientific_result_snapshots, users
from mdi_api.interpretation.queue import RedisRQInterpretationQueue
from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
from mdi_api.research_agent.registry_validation import build_default_agent2_registries
from mdi_api.research_agent.schemas import CreateResearchTurnRequest
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser
from mdi_api.unit_of_work import transaction_active


class ExistingResultClient:
    def __init__(self):
        self.calls = 0

    async def generate_structured(self, **_kwargs):
        assert transaction_active() is False
        self.calls += 1
        return StructuredLLMResult(
            provider="fake",
            model="phase7-service",
            parsed={
                "contract_version": "1.0",
                "action": "INTERPRET_RESULT",
                "assistant_message": "基于已授权的历史科学结果继续解释。",
                "research_objective": None,
                "selected_scope_ref_keys": [],
                "scientific_requirements": [],
                "reusable_result_ref_keys": ["result_1"],
                "clarification": None,
                "confidence": "HIGH",
            },
            latency_ms=1,
            prompt_version="research-orchestrator/1.0",
        )


previous_turn_id, result_snapshot_id, question, redis_url, queue_name = sys.argv[1:6]
factory = create_repository_factory()
with factory.session() as session:
    previous = session.connection.execute(
        select(research_turns).where(research_turns.c.id == previous_turn_id)
    ).mappings().one()
    project = session.connection.execute(
        select(projects).where(projects.c.id == previous["project_id"])
    ).mappings().one()
    user = session.connection.execute(
        select(users).where(users.c.id == project["created_by"])
    ).mappings().one()
    snapshot = session.connection.execute(
        select(scientific_result_snapshots).where(
            scientific_result_snapshots.c.id == result_snapshot_id
        )
    ).mappings().one()
    assert str(snapshot["research_turn_id"]) == previous_turn_id
current_user = CurrentUser(
    id=str(user["id"]),
    email=str(user["email"]),
    displayName=str(user["display_name"]),
    roles=[],
)
received = ResearchTurnService(factory).receive_turn(
    project_id=str(previous["project_id"]),
    session_id=str(previous["research_session_id"]),
    request=CreateResearchTurnRequest(
        message=question,
        ui_context={"explicit_result_ids": [result_snapshot_id]},
    ),
    current_user=current_user,
)
client = ExistingResultClient()
result = asyncio.run(AgentTurnProcessor(
    repository_factory=factory,
    registries=build_default_agent2_registries(),
    llm_client=client,
    interpretation_queue=RedisRQInterpretationQueue(
        redis_url=redis_url,
        queue_name=queue_name,
    ),
).process(received.turn_id))
print(json.dumps({
    "process_id": __import__("os").getpid(),
    "turn_id": str(received.turn_id),
    "status": result.status,
    "provider_calls": client.calls,
}))
"""


_CONTINUATION_PROCESS = r"""
import asyncio
import json
import sys

from sqlalchemy import select

from mdi_api.database import create_repository_factory
from mdi_api.db import analysis_plans, projects, research_turns, scientific_result_snapshots, users
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
from mdi_api.research_agent.planning.processor import CapabilityPlanningProcessor
from mdi_api.research_agent.registry_validation import build_default_agent2_registries
from mdi_api.research_agent.schemas import CreateResearchTurnRequest
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser
from mdi_api.unit_of_work import transaction_active
from mdi_workers.queue_runtime import RedisRQQueueBackend


class ContinueRdfClient:
    def __init__(self, result_snapshot_id):
        self.result_snapshot_id = result_snapshot_id
        self.calls = 0

    async def generate_structured(self, **kwargs):
        assert transaction_active() is False
        self.calls += 1
        context = kwargs["input_payload"]["research_context"]
        structure = next(
            item for item in context["objects"]
            if item["object_type"] == "structure.crystal"
        )
        # Database result identities are deliberately excluded from provider
        # input; only validated opaque result_N references cross the boundary.
        prior_result = context["results"][0]
        return StructuredLLMResult(
            provider="fake",
            model="phase7-service-continuation",
            parsed={
                "contract_version": "1.0",
                "action": "CONTINUE_ANALYSIS",
                "assistant_message": None,
                "research_objective": "Recompute the prior RDF with an 8 angstrom cutoff.",
                "selected_scope_ref_keys": [structure["ref_key"]],
                "scientific_requirements": [{
                    "requirement_id": "structure.compute_rdf",
                    "criticality": "REQUIRED",
                    "subject_ref_keys": [structure["ref_key"]],
                    "constraints": {"cutoff_angstrom": 8.0},
                }],
                "reusable_result_ref_keys": [prior_result["ref_key"]],
                "clarification": None,
                "confidence": "HIGH",
            },
            latency_ms=1,
            prompt_version="research-orchestrator/1.0",
        )


previous_turn_id, result_snapshot_id, redis_url, execution_queue = sys.argv[1:5]
factory = create_repository_factory()
with factory.session() as session:
    previous = session.connection.execute(
        select(research_turns).where(research_turns.c.id == previous_turn_id)
    ).mappings().one()
    project = session.connection.execute(
        select(projects).where(projects.c.id == previous["project_id"])
    ).mappings().one()
    user = session.connection.execute(
        select(users).where(users.c.id == project["created_by"])
    ).mappings().one()
    snapshot = session.connection.execute(
        select(scientific_result_snapshots).where(
            scientific_result_snapshots.c.id == result_snapshot_id
        )
    ).mappings().one()
    source_ref = next(
        item for item in snapshot["bundle_json"]["source_object_refs"]
        if item["object_type"] == "structure.crystal"
    )
current_user = CurrentUser(
    id=str(user["id"]),
    email=str(user["email"]),
    displayName=str(user["display_name"]),
    roles=[],
)
received = ResearchTurnService(factory).receive_turn(
    project_id=str(previous["project_id"]),
    session_id=str(previous["research_session_id"]),
    request=CreateResearchTurnRequest(
        message="重新用 cutoff 8 Å 算一次。",
        ui_context={
            "explicit_result_ids": [result_snapshot_id],
            "explicit_object_refs": [source_ref],
        },
    ),
    current_user=current_user,
)
client = ContinueRdfClient(result_snapshot_id)
orchestrated = asyncio.run(AgentTurnProcessor(
    repository_factory=factory,
    registries=build_default_agent2_registries(),
    llm_client=client,
).process(received.turn_id))
assert orchestrated.status == "READY_TO_PLAN"
planned = CapabilityPlanningProcessor(
    factory,
    registries=build_default_agent2_registries(),
).process(received.turn_id)
assert planned["status"] == "PLAN_READY"
dispatched = ResearchExecutionDispatcher(
    factory,
    queue=RedisRQQueueBackend(redis_url=redis_url, queue_name=execution_queue),
).dispatch_turn(received.turn_id)
with factory.session() as session:
    turn = session.connection.execute(
        select(research_turns).where(research_turns.c.id == received.turn_id)
    ).mappings().one()
    plan = session.connection.execute(
        select(analysis_plans).where(analysis_plans.c.id == turn["analysis_plan_id"])
    ).mappings().one()
print(json.dumps({
    "process_id": __import__("os").getpid(),
    "turn_id": str(received.turn_id),
    "continuation_of_turn_id": str(turn["continuation_of_turn_id"]),
    "analysis_plan_id": str(turn["analysis_plan_id"]),
    "job_id": str(dispatched.job_id),
    "plan": plan["analysis_plan_json"],
    "provider_calls": client.calls,
}))
"""


@pytest.fixture(scope="module")
def phase7_service_pipeline():
    phase6 = _phase6_module()
    phase5 = phase6._phase5_module()
    phase5_generator = phase5.phase5_service_pipeline.__wrapped__()
    redis_url = os.getenv("MDI_REDIS_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"
    queue_name = f"mdi-agent2-phase7-interpretations-{uuid4().hex[:12]}"
    execution_queue: str | None = None
    result_queue: str | None = None
    previous = {
        key: os.environ.get(key)
        for key in (
            "MDI_AGENT2_INTERPRETATION_ENABLED",
            "MDI_AGENT2_INTERPRETATION_FIXTURE_JSON",
            "MDI_AGENT2_INTERPRETATION_QUEUE_NAME",
            "MDI_QUEUE_BACKEND",
        )
    }
    try:
        phase5_data = next(phase5_generator)
        phase6_cases = phase5_data
        database_url = phase5_data["rdf"].get("database_url") or phase5._phase4_module()._postgres_url()
        environment = phase5._phase4_module()._worker_environment(database_url)
        environment.update({
            "MDI_ENV": "ci",
            "MDI_AGENT2_INTERPRETATION_ENABLED": "1",
            "MDI_AGENT2_INTERPRETATION_QUEUE_NAME": queue_name,
            "MDI_QUEUE_BACKEND": "redis",
            "MDI_REDIS_URL": redis_url,
        })
        engine = create_engine(database_url, future=True, pool_pre_ping=True)
        with engine.connect() as connection:
            before = _counts(connection)

        evidence: dict[str, dict] = {}
        for name, question in (
            ("rdf", "解释刚才 RDF 的第一峰。"),
            ("xrd", "解释刚才 XRD 比较中偏差最大的峰。"),
        ):
            case = phase6_cases[name]
            process = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    _FOLLOW_UP_PROCESS,
                    str(case["turn_id"]),
                    str(case["snapshot_id"]),
                    question,
                    redis_url,
                    queue_name,
                ],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=120,
            )
            assert process.returncode == 0, process.stderr[-6000:]
            follow_up = json.loads(process.stdout.splitlines()[-1])
            assert follow_up["provider_calls"] == 1
            assert follow_up["process_id"] not in {
                os.getpid(),
                int(case["execution_worker_pid"]),
            }
            task = Queue(queue_name, connection=Redis.from_url(redis_url)).fetch_job(
                f"agent2-interpretation-{follow_up['turn_id']}"
            )
            assert task is not None

            environment["MDI_AGENT2_INTERPRETATION_FIXTURE_JSON"] = _safe_interpreter_fixture(case["bundle"])
            worker = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "mdi_workers.worker_entrypoint",
                    queue_name,
                    "--url",
                    redis_url,
                    "--burst",
                    "--max-jobs",
                    "1",
                    "--name",
                    f"agent2-phase7-{name}-{uuid4().hex[:8]}",
                ],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=240,
            )
            assert worker.returncode == 0, worker.stderr[-6000:]
            task = Queue(queue_name, connection=Redis.from_url(redis_url)).fetch_job(
                f"agent2-interpretation-{follow_up['turn_id']}"
            )
            assert task is not None and task.is_finished
            interpretation_pid = int(task.return_value()["process_id"])
            assert interpretation_pid not in {
                os.getpid(),
                int(case["execution_worker_pid"]),
                int(follow_up["process_id"]),
            }
            evidence[name] = {
                **follow_up,
                "interpretation_process_id": interpretation_pid,
                "source_turn_id": str(case["turn_id"]),
                "source_result_snapshot_id": str(case["snapshot_id"]),
            }

        with engine.connect() as connection:
            reuse_after = _counts(connection)
            assert reuse_after == before
            for item in evidence.values():
                turn = connection.execute(
                    select(research_turns).where(
                        research_turns.c.id == item["turn_id"]
                    )
                ).mappings().one()
                assert turn["status"] == "COMPLETED"
                assert turn["assistant_final_message_id"]
                state = connection.execute(
                    select(research_session_states).where(
                        research_session_states.c.session_id
                        == turn["research_session_id"]
                    )
                ).mappings().one()
                assert state["session_id"] == turn["research_session_id"]

            rdf_case = phase6_cases["rdf"]
            old_turn = dict(connection.execute(
                select(research_turns).where(
                    research_turns.c.id == rdf_case["turn_id"]
                )
            ).mappings().one())
            old_plan = dict(connection.execute(
                select(analysis_plans).where(
                    analysis_plans.c.id == old_turn["analysis_plan_id"]
                )
            ).mappings().one())
            old_result = dict(connection.execute(
                select(scientific_result_snapshots).where(
                    scientific_result_snapshots.c.id == rdf_case["snapshot_id"]
                )
            ).mappings().one())
            old_context = dict(connection.execute(
                select(research_context_snapshots).where(
                    research_context_snapshots.c.id == old_turn["context_snapshot_id"]
                )
            ).mappings().one())

        execution_queue = f"mdi-agent2-phase7-execution-{uuid4().hex[:12]}"
        result_queue = f"mdi-agent2-phase7-results-{uuid4().hex[:12]}"
        environment.update({
            "MDI_AGENT2_RESULT_PROJECTION_ENABLED": "1",
            "MDI_AGENT2_RESULT_QUEUE_NAME": result_queue,
        })
        continuation_process = subprocess.run(
            [
                sys.executable,
                "-c",
                _CONTINUATION_PROCESS,
                str(rdf_case["turn_id"]),
                str(rdf_case["snapshot_id"]),
                redis_url,
                execution_queue,
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert continuation_process.returncode == 0, continuation_process.stderr[-6000:]
        continuation = json.loads(continuation_process.stdout.splitlines()[-1])
        assert continuation["provider_calls"] == 1
        assert continuation["continuation_of_turn_id"] == str(rdf_case["turn_id"])
        plan_steps = continuation["plan"]["steps"]
        assert plan_steps[0]["params"]["r_max_angstrom"] == 8.0

        execution_worker = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "mdi_workers.worker_entrypoint",
                execution_queue,
                "--url",
                redis_url,
                "--burst",
                "--max-jobs",
                "1",
                "--name",
                f"agent2-phase7-continuation-execution-{uuid4().hex[:8]}",
            ],
            cwd=ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        continuation["execution_process_id"] = execution_worker.pid
        execution_stdout, execution_stderr = execution_worker.communicate(timeout=240)
        assert execution_worker.returncode == 0, execution_stderr[-6000:]
        execution_task = Queue(
            execution_queue, connection=Redis.from_url(redis_url)
        ).fetch_job(continuation["job_id"])
        assert execution_task is not None and execution_task.is_finished

        result_worker = subprocess.run(
            [
                sys.executable,
                "-m",
                "mdi_workers.worker_entrypoint",
                result_queue,
                "--url",
                redis_url,
                "--burst",
                "--max-jobs",
                "1",
                "--name",
                f"agent2-phase7-continuation-result-{uuid4().hex[:8]}",
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=240,
        )
        assert result_worker.returncode == 0, result_worker.stderr[-6000:]
        with engine.connect() as connection:
            continuation_result = connection.execute(
                select(scientific_result_snapshots).where(
                    scientific_result_snapshots.c.research_turn_id
                    == continuation["turn_id"]
                )
            ).mappings().one()
        continuation["result_snapshot_id"] = str(continuation_result["id"])
        environment["MDI_AGENT2_INTERPRETATION_FIXTURE_JSON"] = _safe_interpreter_fixture(dict(continuation_result["bundle_json"]))
        interpretation_worker = subprocess.run(
            [
                sys.executable,
                "-m",
                "mdi_workers.worker_entrypoint",
                queue_name,
                "--url",
                redis_url,
                "--burst",
                "--max-jobs",
                "1",
                "--name",
                f"agent2-phase7-continuation-interpretation-{uuid4().hex[:8]}",
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=240,
        )
        assert interpretation_worker.returncode == 0, interpretation_worker.stderr[-6000:]

        source_ref = ScientificObjectRef.model_validate(
            next(
                item
                for item in old_result["bundle_json"]["source_object_refs"]
                if item["object_type"] == "structure.crystal"
            )
        )
        factory = RepositoryFactory(engine)
        with factory.session() as session:
            source_version = session.agent2.scientific_objects.get_version(
                source_ref.version_id
            )
        new_version = ScientificObjectService(
            factory, build_default_object_type_registry()
        ).create_version(
            source_ref.object_id,
            object_type=source_ref.object_type,
            object_schema_version=str(source_version["object_schema_version"]),
            source_resource_refs=list(source_version["source_resource_refs_json"]),
            parent_object_version_refs=[],
            normalized_payload_ref=StorageRef.model_validate(
                source_version["normalized_payload_ref_json"]
            ),
            content_hash=str(source_version["content_hash"]),
            semantic_hash=f"{source_version['semantic_hash']}-phase7-v2",
            canonical_metadata={
                **dict(source_version["canonical_metadata_json"]),
                "phase7QualificationVersion": 2,
            },
            created_by_user_id=source_version.get("created_by_user_id"),
        )
        with factory.session() as session:
            logical = session.agent2.scientific_objects.get_object(
                source_ref.object_id
            )
            exact_version = session.agent2.scientific_objects.get_version(
                source_ref.version_id
            )
        effective_relevance = ScientificResultRelevanceEvaluator().evaluate(
            [source_ref],
            objects={str(source_ref.object_id): logical},
            versions={str(source_ref.version_id): exact_version},
        )
        assert effective_relevance.value == "STALE"
        assert str(logical["current_version_id"]) == str(new_version["id"])
        assert str(new_version["id"]) != str(source_ref.version_id)

        stale_process = subprocess.run(
            [
                sys.executable,
                "-c",
                _FOLLOW_UP_PROCESS,
                str(rdf_case["turn_id"]),
                str(rdf_case["snapshot_id"]),
                "解释刚才 RDF 的历史结果。",
                redis_url,
                queue_name,
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert stale_process.returncode == 0, stale_process.stderr[-6000:]
        stale_follow_up = json.loads(stale_process.stdout.splitlines()[-1])
        assert stale_follow_up["provider_calls"] == 1
        environment["MDI_AGENT2_INTERPRETATION_FIXTURE_JSON"] = _safe_interpreter_fixture(rdf_case["bundle"])
        stale_worker = subprocess.run(
            [
                sys.executable,
                "-m",
                "mdi_workers.worker_entrypoint",
                queue_name,
                "--url",
                redis_url,
                "--burst",
                "--max-jobs",
                "1",
                "--name",
                f"agent2-phase7-stale-interpretation-{uuid4().hex[:8]}",
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=240,
        )
        assert stale_worker.returncode == 0, stale_worker.stderr[-6000:]

        with engine.connect() as connection:
            final_counts = _counts(connection)
            continuation_turn = connection.execute(
                select(research_turns).where(
                    research_turns.c.id == continuation["turn_id"]
                )
            ).mappings().one()
            assert continuation_turn["status"] == "COMPLETED"
            assert continuation_turn["assistant_final_message_id"]
            stale_turn = connection.execute(
                select(research_turns).where(
                    research_turns.c.id == stale_follow_up["turn_id"]
                )
            ).mappings().one()
            assert stale_turn["status"] == "COMPLETED"
            stale_interpretation = connection.execute(
                select(agent2_scientific_interpretations).where(
                    agent2_scientific_interpretations.c.research_turn_id
                    == stale_turn["id"]
                )
            ).mappings().one()
            assert str(stale_interpretation["result_snapshot_id"]) == str(
                rdf_case["snapshot_id"]
            )
            stale_message = connection.execute(
                select(messages).where(
                    messages.c.id == stale_turn["assistant_final_message_id"]
                )
            ).mappings().one()
            assert "历史结果" in stale_message["content_summary"]
            assert "不代表当前版本" in stale_message["content_summary"]
            assert dict(connection.execute(
                select(research_turns).where(research_turns.c.id == old_turn["id"])
            ).mappings().one()) == old_turn
            assert dict(connection.execute(
                select(analysis_plans).where(analysis_plans.c.id == old_plan["id"])
            ).mappings().one()) == old_plan
            assert dict(connection.execute(
                select(scientific_result_snapshots).where(
                    scientific_result_snapshots.c.id == old_result["id"]
                )
            ).mappings().one()) == old_result
            assert dict(connection.execute(
                select(research_context_snapshots).where(
                    research_context_snapshots.c.id == old_context["id"]
                )
            ).mappings().one()) == old_context
        assert final_counts["plans"] == reuse_after["plans"] + 1
        assert final_counts["jobs"] == reuse_after["jobs"] + 1
        assert final_counts["tool_calls"] == reuse_after["tool_calls"] + 1
        assert final_counts["artifacts"] > reuse_after["artifacts"]
        assert final_counts["result_snapshots"] == reuse_after["result_snapshots"] + 1
        print(json.dumps({
            "phase7_fresh_process_evidence": {
                "rdf_reuse": "PASS",
                "xrd_reuse": "PASS",
                "orchestration_process_ids": [
                    evidence["rdf"]["process_id"],
                    evidence["xrd"]["process_id"],
                ],
                "interpretation_process_ids": [
                    evidence["rdf"]["interpretation_process_id"],
                    evidence["xrd"]["interpretation_process_id"],
                ],
                "selected_skip": 0,
                "no_recompute": reuse_after == before,
                "continuation": "PASS",
                "continuation_of_turn_id": continuation["continuation_of_turn_id"],
                "continuation_execution_process_id": continuation["execution_process_id"],
                "continuation_result_snapshot_id": continuation["result_snapshot_id"],
                "stale_exact_version": str(source_ref.version_id),
                "stale_current_version": str(new_version["id"]),
                "stale_follow_up": "PASS",
            }
        }, sort_keys=True))
        yield {
            "database_url": database_url,
            "before": before,
            "after": reuse_after,
            "evidence": evidence,
            "continuation": continuation,
            "final_counts": final_counts,
            "stale": {
                **stale_follow_up,
                "exact_version_id": str(source_ref.version_id),
                "current_version_id": str(new_version["id"]),
                "effective_relevance": effective_relevance.value,
            },
        }
        engine.dispose()
    finally:
        try:
            next(phase5_generator)
        except StopIteration:
            pass
        for cleanup_queue_name in (
            queue_name,
            execution_queue,
            result_queue,
        ):
            if cleanup_queue_name:
                Queue(
                    cleanup_queue_name,
                    connection=Redis.from_url(redis_url),
                ).delete(delete_jobs=True)
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@pytest.mark.integration
def test_agent2_phase7_rdf_non_adjacent_result_reuse_in_fresh_processes(
    phase7_service_pipeline,
):
    evidence = phase7_service_pipeline["evidence"]["rdf"]
    assert evidence["turn_id"] != evidence["source_turn_id"]
    assert phase7_service_pipeline["after"] == phase7_service_pipeline["before"]


@pytest.mark.integration
def test_agent2_phase7_xrd_result_reuse_is_not_rdf_specific(
    phase7_service_pipeline,
):
    evidence = phase7_service_pipeline["evidence"]["xrd"]
    assert evidence["turn_id"] != evidence["source_turn_id"]
    assert phase7_service_pipeline["after"] == phase7_service_pipeline["before"]


@pytest.mark.integration
def test_agent2_phase7_rdf_parameter_change_creates_real_continuation(
    phase7_service_pipeline,
):
    continuation = phase7_service_pipeline["continuation"]
    assert continuation["turn_id"] != continuation["continuation_of_turn_id"]
    assert continuation["analysis_plan_id"]
    assert continuation["job_id"]
    assert continuation["result_snapshot_id"]


@pytest.mark.integration
def test_agent2_phase7_stale_result_keeps_exact_historical_version(
    phase7_service_pipeline,
):
    stale = phase7_service_pipeline["stale"]
    assert stale["effective_relevance"] == "STALE"
    assert stale["exact_version_id"] != stale["current_version_id"]
