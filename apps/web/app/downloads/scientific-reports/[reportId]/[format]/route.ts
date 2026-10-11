import {
  buildScientificReportMarkdown,
  buildScientificReportReproducibilityManifest,
  type ScientificReportView,
} from "../../../../lib/scientific-report-api";
import { isScientificReportDownload, type reportDownloadErrors } from "../../../../lib/scientific-report-download";
import { buildScientificReportBundle, ReportBundleLimitError } from "../../../../lib/scientific-report-bundle";

export const dynamic = "force-dynamic";

// Only serialize the persisted view returned by the API's account/project access check.
// This route never accepts report contents or a caller-supplied upstream URL.
export async function GET(request: Request, context: { params: Promise<{ reportId: string; format: string }> }) {
  const { reportId, format } = await context.params;
  const fail = (reason: keyof typeof reportDownloadErrors) => {
    const query = new URLSearchParams({ reason, reportId, format }).toString();
    // A relative redirect preserves the browser's origin even behind Next's localhost proxy.
    return new Response(null, { status: 303, headers: { Location: `/downloads/error?${query}`, "Cache-Control": "private, no-store" } });
  };
  if (!isScientificReportDownload(reportId, format)) return fail("missing");

  const controller = new AbortController();
  let timedOut = false;
  const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, format === "zip" ? 30_000 : 10_000);
  const abort = () => controller.abort();
  request.signal.addEventListener("abort", abort, { once: true });
  if (request.signal.aborted) controller.abort();
  try {
    // Match next.config.mjs's trusted API proxy target; never derive it from Host or query parameters.
    const target = (process.env.MDI_API_PROXY_TARGET || process.env.NEXT_PUBLIC_MDI_API_BASE_URL || "http://127.0.0.1:8005").replace(/\/$/u, "");
    const upstream = await fetch(`${target}/api/scientific-reports/${encodeURIComponent(reportId)}`, {
      headers: { cookie: request.headers.get("cookie") || "", accept: "application/json" },
      cache: "no-store",
      redirect: "error",
      signal: controller.signal,
    });
    if (!upstream.ok) {
      return fail(upstream.status === 401 ? "auth" : upstream.status === 403 ? "forbidden" : upstream.status === 404 ? "missing" : "unavailable");
    }
    const view = await upstream.json() as ScientificReportView;
    if (controller.signal.aborted) return fail(timedOut ? "timeout" : "unavailable");
    if (view.report_id !== reportId || !view.report || view.grounding_status !== "VALID") return fail("unavailable");
    const markdown = format === "markdown";
    const contents = format === "zip"
      ? new Uint8Array(await buildScientificReportBundle(view, (jobId, artifactId) => fetch(
        `${target}/planner/jobs/${encodeURIComponent(jobId)}/artifacts/${encodeURIComponent(artifactId)}/content`,
        { headers: { cookie: request.headers.get("cookie") || "" }, cache: "no-store", redirect: "error", signal: controller.signal },
      ), controller.signal)).buffer
      : markdown ? buildScientificReportMarkdown(view) : buildScientificReportReproducibilityManifest(view);
    const suffix = format === "zip" ? ".zip" : markdown ? ".md" : "-reproducibility.json";
    const title = view.report.title.replace(/[^\w\u4e00-\u9fff.-]+/gu, "-").slice(0, 96) || "scientific-report";
    return new Response(contents, { headers: {
      "Content-Type": format === "zip" ? "application/zip" : markdown ? "text/markdown; charset=utf-8" : "application/json; charset=utf-8",
      "Content-Disposition": `attachment; filename="${reportId}${suffix}"; filename*=UTF-8''${encodeURIComponent(title + suffix)}`,
      "Cache-Control": "private, no-store",
      "X-Content-Type-Options": "nosniff",
    } });
  } catch (error) {
    return fail(timedOut ? "timeout" : error instanceof ReportBundleLimitError ? "bundle_limit" : "unavailable");
  } finally {
    clearTimeout(timeout);
    request.signal.removeEventListener("abort", abort);
  }
}
