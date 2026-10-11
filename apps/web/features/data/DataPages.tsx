"use client";

import {
  ProductLink as Link,
} from "../../shared/layout/ProductNavigation";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import {
  bulkProjectAction,
  createProject,
  deleteEmptyDataset,
  deleteEmptyProject,
  getDatasetDependencyImpact,
  getDatasetSourceResources,
  getCachedProjectHistory,
  getProjectDependencyImpact,
  getProjectExportManifest,
  getProjectHistory,
  listProjects,
  updateDataset,
  updateProject,
  uploadDatasetFiles,
  type DatasetSourceResource,
  type DependencyImpact,
  type ProjectHistory,
  type ProjectSummary,
  type UploadDatasetFile,
} from "../../app/lib/planner-api";
import {
  PHONON_BAND_SCHEMA_VERSION,
  PHONON_DOS_SCHEMA_VERSION,
} from "../../app/lib/phononContract";
import { ProductShell, RequireProductAuth } from "../../shared/layout/ProductShell";
import {
  LazyScientificObjectViewer,
  LazyScientificSourceViewer,
} from "../../scientific-viewers/LazyScientificViewers";
import {
  ManagedObjectRow,
  ProductModal,
  type ObjectAction,
} from "../../shared/ui/ObjectManagement";
import type { WorkspaceSelectionContext } from "../../app/lib/workspace-api";
import {
  decodeWorkspaceSelectionUrl,
  encodeWorkspaceSelectionUrl,
} from "../../shared/workspace/workspace-selection-contract";
import {
  researchRunStatusLabel,
  researchRunTitle,
} from "../../app/lib/research-display";
import {
  getScientificObjectDependencyImpact,
  type ScientificObjectDependencyImpact,
  type ScientificObjectSummary,
} from "../../app/lib/scientific-viewer-api";
import { RouteLoading } from "../../shared/ui/RouteLoading";
import { projectRoleAllows } from "../../app/lib/project-permissions";
import { DependencyImpactEntry, dependencyDisplayLabel, EmptyOrError, productProjectName, sourceTypeLabel, useProject } from "../projects/ProductPages";
import type { LoadState } from "../projects/ProductPages";
import { DependencyPreviewFeedback, useDependencyPreview, type DependencyPreviewState } from "../../shared/ui/DependencyPreview";
import { useScientificObjectDirectory } from "./use-scientific-object-directory";
import { pushProductQuery, replaceProductQuery } from "../../shared/layout/product-query-history";
import { useDataNavigator } from "./use-data-navigator";
import { useClampedTitle } from "../../shared/ui/use-clamped-title";
import { useDatasetOperation, validateDataset, readDatasetDirectory, updateDatasetBatches, type DatasetOperation } from "./dataset-operations";
import { useScientificObjectOperation } from "../../shared/workspace/scientific-object-operations";
import { DatasetSourceDetails } from "./DatasetSourceDetails";
import sourceDetailsStyles from "./DatasetSourceDetails.module.css";

type ProjectDataset = ProjectHistory["datasets"][number];

function UnavailableDataEntry({ title }: { title: string }) {
  const name = useClampedTitle(title, true);
  return <div className="data-unavailable-entry" tabIndex={0} {...name.events}><strong ref={name.titleRef} className="managed-object-name-clamped">{title}</strong><span>暂无可查看的版本</span>{name.tooltip}</div>;
}

function ScientificObjectTrashDialog({
  item,
  preview,
  busy,
  error,
  onClose,
  onConfirm,
  recovery,
  locked = false,
}: {
  recovery?: ReactNode;
  locked?: boolean;
  item: ScientificObjectSummary;
  preview: DependencyPreviewState<ScientificObjectDependencyImpact>;
  busy: boolean;
  error: string;
  onClose: () => void;
  onConfirm: () => void;
}) {
  const impact = preview.items[0];
  return (
    <ProductModal
      eyebrow="科研对象管理"
      title="将科研对象移入回收站"
      description="对象会从新的研究选择中移除，但科学版本、历史结果、查看器与报告仍保留。"
      onClose={onClose}
      footer={
        <>
          <button type="button" className="product-secondary-action" onClick={onClose}>
            取消
          </button>
          <button
            type="button"
            className="product-danger-action"
            disabled={busy || locked || !preview.complete}
            onClick={onConfirm}
          >
            {busy ? "正在移动…" : "移入回收站"}
          </button>
        </>
      }
    >
      <div className="product-form-grid danger-zone scientific-object-management-form">
        <p>
          <strong>{item.display_name}</strong> 的历史科学记录不会被删除。
        </p>
        {impact ? (
          <div role="status">
            <strong>依赖影响</strong>
            {impact.dependencies.length ? (
              <ul>
                {impact.dependencies.map((dependency) => (
                  <li key={dependency.kind}>
                    <DependencyImpactEntry item={dependency} />
                  </li>
                ))}
              </ul>
            ) : (
              <p>未发现已持久化的结果依赖。</p>
            )}
            <p>受保护的科学来源、版本和历史研究仍可访问。</p>
          </div>
        ) : null}
        <DependencyPreviewFeedback preview={preview} />
        {recovery}
        {error ? (
          <p className="product-form-error" role="alert">
            {error}
          </p>
        ) : null}
      </div>
    </ProductModal>
  );
}

function ScientificObjectBulkTrashDialog({
  items,
  preview,
  busy,
  error,
  onClose,
  onConfirm,
  recovery,
  locked = false,
}: {
  recovery?: ReactNode;
  locked?: boolean;
  items: ScientificObjectSummary[];
  preview: DependencyPreviewState<ScientificObjectDependencyImpact>;
  busy: boolean;
  error: string;
  onClose: () => void;
  onConfirm: () => void;
}) {
  const impacts = preview.items;
  const dependencyTotals = new Map<string, { label: string; count: number }>();
  for (const impact of impacts || []) {
    for (const dependency of impact.dependencies) {
      const current = dependencyTotals.get(dependency.kind);
      dependencyTotals.set(dependency.kind, {
        label: dependencyDisplayLabel(dependency.kind, dependency.label),
        count: (current?.count || 0) + dependency.count,
      });
    }
  }
  const totalDependencies = (impacts || []).reduce(
    (total, impact) => total + impact.dependencyCount,
    0,
  );
  return (
    <ProductModal
      eyebrow="科研对象管理"
      title={`将 ${items.length} 个科研对象移入回收站`}
      description="批量操作会先检查每个对象的服务器依赖；科学版本、历史结果、查看器与报告不会被删除。"
      onClose={onClose}
      footer={
        <>
          <button type="button" className="product-secondary-action" onClick={onClose}>
            取消
          </button>
          <button
            type="button"
            className="product-danger-action"
            disabled={busy || locked || !preview.complete}
            onClick={onConfirm}
          >
            {busy ? "正在移动…" : "确认移入回收站"}
          </button>
        </>
      }
    >
      <div className="product-form-grid danger-zone scientific-object-management-form">
        <p>
          已选择 <strong>{items.length}</strong> 个对象。
          {impacts.length > 0 ? <>已读取 {impacts.length} 项检查，共 <strong>{totalDependencies}</strong> 项受保护依赖。</> : null}
        </p>
        <ul className="bulk-lifecycle-targets">
          {items.slice(0, 8).map((item) => (
            <li key={item.id}>
              <strong>{item.display_name}</strong>
              <span>{scientificObjectTypeLabel(item.object_type)}</span>
            </li>
          ))}
          {items.length > 8 ? <li>另有 {items.length - 8} 个对象…</li> : null}
        </ul>
        {impacts.length > 0 ? (
          <div role="status">
            <strong>依赖影响汇总</strong>
            {dependencyTotals.size ? (
              <ul>
                {Array.from(dependencyTotals.entries()).map(([kind, value]) => (
                  <li key={kind}>
                    {value.label}：{value.count}
                  </li>
                ))}
              </ul>
            ) : (
              <p>已读取的检查中未发现已持久化的结果依赖。</p>
            )}
            <p>对象会从新的研究选择中移除；历史研究和精确来源记录仍可访问。</p>
          </div>
        ) : null}
        <DependencyPreviewFeedback preview={preview} />
        {recovery}
        {error ? <p className="product-form-error" role="alert">{error}</p> : null}
      </div>
    </ProductModal>
  );
}

function DatasetBulkTrashDialog({
  items,
  preview,
  busy,
  error,
  onClose,
  onConfirm,
  recovery,
  locked = false,
}: {
  recovery?: ReactNode;
  locked?: boolean;
  items: ProjectDataset[];
  preview: DependencyPreviewState<DependencyImpact>;
  busy: boolean;
  error: string;
  onClose: () => void;
  onConfirm: () => void;
}) {
  const impacts = preview.items;
  const dependencyTotals = new Map<string, { label: string; count: number }>();
  for (const impact of impacts || []) {
    for (const dependency of impact.dependencies) {
      const current = dependencyTotals.get(dependency.kind);
      dependencyTotals.set(dependency.kind, {
        label: dependencyDisplayLabel(dependency.kind, dependency.label),
        count: (current?.count || 0) + dependency.count,
      });
    }
  }
  const totalDependencies = (impacts || []).reduce(
    (total, impact) => total + impact.dependencyCount,
    0,
  );
  return (
    <ProductModal
      eyebrow="数据集管理"
      title={`将 ${items.length} 个数据集移入回收站`}
      description="批量操作会先检查每个数据集的服务器依赖；源文件、科学版本、历史结果与报告不会被删除。"
      onClose={onClose}
      footer={
        <>
          <button type="button" className="product-secondary-action" onClick={onClose}>
            取消
          </button>
          <button
            type="button"
            className="product-danger-action"
            disabled={busy || locked || !preview.complete || !items.length}
            onClick={onConfirm}
          >
            {busy ? "正在移动…" : "确认移入回收站"}
          </button>
        </>
      }
    >
      <div className="product-form-grid danger-zone dataset-management-form">
        <p>
          已选择 <strong>{items.length}</strong> 个数据集。
          {impacts.length > 0 ? <>已读取 {impacts.length} 项检查，共 <strong>{totalDependencies}</strong> 项受保护依赖。</> : null}
        </p>
        <ul className="bulk-lifecycle-targets">
          {items.slice(0, 8).map((item) => (
            <li key={item.datasetId}>
              <strong>{productProjectName(item.name)}</strong>
              <span>{dataKindLabel(inferDataKind(item))}</span>
            </li>
          ))}
          {items.length > 8 ? <li>另有 {items.length - 8} 个数据集…</li> : null}
        </ul>
        {impacts.length > 0 ? (
          <div role="status">
            <strong>依赖影响汇总</strong>
            {dependencyTotals.size ? (
              <ul>
                {Array.from(dependencyTotals.entries()).map(([kind, value]) => (
                  <li key={kind}>
                    {value.label}：{value.count}
                  </li>
                ))}
              </ul>
            ) : (
              <p>已读取的检查中未发现已持久化的结果依赖。</p>
            )}
            <p>数据集会从新的研究选择中移除；历史研究和精确来源记录仍可访问。</p>
          </div>
        ) : null}
        <DependencyPreviewFeedback preview={preview} />
        {recovery}
        {error ? <p className="product-form-error" role="alert">{error}</p> : null}
      </div>
    </ProductModal>
  );
}

