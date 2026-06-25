from __future__ import annotations

from fastapi.testclient import TestClient

from mdi_api import create_app
from mdi_api.phase2_runtime import (
    PHASE2_TOOL_ORDER,
    DatasetUploadRequest,
    build_phase2_plan,
    reset_phase2_runtime,
)
from mdi_schemas import ArtifactType


def _fixture_paths(repo_root):
    return [
        repo_root / "tests" / "fixtures" / "structures" / "si.cif",
        repo_root / "tests" / "fixtures" / "structures" / "POSCAR",
        repo_root / "tests" / "fixtures" / "tables" / "ml_results.csv",
    ]


def _seed_project_and_dataset(tmp_path, repo_root):
    runtime = reset_phase2_runtime(tmp_path / "artifacts")
    project = runtime.create_project({"name": "Phase 2 Test Project"})
    dataset = runtime.upload_dataset(
        DatasetUploadRequest(
            projectId=project["id"],
            datasetName="Mixed CIF POSCAR CSV dataset",
            filePaths=[str(path) for path in _fixture_paths(repo_root)],
        )
    )
    return runtime, project, dataset


def test_phase2_data_pipeline_upload_generates_profile_and_normalized_exports(tmp_path, repo_root):
    runtime, project, dataset = _seed_project_and_dataset(tmp_path, repo_root)
    profile = runtime.get_dataset_profile(dataset["id"])

    assert dataset["projectId"] == project["id"]
    assert dataset["status"] == "profile_ready"
    assert {item["detectedFormat"] for item in dataset["files"]} == {"cif", "poscar", "csv"}
    assert profile["datasetType"] == "mixed_material_dataset"
    assert profile["structureSummary"]["nStructures"] == 2
    assert profile["tableSummary"]["inferredTask"] == "regression"

    assert dataset["normalizedExports"]
    for exported in dataset["normalizedExports"]:
        assert (runtime.artifact_root / exported["storageKey"]).exists()
        assert (runtime.artifact_root / exported["metadataKey"]).exists()


def test_phase2_deterministic_planner_selects_three_to_five_mvp_tools(tmp_path, repo_root):
    runtime, _, dataset = _seed_project_and_dataset(tmp_path, repo_root)
    record = runtime.datasets[dataset["id"]]
    plan = build_phase2_plan(
        user_prompt="Analyze composition, structure, and ML errors.",
        data_profile=record.profile,
        registry=runtime.registry,
        object_refs=record.object_refs,
    )

    planned_tools = [step.toolId for step in plan.steps]
    assert planned_tools == list(PHASE2_TOOL_ORDER)
    assert 3 <= len(planned_tools) <= 5
    assert {"composition", "structure", "ml"} == {tool_id.split(".", 1)[0] for tool_id in planned_tools}
    assert plan.expectedArtifacts
    expected_artifacts = [item.model_dump(mode="json") for item in plan.expectedArtifacts]
    assert all(set(item) == {"name", "type", "fromStepId"} for item in expected_artifacts)
    assert {item["fromStepId"] for item in expected_artifacts} == {step.stepId for step in plan.steps}


def test_phase2_local_worker_runtime_records_job_events_and_tool_calls(tmp_path, repo_root):
    runtime, project, dataset = _seed_project_and_dataset(tmp_path, repo_root)
    job = runtime.create_job(
        {
            "projectId": project["id"],
            "datasetId": dataset["id"],
            "userPrompt": "Create a reproducible material analysis report.",
        }
    )

    assert job["status"] == "completed"
    assert job["toolCallCount"] == 5
    assert job["artifactCount"] >= 20

    event_types = [event["eventType"] for event in runtime.get_job_events(job["id"])]
    for required in (
        "job.created",
        "job.queued",
        "job.running",
        "profile.ready",
        "plan.generated",
        "tool.started",
        "artifact.ready",
        "report.ready",
        "job.completed",
    ):
        assert required in event_types

    tool_calls = runtime.get_job_tool_calls(job["id"])
    assert [tool_call["toolId"] for tool_call in tool_calls] == list(PHASE2_TOOL_ORDER)
    assert all(tool_call["status"] == "completed" for tool_call in tool_calls)


