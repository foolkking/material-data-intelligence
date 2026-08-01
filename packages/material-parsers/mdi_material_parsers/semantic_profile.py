from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Any, Iterable

from pymatgen.core import Composition

from mdi_schemas import MaterialObjectType

from .models import NormalizedObjectDraft


SEMANTIC_RULES_VERSION = "phase10k1.material_profile_semantics.v1"
MAX_PROFILE_COLUMNS = 512
MAX_PROFILE_ROWS = 4096
MAX_FORMULA_VALUES = 1024
MAX_FORMULA_LENGTH = 256
MAX_PROBABILITY_COLUMNS = 64
MAX_PROFILE_OBJECTS = 256
MAX_COLUMN_NAME_LENGTH = 256
MAX_GROUP_ID_LENGTH = 128
MAX_UNIT_LENGTH = 64

_CANONICAL_NAMES: dict[str, tuple[str, str | None]] = {
    "formula": ("material_formula", None),
    "sample_id": ("sample_identity", None),
    "y_true": ("regression_target", "regression:default"),
    "y_pred": ("regression_prediction", "regression:default"),
    "y_std": ("regression_uncertainty", "regression:default"),
    "class_true": ("classification_target", "classification:default"),
    "class_pred": ("classification_prediction", "classification:default"),
}

_ALIASES: dict[str, tuple[str, str | None]] = {
    "composition": ("material_formula", None),
    "chemical_formula": ("material_formula", None),
    "pretty_formula": ("material_formula", None),
    "material_formula": ("material_formula", None),
    "reduced_formula": ("material_formula", None),
    "target": ("regression_target", "regression:default"),
    "actual": ("regression_target", "regression:default"),
    "prediction": ("regression_prediction", "regression:default"),
    "pred": ("regression_prediction", "regression:default"),
    "predicted": ("regression_prediction", "regression:default"),
    "uncertainty": ("regression_uncertainty", "regression:default"),
    "std": ("regression_uncertainty", "regression:default"),
    "sigma": ("regression_uncertainty", "regression:default"),
    "label": ("classification_target", "classification:default"),
    "class_label": ("classification_target", "classification:default"),
    "true_label": ("classification_target", "classification:default"),
    "predicted_label": ("classification_prediction", "classification:default"),
    "material_id": ("sample_identity", None),
    "structure_id": ("sample_identity", None),
    "id": ("sample_identity", None),
}

_PROPERTY_NAMES = {
    "energy",
    "formation_energy",
    "band_gap",
    "density",
    "volume",
    "magnetization",
    "force",
    "forces",
    "stress",
    "temperature",
}

_REGRESSION_PATTERN = re.compile(
    r"^(?P<group>[a-z][a-z0-9_]{0,47})_(?P<kind>true|target|pred|prediction|std|sigma|uncertainty)$"
)
_PROBABILITY_PATTERN = re.compile(r"^(?:prob|probability)[_:.\-](?P<class>[a-z0-9][a-z0-9_.\-]{0,47})$")
_LEGACY_ROLE_NAMES = {
    "formula": "formula",
    "composition": "formula",
    "chemical_formula": "formula",
    "pretty_formula": "formula",
    "target": "target",
    "y_true": "target",
    "true": "target",
    "actual": "target",
    "label": "target",
    "prediction": "prediction",
    "pred": "prediction",
    "y_pred": "prediction",
    "predicted": "prediction",
    "uncertainty": "uncertainty",
    "std": "uncertainty",
    "y_std": "uncertainty",
    "sigma": "uncertainty",
    "structure_id": "structure_id",
    "material_id": "structure_id",
    "id": "structure_id",
}