function DatasetEditDialog({
  dataset,
  mode,
  onClose,
  onUpdated,
  onDeleted,
  projectId, operation, onReload, available, canManage,
}: {
  projectId: string;
  operation: DatasetOperation;
  onReload: () => void;
  available: boolean;
  canManage: boolean;
  dataset: ProjectDataset;
  mode: "edit" | "trash" | "delete";
  onClose: () => void;
  onUpdated: (changes: { name: string; status: string }) => void;
  onDeleted: (datasetId: string) => void;
}) {
  const [name, setName] = useState(dataset.name);
  const [confirmation, setConfirmation] = useState("");
  const busy = operation.pending || operation.reading;
  const locked = busy || operation.uncertain || !available || !canManage;
  const error = operation.error;
  const recovery = <>
    {error ? <p className="product-form-error" role="alert">{error}</p> : null}
    {operation.uncertain ? <div className="dataset-operation-recovery"><button type="button" className="product-secondary-action" disabled={busy} onClick={onReload}>{operation.reading ? "正在读取…" : "重新读取数据列表"}</button>{operation.readError ? <p role="status">{operation.readError}</p> : null}</div> : null}
    {!available ? <p role="status">此数据已不在当前项目列表中，编辑内容仍保留。</p> : null}
    {available && !canManage ? <p role="status">当前没有修改此数据的权限，编辑内容仍保留。</p> : null}
  </>;
  const preview = useDependencyPreview(
    mode === "edit" ? [] : [{ id: dataset.datasetId, label: dataset.name }],
    getDatasetDependencyImpact,
  );
  const impact = preview.items[0];
  async function save() {
    if (!name.trim() || locked) return;
    await operation.run("重命名数据集", async (signal) => validateDataset(await updateDataset(dataset.datasetId, { name: name.trim() }, signal), projectId, dataset.datasetId, { name: name.trim() }), (changes) => { onUpdated(changes); onClose(); });
  }
  async function remove() {
    if (confirmation !== dataset.name || locked || !preview.complete || !impact?.canDelete) return;
    await operation.run("删除空数据集", async (signal) => {
      const result = await deleteEmptyDataset(dataset.datasetId, signal);
      if (result?.datasetId !== dataset.datasetId || result.deleted !== true) throw new Error("Dataset deletion identity mismatch");
      return result;
    }, () => { onDeleted(dataset.datasetId); onClose(); });
  }
  async function trash() {
    if (locked || !preview.complete) return;
    await operation.run("移入回收站", async (signal) => validateDataset(await updateDataset(dataset.datasetId, { lifecycle: "TRASHED" }, signal), projectId, dataset.datasetId, { lifecycle: "TRASHED" }), (changes) => { onUpdated(changes); onClose(); });
  }
  if (mode === "trash")
    return (
      <ProductModal
        eyebrow="数据管理"
        title="将数据集移入回收站"
        description="数据集会从当前研究选择中移除，但源数据、科学版本、历史结果与报告仍保留。"
        onClose={onClose}
        footer={
          <>
            <button
              type="button"
              className="product-secondary-action"
              onClick={onClose}
            >
              取消
            </button>
            <button
              type="button"
              className="product-danger-action"
              disabled={locked || !preview.complete}
              onClick={() => void trash()}
            >
              {busy ? "正在移动…" : "移入回收站"}
            </button>
          </>
        }
      >
        <div className="product-form-grid danger-zone dataset-management-form">
          <p>
            <strong>{dataset.name}</strong> 将不再出现在当前数据列表中。
          </p>
          {impact ? (
            <div role="status">
              <strong>依赖影响</strong>
              {impact.dependencies.length ? (
                <ul>
                  {impact.dependencies.map((item) => (
                    <li key={item.kind}>
                      <DependencyImpactEntry item={item} />
                    </li>
                  ))}
                </ul>
              ) : (
                <p>未发现依赖记录。</p>
              )}
              <p>受保护的科学来源记录不会被删除。</p>
            </div>
          ) : null}
          <DependencyPreviewFeedback preview={preview} />
          {recovery}

        </div>
      </ProductModal>
    );
  if (mode === "delete")
    return (
      <ProductModal
        eyebrow="数据管理"
        title="删除空数据集"
        description="只有尚未包含源文件、语义档案和研究记录的数据集可以永久删除。"
        onClose={onClose}
        footer={
          <>
            <button
              type="button"
              className="product-secondary-action"
              onClick={onClose}
            >
              取消
            </button>
            <button
              type="button"
              className="product-danger-action"
              disabled={locked || confirmation !== dataset.name || !preview.complete || !impact?.canDelete}
              onClick={() => void remove()}
            >
              {busy ? "正在删除…" : "永久删除"}
            </button>
          </>
        }
      >
        <div className="product-form-grid danger-zone dataset-management-form">
          <p>
            输入数据集名称 <strong>{dataset.name}</strong> 以确认。
          </p>
          <DependencyPreviewFeedback preview={preview} />
          {impact && !impact.canDelete ? (
            <div role="status">
              <strong>依赖影响</strong>
              <ul>
                {impact.dependencies.map((item) => (
                  <li key={item.kind}>
                    <DependencyImpactEntry item={item} />
                  </li>
                ))}
              </ul>
              <p>已有依赖时系统会拒绝物理删除；请改为归档。</p>
            </div>
          ) : null}
          <label htmlFor="delete-dataset-confirmation">数据集名称</label>
          <input
            id="delete-dataset-confirmation"
            value={confirmation}
            onChange={(event) => setConfirmation(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void remove();
              }
            }}
            autoComplete="off"
          />
          {recovery}

        </div>
      </ProductModal>
    );
  return (
    <ProductModal
      eyebrow="数据管理"
      title="重命名数据集"
      description="修改后可在数据目录和研究中看到新名称。"
      onClose={onClose}
      footer={
        <>
          <button
            type="button"
            className="product-secondary-action"
            onClick={onClose}
          >
            取消
          </button>
          <button
            type="button"
            className="product-primary-action"
            disabled={locked || !name.trim()}
            onClick={() => void save()}
          >
            {busy ? "正在保存…" : "保存更改"}
          </button>
        </>
      }
    >
      <div className="product-form-grid dataset-management-form">
        <label htmlFor="edit-dataset-name">数据集名称</label>
        <input
          id="edit-dataset-name"
          maxLength={160}
          disabled={busy}
          value={name}
          onChange={(event) => setName(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              void save();
            }
          }}
        />
        {recovery}

      </div>
    </ProductModal>
  );
}

type DataKind =
  | "table"
  | "structure"
  | "trajectory"
  | "xrd"
  | "electronic"
  | "phonon"
  | "volumetric"
  | "detected"
  | "generic";

function inferDataKind(dataset: ProjectHistory["datasets"][number]): DataKind {
  const name = dataset.name.toLowerCase();
  const resources = dataset.import.resources || [];
  const objectTypes = new Set(
    resources.map((item) => String(item.objectType || "").toLowerCase()),
  );
  // Prefer validated normalized object types over filenames/profile text. In
  // particular, phonon band/DOS must never be routed to the electronic viewer.
  if (
    objectTypes.has("phononband") ||
    objectTypes.has("phonondos") ||
    objectTypes.has("phononeigenvector")
  )
    return "phonon";
  if (objectTypes.has("electronicband") || objectTypes.has("electronicdos"))
    return "electronic";
  if (objectTypes.has("trajectory")) return "trajectory";
  if (objectTypes.has("structure") || objectTypes.has("atoms"))
    return "structure";
  if (objectTypes.has("volumetricdata")) return "volumetric";
  if (name.includes("xrd")) return "xrd";
  const text =
    `${dataset.profile?.datasetType || ""} ${resources.map((item) => JSON.stringify(item)).join(" ")} ${name}`.toLowerCase();
  if (text.includes("trajectory") || text.includes("xyz")) return "trajectory";
  if (
    text.includes("structure") ||
    text.includes("cif") ||
    text.includes("poscar")
  )
    return "structure";
  if (text.includes("xrd")) return "xrd";
  if (text.includes("phonon")) return "phonon";
  if (text.includes("band") || text.includes("dos")) return "electronic";
  if (text.includes("volumetric") || text.includes("cube")) return "volumetric";
  if (text.includes("zip") || resources.length > 1) return "detected";
  if (dataset.profile?.rowCount) return "table";
  return "generic";
}

export function resolveDatasetSelection(
  queryDatasetId: string,
  selectedId: string,
  visibleDatasetIds: readonly string[],
): string {
  if (queryDatasetId) return visibleDatasetIds.includes(queryDatasetId) ? queryDatasetId : "";
  if (selectedId && visibleDatasetIds.includes(selectedId)) {
    return selectedId;
  }
  return visibleDatasetIds[0] || "";
}

