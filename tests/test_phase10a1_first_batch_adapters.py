from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import AnalysisPlan, DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


def test_mock_planner_routes_matpes_scatter_prompt() -> None:
    plan = _mock_plan("Please compare PBE and r2SCAN with a scatter plot.", _matpes_profile())

    assert plan["steps"][0]["toolId"] == "viz.scatter"
    assert plan["steps"][0]["params"] == {"xColumn": "PBE", "yColumn": "r2SCAN", "title": "PBE vs r2SCAN"}


def test_mock_planner_routes_matpes_histogram_prompt() -> None:
    plan = _mock_plan("Please view the PBE distribution as a histogram.", _matpes_profile())

    assert plan["steps"][0]["toolId"] == "viz.histogram"
    assert plan["steps"][0]["params"]["column"] == "PBE"


def test_mock_planner_routes_ward_distribution_prompt() -> None:
    plan = _mock_plan("Please analyze Ward metallic glasses numeric distribution statistics.", _ward_profile())

    assert plan["steps"][0]["toolId"] == "table.distribution_summary"
    assert "D_max" in plan["steps"][0]["params"]["numericColumns"]
    assert "gfa_type" in plan["steps"][0]["params"]["categoricalColumns"]


def test_mock_planner_routes_ward_correlation_prompt() -> None:
    plan = _mock_plan("Please analyze correlations in the Ward metallic glasses numeric fields.", _ward_profile())

    assert plan["steps"][0]["toolId"] == "viz.correlation"
    assert {"D_max", "dTx"}.issubset(set(plan["steps"][0]["params"]["numericColumns"]))
    assert plan["steps"][0]["params"]["method"] == "pearson"


def test_mock_planner_routes_composition_summary_when_formula_column_exists() -> None:
    plan = _mock_plan("Please summarize element composition from the formula field.", _ward_profile())

    assert plan["steps"][0]["toolId"] == "composition.summary"
    assert plan["steps"][0]["params"]["formulaColumn"] == "composition"


def test_mock_planner_routes_composition_distribution_before_histogram() -> None:
    plan = _mock_plan(
        "Please summarize the element composition distribution from the composition field.",
        _ward_profile(),
    )

    assert plan["steps"][0]["toolId"] == "composition.elements_hist"
    assert plan["steps"][0]["params"]["formulaColumn"] == "composition"


def test_mock_planner_routes_formula_statistics_prompt() -> None:
    plan = _mock_plan("请统计 composition 字段中的 formula 基础信息。", _ward_profile())

    assert plan["steps"][0]["toolId"] == "composition.formula_statistics"
    assert plan["steps"][0]["params"]["formulaColumn"] == "composition"


def test_mock_planner_routes_elements_hist_prompt() -> None:
    plan = _mock_plan("请统计元素分布。", _ward_profile())

    assert plan["steps"][0]["toolId"] == "composition.elements_hist"
    assert plan["steps"][0]["params"]["formulaColumn"] == "composition"
    assert plan["steps"][0]["params"]["countMode"] == "occurrence"


def test_mock_planner_routes_ptable_heatmap_prompt() -> None:
    plan = _mock_plan("请用周期表展示元素出现频率。", _ward_profile())

    assert plan["steps"][0]["toolId"] == "composition.ptable_heatmap"
    assert plan["steps"][0]["params"]["formulaColumn"] == "composition"


def test_mock_planner_routes_chem_sys_treemap_prompt() -> None:
    plan = _mock_plan("请分析化学体系分布，并用 treemap 展示。", _ward_profile())

    assert plan["steps"][0]["toolId"] == "composition.chem_sys_treemap"
    assert plan["steps"][0]["params"]["formulaColumn"] == "composition"
    assert plan["steps"][0]["params"]["groupMode"] == "chem_sys"


def test_mock_planner_routes_chem_sys_sunburst_prompt() -> None:
    plan = _mock_plan("请用 sunburst 展示 arity、chemical system 和 formula 层级。", _ward_profile())

    assert plan["steps"][0]["toolId"] == "composition.chem_sys_sunburst"
    assert plan["steps"][0]["params"]["formulaColumn"] == "composition"


