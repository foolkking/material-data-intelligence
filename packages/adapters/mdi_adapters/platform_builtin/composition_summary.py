from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from pymatgen.core import Composition

from mdi_artifact_core import ArtifactPayload, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from ..ml_common import coerce_dataframe


FORMULA_COLUMN_CANDIDATES = ("formula", "composition", "reduced_formula", "pretty_formula", "formula_pretty")


@dataclass(frozen=True)
class CompositionSummaryResult:
    summary: dict[str, Any]
    params: dict[str, Any]


class CompositionSummaryAdapter(BaseToolAdapter):
    tool_id = "composition.summary"
    adapter_version = "0.1.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> list[str]:
        if not self._resolved_inputs:
            raise ToolExecutionError(
                code="TOOL_INPUT_INVALID",
                message="composition.summary requires formula or table input.",
                tool_id=self.tool_id,
                details={"errorType": "unsupported_profile_type"},
            )
        value = self._resolved_inputs[0]
        if isinstance(value, (list, tuple)):
            formulas = [str(item) for item in value if str(item).strip()]
            if not formulas:
                raise self._missing_formula_column()
            return formulas

        frame = coerce_dataframe(value, tool_id=self.tool_id)
        requested_column = params.get("formulaColumn") or params.get("compositionColumn")
        column = str(requested_column) if requested_column else self._infer_formula_column(frame)
        if not column or column not in frame.columns:
            raise self._missing_formula_column(column)
        formulas = [str(item) for item in frame[column].dropna().tolist() if str(item).strip()]
        if not formulas:
            raise self._missing_formula_column(column)
        return formulas

    def run(self, prepared: list[str], params: dict[str, Any]) -> CompositionSummaryResult:
        formula_column = params.get("formulaColumn") or params.get("compositionColumn") or "formula"
        element_counts: dict[str, float] = {}
        system_types: dict[str, int] = {}
        failed: list[str] = []
        parsed_count = 0
        for formula in prepared:
            try:
                composition = Composition(formula)
            except Exception:
                failed.append(formula)
                continue
            parsed_count += 1
            elements = sorted(str(element) for element in composition.elements)
            system_type = self._system_type(len(elements))
            system_types[system_type] = system_types.get(system_type, 0) + 1
            for element, amount in composition.element_composition.items():
                symbol = str(element)
                element_counts[symbol] = element_counts.get(symbol, 0.0) + float(amount)

        if parsed_count == 0:
            raise ToolExecutionError(
                code="TOOL_INPUT_INVALID",
                message="No formulas could be parsed.",
                tool_id=self.tool_id,
                details={"errorType": "invalid_formula", "failedFormulaCount": len(failed)},
            )

        total_amount = sum(element_counts.values()) or 1.0
        element_fractions = {
            element: amount / total_amount for element, amount in sorted(element_counts.items(), key=lambda item: item[0])
        }
        max_systems = int(params.get("maxSystems") or 20)
        summary = {
            "formulaColumn": formula_column,
            "formulaCount": int(len(prepared)),
            "parsedFormulaCount": int(parsed_count),
            "failedFormulaCount": int(len(failed)),
            "elementCounts": {element: float(amount) for element, amount in sorted(element_counts.items())},
            "elementFractions": element_fractions,
            "systemTypes": dict(sorted(system_types.items(), key=lambda item: item[0])[:max_systems]),
            "warnings": [f"{len(failed)} formulas could not be parsed."] if failed else [],
        }
        return CompositionSummaryResult(summary=summary, params=params)

    def export(self, result: CompositionSummaryResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        requested = set(artifact_types) or {
            ArtifactType.table_json,
            ArtifactType.summary_md,
            ArtifactType.recipe_json,
        }
        payloads: list[ArtifactPayload] = []
        if ArtifactType.table_json in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.table_json,
                    file_name="composition_summary.json",
                    content=stable_json_dumps(result.summary),
                    media_type="application/json",
                )
            )
        if ArtifactType.summary_md in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=self._summary_markdown(result.summary),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=stable_json_dumps(
                        self.recipe_payload(
                            name="Composition summary",
                            params=result.params,
                            artifact_types=list(requested),
                        )
                    ),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={"adapter": "composition.summary", "formulaCount": result.summary["formulaCount"]},
        )

    @staticmethod
    def _infer_formula_column(frame: pd.DataFrame) -> str:
        lowered = {str(column).lower(): str(column) for column in frame.columns}
        for candidate in FORMULA_COLUMN_CANDIDATES:
            if candidate in lowered:
                return lowered[candidate]
        return ""

    @staticmethod
    def _system_type(size: int) -> str:
        labels = {
            1: "unary",
            2: "binary",
            3: "ternary",
            4: "quaternary",
        }
        return labels.get(size, f"{size}-component")

    def _missing_formula_column(self, column: str | None = None) -> ToolExecutionError:
        details: dict[str, Any] = {"errorType": "missing_formula_column"}
        if column:
            details["column"] = column
        return ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message="No formula or composition column was found.",
            tool_id=self.tool_id,
            details=details,
        )

    @staticmethod
    def _summary_markdown(summary: dict[str, Any]) -> str:
        top_elements = sorted(summary["elementCounts"].items(), key=lambda item: item[1], reverse=True)[:8]
        return "\n".join(
            [
                "# Composition Summary",
                "",
                f"- Formulas: {summary['formulaCount']}",
                f"- Parsed formulas: {summary['parsedFormulaCount']}",
                f"- Failed formulas: {summary['failedFormulaCount']}",
                f"- Top elements: {', '.join(element for element, _ in top_elements)}",
            ]
        )
