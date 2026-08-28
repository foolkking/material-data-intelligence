from __future__ import annotations

import asyncio
import json
import os
from uuid import UUID

import pytest
from sqlalchemy import create_engine, func, insert, select
from sqlalchemy.pool import StaticPool

from mdi_api.db import analysis_plans, artifacts, jobs, metadata, organizations, projects, scientific_result_snapshots, sessions, tool_calls, users
from mdi_api.research_agent.schemas import CreateResearchTurnRequest
from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.llm.structured_client import DeepSeekStructuredLLMClient
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser
from mdi_api.scientific_reports.assembler import ReportComposerInputAssembler
from mdi_api.scientific_reports.client import DeepSeekReportComposerClient, FakeStructuredReportComposerClient
from mdi_api.scientific_reports.grounded import DeterministicScientificReportComposer
from mdi_api.scientific_reports.grounding import ReportGroundingValidator
from mdi_api.scientific_reports.schemas import ReportContextBundle, ScientificReportOutput
from mdi_api.scientific_reports.service import ScientificReportError, ScientificReportService
from mdi_api.scientific_results.schemas import ScientificResultBundle
from mdi_api.unit_of_work import RepositoryFactory
from mdi_llm import DeepSeekProvider


OBJECT_ID = UUID("11111111-1111-4111-8111-111111111111")
VERSION_ID = UUID("22222222-2222-4222-8222-222222222222")
TURN_ID = UUID("33333333-3333-4333-8333-333333333333")
RESULT_ID = UUID("44444444-4444-4444-8444-444444444444")


def _bundle(*, execution_status: str = "SUCCESS", relevance_status: str = "CURRENT") -> ScientificResultBundle:
    source = {
        "object_id": str(OBJECT_ID),
        "version_id": str(VERSION_ID),
        "project_id": "project_1",
        "object_type": "structure.crystal",
        "display_name": "LiFePO4",
    }
    return ScientificResultBundle.model_validate({
        "schema_version": "1.0",
        "result_id": str(RESULT_ID),
        "project_id": "project_1",
        "research_session_id": "session_1",
        "research_turn_id": str(TURN_ID),
        "research_question": "LiFePO4 的 RDF 第一峰在哪里？",
        "source_object_refs": [source],
        "execution_status": execution_status,
        "relevance_status": relevance_status,
        "result_items": [{
            "id": "rdf.primary",
            "result_type": "structure.rdf",
            "role": "PRIMARY",
            "title": "LiFePO4 径向分布函数",
            "artifact_ids": ["artifact_private_123"],
            "scientific_object_refs": [source],
            "fact_refs": ["rdf.first_peak_position"],
            "evidence_refs": ["evidence.rdf_curve"],
            "viewer_binding": "rdf",
        }],
        "facts": [{
            "fact_id": "rdf.first_peak_position",
            "predicate": "first_peak_position",
            "subject_ref": str(OBJECT_ID),
            "value": 2.84,
            "unit": "Å",
            "uncertainty": None,
            "source": {
                "tool_call_id": "toolcall_private_123",
                "artifact_id": "artifact_private_123",
                "artifact_locator": "/summary/first_peak_position",
            },
        }],
        "figures": [{
            "figure_id": "figure.rdf_curve",
            "figure_type": "rdf_curve",
            "role": "PRIMARY",
            "title": "径向分布函数",
            "caption_seed": "RDF curve",
            "artifact_ids": ["artifact_private_123"],
            "fact_refs": ["rdf.first_peak_position"],
            "evidence_refs": ["evidence.rdf_curve"],
            "viewer_binding": "rdf",
        }],
        "tables": [],
        "output_object_refs": [],
        "evidence": [{
            "evidence_id": "evidence.rdf_curve",
            "evidence_type": "structured_curve",
            "artifact_id": "artifact_private_123",
            "tool_call_id": "toolcall_private_123",
            "artifact_locator": "/r,/g_r",
            "scientific_object_refs": [source],
            "supports_fact_refs": ["rdf.first_peak_position"],
            "supports_result_item_refs": ["rdf.primary"],
        }],
        "methods": [{
            "method_id": "method.rdf",
            "capability_id": "structure.rdf",
            "capability_version": "1.0",
            "tool_id": "structure.rdf",
            "tool_version": "1.0",
            "parameters": {"r_max_angstrom": 8.0},
            "source_object_refs": [source],
        }],
        "limitations": [{"limitation_id": "limitation.rdf", "code": "FINITE_CUTOFF", "message": "结果受有限截断范围约束。", "source_ref": "method.rdf"}],
        "warnings": [],
        "provenance": {
            "research_turn_id": str(TURN_ID),
            "job_id": "job_private_123",
            "analysis_plan_id": "plan_private_123",
            "source_object_version_ids": [str(VERSION_ID)],
            "tool_call_ids": ["toolcall_private_123"],
            "artifact_ids": ["artifact_private_123"],
            "projector_ids": ["agent2.structure.rdf"],
        },
        "projection_version": "agent2-result/1.0",
    })


