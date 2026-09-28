from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
from uuid import uuid4

import pytest
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, insert, inspect
from sqlalchemy.engine import make_url

from mdi_api.db import organizations, projects, sessions, users
from mdi_api.research_agent.schemas import CreateResearchTurnRequest, ResearchTurnStatus
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import ScientificObjectKind, StorageRef
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.unit_of_work import RepositoryFactory


def postgres_url() -> str:
    value = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not value or not make_url(value).get_backend_name().startswith("postgresql"):
        pytest.skip("A PostgreSQL MDI_TEST_DATABASE_URL or DATABASE_URL is required")
    return value


@pytest.mark.integration
def test_agent2_postgresql_migration_concurrency_and_receive_boundary():
    url = postgres_url()
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", url)
    alembic_command.upgrade(config, "head")
    engine = create_engine(url, future=True, pool_pre_ping=True)
    inspector = inspect(engine)
    assert {
        "scientific_objects", "scientific_object_versions", "scientific_object_relationships",
        "research_turns", "research_context_snapshots", "research_turn_events", "scientific_result_snapshots",
    }.issubset(set(inspector.get_table_names()))
    assert "idx_research_turns_status_updated" in {item["name"] for item in inspector.get_indexes("research_turns")}

    suffix = uuid4().hex[:12]
    owner = CurrentUser(id=f"agent2-owner-{suffix}", email=f"agent2-{suffix}@example.invalid", displayName="Agent2 Owner", roles=[])
    org_id = f"agent2-org-{suffix}"
    project_id = f"agent2-project-{suffix}"
    session_id = f"agent2-session-{suffix}"
    with engine.begin() as connection:
        connection.execute(insert(users), {"id": owner.id, "email": owner.email, "display_name": owner.displayName, "is_active": True})
        connection.execute(insert(organizations), {"id": org_id, "name": f"Agent2 {suffix}"})
        connection.execute(insert(projects), {"id": project_id, "organization_id": org_id, "name": f"Agent2 {suffix}", "created_by": owner.id})
        connection.execute(insert(sessions), {"id": session_id, "project_id": project_id, "mode": "project", "status": "active", "created_by": owner.id})

    factory = RepositoryFactory(engine)
    objects = ScientificObjectService(factory, build_default_object_type_registry())
    logical = objects.create_object(
        project_id=project_id, kind=ScientificObjectKind.STRUCTURE,
        object_type="structure.crystal", display_name="Concurrent structure", created_by_user_id=owner.id,
    )

    def add_version(index: int):
        return objects.create_version(
            logical["id"], object_type="structure.crystal", object_schema_version="1.0",
            source_resource_refs=[{"scope": "system_fixture", "resource_id": f"fixture-{index}"}],
            parent_object_version_refs=[],
            normalized_payload_ref=StorageRef(storage_backend="minio", object_key=f"agent2/{suffix}/{index}.json", checksum=f"checksum-{index}"),
            content_hash=f"content-{suffix}-{index}", semantic_hash=f"semantic-{suffix}-{index}", canonical_metadata={},
            created_by_user_id=owner.id,
        )

    with ThreadPoolExecutor(max_workers=4) as pool:
        versions = list(pool.map(add_version, range(4)))
    assert sorted(item["version_no"] for item in versions) == [1, 2, 3, 4]

    turns = ResearchTurnService(factory)
    with ThreadPoolExecutor(max_workers=8) as pool:
        received = list(pool.map(
            lambda index: turns.receive_turn(
                project_id=project_id, session_id=session_id,
                request=CreateResearchTurnRequest(message=f"Question {index}"), current_user=owner,
            ),
            range(8),
        ))
    assert sorted(item.sequence_no for item in received) == list(range(1, 9))
    first = received[0]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(
            turns.transition,
            turn_id=first.turn_id,
            expected_status=ResearchTurnStatus.RECEIVED,
            expected_version=1,
            target_status=ResearchTurnStatus.RESOLVING_CONTEXT,
        ) for _ in range(2)]
    outcomes = []
    for future in futures:
        try:
            outcomes.append(future.result()["status"])
        except Exception as exc:
            outcomes.append(type(exc).__name__)
    assert sorted(outcomes) == ["ConcurrentTurnModification", "RESOLVING_CONTEXT"]
    engine.dispose()
