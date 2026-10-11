import { presentationLimitationText } from "./scientific-limitation-text";
import { scientificNarrativeText } from "./scientific-narrative-text";
import { tableFactLabels, tableMetricTitle } from "./scientific-table-labels";
export { presentationLimitationText } from "./scientific-limitation-text";
import type { Artifact, GroundedScientificInterpretation, ScientificEvidenceItem } from "./planner-api";
import type { ScientificReportView } from "./scientific-report-api";
import { projectScientificArtifacts } from "./scientific-result-projection";

export type PresentationSource = {
  resultId?: string | null;
  interpretationId?: string | null;
  factId?: string | null;
  evidenceId?: string | null;
  artifactId?: string | null;
  jobId?: string | null;
  toolCallId?: string | null;
  objectId?: string | null;
  versionId?: string | null;
  versionNo?: number | null;
};

export type AuthoritativePresentationFact = {
  factId: string;
  predicate: string;
  subjectRef: string;
  value: unknown;
  unit?: string | null;
  source?: {
    artifactId?: string | null;
    toolCallId?: string | null;
    scientificObjectRef?: { objectId: string; versionId: string } | null;
  };
};

export type PersistedScientificFinding = {
  finding_id: string;
  statement: string;
  importance: "HIGH" | "MEDIUM" | "LOW";
  confidence: "HIGH" | "MEDIUM" | "LIMITED";
  fact_refs: string[];
  evidence_refs: string[];
  result_item_refs: string[];
};

export type PersistedScientificInterpretation = {
  contract_version: "1.0";
  title: string;
  answer_lead: string;
  primary_findings: PersistedScientificFinding[];
  supporting_findings: PersistedScientificFinding[];
  limitations: string[];
  primary_result_refs: string[];
  supporting_result_refs: string[];
  follow_up_suggestions: string[];
};

export type ScientificPresentationBlock =
  | { id: string; type: "narrative"; title?: string; text: string; source: PresentationSource }
  | { id: string; type: "finding"; title: string; text: string; confidence: "DIRECT" | "QUALIFIED" | "LIMITED"; source: PresentationSource; evidenceIds: string[]; factIds?: string[] }
  | { id: string; type: "metric"; title: string; value: string; unit?: string | null; source: PresentationSource }
  | { id: string; type: "table" | "figure"; title: string; artifactId: string; source: PresentationSource }
  | { id: string; type: "viewer_reference"; title: string; label: string; source: PresentationSource }
  | { id: string; type: "evidence_reference"; title: string; label: string; source: PresentationSource }
  | { id: string; type: "limitation" | "warning"; text: string; source: PresentationSource };

export type ScientificPresentation = {
  schemaVersion: "1.0";
  blocks: ScientificPresentationBlock[];
  exactSourceRefs: Array<{ objectId: string; versionId: string; versionNo?: number | null; objectType?: string; displayName?: string }>;
  historicalNotice?: string;
};

export type PresentationInput = {
  interpretation?: GroundedScientificInterpretation | null;
  /**
   * The current Agent2 interpreter persists this bounded scientific
   * communication contract. It is distinct from the legacy planner
   * GroundedScientificInterpretation contract and must not be cast into it.
   */
  persistedInterpretation?: PersistedScientificInterpretation | null;
  /**
   * The persisted interpretation envelope owns this identity. Keep it
   * separate from the nested grounded payload because the latter is
   * intentionally scientific content only.
   */
  interpretationId?: string | null;
  evidence?: ScientificEvidenceItem[];
  artifacts?: Artifact[];
  facts?: AuthoritativePresentationFact[];
  validatedNarrative?: string | null;
  resultId?: string | null;
  sourceObjectRefs?: Array<{ objectId: string; versionId: string; versionNo?: number | null; objectType?: string; displayName?: string }>;
  artifactSourceRefs?: Record<string, Array<{ objectId: string; versionId: string; versionNo?: number | null; objectType?: string; displayName?: string }>>;
  scientificSelections?: Array<{
    selectionType: string;
    semanticLocator: Record<string, string | number | boolean>;
  }>;
  relevance?: "CURRENT" | "STALE" | "SOURCE_MISSING" | "INVALIDATED";
};

function stableId(prefix: string, value: string, index = 0): string {
  const normalized = value.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 72);
  return `${prefix}-${normalized || index}`;
}

function artifactId(artifact: Artifact): string {
  return artifact.artifactId || artifact.id || "";
}

function exactSource(sourceObjectRefs: PresentationInput["sourceObjectRefs"]): PresentationSource {
  const source = sourceObjectRefs?.[0];
  return source ? { objectId: source.objectId, versionId: source.versionId, versionNo: source.versionNo } : {};
}

function evidenceSource(item: ScientificEvidenceItem, resultId: string | null | undefined, interpretationId: string | null | undefined, sourceObjectRefs: PresentationInput["sourceObjectRefs"]): PresentationSource {
  return { ...exactSource(sourceObjectRefs), resultId, interpretationId, evidenceId: item.evidenceItemId, artifactId: item.sourceArtifactId, toolCallId: item.sourceToolId };
}

function displayFactValue(value: unknown): string | null {
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
  return null;
}

const NUMERIC_PRESENTATION_VALUE = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/iu;

/**
 * Keep the persisted value untouched in the presentation contract while
 * providing a bounded, readable scientific display value. The exact source
 * value remains available to the renderer and evidence inspector.
 */
