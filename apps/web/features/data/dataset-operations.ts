"use client";

import { useEffect, useRef, useState } from "react";
import { bulkDatasetAction, getProjectHistory, type DatasetDetail, type ProjectHistory } from "../../app/lib/planner-api";
import { trashRequest } from "../projects/trash-operations";

type Changes = { name?: string; archived?: boolean; lifecycle?: string };
export function validateDataset(value: DatasetDetail, projectId: string, id: string, changes: Changes, previousStatus?: string) {
  if (!value || value.id !== id || (value.datasetId && value.datasetId !== id) || value.projectId !== projectId ||
      typeof value.name !== "string" || !value.name.trim() || typeof value.status !== "string" || !value.status.trim()) throw new Error("Dataset identity mismatch");
  const lifecycle = changes.lifecycle?.toLowerCase() || (changes.archived === undefined ? undefined : changes.archived ? "archived" : "active");
  const actual = ["archived", "trashed"].includes(value.status) ? value.status : "active";
  const restoredFromTrash = previousStatus === "trashed" && changes.archived === false && actual !== "trashed";
  if ((changes.name !== undefined && value.name !== changes.name) || (lifecycle && lifecycle !== actual && !restoredFromTrash)) throw new Error("Dataset update not confirmed");
  return { name: value.name, status: value.status };
}
export function validateDatasetHistory(value: ProjectHistory, projectId: string) {
  if (!value?.project || (value.project.id || value.project.projectId) !== projectId ||
      (value.project.id && value.project.id !== projectId) || (value.project.projectId && value.project.projectId !== projectId) ||
      !Array.isArray(value.datasets) || new Set(value.datasets.map((item) => item?.datasetId)).size !== value.datasets.length ||
      value.datasets.some((item) => !item?.datasetId || typeof item.name !== "string" || typeof item.status !== "string")) throw new Error("Dataset directory identity mismatch");
  return value;
}
export async function readDatasetDirectory(projectId: string, signal: AbortSignal) {
  const first = validateDatasetHistory(await getProjectHistory(projectId, { forceRefresh: true, signal }), projectId);
  signal.throwIfAborted();
  let cursor = first.pagination?.datasets.nextCursor;
  const seen = new Set<string>();
  const datasets = new Map(first.datasets.map((item) => [item.datasetId, item]));
  while (cursor) {
    if (typeof cursor !== "string" || seen.has(cursor)) throw new Error("Dataset directory cursor mismatch");
    seen.add(cursor);
    const page = validateDatasetHistory(await getProjectHistory(projectId, { forceRefresh: true, datasetsCursor: cursor, signal }), projectId);
    signal.throwIfAborted();
    for (const item of page.datasets) datasets.set(item.datasetId, item);
    cursor = page.pagination?.datasets.nextCursor;
  }
  return { ...first, datasets: [...datasets.values()] };
}
export async function updateDatasetBatches(ids: string[], action: "archive" | "trash" | "restore", signal: AbortSignal, accepted: (ids: string[]) => void) {
  for (let offset = 0; offset < ids.length; offset += 100) {
    signal.throwIfAborted();
    const chunk = ids.slice(offset, offset + 100);
    const result = await bulkDatasetAction(chunk, action, signal);
    signal.throwIfAborted();
    if (!result || result.action !== action || result.count !== chunk.length || !Array.isArray(result.datasetIds) ||
        result.datasetIds.length !== chunk.length || new Set(result.datasetIds).size !== chunk.length || chunk.some((id) => !result.datasetIds.includes(id))) throw new Error("Dataset batch identity mismatch");
    accepted(chunk);
  }
}

export function useDatasetOperation(projectId: string) {
  const owner = useRef<AbortController | null>(null);
  const scope = useRef(projectId); scope.current = projectId;
  const requiresRead = useRef(false);
  const labelRef = useRef("");
  const [state, setState] = useState({ projectId, pending: false, reading: false, uncertain: false, error: "", readError: "" });
  const initial = () => ({ projectId, pending: false, reading: false, uncertain: false, error: "", readError: "" });
  useEffect(() => {
    requiresRead.current = false; setState(initial());
    return () => { owner.current?.abort(); owner.current = null; };
  }, [projectId]);
  const owns = (controller: AbortController) => owner.current === controller && !controller.signal.aborted && scope.current === projectId;
  const dismiss = () => {
    if (!owner.current) return;
    owner.current.abort(); owner.current = null; requiresRead.current = true;
    setState((value) => ({ ...value, pending: false, reading: false, uncertain: true, error: `${labelRef.current || "操作"}的结果尚未确认，请重新读取数据列表。` }));
  };
  async function run<T>(label: string, perform: (signal: AbortSignal) => Promise<T>, accept: (value: T) => void) {
    if (owner.current || requiresRead.current || scope.current !== projectId) return false;
    const controller = new AbortController(); owner.current = controller; labelRef.current = label;
    setState({ ...initial(), pending: true });
    try {
      const value = await trashRequest(perform, controller.signal);
      if (!owns(controller)) return false;
      owner.current = null; setState(initial()); accept(value); return true;
    } catch (reason) {
      if (!owns(controller)) return false;
      const status = (reason as { status?: number } | null)?.status;
      const rejected = status !== undefined && [400, 401, 403, 404, 409, 422].includes(status);
      requiresRead.current = !rejected;
      setState({ ...initial(), uncertain: !rejected, error: rejected
        ? status === 409 ? `${label}未完成：名称已存在，或数据状态不允许此操作。请检查后重试。` : `${label}未完成，请检查内容或权限后重试。`
        : `${label}的结果尚未确认，请重新读取数据列表后再操作。` });
      return false;
    } finally { controller.abort(); if (owner.current === controller) owner.current = null; }
  }
  async function reconcile(accept: (history: ProjectHistory) => void) {
    if (owner.current || scope.current !== projectId) return false;
    const controller = new AbortController(); owner.current = controller;
    setState((value) => ({ ...value, reading: true, readError: "" }));
    try {
      const value = await trashRequest((signal) => readDatasetDirectory(projectId, signal), controller.signal);
      if (!owns(controller)) return false;
      accept(value); requiresRead.current = false; setState(initial()); return true;
    } catch {
      if (owns(controller)) setState((value) => ({ ...value, reading: false, readError: "暂时无法读取数据列表，当前内容已保留。请重试。" }));
      return false;
    } finally { controller.abort(); if (owner.current === controller) owner.current = null; }
  }
  return { ...(state.projectId === projectId ? state : initial()), run, dismiss, reconcile, locked: () => Boolean(owner.current || requiresRead.current) };
}
export type DatasetOperation = ReturnType<typeof useDatasetOperation>;
