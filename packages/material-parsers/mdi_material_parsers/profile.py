from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from statistics import median
from typing import Any

from mdi_schemas import DataProfile, MaterialObjectType
from pymatgen.core import Structure

from .models import NormalizedObjectDraft, ParseResult
from .semantic_profile import (
    MAX_PROFILE_OBJECTS,
    SEMANTIC_RULES_VERSION,
    analysis_readiness,
    resource_semantics,
    sample_identity,
    table_semantics,
)


def build_data_profile(
    *,
    dataset_id: str,
    parse_results: list[ParseResult],
    platform_tool_ids: set[str] | None = None,
) -> DataProfile:
    objects = [obj for result in parse_results for obj in result.objects]
    profiled_objects = sorted(objects, key=lambda item: (item.object_type.value, item.id))[:MAX_PROFILE_OBJECTS]
    structure_objects = [obj for obj in objects if obj.object_type == MaterialObjectType.Structure]
    dataframe_objects = [obj for obj in objects if obj.object_type == MaterialObjectType.DataFrame]
    profiled_dataframes = [obj for obj in profiled_objects if obj.object_type == MaterialObjectType.DataFrame]
    quality_issues = _quality_issues(parse_results)

    semantic_columns: list[dict[str, Any]] = []
    semantic_groups: list[dict[str, Any]] = []
    coverage_records: list[dict[str, Any]] = []
    for dataframe_obj in profiled_dataframes:
        columns, groups, coverage, warnings = table_semantics(dataframe_obj)
        semantic_columns.extend(columns)
        semantic_groups.extend(groups)
        coverage_records.append(coverage)
        quality_issues.extend(_semantic_quality_issues(dataframe_obj.id, columns, groups, warnings))
    resources = resource_semantics(profiled_objects)
    if len(objects) > MAX_PROFILE_OBJECTS:
        quality_issues.append(
            {
                "severity": "warning",
                "code": "PROFILE_OBJECT_CAP_APPLIED",
                "message": "Only the bounded resource set was semantically profiled; no omitted objects were classified.",
                "refs": [{"type": "dataset", "id": dataset_id}],
            }
        )
    readiness = analysis_readiness(semantic_columns, semantic_groups, resources, platform_tool_ids)
    coverage = _combined_coverage(coverage_records)
    identity = sample_identity(semantic_columns, profiled_dataframes)
    coordination_readiness = _coordination_readiness(profiled_objects)
    experimental_xrd_readiness = _experimental_xrd_readiness(profiled_objects)
    profile_contract_version = "2.2" if experimental_xrd_readiness["resources"] else ("2.1" if coordination_readiness["structures"] else "2.0")

    semantic_payload = {
        "datasetId": dataset_id,
        "datasetVersion": "2",
        "semanticRulesVersion": SEMANTIC_RULES_VERSION,
        "objectHashes": sorted(obj.hash for obj in objects),
        "semanticColumns": semantic_columns,
        "semanticGroups": semantic_groups,
        "resourceSemantics": resources,
        "analysisReadiness": readiness,
        "sampleIdentity": identity,
        "profileCoverage": coverage,
        "coordinationReadiness": coordination_readiness,
        "experimentalXrdReadiness": experimental_xrd_readiness,
    }
    semantic_hash = hashlib.sha256(
        json.dumps(semantic_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()

    return DataProfile(
        schemaVersion="0.1",
        profileId=f"profile_{dataset_id}_v2",
        datasetId=dataset_id,
        version="2",
        datasetType=_dataset_type(objects, structure_objects, dataframe_objects, semantic_groups),
        files=[result.file_profile() for result in parse_results],
        objects=[_object_profile(obj) for obj in objects],
        structureSummary=_structure_summary(structure_objects) if structure_objects else None,
        tableSummary=_table_summary(dataframe_objects[0]) if dataframe_objects else None,
        phononSummary=_phonon_summary(objects),
        trajectorySummary=_trajectory_summary(objects),
        qualityIssues=quality_issues,
        recommendedTasks=_recommended_tasks(structure_objects, dataframe_objects),
        profileContractVersion=profile_contract_version,
        semanticRulesVersion=SEMANTIC_RULES_VERSION,
        semanticHash=semantic_hash,
        semanticColumns=semantic_columns,
        semanticGroups=semantic_groups,
        resourceSemantics=resources,
        analysisReadiness=readiness,
        sampleIdentity=identity,
        profileCoverage=coverage,
        coordinationReadiness=coordination_readiness if coordination_readiness["structures"] else None,
        experimentalXrdReadiness=experimental_xrd_readiness if profile_contract_version == "2.2" else None,
        createdAt=datetime.now(timezone.utc).isoformat(),
    )


def _coordination_readiness(objects: list[NormalizedObjectDraft]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for obj in objects:
        if obj.object_type != MaterialObjectType.Structure:
            continue
        reasons: list[str] = []
        periodic = obj.metadata.get("periodicity") == "periodic"
        lattice_volume = obj.metadata.get("latticeVolume")
        lattice_status = "VALID" if isinstance(lattice_volume, (int, float)) and math.isfinite(float(lattice_volume)) and float(lattice_volume) > 0 else "INVALID"
        disorder_status = "UNKNOWN"
        partial_status = "UNKNOWN"
        species_status = "UNSUPPORTED"
        try:
            structure = Structure.from_dict(obj.payload)
            disordered = any(not site.is_ordered for site in structure)
            partial = any(not math.isclose(float(site.species.num_atoms), 1.0, abs_tol=1e-12) for site in structure)
            disorder_status = "DISORDERED" if disordered else "ORDERED"
            partial_status = "PRESENT" if partial else "ABSENT"
            species_status = "DISORDERED" if disordered else ("PARTIAL_OCCUPANCY" if partial else "ORDERED_FULL_OCCUPANCY")
        except (TypeError, ValueError, KeyError):
            reasons.append("STRUCTURE_SEMANTICS_UNREADABLE")
        if not periodic:
            reasons.append("PERIODIC_STRUCTURE_REQUIRED")
        if lattice_status != "VALID":
            reasons.append("VALID_LATTICE_REQUIRED")
        if disorder_status == "DISORDERED":
            reasons.append("DISORDERED_SITES_UNSUPPORTED")
        if partial_status == "PRESENT":
            reasons.append("PARTIAL_OCCUPANCY_UNSUPPORTED")
        if int(obj.metadata.get("nAtoms") or 0) > 5000:
            reasons.append("COORDINATION_SITE_CAP_EXCEEDED")
        status = "READY" if not reasons else ("UNSUPPORTED_DATA_KIND" if not periodic else "AMBIGUOUS")
        records.append(
            {
                "objectId": obj.id,
                "objectHash": obj.hash,
                "periodic": periodic,
                "latticeStatus": lattice_status,
                "siteCount": int(obj.metadata.get("nAtoms") or 0),
                "speciesOccupancyStatus": species_status,
                "disorderStatus": disorder_status,
                "partialOccupancyStatus": partial_status,
                "coordinationInputStatus": status,
                "reasons": sorted(set(reasons)),
            }
        )
    eligible = sum(1 for record in records if record["coordinationInputStatus"] == "READY")
    if not records:
        overall = "MISSING_REQUIRED_DATA"
        reasons = ["PERIODIC_STRUCTURE_REQUIRED"]
    elif eligible:
        overall = "READY"
        reasons = []
    else:
        overall = "AMBIGUOUS"
        reasons = sorted({reason for record in records for reason in record["reasons"]})
    return {
        "contractVersion": "1.0",
        "periodicStructurePresent": any(record["periodic"] for record in records),
        "eligibleStructureCount": min(eligible, 32),
        "structures": records[:32],
        "status": overall,
        "reasons": reasons,
    }


def _experimental_xrd_readiness(objects: list[NormalizedObjectDraft]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for obj in objects:
        metadata = obj.metadata.get("experimentalXrd")
        if obj.object_type != MaterialObjectType.DataFrame or not isinstance(metadata, dict):
            continue
        reasons: list[str] = []
        if metadata.get("xAxis") != {"kind": "two_theta", "unit": "degree"}:
            reasons.append("EXPERIMENTAL_XRD_AXIS_UNSUPPORTED")
        wavelength = metadata.get("wavelength") or {}
        wavelength_present = isinstance(wavelength.get("value"), (int, float)) and math.isfinite(float(wavelength["value"])) and float(wavelength["value"]) > 0
        if not wavelength_present:
            reasons.append("XRD_WAVELENGTH_MISSING")
        if wavelength.get("unit") != "angstrom":
            reasons.append("XRD_WAVELENGTH_UNIT_UNSUPPORTED")
        point_count = int(metadata.get("pointCount") or 0)
        if not 3 <= point_count <= 200_000:
            reasons.append("EXPERIMENTAL_XRD_POINT_COUNT_INVALID")
        if metadata.get("axisMonotonicity") != "STRICTLY_INCREASING":
            reasons.append("EXPERIMENTAL_XRD_AXIS_NOT_MONOTONIC")
        status = "READY" if not reasons else "AMBIGUOUS"
        records.append({
            "objectId": obj.id, "objectHash": obj.hash, "resourceId": str(metadata.get("resourceId") or obj.id),
            "resourceHash": str(metadata.get("resourceHash") or obj.hash), "xAxisKind": "two_theta",
            "xAxisUnit": "degree", "intensitySemantic": str(metadata.get("intensitySemantic") or "arbitrary_relative_unit"),
            "wavelengthPresent": wavelength_present, "wavelengthUnit": wavelength.get("unit") if wavelength.get("unit") == "angstrom" else None,
            "pointCount": point_count, "axisMonotonicity": str(metadata.get("axisMonotonicity") or "UNKNOWN"),
            "status": status, "reasons": sorted(set(reasons)),
        })
    eligible = sum(item["status"] == "READY" for item in records)
    return {
        "contractVersion": "1.0", "experimentalXrdPresent": bool(records), "eligibleResourceCount": min(eligible, 32),
        "resources": records[:32], "status": "READY" if eligible else ("AMBIGUOUS" if records else "MISSING_REQUIRED_DATA"),
        "reasons": [] if eligible else sorted({reason for record in records for reason in record["reasons"]}) or ["EXPERIMENTAL_XRD_MISSING"],
    }


def _dataset_type(
    objects: list[NormalizedObjectDraft],
    structures: list[NormalizedObjectDraft],
    dataframes: list[NormalizedObjectDraft],
    semantic_groups: list[dict[str, Any]],
) -> str:
    object_types = {obj.object_type for obj in objects}
    if len(object_types) > 1:
        return "mixed_material_dataset"
    if structures:
        return "structure_collection"
    if dataframes and any(group["kind"] in {"regression", "classification"} for group in semantic_groups):
        return "ml_results"
    if dataframes:
        return "table"
    if MaterialObjectType.Trajectory in object_types:
        return "trajectory"
    if object_types & {MaterialObjectType.PhononBand, MaterialObjectType.PhononDos, MaterialObjectType.PhononEigenvector}:
        return "phonon"
    if MaterialObjectType.VolumetricData in object_types:
        return "volumetric"
    return "unknown"


def _object_profile(obj: NormalizedObjectDraft) -> dict[str, Any]:
    return {
        "objectId": obj.id,
        "objectType": obj.object_type.value,
        "count": 1,
        "sourceFileIds": obj.source_file_ids,
        "objectHash": obj.hash,
        "periodicity": obj.metadata.get("periodicity"),
    }


def _structure_summary(structures: list[NormalizedObjectDraft]) -> dict[str, Any]:
    formulas = [obj.metadata["formula"] for obj in structures]
    formula_counts = Counter(formulas)
    chemical_system_counts = Counter(obj.metadata["chemicalSystem"] for obj in structures)
    atom_counts = [int(obj.metadata["nAtoms"]) for obj in structures]
    elements = sorted({element for obj in structures for element in obj.metadata["elements"]})
    return {
        "nStructures": len(structures),
        "formulaStats": {
            "total": len(formulas),
            "uniqueCount": len(formula_counts),
            "topFormulas": [{"formula": formula, "count": count} for formula, count in formula_counts.most_common(10)],
        },
        "elements": elements,
        "chemicalSystemStats": {
            "uniqueCount": len(chemical_system_counts),
            "topChemicalSystems": [
                {"chemSys": chem_sys, "count": count} for chem_sys, count in chemical_system_counts.most_common(10)
            ],
        },
        "atomCountStats": {
            "min": min(atom_counts),
            "median": median(atom_counts),
            "max": max(atom_counts),
        },
        "hasForces": False,
        "hasMagmoms": False,
        "representativeStructureIds": [obj.id for obj in structures[:8]],
    }


def _table_summary(dataframe_obj: NormalizedObjectDraft) -> dict[str, Any]:
    columns = dataframe_obj.metadata["columns"]
    return {
        "nRows": dataframe_obj.metadata["nRows"],
        "nColumns": dataframe_obj.metadata["nColumns"],
        "columns": columns,
        "inferredTask": "regression" if _has_roles(dataframe_obj, {"target", "prediction"}) else "unknown",
    }


def _trajectory_summary(objects: list[NormalizedObjectDraft]) -> dict[str, Any] | None:
    trajectories = [obj for obj in objects if obj.object_type == MaterialObjectType.Trajectory]
    if not trajectories:
        return None
    summaries = [obj.metadata.get("trajectorySummary", {}) for obj in trajectories]
    return {
        "trajectoryCount": len(trajectories),
        "frameCount": sum(int(summary.get("frameCount", 0)) for summary in summaries),
        "atomCounts": sorted({int(summary.get("atomCount", 0)) for summary in summaries}),
        "properties": sorted({str(value) for summary in summaries for value in summary.get("properties", [])}),
        "resourceIds": [obj.id for obj in trajectories],
    }


def _phonon_summary(objects: list[NormalizedObjectDraft]) -> dict[str, Any] | None:
    phonon_objects = [
        obj
        for obj in objects
        if obj.object_type in {MaterialObjectType.PhononBand, MaterialObjectType.PhononDos, MaterialObjectType.PhononEigenvector}
    ]
    if not phonon_objects:
        return None
    return {
        "resourceCount": len(phonon_objects),
        "resourceKinds": sorted({obj.object_type.value for obj in phonon_objects}),
        "resourceIds": [obj.id for obj in phonon_objects],
    }


def _combined_coverage(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not records:
        return None
    warnings = sorted({warning for record in records for warning in record["warnings"]})
    return {
        "policy": "deterministic_bounded_sample" if any(record["policy"] != "complete" for record in records) else "complete",
        "rowsInspected": sum(record["rowsInspected"] for record in records),
        "totalRows": sum(record["totalRows"] for record in records),
        "columnsInspected": sum(record["columnsInspected"] for record in records),
        "totalColumns": sum(record["totalColumns"] for record in records),
        "limits": records[0]["limits"],
        "warnings": warnings,
    }


def _semantic_quality_issues(
    object_id: str,
    columns: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    warnings: list[str],
) -> list[dict[str, Any]]:
    issues = [
        {
            "severity": "warning",
            "code": warning,
            "message": _semantic_warning_message(warning),
            "refs": [{"type": "object", "id": object_id}],
        }
        for warning in warnings
    ]
    for column in columns:
        for role in column["roles"]:
            if role["role"] == "material_formula" and role["details"].get("invalidCount", 0):
                issues.append(
                    {
                        "severity": "warning",
                        "code": "FORMULA_VALUES_PARTIALLY_INVALID",
                        "message": "Some inspected formula values could not be parsed; row-level validation remains required.",
                        "refs": [{"type": "column", "id": f"{object_id}:{column['column']}"}],
                    }
                )
    for group in groups:
        if group["status"] == "AMBIGUOUS":
            issues.append(
                {
                    "severity": "warning",
                    "code": "SEMANTIC_GROUP_AMBIGUOUS",
                    "message": "Multiple deterministic semantic candidates prevent automatic task binding.",
                    "refs": [{"type": "semantic_group", "id": group["groupId"]}],
                }
            )
    return issues


def _semantic_warning_message(code: str) -> str:
    return {
        "PROFILE_COLUMN_CAP_APPLIED": "Only the bounded profile column set was inspected; no columns were silently classified.",
        "PROFILE_ROW_SAMPLE_APPLIED": "Semantic value checks used a deterministic bounded row sample.",
        "MULTIPLE_FORMULA_COLUMNS_AMBIGUOUS": "Multiple formula candidates were detected and no preferred column was selected.",
    }.get(code, "A bounded material-profile warning was recorded.")


def _quality_issues(parse_results: list[ParseResult]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for result in parse_results:
        if result.parse_status in {"failed", "unsupported"}:
            issues.append(
                {
                    "severity": "error" if result.parse_status == "failed" else "warning",
                    "code": result.error_code or "PARSE_ISSUE",
                    "message": result.error_message or "File could not be parsed.",
                    "refs": [{"type": "file", "id": result.file_id}],
                }
            )
        for obj in result.objects:
            if obj.object_type == MaterialObjectType.Atoms and obj.metadata.get("periodicity") == "non_periodic":
                issues.append(
                    {
                        "severity": "warning",
                        "code": "NON_PERIODIC_ATOMS",
                        "message": "Plain XYZ was parsed as non-periodic Atoms and is not eligible for periodic structure tools.",
                        "refs": [{"type": "object", "id": obj.id}],
                    }
                )
    return issues


def _recommended_tasks(structures: list[NormalizedObjectDraft], dataframes: list[NormalizedObjectDraft]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    if structures:
        tasks.extend(
            [
                {
                    "taskId": "composition.overview",
                    "label": "Composition overview",
                    "stage": "mvp",
                    "taskType": "composition_overview",
                    "availableNow": True,
                    "requiredTools": ["composition.ptable_heatmap"],
                    "reason": "Periodic structures contain composition information.",
                },
                {
                    "taskId": "structure.viewer",
                    "label": "Representative structure viewer",
                    "stage": "mvp",
                    "taskType": "structure_quality",
                    "availableNow": True,
                    "requiredTools": ["structure.structure_3d", "structure.viewer_3d"],
                    "reason": "Periodic Structure objects are available.",
                },
            ]
        )
    if dataframes and _has_roles(dataframes[0], {"target", "prediction"}):
        tasks.append(
            {
                "taskId": "ml.evaluation",
                "label": "ML prediction evaluation",
                "stage": "mvp",
                "taskType": "ml_evaluation",
                "availableNow": False,
                "requiredTools": ["ml.basic_metrics", "ml.error_distribution", "ml.outlier_table"],
                "reason": "Target and prediction columns were detected; the product capability remains planned until its bounded adapter and artifact contract are implemented.",
            }
        )
    return tasks


def _has_roles(dataframe_obj: NormalizedObjectDraft, roles: set[str]) -> bool:
    found = {column.get("inferredRole") for column in dataframe_obj.metadata.get("columns", [])}
    return roles.issubset(found)