export function formatPresentationMetricValue(value: string): string {
  const normalized = value.trim();
  if (!NUMERIC_PRESENTATION_VALUE.test(normalized)) return value;
  const numeric = Number(normalized);
  if (!Number.isFinite(numeric)) return value;
  if (Object.is(numeric, -0) || numeric === 0) return "0";
  const magnitude = Math.abs(numeric);
  if (magnitude >= 1_000_000 || magnitude < 0.0001) {
    return numeric.toExponential(4).replace(/\.?0+e/iu, "e");
  }
  return numeric.toLocaleString("zh-CN", {
    maximumSignificantDigits: 7,
    useGrouping: magnitude >= 10_000,
  });
}

/**
 * Format numeric tokens in a persisted scientific narrative for display only.
 * The persisted message/result remains untouched; authoritative exact values
 * continue to be available from the Result and evidence inspector.
 */
export function formatScientificNarrativeNumbers(text: string): string {
  return text.replace(
    /(^|[^A-Za-z0-9_.-])([-+]?(?:\d+(?:\.\d+)?e[-+]?\d+|\d+\.\d+))(?![A-Za-z0-9_-]|\.\d)/giu,
    (match, prefix: string, token: string, offset: number) => /(?:版本|version)\s*[:：]?\s*v?$/iu.test(text.slice(0, offset + prefix.length))
      ? match : `${prefix}${formatPresentationMetricValue(token)}`,
  );
}

function persistedFindingConfidence(
  confidence: PersistedScientificFinding["confidence"],
): Extract<ScientificPresentationBlock, { type: "finding" }>["confidence"] {
  if (confidence === "HIGH") return "DIRECT";
  if (confidence === "MEDIUM") return "QUALIFIED";
  return "LIMITED";
}

