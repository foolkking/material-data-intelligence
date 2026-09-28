from __future__ import annotations

import importlib

from mdi_api.application.phase2.models import (
    CreateJobRequest,
    CreateProjectRequest,
    DatasetRecord,
    DatasetUploadRequest,
    InlineUploadFile,
    JobRunRecord,
    MaterializedUpload,
    ProjectRecord,
    UploadSessionFileRecord,
    UploadSessionRecord,
)
from mdi_api.infrastructure.phase2 import runtime as canonical
from mdi_api.infrastructure.persistence.phase2_artifacts import LocalFileArtifactStore


def test_legacy_phase2_module_is_canonical_module_alias() -> None:
    legacy = importlib.import_module("mdi_api.phase2_runtime")

    assert legacy is canonical


def test_phase2_public_models_and_store_have_one_identity() -> None:
    legacy = importlib.import_module("mdi_api.phase2_runtime")
    expected = {
        "CreateJobRequest": CreateJobRequest,
        "CreateProjectRequest": CreateProjectRequest,
        "DatasetRecord": DatasetRecord,
        "DatasetUploadRequest": DatasetUploadRequest,
        "InlineUploadFile": InlineUploadFile,
        "JobRunRecord": JobRunRecord,
        "LocalFileArtifactStore": LocalFileArtifactStore,
        "MaterializedUpload": MaterializedUpload,
        "ProjectRecord": ProjectRecord,
        "UploadSessionFileRecord": UploadSessionFileRecord,
        "UploadSessionRecord": UploadSessionRecord,
    }

    for name, owner in expected.items():
        assert getattr(legacy, name) is owner


def test_legacy_monkeypatch_targets_canonical_runtime(monkeypatch) -> None:
    legacy = importlib.import_module("mdi_api.phase2_runtime")

    replacement = object()
    monkeypatch.setattr(legacy, "build_phase2_plan", replacement)

    assert canonical.build_phase2_plan is replacement

