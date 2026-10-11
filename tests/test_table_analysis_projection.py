from __future__ import annotations

from dataclasses import replace
import json
from copy import deepcopy

import pandas as pd
import pytest

from mdi_adapters import (
    CorrelationAdapter, DistributionSummaryAdapter, HistogramAdapter,
    NumericSummaryAdapter, ScatterAdapter,
)
from mdi_api.application.interpretation.assembler import InterpreterInputAssembler
from mdi_api.application.scientific_reports.assembler import ReportComposerInputAssembler
from mdi_api.application.scientific_reports.grounded import DeterministicScientificReportComposer
from mdi_api.application.scientific_reports.grounding import ReportGroundingValidator
from mdi_api.application.interpretation.grounding import validate_interpretation
from mdi_api.domain.interpretation.contracts import ScientificInterpretationOutput
from mdi_api.application.scientific_results.projectors.canonical import resolve_json_pointer
from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.infrastructure.scientific_results.service import ScientificResultProjectionService
from mdi_schemas import ToolExecutionRequest
from tests.test_adapters import make_context
from tests.test_agent2_results import _context


@pytest.fixture
def table_context(tmp_path, request):
    frame = pd.DataFrame({"energy/~eV": [1., 2., 3., 4.], "gap": [4., 3., 2., 1.],
                          "constant": [7., 7., 7., 7.], "kind": ["a", "a", "b", None]})
    context = _context([], projector_id="agent2.data.table_analysis")
    source = context.source_object_refs[0].model_copy(update={"object_type": "materials.table"})
    artifacts, calls, steps, payloads = [], [], [], {}
    for index, (adapter, params, types) in enumerate([
        (DistributionSummaryAdapter(), {}, ["table_json", "recipe_json"]),
        (NumericSummaryAdapter(), {}, ["table_json", "recipe_json"]),
        (CorrelationAdapter(), getattr(request, "param", {}), ["table_json", "plotly_json", "recipe_json"]),
        (HistogramAdapter(), {"column": "energy/~eV", "bins": 3}, ["plotly_json", "recipe_json"]),
        (ScatterAdapter(), {"xColumn": "energy/~eV", "yColumn": "gap"}, ["plotly_json", "recipe_json"]),
    ]):
        step_id, call_id = f"table_step_{index}", f"table_call_{index}"
        input_refs = [{"refType": "normalized_object", "ref": str(source.version_id), "objectType": "DataFrame"}]
        tool_request = ToolExecutionRequest(jobId="job_adapter", stepId=step_id, toolId=adapter.tool_id,
                                       inputRefs=input_refs, params=params, artifactTypes=types)
        adapter_context = make_context(tmp_path, adapter.tool_id, {str(source.version_id): frame}, call_id)
        adapter_context.project_id = context.project_id
        produced = adapter.execute(adapter_context, tool_request)
        calls.append({"id": call_id, "toolId": adapter.tool_id, "stepId": step_id,
                      "jobId": "job_adapter", "state": "COMPLETED", "paramsJson": params})
        steps.append({"stepId": step_id, "inputRefs": input_refs, "output": {"capabilityPlanStepId": "step_1"}})
        for artifact in produced:
            artifacts.append(artifact.model_dump(mode="json"))
            payloads[artifact.id] = json.loads((tmp_path / "artifacts" / artifact.storageKey).read_text(encoding="utf-8"))
    return replace(context, artifacts=tuple(artifacts), artifact_payloads=payloads, tool_calls=tuple(calls),
                   analysis_plan={"steps": steps}, source_object_refs=(source,),
                   execution_summary={"outcome": "SUCCESS", "job_id": "job_adapter"})


def _project(context):
    return ScientificResultProjectionService(None).project_context(context)


