from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import pandas as pd
import plotly.graph_objects as go
from pymatgen.core import Composition, Element

from mdi_artifact_core import ArtifactPayload, stable_json_dumps
from mdi_schemas import ArtifactType

from .base import BaseToolAdapter
from .errors import ToolExecutionError
from .ml_common import coerce_dataframe
from .plotly_export import plotly_payloads


FORMULA_COLUMN_CANDIDATES = (
    "formula",
    "composition",
    "reduced_formula",
    "pretty_formula",
    "material_formula",
    "chemical_formula",
    "formula_pretty",
)

SYSTEM_TYPE_KEYS = ("unary", "binary", "ternary", "quaternary", "quinary_plus")


@dataclass(frozen=True)
class ParsedFormula:
    formula: str
    reduced_formula: str
    elements: tuple[str, ...]
    amounts: dict[str, float]
    chemical_system: str
    arity: int
    is_valid: bool
    warning: str | None = None


@dataclass(frozen=True)
class PreparedCompositionTable:
    frame: pd.DataFrame | None
    formulas: list[str]
    formula_column: str
    row_count: int


@dataclass(frozen=True)
class FormulaStats:
    payload: dict[str, Any]
    parsed: list[ParsedFormula]
    failed: list[ParsedFormula]


def prepare_composition_input(raw: Any, params: dict[str, Any], *, tool_id: str) -> PreparedCompositionTable:
    """Resolve formula values from table, formula collections, or Composition objects."""
    if isinstance(raw, dict) and "formulas" in raw:
        formulas = _coerce_formula_sequence(raw["formulas"])
        return _prepared_from_formula_list(formulas, params)
    if isinstance(raw, (list, tuple)) and not _looks_like_records(raw):
        formulas = _coerce_formula_sequence(raw)
        return _prepared_from_formula_list(formulas, params)
    if isinstance(raw, (str, Composition)):
        return _prepared_from_formula_list(_coerce_formula_sequence([raw]), params)

    frame = coerce_dataframe(raw, tool_id=tool_id)
    if frame.empty:
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message="Composition input table is empty.",
            tool_id=tool_id,
            details={"errorType": "empty_table"},
        )
    column = resolve_formula_column(frame, params, tool_id=tool_id)
    formulas = [str(item).strip() for item in frame[column].dropna().tolist() if str(item).strip()]
    if not formulas:
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message=f"Formula column `{column}` has no values.",
            tool_id=tool_id,
            details={"errorType": "empty_formula_values", "column": column},
        )
    return PreparedCompositionTable(frame=frame, formulas=formulas, formula_column=column, row_count=int(len(frame)))


def resolve_formula_column(frame: pd.DataFrame, params: dict[str, Any], *, tool_id: str) -> str:
    requested = params.get("formulaColumn") or params.get("compositionColumn")
    if requested:
        column = str(requested)
        if column in frame.columns:
            return column
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message=f"Formula column not found: {column}",
            tool_id=tool_id,
            details={"errorType": "missing_formula_column", "column": column, "availableColumns": list(frame.columns)},
        )

    lowered = {str(column).lower(): str(column) for column in frame.columns}
    for candidate in FORMULA_COLUMN_CANDIDATES:
        if candidate in lowered:
            return lowered[candidate]

    raise ToolExecutionError(
        code="TOOL_INPUT_INVALID",
        message="No formula or composition column was found.",
        tool_id=tool_id,
        details={
            "errorType": "missing_formula_column",
            "candidateColumns": list(FORMULA_COLUMN_CANDIDATES),
            "availableColumns": list(frame.columns),
        },
    )


