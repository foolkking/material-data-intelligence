"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Artifact } from "../../lib/planner-api";
import { loadDecodedVolumetricField, loadVolumetricJsonArtifact, type VolumetricByteLoader } from "./volumetricPayloadLoader";
import { mapVolumetricStructureOverlay } from "./volumetricOverlayMapper";
import { fractionalToWorld, probeCanonicalValues } from "./volumetricSliceModel";
import { sliceRgba } from "./volumetricSliceDisplay";
import type { VolumetricSliceRendererEngine } from "./volumetricSliceRendererEngine";
import { createAnnotatedVolumetricPng } from "./volumetricPngExport";
import { VolumetricSliceWorkerClient, type VolumetricSliceWorkerFactory } from "./volumetricSliceWorkerClient";
import { defaultTransferFunction, preflightVolumeMetadata, prepareVolumeTexture, validateTransferFunction, VOLUME_QUALITY_PRESETS } from "./volumetricVolumeModel";
import { validateVolumetricArtifacts } from "./volumetricValidation";
import type { DecodedVolumetricField, ValidatedVolumetricBundle, VolumeGpuCapabilities, VolumeQuality, VolumeTexturePrecision, VolumeTransferFunction, VolumeVector3, VolumetricArtifact, VolumetricFieldCompatibility, VolumetricSlice, VolumetricSliceAxis, VolumetricStructureOverlay, VolumetricVolumeRendererEngine } from "./volumetricViewerTypes";
import { VOLUMETRIC_BROWSER_CAPS, VolumetricViewerError } from "./volumetricViewerTypes";

type Props = Readonly<{
  artifacts: Artifact[];
  mode: "slice" | "volume";
  capabilityOverride?: "supported" | "unsupported";
  byteLoader?: VolumetricByteLoader;
  sliceWorkerFactory?: VolumetricSliceWorkerFactory;
}>;
type ProductState = "loading" | "ready" | "unsupported" | "error";
type SlicePointProbe = Readonly<{
  value: number;
  fractional: VolumeVector3;
  cartesian: VolumeVector3;
  row: number;
  column: number;
  sliceCoordinates: readonly [number, number];
  displayedNormalizedValue: number;
}>;
const SLICE_TABLE_PAGE_SIZE = 64;

