"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { normalizedPlotFigure } from "./workspace-plot-contract";
import { readPlotCoordinates, readPlotNumericMatrix, readPlotNumericVector, type PlotCoordinate } from "./workspace-plot-data";
import { readPlotColorScale, readPlotLayout } from "./workspace-plot-layout";
import { readPlotHierarchy } from "./workspace-plot-hierarchy";
import { isSavedPeriodicTable, readSavedPeriodicTable, periodicLayoutForWidth } from "./saved-periodic-table";
import { isSavedElementComparison, readSavedElementComparison, readSavedElementReference } from "./saved-element-reference";
import { PlatformReferenceSources } from "../../shared/ui/PlatformReferenceSources";
import { isSavedDensityPlot, readSavedDensityPlot } from "./saved-density-plot";
import { histogramNotes, isSavedHistogram, readSavedHistogram } from "./saved-histogram";
import { isSavedScatter, readSavedScatter } from "./saved-scatter";
import { isSavedElementHistogram, readSavedElementHistogram } from "./saved-element-histogram";
import styles from "./WorkspaceGenericPlot.module.css";

type JsonRecord = Record<string, unknown>;
type PlotlyApi = Readonly<{
  newPlot: (target: HTMLElement, data: unknown[], layout: JsonRecord, config: JsonRecord) => Promise<unknown>;
  purge: (target: HTMLElement) => void;
  relayout?: (target: HTMLElement, layout: JsonRecord) => Promise<unknown>;
  register?: (modules: unknown[]) => void;
  Plots?: Readonly<{ resize: (target: HTMLElement) => void }>;
}>;

type PlotlyLoader = () => Promise<PlotlyApi>;
type PlotSpec = Readonly<{ ok: true; data: unknown[]; layout: JsonRecord; pointCount: number; totalPointCount: number; decimated: boolean; samplingStrategy: string; notes?: string[] }> | Readonly<{ ok: false; code: string }>;

const ALLOWED_TRACE_TYPES = new Set(["scatter", "scattergl", "scatter3d", "mesh3d", "bar", "heatmap", "treemap", "sunburst"]);
const MAX_TRACE_COUNT = 128;
const MAX_HEATMAP_CELLS = 100_000;
const MAX_MESH_VERTICES = 100_000;
const MAX_MESH_TRIANGLES = 100_000;
const PALETTE = ["#176b87", "#b84c3b", "#558b2f", "#7a5ca8", "#a26a00", "#2f6f6d"];

