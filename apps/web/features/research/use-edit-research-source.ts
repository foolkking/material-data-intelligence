"use client";
import { useEffect, useRef, useState } from "react";
import type { Agent2ResearchTurnResult, Agent2TurnDetail } from "../../app/lib/agent2-research-api";
import { readBranchResult, readBranchTurn } from "./branch-source";

type SourceState = {
  scope: string; turn: Agent2TurnDetail | null; result: Agent2ResearchTurnResult | null;
  turnPending: boolean; resultPending: boolean; turnFailed: boolean; resultFailed: boolean;
};
export function useEditResearchSource(projectId: string, sessionId?: string, turnId?: string) {
  const scope = JSON.stringify([projectId, sessionId, turnId]);
  const blank = (): SourceState => ({ scope, turn: null, result: null, turnPending: Boolean(turnId), resultPending: Boolean(turnId), turnFailed: false, resultFailed: false });
  const [state, setState] = useState<SourceState>(blank);
  const retry = useRef(() => {});
  useEffect(() => {
    const controller = new AbortController(); let current = blank();
    setState(current);
    const publish = (change: Partial<SourceState>) => { if (!controller.signal.aborted) { current = { ...current, ...change }; setState(current); } };
    async function readTurn() {
      publish({ turnPending: true });
      try { publish({ turn: await readBranchTurn(projectId, sessionId!, turnId!, controller.signal), turnFailed: false }); }
      catch { publish({ turnFailed: true }); }
      finally { publish({ turnPending: false }); }
    }
    async function readResult() {
      publish({ resultPending: true });
      try { publish({ result: await readBranchResult(projectId, turnId!, controller.signal), resultFailed: false }); }
      catch { publish({ resultFailed: true }); }
      finally { publish({ resultPending: false }); }
    }
    retry.current = () => {
      if (controller.signal.aborted) return;
      if (current.turnFailed && !current.turnPending) void readTurn();
      if (current.resultFailed && !current.resultPending) void readResult();
    };
    if (sessionId && turnId) { void readTurn(); void readResult(); }
    return () => { controller.abort(); retry.current = () => {}; };
    // Read ownership is bound to the complete source identity.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scope]);
  const visible = state.scope === scope ? state : blank();
  const pending = visible.turnPending || visible.resultPending;
  const failed = visible.turnFailed || visible.resultFailed;
  return { ...visible, pending, failed, retry: () => retry.current(),
    loadState: !turnId ? "idle" as const : failed ? "error" as const : pending ? "loading" as const : "ready" as const };
}
