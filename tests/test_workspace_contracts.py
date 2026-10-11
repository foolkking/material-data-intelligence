from __future__ import annotations

from datetime import datetime, timezone
import base64
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from mdi_schemas import (
    ScientificWorkspace,
    WorkspaceDurableMetadata,
    WorkspaceLayoutRevision,
    WorkspaceLayoutState,
    WorkspacePanel,
    WorkspacePanelKind,
    WorkspacePanelLayout,
    WorkspacePanelPlacement,
    WorkspacePanelState,
    WorkspaceSelectionContext,
    WorkspaceSelectionKind,
    WorkspaceSelectionRef,
    WorkspaceSourceKind,
    WorkspaceSourceRef,
    WorkspaceWarning,
    WorkspaceStatus,
    decode_workspace_selection_url,
    deterministic_panel_id,
    deterministic_workspace_id,
    encode_workspace_selection_url,
    make_layout_revision,
    strict_workspace_json_loads,
    workspace_semantic_hash,
)


SHA = "a" * 64
NOW = datetime(2026, 8, 1, tzinfo=timezone.utc)


def test_trajectory_atom_keeps_exact_frame_in_navigation_roundtrip() -> None:
    selection = WorkspaceSelectionContext.model_validate({
        "schemaVersion": "1.0", "sourceScopeHash": SHA,
        "primary": {"kind": "TRAJECTORY_ATOM", "sourceScopeHash": SHA,
                    "projectId": "project_1", "datasetId": "dataset_1", "datasetVersion": "version_1",
                    "trajectoryId": "trajectory_1", "atomId": "atom:1:1.0.1", "frameId": "frame:5",
                    "artifactId": "source:trajectory_1", "artifactChecksum": SHA},
        "secondary": [], "propagation": "EXACT_COMPATIBLE_ONLY", "compatibility": "EXACT", "cleared": False,
    })
    restored = decode_workspace_selection_url(encode_workspace_selection_url(selection))
    assert restored.primary.frameId == "frame:5"
    assert restored.primary.atomId == "atom:1:1.0.1"


def _selection_ref(**overrides: object) -> WorkspaceSelectionRef:
    payload: dict[str, object] = {
        "kind": "ARTIFACT",
        "sourceScopeHash": SHA,
        "projectId": "project_1",
        "jobId": "job_1",
        "artifactId": "artifact_1",
        "artifactChecksum": SHA,
        "artifactContract": "table-json",
        "artifactVersion": "1.0",
    }
    payload.update(overrides)
    return WorkspaceSelectionRef.model_validate(payload)


def _panel(workspace_id: str = "workspace_1") -> WorkspacePanel:
    source = WorkspaceSourceRef(
        kind=WorkspaceSourceKind.JOB,
        sourceId="job_1",
        projectId="project_1",
        jobId="job_1",
    )
    source_hash = workspace_semantic_hash([source.model_dump(mode="json")])
    payload = {
        "schemaVersion": "1.0",
        "panelId": deterministic_panel_id(workspace_id, WorkspacePanelKind.OVERVIEW, "job_1"),
        "workspaceId": workspace_id,
        "panelKind": WorkspacePanelKind.OVERVIEW,
        "title": "Analysis overview",
        "ordinal": 0,
        "visible": True,
        "sourceRefs": [source.model_dump(mode="json")],
        "sourceReferenceHash": source_hash,
        "rendererContract": "workspace.overview/1.0",
        "state": WorkspacePanelState.PRODUCED,
        "acceptedSelectionKinds": [],
        "emittedSelectionKinds": [],
        "evidenceRefs": [],
        "provenanceRefs": [],
        "capabilityRequirement": None,
        "layout": WorkspacePanelLayout(order=0).model_dump(mode="json"),
        "mobilePresentationMode": "STACKED",
        "accessibleName": "Analysis overview",
        "unsupportedReason": None,
        "panelStateHash": "0" * 64,
        "contractProvenance": "workspace-projection/1.0",
    }
    payload["panelStateHash"] = workspace_semantic_hash({key: value for key, value in payload.items() if key != "panelStateHash"})
    return WorkspacePanel.model_validate(payload)


