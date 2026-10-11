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
from mdi_api.scientific_reports.queue import ReportQueueSubmitResult
from mdi_api.scientific_reports.requests import ScientificReportRequestService
from mdi_api.scientific_reports.schemas import ReportContextBundle, ScientificReportOutput
from mdi_api.scientific_reports.service import ScientificReportError, ScientificReportService
from mdi_api.scientific_results.schemas import ScientificResultBundle
from mdi_api.unit_of_work import RepositoryFactory
from mdi_llm import DeepSeekProvider


@pytest.mark.parametrize("text,refs,valid", [
    ("平台参考资料（版本 1.0.0），值为 0.76 angstrom。", ["version", "radius"], True),
    ("参考资料版本为 1.0.0。", ["version"], True),
    ("Reference version: 1.0.0.", ["version"], True),
    ("参考资料版本为 1.0.1。", ["version", "one"], False),
    ("参考资料版本为 1.0。", ["version", "one"], False),
    ("参考资料版本为 1.0.0。", ["one"], False),
    ("参考版本 1.0.0；数值 1.0。", ["version"], False),
    ("参考版本 1.0.0；半径为 2.5 angstrom。", ["version", "radius"], False),
])
def test_report_reference_versions_are_whole_cited_identifiers_not_measurements(text, refs, valid):
    facts = {
        "version": {"predicate": "reference.version", "value": "1.0.0"},
        "radius": {"predicate": "reference.element.covalent_radius", "value": 0.76, "unit": "angstrom"},
        "one": {"predicate": "reference.value_count", "value": 1, "unit": "count"},
    }
    errors = ReportGroundingValidator._numeric_errors(text, refs, facts, "finding")
    assert (not errors) is valid, errors


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


@pytest.mark.parametrize("coverage", ["existing", "additional", "unrelated", "absent"])
def test_large_figure_citations_preserve_complete_support_without_truncation(coverage):
    from pydantic import ValidationError
    from mdi_api.application.scientific_reports.grounded import _report_figure
    bundle = _bundle()
    template = bundle.facts[0]
    bundle.facts.extend(template.model_copy(update={"fact_id": f"fact.value.{index}", "value": index})
                        for index in range(1, 119))
    bundle.figures[0].fact_refs = [fact.fact_id for fact in bundle.facts]
    bundle.figures[0].caption_seed = "Saved value 118 Å."
    support = list(bundle.figures[0].fact_refs)
    if coverage == "existing":
        bundle.evidence[0].supports_fact_refs = support
    elif coverage in {"additional", "unrelated"}:
        if coverage == "unrelated":
            bundle.facts.append(template.model_copy(update={"fact_id": "fact.unrelated", "value": 999}))
            support.append("fact.unrelated")
        bundle.evidence.append(bundle.evidence[0].model_copy(update={
            "evidence_id": "evidence.saved_table", "artifact_id": "table", "supports_fact_refs": support,
        }))
    original = bundle.model_dump(mode="json")
    if coverage in {"absent", "unrelated"}:
        with pytest.raises(ValidationError):
            _report_figure(bundle.figures[0], bundle)
    else:
        report = _report().model_copy(update={"primary_figures": [_report_figure(bundle.figures[0], bundle)]})
        assert ReportGroundingValidator().validate(report, bundle=bundle, interpretation=_interpretation()) == []
        figure = report.primary_figures[0]
        assert figure.caption == "Saved value 118 Å."
        cited = set(figure.fact_refs) | {ref for evidence in bundle.evidence
            if evidence.evidence_id in figure.evidence_refs for ref in evidence.supports_fact_refs}
        assert set(bundle.figures[0].fact_refs) <= cited
    assert bundle.model_dump(mode="json") == original


def test_volumetric_report_binds_only_the_saved_datasets_exact_producer():
    from mdi_api.application.scientific_reports.artifact_sources import volumetric_report_figures
    bundle = _bundle()
    bundle.result_items[0].result_type = "volumetric.field"
    base = {"jobId": "job_private_123", "projectId": "project_1", "toolCallId": "toolcall_private_123"}
    artifacts = [
        {**base, "id": "artifact_private_123", "type": "volumetric_dataset_json", "name": "volumetric_dataset.json"},
        {**base, "id": "manifest", "type": "volumetric_manifest_json", "name": "volumetric_manifest.json"},
        {**base, "id": "binary", "type": "volumetric_binary", "name": "field.f64", "storageKey": "must-not-leak"},
        {**base, "id": "sibling", "type": "volumetric_binary", "name": "field.f64", "toolCallId": "other-call"},
        {**base, "id": "foreign", "type": "volumetric_binary", "name": "foreign.f64", "projectId": "foreign"},
        {**base, "id": "unrelated", "type": "recipe_json", "name": "recipe.json"},
    ]
    calls = [{"id": "toolcall_private_123", "jobId": "job_private_123"}]
    original = bundle.model_dump(mode="json")
    [(figure, companions)] = volumetric_report_figures(bundle, artifacts, calls)
    assert figure.artifact_ids == ["artifact_private_123"]
    assert {a["id"] for a in companions} == {"artifact_private_123", "manifest", "binary"}
    assert "storageKey" not in json.dumps(companions)
    assert bundle.model_dump(mode="json") == original
    assert volumetric_report_figures(bundle, artifacts, []) == []
    assert volumetric_report_figures(bundle, artifacts, calls + calls) == []
    assert volumetric_report_figures(bundle, artifacts + [{**artifacts[1], "id": "duplicate"}], calls) == []
    assert volumetric_report_figures(bundle, artifacts + [{**artifacts[2], "id": "ambiguous-name"}], calls) == []
    bundle.provenance.tool_call_ids = []
    assert volumetric_report_figures(bundle, artifacts, calls) == []


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
    assert ReportContextBundle.model_validate(envelope).contract_version == "2.0"
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


def test_report_context_compacts_assessment_traces_without_dropping_scientific_qualifiers():
    bundle = _bundle()
    interpretation = _interpretation()
    finding = interpretation["interpretation"]["primary_findings"][0]
    scientific_assessment = {
        "outcome": "SUPPORTED_WITH_QUALIFIERS",
        "accepted": True,
        "required_qualifiers": ["仅适用于当前结构"],
        "method_context": ["有限截断范围"],
        "limitations": ["不能推断材料稳定性"],
        "reason_codes": ["METHOD_DEPENDENT"],
        "defects": [],
        "severity": None,
        "independent_evidence_groups": 1,
        "contradicting_refs": [],
    }
    finding["reasoning_assessment"] = {
        **scientific_assessment,
        "contract_version": "scientific-reasoning/1.0",
        "assessment_version": "scientific-reasoning-policy/1.0",
        "claim_id": finding["finding_id"],
        "scope": "current ScientificResult scope",
        "supporting_refs": [f"result_fact_{index}" for index in range(64)],
    }
    interpretation["interpretation"]["supporting_findings"] = [
        {**finding, "finding_id": "supporting-1"},
    ]
    original = json.loads(json.dumps(interpretation))

    envelope, fingerprint = ReportComposerInputAssembler().assemble(
        bundle=bundle, interpretation=interpretation, relevance_status="CURRENT",
    )

    assert interpretation == original
    for compact in [*envelope["interpretation"]["findings"], *envelope["interpretation"]["supporting_findings"]]:
        assert compact["statement"] == finding["statement"]
        assert compact["fact_refs"] == finding["fact_refs"]
        assert compact["evidence_refs"] == finding["evidence_refs"]
        assert compact["result_item_refs"] == finding["result_item_refs"]
        assert compact["reasoning_assessment"] == scientific_assessment
    assert len(json.dumps(envelope["interpretation"]["findings"][0])) < len(json.dumps(finding))
    interpretation["interpretation"]["primary_findings"][0]["reasoning_assessment"]["required_qualifiers"] = ["另一个科学限定"]
    _, changed = ReportComposerInputAssembler().assemble(
        bundle=bundle, interpretation=interpretation, relevance_status="CURRENT",
    )
    assert changed != fingerprint


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


@pytest.mark.parametrize("statement", ["MAE、RMSE 和 R² 已计算。", "已生成残差图。", "已列出绝对误差最大的样本。"])
def test_report_rejects_derived_completion_without_metric_or_sample_facts(statement):
    report = _report()
    report = report.model_copy(update={"main_findings": [report.main_findings[0].model_copy(update={"statement": statement})]})
    errors = ReportGroundingValidator().validate(report, bundle=_bundle(), interpretation=_interpretation())
    assert any("derived product" in error for error in errors)


@pytest.mark.parametrize("statement", [
    "R² 未定义（目标值为常量）。",
    "R²状态为undefined_constant_target，无法定义R²。",
    "由于目标变量为常数，R²无法定义。",
])
def test_report_keeps_undefined_r2_grounded_in_saved_status(statement):
    bundle, interpretation = _bundle(), _interpretation()
    bundle.facts[0].predicate = "ml.r2_status"
    bundle.facts[0].value = "undefined_constant_target"
    bundle.facts[0].unit = None
    interpretation["interpretation"]["answer_lead"] = statement
    interpretation["interpretation"]["primary_findings"][0]["statement"] = statement
    report = DeterministicScientificReportComposer().compose(bundle=bundle, interpretation=interpretation, relevance_status="CURRENT")
    assert ReportGroundingValidator().validate(report, bundle=bundle, interpretation=interpretation) == []
    report = report.model_copy(update={"main_findings": [report.main_findings[0].model_copy(update={"statement": statement + "R² = 1。"})]})
    assert ReportGroundingValidator().validate(report, bundle=bundle, interpretation=interpretation)


def test_report_named_metric_notation_does_not_add_a_measurement():
    bundle, interpretation = _diffusion_bundle_and_interpretation()
    report = DeterministicScientificReportComposer().compose(bundle=bundle, interpretation=interpretation, relevance_status="CURRENT")
    report = report.model_copy(update={"summary": "拟合 R^2 为 0.970301847945。"})
    assert ReportGroundingValidator().validate(report, bundle=bundle, interpretation=interpretation) == []


def test_saved_figure_graph_supports_product_availability_but_not_uncited_numbers():
    bundle = _bundle()
    bundle.facts[0].predicate = "ml.mean_signed_error"
    bundle.facts[0].value = 0.18
    bundle.facts[0].unit = None
    report = _report()
    figure = report.primary_figures[0].model_copy(update={"caption": "残差分布图。", "fact_refs": [], "evidence_refs": []})
    report = report.model_copy(update={"primary_figures": [figure]})
    errors = ReportGroundingValidator().validate(report, bundle=bundle, interpretation=_interpretation())
    assert not any(error.startswith("figure") for error in errors)
    quantified = figure.model_copy(update={"caption": "残差分布图，平均误差为 0.18。"})
    report = report.model_copy(update={"primary_figures": [quantified]})
    assert any(error.startswith("figure contains an unsupported numeric") for error in ReportGroundingValidator().validate(report, bundle=bundle, interpretation=_interpretation()))


