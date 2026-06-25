from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .errors import ToolExecutionError


TARGET_COLUMN_CANDIDATES = ("target", "y_true", "actual", "true", "y")
PREDICTION_COLUMN_CANDIDATES = ("prediction", "pred", "y_pred", "predicted", "estimate")


@dataclass(frozen=True)
class PreparedRegressionFrame:
    dataframe: pd.DataFrame
    target_column: str
    prediction_column: str


def coerce_dataframe(raw: Any, *, tool_id: str) -> pd.DataFrame:
    if isinstance(raw, pd.DataFrame):
        return raw.copy()
    if isinstance(raw, dict) and "dataframe" in raw:
        return coerce_dataframe(raw["dataframe"], tool_id=tool_id)
    if isinstance(raw, dict) and "records" in raw:
        return pd.DataFrame(raw["records"])
    if isinstance(raw, list):
        return pd.DataFrame(raw)
    raise ToolExecutionError(
        "TOOL_INPUT_INVALID",
        "ML adapter input must be a pandas DataFrame or table records.",
        tool_id,
        details={"inputType": type(raw).__name__},
    )


def prepare_regression_frame(raw: Any, params: dict[str, Any], *, tool_id: str) -> PreparedRegressionFrame:
    dataframe = coerce_dataframe(raw, tool_id=tool_id)
    target_column = _resolve_column(
        dataframe,
        params.get("targetColumn"),
        TARGET_COLUMN_CANDIDATES,
        role="target",
        tool_id=tool_id,
    )
    prediction_column = _resolve_column(
        dataframe,
        params.get("predictionColumn"),
        PREDICTION_COLUMN_CANDIDATES,
        role="prediction",
        tool_id=tool_id,
    )
    for column, role in ((target_column, "target"), (prediction_column, "prediction")):
        if not pd.api.types.is_numeric_dtype(dataframe[column]):
            raise ToolExecutionError(
                "TOOL_INPUT_INVALID",
                f"{role} column must be numeric.",
                tool_id,
                details={"column": column, "role": role},
            )
    clean = dataframe.dropna(subset=[target_column, prediction_column]).copy()
    if clean.empty:
        raise ToolExecutionError("TOOL_INPUT_INVALID", "No non-null target/prediction rows are available.", tool_id)
    return PreparedRegressionFrame(dataframe=clean, target_column=target_column, prediction_column=prediction_column)


def regression_metrics(prepared: PreparedRegressionFrame) -> dict[str, float | int]:
    target = prepared.dataframe[prepared.target_column].astype(float)
    prediction = prepared.dataframe[prepared.prediction_column].astype(float)
    error = prediction - target
    abs_error = error.abs()
    sq_error = error**2
    target_mean = target.mean()
    ss_tot = float(((target - target_mean) ** 2).sum())
    ss_res = float(sq_error.sum())
    return {
        "n": int(len(prepared.dataframe)),
        "mae": float(abs_error.mean()),
        "rmse": float(sq_error.mean() ** 0.5),
        "r2": float(1 - ss_res / ss_tot) if ss_tot else 1.0,
        "meanError": float(error.mean()),
        "maxAbsError": float(abs_error.max()),
    }


def outlier_records(prepared: PreparedRegressionFrame, *, top_k: int = 10) -> list[dict[str, Any]]:
    frame = prepared.dataframe.copy()
    frame["error"] = frame[prepared.prediction_column].astype(float) - frame[prepared.target_column].astype(float)
    frame["abs_error"] = frame["error"].abs()
    ordered = frame.sort_values("abs_error", ascending=False).head(top_k)
    return ordered.to_dict(orient="records")


def table_to_csv(records: list[dict[str, Any]]) -> str:
    if not records:
        return ""
    return pd.DataFrame(records).to_csv(index=False)


def _resolve_column(
    dataframe: pd.DataFrame,
    requested: Any,
    candidates: tuple[str, ...],
    *,
    role: str,
    tool_id: str,
) -> str:
    columns = list(dataframe.columns)
    if requested:
        if requested not in columns:
            raise ToolExecutionError(
                "TOOL_INPUT_INVALID",
                f"Requested {role} column does not exist.",
                tool_id,
                details={"column": requested, "availableColumns": columns},
            )
        return str(requested)
    lowered = {str(column).lower(): str(column) for column in columns}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    raise ToolExecutionError(
        "TOOL_INPUT_INVALID",
        f"Could not infer {role} column.",
        tool_id,
        details={"availableColumns": columns},
    )
