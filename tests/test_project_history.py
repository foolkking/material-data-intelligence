from __future__ import annotations

import json
from types import SimpleNamespace

from mdi_api.project_history import ProjectHistoryService


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
