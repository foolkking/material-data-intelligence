from __future__ import annotations

import hashlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from mdi_api import create_app
from mdi_api.artifact_storage import LocalFileArtifactStorage, S3CompatibleArtifactStorage
from mdi_api.db import PHASE3_TABLES, metadata
from mdi_api.migrations import PHASE3_MIGRATION_DRAFT_SQL
from mdi_api.phase2_runtime import PHASE2_TOOL_ORDER, reset_phase2_runtime
from mdi_api.repositories import InMemoryRepositoryBundle, SqlAlchemyRepositoryBundle


def _fixture_paths(repo_root):
    return [
        repo_root / "tests" / "fixtures" / "structures" / "si.cif",
        repo_root / "tests" / "fixtures" / "structures" / "POSCAR",
        repo_root / "tests" / "fixtures" / "tables" / "ml_results.csv",
    ]


def test_phase3_in_memory_repository_bundle_supports_seq_cursor():
    repos = InMemoryRepositoryBundle.create()
    repos.projects.save({"id": "project_mem", "name": "Memory Project"})
    repos.datasets.save({"id": "dataset_mem", "projectId": "project_mem", "name": "Memory Dataset"})
    repos.jobs.save({"id": "job_mem", "projectId": "project_mem", "datasetId": "dataset_mem", "status": "created"})

    first = repos.job_events.append_event("job_mem", event_type="job.created", status="info", message="created")
    second = repos.job_events.append_event("job_mem", event_type="job.running", status="running", message="running", progress=0.5)

    assert (first.seq, second.seq) == (1, 2)
    assert [event.seq for event in repos.job_events.list_events_after_seq("job_mem", 1)] == [2]

    repos.tool_calls.save({"id": "call_mem", "jobId": "job_mem", "stepId": "step_1", "toolId": "ml.basic_metrics", "status": "completed"})
    repos.artifacts.save(
        {
            "id": "artifact_mem",
            "projectId": "project_mem",
            "datasetId": "dataset_mem",
            "jobId": "job_mem",
            "type": "metrics_json",
            "name": "metrics.json",
            "storageKey": "projects/project_mem/jobs/job_mem/metrics.json",
            "contentHash": "abc",
            "sizeBytes": 2,
            "metadata": {"provenance": {"mediaType": "application/json"}},
        }
    )
    repos.recipes.save({"recipeId": "recipe_mem", "projectId": "project_mem", "sourceJobId": "job_mem", "name": "Recipe"})

    assert repos.tool_calls.list_for_job("job_mem")[0]["toolId"] == "ml.basic_metrics"
    assert repos.artifacts.list_for_job("job_mem")[0]["storageKey"].endswith("metrics.json")
    assert repos.recipes.list_for_job("job_mem")[0]["recipeId"] == "recipe_mem"


def test_phase3_sqlalchemy_repository_schema_and_cursor():
    engine = create_engine("sqlite:///:memory:", future=True)
    metadata.create_all(engine)
    assert {
        "projects",
        "datasets",
        "data_profiles",
        "jobs",
        "job_events",
        "tool_calls",
        "artifacts",
        "visualization_recipes",
        "reports",
    }.issubset(PHASE3_TABLES)
    assert "CREATE TABLE IF NOT EXISTS reports" in PHASE3_MIGRATION_DRAFT_SQL

    repos = SqlAlchemyRepositoryBundle.create(engine)
    repos.projects.save({"id": "project_sql", "name": "SQL Project"})
    repos.datasets.save({"id": "dataset_sql", "projectId": "project_sql", "name": "SQL Dataset", "status": "profile_ready"})
    repos.jobs.save({"id": "job_sql", "projectId": "project_sql", "datasetId": "dataset_sql", "status": "created"})

    repos.job_events.append_event("job_sql", event_type="job.created", status="info", message="created")
    repos.job_events.append_event("job_sql", event_type="job.running", status="running", message="running", progress=0.5)
    assert [event.seq for event in repos.job_events.list_events_after_seq("job_sql", 1)] == [2]

    repos.tool_calls.save({"id": "call_sql", "jobId": "job_sql", "stepId": "step_1", "toolId": "ml.basic_metrics", "status": "completed"})
    artifact = repos.artifacts.save(
        {
            "id": "artifact_sql",
            "projectId": "project_sql",
            "datasetId": "dataset_sql",
            "jobId": "job_sql",
            "toolCallId": "call_sql",
            "type": "metrics_json",
            "name": "metrics.json",
            "storageKey": "projects/project_sql/jobs/job_sql/metrics.json",
            "contentHash": "def",
            "sha256": "def",
            "sizeBytes": 2,
            "contentType": "application/json",
            "metadata": {"provenance": {"mediaType": "application/json"}},
        }
    )
    recipe = repos.recipes.save({"recipeId": "recipe_sql", "projectId": "project_sql", "sourceJobId": "job_sql", "name": "SQL Recipe"})

    assert artifact["contentType"] == "application/json"
    assert recipe["sourceJobId"] == "job_sql"


