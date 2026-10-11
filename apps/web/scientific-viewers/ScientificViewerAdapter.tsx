"use client";

import { savedXrdTableRows } from "../app/lib/scientific-xrd-table";
import type { Agent2ScientificFact } from "../app/lib/agent2-research-api";
import { useEffect, useMemo, useRef, useState } from "react";

import {
  getPlannerArtifactContent,
  type Artifact,
  type DatasetSourceResource,
} from "../app/lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext } from "../app/lib/workspace-api";
import { WorkspaceSelectionStore, type WorkspaceSelectionDelivery } from "../shared/workspace/workspace-selection-runtime";
import { VOLUMETRIC_BROWSER_CAPS } from "./volumetric-viewer/volumetricViewerTypes";
import { sha256HexSync } from "./volumetric-viewer/volumetricHash";
import { ScientificArtifactRenderer } from "./workspace/WorkspaceArtifactGallery";
import { artifactIdentity, resolveArtifactRenderer, resolveLoadedArtifactRenderer } from "../shared/workspace/workspace-renderer-registry";
import { ProductLink as Link } from "../shared/layout/ProductNavigation";
import { validateViewerSceneForRenderer } from "./viewer-scene/viewerSceneRendererValidation";

export function ScientificSourceViewer({ projectId, resource, resources = [resource], selection = null, onSelection = () => undefined }: Readonly<{ projectId: string; resource: DatasetSourceResource; resources?: readonly DatasetSourceResource[]; selection?: WorkspaceSelectionContext | null; onSelection?: (selection: WorkspaceSelectionContext) => void }>) {
  const artifacts = useMemo(() => sourceResourceArtifacts(resource, resources), [resource, resources]);
  const artifact = useMemo(() => sourcePrimaryArtifact(resource, artifacts), [resource, artifacts]);
  const renderArtifact = (item: Artifact) => {
    const owner = item.metadata?.sourceObjectId === resource.objectId ? resource
      : resources.find(candidate => candidate.datasetId === resource.datasetId && candidate.objectId === item.metadata?.sourceObjectId);
    return owner ? <ScientificSourceArtifact key={artifactIdentity(item)} projectId={projectId} resource={owner}
      artifact={item} artifacts={artifacts} selection={selection} onSelection={onSelection} /> : null;
  };
  const phononBand = artifacts.find((item) => item.type === "phonon_band_json");
  const phononDos = artifacts.find((item) => item.type === "phonon_dos_json");
  const xrdPattern = artifacts.find((item) => item.type === "plotly_json");
  const xrdStructure = artifacts.find((item) => item.type === "structure_json");
  if (["PhononBand", "PhononDos"].includes(resource.objectType) && phononBand && phononDos) {
    const ordered = resource.objectType === "PhononDos" ? [artifact, phononBand] : [artifact, phononDos];
    return <section className="phonon-source-group" aria-label="声子能带与声子态密度">{ordered.map(renderArtifact)}</section>;
  }
  if (["DataFrame", "Structure"].includes(resource.objectType) && xrdPattern && xrdStructure) {
    const ordered = resource.objectType === "Structure" ? [artifact, xrdPattern] : [artifact, xrdStructure];
    return <section aria-label="实验 XRD 与结构上下文">{ordered.map(renderArtifact)}</section>;
  }
  return renderArtifact(artifact);
}

function ScientificSourceArtifact({ projectId, resource, artifact, artifacts, selection, onSelection }: {
  projectId: string; resource: DatasetSourceResource; artifact: Artifact; artifacts: readonly Artifact[];
  selection: WorkspaceSelectionContext | null; onSelection: (selection: WorkspaceSelectionContext) => void;
}) {
  const workspace = useMemo(() => sourceViewerContext(projectId, resource), [projectId, resource]);
  const delivery = useMemo<WorkspaceSelectionDelivery | null>(() => {
    if (!selection || selection.cleared || selection.compatibility !== "EXACT") return null;
    try {
      const context = new WorkspaceSelectionStore(workspace, selection).current();
      return { panelId: "source-view", originPanelId: null, context, compatibility: "EXACT", reason: "Restored exact scientific source selection.", transaction: 0 };
    } catch {
      return null;
    }
  }, [selection, workspace]);
  return <ScientificArtifactRenderer selected={artifact} artifacts={artifacts} workspace={workspace} delivery={delivery} onSelection={onSelection} />;
}

type ScientificResultViewerProps = Readonly<{
  projectId: string;
  datasetId?: string | null;
  jobId: string;
  selected: Artifact;
  artifacts: readonly Artifact[];
  resultFacts?: readonly Agent2ScientificFact[];
}>;

export function ScientificResultViewer(props: ScientificResultViewerProps) {
  // A different exact result must never briefly render the previous payload.
  const scope = JSON.stringify([props.projectId, props.datasetId, resultViewerLoadKey(props.jobId, [props.selected])]);
  return <ScopedScientificResultViewer key={scope} {...props} />;
}

function ScopedScientificResultViewer({
  projectId,
  datasetId,
  jobId,
  selected,
  artifacts,
  resultFacts = [],
}: ScientificResultViewerProps) {
  const viewerSelected = normalizeResultArtifactForViewer(selected);
  const descriptor = resolveArtifactRenderer(viewerSelected).descriptor;
  const bundleTypes = new Set(descriptor?.bundleArtifactTypes ?? [viewerSelected.type]);
  const bundle = [selected, ...selectResultViewerBundle(viewerSelected, artifacts.filter((item) => bundleTypes.has(item.type as never)), jobId)
    .filter((item) => artifactIdentity(item) !== artifactIdentity(selected))];
  const { entries, retry } = useResultArtifactReads(jobId, bundle);
  const selectedKey = resultViewerLoadKey(jobId, [selected]);
  const selectedEntry = entries.find((entry) => entry.key === selectedKey);
  const companions = entries.filter((entry) => entry.key !== selectedKey);
  const incomplete = companions.filter((entry) => entry.status !== "ready");
  const normalized = useMemo(() => entries.flatMap((entry) => entry.loaded ? [normalizeResultArtifactForViewer(entry.loaded)] : []), [entries]);
  const loadedSelected = normalized.find((item) => artifactIdentity(item) === artifactIdentity(selected));
  const workspace = useMemo(() => resultViewerContext(projectId, datasetId, jobId, viewerSelected), [datasetId, jobId, projectId, viewerSelected]);
  return <>
    {incomplete.length ? <div className="product-state scientific-viewer-partial-state" role="status">
      <strong>辅助内容尚未完整读取</strong>
      <p>已读取的内容会保留，重试仅重新读取失败项。</p>
      <ul>{incomplete.map((entry) => <li key={entry.key}>
        {entry.artifact.name || artifactIdentity(entry.artifact) || "辅助结果"}：{entry.status === "pending" ? "正在读取…" : artifactContentFailureMessage(entry.code)}
      </li>)}</ul>
      {incomplete.some((entry) => entry.status === "failed" && artifactContentCanRetry(entry.code)) ?
        <button type="button" className="product-secondary-action" onClick={() => retry(incomplete)}>重新加载缺失内容</button> : null}
    </div> : null}
    {loadedSelected ? <ScientificArtifactRenderer selected={selectProductRendererArtifact(loadedSelected, normalized)} artifacts={normalized} workspace={workspace} resultFacts={resultFacts} /> : <>
      {companions.some((entry) => entry.status === "ready") ? <p>已读取 {companions.filter((entry) => entry.status === "ready").length} 项辅助内容，等待当前结果恢复。</p> : null}
      {!selectedEntry || selectedEntry.status === "pending"
        ? <ResultViewerLoadingState artifact={viewerSelected} projectId={projectId} datasetId={datasetId} />
        : <ResultViewerFailureState selected={selected} projectId={projectId} datasetId={datasetId} failureCode={selectedEntry.code || "ARTIFACT_CONTENT_LOAD_FAILED"} retry={() => retry([selectedEntry])} />}
    </>}
  </>;
}

