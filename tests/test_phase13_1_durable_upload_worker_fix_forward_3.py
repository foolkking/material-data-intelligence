from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from mdi_api.artifact_storage import LocalFileArtifactStorage
from mdi_api.durable_uploads import _persist_normalized_exports
from mdi_api.routers.planner import _execution_object_store_for_dataset
from mdi_api.phase2_runtime import CreateProjectRequest, DatasetUploadRequest, Phase2ProductRuntime
from mdi_workers.object_store import DurableObjectStoreResolver


def _source_export(storage: LocalFileArtifactStorage) -> dict[str, str]:
    data_key = "projects/project_a/datasets/dataset_a/normalized/object_a/data.json"
    metadata_key = "projects/project_a/datasets/dataset_a/normalized/object_a/metadata.json"
    payload = json.dumps({"formula": ["SiO2"]}, indent=2, sort_keys=True).encode("utf-8")
    content_hash = hashlib.sha256(payload).hexdigest()
    metadata = {
        "objectId": "object_a",
        "storageKey": data_key,
        "contentHash": content_hash,
        "metadata": {"objectType": "DataFrame"},
        "provenance": {"objectType": "DataFrame"},
    }
    storage.put_bytes(data_key, payload, content_type="application/json")
    storage.put_json(metadata_key, metadata)
    return {
        "objectId": "object_a",
        "storageKey": data_key,
        "metadataKey": metadata_key,
        "objectHash": content_hash,
        "contentHash": content_hash,
    }


def test_normalized_source_persistence_is_exact_and_idempotent(tmp_path: Path) -> None:
    source = LocalFileArtifactStorage(tmp_path / "source")
    durable = LocalFileArtifactStorage(tmp_path / "durable")
    export = _source_export(source)

    first = _persist_normalized_exports(
        source_storage=source,
        durable_storage=durable,
        project_id="project_a",
        dataset_id="dataset_a",
        exports=[export],
    )
    second = _persist_normalized_exports(
        source_storage=source,
        durable_storage=durable,
        project_id="project_a",
        dataset_id="dataset_a",
        exports=[export],
    )

    assert first == second == [export]
    assert hashlib.sha256(durable.get_bytes(export["storageKey"])).hexdigest() == export["contentHash"]


def test_normalized_source_persistence_rejects_scope_and_conflicting_content(tmp_path: Path) -> None:
    source = LocalFileArtifactStorage(tmp_path / "source")
    durable = LocalFileArtifactStorage(tmp_path / "durable")
    export = _source_export(source)
    wrong_scope = {**export, "storageKey": export["storageKey"].replace("project_a", "project_b")}
    with pytest.raises(ValueError, match="outside the dataset scope"):
        _persist_normalized_exports(
            source_storage=source,
            durable_storage=durable,
            project_id="project_a",
            dataset_id="dataset_a",
            exports=[wrong_scope],
        )

    durable.put_bytes(export["storageKey"], b"{}", content_type="application/json")
    with pytest.raises(ValueError, match="Conflicting durable source content"):
        _persist_normalized_exports(
            source_storage=source,
            durable_storage=durable,
            project_id="project_a",
            dataset_id="dataset_a",
            exports=[export],
        )


def test_durable_resolver_rejects_payload_hash_mismatch(tmp_path: Path) -> None:
    source = LocalFileArtifactStorage(tmp_path / "source")
    export = _source_export(source)
    source.put_bytes(export["storageKey"], b"{}", content_type="application/json")

    class Datasets:
        @staticmethod
        def get(dataset_id: str) -> dict[str, object]:
            return {
                "datasetId": dataset_id,
                "projectId": "project_a",
                "metadata": {"normalizedExports": [export]},
            }

    repos = SimpleNamespace(datasets=Datasets(), data_profiles=SimpleNamespace(list_for_dataset=lambda _id: []))
    resolver = DurableObjectStoreResolver(artifact_storage=source, repositories=repos)
    with pytest.raises(ValueError, match="payload checksum mismatch"):
        resolver.resolve("dataset_a")


def test_exact_durable_resolver_never_falls_back_to_process_memory() -> None:
    class Resolver:
        @staticmethod
        def resolve(dataset_id: str, *, profile_id: str | None = None) -> None:
            return None

    runtime = SimpleNamespace(object_store_resolver=Resolver())
    assert _execution_object_store_for_dataset(runtime, dataset_id="dataset_a", profile_id="profile_a") is None


def test_postgresql_runtime_ids_survive_process_restart_without_collision(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("MDI_RUNTIME_BACKEND", "postgresql")
    first = Phase2ProductRuntime(tmp_path / "first")
    second = Phase2ProductRuntime(tmp_path / "second")
    first_project = first.create_project(CreateProjectRequest(name="first"))
    second_project = second.create_project(CreateProjectRequest(name="second"))
    assert first_project["projectId"] != second_project["projectId"]
    first_dataset = first.upload_dataset(
        DatasetUploadRequest(
            projectId=first_project["projectId"],
            filePaths=["tests/fixtures/tables/formulas.csv"],
        )
    )
    second_dataset = second.upload_dataset(
        DatasetUploadRequest(
            projectId=second_project["projectId"],
            filePaths=["tests/fixtures/tables/formulas.csv"],
        )
    )
    assert first_dataset["datasetId"] != second_dataset["datasetId"]
