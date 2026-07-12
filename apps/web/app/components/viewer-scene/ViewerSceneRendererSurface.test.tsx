import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import minimalScene from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_minimal_crystal.viewer_scene.v1.json";
import multiSpeciesScene from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_multi_species_crystal.viewer_scene.v1.json";
import { ViewerSceneRendererSurface } from "./ViewerSceneRendererSurface";
import type { ViewerRendererEngine, ViewerRendererEngineFactory, ViewerRendererSnapshot } from "./viewerSceneRendererTypes";

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
    selectedSiteIndices: [],
    siteScreenPositions: [],
    metrics: {
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
      initializationMs: 10,
      firstFrameMs: 12,
    },
  });
  const engine: ViewerRendererEngine = {
    resetCamera: vi.fn(),
    setCellVisible(value) { cellVisible = value; },
    setBondsVisible(value) { bondsVisible = value; },
    setSelection: vi.fn(),
    exportPng: vi.fn(async () => new Blob(["png"], { type: "image/png" })),
    render: vi.fn(),
    snapshot,
    dispose,
  };
  return engine;
}

describe("ViewerSceneRendererSurface", () => {
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
    act(() => onSitePick?.(0));
    expect(screen.getByTestId("viewer-selected-site-index").textContent).toContain("0");
    expect(screen.getByTestId("viewer-selected-site-cartesian").textContent).toContain("0, 0, 0");
    await user.click(screen.getByRole("button", { name: "Copy site JSON" }));
    expect(writeText).toHaveBeenCalledOnce();
    await user.click(screen.getByRole("button", { name: "Distance" }));
    act(() => { onSitePick?.(0); onSitePick?.(1); });
    await waitFor(() => expect(screen.getByTestId("viewer-measurement-result").textContent).toContain("distance"));
    expect(engine.setSelection).toHaveBeenLastCalledWith([0, 1]);
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