def _workspace(panel_ids: tuple[str, ...] = ()) -> ScientificWorkspace:
    immutable = {
        "schemaVersion": "1.0",
        "workspaceId": deterministic_workspace_id("project_1", "job_1"),
        "projectId": "project_1",
        "sourceJobId": "job_1",
        "datasetId": "dataset_1",
        "datasetVersion": "v1",
        "profileId": "profile_1",
        "profileSemanticHash": SHA,
        "intentId": "intent_1",
        "intentSemanticHash": SHA,
        "planId": "plan_1",
        "planHash": SHA,
        "planSchemaVersion": "0.2",
    }
    return ScientificWorkspace(
        **immutable,
        sourceReferenceHash=workspace_semantic_hash(immutable),
        title="Workspace for job 1",
        activePanelId=panel_ids[0] if panel_ids else None,
        panelIds=panel_ids,
        currentLayoutRevision=0,
        revision=0,
        projectedStatus=WorkspaceStatus.COMPLETE,
        createdByKind="USER",
        createdBy="user_local",
        createdAt=NOW,
        updatedAt=NOW,
    )


def test_workspace_identity_and_hashes_are_deterministic() -> None:
    first = deterministic_workspace_id("project_1", "job_1")
    assert first == deterministic_workspace_id("project_1", "job_1")
    assert first != deterministic_workspace_id("project_1", "job_2")
    workspace = _workspace()
    assert ScientificWorkspace.model_validate_json(workspace.model_dump_json()) == workspace


def test_workspace_contract_rejects_unknown_fields_and_bad_source_hash() -> None:
    payload = _workspace().model_dump(mode="json")
    payload["toolId"] = "arbitrary.tool"
    with pytest.raises(ValidationError):
        ScientificWorkspace.model_validate(payload)
    payload.pop("toolId")
    payload["sourceReferenceHash"] = "b" * 64
    with pytest.raises(ValidationError, match="sourceReferenceHash"):
        ScientificWorkspace.model_validate(payload)


def test_strict_loader_rejects_duplicates_depth_and_non_finite() -> None:
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        strict_workspace_json_loads('{"schemaVersion":"1.0","schemaVersion":"1.0"}')
    with pytest.raises(ValueError, match="Forbidden JSON key"):
        strict_workspace_json_loads('{"__proto__":{}}')
    with pytest.raises(ValueError, match="Non-finite"):
        strict_workspace_json_loads('{"value":NaN}')
    deep: object = "leaf"
    for _ in range(16):
        deep = {"nested": deep}
    with pytest.raises(ValueError, match="depth"):
        strict_workspace_json_loads(json.dumps(deep))


def test_selection_contract_enforces_exact_kind_fields_and_url_round_trip() -> None:
    artifact = _selection_ref()
    context = WorkspaceSelectionContext(sourceScopeHash=SHA, primary=artifact)
    token = encode_workspace_selection_url(context)
    assert decode_workspace_selection_url(token) == context
    with pytest.raises(ValidationError, match="missing required fields"):
        WorkspaceSelectionRef(
            kind=WorkspaceSelectionKind.PHONON_Q_POINT,
            sourceScopeHash=SHA,
            projectId="project_1",
            datasetId="dataset_1",
            datasetVersion="v1",
            phononArtifactId="artifact_1",
            artifactChecksum=SHA,
        )
    with pytest.raises(ValidationError, match="forbidden fields"):
        WorkspaceSelectionRef.model_validate(
            {**artifact.model_dump(mode="json"), "structureId": "guessed-by-label"}
        )


@pytest.mark.parametrize("channel", ["total", "projection:0", "projection:1"])
def test_phonon_dos_selection_has_exact_frequency_and_channel(channel: str) -> None:
    ref = WorkspaceSelectionRef(
        kind=WorkspaceSelectionKind.PHONON_DOS_POINT, sourceScopeHash=SHA,
        projectId="project_1", datasetId="dataset_1", datasetVersion="version_1",
        phononArtifactId="source:dos_1", artifactChecksum=SHA,
        frequencyPointId="frequency:600", dosChannelId=channel,
    )
    context = WorkspaceSelectionContext(sourceScopeHash=SHA, primary=ref)
    token = encode_workspace_selection_url(context)
    assert len(token) <= 2048
    assert decode_workspace_selection_url(token) == context
    payload = ref.model_dump(mode="json")
    for field in ("frequencyPointId", "dosChannelId"):
        with pytest.raises(ValidationError, match="missing required fields"):
            WorkspaceSelectionRef.model_validate({**payload, field: None})
    for field in ("qPointId", "energyPointId", "branchId"):
        with pytest.raises(ValidationError, match="forbidden fields"):
            WorkspaceSelectionRef.model_validate({**payload, field: "foreign:1"})


