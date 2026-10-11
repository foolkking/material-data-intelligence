from dataclasses import dataclass

from mdi_adapters.profile_binding import canonical_profile_resource_ref


@dataclass(frozen=True)
class _ProfileResource:
    objectId: str
    objectHash: str


def test_exact_version_ref_resolves_only_through_persisted_profile_alias():
    version_id = "cf2aeeea-53ad-452a-a4ef-7b61555004e5"
    resource_id = "obj_dataframe_0088232d32ff"
    resources = [_ProfileResource(resource_id, "1" * 64)]
    object_store = {
        "__mdi_source_resources__": {
            version_id: {
                "objectId": version_id,
                "objectType": "DataFrame",
                "objectHash": "2" * 64,
                "datasetId": "dataset_1",
            },
            resource_id: {
                "objectId": version_id,
                "objectType": "DataFrame",
                "objectHash": "2" * 64,
                "datasetId": "dataset_1",
                "alias": resource_id,
                "canonicalObjectId": version_id,
            },
        }
    }

    assert canonical_profile_resource_ref(
        object_store=object_store,
        runtime_ref=version_id,
        profile_resources=resources,
    ) == resource_id


def test_non_version_unprofiled_resource_is_not_admitted_by_matching_hash():
    profile_resource = _ProfileResource("obj_profiled", "1" * 64)
    object_store = {
        "__mdi_source_resources__": {
            "obj_unprofiled": {
                "objectId": "obj_unprofiled",
                "objectType": "DataFrame",
                "objectHash": profile_resource.objectHash,
                "datasetId": "dataset_1",
            },
        }
    }

    assert canonical_profile_resource_ref(
        object_store=object_store,
        runtime_ref="obj_unprofiled",
        profile_resources=[profile_resource],
    ) == "obj_unprofiled"


def test_exact_version_resolves_scoped_profile_identity_without_a_global_alias():
    version_id = "cf2aeeea-53ad-452a-a4ef-7b61555004e5"
    store = {"__mdi_source_resources__": {version_id: {
        "objectId": version_id, "objectType": "DataFrame", "objectHash": "2" * 64,
        "datasetId": "dataset_b", "profileObjectId": "shared-parser-id",
    }}}
    assert canonical_profile_resource_ref(
        object_store=store, runtime_ref=version_id,
        profile_resources=[_ProfileResource("shared-parser-id", "1" * 64)],
    ) == "shared-parser-id"
    assert canonical_profile_resource_ref(
        object_store=store, runtime_ref=version_id,
        profile_resources=[_ProfileResource("another-resource", "1" * 64)],
    ) == version_id
