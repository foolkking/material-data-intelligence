import type { Artifact, GroundedScientificInterpretation } from "./planner-api";

export type ScientificResultRole =
  | "PRIMARY_FIGURE"
  | "SUPPORTING_FIGURE"
  | "PRIMARY_TABLE"
  | "SUPPORTING_TABLE"
  | "TECHNICAL";

export type ProjectedScientificArtifact = Artifact & {
  resultRole: ScientificResultRole;
  resultTitle: string;
};

const TYPE_LABELS: Record<string, string> = {
  table_json: "数据表",
  metrics_json: "计算指标",
  plotly_json: "科学图表",
  structure_json: "晶体结构",
  trajectory_json: "原子轨迹",
  xrd_json: "XRD 图谱",
  electronic_band_json: "电子能带",
  electronic_dos_json: "电子态密度",
  phonon_band_json: "声子色散",
  phonon_dos_json: "声子态密度",
  volumetric_payload_json: "体数据",
  summary_md: "科学摘要",
  recipe_json: "复现信息",
};

const TECHNICAL_TYPES = new Set(["recipe_json", "summary_md", "manifest_json", "metadata_json"]);
const TABLE_TYPES = new Set(["table_json", "table_csv", "peak_table_json", "regression_table_json", "metrics_json"]);
const SEMANTIC_NAMES: Record<string, string> = {
  experimental_xrd_comparison_plot: "实验与理论 XRD 对比图",
  experimental_xrd_comparison: "实验与理论 XRD 峰位比较",
  xrd_plot: "理论 XRD 图谱",
  xrd_pattern: "XRD 峰位数据",
  structure_composition: "结构组成概览",
  "structure.summary": "晶体结构摘要",
  correlation_heatmap: "材料属性相关性热图",
  correlation_matrix: "属性相关关系",
  formation_energy_band_gap: "形成能与带隙关系",
  formation_energy_density: "形成能与密度关系",
  band_gap_distribution: "材料带隙分布",
  composition_space_plot: "材料组成空间",
  composition_space: "材料组成空间",
  dataset_materials_explorer: "材料数据集概览",
  regression_evaluation: "材料属性回归评估",
  classification_evaluation: "材料分类评估",
  uncertainty_evaluation: "预测不确定性评估",
  trajectory_msd_plot: "均方位移（MSD）",
  trajectory_msd: "均方位移数据",
  trajectory_rdf_plot: "径向分布函数（RDF）",
  trajectory_rdf: "径向分布函数数据",
  trajectory_diffusion_plot: "扩散分析",
  trajectory_diffusion: "扩散分析数据",
  phonon_band: "声子色散",
  phonon_band_dos: "声子色散与态密度",
  phonon_band_dos_plot: "声子色散与态密度",
  phonon_dos: "声子态密度",
  brillouin_zone: "布里渊区",
  electronic_band_structure_plot: "电子能带",
  electronic_band_structure: "电子能带数据",
  electronic_dos_plot: "电子态密度",
  electronic_dos: "电子态密度数据",
  materials_ml_regression: "材料属性回归评估",
  materials_ml_classification: "材料分类评估",
  materials_ml_uncertainty: "预测不确定性评估",
  crystalnn_coordination: "CrystalNN 配位环境",
  voronoinn_coordination: "VoronoiNN 配位环境",
  local_environment_polyhedra: "局部配位多面体",
  rdf_plot: "径向分布函数（RDF）",
  rdf: "径向分布函数数据",
  volumetric_dataset: "体数据场",
  volumetric_payload_01: "体数据等值面",
  formula_statistics: "化学式统计",
  elements_hist: "元素分布",
  chem_sys_sunburst: "化学体系组成",
  numeric_summary: "材料属性统计摘要",
  histogram: "材料属性分布",
  scatter: "材料属性关系",
};

function normalizedType(artifact: Artifact): string {
  return String(artifact.type || "").toLowerCase();
}

function isFigureType(type: string): boolean {
  return ["plotly_json", "xrd_json", "structure_json", "trajectory_json", "electronic_band_json", "electronic_dos_json", "phonon_band_json", "phonon_band_dos_json", "phonon_dos_json", "brillouin_zone_json", "volumetric_payload_json", "volumetric_dataset_json"].includes(type);
}

function isTechnicalArtifact(artifact: Artifact): boolean {
  const type = normalizedType(artifact);
  const name = String(artifact.name || "").toLowerCase();
  return TECHNICAL_TYPES.has(type)
    || type === "plotly_html"
    || type === "preview_png"
    || type === "volumetric_binary"
    || /(?:^|_)(?:manifest|compatibility|parse_report|summary|recipe)(?:_|\.)/.test(name)
    || /(?:_manifest|_compatibility|_report|_summary)_json$/.test(type);
}

