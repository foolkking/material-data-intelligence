from __future__ import annotations

import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from mdi_api.project_history import ProjectHistoryService
from mdi_api.application.projects.history import (
    ProjectHistoryService as CanonicalProjectHistoryService,
)
from mdi_api.routers.project_history import _archived_run_ids_from_config


def test_legacy_project_history_export_is_canonical_symbol() -> None:
    assert ProjectHistoryService is CanonicalProjectHistoryService


class Records:
    def __init__(self, records: list[dict[str, object]]) -> None:
        self.records = records

    def get(self, record_id: str) -> dict[str, object]:
        for item in self.records:
            if record_id in {item.get("id"), item.get("projectId"), item.get("intentId")}:
                return item
        raise LookupError(record_id)

    def list(self) -> list[dict[str, object]]:
        return self.records

    def list_for_project(self, project_id: str) -> list[dict[str, object]]:
        return [item for item in self.records if item.get("projectId") == project_id]

    def list_by_project(self, project_id: str) -> list[dict[str, object]]:
        return self.list_for_project(project_id)

    def list_for_dataset(self, dataset_id: str) -> list[dict[str, object]]:
        return [item for item in self.records if item.get("datasetId") == dataset_id]

    def list_for_job(self, job_id: str) -> list[dict[str, object]]:
        return [item for item in self.records if item.get("jobId") == job_id or item.get("sourceJobId") == job_id]


class IntentRecords(Records):
    def get_execution_for_job(self, job_id: str) -> dict[str, object] | None:
        return {"intentId": "intent_1"} if job_id == "job_1" else None

    def get_intent(self, intent_id: str) -> dict[str, object]:
        return self.get(intent_id)


class PlanRecords(Records):
    def get_plan_for_job(self, job_id: str) -> dict[str, object]:
        if job_id != "job_1":
            raise LookupError(job_id)
        return {"steps": [{"stepId": "step_1"}]}


class MalformedPlanRecords(Records):
    def get_plan_for_job(self, job_id: str) -> dict[str, object]:
        raise ValueError("AnalysisPlan record is missing analysis_plan_json")