export function ProjectDataPage({
  projectId,
  initialDatasetId = "",
  initialObjectId = "",
  initialObjectVersionId = "",
}: {
  projectId: string;
  initialDatasetId?: string;
  initialObjectId?: string;
  initialObjectVersionId?: string;
}) {
  // This component stays mounted across App Router query transitions. Keep
  // the URL query as the live selection authority so the viewer cannot show
  // the previous dataset/object after a client-side navigation.
  const searchParams = useSearchParams();
  const hasRouteQuery = Boolean(searchParams?.toString());
  const queryDatasetId = searchParams?.has("dataset")
    ? searchParams.get("dataset") || ""
    : hasRouteQuery
      ? ""
      : initialDatasetId;
  const queryObjectId = searchParams?.has("object")
    ? searchParams.get("object") || ""
    : hasRouteQuery
      ? ""
      : initialObjectId;
  const queryObjectVersionId = searchParams?.has("version")
    ? searchParams.get("version") || ""
    : hasRouteQuery
      ? ""
      : initialObjectVersionId;
  const queryTableSearch = searchParams?.get("tableQuery") || "";
  const queryTableSort =
    searchParams?.get("tableSort") === "desc" ? "desc" : "asc";
  const queryTableRow = searchParams?.get("tableRow") || "";
  const querySelectionToken = searchParams?.get("selection") || "";
  const queryResourceId = searchParams?.get("resource") ?? null;
  const { history, setHistory, state, error, retry } = useProject(projectId);
  const [selectedId, setSelectedId] = useState("");
  const [statusFilter, setStatusFilter] = useState<
    "active" | "archived" | "trashed"
  >("active");
  const changeStatusFilter = (next: "active" | "archived" | "trashed") => {
    setStatusFilter(next);
    setSelectedDatasetIds(new Set());
    setSelectedScientificObjectIds(new Set());
  };
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedDatasetIds, setSelectedDatasetIds] = useState<Set<string>>(
    new Set(),
  );
  const [selectedScientificObjectIds, setSelectedScientificObjectIds] =
    useState<Set<string>>(new Set());
  const [dialog, setDialog] = useState<{
    dataset: ProjectDataset;
    mode: "edit" | "trash" | "delete";
  } | null>(null);
  const objectOperation = useScientificObjectOperation(projectId);
  const datasetOperation = useDatasetOperation(projectId);
  const busy = objectOperation.pending || objectOperation.reading || datasetOperation.pending || datasetOperation.reading;
  const dataHeadingRef = useRef<HTMLHeadingElement | null>(null);
  async function recoverDatasets() {
    const recovered = await datasetOperation.reconcile((next) => {
      setHistory(next);
      setDialog((current) => { const dataset = next.datasets.find((item) => item.datasetId === current?.dataset.datasetId); return current && dataset ? { ...current, dataset } : current; });
      const visible = new Set(next.datasets.filter((item) => statusFilter === "active" ? !["archived", "trashed"].includes(item.status) : item.status === statusFilter).map((item) => item.datasetId));
      setSelectedDatasetIds((current) => new Set([...current].filter((id) => visible.has(id))));
      setDatasetBulkTrashTargets((current) => { const remaining = current?.filter((item) => visible.has(item.datasetId)); return remaining?.length ? remaining : null; });
    });
    if (recovered) window.requestAnimationFrame(() => (document.getElementById("edit-dataset-name") || dataHeadingRef.current)?.focus());
  }
  const datasetRecovery = datasetOperation.uncertain ? <div className="dataset-operation-recovery" role="status"><p>{datasetOperation.error}</p><button type="button" className="product-secondary-action" disabled={busy} onClick={() => void recoverDatasets()}>{datasetOperation.reading ? "正在读取…" : "重新读取数据列表"}</button>{datasetOperation.readError ? <p>{datasetOperation.readError}</p> : null}</div> : datasetOperation.error ? <p className="product-form-error" role="alert">{datasetOperation.error}</p> : null;
  const [inspector, setInspector] = useState(false);
  const [mobileNavigatorCollapsed, setMobileNavigatorCollapsed] = useState(false);
  const navigator = useDataNavigator();
  const [directoryView, setDirectoryView] = useState<"datasets" | "objects">(queryObjectId ? "objects" : "datasets");
  const dataViewsRef = useRef<HTMLElement | null>(null);
  useEffect(() => { setDirectoryView(queryObjectId ? "objects" : "datasets"); }, [projectId, queryObjectId, queryDatasetId]);
  const changeDirectoryView = (view: "datasets" | "objects") => {
    setDirectoryView(view);
    setSelectionMode(false);
    setSelectedDatasetIds(new Set());
    setSelectedScientificObjectIds(new Set());
  };
  const browseDataViews = () => {
    changeDirectoryView("objects");
    navigator.setCollapsed(false);
    setMobileNavigatorCollapsed(false);
    window.requestAnimationFrame(() => {
      const links = Array.from(dataViewsRef.current?.querySelectorAll<HTMLAnchorElement>("a[href]") || []);
      const target = links.find((link) => new URL(link.href).searchParams.get("object") === queryObjectId) || links[0] || dataViewsRef.current;
      target?.focus();
    });
  };
  const [scientificSelection, setScientificSelection] =
    useState<WorkspaceSelectionContext | null>(null);
  const [selectedSourceAvailability, setSelectedSourceAvailability] = useState<
    "loading" | "ready" | "empty" | "unavailable"
  >("loading");
  const objectDirectory = useScientificObjectDirectory(projectId, statusFilter === "archived" ? "ARCHIVED" : statusFilter === "trashed" ? "TRASHED" : "ACTIVE");
  const scientificObjects = useMemo(() => [...new Map([
    ...objectDirectory.items.map((item) => [item.id, item] as const),
    ...Object.values(objectOperation.known).map((item) => [item.id, item] as const),
  ]).values()].filter((item) => item.lifecycle_status.toLowerCase() === statusFilter), [objectDirectory.items, objectOperation.known, statusFilter]);
  const [scientificObjectTrashTarget, setScientificObjectTrashTarget] =
    useState<ScientificObjectSummary | null>(null);
  const [scientificObjectBulkTrashTargets, setScientificObjectBulkTrashTargets] =
    useState<ScientificObjectSummary[] | null>(null);
  const [datasetBulkTrashTargets, setDatasetBulkTrashTargets] =
    useState<ProjectDataset[] | null>(null);
  useEffect(() => {
    const visible = new Set(scientificObjects.map((item) => item.id));
    setSelectedScientificObjectIds((current) => new Set([...current].filter((id) => visible.has(id))));
    setScientificObjectBulkTrashTargets((current) => {
      const remaining = current?.filter((item) => objectOperation.known[item.id]?.lifecycle_status !== "TRASHED");
      return remaining?.length ? remaining : null;
    });
  }, [scientificObjects, objectOperation.known]);
  const objectRecovery = objectOperation.error ? <div className="dataset-operation-recovery" role="alert"><p>{objectOperation.error}</p><button type="button" className="product-secondary-action" disabled={busy} onClick={() => {
    void objectOperation.recheck("directory").then((success) => { if (success) window.requestAnimationFrame(() => {
      const dialog = document.querySelector<HTMLElement>("[role='dialog']");
      (dialog?.querySelector<HTMLElement>("footer button:last-child:not(:disabled)") || dataHeadingRef.current)?.focus();
    }); });
  }}>{objectOperation.reading ? "正在核对…" : "重新读取对象状态"}</button>{objectOperation.readError ? <p>{objectOperation.readError}</p> : null}</div> : null;
  const objectPreview = useDependencyPreview(
    scientificObjectTrashTarget ? [{ id: scientificObjectTrashTarget.id, label: scientificObjectTrashTarget.display_name }] : [],
    getScientificObjectDependencyImpact,
  );
  const objectBulkPreview = useDependencyPreview(
    (scientificObjectBulkTrashTargets || []).map((item) => ({ id: item.id, label: item.display_name })),
    getScientificObjectDependencyImpact,
  );
  const datasetBulkPreview = useDependencyPreview(
    (datasetBulkTrashTargets || []).map((item) => ({ id: item.datasetId, label: item.name })),
    getDatasetDependencyImpact,
  );
  const inspectorTriggerRef = useRef<HTMLElement | null>(null);
  const inspectorTriggerLabelRef = useRef<string | null>(null);
  const inspectorCloseRef = useRef<HTMLButtonElement | null>(null);
  const visibleDatasets = useMemo(
    () =>
      (history?.datasets || []).filter((dataset) => {
        if (statusFilter === "trashed") return dataset.status === "trashed";
        if (statusFilter === "archived") return dataset.status === "archived";
        return dataset.status !== "archived" && dataset.status !== "trashed";
      }),
    [history?.datasets, statusFilter],
  );
  useEffect(() => {
    if (typeof window.matchMedia !== "function") return;
    const media = window.matchMedia("(max-width: 960px)");
    const sync = () => setMobileNavigatorCollapsed(media.matches);
    sync();
    media.addEventListener("change", sync);
    return () => media.removeEventListener("change", sync);
  }, []);
  useEffect(() => {
    const nextSelection = resolveDatasetSelection(
      queryDatasetId,
      selectedId,
      (queryDatasetId ? history?.datasets || [] : visibleDatasets).map((item) => item.datasetId),
    );
    if (nextSelection !== selectedId) setSelectedId(nextSelection);
  }, [queryDatasetId, selectedId, visibleDatasets, history?.datasets]);
  const openInspector = () => {
    const active = document.activeElement;
    if (active instanceof HTMLElement && active !== document.body) {
      inspectorTriggerRef.current = active;
      inspectorTriggerLabelRef.current = active.getAttribute("aria-label");
    }
    setInspector(true);
  };
  const closeInspector = () => {
    const trigger = inspectorTriggerRef.current;
    const triggerLabel = inspectorTriggerLabelRef.current;
    setInspector(false);
    inspectorTriggerRef.current = null;
    inspectorTriggerLabelRef.current = null;
    window.requestAnimationFrame(() => {
      const currentTrigger = trigger?.isConnected
        ? trigger
        : triggerLabel
          ? Array.from(
              document.querySelectorAll<HTMLElement>("[aria-label]"),
            ).find((item) => item.getAttribute("aria-label") === triggerLabel)
          : null;
      currentTrigger?.focus();
    });
  };
  useEffect(() => {
    if (!inspector) return;
    inspectorCloseRef.current?.focus();
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeInspector();
    };
    document.addEventListener("keydown", close);
    return () => document.removeEventListener("keydown", close);
  }, [inspector]);
  useEffect(() => {
    const remember = (event: Event) => {
      const target =
        event.target instanceof HTMLElement
          ? event.target.closest<HTMLElement>("button, a[href], [tabindex]")
          : null;
      if (
        target &&
        document.querySelector(".scientific-viewer")?.contains(target)
      ) {
        inspectorTriggerRef.current = target;
        inspectorTriggerLabelRef.current = target.getAttribute("aria-label");
      }
    };
    document.addEventListener("pointerdown", remember, true);
    document.addEventListener("click", remember, true);
    document.addEventListener("focusin", remember, true);
    return () => {
      document.removeEventListener("pointerdown", remember, true);
      document.removeEventListener("click", remember, true);
      document.removeEventListener("focusin", remember, true);
    };
  }, []);
  const selected = queryDatasetId
    ? history?.datasets.find((item) => item.datasetId === queryDatasetId)
    : visibleDatasets.find((item) => item.datasetId === selectedId);
  useEffect(() => {
    setScientificSelection(
      resolveDataPageSelection(
        querySelectionToken,
        projectId,
        selected?.datasetId,
      ),
    );
  }, [projectId, querySelectionToken, selected?.datasetId]);
  useEffect(() => {
    setSelectedSourceAvailability("loading");
  }, [selected?.datasetId]);
  const objectRouteMissingVersion = Boolean(
    queryObjectId && !queryObjectVersionId,
  );
  const kind = selected ? inferDataKind(selected) : "generic";
  const canWriteProject = projectRoleAllows(history?.project.role, "write");
  const allVisibleDatasetsSelected =
    visibleDatasets.length > 0 &&
    visibleDatasets.every((dataset) =>
      selectedDatasetIds.has(dataset.datasetId),
    );
  const selectableObjects = scientificObjects.filter((item) => item.current_version_id);
  const directoryFeedbackInViewer = !selected && !queryDatasetId && !queryObjectId && selectableObjects.length === 0;
  const allVisibleObjectsSelected = selectableObjects.length > 0 && selectableObjects.every((item) => selectedScientificObjectIds.has(item.id));
  const handleSelection = (selection: WorkspaceSelectionContext) => {
    setScientificSelection(selection);
    try {
      const token = encodeWorkspaceSelectionUrl(selection);
      const next = dataTableViewHref(window.location.href, {
        selection: selection.cleared ? "" : token,
        ...(!selection.cleared && selection.primary ? {
          resource: selection.primary.kind === "VOLUMETRIC_FIELD"
            ? /^source:(.+):volumetric-dataset$/.exec(selection.primary.artifactId || "")?.[1]
            : selection.primary.artifactId?.startsWith("source:")
            ? selection.primary.artifactId.slice("source:".length)
            : selection.primary.phononArtifactId?.startsWith("source:") ? selection.primary.phononArtifactId.slice("source:".length)
            : selection.primary.objectId || undefined,
        } : {}),
      });
      pushProductQuery(next, { scientificSelection: true });
    } catch {
      // Keep the in-tab selection usable. Only validated, bounded exact
      // selections may become shareable URL state.
    }
  };
  const updateTableViewRoute = (
    changes: DataTableRouteState,
    mode: "push" | "replace",
  ) => {
    const next = dataTableViewHref(window.location.href, changes);
    if (mode === "push") pushProductQuery(next, { dataTableView: true });
    else replaceProductQuery(next);
  };
  const changeResource = (resourceId: string) => {
    if (!selected) return;
    setScientificSelection(null);
    const next = new URL(dataTableViewHref(window.location.href, { resource: resourceId, selection: "", query: "", sort: "asc", row: "" }), window.location.origin);
    next.searchParams.set("dataset", selected.datasetId);
    pushProductQuery(`${next.pathname}${next.search}${next.hash}`, { dataResourceView: true });
  };
  async function setScientificObjectLifecycle(item: ScientificObjectSummary, lifecycle: "ACTIVE" | "ARCHIVED" | "TRASHED"): Promise<boolean> {
    if (busy || !canWriteProject) return false;
    const success = await objectOperation.update([item.id], lifecycle, "directory");
    if (success) window.requestAnimationFrame(() => dataHeadingRef.current?.focus());
    return success;
  }
  async function applyScientificObjectBatch(lifecycle: "ACTIVE" | "ARCHIVED" | "TRASHED", confirmedIds?: string[]): Promise<boolean> {
    const ids = confirmedIds || scientificObjects.filter((item) => selectedScientificObjectIds.has(item.id)).map((item) => item.id);
    if (!ids.length || busy || !canWriteProject) return false;
    const success = await objectOperation.update(ids, lifecycle, "directory", true);
    if (success) { setSelectedScientificObjectIds(new Set()); setSelectionMode(false); window.requestAnimationFrame(() => dataHeadingRef.current?.focus()); }
    return success;
  }
  function requestScientificObjectBulkTrash() {
    if (!selectedScientificObjectIds.size || busy) return;
    const targets = scientificObjects.filter((item) =>
      selectedScientificObjectIds.has(item.id),
    );
    if (!targets.length) return;

    setScientificObjectBulkTrashTargets(targets);
  }
  function confirmScientificObjectBulkTrash() {
    if (
      !scientificObjectBulkTrashTargets ||
      !objectBulkPreview.complete
    ) {
      return;
    }
    void applyScientificObjectBatch("TRASHED", scientificObjectBulkTrashTargets.map((item) => item.id)).then((success) => {
      if (success) {
        setScientificObjectBulkTrashTargets(null);
      }
    });
  }
  const scientificObjectActions = (
    item: ScientificObjectSummary,
  ): ObjectAction[] => [
    {
      label: "打开科研对象",
      href: `/projects/${projectId}/data?object=${encodeURIComponent(item.id)}${item.current_version_id ? `&version=${encodeURIComponent(item.current_version_id)}` : ""}`,
    },
    canWriteProject
      ? {
          label:
            item.lifecycle_status === "ARCHIVED"
              ? "恢复科研对象"
              : item.lifecycle_status === "TRASHED"
                ? "恢复科研对象"
                : "归档科研对象",
          onSelect: () =>
            void setScientificObjectLifecycle(
              item,
              item.lifecycle_status === "TRASHED"
                ? "ACTIVE"
                : item.lifecycle_status === "ARCHIVED"
                  ? "ACTIVE"
                  : "ARCHIVED",
            ),
          disabled: busy || objectOperation.uncertain,
        }
      : { label: "查看研究记录", href: `/projects/${projectId}/research` },
      canWriteProject && item.lifecycle_status === "ACTIVE"
      ? {
          label: "移入回收站",
          destructive: true,
          onSelect: () => setScientificObjectTrashTarget(item),
        }
      : null,
  ].filter(Boolean) as ObjectAction[];
  const updateLocalDataset = (
    datasetId: string,
    changes: Partial<ProjectDataset>,
  ) =>
    setHistory((current) =>
      current
        ? {
            ...current,
            datasets: current.datasets.map((dataset) =>
              dataset.datasetId === datasetId
                ? { ...dataset, ...changes }
                : dataset,
            ),
          }
        : current,
    );
  async function setDatasetArchived(
    dataset: ProjectDataset,
    archived: boolean,
  ) {
    if (busy || !canWriteProject) return;
    await datasetOperation.run(archived ? "归档数据集" : "恢复数据集", async (signal) => validateDataset(await updateDataset(dataset.datasetId, { archived }, signal), projectId, dataset.datasetId, { archived }, dataset.status), (changes) => {
      updateLocalDataset(dataset.datasetId, changes);
      window.requestAnimationFrame(() => dataHeadingRef.current?.focus());
    });
  }
  async function restoreDataset(dataset: ProjectDataset) {
    await setDatasetArchived(dataset, false);
  }
  async function applyDatasetBatch(
    action: "archive" | "trash" | "restore",
    confirmedIds?: string[],
  ): Promise<boolean> {
    const ids = confirmedIds || visibleDatasets.filter((item) => selectedDatasetIds.has(item.datasetId)).map((item) => item.datasetId);
    if (!ids.length || busy || !canWriteProject) return false;
    return datasetOperation.run("批量更新数据集", async (signal) => { await updateDatasetBatches(ids, action, signal, (confirmed) => {
      const completed = new Set(confirmed);
      const status = action === "archive" ? "archived" : "trashed";
      if (action !== "restore") setHistory((current) => current ? { ...current, datasets: current.datasets.map((item) => completed.has(item.datasetId) ? { ...item, status } : item) } : current);
      setSelectedDatasetIds((current) => new Set([...current].filter((id) => !completed.has(id))));
      setDatasetBulkTrashTargets((current) => { const remaining = current?.filter((item) => !completed.has(item.datasetId)); return remaining?.length ? remaining : null; });
    });
      return action === "restore" ? readDatasetDirectory(projectId, signal) : null;
    }, (next) => { if (next) setHistory(next); setSelectionMode(false); window.requestAnimationFrame(() => dataHeadingRef.current?.focus()); });
  }
  function requestDatasetBulkTrash() {
    if (!selectedDatasetIds.size || busy) return;
    const targets = (history?.datasets || []).filter((item) =>
      selectedDatasetIds.has(item.datasetId),
    );
    if (!targets.length) return;

    setDatasetBulkTrashTargets(targets);
  }
  function confirmDatasetBulkTrash() {
    if (
      !datasetBulkTrashTargets ||
      !datasetBulkPreview.complete
    ) {
      return;
    }
    void applyDatasetBatch("trash", datasetBulkTrashTargets.map((item) => item.datasetId)).then((success) => {
      if (success) {
        setDatasetBulkTrashTargets(null);
      }
    });
  }
  const datasetActions = (dataset: ProjectDataset): ObjectAction[] => {
    const actions: ObjectAction[] = [
      {
        label: "打开数据",
        href: `/projects/${projectId}/data?dataset=${dataset.datasetId}`,
      },
    ];
    if (dataset.status === "trashed") {
      if (canWriteProject)
        actions.push({
          label: "从回收站恢复",
          disabled: busy || datasetOperation.uncertain,
          onSelect: () => void restoreDataset(dataset),
        });
      else
        actions.push({
          label: "查看研究记录",
          href: `/projects/${projectId}/research`,
        });
      if (projectRoleAllows(history?.project.role, "purge"))
        actions.push({
          label: "永久删除空数据集",
          destructive: true,
          onSelect: () => setDialog({ dataset, mode: "delete" }),
        });
      return actions;
    }
    actions.push(
      canWriteProject
        ? {
            label: "研究此数据",
            href: `/projects/${projectId}/research?dataset=${dataset.datasetId}`,
          }
        : { label: "查看研究记录", href: `/projects/${projectId}/research` },
    );
    if (canWriteProject) {
      actions.push({
        label: "重命名数据集",
        onSelect: () => setDialog({ dataset, mode: "edit" }),
      });
      actions.push({
        label: dataset.status === "archived" ? "恢复数据集" : "归档数据集",
        disabled: busy || datasetOperation.uncertain,
        onSelect: () =>
          void setDatasetArchived(dataset, dataset.status !== "archived"),
      });
      if (projectRoleAllows(history?.project.role, "purge"))
        actions.push({
          label: "移入回收站",
          destructive: true,
          onSelect: () => setDialog({ dataset, mode: "trash" }),
        });
    }
    return actions;
  };
  const toggleDatasetSelected = (datasetId: string, checked: boolean) =>
    setSelectedDatasetIds((current) => {
      const next = new Set(current);
      if (checked) next.add(datasetId);
      else next.delete(datasetId);
      return next;
    });
  const toggleScientificObjectSelected = (
    objectId: string,
    checked: boolean,
  ) =>
    setSelectedScientificObjectIds((current) => {
      const next = new Set(current);
      if (checked) next.add(objectId);
      else next.delete(objectId);
      return next;
    });
  const confirmScientificObjectTrash = () => {
    if (!scientificObjectTrashTarget || !objectPreview.complete) return;
    void setScientificObjectLifecycle(scientificObjectTrashTarget, "TRASHED").then(
      (updated) => {
        if (updated) setScientificObjectTrashTarget(null);
      },
    );
  };
  return (
    <RequireProductAuth>
      <ProductShell projectId={projectId}>
        {scientificObjectTrashTarget ? (
          <ScientificObjectTrashDialog
            item={scientificObjectTrashTarget}
            preview={objectPreview}
            busy={busy}
            error=""
            recovery={objectRecovery}
            locked={objectOperation.uncertain}
            onClose={() => { objectOperation.dismiss("directory"); setScientificObjectTrashTarget(null); }}
            onConfirm={confirmScientificObjectTrash}
          />
        ) : null}
        {scientificObjectBulkTrashTargets ? (
          <ScientificObjectBulkTrashDialog
            items={scientificObjectBulkTrashTargets}
            preview={objectBulkPreview}
            busy={busy}
            error=""
            recovery={objectRecovery}
            locked={objectOperation.uncertain}
            onClose={() => {
              objectOperation.dismiss("directory");
              setScientificObjectBulkTrashTargets(null);
            }}
            onConfirm={confirmScientificObjectBulkTrash}
          />
        ) : null}
        {datasetBulkTrashTargets ? (
          <DatasetBulkTrashDialog
            items={datasetBulkTrashTargets}
            preview={datasetBulkPreview}
            busy={busy}
            locked={datasetOperation.uncertain}
            error=""
            recovery={datasetRecovery}
            onClose={() => {
              datasetOperation.dismiss();
              setDatasetBulkTrashTargets(null);
            }}
            onConfirm={confirmDatasetBulkTrash}
          />
        ) : null}
        <section className="data-workbench" ref={navigator.workbenchRef} style={navigator.style} data-directory-collapsed={navigator.collapsed} data-directory-dragging={navigator.dragging}>
          {!history ? <EmptyOrError state={state} error={error} onRetry={retry} /> : null}
          {history && (
            <>
              <aside className="data-navigator" aria-label="项目数据目录" data-mobile-collapsed={mobileNavigatorCollapsed}>
                <header>
                  <div className="data-navigator-heading">
                    <div className="data-navigator-title">
                      <h1 ref={dataHeadingRef} tabIndex={-1}>项目数据</h1>
                      {statusFilter !== "active" ? <span className="data-navigator-filter-label">{statusFilter === "archived" ? "已归档" : "回收站"}</span> : null}
                    </div>
                    {canWriteProject ? (
                      <button
                        type="button"
                        className="product-icon-action data-directory-select"
                        aria-label={
                          selectionMode
                            ? "退出数据选择"
                            : "选择多个数据或科研对象"
                        }
                        aria-pressed={selectionMode}
                        title={selectionMode ? "退出选择" : "批量选择"}
                        onClick={() => {
                          setSelectionMode((value) => !value);
                          setSelectedDatasetIds(new Set());
                          setSelectedScientificObjectIds(new Set());
                        }}
                      >
                        {selectionMode ? "×" : "✓"}
                      </button>
                    ) : null}
                    <button type="button" className="data-navigator-collapse" aria-label={navigator.collapsed ? "展开数据目录" : "收起数据目录"} title={navigator.collapsed ? "展开数据目录" : "收起数据目录"} aria-expanded={!navigator.collapsed} aria-controls="data-navigator-content" onClick={() => navigator.setCollapsed((value) => !value)}>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2" /><path d="M9 4v16" /><path d={navigator.collapsed ? "m13 9 3 3-3 3" : "m16 9-3 3 3 3"} /></svg>
                      {navigator.collapsed ? <span>目录</span> : null}
                    </button>
                    <button
                      type="button"
                      className="data-navigator-toggle"
                      aria-expanded={!mobileNavigatorCollapsed}
                      aria-controls="data-navigator-content"
                      onClick={() =>
                        setMobileNavigatorCollapsed((collapsed) => !collapsed)
                      }
                    >
                      {mobileNavigatorCollapsed ? "展开目录" : "收起目录"}
                    </button>
                  </div>
                </header>
                <div
                  id="data-navigator-content"
                  className="data-navigator-content"
                  data-mobile-collapsed={mobileNavigatorCollapsed}
                >
                  <div className="data-navigator-controls">
                    <div
                      className="segmented-control"
                      role="group"
                      aria-label="数据集状态"
                    >
                      <button
                        type="button"
                        aria-pressed={statusFilter === "active"}
                        onClick={() => changeStatusFilter("active")}
                      >
                        当前
                      </button>
                      <button
                        type="button"
                        aria-pressed={statusFilter === "archived"}
                        onClick={() => changeStatusFilter("archived")}
                      >
                        已归档
                      </button>
                      <button
                        type="button"
                        aria-pressed={statusFilter === "trashed"}
                        onClick={() => changeStatusFilter("trashed")}
                      >
                        回收站
                      </button>
                    </div>

                  </div>
                <div className="data-directory-switch" role="group" aria-label="目录内容">
                  <button type="button" aria-pressed={directoryView === "objects"} onClick={() => changeDirectoryView("objects")}>数据视图</button>
                  <button type="button" aria-pressed={directoryView === "datasets"} onClick={() => changeDirectoryView("datasets")}>上传记录</button>
                </div>
                {selectionMode ? (
                  <div
                    className="data-batch-actions"
                    role="region"
                    aria-label="批量数据操作"
                  >
                    <div className="data-batch-selection-summary">
                      <strong>
                        {selectedDatasetIds.size +
                          selectedScientificObjectIds.size}{" "}
                        个已选择
                      </strong>
                      <span>当前筛选</span>
                    </div>
                    <div className="data-batch-selection-tools">
                      {directoryView === "datasets" ? <button
                        type="button"
                        className="data-batch-select-all"
                        disabled={!visibleDatasets.length || busy}
                        onClick={() =>
                          setSelectedDatasetIds(
                            allVisibleDatasetsSelected
                              ? new Set()
                              : new Set(
                                  visibleDatasets.map(
                                    (item) => item.datasetId,
                                  ),
                                ),
                          )
                        }
                      >
                        {allVisibleDatasetsSelected ? "清空数据" : "全选数据"}
                      </button> : null}
                      {directoryView === "objects" && selectableObjects.length ? (
                        <button
                          type="button"
                          className="data-batch-select-all"
                          disabled={busy}
                          onClick={() =>
                            setSelectedScientificObjectIds(
                              allVisibleObjectsSelected
                                ? new Set()
                                : new Set(
                                    selectableObjects.map((item) => item.id),
                                  ),
                            )
                          }
                        >
                          {allVisibleObjectsSelected ? "清空对象" : "全选对象"}
                        </button>
                      ) : null}
                    </div>
                    {directoryView === "datasets" ? <div className="data-batch-selection-actions">
                      {statusFilter === "trashed" ? (
                        <button
                          type="button"
                          disabled={!selectedDatasetIds.size || busy || datasetOperation.uncertain}
                          onClick={() => void applyDatasetBatch("restore")}
                        >
                          恢复
                        </button>
                      ) : (
                        <>
                          <button
                            type="button"
                            disabled={
                              !selectedDatasetIds.size ||
                              datasetOperation.uncertain ||
                              busy ||
                              statusFilter === "archived"
                            }
                            onClick={() => void applyDatasetBatch("archive")}
                          >
                            归档
                          </button>
                          <button
                            type="button"
                            className="product-danger-action"
                            disabled={!selectedDatasetIds.size || busy || datasetOperation.uncertain}
                            onClick={requestDatasetBulkTrash}
                          >
                            移入回收站
                          </button>
                        </>
                      )}
                    </div> : null}
                  </div>
                ) : null}
                {selectionMode && selectedScientificObjectIds.size ? (
                  <div
                    className="data-batch-actions scientific-object-batch-actions"
                    role="region"
                    aria-label="批量科研对象操作"
                  >
                    <strong>
                      {selectedScientificObjectIds.size} 个科研对象已选择
                    </strong>
                    {statusFilter === "trashed" ||
                    statusFilter === "archived" ? (
                      <button
                        type="button"
                        disabled={busy || objectOperation.uncertain}
                        onClick={() =>
                          void applyScientificObjectBatch("ACTIVE")
                        }
                      >
                        恢复科研对象
                      </button>
                    ) : (
                      <>
                        <button
                          type="button"
                          disabled={busy || objectOperation.uncertain}
                          onClick={() =>
                            void applyScientificObjectBatch("ARCHIVED")
                          }
                        >
                          归档科研对象
                        </button>
                        <button
                          type="button"
                          className="product-danger-action"
                          disabled={busy || objectOperation.uncertain}
                          onClick={requestScientificObjectBulkTrash}
                        >
                          移入回收站
                        </button>
                      </>
                    )}
                  </div>
                ) : null}
                {!dialog && !datasetBulkTrashTargets ? datasetRecovery : null}
                {!scientificObjectTrashTarget && !scientificObjectBulkTrashTargets && objectOperation.origin !== `viewer:${queryObjectId}:${queryObjectVersionId}` ? objectRecovery : null}
                <section className="data-directory-list" aria-label="上传记录" hidden={directoryView !== "datasets"}>
                <p className="data-directory-count">{visibleDatasets.length} 条上传记录</p>
                {visibleDatasets.length === 0 ? (
                  <div className="data-navigator-empty">
                    <p>{statusFilter === "archived" ? "没有已归档的上传记录。" : statusFilter === "trashed" ? "上传记录回收站为空。" : "还没有上传记录。"}</p>
                    {scientificObjects.length > 0 ? <button type="button" className="product-secondary-action" onClick={browseDataViews}>查看数据视图</button> : null}
                  </div>
                ) : null}
                <div className="data-tree managed-data-tree">
                  {visibleDatasets.map((dataset) => (
                    <ManagedObjectRow
                      key={dataset.datasetId}
                      href={`/projects/${projectId}/data?dataset=${dataset.datasetId}`}
                      title={productProjectName(dataset.name)}
                      truncateTitle
                      onOpen={() => setMobileNavigatorCollapsed(true)}
                      description={`${dataset.import.fileCount} 个文件 · ${dataKindLabel(inferDataKind(dataset))}`}
                      trailing={
                        dataset.status === "trashed"
                            ? "回收站"
                            : dataset.status === "archived"
                              ? "已归档"
                              : undefined
                      }
                      actions={datasetActions(dataset)}
                      selectionMode={selectionMode}
                      selected={selectedDatasetIds.has(dataset.datasetId)}
                      active={
                        !selectionMode &&
                        !queryObjectId &&
                        dataset.datasetId === selected?.datasetId
                      }
                      onSelectedChange={(checked) =>
                        toggleDatasetSelected(dataset.datasetId, checked)
                      }
                    />
                  ))}
                </div>
                </section>
                {(
                  <section
                    ref={dataViewsRef}
                    tabIndex={-1}
                    className="scientific-object-list data-directory-list"
                    aria-label="数据视图"
                    hidden={directoryView !== "objects"}
                  >
                    <p className="data-directory-count">{objectDirectory.nextCursor ? `已显示 ${scientificObjects.length} 项数据` : objectDirectory.state === "ready" ? `${scientificObjects.length} 项数据` : ""}</p>
                    {objectDirectory.state === "loading" && !directoryFeedbackInViewer ? <p className="data-navigator-section-hint" role="status">正在读取数据视图…</p> : null}
                    {objectDirectory.state === "error" && !directoryFeedbackInViewer ? <div className="data-directory-feedback" role="alert"><p>{objectDirectory.error}</p><button type="button" className="product-secondary-action" onClick={objectDirectory.retry}>重新加载科研对象</button></div> : null}
                    {objectDirectory.state === "ready" && scientificObjects.length === 0 ? <div className="data-navigator-empty"><p>{statusFilter === "archived" ? "没有已归档的数据视图。" : statusFilter === "trashed" ? "数据视图回收站为空。" : "还没有可查看的数据视图。"}</p>{visibleDatasets.length > 0 ? <button type="button" className="product-secondary-action" onClick={() => changeDirectoryView("datasets")}>查看上传记录</button> : null}</div> : null}
                    <div className="managed-scientific-object-list managed-data-tree">
                      {scientificObjects.map((item) =>
                        item.current_version_id ? (
                          <ManagedObjectRow
                            key={item.id}
                            href={`/projects/${projectId}/data?object=${encodeURIComponent(item.id)}&version=${encodeURIComponent(item.current_version_id)}`}
                            title={item.display_name}
                            truncateTitle
                            onOpen={() => setMobileNavigatorCollapsed(true)}
                            description={scientificObjectTypeLabel(
                              item.object_type,
                            )}
                            trailing={
                              item.lifecycle_status === "ARCHIVED"
                                ? "已归档"
                                : item.lifecycle_status === "TRASHED"
                                  ? "回收站"
                                : undefined
                            }
                            actions={scientificObjectActions(item)}
                            selectionMode={selectionMode}
                            selected={selectedScientificObjectIds.has(item.id)}
                            active={item.id === queryObjectId}
                            onSelectedChange={(checked) =>
                              toggleScientificObjectSelected(item.id, checked)
                            }
                          />
                        ) : <UnavailableDataEntry key={item.id} title={item.display_name} />,
                      )}
                    </div>
                    {objectDirectory.nextCursor ? <button type="button" className="product-secondary-action" disabled={objectDirectory.state !== "ready"} onClick={objectDirectory.loadMore}>加载更多科研对象</button> : null}
                  </section>
                )}
                {canWriteProject && statusFilter === "active" ? (
                  <Link
                    className="product-secondary-action data-upload"
                    href={`/projects/${projectId}/datasets/new`}
                  >
                    上传数据
                  </Link>
                ) : null}
                </div>
              </aside>
              <div className="data-directory-divider" {...navigator.separatorProps}><span aria-hidden="true" /></div>
              <section className="scientific-viewer">
                {objectRouteMissingVersion ? (
                  <div className="product-state" role="alert">
                    <h2>这个链接缺少数据版本</h2>
                    <p>请从数据视图中重新选择这份数据。</p>
                    <button
                      type="button"
                      className="product-secondary-action"
                      onClick={browseDataViews}
                    >
                      选择数据版本
                    </button>
                  </div>
                ) : queryObjectId && queryObjectVersionId ? (
                  <LazyScientificObjectViewer
                    management={objectOperation}
                    projectId={projectId}
                    objectId={queryObjectId}
                    versionId={queryObjectVersionId}
                    canManage={canWriteProject}
                    canResearch={projectRoleAllows(history?.project.role, "research")}
                    initialSelectionToken={querySelectionToken}
                  />
                ) : queryDatasetId && !selected ? (
                  <div className="product-state" role={state === "loading" ? "status" : "alert"}>
                    <h2>{state === "loading" ? "正在查找这份数据…" : "暂时无法打开这份数据"}</h2>
                    <p>{state === "error" ? error : "暂未找到链接对应的上传记录。可以重新检查，或从目录选择其他数据。"}</p>
                    <div className="product-row-actions">
                      <button type="button" className="product-primary-action" disabled={state === "loading"} onClick={retry}>{state === "loading" ? "正在检查…" : "重新检查"}</button>
                      <Link className="product-secondary-action" href={`/projects/${projectId}/data`}>浏览项目数据</Link>
                    </div>
                  </div>
                ) : selected ? (
                  <>
                    <header className="viewer-toolbar">
                      <div>
                        <h2>{productProjectName(selected.name)}</h2>
                        <p>
                          {selected.import.fileCount} 个文件 ·{" "}
                          {selected.profile?.rowCount ??
                            selected.profile?.objectCount ??
                            "—"}{" "}
                          个记录
                        </p>
                      </div>
                      <div>
                        {canWriteProject &&
                        selected.status !== "trashed" &&
                        selectedSourceAvailability === "ready" &&
                        Number(selected.import.fileCount || 0) > 0 &&
                        Number(
                          selected.profile?.objectCount ??
                            selected.profile?.rowCount ??
                            0,
                        ) > 0 ? (
                          <Link
                            className="product-primary-action"
                            href={`/projects/${projectId}/research?dataset=${encodeURIComponent(selected.datasetId)}${scientificSelection?.primary?.sampleRef ? `&sample=${encodeURIComponent(scientificSelection.primary.sampleRef)}` : ""}${querySelectionToken && ["DATASET_SAMPLE", "PERIODIC_SITE", "ELECTRONIC_BAND_STATE", "ELECTRONIC_DOS_POINT", "PHONON_Q_POINT", "PHONON_DOS_POINT", "TRAJECTORY_FRAME", "TRAJECTORY_ATOM", "VOLUMETRIC_FIELD"].includes(scientificSelection?.primary?.kind || "") ? `&sourceSelection=${encodeURIComponent(querySelectionToken)}` : ""}`}
                          >
                            研究此数据
                          </Link>
                        ) : null}
                      </div>
                    </header>
                    <ScientificDataView
                      key={`${projectId}:${selected.datasetId}`}
                      projectId={projectId}
                      dataset={selected}
                      kind={kind}
                      onInspect={openInspector}
                      selection={scientificSelection}
                      requestedResourceId={queryDatasetId === selected.datasetId ? queryResourceId : null}
                      onResourceChange={changeResource}
                      onSelection={handleSelection}
                      onAvailabilityChange={setSelectedSourceAvailability}
                      tableRouteState={{
                        query: queryTableSearch,
                        sort: queryTableSort,
                        row: queryTableRow,
                      }}
                      onTableRouteChange={updateTableViewRoute}
                    />
                  </>
                ) : scientificObjects.length > 0 ? (
                  <div className="product-state" role={directoryFeedbackInViewer && objectDirectory.state === "error" ? "alert" : undefined}>
                    <h2>{selectableObjects.length ? "选择一份数据开始查看" : "这些数据暂时无法查看"}</h2>
                    <p>{selectableObjects.length ? "在数据视图中选择表格、结构或图谱，查看具体内容。" : objectDirectory.state === "error" ? "目录暂时无法更新，请重新加载。" : "还没有可打开的版本。可以稍后重新加载数据视图。"}</p>
                    {selectableObjects.length ? <button type="button" className="product-primary-action" onClick={browseDataViews}>浏览数据视图</button> : <button type="button" className="product-secondary-action" disabled={objectDirectory.state === "loading"} onClick={objectDirectory.retry}>{objectDirectory.state === "loading" ? "正在加载…" : "重新加载数据视图"}</button>}
                  </div>
                ) : objectDirectory.state !== "ready" ? (
                  <div className="product-state" role={objectDirectory.state === "error" ? "alert" : "status"}>
                    <h2>{objectDirectory.state === "error" ? "暂时无法读取数据目录" : "正在读取数据目录…"}</h2>
                    {objectDirectory.state === "error" ? <><p>请重新加载，查看项目中已有的数据。</p><button type="button" className="product-primary-action" onClick={objectDirectory.retry}>重新加载目录</button></> : null}
                  </div>
                ) : (
                  <div className="product-state">
                    <h2>
                      {statusFilter === "archived"
                        ? "没有已归档数据"
                        : statusFilter === "trashed"
                          ? "回收站为空"
                          : "尚无项目数据"}
                    </h2>
                    <p>
                      {statusFilter === "archived"
                        ? "切换到当前数据继续查看。"
                        : statusFilter === "trashed"
                          ? "切换到当前数据，或从左侧恢复已移入回收站的数据集。"
                          : "上传支持的材料数据后，可在这里查看与研究。"}
                    </p>
                    {statusFilter === "active" && canWriteProject ? (
                      <Link
                        className="product-primary-action"
                        href={`/projects/${projectId}/datasets/new`}
                      >
                        上传数据
                      </Link>
                    ) : statusFilter !== "active" ? <button type="button" className="product-secondary-action" onClick={() => changeStatusFilter("active")}>查看当前数据</button> : null}
                  </div>
                )}
              </section>
              {inspector && selected && !queryObjectId && (
                <aside
                  className={`context-inspector ${sourceDetailsStyles.inspector}`}
                  role="region"
                  aria-labelledby="context-inspector-title"
                >
                  <header className={sourceDetailsStyles.heading}>
                    <h2 id="context-inspector-title">
                      {scientificSelection?.primary
                        ? `已选${selectionKindLabel(scientificSelection.primary.kind)}`
                        : productProjectName(selected.name)}
                    </h2>
                    <button
                      ref={inspectorCloseRef}
                      type="button"
                      aria-label="关闭详情"
                      onClick={closeInspector}
                    >
                      ×
                    </button>
                  </header>
                  <div className={sourceDetailsStyles.inspectorBody}>
                  {scientificSelection?.primary ? (
                    <dl className={sourceDetailsStyles.summary}>
                      <dt>选择类型</dt>
                      <dd>
                        {selectionKindLabel(scientificSelection.primary.kind)}
                      </dd>
                      <dt>来源数据</dt>
                      <dd>{productProjectName(selected.name)}</dd>
                      <dt>状态</dt>
                      <dd>已选择，可继续查看依据</dd>
                    </dl>
                  ) : (
                    <dl className={sourceDetailsStyles.summary}>
                      <dt>数据类型</dt>
                      <dd>{dataKindLabel(kind)}</dd>
                      <dt>记录</dt>
                      <dd>
                        {selected.profile?.rowCount ??
                          selected.profile?.objectCount ??
                          "未提供"}
                      </dd>
                      <dt>状态</dt>
                      <dd>{dataStatusLabel(selected.status)}</dd>
                    </dl>
                  )}
                  <DatasetSourceDetails key={`${projectId}:${selected.datasetId}`} projectId={projectId} dataset={selected} analyses={history.analyses} />
                  <details>
                    <summary>技术详情</summary>
                    <p>数据标识：{scientificSelection?.primary ? selectionTitle(scientificSelection.primary) : selected.datasetId}</p>
                  </details>
                  </div>
                </aside>
              )}
              {dialog ? (
                <DatasetEditDialog
                  key={`${dialog.dataset.datasetId}:${dialog.mode}`}
                  projectId={projectId}
                  operation={datasetOperation}
                  onReload={() => void recoverDatasets()}
                  available={Boolean(history.datasets.some((item) => item.datasetId === dialog.dataset.datasetId))}
                  canManage={projectRoleAllows(history.project.role, dialog.mode === "delete" ? "purge" : "write")}
                  dataset={dialog.dataset}
                  mode={dialog.mode}
                  onClose={() => { datasetOperation.dismiss(); setDialog(null); }}
                  onUpdated={(changes) =>
                    updateLocalDataset(dialog.dataset.datasetId, changes)
                  }
                  onDeleted={(datasetId) =>
                    setHistory((current) =>
                      current
                        ? {
                            ...current,
                            datasets: current.datasets.filter(
                              (dataset) => dataset.datasetId !== datasetId,
                            ),
                          }
                        : current,
                    )
                  }
                />
              ) : null}
            </>
          )}
        </section>
      </ProductShell>
    </RequireProductAuth>
  );
}

