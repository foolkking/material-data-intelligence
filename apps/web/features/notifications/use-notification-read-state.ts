"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { listNotificationReadStates, updateNotificationReadState } from "../../app/lib/product-api";

type PendingRead = { controller: AbortController; timer: number };
const keyFor = (projectId: string, jobId: string) => `${projectId}:${jobId}`;

export function useNotificationReadState() {
  const [readKeys, setReadKeys] = useState<Set<string>>(new Set());
  const [loaded, setLoaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [readError, setReadError] = useState(false);
  const [savingKeys, setSavingKeys] = useState<Set<string>>(new Set());
  const [saveErrors, setSaveErrors] = useState<Set<string>>(new Set());
  const readRequest = useRef<PendingRead | null>(null);
  const saves = useRef(new Map<string, PendingRead>());
  const mutationVersion = useRef(0);

  const refresh = useCallback(async () => {
    if (saves.current.size) return;
    readRequest.current?.controller.abort();
    if (readRequest.current) window.clearTimeout(readRequest.current.timer);
    const controller = new AbortController();
    const version = mutationVersion.current;
    setLoading(true);
    setReadError(false);
    const timer = window.setTimeout(() => {
      controller.abort();
      readRequest.current = null;
      setLoading(false);
      setReadError(true);
    }, 10_000);
    readRequest.current = { controller, timer };
    try {
      const result = await listNotificationReadStates({ signal: controller.signal });
      if (controller.signal.aborted || version !== mutationVersion.current) return;
      setReadKeys(new Set(result.items.filter((item) => item.read).map((item) => keyFor(item.projectId, item.jobId))));
      setLoaded(true);
      setReadError(false);
    } catch {
      if (!controller.signal.aborted && version === mutationVersion.current) setReadError(true);
    } finally {
      window.clearTimeout(timer);
      if (readRequest.current?.controller === controller) {
        readRequest.current = null;
        setLoading(false);
      }
    }
  }, []);

  const setRead = useCallback(async (projectId: string, jobId: string, read: boolean) => {
    const key = keyFor(projectId, jobId);
    if (saves.current.has(key)) return;
    mutationVersion.current += 1;
    readRequest.current?.controller.abort();
    if (readRequest.current) window.clearTimeout(readRequest.current.timer);
    readRequest.current = null;
    setLoading(false);
    setSaveErrors((current) => { const next = new Set(current); next.delete(key); return next; });
    const controller = new AbortController();
    const finish = () => {
      if (saves.current.get(key)?.controller !== controller) return;
      saves.current.delete(key);
      setSavingKeys(new Set(saves.current.keys()));
    };
    const fail = () => setSaveErrors((current) => new Set(current).add(key));
    const timer = window.setTimeout(() => { controller.abort(); fail(); finish(); }, 10_000);
    saves.current.set(key, { controller, timer });
    setSavingKeys(new Set(saves.current.keys()));
    try {
      const result = await updateNotificationReadState(projectId, jobId, read, { signal: controller.signal });
      if (controller.signal.aborted) return;
      if (result.projectId !== projectId || result.jobId !== jobId || result.read !== read) throw new Error("Notification identity mismatch");
      setReadKeys((current) => {
        const next = new Set(current);
        if (read) next.add(key); else next.delete(key);
        return next;
      });
      mutationVersion.current += 1;
      return true;
    } catch {
      if (!controller.signal.aborted) fail();
    } finally {
      window.clearTimeout(timer);
      finish();
    }
  }, []);

  useEffect(() => () => {
    readRequest.current?.controller.abort();
    if (readRequest.current) window.clearTimeout(readRequest.current.timer);
    readRequest.current = null;
    for (const request of saves.current.values()) {
      request.controller.abort();
      window.clearTimeout(request.timer);
    }
    saves.current.clear();
  }, []);

  return { readKeys, loaded, loading, readError, savingKeys, saveErrors, refresh, setRead };
}
