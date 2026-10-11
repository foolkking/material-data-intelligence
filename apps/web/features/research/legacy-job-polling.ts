import { getPlannerJob, getPlannerJobArtifacts, getPlannerJobEvents, type Artifact, type JobEvent, type PlannerJobDetail } from "../../app/lib/planner-api";
import { readSessionRequest } from "./session-management";

export type LegacyJobReadPart = "运行详情" | "运行记录" | "科学结果";
export const legacyJobIsTerminal = (status: string | undefined) => ["completed", "partial_success", "failed", "cancelled", "canceled"].includes(String(status).toLowerCase());

export function validateLegacyJob(detail: PlannerJobDetail, jobId: string, projectId: string) {
  if (!detail || typeof detail.status !== "string" || !detail.status ||
      (detail.id && detail.id !== jobId) || (detail.jobId && detail.jobId !== jobId) ||
      (detail.projectId && detail.projectId !== projectId)) throw new Error("Job identity mismatch");
}

/** Each stream owns its deadline and retry; optional records cannot hold up job status. */
export function watchLegacyJob(jobId: string, projectId: string, callbacks: {
  detail: (value: PlannerJobDetail) => void;
  events: (value: JobEvent[]) => void;
  artifacts: (value: Artifact[]) => void;
  failure: (part: LegacyJobReadPart, failed: boolean) => void;
}) {
  const controller = new AbortController();
  const timers = new Set<ReturnType<typeof setTimeout>>();
  let terminal = false;
  let lastSeq = 0;

  function stream<T>(part: LegacyJobReadPart, request: (signal: AbortSignal) => Promise<T>, accept: (value: T) => void) {
    let pending = false;
    let trailingRead = false;
    let failures = 0;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const refresh = async (afterTerminal = false) => {
      if (controller.signal.aborted) return;
      if (pending) { trailingRead ||= afterTerminal; return; }
      if (timer) { clearTimeout(timer); timers.delete(timer); timer = undefined; }
      pending = true;
      let failed = false;
      try {
        const value = await readSessionRequest(request, controller.signal);
        if (controller.signal.aborted) return;
        accept(value);
        failures = 0;
        callbacks.failure(part, false);
      } catch {
        if (controller.signal.aborted) return;
        failed = true;
        failures += 1;
        callbacks.failure(part, true);
      } finally {
        pending = false;
        if (!controller.signal.aborted && (trailingRead || !terminal || failed)) {
          const delay = trailingRead ? 0 : failed ? Math.min(2500 * 2 ** Math.min(failures - 1, 2), 8000) : 1400;
          trailingRead = false;
          timer = setTimeout(() => { timers.delete(timer!); timer = undefined; void refresh(); }, delay);
          timers.add(timer);
        }
      }
    };
    return refresh;
  }

  const events = stream("运行记录", (signal) => getPlannerJobEvents(jobId, lastSeq, { signal }), (value) => {
    if (!Array.isArray(value) || value.some((item) => item.jobId && item.jobId !== jobId)) throw new Error("Job events mismatch");
    lastSeq = Math.max(lastSeq, ...value.map((item) => item.seq || 0));
    callbacks.events(value);
  });
  const artifacts = stream("科学结果", (signal) => getPlannerJobArtifacts(jobId, { signal }), (value) => {
    if (!Array.isArray(value) || value.some((item) => item.jobId && item.jobId !== jobId)) throw new Error("Job artifacts mismatch");
    callbacks.artifacts(value);
  });
  const detail = stream("运行详情", (signal) => getPlannerJob(jobId, { signal }), (value) => {
    validateLegacyJob(value, jobId, projectId);
    const justFinished = !terminal && legacyJobIsTerminal(value.status);
    terminal ||= justFinished;
    callbacks.detail(value);
    if (justFinished) { void events(true); void artifacts(true); }
  });
  void events();
  void artifacts();
  void detail();
  return () => { controller.abort(); timers.forEach(clearTimeout); timers.clear(); };
}
