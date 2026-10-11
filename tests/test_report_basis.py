from copy import deepcopy
import json
from types import SimpleNamespace as NS
from uuid import UUID

import pytest

from mdi_api.application.scientific_reports.basis import report_scientific_basis
from mdi_api.infrastructure.scientific_reports.service import ScientificReportError, ScientificReportService
from tests.test_agent2_reports import _bundle, _interpretation, _report, RESULT_ID, TURN_ID


def _project(bundle=None, *, artifacts=None, calls=None, artifact_versions=None):
    bundle = bundle or _bundle()
    return report_scientific_basis(
        snapshot_id="saved-snapshot", bundle=bundle,
        report={"main_findings": [{"fact_refs": [fact.fact_id for fact in bundle.facts],
                                   "evidence_refs": [item.evidence_id for item in bundle.evidence]}]},
        artifacts=artifacts or [], calls=calls or [], artifact_versions=artifact_versions or {},
    )


@pytest.mark.parametrize("value,expected", [
    (0, "0"), (False, "false"), (None, "null"), (0.085023, "0.085023"),
    (3.1000000000000005, "3.1000000000000005"), (9007199254740993, "9007199254740993"),
    ("source_native", "source_native"), ({"x": [1, 0]}, '{"x": [1, 0]}'),
])
def test_basis_keeps_saved_values_exact_without_parsing_the_report(value, expected):
    bundle = _bundle()
    bundle.facts[0].value = value
    before = bundle.model_dump_json()
    view = _project(bundle)
    assert view["facts"][0]["value_text"] == expected
    assert view["result_snapshot_id"] == "saved-snapshot"
    assert view["facts"][0]["source_refs"][0]["version_id"] == str(bundle.source_object_refs[0].version_id)
    assert bundle.model_dump_json() == before


def test_basis_scopes_same_named_material_versions_by_saved_fact_item_identity():
    bundle = _bundle()
    first = bundle.source_object_refs[0]
    second = first.model_copy(update={"version_id": UUID(int=901)})
    bundle.source_object_refs.append(second)
    new_fact = bundle.facts[0].model_copy(deep=True, update={"fact_id": "other-fact", "value": 9.0})
    new_fact.source.artifact_id = "other-artifact"
    new_item = bundle.result_items[0].model_copy(update={"id": "other-item", "scientific_object_refs": [second],
        "artifact_ids": ["other-artifact"], "fact_refs": [new_fact.fact_id], "evidence_refs": []})
    bundle.result_items.insert(0, new_item)
    bundle.facts.append(new_fact)
    view = _project(bundle)
    assert [fact["source_refs"][0]["version_id"] for fact in view["facts"]] == [str(first.version_id), str(second.version_id)]
    assert [fact["value_text"] for fact in view["facts"]] == ["2.84", "9.0"]


@pytest.mark.parametrize("case", ["missing", "foreign", "conflicting-version", "ambiguous-item", "duplicate-source"])
def test_basis_does_not_guess_source_scope(case):
    bundle = _bundle()
    source = bundle.source_object_refs[0]
    versions = {}
    if case == "missing":
        bundle.result_items = []
    elif case == "foreign":
        bundle.facts[0].source.scientific_object_ref = source.model_copy(update={"project_id": "foreign"})
    elif case == "conflicting-version":
        versions[bundle.facts[0].source.artifact_id] = {str(UUID(int=808))}
    elif case == "ambiguous-item":
        bundle.result_items.append(bundle.result_items[0].model_copy(update={"id": "other"}))
    else:
        bundle.source_object_refs.append(source.model_copy())
    fact = _project(bundle, artifact_versions=versions)["facts"][0]
    assert fact["source_refs"] == []
    assert fact["value_text"] == "2.84"


@pytest.mark.parametrize("case", ["owned", "foreign-project", "foreign-job", "duplicate", "unlisted", "conflicting-call"])
def test_basis_file_links_require_exact_owned_records_and_omit_execution_payloads(case):
    bundle = _bundle()
    artifact = {"id": bundle.facts[0].source.artifact_id, "jobId": bundle.provenance.job_id,
                "projectId": bundle.project_id, "name": "rdf.json", "toolCallId": bundle.facts[0].source.tool_call_id,
                "sensitive": "NEVER_EXPORT_THIS"}
    call = {"id": bundle.facts[0].source.tool_call_id, "jobId": bundle.provenance.job_id,
            "toolId": "structure.rdf", "paramsJson": {"secret": "NEVER_EXPORT_THIS"}}
    if case == "foreign-project": artifact["projectId"] = "another-project"
    if case == "foreign-job": artifact["jobId"] = "another-job"
    if case == "unlisted": bundle.provenance.artifact_ids = []
    if case == "conflicting-call": artifact["toolCallId"] = "other-call"
    artifacts = [artifact, deepcopy(artifact)] if case == "duplicate" else [artifact]
    view = _project(bundle, artifacts=artifacts, calls=[call])
    assert view["facts"][0]["job_id"] == (bundle.provenance.job_id if case == "owned" else None)
    assert "NEVER_EXPORT_THIS" not in json.dumps(view)


def _read_fixture():
    bundle = _bundle().model_dump(mode="json")
    snapshot = {"id": RESULT_ID, "project_id": "project_1", "research_turn_id": TURN_ID, "bundle_json": bundle}
    interpretation_id = UUID(int=72)
    interpretation = {"id": interpretation_id, "project_id": "project_1", "research_turn_id": TURN_ID,
                      "result_snapshot_id": RESULT_ID, "output_json": _interpretation()}
    row = {"scientific_result_snapshot_id": RESULT_ID, "scientific_interpretation_id": interpretation_id,
           "project_id": "project_1", "research_turn_id": TURN_ID}
    session = NS(agent2=NS(scientific_result_snapshots=NS(get=lambda identity: snapshot),
                          interpretations=NS(get=lambda identity: interpretation)))
    return row, snapshot, interpretation, session


@pytest.mark.parametrize("record,field", [
    ("snapshot", "id"), ("snapshot", "project_id"), ("snapshot", "research_turn_id"),
    ("interpretation", "id"), ("interpretation", "project_id"),
    ("interpretation", "research_turn_id"), ("interpretation", "result_snapshot_id"),
])
def test_report_read_rejects_mismatched_authority_before_exposing_values(record, field):
    row, snapshot, interpretation, session = _read_fixture()
    (snapshot if record == "snapshot" else interpretation)[field] = "unrelated"
    with pytest.raises(ScientificReportError, match="来源未能核对"):
        ScientificReportService._with_viewer_sources({"report": _report().model_dump(mode="json")}, session, row)


def test_report_read_keeps_the_original_result_when_interpretation_reuses_an_earlier_turn():
    row, snapshot, interpretation, session = _read_fixture()
    row["research_turn_id"] = interpretation["research_turn_id"] = UUID(int=82)
    view = ScientificReportService._with_viewer_sources({"report": _report().model_dump(mode="json")}, session, row)
    assert view["scientific_basis"]["result_snapshot_id"] == str(RESULT_ID)
    assert view["scientific_basis"]["facts"][0]["value_text"] == "2.84"
    assert snapshot["research_turn_id"] == TURN_ID
