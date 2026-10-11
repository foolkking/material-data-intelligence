import { reportLimitationPresentation } from "./scientific-limitation-text";
import { scientificNarrativeText } from "./scientific-narrative-text";
import { reportFindingPresentation } from "./scientific-report-findings";
import { renderReportTableMarkdown } from "./scientific-report-table-export";
import { boundReportBasis, renderReportBasisMarkdown, renderReportInputsMarkdown, reportParameterInputs } from "./scientific-report-basis";
import { readPlatformReferences, referenceSourcesMarkdown, type PlatformReference } from "./platform-reference";

export type ReportViewerArtifact = {
  id: string;
  jobId: string;
  toolCallId: string;
  type: string;
  name: string;
  sha256: string;
  sizeBytes: number;
  contentType: string;
};

const API_BASE = (
  process.env.NEXT_PUBLIC_MDI_API_BASE_URL ||
  (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")
).replace(/\/$/, "");

export type ScientificReportFinding = {
  statement: string;
  finding_refs: string[];
  fact_refs: string[];
  evidence_refs: string[];
  reasoning_assessment?: { accepted: boolean; scope: string; limitations: string[] } | null;
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

export type ScientificReportBasisSource = {
  object_id: string;
  version_id: string;
  object_type: string;
  display_name?: string | null;
};

export type ScientificReportBasisLocation = {
  source_refs: ScientificReportBasisSource[];
  reference_source_ids?: string[];
  input_origin?: "USER_PARAMETERS" | "USER_TEXT_DATA" | "IDEAL_MODEL";
  input_hash?: string;
  artifact_id?: string | null;
  artifact_locator?: string | null;
  artifact_name?: string | null;
  job_id?: string | null;
  tool_call_id?: string | null;
  tool_id?: string | null;
};

export type ScientificReportBasisFact = ScientificReportBasisLocation & {
  fact_id: string;
  predicate: string;
  subject_ref: string;
  value_text: string;
  unit?: string | null;
  uncertainty_text?: string | null;
};

export type ScientificReportBasisEvidence = ScientificReportBasisLocation & {
  evidence_id: string;
  evidence_type: string;
};

export type ScientificReportBasis = {
  project_id: string;
  result_snapshot_id: string;
  facts: ScientificReportBasisFact[];
  evidence: ScientificReportBasisEvidence[];
  reference_sources?: PlatformReference[];
  input_origin?: string;
  parameter_inputs?: unknown;
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
  scientific_basis?: ScientificReportBasis;
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
    renderer?: "volumetric";
    artifacts?: ReportViewerArtifact[];
  }>;
  file_sources?: Array<{ artifact_id: string; job_id?: string | null; title: string }>;
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
  dependencies: Array<{ kind: string; id: string; label: string; href?: string }>;
  canDelete: boolean;
  retentionPolicy?: {
    schemaVersion: string;
    automaticPurge: "ENABLED" | "DISABLED";
    referencedProvenance: string;
    unreferencedTrash: string;
    manualPurge: "SERVER_ZERO_DEPENDENCY_ONLY" | "NOT_SUPPORTED_FOR_ENTITY";
    manualPurgeRequiresZeroDependencies: boolean;
  };
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

export const listScientificReports = (projectId: string, signal?: AbortSignal) =>
  request<{ items: ScientificReportView[]; count: number }>(
    `/api/projects/${encodeURIComponent(projectId)}/scientific-reports`,
    { signal, cache: "no-store" },
  );
export const getScientificReport = (reportId: string, signal?: AbortSignal) =>
  request<ScientificReportView>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}`,
    { signal },
  );
export const getScientificReportForTurn = (turnId: string) =>
  request<ScientificReportView>(
    `/api/research/turns/${encodeURIComponent(turnId)}/report`,
  );
export const getScientificReportStatusForTurn = (turnId: string, signal?: AbortSignal) =>
  request<ScientificReportTurnStatus>(
    `/api/research/turns/${encodeURIComponent(turnId)}/report-status`,
    { signal },
  );
export const requestScientificReport = (turnId: string, signal?: AbortSignal) =>
  request<{ generation_id: string; status: string }>(
    `/api/research/turns/${encodeURIComponent(turnId)}/report`,
    { method: "POST", signal },
  );
export const updateScientificReportLifecycle = (
  reportId: string,
  lifecycle: "ACTIVE" | "ARCHIVED" | "TRASHED",
  signal?: AbortSignal,
) =>
  request<ScientificReportView>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}/lifecycle`,
    { method: "PATCH", body: JSON.stringify({ lifecycle }), signal },
  );

export const bulkUpdateScientificReportLifecycle = (
  projectId: string,
  reportIds: string[],
  lifecycle: "ACTIVE" | "ARCHIVED",
  signal?: AbortSignal,
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
      signal,
    },
  );