def _diffusion_bundle_and_interpretation() -> tuple[ScientificResultBundle, dict]:
    payload = _bundle().model_dump(mode="json")
    source = payload["source_object_refs"][0]
    source_fact = payload["facts"][0]["source"]
    fact_specs = [
        ("trajectory.diffusion_coefficient", 0.038618084156, "angstrom^2/picosecond"),
        ("trajectory.diffusion_fit_start_time", 1.0, "picosecond"),
        ("trajectory.diffusion_fit_end_time", 6.0, "picosecond"),
        ("trajectory.diffusion_fit_point_count", 11, "count"),
        ("trajectory.diffusion_fit_r_squared", 0.970301847945, None),
        ("trajectory.diffusion_fit_rmse", 0.064094868867, "angstrom^2"),
        ("trajectory.diffusion_regime", "DIFFUSIVE_WINDOW_ACCEPTED", None),
    ]
    fact_ids = [item[0] for item in fact_specs]
    payload.update({
        "research_question": "在 1 ps 到 6 ps 窗口内评估 Li 扩散。",
        "facts": [
            {
                "fact_id": fact_id,
                "predicate": fact_id.rsplit(".", 1)[-1],
                "subject_ref": str(OBJECT_ID),
                "value": value,
                "unit": unit,
                "uncertainty": None,
                "source": {**source_fact, "artifact_locator": f"/{fact_id}"},
            }
            for fact_id, value, unit in fact_specs
        ],
    })
    payload["result_items"][0].update({
        "id": "trajectory.diffusion",
        "result_type": "trajectory.diffusion",
        "title": "轨迹扩散评估",
        "fact_refs": fact_ids,
        "evidence_refs": ["evidence.diffusion"],
        "scientific_object_refs": [source],
    })
    payload["figures"][0].update({
        "figure_id": "figure.diffusion",
        "figure_type": "trajectory.diffusion",
        "title": "扩散拟合",
        "fact_refs": fact_ids,
        "evidence_refs": ["evidence.diffusion"],
    })
    payload["evidence"][0].update({
        "evidence_id": "evidence.diffusion",
        "supports_fact_refs": fact_ids,
        "supports_result_item_refs": ["trajectory.diffusion"],
    })
    payload["methods"][0].update({
        "method_id": "method.diffusion",
        "capability_id": "trajectory.diffusion",
        "tool_id": "trajectory.diffusion",
    })
    interpretation = _interpretation()
    interpretation["interpretation"].update({
        "title": "Li 扩散窗口评估",
        "answer_lead": (
            "在 1 ps 到 6 ps 的显式拟合窗口内，Li 的扩散系数估计为 "
            "0.038618084156 Å²/ps。"
        ),
        "primary_result_refs": ["trajectory.diffusion"],
        "primary_findings": [
            {
                "finding_id": "finding.diffusion.coefficient",
                "statement": (
                    "在 1 ps 到 6 ps 的显式拟合窗口内，Li 的扩散系数估计为 "
                    "0.038618084156 Å²/ps。"
                ),
                "importance": "HIGH",
                "confidence": "HIGH",
                "fact_refs": fact_ids[:3],
                "evidence_refs": ["evidence.diffusion"],
                "result_item_refs": ["trajectory.diffusion"],
            },
            {
                "finding_id": "finding.diffusion.quality",
                "statement": (
                    "扩散拟合在 1 ps 到 6 ps 窗口内使用 11 个拟合点，"
                    "R² 为 0.970301847945，RMSE 为 0.064094868867 Å²。"
                ),
                "importance": "HIGH",
                "confidence": "HIGH",
                "fact_refs": fact_ids[3:6],
                "evidence_refs": ["evidence.diffusion"],
                "result_item_refs": ["trajectory.diffusion"],
            },
            {
                "finding_id": "finding.diffusion.regime",
                "statement": (
                    "扩散区间诊断为 DIFFUSIVE_WINDOW_ACCEPTED，"
                    "表明所选 1–6 ps 窗口被接受为扩散性窗口。"
                ),
                "importance": "MEDIUM",
                "confidence": "HIGH",
                "fact_refs": [fact_ids[6]],
                "evidence_refs": ["evidence.diffusion"],
                "result_item_refs": ["trajectory.diffusion"],
            },
        ],
    })
    return ScientificResultBundle.model_validate(payload), interpretation


def test_diffusion_report_follows_evidence_support_and_composite_units() -> None:
    bundle, interpretation = _diffusion_bundle_and_interpretation()
    report = DeterministicScientificReportComposer().compose(
        bundle=bundle,
        interpretation=interpretation,
        relevance_status="CURRENT",
    )
    assert ReportGroundingValidator().validate(
        report,
        bundle=bundle,
        interpretation=interpretation,
    ) == []

    unsupported_window = report.model_dump(mode="json")
    unsupported_window["main_findings"][2]["statement"] = (
        "扩散区间诊断为 DIFFUSIVE_WINDOW_ACCEPTED，"
        "表明所选 1–8 ps 窗口被接受为扩散性窗口。"
    )
    assert any(
        "finding contains an unsupported numeric claim" in error
        for error in ReportGroundingValidator().validate(
            ScientificReportOutput.model_validate(unsupported_window),
            bundle=bundle,
            interpretation=interpretation,
        )
    )

    unsupported_unit = report.model_dump(mode="json")
    unsupported_unit["main_findings"][0]["statement"] = (
        "在 1 ps 到 6 ps 的显式拟合窗口内，Li 的扩散系数估计为 "
        "0.038618084156 m^2/s。"
    )
    assert any(
        "finding contains an unsupported unit" in error
        for error in ReportGroundingValidator().validate(
            ScientificReportOutput.model_validate(unsupported_unit),
            bundle=bundle,
            interpretation=interpretation,
        )
    )


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


def test_lowercase_k_point_label_is_not_treated_as_kelvin_unit() -> None:
    payload = json.loads(
        json.dumps(_report().model_dump(mode="json"), ensure_ascii=False)
        .replace("2.84", "3")
        .replace("Å", "count"),
    )
    payload["summary"] = "电子能带覆盖 3 k 点。"
    payload["main_findings"][0]["statement"] = "电子能带覆盖 3 k 点。"
    payload["main_findings"][0]["fact_refs"] = ["rdf.first_peak_position"]
    bundle_payload = _bundle().model_dump(mode="json")
    bundle_payload["facts"][0].update({"value": 3, "unit": "count", "predicate": "electronic.kpoint_count"})
    assert ReportGroundingValidator().validate(
        ScientificReportOutput.model_validate(payload),
        bundle=ScientificResultBundle.model_validate(bundle_payload),
        interpretation=_interpretation(),
    ) == []


@pytest.mark.parametrize("predicate", ["phonon.frequency", "electronic.energy"])
@pytest.mark.parametrize("statement,valid", [
    ("沿 Γ–M–K–Γ 路径的值为 2.84 Å。", True),
    ("沿 Γ-M-K-Γ 路径的值为 2.84 Å。", True),
    ("沿 Γ–M–K–Γ 路径，温度为 2.84 K。", False),
    ("温度范围 2.84–2.84 K。", False),
    ("温度单位为 K。", False),
])
def test_report_reciprocal_path_labels_do_not_mask_temperature_claims(predicate, statement, valid) -> None:
    payload = _report().model_dump(mode="json")
    payload["summary"] = statement
    payload["main_findings"][0]["statement"] = statement
    payload["primary_figures"][0]["caption"] = statement
    for section in ("discussion", "conclusion"):
        payload[section] = {"text": statement, "fact_refs": ["rdf.first_peak_position"], "evidence_refs": []}
    bundle_payload = _bundle().model_dump(mode="json")
    bundle_payload["facts"][0]["predicate"] = predicate
    errors = ReportGroundingValidator().validate(
        ScientificReportOutput.model_validate(payload),
        bundle=ScientificResultBundle.model_validate(bundle_payload),
        interpretation=_interpretation(),
    )
    if valid:
        assert errors == []
    else:
        for section in ("summary", "finding", "figure", "discussion", "conclusion"):
            assert any(f"{section} contains an unsupported unit: k" in error for error in errors)


def test_report_path_label_exception_requires_referenced_band_facts() -> None:
    assert ReportGroundingValidator._numeric_errors(
        "Γ–M–K–Γ", ["f"], {"f": {"predicate": "temperature", "value": 2.84, "unit": "Å"}}, "summary"
    ) == ["summary contains an unsupported unit: k"]
    assert ReportGroundingValidator._numeric_errors(
        "2.84 K", ["f"], {"f": {"predicate": "temperature", "value": 2.84, "unit": "K"}}, "summary"
    ) == []


@pytest.mark.parametrize("label", ["K点", "K 点", "K-point", "K‑point", "K points"])
def test_report_partial_density_point_labels_preserve_temperature_grounding(label) -> None:
    statement = f"部分电荷密度不能确定具体能带、{label} 或轨道身份。"
    payload = _report().model_dump(mode="json")
    payload["summary"] = statement
    payload["main_findings"][0]["statement"] = statement
    payload["primary_figures"][0]["caption"] = statement
    for section in ("discussion", "conclusion"):
        payload[section] = {"text": statement, "fact_refs": ["rdf.first_peak_position"], "evidence_refs": []}
    bundle = _bundle()
    bundle.facts[0].predicate = "volumetric.minimum"
    validator = ReportGroundingValidator()
    assert validator.validate(ScientificReportOutput.model_validate(payload), bundle=bundle, interpretation=_interpretation()) == []

    for temperature in ("温度单位为 K。", "温度为 2.84 K。", "温度在 2.84 K 点附近。"):
        assert ReportGroundingValidator._numeric_errors(
            statement + temperature, ["f"], {"f": bundle.facts[0].model_dump(mode="json")}, "summary"
        ) == ["summary contains an unsupported unit: k"]


def test_report_caption_uses_exact_saved_figure_type_without_borrowing_facts() -> None:
    payload = _report().model_dump(mode="json")
    caption = payload["primary_figures"][0]
    caption.update({"caption": "Γ–M–K–Γ", "fact_refs": [], "evidence_refs": []})
    bundle = _bundle().model_dump(mode="json")
    bundle["figures"][0]["figure_type"] = "phonon.band"
    validator = ReportGroundingValidator()
    assert validator.validate(ScientificReportOutput.model_validate(payload), bundle=bundle, interpretation=_interpretation()) == []
    caption["caption"] = "Γ–M–K–Γ，2.84 K"
    errors = validator.validate(ScientificReportOutput.model_validate(payload), bundle=bundle, interpretation=_interpretation())
    assert any(error.startswith("figure contains an unsupported numeric claim") for error in errors)
    assert "figure contains an unsupported unit: k" in errors
    caption["caption"] = "Γ–M–K–Γ"
    bundle["figures"][0]["figure_type"] = "rdf_curve"
    assert "figure contains an unsupported unit: k" in validator.validate(ScientificReportOutput.model_validate(payload), bundle=bundle, interpretation=_interpretation())


def test_conclusion_rollup_references_every_authoritative_finding_fact() -> None:
    bundle_payload = _bundle().model_dump(mode="json")
    bundle_payload["facts"].append({
        "fact_id": "electronic.kpoint_count",
        "predicate": "electronic.kpoint_count",
        "subject_ref": str(OBJECT_ID),
        "value": 3,
        "unit": "count",
        "uncertainty": None,
        "source": {
            "tool_call_id": "toolcall_private_123",
            "artifact_id": "artifact_private_123",
            "artifact_locator": "/summary/kpointCount",
        },
    })
    interpretation = _interpretation()
    interpretation["interpretation"]["answer_lead"] = (
        "RDF 第一峰位于 2.84 Å，并覆盖 3 k 点。"
    )
    interpretation["interpretation"]["primary_findings"].append({
        "finding_id": "finding.kpoints",
        "statement": "结果覆盖 3 k 点。",
        "importance": "MEDIUM",
        "confidence": "HIGH",
        "fact_refs": ["electronic.kpoint_count"],
        "evidence_refs": ["evidence.rdf_curve"],
        "result_item_refs": ["rdf.primary"],
    })
    bundle = ScientificResultBundle.model_validate(bundle_payload)
    report = DeterministicScientificReportComposer().compose(
        bundle=bundle,
        interpretation=interpretation,
        relevance_status="CURRENT",
    )
    assert report.conclusion is not None
    assert set(report.conclusion.fact_refs) == {
        "rdf.first_peak_position",
        "electronic.kpoint_count",
    }
    assert ReportGroundingValidator().validate(
        report,
        bundle=bundle,
        interpretation=interpretation,
    ) == []


