from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite, sqrt
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd

from mdi_artifact_core import ArtifactPayload, content_hash, stable_json_dumps
from mdi_material_parsers import stable_sample_reference
from mdi_schemas import Artifact, ArtifactType, DataProfile

from ..base import BaseToolAdapter
from ..composition_common import parse_formula
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from ..ml_common import coerce_dataframe


REGRESSION_SCHEMA_VERSION = "phase10k3.materials_ml_regression.v1"
UNCERTAINTY_SCHEMA_VERSION = "phase10k3.materials_ml_uncertainty.v1"
CLASSIFICATION_SCHEMA_VERSION = "phase10k3.materials_ml_classification.v1"
REGRESSION_TOOL_ID = "ml.regression_evaluation"
UNCERTAINTY_TOOL_ID = "ml.uncertainty_evaluation"
CLASSIFICATION_TOOL_ID = "ml.classification_evaluation"


@dataclass(frozen=True)
class PreparedMaterialsML:
    profile: DataProfile
    tables: Mapping[str, pd.DataFrame]
    groups: tuple[Any, ...]


@dataclass(frozen=True)
class MaterialsMLResult:
    payload: dict[str, Any]
    params: dict[str, Any]


class _MaterialsMLAdapter(BaseToolAdapter):
    expected_kind: str
    schema_version: str
    artifact_name: str
    product_name: str

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedMaterialsML:
        profile: DataProfile | None = None
        tables: dict[str, pd.DataFrame] = {}
        for index, value in enumerate(self._resolved_inputs):
            ref = str(_ref_value(input_refs[index], "ref", f"input_{index}"))
            candidate = _coerce_profile(value, self.tool_id)
            if candidate is not None:
                if profile is not None:
                    raise _input_error(self.tool_id, "Exactly one Profile 2.0 input is allowed.", "multiple_profiles")
                profile = candidate
            elif isinstance(value, pd.DataFrame) or _looks_like_table(value):
                tables[ref] = coerce_dataframe(value, tool_id=self.tool_id)
            else:
                raise _input_error(self.tool_id, "Materials ML received an unsupported input.", "unsupported_input", ref=ref)

        if profile is None or profile.profileContractVersion != "2.0":
            raise _input_error(self.tool_id, "Material Data Profile 2.0 is required.", "profile_contract_unsupported")
        if profile.datasetId != context.dataset_id:
            raise _input_error(self.tool_id, "Profile dataset identity does not match execution context.", "profile_dataset_mismatch")
        if not tables:
            raise _input_error(self.tool_id, "A profiled DataFrame is required.", "missing_table")

        matching_groups = [group for group in profile.semanticGroups if group.kind == self.expected_kind]
        groups = [group for group in matching_groups if group.status == "COMPLETE"]
        requested = params.get("groupIds") or []
        if requested:
            requested_set = set(str(item) for item in requested)
            known = {group.groupId for group in groups}
            unknown = sorted(requested_set - known)
            if unknown:
                raise _input_error(self.tool_id, "Requested semantic group is unavailable.", "unknown_task_group", groupIds=unknown)
            groups = [group for group in groups if group.groupId in requested_set]
        if not groups:
            if any(group.status == "AMBIGUOUS" for group in matching_groups):
                raise _input_error(
                    self.tool_id,
                    "Profile 2.0 task binding is ambiguous.",
                    "ambiguous_semantic_binding",
                    groupIds=[group.groupId for group in matching_groups if group.status == "AMBIGUOUS"],
                )
            if matching_groups:
                raise _input_error(
                    self.tool_id,
                    "Profile 2.0 task is incomplete.",
                    "incomplete_semantic_task",
                    reasons=sorted({reason for group in matching_groups for reason in group.reasons}),
                )
            raise _input_error(self.tool_id, "No complete Profile 2.0 task group is available.", "missing_semantic_task")

        for group in groups:
            object_ids = _group_object_ids(profile, group.groupId)
            if len(object_ids) != 1:
                raise _input_error(self.tool_id, "Semantic task must bind exactly one table object.", "ambiguous_semantic_binding", groupId=group.groupId)
            _table_for_object(tables, object_ids[0], self.tool_id)
        return PreparedMaterialsML(profile=profile, tables=tables, groups=tuple(groups))

    def export(self, result: MaterialsMLResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        requested = set(artifact_types) or {ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json}
        payloads: list[ArtifactPayload] = []
        if ArtifactType.table_json in requested:
            payloads.append(_json_payload(ArtifactType.table_json, self.artifact_name, result.payload))
        if ArtifactType.summary_md in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=_summary_markdown(self.product_name, result.payload),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in requested:
            recipe = self.recipe_payload(
                name=self.product_name,
                params=result.params,
                artifact_types=sorted(requested, key=lambda item: item.value),
            )
            recipe["semanticBinding"] = {
                "datasetId": result.payload["dataset"]["datasetId"],
                "datasetVersion": result.payload["dataset"]["datasetVersion"],
                "profileId": result.payload["dataset"]["profileId"],
                "profileContractVersion": result.payload["dataset"]["profileContractVersion"],
                "semanticHash": result.payload["dataset"]["semanticHash"],
                "datasetContentHash": result.payload["dataset"]["datasetContentHash"],
                "resourceBindings": result.payload["dataset"]["resourceBindings"],
                "groupIds": [item["groupId"] for item in result.payload["evaluations"]],
                "roleInferenceRepeated": False,
            }
            payloads.append(_json_payload(ArtifactType.recipe_json, "recipe.json", recipe))

        max_bytes = int(self.context.resource_limits.get("maxArtifactBytes", 8_000_000))
        for payload in payloads:
            content = payload.content if isinstance(payload.content, str) else stable_json_dumps(payload.content)
            if len(content.encode("utf-8")) > max_bytes:
                raise _resource_error(self.tool_id, "Materials ML artifact exceeds the byte cap.", artifact=payload.file_name)
        return self.export_payloads(
            payloads,
            provenance={
                "sourceFunction": f"platform_builtin.{self.tool_id.replace('.', '_')}",
                "profileContractVersion": "2.0",
                "semanticHash": result.payload["dataset"]["semanticHash"],
                "deterministic": True,
            },
        )

    def _base_payload(self, prepared: PreparedMaterialsML, evaluations: list[dict[str, Any]], limits: dict[str, Any]) -> dict[str, Any]:
        return {
            "schemaVersion": self.schema_version,
            "artifactType": self.tool_id,
            "dataset": _dataset_binding(prepared.profile),
            "evaluations": evaluations,
            "limits": limits,
            "semantics": {
                "source": "material_data_profile_2",
                "roleInferenceRepeated": False,
                "sampleIdentityPreserved": True,
                "backendScientificAuthority": True,
            },
            "security": _security(),
        }


class RegressionEvaluationAdapter(_MaterialsMLAdapter):
    tool_id = REGRESSION_TOOL_ID
    expected_kind = "regression"
    schema_version = REGRESSION_SCHEMA_VERSION
    artifact_name = "materials_ml_regression.json"
    product_name = "Materials ML Regression Evaluation"

    def run(self, prepared: PreparedMaterialsML, params: dict[str, Any]) -> MaterialsMLResult:
        limits = _limits(self.context, params)
        evaluations: list[dict[str, Any]] = []
        internal: list[tuple[dict[str, Any], pd.DataFrame, pd.Series]] = []
        for group in prepared.groups:
            object_id = _only(_group_object_ids(prepared.profile, group.groupId), self.tool_id)
            table = _table_for_object(prepared.tables, object_id, self.tool_id)
            _check_table_cap(table, limits, self.tool_id)
            target_column = _only(group.targetColumns, self.tool_id, "ambiguous_target")
            series = _regression_series(group)
            if len(series) > limits["maxModels"]:
                raise _resource_error(self.tool_id, "Regression model count exceeds the cap.", models=len(series), maxModels=limits["maxModels"])
            for series_id, prediction_column, uncertainty_columns in series:
                evaluation, frame, mask = _regression_evaluation(
                    prepared.profile,
                    table,
                    object_id,
                    group.groupId,
                    series_id,
                    target_column,
                    prediction_column,
                    uncertainty_columns[0] if uncertainty_columns else None,
                    limits,
                )
                evaluations.append(evaluation)
                internal.append((evaluation, frame, mask))
        comparisons = _model_comparisons(internal)
        payload = self._base_payload(prepared, evaluations, limits)
        payload["modelComparisons"] = comparisons
        payload["residualConvention"] = "prediction_minus_target"
        return MaterialsMLResult(payload=payload, params=dict(params))


class UncertaintyEvaluationAdapter(_MaterialsMLAdapter):
    tool_id = UNCERTAINTY_TOOL_ID
    expected_kind = "regression"
    schema_version = UNCERTAINTY_SCHEMA_VERSION
    artifact_name = "materials_ml_uncertainty.json"
    product_name = "Materials ML Uncertainty Evaluation"

    def run(self, prepared: PreparedMaterialsML, params: dict[str, Any]) -> MaterialsMLResult:
        limits = _limits(self.context, params)
        evaluations: list[dict[str, Any]] = []
        for group in prepared.groups:
            object_id = _only(_group_object_ids(prepared.profile, group.groupId), self.tool_id)
            table = _table_for_object(prepared.tables, object_id, self.tool_id)
            _check_table_cap(table, limits, self.tool_id)
            target_column = _only(group.targetColumns, self.tool_id, "ambiguous_target")
            for series_id, prediction_column, uncertainty_columns in _regression_series(group):
                if not uncertainty_columns:
                    continue
                for uncertainty_column in uncertainty_columns:
                    evaluations.append(
                        _uncertainty_evaluation(
                            prepared.profile,
                            table,
                            object_id,
                            group.groupId,
                            series_id,
                            target_column,
                            prediction_column,
                            uncertainty_column,
                            limits,
                        )
                    )
        if not evaluations:
            raise _input_error(self.tool_id, "No complete prediction/uncertainty binding is available.", "missing_uncertainty_binding")
        return MaterialsMLResult(payload=self._base_payload(prepared, evaluations, limits), params=dict(params))


class ClassificationEvaluationAdapter(_MaterialsMLAdapter):
    tool_id = CLASSIFICATION_TOOL_ID
    expected_kind = "classification"
    schema_version = CLASSIFICATION_SCHEMA_VERSION
    artifact_name = "materials_ml_classification.json"
    product_name = "Materials ML Classification Evaluation"

    def run(self, prepared: PreparedMaterialsML, params: dict[str, Any]) -> MaterialsMLResult:
        limits = _limits(self.context, params)
        evaluations: list[dict[str, Any]] = []
        for group in prepared.groups:
            object_id = _only(_group_object_ids(prepared.profile, group.groupId), self.tool_id)
            table = _table_for_object(prepared.tables, object_id, self.tool_id)
            _check_table_cap(table, limits, self.tool_id)
            evaluations.append(
                _classification_evaluation(
                    prepared.profile,
                    table,
                    object_id,
                    group,
                    limits,
                    positive_class=params.get("positiveClass"),
                )
            )
        return MaterialsMLResult(payload=self._base_payload(prepared, evaluations, limits), params=dict(params))


def regression_metric_values(target: Iterable[float], prediction: Iterable[float]) -> dict[str, Any]:
    target_array = np.asarray(list(target), dtype=float)
    prediction_array = np.asarray(list(prediction), dtype=float)
    if target_array.shape != prediction_array.shape or not len(target_array):
        raise ValueError("Aligned non-empty target and prediction arrays are required.")
    residual = prediction_array - target_array
    absolute = np.abs(residual)
    squared = residual**2
    ss_total = float(np.sum((target_array - float(np.mean(target_array))) ** 2))
    ss_residual = float(np.sum(squared))
    r2 = None if ss_total == 0 else float(1.0 - ss_residual / ss_total)
    return {
        "sampleCount": int(len(target_array)),
        "mae": float(np.mean(absolute)),
        "rmse": float(sqrt(float(np.mean(squared)))),
        "r2": r2,
        "r2Status": "undefined_constant_target" if r2 is None else "defined",
        "meanSignedError": float(np.mean(residual)),
        "medianAbsoluteError": float(np.median(absolute)),
    }


def classification_metric_values(actual: Iterable[str], predicted: Iterable[str]) -> dict[str, Any]:
    actual_values = [str(value) for value in actual]
    predicted_values = [str(value) for value in predicted]
    if len(actual_values) != len(predicted_values) or not actual_values:
        raise ValueError("Aligned non-empty classification labels are required.")
    classes = sorted(set(actual_values) | set(predicted_values))
    matrix = [[sum(1 for a, p in zip(actual_values, predicted_values) if a == row and p == column) for column in classes] for row in classes]
    per_class: list[dict[str, Any]] = []
    for index, label in enumerate(classes):
        tp = matrix[index][index]
        support = sum(matrix[index])
        predicted_positive = sum(row[index] for row in matrix)
        precision = None if predicted_positive == 0 else tp / predicted_positive
        recall = None if support == 0 else tp / support
        f1 = None if precision is None or recall is None or precision + recall == 0 else 2 * precision * recall / (precision + recall)
        per_class.append({"class": label, "support": support, "precision": precision, "recall": recall, "f1": f1})
    accuracy = sum(matrix[index][index] for index in range(len(classes))) / len(actual_values)
    return {
        "sampleCount": len(actual_values),
        "classes": classes,
        "accuracy": accuracy,
        "macroPrecision": _mean_defined(item["precision"] for item in per_class),
        "macroRecall": _mean_defined(item["recall"] for item in per_class),
        "macroF1": _mean_defined(item["f1"] for item in per_class),
        "perClass": per_class,
        "confusionMatrix": {"normalization": "raw_counts", "labels": classes, "values": matrix},
        "zeroDivisionPolicy": "undefined_null",
    }


def binary_roc_pr(actual_positive: Iterable[bool], scores: Iterable[float], *, max_points: int) -> dict[str, Any]:
    labels = np.asarray(list(actual_positive), dtype=bool)
    values = np.asarray(list(scores), dtype=float)
    if labels.shape != values.shape or not len(labels) or not np.all(np.isfinite(values)):
        raise ValueError("Aligned finite binary scores are required.")
    positives = int(np.sum(labels))
    negatives = int(len(labels) - positives)
    if positives == 0 or negatives == 0:
        return {"status": "UNAVAILABLE_SINGLE_CLASS", "roc": None, "precisionRecall": None}
    order = np.argsort(-values, kind="stable")
    labels = labels[order]
    values = values[order]
    thresholds = [float("inf"), *sorted({float(value) for value in values}, reverse=True)]
    roc_points: list[dict[str, float | None]] = []
    pr_points: list[dict[str, float | None]] = []
    for threshold in thresholds:
        selected = values >= threshold
        tp = int(np.sum(labels & selected))
        fp = int(np.sum(~labels & selected))
        roc_points.append({"threshold": None if not isfinite(threshold) else threshold, "fpr": fp / negatives, "tpr": tp / positives})
        pr_points.append({"threshold": None if not isfinite(threshold) else threshold, "recall": tp / positives, "precision": 1.0 if tp + fp == 0 else tp / (tp + fp)})
    auc = float(np.trapezoid([point["tpr"] for point in roc_points], [point["fpr"] for point in roc_points]))
    average_precision = 0.0
    for previous, current in zip(pr_points, pr_points[1:]):
        average_precision += max(0.0, float(current["recall"]) - float(previous["recall"])) * float(current["precision"])
    roc_points = _bounded_points(roc_points, max_points)
    pr_points = _bounded_points(pr_points, max_points)
    return {
        "status": "READY",
        "roc": {"points": roc_points, "auc": auc},
        "precisionRecall": {"points": pr_points, "averagePrecision": average_precision},
    }


def _regression_evaluation(
    profile: DataProfile,
    table: pd.DataFrame,
    object_id: str,
    group_id: str,
    series_id: str,
    target_column: str,
    prediction_column: str,
    uncertainty_column: str | None,
    limits: dict[str, int],
) -> tuple[dict[str, Any], pd.DataFrame, pd.Series]:
    _require_columns(table, [target_column, prediction_column], REGRESSION_TOOL_ID)
    unit, unit_warning = _compatible_unit(profile, object_id, group_id, target_column, prediction_column, REGRESSION_TOOL_ID)
    target = pd.to_numeric(table[target_column], errors="coerce")
    prediction = pd.to_numeric(table[prediction_column], errors="coerce")
    target_missing = table[target_column].isna()
    prediction_missing = table[prediction_column].isna()
    target_finite = target.map(isfinite)
    prediction_finite = prediction.map(isfinite)
    mask = target_finite & prediction_finite
    if not bool(mask.any()):
        raise _input_error(REGRESSION_TOOL_ID, "No aligned finite target/prediction samples are available.", "no_aligned_samples", groupId=group_id)
    evaluated = table.loc[mask].copy()
    evaluated["_target"] = target.loc[mask].astype(float)
    evaluated["_prediction"] = prediction.loc[mask].astype(float)
    evaluated["_residual"] = evaluated["_prediction"] - evaluated["_target"]
    evaluated["_absolute_error"] = evaluated["_residual"].abs()
    if uncertainty_column and uncertainty_column in table.columns:
        evaluated["_uncertainty"] = pd.to_numeric(table.loc[mask, uncertainty_column], errors="coerce")
    metrics = regression_metric_values(evaluated["_target"], evaluated["_prediction"])
    sample_records = _regression_sample_records(profile, object_id, evaluated)
    display_indices = _bounded_indices(len(sample_records), limits["maxPlotPoints"])
    formula_column = _role_column(profile, object_id, "material_formula")
    chemistry = _chemistry_error(evaluated, formula_column, limits)
    histogram_counts, histogram_edges = np.histogram(evaluated["_residual"], bins=limits["histogramBins"])
    warnings = [unit_warning] if unit_warning else []
    if metrics["r2"] is None:
        warnings.append("R2_UNDEFINED_CONSTANT_TARGET")
    evaluation = {
        "groupId": group_id,
        "taskId": f"{group_id}:{series_id}",
        "objectId": object_id,
        "seriesId": series_id,
        "targetColumn": target_column,
        "predictionColumn": prediction_column,
        "uncertaintyColumn": uncertainty_column,
        "unit": unit,
        "coverage": {
            "totalSamples": len(table),
            "evaluatedSamples": int(mask.sum()),
            "targetMissing": int(target_missing.sum()),
            "predictionMissing": int(prediction_missing.sum()),
            "nonFiniteOrInvalid": int((~target_missing & ~target_finite | ~prediction_missing & ~prediction_finite).sum()),
            "excludedSamples": int(len(table) - mask.sum()),
        },
        "metrics": metrics,
        "residualConvention": "prediction_minus_target",
        "parityPoints": [sample_records[index] for index in display_indices],
        "visualizationSampling": {"policy": "deterministic_even_index", "sourceCount": len(sample_records), "displayCount": len(display_indices)},
        "residualHistogram": {"counts": histogram_counts.astype(int).tolist(), "edges": histogram_edges.astype(float).tolist()},
        "highErrorSamples": sorted(sample_records, key=lambda item: (-item["absoluteError"], item["sampleKey"]))[: limits["maxHighErrorRows"]],
        "chemistryConditioned": chemistry,
        "warnings": warnings,
    }
    return evaluation, evaluated, mask


def _uncertainty_evaluation(
    profile: DataProfile,
    table: pd.DataFrame,
    object_id: str,
    group_id: str,
    series_id: str,
    target_column: str,
    prediction_column: str,
    uncertainty_column: str,
    limits: dict[str, int],
) -> dict[str, Any]:
    _require_columns(table, [target_column, prediction_column, uncertainty_column], UNCERTAINTY_TOOL_ID)
    target = pd.to_numeric(table[target_column], errors="coerce")
    prediction = pd.to_numeric(table[prediction_column], errors="coerce")
    uncertainty = pd.to_numeric(table[uncertainty_column], errors="coerce")
    finite = target.map(isfinite) & prediction.map(isfinite) & uncertainty.map(isfinite)
    if bool((uncertainty.loc[uncertainty.map(isfinite)] < 0).any()):
        raise _input_error(UNCERTAINTY_TOOL_ID, "Uncertainty values must be non-negative.", "invalid_uncertainty", column=uncertainty_column)
    if not bool(finite.any()):
        raise _input_error(UNCERTAINTY_TOOL_ID, "No aligned finite uncertainty samples are available.", "no_aligned_samples", groupId=group_id)
    frame = table.loc[finite].copy()
    frame["_target"] = target.loc[finite].astype(float)
    frame["_prediction"] = prediction.loc[finite].astype(float)
    frame["_uncertainty"] = uncertainty.loc[finite].astype(float)
    frame["_absolute_error"] = (frame["_prediction"] - frame["_target"]).abs()
    samples = _uncertainty_sample_records(profile, object_id, frame)
    display_indices = _bounded_indices(len(samples), limits["maxPlotPoints"])
    pearson = _safe_correlation(frame["_uncertainty"], frame["_absolute_error"], method="pearson")
    spearman = _safe_correlation(frame["_uncertainty"], frame["_absolute_error"], method="spearman")
    return {
        "groupId": group_id,
        "taskId": f"{group_id}:{series_id}:{uncertainty_column}",
        "objectId": object_id,
        "seriesId": series_id,
        "targetColumn": target_column,
        "predictionColumn": prediction_column,
        "uncertaintyColumn": uncertainty_column,
        "uncertaintyKind": _uncertainty_kind(profile, object_id, group_id, uncertainty_column),
        "coverage": {"totalSamples": len(table), "evaluatedSamples": len(frame), "excludedSamples": len(table) - len(frame)},
        "association": {"pearson": pearson, "spearman": spearman},
        "uncertaintyErrorPoints": [samples[index] for index in display_indices],
        "reliability": {"method": "equal_count_mean_uncertainty_vs_mean_absolute_error", "bins": _reliability_bins(frame, limits["maxUncertaintyBins"])},
        "errorDecay": {"method": "retain_lowest_uncertainty_first", "metric": "mae", "points": _error_decay(frame)},
        "highUncertaintySamples": sorted(samples, key=lambda item: (-item["uncertainty"], item["sampleKey"]))[: limits["maxHighErrorRows"]],
        "warnings": ["UNCERTAINTY_DIAGNOSTIC_NOT_CALIBRATION_AUTHORITY"],
    }


def _classification_evaluation(
    profile: DataProfile,
    table: pd.DataFrame,
    object_id: str,
    group: Any,
    limits: dict[str, int],
    *,
    positive_class: Any,
) -> dict[str, Any]:
    target_column = _only(group.targetColumns, CLASSIFICATION_TOOL_ID, "ambiguous_target")
    prediction_column = group.predictionColumns[0] if group.predictionColumns else None
    raw_probability_map = _probability_map(profile, object_id, group.groupId)
    _require_columns(table, [target_column, *([prediction_column] if prediction_column else []), *raw_probability_map.values()], CLASSIFICATION_TOOL_ID)
    actual = table[target_column].map(_class_value)
    if prediction_column:
        predicted = table[prediction_column].map(_class_value)
        prediction_source = "profile_classification_prediction"
        known_classes = sorted(set(actual.dropna()) | set(predicted.dropna()))
        probability_map = _resolve_probability_labels(raw_probability_map, known_classes)
        probabilities = _validated_probabilities(table, probability_map, CLASSIFICATION_TOOL_ID)
    elif raw_probability_map:
        probability_map = _resolve_probability_labels(raw_probability_map, sorted(set(actual.dropna())))
        probabilities = _validated_probabilities(table, probability_map, CLASSIFICATION_TOOL_ID)
        predicted = probabilities.apply(_probability_argmax, axis=1)
        prediction_source = "deterministic_probability_argmax"
    else:
        raise _input_error(CLASSIFICATION_TOOL_ID, "Classification requires predictions or class probabilities.", "missing_prediction")
    mask = actual.notna() & predicted.notna()
    if not bool(mask.any()):
        raise _input_error(CLASSIFICATION_TOOL_ID, "No aligned classification samples are available.", "no_aligned_samples")
    actual_values = actual.loc[mask].astype(str).tolist()
    predicted_values = predicted.loc[mask].astype(str).tolist()
    metrics = classification_metric_values(actual_values, predicted_values)
    if len(metrics["classes"]) > limits["maxClasses"]:
        raise _resource_error(CLASSIFICATION_TOOL_ID, "Classification class count exceeds the cap.", classes=len(metrics["classes"]), maxClasses=limits["maxClasses"])
    formula_column = _role_column(profile, object_id, "material_formula")
    rows: list[dict[str, Any]] = []
    for row_index in table.index[mask]:
        actual_value = str(actual.loc[row_index])
        predicted_value = str(predicted.loc[row_index])
        rows.append(
            {
                **_sample_identity(profile, object_id, table, int(row_index)),
                **_formula_identity(table, formula_column, int(row_index)),
                "actualClass": actual_value,
                "predictedClass": predicted_value,
                "probabilities": {label: float(probabilities.loc[row_index, label]) for label in probability_map} if probability_map else {},
                "misclassified": actual_value != predicted_value,
            }
        )
    requested_positive = _class_value(positive_class)
    normalized_positive = _resolve_requested_class(requested_positive, metrics["classes"])
    curves: dict[str, Any]
    if len(metrics["classes"]) != 2:
        curves = {"status": "UNAVAILABLE_MULTICLASS_DEFERRED", "positiveClass": normalized_positive, "roc": None, "precisionRecall": None}
    elif not probability_map:
        curves = {"status": "UNAVAILABLE_CLASS_PROBABILITY_MISSING", "positiveClass": normalized_positive, "roc": None, "precisionRecall": None}
    elif normalized_positive is None:
        curves = {"status": "UNAVAILABLE_POSITIVE_CLASS_REQUIRED", "positiveClass": None, "roc": None, "precisionRecall": None}
    elif normalized_positive not in metrics["classes"]:
        raise _input_error(CLASSIFICATION_TOOL_ID, "Requested positive class is not present.", "unknown_positive_class", positiveClass=normalized_positive)
    elif normalized_positive not in probability_map:
        curves = {"status": "UNAVAILABLE_CLASS_PROBABILITY_MISSING", "positiveClass": normalized_positive, "roc": None, "precisionRecall": None}
    else:
        curve_mask = mask & probabilities[normalized_positive].notna()
        curves = binary_roc_pr(
            (actual.loc[curve_mask] == normalized_positive).tolist(),
            probabilities.loc[curve_mask, normalized_positive].tolist(),
            max_points=limits["maxCurvePoints"],
        )
        curves["positiveClass"] = normalized_positive
    return {
        "groupId": group.groupId,
        "taskId": group.groupId,
        "objectId": object_id,
        "targetColumn": target_column,
        "predictionColumn": prediction_column,
        "predictionSource": prediction_source,
        "coverage": {"totalSamples": len(table), "evaluatedSamples": int(mask.sum()), "excludedSamples": int(len(table) - mask.sum())},
        "metrics": metrics,
        "curves": curves,
        "misclassifiedSamples": [row for row in rows if row["misclassified"]][: limits["maxHighErrorRows"]],
        "sampleRows": rows[: limits["maxTableRows"]],
        "warnings": _classification_warnings(metrics),
    }


def _model_comparisons(internal: list[tuple[dict[str, Any], pd.DataFrame, pd.Series]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[tuple[dict[str, Any], pd.DataFrame, pd.Series]]] = {}
    for item in internal:
        evaluation = item[0]
        key = (evaluation["objectId"], evaluation["targetColumn"], evaluation["unit"] or "")
        grouped.setdefault(key, []).append(item)
    comparisons: list[dict[str, Any]] = []
    for (object_id, target_column, unit), items in sorted(grouped.items()):
        if len(items) < 2:
            continue
        common = items[0][2].copy()
        for _evaluation, _frame, mask in items[1:]:
            common &= mask
        models = []
        for evaluation, frame, _mask in items:
            shared = frame.loc[frame.index.intersection(common[common].index)]
            models.append(
                {
                    "taskId": evaluation["taskId"],
                    "seriesId": evaluation["seriesId"],
                    "individualCoverage": evaluation["coverage"],
                    "commonSampleMetrics": regression_metric_values(shared["_target"], shared["_prediction"]) if len(shared) else None,
                }
            )
        comparisons.append(
            {
                "objectId": object_id,
                "targetColumn": target_column,
                "unit": unit or None,
                "policy": "common_valid_samples",
                "commonSampleCount": int(common.sum()),
                "models": models,
            }
        )
    return comparisons


def _chemistry_error(frame: pd.DataFrame, formula_column: str | None, limits: dict[str, int]) -> dict[str, Any]:
    if not formula_column or formula_column not in frame.columns:
        return {"status": "UNAVAILABLE", "reason": "FORMULA_SEMANTICS_UNAVAILABLE", "byElement": [], "byChemicalSystem": []}
    elements: dict[str, list[float]] = {}
    systems: dict[str, list[float]] = {}
    invalid = 0
    for _, row in frame.iterrows():
        parsed = parse_formula(row.get(formula_column))
        if not parsed.is_valid:
            invalid += 1
            continue
        error = float(row["_absolute_error"])
        for element in parsed.elements:
            elements.setdefault(element, []).append(error)
        systems.setdefault(parsed.chemical_system, []).append(error)
    by_element = _group_error_rows(elements, limits)
    by_system = _group_error_rows(systems, limits)
    return {
        "status": "READY",
        "formulaColumn": formula_column,
        "invalidFormulaRows": invalid,
        "elementGroupsOverlap": True,
        "byElement": by_element,
        "byChemicalSystem": by_system,
        "elementGroupCount": len(elements),
        "chemicalSystemGroupCount": len(systems),
        "groupsTruncated": len(elements) > len(by_element) or len(systems) > len(by_system),
        "minimumGroupSize": limits["minGroupSize"],
    }


def _group_error_rows(groups: Mapping[str, list[float]], limits: dict[str, int]) -> list[dict[str, Any]]:
    rows = [
        {
            "group": group,
            "sampleCount": len(values),
            "mae": float(np.mean(values)),
            "rmse": float(sqrt(float(np.mean(np.asarray(values) ** 2)))),
            "smallGroup": len(values) < limits["minGroupSize"],
        }
        for group, values in groups.items()
    ]
    return sorted(rows, key=lambda item: (-item["mae"], -item["sampleCount"], item["group"]))[: limits["maxChemistryGroups"]]


def _regression_sample_records(profile: DataProfile, object_id: str, frame: pd.DataFrame) -> list[dict[str, Any]]:
    formula_column = _role_column(profile, object_id, "material_formula")
    records = []
    for row_index, row in frame.iterrows():
        records.append(
            {
                **_sample_identity(profile, object_id, frame, int(row_index)),
                **_formula_identity(frame, formula_column, int(row_index)),
                "target": float(row["_target"]),
                "prediction": float(row["_prediction"]),
                "residual": float(row["_residual"]),
                "absoluteError": float(row["_absolute_error"]),
                "uncertainty": _optional_finite(row.get("_uncertainty")),
            }
        )
    return records


def _uncertainty_sample_records(profile: DataProfile, object_id: str, frame: pd.DataFrame) -> list[dict[str, Any]]:
    formula_column = _role_column(profile, object_id, "material_formula")
    return [
        {
            **_sample_identity(profile, object_id, frame, int(row_index)),
            **_formula_identity(frame, formula_column, int(row_index)),
            "target": float(row["_target"]),
            "prediction": float(row["_prediction"]),
            "absoluteError": float(row["_absolute_error"]),
            "uncertainty": float(row["_uncertainty"]),
        }
        for row_index, row in frame.iterrows()
    ]


def _reliability_bins(frame: pd.DataFrame, max_bins: int) -> list[dict[str, Any]]:
    ordered = frame.sort_values(["_uncertainty"], kind="stable")
    count = min(max_bins, len(ordered))
    return [
        {
            "bin": index,
            "sampleCount": len(chunk),
            "meanUncertainty": float(chunk["_uncertainty"].mean()),
            "meanAbsoluteError": float(chunk["_absolute_error"].mean()),
        }
        for index, indices in enumerate(np.array_split(np.arange(len(ordered)), count))
        if len(indices) and not (chunk := ordered.iloc[indices]).empty
    ]


def _error_decay(frame: pd.DataFrame) -> list[dict[str, Any]]:
    ordered = frame.sort_values(["_uncertainty"], kind="stable")
    points = []
    for fraction in (1.0, 0.8, 0.5, 0.2):
        count = max(1, min(len(ordered), ceil(len(ordered) * fraction)))
        retained = ordered.iloc[:count]
        points.append({"retainedFraction": fraction, "retainedSamples": count, "mae": float(retained["_absolute_error"].mean())})
    return points


def _probability_map(profile: DataProfile, object_id: str, group_id: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for column in profile.semanticColumns:
        if column.objectId != object_id:
            continue
        for role in column.roles:
            if role.role == "class_probability" and role.groupId == group_id:
                label = _class_value(role.details.get("class"))
                if label is not None:
                    result[label] = column.column
    return dict(sorted(result.items()))


def _validated_probabilities(table: pd.DataFrame, mapping: Mapping[str, str], tool_id: str) -> pd.DataFrame:
    if not mapping:
        return pd.DataFrame(index=table.index)
    frame = pd.DataFrame(
        {label: pd.to_numeric(table[column], errors="coerce") for label, column in mapping.items()},
        index=table.index,
    )
    finite_rows = frame.notna().all(axis=1)
    if bool(((frame < 0) | (frame > 1)).where(frame.notna(), False).any().any()):
        raise _input_error(tool_id, "Class probabilities must be within [0, 1].", "invalid_probability_range")
    if bool((frame.loc[finite_rows].sum(axis=1) - 1.0).abs().gt(1e-6).any()):
        raise _input_error(tool_id, "Normalized class probabilities must sum to one.", "invalid_probability_normalization")
    return frame


def _probability_argmax(row: pd.Series) -> str | None:
    if row.isna().any() or row.empty:
        return None
    maximum = float(row.max())
    winners = [str(column) for column, value in row.items() if float(value) == maximum]
    if len(winners) != 1:
        return None
    return winners[0]


def _sample_identity(profile: DataProfile, object_id: str, table: pd.DataFrame, row_index: int) -> dict[str, Any]:
    explicit = profile.sampleIdentity.explicitColumn if profile.sampleIdentity and profile.sampleIdentity.policy == "explicit_column" else None
    if explicit and explicit in table.columns and not pd.isna(table.at[row_index, explicit]):
        sample_ref = str(table.at[row_index, explicit])
        return {
            "sampleRef": sample_ref,
            "sampleKey": f"{object_id}:{sample_ref}",
            "identitySource": "explicit_column",
            "objectId": object_id,
            "rowIndex": row_index,
        }
    object_hash = next((item.objectHash for item in profile.resourceSemantics if item.objectId == object_id), profile.semanticHash or "unknown")
    sample_ref = stable_sample_reference(
        dataset_id=profile.datasetId,
        dataset_version=profile.version,
        object_hash=object_hash,
        row_index=row_index,
    )
    return {
        "sampleRef": sample_ref,
        "sampleKey": f"{object_id}:{sample_ref}",
        "identitySource": "dataset_version_object_hash_row_index",
        "objectId": object_id,
        "rowIndex": row_index,
    }


def _formula_identity(table: pd.DataFrame, formula_column: str | None, row_index: int) -> dict[str, Any]:
    if not formula_column or formula_column not in table.columns or pd.isna(table.at[row_index, formula_column]):
        return {"formula": None, "reducedFormula": None, "chemicalSystem": None}
    formula = str(table.at[row_index, formula_column])
    parsed = parse_formula(formula)
    return {
        "formula": formula,
        "reducedFormula": parsed.reduced_formula if parsed.is_valid else None,
        "chemicalSystem": parsed.chemical_system if parsed.is_valid else None,
    }


def _compatible_unit(profile: DataProfile, object_id: str, group_id: str, target: str, prediction: str, tool_id: str) -> tuple[str | None, str | None]:
    target_unit = _column_unit(profile, object_id, group_id, target)
    prediction_unit = _column_unit(profile, object_id, group_id, prediction)
    if target_unit and prediction_unit and target_unit != prediction_unit:
        raise _input_error(tool_id, "Target and prediction units are incompatible.", "incompatible_units", targetUnit=target_unit, predictionUnit=prediction_unit)
    if target_unit and prediction_unit:
        return target_unit, None
    return None, "UNIT_UNAVAILABLE"


def _column_unit(profile: DataProfile, object_id: str, group_id: str, name: str) -> str | None:
    return next((column.unit for column in profile.semanticColumns if column.objectId == object_id and column.column == name and any(role.groupId == group_id for role in column.roles)), None)


def _uncertainty_kind(profile: DataProfile, object_id: str, group_id: str, name: str) -> str:
    allowlist = {"standard_deviation", "variance", "generic_uncertainty", "interval"}
    for column in profile.semanticColumns:
        if column.objectId == object_id and column.column == name:
            for role in column.roles:
                if role.role == "regression_uncertainty" and role.groupId == group_id:
                    kind = role.details.get("uncertaintyKind")
                    if kind in allowlist:
                        return str(kind)
    return "source_defined_uncertainty"


def _regression_series(group: Any) -> list[tuple[str, str, list[str]]]:
    values: list[tuple[str, str, list[str]]] = []
    seen: set[str] = set()
    for binding in group.seriesBindings:
        if binding.predictionColumn and binding.predictionColumn not in seen:
            seen.add(binding.predictionColumn)
            values.append((binding.seriesId, binding.predictionColumn, list(binding.uncertaintyColumns)))
    for prediction in group.predictionColumns:
        if prediction not in seen:
            seen.add(prediction)
            values.append((prediction, prediction, list(group.uncertaintyColumns) if len(group.predictionColumns) == 1 else []))
    return values


def _group_object_ids(profile: DataProfile, group_id: str) -> list[str]:
    return sorted({column.objectId for column in profile.semanticColumns if any(role.groupId == group_id for role in column.roles)})


def _role_column(profile: DataProfile, object_id: str, role_name: str) -> str | None:
    values = sorted({column.column for column in profile.semanticColumns if column.objectId == object_id and any(role.role == role_name for role in column.roles)})
    return values[0] if len(values) == 1 else None


def _table_for_object(tables: Mapping[str, pd.DataFrame], object_id: str, tool_id: str) -> pd.DataFrame:
    if object_id in tables:
        return tables[object_id]
    if len(tables) == 1:
        return next(iter(tables.values()))
    raise _input_error(tool_id, "Profile task table was not resolved.", "table_object_missing", objectId=object_id)


def _limits(context: ToolExecutionContext, params: Mapping[str, Any]) -> dict[str, int]:
    resource = context.resource_limits
    return {
        "maxRows": int(resource.get("maxRows", 100_000)),
        "maxModels": int(resource.get("maxModels", 16)),
        "maxClasses": int(resource.get("maxClasses", 64)),
        "maxChemistryGroups": min(int(params.get("maxChemistryGroups") or 128), int(resource.get("maxChemistryGroups", 256))),
        "maxHighErrorRows": min(int(params.get("maxTableRows") or 100), int(resource.get("maxTableRows", 200))),
        "maxTableRows": min(int(params.get("maxTableRows") or 100), int(resource.get("maxTableRows", 200))),
        "maxPlotPoints": min(int(params.get("maxPlotPoints") or 2_000), int(resource.get("maxPlotPoints", 10_000))),
        "maxCurvePoints": min(int(params.get("maxCurvePoints") or 1_000), int(resource.get("maxCurvePoints", 5_000))),
        "maxUncertaintyBins": min(int(params.get("uncertaintyBins") or 10), int(resource.get("maxUncertaintyBins", 50))),
        "histogramBins": min(int(params.get("histogramBins") or 30), int(resource.get("maxHistogramBins", 100))),
        "minGroupSize": int(params.get("minGroupSize") or 3),
    }


def _check_table_cap(table: pd.DataFrame, limits: Mapping[str, int], tool_id: str) -> None:
    if len(table) > limits["maxRows"]:
        raise _resource_error(tool_id, "Materials ML table exceeds the row cap.", rows=len(table), maxRows=limits["maxRows"])


def _coerce_profile(value: Any, tool_id: str) -> DataProfile | None:
    if isinstance(value, DataProfile):
        return value
    if isinstance(value, Mapping) and value.get("profileContractVersion") is not None:
        try:
            return DataProfile.model_validate(value)
        except Exception as exc:
            raise _input_error(tool_id, "Profile 2.0 input is invalid.", "profile_validation_failed") from exc
    return None


def _dataset_binding(profile: DataProfile) -> dict[str, Any]:
    resource_bindings = [
        {"objectId": item.objectId, "objectType": item.objectType, "objectHash": item.objectHash}
        for item in sorted(profile.resourceSemantics, key=lambda item: item.objectId)
    ]
    return {
        "datasetId": profile.datasetId,
        "datasetVersion": profile.version,
        "profileId": profile.profileId,
        "profileContractVersion": profile.profileContractVersion,
        "semanticHash": profile.semanticHash,
        "datasetContentHash": content_hash(resource_bindings),
        "resourceBindings": resource_bindings,
    }


def _security() -> dict[str, bool]:
    return {"artifactJavaScript": False, "externalUrls": False, "externalAssets": False, "executableContent": False}


def _summary_markdown(title: str, payload: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            f"- Dataset: `{payload['dataset']['datasetId']}`",
            f"- Profile: `{payload['dataset']['profileId']}`",
            f"- Evaluations: {len(payload['evaluations'])}",
            "- Scientific authority: deterministic backend artifact",
            "- Interpretation boundary: performance diagnostics do not establish material or model scientific validity.",
        ]
    )


def _json_payload(artifact_type: ArtifactType, file_name: str, content: Any) -> ArtifactPayload:
    return ArtifactPayload(artifact_type=artifact_type, file_name=file_name, content=stable_json_dumps(content), media_type="application/json")


def _bounded_indices(total: int, limit: int) -> list[int]:
    if total <= limit:
        return list(range(total))
    if limit <= 1:
        return [0]
    return [(index * (total - 1)) // (limit - 1) for index in range(limit)]


def _bounded_points(points: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return [points[index] for index in _bounded_indices(len(points), max(2, limit))]


def _safe_correlation(left: pd.Series, right: pd.Series, *, method: str) -> float | None:
    if len(left) < 2 or float(left.std()) == 0 or float(right.std()) == 0:
        return None
    value = left.corr(right, method=method)
    return float(value) if value is not None and isfinite(float(value)) else None


def _mean_defined(values: Iterable[float | None]) -> float | None:
    defined = [float(value) for value in values if value is not None]
    return float(np.mean(defined)) if defined else None


def _optional_finite(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if isfinite(parsed) else None


def _classification_warnings(metrics: Mapping[str, Any]) -> list[str]:
    warnings = ["CLASSIFICATION_PERFORMANCE_NOT_SCIENTIFIC_VALIDITY"]
    supports = [int(item["support"]) for item in metrics["perClass"] if int(item["support"]) > 0]
    if supports and max(supports) >= 4 * min(supports):
        warnings.append("CLASS_IMBALANCE_PRESENT")
    return warnings


def _class_value(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    normalized = str(value).strip()
    return normalized or None


def _resolve_probability_labels(mapping: Mapping[str, str], known_classes: Iterable[str]) -> dict[str, str]:
    classes = sorted(set(known_classes))
    resolved: dict[str, str] = {}
    for profile_label, column in sorted(mapping.items()):
        exact = [label for label in classes if label == profile_label]
        folded = [label for label in classes if label.casefold() == profile_label.casefold()]
        if exact:
            label = exact[0]
        elif len(folded) == 1:
            label = folded[0]
        elif len(folded) > 1:
            raise _input_error(
                CLASSIFICATION_TOOL_ID,
                "Probability class identity is ambiguous after case-insensitive matching.",
                "ambiguous_probability_class_mapping",
                probabilityClass=profile_label,
            )
        else:
            label = profile_label
        if label in resolved and resolved[label] != column:
            raise _input_error(
                CLASSIFICATION_TOOL_ID,
                "Multiple probability columns resolve to one class identity.",
                "duplicate_probability_class_mapping",
                probabilityClass=label,
            )
        resolved[label] = column
    return dict(sorted(resolved.items()))


def _resolve_requested_class(requested: str | None, classes: Iterable[str]) -> str | None:
    if requested is None:
        return None
    values = sorted(set(classes))
    if requested in values:
        return requested
    folded = [label for label in values if label.casefold() == requested.casefold()]
    if len(folded) == 1:
        return folded[0]
    if len(folded) > 1:
        raise _input_error(
            CLASSIFICATION_TOOL_ID,
            "Positive class identity is ambiguous after case-insensitive matching.",
            "ambiguous_positive_class",
            positiveClass=requested,
        )
    return requested


def _only(values: Iterable[Any], tool_id: str = REGRESSION_TOOL_ID, error_type: str = "ambiguous_binding") -> Any:
    items = list(values)
    if len(items) != 1:
        raise _input_error(tool_id, "Exactly one semantic binding is required.", error_type, count=len(items))
    return items[0]


def _require_columns(table: pd.DataFrame, columns: Iterable[str | None], tool_id: str) -> None:
    missing = [column for column in columns if column and column not in table.columns]
    if missing:
        raise _input_error(tool_id, "Profile-bound column is absent from the table.", "missing_profile_column", columns=missing)


def _ref_value(input_ref: Any, field: str, default: Any = None) -> Any:
    if hasattr(input_ref, field):
        return getattr(input_ref, field)
    if isinstance(input_ref, Mapping):
        return input_ref.get(field, default)
    return default


def _looks_like_table(value: Any) -> bool:
    return isinstance(value, list) and (not value or all(isinstance(item, Mapping) for item in value))


def _input_error(tool_id: str, message: str, error_type: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError("TOOL_INPUT_INVALID", message, tool_id, details={"errorType": error_type, **details})


def _resource_error(tool_id: str, message: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError("TOOL_RESOURCE_LIMIT", message, tool_id, details=details)
