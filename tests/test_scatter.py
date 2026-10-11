from copy import deepcopy
import json

import numpy as np
import pandas as pd
import pytest
from jsonschema import Draft202012Validator

from mdi_adapters import ScatterAdapter
from mdi_adapters.errors import ToolExecutionError
from mdi_api.application.scientific_results.projectors.table_analysis import valid_table_output, table_facts, table_warnings
from mdi_tool_registry import load_manifests


def payload(frame, **params):
    result = ScatterAdapter().run(frame, {"xColumn": "x", "yColumn": "y", **params})
    return {**result.metadata, "figure": json.loads(result.figure.to_json())}


def test_numeric_strings_are_paired_and_invalid_coordinates_are_excluded():
    frame = pd.DataFrame({"x": ["2", "10", "bad", None, float("inf"), 5], "y": ["1", "4", "8", 2, 3, None], "material": ["Si", "Cu", "bad", "bad", "bad", "bad"]})
    result = payload(frame, hoverColumns=["material", "x"])
    trace = result["figure"]["data"][0]
    assert trace["x"] == [2, 10] and trace["y"] == [1, 4]
    assert trace["customdata"] == [[1, "Si", "2"], [2, "Cu", "10"]]
    assert result["xRange"] == [2, 10] and result["yRange"] == [1, 4]
    assert result["inputCount"] == 6 and result["pointCount"] == result["validPointCount"] == 2
    assert result["excludedCount"] == result["excludedCoordinateCount"] == 4
    assert result["excludedColorCount"] == result["omittedPointCount"] == 0
    assert valid_table_output("viz.scatter", "plotly_json", result)
    facts = {f.predicate: f for f in table_facts({"id": "scatter"}, result)}
    assert facts["scatter.excluded_count"].value == 4
    assert facts["scatter.valid_point_count"].source.artifact_locator == "/validPointCount"


def test_same_axis_and_overlapping_hover_color_columns_are_valid():
    result = payload(pd.DataFrame({"x": [1, 2, 3]}), yColumn="x", colorColumn="x", hoverColumns=["x"])
    trace = result["figure"]["data"][0]
    assert trace["x"] == trace["y"] == trace["marker"]["color"] == [1, 2, 3]
    assert trace["customdata"] == [[1, 1], [2, 2], [3, 3]]
    assert result["colorMode"] == "numeric"


def test_numeric_color_exclusion_is_distinct_from_invalid_coordinates():
    frame = pd.DataFrame({"x": [0, 1, 2, 3, None], "y": [1, 2, 3, 4, 5], "c": [10., None, 20., float("inf"), 30.]})
    result = payload(frame, colorColumn="c")
    assert result["pointCount"] == 2 and result["excludedCount"] == 3
    assert result["excludedCoordinateCount"] == 1 and result["excludedColorCount"] == 2
    assert result["figure"]["data"][0]["customdata"] == [[1], [3]]
    assert result["figure"]["data"][0]["marker"]["color"] == [10, 20]


def test_categorical_colors_retain_missing_and_typed_labels():
    frame = pd.DataFrame({"x": range(5), "y": range(5), "c": [1, "1", None, "（缺失）", 1]})
    result = payload(frame, colorColumn="c")
    assert result["colorMode"] == "categorical" and result["pointCount"] == 5
    assert len({g["label"] for g in result["groups"]}) == 4
    assert [g["label"] for g in result["groups"]] == ["1（整数）", "1（文本）", "（缺失）（空值）", "（缺失）（文本）"]
    assert [g["value"] for g in result["groups"]] == [1, "1", None, "（缺失）"]
    assert sorted(row[0] for trace in result["figure"]["data"] for row in trace["customdata"]) == [1, 2, 3, 4, 5]


