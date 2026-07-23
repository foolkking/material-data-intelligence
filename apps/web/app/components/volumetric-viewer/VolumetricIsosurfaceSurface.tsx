"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Artifact } from "../../lib/planner-api";
import { loadDecodedVolumetricField, loadVolumetricJsonArtifact, type VolumetricByteLoader } from "./volumetricPayloadLoader";
import { IsosurfaceWorkerClient, type IsosurfaceWorkerFactory } from "./isosurfaceWorkerClient";
import { mapVolumetricStructureOverlay } from "./volumetricOverlayMapper";
import { validateVolumetricArtifacts } from "./volumetricValidation";
import { buildChargeSpinDensityProduct, type ChargeSpinDensityProduct } from "./chargeSpinDensityProduct";
import { buildElectrostaticPotentialProduct, decodePotentialValues, potentialDifference, potentialGaugeView, potentialSurfaceLayer, profilesFromRaw, samplePotential, type ElectrostaticPotentialProduct, type PotentialAxis, type PotentialGaugeMode, type PotentialRawProfiles, type PotentialSample, type PotentialValues } from "./electrostaticPotentialProduct";
import type { IsosurfaceLayerRequest, IsosurfaceMesh, ValidatedVolumetricBundle, VolumetricArtifact, VolumetricFieldCompatibility, VolumetricRendererEngine, VolumetricStructureOverlay, VolumetricSurfacePick } from "./volumetricViewerTypes";
import { VOLUMETRIC_BROWSER_CAPS, VolumetricViewerError } from "./volumetricViewerTypes";

type Props = {
  artifacts: Artifact[];
  capabilityOverride?: "supported" | "unsupported";
  byteLoader?: VolumetricByteLoader;
  workerFactory?: IsosurfaceWorkerFactory;
};

type ViewState = "loading" | "rendered" | "empty" | "unsupported" | "error";

const asVolumetric = (artifact: Artifact): VolumetricArtifact => artifact as unknown as VolumetricArtifact;
const artifactKey = (artifact?: Artifact) => artifact ? String(artifact.id || artifact.artifactId || artifact.name) : "missing";

