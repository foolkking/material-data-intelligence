"""Deterministic projectors for the Agent 2 canonical capability families."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid5, NAMESPACE_URL

from mdi_api.scientific_results.projectors.base import ScientificResultProjection, ScientificResultProjectionContext
from mdi_api.scientific_results.schemas import (
    EvidenceItem,
    FactSourceLocator,
    MethodRecord,
    ProvenanceRecord,
    ResultRelevanceStatus,
    ScientificFigure,
    ScientificFact,
    ScientificLimitation,
    ScientificResultBundle,
    ScientificResultItem,
    ScientificResultRole,
    ScientificTable,
    ScientificWarning,
)


def _stable_id(seed: str) -> str:
    return str(uuid5(NAMESPACE_URL, "mdi-agent2:" + seed))


def _artifact_key(artifact: dict[str, Any]) -> str:
    return str(artifact.get("id") or artifact.get("artifactId"))


def _artifact_payload(context: ScientificResultProjectionContext, artifact: dict[str, Any]) -> Any:
    return context.artifact_payloads.get(_artifact_key(artifact))


def _walk_numbers(value: Any, path: str = "") -> list[tuple[str, float | int]]:
    found: list[tuple[str, float | int]] = []
    if isinstance(value, bool):
        return found
    if isinstance(value, (int, float)):
        return [(path or "/value", value)]
    if isinstance(value, dict):
        for key in sorted(value):
            found.extend(_walk_numbers(value[key], f"{path}/{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_walk_numbers(item, f"{path}/{index}"))
    return found


def _machine_payload(payload: Any) -> bool:
    return isinstance(payload, (dict, list))


def _fact(*, fact_id: str, predicate: str, subject_ref: str, value: Any, artifact: dict[str, Any], locator: str, unit: str | None = None) -> ScientificFact:
    return ScientificFact(
        fact_id=fact_id,
        predicate=predicate,
        subject_ref=subject_ref,
        value=value,
        unit=unit,
        source=FactSourceLocator(artifact_id=_artifact_key(artifact), artifact_locator=locator),
    )


def _project(context: ScientificResultProjectionContext, *, projector_id: str, title: str, result_type: str) -> ScientificResultProjection:
    artifacts = tuple(sorted(context.artifacts, key=lambda item: _artifact_key(item)))
    facts: list[ScientificFact] = []
    evidence: list[EvidenceItem] = []
    figures: list[ScientificFigure] = []
    tables: list[ScientificTable] = []
    result_items: list[ScientificResultItem] = []
    limitations: list[ScientificLimitation] = []
    warnings: list[ScientificWarning] = []

    for artifact in artifacts:
        artifact_id = _artifact_key(artifact)
        payload = _artifact_payload(context, artifact)
        evidence_id = f"evidence.{artifact_id}"
        evidence.append(EvidenceItem(
            evidence_id=evidence_id,
            evidence_type="EXECUTION_ARTIFACT",
            artifact_id=artifact_id,
            artifact_locator="/",
            scientific_object_refs=list(context.source_object_refs),
        ))
        if _machine_payload(payload):
            numbers = _walk_numbers(payload)
            for index, (locator, value) in enumerate(numbers):
                # Only project a bounded, explicitly machine-readable scalar set.
                if index >= 128:
                    break
                safe = locator.strip("/").replace("/", ".") or "value"
                facts.append(_fact(
                    fact_id=f"{artifact_id}.{safe}",
                    predicate=safe,
                    subject_ref=artifact_id,
                    value=value,
                    artifact=artifact,
                    locator=locator,
                ))
            if isinstance(payload, dict):
                table_id = f"table.{artifact_id}"
                tables.append(ScientificTable(
                    table_id=table_id,
                    table_type=result_type,
                    role=ScientificResultRole.PRIMARY,
                    title=title,
                    artifact_ids=[artifact_id],
                    fact_refs=[fact.fact_id for fact in facts if fact.source.artifact_id == artifact_id],
                    evidence_refs=[evidence_id],
                ))
        else:
            content_type = str(artifact.get("contentType") or artifact.get("mediaType") or "")
            if content_type.startswith("image/") or str(artifact.get("type", "")).lower() in {"figure", "png", "svg"}:
                figures.append(ScientificFigure(
                    figure_id=f"figure.{artifact_id}", figure_type=result_type,
                    role=ScientificResultRole.PRIMARY, title=title,
                    artifact_ids=[artifact_id], fact_refs=[], evidence_refs=[evidence_id],
                ))
            else:
                limitations.append(ScientificLimitation(
                    limitation_id=f"limitation.{artifact_id}", code="MACHINE_DATA_UNAVAILABLE",
                    message="The committed artifact does not expose machine-readable numeric data.", source_ref=artifact_id,
                ))

    item_facts = [fact.fact_id for fact in facts]
    item_evidence = [item.evidence_id for item in evidence]
    for artifact in artifacts:
        artifact_id = _artifact_key(artifact)
        result_items.append(ScientificResultItem(
            id=f"result-item.{artifact_id}", result_type=result_type,
            role=ScientificResultRole.PRIMARY if not result_items else ScientificResultRole.SUPPORTING,
            title=title, artifact_ids=[artifact_id], scientific_object_refs=list(context.source_object_refs),
            fact_refs=[fact_id for fact_id in item_facts if fact_id.startswith(artifact_id + ".")],
            evidence_refs=[evidence_id for evidence_id in item_evidence if evidence_id == f"evidence.{artifact_id}"],
        ))
    for item in evidence:
        item.supports_fact_refs = [fact.fact_id for fact in facts if fact.source.artifact_id == item.artifact_id]
        item.supports_result_item_refs = [f"result-item.{item.artifact_id}"]

    plan_steps = context.capability_plan.get("steps") or []
    methods = [MethodRecord(
        method_id=f"method.{step.get('step_id') or step.get('stepId')}",
        capability_id=str(step.get("capability_id") or step.get("capabilityId") or "unknown"),
        capability_version=str(step.get("capability_version") or step.get("capabilityVersion") or "1.0"),
        parameters=dict(step.get("parameters") or {}),
        source_object_refs=list(context.source_object_refs),
    ) for step in plan_steps]
    outcome = str(context.execution_summary.get("execution_outcome") or context.execution_summary.get("outcome") or "SUCCESS")
    bundle = ScientificResultBundle(
        schema_version="1.0", result_id=UUID(_stable_id(f"result:{context.research_turn_id}:{projector_id}")),
        project_id=context.project_id, research_session_id=context.research_session_id,
        research_turn_id=UUID(str(context.research_turn_id)), research_question=context.research_question,
        source_object_refs=list(context.source_object_refs), execution_status=outcome,
        relevance_status=ResultRelevanceStatus.CURRENT, result_items=result_items, facts=facts,
        figures=figures, tables=tables, output_object_refs=[], evidence=evidence, methods=methods,
        limitations=limitations, warnings=warnings, provenance=ProvenanceRecord(
            research_turn_id=UUID(str(context.research_turn_id)),
            job_id=str(context.execution_summary.get("job_id") or ""),
            analysis_plan_id=str(context.execution_summary.get("analysis_plan_id") or ""),
            execution_summary_id=str(context.execution_summary.get("id") or "") or None,
            tool_call_ids=sorted(str(call.get("id")) for call in context.tool_calls),
            artifact_ids=[_artifact_key(artifact) for artifact in artifacts],
            projector_ids=[projector_id],
        ), projection_version="agent2.result/1.0",
    )
    return ScientificResultProjection(bundle=bundle, projector_id=projector_id, projector_version="1.0")


class CanonicalScientificResultProjector:
    def __init__(self, projector_id: str, *, title: str, result_type: str) -> None:
        self.projector_id = projector_id
        self.version = "1.0"
        self.title = title
        self.result_type = result_type

    def project(self, context: ScientificResultProjectionContext) -> ScientificResultProjection:
        return _project(context, projector_id=self.projector_id, title=self.title, result_type=self.result_type)


def build_canonical_result_projectors() -> list[CanonicalScientificResultProjector]:
    specs = {
        "agent2.structure.rdf": ("径向分布函数", "structure.rdf"),
        "agent2.diffraction.theoretical_xrd": ("理论 XRD 图谱", "diffraction.xrd.theoretical"),
        "agent2.diffraction.experimental_theoretical_comparison": ("实验与理论 XRD 比较", "diffraction.xrd.comparison"),
        "agent2.ml.regression_evaluation": ("材料回归评估", "ml.regression.evaluation"),
        "agent2.trajectory.msd": ("轨迹均方位移", "trajectory.msd"),
        "agent2.trajectory.diffusion": ("轨迹扩散性质", "trajectory.diffusion"),
        "agent2.phonon.band": ("声子能带", "phonon.band"),
        "agent2.phonon.dos": ("声子态密度", "phonon.dos"),
        "agent2.phonon.band_dos": ("声子能带与态密度", "phonon.band_dos"),
    }
    return [CanonicalScientificResultProjector(projector_id, title=title, result_type=result_type) for projector_id, (title, result_type) in sorted(specs.items())]
