import type { ProductSearchResponse } from "../../app/lib/planner-api";

/** A search owns both its transport and response-body deadline. */
export async function boundedSearchRequest<T>(request: (signal: AbortSignal) => Promise<T>, signal: AbortSignal): Promise<T> {
  signal.throwIfAborted();
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  let cancel = () => {};
  const interrupted = new Promise<never>((_, reject) => {
    cancel = () => { controller.abort(); reject(new Error("Search cancelled")); };
    signal.addEventListener("abort", cancel, { once: true });
    timer = setTimeout(() => { controller.abort(); reject(new Error("Search timed out")); }, 10_000);
  });
  try { return await Promise.race([interrupted, request(controller.signal)]); }
  finally { clearTimeout(timer); signal.removeEventListener("abort", cancel); }
}

export function validateSearchResponse(result: ProductSearchResponse) {
  const kinds = ["project", "dataset", "scientific_object", "research", "report", "result"];
  if (!Array.isArray(result.items) || !Number.isInteger(result.count) || result.count < 0 || (result.nextCursor != null && typeof result.nextCursor !== "string")) throw new Error("Invalid search response");
  const seen = new Set<string>();
  for (const item of result.items) {
    const identity = `${item.kind}:${item.projectId}:${item.id}`;
    const path = `/projects/${encodeURIComponent(item.projectId)}`;
    const destination = new URL(item.href, "http://search.local");
    if (!item.id || !item.projectId || !kinds.includes(item.kind) || seen.has(identity) ||
      !item.href.startsWith("/") || destination.origin !== "http://search.local" ||
      !(destination.pathname === path || destination.pathname.startsWith(`${path}/`))) throw new Error("Search identity mismatch");
    seen.add(identity);
  }
  return result;
}
