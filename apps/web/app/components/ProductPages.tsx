"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { bulkDatasetAction, bulkProjectAction, createProject, deleteEmptyDataset, deleteEmptyProject, getDatasetSourceResources, getProjectHistory, listProjects, updateDataset, updateProject, uploadDatasetFiles, type DatasetSourceResource, type ProjectHistory, type ProjectSummary } from "../lib/planner-api";
import { PHONON_BAND_SCHEMA_VERSION, PHONON_DOS_SCHEMA_VERSION } from "../lib/phononContract";
import { ProductShell, RequireProductAuth } from "./ProductShell";
import { ScientificSourceViewer } from "./ScientificViewerAdapter";
import { ManagedObjectRow, ProductModal, type ObjectAction } from "./ObjectManagement";
import type { WorkspaceSelectionContext } from "../lib/workspace-api";
import { researchRunTitle } from "../lib/research-display";
import { listScientificObjects, type ScientificObjectSummary } from "../lib/scientific-viewer-api";
import { ScientificObjectViewer } from "./scientific-viewer/ScientificObjectViewer";

type LoadState = "loading" | "ready" | "error";

function canManageProject(role?: string | null) {
  return role === "owner" || role === "admin" || role === "researcher";
}

function projectHistoryRunHref(projectId: string, run: ProjectHistory["analyses"][number]) {
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
  useEffect(() => { let active = true; void listProjects().then((items) => { if (active) { setProjects(items); setState("ready"); } }).catch((reason) => { if (active) { setError(reason instanceof Error ? reason.message : "加载失败"); setState("error"); } }); return () => { active = false; }; }, []);
  return { projects, setProjects, state, error };
}

function useProject(projectId: string) {
  const [history, setHistory] = useState<ProjectHistory | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState("");
  useEffect(() => { let active = true; setState("loading"); void getProjectHistory(projectId).then((item) => { if (active) { setHistory(item); setState("ready"); } }).catch((reason) => { if (active) { setError(reason instanceof Error ? reason.message : "项目加载失败"); setState("error"); } }); return () => { active = false; }; }, [projectId]);
  return { history, setHistory, state, error };
}

function EmptyOrError({ state, error }: { state: LoadState; error: string }) {
  if (state === "loading") return <div className="product-loading" role="status" aria-live="polite">正在加载研究内容…</div>;
  if (state === "error") return <div className="product-state" role="alert"><h2>暂时无法加载</h2><p>{error}</p></div>;
  return null;
}

function ProjectCreateDialog({ onClose, onCreated, returnFocus }: { onClose: () => void; onCreated: (project: ProjectSummary) => void; returnFocus?: HTMLElement | null }) {
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
          result = await updateProject(base.projectId || base.id, { description: description.trim() });
        } catch {
          setError("项目已创建，但研究说明暂未保存。可稍后从项目管理中补充。");
        }
      }
      setCreated(result);
      onCreated(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "项目创建失败，请重试。");
    } finally {
      setBusy(false);
    }
  }
  const projectId = created?.projectId || created?.id;
  return <ProductModal title={created ? "项目已创建" : "新建研究项目"} description={created ? "下一步可直接上传数据，或先进入项目研究。" : "项目会保存数据、研究对话、分析结果和报告。"} onClose={onClose} returnFocus={returnFocus} footer={created ? <><button type="button" className="product-secondary-action" onClick={onClose}>稍后处理</button><Link className="product-primary-action" href={`/projects/${projectId}/datasets/new`}>上传数据</Link></> : <><button type="button" className="product-secondary-action" onClick={onClose}>取消</button><button type="button" className="product-primary-action" disabled={busy || !name.trim()} onClick={() => void submit()}>{busy ? "正在创建…" : "创建项目"}</button></>}>
    {created ? <div className="project-created-state"><strong>{created.name}</strong><p>研究边界已经建立。上传完成后可直接在 Data Viewer 查看，并从 Research 提问。</p>{error ? <p className="product-form-error" role="status">{error}</p> : null}<Link href={`/projects/${projectId}/research`}>先进入研究 →</Link></div> : <div className="product-form-grid"><label htmlFor="new-project-name">项目名称</label><input id="new-project-name" value={name} onChange={(event) => setName(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); void submit(); } }} placeholder="例如：钙钛矿稳定性研究" required /><label htmlFor="new-project-description">研究说明 <span>可选</span></label><textarea id="new-project-description" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="记录材料体系、数据来源或当前研究目标" rows={4} />{error ? <p className="product-form-error" role="alert">{error}</p> : null}</div>}
  </ProductModal>;
}

function ProjectEditDialog({ project, mode, onClose, onUpdated, onDeleted }: { project: ProjectSummary; mode: "edit" | "delete"; onClose: () => void; onUpdated: (project: ProjectSummary) => void; onDeleted: (projectId: string) => void }) {
  const projectId = project.projectId || project.id;
  const [name, setName] = useState(project.name);
  const [description, setDescription] = useState(project.description || "");
  const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function save() {
    if (!name.trim() || busy) return;
    setBusy(true); setError("");
    try { onUpdated(await updateProject(projectId, { name: name.trim(), description: description.trim() })); onClose(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "项目更新失败，请重试。"); }
    finally { setBusy(false); }
  }
  async function remove() {
    if (confirmation !== project.name || busy) return;
    setBusy(true); setError("");
    try { await deleteEmptyProject(projectId); onDeleted(projectId); onClose(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "项目包含数据或研究记录，请改为归档。"); }
    finally { setBusy(false); }
  }
  if (mode === "delete") return <ProductModal title="删除空项目" description="仅完全没有数据、研究记录与报告的项目可被永久删除。" onClose={onClose} footer={<><button type="button" className="product-secondary-action" onClick={onClose}>取消</button><button type="button" className="product-danger-action" disabled={busy || confirmation !== project.name} onClick={() => void remove()}>{busy ? "正在删除…" : "永久删除"}</button></>}>
    <div className="product-form-grid danger-zone"><p>此操作不可撤销。输入项目名称 <strong>{project.name}</strong> 以确认。</p><label htmlFor="delete-project-confirmation">项目名称</label><input id="delete-project-confirmation" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); void remove(); } }} autoComplete="off" />{error ? <p className="product-form-error" role="alert">{error}</p> : null}</div>
  </ProductModal>;
  return <ProductModal title="编辑项目信息" description="名称和研究说明会在 Console、项目列表和研究上下文中同步显示。" onClose={onClose} footer={<><button type="button" className="product-secondary-action" onClick={onClose}>取消</button><button type="button" className="product-primary-action" disabled={busy || !name.trim()} onClick={() => void save()}>{busy ? "正在保存…" : "保存更改"}</button></>}>
    <div className="product-form-grid"><label htmlFor="edit-project-name">项目名称</label><input id="edit-project-name" value={name} onChange={(event) => setName(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); void save(); } }} /><label htmlFor="edit-project-description">研究说明</label><textarea id="edit-project-description" value={description} onChange={(event) => setDescription(event.target.value)} rows={4} />{error ? <p className="product-form-error" role="alert">{error}</p> : null}</div>
  </ProductModal>;
}