export function WorkspaceGenericPlot({ content, maximumPoints, plotlyLoader = loadPlotly }: Readonly<{ content: unknown; maximumPoints: number; plotlyLoader?: PlotlyLoader }>) {
  const hostRef = useRef<HTMLDivElement>(null);
  const savedSpec = useMemo(() => sanitizePlotSpec(content, maximumPoints), [content, maximumPoints]);
  const reference = useMemo(() => readSavedElementReference(content), [content]);
  const histogram = useMemo(() => isSavedHistogram(content) ? readSavedHistogram(content) : null, [content]);
  const scatter = useMemo(() => isSavedScatter(content) ? readSavedScatter(content) : null, [content]);
  const legendGroups = useMemo(() => {
    if (!savedSpec.ok) return null;
    if (histogram) return histogram.groups;
    if (scatter?.colorMode === "categorical") return scatter.groups;
    if (savedSpec.data.length < 2 || savedSpec.data.length > 16) return null;
    const traces = savedSpec.data.map(record);
    return traces.every(trace => trace && ["scatter", "scattergl", "bar"].includes(String(trace.type)))
      ? traces.map(trace => ({ label: String(trace!.name) })) : null;
  }, [savedSpec, histogram, scatter]);
  const [visibility, setVisibility] = useState<{ content: unknown; hidden: number[] }>({ content, hidden: [] });
  const hidden = visibility.content === content ? visibility.hidden : [];
  const spec = useMemo(() => !legendGroups || !savedSpec.ok ? savedSpec : {
    ...savedSpec,
    data: savedSpec.data.map((trace, index) => ({ ...record(trace), visible: visibility.content === content && visibility.hidden.includes(index) ? "legendonly" : true })),
    layout: { ...savedSpec.layout, showlegend: false },
  }, [savedSpec, legendGroups, visibility, content]);
  const [attempt, setAttempt] = useState(0);
  const [result, setResult] = useState<{ spec: PlotSpec; attempt: number; phase: "ready" | "failed" | "timeout"; code?: string } | null>(null);
  const phase = result?.spec === spec && result.attempt === attempt ? result.phase : "loading";

  useEffect(() => {
    const container = hostRef.current;
    if (!container || !spec.ok) return;
    // A timed-out Plotly promise may still mutate its target. Each attempt owns
    // a separate node, detached before any retry or source change can render.
    const host = document.createElement("div");
    container.replaceChildren(host);
    let active = true;
    let api: PlotlyApi | null = null;
    let purged = false;
    let ready = false;
    let detailedNumbers = container.clientWidth >= 650;
    const purge = () => {
      if (purged || !api) return;
      purged = true;
      try { api.purge(host); } catch { /* Failed renderers still release their DOM. */ }
    };
    const fail = (nextPhase: "failed" | "timeout", code: string) => {
      if (!active) return;
      active = false;
      clearTimeout(timer);
      host.remove();
      purge();
      setResult({ spec, attempt, phase: nextPhase, code });
    };
    const timer = setTimeout(() => fail("timeout", "GENERIC_PLOT_TIMEOUT"), 10_000);
    void Promise.resolve().then(plotlyLoader).then(async (loaded) => {
      if (!active) return;
      api = loaded;
      try {
        await api.newPlot(host, mutableRendererCopy(spec.data), mutableRendererCopy(periodicLayoutForWidth(spec.layout, container.clientWidth)), {
          responsive: true,
          displaylogo: false,
          displayModeBar: false,
          scrollZoom: false,
          staticPlot: false,
        });
      } finally {
        if (!active) {
          // Rendering may allocate again after the first purge at cancellation.
          purged = false;
          purge();
        }
      }
      if (!active) return;
      clearTimeout(timer);
      ready = true;
      setResult({ spec, attempt, phase: "ready" });
    }).catch(() => {
      fail("failed", api ? "GENERIC_PLOT_RENDER_FAILED" : "GENERIC_PLOT_MODULE_LOAD_FAILED");
    });
    const resize = () => {
      if (!active || !ready) return;
      try {
        if (reference && isSavedPeriodicTable(content) && detailedNumbers !== (container.clientWidth >= 650)) {
          detailedNumbers = container.clientWidth >= 650;
          void api?.relayout?.(host, { annotations: periodicLayoutForWidth(spec.layout, container.clientWidth).annotations }).catch(() => fail("failed", "GENERIC_PLOT_RENDER_FAILED"));
        }
        void Promise.resolve(api?.Plots?.resize(host)).catch(() => fail("failed", "GENERIC_PLOT_RENDER_FAILED"));
      } catch { fail("failed", "GENERIC_PLOT_RENDER_FAILED"); }
    };
    const resizeObserver = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(resize);
    resizeObserver?.observe(container);
    window.addEventListener("resize", resize);
    return () => {
      active = false;
      clearTimeout(timer);
      resizeObserver?.disconnect();
      window.removeEventListener("resize", resize);
      host.remove();
      purge();
    };
  }, [plotlyLoader, spec, attempt, reference, content]);

  return <section className={`workspace-generic-plot ${styles.plot}${isSavedPeriodicTable(content) ? ` ${styles.periodic}` : ""}`} aria-label="科学图表绘制" aria-busy={spec.ok && phase === "loading"}>
    <div ref={hostRef} hidden={!spec.ok || phase === "failed" || phase === "timeout"} className={`${styles.canvas}${spec.ok && record(record(spec.layout.coloraxis)?.colorbar)?.orientation === "h" ? ` ${styles.withColorScale}` : ""}`} data-testid="workspace-generic-plot-canvas" aria-label="科学图表" />
    {spec.ok && legendGroups && legendGroups.length > 1 ? <div className={styles.legend} role="group" aria-label={histogram ? "直方图分组" : scatter ? "散点图分组" : "图表数据系列"}>
      {legendGroups.map((group, index) => <button key={index} type="button" aria-pressed={!hidden.includes(index)}
        disabled={phase !== "ready" || !hidden.includes(index) && hidden.length === legendGroups.length - 1}
        onClick={() => setVisibility({ content, hidden: hidden.includes(index) ? hidden.filter(item => item !== index) : [...hidden, index] })}>
        <span aria-hidden="true" className={styles.legendSwatch} style={{ backgroundColor: PALETTE[index % PALETTE.length] }} />
        <span>{group.label}</span>
      </button>)}
    </div> : null}
    {spec.ok && phase === "ready" && spec.notes?.length ? <div aria-label="已保存的图表注释">{spec.notes.map((note, index) => <p key={index} style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>{note}</p>)}</div> : null}
    {reference ? <PlatformReferenceSources sources={reference.references} /> : null}
    {!spec.ok ? <p className="workspace-artifact-warning" role="alert">{plotLimitMessage(spec.code)}{spec.code !== "ELEMENT_HISTOGRAM_INCONSISTENT" ? " 可查看数值数据或数据与来源。" : ""}</p>
      : phase === "failed" || phase === "timeout" ? <div className="product-state scientific-plot-failure" role="alert" data-failure-code={result?.code}>
        <h5>{phase === "timeout" ? "图表绘制超时" : "图表暂时无法显示"}</h5>
        <p>{phase === "timeout" ? "绘图已等待超过 10 秒。" : result?.code === "GENERIC_PLOT_MODULE_LOAD_FAILED" ? "绘图组件未能加载。" : "绘图过程未能完成。"}已读取的数值仍可查看。</p>
        <button type="button" className="product-secondary-action" onClick={() => setAttempt((value) => value + 1)}>重新绘制图表</button>
      </div>
        : phase === "loading" ? <p className="product-loading" role="status">正在绘制图表…</p>
          : <p className={spec.decimated ? "workspace-table-preview-note" : "sr-only"} role="status" aria-live="polite">{spec.decimated
            ? `已渲染 ${spec.data.length} 个数据系列和 ${spec.pointCount}/${spec.totalPointCount} 条抽样记录（策略：${spec.samplingStrategy}）；完整数据仍然保留。`
            : `已渲染 ${spec.data.length} 个数据系列和 ${spec.pointCount} 个数值。`}</p>}
  </section>;
}

