from copy import deepcopy
from uuid import uuid4

import pytest

from mdi_api.application.scientific_reports.grounded import (
    DeterministicScientificReportComposer, _comparison_finding, _dedupe_limitations,
)
from mdi_api.domain.scientific_reports.contracts import ReportLimitation
from tests.test_agent2_reports import _bundle, _interpretation


def _comparison_report_input():
    bundle, interpretation = _bundle(), _interpretation()
    source, fact, result, evidence = bundle.source_object_refs[0], bundle.facts[0], bundle.result_items[0], bundle.evidence[0]
    bundle.source_object_refs, bundle.facts, bundle.result_items, bundle.evidence, bundle.figures = [], [], [], [], []
    findings = []
    for index, name in enumerate(("NaCl.cif", "Si.cif", "Cu.cif")):
        exact = source.model_copy(update={"object_id": uuid4(), "version_id": uuid4(), "display_name": name})
        fact_id, result_id, evidence_id, artifact_id = (f"{kind}.{index}" for kind in ("density", "result", "evidence", "artifact"))
        bundle.source_object_refs.append(exact)
        bundle.facts.append(fact.model_copy(update={"fact_id": fact_id, "predicate": "rdf.number_density", "value": (0.04, 0.05, 0.08)[index], "unit": "Å⁻³", "source": fact.source.model_copy(update={"artifact_id": artifact_id})}))
        bundle.result_items.append(result.model_copy(update={"id": result_id, "scientific_object_refs": [exact], "fact_refs": [fact_id], "evidence_refs": [evidence_id], "artifact_ids": [artifact_id]}))
        bundle.evidence.append(evidence.model_copy(update={"evidence_id": evidence_id, "artifact_id": artifact_id, "supports_fact_refs": [fact_id], "supports_result_item_refs": [result_id]}))
        scope = f"{name} 合成晶体"
        findings.append({"finding_id": f"finding.{index}", "statement": f"{name} 的详细计算结果。", "scope": scope,
                         "fact_refs": [fact_id], "evidence_refs": [evidence_id],
                         "reasoning_assessment": {"claim_id": f"finding.{index}", "claim_type": "DIRECT_OBSERVATION",
                         "support_status": "DIRECTLY_SUPPORTED", "outcome": "SUPPORTED", "accepted": True,
                         "scope": scope, "required_qualifiers": ["合成数据，非实验测量"], "independent_evidence_groups": 1}})
    comparison = deepcopy(findings[0])
    comparison.update(finding_id="comparison", statement="三个合成晶体的数密度比较：NaCl.cif 为 0.04 Å⁻³，Si.cif 为 0.05 Å⁻³，Cu.cif 为 0.08 Å⁻³。",
                      scope="三个合成晶体", fact_refs=[fact.fact_id for fact in bundle.facts], evidence_refs=[item.evidence_id for item in bundle.evidence])
    comparison["reasoning_assessment"].update(claim_id="comparison", claim_type="QUANTITATIVE_COMPARISON", scope="三个合成晶体")
    interpretation["interpretation"]["primary_findings"] = [*findings, comparison]
    return bundle, interpretation


def test_comparison_report_keeps_one_complete_verdict_and_all_detailed_findings():
    bundle, interpretation = _comparison_report_input()
    original = deepcopy(interpretation)
    report = DeterministicScientificReportComposer().compose(bundle=bundle, interpretation=interpretation, relevance_status="CURRENT")
    findings = interpretation["interpretation"]["primary_findings"]
    assert report.summary == "研究范围：三个合成晶体。本次分析围绕径向分布函数展开。"
    assert report.conclusion.text == findings[-1]["statement"] + "合成数据，非实验测量。"
    assert report.conclusion.fact_refs == findings[-1]["fact_refs"]
    assert report.conclusion.evidence_refs == findings[-1]["evidence_refs"]
    assert [finding.statement for finding in report.main_findings] == [item["statement"] for item in findings]
    assert interpretation == original


@pytest.mark.parametrize("problem", ["partial_coverage", "different_units", "mixed_topics", "duplicate_source", "extra_source", "unknown_fact", "ambiguous_comparison", "contradicted", "unaccepted", "lost_qualification"])
def test_comparison_conclusion_does_not_guess_scope_or_drop_qualifications(problem):
    bundle, interpretation = _comparison_report_input()
    findings = interpretation["interpretation"]["primary_findings"]
    comparison = findings[-1]
    if problem == "partial_coverage": comparison["fact_refs"].pop()
    elif problem == "different_units": bundle.facts[0].unit = "nm⁻³"
    elif problem == "mixed_topics": bundle.result_items[0].result_type = "trajectory.msd"
    elif problem == "duplicate_source": bundle.result_items[0].scientific_object_refs = bundle.result_items[1].scientific_object_refs
    elif problem == "extra_source": bundle.source_object_refs.append(bundle.source_object_refs[0].model_copy(update={"version_id": uuid4()}))
    elif problem == "unknown_fact": comparison["fact_refs"].append("missing")
    elif problem == "ambiguous_comparison": findings.append(deepcopy(comparison))
    elif problem == "contradicted": comparison["reasoning_assessment"]["contradicting_refs"] = ["conflict"]
    elif problem == "unaccepted": comparison["reasoning_assessment"]["accepted"] = False
    else: findings[0]["reasoning_assessment"]["required_qualifiers"].append("仅适用于室温")
    assert _comparison_finding(bundle, findings) is None


def test_specific_scope_and_explicit_conclusion_are_not_replaced():
    bundle, interpretation = _comparison_report_input()
    interpretation["interpretation"]["primary_findings"][0]["scope"] += "，只包含该温度下的样本"
    interpretation["interpretation"]["conclusion"] = {"text": "已有的完整结论。", "fact_refs": [bundle.facts[0].fact_id], "evidence_refs": []}
    report = DeterministicScientificReportComposer().compose(bundle=bundle, interpretation=interpretation, relevance_status="CURRENT")
    assert "只包含该温度下的样本" in report.summary
    assert report.conclusion.text == "已有的完整结论。"


def test_equivalent_rdf_limitation_translations_merge_references_only():
    limitations = [
        ReportLimitation(statement="The result projector does not infer peaks or coordination shells from the RDF curve.", source_refs=["canonical"]),
        ReportLimitation(statement="结果投影器未从 RDF 曲线推断峰位或配位壳层。", source_refs=["interpretation"]),
        ReportLimitation(statement="结果投影器未从 RDF 曲线推断峰位或配位壳层。仅限当前材料。", source_refs=["qualified"]),
    ]
    compact = _dedupe_limitations(limitations)
    assert len(compact) == 2
    assert compact[0].source_refs == ["canonical", "interpretation"]
    assert compact[1] == limitations[2]
