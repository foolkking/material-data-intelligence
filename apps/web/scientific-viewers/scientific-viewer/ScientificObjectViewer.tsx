"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { getProjectHistory, type DatasetSourceResource } from "../../app/lib/planner-api";
import { listResearchSessions } from "../../app/lib/product-api";
import { getScientificViewerProjection, listScientificObjects, updateScientificObject, type ScientificObjectSummary, type ScientificViewerProjection } from "../../app/lib/scientific-viewer-api";
import type { WorkspaceSelectionContext } from "../../app/lib/workspace-api";
import { ScientificSourceViewer } from "../ScientificViewerAdapter";
import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { decodeWorkspaceSelectionUrl, encodeWorkspaceSelectionUrl } from "../../shared/workspace/workspace-selection-contract";
import { scientificSelectionFromWorkspace, type ScientificSelection } from "./scientificSelection";
import { ScientificViewerShell } from "./ScientificViewerShell";
import { resolveScientificViewer } from "./scientificViewerRegistry";

export function ScientificObjectViewer({ projectId, objectId, versionId, initialSelectionToken = "", onSelection }: Readonly<{ projectId: string; objectId: string; versionId: string; initialSelectionToken?: string; onSelection?: (selection: ScientificSelection) => void }>) {
  const [projection, setProjection] = useState<ScientificViewerProjection | null>(null);
  const [selection, setSelection] = useState<ScientificSelection | null>(null);
  const [selectionToken, setSelectionToken] = useState("");
  const [error, setError] = useState("");
  const [objectSummary, setObjectSummary] = useState<ScientificObjectSummary | null>(null);
  const [objectSummaryLoadState, setObjectSummaryLoadState] = useState<"loading" | "ready" | "error">("loading");
  const [lifecycleError, setLifecycleError] = useState("");
  const [lifecycleBusy, setLifecycleBusy] = useState(false);
  const [retryAttempt, setRetryAttempt] = useState(0);
  const [retryPending, setRetryPending] = useState(false);
  const retryTimerRef = useRef<number | null>(null);
  const retryAttemptRef = useRef(0);
  const deepLinkedSelection = initialSelectionToken || (typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("selection") || "" : "");
  useEffect(() => {
    const controller = new AbortController();
    setProjection(null); setSelection(null); setSelectionToken(""); setError("");
    setObjectSummary(null); setObjectSummaryLoadState("loading"); setLifecycleError("");
    void getScientificViewerProjection(objectId, versionId, controller.signal).then(setProjection).catch((reason) => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "VIEWER_LOAD_FAILED"); }).finally(() => {
      if (!controller.signal.aborted) setRetryPending(false);
    });
    void listScientificObjects(projectId, controller.signal).then((response) => {
      if (!controller.signal.aborted) {
        setObjectSummary(response.items.find((item) => item.id === objectId) || null);
        setObjectSummaryLoadState("ready");
      }
    }).catch(() => { if (!controller.signal.aborted) { setObjectSummary(null); setObjectSummaryLoadState("error"); } });
    return () => controller.abort();
  }, [objectId, projectId, retryAttempt, versionId]);
  useEffect(() => () => {
    if (retryTimerRef.current !== null) window.clearTimeout(retryTimerRef.current);
  }, []);
  const retrySource = () => {
    if (retryPending) return;
    setRetryPending(true);
    const delay = Math.min(1000, 200 * (2 ** Math.min(retryAttemptRef.current, 3)));
    retryAttemptRef.current += 1;
    retryTimerRef.current = window.setTimeout(() => {
      retryTimerRef.current = null;
      setRetryAttempt((value) => value + 1);
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
    if (!projection || !deepLinkedSelection) return;
    try {
      const workspace = decodeWorkspaceSelectionUrl(deepLinkedSelection);
      const descriptor = resolveScientificViewer({ objectType: projection.object_type, schemaVersion: projection.object_schema_version });
      const restored = scientificSelectionFromWorkspace(workspace, { projectId, objectId, versionId, objectType: projection.object_type, displayName: projection.display_name }, descriptor.viewerId);
      if (!restored) return;
      setSelection(restored);
      setSelectionToken(deepLinkedSelection);
      onSelection?.(restored);
    } catch {
      setError("SELECTION_DEEP_LINK_INVALID");
    }
  }, [deepLinkedSelection, objectId, onSelection, projectId, projection, versionId]);
  if (error) return <div className="scientific-viewer-error" role="alert"><h2>无法显示此科学视图</h2><p>原始数据仍然保留；请稍后重试或查看技术详情。</p><div className="product-row-actions"><button type="button" className="product-primary-action" onClick={() => { setError(""); retrySource(); }} disabled={retryPending}>{retryPending ? "稍后重试…" : "重新读取"}</button><Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/data?object=${encodeURIComponent(objectId)}&version=${encodeURIComponent(versionId)}`}>查看来源与属性</Link></div><details><summary>技术详情</summary><p>{error}</p></details></div>;
  if (!projection || !resource) return <div className="product-loading" role="status">正在加载科学视图…</div>;
  const descriptor = resolveScientificViewer({ objectType: projection.object_type, schemaVersion: projection.object_schema_version });
  const relevance = projection.payload_status === "SOURCE_MISSING" ? "SOURCE_MISSING" : projection.payload_status === "INVALIDATED" ? "INVALIDATED" : projection.is_current_version ? "CURRENT" : "STALE";
  const researchHref = selection && selectionToken
    ? `/projects/${encodeURIComponent(projectId)}/research?object=${encodeURIComponent(objectId)}&version=${encodeURIComponent(versionId)}&type=${encodeURIComponent(projection.object_type)}&name=${encodeURIComponent(projection.display_name)}&selection=${encodeURIComponent(selectionToken)}&selectionLabel=${encodeURIComponent(selection.displayLabel)}`
    : `/projects/${encodeURIComponent(projectId)}/research?object=${encodeURIComponent(objectId)}&version=${encodeURIComponent(versionId)}&type=${encodeURIComponent(projection.object_type)}&name=${encodeURIComponent(projection.display_name)}`;
  const choose = (workspace: WorkspaceSelectionContext) => {
    const scientific = scientificSelectionFromWorkspace(workspace, { projectId, objectId, versionId, objectType: projection.object_type, displayName: projection.display_name }, descriptor.viewerId);
    if (!scientific) return;
    setSelection(scientific); setSelectionToken(encodeWorkspaceSelectionUrl(workspace)); onSelection?.(scientific);
  };
  const toggleArchive = async () => {
    if (!objectSummary || lifecycleBusy) return;
    setLifecycleBusy(true);
    setLifecycleError("");
    try {
      const updated = await updateScientificObject(objectSummary.id, { archived: objectSummary.lifecycle_status !== "ARCHIVED" });
      setObjectSummary(updated);
    } catch (reason) {
      setLifecycleError(reason instanceof Error ? reason.message : "科研对象管理服务暂时不可用。");
    } finally {
      setLifecycleBusy(false);
    }
  };
  const recovery = viewerPayloadRecovery(projection.payload_status, projection.limitations[0]);
  const lifecycleUnavailableReason = objectSummary
    ? objectSummary.lifecycle_status === "INVALIDATED"
      ? "此科研对象已失效，生命周期操作已禁用；精确版本仍可只读查看。"
      : objectSummary.lifecycle_status === "TRASHED"
        ? "此科研对象已在回收站中，请从对象管理入口恢复；当前查看器保持只读。"
        : lifecycleError
          ? `对象管理服务暂时不可用，操作已禁用。${lifecycleError}`
          : undefined
    : objectSummaryLoadState === "loading"
      ? "正在读取对象权限与生命周期状态。"
      : "对象管理权限或状态暂时无法读取，当前查看器保持只读。";
  const lifecycleAction = objectSummary
    ? {
        label: objectSummary.lifecycle_status === "ARCHIVED" ? "恢复科研对象" : "归档科研对象",
        onClick: () => void toggleArchive(),
        disabled: lifecycleBusy || objectSummary.lifecycle_status === "INVALIDATED" || objectSummary.lifecycle_status === "TRASHED" || Boolean(lifecycleError),
        disabledReason: lifecycleUnavailableReason,
      }
    : { label: "生命周期操作不可用", onClick: () => undefined, disabled: true, disabledReason: lifecycleUnavailableReason };
  return <ScientificViewerShell title={projection.display_name} descriptor={descriptor} versionLabel={`版本 ${projection.version_no}`} exactVersionId={projection.version_id} relevance={relevance} metadata={projection.canonical_metadata} limitations={projection.limitations} selection={selection} primaryActionHref={projection.payload_status === "READY" ? researchHref : null} lifecycleAction={lifecycleAction}>
    {projection.payload_status === "READY" ? <ScientificSourceViewer projectId={projectId} resource={resource} onSelection={choose} /> : <div className="science-canvas science-canvas-fallback"><div className="science-canvas-label"><span>{descriptor.support === "FALLBACK" ? "安全预览" : "科学元数据"}</span><strong>{recovery.title}</strong></div><p>{recovery.detail}</p><dl data-testid="scientific-viewer-bounded-summary"><div><dt>精确版本</dt><dd>{projection.version_id}</dd></div><div><dt>内容指纹</dt><dd>{projection.content_hash}</dd></div><div><dt>来源引用</dt><dd>{projection.source_resource_refs.length} 项，保持原始身份</dd></div></dl><div className="product-row-actions"><Link className="product-primary-action" href={`/projects/${encodeURIComponent(projectId)}/data?object=${encodeURIComponent(objectId)}&version=${encodeURIComponent(versionId)}`}>查看来源与属性</Link>{recovery.retryable ? <button type="button" className="product-secondary-action" onClick={retrySource} disabled={retryPending}>{retryPending ? "稍后重试…" : "重新读取来源"}</button> : null}</div></div>}
  </ScientificViewerShell>;
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
    datasetId: String(projection.source_resource_refs[0]?.dataset_id || projection.object_id),
    versionId: projection.version_id,
    displayName: projection.display_name,
    payload: projection.payload,
  };
}

function legacyObjectType(objectType: string) {
  return ({ "materials.dataset": "DataFrame", "materials.table": "DataFrame", "structure.crystal": "Structure", "trajectory.atomic": "Trajectory", "diffraction.xrd.experimental": "DataFrame", "diffraction.xrd.theoretical": "DataFrame", "electronic.band_structure": "ElectronicBand", "electronic.dos": "ElectronicDos", "phonon.band_structure": "PhononBand", "phonon.dos": "PhononDos", "volumetric.charge_density": "VolumetricData" } as Record<string, string>)[objectType] || objectType;
}