export function VolumetricSliceVolumeSurface({ artifacts, mode, capabilityOverride, byteLoader, sliceWorkerFactory }: Props) {
  const datasetArtifact = artifacts.find((item) => item.type === "volumetric_dataset_json");
  const manifestArtifact = artifacts.find((item) => item.type === "volumetric_manifest_json");
  const overlayArtifact = artifacts.find((item) => item.type === "volumetric_structure_overlay_json");
  const [state, setState] = useState<ProductState>("loading");
  const [message, setMessage] = useState("Validating canonical volumetric field...");
  const [bundle, setBundle] = useState<ValidatedVolumetricBundle | null>(null);
  const [active, setActive] = useState<VolumetricFieldCompatibility | null>(null);
  const [decoded, setDecoded] = useState<DecodedVolumetricField | null>(null);
  const [overlay, setOverlay] = useState<VolumetricStructureOverlay | null>(null);
  const [axis, setAxis] = useState<VolumetricSliceAxis>(2);
  const [position, setPosition] = useState(0.5);
  const [slice, setSlice] = useState<VolumetricSlice | null>(null);
  const [sliceCalculationMs, setSliceCalculationMs] = useState(0);
  const [sliceView, setSliceView] = useState<"2d" | "3d">("2d");
  const [probe, setProbe] = useState<SlicePointProbe | null>(null);
  const [transfer, setTransfer] = useState<VolumeTransferFunction | null>(null);
  const [quality, setQuality] = useState<VolumeQuality>(VOLUME_QUALITY_PRESETS.balanced);
  const [precision, setPrecision] = useState<VolumeTexturePrecision | null>(null);
  const [gpuValues, setGpuValues] = useState<Float32Array | null>(null);
  const [capabilities, setCapabilities] = useState<VolumeGpuCapabilities | null>(null);
  const [structureVisible, setStructureVisible] = useState(true);
  const [cellVisible, setCellVisible] = useState(true);
  const [clipping, setClipping] = useState(false);
  const [clipOffset, setClipOffset] = useState(1);
  const [projection, setProjection] = useState<"perspective" | "orthographic">("perspective");
  const [volumeSnapshot, setVolumeSnapshot] = useState<Record<string, unknown> | null>(null);
  const [sliceTablePage, setSliceTablePage] = useState(0);
  const [heatmapZoom, setHeatmapZoom] = useState(1);
  const heatmapRef = useRef<HTMLCanvasElement>(null);
  const heatmapWrapRef = useRef<HTMLDivElement>(null);
  const hostRef = useRef<HTMLDivElement>(null);
  const sliceEngineRef = useRef<VolumetricSliceRendererEngine | null>(null);
  const volumeEngineRef = useRef<VolumetricVolumeRendererEngine | null>(null);
  const sliceWorkerRef = useRef<VolumetricSliceWorkerClient | null>(null);
  const revisionRef = useRef(0);
  const artifactKey = [datasetArtifact, manifestArtifact, overlayArtifact].map((item) => String(item?.id || item?.artifactId || item?.name || "missing")).join(":");

  useEffect(() => {
    const revision = ++revisionRef.current; const controller = new AbortController(); cleanupEngines(); sliceWorkerRef.current?.dispose(); sliceWorkerRef.current = null;
    setState("loading"); setMessage("Validating canonical volumetric field..."); setBundle(null); setActive(null); setDecoded(null); setOverlay(null); setSlice(null); setProbe(null); setPrecision(null); setGpuValues(null); setCapabilities(null);
    if (!datasetArtifact || !manifestArtifact) { setState("error"); setMessage("Required volumetric dataset and manifest are unavailable."); return () => controller.abort(); }
    void (async () => {
      try {
        const [dataset, manifest, overlayValue] = await Promise.all([
          loadVolumetricJsonArtifact(datasetArtifact as unknown as VolumetricArtifact, { signal: controller.signal, loader: byteLoader }),
          loadVolumetricJsonArtifact(manifestArtifact as unknown as VolumetricArtifact, { signal: controller.signal, loader: byteLoader }),
          overlayArtifact ? loadVolumetricJsonArtifact(overlayArtifact as unknown as VolumetricArtifact, { signal: controller.signal, loader: byteLoader }) : Promise.resolve(null),
        ]);
        const validation = validateVolumetricArtifacts(dataset, manifest);
        if (!validation.ok) throw new VolumetricViewerError(validation.code, validation.errors.join(", "));
        const selected = validation.bundle.fields.find((item) => item.supported) ?? null;
        if (!selected) throw new VolumetricViewerError("VOLUME_VIEWER_FIELD_UNSUPPORTED", "Slice and volume require a real scalar node-sampled field.");
        const mappedOverlay = overlayValue ? mapVolumetricStructureOverlay(overlayValue, validation.bundle) : null;
        if (mappedOverlay && !mappedOverlay.ok) throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", mappedOverlay.errors.join(", "));
        if (controller.signal.aborted || revision !== revisionRef.current) return;
        setBundle(validation.bundle); setActive(selected); setTransfer(defaultTransferFunction(selected.field)); setOverlay(mappedOverlay?.ok ? mappedOverlay.overlay : null); setState("loading"); setMessage("Loading and verifying the selected field payload...");
      } catch (error) { if (!controller.signal.aborted && revision === revisionRef.current) { setState("error"); setMessage(safeMessage(error)); } }
    })();
    return () => { controller.abort(); cleanupEngines(); sliceWorkerRef.current?.dispose(); sliceWorkerRef.current = null; };
  }, [artifactKey, byteLoader]);

  useEffect(() => {
    if (!bundle || !active) return;
    if (mode === "volume" && capabilityOverride === "unsupported") { cleanupEngines(); setDecoded(null); setGpuValues(null); setCapabilities(null); setState("unsupported"); setMessage("WebGL2 direct volume rendering is unavailable. Slice and Isosurface remain available."); return; }
    if (mode === "volume") {
      const metadata = preflightVolumeMetadata(bundle.grid.shape, typeof matchMedia === "function" && matchMedia("(max-width: 700px)").matches);
      if (!metadata.supported) { cleanupEngines(); setDecoded(null); setGpuValues(null); setCapabilities(null); setState("unsupported"); setMessage(`Direct volume rendering refused before payload allocation: ${metadata.reason}. Slice and Isosurface remain available.`); return; }
    }
    const revision = ++revisionRef.current; const controller = new AbortController(); cleanupEngines(); sliceWorkerRef.current?.cancel(); setDecoded(null); setSlice(null); setProbe(null); setPrecision(null); setGpuValues(null); setCapabilities(null); setState("loading"); setMessage("Loading and verifying the selected field payload...");
    void loadDecodedVolumetricField({ field: active.field, payload: active.payload, artifacts: artifacts as unknown as VolumetricArtifact[], signal: controller.signal, loader: byteLoader }).then(async (value) => {
      const prepared = mode === "volume" ? await prepareVolumeTexture({ buffer: value.buffer, dtype: value.payload.dtype, valueCount: value.payload.valueCount }) : null;
      if (controller.signal.aborted || revision !== revisionRef.current) return;
      setDecoded(value); setGpuValues(prepared?.values ?? null); setPrecision(prepared?.precision ?? null); setTransfer(defaultTransferFunction(active.field)); setState("loading"); setMessage("Canonical field payload verified; initializing the selected product.");
    }).catch((error) => { if (!controller.signal.aborted && revision === revisionRef.current) { setState("error"); setMessage(safeMessage(error)); } });
    return () => controller.abort();
  }, [mode, bundle, active, artifacts, byteLoader, capabilityOverride]);

  useEffect(() => {
    if (mode !== "slice") { sliceWorkerRef.current?.cancel(); return; }
    if (!bundle || !active || !decoded || typeof Worker === "undefined" || capabilityOverride === "unsupported") { if (decoded) { setState("unsupported"); setMessage("Application-owned slice Worker is unavailable; Isosurface and metadata remain available."); } return; }
    const revision = ++revisionRef.current; const client = sliceWorkerRef.current ?? new VolumetricSliceWorkerClient(sliceWorkerFactory); sliceWorkerRef.current = client; setState("loading"); setMessage("Sampling canonical lattice slice in an application-owned Worker...");
    void client.sample({ type: "slice", datasetHash: bundle.datasetContentHash, fieldHash: active.field.contentHash, unit: active.field.unit, grid: bundle.grid, dtype: active.payload.dtype, fieldBuffer: decoded.buffer.slice(0), axis, fractionalPosition: position, maximumOutputValues: VOLUMETRIC_BROWSER_CAPS.maximumSliceValues }).then((result) => {
      if (revision !== revisionRef.current) return; setSlice(result.slice); setSliceCalculationMs(result.calculationMs); setProbe(null); setState("ready"); setMessage(`${result.slice.samplingMode === "exact_grid_plane" ? "Exact" : "Interpolated"} lattice-axis slice ready.`);
    }).catch((error) => { if (revision === revisionRef.current) { setState(error instanceof VolumetricViewerError && error.code === "VOLUME_VIEWER_WORKER_UNAVAILABLE" ? "unsupported" : "error"); setMessage(safeMessage(error)); } });
  }, [mode, bundle, active, decoded, axis, position, sliceWorkerFactory, capabilityOverride]);

  useEffect(() => {
    sliceEngineRef.current?.dispose(); sliceEngineRef.current = null;
    if (mode !== "slice" || sliceView !== "3d" || !slice || !transfer || !hostRef.current) return;
    let cancelled = false;
    void import("./volumetricSliceRendererEngine").then(({ createVolumetricSliceRendererEngine }) => createVolumetricSliceRendererEngine({ container: hostRef.current!, grid: bundle!.grid, slice, transferFunction: transfer, overlay, onProbe: ([u, v]) => setProbeAt(u, v), onContextLost: () => { setState("error"); setMessage("Slice WebGL context was lost. The 2D slice and metadata remain available."); } })).then((engine) => { if (cancelled) engine.dispose(); else sliceEngineRef.current = engine; }).catch(() => { if (!cancelled) { setState("error"); setMessage("The application-owned 3D slice renderer failed safely."); } });
    return () => { cancelled = true; sliceEngineRef.current?.dispose(); sliceEngineRef.current = null; };
  }, [mode, sliceView, slice, transfer, overlay, bundle]);

  useEffect(() => {
    volumeEngineRef.current?.dispose(); volumeEngineRef.current = null; setCapabilities(null); setVolumeSnapshot(null);
    if (mode !== "volume" || !bundle || !gpuValues || !transfer || !hostRef.current || capabilityOverride === "unsupported") return;
    let cancelled = false; setState("loading"); setMessage("Initializing bounded WebGL2 3D texture and application-owned ray marcher...");
    void import("./volumetricVolumeRendererEngine").then(({ createVolumetricVolumeRendererEngine }) => createVolumetricVolumeRendererEngine({ container: hostRef.current!, grid: bundle.grid, values: gpuValues, transferFunction: transfer, quality, overlay, capabilityOverride, onContextLost: () => { setState("error"); setMessage("WebGL2 context was lost. Slice and Isosurface remain available."); } })).then((result) => {
      if (cancelled) { result.engine.dispose(); return; } volumeEngineRef.current = result.engine; setCapabilities(result.capabilities); setVolumeSnapshot(result.engine.snapshot() as unknown as Record<string, unknown>); setState("ready"); setMessage("WebGL2 direct volume rendered from the validated canonical field.");
    }).catch((error) => { if (!cancelled) { setState("unsupported"); setMessage(safeMessage(error)); } });
    return () => { cancelled = true; volumeEngineRef.current?.dispose(); volumeEngineRef.current = null; };
  }, [mode, bundle, gpuValues, overlay, capabilityOverride]);

  useEffect(() => { if (slice && transfer && mode === "slice" && sliceView === "2d") drawHeatmap(); }, [slice, transfer, mode, sliceView]);
  useEffect(() => { setSliceTablePage(0); }, [slice?.contentHash]);
  useEffect(() => { if (transfer) volumeEngineRef.current?.setTransferFunction(transfer); }, [transfer]);
  useEffect(() => { volumeEngineRef.current?.setQuality(quality); }, [quality]);
  useEffect(() => { volumeEngineRef.current?.setStructureVisible(structureVisible); sliceEngineRef.current?.setStructureVisible(structureVisible); }, [structureVisible]);
  useEffect(() => { volumeEngineRef.current?.setCellVisible(cellVisible); sliceEngineRef.current?.setCellVisible(cellVisible); }, [cellVisible]);
  useEffect(() => { volumeEngineRef.current?.setClipping(clipping, axis, clipOffset); }, [clipping, axis, clipOffset]);
  useEffect(() => { volumeEngineRef.current?.setProjection(projection); }, [projection]);

  const statusClass = state === "error" ? "notice warning" : state === "unsupported" ? "notice" : "notice success";
  const textureShape = bundle ? [bundle.grid.shape[2], bundle.grid.shape[1], bundle.grid.shape[0]] : null;
  const activeTransfer = transfer;
  const supportedFields = bundle?.fields.filter((item) => item.supported) ?? [];
  const decodedValues = useMemo(() => decoded ? decoded.payload.dtype === "float32" ? new Float32Array(decoded.buffer) : new Float64Array(decoded.buffer) : null, [decoded]);
  const tablePageCount = Math.max(1, Math.ceil((slice?.values.length ?? 0) / SLICE_TABLE_PAGE_SIZE));
  const tableRows = useMemo(() => slice && bundle && activeTransfer ? buildSliceTableRows(slice, bundle.grid, activeTransfer, sliceTablePage) : [], [slice, bundle, activeTransfer, sliceTablePage]);
  const modeTitle = mode === "slice" ? "Lattice-axis Slice" : "WebGL2 Direct Volume";
  const setProbeAt = (u: number, v: number) => {
    if (!decodedValues || !bundle || !slice || !activeTransfer) return; const boundedU = Math.min(1, Math.max(0, u)), boundedV = Math.min(1, Math.max(0, v)); const fractional: [number, number, number] = [0, 0, 0]; fractional[axis] = slice.fractionalPosition; fractional[slice.plane.horizontalAxis] = boundedU; fractional[slice.plane.verticalAxis] = boundedV;
    try { const point = probeCanonicalValues({ values: decodedValues, grid: bundle.grid, fractional }); const [height, width] = slice.outputShape; setProbe(Object.freeze({ ...point, row: Math.min(height - 1, Math.floor(boundedV * height)), column: Math.min(width - 1, Math.floor(boundedU * width)), sliceCoordinates: Object.freeze([boundedU, boundedV] as const), displayedNormalizedValue: normalizedDisplayValue(point.value, activeTransfer) })); } catch (error) { setMessage(safeMessage(error)); }
  };
  const drawHeatmap = () => { const canvas = heatmapRef.current; if (!canvas || !slice || !transfer) return; const [height, width] = slice.outputShape; canvas.width = width; canvas.height = height; const context = canvas.getContext("2d"); if (!context) return; const rgba = sliceRgba(slice, transfer); const image = context.createImageData(width, height); image.data.set(rgba); context.putImageData(image, 0, 0); };
  const onHeatmapPointer = (event: React.PointerEvent<HTMLCanvasElement>) => { const bounds = event.currentTarget.getBoundingClientRect(); if (!bounds.width || !bounds.height) return; setProbeAt((event.clientX - bounds.left) / bounds.width, (event.clientY - bounds.top) / bounds.height); };
  const onHeatmapKeyDown = (event: React.KeyboardEvent<HTMLCanvasElement>) => { if (!slice || !["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home"].includes(event.key)) return; event.preventDefault(); const [height, width] = slice.outputShape; let row = probe?.row ?? 0, column = probe?.column ?? 0; if (event.key === "Home") { row = 0; column = 0; } else if (event.key === "ArrowLeft") column = Math.max(0, column - 1); else if (event.key === "ArrowRight") column = Math.min(width - 1, column + 1); else if (event.key === "ArrowUp") row = Math.max(0, row - 1); else row = Math.min(height - 1, row + 1); setProbeAt(width === 1 ? 0 : column / (width - 1), height === 1 ? 0 : row / (height - 1)); };
  const resetHeatmapView = () => { setHeatmapZoom(1); heatmapWrapRef.current?.scrollTo({ left: 0, top: 0 }); };
  const updateWindow = (which: "low" | "high", value: number) => { if (!transfer) return; try { setTransfer(validateTransferFunction({ ...transfer, [which === "low" ? "windowLow" : "windowHigh"]: value })); } catch { setMessage("Display window requires finite low < high values; source field was not changed."); } };
  const downloadPng = async () => { try { if (!active || !activeTransfer) return; let source: HTMLCanvasElement | Blob | undefined; if (mode === "volume") source = await volumeEngineRef.current?.exportPng(1200, 900, 1); else if (sliceView === "3d") source = await sliceEngineRef.current?.exportPng(); else source = heatmapRef.current ?? undefined; if (!source) return; const metadata = mode === "volume" ? [`field=${active.field.fieldName}; quantity=${active.field.quantity}; unit=${active.field.unit}`, `field_hash=${active.field.contentHash}`, `window=${activeTransfer.windowLow}..${activeTransfer.windowHigh}; palette=${activeTransfer.paletteId}; opacity=${activeTransfer.opacityScale}`, `quality=${quality.id}; projection=${projection}; samples_per_voxel=${quality.samplesPerVoxel}; max_steps=${quality.maximumRaySteps}`, `clipping=${clipping}; clip_axis=${axis}; clip_offset=${clipOffset}; structure=${structureVisible}; cell=${cellVisible}`, `gpu_dtype=${precision?.gpuDtype ?? "unavailable"}; conversion=${precision?.conversionApplied ?? false}; max_abs_error=${precision?.maximumAbsoluteError ?? "unavailable"}`] : [`field=${active.field.fieldName}; quantity=${active.field.quantity}; unit=${active.field.unit}`, `field_hash=${active.field.contentHash}; slice_hash=${slice?.contentHash ?? "unavailable"}`, `axis=${axis}; fractional_position=${slice?.fractionalPosition ?? position}; sampling=${slice?.samplingMode ?? "unavailable"}`, `window=${activeTransfer.windowLow}..${activeTransfer.windowHigh}; palette=${activeTransfer.paletteId}`, `source_range=${active.field.minimum}..${active.field.maximum}; slice_range=${slice?.statistics.minimum ?? "unavailable"}..${slice?.statistics.maximum ?? "unavailable"}`]; const blob = await createAnnotatedVolumetricPng({ source, outputWidth: mode === "volume" ? 1200 : 1000, imageHeight: mode === "volume" ? 900 : 700, metadataLines: metadata, smoothImage: mode === "volume" || sliceView === "3d" }); const url = URL.createObjectURL(blob); const link = document.createElement("a"); link.href = url; link.download = mode === "volume" ? "volumetric-direct-volume.png" : `volumetric-slice-axis-${axis}.png`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 0); } catch { setMessage("PNG export failed within the bounded local policy."); } };
  const cleanupEngines = () => { sliceEngineRef.current?.dispose(); sliceEngineRef.current = null; volumeEngineRef.current?.dispose(); volumeEngineRef.current = null; };

  return <section className="viewer-renderer-surface volumetric-slice-volume-surface" aria-label={`${modeTitle} product`} data-testid="volumetric-slice-volume-surface">
    <div className="viewer-renderer-toolbar"><div><strong>{modeTitle}</strong><span data-testid="volumetric-slice-volume-state">{state}</span></div><div className="viewer-renderer-controls"><button type="button" onClick={() => mode === "volume" ? volumeEngineRef.current?.resetCamera() : sliceEngineRef.current?.resetCamera()} disabled={state !== "ready" || (mode === "slice" && sliceView === "2d")}>Reset camera</button><button type="button" onClick={downloadPng} disabled={state !== "ready"}>Download PNG</button></div></div>
    <p className={statusClass} role="status" aria-live="polite" data-testid="volumetric-slice-volume-status">{message}</p>
    {bundle && active ? <><div className="viewer-preview-grid"><dl className="mini-grid"><dt>field</dt><dd>{active.field.fieldName}</dd><dt>quantity</dt><dd>{active.field.quantity}</dd><dt>unit</dt><dd>{active.field.unit}</dd><dt>source shape</dt><dd>{bundle.grid.shape.join(" x ")}</dd><dt>source dtype</dt><dd>{active.payload.dtype}</dd><dt>sample location</dt><dd>{bundle.grid.sampleLocation}</dd></dl><div><label>Field <select data-testid="volumetric-slice-volume-field" value={active.field.fieldId} onChange={(event) => setActive(supportedFields.find((item) => item.field.fieldId === event.target.value) ?? active)}>{supportedFields.map((item) => <option key={item.field.fieldId} value={item.field.fieldId}>{item.field.fieldName}</option>)}</select></label><label>Palette <select value={activeTransfer?.paletteId ?? "viridis"} onChange={(event) => activeTransfer && setTransfer(validateTransferFunction({ ...activeTransfer, paletteId: event.target.value as VolumeTransferFunction["paletteId"] }))}><option value="viridis">Viridis</option><option value="diverging_blue_red">Blue / red</option><option value="magma">Magma</option><option value="elf_teal_yellow">ELF teal / yellow</option></select></label></div></div>
      {activeTransfer ? <div className="viewer-renderer-controls volumetric-display-window" data-testid="volumetric-display-window"><label>Window low <input type="number" value={activeTransfer.windowLow} onChange={(event) => updateWindow("low", Number(event.target.value))} /></label><label>Window high <input type="number" value={activeTransfer.windowHigh} onChange={(event) => updateWindow("high", Number(event.target.value))} /></label><label>Opacity <input type="range" min="0" max="1" step="0.01" value={activeTransfer.opacityScale} onChange={(event) => setTransfer(validateTransferFunction({ ...activeTransfer, opacityScale: Number(event.target.value) }))} /></label><button type="button" onClick={() => active && setTransfer(defaultTransferFunction(active.field))}>Reset window</button><button type="button" onClick={() => { if (!active) return; const extent = Math.max(Math.abs(active.field.minimum), Math.abs(active.field.maximum), 1e-12); setTransfer(validateTransferFunction({ ...activeTransfer, presetId: "signed_symmetric", paletteId: "diverging_blue_red", zeroPolicy: "transparent_zero", windowLow: -extent, windowHigh: extent })); }}>Symmetric zero</button><span>Display state only; source values unchanged.</span></div> : null}</> : null}
    {mode === "slice" && bundle ? <section className="volumetric-product-panel" aria-label="Canonical lattice slice controls">
      <div><strong>Canonical plane</strong><span>{slice?.samplingMode ?? "pending"}</span></div>
      <div className="viewer-renderer-controls"><label>Axis <select data-testid="volumetric-slice-axis" value={axis} onChange={(event) => setAxis(Number(event.target.value) as VolumetricSliceAxis)}><option value={0}>lattice axis 0</option><option value={1}>lattice axis 1</option><option value={2}>lattice axis 2</option></select></label><label>Fractional position <input data-testid="volumetric-slice-position" type="range" min="0" max="0.999" step="0.001" value={position} onChange={(event) => setPosition(Number(event.target.value))} /></label><output>{position.toFixed(3)}</output><button type="button" aria-pressed={sliceView === "2d"} onClick={() => setSliceView("2d")}>2D heatmap</button><button type="button" aria-pressed={sliceView === "3d"} onClick={() => setSliceView("3d")}>3D plane</button><label><input type="checkbox" checked={structureVisible} onChange={(event) => setStructureVisible(event.target.checked)} /> structure</label><label><input type="checkbox" checked={cellVisible} onChange={(event) => setCellVisible(event.target.checked)} /> unit cell</label></div>
      {slice ? <dl className="mini-grid" data-testid="volumetric-slice-metadata"><dt>axis</dt><dd>{slice.axis}</dd><dt>fractional position</dt><dd>{slice.fractionalPosition.toFixed(3)}</dd><dt>sampling mode</dt><dd>{slice.samplingMode}</dd><dt>indices</dt><dd>{slice.lowerIndex} to {slice.upperIndex}</dd><dt>factor</dt><dd>{slice.interpolationFactor}</dd><dt>periodic wrap</dt><dd>{String(slice.periodicWrap)}</dd><dt>output</dt><dd>{slice.outputShape.join(" x ")}</dd><dt>physical position</dt><dd>{slice.physicalPosition.toFixed(6)} Angstrom</dd><dt>source range</dt><dd>{active?.field.minimum} to {active?.field.maximum} {active?.field.unit}</dd><dt>slice range</dt><dd>{slice.statistics.minimum} to {slice.statistics.maximum} {slice.unit}</dd><dt>hash</dt><dd>{slice.contentHash}</dd><dt>Worker ms</dt><dd>{sliceCalculationMs}</dd></dl> : null}
    </section> : null}
    {mode === "volume" ? <section className="volumetric-product-panel" aria-label="Direct volume controls"><div><strong>Application-owned ray marcher</strong><span>{capabilities?.webgl2 ? "WebGL2" : "capability pending"}</span></div><div className="viewer-renderer-controls"><label>Quality <select data-testid="volumetric-volume-quality" value={quality.id} onChange={(event) => setQuality(VOLUME_QUALITY_PRESETS[event.target.value as VolumeQuality["id"]])}><option value="low">Low</option><option value="balanced">Balanced</option><option value="high">High</option></select></label><label>Projection <select data-testid="volumetric-volume-projection" value={projection} onChange={(event) => setProjection(event.target.value as "perspective" | "orthographic")}><option value="perspective">Perspective</option><option value="orthographic">Orthographic</option></select></label><label><input type="checkbox" checked={clipping} onChange={(event) => setClipping(event.target.checked)} /> clipping</label><label>Clip offset <input type="range" min="0" max="1" step="0.01" value={clipOffset} onChange={(event) => setClipOffset(Number(event.target.value))} /></label><label><input type="checkbox" checked={structureVisible} onChange={(event) => setStructureVisible(event.target.checked)} /> structure</label><label><input type="checkbox" checked={cellVisible} onChange={(event) => setCellVisible(event.target.checked)} /> unit cell</label></div><dl className="mini-grid" data-testid="volumetric-volume-metrics"><dt>texture mapping</dt><dd>{textureShape?.join(" x ")} (width=nz, height=ny, depth=nx)</dd><dt>GPU dtype</dt><dd>{precision?.gpuDtype ?? "pending"}</dd><dt>conversion</dt><dd>{precision?.conversionApplied ? "float64 to float32 display copy" : "not required"}</dd><dt>max abs error</dt><dd>{precision?.maximumAbsoluteError ?? "pending"}</dd><dt>RMS error</dt><dd>{precision?.rmsError ?? "pending"}</dd><dt>texture bytes</dt><dd>{capabilities?.textureBytes ?? "pending"}</dd><dt>MAX_3D_TEXTURE_SIZE</dt><dd>{capabilities?.maximum3dTextureSize ?? "pending"}</dd><dt>texture units</dt><dd>{capabilities?.maximumTextureImageUnits ?? "pending"}</dd><dt>projection</dt><dd>{projection}</dd><dt>depth policy</dt><dd>single-scene structure depth prepass</dd><dt>sampling</dt><dd>{quality.samplesPerVoxel} samples/voxel, max {quality.maximumRaySteps} steps</dd><dt>compositing</dt><dd>front-to-back / corrected opacity / early stop 0.985</dd></dl>{volumeSnapshot ? <span data-testid="volumetric-volume-snapshot">one canvas / one context / one bounded depth target</span> : null}<p className="notice">Direct volume is source-cell only. Display window and transfer function do not alter the canonical field.</p></section> : null}
    {mode === "slice" && sliceView === "2d" ? <>
      <div className="viewer-renderer-controls" aria-label="Slice heatmap view controls"><button type="button" onClick={() => setHeatmapZoom((value) => Math.min(4, value + 0.5))}>Zoom in</button><button type="button" onClick={() => setHeatmapZoom((value) => Math.max(1, value - 0.5))}>Zoom out</button><button type="button" onClick={resetHeatmapView}>Reset heatmap view</button><output aria-label="Heatmap zoom">{heatmapZoom.toFixed(1)}x</output></div>
      <div ref={heatmapWrapRef} className="volumetric-slice-heatmap-wrap"><div className="volumetric-slice-legend" data-testid="volumetric-slice-legend"><span>{activeTransfer?.windowLow ?? "-"} {active?.field.unit}</span><strong>{activeTransfer?.paletteId ?? "pending"}</strong><span>{activeTransfer?.windowHigh ?? "-"} {active?.field.unit}</span></div><canvas ref={heatmapRef} className="volumetric-slice-heatmap" style={{ width: `${heatmapZoom * 100}%`, maxWidth: "none" }} data-testid="volumetric-slice-heatmap" aria-label="Quantitative two-dimensional lattice slice heatmap. Use arrow keys to inspect grid points." tabIndex={0} onPointerMove={onHeatmapPointer} onPointerUp={onHeatmapPointer} onKeyDown={onHeatmapKeyDown} /><span>horizontal: axis {slice?.plane.horizontalAxis ?? "-"}; vertical: axis {slice?.plane.verticalAxis ?? "-"}; rectangular parameter view of the affine plane. Scroll to pan when zoomed.</span></div>
      {slice ? <section className="volumetric-slice-table" aria-label="Accessible slice value table" data-testid="volumetric-slice-value-table"><div className="viewer-renderer-controls"><button type="button" disabled={sliceTablePage === 0} onClick={() => setSliceTablePage((value) => Math.max(0, value - 1))}>Previous values</button><output>Page {sliceTablePage + 1} of {tablePageCount}</output><button type="button" disabled={sliceTablePage + 1 >= tablePageCount} onClick={() => setSliceTablePage((value) => Math.min(tablePageCount - 1, value + 1))}>Next values</button></div><div className="viewer-table-wrap"><table><caption>Exact slice values; select a row to pin its source coordinate.</caption><thead><tr><th>row</th><th>column</th><th>fractional</th><th>Cartesian (Angstrom)</th><th>source value ({slice.unit})</th><th>display normalized</th></tr></thead><tbody>{tableRows.map((row) => <tr key={`${row.row}:${row.column}`}><td>{row.row}</td><td>{row.column}</td><td>{row.fractional.map((value) => value.toFixed(5)).join(", ")}</td><td>{row.cartesian.map((value) => value.toFixed(5)).join(", ")}</td><td><button type="button" onClick={() => setProbeAt(row.u, row.v)}>{row.value}</button></td><td>{row.displayedNormalizedValue}</td></tr>)}</tbody></table></div></section> : null}
    </> : <div ref={hostRef} className="viewer-renderer-canvas-host" data-testid="volumetric-slice-volume-canvas-host" aria-label={`${modeTitle} graphics canvas`} />}
    {probe ? <dl className="mini-grid" data-testid="volumetric-slice-probe" aria-live="polite"><dt>source value</dt><dd>{probe.value} {active?.field.unit}</dd><dt>display normalized</dt><dd>{probe.displayedNormalizedValue}</dd><dt>pixel index</dt><dd>row {probe.row}, column {probe.column}</dd><dt>slice coordinates</dt><dd>{probe.sliceCoordinates.map((value) => value.toFixed(5)).join(", ")}</dd><dt>fractional</dt><dd>{probe.fractional.map((value) => value.toFixed(5)).join(", ")}</dd><dt>Cartesian</dt><dd>{probe.cartesian.map((value) => value.toFixed(5)).join(", ")} Angstrom</dd><dt>interpolation</dt><dd>{slice?.samplingMode}; indices {slice?.lowerIndex} to {slice?.upperIndex}; factor {slice?.interpolationFactor}</dd></dl> : null}
    <p className="notice">Security: no artifact JavaScript, shader, Worker, URL, texture, module, or arbitrary plane expression is executed.</p>
  </section>;
}