function ResultViewerFailureState({ selected, projectId, datasetId, failureCode, retry }: {
  selected: Artifact; projectId: string; datasetId?: string | null; failureCode: string; retry: () => void;
}) {
  const state = failureCode === "ARTIFACT_CONTENT_NOT_FOUND" ? "missing"
    : failureCode === "ARTIFACT_CONTENT_GONE" ? "gone"
      : failureCode === "ARTIFACT_CONTENT_TOO_LARGE" ? "oversized" : "failed";
  if (state === "missing") return <div className="product-state" role="status">
    <p className="product-kicker">Artifact 可用性</p>
    <h3>原始结果内容当前不可用</h3>
    <p>Artifact 元数据、校验值与科学谱系仍然保留；系统没有替换为其他结果或较新版本。</p>
    <div className="product-row-actions">
      <button type="button" className="product-secondary-action" onClick={retry}>重新检查存储</button>
      {datasetId ? <Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/data?dataset=${encodeURIComponent(datasetId)}`}>返回数据源</Link> : null}
    </div>
    <ViewerArtifactMetadata artifact={selected} />
  </div>;
  if (state === "gone") return <div className="product-state" role="status">
    <p className="product-kicker">Artifact 历史可用性</p>
    <h3>原始 Artifact 已永久不可用</h3>
    <p>Artifact 元数据、校验值与科学谱系继续保留；此状态不可通过重试恢复，系统也不会替换为其他结果或较新版本。</p>
    {datasetId ? <Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/data?dataset=${encodeURIComponent(datasetId)}`}>返回数据源</Link> : null}
    <ViewerArtifactMetadata artifact={selected} />
  </div>;
  if (state === "oversized") return <div className="product-state" role="status">
    <p className="product-kicker">Artifact 浏览上限</p>
    <h3>此 Artifact 超出安全浏览范围</h3>
    <p>为了避免冻结浏览器，系统未读取此大型 payload。科学结果、精确 Artifact 身份与校验值保持不变。</p>
    {datasetId ? <Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/data?dataset=${encodeURIComponent(datasetId)}`}>返回数据源</Link> : null}
    <ViewerArtifactMetadata artifact={selected} />
    <details><summary>技术详情</summary><code>{failureCode}</code></details>
  </div>;
  if (state === "failed") return <div className="product-state" role="alert">
    <p className="product-kicker">科学结果</p>
    <h3>{failureCode === "ARTIFACT_CONTENT_TIMEOUT" ? "科学结果读取超时" : "科学结果加载失败"}</h3>
    <p>{artifactContentFailureMessage(failureCode)}。已读取的辅助内容和结果来源会保留。</p>
    <div className="product-row-actions">
      {artifactContentCanRetry(failureCode) ? <button type="button" className="product-primary-action" onClick={retry}>重新加载</button> : null}
      {datasetId ? <Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/data?dataset=${encodeURIComponent(datasetId)}`}>返回数据源</Link> : null}
    </div>
    <ViewerArtifactMetadata artifact={selected} />
    <details><summary>技术详情</summary><code>{failureCode || "ARTIFACT_CONTENT_LOAD_FAILED"}</code></details>
  </div>;
  return null;
}

