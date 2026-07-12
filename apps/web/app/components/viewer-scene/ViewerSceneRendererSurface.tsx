"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { ViewerMeasurementPanel } from "./ViewerMeasurementPanel";
import { ViewerSiteInspector } from "./ViewerSiteInspector";
import { downloadLocalBlob, jsonBlob, sanitizeViewerFilename } from "./viewerSceneExport";
import { measureAngle, measureDihedral, measureDistance, type ViewerMeasurementEvaluation, type ViewerMeasurementResult } from "./viewerSceneMeasurements";
import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import { ViewerRendererError } from "./viewerSceneRendererErrors";
import type { RenderVector3, ViewerRendererEngine, ViewerRendererEngineFactory, ViewerRendererSnapshot, ViewerRendererState } from "./viewerSceneRendererTypes";
import { changeViewerSelectionMode, initialViewerSelection, selectViewerSite, type ViewerSelectionMode } from "./viewerSceneSelection";

export type ViewerSceneRendererSurfaceProps = {
  readonly payload: unknown;
  readonly capabilityOverride?: boolean;
  readonly engineFactory?: ViewerRendererEngineFactory;
  readonly downloads?: Readonly<{ manifest?: unknown; summary?: string; recipe?: unknown }>;
};

const defaultEngineFactory: ViewerRendererEngineFactory = async (args) => {
  let timeout: ReturnType<typeof setTimeout> | undefined;
  let module: typeof import("./viewerSceneRendererEngine");
  try {
    module = await Promise.race([
      import("./viewerSceneRendererEngine"),
      new Promise<never>((_, reject) => {
        timeout = setTimeout(() => reject(new Error("renderer chunk timeout")), 15_000);
      }),
    ]);
  } catch {
    throw new ViewerRendererError("VIEWER_RENDERER_CHUNK_LOAD_FAILED", "The local renderer module could not be loaded.");
  } finally {
    if (timeout) clearTimeout(timeout);
  }
  return module.createThreeViewerEngine(args);
};