def formula_statistics(prepared: PreparedCompositionTable, params: dict[str, Any], *, tool_id: str) -> FormulaStats:
    max_examples = max(1, int(params.get("maxExamples") or 20))
    parsed: list[ParsedFormula] = []
    failed: list[ParsedFormula] = []
    for formula in prepared.formulas:
        item = parse_formula(formula)
        if item.is_valid:
            parsed.append(item)
        else:
            failed.append(item)

    if not parsed:
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message="No formulas could be parsed.",
            tool_id=tool_id,
            details={"errorType": "invalid_formula", "failedFormulaCount": len(failed)},
        )

    element_counts = element_value_map(parsed, mode="stoichiometric")
    occurrence_counts = element_value_map(parsed, mode="occurrence")
    fractional_counts = element_value_map(parsed, mode="fractional")
    total_amount = sum(element_counts.values()) or 1.0
    chemical_systems = _count_values(item.chemical_system for item in parsed)
    system_type_counts = {key: 0 for key in SYSTEM_TYPE_KEYS}
    for item in parsed:
        system_type_counts[system_type(item.arity)] += 1
    reduced_formulas = _count_values(item.reduced_formula for item in parsed)
    formulas = _count_values(item.formula for item in parsed)
    warnings = [f"{len(failed)} formulas could not be parsed."] if failed else []

    payload = {
        "artifactType": "composition.formula_statistics",
        "formulaColumn": prepared.formula_column,
        "rowCount": prepared.row_count,
        "formulaCount": len(prepared.formulas),
        "parsedFormulaCount": len(parsed),
        "failedFormulaCount": len(failed),
        "uniqueFormulaCount": len(formulas),
        "uniqueReducedFormulaCount": len(reduced_formulas),
        "elementCount": len(element_counts),
        "elements": sorted(element_counts),
        "elementCounts": _stable_float_map(element_counts),
        "elementFractions": _stable_float_map({key: value / total_amount for key, value in element_counts.items()}),
        "elementOccurrences": _stable_float_map(occurrence_counts),
        "elementFractionalSums": _stable_float_map(fractional_counts),
        "chemicalSystems": dict(sorted(chemical_systems.items())),
        "systemTypeCounts": system_type_counts,
        "topFormulas": [
            {"formula": formula, "count": count}
            for formula, count in sorted(formulas.items(), key=lambda item: (-item[1], item[0]))[:max_examples]
        ],
        "failedExamples": [
            {"formula": item.formula, "warning": item.warning}
            for item in failed[:max_examples]
        ],
        "warnings": warnings,
    }
    return FormulaStats(payload=payload, parsed=parsed, failed=failed)


def parse_formula(raw_formula: Any) -> ParsedFormula:
    formula = str(raw_formula).strip()
    if not formula:
        return _invalid_formula(formula, "empty_formula")
    if any(char in formula for char in "()[]{}"):
        return _invalid_formula(formula, "unsupported_parentheses_formula")

    try:
        composition = raw_formula if isinstance(raw_formula, Composition) else Composition(formula)
    except Exception:
        return _invalid_formula(formula, "invalid_formula")

    amounts: dict[str, float] = {}
    for element, amount in composition.element_composition.items():
        symbol = str(element)
        try:
            Element(symbol)
        except Exception:
            return _invalid_formula(formula, f"unknown_element:{symbol}")
        amounts[symbol] = float(amount)

    if not amounts:
        return _invalid_formula(formula, "empty_composition")
    elements = tuple(sorted(amounts))
    return ParsedFormula(
        formula=formula,
        reduced_formula=str(composition.reduced_formula),
        elements=elements,
        amounts=dict(sorted(amounts.items())),
        chemical_system="-".join(elements),
        arity=len(elements),
        is_valid=True,
    )


def element_value_map(parsed: list[ParsedFormula], *, mode: str) -> dict[str, float]:
    values: dict[str, float] = {}
    normalized_mode = normalize_count_mode(mode)
    for item in parsed:
        amount_sum = sum(item.amounts.values()) or 1.0
        for element, amount in item.amounts.items():
            if normalized_mode == "occurrence":
                increment = 1.0
            elif normalized_mode == "fractional":
                increment = float(amount) / amount_sum
            else:
                increment = float(amount)
            values[element] = values.get(element, 0.0) + increment
    return dict(sorted(values.items()))


def normalize_count_mode(mode: Any) -> str:
    normalized = str(mode or "occurrence").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "composition": "stoichiometric",
        "count": "stoichiometric",
        "formula_presence": "occurrence",
        "stoichiometric_count": "stoichiometric",
        "fraction": "fractional",
        "fractional_composition": "fractional",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in {"occurrence", "stoichiometric", "fractional"}:
        raise ValueError(f"Unsupported countMode: {mode}")
    return normalized


def system_type(arity: int) -> str:
    labels = {1: "unary", 2: "binary", 3: "ternary", 4: "quaternary"}
    return labels.get(arity, "quinary_plus")


def arity_label(arity: int) -> str:
    return system_type(arity)


def formula_list(parsed: list[ParsedFormula]) -> list[str]:
    return [item.formula for item in parsed]


def plotly_metadata(figure: Any) -> dict[str, Any]:
    return figure.to_plotly_json()


def simple_bar_figure(labels: list[str], values: list[float], *, title: str, x_title: str, y_title: str) -> go.Figure:
    figure = go.Figure(data=[go.Bar(x=labels, y=values)])
    figure.update_layout(title=title, xaxis_title=x_title, yaxis_title=y_title)
    return figure


def treemap_figure(labels: list[str], parents: list[str], values: list[float], *, title: str) -> go.Figure:
    figure = go.Figure(data=[go.Treemap(labels=labels, parents=parents, values=values, branchvalues="total")])
    figure.update_layout(title=title)
    return figure


