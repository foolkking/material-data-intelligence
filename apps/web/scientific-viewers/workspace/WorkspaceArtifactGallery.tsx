"use client";
import { selectVolumetricField, restoredVolumetricField } from "../volumetric-viewer/volumetric-selection";

import type { Agent2ScientificFact } from "../../app/lib/agent2-research-api";
import { resultTrajectoryPoint } from "../trajectory-viewer/result-trajectory-selection";
import { Fragment, Suspense, useEffect, useId, useMemo, useRef, useState, type ReactNode } from "react";
import { createDeferredScientificViewer } from "../DeferredScientificViewer";
import { getPlannerJobArtifacts, type Artifact } from "../../app/lib/planner-api";
import type { ScientificWorkspace, WorkspacePanel, WorkspaceSelectionContext } from "../../app/lib/workspace-api";
import { WorkspaceArtifactLoader, WorkspaceArtifactLoadError, validateArtifactScope, type WorkspaceArtifactLoadScope } from "./workspace-artifact-loader";
import {
  artifactChecksum,
  artifactIdentity,
  artifactVersion,
  indexArtifactsByIdentity,
  resolveArtifactRenderer,
  resolveLoadedArtifactRenderer,
  type RendererComponent,
  type WorkspaceRendererDescriptor,
} from "../../shared/workspace/workspace-renderer-registry";
import { artifactSelectionFromArtifact, datasetSampleIdentityFromTableRow, datasetSampleSelection, structureSiteSelection, type WorkspaceSelectionDelivery } from "../../shared/workspace/workspace-selection-runtime";
import { clearedWorkspaceSelection } from "../../shared/workspace/workspace-selection-contract";
import { selectPhononBandPoint, restoredPhononBandPoint, selectPhononDosPoint, restoredPhononDosPoint } from "../phonon-shared/phonon-selection";
import { selectTrajectoryPoint, restoredTrajectoryPoint } from "../trajectory-viewer/trajectory-selection";
import { WorkspaceHeavyViewerLease } from "./workspace-heavy-viewer-gate";
import { plotTablePreview } from "./workspace-plot-table";
import { formatPresentationMetricValue } from "../../app/lib/scientific-presentation";
import { savedParameterTableRows } from "../../app/lib/scientific-report-table-data";

