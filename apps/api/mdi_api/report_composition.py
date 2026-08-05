"""Deterministic, read-only scientific Report and Recipe composition."""

from __future__ import annotations

import hashlib
import json
import re
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Iterator, Mapping

from sqlalchemy.engine import Connection, Engine

from mdi_api.unit_of_work import UnitOfWork
from mdi_api.workspaces import WorkspaceDomainError, WorkspaceProjectionService
from mdi_schemas import (
    GroundedScientificInterpretation,
    RecipeOutcome,
    RecipeReplayManifest,
    RecipeStep,
    ReportCompositionRequest,
    ReportCompositionSnapshot,
    ReportExportFormat,
    ReportExportManifest,
    ReportOutcome,
    ReportSection,
    ReportSourceReference,
    ReportSourceRole,
    ReportSourceState,
    ScientificEvidenceBundle,
    ScientificWorkspace,
    canonical_report_composition_json,
    deterministic_report_composition_id,
    report_composition_semantic_hash,
)


_M5_RECORD_VERSION = "m5.1.0"
_PAIR_LOCK = RLock()
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_PRIVATE_PATH = re.compile(r"(?:[A-Za-z]:[\\/]|/(?:home|Users|var|tmp|etc)/)")
_CREDENTIAL_KEY = re.compile(r"(?:api[_-]?key|authorization|password|secret|credential|access[_-]?token)", re.IGNORECASE)
_EXTERNAL_AUTHORITY = re.compile(r"(?:https?://|file:|javascript:|data:)", re.IGNORECASE)


# This is the backend report-role projection of the complete M4 42-contract registry.
_ARTIFACT_REPORT_ROLES: dict[str, tuple[ReportSourceRole, str, str]] = {
    "plotly_json": (ReportSourceRole.REPORT_FIGURE_SOURCE, "STATIC_FIGURE", "Backend-produced plot with a numeric/table fallback."),
    "plotly_html": (ReportSourceRole.REPORT_UNSUPPORTED, "NONE", "Executable HTML is not a Report source."),
    "preview_png": (ReportSourceRole.REPORT_FIGURE_SOURCE, "STATIC_FIGURE", "Persisted static preview."),
    "figure_svg": (ReportSourceRole.REPORT_UNSUPPORTED, "NONE", "SVG is retained as an inert download because scripts and event handlers are not trusted."),
    "figure_pdf": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Persisted figure metadata; PDF embedding is outside mandatory M5 export."),
    "matterviz_html": (ReportSourceRole.REPORT_UNSUPPORTED, "NONE", "Executable viewer HTML is not a Report source."),
    "matterviz_snapshot_png": (ReportSourceRole.REPORT_FIGURE_SOURCE, "STATIC_FIGURE", "Persisted static viewer snapshot."),
    "structure_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Structure identity and approved text fallback; WebGL canvas is not authority."),
    "trajectory_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Trajectory identity and approved text fallback; current frame is not authority."),
    "trajectory_summary_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Validated trajectory summary metadata."),
    "trajectory_report_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Validated trajectory report metadata."),
    "trajectory_manifest_json": (ReportSourceRole.REPORT_PROVENANCE_SOURCE, "PROVENANCE", "Trajectory manifest provenance."),
    "phonon_band_json": (ReportSourceRole.REPORT_FIGURE_SOURCE, "STATIC_FIGURE", "Backend-produced phonon band data with table fallback."),
    "phonon_band_dos_json": (ReportSourceRole.REPORT_FIGURE_SOURCE, "STATIC_FIGURE", "Backend-produced combined phonon band/DOS data with table fallback."),
    "phonon_compatibility_json": (ReportSourceRole.REPORT_PROVENANCE_SOURCE, "PROVENANCE", "Phonon compatibility metadata."),
    "phonon_dos_json": (ReportSourceRole.REPORT_FIGURE_SOURCE, "STATIC_FIGURE", "Backend-produced phonon DOS data with table fallback."),
    "phonon_summary_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Validated phonon summary metadata."),
    "phonon_report_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Validated phonon report metadata."),
    "phonon_manifest_json": (ReportSourceRole.REPORT_PROVENANCE_SOURCE, "PROVENANCE", "Phonon manifest provenance."),
    "phonon_animation_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Animation identity only; an active WebGL frame is not Report authority."),
    "phonon_animation_summary_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Validated animation summary metadata."),
    "phonon_animation_manifest_json": (ReportSourceRole.REPORT_PROVENANCE_SOURCE, "PROVENANCE", "Animation manifest provenance."),
    "reciprocal_lattice_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Reciprocal-lattice identity and approved text fallback."),
    "brillouin_zone_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Brillouin-zone identity and approved text fallback."),
    "kpath_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Persisted k-path metadata; no frontend path reconstruction."),
    "brillouin_zone_manifest_json": (ReportSourceRole.REPORT_PROVENANCE_SOURCE, "PROVENANCE", "Brillouin-zone manifest provenance."),
    "volumetric_grid_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Volumetric field identity; WebGL canvas is not authority."),
    "volumetric_payload_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Volumetric payload identity only."),
    "volumetric_field_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Volumetric quantity and source identity."),
    "volumetric_dataset_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Volumetric dataset metadata."),
    "volumetric_manifest_json": (ReportSourceRole.REPORT_PROVENANCE_SOURCE, "PROVENANCE", "Volumetric manifest provenance."),
    "volumetric_structure_overlay_json": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Persisted overlay identity; no browser recomputation."),
    "volumetric_binary": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Binary payload is omitted; exact checksum and metadata remain."),
    "metrics_json": (ReportSourceRole.REPORT_TABLE_SOURCE, "BOUNDED_TABLE", "Backend-produced metrics table."),
    "table_json": (ReportSourceRole.REPORT_TABLE_SOURCE, "BOUNDED_TABLE", "Validated bounded table representation."),
    "table_csv": (ReportSourceRole.REPORT_TABLE_SOURCE, "BOUNDED_TABLE", "Persisted formal table download with identity and coverage."),
    "quality_issues_json": (ReportSourceRole.REPORT_TABLE_SOURCE, "BOUNDED_TABLE", "Backend-produced data-quality table."),
    "summary_md": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Unvalidated summary prose is not a scientific finding."),
    "report_md": (ReportSourceRole.REPORT_METADATA_ONLY, "METADATA", "Historical report text remains metadata and is not claim authority."),
    "report_html": (ReportSourceRole.REPORT_UNSUPPORTED, "NONE", "Executable Report HTML is retained only as an inert legacy download."),
    "recipe_json": (ReportSourceRole.REPORT_PROVENANCE_SOURCE, "PROVENANCE", "Existing Recipe provenance."),
    "analysis_plan_json": (ReportSourceRole.REPORT_PROVENANCE_SOURCE, "PROVENANCE", "Persisted AnalysisPlan provenance."),
}

if len(_ARTIFACT_REPORT_ROLES) != 42:
    raise RuntimeError("M5_ARTIFACT_ROLE_REGISTRY_INCOMPLETE")


@dataclass(frozen=True)
class ReportCompositionDomainError(Exception):
    code: str
    message: str
    status_code: int = 400
    retryable: bool = False

    def as_detail(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "retryable": self.retryable}


@dataclass(frozen=True)
class CompositionPreview:
    report: ReportCompositionSnapshot
    recipe: RecipeReplayManifest
    source_count: int
    mandatory_disclosure_count: int
    predicted_outcome: ReportOutcome

    def as_dict(self) -> dict[str, Any]:
        return {
            "report": self.report.model_dump(mode="json"),
            "recipe": self.recipe.model_dump(mode="json"),
            "sourceCount": self.source_count,
            "mandatoryDisclosureCount": self.mandatory_disclosure_count,
            "predictedOutcome": self.predicted_outcome.value,
            "persisted": False,
            "noExecution": {
                "planCreated": False,
                "jobCreated": False,
                "toolCallCreated": False,
                "queueMessageCreated": False,
            },
        }


@dataclass(frozen=True)
class _CompositionContext:
    workspace: ScientificWorkspace
    workspace_projection_hash: str
    panels: tuple[Mapping[str, Any], ...]
    source: Any
    sources: tuple[ReportSourceReference, ...]
    mandatory_disclosures: tuple[ReportSourceReference, ...]
    source_by_id: Mapping[str, ReportSourceReference]
    artifact_by_id: Mapping[str, Mapping[str, Any]]
    claim_by_id: Mapping[str, Mapping[str, Any]]
    evidence_by_id: Mapping[str, Mapping[str, Any]]
    interpretation_records: tuple[Mapping[str, Any], ...]
    lineage_records: tuple[Mapping[str, Any], ...]