def sunburst_figure(ids: list[str], labels: list[str], parents: list[str], values: list[float], *, title: str) -> go.Figure:
    figure = go.Figure(data=[go.Sunburst(ids=ids, labels=labels, parents=parents, values=values, branchvalues="total")])
    figure.update_layout(title=title)
    return figure


def export_composition_payloads(
    adapter: BaseToolAdapter,
    *,
    metadata: dict[str, Any],
    figure: Any | None,
    params: dict[str, Any],
    artifact_types: list[ArtifactType],
    json_name: str,
    title: str,
    provenance: dict[str, Any],
) -> list[Any]:
    requested = set(artifact_types) or {
        ArtifactType.plotly_json,
        ArtifactType.plotly_html,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
    }
    payloads: list[ArtifactPayload] = []
    if ArtifactType.plotly_json in requested:
        payloads.append(
            ArtifactPayload(
                artifact_type=ArtifactType.plotly_json,
                file_name=json_name,
                content=stable_json_dumps(metadata),
                media_type="application/json",
            )
        )
    if figure is not None:
        payloads.extend(
            plotly_payloads(
                figure,
                [artifact_type for artifact_type in requested if artifact_type != ArtifactType.plotly_json],
                stem=json_name.removesuffix(".json"),
            )
        )
    if ArtifactType.summary_md in requested:
        payloads.append(
            ArtifactPayload(
                artifact_type=ArtifactType.summary_md,
                file_name="summary.md",
                content=composition_summary_markdown(title, metadata),
                media_type="text/markdown",
            )
        )
    if ArtifactType.recipe_json in requested:
        payloads.append(
            ArtifactPayload(
                artifact_type=ArtifactType.recipe_json,
                file_name="recipe.json",
                content=stable_json_dumps(
                    adapter.recipe_payload(name=title, params=params, artifact_types=list(requested))
                ),
                media_type="application/json",
            )
        )
    return adapter.export_payloads(payloads, provenance=provenance)


def composition_summary_markdown(title: str, metadata: dict[str, Any]) -> str:
    lines = [f"# {title}", ""]
    for key in (
        "artifactType",
        "chartType",
        "formulaColumn",
        "rowCount",
        "formulaCount",
        "parsedFormulaCount",
        "failedFormulaCount",
        "elementCount",
        "countMode",
        "groupMode",
    ):
        if key in metadata:
            lines.append(f"- {key}: {metadata[key]}")
    top_elements = metadata.get("bars") or []
    if top_elements:
        labels = [str(item.get("element")) for item in top_elements[:8]]
        lines.append(f"- top elements: {', '.join(labels)}")
    groups = metadata.get("groups") or []
    if groups:
        labels = [str(item.get("label")) for item in groups[:8]]
        lines.append(f"- top groups: {', '.join(labels)}")
    warnings = metadata.get("warnings") or []
    if warnings:
        lines.append(f"- warnings: {', '.join(str(item) for item in warnings)}")
    return "\n".join(lines)


def _prepared_from_formula_list(formulas: list[str], params: dict[str, Any]) -> PreparedCompositionTable:
    formulas = [formula for formula in formulas if formula.strip()]
    if not formulas:
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message="No formula values were provided.",
            tool_id=str(params.get("_toolId") or "composition"),
            details={"errorType": "empty_formula_values"},
        )
    return PreparedCompositionTable(
        frame=None,
        formulas=formulas,
        formula_column=str(params.get("formulaColumn") or params.get("compositionColumn") or "formula"),
        row_count=len(formulas),
    )


def _coerce_formula_sequence(raw: Any) -> list[str]:
    if isinstance(raw, dict) and "formulas" in raw:
        return _coerce_formula_sequence(raw["formulas"])
    if isinstance(raw, Composition):
        return [raw.formula]
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, (list, tuple)):
        formulas: list[str] = []
        for item in raw:
            formulas.extend(_coerce_formula_sequence(item))
        return formulas
    return [str(raw)]


def _looks_like_records(raw: list[Any] | tuple[Any, ...]) -> bool:
    return bool(raw) and all(isinstance(item, dict) for item in raw)


def _invalid_formula(formula: str, warning: str) -> ParsedFormula:
    return ParsedFormula(
        formula=formula,
        reduced_formula="",
        elements=(),
        amounts={},
        chemical_system="",
        arity=0,
        is_valid=False,
        warning=warning,
    )


def _stable_float_map(values: dict[str, float]) -> dict[str, float]:
    return {key: float(value) for key, value in sorted(values.items())}


def _count_values(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "node"
