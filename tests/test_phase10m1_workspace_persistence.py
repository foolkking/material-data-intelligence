from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine

from mdi_api.db import metadata
from mdi_api.repositories import (
    InMemoryRepositoryBundle,
    SqlAlchemyRepositoryBundle,
    WorkspaceCapacityError,
    WorkspaceConflictError,
    WorkspaceScopeError,
)
from mdi_schemas import (
    ScientificWorkspace,
    WorkspaceLayoutState,
    WorkspacePanel,
    WorkspacePanelKind,
    WorkspacePanelLayout,
    WorkspacePanelPlacement,
    WorkspacePanelState,
    WorkspaceSourceKind,
    WorkspaceSourceRef,
    WorkspaceStatus,
    deterministic_panel_id,
    deterministic_workspace_id,
    make_layout_revision,
    workspace_semantic_hash,
)


NOW = datetime(2026, 8, 1, 8, 0, tzinfo=timezone.utc)


def _panel(workspace_id: str, index: int = 0) -> WorkspacePanel:
    source = WorkspaceSourceRef(
        kind=WorkspaceSourceKind.JOB,
        sourceId="job_1",
        projectId="project_1",
        jobId="job_1",
    )
    source_refs = [source.model_dump(mode="json")]
    payload: dict[str, Any] = {
        "schemaVersion": "1.0",
        "panelId": deterministic_panel_id(workspace_id, WorkspacePanelKind.OVERVIEW, f"job_1:{index}"),
        "workspaceId": workspace_id,
        "panelKind": "OVERVIEW",
        "title": f"Analysis overview {index}",
        "ordinal": min(index, 31),
        "visible": True,
        "sourceRefs": source_refs,
        "sourceReferenceHash": workspace_semantic_hash(source_refs),
        "rendererContract": "workspace.overview/1.0",
        "state": WorkspacePanelState.LOADING,
        "acceptedSelectionKinds": [],
        "emittedSelectionKinds": [],
        "evidenceRefs": [],
        "provenanceRefs": [],
        "capabilityRequirement": None,
        "layout": WorkspacePanelLayout(order=min(index, 31)).model_dump(mode="json"),
        "mobilePresentationMode": "STACKED",
        "accessibleName": f"Analysis overview {index}",
        "unsupportedReason": None,
        "panelStateHash": "0" * 64,
        "contractProvenance": "workspace-projection/1.0",
    }
    payload["panelStateHash"] = workspace_semantic_hash(
        {key: value for key, value in payload.items() if key != "panelStateHash"}
    )
    return WorkspacePanel.model_validate(payload)


def _aggregate(panel_count: int = 1) -> tuple[ScientificWorkspace, tuple[WorkspacePanel, ...], Any]:
    workspace_id = deterministic_workspace_id("project_1", "job_1")
    panels = tuple(_panel(workspace_id, index) for index in range(panel_count))
    panel_ids = tuple(panel.panelId for panel in panels)
    immutable = {
        "schemaVersion": "1.0",
        "workspaceId": workspace_id,
        "projectId": "project_1",
        "sourceJobId": "job_1",
        "datasetId": None,
        "datasetVersion": None,
        "profileId": None,
        "profileSemanticHash": None,
        "intentId": None,
        "intentSemanticHash": None,
        "planId": None,
        "planHash": None,
        "planSchemaVersion": None,
    }
    workspace = ScientificWorkspace(
        **immutable,
        sourceReferenceHash=workspace_semantic_hash(immutable),
        title="Workspace for job 1",
        activePanelId=panel_ids[0] if panel_ids else None,
        panelIds=panel_ids,
        currentLayoutRevision=0,
        revision=0,
        projectedStatus=WorkspaceStatus.INITIALIZING,
        createdByKind="USER",
        createdBy="user_local",
        createdAt=NOW,
        updatedAt=NOW,
    )
    layout = WorkspaceLayoutState(
        activePanelId=workspace.activePanelId,
        panelOrder=panel_ids,
        visiblePanelIds=panel_ids,
        panelLayouts=tuple(
            WorkspacePanelPlacement(panelId=panel.panelId, order=panel.ordinal)
            for panel in panels
        ),
    )
    revision = make_layout_revision(
        workspace_id=workspace_id,
        revision=0,
        layout=layout,
        selection=None,
        created_by="user_local",
        created_at=NOW,
    )
    return workspace, panels, revision


