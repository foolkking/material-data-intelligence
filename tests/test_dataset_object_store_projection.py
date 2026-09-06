from mdi_api.routers import datasets as dataset_routes
from mdi_api.routers.datasets import _json_safe_resource
from mdi_material_parsers.models import NormalizedObjectDraft
from mdi_schemas import MaterialObjectType


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


def test_source_viewer_receives_canonical_trajectory_payload_not_execution_wrapper(monkeypatch):
    payload = {
        "schema_version": "phase10g.trajectory.v1",
        "trajectory_id": "sha256:" + "1" * 64,
        "frames": [{"frame_index": 0}],
    }
    draft = NormalizedObjectDraft(
        id="trajectory_1",
        dataset_id="dataset_1",
        object_type=MaterialObjectType.Trajectory,
        source_file_ids=["file_1"],
        storage_key="normalized/trajectory_1/trajectory.json",
        metadata={"detectedFormat": "extxyz"},
        hash="2" * 64,
        payload=payload,
    )
    monkeypatch.setattr(
        "mdi_api.phase2_runtime.get_phase2_dataset_object_store",
        lambda _dataset_id: {
            "__mdi_source_resources__": {
                "trajectory_1": {
                    "objectId": "trajectory_1",
                    "objectType": "Trajectory",
                    "objectHash": "2" * 64,
                    "datasetId": "dataset_1",
                },
            },
            "trajectory_1": draft,
        },
    )

    projected = dataset_routes.get_dataset_object_store("dataset_1")

    assert projected["resources"][0]["payload"] == payload


def test_source_table_projects_profile_defined_stable_sample_identity(monkeypatch):
    object_hash = "a" * 64
    monkeypatch.setattr(
        "mdi_api.phase2_runtime.get_phase2_dataset_object_store",
        lambda _dataset_id: {
            "__mdi_source_resources__": {
                "table_1": {
                    "objectId": "table_1",
                    "objectType": "DataFrame",
                    "objectHash": object_hash,
                    "datasetId": "dataset_1",
                },
            },
            "table_1": [{"formula": "Si", "value": 1}],
        },
    )
    monkeypatch.setattr(
        "mdi_api.phase2_runtime.get_phase2_dataset_profile",
        lambda _dataset_id: {"version": "2"},
    )

    projected = dataset_routes.get_dataset_object_store("dataset_1")
    row = projected["resources"][0]["payload"][0]

    assert row == {
        "formula": "Si",
        "value": 1,
        "objectId": "table_1",
        "sampleRef": "dataset_1@2:aaaaaaaaaaaaaaaa:0",
        "sampleKey": "table_1:dataset_1@2:aaaaaaaaaaaaaaaa:0",
    }


def test_source_table_preserves_explicit_sample_identity(monkeypatch):
    monkeypatch.setattr(
        "mdi_api.phase2_runtime.get_phase2_dataset_object_store",
        lambda _dataset_id: {
            "__mdi_source_resources__": {
                "table_1": {
                    "objectId": "table_1",
                    "objectType": "DataFrame",
                    "objectHash": "b" * 64,
                    "datasetId": "dataset_1",
                },
            },
            "table_1": [{"sample_id": "mat-2", "formula": "Si"}],
        },
    )
    monkeypatch.setattr(
        "mdi_api.phase2_runtime.get_phase2_dataset_profile",
        lambda _dataset_id: {"version": "3"},
    )

    projected = dataset_routes.get_dataset_object_store("dataset_1")
    row = projected["resources"][0]["payload"][0]

    assert row["sample_id"] == "mat-2"
    assert row["sampleRef"] == "mat-2"
    assert row["sampleKey"] == "table_1:mat-2"
