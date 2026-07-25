import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import manifest from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/manifest.json";
import reciprocal from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/reciprocal_lattice.json";
import zone from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/brillouin_zone.json";
import kpath from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/kpath.json";
import { BrillouinZoneSurface } from "./BrillouinZoneSurface";
import type { BZRendererEngine, BZRendererEngineFactory, BZRendererSnapshot } from "./brillouinZoneTypes";

const bundle = {reciprocal,zone,kpath,manifest};

function fakeEngine(dispose=vi.fn()) {
  let projection: "perspective"|"orthographic"="perspective";
  let selection: BZRendererSnapshot["selection"]=null;
  const snapshot=():BZRendererSnapshot=>({state:"rendered",graphicsContext:"webgl2",rendererVersion:"185",projection,cameraPosition:[5,5,5],cameraTarget:[0,0,0],cameraUp:[0,0,1],selection,pointScreenPositions:[{id:kpath.points[0].point_id,x:100,y:90}],faceScreenPositions:[{id:zone.faces[0].face_id,x:80,y:80}],metrics:{artifactBytes:8000,vertexCount:8,edgeCount:12,faceCount:6,triangleCount:12,pointCount:kpath.points.length,pathSegmentCount:kpath.segments.length,visibleLabelCount:kpath.points.length,drawCalls:7,geometries:7,materials:8,textures:0,canvasCount:1,contextCount:1,mappingMs:2,initializationMs:4,firstFrameMs:5}});
  const engine:BZRendererEngine={resetCamera:vi.fn(),fit:vi.fn(),setCameraPreset:vi.fn(),setProjection:vi.fn((value)=>{projection=value;}),setVisibility:vi.fn(),setOpacity:vi.fn(),setVariant:vi.fn(),setSelection:vi.fn((value)=>{selection=value;}),keyboardCamera:vi.fn(),exportPng:vi.fn(async()=>new Blob([new Uint8Array([137,80,78,71])],{type:"image/png"})),snapshot,dispose};
  return engine;
}