def test_composition_visual_prompt_not_routed_to_generic_histogram() -> None:
    plan = _mock_plan("请画出元素出现频率直方图。", _ward_profile())

    assert plan["steps"][0]["toolId"] == "composition.elements_hist"
    assert plan["steps"][0]["toolId"] != "viz.histogram"


def test_persisted_scatter_plan_executes_exactly_one_tool_call(tmp_path: Path) -> None:
    repos = InMemoryRepositoryBundle.create()
    provider = MockLLMProvider(fixed_plan=_valid_scatter_plan().model_dump(mode="json"))
    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Please compare PBE and r2SCAN with a scatter plot.",
            projectId="project_10a1",
            datasetId="dataset_matpes",
            profileId="profile_matpes",
            enqueue=True,
        ),
        provider=provider,
        repositories=repos,
        queue_runtime=QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path / "artifacts"),
        registry=load_manifests(),
    )

    assert result.ok
    runtime = QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path / "artifacts")
    worker_result = runtime.handle_job(result.job_id or "", object_store={"ml_table": _matpes_frame()})

    tool_calls = repos.tool_calls.list_for_job(result.job_id or "")
    artifacts = repos.artifacts.list_for_job(result.job_id or "")
    assert worker_result.status == "completed"
    assert worker_result.tool_call_count == 1
    assert len(tool_calls) == 1
    assert tool_calls[0]["toolId"] == "viz.scatter"
    assert tool_calls[0]["stepId"] == "step_001"
    assert {artifact["type"] for artifact in artifacts} >= {"plotly_json", "plotly_html", "summary_md", "recipe_json"}


def test_persisted_composition_visual_plan_executes_exactly_one_tool_call(tmp_path: Path) -> None:
    repos = InMemoryRepositoryBundle.create()
    plan = _valid_composition_plan("composition.elements_hist", {"formulaColumn": "composition", "countMode": "occurrence"})
    provider = MockLLMProvider(fixed_plan=plan.model_dump(mode="json"))
    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="请统计元素分布。",
            projectId="project_10b1",
            datasetId="dataset_ward",
            profileId="profile_ward",
            enqueue=True,
        ),
        provider=provider,
        repositories=repos,
        queue_runtime=QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path / "artifacts"),
        registry=load_manifests(),
    )

    assert result.ok
    runtime = QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path / "artifacts")
    worker_result = runtime.handle_job(result.job_id or "", object_store={"ml_table": _ward_frame()})

    tool_calls = repos.tool_calls.list_for_job(result.job_id or "")
    artifacts = repos.artifacts.list_for_job(result.job_id or "")
    assert worker_result.status == "completed"
    assert worker_result.tool_call_count == 1
    assert len(tool_calls) == 1
    assert tool_calls[0]["toolId"] == "composition.elements_hist"
    assert {artifact["type"] for artifact in artifacts} >= {"plotly_json", "plotly_html", "summary_md", "recipe_json"}


def test_invalid_new_tool_params_rejected_before_persistence() -> None:
    repos = InMemoryRepositoryBundle.create()
    bad_plan = _valid_scatter_plan().model_dump(mode="json")
    bad_plan["steps"][0]["params"]["unexpected"] = True
    provider = MockLLMProvider(fixed_plan=bad_plan)

    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="bad scatter",
            projectId="project_10a1",
            datasetId="dataset_matpes",
            profileId="profile_matpes",
        ),
        provider=provider,
        repositories=repos,
        registry=load_manifests(),
    )

    assert result.ok is False
    assert result.job_id is None
    assert result.plan_id is None
    assert repos.jobs.records == {}
    assert repos.analysis_plans.records == {}


def _mock_plan(prompt: str, profile: DataProfile) -> dict[str, Any]:
    response = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt=prompt,
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            tool_registry_version=load_manifests().version,
        ),
        tools=load_manifests().list_mvp_tools(),
        data_profile=profile,
    )
    assert response.raw_json is not None
    return response.raw_json