export function VolumetricIsosurfaceSurface({ artifacts, capabilityOverride, byteLoader, workerFactory }: Props) {
  const datasetArtifact = artifacts.find((item) => item.type === "volumetric_dataset_json" || item.name === "volumetric_dataset.json");
  const manifestArtifact = artifacts.find((item) => item.type === "volumetric_manifest_json" || item.name === "volumetric_manifest.json");
  const overlayArtifact = artifacts.find((item) => item.type === "volumetric_structure_overlay_json" || item.name === "volumetric_structure_overlay.json");
  const [state, setState] = useState<ViewState>("loading");
  const [message, setMessage] = useState("Loading validated volumetric artifacts...");
  const [bundle, setBundle] = useState<ValidatedVolumetricBundle | null>(null);
  const [overlay, setOverlay] = useState<VolumetricStructureOverlay | null>(null);
  const [fieldId, setFieldId] = useState("");
  const [layers, setLayers] = useState<IsosurfaceLayerRequest[]>([]);
  const [layerVisibility, setLayerVisibility] = useState<Record<string, boolean>>({});
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
  const [activeField, setActiveField] = useState<VolumetricFieldCompatibility | null>(null);
  const [product, setProduct] = useState<ChargeSpinDensityProduct | null>(null);
  const [potentialProduct, setPotentialProduct] = useState<ElectrostaticPotentialProduct | null>(null);
  const [potentialGauge, setPotentialGauge] = useState<PotentialGaugeMode>("source_native");
  const [potentialPoints, setPotentialPoints] = useState<readonly [readonly [number,number,number] | null, readonly [number,number,number] | null]>([null, null]);
  const [potentialValues, setPotentialValues] = useState<PotentialValues | null>(null);
  const [potentialRawProfiles, setPotentialRawProfiles] = useState<PotentialRawProfiles | null>(null);
  const [potentialAxis, setPotentialAxis] = useState<PotentialAxis>("lattice_axis_2");
  const [selectedProfileIndex, setSelectedProfileIndex] = useState<number | null>(null);
  const [hoveredProfileIndex, setHoveredProfileIndex] = useState<number | null>(null);
  const [profileWindow, setProfileWindow] = useState<readonly [number,number]>([0,1]);
  const [symmetricThreshold, setSymmetricThreshold] = useState(true);
  const hostRef = useRef<HTMLDivElement>(null);
  const engineRef = useRef<VolumetricRendererEngine | null>(null);
  const workerRef = useRef<IsosurfaceWorkerClient | null>(null);
  const revisionRef = useRef(0);

  const key = `${artifactKey(datasetArtifact)}:${artifactKey(manifestArtifact)}:${artifactKey(overlayArtifact)}`;

  useEffect(() => {
    const revision = ++revisionRef.current;
    const controller = new AbortController();
    engineRef.current?.dispose(); setEngineReady(false);
    engineRef.current = null;
    workerRef.current?.dispose();
    workerRef.current = null;
    setMeshes([]); setPick(null); setAtomPick(null); setMetrics(null); setProduct(null); setPotentialProduct(null); setPotentialValues(null); setPotentialRawProfiles(null); setPotentialPoints([null, null]); setPotentialGauge("source_native"); setSelectedProfileIndex(null); setHoveredProfileIndex(null); setProfileWindow([0,1]); setSymmetricThreshold(true);
    setState("loading"); setMessage("Validating canonical volumetric artifacts...");
    if (!datasetArtifact || !manifestArtifact) { setState("error"); setMessage("Required volumetric dataset and manifest are unavailable."); return () => controller.abort(); }
    if (capabilityOverride === "unsupported" || typeof window === "undefined" || typeof Worker === "undefined") { setState("unsupported"); setMessage("This browser cannot run the application-owned isosurface Worker."); return () => controller.abort(); }
    void (async () => {
      try {
        const [dataset, manifest, overlayValue] = await Promise.all([
          loadVolumetricJsonArtifact(asVolumetric(datasetArtifact), { signal: controller.signal, loader: byteLoader }),
          loadVolumetricJsonArtifact(asVolumetric(manifestArtifact), { signal: controller.signal, loader: byteLoader }),
          overlayArtifact ? loadVolumetricJsonArtifact(asVolumetric(overlayArtifact), { signal: controller.signal, loader: byteLoader }) : Promise.resolve(null),
        ]);
        const validation = validateVolumetricArtifacts(dataset, manifest);
        if (!validation.ok) throw new VolumetricViewerError(validation.code, validation.errors.join(", "));
        const mappedProduct = buildChargeSpinDensityProduct(validation.bundle);
        const mappedPotential = buildElectrostaticPotentialProduct(validation.bundle);
        const selected = validation.bundle.fields.find((item) => item.supported && item.field.fieldId === (mappedPotential.fieldId ?? mappedProduct.defaultFieldId)) ?? getSupportedField(validation.bundle.fields);
        if (!selected) { setBundle(validation.bundle); setState("empty"); setMessage("No real scalar node-sampled field is compatible with isosurface extraction."); return; }
        const mappedOverlay = overlayValue ? mapVolumetricStructureOverlay(overlayValue, validation.bundle) : null;
        if (mappedOverlay && !mappedOverlay.ok) throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", mappedOverlay.errors.join(", "));
        if (revision !== revisionRef.current) return;
        setBundle(validation.bundle); setProduct(mappedProduct); setPotentialProduct(mappedPotential); setActiveField(selected); setFieldId(selected.field.fieldId);
        setOverlay(mappedOverlay && mappedOverlay.ok ? mappedOverlay.overlay : null);
        const nextLayers = defaultLayers(selected);
        setLayers(nextLayers); setLayerVisibility(Object.fromEntries(nextLayers.map((layer) => [layer.layerId, true])));
      } catch (error) {
        if (controller.signal.aborted || revision !== revisionRef.current) return;
        setState(error instanceof VolumetricViewerError && error.code === "VOLUME_VIEWER_WORKER_UNAVAILABLE" ? "unsupported" : "error");
        setMessage(error instanceof Error ? error.message : "Volumetric artifacts could not be loaded safely.");
      }
    })();
    return () => { controller.abort(); engineRef.current?.dispose(); engineRef.current = null; setEngineReady(false); workerRef.current?.dispose(); workerRef.current = null; };
  }, [key, capabilityOverride, byteLoader]);

  useEffect(() => {
    if (!bundle || !activeField || !layers.length) return;
    const revision = ++revisionRef.current;
    const controller = new AbortController();
    setState("loading"); setMessage("Extracting bounded isosurfaces in an application-owned Worker...");
    void (async () => {
      try {
        const decoded = await loadDecodedVolumetricField({ field: activeField.field, payload: activeField.payload, artifacts: artifacts.map(asVolumetric), signal: controller.signal, loader: byteLoader });
        const isPotential = Boolean(potentialProduct?.fieldId === activeField.field.fieldId);
        if (isPotential) setPotentialValues(decodePotentialValues(decoded.buffer.slice(0), activeField.payload.dtype));
        const client = new IsosurfaceWorkerClient(workerFactory); workerRef.current = client;
        const result = await client.extract({ type: "extract", fieldId: activeField.field.fieldId, fieldHash: activeField.field.contentHash, grid: bundle.grid, dtype: activeField.payload.dtype, fieldBuffer: decoded.buffer, computePotentialProfiles:isPotential, layers, caps: { maximumVerticesPerLayer: VOLUMETRIC_BROWSER_CAPS.maximumVerticesPerLayer, maximumTrianglesPerLayer: VOLUMETRIC_BROWSER_CAPS.maximumTrianglesPerLayer, maximumTotalVertices: VOLUMETRIC_BROWSER_CAPS.maximumTotalVertices, maximumTotalTriangles: VOLUMETRIC_BROWSER_CAPS.maximumTotalTriangles, maximumExtractionMs: VOLUMETRIC_BROWSER_CAPS.maximumExtractionMs } });
        if (controller.signal.aborted || revision !== revisionRef.current) return;
        setPotentialRawProfiles(result.potentialProfiles?.sourceValues??null); setMeshes([...result.meshes]); setMetrics({ ...result.metrics, ...(result.potentialProfiles ? { profileCalculationMs:result.potentialProfiles.calculationMs } : {}) }); setState(result.meshes.length ? "rendered" : "empty"); setMessage(result.meshes.length ? "Isosurface rendered from validated canonical field data." : "The selected isovalues do not intersect the field.");
      } catch (error) {
        if (controller.signal.aborted || revision !== revisionRef.current) return;
        setState(error instanceof VolumetricViewerError && error.code === "VOLUME_VIEWER_WORKER_UNAVAILABLE" ? "unsupported" : "error"); setMessage(error instanceof Error ? error.message : "Isosurface extraction failed safely.");
      }
    })();
    return () => { controller.abort(); workerRef.current?.cancel(); workerRef.current = null; };
  }, [bundle, activeField, layers, artifacts, byteLoader, workerFactory, potentialProduct]);

  useEffect(() => {
    if (!hostRef.current || !meshes.length || !bundle || !activeField || state === "error" || state === "unsupported") return;
    let disposed = false;
    void import("./volumetricRendererEngine").then(({ createVolumetricRendererEngine }) => {
      if (disposed || !hostRef.current) return;
      return createVolumetricRendererEngine({ container: hostRef.current, grid: bundle.grid, fieldId: activeField.field.fieldId, meshes, overlay, onSurfacePick: setPick, onAtomPick: setAtomPick, onContextLost: () => { setEngineReady(false); setState("error"); setMessage("WebGL context was lost. JSON and metadata remain available."); } }).then((engine) => { if (disposed) engine.dispose(); else { engineRef.current = engine; engine.setOpacity(opacity); engine.setStructureVisible(structureVisible); engine.setCellVisible(cellVisible); engine.setProjection(projection); engine.setProfilePlane(potentialAxisIndex(potentialAxis),selectedProfileIndex); setEngineReady(true); setState("rendered"); } });
    }).catch(() => { if (!disposed) { setState("error"); setMessage("The local renderer chunk could not be loaded."); } });
    return () => { disposed = true; engineRef.current?.dispose(); engineRef.current = null; setEngineReady(false); };
  }, [meshes, bundle, activeField, overlay]);

  useEffect(() => { engineRef.current?.setSurfaceVisible(surfaceVisible); }, [surfaceVisible]);
  useEffect(() => { engineRef.current?.setStructureVisible(structureVisible); }, [structureVisible]);
  useEffect(() => { engineRef.current?.setCellVisible(cellVisible); }, [cellVisible]);
  useEffect(() => { engineRef.current?.setOpacity(opacity); }, [opacity]);
  useEffect(() => { engineRef.current?.setProjection(projection); }, [projection]);
  useEffect(() => { engineRef.current?.setClipping(clipping, 2, 0); }, [clipping]);
  useEffect(() => { engineRef.current?.setSelection(pick); }, [pick]);
  useEffect(() => { engineRef.current?.setProfilePlane(potentialAxisIndex(potentialAxis), selectedProfileIndex); }, [potentialAxis, selectedProfileIndex]);
  useEffect(() => {
    if(!pick||!bundle||!activeField||!potentialValues||potentialProduct?.fieldId!==activeField.field.fieldId)return;
    const axis=potentialAxisIndex(potentialAxis);const coordinate=samplePotential(potentialValues,bundle.grid,activeField.field,pick.cartesianPosition,0).gridCoordinate[axis];
    setSelectedProfileIndex(Math.max(0,Math.min(bundle.grid.shape[axis]-1,Math.round(coordinate))));
  },[pick,bundle,activeField,potentialValues,potentialProduct,potentialAxis]);

  const selectField = (nextFieldId: string) => {
    const selected = bundle?.fields.find((item) => item.supported && item.field.fieldId === nextFieldId);
    if (!selected) return;
    setActiveField(selected); setFieldId(nextFieldId); setPick(null); setAtomPick(null); setPotentialValues(null); setPotentialRawProfiles(null); setPotentialPoints([null, null]); setPotentialGauge("source_native"); setSelectedProfileIndex(null); setHoveredProfileIndex(null); setProfileWindow([0,1]);
    const nextLayers = defaultLayers(selected);
    setLayers(nextLayers); setLayerVisibility(Object.fromEntries(nextLayers.map((layer) => [layer.layerId, true])));
  };

  const updateLayer = (layerId: string, value: number) => setLayers((current) => current.map((layer) => {
    const sourceValue = potentialField ? value-currentShift : value;
    if (layer.layerId === layerId) return { ...layer, isovalue: sourceValue };
    if (!potentialField && symmetricThreshold && current.length === 2 && Math.sign(layer.isovalue) !== Math.sign(value)) return { ...layer, isovalue: -value };
    return layer;
  }));
  const applyPreset = (absoluteIsovalue: number) => {
    if (!activeField) return;
    const signed = activeField.field.spin?.channel === "spin_difference" || (activeField.field.minimum < 0 && activeField.field.maximum > 0);
    const next = signed ? pairedLayers(absoluteIsovalue) : [{ layerId:"surface-1", isovalue:absoluteIsovalue, sign:"positive" as const }];
    setLayers(next); setLayerVisibility(Object.fromEntries(next.map((layer) => [layer.layerId, true])));
  };
  const addLayer = () => { if (layers.length >= VOLUMETRIC_BROWSER_CAPS.maximumLayers || !activeField) return; const value = activeField.field.minimum + (activeField.field.maximum - activeField.field.minimum) * 0.5; const layerId = `surface-${layers.length + 1}`; setLayers((current) => [...current, { layerId, isovalue: value, sign: value < 0 ? "negative" : "positive" }]); setLayerVisibility((current) => ({ ...current, [layerId]: true })); };
  const toggleLayer = (layerId: string) => setLayerVisibility((current) => { const visible = current[layerId] !== false; engineRef.current?.setLayerVisible(layerId, !visible); return { ...current, [layerId]: !visible }; });
  const downloadPng = async () => { try { const blob = await engineRef.current?.exportPng(1200, 900, 1); if (!blob) return; const url = URL.createObjectURL(blob); const link = document.createElement("a"); link.href = url; link.download = "volumetric-isosurface.png"; link.click(); setTimeout(() => URL.revokeObjectURL(url), 0); } catch { setMessage("PNG export exceeded the bounded local pixel budget."); } };
  const potentialField = potentialProduct?.fieldId && activeField?.field.fieldId === potentialProduct.fieldId ? activeField.field : null;
  const selectedReference = potentialField && potentialValues && potentialPoints[0] && bundle ? samplePotential(potentialValues, bundle.grid, potentialField, potentialPoints[0], 0).sourceValue : null;
  const gaugeView = potentialField&&bundle ? potentialGaugeView(potentialField,bundle.grid,potentialGauge,selectedReference) : null;
  const currentShift = gaugeView?.shift??0;
  const pointSamples: readonly (PotentialSample | null)[] = potentialField && potentialValues && bundle ? potentialPoints.map((point) => point ? samplePotential(potentialValues, bundle.grid, potentialField, point, currentShift) : null) : [null, null];
  const profiles = potentialField && potentialRawProfiles && bundle ? profilesFromRaw(potentialRawProfiles, bundle.grid, potentialField, potentialGauge, currentShift) : [];
  const potentialLayers = potentialField ? layers.map((layer)=>potentialSurfaceLayer(layer.layerId,layer.isovalue,potentialField,potentialGauge,currentShift)) : [];
  const pickedPotentialLayer = pick ? potentialLayers.find((layer) => layer.layerId === pick.layerId) ?? null : null;
  const activeProfile = profiles.find((profile)=>profile.axis===potentialAxis)??null;
  const visibleProfilePoints = activeProfile?.points.filter((point)=>point.fractional>=profileWindow[0]&&point.fractional<=profileWindow[1])??[];
  const inspectedProfilePoint = activeProfile?.points[hoveredProfileIndex??selectedProfileIndex??-1]??null;
  const selectProfilePoint=(index:number)=>setSelectedProfileIndex(Number.isSafeInteger(index)&&activeProfile&&index>=0&&index<activeProfile.points.length?index:null);
  const moveProfileWindow=(direction:-1|1)=>setProfileWindow(([start,end])=>{const width=end-start,delta=width*.25*direction;const nextStart=Math.max(0,Math.min(1-width,start+delta));return [nextStart,nextStart+width];});
  const zoomProfile=()=>setProfileWindow(([start,end])=>{const center=selectedProfileIndex!==null&&activeProfile?activeProfile.points[selectedProfileIndex].fractional:(start+end)/2;const width=Math.max((end-start)/2,.05);const nextStart=Math.max(0,Math.min(1-width,center-width/2));return [nextStart,nextStart+width];});
  const gridCenter: readonly [number,number,number] | null = bundle ? [0,1,2].map((component)=>bundle.grid.origin[component]+bundle.grid.stepMatrix.reduce((sum,row,axis)=>sum+row[component]*bundle.grid.shape[axis]*0.5,0)) as [number,number,number] : null;

  const statusClass = state === "rendered" ? "success" : state === "error" || state === "unsupported" ? "warning" : "notice";
  return <section className="viewer-renderer-surface volumetric-isosurface-surface" aria-label="Interactive volumetric isosurface renderer" data-testid="volumetric-isosurface-surface">
    <div className="viewer-renderer-toolbar"><div><strong>Validated isosurface</strong><span data-testid="volumetric-renderer-state">{state}</span></div><div className="viewer-renderer-controls"><button type="button" onClick={() => engineRef.current?.resetCamera()} disabled={!engineReady}>Reset camera</button><button type="button" onClick={() => engineRef.current?.fitSurface()} disabled={!engineReady}>Fit surface</button><button type="button" onClick={downloadPng} disabled={!engineReady}>Download PNG</button></div></div>
    <p className={statusClass} role="status" aria-live="polite" data-testid="volumetric-renderer-status">{message}</p>
    {bundle && activeField ? <div className="viewer-preview-grid"><div><dl className="mini-grid"><dt>source</dt><dd>{bundle.sourceFormat}</dd><dt>field</dt><dd>{activeField.field.fieldName}</dd><dt>quantity</dt><dd>{activeField.field.quantity}</dd><dt>unit</dt><dd>{activeField.field.unit}</dd><dt>normalization</dt><dd>{activeField.field.normalizationSemantics}</dd><dt>grid</dt><dd>{bundle.grid.shape.join(" x ")} / {bundle.grid.periodic ? "periodic" : "affine"}</dd><dt>range</dt><dd>{activeField.field.minimum} to {activeField.field.maximum}</dd></dl></div><div><label>Field <select data-testid="volumetric-field-selector" value={fieldId} onChange={(event) => selectField(event.target.value)}>{bundle.fields.map((item) => <option key={item.field.fieldId} value={item.field.fieldId} disabled={!item.supported}>{item.field.fieldName}{item.supported ? "" : " (unsupported)"}</option>)}</select></label><label>Projection <select value={projection} onChange={(event) => setProjection(event.target.value as typeof projection)}><option value="perspective">Perspective</option><option value="orthographic">Orthographic</option></select></label><label>Opacity <input type="range" min="0.1" max="0.9" step="0.01" value={opacity} onChange={(event) => setOpacity(Number(event.target.value))} /></label></div></div> : null}
    {product && bundle && potentialProduct?.status !== "ready" ? <section className="volumetric-product-panel" aria-label="Charge and spin density scientific summary" data-testid="charge-spin-density-product">
      <div data-testid="charge-spin-product-header"><strong>{product.title}</strong><span aria-label={`Product status ${product.status}`}>{product.status}</span></div>
      {Object.keys(product.modeFieldIds).length ? <label>Density mode <select data-testid="charge-spin-mode" value={Object.entries(product.modeFieldIds).find(([,id]) => id === fieldId)?.[0] ?? ""} onChange={(event) => selectField(product.modeFieldIds[event.target.value])}>{Object.keys(product.modeFieldIds).map((mode) => <option key={mode} value={mode}>{mode.replaceAll("_", " ")}</option>)}</select></label> : null}
      <div className="viewer-renderer-controls" data-testid="charge-spin-presets">{product.presets.map((preset) => <button type="button" key={preset.id} onClick={() => applyPreset(preset.absoluteIsovalue)}>{preset.label} ({format(preset.absoluteIsovalue)} {activeField?.field.unit})</button>)}</div>
      {activeField?.field.spin?.channel === "spin_difference" ? <label><input type="checkbox" checked={symmetricThreshold} onChange={(event) => setSymmetricThreshold(event.target.checked)} /> Symmetric threshold lock</label> : null}
      {!symmetricThreshold && activeField?.field.spin?.channel === "spin_difference" ? <p className="warning">Asymmetric visualization thresholds do not imply physical asymmetry.</p> : null}
      <table data-testid="charge-spin-integrals"><caption>Full-cell integrals from canonical grid samples</caption><thead><tr><th>Field</th><th>Integral</th><th>Unit</th><th>Semantics</th></tr></thead><tbody>{product.integralRows.map((row) => <tr key={row.fieldId}><td>{row.label}</td><td>{format(row.value)}</td><td>{row.unit}</td><td>{row.interpretation}</td></tr>)}</tbody></table>
      <p className="empty-state">Reference comparison: no authoritative source reference is available. Grid integrals are full-cell values, not atomic charges or enclosed-isosurface electron counts.</p>
      {product.formulaIds.length ? <p data-testid="charge-spin-formulas">Derived formulas: {product.formulaIds.join(", ")}</p> : null}
      {product.warnings.map((warning) => <p className="warning" key={warning}>{warning === "VOLUME_VASP_AUGMENTATION_NOT_INCLUDED" ? "Grid integral may not include all augmentation contributions." : warning}</p>)}
    </section> : null}
    {potentialProduct?.status === "ready" && potentialField && bundle ? <section className="volumetric-product-panel potential-product-panel" aria-label="Electrostatic potential product" data-testid="electrostatic-potential-product">
      <div data-testid="potential-product-header"><strong>{potentialProduct.title}</strong><span>{potentialProduct.status}</span></div>
      <dl className="mini-grid"><dt>quantity</dt><dd data-testid="potential-quantity">{potentialProduct.quantity}</dd><dt>unit</dt><dd data-testid="potential-unit">{potentialProduct.unit}</dd><dt>reference</dt><dd data-testid="potential-reference">{potentialField.potentialReference?.kind}</dd><dt>display shift</dt><dd data-testid="potential-shift">{format(currentShift)} {potentialProduct.unit}</dd><dt>gauge formula</dt><dd data-testid="potential-gauge-formula">{gaugeView?.formulaId}</dd><dt>source field hash</dt><dd>{potentialField.contentHash}</dd></dl>
      <div className="potential-product-controls"><label>Gauge <select data-testid="potential-gauge" value={potentialGauge} onChange={(event) => setPotentialGauge(event.target.value as PotentialGaugeMode)}><option value="source_native">Source native</option><option value="cell_average_zero">Cell-average zero</option><option value="selected_point_zero" disabled={!potentialPoints[0]}>Selected point zero</option></select></label><button type="button" data-testid="potential-gauge-reset" onClick={() => setPotentialGauge("source_native")}>Reset gauge</button><label>Profile axis <select data-testid="potential-profile-axis" value={potentialAxis} onChange={(event) => {setPotentialAxis(event.target.value as PotentialAxis);setSelectedProfileIndex(null);setHoveredProfileIndex(null);setProfileWindow([0,1]);}}><option value="lattice_axis_0">a / lattice axis 0</option><option value="lattice_axis_1">b / lattice axis 1</option><option value="lattice_axis_2">c / lattice axis 2</option></select></label></div>
      <dl className="mini-grid" data-testid="potential-statistics"><dt>source range</dt><dd>{format(gaugeView?.sourceMinimum??potentialField.minimum)} to {format(gaugeView?.sourceMaximum??potentialField.maximum)} {potentialField.unit}</dd><dt>displayed range</dt><dd>{format(gaugeView?.displayedMinimum??potentialField.minimum)} to {format(gaugeView?.displayedMaximum??potentialField.maximum)} {potentialField.unit}</dd><dt>source mean / cell average</dt><dd>{format(gaugeView?.sourceMean??potentialField.mean)} {potentialField.unit}</dd><dt>displayed mean</dt><dd>{format(gaugeView?.displayedMean??potentialField.mean)} {potentialField.unit}</dd><dt>standard deviation (gauge invariant)</dt><dd>{format(potentialField.standardDeviation)} {potentialField.unit}</dd><dt>source / displayed RMS</dt><dd>{format(potentialField.rms)} / {format(gaugeView?.displayedRms??potentialField.rms)} {potentialField.unit}</dd><dt>source volume integral</dt><dd>{format(potentialField.integral)} {potentialField.unit}·Å³</dd><dt>displayed volume integral</dt><dd>{format(gaugeView?.displayedVolumeIntegral??potentialField.integral)} {potentialField.unit}·Å³</dd></dl>
      <div className="potential-product-controls"><button type="button" data-testid="potential-point-a" disabled={!pick} onClick={() => pick && setPotentialPoints(([_, b]) => [pick.cartesianPosition as [number,number,number], b])}>Use surface pick as A</button><button type="button" data-testid="potential-point-b" disabled={!pick} onClick={() => pick && setPotentialPoints(([a, _]) => [a, pick.cartesianPosition as [number,number,number]])}>Use surface pick as B</button><button type="button" data-testid="potential-grid-point-a" onClick={() => setPotentialPoints(([_, b]) => [bundle.grid.origin, b])}>Use grid origin as A</button><button type="button" data-testid="potential-grid-point-b" disabled={!gridCenter} onClick={() => gridCenter && setPotentialPoints(([a, _]) => [a, gridCenter])}>Use cell center as B</button><button type="button" data-testid="potential-points-clear" onClick={() => { setPotentialPoints([null, null]); setPotentialGauge("source_native"); }}>Clear points</button></div>
      <div data-testid="potential-point-inspector"><strong>Point inspector</strong>{pointSamples.map((sample,index) => sample ? <p key={index}>Point {index===0?"A":"B"}: source {format(sample.sourceValue)} {sample.unit}; displayed {format(sample.displayedValue)} {sample.unit}; Cartesian ({sample.cartesian.map(format).join(", ")}); fractional {sample.fractional ? `(${sample.fractional.map(format).join(", ")})` : "not periodic"}; {sample.interpolation}; image {sample.imageOffset.join(",")}</p> : <p key={index}>Point {index===0?"A":"B"}: not selected.</p>)}{potentialGauge==="selected_point_zero"&&pointSamples[0]?<p data-testid="potential-selected-reference">Display reference A uses source {format(pointSamples[0].sourceValue)} {pointSamples[0].unit} at Cartesian ({pointSamples[0].cartesian.map(format).join(", ")}), fractional {pointSamples[0].fractional ? `(${pointSamples[0].fractional.map(format).join(", ")})` : "not periodic"}, image {pointSamples[0].imageOffset.join(",")}, via {pointSamples[0].interpolation}; this is not a physical zero.</p>:null}{pointSamples[0]&&pointSamples[1]?<p data-testid="potential-point-difference">ΔV = {format(potentialDifference(pointSamples[0],pointSamples[1]).value)} {potentialProduct.unit}; gauge invariant; field {potentialField.contentHash}; A/B use {pointSamples[0].interpolation}.</p>:null}</div>
      <div data-testid="potential-profile-panel"><div className="viewer-renderer-toolbar"><div><strong>Raw planar average along lattice axis</strong><span>{activeProfile?.formulaId??"loading"}</span></div><div className="viewer-renderer-controls"><button type="button" onClick={zoomProfile} disabled={!activeProfile}>Zoom in</button><button type="button" onClick={()=>moveProfileWindow(-1)} disabled={profileWindow[0]===0}>Pan left</button><button type="button" onClick={()=>moveProfileWindow(1)} disabled={profileWindow[1]===1}>Pan right</button><button type="button" onClick={()=>setProfileWindow([0,1])}>Reset profile</button><button type="button" onClick={()=>selectProfilePoint(-1)} disabled={selectedProfileIndex===null}>Clear plane</button></div></div><svg className="potential-profile-chart" data-testid="potential-profile-chart" viewBox="0 0 320 120" role="img" aria-label={`Raw planar average for ${potentialAxis}. Use left and right arrow keys to select a plane.`} tabIndex={0} onKeyDown={(event)=>{if(!activeProfile)return;if(event.key==="ArrowRight"||event.key==="ArrowLeft"){event.preventDefault();const delta=event.key==="ArrowRight"?1:-1;selectProfilePoint(Math.max(0,Math.min(activeProfile.points.length-1,(selectedProfileIndex??0)+delta)));}}} onPointerMove={(event)=>{if(!activeProfile)return;const box=event.currentTarget.getBoundingClientRect();const ratio=Math.max(0,Math.min(1,(event.clientX-box.left)/box.width));setHoveredProfileIndex(Math.min(activeProfile.points.length-1,Math.round(ratio*(activeProfile.points.length-1))));}} onPointerLeave={()=>setHoveredProfileIndex(null)} onClick={()=>{if(hoveredProfileIndex!==null)selectProfilePoint(hoveredProfileIndex);}}><line x1="20" y1="100" x2="305" y2="100" /><line x1="20" y1="10" x2="20" y2="100" /><polyline points={profilePolyline(visibleProfilePoints.map((point)=>point.displayedValue))} /></svg>{inspectedProfilePoint?<p role="status" aria-live="polite" data-testid="potential-profile-selection">Plane {inspectedProfilePoint.index}; fraction {inspectedProfilePoint.fractional.toFixed(6)}; path {inspectedProfilePoint.pathLengthAngstrom.toFixed(6)} Å; source {format(inspectedProfilePoint.sourceValue)} {potentialField.unit}; displayed {format(inspectedProfilePoint.displayedValue)} {potentialField.unit}.</p>:null}<p data-testid="potential-profile-identity">Profile hash {activeProfile?.profileHash??"loading"}; field {potentialField.contentHash}; gauge {potentialGauge}; window {profileWindow[0].toFixed(3)}–{profileWindow[1].toFixed(3)}.</p><table><thead><tr><th>Index</th><th>Fraction</th><th>Path Å</th><th>Source</th><th>Displayed</th><th>3D plane</th></tr></thead><tbody>{activeProfile?.points.map((point)=><tr key={point.index} aria-selected={selectedProfileIndex===point.index}><td>{point.index}</td><td>{point.fractional.toFixed(6)}</td><td>{point.pathLengthAngstrom.toFixed(6)}</td><td>{format(point.sourceValue)}</td><td>{format(point.displayedValue)}</td><td><button type="button" aria-pressed={selectedProfileIndex===point.index} onClick={()=>selectProfilePoint(point.index)}>Show plane {point.index}</button></td></tr>)}</tbody></table><p className="empty-state">Arithmetic mean over the two orthogonal grid axes; no smoothing. Lattice-axis path length is not a Cartesian plane-normal distance.</p></div>
      {potentialProduct.warnings.map((warning)=><p className="warning" key={warning}>{warning}</p>)}
    </section> : null}
    <div className="volumetric-layer-controls" data-testid="volumetric-isovalue-controls"><strong>Isovalues</strong>{layers.map((layer) => {const identity=potentialLayers.find((item)=>item.layerId===layer.layerId);return <div className="viewer-renderer-controls" key={layer.layerId}><label>{layer.sign} <input aria-label={`${layer.layerId} isovalue`} type="number" value={identity?.displayedIsovalue??layer.isovalue} onChange={(event) => updateLayer(layer.layerId, Number(event.target.value))} /></label>{identity?<span data-testid="potential-layer-identity">source {format(identity.sourceIsovalue)} / displayed {format(identity.displayedIsovalue)} {identity.unit}</span>:null}<button type="button" aria-pressed={layerVisibility[layer.layerId] !== false} onClick={() => toggleLayer(layer.layerId)}>Toggle</button>{layers.length > 1 ? <button type="button" onClick={() => { setLayers((current) => current.filter((item) => item.layerId !== layer.layerId)); setLayerVisibility((current) => { const next = { ...current }; delete next[layer.layerId]; return next; }); }}>Remove</button> : null}</div>;})}<button type="button" onClick={addLayer} disabled={layers.length >= VOLUMETRIC_BROWSER_CAPS.maximumLayers}>Add layer</button></div>
    <div className="viewer-renderer-controls"><button type="button" className={surfaceVisible ? "active" : "secondary"} onClick={() => setSurfaceVisible((value) => !value)}>Surface</button><button type="button" className={structureVisible ? "active" : "secondary"} onClick={() => setStructureVisible((value) => !value)}>Structure</button><button type="button" className={cellVisible ? "active" : "secondary"} onClick={() => setCellVisible((value) => !value)}>Cell</button><button type="button" className={clipping ? "active" : "secondary"} onClick={() => setClipping((value) => !value)}>Clip</button></div>
    {metrics ? <dl className="mini-grid" data-testid="volumetric-renderer-metrics"><dt>vertices</dt><dd>{metrics.vertices}</dd><dt>triangles</dt><dd>{metrics.triangles}</dd><dt>extraction ms</dt><dd data-testid="volumetric-extraction-ms">{metrics.extractionMs}</dd>{Number.isFinite(metrics.profileCalculationMs)?<><dt>profile calculation ms</dt><dd data-testid="potential-profile-calculation-ms">{metrics.profileCalculationMs}</dd></>:null}</dl> : null}
    {pick ? <p className="notice" data-testid="volumetric-surface-inspector">Surface {pick.layerId}, {pickedPotentialLayer ? <>source isovalue {format(pickedPotentialLayer.sourceIsovalue)} / displayed isovalue {format(pickedPotentialLayer.displayedIsovalue)} {pickedPotentialLayer.unit}</> : <>isovalue {pick.isovalue}</>}, triangle {pick.triangleIndex}, position {pick.cartesianPosition.map((value) => value.toFixed(3)).join(", ")}, mesh {pick.meshHash}</p> : null}
    {atomPick !== null ? <p className="notice" data-testid="volumetric-atom-inspector">Structure site {atomPick} selected.</p> : null}
    <div ref={hostRef} className="viewer-renderer-canvas-host" data-testid="volumetric-renderer-canvas-host" aria-label="Volumetric graphics canvas" />
    <p className="empty-state">The renderer consumes validated scalar field data only. No artifact code, shader, URL, or external asset is executed.</p>
  </section>;
}

