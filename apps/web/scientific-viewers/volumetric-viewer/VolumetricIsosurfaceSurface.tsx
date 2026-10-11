"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Artifact } from "../../app/lib/planner-api";
import { loadDecodedVolumetricField, loadVolumetricJsonArtifact, type VolumetricByteLoader } from "./volumetricPayloadLoader";
import { IsosurfaceWorkerClient, type IsosurfaceWorkerFactory } from "./isosurfaceWorkerClient";
import { mapVolumetricStructureOverlay } from "./volumetricOverlayMapper";
import { deriveVolumetricOverlaySupercell } from "./volumetricOverlaySupercell";
import { validateVolumetricArtifacts } from "./volumetricValidation";
import { buildChargeSpinDensityProduct, type ChargeSpinDensityProduct } from "./chargeSpinDensityProduct";
import { buildElectrostaticPotentialProduct, decodePotentialValues, potentialDifference, potentialGaugeView, potentialSurfaceLayer, profilesFromRaw, samplePotential, type ElectrostaticPotentialProduct, type PotentialAxis, type PotentialGaugeMode, type PotentialRawProfiles, type PotentialSample, type PotentialValues } from "./electrostaticPotentialProduct";
import { buildElfOrbitalProduct, validateElfOrbitalValues, type ElfOrbitalProduct } from "./elfOrbitalProduct";
import type { IsosurfaceLayerRequest, IsosurfaceMesh, ValidatedVolumetricBundle, VolumetricArtifact, VolumetricFieldCompatibility, VolumetricRendererEngine, VolumetricStructureOverlay, VolumetricSurfacePick } from "./volumetricViewerTypes";
import { VOLUMETRIC_BROWSER_CAPS, VolumetricViewerError } from "./volumetricViewerTypes";
import styles from "./VolumetricSurface.module.css";
import { PotentialProfilePanel } from "./PotentialProfilePanel";
import { potentialUnit, potentialWarning } from "./potential-profile-view";
import { DensityScientificDetails } from "./DensityScientificDetails";
import { densityFieldName, densityUnit, rangeStatus } from "./density-display";
import { supportsPairedDensity, updateIsosurfaceLayers } from "./isosurface-layer-controls";
import { useScientificPngDownload } from "../viewer-scene/use-scientific-png-download";
import { VolumetricPickInspector } from "./VolumetricPickInspector";

type Props = {
  artifacts: Artifact[];
  initialFieldId?: string | null;
  onFieldChange?: (fieldId: string) => void;
  capabilityOverride?: "supported" | "unsupported";
  byteLoader?: VolumetricByteLoader;
  workerFactory?: IsosurfaceWorkerFactory;
};

type ViewState = "loading" | "rendered" | "empty" | "unsupported" | "error";

const asVolumetric = (artifact: Artifact): VolumetricArtifact => artifact as unknown as VolumetricArtifact;
const artifactKey = (artifact?: Artifact) => artifact ? String(artifact.id || artifact.artifactId || artifact.name) : "missing";

