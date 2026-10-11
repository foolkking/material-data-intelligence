"use client";

import { volumetricVersionLocator } from "../volumetric-viewer/volumetric-selection";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { getProjectHistory, type DatasetSourceResource } from "../../app/lib/planner-api";
import { listResearchSessions } from "../../app/lib/product-api";
import { getScientificViewerProjection, getScientificObjectSummary, type ScientificViewerProjection } from "../../app/lib/scientific-viewer-api";
import type { WorkspaceSelectionContext } from "../../app/lib/workspace-api";
import { ScientificSourceViewer } from "../ScientificViewerAdapter";
import { phononBandPoint, phononDosPoint } from "../phonon-shared/phonon-selection";
import { trajectoryVersionLocator } from "../trajectory-viewer/trajectory-selection";
import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { pushProductQuery } from "../../shared/layout/product-query-history";
import { decodeWorkspaceSelectionUrl, encodeWorkspaceSelectionUrl, validateWorkspaceSelectionContext } from "../../shared/workspace/workspace-selection-contract";
import { scientificSelectionFromWorkspace, type ScientificSelection } from "./scientificSelection";
import { ScientificViewerShell } from "./ScientificViewerShell";
import { resolveScientificViewer } from "./scientificViewerRegistry";
import { useScientificObjectOperation, validateManagedObject, type ScientificObjectOperation } from "../../shared/workspace/scientific-object-operations";

type ViewerProps = Readonly<{
  projectId: string;
  objectId: string;
  versionId: string;
  initialSelectionToken?: string;
  canManage?: boolean;
  canResearch?: boolean;
  onSelection?: (selection: ScientificSelection) => void;
  management?: ScientificObjectOperation;
}>;

export function ScientificObjectViewer(props: ViewerProps) {
  // A different exact source must never inherit payloads, selections or retry timers.
  return <ExactScientificObjectViewer key={JSON.stringify([props.projectId, props.objectId, props.versionId])} {...props} />;
}

