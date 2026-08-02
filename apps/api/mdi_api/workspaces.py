from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from mdi_schemas.workspace import (
    WORKSPACE_MAX_LAYOUT_REVISIONS,
    WORKSPACE_MAX_PANELS,
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
    WorkspaceSourceKind,
    WorkspaceSourceRef,
    WorkspaceStatus,
    WorkspaceWarning,
    deterministic_panel_id,
    deterministic_workspace_id,
    make_layout_revision,
    workspace_semantic_hash,
)


_DATA_SELECTION_KINDS = (
    WorkspaceSelectionKind.DATASET_SAMPLE,
    WorkspaceSelectionKind.MATERIAL_OBJECT,
    WorkspaceSelectionKind.STRUCTURE,
    WorkspaceSelectionKind.PERIODIC_SITE,
    WorkspaceSelectionKind.TRAJECTORY_ATOM,
    WorkspaceSelectionKind.TRAJECTORY_FRAME,
)
_ARTIFACT_DERIVED_SELECTION_KINDS = (
    WorkspaceSelectionKind.PHONON_Q_POINT,
    WorkspaceSelectionKind.PHONON_BRANCH,
    WorkspaceSelectionKind.RECIPROCAL_POINT,
    WorkspaceSelectionKind.VOLUMETRIC_FIELD,
    WorkspaceSelectionKind.ARTIFACT,
)
_EVIDENCE_SELECTION_KINDS = (
    WorkspaceSelectionKind.EVIDENCE_ITEM,
    WorkspaceSelectionKind.CLAIM,
)
_ALL_SELECTION_KINDS = (
    *_DATA_SELECTION_KINDS,
    *_ARTIFACT_DERIVED_SELECTION_KINDS,
    *_EVIDENCE_SELECTION_KINDS,
)

_PANEL_SELECTION_DECLARATIONS: dict[
    str, tuple[tuple[WorkspaceSelectionKind, ...], tuple[WorkspaceSelectionKind, ...]]
] = {
    "workspace.overview/1.0": (_ALL_SELECTION_KINDS, ()),
    "workspace.data/1.0": (_DATA_SELECTION_KINDS, ()),
    "workspace.plan/1.0": ((), ()),
    "workspace.execution/1.0": ((WorkspaceSelectionKind.ARTIFACT,), ()),
    "workspace.artifact-metadata/1.0": (
        (*_DATA_SELECTION_KINDS, *_ARTIFACT_DERIVED_SELECTION_KINDS),
        (
            WorkspaceSelectionKind.DATASET_SAMPLE,
            WorkspaceSelectionKind.MATERIAL_OBJECT,
            WorkspaceSelectionKind.ARTIFACT,
        ),
    ),
    "workspace.findings/1.0": (
        (*_ARTIFACT_DERIVED_SELECTION_KINDS, *_EVIDENCE_SELECTION_KINDS),
        (),
    ),
    "workspace.evidence/1.0": (
        (*_ARTIFACT_DERIVED_SELECTION_KINDS, *_EVIDENCE_SELECTION_KINDS),
        (),
    ),
    "workspace.provenance/1.0": (_ALL_SELECTION_KINDS, ()),
    "workspace.report/1.0": (
        (WorkspaceSelectionKind.ARTIFACT, *_EVIDENCE_SELECTION_KINDS),
        (),
    ),
    "workspace.inert-fallback/1.0": ((), ()),
}


@dataclass(frozen=True)
class WorkspaceDomainError(Exception):
    code: str
    message: str
    status_code: int = 400
    retryable: bool = False

    def as_detail(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }


@dataclass(frozen=True)
class WorkspaceSnapshot:
    body: dict[str, Any]
    etag: str


@dataclass(frozen=True)
class _SourceProjection:
    project: Mapping[str, Any] | None
    job: Mapping[str, Any] | None
    dataset: Mapping[str, Any] | None
    profile: Mapping[str, Any] | None
    intent: Mapping[str, Any] | None
    eligibility_resolution: Mapping[str, Any] | None
    selection_decision: Mapping[str, Any] | None
    plan_record: Mapping[str, Any] | None
    plan: Mapping[str, Any] | None
    dependency_execution: Mapping[str, Any] | None
    tool_calls: tuple[Mapping[str, Any], ...]
    artifacts: tuple[Mapping[str, Any], ...]
    interpretations: tuple[Mapping[str, Any], ...]
    reports: tuple[Mapping[str, Any], ...]
    recipes: tuple[Mapping[str, Any], ...]
    status: WorkspaceStatus
    read_only: bool
    historical: bool
    warnings: tuple[WorkspaceWarning, ...]

    @property
    def plan_schema_version(self) -> str | None:
        if self.plan is None:
            return None
        value = self.plan.get("schemaVersion")
        return str(value) if value is not None else None

    @property
    def dependency_outcome(self) -> str | None:
        record = self.dependency_execution
        if not record:
            return None
        value = record.get("overallOutcome") or record.get("outcome")
        return str(value) if value is not None else None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        current = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return current.astimezone(timezone.utc).isoformat()
    return str(value)


def _record(value: Any) -> Mapping[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, Mapping):
        return value
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return model_dump(mode="json", by_alias=True)
    raise WorkspaceDomainError(
        "SOURCE_RECORD_INVALID",
        "A source repository returned an invalid record.",
        409,
    )


def _records(value: Any) -> tuple[Mapping[str, Any], ...]:
    if value is None:
        return ()
    return tuple(item for raw in value if (item := _record(raw)) is not None)


def _repo_get(repository: Any, key: str) -> Mapping[str, Any] | None:
    if repository is None:
        return None
    try:
        return _record(repository.get(key))
    except (KeyError, LookupError):
        return None


def _repo_list(repository: Any, method: str, key: str) -> tuple[Mapping[str, Any], ...]:
    if repository is None:
        return ()
    function = getattr(repository, method, None)
    if not callable(function):
        return ()
    try:
        return _records(function(key))
    except (KeyError, LookupError):
        return ()


def _identity(record: Mapping[str, Any] | None, *keys: str) -> str | None:
    if record is None:
        return None
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return str(value)
    return None


def _source_hash(record: Mapping[str, Any] | None, *keys: str) -> str | None:
    value = _identity(record, *keys)
    if value is None:
        return None
    lowered = value.lower()
    if len(lowered) == 64 and all(character in "0123456789abcdef" for character in lowered):
        return lowered
    return None


def _profile_dataset_version(profile: Mapping[str, Any] | None) -> str | None:
    direct = _identity(profile, "datasetVersion", "dataset_version")
    if direct is not None:
        return direct
    sample_identity = _record(profile.get("sampleIdentity")) if profile else None
    return _identity(sample_identity, "datasetVersion", "dataset_version")


def _contract_token(value: Any, fallback: str) -> str:
    text = str(value or fallback).strip()
    if not text:
        return fallback
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._/-")
    if text[0].isalnum() and all(character in allowed for character in text):
        return text[:128]
    return fallback


def _semantic_hash(value: Mapping[str, Any]) -> str:
    return workspace_semantic_hash(value)


