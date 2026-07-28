from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
from math import isfinite
from typing import Any, Mapping

import numpy as np
import pandas as pd
from pymatgen.core import Element
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from mdi_artifact_core import ArtifactPayload, content_hash, stable_json_dumps
from mdi_material_parsers import stable_sample_reference
from mdi_schemas import Artifact, ArtifactType, DataProfile

from ..base import BaseToolAdapter
from ..composition_common import ParsedFormula, parse_formula
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from ..ml_common import coerce_dataframe


COMPOSITION_SPACE_SCHEMA_VERSION = "phase10k4.composition_space.v1"
COMPOSITION_SPACE_TOOL_ID = "dataset.composition_space"
_ML_SCHEMA_PREFIXES = (
    "phase10k3.materials_ml_regression.",
    "phase10k3.materials_ml_uncertainty.",
)


@dataclass(frozen=True)
class PreparedCompositionSpace:
    profile: DataProfile
    tables: Mapping[str, pd.DataFrame]
    ml_artifacts: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class CompositionSpaceResult:
    payload: dict[str, Any]
    plot: dict[str, Any]
    params: dict[str, Any]


@dataclass(frozen=True)
class _Sample:
    sample_ref: str
    identity_source: str
    object_id: str
    row_index: int
    group: str
    parsed: ParsedFormula
    fractions: Mapping[str, float]
    properties: Mapping[str, float]


