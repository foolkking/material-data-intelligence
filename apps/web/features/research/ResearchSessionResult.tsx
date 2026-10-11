"use client";

import { useEffect, useRef, useState } from "react";
import { isAgent2ExecutionTerminal, type Agent2ProgressView } from "../../app/lib/agent2-execution-api";
import { hasAgent2ResultPresentation } from "../../app/lib/research-status";
import { ProductLink } from "../../shared/layout/ProductNavigation";
import { Agent2ScientificPresentation } from "./Agent2ScientificPresentation";
import { watchAgent2Execution, type ExecutionReadState } from "./execution-recovery";
import { ResearchTurnResultState } from "./ResearchTurnResultState";
import styles from "./ResearchConversation.module.css";

/** Inspect the same owned Turn as the conversation without changing its composer draft. */
export function ResearchSessionResult({ projectId, sessionId, turnId, onTerminal, onProgress }: {
  projectId: string; sessionId: string; turnId: string; onTerminal: () => void; onProgress?: (progress: Agent2ProgressView) => void;
}) {
  const [progress, setProgress] = useState<Agent2ProgressView | null>(null);
  const [readState, setReadState] = useState<ExecutionReadState>({ status: "connected" });
  const watcher = useRef<ReturnType<typeof watchAgent2Execution> | null>(null);
  const openTurn = useRef<HTMLAnchorElement>(null);
  const onTerminalRef = useRef(onTerminal);
  onTerminalRef.current = onTerminal;
  const onProgressRef = useRef(onProgress);
  onProgressRef.current = onProgress;
  useEffect(() => {
    setProgress(null); setReadState({ status: "connected" });
    let lastStatus: Agent2ProgressView["status"] | undefined;
    const current = watchAgent2Execution(turnId, {
      progress: next => {
        setProgress(next);
        onProgressRef.current?.(next);
        if (lastStatus && !isAgent2ExecutionTerminal(lastStatus) && isAgent2ExecutionTerminal(next.status)) onTerminalRef.current();
        lastStatus = next.status;
      },
      recovery: setReadState, cancellation: () => {}, dispatch: () => {},
    }, { observeOnly: true });
    watcher.current = current;
    return () => { current.dispose(); watcher.current = null; };
  }, [projectId, sessionId, turnId]);
  const owned = progress?.turn_id === turnId ? progress : null;
  return <>
    <div className={styles.sessionResultActions}>
      <ProductLink ref={openTurn} className="product-link-button" scroll={false}
        href={`/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(sessionId)}?turn=${encodeURIComponent(turnId)}`}>打开这次研究</ProductLink>
    </div>
    {readState.status !== "connected" ? <div className="research-result-read-error" role="status">
      <p>{readState.status === "unavailable" ? readState.message : "研究进度暂时无法读取，已打开的结果仍然保留。"}</p>
      <button type="button" className="product-secondary-action" onClick={() => watcher.current?.refresh()}>重新读取进度</button>
    </div> : null}
    {hasAgent2ResultPresentation(owned)
      ? <Agent2ScientificPresentation projectId={projectId} sessionId={sessionId} turnId={turnId} progress={owned} canModify={false} />
      : <ResearchTurnResultState turnId={turnId} progress={owned} unconfirmed={readState.status !== "connected"}
          onOpenTimeline={() => openTurn.current?.click()} />}
  </>;
}
