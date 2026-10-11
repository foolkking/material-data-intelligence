"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { ProjectSummary } from "../../app/lib/planner-api";
import { trashRequest } from "./trash-operations";

export function validateProject(project: ProjectSummary, id?: string, expected?: { name?: string; description?: string; archived?: boolean; lifecycle?: string; pinned?: boolean }) {
  if (!project?.id || (id && project.id !== id) || (project.projectId && project.projectId !== project.id) ||
      typeof project.name !== "string" || !project.name.trim()) throw new Error("Project identity mismatch");
  const status = expected?.lifecycle?.toLowerCase() || (expected?.archived !== undefined ? expected.archived ? "archived" : "active" : undefined);
  if ((status && project.status?.toLowerCase() !== status) ||
      (expected?.name !== undefined && project.name !== expected.name) ||
      (expected?.description !== undefined && project.description !== expected.description) ||
      (expected?.pinned !== undefined && project.pinned !== expected.pinned)) throw new Error("Project update not confirmed");
  return project;
}
export function validateProjectDirectory(items: ProjectSummary[]) {
  if (!Array.isArray(items) || new Set(items.map((item) => item?.id)).size !== items.length) throw new Error("Project directory mismatch");
  items.forEach((item) => validateProject(item));
  return items;
}
export function validateProjectBatch(result: { action: string; count: number; projectIds: string[] }, action: string, ids: string[]) {
  if (!result || result.action !== action || result.count !== ids.length || !Array.isArray(result.projectIds) ||
      result.projectIds.length !== ids.length || new Set(result.projectIds).size !== ids.length ||
      ids.some((id) => !result.projectIds.includes(id))) throw new Error("Project batch identity mismatch");
  return result;
}

export function useProjectOperation() {
  const owner = useRef<AbortController | null>(null);
  const requiresRead = useRef(false);
  const activeLabel = useRef("");
  const [pending, setPending] = useState(false);
  const [uncertain, setUncertain] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => () => { owner.current?.abort(); owner.current = null; }, []);
  const reconciled = useCallback(() => {
    if (owner.current) return;
    requiresRead.current = false; setUncertain(false); setError("");
  }, []);
  const dismiss = () => {
    if (!owner.current) return;
    owner.current.abort(); owner.current = null;
    requiresRead.current = true; setUncertain(true); setPending(false);
    setError(`${activeLabel.current}的结果尚未确认，请重新读取项目列表。`);
  };
  async function run<T>(label: string, perform: (signal: AbortSignal) => Promise<T>, accept: (value: T) => void, readOnly = false) {
    if (owner.current || requiresRead.current) return false;
    const controller = new AbortController(); owner.current = controller; activeLabel.current = label;
    let confirmed = false;
    setPending(true); setError("");
    try {
      const value = await trashRequest(perform, controller.signal);
      if (owner.current !== controller || controller.signal.aborted) return false;
      confirmed = true; owner.current = null; setPending(false);
      accept(value);
      return true;
    } catch (reason) {
      if (!confirmed && (owner.current !== controller || controller.signal.aborted)) return false;
      const status = (reason as { status?: number } | null)?.status;
      const rejected = status !== undefined && [400, 401, 403, 404, 409, 422].includes(status);
      requiresRead.current = !readOnly && !rejected; setUncertain(requiresRead.current);
      setError(readOnly ? `${label}暂时无法完成，请重试。` : rejected
        ? status === 409 ? `${label}未完成：项目名称已存在，或项目状态不允许此操作。请检查后重试。` : `${label}未完成，请检查内容或权限后重试。`
        : `${label}的结果尚未确认，请重新读取项目列表后再操作。`);
      return false;
    } finally {
      controller.abort();
      if (owner.current === controller) { owner.current = null; setPending(false); }
    }
  }
  return { run, dismiss, reconciled, pending, uncertain, error, locked: () => Boolean(owner.current || requiresRead.current) };
}
export type ProjectOperation = ReturnType<typeof useProjectOperation>;
