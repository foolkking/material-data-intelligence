import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import fixed from "../../../../../tests/fixtures/trajectory_viewer/fixed_lattice_md_12_frames.json";
import variable from "../../../../../tests/fixtures/trajectory_viewer/variable_lattice_relaxation_6_frames.json";
import type { ViewerRendererEngine, ViewerRendererEngineFactory, ViewerRendererSnapshot } from "../viewer-scene/viewerSceneRendererTypes";
import { TrajectoryViewerSurface } from "./TrajectoryViewerSurface";

function snapshot(frame=0):ViewerRendererSnapshot{return {state:"rendered",canvasCount:1,atomCount:2,bondCount:0,latticeEdgeCount:12,triangleCount:560,lineCount:12,cameraPosition:[8,8,8],cameraTarget:[2,2,2],cameraUp:[0,0,1],cameraZoom:1,cameraPreset:"default",activeClipPlanes:0,latticeAxesVisible:false,drawingBuffer:[720,480],graphicsContext:"webgl2",rendererVersion:"185",selectedSites:[],selectedSiteIndices:[],selectedBondId:null,siteScreenPositions:[],bondScreenPositions:[],metrics:{performanceTier:"interactive",atomCount:2,bondCount:0,speciesCount:1,instancedMeshCount:1,latticeEdgeCount:12,drawCalls:2,geometries:5,materials:3,triangles:560,lines:12,textures:0,bufferAttributes:3,sceneObjects:8,initializationMs:10,firstFrameMs:12+frame}};}
function fakeEngine(){let current=0;const engine:ViewerRendererEngine={resetCamera:vi.fn(),fitCurrentScene:vi.fn(),setCellVisible:vi.fn(),setSupercellBoundaryVisible:vi.fn(),setLatticeAxesVisible:vi.fn(),setBondsVisible:vi.fn(),setClipState:vi.fn(),setCameraPreset:vi.fn(),render:vi.fn(),replaceScene:vi.fn(),updateDynamicScene:vi.fn((scene)=>{current=Number(scene.atoms[0]?.canonicalPosition[0]??0);return{atomMatricesUpdated:scene.atoms.length,lineVerticesUpdated:30};}),keyboardCamera:vi.fn(),setSelection:vi.fn(),setBondSelection:vi.fn(),setDisplacementVectors:vi.fn(),setDisplacementTrails:vi.fn(),exportPng:vi.fn(async()=>new Blob()),snapshot:()=>snapshot(current),dispose:vi.fn()};return engine;}