def test_project_history_links_persisted_import_analysis_and_results() -> None:
    project_id = "project_1"
    repositories = SimpleNamespace(
        projects=Records([{
            "id": project_id,
            "projectId": project_id,
            "name": "Apatite screening",
            "description": "Imported materials and analysis history",
            "status": "active",
            "createdAt": "2026-08-17T01:00:00Z",
        }]),
        datasets=Records([{
            "id": "dataset_1",
            "datasetId": "dataset_1",
            "projectId": project_id,
            "name": "materials.csv",
            "status": "ready",
            "createdAt": "2026-08-17T02:00:00Z",
            "metadata": {
                "files": [{
                    "fileId": "file_1",
                    "name": "materials.csv",
                    "detectedFormat": "csv",
                    "status": "succeeded",
                    "byteSize": 2048,
                    "objectCount": 1,
                    "storageKey": "private/source.csv",
                    "sha256": "not-user-facing",
                }],
                "normalizedExports": [{
                    "objectId": "table_1",
                    "metadata": {"objectType": "table", "storageKey": "private/table.json"},
                }],
            },
        }]),
        data_profiles=Records([{
            "profileId": "profile_1",
            "projectId": project_id,
            "datasetId": "dataset_1",
            "schemaVersion": "DataProfile/1.1",
            "datasetType": "tabular",
            "createdAt": "2026-08-17T02:01:00Z",
            "tableSummary": {
                "nRows": 25,
                "columns": [{"name": "band_gap", "semanticRole": "material_property"}],
            },
            "readiness": [{"capability": "TABULAR_DATA", "status": "READY"}],
        }]),
        jobs=Records([{
            "id": "job_1",
            "jobId": "job_1",
            "projectId": project_id,
            "datasetId": "dataset_1",
            "status": "succeeded",
            "createdAt": "2026-08-17T03:00:00Z",
            "updatedAt": "2026-08-17T03:03:00Z",
        }]),
        tool_calls=Records([{"jobId": "job_1", "toolId": "viz.histogram"}]),
        artifacts=Records([{
            "artifactId": "artifact_1",
            "jobId": "job_1",
            "projectId": project_id,
            "type": "plot.histogram",
            "storageKey": "private/artifact.json",
        }]),
        workspaces=Records([{
            "workspaceId": "workspace_1",
            "projectId": project_id,
            "sourceJobId": "job_1",
            "title": "Band-gap distribution",
        }]),
        reports=Records([{"reportId": "report_1", "projectId": project_id, "sourceJobId": "job_1"}]),
        recipes=Records([{"recipeId": "recipe_1", "projectId": project_id, "sourceJobId": "job_1"}]),
        interpretations=Records([{"interpretationId": "interp_1", "projectId": project_id, "jobId": "job_1"}]),
        analysis_intents=IntentRecords([{
            "id": "intent_1",
            "intentId": "intent_1",
            "analysisIntent": {"rawUserRequest": "Show the distribution of band gap."},
        }]),
        analysis_plans=PlanRecords([]),
    )

    result = ProjectHistoryService(repositories).build(project_id)

    assert result["schemaVersion"] == "ProjectHistoryView/1.0"
    assert result["summary"] == {
        "datasetCount": 1,
        "analysisCount": 1,
        "completedAnalysisCount": 1,
        "artifactCount": 1,
        "workspaceCount": 1,
        "reportCount": 1,
        "lastActivityAt": "2026-08-17T03:03:00Z",
    }
    dataset = result["datasets"][0]
    assert dataset["import"]["files"][0]["name"] == "materials.csv"
    assert dataset["import"]["resources"] == [{"objectId": "table_1", "objectType": "table"}]
    assert dataset["profile"]["rowCount"] == 25
    assert dataset["profile"]["semanticRoles"] == {"material_property": 1}
    assert dataset["process"][0] == {
        "key": "import",
        "label": "导入",
        "status": "succeeded",
        "detail": "1 个源文件",
    }
    assert dataset["process"][1]["detail"] == "25 行 · 1 列"
    assert dataset["resultSummary"] == {
        "artifactCount": 1,
        "workspaceCount": 1,
        "interpretationCount": 1,
        "reportCount": 1,
        "recipeCount": 1,
        "artifactTypes": ["plot.histogram"],
        "latestReportStatus": None,
    }

    analysis = result["analyses"][0]
    assert analysis["userQuestion"] == "Show the distribution of band gap."
    assert analysis["toolIds"] == ["viz.histogram"]
    assert analysis["artifactTypes"] == ["plot.histogram"]
    assert analysis["workspaceId"] == "workspace_1"
    assert result["activity"][0]["href"] == "/workspaces/workspace_1"

    serialized = json.dumps(result)
    assert "storageKey" not in serialized
    assert "sha256" not in serialized
    assert "private/" not in serialized


def test_project_history_marks_archived_run_without_changing_execution_facts() -> None:
    repositories = SimpleNamespace(
        projects=Records([{"id": "project_1", "projectId": "project_1", "name": "Project"}]),
        datasets=Records([]), data_profiles=Records([]),
        jobs=Records([{"id": "job_1", "jobId": "job_1", "projectId": "project_1", "status": "completed", "createdAt": "2026-08-17T03:00:00Z"}]),
        tool_calls=Records([]), artifacts=Records([]), workspaces=Records([]), reports=Records([]),
        recipes=Records([]), interpretations=Records([]), analysis_intents=IntentRecords([]), analysis_plans=PlanRecords([]),
    )
    result = ProjectHistoryService(repositories, archived_run_ids={"job_1"}).build("project_1")
    analysis = result["analyses"][0]
    assert analysis["status"] == "completed"
    assert analysis["archived"] is True
    assert analysis["visibleInReports"] is False
    assert result["activity"][0]["archived"] is True


def test_project_history_keeps_legacy_job_readable_when_plan_payload_is_malformed() -> None:
    repositories = SimpleNamespace(
        projects=Records([{"id": "project_1", "projectId": "project_1", "name": "Project"}]),
        datasets=Records([]), data_profiles=Records([]),
        jobs=Records([{"id": "job_1", "jobId": "job_1", "projectId": "project_1", "status": "completed", "createdAt": "2026-08-17T03:00:00Z"}]),
        tool_calls=Records([]), artifacts=Records([]), workspaces=Records([]), reports=Records([]),
        recipes=Records([]), interpretations=Records([]), analysis_intents=IntentRecords([]),
        analysis_plans=MalformedPlanRecords([]),
    )
    result = ProjectHistoryService(repositories).build("project_1")
    assert result["analyses"][0]["jobId"] == "job_1"
    assert result["analyses"][0]["stepCount"] == 0


