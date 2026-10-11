"""Research admission, planning and publication for work without a sample."""
from __future__ import annotations

import asyncio
from copy import deepcopy

import pytest
from sqlalchemy import func, select

from mdi_api.db import datasets, data_profiles, jobs, analysis_plans
from mdi_api.infrastructure.scientific_results.service import ScientificResultProjectionService
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.execution.supervisor import ResearchExecutionSupervisor
from mdi_api.research_agent.planning.processor import CapabilityPlanningProcessor
from mdi_api.research_agent.registry_validation import build_default_agent2_registries, validate_agent2_registries
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime
from tests.test_agent2_execution import CaptureQueue, FailOnceQueue
from tests.test_agent2_processor import FakeStructuredClient, decision, foundation, processor, receive, structure


def reference_decision(*, comparison=False, params=None):
    requirement = "reference.compare_elements" if comparison else "reference.periodic_table"
    return decision("ANALYZE", assistant_message="准备绘制参考图。", research_objective="绘制所请求的元素参考图。",
        scientific_requirements=[{"requirement_id": requirement, "criticality": "REQUIRED", "subject_ref_keys": [], "constraints": params or {}}])


@pytest.mark.parametrize("unrelated_material", [False, True])
@pytest.mark.parametrize("comparison", [False, True])
def test_project_research_uses_real_plan_worker_and_result_without_material_inheritance(tmp_path, monkeypatch, unrelated_material, comparison):
    engine, owner, factory, objects, turns = foundation(tmp_path)
    monkeypatch.setattr(QueueWorkerRuntime, "_notify_agent2_progress", staticmethod(lambda job_id: None))
    monkeypatch.setattr(ScientificResultProjectionService, "_enqueue_interpretation", staticmethod(lambda turn_id: None))
    try:
        refs = [structure(objects)] if unrelated_material else []
        params = {"elements": ["C", "Si", "Cu"], "property": "covalent_radius"} if comparison else {"highlight_elements": ["Si"]}
        question = "比较 C、Si、Cu 的共价半径" if comparison else "画完整元素周期表，并高亮 Si"
        turn = receive(turns, owner, question, refs=refs, selected=refs)
        client = FakeStructuredClient([reference_decision(comparison=comparison, params=params)])
        outcome = asyncio.run(processor(factory, client).process(turn.turn_id))
        assert outcome.status == "READY_TO_PLAN"
        with factory.session() as session:
            original_snapshot = deepcopy(session.agent2.research_context_snapshots.get_for_turn(turn.turn_id))
        planner = CapabilityPlanningProcessor(factory)
        planned = planner.process(turn.turn_id)
        assert planned["status"] == "PLAN_READY", planned
        assert planner.process(turn.turn_id)["status"] == "NOOP"
        with factory.session() as session:
            stored = session.repositories.analysis_plans.get_plan(planned["analysis_plan_id"])
            assert stored["datasetId"] is None and stored["profileId"] is None
            plan = stored["analysisPlan"]
            assert plan["schemaVersion"] == "0.4" and plan["projectId"] == "project"
            assert plan["steps"][0]["inputRefs"] == []
            assert all(plan["steps"][0]["params"][key] == value for key, value in params.items())
            assert session.agent2.research_context_snapshots.get_for_turn(turn.turn_id) == original_snapshot
        queue = CaptureQueue()
        dispatcher = ResearchExecutionDispatcher(factory, queue=queue)
        dispatched = dispatcher.dispatch_turn(turn.turn_id)
        assert dispatcher.dispatch_turn(turn.turn_id).job_id == dispatched.job_id
        runtime = QueueWorkerRuntime(repository_factory=factory, registry=load_manifests(), artifact_root=tmp_path / "artifacts")
        assert runtime.handle_job(dispatched.job_id).status == "completed"
        progress = ResearchExecutionSupervisor(factory).sync_for_job(dispatched.job_id)
        assert progress.status.value == "RESULT_PENDING"
        result_service = ScientificResultProjectionService(factory, artifact_loader=lambda artifact: (
            runtime.artifact_storage.get_json(artifact["storageKey"]) if artifact["type"].endswith("_json") else None))
        result = result_service.project_turn(turn.turn_id)
        bundle = result["bundle_json"]
        assert bundle["source_object_refs"] == [] and bundle["provenance"]["source_object_version_ids"] == []
        assert bundle["provenance"]["execution_scope"] == "PROJECT"
        assert len(bundle["figures"]) == len(bundle["tables"]) == 1
        assert bundle["methods"][0]["source_object_refs"] == []
        assert bundle["methods"][0]["parameters"]["property"] == ("covalent_radius" if comparison else "atomic_number")
        # A complete periodic table has 240 facts, beyond a report caption's
        # 32-reference bound. The saved evidence graph must keep all support.
        from mdi_api.application.scientific_reports.grounded import DeterministicScientificReportComposer
        from mdi_api.application.scientific_reports.grounding import ReportGroundingValidator
        from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
        scientific_bundle = ScientificResultBundle.model_validate(bundle)
        count = next(fact for fact in scientific_bundle.facts if fact.predicate == "reference.element_count")
        version = next(fact for fact in scientific_bundle.facts if fact.predicate == "reference.version")
        interpretation = {"interpretation": {"primary_findings": [{
            "finding_id": "finding.reference_count", "statement": f"参考版本 {version.value}，参考图包含 {count.value} 种元素。",
            "scope": f"平台参考资料（版本 {version.value}），参考覆盖 H–Cm（1–96）",
            "fact_refs": [count.fact_id, version.fact_id], "evidence_refs": [],
        }]}}
        report = DeterministicScientificReportComposer().compose(
            bundle=scientific_bundle, interpretation=interpretation, relevance_status="CURRENT")
        assert ReportGroundingValidator().validate(report, bundle=scientific_bundle, interpretation=interpretation) == []
        figure = report.primary_figures[0]
        support = set(figure.fact_refs) | {ref for evidence in scientific_bundle.evidence
            if evidence.evidence_id in figure.evidence_refs for ref in evidence.supports_fact_refs}
        assert set(scientific_bundle.figures[0].fact_refs).issubset(support)
        assert len(figure.fact_refs) <= 32 and len(figure.evidence_refs) <= 32
        assert "参考" in report.method_summary and "参考" in report.summary
        assert "1–96" not in report.summary
        assert scientific_bundle.model_dump(mode="json") == bundle
        assert result_service.project_turn(turn.turn_id)["id"] == result["id"]
        with engine.connect() as connection:
            assert connection.scalar(select(func.count()).select_from(datasets)) == 0
            assert connection.scalar(select(func.count()).select_from(data_profiles)) == 0
            assert connection.scalar(select(func.count()).select_from(analysis_plans)) == 1
            assert connection.scalar(select(func.count()).select_from(jobs)) == 1
    finally:
        engine.dispose()