def test_phase3_artifact_storage_local_and_s3_mapping(tmp_path):
    local = LocalFileArtifactStorage(tmp_path, public_base_url="/local-artifacts")
    content = b'{"ok":true}'
    metadata_record = local.put_bytes("projects/p/jobs/j/artifact.json", content, content_type="application/json")

    assert metadata_record.sha256 == hashlib.sha256(content).hexdigest()
    assert metadata_record.size_bytes == len(content)
    assert local.get_bytes(metadata_record.storage_key) == content
    assert local.signed_url(metadata_record.storage_key, content_type="application/json").url.endswith("/projects/p/jobs/j/artifact.json")
    with pytest.raises(ValueError):
        local.put_bytes("../escape.json", content, content_type="application/json")

    s3 = S3CompatibleArtifactStorage(bucket="mdi-artifacts", endpoint_url="http://minio:9000", prefix="phase3")
    mapped = s3.map_object(
        "projects/p/jobs/j/artifact.json",
        content_type="application/json",
        sha256=metadata_record.sha256,
        size_bytes=metadata_record.size_bytes,
    )
    signed = s3.signed_url("projects/p/jobs/j/artifact.json", content_type="application/json")

    assert mapped.backend == "s3"
    assert mapped.storage_key == "phase3/projects/p/jobs/j/artifact.json"
    assert signed.status == "not_implemented"
    assert signed.url == "s3://mdi-artifacts/phase3/projects/p/jobs/j/artifact.json"


def test_phase3_api_events_cursor_stream_download_and_phase2_regression(tmp_path, repo_root):
    reset_phase2_runtime(tmp_path / "artifacts")
    client = TestClient(create_app())

    project = client.post("/projects", json={"name": "Phase 3 Project"}).json()
    dataset = client.post(
        "/datasets/upload",
        json={
            "projectId": project["id"],
            "datasetName": "Phase 3 mixed dataset",
            "filePaths": [str(path) for path in _fixture_paths(repo_root)],
        },
    ).json()
    job = client.post(
        "/jobs",
        json={"projectId": project["id"], "datasetId": dataset["id"], "userPrompt": "Run Phase 3 smoke."},
    ).json()

    assert job["status"] == "completed"
    assert job["toolCallCount"] == len(PHASE2_TOOL_ORDER)
    assert client.get(f"/jobs/{job['id']}/tool-calls").json()[0]["toolId"] == PHASE2_TOOL_ORDER[0]

    events_after_two = client.get(f"/jobs/{job['id']}/events", params={"after_seq": 2}).json()
    assert events_after_two
    assert all(event["seq"] > 2 for event in events_after_two)

    with client.stream("GET", f"/jobs/{job['id']}/stream", params={"after_seq": 0}) as response:
        assert response.status_code == 200
        stream_text = "".join(response.iter_text())
    assert "event: job.created" in stream_text
    assert "event: job.completed" in stream_text

    artifacts = client.get(f"/jobs/{job['id']}/artifacts").json()
    report = next(artifact for artifact in artifacts if artifact["type"] == "report_md")
    download = client.get(f"/artifacts/{report['id']}/download").json()
    assert download["artifactId"] == report["id"]
    assert download["storageKey"] == report["storageKey"]
    assert download["contentType"] == "text/markdown"
    assert download["sha256"] == report["contentHash"]
    assert download["signedUrlStatus"] == "local"
