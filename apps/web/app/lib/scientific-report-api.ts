const API_BASE = (
  process.env.NEXT_PUBLIC_MDI_API_BASE_URL ||
  (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")
).replace(/\/$/, "");

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

export type ScientificReportNarrativeSection = {
  text: string;
  fact_refs: string[];
  evidence_refs: string[];
};

export type ScientificReportContent = {
  contract_version: "1.0" | "2.0";
  title: string;
  research_question: string;
  summary: string;
  discussion?: ScientificReportNarrativeSection | null;
  conclusion?: ScientificReportNarrativeSection | null;
  next_steps?: ScientificReportNarrativeSection | null;
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
  research_session_id?: string | null;
  research_turn_id: string;
  scientific_result_snapshot_id: string;
  scientific_interpretation_id: string;
  title: string;
  source_title?: string | null;
  pinned?: boolean;
  revision_group_id?: string;
  parent_report_id?: string | null;
  parent_snapshot_id?: string | null;
  revision_number?: number;
  revision_reason?: "ORIGINAL" | "USER_REVISION" | "DUPLICATE";
  relevance_at_generation:
    | "CURRENT"
    | "STALE"
    | "SOURCE_MISSING"
    | "INVALIDATED";
  current_effective_relevance:
    | "CURRENT"
    | "STALE"
    | "SOURCE_MISSING"
    | "INVALIDATED";
  grounding_status: "VALID";
  lifecycle_status?: "ACTIVE" | "ARCHIVED" | "TRASHED";
  scientific_context: string;
  finding_count: number;
  figure_count: number;
  source_fingerprint: string;
  created_at: string;
  viewer_sources?: Array<{
    source_ref: string;
    object_id: string;
    version_id: string;
    object_type: string;
    display_name: string;
    is_current_version: boolean;
    lifecycle_status?: "ACTIVE" | "ARCHIVED" | "TRASHED" | "INVALIDATED";
  }>;
  figure_sources?: Array<{
    figure_ref: string;
    artifact_ids: string[];
    job_id?: string | null;
    object_id?: string;
    version_id?: string;
    object_type?: string;
  }>;
  table_sources?: Array<{
    table_ref: string;
    title?: string;
    artifact_ids: string[];
    job_id?: string | null;
    source_refs?: Array<{
      object_id: string;
      version_id: string;
      object_type: string;
    }>;
  }>;
  report?: ScientificReportContent;
};

export type ScientificReportTurnStatus = {
  research_turn_id: string;
  status:
    | "NOT_REQUESTED"
    | "REQUESTED"
    | "COMPOSING"
    | "READY"
    | "FAILED";
  report_id: string | null;
  generation_id: string | null;
  attempt_count: number;
  error_code: string | null;
  updated_at: string | null;
};

export type ScientificReportDependencyImpact = {
  entity: "scientific_report";
  entityId: string;
  displayName: string;
  lifecycleStatus: "ACTIVE" | "ARCHIVED" | "TRASHED";
  dependencyCount: number;
  dependencies: Array<{ kind: string; id: string; label: string }>;
  canDelete: boolean;
  impact: {
    removedFromActiveDiscovery: boolean;
    historicalProvenanceProtected: boolean;
    historicalResearchRemainsAccessible: boolean;
    scientificSnapshotMutated: boolean;
  };
};

export type ScientificReportRevisionList = {
  revision_group_id: string;
  current_report_id: string;
  items: ScientificReportView[];
  count: number;
};

export type ScientificReportRevisionComparison = {
  revision_group_id: string;
  base_report_id: string;
  report_id: string;
  base_revision_number: number;
  revision_number: number;
  scientific_authority_unchanged: boolean;
  source_versions_unchanged: boolean;
  changed_sections: string[];
  added_findings: string[];
  removed_findings: string[];
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...(init?.headers || {}),
    },
    credentials: "include",
  });
  if (!response.ok) {
    const error = new Error(
      `Scientific report request failed (${response.status})`,
    ) as Error & { status?: number };
    error.status = response.status;
    throw error;
  }
  return (await response.json()) as T;
}

export const listScientificReports = (projectId: string) =>
  request<{ items: ScientificReportView[]; count: number }>(
    `/api/projects/${encodeURIComponent(projectId)}/scientific-reports`,
  );
