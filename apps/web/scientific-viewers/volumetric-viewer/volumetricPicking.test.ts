import { afterEach, expect, it, vi } from "vitest";
import * as THREE from "three";
import { createVolumetricRendererEngine } from "./volumetricRendererEngine";
import type { IsosurfaceMesh, ValidatedVolumetricGrid } from "./volumetricViewerTypes";

vi.mock("three", async importOriginal => {
  const actual = await importOriginal<typeof import("three")>();
  return { ...actual, WebGLRenderer: class {
    domElement = document.createElement("canvas");
    info = { render:{calls:1}, memory:{geometries:1} };
    setPixelRatio() {} setSize() {} setClearColor() {} render() {} dispose() {} forceContextLoss() {}
  }};
});
vi.mock("three/addons/controls/OrbitControls.js", async () => {
  const { Vector3 } = await import("three");
  return { OrbitControls: class { target = new Vector3(); update() {} dispose() {} addEventListener() {} removeEventListener() {} } };
});
afterEach(() => { vi.restoreAllMocks(); document.body.replaceChildren(); });
it("picks only a visible surface on a tap and skips clipped intersections without changing source identity", async () => {
  const container = document.createElement("div"); document.body.append(container);
  const grid: ValidatedVolumetricGrid = { schemaVersion:"phase10j.volumetric_grid.v1",gridId:"grid",contentHash:"a".repeat(64),shape:[2,2,2],origin:[0,0,0],stepMatrix:[[1,0,0],[0,1,0],[0,0,1]],sampleLocation:"node",boundaryConditions:["non_periodic","non_periodic","non_periodic"],endpointPolicy:"included",periodic:false,structureBinding:null };
  const mesh: IsosurfaceMesh = {layerId:"surface-exact",isovalue:0.25,positions:new Float32Array([0,0,0,1,0,0,0,1,0]),normals:new Float32Array([0,0,1,0,0,1,0,0,1]),indices:new Uint32Array([0,1,2]),vertexCount:3,triangleCount:1,boundingBox:{minimum:[0,0,0],maximum:[1,1,0]},meshHash:"b".repeat(64),warnings:[]};
  const onSurfacePick=vi.fn(), onAtomPick=vi.fn();
  const engine = await createVolumetricRendererEngine({container,grid,fieldId:"field-exact",meshes:[mesh],overlay:null,onSurfacePick,onAtomPick,onContextLost:vi.fn()});
  const canvas = container.querySelector("canvas")!;
  canvas.getBoundingClientRect=()=>({left:0,top:0,right:200,bottom:200,width:200,height:200}) as DOMRect;
  const intersections = vi.spyOn(THREE.Raycaster.prototype,"intersectObjects").mockImplementation(objects => objects.map(object=>[
    {object,faceIndex:0,point:new THREE.Vector3(1,2,-1)}, {object,faceIndex:1,point:new THREE.Vector3(1,2,1)},
  ]).flat() as THREE.Intersection[]);
  const pointer=(type:string,x=50)=>{const event=new Event(type,{bubbles:true});Object.assign(event,{pointerId:1,button:0,isPrimary:true,clientX:x,clientY:50});canvas.dispatchEvent(event);};
  try {
    pointer("pointerdown"); pointer("pointermove",80); pointer("pointerup",80);
    expect(intersections).not.toHaveBeenCalled();
    engine.setClipping(true,2,0);
    pointer("pointerdown"); pointer("pointerup");
    expect(onSurfacePick).toHaveBeenLastCalledWith(expect.objectContaining({fieldId:"field-exact",layerId:mesh.layerId,isovalue:0.25,meshHash:mesh.meshHash,triangleIndex:1,cartesianPosition:[1,2,1]}));
    expect(onAtomPick).toHaveBeenLastCalledWith(null);
    engine.setLayerVisible(mesh.layerId,false);
    pointer("pointerdown"); pointer("pointerup"); expect(onSurfacePick).toHaveBeenLastCalledWith(null);
    engine.dispose(); onSurfacePick.mockClear(); pointer("pointerdown"); pointer("pointerup"); expect(onSurfacePick).not.toHaveBeenCalled();
  } finally { engine.dispose(); }
});
