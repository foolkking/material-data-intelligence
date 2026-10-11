"""Bounded facts from saved coordination geometry, without neighbor searches."""
from __future__ import annotations

from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from jsonschema import Draft202012Validator
import mdi_schemas

from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.domain.scientific_results.contracts import FactSourceLocator, ScientificFact, ScientificWarning
from .base import ScientificResultProjectionContext

N2_SCHEMA = "phase10n2.local_environment_polyhedra.v1"
N1_SCHEMAS = {"phase10n1.crystalnn_coordination.v1", "phase10n1.voronoinn_coordination.v1"}
COORDINATION_PROJECTORS = {
    "agent2.structure.coordination_crystalnn", "agent2.structure.coordination_voronoinn",
    "agent2.structure.local_environment_crystalnn", "agent2.structure.local_environment_voronoi",
}
SITE_FACT_LIMIT = 4
NEIGHBOR_FACT_LIMIT = 8


@lru_cache(maxsize=2)
def _validator(local_environment: bool) -> Draft202012Validator:
    name = "phase10n2-local-environment-polyhedra.schema.json" if local_environment else "phase10n1-coordination-contracts.schema.json"
    path = Path(mdi_schemas.__file__).resolve().parent.parent / "json" / name
    return Draft202012Validator(json.loads(path.read_text(encoding="utf-8")))


def valid_coordination_payload(payload: dict[str, Any]) -> bool:
    schema = payload.get("schema_version")
    if schema not in {*N1_SCHEMAS, N2_SCHEMA}:
        return False
    try:
        json.dumps(payload, allow_nan=False)
    except (TypeError, ValueError, OverflowError):
        return False
    if not _validator(schema == N2_SCHEMA).is_valid(payload):
        return False
    sites = payload["siteResults"]
    if len({site["siteId"] for site in sites}) != len(sites):
        return False
    if schema == N2_SCHEMA:
        for site in sites:
            vertices, faces = site["polyhedron"]["vertices"], site["polyhedron"]["faces"]
            ids = {vertex["vertexIdentity"] for vertex in vertices}
            if len(ids) != len(vertices) or len({face["faceIdentity"] for face in faces}) != len(faces):
                return False
            if any(len(set(face["vertexIdentities"])) != 3 or not set(face["vertexIdentities"]).issubset(ids) for face in faces):
                return False
            if site["polyhedron"]["status"] == "UNAVAILABLE" and faces:
                return False
    return True


