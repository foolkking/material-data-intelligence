"""Project reference results retain reference authority rather than sample refs."""
from __future__ import annotations

from dataclasses import replace
import base64
import binascii
import math
import re
import struct
from typing import Any

from jsonschema import Draft202012Validator

from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.application.scientific_results.projectors.base import ScientificResultProjectionContext
from mdi_api.application.scientific_results.projectors.canonical import FactDeclaration, ProjectorContract, _fact, _project, _semantic_id
from mdi_api.domain.scientific_results.contracts import ProvenanceRecord, ScientificFact, ScientificWarning
from mdi_schemas import AnalysisPlanV04
from mdi_tool_registry.element_reference import ELEMENT_REFERENCE_SOURCE, element_reference, element_reference_description, element_reference_params_schema


def _reference_grid(value: Any) -> list[list[float | None]] | None:
    if isinstance(value, dict):
        # Plotly 6 encodes NumPy arrays. Decode only this bounded reference grid.
        code = {"f8": ("d", 8), "f4": ("f", 4)}.get(value.get("dtype"))
        encoded = value.get("bdata")
        if (code is None or str(value.get("shape", "")).replace(" ", "") != "10,18"
                or not isinstance(encoded, str) or len(encoded) > 1920):
            return None
        try:
            raw = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error):
            return None
        if len(raw) != 180 * code[1]:
            return None
        values = struct.unpack("<" + code[0] * 180, raw)
        if any(math.isinf(item) for item in values):
            return None
        value = [[None if math.isnan(item) else item for item in values[start:start + 18]] for start in range(0, 180, 18)]
    if not isinstance(value, list) or len(value) != 10 or any(not isinstance(row, list) or len(row) != 18 for row in value):
        return None
    return value


def _figure_values_valid(payload: dict[str, Any], *, comparison: bool) -> bool:
    figure = payload.get("plotlyFigure") or {}
    traces, layout = figure.get("data"), figure.get("layout") or {}
    values = payload.get("elementValues") or {}
    if not isinstance(traces, list) or not isinstance(layout, dict):
        return False
    if comparison:
        symbols = [symbol for symbol in payload["selectedElements"] if symbol in values]
        return (len(traces) == 1 and isinstance(traces[0], dict) and traces[0].get("type") == "bar"
                and traces[0].get("x") == symbols and traces[0].get("y") == [values[symbol] for symbol in symbols])
    annotations = layout.get("annotations")
    if len(traces) != 3 or not isinstance(annotations, list) or len(annotations) != 180:
        return False
    grids = []
    for trace in traces:
        if not isinstance(trace, dict) or trace.get("type") != "heatmap" or trace.get("transpose", False):
            return False
        grid = _reference_grid(trace.get("z"))
        if grid is None:
            return False
        grids.append(grid)
    positions = {}
    occupied = set()
    for annotation in annotations:
        if not isinstance(annotation, dict):
            return False
        x, y, text = annotation.get("x"), annotation.get("y"), annotation.get("text")
        if (any(type(value) not in (int, float) or not math.isfinite(value) or int(value) != value for value in (x, y))
                or not 0 <= x < 18 or not 0 <= y < 10
                or (x, y) in occupied or not isinstance(text, str)
                or annotation.get("xref") != "x" or annotation.get("yref") != "y"):
            return False
        x, y = int(x), int(y)
        occupied.add((x, y))
        symbol = re.sub(r"<[^>]*>", "", text.replace("<br>", "\n")).split("\n")[0].strip()
        if symbol:
            if symbol in positions:
                return False
            positions[symbol] = (x, y)
        if grids[2][y][x] != values.get(symbol):
            return False
    if set(positions) != {item["symbol"] for item in payload["elementIdentities"]}:
        return False
    shapes = layout.get("shapes", [])
    if not isinstance(shapes, list) or len(shapes) != 2 * len(payload["highlightElements"]):
        return False
    for symbol in payload["highlightElements"]:
        x, y = positions[symbol]
        for kind, width, color in [("outer", 5, "#ffffff"), ("inner", 2.5, "#17211e")]:
            expected = {"name": f"highlight-{kind}:{symbol}", "type": "rect", "xref": "x", "yref": "y",
                        "x0": x - .44, "x1": x + .44, "y0": y - .44, "y1": y + .44,
                        "line": {"width": width, "color": color}, "fillcolor": "rgba(0,0,0,0)", "layer": "above"}
            if shapes.count(expected) != 1:
                return False
    return True


