import { LegacyAnalysisCompatibility } from "../components/LegacyCompatibilityPages";

/**
 * Compatibility entry point for historical `/analysis?jobId=...` links.
 *
 * The legacy PlannerWorkbench remains available because it is still useful for
 * developer/diagnostic links. When a job can be resolved, the user is given an
 * explicit path into the project-scoped Research experience rather than
 * silently dropping the job context.
 */
export default async function AnalysisPage({ searchParams }: { searchParams?: Promise<{ jobId?: string | string[] }> }) {
  const query = searchParams ? await searchParams : {};
  const jobId = Array.isArray(query.jobId) ? query.jobId[0] : query.jobId;
  return <LegacyAnalysisCompatibility jobId={jobId?.trim() || ""} />;
}
