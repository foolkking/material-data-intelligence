import type { Artifact } from "../../app/lib/planner-api";
import type { ScientificViewerProjection } from "../../app/lib/scientific-viewer-api";
import type { ScientificWorkspace, WorkspaceSelectionContext } from "../../app/lib/workspace-api";
import { validateWorkspaceSelectionContext } from "../../shared/workspace/workspace-selection-contract";
import { artifactChecksum, artifactIdentity } from "../../shared/workspace/workspace-renderer-registry";

/** A channel index addresses the immutable parser payload, not sorted renderer fields. */
export function sourceVolumetricChannel(payload: unknown, channelId: string | null) {
  const match = /^channel:(0|[1-9]\d*)$/.exec(channelId ?? "");
  const channels = record(payload)?.channels;
  if (!match || !Array.isArray(channels)) return null;
  const index = Number(match[1]);
  const channel = Number.isSafeInteger(index) ? record(channels[index]) : null;
  return channel && Array.isArray(channel.values) ? { index, channel } : null;
}

export function volumetricVersionLocator(context: WorkspaceSelectionContext, projection: ScientificViewerProjection) {
  const primary = context.primary;
  if (!primary || context.cleared || context.compatibility !== "EXACT" || context.secondary.length || primary.kind !== "VOLUMETRIC_FIELD" ||
      !["volumetric.field", "volumetric.charge_density"].includes(projection.object_type) || projection.payload_status !== "READY" ||
      primary.projectId !== projection.project_id || primary.datasetVersion !== projection.version_id ||
      primary.artifactId !== `source:${projection.object_id}:volumetric-dataset` || primary.artifactChecksum !== projection.content_hash ||
      context.sourceScopeHash !== projection.content_hash || primary.datasetId !== String(projection.source_resource_refs[0]?.dataset_id || projection.object_id)) return null;
  const channel = sourceVolumetricChannel(projection.payload, primary.fieldId);
  return channel ? { field_id: `channel:${channel.index}`, source_channel_index: channel.index, field_locator: `/channels/${channel.index}` } : null;
}

function sourceFields(artifact: Artifact) {
  const metadata = artifact.metadata;
  const fields = record(artifact.content)?.fields;
  const mappings = metadata?.sourceFields;
  if (artifact.type !== "volumetric_dataset_json" || artifact.jobId !== "source-view" ||
      !metadata?.sourceObjectId || !metadata.sourceVersionId || !artifactChecksum(artifact) ||
      artifactIdentity(artifact) !== `source:${metadata.sourceObjectId}:volumetric-dataset` ||
      !Array.isArray(fields) || !Array.isArray(mappings)) return [];
  return mappings.flatMap((value) => {
    const mapping = record(value);
    if (typeof mapping?.fieldId !== "string" || typeof mapping.channelId !== "string" || !/^channel:(0|[1-9]\d*)$/.test(mapping.channelId) ||
        fields.filter(field => record(field)?.field_id === mapping.fieldId).length !== 1 ||
        mappings.filter(item => record(item)?.fieldId === mapping.fieldId || record(item)?.channelId === mapping.channelId).length !== 1) return [];
    return [{ fieldId: mapping.fieldId, channelId: mapping.channelId }];
  });
}

export function selectVolumetricField(workspace: ScientificWorkspace, artifact: Artifact, fieldId: string): WorkspaceSelectionContext | null {
  const mapping = sourceFields(artifact).find(item => item.fieldId === fieldId);
  const checksum = artifactChecksum(artifact);
  if (!mapping || workspace.sourceJobId !== "source-view" || !workspace.datasetId ||
      workspace.datasetId !== artifact.metadata?.sourceDatasetId || workspace.sourceReferenceHash !== checksum) return null;
  return validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: checksum,
    primary: { selectionSchemaVersion: "1.0", kind: "VOLUMETRIC_FIELD", sourceScopeHash: checksum,
      projectId: workspace.projectId, datasetId: workspace.datasetId, datasetVersion: artifact.metadata?.sourceVersionId,
      artifactId: artifactIdentity(artifact), artifactChecksum: checksum, fieldId: mapping.channelId },
    secondary: [], compatibility: "EXACT", propagation: "EXACT_COMPATIBLE_ONLY", cleared: false });
}

export function restoredVolumetricField(context: WorkspaceSelectionContext | null | undefined, artifact: Artifact): string | null {
  const primary = context?.primary;
  if (!primary || context.cleared || context.compatibility !== "EXACT" || context.secondary.length || primary.kind !== "VOLUMETRIC_FIELD" ||
      primary.artifactId !== artifactIdentity(artifact) || primary.artifactChecksum !== artifactChecksum(artifact) ||
      context.sourceScopeHash !== artifactChecksum(artifact) || primary.datasetVersion !== artifact.metadata?.sourceVersionId ||
      primary.datasetId !== artifact.metadata?.sourceDatasetId) return null;
  return sourceFields(artifact).find(item => item.channelId === primary.fieldId)?.fieldId ?? null;
}

function record(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null;
}