function projectNavigationActions(project: ProjectSummary): ObjectAction[] {
  const id = project.projectId || project.id;
  const actions: ObjectAction[] = [
    { label: "打开项目概览", href: `/projects/${id}` },
    { label: "查看数据", href: `/projects/${id}/data` },
    { label: "研究记录", href: `/projects/${id}/research` },
    { label: "查看报告", href: `/projects/${id}/reports` },
  ];
  if (canManageProject(project.role)) {
    actions.push({ label: "上传数据", href: `/projects/${id}/datasets/new` });
    actions.push({ label: "管理项目", href: `/projects?manage=${encodeURIComponent(id)}` });
  }
  return actions;
}

type ProjectDataset = ProjectHistory["datasets"][number];

function DatasetEditDialog({ dataset, mode, onClose, onUpdated, onDeleted }: { dataset: ProjectDataset; mode: "edit" | "delete"; onClose: () => void; onUpdated: (changes: { name: string; status: string }) => void; onDeleted: (datasetId: string) => void }) {
  const [name, setName] = useState(dataset.name);
  const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function save() {
    if (!name.trim() || busy) return;
    setBusy(true); setError("");
    try { const result = await updateDataset(dataset.datasetId, { name: name.trim() }); onUpdated({ name: result.name || name.trim(), status: result.status || dataset.status }); onClose(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "数据集更新失败，请重试。"); }
    finally { setBusy(false); }
  }
  async function remove() {
    if (confirmation !== dataset.name || busy) return;
    setBusy(true); setError("");
    try { await deleteEmptyDataset(dataset.datasetId); onDeleted(dataset.datasetId); onClose(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "数据集包含源文件或研究记录，请改为归档。"); }
    finally { setBusy(false); }
  }
  if (mode === "delete") return <ProductModal eyebrow="数据管理" title="删除空数据集" description="只有尚未包含源文件、语义档案和研究记录的数据集可以永久删除。" onClose={onClose} footer={<><button type="button" className="product-secondary-action" onClick={onClose}>取消</button><button type="button" className="product-danger-action" disabled={busy || confirmation !== dataset.name} onClick={() => void remove()}>{busy ? "正在删除…" : "永久删除"}</button></>}><div className="product-form-grid danger-zone"><p>输入数据集名称 <strong>{dataset.name}</strong> 以确认。</p><label htmlFor="delete-dataset-confirmation">数据集名称</label><input id="delete-dataset-confirmation" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); void remove(); } }} autoComplete="off" />{error ? <p className="product-form-error" role="alert">{error}</p> : null}</div></ProductModal>;
  return <ProductModal eyebrow="数据管理" title="重命名数据集" description="名称会同步到 Data Navigator、研究数据范围和报告来源。" onClose={onClose} footer={<><button type="button" className="product-secondary-action" onClick={onClose}>取消</button><button type="button" className="product-primary-action" disabled={busy || !name.trim()} onClick={() => void save()}>{busy ? "正在保存…" : "保存更改"}</button></>}><div className="product-form-grid"><label htmlFor="edit-dataset-name">数据集名称</label><input id="edit-dataset-name" value={name} onChange={(event) => setName(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); void save(); } }} />{error ? <p className="product-form-error" role="alert">{error}</p> : null}</div></ProductModal>;
}

export function ConsolePage() {
  const { projects, setProjects, state, error } = useProjects();
  const [preview, setPreview] = useState<ProjectSummary | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [createTrigger, setCreateTrigger] = useState<HTMLElement | null>(null);
  const activeProjects = projects.filter((project) => project.status !== "archived");
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
  useEffect(() => { if (!preview) return; const close = (event: KeyboardEvent) => { if (event.key === "Escape") closePreview(); }; document.addEventListener("keydown", close); return () => document.removeEventListener("keydown", close); }, [preview]);
  return <RequireProductAuth><ProductShell><section className={`console-page ${preview ? "with-preview" : ""}`}>
    <div className="console-content"><header className="product-page-heading"><div><p className="product-kicker">控制台</p><h1>继续你的材料研究</h1><p>回到最近的项目、数据和分析报告。</p></div><div className="product-row-actions"><button type="button" className="product-primary-action" onClick={(event) => { setCreateTrigger(event.currentTarget); setCreateOpen(true); }}>新建项目</button><button type="button" className="product-secondary-action" onClick={() => window.dispatchEvent(new CustomEvent("mdi:open-project-search"))}>搜索项目</button><Link className="product-secondary-action" href="/console?settings=models">模型设置</Link></div></header>
    <EmptyOrError state={state} error={error} />
    {state === "ready" && activeProjects.length === 0 && <div className="product-state"><h2>创建第一个项目</h2><p>项目会保存数据、研究过程与分析报告。创建后可直接上传真实材料数据。</p><button type="button" className="product-primary-action" onClick={(event) => { setCreateTrigger(event.currentTarget); setCreateOpen(true); }}>新建项目</button></div>}
    {activeProjects.length > 0 && <><section className="continue-research"><div><span className="product-kicker">继续研究</span><h2>{activeProjects[0].name}</h2><p>{activeProjects[0].description || "继续查看项目数据，或提出新的材料科学问题。"}</p></div><div className="product-row-actions"><Link className="product-primary-action" href={`/projects/${activeProjects[0].projectId || activeProjects[0].id}/research`}>继续研究</Link><button ref={triggerRef} className="product-secondary-action" onClick={() => setPreview(activeProjects[0])}>快速查看</button></div></section>
    <section className="product-section"><div className="product-section-heading"><h2>最近项目</h2><Link href="/projects">查看全部</Link></div><div className="project-list">{activeProjects.slice(0, 6).map((project) => <ManagedObjectRow key={project.id} href={`/projects/${project.projectId || project.id}`} title={project.name} description={project.description || "材料研究项目"} trailing="打开 →" actions={projectNavigationActions(project)} />)}</div></section></>}
    </div>{preview && <ProjectQuickPreview project={preview} onClose={closePreview} />}{createOpen ? <ProjectCreateDialog returnFocus={createTrigger} onClose={() => setCreateOpen(false)} onCreated={(project) => setProjects((current) => [project, ...current])} /> : null}
  </section></ProductShell></RequireProductAuth>;
}

