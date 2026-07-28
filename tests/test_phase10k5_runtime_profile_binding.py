from __future__ import annotations

from pathlib import Path

from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_schemas import DataProfile
from mdi_workers import QueueToolExecution, QueueWorkerRuntime


def test_runtime_rejects_profile_from_another_dataset_before_tool_execution(tmp_path: Path) -> None:
    repos = _repositories()
    called = False

    def executor(request, context) -> QueueToolExecution:
        nonlocal called
        called = True
        return QueueToolExecution(artifacts=[])

    runtime = QueueWorkerRuntime(repositories=repos, tool_executor=executor, artifact_root=tmp_path)
    result = runtime.handle_job(
        "job_k5_binding",
        plan=_plan(),
        object_store={"profile": _profile("dataset_other", "profile_k5")},
    )

    assert result.status == "failed"
    assert called is False
    assert "does not match the persisted AnalysisPlan binding" in result.message


def test_runtime_rejects_wrong_profile_revision_before_tool_execution(tmp_path: Path) -> None:
    repos = _repositories()
    runtime = QueueWorkerRuntime(
        repositories=repos,
        tool_executor=lambda request, context: QueueToolExecution(artifacts=[]),
        artifact_root=tmp_path,
    )

    result = runtime.handle_job(
        "job_k5_binding",
        plan=_plan(),
        object_store={"profile": _profile("dataset_k5", "profile_stale")},
    )

    assert result.status == "failed"
    assert "does not match the persisted AnalysisPlan binding" in result.message


def _repositories() -> InMemoryRepositoryBundle:
    repos = InMemoryRepositoryBundle.create()
    repos.projects.save({"id": "project_k5", "name": "K5"})
    repos.datasets.save({"id": "dataset_k5", "projectId": "project_k5", "name": "K5"})
    repos.jobs.save({"id": "job_k5_binding", "projectId": "project_k5", "datasetId": "dataset_k5", "status": "created"})
    return repos


def _plan() -> dict[str, object]:
    return {
        "schemaVersion": "0.1",
        "goal": "verify exact profile binding",
        "datasetId": "dataset_k5",
        "profileId": "profile_k5",
        "toolRegistryVersion": "0.1.0",
        "steps": [
            {
                "stepId": "step_binding",
                "toolId": "dataset.materials_explorer",
                "purpose": "verify binding",
                "reason": "integration evidence",
                "inputRefs": [],
                "params": {},
                "output": {"artifactTypes": []},
            }
        ],
        "expectedArtifacts": [],
    }


def _profile(dataset_id: str, profile_id: str) -> DataProfile:
    return DataProfile.model_validate(
        {
            "schemaVersion": "0.1",
            "profileId": profile_id,
            "datasetId": dataset_id,
            "version": "2",
            "datasetType": "table",
            "files": [],
            "objects": [],
            "qualityIssues": [],
            "recommendedTasks": [],
            "profileContractVersion": "2.0",
            "semanticRulesVersion": "phase10k1.semantic_roles.v1",
            "semanticHash": "a" * 64,
            "semanticColumns": [],
            "semanticGroups": [],
            "resourceSemantics": [],
            "analysisReadiness": [],
            "createdAt": "2026-07-28T00:00:00Z",
        }
    )