class CompositionSpaceAdapter(BaseToolAdapter):
    tool_id = COMPOSITION_SPACE_TOOL_ID
    adapter_version = "0.1.0"

    def prepare(
        self,
        context: ToolExecutionContext,
        input_refs: list[Any],
        params: dict[str, Any],
    ) -> PreparedCompositionSpace:
        profile: DataProfile | None = None
        tables: dict[str, pd.DataFrame] = {}
        ml_artifacts: list[Mapping[str, Any]] = []
        for index, value in enumerate(self._resolved_inputs):
            ref = str(_ref_value(input_refs[index], "ref", f"input_{index}"))
            candidate = _coerce_profile(value)
            if candidate is not None:
                if profile is not None:
                    raise _input_error("Exactly one Profile 2.0 input is allowed.", "multiple_profiles")
                profile = candidate
            elif _is_supported_ml_artifact(value):
                encoded_size = len(stable_json_dumps(value).encode("utf-8"))
                if encoded_size > int(context.resource_limits.get("maxArtifactBytes", 16_000_000)):
                    raise _resource_error("Bound ML artifact exceeds the byte cap.", bytes=encoded_size)
                ml_artifacts.append(value)
            elif isinstance(value, pd.DataFrame) or _looks_like_table(value):
                tables[ref] = coerce_dataframe(value, tool_id=self.tool_id).reset_index(drop=True)
            else:
                raise _input_error("Composition space received an unsupported input.", "unsupported_input", ref=ref)

        if profile is None or profile.profileContractVersion != "2.0":
            raise _input_error("Material Data Profile 2.0 is required.", "profile_contract_unsupported")
        if profile.datasetId != context.dataset_id:
            raise _input_error("Profile dataset identity does not match execution context.", "profile_dataset_mismatch")
        if not tables:
            raise _input_error("At least one Profile-bound DataFrame is required.", "missing_table")

        known_tables = {
            item.objectId for item in profile.resourceSemantics if item.objectType == "DataFrame"
        }
        unknown = sorted(set(tables) - known_tables)
        if unknown:
            raise _input_error(
                "Resolved table is not declared by Profile 2.0.",
                "object_not_profiled",
                objectIds=unknown,
            )
        return PreparedCompositionSpace(profile=profile, tables=tables, ml_artifacts=tuple(ml_artifacts))

    def run(self, prepared: PreparedCompositionSpace, params: dict[str, Any]) -> CompositionSpaceResult:
        limits = _limits(self.context, params)
        resolved_rows = sum(len(table) for table in prepared.tables.values())
        if resolved_rows > limits["maxRows"]:
            raise _resource_error(
                "Composition-space resolved input exceeds the row cap.",
                rows=resolved_rows,
                maxRows=limits["maxRows"],
            )
        selected = _selected_tables(prepared, params)
        samples, coverage, property_units = _samples_from_tables(prepared.profile, selected, params, limits)
        if len(samples) < 3:
            raise _input_error(
                "Composition PCA requires at least three valid material samples.",
                "insufficient_valid_samples",
                validSamples=len(samples),
                minimum=3,
            )

        basis = sorted(
            {element for sample in samples for element in sample.fractions},
            key=lambda symbol: (Element(symbol).Z, symbol),
        )
        if len(basis) > limits["maxElements"]:
            raise _resource_error(
                "Composition element basis exceeds the cap.",
                elementCount=len(basis),
                maxElements=limits["maxElements"],
            )
        matrix = np.asarray(
            [[float(sample.fractions.get(element, 0.0)) for element in basis] for sample in samples],
            dtype=np.float64,
        )
        if not np.all(np.isfinite(matrix)):
            raise _input_error("Composition feature matrix contains non-finite values.", "non_finite_feature_matrix")
        centered = matrix - np.mean(matrix, axis=0)
        rank = int(np.linalg.matrix_rank(centered))
        if rank < 2:
            raise _input_error(
                "Composition feature matrix has insufficient rank for a two-dimensional PCA.",
                "insufficient_projection_rank",
                rank=rank,
                requiredRank=2,
            )

        pca = PCA(n_components=2, svd_solver="full")
        coordinates = pca.fit_transform(matrix)
        components = np.asarray(pca.components_, dtype=np.float64).copy()
        for component_index in range(components.shape[0]):
            pivot = int(np.argmax(np.abs(components[component_index])))
            if components[component_index, pivot] < 0:
                components[component_index] *= -1
                coordinates[:, component_index] *= -1

        clustering = _cluster(matrix, samples, basis, params, limits)
        cluster_labels = clustering.pop("labels")
        ml_values = _ml_values(prepared.ml_artifacts)
        points = _point_payloads(samples, coordinates, cluster_labels, ml_values)
        display_indices = _bounded_indices(len(points), limits["maxPlotPoints"])
        display_sample_refs = [points[index]["sampleRef"] for index in display_indices]
        display_point_keys = [points[index]["sampleKey"] for index in display_indices]
        outliers = _outlier_candidates(matrix, samples, limits["maxOutlierRows"])
        comparison = _comparison_payload(params, samples, matrix)
        available_colors = _color_options(points, property_units, prepared.ml_artifacts, params)

        explained = [float(value) for value in pca.explained_variance_ratio_]
        payload = {
            "schemaVersion": COMPOSITION_SPACE_SCHEMA_VERSION,
            "artifactType": COMPOSITION_SPACE_TOOL_ID,
            "dataset": _dataset_binding(prepared.profile),
            "coverage": coverage,
            "featureRepresentation": {
                "type": "normalized_atomic_fraction",
                "elementBasis": basis,
                "basisOrder": "atomic_number_ascending",
                "normalization": "element_amount_divided_by_total_amount",
                "missingElementValue": 0.0,
                "fractionalOccupancySupported": True,
                "featureDimensions": len(basis),
                "parser": "pymatgen.core.Composition via application composition semantics",
            },
            "projection": {
                "method": "PCA",
                "dimensions": 2,
                "centering": True,
                "scaling": "none",
                "solver": "sklearn_full_svd",
                "signConvention": "largest_absolute_loading_is_positive",
                "rank": rank,
                "components": components.tolist(),
                "explainedVarianceRatio": explained,
                "cumulativeExplainedVarianceRatio": float(sum(explained)),
                "mean": [float(value) for value in pca.mean_],
            },
            "clustering": clustering,
            "comparison": comparison,
            "coloring": {
                "available": available_colors,
                "default": "cluster" if clustering["status"] == "READY" else "chemical_system",
                "scientificAuthority": "descriptive_visual_encoding_only",
            },
            "points": points,
            "displaySampleRefs": display_sample_refs,
            "displayPointKeys": display_point_keys,
            "outlierCandidates": outliers,
            "semantics": {
                "source": "material_data_profile_2",
                "roleInferenceRepeated": False,
                "sampleIdentityPreserved": True,
                "projectionIsNotCanonicalMaterialIdentity": True,
                "clusterMeaning": "composition_cluster_only",
                "outlierMeaning": "distance_to_feature_centroid_candidate_only",
                "structuralSimilarityClaimed": False,
                "chemicalFamilyClaimed": False,
            },
            "limits": limits,
            "security": _security(),
        }
        plot = _plot_payload(payload)
        return CompositionSpaceResult(payload=payload, plot=plot, params=dict(params))

    def export(self, result: CompositionSpaceResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        requested = set(artifact_types) or {
            ArtifactType.table_json,
            ArtifactType.plotly_json,
            ArtifactType.summary_md,
            ArtifactType.recipe_json,
        }
        payloads: list[ArtifactPayload] = []
        if ArtifactType.table_json in requested:
            payloads.append(_json_payload(ArtifactType.table_json, "composition_space.json", result.payload))
        if ArtifactType.plotly_json in requested:
            payloads.append(_json_payload(ArtifactType.plotly_json, "composition_space_plot.json", result.plot))
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
                name="Composition Space Explorer",
                params=result.params,
                artifact_types=sorted(requested, key=lambda item: item.value),
            )
            recipe["semanticBinding"] = {
                "profileId": result.payload["dataset"]["profileId"],
                "semanticHash": result.payload["dataset"]["semanticHash"],
                "roleInferenceRepeated": False,
            }
            recipe["algorithm"] = {
                "features": "normalized_atomic_fraction",
                "projection": "centered_unscaled_pca_full_svd",
                "pcaSignConvention": "largest_absolute_loading_is_positive",
                "clustering": result.payload["clustering"].get("method"),
                "clusteringFeatureSpace": "normalized_atomic_fraction",
            }
            payloads.append(_json_payload(ArtifactType.recipe_json, "recipe.json", recipe))

        max_bytes = int(self.context.resource_limits.get("maxArtifactBytes", 16_000_000))
        for item in payloads:
            content = item.content if isinstance(item.content, str) else stable_json_dumps(item.content)
            if len(content.encode("utf-8")) > max_bytes:
                raise _resource_error("Composition-space artifact exceeds the byte cap.", artifact=item.file_name)
        return self.export_payloads(
            payloads,
            provenance={
                "sourceFunction": "platform_builtin.composition_space",
                "profileContractVersion": "2.0",
                "semanticHash": result.payload["dataset"]["semanticHash"],
                "sklearnVersion": metadata.version("scikit-learn"),
                "deterministic": True,
            },
        )


