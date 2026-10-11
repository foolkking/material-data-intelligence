"use client";

import { useEffect, useRef, useState } from "react";
import {
  getAgent2SessionMemory, pinAgent2Object, pinAgent2Result, unpinAgent2Object, unpinAgent2Result,
  validateSessionMemory, type Agent2SessionMemory, type ScientificObjectMemoryRef,
} from "../../app/lib/agent2-memory-api";
import { readSessionRequest } from "./session-management";

type MemoryState = {
  scope: string; memory: Agent2SessionMemory | null; reading: boolean; updating: boolean;
  needsRefresh: boolean; error: string;
};
type MemoryOwner = { scope: string; controller: AbortController; state: MemoryState; busy: boolean };
type Change = { kind: "result"; id: string; pinned: boolean } | { kind: "object"; ref: ScientificObjectMemoryRef; pinned: boolean };

export function hasPinnedObject(memory: Agent2SessionMemory, ref: ScientificObjectMemoryRef) {
  return memory.pinned_object_refs.some((item) => item.project_id === ref.project_id && item.object_id === ref.object_id && item.version_id === ref.version_id);
}

/** One session owns both the conversation chips and result actions. Never infer a failed read is empty. */
export function useSessionMemory(projectId: string, sessionId?: string, canModify = false) {
  const scope = JSON.stringify([projectId, sessionId]);
  const initial = (): MemoryState => ({ scope, memory: null, reading: Boolean(sessionId), updating: false, needsRefresh: false, error: "" });
  const [state, setState] = useState<MemoryState>(initial);
  const owner = useRef<MemoryOwner | null>(null);
  const currentScope = useRef(scope); currentScope.current = scope;
  const permission = useRef(canModify); permission.current = canModify;

  const owns = (task: MemoryOwner) => owner.current === task && currentScope.current === task.scope && !task.controller.signal.aborted;
  function publish(task: MemoryOwner, patch: Partial<MemoryState>) {
    if (!owns(task)) return;
    task.state = { ...task.state, ...patch }; setState(task.state);
  }
  function accept(task: MemoryOwner, value: Agent2SessionMemory) {
    validateSessionMemory(value, projectId, sessionId!);
    if (task.state.memory && value.version < task.state.memory.version) throw new Error("Stale session memory");
    publish(task, { memory: value });
  }
  async function refresh(task = owner.current) {
    if (!task || !sessionId || task.scope !== scope || !owns(task) || task.busy) return;
    task.busy = true; publish(task, { reading: true });
    try {
      const value = await readSessionRequest((signal) => getAgent2SessionMemory(projectId, sessionId, { signal }), task.controller.signal);
      if (!owns(task)) return;
      accept(task, value);
      publish(task, { error: "", needsRefresh: false });
    } catch {
      if (owns(task)) publish(task, { needsRefresh: true, error: task.state.needsRefresh && task.state.memory
        ? "上下文暂未更新，已确认的内容仍保留。请重新读取后再操作。"
        : "上下文暂时无法读取，请重试。" });
    } finally { task.busy = false; publish(task, { reading: false }); }
  }
  useEffect(() => {
    const task: MemoryOwner = { scope, controller: new AbortController(), state: initial(), busy: false };
    owner.current = task; setState(task.state);
    void refresh(task);
    return () => { task.controller.abort(); if (owner.current === task) owner.current = null; };
    // Each owner closes over its exact project/session. Rendering another scope invalidates it immediately.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scope]);

  async function update(changes: Change[]) {
    const task = owner.current;
    if (!task || !sessionId || task.scope !== scope || !owns(task) || !permission.current || task.busy || task.state.needsRefresh || !task.state.memory) return;
    if (changes.some((change) => change.kind === "object" && (change.ref.project_id !== projectId || !change.ref.object_id || !change.ref.version_id || !change.ref.object_type))) {
      publish(task, { error: "来源与当前项目不匹配，请重新读取分析结果。" }); return;
    }
    task.busy = true; publish(task, { updating: true, error: "" });
    try {
      for (const change of changes) {
        if (!owns(task) || !permission.current) return;
        const present = change.kind === "result" ? task.state.memory!.pinned_result_refs.includes(change.id) : hasPinnedObject(task.state.memory!, change.ref);
        if (present === change.pinned) continue;
        const value = await readSessionRequest((signal) => change.kind === "result"
          ? (change.pinned ? pinAgent2Result : unpinAgent2Result)(projectId, sessionId, change.id, { signal })
          : (change.pinned ? pinAgent2Object : unpinAgent2Object)(projectId, sessionId, change.ref, { signal }), task.controller.signal);
        if (!owns(task)) return;
        validateSessionMemory(value, projectId, sessionId);
        const updated = change.kind === "result" ? value.pinned_result_refs.includes(change.id) : hasPinnedObject(value, change.ref);
        if (updated !== change.pinned) throw new Error("Session memory update not confirmed");
        // Publish each confirmed source independently so a later failure cannot hide partial completion.
        accept(task, value);
      }
    } catch (reason) {
      if (!owns(task)) return;
      const status = (reason as { status?: number } | null)?.status;
      const rejected = status !== undefined && [400, 401, 403, 404, 409, 422, 429].includes(status);
      publish(task, { needsRefresh: !rejected, error: rejected
        ? "上下文更新未完成，已确认的内容仍保留。请检查权限或内容后重试。"
        : "上下文更新结果尚未确认，已确认的内容仍保留。请重新读取后再操作。" });
    } finally { task.busy = false; publish(task, { updating: false }); }
  }
  const visible = state.scope === scope ? state : initial();
  return {
    ...visible, canUpdate: Boolean(sessionId && canModify && visible.memory && !visible.reading && !visible.updating && !visible.needsRefresh),
    refresh: () => refresh(),
    setResultPinned: (id: string, pinned: boolean) => update([{ kind: "result", id, pinned }]),
    setSourcesPinned: (refs: ScientificObjectMemoryRef[], pinned: boolean) => update(refs.map((ref) => ({ kind: "object", ref, pinned }))),
  };
}

export type SessionMemoryController = ReturnType<typeof useSessionMemory>;
