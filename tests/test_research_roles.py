from __future__ import annotations

import pytest

from mdi_llm.research_roles import (
    compose_grounded_report,
    orchestrate_research_turn,
    project_grounded_interpretation,
    validate_report_composer_projection,
)


def test_orchestrator_is_grounded_and_does_not_expose_private_reasoning() -> None:
    projection = orchestrate_research_turn(
        "比较 formation energy 与 band gap",
        scope={"status": "READY", "dataset_name": "materials-table"},
        plan={"steps": [{"userFacingPurpose": "生成属性关系图"}]},
    )
    assert projection.mode == "analyze"
    assert "materials-table" in projection.assistantMessage
    assert "生成属性关系图" in projection.assistantMessage
    assert "chain of thought" not in projection.assistantMessage.lower()


def test_orchestrator_falls_back_when_provider_payload_is_unsafe() -> None:
    projection = orchestrate_research_turn(
        "查看带隙分布",
        scope={"status": "READY", "dataset_name": "materials"},
        provider_payload={
            "mode": "analyze",
            "assistantMessage": "api_key=secret; private reasoning",
            "planSummary": ["unsafe"],
        },
    )
    assert projection.mode == "analyze"
    assert "api_key" not in projection.assistantMessage


def test_interpreter_drops_dangling_evidence_and_report_validates_artifacts() -> None:
    interpretation = {
        "sourceBundleId": "bundle-1",
        "sourceJobId": "job-1",
        "claims": [
            {
                "claimId": "claim-1",
                "renderedText": "形成能与带隙呈负相关。",
                "subjectEvidenceIds": ["evidence-1"],
                "supportingEvidenceIds": ["evidence-1"],
            },
            {
                "claimId": "claim-dangling",
                "renderedText": "不应被显示。",
                "subjectEvidenceIds": ["missing"],
                "supportingEvidenceIds": ["missing"],
            },
        ],
        "globalLimitations": ["仅适用于当前数据范围。"],
    }
    projected = project_grounded_interpretation(
        interpretation,
        evidence_items=[{"evidenceItemId": "evidence-1", "sourceArtifactId": "artifact-1"}],
        artifact_ids=["artifact-1"],
        title="形成能与带隙的相关关系",
    )
    assert [item.claimId for item in projected.findings] == ["claim-1"]
    report = compose_grounded_report(
        research_question="比较形成能与带隙",
        interpretation=projected,
        artifact_ids=["artifact-1"],
        figure_ids=["artifact-1"],
        method_summary=["计算相关关系"],
    )
    assert report.primaryFigureRefs == ["artifact-1"]
    assert report.findingRefs == ["claim-1"]


def test_report_rejects_unavailable_result_reference() -> None:
    projected = project_grounded_interpretation(
        {"sourceBundleId": "bundle-1", "sourceJobId": "job-1", "claims": []},
        evidence_items=[],
        artifact_ids=[],
    )
    projected = projected.model_copy(update={"primaryResultRefs": ["not-real"]})
    with pytest.raises(ValueError, match="validated artifact set"):
        compose_grounded_report(
            research_question="q",
            interpretation=projected,
            artifact_ids=[],
        )


def test_report_composer_allows_wording_but_rejects_new_facts_and_refs() -> None:
    interpretation = project_grounded_interpretation(
        {
            "sourceBundleId": "bundle-1",
            "sourceJobId": "job-1",
            "claims": [{
                "claimId": "claim-1",
                "renderedText": "相关系数为 -0.57。",
                "subjectEvidenceIds": ["evidence-1"],
            }],
        },
        evidence_items=[{"evidenceItemId": "evidence-1", "sourceArtifactId": "artifact-1"}],
        artifact_ids=["artifact-1"],
        title="属性关系",
    )
    grounded = compose_grounded_report(
        research_question="相关系数是否为 -0.57？",
        interpretation=interpretation,
        artifact_ids=["artifact-1"],
        figure_ids=["artifact-1"],
    )
    payload = grounded.model_dump(mode="json")
    payload["summary"] = "当前数据中的相关系数为 -0.57。"
    assert validate_report_composer_projection(payload, grounded=grounded).summary.endswith("-0.57。")

    payload["summary"] = "当前数据中的相关系数为 0.99。"
    with pytest.raises(ValueError, match="numeric"):
        validate_report_composer_projection(payload, grounded=grounded)
    payload = grounded.model_dump(mode="json")
    payload["primaryFigureRefs"] = ["artifact-invented"]
    with pytest.raises(ValueError, match="primaryFigureRefs"):
        validate_report_composer_projection(payload, grounded=grounded)