def _selected_tables(
    prepared: PreparedCompositionSpace,
    params: Mapping[str, Any],
) -> list[tuple[str, pd.DataFrame, str]]:
    mode = str(params.get("comparisonMode") or "none")
    if mode == "resources":
        left = str(params.get("leftObjectId") or "")
        right = str(params.get("rightObjectId") or "")
        if not left or not right or left == right or left not in prepared.tables or right not in prepared.tables:
            raise _input_error(
                "Resource comparison requires two distinct Profile-bound tables.",
                "invalid_resource_comparison",
            )
        return [(left, prepared.tables[left], left), (right, prepared.tables[right], right)]

    object_id = str(params.get("tableObjectId") or "")
    if not object_id:
        if len(prepared.tables) != 1:
            raise _input_error("An explicit tableObjectId is required.", "ambiguous_primary_table")
        object_id = next(iter(prepared.tables))
    if object_id not in prepared.tables:
        raise _input_error("Requested table is unavailable.", "table_object_missing", objectId=object_id)
    table = prepared.tables[object_id]
    if mode == "none":
        return [(object_id, table, object_id)]
    if mode != "group":
        raise _input_error("Unsupported comparison mode.", "invalid_comparison_mode", comparisonMode=mode)

    column = str(params.get("groupColumn") or "")
    if not column or column not in table.columns or "groupA" not in params or "groupB" not in params:
        raise _input_error("Group comparison requires an explicit group column and two values.", "invalid_group_comparison")
    group_a = params["groupA"]
    group_b = params["groupB"]
    if group_a == group_b:
        raise _input_error("Comparison groups must be distinct.", "duplicate_comparison_groups")
    left = table.loc[table[column] == group_a].copy()
    right = table.loc[table[column] == group_b].copy()
    if left.empty or right.empty:
        raise _input_error("Both comparison groups must contain samples.", "empty_comparison_group")
    return [
        (object_id, left, str(group_a)),
        (object_id, right, str(group_b)),
    ]


