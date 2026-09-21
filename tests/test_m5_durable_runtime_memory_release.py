from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from mdi_api.infrastructure.phase2 import runtime as phase2_runtime


@dataclass
class _Dataset:
    id: str


class _Runtime:
    def __init__(self) -> None:
        self.datasets = {"dataset-1": _Dataset("dataset-1")}
        self.upload_sessions = {}

    def upload_dataset(self, request: object) -> dict[str, str]:
        return {"datasetId": "dataset-1"}


def test_durable_direct_upload_releases_parsed_runtime_dataset(monkeypatch) -> None:
    runtime = _Runtime()
    monkeypatch.setattr(phase2_runtime, "get_phase2_runtime", lambda: runtime)
    monkeypatch.setattr(
        "mdi_api.durable_uploads.persist_phase2_upload",
        lambda active_runtime, dataset_id: SimpleNamespace(dataset_id=dataset_id),
    )

    result = phase2_runtime.upload_phase2_dataset(SimpleNamespace())

    assert result == {"datasetId": "dataset-1"}
    assert runtime.datasets == {}


def test_nondurable_direct_upload_keeps_local_runtime_dataset(monkeypatch) -> None:
    runtime = _Runtime()
    monkeypatch.setattr(phase2_runtime, "get_phase2_runtime", lambda: runtime)
    monkeypatch.setattr(
        "mdi_api.durable_uploads.persist_phase2_upload",
        lambda active_runtime, dataset_id: None,
    )

    phase2_runtime.upload_phase2_dataset(SimpleNamespace())

    assert list(runtime.datasets) == ["dataset-1"]


def test_completed_session_replay_reads_durable_dataset_after_release(monkeypatch) -> None:
    runtime = _Runtime()
    runtime.datasets.clear()
    runtime.upload_sessions["upload-1"] = SimpleNamespace(
        status="completed",
        dataset_id="dataset-1",
    )
    monkeypatch.setattr(phase2_runtime, "get_phase2_runtime", lambda: runtime)
    monkeypatch.setattr(
        phase2_runtime,
        "get_phase2_dataset",
        lambda dataset_id: {"datasetId": dataset_id, "status": "profile_ready"},
    )

    result = phase2_runtime.complete_phase2_upload_session("upload-1")

    assert result == {"datasetId": "dataset-1", "status": "profile_ready"}
