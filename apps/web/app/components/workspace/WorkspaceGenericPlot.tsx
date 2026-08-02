"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type JsonRecord = Record<string, unknown>;
type PlotlyApi = Readonly<{
  newPlot: (target: HTMLElement, data: unknown[], layout: JsonRecord, config: JsonRecord) => Promise<unknown>;
  purge: (target: HTMLElement) => void;
  register?: (modules: unknown[]) => void;
  Plots?: Readonly<{ resize: (target: HTMLElement) => void }>;
}>;

type PlotlyLoader = () => Promise<PlotlyApi>;
type PlotSpec = Readonly<{ ok: true; data: unknown[]; layout: JsonRecord; pointCount: number }> | Readonly<{ ok: false; code: string }>;

const ALLOWED_TRACE_TYPES = new Set(["scatter", "scattergl", "bar", "heatmap", "treemap", "sunburst"]);
const PALETTE = ["#176b87", "#b84c3b", "#558b2f", "#7a5ca8", "#a26a00", "#2f6f6d"];

export function WorkspaceGenericPlot({ content, maximumPoints, plotlyLoader = loadPlotly }: Readonly<{ content: unknown; maximumPoints: number; plotlyLoader?: PlotlyLoader }>) {
  const hostRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState("Loading validated numeric plot.");
  const spec = useMemo(() => sanitizePlotSpec(content, maximumPoints), [content, maximumPoints]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host || !spec.ok) {
      if (!spec.ok) setStatus(`${spec.code}: table and inert JSON remain available.`);
      return;
    }
    let active = true;
    let api: PlotlyApi | null = null;
    setStatus("Loading application-owned Plotly renderer.");
    void plotlyLoader().then(async (loaded) => {
      if (!active) return;
      api = loaded;
      await api.newPlot(host, spec.data, spec.layout, {
        responsive: true,
        displaylogo: false,
        scrollZoom: false,
        staticPlot: false,
      });
      if (!active) {
        api.purge(host);
        return;
      }
      setStatus(`Rendered ${spec.data.length} backend-produced series and ${spec.pointCount} bounded values.`);
    }).catch(() => {
      if (active) setStatus("GENERIC_PLOT_RENDER_FAILED: table and inert JSON remain available.");
    });
    const resize = () => api?.Plots?.resize(host);
    window.addEventListener("resize", resize);
    return () => {
      active = false;
      window.removeEventListener("resize", resize);
      if (api) api.purge(host);
    };
  }, [plotlyLoader, spec]);

  return <section className="workspace-generic-plot" aria-label="Validated backend-produced numeric plot">
    <div ref={hostRef} data-testid="workspace-generic-plot-canvas" aria-label="Backend-produced numeric plot" />
    <p className="sr-only" role="status" aria-live="polite">{status}</p>
    {!spec.ok ? <p className="workspace-artifact-warning" role="status">{status}</p> : null}
  </section>;
}

export function sanitizePlotSpec(content: unknown, maximumPoints: number): PlotSpec {
  const root = record(content);
  const figure = record(root?.figure) ?? root;
  const rawData = Array.isArray(figure?.data) ? figure.data : null;
  if (!rawData || !rawData.length || rawData.length > 32) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_CAP_EXCEEDED" });
  let pointCount = 0;
  const data: JsonRecord[] = [];
  for (const [index, raw] of rawData.entries()) {
    const trace = record(raw);
    if (!trace) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_INVALID" });
    const type = typeof trace?.type === "string" ? trace.type : "scatter";
    if (!ALLOWED_TRACE_TYPES.has(type)) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_TYPE_UNSUPPORTED" });
    const sanitized = sanitizeTrace(type, trace, index);
    if (!sanitized) return Object.freeze({ ok: false, code: "PLOTLY_TRACE_INVALID" });
    pointCount += tracePointCount(type, sanitized);
    if (pointCount > maximumPoints) return Object.freeze({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
    data.push(sanitized);
  }
  const layout = record(figure?.layout);
  return Object.freeze({
    ok: true,
    data,
    pointCount,
    layout: Object.freeze({
      autosize: true,
      margin: { l: 66, r: 28, t: 48, b: 64 },
      paper_bgcolor: "#ffffff",
      plot_bgcolor: "#ffffff",
      title: { text: safeText(titleText(layout?.title), 160) },
      xaxis: { title: { text: safeText(titleText(record(layout?.xaxis)?.title), 96) } },
      yaxis: { title: { text: safeText(titleText(record(layout?.yaxis)?.title), 96) } },
      showlegend: data.length > 1,
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
  const labels = stringArray(trace.labels);
  const parents = stringArray(trace.parents);
  const values = numericArray(trace.values);
  if (!labels || !parents || !values || labels.length !== parents.length || labels.length !== values.length || !labels.length) return null;
  return { type, labels, parents, values, name, branchvalues: "total" };
}

function tracePointCount(type: string, trace: JsonRecord): number {
  if (type === "heatmap") return Array.isArray(trace.z) ? trace.z.reduce((total, row) => total + (Array.isArray(row) ? row.length : 0), 0) : 0;
  return Array.isArray(trace.x) ? trace.x.length : Array.isArray(trace.labels) ? trace.labels.length : 0;
}

async function loadPlotly(): Promise<PlotlyApi> {
  const [coreModule, scatterModule, scatterglModule, barModule, heatmapModule, treemapModule, sunburstModule] = await Promise.all([
    import("plotly.js/lib/core"), import("plotly.js/lib/scatter"), import("plotly.js/lib/scattergl"), import("plotly.js/lib/bar"), import("plotly.js/lib/heatmap"), import("plotly.js/lib/treemap"), import("plotly.js/lib/sunburst"),
  ]);
  const plotly = ("default" in coreModule ? coreModule.default : coreModule) as unknown as PlotlyApi;
  const scatter = "default" in scatterModule ? scatterModule.default : scatterModule;
  const scattergl = "default" in scatterglModule ? scatterglModule.default : scatterglModule;
  const bar = "default" in barModule ? barModule.default : barModule;
  const heatmap = "default" in heatmapModule ? heatmapModule.default : heatmapModule;
  const treemap = "default" in treemapModule ? treemapModule.default : treemapModule;
  const sunburst = "default" in sunburstModule ? sunburstModule.default : sunburstModule;
  plotly.register?.([scatter, scattergl, bar, heatmap, treemap, sunburst]);
  return plotly;
}

function record(value: unknown): JsonRecord | null { return typeof value === "object" && value !== null && !Array.isArray(value) ? value as JsonRecord : null; }
function safeText(value: unknown, cap: number): string { return typeof value === "string" ? value.replace(/[<>\r\n\t]/g, " ").slice(0, cap) : ""; }
function titleText(value: unknown): unknown { const item = record(value); return item ? item.text : value; }
function allowedMode(value: unknown): string { return value === "markers" || value === "lines" || value === "lines+markers" ? value : "markers"; }
function scalarArray(value: unknown): Array<number | string> | null { return Array.isArray(value) && value.every((item) => (typeof item === "number" && Number.isFinite(item)) || typeof item === "string") ? value.map((item) => typeof item === "string" ? safeText(item, 120) : item) : null; }
function numericArray(value: unknown): number[] | null { return Array.isArray(value) && value.every((item) => typeof item === "number" && Number.isFinite(item)) ? value : null; }
function stringArray(value: unknown): string[] | null { return Array.isArray(value) && value.every((item) => typeof item === "string") ? value.map((item) => safeText(item, 120)) : null; }
function numericMatrix(value: unknown): number[][] | null { return Array.isArray(value) && value.every((row) => numericArray(row) !== null) ? value as number[][] : null; }