const PRESENTATION_METRIC_LABELS: Readonly<Record<string, string>> = {
  "structure.coordination_successful_sites": "成功分析位点数",
  "structure.coordination.method": "近邻判定方法",
  "structure.coordination.coverage.totalSites": "结构位点数",
  "structure.coordination.coverage.successfulSites": "成功分析位点数",
  "structure.coordination.coverage.requestedSites": "请求位点数",
  "structure.coordination.coverage.evaluatedSites": "已评估位点数",
  "structure.coordination.coverage.unavailableSites": "不可用位点数",
  "structure.coordination.coverage.classifiedSites": "已分类位点数",
  "structure.coordination.coverage.ambiguousSites": "分类不唯一位点数",
  "structure.coordination.coverage.unclassifiedSites": "未归类位点数",
  "structure.coordination.site_index": "中心位点编号",
  "structure.coordination.species": "位点元素",
  "structure.coordination.semantics": "配位权重定义",
  "structure.coordination.weighted_value": "配位权重和",
  "structure.coordination.neighbor_count": "近邻数量",
  "structure.coordination.neighbor_site": "近邻精确标识",
  "structure.coordination.neighbor_site_index": "近邻位点编号",
  "structure.coordination.neighbor_distance": "近邻距离",
  "structure.coordination.periodic_image_x": "周期偏移 x",
  "structure.coordination.periodic_image_y": "周期偏移 y",
  "structure.coordination.periodic_image_z": "周期偏移 z",
  "structure.local_environment.status": "几何分类状态",
  "structure.local_environment.reference_geometry": "参考几何",
  "structure.local_environment.geometry_score": "几何匹配分数",
  "structure.local_environment.geometry_distance_rms": "几何距离 RMS",
  "structure.local_environment.face_status": "表面生成状态",
  "structure.local_environment.mean_neighbor_distance": "平均近邻距离",
  "structure.local_environment.neighbor_distance_spread": "近邻距离标准差",
  "structure.local_environment.radial_distortion_index": "径向畸变指数",
  "structure.local_environment.angular_rms_deviation": "角度均方根偏差",
  "structure.local_environment.volume": "多面体体积",
  "structure.local_environment.surface_area": "多面体表面积",
  "structure.local_environment.relative_x": "相对坐标 x",
  "structure.local_environment.relative_y": "相对坐标 y",
  "structure.local_environment.relative_z": "相对坐标 z",
  "xrd.peak_count": "保留衍射峰数",
  "xrd.peak_count_before_limit": "截断前衍射峰数",
  "xrd.wavelength": "X 射线波长",
  "xrd.two_theta_min": "2θ 扫描起点",
  "xrd.two_theta_max": "2θ 扫描终点",
  "xrd.intensity_scale": "强度归一化方式",
  "xrd.peak.two_theta": "衍射峰 2θ",
  "xrd.peak.intensity": "衍射峰相对强度",
  "xrd.peak.d_spacing": "晶面间距",
  "xrd.peak.structure": "衍射峰来源结构",
  "structure.reduced_formula": "简约化学式",
  "structure.site_count": "晶胞位点数",
  "structure.lattice_a": "晶格长度 a",
  "structure.lattice_b": "晶格长度 b",
  "structure.lattice_c": "晶格长度 c",
  "structure.lattice_alpha": "晶格角 α",
  "structure.lattice_beta": "晶格角 β",
  "structure.lattice_gamma": "晶格角 γ",
  "structure.lattice_volume": "晶胞体积",
  "structure.spacegroup_number": "空间群编号",
  "structure.spacegroup_symbol": "空间群符号",
  "structure.crystal_system": "晶系",
  "structure.selected_site_index": "所选位点索引",
  "structure.selected_element": "所选元素",
  "structure.selected_coordinate_basis": "所选坐标基准",
  "structure.selected_base_cartesian_x": "原晶胞坐标 x",
  "structure.selected_base_cartesian_y": "原晶胞坐标 y",
  "structure.selected_base_cartesian_z": "原晶胞坐标 z",
  "structure.selected_base_fractional_x": "原晶胞分数坐标 x",
  "structure.selected_base_fractional_y": "原晶胞分数坐标 y",
  "structure.selected_base_fractional_z": "原晶胞分数坐标 z",
  "volumetric.length_unit": "坐标长度单位",
  "volumetric.coordinate_space": "坐标空间",
  "volumetric.sample_location": "网格采样位置",
  "volumetric.endpoint_policy": "端点规则",
  "volumetric.grid_size_a": "a 方向网格点数",
  "volumetric.grid_size_b": "b 方向网格点数",
  "volumetric.grid_size_c": "c 方向网格点数",
  "volumetric.boundary_a": "a 方向边界",
  "volumetric.boundary_b": "b 方向边界",
  "volumetric.boundary_c": "c 方向边界",
  "volumetric.selected_field_name": "所选数据场",
  "volumetric.selected_component": "所选分量",
  "volumetric.selected_quantity": "所选物理量",
  "volumetric.selected_canonical_unit": "所选数值单位",
  "volumetric.selected_minimum": "所选通道最小值",
  "volumetric.selected_maximum": "所选通道最大值",
  "volumetric.field_name": "数据场名称",
  "volumetric.quantity": "物理量定义",
  "volumetric.value_kind": "数值类型",
  "volumetric.canonical_unit": "数值单位",
  "volumetric.minimum": "源数值最小值",
  "volumetric.integral": "整胞积分",
  "volumetric.mean": "源数值均值",
  "volumetric.volume_integral": "源体积分",
  "volumetric.potential_reference": "势能参考零点",
  "volumetric.potential_shift": "已保存的势能平移量",
  "volumetric.integral_semantics": "积分物理含义",
  "volumetric.normalization_semantics": "归一化方式",
  "volumetric.source_unit": "记录的源单位",
  "volumetric.unit_conversion_applied": "已应用单位转换",
  "volumetric.unit_conversion_factor": "单位转换系数",
  "volumetric.statistics_authority": "统计数值来源",
  "volumetric.maximum": "源数值最大值",
  "phonon.atom_count": "原子数",
  "trajectory.frame_count": "分析帧数",
  "trajectory.source_frame_count": "源轨迹帧数",
  "trajectory.analysis_frame_count": "所选帧数",
  "trajectory.analysis_first_frame": "所选起始帧",
  "trajectory.analysis_last_frame": "所选结束帧",
  "trajectory.analysis_start_time": "分析起始时间",
  "trajectory.analysis_end_time": "分析结束时间",
  "trajectory.msd_atom_count": "MSD 原子数",
  "trajectory.msd_species": "MSD 元素",
  "trajectory.msd_lag_count": "MSD 滞后时间点数",
  "trajectory.msd_first_lag_time": "首个滞后时间",
  "trajectory.msd_last_lag_time": "末个滞后时间",
  "trajectory.msd_first_total": "首个滞后点总 MSD",
  "trajectory.msd_last_total": "末个滞后点总 MSD",
  "trajectory.msd_first_origin_count": "首个滞后点时间原点数",
  "trajectory.msd_last_origin_count": "末个滞后点时间原点数",
  "trajectory.msd_first_x": "首个滞后点 x 方向 MSD",
  "trajectory.msd_first_y": "首个滞后点 y 方向 MSD",
  "trajectory.msd_first_z": "首个滞后点 z 方向 MSD",
  "trajectory.msd_last_x": "末个滞后点 x 方向 MSD",
  "trajectory.msd_last_y": "末个滞后点 y 方向 MSD",
  "trajectory.msd_last_z": "末个滞后点 z 方向 MSD",
  "trajectory.diffusion_coefficient": "所选窗口扩散系数",
  "trajectory.diffusion_fit_start_time": "拟合窗口起点",
  "trajectory.diffusion_fit_end_time": "拟合窗口终点",
  "trajectory.diffusion_fit_point_count": "拟合点数",
  "trajectory.diffusion_fit_duration": "拟合窗口时长",
  "trajectory.diffusion_fit_r2": "拟合决定系数 R²",
  "trajectory.diffusion_fit_rmse": "拟合均方根误差",
  "trajectory.diffusion_regime": "扩散诊断",
  "trajectory.diffusion_minimum_duration": "最短拟合时长要求",
  "trajectory.diffusion_minimum_points": "最少拟合点数要求",
  "trajectory.diffusion_origin_coverage": "时间原点覆盖率",
  "trajectory.diffusion_minimum_origin_coverage": "最低时间原点覆盖率",
  "trajectory.diffusion_minimum_r2": "最低决定系数要求",
  "trajectory.diffusion_alpha": "扩散指数 α",
  "trajectory.diffusion_alpha_min": "扩散指数下限",
  "trajectory.diffusion_alpha_max": "扩散指数上限",
  "phonon.frequency_unit": "频率单位",
  "phonon.selected_qpoint_index": "所选 q 点索引",
  "phonon.selected_branch_index": "所选分支索引",
  "phonon.selected_frequency": "所选模式频率",
  "phonon.selected_qpoint_label": "所选 q 点标签",
  "phonon.branch_count": "声子分支数",
  "phonon.qpoint_count": "q 点数",
  "phonon.frequency_min": "采样最低频率",
  "phonon.frequency_max": "采样最高频率",
  "phonon.imaginary_mode_count": "采样虚频模式数",
  "electronic.band_gap": "电子带隙（供应数据）",
  "electronic.kpoint_count": "k 点数",
  "electronic.energy_point_count": "DOS 能量点数",
  "electronic.energy_reference": "能量参考",
  "electronic.fermi_energy": "费米能量",
  "electronic.spin_mode": "自旋模式",
  "electronic.selected_spin_channel": "所选自旋通道",
  "electronic.selected_band_id": "所选能带",
  "electronic.selected_kpoint_id": "所选 k 点",
  "electronic.selected_kpoint_label": "所选 k 点标签",
  "electronic.selected_energy": "所选能量",
  "electronic.selected_dos_channel": "所选 DOS 通道",
  "electronic.selected_dos_value": "所选态密度",
  "electronic.dos_unit_semantic": "态密度单位定义",
  "electronic.projection_completeness": "投影覆盖情况",
  "ml.sample_count": "评估样本数",
  "ml.mae": "平均绝对误差（MAE）",
  "ml.rmse": "均方根误差（RMSE）",
  "ml.r2": "决定系数（R²）",
  "ml.r2_status": "R² 适用性",
  "ml.mean_signed_error": "平均符号误差",
  "ml.median_absolute_error": "中位绝对误差",
  "ml.high_error_sample_id": "最大误差样本",
  "ml.high_error_formula": "最大误差样本化学式",
  "ml.high_error_target": "最大误差样本真实值",
  "ml.high_error_prediction": "最大误差样本预测值",
  "ml.high_error_residual": "最大误差样本残差",
  "ml.high_error_absolute_error": "最大绝对误差",
  "rdf.structure_count": "结构数",
  "rdf.bin_count": "径向区间数",
  "rdf.r_max": "最大半径",
  "rdf.bin_width": "径向步长",
  "rdf.number_density": "数密度",
  "reference.element_count": "所选元素数", "reference.value_count": "有效参考值数",
  "reference.version": "参考资料版本", "reference.property_definition": "性质定义",
  "reference.element.symbol": "元素", "reference.element.atomic_number": "原子序数", "reference.element.covalent_radius": "参考共价半径",
  "calculation.input_value": "原数值", "calculation.output_value": "换算结果", "calculation.quantity": "物理量",
  "calculation.conversion_factor": "换算系数", "calculation.conversion_offset": "换算偏移",
  "calculation.point_count": "采样点数", "calculation.x_min": "区间起点", "calculation.x_max": "区间终点",
  "calculation.function": "函数", "calculation.sampled_min": "采样最小值", "calculation.sampled_max": "采样最大值",
  "calculation.start_value": "起点函数值", "calculation.end_value": "终点函数值",
  "calculation.parameter.coefficients": "多项式系数", "calculation.parameter.amplitude": "幅值",
  "calculation.parameter.offset": "纵向偏移", "calculation.parameter.rate": "自变量系数",
  "calculation.parameter.phase": "自变量偏移", "calculation.parameter.center": "中心", "calculation.parameter.sigma": "标准差参数",
  "composition.formula": "输入化学式", "composition.total_stoichiometry": "总化学计量数",
  "composition.element": "元素", "composition.stoichiometry": "化学计量数",
  "composition.atomic_fraction": "原子分数", "composition.atomic_percent": "原子百分比",
  "inline.row_count": "数据行数", "inline.column_count": "数据列数", "inline.column": "列名",
  "inline.minimum": "最小值", "inline.maximum": "最大值", "inline.mean": "均值", "inline.first": "首行数值", "inline.last": "末行数值",
  "model.prototype": "晶格原型", "model.formula": "理想模型化学式", "model.site_count": "位点数",
  "model.lattice_a": "单胞 a", "model.lattice_c": "单胞 c", "model.cell_volume": "展示晶胞体积", "model.nearest_distance": "最短周期近邻距离",
  "model.repeat_a": "沿 a 重复数", "model.repeat_b": "沿 b 重复数", "model.repeat_c": "沿 c 重复数",
};