const DatasetMaterialsExplorerPanel = createDeferredScientificViewer(() => import("../dataset-explorer/DatasetMaterialsExplorerPanel").then((module) => ({ default: module.DatasetMaterialsExplorerPanel })));
const MaterialsMlEvaluationPanel = createDeferredScientificViewer(() => import("../materials-ml/MaterialsMlEvaluationPanel").then((module) => ({ default: module.MaterialsMlEvaluationPanel })));
const CompositionSpaceExplorerPanel = createDeferredScientificViewer(() => import("../composition-space/CompositionSpaceExplorerPanel").then((module) => ({ default: module.CompositionSpaceExplorerPanel })));
const ViewerSceneRendererSurface = createDeferredScientificViewer(() => import("../viewer-scene/ViewerSceneRendererSurface").then((module) => ({ default: module.ViewerSceneRendererSurface })));
const TrajectoryViewerSurface = createDeferredScientificViewer(() => import("../trajectory-viewer/TrajectoryViewerSurface").then((module) => ({ default: module.TrajectoryViewerSurface })));
const PhononBandPreviewPanel = createDeferredScientificViewer(() => import("../phonon-band/PhononBandPreviewPanel").then((module) => ({ default: module.PhononBandPreviewPanel })));
const PhononDosPreviewPanel = createDeferredScientificViewer(() => import("../phonon-dos/PhononDosPreviewPanel").then((module) => ({ default: module.PhononDosPreviewPanel })));
const PhononBandDosPreviewPanel = createDeferredScientificViewer(() => import("../phonon-band-dos/PhononBandDosPreviewPanel").then((module) => ({ default: module.PhononBandDosPreviewPanel })));
const PhononAnimationSurface = createDeferredScientificViewer(() => import("../phonon-animation/PhononAnimationSurface").then((module) => ({ default: module.PhononAnimationSurface })));
const BrillouinZonePreviewPanel = createDeferredScientificViewer(() => import("../brillouin-zone/BrillouinZonePreviewPanel").then((module) => ({ default: module.BrillouinZonePreviewPanel })));
const VolumetricPreviewPanel = createDeferredScientificViewer(() => import("../volumetric-viewer/VolumetricPreviewPanel").then((module) => ({ default: module.VolumetricPreviewPanel })));
const WorkspaceGenericPlot = createDeferredScientificViewer(() => import("./WorkspaceGenericPlot").then((module) => ({ default: module.WorkspaceGenericPlot })));
const CoordinationResultPanel = createDeferredScientificViewer(() => import("./CoordinationResultPanel").then((module) => ({ default: module.CoordinationResultPanel })));
const CoordinationHistogramPanel = createDeferredScientificViewer(() => import("./CoordinationHistogramPanel").then((module) => ({ default: module.CoordinationHistogramPanel })));
const LocalEnvironmentPolyhedraPanel = createDeferredScientificViewer(() => import("./LocalEnvironmentPolyhedraPanel").then((module) => ({ default: module.LocalEnvironmentPolyhedraPanel })));
const ExperimentalXrdComparisonPanel = createDeferredScientificViewer(() => import("./ExperimentalXrdComparisonPanel").then((module) => ({ default: module.ExperimentalXrdComparisonPanel })));
const TrajectoryAnalyticsPanel = createDeferredScientificViewer(() => import("./TrajectoryAnalyticsPanel").then((module) => ({ default: module.TrajectoryAnalyticsPanel })));
const ElectronicStructurePanel = createDeferredScientificViewer(() => import("./ElectronicStructurePanel").then((module) => ({ default: module.ElectronicStructurePanel })));

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
  const galleryInstanceId = useId().replace(/[^A-Za-z0-9_-]/g, "");
  const galleryTitleId = `workspace-artifact-gallery-title-${galleryInstanceId}`;
  const activeArtifactTitleId = `workspace-active-artifact-title-${galleryInstanceId}`;
  const artifactGroupId = (group: string) => `artifact-group-${galleryInstanceId}-${slug(group)}`;
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

  return <section className="workspace-artifact-gallery" aria-labelledby={galleryTitleId} data-testid="workspace-artifact-gallery">
    <header className="workspace-gallery-heading">
      <div><span className="eyebrow">Persisted results</span><h3 id={galleryTitleId}>Result gallery</h3><p>{metadataMessage}</p></div>
      <span className="workspace-gallery-count" aria-label={`${artifacts.length} Artifacts loaded`}>{artifacts.length} / {workspace.artifactCount}</span>
    </header>
    {metadataState === "LOADING" ? <GalleryState title="Loading metadata" message="Scientific payloads are not requested during initial Workspace loading." /> : null}
    {metadataState === "EMPTY" ? <GalleryState title="No Artifacts" message={metadataMessage} /> : null}
    {["FAILED", "CAP_EXCEEDED"].includes(metadataState) ? <GalleryState title="Artifact Gallery unavailable" message={metadataMessage} error /> : null}
    {metadataState === "READY" ? <div className="workspace-artifact-groups">{grouped.map(([group, items]) => <section key={group} aria-labelledby={artifactGroupId(group)}>
      <h4 id={artifactGroupId(group)}>{group}</h4>
      <ul className="workspace-artifact-list">{items.map((artifact) => <ArtifactCard key={artifactIdentity(artifact)!} artifact={artifact} panelState={panel.state} active={artifactIdentity(artifact) === activeArtifactId} selected={delivery?.context?.primary?.artifactId === artifactIdentity(artifact)} onOpen={() => openArtifact(artifact)} onDownload={() => downloadArtifact(artifact)} onSelect={() => selectArtifact(artifact)} onEvidence={() => navigateArtifact(artifact, "EVIDENCE")} onLineage={() => navigateArtifact(artifact, "PROVENANCE")} />)}</ul>
    </section>)}</div> : null}
    {activeArtifact ? <section className="workspace-active-artifact workspace-scientific-viewer" aria-labelledby={activeArtifactTitleId} data-testid="workspace-scientific-viewer">
      <header className="workspace-viewer-chrome"><div><span className="eyebrow">Scientific viewer</span><h4 id={activeArtifactTitleId}>{safeTitle(activeArtifact)}</h4><p>Validated, exact-scope payload. Viewer controls affect presentation only.</p></div><button type="button" className="secondary" onClick={() => { payloadRequestRef.current += 1; payloadControllerRef.current?.abort(); setActiveArtifactId(null); setLoadedArtifacts([]); setPayloadState("IDLE"); }}>Close viewer</button></header>
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

export function ScientificArtifactRenderer({ selected, artifacts, workspace, resultFacts = [], delivery = null, onSelection: selectionHandler }: Readonly<{ selected: Artifact; artifacts?: readonly Artifact[]; workspace: ScientificWorkspace; resultFacts?: readonly Agent2ScientificFact[]; delivery?: WorkspaceSelectionDelivery | null; onSelection?: (selection: WorkspaceSelectionContext) => void }>) {
  const onSelection = selectionHandler ?? (() => undefined);
  const artifactIndex = useMemo(() => indexArtifactsByIdentity(artifacts ?? []), [artifacts]);
  const loadedSelected = artifactIndex.get(artifactIdentity(selected) ?? "") ?? selected;
  const resolution = resolveLoadedArtifactRenderer(loadedSelected);
  const descriptor = resolution.descriptor;
  if (!descriptor) return <InertFallback artifact={selected} reason={resolution.reason} />;
  if (!loadedSelected.content && !["METADATA_ONLY", "DOWNLOAD_ONLY"].includes(descriptor.payloadMode)) return <InertFallback artifact={selected} reason="ARTIFACT_PAYLOAD_MISSING" />;
  const bundle = (artifacts ?? [loadedSelected]) as Artifact[];
  const sample = delivery?.compatibility === "EXACT" && delivery.context?.primary?.kind === "DATASET_SAMPLE" ? delivery.context.primary : null;
  const externalSampleKey = sample?.objectId && sample.sampleRef ? `${sample.objectId}:${sample.sampleRef}` : null;
  const site = delivery?.compatibility === "EXACT" && delivery.context?.primary?.kind === "PERIODIC_SITE" ? delivery.context.primary : null;
  const externalSiteId = site?.structureId === artifactChecksum(loadedSelected) ? site.siteId : null;
  const emitSample = (identity: Readonly<{ objectId: string; sampleRef: string; sampleKey: string }>) => onSelection(datasetSampleSelection(workspace, identity));
  const rendered = (() => { switch (descriptor.component) {
    case "DATASET": return <LazyBoundary><DatasetMaterialsExplorerPanel artifacts={bundle} externalSampleKey={externalSampleKey} onSampleSelection={emitSample} /></LazyBoundary>;
    case "ML": return <LazyBoundary><MaterialsMlEvaluationPanel artifacts={bundle} /></LazyBoundary>;
    case "COMPOSITION": return <LazyBoundary><CompositionSpaceExplorerPanel artifacts={bundle} externalSampleKey={externalSampleKey} onSampleSelection={emitSample} /></LazyBoundary>;
    case "STRUCTURE": return <LazyBoundary><ViewerSceneRendererSurface payload={loadedSelected.content} externalSiteId={externalSiteId} onSiteSelection={(site) => {
      if (!site) { if (/^[0-9a-f]{64}$/.test(workspace.sourceReferenceHash)) onSelection(clearedWorkspaceSelection(workspace.sourceReferenceHash)); return; }
      const selection = structureSiteSelection(workspace, loadedSelected, site);
      if (selection) onSelection(selection);
    }} /></LazyBoundary>;
    case "TRAJECTORY": return <LazyBoundary><TrajectoryViewerSurface key={artifactIdentity(loadedSelected)} payload={loadedSelected.content}
      selectedPoint={restoredTrajectoryPoint(delivery?.context, loadedSelected) ?? resultTrajectoryPoint(loadedSelected, resultFacts)} onPointSelection={workspace.sourceJobId === "source-view" ? point => {
        if (!point) { onSelection(clearedWorkspaceSelection(workspace.sourceReferenceHash)); return; }
        const selection = selectTrajectoryPoint(workspace, loadedSelected, point);
        if (selection) onSelection(selection);
      } : undefined} /></LazyBoundary>;
    case "PHONON_BAND": return <LazyBoundary><PhononBandPreviewPanel key={artifactIdentity(loadedSelected)} selected={loadedSelected} artifacts={bundle}
      selectedPoint={restoredPhononBandPoint(delivery?.context, loadedSelected)}
      onPointSelection={workspace.sourceJobId === "source-view" ? point => {
        if (!point) { onSelection(clearedWorkspaceSelection(workspace.sourceReferenceHash)); return; }
        const selection = selectPhononBandPoint(workspace, loadedSelected, point);
        if (selection) onSelection(selection);
      } : undefined} /></LazyBoundary>;
    case "PHONON_DOS": return <LazyBoundary><PhononDosPreviewPanel key={artifactIdentity(loadedSelected)} selected={loadedSelected} artifacts={bundle}
      selectedPoint={restoredPhononDosPoint(delivery?.context, loadedSelected)}
      onPointSelection={workspace.sourceJobId === "source-view" ? point => {
        if (!point) { onSelection(clearedWorkspaceSelection(workspace.sourceReferenceHash)); return; }
        const selection = selectPhononDosPoint(workspace, loadedSelected, point);
        if (selection) onSelection(selection);
      } : undefined} /></LazyBoundary>;
    case "PHONON_COMBINED": return <LazyBoundary><PhononBandDosPreviewPanel artifacts={bundle} /></LazyBoundary>;
    case "PHONON_ANIMATION": return <LazyBoundary><PhononAnimationSurface payload={loadedSelected.content} /></LazyBoundary>;
    case "BRILLOUIN_ZONE": return <LazyBoundary><BrillouinZonePreviewPanel artifacts={bundle} /></LazyBoundary>;
    case "VOLUMETRIC": {
      const dataset = bundle.find(item => item.type === "volumetric_dataset_json");
      return <LazyBoundary><VolumetricPreviewPanel artifacts={bundle}
        selectedFieldId={dataset ? restoredVolumetricField(delivery?.context, dataset) : null}
        onSelectField={dataset?.jobId === "source-view" && dataset.metadata?.sourceVersionId && dataset.sha256 ? fieldId => {
          const selection = selectVolumetricField(workspace, dataset, fieldId);
          if (selection) onSelection(selection);
        } : undefined} /></LazyBoundary>;
    }
    case "COORDINATION": return <LazyBoundary><CoordinationResultPanel artifacts={bundle} selected={loadedSelected} workspace={workspace} onSelection={onSelection} /></LazyBoundary>;
    case "COORDINATION_HISTOGRAM": return <LazyBoundary><CoordinationHistogramPanel artifacts={bundle} /></LazyBoundary>;
    case "LOCAL_ENVIRONMENT": return <LazyBoundary><LocalEnvironmentPolyhedraPanel artifacts={bundle} selected={loadedSelected} workspace={workspace} onSelection={selectionHandler} /></LazyBoundary>;
    case "EXPERIMENTAL_XRD": return <LazyBoundary><ExperimentalXrdComparisonPanel artifacts={bundle} selected={loadedSelected} workspace={workspace} onSelection={onSelection} /></LazyBoundary>;
    case "TRAJECTORY_ANALYTICS": return <LazyBoundary><TrajectoryAnalyticsPanel artifacts={bundle} selected={loadedSelected} workspace={workspace} onSelection={selectionHandler} /></LazyBoundary>;
    case "ELECTRONIC": return <LazyBoundary><ElectronicStructurePanel artifacts={bundle} selected={loadedSelected} workspace={workspace} onSelection={onSelection} /></LazyBoundary>;
    case "TEXT": return <TextFallback content={loadedSelected.content} />;
    case "GENERIC_TABLE": return loadedSelected.type === "metrics_json" && asRecord(asRecord(loadedSelected.content)?.metrics)
      ? <MetricsFallback artifact={loadedSelected} />
      : <TableFallback content={loadedSelected.content} descriptor={descriptor} workspace={workspace} externalSampleKey={externalSampleKey} onSelection={onSelection} />;
    case "GENERIC_PLOT": return <PlotFallback artifact={loadedSelected} descriptor={descriptor} workspace={workspace} onSelection={onSelection} />;
    case "JSON": return <JsonFallback content={loadedSelected.content} />;
    case "STATIC_METADATA": return <StaticMetadataFallback artifact={loadedSelected} />;
    case "DOWNLOAD_ONLY": return <DownloadOnlyFallback artifact={loadedSelected} />;
    default: return <InertFallback artifact={selected} reason="RENDERER_METADATA_ONLY" />;
  } })();
  const sourceKey = JSON.stringify([workspace.projectId, workspace.workspaceId, workspace.sourceJobId, artifactIdentity(loadedSelected), artifactVersion(loadedSelected), artifactChecksum(loadedSelected)]);
  return <Fragment key={sourceKey}>{descriptor.heavy
    ? <WorkspaceHeavyViewerLease owner={`${workspace.workspaceId}:${artifactIdentity(selected) ?? "unknown"}`}>{rendered}</WorkspaceHeavyViewerLease>
    : rendered}</Fragment>;
}

function WorkspaceArtifactRenderer({ selected, artifacts, workspace, delivery, onSelection }: Readonly<{ selected: Artifact; artifacts: readonly Artifact[]; workspace: ScientificWorkspace; delivery: WorkspaceSelectionDelivery | null; onSelection: (selection: WorkspaceSelectionContext) => void }>) {
  return <ScientificArtifactRenderer selected={selected} artifacts={artifacts} workspace={workspace} delivery={delivery} onSelection={onSelection} />;
}

function LazyBoundary({ children }: { children: ReactNode }) { return <Suspense fallback={<div className="workspace-gallery-state" role="status">正在加载科学查看器…</div>}>{children}</Suspense>; }

function MetricsFallback({ artifact }: { artifact: Artifact }) {
  const [fullValues, setFullValues] = useState(false);
  const content = artifact.content;
  const record = asRecord(content);
  const metrics = asRecord(record?.metrics);
  if (!metrics) return <JsonFallback content={content} />;
  const undefinedR2 = metrics.r2 === null && metrics.r2Status === "undefined_constant_target";
  const knownR2Status = undefinedR2 || (metrics.r2Status === "defined" && typeof metrics.r2 === "number" && Number.isFinite(metrics.r2));
  const entries = Object.entries(metrics).filter(([key]) => key !== "r2Status" || !knownR2Status)
    .map(([key, value]) => [key, key === "r2" && undefinedR2 ? "未定义（目标值为常量）" : value] as const);
  const hasShortenedValues = entries.some(([, value]) => compactMetricValue(value) !== displayScalar(value));
  const labels: Record<string, string> = { n: "样本数", mae: "平均绝对误差（MAE）", rmse: "均方根误差（RMSE）", r2: "决定系数（R²）", mse: "均方误差（MSE）", maxAbsError: "最大绝对误差", meanError: "平均误差" };
  return <section className="workspace-generic-renderer" aria-label="计算指标">
    <header className="scientific-figure-header"><div><div className="workspace-metric-heading"><h5>计算指标</h5>
      {hasShortenedValues ? <button type="button" className="product-secondary-action" aria-pressed={fullValues} onClick={() => setFullValues((current) => !current)}>完整数值</button> : null}
    </div>
      {typeof record?.targetColumn === "string" ? <p>目标列：{record.targetColumn}</p> : null}
      {typeof record?.predictionColumn === "string" ? <p>预测列：{record.predictionColumn}</p> : null}
    </div></header>
    <div className="workspace-table-scroll workspace-metrics-table" role="region" aria-label="计算指标表，可横向滚动" tabIndex={0}>
      <table><caption className="sr-only">已保存的计算指标与数值</caption><thead><tr><th scope="col">指标</th><th scope="col">数值</th></tr></thead><tbody>
        {entries.slice(0, 64).map(([key, value]) => <tr key={key}><th scope="row">{labels[key] || key}</th><td title={!fullValues && compactMetricValue(value) !== displayScalar(value) ? `完整数值：${displayScalar(value)}` : undefined}>{value === null ? "未提供" : typeof value === "object" ? "多项数值，见数据与来源" : fullValues ? displayScalar(value) : compactMetricValue(value)}</td></tr>)}
        {!entries.length ? <tr><td colSpan={2}>结果未提供指标值。</td></tr> : null}
      </tbody></table>
    </div>
    {entries.length > 64 ? <p role="note">显示前 64 / {entries.length} 项指标；完整结果保留在源文件中。</p> : null}
    <ArtifactSourceDetails artifact={artifact} />
  </section>;
}

function compactMetricValue(value: unknown): string {
  if (typeof value !== "number" || !Number.isFinite(value) || Number.isInteger(value)) return displayScalar(value);
  const formatted = formatPresentationMetricValue(String(value));
  return Number(formatted.replace(/,/gu, "")) === value ? formatted : `≈ ${formatted}`;
}

function ArtifactSourceDetails({ artifact }: { artifact: Artifact }) {
  return <details className="scientific-result-source"><summary>数据与来源</summary>
      <dl>
        {artifact.name ? <><dt>结果文件</dt><dd>{artifact.name}</dd></> : null}
        {artifact.jobId ? <><dt>分析运行</dt><dd><code>{artifact.jobId}</code></dd></> : null}
        {artifactIdentity(artifact) ? <><dt>结果标识</dt><dd><code>{artifactIdentity(artifact)}</code></dd></> : null}
        {artifact.toolCallId ? <><dt>计算步骤</dt><dd><code>{artifact.toolCallId}</code></dd></> : null}
        {artifactChecksum(artifact) ? <><dt>内容校验值</dt><dd><code>{artifactChecksum(artifact)}</code></dd></> : null}
      </dl>
      <JsonFallback content={artifact.content} />
    </details>;
}

function TableFallback({ content, descriptor, workspace, externalSampleKey = null, onSelection, columnLabels = {}, ordinalColumns = [], missingLabel, sourceRowCount, sourceRowCountIsPartial = false }: Readonly<{ content: unknown; descriptor: WorkspaceRendererDescriptor; workspace: ScientificWorkspace; externalSampleKey?: string | null; onSelection: (selection: WorkspaceSelectionContext) => void; columnLabels?: Record<string, string>; ordinalColumns?: readonly string[]; missingLabel?: string; sourceRowCount?: number; sourceRowCountIsPartial?: boolean }>) {
  const hintId = `workspace-table-scroll-hint-${useId().replace(/[^A-Za-z0-9_-]/g, "")}`;
  const scrollRef = useRef<HTMLDivElement>(null);
  const [overflows, setOverflows] = useState(false);
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<{ key: string; direction: "asc" | "desc" } | null>(null);
  const [visible, setVisible] = useState<Set<string> | null>(null);
  const [columnsOpen, setColumnsOpen] = useState(false);
  const columnsToggleRef = useRef<HTMLButtonElement>(null);
  const [page, setPage] = useState(0);
  const [selectedIdentity, setSelectedIdentity] = useState<string | null>(null);
  useEffect(() => { setSelectedIdentity(externalSampleKey); }, [externalSampleKey]);
  const allRows = savedParameterTableRows(content) ?? tableRows(content);
  const tableScalar = (value: unknown) => missingLabel && value == null ? missingLabel : displayScalar(value);
  const rows = allRows.slice(0, descriptor.maximumRows);
  const columns = [...new Set(rows.flatMap((row) => (
    Object.keys(row).filter((key) => !DATASET_ROW_IDENTITY_FIELDS.has(key))
  )))];
  const totalRowCount = Math.max(allRows.length, sourceRowCount || 0);
  const previewTruncated = sourceRowCountIsPartial || totalRowCount > rows.length;
  useEffect(() => { setPage(0); }, [query, sort, visible]);
  useEffect(() => {
    const container = scrollRef.current;
    if (!container) return;
    const measure = () => setOverflows(container.scrollWidth > container.clientWidth + 1);
    measure();
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(measure);
    observer?.observe(container);
    if (container.firstElementChild) observer?.observe(container.firstElementChild);
    window.addEventListener("resize", measure);
    return () => { observer?.disconnect(); window.removeEventListener("resize", measure); };
  }, [content, query, sort, visible, page]);
  if (!rows.length || !columns.length) return <JsonFallback content={content} />;
  const hasSampleIdentities = rows.every((row) => datasetSampleIdentityFromTableRow(row, workspace.datasetId));
  const hasSelectableRows = Boolean(workspace.datasetId && workspace.datasetVersion)
    && rows.some((row) => datasetSampleIdentityFromTableRow(row, workspace.datasetId));
  const defaultColumns = columns.filter((column) => !(hasSelectableRows && hasSampleIdentities) || !["objectId", "sampleRef"].includes(column));
  const defaultVisible = defaultColumns.length ? defaultColumns : columns;
  const activeColumns = columns.filter((column) => visible ? visible.has(column) : defaultVisible.includes(column));
  const numericColumns = new Set(activeColumns.filter(column => rows.some(row => typeof row[column] === "number") && rows.every(row => row[column] == null || typeof row[column] === "number")));
  const filteredRows = rows.filter((row) => !query.trim() || columns.some((column) => tableScalar(row[column]).toLowerCase().includes(query.trim().toLowerCase())));
  const orderedRows = sort ? [...filteredRows].sort((left, right) => {
    const a = displayScalar(left[sort.key]); const b = displayScalar(right[sort.key]);
    const numeric = Number(a) - Number(b);
    const comparison = Number.isFinite(numeric) ? numeric : a.localeCompare(b, "zh-CN");
    return sort.direction === "asc" ? comparison : -comparison;
  }) : filteredRows;
  const pageSize = 100;
  const pageCount = Math.max(1, Math.ceil(orderedRows.length / pageSize));
  const visibleRows = orderedRows.slice(page * pageSize, (page + 1) * pageSize);
  const shownStart = visibleRows.length ? page * pageSize + 1 : 0;
  const shownEnd = visibleRows.length ? page * pageSize + visibleRows.length : 0;
  const tableCount = previewTruncated
    ? `${query.trim() ? `匹配 ${orderedRows.length.toLocaleString("zh-CN")} 行${pageCount > 1 ? `，显示 ${shownStart.toLocaleString("zh-CN")}-${shownEnd.toLocaleString("zh-CN")}` : ""}` : `显示 ${shownStart.toLocaleString("zh-CN")}-${shownEnd.toLocaleString("zh-CN")} 行`} · ${activeColumns.length} 列`
    : `${pageCount > 1 ? `${shownStart.toLocaleString("zh-CN")}-${shownEnd.toLocaleString("zh-CN")} / ${orderedRows.length.toLocaleString("zh-CN")}` : query.trim() ? `${orderedRows.length.toLocaleString("zh-CN")} / ${rows.length.toLocaleString("zh-CN")}` : rows.length.toLocaleString("zh-CN")} 行 · ${activeColumns.length} 列`;
  const selectRow = (row: Record<string, unknown>) => {
    const identity = datasetSampleIdentityFromTableRow(row, workspace.datasetId);
    if (identity) {
      setSelectedIdentity(identity.sampleKey);
      onSelection(datasetSampleSelection(workspace, identity));
    }
  };
  return <section className="workspace-generic-renderer workspace-data-table" aria-label="数据表">
    <header className="workspace-table-toolbar">
      <h5 className="sr-only">数据表</h5>
      <div className="workspace-table-tools">
        <label><span className="sr-only">搜索</span><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={previewTruncated ? "搜索预览内容" : "搜索表格内容"} aria-describedby={previewTruncated ? `${hintId}-scope` : undefined} /></label>
        <button ref={columnsToggleRef} type="button" className="product-secondary-action" aria-expanded={columnsOpen} aria-controls={`${hintId}-columns`} onClick={() => setColumnsOpen(value => !value)}>列显示</button>
      </div>
      <fieldset id={`${hintId}-columns`} className="workspace-table-columns" hidden={!columnsOpen} onKeyDown={(event) => { if (event.key === "Escape") { event.preventDefault(); setColumnsOpen(false); columnsToggleRef.current?.focus(); } }}>
        <legend className="sr-only">显示列</legend>
        {columns.map((column) => <label key={column}><input type="checkbox" checked={activeColumns.includes(column)} onChange={(event) => { const next = new Set(visible || defaultVisible); event.target.checked ? next.add(column) : next.delete(column); setVisible(next.size ? next : new Set([column])); }} />{columnLabels[column] || column}</label>)}
      </fieldset>
      <p data-testid="workspace-table-count" role="status" aria-live="polite">{tableCount}</p>
      {previewTruncated ? <p id={`${hintId}-scope`} className="workspace-table-preview-note" role="note">{sourceRowCountIsPartial ? "当前预览" : "仅预览前"} {rows.length.toLocaleString("zh-CN")} 行（{sourceRowCountIsPartial ? "已读取系列共" : "全表"} {totalRowCount.toLocaleString("zh-CN")} 行），搜索与排序仅限预览。</p> : null}
    </header>
    {overflows ? <p id={hintId} className="workspace-table-mobile-hint" role="note">
      {hasSelectableRows ? "左右滑动查看完整属性；选择操作固定在左侧。" : "左右滑动查看完整列。"}
    </p> : null}
    <div className="workspace-table-frame" data-overflow={overflows}>
      <div ref={scrollRef} className="workspace-table-scroll" role="region" aria-label="数据表，可横向滚动查看完整列" aria-describedby={overflows ? hintId : undefined} tabIndex={0}>
        <table>
          <thead>
            <tr>
              {hasSelectableRows ? <th scope="col" className="workspace-table-identity-column">选择</th> : null}
              {activeColumns.map((column) => <th key={column} scope="col" data-ordinal={ordinalColumns.includes(column) || undefined} className={numericColumns.has(column) ? "table-number" : undefined} aria-sort={sort?.key === column ? (sort.direction === "asc" ? "ascending" : "descending") : "none"}><button type="button" className="table-sort-button" onClick={() => setSort((current) => ({ key: column, direction: current?.key === column && current.direction === "asc" ? "desc" : "asc" }))}>{columnLabels[column] || column}{sort?.key === column ? (sort.direction === "asc" ? " ↑" : " ↓") : ""}</button></th>)}
            </tr>
          </thead>
          <tbody>
            {!visibleRows.length ? <tr><td colSpan={activeColumns.length + (hasSelectableRows ? 1 : 0)}>{previewTruncated ? "预览范围内没有匹配项。" : hasSelectableRows ? "没有匹配的样本。" : "没有匹配的数据。"}<button type="button" className="table-row-select" onClick={() => setQuery("")}>清除搜索</button></td></tr> : null}
            {visibleRows.map((row, index) => {
              const absoluteIndex = page * pageSize + index;
              const sampleIdentity = datasetSampleIdentityFromTableRow(row, workspace.datasetId);
              const isSelected = !!sampleIdentity && selectedIdentity === sampleIdentity.sampleKey;
              return <tr key={stableRowKey(row, absoluteIndex)}>
                {hasSelectableRows ? <td className="workspace-table-identity-column">
                  {sampleIdentity ? <button type="button" className="table-row-select" aria-pressed={isSelected} title={sampleIdentity.sampleRef} aria-label={`选择样本 ${sampleIdentity.sampleRef}`} onClick={() => selectRow(row)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); selectRow(row); } }}>
                    {isSelected ? "已选择" : "选择"}
                  </button> : <span>无样本标识</span>}
                </td> : null}
                {activeColumns.map((column) => <td key={column} data-ordinal={ordinalColumns.includes(column) || undefined} className={typeof row[column] === "number" ? "table-number" : undefined}>{tableScalar(row[column])}</td>)}
              </tr>;
            })}
          </tbody>
        </table>
      </div>
    </div>
    {pageCount > 1 ? <nav className="table-pagination" aria-label="数据表分页"><button type="button" aria-label="数据表上一页" disabled={page === 0} onClick={() => setPage((value) => Math.max(0, value - 1))}>上一页</button><span aria-live="polite">第 {page + 1} / {pageCount} 页</span><button type="button" aria-label="数据表下一页" disabled={page >= pageCount - 1} onClick={() => setPage((value) => Math.min(pageCount - 1, value + 1))}>下一页</button></nav> : null}
  </section>;
}