function ExactScientificObjectViewer({ projectId, objectId, versionId, initialSelectionToken = "", canManage = false, canResearch = false, onSelection, management }: ViewerProps) {
  const localManagement = useScientificObjectOperation(projectId);
  const operation = management || localManagement;
  const origin = `viewer:${objectId}:${versionId}`;
  const operationRef = useRef(operation); operationRef.current = operation;
  useEffect(() => () => operationRef.current.dismiss(origin), [origin]);
  const readProjection = useCallback(async (signal: AbortSignal) => {
    const value = await getScientificViewerProjection(objectId, versionId, signal);
    if (value.project_id !== projectId || value.object_id !== objectId || value.version_id !== versionId) throw new Error("VIEWER_IDENTITY_MISMATCH");
    return value;
  }, [projectId, objectId, versionId]);
  const readSummary = useCallback(async (signal: AbortSignal) => {
    const value = await getScientificObjectSummary(objectId, signal);
    return validateManagedObject(value, projectId, objectId);
  }, [projectId, objectId]);
  const sourceRead = useViewerRead(readProjection);
  const summaryRead = useViewerRead(readSummary);
  const projection = sourceRead.data;
  const objectSummary = operation.known[objectId] || summaryRead.data;
  const summaryReady = Boolean(operation.known[objectId]) || summaryRead.state === "ready";
  const [selection, setSelection] = useState<ScientificSelection | null>(null);
  const [selectionToken, setSelectionToken] = useState("");
  const [workspaceSelection, setWorkspaceSelection] = useState<WorkspaceSelectionContext | null>(null);
  const [selectionError, setSelectionError] = useState("");
  const relevantOperation = operation.targets.includes(objectId);
  const lifecycleError = relevantOperation ? operation.error : "";
  const lifecycleBusy = operation.pending || operation.reading;
  const lifecycleUncertain = operation.uncertain && relevantOperation;
  const recoveryFocus = useRef<HTMLElement | null>(null);
  useEffect(() => {
    if (recoveryFocus.current && summaryReady && !operation.reading && !lifecycleError) {
      recoveryFocus.current.querySelector<HTMLElement>(".scientific-viewer-shell-actions button")?.focus();
      recoveryFocus.current = null;
    }
  }, [summaryReady, operation.reading, lifecycleError]);
  const [retryScheduled, setRetryScheduled] = useState(false);
  const retryPending = retryScheduled || sourceRead.state === "loading";
  const retryTimerRef = useRef<number | null>(null);
  const retryAttemptRef = useRef(0);
  const deepLinkedSelection = initialSelectionToken || (typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("selection") || "" : "");
  useEffect(() => () => {
    if (retryTimerRef.current !== null) window.clearTimeout(retryTimerRef.current);
  }, []);
  const retrySource = () => {
    if (retryPending || retryTimerRef.current !== null) return;
    setRetryScheduled(true);
    const delay = Math.min(1000, 200 * (2 ** Math.min(retryAttemptRef.current, 3)));
    retryAttemptRef.current += 1;
    retryTimerRef.current = window.setTimeout(() => {
      retryTimerRef.current = null;
      setRetryScheduled(false);
      sourceRead.retry();
    }, delay);
  };
  useEffect(() => {
    if (!projection) return;
    // The Viewer is the normal handoff point into Research. Warm only the
    // bounded project/session indexes needed to render the next workbench;
    // scientific payloads and Artifacts remain lazy.
    void Promise.allSettled([
      getProjectHistory(projectId),
      listResearchSessions(projectId),
    ]);
  }, [projectId, projection]);
  const resource = useMemo(() => projection ? projectionResource(projection) : null, [projection]);
  useEffect(() => {
    setSelection(null); setSelectionToken(""); setWorkspaceSelection(null); setSelectionError("");
    if (!projection || !deepLinkedSelection) return;
    try {
      const workspace = decodeWorkspaceSelectionUrl(deepLinkedSelection);
      if (["TRAJECTORY_FRAME", "TRAJECTORY_ATOM"].includes(workspace.primary?.kind || "") && !trajectoryVersionLocator(workspace, projection)) throw new Error("TRAJECTORY_POINT_UNAVAILABLE");
      if (workspace.primary?.kind === "PHONON_Q_POINT" && (projection.object_type !== "phonon.band_structure" || !phononBandPoint(projection.payload, workspace.primary.qPointId, workspace.primary.branchId))) throw new Error("PHONON_POINT_UNAVAILABLE");
      if (workspace.primary?.kind === "VOLUMETRIC_FIELD" && !volumetricVersionLocator(workspace, projection)) throw new Error("VOLUMETRIC_FIELD_UNAVAILABLE");
      if (workspace.primary?.kind === "PHONON_DOS_POINT" && (projection.object_type !== "phonon.dos" || !phononDosPoint(projection.payload, workspace.primary.frequencyPointId, workspace.primary.dosChannelId))) throw new Error("PHONON_DOS_POINT_UNAVAILABLE");
      const descriptor = resolveScientificViewer({ objectType: projection.object_type, schemaVersion: projection.object_schema_version });
      const restored = scientificSelectionFromWorkspace(workspace, { projectId, objectId, versionId, objectType: projection.object_type, displayName: projection.display_name }, descriptor.viewerId, projection.content_hash);
      if (!restored) throw new Error("EMPTY_SELECTION");
      setSelection(restored);
      setSelectionToken(deepLinkedSelection);
      setWorkspaceSelection(workspace);
      onSelection?.(restored);
    } catch {
      setSelectionError("链接中的选择无法恢复，请在此版本中重新选择。科学内容仍可查看。");
    }
  }, [deepLinkedSelection, objectId, onSelection, projectId, projection, versionId]);
  if (sourceRead.error && !projection) return <div className="scientific-viewer-error" role="alert"><h2>无法显示此科学视图</h2><p>{sourceRead.error === "timeout" ? "此版本的科学内容读取超时，请重试。" : "暂时无法读取或确认此精确版本的科学内容，请重试。"}</p><div className="product-row-actions"><button type="button" className="product-primary-action" onClick={retrySource} disabled={retryPending}>{retryPending ? "稍后重试…" : "重新读取"}</button><Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/data`}>返回项目数据</Link></div></div>;
  if (!projection || !resource) return <div className="product-loading" role="status">正在加载科学视图…</div>;
  const descriptor = resolveScientificViewer({ objectType: projection.object_type, schemaVersion: projection.object_schema_version });
  const relevance = projection.payload_status === "SOURCE_MISSING" ? "SOURCE_MISSING" : projection.payload_status === "INVALIDATED" ? "INVALIDATED" : projection.is_current_version ? "CURRENT" : "STALE";
  const researchHref = selection && selectionToken
    ? `/projects/${encodeURIComponent(projectId)}/research?object=${encodeURIComponent(objectId)}&version=${encodeURIComponent(versionId)}&type=${encodeURIComponent(projection.object_type)}&name=${encodeURIComponent(projection.display_name)}&selection=${encodeURIComponent(selectionToken)}&selectionLabel=${encodeURIComponent(selection.displayLabel)}`
    : `/projects/${encodeURIComponent(projectId)}/research?object=${encodeURIComponent(objectId)}&version=${encodeURIComponent(versionId)}&type=${encodeURIComponent(projection.object_type)}&name=${encodeURIComponent(projection.display_name)}`;
  const persistSelection = (token: string) => {
    const url = new URL(window.location.href);
    if (url.pathname !== `/projects/${encodeURIComponent(projectId)}/data` || url.searchParams.get("object") !== objectId || url.searchParams.get("version") !== versionId) return;
    if (token) url.searchParams.set("selection", token);
    else url.searchParams.delete("selection");
    url.searchParams.delete("selectionLabel");
    pushProductQuery(`${url.pathname}${url.search}${url.hash}`);
  };
  const clearSelection = () => {
    setSelection(null); setSelectionToken(""); setWorkspaceSelection(null); setSelectionError("");
    try { persistSelection(""); } catch { setSelectionError("已清除当前选择，但链接未能更新；刷新后请再次检查选择范围。"); }
  };
  const choose = (workspace: WorkspaceSelectionContext) => {
    try {
      const context = validateWorkspaceSelectionContext(workspace);
      if (context.cleared) {
        if (context.sourceScopeHash !== projection.content_hash) throw new Error("SELECTION_SOURCE_MISMATCH");
        clearSelection(); return;
      }
      if (["TRAJECTORY_FRAME", "TRAJECTORY_ATOM"].includes(context.primary?.kind || "") && !trajectoryVersionLocator(context, projection)) throw new Error("TRAJECTORY_POINT_UNAVAILABLE");
      if (context.primary?.kind === "PHONON_Q_POINT" && (projection.object_type !== "phonon.band_structure" || !phononBandPoint(projection.payload, context.primary.qPointId, context.primary.branchId))) throw new Error("PHONON_POINT_UNAVAILABLE");
      if (context.primary?.kind === "VOLUMETRIC_FIELD" && !volumetricVersionLocator(context, projection)) throw new Error("VOLUMETRIC_FIELD_UNAVAILABLE");
      if (context.primary?.kind === "PHONON_DOS_POINT" && (projection.object_type !== "phonon.dos" || !phononDosPoint(projection.payload, context.primary.frequencyPointId, context.primary.dosChannelId))) throw new Error("PHONON_DOS_POINT_UNAVAILABLE");
      const scientific = scientificSelectionFromWorkspace(workspace, { projectId, objectId, versionId, objectType: projection.object_type, displayName: projection.display_name }, descriptor.viewerId, projection.content_hash);
      if (!scientific) throw new Error("SELECTION_SOURCE_MISMATCH");
      const token = encodeWorkspaceSelectionUrl(workspace);
      setSelection(scientific); setWorkspaceSelection(workspace); setSelectionToken(token); setSelectionError(""); onSelection?.(scientific);
      try { persistSelection(token); } catch { setSelectionError("当前选择已保留，但无法写入链接；刷新后需重新选择。"); }
    } catch {
      setSelectionError("此选择无法绑定到当前版本，请重新选择。已有有效选择仍保留。");
    }
  };
  const toggleArchive = async () => {
    if (!canManage || !objectSummary || !summaryReady || lifecycleBusy || !["ACTIVE", "ARCHIVED"].includes(objectSummary.lifecycle_status)) return;
    await operation.update([objectId], objectSummary.lifecycle_status === "ARCHIVED" ? "ACTIVE" : "ARCHIVED", origin);
  };
  const recovery = viewerPayloadRecovery(projection.payload_status, projection.limitations[0]);
  const lifecycleUnavailableReason = !summaryReady
    ? summaryRead.state === "loading" ? "正在读取对象状态，当前查看器保持只读。" : "对象状态暂时无法读取，当前查看器保持只读。"
    : objectSummary
    ? objectSummary.lifecycle_status === "INVALIDATED"
      ? "此科研对象已失效，生命周期操作已禁用；精确版本仍可只读查看。"
      : objectSummary.lifecycle_status === "TRASHED"
        ? "此科研对象已在回收站中，请从对象管理入口恢复；当前查看器保持只读。"
        : lifecycleError
          ? lifecycleError
          : undefined
    : "对象状态暂时无法读取，当前查看器保持只读。";
  const lifecycleAction = !canManage ? null : objectSummary
    ? {
        label: operation.pending && relevantOperation ? "正在更新…" : objectSummary.lifecycle_status === "ARCHIVED" ? "恢复科研对象" : "归档科研对象",
        onClick: () => void toggleArchive(),
        disabled: lifecycleBusy || !summaryReady || !["ACTIVE", "ARCHIVED"].includes(objectSummary.lifecycle_status) || operation.uncertain,
        disabledReason: lifecycleUnavailableReason,
      }
    : { label: "生命周期操作不可用", onClick: () => undefined, disabled: true, disabledReason: lifecycleUnavailableReason };
  const researchAvailable = canResearch && projection.payload_status === "READY" && summaryReady && objectSummary && ["ACTIVE", "ARCHIVED"].includes(objectSummary.lifecycle_status) && !lifecycleUncertain;
  return <ScientificViewerShell title={projection.display_name} descriptor={descriptor} versionLabel={`版本 ${projection.version_no}`} exactVersionId={projection.version_id} relevance={relevance} metadata={projection.canonical_metadata} limitations={projection.limitations} selection={selection} onClearSelection={clearSelection} primaryActionHref={researchAvailable && (!selectionError || selection) ? researchHref : null} lifecycleAction={lifecycleAction}>
    {selectionError ? <div className="scientific-viewer-feedback" role="alert"><p>{selectionError}</p><button type="button" className="product-secondary-action" onClick={clearSelection}>清除选择，查看完整版本</button></div> : null}
    {sourceRead.error ? <div className="scientific-viewer-feedback" role="alert"><p>{sourceRead.error === "timeout" ? "科学内容重新读取超时。" : "科学内容暂时无法重新读取。"}已读取的此版本信息仍保留。</p><button type="button" className="product-secondary-action" onClick={retrySource} disabled={retryPending}>{retryPending ? "稍后重试…" : "重新读取"}</button></div> : null}
    {summaryRead.state === "loading" ? <p className="scientific-viewer-feedback" role="status">正在读取对象状态…</p> : null}
    {(summaryRead.error && !operation.known[objectId]) || (lifecycleError && (!management || operation.origin === origin)) ? <div className="scientific-viewer-feedback" role="alert"><div className="scientific-viewer-feedback-copy"><p>{lifecycleError || (summaryRead.error === "timeout" ? "对象状态读取超时。" : "对象状态暂时无法读取。")}</p>{operation.readError && relevantOperation ? <p>{operation.readError}</p> : null}</div><button type="button" className="product-secondary-action" disabled={lifecycleBusy || (!lifecycleError && summaryRead.state === "loading")} onClick={(event) => {
      recoveryFocus.current = event.currentTarget.closest("article");
      if (lifecycleError) void operation.recheck(origin, [objectId]); else summaryRead.retry();
    }}>{operation.reading ? "正在核对…" : "重新读取对象状态"}</button></div> : null}
    {projection.payload_status === "READY" ? <ScientificSourceViewer projectId={projectId} resource={resource} selection={workspaceSelection} onSelection={choose} /> : (
      <div className="science-canvas science-canvas-fallback">
        <div className="science-canvas-label">
          <span>{descriptor.support === "FALLBACK" ? "安全预览" : "科学元数据"}</span>
          <strong>{recovery.title}</strong>
        </div>
        <p>{recovery.detail}</p>
        <dl data-testid="scientific-viewer-bounded-summary">
          <div><dt>精确版本</dt><dd>{projection.version_id}</dd></div>
          <div><dt>内容指纹</dt><dd>{projection.content_hash}</dd></div>
          <div><dt>来源引用</dt><dd>{projection.source_resource_refs.length} 项，保持原始身份</dd></div>
        </dl>
        <div className="product-row-actions">
          {recovery.retryable ? <button type="button" className="product-primary-action" onClick={retrySource} disabled={retryPending}>{retryPending ? "稍后重试…" : "重新读取来源"}</button> : null}
          <Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/data`}>返回项目数据</Link>
        </div>
      </div>
    )}
  </ScientificViewerShell>;
}