_PLATFORM_TOOLS: dict[str, tuple[str, ...]] = {
    "table_distribution": ("viz.histogram",),
    "scatter": ("viz.scatter",),
    "histogram": ("viz.histogram",),
    "correlation": ("viz.correlation",),
    "composition_summary": ("composition.summary",),
    "formula_statistics": ("composition.summary",),
    "element_distribution": ("composition.ptable_heatmap",),
    "chemical_system_visualization": ("composition.chem_sys_treemap",),
    "structure_summary": ("structure.summary",),
    "dataset_materials_explorer": ("dataset.materials_explorer",),
    "dataset_structure_statistics": ("dataset.materials_explorer",),
    "composition_space": ("dataset.composition_space",),
    "regression_evaluation": ("ml.regression_evaluation",),
    "uncertainty_evaluation": ("ml.uncertainty_evaluation",),
    "classification_evaluation": ("ml.classification_evaluation",),
    "trajectory_visualization": ("structure.trajectory_viewer",),
    "phonon_visualization": ("phonon.band_dos",),
    "volumetric_visualization": ("structure.volumetric_data",),
}


def legacy_inferred_role(column_name: str) -> str | None:
    """Preserve the pre-10K-1 Planner-facing role contract exactly."""

    return _LEGACY_ROLE_NAMES.get(column_name.strip().lower())


def resolve_column_name(column_name: str, *, dtype: str | None) -> tuple[str, str, str | None, dict[str, Any]] | None:
    if len(column_name) > MAX_COLUMN_NAME_LENGTH:
        return None
    key = column_name.strip().lower()
    if key in _CANONICAL_NAMES:
        role, group_id = _CANONICAL_NAMES[key]
        return _dtype_guard(role, dtype, "canonical_name", group_id, {})
    if key in _ALIASES:
        role, group_id = _ALIASES[key]
        return _dtype_guard(role, dtype, "alias_match", group_id, {})
    probability_match = _PROBABILITY_PATTERN.fullmatch(key)
    if probability_match:
        return _dtype_guard(
            "class_probability",
            dtype,
            "bounded_pattern",
            "classification:default",
            {"class": probability_match.group("class")},
        )
    regression_match = _REGRESSION_PATTERN.fullmatch(key)
    if regression_match:
        group = regression_match.group("group")
        kind = regression_match.group("kind")
        role = {
            "true": "regression_target",
            "target": "regression_target",
            "pred": "regression_prediction",
            "prediction": "regression_prediction",
            "std": "regression_uncertainty",
            "sigma": "regression_uncertainty",
            "uncertainty": "regression_uncertainty",
        }[kind]
        group_id = f"regression:{group}"
        if group in _PROPERTY_NAMES:
            details = {"property": group}
        else:
            details = {"series": group}
        return _dtype_guard(role, dtype, "bounded_pattern", group_id, details)
    if key in _PROPERTY_NAMES:
        return _dtype_guard("material_property", dtype, "canonical_name", None, {"property": key})
    return None


def _dtype_guard(
    role: str,
    dtype: str | None,
    authority: str,
    group_id: str | None,
    details: dict[str, Any],
) -> tuple[str, str, str | None, dict[str, Any]] | None:
    numeric_roles = {
        "regression_target",
        "regression_prediction",
        "regression_uncertainty",
        "class_probability",
        "material_property",
    }
    if dtype is not None and role in numeric_roles and dtype != "number":
        return None
    if dtype is not None and role == "material_formula" and dtype != "string":
        return None
    return role, authority, group_id, details


