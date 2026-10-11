"""Selected source channels resolved from committed adapter component mappings."""

import re
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.domain.scientific_results.contracts import ScientificFact, FactSourceLocator, ScientificLimitation
from .base import ScientificResultProjectionContext


def volumetric_field_limitations(artifact_id: str, payload: dict[str, Any]) -> list[ScientificLimitation]:
    fields = payload.get("fields", []) if payload.get("schema_version") == "phase10j.volumetric_dataset.v1" else [payload]
    quantities = {field.get("quantity") for field in fields}
    limits: list[tuple[str, str]] = []
    if "electron_localization_function" in quantities:
        limits.extend((
            ("ELF_INTEGRAL_NOT_POPULATION", "ELF is dimensionless. Its saved full-cell spatial integral is a mathematical statistic in cubic angstroms; no electron-count or basin-population interpretation is assigned. This does not make the saved statistic unavailable or invalid."),
            ("ELF_CONTOURS_NOT_TOPOLOGY", "ELF isosurfaces and slices display the supplied scalar field. They do not establish bond, lone-pair, basin, shell, or topology classifications; those require additional scientific analysis."),
        ))
    if "orbital_density" in quantities:
        limits.extend((
            ("PARTIAL_DENSITY_IDENTITY_NOT_ESTABLISHED", "Source-defined partial density and its contours do not establish a single orbital, band, k-point, HOMO/LUMO, orbital character, or bonding identity. Such assignments require explicit supporting source metadata and analysis."),
            ("PARTIAL_DENSITY_INTEGRAL_NOT_OCCUPANCY", "The saved full-cell partial-density integral retains its declared unit and normalization. An electron-count integral is not automatically a single-orbital occupancy or probability; no electron count or probability inside an isosurface has been computed."),
        ))
    return [ScientificLimitation(
        limitation_id=f"limitation.{uuid5(NAMESPACE_URL, f'mdi-agent2-volume:{artifact_id}:{code}').hex}",
        code=code, message=message, source_ref=artifact_id,
    ) for code, message in limits]


def volumetric_selection_facts(context: ScientificResultProjectionContext, artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    call_id = str(artifact.get("toolCallId") or artifact.get("tool_call_id") or "")
    call = next((item for item in context.tool_calls if str(item.get("id")) == call_id), {})
    if (call.get("toolId") or call.get("tool_id")) != "structure.volumetric_data":
        return []
    step_id = str(call.get("stepId") or call.get("step_id") or "")
    bound_versions = {str(ref.get("ref"))
        for step in context.analysis_plan.get("steps", []) if step_id and str(step.get("stepId") or step.get("step_id")) == step_id
        for ref in (step.get("inputRefs") or step.get("input_refs") or [])
        if (ref.get("refType") or ref.get("ref_type")) == "normalized_object"}
    exact_refs = {(str(ref.object_id), str(ref.version_id)) for ref in context.source_object_refs
                  if ref.object_type in {"volumetric.field", "volumetric.charge_density"} and str(ref.version_id) in bound_versions}
    artifact_id = str(artifact.get("id") or artifact.get("artifactId"))
    facts: dict[str, ScientificFact] = {}
    for selection in context.scientific_selections[:16]:
        ref = selection.get("object_ref") or {}
        if selection.get("selection_type") != "VOLUMETRIC_FIELD" or (str(ref.get("object_id")), str(ref.get("version_id"))) not in exact_refs:
            continue
        locator = selection.get("semantic_locator") or {}
        channel = locator.get("source_channel_index")
        if type(channel) is not int or not 0 <= channel < 8 or locator.get("field_id") != f"channel:{channel}" or locator.get("field_locator") != f"/channels/{channel}":
            raise ScientificResultProjectionFailed("Selected volumetric source channel has an invalid locator")
        matches = []
        for index, field in enumerate(payload.get("fields") or []):
            provenance = field.get("provenance") or {}
            if provenance.get("producer") != "mdi_volumetric_adapter":
                continue
            for mapping_index, mapping in enumerate(provenance.get("transformations") or []):
                match = re.fullmatch(r"SOURCE_CHANNEL_V1:(0|[1-9]\d*):(0|[1-9]\d*)", str(mapping.get("detail")))
                if mapping.get("kind") == "component_remapping" and match and int(match[1]) == channel:
                    component = int(match[2])
                    if component < len((field.get("statistics") or {}).get("stored_components") or []):
                        matches.append((index, field, mapping_index, mapping, component))
        if len(matches) != 1:
            raise ScientificResultProjectionFailed("Selected volumetric source channel is missing or ambiguous in committed output")
        index, field, mapping_index, mapping, component = matches[0]
        base = f"/fields/{index}"
        subject = f"{artifact_id}:channel:{channel}"

        def add(name: str, value: Any, pointer: str, unit: str | None = None) -> None:
            fact_id = f"fact.{uuid5(NAMESPACE_URL, f'mdi-agent2-volume:{subject}:{name}:{pointer}').hex}"
            facts[fact_id] = ScientificFact(fact_id=fact_id, predicate=f"volumetric.selected_{name}", subject_ref=subject,
                value=value, unit=unit, source=FactSourceLocator(artifact_id=artifact_id, artifact_locator=pointer))

        add("component", field["component_labels"][component], f"{base}/component_labels/{component}")
        add("field_name", field["field_name"], f"{base}/field_name")
        add("quantity", field["quantity"], f"{base}/quantity")
        unit = field["unit"]["canonical_unit"]
        add("canonical_unit", unit, f"{base}/unit/canonical_unit")
        values = field["statistics"]["stored_components"][component]
        for name in ("minimum", "maximum"):
            add(name, values[name], f"{base}/statistics/stored_components/{component}/{name}", unit)
    return list(facts.values())