export function presentationMetricTitle(predicate: string): string {
  const millerComponent = predicate.match(/^xrd\.peak\.hkl_([0-3])\.component_([0-3])$/u);
  if (millerComponent) return `晶面族 ${Number(millerComponent[1]) + 1} · 分量 ${Number(millerComponent[2]) + 1}`;
  return PRESENTATION_METRIC_LABELS[predicate] || tableMetricTitle(predicate) || predicate.replaceAll("_", " ");
}

export function presentationMetricUnit(unit: string): string {
  return ({ count: "", fraction: "", picosecond: "ps", femtosecond: "fs", angstrom: "Å", "angstrom^-3": "Å⁻³", "angstrom^2": "Å²", "angstrom^3": "Å³", "angstrom^2/picosecond": "Å²/ps", degC: "°C", um: "µm", us: "µs" } as Record<string, string>)[unit] ?? unit;
}

export function presentationScientificText(text: string): string {
  const normalized = scientificNarrativeText(presentationLimitationText(text))
    .replace(
      /该事实来自证据\s*(?:\b(?:fact|evidence|limitation|figure)\.[a-z0-9.]+\b)(?:\s*（step_[^)]+）)?/giu,
      "该数值已绑定本次分析证据",
    )
    .replace(
      /(?:来自|来源于)\s*(?:证据\s*)?(?:\b(?:fact|evidence|limitation|figure)\.[a-z0-9.]+\b)(?:\s*（step_[^)]+）)?/giu,
      "已绑定本次分析证据",
    )
    .replace(/\b(?:fact|evidence|limitation|figure)\.[a-z0-9.]+/giu, "")
    .replace(/（step_[^)]+）/giu, "")
    .replace(/（\s*）/gu, "")
    .replace(/该事实来自证据\s*(?:（[^）]*）)?。/gu, "该数值已绑定本次分析证据。")
    .replace(/由证据\s*支持/gu, "由已提交证据支持")
    .replace(/但\s*明确说明：/gu, "同时，权威限制说明：")
    .replace(/[ \t]{2,}/gu, " ")
    .replace(/\s+([，。；：！？])/gu, "$1")
    .trim();
  const sentences = normalized.match(/[^。！？!?]*[。！？!?]|[^。！？!?]+$/gu);
  if (!sentences) return normalized;
  return formatScientificNarrativeNumbers(sentences
    .map((sentence) => sentence.trim())
    .filter((sentence, index, items) => index === 0 || sentence !== items[index - 1])
    .join("")
    .trim());
}

