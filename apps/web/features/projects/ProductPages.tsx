"use client";

import { ProductLink as Link, useProductRouter } from "../../shared/layout/ProductNavigation";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import {
  bulkDatasetAction,
  bulkProjectAction,
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
  researchRunSourceDatasets,
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
import { DependencyPreviewFeedback, useDependencyPreview, type DependencyPreviewState } from "../../shared/ui/DependencyPreview";

import { useProjectOperation, validateProject, validateProjectBatch, validateProjectDirectory, type ProjectOperation } from "./project-operations";

import { ProjectCreateDialog } from "./ProjectCreateDialog";
import { useClampedTitle } from "../../shared/ui/use-clamped-title";
import { SourceDatasetList } from "../../shared/ui/SourceDatasetList";

type LoadState = "loading" | "ready" | "error";

function DependencyImpactEntry({
  item,
}: {
  item: { kind?: string; label: string; count: number; href?: string };
}) {
  const label = dependencyDisplayLabel(item.kind || "", item.label);
  return (
    <>
      {item.href ? <Link href={item.href}>{label}</Link> : label}：
      {item.count}
    </>
  );
}

function dependencyDisplayLabel(kind: string, fallback: string) {
  return ({
    analysis_plans: "分析方案",
    research_context_snapshots: "研究上下文",
    research_session_states: "研究会话状态",
  } as Record<string, string>)[kind] || fallback;
}

function projectHistoryRunHref(
  projectId: string,
  run: ProjectHistory["analyses"][number],
) {
  const query = new URLSearchParams({ run: run.jobId });
  if (run.researchTurnId) query.set("turn", run.researchTurnId);
  if (run.researchSessionId) {
    return `/projects/${projectId}/research/${encodeURIComponent(run.researchSessionId)}?${query.toString()}`;
  }
  return `/projects/${projectId}/research?${query.toString()}`;
}

function useProjects() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState("");
  const [loadAttempt, setLoadAttempt] = useState(0);
  const [revision, setRevision] = useState(0);
  const loadingRef = useRef(true);
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    loadingRef.current = true;
    setState("loading");
    setError("");
    const timer = window.setTimeout(() => {
      if (!active) return;
      active = false;
      controller.abort();
      loadingRef.current = false;
      setError("项目列表读取超时，请重试。");
      setState("error");
    }, 10_000);
    void listProjects({ signal: controller.signal, ...(loadAttempt ? { forceRefresh: true } : {}) })
      .then((items) => {
        if (active) {
          validateProjectDirectory(items);
          setProjects(items);
          setRevision((value) => value + 1);
          setState("ready");
        }
      })
      .catch(() => {
        if (active) {
          setError("暂时无法读取项目列表，请重试。");
          setState("error");
        }
      })
      .finally(() => { window.clearTimeout(timer); if (active) loadingRef.current = false; });
    return () => {
      active = false;
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [loadAttempt]);
  const retry = () => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setLoadAttempt((attempt) => attempt + 1);
  };
  return { projects, setProjects, state, error, retry, revision };
}

function historyBelongsToProject(history: ProjectHistory | null, projectId: string) {
  if (!history) return false;
  const project = history.project;
  return (project.projectId || project.id) === projectId
    && (!project.projectId || project.projectId === projectId)
    && (!project.id || project.id === projectId);
}

function useProject(projectId: string) {
  const [history, setHistory] = useState<ProjectHistory | null>(() => {
    const cached = getCachedProjectHistory(projectId);
    return historyBelongsToProject(cached, projectId) ? cached : null;
  });
  const [state, setState] = useState<LoadState>(() => history ? "ready" : "loading");
  const [error, setError] = useState("");
  const [loadAttempt, setLoadAttempt] = useState(0);
  const loadingRef = useRef(false);
  useEffect(() => {
    let active = true;
    setError("");
    const cached = getCachedProjectHistory(projectId);
    if (historyBelongsToProject(cached, projectId) && loadAttempt === 0) {
      loadingRef.current = false;
      setHistory(cached);
      setState("ready");
      return () => {
        active = false;
      };
    }
    loadingRef.current = true;
    setState("loading");
    const timer = window.setTimeout(() => {
      if (!active) return;
      active = false;
      loadingRef.current = false;
      setError("项目数据读取超时，请重试。");
      setState("error");
    }, 10_000);
    // ProductShell prefetches this ledger on navigation intent. Reuse the
    // shared in-flight/warm request so switching project surfaces does not
    // discard the shell and wait on an avoidable duplicate fetch.
    void getProjectHistory(projectId, loadAttempt > 0 || Boolean(cached && !historyBelongsToProject(cached, projectId)) ? { forceRefresh: true } : undefined)
      .then((item) => {
        if (active) {
          if (!historyBelongsToProject(item, projectId)) throw new Error("PROJECT_IDENTITY_MISMATCH");
          setHistory(item);
          setState("ready");
        }
      })
      .catch(() => {
        if (active) {
          setError("暂时无法读取项目数据，请重试。");
          setState("error");
        }
      }).finally(() => {
        window.clearTimeout(timer);
        if (active) loadingRef.current = false;
      });
    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [projectId, loadAttempt]);
  const retry = () => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setLoadAttempt((attempt) => attempt + 1);
  };
  return { history: historyBelongsToProject(history, projectId) ? history : null, setHistory, state, error, retry };
}

function EmptyOrError({
  state,
  error,
  loading,
  onRetry,
}: {
  state: LoadState;
  error: string;
  loading?: ReactNode;
  onRetry?: () => void;
}) {
  if (state === "loading")
    return loading ?? (
      <div className="product-loading" role="status" aria-live="polite">
        正在加载研究内容…
      </div>
    );
  if (state === "error")
    return (
      <div className="product-state" role="alert">
        <h2>暂时无法加载</h2>
        <p>{error}</p>
        {onRetry ? (
          <div className="product-row-actions">
            <button type="button" className="product-primary-action" onClick={onRetry}>
              重新加载项目数据
            </button>
          </div>
        ) : null}
      </div>
    );
  return null;
}