def validate_local_environment_dependency(context: ScientificResultProjectionContext, artifact: dict[str, Any], payload: dict[str, Any]) -> None:
    source = payload["sourceCoordination"]
    matches = [item for item in context.artifacts if str(item.get("id") or item.get("artifactId")) == source["artifactId"]]
    if len(matches) != 1:
        raise ScientificResultProjectionFailed("Local environment has no exact committed coordination source")
    original = matches[0]
    original_payload = context.artifact_payloads.get(source["artifactId"])
    if (not isinstance(original_payload, dict) or not valid_coordination_payload(original_payload)
            or original_payload.get("schema_version") not in N1_SCHEMAS
            or source["artifactChecksum"] != (original.get("contentHash") or original.get("sha256"))
            or source["contractVersion"] != original_payload["schema_version"]
            or source["toolId"] != original_payload["tool"]["toolId"]
            or source["algorithmId"] != original_payload["algorithm"]["algorithmId"]
            or source["parameterHash"] != original_payload["parameterHash"]
            or any(payload["scope"].get(key) != original_payload["scope"].get(key) for key in ("sourceResourceId", "sourceResourceHash"))):
        raise ScientificResultProjectionFailed("Local environment coordination source identity is inconsistent")
    job_id = str(context.execution_summary.get("job_id") or "")
    for record, data in ((artifact, payload), (original, original_payload)):
        if (record.get("projectId") != context.project_id or record.get("jobId") != job_id
                or data["scope"].get("projectId") != context.project_id or data["scope"].get("jobId") != job_id):
            raise ScientificResultProjectionFailed("Local environment source is outside the executed scope")
    original_sites = {site["siteId"]: site for site in original_payload["siteResults"]}
    for site in payload["siteResults"]:
        original_site = original_sites.get(site["siteId"])
        if (not original_site or site["structureHash"] != original_site["structureHash"]
                or site["siteIndex"] != original_site["siteIndex"]
                or site["sourceCoordinationValue"] != original_site["coordinationValue"]
                or site["sourceCoordinationSemantics"] != original_site["coordinationSemantics"]):
            raise ScientificResultProjectionFailed("Local environment site does not match its saved coordination source")
        neighbors = {neighbor["neighborIdentity"]: neighbor for neighbor in original_site["neighbors"]}
        vertices = site["polyhedron"]["vertices"]
        if len(vertices) != len(neighbors) or set(site["neighborRelationIdentities"]) != set(neighbors):
            raise ScientificResultProjectionFailed("Local environment neighbor coverage is inconsistent")
        for vertex in vertices:
            neighbor = neighbors.get(vertex["neighborIdentity"])
            if (not neighbor or any(vertex[key] != neighbor[key] for key in ("neighborSiteId", "periodicImage", "distance", "distanceUnit"))
                    or not math.isclose(math.hypot(*vertex["relativeCartesian"]), neighbor["distance"], rel_tol=0, abs_tol=1e-6)):
                raise ScientificResultProjectionFailed("Local environment vertex differs from its saved neighbor")


def _sites(context: ScientificResultProjectionContext, artifact_id: str, payload: dict[str, Any]) -> list[tuple[int, dict[str, Any]]]:
    sites = list(enumerate(payload.get("siteResults") or []))
    if payload.get("schema_version") in N1_SCHEMAS:
        consumers = [item for item in context.artifact_payloads.values() if isinstance(item, dict)
                     and item.get("schema_version") == N2_SCHEMA
                     and (item.get("sourceCoordination") or {}).get("artifactId") == artifact_id]
        if consumers:
            requested = {site["siteId"] for item in consumers for site in item["siteResults"]}
            sites = [(index, site) for index, site in sites if site["siteId"] in requested]
    return sites