/** Keep a successful read while bounding and independently retrying its authority. */
function useViewerRead<T>(read: (signal: AbortSignal) => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState<"" | "timeout" | "unavailable">("");
  const [attempt, setAttempt] = useState(0);
  const pendingRef = useRef(true);
  useEffect(() => {
    const controller = new AbortController();
    pendingRef.current = true;
    setState("loading");
    const timer = window.setTimeout(() => {
      controller.abort();
      pendingRef.current = false;
      setError("timeout");
      setState("error");
    }, 10_000);
    void read(controller.signal).then((value) => {
      if (controller.signal.aborted) return;
      setData(value); setError(""); setState("ready");
    }).catch(() => {
      if (controller.signal.aborted) return;
      setError("unavailable"); setState("error");
    }).finally(() => {
      window.clearTimeout(timer);
      if (!controller.signal.aborted) pendingRef.current = false;
    });
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [read, attempt]);
  const retry = useCallback(() => {
    if (pendingRef.current) return;
    pendingRef.current = true;
    setAttempt((value) => value + 1);
  }, []);
  return { data, setData, state, error, retry };
}

export function viewerPayloadRecovery(
  status: ScientificViewerProjection["payload_status"],
  limitation?: string,
) {
  if (status === "METADATA_ONLY") {
    return {
      title: "交互式预览已受限",
      detail: limitation || "此科学数据超过交互式预览上限；精确版本与来源元数据仍可查看。",
      retryable: false,
    };
  }
  if (status === "INVALIDATED") {
    return {
      title: "此历史版本已失效",
      detail: limitation || "该版本仅保留用于审计，不应作为当前有效科研证据。",
      retryable: false,
    };
  }
  return {
    title: "精确来源的原始科学数据当前不可用",
    detail: limitation || "科学元数据与精确版本身份仍可查看；系统没有选择替代版本。",
    retryable: status === "SOURCE_MISSING",
  };
}

function projectionResource(projection: ScientificViewerProjection): DatasetSourceResource {
  return {
    objectId: projection.object_id,
    objectType: legacyObjectType(projection.object_type),
    objectHash: projection.content_hash,
    datasetId: String(projection.source_resource_refs.find(ref => ref.dataset_id)?.dataset_id || projection.object_id),
    versionId: projection.version_id,
    displayName: projection.display_name,
    payload: projection.payload,
    viewerScene: projection.viewer_scene,
    viewerSceneIssue: projection.viewer_scene_issue,
  };
}

function legacyObjectType(objectType: string) {
  return ({ "materials.dataset": "DataFrame", "materials.table": "DataFrame", "structure.crystal": "Structure", "structure.atomic": "Atoms", "trajectory.atomic": "Trajectory", "diffraction.xrd.experimental": "DataFrame", "diffraction.xrd.theoretical": "DataFrame", "electronic.band_structure": "ElectronicBand", "electronic.dos": "ElectronicDos", "phonon.band_structure": "PhononBand", "phonon.dos": "PhononDos", "volumetric.field": "VolumetricData", "volumetric.charge_density": "VolumetricData" } as Record<string, string>)[objectType] || objectType;
}
