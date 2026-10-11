"""Selected mode facts from committed band output and exact executed inputs."""

from typing import Any
from uuid import NAMESPACE_URL, uuid5

from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.domain.scientific_results.contracts import ScientificFact, FactSourceLocator
from .base import ScientificResultProjectionContext


def phonon_band_facts(context: ScientificResultProjectionContext, artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    artifact_id = str(artifact.get("id") or artifact.get("artifactId"))
    facts: dict[str, ScientificFact] = {}

    def add(predicate: str, value: Any, pointer: str, unit: str | None = None, subject: str = "") -> None:
        if value is None:
            return
        fact_id = f"fact.{uuid5(NAMESPACE_URL, f'mdi-agent2-result:{artifact_id}:{predicate}:{pointer}:{subject}').hex}"
        facts[fact_id] = ScientificFact(
            fact_id=fact_id, predicate=f"phonon.{predicate}", subject_ref=subject or artifact_id,
            value=value, unit=unit,
            source=FactSourceLocator(artifact_id=artifact_id, artifact_locator=pointer),
        )

    add("atom_count", payload["atom_count"], "/atom_count", "count")
    add("frequency_unit", payload["frequency_unit"], "/frequency_unit")
    call_id = str(artifact.get("toolCallId") or artifact.get("tool_call_id") or "")
    call = next((item for item in context.tool_calls if str(item.get("id")) == call_id), {})
    step_id = str(call.get("stepId") or call.get("step_id") or "")
    bound_versions = {
        str(ref.get("ref"))
        for step in context.analysis_plan.get("steps", [])
        if str(step.get("stepId") or step.get("step_id")) == step_id
        for ref in (step.get("inputRefs") or step.get("input_refs") or [])
        if (ref.get("refType") or ref.get("ref_type")) == "normalized_object"
    }
    exact_refs = {(str(ref.object_id), str(ref.version_id)) for ref in context.source_object_refs
                  if ref.object_type == "phonon.band_structure" and str(ref.version_id) in bound_versions}
    for selection in context.scientific_selections[:16]:
        ref = selection.get("object_ref") or {}
        if selection.get("selection_type") != "PHONON_Q_POINT" or (str(ref.get("object_id")), str(ref.get("version_id"))) not in exact_refs:
            continue
        locator = selection.get("semantic_locator") or {}
        q, b = locator.get("qpoint_index"), locator.get("branch_index")
        if (type(q) is not int or not 0 <= q < len(payload["qpoints"])
                or type(b) is not int or not 0 <= b < len(payload["branches"])
                or locator.get("q_point_id", f"q:{q}") != f"q:{q}"
                or locator.get("branch_id", f"branch:{b}") != f"branch:{b}"):
            raise ScientificResultProjectionFailed("Selected phonon mode is unavailable in the committed output")
        point, branch = payload["qpoints"][q], payload["branches"][b]
        subject = f"{artifact_id}:q:{q}:branch:{b}"
        add("selected_qpoint_index", point["index"], f"/qpoints/{q}/index", "index (0-based)", subject)
        add("selected_branch_index", branch["branch_index"], f"/branches/{b}/branch_index", "index (0-based)", subject)
        add("selected_frequency", branch["frequencies"][q], f"/branches/{b}/frequencies/{q}", payload["frequency_unit"], subject)
        add("selected_qpoint_label", point.get("label"), f"/qpoints/{q}/label", subject=subject)
    return list(facts.values())