def _repositories(kind: str, tmp_path: Path) -> tuple[Any, Any | None]:
    if kind == "memory":
        repositories = InMemoryRepositoryBundle.create()
        engine = None
    else:
        engine = create_engine(f"sqlite:///{(tmp_path / 'workspace.sqlite3').as_posix()}")
        metadata.create_all(engine)
        repositories = SqlAlchemyRepositoryBundle.create(engine)
    repositories.projects.save({"projectId": "project_1", "name": "Project 1"})
    repositories.jobs.save(
        {
            "jobId": "job_1",
            "projectId": "project_1",
            "kind": "analysis",
            "status": "completed",
            "createdBy": "user_local",
        }
    )
    return repositories, engine


@pytest.mark.parametrize("kind", ["memory", "sql"])
def test_workspace_repository_idempotency_scope_and_round_trip(kind: str, tmp_path: Path) -> None:
    repositories, engine = _repositories(kind, tmp_path)
    workspace, panels, revision = _aggregate()
    first = repositories.workspaces.create_workspace(workspace, panels=panels, initial_layout=revision)
    second = repositories.workspaces.create_workspace(workspace, panels=panels, initial_layout=revision)
    assert first == second
    ScientificWorkspace.model_validate(first)
    assert repositories.workspaces.get_by_project_job("project_1", "job_1")["workspaceId"] == workspace.workspaceId
    stored_panels = repositories.workspaces.list_panels(workspace.workspaceId)
    assert [panel["panelId"] for panel in stored_panels] == [panels[0].panelId]
    assert [WorkspacePanel.model_validate(panel) for panel in stored_panels] == list(panels)
    assert repositories.workspaces.get_current_layout(workspace.workspaceId)["revision"] == 0
    with pytest.raises(WorkspaceScopeError, match="WORKSPACE_PROJECT_SCOPE_MISMATCH"):
        repositories.workspaces.get(workspace.workspaceId, project_id="project_foreign")
    if engine is not None:
        engine.dispose()


@pytest.mark.parametrize("kind", ["memory", "sql"])
def test_workspace_repository_optimistic_update_and_immutable_history(kind: str, tmp_path: Path) -> None:
    repositories, engine = _repositories(kind, tmp_path)
    workspace, panels, revision = _aggregate()
    repositories.workspaces.create_workspace(workspace, panels=panels, initial_layout=revision)
    updated = repositories.workspaces.update_workspace(
        workspace.workspaceId,
        expected_revision=0,
        project_id="project_1",
        title="Reviewed workspace",
        created_by="user_local",
    )
    assert updated["title"] == "Reviewed workspace"
    assert updated["revision"] == 1
    assert [item["revision"] for item in repositories.workspaces.list_layout_revisions(workspace.workspaceId)] == [0, 1]
    with pytest.raises(WorkspaceConflictError, match="WORKSPACE_REVISION_MISMATCH"):
        repositories.workspaces.update_workspace(
            workspace.workspaceId,
            expected_revision=0,
            title="Stale update",
            created_by="user_local",
        )
    assert repositories.workspaces.get(workspace.workspaceId)["sourceJobId"] == "job_1"
    if engine is not None:
        engine.dispose()


@pytest.mark.parametrize("kind", ["memory", "sql"])
def test_workspace_repository_panel_and_revision_caps(kind: str, tmp_path: Path) -> None:
    repositories, engine = _repositories(kind, tmp_path)
    workspace, panels, revision = _aggregate(panel_count=32)
    repositories.workspaces.create_workspace(workspace, panels=panels, initial_layout=revision)
    with pytest.raises(WorkspaceCapacityError, match="PANEL_CAP_EXCEEDED"):
        repositories.workspaces.save_panel(_panel(workspace.workspaceId, 32))

    for next_revision in range(1, 128):
        record = make_layout_revision(
            workspace_id=workspace.workspaceId,
            revision=next_revision,
            layout=revision.layout,
            selection=None,
            created_by="user_local",
            created_at=NOW + timedelta(seconds=next_revision),
        )
        repositories.workspaces.append_layout_revision(
            record,
            expected_revision=next_revision - 1,
            project_id="project_1",
        )
    overflow = make_layout_revision(
        workspace_id=workspace.workspaceId,
        revision=128,
        layout=revision.layout,
        selection=None,
        created_by="user_local",
        created_at=NOW + timedelta(seconds=128),
    )
    with pytest.raises(WorkspaceCapacityError, match="REVISION_CAP_EXCEEDED"):
        repositories.workspaces.append_layout_revision(
            overflow,
            expected_revision=127,
            project_id="project_1",
        )
    assert len(repositories.workspaces.list_layout_revisions(workspace.workspaceId)) == 128
    if engine is not None:
        engine.dispose()
