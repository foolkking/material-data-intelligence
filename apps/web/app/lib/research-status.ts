import type { Agent2ProgressView } from "./agent2-execution-api";

export function canReadSavedAgent2Result(progress: Agent2ProgressView): boolean {
  return progress.preserved_result_available === true || progress.incremental_outputs.length > 0 || progress.warnings.some((warning) =>
    typeof warning !== "string" && warning.code.startsWith("INTERPRETATION_"),
  );
}

export function hasAgent2ResultPresentation(progress: Agent2ProgressView | null): boolean {
  return Boolean(progress && (["COMPLETED", "PARTIAL", "RESULT_READY", "INTERPRETING"].includes(progress.status)
    || (["FAILED", "CANCELED"].includes(progress.status) && canReadSavedAgent2Result(progress))));
}

export const RESEARCH_CANCELLING_LABEL = "正在取消研究";
export const RESEARCH_CANCELLING_POLL_INTERVAL_MS = 1_800;

export function canCancelResearchTurn(status: string | null | undefined): boolean {
  return ["RECEIVED", "RESOLVING_CONTEXT", "ORCHESTRATING", "READY_TO_PLAN", "PLANNING", "PLAN_READY", "QUEUED", "RUNNING", "INTERPRETING"].includes(status || "");
}

export type ResearchCancellationContract =
  | "MODERN_TURN"
  | "LEGACY_READ_ONLY"
  | "NO_TURN_UNAVAILABLE";

export function researchCancellationContract(input: {
  researchTurnId?: string | null;
  jobStatus?: string | null;
  workspaceProjectionStatus?: string | null;
}): ResearchCancellationContract {
  if (input.workspaceProjectionStatus === "LEGACY_READ_ONLY") {
    return "LEGACY_READ_ONLY";
  }
  if (input.researchTurnId) return "MODERN_TURN";
  return "NO_TURN_UNAVAILABLE";
}

export function isResearchCancellationPending(
  status: string | null | undefined,
): boolean {
  const normalized = String(status || "").trim().toUpperCase();
  return normalized === "CANCELING" || normalized === "CANCEL_REQUESTED";
}
