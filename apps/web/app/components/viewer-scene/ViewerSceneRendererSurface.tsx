"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { ViewerMeasurementPanel, type PeriodicMeasurementMode } from "./ViewerMeasurementPanel";
import { ViewerSiteInspector } from "./ViewerSiteInspector";
import { downloadLocalBlob, jsonBlob, sanitizeViewerFilename } from "./viewerSceneExport";
import { measureAngle, measureDihedral, measureDistance, type ViewerMeasurementEvaluation, type ViewerMeasurementResult } from "./viewerSceneMeasurements";
import { minimumImage, periodicAngle, periodicDihedral, periodicSiteKey } from "./viewerScenePeriodicGeometry";
import { classifyViewerPerformance } from "./viewerScenePerformance";
import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import { ViewerRendererError } from "./viewerSceneRendererErrors";
import type { ImageOffset, PeriodicSiteRef, RenderVector3, ViewerRendererEngine, ViewerRendererEngineFactory, ViewerRendererSnapshot, ViewerRendererState } from "./viewerSceneRendererTypes";
import { changeViewerSelectionMode, initialViewerSelection, selectViewerSite, type ViewerSelectionMode } from "./viewerSceneSelection";
import { derivePeriodicSupercell, PERIODIC_DERIVED_CAPS, type SupercellRepeat } from "./viewerSceneSupercell";

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

const DEFAULT_REPEAT: SupercellRepeat = Object.freeze([1,1,1]);

