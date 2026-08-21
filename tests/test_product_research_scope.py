import pytest
from fastapi import HTTPException
from fastapi.params import Depends

from mdi_api.routers.auth import get_current_user_compat
from mdi_api.routers.report_compositions import get_report_composition
from mdi_api.routers.research import (
    ResearchAssistantProjectionCreate,
    _assistant_projection_text,
    _ground_projection_from_run,
    _provider_research_turn_text,
    _semantic_names,
    _user_facing_step_label,
)
from mdi_llm.providers import PlannerRawResponse


def test_scope_catalog_reads_current_profile_semantic_contract() -> None:
    profile = {
        "semanticColumns": [
            {"column": "y_true", "roles": [{"role": "regression_target"}]},
            {"column": "y_pred", "roles": [{"role": "regression_prediction"}]},
        ],
        "resourceSemantics": [{"capabilities": ["table"]}],
        "analysisReadiness": [
            {"capability": "regression_evaluation", "dataStatus": "READY", "platformStatus": "AVAILABLE"},
            {"capability": "structure_summary", "dataStatus": "MISSING_REQUIRED_DATA", "platformStatus": "AVAILABLE"},
        ],
    }

    semantics = _semantic_names(profile)

    assert {"y_true", "y_pred", "regression_target", "regression_prediction", "table", "regression_evaluation"} <= set(semantics)
    assert "structure_summary" not in semantics


def test_research_assistant_projection_is_bounded_and_user_facing() -> None:
    pre_run = _assistant_projection_text(ResearchAssistantProjectionCreate(
        phase="pre_run",
        datasetName="materials-table",
        steps=["比较 formation energy 与 band gap", "生成关系图"],
    ))
    assert "数据集“materials-table”" in pre_run
    assert "1. 比较 formation energy 与 band gap" in pre_run
    assert "ToolCall" not in pre_run
    post_run = _assistant_projection_text(ResearchAssistantProjectionCreate(
        phase="post_run",
        findings=["当前样本中形成能与带隙呈中等相关。"],
        limitations=["结果仅适用于本次选择的数据。"],
    ))
    assert "中等相关" in post_run
    assert "当前限制" in post_run

    failed = _assistant_projection_text(ResearchAssistantProjectionCreate(
        phase="failed",
        failureCode="CAPABILITY_COVERAGE_INCOMPLETE",
    ))
    assert "当前已验证的分析能力无法完整覆盖" in failed
    assert "Eligible capabilities" not in failed

    clarification = _assistant_projection_text(ResearchAssistantProjectionCreate(
        phase="failed",
        failureCode="COORDINATION_ALGORITHM_CLARIFICATION_REQUIRED",
    ))
    assert "CrystalNN" in clarification
    assert "VoronoiNN" in clarification
    assert "确认后再创建分析运行" in clarification
    assert "CrystalNN" in _assistant_projection_text(ResearchAssistantProjectionCreate(
        phase="failed",
        failureCode="NEEDS_CLARIFICATION",
    ))


def test_pre_run_projection_uses_persisted_plan_instead_of_client_copy() -> None:
    request = ResearchAssistantProjectionCreate(
        phase="pre_run",
        runId="job-1",
        steps=["浏览器伪造的步骤"],
        findings=["不应出现在运行前"],
    )

    grounded, metadata = _ground_projection_from_run(
        request,
        {
            "analysisPlan": {
                "steps": [
                    {"toolId": "table.property_distribution", "purpose": "Satisfy the validated structured AnalysisIntent"},
                    {"toolId": "unknown.safe.tool", "reason": "raw machine reason"},
                ],
            },
            "planHash": "sha256:validated-plan",
        },
    )

    assert grounded.steps == ["分析材料属性的分布特征", "整理当前数据中的科学信息"]
    assert "Satisfy the validated" not in _assistant_projection_text(grounded)
    assert grounded.findings == []
    assert grounded.limitations == []
    assert "浏览器伪造的步骤" not in _assistant_projection_text(grounded)
    assert metadata == {
        "groundedBy": ["analysis_plan"],
        "planHash": "sha256:validated-plan",
    }


