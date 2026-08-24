const API_BASE = (process.env.NEXT_PUBLIC_MDI_API_BASE_URL || (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")).replace(/\/$/, "");

export type ScientificReportFinding = {
  statement: string;
  finding_refs: string[];
  fact_refs: string[];
  evidence_refs: string[];
};

export type ScientificReportFigure = {
  figure_ref: string;
  caption: string;
  fact_refs: string[];
  evidence_refs: string[];
};

export type ScientificReportContent = {
  contract_version: "1.0";
  title: string;
  research_question: string;
  summary: string;
  main_findings: ScientificReportFinding[];
  primary_figures: ScientificReportFigure[];
  supporting_results: Array<{ result_item_ref: string; description: string }>;
  method_summary: string;
  limitations: Array<{ statement: string; source_refs: string[] }>;
  data_sources: string[];
  evidence_refs: string[];
  reproducibility_summary: string;
  omitted_supporting_items: string[];
};

export type ScientificReportView = {
  report_id: string;
  snapshot_id: string;
  project_id: string;
  research_turn_id: string;
  scientific_result_snapshot_id: string;
  scientific_interpretation_id: string;
  title: string;
  relevance_at_generation: "CURRENT" | "STALE" | "SOURCE_MISSING" | "INVALIDATED";
  current_effective_relevance: "CURRENT" | "STALE" | "SOURCE_MISSING" | "INVALIDATED";
  grounding_status: "VALID";
  scientific_context: string;
  finding_count: number;
  figure_count: number;
  source_fingerprint: string;
  created_at: string;
  viewer_sources?: Array<{ source_ref: string; object_id: string; version_id: string; object_type: string; display_name: string; is_current_version: boolean }>;
  report?: ScientificReportContent;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { ...init, credentials: "include" });
  if (!response.ok) {
    const error = new Error(`Scientific report request failed (${response.status})`) as Error & { status?: number };
    error.status = response.status;
    throw error;
  }
  return (await response.json()) as T;
}

export const listScientificReports = (projectId: string) => request<{ items: ScientificReportView[]; count: number }>(`/api/projects/${encodeURIComponent(projectId)}/scientific-reports`);
export const getScientificReport = (reportId: string) => request<ScientificReportView>(`/api/scientific-reports/${encodeURIComponent(reportId)}`);
export const getScientificReportForTurn = (turnId: string) => request<ScientificReportView>(`/api/research/turns/${encodeURIComponent(turnId)}/report`);
export const requestScientificReport = (turnId: string) => request<{ generation_id: string; status: string }>(`/api/research/turns/${encodeURIComponent(turnId)}/report`, { method: "POST" });
