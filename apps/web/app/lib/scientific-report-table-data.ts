import { savedXrdTableRows } from "./scientific-xrd-table";
import { savedRdfTableRows } from "./scientific-rdf-table";
import { presentationMetricUnit } from "./scientific-presentation";

type JsonRecord = Record<string, unknown>;

export function savedParameterTableRows(payload: unknown): JsonRecord[] | null {
  const record = asRecord(payload);
  if (record?.schemaVersion !== "mdi.project.parameter-table/1.0"
      || !["reference.convert_units", "generation.function_curve", "composition.from_formula", "viz.inline_xy", "generation.ideal_crystal"].includes(String(record.artifactType))
      || record.sampleAnalysis !== false) return null;
  const conversion = record.artifactType === "reference.convert_units";
  const columns = Array.isArray(record.columns) && record.columns.length <= 64
    && record.columns.every(column => typeof column === "string" && column.trim())
    && new Set(record.columns).size === record.columns.length
    ? record.columns : conversion ? ["原数值", "原单位", "换算结果", "目标单位"] : [];
  return records(record.rows).map(row => Object.fromEntries(
    [...new Set([...columns, ...Object.keys(row)])].filter(column => Object.hasOwn(row, column)).map(column => [
      column, conversion && ["原单位", "目标单位"].includes(column) && typeof row[column] === "string"
        ? presentationMetricUnit(row[column]) : row[column],
    ]),
  ));
}

export function regressionMetricRows(payload: unknown): [string, unknown][] | null {
  const record = asRecord(payload);
  const metrics = asRecord(record?.metrics);
  const fields = [["n", "样本数"], ["mae", "MAE"], ["rmse", "RMSE"], ["r2", "R²"],
    ["meanError", "平均误差"], ["maxAbsError", "最大绝对误差"]] as const;
  const undefinedR2 = metrics?.r2 === null && metrics?.r2Status === "undefined_constant_target";
  const hasStatus = metrics && Object.hasOwn(metrics, "r2Status");
  // The legacy adapter has no schema tag. Recognize its complete saved shape;
  // never reinterpret arbitrary metrics or compute missing values in the UI.
  if (!record || !metrics || Object.keys(record).length !== 3 || Object.keys(metrics).length !== fields.length + (hasStatus ? 1 : 0)
      || typeof record.targetColumn !== "string" || !record.targetColumn.trim()
      || typeof record.predictionColumn !== "string" || !record.predictionColumn.trim()
      || (hasStatus && !undefinedR2 && metrics.r2Status !== "defined")
      || !fields.every(([field]) => (field === "r2" && undefinedR2) || (typeof metrics[field] === "number" && Number.isFinite(metrics[field])))
      || !Number.isInteger(metrics.n) || Number(metrics.n) < 1) return null;
  return [
    ...fields.map(([field, label]): [string, unknown] => [label, field === "r2" && undefinedR2 ? "未定义（目标值为常量）" : metrics[field]]),
    ["目标值列", record.targetColumn], ["预测值列", record.predictionColumn],
  ];
}

