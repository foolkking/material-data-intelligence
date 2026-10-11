"""Readable report support projected from its exact saved Result, never prose."""
from __future__ import annotations

import json
from collections import Counter
from typing import Any

from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.domain.scientific_results.reference_sources import project_reference_context


def report_scientific_basis(
    *, snapshot_id: str, bundle: ScientificResultBundle, report: dict[str, Any],
    artifacts: list[dict[str, Any]], calls: list[dict[str, Any]],
    artifact_versions: dict[str, set[str]],
) -> dict[str, Any]:
    """Attach values and exact source coordinates without copying model inputs.

    File/call links additionally require an owned, unique saved record. A
    missing file does not erase a saved fact, or select another file/source.
    """
    sections = [*report.get("main_findings", []), *report.get("primary_figures", [])]
    sections.extend(value for key in ("discussion", "conclusion", "next_steps")
                    if isinstance(value := report.get(key), dict))
    fact_ids = {ref for section in sections for ref in section.get("fact_refs", [])}
    evidence_ids = {ref for section in sections for ref in section.get("evidence_refs", [])}
    evidence_ids.update(report.get("evidence_refs", []))
    # Names used by table metrics must come from the same saved subject. They
    # are available for labels, but are displayed only when explicitly cited.
    subjects = {(fact.subject_ref, fact.source.artifact_id) for fact in bundle.facts
                if fact.fact_id in fact_ids}
    label_predicates = {"table.numeric.column", "table.categorical.column", "histogram.column",
                        "correlation.left_column", "correlation.right_column", "reference.element.symbol",
                        "composition.element", "calculation.function", "inline.column"}
    fact_ids.update(fact.fact_id for fact in bundle.facts if fact.predicate in label_predicates
                    and (fact.subject_ref, fact.source.artifact_id) in subjects)

    def key(ref: Any) -> tuple[str, str]:
        return str(ref.object_id), str(ref.version_id)

    refs = [*bundle.source_object_refs, *bundle.output_object_refs]
    ref_counts = Counter(key(ref) for ref in refs)
    known_refs = {key(ref): ref for ref in refs if ref_counts[key(ref)] == 1}

    def checked(refs: list[Any]) -> dict[tuple[str, str], Any] | None:
        result = {}
        for ref in refs:
            known = known_refs.get(key(ref))
            if (known is None or ref.project_id != bundle.project_id
                    or known.object_type != ref.object_type):
                return None
            result[key(ref)] = known
        return result

    def sources(explicit: list[Any], artifact_id: str | None, items: list[Any]) -> list[dict[str, Any]]:
        candidates = []
        if explicit:
            direct = checked(explicit)
            if direct is None:
                return []
            candidates.append(direct)
        versions = artifact_versions.get(artifact_id or "", set())
        if versions:
            produced = {identity: ref for identity, ref in known_refs.items() if str(ref.version_id) in versions}
            if {str(ref.version_id) for ref in produced.values()} != versions:
                return []
            candidates.append(produced)
        # A result's own references are usable only if it is the unique item
        # naming this fact/evidence and, when supplied, its exact artifact.
        matched = [item for item in items if not artifact_id or artifact_id in item.artifact_ids]
        if len(matched) == 1 and matched[0].scientific_object_refs:
            item_refs = checked(matched[0].scientific_object_refs)
            if item_refs is None:
                return []
            candidates.append(item_refs)
        if not candidates:
            return []
        selected = candidates[0]
        # Explicit fact scope can be narrower than a combined Result. Two
        # incompatible scopes must not silently borrow a material's label.
        if any(not set(selected).issubset(candidate) for candidate in candidates[1:]):
            return []
        return [{
            "object_id": str(ref.object_id), "version_id": str(ref.version_id),
            "object_type": ref.object_type, "display_name": ref.display_name,
        } for ref in selected.values()]

    job_id = str(bundle.provenance.job_id or "")
    artifact_counts = Counter(str(item.get("id") or item.get("artifactId") or "") for item in artifacts)
    owned = {str(item.get("id") or item.get("artifactId")): item for item in artifacts
             if artifact_counts[str(item.get("id") or item.get("artifactId"))] == 1
             and item.get("projectId") == bundle.project_id and item.get("jobId") == job_id
             and str(item.get("id") or item.get("artifactId")) in bundle.provenance.artifact_ids}
    call_counts = Counter(str(call.get("id") or "") for call in calls)
    saved_calls = {str(call["id"]): call for call in calls if call.get("id")
                   and call_counts[str(call["id"])] == 1 and call.get("jobId") == job_id
                   and str(call["id"]) in bundle.provenance.tool_call_ids}
    reference_context = project_reference_context(bundle)
    reference_sources = reference_context["reference_sources"] if reference_context else []
    parameter_inputs = {item["tool_call_id"]: item for item in (reference_context or {}).get("parameter_inputs", [])}
    verified_parameter_inputs: set[str] = set()

    def location(artifact_id: str | None, tool_call_id: str | None, locator: str | None,
                 *, material_bound: bool = False) -> dict[str, Any]:
        artifact = owned.get(artifact_id or "")
        producer = artifact.get("toolCallId") if artifact else None
        conflict = bool(tool_call_id and producer and tool_call_id != producer)
        call = saved_calls.get(str(tool_call_id or producer or "")) if not conflict else None
        references = []
        parameter = None
        if (artifact and call and not conflict and artifact.get("datasetId") is None
                and not material_bound and not artifact_versions.get(artifact_id or "")):
            provenance = (artifact.get("metadata") or {}).get("provenance") or {}
            declared = provenance.get("referenceSources", [])
            references = [source["referenceId"] for source in reference_sources
                          if {key: source[key] for key in ("referenceId", "version", "contentHash")} in declared]
            candidate = parameter_inputs.get(str(call["id"]))
            if (candidate and candidate["tool_id"] == call.get("toolId")
                    and candidate["input_origin"] == provenance.get("inputOrigin")
                    and candidate["content_hash"] == provenance.get("inputHash")):
                parameter = candidate
                verified_parameter_inputs.add(str(call["id"]))
        return {
            "artifact_id": artifact_id, "artifact_locator": locator,
            "job_id": job_id if artifact and not conflict else None,
            "artifact_name": str(artifact.get("name") or "") if artifact and not conflict else None,
            "tool_call_id": str(call["id"]) if call else tool_call_id,
            "tool_id": str(call["toolId"]) if call and call.get("toolId") else None,
            **({"reference_source_ids": references} if references else {}),
            **({"input_origin": parameter["input_origin"], "input_hash": parameter["content_hash"]} if parameter else {}),
        }

    def exact_text(value: Any) -> str:
        # Numeric text travels separately from JSON numbers so JS cannot round
        # a large integer or the stored floating-point representation on read.
        return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, allow_nan=False)

    basis = {
        "project_id": bundle.project_id, "result_snapshot_id": snapshot_id,
        **({"input_origin": reference_context["input_origin"]} if reference_context else {}),
        **({"reference_sources": reference_sources} if reference_sources else {}),
        "facts": [{
            "fact_id": fact.fact_id, "predicate": fact.predicate, "subject_ref": fact.subject_ref,
            "value_text": exact_text(fact.value), "unit": fact.unit,
            "uncertainty_text": exact_text(fact.uncertainty) if fact.uncertainty is not None else None,
            "source_refs": sources(
                [fact.source.scientific_object_ref] if fact.source.scientific_object_ref else [],
                fact.source.artifact_id, [item for item in bundle.result_items if fact.fact_id in item.fact_refs],
            ),
            **location(fact.source.artifact_id, fact.source.tool_call_id, fact.source.artifact_locator,
                       material_bound=bool(fact.source.scientific_object_ref) or any(
                           item.scientific_object_refs for item in bundle.result_items if fact.fact_id in item.fact_refs)),
        } for fact in bundle.facts if fact.fact_id in fact_ids],
        "evidence": [{
            "evidence_id": evidence.evidence_id, "evidence_type": evidence.evidence_type,
            "source_refs": sources(evidence.scientific_object_refs, evidence.artifact_id,
                                   [item for item in bundle.result_items if evidence.evidence_id in item.evidence_refs]),
            **location(evidence.artifact_id, evidence.tool_call_id, evidence.artifact_locator,
                       material_bound=bool(evidence.scientific_object_refs) or any(
                           item.scientific_object_refs for item in bundle.result_items if evidence.evidence_id in item.evidence_refs)),
        } for evidence in bundle.evidence if evidence.evidence_id in evidence_ids],
    }
    if verified_parameter_inputs:
        # Only expose inputs bound to this report's cited, owned artifacts.
        # Other calls in the snapshot and conflicting sample sources stay out.
        basis["parameter_inputs"] = [item for call_id, item in parameter_inputs.items()
                                     if call_id in verified_parameter_inputs]
    return basis