def test_selection_url_compacts_real_structure_identity_and_keeps_legacy_tokens() -> None:
    dataset_id = "dataset_0002_7d84dd2fe2424b9c"
    site = WorkspaceSelectionRef(
        kind=WorkspaceSelectionKind.PERIODIC_SITE, sourceScopeHash=SHA,
        projectId="project_0001_d280978e0f6c432c", datasetId=dataset_id,
        datasetVersion=SHA, objectId=f"{dataset_id}:obj_structure_6d93a281007b",
        structureId=SHA, siteId="Li-0:0.0.0",
    )
    context = WorkspaceSelectionContext(sourceScopeHash=SHA, primary=site)
    token = encode_workspace_selection_url(context)
    assert len(token) <= 2048
    assert decode_workspace_selection_url(token) == context
    decoded = json.loads(base64.urlsafe_b64decode(token + "=" * (-len(token) % 4)))
    assert all(value is not None for value in decoded["primary"].values())

    legacy_context = WorkspaceSelectionContext(sourceScopeHash=SHA, primary=_selection_ref())
    legacy = legacy_context.model_dump(mode="json")
    for field in ("electronicResourceId", "spinChannelId", "kpointId", "bandId", "bandStateId", "bandEdgeId", "dosChannelId", "projectionId", "energyPointId"):
        legacy["primary"].pop(field, None)
    raw = json.dumps(legacy, sort_keys=True, separators=(",", ":"))
    legacy_token = base64.urlsafe_b64encode(raw.encode()).rstrip(b"=").decode()
    assert decode_workspace_selection_url(legacy_token) == legacy_context
    pretty = base64.urlsafe_b64encode(json.dumps(legacy, indent=2).encode()).rstrip(b"=").decode()
    with pytest.raises(ValueError):
        decode_workspace_selection_url(pretty)


def test_selection_contract_accepts_durable_dataset_sample_reference() -> None:
    selection = WorkspaceSelectionRef(
        kind=WorkspaceSelectionKind.DATASET_SAMPLE,
        sourceScopeHash=SHA,
        projectId="project_1",
        datasetId="dataset_0001",
        datasetVersion="2",
        objectId="obj_dataframe_1f4ba55e6e625275",
        sampleRef="dataset_0001@2:1f4ba55e6e625275:0",
    )
    assert selection.sampleRef == "dataset_0001@2:1f4ba55e6e625275:0"


def test_selection_multi_scope_and_duplicate_rules() -> None:
    primary = _selection_ref(artifactId="artifact_1")
    secondary = _selection_ref(artifactId="artifact_2")
    context = WorkspaceSelectionContext(sourceScopeHash=SHA, primary=primary, secondary=(secondary,))
    assert len(context.secondary) == 1
    with pytest.raises(ValidationError, match="duplicate identities"):
        WorkspaceSelectionContext(sourceScopeHash=SHA, primary=primary, secondary=(primary,))
    with pytest.raises(ValidationError, match="one resource version"):
        WorkspaceSelectionContext(
            sourceScopeHash=SHA,
            primary=WorkspaceSelectionRef(
                kind="MATERIAL_OBJECT",
                sourceScopeHash=SHA,
                projectId="project_1",
                datasetId="dataset_1",
                datasetVersion="v1",
                objectId="object_1",
            ),
            secondary=(
                WorkspaceSelectionRef(
                    kind="MATERIAL_OBJECT",
                    sourceScopeHash=SHA,
                    projectId="project_1",
                    datasetId="dataset_1",
                    datasetVersion="v2",
                    objectId="object_2",
                ),
            ),
        )


