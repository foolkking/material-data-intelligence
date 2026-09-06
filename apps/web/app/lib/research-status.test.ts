import { describe, expect, it } from "vitest";

import {
  RESEARCH_CANCELLING_LABEL,
  RESEARCH_CANCELLING_POLL_INTERVAL_MS,
  isResearchCancellationPending,
  researchCancellationContract,
} from "./research-status";

describe("shared research cancellation status", () => {
  it("normalizes Research and Task Center cancellation states", () => {
    expect(RESEARCH_CANCELLING_LABEL).toBe("正在取消研究");
    expect(isResearchCancellationPending("CANCELING")).toBe(true);
    expect(isResearchCancellationPending("cancel_requested")).toBe(true);
    expect(isResearchCancellationPending("RUNNING")).toBe(false);
  });

  it("keeps the cancellation refresh cadence bounded and explicit", () => {
    expect(RESEARCH_CANCELLING_POLL_INTERVAL_MS).toBe(1800);
  });

  it("fails closed for legacy Jobs and tasks without a ResearchTurn", () => {
    expect(researchCancellationContract({ researchTurnId: "turn-1", jobStatus: "RUNNING" })).toBe("MODERN_TURN");
    expect(researchCancellationContract({ researchTurnId: null, jobStatus: "RUNNING" })).toBe("NO_TURN_UNAVAILABLE");
    expect(researchCancellationContract({ researchTurnId: null, workspaceProjectionStatus: "LEGACY_READ_ONLY" })).toBe("LEGACY_READ_ONLY");
  });
});