def _interpretation() -> dict:
    return {
        "interpretation": {
            "contract_version": "1.0",
            "title": "LiFePO4 RDF 第一配位峰分析",
            "answer_lead": "RDF 第一峰位于 2.84 Å。",
            "primary_findings": [{
                "finding_id": "finding.rdf_peak",
                "statement": "RDF 第一峰位于 2.84 Å。",
                "importance": "HIGH",
                "confidence": "HIGH",
                "fact_refs": ["rdf.first_peak_position"],
                "evidence_refs": ["evidence.rdf_curve"],
                "result_item_refs": ["rdf.primary"],
            }],
            "supporting_findings": [],
            "limitations": ["结果受有限截断范围约束。"],
            "primary_result_refs": ["rdf.primary"],
            "supporting_result_refs": [],
            "follow_up_suggestions": [],
        },
        "message": "RDF 第一峰位于 2.84 Å。",
        "execution_status": "SUCCESS",
    }


def _report() -> ScientificReportOutput:
    return DeterministicScientificReportComposer().compose(bundle=_bundle(), interpretation=_interpretation(), relevance_status="CURRENT")


def _xrd_bundle_and_interpretation() -> tuple[ScientificResultBundle, dict]:
    payload = _bundle().model_dump(mode="json")
    payload["research_question"] = "实验与理论 XRD 匹配了多少个峰？"
    payload["result_items"][0].update({"id": "xrd.comparison", "result_type": "diffraction.experimental_theoretical_comparison", "title": "实验与理论 XRD 峰比较", "fact_refs": ["xrd.matched_peak_count"], "evidence_refs": ["evidence.xrd"]})
    payload["facts"][0].update({"fact_id": "xrd.matched_peak_count", "predicate": "matched_peak_count", "value": 17, "unit": None})
    payload["figures"][0].update({"figure_id": "figure.xrd_comparison", "figure_type": "xrd_comparison", "title": "实验与理论 XRD 图谱", "fact_refs": ["xrd.matched_peak_count"], "evidence_refs": ["evidence.xrd"]})
    payload["evidence"][0].update({"evidence_id": "evidence.xrd", "supports_fact_refs": ["xrd.matched_peak_count"], "supports_result_item_refs": ["xrd.comparison"]})
    payload["methods"][0].update({"method_id": "method.xrd", "capability_id": "diffraction.experimental_theoretical_comparison"})
    payload["limitations"][0]["source_ref"] = "method.xrd"
    interpretation = _interpretation()
    data = interpretation["interpretation"]
    data.update({"title": "实验与理论 XRD 峰比较", "answer_lead": "实验与理论图谱匹配了 17 个峰。", "primary_result_refs": ["xrd.comparison"]})
    data["primary_findings"][0].update({"finding_id": "finding.xrd_matches", "statement": "实验与理论图谱匹配了 17 个峰。", "fact_refs": ["xrd.matched_peak_count"], "evidence_refs": ["evidence.xrd"], "result_item_refs": ["xrd.comparison"]})
    return ScientificResultBundle.model_validate(payload), interpretation


