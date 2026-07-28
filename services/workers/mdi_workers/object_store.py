from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from mdi_api.artifact_storage import ArtifactStorage
from mdi_api.unit_of_work import RepositoryFactory
from mdi_schemas import DataProfile, MaterialObjectType


class DurableObjectStoreResolver:
    """Rebuild worker object_store from persisted dataset metadata and storage.

    Phase2 parsing exports normalized objects to ArtifactStorage and records the
    export keys in dataset metadata. A Redis/RQ worker running out of process can
    use this resolver to reconstruct conventional runtime refs such as
    ``ml_table``, ``structures``, and ``formulas`` without receiving in-memory
    objects from the API process.
    """

    def __init__(
        self,
        *,
        artifact_storage: ArtifactStorage,
        repositories: Any | None = None,
        repository_factory: RepositoryFactory | None = None,
    ) -> None:
        self.artifact_storage = artifact_storage
        self.repositories = repositories
        self.repository_factory = repository_factory

    def __call__(self, dataset_id: str) -> Mapping[str, Any] | None:
        repos = self.repositories or self._repositories_from_factory()
        if repos is None:
            return None
        try:
            dataset = repos.datasets.get(dataset_id)
        except LookupError:
            return None

        exports = _normalized_exports(dataset)
        if not exports:
            return None

        structures: list[Any] = []
        structure_resources: dict[str, Any] = {}
        formulas: list[str] = []
        dataframes: list[pd.DataFrame] = []
        dataframe_resources: dict[str, pd.DataFrame] = {}

        for export in exports:
            metadata_key = str(export.get("metadataKey") or export.get("metadata_key") or "")
            storage_key = str(export.get("storageKey") or export.get("storage_key") or "")
            if not metadata_key or not storage_key:
                continue

            metadata_payload = self.artifact_storage.get_json(metadata_key)
            object_metadata = dict(metadata_payload.get("metadata") or {})
            object_type = str((metadata_payload.get("provenance") or {}).get("objectType") or object_metadata.get("objectType") or "")
            object_id = str(export.get("objectId") or export.get("object_id") or metadata_payload.get("objectId") or "")
            payload = self.artifact_storage.get_json(storage_key)

            if object_type == MaterialObjectType.DataFrame.value:
                dataframe = pd.DataFrame(payload)
                dataframes.append(dataframe)
                if object_id:
                    dataframe_resources[object_id] = dataframe
                if "formula" in dataframe.columns:
                    formulas.extend(str(value) for value in dataframe["formula"].dropna().tolist())
            elif object_type == MaterialObjectType.Structure.value:
                structures.append(payload)
                if object_id:
                    structure_resources[object_id] = payload
                if object_metadata.get("formula"):
                    formulas.append(str(object_metadata["formula"]))
            elif object_type == MaterialObjectType.Atoms.value and object_metadata.get("formula"):
                formulas.append(str(object_metadata["formula"]))

        object_store: dict[str, Any] = {}
        profiles = repos.data_profiles.list_for_dataset(dataset_id)
        current_profiles = [item for item in profiles if item.get("profileContractVersion") == "2.0"]
        if current_profiles:
            selected = sorted(
                current_profiles,
                key=lambda item: (str(item.get("version") or ""), str(item.get("profileId") or "")),
            )[-1]
            object_store["profile"] = DataProfile.model_validate(selected)
        object_store.update(dataframe_resources)
        object_store.update(structure_resources)
        if formulas:
            object_store["formulas"] = formulas
        if structures:
            object_store["structures"] = structures
            object_store["structure_resources"] = structure_resources
            object_store["viewer_structure"] = structures[0]
        if dataframes:
            object_store["ml_table"] = dataframes[0]
        return object_store or None

    def _repositories_from_factory(self) -> Any | None:
        if self.repository_factory is None:
            return None
        return self.repository_factory.create_repositories()


def _normalized_exports(dataset: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    metadata = dataset.get("metadata") or {}
    candidates = dataset.get("normalizedExports") or metadata.get("normalizedExports") or metadata.get("normalized_exports") or []
    return [export for export in candidates if isinstance(export, Mapping)]