export function tableRows(payload: unknown): JsonRecord[] {
    const record = asRecord(payload);
    if (!record) return [];
    const parameterRows = savedParameterTableRows(payload);
    if (parameterRows !== null) return parameterRows;
    const rdfRows = savedRdfTableRows(payload);
    if (rdfRows !== null) return rdfRows;
    const analysis = analysisRows(record);
    if (analysis !== null) return analysis;
  const xrdRows = savedXrdTableRows(payload);
  if (xrdRows) return xrdRows;
  if (record.schema_version === "phase10h1.phonon_band_table.v1") {
    return records(record.rows).map(row => ({
      qpoint_index: row.qpoint_index, branch_index: row.branch_index, frequency_terahertz: row.frequency_terahertz,
      label: row.label, classification: row.classification, path_distance: row.path_distance,
      segment_index: row.segment_index, q_x: row.q_x, q_y: row.q_y, q_z: row.q_z, ...row,
    }));
  }
  if (record.artifactType === "electronic.band_structure" && record.schemaVersion === "phase10n5.electronic_band_structure.v1") {
    const states = records(record.states), points = records(record.kpoints);
    const byId = new Map<unknown, JsonRecord | null>();
    for (const point of points) {
      if (typeof point.kpointId === "string") byId.set(point.kpointId, byId.has(point.kpointId) ? null : point);
    }
    return states.map(state => ({ spinChannel: spinLabel(state.spinChannel), bandId: state.bandId, kpointId: state.kpointId,
      energyEv: state.energyEv, fractionalCoordinates: byId.get(state.kpointId)?.fractionalCoordinates,
      stateId: state.stateId, bandIdentity: state.bandIdentity }));
  }
  if (record.artifactType === "electronic.dos" && record.schemaVersion === "phase10n5.electronic_dos.v1") {
    const energies = Array.isArray(record.energiesEv) ? record.energiesEv : [];
    const pointIds = Array.isArray(record.energyPointIds) ? record.energyPointIds : [];
    const unit = ({states_per_ev: "states/eV", states_per_ev_cell: "states/eV/cell", states_per_ev_formula_unit: "states/eV/f.u.", source_relative: "相对单位"} as Record<string, string>)[String(record.dosUnitSemantic)] || "单位未提供";
    const channels = [
      ...records(record.totalDos).map(channel => ({ channel, kind: "总态密度" })),
      ...records(record.projections).map(channel => ({ channel, kind: channel.projectionKind === "orbital" ? "轨道投影" : channel.projectionKind === "element" ? "元素投影" : channel.projectionKind })),
    ];
    return channels.flatMap(({channel, kind}) => {
      const values = Array.isArray(channel.values) ? channel.values : [];
      return Array.from({length: Math.max(energies.length, values.length)}, (_, index) => ({
        channelLabel: channel.label ?? channel.channelId, spinChannel: spinLabel(channel.spinChannel),
        energyEv: energies[index], [`态密度 (${unit})`]: values[index],
        projectionKind: kind, channelIdentity: channel.channelIdentity, energyPointId: pointIds[index],
      }));
    });
  }
  if (record.artifactType === "structure.summary" && record.schemaVersion === "phase10c1.structure_summary.v2" && Array.isArray(record.structures)) {
    const multipleStructures = record.structures.length > 1;
    return record.structures.flatMap((value) => {
      const structure = asRecord(value);
      if (!structure) return [];
      const lattice = asRecord(structure.lattice);
      const symmetry = asRecord(structure.symmetry);
      const properties: [string, unknown][] = [
        ["化学式", structure.formula], ["简化化学式", structure.reducedFormula],
        ["位点数", structure.numSites], ["元素种类数", structure.numElements],
        ["元素", structure.elements], ["元素数量", structure.elementCounts],
        ["周期结构", typeof structure.isPeriodic === "boolean" ? (structure.isPeriodic ? "是" : "否") : undefined],
        ["晶格 a (Å)", lattice?.a], ["晶格 b (Å)", lattice?.b], ["晶格 c (Å)", lattice?.c],
        ["晶格 α (°)", lattice?.alpha], ["晶格 β (°)", lattice?.beta], ["晶格 γ (°)", lattice?.gamma],
        ["晶胞体积 (Å³)", lattice?.volume], ["晶格矩阵 (Å)", lattice?.matrix],
        ["空间群", symmetry?.spacegroupSymbol], ["空间群编号", symmetry?.spacegroupNumber],
        ["晶系", symmetry?.crystalSystem], ["对称性容差 (Å)", symmetry?.symprecAngstrom],
        ["角度容差 (°)", symmetry?.angleToleranceDegrees],
      ];
      // Display saved fields only; absent values never become zero or inferred facts.
      return properties.filter(([, value]) => value !== undefined && value !== null)
        .map(([property, value]) => ({ ...(multipleStructures ? { structureId: structure.structureId } : {}), "属性": property, "值": value }));
    });
  }
  const nestedTable = asRecord(record.table);
  const direct = [record.rows, record.data, record.site_details, nestedTable?.rows, nestedTable?.data];
  for (const candidate of direct) {
    if (Array.isArray(candidate)) {
      const rows = candidate.map(asRecord).filter((item): item is JsonRecord => Boolean(item));
      if (rows.length) return rows;
    }
  }
  const histogram = asRecord(record.histogram)?.bins;
  if (Array.isArray(histogram)) return histogram.map(asRecord).filter((item): item is JsonRecord => Boolean(item));
  if (record.artifactType === "trajectory.msd") {
    return trajectoryMsdRows(record);
  }
  if (record.artifactType === "trajectory.diffusion") {
    return trajectoryDiffusionRows(record);
  }
  return [];
}

