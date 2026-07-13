import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import minimalScene from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_minimal_crystal.viewer_scene.v1.json";
import multiSpeciesScene from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_multi_species_crystal.viewer_scene.v1.json";
import { ViewerSceneRendererSurface } from "./ViewerSceneRendererSurface";
import type { ViewerRendererEngine, ViewerRendererEngineFactory, ViewerRendererSnapshot } from "./viewerSceneRendererTypes";
import { periodicBoundaryScene } from "./viewerScenePeriodicBondTestFixture";

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
    setCellVisible(value) { cellVisible = value; },
    setBondsVisible(value) { bondsVisible = value; },
    setSelection: vi.fn(),
    setBondSelection: vi.fn(),
    exportPng: vi.fn(async () => new Blob(["png"], { type: "image/png" })),
    render: vi.fn(),
    keyboardCamera: vi.fn(),
    snapshot,
    dispose,
  };
  return engine;
}

describe("ViewerSceneRendererSurface", () => {
  it("shows periodic neighbor topology and highlights the stored target endpoint",async()=>{
    const engine=fakeEngine(); let args:Parameters<ViewerRendererEngineFactory>[0]|undefined;
    render(<ViewerSceneRendererSurface payload={periodicBoundaryScene()} capabilityOverride engineFactory={async(value)=>{args=value;return engine;}}/>);
    await waitFor(()=>expect(args).toBeTruthy());
    fireEvent.change(screen.getByTestId("viewer-supercell-x"), {target:{value:"2"}});
    await userEvent.click(screen.getByTestId("viewer-supercell-apply"));
    await waitFor(()=>expect(args?.scene.bonds).toHaveLength(1));
    act(()=>args?.onSitePick?.({siteIndex:0,imageOffset:[0,0,0]}));
    expect(screen.getByTestId("viewer-periodic-neighbor-offset").textContent).toContain("1, 0, 0");
    expect(screen.getByTestId("viewer-periodic-neighbor-distance").textContent).toBe("0.400000");
    expect(screen.getByTestId("viewer-periodic-neighbor-source").textContent).toBe("distance_cutoff");
    expect(screen.getByText(/Periodic neighbor relationships/).tagName).toBe("CAPTION");
    const neighborButton=screen.getByRole("button",{name:/Highlight bond to site 1/});
    await userEvent.click(neighborButton);
    expect(neighborButton.getAttribute("aria-pressed")).toBe("true");
    expect(engine.setSelection).toHaveBeenLastCalledWith([{siteIndex:0,imageOffset:[0,0,0]},{siteIndex:1,imageOffset:[1,0,0]}]);
  });
  it("maps a canonical bond pick to ordered endpoints, inspector, undo, and artifact download", async () => {
    const engine=fakeEngine(); let args:Parameters<ViewerRendererEngineFactory>[0]|undefined;
    const createUrl=vi.fn(()=>"blob:measurement"); const revokeUrl=vi.fn();
    Object.defineProperty(URL,"createObjectURL",{configurable:true,value:createUrl}); Object.defineProperty(URL,"revokeObjectURL",{configurable:true,value:revokeUrl});
    const anchorClick=vi.spyOn(HTMLAnchorElement.prototype,"click").mockImplementation(()=>undefined);
    render(<ViewerSceneRendererSurface payload={periodicBoundaryScene()} capabilityOverride engineFactory={async(value)=>{args=value;return engine;}}/>);
    await waitFor(()=>expect(args).toBeTruthy());
    fireEvent.change(screen.getByTestId("viewer-supercell-x"),{target:{value:"2"}}); await userEvent.click(screen.getByTestId("viewer-supercell-apply"));
    await waitFor(()=>expect(args?.scene.bonds).toHaveLength(1));
    await userEvent.click(screen.getByRole("button",{name:"Distance"}));
    act(()=>args?.onBondPick?.(args!.scene.bonds[0].id));
    expect(screen.getByTestId("viewer-selected-bond-id").textContent).toBe(args!.scene.bonds[0].id);
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
    await userEvent.click(screen.getByRole("button", {name:"Distance"}));
    act(() => { args?.onSitePick?.({siteIndex:0,imageOffset:[0,0,0]}); args?.onSitePick?.({siteIndex:1,imageOffset:[0,0,0]}); });
    expect(screen.getByTestId("viewer-measurement-result").textContent).toContain("9.600");
    await userEvent.click(screen.getByRole("button", {name:"Minimum image (periodic)"}));
    act(() => { args?.onSitePick?.({siteIndex:0,imageOffset:[0,0,0]}); args?.onSitePick?.({siteIndex:1,imageOffset:[0,0,0]}); });
    expect(screen.getByTestId("viewer-measurement-result").textContent).toContain("0.400");
    expect(screen.getByTestId("viewer-periodic-measurement-offsets").textContent).toContain("1@[1,0,0]");
  });

  it("derives a bounded supercell and exposes periodic replica identity", async () => {
    const scenes: Parameters<ViewerRendererEngineFactory>[0]["scene"][]=[];
    let latest: Parameters<ViewerRendererEngineFactory>[0] | undefined;
    render(<ViewerSceneRendererSurface payload={multiSpeciesScene} capabilityOverride engineFactory={async (args) => { latest=args; scenes.push(args.scene); return fakeEngine(); }} />);
    await waitFor(() => expect(scenes).toHaveLength(1));
    fireEvent.change(screen.getByTestId("viewer-supercell-x"), {target:{value:"2"}});
    fireEvent.change(screen.getByTestId("viewer-supercell-y"), {target:{value:"2"}});
    fireEvent.change(screen.getByTestId("viewer-supercell-z"), {target:{value:"2"}});
    await userEvent.click(screen.getByTestId("viewer-supercell-apply"));
    await waitFor(() => expect(scenes.at(-1)?.atoms).toHaveLength(16));
    const replica=scenes.at(-1)?.atoms.find((atom)=>atom.siteIndex===1&&atom.ref.imageOffset[0]===1);
    expect(replica).toBeTruthy();
    act(()=>latest?.onSitePick?.(replica!.ref));
    expect(screen.getByTestId("viewer-selected-site-index").textContent).toBe("1");
    expect(screen.getByTestId("viewer-selected-site-image-offset").textContent).toContain("1, 0, 0");
    expect(screen.getByText("Jump to primary image")).toBeTruthy();
  });

  it("refuses an over-cap derived supercell without replacing the current renderer", async () => {
    const large = structuredClone(minimalScene) as Record<string, any>;
    large.scene.sites = Array.from({length:256}, (_, index) => ({...large.scene.sites[0], index, label:`Si${index + 1}`, xyz:[index % 8, Math.floor(index / 8) % 8, Math.floor(index / 64)], frac:[(index % 8) / 8, (Math.floor(index / 8) % 8) / 8, Math.floor(index / 64) / 4]}));
    large.metadata.site_count = 256;
    const factory = vi.fn(async () => fakeEngine()) satisfies ViewerRendererEngineFactory;
    render(<ViewerSceneRendererSurface payload={large} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(factory).toHaveBeenCalledOnce());
    for (const axis of ["x","y","z"] as const) fireEvent.change(screen.getByTestId(`viewer-supercell-${axis}`), {target:{value:"3"}});
    await userEvent.click(screen.getByTestId("viewer-supercell-apply"));
    expect(screen.getByTestId("viewer-supercell-status").textContent).toContain("requested 6912 sites");
    expect(screen.getByTestId("viewer-supercell-status").textContent).toContain("limits are 2048");
    expect(factory).toHaveBeenCalledOnce();
  });

  it("uses degraded GPU settings without truncating a near-cap supercell", async () => {
    const large = structuredClone(minimalScene) as Record<string, any>;
    large.scene.sites = Array.from({length:64}, (_, index) => ({...large.scene.sites[0], index, label:`Si${index + 1}`, xyz:[index % 4, Math.floor(index / 4) % 4, Math.floor(index / 16)], frac:[(index % 4) / 4, (Math.floor(index / 4) % 4) / 4, Math.floor(index / 16) / 4]}));
    large.metadata.site_count = 64;
    const calls: Parameters<ViewerRendererEngineFactory>[0][] = [];
    render(<ViewerSceneRendererSurface payload={large} capabilityOverride engineFactory={async (args) => { calls.push(args); return fakeEngine(); }} />);
    await waitFor(() => expect(calls).toHaveLength(1));
    for (const axis of ["x","y","z"] as const) fireEvent.change(screen.getByTestId(`viewer-supercell-${axis}`), {target:{value:"3"}});
    await userEvent.click(screen.getByTestId("viewer-supercell-apply"));
    await waitFor(() => expect(calls).toHaveLength(2));
    expect(calls[1]).toMatchObject({performanceTier:"degraded",pixelRatioCap:1,antialias:false});
    expect(calls[1].scene.atoms).toHaveLength(1_728);
    expect(screen.getByTestId("viewer-scene-renderer-performance-warning").textContent).toContain("VIEWER_RENDERER_DEGRADED_RESOURCE_MODE");
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
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("rendered"));
    expect(factory).toHaveBeenCalledOnce();
    expect((screen.getByRole("button", { name: "Reset camera" }) as HTMLButtonElement).disabled).toBe(false);
    await user.click(screen.getByTestId("viewer-scene-renderer-reset"));
    expect(engine.resetCamera).toHaveBeenCalledOnce();
    await user.click(screen.getByTestId("viewer-scene-renderer-toggle-cell"));
    expect(screen.getByTestId("viewer-scene-renderer-audit").textContent).toContain("cell edges0");
    await user.click(screen.getByTestId("viewer-scene-renderer-toggle-bonds"));
    expect(screen.getByTestId("viewer-scene-renderer-audit").textContent).toContain("bonds0");
  });

  it("provides bounded keyboard camera controls without trapping form inputs", async () => {
    const engine = fakeEngine();
    render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={async () => engine} />);
    const region = await screen.findByRole("region", {name:"3D Structure Viewer"});
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("rendered"));
    region.focus();
    fireEvent.keyDown(region, {key:"ArrowLeft"});
    fireEvent.keyDown(region, {key:"ArrowUp", shiftKey:true});
    fireEvent.keyDown(region, {key:"+"});
    expect(engine.keyboardCamera).toHaveBeenNthCalledWith(1,"rotate_left");
    expect(engine.keyboardCamera).toHaveBeenNthCalledWith(2,"pan_up");
    expect(engine.keyboardCamera).toHaveBeenNthCalledWith(3,"zoom_in");
    fireEvent.keyDown(region, {key:"r"});
    expect(engine.resetCamera).toHaveBeenCalledOnce();
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
    expect(screen.getByTestId("viewer-scene-accessibility-announcement").textContent).toContain("Selected site 0");
    expect(screen.getByTestId("viewer-selected-site-cartesian").textContent).toContain("0, 0, 0");
    await user.click(screen.getByRole("button", { name: "Copy site JSON" }));
    expect(writeText).toHaveBeenCalledOnce();
    await user.click(screen.getByRole("button", { name: "Distance" }));
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
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("rendered"));
    await userEvent.click(screen.getByTestId("viewer-scene-export-png"));
    expect(engine.exportPng).toHaveBeenCalledOnce();
    expect(createUrl).toHaveBeenCalledOnce();
    rerender(<ViewerSceneRendererSurface payload={{ ...minimalScene, metadata: { ...minimalScene.metadata, title: "changed" } }} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(engine.setSelection).toHaveBeenCalledWith([]));
    await Promise.resolve();
    expect(revokeUrl).toHaveBeenCalled();
    delete (URL as unknown as { createObjectURL?: unknown }).createObjectURL;
    delete (URL as unknown as { revokeObjectURL?: unknown }).revokeObjectURL;
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
    expect(screen.getByTestId("viewer-scene-renderer-unavailable").textContent).toContain("Scene JSON and Manifest views remain available");
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
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("rendered"));
    fireEvent(window, new Event("noop"));
    loseContext();
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-fallback").textContent).toContain("Graphics context lost"));
  });

  it("shows an accessible chunk failure fallback and retries the loader", async () => {
    const factory = vi.fn()
      .mockRejectedValueOnce(new (await import("./viewerSceneRendererErrors")).ViewerRendererError("VIEWER_RENDERER_CHUNK_LOAD_FAILED", "blocked"))
      .mockResolvedValueOnce(fakeEngine()) as ViewerRendererEngineFactory;
    const user = userEvent.setup();
    render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={factory} />);
    await waitFor(() => expect(screen.getByText("Renderer module unavailable")).toBeTruthy());
    await user.click(screen.getByRole("button", { name: "Retry renderer" }));
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("rendered"));
    expect(factory).toHaveBeenCalledTimes(2);
  });

  it("exposes a textual scene summary, species legend, live status, and metrics", async () => {
    render(<ViewerSceneRendererSurface payload={minimalScene} capabilityOverride engineFactory={async () => fakeEngine()} />);
    await waitFor(() => expect(screen.getByTestId("viewer-scene-renderer-state").textContent).toContain("rendered"));
    expect(screen.getByRole("region", { name: "3D Structure Viewer" })).toBeTruthy();
    expect(screen.getByTestId("viewer-scene-renderer-summary").textContent).toContain("1 sites");
    expect(screen.getByRole("list", { name: "Species legend" }).textContent).toContain("Si");
    expect(screen.getByTestId("viewer-scene-renderer-metrics").textContent).toContain("instancedMeshCount");
    expect(screen.getByTestId("viewer-scene-semantic-summary").textContent).toContain("Cross-boundary bonds");
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
});