export function VolumetricIsosurfaceSurface({ artifacts, initialFieldId = null, onFieldChange, capabilityOverride, byteLoader, workerFactory }: Props) {
  const preferredField = useRef(initialFieldId);
  preferredField.current = initialFieldId;
  const fieldChange = useRef(onFieldChange);
  fieldChange.current = onFieldChange;
  const datasetArtifact = artifacts.find((item) => item.type === "volumetric_dataset_json");
  const manifestArtifact = artifacts.find((item) => item.type === "volumetric_manifest_json");
  const overlayArtifact = artifacts.find((item) => item.type === "volumetric_structure_overlay_json");
  const [state, setState] = useState<ViewState>("loading");
  const [message, setMessage] = useState("正在加载体数据…");
  const [bundle, setBundle] = useState<ValidatedVolumetricBundle | null>(null);
  const [overlay, setOverlay] = useState<VolumetricStructureOverlay | null>(null);
  const [fieldId, setFieldId] = useState("");
  const [layers, setLayers] = useState<IsosurfaceLayerRequest[]>([]);
  const [layerVisibility, setLayerVisibility] = useState<Record<string, boolean>>({});
  const layerInputs = useRef<Record<string, HTMLInputElement | null>>({});
  const [meshes, setMeshes] = useState<IsosurfaceMesh[]>([]);
  const [surfaceVisible, setSurfaceVisible] = useState(true);
  const [structureVisible, setStructureVisible] = useState(true);
  const [cellVisible, setCellVisible] = useState(true);
  const [opacity, setOpacity] = useState(0.62);
  const [projection, setProjection] = useState<"perspective" | "orthographic">("perspective");
  const [clipping, setClipping] = useState(false);
  const [pick, setPick] = useState<VolumetricSurfacePick | null>(null);
  const [atomPick, setAtomPick] = useState<number | null>(null);
  const [metrics, setMetrics] = useState<Record<string, number> | null>(null);
  const [engineReady, setEngineReady] = useState(false);
  const [engineRevision, setEngineRevision] = useState(0);
  const [activeField, setActiveField] = useState<VolumetricFieldCompatibility | null>(null);
  const [product, setProduct] = useState<ChargeSpinDensityProduct | null>(null);
  const [potentialProduct, setPotentialProduct] = useState<ElectrostaticPotentialProduct | null>(null);
  const [elfOrbitalProduct, setElfOrbitalProduct] = useState<ElfOrbitalProduct | null>(null);
  const [overlaySupercellRepeat, setOverlaySupercellRepeat] = useState<1 | 2>(1);
  const [potentialGauge, setPotentialGauge] = useState<PotentialGaugeMode>("source_native");
  const [potentialPoints, setPotentialPoints] = useState<readonly [readonly [number,number,number] | null, readonly [number,number,number] | null]>([null, null]);
  const [potentialValues, setPotentialValues] = useState<PotentialValues | null>(null);
  const [potentialRawProfiles, setPotentialRawProfiles] = useState<PotentialRawProfiles | null>(null);
  const [potentialAxis, setPotentialAxis] = useState<PotentialAxis>("lattice_axis_2");
  const [selectedProfileIndex, setSelectedProfileIndex] = useState<number | null>(null);
  const [symmetricThreshold, setSymmetricThreshold] = useState(true);
  const hostRef = useRef<HTMLDivElement>(null);
  const engineRef = useRef<VolumetricRendererEngine | null>(null);
  const workerRef = useRef<IsosurfaceWorkerClient | null>(null);
  const revisionRef = useRef(0);
  const loadRevisionRef = useRef(0);
  const loadedKeyRef = useRef<string | null>(null);

  const key = `${artifactKey(datasetArtifact)}:${artifactKey(manifestArtifact)}:${artifactKey(overlayArtifact)}`;
  const exportIdentity = useMemo(() => ({}), [key, fieldId, meshes, overlaySupercellRepeat, engineRevision]);
  const pngDownload = useScientificPngDownload(exportIdentity);
  const overlaySupercell = useMemo(() => deriveVolumetricOverlaySupercell(overlay, overlaySupercellRepeat), [overlay, overlaySupercellRepeat]);
  useEffect(() => { setPick(null); setAtomPick(null); }, [meshes, overlaySupercell, clipping]);
  useEffect(() => {
    if (!surfaceVisible || (pick && layerVisibility[pick.layerId] === false)) setPick(null);
    if (!structureVisible) setAtomPick(null);
  }, [surfaceVisible, structureVisible, layerVisibility, pick]);

  useEffect(() => {
    const revision = ++loadRevisionRef.current;
    loadedKeyRef.current = null;
    setBundle(null); setActiveField(null); setLayers([]); setLayerVisibility({}); setFieldId(""); setOverlay(null);
    const controller = new AbortController();
    engineRef.current?.dispose(); setEngineReady(false);
    engineRef.current = null;
    workerRef.current?.dispose();
    workerRef.current = null;
    setMeshes([]); setPick(null); setAtomPick(null); setMetrics(null); setProduct(null); setPotentialProduct(null); setElfOrbitalProduct(null); setOverlaySupercellRepeat(1); setPotentialValues(null); setPotentialRawProfiles(null); setPotentialPoints([null, null]); setPotentialGauge("source_native"); setSelectedProfileIndex(null); setSymmetricThreshold(true);
    setState("loading"); setMessage("正在加载体数据…");
    if (!datasetArtifact || !manifestArtifact) { setState("error"); setMessage("缺少体数据清单，暂时无法打开。"); return () => controller.abort(); }
    if (capabilityOverride === "unsupported" || typeof window === "undefined" || typeof Worker === "undefined") { setState("unsupported"); setMessage("当前浏览器无法运行体数据等值面计算。"); return () => controller.abort(); }
    void (async () => {
      try {
        const [dataset, manifest, overlayValue] = await Promise.all([
          loadVolumetricJsonArtifact(asVolumetric(datasetArtifact), { signal: controller.signal, loader: byteLoader }),
          loadVolumetricJsonArtifact(asVolumetric(manifestArtifact), { signal: controller.signal, loader: byteLoader }),
          overlayArtifact ? loadVolumetricJsonArtifact(asVolumetric(overlayArtifact), { signal: controller.signal, loader: byteLoader }) : Promise.resolve(null),
        ]);
        if (controller.signal.aborted || revision !== loadRevisionRef.current) return;
        const validation = validateVolumetricArtifacts(dataset, manifest);
        if (!validation.ok) throw new VolumetricViewerError(validation.code, validation.errors.join(", "));
        const mappedProduct = buildChargeSpinDensityProduct(validation.bundle);
        const mappedPotential = buildElectrostaticPotentialProduct(validation.bundle);
        const mappedElfOrbital = buildElfOrbitalProduct(validation.bundle);
        const selected = validation.bundle.fields.find((item) => item.supported && item.field.fieldId === preferredField.current) ?? validation.bundle.fields.find((item) => item.supported && item.field.fieldId === (mappedPotential.fieldId ?? mappedElfOrbital.sourceFieldId ?? mappedProduct.defaultFieldId)) ?? getSupportedField(validation.bundle.fields);
        if (!selected) { setBundle(validation.bundle); setState("empty"); setMessage("没有可用于等值面提取的标量场。"); return; }
        const mappedOverlay = overlayValue ? mapVolumetricStructureOverlay(overlayValue, validation.bundle) : null;
        if (mappedOverlay && !mappedOverlay.ok) throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", mappedOverlay.errors.join(", "));
        if (controller.signal.aborted || revision !== loadRevisionRef.current) return;
        loadedKeyRef.current = key;
        setBundle(validation.bundle); setProduct(buildChargeSpinDensityProduct(validation.bundle, selected.field.fieldId)); setPotentialProduct(mappedPotential); setElfOrbitalProduct(buildElfOrbitalProduct(validation.bundle, null, selected.field.fieldId)); setActiveField(selected); setFieldId(selected.field.fieldId);
        fieldChange.current?.(selected.field.fieldId);
        setOverlay(mappedOverlay && mappedOverlay.ok ? mappedOverlay.overlay : null);
        const nextLayers = defaultLayers(selected);
        setLayers(nextLayers); setLayerVisibility(Object.fromEntries(nextLayers.map((layer) => [layer.layerId, true])));
      } catch (error) {
        if (controller.signal.aborted || revision !== loadRevisionRef.current) return;
        setState(error instanceof VolumetricViewerError && error.code === "VOLUME_VIEWER_WORKER_UNAVAILABLE" ? "unsupported" : "error");
        setMessage(error instanceof Error ? error.message : "体数据无法安全加载。");
      }
    })();
    return () => { controller.abort(); engineRef.current?.dispose(); engineRef.current = null; setEngineReady(false); workerRef.current?.dispose(); workerRef.current = null; };
  }, [key, capabilityOverride, byteLoader]);

  useEffect(() => {
    if (loadedKeyRef.current !== key || !bundle || !activeField || !layers.length) return;
    const revision = ++revisionRef.current;
    const controller = new AbortController();
    setState("loading"); setMessage("正在生成等值面…");
    void (async () => {
      try {
        const decoded = await loadDecodedVolumetricField({ field: activeField.field, payload: activeField.payload, artifacts: artifacts.map(asVolumetric), signal: controller.signal, loader: byteLoader });
        if (controller.signal.aborted || revision !== revisionRef.current) return;
        const isPotential = Boolean(potentialProduct?.fieldId === activeField.field.fieldId);
        if (isPotential) setPotentialValues(decodePotentialValues(decoded.buffer.slice(0), activeField.payload.dtype));
        if (["electron_localization_function", "orbital_density"].includes(activeField.field.quantity)) {
          const values = decodePotentialValues(decoded.buffer.slice(0), activeField.payload.dtype);
          const kind = activeField.field.quantity === "electron_localization_function" ? "elf" : "orbital_density";
          const range = validateElfOrbitalValues(values, activeField.payload.dtype, kind, activeField.field.contentHash);
          setElfOrbitalProduct(buildElfOrbitalProduct(bundle, range, activeField.field.fieldId));
        }
        const client = new IsosurfaceWorkerClient(workerFactory); workerRef.current = client;
        const result = await client.extract({ type: "extract", fieldId: activeField.field.fieldId, fieldHash: activeField.field.contentHash, grid: bundle.grid, dtype: activeField.payload.dtype, fieldBuffer: decoded.buffer, computePotentialProfiles:isPotential, layers, caps: { maximumVerticesPerLayer: VOLUMETRIC_BROWSER_CAPS.maximumVerticesPerLayer, maximumTrianglesPerLayer: VOLUMETRIC_BROWSER_CAPS.maximumTrianglesPerLayer, maximumTotalVertices: VOLUMETRIC_BROWSER_CAPS.maximumTotalVertices, maximumTotalTriangles: VOLUMETRIC_BROWSER_CAPS.maximumTotalTriangles, maximumExtractionMs: VOLUMETRIC_BROWSER_CAPS.maximumExtractionMs } });
        if (controller.signal.aborted || revision !== revisionRef.current) return;
        setPotentialRawProfiles(result.potentialProfiles?.sourceValues??null); setMeshes([...result.meshes]); setMetrics({ ...result.metrics, ...(result.potentialProfiles ? { profileCalculationMs:result.potentialProfiles.calculationMs } : {}) }); setState(result.meshes.length ? "rendered" : "empty"); setMessage(result.meshes.length ? "已根据校验后的规范场数据生成等值面。" : "所选等值未与当前场相交。");
      } catch (error) {
        if (controller.signal.aborted || revision !== revisionRef.current) return;
        setState(error instanceof VolumetricViewerError && error.code === "VOLUME_VIEWER_WORKER_UNAVAILABLE" ? "unsupported" : "error"); setMessage(error instanceof Error ? error.message : "等值面提取已安全停止。");
      }
    })();
    return () => { controller.abort(); workerRef.current?.cancel(); workerRef.current = null; };
  }, [key, bundle, activeField, layers, artifacts, byteLoader, workerFactory, potentialProduct]);

  useEffect(() => {
    if (loadedKeyRef.current !== key || !hostRef.current || !meshes.length || !bundle || !activeField || state === "error" || state === "unsupported") return;
    let disposed = false;
    void import("./volumetricRendererEngine").then(({ createVolumetricRendererEngine }) => {
      if (disposed || !hostRef.current) return;
      return createVolumetricRendererEngine({ container: hostRef.current, grid: bundle.grid, fieldId: activeField.field.fieldId, meshes, overlay: overlaySupercell.overlay,
        onSurfacePick: value => { if (!disposed) { setPick(value); setAtomPick(null); if (value) hostRef.current?.focus({ preventScroll: true }); } },
        onAtomPick: value => { if (!disposed) { setAtomPick(value); if (value !== null) { setPick(null); hostRef.current?.focus({ preventScroll: true }); } } },
        onContextLost: () => { setEngineReady(false); setState("error"); setMessage("WebGL 上下文已丢失，仍可查看 JSON 和元数据。"); } }).then((engine) => { if (disposed) engine.dispose(); else { engineRef.current = engine; setEngineRevision((revision) => revision + 1); setEngineReady(true); setState("rendered"); } });
    }).catch(() => { if (!disposed) { setState("error"); setMessage("体数据渲染模块加载失败。"); } });
    return () => { disposed = true; engineRef.current?.dispose(); engineRef.current = null; setEngineReady(false); };
  }, [key, meshes, bundle, activeField, overlaySupercell]);

  useEffect(() => {
    if (!engineReady) return;
    engineRef.current?.setSurfaceVisible(surfaceVisible);
    for (const [layerId, visible] of Object.entries(layerVisibility)) engineRef.current?.setLayerVisible(layerId, visible);
  }, [engineReady, engineRevision, surfaceVisible, layerVisibility]);
  useEffect(() => { if (engineReady) engineRef.current?.setStructureVisible(structureVisible); }, [engineReady, engineRevision, structureVisible]);
  useEffect(() => { if (engineReady) engineRef.current?.setCellVisible(cellVisible); }, [engineReady, engineRevision, cellVisible]);
  useEffect(() => { if (engineReady) engineRef.current?.setOpacity(opacity); }, [engineReady, engineRevision, opacity]);
  useEffect(() => { if (engineReady) engineRef.current?.setProjection(projection); }, [engineReady, engineRevision, projection]);
  useEffect(() => { if (engineReady) engineRef.current?.setClipping(clipping, 2, 0); }, [engineReady, engineRevision, clipping]);
  useEffect(() => { if (engineReady) engineRef.current?.setSelection(pick); }, [engineReady, engineRevision, pick]);
  useEffect(() => { if (engineReady) engineRef.current?.setProfilePlane(potentialAxisIndex(potentialAxis), selectedProfileIndex); }, [engineReady, engineRevision, potentialAxis, selectedProfileIndex]);
  useEffect(() => {
    if(!pick||!bundle||!activeField||!potentialValues||potentialProduct?.fieldId!==activeField.field.fieldId)return;
    const axis=potentialAxisIndex(potentialAxis);const coordinate=samplePotential(potentialValues,bundle.grid,activeField.field,pick.cartesianPosition,0).gridCoordinate[axis];
    setSelectedProfileIndex(Math.max(0,Math.min(bundle.grid.shape[axis]-1,Math.round(coordinate))));
  },[pick,bundle,activeField,potentialValues,potentialProduct,potentialAxis]);

  const selectField = (nextFieldId: string) => {
    const selected = bundle?.fields.find((item) => item.supported && item.field.fieldId === nextFieldId);
    if (!selected) return;
    fieldChange.current?.(nextFieldId);
    setMeshes([]); setMetrics(null); setEngineReady(false);
    setActiveField(selected); setFieldId(nextFieldId); setPick(null); setAtomPick(null); setPotentialValues(null); setPotentialRawProfiles(null); setPotentialPoints([null, null]); setPotentialGauge("source_native"); setSelectedProfileIndex(null);
    if (bundle) { setElfOrbitalProduct(buildElfOrbitalProduct(bundle, null, nextFieldId)); setProduct(buildChargeSpinDensityProduct(bundle, nextFieldId)); }
    const nextLayers = defaultLayers(selected);
    setLayers(nextLayers); setLayerVisibility(Object.fromEntries(nextLayers.map((layer) => [layer.layerId, true])));
  };

  useEffect(() => {
    if (initialFieldId && initialFieldId !== activeField?.field.fieldId) selectField(initialFieldId);
  }, [initialFieldId, bundle]);

  const pairedDensity = supportsPairedDensity(activeField?.field);
  const updateLayer = (layerId: string, value: number) => setLayers(current => updateIsosurfaceLayers(current, layerId, potentialField ? value - currentShift : value, pairedDensity && symmetricThreshold));
  const applyPreset = (absoluteIsovalue: number) => {
    if (!activeField) return;
    const signed = supportsPairedDensity(activeField.field);
    const next = signed ? pairedLayers(absoluteIsovalue) : [{ layerId:"surface-1", isovalue:absoluteIsovalue, sign:"positive" as const }];
    setLayers(next); setLayerVisibility(Object.fromEntries(next.map((layer) => [layer.layerId, true])));
  };
  const addLayer = () => {
    if (layers.length >= VOLUMETRIC_BROWSER_CAPS.maximumLayers || !activeField) return;
    const value = pairedDensity && symmetricThreshold && layers.length === 1 ? -layers[0].isovalue : activeField.field.minimum + (activeField.field.maximum - activeField.field.minimum) * 0.5;
    let index = 1;
    while (layers.some((layer) => layer.layerId === `surface-${index}`)) index += 1;
    const layerId = `surface-${index}`;
    setLayers((current) => [...current, { layerId, isovalue: value, sign: value < 0 ? "negative" : "positive" }]);
    setLayerVisibility((current) => ({ ...current, [layerId]: true }));
  };
  const toggleLayer = (layerId: string) => setLayerVisibility((current) => ({ ...current, [layerId]: current[layerId] === false }));
  const downloadPng = () => pngDownload.download(async () => {
    const engine = engineRef.current;
    if (!engine) throw new Error("VIEWER_EXPORT_CONTEXT_UNAVAILABLE");
    return engine.exportPng(1200,900,1);
  }, "volumetric-isosurface.png", () => setMessage("图片导出失败，请重试。"));
  const potentialField = potentialProduct?.fieldId && activeField?.field.fieldId === potentialProduct.fieldId ? activeField.field : null;
  const selectedReference = potentialField && potentialValues && potentialPoints[0] && bundle ? samplePotential(potentialValues, bundle.grid, potentialField, potentialPoints[0], 0).sourceValue : null;
  const gaugeView = potentialField&&bundle ? potentialGaugeView(potentialField,bundle.grid,potentialGauge,selectedReference) : null;
  const currentShift = gaugeView?.shift??0;
  const pointSamples: readonly (PotentialSample | null)[] = potentialField && potentialValues && bundle ? potentialPoints.map((point) => point ? samplePotential(potentialValues, bundle.grid, potentialField, point, currentShift) : null) : [null, null];
  const profiles = potentialField && potentialRawProfiles && bundle ? profilesFromRaw(potentialRawProfiles, bundle.grid, potentialField, potentialGauge, currentShift) : [];
  const potentialLayers = potentialField ? layers.map((layer)=>potentialSurfaceLayer(layer.layerId,layer.isovalue,potentialField,potentialGauge,currentShift)) : [];
  const pickedPotentialLayer = pick ? potentialLayers.find((layer) => layer.layerId === pick.layerId) ?? null : null;
  const activeProfile = profiles.find((profile)=>profile.axis===potentialAxis)??null;
  const gridCenter: readonly [number,number,number] | null = bundle ? [0,1,2].map((component)=>bundle.grid.origin[component]+bundle.grid.stepMatrix.reduce((sum,row,axis)=>sum+row[component]*bundle.grid.shape[axis]*0.5,0)) as [number,number,number] : null;
  const hasDensityDetails = Boolean(activeField && (elfOrbitalProduct?.sourceFieldId === activeField.field.fieldId || Object.values(product?.modeFieldIds ?? {}).includes(activeField.field.fieldId)));
  const clearPick = () => { setPick(null); setAtomPick(null); hostRef.current?.focus({ preventScroll: true }); };

  const statusClass = state === "rendered" || state === "error" || state === "unsupported" ? "notice warning" : "notice";
  return <section className={`viewer-renderer-surface volumetric-isosurface-surface ${styles.surface}`} aria-label="交互式体数据等值面" data-testid="volumetric-isosurface-surface">
    <div className="viewer-renderer-toolbar">
      <div>
        {bundle && activeField ? <strong>{bundle.fields.length > 1 ? <label className={styles.fieldSelector}>字段 <select data-testid="volumetric-field-selector" value={fieldId} onChange={(event) => selectField(event.target.value)}>{bundle.fields.map((item) => <option key={item.field.fieldId} value={item.field.fieldId} disabled={!item.supported}>{densityFieldName(item.field)}{item.supported ? "" : "（不支持）"}</option>)}</select></label> : densityFieldName(activeField.field)} · {densityUnit(activeField.field.unit)}</strong> : <strong>等值面</strong>}
        <span className={state === "rendered" ? "sr-only" : undefined} data-testid="volumetric-renderer-state">{state === "rendered" ? "已渲染" : state === "loading" ? "加载中" : state === "error" ? "错误" : state === "unsupported" ? "不支持" : "暂无结果"}</span>
      </div>
      <div className="viewer-renderer-controls">
        <button type="button" onClick={() => engineRef.current?.resetCamera()} disabled={!engineReady}>重置视角</button>
        <button type="button" onClick={() => engineRef.current?.fitSurface()} disabled={!engineReady}>适配表面</button>
        <button type="button" onClick={downloadPng} disabled={!engineReady||pngDownload.busy}>{pngDownload.busy?"正在导出…":"下载图片"}</button>
      </div>
    </div>
    <p className={state === "rendered" && message === "已根据校验后的规范场数据生成等值面。" ? "sr-only" : statusClass} role="status" aria-live="polite" data-testid="volumetric-renderer-status">{message}</p>
    {activeField ? <div className={styles.isosurfaceControls}>
      <div className={styles.layers} data-testid="volumetric-isovalue-controls">
        {layers.map((layer, index) => {
          const identity = potentialLayers.find((item) => item.layerId === layer.layerId);
          return <div className={styles.layerRow} key={layer.layerId}>
            <label className={styles.isovalue}>等值 {layers.length > 1 ? index + 1 : ""}<input ref={(node) => { layerInputs.current[layer.layerId] = node; }} aria-label={`等值面 ${index + 1} 的等值`} type="number" step="any" value={identity?.displayedIsovalue ?? layer.isovalue} onChange={(event) => updateLayer(layer.layerId, Number(event.target.value))} /></label>
            <label className={styles.layerVisibility}><input type="checkbox" aria-label={`显示等值面 ${index + 1}`} checked={layerVisibility[layer.layerId] !== false} onChange={() => toggleLayer(layer.layerId)} />显示</label>
            {layers.length > 1 ? <button type="button" aria-label={`移除等值面 ${index + 1}`} onClick={() => {
              layerInputs.current[(layers[index + 1] ?? layers[index - 1]).layerId]?.focus();
              setLayers((current) => current.filter((item) => item.layerId !== layer.layerId));
              setLayerVisibility((current) => { const next = { ...current }; delete next[layer.layerId]; return next; });
            }}>移除</button> : null}
            {identity && currentShift !== 0 ? <span className={styles.layerIdentity} data-testid="potential-layer-identity">源值 {format(identity.sourceIsovalue)} / 显示值 {format(identity.displayedIsovalue)} {potentialUnit(identity.unit)}</span> : null}
          </div>;
        })}
        <button type="button" onClick={addLayer} disabled={layers.length >= VOLUMETRIC_BROWSER_CAPS.maximumLayers}>添加等值面</button>
      </div>
      {elfOrbitalProduct && elfOrbitalProduct.status !== "unavailable" && elfOrbitalProduct.sourceFieldId === activeField.field.fieldId ? <div className={styles.presetControls} data-testid="elf-orbital-presets" role="group" aria-label="等值预设">
        <span>等值预设</span>{elfOrbitalProduct.presets.map(preset => <button type="button" key={preset.id} onClick={() => applyPreset(preset.exactIsovalue)}>{Number(preset.exactIsovalue.toPrecision(6))}</button>)}
        <span data-testid="elf-orbital-validation" role="status">{rangeStatus(elfOrbitalProduct.rangeValidation?.status)}</span>
      </div> : product && product.status === "ready" && Object.values(product.modeFieldIds).includes(activeField.field.fieldId) ? <div className={styles.presetControls} data-testid="charge-spin-presets" role="group" aria-label="等值预设">
        <span>等值预设</span>{product.presets.map(preset => <button type="button" key={preset.id} onClick={() => applyPreset(preset.absoluteIsovalue)}>{Number(preset.absoluteIsovalue.toPrecision(6))}</button>)}
        {pairedDensity ? <label><input type="checkbox" checked={symmetricThreshold} disabled={layers.length !== 2} onChange={event => {
          const enabled = event.target.checked; setSymmetricThreshold(enabled);
          if (enabled && layers.length === 2) setLayers(current => updateIsosurfaceLayers(current, current[0].layerId, current[0].isovalue, true));
        }} />正负等值同步</label> : null}
        {pairedDensity && !symmetricThreshold ? <span>阈值不对称不代表物理不对称。</span> : null}
      </div> : null}
      <div className={styles.controlRow}>
        <label>投影<select value={projection} onChange={(event) => setProjection(event.target.value as typeof projection)}><option value="perspective">透视</option><option value="orthographic">正交</option></select></label>
        <label className={styles.opacity}>不透明度<span><input aria-label="不透明度" type="range" min="0.1" max="0.9" step="0.01" value={opacity} onChange={(event) => setOpacity(Number(event.target.value))} /><output>{Math.round(opacity * 100)}%</output></span></label>
        {elfOrbitalProduct?.status !== "unavailable" && elfOrbitalProduct?.sourceFieldId === activeField.field.fieldId && overlay?.kind === "periodic_viewer_scene" ? <label>结构超胞<select aria-label="结构超胞" value={overlaySupercellRepeat} onChange={event => { setPick(null); setAtomPick(null); setOverlaySupercellRepeat(Number(event.target.value) === 2 ? 2 : 1); }}><option value="1">1×1×1</option><option value="2">2×2×2</option></select></label> : null}
        <div className={styles.overlaySwitch}>
          <label><input type="checkbox" checked={surfaceVisible} onChange={(event) => setSurfaceVisible(event.target.checked)} />表面</label>
          {overlay ? <label><input type="checkbox" checked={structureVisible} onChange={(event) => setStructureVisible(event.target.checked)} />结构</label> : null}
          <label><input type="checkbox" checked={cellVisible} onChange={(event) => setCellVisible(event.target.checked)} />晶胞</label>
          <label><input type="checkbox" checked={clipping} onChange={(event) => setClipping(event.target.checked)} />裁剪</label>
        </div>
      </div>
    </div> : null}
    {overlaySupercell.status === "cap_exceeded" ? <p className="warning" role="status">结构超胞超出显示上限，已保留原胞。</p> : null}
    <div ref={hostRef} className={`viewer-renderer-canvas-host ${styles.pickCanvas}`} data-testid="volumetric-renderer-canvas-host" aria-label="体数据图形画布" role="group" tabIndex={0}
      onKeyDown={event => { if (event.key === "Escape" && (pick || atomPick !== null)) { event.preventDefault(); event.stopPropagation(); clearPick(); } }} />
    <VolumetricPickInspector pick={pick} atom={atomPick} layerNumber={layers.findIndex(layer => layer.layerId === pick?.layerId) + 1}
      unit={activeField?.field.unit ?? ""} fieldHash={activeField?.field.contentHash} potentialLayer={pickedPotentialLayer} onClear={clearPick} />
    <div className={styles.details}>
      {bundle && activeField ? <details><summary>{hasDensityDetails ? "网格属性" : "字段与网格属性"}</summary><dl className="mini-grid">{!hasDensityDetails ? <><dt>来源</dt><dd>{bundle.sourceFormat}</dd><dt>字段</dt><dd>{activeField.field.fieldName}</dd><dt>物理量</dt><dd>{activeField.field.quantity}</dd><dt>单位</dt><dd>{activeField.field.unit}</dd><dt>归一化</dt><dd>{activeField.field.normalizationSemantics}</dd></> : null}<dt>网格</dt><dd>{bundle.grid.shape.join(" × ")} / {bundle.grid.periodic ? "周期" : "仿射"}</dd><dt>范围</dt><dd>{activeField.field.minimum} 至 {activeField.field.maximum} {densityUnit(activeField.field.unit)}</dd></dl></details> : null}
      {metrics ? <details><summary>渲染详情</summary><dl className="mini-grid" data-testid="volumetric-renderer-metrics"><dt>顶点</dt><dd>{metrics.vertices}</dd><dt>三角形</dt><dd>{metrics.triangles}</dd><dt>提取耗时（ms）</dt><dd data-testid="volumetric-extraction-ms">{metrics.extractionMs}</dd>{overlay ? <><dt>结构显示</dt><dd>{overlaySupercell.repeat}×{overlaySupercell.repeat}×{overlaySupercell.repeat} · {overlaySupercell.atomCount} 个原子 · {overlaySupercell.bondCount} 条键；体数据仍为源晶胞。</dd></> : null}{Number.isFinite(metrics.profileCalculationMs) ? <><dt>剖面计算耗时（ms）</dt><dd data-testid="potential-profile-calculation-ms">{metrics.profileCalculationMs}</dd></> : null}</dl></details> : null}
    </div>
    {bundle && activeField ? <DensityScientificDetails bundle={bundle} field={activeField.field} charge={product} orbital={elfOrbitalProduct} /> : null}
    {potentialProduct?.status === "ready" && potentialField && bundle ? <section className={`volumetric-product-panel potential-product-panel ${styles.scientificPanel}`} aria-label="静电势分析" data-testid="electrostatic-potential-product">
      <div data-testid="potential-product-header"><strong>{potentialField.quantity === "local_potential" ? "局域势" : "静电势"}</strong><span>显示平移 {format(currentShift)} {potentialUnit(potentialField.unit)}</span></div>
      <div className="potential-product-controls"><label>显示零点 <select data-testid="potential-gauge" value={potentialGauge} onChange={(event) => setPotentialGauge(event.target.value as PotentialGaugeMode)}><option value="source_native">源数据零点</option><option value="cell_average_zero">胞平均值为零</option><option value="selected_point_zero" disabled={!potentialPoints[0]}>A 点为零</option></select></label><button type="button" data-testid="potential-gauge-reset" onClick={() => setPotentialGauge("source_native")}>重置零点</button><label>剖面方向 <select data-testid="potential-profile-axis" value={potentialAxis} onChange={(event) => {setPotentialAxis(event.target.value as PotentialAxis);setSelectedProfileIndex(null);}}><option value="lattice_axis_0">a 轴（0）</option><option value="lattice_axis_1">b 轴（1）</option><option value="lattice_axis_2">c 轴（2）</option></select></label></div>
      {potentialGauge === "selected_point_zero" && pointSamples[0] ? <p data-testid="potential-selected-reference">以 A 点的源值 {pointSamples[0].sourceValue} {potentialUnit(pointSamples[0].unit)} 为显示零点；这不定义物理绝对零点。</p> : null}
      <PotentialProfilePanel key={`${potentialField.contentHash}:${potentialAxis}`} profile={activeProfile} selectedIndex={selectedProfileIndex} onSelect={setSelectedProfileIndex} />
      <details className={styles.scientificDetails}><summary>两点势差</summary>
      <div className="potential-product-controls"><button type="button" data-testid="potential-point-a" disabled={!pick} onClick={() => pick && setPotentialPoints(([_, b]) => [pick.cartesianPosition as [number,number,number], b])}>当前选点设为 A</button><button type="button" data-testid="potential-point-b" disabled={!pick} onClick={() => pick && setPotentialPoints(([a, _]) => [a, pick.cartesianPosition as [number,number,number]])}>当前选点设为 B</button><button type="button" data-testid="potential-grid-point-a" onClick={() => setPotentialPoints(([_, b]) => [bundle.grid.origin, b])}>网格原点设为 A</button><button type="button" data-testid="potential-grid-point-b" disabled={!gridCenter} onClick={() => gridCenter && setPotentialPoints(([a, _]) => [a, gridCenter])}>晶胞中心设为 B</button><button type="button" data-testid="potential-points-clear" onClick={() => { setPotentialPoints([null, null]); setPotentialGauge("source_native"); }}>清除选点</button></div>
        <div data-testid="potential-point-inspector" className={styles.pointComparison}>
          {pointSamples.map((sample, index) => <div key={index}><strong>{index === 0 ? "A 点" : "B 点"}</strong>{sample ? <dl className="mini-grid"><dt>源值</dt><dd>{sample.sourceValue} {potentialUnit(sample.unit)}</dd><dt>显示值</dt><dd>{sample.displayedValue} {potentialUnit(sample.unit)}</dd><dt>笛卡尔坐标（Å）</dt><dd>{sample.cartesian.map(format).join(", ")}</dd><dt>分数坐标</dt><dd>{sample.fractional?.map(format).join(", ") ?? "非周期网格"}</dd><dt>周期像</dt><dd>{sample.imageOffset.join(", ")}</dd><dt>插值</dt><dd>{sample.interpolation === "trilinear_periodic" ? "周期三线性插值" : "仿射三线性插值"}</dd></dl> : <p>未选择</p>}</div>)}
        </div>
        {pointSamples[0] && pointSamples[1] ? <p data-testid="potential-point-difference">ΔV（B − A）= {potentialDifference(pointSamples[0], pointSamples[1]).value} {potentialUnit(potentialField.unit)}，不受显示零点影响。</p> : null}
      </details>
      <details className={styles.scientificDetails}><summary>统计量</summary>
      <dl className="mini-grid" data-testid="potential-statistics"><dt>源值范围</dt><dd>{format(gaugeView?.sourceMinimum??potentialField.minimum)} 至 {format(gaugeView?.sourceMaximum??potentialField.maximum)} {potentialUnit(potentialField.unit)}</dd><dt>显示范围</dt><dd>{format(gaugeView?.displayedMinimum??potentialField.minimum)} 至 {format(gaugeView?.displayedMaximum??potentialField.maximum)} {potentialUnit(potentialField.unit)}</dd><dt>源均值／胞平均值</dt><dd>{format(gaugeView?.sourceMean??potentialField.mean)} {potentialUnit(potentialField.unit)}</dd><dt>显示均值</dt><dd>{format(gaugeView?.displayedMean??potentialField.mean)} {potentialUnit(potentialField.unit)}</dd><dt>标准差（不受零点影响）</dt><dd>{format(potentialField.standardDeviation)} {potentialUnit(potentialField.unit)}</dd><dt>源／显示均方根</dt><dd>{format(potentialField.rms)} / {format(gaugeView?.displayedRms??potentialField.rms)} {potentialUnit(potentialField.unit)}</dd><dt>源体积分</dt><dd>{format(potentialField.integral)} {potentialUnit(potentialField.unit)}·Å³</dd><dt>显示体积分</dt><dd>{format(gaugeView?.displayedVolumeIntegral??potentialField.integral)} {potentialUnit(potentialField.unit)}·Å³</dd></dl>
      </details>
      <details className={styles.scientificDetails}><summary>势能属性与来源</summary>
      <dl className="mini-grid"><dt>物理量</dt><dd data-testid="potential-quantity">{potentialProduct.quantity}</dd><dt>单位</dt><dd data-testid="potential-unit">{potentialUnit(potentialProduct.unit ?? "")}</dd><dt>源参考系</dt><dd data-testid="potential-reference">{potentialField.potentialReference?.kind}</dd><dt>显示平移量</dt><dd data-testid="potential-shift">{format(currentShift)} {potentialUnit(potentialProduct.unit ?? "")}</dd><dt>零点变换公式</dt><dd data-testid="potential-gauge-formula">{gaugeView?.formulaId}</dd><dt>字段校验值</dt><dd>{potentialField.contentHash}</dd></dl>
      </details>
      <details className={styles.scientificDetails}><summary>科学适用范围</summary><ul>{potentialProduct.warnings.map(warning => <li key={warning}>{potentialWarning(warning)}</li>)}</ul></details>
    </section> : null}
  </section>;
}

