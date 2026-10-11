import type { Artifact } from "../../app/lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext } from "../../app/lib/workspace-api";
import type { ScientificViewerProjection } from "../../app/lib/scientific-viewer-api";
import { validateWorkspaceSelectionContext } from "../../shared/workspace/workspace-selection-contract";
import { artifactChecksum, artifactIdentity } from "../../shared/workspace/workspace-renderer-registry";
import type { PeriodicSiteRef } from "../viewer-scene/viewerSceneRendererTypes";
import { validateTrajectoryForViewer } from "./trajectoryFrameMapper";

export type TrajectoryPoint = Readonly<{frameIndex: number; atom: PeriodicSiteRef | null}>;

export function trajectoryPointIds(point: TrajectoryPoint) {
  return {frameId: `frame:${point.frameIndex}`, atomId: point.atom ? `atom:${point.atom.siteIndex}:${point.atom.imageOffset.join(".")}` : null};
}

export function parseTrajectoryPoint(frameId: string | null, atomId: string | null): TrajectoryPoint | null {
  const match = /^frame:(0|[1-9]\d*)$/.exec(frameId || "");
  const frameIndex = Number(match?.[1]);
  if (!match || !Number.isSafeInteger(frameIndex)) return null;
  if (atomId === null) return {frameIndex, atom: null};
  const atom = /^atom:(0|[1-9]\d*):([0-2])\.([0-2])\.([0-2])$/.exec(atomId);
  if (!atom || !Number.isSafeInteger(Number(atom[1]))) return null;
  return {frameIndex, atom: {siteIndex: Number(atom[1]), imageOffset: [Number(atom[2]), Number(atom[3]), Number(atom[4])]}};
}

/** Indices address the original trajectory, never a playback counter or sampled frame. */
export function trajectoryPoint(payload: unknown, frameId: string | null, atomId: string | null, trajectoryId?: string | null) {
  const point = parseTrajectoryPoint(frameId, atomId), validation = validateTrajectoryForViewer(payload);
  if (!point || !validation.ok || (trajectoryId !== undefined && validation.trajectory.trajectory_id !== trajectoryId)) return null;
  const trajectory = validation.trajectory, frame = trajectory.frames[point.frameIndex];
  if (!frame || frame.frame_index !== point.frameIndex) return null;
  const atom = point.atom ? trajectory.atoms.records[point.atom.siteIndex] : null;
  if (point.atom && (!atom || atom.atom_id !== point.atom.siteIndex || !frame.positions[point.atom.siteIndex])) return null;
  return {point, trajectory, frame, atom};
}

export function trajectoryPointLabel(point: TrajectoryPoint) {
  return `第 ${point.frameIndex + 1} 帧${point.atom ? ` · 原子 ${point.atom.siteIndex + 1}${point.atom.imageOffset.some(value => value !== 0) ? ` · 周期位置 [${point.atom.imageOffset.join(", ")}]` : ""}` : ""}`;
}

export function selectTrajectoryPoint(workspace: ScientificWorkspace, artifact: Artifact, point: TrajectoryPoint): WorkspaceSelectionContext | null {
  const id = artifactIdentity(artifact), checksum = artifactChecksum(artifact), metadata = artifact.metadata, ids = trajectoryPointIds(point);
  const source = trajectoryPoint(artifact.content, ids.frameId, ids.atomId);
  if (!source || workspace.sourceJobId !== "source-view" || !workspace.datasetId || artifact.jobId !== "source-view" || !checksum ||
      !metadata?.sourceObjectId || id !== `source:${metadata.sourceObjectId}` || metadata.sourceDatasetId !== workspace.datasetId) return null;
  return validateWorkspaceSelectionContext({schemaVersion: "1.0", sourceScopeHash: checksum,
    primary: {selectionSchemaVersion: "1.0", kind: point.atom ? "TRAJECTORY_ATOM" : "TRAJECTORY_FRAME", sourceScopeHash: checksum, projectId: workspace.projectId,
      datasetId: workspace.datasetId, datasetVersion: metadata.sourceVersionId || checksum, trajectoryId: source.trajectory.trajectory_id,
      artifactId: id, artifactChecksum: checksum, ...ids},
    secondary: [], compatibility: "EXACT", propagation: "EXACT_COMPATIBLE_ONLY", cleared: false});
}

export function restoredTrajectoryPoint(context: WorkspaceSelectionContext | null | undefined, artifact: Artifact): TrajectoryPoint | null {
  const primary = context?.primary;
  if (!primary || context.cleared || context.compatibility !== "EXACT" || context.secondary.length ||
      !["TRAJECTORY_FRAME", "TRAJECTORY_ATOM"].includes(primary.kind) || primary.artifactId !== artifactIdentity(artifact) ||
      primary.artifactChecksum !== artifactChecksum(artifact) || primary.datasetId !== artifact.metadata?.sourceDatasetId ||
      primary.datasetVersion !== (artifact.metadata?.sourceVersionId || artifactChecksum(artifact)) ||
      (primary.kind === "TRAJECTORY_ATOM") !== Boolean(primary.atomId)) return null;
  return trajectoryPoint(artifact.content, primary.frameId, primary.atomId, primary.trajectoryId)?.point ?? null;
}

export function trajectorySemanticLocator(payload: unknown, frameId: string | null, atomId: string | null, trajectoryId?: string | null): Record<string, string | number> | null {
  const source = trajectoryPoint(payload, frameId, atomId, trajectoryId);
  if (!source) return null;
  const {point, trajectory, frame, atom} = source;
  const position = point.atom ? frame.positions[point.atom.siteIndex] : null;
  return {frame_id: frameId!, frame_index: point.frameIndex,
    ...(frame.time !== null && trajectory.time.unit ? {time: frame.time, time_unit: trajectory.time.unit} : {}),
    ...(frame.step !== null ? {step: frame.step} : {}),
    ...(point.atom && atom && position ? {atom_id: atomId!, atom_index: atom.atom_id, species: atom.species,
      coordinate_mode: trajectory.coordinate_mode, position_unit: trajectory.coordinate_mode === "cartesian" ? "angstrom" : "fractional",
      source_x: position[0], source_y: position[1], source_z: position[2],
      image_offset_a: point.atom.imageOffset[0], image_offset_b: point.atom.imageOffset[1], image_offset_c: point.atom.imageOffset[2]} : {})};
}

export function trajectoryVersionLocator(context: WorkspaceSelectionContext, projection: ScientificViewerProjection) {
  const primary = context.primary;
  if (!primary || context.cleared || context.compatibility !== "EXACT" || context.secondary.length ||
      !["TRAJECTORY_FRAME", "TRAJECTORY_ATOM"].includes(primary.kind) || projection.object_type !== "trajectory.atomic" || projection.payload_status !== "READY" ||
      primary.projectId !== projection.project_id || primary.datasetVersion !== projection.version_id || primary.artifactId !== `source:${projection.object_id}` ||
      primary.datasetId !== String(projection.source_resource_refs[0]?.dataset_id || projection.object_id) ||
      primary.artifactChecksum !== projection.content_hash || context.sourceScopeHash !== projection.content_hash ||
      (primary.kind === "TRAJECTORY_ATOM") !== Boolean(primary.atomId)) return null;
  return trajectorySemanticLocator(projection.payload, primary.frameId, primary.atomId, primary.trajectoryId);
}