function ProjectQuickPreview({ project, onClose }: { project: ProjectSummary; onClose: () => void }) {
  const projectId = project.projectId || project.id;
  const [dataset, setDataset] = useState<ProjectHistory["datasets"][number] | null>(null);
  const [resource, setResource] = useState<DatasetSourceResource | null>(null);
  const [resources, setResources] = useState<DatasetSourceResource[]>([]);
  const [state, setState] = useState<LoadState>("loading");
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
        return getDatasetSourceResources(firstDataset.datasetId, controller.signal);
      })
      .then((resources) => {
        if (controller.signal.aborted) return;
        setResources(resources || []);
        setResource(resources?.[0] || null);
        setState("ready");
      })
      .catch(() => { if (!controller.signal.aborted) setState("error"); });
    return () => controller.abort();
  }, [projectId]);
  return <aside className="quick-preview" aria-label="数据快速查看">
    <header className="quick-preview-header"><div><p className="product-kicker">快速查看</p><h2>{project.name}</h2><p>从最近的数据开始浏览科学对象。</p></div><button type="button" onClick={onClose} aria-label="关闭快速查看">×</button></header>
    <div className="quick-preview-viewer">
      {state === "loading" ? <div className="product-loading" role="status">正在加载项目数据…</div> : null}
      {state === "error" ? <div className="product-state" role="alert"><h3>暂时无法加载数据</h3><p>项目数据仍然保留，可以打开项目数据页重试。</p></div> : null}
      {state === "ready" && dataset && resource ? <><div className="quick-preview-resource"><strong>{productProjectName(dataset.name)}</strong><span>{sourceTypeLabel(resource.objectType)}</span></div><ScientificSourceViewer projectId={projectId} resource={resource} resources={resources} /></> : null}
      {state === "ready" && !dataset ? <div className="product-state"><h3>项目还没有数据</h3><p>上传数据后，可以在这里快速查看科学对象。</p></div> : null}
    </div>
    <Link className="product-primary-action quick-preview-open" href={`/projects/${projectId}/data`}>打开项目数据</Link>
  </aside>;
}

export function ProjectsPage({ manageProjectId = "" }: { manageProjectId?: string } = {}) {
  const { projects, setProjects, state, error } = useProjects();
  const manageId = manageProjectId;
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"active" | "archived" | "all">("active");
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [createOpen, setCreateOpen] = useState(false);
  const [dialog, setDialog] = useState<{ project: ProjectSummary; mode: "edit" | "delete" } | null>(null);
  const [mutationError, setMutationError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    if (!manageId || state !== "ready" || dialog) return;
    const project = projects.find((item) => (item.projectId || item.id) === manageId);
    if (project) setDialog({ project, mode: "edit" });
  }, [dialog, manageId, projects, state]);
  const filteredProjects = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase();
    return projects.filter((project) => {
      const statusMatches = statusFilter === "all" || (project.status === "archived" ? "archived" : "active") === statusFilter;
      return statusMatches && (!normalized || `${project.name} ${project.description || ""}`.toLocaleLowerCase().includes(normalized));
    });
  }, [projects, query, statusFilter]);
  const byCatalogName = (left: ProjectSummary, right: ProjectSummary) => left.name.localeCompare(right.name, "zh-CN", { numeric: true });
  const caseProjects = filteredProjects.filter((project) => /^Case\s+\d+/i.test(project.name)).sort(byCatalogName);
  const phaseProjects = filteredProjects.filter((project) => /^Phase\s+\d+/i.test(project.name)).sort(byCatalogName);
  const otherProjects = filteredProjects.filter((project) => !/^Case\s+\d+/i.test(project.name) && !/^Phase\s+\d+/i.test(project.name)).sort(byCatalogName);
  const hasSelectableProjects = projects.some((project) => canManageProject(project.role));
  const updateLocal = (next: ProjectSummary) => setProjects((current) => current.map((project) => (project.projectId || project.id) === (next.projectId || next.id) ? next : project));
  async function setArchived(project: ProjectSummary, archived: boolean) {
    setBusy(true); setMutationError("");
    try { updateLocal(await updateProject(project.projectId || project.id, { archived })); }
    catch (reason) { setMutationError(reason instanceof Error ? reason.message : "项目状态更新失败。"); }
    finally { setBusy(false); }
  }
  async function applyBatch(action: "archive" | "restore") {
    if (!selectedIds.size || busy) return;
    setBusy(true); setMutationError("");
    try {
      const ids = Array.from(selectedIds);
      await bulkProjectAction(ids, action);
      const archived = action === "archive";
      setProjects((current) => current.map((project) => ids.includes(project.projectId || project.id) ? { ...project, status: archived ? "archived" : "active" } : project));
      setSelectedIds(new Set()); setSelectionMode(false);
    } catch (reason) { setMutationError(reason instanceof Error ? reason.message : "批量操作失败。"); }
    finally { setBusy(false); }
  }
  function actionsFor(project: ProjectSummary): ObjectAction[] {
    const canWrite = canManageProject(project.role);
    const actions = projectNavigationActions(project).filter((action) => action.label !== "管理项目");
    if (!canWrite) return actions;
    actions.push({ label: "编辑项目信息", onSelect: () => setDialog({ project, mode: "edit" }) });
    actions.push({ label: project.status === "archived" ? "恢复项目" : "归档项目", onSelect: () => void setArchived(project, project.status !== "archived") });
    if (project.role === "owner") actions.push({ label: "删除空项目", destructive: true, onSelect: () => setDialog({ project, mode: "delete" }) });
    return actions;
  }
  const toggleSelected = (project: ProjectSummary, selected: boolean) => {
    const id = project.projectId || project.id;
    setSelectedIds((current) => { const next = new Set(current); if (selected) next.add(id); else next.delete(id); return next; });
  };
  const renderProjects = (items: ProjectSummary[]) => <div className="project-list large">{items.map((project) => <ManagedObjectRow key={project.id} href={`/projects/${project.projectId || project.id}`} title={project.name} description={project.description || "查看数据、研究过程与分析报告"} trailing={project.status === "archived" ? "已归档" : "打开项目 →"} actions={actionsFor(project)} selectionMode={selectionMode} selectable={canManageProject(project.role)} selected={selectedIds.has(project.projectId || project.id)} onSelectedChange={(selected) => toggleSelected(project, selected)} />)}</div>;
  const selectableIds = filteredProjects.filter((project) => canManageProject(project.role)).map((project) => project.projectId || project.id);
  return <RequireProductAuth><ProductShell><section className="document-page"><header className="product-page-heading row"><div><p className="product-kicker">项目</p><h1>材料研究项目</h1><p>项目是数据、研究过程和分析报告的长期边界。</p></div><button type="button" className="product-primary-action" onClick={() => setCreateOpen(true)}>新建项目</button></header><EmptyOrError state={state} error={error} />{state === "ready" && <><div className="project-catalog-toolbar"><label htmlFor="project-catalog-search">搜索项目、Case 或科学能力</label><input id="project-catalog-search" type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="例如：Phase 10、XRD、轨迹或 Q-PHONON-001" /><div className="project-catalog-controls"><div className="segmented-control" role="group" aria-label="项目状态">{(["active", "archived", "all"] as const).map((value) => <button key={value} type="button" aria-pressed={statusFilter === value} onClick={() => setStatusFilter(value)}>{value === "active" ? "当前" : value === "archived" ? "已归档" : "全部"}</button>)}</div>{hasSelectableProjects ? <button type="button" className="product-secondary-action" aria-pressed={selectionMode} onClick={() => { setSelectionMode((value) => !value); setSelectedIds(new Set()); }}>{selectionMode ? "退出选择" : "选择"}</button> : null}<span role="status" aria-live="polite">{filteredProjects.length} 个项目</span></div></div>{selectionMode ? <div className="batch-action-bar" role="region" aria-label="批量项目操作"><strong>{selectedIds.size} 个已选择</strong><button type="button" className="product-link-button" onClick={() => setSelectedIds(new Set(selectableIds))}>选择当前结果</button>{statusFilter !== "archived" ? <button type="button" className="product-secondary-action" disabled={!selectedIds.size || busy} onClick={() => void applyBatch("archive")}>归档</button> : null}{statusFilter !== "active" ? <button type="button" className="product-secondary-action" disabled={!selectedIds.size || busy} onClick={() => void applyBatch("restore")}>恢复</button> : null}<button type="button" className="product-link-button" onClick={() => { setSelectedIds(new Set()); setSelectionMode(false); }}>取消</button></div> : null}{mutationError ? <p className="product-form-error catalog-error" role="alert">{mutationError}</p> : null}{caseProjects.length > 0 && <section className="project-catalog-section" aria-labelledby="case-projects-heading"><div className="product-section-heading"><div><p className="product-kicker">生产验收数据</p><h2 id="case-projects-heading">16-case 项目</h2></div><span>{caseProjects.length} 个 Run</span></div>{renderProjects(caseProjects)}</section>}{phaseProjects.length > 0 && <section className="project-catalog-section" aria-labelledby="phase-projects-heading"><div className="product-section-heading"><div><p className="product-kicker">阶段能力记录</p><h2 id="phase-projects-heading">Phase 项目</h2></div><span>{phaseProjects.length} 个</span></div>{renderProjects(phaseProjects)}</section>}{otherProjects.length > 0 && <section className="project-catalog-section" aria-labelledby="other-projects-heading"><div className="product-section-heading"><h2 id="other-projects-heading">其他项目与历史记录</h2><span>{otherProjects.length} 个</span></div>{renderProjects(otherProjects)}</section>}{filteredProjects.length === 0 && <div className="product-state"><h2>没有匹配的项目</h2><p>{statusFilter === "archived" ? "当前没有已归档项目。" : "可尝试搜索 Phase 10、Case 编号、Q-ID 或科学能力名称。"}</p></div>}</>}{createOpen ? <ProjectCreateDialog onClose={() => setCreateOpen(false)} onCreated={(project) => setProjects((current) => [project, ...current])} /> : null}{dialog ? <ProjectEditDialog project={dialog.project} mode={dialog.mode} onClose={() => setDialog(null)} onUpdated={updateLocal} onDeleted={(projectId) => setProjects((current) => current.filter((project) => (project.projectId || project.id) !== projectId))} /> : null}</section></ProductShell></RequireProductAuth>;
}