def _reference_payload_valid(tool_id: str, kind: str, payload: dict[str, Any], params: dict[str, Any]) -> bool:
    comparison = tool_id == "reference.compare_elements"
    if not Draft202012Validator(element_reference_params_schema(comparison=comparison)).is_valid(params):
        return False
    if kind == "recipe_json":
        steps = payload.get("steps") or []
        return (payload.get("schemaVersion") == "0.1" and len(steps) == 1
                and steps[0].get("toolId") == tool_id and steps[0].get("params") == params
                and payload.get("inputRequirements") == [{"kind": "PLATFORM_REFERENCE", **ELEMENT_REFERENCE_SOURCE.model_dump(mode="json")}])
    reference = element_reference()
    records = {item["symbol"]: item for item in reference["records"]}
    selected = params.get("elements") or list(records)
    highlighted = params.get("highlight_elements", [])
    property_id = params.get("property", "atomic_number")
    definition = reference["properties"][property_id]
    field = "covalent_radius_angstrom" if property_id == "covalent_radius" else "atomic_number"
    missing = [symbol for symbol in selected if records[symbol][field] is None]
    expected_source = {**ELEMENT_REFERENCE_SOURCE.model_dump(mode="json"), "sources": reference["sources"], "propertyDefinition": definition}
    if (not set(highlighted).issubset(selected) or payload.get("referenceSource") != expected_source
            or payload.get("property") != property_id or payload.get("unit") != definition["unit"]
            or payload.get("selectedElements") != selected or payload.get("highlightElements") != highlighted
            or payload.get("missingElements") != missing or payload.get("elementCount") != len(selected)
            or payload.get("valueCount") != len(selected) - len(missing)
            or payload.get("inputOrigin") != "PLATFORM_REFERENCE" or payload.get("sampleAnalysis") is not False):
        return False
    if kind == "table_json":
        rows = [{"symbol": symbol, "name": records[symbol]["name"], "atomic_number": records[symbol]["atomic_number"], field: records[symbol][field]} for symbol in selected]
        return (payload.get("schemaVersion") == "mdi.reference.element-table/1.0"
                and payload.get("artifactType") == f"{tool_id}.table"
                and payload.get("rows") == rows
                and payload.get("columns") == list(dict.fromkeys(["symbol", "name", "atomic_number", field])))
    if kind == "plotly_json":
        return (payload.get("schemaVersion") == "mdi.reference.element-figure/1.0"
                and payload.get("artifactType") == tool_id
                and payload.get("elementValues") == {symbol: records[symbol][field] for symbol in selected if symbol not in missing}
                and payload.get("elementIdentities") == [{"symbol": item["symbol"], "atomicNumber": item["atomic_number"], "name": item["name"]} for item in reference["records"]]
                and isinstance(payload.get("plotlyFigure"), dict) and _figure_values_valid(payload, comparison=comparison))
    return False


