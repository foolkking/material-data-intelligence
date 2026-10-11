from copy import deepcopy
from dataclasses import replace
import json
from uuid import uuid4

import pytest

from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.application.scientific_results.projectors.base import ScientificResultProjectionContext
from mdi_api.application.scientific_results.projectors.canonical import build_canonical_result_projectors, resolve_json_pointer
from mdi_api.application.scientific_results.projectors.coordination import valid_coordination_payload
from mdi_artifact_core import content_hash, stable_json_dumps
from tests.test_local_environment_polyhedra import _n1_payload, _run, _structure, TETRAHEDRAL, SQUARE_PLANAR


def context(tmp_path, *, method="crystalnn", vectors=TETRAHEDRAL):
    structure = _structure(vectors)
    source = _n1_payload(structure, algorithm=method)
    _execution, geometry = _run(tmp_path, structure, source, {"site_indices": [0]})
    artifacts = tuple({
        "id": artifact_id, "projectId": "project_n2", "jobId": "job_n2", "toolCallId": call_id,
        "type": "table_json", "contentHash": content_hash(stable_json_dumps(payload)),
        "sha256": content_hash(stable_json_dumps(payload)),
    } for artifact_id, call_id, payload in (("artifact_n1", "call_n1", source), ("artifact_n2", "call_n2", geometry)))
    return ScientificResultProjectionContext(
        project_id="project_n2", research_session_id="session", research_turn_id=str(uuid4()),
        research_question="展示位点 0 的配位多面体与周期近邻。", execution_summary={"job_id": "job_n2", "outcome": "SUCCESS"},
        capability_plan={}, analysis_plan={}, artifacts=artifacts,
        tool_calls=({"id": "call_n1", "jobId": "job_n2", "stepId": "n1", "toolId": source["artifactType"], "status": "completed"},
                    {"id": "call_n2", "jobId": "job_n2", "stepId": "n2", "toolId": geometry["artifactType"], "status": "completed"}),
        artifact_payloads={"artifact_n1": source, "artifact_n2": geometry},
    )


def project(value, method="crystalnn"):
    name = f"agent2.structure.local_environment_{'voronoi' if method == 'voronoinn' else method}"
    return next(item for item in build_canonical_result_projectors() if item.projector_id == name).project(value)


@pytest.mark.parametrize("method", ["crystalnn", "voronoinn"])
def test_local_environment_projects_saved_site_geometry_and_exact_dependency(tmp_path, method):
    value = context(tmp_path, method=method)
    before = json.dumps(value.artifact_payloads, sort_keys=True)
    result = project(value, method)
    facts = {fact.predicate: fact for fact in result.bundle.facts}
    assert facts["structure.coordination.site_index"].value == 0
    assert facts["structure.coordination.neighbor_count"].value == 4
    assert facts["structure.local_environment.reference_geometry"].value == "tetrahedral"
    assert facts["structure.local_environment.volume"].value == pytest.approx(8 / 3 * 0.8**3, abs=1e-12)
    assert facts["structure.local_environment.volume"].unit == "angstrom^3"
    assert len([fact for fact in result.bundle.facts if fact.predicate == "structure.local_environment.relative_z"]) == 4
    indices = [fact for fact in result.bundle.facts if fact.predicate == "structure.coordination.neighbor_site_index"]
    assert [fact.value for fact in indices] == [1, 2, 3, 4]
    assert all(fact.source.artifact_id == "artifact_n1" and fact.source.artifact_locator.endswith("/neighborSiteIndex") for fact in indices)
    for fact in result.bundle.facts:
        assert resolve_json_pointer(value.artifact_payloads[fact.source.artifact_id], fact.source.artifact_locator) == fact.value
    assert result.bundle.figures[0].artifact_ids == ["artifact_n2"]
    assert result.bundle.tables == []
    assert set(result.bundle.result_items[0].artifact_ids) == {"artifact_n1", "artifact_n2"}
    assert len(result.bundle.methods) == 2
    assert "确定的化学键" in result.bundle.limitations[0].message
    assert json.dumps(value.artifact_payloads, sort_keys=True) == before


@pytest.mark.parametrize("target,field,replacement", [
    ("sourceCoordination", "artifactChecksum", "a" * 64),
    ("sourceCoordination", "artifactId", "foreign-artifact"),
    ("sourceCoordination", "parameterHash", "c" * 64),
    ("scope", "sourceResourceId", "another-structure"),
    ("scope", "jobId", "foreign-job"),
])
def test_local_environment_rejects_changed_source_binding(tmp_path, target, field, replacement):
    value = context(tmp_path)
    payloads = deepcopy(value.artifact_payloads)
    payloads["artifact_n2"][target][field] = replacement
    with pytest.raises(ScientificResultProjectionFailed):
        project(replace(value, artifact_payloads=payloads))


@pytest.mark.parametrize("change", ["coordinate", "neighbor", "face", "duplicate", "nonfinite"])
def test_local_environment_rejects_corrupted_saved_geometry(tmp_path, change):
    value = context(tmp_path)
    payloads = deepcopy(value.artifact_payloads)
    polyhedron = payloads["artifact_n2"]["siteResults"][0]["polyhedron"]
    if change == "coordinate":
        polyhedron["vertices"][0]["relativeCartesian"][2] += 1
    elif change == "neighbor":
        polyhedron["vertices"][0]["periodicImage"][1] += 1
    elif change == "face":
        polyhedron["faces"][0]["vertexIdentities"][0] = "missing"
    elif change == "duplicate":
        polyhedron["vertices"][1]["vertexIdentity"] = polyhedron["vertices"][0]["vertexIdentity"]
    else:
        polyhedron["vertices"][0]["relativeCartesian"][2] = float("nan")
    with pytest.raises(ScientificResultProjectionFailed):
        project(replace(value, artifact_payloads=payloads))


def test_coplanar_classification_does_not_invent_faces_or_volume(tmp_path):
    value = context(tmp_path, vectors=SQUARE_PLANAR)
    result = project(value)
    facts = {fact.predicate: fact.value for fact in result.bundle.facts}
    assert facts["structure.local_environment.reference_geometry"] == "square_planar"
    assert facts["structure.local_environment.face_status"] == "UNAVAILABLE"
    assert "structure.local_environment.volume" not in facts
    assert any(warning.code == "COPLANAR_POLYHEDRON" for warning in result.bundle.warnings)


def test_coordination_only_result_has_saved_site_index_and_neighbor_values(tmp_path):
    value = context(tmp_path)
    source = value.artifact_payloads["artifact_n1"]
    assert valid_coordination_payload(source)
    value = replace(value, artifacts=value.artifacts[:1], tool_calls=value.tool_calls[:1], artifact_payloads={"artifact_n1": source})
    result = next(item for item in build_canonical_result_projectors() if item.projector_id == "agent2.structure.coordination_crystalnn").project(value)
    facts = {fact.predicate: fact.value for fact in result.bundle.facts}
    assert facts["structure.coordination.site_index"] == 0
    assert facts["structure.coordination.neighbor_count"] == 4
    assert facts["structure.coordination.weighted_value"] == 4
    assert facts["structure.coordination.neighbor_distance"] == pytest.approx(0.8 * 3**0.5, abs=1e-12)
