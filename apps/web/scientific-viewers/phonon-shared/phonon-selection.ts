import type { Artifact } from "../../app/lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext } from "../../app/lib/workspace-api";
import { validatePhononBandReference, validatePhononDosReference } from "../../app/lib/phononContract";
import { validateWorkspaceSelectionContext } from "../../shared/workspace/workspace-selection-contract";
import { artifactChecksum, artifactIdentity } from "../../shared/workspace/workspace-renderer-registry";

export type PhononBandPoint = Readonly<{ qpointIndex: number; branchIndex: number }>;
export type PhononDosPoint = Readonly<{ frequencyIndex: number; projectionIndex: number | null }>;

/** A DOS sample is a frequency-grid point and a total/projection channel, never a q point. */
export function phononDosPoint(payload: unknown, frequencyPointId: string | null, dosChannelId: string | null) {
  const frequencyIndex = index(frequencyPointId, "frequency:");
  const projectionIndex = dosChannelId === "total" ? null : index(dosChannelId, "projection:");
  if (frequencyIndex === null || (dosChannelId !== "total" && projectionIndex === null) || !validatePhononDosReference(payload).valid) return null;
  const dos = payload as { frequencies: number[]; total_dos: number[]; projected_dos: {projection_index: number; projection_type: string; atom_index: number | null; species: string; values: number[]}[] };
  const projection = projectionIndex === null ? null : dos.projected_dos.find(item => item.projection_index === projectionIndex);
  if (projectionIndex !== null && !projection) return null;
  const frequency = dos.frequencies[frequencyIndex], density = (projection ? projection.values : dos.total_dos)[frequencyIndex];
  if (!Number.isFinite(frequency) || !Number.isFinite(density)) return null;
  return { frequencyIndex, projectionIndex, frequency, density, projection: projection ?? null };
}

export function selectPhononDosPoint(workspace: ScientificWorkspace, artifact: Artifact, point: PhononDosPoint): WorkspaceSelectionContext | null {
  const id = artifactIdentity(artifact), checksum = artifactChecksum(artifact), metadata = artifact.metadata;
  const frequencyPointId = `frequency:${point.frequencyIndex}`, dosChannelId = point.projectionIndex === null ? "total" : `projection:${point.projectionIndex}`;
  if (workspace.sourceJobId !== "source-view" || !workspace.datasetId || artifact.jobId !== "source-view" || !checksum ||
      !metadata?.sourceObjectId || id !== `source:${metadata.sourceObjectId}` || metadata.sourceDatasetId !== workspace.datasetId ||
      !phononDosPoint(artifact.content, frequencyPointId, dosChannelId)) return null;
  return validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: checksum,
    primary: { selectionSchemaVersion: "1.0", kind: "PHONON_DOS_POINT", sourceScopeHash: checksum, projectId: workspace.projectId,
      datasetId: workspace.datasetId, datasetVersion: metadata.sourceVersionId || checksum, phononArtifactId: id,
      artifactChecksum: checksum, frequencyPointId, dosChannelId },
    secondary: [], compatibility: "EXACT", propagation: "EXACT_COMPATIBLE_ONLY", cleared: false });
}

export function restoredPhononDosPoint(context: WorkspaceSelectionContext | null | undefined, artifact: Artifact): PhononDosPoint | null {
  const primary = context?.primary;
  if (!primary || context.cleared || context.compatibility !== "EXACT" || context.secondary.length || primary.kind !== "PHONON_DOS_POINT" ||
      primary.phononArtifactId !== artifactIdentity(artifact) || primary.artifactChecksum !== artifactChecksum(artifact)) return null;
  return phononDosPoint(artifact.content, primary.frequencyPointId, primary.dosChannelId);
}

/** IDs address the original arrays, never a sampled plot's point index. */
export function phononBandPoint(payload: unknown, qPointId: string | null, branchId: string | null) {
  const qpointIndex = index(qPointId, "q:"), branchIndex = index(branchId, "branch:");
  if (qpointIndex === null || branchIndex === null || !validatePhononBandReference(payload).valid) return null;
  const band = payload as { qpoints: {index: number; coordinates: number[]; distance: number}[]; branches: {branch_index: number; frequencies: number[]}[] };
  const points = band.qpoints.filter(point => point.index === qpointIndex);
  const branches = band.branches.filter(branch => branch.branch_index === branchIndex);
  const frequency = branches[0]?.frequencies[qpointIndex];
  if (points.length !== 1 || branches.length !== 1 || !Number.isFinite(frequency)) return null;
  return { qpointIndex, branchIndex, frequency, distance: points[0].distance, coordinates: points[0].coordinates };
}

export function selectPhononBandPoint(workspace: ScientificWorkspace, artifact: Artifact, point: PhononBandPoint): WorkspaceSelectionContext | null {
  const id = artifactIdentity(artifact), checksum = artifactChecksum(artifact), metadata = artifact.metadata;
  if (workspace.sourceJobId !== "source-view" || !workspace.datasetId || artifact.jobId !== "source-view" || !checksum ||
      !metadata?.sourceObjectId || id !== `source:${metadata.sourceObjectId}` || metadata.sourceDatasetId !== workspace.datasetId ||
      !phononBandPoint(artifact.content, `q:${point.qpointIndex}`, `branch:${point.branchIndex}`)) return null;
  return validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: checksum,
    primary: { selectionSchemaVersion: "1.0", kind: "PHONON_Q_POINT", sourceScopeHash: checksum, projectId: workspace.projectId,
      datasetId: workspace.datasetId, datasetVersion: metadata.sourceVersionId || checksum, phononArtifactId: id,
      artifactChecksum: checksum, qPointId: `q:${point.qpointIndex}`, branchId: `branch:${point.branchIndex}` },
    secondary: [], compatibility: "EXACT", propagation: "EXACT_COMPATIBLE_ONLY", cleared: false });
}

export function restoredPhononBandPoint(context: WorkspaceSelectionContext | null | undefined, artifact: Artifact): PhononBandPoint | null {
  const primary = context?.primary;
  if (!primary || context.cleared || context.compatibility !== "EXACT" || context.secondary.length || primary.kind !== "PHONON_Q_POINT" ||
      primary.phononArtifactId !== artifactIdentity(artifact) || primary.artifactChecksum !== artifactChecksum(artifact)) return null;
  return phononBandPoint(artifact.content, primary.qPointId, primary.branchId);
}

function index(value: string | null, prefix: string): number | null {
  const suffix = value?.startsWith(prefix) ? value.slice(prefix.length) : "";
  const number = Number(suffix);
  return /^(0|[1-9]\d*)$/.test(suffix) && Number.isSafeInteger(number) ? number : null;
}
