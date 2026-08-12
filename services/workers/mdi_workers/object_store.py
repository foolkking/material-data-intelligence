from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

import pandas as pd

from mdi_api.artifact_storage import ArtifactStorage
from mdi_api.unit_of_work import RepositoryFactory
from mdi_schemas import DataProfile, MaterialObjectType

from .source_resources import register_runtime_source_resource


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
        return self.resolve(dataset_id)

    def resolve(self, dataset_id: str, *, profile_id: str | None = None) -> Mapping[str, Any] | None:
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
        source_records: list[dict[str, Any]] = []
        project_id = str(dataset.get("projectId") or "")
        expected_scope = f"projects/{project_id}/datasets/{dataset_id}/normalized/"

        for export in exports:
            metadata_key = str(export.get("metadataKey") or export.get("metadata_key") or "")
            storage_key = str(export.get("storageKey") or export.get("storage_key") or "")
            if not metadata_key or not storage_key:
                continue
            if not project_id or not storage_key.startswith(expected_scope) or not metadata_key.startswith(expected_scope):
                raise ValueError("Normalized source resource is outside the persisted dataset scope.")

            try:
                metadata_bytes = self.artifact_storage.get_bytes(metadata_key)
            except Exception as exc:
                raise ValueError("Durable normalized source metadata is unavailable.") from exc
            metadata_payload = json.loads(metadata_bytes.decode("utf-8"))
            object_metadata = dict(metadata_payload.get("metadata") or {})
            object_type = str((metadata_payload.get("provenance") or {}).get("objectType") or object_metadata.get("objectType") or "")
            object_id = str(export.get("objectId") or export.get("object_id") or metadata_payload.get("objectId") or "")
            payload_hash = str(export.get("contentHash") or export.get("content_hash") or metadata_payload.get("contentHash") or "")
            object_hash = str(export.get("objectHash") or export.get("object_hash") or payload_hash)
            if not object_id or str(metadata_payload.get("objectId") or "") != object_id:
                raise ValueError("Normalized source resource identity mismatch.")
            if not payload_hash or str(metadata_payload.get("contentHash") or "") != payload_hash:
                raise ValueError(f"Normalized source metadata checksum mismatch for {object_id}.")
            try:
                payload_bytes = self.artifact_storage.get_bytes(storage_key)
            except Exception as exc:
                raise ValueError(f"Durable normalized source payload is unavailable for {object_id}.") from exc
            if hashlib.sha256(payload_bytes).hexdigest() != payload_hash:
                raise ValueError(f"Normalized source payload checksum mismatch for {object_id}.")
            payload = json.loads(payload_bytes.decode("utf-8"))

            if object_type == MaterialObjectType.DataFrame.value:
                dataframe = pd.DataFrame(payload)
                dataframes.append(dataframe)
                if object_id:
                    experimental_xrd = object_metadata.get("experimentalXrd")
                    source_records.append({"id": object_id, "type": object_type, "hash": object_hash, "value": _experimental_xrd_resource(dataframe, experimental_xrd) if isinstance(experimental_xrd, dict) else dataframe})
                if "formula" in dataframe.columns:
                    formulas.extend(str(value) for value in dataframe["formula"].dropna().tolist())
            elif object_type == MaterialObjectType.Structure.value:
                structures.append(payload)
                if object_id:
                    structure_resources[object_id] = payload
                    source_records.append({"id": object_id, "type": object_type, "hash": object_hash, "value": payload})
                if object_metadata.get("formula"):
                    formulas.append(str(object_metadata["formula"]))
            elif object_type == MaterialObjectType.Atoms.value and object_metadata.get("formula"):
                formulas.append(str(object_metadata["formula"]))
            elif object_id and object_type in {item.value for item in MaterialObjectType}:
                source_records.append({"id": object_id, "type": object_type, "hash": object_hash, "value": payload})

        object_store: dict[str, Any] = {}
        profiles = repos.data_profiles.list_for_dataset(dataset_id)
        eligible_profiles = (
            [
                item
                for item in profiles
                if str(item.get("profileId") or item.get("id") or "") == profile_id
            ]
            if profile_id is not None
            else [item for item in profiles if item.get("profileContractVersion") == "2.0"]
        )
        if profile_id is not None and not eligible_profiles:
            raise LookupError("Requested DataProfile is unavailable for this dataset.")
        if eligible_profiles:
            selected = sorted(
                eligible_profiles,
                key=lambda item: (str(item.get("version") or ""), str(item.get("profileId") or "")),
            )[-1]
            profile = DataProfile.model_validate(selected)
            register_runtime_source_resource(
                object_store, object_id="profile", object_type="DataProfile",
                object_hash=profile.semanticHash or profile.profileId,
                dataset_id=dataset_id, value=profile,
            )
        for source in source_records:
            aliases = (
                ("ml_table",)
                if source["type"] == MaterialObjectType.DataFrame.value
                and isinstance(source["value"], pd.DataFrame)
                and "ml_table" not in object_store
                else ()
            )
            register_runtime_source_resource(
                object_store, object_id=source["id"], object_type=source["type"],
                object_hash=source["hash"], dataset_id=dataset_id, value=source["value"], aliases=aliases,
            )
        if formulas:
            object_store["formulas"] = formulas
        if structures:
            object_store["structures"] = structures
            object_store["structure_resources"] = structure_resources
            object_store["viewer_structure"] = structures[0]
        if dataframes:
            object_store.setdefault("ml_table", dataframes[0])
        return object_store or None

    def _repositories_from_factory(self) -> Any | None:
        if self.repository_factory is None:
            return None
        return self.repository_factory.create_repositories()


def _normalized_exports(dataset: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    metadata = dataset.get("metadata") or {}
    candidates = dataset.get("normalizedExports") or metadata.get("normalizedExports") or metadata.get("normalized_exports") or []
    return [export for export in candidates if isinstance(export, Mapping)]


def _experimental_xrd_resource(dataframe: pd.DataFrame, metadata: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": metadata["schemaVersion"], "resourceId": metadata["resourceId"],
        "resourceVersion": metadata["resourceVersion"], "resourceHash": metadata["resourceHash"],
        "xAxis": metadata["xAxis"], "twoTheta": [float(item) for item in dataframe["two_theta"].tolist()],
        "intensity": [float(item) for item in dataframe["intensity"].tolist()],
        "intensitySemantic": metadata["intensitySemantic"], "wavelength": metadata["wavelength"],
    }