export const getScientificReport = (reportId: string) =>
  request<ScientificReportView>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}`,
  );
export const getScientificReportForTurn = (turnId: string) =>
  request<ScientificReportView>(
    `/api/research/turns/${encodeURIComponent(turnId)}/report`,
  );
export const getScientificReportStatusForTurn = (turnId: string) =>
  request<ScientificReportTurnStatus>(
    `/api/research/turns/${encodeURIComponent(turnId)}/report-status`,
  );
export const requestScientificReport = (turnId: string) =>
  request<{ generation_id: string; status: string }>(
    `/api/research/turns/${encodeURIComponent(turnId)}/report`,
    { method: "POST" },
  );
export const updateScientificReportLifecycle = (
  reportId: string,
  lifecycle: "ACTIVE" | "ARCHIVED" | "TRASHED",
) =>
  request<ScientificReportView>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}/lifecycle`,
    { method: "PATCH", body: JSON.stringify({ lifecycle }) },
  );

export const bulkUpdateScientificReportLifecycle = (
  projectId: string,
  reportIds: string[],
  lifecycle: "ACTIVE" | "ARCHIVED",
) =>
  request<{
    lifecycle: "ACTIVE" | "ARCHIVED";
    reportIds: string[];
    count: number;
    items: ScientificReportView[];
  }>(
    `/api/projects/${encodeURIComponent(projectId)}/scientific-reports/bulk`,
    {
      method: "POST",
      body: JSON.stringify({ reportIds, lifecycle }),
    },
  );

export const updateScientificReportOrganization = (
  reportId: string,
  changes: { title?: string | null; pinned?: boolean },
) =>
  request<ScientificReportView>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}/organization`,
    { method: "PATCH", body: JSON.stringify(changes) },
  );

export const getScientificReportDependencyImpact = (reportId: string) =>
  request<ScientificReportDependencyImpact>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}/dependency-impact`,
  );

export const createScientificReportRevision = (
  reportId: string,
  changes: {
    reason?: "USER_REVISION" | "DUPLICATE";
    title?: string | null;
  } = {},
) =>
  request<ScientificReportView>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}/revisions`,
    {
      method: "POST",
      body: JSON.stringify({
        reason: changes.reason || "USER_REVISION",
        ...(changes.title ? { title: changes.title } : {}),
      }),
    },
  );

export const listScientificReportRevisions = (reportId: string) =>
  request<ScientificReportRevisionList>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}/revisions`,
  );

