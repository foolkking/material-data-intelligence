"""Bounded facts read from committed trajectory bytes, never viewer coordinates."""

from typing import Any
from uuid import NAMESPACE_URL, uuid5

from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.domain.scientific_results.contracts import ScientificFact, FactSourceLocator
from .base import ScientificResultProjectionContext


def trajectory_view_facts(
    context: ScientificResultProjectionContext, artifact: dict[str, Any], payload: dict[str, Any]
) -> list[ScientificFact]:
    artifact_id = str(artifact.get("id") or artifact.get("artifactId"))
    facts: dict[str, ScientificFact] = {}

    def add(predicate: str, value: Any, pointer: str, unit: str | None = None, subject: str = "") -> None:
        if value is None:
            return
        identity = f"mdi-agent2-result:{artifact_id}:{predicate}:{pointer}:{subject}"
        fact_id = f"fact.{uuid5(NAMESPACE_URL, identity).hex}"
        facts[fact_id] = ScientificFact(
            fact_id=fact_id, predicate=f"trajectory.{predicate}",
            subject_ref=subject or artifact_id, value=value, unit=unit,
            source=FactSourceLocator(artifact_id=artifact_id, artifact_locator=pointer),
        )

    frames = payload["frames"]
    add("frame_count", len(frames), "/frames", "count")
    add("atom_count", payload["atoms"]["count"], "/atoms/count", "count")
    for key in ("coordinate_mode", "position_wrapping", "lattice_mode"):
        add(key, payload.get(key), f"/{key}")
    for axis, name in enumerate("abc"):
        add(f"periodic_boundary_{name}", payload["periodic_boundary"][axis], f"/periodic_boundary/{axis}")

    # Bind each Artifact to its actual executed step and exact input version.
    # A sibling trajectory with the same shape is not a substitute source.
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
                  if ref.object_type == "trajectory.atomic" and str(ref.version_id) in bound_versions}
    for selection in context.scientific_selections[:16]:
        ref = selection.get("object_ref") or {}
        if (str(ref.get("object_id")), str(ref.get("version_id"))) not in exact_refs:
            continue
        kind = selection.get("selection_type")
        if kind not in {"TRAJECTORY_FRAME", "TRAJECTORY_ATOM"}:
            continue
        locator = selection.get("semantic_locator") or {}
        index = locator.get("frame_index")
        if (type(index) is not int or not 0 <= index < len(frames)
                or locator.get("frame_id", f"frame:{index}") != f"frame:{index}"):
            raise ScientificResultProjectionFailed("Selected trajectory frame is unavailable in the committed output")
        frame = frames[index]
        subject = f"{artifact_id}:frame:{index}"
        atom_index = locator.get("atom_index") if kind == "TRAJECTORY_ATOM" else None
        if kind == "TRAJECTORY_ATOM":
            if type(atom_index) is not int or not 0 <= atom_index < len(frame["positions"]):
                raise ScientificResultProjectionFailed("Selected trajectory atom is unavailable in the committed output")
            atom_locator = locator.get("atom_id")
            if atom_locator is not None and (not isinstance(atom_locator, str) or not atom_locator.startswith(f"atom:{atom_index}:")):
                raise ScientificResultProjectionFailed("Selected trajectory atom identity conflicts with its index")
            subject += f":atom:{atom_index}"
        # Human frame/atom numbers are deterministic one-based presentation
        # ordinals. Coordinates, species and time come only from Artifact bytes.
        add("selected_frame_number", int(frame["frame_index"]) + 1,
            f"/frames/{index}/frame_index", "ordinal (1-based)", subject)
        add("selected_frame_time", frame.get("time"), f"/frames/{index}/time", payload["time"]["unit"], subject)
        if atom_index is not None:
            add("selected_atom_number", atom_index + 1, f"/frames/{index}/atom_ids/{atom_index}", "ordinal (1-based)", subject)
            atom_id = frame["atom_ids"][atom_index]
            record_index = next((i for i, record in enumerate(payload["atoms"]["records"]) if record["atom_id"] == atom_id), None)
            if record_index is not None:
                add("selected_atom_species", payload["atoms"]["records"][record_index]["species"], f"/atoms/records/{record_index}/species", subject=subject)
            for axis, name in enumerate("xyz"):
                add(f"selected_atom_source_{name}", frame["positions"][atom_index][axis],
                    f"/frames/{index}/positions/{atom_index}/{axis}", payload["units"]["positions"], subject)
    return list(facts.values())