const DATASET_ROW_IDENTITY_FIELDS = new Set([
  "sampleKey",
]);

function PlotFallback({ artifact, descriptor, workspace, onSelection }: Readonly<{ artifact: Artifact; descriptor: WorkspaceRendererDescriptor; workspace: ScientificWorkspace; onSelection: (selection: WorkspaceSelectionContext) => void }>) {
  const content = artifact.content;
  const preview = useMemo(() => plotTablePreview(content, descriptor.maximumRows), [content, descriptor.maximumRows]);
  const { rows } = preview;
  return <section className="workspace-generic-renderer" aria-label="科学图表">
    <LazyBoundary><WorkspaceGenericPlot content={content} maximumPoints={descriptor.maximumPoints} /></LazyBoundary>
    {rows.length ? <details><summary>查看数值数据 · {rows.length} 行</summary>
      <TableFallback content={{ rows }} columnLabels={preview.columnLabels} ordinalColumns={["point", "row", "column", "sourceRow"]} missingLabel="缺失" sourceRowCount={preview.totalRows} sourceRowCountIsPartial={preview.omittedTraces > 0} descriptor={descriptor} workspace={workspace} onSelection={onSelection} />
      {preview.notes.map(note => <p className="workspace-table-preview-note" role="note" key={note}>{note}</p>)}
      {preview.omittedTraces ? <p className="workspace-table-preview-note" role="note">另有 {preview.omittedTraces} 个数据系列未展开，完整内容保留在“数据与来源”中。</p> : null}
    </details> : null}
    <ArtifactSourceDetails artifact={artifact} />
  </section>;
}

