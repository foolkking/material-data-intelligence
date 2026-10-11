"use client";

import { useEffect, useRef, useState } from "react";
import { validateMaterials, type ResearchMaterials } from "./research-materials";

type Draft = { value: ResearchMaterials | null; error: string };
export function useResearchMaterials(projectId: string, draftKey: string) {
  const cache = useRef(new Map<string, Draft>());
  const key = `${draftKey}:materials`;
  const currentKey = useRef(key); currentKey.current = key;
  const [snapshot, setSnapshot] = useState<{ key: string; draft: Draft } | null>(null);
  useEffect(() => {
    const existing = cache.current.get(key);
    if (existing) { setSnapshot({ key, draft: existing }); return; }
    let loaded: Draft = { value: null, error: "" };
    try {
      const raw = window.sessionStorage.getItem(key);
      if (raw) {
        if (raw.length > 256_000) throw new Error("Oversized material draft");
        loaded = { value: validateMaterials(JSON.parse(raw), projectId), error: "" };
      }
    } catch { loaded = { value: null, error: "所选材料暂时无法恢复，请重新选择材料。" }; }
    cache.current.set(key, loaded);
    setSnapshot({ key, draft: loaded });
  }, [key, projectId]);
  const pending = snapshot?.key !== key;
  const draft = !pending ? snapshot!.draft : { value: null, error: "" };
  function write(target: string, value: ResearchMaterials | null) {
    if (value) validateMaterials(value, projectId);
    cache.current.set(target, { value, error: "" });
    try {
      if (value) window.sessionStorage.setItem(target, JSON.stringify(value));
      else window.sessionStorage.removeItem(target);
    } catch { /* The in-memory selection remains usable if storage is unavailable. */ }
    if (target === currentKey.current) setSnapshot({ key: target, draft: { value, error: "" } });
  }
  return { ...draft, pending, set: (value: ResearchMaterials | null) => write(key, value),
    copyTo: (nextDraftKey: string) => { if (draft.value) write(`${nextDraftKey}:materials`, draft.value); },
    clearKey: (targetDraftKey: string) => write(`${targetDraftKey}:materials`, null) };
}