function getSupportedField(fields: readonly VolumetricFieldCompatibility[]): VolumetricFieldCompatibility | null { return fields.find((item) => item.supported) ?? null; }
function pairedLayers(value:number):IsosurfaceLayerRequest[]{const magnitude=Math.max(Math.abs(value),Number.EPSILON);return [{layerId:"positive-1",isovalue:magnitude,sign:"positive"},{layerId:"negative-1",isovalue:-magnitude,sign:"negative"}];}
function defaultLayers(field:VolumetricFieldCompatibility):IsosurfaceLayerRequest[]{const range=Math.max(Math.abs(field.field.minimum),Math.abs(field.field.maximum));const span=field.field.maximum-field.field.minimum;const potential=["local_potential","electrostatic_potential"].includes(field.field.quantity);const elf=field.field.quantity==="electron_localization_function";const orbital=field.field.quantity==="orbital_density";const signed=!potential&&!elf&&!orbital&&(field.field.spin?.channel==="spin_difference"||(field.field.minimum<0&&field.field.maximum>0));const value=elf?0.7:orbital?Math.max(0,field.field.maximum)*0.25:potential?field.field.mean:field.field.minimum+span*0.25;return signed?pairedLayers(range*0.25):[{layerId:"surface-1",isovalue:value,sign:value<0?"negative":"positive"}];}
function format(value:number){return Number.isFinite(value)?value.toPrecision(6):"unavailable";}
function potentialAxisIndex(axis:PotentialAxis):0|1|2{return axis==="lattice_axis_0"?0:axis==="lattice_axis_1"?1:2;}
