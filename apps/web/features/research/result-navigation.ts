import type { Agent2ResearchTurnResult } from "../../app/lib/agent2-research-api";

export type ResearchResultTarget = { snapshotId: string; itemId: string; requestKey?: number };
export type ResearchVisualTarget = { key: string; artifactIds: readonly string[]; missing: boolean };

/** A citation may select only outputs belonging to its exact saved result item. */
export function resolveResultVisualTarget(result: Agent2ResearchTurnResult, target?: ResearchResultTarget): ResearchVisualTarget | undefined {
  if (!target) return undefined;
  const matches = target.snapshotId && result.result_snapshot_id === target.snapshotId && target.itemId
    ? (result.result_items || []).filter(item => item.id === target.itemId) : [];
  return {
    key: JSON.stringify([result.result_snapshot_id, target.snapshotId, target.itemId, target.requestKey || 0]),
    artifactIds: matches.length === 1 ? matches[0].artifact_ids || [] : [],
    missing: matches.length !== 1,
  };
}