def test_archive_projection_config_is_bounded_and_ignores_malformed_values() -> None:
    assert _archived_run_ids_from_config({"archivedRunIds": ["job_1", "", 42, None, "job_1"]}) == {"job_1"}
    assert _archived_run_ids_from_config(None) == set()


def test_project_history_paginates_large_dataset_history_with_stable_cursor() -> None:
    datasets = [{
        "id": f"dataset_{index:04d}",
        "datasetId": f"dataset_{index:04d}",
        "projectId": "project_1",
        "name": f"materials-{index:04d}.csv",
        "status": "ready",
        "createdAt": f"2026-12-31T23:59:{index:04d}Z",
    } for index in range(1000)]
    repositories = SimpleNamespace(
        projects=Records([{"id": "project_1", "projectId": "project_1", "name": "Project"}]),
        datasets=Records(datasets), data_profiles=Records([]),
        jobs=Records([]), tool_calls=Records([]), artifacts=Records([]),
        workspaces=Records([]), reports=Records([]), recipes=Records([]),
        interpretations=Records([]), analysis_intents=IntentRecords([]),
        analysis_plans=PlanRecords([]),
    )

    first = ProjectHistoryService(repositories).build("project_1", limit=8)
    second = ProjectHistoryService(repositories).build(
        "project_1", limit=100, datasets_cursor=first["pagination"]["datasets"]["nextCursor"],
    )

    assert len(first["datasets"]) == 8
    assert first["datasets"][0]["datasetId"] == "dataset_0999"
    assert first["pagination"]["datasets"]["nextCursor"] == "8"
    assert len(second["datasets"]) == 100
    assert second["datasets"][0]["datasetId"] == "dataset_0991"
    assert second["pagination"]["datasets"]["nextCursor"] == "108"


def _multi_material_history():
    from mdi_api.application.research.planning.integrity import compute_plan_hash
    from mdi_schemas import AnalysisPlanV03
    from mdi_schemas.multi_source_planning import step_source_inventory
    from tests.test_multi_source_plan_contract import payload, V1, V2

    plan = payload()
    third = "33333333-3333-4333-8333-333333333333"
    plan["sourceContexts"].append({"datasetId": "dataset_c", "profileId": "profile_c"})
    plan["sourceVersions"].append({"objectId": third, "versionId": third, "datasetId": "dataset_c", "objectType": "Structure"})
    plan["steps"].append({**deepcopy(plan["steps"][0]), "stepId": "s3", "inputRefs": [
        {"refType": "normalized_object", "ref": third, "objectType": "Structure"}], "output": {"sourceObjectVersionIds": [third]}})
    plan["steps"].append({"stepId": "compare_ab", "toolId": "compare", "purpose": "Compare two materials", "reason": "Pairwise comparison",
        "inputRefs": [{"refType": "normalized_object", "ref": value, "objectType": "Structure"} for value in (V1, V2)],
        "output": {"sourceObjectVersionIds": [V1, V2]}})
    plan_record = {"planId": "plan_multi", "projectId": "project_1", "datasetId": "dataset_a", "profileId": "profile_a",
        "analysisPlan": plan, "planHash": compute_plan_hash(plan)}

    class MultiPlanRecords(Records):
        def get_plan_for_job(self, job_id):
            return self.records[0]

    # SQL ToolCalls inherit Project ownership through Job; they do not carry
    # the denormalized projectId field from older in-memory fixtures.
    calls = [{"id": f"call_{step['stepId']}", "jobId": "job_multi", "stepId": step["stepId"], "toolId": step["toolId"]} for step in plan["steps"]]
    artifacts = [{"artifactId": f"artifact_{index}", "jobId": "job_multi", "projectId": "project_1", "toolCallId": call["id"],
        "datasetId": f"dataset_{chr(97 + index)}" if index < 3 else None, "type": "table_json"} for index, call in enumerate(calls)]
    for artifact, call in zip(artifacts, calls):
        contexts, versions = step_source_inventory(AnalysisPlanV03.model_validate(plan), call["stepId"])
        artifact["metadata"] = {"provenance": {"planId": "plan_multi", "planHash": plan_record["planHash"],
            "sourceContexts": [item.model_dump(mode="json") for item in contexts],
            "sourceVersions": [item.model_dump(mode="json") for item in versions]}}
    return SimpleNamespace(
        projects=Records([{"id": "project_1", "projectId": "project_1", "name": "Three materials"}]),
        datasets=Records([{"datasetId": f"dataset_{key}", "projectId": "project_1", "name": key} for key in "abc"]),
        data_profiles=Records([]), jobs=Records([{"jobId": "job_multi", "projectId": "project_1", "datasetId": "dataset_a", "planId": "plan_multi", "status": "completed"}]),
        tool_calls=Records(calls), artifacts=Records(artifacts), workspaces=Records([]), reports=Records([]), recipes=Records([]),
        interpretations=Records([]), analysis_intents=IntentRecords([]), analysis_plans=MultiPlanRecords([plan_record]),
    )


