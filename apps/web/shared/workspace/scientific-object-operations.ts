"use client";

import { useEffect, useRef, useState } from "react";
import { bulkUpdateScientificObjects, getScientificObjectSummary, updateScientificObject, type ScientificObjectSummary } from "../../app/lib/scientific-viewer-api";
import { trashRequest } from "../../features/projects/trash-operations";

export type ObjectLifecycle = "ACTIVE" | "ARCHIVED" | "TRASHED";
export function validateManagedObject(value: ScientificObjectSummary, projectId: string, id?: string, lifecycle?: ObjectLifecycle) {
  if (!value || !value.id || value.project_id !== projectId || (id && value.id !== id) ||
      typeof value.display_name !== "string" || !value.display_name.trim() || typeof value.object_type !== "string" ||
      !["ACTIVE", "ARCHIVED", "TRASHED", "INVALIDATED"].includes(value.lifecycle_status) ||
      (lifecycle && value.lifecycle_status !== lifecycle)) throw new Error("Scientific object identity or lifecycle mismatch");
  return value;
}
export function validateManagedObjectBatch(value: { project_id: string; lifecycle: ObjectLifecycle; count: number; items: ScientificObjectSummary[] }, projectId: string, ids: string[], lifecycle: ObjectLifecycle) {
  if (!value || value.project_id !== projectId || value.lifecycle !== lifecycle || value.count !== ids.length ||
      !Array.isArray(value.items) || value.items.length !== ids.length || new Set(value.items.map((item) => item?.id)).size !== ids.length ||
      ids.some((id) => !value.items.some((item) => item?.id === id))) throw new Error("Scientific object batch mismatch");
  return value.items.map((item) => validateManagedObject(item, projectId, item.id, lifecycle));
}

type State = { projectId: string; origin: string; known: Record<string, ScientificObjectSummary>; pending: boolean; reading: boolean; uncertain: boolean; targets: string[]; error: string; readError: string };
const empty = (projectId: string): State => ({ projectId, origin: "", known: {}, pending: false, reading: false, uncertain: false, targets: [], error: "", readError: "" });
export function useScientificObjectOperation(projectId: string) {
  const [state, setState] = useState(() => empty(projectId));
  const owner = useRef<{ controller: AbortController; origin: string } | null>(null);
  const unresolved = useRef<string[]>([]);
  const requiresRead = useRef(false);
  const scope = useRef(projectId); scope.current = projectId;
  const current = state.projectId === projectId ? state : empty(projectId);
  const known = useRef(current.known); known.current = current.known;
  useEffect(() => {
    unresolved.current = []; requiresRead.current = false; setState(empty(projectId));
    return () => { owner.current?.controller.abort(); owner.current = null; };
  }, [projectId]);
  const owns = (controller: AbortController) => owner.current?.controller === controller && !controller.signal.aborted && scope.current === projectId;
  function publish(items: ScientificObjectSummary[]) {
    known.current = { ...known.current, ...Object.fromEntries(items.map((item) => [item.id, item])) };
    setState((value) => ({ ...value, known: known.current }));
  }
  function dismiss(origin?: string) {
    if (!owner.current || (origin && owner.current.origin !== origin)) return;
    owner.current.controller.abort(); owner.current = null;
    requiresRead.current = unresolved.current.length > 0;
    setState((value) => ({ ...value, pending: false, reading: false, uncertain: requiresRead.current, targets: [...unresolved.current], error: requiresRead.current ? "修改结果尚未确认，请核对对象状态后再操作。" : value.error }));
  }
  async function update(ids: string[], lifecycle: ObjectLifecycle, origin: string, batch = false) {
    if (!ids.length || (!batch && ids.length !== 1) || new Set(ids).size !== ids.length || owner.current || requiresRead.current || scope.current !== projectId) return false;
    const controller = new AbortController(); owner.current = { controller, origin }; unresolved.current = [...ids];
    setState((value) => ({ ...value, origin, pending: true, targets: ids, error: "", readError: "" }));
    try {
      for (let offset = 0; offset < ids.length; offset += 100) {
        controller.signal.throwIfAborted();
        const chunk = ids.slice(offset, offset + 100);
        unresolved.current = [...chunk];
        const items = await trashRequest(async (signal) => batch
          ? validateManagedObjectBatch(await bulkUpdateScientificObjects(projectId, chunk, lifecycle, signal), projectId, chunk, lifecycle)
          : [validateManagedObject(await updateScientificObject(chunk[0], { lifecycle }, signal), projectId, chunk[0], lifecycle)], controller.signal);
        if (!owns(controller)) return false;
        publish(items);
        unresolved.current = [];
      }
      setState((value) => ({ ...value, pending: false, uncertain: false, targets: [], error: "" }));
      return true;
    } catch (reason) {
      if (!owns(controller)) return false;
      const status = (reason as { status?: number } | null)?.status;
      const rejected = status !== undefined && [400, 401, 403, 404, 409, 422].includes(status);
      requiresRead.current = !rejected;
      setState((value) => ({ ...value, pending: false, uncertain: !rejected, targets: [...unresolved.current], error: rejected
        ? "修改未完成，请检查对象状态或权限后重试。"
        : "修改结果尚未确认，请核对对象状态后再操作。" }));
      return false;
    } finally { controller.abort(); if (owner.current?.controller === controller) owner.current = null; }
  }
  async function recheck(origin: string, ids = unresolved.current) {
    if (owner.current || scope.current !== projectId || !ids.length) return false;
    const controller = new AbortController(); owner.current = { controller, origin };
    setState((value) => ({ ...value, reading: true, readError: "" }));
    try {
      const results = await Promise.allSettled(ids.map((id) => trashRequest(async (signal) => validateManagedObject(await getScientificObjectSummary(id, signal), projectId, id), controller.signal)));
      if (!owns(controller)) return false;
      const items = results.flatMap((result) => result.status === "fulfilled" ? [result.value] : []);
      publish(items);
      const failed = ids.filter((_, index) => results[index].status === "rejected");
      unresolved.current = [...unresolved.current.filter((id) => !ids.includes(id)), ...failed];
      requiresRead.current = unresolved.current.length > 0;
      setState((value) => ({ ...value, reading: false, uncertain: requiresRead.current, targets: [...unresolved.current], error: requiresRead.current ? value.error : "", readError: failed.length ? "部分对象状态暂时无法核对，已读取内容保留。请重试。" : "" }));
      return failed.length === 0;
    } finally { controller.abort(); if (owner.current?.controller === controller) owner.current = null; }
  }
  return { ...current, update, recheck, dismiss, locked: () => Boolean(owner.current || requiresRead.current) };
}
export type ScientificObjectOperation = ReturnType<typeof useScientificObjectOperation>;
