from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping
from uuid import UUID

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
            elif object_type == MaterialObjectType.Atoms.value:
                if object_id:
                    source_records.append({"id": object_id, "type": object_type, "hash": object_hash, "value": payload})
                if object_metadata.get("formula"):
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

    def hydrate_agent2_sources(
        self,
        object_store: Mapping[str, Any],
        *,
        job: Mapping[str, Any],
        plan_payload: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """Hydrate exact ScientificObjectVersion refs used by Agent 2.0 plans.

        The persisted version id is the execution identity. This method never
        follows ``ScientificObject.current_version_id`` and never aliases a
        missing historical version to a newer payload.
        """
        version_refs = _agent2_version_refs(plan_payload)
        if not version_refs:
            return object_store
        if self.repository_factory is None:
            raise ValueError("Exact ScientificObjectVersion hydration requires RepositoryFactory.")

        project_id = str(job.get("projectId") or job.get("project_id") or "")
        dataset_id = str(job.get("datasetId") or job.get("dataset_id") or "")
        if not project_id or not dataset_id:
            raise ValueError("Agent 2.0 execution requires persisted project and dataset scope.")

        records: list[tuple[str, str, dict[str, Any], dict[str, Any]]] = []
        with self.repository_factory.session() as session:
            for version_id, executable_type in version_refs:
                version = session.agent2.scientific_objects.get_version(UUID(version_id))
                logical = session.agent2.scientific_objects.get_object(version["scientific_object_id"])
                if str(logical["project_id"]) != project_id:
                    raise ValueError("ScientificObjectVersion belongs to another Project.")
                if str(version["scientific_object_id"]) != str(logical["id"]):
                    raise ValueError("ScientificObjectVersion identity is inconsistent.")
                if str(version.get("availability_status")) not in {"AVAILABLE", "PARTIALLY_AVAILABLE"}:
                    raise ValueError("Exact ScientificObjectVersion is unavailable.")
                records.append((version_id, executable_type, dict(logical), dict(version)))

        hydrated = dict(object_store)
        for version_id, executable_type, _logical, version in records:
            storage_ref = dict(version.get("normalized_payload_ref_json") or {})
            storage_key = str(storage_ref.get("object_key") or "")
            expected_checksum = _sha256_identity(
                storage_ref.get("checksum"),
                version.get("content_hash"),
            )
            if not storage_key or expected_checksum is None:
                raise ValueError("Exact ScientificObjectVersion payload lacks a verifiable SHA-256 identity.")
            max_bytes = int(storage_ref.get("byte_size") or 268_435_456)
            if max_bytes < 0 or max_bytes > 268_435_456:
                raise ValueError("Exact ScientificObjectVersion payload size is outside the execution limit.")
            bounded_reader = getattr(self.artifact_storage, "get_bytes_bounded", None)
            try:
                payload_bytes = (
                    bounded_reader(storage_key, max_bytes=max_bytes)
                    if callable(bounded_reader)
                    else self.artifact_storage.get_bytes(storage_key)
                )
            except Exception as exc:
                raise ValueError("Exact ScientificObjectVersion payload is unavailable.") from exc
            if len(payload_bytes) > max_bytes or hashlib.sha256(payload_bytes).hexdigest() != expected_checksum:
                raise ValueError("Exact ScientificObjectVersion payload checksum mismatch.")
            try:
                payload = json.loads(payload_bytes.decode("utf-8"))
            except Exception as exc:
                raise ValueError("Exact ScientificObjectVersion payload is not strict JSON.") from exc
            value = _materialize_agent2_payload(
                payload,
                executable_type=executable_type,
                canonical_metadata=version.get("canonical_metadata_json") or {},
            )
            canonical_resource_id = str((version.get("canonical_metadata_json") or {}).get("source_resource_id") or "")
            aliases = (canonical_resource_id,) if canonical_resource_id and canonical_resource_id != version_id else ()
            register_runtime_source_resource(
                hydrated,
                object_id=version_id,
                object_type=executable_type,
                object_hash=expected_checksum,
                dataset_id=dataset_id,
                value=value,
                aliases=aliases,
            )
        return hydrated

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
        "xAxis": {
            "kind": metadata["xAxis"]["kind"],
            "unit": metadata["xAxis"]["unit"],
            "values": [float(item) for item in dataframe["two_theta"].tolist()],
        },
        "intensity": {
            "semantic": metadata["intensitySemantic"],
            "values": [float(item) for item in dataframe["intensity"].tolist()],
        },
        "wavelength": metadata["wavelength"],
    }


def _agent2_version_refs(plan_payload: Mapping[str, Any]) -> list[tuple[str, str]]:
    refs: dict[str, str] = {}
    for step in plan_payload.get("steps") or []:
        for input_ref in step.get("inputRefs") or []:
            if input_ref.get("refType") != "normalized_object":
                continue
            value = str(input_ref.get("ref") or "")
            try:
                UUID(value)
            except (TypeError, ValueError):
                continue
            object_type = str(input_ref.get("objectType") or "")
            if not object_type:
                raise ValueError("Exact ScientificObjectVersion binding is missing objectType.")
            existing = refs.get(value)
            if existing is not None and existing != object_type:
                raise ValueError("Exact ScientificObjectVersion is bound with conflicting execution types.")
            refs[value] = object_type
    return sorted(refs.items())


def _sha256_identity(*values: Any) -> str | None:
    for value in values:
        candidate = str(value or "").lower()
        if len(candidate) == 64 and all(character in "0123456789abcdef" for character in candidate):
            return candidate
    return None


def _materialize_agent2_payload(
    payload: Any,
    *,
    executable_type: str,
    canonical_metadata: Mapping[str, Any],
) -> Any:
    if executable_type == MaterialObjectType.DataFrame.value:
        dataframe = pd.DataFrame(payload)
        experimental_xrd = canonical_metadata.get("experimentalXrd")
        return (
            _experimental_xrd_resource(dataframe, experimental_xrd)
            if isinstance(experimental_xrd, Mapping)
            else dataframe
        )
    return payload
