"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { normalizedPlotFigure } from "./workspace-plot-contract";

type JsonRecord = Record<string, unknown>;
type PlotlyApi = Readonly<{
  newPlot: (target: HTMLElement, data: unknown[], layout: JsonRecord, config: JsonRecord) => Promise<unknown>;
  purge: (target: HTMLElement) => void;
  register?: (modules: unknown[]) => void;
  Plots?: Readonly<{ resize: (target: HTMLElement) => void }>;
}>;

type PlotlyLoader = () => Promise<PlotlyApi>;
type PlotSpec = Readonly<{ ok: true; data: unknown[]; layout: JsonRecord; pointCount: number; decimated: boolean }> | Readonly<{ ok: false; code: string }>;

const ALLOWED_TRACE_TYPES = new Set(["scatter", "scattergl", "scatter3d", "mesh3d", "bar", "heatmap", "treemap", "sunburst"]);
const MAX_TRACE_COUNT = 128;
const MAX_TYPED_ARRAY_BYTES = 8_000_000;
const PALETTE = ["#176b87", "#b84c3b", "#558b2f", "#7a5ca8", "#a26a00", "#2f6f6d"];

export function WorkspaceGenericPlot({ content, maximumPoints, plotlyLoader = loadPlotly }: Readonly<{ content: unknown; maximumPoints: number; plotlyLoader?: PlotlyLoader }>) {
  const hostRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState("正在加载已验证的科学图表。");
  const spec = useMemo(() => sanitizePlotSpec(content, maximumPoints), [content, maximumPoints]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host || !spec.ok) {
      if (!spec.ok) setStatus("当前图表超出交互显示范围，完整数值仍然保留在技术详情中。");
      return;
    }
    let active = true;
    let api: PlotlyApi | null = null;
    setStatus("正在加载科学图表渲染器。");
    void plotlyLoader().then(async (loaded) => {
      if (!active) return;
      api = loaded;
      await api.newPlot(host, mutableRendererCopy(spec.data), mutableRendererCopy(spec.layout), {
        responsive: true,
        displaylogo: false,
        displayModeBar: false,
        scrollZoom: false,
        staticPlot: false,
      });
      if (!active) {
        api.purge(host);
        return;
      }
      setStatus(spec.decimated
        ? `已渲染 ${spec.data.length} 个数据系列和 ${spec.pointCount} 个保真抽样数值；完整数值仍然保留。`
        : `已渲染 ${spec.data.length} 个数据系列和 ${spec.pointCount} 个数值。`);
    }).catch((error: unknown) => {
      if (!active) return;
      const detail = safeText(error instanceof Error ? error.message : String(error), 160);
      const code = api ? "GENERIC_PLOT_RENDER_FAILED" : "GENERIC_PLOT_MODULE_LOAD_FAILED";
      setStatus("科学图表暂时无法渲染，完整数值仍然保留。" + (detail ? ` (${code})` : ""));
    });
    const resize = () => api?.Plots?.resize(host);
    window.addEventListener("resize", resize);
    return () => {
      active = false;
      window.removeEventListener("resize", resize);
      if (api) api.purge(host);
    };
  }, [plotlyLoader, spec]);

  return <section className="workspace-generic-plot" aria-label="已验证的科学图表">
    <div ref={hostRef} data-testid="workspace-generic-plot-canvas" aria-label="科学图表" />
    {!spec.ok
      ? <p className="workspace-artifact-warning" role="status" aria-live="polite">{status}</p>
      : <p className="sr-only" role="status" aria-live="polite">{status}</p>}
  </section>;
}