function ProjectEditDialog({
  project,
  mode,
  returnFocus,
  onClose,
  onUpdated,
  onDeleted,
  operation,
  onReload,
  reading,
  readError,
}: {
  operation: ProjectOperation;
  onReload: () => void;
  reading: boolean;
  readError: string;
  project: ProjectSummary;
  mode: "edit" | "trash" | "delete";
  returnFocus?: HTMLElement | null;
  onClose: () => void;
  onUpdated: (project: ProjectSummary) => void;
  onDeleted: (projectId: string) => void;
}) {
  const projectId = project.projectId || project.id;
  const [name, setName] = useState(project.name);
  const [description, setDescription] = useState(project.description || "");
  const [tags, setTags] = useState((project.tags || []).join(", "));
  const [confirmation, setConfirmation] = useState("");
  const busy = operation.pending || reading;
  const error = operation.error;
  const locked = busy || operation.uncertain;
  const recovery = operation.uncertain ? <div className="project-operation-recovery"><button type="button" className="product-secondary-action" disabled={busy} onClick={onReload}>{reading ? "正在读取…" : "重新读取项目列表"}</button>{readError ? <p role="status">{readError} 当前编辑内容已保留。</p> : null}</div> : null;
  const preview = useDependencyPreview(
    mode === "edit" ? [] : [{ id: projectId, label: project.name }],
    getProjectDependencyImpact,
  );
  const impact = preview.items[0];
  async function save() {
    if (!name.trim() || locked) return;
    await operation.run("保存项目", async (signal) => validateProject(await updateProject(projectId, {
      name: name.trim(), description: description.trim(),
      tags: tags.split(/[,，]/u).map((value) => value.trim()).filter(Boolean).slice(0, 12),
    }, signal), projectId, { name: name.trim(), description: description.trim() }), (next) => { onUpdated(next); onClose(); });
  }
  async function remove() {
    if (confirmation !== project.name || locked || !preview.complete || !impact?.canDelete) return;
    await operation.run("删除空项目", async (signal) => {
      const result = await deleteEmptyProject(projectId, signal);
      if (result?.projectId !== projectId || result.deleted !== true) throw new Error("Project deletion identity mismatch");
      return result;
    }, () => { onDeleted(projectId); onClose(); });
  }
  async function trash() {
    if (locked || !preview.complete) return;
    await operation.run("移入回收站", async (signal) => validateProject(await updateProject(projectId, { lifecycle: "TRASHED" }, signal), projectId, { lifecycle: "TRASHED" }),
      (next) => { onUpdated(next); onClose(); });
  }
  if (mode === "trash")
    return (
      <ProductModal
        title="将项目移入回收站"
        description="项目会从当前工作流中移除，但受保护的数据、研究结果和报告仍保留，可从回收站恢复。"
        onClose={onClose}
        returnFocus={returnFocus}
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
        <div className="product-form-grid danger-zone">
          <p>
            <strong>{project.name}</strong> 将不再出现在当前项目列表中。
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
              <p>历史研究和科学来源记录不会被删除。</p>
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
  if (mode === "delete")
    return (
      <ProductModal
        title="删除空项目"
        description="仅完全没有数据、研究记录与报告的项目可被永久删除。"
        onClose={onClose}
        returnFocus={returnFocus}
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
              disabled={locked || confirmation !== project.name || !preview.complete || !impact?.canDelete}
              onClick={() => void remove()}
            >
              {busy ? "正在删除…" : "永久删除"}
            </button>
          </>
        }
      >
        <div className="product-form-grid danger-zone">
          <p>
            此操作不可撤销。输入项目名称 <strong>{project.name}</strong>{" "}
            以确认。
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
          <label htmlFor="delete-project-confirmation">项目名称</label>
          <input
            id="delete-project-confirmation"
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
      title="编辑项目信息"
      description="更新项目名称、说明和整理标签。"
      onClose={onClose}
      returnFocus={returnFocus}
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
      <div className="product-form-grid">
        <label htmlFor="edit-project-name">项目名称</label>
        <input
          id="edit-project-name"
          maxLength={160}
          value={name}
          onChange={(event) => setName(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              void save();
            }
          }}
        />
        <label htmlFor="edit-project-description">研究说明</label>
        <textarea
          id="edit-project-description"
          maxLength={2000}
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          rows={4}
        />
        <label htmlFor="edit-project-tags">
          组织标签 <span>可选，用逗号分隔</span>
        </label>
        <input
          id="edit-project-tags"
          value={tags}
          onChange={(event) => setTags(event.target.value)}
          placeholder="例如：钙钛矿，XRD，待复核"
        />
        <p className="product-form-hint">
          用标签查找和整理项目，支持中文或英文逗号。
        </p>
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

function projectNavigationActions(project: ProjectSummary): ObjectAction[] {
  const id = project.projectId || project.id;
  const actions: ObjectAction[] = [
    { label: "打开项目概览", href: `/projects/${id}` },
    { label: "查看数据", href: `/projects/${id}/data` },
    { label: "研究记录", href: `/projects/${id}/research` },
    { label: "查看报告", href: `/projects/${id}/reports` },
  ];
  if (projectRoleAllows(project.role, "write")) {
    actions.push({ label: "上传数据", href: `/projects/${id}/datasets/new` });
    actions.push({
      label: "管理项目",
      href: `/projects?manage=${encodeURIComponent(id)}`,
    });
  }
  return actions;
}

function ProjectBulkTrashDialog({
  items,
  preview,
  busy,
  error,
  onClose,
  onConfirm,
}: {
  items: ProjectSummary[];
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
      eyebrow="项目管理"
      title={`将 ${items.length} 个项目移入回收站`}
      description="批量操作会先检查每个项目的服务器依赖；数据、研究结果、历史版本与报告不会被删除。"
      onClose={onClose}
      footer={
        <>
          <button type="button" className="product-secondary-action" onClick={onClose}>
            取消
          </button>
          <button
            type="button"
            className="product-danger-action"
            disabled={busy || !preview.complete}
            onClick={onConfirm}
          >
            {busy ? "正在移动…" : "确认移入回收站"}
          </button>
        </>
      }
    >
      <div className="product-form-grid danger-zone">
        <p>
          已选择 <strong>{items.length}</strong> 个项目。
          {impacts.length > 0 ? <>已读取 {impacts.length} 项检查，共 <strong>{totalDependencies}</strong> 项受保护依赖。</> : null}
        </p>
        <ul className="bulk-lifecycle-targets">
          {items.slice(0, 8).map((item) => (
            <li key={item.projectId || item.id}>
              <strong>{item.name}</strong>
              <span>{item.role === "owner" ? "所有者" : "协作项目"}</span>
            </li>
          ))}
          {items.length > 8 ? <li>另有 {items.length - 8} 个项目…</li> : null}
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
              <p>已读取的检查中未发现已持久化的科学依赖。</p>
            )}
            <p>项目会从当前列表中移除；历史研究和精确来源记录仍可访问。</p>
          </div>
        ) : null}
        <DependencyPreviewFeedback preview={preview} />
        {error ? <p className="product-form-error" role="alert">{error}</p> : null}
      </div>
    </ProductModal>
  );
}

