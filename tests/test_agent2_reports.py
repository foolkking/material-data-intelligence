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


def test_report_discussion_prefers_fact_grounded_synthesis_over_figure_availability() -> None:
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
    assert report.discussion is not None
    assert report.discussion.text.startswith("综合已验证的结果：")
    assert "已生成一个可查看图表" not in report.discussion.text
    assert "。；" not in report.discussion.text
    assert report.discussion.fact_refs == ["rdf.first_peak_position"]


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

    assert report.discussion is not None
    assert "17 个峰" in report.discussion.text
    assert report.discussion.fact_refs == ["xrd.matched_peak_count"]
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
    assert projected.summary == "RDF 第一峰位于 2.84 Å。"
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
    assert result.parsed["contract_version"] == "2.0"
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


def test_report_viewer_sources_are_derived_only_from_result_provenance() -> None:
    source = _bundle().source_object_refs[0]

    class Objects:
        def get_object(self, object_id):
            assert str(object_id) == str(source.object_id)
            return {
                "id": str(source.object_id),
                "display_name": "LiFePO4",
                "current_version_id": str(source.version_id),
                "lifecycle_status": "ARCHIVED",
            }

        def get_version(self, version_id):
            assert str(version_id) == str(source.version_id)
            return {"id": str(source.version_id), "object_type": source.object_type}

    class Snapshots:
        def __init__(self, bundle):
            self.bundle = bundle

        def get(self, _snapshot_id):
            return {"bundle_json": self.bundle}

    class Interpretations:
        def get(self, _interpretation_id):
            return {"output_json": _interpretation()}

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
        "relevance_at_generation": "CURRENT",
    }
    view_bundle = _bundle().model_dump(mode="json")
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
        "display_name": "LiFePO4",
        "is_current_version": True,
        "lifecycle_status": "ARCHIVED",
    }]
    assert fresh["figure_sources"] == [{
        "figure_ref": "figure.rdf_curve",
        "artifact_ids": ["artifact_private_123"],
        "job_id": "job_private_123",
    }]
    assert fresh["table_sources"] == []
    assert fresh["report"]["research_question"] == "比较 LiFePO4 的局域环境。"
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


def test_report_exposes_result_tables_with_exact_artifact_and_source_refs() -> None:
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
    bundle = ScientificResultBundle.model_validate(payload).model_dump(mode="json")

    class Objects:
        def get_object(self, object_id):
            return {
                "id": str(object_id),
                "display_name": "LiFePO4",
                "current_version_id": str(VERSION_ID),
                "lifecycle_status": "ACTIVE",
            }

        def get_version(self, version_id):
            return {"id": str(version_id), "object_type": "structure.crystal"}

    class Snapshots:
        def get(self, _snapshot_id):
            return {"bundle_json": bundle}

    class Agent2:
        scientific_result_snapshots = Snapshots()
        scientific_objects = Objects()
        interpretations = None

    class Session:
        agent2 = Agent2()

    view = ScientificReportService._with_viewer_sources(
        {},
        Session(),
        {"scientific_result_snapshot_id": "snapshot-1"},
    )
    assert view["table_sources"] == [{
        "table_ref": "diffusion.diagnostic",
        "title": "扩散拟合诊断",
        "artifact_ids": ["artifact_diffusion_table"],
        "job_id": "job_private_123",
        "source_refs": [{
            "object_id": str(OBJECT_ID),
            "version_id": str(VERSION_ID),
            "object_type": "structure.crystal",
        }],
    }]

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
            }

        def set_status(self, received_id, status, **_kwargs):
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
                return {"id": "interpretation-1"}

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
        def enqueue_generation(received_id):
            assert received_id == generation_id
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
