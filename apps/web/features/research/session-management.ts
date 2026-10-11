"use client";

import { useEffect, useRef, useState } from "react";
import type { ResearchSession } from "../../app/lib/product-api";

export async function readSessionRequest<T>(request: (signal: AbortSignal) => Promise<T>, signal: AbortSignal): Promise<T> {
  signal.throwIfAborted();
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  let cancel = () => {};
  const interrupted = new Promise<never>((_, reject) => {
    cancel = () => { controller.abort(); reject(new Error("Session request cancelled")); };
    signal.addEventListener("abort", cancel, { once: true });
    timer = setTimeout(() => { controller.abort(); reject(new Error("Session request timed out")); }, 10_000);
  });
  try { return await Promise.race([interrupted, request(controller.signal)]); }
  finally { clearTimeout(timer); signal.removeEventListener("abort", cancel); controller.abort(); }
}

export function validateResearchSession(session: ResearchSession, projectId: string, id?: string) {
  if (!session?.id || (id && session.id !== id) ||
      (session.projectId || session.project_id) !== projectId ||
      (session.projectId && session.project_id && session.projectId !== session.project_id) ||
      typeof session.title !== "string") throw new Error("Session identity mismatch");
  return session;
}

export function validateSessionDirectory(items: ResearchSession[], projectId: string) {
  if (!Array.isArray(items) || new Set(items.map((item) => item.id)).size !== items.length) throw new Error("Session directory mismatch");
  items.forEach((item) => validateResearchSession(item, projectId));
  return items;
}

export function useSessionOperation(projectId: string) {
  const owner = useRef<AbortController | null>(null);
  const needsRead = useRef(false);
  const [pending, setPending] = useState(false);
  const [uncertain, setUncertain] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  useEffect(() => {
    needsRead.current = false;
    setPending(false); setUncertain(false); setError(""); setNotice("");
    return () => { owner.current?.abort(); owner.current = null; };
  }, [projectId]);

  function dismiss() {
    if (!owner.current) return;
    owner.current.abort(); owner.current = null;
    needsRead.current = true; setUncertain(true); setPending(false);
    setError("更改结果尚未确认，请重新读取研究记录后再操作。");
  }
  function reconciled() {
    if (owner.current) return;
    needsRead.current = false; setUncertain(false); setError("");
  }
  async function run<T>(label: string, perform: (signal: AbortSignal) => Promise<T>, accept: (value: T) => void) {
    if (owner.current || needsRead.current) return false;
    const controller = new AbortController(); owner.current = controller;
    setPending(true); setError(""); setNotice("");
    try {
      const value = await readSessionRequest(perform, controller.signal);
      if (owner.current !== controller || controller.signal.aborted) return false;
      accept(value); setNotice(`${label}完成。`);
      return true;
    } catch (reason) {
      if (owner.current !== controller || controller.signal.aborted) return false;
      const status = (reason as { status?: number } | null)?.status;
      const rejected = status !== undefined && [400, 401, 403, 404, 409, 422].includes(status);
      needsRead.current = !rejected; setUncertain(!rejected);
      setError(rejected ? `${label}未完成，请检查权限或内容后重试。` : `尚未确认${label}的结果，请重新读取研究记录后再操作。`);
      return false;
    } finally {
      if (owner.current === controller) { owner.current = null; setPending(false); }
    }
  }
  return { run, pending, uncertain, error, notice, reconciled, dismiss, locked: () => Boolean(owner.current || needsRead.current) };
}
