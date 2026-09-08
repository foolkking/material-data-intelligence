"use client";

import { ProductLink as Link } from "../../app/components/ProductNavigation";
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
import { ProductShell, RequireProductAuth } from "../../app/components/ProductShell";
import {
  LazyScientificObjectViewer,
  LazyScientificSourceViewer,
} from "../../app/components/LazyScientificViewers";
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

type LoadState = "loading" | "ready" | "error";

function DependencyImpactEntry({
  item,
}: {
  item: { label: string; count: number; href?: string };
}) {
  return (
    <>
      {item.href ? <Link href={item.href}>{item.label}</Link> : item.label}：
      {item.count}
    </>
  );
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
  useEffect(() => {
    let active = true;
    void listProjects()
      .then((items) => {
        if (active) {
          setProjects(items);
          setState("ready");
        }
      })
      .catch((reason) => {
        if (active) {
          setError(reason instanceof Error ? reason.message : "加载失败");
          setState("error");
        }
      });
    return () => {
      active = false;
    };
  }, []);
  return { projects, setProjects, state, error };
}

function useProject(projectId: string) {
  const [history, setHistory] = useState<ProjectHistory | null>(() => getCachedProjectHistory(projectId));
  const [state, setState] = useState<LoadState>(() => getCachedProjectHistory(projectId) ? "ready" : "loading");
  const [error, setError] = useState("");
  const [loadAttempt, setLoadAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    setError("");
    const cached = getCachedProjectHistory(projectId);
    if (cached) {
      setHistory(cached);
      setState("ready");
      return () => {
        active = false;
      };
    }
    setState("loading");
    // ProductShell prefetches this ledger on navigation intent. Reuse the
    // shared in-flight/warm request so switching project surfaces does not
    // discard the shell and wait on an avoidable duplicate fetch.
    void getProjectHistory(projectId)
      .then((item) => {
        if (active) {
          setHistory(item);
          setState("ready");
        }
      })
      .catch((reason) => {
        if (active) {
          setError(reason instanceof Error ? reason.message : "项目加载失败");
          setState("error");
        }
      });
    return () => {
      active = false;
    };
  }, [projectId, loadAttempt]);
  return { history, setHistory, state, error, retry: () => setLoadAttempt((attempt) => attempt + 1) };
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

function ProjectCreateDialog({
  onClose,
  onCreated,
  returnFocus,
}: {
  onClose: () => void;
  onCreated: (project: ProjectSummary) => void;
  returnFocus?: HTMLElement | null;
}) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [created, setCreated] = useState<ProjectSummary | null>(null);
  async function submit() {
    if (!name.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      const base = await createProject(name.trim());
      let result = base;
      if (description.trim()) {
        try {
          result = await updateProject(base.projectId || base.id, {
            description: description.trim(),
          });
        } catch {
          setError("项目已创建，但研究说明暂未保存。可稍后从项目管理中补充。");
        }
      }
      setCreated(result);
      onCreated(result);
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "项目创建失败，请重试。",
      );
    } finally {
      setBusy(false);
    }
  }
  const projectId = created?.projectId || created?.id;
  return (
    <ProductModal
      title={created ? "项目已创建" : "新建研究项目"}
      description={
        created
          ? "下一步可直接上传数据，或先进入项目研究。"
          : "项目会保存数据、研究对话、分析结果和报告。"
      }
      onClose={onClose}
      returnFocus={returnFocus}
      footer={
        created ? (
          <>
            <button
              type="button"
              className="product-secondary-action"
              onClick={onClose}
            >
              稍后处理
            </button>
            <Link
              className="product-primary-action"
              href={`/projects/${projectId}/datasets/new`}
            >
              上传数据
            </Link>
          </>
        ) : (
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
              onClick={() => void submit()}
            >
              {busy ? "正在创建…" : "创建项目"}
            </button>
          </>
        )
      }
    >
      {created ? (
        <div className="project-created-state">
          <strong>{created.name}</strong>
          <p>
            研究边界已经建立。上传完成后可直接在 Data Viewer 查看，并从 Research
            提问。
          </p>
          {error ? (
            <p className="product-form-error" role="status">
              {error}
            </p>
          ) : null}
          <Link href={`/projects/${projectId}/research`}>先进入研究 →</Link>
        </div>
      ) : (
        <div className="product-form-grid">
          <label htmlFor="new-project-name">项目名称</label>
          <input
            id="new-project-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void submit();
              }
            }}
            placeholder="例如：钙钛矿稳定性研究"
            required
          />
          <label htmlFor="new-project-description">
            研究说明 <span>可选</span>
          </label>
          <textarea
            id="new-project-description"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="记录材料体系、数据来源或当前研究目标"
            rows={4}
          />
          {error ? (
            <p className="product-form-error" role="alert">
              {error}
            </p>
          ) : null}
        </div>
      )}
    </ProductModal>
  );
}