def test_panel_hash_renderer_allowlist_and_source_scope() -> None:
    panel = _panel()
    assert WorkspacePanel.model_validate_json(panel.model_dump_json()) == panel
    payload = panel.model_dump(mode="json")
    payload["rendererContract"] = "arbitrary.module/1.0"
    payload["panelStateHash"] = workspace_semantic_hash({key: value for key, value in payload.items() if key != "panelStateHash"})
    with pytest.raises(ValidationError, match="allowlisted"):
        WorkspacePanel.model_validate(payload)
    payload = panel.model_dump(mode="json")
    payload["sourceReferenceHash"] = "b" * 64
    payload["panelStateHash"] = workspace_semantic_hash({key: value for key, value in payload.items() if key != "panelStateHash"})
    with pytest.raises(ValidationError, match="sourceReferenceHash"):
        WorkspacePanel.model_validate(payload)


def test_layout_uses_panel_identity_and_revision_129_is_rejected() -> None:
    panel_ids = ("panel_1", "panel_2")
    layout = WorkspaceLayoutState(
        activePanelId="panel_1",
        panelOrder=panel_ids,
        visiblePanelIds=panel_ids,
        panelLayouts=(
            WorkspacePanelPlacement(panelId="panel_1", order=0),
            WorkspacePanelPlacement(panelId="panel_2", order=1),
        ),
    )
    revision = make_layout_revision(
        workspace_id="workspace_1",
        revision=128,
        layout=layout,
        selection=None,
        created_by="user_local",
        created_at=NOW,
    )
    assert revision.revision == 128
    with pytest.raises(ValidationError):
        make_layout_revision(
            workspace_id="workspace_1",
            revision=129,
            layout=layout,
            selection=None,
            created_by="user_local",
            created_at=NOW,
        )
    with pytest.raises(ValidationError, match="exact panelOrder identities"):
        WorkspaceLayoutState(
            panelOrder=panel_ids,
            panelLayouts=(
                WorkspacePanelPlacement(panelId="panel_1", order=0),
                WorkspacePanelPlacement(panelId="panel_3", order=1),
            ),
        )


def test_workspace_panel_cap_and_executable_text_rejection() -> None:
    workspace_id = deterministic_workspace_id("project_1", "job_1")
    valid_ids = tuple(f"panel_{index}" for index in range(32))
    assert len(_workspace(valid_ids).panelIds) == 32
    with pytest.raises(ValidationError):
        _workspace(valid_ids + ("panel_32",))
    payload = _workspace().model_dump(mode="json")
    payload["title"] = '<script src="https://example.invalid/x.js"></script>'
    with pytest.raises(ValidationError, match="executable"):
        ScientificWorkspace.model_validate(payload)
    assert workspace_id.startswith("workspace_")


def test_checked_json_schema_and_typescript_contract_parity() -> None:
    manifest = json.loads(Path("packages/schemas/json/workspace-v1.schema.json").read_text(encoding="utf-8"))
    expected = {
        "scientificWorkspace": ScientificWorkspace,
        "workspaceDurableMetadata": WorkspaceDurableMetadata,
        "workspaceLayoutRevision": WorkspaceLayoutRevision,
        "workspaceLayoutState": WorkspaceLayoutState,
        "workspacePanel": WorkspacePanel,
        "workspacePanelLayout": WorkspacePanelLayout,
        "workspacePanelPlacement": WorkspacePanelPlacement,
        "workspaceSelectionContext": WorkspaceSelectionContext,
        "workspaceSelectionRef": WorkspaceSelectionRef,
        "workspaceSourceRef": WorkspaceSourceRef,
        "workspaceWarning": WorkspaceWarning,
    }
    assert set(manifest) == set(expected)
    for key, model in expected.items():
        assert manifest[key] == model.model_json_schema()
        _assert_object_schemas_forbid_unknown_fields(manifest[key])
    typescript = Path("packages/schemas/src/index.ts").read_text(encoding="utf-8")
    workspace_types = typescript[typescript.index("export const WORKSPACE_SCHEMA_VERSION") :]
    for type_name in (
        "ScientificWorkspace",
        "WorkspacePanel",
        "WorkspaceSelectionContext",
        "WorkspaceLayoutRevision",
        "WorkspacePanelPlacement",
    ):
        assert f"export type {type_name}" in workspace_types
    assert ": any" not in workspace_types


def _assert_object_schemas_forbid_unknown_fields(value: object) -> None:
    if isinstance(value, dict):
        if value.get("type") == "object":
            assert value.get("additionalProperties") is False
        for child in value.values():
            _assert_object_schemas_forbid_unknown_fields(child)
    elif isinstance(value, list):
        for child in value:
            _assert_object_schemas_forbid_unknown_fields(child)
