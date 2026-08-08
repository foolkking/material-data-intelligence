"use client";

import { lazy, Suspense, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { getPlannerJobArtifacts, type Artifact } from "../../lib/planner-api";
import type { ScientificWorkspace, WorkspacePanel, WorkspaceSelectionContext } from "../../lib/workspace-api";
import { WorkspaceArtifactLoader, WorkspaceArtifactLoadError, validateArtifactScope, type WorkspaceArtifactLoadScope } from "./workspace-artifact-loader";
import {
  artifactChecksum,
  artifactIdentity,
  artifactVersion,
  resolveArtifactRenderer,
  resolveLoadedArtifactRenderer,
  type RendererComponent,
  type WorkspaceRendererDescriptor,
} from "./workspace-renderer-registry";
import { artifactSelectionFromArtifact, datasetSampleSelection, type WorkspaceSelectionDelivery } from "./workspace-selection-runtime";
import { WorkspaceHeavyViewerLease } from "./workspace-heavy-viewer-gate";

const DatasetMaterialsExplorerPanel = lazy(() => import("../dataset-explorer/DatasetMaterialsExplorerPanel").then((module) => ({ default: module.DatasetMaterialsExplorerPanel })));
const MaterialsMlEvaluationPanel = lazy(() => import("../materials-ml/MaterialsMlEvaluationPanel").then((module) => ({ default: module.MaterialsMlEvaluationPanel })));
const CompositionSpaceExplorerPanel = lazy(() => import("../composition-space/CompositionSpaceExplorerPanel").then((module) => ({ default: module.CompositionSpaceExplorerPanel })));
const ViewerSceneRendererSurface = lazy(() => import("../viewer-scene/ViewerSceneRendererSurface").then((module) => ({ default: module.ViewerSceneRendererSurface })));
const TrajectoryViewerSurface = lazy(() => import("../trajectory-viewer/TrajectoryViewerSurface").then((module) => ({ default: module.TrajectoryViewerSurface })));
const PhononBandPreviewPanel = lazy(() => import("../phonon-band/PhononBandPreviewPanel").then((module) => ({ default: module.PhononBandPreviewPanel })));
const PhononDosPreviewPanel = lazy(() => import("../phonon-dos/PhononDosPreviewPanel").then((module) => ({ default: module.PhononDosPreviewPanel })));
const PhononBandDosPreviewPanel = lazy(() => import("../phonon-band-dos/PhononBandDosPreviewPanel").then((module) => ({ default: module.PhononBandDosPreviewPanel })));
const PhononAnimationSurface = lazy(() => import("../phonon-animation/PhononAnimationSurface").then((module) => ({ default: module.PhononAnimationSurface })));
const BrillouinZonePreviewPanel = lazy(() => import("../brillouin-zone/BrillouinZonePreviewPanel").then((module) => ({ default: module.BrillouinZonePreviewPanel })));
const VolumetricPreviewPanel = lazy(() => import("../volumetric-viewer/VolumetricPreviewPanel").then((module) => ({ default: module.VolumetricPreviewPanel })));
const WorkspaceGenericPlot = lazy(() => import("./WorkspaceGenericPlot").then((module) => ({ default: module.WorkspaceGenericPlot })));
const CoordinationResultPanel = lazy(() => import("./CoordinationResultPanel").then((module) => ({ default: module.CoordinationResultPanel })));
const LocalEnvironmentPolyhedraPanel = lazy(() => import("./LocalEnvironmentPolyhedraPanel").then((module) => ({ default: module.LocalEnvironmentPolyhedraPanel })));
const ExperimentalXrdComparisonPanel = lazy(() => import("./ExperimentalXrdComparisonPanel").then((module) => ({ default: module.ExperimentalXrdComparisonPanel })));

export const MAX_METADATA_ARTIFACTS = 256;
const MAX_JSON_PREVIEW_CHARS = 80_000;

type GalleryProps = Readonly<{
  workspace: ScientificWorkspace;
  panel: WorkspacePanel;
  delivery: WorkspaceSelectionDelivery | null;
  onSelection: (selection: WorkspaceSelectionContext) => void;
  onNavigateReference: (selection: WorkspaceSelectionContext, destination: "EVIDENCE" | "PROVENANCE") => void;
}>;

export function WorkspaceArtifactGallery({ workspace, panel, delivery, onSelection, onNavigateReference }: GalleryProps) {
  const [metadataState, setMetadataState] = useState<"LOADING" | "READY" | "EMPTY" | "FAILED" | "CAP_EXCEEDED">("LOADING");
  const [artifacts, setArtifacts] = useState<readonly Artifact[]>([]);
  const [metadataMessage, setMetadataMessage] = useState("Loading Artifact metadata only.");
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(null);
  const [loadedArtifacts, setLoadedArtifacts] = useState<readonly Artifact[]>([]);
  const [payloadState, setPayloadState] = useState<"IDLE" | "LOADING" | "READY" | "FAILED">("IDLE");
  const [payloadMessage, setPayloadMessage] = useState("Choose an Artifact to load its validated payload.");
  const loaderRef = useRef(new WorkspaceArtifactLoader());
  const payloadControllerRef = useRef<AbortController | null>(null);
  const payloadRequestRef = useRef(0);

  useEffect(() => {
    const controller = new AbortController();
    setMetadataState("LOADING");
    setMetadataMessage("Loading Artifact metadata only.");
    void getPlannerJobArtifacts(workspace.sourceJobId, { signal: controller.signal }).then((items) => {
      if (controller.signal.aborted) return;
      let ordered: readonly Artifact[];
      try {
        ordered = validateAndOrderArtifactMetadata(items, scope(workspace));
      } catch (error) {
        const message = errorCode(error);
        setMetadataState(message.startsWith("ARTIFACT_METADATA_CAP_EXCEEDED") ? "CAP_EXCEEDED" : "FAILED");
        setMetadataMessage(message);
        return;
      }
      setArtifacts(Object.freeze(ordered));
      setMetadataState(ordered.length ? "READY" : "EMPTY");
      setMetadataMessage(ordered.length ? `${ordered.length} Artifact metadata records loaded; payload requests remain zero.` : "No persisted Artifacts are available for this Job.");
    }).catch((error) => {
      if (controller.signal.aborted) return;
      setMetadataState("FAILED");
      setMetadataMessage(errorCode(error));
    });
    return () => controller.abort();
  }, [workspace.projectId, workspace.revision, workspace.sourceJobId, workspace.workspaceId]);

  useEffect(() => () => loaderRef.current.clear(), [workspace.workspaceId]);

  const activeArtifact = artifacts.find((item) => artifactIdentity(item) === activeArtifactId) ?? null;
  const grouped = useMemo(() => groupArtifacts(artifacts), [artifacts]);

  const openArtifact = (artifact: Artifact) => {
    if (!panelAllowsPayload(panel.state)) {
      setPayloadState("FAILED");
      setPayloadMessage(`PANEL_PAYLOAD_UNAVAILABLE: ${panel.state}`);
      return;
    }
    const id = artifactIdentity(artifact);
    if (!id) return;
    payloadControllerRef.current?.abort();
    const controller = new AbortController();
    payloadControllerRef.current = controller;
    const requestId = ++payloadRequestRef.current;
    setActiveArtifactId(id);
    setLoadedArtifacts([]);
    setPayloadState("LOADING");
    setPayloadMessage("Validating exact scope, contract, length and checksum.");
    void loaderRef.current.loadBundle(artifact, artifacts, scope(workspace), controller.signal).then((bundle) => {
      if (requestId !== payloadRequestRef.current || controller.signal.aborted) return;
      setLoadedArtifacts(bundle);
      setPayloadState("READY");
      setPayloadMessage(`${bundle.filter((item) => item.content !== undefined).length} bounded payload record(s) validated.`);
    }).catch((error) => {
      if (controller.signal.aborted || requestId !== payloadRequestRef.current) return;
      setPayloadState("FAILED");
      setPayloadMessage(errorCode(error));
    });
  };

  const downloadArtifact = (artifact: Artifact) => {
    const id = artifactIdentity(artifact);
    if (!id) return;
    const controller = new AbortController();
    setPayloadState("LOADING");
    setPayloadMessage("Validating exact scope, length and checksum before download.");
    void loaderRef.current.download(artifact, scope(workspace), controller.signal).then((bytes) => {
      const objectUrl = URL.createObjectURL(new Blob([bytes], { type: artifact.contentType || "application/octet-stream" }));
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = safeDownloadName(artifact);
      anchor.rel = "noopener";
      anchor.click();
      window.setTimeout(() => URL.revokeObjectURL(objectUrl), 0);
      setPayloadState("READY");
      setPayloadMessage("Download completed after exact checksum validation.");
    }).catch((error) => {
      if (controller.signal.aborted) return;
      setPayloadState("FAILED");
      setPayloadMessage(errorCode(error));
    });
  };

  useEffect(() => {
    return () => { payloadRequestRef.current += 1; payloadControllerRef.current?.abort(); };
  }, [workspace.workspaceId]);

  const selectArtifact = (artifact: Artifact) => {
    const selection = artifactSelectionFromArtifact(artifact, workspace);
    if (selection) onSelection(selection);
  };

  const navigateArtifact = (artifact: Artifact, destination: "EVIDENCE" | "PROVENANCE") => {
    const selection = artifactSelectionFromArtifact(artifact, workspace);
    if (selection) onNavigateReference(selection, destination);
  };

  return <section className="workspace-artifact-gallery" aria-labelledby="workspace-artifact-gallery-title" data-testid="workspace-artifact-gallery">
    <header className="workspace-gallery-heading">
      <div><h3 id="workspace-artifact-gallery-title">Typed Artifact Gallery</h3><p>{metadataMessage}</p></div>
      <span className="workspace-gallery-count" aria-label={`${artifacts.length} Artifacts loaded`}>{artifacts.length} / {workspace.artifactCount}</span>
    </header>
    {metadataState === "LOADING" ? <GalleryState title="Loading metadata" message="Scientific payloads are not requested during initial Workspace loading." /> : null}
    {metadataState === "EMPTY" ? <GalleryState title="No Artifacts" message={metadataMessage} /> : null}
    {["FAILED", "CAP_EXCEEDED"].includes(metadataState) ? <GalleryState title="Artifact Gallery unavailable" message={metadataMessage} error /> : null}
    {metadataState === "READY" ? <div className="workspace-artifact-groups">{grouped.map(([group, items]) => <section key={group} aria-labelledby={`artifact-group-${slug(group)}`}>
      <h4 id={`artifact-group-${slug(group)}`}>{group}</h4>
      <ul className="workspace-artifact-list">{items.map((artifact) => <ArtifactCard key={artifactIdentity(artifact)!} artifact={artifact} panelState={panel.state} active={artifactIdentity(artifact) === activeArtifactId} selected={delivery?.context?.primary?.artifactId === artifactIdentity(artifact)} onOpen={() => openArtifact(artifact)} onDownload={() => downloadArtifact(artifact)} onSelect={() => selectArtifact(artifact)} onEvidence={() => navigateArtifact(artifact, "EVIDENCE")} onLineage={() => navigateArtifact(artifact, "PROVENANCE")} />)}</ul>
    </section>)}</div> : null}
    {activeArtifact ? <section className="workspace-active-artifact" aria-labelledby="workspace-active-artifact-title">
      <header><div><span className="eyebrow">Calculated result</span><h4 id="workspace-active-artifact-title">{safeTitle(activeArtifact)}</h4></div><button type="button" className="secondary" onClick={() => { payloadRequestRef.current += 1; payloadControllerRef.current?.abort(); setActiveArtifactId(null); setLoadedArtifacts([]); setPayloadState("IDLE"); }}>Close viewer</button></header>
      <div role="status" className={`workspace-artifact-load-state tone-${payloadState === "FAILED" ? "danger" : payloadState === "READY" ? "success" : "muted"}`}>{payloadMessage}</div>
      {payloadState === "READY" ? <WorkspaceArtifactRenderer selected={activeArtifact} artifacts={loadedArtifacts} workspace={workspace} delivery={delivery} onSelection={onSelection} /> : null}
    </section> : null}
    <details className="workspace-audit-json"><summary>Gallery audit JSON</summary><pre>{JSON.stringify({ metadataOnly: true, artifactCount: artifacts.length, activeArtifactId, rendererAuthority: "type+version+validated-payload-schema", delivery: delivery?.compatibility ?? "NOT_APPLICABLE" }, null, 2)}</pre></details>
  </section>;
}

function ArtifactCard({ artifact, panelState, active, selected, onOpen, onDownload, onSelect, onEvidence, onLineage }: Readonly<{ artifact: Artifact; panelState: WorkspacePanel["state"]; active: boolean; selected: boolean; onOpen: () => void; onDownload: () => void; onSelect: () => void; onEvidence: () => void; onLineage: () => void }>) {
  const resolution = resolveArtifactRenderer(artifact);
  const descriptor = resolution.descriptor;
  return <li className={`workspace-artifact-card ${active ? "active" : ""}`} data-testid={`workspace-artifact-${artifactIdentity(artifact)}`}>
    <div className="workspace-artifact-card-heading"><div><strong>{safeTitle(artifact)}</strong><code>{artifact.type || "unknown"}@{artifactVersion(artifact)}</code></div><span>{resolution.status === "SUPPORTED" ? descriptor?.classification : resolution.status}</span></div>
    <dl className="workspace-artifact-metadata">
      <dt>Renderer</dt><dd>{descriptor ? `${descriptor.rendererContract}/${descriptor.rendererVersion}` : "Inert fallback"}</dd>
      <dt>Source</dt><dd>{compact(artifact.toolCallId)} / {compact(stepId(artifact))}</dd>
      <dt>Checksum</dt><dd><code>{compact(artifactChecksum(artifact), 16)}</code></dd>
      <dt>Size</dt><dd>{formatBytes(artifact.sizeBytes)}</dd>
      <dt>Selection</dt><dd>{descriptor?.selectionOutputs.length ? descriptor.selectionOutputs.join(", ") : "Consumer only"}</dd>
      <dt>Status</dt><dd>{panelState} / {resolution.reason}</dd>
    </dl>
    {resolution.status !== "SUPPORTED" || descriptor?.classification === "INERT_FALLBACK" ? <p className="workspace-artifact-warning">No renderer is guessed from filename, label or MIME. Provenance remains available.</p> : null}
    <div className="workspace-artifact-actions"><button type="button" onClick={onOpen} disabled={!descriptor || descriptor.payloadMode === "DOWNLOAD_ONLY" || !panelAllowsPayload(panelState)} aria-label={`Open ${safeTitle(artifact)}`}>Open</button><button type="button" className="secondary" onClick={onDownload} aria-label={`Download ${safeTitle(artifact)}`}>Download</button><button type="button" className="secondary" onClick={onSelect} disabled={!descriptor?.selectionOutputs.includes("ARTIFACT")} aria-pressed={selected}>Select</button><button type="button" className="secondary" onClick={onEvidence} disabled={!descriptor?.selectionOutputs.includes("ARTIFACT")}>Evidence</button><button type="button" className="secondary" onClick={onLineage} disabled={!descriptor?.selectionOutputs.includes("ARTIFACT")}>Lineage</button></div>
  </li>;
}

function WorkspaceArtifactRenderer({ selected, artifacts, workspace, delivery, onSelection }: Readonly<{ selected: Artifact; artifacts: readonly Artifact[]; workspace: ScientificWorkspace; delivery: WorkspaceSelectionDelivery | null; onSelection: (selection: WorkspaceSelectionContext) => void }>) {
  const loadedSelected = artifacts.find((item) => artifactIdentity(item) === artifactIdentity(selected)) ?? selected;
  const resolution = resolveLoadedArtifactRenderer(loadedSelected);
  const descriptor = resolution.descriptor;
  if (!descriptor) return <InertFallback artifact={selected} reason={resolution.reason} />;
  if (!loadedSelected.content && !["METADATA_ONLY", "DOWNLOAD_ONLY"].includes(descriptor.payloadMode)) return <InertFallback artifact={selected} reason="ARTIFACT_PAYLOAD_MISSING" />;
  const bundle = artifacts as Artifact[];
  const sample = delivery?.compatibility === "EXACT" && delivery.context?.primary?.kind === "DATASET_SAMPLE" ? delivery.context.primary : null;
  const externalSampleKey = sample?.objectId && sample.sampleRef ? `${sample.objectId}:${sample.sampleRef}` : null;
  const emitSample = (identity: Readonly<{ objectId: string; sampleRef: string; sampleKey: string }>) => onSelection(datasetSampleSelection(workspace, identity));
  const rendered = (() => { switch (descriptor.component) {
    case "DATASET": return <LazyBoundary><DatasetMaterialsExplorerPanel artifacts={bundle} externalSampleKey={externalSampleKey} onSampleSelection={emitSample} /></LazyBoundary>;
    case "ML": return <LazyBoundary><MaterialsMlEvaluationPanel artifacts={bundle} /></LazyBoundary>;
    case "COMPOSITION": return <LazyBoundary><CompositionSpaceExplorerPanel artifacts={bundle} externalSampleKey={externalSampleKey} onSampleSelection={emitSample} /></LazyBoundary>;
    case "STRUCTURE": return <LazyBoundary><ViewerSceneRendererSurface payload={loadedSelected.content} /></LazyBoundary>;
    case "TRAJECTORY": return <LazyBoundary><TrajectoryViewerSurface payload={loadedSelected.content} /></LazyBoundary>;
    case "PHONON_BAND": return <LazyBoundary><PhononBandPreviewPanel artifacts={bundle} /></LazyBoundary>;
    case "PHONON_DOS": return <LazyBoundary><PhononDosPreviewPanel artifacts={bundle} /></LazyBoundary>;
    case "PHONON_COMBINED": return <LazyBoundary><PhononBandDosPreviewPanel artifacts={bundle} /></LazyBoundary>;
    case "PHONON_ANIMATION": return <LazyBoundary><PhononAnimationSurface payload={loadedSelected.content} /></LazyBoundary>;
    case "BRILLOUIN_ZONE": return <LazyBoundary><BrillouinZonePreviewPanel artifacts={bundle} /></LazyBoundary>;
    case "VOLUMETRIC": return <LazyBoundary><VolumetricPreviewPanel artifacts={bundle} /></LazyBoundary>;
    case "COORDINATION": return <LazyBoundary><CoordinationResultPanel artifacts={bundle} selected={loadedSelected} workspace={workspace} onSelection={onSelection} /></LazyBoundary>;
    case "LOCAL_ENVIRONMENT": return <LazyBoundary><LocalEnvironmentPolyhedraPanel artifacts={bundle} selected={loadedSelected} workspace={workspace} onSelection={onSelection} /></LazyBoundary>;
    case "EXPERIMENTAL_XRD": return <LazyBoundary><ExperimentalXrdComparisonPanel artifacts={bundle} selected={loadedSelected} workspace={workspace} onSelection={onSelection} /></LazyBoundary>;
    case "TEXT": return <TextFallback content={loadedSelected.content} />;
    case "GENERIC_TABLE": return <TableFallback content={loadedSelected.content} descriptor={descriptor} />;
    case "GENERIC_PLOT": return <PlotFallback content={loadedSelected.content} descriptor={descriptor} />;
    case "JSON": return <JsonFallback content={loadedSelected.content} />;
    default: return <InertFallback artifact={selected} reason="RENDERER_METADATA_ONLY" />;
  } })();
  return descriptor.heavy
    ? <WorkspaceHeavyViewerLease owner={`${workspace.workspaceId}:${artifactIdentity(selected) ?? "unknown"}`}>{rendered}</WorkspaceHeavyViewerLease>
    : rendered;
}

function LazyBoundary({ children }: { children: ReactNode }) { return <Suspense fallback={<div className="workspace-gallery-state" role="status">Loading application-owned Viewer code.</div>}>{children}</Suspense>; }

function TableFallback({ content, descriptor }: Readonly<{ content: unknown; descriptor: WorkspaceRendererDescriptor }>) {
  const rows = tableRows(content).slice(0, descriptor.maximumRows);
  const columns = rows.length ? Object.keys(rows[0]).slice(0, 32) : [];
  if (!rows.length || !columns.length) return <JsonFallback content={content} />;
  return <section className="workspace-generic-renderer"><h5>Validated numeric table</h5><p>Showing {rows.length} bounded backend-produced row(s). No statistics are recomputed.</p><div className="workspace-table-scroll"><table><thead><tr>{columns.map((column) => <th key={column} scope="col">{column}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={stableRowKey(row, index)}>{columns.map((column) => <td key={column}>{displayScalar(row[column])}</td>)}</tr>)}</tbody></table></div></section>;
}

function PlotFallback({ content, descriptor }: Readonly<{ content: unknown; descriptor: WorkspaceRendererDescriptor }>) {
  const record = asRecord(content);
  const figure = asRecord(record?.figure) ?? record;
  const traces = Array.isArray(figure?.data) ? figure.data.slice(0, 32) : [];
  return <section className="workspace-generic-renderer" aria-label="Numeric plot fallback"><h5>Backend-produced numeric plot</h5><p>{traces.length} bounded series are available. Histogram traces remain table-only so the browser never recomputes bins.</p><LazyBoundary><WorkspaceGenericPlot content={content} maximumPoints={descriptor.maximumPoints} /></LazyBoundary><TableFallback content={{ rows: traces.flatMap((trace, traceIndex) => plotRows(trace, traceIndex, descriptor.maximumPoints)).slice(0, descriptor.maximumRows) }} descriptor={descriptor} /><details><summary>Plot specification</summary><JsonFallback content={content} /></details></section>;
}

function TextFallback({ content }: { content: unknown }) { return <section className="workspace-generic-renderer"><h5>Inert text</h5><pre>{typeof content === "string" ? content.slice(0, MAX_JSON_PREVIEW_CHARS) : "Text payload unavailable."}</pre></section>; }
function JsonFallback({ content }: { content: unknown }) { const text = JSON.stringify(content, null, 2); return <section className="workspace-generic-renderer"><h5>Inert JSON</h5><pre>{text.length > MAX_JSON_PREVIEW_CHARS ? `${text.slice(0, MAX_JSON_PREVIEW_CHARS)}\n[bounded preview]` : text}</pre></section>; }
function InertFallback({ artifact, reason }: { artifact: Artifact; reason: string }) { return <section className="workspace-generic-renderer" role="status"><h5>Inert Artifact fallback</h5><p>{reason}. No HTML, JavaScript, iframe, dynamic module, external URL or guessed renderer is executed.</p><dl><dt>Contract</dt><dd>{artifact.type || "unknown"}@{artifactVersion(artifact)}</dd><dt>Checksum</dt><dd>{compact(artifactChecksum(artifact), 20)}</dd></dl></section>; }
function GalleryState({ title, message, error = false }: { title: string; message: string; error?: boolean }) { return <div className="workspace-gallery-state" role={error ? "alert" : "status"}><strong>{title}</strong><span>{message}</span></div>; }

function scope(workspace: ScientificWorkspace) { return { workspaceId: workspace.workspaceId, workspaceRevision: workspace.revision, projectId: workspace.projectId, sourceJobId: workspace.sourceJobId }; }

function panelAllowsPayload(state: WorkspacePanel["state"]): boolean { return state === "PRODUCED" || state === "PARTIAL"; }
function safeDownloadName(artifact: Artifact): string {
  const source = artifact.name || `${artifact.type || "artifact"}.${artifact.contentType === "application/json" ? "json" : "bin"}`;
  const safe = source.replace(/[^A-Za-z0-9._-]+/g, "_").replace(/^\.+/, "").slice(0, 128);
  return safe || "artifact.bin";
}
function compareArtifacts(left: Artifact, right: Artifact) { return String(left.type).localeCompare(String(right.type)) || String(left.createdAt).localeCompare(String(right.createdAt)) || String(artifactIdentity(left)).localeCompare(String(artifactIdentity(right))); }

export function validateAndOrderArtifactMetadata(items: readonly Artifact[], sourceScope: WorkspaceArtifactLoadScope): readonly Artifact[] {
  if (items.length > MAX_METADATA_ARTIFACTS) {
    throw new WorkspaceArtifactLoadError(`ARTIFACT_METADATA_CAP_EXCEEDED: ${items.length} exceeds ${MAX_METADATA_ARTIFACTS}.`);
  }
  for (const item of items) validateArtifactScope(item, sourceScope);
  return Object.freeze([...items].sort(compareArtifacts));
}
function groupArtifacts(artifacts: readonly Artifact[]): Array<[string, Artifact[]]> { const groups = new Map<string, Artifact[]>(); for (const artifact of artifacts) { const resolution = resolveArtifactRenderer(artifact); const group = resolution.descriptor?.component.replaceAll("_", " ") ?? "UNSUPPORTED"; groups.set(group, [...(groups.get(group) ?? []), artifact]); } return [...groups.entries()].sort(([a], [b]) => a.localeCompare(b)); }
function safeTitle(artifact: Artifact) { const value = typeof artifact.name === "string" ? artifact.name.replace(/[\r\n\t]/g, " ").slice(0, 120) : "Untitled Artifact"; return value || "Untitled Artifact"; }
function compact(value: unknown, size = 20) { const text = typeof value === "string" ? value : "none"; return text.length > size ? `${text.slice(0, size - 3)}...` : text; }
function stepId(artifact: Artifact) { return typeof artifact.metadata?.stepId === "string" ? artifact.metadata.stepId : "none"; }
function slug(value: string) { return value.toLowerCase().replace(/[^a-z0-9]+/g, "-"); }
function formatBytes(value: unknown) { if (!Number.isSafeInteger(value) || Number(value) < 0) return "unknown"; const bytes = Number(value); return bytes < 1024 ? `${bytes} B` : `${(bytes / 1024).toFixed(1)} KiB`; }
function errorCode(error: unknown) { if (error instanceof WorkspaceArtifactLoadError) return error.code; if (error instanceof Error) return error.message.replace(/[\r\n\t]/g, " ").slice(0, 160); return "ARTIFACT_GALLERY_FAILED"; }
function asRecord(value: unknown): Record<string, unknown> | null { return value !== null && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function tableRows(content: unknown): Record<string, unknown>[] { const record = asRecord(content); const candidates = [record?.rows, record?.data, record?.records]; for (const candidate of candidates) if (Array.isArray(candidate)) return candidate.filter((item): item is Record<string, unknown> => asRecord(item) !== null); return []; }
function stableRowKey(row: Record<string, unknown>, index: number) { for (const key of ["objectId", "sampleRef", "sampleKey", "id"]) if (typeof row[key] === "string") return `${key}:${row[key]}`; return `display-row-${index}`; }
function displayScalar(value: unknown) { if (typeof value === "number") return Number.isFinite(value) ? String(value) : "invalid"; if (["string", "boolean"].includes(typeof value)) return String(value).slice(0, 200); return value === null ? "null" : "[structured]"; }
function plotRows(value: unknown, traceIndex: number, cap: number): Record<string, unknown>[] { const trace = asRecord(value); const x = Array.isArray(trace?.x) ? trace.x : []; const y = Array.isArray(trace?.y) ? trace.y : []; const values = Array.isArray(trace?.values) ? trace.values : []; const count = Math.min(Math.max(x.length, y.length, values.length), cap); return Array.from({ length: count }, (_, index) => ({ trace: traceIndex + 1, point: index + 1, x: x[index] ?? null, y: y[index] ?? null, value: values[index] ?? null })); }