export const updateScientificReportOrganization = (
  reportId: string,
  changes: { title?: string | null; pinned?: boolean },
  signal?: AbortSignal,
) =>
  request<ScientificReportView>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}/organization`,
    { method: "PATCH", body: JSON.stringify(changes), signal },
  );

export const getScientificReportDependencyImpact = (reportId: string, signal?: AbortSignal) =>
  request<ScientificReportDependencyImpact>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}/dependency-impact`,
    { signal },
  );

export const createScientificReportRevision = (
  reportId: string,
  changes: {
    reason?: "USER_REVISION" | "DUPLICATE";
    title?: string | null;
  } = {},
  signal?: AbortSignal,
) =>
  request<ScientificReportView>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}/revisions`,
    {
      method: "POST",
      signal,
      body: JSON.stringify({
        reason: changes.reason || "USER_REVISION",
        ...(changes.title ? { title: changes.title } : {}),
      }),
    },
  );

export const listScientificReportRevisions = (reportId: string, signal?: AbortSignal) =>
  request<ScientificReportRevisionList>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}/revisions`,
    { signal },
  );

export const compareScientificReportRevisions = (
  reportId: string,
  baseReportId?: string,
  signal?: AbortSignal,
) =>
  request<ScientificReportRevisionComparison>(
    `/api/scientific-reports/${encodeURIComponent(reportId)}/compare${
      baseReportId
        ? `?base_report_id=${encodeURIComponent(baseReportId)}`
        : ""
    }`,
    { signal },
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
    scientificNarrativeText(summary),
  );
}

/** Keep the reader and exports consistent without changing saved numeric precision. */
export function dedupeReportSentences(value: string): string {
  const sentences = value.match(/[^。！？!?]*[。！？!?]|[^。！？!?]+$/gu) || [];
  const seen = new Set<string>();
  return sentences.map(sentence => sentence.trim()).filter(sentence => {
    const key = sentence.toLocaleLowerCase();
    if (!sentence || seen.has(key)) return false;
    seen.add(key);
    return true;
  }).join("").trim();
}

export type ScientificReportExportAssets = {
  figures: Array<{ figureRef: string; images: string[]; embeddedImages?: string[]; originals: string[]; dataFiles?: string[]; note?: string }>;
  artifacts?: Array<{ jobId: string; artifactId: string; path: string }>;
  tables?: import("./scientific-report-table-export").ReportTableExport[];
};

