"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getAgent2ContextManifest, listAgent2ResearchTurns, type Agent2ContextManifest, type Agent2ContextManifestResponse, type Agent2TurnResponse } from "../../app/lib/agent2-research-api";
import { readSessionRequest } from "./session-management";

export function validateContextManifest(value: Agent2ContextManifestResponse, projectId: string, sessionId: string, turnId: string) {
  const validate = (manifest: Agent2ContextManifest) => {
    if (!manifest || manifest.project_id !== projectId || manifest.research_session_id !== sessionId || manifest.research_turn_id !== turnId ||
        !manifest.context_manifest_id || !manifest.operation || !Array.isArray(manifest.included_items) || !Array.isArray(manifest.excluded_items) ||
        manifest.included_items.some((item) => !item?.item_id || !item.kind)) throw new Error("Context manifest identity mismatch");
  };
  if (value?.turn_id !== turnId) throw new Error("Context response identity mismatch");
  validate(value.manifest);
  if (value.manifests !== undefined && !Array.isArray(value.manifests)) throw new Error("Context history unavailable");
  for (const entry of value.manifests || []) {
    validate(entry?.manifest);
    if (entry.operation !== entry.manifest.operation) throw new Error("Context operation mismatch");
  }
  if (value.result_sources !== undefined) {
    const references = new Set([value.manifest, ...(value.manifests || []).map(entry => entry.manifest)]
      .flatMap(manifest => manifest.included_items)
      .filter(item => item.kind === "SCIENTIFIC_RESULT" && item.authorization_checked === true && item.server_side_source_identity === item.result_ref)
      .map(item => item.result_ref));
    if (!Array.isArray(value.result_sources) || value.result_sources.length > 128 ||
        new Set(value.result_sources.map(source => source?.result_snapshot_id)).size !== value.result_sources.length ||
        value.result_sources.some(source => !source || source.project_id !== projectId ||
          typeof source.result_snapshot_id !== "string" || !references.has(source.result_snapshot_id) ||
          typeof source.research_session_id !== "string" || !source.research_session_id.trim() ||
          typeof source.research_turn_id !== "string" || !source.research_turn_id.trim())) {
      throw new Error("Context result source identity mismatch");
    }
  }
  return value;
}

export function validateTurnDirectory(items: Agent2TurnResponse[], projectId: string, sessionId: string) {
  if (!Array.isArray(items) || new Set(items.map((item) => item?.turn_id)).size !== items.length || items.some((item) =>
    !item?.turn_id || (item.id && item.id !== item.turn_id) || item.project_id !== projectId || item.research_session_id !== sessionId ||
    !item.user_message?.id || typeof item.user_message.content !== "string" || !item.user_message.content.trim() ||
    !Number.isFinite(item.sequence_no))) throw new Error("Research turn directory identity mismatch");
  return items;
}

// Retain successful reads only inside their exact scope. Each refresh owns its
// deadline, including response parsing; canceled or late responses cannot publish.
function useScopedResearchRead<T>(scope: string, enabled: boolean, refreshKey: string, read: (signal: AbortSignal) => Promise<T>) {
  const [state, setState] = useState<{ scope: string; data: T | null; pending: boolean; failed: boolean }>({ scope, data: null, pending: enabled, failed: false });
  const [retryKey, setRetryKey] = useState(0);
  const owner = useRef<AbortController | null>(null);
  useEffect(() => {
    const controller = new AbortController(); owner.current = controller;
    setState((previous) => ({ scope, data: previous.scope === scope && enabled ? previous.data : null, pending: enabled, failed: false }));
    if (enabled) void readSessionRequest(read, controller.signal)
      .then((data) => { if (!controller.signal.aborted) setState({ scope, data, pending: false, failed: false }); })
      .catch(() => { if (!controller.signal.aborted) setState((previous) => ({ ...previous, pending: false, failed: true })); })
      .finally(() => { if (owner.current === controller) owner.current = null; });
    return () => { controller.abort(); if (owner.current === controller) owner.current = null; };
  }, [scope, enabled, refreshKey, retryKey, read]);
  const retry = useCallback(() => { if (!owner.current) setRetryKey((value) => value + 1); }, []);
  return { ...(enabled && state.scope === scope ? state : { scope, data: null, pending: enabled, failed: false }), retry };
}

export function useResearchContextNavigation(projectId: string, sessionId?: string, turnId?: string, status?: string, browseSession = false) {
  const readDirectory = useCallback(async (signal: AbortSignal) => validateTurnDirectory(
    await listAgent2ResearchTurns(projectId, sessionId!, { signal }), projectId, sessionId!,
  ), [projectId, sessionId]);
  const directory = useScopedResearchRead(JSON.stringify([projectId, sessionId]), Boolean(projectId && sessionId && (turnId || browseSession)), JSON.stringify([turnId, status]), readDirectory);
  // A session landing page has no explicit Turn URL. Read the latest owned
  // record for inspection only; never change submission scope or draft identity.
  const selectedTurnId = turnId || (browseSession ? directory.data?.reduce<Agent2TurnResponse | undefined>(
    (latest, item) => !latest || item.sequence_no > latest.sequence_no ? item : latest, undefined,
  )?.turn_id : undefined);
  const readContext = useCallback(async (signal: AbortSignal) => validateContextManifest(
    await getAgent2ContextManifest(selectedTurnId!, { signal }), projectId, sessionId!, selectedTurnId!,
  ), [projectId, sessionId, selectedTurnId]);
  const context = useScopedResearchRead(JSON.stringify([projectId, sessionId, selectedTurnId]), Boolean(projectId && sessionId && selectedTurnId), status || "", readContext);
  return { context, directory, selectedTurnId };
}
