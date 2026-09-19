from __future__ import annotations

import hashlib
import json
from types import SimpleNamespace

from mdi_api.infrastructure.scientific_objects.service import ScientificObjectService


class _Session:
    def __init__(self, dataset: dict[str, object]) -> None:
        self.repositories = SimpleNamespace(
            datasets=SimpleNamespace(get=lambda _dataset_id: dataset),
        )

    def __enter__(self) -> "_Session":
        return self

    def __exit__(self, *_args: object) -> None:
        return None


class _RepositoryFactory:
    def __init__(self, dataset: dict[str, object]) -> None:
        self._dataset = dataset

    def session(self) -> _Session:
        return _Session(self._dataset)


class _Storage:
    def __init__(self, payloads: dict[str, bytes]) -> None:
        self._payloads = payloads

    def get_bytes_bounded(self, key: str, *, max_bytes: int) -> bytes:
        value = self._payloads[key]
        assert len(value) <= max_bytes
        return value


def test_semantically_typed_experimental_xrd_dataframe_uses_generic_admission() -> None:
    project_id = "project-xrd"
    dataset_id = "dataset-xrd"
    resource_id = f"{dataset_id}:resource-xrd"
    payload = json.dumps(
        [{"two_theta": 20.0, "intensity": 10.0}],
        separators=(",", ":"),
    ).encode("utf-8")
    content_hash = hashlib.sha256(payload).hexdigest()
    storage_key = f"projects/{project_id}/datasets/{dataset_id}/normalized/{resource_id}/data.json"
    metadata_key = f"projects/{project_id}/datasets/{dataset_id}/normalized/{resource_id}/metadata.json"
    source_metadata = {
        "objectId": resource_id,
        "contentHash": content_hash,
        "provenance": {"objectType": "DataFrame"},
        "metadata": {
            "experimentalXrd": {
                "schemaVersion": "phase10n3.experimental_xrd_resource.v1",
            },
        },
    }
    dataset = {
        "projectId": project_id,
        "name": "Experimental XRD",
        "metadata": {
            "normalizedExports": [
                {
                    "objectId": resource_id,
                    "storageKey": storage_key,
                    "metadataKey": metadata_key,
                    "contentHash": content_hash,
                    "objectHash": "a" * 64,
                },
            ],
        },
    }
    service = ScientificObjectService.__new__(ScientificObjectService)
    service.repository_factory = _RepositoryFactory(dataset)
    service_calls: list[dict[str, object]] = []

    def admit_dataset_resource(**kwargs: object) -> tuple[dict[str, object], dict[str, object]]:
        service_calls.append(kwargs)
        return {"object_type": "diffraction.xrd.experimental"}, {"version": 1}

    service.admit_dataset_resource = admit_dataset_resource  # type: ignore[method-assign]

    result = service.create_table_from_dataset(
        project_id=project_id,
        dataset_id=dataset_id,
        resource_id=resource_id,
        storage=_Storage({
            storage_key: payload,
            metadata_key: json.dumps(source_metadata).encode("utf-8"),
        }),
    )

    assert result == (
        {"object_type": "diffraction.xrd.experimental"},
        {"version": 1},
    )
    assert len(service_calls) == 1
    assert service_calls[0]["project_id"] == project_id
    assert service_calls[0]["dataset_id"] == dataset_id
    assert service_calls[0]["resource_id"] == resource_id