function displayPriority(artifact: Artifact): number {
  if (isPolyhedronArtifact(artifact)) return 1;
  const type = normalizedType(artifact);
  const name = String(artifact.name || "").toLowerCase();
  if (/(?:experimental_xrd_comparison_plot|composition_space_plot)/.test(name)) return 0;
  if (type === "phonon_band_dos_json") return 0;
  if (["volumetric_dataset_json", "electronic_band_json", "trajectory_json", "structure_json"].includes(type)) return 1;
  if (isFigureType(type)) return 2;
  if (TABLE_TYPES.has(type) || type.endsWith("_table_json")) return 3;
  return 4;
}

function isPolyhedronArtifact(artifact: Artifact): boolean {
  return normalizedType(artifact) === "table_json" && artifact.metadata?.toolId === "structure.local_environment_polyhedra";
}

function dedupeCompositeArtifacts(artifacts: Artifact[]): Artifact[] {
  const names = new Set(artifacts.map((artifact) => String(artifact.name || "").toLowerCase()));
  const hasPhononComposite = names.has("phonon_band_dos.json") || names.has("phonon_band_dos_plot.json");
  if (!hasPhononComposite) return artifacts;
  return artifacts.filter((artifact) => {
    const name = String(artifact.name || "").toLowerCase();
    // The combined panel already contains the band and DOS curves. Keep the
    // compatibility/table context, but do not present duplicate standalone
    // curves as separate supporting results.
    return !/^(?:phonon_band_plot|phonon_dos_plot|phonon_band_dos_plot|phonon_band_table|phonon_dos_table|phonon_band_dos_table)\.json$/.test(name);
  });
}

function semanticTitle(type: string, artifact: Artifact): string {
  const explicit = typeof artifact.metadata?.resultTitle === "string" ? artifact.metadata.resultTitle : null;
  if (explicit) return explicit;
  const toolId = typeof artifact.metadata?.toolId === "string" ? artifact.metadata.toolId.toLowerCase() : "";
  if (toolId === "reference.periodic_table") return type === "plotly_json" ? "元素周期表" : "元素参考值";
  if (toolId === "reference.compare_elements") return type === "plotly_json" ? "元素性质比较" : "元素参考值";
  if (toolId === "reference.convert_units") return "单位换算数值";
  if (toolId === "generation.function_curve") return type === "plotly_json" ? "函数曲线" : "函数采样数值";
  if (toolId === "composition.from_formula") return type === "plotly_json" ? "原子组成" : "化学式组成数值";
  if (toolId === "viz.inline_xy") return type === "plotly_json" ? "输入数据图" : "原始输入数值";
  if (toolId === "generation.ideal_crystal") return type === "structure_json" ? "理想晶格示意" : "理想晶格参数";
  if (toolId === "structure.structure_3d") return "晶体结构三维视图";
  if (isPolyhedronArtifact(artifact)) return "配位多面体";
  if (toolId === "ml.density_scatter" && type === "plotly_json") return "真实值与预测值";
  if (toolId === "ml.error_distribution") {
    if (type === "plotly_json") return "残差分布";
    if (type === "metrics_json") return "回归评估指标（残差分析）";
    if (TABLE_TYPES.has(type)) return "高误差样本（残差分析）";
  }
  if (toolId === "ml.outlier_table" && TABLE_TYPES.has(type)) return "高误差样本";
  if (type === "metrics_json") return toolId === "ml.basic_metrics" ? "回归评估指标" : "计算指标";
  const name = String(artifact.name || "").replace(/\.(json|csv|md|gz)$/i, "");
  if (SEMANTIC_NAMES[name]) return SEMANTIC_NAMES[name];
  const content = artifact.content && typeof artifact.content === "object" && !Array.isArray(artifact.content)
    ? artifact.content as Record<string, unknown>
    : null;
  const artifactType = typeof content?.artifactType === "string" ? content.artifactType : "";
  if (artifactType === "structure.composition_from_structure") return "结构组成概览";
  if (artifactType === "structure.summary") return "晶体结构摘要";
  if (name && !/^(artifact|output|result|figure|table)[_-]?\d*$/i.test(name)) return name;
  return TYPE_LABELS[type] || "科学结果";
}