def test_standard_unit_abbreviation_matches_authoritative_long_name() -> None:
    payload = json.loads(
        json.dumps(_report().model_dump(mode="json"), ensure_ascii=False)
        .replace("2.84", "5.0")
        .replace("Å", "THz"),
    )
    bundle_payload = _bundle().model_dump(mode="json")
    bundle_payload["facts"][0].update(
        {"predicate": "phonon.frequency_max", "value": 5.0, "unit": "terahertz"},
    )
    bundle = ScientificResultBundle.model_validate(bundle_payload)
    assert ReportGroundingValidator().validate(
        ScientificReportOutput.model_validate(payload),
        bundle=bundle,
        interpretation=_interpretation(),
    ) == []


def test_unrelated_unit_remains_rejected_when_frequency_unit_is_authoritative() -> None:
    payload = json.loads(
        json.dumps(_report().model_dump(mode="json"), ensure_ascii=False)
        .replace("2.84", "5.0")
        .replace("Å", "eV"),
    )
    bundle_payload = _bundle().model_dump(mode="json")
    bundle_payload["facts"][0].update(
        {"predicate": "phonon.frequency_max", "value": 5.0, "unit": "terahertz"},
    )
    errors = ReportGroundingValidator().validate(
        ScientificReportOutput.model_validate(payload),
        bundle=ScientificResultBundle.model_validate(bundle_payload),
        interpretation=_interpretation(),
    )
    assert any("unsupported unit: ev" in error for error in errors)


@pytest.mark.parametrize("unit, valid", [("angstrom^3", True), ("angstrom", False), ("dimensionless", False)])
def test_report_elf_integral_keeps_its_volume_unit(unit, valid):
    payload = json.loads(json.dumps(_report().model_dump(mode="json"), ensure_ascii=False).replace("2.84", "3.1").replace("Å", "Å³"))
    bundle = _bundle().model_dump(mode="json")
    bundle["facts"][0].update(predicate="volumetric.volume_integral", value=3.1, unit=unit)
    errors = ReportGroundingValidator().validate(ScientificReportOutput.model_validate(payload), bundle=bundle, interpretation=_interpretation())
    assert (errors == []) is valid


@pytest.mark.parametrize("spelling", [
    "electron/angstrom^3", "electron/Å^3", "electrons / Å^{3}", "电子/Å³",
])
def test_report_density_units_are_grounded_as_whole_compounds(spelling: str) -> None:
    payload = json.loads(json.dumps(_report().model_dump(mode="json"), ensure_ascii=False).replace("Å", spelling))
    bundle = _bundle().model_dump(mode="json")
    bundle["facts"][0].update(predicate="volumetric.minimum", unit="electron/angstrom^3")
    report = ScientificReportOutput.model_validate(payload)
    assert ReportGroundingValidator().validate(report, bundle=bundle, interpretation=_interpretation()) == []
    # Neither a length nor a reciprocal volume establishes an electron density.
    for unit in ("angstrom", "angstrom^-3"):
        bundle["facts"][0]["unit"] = unit
        errors = ReportGroundingValidator().validate(report, bundle=bundle, interpretation=_interpretation())
        assert any("unsupported unit" in error for error in errors)


@pytest.mark.parametrize("wrong_unit", [
    "Å³", "Å^-3", "electron/bohr^3", "electron/nm³",
    "elementary_charge/Å^3", "bohr_magneton/Å³",
])
def test_report_density_rejects_other_quantities_and_unit_conversions(wrong_unit: str) -> None:
    payload = json.loads(json.dumps(_report().model_dump(mode="json"), ensure_ascii=False).replace("Å", wrong_unit))
    bundle = _bundle().model_dump(mode="json")
    bundle["facts"][0].update(predicate="volumetric.minimum", unit="electron/angstrom^3")
    errors = ReportGroundingValidator().validate(
        ScientificReportOutput.model_validate(payload), bundle=bundle, interpretation=_interpretation(),
    )
    assert any("unsupported unit" in error for error in errors)


@pytest.mark.parametrize("predicate,value,statement", [
    ("volumetric.length_unit", "angstrom", "坐标长度单位为 Å。"),
    ("volumetric.canonical_unit", "electron/angstrom^3", "密度单位为 电子/Å³。"),
    ("volumetric.selected_canonical_unit", "electronvolt", "所选场单位为 eV。"),
    ("phonon.frequency_unit", "terahertz", "频率单位为 THz。"),
])
def test_report_uses_only_referenced_explicit_unit_definitions(predicate, value, statement):
    facts = {"unit": {"predicate": predicate, "value": value, "unit": None}}
    validator = ReportGroundingValidator()
    assert validator._numeric_errors(statement, ["unit"], facts, "summary") == []
    assert validator._numeric_errors(
        statement, [], facts, "finding", evidence_refs=["e"],
        evidence={"e": {"supports_fact_refs": ["unit"]}},
    ) == []
    assert any("unsupported unit" in e for e in validator._numeric_errors(statement, [], facts, "finding"))
    assert any("unsupported unit" in e for e in validator._numeric_errors("单位为 nm。", ["unit"], facts, "finding"))
    facts["unit"]["predicate"] = "volumetric.field_name"
    assert any("unsupported unit" in e for e in validator._numeric_errors(statement, ["unit"], facts, "finding"))


def test_report_abstract_describes_analysis_without_repeating_the_conclusion() -> None:
    report = _report()
    assert report.conclusion is not None
    assert report.summary != report.conclusion.text
    assert "径向分布函数" in report.summary
    assert "2.84" not in report.summary
    assert report.conclusion.text == "RDF 第一峰位于 2.84 Å。"


def test_report_abstract_keeps_qualified_scope_without_repeating_its_opening_clause():
    interpretation = _interpretation()
    original = interpretation["interpretation"]["primary_findings"][0]
    scopes = ["当前合成回归测试表。", "当前合成回归测试表，共 4096 条记录。", "当前合成回归测试表，不代表真实材料性能。", "当前合成回归测试表附录"]
    interpretation["interpretation"]["primary_findings"] = [{**original, "scope": scope} for scope in scopes]
    report = DeterministicScientificReportComposer().compose(bundle=_bundle(), interpretation=interpretation, relevance_status="CURRENT")
    assert "研究范围：当前合成回归测试表。" not in report.summary
    assert report.summary.count("研究范围：") == 1
    for scope in scopes[1:]:
        assert scope in report.summary
    assert interpretation["interpretation"]["primary_findings"][0]["scope"] == scopes[0]


def _regression_overall_fixture():
    bundle, interpretation = _bundle(), _interpretation()
    base = bundle.facts[0]
    bundle.result_items[0].result_type = "ml.regression.evaluation"
    bundle.methods[0].capability_id = "ml.regression_evaluation"
    bundle.facts = [base.model_copy(update={"fact_id": f"metric.{i}", "predicate": predicate, "value": value, "unit": None})
                    for i, (predicate, value) in enumerate([("ml.sample_count", 100), ("ml.mae", 0.1), ("ml.rmse", 0.2), ("ml.r2", 0.9)])]
    refs = [fact.fact_id for fact in bundle.facts]
    bundle.result_items[0].fact_refs = refs
    finding = interpretation["interpretation"]["primary_findings"][0]
    finding.update(statement="对合成样本的回归评估：100 条记录，MAE 0.1，RMSE 0.2，R² 0.9。不能据此推断真实材料的泛化性能。", fact_refs=refs,
                   qualifiers=["数值未声明物理单位"])
    return bundle, interpretation


def test_regression_conclusion_keeps_complete_overall_finding_and_qualifications():
    bundle, interpretation = _regression_overall_fixture()
    finding = interpretation["interpretation"]["primary_findings"][0]
    interpretation["interpretation"]["primary_findings"].append({**finding, "statement": "高误差样本列表。", "fact_refs": []})
    report = DeterministicScientificReportComposer().compose(bundle=bundle, interpretation=interpretation, relevance_status="CURRENT")
    assert report.conclusion.text == finding["statement"] + "数值未声明物理单位。"
    assert report.conclusion.fact_refs == finding["fact_refs"]
    assert "高误差样本" not in report.conclusion.text
    assert "高误差样本" in report.main_findings[1].statement
    assert report.summary != report.conclusion.text


@pytest.mark.parametrize("constant", [False, True])
def test_regression_conclusion_joins_scoped_metrics_without_repeating_samples(constant):
    bundle, interpretation = _regression_overall_fixture()
    finding = interpretation["interpretation"]["primary_findings"][0]
    if constant:
        bundle.facts[-1].predicate = "ml.r2_status"
        bundle.facts[-1].value = "undefined_constant_target"
    metric_refs = [fact.fact_id for fact in bundle.facts]
    scope = "当前合成测试表"
    metrics = {**finding, "statement": "MAE 0.1，RMSE 0.2。", "fact_refs": metric_refs[1:3], "scope": scope}
    r2 = {**finding, "finding_id": "r2", "statement": "R²未定义（目标值为常量）。" if constant else "R² 0.9。",
          "fact_refs": metric_refs[3:], "scope": scope, "qualifiers": ["不能推断泛化性能"]}
    count = {**finding, "finding_id": "count", "statement": "共 100 个样本。", "fact_refs": metric_refs[:1], "scope": scope}
    samples = {**finding, "finding_id": "samples", "statement": "高误差样本列表。", "fact_refs": [], "scope": scope}
    interpretation["interpretation"]["primary_findings"] = [count, r2, metrics, samples]
    report = DeterministicScientificReportComposer().compose(bundle=bundle, interpretation=interpretation, relevance_status="CURRENT")
    assert report.conclusion is not None
    assert r2["statement"] in report.conclusion.text
    assert metrics["statement"] in report.conclusion.text
    assert "数值未声明物理单位" in report.conclusion.text
    assert "不能推断泛化性能" in report.conclusion.text
    assert scope in report.conclusion.text
    assert "高误差样本" not in report.conclusion.text
    assert count["statement"] not in report.conclusion.text
    assert set(report.conclusion.fact_refs) == set(metric_refs[1:])
    assert len(report.main_findings) == 4


@pytest.mark.parametrize("problem", ["scope_mismatch", "missing_scope", "missing_metric", "wrong_status", "duplicate_status"])
def test_split_regression_conclusion_requires_exact_status_and_same_scope(problem):
    from mdi_api.application.scientific_reports.grounded import _regression_conclusion
    bundle, interpretation = _regression_overall_fixture()
    bundle.facts[-1].predicate = "ml.r2_status"
    bundle.facts[-1].value = "undefined_constant_target"
    finding = interpretation["interpretation"]["primary_findings"][0]
    metrics = {**finding, "fact_refs": ["metric.1", "metric.2"], "scope": "合成数据"}
    status = {**finding, "fact_refs": ["metric.3"], "scope": "合成数据"}
    if problem == "scope_mismatch":
        status["scope"] = "另一个材料"
    elif problem == "missing_scope":
        status["scope"] = metrics["scope"] = ""
    elif problem == "missing_metric":
        metrics["fact_refs"] = ["metric.1"]
    elif problem == "wrong_status":
        bundle.facts[-1].value = "defined"
    else:
        duplicate = bundle.facts[-1].model_copy(update={"fact_id": "other.r2_status"})
        bundle.facts.append(duplicate)
        bundle.result_items[0].fact_refs.append(duplicate.fact_id)
    assert _regression_conclusion(bundle, [metrics, status]) is None


def test_report_places_saved_finding_limits_in_the_limitations_section_once():
    bundle, interpretation = _regression_overall_fixture()
    finding = interpretation["interpretation"]["primary_findings"][0]
    limits = ["数值未声明物理单位。", "合成数据不能证明真实材料的泛化性能。"]
    finding["reasoning_assessment"] = {
        "claim_id": finding["finding_id"], "claim_type": "QUANTITATIVE_COMPARISON",
        "support_status": "DIRECTLY_SUPPORTED", "outcome": "SUPPORTED", "accepted": True,
        "scope": "当前合成测试表", "independent_evidence_groups": 1,
        "required_qualifiers": ["合成样本"], "limitations": limits,
    }
    interpretation["interpretation"]["limitations"] = [limits[0]]
    report = DeterministicScientificReportComposer().compose(bundle=bundle, interpretation=interpretation, relevance_status="CURRENT")
    assert all(value not in report.conclusion.text for value in limits)
    for value in limits:
        assert [item.statement for item in report.limitations].count(value) == 1
    assert report.conclusion.text == finding["statement"]