def _valid_scatter_plan() -> AnalysisPlan:
    return AnalysisPlan.model_validate(
        {
            "schemaVersion": "0.1",
            "goal": "scatter",
            "datasetId": "dataset_matpes",
            "profileId": "profile_matpes",
            "toolRegistryVersion": load_manifests().version,
            "assumptions": [],
            "warnings": [],
            "steps": [
                {
                    "stepId": "step_001",
                    "toolId": "viz.scatter",
                    "purpose": "scatter",
                    "reason": "test",
                    "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
                    "params": {"xColumn": "PBE", "yColumn": "r2SCAN"},
                    "output": {"artifactTypes": ["plotly_json", "plotly_html", "summary_md", "recipe_json"]},
                }
            ],
            "expectedArtifacts": [
                {"name": "scatter.json", "type": "plotly_json", "fromStepId": "step_001"},
                {"name": "scatter.html", "type": "plotly_html", "fromStepId": "step_001"},
                {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
                {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
            ],
        }
    )


def _valid_composition_plan(tool_id: str, params: dict[str, Any]) -> AnalysisPlan:
    return AnalysisPlan.model_validate(
        {
            "schemaVersion": "0.1",
            "goal": "composition",
            "datasetId": "dataset_ward",
            "profileId": "profile_ward",
            "toolRegistryVersion": load_manifests().version,
            "assumptions": [],
            "warnings": [],
            "steps": [
                {
                    "stepId": "step_001",
                    "toolId": tool_id,
                    "purpose": "composition",
                    "reason": "test",
                    "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
                    "params": params,
                    "output": {"artifactTypes": ["plotly_json", "plotly_html", "summary_md", "recipe_json"]},
                }
            ],
            "expectedArtifacts": [
                {"name": "elements_hist.json", "type": "plotly_json", "fromStepId": "step_001"},
                {"name": "elements_hist.html", "type": "plotly_html", "fromStepId": "step_001"},
                {"name": "summary.md", "type": "summary_md", "fromStepId": "step_001"},
                {"name": "recipe.json", "type": "recipe_json", "fromStepId": "step_001"},
            ],
        }
    )


def _matpes_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "element": ["H", "He", "Li", "Be"],
            "PBE": [-13.6, -24.5, -5.3, -8.1],
            "r2SCAN": [-13.8, -24.2, -5.0, -8.4],
        }
    )


def _ward_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "composition": ["Zr46Cu46Al8", "Ni80P20", "Fe80B20", "Pd40Ni40P20"],
            "gfa_type": ["BMG", "ribbon", "BMG", "ribbon"],
            "D_max": [3.0, 1.2, 4.1, 0.8],
            "dTx": [40.0, 12.0, 55.0, 5.0],
            "Tg": [650.0, 580.0, 700.0, 540.0],
        }
    )


def _matpes_profile() -> DataProfile:
    return DataProfile.model_validate(
        {
            "schemaVersion": "0.1",
            "profileId": "profile_matpes",
            "datasetId": "dataset_matpes",
            "version": "1",
            "datasetType": "table",
            "files": [],
            "objects": [],
            "tableSummary": {
                "nRows": 89,
                "columns": [
                    {"name": "element", "dtype": "string", "missingCount": 0},
                    {"name": "PBE", "dtype": "number", "missingCount": 0},
                    {"name": "r2SCAN", "dtype": "number", "missingCount": 0},
                ],
            },
            "qualityIssues": [],
            "recommendedTasks": [],
            "createdAt": "2026-07-05T00:00:00+00:00",
        }
    )


def _ward_profile() -> DataProfile:
    return DataProfile.model_validate(
        {
            "schemaVersion": "0.1",
            "profileId": "profile_ward",
            "datasetId": "dataset_ward",
            "version": "1",
            "datasetType": "table",
            "files": [],
            "objects": [],
            "tableSummary": {
                "nRows": 8415,
                "columns": [
                    {"name": "composition", "dtype": "string", "missingCount": 0},
                    {"name": "gfa_type", "dtype": "string", "missingCount": 0},
                    {"name": "D_max", "dtype": "number", "missingCount": 12},
                    {"name": "dTx", "dtype": "number", "missingCount": 25},
                    {"name": "Tg", "dtype": "number", "missingCount": 30},
                ],
            },
            "qualityIssues": [],
            "recommendedTasks": [],
            "createdAt": "2026-07-05T00:00:00+00:00",
        }
    )
