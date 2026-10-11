"use client";

import { useEffect, useRef } from "react";
import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { ProductModal } from "../../shared/ui/ObjectManagement";
import { projectRoleAllows } from "../../app/lib/project-permissions";
import type { ProjectSummary } from "../../app/lib/planner-api";
import { useProjectCreation } from "./use-project-creation";

export function ProjectCreateDialog({ onClose, onCreated, returnFocus }: {
  onClose: () => void;
  onCreated: (project: ProjectSummary) => void;
  returnFocus?: HTMLElement | null;
}) {
  const creation = useProjectCreation(onCreated);
  const uploadRef = useRef<HTMLAnchorElement | null>(null);
  const nameRef = useRef<HTMLInputElement | null>(null);
  const descriptionRef = useRef<HTMLTextAreaElement | null>(null);
  const checkRef = useRef<HTMLButtonElement | null>(null);
  const matchesRef = useRef<HTMLUListElement | null>(null);
  const recoveryFocus = useRef(false);
  const project = creation.project;
  const close = () => { creation.dismiss(); onClose(); };
  useEffect(() => {
    if (creation.ready) {
      if (creation.needsRead) (checkRef.current || uploadRef.current)?.focus();
      else if (project) uploadRef.current?.focus(); else nameRef.current?.focus();
    }
  }, [creation.ready, project?.id]);
  useEffect(() => {
    if (!creation.busy && recoveryFocus.current && !creation.error) {
      recoveryFocus.current = false;
      if (creation.matches.length) matchesRef.current?.querySelector<HTMLElement>("button")?.focus();
      else if (project && !creation.descriptionSaved) descriptionRef.current?.focus();
      else if (project) uploadRef.current?.focus();
      else nameRef.current?.focus();
    }
  }, [creation.busy, creation.error, project, creation.descriptionSaved]);
  const feedback = <>
    {creation.needsRead && !creation.busy && !creation.error && !creation.notice ? <p role="status">已保留上次的创建草稿，请核对项目后继续。</p> : null}
    {creation.error ? <p className="product-form-error" role="alert">{creation.error}</p> : null}
    {creation.notice ? <p role="status">{creation.notice}</p> : null}
    {creation.needsRead && creation.busy !== "creating" && creation.busy !== "description" ? <button ref={checkRef} type="button" className="product-secondary-action" disabled={Boolean(creation.busy) || !creation.ready}
      onClick={() => { recoveryFocus.current = true; void creation.recheck(); }}>{creation.busy === "checking" ? "正在核对…" : "核对项目列表"}</button> : null}
  </>;
  return <ProductModal
    title={project ? creation.origin === "matched" ? "继续使用项目" : "项目已创建" : "新建研究项目"}
    description={project ? "可继续上传数据或进入研究。" : "在项目中整理数据、研究记录和报告。"}
    onClose={close} returnFocus={returnFocus}
    footer={project ? <>
      <button type="button" className="product-secondary-action" onClick={close}>稍后处理</button>
      <Link ref={uploadRef} className="product-primary-action" href={`/projects/${encodeURIComponent(project.id)}/datasets/new`} onClick={() => creation.dismiss()}>上传数据</Link>
    </> : <>
      <button type="button" className="product-secondary-action" onClick={close}>取消</button>
      <button type="button" className="product-primary-action" disabled={!creation.ready || Boolean(creation.busy) || !creation.name.trim() || (creation.needsRead && !creation.retryAllowed)} onClick={() => void creation.submit()}>
        {creation.busy === "creating" ? "正在创建…" : creation.mode === "unconfirmed" ? "用原名称重试" : "创建项目"}
      </button>
    </>}
  >
    {!creation.ready ? <div role="status">{creation.authError ? <><p>暂时无法确认账户，请重试。</p><button type="button" className="product-secondary-action" onClick={creation.retryAuth}>重新读取账户</button></> : "正在读取创建草稿…"}</div> : null}
    {project ? <div className="project-created-state project-creation-form">
      <strong>{project.name}</strong>
      <Link href={`/projects/${encodeURIComponent(project.id)}/research`} onClick={() => creation.dismiss()}>进入研究 →</Link>
      {!creation.descriptionSaved ? <div className="product-form-grid">
        <label htmlFor="created-project-description">待保存的研究说明</label>
        <textarea ref={descriptionRef} id="created-project-description" rows={4} maxLength={2000} value={creation.description}
          disabled={Boolean(creation.busy) || !creation.ready} onChange={(event) => creation.setDescription(event.target.value)} />
        {creation.busy === "description" ? <p role="status">项目已创建，正在保存研究说明…</p> : null}
        {!projectRoleAllows(project.role, "write") ? <p>当前项目为只读，无法保存研究说明。</p>
          : !creation.needsRead && creation.busy !== "description" ? <button type="button" className="product-secondary-action" disabled={Boolean(creation.busy) || !creation.ready} onClick={() => void creation.saveDescription()}>保存研究说明</button> : null}
      </div> : creation.description.trim() ? <p>研究说明已保存。</p> : null}
      {feedback}
    </div> : <div className="product-form-grid project-creation-form">
      <label htmlFor="new-project-name">项目名称</label>
      <input ref={nameRef} id="new-project-name" maxLength={160} value={creation.name} disabled={!creation.ready || Boolean(creation.busy)} readOnly={creation.mode === "unconfirmed"}
        onChange={(event) => creation.setName(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); void creation.submit(); } }} placeholder="例如：钙钛矿稳定性研究" required />
      <label htmlFor="new-project-description">研究说明 <span>可选</span></label>
      <textarea id="new-project-description" maxLength={2000} value={creation.description} disabled={!creation.ready || Boolean(creation.busy)} onChange={(event) => creation.setDescription(event.target.value)} placeholder="记录材料体系、数据来源或当前研究目标" rows={4} />
      {feedback}
      {creation.matches.length ? <ul ref={matchesRef} className="project-create-matches">{creation.matches.map((item) => <li key={item.id}>
        <strong>{item.name}</strong>
        <span>{item.status === "archived" ? "已归档" : item.status === "trashed" ? "回收站" : "当前项目"}{projectRoleAllows(item.role, "write") ? "" : " · 只读"}</span>
        <Link href={`/projects/${encodeURIComponent(item.id)}`}>查看项目</Link>
        <button type="button" className="product-secondary-action" onClick={() => creation.useExisting(item.id)}>继续使用这个项目</button>
      </li>)}</ul> : null}
    </div>}
  </ProductModal>;
}
