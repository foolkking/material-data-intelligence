"""Integrity-bound Results for user parameters, inline values and ideal models."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from mdi_adapters.context import ToolExecutionContext
from mdi_adapters.platform_builtin.project_parameters import compute_parameters, parameter_hash, result_plot, result_scene, result_table
from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.application.scientific_results.projectors.base import ScientificResultProjectionContext
from mdi_api.application.scientific_results.projectors.canonical import FactDeclaration, ProjectorContract, _fact, _project
from mdi_api.domain.scientific_results.contracts import ProvenanceRecord
from mdi_schemas import AnalysisPlanV04
from mdi_tool_registry.project_parameters import PARAMETER_TOOLS, SI_REFERENCE_SOURCE, si_reference_description


def parameter_facts(artifact: dict[str, Any], payload: dict[str, Any]):
    if artifact.get("type") != "table_json":
        return []
    facts = []
    for index, entry in enumerate(payload["facts"]):
        fact = _fact(artifact, payload, FactDeclaration(entry["predicate"], f"/facts/{index}/value", entry["unit"]))
        if fact is not None:
            facts.append(fact.model_copy(update={"subject_ref": f"{artifact['id']}:{entry['subject']}"}))
    if payload.get("artifactType") == "generation.ideal_crystal":
        # Repetitions are saved, validated calculation inputs. Project their
        # exact scalar locations without changing historical artifact bytes.
        for index, axis in enumerate("abc"):
            fact = _fact(artifact, payload, FactDeclaration(
                f"model.repeat_{axis}", f"/resolvedParameters/repetitions/{index}", "count"))
            if fact is not None:
                facts.append(fact.model_copy(update={"subject_ref": f"{artifact['id']}:summary"}))
    return facts


class ParameterResultProjector:
    version = "1.0"

    def __init__(self, tool_id: str):
        self.tool_id = tool_id
        self.projector_id = "agent2." + tool_id
        self.version = "1.1" if tool_id == "generation.ideal_crystal" else "1.0"

    def project(self, context: ScientificResultProjectionContext):
        def reject(message: str):
            raise ScientificResultProjectionFailed(message, code="RESULT_PARAMETER_IDENTITY_INVALID")
        try:
            plan = AnalysisPlanV04.model_validate(context.analysis_plan)
        except ValueError as exc:
            raise ScientificResultProjectionFailed("Parameter results require project scope", code="RESULT_PARAMETER_IDENTITY_INVALID") from exc
        if (plan.projectId != context.project_id or context.source_object_refs or context.scientific_selections
                or (self.tool_id == "reference.convert_units" and SI_REFERENCE_SOURCE not in plan.referenceSources)):
            reject("Parameter result cannot inherit sample authority")
        calls = {str(call.get("id")): call for call in context.tool_calls}
        verified, kinds_by_call, results = [], {}, {}
        for artifact in context.artifacts:
            kind = artifact.get("type")
            if kind not in {"table_json", "plotly_json", "structure_json", "recipe_json"}:
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
                    or step is None or step.toolId != self.tool_id or params != step.params or not isinstance(payload, dict)):
                reject("Parameter output does not match its committed invocation")
            if self.tool_id == "viz.inline_xy" and params.get("data_text", "").replace("\r\n", "\n") not in context.research_question.replace("\r\n", "\n"):
                reject("Inline data differs from the user's original table")
            if call_id not in results:
                try:
                    results[call_id] = compute_parameters(self.tool_id, params)
                except (ValueError, ArithmeticError) as exc:
                    raise ScientificResultProjectionFailed("Committed parameters are invalid", code="RESULT_PARAMETER_IDENTITY_INVALID") from exc
            result = results[call_id]
            if kind == "table_json":
                expected = result_table(self.tool_id, params, result)
            elif kind == "plotly_json" and result.figure is not None:
                expected = result_plot(self.tool_id, params, result)
            elif kind == "structure_json" and result.model is not None:
                # Only bounded in-memory geometry is rebuilt for verification;
                # the path is never used for reading, writing or source lookup.
                scope = ToolExecutionContext("verification", context.project_id, None, self.tool_id, "0.1.0", "1.0.0", "verification", Path("."))
                expected = result_scene(self.tool_id, params, result, scope)
            elif kind == "recipe_json":
                steps = payload.get("steps") or []
                sources = [SI_REFERENCE_SOURCE.model_dump(mode="json")] if self.tool_id == "reference.convert_units" else []
                inputs = [{"kind": result.origin, "contentHash": parameter_hash(params), "parameters": params},
                          *({"kind": "PLATFORM_REFERENCE", **source} for source in sources)]
                if (payload.get("schemaVersion") != "0.1" or len(steps) != 1 or steps[0].get("toolId") != self.tool_id
                        or steps[0].get("params") != params or payload.get("inputRequirements") != inputs):
                    reject("Calculation recipe differs from its input")
                expected = payload
            else:
                reject("Unexpected calculation artifact")
            if payload != expected:
                reject("Saved calculation data or geometry differs from its parameters")
            kinds = kinds_by_call.setdefault(call_id, set())
            if kind in kinds:
                reject("Calculation contains duplicate output types")
            kinds.add(kind)
            verified.append(artifact)
        for call_id, result in results.items():
            required = {"table_json", "recipe_json"} | ({"plotly_json"} if result.figure else set()) | ({"structure_json"} if result.model is not None else set())
            if kinds_by_call[call_id] != required:
                reject("Calculation is missing one of its exact outputs")
        if not results:
            reject("Calculation has no completed output")
        limitations = list(dict.fromkeys(message for result in results.values() for message in result.limitations))
        contract = ProjectorContract(self.projector_id, PARAMETER_TOOLS[self.tool_id][0], self.tool_id, (), (), (),
            accepted_tool_ids=(self.tool_id,), required_tool_ids=(self.tool_id,), fact_builder=parameter_facts,
            limitations=tuple((f"PARAMETER_SCOPE_{index}", message) for index, message in enumerate(limitations)), version=self.version)
        projection = _project(replace(context, artifacts=tuple(verified)), contract)
        bundle = projection.bundle
        if self.tool_id == "generation.ideal_crystal":
            # The shared projector historically treated structure JSON as a
            # table. This new tool declares its inert scene as a figure.
            from mdi_api.domain.scientific_results.contracts import ScientificFigure
            scenes = {str(item["id"]) for item in verified if item["type"] == "structure_json"}
            for table in list(bundle.tables):
                if scenes.intersection(table.artifact_ids):
                    bundle.figures.append(ScientificFigure(figure_id=table.table_id, figure_type=self.tool_id,
                        role=table.role, title="理想晶格示意", artifact_ids=table.artifact_ids,
                        fact_refs=table.fact_refs, evidence_refs=table.evidence_refs))
                    bundle.tables.remove(table)
        for figure in bundle.figures:
            producers = {str(item.get("toolCallId") or item.get("tool_call_id")) for item in verified if str(item["id"]) in figure.artifact_ids}
            tables = {str(item["id"]) for item in verified if item["type"] == "table_json" and str(item.get("toolCallId") or item.get("tool_call_id")) in producers}
            figure.fact_refs = [fact.fact_id for fact in bundle.facts if fact.source.artifact_id in tables]
        origins = {result.origin for result in results.values()}
        if len(origins) != 1:
            reject("Calculation input origins conflict")
        bundle.provenance = ProvenanceRecord.model_validate({**bundle.provenance.model_dump(mode="json"),
            "execution_scope": "PROJECT", "input_origin": origins.pop(),
            "reference_sources": [si_reference_description().model_dump(mode="json", exclude_none=True)] if self.tool_id == "reference.convert_units" else [],
            "parameter_inputs": [{"tool_call_id": call_id, "tool_id": self.tool_id,
                "input_origin": result.origin,
                "content_hash": parameter_hash(dict(calls[call_id].get("paramsJson") or calls[call_id].get("params_json") or calls[call_id].get("params") or {})),
                "resolved_parameters": result.resolved} for call_id, result in results.items()]})
        for evidence in bundle.evidence:
            evidence.evidence_type = "COMMITTED_PARAMETER_ARTIFACT"
        return projection


def build_parameter_result_projectors():
    return [ParameterResultProjector(tool_id) for tool_id in PARAMETER_TOOLS]