def table_semantics(obj: NormalizedObjectDraft) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], list[str]]:
    metadata_columns = obj.metadata.get("columns", [])
    total_columns = int(obj.metadata.get("nColumns", len(metadata_columns)))
    total_rows = int(obj.metadata.get("nRows", len(obj.payload) if isinstance(obj.payload, list) else 0))
    columns = metadata_columns[:MAX_PROFILE_COLUMNS]
    rows = obj.payload if isinstance(obj.payload, list) else []
    row_indices = _bounded_indices(total_rows, MAX_PROFILE_ROWS)
    sampled_rows = [rows[index] for index in row_indices if index < len(rows) and isinstance(rows[index], dict)]
    warnings: list[str] = []
    if total_columns > len(columns):
        warnings.append("PROFILE_COLUMN_CAP_APPLIED")
    if total_rows > len(sampled_rows):
        warnings.append("PROFILE_ROW_SAMPLE_APPLIED")

    semantic_columns: list[dict[str, Any]] = []
    formula_role_columns: list[str] = []
    for column in columns:
        name = str(column.get("name", ""))
        dtype = str(column.get("dtype", "unknown"))
        ambiguities: list[str] = []
        roles: list[dict[str, Any]] = []
        metadata_role = column.get("semanticRole")
        user_declared_role = column.get("declaredRole")
        explicit_role = metadata_role or user_declared_role
        explicit_group_id = column.get("semanticGroupId") or column.get("groupId")
        if isinstance(explicit_role, str) and explicit_role in _allowed_explicit_roles():
            scoped_group_id: str | None = None
            if isinstance(explicit_group_id, str):
                if len(explicit_group_id) <= MAX_GROUP_ID_LENGTH:
                    scoped_group_id = f"{obj.id}:{explicit_group_id}"
                else:
                    ambiguities.append("SEMANTIC_GROUP_ID_EXCEEDS_PROFILE_LIMIT")
            resolved_explicit = _dtype_guard(
                explicit_role,
                dtype,
                "explicit_metadata" if metadata_role else "user_declared",
                scoped_group_id,
                {},
            )
            if resolved_explicit is not None:
                role, authority, group_id, details = resolved_explicit
                roles.append({"role": role, "authority": authority, "groupId": group_id, "details": details})
        else:
            resolved = resolve_column_name(name, dtype=dtype)
            if resolved is not None:
                role, authority, group_id, details = resolved
                roles.append(
                    {
                        "role": role,
                        "authority": authority,
                        "groupId": f"{obj.id}:{group_id}" if group_id else None,
                        "details": details,
                    }
                )
        if len(name) > MAX_COLUMN_NAME_LENGTH:
            ambiguities.append("COLUMN_NAME_EXCEEDS_PROFILE_LIMIT")
            roles = []
        unit = column.get("unit") if isinstance(column.get("unit"), str) else None
        if unit is not None and len(unit) > MAX_UNIT_LENGTH:
            unit = None
            ambiguities.append("UNIT_METADATA_EXCEEDS_PROFILE_LIMIT")

        values = [row.get(name) for row in sampled_rows]
        finite_count, non_finite_count = _finite_counts(values) if dtype == "number" else (None, None)
        if dtype == "number" and finite_count == 0 and roles:
            ambiguities.append("SEMANTIC_NUMERIC_COLUMN_HAS_NO_FINITE_VALUES")
            roles = []
        for role in roles:
            if role["role"] == "material_formula":
                formula_role_columns.append(name)
                role["details"] = {**role["details"], **_formula_parseability(values)}

        semantic_columns.append(
            {
                "objectId": obj.id,
                "column": name,
                "dtype": dtype,
                "roles": roles,
                "missingCount": int(column.get("missingCount", 0)),
                "uniqueCount": int(column.get("uniqueCount", 0)),
                "finiteCount": finite_count,
                "nonFiniteCount": non_finite_count,
                "rowsInspected": len(sampled_rows),
                "totalRows": total_rows,
                "unit": unit,
                "ambiguities": ambiguities,
            }
        )

    groups = _semantic_groups(semantic_columns)
    _validate_probability_groups(groups, sampled_rows)
    if len(formula_role_columns) > 1:
        warnings.append("MULTIPLE_FORMULA_COLUMNS_AMBIGUOUS")
    coverage = {
        "policy": "complete" if total_rows <= MAX_PROFILE_ROWS and total_columns <= MAX_PROFILE_COLUMNS else "deterministic_bounded_sample",
        "rowsInspected": len(sampled_rows),
        "totalRows": total_rows,
        "columnsInspected": len(columns),
        "totalColumns": total_columns,
        "limits": {
            "maxRows": MAX_PROFILE_ROWS,
            "maxColumns": MAX_PROFILE_COLUMNS,
            "maxFormulaValues": MAX_FORMULA_VALUES,
            "maxFormulaLength": MAX_FORMULA_LENGTH,
            "maxProbabilityColumns": MAX_PROBABILITY_COLUMNS,
            "maxObjects": MAX_PROFILE_OBJECTS,
            "maxGroupIdLength": MAX_GROUP_ID_LENGTH,
            "maxUnitLength": MAX_UNIT_LENGTH,
        },
        "warnings": warnings,
    }
    return semantic_columns, groups, coverage, warnings