def test_pre_run_projection_uses_scientific_tool_metadata_for_retained_runs() -> None:
    grounded, _ = _ground_projection_from_run(
        ResearchAssistantProjectionCreate(phase="pre_run", runId="job-x"),
        {
            "analysisPlan": {
                "steps": [
                    {"toolId": "structure.experimental_xrd_comparison", "purpose": "Satisfy the validated structured AnalysisIntent with an eligible registered capability."},
                    {"toolId": "phonon.band_dos", "purpose": "Satisfy the validated structured AnalysisIntent with an eligible registered capability."},
                ],
            },
            "planHash": "a" * 64,
        },
    )
    assert grounded.steps == ["比较实验峰与理论峰的位置和强度", "组合声子色散与态密度"]


def test_pre_run_provider_role_is_strictly_validated_before_persistence(monkeypatch: pytest.MonkeyPatch) -> None:
    class Provider:
        def generate_research_turn(self, **_kwargs):
            return PlannerRawResponse(
                raw_json={
                    "schemaVersion": "1.0",
                    "mode": "analyze",
                    "assistantMessage": "我会使用当前材料表，先比较两个属性，再生成可复核的关系图。",
                    "scientificIntent": "比较形成能与带隙",
                    "scopeHints": ["materials-table"],
                    "planSummary": ["比较两个属性", "生成关系图"],
                    "clarificationQuestion": None,
                    "sessionTitleCandidate": "形成能与带隙关系",
                    "groundingRefs": [],
                },
                raw_text=None,
                model="configured-model",
                finish_reason="stop",
            )

    monkeypatch.setattr("mdi_api.routers.planner._select_planner_provider", lambda _name: Provider())
    monkeypatch.setattr("mdi_api.routers.planner._planner_user_config_from_request", lambda *_args, **_kwargs: None)
    text, metadata = _provider_research_turn_text(
        ResearchAssistantProjectionCreate(
            phase="pre_run",
            question="比较形成能与带隙",
            datasetName="materials-table",
            steps=["比较两个属性", "生成关系图"],
            provider="configured",
            useProvider=True,
        ),
        "确定性回退",
    )

    assert "生成可复核的关系图" in text
    assert metadata == {
        "llmRoleExecution": "provider_validated",
        "llmRoleProvider": "configured",
        "llmRoleModel": "configured-model",
    }


def test_unknown_scientific_tool_uses_safe_chinese_fallback() -> None:
    assert _user_facing_step_label({"toolId": "future.scientific_tool", "purpose": "Satisfy the validated structured AnalysisIntent with an eligible registered capability."}) == "整理当前数据中的科学信息"


def test_post_run_projection_uses_persisted_interpretation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "mdi_api.routers.planner.list_planner_job_interpretations",
        lambda _job_id: {
            "interpretations": [{
                "interpretationId": "interpretation-1",
                "bundleId": "bundle-1",
                "claims": [
                    {"claimType": "FINDING", "renderedText": "形成能与带隙呈负相关。"},
                    {"claimType": "FINDING", "renderedText": "dataset reported count: 1; artifact(s) have no approved projector."},
                    {"claimType": "LIMITATION", "renderedText": "样本量有限。"},
                    {"claimType": "LIMITATION", "renderedText": "schema contract unavailable for artifact(s)."},
                ],
                "globalLimitations": ["结论仅适用于当前数据范围。"],
            }],
        },
    )
    request = ResearchAssistantProjectionCreate(
        phase="post_run",
        runId="job-1",
        findings=["浏览器伪造的发现"],
        limitations=["浏览器伪造的限制"],
    )

    grounded, metadata = _ground_projection_from_run(request, {})

    assert grounded.findings == ["形成能与带隙呈负相关。"]
    assert grounded.limitations == ["结论仅适用于当前数据范围。", "样本量有限。"]
    assert "浏览器伪造" not in _assistant_projection_text(grounded)
    assert metadata == {
        "groundedBy": ["scientific_interpretation"],
        "interpretationId": "interpretation-1",
        "bundleId": "bundle-1",
    }


def test_post_run_projection_requires_persisted_interpretation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "mdi_api.routers.planner.list_planner_job_interpretations",
        lambda _job_id: {"interpretations": []},
    )

    with pytest.raises(HTTPException) as error:
        _ground_projection_from_run(
            ResearchAssistantProjectionCreate(
                phase="post_run",
                runId="job-1",
                findings=["浏览器伪造的发现"],
            ),
            {},
        )

    assert error.value.status_code == 409
    assert "科学解释尚未生成" in str(error.value.detail)


def test_report_composition_uses_the_production_auth_dependency() -> None:
    # Keep the route import exercised while asserting its runtime dependency.
    default = get_report_composition.__defaults__[0]
    assert isinstance(default, Depends)
    assert default.dependency is get_current_user_compat