def _samples_from_tables(
    profile: DataProfile,
    selected: list[tuple[str, pd.DataFrame, str]],
    params: Mapping[str, Any],
    limits: Mapping[str, int],
) -> tuple[list[_Sample], dict[str, Any], dict[str, str | None]]:
    selected_rows = sum(len(table) for _object_id, table, _group in selected)
    if selected_rows > limits["maxRows"]:
        raise _resource_error(
            "Composition-space input exceeds the row cap.",
            rows=selected_rows,
            maxRows=limits["maxRows"],
        )

    samples: list[_Sample] = []
    invalid: list[dict[str, Any]] = []
    property_units: dict[str, str | None] = {}
    for object_id, table, group in selected:
        formula_column = _single_role_column(profile, object_id, "material_formula")
        property_columns = _property_columns(profile, object_id, limits["maxColorProperties"])
        for column, unit in property_columns:
            if column in property_units and property_units[column] != unit:
                raise _input_error(
                    "Compared property columns must have identical explicit unit semantics.",
                    "incompatible_property_units",
                    column=column,
                    leftUnit=property_units[column],
                    rightUnit=unit,
                )
            property_units.setdefault(column, unit)
        for row_index, row in table.iterrows():
            parsed = parse_formula(row.get(formula_column))
            total = sum(parsed.amounts.values()) if parsed.is_valid else 0.0
            valid_amounts = parsed.is_valid and isfinite(total) and total > 0 and all(
                isfinite(float(value)) and float(value) > 0 for value in parsed.amounts.values()
            )
            if not valid_amounts:
                invalid.append(
                    {
                        "objectId": object_id,
                        "rowIndex": int(row_index),
                        "reason": parsed.warning or "non_positive_or_non_finite_composition",
                    }
                )
                continue
            fractions = {symbol: float(amount) / total for symbol, amount in parsed.amounts.items()}
            properties = {
                column: value
                for column, _unit in property_columns
                if (value := _finite_float(row.get(column))) is not None
            }
            identity = _sample_identity(profile, object_id, table, int(row_index))
            samples.append(
                _Sample(
                    sample_ref=identity["sampleRef"],
                    identity_source=identity["identitySource"],
                    object_id=object_id,
                    row_index=int(row_index),
                    group=group,
                    parsed=parsed,
                    fractions=dict(sorted(fractions.items(), key=lambda item: (Element(item[0]).Z, item[0]))),
                    properties=properties,
                )
            )

    if len(samples) > limits["maxAnalyzedSamples"]:
        raise _resource_error(
            "Valid composition sample count exceeds the analysis cap; no silent sampling is allowed.",
            validSamples=len(samples),
            maxAnalyzedSamples=limits["maxAnalyzedSamples"],
        )
    return samples, {
        "selectedRows": selected_rows,
        "validCompositionSamples": len(samples),
        "invalidCompositionSamples": len(invalid),
        "invalidExamples": invalid[: limits["maxWarnings"]],
        "invalidExamplesTruncated": len(invalid) > limits["maxWarnings"],
        "silentDrops": False,
    }, dict(sorted(property_units.items()))