function TextFallback({ content }: { content: unknown }) {
  const text = typeof content === "string" ? content : "";
  const truncated = text.length > MAX_JSON_PREVIEW_CHARS;
  return <section className="workspace-generic-renderer"><h5>文本结果</h5><pre>{text ? text.slice(0, MAX_JSON_PREVIEW_CHARS) : "文本内容暂时无法读取。"}</pre>{truncated ? <p className="workspace-table-preview-note" role="note">当前文本预览显示前 {MAX_JSON_PREVIEW_CHARS.toLocaleString("zh-CN")} / {text.length.toLocaleString("zh-CN")} 个字符；完整内容仍保留在权威 Artifact 中。</p> : null}</section>;
}
function StaticMetadataFallback({ artifact }: { artifact: Artifact }) {
  return <section className="workspace-generic-renderer workspace-metadata-fallback" role="status" aria-label="科学资源元数据">
    <p className="product-kicker">安全元数据预览</p>
    <h5>原始文件保留，可查看元数据</h5>
    <p>当前资源类型不在浏览器中展开渲染；原始科学文件没有被替换、重算或伪装成图片预览。</p>
    <dl>
      <dt>资源契约</dt><dd>{artifact.type || "未知"}@{artifactVersion(artifact)}</dd>
      <dt>文件名</dt><dd>{safeTitle(artifact)}</dd>
      <dt>文件大小</dt><dd>{formatBytes(artifact.sizeBytes)}</dd>
      <dt>校验摘要</dt><dd><code>{compact(artifactChecksum(artifact), 24)}</code></dd>
    </dl>
    <p className="workspace-metadata-fallback-note">请使用结果目录中的“Download”获取原始文件；科学来源、版本与校验信息仍保持不变。</p>
  </section>;
}
function DownloadOnlyFallback({ artifact }: { artifact: Artifact }) {
  return <section className="workspace-generic-renderer workspace-metadata-fallback" role="status" aria-label="科学资源下载">
    <p className="product-kicker">原始文件</p>
    <h5>该资源通过安全下载访问</h5>
    <p>此文件不在浏览器中执行或内联渲染。请从结果目录下载原始内容，以保留完整的科学文件语义。</p>
    <dl><dt>资源契约</dt><dd>{artifact.type || "未知"}@{artifactVersion(artifact)}</dd><dt>校验摘要</dt><dd><code>{compact(artifactChecksum(artifact), 24)}</code></dd></dl>
  </section>;
}
export function structuredDataPreview(content: unknown): { text: string; summary: string; state: "READY" | "EMPTY" | "UNAVAILABLE"; truncated: boolean } {
  if (content === undefined) return { text: "当前 Artifact 未提供可预览的结构化内容。", summary: "无可用内容", state: "UNAVAILABLE", truncated: false };
  const previewState: StructuredPreviewState = {
    remainingNodes: 2_048,
    omittedArrayItems: 0,
    omittedObjectFields: 0,
    omittedStringCharacters: 0,
    reachedNodeLimit: false,
    activeObjects: new WeakSet<object>(),
  };
  let serialized: string;
  try {
    serialized = JSON.stringify(
      boundedStructuredPreviewValue(content, previewState, 0),
      null,
      2,
    );
  } catch {
    return { text: "当前 Artifact 内容无法安全序列化；原始结果仍保留在持久化 Artifact 中。", summary: "预览不可用", state: "UNAVAILABLE", truncated: false };
  }
  if (serialized === undefined) return { text: "当前 Artifact 内容不是可预览的 JSON 值；原始结果仍保留在持久化 Artifact 中。", summary: "预览不可用", state: "UNAVAILABLE", truncated: false };
  const topLevelCount = Array.isArray(content) ? content.length : content && typeof content === "object" ? Object.keys(content).length : 1;
  const kind = Array.isArray(content) ? "数组" : content === null ? "空值" : typeof content === "object" ? "对象" : "标量";
  const empty = content === null || serialized === "" || (typeof content === "object" && topLevelCount === 0);
  const serializedOverLimit = serialized.length > MAX_JSON_PREVIEW_CHARS;
  const truncated = serializedOverLimit
    || previewState.omittedArrayItems > 0
    || previewState.omittedObjectFields > 0
    || previewState.omittedStringCharacters > 0
    || previewState.reachedNodeLimit;
  const boundedText = serializedOverLimit
    ? serialized.slice(0, MAX_JSON_PREVIEW_CHARS)
    : serialized;
  const text = truncated
    ? `${boundedText}\n${structuredPreviewLimitNote(previewState, serializedOverLimit)}`
    : serialized;
  return { text, summary: `${kind} · ${topLevelCount} ${Array.isArray(content) ? "项" : "个顶层字段"}${truncated ? " · 有界预览" : ""}`, state: empty ? "EMPTY" : "READY", truncated };
}

