import { describe, expect, it } from "vitest";
import { projectVolumetricSourceArtifacts } from "../../../scientific-viewers/ScientificViewerAdapter";
import { selectVolumetricField, restoredVolumetricField, sourceVolumetricChannel } from "../../../scientific-viewers/volumetric-viewer/volumetric-selection";
import { scientificSelectionFromWorkspace, apiSemanticLocator } from "../../../scientific-viewers/scientific-viewer/scientificSelection";
import type { ScientificWorkspace } from "../../lib/workspace-api";
import { encodeWorkspaceSelectionUrl } from "../../../shared/workspace/workspace-selection-contract";
import { datasetSourceSelection, selectedDatasetSourceResource, bindDatasetSourceSelection } from "../../../features/research/dataset-source-selection";

const hash = "a".repeat(64);
const resource = { objectId: "cube", versionId: "version-1", objectHash: hash, objectType: "VolumetricData", datasetId: "dataset-cube", payload: {
  source_format: "gaussian_cube", shape: [2, 2, 2], origin_cartesian: [0, 0, 0], step_matrix: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
  boundary_conditions: ["non_periodic", "non_periodic", "non_periodic"], sample_location: "node",
  channels: [0, 1].map(index => ({ name: `scalar-${index}`, quantity: "generic_scalar", canonical_unit: "dimensionless", values: Array.from({length: 8}, (_, i) => i + index) })),
} };
const workspace = { sourceJobId: "source-view", projectId: "project", datasetId: "dataset-cube", sourceReferenceHash: hash } as ScientificWorkspace;

describe("source volumetric field selection", () => {
  it("carries an uploaded field through source-hash selection into the admitted exact version", () => {
    const uploaded = { ...resource, versionId: undefined };
    const artifact = projectVolumetricSourceArtifacts(uploaded)![0];
    const mapping = (artifact.metadata!.sourceFields as {fieldId: string; channelId: string}[]).find(item => item.channelId === "channel:1")!;
    const context = selectVolumetricField(workspace, artifact, mapping.fieldId)!;
    expect(context?.primary).toMatchObject({ fieldId: "channel:1", datasetVersion: hash });
    expect(restoredVolumetricField(context, artifact)).toBe(mapping.fieldId);
    const token = encodeWorkspaceSelectionUrl(context);
    const selection = datasetSourceSelection("project", "dataset-cube", token)!;
    expect(selection.family).toBe("volumetric");
    expect(selectedDatasetSourceResource(selection, [{...uploaded, objectId:"same-values"}, uploaded])).toBe(uploaded);
    const promoted = {object:{id:"volume-object",project_id:"project",object_type:"volumetric.field"},version:{id:"exact-version",scientific_object_id:"volume-object",semantic_hash:hash,source_resource_refs_json:[{project_id:"project",dataset_id:"dataset-cube",resource_id:"cube"}]}};
    const bound = bindDatasetSourceSelection(selection, uploaded, promoted);
    expect(bound).toMatchObject({ object_ref:{object_id:"volume-object",version_id:"exact-version"},viewer_id:"scientific.volumetric",selection_type:"VOLUMETRIC_FIELD",semantic_locator:{field_id:"channel:1",source_channel_index:1,field_locator:"/channels/1"} });
    expect(bound.display_label).toContain("scalar-1");
    expect(() => datasetSourceSelection("foreign", "dataset-cube", token)).toThrow();
    expect(() => selectedDatasetSourceResource(selection, [uploaded, uploaded])).toThrow();
    expect(() => selectedDatasetSourceResource(selection, [{...uploaded,objectHash:"b".repeat(64)}])).toThrow();
    expect(() => selectedDatasetSourceResource(selection, [{...uploaded,payload:{...uploaded.payload,channels:uploaded.payload.channels.slice(0,1)}}])).toThrow();
    expect(() => bindDatasetSourceSelection(selection, uploaded, {...promoted,version:{...promoted.version,semantic_hash:"b".repeat(64)}})).toThrow();
    expect(() => bindDatasetSourceSelection(selection, uploaded, {...promoted,version:{...promoted.version,source_resource_refs_json:[]}})).toThrow();
    expect(selectVolumetricField(workspace, projectVolumetricSourceArtifacts({...uploaded,objectHash:undefined})![0], mapping.fieldId)).toBeNull();
  });
  it("maps renderer field identity to the original channel, survives sorting, and produces a bounded research locator", () => {
    const artifact = projectVolumetricSourceArtifacts(resource)![0];
    const mapping = (artifact.metadata!.sourceFields as {fieldId: string; channelId: string}[]).find(item => item.channelId === "channel:1")!;
    const context = selectVolumetricField(workspace, artifact, mapping.fieldId)!;
    expect(context.primary).toMatchObject({ fieldId: "channel:1", datasetVersion: "version-1", artifactChecksum: hash });
    expect(restoredVolumetricField(context, artifact)).toBe(mapping.fieldId);
    const scientific = scientificSelectionFromWorkspace(context, { projectId: "project", objectId: "cube", versionId: "version-1", objectType: "volumetric.field", displayName: "Cube" }, "volume", hash)!;
    expect(scientific.displayLabel).toBe("体数据字段 2");
    expect(apiSemanticLocator(scientific)).toEqual({ field_id: "channel:1" });
    expect(sourceVolumetricChannel(resource.payload, "channel:1")?.channel.name).toBe("scalar-1");
  });

  it("keeps equal-valued channels separately selectable", () => {
    const sameValues = {...resource, payload: {...resource.payload, channels: resource.payload.channels.map(channel => ({...channel, values: Array(8).fill(0)}))}};
    const artifact = projectVolumetricSourceArtifacts(sameValues)![0];
    const mappings = artifact.metadata!.sourceFields as {fieldId: string; channelId: string}[];
    expect(new Set(mappings.map(item => item.fieldId)).size).toBe(2);
    for (const mapping of mappings) {
      const selected = selectVolumetricField(workspace, artifact, mapping.fieldId)!;
      expect(selected.primary?.fieldId).toBe(mapping.channelId);
      expect(restoredVolumetricField(selected, artifact)).toBe(mapping.fieldId);
    }
  });

  it("rejects foreign, stale, unknown and ambiguous fields", () => {
    const artifact = projectVolumetricSourceArtifacts(resource)![0];
    const mappings = artifact.metadata!.sourceFields as {fieldId: string; channelId: string}[];
    const fieldId = mappings[0].fieldId;
    const context = selectVolumetricField(workspace, artifact, fieldId)!;
    expect(selectVolumetricField(workspace, artifact, "unknown")).toBeNull();
    expect(selectVolumetricField({...workspace, sourceReferenceHash: "b".repeat(64)}, artifact, fieldId)).toBeNull();
    expect(selectVolumetricField({...workspace, datasetId: "foreign"}, artifact, fieldId)).toBeNull();
    expect(selectVolumetricField(workspace, {...artifact, jobId: "result-job"}, fieldId)).toBeNull();
    expect(selectVolumetricField(workspace, {...artifact, metadata: {...artifact.metadata, sourceFields: [...mappings, mappings[0]]}}, fieldId)).toBeNull();
    expect(restoredVolumetricField(context, {...artifact, metadata: {...artifact.metadata, sourceVersionId: "version-2"}})).toBeNull();
    expect(restoredVolumetricField({...context, cleared: true}, artifact)).toBeNull();
    for (const id of ["channel:2", "channel:-1", "channel:01", "channel:1.0", "field:unknown"]) expect(sourceVolumetricChannel(resource.payload, id)).toBeNull();
  });
});