function projectUpdatedTime(project: ProjectSummary) {
  const value = Date.parse(project.updatedAt || project.createdAt || "");
  return Number.isFinite(value) ? value : 0;
}

function projectDirectoryDescription(project: ProjectSummary) {
  const date = projectUpdatedTime(project);
  return [project.description?.trim(), project.tags?.join(" · "), date ? `更新于 ${new Date(date).toLocaleDateString("zh-CN")}` : ""].filter(Boolean).join(" · ");
}

export function ConsolePage() {
  const { projects, setProjects, state, error, retry } = useProjects();
  const [preview, setPreview] = useState<ProjectSummary | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [createTrigger, setCreateTrigger] = useState<HTMLElement | null>(null);
  const activeProjects = projects.filter(
    (project) => !["archived", "trashed"].includes(project.status?.toLowerCase() || ""),
  ).sort((a, b) => projectUpdatedTime(b) - projectUpdatedTime(a));
  const primaryProjectId =
    activeProjects[0]?.projectId || activeProjects[0]?.id || "";
  const triggerRef = useRef<HTMLButtonElement | null>(null);
  const wasPreviewOpenRef = useRef(false);
  const closePreview = () => {
    setPreview(null);
    // On narrow layouts the trigger is hidden while the preview is open. Defer focus
    // until React has restored the original content to the accessibility tree.
    window.setTimeout(() => triggerRef.current?.focus(), 0);
  };
  useEffect(() => {
    if (wasPreviewOpenRef.current && !preview) {
      window.requestAnimationFrame(() => triggerRef.current?.focus());
    }
    wasPreviewOpenRef.current = Boolean(preview);
  }, [preview]);
  useEffect(() => {
    if (!preview) return;
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !event.defaultPrevented) closePreview();
    };
    document.addEventListener("keydown", close);
    return () => document.removeEventListener("keydown", close);
  }, [preview]);
  useEffect(() => {
    if (!primaryProjectId) return;
    // Warm the same bounded project ledger used by the overview/data/research
    // routes while the user is still on the console. The request is deduped by
    // planner-api and is intentionally fire-and-forget: navigation remains
    // fully client-side, while the first project page can paint immediately
    // from the resolved snapshot instead of waiting for a second round trip.
    const timer = window.setTimeout(() => {
      void getProjectHistory(primaryProjectId).catch(() => undefined);
    }, 160);
    return () => window.clearTimeout(timer);
  }, [primaryProjectId]);
  return (
    <RequireProductAuth>
      <ProductShell>
        <section className={`console-page ${preview ? "with-preview" : ""}`}>
          <div className="console-content">
            <header className="product-page-heading console-heading">
              <div>
                <h1>控制台</h1>
                <p>打开项目，继续分析数据或查看报告。</p>
              </div>
              <div className="product-row-actions">
                <button
                  type="button"
                  className="product-primary-action"
                  onClick={(event) => {
                    setCreateTrigger(event.currentTarget);
                    setCreateOpen(true);
                  }}
                >
                  新建项目
                </button>
                <button
                  type="button"
                  className="product-secondary-action"
                  onClick={() =>
                    window.dispatchEvent(
                      new CustomEvent("mdi:open-project-search"),
                    )
                  }
                >
                  搜索项目
                </button>
              </div>
            </header>
            <EmptyOrError state={state} error={error} onRetry={retry} />
            {state === "ready" && activeProjects.length === 0 && (
              <div className="product-state">
                <h2>{projects.length ? "暂时没有进行中的项目" : "创建第一个项目"}</h2>
                <p>{projects.length ? "已有项目已归档或移入回收站。打开项目目录后可以恢复。" : "点击“新建项目”，上传文件后即可开始分析。"}</p>
                {projects.length ? <Link className="product-secondary-action" href="/projects">查看全部项目</Link> : null}
              </div>
            )}
            {activeProjects.length > 0 && (
              <>
                <section className="continue-research">
                  <div>
                    <span className="product-kicker">{projectUpdatedTime(activeProjects[0]) ? "最近更新" : "继续研究"}</span>
                    <h2><Link href={`/projects/${primaryProjectId}`}>{activeProjects[0].name}</Link></h2>
                    {projectDirectoryDescription(activeProjects[0]) ? <p>{projectDirectoryDescription(activeProjects[0])}</p> : null}
                  </div>
                  <div className="product-row-actions">
                    <Link
                      className="product-primary-action"
                      href={`/projects/${primaryProjectId}/research`}
                      prefetch
                    >
                      继续研究
                    </Link>
                    <button
                      ref={triggerRef}
                      className="product-secondary-action"
                      onClick={() => setPreview(activeProjects[0])}
                    >
                      快速查看
                    </button>
                  </div>
                </section>
                <section className="product-section">
                  <div className="product-section-heading">
                    {activeProjects.length > 1 ? <h2>其他项目</h2> : null}
                    <Link href="/projects">查看全部项目</Link>
                  </div>
                  <div className="project-list">
                    {activeProjects.slice(1, 6).map((project) => (
                      <ManagedObjectRow
                        key={project.id}
                        href={`/projects/${project.projectId || project.id}`}
                        title={project.name}
                        description={projectDirectoryDescription(project)}
                        trailing="打开 →"
                        actions={projectNavigationActions(project)}
                      />
                    ))}
                  </div>
                </section>
              </>
            )}
          </div>
          {preview && (
            <ProjectQuickPreview project={preview} onClose={closePreview} />
          )}
          {createOpen ? (
            <ProjectCreateDialog
              returnFocus={createTrigger}
              onClose={() => setCreateOpen(false)}
              onCreated={(project) =>
                setProjects((current) => [project, ...current.filter((item) => item.id !== project.id)])
              }
            />
          ) : null}
        </section>
      </ProductShell>
    </RequireProductAuth>
  );
}

