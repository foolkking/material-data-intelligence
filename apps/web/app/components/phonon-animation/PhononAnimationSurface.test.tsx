import {act,fireEvent,render,screen,waitFor,within} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {afterEach,describe,expect,it,vi} from "vitest";
import type {ViewerRendererEngine,ViewerRendererEngineFactory,ViewerRendererSnapshot} from "../viewer-scene/viewerSceneRendererTypes";
import {PhononAnimationSurface} from "./PhononAnimationSurface";
import {phononAnimationFixture} from "./phononAnimationTestFixture";

function snapshot():ViewerRendererSnapshot{return {state:"rendered",canvasCount:1,atomCount:4,bondCount:2,latticeEdgeCount:12,triangleCount:1,lineCount:1,cameraPosition:[1,1,1],cameraTarget:[0,0,0],cameraUp:[0,0,1],cameraZoom:1,cameraPreset:"default",activeClipPlanes:0,latticeAxesVisible:true,drawingBuffer:[720,480],graphicsContext:"webgl2",rendererVersion:"185",selectedSites:[],selectedSiteIndices:[],selectedBondId:null,siteScreenPositions:[],bondScreenPositions:[],metrics:{performanceTier:"interactive",atomCount:4,bondCount:2,speciesCount:1,instancedMeshCount:1,latticeEdgeCount:12,drawCalls:5,geometries:5,materials:5,triangles:1,lines:1,textures:0,bufferAttributes:3,sceneObjects:8,initializationMs:1,firstFrameMs:2}};}
function fakeEngine():ViewerRendererEngine{return{resetCamera:vi.fn(),fitCurrentScene:vi.fn(),setCellVisible:vi.fn(),setSupercellBoundaryVisible:vi.fn(),setLatticeAxesVisible:vi.fn(),setBondsVisible:vi.fn(),setClipState:vi.fn(),setCameraPreset:vi.fn(),render:vi.fn(),replaceScene:vi.fn(),updateDynamicScene:vi.fn(()=>({atomMatricesUpdated:4,lineVerticesUpdated:34})),keyboardCamera:vi.fn(),setSelection:vi.fn(),setBondSelection:vi.fn(),setDisplacementVectors:vi.fn(),setDisplacementTrails:vi.fn(),exportPng:vi.fn(async()=>new Blob()),snapshot,dispose:vi.fn()};}
afterEach(()=>{vi.useRealTimers();vi.unstubAllGlobals();});
describe("PhononAnimationSurface",()=>{
  it("keeps playback unavailable until initialization and removes the loading overlay when ready", async () => {
    const engine = fakeEngine();
    let ready!: (engine: ViewerRendererEngine) => void;
    const factory: ViewerRendererEngineFactory = () => new Promise(resolve => { ready = resolve; });
    render(<PhononAnimationSurface payload={phononAnimationFixture()} capabilityOverride engineFactory={factory}/>);
    expect(screen.getByRole("button", {name: "播放声子动画"})).toBeDisabled();
    expect(screen.getByTestId("phonon-phase-slider")).toBeDisabled();
    expect(screen.getByTestId("phonon-animation-canvas-host")).toHaveAttribute("aria-busy", "true");
    expect(within(screen.getByTestId("phonon-animation-canvas-host")).getByRole("status")).toHaveTextContent("正在加载声子图");
    await act(async () => ready(engine));
    expect(screen.getByRole("button", {name: "播放声子动画"})).toBeEnabled();
    expect(screen.getByTestId("phonon-animation-canvas-host")).toHaveAttribute("aria-busy", "false");
    expect(within(screen.getByTestId("phonon-animation-canvas-host")).queryByRole("status")).not.toBeInTheDocument();
  });

  it("clears both the periodic atom inspector and renderer highlight", async () => {
    const engine = fakeEngine();
    let args: Parameters<ViewerRendererEngineFactory>[0] | undefined;
    render(<PhononAnimationSurface payload={phononAnimationFixture()} capabilityOverride engineFactory={async value => { args = value; return engine; }}/>);
    await waitFor(() => expect(screen.getByRole("button", {name: "播放声子动画"})).toBeEnabled());
    const ref = {siteIndex: 0, imageOffset: [1, 0, 0] as const};
    act(() => args?.onSitePick?.(ref));
    expect(engine.setSelection).toHaveBeenLastCalledWith([ref]);
    expect(screen.getByTestId("phonon-selected-atom")).toHaveTextContent("[1, 0, 0]");
    await userEvent.click(screen.getByRole("button", {name: "清除选择"}));
    expect(screen.queryByTestId("phonon-animation-inspector")).not.toBeInTheDocument();
    expect(engine.setSelection).toHaveBeenLastCalledWith([]);
  });

  it("starts paused and updates a mathematically mapped fixed phase",async()=>{const engine=fakeEngine();render(<PhononAnimationSurface payload={phononAnimationFixture()} capabilityOverride engineFactory={async()=>engine}/>);await waitFor(()=>expect(screen.getByTestId("phonon-animation-state").textContent).toBe("已暂停"));fireEvent.change(screen.getByTestId("phonon-phase-slider"),{target:{value:String(Math.PI)}});await waitFor(()=>expect(screen.getByTestId("phonon-phase-value").textContent).toContain("3.142"));expect(engine.updateDynamicScene).toHaveBeenCalled();expect(engine.setDisplacementVectors).toHaveBeenCalled();});
  it("plays with one RAF and pauses cleanly",async()=>{let callback:FrameRequestCallback|undefined;vi.stubGlobal("requestAnimationFrame",vi.fn((value:FrameRequestCallback)=>{callback=value;return 7;}));vi.stubGlobal("cancelAnimationFrame",vi.fn());const engine=fakeEngine();render(<PhononAnimationSurface payload={phononAnimationFixture()} capabilityOverride engineFactory={async()=>engine}/>);await waitFor(()=>expect(screen.getByRole("button",{name:"播放声子动画"})).toBeTruthy());await userEvent.click(screen.getByRole("button",{name:"播放声子动画"}));expect(screen.getByTestId("phonon-animation-state").textContent).toBe("播放中");act(()=>callback?.(100));act(()=>callback?.(150));await userEvent.click(screen.getByRole("button",{name:"暂停声子动画"}));expect(screen.getByTestId("phonon-animation-state").textContent).toBe("已暂停");expect(cancelAnimationFrame).toHaveBeenCalled();});
  it("honors reduced motion and retains static phase controls",async()=>{render(<PhononAnimationSurface payload={phononAnimationFixture()} capabilityOverride reducedMotionOverride engineFactory={async()=>fakeEngine()}/>);await waitFor(()=>expect(screen.getByTestId("phonon-reduced-motion")).toBeTruthy());await userEvent.click(screen.getByRole("button",{name:"播放声子动画"}));expect(screen.getByTestId("phonon-animation-state").textContent).toBe("已暂停");expect(screen.getByTestId("phonon-phase-slider")).toBeTruthy();});
  it("supports toggles and periodic atom inspection",async()=>{const engine=fakeEngine();let args:Parameters<ViewerRendererEngineFactory>[0]|undefined;render(<PhononAnimationSurface payload={phononAnimationFixture()} capabilityOverride engineFactory={async(value)=>{args=value;return engine;}}/>);await waitFor(()=>expect(args).toBeTruthy());act(()=>args?.onSitePick?.({siteIndex:0,imageOffset:[1,0,0]}));expect(screen.getByTestId("phonon-selected-atom").textContent).toContain("[1, 0, 0]");await userEvent.click(screen.getByText("显示与播放设置"));await userEvent.click(screen.getByLabelText("运动轨迹"));expect(engine.setDisplacementTrails).toHaveBeenCalled();await userEvent.click(screen.getByLabelText("位移向量"));expect(engine.setDisplacementVectors).toHaveBeenLastCalledWith([]);});
  it("rejects invalid or unsupported payloads before creating a context",()=>{const factory=vi.fn();render(<PhononAnimationSurface payload={{schema_version:"bad"}} capabilityOverride engineFactory={factory as ViewerRendererEngineFactory}/>);expect(screen.getByTestId("phonon-animation-fallback")).toBeTruthy();expect(factory).not.toHaveBeenCalled();});
  it("stops and disposes on context loss and unmount",async()=>{const engine=fakeEngine();let args:Parameters<ViewerRendererEngineFactory>[0]|undefined;const view=render(<PhononAnimationSurface payload={phononAnimationFixture()} capabilityOverride engineFactory={async(value)=>{args=value;return engine;}}/>);await waitFor(()=>expect(args).toBeTruthy());act(()=>args?.onContextLost());expect(screen.getByText("PHONON_ANIMATION_CONTEXT_LOST")).toBeTruthy();view.unmount();expect(engine.dispose).toHaveBeenCalled();});
});
