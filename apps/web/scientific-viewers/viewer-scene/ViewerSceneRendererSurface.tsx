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
import { supportsManagedWebGL } from "./viewerWebglCapability";
import { changeViewerSelectionMode, initialViewerSelection, selectViewerBondEndpoints, selectViewerSite, undoViewerSelection, type ViewerSelectionMode, type ViewerSelectionState } from "./viewerSceneSelection";
import { derivePeriodicSupercell, estimatePeriodicSupercell, type NeighborDisplay, type SupercellRepeat } from "./viewerSceneSupercell";
import { buildViewerSupercellState } from "./viewerSceneSupercellState";
import { buildViewerViewState, initialViewerClipState, sceneClipBounds, VIEWER_CLIP_AXES, type CameraPreset, type ViewerCellDisplayState, type ViewerClipAxis, type ViewerClipState } from "./viewerSceneViewState";

export type ViewerSceneRendererSurfaceProps = {
  readonly payload: unknown;
  readonly capabilityOverride?: boolean;
  readonly engineFactory?: ViewerRendererEngineFactory;
  readonly downloads?: Readonly<{ manifest?: unknown; summary?: string; recipe?: unknown }>;
  readonly externalSiteId?: string | null;
  readonly onSiteSelection?: (selection: Readonly<{ siteIndex: number; imageOffset: ImageOffset; siteId: string; species: string }> | null) => void;
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

function rendererStateLabel(state: ViewerRendererState) {
  const labels: Record<string, string> = {
    ready: "已准备",
    initializing_renderer: "正在加载",
    rendered: "已就绪",
    unsupported: "暂不支持",
    scene_over_renderer_cap: "超出交互范围",
    renderer_failed: "加载失败",
    chunk_load_failed: "加载失败",
    context_lost: "渲染中断",
    validation_failed: "数据校验失败",
  };
  return labels[state] ?? state;
}

export function ViewerSceneRendererSurface({ payload, capabilityOverride, engineFactory = defaultEngineFactory, downloads, externalSiteId, onSiteSelection }: ViewerSceneRendererSurfaceProps) {
  const mapping = useMemo(() => mapViewerSceneForRenderer(payload), [payload]);
  const previousPayloadRef = useRef(payload);
  const payloadChanged = previousPayloadRef.current !== payload;
  const containerRef = useRef<HTMLDivElement>(null);
  const surfaceRef = useRef<HTMLElement>(null);
  const engineRef = useRef<ViewerRendererEngine | null>(null);
  const siteSelectionListenerRef = useRef(onSiteSelection);
  const engineSceneRef = useRef<typeof renderScene>(null);
  const generationRef = useRef(0);
  const exportGenerationRef = useRef(0);
  const exportOwnerRef = useRef<symbol | null>(null);
  const [state, setState] = useState<ViewerRendererState>(mapping.ok ? "ready" : "validation_failed");
  const [showCell, setShowCell] = useState(true);
  const [showBonds, setShowBonds] = useState(true);
  const [showSupercellBoundary, setShowSupercellBoundary] = useState(true);
  const [showLatticeAxes, setShowLatticeAxes] = useState(false);
  const [cameraPreset, setCameraPreset] = useState<CameraPreset>("default");
  const [clipState, setClipState] = useState<ViewerClipState>(() => mapping.ok ? initialViewerClipState(mapping.scene) : Object.freeze({ enabled:false, planes:Object.freeze(VIEWER_CLIP_AXES.map((axis)=>Object.freeze({axis,position:0,enabled:false}))) }));
  const [snapshot, setSnapshot] = useState<ViewerRendererSnapshot | null>(null);
  const [rendererError, setRendererError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [selection, setSelection] = useState(initialViewerSelection());
  const [selectionRestoreError, setSelectionRestoreError] = useState(false);
  const [selectedBondId, setSelectedBondId] = useState<string | null>(null);
  const selectionRef = useRef(selection);
  const [history, setHistory] = useState<readonly ViewerMeasurementResult[]>([]);
  const [coordinateMode, setCoordinateMode] = useState<PeriodicMeasurementMode>("displayed_positions");
  const [repeat, setRepeat] = useState<SupercellRepeat>(DEFAULT_REPEAT);
  const [repeatDraft, setRepeatDraft] = useState<readonly string[]>(["1","1","1"]);
  const [neighborDisplay, setNeighborDisplay] = useState<NeighborDisplay | null>(null);
  const [neighborError, setNeighborError] = useState<string | null>(null);
  const [supercellError, setSupercellError] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  const [exportRequest,setExportRequest]=useState<ViewerExportRequest>(DEFAULT_VIEWER_EXPORT_REQUEST);
  const [exportBusy,setExportBusy]=useState(false);
  const [exportStatus,setExportStatus]=useState("尚未准备导出。");
  const [exportBundle,setExportBundle]=useState<Readonly<{png:Blob;json:Blob;markdown:Blob;manifest:Blob}>|null>(null);
  const [announcement, setAnnouncement] = useState("已加载通过校验的结构场景。");
  const renderedRepeat = payloadChanged ? DEFAULT_REPEAT : repeat;
  const renderedNeighborDisplay = payloadChanged ? null : neighborDisplay;
  const derivation = useMemo(() => mapping.ok ? derivePeriodicSupercell(mapping.scene, renderedRepeat, renderedNeighborDisplay) : null, [mapping, renderedNeighborDisplay, renderedRepeat]);
  const renderScene = derivation?.ok ? derivation.scene : mapping.ok ? mapping.scene : null;
  const renderSceneRef = useRef(renderScene);
  renderSceneRef.current = renderScene;
  const parsedRepeatDraft = useMemo(() => repeatDraft.map((value) => value === "" ? Number.NaN : Number(value)) as unknown as SupercellRepeat, [repeatDraft]);
  const supercellEstimate = useMemo(() => mapping.ok ? estimatePeriodicSupercell(mapping.scene, parsedRepeatDraft) : Object.freeze({ expansion: DEFAULT_REPEAT, totalCells:0, displayedAtoms:0, displayedBonds:0, mode:"refused" as const, warnings:Object.freeze([]), error:"VIEWER_SUPERCELL_SCENE_UNSUPPORTED" }), [mapping, parsedRepeatDraft]);
  const performanceDecision = useMemo(() => renderScene ? classifyViewerPerformance(renderScene) : null, [renderScene]);
  const truncationWarning = useMemo(
    () => mapping.ok
      ? mapping.scene.warnings.find((warning) => warning.includes("当前显示前"))
        ?? mapping.scene.warnings.find((warning) => warning.startsWith("VIEWER_SCENE_SITES_TRUNCATED"))
      : undefined,
    [mapping],
  );
  const clipBounds = useMemo(() => renderScene ? sceneClipBounds(renderScene) : Object.freeze({x:[-1,1] as const,y:[-1,1] as const,z:[-1,1] as const}), [renderScene]);
  const latticeLengths = useMemo(() => (mapping.ok ? mapping.scene.lattice.matrix.map((vector)=>Math.hypot(...vector)) : [0,0,0]) as [number,number,number], [mapping]);
  const commitSelection = useCallback((next: ViewerSelectionState, notify = true) => {
    selectionRef.current = next;
    setSelection(next);
    if (!notify) return;
    setSelectionRestoreError(false);
    const site = next.activeSite;
    const atom = site ? renderSceneRef.current?.atoms.find((candidate) => periodicSiteKey(candidate.ref) === periodicSiteKey(site)) : null;
    siteSelectionListenerRef.current?.(atom ? Object.freeze({
      siteIndex: atom.siteIndex,
      imageOffset: atom.ref.imageOffset,
      siteId: `${atom.species}-${atom.siteIndex}:${atom.ref.imageOffset.join(".")}`,
      species: atom.species,
    }) : null);
  }, []);
  const onSitePick = useCallback((site: PeriodicSiteRef | null) => {
    setSelectedBondId(null);
    commitSelection(selectViewerSite(selectionRef.current, site));
  }, [commitSelection]);
  const onBondPick = useCallback((bondId: string) => {
    const bond = renderSceneRef.current?.bonds.find((candidate) => candidate.id === bondId);
    if (!bond) return;
    setSelectedBondId(bond.id);
    commitSelection(selectViewerBondEndpoints(selectionRef.current, bond.fromRef, bond.toRef));
  }, [commitSelection]);
  const onViewChange = useCallback(() => {
    exportGenerationRef.current += 1;
    setExportBundle(null);
    setExportStatus("查看状态已变化，请重新准备导出。");
  }, []);

  useEffect(() => { selectionRef.current = selection; }, [selection]);
  useEffect(() => { siteSelectionListenerRef.current = onSiteSelection; }, [onSiteSelection]);
  useEffect(() => () => { exportOwnerRef.current = null; }, []);

  useEffect(() => {
    const active = selection.activeSite;
    setAnnouncement(active ? `已选择位点 ${active.siteIndex}，周期偏移 ${active.imageOffset.join(", ")}。` : "已清除选择。");
  }, [selection.activeSite]);

  useEffect(() => {
    if (previousPayloadRef.current === payload) return;
    previousPayloadRef.current = payload;
    commitSelection(initialViewerSelection(), false); setSelectedBondId(null); setHistory([]); setCoordinateMode("displayed_positions");
    exportOwnerRef.current=null;exportGenerationRef.current+=1;setExportBundle(null);setExportError(null);setExportStatus("尚未准备导出。");setExportBusy(false);
    setRepeat(DEFAULT_REPEAT); setRepeatDraft(["1","1","1"]); setNeighborDisplay(null); setNeighborError(null); setSupercellError(null); setShowCell(true); setShowSupercellBoundary(true); setShowLatticeAxes(false); setCameraPreset("default");
    if (mapping.ok) setClipState(initialViewerClipState(mapping.scene));
  }, [payload]);

  useEffect(() => {
    if (externalSiteId === undefined) return;
    setSelectionRestoreError(false);
    if (!externalSiteId) { commitSelection(initialViewerSelection(selectionRef.current.mode), false); setSelectedBondId(null); return; }
    if (!mapping.ok) return;
    const match = /^(.+)-(\d+):(-?\d+)\.(-?\d+)\.(-?\d+)$/.exec(externalSiteId);
    const source = match ? mapping.scene.atoms.find(atom => atom.siteIndex === Number(match[2]) && atom.species === match[1]) : null;
    const offset = match?.slice(3).map(Number) as ImageOffset | undefined;
    if (!source || !offset || !offset.every(value => Number.isSafeInteger(value) && Math.abs(value) <= 3)) { commitSelection(initialViewerSelection(), false); setSelectionRestoreError(true); return; }
    const target: PeriodicSiteRef = { siteIndex: source.siteIndex, imageOffset: offset };
    if (selectionRef.current.activeSite && periodicSiteKey(selectionRef.current.activeSite) === periodicSiteKey(target)) return;
    if (!renderSceneRef.current?.atoms.some(atom => periodicSiteKey(atom.ref) === periodicSiteKey(target))) {
      const neighboring = offset.some(value => value < 0);
      const neighborConnections = Boolean(mapping.scene.connectivity);
      const nextRepeat: SupercellRepeat = neighborConnections || neighboring ? [1, 1, 1] : [offset[0] + 1, offset[1] + 1, offset[2] + 1];
      const nextNeighbors: NeighborDisplay | null = neighborConnections ? { mode: "image", center: target } : neighboring ? source.siteIndex : null;
      const restored = (neighborConnections || !neighboring || offset.every(value => value >= -1 && value <= 1)) ? derivePeriodicSupercell(mapping.scene, nextRepeat, nextNeighbors) : null;
      if (!restored?.ok || !restored.scene.atoms.some(atom => periodicSiteKey(atom.ref) === periodicSiteKey(target))) { commitSelection(initialViewerSelection(), false); setSelectionRestoreError(true); return; }
      setRepeat(nextRepeat); setRepeatDraft(nextRepeat.map(String)); setNeighborDisplay(nextNeighbors);
    }
    commitSelection(selectViewerSite(initialViewerSelection(), target), false);
    setSelectedBondId(null);
  }, [externalSiteId, payload, mapping, commitSelection]);

  useEffect(() => {
    setState(mapping.ok ? "ready" : "validation_failed");
    setSnapshot(null);
    setRendererError(null);
    if (!mapping.ok || !renderScene || !performanceDecision) return;
    if (performanceDecision.tier === "refused") {
      setState("scene_over_renderer_cap");
      return;
    }
    const supported = capabilityOverride ?? supportsManagedWebGL();
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
      // A restored periodic copy can expand the scene while the renderer loads.
      // Apply that current scene before publishing a rendered state.
      const currentScene = renderSceneRef.current ?? renderScene;
      if (currentScene !== renderScene) {
        const currentPerformance = classifyViewerPerformance(currentScene);
        if (currentPerformance.tier === "refused") { engine.dispose(); engineRef.current = null; setState("scene_over_renderer_cap"); return; }
        engine.replaceScene(currentScene, currentPerformance.tier, currentPerformance.pixelRatioCap);
      }
      engineSceneRef.current = currentScene;
      engine.setCellVisible(showCell);
      engine.setSupercellBoundaryVisible(showSupercellBoundary);
      engine.setLatticeAxesVisible(showLatticeAxes);
      engine.setBondsVisible(showBonds);
      engine.setClipState(clipState);
      engine.setSelection(selectionRef.current.selectedSites);
      engine.setBondSelection(selectedBondId);
      setSnapshot(engine.snapshot());
      setState("rendered");
      setAnnouncement(`结构场景已渲染，共 ${currentScene.atoms.length} 个显示位点。`);
    }).catch((error: unknown) => {
      if (!cancelled) {
        const code = error instanceof ViewerRendererError ? error.code : "VIEWER_RENDERER_INITIALIZATION_FAILED";
        setRendererError(code);
        setState(code === "VIEWER_RENDERER_CHUNK_LOAD_FAILED" ? "chunk_load_failed" : "renderer_failed");
      }
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
    engine.setSelection(selectionRef.current.selectedSites);
    engine.setBondSelection(selectedBondId);
    engineSceneRef.current=renderScene;setSnapshot(engine.snapshot());setState("rendered");
  },[performanceDecision,renderScene,showBonds,showCell,showSupercellBoundary,showLatticeAxes,clipState,selectedBondId]);

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
    setAnnouncement(`${kind === "latticeAxes" ? "晶格轴" : kind === "unitCell" ? "晶胞边界" : "超晶胞边界"}${visible ? "已显示" : "已隐藏"}。`);
  };
  const updateClipState = (next: ViewerClipState) => { exportGenerationRef.current+=1;setExportBundle(null);setClipState(next); engineRef.current?.setClipState(next); if (engineRef.current) setSnapshot(engineRef.current.snapshot()); };
  const updateClipPlane = (axis: ViewerClipAxis, update: Readonly<{ enabled?: boolean; position?: number }>) => {
    const [min,max]=clipBounds[axis];
    if (update.position !== undefined && (!Number.isFinite(update.position) || update.position < min || update.position > max)) { setAnnouncement(`${axis.toUpperCase()} 裁剪位置无效。`); return; }
    const planes=clipState.planes.map((plane)=>plane.axis===axis?Object.freeze({...plane,...update}):plane);
    const next=Object.freeze({enabled:clipState.enabled,planes:Object.freeze(planes)}) as ViewerClipState;
    updateClipState(next);
    const active=next.enabled&&next.planes.find((plane)=>plane.axis===axis)?.enabled;
    setAnnouncement(active ? `已启用裁剪，${axis.toUpperCase()} 平面位置为 ${next.planes.find((plane)=>plane.axis===axis)!.position.toFixed(3)} Å。` : `已停用 ${axis.toUpperCase()} 裁剪平面。`);
  };
  const applyCameraPreset = (preset: CameraPreset) => { exportGenerationRef.current+=1;setExportBundle(null);setCameraPreset(preset); engineRef.current?.setCameraPreset(preset); if(engineRef.current)setSnapshot(engineRef.current.snapshot()); setAnnouncement(`相机视角已切换为 ${preset}。`); };
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
  const changeMode = (mode: ViewerSelectionMode) => { setSelectedBondId(null); commitSelection(changeViewerSelectionMode(selectionRef.current, mode)); };
  const clearSelection = () => { commitSelection(initialViewerSelection(selectionRef.current.mode)); setSelectedBondId(null); queueMicrotask(() => surfaceRef.current?.focus()); };
  const undoSelection = () => { commitSelection(undoViewerSelection(selectionRef.current)); setSelectedBondId(null); };
  const updateNeighborDisplay = (next: NeighborDisplay | null) => {
    if (!mapping.ok) return;
    const checked = derivePeriodicSupercell(mapping.scene, repeat, next);
    if (!checked.ok) {
      setNeighborError(checked.error === "PERIODIC_NEIGHBOR_IMAGE_LIMIT_EXCEEDED" ? "此邻域超出周期显示范围，请先返回主位点。" : "当前近邻超出显示上限，请减小超晶胞后重试。");
      return;
    }
    invalidatePreparedExport();
    setNeighborError(null);
    setNeighborDisplay(next);
    const active = selectionRef.current.activeSite;
    if (next === null && active && !checked.scene.atoms.some(atom => periodicSiteKey(atom.ref) === periodicSiteKey(active))) clearSelection();
    setAnnouncement(next === null ? "已隐藏额外周期副本。" : "已显示所选位点的周期邻域。");
  };
  const applySupercell = () => {
    if (!mapping.ok) return;
    if (supercellEstimate.mode === "refused") { setSupercellError(supercellEstimate.error); return; }
    const checked = derivePeriodicSupercell(mapping.scene, parsedRepeatDraft);
    if (!checked.ok) {
      setSupercellError(checked.error);
      return;
    }
    exportGenerationRef.current+=1;setExportBundle(null);setSupercellError(null); setRepeat(parsedRepeatDraft); setNeighborDisplay(null); clearSelection(); setHistory([]); setAnnouncement(`已应用 ${parsedRepeatDraft.join(" × ")} 超晶胞，共 ${supercellEstimate.totalCells} 个晶胞、显示 ${supercellEstimate.displayedAtoms} 个原子。`);
  };
  const resetSupercell = () => { exportGenerationRef.current+=1;setExportBundle(null);setRepeatDraft(["1","1","1"]); setRepeat(DEFAULT_REPEAT); setNeighborDisplay(null); setSupercellError(null); clearSelection(); setHistory([]); setAnnouncement("超晶胞已重置为 1 × 1 × 1。"); };
  const downloadSupercellState = () => { if (!mapping.ok) return; const artifact=buildViewerSupercellState(mapping.scene,{expansion:repeat,originPolicy:"positive_octant",showPrimaryCell:showCell,showSupercellBoundary,showInternalGrid:false}); downloadLocalBlob(jsonBlob(artifact),"viewer_supercell_state.json"); };
  const downloadViewState = () => { if (!renderScene || !snapshot) return; const artifact=buildViewerViewState(renderScene,clipState,{unitCell:showCell,supercellBoundary:showSupercellBoundary,latticeAxes:showLatticeAxes},cameraPreset,snapshot); downloadLocalBlob(jsonBlob(artifact),"viewer_view_state.json"); };
  const prepareExport = async () => {
    if(exportOwnerRef.current){return;}
    const owner=Symbol();exportOwnerRef.current=owner;
    setExportError(null);
    const engine=engineRef.current;const scene=renderScene;const currentSnapshot=engine?.snapshot();const version=exportGenerationRef.current;
    const ownsExport=()=>exportOwnerRef.current===owner&&renderSceneRef.current===scene;
    try {
      if (!engine || !scene || !currentSnapshot) throw new Error("VIEWER_EXPORT_SCENE_UNAVAILABLE");
      setExportBusy(true);
      setExportStatus("正在准备导出。");
      setAnnouncement("正在准备导出。");
      const request=validateViewerExportRequest(exportRequest);const png=await engine.exportPng(request);
      if(!ownsExport())return;
      if(version!==exportGenerationRef.current||renderSceneRef.current!==scene)throw new Error("VIEWER_EXPORT_STALE_SCENE");
      const refs=measurementDetails.refs.length?measurementDetails.refs:selection.selectedSites;const measurements=measurement?.ok&&request.includeMeasurements?[{result:measurement.result,refs}]:[];
      const inspectorSummary=selectedAtom?{siteIndex:selectedAtom.siteIndex,imageOffset:selectedAtom.ref.imageOffset,species:selectedAtom.species,displayedCartesian:selectedAtom.position}:undefined;
      const state=buildViewerExportState({scene,snapshot:currentSnapshot,request,clip:clipState,cameraPreset,showCell,showSupercellBoundary,showAxes:showLatticeAxes,showBonds,measurements,inspectorSummary});const json=jsonBlob(state);const markdown=markdownBlob(buildViewerExportMarkdown(scene,state));const manifestObject=await buildViewerExportManifest([{name:"viewer.png",mediaType:"image/png",blob:png},{name:"viewer_export_state.json",mediaType:"application/json",blob:json},{name:"viewer_export_summary.md",mediaType:"text/markdown",blob:markdown}]);
      if(!ownsExport())return;
      if(version!==exportGenerationRef.current)throw new Error("VIEWER_EXPORT_STALE_SCENE");const manifest=jsonBlob(manifestObject);const bundle=Object.freeze({png,json,markdown,manifest});setExportBundle(bundle);
      const selected=request.format==="png"?png:request.format==="json"?json:markdown;const suffix=request.format==="png"?"structure-viewer.png":request.format==="json"?"viewer-export-state.json":"viewer-export-summary.md";const filename=sanitizeViewerFilename(scene.formula,suffix);downloadLocalBlob(selected,filename);setExportStatus(`导出完成：${filename}。`);setAnnouncement(`导出完成：${filename}。`);
    } catch(error) {
      if(!ownsExport())return;
      const code=error instanceof Error&&/^VIEWER_EXPORT_/.test(error.message)?error.message:"VIEWER_EXPORT_FAILED";setExportError(code);setExportStatus("导出失败，当前结构仍可继续查看。");setAnnouncement("导出失败，当前结构仍可继续查看。");
    } finally {
      if(exportOwnerRef.current===owner){exportOwnerRef.current=null;setExportBusy(false);}
    }
  };
  const downloadPrepared=(kind:"png"|"json"|"markdown"|"manifest")=>{if(!exportBundle||!renderScene)return;const suffix=kind==="png"?"structure-viewer.png":kind==="json"?"viewer-export-state.json":kind==="markdown"?"viewer-export-summary.md":"viewer-export-manifest.json";downloadLocalBlob(exportBundle[kind],sanitizeViewerFilename(renderScene.formula,suffix));};
  const selectedAtom = renderScene && selection.activeSite ? renderScene.atoms.find((atom) => periodicSiteKey(atom.ref) === periodicSiteKey(selection.activeSite!)) ?? null : null;
  const selectedBond = renderScene?.bonds.find((bond) => bond.id === selectedBondId) ?? null;
  const extraImageCount = renderScene?.atoms.filter(atom => atom.ref.imageOffset.some((value, axis) => value < 0 || value >= repeat[axis])).length ?? 0;
  const downloadMeasurement = () => {
    if (!mapping.ok || !measurement?.ok) return;
    const refs = measurementDetails.refs.length ? measurementDetails.refs : selection.selectedSites;
    const artifact = buildViewerMeasurementArtifact(mapping.scene, coordinateMode, refs, measurement.result, repeat);
    downloadLocalBlob(jsonBlob(artifact), "viewer_measurement.json");
  };
  const topologySummary = useMemo(() => {
    const bonds = mapping.ok ? mapping.scene.bonds : [];
    return {
      crossBoundary: bonds.filter((bond) => bond.fromRef.imageOffset.some((value, index) => value !== bond.toRef.imageOffset[index])).length,
      selfPeriodic: bonds.filter((bond) => bond.fromSiteIndex === bond.toSiteIndex && bond.fromRef.imageOffset.some((value, index) => value !== bond.toRef.imageOffset[index])).length,
    };
  }, [mapping]);
  const onViewerKeyDown = (event: React.KeyboardEvent<HTMLElement>) => {
    if (event.target !== event.currentTarget && !(event.target instanceof HTMLCanvasElement)) return;
    const key = event.key.toLowerCase();
    if (key === "escape") { event.preventDefault(); clearSelection(); return; }
    if (key === "backspace") { event.preventDefault(); undoSelection(); return; }
    if (key === "n" && renderScene?.atoms.length) {
      event.preventDefault();
      const selectedKeys = new Set(selection.selectedSites.map(periodicSiteKey));
      const activeIndex = selection.activeSite ? renderScene.atoms.findIndex(atom => periodicSiteKey(atom.ref) === periodicSiteKey(selection.activeSite!)) : -1;
      const next = Array.from({ length: renderScene.atoms.length }, (_, step) => renderScene.atoms[(activeIndex + step + 1) % renderScene.atoms.length])
        .find(atom => !selectedKeys.has(periodicSiteKey(atom.ref)));
      if (next) onSitePick(next.ref);
      return;
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
    <section ref={surfaceRef} className="viewer-renderer-surface" role="region" tabIndex={0} aria-label="三维结构查看器" aria-describedby="viewer-scene-keyboard-help viewer-scene-semantic-summary" aria-keyshortcuts="ArrowLeft ArrowRight ArrowUp ArrowDown Shift+ArrowLeft Shift+ArrowRight Shift+ArrowUp Shift+ArrowDown + - 0 R N B Backspace Escape" onKeyDown={onViewerKeyDown} data-testid="viewer-scene-renderer-surface">
      <p id="viewer-scene-keyboard-help" className="sr-only">方向键旋转，Shift 加方向键平移，加号和减号缩放。N 选择下一个原子，B 选择下一条{mapping.ok && mapping.scene.connectivity ? "连接" : "键"}，Backspace 撤销上一步，0 或 R 重置相机，Escape 清除选择。</p>
      <p className="sr-only" aria-live="polite" aria-atomic="true" data-testid="viewer-scene-accessibility-announcement">{announcement}</p>
      {selectionRestoreError ? <p role="alert">链接中的位点当前无法显示，请重新选择。原始结构仍然保留。</p> : null}
      <div className="viewer-renderer-toolbar">
        <div>
          <strong>{mapping.ok ? mapping.scene.formula.split(/(\d+)/u).map((part, index) => /^\d+$/u.test(part) ? <sub key={index}>{part}</sub> : part) : "三维结构"}</strong>
          <span className={state === "rendered" ? "sr-only" : undefined} role="status" aria-live="polite" data-testid="viewer-scene-renderer-state">{rendererStateLabel(state)}</span>
        </div>
        <div className="viewer-renderer-controls" aria-label="查看器控制">
          <button type="button" className="compact secondary" data-testid="viewer-scene-renderer-reset" onClick={reset} disabled={state !== "rendered"}>重置相机</button>
          <button type="button" className={`compact ${showBonds ? "active" : "secondary"}`} data-testid="viewer-scene-renderer-toggle-bonds" aria-pressed={showBonds}
            disabled={mapping.ok && mapping.scene.sourcePreview === true && mapping.scene.bonds.length === 0}
            title={mapping.ok && mapping.scene.connectivity ? mapping.scene.connectivity.method === "ideal_first_shell"
              ? "理想模型中已保存的最短周期近邻，不表示确定的化学键或键级。"
              : "按参考共价半径估算近邻，不代表已确定化学键或键级；判定条件可在技术详情中查看。" : undefined}
            onClick={() => applyVisibility("bonds", !showBonds)}>{mapping.ok && (mapping.scene.sourcePreview || mapping.scene.connectivity) ? "近邻连接" : "键合"}</button>
        </div>
      </div>

      {mapping.ok ? <div className="viewer-structure-overview">
        <p className="viewer-renderer-scene-summary" data-testid="viewer-scene-renderer-summary">
          {renderScene?.atoms.length ?? 0} 个位点 · {new Set(mapping.scene.atoms.map((atom) => atom.species)).size} 种元素{repeat.some(value => value > 1) ? ` · ${repeat.join(" × ")} 超晶胞` : ""}{extraImageCount ? ` · 含 ${extraImageCount} 个周期副本` : ""}
        </p>
        <ul className="viewer-renderer-species-legend" aria-label="元素图例">
          {[...new Map(mapping.scene.atoms.map((atom) => [atom.species, atom])).values()].map((atom) => <li key={atom.species}><span aria-hidden="true" style={{ backgroundColor: atom.color }} />{atom.species}</li>)}
        </ul>
      </div> : null}

      {!mapping.ok ? (
        <div className="viewer-renderer-fallback" data-testid="viewer-scene-renderer-invalid">
          <strong>场景校验失败</strong>
          <p role="status" aria-live="polite">当前结构数据无法进入三维查看器，源数据仍然保留；可继续查看下方有界摘要或下载已校验场景。</p>
          <details><summary>技术详情</summary><code>{mapping.validation.errors.join(", ")}</code></details>
        </div>
      ) : null}
      {mapping.ok && state === "unsupported" ? (
        <div className="viewer-renderer-fallback" data-testid="viewer-scene-renderer-unavailable">
          <strong>交互式渲染器不可用</strong>
          <p role="status" aria-live="polite">当前浏览器没有可用的图形环境；结构数据和来源记录仍然保留，可继续查看有界摘要或下载场景。</p>
        </div>
      ) : null}
      {mapping.ok && state === "scene_over_renderer_cap" ? (
        <div className="viewer-renderer-fallback" data-testid="viewer-scene-renderer-performance-refused">
          <strong>场景超出交互式渲染范围</strong>
          <p>结构数据量超过当前交互式三维视图的安全范围，源数据仍然保留。</p>
          <details><summary>技术详情</summary><code>{performanceDecision?.reason}</code></details>
        </div>
      ) : null}
      {mapping.ok && (state === "renderer_failed" || state === "chunk_load_failed" || state === "context_lost") ? (
        <div className="viewer-renderer-fallback" data-testid="viewer-scene-renderer-fallback">
          <strong>{state === "context_lost" ? "图形上下文已中断" : state === "chunk_load_failed" ? "渲染模块不可用" : "渲染器初始化失败"}</strong>
          <p role="status" aria-live="polite">已校验的结构数据仍然保留，未执行任何文件内容；可重试本地渲染器或查看下方摘要。</p>
          {state === "chunk_load_failed" || state === "context_lost" || state === "renderer_failed" ? <button type="button" className="compact secondary" onClick={retry}>重试渲染</button> : null}
          {rendererError ? <details><summary>技术详情</summary><code>{rendererError}</code></details> : null}
        </div>
      ) : null}
      {mapping.ok && state === "initializing_renderer" ? <p className="viewer-renderer-loading">正在加载本地渲染器……</p> : null}
      {mapping.ok && !["unsupported", "renderer_failed", "chunk_load_failed", "context_lost", "scene_over_renderer_cap"].includes(state) ? (
        <div ref={containerRef} className="viewer-renderer-canvas-host" data-testid="viewer-scene-renderer-valid">
          <span className="sr-only">当前显示范围包含 {renderScene?.atoms.length ?? 0} 个位点和 {renderScene?.bonds.length ?? 0} 条场景连接。</span>
        </div>
      ) : null}
      {mapping.ok && mapping.scene.sourcePreviewWarning ? <p className="notice" role="status">{mapping.scene.sourcePreviewWarning}</p> : null}
      {mapping.ok ? (
        <>
        <p className="viewer-canvas-help">拖动旋转 · 滚轮或双指缩放 · 点击原子查看详情</p>
        <dl id="viewer-scene-semantic-summary" className="sr-only" data-testid="viewer-scene-semantic-summary">
          <div><dt>化学式</dt><dd>{mapping.scene.formula}</dd></div>
          <div><dt>规范位点</dt><dd>{mapping.scene.atoms.length}</dd></div>
          <div><dt>元素种类</dt><dd>{new Set(mapping.scene.atoms.map((atom) => atom.species)).size}</dd></div>
          <div><dt>晶格</dt><dd>{mapping.scene.lattice.matrix.map((row) => `[${row.join(", ")}]`).join(" ")}</dd></div>
          <div><dt>{mapping.scene.connectivity ? "近邻连接" : "规范键合"}</dt><dd>{mapping.scene.bonds.length}</dd></div>
          <div><dt>{mapping.scene.connectivity ? "跨边界连接" : "跨边界键合"}</dt><dd>{topologySummary.crossBoundary}</dd></div>
          <div><dt>{mapping.scene.connectivity ? "自周期连接" : "自周期键合"}</dt><dd>{topologySummary.selfPeriodic}</dd></div>
          <div><dt>渲染模式</dt><dd>{performanceDecision?.tier ?? "不可用"}</dd></div>
          <div><dt>超晶胞扩展</dt><dd>{repeat.join(" × ")}</dd></div>
          <div><dt>显示位点</dt><dd>{renderScene?.atoms.length ?? 0}</dd></div>
          <div><dt>{mapping.scene.connectivity ? "显示连接" : "显示键合"}</dt><dd>{renderScene?.bonds.length ?? 0}</dd></div>
          <div><dt>选择</dt><dd>{selection.activeSite ? `${selection.activeSite.siteIndex}@[${selection.activeSite.imageOffset.join(",")}]` : "无"}</dd></div>
          <div><dt>{mapping.scene.connectivity ? "已选连接" : "已选键合"}</dt><dd>{selectedBondId ?? "无"}</dd></div>
          <div><dt>裁剪</dt><dd>{clipState.enabled ? clipState.planes.filter((plane)=>plane.enabled).map((plane)=>`${plane.axis}=${plane.position.toFixed(3)}`).join(", ") || "已启用但未设置平面" : "已停用"}</dd></div>
          <div><dt>相机视角</dt><dd>{cameraPreset}</dd></div>
          <div><dt>晶格轴</dt><dd>{showLatticeAxes ? "已显示" : "已隐藏"}</dd></div>
          <div><dt>警告</dt><dd>{mapping.scene.warnings.length ? mapping.scene.warnings.join(", ") : "无"}</dd></div>
        </dl>
        {performanceDecision?.warning ? <p className="notice" role="status" data-testid="viewer-scene-renderer-performance-warning">当前结构较大，查看器已降低像素密度以保持交互；所有通过校验的原子与键合仍会显示。</p> : null}
        {truncationWarning ? (
          <p className="notice viewer-scene-truncation-warning" role="status" data-testid="viewer-scene-renderer-truncation-warning">
            {truncationWarning.includes("当前显示前") ? truncationWarning : "当前结构已按查看器安全上限截断；完整结构仍保留在源数据中。"}
          </p>
        ) : null}
        <ViewerBondInspector bond={selectedBond} neighborMethod={mapping.scene.connectivity?.method} onClear={() => setSelectedBondId(null)} />
        {neighborError ? <p className="notice" role="alert">{neighborError}</p> : null}
        <ViewerSiteInspector atom={selectedAtom} atoms={renderScene?.atoms ?? []} bonds={renderScene?.bonds ?? []} sourceAtoms={mapping.scene.atoms} sourceBonds={mapping.scene.bonds} repeat={repeat} sourcePreview={mapping.scene.sourcePreview} neighborMethod={mapping.scene.connectivity?.method} source={mapping.scene.source.filename || mapping.scene.source.resourceId} onClear={clearSelection} onJumpPrimary={() => selectedAtom && commitSelection(selectViewerSite(initialViewerSelection(selectionRef.current.mode), {siteIndex:selectedAtom.siteIndex,imageOffset:[0,0,0]}))} onShowNeighbors={() => selectedAtom && updateNeighborDisplay(mapping.scene.connectivity ? { mode: "neighbors", center: selectedAtom.ref } : selectedAtom.siteIndex)} onClearNeighbors={() => updateNeighborDisplay(null)} onHighlightNeighbor={(target)=>{if(!selectedAtom)return;engineRef.current?.setSelection([selectedAtom.ref,target]);if(engineRef.current)setSnapshot(engineRef.current.snapshot());}} />
        <div className="viewer-structure-tools">
        <details className="viewer-progressive-details viewer-supercell-disclosure"><summary>超晶胞</summary>
        <ViewerSupercellControls draft={repeatDraft} applied={repeat} estimate={supercellError ? Object.freeze({...supercellEstimate,error:supercellError,mode:"refused" as const}) : supercellEstimate} onDraft={(axis,value)=>{const next=[...repeatDraft];next[axis]=value;setRepeatDraft(next);setSupercellError(null);}} onApply={applySupercell} onReset={resetSupercell} onPreset={(value)=>{setRepeatDraft(value.map(String));setSupercellError(null);}} onDownload={downloadSupercellState} />
        </details>
        <details className="viewer-progressive-details viewer-view-disclosure"><summary>视角与裁剪</summary>
        <ViewerViewControls clip={clipState} bounds={clipBounds} display={{unitCell:showCell,supercellBoundary:showSupercellBoundary,latticeAxes:showLatticeAxes}} preset={cameraPreset} latticeLengths={latticeLengths} onClipEnabled={(enabled)=>{const next=Object.freeze({...clipState,enabled});updateClipState(next);setAnnouncement(enabled?"已启用裁剪。":"已停用裁剪。");}} onPlaneEnabled={(axis,enabled)=>updateClipPlane(axis,{enabled})} onPosition={(axis,position)=>updateClipPlane(axis,{position})} onResetClip={()=>{const next=renderScene?initialViewerClipState(renderScene):clipState;updateClipState(next);setAnnouncement("已重置裁剪。");}} onDisplay={applyViewDisplay} onPreset={applyCameraPreset} onDownload={downloadViewState} />
        </details>

        <details className="viewer-progressive-details viewer-measurement-disclosure"><summary>测量距离与角度</summary>
        <ViewerMeasurementPanel mode={selection.mode} selected={selection.selectedSites} coordinateMode={coordinateMode} resolvedRefs={measurementDetails.refs} evaluation={measurement} history={history} onMode={changeMode} onCoordinateMode={(mode) => { setCoordinateMode(mode); clearSelection(); }} onUndo={undoSelection} onClear={clearSelection} onDownload={downloadMeasurement} />
        </details>
        {exportError ? <p className="notice" role="alert" data-testid="viewer-scene-export-error">导出失败，当前结构和已生成文件仍然保留。</p> : null}
        <details className="viewer-progressive-details viewer-advanced-export"><summary>高级导出</summary><ViewerExportPanel request={exportRequest} busy={exportBusy||state!=="rendered"} status={exportStatus} bundleReady={Boolean(exportBundle)} onChange={(request)=>{setExportRequest(request);setExportBundle(null);setExportStatus("导出设置已变化，请重新准备导出。");}} onExport={()=>void prepareExport()} onDownload={downloadPrepared}/></details>
        <details className="viewer-progressive-details viewer-technical-details"><summary>技术详情</summary>
          {exportError ? <p>导出诊断：<code>{exportError}</code></p> : null}
          <div className="viewer-artifact-downloads" aria-label="查看器技术文件">
            <button type="button" className="compact secondary" onClick={() => downloadLocalBlob(jsonBlob(payload), "viewer_scene.json")}>下载场景 JSON</button>
            {downloads?.manifest ? <button type="button" className="compact secondary" onClick={() => downloadLocalBlob(jsonBlob(downloads.manifest), "viewer_scene_manifest.json")}>下载清单</button> : null}
            {downloads?.summary ? <button type="button" className="compact secondary" onClick={() => downloadLocalBlob(new Blob([downloads.summary ?? ""], { type: "text/markdown" }), "summary.md")}>下载摘要</button> : null}
            {downloads?.recipe ? <button type="button" className="compact secondary" onClick={() => downloadLocalBlob(jsonBlob(downloads.recipe), "recipe.json")}>下载复现信息</button> : null}
          </div>
          <dl className="mini-grid viewer-renderer-audit" data-testid="viewer-scene-renderer-audit">
            <div><dt>位点</dt><dd>{mapping.scene.atoms.length}</dd></div>
            <div><dt>元素种类</dt><dd>{new Set(mapping.scene.atoms.map((atom) => atom.species)).size}</dd></div>
            <div><dt>{mapping.scene.connectivity ? "近邻连接" : "键合"}</dt><dd>{snapshot?.bondCount ?? mapping.scene.bonds.length}</dd></div>
            <div><dt>晶胞边</dt><dd>{snapshot?.latticeEdgeCount ?? 12}</dd></div>
            <div><dt>图形环境</dt><dd>{snapshot?.graphicsContext ?? "等待中"}</dd></div>
            <div><dt>渲染器</dt><dd>{snapshot?.rendererVersion ? `Three r${snapshot.rendererVersion}` : "等待中"}</dd></div>
          </dl>
          {mapping.scene.connectivity?.method === "covalent_radii" ? <div className="viewer-connection-basis">
            <p>连接判定：原子间距离不超过两元素参考共价半径之和的 {mapping.scene.connectivity.radiusScale} 倍；仅表示近邻候选，不确定键类型与键级。</p>
            <p>半径来源：{mapping.scene.connectivity.radiusReference}</p>
          </div> : mapping.scene.connectivity?.method === "ideal_first_shell" ? <p className="viewer-connection-basis">连接判定：理想晶格中已保存的最短周期距离，不表示确定的化学键或键级。</p> : null}
          {mapping.scene.sourcePreview ? mapping.scene.warnings.map((warning, index) => <p key={index}>{warning}</p>) : null}
          <output className="sr-only" data-testid="viewer-scene-renderer-metrics">{snapshot ? JSON.stringify(snapshot.metrics) : "性能指标等待中"}</output>
          <output className="sr-only" data-testid="viewer-scene-renderer-performance-tier">{performanceDecision?.tier ?? "不可用"}</output>
        </details>
        </div>
        </>
      ) : null}
    </section>
  );
}

function addOffset(value: RenderVector3, offset: ImageOffset): RenderVector3 {
  return Object.freeze([value[0] + offset[0], value[1] + offset[1], value[2] + offset[2]]);
}
