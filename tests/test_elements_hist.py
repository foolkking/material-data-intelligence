from __future__ import annotations

import pytest

from mdi_adapters import ElementsHistAdapter
from mdi_adapters.composition_common import formula_statistics, prepare_composition_input


def run_histogram(formulas, **params):
    prepared = prepare_composition_input({"formulas": formulas}, params, tool_id="composition.elements_hist")
    stats = formula_statistics(prepared, params, tool_id="composition.elements_hist")
    return ElementsHistAdapter().run(stats, params)


@pytest.mark.parametrize("count_mode", ["occurrence", "stoichiometric", "fractional"])
@pytest.mark.parametrize("top_n", [1, 2])
def test_tied_top_elements_have_the_same_identity_and_order_in_plot_and_saved_counts(count_mode, top_n):
    result = run_histogram(["FeO"] * 12 + ["Si"] * 3 + ["Cu"], countMode=count_mode, topN=top_n)
    bars = result.metadata["bars"]
    trace = result.figure.data[0]
    assert list(trace.x) == [bar["element"] for bar in bars]
    assert list(trace.y) == [bar["count"] for bar in bars]
    assert list(trace.x) == ["Fe", "O"][:top_n]


@pytest.mark.parametrize("log_y", [False, True])
def test_fallback_retains_scale_labels_and_source_provenance(monkeypatch, log_y):
    def unavailable(*args, **kwargs):
        raise RuntimeError("synthetic renderer failure")

    monkeypatch.setattr("mdi_adapters.pymatviz.elements_hist.pmv.elements_hist", unavailable)
    result = run_histogram(["FeO", "Si"], countMode="fractional", logY=log_y, showValues="count")
    assert result.figure.layout.yaxis.type == ("log" if log_y else "linear")
    assert ("对数刻度" in result.figure.layout.yaxis.title.text) is log_y
    assert list(result.figure.data[0].text) == ["1", "0.5", "0.5"]
    assert result.metadata["sourceFunction"] == "mdi_adapters.composition_common.simple_bar_figure"


def test_fractional_value_labels_are_not_truncated_to_zero():
    result = run_histogram(["FeO"], countMode="fractional", showValues="count")
    assert list(result.figure.data[0].text) == ["0.5", "0.5"]


def test_false_show_values_hides_labels():
    result = run_histogram(["FeO"], showValues=False)
    assert result.figure.data[0].text is None


def test_top_selection_discloses_omitted_elements_and_percentage_denominator():
    result = run_histogram(["FeO"] * 12 + ["Si"] * 3 + ["Cu"], countMode="occurrence", topN=1)
    assert result.metadata["fractionScope"] == "displayed_elements"
    assert result.metadata["totalElementValue"] == 28
    assert result.metadata["retainedElementValue"] == 12
    assert result.metadata["omittedElementCount"] == 3
    assert result.metadata["warnings"]


def test_label_modes_are_validated_by_the_current_registry():
    from jsonschema import Draft202012Validator
    from mdi_tool_registry import load_manifests

    validator = Draft202012Validator(load_manifests().get_tool_by_id("composition.elements_hist").paramsSchema)
    for value in ("percent", "count", True, False):
        assert validator.is_valid({"showValues": value})
    for value in ("misspelled", "", 0, 1, [], {}):
        assert not validator.is_valid({"showValues": value})
