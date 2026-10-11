import { describe, expect, it } from "vitest";
import fixed from "../../../../tests/fixtures/trajectory_viewer/fixed_lattice_md_12_frames.json";
import type { ScientificWorkspace } from "../../app/lib/workspace-api";
import type { ScientificViewerProjection } from "../../app/lib/scientific-viewer-api";
import { sourceResourceArtifact } from "../ScientificViewerAdapter";
import { encodeWorkspaceSelectionUrl, decodeWorkspaceSelectionUrl } from "../../shared/workspace/workspace-selection-contract";
import { datasetSourceSelection, selectedDatasetSourceResource, bindDatasetSourceSelection } from "../../features/research/dataset-source-selection";
import { parseTrajectoryPoint, selectTrajectoryPoint, restoredTrajectoryPoint, trajectoryVersionLocator } from "./trajectory-selection";

const hash = "a".repeat(64);
const resource = {objectId:"trajectory_resource",datasetId:"dataset_1",objectType:"Trajectory",objectHash:hash,versionId:"source_v1",payload:fixed};
const artifact = sourceResourceArtifact(resource);
const workspace = {projectId:"project_1",datasetId:resource.datasetId,datasetVersion:resource.versionId,sourceJobId:"source-view",sourceReferenceHash:hash} as ScientificWorkspace;
const promoted = {object:{id:"trajectory_object",project_id:"project_1",object_type:"trajectory.atomic"},version:{id:"exact_version",scientific_object_id:"trajectory_object",semantic_hash:hash,source_resource_refs_json:[{project_id:"project_1",dataset_id:resource.datasetId,resource_id:resource.objectId}]}};

describe("trajectory selection to Research", () => {
  it.each([null, {siteIndex:1,imageOffset:[1,0,1] as const}])("preserves the original frame and periodic atom through URL and admission: %j", atom => {
    const point = {frameIndex:5,atom};
    const context = selectTrajectoryPoint(workspace,artifact,point)!;
    const token = encodeWorkspaceSelectionUrl(context);
    expect(restoredTrajectoryPoint(decodeWorkspaceSelectionUrl(token),artifact)).toEqual(point);
    const selection = datasetSourceSelection("project_1",resource.datasetId,token)!;
    expect(selectedDatasetSourceResource(selection,[{...resource,objectId:"other"},resource])).toBe(resource);
    const bound = bindDatasetSourceSelection(selection,resource,promoted);
    expect(bound.object_ref).toMatchObject({object_id:"trajectory_object",version_id:"exact_version",object_type:"trajectory.atomic"});
    expect(bound.semantic_locator).toMatchObject({frame_id:"frame:5",frame_index:5,time:fixed.frames[5].time,time_unit:fixed.time.unit,step:fixed.frames[5].step});
    expect(bound.evidence_locator).toEqual(bound.semantic_locator);
    if(atom) expect(bound.semantic_locator).toMatchObject({atom_id:"atom:1:1.0.1",atom_index:1,species:fixed.atoms.records[1].species,source_x:fixed.frames[5].positions[1][0],image_offset_a:1,image_offset_c:1});
    else expect(bound.semantic_locator).not.toHaveProperty("atom_index");
  });
  it.each(["objectHash","versionId","datasetId","objectType"])("rejects changed source %s before admission", field => {
    const context = selectTrajectoryPoint(workspace,artifact,{frameIndex:5,atom:null})!;
    const selection = datasetSourceSelection("project_1",resource.datasetId,encodeWorkspaceSelectionUrl(context))!;
    expect(() => selectedDatasetSourceResource(selection,[{...resource,[field]:"foreign"}])).toThrow();
  });
  it("rejects a missing frame, foreign trajectory and missing atom", () => {
    expect(selectTrajectoryPoint(workspace,artifact,{frameIndex:fixed.frames.length,atom:null})).toBeNull();
    expect(selectTrajectoryPoint(workspace,artifact,{frameIndex:0,atom:{siteIndex:fixed.atoms.count,imageOffset:[0,0,0]}})).toBeNull();
    const context=selectTrajectoryPoint(workspace,artifact,{frameIndex:0,atom:null})!;
    expect(restoredTrajectoryPoint({...context,primary:{...context.primary!,trajectoryId:"foreign"}},artifact)).toBeNull();
  });
  it.each([["frame:-1",null],["frame:01",null],["frame:9007199254740992",null],["frame:1","atom:1:3.0.0"],["frame:1","atom:1:-1.0.0"]])("rejects malformed source indices %s %s", (frame,atom) => {
    expect(parseTrajectoryPoint(frame,atom)).toBeNull();
  });
  it("rereads the exact version to bind scientific coordinates and rejects foreign projections", () => {
    const versionResource={...resource,objectId:"trajectory_object",versionId:"exact_version"};
    const context=selectTrajectoryPoint({...workspace,datasetVersion:"exact_version"},sourceResourceArtifact(versionResource),{frameIndex:5,atom:{siteIndex:1,imageOffset:[0,0,0]}})!;
    const projection: ScientificViewerProjection = {
      contract_version: "1.0", project_id: "project_1", object_id: "trajectory_object",
      version_id: "exact_version", object_type: "trajectory.atomic", object_schema_version: "1.0",
      display_name: "Trajectory", version_no: 1, is_current_version: true, availability_status: "AVAILABLE",
      viewer: { viewer_id: "trajectory.atomic", viewer_version: "1.0", renderer_key: "trajectory",
        support: "SUPPORTED", interaction_capabilities: [], selection_capabilities: [],
        maximum_payload_bytes: 2_000_000, fallback_policy: "METADATA_ONLY" },
      payload_status: "READY", payload: fixed, content_hash: hash, semantic_hash: hash,
      source_resource_refs: [{ dataset_id: resource.datasetId }], canonical_metadata: {},
      payload_bytes: null, omitted_item_count: 0, limitations: [],
    };
    expect(trajectoryVersionLocator(context,projection)).toMatchObject({frame_index:5,atom_index:1,source_x:fixed.frames[5].positions[1][0]});
    for(const field of ["project_id","version_id","object_id","content_hash","object_type","payload_status"]) expect(trajectoryVersionLocator(context,{...projection,[field]:"foreign"})).toBeNull();
  });
});
