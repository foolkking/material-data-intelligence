from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from mdi_api import create_app
from mdi_api.artifact_storage import LocalFileArtifactStorage, S3CompatibleArtifactStorage
from mdi_api.db import PHASE3_TABLES, artifacts, job_events, metadata
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
    repos.projects.create({"id": "project_mem", "name": "Memory Project"})
    repos.datasets.create({"id": "dataset_mem", "projectId": "project_mem", "name": "Memory Dataset"})
    repos.data_profiles.create(
        {
            "profileId": "profile_mem",
            "datasetId": "dataset_mem",
            "version": "1",
            "datasetType": "mixed",
            "createdAt": "2026-06-26T00:00:00+00:00",
        }
    )
    repos.jobs.create({"id": "job_mem", "projectId": "project_mem", "datasetId": "dataset_mem", "status": "created"})

    first = repos.job_events.append_event("job_mem", event_type="job.created", status="info", message="created")
    second = repos.job_events.append_event("job_mem", event_type="job.running", status="running", message="running", progress=0.5)

    assert (first.seq, second.seq) == (1, 2)
    assert [event.seq for event in repos.job_events.list_events_after_seq("job_mem", 1)] == [2]
    assert repos.data_profiles.get_by_id("profile_mem")["datasetId"] == "dataset_mem"
    assert repos.data_profiles.list_by_project("project_mem")[0]["profileId"] == "profile_mem"
    assert repos.jobs.update_status("job_mem", "running")["status"] == "running"

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
    repos.reports.save(
        {
            "reportId": "report_mem",
            "projectId": "project_mem",
            "datasetId": "dataset_mem",
            "jobId": "job_mem",
            "title": "Memory Report",
            "markdownKey": "projects/project_mem/jobs/job_mem/report.md",
        }
    )

    assert repos.tool_calls.list_for_job("job_mem")[0]["toolId"] == "ml.basic_metrics"
    assert repos.artifacts.list_artifacts_by_job("job_mem")[0]["storageKey"].endswith("metrics.json")
    assert repos.recipes.list_for_job("job_mem")[0]["recipeId"] == "recipe_mem"
    assert repos.reports.list_for_job("job_mem")[0]["reportId"] == "report_mem"


def test_phase3_job_event_repository_concurrent_append_has_unique_seq():
    repos = InMemoryRepositoryBundle.create()

    def append(index: int):
        return repos.job_events.append_event(
            "job_concurrent",
            event_type="job.progress",
            status="running",
            message=f"event {index}",
            progress=index / 20,
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        events = list(executor.map(append, range(20)))

    assert sorted(event.seq for event in events) == list(range(1, 21))
    assert [event.seq for event in repos.job_events.list_events_after_seq("job_concurrent", 15)] == [16, 17, 18, 19, 20]


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
    assert {"job_id", "seq"}.issubset(job_events.columns.keys())
    assert {"storage_provider", "bucket", "storage_key", "content_type", "size_bytes", "sha256", "created_at"}.issubset(artifacts.columns.keys())
    index_names = {index.name for table_name in ("job_events", "jobs", "tool_calls", "artifacts") for index in metadata.tables[table_name].indexes}
    assert {"idx_job_events_job_seq", "idx_jobs_project_created", "idx_tool_calls_job", "idx_artifacts_job", "idx_artifacts_project_created"}.issubset(index_names)

    repos = SqlAlchemyRepositoryBundle.create(engine)
    repos.projects.save({"id": "project_sql", "name": "SQL Project"})
    repos.datasets.save({"id": "dataset_sql", "projectId": "project_sql", "name": "SQL Dataset", "status": "profile_ready"})
    profile = repos.data_profiles.save(
        {
            "profileId": "profile_sql",
            "datasetId": "dataset_sql",
            "version": "1",
            "datasetType": "mixed",
            "files": [],
            "objects": [],
            "createdAt": "2026-06-26T00:00:00+00:00",
        }
    )
    repos.jobs.save({"id": "job_sql", "projectId": "project_sql", "datasetId": "dataset_sql", "status": "created"})

    repos.job_events.append_event("job_sql", event_type="job.created", status="info", message="created")
    repos.job_events.append_event("job_sql", event_type="job.running", status="running", message="running", progress=0.5)
    assert [event.seq for event in repos.job_events.list_events_after_seq("job_sql", 1)] == [2]
    assert profile["profileId"] == "profile_sql"
    assert repos.data_profiles.list_by_project("project_sql")[0]["profileId"] == "profile_sql"

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
            "storageProvider": "s3",
            "bucket": "mdi-artifacts",
            "contentHash": "def",
            "sha256": "def",
            "sizeBytes": 2,
            "contentType": "application/json",
            "metadata": {"provenance": {"mediaType": "application/json"}},
        }
    )
    recipe = repos.recipes.save({"recipeId": "recipe_sql", "projectId": "project_sql", "sourceJobId": "job_sql", "name": "SQL Recipe"})
    report = repos.reports.save(
        {
            "reportId": "report_sql",
            "projectId": "project_sql",
            "datasetId": "dataset_sql",
            "jobId": "job_sql",
            "title": "SQL Report",
            "markdownKey": "projects/project_sql/jobs/job_sql/report.md",
            "htmlKey": "projects/project_sql/jobs/job_sql/report.html",
        }
    )

    assert artifact["contentType"] == "application/json"
    assert artifact["storageProvider"] == "s3"
    assert artifact["bucket"] == "mdi-artifacts"
    assert recipe["sourceJobId"] == "job_sql"
    assert report["reportId"] == "report_sql"
    assert repos.reports.list_by_project("project_sql")[0]["jobId"] == "job_sql"


def test_phase3_artifact_storage_local_and_s3_mapping(tmp_path):
    local = LocalFileArtifactStorage(tmp_path, public_base_url="/local-artifacts")
    content = b'{"ok":true}'
    metadata_record = local.put_bytes("projects/p/jobs/j/artifact.json", content, content_type="application/json")
    text_record = local.put_text("projects/p/jobs/j/readme.txt", "hello", content_type="text/plain")
    json_record = local.put_json("projects/p/jobs/j/data.json", {"ok": True})

    assert metadata_record.sha256 == hashlib.sha256(content).hexdigest()
    assert metadata_record.size_bytes == len(content)
    assert metadata_record.storage_provider == "local"
    assert metadata_record.created_at
    assert local.get_bytes(metadata_record.storage_key) == content
    assert local.get_text(text_record.storage_key) == "hello"
    assert local.get_json(json_record.storage_key) == {"ok": True}
    assert local.exists(metadata_record.storage_key)
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
    assert mapped.storage_provider == "s3"
    assert mapped.bucket == "mdi-artifacts"
    assert mapped.created_at
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
    first_data_line = next(line for line in stream_text.splitlines() if line.startswith("data: "))
    first_event = json.loads(first_data_line.removeprefix("data: "))
    assert {"job_id", "seq", "event_type", "status", "message", "progress", "payload", "created_at"}.issubset(first_event)

    artifacts = client.get(f"/jobs/{job['id']}/artifacts").json()
    report = next(artifact for artifact in artifacts if artifact["type"] == "report_md")
    download = client.get(f"/artifacts/{report['id']}/download").json()
    assert download["artifactId"] == report["id"]
    assert download["storageKey"] == report["storageKey"]
    assert download["contentType"] == "text/markdown"
    assert download["sha256"] == report["contentHash"]
    assert download["signedUrlStatus"] == "local"
