from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from mdi_artifact_core import (
    ArtifactPayload,
    TRAJECTORY_FRAME_SCHEMA_VERSION,
    TRAJECTORY_MANIFEST_SCHEMA_VERSION,
    TRAJECTORY_SCHEMA_VERSION,
    TRAJECTORY_SUMMARY_SCHEMA_VERSION,
    stable_trajectory_json,
    trajectory_summary,
    validate_trajectory,
    validate_trajectory_manifest,
    validate_trajectory_summary,
)
from mdi_material_parsers.trajectory import TRAJECTORY_PARSE_REPORT_SCHEMA_VERSION
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


@dataclass(frozen=True)
class PreparedTrajectory:
    payload: dict[str, Any]
    parse_report: dict[str, Any]


@dataclass(frozen=True)
class TrajectoryImportResult:
    trajectory: dict[str, Any]
    summary: dict[str, Any]
    report: dict[str, Any]
    manifest: dict[str, Any]


class TrajectoryImportAdapter(BaseToolAdapter):
    """Planner-hidden adapter that emits inert validated trajectory artifacts."""

    tool_id = "structure.trajectory_import"
    adapter_version = "1.0.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedTrajectory:
        if params:
            raise ToolExecutionError(
                code="TOOL_PARAM_INVALID",
                message="Trajectory import accepts no post-parse normalization overrides.",
                tool_id=self.tool_id,
                details={"errorType": "trajectory_import_params_forbidden", "fields": sorted(params)},
            )
        if len(self._resolved_inputs) != 1:
            raise self._input_error("Trajectory import accepts exactly one normalized trajectory.", "trajectory_input_count_invalid")
        raw = self._resolved_inputs[0]
        payload = getattr(raw, "payload", raw)
        metadata = getattr(raw, "metadata", {})
        if isinstance(payload, dict) and "trajectory" in payload and isinstance(payload["trajectory"], dict):
            payload = payload["trajectory"]
        if not isinstance(payload, dict):
            raise self._input_error("Trajectory input is not a canonical JSON object.", "trajectory_input_invalid")
        validation = validate_trajectory(payload)
        if not validation.valid:
            raise self._input_error(
                "Trajectory input failed canonical validation.",
                "trajectory_contract_invalid",
                errors=list(validation.errors[:8]),
            )
        report = metadata.get("trajectoryParseReport") if isinstance(metadata, dict) else None
        if not _valid_parse_report(report, payload):
            report = _canonical_pass_through_report(payload)
        return PreparedTrajectory(payload=payload, parse_report=report)

    def run(self, prepared: PreparedTrajectory, params: dict[str, Any]) -> TrajectoryImportResult:
        trajectory = prepared.payload
        summary = trajectory_summary(trajectory)
        summary_validation = validate_trajectory_summary(summary)
        if not summary_validation.valid:
            raise ToolExecutionError(
                code="TOOL_CONTRACT_INVALID",
                message="Generated trajectory summary failed validation.",
                tool_id=self.tool_id,
                details={"errorType": "trajectory_summary_invalid", "errors": list(summary_validation.errors)},
            )
        trajectory_raw = stable_trajectory_json(trajectory).encode("utf-8")
        summary_raw = stable_trajectory_json(summary).encode("utf-8")
        manifest = {
            "schema_version": TRAJECTORY_MANIFEST_SCHEMA_VERSION,
            "trajectory_schema_version": TRAJECTORY_SCHEMA_VERSION,
            "frame_schema_version": TRAJECTORY_FRAME_SCHEMA_VERSION,
            "summary_schema_version": TRAJECTORY_SUMMARY_SCHEMA_VERSION,
            "trajectory_id": trajectory["trajectory_id"],
            "frame_count": len(trajectory["frames"]),
            "atom_count": trajectory["atoms"]["count"],
            "artifacts": [
                {"name": "trajectory.json", "media_type": "application/json", "bytes": len(trajectory_raw), "sha256": hashlib.sha256(trajectory_raw).hexdigest()},
                {"name": "trajectory_summary.json", "media_type": "application/json", "bytes": len(summary_raw), "sha256": hashlib.sha256(summary_raw).hexdigest()},
            ],
            "security": {"contains_javascript": False, "contains_html": False, "external_urls_allowed": False, "remote_frames_allowed": False, "executable_content_allowed": False},
        }
        manifest_validation = validate_trajectory_manifest(manifest)
        if not manifest_validation.valid:
            raise ToolExecutionError(
                code="TOOL_CONTRACT_INVALID",
                message="Generated trajectory manifest failed validation.",
                tool_id=self.tool_id,
                details={"errorType": "trajectory_manifest_invalid", "errors": list(manifest_validation.errors)},
            )
        return TrajectoryImportResult(trajectory=trajectory, summary=summary, report=prepared.parse_report, manifest=manifest)

    def export(self, result: TrajectoryImportResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        expected = {
            ArtifactType.trajectory_json,
            ArtifactType.trajectory_summary_json,
            ArtifactType.trajectory_report_json,
            ArtifactType.trajectory_manifest_json,
        }
        if set(artifact_types) != expected:
            raise ToolExecutionError(
                code="TOOL_INPUT_INVALID",
                message="Trajectory import requires its complete inert artifact set.",
                tool_id=self.tool_id,
                details={"errorType": "trajectory_artifact_set_invalid"},
            )
        payloads = [
            ArtifactPayload(ArtifactType.trajectory_json, "trajectory.json", stable_trajectory_json(result.trajectory), "application/json"),
            ArtifactPayload(ArtifactType.trajectory_summary_json, "trajectory_summary.json", stable_trajectory_json(result.summary), "application/json"),
            ArtifactPayload(ArtifactType.trajectory_report_json, "trajectory_parse_report.json", result.report, "application/json"),
            ArtifactPayload(ArtifactType.trajectory_manifest_json, "trajectory_manifest.json", result.manifest, "application/json"),
        ]
        return self.export_payloads(
            payloads,
            provenance={
                "trajectorySchemaVersion": TRAJECTORY_SCHEMA_VERSION,
                "parseReportSchemaVersion": TRAJECTORY_PARSE_REPORT_SCHEMA_VERSION,
                "deterministic": True,
                "rendererIncluded": False,
                "externalAssets": "none",
            },
        )

    def _input_error(self, message: str, error_type: str, **details: Any) -> ToolExecutionError:
        return ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message=message,
            tool_id=self.tool_id,
            details={"errorType": error_type, **details},
        )