export function ViewerSceneRendererSurface({ payload, capabilityOverride, engineFactory = defaultEngineFactory, downloads }: ViewerSceneRendererSurfaceProps) {
  const mapping = useMemo(() => mapViewerSceneForRenderer(payload), [payload]);
  const containerRef = useRef<HTMLDivElement>(null);
  const engineRef = useRef<ViewerRendererEngine | null>(null);
  const [state, setState] = useState<ViewerRendererState>(mapping.ok ? "ready" : "validation_failed");
  const [showCell, setShowCell] = useState(true);
  const [showBonds, setShowBonds] = useState(true);
  const [snapshot, setSnapshot] = useState<ViewerRendererSnapshot | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [selection, setSelection] = useState(initialViewerSelection());
  const [history, setHistory] = useState<readonly ViewerMeasurementResult[]>([]);
  const [exportError, setExportError] = useState<string | null>(null);
  const onSitePick = useCallback((siteIndex: number | null) => setSelection((current) => selectViewerSite(current, siteIndex)), []);

  useEffect(() => {
    setState(mapping.ok ? "ready" : "validation_failed");
    setSnapshot(null);
    setSelection(initialViewerSelection());
    setHistory([]);
    if (!mapping.ok) return;
    const supported = capabilityOverride ?? supportsWebGL();
    if (!supported) {
      setState("unsupported");
      return;
    }
    const container = containerRef.current;
    if (!container) return;
    let cancelled = false;
    setState("initializing_renderer");
    void engineFactory({
      container,
      scene: mapping.scene,
      pixelRatioCap: 2,
      onContextLost: () => {
        setState("context_lost");
        queueMicrotask(() => {
          engineRef.current?.dispose();
          engineRef.current = null;
        });
      },
      onSitePick,
    }).then((engine) => {
      if (cancelled) {
        engine.dispose();
        return;
      }
      engineRef.current = engine;
      engine.setCellVisible(showCell);
      engine.setBondsVisible(showBonds);
      engine.setSelection([]);
      setSnapshot(engine.snapshot());
      setState("rendered");
    }).catch((error: unknown) => {
      if (!cancelled) setState(error instanceof ViewerRendererError && error.code === "VIEWER_RENDERER_CHUNK_LOAD_FAILED" ? "chunk_load_failed" : "renderer_failed");
    });
    return () => {
      cancelled = true;
      const engine = engineRef.current;
      engineRef.current = null;
      if (engine) {
        try { engine.dispose(); } catch { /* disposal is best-effort after the surface is detached */ }
      }
    };
  }, [attempt, capabilityOverride, engineFactory, mapping, onSitePick]);

  useEffect(() => {
    engineRef.current?.setSelection(selection.selectedSiteIndices);
    if (engineRef.current) setSnapshot(engineRef.current.snapshot());
  }, [selection.selectedSiteIndices]);

  const measurement = useMemo<ViewerMeasurementEvaluation | null>(() => {
    if (!mapping.ok || selection.mode === "inspect") return null;
    const atoms = new Map(mapping.scene.atoms.map((atom) => [atom.siteIndex, atom] as const));
    const points = selection.selectedSiteIndices.map((index) => atoms.get(index)?.position).filter((point): point is RenderVector3 => Boolean(point));
    if (selection.mode === "distance" && points.length === 2) return measureDistance(selection.selectedSiteIndices as [number, number], [points[0], points[1]]);
    if (selection.mode === "angle" && points.length === 3) return measureAngle(selection.selectedSiteIndices as [number, number, number], [points[0], points[1], points[2]]);
    if (selection.mode === "dihedral" && points.length === 4) return measureDihedral(selection.selectedSiteIndices as [number, number, number, number], [points[0], points[1], points[2], points[3]]);
    return null;
  }, [mapping, selection]);

  useEffect(() => {
    if (!measurement?.ok) return;
    setHistory((current) => {
      const key = `${measurement.result.kind}:${measurement.result.siteIndices.join("-")}`;
      if (current.some((item) => `${item.kind}:${item.siteIndices.join("-")}` === key)) return current;
      return Object.freeze([...current, measurement.result].slice(-20));
    });
  }, [measurement]);

  const applyVisibility = (kind: "cell" | "bonds", visible: boolean) => {
    if (kind === "cell") {
      setShowCell(visible);
      engineRef.current?.setCellVisible(visible);
    } else {
      setShowBonds(visible);
      engineRef.current?.setBondsVisible(visible);
    }
    if (engineRef.current) setSnapshot(engineRef.current.snapshot());
  };
  const reset = () => {
    engineRef.current?.resetCamera();
    if (engineRef.current) setSnapshot(engineRef.current.snapshot());
  };
  const retry = () => {
    setState("ready");
    setAttempt((value) => value + 1);
  };
  const changeMode = (mode: ViewerSelectionMode) => setSelection((current) => changeViewerSelectionMode(current, mode));
  const clearSelection = () => setSelection((current) => initialViewerSelection(current.mode));
  const exportPng = async () => {
    setExportError(null);
    try {
      const blob = await engineRef.current?.exportPng();
      if (!blob) throw new Error("VIEWER_EXPORT_RENDERER_UNAVAILABLE");
      downloadLocalBlob(blob, sanitizeViewerFilename(mapping.ok ? mapping.scene.formula : "structure"));
    } catch {
      setExportError("Current-view PNG export failed. Scene JSON remains available.");
    }
  };
  const selectedAtom = mapping.ok ? mapping.scene.atoms.find((atom) => atom.siteIndex === selection.activeSiteIndex) ?? null : null;

  return (
    <section className="viewer-renderer-surface" aria-label="3D Structure Viewer" data-testid="viewer-scene-renderer-surface">
      <div className="viewer-renderer-toolbar">
        <div>
          <strong>3D Structure Viewer</strong>
          <span role="status" aria-live="polite" data-testid="viewer-scene-renderer-state">{state}</span>
        </div>
        <div className="viewer-renderer-controls" aria-label="Viewer controls">
          <button type="button" className="compact secondary" data-testid="viewer-scene-renderer-reset" onClick={reset} disabled={state !== "rendered"}>Reset camera</button>
          <button type="button" className={`compact ${showCell ? "active" : "secondary"}`} data-testid="viewer-scene-renderer-toggle-cell" aria-pressed={showCell} onClick={() => applyVisibility("cell", !showCell)}>Unit cell</button>
          <button type="button" className={`compact ${showBonds ? "active" : "secondary"}`} data-testid="viewer-scene-renderer-toggle-bonds" aria-pressed={showBonds} onClick={() => applyVisibility("bonds", !showBonds)}>Bonds</button>
          <button type="button" className="compact secondary" data-testid="viewer-scene-export-png" onClick={() => void exportPng()} disabled={state !== "rendered"}>Download PNG</button>
        </div>
      </div>

      {!mapping.ok ? (
        <div className="viewer-renderer-fallback" data-testid="viewer-scene-renderer-invalid">
          <strong>Scene validation failed</strong>
          <p>The renderer was not initialized. Review the inert JSON preview for contract errors.</p>
          <code>{mapping.validation.errors.join(", ")}</code>
        </div>
      ) : null}
      {mapping.ok && state === "unsupported" ? (
        <div className="viewer-renderer-fallback" data-testid="viewer-scene-renderer-unavailable">
          <strong>Interactive renderer unavailable</strong>
          <p>This browser did not provide a usable WebGL context. The Scene JSON and Manifest views remain available.</p>
        </div>
      ) : null}
      {mapping.ok && (state === "renderer_failed" || state === "chunk_load_failed" || state === "context_lost") ? (
        <div className="viewer-renderer-fallback" data-testid="viewer-scene-renderer-fallback">
          <strong>{state === "context_lost" ? "Graphics context lost" : state === "chunk_load_failed" ? "Renderer module unavailable" : "Renderer initialization failed"}</strong>
          <p>The artifact remains available as validated JSON. No artifact content was executed.</p>
          {state === "chunk_load_failed" ? <button type="button" className="compact secondary" onClick={retry}>Retry renderer</button> : null}
        </div>
      ) : null}
      {mapping.ok && state === "initializing_renderer" ? <p className="viewer-renderer-loading">Initializing local renderer...</p> : null}
      {mapping.ok && !["unsupported", "renderer_failed", "chunk_load_failed", "context_lost"].includes(state) ? (
        <div ref={containerRef} className="viewer-renderer-canvas-host" data-testid="viewer-scene-renderer-valid">
          <span className="sr-only">Interactive canvas showing {mapping.scene.atoms.length} sites, {new Set(mapping.scene.atoms.map((atom) => atom.species)).size} species, and {mapping.scene.bonds.length} bounded bonds.</span>
        </div>
      ) : null}
      {mapping.ok ? (
        <>
        <ViewerMeasurementPanel mode={selection.mode} selected={selection.selectedSiteIndices} evaluation={measurement} history={history} onMode={changeMode} onClear={clearSelection} />
        <ViewerSiteInspector atom={selectedAtom} bonds={mapping.scene.bonds} source={mapping.scene.source.filename || mapping.scene.source.resourceId} onClear={clearSelection} />
        <div className="viewer-artifact-downloads" aria-label="Viewer artifact downloads">
          <button type="button" className="compact secondary" onClick={() => downloadLocalBlob(jsonBlob(payload), "viewer_scene.json")}>Download scene JSON</button>
          {downloads?.manifest ? <button type="button" className="compact secondary" onClick={() => downloadLocalBlob(jsonBlob(downloads.manifest), "viewer_scene_manifest.json")}>Download manifest</button> : null}
          {downloads?.summary ? <button type="button" className="compact secondary" onClick={() => downloadLocalBlob(new Blob([downloads.summary ?? ""], { type: "text/markdown" }), "summary.md")}>Download summary</button> : null}
          {downloads?.recipe ? <button type="button" className="compact secondary" onClick={() => downloadLocalBlob(jsonBlob(downloads.recipe), "recipe.json")}>Download recipe</button> : null}
        </div>
        {exportError ? <p className="notice" role="alert" data-testid="viewer-scene-export-error">{exportError}</p> : null}
        <p className="viewer-renderer-scene-summary" data-testid="viewer-scene-renderer-summary">
          Validated canonical scene: {mapping.scene.atoms.length} sites, {new Set(mapping.scene.atoms.map((atom) => atom.species)).size} species, {mapping.scene.bonds.length} bounded bonds.
        </p>
        <ul className="viewer-renderer-species-legend" aria-label="Species legend">
          {[...new Map(mapping.scene.atoms.map((atom) => [atom.species, atom])).values()].map((atom) => <li key={atom.species}><span aria-hidden="true" style={{ backgroundColor: atom.color }} />{atom.species}</li>)}
        </ul>
        <dl className="mini-grid viewer-renderer-audit" data-testid="viewer-scene-renderer-audit">
          <div><dt>sites</dt><dd>{mapping.scene.atoms.length}</dd></div>
          <div><dt>species</dt><dd>{new Set(mapping.scene.atoms.map((atom) => atom.species)).size}</dd></div>
          <div><dt>bonds</dt><dd>{snapshot?.bondCount ?? mapping.scene.bonds.length}</dd></div>
          <div><dt>cell edges</dt><dd>{snapshot?.latticeEdgeCount ?? 12}</dd></div>
          <div><dt>graphics</dt><dd>{snapshot?.graphicsContext ?? "pending"}</dd></div>
          <div><dt>renderer</dt><dd>{snapshot?.rendererVersion ? `Three r${snapshot.rendererVersion}` : "pending"}</dd></div>
        </dl>
        <output className="sr-only" data-testid="viewer-scene-renderer-metrics">{snapshot ? JSON.stringify(snapshot.metrics) : "metrics pending"}</output>
        </>
      ) : null}
    </section>
  );
}

function supportsWebGL() {
  if (typeof window === "undefined" || typeof document === "undefined") return false;
  if (/jsdom/i.test(window.navigator.userAgent)) return false;
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl"));
  } catch {
    return false;
  }
}