describe("TrajectoryViewerSurface",()=>{
  it("publishes only explicit Research choices and keeps frame and periodic atom identity", async () => {
    const engine=fakeEngine(), selection=vi.fn();
    let args:Parameters<ViewerRendererEngineFactory>[0];
    const factory:ViewerRendererEngineFactory=async value=>{args=value;return engine;};
    render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={factory} onPointSelection={selection}/>);
    await waitFor(()=>expect(screen.getByRole("button",{name:"播放轨迹"})).toBeEnabled());
    fireEvent.change(screen.getByTestId("trajectory-frame-slider"),{target:{value:"5"}});
    await waitFor(()=>expect(screen.getByText("第 6 / 12 帧")).toBeInTheDocument());
    expect(selection).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button",{name:"选择当前帧用于研究"}));
    expect(selection).toHaveBeenLastCalledWith({frameIndex:5,atom:null});
    act(()=>args.onSitePick?.({siteIndex:1,imageOffset:[0,0,0]}));
    expect(selection).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole("button",{name:"选择此原子用于研究"}));
    expect(selection).toHaveBeenLastCalledWith({frameIndex:5,atom:{siteIndex:1,imageOffset:[0,0,0]}});
    fireEvent.click(screen.getByRole("button",{name:"距离"}));
    expect(screen.queryByRole("button",{name:"选择此原子用于研究"})).toBeNull();
    expect(selection).toHaveBeenCalledTimes(2);
  });
  it("makes atom inspection available from the keyboard without changing Research selection", async () => {
    const engine=fakeEngine(),selection=vi.fn();
    render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={async()=>engine} onPointSelection={selection}/>);
    await waitFor(()=>expect(screen.getByRole("button",{name:"播放轨迹"})).toBeEnabled());
    const viewer=screen.getByTestId("trajectory-viewer");
    fireEvent.keyDown(viewer,{key:"n"});
    expect(engine.setSelection).toHaveBeenLastCalledWith([{siteIndex:0,imageOffset:[0,0,0]}]);
    fireEvent.keyDown(viewer,{key:"N"});
    expect(engine.setSelection).toHaveBeenLastCalledWith([{siteIndex:1,imageOffset:[0,0,0]}]);
    expect(screen.getByRole("button",{name:"选择此原子用于研究"})).toBeEnabled();
    fireEvent.keyDown(viewer,{key:"Escape"});
    expect(screen.queryByTestId("trajectory-selected-atom")).toBeNull();
    expect(selection).not.toHaveBeenCalled();
  });
  it("restores a periodic atom and frame while allowing subsequent browsing and history changes", async () => {
    const engines:ViewerRendererEngine[]=[];
    const factory=vi.fn(async()=>{const engine=fakeEngine();engines.push(engine);return engine;});
    const selection=vi.fn(), point={frameIndex:5,atom:{siteIndex:1,imageOffset:[1,0,1] as const}};
    const view=render(<TrajectoryViewerSurface payload={fixed} capabilityOverride mobileOverride={false} engineFactory={factory} selectedPoint={point} onPointSelection={selection}/>);
    await waitFor(()=>expect(screen.getByText("第 6 / 12 帧")).toBeInTheDocument());
    expect(screen.getByTestId("trajectory-supercell")).toHaveValue("2x2x2");
    expect(engines.at(-1)!.setSelection).toHaveBeenLastCalledWith([point.atom]);
    expect(screen.getByTestId("trajectory-research-selection")).toHaveTextContent("已选 第 6 帧 · 原子 2 · 周期位置 [1, 0, 1]");
    fireEvent.click(screen.getByRole("button",{name:"下一帧"}));
    await waitFor(()=>expect(screen.getByText("第 7 / 12 帧")).toBeInTheDocument());
    expect(screen.getByTestId("trajectory-research-selection")).toHaveTextContent("第 6 帧");
    view.rerender(<TrajectoryViewerSurface payload={fixed} capabilityOverride mobileOverride={false} engineFactory={factory} selectedPoint={{frameIndex:2,atom:null}} onPointSelection={selection}/>);
    await waitFor(()=>expect(screen.getByText("第 3 / 12 帧")).toBeInTheDocument());
    expect(screen.queryByTestId("trajectory-selected-atom")).toBeNull();
    fireEvent.click(screen.getByRole("button",{name:"清除研究选择"}));
    expect(selection).toHaveBeenCalledOnce();
    expect(selection).toHaveBeenCalledWith(null);
  });
  const largerTrajectory = {...fixed, atoms: {count: 64, records: Array.from({length: 64}, (_, atom_id) => ({...fixed.atoms.records[atom_id % 4], atom_id, label: `atom-${atom_id}`}))},
    frames: fixed.frames.map(frame => ({...frame, atom_ids: Array.from({length: 64}, (_, i) => i), positions: Array.from({length: 64}, (_, i) => frame.positions[i % 4]), velocities: Array.from({length: 64}, (_, i) => frame.velocities[i % 4])}))};
  it("disables over-budget supercells before selection and retains the usable renderer", async () => {
    const factory = vi.fn(async () => fakeEngine());
    render(<TrajectoryViewerSurface payload={largerTrajectory} capabilityOverride mobileOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.getByRole("button", {name: "播放轨迹"})).toBeEnabled());
    expect(screen.getByRole("option", {name: "2 × 2 × 2（超出显示上限）"})).toBeDisabled();
    fireEvent.change(screen.getByTestId("trajectory-supercell"), {target: {value: "2x2x2"}});
    expect(screen.queryByRole("alert")).toBeNull();
    expect(factory).toHaveBeenCalledOnce();
    expect(screen.getByTestId("trajectory-supercell")).toHaveValue("1x1x1");
  });
  it("recovers an excessive saved supercell without changing source or playback settings", async () => {
    const factory = vi.fn(async () => fakeEngine());
    render(<TrajectoryViewerSurface payload={largerTrajectory} capabilityOverride mobileOverride={false} engineFactory={factory}
      initialOptions={{playbackSpeed:2,loop:true,supercell:[3,3,3],showCell:true,clipping:false,performanceMode:"auto",bondMode:"none"}} />);
    expect(factory).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", {name: "恢复原始晶胞"}));
    await waitFor(() => expect(screen.getByRole("button", {name: "播放轨迹"})).toBeEnabled());
    expect(screen.getByTestId("trajectory-playback-speed")).toHaveValue("2");
    expect(screen.getByTestId("trajectory-loop")).toBeChecked();
    expect(screen.getByTestId("trajectory-supercell")).toHaveValue("1x1x1");
    expect(factory.mock.calls).toHaveLength(1);
    expect(screen.getByTestId("trajectory-viewer")).toHaveFocus();
  });
  it("retains the displayed frame when a smaller viewport requires reducing the supercell", async () => {
    const factory = vi.fn(async () => fakeEngine());
    const view = render(<TrajectoryViewerSurface payload={largerTrajectory} capabilityOverride mobileOverride={false} engineFactory={factory} />);
    await waitFor(() => expect(screen.getByRole("button", {name: "播放轨迹"})).toBeEnabled());
    fireEvent.keyDown(screen.getByTestId("trajectory-viewer"), {key:"End"});
    await waitFor(() => expect(screen.getByText("第 12 / 12 帧")).toBeVisible());
    fireEvent.change(screen.getByTestId("trajectory-supercell"), {target:{value:"2x2x2"}});
    await waitFor(() => expect(factory).toHaveBeenCalledTimes(2));
    view.rerender(<TrajectoryViewerSurface payload={largerTrajectory} capabilityOverride mobileOverride engineFactory={factory} />);
    fireEvent.click(screen.getByRole("button", {name: "恢复原始晶胞"}));
    await waitFor(() => expect(screen.getByRole("button", {name: "播放轨迹"})).toBeEnabled());
    expect(screen.getByText("第 12 / 12 帧")).toBeVisible();
    expect(JSON.parse(screen.getByTestId("trajectory-viewer-metrics").textContent!).viewer).toMatchObject({currentFrame:11,displayedInstances:64,activeLoops:0});
  });
  it("keeps controls disabled during loading and rejects a late engine after timeout and retry", async () => {
    vi.useFakeTimers();
    try {
      const late = fakeEngine(), recovered = fakeEngine();
      let finish!: (engine: ViewerRendererEngine) => void;
      const factory = vi.fn<ViewerRendererEngineFactory>().mockImplementationOnce(() => new Promise(resolve => {finish = resolve;})).mockResolvedValueOnce(recovered);
      render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={factory} />);
      await act(async () => Promise.resolve());
      expect(screen.getByTestId("trajectory-viewer-state").textContent).toBe("正在加载");
      expect(screen.getByRole("button", {name: "播放轨迹"})).toBeDisabled();
      expect(screen.getByTestId("trajectory-frame-slider")).toBeDisabled();
      const oldHost = factory.mock.calls[0][0].container;
      await act(async () => vi.advanceTimersByTimeAsync(10_000));
      expect(screen.getByRole("alert")).toHaveTextContent("加载超过 10 秒");
      expect(oldHost.isConnected).toBe(false);
      fireEvent.click(screen.getByRole("button", {name: "重试渲染器"}));
      await act(async () => Promise.resolve());
      expect(factory).toHaveBeenCalledTimes(2);
      expect(screen.getByRole("button", {name: "播放轨迹"})).toBeEnabled();
      expect(screen.getByTestId("trajectory-viewer")).toHaveFocus();
      await act(async () => finish(late));
      expect(late.dispose).toHaveBeenCalledOnce();
      expect(recovered.dispose).not.toHaveBeenCalled();
      expect(screen.queryByRole("alert")).toBeNull();
    } finally { vi.useRealTimers(); }
  });
  it("disposes a late initialization after a source change without changing the replacement view", async () => {
    const old = fakeEngine(), next = fakeEngine();
    let finish!: (engine: ViewerRendererEngine) => void;
    const factory = vi.fn<ViewerRendererEngineFactory>().mockImplementationOnce(() => new Promise(resolve => {finish = resolve;})).mockResolvedValueOnce(next);
    const view = render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(factory).toHaveBeenCalledOnce());
    view.rerender(<TrajectoryViewerSurface payload={variable} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.getByRole("button", {name: "播放轨迹"})).toBeEnabled());
    await act(async () => finish(old));
    expect(old.dispose).toHaveBeenCalledOnce();
    expect(next.dispose).not.toHaveBeenCalled();
    expect(screen.getByText("第 1 / 6 帧")).toBeVisible();
  });
  it("keeps technical details collapsed and does not rebuild the canvas while opening controls", async () => {
    const factory = vi.fn(async () => fakeEngine());
    render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.getByRole("button", {name: "播放轨迹"})).toBeEnabled());
    expect(screen.getByText("测量与显示").closest("details")).not.toHaveAttribute("open");
    expect(screen.getByText("数据与来源").closest("details")).not.toHaveAttribute("open");
    fireEvent.click(screen.getByText("测量与显示"));
    fireEvent.click(screen.getByText("数据与来源"));
    expect(factory).toHaveBeenCalledOnce();
  });
  it("leaves native button Space and slider arrows intact while supporting viewer shortcuts", async () => {
    const engine = fakeEngine();
    render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={async () => engine} />);
    await waitFor(() => expect(screen.getByRole("button", {name: "下一帧"})).toBeEnabled());
    const next = screen.getByRole("button", {name: "下一帧"});
    expect(fireEvent.keyDown(next, {key: " "})).toBe(true);
    expect(screen.queryByRole("button", {name: "暂停轨迹"})).toBeNull();
    expect(fireEvent.keyDown(screen.getByTestId("trajectory-frame-slider"), {key: "ArrowRight"})).toBe(true);
    fireEvent.keyDown(screen.getByTestId("trajectory-viewer"), {key: "End"});
    await waitFor(() => expect(screen.getByText("第 12 / 12 帧")).toBeVisible());
    expect(screen.getByRole("button", {name: "下一帧"})).toBeDisabled();
  });
  it("stops and releases the engine when a frame update fails, then retries the last displayed frame", async () => {
    const failed = fakeEngine(), recovered = fakeEngine();
    const factory = vi.fn<ViewerRendererEngineFactory>().mockResolvedValueOnce(failed).mockResolvedValueOnce(recovered);
    render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.getByRole("button", {name: "下一帧"})).toBeEnabled());
    fireEvent.click(screen.getByRole("button", {name: "下一帧"}));
    await waitFor(() => expect(screen.getByText("第 2 / 12 帧")).toBeVisible());
    vi.mocked(failed.updateDynamicScene).mockImplementationOnce(() => { throw new Error("private renderer error"); });
    fireEvent.click(screen.getByRole("button", {name: "下一帧"}));
    await screen.findByRole("alert");
    expect(failed.dispose).toHaveBeenCalledOnce();
    expect(screen.queryByText("private renderer error")).toBeNull();
    fireEvent.click(screen.getByRole("button", {name: "重试渲染器"}));
    await waitFor(() => expect(screen.getByText("第 2 / 12 帧")).toBeVisible());
    expect(factory.mock.calls[1][0].scene.atoms[0].canonicalPosition).toEqual(vi.mocked(failed.updateDynamicScene).mock.calls[0][0].atoms[0].canonicalPosition);
  });
  it("shows formal product identity and bounded capability truth",async()=>{const engine=fakeEngine();render(<TrajectoryViewerSurface payload={fixed} toolId="structure.trajectory_viewer" capabilityOverride engineFactory={async()=>engine}/>);await waitFor(()=>expect(screen.getByTestId("trajectory-viewer-state").textContent).toContain("已暂停"));expect(screen.getByTestId("trajectory-viewer-product-identity").textContent).toContain("正式轨迹查看器");expect(screen.getByTestId("trajectory-viewer-capability-truth").textContent).toContain("动态键合");const metrics=JSON.parse(screen.getByTestId("trajectory-viewer-metrics").textContent||"{}");expect(metrics.viewer.toolId).toBe("structure.trajectory_viewer");});
  it("applies allowlisted formal launch defaults without rebuilding on cell toggle",async()=>{const engine=fakeEngine();const factory=vi.fn(async()=>engine);render(<TrajectoryViewerSurface payload={fixed} initialOptions={{playbackSpeed:2,loop:true,supercell:[2,2,2],showCell:false,clipping:true,performanceMode:"auto",bondMode:"none"}} capabilityOverride engineFactory={factory}/>);await waitFor(()=>expect(factory).toHaveBeenCalledOnce());expect((screen.getByTestId("trajectory-playback-speed") as HTMLSelectElement).value).toBe("2");expect((screen.getByTestId("trajectory-loop") as HTMLInputElement).checked).toBe(true);expect((screen.getByTestId("trajectory-supercell") as HTMLSelectElement).value).toBe("2x2x2");expect(engine.setCellVisible).toHaveBeenCalledWith(false);expect(engine.setClipState).toHaveBeenCalled();fireEvent.click(screen.getByLabelText("晶胞"));expect(factory).toHaveBeenCalledOnce();expect(engine.setCellVisible).toHaveBeenLastCalledWith(true);});
  it("loads paused at frame zero and navigates by dynamic updates without renderer rebuild",async()=>{const engine=fakeEngine();const factory=vi.fn(async()=>engine);render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={factory}/>);await waitFor(()=>expect(factory).toHaveBeenCalledOnce());expect(screen.getByTestId("trajectory-viewer-state").textContent).toContain("已暂停");await userEvent.click(screen.getByRole("button",{name:"下一帧"}));await waitFor(()=>expect(screen.queryByText("第 2 / 12 帧")).not.toBeNull());expect(engine.updateDynamicScene).toHaveBeenCalledOnce();expect(engine.replaceScene).not.toHaveBeenCalled();expect(factory).toHaveBeenCalledOnce();});
  it("runs one bounded playback timer and pauses without leaving a loop",async()=>{vi.useFakeTimers();const engine=fakeEngine();render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={async()=>engine}/>);await act(async()=>Promise.resolve());fireEvent.click(screen.getByRole("button",{name:"播放轨迹"}));expect(screen.getByTestId("trajectory-viewer-state").textContent).toContain("播放中");await act(async()=>vi.advanceTimersByTimeAsync(120));expect(engine.updateDynamicScene).toHaveBeenCalled();fireEvent.click(screen.getByRole("button",{name:"暂停轨迹"}));const metrics=JSON.parse(screen.getByTestId("trajectory-viewer-metrics").textContent||"{}");expect(metrics.viewer.activeLoops).toBe(0);vi.useRealTimers();});
  it("binds picking and distance measurement to the committed frame",async()=>{const engine=fakeEngine();let args:Parameters<ViewerRendererEngineFactory>[0]|undefined;render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={async(value)=>{args=value;return engine;}}/>);await waitFor(()=>expect(args).toBeTruthy());await userEvent.click(screen.getByRole("button",{name:"距离"}));act(()=>args?.onSitePick?.({siteIndex:0,imageOffset:[0,0,0]}));expect(screen.getByTestId("trajectory-selected-velocity").textContent).toContain("Å/飞秒");act(()=>args?.onSitePick?.({siteIndex:1,imageOffset:[0,0,0]}));await waitFor(()=>expect(screen.getByTestId("trajectory-measurement").textContent).toContain("第 1 帧"));await userEvent.click(screen.getByRole("button",{name:"下一帧"}));await waitFor(()=>expect(screen.queryByTestId("trajectory-measurement")).toBeNull());});
  it("rejects stale picking while a requested frame is buffering",async()=>{const engine=fakeEngine();let args:Parameters<ViewerRendererEngineFactory>[0]|undefined;let queued:(()=>void)|undefined;render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={async(value)=>{args=value;return engine;}}/>);await waitFor(()=>expect(args).toBeTruthy());vi.stubGlobal("queueMicrotask",(callback:()=>void)=>{queued=callback;});fireEvent.click(screen.getByRole("button",{name:"下一帧"}));act(()=>args?.onSitePick?.({siteIndex:0,imageOffset:[0,0,0]}));expect(screen.queryByTestId("trajectory-selected-atom")).toBeNull();await act(async()=>queued?.());vi.unstubAllGlobals();});
  it("coalesces rapid seeks to one pending map and commits only the latest frame",async()=>{const engine=fakeEngine();render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={async()=>engine}/>);await waitFor(()=>expect(screen.getByTestId("trajectory-viewer-state").textContent).toContain("已暂停"));const queued:Array<()=>void>=[];vi.stubGlobal("queueMicrotask",(callback:()=>void)=>queued.push(callback));const slider=screen.getByTestId("trajectory-frame-slider");for(let index=1;index<12;index+=1)fireEvent.change(slider,{target:{value:String(index)}});expect(queued).toHaveLength(1);await act(async()=>queued[0]());await waitFor(()=>expect(screen.queryByText("第 12 / 12 帧")).not.toBeNull());const metrics=JSON.parse(screen.getByTestId("trajectory-viewer-metrics").textContent||"{}");expect(metrics.viewer).toMatchObject({currentFrame:11,requestedFrame:11,pendingRequests:0,peakPendingRequests:1,maxPendingRequests:1,prefetchRequests:0});expect(engine.updateDynamicScene).toHaveBeenCalledOnce();vi.unstubAllGlobals();});
  it("uses mobile resource policy and refreshes clipping on frame commit",async()=>{const engine=fakeEngine();render(<TrajectoryViewerSurface payload={fixed} capabilityOverride mobileOverride engineFactory={async()=>engine}/>);await waitFor(()=>expect(screen.getByTestId("trajectory-viewer-state").textContent).toContain("已暂停"));let metrics=JSON.parse(screen.getByTestId("trajectory-viewer-metrics").textContent||"{}");expect(metrics.viewer).toMatchObject({mobile:true,maxPlaybackFps:15});expect(metrics.viewer.cache.maxFrames).toBe(3);fireEvent.click(screen.getByLabelText("裁剪"));const before=vi.mocked(engine.setClipState).mock.calls.length;await userEvent.click(screen.getByRole("button",{name:"下一帧"}));await waitFor(()=>expect(vi.mocked(engine.setClipState).mock.calls.length).toBeGreaterThan(before));metrics=JSON.parse(screen.getByTestId("trajectory-viewer-metrics").textContent||"{}");expect(metrics.viewer.currentFrame).toBe(1);});
  it("keeps mobile budgets on a touch device in landscape",async()=>{const descriptor=Object.getOwnPropertyDescriptor(navigator,"maxTouchPoints");Object.defineProperty(navigator,"maxTouchPoints",{configurable:true,value:1});const width=vi.spyOn(window,"innerWidth","get").mockReturnValue(844);const engine=fakeEngine();render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={async()=>engine}/>);await waitFor(()=>expect(JSON.parse(screen.getByTestId("trajectory-viewer-metrics").textContent||"{}").viewer.mobile).toBe(true));const metrics=JSON.parse(screen.getByTestId("trajectory-viewer-metrics").textContent||"{}");expect(metrics.viewer).toMatchObject({mobile:true,maxPlaybackFps:15});width.mockRestore();if(descriptor)Object.defineProperty(navigator,"maxTouchPoints",descriptor);else Reflect.deleteProperty(navigator,"maxTouchPoints");});
  it("shows canonical force data for a selected variable-lattice atom",async()=>{const engine=fakeEngine();let args:Parameters<ViewerRendererEngineFactory>[0]|undefined;render(<TrajectoryViewerSurface payload={variable} capabilityOverride engineFactory={async(value)=>{args=value;return engine;}}/>);await waitFor(()=>expect(args).toBeTruthy());act(()=>args?.onSitePick?.({siteIndex:0,imageOffset:[0,0,0]}));expect(screen.getByTestId("trajectory-selected-force").textContent).toContain("eV/Å");});
  it("reports renderer initialization failure without crashing the preview",async()=>{render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={async()=>{throw new Error("private diagnostic");}}/>);expect(await screen.findByText("TRAJECTORY_VIEWER_INITIALIZATION_FAILED")).not.toBeNull();expect(screen.queryByText("private diagnostic")).toBeNull();});
  it("stops safely on context loss and disposes on unmount",async()=>{const engine=fakeEngine();let args:Parameters<ViewerRendererEngineFactory>[0]|undefined;const view=render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={async(value)=>{args=value;return engine;}}/>);await waitFor(()=>expect(args).toBeTruthy());act(()=>args?.onContextLost());expect(screen.getByTestId("trajectory-viewer-state").textContent).toContain("context_lost");view.unmount();expect(engine.dispose).toHaveBeenCalled();});
  it("retries context loss with one replacement engine and no duplicate context",async()=>{const engines=[fakeEngine(),fakeEngine()];const args:Array<Parameters<ViewerRendererEngineFactory>[0]>=[];const factory=vi.fn(async(value:Parameters<ViewerRendererEngineFactory>[0])=>{args.push(value);return engines[args.length-1];});const view=render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={factory}/>);await waitFor(()=>expect(factory).toHaveBeenCalledTimes(1));act(()=>args[0].onContextLost());expect(engines[0].dispose).toHaveBeenCalled();await userEvent.click(screen.getByRole("button",{name:"重试渲染器"}));await waitFor(()=>expect(factory).toHaveBeenCalledTimes(2));const metrics=JSON.parse(screen.getByTestId("trajectory-viewer-metrics").textContent||"{}");expect(metrics.viewer).toMatchObject({canvasCount:1,contextCount:1,activeLoops:0});view.unmount();expect(engines[1].dispose).toHaveBeenCalledOnce();});
  it("clears selection and disposes the old engine on trajectory switch",async()=>{const engines=[fakeEngine(),fakeEngine()];const args:Array<Parameters<ViewerRendererEngineFactory>[0]>=[];const factory=vi.fn(async(value:Parameters<ViewerRendererEngineFactory>[0])=>{args.push(value);return engines[args.length-1];});const view=render(<TrajectoryViewerSurface payload={fixed} capabilityOverride engineFactory={factory}/>);await waitFor(()=>expect(factory).toHaveBeenCalledTimes(1));act(()=>args[0].onSitePick?.({siteIndex:0,imageOffset:[0,0,0]}));await waitFor(()=>expect(screen.queryByTestId("trajectory-selected-atom")).not.toBeNull());view.rerender(<TrajectoryViewerSurface payload={variable} capabilityOverride engineFactory={factory}/>);await waitFor(()=>expect(factory).toHaveBeenCalledTimes(2));expect(engines[0].dispose).toHaveBeenCalled();expect(screen.queryByTestId("trajectory-selected-atom")).toBeNull();expect(screen.queryByText("第 1 / 6 帧")).not.toBeNull();});
  it("rejects invalid artifacts before creating a renderer",()=>{const factory=vi.fn();render(<TrajectoryViewerSurface payload={{schema_version:"phase10g.trajectory.v1"}} capabilityOverride engineFactory={factory as ViewerRendererEngineFactory}/>);expect(screen.queryByTestId("trajectory-viewer-fallback")).not.toBeNull();expect(factory).not.toHaveBeenCalled();});
});
