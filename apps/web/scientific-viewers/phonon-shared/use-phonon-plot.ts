"use client";

import { useEffect, useRef, useState } from "react";

type JsonRecord = Record<string, unknown>;
export type PhononPlotlyApi = {
  newPlot: (target: HTMLElement, data: unknown[], layout: JsonRecord, config: JsonRecord) => Promise<unknown>;
  purge: (target: HTMLElement) => void;
  downloadImage?: (target: HTMLElement, options: JsonRecord) => Promise<unknown>;
  register?: (modules: unknown[]) => void;
  Plots?: { resize: (target: HTMLElement) => void | Promise<unknown> };
};
export type PhononPlotlyLoader = () => Promise<PhononPlotlyApi>;
type PlotSpec = { ok: true; data: unknown[]; layout: JsonRecord } | { ok: false; message: string };
type Phase = "loading" | "rendered" | "error" | "timeout" | "refused";

/** A timed-out Plotly render can still mutate its target. Detach that target
 * before retrying, and never let an old render purge a newer canvas. */
export function usePhononPlot(spec: PlotSpec, loader: PhononPlotlyLoader) {
  const hostRef = useRef<HTMLDivElement>(null);
  const renderer = useRef<{ api: PhononPlotlyApi; host: HTMLElement } | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [result, setResult] = useState<{ spec: PlotSpec; attempt: number; phase: Phase } | null>(null);
  const phase: Phase = !spec.ok ? "refused" : result?.spec === spec && result.attempt === attempt ? result.phase : "loading";
  const [exportState, setExportState] = useState<"idle" | "pending" | "failed">("idle");
  const exportRef = useRef<{ timer: ReturnType<typeof setTimeout> } | null>(null);
  useEffect(() => {
    const container = hostRef.current;
    if (!container || !spec.ok) return;
    const host = document.createElement("div");
    host.style.width = "100%"; host.style.height = "100%";
    container.replaceChildren(host);
    let active = true, ready = false, purged = false;
    let api: PhononPlotlyApi | null = null;
    const purge = () => { if (!api || purged) return; purged = true; try { api.purge(host); } catch { /* Detached failed geometry is disposable. */ } };
    const fail = (phase: "error" | "timeout") => {
      if (!active) return;
      active = false; clearTimeout(timer); host.remove(); purge();
      if (renderer.current?.host === host) renderer.current = null;
      setResult({ spec, attempt, phase });
    };
    const timer = setTimeout(() => fail("timeout"), 10_000);
    void Promise.resolve().then(loader).then(async loaded => {
      if (!active) return;
      api = loaded;
      try {
        const layout = structuredClone(spec.layout);
        const style = getComputedStyle(container);
        layout.font = { family: style.fontFamily, size: 13, color: style.color, ...(layout.font as JsonRecord | undefined) };
        await api.newPlot(host, structuredClone(spec.data), layout, { responsive: true, displaylogo: false, displayModeBar: false, scrollZoom: false });
      } finally { if (!active) { purged = false; purge(); } }
      if (!active) return;
      clearTimeout(timer); ready = true; renderer.current = { api, host };
      setResult({ spec, attempt, phase: "rendered" });
    }).catch(() => fail("error"));
    const resize = () => {
      if (!active || !ready) return;
      try { void Promise.resolve(api?.Plots?.resize(host)).catch(() => fail("error")); } catch { fail("error"); }
    };
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(resize);
    observer?.observe(container); window.addEventListener("resize", resize);
    setExportState("idle");
    return () => {
      active = false; clearTimeout(timer); observer?.disconnect(); window.removeEventListener("resize", resize); host.remove(); purge();
      if (renderer.current?.host === host) renderer.current = null;
      if (exportRef.current) clearTimeout(exportRef.current.timer);
      exportRef.current = null;
    };
  }, [spec, loader, attempt]);
  const downloadPng = (filename: string, size = { width: 800, height: 500 }) => {
    const current = renderer.current;
    if (phase !== "rendered" || !current?.api.downloadImage || exportRef.current) return;
    setExportState("pending");
    const request = { timer: setTimeout(() => finish("failed"), 10_000) };
    function finish(state: "idle" | "failed") {
      if (exportRef.current !== request) return;
      clearTimeout(request.timer); exportRef.current = null; setExportState(state);
    }
    exportRef.current = request;
    void Promise.resolve().then(() => current.api.downloadImage!(current.host, { format: "png", filename, ...size, scale: 2 })).then(() => finish("idle"), () => finish("failed"));
  };
  return { hostRef, phase, retry: () => setAttempt(value => value + 1), downloadPng, exportState, canExport: phase === "rendered" && Boolean(renderer.current?.api.downloadImage) };
}

export async function loadPhononPlotly(): Promise<PhononPlotlyApi> {
  const [coreModule, scatterModule] = await Promise.all([import("plotly.js/lib/core"), import("plotly.js/lib/scatter")]);
  const api = ("default" in coreModule ? coreModule.default : coreModule) as unknown as PhononPlotlyApi;
  api.register?.(["default" in scatterModule ? scatterModule.default : scatterModule]);
  return api;
}