def _cluster(
    matrix: np.ndarray,
    samples: list[_Sample],
    basis: list[str],
    params: Mapping[str, Any],
    limits: Mapping[str, int],
) -> dict[str, Any]:
    enabled = bool(params.get("clusteringEnabled", True))
    if not enabled:
        return {
            "status": "DISABLED",
            "method": None,
            "featureSpace": "normalized_atomic_fraction",
            "labels": [None] * len(samples),
            "clusters": [],
        }
    n_clusters = int(params.get("nClusters") or 3)
    unique_rows = len(np.unique(matrix, axis=0))
    if n_clusters < 2 or n_clusters > limits["maxClusters"] or n_clusters > len(samples) or n_clusters > unique_rows:
        raise _input_error(
            "Requested cluster count is incompatible with the bounded feature matrix.",
            "invalid_cluster_count",
            nClusters=n_clusters,
            sampleCount=len(samples),
            uniqueCompositionCount=unique_rows,
            maxClusters=limits["maxClusters"],
        )
    random_state = int(params.get("randomState") or 0)
    n_init = int(params.get("nInit") or 10)
    max_iterations = int(params.get("maxIterations") or 300)
    tolerance = float(params.get("tolerance") or 1e-4)
    model = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=n_init,
        max_iter=max_iterations,
        tol=tolerance,
        algorithm="lloyd",
    ).fit(matrix)
    order = sorted(
        range(n_clusters),
        key=lambda index: tuple(round(float(value), 12) for value in model.cluster_centers_[index]),
    )
    relabel = {old: new for new, old in enumerate(order)}
    labels = [relabel[int(label)] for label in model.labels_]
    clusters = []
    for new_label, old_label in enumerate(order):
        member_indices = [index for index, label in enumerate(labels) if label == new_label]
        average = np.mean(matrix[member_indices], axis=0)
        dominant = sorted(
            ((basis[index], float(value)) for index, value in enumerate(average) if value > 0),
            key=lambda item: (-item[1], Element(item[0]).Z),
        )[:5]
        systems: dict[str, int] = {}
        for index in member_indices:
            system = samples[index].parsed.chemical_system
            systems[system] = systems.get(system, 0) + 1
        clusters.append(
            {
                "cluster": new_label,
                "sampleCount": len(member_indices),
                "centroid": [float(value) for value in model.cluster_centers_[old_label]],
                "dominantElements": [{"element": element, "meanFraction": value} for element, value in dominant],
                "topChemicalSystems": [
                    {"chemicalSystem": key, "count": count}
                    for key, count in sorted(systems.items(), key=lambda item: (-item[1], item[0]))[:10]
                ],
            }
        )
    return {
        "status": "READY",
        "method": "kmeans_lloyd",
        "featureSpace": "normalized_atomic_fraction",
        "labels": labels,
        "parameters": {
            "nClusters": n_clusters,
            "randomState": random_state,
            "nInit": n_init,
            "maxIterations": max_iterations,
            "tolerance": tolerance,
            "labelOrdering": "centroid_lexicographic",
        },
        "inertia": float(model.inertia_),
        "iterations": int(model.n_iter_),
        "clusters": clusters,
        "scientificAuthority": "descriptive_composition_clusters_not_material_families",
    }


