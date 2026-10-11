from copy import deepcopy
import json

import numpy as np
import pandas as pd
import pytest
from jsonschema import Draft202012Validator

from mdi_adapters import HistogramAdapter
from mdi_adapters.errors import ToolExecutionError
from mdi_api.application.scientific_results.projectors.table_analysis import valid_table_output, table_facts
from mdi_api.research_agent.execution.diagnostics import execution_warnings
from mdi_tool_registry import load_manifests


def payload(frame, **params):
    result = HistogramAdapter().run(frame, {"column": "x", **params})
    return {**result.metadata, "figure": json.loads(result.figure.to_json())}


@pytest.mark.parametrize("values,bins,edges,counts", [
    ([0, 1, 2, 3, 4], 4, [0, 1, 2, 3, 4], [1, 1, 1, 2]),
    ([7, 7, 7], 2, [6.5, 7, 7.5], [0, 3]),
    (["0", "1", "bad", "2", None, float("inf"), float("-inf")], 2, [0, 1, 2], [1, 2]),
    ([0, 4], 1, [0, 4], [2]),
])
def test_saved_intervals_drive_plot_counts_and_summary(values, bins, edges, counts):
    result = payload(pd.DataFrame({"x": values}), bins=bins)
    assert result["binEdges"] == edges and result["binCounts"] == counts
    assert result["count"] == sum(counts)
    assert result["inputCount"] == len(values)
    assert result["excludedCount"] == len(values) - sum(counts)
    trace = result["figure"]["data"][0]
    assert trace["type"] == "bar" and trace["y"] == counts
    assert trace["width"] == np.diff(edges).tolist()
    assert trace["customdata"][-1] == [edges[-2], edges[-1], "]"]
    assert trace["x"] == [(a + b) / 2 for a, b in zip(edges, edges[1:])]
    assert valid_table_output("viz.histogram", "plotly_json", result)
    facts = {f.predicate: f for f in table_facts({"id": "hist"}, result)}
    assert facts["histogram.excluded_count"].value == result["excludedCount"]
    assert facts["histogram.count"].source.artifact_locator == "/count"


def test_groups_share_edges_include_missing_and_preserve_typed_identity():
    frame = pd.DataFrame({"x": [0, 1, 2, 3, 4, 4, None], "g": [1, "1", None, "（缺失）", 1, "1", "unused"]})
    result = payload(frame, bins=2, groupBy="g")
    assert result["count"] == 6 and result["excludedCount"] == 1
    assert [g["value"] for g in result["groups"]] == [1, "1", None, "（缺失）"]
    assert len({g["label"] for g in result["groups"]}) == 4
    assert result["groups"][2]["binCounts"] == [0, 1]
    assert np.sum([g["binCounts"] for g in result["groups"]], axis=0).tolist() == result["binCounts"]
    for group, trace in zip(result["groups"], result["figure"]["data"]):
        assert trace["y"] == group["binCounts"] and trace["name"] == group["label"]
        assert trace["x"] == [1, 3] and trace["width"] == [2, 2]
    assert result["figure"]["layout"]["barmode"] == "stack"
    assert valid_table_output("viz.histogram", "plotly_json", result)


@pytest.mark.parametrize("bins", [0, -1, 4097, True, 2.5, "2", None])
def test_invalid_bins_fail_before_allocating(bins):
    with pytest.raises(ToolExecutionError) as caught:
        payload(pd.DataFrame({"x": [0, 1]}), bins=bins)
    assert caught.value.details["errorType"] == "HISTOGRAM_PARAMS_INVALID"


def test_registry_bounds_histogram_bins():
    validator = Draft202012Validator(load_manifests().get_tool_by_id("viz.histogram").paramsSchema)
    assert not list(validator.iter_errors({"column": "x", "bins": 4096}))
    assert list(validator.iter_errors({"column": "x", "bins": 4097}))


@pytest.mark.parametrize("frame,params,reason", [
    (pd.DataFrame({"x": [None, "bad", float("inf")]}), {}, "HISTOGRAM_VALUES_INVALID"),
    (pd.DataFrame({"x": [1+2j]}), {}, "HISTOGRAM_VALUES_INVALID"),
    (pd.DataFrame([[1, 2]], columns=["x", "x"]), {}, "HISTOGRAM_COLUMN_INVALID"),
    (pd.DataFrame({"x": [1, 2]}), {"groupBy": "absent"}, "HISTOGRAM_COLUMN_INVALID"),
    (pd.DataFrame({"x": [1], "g": [["array"]]}), {"groupBy": "g"}, "HISTOGRAM_GROUP_INVALID"),
    (pd.DataFrame({"x": range(17), "g": range(17)}), {"groupBy": "g"}, "HISTOGRAM_GROUP_LIMIT"),
    (pd.DataFrame({"x": [1e308, 1e308]}), {}, "HISTOGRAM_RANGE_INVALID"),
    (pd.DataFrame({"x": [-1e308, 1e308]}), {}, "HISTOGRAM_RANGE_INVALID"),
])
def test_unrepresentable_inputs_fail_with_actionable_safe_reason(frame, params, reason):
    with pytest.raises(ToolExecutionError) as caught:
        payload(frame, **params)
    assert caught.value.details["errorType"] == reason
    warning = execution_warnings({"status": "failed"}, [{"status": "error", "eventType": "tool.failed", "payload": {
        "toolId": "viz.histogram", "error": {"code": caught.value.code, "details": caught.value.details, "message": "secret"}}}])[0]
    assert warning.code == reason and "secret" not in warning.message


def test_nullable_numeric_series_and_maximum_bins_are_supported():
    result = payload(pd.DataFrame({"x": pd.Series([1, None, 2], dtype="Int64")}), bins=4096)
    assert result["count"] == 2 and result["excludedCount"] == 1
    assert len(result["binCounts"]) == 4096


@pytest.mark.parametrize("key,value", [("binCounts", [1, 99]), ("binEdges", [0, 0, 2]), ("excludedCount", 2), ("schemaVersion", "unknown")])
def test_inconsistent_saved_histogram_does_not_satisfy_scientific_coverage(key, value):
    result = payload(pd.DataFrame({"x": [0, 1, 2]}), bins=2)
    result[key] = value
    assert not valid_table_output("viz.histogram", "plotly_json", result)


def test_mismatched_group_counts_are_not_accepted_as_complete():
    result = payload(pd.DataFrame({"x": [0, 1, 2], "g": ["a", "b", "a"]}), bins=2, groupBy="g")
    corrupted = deepcopy(result)
    corrupted["groups"][0]["binCounts"] = [2, 0]
    assert not valid_table_output("viz.histogram", "plotly_json", corrupted)