/** Build a bounded, deterministic Markdown export from an authorized report snapshot. */
export function buildScientificReportMarkdown(
  view: ScientificReportView,
  assets?: ScientificReportExportAssets,
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
    "## 摘要",
    scientificNarrativeText(report.summary),
    "",
    "## 研究问题",
    report.research_question,
    "",
    "## 数据与方法",
    dedupeReportSentences(humanizeScientificMethodSummary(report.method_summary)),
  ];
  const references = (item: { fact_refs?: string[]; evidence_refs?: string[]; finding_refs?: string[] }, indent = "") => {
    const content = renderReportBasisMarkdown(view, item, assets?.artifacts);
    if (content) lines.push("", ...content.split("\n").map(line => line ? indent + line : ""));
  };
  const artifactLink = (jobId: string | null | undefined, artifactId: string, label: string) => {
    const matches = assets?.artifacts?.filter(item => item.jobId === jobId && item.artifactId === artifactId) || [];
    if (matches.length === 1) lines.push(`  - [${label}](${matches[0].path})`);
  };
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
  const referenceSources = readPlatformReferences(boundReportBasis(view)?.reference_sources);
  if (referenceSources.length) lines.push("", "### 参考资料", "", ...referenceSourcesMarkdown(referenceSources));
  const inputs = renderReportInputsMarkdown(view);
  if (inputs) lines.push("", inputs);
  if (report.main_findings.length) {
    lines.push("", "## 主要发现");
    const presentation = reportFindingPresentation(report.main_findings);
    if (presentation.sharedLimitations.length) lines.push("", `共同限制：${scientificNarrativeText(presentation.sharedLimitations.join(""))}`, "");
    report.main_findings.forEach((finding, index) => {
      lines.push(`${index + 1}. ${scientificNarrativeText(presentation.statements[index])}`);
      references(finding, "   ");
    });
  }
  if (report.primary_figures.length) {
    lines.push("", "## 主要图表");
    report.primary_figures.forEach((figure) => {
      const matches = view.figure_sources?.filter(
        (candidate) => candidate.figure_ref === figure.figure_ref,
      ) || [];
      const source = matches.length === 1 ? matches[0] : undefined;
      const artifactRefs = source?.artifact_ids?.length
        ? ` · Artifacts: ${source.artifact_ids.join(", ")}`
        : "";
      const exactSource = source?.object_id && source.version_id
        ? ` · exact source ${source.object_id} / version ${source.version_id}`
        : "";
      lines.push(`- ${scientificNarrativeText(figure.caption)} (${figure.figure_ref})${artifactRefs}${exactSource}`);
      references(figure, "  ");
      if (!source) lines.push("  - 图表来源未唯一绑定，请在平台核对来源研究。");
      const locals = assets?.figures.filter(item => item.figureRef === figure.figure_ref) || [];
      const local = source && locals.length === 1 ? locals[0] : undefined;
      if (local) {
        for (const [index, path] of local.images.entries()) {
          lines.push("", `[![科学图表](${local.embeddedImages?.[index] || path})](${path})`, "");
        }
        for (const [index, path] of (local.dataFiles || []).entries()) lines.push(`[切片 ${index + 1} 原始数值](${path})`);
        for (const path of local.originals) lines.push(`[原始图表数据](${path})`);
        if (local.note) lines.push(local.note);
      }
    });
  }
  if (view.table_sources?.length) {
    lines.push("", "## 主要数据表");
    for (const table of view.table_sources) {
      lines.push(`- ${table.title || table.table_ref} (${table.table_ref})`);
      if (table.artifact_ids.length) lines.push(`  - Artifacts: ${table.artifact_ids.join(", ")}`);
      if (table.job_id) lines.push(`  - Job: ${table.job_id}`);
      for (const id of table.artifact_ids) {
        const preview = assets?.tables?.find(item => item.jobId === table.job_id && item.artifactId === id);
        if (preview) lines.push(renderReportTableMarkdown(preview.preview));
      }
      table.artifact_ids.forEach((id, index) => artifactLink(table.job_id, id, table.artifact_ids.length > 1 ? `原始数据表 ${index + 1}` : "原始数据表"));
      if (assets && !table.artifact_ids.length) lines.push("  - 此表未绑定可导出的数据文件。");
      for (const source of table.source_refs || []) {
        lines.push(`  - exact source ${source.object_id} / version ${source.version_id} (${source.object_type})`);
      }
    }
  }
  if (report.discussion?.text) {
    lines.push("", "## 科学讨论", scientificNarrativeText(report.discussion.text));
    references(report.discussion);
  }
  if (report.limitations.length) {
    lines.push("", "## 限制与适用范围");
    reportLimitationPresentation(report.limitations).forEach((limitation) =>
      lines.push(`- ${limitation.statement}`),
    );
  }
  if (report.conclusion?.text) {
    lines.push("", "## 结论", scientificNarrativeText(report.conclusion.text));
    references(report.conclusion);
  }
  if (report.next_steps?.text) {
    lines.push("", "## 后续工作建议", scientificNarrativeText(report.next_steps.text));
    references(report.next_steps);
  }
  if (report.supporting_results.length) {
    lines.push("", "## 支持结果");
    for (const item of report.supporting_results) lines.push(`- ${scientificNarrativeText(item.description)} (${item.result_item_ref})`);
  }
  if (view.file_sources?.length) {
    lines.push("", "## 结果文件");
    view.file_sources.forEach((file) => {
      lines.push(`- ${file.title} · Artifact: ${file.artifact_id} · Job: ${file.job_id || "未提供"}`);
      artifactLink(file.job_id, file.artifact_id, "原始结果文件");
    });
  }
  lines.push(
    "",
    "## 复现信息",
    scientificNarrativeText(report.reproducibility_summary),
    "",
    `Evidence refs: ${report.evidence_refs.join(", ") || "none"}`,
  );
  return `${lines.join("\n")}\n`;
}

/**
 * Build a bounded, non-executable reproducibility manifest from an authorized
 * immutable report view. The manifest carries identities, checksums and bound scientific inputs;
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
      ...(figure.renderer === "volumetric" ? { renderer: figure.renderer, artifacts: figure.artifacts || [] } : {}),
    })),
    tables: (view.table_sources || []).map((table) => ({
      table_ref: table.table_ref,
      artifact_ids: [...table.artifact_ids],
      job_id: table.job_id || null,
      source_refs: (table.source_refs || []).map((source) => ({
        object_id: source.object_id,
        version_id: source.version_id,
        object_type: source.object_type,
      })),
    })),
    result_files: (view.file_sources || []).map((file) => ({ artifact_id: file.artifact_id, job_id: file.job_id || null })),
    evidence_refs: report?.evidence_refs || [],
    data_sources: report?.data_sources || [],
    ...(boundReportBasis(view)?.reference_sources?.length ? { reference_sources: readPlatformReferences(boundReportBasis(view)?.reference_sources) } : {}),
    ...(reportParameterInputs(view).length ? { parameter_inputs: reportParameterInputs(view) } : {}),
    limitations: (report?.limitations || []).map((item) => item.statement),
    content_contract: report?.contract_version || null,
    omitted_supporting_items: report?.omitted_supporting_items || [],
  };
  return `${JSON.stringify(manifest, null, 2)}\n`;
}