function presentationSummary(
  persistedInterpretation: PersistedScientificInterpretation | null | undefined,
  fallback: string | null | undefined,
): string {
  const primary = (persistedInterpretation?.primary_findings || [])
    .map((finding) => presentationScientificText(finding.statement))
    .map((statement) => statement.match(/^[^。！？!?]*[。！？!?]/u)?.[0]?.trim() || statement)
    .filter(Boolean)
    .slice(0, 2);
  return primary.length
    ? primary.join("")
    : fallback
      ? presentationScientificText(fallback)
      : "";
}

function selectedDatasetSampleRefs(selections: PresentationInput["scientificSelections"]): string[] {
  const refs = selections
    ?.filter((selection) => selection.selectionType === "DATASET_SAMPLE")
    .flatMap((selection) => {
      const locator = selection.semanticLocator || {};
      return [locator.sample_ref, locator.sample_id]
        .filter((value): value is string => typeof value === "string" && value.trim().length > 0);
    }) || [];
  return [...new Set(refs)];
}

function selectedFactsFirst(facts: AuthoritativePresentationFact[], selections: PresentationInput["scientificSelections"]): AuthoritativePresentationFact[] {
  const sampleRefs = selectedDatasetSampleRefs(selections);
  if (sampleRefs.length === 0) return facts;
  const matchesSelectedSample = (fact: AuthoritativePresentationFact) =>
    sampleRefs.some((sampleRef) => fact.subjectRef === sampleRef || fact.subjectRef.endsWith(`:${sampleRef}`));
  return [...facts.filter(matchesSelectedSample), ...facts.filter((fact) => !matchesSelectedSample(fact))];
}

function factSource(fact: AuthoritativePresentationFact, resultId: string | null | undefined, sourceObjectRefs: PresentationInput["sourceObjectRefs"]): PresentationSource {
  const exact = fact.source?.scientificObjectRef;
  return {
    ...(exact ? { objectId: exact.objectId, versionId: exact.versionId } : exactSource(sourceObjectRefs)),
    resultId,
    factId: fact.factId,
    artifactId: fact.source?.artifactId,
    toolCallId: fact.source?.toolCallId,
  };
}

function projectedArtifactBlocks(
  artifacts: Artifact[],
  resultId: string | null | undefined,
  sourceObjectRefs: PresentationInput["sourceObjectRefs"],
  artifactSourceRefs: PresentationInput["artifactSourceRefs"],
): ScientificPresentationBlock[] {
  return projectScientificArtifacts(artifacts).slice(0, 12).map((artifact, index) => {
    const id = artifactId(artifact);
    const itemSources = artifactSourceRefs?.[id] || [];
    const title = sourceLabelledTitle(artifact.resultTitle, itemSources, sourceObjectRefs);
    const exactArtifactSource =
      itemSources.length === 1
        ? exactSource(itemSources)
        : sourceObjectRefs?.length === 1
          ? exactSource(sourceObjectRefs)
          : {};
    const source = { ...exactArtifactSource, resultId, artifactId: id, jobId: artifact.jobId };
    const isTable = artifact.resultRole.endsWith("TABLE");
    const block: ScientificPresentationBlock = { id: `${isTable ? "table" : "figure"}-${id || index}`, type: isTable ? "table" : "figure", title, artifactId: id, source };
    return block;
  });
}

function sourceLabelledTitle(title: string, itemSources: PresentationInput["sourceObjectRefs"], allSources: PresentationInput["sourceObjectRefs"]): string {
  if ((allSources?.length || 0) <= 1 || itemSources?.length !== 1) return title;
  const item = itemSources[0];
  const index = allSources?.findIndex((source) => source.objectId === item.objectId && source.versionId === item.versionId) ?? -1;
  const label = item.displayName?.trim() || (index >= 0 ? `来源 ${index + 1}` : "");
  return label ? `${label} · ${title}` : title;
}

/**
 * Compile only bounded, persisted scientific semantics. This function has no
 * execution hooks, HTML fields, component names, or latest-version lookup.
 */
