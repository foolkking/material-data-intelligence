import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import minimalScene from "../../../../../tests/fixtures/viewer_scene_v1/valid_minimal_crystal.viewer_scene.v1.json";
import multiSpeciesScene from "../../../../../tests/fixtures/viewer_scene_v1/valid_multi_species_crystal.viewer_scene.v1.json";
import { ViewerSceneRendererSurface } from "./ViewerSceneRendererSurface";
import type { ViewerRendererEngine, ViewerRendererEngineFactory, ViewerRendererSnapshot } from "./viewerSceneRendererTypes";
import { idealCrystalScene, periodicBoundaryScene } from "./viewerScenePeriodicBondTestFixture";

function fakeEngine(dispose = vi.fn()) {
  let cellVisible = true;
  let bondsVisible = true;
  const snapshot = (): ViewerRendererSnapshot => ({
    state: "rendered",
    canvasCount: 1,
    atomCount: 2,
    bondCount: bondsVisible ? 1 : 0,
    latticeEdgeCount: cellVisible ? 12 : 0,
    triangleCount: 560,
    lineCount: 13,
    cameraPosition: [8, 8, 8],
    cameraTarget: [2, 2, 2],
    cameraUp: [0, 0, 1],
    cameraZoom: 1,
    cameraPreset: "default",
    activeClipPlanes: 0,
    latticeAxesVisible: false,
    drawingBuffer: [720, 480],
    graphicsContext: "webgl2",
    rendererVersion: "185",
    selectedSites: [],
    selectedSiteIndices: [],
    selectedBondId: null,
    siteScreenPositions: [],
    bondScreenPositions: [],
    metrics: {
      performanceTier: "interactive",
      atomCount: 2,
      bondCount: 1,
      speciesCount: 1,
      instancedMeshCount: 1,
      latticeEdgeCount: 12,
      drawCalls: 3,
      geometries: 3,
      materials: 3,
      triangles: 560,
      lines: 13,
      textures: 0,
      bufferAttributes: 3,
      sceneObjects: 8,
      initializationMs: 10,
      firstFrameMs: 12,
    },
  });
  const engine: ViewerRendererEngine = {
    resetCamera: vi.fn(),
    fitCurrentScene: vi.fn(),
    setCellVisible(value) { cellVisible = value; },
    setSupercellBoundaryVisible: vi.fn(),
    setLatticeAxesVisible: vi.fn(),
    setBondsVisible(value) { bondsVisible = value; },
    setClipState: vi.fn(),
    setCameraPreset: vi.fn(),
    setSelection: vi.fn(),
    setBondSelection: vi.fn(),
    setDisplacementVectors: vi.fn(),
    setDisplacementTrails: vi.fn(),
    exportPng: vi.fn(async () => new Blob(["png"], { type: "image/png" })),
    render: vi.fn(),
    replaceScene: vi.fn(),
    updateDynamicScene: vi.fn(() => ({ atomMatricesUpdated: 2, lineVerticesUpdated: 30 })),
    keyboardCamera: vi.fn(),
    snapshot,
    dispose,
  };
  return engine;
}

