from copy import deepcopy

import pytest
from fastapi import HTTPException

from mdi_api.application.research.source_catalog import research_source_catalog


def source_fixture():
    dataset = {"id": "d", "projectId": "p", "name": "batch", "status": "profile_ready", "metadata": {
        "files": [{"fileId": "f", "name": r"C:\private\Si.cif", "secret": "must-not-appear"}],
        "normalizedExports": [{"objectId": "resource", "objectHash": "a" * 64, "storageKey": "private/key"}],
    }}
    profile = {"datasetId": "d", "profileId": "profile", "objects": [{
        "objectId": "resource", "objectHash": "a" * 64, "objectType": "Structure", "sourceFileIds": ["f"],
    }]}
    return dataset, profile


def test_catalog_projects_only_exact_names_types_and_hashes_without_payloads():
    dataset, profile = source_fixture()
    original = deepcopy((dataset, profile))
    assert research_source_catalog(dataset, [profile]) == {
        "datasetId": "d", "projectId": "p", "resources": [{
            "datasetId": "d", "objectId": "resource", "objectHash": "a" * 64,
            "objectType": "Structure", "displayName": "Si.cif",
        }],
    }
    assert (dataset, profile) == original


@pytest.mark.parametrize("problem", ["hash", "duplicate_export", "duplicate_profile_object", "foreign_profile", "unprofiled", "trashed", "unsupported"])
def test_catalog_never_exposes_ambiguous_unprofiled_or_unavailable_resources(problem):
    dataset, profile = source_fixture()
    if problem == "hash": profile["objects"][0]["objectHash"] = "b" * 64
    if problem == "duplicate_export": dataset["metadata"]["normalizedExports"] *= 2
    if problem == "duplicate_profile_object": profile["objects"] *= 2
    if problem == "foreign_profile": profile["datasetId"] = "another"
    if problem == "unprofiled": dataset["status"] = "parsing"
    if problem == "trashed": dataset["metadata"]["trashedAt"] = "today"
    if problem == "unsupported": profile["objects"][0]["objectType"] = "Image"
    assert research_source_catalog(dataset, [profile])["resources"] == []


def test_companion_filenames_follow_exact_profile_file_ids_not_array_position():
    dataset, profile = source_fixture()
    dataset["metadata"]["files"].insert(0, {"fileId": "wrong", "name": "Cu.cif"})
    dataset["metadata"]["files"].append({"fileId": "partner", "name": "DOS.dat"})
    profile["objects"][0]["sourceFileIds"] = ["f", "partner"]
    assert research_source_catalog(dataset, [profile])["resources"][0]["displayName"] == "Si.cif + DOS.dat"


def test_source_catalog_authorizes_before_reading_any_dataset(monkeypatch):
    from mdi_api.transport.routers import secured_runtime
    from mdi_api.bootstrap import repository_factory
    def deny(*args): raise HTTPException(status_code=403)
    def forbidden(*args): raise AssertionError("read happened before authorization")
    monkeypatch.setattr(secured_runtime, "_authorize_dataset", deny)
    monkeypatch.setattr(repository_factory, "create_repository_factory", forbidden)
    with pytest.raises(HTTPException) as exc:
        secured_runtime.get_dataset_research_sources_secured("d", object())
    assert exc.value.status_code == 403
