"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Artifact } from "../../lib/planner-api";
import { loadDecodedVolumetricField, loadVolumetricJsonArtifact, type VolumetricByteLoader } from "./volumetricPayloadLoader";
import { IsosurfaceWorkerClient, type IsosurfaceWorkerFactory } from "./isosurfaceWorkerClient";
import { mapVolumetricStructureOverlay } from "./volumetricOverlayMapper";
import { validateVolumetricArtifacts } from "./volumetricValidation";
import { buildChargeSpinDensityProduct, type ChargeSpinDensityProduct } from "./chargeSpinDensityProduct";
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
    setMeshes([]); setPick(null); setAtomPick(null); setMetrics(null); setProduct(null); setSymmetricThreshold(true);
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
        const selected = validation.bundle.fields.find((item) => item.supported && item.field.fieldId === mappedProduct.defaultFieldId) ?? getSupportedField(validation.bundle.fields);
        if (!selected) { setBundle(validation.bundle); setState("empty"); setMessage("No real scalar node-sampled field is compatible with isosurface extraction."); return; }
        const mappedOverlay = overlayValue ? mapVolumetricStructureOverlay(overlayValue, validation.bundle) : null;
        if (mappedOverlay && !mappedOverlay.ok) throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", mappedOverlay.errors.join(", "));
        if (revision !== revisionRef.current) return;
        setBundle(validation.bundle); setProduct(mappedProduct); setActiveField(selected); setFieldId(selected.field.fieldId);
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
        const client = new IsosurfaceWorkerClient(workerFactory); workerRef.current = client;
        const result = await client.extract({ type: "extract", fieldId: activeField.field.fieldId, fieldHash: activeField.field.contentHash, grid: bundle.grid, dtype: activeField.payload.dtype, fieldBuffer: decoded.buffer, layers, caps: { maximumVerticesPerLayer: VOLUMETRIC_BROWSER_CAPS.maximumVerticesPerLayer, maximumTrianglesPerLayer: VOLUMETRIC_BROWSER_CAPS.maximumTrianglesPerLayer, maximumTotalVertices: VOLUMETRIC_BROWSER_CAPS.maximumTotalVertices, maximumTotalTriangles: VOLUMETRIC_BROWSER_CAPS.maximumTotalTriangles, maximumExtractionMs: VOLUMETRIC_BROWSER_CAPS.maximumExtractionMs } });
        if (controller.signal.aborted || revision !== revisionRef.current) return;
        setMeshes([...result.meshes]); setMetrics({ ...result.metrics }); setState(result.meshes.length ? "rendered" : "empty"); setMessage(result.meshes.length ? "Isosurface rendered from validated canonical field data." : "The selected isovalues do not intersect the field.");
      } catch (error) {
        if (controller.signal.aborted || revision !== revisionRef.current) return;
        setState(error instanceof VolumetricViewerError && error.code === "VOLUME_VIEWER_WORKER_UNAVAILABLE" ? "unsupported" : "error"); setMessage(error instanceof Error ? error.message : "Isosurface extraction failed safely.");
      }
    })();
    return () => { controller.abort(); workerRef.current?.cancel(); workerRef.current = null; };
  }, [bundle, activeField, layers, artifacts, byteLoader, workerFactory]);

  useEffect(() => {
    if (!hostRef.current || !meshes.length || !bundle || !activeField || state === "error" || state === "unsupported") return;
    let disposed = false;
    void import("./volumetricRendererEngine").then(({ createVolumetricRendererEngine }) => {
      if (disposed || !hostRef.current) return;
      return createVolumetricRendererEngine({ container: hostRef.current, grid: bundle.grid, fieldId: activeField.field.fieldId, meshes, overlay, onSurfacePick: setPick, onAtomPick: setAtomPick, onContextLost: () => { setEngineReady(false); setState("error"); setMessage("WebGL context was lost. JSON and metadata remain available."); } }).then((engine) => { if (disposed) engine.dispose(); else { engineRef.current = engine; engine.setOpacity(opacity); engine.setStructureVisible(structureVisible); engine.setCellVisible(cellVisible); engine.setProjection(projection); setEngineReady(true); setState("rendered"); } });
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

  const selectField = (nextFieldId: string) => {
    const selected = bundle?.fields.find((item) => item.supported && item.field.fieldId === nextFieldId);
    if (!selected) return;
    setActiveField(selected); setFieldId(nextFieldId); setPick(null); setAtomPick(null);
    const nextLayers = defaultLayers(selected);
    setLayers(nextLayers); setLayerVisibility(Object.fromEntries(nextLayers.map((layer) => [layer.layerId, true])));
  };

  const updateLayer = (layerId: string, value: number) => setLayers((current) => current.map((layer) => {
    if (layer.layerId === layerId) return { ...layer, isovalue: value };
    if (symmetricThreshold && current.length === 2 && Math.sign(layer.isovalue) !== Math.sign(value)) return { ...layer, isovalue: -value };
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

  const statusClass = state === "rendered" ? "success" : state === "error" || state === "unsupported" ? "warning" : "notice";
  return <section className="viewer-renderer-surface volumetric-isosurface-surface" aria-label="Interactive volumetric isosurface renderer" data-testid="volumetric-isosurface-surface">
    <div className="viewer-renderer-toolbar"><div><strong>Validated isosurface</strong><span data-testid="volumetric-renderer-state">{state}</span></div><div className="viewer-renderer-controls"><button type="button" onClick={() => engineRef.current?.resetCamera()} disabled={!engineReady}>Reset camera</button><button type="button" onClick={() => engineRef.current?.fitSurface()} disabled={!engineReady}>Fit surface</button><button type="button" onClick={downloadPng} disabled={!engineReady}>Download PNG</button></div></div>
    <p className={statusClass} role="status" aria-live="polite" data-testid="volumetric-renderer-status">{message}</p>
    {bundle && activeField ? <div className="viewer-preview-grid"><div><dl className="mini-grid"><dt>source</dt><dd>{bundle.sourceFormat}</dd><dt>field</dt><dd>{activeField.field.fieldName}</dd><dt>quantity</dt><dd>{activeField.field.quantity}</dd><dt>unit</dt><dd>{activeField.field.unit}</dd><dt>normalization</dt><dd>{activeField.field.normalizationSemantics}</dd><dt>grid</dt><dd>{bundle.grid.shape.join(" x ")} / {bundle.grid.periodic ? "periodic" : "affine"}</dd><dt>range</dt><dd>{activeField.field.minimum} to {activeField.field.maximum}</dd></dl></div><div><label>Field <select data-testid="volumetric-field-selector" value={fieldId} onChange={(event) => selectField(event.target.value)}>{bundle.fields.map((item) => <option key={item.field.fieldId} value={item.field.fieldId} disabled={!item.supported}>{item.field.fieldName}{item.supported ? "" : " (unsupported)"}</option>)}</select></label><label>Projection <select value={projection} onChange={(event) => setProjection(event.target.value as typeof projection)}><option value="perspective">Perspective</option><option value="orthographic">Orthographic</option></select></label><label>Opacity <input type="range" min="0.1" max="0.9" step="0.01" value={opacity} onChange={(event) => setOpacity(Number(event.target.value))} /></label></div></div> : null}
    {product && bundle ? <section className="volumetric-product-panel" aria-label="Charge and spin density scientific summary" data-testid="charge-spin-density-product">
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
    <div className="volumetric-layer-controls" data-testid="volumetric-isovalue-controls"><strong>Isovalues</strong>{layers.map((layer) => <div className="viewer-renderer-controls" key={layer.layerId}><label>{layer.sign} <input aria-label={`${layer.layerId} isovalue`} type="number" value={layer.isovalue} onChange={(event) => updateLayer(layer.layerId, Number(event.target.value))} /></label><button type="button" aria-pressed={layerVisibility[layer.layerId] !== false} onClick={() => toggleLayer(layer.layerId)}>Toggle</button>{layers.length > 1 ? <button type="button" onClick={() => { setLayers((current) => current.filter((item) => item.layerId !== layer.layerId)); setLayerVisibility((current) => { const next = { ...current }; delete next[layer.layerId]; return next; }); }}>Remove</button> : null}</div>)}<button type="button" onClick={addLayer} disabled={layers.length >= VOLUMETRIC_BROWSER_CAPS.maximumLayers}>Add layer</button></div>
    <div className="viewer-renderer-controls"><button type="button" className={surfaceVisible ? "active" : "secondary"} onClick={() => setSurfaceVisible((value) => !value)}>Surface</button><button type="button" className={structureVisible ? "active" : "secondary"} onClick={() => setStructureVisible((value) => !value)}>Structure</button><button type="button" className={cellVisible ? "active" : "secondary"} onClick={() => setCellVisible((value) => !value)}>Cell</button><button type="button" className={clipping ? "active" : "secondary"} onClick={() => setClipping((value) => !value)}>Clip</button></div>
    {metrics ? <dl className="mini-grid" data-testid="volumetric-renderer-metrics"><dt>vertices</dt><dd>{metrics.vertices}</dd><dt>triangles</dt><dd>{metrics.triangles}</dd><dt>extraction ms</dt><dd>{metrics.extractionMs}</dd></dl> : null}
    {pick ? <p className="notice" data-testid="volumetric-surface-inspector">Surface {pick.layerId}, isovalue {pick.isovalue}, triangle {pick.triangleIndex}, position {pick.cartesianPosition.map((value) => value.toFixed(3)).join(", ")}</p> : null}
    {atomPick !== null ? <p className="notice" data-testid="volumetric-atom-inspector">Structure site {atomPick} selected.</p> : null}
    <div ref={hostRef} className="viewer-renderer-canvas-host" data-testid="volumetric-renderer-canvas-host" aria-label="Volumetric graphics canvas" />
    <p className="empty-state">The renderer consumes validated scalar field data only. No artifact code, shader, URL, or external asset is executed.</p>
  </section>;
}

function getSupportedField(fields: readonly VolumetricFieldCompatibility[]): VolumetricFieldCompatibility | null { return fields.find((item) => item.supported) ?? null; }
function pairedLayers(value:number):IsosurfaceLayerRequest[]{const magnitude=Math.max(Math.abs(value),Number.EPSILON);return [{layerId:"positive-1",isovalue:magnitude,sign:"positive"},{layerId:"negative-1",isovalue:-magnitude,sign:"negative"}];}
function defaultLayers(field:VolumetricFieldCompatibility):IsosurfaceLayerRequest[]{const range=Math.max(Math.abs(field.field.minimum),Math.abs(field.field.maximum));const span=field.field.maximum-field.field.minimum;const signed=field.field.spin?.channel==="spin_difference"||(field.field.minimum<0&&field.field.maximum>0);return signed?pairedLayers(range*0.25):[{layerId:"surface-1",isovalue:field.field.minimum+span*0.25,sign:field.field.minimum>=0?"positive":"negative"}];}
function format(value:number){return Number.isFinite(value)?value.toPrecision(6):"unavailable";}
