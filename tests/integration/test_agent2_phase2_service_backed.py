from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import threading
from typing import Any
from uuid import uuid4

import pytest
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from redis import Redis
from rq import Queue
from sqlalchemy import create_engine, func, insert, inspect, select
from sqlalchemy.engine import make_url

from mdi_api.db import (
    analysis_plans,
    jobs,
    organizations,
    projects,
    research_context_snapshots,
    research_turn_decisions,
    sessions,
    tool_calls,
    users,
)
from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
from mdi_api.research_agent.orchestration.queue import RedisRQAgentTurnQueue
from mdi_api.research_agent.registry_validation import build_default_agent2_registries
from mdi_api.research_agent.schemas import CreateResearchTurnRequest
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import ScientificObjectKind, ScientificObjectRef, StorageRef
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.unit_of_work import RepositoryFactory, transaction_active


class ServiceFakeStructuredClient:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.calls = 0

    async def generate_structured(self, **_kwargs: Any) -> StructuredLLMResult:
        assert transaction_active() is False
        await asyncio.sleep(0.03)
        with self._lock:
            self.calls += 1
        return StructuredLLMResult(
            provider="fake",
            model="service-fixture",
            parsed={
                "contract_version": "1.0",
                "action": "ANALYZE",
                "assistant_message": "我会准备当前结构的 RDF 分析。",
                "research_objective": "计算当前结构的径向分布函数。",
                "selected_scope_ref_keys": ["obj_1"],
                "scientific_requirements": [{
                    "requirement_id": "structure.compute_rdf",
                    "criticality": "REQUIRED",
                    "subject_ref_keys": ["obj_1"],
                    "constraints": {},
                }],
                "reusable_result_ref_keys": [],
                "clarification": None,
                "confidence": "HIGH",
            },
            latency_ms=30,
            prompt_version="research-orchestrator/1.0",
        )


def _postgres_url() -> str:
    value = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not value or not make_url(value).get_backend_name().startswith("postgresql"):
        pytest.skip("A PostgreSQL MDI_TEST_DATABASE_URL or DATABASE_URL is required")
    return value


@pytest.mark.integration
def test_agent2_phase2_postgresql_orchestration_and_redis_wakeup_boundary():
    url = _postgres_url()
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", url)
    alembic_command.upgrade(config, "head")
    engine = create_engine(url, future=True, pool_pre_ping=True)
    assert "research_turn_decisions" in inspect(engine).get_table_names()

    suffix = uuid4().hex[:12]
    owner = CurrentUser(
        id=f"agent2-phase2-owner-{suffix}",
        email=f"agent2-phase2-{suffix}@example.invalid",
        displayName="Agent2 Phase2 Owner",
        roles=[],
    )
    org_id = f"agent2-phase2-org-{suffix}"
    project_id = f"agent2-phase2-project-{suffix}"
    session_id = f"agent2-phase2-session-{suffix}"
    with engine.begin() as connection:
        connection.execute(insert(users), {"id": owner.id, "email": owner.email, "display_name": owner.displayName, "is_active": True})
        connection.execute(insert(organizations), {"id": org_id, "name": f"Agent2 Phase2 {suffix}"})
        connection.execute(insert(projects), {"id": project_id, "organization_id": org_id, "name": f"Agent2 Phase2 {suffix}", "created_by": owner.id})
        connection.execute(insert(sessions), {"id": session_id, "project_id": project_id, "mode": "project", "status": "active", "created_by": owner.id})

    factory = RepositoryFactory(engine)
    objects = ScientificObjectService(factory, build_default_object_type_registry())
    logical = objects.create_object(
        project_id=project_id,
        kind=ScientificObjectKind.STRUCTURE,
        object_type="structure.crystal",
        display_name="Service-backed structure",
        created_by_user_id=owner.id,
    )
    version = objects.create_version(
        logical["id"],
        object_type="structure.crystal",
        object_schema_version="1.0",
        source_resource_refs=[{"scope": "system_fixture", "resource_id": suffix}],
        parent_object_version_refs=[],
        normalized_payload_ref=StorageRef(
            storage_backend="minio",
            object_key=f"agent2-phase2/{suffix}.json",
            checksum=f"checksum-{suffix}",
        ),
        content_hash=f"content-{suffix}",
        semantic_hash=f"semantic-{suffix}",
        canonical_metadata={"summary": "Authorized service-backed structure"},
        created_by_user_id=owner.id,
    )
    ref = ScientificObjectRef(
        object_id=logical["id"],
        version_id=version["id"],
        project_id=project_id,
        object_type="structure.crystal",
        display_name=logical["display_name"],
    )
    turns = ResearchTurnService(factory)
    with engine.connect() as connection:
        execution_counts_before = (
            connection.execute(select(func.count()).select_from(analysis_plans)).scalar_one(),
            connection.execute(select(func.count()).select_from(jobs)).scalar_one(),
            connection.execute(select(func.count()).select_from(tool_calls)).scalar_one(),
        )
    received = turns.receive_turn(
        project_id=project_id,
        session_id=session_id,
        request=CreateResearchTurnRequest(
            message="计算这个结构的 RDF。",
            ui_context={"active_object_refs": [ref], "selection_refs": []},
        ),
        current_user=owner,
    )
    fake = ServiceFakeStructuredClient()
    processor = AgentTurnProcessor(
        repository_factory=factory,
        registries=build_default_agent2_registries(),
        llm_client=fake,
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _index: asyncio.run(processor.process(received.turn_id)), range(2)))
    assert sorted(item.outcome for item in outcomes) == ["APPLIED", "NOOP"]
    assert fake.calls == 1
    view = turns.get_turn(received.turn_id, owner)
    assert view["status"] == "READY_TO_PLAN" and view["action"] == "ANALYZE"
    with engine.connect() as connection:
        assert connection.execute(select(func.count()).select_from(research_context_snapshots).where(
            research_context_snapshots.c.research_turn_id == received.turn_id
        )).scalar_one() == 1
        assert connection.execute(select(func.count()).select_from(research_turn_decisions).where(
            research_turn_decisions.c.research_turn_id == received.turn_id
        )).scalar_one() == 1
        execution_counts_after = (
            connection.execute(select(func.count()).select_from(analysis_plans)).scalar_one(),
            connection.execute(select(func.count()).select_from(jobs)).scalar_one(),
            connection.execute(select(func.count()).select_from(tool_calls)).scalar_one(),
        )
    assert execution_counts_after == execution_counts_before

    redis_url = os.getenv("MDI_REDIS_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"
    queue_name = f"mdi-agent2-phase2-{suffix}"
    queued = RedisRQAgentTurnQueue(redis_url=redis_url, queue_name=queue_name).enqueue_turn(received.turn_id)
    queue = Queue(queue_name, connection=Redis.from_url(redis_url))
    rq_job = queue.fetch_job(f"agent2-turn-{received.turn_id}")
    assert queued.enqueued is True and rq_job is not None
    assert rq_job.args == (str(received.turn_id),)
    assert rq_job.kwargs == {}
    rq_job.delete()
    engine.dispose()
