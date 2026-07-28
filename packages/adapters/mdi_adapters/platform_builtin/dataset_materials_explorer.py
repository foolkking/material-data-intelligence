from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping

import numpy as np
import pandas as pd
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from mdi_artifact_core import ArtifactPayload, content_hash, stable_json_dumps
from mdi_material_parsers import stable_sample_reference
from mdi_schemas import Artifact, ArtifactType, DataProfile

from ..base import BaseToolAdapter
from ..composition_common import ParsedFormula, PreparedCompositionTable, formula_statistics, parse_formula
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from ..ml_common import coerce_dataframe
from .structure import _structure_from_normalized_dict


DATASET_EXPLORER_SCHEMA_VERSION = "phase10k2.dataset_materials_explorer.v1"
DATASET_EXPLORER_TOOL_ID = "dataset.materials_explorer"


@dataclass(frozen=True)
class PreparedDatasetExplorer:
    profile: DataProfile
    tables: Mapping[str, pd.DataFrame]
    structures: Mapping[str, Structure]


@dataclass(frozen=True)
class DatasetExplorerResult:
    payload: dict[str, Any]
    params: dict[str, Any]


class DatasetMaterialsExplorerAdapter(BaseToolAdapter):
    tool_id = DATASET_EXPLORER_TOOL_ID
    adapter_version = "0.1.0"

    def prepare(
        self,
        context: ToolExecutionContext,
        input_refs: list[Any],
        params: dict[str, Any],
    ) -> PreparedDatasetExplorer:
        if not self._resolved_inputs:
            raise _input_error("A Profile 2.0 input is required.", "missing_profile")

        profile: DataProfile | None = None
        tables: dict[str, pd.DataFrame] = {}
        structures: dict[str, Structure] = {}
        structure_ids = [
            item.objectId for item in _profile_resources_from_values(self._resolved_inputs) if item.objectType == "Structure"
        ]

        for index, value in enumerate(self._resolved_inputs):
            ref = str(_ref_value(input_refs[index], "ref", f"input_{index}")) if index < len(input_refs) else f"input_{index}"
            candidate = _coerce_profile(value)
            if candidate is not None:
                if profile is not None:
                    raise _input_error("Exactly one Profile 2.0 input is allowed.", "multiple_profiles")
                profile = candidate
                continue
            if ref == "structure_resources" and isinstance(value, Mapping):
                for object_id, raw_structure in sorted(value.items(), key=lambda item: str(item[0])):
                    structures[str(object_id)] = _coerce_structure(raw_structure)
                continue
            if isinstance(value, (list, tuple)) and value and all(_looks_like_structure(item) for item in value):
                for item_index, raw_structure in enumerate(value):
                    object_id = structure_ids[item_index] if item_index < len(structure_ids) else f"structure_{item_index + 1}"
                    structures[object_id] = _coerce_structure(raw_structure)
                continue
            if isinstance(value, pd.DataFrame) or _looks_like_table(value):
                tables[ref] = coerce_dataframe(value, tool_id=self.tool_id)
                continue
            if _looks_like_structure(value):
                structures[ref] = _coerce_structure(value)
                continue
            raise _input_error("Dataset explorer received an unsupported input reference.", "unsupported_input", ref=ref)

        if profile is None or profile.profileContractVersion != "2.0":
            raise _input_error("Dataset explorer requires Material Data Profile 2.0.", "profile_contract_unsupported")
        if profile.datasetId != context.dataset_id:
            raise _input_error("Profile dataset identity does not match the execution context.", "profile_dataset_mismatch")
        if not tables and not structures:
            raise _input_error("Profile has no resolved table or structure resources.", "missing_material_resources")

        known_object_ids = {item.objectId for item in profile.resourceSemantics}
        for object_id in (*tables, *structures):
            if object_id not in known_object_ids and object_id not in {"ml_table", "structures", "structure_resources"}:
                raise _input_error("Resolved object is not declared by Profile 2.0.", "object_not_profiled", objectId=object_id)
        return PreparedDatasetExplorer(profile=profile, tables=tables, structures=structures)

    def run(self, prepared: PreparedDatasetExplorer, params: dict[str, Any]) -> DatasetExplorerResult:
        limits = self.context.resource_limits
        max_rows = int(limits.get("maxRows", 100000))
        max_columns = int(limits.get("maxColumns", 512))
        max_structures = min(int(params.get("maxStructures") or 256), int(limits.get("maxStructures", 256)))
        max_properties = min(int(params.get("maxProperties") or 32), int(limits.get("maxProperties", 64)))
        max_categories = min(int(params.get("maxCategories") or 50), int(limits.get("maxCategories", 256)))
        max_table_rows = min(int(params.get("maxTableRows") or 100), int(limits.get("maxTableRows", 200)))
        histogram_bins = min(int(params.get("histogramBins") or 20), int(limits.get("maxHistogramBins", 100)))
        warnings: list[str] = []

        for object_id, table in prepared.tables.items():
            if len(table) > max_rows:
                raise _resource_error("Table exceeds the dataset explorer row cap.", objectId=object_id, rows=len(table), maxRows=max_rows)
            if len(table.columns) > max_columns:
                raise _resource_error(
                    "Table exceeds the dataset explorer column cap.",
                    objectId=object_id,
                    columns=len(table.columns),
                    maxColumns=max_columns,
                )
        if len(prepared.structures) > max_structures:
            raise _resource_error(
                "Structure collection exceeds the requested dataset explorer cap.",
                structures=len(prepared.structures),
                maxStructures=max_structures,
            )
        max_atoms = int(limits.get("maxAtomsPerStructure", 5000))
        for object_id, structure in prepared.structures.items():
            if len(structure) > max_atoms:
                raise _resource_error(
                    "Structure exceeds the dataset explorer atom cap.",
                    objectId=object_id,
                    sites=len(structure),
                    maxAtomsPerStructure=max_atoms,
                )

        table_id = _select_primary_table(prepared.profile, prepared.tables, params.get("tableObjectId"))
        table = prepared.tables.get(table_id) if table_id else None
        composition = _composition_summary(prepared.profile, table_id, table, max_examples=max_categories)
        warnings.extend(composition.pop("_warnings", []))
        properties = _property_summary(
            prepared.profile,
            table_id,
            table,
            max_properties=max_properties,
            histogram_bins=histogram_bins,
        )
        warnings.extend(properties.pop("_warnings", []))
        structures = _structure_summary(prepared.profile, prepared.structures, symprec=float(params.get("symprec") or 0.01))
        warnings.extend(structures.pop("_warnings", []))
        sample_index = _sample_index(
            prepared.profile,
            table_id,
            table,
            composition.get("formulaColumn"),
            [item["column"] for item in properties["properties"]],
            max_rows=max_table_rows,
        )
        quality = _quality_summary(prepared.profile, table_id, table, composition, sample_index)
        comparison = _comparison_summary(
            prepared.profile,
            prepared.tables,
            table_id,
            params,
            max_properties=max_properties,
            max_categories=max_categories,
        )
        warnings.extend(comparison.pop("_warnings", []))
        warnings.extend(str(issue.get("code")) for issue in prepared.profile.qualityIssues if issue.get("code"))
        warnings = _bounded_unique(warnings, int(limits.get("maxWarnings", 128)))

        row_count = int(len(table)) if table is not None else len(prepared.structures)
        resource_bindings = [
            {"objectId": item.objectId, "objectType": item.objectType, "objectHash": item.objectHash}
            for item in sorted(prepared.profile.resourceSemantics, key=lambda item: item.objectId)
        ]
        payload = {
            "schemaVersion": DATASET_EXPLORER_SCHEMA_VERSION,
            "artifactType": self.tool_id,
            "dataset": {
                "datasetId": prepared.profile.datasetId,
                "datasetVersion": prepared.profile.version,
                "profileId": prepared.profile.profileId,
                "profileContractVersion": prepared.profile.profileContractVersion,
                "semanticHash": prepared.profile.semanticHash,
                "datasetContentHash": content_hash(resource_bindings),
                "datasetType": prepared.profile.datasetType,
                "primaryTableObjectId": table_id,
                "resourceBindings": resource_bindings,
            },
            "overview": {
                "sampleCount": row_count,
                "tableCount": len(prepared.tables),
                "structureCount": len(prepared.structures),
                "formulaCoverage": composition.get("coverage"),
                "propertyCount": len(properties["properties"]),
                "availableAnalyses": [
                    item.capability
                    for item in prepared.profile.analysisReadiness
                    if item.dataStatus == "READY" and item.platformStatus == "AVAILABLE"
                ],
                "unavailableAnalyses": [
                    item.capability
                    for item in prepared.profile.analysisReadiness
                    if item.dataStatus != "READY" or item.platformStatus != "AVAILABLE"
                ],
            },
            "composition": composition,
            "structures": structures,
            "properties": properties,
            "quality": quality,
            "comparison": comparison,
            "sampleIndex": sample_index,
            "coverage": prepared.profile.profileCoverage.model_dump(mode="json") if prepared.profile.profileCoverage else None,
            "warnings": warnings,
            "limits": {
                "maxRows": max_rows,
                "maxColumns": max_columns,
                "maxProperties": max_properties,
                "maxCategories": max_categories,
                "maxTableRows": max_table_rows,
                "histogramBins": histogram_bins,
                "maxStructures": max_structures,
                "maxAtomsPerStructure": max_atoms,
            },
            "semantics": {
                "source": "material_data_profile_2",
                "roleInferenceRepeated": False,
                "comparisonRequiresExplicitBinding": True,
                "nearDuplicateInference": False,
                "outlierPolicy": "iqr_1_5_statistical_candidate_only",
            },
            "security": {
                "artifactJavaScript": False,
                "externalUrls": False,
                "externalAssets": False,
                "executableContent": False,
            },
        }
        return DatasetExplorerResult(payload=payload, params=dict(params))

    def export(self, result: DatasetExplorerResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        requested = set(artifact_types) or {
            ArtifactType.table_json,
            ArtifactType.quality_issues_json,
            ArtifactType.summary_md,
            ArtifactType.recipe_json,
        }
        payloads: list[ArtifactPayload] = []
        if ArtifactType.table_json in requested:
            payloads.append(_json_payload(ArtifactType.table_json, "dataset_materials_explorer.json", result.payload))
        if ArtifactType.quality_issues_json in requested:
            payloads.append(_json_payload(ArtifactType.quality_issues_json, "dataset_quality.json", result.payload["quality"]))
        if ArtifactType.summary_md in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=_summary_markdown(result.payload),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in requested:
            recipe = self.recipe_payload(
                name="Dataset Materials Explorer",
                params=result.params,
                artifact_types=sorted(requested, key=lambda item: item.value),
            )
            recipe["profileBinding"] = {
                "profileId": result.payload["dataset"]["profileId"],
                "semanticHash": result.payload["dataset"]["semanticHash"],
                "roleInferenceRepeated": False,
            }
            payloads.append(_json_payload(ArtifactType.recipe_json, "recipe.json", recipe))

        max_bytes = int(self.context.resource_limits.get("maxArtifactBytes", 8000000))
        for payload in payloads:
            size = len(payload.content.encode("utf-8")) if isinstance(payload.content, str) else len(stable_json_dumps(payload.content).encode("utf-8"))
            if size > max_bytes:
                raise _resource_error("Dataset explorer artifact exceeds the byte cap.", artifact=payload.file_name, bytes=size, maxArtifactBytes=max_bytes)
        return self.export_payloads(
            payloads,
            provenance={
                "sourceFunction": "platform_builtin.dataset_materials_explorer",
                "profileContractVersion": "2.0",
                "semanticHash": result.payload["dataset"]["semanticHash"],
                "deterministic": True,
            },
        )


def _coerce_profile(value: Any) -> DataProfile | None:
    if isinstance(value, DataProfile):
        return value
    if isinstance(value, Mapping) and value.get("profileContractVersion") is not None:
        try:
            return DataProfile.model_validate(value)
        except Exception as exc:
            raise _input_error("Profile 2.0 input is invalid.", "profile_validation_failed") from exc
    return None


def _profile_resources_from_values(values: list[Any]) -> list[Any]:
    for value in values:
        profile = _coerce_profile(value)
        if profile is not None:
            return list(profile.resourceSemantics)
    return []


def _looks_like_table(value: Any) -> bool:
    return isinstance(value, list) and (not value or all(isinstance(item, Mapping) for item in value))


def _looks_like_structure(value: Any) -> bool:
    return isinstance(value, Structure) or isinstance(value, Mapping) and (
        "lattice" in value or {"species", "coords"}.issubset(value)
    )


def _coerce_structure(value: Any) -> Structure:
    if isinstance(value, Structure):
        return value.copy()
    if isinstance(value, Mapping):
        try:
            return Structure.from_dict(dict(value))
        except Exception:
            return _structure_from_normalized_dict(dict(value), tool_id=DATASET_EXPLORER_TOOL_ID)
    raise _input_error("Structure resource is invalid.", "invalid_structure_resource")


def _select_primary_table(profile: DataProfile, tables: Mapping[str, pd.DataFrame], requested: Any) -> str | None:
    if not tables:
        return None
    if requested is not None:
        requested_id = str(requested)
        if requested_id not in tables:
            raise _input_error("Requested tableObjectId was not resolved.", "table_object_missing", objectId=requested_id)
        return requested_id
    profiled = sorted({column.objectId for column in profile.semanticColumns if column.objectId in tables})
    return profiled[0] if profiled else sorted(tables)[0]


def _semantic_columns(profile: DataProfile, object_id: str | None, role: str) -> list[Any]:
    if object_id is None:
        return []
    return sorted(
        [
            column
            for column in profile.semanticColumns
            if column.objectId == object_id and any(item.role == role for item in column.roles)
        ],
        key=lambda item: item.column,
    )


def _composition_summary(
    profile: DataProfile,
    object_id: str | None,
    table: pd.DataFrame | None,
    *,
    max_examples: int,
) -> dict[str, Any]:
    columns = _semantic_columns(profile, object_id, "material_formula")
    if table is None or len(columns) != 1 or columns[0].column not in table.columns:
        warning = "DATASET_FORMULA_SEMANTICS_UNAVAILABLE" if not columns else "DATASET_FORMULA_SEMANTICS_AMBIGUOUS"
        return {
            "status": "UNAVAILABLE",
            "formulaColumn": None,
            "coverage": {"total": int(len(table)) if table is not None else 0, "valid": 0, "invalid": 0},
            "elements": [],
            "chemicalSystems": [],
            "duplicateReducedFormulaGroups": [],
            "_warnings": [warning],
        }
    formula_column = columns[0].column
    values = table[formula_column]
    prepared = PreparedCompositionTable(
        frame=table,
        formulas=[str(value).strip() for value in values.dropna().tolist() if str(value).strip()],
        formula_column=formula_column,
        row_count=int(len(table)),
    )
    try:
        stats = formula_statistics(prepared, {"maxExamples": max_examples}, tool_id=DATASET_EXPLORER_TOOL_ID)
    except ToolExecutionError:
        return {
            "status": "UNAVAILABLE",
            "formulaColumn": formula_column,
            "coverage": {"total": int(len(table)), "valid": 0, "invalid": int(values.notna().sum())},
            "elements": [],
            "chemicalSystems": [],
            "duplicateReducedFormulaGroups": [],
            "_warnings": ["DATASET_FORMULAS_ALL_INVALID"],
        }
    containing = Counter(element for item in stats.parsed for element in item.elements)
    element_rows = [
        {
            "element": element,
            "materialsContainingElement": int(containing[element]),
            "stoichiometricSum": float(stats.payload["elementCounts"][element]),
            "fractionalSum": float(stats.payload["elementFractionalSums"][element]),
        }
        for element in sorted(containing)
    ]
    systems = [
        {"chemicalSystem": key, "count": int(value)}
        for key, value in sorted(stats.payload["chemicalSystems"].items(), key=lambda item: (-item[1], item[0]))
    ]
    reduced_rows: dict[str, list[int]] = defaultdict(list)
    parsed_by_row: dict[int, ParsedFormula] = {}
    for row_index, value in enumerate(values.tolist()):
        if pd.isna(value):
            continue
        parsed = parse_formula(value)
        if parsed.is_valid:
            parsed_by_row[row_index] = parsed
            reduced_rows[parsed.reduced_formula].append(row_index)
    duplicate_groups = [
        {"reducedFormula": formula, "count": len(indices), "rowIndices": indices[:max_examples]}
        for formula, indices in sorted(reduced_rows.items())
        if len(indices) > 1
    ]
    warnings = ["DATASET_FORMULA_PARSE_FAILURES"] if stats.failed else []
    if len(systems) > max_examples or len(duplicate_groups) > max_examples:
        warnings.append("DATASET_COMPOSITION_CATEGORY_CAP_APPLIED")
    return {
        "status": "READY",
        "formulaColumn": formula_column,
        "coverage": {
            "total": int(len(table)),
            "nonNull": int(values.notna().sum()),
            "valid": len(parsed_by_row),
            "invalid": int(values.notna().sum()) - len(parsed_by_row),
        },
        "elements": element_rows,
        "chemicalSystems": systems[:max_examples],
        "systemTypeCounts": stats.payload["systemTypeCounts"],
        "uniqueFormulaCount": stats.payload["uniqueFormulaCount"],
        "uniqueReducedFormulaCount": stats.payload["uniqueReducedFormulaCount"],
        "duplicateReducedFormulaGroups": duplicate_groups[:max_examples],
        "failedExamples": stats.payload["failedExamples"],
        "_warnings": warnings,
    }


def _property_summary(
    profile: DataProfile,
    object_id: str | None,
    table: pd.DataFrame | None,
    *,
    max_properties: int,
    histogram_bins: int,
) -> dict[str, Any]:
    columns = _semantic_columns(profile, object_id, "material_property")
    warnings: list[str] = []
    if len(columns) > max_properties:
        warnings.append("DATASET_PROPERTY_CAP_APPLIED")
        columns = columns[:max_properties]
    records: list[dict[str, Any]] = []
    for column in columns:
        if table is None or column.column not in table.columns:
            continue
        numeric = pd.to_numeric(table[column.column], errors="coerce")
        finite = numeric[np.isfinite(numeric)]
        missing_count = int(table[column.column].isna().sum())
        nonfinite_count = int((numeric.notna() & ~np.isfinite(numeric)).sum())
        if finite.empty:
            records.append(
                {
                    "column": column.column,
                    "unit": column.unit,
                    "count": 0,
                    "missingCount": missing_count,
                    "nonFiniteCount": nonfinite_count,
                    "statistics": None,
                    "histogram": None,
                    "outlierCandidates": [],
                }
            )
            continue
        q1, median, q3 = [float(value) for value in finite.quantile([0.25, 0.5, 0.75]).tolist()]
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outlier_indices = [int(index) for index, value in finite.items() if float(value) < low or float(value) > high]
        counts, edges = np.histogram(finite.to_numpy(dtype=float), bins=min(histogram_bins, max(1, len(finite))))
        records.append(
            {
                "column": column.column,
                "unit": column.unit,
                "count": int(len(finite)),
                "missingCount": missing_count,
                "nonFiniteCount": nonfinite_count,
                "statistics": {
                    "min": float(finite.min()),
                    "q1": q1,
                    "median": median,
                    "q3": q3,
                    "max": float(finite.max()),
                    "mean": float(finite.mean()),
                    "std": float(finite.std(ddof=1)) if len(finite) > 1 else 0.0,
                },
                "histogram": {"binEdges": [float(value) for value in edges], "counts": [int(value) for value in counts]},
                "outlierCandidates": outlier_indices[:100],
                "outlierPolicy": "iqr_1_5_statistical_candidate_only",
            }
        )
    return {"status": "READY" if records else "UNAVAILABLE", "properties": records, "_warnings": warnings}


def _structure_summary(profile: DataProfile, structures: Mapping[str, Structure], *, symprec: float) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    for object_id, structure in sorted(structures.items()):
        lattice = structure.lattice
        try:
            analyzer = SpacegroupAnalyzer(structure, symprec=symprec, angle_tolerance=5.0)
            spacegroup = analyzer.get_space_group_symbol()
            spacegroup_number = int(analyzer.get_space_group_number())
            crystal_system = analyzer.get_crystal_system()
        except Exception:
            spacegroup = None
            spacegroup_number = None
            crystal_system = None
            warnings.append("DATASET_STRUCTURE_SYMMETRY_UNAVAILABLE")
        rows.append(
            {
                "objectId": object_id,
                "formula": structure.composition.reduced_formula,
                "siteCount": len(structure),
                "volumeAngstrom3": float(lattice.volume),
                "densityGramCm3": float(structure.density),
                "lattice": {
                    "a": float(lattice.a),
                    "b": float(lattice.b),
                    "c": float(lattice.c),
                    "alpha": float(lattice.alpha),
                    "beta": float(lattice.beta),
                    "gamma": float(lattice.gamma),
                },
                "spacegroup": spacegroup,
                "spacegroupNumber": spacegroup_number,
                "crystalSystem": crystal_system,
            }
        )
    hash_groups: dict[str, list[str]] = defaultdict(list)
    for resource in profile.resourceSemantics:
        if resource.objectType == "Structure":
            hash_groups[resource.objectHash].append(resource.objectId)
    duplicates = [
        {"objectHash": key, "objectIds": sorted(values), "count": len(values)}
        for key, values in sorted(hash_groups.items())
        if len(values) > 1
    ]
    return {
        "status": "READY" if rows else "UNAVAILABLE",
        "structureCount": len(rows),
        "records": rows,
        "distributions": {
            "siteCount": _finite_distribution([row["siteCount"] for row in rows]),
            "volumeAngstrom3": _finite_distribution([row["volumeAngstrom3"] for row in rows]),
            "densityGramCm3": _finite_distribution([row["densityGramCm3"] for row in rows]),
            "spacegroups": _value_counts([row["spacegroup"] for row in rows if row["spacegroup"]]),
            "crystalSystems": _value_counts([row["crystalSystem"] for row in rows if row["crystalSystem"]]),
        },
        "exactStructureDuplicateGroups": duplicates,
        "duplicatePolicy": "equal canonical normalized object hash only",
        "_warnings": warnings,
    }


def _sample_index(
    profile: DataProfile,
    object_id: str | None,
    table: pd.DataFrame | None,
    formula_column: Any,
    property_columns: list[str],
    *,
    max_rows: int,
) -> list[dict[str, Any]]:
    if table is None or object_id is None:
        return []
    object_hash = next((item.objectHash for item in profile.resourceSemantics if item.objectId == object_id), profile.semanticHash or "unknown")
    identity_column = profile.sampleIdentity.explicitColumn if profile.sampleIdentity and profile.sampleIdentity.policy == "explicit_column" else None
    records: list[dict[str, Any]] = []
    for row_index, (_, row) in enumerate(table.head(max_rows).iterrows()):
        if identity_column and identity_column in table.columns:
            sample_ref = str(row.get(identity_column))
            identity_source = "explicit_column"
        else:
            sample_ref = stable_sample_reference(
                dataset_id=profile.datasetId,
                dataset_version=profile.version,
                object_hash=object_hash,
                row_index=row_index,
            )
            identity_source = "dataset_version_object_hash_row_index"
        formula = row.get(formula_column) if isinstance(formula_column, str) and formula_column in table.columns else None
        parsed = parse_formula(formula) if formula is not None and not pd.isna(formula) else None
        records.append(
            {
                "sampleRef": sample_ref,
                "identitySource": identity_source,
                "objectId": object_id,
                "rowIndex": row_index,
                "formula": None if formula is None or pd.isna(formula) else str(formula),
                "reducedFormula": parsed.reduced_formula if parsed and parsed.is_valid else None,
                "properties": {column: _finite_or_none(row.get(column)) for column in property_columns},
            }
        )
    return records


def _quality_summary(
    profile: DataProfile,
    object_id: str | None,
    table: pd.DataFrame | None,
    composition: Mapping[str, Any],
    sample_index: list[dict[str, Any]],
) -> dict[str, Any]:
    semantic_columns = [column for column in profile.semanticColumns if column.objectId == object_id]
    duplicate_ids: list[dict[str, Any]] = []
    if table is not None:
        for column in _semantic_columns(profile, object_id, "sample_identity"):
            if column.column not in table.columns:
                continue
            counts = table[column.column].dropna().astype(str).value_counts()
            duplicate_ids.extend(
                {"column": column.column, "value": str(value), "count": int(count)}
                for value, count in counts.items()
                if int(count) > 1
            )
    return {
        "profileIssues": list(profile.qualityIssues),
        "columnIssues": [
            {
                "column": column.column,
                "missingCount": column.missingCount,
                "nonFiniteCount": column.nonFiniteCount,
                "ambiguities": list(column.ambiguities),
            }
            for column in semantic_columns
            if column.missingCount or column.nonFiniteCount or column.ambiguities
        ],
        "invalidFormulaCount": int((composition.get("coverage") or {}).get("invalid", 0)),
        "duplicateSampleIdentityValues": sorted(duplicate_ids, key=lambda item: (item["column"], item["value"])),
        "duplicateReducedFormulaGroups": list(composition.get("duplicateReducedFormulaGroups") or []),
        "sampleLinksMaterialized": len(sample_index),
        "nearDuplicateAnalysis": "NOT_IMPLEMENTED_BY_DESIGN",
    }


def _comparison_summary(
    profile: DataProfile,
    tables: Mapping[str, pd.DataFrame],
    primary_id: str | None,
    params: Mapping[str, Any],
    *,
    max_properties: int,
    max_categories: int,
) -> dict[str, Any]:
    mode = str(params.get("comparisonMode") or "none")
    if mode == "none":
        return {"status": "NOT_REQUESTED", "mode": "none", "_warnings": []}
    if mode == "group":
        if primary_id is None or primary_id not in tables:
            raise _input_error("Group comparison requires the primary table.", "comparison_table_missing")
        column = str(params.get("groupColumn") or "")
        if not column or column not in tables[primary_id].columns:
            raise _input_error("Group comparison requires an existing explicit groupColumn.", "comparison_group_column_missing")
        if "groupA" not in params or "groupB" not in params or params["groupA"] == params["groupB"]:
            raise _input_error("Group comparison requires two distinct explicit group values.", "comparison_groups_invalid")
        left = tables[primary_id][tables[primary_id][column] == params["groupA"]].copy()
        right = tables[primary_id][tables[primary_id][column] == params["groupB"]].copy()
        if left.empty or right.empty:
            raise _input_error("One or both explicit comparison groups are empty.", "comparison_group_empty")
        return _compare_frames(
            profile,
            primary_id,
            left,
            primary_id,
            right,
            labels=[str(params["groupA"]), str(params["groupB"])],
            mode="group",
            binding={"groupColumn": column, "groupA": params["groupA"], "groupB": params["groupB"]},
            max_properties=max_properties,
            max_categories=max_categories,
        )
    if mode == "resources":
        left_id = str(params.get("leftObjectId") or "")
        right_id = str(params.get("rightObjectId") or "")
        if not left_id or not right_id or left_id == right_id or left_id not in tables or right_id not in tables:
            raise _input_error("Resource comparison requires two distinct resolved table object IDs.", "comparison_resources_invalid")
        return _compare_frames(
            profile,
            left_id,
            tables[left_id],
            right_id,
            tables[right_id],
            labels=[left_id, right_id],
            mode="resources",
            binding={"leftObjectId": left_id, "rightObjectId": right_id},
            max_properties=max_properties,
            max_categories=max_categories,
        )
    raise _input_error("Unknown comparison mode.", "comparison_mode_invalid", mode=mode)


def _compare_frames(
    profile: DataProfile,
    left_id: str,
    left: pd.DataFrame,
    right_id: str,
    right: pd.DataFrame,
    *,
    labels: list[str],
    mode: str,
    binding: dict[str, Any],
    max_properties: int,
    max_categories: int,
) -> dict[str, Any]:
    left_composition = _composition_summary(profile, left_id, left, max_examples=max_categories)
    right_composition = _composition_summary(profile, right_id, right, max_examples=max_categories)
    left_elements = {item["element"] for item in left_composition.get("elements", [])}
    right_elements = {item["element"] for item in right_composition.get("elements", [])}
    left_properties = _property_summary(profile, left_id, left, max_properties=max_properties, histogram_bins=20)["properties"]
    right_properties = _property_summary(profile, right_id, right, max_properties=max_properties, histogram_bins=20)["properties"]
    left_by_name = {item["column"]: item for item in left_properties}
    right_by_name = {item["column"]: item for item in right_properties}
    property_rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    for name in sorted(set(left_by_name) & set(right_by_name)):
        left_item, right_item = left_by_name[name], right_by_name[name]
        comparable = left_item["unit"] == right_item["unit"]
        if not comparable:
            warnings.append(f"DATASET_COMPARISON_UNIT_MISMATCH:{name}")
        property_rows.append(
            {
                "column": name,
                "unit": left_item["unit"] if comparable else None,
                "comparable": comparable,
                "left": left_item["statistics"],
                "right": right_item["statistics"],
                "leftMissingCount": left_item["missingCount"],
                "rightMissingCount": right_item["missingCount"],
            }
        )
    return {
        "status": "READY",
        "mode": mode,
        "binding": binding,
        "labels": labels,
        "sampleCounts": {labels[0]: int(len(left)), labels[1]: int(len(right))},
        "elementOverlap": {
            "shared": sorted(left_elements & right_elements),
            "leftOnly": sorted(left_elements - right_elements),
            "rightOnly": sorted(right_elements - left_elements),
        },
        "propertyComparison": property_rows,
        "semantics": "explicitly bound groups/resources; no row-order inference",
        "_warnings": warnings,
    }


def _finite_distribution(values: list[Any]) -> dict[str, Any] | None:
    finite = [float(value) for value in values if _finite_or_none(value) is not None]
    if not finite:
        return None
    return {
        "count": len(finite),
        "min": min(finite),
        "median": float(np.median(finite)),
        "mean": float(np.mean(finite)),
        "max": max(finite),
    }


def _value_counts(values: list[Any]) -> list[dict[str, Any]]:
    counts = Counter(str(value) for value in values)
    return [{"value": value, "count": count} for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]


def _finite_or_none(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if isfinite(number) else None


def _bounded_unique(values: list[str], limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
        if len(result) == limit:
            break
    return result


def _json_payload(artifact_type: ArtifactType, file_name: str, content: Any) -> ArtifactPayload:
    return ArtifactPayload(
        artifact_type=artifact_type,
        file_name=file_name,
        content=stable_json_dumps(content),
        media_type="application/json",
    )


def _summary_markdown(payload: Mapping[str, Any]) -> str:
    dataset = payload["dataset"]
    overview = payload["overview"]
    composition = payload["composition"]
    structures = payload["structures"]
    comparison = payload["comparison"]
    return "\n".join(
        [
            "# Dataset Materials Explorer",
            "",
            f"- Dataset: `{dataset['datasetId']}`",
            f"- Profile: `{dataset['profileId']}` (contract {dataset['profileContractVersion']})",
            f"- Samples: {overview['sampleCount']}",
            f"- Structures: {structures['structureCount']}",
            f"- Formula coverage: {composition['status']}",
            f"- Material properties: {overview['propertyCount']}",
            f"- Comparison: {comparison['status']} ({comparison['mode']})",
            "",
            "All semantic roles come from Material Data Profile 2.0. Statistical outliers are candidates, not scientific diagnoses.",
        ]
    )


def _ref_value(input_ref: Any, field: str, default: Any = None) -> Any:
    if hasattr(input_ref, field):
        return getattr(input_ref, field)
    if isinstance(input_ref, Mapping):
        return input_ref.get(field, default)
    return default


def _input_error(message: str, error_type: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError(
        code="TOOL_INPUT_INVALID",
        message=message,
        tool_id=DATASET_EXPLORER_TOOL_ID,
        details={"errorType": error_type, **details},
    )


def _resource_error(message: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError(
        code="TOOL_RESOURCE_LIMIT",
        message=message,
        tool_id=DATASET_EXPLORER_TOOL_ID,
        details=details,
    )
