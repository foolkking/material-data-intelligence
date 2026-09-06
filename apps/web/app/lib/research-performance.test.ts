import { describe, expect, it, vi } from "vitest";
import {
  RESEARCH_PERFORMANCE_SAMPLE_LIMIT,
  beginResearchPerformanceAttempt,
  bindResearchPerformanceTurn,
  markResearchSubmitAcknowledged,
  recordResearchFirstTruthfulProgress,
  scheduleResearchSubmitAcknowledgement,
  summarizeResearchPerformance,
} from "./research-performance";

class MemoryStorage {
  private readonly values = new Map<string, string>();

  getItem(key: string) {
    return this.values.get(key) ?? null;
  }

  setItem(key: string, value: string) {
    this.values.set(key, value);
  }
}

describe("research performance diagnostics", () => {
  it("records acknowledgement and first persisted progress across a route handoff", () => {
    const storage = new MemoryStorage();
    const attemptId = beginResearchPerformanceAttempt(storage, () => 1000);
    markResearchSubmitAcknowledged(attemptId, storage, () => 1080);
    bindResearchPerformanceTurn(attemptId, "turn-exact", storage);

    const sample = recordResearchFirstTruthfulProgress(
      "turn-exact",
      "PLAN_REQUESTED",
      storage,
      () => 1425,
    );

    expect(sample).toMatchObject({
      turnId: "turn-exact",
      status: "PLAN_REQUESTED",
      acknowledgementMs: 80,
      firstTruthfulProgressMs: 425,
    });
  });

  it("fails closed for a progress update from another Turn", () => {
    const storage = new MemoryStorage();
    const attemptId = beginResearchPerformanceAttempt(storage, () => 1000);
    bindResearchPerformanceTurn(attemptId, "turn-a", storage);

    expect(
      recordResearchFirstTruthfulProgress(
        "turn-b",
        "RUNNING",
        storage,
        () => 2000,
      ),
    ).toBeNull();
    expect(summarizeResearchPerformance(storage).sampleCount).toBe(0);
  });

  it("records only the first truthful progress state for an exact Turn", () => {
    const storage = new MemoryStorage();
    const attemptId = beginResearchPerformanceAttempt(storage, () => 1000);
    bindResearchPerformanceTurn(attemptId, "turn-a", storage);

    expect(
      recordResearchFirstTruthfulProgress(
        "turn-a",
        "ORCHESTRATING",
        storage,
        () => 1200,
      ),
    ).not.toBeNull();
    expect(
      recordResearchFirstTruthfulProgress(
        "turn-a",
        "RUNNING",
        storage,
        () => 1500,
      ),
    ).toBeNull();
    expect(summarizeResearchPerformance(storage).sampleCount).toBe(1);
  });

  it("keeps a bounded sample ledger and reports deterministic p50/p95", () => {
    const storage = new MemoryStorage();
    for (let index = 1; index <= RESEARCH_PERFORMANCE_SAMPLE_LIMIT + 5; index += 1) {
      const attemptId = beginResearchPerformanceAttempt(
        storage,
        () => index * 1000,
      );
      markResearchSubmitAcknowledged(
        attemptId,
        storage,
        () => index * 1000 + index,
      );
      bindResearchPerformanceTurn(attemptId, `turn-${index}`, storage);
      recordResearchFirstTruthfulProgress(
        `turn-${index}`,
        "PLAN_REQUESTED",
        storage,
        () => index * 1000 + index * 10,
      );
    }

    expect(summarizeResearchPerformance(storage)).toEqual({
      sampleCount: RESEARCH_PERFORMANCE_SAMPLE_LIMIT,
      acknowledgement: { p50: 30, p95: 53 },
      firstTruthfulProgress: { p50: 300, p95: 530 },
    });
  });

  it("measures acknowledgement after two browser paint opportunities and cancels cleanly", () => {
    const callbacks = new Map<number, FrameRequestCallback>();
    let nextId = 0;
    const target = {
      requestAnimationFrame: vi.fn((callback: FrameRequestCallback) => {
        nextId += 1;
        callbacks.set(nextId, callback);
        return nextId;
      }),
      cancelAnimationFrame: vi.fn((id: number) => callbacks.delete(id)),
    };

    const cancel = scheduleResearchSubmitAcknowledgement(
      "attempt",
      target as unknown as Window,
    );
    callbacks.get(1)?.(0);
    expect(target.requestAnimationFrame).toHaveBeenCalledTimes(2);
    cancel();
    expect(callbacks.has(2)).toBe(false);
  });
});