def test_large_scatter_samples_all_source_regions_and_keeps_extrema_and_rare_groups():
    size = 60013
    frame = pd.DataFrame({"x": np.arange(size, dtype=float), "y": np.zeros(size), "c": ["common"] * size})
    frame.loc[50007, "y"] = -100
    frame.loc[60001, "y"] = 100
    frame.loc[59997, "c"] = "rare"
    frame.loc[100, "x"] = np.nan
    result = payload(frame, colorColumn="c")
    points = {row[0]: (trace["x"][i], trace["y"][i]) for trace in result["figure"]["data"] for i, row in enumerate(trace["customdata"])}
    assert len(points) == result["pointCount"] == 50000
    assert result["validPointCount"] == size - 1 and result["omittedPointCount"] == size - 50001
    assert result["excludedCount"] == 1
    assert {1, size, 50008, 60002, 59998} <= points.keys()
    assert 101 not in points
    assert points[60002] == (60001, 100) and points[50008] == (50007, -100)
    assert result["xRange"] == [0, size - 1] and result["yRange"] == [-100, 100]
    assert all(tuple(frame.iloc[row - 1][["x", "y"]]) == point for row, point in points.items())
    assert valid_table_output("viz.scatter", "plotly_json", result)
    warnings = table_warnings("scatter", result)
    assert any(w.code == "TABLE_ANALYSIS_SCATTER_SAMPLED" for w in warnings)
    assert "前 50000" not in " ".join(w.message for w in warnings)


@pytest.mark.parametrize("params,reason", [
    ({"xColumn": "absent"}, "SCATTER_COLUMN_INVALID"),
    ({"hoverColumns": ["x", "x"]}, "SCATTER_PARAMS_INVALID"),
    ({"hoverColumns": list("abcdefghi")}, "SCATTER_PARAMS_INVALID"),
    ({"colorColumn": ""}, "SCATTER_PARAMS_INVALID"),
])
def test_invalid_selections_fail_explicitly(params, reason):
    with pytest.raises(ToolExecutionError) as error:
        payload(pd.DataFrame({"x": [1, 2], "y": [3, 4]}), **params)
    assert error.value.details["errorType"] == reason


@pytest.mark.parametrize("frame,params,reason", [
    (pd.DataFrame({"x": [1, None], "y": [None, 1]}), {}, "SCATTER_VALUES_INVALID"),
    (pd.DataFrame({"x": [1j], "y": [1]}), {}, "SCATTER_VALUES_INVALID"),
    (pd.DataFrame([[1, 2, 3]], columns=["x", "x", "y"]), {}, "SCATTER_COLUMN_INVALID"),
    (pd.DataFrame({"x": range(65), "y": range(65), "c": [str(i) for i in range(65)]}), {"colorColumn": "c"}, "SCATTER_GROUP_LIMIT"),
    (pd.DataFrame({"x": [1, 2], "y": [3, 4], "c": [[1], [2]]}), {"colorColumn": "c"}, "SCATTER_GROUP_INVALID"),
    (pd.DataFrame({"x": [-1e308, 1e308], "y": [1, 2]}), {}, "SCATTER_RANGE_INVALID"),
])
def test_invalid_numeric_and_group_data_have_safe_reasons(frame, params, reason):
    with pytest.raises(ToolExecutionError) as error:
        payload(frame, **params)
    assert error.value.details["errorType"] == reason


def test_registry_bounds_hover_columns():
    validator = Draft202012Validator(load_manifests().get_tool_by_id("viz.scatter").paramsSchema)
    assert list(validator.iter_errors({"xColumn": "x", "yColumn": "y", "hoverColumns": ["x", "x"]}))
    assert not list(validator.iter_errors({"xColumn": "x", "yColumn": "x", "hoverColumns": ["x"]}))


@pytest.mark.parametrize("change", [
    lambda p: p.update(pointCount=99),
    lambda p: p.update(excludedCount=99),
    lambda p: p.update(xRange=[1, 99]),
    lambda p: p["figure"]["data"][0].update(customdata=[[1], [1]]),
    lambda p: p["figure"]["data"][0].update(transforms=[]),
    lambda p: p["figure"]["layout"]["xaxis"].update(type="category"),
    lambda p: p["figure"]["data"][0]["marker"].update(color=[1, 2]),
])
def test_corrupted_scatter_does_not_satisfy_scientific_coverage(change):
    result = deepcopy(payload(pd.DataFrame({"x": [1, 2], "y": [3, 4]})))
    change(result)
    assert not valid_table_output("viz.scatter", "plotly_json", result)


@pytest.mark.parametrize("colors", [[1], [1, None], [1, float("inf")], ["1", "2"]])
def test_inconsistent_continuous_colors_do_not_satisfy_scientific_coverage(colors):
    result = payload(pd.DataFrame({"x": [1, 2], "y": [3, 4]}), colorColumn="x")
    result["figure"]["data"][0]["marker"]["color"] = colors
    assert not valid_table_output("viz.scatter", "plotly_json", result)