type StructuredPreviewState = {
  remainingNodes: number;
  omittedArrayItems: number;
  omittedObjectFields: number;
  omittedStringCharacters: number;
  reachedNodeLimit: boolean;
  activeObjects: WeakSet<object>;
};

function boundedStructuredPreviewValue(
  value: unknown,
  state: StructuredPreviewState,
  depth: number,
): unknown {
  if (typeof value === "string") {
    const maximumStringCharacters = 4_000;
    if (value.length <= maximumStringCharacters) return value;
    state.omittedStringCharacters += value.length - maximumStringCharacters;
    return `${value.slice(0, maximumStringCharacters)}…`;
  }
  if (
    value === null
    || typeof value === "number"
    || typeof value === "boolean"
    || value === undefined
  ) return value;
  if (typeof value !== "object") {
    throw new TypeError("Unsupported JSON preview value.");
  }
  if (state.activeObjects.has(value)) {
    throw new TypeError("Circular JSON preview value.");
  }
  if (state.remainingNodes <= 0 || depth >= 12) {
    state.reachedNodeLimit = true;
    return "[预览层级或节点预算已达上限]";
  }
  state.remainingNodes -= 1;
  state.activeObjects.add(value);
  try {
    if (Array.isArray(value)) {
      const maximumItems = Math.min(value.length, 128);
      const result: unknown[] = [];
      for (let index = 0; index < maximumItems; index += 1) {
        if (state.remainingNodes <= 0) {
          state.reachedNodeLimit = true;
          state.omittedArrayItems += value.length - index;
          break;
        }
        result.push(boundedStructuredPreviewValue(value[index], state, depth + 1));
      }
      if (maximumItems < value.length && !state.reachedNodeLimit) {
        state.omittedArrayItems += value.length - maximumItems;
      }
      return result;
    }
    const source = value as Record<string, unknown>;
    const keys = Object.keys(source);
    const maximumFields = Math.min(keys.length, 64);
    const result: Record<string, unknown> = {};
    for (let index = 0; index < maximumFields; index += 1) {
      if (state.remainingNodes <= 0) {
        state.reachedNodeLimit = true;
        state.omittedObjectFields += keys.length - index;
        break;
      }
      const key = keys[index];
      result[key] = boundedStructuredPreviewValue(source[key], state, depth + 1);
    }
    if (maximumFields < keys.length && !state.reachedNodeLimit) {
      state.omittedObjectFields += keys.length - maximumFields;
    }
    return result;
  } finally {
    state.activeObjects.delete(value);
  }
}