function safeMessage(error: unknown): string { return error instanceof VolumetricViewerError || error instanceof Error ? error.message : "Volumetric slice/volume product failed safely."; }

function normalizedDisplayValue(value: number, transfer: VolumeTransferFunction): number { return Number(Math.min(1, Math.max(0, (value - transfer.windowLow) / (transfer.windowHigh - transfer.windowLow))).toPrecision(10)); }
function buildSliceTableRows(slice: VolumetricSlice, grid: ValidatedVolumetricBundle["grid"], transfer: VolumeTransferFunction, page: number) { const [height, width] = slice.outputShape; const start = Math.min(Math.max(0, page) * SLICE_TABLE_PAGE_SIZE, Math.max(0, slice.values.length - 1)); const end = Math.min(slice.values.length, start + SLICE_TABLE_PAGE_SIZE); const rows = []; for (let index = start; index < end; index += 1) { const row = Math.floor(index / width), column = index % width; const u = width <= 1 ? 0 : column / (width - 1), v = height <= 1 ? 0 : row / (height - 1); const fractional: [number, number, number] = [0, 0, 0]; fractional[slice.axis] = slice.fractionalPosition; fractional[slice.plane.horizontalAxis] = u; fractional[slice.plane.verticalAxis] = v; const value = slice.values[index]; rows.push(Object.freeze({ row, column, u, v, fractional: Object.freeze(fractional), cartesian: Object.freeze(fractionalToWorld(grid, fractional)), value, displayedNormalizedValue: normalizedDisplayValue(value, transfer) })); } return rows; }