class WorkspaceProjectionService:
    """Metadata-only Workspace projection over the existing repository bundle."""

    def __init__(self, repositories: Any) -> None:
        if not hasattr(repositories, "workspaces"):
            raise WorkspaceDomainError(
                "WORKSPACE_REPOSITORY_UNAVAILABLE",
                "Workspace persistence is unavailable.",
                503,
                True,
            )
        self.repositories = repositories

    def get_project(self, project_id: str) -> Mapping[str, Any]:
        project = _repo_get(getattr(self.repositories, "projects", None), project_id)
        if project is None:
            raise WorkspaceDomainError("PROJECT_NOT_FOUND", "Project not found.", 404)
        return project

    def get_job(self, job_id: str) -> Mapping[str, Any]:
        job = _repo_get(getattr(self.repositories, "jobs", None), job_id)
        if job is None:
            raise WorkspaceDomainError("JOB_NOT_FOUND", "Analysis job not found.", 404)
        return job

    def get_stored_workspace(self, workspace_id: str) -> ScientificWorkspace:
        try:
            value = self.repositories.workspaces.get(workspace_id)
        except (KeyError, LookupError):
            value = None
        if value is None:
            raise WorkspaceDomainError("WORKSPACE_NOT_FOUND", "Workspace not found.", 404)
        try:
            return ScientificWorkspace.model_validate(value)
        except Exception as exc:
            raise WorkspaceDomainError(
                "WORKSPACE_RECORD_INVALID",
                "The persisted Workspace record failed contract validation.",
                409,
            ) from exc

    def project_job(
        self,
        *,
        source_job_id: str,
        created_by: str,
        title: str | None = None,
    ) -> tuple[WorkspaceSnapshot, bool]:
        job = self.get_job(source_job_id)
        project_id = _identity(job, "projectId", "project_id")
        if project_id is None:
            raise WorkspaceDomainError(
                "JOB_PROJECT_MISSING",
                "The source job has no exact Project identity.",
                409,
            )
        self.get_project(project_id)

        try:
            existing = self.repositories.workspaces.get_by_project_job(
                project_id, source_job_id
            )
        except (KeyError, LookupError):
            existing = None
        if existing is not None:
            workspace = ScientificWorkspace.model_validate(existing)
            if title is not None and title.strip() != workspace.title:
                raise WorkspaceDomainError(
                    "WORKSPACE_CREATE_CONFLICT",
                    "A Workspace already exists for this Project and Job with different creation metadata.",
                    409,
                )
            return self.get_snapshot(workspace.workspaceId), False

        source = self._collect_source(source_job_id, allow_missing_job=False)
        workspace_id = deterministic_workspace_id(project_id, source_job_id)
        panels = self._build_panels(workspace_id, project_id, source_job_id, source)
        if len(panels) > WORKSPACE_MAX_PANELS:
            raise WorkspaceDomainError(
                "PANEL_CAP_EXCEEDED",
                f"Workspace projection exceeds the {WORKSPACE_MAX_PANELS}-panel cap.",
                422,
            )

        profile = source.profile
        intent = source.intent
        plan_record = source.plan_record
        dataset_id = _identity(source.job, "datasetId", "dataset_id")
        dataset_version = _profile_dataset_version(profile)
        profile_id = _identity(profile, "profileId", "profile_id")
        profile_hash = _source_hash(profile, "semanticHash", "semantic_hash")
        intent_id = _identity(intent, "intentId", "intent_id")
        intent_hash = _source_hash(
            intent, "intentHash", "semanticHash", "semantic_hash"
        )
        plan_id = (
            _identity(plan_record, "planId", "analysisPlanId", "id")
            or _identity(source.job, "planId", "plan_id")
        )
        plan_hash = _source_hash(
            plan_record, "planHash", "semanticHash", "semantic_hash"
        )
        immutable_sources = {
            "schemaVersion": "1.0",
            "workspaceId": workspace_id,
            "projectId": project_id,
            "sourceJobId": source_job_id,
            "datasetId": dataset_id,
            "datasetVersion": dataset_version,
            "profileId": profile_id,
            "profileSemanticHash": profile_hash,
            "intentId": intent_id,
            "intentSemanticHash": intent_hash,
            "planId": plan_id,
            "planHash": plan_hash,
            "planSchemaVersion": source.plan_schema_version,
        }
        source_reference_hash = _semantic_hash(immutable_sources)
        now = _utc_now()
        initial_layout = WorkspaceLayoutState(
            activePanelId=panels[0].panelId if panels else None,
            panelOrder=tuple(panel.panelId for panel in panels),
            visiblePanelIds=tuple(panel.panelId for panel in panels if panel.visible),
            panelLayouts=tuple(
                WorkspacePanelPlacement(
                    panelId=panel.panelId,
                    region=panel.layout.region,
                    order=panel.layout.order,
                    width=panel.layout.width,
                    height=panel.layout.height,
                    collapsed=panel.layout.collapsed,
                )
                for panel in panels
            ),
            durableMetadata=WorkspaceDurableMetadata(),
        )
        initial_revision = make_layout_revision(
            workspace_id=workspace_id,
            revision=0,
            layout=initial_layout,
            selection=None,
            created_by=created_by,
            created_at=now,
        )

        try:
            record = ScientificWorkspace(
                workspaceId=workspace_id,
                projectId=project_id,
                sourceJobId=source_job_id,
                sourceReferenceHash=source_reference_hash,
                datasetId=dataset_id,
                datasetVersion=dataset_version,
                profileId=profile_id,
                profileSemanticHash=profile_hash,
                intentId=intent_id,
                intentSemanticHash=intent_hash,
                planId=plan_id,
                planHash=plan_hash,
                planSchemaVersion=source.plan_schema_version,
                title=(title or "Scientific analysis workspace").strip(),
                activePanelId=initial_layout.activePanelId,
                panelIds=tuple(panel.panelId for panel in panels),
                currentLayoutRevision=0,
                revision=0,
                projectedStatus=source.status,
                historicalProjection=source.historical,
                readOnly=source.read_only,
                warnings=source.warnings,
                diagnostics=(),
                artifactCount=len(source.artifacts),
                toolCallCount=len(source.tool_calls),
                interpretationCount=len(source.interpretations),
                reportCount=len(source.reports),
                recipeCount=len(source.recipes),
                createdByKind="USER",
                createdBy=created_by,
                createdAt=now,
                updatedAt=now,
            )
        except Exception as exc:
            raise WorkspaceDomainError(
                "WORKSPACE_CONTRACT_INVALID",
                "Workspace creation metadata failed strict contract validation.",
                422,
            ) from exc

        try:
            persisted = self.repositories.workspaces.create_workspace(
                record.model_dump(mode="json", by_alias=True),
                panels=tuple(
                    panel.model_dump(mode="json", by_alias=True) for panel in panels
                ),
                initial_layout=initial_revision.model_dump(
                    mode="json", by_alias=True
                ),
            )
        except Exception as exc:
            try:
                concurrent = self.repositories.workspaces.get_by_project_job(
                    project_id, source_job_id
                )
            except (KeyError, LookupError):
                concurrent = None
            if concurrent is None:
                raise self._translate_repository_error(exc) from exc
            persisted = concurrent

        persisted_workspace = ScientificWorkspace.model_validate(persisted or record)
        return self.get_snapshot(persisted_workspace.workspaceId), True

    def get_snapshot(self, workspace_id: str) -> WorkspaceSnapshot:
        stored = self.get_stored_workspace(workspace_id)
        source = self._collect_source(
            stored.sourceJobId,
            allow_missing_job=True,
            fallback_project_id=stored.projectId,
        )
        workspace_payload = stored.model_dump(mode="json", by_alias=True)
        workspace_payload.update(
            {
                "projectedStatus": source.status.value,
                "readOnly": bool(stored.readOnly or source.read_only),
                "historicalProjection": bool(stored.historicalProjection or source.historical),
                "warnings": [
                    warning.model_dump(mode="json", by_alias=True)
                    for warning in self._merge_warnings(stored.warnings, source.warnings)
                ],
                "artifactCount": len(source.artifacts),
                "toolCallCount": len(source.tool_calls),
                "interpretationCount": len(source.interpretations),
                "reportCount": len(source.reports),
                "recipeCount": len(source.recipes),
            }
        )
        projected_workspace = ScientificWorkspace.model_validate(workspace_payload)
        panels = self._project_current_panels(
            self._load_panels(workspace_id, projected_workspace.projectId),
            source.status,
        )
        revisions = self._load_revisions(workspace_id, projected_workspace.projectId)
        current_layout = self._current_layout(projected_workspace, revisions)
        body: dict[str, Any] = {
            "workspace": projected_workspace.model_dump(mode="json", by_alias=True),
            "panels": [panel.model_dump(mode="json", by_alias=True) for panel in panels],
            "currentLayoutRevision": (
                current_layout.model_dump(mode="json", by_alias=True)
                if current_layout is not None
                else None
            ),
            "sourceSummary": {
                "jobStatus": _identity(source.job, "status"),
                "analysisPlanSchemaVersion": source.plan_schema_version,
                "dependencyOutcome": source.dependency_outcome,
                "artifactCount": len(source.artifacts),
                "toolCallCount": len(source.tool_calls),
                "interpretationCount": len(source.interpretations),
                "reportCount": len(source.reports),
                "recipeCount": len(source.recipes),
                "metadataOnly": True,
            },
        }
        etag = _semantic_hash(body)
        body["projectionHash"] = etag
        return WorkspaceSnapshot(body=body, etag=etag)

    def patch_workspace(
        self,
        *,
        workspace_id: str,
        expected_revision: int,
        changes: Mapping[str, Any],
        updated_by: str,
    ) -> WorkspaceSnapshot:
        stored = self.get_stored_workspace(workspace_id)
        source = self._collect_source(
            stored.sourceJobId,
            allow_missing_job=True,
            fallback_project_id=stored.projectId,
        )
        if stored.readOnly or source.read_only:
            raise WorkspaceDomainError(
                "WORKSPACE_READ_ONLY",
                "This historical Workspace is read-only.",
                409,
            )
        if stored.revision != expected_revision:
            raise WorkspaceDomainError(
                "REVISION_MISMATCH",
                "Workspace revision does not match If-Match.",
                412,
            )

        revisions = self._load_revisions(workspace_id, stored.projectId)
        if len(revisions) >= WORKSPACE_MAX_LAYOUT_REVISIONS:
            raise WorkspaceDomainError(
                "REVISION_CAP_EXCEEDED",
                f"Workspace already has {WORKSPACE_MAX_LAYOUT_REVISIONS} layout revisions.",
                422,
            )
        panels = self._load_panels(workspace_id, stored.projectId)
        panel_ids = tuple(panel.panelId for panel in panels)
        current = self._current_layout(stored, revisions)
        if current is None:
            raise WorkspaceDomainError(
                "LAYOUT_REVISION_MISSING",
                "The current layout revision is unavailable.",
                409,
            )

        layout_value = changes.get("layout")
        if layout_value is None:
            layout = current.layout
        else:
            try:
                layout = WorkspaceLayoutState.model_validate(layout_value)
            except Exception as exc:
                raise WorkspaceDomainError(
                    "LAYOUT_INVALID",
                    "Workspace layout failed contract validation.",
                    422,
                ) from exc

        layout_payload = layout.model_dump(mode="json", by_alias=True)
        active_panel_present = "activePanelId" in changes
        if active_panel_present:
            layout_payload["activePanelId"] = changes.get("activePanelId")

        visibility = changes.get("panelVisibility")
        if visibility is not None:
            visibility_map = {
                str(item["panelId"]): bool(item["visible"])
                for item in visibility
            }
            unknown_visibility = sorted(set(visibility_map) - set(panel_ids))
            if unknown_visibility:
                raise WorkspaceDomainError(
                    "UNKNOWN_PANEL",
                    "Panel visibility references an unknown Workspace panel.",
                    422,
                )
            layout_payload["visiblePanelIds"] = [
                panel_id
                for panel_id in panel_ids
                if visibility_map.get(
                    panel_id,
                    panel_id in set(layout.visiblePanelIds),
                )
            ]

        try:
            next_layout = WorkspaceLayoutState.model_validate(layout_payload)
        except Exception as exc:
            raise WorkspaceDomainError(
                "LAYOUT_INVALID",
                "Workspace layout failed contract validation.",
                422,
            ) from exc
        self._validate_layout_membership(next_layout, panel_ids)

        selection_value: Any = current.selection
        if "pinnedSelection" in changes:
            selection_value = changes.get("pinnedSelection")
        if selection_value is not None and not isinstance(
            selection_value, WorkspaceSelectionContext
        ):
            try:
                selection_value = WorkspaceSelectionContext.model_validate(selection_value)
            except Exception as exc:
                raise WorkspaceDomainError(
                    "SELECTION_INVALID",
                    "Pinned selection failed contract validation.",
                    422,
                ) from exc
        if selection_value is not None:
            self._validate_selection_scope(selection_value, stored)

        next_revision = make_layout_revision(
            workspace_id=workspace_id,
            revision=expected_revision + 1,
            layout=next_layout,
            selection=selection_value,
            created_by=updated_by,
            created_at=_utc_now(),
        )
        update_arguments: dict[str, Any] = {
            "expected_revision": expected_revision,
            "project_id": stored.projectId,
            "active_panel_id": next_layout.activePanelId,
            "pinned_selection": (
                selection_value.model_dump(mode="json", by_alias=True)
                if selection_value is not None
                else None
            ),
            "layout_revision": next_revision.model_dump(mode="json", by_alias=True),
            "created_by": updated_by,
        }
        if "title" in changes:
            try:
                validated = stored.model_copy(update={"title": changes["title"]})
                validated = ScientificWorkspace.model_validate(
                    validated.model_dump(mode="json", by_alias=True)
                )
            except Exception as exc:
                raise WorkspaceDomainError(
                    "WORKSPACE_CONTRACT_INVALID",
                    "Workspace title failed strict contract validation.",
                    422,
                ) from exc
            update_arguments["title"] = validated.title

        try:
            self.repositories.workspaces.update_workspace(
                workspace_id,
                **update_arguments,
            )
        except Exception as exc:
            raise self._translate_repository_error(exc) from exc
        return self.get_snapshot(workspace_id)

    def list_project_workspaces(
        self,
        *,
        project_id: str,
        limit: int,
        cursor: str | None,
    ) -> dict[str, Any]:
        self.get_project(project_id)
        metadata_loader = getattr(
            self.repositories.workspaces,
            "list_projection_metadata_by_project",
            None,
        )
        if callable(metadata_loader):
            records = _records(metadata_loader(project_id))
            page, next_cursor = self._page_by_id(
                records,
                cursor,
                limit,
                lambda item: str(item["workspace_id"]),
            )
            return {
                "items": [self._workspace_list_summary(item) for item in page],
                "nextCursor": next_cursor,
                "limit": limit,
            }
        records = _records(self.repositories.workspaces.list_by_project(project_id))
        ordered = sorted(
            (ScientificWorkspace.model_validate(item) for item in records),
            key=lambda item: (item.updatedAt, item.workspaceId),
            reverse=True,
        )
        page, next_cursor = self._page_by_id(
            ordered,
            cursor,
            limit,
            lambda item: item.workspaceId,
        )
        items: list[dict[str, Any]] = []
        for workspace in page:
            snapshot = self.get_snapshot(workspace.workspaceId)
            projected = snapshot.body["workspace"]
            items.append(
                {
                    "workspaceId": projected["workspaceId"],
                    "projectId": projected["projectId"],
                    "sourceJobId": projected["sourceJobId"],
                    "title": projected["title"],
                    "projectedStatus": projected["projectedStatus"],
                    "readOnly": projected["readOnly"],
                    "analysisPlanSchemaVersion": projected.get("planSchemaVersion"),
                    "panelCount": len(snapshot.body["panels"]),
                    "artifactCount": projected["artifactCount"],
                    "interpretationCount": projected["interpretationCount"],
                    "revision": projected["revision"],
                    "updatedAt": projected["updatedAt"],
                    "projectionHash": snapshot.etag,
                }
            )
        return {"items": items, "nextCursor": next_cursor, "limit": limit}

    @staticmethod
    def _workspace_list_summary(record: Mapping[str, Any]) -> dict[str, Any]:
        schema = str(record.get("plan_schema_version") or "")
        read_only = False
        if record.get("current_job_id") is None:
            status = WorkspaceStatus.SOURCE_MISSING
            read_only = True
        elif schema in {"", "0.1"}:
            status = WorkspaceStatus.LEGACY_READ_ONLY
            read_only = True
        elif schema != "0.2":
            status = WorkspaceStatus.UNSUPPORTED
            read_only = True
        else:
            profile_payload = record.get("current_profile_json")
            profile_hash = (
                profile_payload.get("semanticHash")
                if isinstance(profile_payload, Mapping)
                else None
            )
            missing_identity = any(
                record.get(key) is None
                for key in (
                    "current_dataset_id",
                    "current_profile_id",
                    "current_intent_id",
                    "current_plan_id",
                    "current_capability_execution_id",
                    "current_decision_id",
                    "current_resolution_id",
                )
            )
            hash_mismatch = (
                profile_hash != record.get("profile_semantic_hash")
                or record.get("current_intent_hash") != record.get("intent_semantic_hash")
                or record.get("current_plan_hash") != record.get("plan_hash")
            )
            if missing_identity:
                status = WorkspaceStatus.LEGACY_READ_ONLY
                read_only = True
            elif hash_mismatch:
                status = WorkspaceStatus.STALE
                read_only = True
            else:
                job_status = str(record.get("current_job_status") or "").lower()
                dependency_outcome = str(record.get("dependency_outcome") or "").upper()
                if job_status in {"created", "pending", "queued", "running", "cancel_requested"}:
                    status = WorkspaceStatus.RUNNING
                elif job_status == "partial_success" or dependency_outcome == "PARTIAL_RESULTS":
                    status = WorkspaceStatus.PARTIAL_RESULTS
                elif job_status in {"failed", "cancelled", "canceled"} or dependency_outcome in {
                    "ALL_FAILED",
                    "VALIDATION_ABORTED",
                }:
                    status = WorkspaceStatus.FAILED
                elif job_status in {"completed", "succeeded", "success"}:
                    status = WorkspaceStatus.COMPLETE
                else:
                    status = WorkspaceStatus.READY
        summary = {
            "workspaceId": str(record["workspace_id"]),
            "projectId": str(record["project_id"]),
            "sourceJobId": str(record["source_job_id"]),
            "title": str(record["title"]),
            "projectedStatus": status.value,
            "readOnly": read_only,
            "analysisPlanSchemaVersion": record.get("plan_schema_version"),
            "panelCount": int(record.get("panel_count") or 0),
            "artifactCount": int(record.get("artifact_count") or 0),
            "interpretationCount": int(record.get("interpretation_count") or 0),
            "revision": int(record.get("revision") or 0),
            "updatedAt": _iso_value(record.get("updated_at")),
        }
        summary["projectionHash"] = _semantic_hash(summary)
        return summary

    def list_analysis_jobs(
        self,
        *,
        project_id: str,
        limit: int,
        cursor: str | None,
    ) -> dict[str, Any]:
        self.get_project(project_id)
        jobs = _repo_list(getattr(self.repositories, "jobs", None), "list_by_project", project_id)
        ordered = sorted(
            jobs,
            key=lambda item: (
                str(item.get("updatedAt") or item.get("createdAt") or ""),
                str(item.get("jobId") or item.get("id") or ""),
            ),
            reverse=True,
        )
        page, next_cursor = self._page_by_id(
            ordered,
            cursor,
            limit,
            lambda item: str(item.get("jobId") or item.get("id")),
        )
        items: list[dict[str, Any]] = []
        for job in page:
            job_id = str(job.get("jobId") or job.get("id"))
            try:
                existing = self.repositories.workspaces.get_by_project_job(
                    project_id, job_id
                )
            except (KeyError, LookupError):
                existing = None
            source = self._collect_source(job_id, allow_missing_job=False)
            items.append(
                {
                    "jobId": job_id,
                    "projectId": project_id,
                    "datasetId": _identity(job, "datasetId", "dataset_id"),
                    "jobStatus": _identity(job, "status"),
                    "workspaceProjectionStatus": source.status.value,
                    "analysisPlanSchemaVersion": source.plan_schema_version,
                    "dependencyOutcome": source.dependency_outcome,
                    "artifactCount": len(source.artifacts),
                    "interpretationCount": len(source.interpretations),
                    "workspaceId": (
                        _identity(_record(existing), "workspaceId", "workspace_id")
                        if existing is not None
                        else None
                    ),
                    "workspaceExists": existing is not None,
                    "createdAt": job.get("createdAt"),
                    "updatedAt": job.get("updatedAt"),
                }
            )
        return {"items": items, "nextCursor": next_cursor, "limit": limit}

    def list_panels(self, workspace_id: str) -> tuple[WorkspacePanel, ...]:
        workspace = self.get_stored_workspace(workspace_id)
        source = self._collect_source(
            workspace.sourceJobId,
            allow_missing_job=True,
            fallback_project_id=workspace.projectId,
        )
        return self._project_current_panels(
            self._load_panels(workspace_id, workspace.projectId),
            source.status,
        )

    def get_panel(self, workspace_id: str, panel_id: str) -> WorkspacePanel:
        for panel in self.list_panels(workspace_id):
            if panel.panelId == panel_id:
                return panel
        raise WorkspaceDomainError("PANEL_NOT_FOUND", "Workspace panel not found.", 404)

    def list_layout_revisions(
        self, workspace_id: str
    ) -> tuple[WorkspaceLayoutRevision, ...]:
        workspace = self.get_stored_workspace(workspace_id)
        return self._load_revisions(workspace_id, workspace.projectId)

    def get_layout_revision(
        self, workspace_id: str, revision: int
    ) -> WorkspaceLayoutRevision:
        workspace = self.get_stored_workspace(workspace_id)
        try:
            value = self.repositories.workspaces.get_layout_revision(
                workspace_id, revision, project_id=workspace.projectId
            )
        except (KeyError, LookupError):
            value = None
        if value is None:
            raise WorkspaceDomainError(
                "LAYOUT_REVISION_NOT_FOUND",
                "Workspace layout revision not found.",
                404,
            )
        try:
            return WorkspaceLayoutRevision.model_validate(value)
        except Exception as exc:
            raise WorkspaceDomainError(
                "LAYOUT_REVISION_INVALID",
                "The persisted layout revision failed contract validation.",
                409,
            ) from exc

    def _collect_source(
        self,
        job_id: str,
        *,
        allow_missing_job: bool,
        fallback_project_id: str | None = None,
    ) -> _SourceProjection:
        job = _repo_get(getattr(self.repositories, "jobs", None), job_id)
        if job is None and not allow_missing_job:
            raise WorkspaceDomainError("JOB_NOT_FOUND", "Analysis job not found.", 404)

        project_id = _identity(job, "projectId", "project_id") or fallback_project_id
        project = (
            _repo_get(getattr(self.repositories, "projects", None), project_id)
            if project_id
            else None
        )
        dataset_id = _identity(job, "datasetId", "dataset_id")
        dataset = (
            _repo_get(getattr(self.repositories, "datasets", None), dataset_id)
            if dataset_id
            else None
        )

        plan_record = None
        plan = None
        plan_repository = getattr(self.repositories, "analysis_plans", None)
        if plan_repository is not None and job is not None:
            getter = getattr(plan_repository, "get_plan_for_job", None)
            if callable(getter):
                try:
                    plan_record = _record(getter(job_id))
                except (KeyError, LookupError):
                    plan_record = None
            if plan_record is not None:
                nested = plan_record.get("analysisPlan") or plan_record.get("plan")
                plan = _record(nested) if nested is not None else plan_record

        profile_id = (
            _identity(plan_record, "profileId", "profile_id")
            or _identity(plan, "profileId", "profile_id")
        )
        profile = (
            _repo_get(getattr(self.repositories, "data_profiles", None), profile_id)
            if profile_id
            else None
        )

        intent = None
        intent_repository = getattr(self.repositories, "analysis_intents", None)
        if intent_repository is not None and job is not None:
            execution_getter = getattr(intent_repository, "get_execution_for_job", None)
            try:
                execution = (
                    _record(execution_getter(job_id))
                    if callable(execution_getter)
                    else None
                )
            except (KeyError, LookupError):
                execution = None
            intent_id = _identity(execution, "intentId", "intent_id")
            intent_getter = getattr(intent_repository, "get_intent", None)
            if intent_id and callable(intent_getter):
                try:
                    intent_record = _record(intent_getter(intent_id))
                except (KeyError, LookupError):
                    intent_record = None
                if intent_record is not None:
                    nested = intent_record.get("analysisIntent")
                    intent = _record(nested) if nested is not None else intent_record

        eligibility_resolution = None
        selection_decision = None
        capability_repository = getattr(
            self.repositories, "capability_planning", None
        )
        capability_execution_getter = getattr(
            capability_repository, "get_execution_for_job", None
        )
        try:
            capability_execution = (
                _record(capability_execution_getter(job_id))
                if job is not None and callable(capability_execution_getter)
                else None
            )
        except (KeyError, LookupError):
            capability_execution = None
        decision_id = _identity(
            capability_execution, "decisionId", "decision_id"
        )
        decision_getter = getattr(capability_repository, "get_decision", None)
        if decision_id and callable(decision_getter):
            try:
                decision_record = _record(decision_getter(decision_id))
            except (KeyError, LookupError):
                decision_record = None
            if decision_record is not None:
                nested = decision_record.get("capabilityDecision")
                selection_decision = (
                    _record(nested) if nested is not None else decision_record
                )
        resolution_id = (
            _identity(selection_decision, "resolutionId", "resolution_id")
            or _identity(capability_execution, "resolutionId", "resolution_id")
        )
        resolution_getter = getattr(
            capability_repository, "get_resolution", None
        )
        if resolution_id and callable(resolution_getter):
            try:
                resolution_record = _record(resolution_getter(resolution_id))
            except (KeyError, LookupError):
                resolution_record = None
            if resolution_record is not None:
                nested = resolution_record.get("eligibilityResolution")
                eligibility_resolution = (
                    _record(nested) if nested is not None else resolution_record
                )

        dependency = None
        dependency_repository = getattr(
            self.repositories, "dependency_execution", None
        )
        dependency_getter = getattr(
            dependency_repository, "get_execution_for_job", None
        )
        if job is not None and callable(dependency_getter):
            try:
                dependency = _record(dependency_getter(job_id))
            except (KeyError, LookupError):
                dependency = None

        tool_calls = _repo_list(
            getattr(self.repositories, "tool_calls", None), "list_for_job", job_id
        )
        artifacts = _repo_list(
            getattr(self.repositories, "artifacts", None), "list_for_job", job_id
        )
        interpretations = _repo_list(
            getattr(self.repositories, "interpretations", None),
            "list_for_job",
            job_id,
        )
        reports = _repo_list(
            getattr(self.repositories, "reports", None), "list_for_job", job_id
        )
        recipes = _repo_list(
            getattr(self.repositories, "recipes", None), "list_for_job", job_id
        )

        status, read_only, historical, warnings = self._project_status(
            job=job,
            project=project,
            dataset=dataset,
            profile=profile,
            intent=intent,
            eligibility_resolution=eligibility_resolution,
            selection_decision=selection_decision,
            plan_record=plan_record,
            plan=plan,
            dependency=dependency,
        )
        return _SourceProjection(
            project=project,
            job=job,
            dataset=dataset,
            profile=profile,
            intent=intent,
            eligibility_resolution=eligibility_resolution,
            selection_decision=selection_decision,
            plan_record=plan_record,
            plan=plan,
            dependency_execution=dependency,
            tool_calls=tool_calls,
            artifacts=artifacts,
            interpretations=interpretations,
            reports=reports,
            recipes=recipes,
            status=status,
            read_only=read_only,
            historical=historical,
            warnings=warnings,
        )

    @staticmethod
    def _project_status(
        *,
        job: Mapping[str, Any] | None,
        project: Mapping[str, Any] | None,
        dataset: Mapping[str, Any] | None,
        profile: Mapping[str, Any] | None,
        intent: Mapping[str, Any] | None,
        eligibility_resolution: Mapping[str, Any] | None,
        selection_decision: Mapping[str, Any] | None,
        plan_record: Mapping[str, Any] | None,
        plan: Mapping[str, Any] | None,
        dependency: Mapping[str, Any] | None,
    ) -> tuple[WorkspaceStatus, bool, bool, tuple[WorkspaceWarning, ...]]:
        warnings: list[WorkspaceWarning] = []
        if job is None or project is None:
            warnings.append(
                WorkspaceWarning(
                    code="SOURCE_MISSING",
                    message="The exact source Job or Project is no longer available.",
                )
            )
            return WorkspaceStatus.SOURCE_MISSING, True, True, tuple(warnings)

        schema_version = _identity(plan, "schemaVersion")
        historical = schema_version != "0.2"
        if schema_version is None:
            warnings.append(
                WorkspaceWarning(
                    code="LEGACY_SOURCE_IDENTITIES_INCOMPLETE",
                    message="The historical source has no current AnalysisPlan identity and remains read-only.",
                )
            )
            return WorkspaceStatus.LEGACY_READ_ONLY, True, True, tuple(warnings)
        if schema_version not in {"0.1", "0.2"}:
            warnings.append(
                WorkspaceWarning(
                    code="UNSUPPORTED_PLAN_SCHEMA",
                    message="The source AnalysisPlan schema is unsupported.",
                )
            )
            return WorkspaceStatus.UNSUPPORTED, True, historical, tuple(warnings)

        if dataset is None:
            warnings.append(
                WorkspaceWarning(
                    code="SOURCE_DATASET_MISSING",
                    message="The exact source Dataset is unavailable.",
                )
            )
            return WorkspaceStatus.SOURCE_MISSING, True, historical, tuple(warnings)

        if schema_version == "0.1":
            warnings.append(
                WorkspaceWarning(
                    code="LEGACY_PLAN_READ_ONLY",
                    message="AnalysisPlan 0.1 is projected without dependency reinterpretation.",
                )
            )
            return WorkspaceStatus.LEGACY_READ_ONLY, True, True, tuple(warnings)

        plan_hash = _source_hash(plan_record, "planHash", "semanticHash", "semantic_hash")
        profile_hash = _source_hash(profile, "semanticHash", "semantic_hash")
        intent_hash = _source_hash(intent, "intentHash", "semanticHash", "semantic_hash")
        resolution_hash = _source_hash(
            eligibility_resolution, "resolutionHash", "semanticHash", "semantic_hash"
        )
        decision_hash = _source_hash(
            selection_decision, "decisionHash", "semanticHash", "semantic_hash"
        )
        if (
            profile is None
            or intent is None
            or eligibility_resolution is None
            or selection_decision is None
            or plan_hash is None
            or profile_hash is None
            or intent_hash is None
            or resolution_hash is None
            or decision_hash is None
        ):
            warnings.append(
                WorkspaceWarning(
                    code="LEGACY_SOURCE_IDENTITIES_INCOMPLETE",
                    message="Current source identities are incomplete; the Workspace remains a read-only legacy projection.",
                )
            )
            return WorkspaceStatus.LEGACY_READ_ONLY, True, True, tuple(warnings)

        job_dataset_id = _identity(job, "datasetId", "dataset_id")
        plan_dataset_id = _identity(plan, "datasetId", "dataset_id")
        profile_dataset_id = _identity(profile, "datasetId", "dataset_id")
        profile_dataset_version = _profile_dataset_version(profile)
        resolution_dataset_id = _identity(
            eligibility_resolution, "datasetId", "dataset_id"
        )
        resolution_dataset_version = _identity(
            eligibility_resolution, "datasetVersion", "dataset_version"
        )
        resolution_intent_id = _identity(
            eligibility_resolution, "intentId", "intent_id"
        )
        resolution_intent_hash = _source_hash(
            eligibility_resolution, "intentHash", "intent_hash"
        )
        resolution_profile_id = _identity(
            eligibility_resolution, "profileId", "profile_id"
        )
        resolution_profile_hash = _source_hash(
            eligibility_resolution, "profileSemanticHash", "profile_semantic_hash"
        )
        decision_intent_id = _identity(selection_decision, "intentId", "intent_id")
        decision_intent_hash = _source_hash(
            selection_decision, "intentHash", "intent_hash"
        )
        decision_profile_id = _identity(selection_decision, "profileId", "profile_id")
        decision_profile_hash = _source_hash(
            selection_decision, "profileSemanticHash", "profile_semantic_hash"
        )
        decision_resolution_id = _identity(
            selection_decision, "resolutionId", "resolution_id"
        )
        decision_resolution_hash = _source_hash(
            selection_decision, "resolutionHash", "resolution_hash"
        )
        if (
            plan_dataset_id not in {None, job_dataset_id}
            or profile_dataset_id not in {None, job_dataset_id}
            or resolution_dataset_id not in {None, job_dataset_id}
            or resolution_dataset_version not in {None, profile_dataset_version}
            or resolution_intent_id != _identity(intent, "intentId", "intent_id")
            or resolution_intent_hash != intent_hash
            or resolution_profile_id != _identity(profile, "profileId", "profile_id")
            or resolution_profile_hash != profile_hash
            or decision_intent_id != _identity(intent, "intentId", "intent_id")
            or decision_intent_hash != intent_hash
            or decision_profile_id != _identity(profile, "profileId", "profile_id")
            or decision_profile_hash != profile_hash
            or decision_resolution_id
            != _identity(eligibility_resolution, "resolutionId", "resolution_id")
            or decision_resolution_hash != resolution_hash
        ):
            warnings.append(
                WorkspaceWarning(
                    code="SOURCE_IDENTITY_STALE",
                    message="Persisted source identities no longer describe one exact Dataset.",
                )
            )
            return WorkspaceStatus.STALE, True, False, tuple(warnings)

        job_status = (_identity(job, "status") or "").lower()
        dependency_outcome = (
            (_identity(dependency, "overallOutcome", "outcome") or "").upper()
        )
        if job_status in {
            "created",
            "pending",
            "queued",
            "running",
            "cancel_requested",
        }:
            return WorkspaceStatus.RUNNING, False, False, tuple(warnings)
        if job_status in {"partial_success", "partial_results"} or dependency_outcome == "PARTIAL_RESULTS":
            warnings.append(
                WorkspaceWarning(
                    code="PARTIAL_EXECUTION",
                    message="The source execution completed with partial results.",
                )
            )
            return WorkspaceStatus.PARTIAL_RESULTS, False, False, tuple(warnings)
        if job_status in {"failed", "cancelled", "canceled"} or dependency_outcome in {
            "ALL_FAILED",
            "VALIDATION_ABORTED",
        }:
            return WorkspaceStatus.FAILED, False, False, tuple(warnings)
        if job_status in {"completed", "succeeded", "success"}:
            return WorkspaceStatus.COMPLETE, False, False, tuple(warnings)
        return WorkspaceStatus.READY, False, False, tuple(warnings)

    def _workspace_source_refs(
        self,
        project_id: str,
        job_id: str,
        source: _SourceProjection,
    ) -> tuple[WorkspaceSourceRef, ...]:
        refs: list[WorkspaceSourceRef] = [
            WorkspaceSourceRef(
                kind=WorkspaceSourceKind.PROJECT,
                sourceId=project_id,
                projectId=project_id,
                jobId=job_id,
            ),
            WorkspaceSourceRef(
                kind=WorkspaceSourceKind.JOB,
                sourceId=job_id,
                projectId=project_id,
                jobId=job_id,
                contract="job",
                contractVersion="1.0",
            ),
        ]
        dataset_id = _identity(source.job, "datasetId", "dataset_id")
        if dataset_id:
            refs.append(
                WorkspaceSourceRef(
                    kind=WorkspaceSourceKind.DATASET,
                    sourceId=dataset_id,
                    projectId=project_id,
                    jobId=job_id,
                    contract="dataset",
                    contractVersion="1.0",
                )
            )
        profile_id = _identity(source.profile, "profileId", "profile_id")
        if profile_id:
            refs.append(
                WorkspaceSourceRef(
                    kind=WorkspaceSourceKind.PROFILE,
                    sourceId=profile_id,
                    sourceHash=_source_hash(
                        source.profile, "semanticHash", "semantic_hash"
                    ),
                    projectId=project_id,
                    jobId=job_id,
                    contract="data_profile",
                    contractVersion=_identity(
                        source.profile, "contractVersion", "schemaVersion"
                    ),
                )
            )
        intent_id = _identity(source.intent, "intentId", "intent_id")
        if intent_id:
            refs.append(
                WorkspaceSourceRef(
                    kind=WorkspaceSourceKind.INTENT,
                    sourceId=intent_id,
                    sourceHash=_source_hash(
                        source.intent, "intentHash", "semanticHash", "semantic_hash"
                    ),
                    contract="analysis_intent",
                    contractVersion=_identity(
                        source.intent, "schemaVersion", "contractVersion"
                    ),
                    projectId=project_id,
                    jobId=job_id,
                )
            )
        resolution_id = _identity(
            source.eligibility_resolution, "resolutionId", "resolution_id"
        )
        if resolution_id:
            refs.append(
                WorkspaceSourceRef(
                    kind=WorkspaceSourceKind.ELIGIBILITY_RESOLUTION,
                    sourceId=resolution_id,
                    sourceHash=_source_hash(
                        source.eligibility_resolution,
                        "resolutionHash",
                        "semanticHash",
                        "semantic_hash",
                    ),
                    contract="eligibility_resolution",
                    contractVersion=_identity(
                        source.eligibility_resolution,
                        "schemaVersion",
                        "contractVersion",
                    ),
                    projectId=project_id,
                    jobId=job_id,
                )
            )
        decision_id = _identity(
            source.selection_decision, "decisionId", "decision_id"
        )
        if decision_id:
            refs.append(
                WorkspaceSourceRef(
                    kind=WorkspaceSourceKind.SELECTION_DECISION,
                    sourceId=decision_id,
                    sourceHash=_source_hash(
                        source.selection_decision,
                        "decisionHash",
                        "semanticHash",
                        "semantic_hash",
                    ),
                    contract="capability_planning_decision",
                    contractVersion=_identity(
                        source.selection_decision,
                        "schemaVersion",
                        "contractVersion",
                    ),
                    projectId=project_id,
                    jobId=job_id,
                )
            )
        plan_id = (
            _identity(source.plan_record, "planId", "analysisPlanId", "id")
            or _identity(source.job, "planId", "plan_id")
        )
        if plan_id:
            refs.append(
                WorkspaceSourceRef(
                    kind=WorkspaceSourceKind.PLAN,
                    sourceId=plan_id,
                    sourceHash=_source_hash(
                        source.plan_record, "planHash", "semanticHash", "semantic_hash"
                    ),
                    projectId=project_id,
                    jobId=job_id,
                    contract="analysis_plan",
                    contractVersion=source.plan_schema_version,
                )
            )
        dependency_id = _identity(
            source.dependency_execution,
            "executionRecordId",
            "executionId",
            "id",
        )
        if dependency_id:
            refs.append(
                WorkspaceSourceRef(
                    kind=WorkspaceSourceKind.DEPENDENCY_EXECUTION,
                    sourceId=dependency_id,
                    sourceHash=_source_hash(
                        source.dependency_execution,
                        "executionHash",
                        "executionRecordHash",
                        "semanticHash",
                    ),
                    contract="dependency_execution",
                    contractVersion=_identity(
                        source.dependency_execution,
                        "schemaVersion",
                        "contractVersion",
                    ),
                    projectId=project_id,
                    jobId=job_id,
                )
            )
        return tuple(refs)

    def _build_panels(
        self,
        workspace_id: str,
        project_id: str,
        job_id: str,
        source: _SourceProjection,
    ) -> tuple[WorkspacePanel, ...]:
        base_refs = self._workspace_source_refs(project_id, job_id, source)
        specifications: list[dict[str, Any]] = [
            {
                "kind": WorkspacePanelKind.OVERVIEW,
                "title": "Overview",
                "identity": job_id,
                "refs": base_refs,
                "renderer": "workspace.overview/1.0",
                "state": self._base_panel_state(source.status),
            }
        ]
        if source.dataset is not None:
            specifications.append(
                {
                    "kind": WorkspacePanelKind.DATA,
                    "title": "Data context",
                    "identity": _identity(source.job, "datasetId", "dataset_id") or job_id,
                    "refs": base_refs,
                    "renderer": "workspace.data/1.0",
                    "state": self._base_panel_state(source.status),
                }
            )
        specifications.extend(
            [
                {
                    "kind": WorkspacePanelKind.PLAN,
                    "title": "Analysis plan",
                    "identity": _identity(
                        source.plan_record, "planId", "analysisPlanId", "id"
                    )
                    or job_id,
                    "refs": base_refs,
                    "renderer": "workspace.plan/1.0",
                    "state": self._base_panel_state(source.status),
                },
                {
                    "kind": WorkspacePanelKind.EXECUTION,
                    "title": "Execution",
                    "identity": job_id,
                    "refs": base_refs,
                    "renderer": "workspace.execution/1.0",
                    "state": self._execution_panel_state(source.status),
                },
            ]
        )

        sorted_artifacts = sorted(
            source.artifacts,
            key=lambda item: (
                str(item.get("type") or ""),
                str(item.get("artifactId") or item.get("id") or ""),
            ),
        )
        artifact_refs: list[WorkspaceSourceRef] = []
        for artifact in sorted_artifacts:
            artifact_id = _identity(artifact, "artifactId", "id")
            if not artifact_id:
                continue
            artifact_type = _contract_token(artifact.get("type"), "artifact")
            content_type = str(artifact.get("contentType") or "")
            unsupported = content_type in {"text/html", "application/javascript"} or artifact_type in {
                "html",
                "javascript",
            }
            artifact_ref = WorkspaceSourceRef(
                kind=WorkspaceSourceKind.ARTIFACT,
                sourceId=artifact_id,
                sourceHash=_source_hash(
                    artifact, "contentHash", "sha256", "semanticHash"
                ),
                projectId=project_id,
                jobId=job_id,
                toolCallId=_identity(artifact, "toolCallId", "tool_call_id"),
                contract=artifact_type,
                contractVersion=_identity(artifact, "version"),
                mediaType=(content_type if content_type and not unsupported else None),
            )
            artifact_refs.append(artifact_ref)
            specifications.append(
                {
                    "kind": WorkspacePanelKind.SCIENTIFIC_RESULT,
                    "title": f"Result: {artifact_type}",
                    "identity": artifact_id,
                    "refs": (*base_refs, artifact_ref),
                    "renderer": (
                        "workspace.inert-fallback/1.0"
                        if unsupported
                        else "workspace.artifact-metadata/1.0"
                    ),
                    "state": (
                        WorkspacePanelState.CONTRACT_UNSUPPORTED
                        if unsupported
                        else self._artifact_panel_state(source.status)
                    ),
                    "unsupported": (
                        "Executable or HTML artifact contracts are inert and unsupported."
                        if unsupported
                        else None
                    ),
                }
            )

        if source.interpretations:
            interpretation_refs: list[WorkspaceSourceRef] = []
            evidence_bundle_refs: list[WorkspaceSourceRef] = []
            evidence_artifact_ids: set[str] = set()
            evidence_repository = getattr(self.repositories, "interpretations", None)
            bundle_getter = getattr(evidence_repository, "get_bundle", None)
            for interpretation in sorted(
                source.interpretations,
                key=lambda item: str(
                    (item.get("interpretation") or {}).get("interpretationId")
                    or item.get("interpretationId")
                    or item.get("id")
                    or ""
                ),
            ):
                nested_interpretation = _record(
                    interpretation.get("interpretation")
                )
                interpretation_payload = nested_interpretation or interpretation
                interpretation_id = _identity(
                    interpretation_payload, "interpretationId", "id"
                )
                if interpretation_id:
                    interpretation_refs.append(
                        WorkspaceSourceRef(
                            kind=WorkspaceSourceKind.INTERPRETATION,
                            sourceId=interpretation_id,
                            sourceHash=_source_hash(
                                interpretation_payload,
                                "semanticHash",
                                "interpretationHash",
                            ),
                            projectId=project_id,
                            jobId=job_id,
                            contract="grounded_interpretation",
                            contractVersion=_identity(
                                interpretation_payload,
                                "schemaVersion",
                                "contractVersion",
                            ),
                        )
                    )
                bundle_id = _identity(
                    interpretation,
                    "bundleId",
                ) or _identity(
                    interpretation_payload,
                    "sourceBundleId",
                )
                if not bundle_id or not callable(bundle_getter):
                    continue
                try:
                    bundle = _record(bundle_getter(bundle_id))
                except (KeyError, LookupError):
                    bundle = None
                if bundle is None:
                    continue
                if (
                    _identity(bundle, "projectId") != project_id
                    or _identity(bundle, "jobId") != job_id
                ):
                    raise WorkspaceDomainError(
                        "EVIDENCE_SOURCE_SCOPE_MISMATCH",
                        "A persisted evidence bundle does not belong to the Workspace source Job.",
                        409,
                    )
                bundle_hash = _source_hash(bundle, "bundleHash", "semanticHash")
                if bundle_hash is None:
                    raise WorkspaceDomainError(
                        "EVIDENCE_SOURCE_INTEGRITY_FAILED",
                        "A persisted evidence bundle has no exact semantic hash.",
                        409,
                    )
                evidence_bundle_refs.append(
                    WorkspaceSourceRef(
                        kind=WorkspaceSourceKind.EVIDENCE_BUNDLE,
                        sourceId=bundle_id,
                        sourceHash=bundle_hash,
                        projectId=project_id,
                        jobId=job_id,
                        contract="scientific_evidence_bundle",
                        contractVersion=_identity(bundle, "schemaVersion"),
                    )
                )
                for evidence_item in _records(bundle.get("evidenceItems")):
                    artifact_id = _identity(evidence_item, "sourceArtifactId")
                    artifact_hash = _source_hash(
                        evidence_item, "sourceArtifactChecksum"
                    )
                    matching_ref = next(
                        (
                            ref
                            for ref in artifact_refs
                            if ref.sourceId == artifact_id
                            and ref.sourceHash == artifact_hash
                        ),
                        None,
                    )
                    if matching_ref is None:
                        raise WorkspaceDomainError(
                            "EVIDENCE_ARTIFACT_SCOPE_MISMATCH",
                            "Grounded evidence references an Artifact outside the exact Workspace source.",
                            409,
                        )
                    evidence_artifact_ids.add(matching_ref.sourceId)

            evidence_artifact_refs = [
                ref for ref in artifact_refs if ref.sourceId in evidence_artifact_ids
            ]
            findings_refs = [
                *base_refs,
                *interpretation_refs,
                *evidence_bundle_refs,
                *evidence_artifact_refs,
            ]
            if len(findings_refs) > 32:
                raise WorkspaceDomainError(
                    "PANEL_SOURCE_REF_CAP_EXCEEDED",
                    "Grounded findings source references exceed the WorkspacePanel cap.",
                    422,
                )
            specifications.append(
                {
                    "kind": WorkspacePanelKind.FINDINGS,
                    "title": "Grounded findings",
                    "identity": job_id,
                    "refs": tuple(findings_refs),
                    "renderer": "workspace.findings/1.0",
                    "state": self._artifact_panel_state(source.status),
                    "evidence_refs": tuple(
                        sorted(ref.sourceId for ref in evidence_bundle_refs)
                    ),
                    "provenance_refs": tuple(
                        sorted(evidence_artifact_ids)
                    ),
                }
            )
            if evidence_bundle_refs:
                evidence_refs = [*evidence_bundle_refs, *evidence_artifact_refs]
                if len(evidence_refs) > 32:
                    raise WorkspaceDomainError(
                        "PANEL_SOURCE_REF_CAP_EXCEEDED",
                        "Scientific evidence source references exceed the WorkspacePanel cap.",
                        422,
                    )
                specifications.append(
                    {
                        "kind": WorkspacePanelKind.EVIDENCE,
                        "title": "Scientific evidence",
                        "identity": job_id,
                        "refs": tuple(evidence_refs),
                        "renderer": "workspace.evidence/1.0",
                        "state": self._artifact_panel_state(source.status),
                        "evidence_refs": tuple(
                            sorted(ref.sourceId for ref in evidence_bundle_refs)
                        ),
                        "provenance_refs": tuple(
                            sorted(evidence_artifact_ids)
                        ),
                    }
                )

        specifications.append(
            {
                "kind": WorkspacePanelKind.PROVENANCE,
                "title": "Provenance",
                "identity": job_id,
                "refs": base_refs,
                "renderer": "workspace.provenance/1.0",
                "state": self._base_panel_state(source.status),
            }
        )
        if source.reports or source.recipes:
            specifications.append(
                {
                    "kind": WorkspacePanelKind.REPORT,
                    "title": "Report and recipe references",
                    "identity": job_id,
                    "refs": base_refs,
                    "renderer": "workspace.report/1.0",
                    "state": self._artifact_panel_state(source.status),
                }
            )

        if len(specifications) > WORKSPACE_MAX_PANELS:
            raise WorkspaceDomainError(
                "PANEL_CAP_EXCEEDED",
                f"Workspace projection exceeds the {WORKSPACE_MAX_PANELS}-panel cap.",
                422,
            )

        panels: list[WorkspacePanel] = []
        for ordinal, specification in enumerate(specifications):
            kind = specification["kind"]
            panel_id = deterministic_panel_id(
                workspace_id, kind, str(specification["identity"])
            )
            refs = tuple(specification["refs"])
            source_ref_hash = workspace_semantic_hash(
                [ref.model_dump(mode="json", by_alias=True) for ref in refs]
            )
            accepted_selection_kinds, emitted_selection_kinds = (
                _PANEL_SELECTION_DECLARATIONS[specification["renderer"]]
            )
            payload: dict[str, Any] = {
                "schemaVersion": "1.0",
                "panelId": panel_id,
                "workspaceId": workspace_id,
                "panelKind": kind.value,
                "title": specification["title"],
                "ordinal": ordinal,
                "visible": True,
                "sourceRefs": [
                    ref.model_dump(mode="json", by_alias=True) for ref in refs
                ],
                "sourceReferenceHash": source_ref_hash,
                "rendererContract": specification["renderer"],
                "state": specification["state"].value,
                "acceptedSelectionKinds": [
                    item.value for item in accepted_selection_kinds
                ],
                "emittedSelectionKinds": [
                    item.value for item in emitted_selection_kinds
                ],
                "evidenceRefs": list(specification.get("evidence_refs", ())),
                "provenanceRefs": list(specification.get("provenance_refs", ())),
                "capabilityRequirement": None,
                "layout": WorkspacePanelLayout(
                    order=ordinal
                ).model_dump(mode="json", by_alias=True),
                "mobilePresentationMode": "STACKED",
                "accessibleName": specification["title"],
                "unsupportedReason": specification.get("unsupported"),
                "contractProvenance": "phase10m1.explicit_metadata_projection/1.0",
            }
            payload["panelStateHash"] = _semantic_hash(payload)
            panels.append(WorkspacePanel.model_validate(payload))
        return tuple(panels)

    @staticmethod
    def _base_panel_state(status: WorkspaceStatus) -> WorkspacePanelState:
        if status is WorkspaceStatus.SOURCE_MISSING:
            return WorkspacePanelState.SOURCE_DELETED
        if status is WorkspaceStatus.STALE:
            return WorkspacePanelState.STALE
        if status is WorkspaceStatus.UNSUPPORTED:
            return WorkspacePanelState.CONTRACT_UNSUPPORTED
        return WorkspacePanelState.PRODUCED

    @staticmethod
    def _execution_panel_state(status: WorkspaceStatus) -> WorkspacePanelState:
        if status is WorkspaceStatus.RUNNING:
            return WorkspacePanelState.LOADING
        if status is WorkspaceStatus.PARTIAL_RESULTS:
            return WorkspacePanelState.PARTIAL
        if status is WorkspaceStatus.FAILED:
            return WorkspacePanelState.FAILED
        return WorkspaceProjectionService._base_panel_state(status)

    @staticmethod
    def _artifact_panel_state(status: WorkspaceStatus) -> WorkspacePanelState:
        if status is WorkspaceStatus.PARTIAL_RESULTS:
            return WorkspacePanelState.PARTIAL
        return WorkspaceProjectionService._base_panel_state(status)

    def _project_current_panels(
        self,
        panels: Sequence[WorkspacePanel],
        status: WorkspaceStatus,
    ) -> tuple[WorkspacePanel, ...]:
        projected: list[WorkspacePanel] = []
        for panel in panels:
            state = panel.state
            if state is not WorkspacePanelState.CONTRACT_UNSUPPORTED:
                if panel.panelKind is WorkspacePanelKind.EXECUTION:
                    state = self._execution_panel_state(status)
                elif panel.panelKind in {
                    WorkspacePanelKind.SCIENTIFIC_RESULT,
                    WorkspacePanelKind.FINDINGS,
                    WorkspacePanelKind.EVIDENCE,
                    WorkspacePanelKind.REPORT,
                }:
                    state = self._artifact_panel_state(status)
                else:
                    state = self._base_panel_state(status)
            declarations = _PANEL_SELECTION_DECLARATIONS.get(panel.rendererContract)
            accepted = panel.acceptedSelectionKinds if declarations is None else declarations[0]
            emitted = panel.emittedSelectionKinds if declarations is None else declarations[1]
            if (
                state is panel.state
                and accepted == panel.acceptedSelectionKinds
                and emitted == panel.emittedSelectionKinds
            ):
                projected.append(panel)
                continue
            payload = panel.model_dump(
                mode="json",
                by_alias=True,
                exclude={"panelStateHash"},
            )
            payload["state"] = state.value
            payload["acceptedSelectionKinds"] = [item.value for item in accepted]
            payload["emittedSelectionKinds"] = [item.value for item in emitted]
            payload["contractProvenance"] = "phase10m3.selection_registry.v1"
            payload["panelStateHash"] = _semantic_hash(payload)
            projected.append(WorkspacePanel.model_validate(payload))
        return tuple(projected)

    def _load_panels(
        self, workspace_id: str, project_id: str | None = None
    ) -> tuple[WorkspacePanel, ...]:
        try:
            records = self.repositories.workspaces.list_panels(
                workspace_id, project_id=project_id
            )
        except (KeyError, LookupError):
            records = ()
        try:
            panels = tuple(WorkspacePanel.model_validate(item) for item in records)
        except Exception as exc:
            raise WorkspaceDomainError(
                "PANEL_RECORD_INVALID",
                "A persisted panel failed contract validation.",
                409,
            ) from exc
        return tuple(sorted(panels, key=lambda item: (item.ordinal, item.panelId)))

    def _load_revisions(
        self, workspace_id: str, project_id: str | None = None
    ) -> tuple[WorkspaceLayoutRevision, ...]:
        try:
            records = self.repositories.workspaces.list_layout_revisions(
                workspace_id, project_id=project_id
            )
        except (KeyError, LookupError):
            records = ()
        try:
            revisions = tuple(
                WorkspaceLayoutRevision.model_validate(item) for item in records
            )
        except Exception as exc:
            raise WorkspaceDomainError(
                "LAYOUT_REVISION_INVALID",
                "A persisted layout revision failed contract validation.",
                409,
            ) from exc
        return tuple(sorted(revisions, key=lambda item: item.revision))

    def _current_layout(
        self,
        workspace: ScientificWorkspace,
        revisions: Sequence[WorkspaceLayoutRevision],
    ) -> WorkspaceLayoutRevision | None:
        for revision in revisions:
            if revision.revision == workspace.currentLayoutRevision:
                return revision
        try:
            raw = self.repositories.workspaces.get_current_layout(
                workspace.workspaceId, project_id=workspace.projectId
            )
        except (KeyError, LookupError):
            raw = None
        return WorkspaceLayoutRevision.model_validate(raw) if raw is not None else None

    @staticmethod
    def _validate_layout_membership(
        layout: WorkspaceLayoutState, panel_ids: Sequence[str]
    ) -> None:
        expected = set(panel_ids)
        if set(layout.panelOrder) != expected:
            raise WorkspaceDomainError(
                "LAYOUT_PANEL_MEMBERSHIP_INVALID",
                "Layout panel order must contain every Workspace panel exactly once.",
                422,
            )
        if not set(layout.visiblePanelIds).issubset(expected):
            raise WorkspaceDomainError(
                "UNKNOWN_PANEL",
                "Layout visibility references an unknown Workspace panel.",
                422,
            )
        if layout.activePanelId is not None and layout.activePanelId not in expected:
            raise WorkspaceDomainError(
                "UNKNOWN_PANEL",
                "The active panel does not belong to this Workspace.",
                422,
            )

    @staticmethod
    def _validate_selection_scope(
        selection: WorkspaceSelectionContext, workspace: ScientificWorkspace
    ) -> None:
        if selection.sourceScopeHash != workspace.sourceReferenceHash:
            raise WorkspaceDomainError(
                "SELECTION_SCOPE_MISMATCH",
                "Pinned selection source identity is stale or belongs elsewhere.",
                422,
            )
        refs = (() if selection.primary is None else (selection.primary,)) + selection.secondary
        for ref in refs:
            if ref.projectId != workspace.projectId:
                raise WorkspaceDomainError(
                    "SELECTION_SCOPE_MISMATCH",
                    "Pinned selection belongs to a different Project.",
                    422,
                )
            if ref.datasetId and ref.datasetId != workspace.datasetId:
                raise WorkspaceDomainError(
                    "SELECTION_SCOPE_MISMATCH",
                    "Pinned selection belongs to a different Dataset.",
                    422,
                )

    @staticmethod
    def _merge_warnings(
        stored: Sequence[WorkspaceWarning],
        projected: Sequence[WorkspaceWarning],
    ) -> tuple[WorkspaceWarning, ...]:
        indexed: dict[str, WorkspaceWarning] = {}
        for warning in (*stored, *projected):
            indexed[warning.code] = warning
        return tuple(indexed[key] for key in sorted(indexed))

    @staticmethod
    def _page_by_id(
        records: Sequence[Any],
        cursor: str | None,
        limit: int,
        identity: Any,
    ) -> tuple[list[Any], str | None]:
        start = 0
        if cursor:
            for index, record in enumerate(records):
                if identity(record) == cursor:
                    start = index + 1
                    break
            else:
                raise WorkspaceDomainError(
                    "CURSOR_INVALID",
                    "Pagination cursor is invalid for this collection.",
                    400,
                )
        page = list(records[start : start + limit])
        has_more = start + limit < len(records)
        next_cursor = identity(page[-1]) if page and has_more else None
        return page, next_cursor

    @staticmethod
    def _translate_repository_error(exc: Exception) -> WorkspaceDomainError:
        text = str(exc).lower()
        if "revision" in text or "concurr" in text or "etag" in text:
            return WorkspaceDomainError(
                "REVISION_MISMATCH",
                "Workspace revision does not match If-Match.",
                412,
            )
        if "cap" in text or "limit" in text:
            return WorkspaceDomainError(
                "REVISION_CAP_EXCEEDED",
                "Workspace revision cap was exceeded.",
                422,
            )
        if "project" in text or "scope" in text:
            return WorkspaceDomainError(
                "SOURCE_SCOPE_MISMATCH",
                "Workspace source scope validation failed.",
                409,
            )
        return WorkspaceDomainError(
            "WORKSPACE_PERSISTENCE_CONFLICT",
            "Workspace persistence rejected the request.",
            409,
        )