def test_real_table_suite_publishes_saved_facts_and_bound_sources(table_context):
    bundle = _project(table_context)
    assert bundle.facts, "Successful table tools must publish scientific facts for Research"
    for fact in bundle.facts:
        assert resolve_json_pointer(table_context.artifact_payloads[fact.source.artifact_id], fact.source.artifact_locator) == fact.value
    assert bundle.source_object_refs == list(table_context.source_object_refs)
    assert all(f.fact_refs for f in bundle.figures)
    assert any(f.predicate == "correlation.coefficient" and f.value == pytest.approx(-1) for f in bundle.facts)
    assert any(f.predicate == "table.numeric.mean" and f.value == 2.5 for f in bundle.facts)
    assert any(f.predicate == "table.numeric.missing" and f.value == 0 for f in bundle.facts)
    assert any(w.code == "TABLE_ANALYSIS_MISSING_CORRELATIONS" for w in bundle.warnings)
    envelope, _ = InterpreterInputAssembler().assemble(bundle=bundle, question="解释相关性和均值", relevance_status="CURRENT")
    represented = envelope.result["facts"]
    pair = next(f for f in represented if f["predicate"] == "correlation.coefficient")
    assert {f["value"] for f in represented if f["subject_ref"] == pair["subject_ref"] and f["predicate"] in
            {"correlation.left_column", "correlation.right_column"}} == {"energy/~eV", "gap"}


def test_real_table_outputs_have_distinct_titles_with_exact_columns(table_context):
    bundle = _project(table_context)
    assert {f.title for f in bundle.figures} == {
        "Pearson 相关矩阵", "直方图 · energy/~eV", "散点图 · energy/~eV × gap",
    }
    assert {t.title for t in bundle.tables} == {"数据分布概览", "数值统计", "Pearson 相关系数"}
    scoped = _project(replace(table_context, projection_scope_key="material-a"))
    source = table_context.source_object_refs[0]
    label = source.display_name or f"{source.object_type} · {str(source.version_id)[:8]}"
    assert {f.title for f in scoped.figures} == {f"{f.title} · {label}" for f in bundle.figures}
    assert {t.title for t in scoped.tables} == {f"{t.title} · {label}" for t in bundle.tables}


@pytest.mark.parametrize("state", ["RUNNING", "FAILED", None])
def test_table_title_does_not_describe_uncommitted_execution(table_context, state):
    from mdi_api.application.scientific_results.figure_titles import scientific_figure_title
    calls = [{**c, "state": state} for c in table_context.tool_calls]
    title = "数值表格分布与相关性分析"
    assert scientific_figure_title(title, ["table_call_2-plotly_json"],
        artifacts=table_context.artifacts, calls=calls, job_id="job_adapter", project_id=table_context.project_id) == title


@pytest.mark.parametrize("params", [None, {"method": []}, {"method": "other"}])
def test_table_title_does_not_invent_a_method_from_malformed_saved_params(table_context, params):
    from mdi_api.application.scientific_results.figure_titles import scientific_figure_title
    calls = [{**c, "paramsJson": params} for c in table_context.tool_calls]
    assert scientific_figure_title("数值表格分布与相关性分析", ["table_call_2-plotly_json"],
        artifacts=table_context.artifacts, calls=calls, job_id="job_adapter", project_id=table_context.project_id) == "相关矩阵"


def test_dense_correlation_stays_within_model_budget_and_keeps_pair_identities(table_context):
    from mdi_api.research_agent.context.policy import ContextOperation, context_budget_policy
    chart = CorrelationAdapter().run(pd.DataFrame({f"property_{i}": [i + 1., i + 2., i + 3., i + 4.]
                                                 for i in range(30)}), {})
    payloads = deepcopy(table_context.artifact_payloads)
    payloads["table_call_2-table_json"] = chart.metadata
    payloads["table_call_2-plotly_json"] = chart.figure.to_plotly_json()
    bundle = _project(replace(table_context, artifact_payloads=payloads))
    assert len([f for f in bundle.facts if f.predicate == "correlation.coefficient"]) == 435
    envelope, _ = InterpreterInputAssembler().assemble(bundle=bundle, question="解释相关性", relevance_status="CURRENT")
    report, _ = ReportComposerInputAssembler().assemble(bundle=bundle, interpretation={}, relevance_status="CURRENT")
    for encoded, operation in ((envelope.model_dump(mode="json"), ContextOperation.INTERPRETER), (report, ContextOperation.REPORT)):
        assert len(json.dumps(encoded, sort_keys=True, separators=(",", ":")).encode()) // 4 <= context_budget_policy(operation).effective_input_budget
    for payload in (envelope.result, report["result"]):
        pairs = [f for f in payload["facts"] if f["predicate"] == "correlation.coefficient"]
        assert pairs
        for pair in pairs:
            assert {f["predicate"] for f in payload["facts"] if f.get("subject_ref") == pair.get("subject_ref")} >= {
                "correlation.left_column", "correlation.right_column", "correlation.coefficient"}
        allowed = {f["fact_id"] for f in payload["facts"]}
        for item in [*payload["figures"], *payload["tables"], *payload["result_items"]]:
            assert set(item["fact_refs"]) <= allowed
    assert "items omitted" in envelope.omitted_supporting_items[0]
    assert report["omitted_supporting_items"]