export const compareScientificReportRevisions = (
  reportId: string,
  baseReportId?: string,
) =>
  request<ScientificReportRevisionComparison>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}/compare${
      baseReportId
        ? `?base_report_id=${encodeURIComponent(baseReportId)}`
        : ""
    }`,
  );

const SCIENTIFIC_METHOD_LABELS: Readonly<Record<string, string>> = {
  "structure.rdf": "晶体结构径向分布函数分析",
  "structure.coordination_hist": "配位数分布分析",
  "structure.coordination_crystalnn": "CrystalNN 局域配位分析",
  "structure.coordination_voronoinn": "VoronoiNN 局域配位分析",
  "diffraction.theoretical_xrd": "理论 XRD 分析",
  "diffraction.experimental_theoretical_comparison": "实验与理论 XRD 对比",
  "trajectory.rdf": "轨迹径向分布函数分析",
  "trajectory.msd": "均方位移分析",
  "trajectory.diffusion": "扩散性质估算",
  "phonon.band": "声子能带分析",
  "phonon.dos": "声子态密度分析",
  "phonon.band_dos": "声子能带与态密度联合分析",
  "electronic.band_structure": "电子能带分析",
  "electronic.dos": "电子态密度分析",
  "data.composition_space": "材料组成空间分析",
  "data.materials_explorer": "材料数据集探索",
  "ml.regression_evaluation": "回归模型评估",
};

/** Replace implementation-facing capability identifiers in reader/export prose. */
export function humanizeScientificMethodSummary(summary: string): string {
  return Object.entries(SCIENTIFIC_METHOD_LABELS).reduce(
    (current, [capabilityId, label]) => {
      const escaped = capabilityId.replaceAll(".", "\\.");
      return current
        .replace(
          new RegExp(`使用[^，。；]{0,40}?工具[（(]capability:\\s*${escaped}\\s*,\\s*version\\s*([\\w.-]+)[）)]`, "giu"),
          `使用${label}（版本 $1）`,
        )
        .replace(
          new RegExp(`使用\\s*${escaped}\\s*工具[（(]版本\\s*([\\w.-]+)[）)]`, "giu"),
          `使用${label}（版本 $1）`,
        )
        .replace(
          new RegExp(`capability:\\s*${escaped}\\s*,\\s*version\\s*([\\w.-]+)`, "giu"),
          `${label}（版本 $1）`,
        )
        .replace(
          new RegExp(`${escaped}\\s*工具[（(]版本\\s*([\\w.-]+)[）)]`, "giu"),
          `${label}（版本 $1）`,
        )
        .replace(new RegExp(escaped, "gu"), label);
    },
    summary,
  );
}

/** Build a bounded, deterministic Markdown export from an authorized report snapshot. */
export function buildScientificReportMarkdown(
  view: ScientificReportView,
): string {
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
    humanizeScientificMethodSummary(report.method_summary),
  ];
  if (view.viewer_sources?.length) {
    lines.push("", "### 精确来源");
    for (const source of view.viewer_sources) {
      const lifecycle =
        source.lifecycle_status === "ARCHIVED"
          ? " · 来源对象已归档"
          : source.lifecycle_status === "TRASHED"
            ? " · 来源对象位于回收站"
            : source.lifecycle_status === "INVALIDATED"
              ? " · 来源对象已失效"
              : "";
      lines.push(
        `- ${source.display_name} (${source.object_type}) · version ${source.version_id}${source.is_current_version ? " · 当前版本" : " · 历史版本"}${lifecycle}`,
      );
    }
  }
  if (report.main_findings.length) {
    lines.push("", "## 主要发现");
    report.main_findings.forEach((finding, index) =>
      lines.push(`${index + 1}. ${finding.statement}`),
    );
  }
  if (report.discussion?.text) {
    lines.push("", "## 科学讨论", report.discussion.text);
  }
  if (report.primary_figures.length) {
    lines.push("", "## 主要图表");
    report.primary_figures.forEach((figure) => {
      const source = view.figure_sources?.find(
        (candidate) => candidate.figure_ref === figure.figure_ref,
      );
      const artifactRefs = source?.artifact_ids?.length
        ? ` · Artifacts: ${source.artifact_ids.join(", ")}`
        : "";
      const exactSource = source?.object_id && source.version_id
        ? ` · exact source ${source.object_id} / version ${source.version_id}`
        : "";
      lines.push(`- ${figure.caption} (${figure.figure_ref})${artifactRefs}${exactSource}`);
    });
  }
  if (report.limitations.length) {
    lines.push("", "## 限制与适用范围");
    report.limitations.forEach((limitation) =>
      lines.push(`- ${limitation.statement}`),
    );
  }
  if (report.conclusion?.text) {
    lines.push("", "## 结论", report.conclusion.text);
  }
  if (report.next_steps?.text) {
    lines.push("", "## 后续工作建议", report.next_steps.text);
  }
  lines.push(
    "",
    "## 复现信息",
    report.reproducibility_summary,
    "",
    `Evidence refs: ${report.evidence_refs.join(", ") || "none"}`,
  );
  return `${lines.join("\n")}\n`;
}

/**
 * Build a bounded, non-executable reproducibility manifest from an authorized
 * immutable report view. The manifest carries identities and checksums only;
 * it never contains provider credentials, prompts, raw tool logs, or code.
 */
export function buildScientificReportReproducibilityManifest(
  view: ScientificReportView,
): string {
  const report = view.report;
  const manifest = {
    schema_version: "mdi.reproducibility-manifest/1.0",
    report: {
      report_id: view.report_id,
      snapshot_id: view.snapshot_id,
      project_id: view.project_id,
      research_turn_id: view.research_turn_id,
      scientific_result_snapshot_id: view.scientific_result_snapshot_id,
      scientific_interpretation_id: view.scientific_interpretation_id,
      source_fingerprint: view.source_fingerprint,
      grounding_status: view.grounding_status,
      lifecycle_status: view.lifecycle_status || "ACTIVE",
      created_at: view.created_at,
    },
    scientific_sources: (view.viewer_sources || []).map((source) => ({
      source_ref: source.source_ref,
      object_id: source.object_id,
      version_id: source.version_id,
      object_type: source.object_type,
      display_name: source.display_name,
      is_current_version: source.is_current_version,
      lifecycle_status: source.lifecycle_status,
    })),
    figures: (view.figure_sources || []).map((figure) => ({
      figure_ref: figure.figure_ref,
      artifact_ids: [...figure.artifact_ids],
      job_id: figure.job_id || null,
      object_id: figure.object_id || null,
      version_id: figure.version_id || null,
      object_type: figure.object_type || null,
    })),
    evidence_refs: report?.evidence_refs || [],
    data_sources: report?.data_sources || [],
    limitations: (report?.limitations || []).map((item) => item.statement),
    content_contract: report?.contract_version || null,
    omitted_supporting_items: report?.omitted_supporting_items || [],
  };
  return `${JSON.stringify(manifest, null, 2)}\n`;
}