def _semantic_groups(columns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "kind": "regression",
            "targetColumns": [],
            "predictionColumns": [],
            "uncertaintyColumns": [],
            "probabilityColumns": [],
            "classes": [],
            "_series": {},
        }
    )
    for column in columns:
        for role in column["roles"]:
            group_id = role.get("groupId")
            if not group_id:
                continue
            group = grouped[group_id]
            semantic_role = role["role"]
            if semantic_role.startswith("classification") or semantic_role == "class_probability":
                group["kind"] = "classification"
            if semantic_role.endswith("target"):
                group["targetColumns"].append(column["column"])
            elif semantic_role.endswith("prediction"):
                group["predictionColumns"].append(column["column"])
            elif semantic_role == "regression_uncertainty":
                group["uncertaintyColumns"].append(column["column"])
            elif semantic_role == "class_probability":
                group["probabilityColumns"].append(column["column"])
                group["classes"].append(str(role["details"]["class"]))
            if semantic_role in {"regression_prediction", "regression_uncertainty"}:
                series_id = str(role["details"].get("series") or role["details"].get("property") or "default")
                series = group["_series"].setdefault(series_id, {"predictionColumn": None, "uncertaintyColumns": []})
                if semantic_role == "regression_prediction":
                    series["predictionColumn"] = column["column"]
                else:
                    series["uncertaintyColumns"].append(column["column"])

    # A single canonical target may be shared by independently named model
    # series, but uncertainties remain bound only to their matching series.
    for group_id in list(grouped):
        marker = ":regression:default"
        if not group_id.endswith(marker):
            continue
        default_group = grouped[group_id]
        object_prefix = group_id[: -len(marker)]
        if len(default_group["targetColumns"]) != 1 or default_group["predictionColumns"]:
            continue
        related_ids = [
            candidate_id
            for candidate_id, candidate in grouped.items()
            if candidate_id.startswith(f"{object_prefix}:regression:")
            and candidate_id != group_id
            and candidate["kind"] == "regression"
            and not candidate["targetColumns"]
        ]
        for candidate_id in related_ids:
            grouped[candidate_id]["targetColumns"] = list(default_group["targetColumns"])
        if related_ids and not default_group["uncertaintyColumns"]:
            del grouped[group_id]

    result: list[dict[str, Any]] = []
    for group_id in sorted(grouped):
        group = grouped[group_id]
        series_bindings = [
            {
                "seriesId": series_id,
                "predictionColumn": values["predictionColumn"],
                "uncertaintyColumns": sorted(values["uncertaintyColumns"]),
            }
            for series_id, values in sorted(group.pop("_series").items())
        ]
        reasons: list[str] = []
        if len(group["targetColumns"]) > 1:
            reasons.append("MULTIPLE_TARGET_COLUMNS")
        if group["kind"] == "regression" and not group["predictionColumns"]:
            reasons.append("PREDICTION_COLUMN_MISSING")
        if group["kind"] == "classification" and not (group["predictionColumns"] or group["probabilityColumns"]):
            reasons.append("CLASS_PREDICTION_OR_PROBABILITY_MISSING")
        if not group["targetColumns"]:
            reasons.append("TARGET_COLUMN_MISSING")
        if len(group["probabilityColumns"]) > MAX_PROBABILITY_COLUMNS:
            reasons.append("PROBABILITY_COLUMN_CAP_EXCEEDED")
        status = "AMBIGUOUS" if "MULTIPLE_TARGET_COLUMNS" in reasons else ("COMPLETE" if not reasons else "INCOMPLETE")
        result.append(
            {
                "groupId": group_id,
                **{key: sorted(value) if isinstance(value, list) else value for key, value in group.items()},
                "seriesBindings": series_bindings,
                "status": status,
                "reasons": reasons,
            }
        )
    return result


