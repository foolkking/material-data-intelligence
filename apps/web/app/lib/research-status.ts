export const RESEARCH_CANCELLING_LABEL = "正在取消研究";
export const RESEARCH_CANCELLING_POLL_INTERVAL_MS = 1_800;

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