def test_grounded_rdf_report_and_opaque_provider_boundary() -> None:
    bundle = _bundle()
    report = _report()
    assert ReportGroundingValidator().validate(report, bundle=bundle, interpretation=_interpretation()) == []
    envelope, first = ReportComposerInputAssembler().assemble(bundle=bundle, interpretation=_interpretation(), relevance_status="CURRENT")
    assert ReportContextBundle.model_validate(envelope).contract_version == "1.0"
    _, second = ReportComposerInputAssembler().assemble(bundle=bundle, interpretation=_interpretation(), relevance_status="CURRENT")
    serialized = json.dumps(envelope, sort_keys=True)
    assert first == second
    assert "artifact_private_123" not in serialized
    assert "toolcall_private_123" not in serialized
    assert str(OBJECT_ID) not in serialized
    assert str(VERSION_ID) not in serialized
    assert "raw_artifact" not in serialized
    assert "method.rdf" not in json.dumps(envelope["result"]["limitations"], sort_keys=True)
    assert envelope["opaque_refs"]["limitations"] == ["limitation.rdf"]


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("finding_refs", ["finding.unknown"], "unknown reference"),
        ("evidence_refs", ["evidence.unknown"], "unknown reference"),
        ("fact_refs", ["fact.unknown"], "unknown reference"),
    ],
)
def test_unknown_finding_fact_and_evidence_refs_are_rejected(field: str, value: list[str], error: str) -> None:
    payload = _report().model_dump(mode="json")
    payload["main_findings"][0][field] = value
    report = ScientificReportOutput.model_validate(payload)
    assert any(error in item for item in ReportGroundingValidator().validate(report, bundle=_bundle(), interpretation=_interpretation()))


def test_unknown_figure_and_result_item_refs_are_rejected() -> None:
    payload = _report().model_dump(mode="json")
    payload["primary_figures"][0]["figure_ref"] = "figure.unknown"
    payload["supporting_results"] = [{"result_item_ref": "result.unknown", "description": "未知结果"}]
    errors = ReportGroundingValidator().validate(ScientificReportOutput.model_validate(payload), bundle=_bundle(), interpretation=_interpretation())
    assert any("unknown figure" in item for item in errors)
    assert any("unknown result item" in item for item in errors)


@pytest.mark.parametrize(
    "statement",
    ["RDF 第一峰位于 3.21 Å。", "RDF 第一峰位于 0.284 nm。"],
)
def test_numeric_invention_and_unit_substitution_are_rejected(statement: str) -> None:
    payload = _report().model_dump(mode="json")
    payload["main_findings"][0]["statement"] = statement
    errors = ReportGroundingValidator().validate(ScientificReportOutput.model_validate(payload), bundle=_bundle(), interpretation=_interpretation())
    assert errors


def test_numeric_presentation_rounding_remains_grounded() -> None:
    payload = _report().model_dump(mode="json")
    payload["summary"] = "The measured value is 2.8."
    payload["main_findings"][0]["statement"] = "The measured value is 2.8."
    payload["main_findings"][0]["fact_refs"] = ["rdf.first_peak_position"]
    bundle = _bundle()
    assert ReportGroundingValidator().validate(
        ScientificReportOutput.model_validate(payload),
        bundle=bundle,
        interpretation=_interpretation(),
    ) == []


def test_partial_and_stale_status_are_preserved() -> None:
    partial = DeterministicScientificReportComposer().compose(bundle=_bundle(execution_status="PARTIAL"), interpretation=_interpretation(), relevance_status="STALE")
    text = " ".join([partial.summary, *(item.statement for item in partial.limitations)])
    assert "部分" in text
    assert "历史" in text
    assert ReportGroundingValidator().validate(partial, bundle=_bundle(execution_status="PARTIAL", relevance_status="STALE"), interpretation=_interpretation()) == []


def test_deterministic_report_deduplicates_limitations_and_uses_readable_method_copy() -> None:
    report = DeterministicScientificReportComposer().compose(
        bundle=_bundle(),
        interpretation=_interpretation(),
        relevance_status="CURRENT",
    )
    assert [item.statement for item in report.limitations].count("结果受有限截断范围约束。") == 1
    assert report.method_summary == "根据晶体结构统计指定截断范围内的原子对距离分布，得到径向分布函数。"
    assert "structure.rdf" not in report.method_summary


