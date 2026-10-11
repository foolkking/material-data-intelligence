"""Resolve report artifact inputs without borrowing sibling step sources."""
from typing import Any

from mdi_api.domain.scientific_results.contracts import ScientificFigure, ScientificResultBundle


def volumetric_report_figures(
    bundle: ScientificResultBundle, artifacts: list[dict[str, Any]], calls: list[dict[str, Any]],
) -> list[tuple[ScientificFigure, list[dict[str, Any]]]]:
    """Bind a saved dataset and its controlled producer's files, never sibling calls.

    Older Result snapshots retained the dataset/field JSON but omitted binary
    dependencies from their artifact list. The recorded ToolCall owns those
    dependencies; the viewer/exporter must additionally validate its manifest,
    dataset and payload hashes before using any of their bytes.
    """
    job_id = str(bundle.provenance.job_id or "")
    allowed_types = {
        "volumetric_dataset_json", "volumetric_manifest_json", "volumetric_grid_json",
        "volumetric_field_json", "volumetric_payload_json", "volumetric_binary",
        "volumetric_structure_overlay_json",
    }
    owned = [a for a in artifacts if a.get("jobId") == job_id and a.get("projectId") == bundle.project_id]
    result = []
    seen = set()
    for item in bundle.result_items:
        if item.result_type != "volumetric.field":
            continue
        for artifact_id in item.artifact_ids:
            matches = [a for a in owned if a.get("id") == artifact_id and a.get("type") == "volumetric_dataset_json"]
            if len(matches) != 1 or artifact_id not in bundle.provenance.artifact_ids or artifact_id in seen:
                continue
            anchor = matches[0]
            producer = anchor.get("toolCallId")
            if not producer or producer not in bundle.provenance.tool_call_ids:
                continue
            if len([c for c in calls if c.get("id") == producer and c.get("jobId") == job_id]) != 1:
                continue
            companions = [a for a in owned if a.get("toolCallId") == producer and a.get("type") in allowed_types]
            # Never choose a dataset or manifest by array order.
            if any(len([a for a in companions if a.get("type") == kind]) != 1
                   for kind in ("volumetric_dataset_json", "volumetric_manifest_json")):
                continue
            names = [a.get("name") for a in companions]
            if not all(isinstance(name, str) and name for name in names) or len(set(names)) != len(names):
                continue
            descriptors = [{key: a.get(key) for key in (
                "id", "jobId", "toolCallId", "type", "name", "sha256", "sizeBytes", "contentType",
            )} for a in companions]
            figure = ScientificFigure(
                figure_id=f"figure.volumetric.{artifact_id}", figure_type="volumetric.field",
                role=item.role, title="体数据场与晶格切片", caption_seed="体数据场与晶格切片",
                artifact_ids=[artifact_id], fact_refs=list(item.fact_refs), evidence_refs=list(item.evidence_refs),
            )
            result.append((figure, descriptors))
            seen.add(artifact_id)
    return result


def artifact_input_versions(
    *, artifact_ids: list[str], artifacts: dict[str, dict[str, Any]],
    calls: list[dict[str, Any]], plan: dict[str, Any],
    project_id: str, job_id: str, plan_id: str,
) -> set[str]:
    if str(plan.get("planId")) != plan_id or str(plan.get("projectId")) != project_id:
        return set()
    steps = (plan.get("analysisPlan") or {}).get("steps") or []
    versions: set[str] = set()
    for artifact_id in artifact_ids:
        artifact = artifacts.get(artifact_id, {})
        if artifact.get("jobId") != job_id or artifact.get("projectId") != project_id:
            continue
        matches = [call for call in calls if call.get("id") == artifact.get("toolCallId") and call.get("jobId") == job_id]
        if len(matches) != 1:
            continue
        call = matches[0]
        matched_steps = [step for step in steps if step.get("stepId") == call.get("stepId") and step.get("toolId") == call.get("toolId")]
        if len(matched_steps) != 1:
            continue
        versions.update(str(ref["ref"]) for ref in matched_steps[0].get("inputRefs", [])
                        if ref.get("refType") == "normalized_object" and ref.get("ref"))
    return versions