describe("BrillouinZoneSurface",()=>{
  it("initializes only after validation and drives layers, opacity, projection, camera, selection and inspector by canonical IDs",async()=>{
    const engine=fakeEngine();let args:Parameters<BZRendererEngineFactory>[0]|undefined;
    render(<BrillouinZoneSurface bundle={bundle} capabilityOverride engineFactory={async(value)=>{args=value;return engine;}}/>);
    await waitFor(()=>expect(screen.getByTestId("brillouin-zone-renderer-state")).toHaveTextContent("rendered"));
    expect(args?.scene.vertices[0].id).toBe(zone.vertices[0].vertex_id);
    await userEvent.click(screen.getByRole("button",{name:"faces"}));expect(engine.setVisibility).toHaveBeenLastCalledWith(expect.objectContaining({faces:false}));
    fireEvent.change(screen.getByTestId("brillouin-zone-opacity"),{target:{value:"0.4"}});expect(engine.setOpacity).toHaveBeenLastCalledWith(.4);
    await userEvent.selectOptions(screen.getByTestId("brillouin-zone-projection"),"orthographic");expect(engine.setProjection).toHaveBeenLastCalledWith("orthographic");
    await userEvent.selectOptions(screen.getByTestId("brillouin-zone-camera-preset"),"b1");expect(engine.setCameraPreset).toHaveBeenLastCalledWith("b1");
    act(()=>args?.onSelection({kind:"point",id:kpath.points[0].point_id}));
    expect(screen.getByTestId("brillouin-zone-selection-id")).toHaveTextContent(kpath.points[0].point_id);
    expect(screen.getByTestId("brillouin-zone-inspector")).toHaveTextContent("Cartesian");
    fireEvent.keyDown(screen.getByTestId("brillouin-zone-renderer-surface"),{key:"ArrowLeft"});expect(engine.keyboardCamera).toHaveBeenCalledWith("rotate_left");
  });

  it("rejects invalid and unsupported artifacts before engine initialization while keeping readable fallbacks",async()=>{
    const factory=vi.fn(async()=>fakeEngine());const invalidManifest=structuredClone(manifest);invalidManifest.artifacts[1].sha256="f".repeat(64);
    const {rerender}=render(<BrillouinZoneSurface bundle={{...bundle,manifest:invalidManifest}} capabilityOverride engineFactory={factory}/>);
    expect(screen.getByTestId("brillouin-zone-renderer-state")).toHaveTextContent("invalid");expect(screen.getByTestId("brillouin-zone-renderer-fallback")).toHaveTextContent("BZ_RENDERER_VALIDATION_FAILED");expect(factory).not.toHaveBeenCalled();
    rerender(<BrillouinZoneSurface bundle={bundle} capabilityOverride={false} engineFactory={factory}/>);
    await waitFor(()=>expect(screen.getByTestId("brillouin-zone-renderer-state")).toHaveTextContent("unsupported"));expect(factory).not.toHaveBeenCalled();
  });

  it("releases stale engines on context loss, retry, artifact switch and unmount",async()=>{
    const firstDispose=vi.fn();const secondDispose=vi.fn();const engines=[fakeEngine(firstDispose),fakeEngine(secondDispose),fakeEngine()];let args:Parameters<BZRendererEngineFactory>[0]|undefined;const factory=vi.fn(async(value:Parameters<BZRendererEngineFactory>[0])=>{args=value;return engines.shift()!;});
    const {rerender,unmount}=render(<BrillouinZoneSurface bundle={bundle} capabilityOverride engineFactory={factory}/>);await waitFor(()=>expect(factory).toHaveBeenCalledTimes(1));
    act(()=>args?.onContextLost());await waitFor(()=>expect(screen.getByTestId("brillouin-zone-renderer-state")).toHaveTextContent("context_lost"));expect(firstDispose).toHaveBeenCalledTimes(1);
    await userEvent.click(screen.getByRole("button",{name:"Reinitialize renderer"}));await waitFor(()=>expect(factory).toHaveBeenCalledTimes(2));
    const nextZone=structuredClone(zone);rerender(<BrillouinZoneSurface bundle={{...bundle,zone:nextZone}} capabilityOverride engineFactory={factory}/>);await waitFor(()=>expect(factory).toHaveBeenCalledTimes(3));expect(secondDispose).toHaveBeenCalledTimes(1);unmount();
  });

  it("exports a bounded local PNG, sanitizes the filename, and revokes its object URL",async()=>{
    vi.useFakeTimers({shouldAdvanceTime:true});const engine=fakeEngine();const create=vi.fn(()=>"blob:bz");const revoke=vi.fn();Object.defineProperty(URL,"createObjectURL",{configurable:true,value:create});Object.defineProperty(URL,"revokeObjectURL",{configurable:true,value:revoke});const click=vi.spyOn(HTMLAnchorElement.prototype,"click").mockImplementation(()=>undefined);
    render(<BrillouinZoneSurface bundle={bundle} capabilityOverride engineFactory={async()=>engine}/>);await waitFor(()=>expect(screen.getByTestId("brillouin-zone-renderer-state")).toHaveTextContent("rendered"));await userEvent.click(screen.getByTestId("brillouin-zone-export-png"));await waitFor(()=>expect(engine.exportPng).toHaveBeenCalled());expect(engine.setCameraPreset).toHaveBeenCalledWith("isometric");expect(create).toHaveBeenCalledOnce();vi.runAllTimers();expect(revoke).toHaveBeenCalledWith("blob:bz");click.mockRestore();vi.useRealTimers();
  });

  it("provides semantic controls, live status and non-canvas scientific tables",async()=>{
    render(<BrillouinZoneSurface bundle={bundle} capabilityOverride={false}/>);expect(screen.getByLabelText("First Brillouin zone viewer")).not.toBeNull();expect(screen.getByTestId("brillouin-zone-live-region").getAttribute("aria-live")).toBe("polite");expect(screen.getByText(/High-symmetry points in canonical reciprocal coordinates/).tagName).toBe("CAPTION");expect(screen.getByRole("button",{name:"faces"}).getAttribute("aria-pressed")).toBe("true");expect(screen.getByTestId("brillouin-zone-opacity").getAttribute("aria-valuetext")).toContain("percent");
  });

  it("keeps one engine through repeated controls and disposes every stale engine across twenty artifact replacements",async()=>{
    const created:Array<ReturnType<typeof fakeEngine>>=[];const factory=vi.fn(async()=>{const engine=fakeEngine();created.push(engine);return engine;});
    const {rerender,unmount}=render(<BrillouinZoneSurface bundle={bundle} capabilityOverride engineFactory={factory}/>);await waitFor(()=>expect(factory).toHaveBeenCalledTimes(1));
    for(let index=0;index<20;index+=1){fireEvent.click(screen.getByRole("button",{name:"labels"}));fireEvent.change(screen.getByTestId("brillouin-zone-projection"),{target:{value:index%2?"perspective":"orthographic"}});fireEvent.click(screen.getByTestId("brillouin-zone-reset"));}
    expect(factory).toHaveBeenCalledTimes(1);expect(created[0].dispose).not.toHaveBeenCalled();
    for(let index=0;index<20;index+=1){rerender(<BrillouinZoneSurface bundle={{...bundle,zone:structuredClone(zone)}} capabilityOverride engineFactory={factory}/>);await waitFor(()=>expect(factory).toHaveBeenCalledTimes(index+2));expect(created[index].dispose).toHaveBeenCalledTimes(1);}
    unmount();expect(created.at(-1)?.dispose).toHaveBeenCalledTimes(1);
  },10_000);
});