@pytest.mark.parametrize("ambiguous", ["multiple_metrics", "multiple_findings", "mixed_topics", "missing_metric"])
def test_regression_compact_conclusion_does_not_choose_ambiguous_or_partial_metrics(ambiguous):
    from mdi_api.application.scientific_reports.grounded import _regression_conclusion
    bundle, interpretation = _regression_overall_fixture()
    findings = interpretation["interpretation"]["primary_findings"]
    if ambiguous == "multiple_metrics":
        duplicate = bundle.facts[0].model_copy(update={"fact_id": "other.sample_count"})
        bundle.facts.append(duplicate)
        bundle.result_items[0].fact_refs.append(duplicate.fact_id)
    elif ambiguous == "multiple_findings":
        findings.append(dict(findings[0]))
    elif ambiguous == "mixed_topics":
        bundle.result_items.append(bundle.result_items[0].model_copy(update={"id": "other", "result_type": "structure.rdf"}))
    else:
        bundle.facts.pop()
    assert _regression_conclusion(bundle, findings) is None


@pytest.mark.parametrize("status, reason", [
    ("INSUFFICIENT_DURATION", "拟合窗口时长不足"),
    ("INSUFFICIENT_POINTS", "拟合点数不足"),
    ("POOR_LINEAR_FIT", "线性拟合质量未达标"),
])
def test_trajectory_report_conclusion_uses_saved_diagnostic_not_fit_statistics(status, reason):
    bundle = _bundle()
    bundle.methods[0].capability_id = "trajectory.diffusion"
    bundle.result_items[0].result_type = "trajectory.diffusion"
    bundle.facts[0].predicate = "trajectory.diffusion_regime"
    bundle.facts[0].value = status
    bundle.facts[0].unit = None
    interpretation = _interpretation()
    finding = interpretation["interpretation"]["primary_findings"][0]
    finding["statement"] = "用户声明为合成测试轨迹。拟合窗口被拒绝，不能成立扩散系数。"
    interpretation["interpretation"]["answer_lead"] = finding["statement"]
    finding["scope"] = "用户声明为合成测试轨迹"
    report = DeterministicScientificReportComposer().compose(
        bundle=bundle, interpretation=interpretation, relevance_status="CURRENT",
    )
    assert report.conclusion is not None
    assert report.summary != report.conclusion.text
    assert "扩散拟合" in report.summary
    assert reason in report.conclusion.text
    assert "不能成立扩散系数" in report.conclusion.text
    assert "用户声明为合成测试轨迹" in report.conclusion.text
    assert report.conclusion.fact_refs == [bundle.facts[0].fact_id]
    assert report.main_findings[0].statement == finding["statement"]
    assert ReportGroundingValidator().validate(report, bundle=bundle, interpretation=interpretation) == []


@pytest.mark.parametrize("unavailable", ["unbound", "ambiguous", "unknown", "accepted"])
def test_report_does_not_invent_a_compact_diffusion_verdict(unavailable):
    bundle = _bundle()
    bundle.methods[0].capability_id = "trajectory.diffusion"
    bundle.result_items[0].result_type = "trajectory.diffusion"
    bundle.facts[0].predicate = "trajectory.diffusion_regime"
    bundle.facts[0].value = "INSUFFICIENT_DURATION"
    bundle.facts[0].unit = None
    if unavailable == "unbound":
        bundle.result_items[0].fact_refs = []
    elif unavailable == "ambiguous":
        duplicate = bundle.facts[0].model_copy(update={"fact_id": "second", "value": "POOR_LINEAR_FIT"})
        bundle.facts.append(duplicate)
        bundle.result_items[0].fact_refs.append("second")
    else:
        bundle.facts[0].value = "DIFFUSIVE_WINDOW_ACCEPTED" if unavailable == "accepted" else "FUTURE_STATUS"
    interpretation = _interpretation()
    statement = "当前结果的完整判断和适用限定。"
    interpretation["interpretation"]["answer_lead"] = statement
    interpretation["interpretation"]["primary_findings"][0]["statement"] = statement
    report = DeterministicScientificReportComposer().compose(
        bundle=bundle, interpretation=interpretation, relevance_status="CURRENT",
    )
    assert report.conclusion.text == statement


def test_report_never_truncates_citations_while_retaining_their_claims():
    section = DeterministicScientificReportComposer._narrative_section(
        None, "包含全部测量结果的文字。", fact_refs=[f"fact.{i}" for i in range(33)], evidence_refs=[],
    )
    assert section is None


def test_many_long_scopes_cannot_overflow_the_abstract_or_change_primary_findings():
    interpretation = _interpretation()
    original = interpretation["interpretation"]["primary_findings"][0]
    findings = [{**original, "finding_id": f"finding.{index}", "scope": f"来源{index}：" + "精确版本范围" * 150} for index in range(8)]
    interpretation["interpretation"]["primary_findings"] = findings
    report = DeterministicScientificReportComposer().compose(
        bundle=_bundle(), interpretation=interpretation, relevance_status="CURRENT",
    )
    assert len(report.summary) < 200
    assert len(report.main_findings) == 8
    assert [item.statement for item in report.main_findings] == [item["statement"] for item in findings]
    assert interpretation["interpretation"]["primary_findings"] == findings