describe("ViewerSceneRendererSurface", () => {
  it("shows saved ideal-model neighbors with their own method and complete periodic endpoints", async () => {
    let args: Parameters<ViewerRendererEngineFactory>[0] | undefined;
    const payload = idealCrystalScene();
    render(<ViewerSceneRendererSurface payload={payload} capabilityOverride engineFactory={async value => { args = value; return fakeEngine(); }} />);
    await waitFor(() => expect(args).toBeTruthy());
    expect(screen.getByRole("button", { name: "近邻连接" })).toHaveAttribute("title", expect.stringContaining("最短周期近邻"));
    expect(screen.queryByRole("button", { name: /^键合$/ })).toBeNull();
    act(() => args?.onSitePick?.({ siteIndex: 0, imageOffset: [0, 0, 0] }));
    await userEvent.click(screen.getByText("完整坐标与相邻关系", { selector: "summary" }));
    expect(screen.getByRole("region", { name: "已保存的相邻关系" })).toBeVisible();
    expect(screen.getByTestId("viewer-periodic-neighbor-source")).toHaveTextContent("最短周期距离");
    expect(screen.getByTestId("viewer-periodic-neighbor-authoritative")).toHaveTextContent("理想模型近邻");
    expect(screen.getByTestId("viewer-periodic-neighbor-table")).not.toHaveTextContent("参考共价半径");
    await userEvent.click(screen.getByRole("button", { name: "显示完整近邻" }));
    expect(screen.getByTestId("viewer-scene-renderer-summary")).toHaveTextContent("含 1 个周期副本");
    expect(screen.getByTestId("viewer-periodic-neighbor-row")).toHaveTextContent("范围内");
    fireEvent.keyDown(screen.getByTestId("viewer-scene-renderer-surface"), { key: "b" });
    expect(screen.getByRole("complementary", { name: "已选近邻连接" })).toBeVisible();
    await userEvent.click(screen.getByText("来源与判定", { selector: "summary" }));
    expect(screen.getByTestId("viewer-bond-inspector")).toHaveTextContent("理想模型中已保存的最短周期近邻");
    expect(screen.getByTestId("viewer-bond-inspector")).not.toHaveTextContent("参考共价半径");
  });

  it("identifies source radius previews as current near-neighbor candidates", async () => {
    let args: Parameters<ViewerRendererEngineFactory>[0] | undefined;
    const engine = fakeEngine();
    const original = periodicBoundaryScene();
    const payload = { ...original, metadata: { ...original.metadata, display_only: true,
      connectivity: { method: "covalent_radii", radius_scale: 1.15, radius_reference: "Cordero et al. 2008 / ASE", authoritative: false } } };
    render(<ViewerSceneRendererSurface payload={payload} capabilityOverride engineFactory={async value => { args = value; return engine; }} />);
    await waitFor(() => expect(args).toBeTruthy());
    expect(screen.getByRole("button", { name: "近邻连接" })).toBeVisible();
    act(() => args?.onSitePick?.({ siteIndex: 0, imageOffset: [0, 0, 0] }));
    await userEvent.click(screen.getByText("完整坐标与相邻关系", { selector: "summary" }));
    expect(screen.getByRole("region", { name: "当前预览的近邻关系" })).toBeVisible();
    expect(screen.getByTestId("viewer-periodic-neighbor-source")).toHaveTextContent("参考共价半径");
    expect(screen.getByTestId("viewer-periodic-neighbor-authoritative")).toHaveTextContent("近邻候选");
    expect(screen.getByTestId("viewer-periodic-neighbor-table")).not.toHaveTextContent("已保存");
    vi.mocked(engine.setSelection).mockClear();
    await userEvent.click(screen.getByRole("button", { name: "显示完整近邻" }));
    expect(screen.getByTestId("viewer-periodic-neighbor-row")).toHaveTextContent("范围内");
    expect(screen.getByRole("button", { name: /高亮指向位点 1/ })).toBeVisible();
    expect(engine.setSelection).toHaveBeenCalledWith([{ siteIndex: 0, imageOffset: [0, 0, 0] }]);
  });

  it("shows an actionable connection-limit notice while retaining the source atoms", async () => {
    const original = periodicBoundaryScene();
    const message = "近邻搜索超出快速预览范围，当前仅显示原子；可在研究中选择适合此结构的连接规则。";
    render(<ViewerSceneRendererSurface payload={{ ...original, metadata: { ...original.metadata, display_only: true },
      scene: { ...original.scene, bonds: [] }, warnings: [{ code: "VIEWER_PREVIEW_CONNECTIONS_UNAVAILABLE", message }] }} capabilityOverride engineFactory={async () => fakeEngine()} />);
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state")).toHaveTextContent("已就绪"));
    expect(screen.getByRole("button", { name: "近邻连接" })).toBeDisabled();
    expect(screen.getAllByText(message).some(node => node.classList.contains("notice"))).toBe(true);
    expect(screen.getByTestId("viewer-scene-renderer-summary")).toHaveTextContent("2 个位点");
  });

  it.each([-3, 3])("restores a source preview image at offset %s and clears it when hidden", async offset => {
    const original = periodicBoundaryScene();
    const onSiteSelection = vi.fn();
    const payload = { ...original, metadata: { ...original.metadata, display_only: true,
      connectivity: { method: "covalent_radii", radius_scale: 1.15, radius_reference: "Cordero et al. 2008 / ASE", authoritative: false } } };
    render(<ViewerSceneRendererSurface payload={payload} externalSiteId={`${original.scene.sites[0].element}-0:${offset}.0.0`} onSiteSelection={onSiteSelection} capabilityOverride engineFactory={async () => fakeEngine()} />);
    await waitFor(() => expect(screen.getByTestId("viewer-selected-site-image-offset")).toHaveTextContent(`[${offset}, 0, 0]`));
    expect(screen.getByTestId("viewer-scene-renderer-summary")).toHaveTextContent("3 个位点");
    expect(onSiteSelection).not.toHaveBeenCalled();
    await userEvent.click(screen.getByText("完整坐标与相邻关系", { selector: "summary" }));
    await userEvent.click(screen.getByRole("button", { name: "隐藏额外周期副本" }));
    expect(screen.queryByTestId("viewer-selected-site-image-offset")).toBeNull();
    expect(onSiteSelection).toHaveBeenLastCalledWith(null);
  });

  it("separates draft from applied state, uses presets, toggles the outer boundary, and downloads inert state",async()=>{
    const engine=fakeEngine(); const createUrl=vi.fn(()=>"blob:supercell"); Object.defineProperty(URL,"createObjectURL",{configurable:true,value:createUrl}); Object.defineProperty(URL,"revokeObjectURL",{configurable:true,value:vi.fn()}); const anchorClick=vi.spyOn(HTMLAnchorElement.prototype,"click").mockImplementation(()=>undefined);
    render(<ViewerSceneRendererSurface payload={periodicBoundaryScene()} capabilityOverride engineFactory={async()=>engine}/>);
    await waitFor(()=>expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toBe("已就绪"));
    await userEvent.click(screen.getByText("超晶胞", { selector: "summary" }));
    await userEvent.click(screen.getByRole("button",{name:"2 × 2 × 1"}));
    expect(screen.getByTestId("viewer-supercell-status").textContent).toContain("已应用 1 × 1 × 1");
    expect(screen.getByTestId("viewer-supercell-estimate").textContent).toContain("草稿 2 × 2 × 1");
    await userEvent.click(screen.getByTestId("viewer-supercell-apply"));
    await waitFor(()=>expect(screen.getByTestId("viewer-supercell-status").textContent).toContain("已应用 2 × 2 × 1"));
    await userEvent.click(screen.getByText("视角与裁剪", { selector: "summary" }));
    await userEvent.click(screen.getByTestId("viewer-scene-renderer-toggle-supercell-boundary"));
    expect(engine.setSupercellBoundaryVisible).toHaveBeenLastCalledWith(false);
    await userEvent.click(screen.getByTestId("viewer-supercell-download"));
    expect(createUrl).toHaveBeenCalledOnce(); expect(anchorClick).toHaveBeenCalled();
    anchorClick.mockRestore();
  });
  it("retains saved out-of-range neighbors in a single cell without offering an ineffective highlight", async () => {
    let args: Parameters<ViewerRendererEngineFactory>[0] | undefined;
    render(<ViewerSceneRendererSurface payload={periodicBoundaryScene()} capabilityOverride engineFactory={async value => { args = value; return fakeEngine(); }} />);
    await waitFor(() => expect(args).toBeTruthy());
    act(() => args?.onSitePick?.({ siteIndex: 0, imageOffset: [0, 0, 0] }));
    await userEvent.click(screen.getByText("完整坐标与相邻关系", { selector: "summary" }));
    expect(screen.getByTestId("viewer-selected-site-neighbors")).toHaveTextContent("1@[1,0,0]（1）");
    expect(screen.getByTestId("viewer-periodic-neighbor-row")).toHaveTextContent("Cl");
    expect(screen.getByTestId("viewer-periodic-neighbor-row")).toHaveTextContent("范围外");
    expect(screen.getByTestId("viewer-periodic-neighbor-distance")).toHaveTextContent("0.400000");
    expect(screen.queryByRole("button", { name: /高亮指向位点/ })).toBeNull();
    expect(screen.getByText("跨边界键合").nextElementSibling).toHaveTextContent("1");
    expect(screen.getByText("显示键合").nextElementSibling).toHaveTextContent("0");
    act(() => args?.onSitePick?.({ siteIndex: 1, imageOffset: [0, 0, 0] }));
    expect(screen.getByTestId("viewer-selected-site-neighbors")).toHaveTextContent("0@[-1,0,0]（1）");
    expect(screen.getByTestId("viewer-periodic-neighbor-row")).toHaveTextContent("Na");
  });

  it("shows periodic neighbor topology and highlights the stored target endpoint",async()=>{
    const engine=fakeEngine(); let args:Parameters<ViewerRendererEngineFactory>[0]|undefined; const onSiteSelection=vi.fn();
    render(<ViewerSceneRendererSurface payload={periodicBoundaryScene()} capabilityOverride engineFactory={async(value)=>{args=value;return engine;}} onSiteSelection={onSiteSelection}/>);
    await waitFor(()=>expect(args).toBeTruthy());
    await userEvent.click(screen.getByText("超晶胞", { selector: "summary" }));
    fireEvent.change(screen.getByTestId("viewer-supercell-x"), {target:{value:"2"}});
    await userEvent.click(screen.getByTestId("viewer-supercell-apply"));
    await waitFor(()=>expect(vi.mocked(engine.replaceScene).mock.calls.at(-1)?.[0].bonds).toHaveLength(1));
    act(()=>args?.onSitePick?.({siteIndex:0,imageOffset:[0,0,0]}));
    expect(onSiteSelection).toHaveBeenLastCalledWith({siteIndex:0,imageOffset:[0,0,0],siteId:"Na-0:0.0.0",species:"Na"});
    expect(screen.getByTestId("viewer-periodic-neighbor-offset").textContent).toContain("1, 0, 0");
    expect(screen.getByTestId("viewer-periodic-neighbor-distance").textContent).toBe("0.400000");
    expect(screen.getByTestId("viewer-periodic-neighbor-source").textContent).toBe("distance_cutoff");
    expect(screen.getByText(/周期相邻关系/).tagName).toBe("CAPTION");
    await userEvent.click(screen.getByText("完整坐标与相邻关系", { selector: "summary" }));
    const neighborButton=screen.getByRole("button",{name:/高亮指向位点 1/});
    await userEvent.click(neighborButton);
    expect(neighborButton.getAttribute("aria-pressed")).toBe("true");
    expect(engine.setSelection).toHaveBeenLastCalledWith([{siteIndex:0,imageOffset:[0,0,0]},{siteIndex:1,imageOffset:[1,0,0]}]);
  });
  it("leaves inspector keyboard navigation to the focused table and controls", async () => {
    const engine = fakeEngine(); let args: Parameters<ViewerRendererEngineFactory>[0] | undefined;
    render(<ViewerSceneRendererSurface payload={periodicBoundaryScene()} capabilityOverride engineFactory={async value => { args = value; return engine; }} />);
    await waitFor(() => expect(args).toBeTruthy());
    act(() => args?.onSitePick?.({ siteIndex: 0, imageOffset: [0, 0, 0] }));
    await userEvent.click(screen.getByText("完整坐标与相邻关系", { selector: "summary" }));
    const table = screen.getByRole("region", { name: "已保存的相邻关系" });
    expect(table).toHaveAttribute("tabindex", "0");
    expect(fireEvent.keyDown(table, { key: "ArrowRight" })).toBe(true);
    expect(fireEvent.keyDown(screen.getByRole("button", { name: "复制坐标" }), { key: "n" })).toBe(true);
    expect(engine.keyboardCamera).not.toHaveBeenCalled();
    expect(screen.getByTestId("viewer-selected-site-index")).toHaveTextContent("0");
    fireEvent.keyDown(screen.getByTestId("viewer-scene-renderer-surface"), { key: "ArrowRight" });
    expect(engine.keyboardCamera).toHaveBeenLastCalledWith("rotate_right");
  });
  it("maps a canonical bond pick to ordered endpoints, inspector, undo, and artifact download", async () => {
    const engine=fakeEngine(); let args:Parameters<ViewerRendererEngineFactory>[0]|undefined;
    const createUrl=vi.fn(()=>"blob:measurement"); const revokeUrl=vi.fn();
    Object.defineProperty(URL,"createObjectURL",{configurable:true,value:createUrl}); Object.defineProperty(URL,"revokeObjectURL",{configurable:true,value:revokeUrl});
    const anchorClick=vi.spyOn(HTMLAnchorElement.prototype,"click").mockImplementation(()=>undefined);
    render(<ViewerSceneRendererSurface payload={periodicBoundaryScene()} capabilityOverride engineFactory={async(value)=>{args=value;return engine;}}/>);
    await waitFor(()=>expect(args).toBeTruthy());
    await userEvent.click(screen.getByText("超晶胞", { selector: "summary" }));
    fireEvent.change(screen.getByTestId("viewer-supercell-x"),{target:{value:"2"}}); await userEvent.click(screen.getByTestId("viewer-supercell-apply"));
    await waitFor(()=>expect(vi.mocked(engine.replaceScene).mock.calls.at(-1)?.[0].bonds).toHaveLength(1));
    const expanded=vi.mocked(engine.replaceScene).mock.calls.at(-1)![0];
    await userEvent.click(screen.getByText("测量距离与角度", { selector: "summary" }));
    await userEvent.click(screen.getByRole("button",{name:"距离"}));
    act(()=>args?.onBondPick?.(expanded.bonds[0].id));
    expect(screen.getByTestId("viewer-selected-bond-id").textContent).toBe(expanded.bonds[0].id);
    expect(screen.getByTestId("viewer-measurement-selection").textContent).toContain("0@[0,0,0]");
    expect(screen.getByTestId("viewer-measurement-selection").textContent).toContain("1@[1,0,0]");
    await userEvent.click(screen.getByTestId("viewer-measurement-download")); expect(createUrl).toHaveBeenCalledOnce();
    await userEvent.click(screen.getByTestId("viewer-measurement-undo")); expect(screen.getByTestId("viewer-measurement-selection").textContent).toContain("1/2");
    anchorClick.mockRestore();
  });
  it("distinguishes displayed and minimum-image boundary measurements", async () => {
    const boundary = structuredClone(multiSpeciesScene) as Record<string, any>;
    boundary.scene.lattice.vectors = [[10,0,0],[0,10,0],[0,0,10]];
    boundary.scene.sites[0].frac = [0.98,0,0]; boundary.scene.sites[0].xyz = [9.8,0,0];
    boundary.scene.sites[1].frac = [0.02,0,0]; boundary.scene.sites[1].xyz = [0.2,0,0];
    let args: Parameters<ViewerRendererEngineFactory>[0] | undefined;
    render(<ViewerSceneRendererSurface payload={boundary} capabilityOverride engineFactory={async (value) => { args=value; return fakeEngine(); }} />);
    await waitFor(() => expect(args).toBeTruthy());
    await userEvent.click(screen.getByText("测量距离与角度", { selector: "summary" }));
    await userEvent.click(screen.getByRole("button", {name:"距离"}));
    act(() => { args?.onSitePick?.({siteIndex:0,imageOffset:[0,0,0]}); args?.onSitePick?.({siteIndex:1,imageOffset:[0,0,0]}); });
    expect(screen.getByTestId("viewer-measurement-result").textContent).toContain("9.600");
    await userEvent.click(screen.getByRole("button", {name:"最小周期像"}));
    act(() => { args?.onSitePick?.({siteIndex:0,imageOffset:[0,0,0]}); args?.onSitePick?.({siteIndex:1,imageOffset:[0,0,0]}); });
    expect(screen.getByTestId("viewer-measurement-result").textContent).toContain("0.400");
    expect(screen.getByTestId("viewer-periodic-measurement-offsets").textContent).toContain("1@[1,0,0]");
  });

  it("derives a bounded supercell and exposes periodic replica identity", async () => {
    const scenes: Parameters<ViewerRendererEngineFactory>[0]["scene"][]=[]; const engine=fakeEngine();
    let latest: Parameters<ViewerRendererEngineFactory>[0] | undefined;
    render(<ViewerSceneRendererSurface payload={multiSpeciesScene} capabilityOverride engineFactory={async (args) => { latest=args; scenes.push(args.scene); return engine; }} />);
    await waitFor(() => expect(scenes).toHaveLength(1));
    await userEvent.click(screen.getByText("超晶胞", { selector: "summary" }));
    fireEvent.change(screen.getByTestId("viewer-supercell-x"), {target:{value:"2"}});
    fireEvent.change(screen.getByTestId("viewer-supercell-y"), {target:{value:"2"}});
    fireEvent.change(screen.getByTestId("viewer-supercell-z"), {target:{value:"2"}});
    await userEvent.click(screen.getByTestId("viewer-supercell-apply"));
    await waitFor(() => expect(vi.mocked(engine.replaceScene).mock.calls.at(-1)?.[0].atoms).toHaveLength(16));
    const replica=vi.mocked(engine.replaceScene).mock.calls.at(-1)?.[0].atoms.find((atom)=>atom.siteIndex===1&&atom.ref.imageOffset[0]===1);
    expect(replica).toBeTruthy();
    act(()=>latest?.onSitePick?.(replica!.ref));
    expect(screen.getByTestId("viewer-selected-site-index").textContent).toBe("1");
    expect(screen.getByTestId("viewer-selected-site-image-offset").textContent).toContain("1, 0, 0");
    expect(screen.getByText("跳转到主位点")).toBeTruthy();
  });

  it("refuses an over-cap derived supercell without replacing the current renderer", async () => {
    const large = structuredClone(minimalScene) as Record<string, any>;
    large.scene.sites = Array.from({length:256}, (_, index) => ({...large.scene.sites[0], index, label:`Si${index + 1}`, xyz:[index % 8, Math.floor(index / 8) % 8, Math.floor(index / 64)], frac:[(index % 8) / 8, (Math.floor(index / 8) % 8) / 8, Math.floor(index / 64) / 4]}));
    large.metadata.site_count = 256;
    const factory = vi.fn(async () => fakeEngine()) satisfies ViewerRendererEngineFactory;
    render(<ViewerSceneRendererSurface payload={large} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(factory).toHaveBeenCalledOnce());
    await userEvent.click(screen.getByText("超晶胞", { selector: "summary" }));
    for (const axis of ["x","y","z"] as const) fireEvent.change(screen.getByTestId(`viewer-supercell-${axis}`), {target:{value:"3"}});
    await userEvent.click(screen.getByTestId("viewer-supercell-apply"));
    expect(screen.getByTestId("viewer-supercell-status").textContent).toContain("请求 6912 个位点");
    expect(screen.getByTestId("viewer-supercell-status").textContent).toContain("限制为 2048");
    expect(factory).toHaveBeenCalledOnce();
  });

  it("uses degraded GPU settings without truncating a near-cap supercell", async () => {
    const large = structuredClone(minimalScene) as Record<string, any>;
    large.scene.sites = Array.from({length:64}, (_, index) => ({...large.scene.sites[0], index, label:`Si${index + 1}`, xyz:[index % 4, Math.floor(index / 4) % 4, Math.floor(index / 16)], frac:[(index % 4) / 4, (Math.floor(index / 4) % 4) / 4, Math.floor(index / 16) / 4]}));
    large.metadata.site_count = 64;
    const calls: Parameters<ViewerRendererEngineFactory>[0][] = []; const engine=fakeEngine();
    render(<ViewerSceneRendererSurface payload={large} capabilityOverride engineFactory={async (args) => { calls.push(args); return engine; }} />);
    await waitFor(() => expect(calls).toHaveLength(1));
    await userEvent.click(screen.getByText("超晶胞", { selector: "summary" }));
    for (const axis of ["x","y","z"] as const) fireEvent.change(screen.getByTestId(`viewer-supercell-${axis}`), {target:{value:"3"}});
    await userEvent.click(screen.getByTestId("viewer-supercell-apply"));
    await waitFor(() => expect(vi.mocked(engine.replaceScene)).toHaveBeenCalled());
    expect(vi.mocked(engine.replaceScene).mock.calls.at(-1)?.slice(1)).toEqual(["degraded",1]);
    expect(vi.mocked(engine.replaceScene).mock.calls.at(-1)?.[0].atoms).toHaveLength(1_728);
    expect(screen.getByTestId("viewer-scene-renderer-performance-warning").textContent).toContain("当前结构较大");
  });

  it("surfaces an authoritative shown/total truncation warning", async () => {
    const payload = structuredClone(minimalScene) as Record<string, any>;
    payload.warnings = [{ code: "VIEWER_SCENE_SITES_TRUNCATED", message: "当前显示前 256 / 512 个站点；完整结构仍保留在源数据中。" }];
    const factory = vi.fn(async () => fakeEngine()) satisfies ViewerRendererEngineFactory;
    render(<ViewerSceneRendererSurface payload={payload} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(factory).toHaveBeenCalledOnce());
    expect(screen.getByTestId("viewer-scene-renderer-truncation-warning").textContent).toContain("256 / 512");
    expect(screen.getByTestId("viewer-scene-renderer-summary").textContent).toContain("1 个位点");
  });

  it("disposes a stale asynchronous engine generation after a scene switch", async () => {
    let resolveFirst: ((engine: ViewerRendererEngine) => void) | undefined;
    const stale = fakeEngine();
    const current = fakeEngine();
    const factory = vi.fn()
      .mockImplementationOnce(() => new Promise<ViewerRendererEngine>((resolve) => { resolveFirst = resolve; }))
      .mockResolvedValueOnce(current) as ViewerRendererEngineFactory;
    const {rerender} = render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(factory).toHaveBeenCalledOnce());
    rerender(<ViewerSceneRendererSurface payload={multiSpeciesScene} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(factory).toHaveBeenCalledTimes(2));
    act(() => resolveFirst?.(stale));
    await waitFor(() => expect(stale.dispose).toHaveBeenCalledOnce());
    expect(current.dispose).not.toHaveBeenCalled();
  });

  it("initializes a validated scene and exposes accessible controls", async () => {
    const engine = fakeEngine();
    const factory = vi.fn(async () => engine) satisfies ViewerRendererEngineFactory;
    const user = userEvent.setup();
    render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("已就绪"));
    expect(factory).toHaveBeenCalledOnce();
    expect((screen.getByRole("button", { name: "重置相机" }) as HTMLButtonElement).disabled).toBe(false);
    await user.click(screen.getByTestId("viewer-scene-renderer-reset"));
    expect(engine.resetCamera).toHaveBeenCalledOnce();
    await userEvent.click(screen.getByText("视角与裁剪", { selector: "summary" }));
    await user.click(screen.getByTestId("viewer-scene-renderer-toggle-cell"));
    expect(screen.getByTestId("viewer-scene-renderer-audit").textContent).toContain("晶胞边0");
    await user.click(screen.getByTestId("viewer-scene-renderer-toggle-bonds"));
    expect(screen.getByTestId("viewer-scene-renderer-audit").textContent).toContain("键合0");
  });

  it("applies bounded clipping, lattice axes, and deterministic camera presets", async () => {
    const engine=fakeEngine();
    render(<ViewerSceneRendererSurface payload={multiSpeciesScene} capabilityOverride engineFactory={async()=>engine}/>);
    await waitFor(()=>expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toBe("已就绪"));
    await userEvent.click(screen.getByText("视角与裁剪", { selector: "summary" }));
    await userEvent.click(screen.getByTestId("viewer-clipping-enabled"));
    await userEvent.click(screen.getByTestId("viewer-clip-x-enabled"));
    fireEvent.change(screen.getByTestId("viewer-clip-x-position"),{target:{value:"1"}});
    expect(engine.setClipState).toHaveBeenLastCalledWith(expect.objectContaining({enabled:true,planes:expect.arrayContaining([expect.objectContaining({axis:"x",position:1,enabled:true})])}));
    expect(screen.getByTestId("viewer-clipping-status").textContent).toContain("X 位于 1.000 Å");
    await userEvent.click(screen.getByTestId("viewer-lattice-axes"));
    expect(engine.setLatticeAxesVisible).toHaveBeenLastCalledWith(true);
    await userEvent.click(screen.getByTestId("viewer-camera-top"));
    expect(engine.setCameraPreset).toHaveBeenLastCalledWith("top");
    expect(screen.getByTestId("viewer-camera-status").textContent).toContain("顶部");
  });

  it("provides bounded keyboard camera controls without trapping form inputs", async () => {
    const engine = fakeEngine();
    render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={async () => engine} />);
    const region = await screen.findByRole("region", {name:"三维结构查看器"});
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("已就绪"));
    region.focus();
    fireEvent.keyDown(region, {key:"ArrowLeft"});
    fireEvent.keyDown(region, {key:"ArrowUp", shiftKey:true});
    fireEvent.keyDown(region, {key:"+"});
    expect(engine.keyboardCamera).toHaveBeenNthCalledWith(1,"rotate_left");
    expect(engine.keyboardCamera).toHaveBeenNthCalledWith(2,"pan_up");
    expect(engine.keyboardCamera).toHaveBeenNthCalledWith(3,"zoom_in");
    fireEvent.keyDown(region, {key:"r"});
    expect(engine.resetCamera).toHaveBeenCalledOnce();
    await userEvent.click(screen.getByText("超晶胞", { selector: "summary" }));
    const input=screen.getByTestId("viewer-supercell-x");
    fireEvent.keyDown(input,{key:"ArrowLeft"});
    expect(engine.keyboardCamera).toHaveBeenCalledTimes(3);
    expect(region.getAttribute("aria-keyshortcuts")).toContain("Shift+ArrowLeft");
  });

  it("maps engine picks to canonical inspector fields and measurements", async () => {
    const engine = fakeEngine();
    const writeText = vi.fn(async () => { throw new Error("clipboard denied"); });
    let engineArgs: Parameters<ViewerRendererEngineFactory>[0] | undefined;
    const factory = vi.fn(async (args: Parameters<ViewerRendererEngineFactory>[0]) => { engineArgs = args; return engine; }) satisfies ViewerRendererEngineFactory;
    const user = userEvent.setup();
    Object.defineProperty(navigator, "clipboard", { configurable: true, value: { writeText } });
    render(<ViewerSceneRendererSurface payload={multiSpeciesScene} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(factory).toHaveBeenCalledOnce());
    const onSitePick = engineArgs?.onSitePick;
    act(() => onSitePick?.({siteIndex:0,imageOffset:[0,0,0]}));
    expect(screen.getByTestId("viewer-selected-site-index").textContent).toContain("0");
    expect(screen.getByTestId("viewer-scene-semantic-summary").textContent).toContain("0@[0,0,0]");
    expect(screen.getByTestId("viewer-scene-accessibility-announcement").textContent).toContain("已选择位点 0");
    expect(screen.getByTestId("viewer-selected-site-cartesian").textContent).toContain("0, 0, 0");
    await userEvent.click(screen.getByText("完整坐标与相邻关系", { selector: "summary" }));
    await user.click(screen.getByRole("button", { name: "复制位点 JSON" }));
    expect(writeText).toHaveBeenCalledOnce();
    await userEvent.click(screen.getByText("测量距离与角度", { selector: "summary" }));
    await user.click(screen.getByRole("button", { name: "距离" }));
    act(() => { onSitePick?.({siteIndex:0,imageOffset:[0,0,0]}); onSitePick?.({siteIndex:1,imageOffset:[0,0,0]}); });
    await waitFor(() => expect(screen.getByTestId("viewer-measurement-result").textContent).toContain("distance"));
    expect(engine.setSelection).toHaveBeenLastCalledWith([{siteIndex:0,imageOffset:[0,0,0]}, {siteIndex:1,imageOffset:[0,0,0]}]);
    delete (navigator as unknown as { clipboard?: unknown }).clipboard;
  });

  it("exports a bounded local PNG and clears selection when the scene changes", async () => {
    const engine = fakeEngine();
    const factory = vi.fn(async () => engine) satisfies ViewerRendererEngineFactory;
    const createUrl = vi.fn(() => "blob:local-viewer");
    const revokeUrl = vi.fn();
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createUrl });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revokeUrl });
    const anchorClick = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    const { rerender } = render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("已就绪"));
    await userEvent.click(screen.getByText("高级导出"));
    await userEvent.click(screen.getByTestId("viewer-scene-export-png"));
    expect(engine.exportPng).toHaveBeenCalledOnce();
    expect(engine.exportPng).toHaveBeenCalledWith(expect.objectContaining({width:1600,height:1200,pixelRatio:1,background:"light"}));
    await waitFor(() => expect(createUrl).toHaveBeenCalledOnce());
    rerender(<ViewerSceneRendererSurface payload={{ ...minimalScene, metadata: { ...minimalScene.metadata, title: "changed" } }} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(engine.setSelection).toHaveBeenCalledWith([]));
    await Promise.resolve();
    expect(revokeUrl).toHaveBeenCalled();
    delete (URL as unknown as { createObjectURL?: unknown }).createObjectURL;
    delete (URL as unknown as { revokeObjectURL?: unknown }).revokeObjectURL;
    anchorClick.mockRestore();
  });

  it("keeps one export active and reports renderer export failures safely", async () => {
    let rejectExport: ((reason?: unknown) => void) | undefined;
    const engine = fakeEngine();
    vi.mocked(engine.exportPng).mockImplementation(() => new Promise<Blob>((_resolve, reject) => { rejectExport = reject; }));
    render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={async () => engine} />);
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toBe("已就绪"));
    await userEvent.click(screen.getByText("高级导出"));
    await userEvent.click(screen.getByTestId("viewer-scene-export-png"));
    expect((screen.getByTestId("viewer-scene-export-png") as HTMLButtonElement).disabled).toBe(true);
    expect(engine.exportPng).toHaveBeenCalledOnce();
    act(() => rejectExport?.(new Error("private renderer details")));
    await waitFor(() => expect(screen.getByTestId("viewer-scene-export-error").textContent).toContain("导出失败"));
    expect(screen.getByTestId("viewer-scene-export-error").textContent).not.toContain("private renderer details");
    expect((screen.getByTestId("viewer-scene-export-png") as HTMLButtonElement).disabled).toBe(false);
  });

  it("rejects a stale asynchronous export after a scene switch", async () => {
    let resolveExport: ((blob: Blob) => void) | undefined;
    const engine = fakeEngine();
    vi.mocked(engine.exportPng).mockImplementation(() => new Promise<Blob>((resolve) => { resolveExport = resolve; }));
    const createUrl = vi.fn(() => "blob:must-not-download");
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createUrl });
    const changed = structuredClone(minimalScene) as Record<string, any>;
    changed.metadata.title = "Changed during export";
    const {rerender} = render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={async () => engine} />);
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toBe("已就绪"));
    await userEvent.click(screen.getByText("高级导出"));
    await userEvent.click(screen.getByTestId("viewer-scene-export-png"));
    rerender(<ViewerSceneRendererSurface payload={changed} capabilityOverride engineFactory={async () => engine} />);
    await act(async () => resolveExport?.(new Blob(["stale"], {type:"image/png"})));
    expect(screen.getByTestId("viewer-export-status").textContent).toContain("尚未准备导出");
    expect(screen.queryByTestId("viewer-scene-export-error")).not.toBeInTheDocument();
    expect(createUrl).not.toHaveBeenCalled();
    delete (URL as unknown as { createObjectURL?: unknown }).createObjectURL;
  });

  it("keeps the new scene's export busy when the previous scene fails late", async () => {
    const oldEngine = fakeEngine();
    const newEngine = fakeEngine();
    let failOld!: (error: Error) => void;
    let failNew!: (error: Error) => void;
    vi.mocked(oldEngine.exportPng).mockImplementation(() => new Promise((_resolve, reject) => { failOld = reject; }));
    vi.mocked(newEngine.exportPng).mockImplementation(() => new Promise((_resolve, reject) => { failNew = reject; }));
    const factory = vi.fn().mockResolvedValueOnce(oldEngine).mockResolvedValue(newEngine);
    const view = render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state")).toHaveTextContent("已就绪"));
    await userEvent.click(screen.getByText("高级导出"));
    await userEvent.click(screen.getByTestId("viewer-scene-export-png"));
    view.rerender(<ViewerSceneRendererSurface payload={{...minimalScene, metadata:{...minimalScene.metadata,title:"new source"}}} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.getByTestId("viewer-scene-export-png")).toBeEnabled());
    await userEvent.click(screen.getByTestId("viewer-scene-export-png"));
    await act(async () => failOld(new Error("old source failure")));
    expect(screen.getByTestId("viewer-scene-export-png")).toBeDisabled();
    expect(screen.getByTestId("viewer-export-status")).toHaveTextContent("正在准备导出");
    expect(screen.queryByTestId("viewer-scene-export-error")).not.toBeInTheDocument();
    await act(async () => failNew(new Error("current source failure")));
    expect(screen.getByTestId("viewer-scene-export-png")).toBeEnabled();
    expect(screen.getByTestId("viewer-export-status")).toHaveTextContent("导出失败");
  });

  it("invalidates a prepared bundle when orbit controls change the camera", async () => {
    const engine=fakeEngine();let args:Parameters<ViewerRendererEngineFactory>[0]|undefined;
    const createUrl=vi.fn(()=>"blob:export");Object.defineProperty(URL,"createObjectURL",{configurable:true,value:createUrl});Object.defineProperty(URL,"revokeObjectURL",{configurable:true,value:vi.fn()});const anchorClick=vi.spyOn(HTMLAnchorElement.prototype,"click").mockImplementation(()=>undefined);
    render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={async(value)=>{args=value;return engine;}}/>);
    await waitFor(()=>expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toBe("已就绪"));
    await userEvent.click(screen.getByTestId("viewer-scene-export-png"));
    await waitFor(()=>expect((screen.getByRole("button",{name:"下载导出清单"}) as HTMLButtonElement).disabled).toBe(false));
    act(()=>args?.onViewChange?.());
    expect((screen.getByRole("button",{name:"下载导出清单"}) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getByTestId("viewer-export-status").textContent).toContain("查看状态已变化");
    anchorClick.mockRestore();
  });

  it("rejects an invalid scene without initializing an engine", () => {
    const payload = structuredClone(minimalScene) as Record<string, any>;
    payload.scene.sites[0].xyz[0] = Number.NaN;
    const factory = vi.fn(async () => fakeEngine()) satisfies ViewerRendererEngineFactory;
    render(<ViewerSceneRendererSurface payload={payload} capabilityOverride engineFactory={factory} />);
    expect(screen.getByTestId("viewer-scene-renderer-invalid").textContent).toContain("VIEWER_SCENE_COORDINATE_NON_FINITE");
    expect(factory).not.toHaveBeenCalled();
    expect(document.querySelector("canvas")).toBeNull();
  });

  it("shows the unsupported fallback while preserving a validated audit", () => {
    const factory = vi.fn(async () => fakeEngine()) satisfies ViewerRendererEngineFactory;
    render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride={false} engineFactory={factory} />);
    expect(screen.getByTestId("viewer-scene-renderer-unavailable").textContent).toContain("结构数据和来源记录仍然保留");
    expect(factory).not.toHaveBeenCalled();
  });

  it("disposes on artifact change and unmount without duplicate initialization", async () => {
    const firstDispose = vi.fn();
    const secondDispose = vi.fn();
    const factory = vi.fn()
      .mockResolvedValueOnce(fakeEngine(firstDispose))
      .mockResolvedValueOnce(fakeEngine(secondDispose)) as ViewerRendererEngineFactory;
    const { rerender, unmount } = render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(factory).toHaveBeenCalledTimes(1));
    const changed = structuredClone(minimalScene) as Record<string, any>;
    changed.metadata.title = "Changed artifact";
    rerender(<ViewerSceneRendererSurface payload={changed} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(factory).toHaveBeenCalledTimes(2));
    expect(firstDispose).toHaveBeenCalledOnce();
    unmount();
    expect(secondDispose).toHaveBeenCalledOnce();
  });

  it("handles a synthetic context loss as a safe fallback", async () => {
    let loseContext = () => {};
    const factory: ViewerRendererEngineFactory = async ({ onContextLost }) => {
      loseContext = onContextLost;
      return fakeEngine();
    };
    render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("已就绪"));
    fireEvent(window, new Event("noop"));
    loseContext();
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-fallback").textContent).toContain("图形上下文已中断"));
  });

  it("shows an accessible chunk failure fallback and retries the loader", async () => {
    const factory = vi.fn()
      .mockRejectedValueOnce(new (await import("./viewerSceneRendererErrors")).ViewerRendererError("VIEWER_RENDERER_CHUNK_LOAD_FAILED", "blocked"))
      .mockResolvedValueOnce(fakeEngine()) as ViewerRendererEngineFactory;
    const user = userEvent.setup();
    render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.getByText("渲染模块不可用")).toBeTruthy());
    await user.click(screen.getByRole("button", { name: "重试渲染" }));
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("已就绪"));
    expect(factory).toHaveBeenCalledTimes(2);
  });

  it("distinguishes renderer initialization failure and offers a safe retry", async () => {
    const factory = vi.fn()
      .mockRejectedValueOnce(new (await import("./viewerSceneRendererErrors")).ViewerRendererError("VIEWER_RENDERER_INITIALIZATION_FAILED", "no context"))
      .mockResolvedValueOnce(fakeEngine()) as ViewerRendererEngineFactory;
    const user = userEvent.setup();
    render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.getByText("渲染器初始化失败")).toBeInTheDocument());
    expect(screen.getByText("VIEWER_RENDERER_INITIALIZATION_FAILED")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "重试渲染" }));
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("已就绪"));
    expect(factory).toHaveBeenCalledTimes(2);
  });

  it("exposes a textual scene summary, species legend, live status, and metrics", async () => {
    render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={async () => fakeEngine()} />);
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("已就绪"));
    expect(screen.getByRole("region", { name: "三维结构查看器" })).toBeTruthy();
    expect(screen.getByTestId("viewer-scene-renderer-summary").textContent).toContain("1 个位点");
    expect(screen.getByRole("list", { name: "元素图例" }).textContent).toContain("Si");
    expect(screen.getByTestId("viewer-scene-renderer-metrics").textContent).toContain("instancedMeshCount");
    expect(screen.getByTestId("viewer-scene-semantic-summary").textContent).toContain("跨边界键合");
  });

  it("disposes every renderer across twenty bounded artifact switches", async () => {
    const disposals = Array.from({ length: 21 }, () => vi.fn());
    let call = 0;
    const factory: ViewerRendererEngineFactory = async () => fakeEngine(disposals[call++]);
    const { rerender, unmount } = render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(call).toBe(1));
    for (let index = 1; index <= 20; index += 1) {
      const changed = structuredClone(minimalScene) as Record<string, any>;
      changed.metadata.title = `switch-${index}`;
      rerender(<ViewerSceneRendererSurface payload={changed} capabilityOverride engineFactory={factory} />);
      await waitFor(() => expect(call).toBe(index + 1));
      expect(disposals[index - 1]).toHaveBeenCalledOnce();
    }
    unmount();
    expect(disposals[20]).toHaveBeenCalledOnce();
  });

  it.each(["Si-0:0.0.0", "Si-0:1.0.0", "Si-0:-1.0.0"])("restores the exact periodic site %s without publishing a new selection", async (siteId) => {
    const listener = vi.fn();
    const factory: ViewerRendererEngineFactory = async () => fakeEngine();
    const { rerender } = render(<ViewerSceneRendererSurface payload={minimalScene} externalSiteId={siteId} onSiteSelection={listener} capabilityOverride engineFactory={factory} />);
    await screen.findByTestId("viewer-selected-site-index");
    const match = /^Si-(\d+):(.+)$/.exec(siteId)!;
    expect(screen.getByTestId("viewer-selected-site-index")).toHaveTextContent(match[1]);
    expect(screen.getByTestId("viewer-selected-site-image-offset")).toHaveTextContent(`[${match[2].split(".").join(", ")}]`);
    expect(listener).not.toHaveBeenCalled();
    rerender(<ViewerSceneRendererSurface payload={minimalScene} externalSiteId={null} onSiteSelection={listener} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.queryByTestId("viewer-selected-site-index")).not.toBeInTheDocument());
    expect(listener).not.toHaveBeenCalled();
  });

  it.each(["Fe-0:0.0.0", "Si-99:0.0.0", "Si-0:99.0.0", "Si-0:-2.0.0", "broken"])("does not substitute another atom for unavailable site %s", async (siteId) => {
    render(<ViewerSceneRendererSurface payload={minimalScene} externalSiteId={siteId} capabilityOverride engineFactory={async () => fakeEngine()} />);
    expect(await screen.findByRole("alert")).toHaveTextContent("链接中的位点当前无法显示");
    expect(screen.queryByTestId("viewer-selected-site-index")).not.toBeInTheDocument();
  });

  it("publishes committed selection and clear for toggles, undo and Escape", async () => {
    const listener = vi.fn();
    let pick: Parameters<ViewerRendererEngineFactory>[0]["onSitePick"];
    const factory: ViewerRendererEngineFactory = async args => { pick = args.onSitePick; return fakeEngine(); };
    render(<ViewerSceneRendererSurface payload={minimalScene} onSiteSelection={listener} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(pick).toBeTypeOf("function"));
    act(() => pick?.({ siteIndex: 0, imageOffset: [0, 0, 0] }));
    expect(listener).toHaveBeenLastCalledWith(expect.objectContaining({ siteId: "Si-0:0.0.0" }));
    act(() => pick?.({ siteIndex: 0, imageOffset: [0, 0, 0] }));
    expect(listener).toHaveBeenLastCalledWith(null);
    const surface = screen.getByRole("region", { name: "三维结构查看器" });
    fireEvent.keyDown(surface, { key: "n" });
    fireEvent.keyDown(surface, { key: "Backspace" });
    expect(listener).toHaveBeenLastCalledWith(null);
    fireEvent.keyDown(surface, { key: "n" });
    fireEvent.keyDown(surface, { key: "Escape" });
    expect(listener).toHaveBeenLastCalledWith(null);
  });

  it("cycles through every displayed atom with N before wrapping to the first", async () => {
    const payload = structuredClone(minimalScene);
    payload.scene.sites = [0, 1, 2].map(index => ({ ...payload.scene.sites[0], index, label: `Si${index + 1}`, xyz: [index, 0, 0], frac: [index / 5, 0, 0] }));
    payload.metadata.site_count = 3;
    const factory: ViewerRendererEngineFactory = async () => fakeEngine();
    render(<ViewerSceneRendererSurface payload={payload} capabilityOverride engineFactory={factory} />);
    const surface = screen.getByRole("region", { name: "三维结构查看器" });
    for (const expected of [0, 1, 2, 0]) {
      fireEvent.keyDown(surface, { key: "n" });
      expect(screen.getByTestId("viewer-selected-site-index")).toHaveTextContent(String(expected));
    }
  });

  it("applies a restored supercell to a renderer that finishes loading after selection recovery", async () => {
    const engine = fakeEngine();
    let resolve!: (engine: ViewerRendererEngine) => void;
    const factory: ViewerRendererEngineFactory = () => new Promise(done => { resolve = done; });
    render(<ViewerSceneRendererSurface payload={minimalScene} externalSiteId="Si-0:1.0.0" capabilityOverride engineFactory={factory} />);
    await screen.findByTestId("viewer-selected-site-index");
    await act(async () => resolve(engine));
    expect(engine.replaceScene).toHaveBeenCalledWith(expect.objectContaining({ atoms: expect.any(Array), supercellRepeat: [2, 1, 1] }), "interactive", expect.any(Number));
    expect(vi.mocked(engine.replaceScene).mock.calls[0][0].atoms).toHaveLength(2);
    expect(engine.setSelection).toHaveBeenLastCalledWith([{ siteIndex: 0, imageOffset: [1, 0, 0] }]);
    expect(screen.getByTestId("viewer-scene-accessibility-announcement")).toHaveTextContent("共 2 个显示位点");
  });
});