@pytest.mark.parametrize("table_context", [
    {"method": "pearson", "minNonNullCount": 1},
    {"method": "spearman", "minNonNullCount": 1},
], indirect=True)
def test_minimum_one_setting_preserves_real_correlation_across_model_inputs(table_context):
    matrix = table_context.artifact_payloads["table_call_2-table_json"]
    plot = table_context.artifact_payloads["table_call_2-plotly_json"]
    assert matrix["minNonNullCount"] == 1
    assert matrix["validPairCount"] == 1
    assert matrix["matrix"] == plot["data"][0]["z"]
    assert matrix["matrix"][2] == [None, None, None]

    bundle = _project(table_context)
    minimum = next(f for f in bundle.facts if f.predicate == "correlation.minimum_sample_count")
    coefficient = next(f for f in bundle.facts if f.predicate == "correlation.coefficient")
    assert minimum.value == 1
    assert coefficient.value == pytest.approx(-1)
    assert minimum.source.artifact_locator == "/minNonNullCount"
    assert coefficient.source.artifact_locator == "/matrix/0/1"
    for fact in (minimum, coefficient):
        assert resolve_json_pointer(table_context.artifact_payloads[fact.source.artifact_id], fact.source.artifact_locator) == fact.value
    envelope, _ = InterpreterInputAssembler().assemble(bundle=bundle, question="解释相关性", relevance_status="CURRENT")
    report, _ = ReportComposerInputAssembler().assemble(bundle=bundle, interpretation={}, relevance_status="CURRENT")
    for payload in (envelope.result, report["result"]):
        represented = {f["fact_id"]: f for f in payload["facts"]}
        assert represented[minimum.fact_id]["value"] == 1
        assert represented[coefficient.fact_id]["value"] == pytest.approx(-1)


@pytest.mark.parametrize("minimum", [0, -1, True, False, 1.5, "1", None])
def test_invalid_minimum_correlation_setting_cannot_create_facts(table_context, minimum):
    context = deepcopy(table_context)
    context.artifact_payloads["table_call_2-table_json"]["minNonNullCount"] = minimum
    with pytest.raises(ScientificResultProjectionFailed):
        _project(context)


@pytest.mark.parametrize("tool_index", range(5))
def test_recipe_cannot_replace_a_missing_scientific_output(table_context, tool_index):
    context = replace(table_context, artifacts=tuple(a for a in table_context.artifacts
                      if a["toolCallId"] != f"table_call_{tool_index}" or a["type"] == "recipe_json"))
    with pytest.raises(ScientificResultProjectionFailed):
        _project(context)


@pytest.mark.parametrize("invalid", ["duplicate", "ragged", "boolean", "asymmetric", "count", "method", "foreign_call"])
def test_invalid_correlation_cannot_create_facts(table_context, invalid):
    context = deepcopy(table_context)
    data = context.artifact_payloads["table_call_2-table_json"]
    if invalid == "duplicate":
        data["columns"][1] = data["columns"][0]
    elif invalid == "ragged":
        data["matrix"][0].pop()
    elif invalid == "boolean":
        data["matrix"][0][1] = True
    elif invalid == "asymmetric":
        data["matrix"][0][1] = 0.5
    elif invalid == "count":
        data["validPairCount"] += 1
    elif invalid == "method":
        data["method"] = "imaginary"
    else:
        context = replace(context, artifacts=tuple({**a, "toolCallId": "foreign-call"}
                          if a["id"] == "table_call_2-table_json" else a for a in context.artifacts))
    with pytest.raises(ScientificResultProjectionFailed):
        _project(context)