def _identity(record: Mapping[str, Any] | None, *keys: str) -> str | None:
    if record is None:
        return None
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return str(value)
    return None


def _hash(record: Mapping[str, Any] | None, *keys: str) -> str | None:
    value = _identity(record, *keys)
    if value is None:
        return None
    lowered = value.lower()
    return lowered if _SHA256.fullmatch(lowered) else None


def _mapping(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        return value
    return None


def _safe_source_time(workspace: ScientificWorkspace) -> datetime:
    return workspace.updatedAt.astimezone(timezone.utc)


def _evidence_dataset_version_matches(*, evidence_version: str | None, workspace: ScientificWorkspace) -> bool:
    if evidence_version is None:
        return True
    if workspace.datasetVersion is not None:
        return evidence_version == workspace.datasetVersion
    return (
        workspace.planSchemaVersion == "0.1"
        and workspace.planId is not None
        and evidence_version == f"legacy-plan:{workspace.planId}"
    )


def _disclosure(
    *,
    workspace: ScientificWorkspace,
    code: str,
    message: str,
    state: ReportSourceState = ReportSourceState.MANDATORY,
) -> ReportSourceReference:
    semantic = report_composition_semantic_hash({"code": code, "message": message, "workspaceId": workspace.workspaceId})
    return ReportSourceReference(
        sourceKind="DISCLOSURE",
        sourceId=deterministic_report_composition_id("disclosure", semantic),
        sourceHash=semantic,
        contract="report.disclosure",
        contractVersion="1.0",
        projectId=workspace.projectId,
        datasetId=workspace.datasetId,
        datasetVersion=workspace.datasetVersion,
        jobId=workspace.sourceJobId,
        role=ReportSourceRole.REPORT_DISCLOSURE_ONLY,
        state=state,
        representation="DISCLOSURE",
        fallback=message,
        reason=code,
    )


class ReportSourceEligibilityProjector:
    """Projects bounded report sources from exact persisted Workspace authorities."""

    def __init__(self, repositories: Any) -> None:
        self.repositories = repositories
        self.workspace_service = WorkspaceProjectionService(repositories)

    def project(self, workspace_id: str) -> _CompositionContext:
        try:
            snapshot = self.workspace_service.get_snapshot(workspace_id)
            source = self.workspace_service.read_source_projection(workspace_id)
            workspace = ScientificWorkspace.model_validate(snapshot.body["workspace"])
        except WorkspaceDomainError as exc:
            raise ReportCompositionDomainError(exc.code, exc.message, exc.status_code, exc.retryable) from exc

        if source.job is None or source.project is None:
            raise ReportCompositionDomainError("SOURCE_JOB_NOT_FOUND", "The exact source Job or Project is unavailable.", 409)
        if _identity(source.job, "projectId", "project_id") != workspace.projectId:
            raise ReportCompositionDomainError("SOURCE_SCOPE_MISMATCH", "The source Job does not belong to this Workspace Project.", 403)

        panels = tuple(sorted(snapshot.body["panels"], key=lambda panel: (int(panel.get("ordinal", 0)), str(panel.get("panelId", "")))))
        artifact_by_id = {
            str(_identity(artifact, "artifactId", "id")): artifact
            for artifact in source.artifacts
            if _identity(artifact, "artifactId", "id") is not None
        }
        sources: list[ReportSourceReference] = []
        mandatory: list[ReportSourceReference] = []

        for panel in panels:
            panel_id = _identity(panel, "panelId")
            if panel_id is None:
                continue
            panel_kind = str(panel.get("panelKind") or "UNKNOWN")
            role = ReportSourceRole.REPORT_PROVENANCE_SOURCE if panel_kind == "PROVENANCE" else ReportSourceRole.REPORT_METADATA_ONLY
            state = ReportSourceState.UNSUPPORTED if panel_kind == "REPORT" else ReportSourceState.METADATA_ONLY
            if panel_kind == "REPORT":
                role = ReportSourceRole.REPORT_UNSUPPORTED
            sources.append(ReportSourceReference(
                sourceKind="WORKSPACE_PANEL",
                sourceId=panel_id,
                sourceHash=_hash(panel, "panelStateHash", "sourceReferenceHash"),
                contract=str(panel.get("rendererContract") or "workspace.panel"),
                contractVersion=str(panel.get("rendererContractVersion") or "1.0"),
                projectId=workspace.projectId,
                datasetId=workspace.datasetId,
                datasetVersion=workspace.datasetVersion,
                jobId=workspace.sourceJobId,
                panelId=panel_id,
                role=role,
                state=state,
                representation="PROVENANCE" if role == ReportSourceRole.REPORT_PROVENANCE_SOURCE else "METADATA" if state != ReportSourceState.UNSUPPORTED else "NONE",
                fallback="Exact Workspace panel metadata.",
                reason="CURRENT_REPORT_PANEL_NOT_NESTABLE" if panel_kind == "REPORT" else None,
            ))

        stale_workspace = workspace.projectedStatus.value in {"STALE", "SOURCE_MISSING"}
        for artifact_id, artifact in sorted(artifact_by_id.items()):
            artifact_type = str(artifact.get("type") or "")
            artifact_version = str(artifact.get("version") or (_mapping(artifact.get("metadata")) or {}).get("artifactVersion") or "1")
            checksum = _hash(artifact, "sha256", "contentHash")
            classification = _ARTIFACT_REPORT_ROLES.get(artifact_type)
            scope_mismatch = (
                _identity(artifact, "projectId", "project_id") != workspace.projectId
                or _identity(artifact, "jobId", "job_id") != workspace.sourceJobId
                or (
                    workspace.datasetId is not None
                    and _identity(artifact, "datasetId", "dataset_id") not in {None, workspace.datasetId}
                )
            )
            if scope_mismatch:
                role, representation, fallback = ReportSourceRole.REPORT_UNSUPPORTED, "NONE", "Artifact exact Project, Job, or Dataset scope does not match the Workspace."
                state = ReportSourceState.SOURCE_INTEGRITY_FAILED
            elif classification is None:
                role, representation, fallback = ReportSourceRole.REPORT_UNSUPPORTED, "NONE", "Unknown Artifact contract; no renderer or Report role is guessed."
                state = ReportSourceState.UNSUPPORTED
            elif artifact_version != "1":
                role, representation, fallback = ReportSourceRole.REPORT_UNSUPPORTED, "NONE", "Artifact contract version is unsupported."
                state = ReportSourceState.UNSUPPORTED
            else:
                role, representation, fallback = classification
                state = ReportSourceState.METADATA_ONLY if role == ReportSourceRole.REPORT_METADATA_ONLY else ReportSourceState.ELIGIBLE
                if role == ReportSourceRole.REPORT_UNSUPPORTED:
                    state = ReportSourceState.UNSUPPORTED
            if checksum is None:
                role, representation, state = ReportSourceRole.REPORT_UNSUPPORTED, "NONE", ReportSourceState.SOURCE_INTEGRITY_FAILED
                fallback = "Artifact checksum is missing or invalid."
            elif stale_workspace:
                state = ReportSourceState.STALE
            reference = ReportSourceReference(
                sourceKind="ARTIFACT",
                sourceId=artifact_id,
                sourceHash=checksum,
                contract=artifact_type or "unknown",
                contractVersion=artifact_version,
                projectId=workspace.projectId,
                datasetId=_identity(artifact, "datasetId") or workspace.datasetId,
                datasetVersion=workspace.datasetVersion,
                jobId=workspace.sourceJobId,
                toolCallId=_identity(artifact, "toolCallId"),
                stepId=self._artifact_step_id(source.tool_calls, artifact),
                artifactId=artifact_id,
                artifactChecksum=checksum,
                role=role,
                state=state,
                representation=representation,
                fallback=fallback,
                reason="ARTIFACT_SCOPE_MISMATCH" if scope_mismatch else "ARTIFACT_CONTRACT_VERSION_UNSUPPORTED" if artifact_version != "1" else "CONTRACT_UNSUPPORTED" if classification is None else None,
            )
            sources.append(reference)
            if state in {ReportSourceState.STALE, ReportSourceState.SOURCE_INTEGRITY_FAILED, ReportSourceState.UNSUPPORTED}:
                mandatory.append(_disclosure(
                    workspace=workspace,
                    code=f"ARTIFACT_{state.value}_{artifact_id}",
                    message=f"Artifact {artifact_id} is {state.value.lower()} and is not treated as a normal scientific result.",
                    state=state if state != ReportSourceState.UNSUPPORTED else ReportSourceState.MANDATORY,
                ))

        claim_by_id: dict[str, Mapping[str, Any]] = {}
        evidence_by_id: dict[str, Mapping[str, Any]] = {}
        interpretation_records: list[Mapping[str, Any]] = []
        for stored in sorted(source.interpretations, key=lambda item: str((_mapping(item.get("interpretation")) or {}).get("interpretationId", ""))):
            try:
                interpretation = GroundedScientificInterpretation.model_validate(stored.get("interpretation"))
                bundle = ScientificEvidenceBundle.model_validate(self.repositories.interpretations.get_bundle(interpretation.sourceBundleId))
            except Exception:
                mandatory.append(_disclosure(workspace=workspace, code="INTERPRETATION_SOURCE_INTEGRITY_FAILED", message="A persisted interpretation or evidence bundle failed strict validation.", state=ReportSourceState.SOURCE_INTEGRITY_FAILED))
                continue
            if (
                interpretation.sourceJobId != workspace.sourceJobId
                or bundle.jobId != workspace.sourceJobId
                or bundle.projectId != workspace.projectId
                or interpretation.sourcePlanId != workspace.planId
                or interpretation.sourcePlanHash != workspace.planHash
            ):
                mandatory.append(_disclosure(workspace=workspace, code="INTERPRETATION_SCOPE_MISMATCH", message="An interpretation was excluded because its exact source scope does not match the Workspace.", state=ReportSourceState.SOURCE_INTEGRITY_FAILED))
                continue
            interpretation_records.append(stored)
            for evidence in bundle.evidenceItems:
                source_artifact = artifact_by_id.get(evidence.sourceArtifactId)
                evidence_scope_matches = (
                    source_artifact is not None
                    and _hash(source_artifact, "sha256", "contentHash") == evidence.sourceArtifactChecksum
                    and _identity(source_artifact, "projectId", "project_id") == workspace.projectId
                    and _identity(source_artifact, "jobId", "job_id") == workspace.sourceJobId
                    and evidence.datasetId in {None, workspace.datasetId}
                    and _evidence_dataset_version_matches(
                        evidence_version=evidence.datasetVersion,
                        workspace=workspace,
                    )
                )
                if not evidence_scope_matches:
                    mandatory.append(_disclosure(
                        workspace=workspace,
                        code=f"EVIDENCE_SOURCE_INTEGRITY_FAILED_{evidence.evidenceItemId}",
                        message=f"Evidence {evidence.evidenceItemId} was excluded because its exact Artifact, checksum, Dataset, or Job scope does not match the Workspace.",
                        state=ReportSourceState.SOURCE_INTEGRITY_FAILED,
                    ))
                    continue
                value = evidence.model_dump(mode="json")
                evidence_by_id[evidence.evidenceItemId] = value
                sources.append(ReportSourceReference(
                    sourceKind="EVIDENCE_ITEM", sourceId=evidence.evidenceItemId,
                    sourceHash=evidence.sourceArtifactChecksum, contract="ScientificEvidenceItem", contractVersion=evidence.schemaVersion,
                    projectId=workspace.projectId, datasetId=evidence.datasetId, datasetVersion=evidence.datasetVersion,
                    jobId=workspace.sourceJobId, toolCallId=evidence.producerToolCallId, stepId=evidence.producerStepId,
                    artifactId=evidence.sourceArtifactId, artifactChecksum=evidence.sourceArtifactChecksum,
                    interpretationId=interpretation.interpretationId, evidenceItemId=evidence.evidenceItemId,
                    role=ReportSourceRole.REPORT_EVIDENCE_SOURCE, state=ReportSourceState.ELIGIBLE,
                    representation="EVIDENCE", fallback=evidence.displayValue,
                ))
            for claim in sorted(interpretation.claims, key=lambda item: (item.displayOrder, item.claimId)):
                evidence_ids = set(claim.subjectEvidenceIds + claim.supportingEvidenceIds + claim.limitingEvidenceIds + claim.contradictingEvidenceIds)
                if not evidence_ids.issubset(evidence_by_id):
                    mandatory.append(_disclosure(workspace=workspace, code=f"CLAIM_EVIDENCE_MISSING_{claim.claimId}", message=f"Claim {claim.claimId} was excluded because exact supporting Evidence is unavailable.", state=ReportSourceState.SOURCE_INTEGRITY_FAILED))
                    continue
                value = claim.model_dump(mode="json")
                claim_by_id[claim.claimId] = value
                sources.append(ReportSourceReference(
                    sourceKind="SCIENTIFIC_CLAIM", sourceId=claim.claimId,
                    sourceHash=interpretation.interpretationHash, contract="ScientificClaim", contractVersion=claim.schemaVersion,
                    projectId=workspace.projectId, datasetId=workspace.datasetId, datasetVersion=workspace.datasetVersion,
                    jobId=workspace.sourceJobId, interpretationId=interpretation.interpretationId, claimId=claim.claimId,
                    role=ReportSourceRole.REPORT_FINDING_SOURCE, state=ReportSourceState.ELIGIBLE,
                    representation="CLAIM", fallback=claim.renderedText,
                ))
            for index, warning in enumerate(interpretation.globalWarnings):
                mandatory.append(_disclosure(workspace=workspace, code=f"INTERPRETATION_WARNING_{interpretation.interpretationId}_{index}", message=warning))
            for index, limitation in enumerate(interpretation.globalLimitations):
                mandatory.append(_disclosure(workspace=workspace, code=f"INTERPRETATION_LIMITATION_{interpretation.interpretationId}_{index}", message=limitation))
            for index, warning in enumerate(bundle.bundleWarnings):
                mandatory.append(_disclosure(workspace=workspace, code=f"EVIDENCE_WARNING_{bundle.bundleId}_{index}", message=warning))
            for index, limitation in enumerate(bundle.bundleLimitations):
                mandatory.append(_disclosure(workspace=workspace, code=f"EVIDENCE_LIMITATION_{bundle.bundleId}_{index}", message=limitation))

        if not interpretation_records:
            mandatory.append(_disclosure(workspace=workspace, code="GROUNDED_FINDINGS_UNAVAILABLE", message="No validated grounded interpretation is available; no findings were generated from raw Artifact content."))

        for warning in workspace.warnings:
            mandatory.append(_disclosure(workspace=workspace, code=f"WORKSPACE_{warning.code}", message=warning.message))
        mandatory.extend(self._execution_disclosures(workspace, source))

        lineage_getter = getattr(getattr(self.repositories, "dependency_execution", None), "list_lineage_for_job", None)
        lineage = tuple(lineage_getter(workspace.sourceJobId)) if callable(lineage_getter) else ()
        for record in sorted(lineage, key=lambda item: str(item.get("artifactId", ""))):
            lineage_id = _identity(record, "lineageId")
            if lineage_id is None:
                continue
            sources.append(ReportSourceReference(
                sourceKind="ARTIFACT_LINEAGE", sourceId=lineage_id,
                sourceHash=_hash(record, "lineageHash"), contract="ArtifactLineageRecord", contractVersion=str(record.get("schemaVersion") or "1.0"),
                projectId=workspace.projectId, datasetId=workspace.datasetId, datasetVersion=workspace.datasetVersion,
                jobId=workspace.sourceJobId, toolCallId=_identity(record, "producerToolCallId"), stepId=_identity(record, "producerStepId"),
                artifactId=_identity(record, "artifactId"), artifactChecksum=_hash(record, "contentHash"),
                role=ReportSourceRole.REPORT_PROVENANCE_SOURCE, state=ReportSourceState.ELIGIBLE,
                representation="PROVENANCE", fallback="Exact persisted Artifact lineage.",
            ))

        ordered_sources = tuple(sorted(sources, key=lambda item: (item.role.value, item.sourceKind, item.sourceId)))
        ordered_mandatory = tuple(sorted({item.sourceId: item for item in mandatory}.values(), key=lambda item: item.sourceId))
        source_by_id: dict[str, ReportSourceReference] = {}
        for item in ordered_sources:
            if item.sourceId in source_by_id:
                raise ReportCompositionDomainError("REPORT_SOURCE_INTEGRITY_FAILED", "Report source identities are not globally unique.", 409)
            source_by_id[item.sourceId] = item
        return _CompositionContext(
            workspace=workspace,
            workspace_projection_hash=snapshot.etag,
            panels=panels,
            source=source,
            sources=ordered_sources,
            mandatory_disclosures=ordered_mandatory,
            source_by_id=source_by_id,
            artifact_by_id=artifact_by_id,
            claim_by_id=claim_by_id,
            evidence_by_id=evidence_by_id,
            interpretation_records=tuple(interpretation_records),
            lineage_records=tuple(lineage),
        )

    def inventory(self, workspace_id: str) -> dict[str, Any]:
        context = self.project(workspace_id)
        return {
            "schemaVersion": "1.0",
            "workspaceId": context.workspace.workspaceId,
            "workspaceRevision": context.workspace.revision,
            "workspaceProjectionHash": context.workspace_projection_hash,
            "sources": [item.model_dump(mode="json") for item in context.sources],
            "mandatoryDisclosures": [item.model_dump(mode="json") for item in context.mandatory_disclosures],
            "sourceCount": len(context.sources),
            "mandatoryDisclosureCount": len(context.mandatory_disclosures),
            "artifactContractInventoryCount": len(_ARTIFACT_REPORT_ROLES),
            "metadataOnly": True,
            "heavyArtifactPayloadRequests": 0,
            "webglContexts": 0,
        }

    @staticmethod
    def _artifact_step_id(tool_calls: tuple[Mapping[str, Any], ...], artifact: Mapping[str, Any]) -> str | None:
        tool_call_id = _identity(artifact, "toolCallId")
        match = next((item for item in tool_calls if _identity(item, "id", "toolCallId") == tool_call_id), None)
        return _identity(match, "stepId")

    @staticmethod
    def _execution_disclosures(workspace: ScientificWorkspace, source: Any) -> list[ReportSourceReference]:
        disclosures: list[ReportSourceReference] = []
        dependency = source.dependency_execution or {}
        for step in dependency.get("steps") or ():
            state = str(step.get("state") or "")
            if state not in {"SUCCEEDED", "COMPLETED"}:
                step_id = str(step.get("stepId") or "unknown")
                error_code = str(step.get("errorCode") or state or "UNAVAILABLE")
                disclosures.append(_disclosure(
                    workspace=workspace,
                    code=f"EXECUTION_{step_id}_{state or 'UNKNOWN'}",
                    message=f"Step {step_id} ended in {state or 'UNKNOWN'} ({error_code}); dependent missing scope remains disclosed.",
                ))
        outcome = str(dependency.get("outcome") or source.job.get("status") or "UNKNOWN")
        if outcome in {"PARTIAL_RESULTS", "ALL_FAILED", "failed", "partial_success"}:
            disclosures.append(_disclosure(workspace=workspace, code=f"EXECUTION_OUTCOME_{outcome}", message=f"The persisted execution outcome is {outcome}; the Report must not present it as complete."))
        return disclosures


class ReportCompositionService:
    """Compose immutable Report/Recipe pairs without execution or provider authority."""

    def __init__(self, repositories: Any) -> None:
        self.repositories = repositories
        self.projector = ReportSourceEligibilityProjector(repositories)

    def source_inventory(self, workspace_id: str) -> dict[str, Any]:
        return self.projector.inventory(workspace_id)

    def preview(self, request: ReportCompositionRequest) -> CompositionPreview:
        context = self.projector.project(request.workspaceId)
        self._validate_workspace_revision(context, request.expectedWorkspaceRevision)
        request_hash = report_composition_semantic_hash(request.model_dump(mode="json"))
        seed = report_composition_semantic_hash({"mode": "PREVIEW", "requestHash": request_hash})
        report_id = deterministic_report_composition_id("report_preview", seed)
        recipe_id = deterministic_report_composition_id("recipe_preview", seed)
        report, recipe, predicted = self._compose_pair(
            context=context,
            request=request,
            report_id=report_id,
            recipe_id=recipe_id,
            preview=True,
        )
        return CompositionPreview(
            report=report,
            recipe=recipe,
            source_count=len(context.sources),
            mandatory_disclosure_count=len(context.mandatory_disclosures),
            predicted_outcome=predicted,
        )

    def finalize(
        self,
        request: ReportCompositionRequest,
        *,
        idempotency_key: str,
        created_by: str,
    ) -> dict[str, Any]:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", idempotency_key):
            raise ReportCompositionDomainError("REPORT_VALIDATION_FAILED", "Idempotency-Key is missing or invalid.", 400)
        key_hash = hashlib.sha256(idempotency_key.encode("utf-8")).hexdigest()
        report_repository = getattr(self.repositories, "reports", None)
        bind = getattr(report_repository, "bind", None)
        if isinstance(bind, Engine):
            with UnitOfWork(bind) as unit:
                return ReportCompositionService(unit.repositories)._finalize_bound(
                    request, key_hash=key_hash, created_by=created_by
                )
        with _PAIR_LOCK:
            return self._finalize_bound(request, key_hash=key_hash, created_by=created_by)

    def _finalize_bound(
        self,
        request: ReportCompositionRequest,
        *,
        key_hash: str,
        created_by: str,
    ) -> dict[str, Any]:
        context = self.projector.project(request.workspaceId)
        self._validate_workspace_revision(context, request.expectedWorkspaceRevision)
        request_hash = report_composition_semantic_hash(request.model_dump(mode="json"))
        identity_hash = report_composition_semantic_hash({
            "workspaceId": context.workspace.workspaceId,
            "projectId": context.workspace.projectId,
            "sourceJobId": context.workspace.sourceJobId,
            "idempotencyKeyHash": key_hash,
        })
        report_id = deterministic_report_composition_id("report", identity_hash)
        recipe_id = deterministic_report_composition_id("recipe", identity_hash)

        existing = self._existing_pair(report_id, recipe_id)
        if existing is not None:
            report_record, recipe_record = existing
            if report_record.get("requestHash") != request_hash or recipe_record.get("requestHash") != request_hash:
                raise ReportCompositionDomainError("REPORT_IDEMPOTENCY_CONFLICT", "The idempotency key is already bound to a different semantic request.", 409)
            self._validate_persisted_pair(report_record, recipe_record, context.workspace)
            return self._finalize_response(report_record, recipe_record, replayed=True)

        report, recipe, _predicted = self._compose_pair(
            context=context,
            request=request,
            report_id=report_id,
            recipe_id=recipe_id,
            preview=False,
        )
        report_record = {
            "id": report.reportId,
            "reportId": report.reportId,
            "recipeId": recipe.recipeId,
            "projectId": report.projectId,
            "datasetId": report.datasetId,
            "jobId": report.sourceJobId,
            "sourceJobId": report.sourceJobId,
            "workspaceId": report.workspaceId,
            "workspaceRevision": report.workspaceRevision,
            "version": _M5_RECORD_VERSION,
            "title": report.title,
            "compositionHash": report.compositionHash,
            "reportHash": report.reportHash,
            "recipeHash": recipe.recipeHash,
            "requestHash": request_hash,
            "idempotencyKeyHash": key_hash,
            "composition": report.model_dump(mode="json"),
            "createdBy": created_by,
            "createdAt": report.createdAt.isoformat(),
            "executionAuthorized": False,
        }
        recipe_record = {
            "id": recipe.recipeId,
            "recipeId": recipe.recipeId,
            "reportId": report.reportId,
            "projectId": recipe.projectId,
            "sourceJobId": report.sourceJobId,
            "workspaceId": recipe.workspaceId,
            "workspaceRevision": recipe.workspaceRevision,
            "version": _M5_RECORD_VERSION,
            "name": f"Exact rerun recipe for {report.title}",
            "compositionHash": recipe.compositionHash,
            "reportHash": report.reportHash,
            "recipeHash": recipe.recipeHash,
            "requestHash": request_hash,
            "idempotencyKeyHash": key_hash,
            "manifest": recipe.model_dump(mode="json"),
            "createdBy": created_by,
            "createdAt": recipe.createdAt.isoformat(),
            "executionAuthorized": False,
        }
        self._persist_pair(report_record, recipe_record)
        persisted_report = self.repositories.reports.get(report_id)
        persisted_recipe = self.repositories.recipes.get(recipe_id)
        self._validate_persisted_pair(persisted_report, persisted_recipe, context.workspace)
        return self._finalize_response(persisted_report, persisted_recipe, replayed=False)

    def list_history(self, workspace_id: str) -> dict[str, Any]:
        context = self.projector.project(workspace_id)
        reports = []
        for record in self.repositories.reports.list_for_job(context.workspace.sourceJobId):
            if record.get("projectId") != context.workspace.projectId:
                continue
            is_m5 = record.get("version") == _M5_RECORD_VERSION and record.get("workspaceId") == workspace_id
            if record.get("workspaceId") not in {None, workspace_id}:
                continue
            reports.append({
                "reportId": record.get("reportId") or record.get("id"),
                "recipeId": record.get("recipeId"),
                "version": record.get("version") or "legacy",
                "title": record.get("title") or record.get("name") or "Untitled report",
                "reportHash": record.get("reportHash"),
                "recipeHash": record.get("recipeHash"),
                "compositionHash": record.get("compositionHash"),
                "workspaceId": record.get("workspaceId"),
                "workspaceRevision": record.get("workspaceRevision"),
                "sourceJobId": record.get("sourceJobId") or record.get("jobId"),
                "outcome": (_mapping(record.get("composition")) or {}).get("outcome"),
                "createdAt": record.get("createdAt"),
                "legacyReadOnly": not is_m5,
                "exportFormats": ["json", "markdown"] if is_m5 else [],
            })
        reports.sort(key=lambda item: (str(item.get("createdAt") or ""), str(item.get("reportId") or "")), reverse=True)
        return {"workspaceId": workspace_id, "items": reports, "count": len(reports), "immutableHistory": True}

    def get_report(self, workspace_id: str, report_id: str) -> dict[str, Any]:
        context = self.projector.project(workspace_id)
        try:
            record = self.repositories.reports.get(report_id)
        except (KeyError, LookupError) as exc:
            raise ReportCompositionDomainError("REPORT_SOURCE_NOT_FOUND", "Report not found.", 404) from exc
        self._require_record_scope(record, context.workspace)
        if record.get("version") != _M5_RECORD_VERSION or record.get("workspaceId") != workspace_id:
            return {"legacyReadOnly": True, "report": self._legacy_report_projection(record)}
        try:
            report = ReportCompositionSnapshot.model_validate(record.get("composition"))
        except Exception as exc:
            raise ReportCompositionDomainError("REPORT_SOURCE_INTEGRITY_FAILED", "The persisted Report snapshot failed strict validation.", 409) from exc
        return {"legacyReadOnly": False, "report": report.model_dump(mode="json"), "recipeId": record.get("recipeId")}

    def get_recipe(self, workspace_id: str, report_id: str) -> dict[str, Any]:
        report_detail = self.get_report(workspace_id, report_id)
        if report_detail["legacyReadOnly"]:
            raise ReportCompositionDomainError("LEGACY_REPORT_READ_ONLY", "The historical Report has no M5 Recipe pair.", 409)
        recipe_id = str(report_detail["recipeId"])
        try:
            record = self.repositories.recipes.get(recipe_id)
        except (KeyError, LookupError) as exc:
            raise ReportCompositionDomainError("REPORT_RECIPE_PAIR_INCONSISTENT", "The exact paired Recipe is unavailable.", 409) from exc
        context = self.projector.project(workspace_id)
        self._require_record_scope(record, context.workspace)
        try:
            recipe = RecipeReplayManifest.model_validate(record.get("manifest"))
        except Exception as exc:
            raise ReportCompositionDomainError("REPORT_RECIPE_PAIR_INCONSISTENT", "The persisted Recipe manifest failed strict validation.", 409) from exc
        if recipe.sourceReportId != report_id:
            raise ReportCompositionDomainError("REPORT_RECIPE_PAIR_INCONSISTENT", "Report and Recipe identities do not match.", 409)
        return {"legacyReadOnly": False, "recipe": recipe.model_dump(mode="json")}

    def export(self, workspace_id: str, report_id: str, export_format: str) -> dict[str, Any]:
        try:
            format_value = ReportExportFormat(export_format)
        except ValueError as exc:
            raise ReportCompositionDomainError("EXPORT_FORMAT_UNSUPPORTED", "Only json and markdown exports are supported.", 404) from exc
        report = ReportCompositionSnapshot.model_validate(self.get_report(workspace_id, report_id)["report"])
        recipe = RecipeReplayManifest.model_validate(self.get_recipe(workspace_id, report_id)["recipe"])
        core = {"report": report.model_dump(mode="json"), "recipe": recipe.model_dump(mode="json")}
        _assert_safe_export_value(core)
        if format_value == ReportExportFormat.JSON:
            core_text = canonical_report_composition_json(core) + "\n"
            content_checksum = hashlib.sha256(core_text.encode("utf-8")).hexdigest()
            manifest = self._export_manifest(report, recipe, format_value, content_checksum, len(core_text.encode("utf-8")))
            content = canonical_report_composition_json({**core, "exportManifest": manifest.model_dump(mode="json")}) + "\n"
            content_type = "application/json; charset=utf-8"
            suffix = "json"
        else:
            content = self._render_markdown(report, recipe)
            encoded = content.encode("utf-8")
            content_checksum = hashlib.sha256(encoded).hexdigest()
            manifest = self._export_manifest(report, recipe, format_value, content_checksum, len(encoded))
            content_type = "text/markdown; charset=utf-8"
            suffix = "md"
        encoded = content.encode("utf-8")
        if len(encoded) > 2_097_152:
            raise ReportCompositionDomainError("EXPORT_SIZE_EXCEEDED", "The deterministic export exceeds the 2 MiB cap.", 413)
        return {
            "content": content,
            "contentType": content_type,
            "filename": f"scientific-report-{report.reportId}.{suffix}",
            "manifest": manifest.model_dump(mode="json"),
            "contentBytes": len(encoded),
        }

    def _compose_pair(
        self,
        *,
        context: _CompositionContext,
        request: ReportCompositionRequest,
        report_id: str,
        recipe_id: str,
        preview: bool,
    ) -> tuple[ReportCompositionSnapshot, RecipeReplayManifest, ReportOutcome]:
        selected = self._selected_sources(context, request)
        plan_record = context.source.plan_record
        plan = context.source.plan
        if plan_record is None or plan is None:
            raise ReportCompositionDomainError("REPORT_SOURCE_INTEGRITY_FAILED", "An exact AnalysisPlan is required for Report/Recipe composition.", 409)
        plan_id = _identity(plan_record, "planId", "id", "analysisPlanId") or context.workspace.planId
        plan_hash = _hash(plan_record, "planHash", "semanticHash") or context.workspace.planHash
        schema_version = str(plan.get("schemaVersion") or "")
        if plan_id is None or plan_hash is None or schema_version not in {"0.1", "0.2"}:
            raise ReportCompositionDomainError("REPORT_SOURCE_INTEGRITY_FAILED", "The exact AnalysisPlan identity or schema is unavailable.", 409)

        composition_hash = report_composition_semantic_hash({
            "request": request.model_dump(mode="json"),
            "workspaceSourceReferenceHash": context.workspace.sourceReferenceHash,
            "workspaceProjectionHash": context.workspace_projection_hash,
            "planId": plan_id,
            "planHash": plan_hash,
            "selectedSources": [item.model_dump(mode="json") for item in selected],
            "mandatoryDisclosures": [item.model_dump(mode="json") for item in context.mandatory_disclosures],
        })
        predicted = self._predicted_outcome(context, selected)
        analysis_goal = self._analysis_goal(context, plan)
        sections = self._build_sections(
            context=context,
            request=request,
            selected=selected,
            analysis_goal=analysis_goal,
            plan=plan,
            recipe_id=recipe_id,
        )
        warnings, limitations = self._warning_limitation_text(context)
        report_payload: dict[str, Any] = {
            "schemaVersion": "1.0",
            "reportId": report_id,
            "reportHash": "0" * 64,
            "compositionHash": composition_hash,
            "recipeId": recipe_id,
            "workspaceId": context.workspace.workspaceId,
            "workspaceRevision": context.workspace.revision,
            "projectId": context.workspace.projectId,
            "datasetId": context.workspace.datasetId,
            "datasetVersion": context.workspace.datasetVersion,
            "sourceJobId": context.workspace.sourceJobId,
            "sourcePlanId": plan_id,
            "sourcePlanHash": plan_hash,
            "sourcePlanSchemaVersion": schema_version,
            "title": request.title,
            "analysisGoal": analysis_goal,
            "outcome": ReportOutcome.REPORT_PREVIEW_READY.value if preview else predicted.value,
            "selectedSources": [item.model_dump(mode="json") for item in selected],
            "mandatoryDisclosures": [item.model_dump(mode="json") for item in context.mandatory_disclosures],
            "sections": [item.model_dump(mode="json") for item in sections],
            "warnings": warnings,
            "limitations": limitations,
            "executionAuthorized": False,
            "scientificAuthority": False,
            "createdAt": _safe_source_time(context.workspace),
        }
        report_semantic = {key: value for key, value in report_payload.items() if key not in {"reportId", "reportHash", "recipeId", "createdAt"}}
        report_payload["reportHash"] = report_composition_semantic_hash(report_semantic)
        try:
            report = ReportCompositionSnapshot.model_validate(report_payload)
        except Exception as exc:
            raise ReportCompositionDomainError("REPORT_VALIDATION_FAILED", "The deterministic Report snapshot failed strict validation.", 422) from exc

        recipe = self._build_recipe(
            context=context,
            report=report,
            recipe_id=recipe_id,
            plan_record=plan_record,
            plan=plan,
            warnings=warnings,
            limitations=limitations,
            limited=predicted != ReportOutcome.REPORT_READY,
        )
        return report, recipe, predicted

    def _selected_sources(self, context: _CompositionContext, request: ReportCompositionRequest) -> tuple[ReportSourceReference, ...]:
        groups = (
            (request.selectedPanelIds, "WORKSPACE_PANEL"),
            (request.selectedArtifactIds, "ARTIFACT"),
            (request.selectedClaimIds, "SCIENTIFIC_CLAIM"),
            (request.selectedEvidenceItemIds, "EVIDENCE_ITEM"),
        )
        requested: dict[str, ReportSourceReference] = {}
        for identities, expected_kind in groups:
            for source_id in identities:
                item = context.source_by_id.get(source_id)
                if item is None:
                    raise ReportCompositionDomainError("REPORT_SOURCE_NOT_FOUND", f"Selected source {source_id} is not in the exact Workspace inventory.", 404)
                if item.sourceKind != expected_kind:
                    raise ReportCompositionDomainError("REPORT_SELECTION_UNSUPPORTED", "A selected identity was supplied in the wrong source category.", 422)
                if item.state == ReportSourceState.STALE:
                    raise ReportCompositionDomainError("REPORT_SOURCE_STALE", f"Selected source {source_id} is stale.", 409)
                if item.state == ReportSourceState.SOURCE_INTEGRITY_FAILED:
                    raise ReportCompositionDomainError("REPORT_SOURCE_INTEGRITY_FAILED", f"Selected source {source_id} failed integrity validation.", 409)
                if item.state in {ReportSourceState.UNAVAILABLE, ReportSourceState.UNSUPPORTED} or item.role == ReportSourceRole.REPORT_UNSUPPORTED:
                    raise ReportCompositionDomainError("REPORT_SELECTION_UNSUPPORTED", f"Selected source {source_id} has no approved Report representation.", 422)
                requested[source_id] = item
        ordered = tuple(requested[source_id] for source_id in request.itemOrder)
        figure_count = sum(item.role == ReportSourceRole.REPORT_FIGURE_SOURCE for item in ordered)
        table_count = sum(item.role == ReportSourceRole.REPORT_TABLE_SOURCE for item in ordered)
        if figure_count > 32 or table_count > 32:
            raise ReportCompositionDomainError("REPORT_CAP_EXCEEDED", "Selected figure or table count exceeds the frozen cap.", 422)
        return ordered

    @staticmethod
    def _validate_workspace_revision(context: _CompositionContext, expected: int) -> None:
        if context.workspace.revision != expected:
            raise ReportCompositionDomainError("WORKSPACE_REVISION_CONFLICT", "The Workspace revision changed; no Report or Recipe was persisted.", 409)

    @staticmethod
    def _analysis_goal(context: _CompositionContext, plan: Mapping[str, Any]) -> str:
        intent = context.source.intent or {}
        goal = _identity(intent, "normalizedGoal", "goal") or _identity(plan, "goal") or "ANALYSIS_GOAL_NOT_AVAILABLE"
        return goal[:4096]

    @staticmethod
    def _predicted_outcome(context: _CompositionContext, selected: tuple[ReportSourceReference, ...]) -> ReportOutcome:
        execution = context.source.dependency_execution or {}
        outcome = str(execution.get("outcome") or context.source.job.get("status") or "")
        scientific_results = [item for item in selected if item.role in {ReportSourceRole.REPORT_FIGURE_SOURCE, ReportSourceRole.REPORT_TABLE_SOURCE, ReportSourceRole.REPORT_FINDING_SOURCE}]
        if outcome in {"ALL_FAILED", "failed"} and not scientific_results:
            return ReportOutcome.REPORT_NO_SCIENTIFIC_RESULTS
        if context.mandatory_disclosures or outcome in {"PARTIAL_RESULTS", "partial_success"}:
            return ReportOutcome.REPORT_READY_WITH_LIMITS
        return ReportOutcome.REPORT_READY

    def _build_sections(
        self,
        *,
        context: _CompositionContext,
        request: ReportCompositionRequest,
        selected: tuple[ReportSourceReference, ...],
        analysis_goal: str,
        plan: Mapping[str, Any],
        recipe_id: str,
    ) -> tuple[ReportSection, ...]:
        caption_by_id = {caption.sourceId: caption.text for caption in request.captions}
        result_items = [
            f"{item.sourceKind} {item.sourceId} ({item.contract or 'unknown'}@{item.contractVersion or 'unknown'}; checksum {item.sourceHash or 'unavailable'})"
            + (f" - {caption_by_id[item.sourceId]}" if item.sourceId in caption_by_id else "")
            for item in selected
            if item.role in {ReportSourceRole.REPORT_FIGURE_SOURCE, ReportSourceRole.REPORT_TABLE_SOURCE, ReportSourceRole.REPORT_METADATA_ONLY}
        ]
        finding_items = [context.claim_by_id[item.sourceId]["renderedText"] for item in selected if item.role == ReportSourceRole.REPORT_FINDING_SOURCE]
        evidence_items = [f"Evidence {item.sourceId} from Artifact {item.artifactId or 'unavailable'} ({item.artifactChecksum or 'checksum unavailable'})." for item in selected if item.role == ReportSourceRole.REPORT_EVIDENCE_SOURCE]
        provenance_items = [f"{item.sourceKind} {item.sourceId}: {item.fallback or 'exact provenance reference'}" for item in selected if item.role == ReportSourceRole.REPORT_PROVENANCE_SOURCE]
        disclosures = [item.fallback or item.reason or item.sourceId for item in context.mandatory_disclosures]
        steps = plan.get("steps") or ()
        method_items = [f"Step {step.get('stepId', 'unknown')}: tool {step.get('toolId', 'unknown')}; exact parameters and bindings are retained in Recipe {recipe_id}." for step in steps]
        execution = context.source.dependency_execution or {}
        execution_outcome = str(execution.get("outcome") or context.source.job.get("status") or "UNKNOWN")
        failed_items = [item for item in disclosures if any(token in item.lower() for token in ("failed", "blocked", "missing", "unavailable", "stale", "unsupported"))]
        environment_items = [
            f"Plan schema {plan.get('schemaVersion', 'unavailable')}.",
            f"Application source Workspace {context.workspace.workspaceId} revision {context.workspace.revision}.",
            "REFERENCE_METADATA_NOT_AVAILABLE" if not context.lineage_records else f"Persisted lineage records: {len(context.lineage_records)}.",
        ]
        raw = (
            ("TITLE", "Title", "READY", [request.title]),
            ("ANALYSIS_GOAL", "Analysis Goal", "READY", [analysis_goal]),
            ("DATASET_RESOURCE_SCOPE", "Dataset and Resource Scope", "READY" if context.workspace.datasetId else "UNAVAILABLE", [f"Project {context.workspace.projectId}; Dataset {context.workspace.datasetId or 'unavailable'} version {context.workspace.datasetVersion or 'unavailable'}; Profile {context.workspace.profileId or 'unavailable'} hash {context.workspace.profileSemanticHash or 'unavailable'}."]),
            ("METHODS_PLAN", "Methods and Plan", "READY" if method_items else "UNAVAILABLE", method_items),
            ("EXECUTION_STATUS", "Execution Status", "READY", [f"Persisted execution outcome: {execution_outcome}."]),
            ("SELECTED_RESULTS", "Selected Results", "READY" if result_items else "EMPTY", result_items),
            ("GROUNDED_FINDINGS", "Grounded Findings", "READY" if finding_items else "UNAVAILABLE", finding_items or ["GROUNDED_FINDINGS_UNAVAILABLE"]),
            ("WARNINGS_LIMITATIONS", "Warnings and Limitations", "LIMITED" if disclosures else "EMPTY", disclosures),
            ("FAILED_BLOCKED_MISSING", "Failed, Blocked and Missing Scope", "LIMITED" if failed_items else "EMPTY", failed_items),
            ("EVIDENCE_PROVENANCE", "Evidence and Provenance", "READY" if evidence_items or provenance_items else "EMPTY", evidence_items + provenance_items),
            ("ENVIRONMENT_REFERENCES", "Environment and References", "READY", environment_items),
            ("EXACT_RERUN_RECIPE", "Exact Rerun Recipe Reference", "READY", [f"Recipe {recipe_id}; declarative only; executionAuthorized=false."]),
        )
        return tuple(ReportSection(sectionId=section_id, title=title, status=status, items=tuple(items)) for section_id, title, status, items in raw)

    @staticmethod
    def _warning_limitation_text(context: _CompositionContext) -> tuple[tuple[str, ...], tuple[str, ...]]:
        warnings: list[str] = []
        limitations: list[str] = []
        for item in context.mandatory_disclosures:
            text = item.fallback or item.reason or item.sourceId
            if "LIMITATION" in str(item.reason or "") or "coverage" in text.lower():
                limitations.append(text)
            else:
                warnings.append(text)
        return tuple(warnings[:128]), tuple(limitations[:64])

    def _build_recipe(
        self,
        *,
        context: _CompositionContext,
        report: ReportCompositionSnapshot,
        recipe_id: str,
        plan_record: Mapping[str, Any],
        plan: Mapping[str, Any],
        warnings: tuple[str, ...],
        limitations: tuple[str, ...],
        limited: bool,
    ) -> RecipeReplayManifest:
        schema_version = str(plan["schemaVersion"])
        tool_calls = {str(item.get("stepId")): item for item in context.source.tool_calls}
        artifacts_by_step: dict[str, list[Mapping[str, Any]]] = {}
        for artifact in context.source.artifacts:
            step_id = ReportSourceEligibilityProjector._artifact_step_id(context.source.tool_calls, artifact)
            if step_id:
                artifacts_by_step.setdefault(step_id, []).append(artifact)
        steps: list[RecipeStep] = []
        resource_bindings: list[dict[str, Any]] = []
        for step in plan.get("steps") or ():
            step_id = str(step.get("stepId"))
            tool_call = tool_calls.get(step_id, {})
            produced = artifacts_by_step.get(step_id, [])
            metadata = _mapping(produced[0].get("metadata")) if produced else {}
            output = _mapping(step.get("output")) or {}
            expected = tuple(str(item) for item in output.get("artifactTypes") or ())
            if not expected:
                expected = tuple(sorted({str(item.get("type")) for item in produced if item.get("type")}))
            input_refs = tuple(deepcopy(item) for item in (step.get("inputRefs") or ()))
            resource_bindings.extend(deepcopy(item) for item in input_refs)
            steps.append(RecipeStep(
                stepId=step_id,
                toolId=str(step.get("toolId")),
                toolVersion=_identity(metadata or {}, "toolVersion") or _identity(tool_call, "toolVersion"),
                adapterVersion=_identity(metadata or {}, "adapterVersion"),
                params=deepcopy(step.get("params") or {}),
                inputRefs=input_refs,
                expectedOutputContracts=expected,
            ))
        dependency_bindings = tuple(sorted((deepcopy(item) for item in (plan.get("dependencyBindings") or ())), key=canonical_report_composition_json))
        graph_hash = _hash(plan, "graphHash") if schema_version == "0.2" else None
        original_artifacts = tuple(
            item for item in context.sources
            if item.sourceKind == "ARTIFACT" and item.artifactChecksum is not None
        )
        if len(original_artifacts) > 64:
            raise ReportCompositionDomainError(
                "REPORT_CAP_EXCEEDED",
                "The exact Recipe requires more than 64 original Artifact references.",
                422,
            )
        profile = context.source.profile or {}
        intent = context.source.intent or {}
        resolution = context.source.eligibility_resolution or {}
        decision = context.source.selection_decision or {}
        execution = context.source.dependency_execution or {}
        provider = None
        if context.interpretation_records:
            interpretation = _mapping(context.interpretation_records[0].get("interpretation")) or {}
            execution_record = _mapping(context.interpretation_records[0].get("execution")) or {}
            provider = {
                "mode": interpretation.get("mode"),
                "provider": interpretation.get("provider"),
                "providerVersion": interpretation.get("providerVersion"),
                "providerModel": execution_record.get("providerModel"),
                "repairCount": execution_record.get("repairCount"),
            }
        payload: dict[str, Any] = {
            "schemaVersion": "1.0",
            "recipeId": recipe_id,
            "recipeHash": "0" * 64,
            "compositionHash": report.compositionHash,
            "sourceReportId": report.reportId,
            "sourceReportHash": report.reportHash,
            "workspaceId": report.workspaceId,
            "workspaceRevision": report.workspaceRevision,
            "projectId": report.projectId,
            "datasetId": report.datasetId,
            "datasetVersion": report.datasetVersion,
            "datasetHash": _hash(context.source.dataset, "datasetHash", "semanticHash", "contentHash"),
            "profileId": _identity(profile, "profileId"),
            "profileVersion": _identity(profile, "schemaVersion", "version"),
            "profileHash": _hash(profile, "semanticHash"),
            "intentId": _identity(intent, "intentId"),
            "intentHash": _hash(intent, "intentHash", "semanticHash"),
            "eligibilityResolutionId": _identity(resolution, "resolutionId"),
            "eligibilityResolutionHash": _hash(resolution, "resolutionHash", "semanticHash"),
            "plannerDecisionId": _identity(decision, "decisionId"),
            "plannerDecisionHash": _hash(decision, "decisionHash", "semanticHash"),
            "analysisPlanId": _identity(plan_record, "planId", "id", "analysisPlanId"),
            "analysisPlanHash": _hash(plan_record, "planHash", "semanticHash"),
            "planSchemaVersion": schema_version,
            "dependencyModel": "TYPED_ARTIFACT_BINDINGS" if schema_version == "0.2" else "NONE_OR_SEQUENTIAL_INDEPENDENT",
            "graphHash": graph_hash,
            "steps": [step.model_dump(mode="json") for step in steps],
            "dependencyBindings": dependency_bindings,
            "sourceResourceBindings": tuple(resource_bindings),
            "originalArtifacts": [item.model_dump(mode="json") for item in original_artifacts],
            "executionOutcome": str(execution.get("outcome") or context.source.job.get("status") or "UNKNOWN"),
            "providerProvenance": provider,
            "environmentProvenance": {
                "planSchemaVersion": schema_version,
                "toolRegistryVersion": plan.get("toolRegistryVersion"),
                "runtimeVersion": execution.get("runtimeVersion"),
                "sourceExecutionTimestamp": execution.get("createdAt") or context.source.job.get("createdAt"),
            },
            "warnings": warnings,
            "limitations": limitations,
            "outcome": RecipeOutcome.RECIPE_READY_WITH_LIMITS.value if limited else RecipeOutcome.RECIPE_READY.value,
            "executionAuthorized": False,
            "planCreated": False,
            "jobCreated": False,
            "queueMessageCreated": False,
            "automaticReplay": False,
            "createdAt": report.createdAt,
        }
        _assert_safe_export_value(payload)
        semantic = {key: value for key, value in payload.items() if key not in {"recipeId", "recipeHash", "createdAt"}}
        payload["recipeHash"] = report_composition_semantic_hash(semantic)
        try:
            return RecipeReplayManifest.model_validate(payload)
        except Exception as exc:
            raise ReportCompositionDomainError("RECIPE_VALIDATION_FAILED", "The exact declarative Recipe failed strict validation.", 422) from exc

    def _existing_pair(self, report_id: str, recipe_id: str) -> tuple[dict[str, Any], dict[str, Any]] | None:
        try:
            report = self.repositories.reports.get(report_id)
        except (KeyError, LookupError):
            report = None
        try:
            recipe = self.repositories.recipes.get(recipe_id)
        except (KeyError, LookupError):
            recipe = None
        if (report is None) != (recipe is None):
            raise ReportCompositionDomainError("REPORT_RECIPE_PAIR_INCONSISTENT", "Only one member of the immutable Report/Recipe pair exists.", 409)
        return None if report is None else (report, recipe)

    def _persist_pair(self, report: Mapping[str, Any], recipe: Mapping[str, Any]) -> None:
        in_memory = hasattr(self.repositories.reports, "records") and hasattr(self.repositories.recipes, "records")
        report_backup = deepcopy(self.repositories.reports.records) if in_memory else None
        recipe_backup = deepcopy(self.repositories.recipes.records) if in_memory else None
        try:
            self.repositories.reports.create_immutable(report)
            self.repositories.recipes.create_immutable(recipe)
        except Exception as exc:
            if in_memory:
                self.repositories.reports.records = report_backup
                self.repositories.recipes.records = recipe_backup
            if "immutable snapshot conflict" in str(exc):
                raise ReportCompositionDomainError("REPORT_IDEMPOTENCY_CONFLICT", "The idempotency key conflicts with an immutable delivery snapshot.", 409) from exc
            raise

    @staticmethod
    def _validate_persisted_pair(report: Mapping[str, Any], recipe: Mapping[str, Any], workspace: ScientificWorkspace) -> None:
        try:
            report_model = ReportCompositionSnapshot.model_validate(report.get("composition"))
            recipe_model = RecipeReplayManifest.model_validate(recipe.get("manifest"))
        except Exception as exc:
            raise ReportCompositionDomainError("REPORT_RECIPE_PAIR_INCONSISTENT", "The persisted delivery pair failed strict validation.", 409) from exc
        exact = (
            report_model.recipeId == recipe_model.recipeId
            and recipe_model.sourceReportId == report_model.reportId
            and recipe_model.sourceReportHash == report_model.reportHash
            and report_model.compositionHash == recipe_model.compositionHash
            and report_model.workspaceId == recipe_model.workspaceId == workspace.workspaceId
            and report_model.projectId == recipe_model.projectId == workspace.projectId
            and report_model.sourceJobId == workspace.sourceJobId
            and report_model.sourcePlanHash == recipe_model.analysisPlanHash
        )
        if not exact:
            raise ReportCompositionDomainError("REPORT_RECIPE_PAIR_INCONSISTENT", "Report and Recipe exact identities do not match.", 409)

    @staticmethod
    def _finalize_response(report: Mapping[str, Any], recipe: Mapping[str, Any], *, replayed: bool) -> dict[str, Any]:
        return {
            "reportId": report.get("reportId"),
            "reportHash": report.get("reportHash"),
            "recipeId": recipe.get("recipeId"),
            "recipeHash": recipe.get("recipeHash"),
            "compositionHash": report.get("compositionHash"),
            "workspaceId": report.get("workspaceId"),
            "workspaceRevision": report.get("workspaceRevision"),
            "outcome": (_mapping(report.get("composition")) or {}).get("outcome"),
            "idempotentReplay": replayed,
            "immutable": True,
            "noExecution": {"planCreated": False, "jobCreated": False, "toolCallCreated": False, "queueMessageCreated": False},
        }

    @staticmethod
    def _require_record_scope(record: Mapping[str, Any], workspace: ScientificWorkspace) -> None:
        if record.get("projectId") != workspace.projectId:
            raise ReportCompositionDomainError("REPORT_AUTHORIZATION_FAILED", "Report/Recipe Project scope mismatch.", 403)
        source_job = record.get("sourceJobId") or record.get("jobId")
        if source_job != workspace.sourceJobId:
            raise ReportCompositionDomainError("SOURCE_SCOPE_MISMATCH", "Report/Recipe Job scope mismatch.", 403)
        if record.get("workspaceId") not in {None, workspace.workspaceId}:
            raise ReportCompositionDomainError("REPORT_AUTHORIZATION_FAILED", "Report/Recipe Workspace scope mismatch.", 403)

    @staticmethod
    def _legacy_report_projection(record: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "reportId": record.get("reportId") or record.get("id"),
            "projectId": record.get("projectId"),
            "sourceJobId": record.get("sourceJobId") or record.get("jobId"),
            "title": record.get("title") or record.get("name") or "Historical report",
            "version": record.get("version") or "legacy",
            "createdAt": record.get("createdAt"),
            "state": "LEGACY_READ_ONLY",
            "missingCompositionContract": True,
        }

    @staticmethod
    def _export_manifest(
        report: ReportCompositionSnapshot,
        recipe: RecipeReplayManifest,
        export_format: ReportExportFormat,
        content_checksum: str,
        byte_size: int,
    ) -> ReportExportManifest:
        payload: dict[str, Any] = {
            "schemaVersion": "1.0",
            "exportId": "export_pending",
            "exportHash": "0" * 64,
            "reportId": report.reportId,
            "reportHash": report.reportHash,
            "recipeId": recipe.recipeId,
            "recipeHash": recipe.recipeHash,
            "workspaceId": report.workspaceId,
            "projectId": report.projectId,
            "format": export_format.value,
            "rendererContract": "report_export.v1",
            "sourceReferences": [item.model_dump(mode="json") for item in report.selectedSources + report.mandatoryDisclosures],
            "contentChecksum": content_checksum,
            "byteSize": byte_size,
            "authorizationScope": f"project:{report.projectId}/workspace:{report.workspaceId}",
            "omittedPayloadReasons": (
                "Artifact payload bytes are referenced by exact identity and checksum, not embedded.",
                "WebGL canvas, camera state, browser screenshots, external assets and temporary URLs are excluded.",
            ),
            "coverage": f"{len(report.selectedSources)} selected sources and {len(report.mandatoryDisclosures)} mandatory disclosures.",
            "executionAuthorized": False,
            "generatedAt": report.createdAt,
        }
        semantic = {key: value for key, value in payload.items() if key not in {"exportId", "exportHash", "generatedAt"}}
        export_hash = report_composition_semantic_hash(semantic)
        payload["exportHash"] = export_hash
        payload["exportId"] = deterministic_report_composition_id("export", export_hash)
        return ReportExportManifest.model_validate(payload)

    @staticmethod
    def _render_markdown(report: ReportCompositionSnapshot, recipe: RecipeReplayManifest) -> str:
        lines = [f"# {_markdown_escape(report.title)}", ""]
        for section in report.sections:
            lines.extend((f"## {_markdown_escape(section.title)}", "", f"Status: `{section.status}`", ""))
            if section.items:
                lines.extend(f"- {_markdown_escape(item)}" for item in section.items)
            else:
                lines.append("- No verified content is available for this section.")
            lines.append("")
        lines.extend((
            "## Machine-readable identities", "",
            f"- Report: `{report.reportId}` (`{report.reportHash}`)",
            f"- Recipe: `{recipe.recipeId}` (`{recipe.recipeHash}`)",
            f"- Workspace: `{report.workspaceId}` revision `{report.workspaceRevision}`",
            f"- Source Job: `{report.sourceJobId}`",
            f"- Source Plan: `{recipe.analysisPlanId}` (`{recipe.analysisPlanHash}`)",
            "- Recipe execution authorization: `false`", "",
        ))
        return "\n".join(lines).replace("\r\n", "\n").replace("\r", "\n")


def _markdown_escape(value: str) -> str:
    return re.sub(r"([\\`*_{}\[\]()#+.!|>-])", r"\\\1", value)


def _assert_safe_export_value(value: Any, *, key: str | None = None) -> None:
    if key is not None and _CREDENTIAL_KEY.search(key):
        raise ReportCompositionDomainError("REPORT_VALIDATION_FAILED", "Credential-shaped fields cannot enter Report/Recipe composition.", 422)
    if isinstance(value, Mapping):
        for nested_key, nested in value.items():
            _assert_safe_export_value(nested, key=str(nested_key))
    elif isinstance(value, (list, tuple)):
        for nested in value:
            _assert_safe_export_value(nested)
    elif isinstance(value, str) and (_PRIVATE_PATH.search(value) or _EXTERNAL_AUTHORITY.search(value)):
        raise ReportCompositionDomainError("REPORT_VALIDATION_FAILED", "Private paths and external executable authorities cannot enter Report/Recipe composition.", 422)


__all__ = [
    "CompositionPreview",
    "ReportCompositionDomainError",
    "ReportCompositionService",
    "ReportSourceEligibilityProjector",
]
