"use client";

import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import {
  bulkDatasetAction,
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
  bulkUpdateScientificObjects,
  listScientificObjects,
  getScientificObjectDependencyImpact,
  updateScientificObject,
  type ScientificObjectDependencyImpact,
  type ScientificObjectSummary,
} from "../../app/lib/scientific-viewer-api";
import { RouteLoading } from "../../shared/ui/RouteLoading";
import { projectRoleAllows } from "../../app/lib/project-permissions";
import { DependencyImpactEntry, EmptyOrError, productProjectName, sourceTypeLabel, useProject } from "../projects/ProductPages";
import type { LoadState } from "../projects/ProductPages";

type ProjectDataset = ProjectHistory["datasets"][number];

function ScientificObjectTrashDialog({
  item,
  impact,
  busy,
  error,
  onClose,
  onConfirm,
}: {
  item: ScientificObjectSummary;
  impact: ScientificObjectDependencyImpact | null;
  busy: boolean;
  error: string;
  onClose: () => void;
  onConfirm: () => void;
}) {
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
            disabled={busy}
            onClick={onConfirm}
          >
            {busy ? "正在移动…" : "移入回收站"}
          </button>
        </>
      }
    >
      <div className="product-form-grid danger-zone">
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
            <p>受保护的科学 provenance、版本和历史研究仍可访问。</p>
          </div>
        ) : (
          <p role="status">正在检查依赖影响…</p>
        )}
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
  impacts,
  busy,
  error,
  onClose,
  onConfirm,
}: {
  items: ScientificObjectSummary[];
  impacts: ScientificObjectDependencyImpact[] | null;
  busy: boolean;
  error: string;
  onClose: () => void;
  onConfirm: () => void;
}) {
  const dependencyTotals = new Map<string, { label: string; count: number }>();
  for (const impact of impacts || []) {
    for (const dependency of impact.dependencies) {
      const current = dependencyTotals.get(dependency.kind);
      dependencyTotals.set(dependency.kind, {
        label: dependency.label,
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
            disabled={busy || !impacts || impacts.length !== items.length}
            onClick={onConfirm}
          >
            {busy ? "正在移动…" : "确认移入回收站"}
          </button>
        </>
      }
    >
      <div className="product-form-grid danger-zone">
        <p>
          已选择 <strong>{items.length}</strong> 个对象，服务器报告共{" "}
          <strong>{totalDependencies}</strong> 项受保护依赖。
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
        {impacts ? (
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
              <p>未发现已持久化的结果依赖。</p>
            )}
            <p>对象会从新的研究选择中移除；历史研究和 exact source provenance 仍可访问。</p>
          </div>
        ) : (
          <p role="status">正在检查 {items.length} 个对象的依赖影响…</p>
        )}
        {error ? <p className="product-form-error" role="alert">{error}</p> : null}
      </div>
    </ProductModal>
  );
}

