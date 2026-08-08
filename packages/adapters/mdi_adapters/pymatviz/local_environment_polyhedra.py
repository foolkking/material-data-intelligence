from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

import numpy as np
from pymatgen.core import Structure
from scipy.spatial import ConvexHull, QhullError

from mdi_artifact_core import ArtifactPayload, content_hash, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType

from ..context import ToolExecutionContext, hashable_material
from ..errors import ToolExecutionError
from ..platform_builtin.structure import _BaseStructureAdapter


TOOL_ID = "structure.local_environment_polyhedra"
TOOL_VERSION = "0.1.0"
ARTIFACT_SCHEMA = "phase10n2.local_environment_polyhedra.v1"
CATALOG_ID = "mdi.local_geometry_reference_catalog"
CATALOG_VERSION = "1.0.0"
CLASSIFICATION_ALGORITHM = "mdi.angular_spectrum_reference_match@1.0.0"
FACE_ALGORITHM = "scipy.spatial.ConvexHull@1.17.1"
N1_CONTRACTS = {
    "phase10n1.crystalnn_coordination.v1": ("structure.coordination_crystalnn", "pymatgen.crystalnn"),
    "phase10n1.voronoinn_coordination.v1": ("structure.coordination_voronoinn", "pymatgen.voronoinn"),
}
DISTANCE_TOLERANCE_ANGSTROM = 1e-6


def _unit(values: tuple[float, float, float]) -> tuple[float, float, float]:
    length = math.sqrt(sum(value * value for value in values))
    return tuple(value / length for value in values)


def _ring(count: int) -> tuple[tuple[float, float, float], ...]:
    return tuple((math.cos(2 * math.pi * index / count), math.sin(2 * math.pi * index / count), 0.0) for index in range(count))


GEOMETRY_REFERENCE_CATALOG: dict[str, tuple[tuple[float, float, float], ...]] = {
    "linear": ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)),
    "trigonal_planar": _ring(3),
    "tetrahedral": tuple(_unit(item) for item in ((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1))),
    "square_planar": ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0), (0.0, -1.0, 0.0)),
    "trigonal_bipyramidal": (*_ring(3), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)),
    "square_pyramidal": ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0)),
    "octahedral": ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)),
    "pentagonal_bipyramidal": (*_ring(5), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)),
    "cubic": tuple(_unit((x, y, z)) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)),
}


@dataclass(frozen=True)
class PreparedLocalEnvironment:
    structure: Structure
    structure_id: str
    structure_hash: str
    source_resource_id: str
    source_resource_hash: str
    coordination: dict[str, Any]
    binding: dict[str, Any]


@dataclass(frozen=True)
class LocalEnvironmentResult:
    payload: dict[str, Any]
    summary: str
    recipe: dict[str, Any]