export function compileScientificPresentation(input: PresentationInput): ScientificPresentation {
  const interpretation = input.interpretation;
  const persistedInterpretation = input.persistedInterpretation;
  const interpretationId = input.interpretationId || interpretation?.interpretationId;
  const evidence = input.evidence || [];
  const artifacts = input.artifacts || [];
  const blocks: ScientificPresentationBlock[] = [];
  const source = exactSource(input.sourceObjectRefs);

  const persistedFindings = [
    ...(persistedInterpretation?.primary_findings || []).map((finding) => ({ finding, primary: true })),
    ...(persistedInterpretation?.supporting_findings || []).map((finding) => ({ finding, primary: false })),
  ].filter(({ finding }) => finding.statement.trim());
  if (persistedFindings.length) {
    persistedFindings.slice(0, 12).forEach(({ finding, primary }, index) => {
      blocks.push({
        id: stableId("finding", finding.finding_id || finding.statement, index),
        type: "finding",
        title: primary ? "主要发现" : "支持发现",
        text: presentationScientificText(finding.statement),
        confidence: persistedFindingConfidence(finding.confidence),
        source: {
          ...source,
          resultId: input.resultId,
          interpretationId,
          factId: finding.fact_refs[0] || null,
          evidenceId: finding.evidence_refs[0] || null,
        },
        factIds: [...new Set(finding.fact_refs)].slice(0, 12),
        evidenceIds: [...new Set(finding.evidence_refs)].slice(0, 12),
      });
    });
  } else {
    const groundedClaims = (interpretation?.claims || []).filter((claim) => claim.groundingStatus === "GROUNDED" && claim.renderedText.trim());
    groundedClaims.slice(0, 8).forEach((claim, index) => {
      blocks.push({
        id: stableId("finding", claim.claimId || claim.renderedText, index),
        type: "finding",
        title: claim.claimType === "LIMITATION" ? "限制" : claim.claimType === "COMPARISON" ? "比较发现" : "科学发现",
        text: claim.renderedText,
        confidence: claim.confidenceClass,
        source: { ...source, resultId: input.resultId, interpretationId, evidenceId: claim.supportingEvidenceIds[0] || claim.subjectEvidenceIds[0] || null },
        evidenceIds: [...new Set([...claim.subjectEvidenceIds, ...claim.supportingEvidenceIds])].slice(0, 12),
      });
    });
  }

  const groundedClaims = (interpretation?.claims || []).filter((claim) => claim.groundingStatus === "GROUNDED" && claim.renderedText.trim());
  const narrativeSource = persistedInterpretation?.answer_lead?.trim() || groundedClaims[0]?.renderedText || input.validatedNarrative?.trim();
  const narrative = presentationSummary(persistedInterpretation, narrativeSource);
  if (narrative) blocks.unshift({ id: "narrative-grounded-summary", type: "narrative", title: "科学摘要", text: narrative, source: { ...source, resultId: input.resultId, interpretationId } });

  evidence.filter((item) => ["SCALAR", "COUNT", "RANGE", "CATEGORY", "BOOLEAN"].includes(item.evidenceKind)).forEach((item, index) => {
    blocks.push({
      id: stableId("metric", item.semanticRole || item.evidenceItemId, index),
      type: "metric",
      title: item.semanticRole.replaceAll("_", " "),
      value: item.displayValue,
      unit: item.unit,
      source: evidenceSource(item, input.resultId, interpretationId, input.sourceObjectRefs),
    });
  });

  const tableLabels = tableFactLabels(input.facts || []);
  selectedFactsFirst(input.facts || [], input.scientificSelections).forEach((fact, index) => {
    const value = displayFactValue(fact.value);
    if (value === null) return;
    blocks.push({
      id: stableId("fact-metric", fact.factId || fact.predicate, index),
      type: "metric",
      title: sourceLabelledTitle(tableLabels.get(fact.factId) || presentationMetricTitle(fact.predicate), input.artifactSourceRefs?.[fact.source?.artifactId || ""], input.sourceObjectRefs),
      value,
      unit: fact.unit,
      source: factSource(fact, input.resultId, input.artifactSourceRefs?.[fact.source?.artifactId || ""] || input.sourceObjectRefs),
    });
  });

  blocks.push(
    ...projectedArtifactBlocks(
      artifacts,
      input.resultId,
      input.sourceObjectRefs,
      input.artifactSourceRefs,
    ),
  );

  evidence.slice(0, 8).forEach((item, index) => {
    blocks.push({
      id: stableId("evidence", item.evidenceItemId, index),
      type: "evidence_reference",
      title: "证据",
      label: item.displayValue,
      source: evidenceSource(item, input.resultId, interpretationId, input.sourceObjectRefs),
    });
  });

  const presentationLimitations = persistedInterpretation?.limitations || interpretation?.globalLimitations || [];
  presentationLimitations.filter(Boolean).slice(0, 8).forEach((text, index) => {
    blocks.push({ id: stableId("limitation", text, index), type: "limitation", text, source: { ...source, resultId: input.resultId, interpretationId } });
  });
  (interpretation?.globalWarnings || []).filter(Boolean).slice(0, 6).forEach((text, index) => {
    blocks.push({ id: stableId("warning", text, index), type: "warning", text, source: { ...source, resultId: input.resultId, interpretationId } });
  });

  const viewerSources = [...new Map(
    (input.sourceObjectRefs || []).map((item) => [
      `${item.objectId}:${item.versionId}`,
      item,
    ]),
  ).values()].slice(0, 8);
  viewerSources.forEach((viewerSource, index) => {
    blocks.push({
      id: stableId(
        "viewer-exact-source",
        `${viewerSource.objectId}-${viewerSource.versionId}`,
        index,
      ),
      type: "viewer_reference",
      title: "精确科学视图",
      label: viewerSource.displayName
        || `${viewerSource.objectType || "ScientificObject"} · ${viewerSource.versionNo ? `版本 ${viewerSource.versionNo}` : "精确版本"}`,
      source: {
        objectId: viewerSource.objectId,
        versionId: viewerSource.versionId,
        versionNo: viewerSource.versionNo,
        resultId: input.resultId,
      },
    });
  });

  return {
    schemaVersion: "1.0",
    blocks,
    exactSourceRefs: input.sourceObjectRefs || [],
    historicalNotice: input.relevance && input.relevance !== "CURRENT"
      ? input.relevance === "STALE"
        ? "本次呈现基于历史 source version；新版本存在时不会替换本记录。"
        : "本次呈现保留历史来源，但当前来源状态需要进一步检查。"
      : undefined,
  };
}

