import { afterEach, expect, it, vi } from "vitest";
import type * as Three from "three";
import { createVolumetricSliceRendererEngine } from "./volumetricSliceRendererEngine";
import { createVolumetricVolumeRendererEngine } from "./volumetricVolumeRendererEngine";
import type { ValidatedVolumetricGrid, VolumeTransferFunction, VolumetricSlice, VolumetricStructureOverlay } from "./volumetricViewerTypes";

const draws = vi.hoisted(() => [] as Array<{atoms:number; cells:number; volume:boolean; depth:boolean}>);
vi.mock("three", async importOriginal => {
  const actual = await importOriginal<typeof Three>();
  return {...actual, WebGLRenderer: class {
    domElement: HTMLCanvasElement;
    info = {render:{calls:0}};
    constructor(args: {canvas?:HTMLCanvasElement}) {this.domElement=args.canvas || document.createElement("canvas");}
    setClearColor() {} setPixelRatio() {} getPixelRatio() {return 1;} setSize() {} setRenderTarget() {} clear() {} forceContextLoss() {} dispose() {}
    render(scene: Three.Scene) {
      let atoms=0, cells=0, volume=false, depth=false;
      scene.traverseVisible(object => {
        if (object instanceof actual.InstancedMesh) atoms++;
        if (object instanceof actual.LineSegments) cells++;
        if (object instanceof actual.Mesh && object.material instanceof actual.RawShaderMaterial) {
          volume=true; depth=object.material.uniforms.uHasStructureDepth.value;
        }
      });
      draws.push({atoms,cells,volume,depth});
    }
  }};
});
vi.mock("three/examples/jsm/controls/OrbitControls.js", async () => {
  const {Vector3}=await import("three");
  return {OrbitControls:class {target=new Vector3(); update() {} dispose() {} addEventListener() {} removeEventListener() {}}};
});
vi.mock("./volumetricVolumeShader", () => ({validateVolumeShaderProgram:vi.fn(),VOLUME_FRAGMENT_SHADER:"",VOLUME_VERTEX_SHADER:"",VOLUME_SHADER_VERSION:"test"}));
vi.mock("./volumetricVolumeModel", async importOriginal => ({...await importOriginal<object>(), inspectVolumeGpuCapabilities:()=>({supported:true,textureShape:[2,2,2],textureBytes:32})}));

const grid: ValidatedVolumetricGrid = {schemaVersion:"phase10j.volumetric_grid.v1",gridId:"grid",contentHash:"a".repeat(64),shape:[2,2,2],origin:[0,0,0],stepMatrix:[[1,0,0],[0,1,0],[0,0,1]],sampleLocation:"node",boundaryConditions:["periodic","periodic","periodic"],endpointPolicy:"excluded",periodic:true,structureBinding:null};
const transferFunction: VolumeTransferFunction = {version:"phase10j6.transfer_function.v1",presetId:"nonnegative_medium",windowLow:0,windowHigh:2,opacityScale:1,paletteId:"viridis",zeroPolicy:"none"};
const overlay = {atoms:[{position:[0,0,0],radius:0.2,color:0x009988,species:"C"}],bonds:[]} as unknown as VolumetricStructureOverlay;
const slice = {outputShape:[2,2],values:new Float64Array(4).fill(1),plane:{origin:[0,0,1],basisU:[2,0,0],basisV:[0,2,0]}} as unknown as VolumetricSlice;
afterEach(() => {vi.restoreAllMocks();draws.length=0;});

it.each(["slice","volume"])("%s renders structure and cell independently in every toggle combination", async mode => {
  vi.spyOn(HTMLCanvasElement.prototype,"getContext").mockReturnValue({} as WebGL2RenderingContext);
  const args={container:document.createElement("div"),grid,transferFunction,overlay,onContextLost:vi.fn()};
  const engine=mode==="slice" ? await createVolumetricSliceRendererEngine({...args,slice,onProbe:vi.fn()})
    : (await createVolumetricVolumeRendererEngine({...args,values:new Float32Array(8),quality:{id:"low",samplesPerVoxel:1,maximumRaySteps:64,pixelRatioCap:1}})).engine;
  try {
    for (const [structure,cell] of [[false,true],[true,false],[false,false],[true,true]]) {
      engine.setStructureVisible(structure);
      draws.length=0;
      engine.setCellVisible(cell);
      expect(draws.some(draw=>draw.atoms>0)).toBe(structure);
      expect(draws.some(draw=>draw.cells>0)).toBe(cell);
      if (mode==="volume") {
        expect(draws.at(-1)).toEqual({atoms:0,cells:0,volume:true,depth:structure||cell});
        expect(draws.length).toBe(structure||cell ? 3 : 1);
      }
    }
  } finally {engine.dispose();}
  expect(args.container.querySelector("canvas")).toBeNull();
});