def _point_payloads(
    samples: list[_Sample],
    coordinates: np.ndarray,
    labels: list[int | None],
    ml_values: Mapping[tuple[str, str], Mapping[str, float]],
) -> list[dict[str, Any]]:
    points = []
    for index, sample in enumerate(samples):
        points.append(
            {
                "sampleRef": sample.sample_ref,
                "sampleKey": f"{sample.object_id}:{sample.sample_ref}",
                "identitySource": sample.identity_source,
                "objectId": sample.object_id,
                "rowIndex": sample.row_index,
                "formula": sample.parsed.formula,
                "reducedFormula": sample.parsed.reduced_formula,
                "chemicalSystem": sample.parsed.chemical_system,
                "group": sample.group,
                "coordinates": [float(value) for value in coordinates[index]],
                "cluster": labels[index],
                "elementFractions": dict(sample.fractions),
                "propertyValues": dict(sample.properties),
                "mlValues": dict(ml_values.get((sample.object_id, sample.sample_ref), {})),
            }
        )
    return points


def _ml_values(artifacts: tuple[Mapping[str, Any], ...]) -> dict[tuple[str, str], dict[str, float]]:
    values: dict[tuple[str, str], dict[str, float]] = {}
    for artifact in artifacts:
        for evaluation in artifact.get("evaluations") or []:
            task_id = str(evaluation.get("taskId") or evaluation.get("groupId") or "task")
            candidates = [
                *(evaluation.get("parityPoints") or []),
                *(evaluation.get("uncertaintyErrorPoints") or []),
                *(evaluation.get("highErrorSamples") or []),
                *(evaluation.get("sampleRows") or []),
                *(evaluation.get("highUncertaintySamples") or []),
            ]
            for item in candidates:
                object_id = item.get("objectId")
                sample_ref = item.get("sampleRef")
                if not object_id or not sample_ref:
                    continue
                target = values.setdefault((str(object_id), str(sample_ref)), {})
                for source_key, output_key in (
                    ("absoluteError", "absolute_error"),
                    ("residual", "residual"),
                    ("uncertainty", "uncertainty"),
                ):
                    if (number := _finite_float(item.get(source_key))) is not None:
                        target[f"{task_id}:{output_key}"] = number
    return values


def _outlier_candidates(matrix: np.ndarray, samples: list[_Sample], limit: int) -> list[dict[str, Any]]:
    centroid = np.mean(matrix, axis=0)
    distances = np.linalg.norm(matrix - centroid, axis=1)
    ordered = sorted(range(len(samples)), key=lambda index: (-float(distances[index]), samples[index].sample_ref))
    return [
        {
            "rank": rank + 1,
            "sampleRef": samples[index].sample_ref,
            "objectId": samples[index].object_id,
            "rowIndex": samples[index].row_index,
            "distance": float(distances[index]),
            "policy": "euclidean_distance_to_combined_feature_centroid",
            "interpretation": "composition_space_candidate_not_invalid_material",
        }
        for rank, index in enumerate(ordered[:limit])
    ]


def _comparison_payload(params: Mapping[str, Any], samples: list[_Sample], matrix: np.ndarray) -> dict[str, Any]:
    mode = str(params.get("comparisonMode") or "none")
    if mode == "none":
        return {"status": "NOT_REQUESTED", "mode": "none"}
    groups = sorted({sample.group for sample in samples})
    rows = []
    for group in groups:
        indices = [index for index, sample in enumerate(samples) if sample.group == group]
        rows.append(
            {
                "group": group,
                "sampleCount": len(indices),
                "featureCentroid": [float(value) for value in np.mean(matrix[indices], axis=0)],
            }
        )
    return {
        "status": "READY",
        "mode": mode,
        "groups": rows,
        "projectionPolicy": "exploratory_combined_projection",
        "sharedElementBasis": True,
        "sharedPcaFit": True,
        "trainingSafetyClaimed": False,
    }