def test_projection_is_deterministic_and_does_not_modify_saved_payloads(table_context):
    before = deepcopy(table_context.artifact_payloads)
    first, second = _project(table_context), _project(table_context)
    assert first == second
    assert table_context.artifact_payloads == before
    assert not any(f.source.artifact_id.endswith("recipe_json") for f in first.facts)


def test_saved_zero_and_missing_correlations_are_distinct(table_context):
    context = deepcopy(table_context)
    data = context.artifact_payloads["table_call_2-table_json"]
    data["matrix"][0][1] = data["matrix"][1][0] = 0.0
    bundle = _project(context)
    coefficients = [f for f in bundle.facts if f.predicate == "correlation.coefficient"]
    assert [f.value for f in coefficients] == [0.0]
    assert coefficients[0].source.artifact_locator == "/matrix/0/1"
    assert next(f for f in bundle.facts if f.predicate == "correlation.missing_pair_count").value == 2


def test_legacy_distribution_preserves_files_without_inventing_column_locators(table_context):
    context = deepcopy(table_context)
    data = context.artifact_payloads["table_call_0-table_json"]
    for family in ("numericColumns", "categoricalColumns"):
        for stats in data[family].values():
            stats.pop("column")
    bundle = _project(context)
    assert any(w.code == "TABLE_ANALYSIS_LEGACY_COLUMN_IDENTITY" for w in bundle.warnings)
    assert all(f.predicate in {"table.row_count", "table.column_count"} for f in bundle.facts
               if f.source.artifact_id == "table_call_0-table_json")


@pytest.mark.parametrize("key,value", [("mean", 1000), ("std", -1), ("missingRate", 1), ("uniqueCount", 50), ("column", "other")])
def test_inconsistent_saved_statistics_fail_closed(table_context, key, value):
    context = deepcopy(table_context)
    context.artifact_payloads["table_call_0-table_json"]["numericColumns"]["gap"][key] = value
    with pytest.raises(ScientificResultProjectionFailed):
        _project(context)


def test_uncompleted_tool_cannot_publish_saved_looking_output(table_context):
    context = replace(table_context, tool_calls=tuple({**call, "state": "failed"}
                      if call["id"] == "table_call_2" else call for call in table_context.tool_calls))
    with pytest.raises(ScientificResultProjectionFailed):
        _project(context)


@pytest.mark.parametrize("table_context", [
    {}, {"method": "pearson", "minNonNullCount": 1}, {"method": "spearman", "minNonNullCount": 1},
], indirect=True)
def test_real_table_facts_ground_interpretation_and_report(table_context):
    bundle = _project(table_context)
    coefficient = next(f for f in bundle.facts if f.predicate == "correlation.coefficient")
    refs = [f.fact_id for f in bundle.facts if f.subject_ref == coefficient.subject_ref]
    method = next(f.value for f in bundle.facts if f.predicate == "correlation.method")
    statement = f"energy/~eV 与 gap 的 {method.title()} 相关系数为 -1。"
    output = ScientificInterpretationOutput.model_validate({
        "contract_version": "1.0", "title": "表格分析", "answer_lead": statement,
        "primary_findings": [{"finding_id": "pair", "statement": statement, "importance": "HIGH",
            "confidence": "HIGH", "fact_refs": refs, "evidence_refs": [], "result_item_refs": []}],
        "supporting_findings": [], "limitations": [], "primary_result_refs": [bundle.result_items[0].id],
        "supporting_result_refs": [], "follow_up_suggestions": []})
    assert validate_interpretation(output, bundle).valid
    interpretation = {"interpretation": output.model_dump(mode="json")}
    report = DeterministicScientificReportComposer().compose(bundle=bundle, interpretation=interpretation, relevance_status="CURRENT")
    assert ReportGroundingValidator().validate(report, bundle=bundle, interpretation=interpretation) == []
    assert {figure.caption for figure in report.primary_figures} == {
        f"{method.title()} 相关矩阵", "直方图 · energy/~eV", "散点图 · energy/~eV × gap",
    }
    output.primary_findings[0].statement = "Pearson 相关系数为 0.987654。"
    assert not validate_interpretation(output, bundle).valid
    output.primary_findings[0].statement = "energy/~eV 与 gap 的相关系数为 -1 eV。"
    assert not validate_interpretation(output, bundle).valid