def test_ml_table_result_uses_same_grounded_report_grammar() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["research_question"] = "回归模型的 RMSE 是多少？"
    payload["result_items"][0].update({"id": "ml.regression", "result_type": "ml.regression_evaluation", "title": "材料属性回归评估", "fact_refs": ["ml.rmse"], "evidence_refs": ["evidence.ml"]})
    payload["facts"][0].update({"fact_id": "ml.rmse", "predicate": "rmse", "value": 0.18, "unit": "eV"})
    payload["figures"] = []
    payload["tables"] = [{"table_id": "table.ml_metrics", "table_type": "regression_metrics", "role": "PRIMARY", "title": "回归指标", "artifact_ids": ["artifact_private_123"], "fact_refs": ["ml.rmse"], "evidence_refs": ["evidence.ml"]}]
    payload["evidence"][0].update({"evidence_id": "evidence.ml", "supports_fact_refs": ["ml.rmse"], "supports_result_item_refs": ["ml.regression"]})
    payload["methods"][0].update({"method_id": "method.ml", "capability_id": "ml.regression_evaluation"})
    interpretation = _interpretation()
    interpretation["interpretation"].update({"title": "材料属性回归评估", "answer_lead": "模型 RMSE 为 0.18 eV。", "primary_result_refs": ["ml.regression"]})
    interpretation["interpretation"]["primary_findings"][0].update({"finding_id": "finding.ml.rmse", "statement": "模型 RMSE 为 0.18 eV。", "fact_refs": ["ml.rmse"], "evidence_refs": ["evidence.ml"], "result_item_refs": ["ml.regression"]})
    bundle = ScientificResultBundle.model_validate(payload)
    report = DeterministicScientificReportComposer().compose(bundle=bundle, interpretation=interpretation, relevance_status="CURRENT")
    assert report.title == "材料属性回归评估"
    assert report.primary_figures == []
    assert ReportGroundingValidator().validate(report, bundle=bundle, interpretation=interpretation) == []


def test_report_repair_is_bounded_to_one_attempt() -> None:
    valid = _report().model_dump(mode="json")
    invalid = {**valid, "main_findings": [{**valid["main_findings"][0], "fact_refs": ["fact.unknown"]}]}
    client = FakeStructuredReportComposerClient([invalid, valid])
    service = ScientificReportService(repository_factory=object(), client=client)  # type: ignore[arg-type]
    output, _, repair = service._compose_with_one_repair(input_payload={}, bundle=_bundle(), interpretation=_interpretation())
    assert output.title
    assert repair is True
    assert client.calls == 2


def test_report_repair_never_calls_provider_a_third_time() -> None:
    invalid = _report().model_dump(mode="json")
    invalid["main_findings"][0]["fact_refs"] = ["fact.unknown"]
    client = FakeStructuredReportComposerClient([invalid, invalid, invalid])
    service = ScientificReportService(repository_factory=object(), client=client)  # type: ignore[arg-type]
    with pytest.raises(ScientificReportError, match="unknown reference"):
        service._compose_with_one_repair(input_payload={}, bundle=_bundle(), interpretation=_interpretation())
    assert client.calls == 2