def _validate_probability_groups(groups: list[dict[str, Any]], sampled_rows: list[dict[str, Any]]) -> None:
    for group in groups:
        probability_columns = group["probabilityColumns"]
        if not probability_columns or len(probability_columns) > MAX_PROBABILITY_COLUMNS:
            continue
        checked = 0
        invalid = 0
        for row in sampled_rows:
            values: list[float] = []
            for column in probability_columns:
                value = row.get(column)
                if value is None:
                    values = []
                    break
                try:
                    number = float(value)
                except (TypeError, ValueError):
                    values = []
                    break
                if not math.isfinite(number):
                    values = []
                    break
                values.append(number)
            if not values:
                continue
            checked += 1
            if any(value < 0 or value > 1 for value in values) or abs(sum(values) - 1.0) > 1e-6:
                invalid += 1
        if checked and invalid:
            group["reasons"].append("PROBABILITY_ROWS_NOT_NORMALIZED")
            if group["status"] == "COMPLETE":
                group["status"] = "INCOMPLETE"


def resource_semantics(objects: Iterable[NormalizedObjectDraft]) -> list[dict[str, Any]]:
    ordered = sorted(objects, key=lambda item: (item.object_type.value, item.id))
    return [_resource_semantic(obj) for obj in ordered[:MAX_PROFILE_OBJECTS]]


def _resource_semantic(obj: NormalizedObjectDraft) -> dict[str, Any]:
    metadata = obj.metadata
    facts: dict[str, Any] = {"sourceFileIds": sorted(obj.source_file_ids)}
    capabilities: list[str] = []
    warnings: list[str] = []
    kind = obj.object_type.value.lower()
    if obj.object_type in {MaterialObjectType.Structure, MaterialObjectType.Atoms}:
        facts.update(
            {
                "formula": metadata.get("formula"),
                "elements": metadata.get("elements", []),
                "chemicalSystem": metadata.get("chemicalSystem"),
                "siteCount": metadata.get("nAtoms"),
                "periodicity": metadata.get("periodicity"),
                "latticeVolume": metadata.get("latticeVolume"),
                "density": metadata.get("density"),
            }
        )
        capabilities.extend(["composition", "structure"] if obj.object_type == MaterialObjectType.Structure else ["composition"])
    elif obj.object_type == MaterialObjectType.DataFrame:
        facts.update({"rowCount": metadata.get("nRows"), "columnCount": metadata.get("nColumns")})
        capabilities.append("table")
    elif obj.object_type == MaterialObjectType.Trajectory:
        summary = metadata.get("trajectorySummary", {})
        properties = sorted(str(value) for value in summary.get("properties", []))
        facts.update(
            {
                "frameCount": summary.get("frameCount"),
                "atomCount": summary.get("atomCount"),
                "coordinateMode": summary.get("coordinateMode"),
                "latticeMode": summary.get("latticeMode"),
                "properties": properties,
                "timeAvailable": _trajectory_time_available(obj.payload),
                "positionWrapping": obj.payload.get("position_wrapping") if isinstance(obj.payload, dict) else None,
            }
        )
        capabilities.append("trajectory")
    elif obj.object_type in {MaterialObjectType.PhononBand, MaterialObjectType.PhononDos, MaterialObjectType.PhononEigenvector}:
        facts.update({key: metadata.get(key) for key in sorted(metadata) if key in {"qPointCount", "frequencyCount", "projected", "imaginaryFrequencyCount"}})
        capabilities.append("phonon")
    elif obj.object_type == MaterialObjectType.VolumetricData:
        payload = obj.payload if isinstance(obj.payload, dict) else {}
        channels = payload.get("channels", []) if isinstance(payload.get("channels", []), list) else []
        facts.update(
            {
                "gridShape": metadata.get("gridShape") or payload.get("shape"),
                "fieldCount": metadata.get("fieldCount", len(channels)),
                "sourceFormat": metadata.get("detectedFormat") or payload.get("source_format"),
                "quantities": sorted(
                    str(channel.get("quantity")) for channel in channels if isinstance(channel, dict) and channel.get("quantity")
                ),
                "structureBound": bool(payload.get("structure_sha256") or payload.get("structure_hash")),
            }
        )
        capabilities.append("volumetric")
    return {
        "objectId": obj.id,
        "objectType": obj.object_type.value,
        "objectHash": obj.hash,
        "kind": kind,
        "facts": {key: value for key, value in facts.items() if value is not None},
        "capabilities": sorted(set(capabilities)),
        "warnings": warnings,
    }


