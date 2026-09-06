export const RESEARCH_PERFORMANCE_STORAGE_KEY =
  "mdi:research-performance:v1";

export const RESEARCH_PERFORMANCE_SAMPLE_LIMIT = 50;

export const RESEARCH_PERFORMANCE_BUDGETS_MS = Object.freeze({
  acknowledgement: 500,
  firstTruthfulProgress: 1500,
});

export type ResearchPerformanceSample = Readonly<{
  attemptId: string;
  turnId: string;
  status: string;
  acknowledgementMs: number | null;
  firstTruthfulProgressMs: number;
  recordedAt: string;
}>;

type PendingResearchPerformance = Readonly<{
  attemptId: string;
  startedAtMs: number;
  acknowledgedAtMs: number | null;
  turnId: string | null;
}>;

type ResearchPerformanceLedger = Readonly<{
  pending: PendingResearchPerformance | null;
  samples: readonly ResearchPerformanceSample[];
}>;

type StorageLike = Pick<Storage, "getItem" | "setItem">;

type AnimationFrameTarget = Pick<
  Window,
  "requestAnimationFrame" | "cancelAnimationFrame"
>;

const EMPTY_LEDGER: ResearchPerformanceLedger = Object.freeze({
  pending: null,
  samples: Object.freeze([]),
});

function currentStorage(): StorageLike | null {
  if (typeof window === "undefined") return null;
  try {
    return window.sessionStorage;
  } catch {
    return null;
  }
}

function readLedger(storage: StorageLike | null): ResearchPerformanceLedger {
  if (!storage) return EMPTY_LEDGER;
  try {
    const parsed = JSON.parse(
      storage.getItem(RESEARCH_PERFORMANCE_STORAGE_KEY) || "{}",
    ) as Partial<ResearchPerformanceLedger>;
    const samples = Array.isArray(parsed.samples)
      ? parsed.samples
          .filter(
            (sample): sample is ResearchPerformanceSample =>
              Boolean(
                sample &&
                  typeof sample.attemptId === "string" &&
                  typeof sample.turnId === "string" &&
                  typeof sample.status === "string" &&
                  (sample.acknowledgementMs === null ||
                    Number.isFinite(sample.acknowledgementMs)) &&
                  Number.isFinite(sample.firstTruthfulProgressMs) &&
                  typeof sample.recordedAt === "string",
              ),
          )
          .slice(-RESEARCH_PERFORMANCE_SAMPLE_LIMIT)
      : [];
    const pending =
      parsed.pending &&
      typeof parsed.pending.attemptId === "string" &&
      Number.isFinite(parsed.pending.startedAtMs) &&
      (parsed.pending.acknowledgedAtMs === null ||
        Number.isFinite(parsed.pending.acknowledgedAtMs)) &&
      (parsed.pending.turnId === null ||
        typeof parsed.pending.turnId === "string")
        ? parsed.pending
        : null;
    return Object.freeze({
      pending,
      samples: Object.freeze(samples),
    });
  } catch {
    return EMPTY_LEDGER;
  }
}

function writeLedger(
  storage: StorageLike | null,
  ledger: ResearchPerformanceLedger,
): void {
  if (!storage) return;
  try {
    storage.setItem(RESEARCH_PERFORMANCE_STORAGE_KEY, JSON.stringify(ledger));
  } catch {
    // Performance diagnostics must never block Research.
  }
}

function boundedElapsed(startedAtMs: number, finishedAtMs: number): number {
  return Math.max(0, Math.round((finishedAtMs - startedAtMs) * 10) / 10);
}