function DatasetBulkTrashDialog({
  items,
  impacts,
  busy,
  error,
  onClose,
  onConfirm,
}: {
  items: ProjectDataset[];
  impacts: DependencyImpact[] | null;
  busy: boolean;
  error: string;
  onClose: () => void;
  onConfirm: () => void;
}) {
  const dependencyTotals = new Map<string, { label: string; count: number }>();
  for (const impact of impacts || []) {
    for (const dependency of impact.dependencies) {
      const current = dependencyTotals.get(dependency.kind);
      dependencyTotals.set(dependency.kind, {
        label: dependency.label,
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
            disabled={busy || !impacts || impacts.length !== items.length}
            onClick={onConfirm}
          >
            {busy ? "正在移动…" : "确认移入回收站"}
          </button>
        </>
      }
    >
      <div className="product-form-grid danger-zone">
        <p>
          已选择 <strong>{items.length}</strong> 个数据集，服务器报告共{" "}
          <strong>{totalDependencies}</strong> 项受保护依赖。
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
        {impacts ? (
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
              <p>未发现已持久化的结果依赖。</p>
            )}
            <p>数据集会从新的研究选择中移除；历史研究和 exact source provenance 仍可访问。</p>
          </div>
        ) : (
          <p role="status">正在检查 {items.length} 个数据集的依赖影响…</p>
        )}
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
}: {
  dataset: ProjectDataset;
  mode: "edit" | "trash" | "delete";
  onClose: () => void;
  onUpdated: (changes: { name: string; status: string }) => void;
  onDeleted: (datasetId: string) => void;
}) {
  const [name, setName] = useState(dataset.name);
  const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [impact, setImpact] = useState<DependencyImpact | null>(null);
  useEffect(() => {
    if (mode !== "delete" && mode !== "trash") return;
    void getDatasetDependencyImpact(dataset.datasetId)
      .then(setImpact)
      .catch(() => setImpact(null));
  }, [dataset.datasetId, mode]);
  async function save() {
    if (!name.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      const result = await updateDataset(dataset.datasetId, {
        name: name.trim(),
      });
      onUpdated({
        name: result.name || name.trim(),
        status: result.status || dataset.status,
      });
      onClose();
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "数据集更新失败，请重试。",
      );
    } finally {
      setBusy(false);
    }
  }
  async function remove() {
    if (confirmation !== dataset.name || busy) return;
    setBusy(true);
    setError("");
    try {
      await deleteEmptyDataset(dataset.datasetId);
      onDeleted(dataset.datasetId);
      onClose();
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "数据集包含源文件或研究记录，请改为归档。",
      );
    } finally {
      setBusy(false);
    }
  }
  async function trash() {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const result = await updateDataset(dataset.datasetId, {
        lifecycle: "TRASHED",
      });
      onUpdated({
        name: result.name || dataset.name,
        status: result.status || "trashed",
      });
      onClose();
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "数据集暂时无法移入回收站。",
      );
    } finally {
      setBusy(false);
    }
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
              disabled={busy}
              onClick={() => void trash()}
            >
              {busy ? "正在移动…" : "移入回收站"}
            </button>
          </>
        }
      >
        <div className="product-form-grid danger-zone">
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
              <p>受保护的科学 provenance 不会被删除。</p>
            </div>
          ) : (
            <p role="status">正在检查依赖影响…</p>
          )}
          {error ? (
            <p className="product-form-error" role="alert">
              {error}
            </p>
          ) : null}
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
              disabled={busy || confirmation !== dataset.name}
              onClick={() => void remove()}
            >
              {busy ? "正在删除…" : "永久删除"}
            </button>
          </>
        }
      >
        <div className="product-form-grid danger-zone">
          <p>
            输入数据集名称 <strong>{dataset.name}</strong> 以确认。
          </p>
          {impact && impact.dependencyCount > 0 ? (
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
          {error ? (
            <p className="product-form-error" role="alert">
              {error}
            </p>
          ) : null}
        </div>
      </ProductModal>
    );
  return (
    <ProductModal
      eyebrow="数据管理"
      title="重命名数据集"
      description="名称会同步到 Data Navigator、研究数据范围和报告来源。"
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
            disabled={busy || !name.trim()}
            onClick={() => void save()}
          >
            {busy ? "正在保存…" : "保存更改"}
          </button>
        </>
      }
    >
      <div className="product-form-grid">
        <label htmlFor="edit-dataset-name">数据集名称</label>
        <input
          id="edit-dataset-name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              void save();
            }
          }}
        />
        {error ? (
          <p className="product-form-error" role="alert">
            {error}
          </p>
        ) : null}
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
  if (queryDatasetId && visibleDatasetIds.includes(queryDatasetId)) {
    return queryDatasetId;
  }
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
  const { history, setHistory, state, error, retry } = useProject(projectId);
  const [selectedId, setSelectedId] = useState("");
  const [statusFilter, setStatusFilter] = useState<
    "active" | "archived" | "trashed"
  >("active");
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
  const [mutationError, setMutationError] = useState("");
  const [busy, setBusy] = useState(false);
  const [inspector, setInspector] = useState(false);
  const [mobileNavigatorCollapsed, setMobileNavigatorCollapsed] = useState(false);
  const [scientificSelection, setScientificSelection] =
    useState<WorkspaceSelectionContext | null>(null);
  const [selectedSourceAvailability, setSelectedSourceAvailability] = useState<
    "loading" | "ready" | "empty" | "unavailable"
  >("loading");
  const [scientificObjects, setScientificObjects] = useState<
    ScientificObjectSummary[]
  >([]);
  const [scientificObjectTrashTarget, setScientificObjectTrashTarget] =
    useState<ScientificObjectSummary | null>(null);
  const [scientificObjectBulkTrashTargets, setScientificObjectBulkTrashTargets] =
    useState<ScientificObjectSummary[] | null>(null);
  const [scientificObjectBulkTrashImpacts, setScientificObjectBulkTrashImpacts] =
    useState<ScientificObjectDependencyImpact[] | null>(null);
  const [datasetBulkTrashTargets, setDatasetBulkTrashTargets] =
    useState<ProjectDataset[] | null>(null);
  const [datasetBulkTrashImpacts, setDatasetBulkTrashImpacts] =
    useState<DependencyImpact[] | null>(null);
  const [scientificObjectImpact, setScientificObjectImpact] =
    useState<ScientificObjectDependencyImpact | null>(null);
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
    const controller = new AbortController();
    void listScientificObjects(
      projectId,
      controller.signal,
      queryObjectId
        ? undefined
        : statusFilter === "archived"
          ? "ARCHIVED"
          : statusFilter === "trashed"
            ? "TRASHED"
            : "ACTIVE",
    )
      .then((response) => setScientificObjects(response.items))
      .catch(() => setScientificObjects([]));
    return () => controller.abort();
  }, [queryObjectId, projectId, statusFilter]);
  useEffect(() => {
    if (!scientificObjectTrashTarget) {
      setScientificObjectImpact(null);
      return;
    }
    let active = true;
    setScientificObjectImpact(null);
    void getScientificObjectDependencyImpact(scientificObjectTrashTarget.id)
      .then((preview) => {
        if (active) setScientificObjectImpact(preview);
      })
      .catch(() => {
        if (active) setScientificObjectImpact(null);
      });
    return () => {
      active = false;
    };
  }, [scientificObjectTrashTarget]);
  useEffect(() => {
    if (!scientificObjectBulkTrashTargets) {
      setScientificObjectBulkTrashImpacts(null);
      return;
    }
    let active = true;
    setScientificObjectBulkTrashImpacts(null);
    void Promise.all(
      scientificObjectBulkTrashTargets.map((item) =>
        getScientificObjectDependencyImpact(item.id),
      ),
    )
      .then((impacts) => {
        if (active) setScientificObjectBulkTrashImpacts(impacts);
      })
      .catch(() => {
        if (active) {
          setScientificObjectBulkTrashImpacts(null);
          setMutationError("批量对象的依赖影响暂时无法读取，未执行回收站操作。");
        }
      });
    return () => {
      active = false;
    };
  }, [scientificObjectBulkTrashTargets]);
  useEffect(() => {
    if (!datasetBulkTrashTargets) {
      setDatasetBulkTrashImpacts(null);
      return;
    }
    let active = true;
    setDatasetBulkTrashImpacts(null);
    void Promise.all(
      datasetBulkTrashTargets.map((item) =>
        getDatasetDependencyImpact(item.datasetId),
      ),
    )
      .then((impacts) => {
        if (active) setDatasetBulkTrashImpacts(impacts);
      })
      .catch(() => {
        if (active) {
          setDatasetBulkTrashImpacts(null);
          setMutationError("批量数据集的依赖影响暂时无法读取，未执行回收站操作。");
        }
      });
    return () => {
      active = false;
    };
  }, [datasetBulkTrashTargets]);
  useEffect(() => {
    if (typeof window.matchMedia !== "function") return;
    const media = window.matchMedia("(max-width: 720px)");
    const sync = () => setMobileNavigatorCollapsed(media.matches);
    sync();
    media.addEventListener("change", sync);
    return () => media.removeEventListener("change", sync);
  }, []);
  useEffect(() => {
    const nextSelection = resolveDatasetSelection(
      queryDatasetId,
      selectedId,
      visibleDatasets.map((item) => item.datasetId),
    );
    if (nextSelection !== selectedId) setSelectedId(nextSelection);
  }, [queryDatasetId, selectedId, visibleDatasets]);
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
  const selected = visibleDatasets.find(
    (item) => item.datasetId === selectedId,
  );
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
  const selectedScientificObject = scientificObjects.find(
    (item) => item.id === queryObjectId,
  );
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
  const allVisibleObjectsSelected =
    scientificObjects.length > 0 &&
    scientificObjects.every((item) => selectedScientificObjectIds.has(item.id));
  const handleSelection = (selection: WorkspaceSelectionContext) => {
    setScientificSelection(selection);
    try {
      const token = encodeWorkspaceSelectionUrl(selection);
      const next = dataTableViewHref(window.location.href, {
        selection: token,
      });
      window.history.pushState(
        { ...(window.history.state || {}), scientificSelection: true },
        "",
        next,
      );
    } catch {
      // Keep the in-tab selection usable. Only validated, bounded exact
      // selections may become shareable URL state.
    }
    openInspector();
  };
  const updateTableViewRoute = (
    changes: DataTableRouteState,
    mode: "push" | "replace",
  ) => {
    const next = dataTableViewHref(window.location.href, changes);
    window.history[mode === "push" ? "pushState" : "replaceState"](
      { ...(window.history.state || {}), dataTableView: true },
      "",
      next,
    );
  };
  async function setScientificObjectLifecycle(
    item: ScientificObjectSummary,
    lifecycle: "ACTIVE" | "ARCHIVED" | "TRASHED",
  ): Promise<boolean> {
    if (busy) return false;
    setBusy(true);
    setMutationError("");
    try {
      const updated = await updateScientificObject(
        item.id,
        lifecycle === "TRASHED"
          ? { lifecycle }
          : { archived: lifecycle === "ARCHIVED" },
      );
      setScientificObjects((current) => {
        const shouldRemove = statusFilter !== lifecycle.toLowerCase();
        return shouldRemove
          ? current.filter((candidate) => candidate.id !== item.id)
          : current.map((candidate) =>
              candidate.id === item.id
                ? { ...candidate, ...updated }
                : candidate,
            );
      });
      return true;
    } catch (reason) {
      setMutationError(
        reason instanceof Error ? reason.message : "科研对象状态更新失败。",
      );
      return false;
    } finally {
      setBusy(false);
    }
  }
  async function applyScientificObjectBatch(
    lifecycle: "ACTIVE" | "ARCHIVED" | "TRASHED",
  ): Promise<boolean> {
    if (!selectedScientificObjectIds.size || busy) return false;
    setBusy(true);
    setMutationError("");
    try {
      await bulkUpdateScientificObjects(
        projectId,
        Array.from(selectedScientificObjectIds),
        lifecycle,
      );
      setScientificObjects((current) =>
        current.filter((item) => !selectedScientificObjectIds.has(item.id)),
      );
      setSelectedScientificObjectIds(new Set());
      return true;
    } catch (reason) {
      setMutationError(
        reason instanceof Error ? reason.message : "批量科研对象操作失败。",
      );
      return false;
    } finally {
      setBusy(false);
    }
  }
  function requestScientificObjectBulkTrash() {
    if (!selectedScientificObjectIds.size || busy) return;
    const targets = scientificObjects.filter((item) =>
      selectedScientificObjectIds.has(item.id),
    );
    if (!targets.length) return;
    setMutationError("");
    setScientificObjectBulkTrashTargets(targets);
  }
  function confirmScientificObjectBulkTrash() {
    if (
      !scientificObjectBulkTrashTargets ||
      !scientificObjectBulkTrashImpacts ||
      scientificObjectBulkTrashImpacts.length !== scientificObjectBulkTrashTargets.length
    ) {
      return;
    }
    void applyScientificObjectBatch("TRASHED").then((success) => {
      if (success) {
        setScientificObjectBulkTrashTargets(null);
        setScientificObjectBulkTrashImpacts(null);
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
    setBusy(true);
    setMutationError("");
    try {
      const result = await updateDataset(dataset.datasetId, { archived });
      updateLocalDataset(dataset.datasetId, {
        name: result.name,
        status: result.status,
      });
    } catch (reason) {
      setMutationError(
        reason instanceof Error ? reason.message : "数据集状态更新失败。",
      );
    } finally {
      setBusy(false);
    }
  }
  async function restoreDataset(dataset: ProjectDataset) {
    setBusy(true);
    setMutationError("");
    try {
      const result = await updateDataset(dataset.datasetId, {
        archived: false,
      });
      updateLocalDataset(dataset.datasetId, {
        name: result.name,
        status: result.status,
      });
    } catch (reason) {
      setMutationError(
        reason instanceof Error ? reason.message : "数据集恢复失败。",
      );
    } finally {
      setBusy(false);
    }
  }
  async function applyDatasetBatch(
    action: "archive" | "trash" | "restore",
  ): Promise<boolean> {
    if (!selectedDatasetIds.size || busy) return false;
    setBusy(true);
    setMutationError("");
    try {
      const ids = Array.from(selectedDatasetIds);
      await bulkDatasetAction(ids, action);
      setHistory(await getProjectHistory(projectId));
      setSelectedDatasetIds(new Set());
      setSelectionMode(false);
      return true;
    } catch (reason) {
      setMutationError(
        reason instanceof Error ? reason.message : "批量数据操作失败。",
      );
      return false;
    } finally {
      setBusy(false);
    }
  }
  function requestDatasetBulkTrash() {
    if (!selectedDatasetIds.size || busy) return;
    const targets = (history?.datasets || []).filter((item) =>
      selectedDatasetIds.has(item.datasetId),
    );
    if (!targets.length) return;
    setMutationError("");
    setDatasetBulkTrashTargets(targets);
  }
  function confirmDatasetBulkTrash() {
    if (
      !datasetBulkTrashTargets ||
      !datasetBulkTrashImpacts ||
      datasetBulkTrashImpacts.length !== datasetBulkTrashTargets.length
    ) {
      return;
    }
    void applyDatasetBatch("trash").then((success) => {
      if (success) {
        setDatasetBulkTrashTargets(null);
        setDatasetBulkTrashImpacts(null);
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
    if (!scientificObjectTrashTarget) return;
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
            impact={scientificObjectImpact}
            busy={busy}
            error={mutationError}
            onClose={() => setScientificObjectTrashTarget(null)}
            onConfirm={confirmScientificObjectTrash}
          />
        ) : null}
        {scientificObjectBulkTrashTargets ? (
          <ScientificObjectBulkTrashDialog
            items={scientificObjectBulkTrashTargets}
            impacts={scientificObjectBulkTrashImpacts}
            busy={busy}
            error={mutationError}
            onClose={() => {
              if (!busy) {
                setScientificObjectBulkTrashTargets(null);
                setScientificObjectBulkTrashImpacts(null);
                setMutationError("");
              }
            }}
            onConfirm={confirmScientificObjectBulkTrash}
          />
        ) : null}
        {datasetBulkTrashTargets ? (
          <DatasetBulkTrashDialog
            items={datasetBulkTrashTargets}
            impacts={datasetBulkTrashImpacts}
            busy={busy}
            error={mutationError}
            onClose={() => {
              if (!busy) {
                setDatasetBulkTrashTargets(null);
                setDatasetBulkTrashImpacts(null);
                setMutationError("");
              }
            }}
            onConfirm={confirmDatasetBulkTrash}
          />
        ) : null}
        <section className="data-workbench">
          <EmptyOrError state={state} error={error} onRetry={retry} />
          {history && (
            <>
              <aside className="data-navigator">
                <header>
                  <div className="data-navigator-heading">
                    <div>
                      <p className="product-kicker">项目数据</p>
                      <h1>{productProjectName(history.project.name)}</h1>
                    </div>
                    <button
                      type="button"
                      className="data-navigator-toggle"
                      aria-expanded={!mobileNavigatorCollapsed}
                      aria-controls="data-navigator-content"
                      onClick={() =>
                        setMobileNavigatorCollapsed((collapsed) => !collapsed)
                      }
                    >
                      {mobileNavigatorCollapsed ? "显示数据" : "收起数据"}
                    </button>
                  </div>
                  <div className="data-navigator-controls">
                    <div
                      className="segmented-control"
                      role="group"
                      aria-label="数据集状态"
                    >
                      <button
                        type="button"
                        aria-pressed={statusFilter === "active"}
                        onClick={() => setStatusFilter("active")}
                      >
                        当前
                      </button>
                      <button
                        type="button"
                        aria-pressed={statusFilter === "archived"}
                        onClick={() => setStatusFilter("archived")}
                      >
                        已归档
                      </button>
                      <button
                        type="button"
                        aria-pressed={statusFilter === "trashed"}
                        onClick={() => setStatusFilter("trashed")}
                      >
                        回收站
                      </button>
                    </div>
                    {canWriteProject ? (
                      <button
                        type="button"
                        className="product-icon-action"
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
                  </div>
                </header>
                <div
                  id="data-navigator-content"
                  className="data-navigator-content"
                  data-mobile-collapsed={mobileNavigatorCollapsed}
                >
                <section
                  className="data-authority-legend"
                  aria-labelledby="data-authority-legend-title"
                >
                  <p className="product-kicker">阅读提示</p>
                  <h2 id="data-authority-legend-title">来源数据与科学身份</h2>
                  <p className="data-authority-legend-intro">
                    左侧按两种层级组织数据；查看器和研究结果始终回链到精确对象版本。
                  </p>
                  <div className="data-authority-legend-items">
                    <div>
                      <span className="data-authority-legend-token">Dataset</span>
                      <strong>来源范围</strong>
                      <small>管理导入文件、记录与查询，不代表不可变科学状态。</small>
                    </div>
                    <div>
                      <span className="data-authority-legend-token">Scientific Object</span>
                      <strong>科研对象 / 版本</strong>
                      <small>保存解析后的科学身份；打开时不会按名称替换版本。</small>
                    </div>
                  </div>
                </section>
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
                      <button
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
                      </button>
                      {scientificObjects.length ? (
                        <button
                          type="button"
                          className="data-batch-select-all"
                          disabled={busy}
                          onClick={() =>
                            setSelectedScientificObjectIds(
                              allVisibleObjectsSelected
                                ? new Set()
                                : new Set(
                                    scientificObjects.map((item) => item.id),
                                  ),
                            )
                          }
                        >
                          {allVisibleObjectsSelected ? "清空对象" : "全选对象"}
                        </button>
                      ) : null}
                    </div>
                    <div className="data-batch-selection-actions">
                      {statusFilter === "trashed" ? (
                        <button
                          type="button"
                          disabled={!selectedDatasetIds.size || busy}
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
                            disabled={!selectedDatasetIds.size || busy}
                            onClick={requestDatasetBulkTrash}
                          >
                            移入回收站
                          </button>
                        </>
                      )}
                    </div>
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
                        disabled={busy}
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
                          disabled={busy}
                          onClick={() =>
                            void applyScientificObjectBatch("ARCHIVED")
                          }
                        >
                          归档科研对象
                        </button>
                        <button
                          type="button"
                          className="product-danger-action"
                          disabled={busy}
                          onClick={requestScientificObjectBulkTrash}
                        >
                          移入回收站
                        </button>
                      </>
                    )}
                  </div>
                ) : null}
                {mutationError ? (
                  <p
                    className="product-form-error data-management-error"
                    role="alert"
                  >
                    {mutationError}
                  </p>
                ) : null}
                <div className="data-navigator-section-heading">
                  <div>
                    <p className="product-kicker">来源范围</p>
                    <strong>数据集</strong>
                  </div>
                  <span>{visibleDatasets.length} 个</span>
                </div>
                <div className="data-tree managed-data-tree">
                  {visibleDatasets.map((dataset) => (
                    <ManagedObjectRow
                      key={dataset.datasetId}
                      href={`/projects/${projectId}/data?dataset=${dataset.datasetId}`}
                      title={productProjectName(dataset.name)}
                      description={`${dataset.import.fileCount} 个文件 · ${dataKindLabel(inferDataKind(dataset))}`}
                      trailing={
                        dataset.datasetId === selected?.datasetId &&
                        !selectedScientificObject
                          ? "正在查看"
                          : dataset.status === "trashed"
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
                        !selectedScientificObject &&
                        dataset.datasetId === selected?.datasetId
                      }
                      onSelectedChange={(checked) =>
                        toggleDatasetSelected(dataset.datasetId, checked)
                      }
                    />
                  ))}
                </div>
                {selected && scientificObjects.length ? (
                  <section
                    className="data-authority-map"
                    aria-labelledby="data-authority-map-title"
                  >
                    <p className="product-kicker">数据权威层级</p>
                    <h2 id="data-authority-map-title">
                      来源 Dataset → 科研对象 → 不可变版本
                    </h2>
                    <ol>
                      <li>
                        <span>来源 Dataset</span>
                        <strong>{productProjectName(selected.name)}</strong>
                        <small>{selected.import.fileCount} 个源文件</small>
                      </li>
                      <li>
                        <span>项目科研对象</span>
                        <strong>{scientificObjects.length} 个</strong>
                        <small>由解析与科学身份流程管理</small>
                      </li>
                      <li>
                        <span>当前不可变版本</span>
                        <strong>
                          {
                            scientificObjects.filter(
                              (item) => item.current_version_id,
                            ).length
                          }{" "}
                          个已绑定
                        </strong>
                        <small>选择下方对象查看精确版本</small>
                      </li>
                    </ol>
                    <p>
                      Dataset 负责来源组织；科研对象及其版本是科学权威。
                      重命名或归档 Dataset 不会改写不可变科学版本。
                    </p>
                    <details>
                      <summary>如何核对一一对应关系</summary>
                      <p>
                        打开下方科研对象后，以查看器显示的精确对象、版本与来源绑定为准；
                        本页不会按名称猜测或替换版本。
                      </p>
                    </details>
                  </section>
                ) : null}
                {scientificObjects.length ? (
                  <section
                    className="scientific-object-list"
                    aria-labelledby="scientific-object-list-title"
                  >
                    <div className="data-navigator-section-heading scientific-object-section-heading">
                      <div>
                        <p className="product-kicker">解析后的科学身份</p>
                        <h2 id="scientific-object-list-title">科研对象</h2>
                      </div>
                      <span>{scientificObjects.length} 个</span>
                    </div>
                    <p className="data-navigator-section-hint">
                      选择对象后查看其精确不可变版本；它不是 Dataset 的替代入口。
                    </p>
                    <div className="managed-scientific-object-list">
                      {scientificObjects.map((item) =>
                        item.current_version_id ? (
                          <ManagedObjectRow
                            key={item.id}
                            href={`/projects/${projectId}/data?object=${encodeURIComponent(item.id)}&version=${encodeURIComponent(item.current_version_id)}`}
                            title={item.display_name}
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
                            onSelectedChange={(checked) =>
                              toggleScientificObjectSelected(item.id, checked)
                            }
                          />
                        ) : null,
                      )}
                    </div>
                  </section>
                ) : null}
                {visibleDatasets.length === 0 &&
                scientificObjects.length === 0 ? (
                  <div className="data-navigator-empty">
                    <strong>
                      {statusFilter === "archived"
                        ? "没有已归档数据"
                        : statusFilter === "trashed"
                          ? "回收站为空"
                          : "还没有项目数据"}
                    </strong>
                    <p>
                      {statusFilter === "archived"
                        ? "归档后的数据会显示在这里。"
                        : statusFilter === "trashed"
                          ? "移入回收站的数据集可在这里检查依赖并恢复。"
                          : "上传后将按文件、科学对象和组合视图组织。"}
                    </p>
                  </div>
                ) : null}
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
              <section className="scientific-viewer">
                {objectRouteMissingVersion ? (
                  <div className="product-state" role="alert">
                    <p className="product-kicker">精确科学来源</p>
                    <h2>需要指定科研对象版本</h2>
                    <p>
                      此链接只指定了科研对象，没有指定不可变版本。为避免静默替换为最新版本，
                      请从左侧科研对象列表重新打开精确版本。
                    </p>
                    <Link
                      className="product-secondary-action"
                      href={`/projects/${projectId}/data`}
                    >
                      返回项目数据
                    </Link>
                  </div>
                ) : selectedScientificObject && queryObjectVersionId ? (
                  <LazyScientificObjectViewer
                    projectId={projectId}
                    objectId={selectedScientificObject.id}
                    versionId={queryObjectVersionId}
                  />
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
                            href={`/projects/${projectId}/research?dataset=${encodeURIComponent(selected.datasetId)}${
                              scientificSelection?.primary?.sampleRef
                                ? `&sample=${encodeURIComponent(scientificSelection.primary.sampleRef)}`
                                : ""
                            }`}
                          >
                            研究此数据
                          </Link>
                        ) : null}
                      </div>
                    </header>
                    <ScientificDataView
                      projectId={projectId}
                      dataset={selected}
                      kind={kind}
                      onInspect={openInspector}
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
                ) : (
                  <div className="product-state">
                    <h2>
                      {statusFilter === "archived"
                        ? "没有可恢复的数据"
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
                    ) : null}
                  </div>
                )}
              </section>
              {inspector && selected && (
                <aside
                  className="context-inspector"
                  role="region"
                  aria-labelledby="context-inspector-title"
                >
                  <button
                    ref={inspectorCloseRef}
                    type="button"
                    aria-label="关闭详情"
                    onClick={closeInspector}
                  >
                    ×
                  </button>
                  <p className="product-kicker">详情</p>
                  <h2 id="context-inspector-title">
                    {scientificSelection?.primary
                      ? selectionTitle(scientificSelection.primary)
                      : productProjectName(selected.name)}
                  </h2>
                  {scientificSelection?.primary ? (
                    <dl>
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
                    <dl>
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
                  <h3>依据</h3>
                  <p>内容类型与可用属性来自已生成的数据语义档案。</p>
                  <details>
                    <summary>来源与过程</summary>
                    <p>
                      {selected.import.fileCount} 个源文件，经当前导入流程识别。
                    </p>
                  </details>
                  <details>
                    <summary>技术详情</summary>
                    <p>选择 contract 已绑定当前项目和数据范围。</p>
                  </details>
                </aside>
              )}
              {dialog ? (
                <DatasetEditDialog
                  dataset={dialog.dataset}
                  mode={dialog.mode}
                  onClose={() => setDialog(null)}
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

export function DatasetUploadPage({ projectId }: { projectId: string }) {
  const {
    history,
    state: projectState,
    error: projectError,
    retry: retryProject,
  } = useProject(projectId);
  const [name, setName] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!name.trim() || !files.length) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await uploadDatasetFiles(
        projectId,
        name.trim(),
        files.map((file) => {
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
        }),
      );
      setMessage("数据已上传并进入解析流程。");
      setFiles([]);
      setName("");
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "上传失败，请检查文件后重试。",
      );
    } finally {
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
            <p className="product-kicker">项目数据</p>
            <h1>上传数据</h1>
            <p>上传后，系统会识别文件格式并生成可用于研究的数据档案。</p>
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
          {history && canUpload ? (
            <form
              className="upload-form"
              onSubmit={(event) => void submit(event)}
            >
              <label htmlFor="dataset-upload-name">数据集名称</label>
              <input
                id="dataset-upload-name"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="例如：BaTiO3 稳定性数据"
                required
              />
              <label htmlFor="dataset-upload-files">源文件</label>
              <input
                id="dataset-upload-files"
                type="file"
                multiple
                onChange={(event) =>
                  setFiles(Array.from(event.target.files || []))
                }
                required
              />
              {files.length ? (
                <ul aria-label="已选择文件">
                  {files.map((file) => (
                    <li key={file.name + file.size}>
                      {file.name} · {(file.size / 1024).toFixed(1)} KiB
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="upload-hint">
                  支持的格式以当前导入能力为准；不支持的文件会保留为可解释的失败状态。
                </p>
              )}
              {error && (
                <p className="product-form-error" role="alert">
                  {error}
                </p>
              )}
              {message && (
                <p className="product-form-success" role="status">
                  {message}
                </p>
              )}
              <div className="product-row-actions">
                <button
                  type="submit"
                  className="product-primary-action"
                  disabled={busy || !name.trim() || !files.length}
                >
                  {busy ? "正在上传…" : "上传并解析"}
                </button>
                <Link
                  className="product-secondary-action"
                  href={`/projects/${projectId}/data`}
                >
                  取消
                </Link>
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
        EXPERIMENTAL_XRD_PEAK: "实验峰",
        XRD_MATCH: "匹配峰",
        TRAJECTORY_ATOM: "轨迹原子",
        ARTIFACT: "科学结果",
      } as Record<string, string>
    )[kind] || "科学对象"
  );
}

function selectionTitle(selection: {
  kind: string;
  sampleRef: string | null;
  siteId: string | null;
  peakId: string | null;
  matchId: string | null;
  atomId: string | null;
}) {
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
  onSelection,
  onAvailabilityChange,
  tableRouteState,
  onTableRouteChange,
}: {
  projectId: string;
  dataset: ProjectHistory["datasets"][number];
  kind: DataKind;
  onInspect: () => void;
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
  const [resourceError, setResourceError] = useState<string | null>(null);
  const [resourceErrorKind, setResourceErrorKind] = useState<
    "TRANSIENT" | "CONFIRMED_MISSING"
  >("TRANSIENT");
  const [selectedId, setSelectedId] = useState("");
  const [loadAttempt, setLoadAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setResources(null);
    setResourceError(null);
    setResourceErrorKind("TRANSIENT");
    setSelectedId("");
    onAvailabilityChange("loading");
    void getDatasetSourceResources(dataset.datasetId, controller.signal)
      .then((items) => {
        setResources(items);
        setSelectedId(
          preferredResource(items, kind)?.objectId || items[0]?.objectId || "",
        );
        onAvailabilityChange(items.length ? "ready" : "empty");
      })
      .catch((reason) => {
        if (controller.signal.aborted) return;
        setResources([]);
        setResourceErrorKind(classifySourceLoadFailure(reason));
        setResourceError(
          reason instanceof Error
            ? reason.message
            : "SOURCE_RESOURCE_LOAD_FAILED",
        );
        onAvailabilityChange("unavailable");
      });
    return () => controller.abort();
  }, [dataset.datasetId, kind, loadAttempt, onAvailabilityChange]);
  if (resources === null)
    return (
      <div className="product-loading" role="status">
        正在加载科学数据…
      </div>
    );
  if (resourceError && kind !== "table") {
    const confirmedMissing = resourceErrorKind === "CONFIRMED_MISSING";
    const fallbackTitleId = `science-fallback-title-${dataset.datasetId}-${kind}`.replace(
      /[^a-zA-Z0-9_-]/g,
      "-",
    );
    const uploadHref = `/projects/${encodeURIComponent(projectId)}/datasets/new`;
    return (
      <div
        className={`science-canvas science-canvas-fallback source-load-failure ${kind}`}
        role="alert"
        aria-labelledby={fallbackTitleId}
      >
        <div className="science-canvas-label">
          <span>{dataKindLabel(kind)}</span>
          <strong id={fallbackTitleId}>
            {confirmedMissing
              ? "原始解析 payload 当前不可用"
              : "当前科学资源暂时无法读取"}
          </strong>
        </div>
        <p>
          {confirmedMissing
            ? "系统已确认声明位置没有原始 payload；数据档案、精确来源与解析记录仍然保留，不会用其他版本替代。请重新导入或恢复原始文件。"
            : "数据档案、精确来源与解析记录仍然保留；当前规范化 payload 暂时未能通过存储读取。"}
        </p>
        <p className="source-load-failure-status" role="status">
          <span>读取状态</span>
          <strong>{confirmedMissing ? "已确认缺失" : "暂时失败，可重试"}</strong>
        </p>
        <div className="source-load-failure-actions">
          <button
            type="button"
            className="product-primary-action"
            onClick={onInspect}
          >
            查看来源与属性
          </button>
          <button
            type="button"
            className="product-secondary-action"
            onClick={() => setLoadAttempt((attempt) => attempt + 1)}
          >
            {confirmedMissing ? "再次确认来源" : "重新检查存储"}
          </button>
          {confirmedMissing ? (
            <Link className="product-secondary-action" href={uploadHref}>
              重新导入源文件
            </Link>
          ) : null}
        </div>
        <details>
          <summary>技术详情</summary>
          <p>{resourceError}</p>
          <p>未选择其他 Dataset、ScientificObjectVersion 或 Artifact 作为替代。</p>
        </details>
      </div>
    );
  }
  const selected =
    resources.find((item) => item.objectId === selectedId) ||
    preferredResource(resources, kind);
  if (resources.length > 1 || kind === "detected")
    return (
      <div className="detected-content">
        <div>
          <p className="product-kicker">检测到的数据</p>
          <h2>此上传包含 {resources.length} 个科学对象</h2>
          <p>仅展示导入流程实际识别的资源，不推测压缩包目录。</p>
        </div>
        <nav aria-label="检测到的科学对象">
           {resources.map((resource, index) => (
             <button
               key={resource.objectId}
              className={
                resource.objectId === selected?.objectId ? "selected" : ""
              }
               aria-pressed={resource.objectId === selected?.objectId}
               onClick={() => setSelectedId(resource.objectId)}
             >
               <strong>{resourceDisplayName(resource, resources, index)}</strong>
               <span>
                 {resource.objectId === selected?.objectId
                   ? "当前查看"
                   : "切换查看"}
               </span>
             </button>
           ))}
        </nav>
        {selected ? (
          <section className="source-scientific-viewer">
            <LazyScientificSourceViewer
              projectId={projectId}
              resource={selected}
              resources={resources}
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
  const status = Number(candidate.status);
  const errorType = String(candidate.errorType || "");
  const detail = candidate.details && typeof candidate.details === "object"
    ? candidate.details as { errorType?: unknown; code?: unknown }
    : {};
  const detailType = String(detail.errorType || detail.code || "");
  return status === 404
    || /(?:SOURCE_MISSING|OBJECT_STORE_SOURCE_MISSING|SOURCE_RESOURCE_MISSING|PAYLOAD_MISSING)/i.test(`${errorType} ${detailType}`)
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
  DataTableViewState & { selection: string }
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