function plotLimitMessage(code: string): string {
  if (code === "ELEMENT_HISTOGRAM_INCONSISTENT") return "元素图表与保存的计数不一致，请重新分析；原始文件可在“数据与来源”中查看。";
  if (code === "PLOTLY_TRACE_TYPE_UNSUPPORTED") return "当前图表类型暂不支持显示。";
  if (code === "PLOTLY_TRACE_INVALID") return "图表数据格式无法读取。";
  if (code === "PLOTLY_NO_FINITE_POINTS") return "图表中没有可绘制的数据点。";
  if (code === "PLOTLY_LAYOUT_UNSUPPORTED") return "图表的坐标或尺度设置暂无法安全显示。";
  if (code === "PLOTLY_HEATMAP_CELL_CAP_EXCEEDED") return "热图网格超过交互显示上限，已拒绝渲染，未静默截断。";
  if (code === "PLOTLY_MESH_CAP_EXCEEDED") return "Mesh 顶点或三角面超过交互显示上限，已拒绝渲染，未静默截断。";
  if (code === "PLOTLY_POINT_CAP_EXCEEDED") return "图表点数超过交互显示上限，已拒绝渲染，未静默截断。";
  return "当前图表超出交互显示范围，已拒绝渲染，未静默截断。";
}

export function sanitizePlotSpec(content: unknown, maximumPoints: number): PlotSpec {
  if (!Number.isSafeInteger(maximumPoints) || maximumPoints < 1) return Object.freeze({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
  const elements = isSavedElementHistogram(content) ? readSavedElementHistogram(content) : null;
  if (isSavedElementHistogram(content) && !elements) return Object.freeze({ ok: false, code: "ELEMENT_HISTOGRAM_INCONSISTENT" });
  const histogram = isSavedHistogram(content) ? readSavedHistogram(content) : null;
  if (isSavedHistogram(content) && !histogram) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_INVALID" });
  const scatter = isSavedScatter(content) ? readSavedScatter(content) : null;
  if (isSavedScatter(content) && !scatter) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_INVALID" });
  if (scatter && scatter.pointCount > maximumPoints) return Object.freeze({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
  if (isSavedPeriodicTable(content)) {
    const plot = readSavedPeriodicTable(content);
    if (!plot) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_INVALID" });
    if (plot.pointCount > maximumPoints) return Object.freeze({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
    return Object.freeze({ ok: true, ...plot, totalPointCount: plot.pointCount, decimated: false, samplingStrategy: "无抽样（已保存的元素数值）", notes: readSavedElementReference(content)?.notes });
  }
  if (isSavedElementComparison(content) && !readSavedElementComparison(content)) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_INVALID" });
  if (isSavedDensityPlot(content)) {
    const plot = readSavedDensityPlot(content);
    if (!plot) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_INVALID" });
    if (plot.x.length > maximumPoints) return Object.freeze({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
    return Object.freeze({ ok: true, pointCount: plot.x.length, totalPointCount: plot.x.length, decimated: false, samplingStrategy: "无抽样（完整有限点）",
      notes: [...plot.annotations, ...(scatter?.notes ?? [])],
      data: [{ type: "scattergl", mode: "markers", x: plot.x, y: plot.y,
        marker: { ...(plot.solidColor ? { color: plot.solidColor } : { color: plot.density, coloraxis: "coloraxis" }), size: plot.markerSize, opacity: plot.opacity },
        ...(scatter ? { customdata: scatter.traces[0].rows } : {}),
        hovertemplate: scatter?.hovertemplate ?? (plot.solidColor ? "%{x}, %{y}<extra></extra>" : "%{x}, %{y}<br>%{marker.color}<extra></extra>") }],
      layout: {
        autosize: true, margin: { l: 66, r: 28, t: 48, b: plot.solidColor ? 64 : 145 }, paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff",
        title: { text: plot.title }, showlegend: false, hovermode: "closest",
        xaxis: { title: { text: plot.xLabel }, ...(plot.xRange ? { range: plot.xRange } : {}) },
        yaxis: { title: { text: plot.yLabel }, ...(plot.yRange ? { range: plot.yRange } : {}) },
        ...(plot.solidColor ? {} : { coloraxis: { colorscale: plot.colors, ...(plot.colorRange[0] !== plot.colorRange[1] ? { cmin: plot.colorRange[0], cmax: plot.colorRange[1] } : {}),
          colorbar: { orientation: "h", x: 0.5, xanchor: "center", yref: "container", y: 0.03, yanchor: "bottom", ypad: 0, len: 0.9, thickness: 12, title: { text: plot.densityLabel, side: "top" },
            tickvals: [...new Set(plot.colorRange)] } } }),
        shapes: plot.lines.map(line => ({ type: "line", x0: line.x0, x1: line.x1, y0: line.y0, y1: line.y1, xref: "x", yref: "y",
          layer: line.below ? "below" : "above", line: { color: line.color, width: line.width, dash: line.dash } })),
      },
    });
  }
  const figure = normalizedPlotFigure(content);
  const rawData = Array.isArray(figure?.data) ? figure.data : null;
  if (!rawData || !rawData.length || rawData.length > MAX_TRACE_COUNT) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_CAP_EXCEEDED" });
  let pointCount = 0;
  let decimated = false;
  const data: JsonRecord[] = [];
  for (const [index, raw] of rawData.entries()) {
    const trace = record(raw);
    if (!trace) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_INVALID" });
    const type = typeof trace?.type === "string" ? trace.type : "scatter";
    if (!ALLOWED_TRACE_TYPES.has(type)) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_TYPE_UNSUPPORTED" });
    const sanitized = sanitizeTrace(type, trace, index);
    if (!sanitized) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_INVALID" });
    if (histogram) {
      sanitized.customdata = histogram.edges.slice(0, -1).map((left, bin) => [left, histogram.edges[bin + 1], bin === histogram.counts.length - 1 ? "]" : ")"]);
      sanitized.hovertemplate = "区间：[%{customdata[0]}, %{customdata[1]}%{customdata[2]}<br>样本数：%{y}<extra>%{fullData.name}</extra>";
    }
    if (scatter) {
      sanitized.customdata = scatter.traces[index].rows;
      sanitized.hovertemplate = scatter.hovertemplate;
      sanitized.marker = { ...record(sanitized.marker), size: 6, opacity: 0.85 };
    }
    for (const key of ["xaxis", "yaxis", "scene"]) if (trace[key] !== undefined) sanitized[key] = trace[key];
    if (type === "heatmap" && tracePointCount(type, sanitized) > MAX_HEATMAP_CELLS) {
      return Object.freeze({ ok: false, code: "PLOTLY_HEATMAP_CELL_CAP_EXCEEDED" });
    }
    if (type === "mesh3d") {
      const vertexCount = tracePointCount(type, sanitized);
      const triangleCount = meshTriangleCount(sanitized);
      if (vertexCount > MAX_MESH_VERTICES || triangleCount > MAX_MESH_TRIANGLES) {
        return Object.freeze({ ok: false, code: "PLOTLY_MESH_CAP_EXCEEDED" });
      }
    }
    data.push(sanitized);
  }
  const rawPointCount = data.reduce((total, trace) => total + tracePointCount(String(trace.type), trace), 0);
  if (!data.some(hasPlottableData)) return Object.freeze({ ok: false, code: "PLOTLY_NO_FINITE_POINTS" });
  if (rawPointCount > maximumPoints && data.every((trace) => trace.type === "scatter" || trace.type === "scattergl")) {
    const required = data.map(trace => requiredSampleIndices(trace.x as PlotCoordinate[], trace.y as PlotCoordinate[], maximumPoints));
    if (required.some(indices => indices === null)) return Object.freeze({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
    const targets = required.map(indices => indices!.size);
    let remaining = maximumPoints - targets.reduce((sum, count) => sum + count, 0);
    if (remaining < 0) return Object.freeze({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
    const capacities = data.map((trace, index) => tracePointCount(String(trace.type), trace) - targets[index]);
    const capacity = capacities.reduce((sum, count) => sum + count, 0);
    const extra = capacities.map(count => capacity ? Math.floor(remaining * count / capacity) : 0);
    extra.forEach((count, index) => { targets[index] += count; remaining -= count; });
    for (let index = 0; index < targets.length && remaining > 0; index += 1) {
      if (targets[index] < tracePointCount(String(data[index].type), data[index])) { targets[index] += 1; remaining -= 1; }
    }
    for (const [index, trace] of data.entries()) {
      const current = tracePointCount(String(trace.type), trace);
      if (current > targets[index]) {
        const sampled = decimateTrace(trace, targets[index], required[index]!);
        trace.x = sampled.x;
        trace.y = sampled.y;
        decimated = true;
      }
    }
  }
  pointCount = data.reduce((total, trace) => total + tracePointCount(String(trace.type), trace), 0);
  if (pointCount > maximumPoints) return Object.freeze({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
  const layout = record(figure?.layout);
  const scientificLayout = readPlotLayout(layout, data);
  if (!scientificLayout) return Object.freeze({ ok: false, code: "PLOTLY_LAYOUT_UNSUPPORTED" });
  if (elements?.textLabels) {
    data[0].text = elements.textLabels;
    data[0].textposition = "outside";
    data[0].cliponaxis = false;
    data[0].textfont = { size: 12 };
  }
  for (const key of Object.keys(scientificLayout)) if (/^[xy]axis/.test(key)) {
    const axis = record(scientificLayout[key]);
    if (axis) axis.title = { text: localizePlotLabel(String(record(axis.title)?.text ?? "")) };
  }
  const source = record(content);
  const warnings = Array.isArray(source?.warnings) ? source.warnings : [];
  const notes = source?.artifactType === "composition.chem_sys_sunburst" && warnings.includes("too_many_leaf_nodes_warning")
    ? ["图表仅保留部分末级分组；父节点数值仍包含未显示分组。"]
    : source?.artifactType === "composition.chem_sys_treemap" && warnings.includes("too_many_groups_warning") ? ["图表仅显示部分分组。"] : [];
  return Object.freeze({
    ok: true,
    data,
    pointCount,
    totalPointCount: rawPointCount,
    decimated,
    notes: histogram ? histogramNotes(histogram) : elements?.notes ?? scatter?.notes ?? readSavedElementReference(content)?.notes ?? notes,
    samplingStrategy: decimated ? data.some(trace => (trace.x as PlotCoordinate[]).includes(null) || (trace.y as PlotCoordinate[]).includes(null))
      ? "保留断点与各段端点" : "保留端点、优先极值" : "无抽样（完整数据位置）",
    layout: Object.freeze({
      autosize: true,
      margin: data.every(trace => trace.type === "treemap" || trace.type === "sunburst")
        ? { l: 16, r: 16, t: 48, b: 16 } : { l: 66, r: 28, t: 48, b: 64 },
      paper_bgcolor: "#ffffff",
      plot_bgcolor: "#ffffff",
      title: { text: localizePlotLabel(safeText(titleText(layout?.title), 160)) },
      ...scientificLayout,
      ...(histogram ? { bargap: 0 } : {}),
      legend: { orientation: "h", x: 0, xanchor: "left", y: -0.35, yanchor: "top" },
      showlegend: data.length > 1 && data.length <= 16 && !data.some((trace) => trace.type === "scatter3d" || trace.type === "mesh3d"),
      hovermode: "closest",
    }),
  });
}

function sanitizeTrace(type: string, trace: JsonRecord, index: number): JsonRecord | null {
  const name = safeSeriesName(trace.name) || `Series ${index + 1}`;
  const color = PALETTE[index % PALETTE.length];
  if (type === "scatter" || type === "scattergl" || type === "bar") {
    const x = scalarArray(trace.x);
    const y = scalarArray(trace.y);
    if (!x || !y || x.length !== y.length || !x.length) return null;
    const width = type === "bar" && trace.width !== undefined
      ? typeof trace.width === "number" && Number.isFinite(trace.width) ? trace.width : numericArray(trace.width) : null;
    if (type === "bar" && trace.width !== undefined && (width === null || typeof width === "number" && width <= 0
      || Array.isArray(width) && (width.length !== x.length || width.some(value => value <= 0)))) return null;
    const bar: JsonRecord = {};
    if (type === "bar") {
      if (trace.orientation !== undefined && !["h", "v"].includes(String(trace.orientation))) return null;
      if (trace.orientation !== undefined) bar.orientation = trace.orientation;
      for (const key of ["base", "offset"]) if (trace[key] !== undefined) {
        const values = typeof trace[key] === "number" && Number.isFinite(trace[key]) ? trace[key] : numericArray(trace[key]);
        if (values === null || Array.isArray(values) && values.length !== x.length) return null;
        bar[key] = values;
      }
    }
    return { type, x, y, ...(width ? { width } : {}), ...bar, name, mode: type === "bar" ? undefined : allowedMode(trace.mode), connectgaps: false, marker: { color }, line: { color, width: 1.5 } };
  }
  if (type === "heatmap") {
    const z = numericMatrix(trace.z);
    if (!z?.length) return null;
    if (trace.transpose !== undefined && typeof trace.transpose !== "boolean") return null;
    const transpose = trace.transpose === true;
    const width = z.reduce((maximum, row) => Math.max(maximum, row.length), 0);
    if (!width) return null;
    const x = trace.x === undefined ? undefined : scalarArray(trace.x);
    const y = trace.y === undefined ? undefined : scalarArray(trace.y);
    const xCount = transpose ? z.length : width, yCount = transpose ? width : z.length;
    if (x === null || y === null || x?.includes(null) || y?.includes(null)
      || x && ![xCount, xCount + 1].includes(x.length) || y && ![yCount, yCount + 1].includes(y.length)) return null;
    const scale = readPlotColorScale(trace);
    if (!scale) return null;
    return { type, z, x, y, transpose, connectgaps: false, name, colorscale: "Viridis", showscale: true, ...scale };
  }
  if (type === "scatter3d") {
    const x = nullableNumericArray(trace.x);
    const y = nullableNumericArray(trace.y);
    const z = nullableNumericArray(trace.z);
    if (!x || !y || !z || x.length !== y.length || x.length !== z.length || !x.length) return null;
    const marker = record(trace.marker);
    const line = record(trace.line);
    return {
      type,
      x,
      y,
      z,
      name,
      mode: allowed3dMode(trace.mode),
      connectgaps: false,
      marker: {
        color: safePlotColor(marker?.color) || color,
        size: boundedNumber(marker?.size, 2, 18, 7),
        opacity: boundedNumber(marker?.opacity, 0.1, 1, 1),
      },
      line: {
        color: safePlotColor(line?.color) || color,
        width: boundedNumber(line?.width, 0.5, 12, 2),
      },
    };
  }
  if (type === "mesh3d") {
    const x = numericArray(trace.x);
    const y = numericArray(trace.y);
    const z = numericArray(trace.z);
    const i = indexArray(trace.i, x?.length ?? 0);
    const j = indexArray(trace.j, x?.length ?? 0);
    const k = indexArray(trace.k, x?.length ?? 0);
    if (!x || !y || !z || x.length !== y.length || x.length !== z.length || !x.length || !i || !j || !k || i.length !== j.length || i.length !== k.length) return null;
    return {
      type,
      x,
      y,
      z,
      i,
      j,
      k,
      name,
      color: safePlotColor(trace.color) || color,
      opacity: boundedNumber(trace.opacity, 0.05, 1, 0.25),
      showscale: false,
    };
  }
  const hierarchy = readPlotHierarchy(trace);
  return hierarchy ? { type, ...hierarchy, name } : null;
}

function tracePointCount(type: string, trace: JsonRecord): number {
  if (type === "heatmap") return Array.isArray(trace.z) ? trace.z.reduce((total, row) => total + (Array.isArray(row) ? row.length : 0), 0) : 0;
  if (type === "scatter3d" || type === "mesh3d") return Array.isArray(trace.x) ? trace.x.length : 0;
  return Array.isArray(trace.x) ? trace.x.length : Array.isArray(trace.labels) ? trace.labels.length : 0;
}

function meshTriangleCount(trace: JsonRecord): number {
  const indices = [trace.i, trace.j, trace.k].map((value) => Array.isArray(value) ? value.length : 0);
  return Math.min(...indices);
}

function hasPlottableData(trace: JsonRecord): boolean {
  if (trace.type === "heatmap") return (trace.z as Array<Array<number | null>>).some(row => row.some(value => value !== null));
  if (trace.type === "treemap" || trace.type === "sunburst") return (trace.values as number[]).some(value => value > 0);
  return (trace.x as PlotCoordinate[]).some((x, index) => x !== null && (trace.y as PlotCoordinate[])[index] !== null
    && (trace.type !== "scatter3d" || (trace.z as PlotCoordinate[])[index] !== null));
}

// Keep each finite segment's endpoints and an original missing position between
// segments. Sampling may discard points, but must never manufacture continuity.
function requiredSampleIndices(x: PlotCoordinate[], y: PlotCoordinate[], cap: number): Set<number> | null {
  const indices = new Set<number>();
  let start = 0;
  while (start < x.length) {
    const missing = x[start] === null || y[start] === null;
    let end = start + 1;
    while (end < x.length && (x[end] === null || y[end] === null) === missing) end += 1;
    indices.add(start);
    if (!missing) indices.add(end - 1);
    if (indices.size > cap) return null;
    start = end;
  }
  return indices;
}

function decimateTrace(trace: JsonRecord, target: number, required: Set<number>): { x: PlotCoordinate[]; y: PlotCoordinate[] } {
  const x = trace.x as PlotCoordinate[], y = trace.y as PlotCoordinate[];
  const indices = new Set(required);
  let globalMinIndex = -1;
  let globalMaxIndex = -1;
  for (let index = 0; index < y.length; index += 1) {
    if (x[index] === null || y[index] === null) continue;
    if (globalMinIndex < 0) { globalMinIndex = index; globalMaxIndex = index; }
    if (numericValue(y[index]) < numericValue(y[globalMinIndex])) globalMinIndex = index;
    if (numericValue(y[index]) > numericValue(y[globalMaxIndex])) globalMaxIndex = index;
  }
  if (globalMinIndex >= 0 && indices.size < target) indices.add(globalMinIndex);
  if (globalMaxIndex >= 0 && indices.size < target) indices.add(globalMaxIndex);
  const buckets = Math.max(1, Math.floor((target - 2) / 2));
  const localExtrema: number[] = [];
  for (let bucket = 0; bucket < buckets; bucket += 1) {
    const start = Math.floor((bucket * (x.length - 1)) / buckets);
    const end = Math.max(start + 1, Math.floor(((bucket + 1) * (x.length - 1)) / buckets));
    let minIndex = -1;
    let maxIndex = -1;
    for (let index = start; index <= Math.min(end, y.length - 1); index += 1) {
      if (x[index] === null || y[index] === null) continue;
      if (minIndex < 0) { minIndex = index; maxIndex = index; }
      if (numericValue(y[index]) < numericValue(y[minIndex])) minIndex = index;
      if (numericValue(y[index]) > numericValue(y[maxIndex])) maxIndex = index;
    }
    if (minIndex >= 0) localExtrema.push(minIndex, maxIndex);
  }
  for (const index of localExtrema) {
    if (indices.size >= target) break;
    indices.add(index);
  }
  for (let index = 1; indices.size < target && index < x.length - 1; index += 1) indices.add(index);
  const ordered = [...indices].sort((a, b) => a - b).slice(0, target);
  return { x: ordered.map((index) => x[index]), y: ordered.map((index) => y[index]) };
}

function numericValue(value: PlotCoordinate): number {
  if (value === null) return Number.NaN;
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

async function loadPlotly(): Promise<PlotlyApi> {
  const [coreModule, scatterModule, scatterglModule, scatter3dModule, mesh3dModule, barModule, heatmapModule, treemapModule, sunburstModule] = await Promise.all([
    import("plotly.js/lib/core"), import("plotly.js/lib/scatter"), import("plotly.js/lib/scattergl"), import("plotly.js/lib/scatter3d"), import("plotly.js/lib/mesh3d"), import("plotly.js/lib/bar"), import("plotly.js/lib/heatmap"), import("plotly.js/lib/treemap"), import("plotly.js/lib/sunburst"),
  ]);
  const plotly = ("default" in coreModule ? coreModule.default : coreModule) as unknown as PlotlyApi;
  const scatter = "default" in scatterModule ? scatterModule.default : scatterModule;
  const scattergl = "default" in scatterglModule ? scatterglModule.default : scatterglModule;
  const scatter3d = "default" in scatter3dModule ? scatter3dModule.default : scatter3dModule;
  const mesh3d = "default" in mesh3dModule ? mesh3dModule.default : mesh3dModule;
  const bar = "default" in barModule ? barModule.default : barModule;
  const heatmap = "default" in heatmapModule ? heatmapModule.default : heatmapModule;
  const treemap = "default" in treemapModule ? treemapModule.default : treemapModule;
  const sunburst = "default" in sunburstModule ? sunburstModule.default : sunburstModule;
  plotly.register?.([scatter, scattergl, scatter3d, mesh3d, bar, heatmap, treemap, sunburst]);
  return plotly;
}

function record(value: unknown): JsonRecord | null { return typeof value === "object" && value !== null && !Array.isArray(value) ? value as JsonRecord : null; }
function safeSeriesName(value: unknown): string {
  // Directed scientific pairs must survive the removal of HTML delimiters.
  return safeText(typeof value === "string" ? value.replace(/<->|->|<-/g, arrow => arrow === "->" ? "→" : arrow === "<-" ? "←" : "↔") : value, 96);
}
function safeText(value: unknown, cap: number): string { return typeof value === "string" ? value.replace(/[<>\r\n\t]/g, " ").slice(0, cap) : ""; }
function titleText(value: unknown): unknown { const item = record(value); return item ? item.text : value; }
function localizePlotLabel(value: string): string {
  const labels: Record<string, string> = {
    "Supplied electronic band structure": "电子能带",
    "Supplied electronic DOS": "电子态密度",
    "Reciprocal path": "倒易路径",
    "Energy / eV": "能量 / eV",
    "3D Structure": "晶体结构三维视图",
  };
  return labels[value] ?? value;
}
function allowedMode(value: unknown): string { return value === "markers" || value === "lines" || value === "lines+markers" ? value : "markers"; }
function allowed3dMode(value: unknown): string { return value === "markers" || value === "lines" || value === "lines+markers" ? value : "markers"; }
function scalarArray(value: unknown): PlotCoordinate[] | null {
  return readPlotCoordinates(value)?.map(item => typeof item === "string" ? safeText(item, 120) : item) ?? null;
}
function numericArray(value: unknown): number[] | null {
  return readPlotNumericVector(value);
}
function nullableNumericArray(value: unknown): Array<number | null> | null {
  return readPlotNumericVector(value, true);
}
function indexArray(value: unknown, pointCount: number): number[] | null {
  const items = Number.isSafeInteger(value) ? [Number(value)] : numericArray(value);
  return items && items.every((item) => Number.isSafeInteger(item) && item >= 0 && item < pointCount) ? items : null;
}
function numericMatrix(value: unknown): Array<Array<number | null>> | null {
  return readPlotNumericMatrix(value);
}
function mutableRendererCopy<T>(value: T): T { return JSON.parse(JSON.stringify(value)) as T; }
function boundedNumber(value: unknown, minimum: number, maximum: number, fallback: number): number { return typeof value === "number" && Number.isFinite(value) ? Math.min(maximum, Math.max(minimum, value)) : fallback; }
function safePlotColor(value: unknown): string | null { return typeof value === "string" && /^(?:#[0-9a-f]{3,8}|rgba?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}(?:\s*,\s*(?:0(?:\.\d+)?|1(?:\.0+)?))?\s*\))$/i.test(value.trim()) ? value.trim() : null; }
