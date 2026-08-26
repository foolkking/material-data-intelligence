"use client";

import { useEffect, useMemo, useState } from "react";

import type { DatasetSourceResource } from "../../lib/planner-api";
import { getScientificViewerProjection, listScientificObjects, updateScientificObject, type ScientificObjectSummary, type ScientificViewerProjection } from "../../lib/scientific-viewer-api";
import type { WorkspaceSelectionContext } from "../../lib/workspace-api";
import { ScientificSourceViewer } from "../ScientificViewerAdapter";
import { decodeWorkspaceSelectionUrl, encodeWorkspaceSelectionUrl } from "../workspace/workspace-selection-contract";
import { scientificSelectionFromWorkspace, type ScientificSelection } from "./scientificSelection";
import { ScientificViewerShell } from "./ScientificViewerShell";
import { resolveScientificViewer } from "./scientificViewerRegistry";

export function ScientificObjectViewer({ projectId, objectId, versionId, initialSelectionToken = "", onSelection }: Readonly<{ projectId: string; objectId: string; versionId: string; initialSelectionToken?: string; onSelection?: (selection: ScientificSelection) => void }>) {
  const [projection, setProjection] = useState<ScientificViewerProjection | null>(null);
  const [selection, setSelection] = useState<ScientificSelection | null>(null);
  const [selectionToken, setSelectionToken] = useState("");
  const [error, setError] = useState("");
  const [objectSummary, setObjectSummary] = useState<ScientificObjectSummary | null>(null);
  const [lifecycleBusy, setLifecycleBusy] = useState(false);
  const deepLinkedSelection = initialSelectionToken || (typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("selection") || "" : "");
  useEffect(() => {
    const controller = new AbortController();
    setProjection(null); setSelection(null); setSelectionToken(""); setError("");
    void getScientificViewerProjection(objectId, versionId, controller.signal).then(setProjection).catch((reason) => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "VIEWER_LOAD_FAILED"); });
    void listScientificObjects(projectId, controller.signal).then((response) => {
      if (!controller.signal.aborted) setObjectSummary(response.items.find((item) => item.id === objectId) || null);
    }).catch(() => { if (!controller.signal.aborted) setObjectSummary(null); });
    return () => controller.abort();
  }, [objectId, projectId, versionId]);
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
  if (error) return <div className="scientific-viewer-error" role="alert"><h2>无法显示此科学视图</h2><p>原始数据仍然保留；请稍后重试或查看技术详情。</p><details><summary>技术详情</summary><p>{error}</p></details></div>;
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
    try {
      const updated = await updateScientificObject(objectSummary.id, { archived: objectSummary.lifecycle_status !== "ARCHIVED" });
      setObjectSummary(updated);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "SCIENTIFIC_OBJECT_UPDATE_FAILED");
    } finally {
      setLifecycleBusy(false);
    }
  };
  return <ScientificViewerShell title={projection.display_name} descriptor={descriptor} versionLabel={`版本 ${projection.version_no}`} relevance={relevance} metadata={projection.canonical_metadata} limitations={projection.limitations} selection={selection} primaryActionHref={researchHref} lifecycleAction={objectSummary ? { label: objectSummary.lifecycle_status === "ARCHIVED" ? "恢复科研对象" : "归档科研对象", onClick: () => void toggleArchive(), disabled: lifecycleBusy } : null}>
    {projection.payload_status === "READY" ? <ScientificSourceViewer projectId={projectId} resource={resource} onSelection={choose} /> : <div className="science-canvas science-canvas-fallback"><div className="science-canvas-label"><span>{descriptor.support === "FALLBACK" ? "安全预览" : "科学元数据"}</span><strong>当前没有可交互的 payload</strong></div><p>{projection.limitations[0] || "可查看元数据与版本信息。"}</p></div>}
  </ScientificViewerShell>;
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