export function projectScientificArtifacts(artifacts: Artifact[]): ProjectedScientificArtifact[] {
  const candidates = dedupeCompositeArtifacts(artifacts)
    .map((artifact, index) => ({ artifact, index }))
    .filter(({ artifact }) => {
      const type = normalizedType(artifact);
      // JSON and CSV from the same exact call are two encodings of one table.
      // Keep the downloadable CSV in provenance, not as a second view choice.
      const call = artifact.toolCallId;
      if (type === "table_csv" && call && artifacts.some((other) =>
        other.toolCallId === call && other.jobId === artifact.jobId
        && normalizedType(other) === "table_json")) return false;
      return !isTechnicalArtifact(artifact)
        && (isFigureType(type) || TABLE_TYPES.has(type) || type.endsWith("_table_json"));
    })
    .sort((left, right) => displayPriority(left.artifact) - displayPriority(right.artifact) || left.index - right.index)
    .map(({ artifact }) => artifact);
  let primaryAssigned = false;
  return candidates.map((artifact) => {
    const type = normalizedType(artifact);
    const table = !isPolyhedronArtifact(artifact) && (TABLE_TYPES.has(type) || type.endsWith("_table_json"));
    const figure = isFigureType(type) || isPolyhedronArtifact(artifact);
    const role: ScientificResultRole = table
      ? (primaryAssigned ? "SUPPORTING_TABLE" : "PRIMARY_TABLE")
      : figure
        ? (primaryAssigned ? "SUPPORTING_FIGURE" : "PRIMARY_FIGURE")
        : "TECHNICAL";
    if (role === "PRIMARY_TABLE" || role === "PRIMARY_FIGURE") primaryAssigned = true;
    return { ...artifact, resultRole: role, resultTitle: semanticTitle(type, artifact) };
  });
}

export function scientificResultTitle(question: string | null | undefined, artifacts: Artifact[], interpretation?: GroundedScientificInterpretation | null): string {
  const artifactNames = new Set(artifacts.map((artifact) => String(artifact.name || "").toLowerCase()));
  const hasElectronicBand = artifacts.some((artifact) => normalizedType(artifact) === "electronic_band_json")
    || ["electronic_band.json", "electronic_band_structure.json", "electronic_band_structure_plot.json"].some((name) => artifactNames.has(name));
  const hasElectronicDos = artifacts.some((artifact) => normalizedType(artifact) === "electronic_dos_json")
    || ["electronic_dos.json", "electronic_dos_plot.json"].some((name) => artifactNames.has(name));
  if (hasElectronicBand && hasElectronicDos) {
    return "电子能带与态密度";
  }
  const projectedTitle = projectScientificArtifacts(artifacts).find((artifact) => artifact.resultRole === "PRIMARY_FIGURE" || artifact.resultRole === "PRIMARY_TABLE")?.resultTitle;
  if (projectedTitle && isSpecificScientificTitle(projectedTitle)) return projectedTitle;
  const interpreted = interpretation?.claims.find((claim) => claim.claimType !== "LIMITATION")?.scope;
  const interpretedTitle = humanizeInterpretationScope(interpreted);
  if (interpretedTitle && interpretedTitle.length <= 120) return interpretedTitle;
  const trimmed = question?.trim();
  if (trimmed && !looksMachineFacing(trimmed)) return trimmed.length > 120 ? `${trimmed.slice(0, 117)}…` : trimmed;
  return projectedTitle || "科学结果";
}

function humanizeInterpretationScope(scope: string | null | undefined): string | null {
  if (!scope) return null;
  if (/^(?:dataset|table|structure|trajectory|artifact|result|project)$/i.test(scope.trim())) return null;
  const match = /^correlation:([^:]+):([^:]+)$/.exec(scope.trim());
  if (match) return `${match[1]} 与 ${match[2]} 的相关关系`;
  if (looksMachineFacing(scope)) return null;
  return scope;
}

function isSpecificScientificTitle(value: string): boolean {
  return /(?:XRD|轨迹|能带|态密度|声子|体数据|结构|相关|分布|回归|分类|不确定|组成空间|数据集概览|位移|扩散|RDF|配位|局部环境)/i.test(value)
    && !/^(?:科学图表|数据表|科学结果|晶体结构|原子轨迹|电子能带|电子态密度|声子色散|声子态密度|体数据)$/u.test(value);
}

function looksMachineFacing(value: string): boolean {
  return /(?:^|:)[a-f0-9]{24,}$/i.test(value) || /(?:artifact|toolcall|inputref|job|plan)[_-]?[a-f0-9]{12,}/i.test(value);
}