function ProjectQuickPreview({
  project,
  onClose,
}: {
  project: ProjectSummary;
  onClose: () => void;
}) {
  const projectId = project.projectId || project.id;
  const [dataset, setDataset] = useState<
    ProjectHistory["datasets"][number] | null
  >(null);
  const [resource, setResource] = useState<DatasetSourceResource | null>(null);
  const [resources, setResources] = useState<DatasetSourceResource[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [loadAttempt, setLoadAttempt] = useState(0);
  const [previewSelection, setPreviewSelection] = useState<WorkspaceSelectionContext | null>(null);
  const [selectionToken, setSelectionToken] = useState("");
  const [selectionError, setSelectionError] = useState("");
  const closeRef = useRef<HTMLButtonElement>(null);
  useEffect(() => { closeRef.current?.focus(); }, []);
  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      controller.abort();
      setState("error");
    }, 10_000);
    setState("loading");
    setDataset(null);
    setResource(null);
    setResources([]);
    setPreviewSelection(null);
    setSelectionToken("");
    setSelectionError("");
    void getProjectHistory(projectId, { signal: controller.signal })
      .then((history) => {
        if (controller.signal.aborted) return null;
        if (!historyBelongsToProject(history, projectId)) throw new Error("PROJECT_IDENTITY_MISMATCH");
        const firstDataset = history.datasets.find((item) => !["archived", "trashed"].includes(item.status?.toLowerCase() || ""));
        if (!firstDataset) return null;
        if (!firstDataset.datasetId) throw new Error("DATASET_IDENTITY_MISSING");
        setDataset(firstDataset);
        return getDatasetSourceResources(
          firstDataset.datasetId,
          controller.signal,
        ).then((items) => {
          if (items.some((item) => item.datasetId !== firstDataset.datasetId)) throw new Error("DATASET_IDENTITY_MISMATCH");
          return items;
        });
      })
      .then((resources) => {
        if (controller.signal.aborted) return;
        setResources(resources || []);
        setResource(resources?.[0] || null);
        setState("ready");
      })
      .catch(() => {
        if (!controller.signal.aborted) setState("error");
      }).finally(() => window.clearTimeout(timer));
    return () => { controller.abort(); window.clearTimeout(timer); };
  }, [projectId, loadAttempt]);
  const previewQuery = new URLSearchParams();
  if (dataset) previewQuery.set("dataset", dataset.datasetId);
  if (selectionToken) previewQuery.set("selection", selectionToken);
  const dataHref = `/projects/${projectId}/data${previewQuery.size ? `?${previewQuery}` : ""}`;
  return (
    <aside className="quick-preview" aria-label="数据快速查看">
      <header className="quick-preview-header">
        <div>
          <p className="product-kicker">快速查看</p>
          <h2>{project.name}</h2>
          <p>预览项目数据，或打开数据页继续查看。</p>
        </div>
        <button ref={closeRef} type="button" onClick={onClose} aria-label="关闭快速查看">
          ×
        </button>
      </header>
      <div className="quick-preview-viewer">
        {state === "loading" ? (
          <div className="product-loading" role="status">
            正在加载项目数据…
          </div>
        ) : null}
        {state === "error" ? (
          <div className="product-state" role="alert">
            <h3>暂时无法加载数据</h3>
            <p>请重新加载，或打开项目数据页查看。</p>
            <div className="product-row-actions">
              <button
                type="button"
                className="product-primary-action"
                onClick={() => setLoadAttempt((attempt) => attempt + 1)}
              >
                重新加载数据
              </button>
            </div>
          </div>
        ) : null}
        {state === "ready" && dataset && resource ? (
          <>
            <div className="quick-preview-resource">
              <strong>{productProjectName(dataset.name)}</strong>
              <span>{sourceTypeLabel(resource.objectType)}</span>
            </div>
            <LazyScientificSourceViewer
              projectId={projectId}
              resource={resource}
              resources={resources}
              selection={previewSelection}
              onSelection={(selection) => {
                setSelectionError("");
                try {
                  if (!selection.cleared && (!selection.primary || selection.compatibility !== "EXACT" || [selection.primary, ...selection.secondary].some((ref) => ref.projectId !== projectId || ref.datasetId !== dataset.datasetId))) throw new Error("PREVIEW_SELECTION_SCOPE_MISMATCH");
                  setSelectionToken(selection.cleared ? "" : encodeWorkspaceSelectionUrl(selection));
                  setPreviewSelection(selection.cleared ? null : selection);
                } catch {
                  setSelectionToken("");
                  setPreviewSelection(null);
                  setSelectionError("当前选择无法带到数据页，请打开数据页后重新选择。");
                }
              }}
            />
          </>
        ) : null}
        {state === "ready" && dataset && !resource ? (
          <div className="product-state">
            <h3>
              {Number(dataset.import.fileCount || 0) === 0
                ? "这份数据尚未上传文件"
                : "这份数据暂时无法预览"}
            </h3>
            <p>
              {Number(dataset.import.fileCount || 0) === 0
                ? "打开项目数据页，上传文件后即可查看。"
                : "打开项目数据页，查看上传记录和处理状态。"}
            </p>
          </div>
        ) : null}
        {state === "ready" && !dataset ? (
          <div className="product-state">
            <h3>项目还没有数据</h3>
            <p>打开项目数据页，上传第一份文件。</p>
          </div>
        ) : null}
      </div>
      <div className="quick-preview-footer">
        {selectionError ? <p role="alert" className="product-form-error">{selectionError}</p> : null}
        {selectionToken ? <div className="quick-preview-selection"><span role="status">已选中数据</span><button type="button" className="product-link-button" onClick={() => { setPreviewSelection(null); setSelectionToken(""); }}>取消选择</button></div> : null}
        <Link className="product-primary-action quick-preview-open" href={dataHref}>{selectionToken ? "查看所选数据" : "打开项目数据"}</Link>
      </div>
    </aside>
  );
}