function ProjectEditDialog({
  project,
  mode,
  onClose,
  onUpdated,
  onDeleted,
}: {
  project: ProjectSummary;
  mode: "edit" | "trash" | "delete";
  onClose: () => void;
  onUpdated: (project: ProjectSummary) => void;
  onDeleted: (projectId: string) => void;
}) {
  const projectId = project.projectId || project.id;
  const [name, setName] = useState(project.name);
  const [description, setDescription] = useState(project.description || "");
  const [tags, setTags] = useState((project.tags || []).join(", "));
  const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [impact, setImpact] = useState<DependencyImpact | null>(null);
  useEffect(() => {
    if (mode !== "delete" && mode !== "trash") return;
    void getProjectDependencyImpact(projectId)
      .then(setImpact)
      .catch(() => setImpact(null));
  }, [mode, projectId]);
  async function save() {
    if (!name.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      onUpdated(
        await updateProject(projectId, {
          name: name.trim(),
          description: description.trim(),
          tags: tags
            .split(",")
            .map((value) => value.trim())
            .filter(Boolean)
            .slice(0, 12),
        }),
      );
      onClose();
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "项目更新失败，请重试。",
      );
    } finally {
      setBusy(false);
    }
  }
  async function remove() {
    if (confirmation !== project.name || busy) return;
    setBusy(true);
    setError("");
    try {
      await deleteEmptyProject(projectId);
      onDeleted(projectId);
      onClose();
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "项目包含数据或研究记录，请改为归档。",
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
      onUpdated(await updateProject(projectId, { lifecycle: "TRASHED" }));
      onClose();
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "项目暂时无法移入回收站。",
      );
    } finally {
      setBusy(false);
    }
  }
  if (mode === "trash")
    return (
      <ProductModal
        title="将项目移入回收站"
        description="项目会从当前工作流中移除，但受保护的数据、研究结果和报告仍保留，可从回收站恢复。"
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
              <p>历史研究和科学 provenance 不会被删除。</p>
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
        title="删除空项目"
        description="仅完全没有数据、研究记录与报告的项目可被永久删除。"
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
              disabled={busy || confirmation !== project.name}
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
      description="名称和研究说明会在 Console、项目列表和研究上下文中同步显示。"
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
        <label htmlFor="edit-project-name">项目名称</label>
        <input
          id="edit-project-name"
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
          标签只用于整理项目，不会进入科学分析上下文或改变数据权威。
        </p>
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
  impacts,
  busy,
  error,
  onClose,
  onConfirm,
}: {
  items: ProjectSummary[];
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
          已选择 <strong>{items.length}</strong> 个项目，服务器报告共{" "}
          <strong>{totalDependencies}</strong> 项受保护依赖。
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
              <p>未发现已持久化的科学依赖。</p>
            )}
            <p>项目会从新的工作发现中移除；历史研究和 exact source provenance 仍可访问。</p>
          </div>
        ) : (
          <p role="status">正在检查 {items.length} 个项目的依赖影响…</p>
        )}
        {error ? <p className="product-form-error" role="alert">{error}</p> : null}
      </div>
    </ProductModal>
  );
}