function ResultViewerLoadingState({ artifact, projectId, datasetId }: { artifact: Artifact; projectId: string; datasetId?: string | null }) {
  return <div className="product-loading" role="status" aria-label="科学结果载荷正在加载">
    <p className="product-kicker">科学结果已定位</p>
    <h3>正在加载科学结果载荷…</h3>
    <p>结果来源与恢复入口已可用；专业查看器正在读取已验证载荷。</p>
    <ViewerArtifactMetadata artifact={artifact} />
    {datasetId ? <div className="product-row-actions"><Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/data?dataset=${encodeURIComponent(datasetId)}`}>返回数据源</Link></div> : null}
  </div>;
}

function ViewerArtifactMetadata({ artifact }: { artifact: Artifact }) {
  const identity = artifactIdentity(artifact);
  const projectId = typeof artifact.metadata?.projectId === "string" ? artifact.metadata.projectId : null;
  return <details>
    <summary>技术来源与精确身份</summary>
    <p>Artifact：<code>{identity || "未提供"}</code></p>
    <p>类型：<code>{artifact.type || "未提供"}@{artifact.version || "1"}</code></p>
    {artifact.name ? <p>名称：{artifact.name}</p> : null}
    {artifact.toolCallId ? <p>来源 ToolCall：<code>{artifact.toolCallId}</code></p> : null}
    {projectId ? <p>项目：<code>{projectId}</code></p> : null}
    {artifact.sha256 || artifact.contentHash ? <p>SHA-256：<code>{artifact.sha256 || artifact.contentHash}</code></p> : null}
  </details>;
}

type ResultArtifactRead = {
  key: string;
  artifact: Artifact;
  status: "pending" | "ready" | "failed";
  loaded?: Artifact;
  code?: string;
};

/** Each exact payload owns its deadline and retry. Reconciliation only drops
 * changed/removed identities; pending and successful siblings stay intact. */
function useResultArtifactReads(jobId: string, bundle: readonly Artifact[]) {
  const [snapshot, setSnapshot] = useState<Map<string, ResultArtifactRead>>(new Map());
  const reads = useRef(new Map<string, ResultArtifactRead>());
  const requests = useRef(new Map<string, { controller: AbortController; timer: ReturnType<typeof setTimeout> }>());
  const loadKey = resultViewerLoadKey(jobId, bundle);
  const publish = () => setSnapshot(new Map(reads.current));
  const start = (artifact: Artifact) => {
    const key = resultViewerLoadKey(jobId, [artifact]);
    const prior = reads.current.get(key);
    if (prior?.status === "ready" || requests.current.has(key)) return;
    const id = artifactIdentity(artifact);
    if (artifact.jobId && artifact.jobId !== jobId) {
      reads.current.set(key, { key, artifact, status: "failed", code: "ARTIFACT_CONTENT_SCOPE_MISMATCH" });
      publish();
      return;
    }
    if (artifact.content !== undefined) {
      reads.current.set(key, { key, artifact, status: "ready", loaded: artifact });
      publish();
      return;
    }
    if (!id) {
      reads.current.set(key, { key, artifact, status: "failed", code: "ARTIFACT_CONTENT_LOAD_FAILED" });
      publish();
      return;
    }
    reads.current.set(key, { key, artifact, status: "pending" });
    const controller = new AbortController();
    const settle = (result: Pick<ResultArtifactRead, "status" | "loaded" | "code">) => {
      if (requests.current.get(key)?.controller !== controller) return;
      clearTimeout(requests.current.get(key)?.timer);
      requests.current.delete(key);
      reads.current.set(key, { key, artifact, ...result });
      publish();
    };
    const timer = setTimeout(() => {
      controller.abort();
      settle({ status: "failed", code: "ARTIFACT_CONTENT_TIMEOUT" });
    }, 10_000);
    requests.current.set(key, { controller, timer });
    publish();
    void (async () => {
      try {
        const bytes = await getPlannerArtifactContent(jobId, id, {
          signal: controller.signal,
          maximumBytes: resolveArtifactRenderer(artifact).descriptor?.maximumPayloadBytes,
        });
        if (!controller.signal.aborted) settle({ status: "ready", loaded: { ...artifact, content: decodeArtifactPayload(bytes, artifact) } });
      } catch (reason) {
        if (!controller.signal.aborted) settle({ status: "failed", code: artifactContentFailureCode(reason) });
      }
    })();
  };
  useEffect(() => () => {
    requests.current.forEach(({ controller, timer }) => { clearTimeout(timer); controller.abort(); });
    requests.current.clear();
    reads.current.clear();
  }, []);
  useEffect(() => {
    const keys = new Set(bundle.map((artifact) => resultViewerLoadKey(jobId, [artifact])));
    for (const key of reads.current.keys()) {
      if (keys.has(key)) continue;
      const request = requests.current.get(key);
      if (request) { clearTimeout(request.timer); request.controller.abort(); }
      requests.current.delete(key);
      reads.current.delete(key);
    }
    for (const artifact of bundle) {
      if (!reads.current.has(resultViewerLoadKey(jobId, [artifact]))) start(artifact);
    }
    publish();
  }, [loadKey]);
  const entries = useMemo(() => bundle.map((artifact): ResultArtifactRead => {
    const key = resultViewerLoadKey(jobId, [artifact]);
    return snapshot.get(key) ?? { key, artifact, status: "pending" };
  }), [loadKey, snapshot]);
  return {
    entries,
    retry: (failed: readonly ResultArtifactRead[]) => {
      for (const entry of failed) {
        const current = reads.current.get(entry.key);
        if (current?.status === "failed" && artifactContentCanRetry(current.code)) start(current.artifact);
      }
    },
  };
}

const ARTIFACT_FAILURE_MESSAGES: Record<string, string> = {
  ARTIFACT_CONTENT_LOAD_FAILED: "暂时无法读取，请重试",
  ARTIFACT_CONTENT_TIMEOUT: "读取超过 10 秒，请重试",
  ARTIFACT_CONTENT_INVALID: "内容格式校验失败，请重试",
  ARTIFACT_CONTENT_BYTE_MISMATCH: "内容完整性校验失败，请重试",
  ARTIFACT_CONTENT_SCOPE_MISMATCH: "结果与当前任务的来源不一致，未加载内容",
  ARTIFACT_CONTENT_LIMIT_EXCEEDED: "内容大小未通过浏览校验，请重试",
  ARTIFACT_CONTENT_NOT_FOUND: "原始内容当前不可用，可重新检查存储",
  ARTIFACT_CONTENT_GONE: "原始内容已永久不可用，无法通过重试恢复",
  ARTIFACT_CONTENT_TOO_LARGE: "内容超出安全浏览范围，无法在此加载",
};

function artifactContentFailureMessage(code?: string): string {
  return ARTIFACT_FAILURE_MESSAGES[code || ""] || ARTIFACT_FAILURE_MESSAGES.ARTIFACT_CONTENT_LOAD_FAILED;
}

function artifactContentCanRetry(code?: string): boolean {
  return !["ARTIFACT_CONTENT_GONE", "ARTIFACT_CONTENT_TOO_LARGE", "ARTIFACT_CONTENT_SCOPE_MISMATCH"].includes(code || "");
}

function artifactContentFailureCode(reason: unknown): string {
  if (reason instanceof SyntaxError) return "ARTIFACT_CONTENT_INVALID";
  if (reason && typeof reason === "object") {
    const details = "details" in reason ? (reason as { details?: unknown }).details : undefined;
    if (details && typeof details === "object" && "detail" in details) {
      const detail = (details as { detail?: unknown }).detail;
      if (detail && typeof detail === "object" && "code" in detail && typeof detail.code === "string") {
        return Object.hasOwn(ARTIFACT_FAILURE_MESSAGES, detail.code) ? detail.code : "ARTIFACT_CONTENT_LOAD_FAILED";
      }
    }
    if ("message" in reason && typeof reason.message === "string") {
      return Object.hasOwn(ARTIFACT_FAILURE_MESSAGES, reason.message) ? reason.message : "ARTIFACT_CONTENT_LOAD_FAILED";
    }
  }
  return "ARTIFACT_CONTENT_LOAD_FAILED";
}

/** Keep a composite viewer's request set semantic and bounded. The registry
 * declares compatible types, but a Job can contain the same type for several
 * independent steps. Loading every sibling table makes a result appear stuck
 * while the renderer only needs the selected scientific bundle. */
export function selectResultViewerBundle(selected: Artifact, candidates: readonly Artifact[], jobId = selected.jobId): Artifact[] {
  const producer = artifactProducerIdentity(selected);
  // Type and filename describe format, never source ownership. A multi-material
  // Job can publish identically named companions for independent ToolCalls.
  if (!producer) return [selected];
  const scoped = candidates.filter((item) => (!jobId || !item.jobId || item.jobId === jobId)
    && artifactProducerIdentity(item) === producer);
  const name = String(selected.name || "").toLowerCase();
  const keepName = (item: Artifact, pattern: RegExp) => pattern.test(String(item.name || "").toLowerCase());
  if (selected.type === "phonon_band_dos_json" || /phonon_band_dos/.test(name)) {
    return scoped.filter((item) => keepName(item, /^phonon_band_dos(?:_|\.)/) || item === selected);
  }
  if (selected.type === "phonon_band_json" || /phonon_band(?:_|\.)/.test(name)) {
    return scoped.filter((item) => keepName(item, /^phonon_band(?:_|\.)/) && !keepName(item, /^phonon_band_dos(?:_|\.)/) || item === selected);
  }
  if (selected.type === "phonon_dos_json" || /phonon_dos/.test(name)) {
    return scoped.filter((item) => keepName(item, /^phonon_dos(?:_|\.)/) && !keepName(item, /^phonon_band_dos(?:_|\.)/) || item === selected);
  }
  if (selected.type === "plotly_json") {
    // A generic figure can have a richer, authoritative product contract in a
    // table_json companion. Keep that pair exact to one ToolCall so a
    // multi-capability Job cannot mix XRD, trajectory, or Dataset products.
    return scoped.filter((item) => ["plotly_json", "table_json"].includes(String(item.type)));
  }
  if (["electronic_band_json", "electronic_dos_json"].includes(String(selected.type))) {
    return scoped.filter((item) => ["electronic_band_json", "electronic_dos_json"].includes(String(item.type)));
  }
  return scoped;
}

export function selectProductRendererArtifact(selected: Artifact, candidates: readonly Artifact[]): Artifact {
  if (selected.type !== "plotly_json") return selected;
  const producer = artifactProducerIdentity(selected);
  if (!producer) return selected;
  const product = selectResultViewerBundle(selected, candidates).find((item) => {
    if (item.type !== "table_json" || artifactProducerIdentity(item) !== producer) return false;
    const descriptor = resolveLoadedArtifactRenderer(item).descriptor;
    return Boolean(descriptor && !["GENERIC_TABLE", "GENERIC_PLOT", "JSON", "TEXT"].includes(descriptor.component));
  });
  return product ?? selected;
}

export function resultViewerLoadKey(jobId: string, artifacts: readonly Artifact[]): string {
  const artifactKeys = artifacts.map((artifact) => [
    artifactIdentity(artifact) || "missing",
    artifact.type || "unknown",
    artifact.version || "1",
    artifact.sha256 || artifact.contentHash || "no-content-hash",
    artifact.sizeBytes ?? "unknown-size",
    artifact.content === undefined ? "remote" : "inline",
    artifact.jobId || jobId,
    artifactProducerIdentity(artifact) || "unknown-producer",
  ].join(":"));
  return `${jobId}\u0000${artifactKeys.sort().join("\u0001")}`;
}

function artifactProducerIdentity(artifact: Artifact): string | null {
  const metadata = artifact.metadata && typeof artifact.metadata === "object" ? artifact.metadata as Record<string, unknown> : {};
  const provenance = artifact.provenance && typeof artifact.provenance === "object" ? artifact.provenance as Record<string, unknown> : {};
  const identities = (values: unknown[]) => [...new Set(values.filter((value): value is string => typeof value === "string" && Boolean(value.trim())).map(value => value.trim()))];
  const calls = identities([
    artifact.toolCallId,
    metadata.toolCallId,
    metadata.tool_call_id,
    provenance.toolCallId,
    provenance.tool_call_id,
  ]);
  if (calls.length) return calls.length === 1 ? `call:${calls[0]}` : null;
  const steps = identities([
    metadata.stepId,
    metadata.step_id,
    provenance.stepId,
    provenance.step_id,
  ]);
  return steps.length === 1 ? `step:${steps[0]}` : null;
}

export function normalizeResultArtifactForViewer(artifact: Artifact): Artifact {
  // structure.summary emits a structured summary using the historical
  // structure_json type; it is not a validated viewer_scene and must not
  // enter the 3D renderer.
  const metadata = artifact.metadata && typeof artifact.metadata === "object" ? artifact.metadata as Record<string, unknown> : {};
  const provenance = artifact.provenance && typeof artifact.provenance === "object" ? artifact.provenance as Record<string, unknown> : {};
  const toolId = String(metadata.toolId || provenance.toolId || "").toLowerCase();
  if (toolId === "structure.summary" && artifact.type === "structure_json") {
    return { ...artifact, type: "table_json", content: structureSummaryTableContent(artifact.content) };
  }
  if (artifact.type === "table_json" && artifact.content && typeof artifact.content === "object" && !Array.isArray(artifact.content)) {
    const content = artifact.content as Record<string, unknown>;
    if (!Array.isArray(content.rows) && typeof content.schemaVersion !== "string" && typeof content.schema_version !== "string") {
      return { ...artifact, content: structureSummaryTableContent(content) };
    }
  }
  return artifact;
}

function structureSummaryTableContent(content: unknown): unknown {
  if (!content || typeof content !== "object" || Array.isArray(content)) return content;
  const source = content as Record<string, unknown>;
  if (Array.isArray(source.rows)) return content;
  const rows = Object.entries(source).slice(0, 32).map(([property, value]) => ({
    property,
    value: scalarSummaryValue(value),
  }));
  return rows.length ? { rows } : content;
}

function scalarSummaryValue(value: unknown): string | number | boolean {
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return value;
  if (Array.isArray(value)) return `${value.length} 项`;
  if (value && typeof value === "object") return `${Object.keys(value).length} 个字段`;
  return "未提供";
}

export function sourceResourceArtifact(resource: DatasetSourceResource): Artifact {
  const volumetric = projectVolumetricSourceArtifacts(resource);
  if (volumetric) return volumetric[0];
  const experimentalXrd = experimentalXrdPlot(resource.payload);
  const electronic = projectElectronicSource(resource);
  const type = experimentalXrd ? "plotly_json" : electronic ? sourceArtifactType(resource.objectType) : resource.objectType === "VolumetricData" ? "table_json" : sourceArtifactType(resource.objectType);
  const sourceScene = sourceStructurePreview(resource);
  const structureScene = resource.objectType === "Structure" ? sourceScene ?? projectStructureSource(resource.payload, resource.objectHash) : null;
  const atomsScene = resource.objectType === "Atoms" ? sourceScene ?? projectAtomsSource(resource.payload, resource.objectHash) : null;
  const fallbackScene = structureScene ?? atomsScene;
  if (isRecord(fallbackScene) && !sourceScene && resource.viewerSceneIssue) {
    fallbackScene.metadata = { ...(isRecord(fallbackScene.metadata) ? fallbackScene.metadata : {}), display_only: true };
    fallbackScene.warnings = [...(Array.isArray(fallbackScene.warnings) ? fallbackScene.warnings : []), {
      code: "VIEWER_PREVIEW_CONNECTIONS_UNAVAILABLE", message: sourcePreviewIssue(resource.viewerSceneIssue),
    }];
  }
  const content = experimentalXrd ?? electronic ?? structureScene ?? atomsScene ?? (resource.objectType === "VolumetricData" ? projectVolumetricSourceSummary(resource.payload) : null) ?? (resource.objectType === "DataFrame" && Array.isArray(resource.payload)
    ? { rows: resource.payload }
    : resource.payload);
  return {
    artifactId: `source:${resource.objectId}`,
    id: `source:${resource.objectId}`,
    jobId: "source-view",
    type,
    version: "1",
    name: sourceResourceDisplayName(resource),
    sha256: resource.objectHash || null,
    contentType: "application/json",
    content,
    metadata: { sourceObjectType: resource.objectType, sourceDatasetId: resource.datasetId, sourceObjectId: resource.objectId, sourceVersionId: resource.versionId },
  };
}

function sourceStructurePreview(resource: DatasetSourceResource): Record<string, unknown> | null {
  if (!["Structure", "Atoms"].includes(resource.objectType) || !resource.objectHash) return null;
  const scene = resource.viewerScene;
  if (!isRecord(scene) || !isRecord(scene.provenance) || !isRecord(scene.source)) return null;
  const provenance = scene.provenance;
  if (provenance.projection !== "source_structure_preview/1.0"
      || provenance.source_hash !== resource.objectHash || scene.source.hash !== resource.objectHash
      || provenance.source_object_id !== resource.objectId
      || (provenance.source_version_id ?? undefined) !== (resource.versionId ?? undefined)
      || (provenance.source_dataset_id != null && provenance.source_dataset_id !== resource.datasetId)
      || !validateViewerSceneForRenderer(scene).valid) return null;
  return scene;
}

function sourcePreviewIssue(code: string): string {
  if (["VIEWER_NEIGHBOR_SITE_LIMIT", "VIEWER_NEIGHBOR_WORK_LIMIT", "VIEWER_NEIGHBOR_OFFSET_LIMIT", "VIEWER_NEIGHBOR_SPECIES_LIMIT"].includes(code)) {
    return "近邻搜索超出快速预览范围，当前仅显示原子；可在研究中选择适合此结构的连接规则。";
  }
  return "当前结构尚不能生成可靠的近邻预览，原始原子坐标仍然保留。";
}

export function sourceResourceArtifacts(selected: DatasetSourceResource, resources: readonly DatasetSourceResource[]): Artifact[] {
  const companions = resources.filter((item) => item.datasetId === selected.datasetId && isCompanionResource(selected, item));
  const counts = new Map<string, number>();
  for (const item of companions) counts.set(item.objectType, (counts.get(item.objectType) || 0) + 1);
  // The selected resource owns its exact version. Other same-type resources
  // are alternatives in Data navigation, not part of this viewer's payload.
  // Keep cross-type context only when it has one unambiguous candidate.
  const source = [selected, ...companions.filter(item => counts.get(item.objectType) === 1)];
  return [...new Map(source.flatMap((item) => {
    const volumetric = projectVolumetricSourceArtifacts(item);
    const artifacts = volumetric ?? [sourceResourceArtifact(item)];
    return artifacts.map((artifact) => [artifactIdentity(artifact) || `${item.objectId}:${artifact.type}`, artifact] as const);
  })).values()];
}

function sourcePrimaryArtifact(resource: DatasetSourceResource, artifacts: readonly Artifact[]): Artifact {
  return artifacts.find((item) => item.metadata?.sourceObjectId === resource.objectId) ?? sourceResourceArtifact(resource);
}

function companionTypes(objectType: string): string[] {
  if (["ElectronicBand", "ElectronicDos"].includes(objectType)) return ["ElectronicBand", "ElectronicDos"];
  if (["PhononBand", "PhononDos"].includes(objectType)) return ["PhononBand", "PhononDos"];
  if (objectType === "DataFrame") return ["DataFrame", "Structure"];
  return [objectType];
}

function isCompanionResource(selected: DatasetSourceResource, candidate: DatasetSourceResource): boolean {
  if (candidate.objectId === selected.objectId || candidate.objectType === selected.objectType) return false;
  if (selected.objectType === "Structure" && candidate.objectType === "DataFrame") return experimentalXrdPlot(candidate.payload) !== null;
  if (selected.objectType === "DataFrame" && candidate.objectType === "Structure") return experimentalXrdPlot(selected.payload) !== null;
  if (companionTypes(selected.objectType).includes(candidate.objectType)) {
    return true;
  }
  return false;
}

export function projectStructureSource(payload: unknown, sourceHash?: string): unknown | null {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
  const value = payload as Record<string, unknown>;
  const lattice = value.lattice && typeof value.lattice === "object" && !Array.isArray(value.lattice)
    ? value.lattice as Record<string, unknown>
    : null;
  const matrix = Array.isArray(lattice?.matrix) ? lattice.matrix : null;
  const inputSites = Array.isArray(value.sites) ? value.sites : [];
  if (!matrix || matrix.length !== 3 || !matrix.every(finiteTriplet) || !inputSites.length) return null;
  const sites = inputSites.slice(0, 256).flatMap((item, index) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const site = item as Record<string, unknown>;
    if (!finiteTriplet(site.xyz)) return [];
    const species = Array.isArray(site.species) ? site.species : [];
    const firstSpecies = species.find((entry) => entry && typeof entry === "object" && !Array.isArray(entry)) as Record<string, unknown> | undefined;
    const element = typeof firstSpecies?.element === "string" ? firstSpecies.element : typeof site.label === "string" ? site.label.replace(/\d+$/u, "") : "X";
    return [{ index, element, label: typeof site.label === "string" ? site.label : `${element}${index + 1}`, xyz: site.xyz, ...(finiteTriplet(site.abc) ? { frac: site.abc } : {}) }];
  });
  if (!sites.length) return null;
  const species = [...new Set(sites.map((site) => site.element))].sort();
  return {
    kind: "viewer_scene",
    version: "viewer_scene.v2",
    schema_version: "phase10f18.viewer_scene.v2",
    source: { kind: "normalized_structure", hash: sourceHash || "source-hash-unavailable" },
    metadata: { formula: structureFormula(sites), species, species_count: species.length, site_count: sites.length, periodic: true },
    scene: { coordinate_basis: "cartesian_angstrom", lattice: { vectors: matrix }, sites, bonds: [], cell_expansion: [1, 1, 1] },
    validation: { status: "valid", deterministic: true },
    capabilities: { periodic_structure: true, periodic_bonds: true, cross_boundary_bonds: true, neighbor_graph: true, trajectory: false, phonon: false, volumetric: false },
    caps: { max_sites: 256, max_bonds: 2048, max_species: 32, max_scene_json_bytes: 1_000_000, max_cell_expansion: [1, 1, 1] },
    warnings: inputSites.length > 256 ? [{ code: "VIEWER_SCENE_SITES_TRUNCATED", message: `当前显示前 256 / ${inputSites.length} 个站点；完整结构仍保留在源数据中。` }] : [],
    provenance: { projection: "normalized_structure_to_viewer_scene", source_hash: sourceHash || null },
    security: { contains_javascript: false, external_urls: [], external_urls_allowed: false, artifact_supplied_js_allowed: false, renderer_required: false, remote_assets_allowed: false, html_allowed: false },
  };
}

export function projectAtomsSource(payload: unknown, sourceHash?: string): unknown | null {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
  const value = payload as Record<string, unknown>;
  const symbols = Array.isArray(value.symbols) ? value.symbols : [];
  const positions = Array.isArray(value.positions) ? value.positions : [];
  if (!symbols.length || symbols.length !== positions.length || symbols.some((item) => typeof item !== "string" || !/^[A-Z][a-z]?$/u.test(item)) || !positions.every(finiteTriplet)) return null;
  const sites = positions.slice(0, 256).map((position, index) => ({ index, element: symbols[index], label: `${symbols[index]}${index + 1}`, xyz: position }));
  const axes = [0, 1, 2].map((axis) => {
    const values = positions.map((position) => Number((position as number[])[axis]));
    const minimum = Math.min(...values); const maximum = Math.max(...values);
    return { minimum, length: Math.max(4, maximum - minimum + 4) };
  });
  const species = [...new Set(sites.map((site) => site.element))].sort();
  return {
    kind: "viewer_scene", version: "viewer_scene.v1", schema_version: "phase10f8.viewer_scene.v1",
    source: { kind: "normalized_non_periodic_atoms", hash: sourceHash || "source-hash-unavailable" },
    metadata: { formula: structureFormula(sites), species, site_count: sites.length, periodic: false },
    scene: {
      coordinate_basis: "cartesian_angstrom", sites,
      lattice: { pbc: [false, false, false], vectors: [[axes[0].length, 0, 0], [0, axes[1].length, 0], [0, 0, axes[2].length]], presentation_only: true },
      bonds: [], cell_expansion: [1, 1, 1], style: { representation: "space_filling", background: "transparent" },
    },
    validation: { status: "valid", deterministic: true, non_periodic: true },
    caps: { max_sites: 256, max_bonds: 2048, max_species: 32, max_scene_json_bytes: 1_000_000, max_cell_expansion: [1, 1, 1] },
    warnings: positions.length > 256 ? [{ code: "VIEWER_SCENE_SITES_TRUNCATED", message: `当前显示前 256 / ${positions.length} 个原子；完整坐标仍保留在源数据中。` }] : [],
    provenance: { projection: "normalized_atoms_to_non_periodic_viewer_scene", source_hash: sourceHash || null, presentation_cell_is_scientific_authority: false },
    security: { contains_javascript: false, external_urls: [], external_urls_allowed: false, artifact_supplied_js_allowed: false, renderer_required: false, remote_assets_allowed: false, html_allowed: false },
  };
}

export function projectElectronicSource(resource: DatasetSourceResource): Record<string, unknown> | null {
  if (!["ElectronicBand", "ElectronicDos"].includes(resource.objectType) || !resource.payload || typeof resource.payload !== "object" || Array.isArray(resource.payload)) return null;
  const value = resource.payload as Record<string, unknown>;
  const isBand = resource.objectType === "ElectronicBand";
  const expected = isBand ? "phase10n5.electronic_band_resource.v1" : "phase10n5.electronic_dos_resource.v1";
  if (value.schemaVersion !== expected) return null;
  const spinMode = String(value.spinMode || "non_spin_polarized");
  const common = {
    artifactType: isBand ? "electronic.band_structure" : "electronic.dos",
    schemaVersion: isBand ? "phase10n5.electronic_band_structure.v1" : "phase10n5.electronic_dos.v1",
    tool: { toolId: "source.electronic_projection", toolVersion: "1.0.0", adapterVersion: "1.0.0" },
    sourceResource: { resourceId: value.resourceId, resourceVersion: value.resourceVersion, resourceHash: value.resourceHash || resource.objectHash, resourceContract: value.schemaVersion, calculationIdentity: value.calculationIdentity, structureIdentity: value.structureIdentity ?? null, sourceMetadata: value.sourceMetadata ?? {} },
    energy: { unit: "eV", sourceUnit: value.energyUnit, reference: value.energyReference, fermiEnergyEv: value.fermiEnergyEv ?? null, frontendAlignmentAuthority: false },
    spin: { mode: spinMode, channels: spinMode === "non_spin_polarized" ? ["none"] : ["up", "down"], frontendMergeAuthority: false },
    warnings: [], limitations: ["仅展示源文件提供的电子结构数值；平台未在浏览器中执行 DFT、插值或能带计算。"],
  };
  if (isBand) {
    const kpoints = Array.isArray(value.kpoints) ? value.kpoints : [];
    const sourceBands = Array.isArray(value.bands) ? value.bands : [];
    if (!kpoints.length || !sourceBands.length) return null;
    const bands = sourceBands.flatMap((item, index) => {
      if (!item || typeof item !== "object" || Array.isArray(item)) return [];
      const band = item as Record<string, unknown>;
      if (!Array.isArray(band.energiesEv) || band.energiesEv.length !== kpoints.length) return [];
      const bandId = String(band.bandId || `band-${index + 1}`); const spinChannel = String(band.spinChannel || "none");
      return [{ bandId, bandIdentity: `source-band:${resource.objectId}:${spinChannel}:${bandId}`, energiesEv: band.energiesEv, spinChannel }];
    });
    if (!bands.length) return null;
    const states = bands.flatMap((band) => band.energiesEv.map((energy, index) => ({ stateId: `source-state:${resource.objectId}:${band.bandId}:${index}`, bandId: band.bandId, bandIdentity: band.bandIdentity, spinChannel: band.spinChannel, kpointId: String((kpoints[index] as Record<string, unknown>)?.kpointId || `kpoint-${index}`), energyEv: energy })));
    return { ...common, kpoints, pathSegments: Array.isArray(value.pathSegments) ? value.pathSegments : [], bands, states, gap: { status: "UNAVAILABLE", valueEv: null, vbm: null, cbm: null, directness: "UNAVAILABLE", classification: "CLASSIFICATION_UNAVAILABLE", algorithmId: "source_projection_no_gap_inference" }, coverage: { kpointCount: kpoints.length, bandCount: bands.length, stateCount: states.length }, algorithm: { algorithmId: "source_projection_only", interpolation: false, sourceOrderingPreserved: true } };
  }
  const energies = Array.isArray(value.energiesEv) ? value.energiesEv : [];
  const total = Array.isArray(value.totalDos) ? value.totalDos : [];
  if (!energies.length || !total.length) return null;
  const mapChannel = (item: unknown, index: number, projection = false) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return null;
    const channel = item as Record<string, unknown>;
    const channelId = String(channel.channelId || `channel-${index + 1}`); const spinChannel = String(channel.spinChannel || "none");
    return { ...channel, channelId, spinChannel, channelIdentity: `source-dos:${resource.objectId}:${projection ? "projection" : "total"}:${spinChannel}:${channelId}` };
  };
  const totalDos = total.map((item, index) => mapChannel(item, index)).filter(Boolean);
  const projections = (Array.isArray(value.projections) ? value.projections : []).map((item, index) => mapChannel(item, index, true)).filter(Boolean);
  return { ...common, energiesEv: energies, energyPointIds: energies.map((_, index) => `source-dos-point:${resource.objectId}:${index}`), totalDos, projections, projectionCompleteness: value.projectionCompleteness, dosUnitSemantic: value.dosUnitSemantic, coverage: { energyPointCount: energies.length, totalChannelCount: totalDos.length, projectionCount: projections.length }, algorithm: { algorithmId: "source_projection_only", interpolation: false, projectionSummation: false, smoothing: false } };
}

export function projectVolumetricSourceSummary(payload: unknown): { rows: Record<string, unknown>[]; source: Record<string, unknown> } | null {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
  const value = payload as Record<string, unknown>;
  const shape = Array.isArray(value.shape) ? value.shape : [];
  const channels = Array.isArray(value.channels) ? value.channels : [];
  if (shape.length !== 3 || !shape.every((item) => Number.isSafeInteger(item) && Number(item) > 0) || !channels.length) return null;
  const rows = channels.flatMap((item, index) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const channel = item as Record<string, unknown>; const values = Array.isArray(channel.values) ? channel.values : [];
    return [{ field: String(channel.name || `field-${index + 1}`), quantity: String(channel.quantity || "generic_scalar"), unit: String(channel.canonical_unit || channel.source_unit || "未声明"), samples: values.length, grid: shape.join(" × "), boundaries: Array.isArray(value.boundary_conditions) ? value.boundary_conditions.join(" / ") : "未声明" }];
  });
  return rows.length ? { rows, source: { sourceFormat: value.source_format, sourceName: value.source_name, shape, origin: value.origin_cartesian, stepMatrix: value.step_matrix, warnings: value.warnings ?? [] } } : null;
}

/**
 * Adapt the parser's bounded source payload to the existing Phase 10J viewer
 * contract. This remains a projection only: it never infers a unit, structure
 * binding, or physical normalization that the source did not provide.
 */
export function projectVolumetricSourceArtifacts(resource: DatasetSourceResource): Artifact[] | null {
  if (resource.objectType !== "VolumetricData" || !isRecord(resource.payload)) return null;
  const source = resource.payload;
  const shape = asIntTriplet(source.shape);
  const origin = asFiniteTriplet(source.origin_cartesian);
  const stepMatrix = asFiniteMatrix(source.step_matrix);
  const boundaries = Array.isArray(source.boundary_conditions) && source.boundary_conditions.length === 3 && source.boundary_conditions.every((item) => item === "periodic" || item === "non_periodic")
    ? source.boundary_conditions as ["periodic" | "non_periodic", "periodic" | "non_periodic", "periodic" | "non_periodic"]
    : null;
  const channels = Array.isArray(source.channels) ? source.channels : [];
  if (!shape || !origin || !stepMatrix || !boundaries || !channels.length || channels.length > 8) return null;
  const voxelCount = shape[0] * shape[1] * shape[2];
  if (!Number.isSafeInteger(voxelCount) || voxelCount < 1 || voxelCount > VOLUMETRIC_BROWSER_CAPS.maximumVolumeVoxelsDesktop || voxelCount * 8 > VOLUMETRIC_BROWSER_CAPS.maximumPayloadBytes) return null;
  const determinant = determinant3(stepMatrix);
  if (!Number.isFinite(determinant) || Math.abs(determinant) <= 1e-12) return null;
  const periodic = boundaries.every((item) => item === "periodic");
  if (boundaries.some((item) => item !== boundaries[0])) return null;
  const structureHash = asSha(source.structure_sha256);
  const lattice = asFiniteMatrix(source.lattice_matrix);
  if (periodic && (!structureHash || !lattice)) return null;
  const sourceSha = asSha(source.source_sha256) || hashJson(source);
  const datasetId = `volume-dataset:${hashJson({ objectId: resource.objectId, sourceSha, shape, origin, stepMatrix })}`;
  const gridCore: Record<string, unknown> = {
    schema_version: "phase10j.volumetric_grid.v1", grid_id: "grid:pending", coordinate_space: "real_cartesian", length_unit: "angstrom",
    shape, origin_cartesian: origin, origin_fractional: null, step_matrix: stepMatrix, sample_location: source.sample_location === "cell_center" ? "cell_center" : "node",
    boundary_conditions: boundaries, endpoint_policy: source.endpoint_policy === "included" ? "included" : periodic ? "excluded" : "not_applicable",
    structure_binding: periodic ? { structure_sha256: structureHash, lattice_sha256: hashJson(lattice), lattice_matrix: lattice, basis_role: "canonical_structure_cell" } : null,
    domain_extent_matrix: stepMatrix.map((row, index) => row.map((value, column) => value * shape[index] + (column === index ? 0 : 0))), voxel_volume: Math.abs(determinant),
    tolerance_policy: { schema_version: "phase10j.volumetric_tolerances.v1", determinant_relative_minimum: 1e-12, endpoint: 1e-10, matrix_absolute: 1e-9, maximum_condition_number: 100000000, relative: 1e-9 },
    security: volumetricSecurity(), content_hash: "pending",
  };
  gridCore.grid_id = `grid:${hashJson({ ...gridCore, content_hash: undefined })}`;
  gridCore.content_hash = hashJson({ ...gridCore, content_hash: undefined });
  const fields: Record<string, unknown>[] = [];
  const payloads: Record<string, unknown>[] = [];
  const binaryArtifacts: Artifact[] = [];
  const sourceFields: { fieldId: string; channelId: string }[] = [];
  for (let index = 0; index < channels.length; index += 1) {
    const channel = channels[index];
    if (!isRecord(channel) || !Array.isArray(channel.values) || channel.values.length !== voxelCount || !channel.values.every((value) => typeof value === "number" && Number.isFinite(value))) return null;
    const values = channel.values.map((value) => Object.is(value, -0) ? 0 : Number(value));
    const logicalHash = hashFloat64(values);
    const payloadId = `payload:${logicalHash}`;
    const inline = voxelCount <= 262144;
    const artifactName = `volumetric_field_${String(index + 1).padStart(2, "0")}.f64`;
    const fieldName = safeText(channel.name, `field-${index + 1}`);
    const fieldCore: Record<string, unknown> = {
      schema_version: "phase10j.volumetric_field.v1", field_id: "pending", field_name: fieldName, grid_id: gridCore.grid_id, grid_content_hash: gridCore.content_hash,
      payload_id: payloadId, payload_logical_sha256: logicalHash, quantity: safeText(channel.quantity, "unknown"), custom_quantity: null, value_kind: "real", field_rank: "scalar", logical_component_count: 1, stored_component_count: 1,
      component_labels: ["value"], component_basis: "not_applicable", unit: { canonical_unit: safeText(channel.canonical_unit, "unknown"), source_unit: safeText(channel.source_unit, safeText(channel.canonical_unit, "unknown")) },
      normalization_semantics: safeText(channel.normalization_semantics, "unknown"), integral_semantics: safeText(channel.integral_semantics, "unknown"), spin: null,
      // Match the controlled adapter's source-zero policy; this declares no
      // alignment and makes no claim about an absolute physical reference.
      potential_reference: ["local_potential", "electrostatic_potential"].includes(String(channel.quantity)) ? {
        kind: "source_defined", reference_value: 0, reference_unit: safeText(channel.canonical_unit, "unknown"),
        shift_applied: false, shift_amount: 0, source_metadata: "No alignment or mean shift was applied.",
      } : null,
      complex_semantics: null,
      statistics: sourceStatistics(values, Math.abs(determinant)), provenance: { source_sha256: sourceSha, producer: "mdi_source_viewer_projection", producer_version: "1.1.0", transformations: [{ kind: "dtype_conversion", detail: "有限源数值以确定性的 little-endian float64 内联载荷展示。" }] }, warnings: [], security: volumetricSecurity(), content_hash: "pending",
    };
    fieldCore.field_id = `field:${hashJson({ ...fieldCore, field_id: undefined, content_hash: undefined })}`;
    fieldCore.content_hash = hashJson({ ...fieldCore, field_id: undefined, content_hash: undefined });
    sourceFields.push({ fieldId: String(fieldCore.field_id), channelId: `channel:${index}` });
    fields.push(fieldCore);
    payloads.push({ schema_version: "phase10j.volumetric_payload.v1", payload_id: payloadId, encoding: inline ? "inline_json" : "raw_binary", dtype: "float64", endianness: "little", stored_component_count: 1, flatten_order: "ijkc_component_fastest", grid_shape: shape, logical_shape: [...shape, 1], value_count: voxelCount, uncompressed_bytes: voxelCount * 8, compressed_bytes: voxelCount * 8, media_type: inline ? "application/json" : "application/octet-stream", artifact_name: inline ? null : artifactName, inline_values: inline ? values : null, chunks: [], compression: null, logical_sha256: logicalHash, storage_sha256: logicalHash, storage_layout_hash: hashJson({ payloadId, shape }), security: volumetricSecurity() });
    if (!inline) binaryArtifacts.push({ id: `source:${resource.objectId}:${artifactName}`, artifactId: `source:${resource.objectId}:${artifactName}`, jobId: "source-view", type: "volumetric_binary", version: "1", name: artifactName, contentType: "application/octet-stream", sizeBytes: voxelCount * 8, sha256: logicalHash, content: float64Bytes(values), metadata: { sourceObjectType: resource.objectType, sourceDatasetId: resource.datasetId } });
  }
  fields.sort((left, right) => String(left.field_id).localeCompare(String(right.field_id)));
  payloads.sort((left, right) => String(left.payload_id).localeCompare(String(right.payload_id)));
  const datasetCore: Record<string, unknown> = { schema_version: "phase10j.volumetric_dataset.v1", dataset_id: datasetId, grid: gridCore, payloads, fields, relationships: [], provenance: { producer: "mdi_source_viewer_projection", producer_version: "1.0.0", source_format: safeText(source.source_format, "unknown"), source_kind: "normalized_source", source_sha256: sourceSha, transformations: [] }, warnings: Array.isArray(source.warnings) ? source.warnings.filter((item): item is string => typeof item === "string").slice(0, 32) : [], caps: { max_fields_per_dataset: 8, max_grid_dimension: 512, max_inline_values: 262144 }, security: volumetricSecurity(), content_hash: "pending" };
  datasetCore.content_hash = hashJson({ ...datasetCore, content_hash: undefined });
  const manifestArtifacts = [{ name: "volumetric_dataset.json", kind: "dataset", media_type: "application/json", bytes: canonicalJson(datasetCore).length, sha256: hashJson(datasetCore), schema_version: "phase10j.volumetric_dataset.v1" }, { name: "volumetric_grid.json", kind: "grid", media_type: "application/json", bytes: canonicalJson(gridCore).length, sha256: hashJson(gridCore), schema_version: "phase10j.volumetric_grid.v1" }, ...binaryArtifacts.map((artifact) => ({ name: String(artifact.name), kind: "numeric_payload", media_type: String(artifact.contentType), bytes: Number(artifact.sizeBytes), sha256: String(artifact.sha256), schema_version: "phase10j.volumetric_payload.v1" }))].sort((left, right) => String(left.name).localeCompare(String(right.name)));
  const manifestCore: Record<string, unknown> = { schema_version: "phase10j.volumetric_manifest.v1", manifest_id: "pending", dataset_id: datasetId, dataset_content_hash: datasetCore.content_hash, schema_versions: { dataset: "phase10j.volumetric_dataset.v1", field: "phase10j.volumetric_field.v1", grid: "phase10j.volumetric_grid.v1", manifest: "phase10j.volumetric_manifest.v1", payload: "phase10j.volumetric_payload.v1" }, artifacts: manifestArtifacts, capabilities: { renderer_included: false, isosurface_included: false, slice_included: false, metadata_preview: true }, external_resources: [], executable_assets: [], preview_mode: "metadata_json_only", caps: { max_fields_per_dataset: 8, max_grid_dimension: 512 }, security: volumetricSecurity(), content_hash: "pending" };
  manifestCore.manifest_id = `volume-manifest:${hashJson({ ...manifestCore, manifest_id: undefined, content_hash: undefined })}`;
  manifestCore.content_hash = hashJson({ ...manifestCore, content_hash: undefined });
  const base = { jobId: "source-view", version: "1", sha256: resource.objectHash || null, contentType: "application/json", metadata: { sourceObjectType: resource.objectType, sourceDatasetId: resource.datasetId, sourceObjectId: resource.objectId, sourceVersionId: resource.versionId || resource.objectHash, sourceFields } };
  return [
    { ...base, id: `source:${resource.objectId}:volumetric-dataset`, artifactId: `source:${resource.objectId}:volumetric-dataset`, type: "volumetric_dataset_json", name: "volumetric_dataset.json", content: datasetCore },
    { ...base, id: `source:${resource.objectId}:volumetric-manifest`, artifactId: `source:${resource.objectId}:volumetric-manifest`, type: "volumetric_manifest_json", name: "volumetric_manifest.json", content: manifestCore },
    { ...base, id: `source:${resource.objectId}:volumetric-grid`, artifactId: `source:${resource.objectId}:volumetric-grid`, type: "volumetric_grid_json", name: "volumetric_grid.json", content: gridCore },
    ...binaryArtifacts,
  ];
}

function volumetricSecurity() { return { contains_css: false, contains_executable: false, contains_html: false, contains_javascript: false, contains_shader: false, external_urls_allowed: false, renderer_included: false }; }
function isRecord(value: unknown): value is Record<string, unknown> { return Boolean(value && typeof value === "object" && !Array.isArray(value)); }
function asFiniteTriplet(value: unknown): [number, number, number] | null { return Array.isArray(value) && value.length === 3 && value.every((item) => typeof item === "number" && Number.isFinite(item)) ? value.map(Number) as [number, number, number] : null; }
function asFiniteMatrix(value: unknown): [number[], number[], number[]] | null { return Array.isArray(value) && value.length === 3 && value.every((row) => asFiniteTriplet(row)) ? value.map((row) => asFiniteTriplet(row)!) as unknown as [number[], number[], number[]] : null; }
function asIntTriplet(value: unknown): [number, number, number] | null { return Array.isArray(value) && value.length === 3 && value.every((item) => Number.isSafeInteger(item) && Number(item) > 0 && Number(item) <= 512) ? value.map(Number) as [number, number, number] : null; }
function asSha(value: unknown): string | null { return typeof value === "string" && /^[0-9a-f]{64}$/.test(value) ? value : null; }
function safeText(value: unknown, fallback: string): string { return typeof value === "string" && value.length > 0 && value.length <= 96 ? value : fallback; }
function determinant3(matrix: readonly (readonly number[])[]): number { const [a, b, c] = matrix; return a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0]); }
function float64Bytes(values: readonly number[]): ArrayBuffer { const bytes = new Uint8Array(values.length * 8); const view = new DataView(bytes.buffer); values.forEach((value, index) => view.setFloat64(index * 8, value, true)); return bytes.buffer; }
function hashFloat64(values: readonly number[]): string { return sha256HexSync(new Uint8Array(float64Bytes(values))); }
function hashJson(value: unknown): string { return sha256HexSync(new TextEncoder().encode(canonicalJson(value))); }
function canonicalJson(value: unknown): string { if (value === undefined) return "null"; if (value === null || typeof value !== "object") return JSON.stringify(value); if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`; const record = value as Record<string, unknown>; return `{${Object.keys(record).filter((key) => record[key] !== undefined).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(record[key])}`).join(",")}}`; }
function sourceStatistics(values: readonly number[], voxelVolume: number) {
  let minimum = Number.POSITIVE_INFINITY;
  let maximum = Number.NEGATIVE_INFINITY;
  let sum = 0;
  let sumSquares = 0;
  for (const value of values) {
    minimum = Math.min(minimum, value);
    maximum = Math.max(maximum, value);
    sum += value;
    sumSquares += value * value;
  }
  const mean = sum / values.length;
  let squaredDeviation = 0;
  for (const value of values) squaredDeviation += (value - mean) ** 2;
  const variance = squaredDeviation / values.length;
  return {
    accumulation_dtype: "float64",
    authority: "computed_from_source_values",
    complex_magnitude: null,
    stored_components: [{
      count: values.length,
      minimum,
      maximum,
      mean,
      standard_deviation: Math.sqrt(variance),
      rms: Math.sqrt(sumSquares / values.length),
      integral: sum * voxelVolume,
    }],
  };
}

function finiteTriplet(value: unknown): value is [number, number, number] {
  return Array.isArray(value) && value.length === 3 && value.every((item) => typeof item === "number" && Number.isFinite(item));
}

function structureFormula(sites: readonly { element: string }[]): string {
  const counts = new Map<string, number>();
  for (const site of sites) counts.set(site.element, (counts.get(site.element) || 0) + 1);
  return [...counts.entries()].sort(([left], [right]) => left.localeCompare(right)).map(([element, count]) => `${element}${count === 1 ? "" : count}`).join("");
}

function sourceResourceDisplayName(resource: DatasetSourceResource): string {
  if (experimentalXrdPlot(resource.payload)) return "实验 XRD 图谱";
  return ({
    DataFrame: "表格数据",
    Structure: "晶体结构",
    Atoms: "原子结构",
    Trajectory: "原子轨迹",
    ElectronicBand: "能带",
    ElectronicDos: "态密度",
    PhononBand: "声子能带",
    PhononDos: "声子态密度",
    PhononEigenvector: "声子振型",
    VolumetricData: "体数据",
  } as Record<string, string>)[resource.objectType] || "科学数据";
}

function sourceArtifactType(objectType: string): string {
  return ({
    DataFrame: "table_json",
    Structure: "structure_json",
    Atoms: "structure_json",
    Trajectory: "trajectory_json",
    ElectronicBand: "electronic_band_json",
    ElectronicDos: "electronic_dos_json",
    PhononBand: "phonon_band_json",
    PhononDos: "phonon_dos_json",
    PhononEigenvector: "phonon_animation_json",
    VolumetricData: "volumetric_payload_json",
  } as Record<string, string>)[objectType] || "unsupported_source_json";
}

function experimentalXrdPlot(payload: unknown): Record<string, unknown> | null {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
  const value = payload as Record<string, unknown>;
  const x = Array.isArray(value.twoTheta) ? value.twoTheta : null;
  const y = Array.isArray(value.intensity) ? value.intensity : null;
  if (!x || !y || x.length === 0 || x.length !== y.length) return null;
  if (!x.every((item) => typeof item === "number" && Number.isFinite(item))) return null;
  if (!y.every((item) => typeof item === "number" && Number.isFinite(item))) return null;
  return {
    figure: {
      data: [{ type: "scattergl", mode: "lines", name: "实验 XRD", x, y }],
      layout: {
        title: { text: "实验 XRD 图谱" },
        xaxis: { title: { text: "2θ (°)" } },
        yaxis: { title: { text: "Intensity" } },
      },
    },
  };
}

function sourceViewerContext(projectId: string, resource: DatasetSourceResource): ScientificWorkspace {
  return {
    workspaceId: `source:${resource.datasetId}`,
    projectId,
    sourceJobId: "source-view",
    datasetId: resource.datasetId,
    datasetVersion: resource.versionId || resource.objectHash || "current",
    sourceReferenceHash: resource.objectHash || `source:${resource.datasetId}`,
    revision: 0,
  } as ScientificWorkspace;
}

function resultViewerContext(projectId: string, datasetId: string | null | undefined, jobId: string, artifact: Artifact): ScientificWorkspace {
  return {
    workspaceId: `run:${jobId}`,
    projectId,
    sourceJobId: jobId,
    datasetId: datasetId || null,
    datasetVersion: "current",
    sourceReferenceHash: String(artifact.planHash || artifact.sha256 || `run:${jobId}`),
    revision: 0,
  } as ScientificWorkspace;
}

function decodeArtifactPayload(bytes: ArrayBuffer, artifact: Artifact): unknown {
  if (artifact.type === "volumetric_binary") return bytes.slice(0);
  const text = new TextDecoder("utf-8", { fatal: false }).decode(bytes);
  if (artifact.type?.endsWith("_json") || /\.json$/i.test(String(artifact.name || ""))) {
    return normalizeScientificPayload(JSON.parse(text));
  }
  return text;
}

function normalizeScientificPayload(payload: unknown): unknown {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return payload;
  const value = payload as Record<string, unknown>;
  const xrdRows = savedXrdTableRows(payload);
  if (xrdRows) return { ...value, rows: xrdRows };
  if (!["phase10n3.experimental_xrd_comparison_plot.v1", "phase10e4.static_chart.v1"].includes(String(value.schema_version)) || !Array.isArray(value.series)) return payload;
  const data = value.series.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const series = item as Record<string, unknown>;
    if (!Array.isArray(series.x) || !Array.isArray(series.y) || series.x.length !== series.y.length) return [];
    const kind = series.kind === "stick" || value.chart_type === "stem" ? "bar" : "scattergl";
    return [{
      type: kind,
      mode: kind === "bar" ? undefined : "lines",
      name: series.name === "Experimental" ? "实验 XRD" : ["Theoretical peaks", "XRD peaks"].includes(String(series.name)) ? "理论峰" : String(series.name || "数据系列"),
      x: series.x,
      y: series.y,
    }];
  });
  if (!data.length) return payload;
  return {
    ...value,
    figure: {
      data,
      layout: {
        title: { text: value.schema_version === "phase10e4.static_chart.v1" ? "理论 XRD 图谱" : "实验与理论 XRD 对比" },
        xaxis: { title: { text: "2θ (°)" } },
        yaxis: { title: { text: "归一化强度" } },
      },
    },
  };
}
