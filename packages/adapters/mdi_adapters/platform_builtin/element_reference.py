"""Controlled reference figures independent of user material datasets."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from jsonschema import Draft202012Validator
import plotly.graph_objects as go
import pymatviz as pmv

from mdi_artifact_core import ArtifactPayload, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType
from mdi_tool_registry.element_reference import ELEMENT_REFERENCE_SOURCE, element_reference, element_reference_params_schema

from ..base import BaseToolAdapter
from ..composition_common import plotly_metadata
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


@dataclass(frozen=True)
class ReferenceFigure:
    metadata: dict[str, Any]
    table: dict[str, Any]
    params: dict[str, Any]
    summary: str


class ReferencePeriodicTableAdapter(BaseToolAdapter):
    tool_id = "reference.periodic_table"
    adapter_version = "1.0.0"
    comparison = False

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> dict[str, Any]:
        if input_refs or context.dataset_id is not None:
            raise ToolExecutionError("TOOL_INPUT_INVALID", "元素参考工具需要项目范围，不能绑定样品数据。", self.tool_id)
        errors = list(Draft202012Validator(element_reference_params_schema(comparison=self.comparison)).iter_errors(params))
        if errors:
            raise ToolExecutionError("TOOL_PARAM_INVALID", "请选择受支持的元素符号与参考性质。", self.tool_id)
        reference = element_reference()
        selected = params.get("elements") or [item["symbol"] for item in reference["records"]]
        if not set(params.get("highlight_elements", [])).issubset(selected):
            raise ToolExecutionError("TOOL_PARAM_INVALID", "高亮元素必须在所选元素范围内。", self.tool_id)
        self._input_hashes = [ELEMENT_REFERENCE_SOURCE.contentHash]
        return reference

    def run(self, prepared: dict[str, Any], params: dict[str, Any]) -> ReferenceFigure:
        property_id = params.get("property", "atomic_number")
        definition = prepared["properties"][property_id]
        field = "covalent_radius_angstrom" if property_id == "covalent_radius" else "atomic_number"
        by_symbol = {item["symbol"]: item for item in prepared["records"]}
        symbols = params.get("elements") or list(by_symbol)
        records = [by_symbol[symbol] for symbol in symbols]
        values = {item["symbol"]: item[field] for item in records if item[field] is not None}
        missing = [item["symbol"] for item in records if item[field] is None]
        if not values:
            raise ToolExecutionError("TOOL_INPUT_INVALID", "参考资料未覆盖所选元素的此项性质，请更换元素或性质。", self.tool_id,
                                     details={"errorType": "REFERENCE_VALUES_UNAVAILABLE", "missingElements": missing})
        label = definition["label"] + ("（Å）" if definition["unit"] == "angstrom" else "")
        title = ("元素性质比较" if self.comparison else "元素周期表") + f" · {label}"
        if self.comparison:
            figure = go.Figure(go.Bar(x=list(values), y=list(values.values()), marker_color="#1c7665",
                                     hovertemplate="%{x}: %{y}<extra></extra>"))
            figure.update_layout(title=title, xaxis_title="元素", yaxis_title=label,
                                 xaxis={"type": "category"}, yaxis={"rangemode": "tozero"}, showlegend=False)
        else:
            figure = pmv.ptable_heatmap(values, log=False, colorscale="viridis", show_values=True,
                                       hover_props=None, hover_data={item["symbol"]: item["name"] for item in records})
            figure.update_layout(title_text=title)
            highlighted = set(params.get("highlight_elements", []))
            for annotation in figure.layout.annotations:
                symbol = re.sub(r"<[^>]*>", "", annotation.text.replace("<br>", "\n")).split("\n")[0].strip()
                if symbol not in highlighted:
                    continue
                for name, width, color in [("outer", 5, "#ffffff"), ("inner", 2.5, "#17211e")]:
                    figure.add_shape(type="rect", name=f"highlight-{name}:{symbol}",
                        xref="x", yref="y", x0=annotation.x - .44, x1=annotation.x + .44,
                        y0=annotation.y - .44, y1=annotation.y + .44,
                        line={"width": width, "color": color}, fillcolor="rgba(0,0,0,0)", layer="above")
        source = {**ELEMENT_REFERENCE_SOURCE.model_dump(mode="json"), "sources": prepared["sources"], "propertyDefinition": definition}
        metadata = {
            "schemaVersion": "mdi.reference.element-figure/1.0", "artifactType": self.tool_id,
            "chartType": "reference_element_comparison" if self.comparison else "periodic_table_reference",
            "title": title, "property": property_id, "valueLabel": label, "unit": definition["unit"],
            "elementValues": values, "selectedElements": symbols, "missingElements": missing,
            "highlightElements": params.get("highlight_elements", []),
            "elementIdentities": [{"symbol": item["symbol"], "atomicNumber": item["atomic_number"], "name": item["name"]} for item in prepared["records"]],
            "elementCount": len(records), "valueCount": len(values), "log": False,
            "referenceSource": source, "inputOrigin": "PLATFORM_REFERENCE", "sampleAnalysis": False,
            "plotlyFigure": plotly_metadata(figure),
        }
        table = {"schemaVersion": "mdi.reference.element-table/1.0", "artifactType": f"{self.tool_id}.table",
                 "title": title, "columns": list(dict.fromkeys(["symbol", "name", "atomic_number", field])),
                 "rows": [{"symbol": item["symbol"], "name": item["name"], "atomic_number": item["atomic_number"], field: item[field]} for item in records],
                 "referenceSource": source, "property": property_id, "unit": definition["unit"],
                 "inputOrigin": "PLATFORM_REFERENCE", "sampleAnalysis": False, "missingElements": missing,
                 "elementCount": len(records), "valueCount": len(values), "selectedElements": symbols,
                 "highlightElements": params.get("highlight_elements", [])}
        summary = f"# {title}\n\n平台参考数据；{len(records)} 种元素，{len(values)} 个有效参考值。\n\n"
        if missing:
            summary += f"资料未覆盖：{', '.join(missing)}。\n\n"
        summary += f"参考版本：{ELEMENT_REFERENCE_SOURCE.version}；性质定义：{definition['definition']}\n"
        if definition.get("citation"):
            summary += f"\n{definition['citation']}\n"
        return ReferenceFigure(metadata, table, dict(params), summary)

    def export(self, result: ReferenceFigure, artifact_types: list[ArtifactType]) -> list[Artifact]:
        recipe = self.recipe_payload(name=result.metadata["title"], params=result.params, artifact_types=artifact_types)
        recipe["inputRequirements"] = [{"kind": "PLATFORM_REFERENCE", **ELEMENT_REFERENCE_SOURCE.model_dump(mode="json")}]
        definitions = {
            ArtifactType.plotly_json: ("element_figure.json", result.metadata, "application/json"),
            ArtifactType.table_json: ("element_reference.json", result.table, "application/json"),
            ArtifactType.summary_md: ("summary.md", result.summary, "text/markdown"),
            ArtifactType.recipe_json: ("recipe.json", recipe, "application/json"),
        }
        payloads = []
        for kind in artifact_types:
            if kind not in definitions:
                raise ToolExecutionError("TOOL_PARAM_INVALID", "不支持此参考图导出类型。", self.tool_id)
            name, content, media = definitions[kind]
            payloads.append(ArtifactPayload(file_name=name, artifact_type=kind,
                content=(content if isinstance(content, str) else stable_json_dumps(content)).encode("utf-8"), media_type=media))
        return self.export_payloads(payloads, {"schemaVersion": "mdi.reference.elements/1.0", "inputOrigin": "PLATFORM_REFERENCE",
                                              "referenceSources": [ELEMENT_REFERENCE_SOURCE.model_dump(mode="json")], "sampleAnalysis": False})


class ReferenceElementComparisonAdapter(ReferencePeriodicTableAdapter):
    tool_id = "reference.compare_elements"
    comparison = True