export function ProjectsPage({
  manageProjectId = "",
}: { manageProjectId?: string } = {}) {
  const { projects, setProjects, state, error, retry, revision } = useProjects();
  const operation = useProjectOperation();
  const manageId = manageProjectId;
  const router = useProductRouter();
  const handledManageIdRef = useRef("");
  const projectHeadingRef = useRef<HTMLHeadingElement>(null);
  const focusAfterProjectRead = useRef(false);
  useEffect(() => {
    if (!revision) return;
    operation.reconciled();
    if (!focusAfterProjectRead.current) return;
    focusAfterProjectRead.current = false;
    const frame = window.requestAnimationFrame(() => {
      (document.getElementById("edit-project-name") || projectHeadingRef.current)?.focus();
    });
    return () => window.cancelAnimationFrame(frame);
  }, [revision, operation.reconciled]);
  const recoverProjectList = () => { focusAfterProjectRead.current = true; retry(); };
  const [manageError, setManageError] = useState("");
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<
    "active" | "archived" | "trashed" | "all"
  >("active");
  const [tagFilter, setTagFilter] = useState("");
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [createOpen, setCreateOpen] = useState(false);
  const [dialog, setDialog] = useState<{
    project: ProjectSummary;
    mode: "edit" | "trash" | "delete";
    returnFocus?: HTMLElement | null;
  } | null>(null);
  const [projectBulkTrashTargets, setProjectBulkTrashTargets] = useState<
    ProjectSummary[] | null
  >(null);
  const projectBulkPreview = useDependencyPreview(
    (projectBulkTrashTargets || []).map((project) => ({ id: project.projectId || project.id, label: project.name })),
    getProjectDependencyImpact,
  );
  const mutationError = operation.error;
  const [mutationNotice, setMutationNotice] = useState("");
  const busy = operation.pending || state === "loading";
  useEffect(() => {
    if (!manageId) {
      handledManageIdRef.current = "";
      setManageError("");
      return;
    }
    if (state !== "ready" || dialog || handledManageIdRef.current === manageId) return;
    handledManageIdRef.current = manageId;
    const project = projects.find(
      (item) => (item.projectId || item.id) === manageId,
    );
    if (!project) {
      setManageError("无法打开项目管理。该项目不存在或当前账户无法访问。");
    } else if (!projectRoleAllows(project.role, "write")) {
      setManageError("该项目当前为只读，无法编辑项目信息。仍可从列表打开项目查看内容。");
    } else {
      setManageError("");
      setDialog({ project, mode: "edit", returnFocus: projectHeadingRef.current });
    }
  }, [dialog, manageId, projects, state]);
  function dismissManageRoute() {
    setManageError("");
    if (!manageId) return;
    const url = new URL(window.location.href);
    if (url.searchParams.get("manage") !== manageId) return;
    url.searchParams.delete("manage");
    router.replace(`${url.pathname}${url.search}${url.hash}`, { scroll: false });
  }
  function closeProjectDialog() {
    operation.dismiss();
    setDialog(null);
    dismissManageRoute();
  }
  const filteredProjects = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase();
    return projects.filter((project) => {
      const lifecycle =
        project.status === "trashed"
          ? "trashed"
          : project.status === "archived"
            ? "archived"
            : "active";
      const statusMatches =
        statusFilter === "all" || lifecycle === statusFilter;
      const tagMatches =
        !tagFilter || (project.tags || []).some((tag) => tag === tagFilter);
      return (
        statusMatches &&
        tagMatches &&
        (!normalized ||
          `${project.name} ${project.description || ""} ${(project.tags || []).join(" ")}`
            .toLocaleLowerCase()
            .includes(normalized))
      );
    });
  }, [projects, query, statusFilter, tagFilter]);
  const selectableIds = useMemo(
    () => filteredProjects
      .filter((project) => projectRoleAllows(project.role, "write"))
      .map((project) => project.projectId || project.id),
    [filteredProjects],
  );
  useEffect(() => {
    setSelectedIds((current) => {
      const retained = new Set(selectableIds.filter((id) => current.has(id)));
      return retained.size === current.size ? current : retained;
    });
  }, [selectableIds]);
  const availableTags = useMemo(
    () =>
      Array.from(
        new Set(
          projects
            .flatMap((project) => project.tags || [])
            .filter((tag) => tag.trim()),
        ),
      ).sort((left, right) => left.localeCompare(right, "zh-CN")),
    [projects],
  );
  const byCatalogName = (left: ProjectSummary, right: ProjectSummary) => {
    const pinOrder = Number(Boolean(right.pinned)) - Number(Boolean(left.pinned));
    return pinOrder || left.name.localeCompare(right.name, "zh-CN", { numeric: true });
  };
  const catalogProjects = [...filteredProjects].sort(byCatalogName);
  const hasSelectableProjects = projects.some((project) =>
    projectRoleAllows(project.role, "write"),
  );
  const updateLocal = (next: ProjectSummary) =>
    setProjects((current) =>
      current.map((project) =>
        (project.projectId || project.id) === (next.projectId || next.id)
          ? next
          : project,
      ),
    );
  async function setArchived(project: ProjectSummary, archived: boolean) {
    if (busy) return;
    setMutationNotice("");
    const id = project.projectId || project.id;
    await operation.run(archived ? "归档项目" : "恢复项目", async (signal) => validateProject(await updateProject(id, { archived }, signal), id, { archived }), (next) => {
      updateLocal(next); setMutationNotice(`“${project.name}”${archived ? "已归档" : "已恢复"}。`);
      window.requestAnimationFrame(() => projectHeadingRef.current?.focus());
    });
  }
  async function restoreProject(project: ProjectSummary) { await setArchived(project, false); }
  async function setPinned(project: ProjectSummary, pinned: boolean) {
    if (busy) return;
    setMutationNotice("");
    const id = project.projectId || project.id;
    await operation.run(pinned ? "置顶项目" : "取消置顶", async (signal) => validateProject(await updateProject(id, { pinned }, signal), id, { pinned }), updateLocal);
  }
  async function applyBatch(action: "archive" | "trash" | "restore" | "pin" | "unpin", confirmedIds?: string[]) {
    const ids = confirmedIds || selectableIds.filter((id) => selectedIds.has(id));
    if (!ids.length || busy) return;
    setMutationNotice("");
    await operation.run("批量更新项目", async (signal) => validateProjectBatch(await bulkProjectAction(ids, action, signal), action, ids), (result) => {
      const completedLabel = { archive: "已归档", trash: "已移入回收站", restore: "已恢复", pin: "已列表置顶", unpin: "已取消列表置顶" }[action];
      setMutationNotice(`${completedLabel} ${result.count} 个项目。`);
      setSelectedIds(new Set()); setSelectionMode(false); retry();
    });
  }
  function requestProjectBulkTrash() {
    const targets = filteredProjects.filter((project) =>
      selectedIds.has(project.projectId || project.id) && projectRoleAllows(project.role, "write"),
    );
    if (targets.length) {
      setProjectBulkTrashTargets(targets);
    }
  }
  function confirmProjectBulkTrash() {
    if (
      !projectBulkTrashTargets ||
      !projectBulkPreview.complete
    ) {
      return;
    }
    const confirmedIds = projectBulkTrashTargets.map((project) => project.projectId || project.id);
    setProjectBulkTrashTargets(null);
    void applyBatch("trash", confirmedIds);
  }
  async function exportProject(project: ProjectSummary) {
    if (busy) return;
    setMutationNotice("");
    const id = project.projectId || project.id;
    await operation.run("导出项目清单", async (signal) => {
      const manifest = await getProjectExportManifest(id, signal);
      if (manifest?.project?.id !== id || manifest.exportKind !== "authorized_project_provenance" || manifest.executable !== false) throw new Error("Project export identity mismatch");
      return manifest;
    }, (manifest) => {
      const blob = new Blob([JSON.stringify(manifest, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      try {
        const anchor = document.createElement("a"); anchor.href = url;
        anchor.download = `${(project.name || "project").replace(/[^\w\u4e00-\u9fff.-]+/gu, "-").slice(0, 80) || "project"}-provenance.json`;
        document.body.appendChild(anchor); anchor.click(); anchor.remove();
      } finally { window.setTimeout(() => URL.revokeObjectURL(url), 0); }
      setMutationNotice(`已导出“${project.name}”的来源清单。`);
    }, true);
  }
  function actionsFor(project: ProjectSummary): ObjectAction[] {
    const canWrite = projectRoleAllows(project.role, "write");
    const actions = projectNavigationActions(project).filter(
      (action) => action.label !== "管理项目",
    );
    // Export is a read-only provenance operation. The API authorizes it with
    // project read access, so shared viewers must be able to discover it even
    // though lifecycle and metadata mutations remain write-gated below.
    actions.push({
      label: "导出项目清单",
      onSelect: () => void exportProject(project),
    });
    if (!canWrite) return actions;
    if (project.status === "trashed") {
      const historicalActions = actions.filter(
        (action) => action.label !== "上传数据",
      );
      historicalActions.push({
        label: "从回收站恢复",
        onSelect: () => void restoreProject(project),
      });
      if (project.role === "owner")
        historicalActions.push({
          label: "永久删除空项目",
          destructive: true,
          onSelect: () => setDialog({ project, mode: "delete" }),
        });
      return historicalActions;
    }
    actions.push({
      label: "编辑项目信息",
      onSelect: () => setDialog({ project, mode: "edit" }),
    });
    actions.push({
      label: project.pinned ? "取消列表置顶" : "列表置顶",
      onSelect: () => void setPinned(project, !project.pinned),
    });
    actions.push({
      label: project.status === "archived" ? "恢复项目" : "归档项目",
      onSelect: () => void setArchived(project, project.status !== "archived"),
    });
    if (project.role === "owner")
      actions.push({
        label: "移入回收站",
        destructive: true,
        onSelect: () => setDialog({ project, mode: "trash" }),
      });
    return actions;
  }
  const toggleSelected = (project: ProjectSummary, selected: boolean) => {
    const id = project.projectId || project.id;
    setSelectedIds((current) => {
      const next = new Set(current);
      if (selected) next.add(id);
      else next.delete(id);
      return next;
    });
  };
  const renderProjects = (items: ProjectSummary[]) => (
    <div className="project-list large">
      {items.map((project) => (
        <ManagedObjectRow
          key={project.id}
          href={`/projects/${project.projectId || project.id}`}
          title={project.name}
          description={projectDirectoryDescription(project)}
          trailing={
            project.status === "trashed"
              ? "回收站"
              : project.status === "archived"
                ? project.pinned
                  ? "列表置顶 · 已归档"
                  : "已归档"
                : project.pinned
                  ? "列表置顶 · 打开项目 →"
                  : "打开项目 →"
          }
          actions={actionsFor(project).map((action) => ({ ...action, disabled: action.disabled || Boolean(action.onSelect && (busy || operation.uncertain)) }))}
          selectionMode={selectionMode}
          selectable={projectRoleAllows(project.role, "write")}
          selected={selectedIds.has(project.projectId || project.id)}
          onSelectedChange={(selected) => toggleSelected(project, selected)}
        />
      ))}
    </div>
  );
  return (
    <RequireProductAuth>
      <ProductShell>
        <section className="document-page projects-directory-page">
          <header className="product-page-heading projects-directory-heading">
            <div>
              <h1 ref={projectHeadingRef} tabIndex={-1}>项目</h1>
              <p>按项目整理数据、研究记录和报告。</p>
            </div>
            <button
              type="button"
              className="product-primary-action"
              onClick={() => setCreateOpen(true)}
            >
              新建项目
            </button>
          </header>
          <EmptyOrError
            state={state}
            error={error}
            onRetry={retry}
            loading={
              projects.length ? <p role="status" className="product-loading">正在更新项目列表…</p> : <RouteLoading
                embedded
                section="项目研究"
                variant="overview"
              />
            }
          />
          {operation.pending && !dialog ? <p className="catalog-notice" role="status">正在更新项目…</p> : null}
          {operation.uncertain && !dialog ? <div className="project-operation-recovery" role="status"><p>{mutationError}</p><button type="button" className="product-secondary-action" disabled={busy} onClick={recoverProjectList}>重新读取项目列表</button></div> : null}
          {mutationNotice ? (
            <p className="product-form-success catalog-notice" role="status">
              {mutationNotice}
            </p>
          ) : null}
          {manageError ? (
            <div className="product-state" role="alert">
              <p>{manageError}</p>
              <button type="button" className="product-secondary-action" onClick={dismissManageRoute}>
                返回项目列表
              </button>
            </div>
          ) : null}
          {(state === "ready" || projects.length > 0) && (
            <>
              <div className="project-catalog-toolbar">
                <label htmlFor="project-catalog-search">
                  搜索项目、描述或标签
                </label>
                <input
                  id="project-catalog-search"
                  type="search"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="例如：钙钛矿、XRD 或轨迹"
                />
                {availableTags.length > 0 ? (
                  <label
                    className="project-catalog-tag-filter"
                    htmlFor="project-catalog-tag-filter"
                  >
                    标签
                    <select
                      id="project-catalog-tag-filter"
                      value={tagFilter}
                      onChange={(event) => setTagFilter(event.target.value)}
                    >
                      <option value="">全部标签</option>
                      {availableTags.map((tag) => (
                        <option key={tag} value={tag}>
                          {tag}
                        </option>
                      ))}
                    </select>
                  </label>
                ) : null}
                <div className="project-catalog-controls">
                  <div
                    className="segmented-control"
                    role="group"
                    aria-label="项目状态"
                  >
                    {(["active", "archived", "trashed", "all"] as const).map(
                      (value) => (
                        <button
                          key={value}
                          type="button"
                          aria-pressed={statusFilter === value}
                          onClick={() => setStatusFilter(value)}
                        >
                          {value === "active"
                            ? "当前"
                            : value === "archived"
                              ? "已归档"
                              : value === "trashed"
                                ? "回收站"
                                : "全部"}
                        </button>
                      ),
                    )}
                  </div>
                  {hasSelectableProjects ? (
                    <button
                      type="button"
                      className="product-secondary-action"
                      aria-pressed={selectionMode}
                      onClick={() => {
                        setSelectionMode((value) => !value);
                        setSelectedIds(new Set());
                      }}
                    >
                      {selectionMode ? "退出选择" : "选择"}
                    </button>
                  ) : null}
                  <span role="status" aria-live="polite">
                    {filteredProjects.length} 个项目
                  </span>
                </div>
              </div>
              {selectionMode ? (
                <div
                  className="batch-action-bar"
                  role="region"
                  aria-label="批量项目操作"
                >
                  <strong>{selectedIds.size} 个已选择</strong>
                  <button
                    type="button"
                    className="product-link-button"
                    onClick={() => setSelectedIds(new Set(selectableIds))}
                  >
                    选择当前结果
                  </button>
                  {statusFilter === "trashed" ? (
                    <button
                      type="button"
                      className="product-secondary-action"
                      disabled={!selectedIds.size || busy || operation.uncertain}
                      onClick={() => void applyBatch("restore")}
                    >
                      恢复
                    </button>
                  ) : (
                    <>
                      <button
                        type="button"
                        className="product-secondary-action"
                        disabled={!selectedIds.size || busy || operation.uncertain}
                        onClick={() => void applyBatch("pin")}
                      >
                        列表置顶
                      </button>
                      <button
                        type="button"
                        className="product-link-button"
                        disabled={!selectedIds.size || busy || operation.uncertain}
                        onClick={() => void applyBatch("unpin")}
                      >
                        取消列表置顶
                      </button>
                      <button
                        type="button"
                        className="product-secondary-action"
                        disabled={
                          !selectedIds.size ||
                          busy || operation.uncertain ||
                          statusFilter === "archived"
                        }
                        onClick={() => void applyBatch("archive")}
                      >
                        归档
                      </button>
                      <button
                        type="button"
                        className="product-danger-action"
                        disabled={!selectedIds.size || busy || operation.uncertain}
                        onClick={requestProjectBulkTrash}
                      >
                        移入回收站
                      </button>
                    </>
                  )}
                  <button
                    type="button"
                    className="product-link-button"
                    onClick={() => {
                      setSelectedIds(new Set());
                      setSelectionMode(false);
                    }}
                  >
                    取消
                  </button>
                </div>
              ) : null}
              {mutationError && !operation.uncertain && !dialog ? (
                <p className="product-form-error catalog-error" role="alert">
                  {mutationError}
                </p>
              ) : null}
              {projectBulkTrashTargets ? (
                <ProjectBulkTrashDialog
                  items={projectBulkTrashTargets}
                  preview={projectBulkPreview}
                  busy={busy}
                  error={mutationError}
                  onClose={() => {
                    setProjectBulkTrashTargets(null);
                  }}
                  onConfirm={confirmProjectBulkTrash}
                />
              ) : null}
              {catalogProjects.length > 0 && (
                <section
                  className="project-catalog-section"
                  aria-label="项目列表"
                >
                  {renderProjects(catalogProjects)}
                </section>
              )}
              {filteredProjects.length === 0 && (
                <div className="product-state">
                  <h2>{projects.length ? "没有匹配的项目" : "还没有项目"}</h2>
                  <p>
                    {!projects.length
                      ? "新建项目后，即可上传材料数据并开始研究。"
                      : query.trim() || tagFilter
                        ? "当前搜索与筛选条件下没有项目。试试其他名称、描述或标签。"
                        : statusFilter === "archived"
                          ? "当前没有已归档项目。"
                          : statusFilter === "trashed"
                            ? "回收站为空。"
                            : "当前没有活跃项目，可查看全部项目或新建项目。"}
                  </p>
                  {query.trim() || tagFilter || statusFilter !== "active" ? (
                    <button
                      type="button"
                      className="product-secondary-action"
                      onClick={() => {
                        setQuery("");
                        setTagFilter("");
                        setStatusFilter("active");
                      }}
                    >
                      清除搜索与筛选
                    </button>
                  ) : null}
                </div>
              )}
            </>
          )}
          {createOpen ? (
            <ProjectCreateDialog
              onClose={() => setCreateOpen(false)}
              onCreated={(project) =>
                setProjects((current) => [project, ...current.filter((item) => item.id !== project.id)])
              }
            />
          ) : null}
          {dialog ? (
            <ProjectEditDialog
              project={dialog.project}
              mode={dialog.mode}
              returnFocus={dialog.returnFocus}
              operation={operation}
              onReload={recoverProjectList}
              reading={state === "loading"}
              readError={state === "error" ? error : ""}
              onClose={closeProjectDialog}
              onUpdated={updateLocal}
              onDeleted={(projectId) =>
                setProjects((current) =>
                  current.filter(
                    (project) =>
                      (project.projectId || project.id) !== projectId,
                  ),
                )
              }
            />
          ) : null}
        </section>
      </ProductShell>
    </RequireProductAuth>
  );
}

function OverviewRow({ href, title, children }: { href: string; title: string; children: ReactNode }) {
  const disclosure = useClampedTitle(title, true);
  return <>
    <Link className="project-list-row overview-row" href={href} {...disclosure.events}>
      <div>
        <strong ref={disclosure.titleRef}>{title}</strong>
        {children}
      </div>
      <span aria-hidden="true">→</span>
    </Link>
    {disclosure.tooltip}
  </>;
}

function overviewRunTime(value?: string | null) {
  if (!value) return null;
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return null;
  return { iso: date.toISOString(), label: date.toLocaleString("zh-CN", {
    year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false,
  }) };
}

export function ProjectOverviewPage({ projectId }: { projectId: string }) {
  const { history, state, error, retry } = useProject(projectId);
  const canWriteProject = projectRoleAllows(history?.project.role, "write");
  const datasets = history?.datasets.filter((dataset) => !["archived", "trashed"].includes(dataset.status.toLowerCase())) ?? [];
  const runs = [...(history?.analyses ?? [])].sort((a, b) =>
    (Date.parse(b.createdAt || "") || 0) - (Date.parse(a.createdAt || "") || 0),
  ).slice(0, 5);
  const description = history?.project.description?.trim();
  return (
    <RequireProductAuth>
      <ProductShell projectId={projectId}>
        <section className="document-page project-overview" aria-label={history ? `${productProjectName(history.project.name)}的项目概览` : "项目概览"}>
          <EmptyOrError
            state={state}
            error={error}
            onRetry={retry}
            loading={
              history ? <p role="status">正在更新项目概览…</p> : <RouteLoading embedded section="项目概览" variant="data" />
            }
          />
          {history && (
            <>
              <header className="project-overview-header">
                <h1>项目概览</h1>
                {description ? description.length > 140 ? <details className="overview-description" key={`${projectId}:${description}`}>
                  <summary>项目说明</summary>
                  <p>{description}</p>
                </details> : <p className="overview-description">{description}</p> : null}
                <div className="product-row-actions">
                  <Link
                    className="product-primary-action"
                    href={`/projects/${projectId}/research`}
                  >
                    {canWriteProject ? "继续研究" : "查看研究记录"}
                  </Link>
                  <Link
                    className="product-secondary-action"
                    href={`/projects/${projectId}/data`}
                  >
                    查看数据
                  </Link>
                </div>
              </header>
              <div className="overview-columns">
                <section>
                  <div className="product-section-heading">
                    <h2>当前数据</h2>
                    <Link href={`/projects/${projectId}/data`}>全部数据</Link>
                  </div>
                  {datasets.length ? (
                    datasets.slice(0, 5).map((dataset) => (
                      <OverviewRow
                        key={dataset.datasetId}
                        href={`/projects/${projectId}/data?dataset=${encodeURIComponent(dataset.datasetId)}`}
                        title={dataset.name.trim() || "未命名数据"}
                      >
                          <p>
                            {dataset.import.fileCount} 个文件
                            {dataset.profile?.rowCount != null ? ` · ${dataset.profile.rowCount.toLocaleString("zh-CN")} 行` : dataset.profile?.objectCount != null ? ` · ${dataset.profile.objectCount.toLocaleString("zh-CN")} 个对象` : ""}
                          </p>
                      </OverviewRow>
                    ))
                  ) : (
                    <div className="product-empty-inline">
                      <p>暂无当前数据。</p>
                      {canWriteProject ? (
                        <Link href={`/projects/${projectId}/datasets/new`}>
                          上传数据 →
                        </Link>
                      ) : null}
                    </div>
                  )}
                </section>
                <section>
                  <div className="product-section-heading">
                    <h2>最近研究</h2>
                    <Link href={`/projects/${projectId}/research`}>
                      研究记录
                    </Link>
                  </div>
                  {runs.length ? (
                    runs.map((run) => {
                      const sources = researchRunSourceDatasets(run, history.datasets);
                      const time = overviewRunTime(run.createdAt);
                      return <OverviewRow
                        key={run.jobId}
                        href={projectHistoryRunHref(projectId, run)}
                        title={run.userQuestion?.trim() || researchRunTitle(run)}
                      >
                        <SourceDatasetList sources={sources} />
                        {run.sourceDatasetIds !== undefined && !sources.length ? <p>来源待核实</p> : null}
                        <p className="overview-run-meta"><span>{researchRunStatusLabel(run)}</span>{time ? <time dateTime={time.iso}>{time.label}</time> : null}</p>
                      </OverviewRow>;
                    })
                  ) : (
                    <div className="product-empty-inline">
                      <p>
                        {canWriteProject
                          ? "上传数据后，在这里开始材料分析。"
                          : "这个项目还没有研究记录。"}
                      </p>
                      {canWriteProject ? (
                        <Link href={`/projects/${projectId}/research`}>
                          进入研究 →
                        </Link>
                      ) : null}
                    </div>
                  )}
                </section>
              </div>
            </>
          )}
        </section>
      </ProductShell>
    </RequireProductAuth>
  );
}

function productProjectName(name: string | null | undefined) {
  const value = String(name || "").trim();
  const acceptanceName = value.match(
    /^current\s+acceptance\s+(.+?)\s+\d{10,}$/iu,
  );
  return (
    (acceptanceName
      ? acceptanceName[1]
      : value.replace(/^current\s+acceptance\s+/i, "")
    ).trim() || "材料研究项目"
  );
}

function sourceTypeLabel(objectType: string) {
  return (
    (
      {
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
      } as Record<string, string>
    )[objectType] || objectType
  );
}

export { DependencyImpactEntry, dependencyDisplayLabel, EmptyOrError, productProjectName, sourceTypeLabel, useProject };
export type { LoadState };
