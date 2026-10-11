"""Electronic selection facts resolved only from validated committed tool output."""
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.domain.scientific_results.contracts import ScientificFact, FactSourceLocator
from .base import ScientificResultProjectionContext


def electronic_selection_facts(context: ScientificResultProjectionContext, artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    artifact_id = str(artifact.get("id") or artifact.get("artifactId"))
    facts: dict[str, ScientificFact] = {}

    def add(predicate: str, value: Any, pointer: str, unit: str | None = None, subject: str = "") -> None:
        if value is None:
            return
        fact_id = f"fact.{uuid5(NAMESPACE_URL, f'mdi-agent2-result:{artifact_id}:{predicate}:{pointer}:{subject}').hex}"
        facts[fact_id] = ScientificFact(fact_id=fact_id, predicate=f"electronic.{predicate}", subject_ref=subject or artifact_id,
            value=value, unit=unit, source=FactSourceLocator(artifact_id=artifact_id, artifact_locator=pointer))

    add("energy_reference", payload["energy"]["reference"], "/energy/reference")
    add("fermi_energy", payload["energy"].get("fermiEnergyEv"), "/energy/fermiEnergyEv", "eV")
    add("spin_mode", payload["spin"]["mode"], "/spin/mode")
    is_band = payload["artifactType"] == "electronic.band_structure"
    if not is_band:
        add("dos_unit_semantic", payload["dosUnitSemantic"], "/dosUnitSemantic")
        add("projection_completeness", payload["projectionCompleteness"], "/projectionCompleteness")
    call_id = str(artifact.get("toolCallId") or artifact.get("tool_call_id") or "")
    call = next((item for item in context.tool_calls if str(item.get("id")) == call_id), {})
    step_id = str(call.get("stepId") or call.get("step_id") or "")
    versions = {str(ref.get("ref")) for step in context.analysis_plan.get("steps", [])
        if step_id and str(step.get("stepId") or step.get("step_id")) == step_id
        for ref in (step.get("inputRefs") or step.get("input_refs") or [])
        if (ref.get("refType") or ref.get("ref_type")) == "normalized_object"}
    exact_refs = {(str(ref.object_id), str(ref.version_id)) for ref in context.source_object_refs
        if ref.object_type == payload["artifactType"] and str(ref.version_id) in versions}
    for selection in context.scientific_selections[:16]:
        ref = selection.get("object_ref") or {}
        if selection.get("selection_type") != ("ELECTRONIC_BAND_STATE" if is_band else "ELECTRONIC_DOS_POINT") or (str(ref.get("object_id")), str(ref.get("version_id"))) not in exact_refs:
            continue
        loc = selection.get("semantic_locator") or {}
        if is_band:
            index = loc.get("kpoint_index")
            if type(index) is not int or not 0 <= index < len(payload["kpoints"]):
                raise ScientificResultProjectionFailed("Selected electronic k point is unavailable")
            point = payload["kpoints"][index]
            matches = [(i, state) for i, state in enumerate(payload["states"]) if state["spinChannel"] == loc.get("spin_channel_id") and state["bandId"] == loc.get("band_id") and state["kpointId"] == loc.get("kpoint_id")]
            if point["kpointId"] != loc.get("kpoint_id") or len(matches) != 1:
                raise ScientificResultProjectionFailed("Selected electronic band state is unavailable")
            i, state = matches[0]
            subject = f"{artifact_id}:{state['stateId']}"
            for key, name in (("spinChannel", "selected_spin_channel"), ("bandId", "selected_band_id"), ("kpointId", "selected_kpoint_id"), ("energyEv", "selected_energy")):
                add(name, state[key], f"/states/{i}/{key}", "eV" if key == "energyEv" else None, subject)
            add("selected_kpoint_label", point.get("label"), f"/kpoints/{index}/label", subject=subject)
        else:
            index = loc.get("energy_point_index")
            kind = loc.get("channel_kind")
            if type(index) is not int or not 0 <= index < len(payload["energiesEv"]) or kind not in {"total", "projection"}:
                raise ScientificResultProjectionFailed("Selected electronic DOS point is unavailable")
            key = "totalDos" if kind == "total" else "projections"
            matches = [(i, channel) for i, channel in enumerate(payload[key]) if channel["spinChannel"] == loc.get("spin_channel_id") and channel["channelId"] == loc.get("dos_channel_id")]
            if len(matches) != 1 or (kind == "projection" and matches[0][1].get("projectionKind") != loc.get("projection_kind")):
                raise ScientificResultProjectionFailed("Selected electronic DOS channel is unavailable")
            i, channel = matches[0]
            subject = f"{artifact_id}:{channel['channelIdentity']}:{index}"
            add("selected_spin_channel", channel["spinChannel"], f"/{key}/{i}/spinChannel", subject=subject)
            add("selected_dos_channel", channel["channelId"], f"/{key}/{i}/channelId", subject=subject)
            add("selected_energy", payload["energiesEv"][index], f"/energiesEv/{index}", "eV", subject)
            add("selected_dos_value", channel["values"][index], f"/{key}/{i}/values/{index}", payload["dosUnitSemantic"], subject)
    return list(facts.values())
