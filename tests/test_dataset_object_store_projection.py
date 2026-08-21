from mdi_api.routers.datasets import _json_safe_resource


def test_volumetric_channel_values_are_not_silently_cut_at_generic_list_limit():
    values = [float(index) for index in range(100_001)]

    projected = _json_safe_resource({
        "name": "density",
        "quantity": "generic_scalar",
        "values": values,
    })

    assert isinstance(projected, dict)
    assert len(projected["values"]) == len(values)
    assert projected["values"][-1] == values[-1]


def test_generic_source_lists_remain_bounded():
    projected = _json_safe_resource(list(range(100_001)))

    assert isinstance(projected, list)
    assert len(projected) == 100_000
