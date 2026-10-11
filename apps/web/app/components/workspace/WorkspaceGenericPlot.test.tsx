import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { sanitizePlotSpec, WorkspaceGenericPlot } from "./WorkspaceGenericPlot";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe("Phase 10M-4 generic Plotly renderer", () => {
  it("directs contradictory element counts to their original source, without offering an unavailable numeric table", () => {
    const plotlyLoader = vi.fn();
    render(<WorkspaceGenericPlot content={{ artifactType: "composition.elements_hist", chartType: "bar", countMode: "occurrence", elementCount: 4,
      bars: [{ element: "Fe", count: 12, fraction: 1 }], plotlyFigure: { data: [{ type: "bar", x: ["O"], y: [12] }] } }} maximumPoints={100} plotlyLoader={plotlyLoader} />);
    expect(screen.getByRole("alert")).toHaveTextContent("原始文件可在“数据与来源”中查看");
    expect(screen.getByRole("alert")).not.toHaveTextContent("数值数据");
    expect(plotlyLoader).not.toHaveBeenCalled();
  });

  it("reads the composition adapter envelope and preserves a requested logarithmic axis", () => {
    const payload = { artifactType: "composition.elements_hist", chartType: "bar", countMode: "occurrence", elementCount: 2,
      bars: [{ element: "Fe", count: 12, fraction: 0.8 }, { element: "Si", count: 3, fraction: 0.2 }],
      plotlyFigure: { data: [{ type: "bar", x: ["Fe", "Si"], y: [12, 3], width: 0.7 }], layout: { yaxis: { type: "log", title: { text: "log(Element Count)" }, range: [0, 2] } } } };
    expect(sanitizePlotSpec(payload, 10)).toMatchObject({ ok: true, layout: { yaxis: { type: "log", range: [0, 2] } }, data: [{ y: [12, 3], width: 0.7 }] });
  });

  it("retains the correlation adapter's absolute diverging scale and scientific colorbar title", () => {
    expect(sanitizePlotSpec({ data: [{ type: "heatmap", z: [[1, 0.95], [0.95, 1]], zmin: -1, zmax: 1, colorscale: [[0, "rgb(103,0,31)"], [0.5, "rgb(247,247,247)"], [1, "rgb(5,48,97)"]], colorbar: { title: { text: "pearson" } } }] }, 10)).toMatchObject({ ok: true, data: [{ zmin: -1, zmax: 1, colorscale: [[0, "rgb(103,0,31)"], [0.5, "rgb(247,247,247)"], [1, "rgb(5,48,97)"]], colorbar: { title: { text: "pearson" } } }] });
  });

  it("keeps bounded secondary-axis identities, domains and reversed ranges", () => {
    const result = sanitizePlotSpec({ data: [{ x: [1, 2], y: [10, 20], xaxis: "x2", yaxis: "y2" }], layout: { xaxis2: { domain: [0.6, 1], anchor: "y2", type: "log", title: "Energy (eV)" }, yaxis2: { overlaying: "y", side: "right", autorange: "reversed", title: "DOS" } } }, 10);
    expect(result).toMatchObject({ ok: true, data: [{ xaxis: "x2", yaxis: "y2" }], layout: { xaxis2: { domain: [0.6, 1], anchor: "y2", type: "log" }, yaxis2: { overlaying: "y", side: "right", autorange: "reversed" } } });
  });

  it("preserves horizontal bars and their saved grouping and baseline", () => {
    expect(sanitizePlotSpec({ data: [{ type: "bar", orientation: "h", x: [2, 3], y: ["Fe", "Si"], base: [1, 2] }], layout: { barmode: "overlay" } }, 10)).toMatchObject({ ok: true, data: [{ orientation: "h", base: [1, 2] }], layout: { barmode: "overlay" } });
  });

  it("rejects invalid axis or scale definitions instead of drawing default substitutes", () => {
    const scatter = { data: [{ x: [1, 2], y: [3, 4] }] };
    for (const xaxis of [{ type: "unknown" }, { range: [1, NaN] }, { domain: [-1, 2] }, { anchor: "javascript:alert(1)" }]) {
      expect(sanitizePlotSpec({ ...scatter, layout: { xaxis } }, 10)).toMatchObject({ ok: false });
    }
    expect(sanitizePlotSpec({ data: [{ x: [1], y: [2], xaxis: "x99" }] }, 10)).toMatchObject({ ok: false });
    expect(sanitizePlotSpec({ data: [{ type: "heatmap", z: [[1]], zmin: 2, zmax: -2 }] }, 10)).toMatchObject({ ok: false });
    expect(sanitizePlotSpec({ data: [{ type: "heatmap", z: [[1]], colorscale: [[0, "url(https://example.invalid)"], [1, "red"]] }] }, 10)).toMatchObject({ ok: false });
  });

  it("keeps a shared heatmap color axis and secondary 3D scene without mutating saved settings", () => {
    const content = { data: [
      { type: "heatmap", z: [[-0.2, 0.8]], coloraxis: "coloraxis2" },
      { type: "scatter3d", x: [1], y: [2], z: [3], scene: "scene2" },
    ], layout: { coloraxis2: { cmin: -1, cmax: 1, colorscale: "RdBu", colorbar: { title: "Pearson r" } }, scene2: { domain: { x: [0.6, 1], y: [0, 1] }, zaxis: { range: [5, -1], title: "z (Å)" } } } };
    const before = JSON.stringify(content);
    expect(sanitizePlotSpec(content, 10)).toMatchObject({ ok: true, data: [{ coloraxis: "coloraxis2" }, { scene: "scene2" }], layout: { coloraxis2: { cmin: -1, cmax: 1, colorscale: "RdBu" }, scene2: { domain: { x: [0.6, 1], y: [0, 1] }, zaxis: { range: [5, -1] } } } });
    expect(JSON.stringify(content)).toBe(before);
  });

  it("preserves exact category order and tick identities while excluding external layout content", () => {
    const result = sanitizePlotSpec({ data: [{ type: "bar", x: ["Cu", "Fe"], y: [2, 5] }], layout: { xaxis: { type: "category", categoryorder: "array", categoryarray: ["Fe", "Cu"], tickmode: "array", tickvals: ["Fe", "Cu"], ticktext: ["Iron", "Copper"] }, images: [{ source: "https://example.invalid/image.png" }], annotations: [{ text: "<script>bad</script>" }] } }, 10);
    expect(result).toMatchObject({ ok: true, layout: { xaxis: { categoryarray: ["Fe", "Cu"], tickvals: ["Fe", "Cu"], ticktext: ["Iron", "Copper"] } } });
    if (result.ok) { expect(result.layout).not.toHaveProperty("images"); expect(result.layout).not.toHaveProperty("annotations"); }
  });
  it("renders encoded heatmap matrices from the backend exporter with their exact shape and gaps", () => {
    expect(sanitizePlotSpec({ data: [{ type: "heatmap", x: { dtype: "i1", bdata: "ChQe" }, y: { dtype: "i1", bdata: "AQI=" }, z: { dtype: "f8", bdata: "AAAAAAAAJkAAAAAAAAAoQAAAAAAAACpAAAAAAAAANUAAAAAAAAD4fwAAAAAAADdA", shape: "2, 3" } }] }, 10)).toMatchObject({ ok: true, data: [{ x: [10, 20, 30], y: [1, 2], z: [[11, 12, 13], [21, null, 23]] }] });
  });

  it("rejects encoded matrices supplied as vectors instead of silently flattening them", () => {
    expect(sanitizePlotSpec({ data: [{ type: "scatter", x: { dtype: "i1", bdata: "AQIDBA==", shape: "2, 2" }, y: [1, 2, 3, 4] }] }, 10)).toMatchObject({ ok: false, code: "PLOTLY_TRACE_INVALID" });
  });
  it("renders only bounded backend data through a stripped application layout", () => {
    const result = sanitizePlotSpec({
      figure: {
        data: [{ type: "scatter", x: [1, 2], y: [3, 4], name: "<img src=x>", hovertemplate: "javascript:alert(1)" }],
        layout: { title: { text: "<script>bad</script> Valid" }, images: [{ source: "https://example.invalid/image.png" }], annotations: [{ text: "<iframe>" }] },
      },
    }, 10);
    expect(result).toMatchObject({ ok: true, pointCount: 2 });
    if (!result.ok) return;
    expect(result.layout).not.toHaveProperty("images");
    expect(result.layout).not.toHaveProperty("annotations");
    expect(result.data[0]).not.toHaveProperty("hovertemplate");
    expect((result.data[0] as Record<string, unknown>).name).toBe(" img src=x ");
  });

  it("refuses browser histogram binning, non-finite values, and point caps", () => {
    expect(sanitizePlotSpec({ figure: { data: [{ type: "histogram", x: [1, 2] }] } }, 10)).toMatchObject({ ok: false, code: "PLOTLY_TRACE_TYPE_UNSUPPORTED" });
    expect(sanitizePlotSpec({ figure: { data: [{ type: "scatter", x: [1], y: [Number.NaN] }] } }, 10)).toMatchObject({ ok: false, code: "PLOTLY_TRACE_INVALID" });
    expect(sanitizePlotSpec({ figure: { data: [{ type: "heatmap", z: [[1, 2], [3, 4]] }] } }, 2)).toMatchObject({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
  });

  it("rejects oversized heatmap cells and mesh triangles without truncating authority", () => {
    const heatmap = Array.from({ length: 317 }, () => Array.from({ length: 317 }, () => 1));
    expect(sanitizePlotSpec({ figure: { data: [{ type: "heatmap", z: heatmap }] } }, 200_000)).toMatchObject({
      ok: false,
      code: "PLOTLY_HEATMAP_CELL_CAP_EXCEEDED",
    });
    const triangles = 100_001;
    const indices = Array.from({ length: triangles }, (_, index) => index % 3);
    expect(sanitizePlotSpec({
      figure: { data: [{ type: "mesh3d", x: [0, 1, 0], y: [0, 0, 1], z: [0, 0, 0], i: indices, j: indices, k: indices }] },
    }, 10)).toMatchObject({ ok: false, code: "PLOTLY_MESH_CAP_EXCEEDED" });
  });

  it("uses deterministic extrema-preserving sampling when line data exceeds the display cap", () => {
    const result = sanitizePlotSpec({ figure: { data: [{ type: "scatter", x: [0, 1, 2, 3, 4, 5], y: [0, -9, 2, 3, 8, 1] }] } }, 4);
    expect(result).toMatchObject({ ok: true, pointCount: 4, totalPointCount: 6, decimated: true, samplingStrategy: "保留端点、优先极值" });
    if (!result.ok) return;
    expect(result.data[0]).toMatchObject({ x: [0, 1, 4, 5], y: [0, -9, 8, 1] });
  });

  it("keeps global extrema even when they occur outside the first local bucket", () => {
    const result = sanitizePlotSpec({ figure: { data: [{ type: "scatter", x: [0, 1, 2, 3, 4, 5, 6, 7], y: [0, 1, 2, 3, 100, 5, -100, 7] }] } }, 4);
    expect(result).toMatchObject({ ok: true, pointCount: 4, totalPointCount: 8, decimated: true });
    if (!result.ok) return;
    expect(result.data[0]).toMatchObject({ x: [0, 4, 6, 7], y: [0, 100, -100, 7] });
  });

  it("discloses the total source point count when the bounded preview samples", async () => {
    render(
      <WorkspaceGenericPlot
        content={{ figure: { data: [{ type: "scatter", x: [0, 1, 2, 3, 4, 5], y: [0, -9, 2, 3, 8, 1] }] } }}
        maximumPoints={4}
        plotlyLoader={async () => ({ newPlot: async () => undefined, purge: () => undefined })}
      />,
    );
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("已渲染 1 个数据系列和 4/6 条抽样记录"));
    expect(screen.getByRole("status")).toHaveTextContent("策略：保留端点、优先极值");
    expect(screen.getByRole("status")).not.toHaveClass("sr-only");
  });

  it("projects the persisted static-chart contract into bounded Plotly traces", () => {
    const result = sanitizePlotSpec({
      artifactType: "structure.rdf_plot",
      schema_version: "phase10e7.static_chart.v1",
      chart_type: "line",
      title: "Radial distribution function",
      x_axis: { label: "r (angstrom)", values: [0.1, 0.2] },
      y_axis: { label: "g(r)" },
      series: [
        { name: "Fe-O", x: [0.1, 0.2], y: [0, 2.4], hovertemplate: "javascript:alert(1)" },
        { name: "O-O", y: [0, 1.2] },
      ],
      security: { contains_javascript: false, external_urls: [] },
    }, 10);

    expect(result).toMatchObject({ ok: true, pointCount: 4, decimated: false });
    if (!result.ok) return;
    expect(result.data).toHaveLength(2);
    expect(result.data[0]).toMatchObject({ type: "scatter", mode: "lines", name: "Fe-O" });
    expect(result.data[0]).not.toHaveProperty("hovertemplate");
    expect(result.layout).toMatchObject({
      title: { text: "Radial distribution function" },
      xaxis: { title: { text: "r (angstrom)" } },
      yaxis: { title: { text: "g(r)" } },
    });
  });

  it("preserves scientific direction in series names while still removing HTML delimiters", () => {
    const content = { data: [
      { name: "Cl->Na", x: [0.1], y: [2.4] },
      { name: "Cl<-Na", x: [0.1], y: [1.2] },
      { name: "Cl<->Na", x: [0.1], y: [0.8] },
      { name: "<img src=x>Cl->Na", x: [0.1], y: [0] },
    ] };
    const before = JSON.stringify(content);
    const result = sanitizePlotSpec(content, 10);
    expect(result).toMatchObject({ ok: true, data: [
      { name: "Cl→Na" }, { name: "Cl←Na" }, { name: "Cl↔Na" }, { name: " img src=x Cl→Na" },
    ] });
    expect(JSON.stringify(content)).toBe(before);
  });

  it("lets the keyboard independently toggle directed pairs without changing saved points or axes", async () => {
    const user = userEvent.setup();
    const content = { data: [
      { type: "scatter", mode: "lines", name: "Cl->Na", x: [0.1, 0.2], y: [0, 2.4] },
      { type: "scatter", mode: "lines", name: "Na->Cl", x: [0.1, 0.2], y: [0, 1.2] },
    ], layout: { xaxis: { range: [0, 8], title: "r (angstrom)" }, yaxis: { title: "g(r)" } } };
    const before = JSON.stringify(content);
    const newPlot = vi.fn(async (_target: HTMLElement, _data: unknown[], _layout: Record<string, unknown>) => undefined);
    render(<WorkspaceGenericPlot content={content} maximumPoints={10} plotlyLoader={async () => ({ newPlot, purge: () => undefined })} />);
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("已渲染 2 个数据系列和 4 个数值"));
    expect(screen.getByRole("group", { name: "图表数据系列" })).toBeVisible();
    const forward = screen.getByRole("button", { name: "Cl→Na" });
    const reverse = screen.getByRole("button", { name: "Na→Cl" });
    forward.focus();
    await user.keyboard("{Enter}");
    await waitFor(() => expect(forward).toBeEnabled());
    expect(forward).toHaveFocus();
    expect(forward).toHaveAttribute("aria-pressed", "false");
    expect(reverse).toHaveAttribute("aria-pressed", "true");
    expect(reverse).toBeDisabled();
    const [, data, layout] = newPlot.mock.calls.at(-1)!;
    expect(data).toMatchObject([
      { name: "Cl→Na", x: [0.1, 0.2], y: [0, 2.4], visible: "legendonly" },
      { name: "Na→Cl", x: [0.1, 0.2], y: [0, 1.2], visible: true },
    ]);
    expect(layout).toMatchObject({ showlegend: false, xaxis: { range: [0, 8], title: { text: "r (angstrom)" } }, yaxis: { title: { text: "g(r)" } } });
    await user.keyboard(" ");
    await waitFor(() => expect(reverse).toBeEnabled());
    expect(forward).toHaveAttribute("aria-pressed", "true");
    expect(JSON.stringify(content)).toBe(before);
  });

  it("resets curve visibility when a different saved plot replaces the current source", async () => {
    const newPlot = vi.fn(async (_target: HTMLElement, _data: unknown[]) => undefined);
    const plotlyLoader = async () => ({ newPlot, purge: () => undefined });
    const data = [{ name: "A", x: [1], y: [2] }, { name: "B", x: [1], y: [3] }];
    const view = render(<WorkspaceGenericPlot content={{ data }} maximumPoints={10} plotlyLoader={plotlyLoader} />);
    await waitFor(() => expect(screen.getByRole("button", { name: "A" })).toBeEnabled());
    fireEvent.click(screen.getByRole("button", { name: "A" }));
    await waitFor(() => expect(newPlot.mock.calls.at(-1)![1][0]).toMatchObject({ visible: "legendonly" }));
    view.rerender(<WorkspaceGenericPlot content={{ data: data.map(trace => ({ ...trace, y: [9] })) }} maximumPoints={10} plotlyLoader={plotlyLoader} />);
    await waitFor(() => expect(screen.getByRole("button", { name: "B" })).toBeEnabled());
    expect(newPlot.mock.calls.at(-1)![1]).toMatchObject([{ y: [9], visible: true }, { y: [9], visible: true }]);
    expect(screen.getByRole("button", { name: "A" })).toHaveAttribute("aria-pressed", "true");
  });

  it.each([
    { kind: "single series", data: [{ type: "scatter", x: [1], y: [2] }] },
    { kind: "heatmap", data: [{ type: "heatmap", z: [[0, 1]] }, { type: "scatter", x: [1], y: [2] }] },
    { kind: "3D", data: [{ type: "scatter3d", x: [1], y: [2], z: [3] }, { type: "scatter3d", x: [2], y: [3], z: [4] }] },
  ])("does not assign a curve legend to $kind plots", async ({ data }) => {
    render(<WorkspaceGenericPlot content={{ data }} maximumPoints={10} plotlyLoader={async () => ({ newPlot: async () => undefined, purge: () => undefined })} />);
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("已渲染"));
    expect(screen.queryByRole("group", { name: "图表数据系列" })).not.toBeInTheDocument();
  });

  it("accepts bounded three-dimensional structure traces and strips executable options", () => {
    const result = sanitizePlotSpec({
      data: [
        { type: "scatter3d", mode: "markers", x: [0], y: [1], z: [2], marker: { color: "rgb(224,102,51)", size: 80 }, hovertemplate: "javascript:alert(1)" },
        {
          type: "mesh3d",
          x: { dtype: "f8", bdata: "AAAAAAAAAAAAAAAAAADwPwAAAAAAAAAA" },
          y: { dtype: "f8", bdata: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAPA/" },
          z: { dtype: "f8", bdata: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" },
          i: 0,
          j: 1,
          k: 2,
          color: "rgba(255,255,255,0.1)",
          opacity: 0.2,
        },
      ],
      layout: { scene: { xaxis: { title: "x / Å" }, yaxis: { title: "y / Å" }, zaxis: { title: "z / Å" } }, annotations: [{ text: "unsafe" }] },
    }, 10);

    expect(result).toMatchObject({ ok: true, pointCount: 4 });
    if (!result.ok) return;
    expect(result.data[0]).toMatchObject({ type: "scatter3d", marker: { size: 18 } });
    expect(result.data[0]).not.toHaveProperty("hovertemplate");
    expect(result.data[1]).toMatchObject({ type: "mesh3d", i: [0], j: [1], k: [2], showscale: false });
    expect(result.layout).not.toHaveProperty("annotations");
    expect(result.layout).toMatchObject({ showlegend: false });
  });

  it("keeps a hard cap on the number of three-dimensional traces", () => {
    const traces = Array.from({ length: 129 }, () => ({ type: "scatter3d", x: [0], y: [0], z: [0] }));
    expect(sanitizePlotSpec({ data: traces }, 1_000)).toMatchObject({ ok: false, code: "PLOTLY_TRACE_CAP_EXCEEDED" });
  });

  it("distinguishes module loading from Plotly rendering failures", async () => {
    const content = { figure: { data: [{ type: "scatter", x: [1], y: [2] }] } };
    const first = render(
      <WorkspaceGenericPlot
        content={content}
        maximumPoints={10}
        plotlyLoader={async () => { throw new Error("module unavailable"); }}
      />,
    );
    await waitFor(() => expect(screen.getByRole("alert")).toHaveAttribute("data-failure-code", "GENERIC_PLOT_MODULE_LOAD_FAILED"));
    expect(screen.getByRole("alert")).toBeVisible();
    expect(screen.getByTestId("workspace-generic-plot-canvas")).not.toBeVisible();
    expect(screen.getByRole("button", { name: "重新绘制图表" })).toBeVisible();
    expect(screen.queryByText(/module unavailable/)).not.toBeInTheDocument();
    first.unmount();

    render(
      <WorkspaceGenericPlot
        content={content}
        maximumPoints={10}
        plotlyLoader={async () => ({
          newPlot: async () => { throw new Error("render unavailable"); },
          purge: () => undefined,
        })}
      />,
    );
    await waitFor(() => expect(screen.getByRole("alert")).toHaveAttribute("data-failure-code", "GENERIC_PLOT_RENDER_FAILED"));
    expect(screen.getByRole("alert")).toBeVisible();
  });

  it("passes mutable copies of the validated spec to Plotly", async () => {
    render(
      <WorkspaceGenericPlot
        content={{ figure: { data: [{ type: "scatter", x: [1], y: [2] }] } }}
        maximumPoints={10}
        plotlyLoader={async () => ({
          newPlot: async (_target, data, layout) => {
            layout.paper_bgcolor = "#000000";
            const trace = data[0] as Record<string, unknown>;
            (trace.marker as Record<string, unknown>).color = "#ffffff";
          },
          purge: () => undefined,
        })}
      />,
    );
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("已渲染 1 个数据系列"));
  });

  it("resizes Plotly when its container changes size and disconnects on unmount", async () => {
    let resizeCallback: ResizeObserverCallback | null = null;
    const observe = vi.fn();
    const disconnect = vi.fn();
    class MockResizeObserver {
      constructor(callback: ResizeObserverCallback) {
        resizeCallback = callback;
      }
      observe = observe;
      disconnect = disconnect;
    }
    vi.stubGlobal("ResizeObserver", MockResizeObserver);

    const resize = vi.fn();
    const view = render(
      <WorkspaceGenericPlot
        content={{ figure: { data: [{ type: "scatter", x: [1], y: [2] }] } }}
        maximumPoints={10}
        plotlyLoader={async () => ({
          newPlot: async () => undefined,
          purge: () => undefined,
          Plots: { resize },
        })}
      />,
    );

    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("已渲染 1 个数据系列"));
    expect(observe).toHaveBeenCalledWith(screen.getByTestId("workspace-generic-plot-canvas"));
    expect(resizeCallback).toBeTypeOf("function");
    (resizeCallback as unknown as ResizeObserverCallback)([], {} as ResizeObserver);
    expect(resize).toHaveBeenCalledTimes(1);

    view.unmount();
    expect(disconnect).toHaveBeenCalledTimes(1);
  });

  it("purges a Plotly surface when unmounted during asynchronous plot creation", async () => {
    let resolvePlot: ((value?: void | PromiseLike<void>) => void) | undefined;
    const newPlot = vi.fn(() => new Promise<void>((resolve) => { resolvePlot = resolve; }));
    const purge = vi.fn();
    const view = render(
      <WorkspaceGenericPlot
        content={{ figure: { data: [{ type: "scatter", x: [1], y: [2] }] } }}
        maximumPoints={10}
        plotlyLoader={async () => ({ newPlot, purge })}
      />,
    );
    await waitFor(() => expect(newPlot).toHaveBeenCalledOnce());
    view.unmount();
    const finish = resolvePlot;
    if (finish) finish();
    await waitFor(() => expect(purge).toHaveBeenCalledWith(expect.any(HTMLElement)));
    expect(purge).toHaveBeenCalledTimes(2);
  });

  it("preserves explicit gaps in saved line coordinates without connecting across them", () => {
    const content = { data: [{ type: "scatter", mode: "lines", x: [0, 1, 2, 3, 4], y: [1, 2, null, 4, 5], connectgaps: true }] };
    const before = JSON.stringify(content);
    const result = sanitizePlotSpec(content, 10);
    expect(result).toMatchObject({ ok: true, pointCount: 5 });
    if (!result.ok) return;
    expect(result.data[0]).toMatchObject({ x: [0, 1, 2, 3, 4], y: [1, 2, null, 4, 5], connectgaps: false });
    expect(JSON.stringify(content)).toBe(before);
  });

  it("keeps gaps and both neighboring segment endpoints during bounded sampling", () => {
    const result = sanitizePlotSpec({ data: [{ type: "scatter", mode: "lines", x: [0, 1, 2, 3, 4, 5, 6, 7, 8], y: [0, 1, 2, null, null, null, 6, 7, 8] }] }, 5);
    expect(result).toMatchObject({ ok: true, pointCount: 5, totalPointCount: 9, decimated: true });
    if (!result.ok) return;
    expect(result.data[0]).toMatchObject({ x: [0, 2, 3, 6, 8], y: [0, 2, null, 6, 8], connectgaps: false });
  });

  it("allocates enough shared budget to retain a discontinuous series beside a short series", () => {
    const result = sanitizePlotSpec({ data: [
      { type: "scatter", x: [0, 1, 2, 3, 4, 5, 6], y: [0, 1, null, null, 4, 5, 6] },
      { type: "scatter", x: [0, 1], y: [1, 2] },
    ] }, 7);
    expect(result).toMatchObject({ ok: true, pointCount: 7 });
    if (!result.ok) return;
    expect(result.data[0]).toMatchObject({ x: [0, 1, 2, 4, 6], y: [0, 1, null, 4, 6] });
    expect(result.data[1]).toMatchObject({ x: [0, 1], y: [1, 2] });
  });

  it("refuses sampling that would erase a real discontinuity", () => {
    expect(sanitizePlotSpec({ data: [{ type: "scatter", mode: "lines", x: [0, 1, 2, 3, 4], y: [1, 2, null, 3, 4] }] }, 4)).toMatchObject({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
  });

  it("keeps static-chart gaps and scatter3d line breaks while rejecting missing mesh vertices", () => {
    expect(sanitizePlotSpec({ chart_type: "line", series: [{ x: [0, 1, 2], y: [2, null, 4] }] }, 10)).toMatchObject({ ok: true, data: [{ y: [2, null, 4] }] });
    expect(sanitizePlotSpec({ data: [{ type: "scatter3d", mode: "lines", x: [0, 1, 2], y: [1, null, 3], z: [2, 3, 4] }] }, 10)).toMatchObject({ ok: true, data: [{ y: [1, null, 3], connectgaps: false }] });
    expect(sanitizePlotSpec({ data: [{ type: "mesh3d", x: [0, null, 1], y: [0, 1, 0], z: [0, 0, 0], i: [0], j: [1], k: [2] }] }, 10)).toMatchObject({ ok: false, code: "PLOTLY_TRACE_INVALID" });
  });

  it("retains heatmap transpose and explicit missing cells with exact axis coordinates", () => {
    const content = { data: [{ type: "heatmap", transpose: true, x: [10, 20], y: [1, 2, 3], z: [[11, null, 13], [21, 22, 23]] }] };
    const before = JSON.stringify(content);
    expect(sanitizePlotSpec(content, 10)).toMatchObject({ ok: true, data: [{ transpose: true, x: [10, 20], y: [1, 2, 3], z: [[11, null, 13], [21, 22, 23]], connectgaps: false }] });
    expect(JSON.stringify(content)).toBe(before);
  });

  it("rejects malformed supplied heatmap coordinates instead of substituting implicit positions", () => {
    for (const x of [[1, Number.NaN], [1, null], [1, 2, 3, 4], { bad: true }]) {
      expect(sanitizePlotSpec({ data: [{ type: "heatmap", x, z: [[1, 2]] }] }, 10)).toMatchObject({ ok: false, code: "PLOTLY_TRACE_INVALID" });
    }
    expect(sanitizePlotSpec({ data: [{ type: "heatmap", x: [0, 2, 5], z: [[1, 2]] }] }, 10)).toMatchObject({ ok: true, data: [{ x: [0, 2, 5] }] });
  });

  it("gives an explicit no-data result when all saved coordinates are gaps", () => {
    expect(sanitizePlotSpec({ data: [{ type: "scatter", x: [0, 1], y: [null, null] }] }, 10)).toMatchObject({ ok: false, code: "PLOTLY_NO_FINITE_POINTS" });
    expect(sanitizePlotSpec({ data: [{ type: "heatmap", z: [[null]] }] }, 10)).toMatchObject({ ok: false, code: "PLOTLY_NO_FINITE_POINTS" });
  });

  it("never joins emitted finite points across a saved gap across varied sampling budgets", () => {
    for (let stride = 3; stride <= 15; stride += 3) {
      const x = Array.from({ length: 64 }, (_, i) => i);
      const y = x.map(i => i % stride === 1 || i % stride === 2 ? null : Math.sin(i));
      for (const budget of [16, 32, 48, 64]) {
        const result = sanitizePlotSpec({ data: [{ type: "scatter", mode: "lines", x, y }] }, budget);
        if (!result.ok) { expect(result.code).toBe("PLOTLY_POINT_CAP_EXCEEDED"); continue; }
        expect(result.pointCount).toBeLessThanOrEqual(budget);
        const trace = result.data[0] as { x: number[]; y: Array<number | null> };
        trace.x.forEach((originalIndex, index) => {
          expect(trace.y[index]).toBe(y[originalIndex]);
          if (index > 0 && trace.y[index] !== null && trace.y[index - 1] !== null) {
            expect(y.slice(trace.x[index - 1], originalIndex + 1)).not.toContain(null);
          }
        });
      }
    }
  });

  it("preserves saved histogram widths and counts without sampling away bins", () => {
    const content = { data: [{ type: "bar", x: [-1, 1], y: [2, 3], width: [2, 2] }] };
    const original = JSON.stringify(content);
    const result = sanitizePlotSpec(content, 2);
    expect(result).toMatchObject({ ok: true, pointCount: 2, decimated: false, data: content.data });
    expect(sanitizePlotSpec(content, 1)).toMatchObject({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
    expect(JSON.stringify(content)).toBe(original);
    expect(sanitizePlotSpec({ data: [{ ...content.data[0], width: [2] }] }, 2)).toMatchObject({ ok: false });
    expect(sanitizePlotSpec({ data: [{ ...content.data[0], width: [0, 2] }] }, 2)).toMatchObject({ ok: false });
    for (const width of [0, -1, Infinity, NaN]) expect(sanitizePlotSpec({ data: [{ ...content.data[0], width }] }, 2)).toMatchObject({ ok: false });
  });

  it("recovers a failed module load in place without exposing provider errors", async () => {
    const newPlot = vi.fn(async () => undefined);
    const loader = vi.fn().mockRejectedValueOnce(new Error("private module url and stack"))
      .mockResolvedValue({ newPlot, purge: vi.fn() });
    render(<WorkspaceGenericPlot content={{ data: [{ x: [1], y: [2] }] }} maximumPoints={10} plotlyLoader={loader} />);
    await screen.findByRole("alert");
    fireEvent.click(screen.getByRole("button", { name: "重新绘制图表" }));
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("已渲染 1 个数据系列"));
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(loader).toHaveBeenCalledTimes(2);
    expect(newPlot).toHaveBeenCalledOnce();
  });

  it("times out a stalled module and ignores it after a successful retry", async () => {
    vi.useFakeTimers();
    let finish!: (api: unknown) => void;
    const stalePlot = vi.fn(async () => undefined);
    const freshPlot = vi.fn(async () => undefined);
    const loader = vi.fn().mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }))
      .mockResolvedValue({ newPlot: freshPlot, purge: vi.fn() });
    await act(async () => { render(<WorkspaceGenericPlot content={{ data: [{ x: [1], y: [2] }] }} maximumPoints={10} plotlyLoader={loader} />); });
    await act(async () => { vi.advanceTimersByTime(10_000); });
    expect(screen.getByRole("heading", { name: "图表绘制超时" })).toBeVisible();
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新绘制图表" })); });
    expect(screen.getByRole("status")).toHaveTextContent("已渲染 1 个数据系列");
    await act(async () => finish({ newPlot: stalePlot, purge: vi.fn() }));
    expect(stalePlot).not.toHaveBeenCalled();
    expect(freshPlot).toHaveBeenCalledOnce();
  });

  it("detaches a stalled renderer so its late mutations cannot overwrite the retried plot", async () => {
    vi.useFakeTimers();
    let finish!: () => void;
    let staleHost!: HTMLElement;
    const purge = vi.fn();
    const newPlot = vi.fn().mockImplementationOnce((host: HTMLElement) => {
      staleHost = host;
      return new Promise<void>(resolve => { finish = () => { host.textContent = "late stale plot"; resolve(); }; });
    }).mockImplementation(async (host: HTMLElement) => { host.textContent = "current plot"; });
    const loader = async () => ({ newPlot, purge });
    await act(async () => { render(<WorkspaceGenericPlot content={{ data: [{ x: [1], y: [2] }] }} maximumPoints={10} plotlyLoader={loader} />); });
    await act(async () => { vi.advanceTimersByTime(10_000); });
    expect(staleHost.isConnected).toBe(false);
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新绘制图表" })); });
    expect(screen.getByTestId("workspace-generic-plot-canvas")).toHaveTextContent("current plot");
    await act(async () => finish());
    expect(screen.getByTestId("workspace-generic-plot-canvas")).not.toHaveTextContent("stale");
    expect(purge).toHaveBeenLastCalledWith(staleHost);
  });

  it("keeps contract rejection visible without offering an identical retry", () => {
    render(<WorkspaceGenericPlot content={{ data: [{ type: "histogram", x: [1, 2] }] }} maximumPoints={10} />);
    expect(screen.getByRole("alert")).toBeVisible();
    expect(screen.queryByRole("button", { name: "重新绘制图表" })).not.toBeInTheDocument();
  });
});
