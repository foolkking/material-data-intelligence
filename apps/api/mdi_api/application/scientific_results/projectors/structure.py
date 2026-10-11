"""Selected base-cell site facts from owned, validated viewer artifacts."""
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from mdi_artifact_core.viewer_scene_contract import validate_viewer_scene
from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.domain.scientific_results.contracts import ScientificFact, FactSourceLocator
from .base import ScientificResultProjectionContext


def structure_selection_facts(context: ScientificResultProjectionContext, artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    if not validate_viewer_scene(payload).valid:
        return []
    if (artifact.get("projectId") != context.project_id
            or artifact.get("jobId") != context.execution_summary.get("job_id")):
        return []
    calls = [call for call in context.tool_calls if call.get("id") == artifact.get("toolCallId")
             and call.get("jobId") == artifact.get("jobId")]
    if len(calls) != 1:
        return []
    call = calls[0]
    steps = [step for step in context.analysis_plan.get("steps", [])
             if step.get("stepId") == call.get("stepId") and step.get("toolId") == call.get("toolId")]
    if len(steps) != 1:
        return []
    versions = {str(ref.get("ref")) for ref in steps[0].get("inputRefs", []) if ref.get("refType") == "normalized_object"}
    refs = {(str(ref.object_id), str(ref.version_id)) for ref in context.source_object_refs
            if ref.object_type == "structure.crystal" and str(ref.version_id) in versions}
    facts: dict[str, ScientificFact] = {}
    artifact_id = str(artifact["id"])

    def add(name: str, value: Any, pointer: str, subject: str, unit: str | None = None) -> None:
        fact_id = f"fact.{uuid5(NAMESPACE_URL, f'mdi-structure-site:{artifact_id}:{pointer}').hex}"
        facts[fact_id] = ScientificFact(fact_id=fact_id, predicate=f"structure.{name}",
            subject_ref=subject, value=value, unit=unit,
            source=FactSourceLocator(artifact_id=artifact_id, artifact_locator=pointer))

    for selection in context.scientific_selections[:16]:
        ref = selection.get("object_ref") or {}
        if selection.get("selection_type") != "PERIODIC_SITE" or (str(ref.get("object_id")), str(ref.get("version_id"))) not in refs:
            continue
        loc = selection.get("semantic_locator") or {}
        matches = [(i, site) for i, site in enumerate(payload["scene"]["sites"])
                   if type(loc.get("site_index")) is int and site["index"] == loc["site_index"]]
        if len(matches) != 1 or matches[0][1]["element"] != loc.get("species"):
            raise ScientificResultProjectionFailed("Selected structure site is unavailable in the committed scene")
        i, site = matches[0]
        base = f"/scene/sites/{i}"
        subject = f"{artifact_id}:base-site:{site['index']}"
        add("selected_site_index", site["index"], f"{base}/index", subject)
        add("selected_element", site["element"], f"{base}/element", subject)
        add("selected_coordinate_basis", payload["scene"]["coordinate_basis"], "/scene/coordinate_basis", subject)
        for axis, name in enumerate(("x", "y", "z")):
            add(f"selected_base_cartesian_{name}", site["xyz"][axis], f"{base}/xyz/{axis}", subject, "angstrom")
            if "frac" in site:
                add(f"selected_base_fractional_{name}", site["frac"][axis], f"{base}/frac/{axis}", subject)
    return list(facts.values())