function structuredPreviewLimitNote(
  state: StructuredPreviewState,
  serializedOverLimit: boolean,
): string {
  const details = [
    state.omittedArrayItems ? `省略 ${state.omittedArrayItems.toLocaleString("zh-CN")} 个数组项` : "",
    state.omittedObjectFields ? `省略 ${state.omittedObjectFields.toLocaleString("zh-CN")} 个对象字段` : "",
    state.omittedStringCharacters ? `省略 ${state.omittedStringCharacters.toLocaleString("zh-CN")} 个长文本字符` : "",
    state.reachedNodeLimit ? "达到预览层级或节点预算" : "",
    serializedOverLimit ? "达到显示字符上限" : "",
  ].filter(Boolean);
  return `[预览已限制${details.length ? `：${details.join("；")}` : ""}；完整内容仍保留在 Artifact 中]`;
}
function JsonFallback({ content }: { content: unknown }) { const preview = structuredDataPreview(content); return <section className="workspace-generic-renderer workspace-structured-preview" aria-label="结构化数据预览"><header><h5>结构化数据</h5><span>{preview.summary}</span></header>{preview.state === "EMPTY" ? <p className="workspace-structured-empty" role="note">该结果的结构化内容为空；下方保留精确 JSON 表示。</p> : null}<pre tabIndex={0} aria-label="结构化数据 JSON">{preview.text}</pre></section>; }
function InertFallback({ artifact, reason }: { artifact: Artifact; reason: string }) {
  const copy = inertReasonCopy(reason);
  return <section className="workspace-generic-renderer workspace-inert-fallback" role="status">
    <h5>{copy.title}</h5>
    <p>{copy.body}</p>
    <details><summary>查看技术详情</summary><p className="workspace-inert-fallback-code"><code>{reason}</code></p></details>
    <dl><dt>数据契约</dt><dd>{artifact.type || "未知"}@{artifactVersion(artifact)}</dd><dt>校验摘要</dt><dd>{compact(artifactChecksum(artifact), 20)}</dd></dl>
  </section>;
}
function inertReasonCopy(reason: string): { title: string; body: string } {
  if (reason === "ARTIFACT_PAYLOAD_MISSING" || reason.includes("PAYLOAD_MISSING")) {
    return { title: "当前解析资源暂时无法读取", body: "科学结果和来源元数据仍被保留，但当前精确 payload 不可用。请稍后重试或打开来源与属性；系统不会用其他版本替代它。" };
  }
  if (reason.includes("UNSUPPORTED") || reason.includes("METADATA_ONLY")) {
    return { title: "当前资源没有可用的专业查看器", body: "该资源契约暂未映射到受信任的查看器；你仍可查看有界元数据或原始结构化内容，系统不会执行未知组件。" };
  }
  return { title: "当前资源无法安全呈现", body: "查看器拒绝了当前资源的呈现请求。原始科学记录没有被改写，也不会执行 HTML、脚本、外部页面或猜测出的渲染器。" };
}
function GalleryState({ title, message, error = false }: { title: string; message: string; error?: boolean }) {
  const titleCopy = title === "Artifact Gallery unavailable" ? "科学结果暂时无法读取" : title === "No Artifacts" ? "暂无已保存的科学结果" : title === "Loading metadata" ? "正在读取结果目录" : title;
  const messageCopy = message === "Scientific payloads are not requested during initial Workspace loading."
    ? "正在读取已保存结果的元数据；初始加载不会请求科学 payload。"
    : message === "No persisted Artifacts are available for this Job."
      ? "当前分析尚未保存可查看的科学结果。"
      : error
        ? "结果目录暂时无法读取；科学记录没有被修改，请稍后重试。"
        : message;
  return <div className="workspace-gallery-state" role={error ? "alert" : "status"}><strong>{titleCopy}</strong><span>{messageCopy}</span></div>;
}

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
function stableRowKey(row: Record<string, unknown>, index: number) {
  const objectId = typeof row.objectId === "string" ? row.objectId : "";
  for (const key of ["sampleKey", "sample_id", "sampleRef", "id"]) {
    if (typeof row[key] === "string" && row[key]) return `${key}:${objectId ? `${objectId}:` : ""}${row[key]}`;
  }
  if (objectId) return `objectId:${objectId}:row-${index}`;
  return `display-row-${index}`;
}
function displayScalar(value: unknown) { if (typeof value === "number") return Number.isFinite(value) ? String(value) : "invalid"; if (["string", "boolean"].includes(typeof value)) return String(value).slice(0, 200); return value === null ? "null" : "[structured]"; }
