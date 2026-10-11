import type { Agent2ProgressView } from "../../app/lib/agent2-execution-api";
import { ArtifactOpenLink, isTrustedArtifactContentHref } from "../../shared/ui/ArtifactOpenLink";
import styles from "./ResearchConversation.module.css";

function savedOutputs(turnId: string, progress?: Agent2ProgressView | null) {
  if (progress?.turn_id !== turnId) return [];
  return progress.incremental_outputs.filter(output => output && typeof output.content_url === "string"
    && isTrustedArtifactContentHref(output.content_url));
}

export function SavedResearchOutputs({ turnId, progress, heading = true }: {
  turnId: string; progress?: Agent2ProgressView | null; heading?: boolean;
}) {
  const outputs = savedOutputs(turnId, progress);
  if (!outputs.length) return null;
  return <section className="scientific-presentation scientific-tool-process scientific-saved-outputs" aria-label="已保存的工具输出">
    {heading ? <h3>已保存的工具输出</h3> : null}
    <ul aria-label="工具输出">{outputs.map((output, index) => <li key={`${output.output_key || output.artifact_id}:${index}`}>
      <ArtifactOpenLink href={output.content_url as string}>{output.display_label || "查看输出文件"}</ArtifactOpenLink>
    </li>)}</ul>
  </section>;
}

/** A selected Turn never falls back to unrelated project data or legacy scope guesses. */
export function ResearchTurnResultState({ turnId, progress, unconfirmed, onOpenTimeline }: {
  turnId: string; progress: Agent2ProgressView | null; unconfirmed: boolean; onOpenTimeline: () => void;
}) {
  const owned = progress?.turn_id === turnId ? progress : null;
  const titles: Partial<Record<Agent2ProgressView["status"], string>> = {
    ANSWERED: "本次没有新的科学结果",
    NEEDS_CLARIFICATION: "等待补充研究条件",
    UNSUPPORTED: "尚无科学结果",
    PLAN_REJECTED: "尚无科学结果",
    FAILED: "尚无科学结果",
    CANCELED: "尚无科学结果",
    CANCELING: "正在确认取消",
    RESULT_PENDING: "正在整理科学结果",
  };
  const hasOutputs = savedOutputs(turnId, owned).length > 0;
  const title = hasOutputs ? "已保存的工具输出" : !owned
    ? unconfirmed ? "结果状态尚未确认" : "正在读取本次结果状态…"
    : titles[owned.status] || "等待科学结果";
  return <section className={styles.turnResultState} aria-label="本次研究结果">
    <h2 aria-live="polite">{title}</h2>
    {owned?.status === "CANCELED" && !hasOutputs ? <p>本次研究已取消，尚未生成可展示的科学结果。</p> : null}
    {owned?.status === "FAILED" && !hasOutputs ? <p>本次研究未能生成可展示的科学结果。</p> : null}
    <SavedResearchOutputs turnId={turnId} progress={owned} heading={false} />
    <button type="button" className="product-secondary-action" onClick={onOpenTimeline}>查看研究时间线</button>
  </section>;
}