def test_multi_material_history_counts_each_analysis_once_and_only_its_own_outputs():
    repositories = _multi_material_history()
    before = deepcopy({name: value.records for name, value in vars(repositories).items()})
    history = ProjectHistoryService(repositories).build("project_1")
    assert len(history["analyses"]) == 1
    assert history["analyses"][0]["sourceDatasetIds"] == ["dataset_a", "dataset_b", "dataset_c"]
    assert history["analyses"][0]["datasetId"] == "dataset_a"  # Job routing identity remains intact.
    assert history["analyses"][0]["stepCount"] == 4
    assert history["summary"]["analysisCount"] == 1
    assert history["summary"]["artifactCount"] == 4
    by_dataset = {item["datasetId"]: item for item in history["datasets"]}
    for dataset in by_dataset.values():
        assert dataset["analysisCount"] == 1
        assert dataset["lastAnalysisStatus"] == "completed"
    assert [by_dataset[f"dataset_{key}"]["resultSummary"]["artifactCount"] for key in "abc"] == [2, 2, 1]
    assert before == {name: value.records for name, value in vars(repositories).items()}
    paged = ProjectHistoryService(repositories).build("project_1", limit=1, datasets_cursor="1")
    assert paged["datasets"][0]["analysisCount"] == 1
    assert paged["datasets"][0]["resultSummary"]["artifactCount"] == 2


@pytest.mark.parametrize("field,value", [("planId", "another_plan"), ("projectId", "foreign"), ("planHash", "0" * 64), ("profileId", "foreign_profile")])
def test_multi_material_history_does_not_guess_sources_from_an_unverified_plan(field, value):
    repositories = _multi_material_history()
    repositories.analysis_plans.records[0][field] = value
    history = ProjectHistoryService(repositories).build("project_1")
    assert history["analyses"][0]["sourceDatasetIds"] == []
    assert history["summary"]["artifactCount"] == 4  # Originals stay accessible by Job.
    assert all(item["analysisCount"] == 0 and item["resultSummary"]["artifactCount"] == 0 for item in history["datasets"])


def test_multi_material_history_does_not_borrow_outputs_from_another_step_or_project():
    repositories = _multi_material_history()
    repositories.artifacts.records[0]["toolCallId"] = "unknown"
    repositories.artifacts.records[1]["datasetId"] = "dataset_a"
    repositories.tool_calls.records[2]["projectId"] = "foreign"
    history = ProjectHistoryService(repositories).build("project_1")
    assert [item["resultSummary"]["artifactCount"] for item in history["datasets"]] == [1, 1, 0]


@pytest.mark.parametrize("field,value", [("planHash", "0" * 64), ("planId", "another_plan"), ("sourceVersions", []), ("sourceContexts", [])])
def test_multi_material_history_rejects_conflicting_saved_output_provenance(field, value):
    repositories = _multi_material_history()
    repositories.artifacts.records[3]["metadata"]["provenance"][field] = value
    history = ProjectHistoryService(repositories).build("project_1")
    assert [item["resultSummary"]["artifactCount"] for item in history["datasets"]] == [1, 1, 1]


def test_failed_multi_material_history_retains_all_sources_without_inventing_outputs():
    repositories = _multi_material_history()
    repositories.jobs.records[0]["status"] = "failed"
    repositories.artifacts.records.clear()
    repositories.tool_calls.records.clear()
    history = ProjectHistoryService(repositories).build("project_1")
    assert history["analyses"][0]["sourceDatasetIds"] == ["dataset_a", "dataset_b", "dataset_c"]
    assert all(item["analysisCount"] == 1 and item["lastAnalysisStatus"] == "failed" and item["resultSummary"]["artifactCount"] == 0 for item in history["datasets"])