function createAttemptId(): string {
  if (
    typeof globalThis.crypto !== "undefined" &&
    typeof globalThis.crypto.randomUUID === "function"
  ) {
    return globalThis.crypto.randomUUID();
  }
  return `research-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

export function beginResearchPerformanceAttempt(
  storage: StorageLike | null = currentStorage(),
  now: () => number = Date.now,
): string {
  const ledger = readLedger(storage);
  const attemptId = createAttemptId();
  writeLedger(storage, {
    pending: {
      attemptId,
      startedAtMs: now(),
      acknowledgedAtMs: null,
      turnId: null,
    },
    samples: ledger.samples,
  });
  return attemptId;
}

export function markResearchSubmitAcknowledged(
  attemptId: string,
  storage: StorageLike | null = currentStorage(),
  now: () => number = Date.now,
): void {
  const ledger = readLedger(storage);
  if (
    !ledger.pending ||
    ledger.pending.attemptId !== attemptId ||
    ledger.pending.acknowledgedAtMs !== null
  ) {
    return;
  }
  writeLedger(storage, {
    pending: { ...ledger.pending, acknowledgedAtMs: now() },
    samples: ledger.samples,
  });
}

export function scheduleResearchSubmitAcknowledgement(
  attemptId: string,
  target: AnimationFrameTarget = window,
): () => void {
  let secondFrame: number | null = null;
  const firstFrame = target.requestAnimationFrame(() => {
    secondFrame = target.requestAnimationFrame(() => {
      markResearchSubmitAcknowledged(attemptId);
    });
  });
  return () => {
    target.cancelAnimationFrame(firstFrame);
    if (secondFrame !== null) target.cancelAnimationFrame(secondFrame);
  };
}

export function bindResearchPerformanceTurn(
  attemptId: string,
  turnId: string,
  storage: StorageLike | null = currentStorage(),
): void {
  const ledger = readLedger(storage);
  if (!ledger.pending || ledger.pending.attemptId !== attemptId || !turnId) {
    return;
  }
  writeLedger(storage, {
    pending: { ...ledger.pending, turnId },
    samples: ledger.samples,
  });
}

export function recordResearchFirstTruthfulProgress(
  turnId: string,
  status: string,
  storage: StorageLike | null = currentStorage(),
  now: () => number = Date.now,
): ResearchPerformanceSample | null {
  const ledger = readLedger(storage);
  const pending = ledger.pending;
  if (!pending || pending.turnId !== turnId || !status.trim()) return null;
  const finishedAtMs = now();
  const sample: ResearchPerformanceSample = Object.freeze({
    attemptId: pending.attemptId,
    turnId,
    status: status.trim(),
    acknowledgementMs:
      pending.acknowledgedAtMs === null
        ? null
        : boundedElapsed(pending.startedAtMs, pending.acknowledgedAtMs),
    firstTruthfulProgressMs: boundedElapsed(
      pending.startedAtMs,
      finishedAtMs,
    ),
    recordedAt: new Date(finishedAtMs).toISOString(),
  });
  const samples = [...ledger.samples, sample].slice(
    -RESEARCH_PERFORMANCE_SAMPLE_LIMIT,
  );
  writeLedger(storage, { pending: null, samples });
  if (typeof window !== "undefined") {
    if (sample.acknowledgementMs !== null) {
      window.performance?.measure(
        `mdi:research-submit-acknowledgement:${sample.attemptId}`,
        { start: 0, duration: sample.acknowledgementMs },
      );
    }
    window.performance?.measure(
      `mdi:research-first-truthful-progress:${sample.attemptId}`,
      { start: 0, duration: sample.firstTruthfulProgressMs },
    );
    window.dispatchEvent(
      new CustomEvent("mdi:research-performance", { detail: sample }),
    );
  }
  return sample;
}

function percentile(values: readonly number[], fraction: number): number | null {
  if (!values.length) return null;
  const sorted = [...values].sort((left, right) => left - right);
  const index = Math.max(
    0,
    Math.min(sorted.length - 1, Math.ceil(sorted.length * fraction) - 1),
  );
  return sorted[index];
}

export function summarizeResearchPerformance(
  storage: StorageLike | null = currentStorage(),
): Readonly<{
  sampleCount: number;
  acknowledgement: Readonly<{ p50: number | null; p95: number | null }>;
  firstTruthfulProgress: Readonly<{
    p50: number | null;
    p95: number | null;
  }>;
}> {
  const samples = readLedger(storage).samples;
  const acknowledgements = samples
    .map((sample) => sample.acknowledgementMs)
    .filter((value): value is number => value !== null);
  const firstProgress = samples.map(
    (sample) => sample.firstTruthfulProgressMs,
  );
  return Object.freeze({
    sampleCount: samples.length,
    acknowledgement: Object.freeze({
      p50: percentile(acknowledgements, 0.5),
      p95: percentile(acknowledgements, 0.95),
    }),
    firstTruthfulProgress: Object.freeze({
      p50: percentile(firstProgress, 0.5),
      p95: percentile(firstProgress, 0.95),
    }),
  });
}
