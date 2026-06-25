from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from statistics import median
from typing import Any

from mdi_schemas import DataProfile, MaterialObjectType

from .models import NormalizedObjectDraft, ParseResult


def build_data_profile(*, dataset_id: str, parse_results: list[ParseResult]) -> DataProfile:
    objects = [obj for result in parse_results for obj in result.objects]
    structure_objects = [obj for obj in objects if obj.object_type == MaterialObjectType.Structure]
    dataframe_objects = [obj for obj in objects if obj.object_type == MaterialObjectType.DataFrame]
    quality_issues = _quality_issues(parse_results)

    return DataProfile(
        schemaVersion="0.1",
        profileId=f"profile_{dataset_id}_v1",
        datasetId=dataset_id,
        version="1",
        datasetType=_dataset_type(structure_objects, dataframe_objects),
        files=[result.file_profile() for result in parse_results],
        objects=[_object_profile(obj) for obj in objects],
        structureSummary=_structure_summary(structure_objects) if structure_objects else None,
        tableSummary=_table_summary(dataframe_objects[0]) if dataframe_objects else None,
        qualityIssues=quality_issues,
        recommendedTasks=_recommended_tasks(structure_objects, dataframe_objects),
        createdAt=datetime.now(timezone.utc).isoformat(),
    )


def _dataset_type(structures: list[NormalizedObjectDraft], dataframes: list[NormalizedObjectDraft]) -> str:
    if structures and dataframes:
        return "mixed_material_dataset"
    if structures:
        return "structure_collection"
    if dataframes and _has_roles(dataframes[0], {"target", "prediction"}):
        return "ml_results"
    if dataframes:
        return "unknown"
    return "unknown"


def _object_profile(obj: NormalizedObjectDraft) -> dict[str, Any]:
    return {
        "objectId": obj.id,
        "objectType": obj.object_type.value,
        "count": 1,
        "sourceFileIds": obj.source_file_ids,
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
                "availableNow": True,
                "requiredTools": ["ml.basic_metrics", "ml.error_distribution", "ml.outlier_table"],
                "reason": "A table with target and prediction columns was detected.",
            }
        )
    return tasks


def _has_roles(dataframe_obj: NormalizedObjectDraft, roles: set[str]) -> bool:
    found = {column.get("inferredRole") for column in dataframe_obj.metadata.get("columns", [])}
    return roles.issubset(found)
