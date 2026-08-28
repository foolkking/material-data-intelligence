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
  figure_sources?: Array<{ figure_ref: string; artifact_ids: string[]; job_id?: string | null }>;
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

/** Build a bounded, deterministic Markdown export from an authorized report snapshot. */
export function buildScientificReportMarkdown(view: ScientificReportView): string {
  const report = view.report;
  if (!report) return "";
  const lines = [
    `# ${report.title}`,
    "",
    `- Report: ${view.report_id}`,
    `- Snapshot: ${view.snapshot_id}`,
    `- ResearchTurn: ${view.research_turn_id}`,
    `- ScientificResultSnapshot: ${view.scientific_result_snapshot_id}`,
    `- ScientificInterpretation: ${view.scientific_interpretation_id}`,
    `- Source fingerprint: ${view.source_fingerprint}`,
    "",
    "## 研究问题",
    report.research_question,
    "",
    "## 摘要",
    report.summary,
    "",
    "## 数据与方法",
    report.method_summary,
  ];
  if (view.viewer_sources?.length) {
    lines.push("", "### 精确来源");
    for (const source of view.viewer_sources) {
      lines.push(`- ${source.display_name} (${source.object_type}) · version ${source.version_id}${source.is_current_version ? " · 当前版本" : " · 历史版本"}`);
    }
  }
  if (report.main_findings.length) {
    lines.push("", "## 主要发现");
    report.main_findings.forEach((finding, index) => lines.push(`${index + 1}. ${finding.statement}`));
  }
  if (report.primary_figures.length) {
    lines.push("", "## 主要图表");
    report.primary_figures.forEach((figure) => lines.push(`- ${figure.caption} (${figure.figure_ref})`));
  }
  if (report.limitations.length) {
    lines.push("", "## 限制与适用范围");
    report.limitations.forEach((limitation) => lines.push(`- ${limitation.statement}`));
  }
  lines.push("", "## 复现信息", report.reproducibility_summary, "", `Evidence refs: ${report.evidence_refs.join(", ") || "none"}`);
  return `${lines.join("\n")}\n`;
}