def test_opaque_version_and_sample_identifiers_are_not_numeric_claims() -> None:
    payload = _report().model_dump(mode="json")
    payload["summary"] = (
        "依据精确 Dataset 版本 809a6825-5bfe-4820-81fc-b589ba447abc，"
        "RDF 第一峰位于 2.84 Å。"
    )
    payload["main_findings"][0]["statement"] = (
        "RDF 第一峰位于 2.84 Å；来源版本为 "
        "809a6825-5bfe-4820-81fc-b589ba447abc。"
    )
    report = ScientificReportOutput.model_validate(payload)
    assert ReportGroundingValidator().validate(
        report,
        bundle=_bundle(),
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


def test_report_uses_interpretation_title_without_falling_back_to_first_result_item() -> None:
    report = DeterministicScientificReportComposer().compose(
        bundle=_bundle(),
        interpretation=_interpretation(),
        relevance_status="CURRENT",
    )
    assert report.title == "LiFePO4 RDF 第一配位峰分析"


def test_volumetric_method_describes_saved_field_processing_without_new_science() -> None:
    bundle = _bundle()
    bundle.methods[0].capability_id = "volumetric.data"
    bundle.methods[0].tool_id = "structure.volumetric_data"
    report = DeterministicScientificReportComposer().compose(
        bundle=bundle, interpretation=_interpretation(), relevance_status="CURRENT",
    )
    assert report.method_summary == "读取来源中的体数据场，整理网格、物理量与单位，并根据保存的网格数值计算场统计量。"
    assert ReportGroundingValidator().validate(report, bundle=bundle, interpretation=_interpretation()) == []


def test_report_omits_repeated_primary_findings_instead_of_inventing_a_discussion() -> None:
    interpretation = _interpretation()
    interpretation["interpretation"]["primary_findings"].append({
        "finding_id": "finding.rdf_scope",
        "statement": "该结论仅适用于已提交的 RDF 截断范围。",
        "importance": "MEDIUM",
        "confidence": "HIGH",
        "fact_refs": ["rdf.first_peak_position"],
        "evidence_refs": ["evidence.rdf_curve"],
        "result_item_refs": ["rdf.primary"],
    })
    interpretation["interpretation"]["supporting_findings"] = [{
        "finding_id": "finding.figure",
        "statement": "已生成一个可查看图表。",
        "importance": "MEDIUM",
        "confidence": "HIGH",
        "fact_refs": [],
        "evidence_refs": ["evidence.rdf_curve"],
        "result_item_refs": ["rdf.primary"],
    }]
    report = DeterministicScientificReportComposer().compose(
        bundle=_bundle(),
        interpretation=interpretation,
        relevance_status="CURRENT",
    )
    assert report.discussion is None
    assert [finding.statement for finding in report.main_findings] == [
        item["statement"] for item in interpretation["interpretation"]["primary_findings"]
    ]
    assert ReportGroundingValidator().validate(report, bundle=_bundle(), interpretation=interpretation) == []


def test_report_discussion_keeps_distinct_supporting_content_and_its_exact_references():
    interpretation = _interpretation()
    primary = interpretation["interpretation"]["primary_findings"][0]
    supporting = {**primary, "finding_id": "finding.detail", "statement": "该峰仅描述当前来源的局域配位。"}
    interpretation["interpretation"]["supporting_findings"] = [
        {**primary, "finding_id": "finding.duplicate"}, supporting,
    ]
    report = DeterministicScientificReportComposer().compose(bundle=_bundle(), interpretation=interpretation, relevance_status="CURRENT")
    assert report.discussion.text == supporting["statement"]
    assert report.discussion.fact_refs == supporting["fact_refs"]
    assert report.discussion.evidence_refs == supporting["evidence_refs"]


def test_report_discussion_does_not_merge_equal_text_with_different_scope_or_sources():
    interpretation = _interpretation()
    primary = interpretation["interpretation"]["primary_findings"][0]
    for change in ({"scope": "另一来源版本"}, {"fact_refs": ["another.fact"]}):
        interpretation["interpretation"]["supporting_findings"] = [{**primary, **change, "finding_id": "finding.other"}]
        report = DeterministicScientificReportComposer().compose(bundle=_bundle(), interpretation=interpretation, relevance_status="CURRENT")
        assert report.discussion.text == primary["statement"]


def test_report_preserves_explicit_validated_discussion():
    interpretation = _interpretation()
    discussion = {"text": "该峰仅描述当前来源的局域配位。", "fact_refs": ["rdf.first_peak_position"], "evidence_refs": ["evidence.rdf_curve"]}
    interpretation["interpretation"]["discussion"] = discussion
    report = DeterministicScientificReportComposer().compose(bundle=_bundle(), interpretation=interpretation, relevance_status="CURRENT")
    assert report.discussion.model_dump() == discussion
    interpretation["interpretation"]["discussion"] = discussion["text"]
    legacy = DeterministicScientificReportComposer().compose(bundle=_bundle(), interpretation=interpretation, relevance_status="CURRENT")
    assert legacy.discussion.model_dump() == discussion


def test_coordination_report_uses_readable_methods_title_and_absence_limitation() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["methods"] = [
        {
            **payload["methods"][0],
            "method_id": "method.crystalnn",
            "capability_id": "structure.coordination_crystalnn",
        },
        {
            **payload["methods"][0],
            "method_id": "method.voronoinn",
            "capability_id": "structure.coordination_voronoinn",
        },
    ]
    payload["limitations"] = []
    interpretation = _interpretation()
    interpretation["interpretation"]["limitations"] = []
    report = DeterministicScientificReportComposer().compose(
        bundle=ScientificResultBundle.model_validate(payload),
        interpretation=interpretation,
        relevance_status="CURRENT",
    )
    assert report.title == "CrystalNN 与 VoronoiNN 局部配位环境比较"
    assert "使用 CrystalNN" in report.method_summary
    assert "使用 VoronoiNN" in report.method_summary
    assert "方法信息来自已验证" not in report.method_summary
    assert [item.statement for item in report.limitations] == [
        "ScientificResult 未提供额外方法限制；报告不补充未来源的算法常识。",
    ]


def test_report_contains_bounded_discussion_conclusion_and_next_steps() -> None:
    interpretation = _interpretation()
    interpretation["interpretation"]["supporting_findings"] = [{
        "finding_id": "finding.rdf_support",
        "statement": "峰形来自已提交的 RDF 曲线证据。",
        "fact_refs": ["rdf.first_peak_position"],
        "evidence_refs": ["evidence.rdf_curve"],
    }]
    interpretation["interpretation"]["follow_up_suggestions"] = ["在相同来源版本上比较另一种截断范围。"]
    report = DeterministicScientificReportComposer().compose(
        bundle=_bundle(),
        interpretation=interpretation,
        relevance_status="CURRENT",
    )
    assert report.discussion is not None
    assert report.discussion.fact_refs == ["rdf.first_peak_position"]
    assert report.conclusion is not None
    assert report.conclusion.fact_refs == ["rdf.first_peak_position"]
    assert report.next_steps is not None
    assert "另一种截断范围" in report.next_steps.text
    assert ReportGroundingValidator().validate(report, bundle=_bundle(), interpretation=interpretation) == []


def test_xrd_report_contains_grounded_discussion_conclusion_and_limitations() -> None:
    bundle, interpretation = _xrd_bundle_and_interpretation()
    report = DeterministicScientificReportComposer().compose(
        bundle=bundle,
        interpretation=interpretation,
        relevance_status="CURRENT",
    )

    assert report.discussion is None
    assert report.conclusion is not None
    assert "17 个峰" in report.conclusion.text
    assert report.conclusion.fact_refs == ["xrd.matched_peak_count"]
    assert report.limitations
    assert ReportGroundingValidator().validate(
        report,
        bundle=bundle,
        interpretation=interpretation,
    ) == []


def test_provider_report_is_projected_back_to_validated_scientific_authority() -> None:
    bundle_payload = _bundle().model_dump(mode="json")
    bundle_payload["research_question"] = "比较精确结构版本 obj_1 的局域环境。"
    bundle = ScientificResultBundle.model_validate(bundle_payload)
    provider_payload = _report().model_dump(mode="json")
    provider_payload.update({
        "research_question": "比较精确结构版本 obj_1 的局域环境。",
        "summary": "Provider 自行扩展的摘要。",
        "discussion": {
            "text": "Provider 推断该方法非常准确。",
            "fact_refs": ["rdf.first_peak_position"],
            "evidence_refs": ["evidence.rdf_curve"],
        },
        "conclusion": {
            "text": "该方法在此结构上有效且可靠。",
            "fact_refs": ["rdf.first_peak_position"],
            "evidence_refs": ["evidence.rdf_curve"],
        },
        "data_sources": [],
    })
    interpretation = _interpretation()
    interpretation["interpretation"]["primary_findings"][0]["statement"] += (
        "（rdf.first_peak_position）"
    )
    projected = ScientificReportService._project_authoritative_report(
        ScientificReportOutput.model_validate(provider_payload),
        bundle=bundle,
        interpretation=interpretation,
        relevance_status="CURRENT",
        source_labels=["LiFePO4 结构"],
    )
    assert projected.research_question == "比较精确结构版本 LiFePO4 结构 的局域环境。"
    assert "径向分布函数" in projected.summary
    assert "Provider" not in projected.summary
    assert projected.summary != projected.conclusion.text
    assert projected.conclusion is not None
    assert projected.conclusion.text == "RDF 第一峰位于 2.84 Å。"
    assert "有效" not in projected.conclusion.text
    assert "rdf.first_peak_position" not in projected.summary
    assert "rdf.first_peak_position" not in projected.main_findings[0].statement
    assert projected.data_sources == ["source_1"]
    assert ReportGroundingValidator().validate(
        projected,
        bundle=bundle,
        interpretation=_interpretation(),
    ) == []


def test_report_narrative_sections_remain_fail_closed_for_unsupported_claims() -> None:
    payload = _report().model_dump(mode="json")
    payload["discussion"] = {
        "text": "RDF 第一峰位于 9.99 Å。",
        "fact_refs": ["rdf.first_peak_position"],
        "evidence_refs": ["evidence.rdf_curve"],
    }
    report = ScientificReportOutput.model_validate(payload)
    errors = ReportGroundingValidator().validate(report, bundle=_bundle(), interpretation=_interpretation())
    assert any("discussion contains an unsupported numeric claim" in error for error in errors)


@pytest.mark.parametrize("upstream_has_invalid_suggestion", [False, True])
def test_elf_report_does_not_promote_unvalidated_method_recommendations(upstream_has_invalid_suggestion):
    from mdi_api.application.scientific_results.projectors.volumetric import volumetric_field_limitations

    bundle = _bundle()
    bundle.limitations = volumetric_field_limitations("artifact_private_123", {"quantity": "electron_localization_function"})
    incorrect = "使用 Bader 分析处理该 ELF 场以获得电子计数。"
    interpretation = _interpretation()
    if upstream_has_invalid_suggestion:
        interpretation["interpretation"]["follow_up_suggestions"] = [incorrect]
    payload = _report().model_dump(mode="json")
    payload["next_steps"] = {"text": incorrect, "fact_refs": ["rdf.first_peak_position"], "evidence_refs": ["evidence.rdf_curve"]}
    provider_output = ScientificReportOutput.model_validate(payload)
    assert any("next_steps must copy" in error for error in ReportGroundingValidator().validate(
        provider_output, bundle=bundle, interpretation=interpretation,
    ))
    before = json.dumps(interpretation, sort_keys=True)
    projected = ScientificReportService._project_authoritative_report(
        provider_output, bundle=bundle, interpretation=interpretation,
        relevance_status="CURRENT", source_labels=["ELF"],
    )
    assert projected.next_steps is None
    assert "Bader" not in projected.model_dump_json()
    assert json.dumps(interpretation, sort_keys=True) == before
    assert provider_output.next_steps.text == incorrect
    context, _ = ReportComposerInputAssembler().assemble(bundle=bundle, interpretation=interpretation, relevance_status="CURRENT")
    assert context["interpretation"]["follow_up_suggestions"] == []
    assert context["interpretation"]["report_next_steps_text"] is None


@pytest.mark.parametrize("repair_succeeds", [True, False])
def test_report_recommendation_invention_requires_one_bounded_repair(repair_succeeds):
    interpretation = _interpretation()
    suggestion = "在相同来源版本上比较另一种截断范围。"
    interpretation["interpretation"]["follow_up_suggestions"] = [suggestion]
    valid = _report().model_dump(mode="json")
    valid["next_steps"] = {"text": suggestion, "fact_refs": [], "evidence_refs": []}
    invalid = {**valid, "next_steps": {"text": suggestion + "该方法会证明材料稳定。", "fact_refs": [], "evidence_refs": []}}

    class RecordingClient(FakeStructuredReportComposerClient):
        async def generate_structured(self, **kwargs):
            schema = kwargs["output_schema"]
            assert schema["properties"]["next_steps"]["anyOf"][1]["properties"]["text"]["const"] == suggestion
            assert "const" not in schema["$defs"]["ReportNarrativeSection"]["properties"]["text"]
            return await super().generate_structured(**kwargs)

    client = RecordingClient([invalid, valid if repair_succeeds else invalid])
    service = ScientificReportService(repository_factory=object(), client=client)
    if repair_succeeds:
        output, _, repaired = service._compose_with_one_repair(input_payload={}, bundle=_bundle(), interpretation=interpretation)
        assert repaired and output.next_steps.text == suggestion
    else:
        with pytest.raises(ScientificReportError, match="next_steps must copy"):
            service._compose_with_one_repair(input_payload={}, bundle=_bundle(), interpretation=interpretation)
    assert client.calls == 2


def test_report_narrative_numeric_claim_requires_explicit_fact_binding() -> None:
    payload = _report().model_dump(mode="json")
    payload["next_steps"] = {
        "text": "后续应把温度设为 300 K。",
        "fact_refs": [],
        "evidence_refs": [],
    }
    report = ScientificReportOutput.model_validate(payload)
    errors = ReportGroundingValidator().validate(report, bundle=_bundle(), interpretation=_interpretation())
    assert any("next_steps contains an unsupported numeric claim" in error for error in errors)


@pytest.mark.parametrize("text", ["后续需要补充能带和 K 点身份信息。", "Explicit K-point metadata is needed before assigning an orbital."])
def test_report_k_point_metadata_recommendation_needs_no_temperature_fact(text) -> None:
    payload = _report().model_dump(mode="json")
    payload["next_steps"] = {"text": text, "fact_refs": [], "evidence_refs": []}
    validator = ReportGroundingValidator()
    interpretation = _interpretation()
    interpretation["interpretation"]["follow_up_suggestions"] = [text]
    assert validator.validate(ScientificReportOutput.model_validate(payload), bundle=_bundle(), interpretation=interpretation) == []

    for addition in ("温度单位为 K。", "温度为 300 K。", "采样 81 个 K 点。", "能量单位为 eV。"):
        payload["next_steps"]["text"] = text + addition
        errors = validator.validate(ScientificReportOutput.model_validate(payload), bundle=_bundle(), interpretation=_interpretation())
        assert any(error.startswith("next_steps contains an unsupported") for error in errors)


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


def test_report_replaces_only_invalid_abstract_with_validated_scope_after_repair():
    payload = _report().model_dump(mode="json")
    payload["summary"] = "列出了 9 个样本。"
    client = FakeStructuredReportComposerClient([payload, payload])
    service = ScientificReportService(repository_factory=object(), client=client)
    output, _, repaired = service._compose_with_one_repair(input_payload={}, bundle=_bundle(), interpretation=_interpretation())
    assert repaired and client.calls == 2
    assert output.summary != payload["summary"] and "9" not in output.summary
    assert output.main_findings == _report().main_findings
    assert ReportGroundingValidator().validate(output, bundle=_bundle(), interpretation=_interpretation()) == []
    payload["main_findings"][0]["statement"] = "列出了 9 个样本。"
    service.client = FakeStructuredReportComposerClient([payload, payload])
    with pytest.raises(ScientificReportError, match="finding contains an unsupported"):
        service._compose_with_one_repair(input_payload={}, bundle=_bundle(), interpretation=_interpretation())


def test_report_caption_repair_can_remove_unreferenced_measurements_without_dropping_findings():
    valid = _report().model_dump(mode="json")
    invalid = json.loads(json.dumps(valid))
    invalid["primary_figures"][0].update({"caption": "MSD over 0.398 ps.", "fact_refs": [], "evidence_refs": []})
    contexts = []

    class RecordingClient(FakeStructuredReportComposerClient):
        async def generate_structured(self, **kwargs):
            contexts.append(kwargs["request_context"])
            return await super().generate_structured(**kwargs)

    client = RecordingClient([invalid, valid])
    service = ScientificReportService(repository_factory=object(), client=client)
    output, _, repaired = service._compose_with_one_repair(input_payload={}, bundle=_bundle(), interpretation=_interpretation())
    assert repaired and client.calls == 2
    guidance = contexts[1]["repair"]["figure_caption_guidance"]
    assert "qualitative" in guidance and "main_findings" in guidance
    assert output.main_findings[0].statement == valid["main_findings"][0]["statement"]
    assert output.primary_figures[0].figure_ref == invalid["primary_figures"][0]["figure_ref"]


@pytest.mark.parametrize("section", ["discussion", "conclusion"])
@pytest.mark.parametrize("repair_succeeds", [True, False])
def test_oversized_report_narrative_is_repaired_without_echoing_inputs(section, repair_succeeds):
    valid = _report().model_dump(mode="json")
    invalid = {**valid, section: {"text": "A short synthesis.", "fact_refs": ["private-rejected-input"] * 41, "evidence_refs": []}}
    contexts = []

    class RecordingClient(FakeStructuredReportComposerClient):
        async def generate_structured(self, **kwargs):
            contexts.append(kwargs["request_context"])
            assert kwargs["output_schema"]["$defs"]["ReportNarrativeSection"]["properties"]["fact_refs"]["maxItems"] == 32
            return await super().generate_structured(**kwargs)

    client = RecordingClient([invalid, valid if repair_succeeds else invalid])
    service = ScientificReportService(repository_factory=object(), client=client)
    if repair_succeeds:
        output, _, repaired = service._compose_with_one_repair(input_payload={}, bundle=_bundle(), interpretation=_interpretation())
        assert repaired and output.title
    else:
        with pytest.raises(ScientificReportError) as caught:
            service._compose_with_one_repair(input_payload={}, bundle=_bundle(), interpretation=_interpretation())
        assert caught.value.code == "REPORT_SCHEMA_INVALID"
    assert client.calls == 2
    feedback = json.dumps(contexts[1]["repair"])
    assert f"{section}.fact_refs" in feedback and "32" in feedback and "41" in feedback
    assert "private-rejected-input" not in feedback
    assert "Do not truncate citations" in feedback
    assert "main_findings" in feedback
    assert len(invalid[section]["fact_refs"]) == 41


@pytest.mark.parametrize("repair_succeeds", [True, False])
def test_limitation_reference_repair_names_only_supplied_limitations(repair_succeeds):
    valid = _report().model_dump(mode="json")
    invalid = {**valid, "limitations": [{"statement": "Saved limitation", "source_refs": ["finding.limitation"]}]}
    contexts = []

    class RecordingClient(FakeStructuredReportComposerClient):
        async def generate_structured(self, **kwargs):
            contexts.append(kwargs["request_context"])
            reference_schema = kwargs["output_schema"]["$defs"]["ReportLimitation"]["properties"]["source_refs"]
            assert reference_schema["items"]["enum"] == source_ids
            return await super().generate_structured(**kwargs)

    client = RecordingClient([invalid, valid if repair_succeeds else invalid])
    service = ScientificReportService(repository_factory=object(), client=client)
    source_ids = [item.limitation_id for item in _bundle().limitations]
    payload = {"opaque_refs": {"limitations": source_ids, "findings": ["finding.limitation"]}}
    if repair_succeeds:
        _, _, repaired = service._compose_with_one_repair(input_payload=payload, bundle=_bundle(), interpretation=_interpretation())
        assert repaired
    else:
        with pytest.raises(ScientificReportError, match="limitation.source_refs"):
            service._compose_with_one_repair(input_payload=payload, bundle=_bundle(), interpretation=_interpretation())
    assert client.calls == 2
    assert contexts[0]["repair"] is None
    guidance = contexts[1]["repair"]["limitation_reference_guidance"]
    assert guidance["supplied_limitation_ids"] == source_ids
    assert "finding.limitation" not in guidance["supplied_limitation_ids"]
    assert invalid["limitations"][0]["source_refs"] == ["finding.limitation"]


@pytest.mark.parametrize("code", ["PROVIDER_TIMEOUT", "DEEPSEEK_TIMEOUT", "LLM_TIMEOUT", "OPENAI_TIMEOUT", "PROVIDER_RATE_LIMITED", "PROVIDER_AUTH_FAILED", "PROVIDER_REQUEST_REJECTED", "PROVIDER_OUTPUT_TRUNCATED", "PROVIDER_INVALID_RESPONSE", "EXTERNAL_UNAVAILABLE", "UNKNOWN_PRIVATE_CODE"])
def test_report_provider_failure_retains_only_reviewed_diagnostic(code):
    from mdi_llm.providers import LLMProviderError

    class FailedClient:
        async def generate_structured(self, **kwargs):
            raise LLMProviderError("private upstream body must not appear", code=code)

    service = ScientificReportService(repository_factory=object(), client=FailedClient())
    with pytest.raises(ScientificReportError) as caught:
        service._compose_with_one_repair(input_payload={}, bundle=_bundle(), interpretation=_interpretation())
    expected = "REPORT_PROVIDER_TIMEOUT" if code in {"PROVIDER_TIMEOUT", "DEEPSEEK_TIMEOUT", "LLM_TIMEOUT", "OPENAI_TIMEOUT"} else "REPORT_COMPOSITION_FAILED" if code == "UNKNOWN_PRIVATE_CODE" else f"REPORT_{code}"
    assert caught.value.code == expected
    assert "private" not in str(caught.value)
    assert caught.value.__suppress_context__


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
    assert result.parsed["contract_version"] == "2.0"
    assert provider.call_audit[-1]["purpose"] == "REPORT_COMPOSITION"


@pytest.mark.parametrize("role,expected_tokens", [("scientific_report_composer", 6144), ("research_orchestrator", 4096)])
def test_report_output_budget_applies_to_account_connection_without_mutating_selection(monkeypatch, role, expected_tokens):
    from types import SimpleNamespace
    from uuid import uuid4
    from mdi_llm.providers import PlannerRawResponse, PlannerUserConfig
    from mdi_api import user_models

    captured = []
    config = PlannerUserConfig(model="selected-model", max_tokens=4096, thinking_mode="standard")

    class CapturingProvider:
        meta = SimpleNamespace(model="selected-model")

        def complete_json(self, *, user_config, **kwargs):
            captured.append(user_config)
            return PlannerRawResponse(raw_json={"ok": True}, raw_text=None, model=user_config.model, finish_reason="stop")

    provider = CapturingProvider()
    monkeypatch.setattr(user_models, "selection_for_turn", lambda _turn: {"model": "selected-model"})
    monkeypatch.setattr(user_models, "resolve_user_selection", lambda *_args: (provider, config))
    client = DeepSeekStructuredLLMClient(provider, turn_id=str(uuid4()))
    asyncio.run(client.generate_structured(
        role=role, system_prompt="Return JSON.", input_payload={}, output_schema={}, timeout_seconds=30,
    ))

    assert captured[0].max_tokens == expected_tokens
    assert captured[0].model == "selected-model"
    assert captured[0].thinking_mode == "standard"
    assert config.max_tokens == 4096


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
    assert created["research_session_id"] == "session_1"
    assert client.calls == 1
    assert scientific_counts() == before
    assert service.get_by_report_id(created["report_id"])["report"] == created["report"]
    revision = service.create_revision(
        created["report_id"],
        created_by=owner.id,
        title="LiFePO4 RDF 科学报告（修订 2）",
    )
    original_after_revision = service.get_by_report_id(created["report_id"])
    assert revision["report_id"] != created["report_id"]
    assert revision["snapshot_id"] != created["snapshot_id"]
    assert revision["revision_group_id"] == created["report_id"]
    assert revision["parent_report_id"] == created["report_id"]
    assert revision["parent_snapshot_id"] == created["snapshot_id"]
    assert revision["revision_number"] == 2
    assert revision["title"] == "LiFePO4 RDF 科学报告（修订 2）"
    assert revision["scientific_result_snapshot_id"] == created["scientific_result_snapshot_id"]
    assert revision["scientific_interpretation_id"] == created["scientific_interpretation_id"]
    assert original_after_revision["report"] == created["report"]
    assert scientific_counts() == before
    revisions = service.list_revisions(revision["report_id"])
    assert [item["revision_number"] for item in revisions["items"]] == [1, 2]
    comparison = service.compare_revisions(revision["report_id"])
    assert comparison["base_report_id"] == created["report_id"]
    assert comparison["scientific_authority_unchanged"] is True
    assert comparison["source_versions_unchanged"] is True
    assert comparison["changed_sections"] == ["title"]
    assert comparison["added_findings"] == []
    assert comparison["removed_findings"] == []
    with factory.session() as session:
        manifests = [
            event["payload_json"]["context_manifest"]
            for event in session.agent2.research_turn_events.list_for_turn(received.turn_id)
            if event["event_type"] == "CONTEXT_MANIFEST_RECORDED"
            and (event.get("payload_json") or {}).get("operation") == "REPORT"
        ]
    assert len(manifests) == 1
    assert manifests[0]["operation"] == "REPORT"
    assert manifests[0]["input_state"] == "ACTUAL"
    assert manifests[0]["invocation_role"] == "scientific_report_composer"
    assert manifests[0]["serialized_input"]
    assert manifests[0]["serialized_input_fingerprint"]
    assert any(
        item["kind"] == "SCIENTIFIC_RESULT"
        and item["result_ref"] == str(snapshot_id)
        for item in manifests[0]["included_items"]
    )


@pytest.mark.parametrize("multi_source", [False, True])
def test_report_viewer_sources_are_derived_only_from_result_provenance(multi_source) -> None:
    source = _bundle().source_object_refs[0]

    class Objects:
        def get_object(self, object_id):
            assert str(object_id) == str(source.object_id)
            return {
                "id": str(source.object_id),
                "project_id": source.project_id,
                "display_name": "LiFePO4",
                "current_version_id": str(source.version_id),
                "lifecycle_status": "ARCHIVED",
            }

        def get_version(self, version_id):
            assert str(version_id) == str(source.version_id)
            return {"id": str(source.version_id), "scientific_object_id": str(source.object_id), "object_type": source.object_type}

    class Snapshots:
        def __init__(self, bundle):
            self.bundle = bundle

        def get(self, _snapshot_id):
            return {"id": _snapshot_id, "project_id": "project_1", "research_turn_id": TURN_ID, "bundle_json": self.bundle}

    class Interpretations:
        def get(self, _interpretation_id):
            return {"id": _interpretation_id, "project_id": "project_1", "research_turn_id": TURN_ID, "result_snapshot_id": "snapshot-1", "output_json": _interpretation()}

    class Agent2:
        def __init__(self, bundle):
            self.scientific_result_snapshots = Snapshots(bundle)
            self.scientific_objects = Objects()
            self.interpretations = Interpretations()

    class Session:
        def __init__(self, bundle):
            self.agent2 = Agent2(bundle)

    row = {
        "scientific_result_snapshot_id": "snapshot-1",
        "scientific_interpretation_id": str(UUID("98989898-9898-4989-8989-989898989898")),
        "project_id": "project_1", "research_turn_id": TURN_ID,
        "relevance_at_generation": "CURRENT",
    }
    view_bundle = _bundle().model_dump(mode="json")
    if multi_source:
        view_bundle["source_object_refs"].append({
            **view_bundle["source_object_refs"][0],
            "object_id": str(UUID(int=1024)), "version_id": str(UUID(int=2048)),
            "display_name": "other.cif",
        })
        view_bundle["source_object_refs"][0]["display_name"] = "exact-source.cif"
    view_bundle["research_question"] = "比较 obj_1 的局域环境。"
    fresh = ScientificReportService._with_viewer_sources({
        "report": {
            **_report().model_dump(mode="json"),
            "research_question": "比较 obj_1 的局域环境。",
            "conclusion": {
                "text": "该方法在此结构上有效且可靠。",
                "fact_refs": ["rdf.first_peak_position"],
                "evidence_refs": ["evidence.rdf_curve"],
            },
            "data_sources": [],
        },
    }, Session(view_bundle), row)
    assert fresh["viewer_sources"] == [{
        "source_ref": "source_1",
        "object_id": str(source.object_id),
        "version_id": str(source.version_id),
        "object_type": source.object_type,
        "display_name": "exact-source.cif" if multi_source else "LiFePO4",
        "is_current_version": True,
        "lifecycle_status": "ARCHIVED",
    }]
    assert fresh["figure_sources"] == [{
        "figure_ref": "figure.rdf_curve",
        "artifact_ids": ["artifact_private_123"],
        "job_id": "job_private_123",
    }]
    assert fresh["table_sources"] == []
    assert fresh["report"]["research_question"] == f"比较 {'exact-source.cif' if multi_source else 'LiFePO4'} 的局域环境。"
    assert fresh["report"]["data_sources"] == ["source_1"]
    assert fresh["report"]["conclusion"]["text"] == "RDF 第一峰位于 2.84 Å。"

    legacy_bundle = _bundle().model_copy(update={"source_object_refs": []}).model_dump(mode="json")
    legacy = ScientificReportService._with_viewer_sources({}, Session(legacy_bundle), row)
    assert legacy["viewer_sources"] == []
    assert legacy["figure_sources"] == [{
        "figure_ref": "figure.rdf_curve",
        "artifact_ids": ["artifact_private_123"],
        "job_id": "job_private_123",
    }]
    assert legacy["table_sources"] == []


@pytest.mark.parametrize("case,expected", [("bound", "真实值与预测值"), ("foreign", "材料回归评估"), ("unlisted", "材料回归评估"), ("caption", "已有图注及其科学限定")])
@pytest.mark.parametrize("family", ["regression", "table"])
def test_historical_report_projects_generic_figure_titles_without_rewriting_saved_science(case, expected, family):
    from types import SimpleNamespace as NS
    title = "材料回归评估" if family == "regression" else "数值表格分布与相关性分析"
    if family == "table":
        expected = {"bound": "Spearman 相关矩阵", "foreign": title, "unlisted": title, "caption": "已有图注及其科学限定"}[case]
    saved = _bundle().model_dump(mode="json")
    saved["figures"][0].update(title=title, caption_seed="已有图注及其科学限定" if case == "caption" else None)
    saved["tables"] = [{"table_id": "table.metrics", "table_type": "ml.regression.evaluation" if family == "regression" else "data.table_analysis", "title": title, "role": "PRIMARY", "artifact_ids": ["metrics"], "fact_refs": [], "evidence_refs": []}]
    saved["provenance"]["artifact_ids"].append("metrics")
    if case == "unlisted": saved["provenance"]["tool_call_ids"] = []
    artifact = {"id": "artifact_private_123", "jobId": "job_private_123", "projectId": "foreign" if case == "foreign" else "project_1", "type": "plotly_json", "toolCallId": "toolcall_private_123"}
    call = {"id": "toolcall_private_123", "jobId": "job_private_123", "toolId": "ml.density_scatter" if family == "regression" else "viz.correlation", "state": "COMPLETED", "paramsJson": {"method": "spearman"}}
    metrics = {**artifact, "id": "metrics", "type": "metrics_json" if family == "regression" else "table_json"}
    metric_call = {**call, "id": "metrics-call", "toolId": "ml.error_distribution" if family == "regression" else "table.numeric_summary"}
    metrics["toolCallId"] = metric_call["id"]
    if case != "unlisted": saved["provenance"]["tool_call_ids"].append(metric_call["id"])
    before = json.dumps(saved)
    session = NS(agent2=NS(
        scientific_result_snapshots=NS(get=lambda identity: {"id": identity, "project_id": "project_1", "research_turn_id": TURN_ID, "bundle_json": saved}),
        interpretations=NS(get=lambda identity: {"id": identity, "project_id": "project_1", "research_turn_id": TURN_ID, "result_snapshot_id": RESULT_ID, "output_json": _interpretation()}),
    ), repositories=NS(artifacts=NS(list_for_job=lambda _: [artifact, metrics]), tool_calls=NS(list_for_job=lambda _: [call, metric_call])))
    row = {"scientific_result_snapshot_id": str(RESULT_ID), "scientific_interpretation_id": str(TURN_ID), "project_id": "project_1", "research_turn_id": TURN_ID}
    view = ScientificReportService._with_viewer_sources({"report": _report().model_dump(mode="json")}, session, row)
    assert view["report"]["primary_figures"][0]["caption"] == expected
    assert view["table_sources"][0]["title"] == (title if case in {"foreign", "unlisted"} else "回归评估指标（残差分析）" if family == "regression" else "数值统计")
    assert json.dumps(saved) == before


@pytest.mark.parametrize("execution", [None, "owned", "foreign_project", "conflicting_plan", "missing_job"])
@pytest.mark.parametrize("file_result_type", [None, "trajectory.viewer", "volumetric.field", "phonon.band", "structure.viewer_scene"])
def test_report_exposes_result_tables_with_exact_artifact_and_source_refs(file_result_type: str | None, execution) -> None:
    payload = _bundle().model_dump(mode="json")
    payload["tables"] = [{
        "table_id": "diffusion.diagnostic",
        "table_type": "trajectory_diffusion_diagnostic",
        "role": "PRIMARY",
        "title": "扩散拟合诊断",
        "artifact_ids": ["artifact_diffusion_table"],
        "fact_refs": ["rdf.first_peak_position"],
        "evidence_refs": ["evidence.rdf_curve"],
    }]
    payload["result_items"][0]["artifact_ids"].append("artifact_diffusion_table")
    payload["provenance"]["artifact_ids"].append("artifact_diffusion_table")
    if file_result_type:
        payload["tables"][0]["table_type"] = file_result_type
        payload["result_items"][0]["result_type"] = file_result_type
    payload["provenance"]["analysis_plan_id"] = "other" if execution == "conflicting_plan" else ""
    bundle = ScientificResultBundle.model_validate(payload).model_dump(mode="json")

    class Objects:
        def get_object(self, object_id):
            return {
                "id": str(object_id),
                "project_id": "project_1",
                "display_name": "LiFePO4",
                "current_version_id": str(VERSION_ID),
                "lifecycle_status": "ACTIVE",
            }

        def get_version(self, version_id):
            return {"id": str(version_id), "scientific_object_id": str(OBJECT_ID), "object_type": "structure.crystal"}

    class Snapshots:
        def get(self, _snapshot_id):
            return {"id": _snapshot_id, "project_id": "project_1", "research_turn_id": TURN_ID, "bundle_json": bundle}

    class Agent2:
        scientific_result_snapshots = Snapshots()
        scientific_objects = Objects()
        interpretations = None

    class Session:
        agent2 = Agent2()

    class Artifacts:
        def list_for_job(self, job_id):
            assert job_id == "job_private_123"
            return [
                {"id": "artifact_diffusion_table", "toolCallId": "call-table", "jobId": job_id, "projectId": bundle["project_id"], "name": "trajectory_summary.json", "type": "structure_json" if file_result_type == "structure.viewer_scene" else "phonon_summary_json" if file_result_type == "phonon.band" else "table_json"},
                {"id": payload["result_items"][0]["artifact_ids"][0], "jobId": "foreign", "projectId": bundle["project_id"], "name": "wrong.json"},
            ]

    class Repositories:
        artifacts = Artifacts()

    class Jobs:
        def get(self, job_id):
            assert job_id == "job_private_123"
            if execution == "missing_job":
                raise LookupError(job_id)
            return {"projectId": "other" if execution == "foreign_project" else bundle["project_id"], "planId": "plan-owned"}

    class Plans:
        def get_plan(self, plan_id):
            assert plan_id == "plan-owned"
            return {"planId": plan_id, "projectId": bundle["project_id"], "analysisPlan": {"steps": [
                {"stepId": "s1", "toolId": "diagnostic", "inputRefs": [{"refType": "normalized_object", "ref": str(VERSION_ID)}]}
            ]}}

    class Calls:
        def list_for_job(self, job_id):
            return [{"id": "call-table", "jobId": job_id, "stepId": "s1", "toolId": "diagnostic"}]

    session = Session()
    session.repositories = Repositories()
    if execution:
        session.repositories.jobs = Jobs()
        session.repositories.analysis_plans = Plans()
        session.repositories.tool_calls = Calls()
    view = ScientificReportService._with_viewer_sources(
        {}, session, {"scientific_result_snapshot_id": "snapshot-1", "project_id": "project_1", "research_turn_id": TURN_ID},
    )
    if file_result_type == "structure.viewer_scene":
        assert view["table_sources"] == []
        assert any(f["artifact_ids"] == ["artifact_diffusion_table"] for f in view["figure_sources"])
        scene = next(f for f in view["figure_sources"] if f["artifact_ids"] == ["artifact_diffusion_table"])
        if execution == "owned":
            assert scene["version_id"] == str(VERSION_ID)
            assert scene["object_type"] == "structure.crystal"
        else:
            assert "version_id" not in scene
        assert bundle["figures"] == payload["figures"]
        assert not any(f["artifact_id"] == "artifact_diffusion_table" for f in view["file_sources"])
        return
    if file_result_type:
        titles = {item["artifact_id"]: item["title"] for item in view["file_sources"]}
        assert titles["artifact_diffusion_table"] == "trajectory_summary.json"
        assert "wrong.json" not in titles.values()
        assert view["table_sources"] == []
        expected_files = {"artifact_diffusion_table"} if file_result_type == "phonon.band" else set(payload["result_items"][0]["artifact_ids"])
        assert {item["artifact_id"] for item in view["file_sources"]} == expected_files
        assert all(item["job_id"] == "job_private_123" for item in view["file_sources"])
        assert bundle["tables"][0]["table_type"] == file_result_type
        return
    assert view["file_sources"] == []
    assert view["table_sources"] == [{
        "table_ref": "diffusion.diagnostic",
        "title": "扩散拟合诊断",
        "artifact_ids": ["artifact_diffusion_table"],
        "job_id": "job_private_123",
        "source_refs": [{"object_id": str(OBJECT_ID), "version_id": str(VERSION_ID), "object_type": "structure.crystal"}] if execution == "owned" else [],
    }]
    assert bundle["provenance"]["analysis_plan_id"] == ("other" if execution == "conflicting_plan" else "")


@pytest.mark.parametrize("invalid", [None, "foreign_project", "foreign_job", "missing_call", "duplicate_call", "wrong_tool", "wrong_plan"])
def test_report_table_sources_follow_owned_execution_inputs(invalid):
    from mdi_api.application.scientific_reports.artifact_sources import artifact_input_versions
    artifacts = {"band": {"jobId": "job", "projectId": "p", "toolCallId": "call-band"},
                 "dos": {"jobId": "job", "projectId": "p", "toolCallId": "call-dos"}}
    calls = [{"id": "call-band", "jobId": "job", "stepId": "s1", "toolId": "band"},
             {"id": "call-dos", "jobId": "job", "stepId": "s2", "toolId": "dos"}]
    plan = {"planId": "plan", "projectId": "p", "analysisPlan": {"steps": [
        {"stepId": "s1", "toolId": "band", "inputRefs": [{"refType": "normalized_object", "ref": "band-version"}]},
        {"stepId": "s2", "toolId": "dos", "inputRefs": [{"refType": "normalized_object", "ref": "dos-version"}]},
    ]}}
    if invalid == "foreign_project": artifacts["band"]["projectId"] = "other"
    if invalid == "foreign_job": calls[0]["jobId"] = "other"
    if invalid == "missing_call": calls.pop(0)
    if invalid == "duplicate_call": calls.append(dict(calls[0]))
    if invalid == "wrong_tool": calls[0]["toolId"] = "other"
    if invalid == "wrong_plan": plan["planId"] = "other"
    args = dict(artifacts=artifacts, calls=calls, plan=plan, project_id="p", job_id="job", plan_id="plan")
    assert artifact_input_versions(artifact_ids=["band"], **args) == (set() if invalid else {"band-version"})
    if invalid is None:
        assert artifact_input_versions(artifact_ids=["dos"], **args) == {"dos-version"}
        assert artifact_input_versions(artifact_ids=["band", "dos"], **args) == {"band-version", "dos-version"}

def test_report_resolves_the_exact_result_bound_to_a_reinterpretation() -> None:
    snapshot_id = UUID("69696969-6969-4696-8696-696969696969")

    class Snapshots:
        def get(self, received_snapshot_id):
            assert received_snapshot_id == snapshot_id
            return {
                "id": snapshot_id,
                "project_id": "project-1",
                "bundle_json": _bundle().model_dump(mode="json"),
            }

    class Agent2:
        scientific_result_snapshots = Snapshots()

    class Session:
        agent2 = Agent2()

    snapshot = ScientificReportService._snapshot_for_interpretation(
        Session(),
        turn={"project_id": "project-1"},
        interpretation={"result_snapshot_id": snapshot_id},
    )
    assert snapshot["id"] == snapshot_id

    with pytest.raises(ScientificReportError) as mismatch:
        ScientificReportService._snapshot_for_interpretation(
            Session(),
            turn={"project_id": "project-2"},
            interpretation={"result_snapshot_id": snapshot_id},
        )
    assert mismatch.value.code == "REPORT_RESULT_PROJECT_MISMATCH"


def test_report_status_is_non_exceptional_before_request_and_ready_after_persistence() -> None:
    turn_id = UUID("71717171-7171-4717-8717-717171717171")

    class Reports:
        row = None

        def get_for_turn(self, received_turn_id):
            assert received_turn_id == turn_id
            return self.row

    class Generations:
        row = None

        def get_for_turn(self, received_turn_id):
            assert received_turn_id == turn_id
            return self.row

    class Agent2:
        def __init__(self):
            self.scientific_reports = Reports()
            self.scientific_report_generations = Generations()

    class Session:
        def __init__(self, agent2):
            self.agent2 = agent2

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    class Factory:
        def __init__(self):
            self.agent2 = Agent2()

        def session(self):
            return Session(self.agent2)

    factory = Factory()
    service = ScientificReportService(factory)  # type: ignore[arg-type]

    assert service.status_for_turn(turn_id) == {
        "research_turn_id": str(turn_id),
        "status": "NOT_REQUESTED",
        "report_id": None,
        "generation_id": None,
        "attempt_count": 0,
        "error_code": None,
        "updated_at": None,
    }

    factory.agent2.scientific_report_generations.row = {
        "id": UUID("72727272-7272-4727-8727-727272727272"),
        "status": "COMPOSING",
        "attempt_count": 1,
        "error_code": None,
        "updated_at": "2026-08-30T00:00:00Z",
    }
    composing = service.status_for_turn(turn_id)
    assert composing["status"] == "COMPOSING"
    assert composing["generation_id"] == "72727272-7272-4727-8727-727272727272"

    factory.agent2.scientific_reports.row = {
        "report_id": "report_status_fixture",
        "created_at": "2026-08-30T00:01:00Z",
    }
    ready = service.status_for_turn(turn_id)
    assert ready["status"] == "READY"
    assert ready["report_id"] == "report_status_fixture"

def test_failed_report_retry_returns_to_requested_before_queueing() -> None:
    from datetime import datetime, timezone
    turn_id = UUID("73737373-7373-4737-8737-737373737373")
    generation_id = UUID("74747474-7474-4747-8747-747474747474")

    class Generations:
        def create(self, _values):
            return {
                "id": generation_id,
                "project_id": "project-1",
                "research_turn_id": turn_id,
                "status": "FAILED",
                "attempt_count": 1,
                "error_code": "REPORT_GENERATION_FAILED",
                "error_summary": "previous failure",
                "updated_at": datetime.now(timezone.utc),
            }

        def compare_status(self, received_id, status, **_kwargs):
            assert received_id == generation_id
            assert status == "REQUESTED"
            return {
                "id": generation_id,
                "project_id": "project-1",
                "research_turn_id": turn_id,
                "status": "REQUESTED",
                "attempt_count": 1,
                "error_code": None,
                "error_summary": None,
            }

    class Agent2:
        scientific_report_generations = Generations()

        class Turns:
            @staticmethod
            def get(received_turn_id):
                assert received_turn_id == turn_id
                return {"id": turn_id, "project_id": "project-1"}

        class Interpretations:
            @staticmethod
            def get_for_turn(received_turn_id):
                assert received_turn_id == turn_id
                return {"id": "interpretation-1", "result_snapshot_id": RESULT_ID, "grounding_status": "VALID", "output_json": _interpretation()}

        class Snapshots:
            @staticmethod
            def get(snapshot_id):
                assert snapshot_id == RESULT_ID
                return {"project_id": "project-1", "bundle_json": _bundle().model_dump(mode="json")}

        scientific_result_snapshots = Snapshots()

        research_turns = Turns()
        interpretations = Interpretations()

    class Unit:
        agent2 = Agent2()

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    class Factory:
        @staticmethod
        def unit_of_work():
            return Unit()

    class Queue:
        @staticmethod
        def enqueue_generation(received_id, *, attempt):
            assert received_id == generation_id
            assert attempt == 2
            return ReportQueueSubmitResult(
                generation_id,
                True,
                "test",
                "queued",
            )

    result = ScientificReportRequestService(
        Factory(),  # type: ignore[arg-type]
        queue=Queue(),
    ).request(turn_id, requested_by="owner")
    assert result["status"] == "REQUESTED"
    assert result["queue"]["enqueued"] is True


def test_report_lifecycle_is_recoverable_without_mutating_immutable_snapshot() -> None:
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
    snapshot_id = UUID("77777777-7777-4777-8777-777777777777")
    interpretation_id = UUID("88888888-8888-4888-8888-888888888888")
    job_id = "job_report_lifecycle"
    with engine.begin() as connection:
        connection.execute(insert(analysis_plans), {
            "id": "plan_report_lifecycle", "project_id": "project_1", "dataset_id": None, "profile_id": None,
            "job_id": job_id, "plan_source": "agent2", "planner_provider": "fixture", "analysis_plan_json": {},
            "plan_hash": "d" * 64, "validation_status": "validated", "created_by": owner.id,
        })
        connection.execute(insert(jobs), {"id": job_id, "project_id": "project_1", "dataset_id": None, "plan_id": "plan_report_lifecycle", "kind": "agent2", "status": "completed", "created_by": owner.id})
    bundle_payload = _bundle().model_dump(mode="json")
    bundle_payload.update({"research_turn_id": str(received.turn_id), "source_object_refs": []})
    bundle_payload["result_items"][0]["scientific_object_refs"] = []
    bundle_payload["methods"][0]["source_object_refs"] = []
    bundle_payload["provenance"]["job_id"] = job_id
    with factory.unit_of_work() as unit:
        unit.agent2.scientific_result_snapshots.add({
            "id": snapshot_id, "project_id": "project_1", "research_turn_id": received.turn_id, "job_id": job_id,
            "schema_version": "1.0", "projection_version": "agent2-result/1.0", "execution_status": "SUCCESS",
            "relevance_status": "CURRENT", "source_fingerprint": "e" * 64, "bundle_json": bundle_payload,
        })
        unit.agent2.interpretations.add({
            "id": interpretation_id, "research_turn_id": received.turn_id, "result_snapshot_id": snapshot_id,
            "project_id": "project_1", "contract_version": "1.0", "prompt_version": "scientific-interpreter/1.0",
            "provider": "fake", "model": "fixture", "provider_request_id": None, "repair_attempted": False,
            "input_fingerprint": "f" * 64, "grounding_status": "VALID", "output_json": _interpretation(),
        })
    report_payload = _report().model_dump(mode="json")
    report_payload["data_sources"] = []
    service = ScientificReportService(factory, client=FakeStructuredReportComposerClient(report_payload))
    created = service.generate_for_turn(received.turn_id, created_by=owner.id)
    before = service.get_by_report_id(created["report_id"])
    revision = service.create_revision(
        created["report_id"],
        created_by=owner.id,
        reason="USER_REVISION",
        title="LiFePO4 RDF 论文报告（修订）",
    )
    bulk_archived = service.bulk_set_lifecycle(
        "project_1",
        [created["report_id"], revision["report_id"], created["report_id"]],
        "ARCHIVED",
    )
    assert bulk_archived["count"] == 2
    assert bulk_archived["reportIds"] == [
        created["report_id"],
        revision["report_id"],
    ]
    assert {
        item["lifecycle_status"] for item in bulk_archived["items"]
    } == {"ARCHIVED"}
    bulk_restored = service.bulk_set_lifecycle(
        "project_1",
        [created["report_id"], revision["report_id"]],
        "ACTIVE",
    )
    assert bulk_restored["count"] == 2
    with pytest.raises(ScientificReportError) as bulk_scope_error:
        service.bulk_set_lifecycle(
            "project_1",
            [created["report_id"], "report-missing"],
            "ARCHIVED",
        )
    assert bulk_scope_error.value.code == "REPORT_BULK_SCOPE_INVALID"
    assert service.get_by_report_id(created["report_id"])["lifecycle_status"] == "ACTIVE"
    assert service.get_by_report_id(revision["report_id"])["lifecycle_status"] == "ACTIVE"
    organized = service.set_organization(
        created["report_id"],
        {"title": "LiFePO4 RDF 论文报告", "pinned": True},
    )
    assert organized["title"] == "LiFePO4 RDF 论文报告"
    assert organized["source_title"] == before["title"]
    assert organized["pinned"] is True
    assert organized["snapshot_id"] == before["snapshot_id"]
    assert organized["scientific_result_snapshot_id"] == before["scientific_result_snapshot_id"]
    assert service.list_project("project_1")["items"][0]["pinned"] is True
    impact = service.dependency_impact(created["report_id"])
    assert impact["displayName"] == "LiFePO4 RDF 论文报告"
    assert impact["entity"] == "scientific_report"
    assert impact["dependencyCount"] >= 3
    assert {item["kind"] for item in impact["dependencies"]} >= {
        "RESEARCH_TURN", "SCIENTIFIC_RESULT", "INTERPRETATION",
    }
    assert next(
        item["href"]
        for item in impact["dependencies"]
        if item["kind"] == "RESEARCH_TURN"
    ).startswith("/projects/project_1/research/")
    assert impact["impact"]["historicalProvenanceProtected"] is True
    assert impact["impact"]["scientificSnapshotMutated"] is False
    assert impact["retentionPolicy"]["automaticPurge"] == "DISABLED"
    assert impact["retentionPolicy"]["manualPurge"] == "NOT_SUPPORTED_FOR_ENTITY"
    trashed = service.set_lifecycle(created["report_id"], "TRASHED")
    assert trashed["lifecycle_status"] == "TRASHED"
    assert service.get_by_report_id(created["report_id"])["lifecycle_status"] == "TRASHED"
    restored = service.set_lifecycle(created["report_id"], "ACTIVE")
    assert restored["lifecycle_status"] == "ACTIVE"
    after = service.get_by_report_id(created["report_id"])
    assert after["title"] == "LiFePO4 RDF 论文报告"
    assert after["pinned"] is True
    assert after["report_id"] == before["report_id"]
    assert after["snapshot_id"] == before["snapshot_id"]
    assert after["scientific_result_snapshot_id"] == before["scientific_result_snapshot_id"]
    reset = service.set_organization(created["report_id"], {"title": "", "pinned": False})
    assert reset["title"] == before["title"]
    assert reset["pinned"] is False
    assert reset["snapshot_id"] == before["snapshot_id"]


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


@pytest.mark.parametrize("spelling", ["fs", "femtosecond"])
@pytest.mark.parametrize("source_unit", ["fs", "femtosecond"])
def test_report_trajectory_time_unit_spelling(spelling: str, source_unit: str) -> None:
    payload = json.loads(json.dumps(_report().model_dump(mode="json"), ensure_ascii=False).replace("2.84", "398").replace("Å", spelling))
    bundle = _bundle().model_dump(mode="json")
    bundle["facts"][0].update(value=398, unit=source_unit)
    assert ReportGroundingValidator().validate(ScientificReportOutput.model_validate(payload), bundle=bundle, interpretation=_interpretation()) == []


@pytest.mark.parametrize("spelling", ["ps", "picosecond", "eV"])
def test_report_time_alias_does_not_permit_unit_conversion(spelling: str) -> None:
    payload = json.loads(json.dumps(_report().model_dump(mode="json"), ensure_ascii=False).replace("2.84", "398").replace("Å", spelling))
    bundle = _bundle().model_dump(mode="json")
    bundle["facts"][0].update(value=398, unit="femtosecond")
    errors = ReportGroundingValidator().validate(ScientificReportOutput.model_validate(payload), bundle=bundle, interpretation=_interpretation())
    assert any("unsupported unit" in error for error in errors)