export function sanitizePlotSpec(content: unknown, maximumPoints: number): PlotSpec {
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
    data.push(sanitized);
  }
  const rawPointCount = data.reduce((total, trace) => total + tracePointCount(String(trace.type), trace), 0);
  if (rawPointCount > maximumPoints && data.every((trace) => trace.type === "scatter" || trace.type === "scattergl" || trace.type === "bar")) {
    const target = Math.max(2, Math.floor(maximumPoints / Math.max(1, data.length)));
    for (const trace of data) {
      const current = tracePointCount(String(trace.type), trace);
      if (current > target) {
        const sampled = decimateTrace(trace, target);
        trace.x = sampled.x;
        trace.y = sampled.y;
        decimated = true;
      }
    }
  }
  pointCount = data.reduce((total, trace) => total + tracePointCount(String(trace.type), trace), 0);
  if (pointCount > maximumPoints) return Object.freeze({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
  const layout = record(figure?.layout);
  return Object.freeze({
    ok: true,
    data,
    pointCount,
    decimated,
    layout: Object.freeze({
      autosize: true,
      margin: { l: 66, r: 28, t: 48, b: 64 },
      paper_bgcolor: "#ffffff",
      plot_bgcolor: "#ffffff",
      title: { text: localizePlotLabel(safeText(titleText(layout?.title), 160)) },
      xaxis: { title: { text: localizePlotLabel(safeText(titleText(record(layout?.xaxis)?.title), 96)) } },
      yaxis: { title: { text: localizePlotLabel(safeText(titleText(record(layout?.yaxis)?.title), 96)) } },
      scene: {
        aspectmode: "data",
        xaxis: { title: { text: localizePlotLabel(safeText(titleText(record(record(layout?.scene)?.xaxis)?.title), 96)) } },
        yaxis: { title: { text: localizePlotLabel(safeText(titleText(record(record(layout?.scene)?.yaxis)?.title), 96)) } },
        zaxis: { title: { text: localizePlotLabel(safeText(titleText(record(record(layout?.scene)?.zaxis)?.title), 96)) } },
      },
      showlegend: data.length > 1 && data.length <= 16 && !data.some((trace) => trace.type === "scatter3d" || trace.type === "mesh3d"),
      hovermode: "closest",
    }),
  });
}

function sanitizeTrace(type: string, trace: JsonRecord, index: number): JsonRecord | null {
  const name = safeText(trace.name, 96) || `Series ${index + 1}`;
  const color = PALETTE[index % PALETTE.length];
  if (type === "scatter" || type === "scattergl" || type === "bar") {
    const x = scalarArray(trace.x);
    const y = scalarArray(trace.y);
    if (!x || !y || x.length !== y.length || !x.length) return null;
    return { type, x, y, name, mode: type === "bar" ? undefined : allowedMode(trace.mode), marker: { color }, line: { color, width: 1.5 } };
  }
  if (type === "heatmap") {
    const z = numericMatrix(trace.z);
    if (!z?.length) return null;
    const x = scalarArray(trace.x) ?? undefined;
    const y = scalarArray(trace.y) ?? undefined;
    return { type, z, x, y, name, colorscale: "Viridis", showscale: true };
  }
  if (type === "scatter3d") {
    const x = numericArray(trace.x);
    const y = numericArray(trace.y);
    const z = numericArray(trace.z);
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
  const labels = stringArray(trace.labels);
  const parents = stringArray(trace.parents);
  const values = numericArray(trace.values);
  if (!labels || !parents || !values || labels.length !== parents.length || labels.length !== values.length || !labels.length) return null;
  return { type, labels, parents, values, name, branchvalues: "total" };
}

function tracePointCount(type: string, trace: JsonRecord): number {
  if (type === "heatmap") return Array.isArray(trace.z) ? trace.z.reduce((total, row) => total + (Array.isArray(row) ? row.length : 0), 0) : 0;
  if (type === "scatter3d" || type === "mesh3d") return Array.isArray(trace.x) ? trace.x.length : 0;
  return Array.isArray(trace.x) ? trace.x.length : Array.isArray(trace.labels) ? trace.labels.length : 0;
}

function decimateTrace(trace: JsonRecord, target: number): { x: Array<number | string>; y: Array<number | string> } {
  const x = Array.isArray(trace.x) ? trace.x as Array<number | string> : [];
  const y = Array.isArray(trace.y) ? trace.y as Array<number | string> : [];
  if (x.length <= target || x.length !== y.length || target < 3) return { x: x.slice(0, target), y: y.slice(0, target) };
  const indices = new Set<number>([0, x.length - 1]);
  const buckets = Math.max(1, Math.floor((target - 2) / 2));
  for (let bucket = 0; bucket < buckets && indices.size < target; bucket += 1) {
    const start = Math.floor((bucket * (x.length - 1)) / buckets);
    const end = Math.max(start + 1, Math.floor(((bucket + 1) * (x.length - 1)) / buckets));
    let minIndex = start;
    let maxIndex = start;
    for (let index = start; index <= Math.min(end, y.length - 1); index += 1) {
      if (numericValue(y[index]) < numericValue(y[minIndex])) minIndex = index;
      if (numericValue(y[index]) > numericValue(y[maxIndex])) maxIndex = index;
    }
    indices.add(minIndex);
    if (indices.size < target) indices.add(maxIndex);
  }
  for (let index = 1; indices.size < target && index < x.length - 1; index += 1) indices.add(index);
  const ordered = [...indices].sort((a, b) => a - b).slice(0, target);
  return { x: ordered.map((index) => x[index]), y: ordered.map((index) => y[index]) };
}

function numericValue(value: number | string): number {
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
function scalarArray(value: unknown): Array<number | string> | null {
  if (Array.isArray(value) && value.every((item) => (typeof item === "number" && Number.isFinite(item)) || typeof item === "string")) {
    return value.map((item) => typeof item === "string" ? safeText(item, 120) : item);
  }
  return numericArray(value);
}
function numericArray(value: unknown): number[] | null {
  if (Array.isArray(value)) return value.every((item) => typeof item === "number" && Number.isFinite(item)) ? value : null;
  return decodePlotlyTypedArray(value);
}
function indexArray(value: unknown, pointCount: number): number[] | null {
  const items = Number.isSafeInteger(value) ? [Number(value)] : numericArray(value);
  return items && items.every((item) => Number.isSafeInteger(item) && item >= 0 && item < pointCount) ? items : null;
}
function stringArray(value: unknown): string[] | null { return Array.isArray(value) && value.every((item) => typeof item === "string") ? value.map((item) => safeText(item, 120)) : null; }
function numericMatrix(value: unknown): number[][] | null { return Array.isArray(value) && value.every((row) => numericArray(row) !== null) ? value as number[][] : null; }
function mutableRendererCopy<T>(value: T): T { return JSON.parse(JSON.stringify(value)) as T; }
function boundedNumber(value: unknown, minimum: number, maximum: number, fallback: number): number { return typeof value === "number" && Number.isFinite(value) ? Math.min(maximum, Math.max(minimum, value)) : fallback; }
function safePlotColor(value: unknown): string | null { return typeof value === "string" && /^(?:#[0-9a-f]{3,8}|rgba?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}(?:\s*,\s*(?:0(?:\.\d+)?|1(?:\.0+)?))?\s*\))$/i.test(value.trim()) ? value.trim() : null; }

function decodePlotlyTypedArray(value: unknown): number[] | null {
  const encoded = record(value);
  const dtype = typeof encoded?.dtype === "string" ? encoded.dtype : "";
  const bdata = typeof encoded?.bdata === "string" ? encoded.bdata : "";
  const match = /^([<>=|]?)([fiu])([1248])$/.exec(dtype);
  if (!match || !bdata || bdata.length > Math.ceil(MAX_TYPED_ARRAY_BYTES / 3) * 4 || !/^[A-Za-z0-9+/]*={0,2}$/.test(bdata)) return null;
  const kind = match[2];
  const bytesPerValue = Number(match[3]);
  if ((kind === "f" && ![4, 8].includes(bytesPerValue)) || (kind !== "f" && ![1, 2, 4].includes(bytesPerValue))) return null;
  let bytes: Uint8Array;
  try {
    const decoded = atob(bdata);
    if (!decoded.length || decoded.length > MAX_TYPED_ARRAY_BYTES || decoded.length % bytesPerValue !== 0) return null;
    bytes = Uint8Array.from(decoded, (character) => character.charCodeAt(0));
  } catch {
    return null;
  }
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const littleEndian = match[1] !== ">";
  const values: number[] = [];
  for (let offset = 0; offset < bytes.byteLength; offset += bytesPerValue) {
    const item = kind === "f"
      ? (bytesPerValue === 4 ? view.getFloat32(offset, littleEndian) : view.getFloat64(offset, littleEndian))
      : kind === "i"
        ? (bytesPerValue === 1 ? view.getInt8(offset) : bytesPerValue === 2 ? view.getInt16(offset, littleEndian) : view.getInt32(offset, littleEndian))
        : (bytesPerValue === 1 ? view.getUint8(offset) : bytesPerValue === 2 ? view.getUint16(offset, littleEndian) : view.getUint32(offset, littleEndian));
    if (!Number.isFinite(item)) return null;
    values.push(item);
  }
  return values;
}