def coordination_facts(context: ScientificResultProjectionContext, artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    if not valid_coordination_payload(payload):
        return []
    artifact_id = str(artifact.get("id") or artifact.get("artifactId"))
    local = payload["schema_version"] == N2_SCHEMA
    facts: list[ScientificFact] = []

    def add(predicate: str, pointer: str, subject: str, unit: str | None = None) -> None:
        value: Any = payload
        try:
            for token in pointer.strip("/").split("/"):
                value = value[int(token)] if isinstance(value, list) else value[token]
        except (KeyError, IndexError, TypeError, ValueError):
            return
        if value is None or isinstance(value, (dict, list, bool)):
            return
        facts.append(ScientificFact(
            fact_id=f"fact.{uuid5(NAMESPACE_URL, f'mdi-coordination:{artifact_id}:{predicate}:{pointer}').hex}",
            predicate=f"structure.{predicate}", subject_ref=subject, value=value, unit=unit,
            source=FactSourceLocator(artifact_id=artifact_id, artifact_locator=pointer),
        ))

    add("coordination.method", "/sourceCoordination/algorithmId" if local else "/algorithm/algorithmId", artifact_id)
    for key in (("requestedSites", "evaluatedSites", "unavailableSites", "classifiedSites", "ambiguousSites", "unclassifiedSites") if local else ("totalSites", "successfulSites")):
        add(f"coordination.coverage.{key}", f"/coverage/{key}", artifact_id, "count")
    for position, (index, site) in enumerate(_sites(context, artifact_id, payload)[:SITE_FACT_LIMIT]):
        base = f"/siteResults/{index}"
        subject = f"{artifact_id}:site:{site['siteIndex']}"
        add("coordination.site_index", f"{base}/siteIndex", subject)
        if local:
            for key, predicate in (("status", "status"), ("referenceGeometryId", "reference_geometry"), ("geometryScore", "geometry_score"), ("geometryDistanceRms", "geometry_distance_rms")):
                add(f"local_environment.{predicate}", f"{base}/classification/{key}", subject)
            add("local_environment.face_status", f"{base}/polyhedron/status", subject)
            for key, predicate, unit in (
                ("radialDistanceMean", "mean_neighbor_distance", "angstrom"),
                ("radialDistanceSpread", "neighbor_distance_spread", "angstrom"),
                ("bondLengthDistortionIndex", "radial_distortion_index", None),
                ("angularRmsDeviation", "angular_rms_deviation", "degree"),
                ("polyhedronVolume", "volume", "angstrom^3"),
                ("polyhedronSurfaceArea", "surface_area", "angstrom^2"),
            ):
                add(f"local_environment.{predicate}", f"{base}/distortionMetrics/{key}", subject, unit)
        else:
            for key, predicate, unit in (("species", "species", None), ("coordinationSemantics", "semantics", None), ("coordinationValue", "weighted_value", None), ("neighborCount", "neighbor_count", "count")):
                add(f"coordination.{predicate}", f"{base}/{key}", subject, unit)
        # Detailed coordinates belong to the first retained site. The full
        # saved tables remain available independently of the text-fact budget.
        if position != 0:
            continue
        has_geometry = not local and any(isinstance(item, dict) and item.get("schema_version") == N2_SCHEMA
                                          and item.get("sourceCoordination", {}).get("artifactId") == artifact_id
                                          for item in context.artifact_payloads.values())
        entries = site["polyhedron"]["vertices"] if local else site["neighbors"]
        for neighbor_index, _neighbor in enumerate(entries[:NEIGHBOR_FACT_LIMIT]):
            pointer = f"{base}/polyhedron/vertices/{neighbor_index}" if local else f"{base}/neighbors/{neighbor_index}"
            neighbor_subject = f"{subject}:neighbor:{neighbor_index}"
            if not local:
                # N2 retains the neighbor identity; the exact numeric site index
                # remains authoritative in its committed N1 dependency.
                add("coordination.neighbor_site_index", f"{pointer}/neighborSiteIndex", neighbor_subject)
                if has_geometry:
                    continue
            add("coordination.neighbor_distance", f"{pointer}/distance", neighbor_subject, "angstrom")
            add("coordination.neighbor_site", f"{pointer}/neighborSiteId", neighbor_subject)
            for axis, name in enumerate(("x", "y", "z")):
                add(f"coordination.periodic_image_{name}", f"{pointer}/periodicImage/{axis}", neighbor_subject)
                if local:
                    add(f"local_environment.relative_{name}", f"{pointer}/relativeCartesian/{axis}", neighbor_subject, "angstrom")
    return facts


def coordination_warnings(context: ScientificResultProjectionContext, artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificWarning]:
    artifact_id = str(artifact.get("id") or artifact.get("artifactId"))
    sites = _sites(context, artifact_id, payload)
    entries = (sites[0][1].get("polyhedron", {}).get("vertices", sites[0][1].get("neighbors", [])) if sites else [])
    messages = [(str(code), str(code)) for code in dict.fromkeys(payload.get("warnings") or [])]
    if len(sites) > SITE_FACT_LIMIT or len(entries) > NEIGHBOR_FACT_LIMIT or len(sites) > 1:
        messages.append(("COORDINATION_TEXT_FACTS_BOUNDED", "数值解读最多涵盖前 4 个已评估位点；详细近邻坐标限于首个位点的前 8 项。完整位点、顶点与面保留在原始结果中。"))
    return [ScientificWarning(warning_id=f"warning.{uuid5(NAMESPACE_URL, f'{artifact_id}:{code}').hex}",
                              code=code, message=message, source_ref=artifact_id) for code, message in messages]
