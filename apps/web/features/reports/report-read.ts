export class ReportReadTimeoutError extends Error {
  constructor() {
    super("Report read timed out");
    this.name = "ReportReadTimeoutError";
  }
}

/** Bound document reads without allowing a stalled section to hide its siblings. */
export async function readReportContent<T>(
  request: (signal: AbortSignal) => Promise<T>,
  signal: AbortSignal,
): Promise<T> {
  if (signal.aborted) throw new Error("Report read cancelled");
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  let cancel = () => {};
  const interrupted = new Promise<never>((_, reject) => {
    cancel = () => {
      controller.abort();
      reject(new Error("Report read cancelled"));
    };
    signal.addEventListener("abort", cancel, { once: true });
    timer = setTimeout(() => {
      controller.abort();
      reject(new ReportReadTimeoutError());
    }, 10_000);
  });
  try {
    return await Promise.race([interrupted, request(controller.signal)]);
  } finally {
    clearTimeout(timer);
    signal.removeEventListener("abort", cancel);
  }
}