def analysis_readiness(
    semantic_columns: list[dict[str, Any]],
    semantic_groups: list[dict[str, Any]],
    resources: list[dict[str, Any]],
    platform_tool_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    roles = {role["role"] for column in semantic_columns for role in column["roles"]}
    resource_capabilities = {capability for resource in resources for capability in resource["capabilities"]}
    effective_semantics = roles | resource_capabilities
    effective_semantics.add("profile_2")
    if {"classification_prediction", "class_probability"} & roles:
        effective_semantics.add("classification_output")
    parseable_formula = any(
        role["role"] == "material_formula" and int(role["details"].get("validCount", 0)) > 0
        for column in semantic_columns
        for role in column["roles"]
    )
    composition_available = parseable_formula or "composition" in resource_capabilities
    numeric_column_count = _numeric_column_count(semantic_columns)
    regression_groups = [group for group in semantic_groups if group["kind"] == "regression"]
    classification_groups = [group for group in semantic_groups if group["kind"] == "classification"]
    rules: list[tuple[str, set[str], bool, list[dict[str, Any]]]] = [
        ("dataset_materials_explorer", {"profile_2"}, bool(semantic_columns or resources), []),
        ("table_distribution", {"table"}, "table" in resource_capabilities, []),
        ("scatter", {"table"}, "table" in resource_capabilities and numeric_column_count >= 2, []),
        ("histogram", {"table"}, "table" in resource_capabilities and numeric_column_count >= 1, []),
        ("correlation", {"table"}, "table" in resource_capabilities and numeric_column_count >= 2, []),
        ("composition_summary", {"material_formula"}, composition_available, []),
        ("formula_statistics", {"material_formula"}, composition_available, []),
        ("element_distribution", {"material_formula"}, composition_available, []),
        ("chemical_system_visualization", {"material_formula"}, composition_available, []),
        ("structure_summary", {"structure"}, "structure" in resource_capabilities, []),
        ("trajectory_visualization", {"trajectory"}, "trajectory" in resource_capabilities, []),
        ("phonon_visualization", {"phonon"}, "phonon" in resource_capabilities, []),
        ("volumetric_visualization", {"volumetric"}, "volumetric" in resource_capabilities, []),
        ("regression_evaluation", {"regression_target", "regression_prediction"}, any(group["status"] == "COMPLETE" for group in regression_groups), regression_groups),
        ("uncertainty_evaluation", {"regression_target", "regression_prediction", "regression_uncertainty"}, any(group["status"] == "COMPLETE" and group["uncertaintyColumns"] for group in regression_groups), regression_groups),
        ("classification_evaluation", {"classification_target", "classification_output"}, any(group["status"] == "COMPLETE" for group in classification_groups), classification_groups),
        ("composition_space", {"material_formula"}, composition_available, []),
        ("dataset_structure_statistics", {"structure"}, "structure" in resource_capabilities, []),
    ]
    results: list[dict[str, Any]] = []
    for capability, required, ready, related_groups in rules:
        ambiguous_groups = [group for group in related_groups if group["status"] == "AMBIGUOUS"]
        if ambiguous_groups:
            data_status = "AMBIGUOUS"
            reasons = sorted({reason for group in ambiguous_groups for reason in group["reasons"]})
        elif ready:
            data_status = "READY"
            reasons = ["DATA_REQUIREMENTS_SATISFIED"]
        elif not semantic_columns and not resource_capabilities:
            data_status = "UNSUPPORTED_DATA_KIND"
            reasons = ["NO_SUPPORTED_PROFILE_RESOURCE"]
        else:
            data_status = "MISSING_REQUIRED_DATA"
            related_reasons = sorted({reason for group in related_groups for reason in group["reasons"]})
            if related_reasons:
                reasons = related_reasons
            elif capability in {
                "composition_summary",
                "formula_statistics",
                "element_distribution",
                "chemical_system_visualization",
                "composition_space",
            } and "material_formula" in roles:
                reasons = ["NO_PARSEABLE_FORMULA_VALUES"]
            elif capability in {"scatter", "correlation"} and numeric_column_count < 2:
                reasons = ["MISSING:two_finite_numeric_columns"]
            elif capability == "histogram" and numeric_column_count < 1:
                reasons = ["MISSING:finite_numeric_column"]
            else:
                reasons = [f"MISSING:{value}" for value in sorted(required - effective_semantics)] or ["NO_COMPLETE_SEMANTIC_GROUP"]
        if platform_tool_ids is None:
            platform_status = "NOT_EVALUATED"
        else:
            registered_candidates = _PLATFORM_TOOLS.get(capability, ())
            platform_status = "AVAILABLE" if any(tool_id in platform_tool_ids for tool_id in registered_candidates) else "NOT_IMPLEMENTED"
        results.append(
            {
                "capability": capability,
                "dataStatus": data_status,
                "platformStatus": platform_status,
                "reasons": reasons,
                "requiredSemantics": sorted(required),
                "matchingGroups": sorted(group["groupId"] for group in related_groups),
            }
        )
    return results


def sample_identity(semantic_columns: list[dict[str, Any]], dataframe_objects: list[NormalizedObjectDraft]) -> dict[str, Any] | None:
    if not dataframe_objects:
        return None
    explicit_columns = sorted(
        (
            column
            for column in semantic_columns
            if any(role["role"] == "sample_identity" for role in column["roles"])
        ),
        key=lambda column: column["column"],
    )
    valid_explicit_columns = [
        column
        for column in explicit_columns
        if column["missingCount"] == 0
        and column["totalRows"] > 0
        and column["uniqueCount"] == column["totalRows"]
    ]
    explicit_column = valid_explicit_columns[0]["column"] if len(valid_explicit_columns) == 1 else None
    return {
        "policy": "explicit_column" if explicit_column is not None else "object_hash_row_index",
        "explicitColumn": explicit_column,
        "fallbackPolicy": "dataset_version_object_hash_row_index",
        "datasetVersion": "2",
        "objectIds": sorted(obj.id for obj in dataframe_objects),
    }


def stable_sample_reference(*, dataset_id: str, dataset_version: str, object_hash: str, row_index: int) -> str:
    if row_index < 0:
        raise ValueError("row_index must be non-negative.")
    return f"{dataset_id}@{dataset_version}:{object_hash[:16]}:{row_index}"


def _allowed_explicit_roles() -> set[str]:
    return {
        "material_formula",
        "sample_identity",
        "regression_target",
        "regression_prediction",
        "regression_uncertainty",
        "classification_target",
        "classification_prediction",
        "class_probability",
        "material_property",
    }


def _bounded_indices(total: int, limit: int) -> list[int]:
    if total <= limit:
        return list(range(max(0, total)))
    if limit <= 1:
        return [0]
    return [(index * (total - 1)) // (limit - 1) for index in range(limit)]


def _finite_counts(values: list[Any]) -> tuple[int, int]:
    finite = 0
    non_finite = 0
    for value in values:
        if value is None:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            non_finite += 1
            continue
        if math.isfinite(number):
            finite += 1
        else:
            non_finite += 1
    return finite, non_finite


def _formula_parseability(values: list[Any]) -> dict[str, Any]:
    valid = 0
    invalid = 0
    inspected = 0
    too_long = 0
    for value in values[:MAX_FORMULA_VALUES]:
        if value is None or str(value).strip() == "":
            continue
        inspected += 1
        if len(str(value)) > MAX_FORMULA_LENGTH:
            too_long += 1
            invalid += 1
            continue
        try:
            Composition(str(value))
            valid += 1
        except (TypeError, ValueError):
            invalid += 1
    return {"validCount": valid, "invalidCount": invalid, "inspectedCount": inspected, "tooLongCount": too_long}


def _numeric_column_count(columns: list[dict[str, Any]]) -> int:
    return sum(1 for column in columns if column["dtype"] == "number" and (column["finiteCount"] or 0) > 0)


def _trajectory_time_available(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    if payload.get("time") is not None or payload.get("timestep") is not None:
        return True
    frames = payload.get("frames")
    return bool(isinstance(frames, list) and frames and isinstance(frames[0], dict) and "time" in frames[0])