def reference_facts(artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    if artifact.get("type") != "table_json":
        return []
    declarations = [
        FactDeclaration("reference.element_count", "/elementCount", "count"),
        FactDeclaration("reference.value_count", "/valueCount", "count"),
        FactDeclaration("reference.version", "/referenceSource/version"),
        FactDeclaration("reference.property_definition", "/referenceSource/propertyDefinition/definition"),
    ]
    facts = [fact for declaration in declarations if (fact := _fact(artifact, payload, declaration)) is not None]
    field = "covalent_radius_angstrom" if payload["property"] == "covalent_radius" else "atomic_number"
    highlighted = payload.get("highlightElements", [])
    # Complete symbol/value pairs survive bounded interpretation compaction.
    # Explicit highlights come first; the persisted table retains every row.
    rows = sorted(enumerate(payload["rows"]), key=lambda pair: (pair[1]["symbol"] not in highlighted, pair[0]))
    for index, row in rows:
        if row[field] is None:
            continue
        for declaration in [FactDeclaration("reference.element.symbol", f"/rows/{index}/symbol"),
                            FactDeclaration(f"reference.element.{payload['property']}", f"/rows/{index}/{field}", payload["unit"])]:
            fact = _fact(artifact, payload, declaration)
            if fact is not None:
                facts.append(fact.model_copy(update={"subject_ref": f"{artifact['id']}:element:{row['symbol']}"}))
    return facts


class ElementReferenceResultProjector:
    version = "1.0"

    def __init__(self, tool_id: str):
        self.tool_id = tool_id
        self.projector_id = f"agent2.{tool_id}"

    def project(self, context: ScientificResultProjectionContext):
        def reject(message):
            raise ScientificResultProjectionFailed(message, code="RESULT_REFERENCE_IDENTITY_INVALID")
        try:
            plan = AnalysisPlanV04.model_validate(context.analysis_plan)
        except ValueError as exc:
            raise ScientificResultProjectionFailed("Reference results require a validated project plan", code="RESULT_REFERENCE_IDENTITY_INVALID") from exc
        if (plan.projectId != context.project_id or context.source_object_refs or context.scientific_selections
                or ELEMENT_REFERENCE_SOURCE not in plan.referenceSources):
            reject("Reference result scope is inconsistent")
        calls = {str(call.get("id")): call for call in context.tool_calls}
        verified = []
        kinds_by_call: dict[str, set[str]] = {}
        missing = []
        for artifact in context.artifacts:
            if artifact.get("type") not in {"table_json", "plotly_json", "recipe_json"}:
                continue
            call_id = str(artifact.get("toolCallId") or artifact.get("tool_call_id") or "")
            call = calls.get(call_id) or {}
            step_id = str(call.get("stepId") or call.get("step_id") or "")
            step = next((step for step in plan.steps if step.stepId == step_id), None)
            params = call.get("paramsJson") or call.get("params_json") or call.get("params") or {}
            payload = context.artifact_payloads.get(str(artifact["id"]))
            if (artifact.get("projectId") != context.project_id or artifact.get("datasetId") is not None
                    or str(call.get("toolId") or call.get("tool_id")) != self.tool_id
                    or str(call.get("status") or call.get("state") or "").lower() != "completed"
                    or step is None or step.toolId != self.tool_id or params != step.params
                    or not isinstance(payload, dict) or not _reference_payload_valid(self.tool_id, artifact["type"], payload, params)):
                reject("Committed element reference output differs from its source or invocation")
            kinds = kinds_by_call.setdefault(call_id, set())
            if artifact["type"] in kinds:
                reject("Reference invocation contains duplicate scientific output types")
            kinds.add(artifact["type"])
            verified.append(artifact)
            missing.extend(payload.get("missingElements", []))
        if not kinds_by_call or any(not {"table_json", "plotly_json", "recipe_json"}.issubset(kinds) for kinds in kinds_by_call.values()):
            reject("Reference result requires its matching figure and values table")
        title = "元素参考性质比较" if self.tool_id.endswith("compare_elements") else "元素周期表"
        contract = ProjectorContract(self.projector_id, title, self.tool_id, (), (), (),
                                     accepted_tool_ids=(self.tool_id,), required_tool_ids=(self.tool_id,),
                                     fact_builder=reference_facts, version=self.version,
                                     limitations=(("PLATFORM_REFERENCE_NOT_SAMPLE", "本结果使用版本化元素参考资料，不代表用户样品的测量或计算性质。"),))
        projection = _project(replace(context, artifacts=tuple(verified)), contract)
        bundle = projection.bundle
        bundle.provenance = ProvenanceRecord.model_validate({**bundle.provenance.model_dump(mode="json"),
            "execution_scope": "PROJECT", "input_origin": "PLATFORM_REFERENCE",
            "reference_sources": [element_reference_description([
                context.artifact_payloads[str(artifact["id"])]["property"]
                for artifact in verified if artifact["type"] == "table_json"
            ]).model_dump(mode="json", exclude_none=True)]})
        for evidence in bundle.evidence:
            evidence.evidence_type = "COMMITTED_PLATFORM_REFERENCE_ARTIFACT"
        for figure in bundle.figures:
            figure.fact_refs = [fact.fact_id for fact in bundle.facts]
        if missing:
            bundle.warnings.append(ScientificWarning(warning_id=_semantic_id("warning", self.projector_id, "missing"),
                code="REFERENCE_VALUES_MISSING", message=f"参考资料未覆盖所选性质：{', '.join(dict.fromkeys(missing))}。", source_ref=self.projector_id))
        return projection


def build_reference_result_projectors():
    return [ElementReferenceResultProjector(tool_id) for tool_id in ("reference.periodic_table", "reference.compare_elements")]