export function ProjectOverviewPage({ projectId }: { projectId: string }) {
  const { history, state, error } = useProject(projectId);
  const canWriteProject = canManageProject(history?.project.role);
  return <RequireProductAuth><ProductShell projectId={projectId}><section className="document-page"><EmptyOrError state={state} error={error} />{history && <><header className="project-overview-header"><p className="product-kicker">项目概览</p><h1>{productProjectName(history.project.name)}</h1><p>{history.project.description || "围绕项目数据继续研究，并保留每次分析的科学结果。"}</p><div className="product-row-actions"><Link className="product-primary-action" href={`/projects/${projectId}/research`}>{canWriteProject ? "继续研究" : "查看研究记录"}</Link><Link className="product-secondary-action" href={`/projects/${projectId}/data`}>查看数据</Link></div></header><div className="overview-columns"><section><div className="product-section-heading"><h2>项目数据</h2><Link href={`/projects/${projectId}/data`}>全部数据</Link></div>{history.datasets.length ? history.datasets.slice(0, 5).map((dataset) => <Link className="project-list-row" key={dataset.datasetId} href={`/projects/${projectId}/data?dataset=${dataset.datasetId}`}><div><strong>{productProjectName(dataset.name)}</strong><p>{dataset.import.fileCount} 个文件 · {dataset.profile?.rowCount ?? dataset.profile?.objectCount ?? "—"} 个记录</p></div><span>查看 →</span></Link>) : <div className="product-empty-inline"><p>还没有项目数据。</p>{canWriteProject ? <Link href={`/projects/${projectId}/datasets/new`}>上传第一份数据 →</Link> : null}</div>}</section><section><div className="product-section-heading"><h2>最近研究</h2><Link href={`/projects/${projectId}/research`}>研究记录</Link></div>{history.analyses.length ? history.analyses.slice(0, 5).map((run) => <Link className="project-list-row" key={run.jobId} href={projectHistoryRunHref(projectId, run)}><div><strong>{researchRunTitle(run)}</strong><p>{run.status === "completed" ? "分析完成" : run.status === "partial_success" ? "部分完成" : "分析进行中"}</p></div><span>打开 →</span></Link>) : <div className="product-empty-inline"><p>{canWriteProject ? "上传数据后，在这里开始材料分析。" : "这个项目还没有研究记录。"}</p>{canWriteProject ? <Link href={`/projects/${projectId}/research`}>进入研究 →</Link> : null}</div>}</section></div></>}</section></ProductShell></RequireProductAuth>;
}