function analysisRows(record: JsonRecord): JsonRecord[] | null {
  if (record.chartType === "correlation_heatmap") {
    const columns = record.columns, matrix = record.matrix;
    if (!Array.isArray(columns) || columns.length < 2 || columns.length > 30
        || !columns.every(c => typeof c === "string" && c.trim()) || new Set(columns).size !== columns.length
        || !Array.isArray(matrix) || matrix.length !== columns.length
        || !matrix.every(row => Array.isArray(row) && row.length === columns.length
          && row.every(v => v === null || (typeof v === "number" && Number.isFinite(v) && v >= -1 && v <= 1)))) return [];
    return matrix.flatMap((row, i) => row.map((value: number | null, j: number) => ({
      "变量 A": columns[i], "变量 B": columns[j], "相关系数": value,
    })));
  }
  const numeric = asRecord(record.numericColumns), categorical = asRecord(record.categoricalColumns);
  if (!numeric || !categorical || !Number.isInteger(record.rowCount) || Number(record.rowCount) < 0) return null;
  const descriptors = new Map(records(record.columns).map(column => [column.name, column]));
  const statsFields = { count: "有效样本", missing: "缺失", unique: "唯一值数", uniqueCount: "唯一值数",
    mean: "平均值", std: "标准差", min: "最小值", p25: "25% 分位数", median: "中位数", p75: "75% 分位数", max: "最大值",
    missingRate: "缺失比例", topValues: "高频类别", valueCounts: "类别计数" };
  const rows: JsonRecord[] = [];
  for (const [family, kind] of [[numeric, "数值"], [categorical, "类别"]] as const) {
    for (const [name, raw] of Object.entries(family)) {
      const stats = asRecord(raw);
      if (!stats || (stats.column !== undefined && stats.column !== name)) return [];
      const row: JsonRecord = { "变量": name, "类型": kind };
      for (const [key, label] of Object.entries(statsFields)) if (Object.hasOwn(stats, key)) {
        row[label] = key === "topValues" || key === "valueCounts" ? categoryCounts(stats[key], key) : stats[key];
      }
      const descriptor = descriptors.get(name);
      if (!Object.hasOwn(stats, "missing") && descriptor && Object.hasOwn(descriptor, "missingCount")) row["缺失"] = descriptor.missingCount;
      rows.push(row);
    }
  }
  return rows;
}

function categoryCounts(value: unknown, kind: string): unknown {
  let entries: [unknown, unknown][];
  if (kind === "valueCounts") {
    const counts = asRecord(value);
    if (!counts) return value;
    entries = Object.entries(counts);
  } else {
    if (!Array.isArray(value) || !value.every(item => asRecord(item) && Object.keys(item).length === 2 && "value" in item && "count" in item)) return value;
    entries = value.map(item => [item.value, item.count]);
  }
  if (!entries.every(([label, count]) => typeof label === "string" && typeof count === "number" && Number.isSafeInteger(count) && count >= 0)) return value;
  return entries.length ? entries.map(([label, count]) => `${JSON.stringify(label)}：${count}`).join("\n") : "未列出";
}

function trajectoryMsdRows(record: JsonRecord): JsonRecord[] {
  const times = Array.isArray(record.lagTimesPs) ? record.lagTimesPs : [];
  const total = Array.isArray(record.totalMsdAngstrom2) ? record.totalMsdAngstrom2 : [];
  const directional = asRecord(record.directionalMsdAngstrom2);
  const x = Array.isArray(directional?.x) ? directional.x : [];
  const y = Array.isArray(directional?.y) ? directional.y : [];
  const z = Array.isArray(directional?.z) ? directional.z : [];
  const count = Math.min(times.length, total.length);
  return Array.from({ length: count }, (_, index) => ({
    lag_time_ps: times[index],
    total_msd_angstrom2: total[index],
    x_msd_angstrom2: x[index],
    y_msd_angstrom2: y[index],
    z_msd_angstrom2: z[index],
  }));
}

