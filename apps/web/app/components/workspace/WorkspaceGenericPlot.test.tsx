import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { sanitizePlotSpec, WorkspaceGenericPlot } from "./WorkspaceGenericPlot";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("Phase 10M-4 generic Plotly renderer", () => {
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
    expect(result).toMatchObject({ ok: true, pointCount: 4, totalPointCount: 6, decimated: true, samplingStrategy: "固定端点 + 全局最小/最大值 + 分桶局部极值" });
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
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("已渲染 1 个数据系列和 4/6 个保真抽样数值"));
    expect(screen.getByRole("status")).toHaveTextContent("策略：固定端点 + 全局最小/最大值 + 分桶局部极值");
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
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("GENERIC_PLOT_MODULE_LOAD_FAILED"));
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
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("GENERIC_PLOT_RENDER_FAILED"));
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
    expect(purge).toHaveBeenCalledTimes(1);
  });
});