export function ViewerSceneRendererSurface({ payload, capabilityOverride, engineFactory = defaultEngineFactory, downloads }: ViewerSceneRendererSurfaceProps) {
  const mapping = useMemo(() => mapViewerSceneForRenderer(payload), [payload]);
  const previousPayloadRef = useRef(payload);
  const payloadChanged = previousPayloadRef.current !== payload;
  const containerRef = useRef<HTMLDivElement>(null);
  const engineRef = useRef<ViewerRendererEngine | null>(null);
  const generationRef = useRef(0);
  const [state, setState] = useState<ViewerRendererState>(mapping.ok ? "ready" : "validation_failed");
  const [showCell, setShowCell] = useState(true);
  const [showBonds, setShowBonds] = useState(true);
  const [snapshot, setSnapshot] = useState<ViewerRendererSnapshot | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [selection, setSelection] = useState(initialViewerSelection());
  const selectionRef = useRef(selection);
  const [history, setHistory] = useState<readonly ViewerMeasurementResult[]>([]);
  const [coordinateMode, setCoordinateMode] = useState<PeriodicMeasurementMode>("displayed_positions");
  const [repeat, setRepeat] = useState<SupercellRepeat>(DEFAULT_REPEAT);
  const [repeatDraft, setRepeatDraft] = useState<SupercellRepeat>(DEFAULT_REPEAT);
  const [neighborSiteIndex, setNeighborSiteIndex] = useState<number | null>(null);
  const [supercellError, setSupercellError] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  const renderedRepeat = payloadChanged ? DEFAULT_REPEAT : repeat;
  const renderedNeighborSiteIndex = payloadChanged ? null : neighborSiteIndex;
  const derivation = useMemo(() => mapping.ok ? derivePeriodicSupercell(mapping.scene, renderedRepeat, renderedNeighborSiteIndex) : null, [mapping, renderedNeighborSiteIndex, renderedRepeat]);
  const renderScene = derivation?.ok ? derivation.scene : mapping.ok ? mapping.scene : null;
  const performanceDecision = useMemo(() => renderScene ? classifyViewerPerformance(renderScene) : null, [renderScene]);
  const onSitePick = useCallback((site: PeriodicSiteRef | null) => setSelection((current) => selectViewerSite(current, site)), []);

  useEffect(() => { selectionRef.current = selection; }, [selection]);

  useEffect(() => {
    if (previousPayloadRef.current === payload) return;
    previousPayloadRef.current = payload;
    setSelection(initialViewerSelection()); setHistory([]); setCoordinateMode("displayed_positions");
    setRepeat(DEFAULT_REPEAT); setRepeatDraft(DEFAULT_REPEAT); setNeighborSiteIndex(null); setSupercellError(null);
  }, [payload]);

  useEffect(() => {
    setState(mapping.ok ? "ready" : "validation_failed");
    setSnapshot(null);
    if (!mapping.ok || !renderScene || !performanceDecision) return;
    if (performanceDecision.tier === "refused") {
      setState("scene_over_renderer_cap");
      return;
    }
    const supported = capabilityOverride ?? supportsWebGL();
    if (!supported) {
      setState("unsupported");
      return;
    }
    const container = containerRef.current;
    if (!container) return;
    let cancelled = false;
    const generation = ++generationRef.current;
    setState("initializing_renderer");
    void engineFactory({
      container,
      scene: renderScene,
      pixelRatioCap: performanceDecision.pixelRatioCap,
      antialias: performanceDecision.antialias,
      performanceTier: performanceDecision.tier,
      onContextLost: () => {
        setState("context_lost");
        queueMicrotask(() => {
          engineRef.current?.dispose();
          engineRef.current = null;
        });
      },
      onSitePick,
    }).then((engine) => {
      if (cancelled || generation !== generationRef.current) {
        engine.dispose();
        return;
      }
      engineRef.current = engine;
      engine.setCellVisible(showCell);
      engine.setBondsVisible(showBonds);
      engine.setSelection(selectionRef.current.selectedSites);
      setSnapshot(engine.snapshot());
      setState("rendered");
    }).catch((error: unknown) => {
      if (!cancelled) setState(error instanceof ViewerRendererError && error.code === "VIEWER_RENDERER_CHUNK_LOAD_FAILED" ? "chunk_load_failed" : "renderer_failed");
    });
    return () => {
      cancelled = true;
      if (generation === generationRef.current) generationRef.current += 1;
      const engine = engineRef.current;
      engineRef.current = null;
      if (engine) {
        try { engine.dispose(); } catch { /* disposal is best-effort after the surface is detached */ }
      }
    };
  }, [attempt, capabilityOverride, engineFactory, mapping, onSitePick, performanceDecision, renderScene]);

  useEffect(() => {
    engineRef.current?.setSelection(selection.selectedSites);
    if (engineRef.current) setSnapshot(engineRef.current.snapshot());
  }, [selection.selectedSites]);

  const measurementDetails = useMemo<{ readonly evaluation: ViewerMeasurementEvaluation | null; readonly refs: readonly PeriodicSiteRef[] }>(() => {
    if (!mapping.ok || !renderScene || selection.mode === "inspect") return { evaluation: null, refs: Object.freeze([]) };
    const atomsByRef = new Map(renderScene.atoms.map((atom) => [periodicSiteKey(atom.ref), atom] as const));
    const points = selection.selectedSites.map((ref) => atomsByRef.get(periodicSiteKey(ref))?.position).filter((point): point is RenderVector3 => Boolean(point));
    const indices = selection.selectedSites.map((ref) => ref.siteIndex);
    if (coordinateMode === "displayed_positions") {
      if (selection.mode === "distance" && points.length === 2) return { evaluation: measureDistance(indices as [number, number], [points[0], points[1]]), refs: selection.selectedSites };
      if (selection.mode === "angle" && points.length === 3) return { evaluation: measureAngle(indices as [number, number, number], [points[0], points[1], points[2]]), refs: selection.selectedSites };
      if (selection.mode === "dihedral" && points.length === 4) return { evaluation: measureDihedral(indices as [number, number, number, number], [points[0], points[1], points[2], points[3]]), refs: selection.selectedSites };
      return { evaluation: null, refs: Object.freeze([]) };
    }
    const fractionalBySite = new Map(mapping.scene.atoms.flatMap((atom) => atom.fractionalPosition ? [[atom.siteIndex, atom.fractionalPosition] as const] : []));
    if (selection.mode === "distance" && selection.selectedSites.length === 2) {
      const source = selection.selectedSites[0]; const target = selection.selectedSites[1];
      const sourceFrac = fractionalBySite.get(source.siteIndex); const targetFrac = fractionalBySite.get(target.siteIndex);
      if (!sourceFrac || !targetFrac) return { evaluation: { ok: false, error: "INVALID_COORDINATE" }, refs: Object.freeze([]) };
      const resolved = minimumImage(addOffset(sourceFrac, source.imageOffset), targetFrac, mapping.scene.lattice.matrix);
      if (!resolved.ok) return { evaluation: { ok: false, error: "INVALID_COORDINATE" }, refs: Object.freeze([]) };
      const targetRef = Object.freeze({ siteIndex: target.siteIndex, imageOffset: resolved.result.imageOffset });
      return { evaluation: measureDistance(indices as [number,number], [[0,0,0], resolved.result.displacementCartesian]), refs: Object.freeze([source,targetRef]) };
    }
    if (selection.mode === "angle" && selection.selectedSites.length === 3) {
      const resolved = periodicAngle(selection.selectedSites[1], indices[0], indices[2], fractionalBySite, mapping.scene.lattice.matrix);
      if (!resolved.ok) return { evaluation: { ok: false, error: "DEGENERATE_MEASUREMENT" }, refs: Object.freeze([]) };
      return { evaluation: { ok: true, result: Object.freeze({ kind:"angle", siteIndices: indices as [number,number,number], value: resolved.value, unit:"degree" }) }, refs: resolved.refs };
    }
    if (selection.mode === "dihedral" && selection.selectedSites.length === 4) {
      const resolved = periodicDihedral(selection.selectedSites[1], indices[0], indices[2], indices[3], fractionalBySite, mapping.scene.lattice.matrix);
      if (!resolved.ok) return { evaluation: { ok: false, error: "DEGENERATE_MEASUREMENT" }, refs: Object.freeze([]) };
      return { evaluation: { ok: true, result: Object.freeze({ kind:"dihedral", siteIndices: indices as [number,number,number,number], value: resolved.value, unit:"degree" }) }, refs: resolved.refs };
    }
    return { evaluation: null, refs: Object.freeze([]) };
  }, [coordinateMode, mapping, renderScene, selection]);
  const measurement = measurementDetails.evaluation;

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
  const applySupercell = () => {
    if (!mapping.ok) return;
    const checked = derivePeriodicSupercell(mapping.scene, repeatDraft, neighborSiteIndex);
    if (!checked.ok) {
      setSupercellError(`${checked.error}: requested ${checked.requestedSites} sites and ${checked.requestedBonds} bonds; limits are ${PERIODIC_DERIVED_CAPS.maxDisplayedSites} and ${PERIODIC_DERIVED_CAPS.maxDisplayedBonds}.`);
      return;
    }
    setSupercellError(null); setRepeat(repeatDraft); setNeighborSiteIndex(null); clearSelection(); setHistory([]);
  };
  const resetSupercell = () => { setRepeatDraft(DEFAULT_REPEAT); setRepeat(DEFAULT_REPEAT); setNeighborSiteIndex(null); setSupercellError(null); clearSelection(); setHistory([]); };
  const exportPng = async () => {
    setExportError(null);
    try {
      const blob = await engineRef.current?.exportPng();
      if (!blob) throw new Error("VIEWER_EXPORT_RENDERER_UNAVAILABLE");
      const base = sanitizeViewerFilename(mapping.ok ? mapping.scene.formula : "structure").replace(/\.png$/i, "");
      downloadLocalBlob(blob, `${base}-${repeat.join("x")}.png`);
    } catch {
      setExportError("Current-view PNG export failed. Scene JSON remains available.");
    }
  };
  const selectedAtom = renderScene && selection.activeSite ? renderScene.atoms.find((atom) => periodicSiteKey(atom.ref) === periodicSiteKey(selection.activeSite!)) ?? null : null;

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
      {mapping.ok && state === "scene_over_renderer_cap" ? (
        <div className="viewer-renderer-fallback" data-testid="viewer-scene-renderer-performance-refused">
          <strong>Scene exceeds the interactive renderer budget</strong>
          <p>No graphics context was created. Scene JSON remains available.</p>
          <code>{performanceDecision?.reason}</code>
        </div>
      ) : null}
      {mapping.ok && (state === "renderer_failed" || state === "chunk_load_failed" || state === "context_lost") ? (
        <div className="viewer-renderer-fallback" data-testid="viewer-scene-renderer-fallback">
          <strong>{state === "context_lost" ? "Graphics context lost" : state === "chunk_load_failed" ? "Renderer module unavailable" : "Renderer initialization failed"}</strong>
          <p>The artifact remains available as validated JSON. No artifact content was executed.</p>
          {state === "chunk_load_failed" || state === "context_lost" ? <button type="button" className="compact secondary" onClick={retry}>Retry renderer</button> : null}
        </div>
      ) : null}
      {mapping.ok && state === "initializing_renderer" ? <p className="viewer-renderer-loading">Initializing local renderer...</p> : null}
      {mapping.ok && !["unsupported", "renderer_failed", "chunk_load_failed", "context_lost", "scene_over_renderer_cap"].includes(state) ? (
        <div ref={containerRef} className="viewer-renderer-canvas-host" data-testid="viewer-scene-renderer-valid">
          <span className="sr-only">Interactive canvas showing {mapping.scene.atoms.length} sites, {new Set(mapping.scene.atoms.map((atom) => atom.species)).size} species, and {mapping.scene.bonds.length} bounded bonds.</span>
        </div>
      ) : null}
      {mapping.ok ? (
        <>
        {performanceDecision?.warning ? <p className="notice" role="status" data-testid="viewer-scene-renderer-performance-warning">{performanceDecision.warning}: all validated atoms and bonds remain rendered with reduced pixel ratio and antialiasing.</p> : null}
        <fieldset className="viewer-supercell-controls" aria-label="Bounded supercell controls">
          <legend>Renderer-local supercell</legend>
          {([0,1,2] as const).map((axis) => <label key={axis}>{["X","Y","Z"][axis]}<input data-testid={`viewer-supercell-${["x","y","z"][axis]}`} type="number" min="1" max="3" value={repeatDraft[axis]} onChange={(event) => { const next=[...repeatDraft] as number[]; next[axis]=Number(event.target.value); setRepeatDraft(next as unknown as SupercellRepeat); }} /></label>)}
          <button type="button" className="compact secondary" data-testid="viewer-supercell-apply" onClick={applySupercell}>Apply</button>
          <button type="button" className="compact secondary" data-testid="viewer-supercell-reset" onClick={resetSupercell}>Reset 1 x 1 x 1</button>
          <output data-testid="viewer-supercell-status">{supercellError ?? `${repeat.join(" x ")}: ${renderScene?.atoms.length ?? 0} displayed sites`}</output>
        </fieldset>
        <ViewerMeasurementPanel mode={selection.mode} selected={selection.selectedSites} coordinateMode={coordinateMode} resolvedRefs={measurementDetails.refs} evaluation={measurement} history={history} onMode={changeMode} onCoordinateMode={(mode) => { setCoordinateMode(mode); clearSelection(); }} onClear={clearSelection} />
        <ViewerSiteInspector atom={selectedAtom} bonds={renderScene?.bonds ?? []} repeat={repeat} source={mapping.scene.source.filename || mapping.scene.source.resourceId} onClear={clearSelection} onJumpPrimary={() => selectedAtom && setSelection((current) => selectViewerSite(initialViewerSelection(current.mode), {siteIndex:selectedAtom.siteIndex,imageOffset:[0,0,0]}))} onShowNeighbors={() => selectedAtom && setNeighborSiteIndex(selectedAtom.siteIndex)} onClearNeighbors={() => setNeighborSiteIndex(null)} onHighlightNeighbor={(target)=>{if(!selectedAtom)return;engineRef.current?.setSelection([selectedAtom.ref,target]);if(engineRef.current)setSnapshot(engineRef.current.snapshot());}} />
        <div className="viewer-artifact-downloads" aria-label="Viewer artifact downloads">
          <button type="button" className="compact secondary" onClick={() => downloadLocalBlob(jsonBlob(payload), "viewer_scene.json")}>Download scene JSON</button>
          {downloads?.manifest ? <button type="button" className="compact secondary" onClick={() => downloadLocalBlob(jsonBlob(downloads.manifest), "viewer_scene_manifest.json")}>Download manifest</button> : null}
          {downloads?.summary ? <button type="button" className="compact secondary" onClick={() => downloadLocalBlob(new Blob([downloads.summary ?? ""], { type: "text/markdown" }), "summary.md")}>Download summary</button> : null}
          {downloads?.recipe ? <button type="button" className="compact secondary" onClick={() => downloadLocalBlob(jsonBlob(downloads.recipe), "recipe.json")}>Download recipe</button> : null}
        </div>
        {exportError ? <p className="notice" role="alert" data-testid="viewer-scene-export-error">{exportError}</p> : null}
        <p className="viewer-renderer-scene-summary" data-testid="viewer-scene-renderer-summary">
          Validated canonical scene: {mapping.scene.atoms.length} sites; current renderer-local view: {renderScene?.atoms.length ?? 0} sites, {new Set(mapping.scene.atoms.map((atom) => atom.species)).size} species, {renderScene?.bonds.length ?? 0} bounded same-cell bonds.
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
        <output className="sr-only" data-testid="viewer-scene-renderer-performance-tier">{performanceDecision?.tier ?? "unavailable"}</output>
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

function addOffset(value: RenderVector3, offset: ImageOffset): RenderVector3 {
  return Object.freeze([value[0] + offset[0], value[1] + offset[1], value[2] + offset[2]]);
}