function getSupportedField(fields: readonly VolumetricFieldCompatibility[]): VolumetricFieldCompatibility | null { return fields.find((item) => item.supported) ?? null; }
function pairedLayers(value:number):IsosurfaceLayerRequest[]{const magnitude=Math.max(Math.abs(value),Number.EPSILON);return [{layerId:"positive-1",isovalue:magnitude,sign:"positive"},{layerId:"negative-1",isovalue:-magnitude,sign:"negative"}];}
function defaultLayers(field:VolumetricFieldCompatibility):IsosurfaceLayerRequest[]{const range=Math.max(Math.abs(field.field.minimum),Math.abs(field.field.maximum));const span=field.field.maximum-field.field.minimum;const potential=["local_potential","electrostatic_potential"].includes(field.field.quantity);const signed=!potential&&(field.field.spin?.channel==="spin_difference"||(field.field.minimum<0&&field.field.maximum>0));const value=potential?field.field.mean:field.field.minimum+span*0.25;return signed?pairedLayers(range*0.25):[{layerId:"surface-1",isovalue:value,sign:value<0?"negative":"positive"}];}
function format(value:number){return Number.isFinite(value)?value.toPrecision(6):"unavailable";}
function profilePolyline(values:readonly number[]){if(!values.length)return"";const minimum=Math.min(...values),maximum=Math.max(...values),span=Math.max(maximum-minimum,Number.EPSILON);return values.map((value,index)=>`${20+(values.length===1?0:index/(values.length-1)*285)},${100-(value-minimum)/span*90}`).join(" ");}
function potentialAxisIndex(axis:PotentialAxis):0|1|2{return axis==="lattice_axis_0"?0:axis==="lattice_axis_1"?1:2;}