def test_report_role_uses_report_composition_provider_purpose() -> None:
    def transport(**_kwargs):
        return {
            "choices": [{"message": {"content": json.dumps(_report().model_dump(mode="json"))}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 24},
        }

    provider = DeepSeekProvider(transport=transport)
    client = DeepSeekStructuredLLMClient(provider)
    result = asyncio.run(client.generate_structured(
        role="scientific_report_composer",
        system_prompt="Return one JSON object.",
        input_payload={},
        output_schema=ScientificReportOutput.model_json_schema(),
        timeout_seconds=30,
    ))
    assert result.parsed["contract_version"] == "1.0"
    assert provider.call_audit[-1]["purpose"] == "REPORT_COMPOSITION"


def test_persisted_report_is_idempotent_reopens_without_provider_or_scientific_computation() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    owner = CurrentUser(id="owner", email="owner@example.invalid", displayName="Owner", roles=[])
    with engine.begin() as connection:
        connection.execute(insert(users), {"id": owner.id, "email": owner.email, "display_name": owner.displayName, "is_active": True})
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), {"id": "project_1", "organization_id": "org", "name": "Project", "created_by": owner.id})
        connection.execute(insert(sessions), {"id": "session_1", "project_id": "project_1", "mode": "project", "status": "active", "created_by": owner.id})
    factory = RepositoryFactory(engine)
    received = ResearchTurnService(factory).receive_turn(
        project_id="project_1",
        session_id="session_1",
        current_user=owner,
        request=CreateResearchTurnRequest(message="计算 LiFePO4 的 RDF。"),
    )
    job_id = "job_report_fixture"
    with engine.begin() as connection:
        connection.execute(insert(analysis_plans), {
            "id": "plan_report_fixture", "project_id": "project_1", "dataset_id": None, "profile_id": None,
            "job_id": job_id, "plan_source": "agent2", "planner_provider": "fixture", "analysis_plan_json": {},
            "plan_hash": "a" * 64, "validation_status": "validated", "created_by": owner.id,
        })
        connection.execute(insert(jobs), {"id": job_id, "project_id": "project_1", "dataset_id": None, "plan_id": "plan_report_fixture", "kind": "agent2", "status": "completed", "created_by": owner.id})
    bundle_payload = _bundle().model_dump(mode="json")
    bundle_payload.update({"research_turn_id": str(received.turn_id), "source_object_refs": []})
    bundle_payload["result_items"][0]["scientific_object_refs"] = []
    bundle_payload["methods"][0]["source_object_refs"] = []
    bundle_payload["provenance"]["job_id"] = job_id
    snapshot_id = UUID("55555555-5555-4555-8555-555555555555")
    interpretation_id = UUID("66666666-6666-4666-8666-666666666666")
    with factory.unit_of_work() as unit:
        unit.agent2.scientific_result_snapshots.add({
            "id": snapshot_id, "project_id": "project_1", "research_turn_id": received.turn_id, "job_id": job_id,
            "schema_version": "1.0", "projection_version": "agent2-result/1.0", "execution_status": "SUCCESS",
            "relevance_status": "CURRENT", "source_fingerprint": "b" * 64, "bundle_json": bundle_payload,
        })
        unit.agent2.interpretations.add({
            "id": interpretation_id, "research_turn_id": received.turn_id, "result_snapshot_id": snapshot_id,
            "project_id": "project_1", "contract_version": "1.0", "prompt_version": "scientific-interpreter/1.0",
            "provider": "fake", "model": "fixture", "provider_request_id": None, "repair_attempted": False,
            "input_fingerprint": "c" * 64, "grounding_status": "VALID", "output_json": _interpretation(),
        })

    def scientific_counts() -> tuple[int, int, int, int, int]:
        with engine.connect() as connection:
            return tuple(connection.execute(select(func.count()).select_from(table)).scalar_one() for table in (analysis_plans, jobs, tool_calls, artifacts, scientific_result_snapshots))

    report_payload = _report().model_dump(mode="json")
    report_payload["data_sources"] = []
    client = FakeStructuredReportComposerClient(report_payload)
    service = ScientificReportService(factory, client=client)
    before = scientific_counts()
    created = service.generate_for_turn(received.turn_id, created_by=owner.id)
    reopened = service.generate_for_turn(received.turn_id, created_by=owner.id)
    assert created == reopened
    assert client.calls == 1
    assert scientific_counts() == before
    assert service.get_by_report_id(created["report_id"])["report"] == created["report"]


def test_report_viewer_sources_are_derived_only_from_result_provenance() -> None:
    source = _bundle().source_object_refs[0]

    class Objects:
        def get_object(self, object_id):
            assert str(object_id) == str(source.object_id)
            return {"id": str(source.object_id), "display_name": "LiFePO4", "current_version_id": str(source.version_id)}

        def get_version(self, version_id):
            assert str(version_id) == str(source.version_id)
            return {"id": str(source.version_id), "object_type": source.object_type}

    class Snapshots:
        def __init__(self, bundle):
            self.bundle = bundle

        def get(self, _snapshot_id):
            return {"bundle_json": self.bundle}

    class Agent2:
        def __init__(self, bundle):
            self.scientific_result_snapshots = Snapshots(bundle)
            self.scientific_objects = Objects()

    class Session:
        def __init__(self, bundle):
            self.agent2 = Agent2(bundle)

    row = {"scientific_result_snapshot_id": "snapshot-1"}
    fresh = ScientificReportService._with_viewer_sources({}, Session(_bundle().model_dump(mode="json")), row)
    assert fresh["viewer_sources"] == [{
        "source_ref": "source_1",
        "object_id": str(source.object_id),
        "version_id": str(source.version_id),
        "object_type": source.object_type,
        "display_name": "LiFePO4",
        "is_current_version": True,
    }]
    assert fresh["figure_sources"] == [{
        "figure_ref": "figure.rdf_curve",
        "artifact_ids": ["artifact_private_123"],
        "job_id": "job_private_123",
    }]

    legacy_bundle = _bundle().model_copy(update={"source_object_refs": []}).model_dump(mode="json")
    legacy = ScientificReportService._with_viewer_sources({}, Session(legacy_bundle), row)
    assert legacy["viewer_sources"] == []
    assert legacy["figure_sources"] == [{
        "figure_ref": "figure.rdf_curve",
        "artifact_ids": ["artifact_private_123"],
        "job_id": "job_private_123",
    }]


