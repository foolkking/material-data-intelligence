from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.scientific_results.fingerprint import ScientificResultSourceFingerprint
from mdi_api.scientific_results.projectors.base import ScientificResultProjectionContext
from mdi_api.scientific_results.projectors.canonical import build_canonical_result_projectors
from mdi_api.scientific_results.schemas import (
    FactSourceLocator,
    ScientificFact,
    ScientificResultBundle,
)


def _context(payload, *, content_type="application/json"):
    turn_id = uuid4()
    ref = ScientificObjectRef(object_id=uuid4(), version_id=uuid4(), project_id="project", object_type="structure.crystal")
    return ScientificResultProjectionContext(
        project_id="project", research_session_id="session", research_turn_id=str(turn_id),
        research_question="Compute RDF", execution_summary={"outcome": "SUCCESS", "job_id": "job-1", "analysis_plan_id": "plan-1"},
        capability_plan={"steps": [{"step_id": "step_1", "capability_id": "structure.rdf", "capability_version": "1.0", "parameters": {}}]},
        analysis_plan={"schemaVersion": "0.2"}, tool_calls=(),
        artifacts=({"id": "artifact-1", "contentType": content_type},), artifact_payloads={"artifact-1": payload},
        source_object_refs=(ref,),
    )


def test_rdf_projector_is_machine_readable_and_deterministic():
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.structure.rdf")
    first = projector.project(_context({"rdf": {"r_angstrom": [1.0], "g_r": [2.0]}})).bundle
    second = projector.project(_context({"rdf": {"r_angstrom": [1.0], "g_r": [2.0]}})).bundle
    assert {fact.value for fact in first.facts} == {1.0, 2.0}
    assert all(fact.source.artifact_id == "artifact-1" and fact.source.artifact_locator for fact in first.facts)
    assert first.model_dump(mode="json")["facts"] == second.model_dump(mode="json")["facts"]


def test_image_only_artifact_never_creates_numeric_fact():
    projector = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.structure.rdf")
    bundle = projector.project(_context(None, content_type="image/png")).bundle
    assert bundle.facts == []
    assert len(bundle.figures) == 1


def test_fingerprint_is_order_independent():
    left = ScientificResultSourceFingerprint.compute(artifacts=[{"id": "a"}, {"id": "b"}], tool_calls=[{"id": "t"}], projector_ids=["p"])
    right = ScientificResultSourceFingerprint.compute(projector_ids=["p"], tool_calls=[{"id": "t"}], artifacts=[{"id": "a"}, {"id": "b"}])
    assert left == right


def test_invalid_fact_source_rejected():
    with pytest.raises(ValidationError):
        FactSourceLocator()


def test_dangling_bundle_fact_reference_rejected():
    ref = ScientificObjectRef(object_id=uuid4(), version_id=uuid4(), project_id="project", object_type="structure.crystal")
    with pytest.raises(ValidationError):
        ScientificResultBundle(
            schema_version="1.0", result_id=uuid4(), project_id="project", research_session_id="session", research_turn_id=uuid4(),
            research_question="x", source_object_refs=[ref], execution_status="SUCCESS", relevance_status="CURRENT",
            result_items=[{"id": "item", "result_type": "rdf", "role": "PRIMARY", "title": "RDF", "artifact_ids": [], "scientific_object_refs": [ref], "fact_refs": ["missing"], "evidence_refs": []}],
            facts=[], figures=[], tables=[], output_object_refs=[], evidence=[], methods=[], limitations=[], warnings=[], provenance={}, projection_version="agent2.result/1.0",
        )
