from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mdi_artifact_core import ArtifactPayload, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..composition_common import formula_statistics, prepare_composition_input
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


@dataclass(frozen=True)
class FormulaStatisticsResult:
    payload: dict[str, Any]
    params: dict[str, Any]


class FormulaStatisticsAdapter(BaseToolAdapter):
    tool_id = "composition.formula_statistics"
    adapter_version = "0.1.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> Any:
        if not self._resolved_inputs:
            raise ToolExecutionError(
                "TOOL_INPUT_INVALID",
                "formula_statistics requires table or formula input.",
                self.tool_id,
                details={"errorType": "unsupported_profile_type"},
            )
        return prepare_composition_input(self._resolved_inputs[0], {**params, "_toolId": self.tool_id}, tool_id=self.tool_id)

    def run(self, prepared: Any, params: dict[str, Any]) -> FormulaStatisticsResult:
        stats = formula_statistics(prepared, params, tool_id=self.tool_id)
        return FormulaStatisticsResult(payload=stats.payload, params=params)

    def export(self, result: FormulaStatisticsResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
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
                    file_name="formula_statistics.json",
                    content=stable_json_dumps(result.payload),
                    media_type="application/json",
                )
            )
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
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=stable_json_dumps(
                        self.recipe_payload(
                            name="Formula statistics",
                            params=result.params,
                            artifact_types=list(requested),
                        )
                    ),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={
                "adapter": self.tool_id,
                "formulaColumn": result.payload["formulaColumn"],
                "parsedFormulaCount": result.payload["parsedFormulaCount"],
            },
        )


def _summary_markdown(payload: dict[str, Any]) -> str:
    top_elements = sorted(payload["elementCounts"].items(), key=lambda item: item[1], reverse=True)[:8]
    return "\n".join(
        [
            "# Formula Statistics",
            "",
            f"- Formula column: `{payload['formulaColumn']}`",
            f"- Rows: {payload['rowCount']}",
            f"- Formulas: {payload['formulaCount']}",
            f"- Parsed formulas: {payload['parsedFormulaCount']}",
            f"- Failed formulas: {payload['failedFormulaCount']}",
            f"- Unique formulas: {payload['uniqueFormulaCount']}",
            f"- Elements: {', '.join(element for element, _ in top_elements)}",
            f"- Warnings: {', '.join(payload['warnings']) if payload['warnings'] else 'none'}",
        ]
    )