class LocalEnvironmentPolyhedraAdapter(_BaseStructureAdapter):
    tool_id = TOOL_ID
    adapter_version = TOOL_VERSION

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedLocalEnvironment:
        normalized = self.normalize_params(params)
        structure_value: Any | None = None
        coordination: dict[str, Any] | None = None
        coordination_ref = ""
        for input_ref, resolved in zip(input_refs, self._resolved_inputs, strict=True):
            if isinstance(resolved, Mapping) and str(resolved.get("schema_version") or "") in N1_CONTRACTS:
                if coordination is not None:
                    raise _error("TOOL_INPUT_INVALID", "MISSING_COORDINATION_ARTIFACT", "N2 accepts exactly one N1 coordination Artifact.")
                coordination = dict(resolved)
                coordination_ref = _ref(input_ref)
            elif structure_value is None:
                structure_value = resolved
            else:
                raise _error("TOOL_INPUT_INVALID", "N2_PARAMETER_INVALID", "N2 accepts one Structure and one N1 coordination Artifact.")
        if structure_value is None or coordination is None:
            raise _error("TOOL_INPUT_INVALID", "MISSING_COORDINATION_ARTIFACT", "N2 requires one exact Structure and one exact N1 coordination Artifact.")

        structures = self._coerce_structures(structure_value)
        if len(structures) != 1:
            raise _error("TOOL_INPUT_INVALID", "COORDINATION_STRUCTURE_MISMATCH", "N2 requires exactly one Structure.")
        structure_id, structure = next(iter(sorted(structures.items())))
        self._validate_structure(structure_id, structure, max_atoms=normalized["max_evaluated_sites"])
        structure_hash = content_hash(stable_json_dumps(hashable_material(structure)))
        binding = dict(context.artifact_bindings.get(coordination_ref) or {})
        if not binding:
            raise _error("TOOL_INPUT_INVALID", "MISSING_COORDINATION_ARTIFACT", "Exact persisted Artifact binding metadata is unavailable.")
        _validate_source_coordination(coordination, binding, structure_hash)
        scope = coordination["scope"]
        return PreparedLocalEnvironment(
            structure=structure,
            structure_id=structure_id,
            structure_hash=structure_hash,
            source_resource_id=str(scope["sourceResourceId"]),
            source_resource_hash=str(scope["sourceResourceHash"]),
            coordination=coordination,
            binding=binding,
        )

    def run(self, prepared: PreparedLocalEnvironment, params: dict[str, Any]) -> LocalEnvironmentResult:
        normalized = self.normalize_params(params)
        parameter_hash = content_hash(stable_json_dumps(normalized))
        selected = normalized["site_indices"] or [int(item["siteIndex"]) for item in prepared.coordination["siteResults"]]
        selected = sorted(set(selected))
        if len(selected) > normalized["max_evaluated_sites"]:
            raise _error("TOOL_RESOURCE_LIMIT", "N2_SITE_LIMIT_EXCEEDED", "Selected sites exceed max_evaluated_sites.")
        by_index = {int(item["siteIndex"]): item for item in prepared.coordination["siteResults"]}
        site_results: list[dict[str, Any]] = []
        unavailable: list[dict[str, Any]] = []
        for site_index in selected:
            source_site = by_index.get(site_index)
            if source_site is None:
                unavailable.append({"siteIndex": site_index, "reason": "COORDINATION_SITE_IDENTITY_INVALID"})
                continue
            try:
                site_results.append(self._analyze_site(prepared, source_site, normalized, parameter_hash))
            except ToolExecutionError as exc:
                unavailable.append({"siteIndex": site_index, "siteId": source_site.get("siteId"), "reason": str((exc.details or {}).get("errorType") or exc.code)})

        classified = sum(item["classification"]["status"] == "CLASSIFIED" for item in site_results)
        ambiguous = sum(item["classification"]["status"] == "AMBIGUOUS" for item in site_results)
        unclassified = sum(item["classification"]["status"] in {"UNCLASSIFIED", "UNSUPPORTED"} for item in site_results)
        total = len(selected)
        status = "COMPLETE" if not unavailable else ("PARTIAL" if site_results else "FAILED")
        source = _source_identity(prepared.coordination, prepared.binding)
        payload = {
            "artifactType": TOOL_ID,
            "schema_version": ARTIFACT_SCHEMA,
            "tool": {"toolId": TOOL_ID, "toolVersion": self.context.tool_version, "adapterVersion": self.adapter_version},
            "algorithm": {"classification": CLASSIFICATION_ALGORITHM, "faceConstruction": FACE_ALGORITHM},
            "referenceCatalog": {"catalogId": CATALOG_ID, "catalogVersion": CATALOG_VERSION, "geometryIds": sorted(GEOMETRY_REFERENCE_CATALOG)},
            "resolvedParameters": normalized,
            "parameterHash": parameter_hash,
            "scope": {
                "projectId": self.context.project_id,
                "datasetId": self.context.dataset_id,
                "jobId": self.context.job_id,
                "planId": self.context.plan_id,
                "planVersion": self.context.plan_version,
                "toolCallId": self.context.tool_call_id,
                "sourceResourceId": prepared.source_resource_id,
                "sourceResourceHash": prepared.source_resource_hash,
                "structureHash": prepared.structure_hash,
            },
            "sourceCoordination": source,
            "siteResults": sorted(site_results, key=lambda item: item["siteIndex"]),
            "coverage": {
                "status": status,
                "requestedSites": total,
                "evaluatedSites": len(site_results),
                "unavailableSites": len(unavailable),
                "classifiedSites": classified,
                "ambiguousSites": ambiguous,
                "unclassifiedSites": unclassified,
                "ratio": _round(len(site_results) / total) if total else 0.0,
                "unavailable": unavailable,
            },
            "warnings": sorted({warning for item in site_results for warning in item["warnings"]}),
            "runtimeDiagnostics": {
                "n1NeighborRecomputation": False,
                "independentNeighborSearch": False,
                "coordinationAlgorithmFallback": False,
                "resultSubstitution": False,
                "boundedPairwiseMatching": True,
            },
            "provenance": {
                "authority": "registered_backend_adapter",
                "sourceArtifactId": source["artifactId"],
                "sourceArtifactChecksum": source["artifactChecksum"],
                "sourceParameterHash": source["parameterHash"],
                "resolvedParameterHash": parameter_hash,
                "comparisonAuthority": "deterministic_consumer_presentation_only",
            },
            "limits": {
                "maxEvaluatedSites": normalized["max_evaluated_sites"],
                "maxNeighborsPerSite": normalized["max_neighbors_per_site"],
                "maxGeometryReferencesPerSite": normalized["max_geometry_references_per_site"],
                "maxPolyhedronVertices": normalized["max_polyhedron_vertices"],
                "maxFaces": normalized["max_faces"],
                "maxOutputBytes": normalized["max_output_bytes"],
                "timeoutSeconds": 180,
            },
            "security": {"containsJavascript": False, "containsHtml": False, "externalUrls": [], "arbitraryCodeExecution": False},
        }
        encoded = stable_json_dumps(payload).encode("utf-8")
        if len(encoded) > normalized["max_output_bytes"]:
            raise _error("TOOL_RESOURCE_LIMIT", "N2_ARTIFACT_TOO_LARGE", "N2 Artifact exceeds max_output_bytes.")
        return LocalEnvironmentResult(payload, _summary(payload), _recipe(self, payload))

    def _analyze_site(
        self,
        prepared: PreparedLocalEnvironment,
        source_site: Mapping[str, Any],
        params: dict[str, Any],
        parameter_hash: str,
    ) -> dict[str, Any]:
        site_index = int(source_site["siteIndex"])
        site_id = str(source_site["siteId"])
        expected_site_id = f"site:{prepared.structure_hash}:{site_index}"
        if site_id != expected_site_id or str(source_site.get("structureHash")) != prepared.structure_hash:
            raise _error("TOOL_INPUT_INVALID", "COORDINATION_SITE_IDENTITY_INVALID", "N1 site identity does not match the exact Structure.")
        neighbors = list(source_site.get("neighbors") or [])
        if len(neighbors) > min(params["max_neighbors_per_site"], params["max_polyhedron_vertices"]):
            raise _error("TOOL_RESOURCE_LIMIT", "N2_SITE_LIMIT_EXCEEDED", "N1 neighbor count exceeds the N2 per-site cap.")
        vertices = [_vertex(prepared.structure, prepared.structure_hash, site_index, item) for item in neighbors]
        vertices.sort(key=lambda item: item["neighborIdentity"])
        vectors = np.asarray([item["relativeCartesian"] for item in vertices], dtype=float)
        references = params["geometry_reference_ids"] or sorted(GEOMETRY_REFERENCE_CATALOG)
        candidates = _classify(vectors, references, params)
        classification = _classification(candidates, params)
        faces, face_status, face_reason, volume, area = _faces(vertices, vectors, params)
        metrics = _metrics(vectors, candidates[0] if candidates else None, volume, area)
        relation_ids = [item["neighborIdentity"] for item in vertices]
        source = _source_identity(prepared.coordination, prepared.binding)
        identity_fields = {
            "sourceArtifactId": source["artifactId"],
            "sourceArtifactChecksum": source["artifactChecksum"],
            "structureHash": prepared.structure_hash,
            "siteId": site_id,
            "sourceAlgorithmId": source["algorithmId"],
            "geometryReferenceId": classification.get("referenceGeometryId"),
            "geometryReferenceVersion": classification.get("referenceGeometryVersion"),
            "parameterHash": parameter_hash,
        }
        environment_identity = f"environment:{content_hash(stable_json_dumps(identity_fields))}"
        polyhedron_identity = f"polyhedron:{content_hash(stable_json_dumps({**identity_fields, 'neighborRelationIdentities': relation_ids, 'contract': ARTIFACT_SCHEMA}))}"
        warnings: list[str] = []
        if classification["status"] == "AMBIGUOUS":
            warnings.append("LOCAL_ENVIRONMENT_AMBIGUOUS")
        elif classification["status"] in {"UNCLASSIFIED", "UNSUPPORTED"}:
            warnings.append("LOCAL_ENVIRONMENT_UNCLASSIFIED")
        if face_status == "UNAVAILABLE" and face_reason:
            warnings.append(face_reason)
        return {
            "environmentIdentity": environment_identity,
            "polyhedronIdentity": polyhedron_identity,
            "structureHash": prepared.structure_hash,
            "siteId": site_id,
            "siteIndex": site_index,
            "sourceCoordinationSemantics": str(source_site["coordinationSemantics"]),
            "sourceCoordinationValue": _round(float(source_site["coordinationValue"])),
            "neighborRelationIdentities": relation_ids,
            "classification": classification,
            "polyhedron": {"status": face_status, "vertices": vertices, "faces": faces, "unavailableReason": face_reason},
            "distortionMetrics": metrics,
            "warnings": sorted(warnings),
        }

    def normalize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        allowed = {
            "site_indices", "geometry_reference_ids", "classification_max_distance",
            "classification_tie_tolerance", "include_faces", "max_evaluated_sites",
            "max_neighbors_per_site", "max_geometry_references_per_site",
            "max_polyhedron_vertices", "max_faces", "max_output_bytes",
        }
        unknown = sorted(set(params) - allowed)
        if unknown:
            raise _error("TOOL_PARAM_INVALID", "N2_PARAMETER_INVALID", "Unknown N2 parameters were rejected.", parameters=unknown)
        site_indices = _unique_ints(params.get("site_indices", []), "site_indices", 0, 4999, 5000)
        references = params.get("geometry_reference_ids", [])
        if not isinstance(references, list) or len(references) > len(GEOMETRY_REFERENCE_CATALOG) or len(references) != len(set(references)) or any(item not in GEOMETRY_REFERENCE_CATALOG for item in references):
            raise _error("TOOL_PARAM_INVALID", "N2_PARAMETER_INVALID", "geometry_reference_ids must be a unique bounded catalog subset.")
        result = {
            "site_indices": site_indices,
            "geometry_reference_ids": sorted(references),
            "classification_max_distance": _number(params, "classification_max_distance", 0.35, 0.0, 2.0),
            "classification_tie_tolerance": _number(params, "classification_tie_tolerance", 0.01, 0.0, 0.25),
            "include_faces": _boolean(params, "include_faces", True),
            "max_evaluated_sites": _integer(params, "max_evaluated_sites", 5000, 1, 5000),
            "max_neighbors_per_site": _integer(params, "max_neighbors_per_site", 64, 1, 64),
            "max_geometry_references_per_site": _integer(params, "max_geometry_references_per_site", 32, 1, 32),
            "max_polyhedron_vertices": _integer(params, "max_polyhedron_vertices", 64, 1, 64),
            "max_faces": _integer(params, "max_faces", 128, 1, 128),
            "max_output_bytes": _integer(params, "max_output_bytes", 16 * 1024 * 1024, 1024, 16 * 1024 * 1024),
        }
        if len(result["geometry_reference_ids"]) > result["max_geometry_references_per_site"]:
            raise _error("TOOL_PARAM_INVALID", "N2_PARAMETER_INVALID", "Selected geometry references exceed max_geometry_references_per_site.")
        return result

    def export(self, result: LocalEnvironmentResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        requested = set(artifact_types) or {ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json}
        payloads: list[ArtifactPayload] = []
        if ArtifactType.table_json in requested:
            payloads.append(ArtifactPayload(artifact_type=ArtifactType.table_json, file_name="local_environment_polyhedra.json", content=stable_json_dumps(result.payload), media_type="application/json"))
        if ArtifactType.summary_md in requested:
            payloads.append(ArtifactPayload(artifact_type=ArtifactType.summary_md, file_name="summary.md", content=result.summary, media_type="text/markdown"))
        if ArtifactType.recipe_json in requested:
            payloads.append(ArtifactPayload(artifact_type=ArtifactType.recipe_json, file_name="recipe.json", content=stable_json_dumps(result.recipe), media_type="application/json"))
        source = result.payload["sourceCoordination"]
        return self.export_payloads(payloads, provenance={
            "artifactType": TOOL_ID,
            "schemaVersion": ARTIFACT_SCHEMA,
            "sourceArtifactId": source["artifactId"],
            "sourceArtifactChecksum": source["artifactChecksum"],
            "sourceToolId": source["toolId"],
            "sourceAlgorithmId": source["algorithmId"],
            "parameterHash": result.payload["parameterHash"],
            "scientificAuthority": "registered_backend_adapter",
        })


def _validate_source_coordination(payload: Mapping[str, Any], binding: Mapping[str, Any], structure_hash: str) -> None:
    contract = str(payload.get("schema_version") or "")
    expected = N1_CONTRACTS.get(contract)
    if expected is None or str(binding.get("artifactContractVersion") or "") != contract:
        raise _error("TOOL_INPUT_INVALID", "UNSUPPORTED_COORDINATION_CONTRACT", "N1 coordination contract is unsupported.")
    tool = payload.get("tool") or {}
    algorithm = payload.get("algorithm") or {}
    if str(tool.get("toolId")) != expected[0] or str(tool.get("toolVersion")) != TOOL_VERSION or str(algorithm.get("algorithmId")) != expected[1]:
        raise _error("TOOL_INPUT_INVALID", "UNSUPPORTED_COORDINATION_CONTRACT", "N1 producer identity does not match its contract.")
    if str(binding.get("checksum") or "") == "" or str(binding.get("artifactId") or "") == "":
        raise _error("TOOL_INPUT_INVALID", "COORDINATION_ARTIFACT_CHECKSUM_MISMATCH", "N1 Artifact identity/checksum is missing.")
    structures = list(payload.get("structures") or [])
    if len(structures) != 1 or str(structures[0].get("structureHash") or "") != structure_hash:
        raise _error("TOOL_INPUT_INVALID", "COORDINATION_STRUCTURE_MISMATCH", "N1 Artifact structure hash does not match the bound Structure.")
    if any(str(item.get("structureHash") or "") != structure_hash for item in payload.get("siteResults") or []):
        raise _error("TOOL_INPUT_INVALID", "COORDINATION_STRUCTURE_MISMATCH", "N1 site result is bound to another Structure.")


def _source_identity(payload: Mapping[str, Any], binding: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifactId": str(binding["artifactId"]),
        "artifactChecksum": str(binding["checksum"]),
        "contractVersion": str(binding["artifactContractVersion"]),
        "toolId": str(payload["tool"]["toolId"]),
        "toolVersion": str(payload["tool"]["toolVersion"]),
        "algorithmId": str(payload["algorithm"]["algorithmId"]),
        "algorithmVersion": str(payload["algorithm"]["algorithmVersion"]),
        "parameterHash": str(payload["parameterHash"]),
    }


def _vertex(structure: Structure, structure_hash: str, center_index: int, neighbor: Mapping[str, Any]) -> dict[str, Any]:
    neighbor_index = int(neighbor.get("neighborSiteIndex", -1))
    if not 0 <= neighbor_index < len(structure):
        raise _error("TOOL_INPUT_INVALID", "COORDINATION_SITE_IDENTITY_INVALID", "N1 neighbor site index is invalid.")
    image = neighbor.get("periodicImage")
    if not isinstance(image, list) or len(image) != 3 or any(isinstance(item, bool) or not isinstance(item, int) for item in image):
        raise _error("TOOL_INPUT_INVALID", "COORDINATION_SITE_IDENTITY_INVALID", "N1 periodic image is invalid.")
    expected_site = f"site:{structure_hash}:{neighbor_index}"
    if str(neighbor.get("neighborSiteId")) != expected_site:
        raise _error("TOOL_INPUT_INVALID", "COORDINATION_SITE_IDENTITY_INVALID", "N1 neighbor site identity is invalid.")
    delta_fractional = np.asarray(structure[neighbor_index].frac_coords, dtype=float) + np.asarray(image, dtype=float) - np.asarray(structure[center_index].frac_coords, dtype=float)
    vector = np.asarray(structure.lattice.get_cartesian_coords(delta_fractional), dtype=float)
    if vector.shape != (3,) or not np.isfinite(vector).all():
        raise _error("TOOL_INPUT_INVALID", "NON_FINITE_GEOMETRY", "N1 neighbor geometry is non-finite.")
    distance = float(np.linalg.norm(vector))
    source_distance = float(neighbor.get("distance", math.nan))
    if not math.isfinite(source_distance) or abs(distance - source_distance) > DISTANCE_TOLERANCE_ANGSTROM:
        raise _error("TOOL_INPUT_INVALID", "COORDINATION_STRUCTURE_MISMATCH", "N1 neighbor distance does not match the exact Structure and periodic image.")
    identity = str(neighbor.get("neighborIdentity") or "")
    if not identity:
        raise _error("TOOL_INPUT_INVALID", "COORDINATION_SITE_IDENTITY_INVALID", "N1 neighbor relation identity is missing.")
    return {
        "vertexIdentity": f"vertex:{identity}",
        "neighborIdentity": identity,
        "neighborSiteId": expected_site,
        "periodicImage": image,
        "relativeCartesian": [_round(value) for value in vector],
        "distance": _round(distance),
        "distanceUnit": "angstrom",
    }


def _spectrum(vectors: np.ndarray) -> list[float]:
    if len(vectors) < 2:
        return []
    norms = np.linalg.norm(vectors, axis=1)
    if not np.isfinite(norms).all() or np.any(norms <= 0):
        raise _error("TOOL_INPUT_INVALID", "NON_FINITE_GEOMETRY", "Neighbor vectors must be finite and non-zero.")
    unit = vectors / norms[:, None]
    values = [float(np.clip(np.dot(unit[left], unit[right]), -1.0, 1.0)) for left in range(len(unit)) for right in range(left + 1, len(unit))]
    return sorted(values)


def _classify(vectors: np.ndarray, reference_ids: list[str], params: Mapping[str, Any]) -> list[dict[str, Any]]:
    observed = _spectrum(vectors)
    candidates: list[dict[str, Any]] = []
    for reference_id in reference_ids[: int(params["max_geometry_references_per_site"])]:
        reference = GEOMETRY_REFERENCE_CATALOG[reference_id]
        if len(reference) != len(vectors):
            continue
        expected = _spectrum(np.asarray(reference, dtype=float))
        distance = math.sqrt(sum((left - right) ** 2 for left, right in zip(observed, expected, strict=True)) / max(1, len(observed)))
        angle_rms = math.sqrt(sum((math.degrees(math.acos(left)) - math.degrees(math.acos(right))) ** 2 for left, right in zip(observed, expected, strict=True)) / max(1, len(observed)))
        candidates.append({
            "referenceGeometryId": reference_id,
            "referenceGeometryVersion": "1.0.0",
            "geometryDistanceRms": _round(distance),
            "geometryScore": _round(max(0.0, 1.0 - distance / 2.0)),
            "angularRmsDeviation": _round(angle_rms),
            "angularRmsDeviationUnit": "degree",
        })
    return sorted(candidates, key=lambda item: (item["geometryDistanceRms"], item["referenceGeometryId"]))


def _classification(candidates: list[dict[str, Any]], params: Mapping[str, Any]) -> dict[str, Any]:
    if not candidates:
        return {"status": "UNSUPPORTED", "referenceGeometryId": None, "referenceGeometryVersion": None, "geometryDistanceRms": None, "geometryScore": None, "alternatives": []}
    best = candidates[0]
    if best["geometryDistanceRms"] > params["classification_max_distance"]:
        status = "UNCLASSIFIED"
    elif len(candidates) > 1 and candidates[1]["geometryDistanceRms"] - best["geometryDistanceRms"] <= params["classification_tie_tolerance"]:
        status = "AMBIGUOUS"
    else:
        status = "CLASSIFIED"
    return {"status": status, **best, "alternatives": candidates[1:8], "tieTolerance": params["classification_tie_tolerance"], "maximumDistance": params["classification_max_distance"]}


def _faces(vertices: list[dict[str, Any]], vectors: np.ndarray, params: Mapping[str, Any]) -> tuple[list[dict[str, Any]], str, str | None, float | None, float | None]:
    if not params["include_faces"]:
        return [], "UNAVAILABLE", "POLYHEDRON_FACES_DISABLED", None, None
    if len(vertices) < 4:
        return [], "UNAVAILABLE", "INSUFFICIENT_POLYHEDRON_VERTICES", None, None
    if len(vertices) > params["max_polyhedron_vertices"]:
        raise _error("TOOL_RESOURCE_LIMIT", "N2_SITE_LIMIT_EXCEEDED", "Polyhedron vertex cap exceeded.")
    centered = vectors - vectors.mean(axis=0)
    if np.linalg.matrix_rank(centered, tol=1e-10) < 3:
        return [], "UNAVAILABLE", "COPLANAR_POLYHEDRON", None, None
    if any(float(np.linalg.norm(vectors[left] - vectors[right])) <= 1e-10 for left in range(len(vectors)) for right in range(left + 1, len(vectors))):
        return [], "UNAVAILABLE", "DEGENERATE_POLYHEDRON", None, None
    try:
        hull = ConvexHull(vectors)
    except QhullError:
        return [], "UNAVAILABLE", "POLYHEDRON_FACE_CONSTRUCTION_FAILED", None, None
    faces: list[dict[str, Any]] = []
    for simplex in hull.simplices:
        identities = sorted(vertices[int(index)]["vertexIdentity"] for index in simplex)
        faces.append(
            {
                "faceIdentity": "face:" + content_hash(stable_json_dumps(identities)),
                "vertexIdentities": identities,
            }
        )
    faces.sort(key=lambda item: item["faceIdentity"])
    if len(faces) > params["max_faces"]:
        raise _error("TOOL_RESOURCE_LIMIT", "N2_SITE_LIMIT_EXCEEDED", "Polyhedron face cap exceeded.")
    return faces, "AVAILABLE", None, _round(float(hull.volume)), _round(float(hull.area))


def _metrics(vectors: np.ndarray, best: Mapping[str, Any] | None, volume: float | None, area: float | None) -> dict[str, Any]:
    distances = np.linalg.norm(vectors, axis=1) if len(vectors) else np.asarray([], dtype=float)
    mean = float(np.mean(distances)) if len(distances) else 0.0
    spread = float(np.std(distances)) if len(distances) else 0.0
    distortion = float(np.mean(np.abs(distances - mean)) / mean) if mean > 0 else 0.0
    return {
        "radialDistanceMean": _round(mean),
        "radialDistanceSpread": _round(spread),
        "radialDistanceUnit": "angstrom",
        "bondLengthDistortionIndex": _round(distortion),
        "angularRmsDeviation": best.get("angularRmsDeviation") if best else None,
        "angularRmsDeviationUnit": "degree",
        "geometryDistanceRms": best.get("geometryDistanceRms") if best else None,
        "geometryScore": best.get("geometryScore") if best else None,
        "polyhedronVolume": volume,
        "polyhedronVolumeUnit": "angstrom^3",
        "polyhedronSurfaceArea": area,
        "polyhedronSurfaceAreaUnit": "angstrom^2",
    }


def _recipe(adapter: LocalEnvironmentPolyhedraAdapter, payload: Mapping[str, Any]) -> dict[str, Any]:
    source = payload["sourceCoordination"]
    return {
        "schemaVersion": "0.1",
        "recipeId": f"recipe_{adapter.context.tool_call_id}",
        "name": "Geometry-derived local environment and coordination polyhedra",
        "version": "1",
        "projectId": adapter.context.project_id,
        "sourceJobId": adapter.context.job_id,
        "executionAuthority": "NONE",
        "dependencyBindings": [{"sourceArtifactId": source["artifactId"], "sourceArtifactChecksum": source["artifactChecksum"], "sourceContractVersion": source["contractVersion"]}],
        "steps": [{"stepId": "step_from_adapter", "toolId": TOOL_ID, "toolVersion": TOOL_VERSION, "params": payload["resolvedParameters"], "parameterHash": payload["parameterHash"], "artifactContract": ARTIFACT_SCHEMA}],
    }


def _summary(payload: Mapping[str, Any]) -> str:
    coverage = payload["coverage"]
    source = payload["sourceCoordination"]
    return "\n".join([
        "# Geometry-derived local environment and coordination polyhedra",
        "",
        f"- Source coordination: `{source['toolId']}@{source['toolVersion']}`",
        f"- Source Artifact: `{source['artifactId']}` / `{source['artifactChecksum']}`",
        f"- Evaluated sites: {coverage['evaluatedSites']}/{coverage['requestedSites']} ({coverage['status']})",
        f"- Classified / ambiguous / unclassified: {coverage['classifiedSites']} / {coverage['ambiguousSites']} / {coverage['unclassifiedSites']}",
        "- Interpretation boundary: geometry-derived and source-algorithm-dependent; not definitive bonding chemistry.",
        "",
    ])


def _ref(value: Any) -> str:
    return str(getattr(value, "ref", value.get("ref", "") if isinstance(value, dict) else ""))


def _unique_ints(value: Any, name: str, minimum: int, maximum: int, maximum_items: int) -> list[int]:
    if not isinstance(value, list) or len(value) > maximum_items or len(value) != len(set(value)) or any(isinstance(item, bool) or not isinstance(item, int) or not minimum <= item <= maximum for item in value):
        raise _error("TOOL_PARAM_INVALID", "N2_PARAMETER_INVALID", f"{name} must be a unique bounded integer array.")
    return sorted(value)


def _number(params: Mapping[str, Any], name: str, default: float, minimum: float, maximum: float) -> float:
    value = params.get(name, default)
    if isinstance(value, bool):
        raise _error("TOOL_PARAM_INVALID", "N2_PARAMETER_INVALID", f"{name} must be a finite number.")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise _error("TOOL_PARAM_INVALID", "N2_PARAMETER_INVALID", f"{name} must be a finite number.") from exc
    if not math.isfinite(number) or not minimum <= number <= maximum:
        raise _error("TOOL_PARAM_INVALID", "N2_PARAMETER_INVALID", f"{name} is outside its bounded range.")
    return number


def _integer(params: Mapping[str, Any], name: str, default: int, minimum: int, maximum: int) -> int:
    value = params.get(name, default)
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise _error("TOOL_PARAM_INVALID", "N2_PARAMETER_INVALID", f"{name} must be a bounded integer.")
    return value


def _boolean(params: Mapping[str, Any], name: str, default: bool) -> bool:
    value = params.get(name, default)
    if not isinstance(value, bool):
        raise _error("TOOL_PARAM_INVALID", "N2_PARAMETER_INVALID", f"{name} must be a boolean.")
    return value


def _round(value: float) -> float:
    return round(float(value), 12)


def _error(code: str, error_type: str, message: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError(code=code, message=message, tool_id=TOOL_ID, details={"errorType": error_type, **details})


__all__ = [
    "ARTIFACT_SCHEMA",
    "CATALOG_ID",
    "CATALOG_VERSION",
    "GEOMETRY_REFERENCE_CATALOG",
    "LocalEnvironmentPolyhedraAdapter",
]