def test_project_reference_recovers_same_job_after_queue_publish_failure(tmp_path):
    from mdi_api.research_agent.execution.errors import ExecutionQueuePublishFailed
    engine, owner, factory, _objects, turns = foundation(tmp_path)
    try:
        turn = receive(turns, owner, "绘制周期表")
        assert asyncio.run(processor(factory, FakeStructuredClient([reference_decision()])).process(turn.turn_id)).status == "READY_TO_PLAN"
        assert CapabilityPlanningProcessor(factory).process(turn.turn_id)["status"] == "PLAN_READY"
        queue = FailOnceQueue()
        dispatcher = ResearchExecutionDispatcher(factory, queue=queue)
        with pytest.raises(ExecutionQueuePublishFailed):
            dispatcher.dispatch_turn(turn.turn_id)
        recovered = dispatcher.dispatch_turn(turn.turn_id)
        assert recovered.queued and queue.ids == [recovered.job_id, recovered.job_id]
        with engine.connect() as connection:
            assert connection.scalar(select(func.count()).select_from(jobs)) == 1
    finally:
        engine.dispose()


def test_project_reference_registry_remains_executable_and_scientific_qualification_is_current():
    from mdi_api.research_agent.capabilities.quality_evidence import get_capability_quality_evidence, scientific_contract_fingerprint
    registries = build_default_agent2_registries()
    validate_agent2_registries(registries, load_manifests())
    for key in ["reference.periodic_table", "reference.compare_elements"]:
        capability = registries.capabilities.require(key)
        assert capability.input_slots == []
        assert registries.requirements.require(key).requires_material is False
        assert scientific_contract_fingerprint(capability) == get_capability_quality_evidence(key).qualified_contract_fingerprint


def test_project_reference_cancel_before_worker_never_publishes_artifacts(tmp_path, monkeypatch):
    engine, owner, factory, _objects, turns = foundation(tmp_path)
    monkeypatch.setattr(QueueWorkerRuntime, "_notify_agent2_progress", staticmethod(lambda job_id: None))
    try:
        turn = receive(turns, owner, "绘制周期表")
        assert asyncio.run(processor(factory, FakeStructuredClient([reference_decision()])).process(turn.turn_id)).status == "READY_TO_PLAN"
        assert CapabilityPlanningProcessor(factory).process(turn.turn_id)["status"] == "PLAN_READY"
        dispatched = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn.turn_id)
        supervisor = ResearchExecutionSupervisor(factory)
        assert supervisor.request_cancel(turn.turn_id)["status"] == "CANCELING"
        runtime = QueueWorkerRuntime(repository_factory=factory, registry=load_manifests(), artifact_root=tmp_path / "artifacts")
        assert runtime.handle_job(dispatched.job_id).status == "cancelled"
        assert supervisor.sync_for_job(dispatched.job_id).status.value == "CANCELED"
        with factory.session() as session:
            assert session.repositories.artifacts.list_for_job(dispatched.job_id) == []
    finally:
        engine.dispose()
