"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { ViewerMeasurementPanel, type PeriodicMeasurementMode } from "./ViewerMeasurementPanel";
import { ViewerBondInspector } from "./ViewerBondInspector";
import { ViewerSiteInspector } from "./ViewerSiteInspector";
import { ViewerSupercellControls } from "./ViewerSupercellControls";
import { ViewerViewControls } from "./ViewerViewControls";
import { ViewerExportPanel } from "./ViewerExportPanel";
import { buildViewerExportManifest, buildViewerExportMarkdown, buildViewerExportState, DEFAULT_VIEWER_EXPORT_REQUEST, downloadLocalBlob, jsonBlob, markdownBlob, sanitizeViewerFilename, validateViewerExportRequest, type ViewerExportRequest } from "./viewerSceneExport";
import { measureAngle, measureDihedral, measureDistance, type ViewerMeasurementEvaluation, type ViewerMeasurementResult } from "./viewerSceneMeasurements";
import { buildViewerMeasurementArtifact } from "./viewerSceneMeasurementArtifact";
import { minimumImage, periodicAngle, periodicDihedral, periodicSiteKey } from "./viewerScenePeriodicGeometry";
import { classifyViewerPerformance } from "./viewerScenePerformance";
import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import { ViewerRendererError } from "./viewerSceneRendererErrors";
import type { ImageOffset, PeriodicSiteRef, RenderVector3, ViewerRendererEngine, ViewerRendererEngineFactory, ViewerRendererSnapshot, ViewerRendererState } from "./viewerSceneRendererTypes";
import { changeViewerSelectionMode, initialViewerSelection, selectViewerBondEndpoints, selectViewerSite, undoViewerSelection, type ViewerSelectionMode } from "./viewerSceneSelection";
import { derivePeriodicSupercell, estimatePeriodicSupercell, type SupercellRepeat } from "./viewerSceneSupercell";
import { buildViewerSupercellState } from "./viewerSceneSupercellState";
import { buildViewerViewState, initialViewerClipState, sceneClipBounds, VIEWER_CLIP_AXES, type CameraPreset, type ViewerCellDisplayState, type ViewerClipAxis, type ViewerClipState } from "./viewerSceneViewState";

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
  const surfaceRef = useRef<HTMLElement>(null);
  const engineRef = useRef<ViewerRendererEngine | null>(null);
  const engineSceneRef = useRef<typeof renderScene>(null);
  const generationRef = useRef(0);
  const exportGenerationRef = useRef(0);
  const [state, setState] = useState<ViewerRendererState>(mapping.ok ? "ready" : "validation_failed");
  const [showCell, setShowCell] = useState(true);
  const [showBonds, setShowBonds] = useState(true);
  const [showSupercellBoundary, setShowSupercellBoundary] = useState(true);
  const [showLatticeAxes, setShowLatticeAxes] = useState(false);
  const [cameraPreset, setCameraPreset] = useState<CameraPreset>("default");
  const [clipState, setClipState] = useState<ViewerClipState>(() => mapping.ok ? initialViewerClipState(mapping.scene) : Object.freeze({ enabled:false, planes:Object.freeze(VIEWER_CLIP_AXES.map((axis)=>Object.freeze({axis,position:0,enabled:false}))) }));
  const [snapshot, setSnapshot] = useState<ViewerRendererSnapshot | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [selection, setSelection] = useState(initialViewerSelection());
  const [selectedBondId, setSelectedBondId] = useState<string | null>(null);
  const selectionRef = useRef(selection);
  const [history, setHistory] = useState<readonly ViewerMeasurementResult[]>([]);
  const [coordinateMode, setCoordinateMode] = useState<PeriodicMeasurementMode>("displayed_positions");
  const [repeat, setRepeat] = useState<SupercellRepeat>(DEFAULT_REPEAT);
  const [repeatDraft, setRepeatDraft] = useState<readonly string[]>(["1","1","1"]);
  const [neighborSiteIndex, setNeighborSiteIndex] = useState<number | null>(null);
  const [supercellError, setSupercellError] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  const [exportRequest,setExportRequest]=useState<ViewerExportRequest>(DEFAULT_VIEWER_EXPORT_REQUEST);
  const [exportBusy,setExportBusy]=useState(false);
  const [exportStatus,setExportStatus]=useState("No export prepared.");
  const [exportBundle,setExportBundle]=useState<Readonly<{png:Blob;json:Blob;markdown:Blob;manifest:Blob}>|null>(null);
  const [announcement, setAnnouncement] = useState("Viewer ready for a validated scene.");
  const renderedRepeat = payloadChanged ? DEFAULT_REPEAT : repeat;
  const renderedNeighborSiteIndex = payloadChanged ? null : neighborSiteIndex;
  const derivation = useMemo(() => mapping.ok ? derivePeriodicSupercell(mapping.scene, renderedRepeat, renderedNeighborSiteIndex) : null, [mapping, renderedNeighborSiteIndex, renderedRepeat]);
  const renderScene = derivation?.ok ? derivation.scene : mapping.ok ? mapping.scene : null;
  const renderSceneRef = useRef(renderScene);
  renderSceneRef.current = renderScene;
  const parsedRepeatDraft = useMemo(() => repeatDraft.map((value) => value === "" ? Number.NaN : Number(value)) as unknown as SupercellRepeat, [repeatDraft]);
  const supercellEstimate = useMemo(() => mapping.ok ? estimatePeriodicSupercell(mapping.scene, parsedRepeatDraft) : Object.freeze({ expansion: DEFAULT_REPEAT, totalCells:0, displayedAtoms:0, displayedBonds:0, mode:"refused" as const, warnings:Object.freeze([]), error:"VIEWER_SUPERCELL_SCENE_UNSUPPORTED" }), [mapping, parsedRepeatDraft]);
  const performanceDecision = useMemo(() => renderScene ? classifyViewerPerformance(renderScene) : null, [renderScene]);
  const clipBounds = useMemo(() => renderScene ? sceneClipBounds(renderScene) : Object.freeze({x:[-1,1] as const,y:[-1,1] as const,z:[-1,1] as const}), [renderScene]);
  const latticeLengths = useMemo(() => (mapping.ok ? mapping.scene.lattice.matrix.map((vector)=>Math.hypot(...vector)) : [0,0,0]) as [number,number,number], [mapping]);
  const onSitePick = useCallback((site: PeriodicSiteRef | null) => { setSelectedBondId(null); setSelection((current) => selectViewerSite(current, site)); }, []);
  const onBondPick = useCallback((bondId: string) => {
    const bond = renderSceneRef.current?.bonds.find((candidate) => candidate.id === bondId);
    if (!bond) return;
    setSelectedBondId(bond.id);
    setSelection((current) => selectViewerBondEndpoints(current, bond.fromRef, bond.toRef));
  }, []);
  const onViewChange = useCallback(() => {
    exportGenerationRef.current += 1;
    setExportBundle(null);
    setExportStatus("Viewer state changed; prepare a new export.");
  }, []);

  useEffect(() => { selectionRef.current = selection; }, [selection]);

  useEffect(() => {
    const active = selection.activeSite;
    setAnnouncement(active ? `Selected site ${active.siteIndex} at image offset ${active.imageOffset.join(", ")}.` : "Selection cleared.");
  }, [selection.activeSite]);

  useEffect(() => {
    if (previousPayloadRef.current === payload) return;
    previousPayloadRef.current = payload;
    setSelection(initialViewerSelection()); setSelectedBondId(null); setHistory([]); setCoordinateMode("displayed_positions");
    exportGenerationRef.current+=1;setExportBundle(null);setExportStatus("No export prepared.");setExportBusy(false);
    setRepeat(DEFAULT_REPEAT); setRepeatDraft(["1","1","1"]); setNeighborSiteIndex(null); setSupercellError(null); setShowCell(true); setShowSupercellBoundary(true); setShowLatticeAxes(false); setCameraPreset("default");
    if (mapping.ok) setClipState(initialViewerClipState(mapping.scene));
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
      onBondPick,
      onViewChange,
    }).then((engine) => {
      if (cancelled || generation !== generationRef.current) {
        engine.dispose();
        return;
      }
      engineRef.current = engine;
      engineSceneRef.current = renderScene;
      engine.setCellVisible(showCell);
      engine.setSupercellBoundaryVisible(showSupercellBoundary);
      engine.setLatticeAxesVisible(showLatticeAxes);
      engine.setBondsVisible(showBonds);
      engine.setClipState(clipState);
      engine.setSelection(selectionRef.current.selectedSites);
      engine.setBondSelection(selectedBondId);
      setSnapshot(engine.snapshot());
      setState("rendered");
      setAnnouncement(`Scene rendered with ${renderScene.atoms.length} displayed sites in ${performanceDecision.tier} mode.`);
    }).catch((error: unknown) => {
      if (!cancelled) setState(error instanceof ViewerRendererError && error.code === "VIEWER_RENDERER_CHUNK_LOAD_FAILED" ? "chunk_load_failed" : "renderer_failed");
    });
    return () => {
      cancelled = true;
      if (generation === generationRef.current) generationRef.current += 1;
      const engine = engineRef.current;
      engineRef.current = null;
      engineSceneRef.current = null;
      if (engine) {
        try { engine.dispose(); } catch { /* disposal is best-effort after the surface is detached */ }
      }
    };
  }, [attempt, capabilityOverride, engineFactory, mapping, onBondPick, onSitePick, onViewChange]);

  useEffect(() => {
    const engine=engineRef.current;
    if(!engine||!renderScene||!performanceDecision||performanceDecision.tier==="refused"||engineSceneRef.current===renderScene)return;
    engine.replaceScene(renderScene,performanceDecision.tier,performanceDecision.pixelRatioCap);
    engine.setCellVisible(showCell);engine.setSupercellBoundaryVisible(showSupercellBoundary);engine.setLatticeAxesVisible(showLatticeAxes);engine.setBondsVisible(showBonds);engine.setClipState(clipState);
    engineSceneRef.current=renderScene;setSnapshot(engine.snapshot());setState("rendered");
  },[performanceDecision,renderScene,showBonds,showCell,showSupercellBoundary,showLatticeAxes,clipState]);

  useEffect(() => {
    engineRef.current?.setSelection(selection.selectedSites);
    if (engineRef.current) setSnapshot(engineRef.current.snapshot());
  }, [selection.selectedSites]);

  useEffect(() => {
    engineRef.current?.setBondSelection(selectedBondId);
    if (engineRef.current) setSnapshot(engineRef.current.snapshot());
  }, [selectedBondId]);

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
    exportGenerationRef.current+=1;setExportBundle(null);
    if (kind === "cell") {
      setShowCell(visible);
      engineRef.current?.setCellVisible(visible);
    } else {
      setShowBonds(visible);
      engineRef.current?.setBondsVisible(visible);
    }
    if (engineRef.current) setSnapshot(engineRef.current.snapshot());
  };
  const invalidatePreparedExport = () => {
    onViewChange();
  };
  const applySupercellBoundaryVisibility = (visible: boolean) => {
    invalidatePreparedExport();
    setShowSupercellBoundary(visible);
    engineRef.current?.setSupercellBoundaryVisible(visible);
    if (engineRef.current) setSnapshot(engineRef.current.snapshot());
  };
  const applyViewDisplay = (kind: keyof ViewerCellDisplayState, visible: boolean) => {
    if (kind === "unitCell") applyVisibility("cell", visible);
    if (kind === "supercellBoundary") applySupercellBoundaryVisibility(visible);
    if (kind === "latticeAxes") { exportGenerationRef.current+=1;setExportBundle(null);setShowLatticeAxes(visible); engineRef.current?.setLatticeAxesVisible(visible); if (engineRef.current) setSnapshot(engineRef.current.snapshot()); }
    setAnnouncement(`${kind === "latticeAxes" ? "Lattice axes" : kind === "unitCell" ? "Unit cell" : "Supercell boundary"} ${visible ? "shown" : "hidden"}.`);
  };
  const updateClipState = (next: ViewerClipState) => { exportGenerationRef.current+=1;setExportBundle(null);setClipState(next); engineRef.current?.setClipState(next); if (engineRef.current) setSnapshot(engineRef.current.snapshot()); };
  const updateClipPlane = (axis: ViewerClipAxis, update: Readonly<{ enabled?: boolean; position?: number }>) => {
    const [min,max]=clipBounds[axis];
    if (update.position !== undefined && (!Number.isFinite(update.position) || update.position < min || update.position > max)) { setAnnouncement(`Invalid ${axis.toUpperCase()} clipping position.`); return; }
    const planes=clipState.planes.map((plane)=>plane.axis===axis?Object.freeze({...plane,...update}):plane);
    const next=Object.freeze({enabled:clipState.enabled,planes:Object.freeze(planes)}) as ViewerClipState;
    updateClipState(next);
    const active=next.enabled&&next.planes.find((plane)=>plane.axis===axis)?.enabled;
    setAnnouncement(active ? `Clipping enabled. ${axis.toUpperCase()} plane at ${next.planes.find((plane)=>plane.axis===axis)!.position.toFixed(3)} angstrom.` : `${axis.toUpperCase()} clipping plane disabled.`);
  };
  const applyCameraPreset = (preset: CameraPreset) => { exportGenerationRef.current+=1;setExportBundle(null);setCameraPreset(preset); engineRef.current?.setCameraPreset(preset); if(engineRef.current)setSnapshot(engineRef.current.snapshot()); setAnnouncement(`Camera preset: ${preset}.`); };
  const reset = () => {
    invalidatePreparedExport();
    setCameraPreset("default");
    engineRef.current?.resetCamera();
    if (engineRef.current) setSnapshot(engineRef.current.snapshot());
  };
  const retry = () => {
    setState("ready");
    setAttempt((value) => value + 1);
    queueMicrotask(() => surfaceRef.current?.focus());
  };
  const changeMode = (mode: ViewerSelectionMode) => { setSelectedBondId(null); setSelection((current) => changeViewerSelectionMode(current, mode)); };
  const clearSelection = () => { setSelection((current) => initialViewerSelection(current.mode)); setSelectedBondId(null); queueMicrotask(() => surfaceRef.current?.focus()); };
  const undoSelection = () => { setSelection(undoViewerSelection); setSelectedBondId(null); };
  const applySupercell = () => {
    if (!mapping.ok) return;
    if (supercellEstimate.mode === "refused") { setSupercellError(supercellEstimate.error); return; }
    const checked = derivePeriodicSupercell(mapping.scene, parsedRepeatDraft, neighborSiteIndex);
    if (!checked.ok) {
      setSupercellError(checked.error);
      return;
    }
    exportGenerationRef.current+=1;setExportBundle(null);setSupercellError(null); setRepeat(parsedRepeatDraft); setNeighborSiteIndex(null); clearSelection(); setHistory([]); setAnnouncement(`Supercell applied: ${parsedRepeatDraft.join(" by ")}, ${supercellEstimate.totalCells} cells, ${supercellEstimate.displayedAtoms} displayed atoms.`);
  };
  const resetSupercell = () => { exportGenerationRef.current+=1;setExportBundle(null);setRepeatDraft(["1","1","1"]); setRepeat(DEFAULT_REPEAT); setNeighborSiteIndex(null); setSupercellError(null); clearSelection(); setHistory([]); setAnnouncement("Supercell reset to 1 by 1 by 1."); };
  const downloadSupercellState = () => { if (!mapping.ok) return; const artifact=buildViewerSupercellState(mapping.scene,{expansion:repeat,originPolicy:"positive_octant",showPrimaryCell:showCell,showSupercellBoundary,showInternalGrid:false}); downloadLocalBlob(jsonBlob(artifact),"viewer_supercell_state.json"); };
  const downloadViewState = () => { if (!renderScene || !snapshot) return; const artifact=buildViewerViewState(renderScene,clipState,{unitCell:showCell,supercellBoundary:showSupercellBoundary,latticeAxes:showLatticeAxes},cameraPreset,snapshot); downloadLocalBlob(jsonBlob(artifact),"viewer_view_state.json"); };
  const prepareExport = async () => {
    if(exportBusy){setExportStatus("VIEWER_EXPORT_BUSY");return;}
    setExportError(null);
    const engine=engineRef.current;const scene=renderScene;const currentSnapshot=engine?.snapshot();const version=exportGenerationRef.current;
    try {
      if (!engine || !scene || !currentSnapshot) throw new Error("VIEWER_EXPORT_SCENE_UNAVAILABLE");
      setExportBusy(true);
      setExportStatus("Export started.");
      setAnnouncement("Export started.");
      const request=validateViewerExportRequest(exportRequest);const png=await engine.exportPng(request);
      if(version!==exportGenerationRef.current||renderSceneRef.current!==scene)throw new Error("VIEWER_EXPORT_STALE_SCENE");
      const refs=measurementDetails.refs.length?measurementDetails.refs:selection.selectedSites;const measurements=measurement?.ok&&request.includeMeasurements?[{result:measurement.result,refs}]:[];
      const inspectorSummary=selectedAtom?{siteIndex:selectedAtom.siteIndex,imageOffset:selectedAtom.ref.imageOffset,species:selectedAtom.species,displayedCartesian:selectedAtom.position}:undefined;
      const state=buildViewerExportState({scene,snapshot:currentSnapshot,request,clip:clipState,cameraPreset,showCell,showSupercellBoundary,showAxes:showLatticeAxes,showBonds,measurements,inspectorSummary});const json=jsonBlob(state);const markdown=markdownBlob(buildViewerExportMarkdown(scene,state));const manifestObject=await buildViewerExportManifest([{name:"viewer.png",mediaType:"image/png",blob:png},{name:"viewer_export_state.json",mediaType:"application/json",blob:json},{name:"viewer_export_summary.md",mediaType:"text/markdown",blob:markdown}]);
      if(version!==exportGenerationRef.current)throw new Error("VIEWER_EXPORT_STALE_SCENE");const manifest=jsonBlob(manifestObject);const bundle=Object.freeze({png,json,markdown,manifest});setExportBundle(bundle);
      const selected=request.format==="png"?png:request.format==="json"?json:markdown;const suffix=request.format==="png"?"structure-viewer.png":request.format==="json"?"viewer-export-state.json":"viewer-export-summary.md";const filename=sanitizeViewerFilename(scene.formula,suffix);downloadLocalBlob(selected,filename);setExportStatus(`Export completed: ${filename}.`);setAnnouncement(`Export completed: ${filename}.`);
    } catch(error) {
      const code=error instanceof Error&&/^VIEWER_EXPORT_/.test(error.message)?error.message:"VIEWER_EXPORT_FAILED";setExportError(`${code}. Existing scene artifacts remain available.`);setExportStatus(`Export failed: ${code}.`);setAnnouncement(`Export failed: ${code}.`);
    } finally {
      setExportBusy(false);
    }
  };
  const downloadPrepared=(kind:"png"|"json"|"markdown"|"manifest")=>{if(!exportBundle||!renderScene)return;const suffix=kind==="png"?"structure-viewer.png":kind==="json"?"viewer-export-state.json":kind==="markdown"?"viewer-export-summary.md":"viewer-export-manifest.json";downloadLocalBlob(exportBundle[kind],sanitizeViewerFilename(renderScene.formula,suffix));};
  const selectedAtom = renderScene && selection.activeSite ? renderScene.atoms.find((atom) => periodicSiteKey(atom.ref) === periodicSiteKey(selection.activeSite!)) ?? null : null;
  const selectedBond = renderScene?.bonds.find((bond) => bond.id === selectedBondId) ?? null;
  const downloadMeasurement = () => {
    if (!mapping.ok || !measurement?.ok) return;
    const refs = measurementDetails.refs.length ? measurementDetails.refs : selection.selectedSites;
    const artifact = buildViewerMeasurementArtifact(mapping.scene, coordinateMode, refs, measurement.result, repeat);
    downloadLocalBlob(jsonBlob(artifact), "viewer_measurement.json");
  };
  const topologySummary = useMemo(() => {
    const bonds = renderScene?.bonds ?? [];
    return {
      crossBoundary: bonds.filter((bond) => bond.fromRef.imageOffset.some((value, index) => value !== bond.toRef.imageOffset[index])).length,
      selfPeriodic: bonds.filter((bond) => bond.fromSiteIndex === bond.toSiteIndex && bond.fromRef.imageOffset.some((value, index) => value !== bond.toRef.imageOffset[index])).length,
    };
  }, [renderScene]);
  const onViewerKeyDown = (event: React.KeyboardEvent<HTMLElement>) => {
    if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement || event.target instanceof HTMLSelectElement) return;
    const key = event.key.toLowerCase();
    if (key === "escape") { event.preventDefault(); clearSelection(); return; }
    if (key === "backspace") { event.preventDefault(); undoSelection(); return; }
    if (key === "n" && renderScene?.atoms.length) {
      event.preventDefault();
      const selectedKeys = new Set(selection.selectedSites.map(periodicSiteKey));
      const next = renderScene.atoms.find((atom) => !selectedKeys.has(periodicSiteKey(atom.ref))) ?? renderScene.atoms[0];
      onSitePick(next.ref); return;
    }
    if (key === "b" && renderScene?.bonds.length) {
      event.preventDefault();
      const index = Math.max(0, renderScene.bonds.findIndex((bond) => bond.id === selectedBondId) + 1) % renderScene.bonds.length;
      onBondPick(renderScene.bonds[index].id); return;
    }
    if (key === "0" || key === "r") { event.preventDefault(); reset(); return; }
    const action = key === "+" || key === "=" ? "zoom_in" : key === "-" ? "zoom_out" : key.startsWith("arrow") ? `${event.shiftKey ? "pan" : "rotate"}_${key.replace("arrow", "")}` : null;
    if (!action || state !== "rendered") return;
    event.preventDefault();
    engineRef.current?.keyboardCamera(action as Parameters<ViewerRendererEngine["keyboardCamera"]>[0]);
  };

  return (
    <section ref={surfaceRef} className="viewer-renderer-surface" role="region" tabIndex={0} aria-label="3D Structure Viewer" aria-describedby="viewer-scene-keyboard-help viewer-scene-semantic-summary" aria-keyshortcuts="ArrowLeft ArrowRight ArrowUp ArrowDown Shift+ArrowLeft Shift+ArrowRight Shift+ArrowUp Shift+ArrowDown + - 0 R N B Backspace Escape" onKeyDown={onViewerKeyDown} data-testid="viewer-scene-renderer-surface">
      <p id="viewer-scene-keyboard-help" className="sr-only">Arrow keys rotate. Shift plus arrow keys pan. Plus and minus zoom. N selects the next atom. B selects the next bond. Backspace undoes a point. Zero or R resets the camera. Escape clears selection.</p>
      <p className="sr-only" aria-live="polite" aria-atomic="true" data-testid="viewer-scene-accessibility-announcement">{announcement}</p>
      <div className="viewer-renderer-toolbar">
        <div>
          <strong>3D Structure Viewer</strong>
          <span role="status" aria-live="polite" data-testid="viewer-scene-renderer-state">{state}</span>
        </div>
        <div className="viewer-renderer-controls" aria-label="Viewer controls">
          <button type="button" className="compact secondary" data-testid="viewer-scene-renderer-reset" onClick={reset} disabled={state !== "rendered"}>Reset camera</button>
          <button type="button" className={`compact ${showBonds ? "active" : "secondary"}`} data-testid="viewer-scene-renderer-toggle-bonds" aria-pressed={showBonds} onClick={() => applyVisibility("bonds", !showBonds)}>Bonds</button>
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
        <dl id="viewer-scene-semantic-summary" className="sr-only" data-testid="viewer-scene-semantic-summary">
          <div><dt>Formula</dt><dd>{mapping.scene.formula}</dd></div>
          <div><dt>Canonical sites</dt><dd>{mapping.scene.atoms.length}</dd></div>
          <div><dt>Species</dt><dd>{new Set(mapping.scene.atoms.map((atom) => atom.species)).size}</dd></div>
          <div><dt>Lattice</dt><dd>{mapping.scene.lattice.matrix.map((row) => `[${row.join(", ")}]`).join(" ")}</dd></div>
          <div><dt>Canonical bonds</dt><dd>{mapping.scene.bonds.length}</dd></div>
          <div><dt>Cross-boundary bonds</dt><dd>{topologySummary.crossBoundary}</dd></div>
          <div><dt>Self-periodic bonds</dt><dd>{topologySummary.selfPeriodic}</dd></div>
          <div><dt>Render mode</dt><dd>{performanceDecision?.tier ?? "unavailable"}</dd></div>
          <div><dt>Supercell expansion</dt><dd>{repeat.join(" by ")}</dd></div>
          <div><dt>Displayed sites</dt><dd>{renderScene?.atoms.length ?? 0}</dd></div>
          <div><dt>Displayed bonds</dt><dd>{renderScene?.bonds.length ?? 0}</dd></div>
          <div><dt>Selection</dt><dd>{selection.activeSite ? `${selection.activeSite.siteIndex}@[${selection.activeSite.imageOffset.join(",")}]` : "none"}</dd></div>
          <div><dt>Selected bond</dt><dd>{selectedBondId ?? "none"}</dd></div>
          <div><dt>Clipping</dt><dd>{clipState.enabled ? clipState.planes.filter((plane)=>plane.enabled).map((plane)=>`${plane.axis}=${plane.position.toFixed(3)}`).join(", ") || "enabled with no planes" : "disabled"}</dd></div>
          <div><dt>Camera preset</dt><dd>{cameraPreset}</dd></div>
          <div><dt>Lattice axes</dt><dd>{showLatticeAxes ? "shown" : "hidden"}</dd></div>
          <div><dt>Warnings</dt><dd>{mapping.scene.warnings.length ? mapping.scene.warnings.join(", ") : "none"}</dd></div>
        </dl>
        {performanceDecision?.warning ? <p className="notice" role="status" data-testid="viewer-scene-renderer-performance-warning">{performanceDecision.warning}: all validated atoms and bonds remain rendered with reduced pixel ratio and antialiasing.</p> : null}
        <ViewerSupercellControls draft={repeatDraft} applied={repeat} estimate={supercellError ? Object.freeze({...supercellEstimate,error:supercellError,mode:"refused" as const}) : supercellEstimate} onDraft={(axis,value)=>{const next=[...repeatDraft];next[axis]=value;setRepeatDraft(next);setSupercellError(null);}} onApply={applySupercell} onReset={resetSupercell} onPreset={(value)=>{setRepeatDraft(value.map(String));setSupercellError(null);}} onDownload={downloadSupercellState} />
        <ViewerViewControls clip={clipState} bounds={clipBounds} display={{unitCell:showCell,supercellBoundary:showSupercellBoundary,latticeAxes:showLatticeAxes}} preset={cameraPreset} latticeLengths={latticeLengths} onClipEnabled={(enabled)=>{const next=Object.freeze({...clipState,enabled});updateClipState(next);setAnnouncement(enabled?"Clipping enabled.":"Clipping disabled.");}} onPlaneEnabled={(axis,enabled)=>updateClipPlane(axis,{enabled})} onPosition={(axis,position)=>updateClipPlane(axis,{position})} onResetClip={()=>{const next=renderScene?initialViewerClipState(renderScene):clipState;updateClipState(next);setAnnouncement("Clipping reset.");}} onDisplay={applyViewDisplay} onPreset={applyCameraPreset} onDownload={downloadViewState} />
        <ViewerExportPanel request={exportRequest} busy={exportBusy||state!=="rendered"} status={exportStatus} bundleReady={Boolean(exportBundle)} onChange={(request)=>{setExportRequest(request);setExportBundle(null);setExportStatus("Export settings changed; prepare a new export.");}} onExport={()=>void prepareExport()} onDownload={downloadPrepared}/>
        <ViewerMeasurementPanel mode={selection.mode} selected={selection.selectedSites} coordinateMode={coordinateMode} resolvedRefs={measurementDetails.refs} evaluation={measurement} history={history} onMode={changeMode} onCoordinateMode={(mode) => { setCoordinateMode(mode); clearSelection(); }} onUndo={undoSelection} onClear={clearSelection} onDownload={downloadMeasurement} />
        <ViewerBondInspector bond={selectedBond} onClear={() => setSelectedBondId(null)} />
        <ViewerSiteInspector atom={selectedAtom} atoms={renderScene?.atoms ?? []} bonds={renderScene?.bonds ?? []} repeat={repeat} source={mapping.scene.source.filename || mapping.scene.source.resourceId} onClear={clearSelection} onJumpPrimary={() => selectedAtom && setSelection((current) => selectViewerSite(initialViewerSelection(current.mode), {siteIndex:selectedAtom.siteIndex,imageOffset:[0,0,0]}))} onShowNeighbors={() => selectedAtom && setNeighborSiteIndex(selectedAtom.siteIndex)} onClearNeighbors={() => setNeighborSiteIndex(null)} onHighlightNeighbor={(target)=>{if(!selectedAtom)return;engineRef.current?.setSelection([selectedAtom.ref,target]);if(engineRef.current)setSnapshot(engineRef.current.snapshot());}} />
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