function trajectoryDiffusionRows(record: JsonRecord): JsonRecord[] {
  const estimate = asRecord(record.diffusionEstimate);
  const fit = asRecord(record.fit);
  const window = asRecord(record.fitWindow);
  const diagnostic = asRecord(record.regimeDiagnostic);
  if (!estimate && !fit && !window) return [];
  return [{
    fit_start_ps: window?.startPs,
    fit_end_ps: window?.endPs,
    fit_points: window?.pointCount ?? fit?.pointCount,
    diffusion_coefficient_angstrom2_per_ps: estimate?.value,
    diffusion_unit: estimate?.unit,
    r_squared: fit?.rSquared,
    rmse_angstrom2: fit?.rmseAngstrom2,
    regime_status: diagnostic?.status,
  }];
}

export function asRecord(value: unknown): JsonRecord | null {
  return value && typeof value === "object" && !Array.isArray(value) ? value as JsonRecord : null;
}

function records(value: unknown): JsonRecord[] {
  return Array.isArray(value) ? value.map(asRecord).filter((item): item is JsonRecord => Boolean(item)) : [];
}

function spinLabel(value: unknown): unknown {
  return value === "up" ? "上自旋" : value === "down" ? "下自旋" : value === "none" ? "非自旋极化" : value;
}

function numberValue(value: unknown): number | null {
  const number = typeof value === "number" ? value : Number(value);
  return Number.isFinite(number) ? number : null;
}

export function displayValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) return `[${value.map((item) => displayValue(item)).join(", ")}]`;
  return JSON.stringify(value);
}

export function isNumericTableColumn(rows: JsonRecord[], key: string): boolean {
  return rows.some(row => typeof row[key] === "number")
    && rows.every(row => row[key] == null || (typeof row[key] === "number" && Number.isFinite(row[key])));
}

export function formatColumnLabel(value: string, payload?: unknown): string {
  const table = asRecord(payload);
  if (table?.schemaVersion === "mdi.reference.element-table/1.0") {
    const labels: Record<string, string> = { symbol: "元素", name: "元素名称", atomic_number: "原子序数", covalent_radius_angstrom: "参考共价半径（Å）" };
    if (labels[value]) return labels[value];
  }
  if (table?.schema_version === "phase10h1.phonon_band_table.v1") {
    const units = asRecord(table.units);
    const unit = (key: string, known: string, label: string) => units?.[key] === known ? label : typeof units?.[key] === "string" ? String(units[key]) : "单位未提供";
    const phononLabels: Record<string, string> = {
      qpoint_index: "q 点索引", branch_index: "分支索引", frequency_terahertz: `频率 (${unit("frequency", "terahertz", "THz")})`,
      label: "路径标签", classification: "频率分类", path_distance: `路径距离 (${unit("path_distance", "radian_per_angstrom", "rad/Å")})`,
      segment_index: "路径段索引", q_x: "qₓ", q_y: "qᵧ", q_z: "q_z",
    };
    if (phononLabels[value]) return phononLabels[value];
  }
  const labels: Record<string, string> = {
    spinChannel: "自旋", bandId: "能带", kpointId: "k 点", energyEv: "能量 (eV)", fractionalCoordinates: "分数坐标",
    stateId: "状态标识", bandIdentity: "能带标识", channelLabel: "通道", channelIdentity: "通道标识", energyPointId: "能量点标识", projectionKind: "通道类型",
    coordination_number: "配位数",
    element: "元素",
    neighbor_count_before_truncation: "截断前邻居数",
    neighbor_distances_angstrom: "邻居距离 (Å)",
    neighbor_elements: "邻居元素",
    neighbor_indices: "邻居索引",
    site_index: "位点索引",
    structureId: "结构标识",
    sample_id: "样本标识",
    band_gap: "带隙",
    lag_time_ps: "滞后时间 (ps)",
    total_msd_angstrom2: "总 MSD (Å²)",
    x_msd_angstrom2: "X 方向 MSD (Å²)",
    y_msd_angstrom2: "Y 方向 MSD (Å²)",
    z_msd_angstrom2: "Z 方向 MSD (Å²)",
    fit_start_ps: "拟合起点 (ps)",
    fit_end_ps: "拟合终点 (ps)",
    fit_points: "拟合点数",
    diffusion_coefficient_angstrom2_per_ps: "扩散系数 (Å²/ps)",
    diffusion_unit: "扩散系数单位",
    r_squared: "R²",
    rmse_angstrom2: "RMSE (Å²)",
    regime_status: "区间诊断",
  };
  return labels[value] || value.replaceAll("_", " ");
}