/**
 * Reports are immutable communication snapshots. Compile their bounded,
 * already-authoritative fields into the same presentation contract used by
 * Research so a report cannot silently acquire a second fact authority.
 */
export function compileReportPresentation(view: ScientificReportView): ScientificPresentation {
  const report = view.report;
  const interpretationId = view.scientific_interpretation_id || null;
  const sourceRefs = (view.viewer_sources || []).map((source) => ({
    objectId: source.object_id,
    versionId: source.version_id,
    objectType: source.object_type,
    displayName: source.display_name,
  }));
  const source = exactSource(sourceRefs);
  const blocks: ScientificPresentationBlock[] = [];
  if (report?.summary) {
    blocks.push({
      id: "report-summary",
      type: "narrative",
      title: "报告摘要",
      text: presentationScientificText(report.summary),
      source: { ...source, resultId: view.scientific_result_snapshot_id, interpretationId },
    });
  }
  for (const section of [
    ["科学讨论", report?.discussion],
    ["结论", report?.conclusion],
    ["后续工作建议", report?.next_steps],
  ] as const) {
    const [title, value] = section;
    if (!value?.text) continue;
    blocks.push({
      id: stableId("report-narrative", title, blocks.length),
      type: "narrative",
      title,
      text: presentationScientificText(value.text),
      source: { ...source, resultId: view.scientific_result_snapshot_id, interpretationId, factId: value.fact_refs[0] || null, evidenceId: value.evidence_refs[0] || null },
    });
  }
  (report?.main_findings || []).slice(0, 12).forEach((finding, index) => {
    blocks.push({
      id: stableId("report-finding", finding.statement, index),
      type: "finding",
      title: "报告发现",
      text: presentationScientificText(finding.statement),
      confidence: "QUALIFIED",
      source: {
        ...source,
        resultId: view.scientific_result_snapshot_id,
        interpretationId,
        factId: finding.fact_refs[0] || null,
      },
      factIds: [...new Set(finding.fact_refs)].slice(0, 12),
      evidenceIds: [...new Set(finding.evidence_refs)].slice(0, 12),
    });
  });
  (report?.primary_figures || []).slice(0, 12).forEach((figure, index) => {
    const figureSource = (view.figure_sources || []).find((candidate) => candidate.figure_ref === figure.figure_ref);
    const artifactId = figureSource?.artifact_ids?.[0] || figure.figure_ref;
    const figureExactSource = figureSource?.object_id && figureSource.version_id
      ? {
          objectId: figureSource.object_id,
          versionId: figureSource.version_id,
        }
      : source;
    blocks.push({
      id: stableId("report-figure", figure.figure_ref || figure.caption, index),
      type: "figure",
      title: figure.caption || figure.figure_ref,
      artifactId,
      source: {
        ...figureExactSource,
        resultId: view.scientific_result_snapshot_id,
        interpretationId,
        artifactId,
        jobId: figureSource?.job_id || null,
      },
    });
  });
  (report?.evidence_refs || []).slice(0, 12).forEach((evidenceId, index) => {
    blocks.push({
      id: stableId("report-evidence", evidenceId, index),
      type: "evidence_reference",
      title: "报告证据",
      label: evidenceId,
      source: { ...source, resultId: view.scientific_result_snapshot_id, interpretationId, evidenceId },
    });
  });
  (report?.limitations || []).slice(0, 8).forEach((limitation, index) => {
    blocks.push({
      id: stableId("report-limitation", limitation.statement, index),
      type: "limitation",
      text: limitation.statement,
      source: { ...source, resultId: view.scientific_result_snapshot_id, interpretationId },
    });
  });
  sourceRefs.slice(0, 8).forEach((sourceRef, index) => {
    blocks.push({
      id: stableId("report-viewer", sourceRef.versionId, index),
      type: "viewer_reference",
      title: "历史 Viewer",
      label: sourceRef.displayName || `${sourceRef.objectType || "ScientificObject"} · 精确版本`,
      source: { objectId: sourceRef.objectId, versionId: sourceRef.versionId, resultId: view.scientific_result_snapshot_id, interpretationId },
    });
  });
  return {
    schemaVersion: "1.0",
    blocks,
    exactSourceRefs: sourceRefs,
    historicalNotice: view.current_effective_relevance !== "CURRENT"
      ? "本报告保留生成时的精确来源；新版本不会静默替换历史报告。"
      : undefined,
  };
}

