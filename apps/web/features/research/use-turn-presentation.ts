"use client";

import { useEffect, useRef, useState } from "react";
import { getAgent2ResearchTurnInterpretation, getAgent2ResearchTurnResult, type Agent2ResearchTurnInterpretation, type Agent2ResearchTurnResult } from "../../app/lib/agent2-research-api";
import { readSessionRequest } from "./session-management";

type ReadState<T> = { scope: string; value: T | null; pending: boolean; failed: boolean; notReady?: boolean };

/** Sibling reads settle independently; successful content survives a failed reread. */
function useTurnRead<T>(projectId: string, turnId: string,
  read: (id: string, options: { signal: AbortSignal }) => Promise<T>,
  validate: (value: T, projectId: string, turnId: string) => void, enabled = true) {
  const scope = JSON.stringify([projectId, turnId]);
  const [state, setState] = useState<ReadState<T>>({ scope, value: null, pending: true, failed: false });
  const retry = useRef(() => {});
  useEffect(() => {
    const controller = new AbortController();
    let pending = false;
    setState({ scope, value: null, pending: true, failed: false });
    if (!enabled) return () => { controller.abort(); retry.current = () => {}; };
    const refresh = async () => {
      if (pending || controller.signal.aborted) return;
      pending = true;
      setState((current) => ({ ...current, pending: true }));
      try {
        const value = await readSessionRequest((signal) => read(turnId, { signal }), controller.signal);
        if (controller.signal.aborted) return;
        validate(value, projectId, turnId);
        setState({ scope, value, pending: false, failed: false });
      } catch (error) {
        const notReady = error instanceof Error && "code" in error && error.code === "SCIENTIFIC_RESULT_NOT_READY";
        if (!controller.signal.aborted) setState((current) => ({ ...current, pending: false, failed: true, notReady }));
      } finally { pending = false; }
    };
    retry.current = () => { void refresh(); };
    void refresh();
    return () => { controller.abort(); retry.current = () => {}; };
  }, [scope, projectId, turnId, read, validate, enabled]);
  // Effect cleanup occurs after rendering: never render the previous Turn in that gap.
  return { ...(state.scope === scope ? state : { value: null, pending: true, failed: false, notReady: false }), retry: () => retry.current() };
}

function validateResult(value: Agent2ResearchTurnResult, projectId: string, turnId: string) {
  if (!value || value.research_turn_id !== turnId || !value.result_id ||
      !Array.isArray(value.source_object_refs) || value.source_object_refs.some((source) => source.project_id && source.project_id !== projectId)) {
    throw new Error("Scientific result identity mismatch");
  }
  for (const field of ["result_items", "facts", "figures", "tables", "evidence", "artifacts", "scientific_selections"] as const) {
    if (value[field] !== undefined && !Array.isArray(value[field])) throw new Error("Scientific result content invalid");
  }
}
function validateInterpretation(value: Agent2ResearchTurnInterpretation, _projectId: string, turnId: string) {
  if (!value || value.research_turn_id !== turnId || !value.interpretation_id || typeof value.status !== "string") throw new Error("Interpretation identity mismatch");
}

export function useTurnPresentation(projectId: string, turnId: string, interpretationReady = true) {
  const result = useTurnRead(projectId, turnId, getAgent2ResearchTurnResult, validateResult);
  const interpretation = useTurnRead(projectId, turnId, getAgent2ResearchTurnInterpretation, validateInterpretation, interpretationReady);
  return { result, interpretation };
}
