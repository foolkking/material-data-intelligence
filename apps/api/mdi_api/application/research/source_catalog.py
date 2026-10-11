from __future__ import annotations

from typing import Any


SUPPORTED_RESEARCH_RESOURCES = {
    "DataFrame", "Structure", "Trajectory", "ElectronicBand", "ElectronicDos",
    "PhononBand", "PhononDos", "VolumetricData",
}


def research_source_catalog(dataset: dict[str, Any], profiles: list[dict[str, Any]]) -> dict[str, Any]:
    """List profiled source identities without hydrating scientific payloads."""
    dataset_id = str(dataset.get("datasetId") or dataset.get("id") or "")
    project_id = str(dataset.get("projectId") or "")
    metadata = dataset.get("metadata") or {}
    result: dict[str, Any] = {"projectId": project_id, "datasetId": dataset_id, "resources": []}
    if metadata.get("trashedAt") or dataset.get("status") not in {"profile_ready", "partially_ready"}:
        return result
    owned = [p for p in profiles if str(p.get("datasetId") or "") == dataset_id]
    if not owned:
        return result
    profile = max(owned, key=lambda p: str(p.get("createdAt") or p.get("profileId") or ""))
    exports = [x for x in metadata.get("normalizedExports", []) if isinstance(x, dict)]
    files = [x for x in metadata.get("files", []) if isinstance(x, dict)]
    objects = [x for x in profile.get("objects", []) if isinstance(x, dict)]
    for obj in objects:
        resource_id, resource_type = obj.get("objectId"), obj.get("objectType")
        matches = [x for x in exports if x.get("objectId") == resource_id]
        if resource_type not in SUPPORTED_RESEARCH_RESOURCES or not resource_id or len(matches) != 1:
            continue
        if sum(x.get("objectId") == resource_id for x in objects) != 1:
            continue
        export = matches[0]
        object_hash = str(obj.get("objectHash") or "")
        if len(object_hash) != 64 or object_hash != export.get("objectHash"):
            continue
        names: list[str] = []
        for file_id in obj.get("sourceFileIds") or []:
            sources = [f for f in files if f.get("fileId") == file_id]
            if len(sources) == 1:
                name = str(sources[0].get("name") or sources[0].get("fileName") or "")
                # A display label never exposes a local path from import metadata.
                name = name.replace("\\", "/").rsplit("/", 1)[-1]
                if name and name not in names:
                    names.append(name)
        result["resources"].append({
            "objectId": resource_id, "objectType": resource_type,
            "objectHash": object_hash, "datasetId": dataset_id,
            "displayName": " + ".join(names) or str(dataset.get("name") or resource_id),
        })
    return result