export function presentationBlockLabel(block: ScientificPresentationBlock): string {
  if (block.type === "metric") return `${block.value}${block.unit ? ` ${block.unit}` : ""}`;
  if (block.type === "evidence_reference" || block.type === "viewer_reference") return block.label;
  if (block.type === "figure" || block.type === "table") return block.title;
  if (block.type === "finding" || block.type === "narrative" || block.type === "limitation" || block.type === "warning") return block.text;
  return "";
}

const PRESENTATION_BLOCK_TYPES = new Set([
  "narrative",
  "finding",
  "metric",
  "table",
  "figure",
  "viewer_reference",
  "evidence_reference",
  "limitation",
  "warning",
]);

const PRESENTATION_SOURCE_KEYS = new Set([
  "resultId",
  "interpretationId",
  "factId",
  "evidenceId",
  "artifactId",
  "jobId",
  "toolCallId",
  "objectId",
  "versionId",
  "versionNo",
]);

const PRESENTATION_BLOCK_KEYS: Readonly<Record<string, ReadonlySet<string>>> = {
  narrative: new Set(["id", "type", "title", "text", "source"]),
  finding: new Set(["id", "type", "title", "text", "confidence", "source", "evidenceIds", "factIds"]),
  metric: new Set(["id", "type", "title", "value", "unit", "source"]),
  table: new Set(["id", "type", "title", "artifactId", "source"]),
  figure: new Set(["id", "type", "title", "artifactId", "source"]),
  viewer_reference: new Set(["id", "type", "title", "label", "source"]),
  evidence_reference: new Set(["id", "type", "title", "label", "source"]),
  limitation: new Set(["id", "type", "text", "source"]),
  warning: new Set(["id", "type", "text", "source"]),
};

const EXECUTABLE_PRESENTATION_TEXT = /[<>]|javascript:|vbscript:|data:text\/html/iu;
const REMOTE_OR_EXECUTABLE_REFERENCE = /[<>]|(?:javascript|vbscript|data:text\/html):|https?:\/\/|^\/\//iu;

function isPlainRecord(value: unknown): value is Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function hasOnlyKeys(value: Record<string, unknown>, allowed: ReadonlySet<string>): boolean {
  return Object.keys(value).every((key) => allowed.has(key));
}

function isSafeDisplayText(value: unknown, optional = false): value is string | undefined {
  if (optional && value === undefined) return true;
  return typeof value === "string"
    && value.length <= 16_000
    && !EXECUTABLE_PRESENTATION_TEXT.test(value);
}

function isSafeReference(value: unknown, optional = false): value is string | null | undefined {
  if (optional && (value === undefined || value === null)) return true;
  return typeof value === "string"
    && value.length > 0
    && value.length <= 256
    && !REMOTE_OR_EXECUTABLE_REFERENCE.test(value);
}

function isSafePresentationSource(value: unknown): value is PresentationSource {
  if (!isPlainRecord(value) || !hasOnlyKeys(value, PRESENTATION_SOURCE_KEYS)) return false;
  return Object.entries(value).every(([key, item]) =>
    key === "versionNo"
      ? item === undefined
        || item === null
        || (Number.isSafeInteger(item) && Number(item) > 0)
      : isSafeReference(item, true),
  );
}

export function isSafePresentationBlock(block: unknown): block is ScientificPresentationBlock {
  if (!isPlainRecord(block)) return false;
  const candidate = block as Record<string, unknown>;
  if (typeof candidate.type !== "string" || !PRESENTATION_BLOCK_TYPES.has(candidate.type)) return false;
  const allowedKeys = PRESENTATION_BLOCK_KEYS[candidate.type];
  if (!allowedKeys || !hasOnlyKeys(candidate, allowedKeys)) return false;
  if (!isSafeReference(candidate.id) || !isSafePresentationSource(candidate.source)) return false;

  if (candidate.type === "narrative") {
    return isSafeDisplayText(candidate.title, true) && isSafeDisplayText(candidate.text);
  }
  if (candidate.type === "finding") {
    return isSafeDisplayText(candidate.title)
      && isSafeDisplayText(candidate.text)
      && ["DIRECT", "QUALIFIED", "LIMITED"].includes(String(candidate.confidence))
      && Array.isArray(candidate.evidenceIds)
      && candidate.evidenceIds.length <= 12
      && candidate.evidenceIds.every((item) => isSafeReference(item))
      && (candidate.factIds === undefined || (Array.isArray(candidate.factIds)
        && candidate.factIds.length <= 12 && candidate.factIds.every((item) => isSafeReference(item))));
  }
  if (candidate.type === "metric") {
    return isSafeDisplayText(candidate.title)
      && isSafeDisplayText(candidate.value)
      && (candidate.unit === null || isSafeDisplayText(candidate.unit, true));
  }
  if (candidate.type === "table" || candidate.type === "figure") {
    return isSafeDisplayText(candidate.title) && isSafeReference(candidate.artifactId);
  }
  if (candidate.type === "viewer_reference" || candidate.type === "evidence_reference") {
    return isSafeDisplayText(candidate.title) && isSafeDisplayText(candidate.label);
  }
  return isSafeDisplayText(candidate.text);
}