export function ConsolePage() {
  const { projects, setProjects, state, error } = useProjects();
  const [preview, setPreview] = useState<ProjectSummary | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [createTrigger, setCreateTrigger] = useState<HTMLElement | null>(null);
  const activeProjects = projects.filter(
    (project) => project.status !== "archived" && project.status !== "trashed",
  );
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
      if (event.key === "Escape") closePreview();
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
            <header className="product-page-heading">
              <div>
                <p className="product-kicker">控制台</p>
                <h1>继续你的材料研究</h1>
                <p>回到最近的项目、数据和分析报告。</p>
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
                <Link
                  className="product-secondary-action"
                  href="/console?settings=models"
                >
                  模型设置
                </Link>
              </div>
            </header>
            <EmptyOrError state={state} error={error} />
            {state === "ready" && activeProjects.length === 0 && (
              <div className="product-state">
                <h2>创建第一个项目</h2>
                <p>
                  项目会保存数据、研究过程与分析报告。创建后可直接上传真实材料数据。
                </p>
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
              </div>
            )}
            {activeProjects.length > 0 && (
              <>
                <section className="continue-research">
                  <div>
                    <span className="product-kicker">继续研究</span>
                    <h2>{activeProjects[0].name}</h2>
                    <p>
                      {activeProjects[0].description ||
                        "继续查看项目数据，或提出新的材料科学问题。"}
                    </p>
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
                    <h2>最近项目</h2>
                    <Link href="/projects">查看全部</Link>
                  </div>
                  <div className="project-list">
                    {activeProjects.slice(0, 6).map((project) => (
                      <ManagedObjectRow
                        key={project.id}
                        href={`/projects/${project.projectId || project.id}`}
                        title={project.name}
                        description={project.description || "材料研究项目"}
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
                setProjects((current) => [project, ...current])
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
  useEffect(() => {
    const controller = new AbortController();
    setState("loading");
    setDataset(null);
    setResource(null);
    setResources([]);
    void getProjectHistory(projectId)
      .then((history) => {
        const firstDataset = history.datasets[0];
        if (!firstDataset) return null;
        setDataset(firstDataset);
        return getDatasetSourceResources(
          firstDataset.datasetId,
          controller.signal,
        );
      })
      .then((resources) => {
        if (controller.signal.aborted) return;
        setResources(resources || []);
        setResource(resources?.[0] || null);
        setState("ready");
      })
      .catch(() => {
        if (!controller.signal.aborted) setState("error");
      });
    return () => controller.abort();
  }, [projectId, loadAttempt]);
  return (
    <aside className="quick-preview" aria-label="数据快速查看">
      <header className="quick-preview-header">
        <div>
          <p className="product-kicker">快速查看</p>
          <h2>{project.name}</h2>
          <p>从最近的数据开始浏览科学对象。</p>
        </div>
        <button type="button" onClick={onClose} aria-label="关闭快速查看">
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
            <p>项目数据仍然保留；可以在当前快速查看面板重试，或打开项目数据页继续检查。</p>
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
            />
          </>
        ) : null}
        {state === "ready" && dataset && !resource ? (
          <div className="product-state">
            <h3>
              {Number(dataset.import.fileCount || 0) === 0
                ? "项目还没有科学数据"
                : "当前数据没有可预览的科学对象"}
            </h3>
            <p>
              {Number(dataset.import.fileCount || 0) === 0
                ? "上传受支持的源文件后，可以在这里快速查看科学对象。"
                : "数据记录仍保留；请打开项目数据页检查来源、解析状态与恢复操作。"}
            </p>
          </div>
        ) : null}
        {state === "ready" && !dataset ? (
          <div className="product-state">
            <h3>项目还没有数据</h3>
            <p>上传数据后，可以在这里快速查看科学对象。</p>
          </div>
        ) : null}
      </div>
      <Link
        className="product-primary-action quick-preview-open"
        href={`/projects/${projectId}/data`}
      >
        打开项目数据
      </Link>
    </aside>
  );
}

export function ProjectsPage({
  manageProjectId = "",
}: { manageProjectId?: string } = {}) {
  const { projects, setProjects, state, error } = useProjects();
  const manageId = manageProjectId;
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
  } | null>(null);
  const [projectBulkTrashTargets, setProjectBulkTrashTargets] = useState<
    ProjectSummary[] | null
  >(null);
  const [projectBulkTrashImpacts, setProjectBulkTrashImpacts] = useState<
    DependencyImpact[] | null
  >(null);
  const [mutationError, setMutationError] = useState("");
  const [mutationNotice, setMutationNotice] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    if (!manageId || state !== "ready" || dialog) return;
    const project = projects.find(
      (item) => (item.projectId || item.id) === manageId,
    );
    if (project) setDialog({ project, mode: "edit" });
  }, [dialog, manageId, projects, state]);
  useEffect(() => {
    if (!projectBulkTrashTargets) {
      setProjectBulkTrashImpacts(null);
      return;
    }
    let active = true;
    setProjectBulkTrashImpacts(null);
    void Promise.all(
      projectBulkTrashTargets.map((project) =>
        getProjectDependencyImpact(project.projectId || project.id),
      ),
    )
      .then((impacts) => {
        if (active) setProjectBulkTrashImpacts(impacts);
      })
      .catch(() => {
        if (active) setProjectBulkTrashImpacts(null);
      });
    return () => {
      active = false;
    };
  }, [projectBulkTrashTargets]);
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
          `${project.name} ${project.description || ""}`
            .toLocaleLowerCase()
            .includes(normalized))
      );
    });
  }, [projects, query, statusFilter, tagFilter]);
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
  const caseProjects = filteredProjects
    .filter((project) => /^Case\s+\d+/i.test(project.name))
    .sort(byCatalogName);
  const phaseProjects = filteredProjects
    .filter((project) => /^Phase\s+\d+/i.test(project.name))
    .sort(byCatalogName);
  const otherProjects = filteredProjects
    .filter(
      (project) =>
        !/^Case\s+\d+/i.test(project.name) &&
        !/^Phase\s+\d+/i.test(project.name),
    )
    .sort(byCatalogName);
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
    setBusy(true);
    setMutationError("");
    setMutationNotice("");
    try {
      updateLocal(
        await updateProject(project.projectId || project.id, { archived }),
      );
    } catch (reason) {
      setMutationError(
        reason instanceof Error ? reason.message : "项目状态更新失败。",
      );
    } finally {
      setBusy(false);
    }
  }
  async function restoreProject(project: ProjectSummary) {
    setBusy(true);
    setMutationError("");
    setMutationNotice("");
    try {
      updateLocal(
        await updateProject(project.projectId || project.id, {
          archived: false,
        }),
      );
    } catch (reason) {
      setMutationError(
        reason instanceof Error ? reason.message : "项目恢复失败。",
      );
    } finally {
      setBusy(false);
    }
  }
  async function setPinned(project: ProjectSummary, pinned: boolean) {
    if (busy) return;
    setBusy(true);
    setMutationError("");
    setMutationNotice("");
    try {
      updateLocal(
        await updateProject(project.projectId || project.id, { pinned }),
      );
    } catch (reason) {
      setMutationError(
        reason instanceof Error ? reason.message : "项目固定状态更新失败。",
      );
    } finally {
      setBusy(false);
    }
  }
  async function applyBatch(action: "archive" | "trash" | "restore" | "pin" | "unpin") {
    if (!selectedIds.size || busy) return;
    setBusy(true);
    setMutationError("");
    setMutationNotice("");
    try {
      const ids = Array.from(selectedIds);
      await bulkProjectAction(ids, action);
      setProjects(await listProjects());
      setSelectedIds(new Set());
      setSelectionMode(false);
    } catch (reason) {
      setMutationError(
        reason instanceof Error ? reason.message : "批量操作失败。",
      );
    } finally {
      setBusy(false);
    }
  }
  function requestProjectBulkTrash() {
    const targets = filteredProjects.filter((project) =>
      selectedIds.has(project.projectId || project.id),
    );
    if (targets.length) {
      setMutationError("");
      setProjectBulkTrashTargets(targets);
    }
  }
  function confirmProjectBulkTrash() {
    if (
      !projectBulkTrashTargets ||
      !projectBulkTrashImpacts ||
      projectBulkTrashImpacts.length !== projectBulkTrashTargets.length
    ) {
      return;
    }
    setProjectBulkTrashTargets(null);
    setProjectBulkTrashImpacts(null);
    void applyBatch("trash");
  }
  async function exportProject(project: ProjectSummary) {
    if (busy) return;
    setBusy(true);
    setMutationError("");
    setMutationNotice("");
    try {
      const manifest = await getProjectExportManifest(project.projectId || project.id);
      const blob = new Blob([JSON.stringify(manifest, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${(project.name || "project").replace(/[^\w\u4e00-\u9fff.-]+/gu, "-").slice(0, 80) || "project"}-provenance.json`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
      setMutationNotice(`已导出“${project.name}”的有界复现清单；科学源文件仍由原始存储负责。`);
    } catch (reason) {
      setMutationError(reason instanceof Error ? reason.message : "项目清单导出失败。");
    } finally {
      setBusy(false);
    }
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
          description={
            project.tags?.length
              ? `${project.description || "查看数据、研究过程与分析报告"} · ${project.tags.join(" · ")}`
              : project.description || "查看数据、研究过程与分析报告"
          }
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
          actions={actionsFor(project)}
          selectionMode={selectionMode}
          selectable={projectRoleAllows(project.role, "write")}
          selected={selectedIds.has(project.projectId || project.id)}
          onSelectedChange={(selected) => toggleSelected(project, selected)}
        />
      ))}
    </div>
  );
  const selectableIds = filteredProjects
    .filter((project) => projectRoleAllows(project.role, "write"))
    .map((project) => project.projectId || project.id);
  return (
    <RequireProductAuth>
      <ProductShell>
        <section className="document-page">
          <header className="product-page-heading row">
            <div>
              <p className="product-kicker">项目</p>
              <h1>材料研究项目</h1>
              <p>项目是数据、研究过程和分析报告的长期边界。</p>
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
            loading={
              <RouteLoading
                embedded
                section="项目研究"
                variant="overview"
              />
            }
          />
          {state === "ready" && (
            <>
              <div className="project-catalog-toolbar">
                <label htmlFor="project-catalog-search">
                  搜索项目、Case 或科学能力
                </label>
                <input
                  id="project-catalog-search"
                  type="search"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="例如：Phase 10、XRD、轨迹或 Q-PHONON-001"
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
                      disabled={!selectedIds.size || busy}
                      onClick={() => void applyBatch("restore")}
                    >
                      恢复
                    </button>
                  ) : (
                    <>
                      <button
                        type="button"
                        className="product-secondary-action"
                        disabled={!selectedIds.size || busy}
                        onClick={() => void applyBatch("pin")}
                      >
                        列表置顶
                      </button>
                      <button
                        type="button"
                        className="product-link-button"
                        disabled={!selectedIds.size || busy}
                        onClick={() => void applyBatch("unpin")}
                      >
                        取消列表置顶
                      </button>
                      <button
                        type="button"
                        className="product-secondary-action"
                        disabled={
                          !selectedIds.size ||
                          busy ||
                          statusFilter === "archived"
                        }
                        onClick={() => void applyBatch("archive")}
                      >
                        归档
                      </button>
                      <button
                        type="button"
                        className="product-danger-action"
                        disabled={!selectedIds.size || busy}
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
              {mutationError ? (
                <p className="product-form-error catalog-error" role="alert">
                  {mutationError}
                </p>
              ) : null}
              {mutationNotice ? (
                <p className="product-form-success catalog-notice" role="status">
                  {mutationNotice}
                </p>
              ) : null}
              {projectBulkTrashTargets ? (
                <ProjectBulkTrashDialog
                  items={projectBulkTrashTargets}
                  impacts={projectBulkTrashImpacts}
                  busy={busy}
                  error={mutationError}
                  onClose={() => {
                    setProjectBulkTrashTargets(null);
                    setProjectBulkTrashImpacts(null);
                  }}
                  onConfirm={confirmProjectBulkTrash}
                />
              ) : null}
              {caseProjects.length > 0 && (
                <section
                  className="project-catalog-section"
                  aria-labelledby="case-projects-heading"
                >
                  <div className="product-section-heading">
                    <div>
                      <p className="product-kicker">生产验收数据</p>
                      <h2 id="case-projects-heading">16-case 项目</h2>
                    </div>
                    <span>{caseProjects.length} 个 Run</span>
                  </div>
                  {renderProjects(caseProjects)}
                </section>
              )}
              {phaseProjects.length > 0 && (
                <section
                  className="project-catalog-section"
                  aria-labelledby="phase-projects-heading"
                >
                  <div className="product-section-heading">
                    <div>
                      <p className="product-kicker">阶段能力记录</p>
                      <h2 id="phase-projects-heading">Phase 项目</h2>
                    </div>
                    <span>{phaseProjects.length} 个</span>
                  </div>
                  {renderProjects(phaseProjects)}
                </section>
              )}
              {otherProjects.length > 0 && (
                <section
                  className="project-catalog-section"
                  aria-labelledby="other-projects-heading"
                >
                  <div className="product-section-heading">
                    <h2 id="other-projects-heading">其他项目与历史记录</h2>
                    <span>{otherProjects.length} 个</span>
                  </div>
                  {renderProjects(otherProjects)}
                </section>
              )}
              {filteredProjects.length === 0 && (
                <div className="product-state">
                  <h2>没有匹配的项目</h2>
                  <p>
                    {statusFilter === "archived"
                      ? "当前没有已归档项目。"
                      : statusFilter === "trashed"
                        ? "回收站为空。"
                        : "可尝试搜索 Phase 10、Case 编号、Q-ID 或科学能力名称。"}
                  </p>
                </div>
              )}
            </>
          )}
          {createOpen ? (
            <ProjectCreateDialog
              onClose={() => setCreateOpen(false)}
              onCreated={(project) =>
                setProjects((current) => [project, ...current])
              }
            />
          ) : null}
          {dialog ? (
            <ProjectEditDialog
              project={dialog.project}
              mode={dialog.mode}
              onClose={() => setDialog(null)}
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

export function ProjectOverviewPage({ projectId }: { projectId: string }) {
  const { history, state, error, retry } = useProject(projectId);
  const canWriteProject = projectRoleAllows(history?.project.role, "write");
  return (
    <RequireProductAuth>
      <ProductShell projectId={projectId}>
        <section className="document-page">
          <EmptyOrError
            state={state}
            error={error}
            onRetry={retry}
            loading={
              <RouteLoading embedded section="项目数据" variant="data" />
            }
          />
          {history && (
            <>
              <header className="project-overview-header">
                <p className="product-kicker">项目概览</p>
                <h1>{productProjectName(history.project.name)}</h1>
                <p>
                  {history.project.description ||
                    "围绕项目数据继续研究，并保留每次分析的科学结果。"}
                </p>
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
                    <h2>项目数据</h2>
                    <Link href={`/projects/${projectId}/data`}>全部数据</Link>
                  </div>
                  {history.datasets.length ? (
                    history.datasets.slice(0, 5).map((dataset) => (
                      <Link
                        className="project-list-row"
                        key={dataset.datasetId}
                        href={`/projects/${projectId}/data?dataset=${dataset.datasetId}`}
                      >
                        <div>
                          <strong>{productProjectName(dataset.name)}</strong>
                          <p>
                            {dataset.import.fileCount} 个文件 ·{" "}
                            {dataset.profile?.rowCount ??
                              dataset.profile?.objectCount ??
                              "—"}{" "}
                            个记录
                          </p>
                        </div>
                        <span>查看 →</span>
                      </Link>
                    ))
                  ) : (
                    <div className="product-empty-inline">
                      <p>还没有项目数据。</p>
                      {canWriteProject ? (
                        <Link href={`/projects/${projectId}/datasets/new`}>
                          上传第一份数据 →
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
                  {history.analyses.length ? (
                    history.analyses.slice(0, 5).map((run) => (
                      <Link
                        className="project-list-row"
                        key={run.jobId}
                        href={projectHistoryRunHref(projectId, run)}
                      >
                        <div>
                          <strong>{researchRunTitle(run)}</strong>
                          <p>{researchRunStatusLabel(run)}</p>
                        </div>
                        <span>打开 →</span>
                      </Link>
                    ))
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

export { DependencyImpactEntry, EmptyOrError, productProjectName, sourceTypeLabel, useProject };
export type { LoadState };