def _color_options(
    points: list[dict[str, Any]],
    property_units: Mapping[str, str | None],
    ml_artifacts: tuple[Mapping[str, Any], ...],
    params: Mapping[str, Any],
) -> list[dict[str, Any]]:
    options = [
        {"id": "cluster", "kind": "categorical", "label": "Composition cluster", "source": "composition_space"},
        {"id": "chemical_system", "kind": "categorical", "label": "Chemical system", "source": "composition_semantics"},
        {"id": "group", "kind": "categorical", "label": "Dataset / group", "source": "explicit_comparison_binding"},
    ]
    for column, unit in property_units.items():
        if any(column in point["propertyValues"] for point in points):
            options.append(
                {
                    "id": f"property:{column}",
                    "kind": "continuous",
                    "label": column,
                    "unit": unit,
                    "source": "material_data_profile_2_material_property",
                }
            )
    ml_keys = sorted({key for point in points for key in point["mlValues"]})
    for key in ml_keys:
        options.append(
            {
                "id": f"ml:{key}",
                "kind": "continuous",
                "label": key,
                "unit": None,
                "source": "phase10k3_sample_bound_artifact",
            }
        )
    requested = params.get("colorBy")
    if requested and str(requested) not in {item["id"] for item in options}:
        raise _input_error("Requested color source is unavailable.", "color_source_unavailable", colorBy=requested)
    if not ml_artifacts and requested and str(requested).startswith("ml:"):
        raise _input_error("ML coloring requires an explicit Phase 10K-3 artifact binding.", "missing_ml_artifact")
    return options


def _plot_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    display = set(payload["displayPointKeys"])
    points = [point for point in payload["points"] if point["sampleKey"] in display]
    marker_colors = [point["cluster"] if point["cluster"] is not None else 0 for point in points]
    return {
        "data": [
            {
                "type": "scattergl",
                "mode": "markers",
                "x": [point["coordinates"][0] for point in points],
                "y": [point["coordinates"][1] for point in points],
                "customdata": [point["sampleKey"] for point in points],
                "marker": {"color": marker_colors, "colorscale": "Viridis", "showscale": False, "size": 7},
                "hovertemplate": "sample=%{customdata}<extra></extra>",
            }
        ],
        "layout": {
            "title": "PCA Composition Space",
            "xaxis": {"title": "PC1"},
            "yaxis": {"title": "PC2"},
            "showlegend": False,
        },
        "config": {"displaylogo": False, "responsive": True},
        "security": _security(),
    }


def _property_columns(profile: DataProfile, object_id: str, limit: int) -> list[tuple[str, str | None]]:
    columns = [
        (column.column, column.unit)
        for column in profile.semanticColumns
        if column.objectId == object_id and any(role.role == "material_property" for role in column.roles)
    ]
    return sorted(set(columns), key=lambda item: item[0])[:limit]


def _single_role_column(profile: DataProfile, object_id: str, role_name: str) -> str:
    values = sorted(
        {
            column.column
            for column in profile.semanticColumns
            if column.objectId == object_id and any(role.role == role_name for role in column.roles)
        }
    )
    if len(values) != 1:
        raise _input_error(
            "Composition space requires exactly one Profile-bound formula column per table.",
            "ambiguous_formula_semantics" if values else "missing_formula_semantics",
            objectId=object_id,
            columns=values,
        )
    return values[0]


def _sample_identity(profile: DataProfile, object_id: str, table: pd.DataFrame, row_index: int) -> dict[str, str]:
    explicit = profile.sampleIdentity.explicitColumn if profile.sampleIdentity and profile.sampleIdentity.policy == "explicit_column" else None
    if explicit and explicit in table.columns and not pd.isna(table.at[row_index, explicit]):
        return {"sampleRef": str(table.at[row_index, explicit]), "identitySource": "explicit_column"}
    object_hash = next(
        (item.objectHash for item in profile.resourceSemantics if item.objectId == object_id),
        profile.semanticHash or "unknown",
    )
    return {
        "sampleRef": stable_sample_reference(
            dataset_id=profile.datasetId,
            dataset_version=profile.version,
            object_hash=object_hash,
            row_index=row_index,
        ),
        "identitySource": "dataset_version_object_hash_row_index",
    }