@pytest.mark.live_llm
@pytest.mark.skipif(os.getenv("MDI_RUN_AGENT2_LIVE") != "1" or not os.getenv("DEEPSEEK_KEY"), reason="live DeepSeek report qualification is explicitly gated")
@pytest.mark.parametrize("family", ["rdf", "xrd", "stale"])
def test_live_deepseek_report_composer_is_grounded(family: str) -> None:
    if family == "xrd":
        bundle, interpretation = _xrd_bundle_and_interpretation()
        relevance = "CURRENT"
    else:
        bundle, interpretation = _bundle(relevance_status="STALE" if family == "stale" else "CURRENT"), _interpretation()
        relevance = "STALE" if family == "stale" else "CURRENT"
    input_payload, _ = ReportComposerInputAssembler().assemble(bundle=bundle, interpretation=interpretation, relevance_status=relevance)
    composer = DeepSeekReportComposerClient()
    service = ScientificReportService(repository_factory=object(), client=composer, timeout_seconds=120)  # type: ignore[arg-type]
    output, _, repair = service._compose_with_one_repair(input_payload=input_payload, bundle=bundle, interpretation=interpretation)
    assert ReportGroundingValidator().validate(output, bundle=bundle, interpretation=interpretation) == []
    provider_calls = len(composer.client.provider.call_audit)
    assert provider_calls == (2 if repair else 1)
    assert provider_calls <= 2
    print({"family": family, "provider_calls": provider_calls, "repair": repair})


@pytest.mark.live_llm
@pytest.mark.skipif(os.getenv("MDI_RUN_AGENT2_LIVE") != "1" or not os.getenv("DEEPSEEK_KEY"), reason="live DeepSeek report qualification is explicitly gated")
def test_live_deepseek_report_composer_repairs_one_grounding_failure() -> None:
    bundle, interpretation = _bundle(), _interpretation()
    input_payload, _ = ReportComposerInputAssembler().assemble(
        bundle=bundle,
        interpretation=interpretation,
        relevance_status="CURRENT",
    )
    live = DeepSeekReportComposerClient()
    invalid = _report().model_dump(mode="json")
    invalid["main_findings"][0]["fact_refs"] = ["fact.unknown"]

    class InvalidThenLiveClient:
        def __init__(self) -> None:
            self.calls = 0

        async def generate_structured(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                return StructuredLLMResult(
                    provider="controlled-fixture",
                    model="invalid-first-response",
                    parsed=invalid,
                    latency_ms=0,
                    repair_attempted=False,
                    prompt_version="scientific-report-composer/1.0",
                )
            return await live.generate_structured(**kwargs)

    client = InvalidThenLiveClient()
    service = ScientificReportService(repository_factory=object(), client=client, timeout_seconds=120)  # type: ignore[arg-type]
    output, _, repair = service._compose_with_one_repair(
        input_payload=input_payload,
        bundle=bundle,
        interpretation=interpretation,
    )
    assert repair is True
    assert client.calls == 2
    assert len(live.client.provider.call_audit) == 1
    assert ReportGroundingValidator().validate(output, bundle=bundle, interpretation=interpretation) == []
    print({"family": "controlled_repair", "semantic_calls": client.calls, "live_provider_calls": 1, "repair": repair})