function UploadFilePicker({ id, label, files, onChange, multiple = false, accept, disabled }: {
  id: string;
  label: string;
  files: File[];
  onChange: (files: File[]) => void;
  multiple?: boolean;
  accept?: string;
  disabled: boolean;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  return <div className="upload-field">
    <label id={`${id}-label`} htmlFor={id}>{label}</label>
    <div className="upload-file-select">
      <input ref={inputRef} id={id} type="file" className="upload-file-input" aria-labelledby={`${id}-label`} aria-required="true" multiple={multiple} accept={accept} disabled={disabled} onChange={(event) => {
        const chosen = Array.from(event.currentTarget.files || []);
        if (chosen.length) onChange(chosen);
        event.currentTarget.value = "";
      }} />
      <label className="upload-pick-action" htmlFor={id}>{files.length ? "重新选择" : "选择文件"}</label>
      <span>{files.length ? `已选 ${files.length} 个文件` : multiple ? "可同时选择多个文件" : "尚未选择文件"}</span>
    </div>
    {files.length ? <ul className="upload-file-list" aria-label={`${label}已选择文件`}>
      {files.map((file, index) => <li key={`${file.name}:${file.size}:${index}`}>
        <span className="upload-file-name">{file.name}</span>
        <span className="upload-file-size">{file.size < 1024 ? `${file.size} B` : file.size < 1024 * 1024 ? `${(file.size / 1024).toFixed(1)} KiB` : `${(file.size / (1024 * 1024)).toFixed(1)} MiB`}</span>
        <button type="button" disabled={disabled} aria-label={`移除 ${label} ${file.name}`} onClick={() => {
          onChange(files.filter((_, itemIndex) => itemIndex !== index));
          window.requestAnimationFrame(() => inputRef.current?.focus());
        }}>移除</button>
      </li>)}
    </ul> : null}
  </div>;
}

export function DatasetUploadPage({ projectId }: { projectId: string }) {
  return <DatasetUploadForm key={projectId} projectId={projectId} />;
}

function DatasetUploadForm({ projectId }: { projectId: string }) {
  const {
    history,
    state: projectState,
    error: projectError,
    retry: retryProject,
  } = useProject(projectId);
  const [name, setName] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [uploadMode, setUploadMode] = useState<"files" | "phonon">("files");
  const [uploaded, setUploaded] = useState<{ datasetId: string | null; name: string; fileCount: number } | null>(null);
  const uploadingRef = useRef(false);
  const resultRef = useRef<HTMLHeadingElement | null>(null);
  const nameRef = useRef<HTMLInputElement | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [phononStructureFile, setPhononStructureFile] =
    useState<File | null>(null);
  const [phononBandFile, setPhononBandFile] = useState<File | null>(null);
  const [phononDosFile, setPhononDosFile] = useState<File | null>(null);
  const typedPhononReady = Boolean(
    name.trim() &&
      phononStructureFile &&
      phononBandFile &&
      phononDosFile,
  );
  useEffect(() => { if (uploaded) resultRef.current?.focus(); }, [uploaded]);
  const canSubmit = Boolean(name.trim() && (uploadMode === "phonon" ? typedPhononReady : files.length));
  const changeUploadMode = (mode: "files" | "phonon") => {
    if (uploadingRef.current) return;
    setUploadMode(mode);
    setError("");
  };
  const startAnotherUpload = () => {
    setUploaded(null);
    setName("");
    setFiles([]);
    setPhononStructureFile(null);
    setPhononBandFile(null);
    setPhononDosFile(null);
    setError("");
    window.requestAnimationFrame(() => nameRef.current?.focus());
  };
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (uploadingRef.current || uploaded || !canSubmit) return;
    uploadingRef.current = true;
    setBusy(true);
    setError("");
    try {
      const requestedName = name.trim();
      const uploadFiles: UploadDatasetFile[] = uploadMode === "phonon" ? [
        { file: phononStructureFile!, companionGroupId: "phonon_bundle" },
        { file: phononBandFile!, importKind: "phonon_band", contractVersion: PHONON_BAND_SCHEMA_VERSION, companionGroupId: "phonon_bundle" },
        { file: phononDosFile!, importKind: "phonon_dos", contractVersion: PHONON_DOS_SCHEMA_VERSION, companionGroupId: "phonon_bundle" },
      ] : files.map((file) => {
          const normalizedName = file.name
            .toLowerCase()
            .replace(/[\s-]+/gu, "_");
          const importKind =
            normalizedName.includes("phonon") && normalizedName.includes("band")
              ? "phonon_band"
              : normalizedName.includes("phonon") &&
                  normalizedName.includes("dos")
                ? "phonon_dos"
                : undefined;
          return {
            file,
            importKind,
            contractVersion:
              importKind === "phonon_band"
                ? PHONON_BAND_SCHEMA_VERSION
                : importKind === "phonon_dos"
                  ? PHONON_DOS_SCHEMA_VERSION
                  : undefined,
            companionGroupId:
              files.length > 1
                ? importKind
                  ? "phonon_bundle"
                  : "primary_bundle"
                : undefined,
          };
        });
      const result = await uploadDatasetFiles(projectId, requestedName, uploadFiles);
      const datasetId = result.datasetId || result.id;
      setUploaded({ datasetId: typeof datasetId === "string" && datasetId.trim() && (!result.projectId || result.projectId === projectId) ? datasetId : null, name: requestedName, fileCount: uploadFiles.length });
    } catch (reason) {
      const status = typeof reason === "object" && reason !== null && "status" in reason ? Number(reason.status) : 0;
      setError(status === 413 ? "文件超出上传大小限制。请减小文件或分批上传。" : status === 401 || status === 403 ? "当前账户无法上传到此项目。请检查登录状态和项目权限。" : "暂时无法确认上传结果。名称和文件已保留，重试前可先查看项目数据。");
    } finally {
      uploadingRef.current = false;
      setBusy(false);
    }
  }
  const dataHref = "/projects/" + projectId + "/data";
  const canUpload = projectRoleAllows(history?.project.role, "write");
  return (
    <RequireProductAuth>
      <ProductShell projectId={projectId}>
        <section className="document-page upload-page">
          <Link className="back-link" href={dataHref}>
            ← 返回项目数据
          </Link>
          <header className="product-page-heading">
            <h1>上传数据</h1>
            <p>添加材料文件，查看数据并开始研究。</p>
          </header>
          <EmptyOrError state={projectState} error={projectError} onRetry={retryProject} />
          {history && !canUpload ? (
            <div className="product-state">
              <h2>此项目为只读</h2>
              <p>你可以查看已有数据和研究结果，但不能向此项目上传新数据。</p>
              <Link className="product-primary-action" href={dataHref}>
                查看项目数据
              </Link>
            </div>
          ) : null}
          {history && canUpload && uploaded ? (
            <section className="upload-result" aria-labelledby="upload-result-title">
              <h2 id="upload-result-title" ref={resultRef} tabIndex={-1}>文件已上传</h2>
              <p><strong>{uploaded.name}</strong> · {uploaded.fileCount} 个文件</p>
              <p>{uploaded.datasetId ? "可以查看数据与解析情况，或进入研究工作区提问。" : "请在项目数据中检查这次上传记录。"}</p>
              <div className="product-row-actions">
                <Link className="product-primary-action" href={uploaded.datasetId ? `${dataHref}?dataset=${encodeURIComponent(uploaded.datasetId)}` : dataHref}>{uploaded.datasetId ? "查看数据" : "查看项目数据"}</Link>
                {uploaded.datasetId ? <Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/research?dataset=${encodeURIComponent(uploaded.datasetId)}`}>开始研究</Link> : null}
                <button type="button" className="product-secondary-action" onClick={startAnotherUpload}>继续上传</button>
              </div>
            </section>
          ) : history && canUpload ? (
            <form
              className="upload-form"
              aria-label="上传数据"
              onSubmit={(event) => void submit(event)}
            >
              <div className="upload-field">
                <span id="upload-mode-label" className="upload-field-label">上传方式</span>
                <div className="upload-method-switch" role="group" aria-labelledby="upload-mode-label">
                  <button type="button" disabled={busy} aria-pressed={uploadMode === "files"} onClick={() => changeUploadMode("files")}>普通文件</button>
                  <button type="button" disabled={busy} aria-pressed={uploadMode === "phonon"} onClick={() => changeUploadMode("phonon")}>声子组合</button>
                </div>
                <p className="upload-hint">{uploadMode === "files" ? "上传表格、晶体结构、轨迹或压缩包。" : "将同一材料的结构、声子能带和态密度文件一起上传。"}</p>
              </div>
              <div className="upload-field">
                <label htmlFor="dataset-upload-name">数据集名称</label>
                <input ref={nameRef} id="dataset-upload-name" value={name} disabled={busy} onChange={(event) => setName(event.target.value)} placeholder="例如：BaTiO3 稳定性数据" required maxLength={160} />
              </div>
              <fieldset className="upload-source-fields" hidden={uploadMode !== "files"} disabled={busy || uploadMode !== "files"}>
                <legend className="sr-only">普通文件</legend>
                <UploadFilePicker id="dataset-upload-files" label="源文件" files={files} onChange={setFiles} multiple disabled={busy || uploadMode !== "files"} />
                <p className="upload-hint">常用格式：CSV、CIF、POSCAR、XYZ、ZIP。文件内容是否可解析，会在上传后显示。</p>
              </fieldset>
              <fieldset className="upload-source-fields" hidden={uploadMode !== "phonon"} disabled={busy || uploadMode !== "phonon"}>
                <legend className="sr-only">声子组合文件</legend>
                <UploadFilePicker id="phonon-structure-file" label="结构文件" files={phononStructureFile ? [phononStructureFile] : []} onChange={(items) => setPhononStructureFile(items[0] || null)} disabled={busy || uploadMode !== "phonon"} />
                <UploadFilePicker id="phonon-band-file" label="声子能带文件" files={phononBandFile ? [phononBandFile] : []} onChange={(items) => setPhononBandFile(items[0] || null)} accept="application/json,.json" disabled={busy || uploadMode !== "phonon"} />
                <UploadFilePicker id="phonon-dos-file" label="声子态密度文件" files={phononDosFile ? [phononDosFile] : []} onChange={(items) => setPhononDosFile(items[0] || null)} accept="application/json,.json" disabled={busy || uploadMode !== "phonon"} />
                <p className="upload-hint">能带与态密度请选择声子数据 JSON 文件。</p>
              </fieldset>
              {error && (
                <div className="upload-error" role="alert"><p className="product-form-error">{error}</p><Link href={dataHref}>查看项目数据</Link></div>
              )}
              {busy ? <p className="upload-hint" role="status">正在上传文件，请保持此页面打开。</p> : null}
              <div className="product-row-actions">
                <button
                  type="submit"
                  className="product-primary-action"
                  disabled={busy || !canSubmit}
                >
                  {busy ? "正在上传…" : error ? "重试上传" : "上传并解析"}
                </button>
                {!busy ? <Link
                  className="product-secondary-action"
                  href={`/projects/${projectId}/data`}
                >
                  取消
                </Link> : null}
              </div>
            </form>
          ) : null}
        </section>
      </ProductShell>
    </RequireProductAuth>
  );
}

function dataKindLabel(kind: DataKind) {
  return {
    table: "表格",
    structure: "结构",
    trajectory: "轨迹",
    xrd: "XRD",
    electronic: "电子结构",
    phonon: "声子",
    volumetric: "体数据",
    detected: "检测到的内容",
    generic: "通用文件",
  }[kind];
}

function dataStatusLabel(status: string | null | undefined) {
  return (
    (
      {
        ready: "可用于研究",
        profile_ready: "已识别数据",
        processing: "正在解析",
        failed: "解析失败",
        partial: "部分可用",
      } as Record<string, string>
    )[String(status || "").toLowerCase()] || "已识别数据"
  );
}

function selectionKindLabel(kind: string) {
  return (
    (
      {
        DATASET_SAMPLE: "数据样本",
        STRUCTURE_SITE: "结构位点",
        PERIODIC_SITE: "结构位点",
        ELECTRONIC_BAND_STATE: "能带状态",
        ELECTRONIC_DOS_POINT: "态密度点",
        PHONON_Q_POINT: "声子模式",
        PHONON_DOS_POINT: "声子态密度点",
        EXPERIMENTAL_XRD_PEAK: "实验峰",
        XRD_MATCH: "匹配峰",
        TRAJECTORY_ATOM: "轨迹原子",
        TRAJECTORY_FRAME: "轨迹帧",
        ARTIFACT: "科学结果",
      } as Record<string, string>
    )[kind] || "科学对象"
  );
}

function selectionTitle(selection: {
  kind: string;
  qPointId?: string | null;
  branchId?: string | null;
  frequencyPointId?: string | null;
  dosChannelId?: string | null;
  sampleRef: string | null;
  siteId: string | null;
  peakId: string | null;
  matchId: string | null;
  atomId: string | null;
  frameId?: string | null;
}) {
  if (["TRAJECTORY_FRAME", "TRAJECTORY_ATOM"].includes(selection.kind)) return `第 ${Number(selection.frameId?.replace(/^frame:/, "")) + 1} 帧${selection.atomId ? ` · 原子 ${Number(selection.atomId.split(":")[1]) + 1}` : ""}`;
  if (selection.kind === "PHONON_DOS_POINT") return `${selection.dosChannelId === "total" ? "总态密度" : `投影 ${selection.dosChannelId?.replace(/^projection:/, "")}`} · 频率点 ${selection.frequencyPointId?.replace(/^frequency:/, "")}`;
  if (selection.kind === "PHONON_Q_POINT") return `q 点 ${selection.qPointId?.replace(/^q:/, "")}${selection.branchId ? ` · 分支 ${selection.branchId.replace(/^branch:/, "")}` : ""}`;
  return (
    selection.sampleRef ||
    selection.siteId ||
    selection.peakId ||
    selection.matchId ||
    selection.atomId ||
    selectionKindLabel(selection.kind)
  );
}

function ScientificDataView({
  projectId,
  dataset,
  kind,
  onInspect,
  selection,
  requestedResourceId,
  onResourceChange,
  onSelection,
  onAvailabilityChange,
  tableRouteState,
  onTableRouteChange,
}: {
  projectId: string;
  dataset: ProjectHistory["datasets"][number];
  kind: DataKind;
  onInspect: () => void;
  selection: WorkspaceSelectionContext | null;
  requestedResourceId: string | null;
  onResourceChange: (resourceId: string) => void;
  onSelection: (selection: WorkspaceSelectionContext) => void;
  onAvailabilityChange: (
    state: "loading" | "ready" | "empty" | "unavailable",
  ) => void;
  tableRouteState: DataTableViewState;
  onTableRouteChange: (
    changes: DataTableRouteState,
    mode: "push" | "replace",
  ) => void;
}) {
  const [resources, setResources] = useState<DatasetSourceResource[] | null>(
    null,
  );
  const [resourceError, setResourceError] = useState<"FAILED" | "TIMEOUT" | null>(null);
  const [resourceErrorKind, setResourceErrorKind] = useState<
    "TRANSIENT" | "CONFIRMED_MISSING"
  >("TRANSIENT");
  const [loadAttempt, setLoadAttempt] = useState(0);
  const recoveryContainerRef = useRef<HTMLElement | null>(null);
  const retrySourceRead = (event: React.MouseEvent<HTMLButtonElement>) => {
    recoveryContainerRef.current = event.currentTarget.closest<HTMLElement>(".scientific-viewer");
    setLoadAttempt(attempt => attempt + 1);
  };
  const selectionResource = useMemo(() => {
    const primary = selection?.primary;
    if (!resources || !primary || primary.projectId !== projectId || primary.datasetId !== dataset.datasetId) return null;
    const matching = resources.filter((item) => item.datasetId === dataset.datasetId
      && (!primary.objectId || item.objectId === primary.objectId)
      && (!primary.kind.startsWith("ELECTRONIC_") || primary.artifactId === `source:${item.objectId}`)
      && (!primary.kind.startsWith("PHONON_") || primary.phononArtifactId === `source:${item.objectId}`)
      && (primary.kind !== "VOLUMETRIC_FIELD" || primary.artifactId === `source:${item.objectId}:volumetric-dataset`)
      && (!["TRAJECTORY_FRAME", "TRAJECTORY_ATOM"].includes(primary.kind) || primary.artifactId === `source:${item.objectId}`)
      && item.objectHash === selection.sourceScopeHash
      && (item.versionId || item.objectHash || "current") === primary.datasetVersion);
    return matching.length === 1 ? matching[0] : null;
  }, [resources, selection, projectId, dataset.datasetId]);
  const selected = resources && (requestedResourceId !== null
    ? resources.find(item => item.objectId === requestedResourceId)
    : selectionResource || preferredResource(resources, kind));
  const selectionConflict = Boolean(selected && selectionResource && selected.objectId !== selectionResource.objectId);
  useEffect(() => {
    onAvailabilityChange(resources === null ? "loading" : resourceError || selectionConflict || (requestedResourceId !== null && !selected) ? "unavailable" : selected ? "ready" : "empty");
  }, [resources, resourceError, selected, selectionConflict, requestedResourceId, onAvailabilityChange]);
  useEffect(() => {
    if (resources === null || !recoveryContainerRef.current) return;
    const container = recoveryContainerRef.current;
    const frame = window.requestAnimationFrame(() => {
      if (!container.isConnected) return;
      container.querySelector<HTMLElement>('nav[aria-label="数据内容"] button[aria-pressed="true"], [data-source-retry], .source-scientific-viewer > button')?.focus();
      recoveryContainerRef.current = null;
    });
    return () => window.cancelAnimationFrame(frame);
  }, [resources, resourceError, selected]);
  useEffect(() => {
    const controller = new AbortController();
    setResources(null);
    setResourceError(null);
    setResourceErrorKind("TRANSIENT");
    const timer = setTimeout(() => {
      controller.abort();
      setResources([]);
      setResourceError("TIMEOUT");
    }, 10_000);
    void getDatasetSourceResources(dataset.datasetId, controller.signal)
      .then((items) => {
        if (controller.signal.aborted) return;
        if (items.some(item => item.datasetId !== dataset.datasetId || !item.objectId) || new Set(items.map(item => item.objectId)).size !== items.length) throw new Error("SOURCE_RESOURCE_IDENTITY_MISMATCH");
        setResources(items);
      })
      .catch((reason) => {
        if (controller.signal.aborted) return;
        setResources([]);
        setResourceErrorKind(classifySourceLoadFailure(reason));
        setResourceError("FAILED");
      })
      .finally(() => clearTimeout(timer));
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [dataset.datasetId, kind, loadAttempt]);
  if (resources === null)
    return (
      <div className="product-loading" role="status">
        正在加载科学数据…
      </div>
    );
  if (resourceError) {
    const confirmedMissing = resourceErrorKind === "CONFIRMED_MISSING";
    const fallbackTitleId = `science-fallback-title-${dataset.datasetId}-${kind}`.replace(
      /[^a-zA-Z0-9_-]/g,
      "-",
    );
    const uploadHref = `/projects/${encodeURIComponent(projectId)}/datasets/new`;
    return (
      <>
        <div
          className={`science-canvas science-canvas-fallback source-load-failure ${kind}`}
          role="alert"
          aria-labelledby={fallbackTitleId}
        >
          <div className="science-canvas-label">
            <span>{dataKindLabel(kind)}</span>
            <strong id={fallbackTitleId}>
              {confirmedMissing
                ? "原始科学数据当前不可用"
                : resourceError === "TIMEOUT"
                  ? "读取科学数据超时"
                  : "当前科学资源暂时无法读取"}
            </strong>
          </div>
          <p>
            {confirmedMissing
              ? "系统已确认声明位置没有原始科学数据；数据档案、精确来源与解析记录仍然保留，不会用其他版本替代。请重新导入或恢复原始文件。"
              : kind === "table"
                ? "表格数据尚未加载。已读取的数据档案与来源信息仍可查看，请重新加载数据。"
                : "数据档案、精确来源与解析记录仍然保留；科学数据暂时无法读取，请重新加载。"}
          </p>
          <p className="source-load-failure-status" role="status">
            <span>读取状态</span>
            <strong>{confirmedMissing ? "已确认缺失" : "暂时失败，可重试"}</strong>
          </p>
          <div className="source-load-failure-actions">
            <button
              type="button"
              className="product-secondary-action"
              onClick={onInspect}
            >
              查看来源与属性
            </button>
            <button
              type="button"
              className="product-primary-action"
              data-source-retry
              onClick={retrySourceRead}
            >
              {confirmedMissing ? "再次确认来源" : "重新加载数据"}
            </button>
            {confirmedMissing ? (
              <Link className="product-secondary-action" href={uploadHref}>
                重新导入源文件
              </Link>
            ) : null}
          </div>
        </div>
        {kind === "table" && Object.keys(dataset.profile?.semanticRoles || {}).length > 0 ? (
          <details className="data-retained-profile">
            <summary>查看已读取的列描述</summary>
            <TableScientificView
              dataset={dataset}
              onInspect={onInspect}
              initialQuery={tableRouteState.query}
              initialSort={tableRouteState.sort}
              initialSelectedRow={tableRouteState.row}
              onRouteStateChange={onTableRouteChange}
            />
          </details>
        ) : null}
      </>
    );
  }
  const missingResource = requestedResourceId !== null && !selected;
  if (resources.length > 1 || kind === "detected" || missingResource || selectionConflict)
    return (
      <div className="detected-content">
        <div className="detected-content-heading">
          <strong>数据内容</strong>
          <span>{resources.length} 项</span>
        </div>
        <nav aria-label="数据内容">
           {resources.map((resource, index) => (
             <button
               key={resource.objectId}
              className={
                resource.objectId === selected?.objectId ? "selected" : ""
              }
               aria-pressed={resource.objectId === selected?.objectId}
               title={resourceDisplayName(resource, resources, index)}
               onClick={() => { if (resource.objectId !== selected?.objectId || selectionConflict) onResourceChange(resource.objectId); }}
             >
               <strong>{resourceDisplayName(resource, resources, index)}</strong>
             </button>
           ))}
        </nav>
        {missingResource || selectionConflict ? <div className="product-state" role="alert">
          <h2>{selectionConflict ? "链接中的数据内容与选择不一致" : "暂时无法找到这项数据内容"}</h2>
          <p>{selectionConflict ? "请从上方选择要查看的数据内容，旧的数据点选择会随之清除。" : "所选内容不在当前资源列表中。可以重新读取，或从上方选择其他内容。"}</p>
          <button type="button" className="product-secondary-action" data-source-retry onClick={retrySourceRead}>重新读取数据内容</button>
        </div> : selected ? (
          <section className="source-scientific-viewer">
            <LazyScientificSourceViewer
              projectId={projectId}
              resource={selected}
              resources={resources}
              selection={selection}
              onSelection={onSelection}
            />
            <button
              type="button"
              className="product-secondary-action"
              onClick={onInspect}
            >
              查看所选对象详情
            </button>
          </section>
        ) : null}
      </div>
    );
  if (selected)
    return (
      <section className="source-scientific-viewer">
        <LazyScientificSourceViewer
          projectId={projectId}
          resource={selected}
          resources={resources}
          selection={selection}
          onSelection={onSelection}
        />
        <button
          type="button"
          className="product-secondary-action"
          onClick={onInspect}
        >
          查看来源与属性
        </button>
      </section>
    );
  if (kind === "table")
    return (
      <TableScientificView
        dataset={dataset}
        onInspect={onInspect}
        initialQuery={tableRouteState.query}
        initialSort={tableRouteState.sort}
        initialSelectedRow={tableRouteState.row}
        onRouteStateChange={onTableRouteChange}
      />
    );
  const isEmptyDataset =
    Number(dataset.import.fileCount || 0) === 0 &&
    Number(dataset.profile?.objectCount || 0) === 0;
  if (!resources.length && isEmptyDataset)
    return <DatasetOverview dataset={dataset} onInspect={onInspect} />;
  return (
      <div
      className="science-canvas science-canvas-fallback"
      role="region"
      aria-labelledby={`science-fallback-title-${dataset.datasetId}-${kind}`.replace(
        /[^a-zA-Z0-9_-]/g,
        "-",
      )}
    >
      <div className="science-canvas-label">
        <span>{dataKindLabel(kind)}</span>
        <strong
          id={`science-fallback-title-${dataset.datasetId}-${kind}`.replace(
            /[^a-zA-Z0-9_-]/g,
            "-",
          )}
        >
          {isEmptyDataset ? "尚未导入科学对象" : "当前没有可渲染的科学对象"}
        </strong>
      </div>
      {isEmptyDataset ? (
        <p>该数据集尚未接收源文件。请使用本页的“导入数据”操作添加受支持的科学数据。</p>
      ) : (
        <p>
          数据档案和来源信息仍然保留，但当前没有通过 Viewer contract
          验证的资源可供交互查看。
        </p>
      )}
      <button
        type="button"
        className="product-secondary-action"
        onClick={onInspect}
      >
        查看来源与属性
      </button>
    </div>
  );
}

function DatasetOverview({
  dataset,
  onInspect,
}: {
  dataset: ProjectHistory["datasets"][number];
  onInspect: () => void;
}) {
  return (
    <section className="dataset-overview" aria-labelledby="dataset-overview-title">
      <p className="product-kicker">数据集概览</p>
      <h2 id="dataset-overview-title">这个数据集还没有科学对象</h2>
      <p>
        这是一个可继续接收材料数据的来源范围。导入文件后，系统会在这里按科学类型整理
        Scientific Data，再提供对应的查看器和研究入口。
      </p>
      <dl className="dataset-overview-stats">
        <div>
          <dt>源文件</dt>
          <dd>{dataset.import.fileCount || 0}</dd>
        </div>
        <div>
          <dt>已识别对象</dt>
          <dd>{dataset.profile?.objectCount || 0}</dd>
        </div>
        <div>
          <dt>当前状态</dt>
          <dd>{dataStatusLabel(dataset.status)}</dd>
        </div>
      </dl>
      <div className="dataset-overview-next">
        <strong>下一步</strong>
        <span>导入受支持的 CIF、表格、轨迹或其他材料数据。</span>
      </div>
      <button type="button" className="product-secondary-action" onClick={onInspect}>
        查看数据集来源与属性
      </button>
    </section>
  );
}

function preferredResource(
  resources: DatasetSourceResource[],
  kind: DataKind,
): DatasetSourceResource | undefined {
  const types: Record<DataKind, string[]> = {
    table: ["DataFrame"],
    structure: ["Structure", "Atoms"],
    trajectory: ["Trajectory"],
    xrd: ["DataFrame"],
    electronic: ["ElectronicBand", "ElectronicDos"],
    phonon: ["PhononBand", "PhononDos", "PhononEigenvector"],
    volumetric: ["VolumetricData"],
    detected: [],
    generic: [],
  };
  return (
    resources.find((item) => types[kind].includes(item.objectType)) ||
    resources[0]
  );
}

function classifySourceLoadFailure(reason: unknown): "TRANSIENT" | "CONFIRMED_MISSING" {
  if (!reason || typeof reason !== "object") return "TRANSIENT";
  const candidate = reason as { status?: unknown; errorType?: unknown; details?: unknown };
  const errorType = String(candidate.errorType || "");
  const detail = candidate.details && typeof candidate.details === "object"
    ? candidate.details as { errorType?: unknown; code?: unknown }
    : {};
  const detailType = String(detail.errorType || detail.code || "");
  return /(?:SOURCE_MISSING|OBJECT_STORE_SOURCE_MISSING|SOURCE_RESOURCE_MISSING|PAYLOAD_MISSING)/i.test(`${errorType} ${detailType}`)
    ? "CONFIRMED_MISSING"
    : "TRANSIENT";
}

function scientificObjectTypeLabel(objectType: string) {
  return (
    (
      {
        "materials.dataset": "材料数据表",
        "materials.table": "科研材料表",
        "structure.crystal": "晶体结构",
        "trajectory.atomic": "原子轨迹",
        "diffraction.xrd.experimental": "实验 XRD",
        "diffraction.xrd.theoretical": "理论 XRD",
        "electronic.band_structure": "电子能带",
        "electronic.dos": "电子态密度",
        "phonon.band_structure": "声子能带",
        "phonon.dos": "声子态密度",
        "volumetric.charge_density": "电荷密度",
      } as Record<string, string>
    )[objectType] || "科学数据"
  );
}

function resourceDisplayName(
  resource: DatasetSourceResource,
  resources: DatasetSourceResource[],
  index: number,
) {
  const label = sourceTypeLabel(resource.objectType);
  const sameTypeCount = resources.filter(
    (item) => item.objectType === resource.objectType,
  ).length;
  return sameTypeCount > 1 ? `${label} · 第 ${index + 1} 项` : label;
}

export type DataTableViewState = Readonly<{
  query: string;
  sort: "asc" | "desc";
  row: string;
}>;

export type DataTableRouteState = Partial<
  DataTableViewState & { selection: string; resource: string }
>;

export function resolveDataPageSelection(
  token: string,
  projectId: string,
  datasetId?: string,
): WorkspaceSelectionContext | null {
  if (!token) return null;
  try {
    const restored = decodeWorkspaceSelectionUrl(token);
    const primary = restored.primary;
    if (
      !primary ||
      primary.projectId !== projectId ||
      (primary.datasetId && datasetId && primary.datasetId !== datasetId)
    ) {
      return null;
    }
    return restored;
  } catch {
    return null;
  }
}

export function dataTableViewHref(
  currentHref: string,
  changes: DataTableRouteState,
): string {
  const url = new URL(currentHref, "http://localhost");
  if (changes.resource !== undefined) {
    if (changes.resource) url.searchParams.set("resource", changes.resource);
    else url.searchParams.delete("resource");
  }
  if (changes.query !== undefined) {
    if (changes.query) url.searchParams.set("tableQuery", changes.query);
    else url.searchParams.delete("tableQuery");
  }
  if (changes.sort !== undefined) {
    if (changes.sort === "desc") url.searchParams.set("tableSort", "desc");
    else url.searchParams.delete("tableSort");
  }
  if (changes.row !== undefined) {
    if (changes.row) url.searchParams.set("tableRow", changes.row);
    else url.searchParams.delete("tableRow");
  }
  if (changes.selection !== undefined) {
    if (changes.selection) url.searchParams.set("selection", changes.selection);
    else url.searchParams.delete("selection");
  }
  return `${url.pathname}${url.search}${url.hash}`;
}

export function TableScientificView({
  dataset,
  onInspect,
  initialQuery = "",
  initialSort = "asc",
  initialSelectedRow = "",
  onRouteStateChange,
}: {
  dataset: ProjectHistory["datasets"][number];
  onInspect: () => void;
  initialQuery?: string;
  initialSort?: "asc" | "desc";
  initialSelectedRow?: string;
  onRouteStateChange?: (
    changes: DataTableRouteState,
    mode: "push" | "replace",
  ) => void;
}) {
  const [query, setQuery] = useState(initialQuery);
  const [sortAsc, setSortAsc] = useState(initialSort !== "desc");
  const [selected, setSelected] = useState<string | null>(
    initialSelectedRow || null,
  );
  const [visible, setVisible] = useState({
    property: true,
    semantic: true,
    count: true,
    unit: true,
  });
  const rows = useMemo(
    () =>
      Object.entries(dataset.profile?.semanticRoles || {})
        .map(([role, count]) => ({
          id: role,
          property: role,
          semantic: semanticRoleLabel(role),
          count: Number(count) || 0,
          unit: "未声明",
        }))
        .filter(
          (row) =>
            !query ||
            Object.values(row).some((value) =>
              String(value).toLowerCase().includes(query.toLowerCase()),
            ),
        )
        .sort((a, b) =>
          sortAsc
            ? a.property.localeCompare(b.property)
            : b.property.localeCompare(a.property),
        ),
    [dataset.profile?.semanticRoles, query, sortAsc],
  );
  useEffect(() => setQuery(initialQuery), [initialQuery]);
  useEffect(() => setSortAsc(initialSort !== "desc"), [initialSort]);
  useEffect(
    () => setSelected(initialSelectedRow || null),
    [initialSelectedRow],
  );
  const choose = (id: string) => {
    setSelected(id);
    onRouteStateChange?.({ row: id }, "push");
    onInspect();
  };
  return (
    <div className="table-view">
      <div className="table-tools">
        <input
          type="search"
          aria-label="搜索表格"
          placeholder="搜索属性…"
          value={query}
          onChange={(event) => {
            const next = event.target.value;
            setQuery(next);
            onRouteStateChange?.({ query: next }, "replace");
          }}
        />
        <button
          type="button"
          onClick={() =>
            setSortAsc((value) => {
              const next = !value;
              onRouteStateChange?.(
                { sort: next ? "asc" : "desc" },
                "push",
              );
              return next;
            })
          }
          aria-label="切换排序"
        >
          按属性 {sortAsc ? "↑" : "↓"}
        </button>
        <details>
          <summary>列</summary>
          <div className="column-menu">
            {Object.entries({
              property: "属性",
              semantic: "语义角色",
              count: "记录",
              unit: "单位",
            }).map(([key, label]) => (
              <label key={key}>
                <input
                  aria-label={`显示${label}列`}
                  type="checkbox"
                  checked={visible[key as keyof typeof visible]}
                  onChange={() =>
                    setVisible((value) => ({
                      ...value,
                      [key]: !value[key as keyof typeof value],
                    }))
                  }
                />
                {label}
              </label>
            ))}
          </div>
        </details>
      </div>
      <p className="table-route-state-note" role="status">
        当前查询、排序与所选行会保存在此页面地址中；复制地址可恢复同一数据视图。
      </p>
      <p className="table-scroll-hint" role="note">
        <span aria-hidden="true">↔</span>
        <span>左右滑动查看完整列；选择一行可查看对应科学属性。</span>
      </p>
      <div className="table-scroll" role="region" aria-label="科学属性表，可横向滚动查看完整列" tabIndex={0}>
        <table aria-label={`${productProjectName(dataset.name)}科学属性`}>
          <caption className="sr-only">
            {productProjectName(dataset.name)}
            的科学属性、语义角色、记录数量和单位
          </caption>
          <thead>
            <tr>
              {visible.property && <th scope="col">属性</th>}
              {visible.semantic && <th scope="col">语义角色</th>}
              {visible.count && <th scope="col">可用记录</th>}
              {visible.unit && <th scope="col">单位</th>}
            </tr>
          </thead>
          <tbody>
            {rows.length ? (
              rows.map((row) => (
                <tr
                  key={row.id}
                  tabIndex={0}
                  aria-selected={selected === row.id}
                  className={selected === row.id ? "selected" : ""}
                  onClick={() => choose(row.id)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      choose(row.id);
                    }
                  }}
                >
                  {visible.property && <td>{row.property}</td>}
                  {visible.semantic && <td>{row.semantic}</td>}
                  {visible.count && <td>{row.count}</td>}
                  {visible.unit && <td>{row.unit}</td>}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4}>当前数据未提供可浏览的列语义。</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function semanticRoleLabel(role: string) {
  const labels: Record<string, string> = {
    band_gap: "带隙",
    formation_energy: "形成能",
    density: "密度",
    material_property: "材料性质",
    formula: "化学式",
    target: "分析目标",
    identifier: "样本标识",
  };
  return labels[role] || role.replaceAll("_", " ");
}
