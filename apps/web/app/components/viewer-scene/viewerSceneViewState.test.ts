import { describe, expect, it } from "vitest";

import minimalScene from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_minimal_crystal.viewer_scene.v1.json";
import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import { buildViewerViewState, initialViewerClipState, replayViewerViewState, sceneClipBounds, validateViewerClipState } from "./viewerSceneViewState";
import type { ViewerRendererSnapshot } from "./viewerSceneRendererTypes";

function scene() { const result=mapViewerSceneForRenderer(minimalScene); if(!result.ok)throw new Error("fixture invalid"); return result.scene; }
function snapshot(): ViewerRendererSnapshot { return {state:"rendered",canvasCount:1,atomCount:1,bondCount:0,latticeEdgeCount:12,triangleCount:560,lineCount:12,cameraPosition:[8,8,8],cameraTarget:[0,0,0],cameraUp:[0,0,1],cameraZoom:1,cameraPreset:"isometric",activeClipPlanes:1,latticeAxesVisible:true,drawingBuffer:[720,480],graphicsContext:"webgl2",rendererVersion:"185",selectedSites:[],selectedSiteIndices:[],selectedBondId:null,siteScreenPositions:[],bondScreenPositions:[],metrics:{performanceTier:"interactive",atomCount:1,bondCount:0,speciesCount:1,instancedMeshCount:1,latticeEdgeCount:12,drawCalls:3,geometries:4,materials:4,triangles:560,lines:12,textures:0,bufferAttributes:3,sceneObjects:9,initializationMs:1,firstFrameMs:2}}; }

describe("viewer clipping and camera state",()=>{
  it("derives finite axis bounds and deterministic midpoint planes",()=>{
    const bounds=sceneClipBounds(scene()); const clip=initialViewerClipState(scene());
    expect(bounds.x[0]).toBeLessThan(bounds.x[1]);
    expect(clip.planes.map((plane)=>plane.axis)).toEqual(["x","y","z"]);
    expect(clip.planes.every((plane)=>Number.isFinite(plane.position))).toBe(true);
  });
  it("rejects arbitrary, out-of-range, and non-finite clipping input",()=>{
    const current=initialViewerClipState(scene());
    expect(()=>validateViewerClipState({...current,planes:[...current.planes,{axis:"x",position:0,enabled:true}]},scene())).toThrow("VIEWER_CLIP_STATE_INVALID");
    expect(()=>validateViewerClipState({...current,planes:current.planes.map((plane,index)=>index?plane:{...plane,position:Number.NaN})},scene())).toThrow("VIEWER_CLIP_STATE_INVALID");
    expect(()=>validateViewerClipState({...current,planes:current.planes.map((plane,index)=>index?plane:{...plane,position:1e9})},scene())).toThrow("VIEWER_CLIP_POSITION_OUT_OF_RANGE");
  });
  it("builds and replays inert scene-bound view state without executable fields",()=>{
    const current=initialViewerClipState(scene());
    const artifact=buildViewerViewState(scene(),{...current,enabled:true,planes:current.planes.map((plane,index)=>({...plane,enabled:index===0}))},{unitCell:true,supercellBoundary:true,latticeAxes:true},"isometric",snapshot());
    expect(artifact).toMatchObject({schema_version:"phase10f25.viewer_view_state.v1",camera:{preset:"isometric"},policy:{renderer_local:true,structure_mutated:false,canonical_topology_mutated:false},security:{inert_json:true,contains_javascript:false,external_urls:[]}});
    expect(replayViewerViewState(scene(),artifact)).toMatchObject({camera:{preset:"isometric"},display:{latticeAxes:true},clipping:{enabled:true}});
    expect(()=>replayViewerViewState(scene(),{...artifact,scene:{...artifact.scene,resource_id:"other"}})).toThrow("VIEWER_VIEW_STATE_INVALID");
  });
});