def _valid_parse_report(report: Any, trajectory: dict[str, Any]) -> bool:
    fields = {
        "schema_version", "detected_format", "frames_read", "atoms_per_frame", "lattice_mode",
        "coordinate_mode", "properties_detected", "unit_conversions", "reordered_by_atom_id",
        "warnings", "input_sha256", "deterministic",
    }
    return (
        isinstance(report, dict)
        and set(report) == fields
        and report.get("schema_version") == TRAJECTORY_PARSE_REPORT_SCHEMA_VERSION
        and report.get("frames_read") == len(trajectory["frames"])
        and report.get("atoms_per_frame") == trajectory["atoms"]["count"]
        and report.get("lattice_mode") == trajectory["lattice_mode"]
        and report.get("coordinate_mode") == trajectory["coordinate_mode"]
        and report.get("deterministic") is True
        and isinstance(report.get("warnings"), list)
        and isinstance(report.get("unit_conversions"), list)
    )


def _canonical_pass_through_report(trajectory: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": TRAJECTORY_PARSE_REPORT_SCHEMA_VERSION,
        "detected_format": "canonical_json",
        "frames_read": len(trajectory["frames"]),
        "atoms_per_frame": trajectory["atoms"]["count"],
        "lattice_mode": trajectory["lattice_mode"],
        "coordinate_mode": trajectory["coordinate_mode"],
        "properties_detected": [key for key in ("positions", "velocities", "forces", "energy", "temperature") if trajectory["properties"][key]],
        "unit_conversions": [],
        "reordered_by_atom_id": False,
        "warnings": [],
        "input_sha256": trajectory["provenance"]["input_sha256"],
        "deterministic": True,
    }
