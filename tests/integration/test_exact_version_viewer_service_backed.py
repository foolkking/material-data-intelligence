from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import UUID

import pytest
from sqlalchemy import create_engine, func, select

from mdi_api.db import analysis_plans, artifacts, jobs, projects, research_context_snapshots, research_turns, scientific_result_snapshots, tool_calls
from mdi_api.research_agent.schemas import CreateResearchTurnRequest, ResearchTurnUIContext, ScientificSelectionContext
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser
from mdi_api.unit_of_work import RepositoryFactory


ROOT = Path(__file__).resolve().parents[2]


def _phase6_module():
    path = ROOT / "tests" / "integration" / "test_interpretation_service_backed.py"
    spec = importlib.util.spec_from_file_location("agent2_phase6_viewer_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _scientific_counts(connection) -> dict[str, int]:
    return {
        "plans": connection.execute(select(func.count()).select_from(analysis_plans)).scalar_one(),
        "jobs": connection.execute(select(func.count()).select_from(jobs)).scalar_one(),
        "tool_calls": connection.execute(select(func.count()).select_from(tool_calls)).scalar_one(),
        "artifacts": connection.execute(select(func.count()).select_from(artifacts)).scalar_one(),
        "result_snapshots": connection.execute(select(func.count()).select_from(scientific_result_snapshots)).scalar_one(),
    }


_FRESH_VIEWER_PROCESS = r"""
import json
import os
import sys
from uuid import UUID
from mdi_api.artifact_storage import create_artifact_storage_from_settings
from mdi_api.config import load_settings
from mdi_api.database import create_repository_factory
from mdi_api.scientific_viewers import ScientificViewerProjectionService, build_scientific_viewer_registry

projection = ScientificViewerProjectionService(
    create_repository_factory(),
    create_artifact_storage_from_settings(load_settings()),
    build_scientific_viewer_registry(),
).project(UUID(sys.argv[1]), UUID(sys.argv[2]))
print(json.dumps({
    "process_id": os.getpid(),
    "object_id": str(projection.object_id),
    "version_id": str(projection.version_id),
    "object_type": projection.object_type,
    "renderer_key": projection.viewer.renderer_key,
    "payload_status": projection.payload_status,
    "payload_bytes": projection.payload_bytes,
    "omitted_item_count": projection.omitted_item_count,
}))
"""


@pytest.fixture(scope="module")
def phase9_service_pipeline():
    phase6 = _phase6_module()
    generator = phase6.phase6_service_pipeline.__wrapped__()
    try:
        phase6_data = next(generator)
        database_url = phase6_data["database_url"]
        phase5 = phase6._phase5_module()
        environment = phase5._phase4_module()._worker_environment(database_url)
        engine = create_engine(database_url, future=True, pool_pre_ping=True)
        factory = RepositoryFactory(engine)
        evidence: dict[str, dict] = {}

        with engine.connect() as connection:
            before = _scientific_counts(connection)

        for family in ("rdf", "xrd"):
            case = phase6_data["cases"][family]
            source = case["bundle"]["source_object_refs"][0]
            process = subprocess.run(
                [sys.executable, "-c", _FRESH_VIEWER_PROCESS, source["object_id"], source["version_id"]],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=90,
            )
            assert process.returncode == 0, process.stderr[-5000:]
            projected = json.loads(process.stdout.splitlines()[-1])
            assert projected["process_id"] != os.getpid()
            assert projected["object_id"] == source["object_id"]
            assert projected["version_id"] == source["version_id"]
            assert projected["payload_status"] == "READY"
            evidence[family] = {**projected, "result_id": str(case["snapshot_id"])}

        rdf_case = phase6_data["cases"]["rdf"]
        rdf_source = rdf_case["bundle"]["source_object_refs"][0]
        with factory.session() as session:
            parent_turn = session.connection.execute(
                select(research_turns).where(research_turns.c.id == UUID(str(rdf_case["turn_id"])))
            ).mappings().one()
            project = session.connection.execute(
                select(projects).where(projects.c.id == parent_turn["project_id"])
            ).mappings().one()

        current_user = CurrentUser(
            id=str(project["created_by"]),
            email="phase9-service@local.invalid",
            displayName="Phase 9 Service User",
            roles=[],
        )
        object_ref = {
            "object_id": rdf_source["object_id"],
            "version_id": rdf_source["version_id"],
            "project_id": rdf_source["project_id"],
            "object_type": rdf_source["object_type"],
            "display_name": rdf_source.get("display_name"),
        }
        turns = ResearchTurnService(factory)
        follow_up = turns.receive_turn(
            project_id=str(parent_turn["project_id"]),
            session_id=str(parent_turn["research_session_id"]),
            current_user=current_user,
            request=CreateResearchTurnRequest(
                message="分析当前科学视图中的选择。",
                ui_context=ResearchTurnUIContext(
                    active_object_refs=[object_ref],
                    selection_refs=[object_ref],
                    scientific_selections=[ScientificSelectionContext(
                        object_ref=object_ref,
                        viewer_id=evidence["rdf"]["renderer_key"],
                        selection_type="RDF_PEAK",
                        semantic_locator={"peak_id": "first_peak", "field_locator": "$.peaks[0]"},
                        display_label="RDF 第一峰",
                        evidence_locator={"field_locator": "$.peaks[0]"},
                    )],
                ),
            ),
        )
        turns.resolve_turn_context_stub(follow_up.turn_id)
        with engine.connect() as connection:
            snapshot = connection.execute(
                select(research_context_snapshots).where(research_context_snapshots.c.research_turn_id == follow_up.turn_id)
            ).mappings().one()
            after = _scientific_counts(connection)
        assert after == before
        assert str(snapshot["scientific_selections_json"][0]["object_ref"]["version_id"]) == rdf_source["version_id"]
        assert snapshot["scientific_selections_json"][0]["semantic_locator"]["peak_id"] == "first_peak"

        yield {
            "before": before,
            "after": after,
            "evidence": evidence,
            "selection_turn_id": str(follow_up.turn_id),
            "selection_snapshot_id": str(snapshot["id"]),
        }
        engine.dispose()
    finally:
        try:
            next(generator)
        except StopIteration:
            pass


@pytest.mark.integration
def test_agent2_phase9_exact_version_viewers_load_in_fresh_process(phase9_service_pipeline):
    assert phase9_service_pipeline["evidence"]["rdf"]["version_id"]
    assert phase9_service_pipeline["evidence"]["xrd"]["version_id"]
    assert phase9_service_pipeline["evidence"]["rdf"]["process_id"] != phase9_service_pipeline["evidence"]["xrd"]["process_id"]


@pytest.mark.integration
def test_agent2_phase9_selection_is_durable_and_zero_computation(phase9_service_pipeline):
    assert phase9_service_pipeline["selection_turn_id"]
    assert phase9_service_pipeline["selection_snapshot_id"]
    assert phase9_service_pipeline["after"] == phase9_service_pipeline["before"]


@pytest.mark.integration
def test_agent2_phase9_dedicated_selection_has_no_skips(phase9_service_pipeline):
    assert set(phase9_service_pipeline["evidence"]) == {"rdf", "xrd"}