type DataKind = "table" | "structure" | "trajectory" | "xrd" | "electronic" | "phonon" | "volumetric" | "detected" | "generic";
function inferDataKind(dataset: ProjectHistory["datasets"][number]): DataKind {
  const name = dataset.name.toLowerCase();
  const resources = dataset.import.resources || [];
  const objectTypes = new Set(resources.map((item) => String(item.objectType || "").toLowerCase()));
  // Prefer validated normalized object types over filenames/profile text. In
  // particular, phonon band/DOS must never be routed to the electronic viewer.
  if (objectTypes.has("phononband") || objectTypes.has("phonondos") || objectTypes.has("phononeigenvector")) return "phonon";
  if (objectTypes.has("electronicband") || objectTypes.has("electronicdos")) return "electronic";
  if (objectTypes.has("trajectory")) return "trajectory";
  if (objectTypes.has("structure") || objectTypes.has("atoms")) return "structure";
  if (objectTypes.has("volumetricdata")) return "volumetric";
  if (name.includes("xrd")) return "xrd";
  const text = `${dataset.profile?.datasetType || ""} ${resources.map((item) => JSON.stringify(item)).join(" ")} ${name}`.toLowerCase();
  if (text.includes("trajectory") || text.includes("xyz")) return "trajectory";
  if (text.includes("structure") || text.includes("cif") || text.includes("poscar")) return "structure";
  if (text.includes("xrd")) return "xrd";
  if (text.includes("phonon")) return "phonon";
  if (text.includes("band") || text.includes("dos")) return "electronic";
  if (text.includes("volumetric") || text.includes("cube")) return "volumetric";
  if (text.includes("zip") || resources.length > 1) return "detected";
  if (dataset.profile?.rowCount) return "table";
  return "generic";
}