def _limits(context: ToolExecutionContext, params: Mapping[str, Any]) -> dict[str, int]:
    resource = context.resource_limits
    return {
        "maxRows": int(resource.get("maxRows", 100_000)),
        "maxAnalyzedSamples": int(resource.get("maxAnalyzedSamples", 20_000)),
        "maxElements": int(resource.get("maxElements", 118)),
        "maxClusters": int(resource.get("maxClusters", 12)),
        "maxPlotPoints": min(int(params.get("maxPlotPoints") or 5_000), int(resource.get("maxPlotPoints", 10_000))),
        "maxOutlierRows": min(int(params.get("maxOutlierRows") or 50), int(resource.get("maxOutlierRows", 200))),
        "maxColorProperties": int(resource.get("maxColorProperties", 16)),
        "maxWarnings": int(resource.get("maxWarnings", 128)),
        "maxArtifactBytes": int(resource.get("maxArtifactBytes", 16_000_000)),
    }


def _dataset_binding(profile: DataProfile) -> dict[str, Any]:
    return {
        "datasetId": profile.datasetId,
        "datasetVersion": profile.version,
        "profileId": profile.profileId,
        "profileContractVersion": profile.profileContractVersion,
        "semanticHash": profile.semanticHash,
        "datasetContentHash": content_hash(
            stable_json_dumps(
                [
                    {"objectId": item.objectId, "objectHash": item.objectHash, "objectType": item.objectType}
                    for item in sorted(profile.resourceSemantics, key=lambda value: value.objectId)
                ]
            )
        ),
    }


def _summary_markdown(payload: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Composition Space Explorer",
            "",
            f"- Dataset: `{payload['dataset']['datasetId']}`",
            f"- Valid compositions: {payload['coverage']['validCompositionSamples']}",
            f"- Invalid compositions: {payload['coverage']['invalidCompositionSamples']}",
            f"- Element basis dimensions: {payload['featureRepresentation']['featureDimensions']}",
            f"- PCA explained variance: {payload['projection']['cumulativeExplainedVarianceRatio']:.6f}",
            f"- Clustering: {payload['clustering']['status']}",
            "- Scientific boundary: PCA proximity and composition clusters do not establish structural similarity or material families.",
        ]
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


def _is_supported_ml_artifact(value: Any) -> bool:
    if not isinstance(value, Mapping) or not any(
        str(value.get("schemaVersion") or "").startswith(prefix) for prefix in _ML_SCHEMA_PREFIXES
    ):
        return False
    security = value.get("security")
    return (
        isinstance(value.get("evaluations"), list)
        and isinstance(security, Mapping)
        and security == _security()
    )


def _looks_like_table(value: Any) -> bool:
    return isinstance(value, list) and (not value or all(isinstance(item, Mapping) for item in value))


def _finite_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if isfinite(parsed) else None


def _bounded_indices(total: int, limit: int) -> list[int]:
    if total <= limit:
        return list(range(total))
    if limit <= 1:
        return [0]
    return [(index * (total - 1)) // (limit - 1) for index in range(limit)]


def _security() -> dict[str, bool]:
    return {
        "artifactJavaScript": False,
        "externalUrls": False,
        "externalAssets": False,
        "executableContent": False,
    }


def _json_payload(artifact_type: ArtifactType, file_name: str, content: Any) -> ArtifactPayload:
    return ArtifactPayload(
        artifact_type=artifact_type,
        file_name=file_name,
        content=stable_json_dumps(content),
        media_type="application/json",
    )


def _ref_value(input_ref: Any, field: str, default: Any = None) -> Any:
    if hasattr(input_ref, field):
        return getattr(input_ref, field)
    if isinstance(input_ref, Mapping):
        return input_ref.get(field, default)
    return default


def _input_error(message: str, error_type: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError(
        "TOOL_INPUT_INVALID",
        message,
        COMPOSITION_SPACE_TOOL_ID,
        details={"errorType": error_type, **details},
    )


def _resource_error(message: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError("TOOL_RESOURCE_LIMIT", message, COMPOSITION_SPACE_TOOL_ID, details=details)