def test_phase2_local_file_artifact_store_returns_report_and_recipe_content(tmp_path, repo_root):
    runtime, project, dataset = _seed_project_and_dataset(tmp_path, repo_root)
    job = runtime.create_job({"projectId": project["id"], "datasetId": dataset["id"]})
    artifacts = runtime.get_job_artifacts(job["id"])

    artifact_types = {artifact["type"] for artifact in artifacts}
    assert ArtifactType.analysis_plan_json.value in artifact_types
    assert ArtifactType.recipe_json.value in artifact_types
    assert ArtifactType.report_md.value in artifact_types
    assert ArtifactType.report_html.value in artifact_types

    report = next(artifact for artifact in artifacts if artifact["type"] == ArtifactType.report_md.value)
    report_detail = runtime.get_artifact(report["id"])
    assert report_detail["contentEncoding"] == "text"
    assert "Phase 2 Material Analysis Report" in report_detail["content"]

    recipe = next(artifact for artifact in artifacts if artifact["id"] == "system_recipe-recipe_json")
    recipe_detail = runtime.get_artifact(recipe["id"])
    assert recipe_detail["contentEncoding"] == "json"
    assert recipe_detail["content"]["sourceJobId"] == job["id"]
    assert recipe_detail["content"]["sourcePlanId"] == "system_plan-analysis_plan_json"
    first_recipe_step = recipe_detail["content"]["steps"][0]
    assert first_recipe_step["toolVersion"] == runtime.registry.get_tool_by_id(first_recipe_step["toolId"]).version
    assert isinstance(first_recipe_step["inputBindings"], dict)
    assert first_recipe_step["inputBindings"] == {"input_1": "formulas"}


def test_phase2_api_routes_query_upload_profile_job_tool_calls_and_artifacts(tmp_path, repo_root):
    reset_phase2_runtime(tmp_path / "artifacts")
    client = TestClient(create_app())

    project_resp = client.post("/projects", json={"name": "API Phase 2 Project"})
    assert project_resp.status_code == 200
    project = project_resp.json()

    dataset_resp = client.post(
        "/datasets/upload",
        json={
            "projectId": project["id"],
            "datasetName": "API mixed dataset",
            "filePaths": [str(path) for path in _fixture_paths(repo_root)],
        },
    )
    assert dataset_resp.status_code == 200
    dataset = dataset_resp.json()

    profile_resp = client.get(f"/datasets/{dataset['id']}/profile")
    assert profile_resp.status_code == 200
    assert profile_resp.json()["datasetType"] == "mixed_material_dataset"

    job_resp = client.post(
        "/jobs",
        json={
            "projectId": project["id"],
            "datasetId": dataset["id"],
            "userPrompt": "Run the local Phase 2 loop.",
        },
    )
    assert job_resp.status_code == 200
    job = job_resp.json()
    assert job["status"] == "completed"

    assert client.get(f"/jobs/{job['id']}").json()["artifactCount"] == job["artifactCount"]
    assert len(client.get(f"/jobs/{job['id']}/events").json()) >= 10
    assert len(client.get(f"/jobs/{job['id']}/tool-calls").json()) == 5

    artifacts = client.get(f"/jobs/{job['id']}/artifacts").json()
    report = next(artifact for artifact in artifacts if artifact["type"] == "report_md")
    artifact_detail = client.get(f"/artifacts/{report['id']}").json()
    assert artifact_detail["contentEncoding"] == "text"
    assert "Reproducibility" in artifact_detail["content"]


def test_phase2_end_to_end_product_flow_covers_profile_plan_job_artifacts_and_report(tmp_path, repo_root):
    runtime, project, dataset = _seed_project_and_dataset(tmp_path, repo_root)
    job = runtime.create_job(
        {
            "projectId": project["id"],
            "datasetId": dataset["id"],
            "userPrompt": "Analyze composition, 3D structure, and ML prediction errors.",
        }
    )

    profile = runtime.get_dataset_profile(dataset["id"])
    assert profile["structureSummary"]["nStructures"] >= 2
    assert profile["tableSummary"]["nRows"] == 3

    assert [step["toolId"] for step in job["plan"]["steps"]] == list(PHASE2_TOOL_ORDER)
    assert job["status"] == "completed"

    event_types = {event["eventType"] for event in runtime.get_job_events(job["id"])}
    assert {"plan.generated", "tool.started", "artifact.ready", "report.ready", "job.completed"}.issubset(event_types)

    artifact_types = {artifact["type"] for artifact in runtime.get_job_artifacts(job["id"])}
    assert {
        "analysis_plan_json",
        "recipe_json",
        "report_md",
        "report_html",
        "plotly_json",
        "matterviz_html",
        "metrics_json",
        "table_json",
    }.issubset(artifact_types)