export function ProjectDataPage({ projectId, initialDatasetId = "", initialObjectId = "", initialObjectVersionId = "" }: { projectId: string; initialDatasetId?: string; initialObjectId?: string; initialObjectVersionId?: string }) {
  const queryDatasetId = initialDatasetId;
  const { history, setHistory, state, error } = useProject(projectId);
  const [selectedId, setSelectedId] = useState("");
  const [statusFilter, setStatusFilter] = useState<"active" | "archived">("active");
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedDatasetIds, setSelectedDatasetIds] = useState<Set<string>>(new Set());
  const [dialog, setDialog] = useState<{ dataset: ProjectDataset; mode: "edit" | "delete" } | null>(null);
  const [mutationError, setMutationError] = useState("");
  const [busy, setBusy] = useState(false);
  const [inspector, setInspector] = useState(false);
  const [scientificSelection, setScientificSelection] = useState<WorkspaceSelectionContext | null>(null);
  const [scientificObjects, setScientificObjects] = useState<ScientificObjectSummary[]>([]);
  const inspectorTriggerRef = useRef<HTMLElement | null>(null);
  const inspectorTriggerLabelRef = useRef<string | null>(null);
  const inspectorCloseRef = useRef<HTMLButtonElement | null>(null);
  const visibleDatasets = useMemo(() => (history?.datasets || []).filter((dataset) => statusFilter === "archived" ? dataset.status === "archived" : dataset.status !== "archived"), [history?.datasets, statusFilter]);
  useEffect(() => {
    const controller = new AbortController();
    void listScientificObjects(projectId, controller.signal, initialObjectId ? undefined : statusFilter === "archived" ? "ARCHIVED" : "ACTIVE").then((response) => setScientificObjects(response.items)).catch(() => setScientificObjects([]));
    return () => controller.abort();
  }, [initialObjectId, projectId, statusFilter]);
  useEffect(() => {
    if (selectedId && visibleDatasets.some((item) => item.datasetId === selectedId)) return;
    const requested = queryDatasetId && visibleDatasets.some((item) => item.datasetId === queryDatasetId) ? queryDatasetId : visibleDatasets[0]?.datasetId || "";
    setSelectedId(requested);
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
          ? Array.from(document.querySelectorAll<HTMLElement>("[aria-label]")).find((item) => item.getAttribute("aria-label") === triggerLabel)
          : null;
      currentTrigger?.focus();
    });
  };
  useEffect(() => { if (!inspector) return; inspectorCloseRef.current?.focus(); const close = (event: KeyboardEvent) => { if (event.key === "Escape") closeInspector(); }; document.addEventListener("keydown", close); return () => document.removeEventListener("keydown", close); }, [inspector]);
  useEffect(() => {
    const remember = (event: Event) => {
      const target = event.target instanceof HTMLElement ? event.target.closest<HTMLElement>("button, a[href], [tabindex]") : null;
      if (target && document.querySelector(".scientific-viewer")?.contains(target)) {
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
  const selected = visibleDatasets.find((item) => item.datasetId === selectedId);
  const selectedScientificObject = scientificObjects.find((item) => item.id === initialObjectId);
  const kind = selected ? inferDataKind(selected) : "generic";
  const canWriteProject = canManageProject(history?.project.role);
  const handleSelection = (selection: WorkspaceSelectionContext) => { setScientificSelection(selection); openInspector(); };
  const updateLocalDataset = (datasetId: string, changes: Partial<ProjectDataset>) => setHistory((current) => current ? { ...current, datasets: current.datasets.map((dataset) => dataset.datasetId === datasetId ? { ...dataset, ...changes } : dataset) } : current);
  async function setDatasetArchived(dataset: ProjectDataset, archived: boolean) {
    setBusy(true); setMutationError("");
    try { const result = await updateDataset(dataset.datasetId, { archived }); updateLocalDataset(dataset.datasetId, { name: result.name, status: result.status }); }
    catch (reason) { setMutationError(reason instanceof Error ? reason.message : "数据集状态更新失败。"); }
    finally { setBusy(false); }
  }
  async function applyDatasetBatch(action: "archive" | "restore") {
    if (!selectedDatasetIds.size || busy) return;
    setBusy(true); setMutationError("");
    try {
      const ids = Array.from(selectedDatasetIds);
      await bulkDatasetAction(ids, action);
      setHistory(await getProjectHistory(projectId));
      setSelectedDatasetIds(new Set()); setSelectionMode(false);
    } catch (reason) { setMutationError(reason instanceof Error ? reason.message : "批量数据操作失败。"); }
    finally { setBusy(false); }
  }
  const datasetActions = (dataset: ProjectDataset): ObjectAction[] => {
    const actions: ObjectAction[] = [
      { label: "打开数据", href: `/projects/${projectId}/data?dataset=${dataset.datasetId}` },
      canWriteProject
        ? { label: "研究此数据", href: `/projects/${projectId}/research?dataset=${dataset.datasetId}` }
        : { label: "查看研究记录", href: `/projects/${projectId}/research` },
    ];
    if (canWriteProject) {
      actions.push({ label: "重命名数据集", onSelect: () => setDialog({ dataset, mode: "edit" }) });
      actions.push({ label: dataset.status === "archived" ? "恢复数据集" : "归档数据集", onSelect: () => void setDatasetArchived(dataset, dataset.status !== "archived") });
      if (history?.project.role === "owner") actions.push({ label: "删除空数据集", destructive: true, onSelect: () => setDialog({ dataset, mode: "delete" }) });
    }
    return actions;
  };
  const toggleDatasetSelected = (datasetId: string, checked: boolean) => setSelectedDatasetIds((current) => { const next = new Set(current); if (checked) next.add(datasetId); else next.delete(datasetId); return next; });
  return <RequireProductAuth><ProductShell projectId={projectId}><section className="data-workbench"><EmptyOrError state={state} error={error} />{history && <><aside className="data-navigator"><header><p className="product-kicker">项目数据</p><h1>{productProjectName(history.project.name)}</h1><div className="data-navigator-controls"><div className="segmented-control" role="group" aria-label="数据集状态"><button type="button" aria-pressed={statusFilter === "active"} onClick={() => setStatusFilter("active")}>当前</button><button type="button" aria-pressed={statusFilter === "archived"} onClick={() => setStatusFilter("archived")}>已归档</button></div>{canWriteProject ? <button type="button" className="product-icon-action" aria-label={selectionMode ? "退出数据集选择" : "选择多个数据集"} aria-pressed={selectionMode} title={selectionMode ? "退出选择" : "批量选择"} onClick={() => { setSelectionMode((value) => !value); setSelectedDatasetIds(new Set()); }}>{selectionMode ? "×" : "✓"}</button> : null}</div></header>{selectionMode ? <div className="data-batch-actions" role="region" aria-label="批量数据操作"><strong>{selectedDatasetIds.size} 个已选择</strong><button type="button" disabled={!selectedDatasetIds.size || busy} onClick={() => void applyDatasetBatch(statusFilter === "archived" ? "restore" : "archive")}>{statusFilter === "archived" ? "恢复" : "归档"}</button></div> : null}{mutationError ? <p className="product-form-error data-management-error" role="alert">{mutationError}</p> : null}<div className="data-tree managed-data-tree">{visibleDatasets.map((dataset) => <ManagedObjectRow key={dataset.datasetId} href={`/projects/${projectId}/data?dataset=${dataset.datasetId}`} title={productProjectName(dataset.name)} description={`${dataset.import.fileCount} 个文件 · ${dataKindLabel(inferDataKind(dataset))}`} trailing={dataset.datasetId === selected?.datasetId && !selectedScientificObject ? "正在查看" : dataset.status === "archived" ? "已归档" : undefined} actions={datasetActions(dataset)} selectionMode={selectionMode} selected={selectedDatasetIds.has(dataset.datasetId)} active={!selectionMode && !selectedScientificObject && dataset.datasetId === selected?.datasetId} onSelectedChange={(checked) => toggleDatasetSelected(dataset.datasetId, checked)} />)}</div>{scientificObjects.length ? <section className="scientific-object-list" aria-labelledby="scientific-object-list-title"><h2 id="scientific-object-list-title">科研对象</h2>{scientificObjects.map((item) => item.current_version_id ? <Link key={item.id} className={item.id === selectedScientificObject?.id ? "active" : ""} href={`/projects/${projectId}/data?object=${encodeURIComponent(item.id)}&version=${encodeURIComponent(item.current_version_id)}`}><strong>{item.display_name}</strong><span>{scientificObjectTypeLabel(item.object_type)}</span></Link> : null)}</section> : null}{visibleDatasets.length === 0 && scientificObjects.length === 0 ? <div className="data-navigator-empty"><strong>{statusFilter === "archived" ? "没有已归档数据" : "还没有项目数据"}</strong><p>{statusFilter === "archived" ? "归档后的数据会显示在这里。" : "上传后将按文件、科学对象和组合视图组织。"}</p></div> : null}{canWriteProject ? <Link className="product-secondary-action data-upload" href={`/projects/${projectId}/datasets/new`}>上传数据</Link> : null}</aside><section className="scientific-viewer">{selectedScientificObject && initialObjectVersionId ? <ScientificObjectViewer projectId={projectId} objectId={selectedScientificObject.id} versionId={initialObjectVersionId} /> : selected ? <><header className="viewer-toolbar"><div><h2>{productProjectName(selected.name)}</h2><p>{selected.import.fileCount} 个文件 · {selected.profile?.rowCount ?? selected.profile?.objectCount ?? "—"} 个记录</p></div><div>{canWriteProject ? <Link className="product-primary-action" href={`/projects/${projectId}/research?dataset=${selected.datasetId}`}>研究此数据</Link> : null}</div></header><ScientificDataView projectId={projectId} dataset={selected} kind={kind} onInspect={openInspector} onSelection={handleSelection} /></> : <div className="product-state"><h2>{statusFilter === "archived" ? "没有可恢复的数据" : "尚无项目数据"}</h2><p>{statusFilter === "archived" ? "切换到当前数据继续查看。" : "上传支持的材料数据后，可在这里查看与研究。"}</p>{statusFilter === "active" && canWriteProject ? <Link className="product-primary-action" href={`/projects/${projectId}/datasets/new`}>上传数据</Link> : null}</div>}</section>{inspector && selected && <aside className="context-inspector" role="region" aria-labelledby="context-inspector-title"><button ref={inspectorCloseRef} type="button" aria-label="关闭详情" onClick={closeInspector}>×</button><p className="product-kicker">详情</p><h2 id="context-inspector-title">{scientificSelection?.primary ? selectionTitle(scientificSelection.primary) : productProjectName(selected.name)}</h2>{scientificSelection?.primary ? <dl><dt>选择类型</dt><dd>{selectionKindLabel(scientificSelection.primary.kind)}</dd><dt>来源数据</dt><dd>{productProjectName(selected.name)}</dd><dt>状态</dt><dd>已选择，可继续查看依据</dd></dl> : <dl><dt>数据类型</dt><dd>{dataKindLabel(kind)}</dd><dt>记录</dt><dd>{selected.profile?.rowCount ?? selected.profile?.objectCount ?? "未提供"}</dd><dt>状态</dt><dd>{dataStatusLabel(selected.status)}</dd></dl>}<h3>依据</h3><p>内容类型与可用属性来自已生成的数据语义档案。</p><details><summary>来源与过程</summary><p>{selected.import.fileCount} 个源文件，经当前导入流程识别。</p></details><details><summary>技术详情</summary><p>选择 contract 已绑定当前项目和数据范围。</p></details></aside>}{dialog ? <DatasetEditDialog dataset={dialog.dataset} mode={dialog.mode} onClose={() => setDialog(null)} onUpdated={(changes) => updateLocalDataset(dialog.dataset.datasetId, changes)} onDeleted={(datasetId) => setHistory((current) => current ? { ...current, datasets: current.datasets.filter((dataset) => dataset.datasetId !== datasetId) } : current)} /> : null}</>}</section></ProductShell></RequireProductAuth>;
}

export function DatasetUploadPage({ projectId }: { projectId: string }) {
  const { history, state: projectState, error: projectError } = useProject(projectId);
  const [name, setName] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!name.trim() || !files.length) return;
    setBusy(true); setError(""); setMessage("");
    try {
      await uploadDatasetFiles(projectId, name.trim(), files.map((file) => {
        const normalizedName = file.name.toLowerCase().replace(/[\s-]+/gu, "_");
        const importKind = normalizedName.includes("phonon") && normalizedName.includes("band") ? "phonon_band" : normalizedName.includes("phonon") && normalizedName.includes("dos") ? "phonon_dos" : undefined;
        return {
          file,
          importKind,
          contractVersion: importKind === "phonon_band" ? PHONON_BAND_SCHEMA_VERSION : importKind === "phonon_dos" ? PHONON_DOS_SCHEMA_VERSION : undefined,
          companionGroupId: files.length > 1 ? (importKind ? "phonon_bundle" : "primary_bundle") : undefined,
        };
      }));
      setMessage("数据已上传并进入解析流程。"); setFiles([]); setName("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "上传失败，请检查文件后重试。");
    } finally { setBusy(false); }
  }
  const dataHref = "/projects/" + projectId + "/data";
  const canUpload = canManageProject(history?.project.role);
  return <RequireProductAuth><ProductShell projectId={projectId}><section className="document-page upload-page"><Link className="back-link" href={dataHref}>← 返回项目数据</Link><header className="product-page-heading"><p className="product-kicker">项目数据</p><h1>上传数据</h1><p>上传后，系统会识别文件格式并生成可用于研究的数据档案。</p></header><EmptyOrError state={projectState} error={projectError} />{history && !canUpload ? <div className="product-state"><h2>此项目为只读</h2><p>你可以查看已有数据和研究结果，但不能向此项目上传新数据。</p><Link className="product-primary-action" href={dataHref}>查看项目数据</Link></div> : null}{history && canUpload ? <form className="upload-form" onSubmit={(event) => void submit(event)}><label htmlFor="dataset-upload-name">数据集名称</label><input id="dataset-upload-name" value={name} onChange={(event) => setName(event.target.value)} placeholder="例如：BaTiO3 稳定性数据" required /><label htmlFor="dataset-upload-files">源文件</label><input id="dataset-upload-files" type="file" multiple onChange={(event) => setFiles(Array.from(event.target.files || []))} required />{files.length ? <ul aria-label="已选择文件">{files.map((file) => <li key={file.name + file.size}>{file.name} · {(file.size / 1024).toFixed(1)} KiB</li>)}</ul> : <p className="upload-hint">支持的格式以当前导入能力为准；不支持的文件会保留为可解释的失败状态。</p>}{error && <p className="product-form-error" role="alert">{error}</p>}{message && <p className="product-form-success" role="status">{message}</p>}<div className="product-row-actions"><button type="submit" className="product-primary-action" disabled={busy || !name.trim() || !files.length}>{busy ? "正在上传…" : "上传并解析"}</button><Link className="product-secondary-action" href={`/projects/${projectId}/data`}>取消</Link></div></form> : null}</section></ProductShell></RequireProductAuth>;
}

function dataKindLabel(kind: DataKind) { return ({ table: "表格", structure: "结构", trajectory: "轨迹", xrd: "XRD", electronic: "电子结构", phonon: "声子", volumetric: "体数据", detected: "检测到的内容", generic: "通用文件" })[kind]; }
function productProjectName(name: string | null | undefined) {
  const value = String(name || "").trim();
  const acceptanceName = value.match(/^current\s+acceptance\s+(.+?)\s+\d{10,}$/iu);
  return (acceptanceName ? acceptanceName[1] : value.replace(/^current\s+acceptance\s+/i, "")).trim() || "材料研究项目";
}
function dataStatusLabel(status: string | null | undefined) { return ({ ready: "可用于研究", profile_ready: "已识别数据", processing: "正在解析", failed: "解析失败", partial: "部分可用" } as Record<string, string>)[String(status || "").toLowerCase()] || "已识别数据"; }
function selectionKindLabel(kind: string) { return ({ DATASET_SAMPLE: "数据样本", STRUCTURE_SITE: "结构位点", EXPERIMENTAL_XRD_PEAK: "实验峰", XRD_MATCH: "匹配峰", TRAJECTORY_ATOM: "轨迹原子", ARTIFACT: "科学结果" } as Record<string, string>)[kind] || "科学对象"; }
function selectionTitle(selection: { kind: string; sampleRef: string | null; siteId: string | null; peakId: string | null; matchId: string | null; atomId: string | null }) { return selection.sampleRef || selection.siteId || selection.peakId || selection.matchId || selection.atomId || selectionKindLabel(selection.kind); }
function ScientificDataView({ projectId, dataset, kind, onInspect, onSelection }: { projectId: string; dataset: ProjectHistory["datasets"][number]; kind: DataKind; onInspect: () => void; onSelection: (selection: WorkspaceSelectionContext) => void }) {
  const [resources, setResources] = useState<DatasetSourceResource[] | null>(null);
  const [resourceError, setResourceError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    setResources(null);
    setResourceError(null);
    setSelectedId("");
    void getDatasetSourceResources(dataset.datasetId, controller.signal)
      .then((items) => { setResources(items); setSelectedId(preferredResource(items, kind)?.objectId || items[0]?.objectId || ""); })
      .catch((reason) => {
        if (controller.signal.aborted) return;
        setResources([]);
        setResourceError(reason instanceof Error ? reason.message : "SOURCE_RESOURCE_LOAD_FAILED");
      });
    return () => controller.abort();
  }, [dataset.datasetId, kind]);
  if (resources === null) return <div className="product-loading" role="status">正在加载科学数据…</div>;
  if (resourceError && kind !== "table") return <div className={`science-canvas ${kind}`} role="alert" tabIndex={0} onClick={onInspect}><div className="science-canvas-label"><span>{dataKindLabel(kind)}</span><strong>当前解析资源暂时无法读取</strong></div><p>数据档案仍然可用；请稍后重试或查看来源与属性。</p><details><summary>技术详情</summary><p>{resourceError}</p></details></div>;
  const selected = resources.find((item) => item.objectId === selectedId) || preferredResource(resources, kind);
   if (resources.length > 1 || kind === "detected") return <div className="detected-content"><div><p className="product-kicker">检测到的数据</p><h2>此上传包含 {resources.length} 个科学对象</h2><p>仅展示导入流程实际识别的资源，不推测压缩包目录。</p></div><nav aria-label="检测到的科学对象">{resources.map((resource, index) => <button key={resource.objectId} className={resource.objectId === selected?.objectId ? "selected" : ""} aria-pressed={resource.objectId === selected?.objectId} onClick={() => setSelectedId(resource.objectId)}><strong>{sourceTypeLabel(resource.objectType)}</strong><span>{resourceDisplayName(resource, resources, index)}</span></button>)}</nav>{selected ? <section className="source-scientific-viewer"><ScientificSourceViewer projectId={projectId} resource={selected} resources={resources} onSelection={onSelection} /><button type="button" className="product-secondary-action" onClick={onInspect}>查看所选对象详情</button></section> : null}</div>;
   if (selected) return <section className="source-scientific-viewer"><ScientificSourceViewer projectId={projectId} resource={selected} resources={resources} onSelection={onSelection} /><button type="button" className="product-secondary-action" onClick={onInspect}>查看来源与属性</button></section>;
  if (kind === "table") return <TableScientificView dataset={dataset} onInspect={onInspect} />;
  return <div className="science-canvas science-canvas-fallback" role="region" aria-labelledby="science-fallback-title"><div className="science-canvas-label"><span>{dataKindLabel(kind)}</span><strong id="science-fallback-title">当前没有可渲染的科学对象</strong></div><p>数据档案和来源信息仍然保留，但当前没有通过 Viewer contract 验证的资源可供交互查看。</p><button type="button" className="product-secondary-action" onClick={onInspect}>查看来源与属性</button></div>;
}

function preferredResource(resources: DatasetSourceResource[], kind: DataKind): DatasetSourceResource | undefined {
  const types: Record<DataKind, string[]> = { table: ["DataFrame"], structure: ["Structure", "Atoms"], trajectory: ["Trajectory"], xrd: ["DataFrame"], electronic: ["ElectronicBand", "ElectronicDos"], phonon: ["PhononBand", "PhononDos", "PhononEigenvector"], volumetric: ["VolumetricData"], detected: [], generic: [] };
  return resources.find((item) => types[kind].includes(item.objectType)) || resources[0];
}

function sourceTypeLabel(objectType: string) {
  return ({ DataFrame: "表格数据", Structure: "晶体结构", Atoms: "原子结构", Trajectory: "原子轨迹", ElectronicBand: "能带", ElectronicDos: "态密度", PhononBand: "声子能带", PhononDos: "声子态密度", PhononEigenvector: "声子振型", VolumetricData: "体数据" } as Record<string, string>)[objectType] || objectType;
}

function scientificObjectTypeLabel(objectType: string) {
  return ({ "materials.dataset": "材料数据表", "materials.table": "科研材料表", "structure.crystal": "晶体结构", "trajectory.atomic": "原子轨迹", "diffraction.xrd.experimental": "实验 XRD", "diffraction.xrd.theoretical": "理论 XRD", "electronic.band_structure": "电子能带", "electronic.dos": "电子态密度", "phonon.band_structure": "声子能带", "phonon.dos": "声子态密度", "volumetric.charge_density": "电荷密度" } as Record<string, string>)[objectType] || "科学数据";
}

function resourceDisplayName(resource: DatasetSourceResource, resources: DatasetSourceResource[], index: number) {
  const label = sourceTypeLabel(resource.objectType);
  const sameTypeCount = resources.filter((item) => item.objectType === resource.objectType).length;
  return sameTypeCount > 1 ? `${label} · 第 ${index + 1} 项` : label;
}

export function TableScientificView({ dataset, onInspect }: { dataset: ProjectHistory["datasets"][number]; onInspect: () => void }) {
  const [query, setQuery] = useState("");
  const [sortAsc, setSortAsc] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  const [visible, setVisible] = useState({ property: true, semantic: true, count: true, unit: true });
  const rows = useMemo(() => Object.entries(dataset.profile?.semanticRoles || {}).map(([role, count]) => ({ id: role, property: role, semantic: semanticRoleLabel(role), count: Number(count) || 0, unit: "未声明" })).filter((row) => !query || Object.values(row).some((value) => String(value).toLowerCase().includes(query.toLowerCase()))).sort((a, b) => sortAsc ? a.property.localeCompare(b.property) : b.property.localeCompare(a.property)), [dataset.profile?.semanticRoles, query, sortAsc]);
  const choose = (id: string) => { setSelected(id); onInspect(); };
  return <div className="table-view"><div className="table-tools"><input aria-label="搜索表格" placeholder="搜索属性…" value={query} onChange={(event) => setQuery(event.target.value)} /><button type="button" onClick={() => setSortAsc((value) => !value)} aria-label="切换排序">按属性 {sortAsc ? "↑" : "↓"}</button><details><summary>列</summary><div className="column-menu">{Object.entries({ property: "属性", semantic: "语义角色", count: "记录", unit: "单位" }).map(([key, label]) => <label key={key}><input type="checkbox" checked={visible[key as keyof typeof visible]} onChange={() => setVisible((value) => ({ ...value, [key]: !value[key as keyof typeof value] }))} />{label}</label>)}</div></details></div><div className="table-scroll"><table aria-label={`${productProjectName(dataset.name)}科学属性`}><caption className="sr-only">{productProjectName(dataset.name)}的科学属性、语义角色、记录数量和单位</caption><thead><tr>{visible.property && <th scope="col">属性</th>}{visible.semantic && <th scope="col">语义角色</th>}{visible.count && <th scope="col">可用记录</th>}{visible.unit && <th scope="col">单位</th>}</tr></thead><tbody>{rows.length ? rows.map((row) => <tr key={row.id} tabIndex={0} aria-selected={selected === row.id} className={selected === row.id ? "selected" : ""} onClick={() => choose(row.id)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); choose(row.id); } }}>{visible.property && <td>{row.property}</td>}{visible.semantic && <td>{row.semantic}</td>}{visible.count && <td>{row.count}</td>}{visible.unit && <td>{row.unit}</td>}</tr>) : <tr><td colSpan={4}>当前数据未提供可浏览的列语义。</td></tr>}</tbody></table></div></div>;
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
